"""Vols simulés du Huard dans le vrai logiciel ArduPilot (SITL), avec le modèle de modele_sitl.py
et les paramètres de ardupilot/huard_*.param.

    python simulation/vol_simule.py                      # Huard DFR
    HUARD_VERSION=mini python simulation/vol_simule.py   # Huard Mini

Prérequis (une fois) : ArduPilot compilé pour SITL, avec le petit ajout de
simulation/sitl_poussee.patch (moteur propulsif réaliste : poussée, hélice, courant) :
    git clone --recursive https://github.com/ArduPilot/ardupilot ~/ardupilot
    cd ~/ardupilot && git apply <ce dossier>/sitl_poussee.patch
    ./waf configure --board sitl && ./waf plane
    pip install pymavlink
Variable ARDUPILOT si le dépôt n'est pas dans ~/ardupilot.

Scénarios : mission complète sans vent, avec vent et rafales, perte de la radio en croisière,
batterie faible. Rapport : docs/simulation*.md + images.
"""
import math
import os
import shutil
import subprocess
import sys
import tempfile
import time

from pymavlink import mavutil

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, ICI)
import modele_sitl as MS  # noqa: E402
from params import VERSION  # noqa: E402  (chemin ajouté par modele_sitl)

ARDUPILOT = os.environ.get("ARDUPILOT", next((d for d in (os.path.expanduser("~/ardupilot"), "/home/user/ardupilot")
                                              if os.path.isdir(d)), os.path.expanduser("~/ardupilot")))
BINAIRE = os.path.join(ARDUPILOT, "build", "sitl", "bin", "arduplane")
DEFAUTS_SITL = os.path.join(ARDUPILOT, "Tools", "autotest", "default_params", "quadplane.parm")
ACCELERE = 8
MAISON = (45.5370, -73.8500, 30.0, 0.0)     # terrain dégagé fictif près de Montréal
ALT_CROISIERE = 60.0

# Sorties du simulateur quadplane : 1 aileron, 2 profondeur, 3 propulseur, 5-8 moteurs VTOL
# (sur le vrai avion elles sont ailleurs : voir ardupilot/huard_*.param).
SORTIES_SITL = {
    "SERVO1_FUNCTION": 4, "SERVO2_FUNCTION": 19, "SERVO3_FUNCTION": 70, "SERVO4_FUNCTION": 0,
    "SERVO5_FUNCTION": 33, "SERVO6_FUNCTION": 34, "SERVO7_FUNCTION": 35, "SERVO8_FUNCTION": 36,
    "SERVO_BLH_MASK": 0, "Q_M_PWM_TYPE": 0, "RSSI_TYPE": 0, "LOG_DISARMED": 0,
}
for k in range(1, 9):
    SORTIES_SITL[f"SERVO{k}_MIN"] = 1000
    SORTIES_SITL[f"SERVO{k}_MAX"] = 2000
    SORTIES_SITL[f"SERVO{k}_TRIM"] = 1000 if k >= 3 else 1500
    SORTIES_SITL[f"SERVO{k}_REVERSED"] = 0


# étalonnages des capteurs de la vraie carte : le simulateur fournit ses propres mesures
PROPRES_A_LA_CARTE = {"BATT_AMP_PERVLT", "BATT_VOLT_MULT", "BATT_AMP_OFFSET"}


def lire_params():
    nom = "huard_dfr.param" if VERSION == "dfr" else f"huard_{VERSION}.param"
    p = {}
    with open(os.path.join(RACINE, "ardupilot", nom)) as f:
        for ligne in f:
            ligne = ligne.split("#")[0].strip()
            if not ligne:
                continue
            k, v = [x.strip() for x in ligne.replace("\t", ",").split(",")[:2]]
            p[k] = float(v)
    return p


# courbe tension / charge de la batterie du simulateur (SIM_Battery.cpp), tension par élément
COURBE = [(4.173, 100), (4.112, 96.15), (4.085, 92.31), (4.071, 88.46), (4.039, 84.62), (3.987, 80.77),
          (3.943, 76.92), (3.908, 73.08), (3.887, 69.23), (3.854, 65.38), (3.833, 61.54), (3.801, 57.69),
          (3.783, 53.85), (3.742, 50), (3.715, 46.15), (3.679, 42.31), (3.636, 38.46), (3.588, 34.62),
          (3.543, 30.77), (3.503, 26.92), (3.462, 23.08), (3.379, 19.23), (3.296, 15.38), (3.218, 11.54),
          (3.165, 7.69)]


def tension_repos(charge_pct):
    """Tension du pack au repos (V) pour un état de charge donné, comme le simulateur."""
    n = MS.PAR_VERSION[VERSION]["cellules"]
    for (v1, s1), (v2, s2) in zip(COURBE, COURBE[1:]):
        if charge_pct >= s2:
            return (v2 + (charge_pct - s2) / (s1 - s2) * (v1 - v2)) / 4.173 * 4.2 * n
    return COURBE[-1][0] / 4.173 * 4.2 * n


def decale(dn, de):
    lat, lon = MAISON[0], MAISON[1]
    return (lat + dn / 111320.0, lon + de / (111320.0 * math.cos(math.radians(lat))))


class Simu:
    def __init__(self, nom, env_sim):
        self.nom = nom
        self.dos = tempfile.mkdtemp(prefix=f"huard_{nom}_")
        self.env_sim = env_sim
        self.trace = []           # (t, n, e, alt, vitesse air, vitesse sol, gaz, roulis, tangage, mode)
        self.textes = []
        self.moteurs_max = []     # (t, sortie VTOL max 0..1)
        self.batt = []            # (t, tension, mAh consommés)
        self.mode = ""
        self.t = 0.0

    def demarre(self, modele_json, defauts):
        env = dict(os.environ)
        env["SIM_POUSSEE_MAX_N"] = str(MS.PAR_VERSION[VERSION]["poussee"])
        env["SIM_VITESSE_PAS"] = str(MS.PAR_VERSION[VERSION]["pas"])
        env["SIM_COURANT_POUSSEUR_A"] = str(MS.PAR_VERSION[VERSION]["courant"])
        shutil.copy(modele_json, self.dos)   # le simulateur lit le modèle dans son dossier de travail
        cmd = [BINAIRE, "--model", f"quadplane:{os.path.basename(modele_json)}", "--speedup", str(ACCELERE),
               "--defaults", defauts, "-I0", "--wipe",
               "--home", ",".join(str(x) for x in MAISON)]
        self.journal = open(os.path.join(self.dos, "sitl.txt"), "w")
        self.proc = subprocess.Popen(cmd, cwd=self.dos, stdout=self.journal, stderr=subprocess.STDOUT, env=env)
        time.sleep(2)
        self.m = mavutil.mavlink_connection("tcp:127.0.0.1:5760", source_system=255, retries=60)
        self.m.wait_heartbeat(timeout=60)
        self.m.mav.request_data_stream_send(self.m.target_system, self.m.target_component,
                                            mavutil.mavlink.MAV_DATA_STREAM_ALL, 10, 1)

    def arrete(self):
        try:
            self.m.close()
        except Exception:
            pass
        self.proc.terminate()
        try:
            self.proc.wait(10)
        except Exception:
            self.proc.kill()
        self.journal.close()

    # --- réception -----------------------------------------------------------
    def pompe(self, duree_sim=0.0, jusqua=None, limite_sim=1800.0):
        """Lit la télémétrie pendant duree_sim secondes simulées, ou jusqu'à ce que jusqua() soit vrai."""
        t0 = self.t
        dernier = time.time()
        while True:
            msg = self.m.recv_match(blocking=True, timeout=1.0)
            if msg is None:
                if time.time() - dernier > 60:
                    raise RuntimeError("le simulateur ne répond plus")
                continue
            dernier = time.time()
            self.traite(msg)
            if jusqua is not None and jusqua():
                return True
            if jusqua is None and self.t - t0 >= duree_sim:
                return True
            if self.t - t0 > limite_sim:
                return False

    def traite(self, msg):
        typ = msg.get_type()
        if typ == "SYSTEM_TIME":
            self.t = msg.time_boot_ms / 1000.0
        elif typ == "HEARTBEAT" and msg.get_srcSystem() == self.m.target_system and msg.type != 6:
            self.mode = mavutil.mode_string_v10(msg)
            self.arme = bool(msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED)
        elif typ == "GLOBAL_POSITION_INT":
            self.pos = msg
        elif typ == "ATTITUDE":
            self.att = msg
        elif typ == "VFR_HUD" and hasattr(self, "pos") and hasattr(self, "att") and self.pos.lat != 0:
            n = (self.pos.lat / 1e7 - MAISON[0]) * 111320.0
            e = (self.pos.lon / 1e7 - MAISON[1]) * 111320.0 * math.cos(math.radians(MAISON[0]))
            self.trace.append((self.t, n, e, self.pos.relative_alt / 1000.0, msg.airspeed, msg.groundspeed,
                               msg.throttle, math.degrees(self.att.roll), math.degrees(self.att.pitch), self.mode,
                               math.degrees(self.att.yaw), *getattr(self, "servos", (0, 0, 0))))
        elif typ == "SERVO_OUTPUT_RAW":
            sorties = [msg.servo5_raw, msg.servo6_raw, msg.servo7_raw, msg.servo8_raw]
            self.servos = (msg.servo1_raw, msg.servo2_raw, msg.servo3_raw)
            self.moteurs_max.append((self.t, max((s - 1000) / 1000.0 for s in sorties)))
        elif typ == "BATTERY_STATUS":
            self.batt.append((self.t, msg.voltages[0] / 1000.0, msg.current_consumed))
        elif typ == "STATUSTEXT":
            self.textes.append((self.t, msg.text))

    # --- commandes -------------------------------------------------------------
    def param(self, nom, valeur):
        for _ in range(5):
            self.m.mav.param_set_send(self.m.target_system, self.m.target_component, nom.encode(),
                                      float(valeur), mavutil.mavlink.MAV_PARAM_TYPE_REAL32)
            msg = self.m.recv_match(type="PARAM_VALUE", blocking=True, timeout=3)
            if msg is not None and msg.param_id == nom:
                return True
        return False

    def tous_les_params(self):
        self.m.mav.param_request_list_send(self.m.target_system, self.m.target_component)
        noms, fin = set(), time.time() + 60
        while time.time() < fin:
            msg = self.m.recv_match(type="PARAM_VALUE", blocking=True, timeout=5)
            if msg is None:
                break
            noms.add(msg.param_id)
            if len(noms) >= msg.param_count:
                break
        return noms

    def commande(self, cmd, *p):
        p = list(p) + [0] * (7 - len(p))
        self.m.mav.command_long_send(self.m.target_system, self.m.target_component, cmd, 0, *p)

    def change_mode(self, nom):
        self.m.set_mode(self.m.mode_mapping()[nom])
        return self.pompe(jusqua=lambda: self.mode == nom, limite_sim=20)

    def arme_moteurs(self, limite=180):
        debut = self.t
        while self.t - debut < limite:
            self.commande(mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 1)
            self.pompe(3)
            if getattr(self, "arme", False):
                return True
        return False

    def envoie_mission(self, points):
        """points : liste de (commande, p1, p2, p3, p4, lat, lon, alt)."""
        items = [(mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, MAISON[0], MAISON[1], 0)] + points
        self.m.mav.mission_count_send(self.m.target_system, self.m.target_component, len(items))
        envoyes = set()
        fin = time.time() + 60
        while time.time() < fin:
            msg = self.m.recv_match(type=["MISSION_REQUEST", "MISSION_REQUEST_INT", "MISSION_ACK"],
                                    blocking=True, timeout=5)
            if msg is None:
                continue
            if msg.get_type() == "MISSION_ACK":
                return msg.type == 0 and len(envoyes) == len(items)
            cmd, p1, p2, p3, p4, lat, lon, alt = items[msg.seq]
            self.m.mav.mission_item_int_send(
                self.m.target_system, self.m.target_component, msg.seq,
                mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT, cmd, 0, 1, p1, p2, p3, p4,
                int(lat * 1e7), int(lon * 1e7), alt)
            envoyes.add(msg.seq)
        return False


def mission():
    W = mavutil.mavlink
    pts = [(W.MAV_CMD_NAV_VTOL_TAKEOFF, 0, 0, 0, 0, MAISON[0], MAISON[1], 40)]
    for dn, de in ((300, 0), (700, 300), (700, 900), (200, 900)):
        lat, lon = decale(dn, de)
        pts.append((W.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, lat, lon, ALT_CROISIERE))
    lat, lon = decale(450, 600)
    pts.append((W.MAV_CMD_NAV_LOITER_TURNS, 2, 0, 80, 0, lat, lon, ALT_CROISIERE))   # « sur les lieux »
    # approche finale en ligne droite : 400 m au sud, puis cap au nord vers le point de pose
    lat, lon = decale(-400, 0)
    pts.append((W.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, lat, lon, 40))
    pts.append((W.MAV_CMD_NAV_VTOL_LAND, 0, 0, 0, 0, MAISON[0], MAISON[1], 0))
    return pts


SCENARIOS = [
    dict(nom="nominal", titre="Mission complète, sans vent", sim={}, panne=None),
    # turbulence : écart-type des rafales (m/s) ; en basse altitude, environ 0,1 x la vitesse du vent
    dict(nom="vent", titre="Vent 25 km/h avec rafales", sim={"SIM_WIND_SPD": 7, "SIM_WIND_DIR": 250, "SIM_WIND_TURB": 1.0},
         panne=None),
    dict(nom="vent_fort", titre="Vent 32 km/h, rafales fortes (test de limite)",
         sim={"SIM_WIND_SPD": 9, "SIM_WIND_DIR": 250, "SIM_WIND_TURB": 1.5}, panne=None),
    dict(nom="radio", titre="Perte de la radio en croisière", sim={"SIM_WIND_SPD": 4, "SIM_WIND_DIR": 200},
         panne="radio"),
    dict(nom="batterie", titre="Batterie presque vide pendant la mission", sim={"SIM_WIND_SPD": 5, "SIM_WIND_DIR": 250,
                                                                                "SIM_WIND_TURB": 0.7},
         panne="batterie"),
]


def vol(sc, modele_json, defauts, params_attendus):
    if sc.get("parm"):   # paramètres propres au scénario (chargés au démarrage)
        d2 = defauts.replace(".parm", f"_{sc['nom']}.parm")
        shutil.copy(defauts, d2)
        with open(d2, "a") as f:
            for k, v in sc["parm"].items():
                f.write(f"{k} {v:g}\n")
        defauts = d2
    s = Simu(sc["nom"], sc["sim"])
    res = dict(sc=sc, ok=False, notes=[])
    try:
        s.demarre(modele_json, defauts)
        s.pompe(5)
        if params_attendus is not None:
            presents = s.tous_les_params()
            res["inconnus"] = sorted(k for k in params_attendus if k not in presents)
        for k, v in sc["sim"].items():
            s.param(k, v)
        if sc["panne"] == "batterie":
            # Fin de batterie réaliste : le vrai pack, mais qui commence le vol déjà déchargé, de
            # sorte que l'alarme « batterie faible » (BATT_LOW_MAH, la vraie réserve) se déclenche à
            # mi-mission. L'avion rentre et se pose à la verticale vers 15 % de charge, à basse tension.
            p = lire_params()
            cap_vrai = MS.PAR_VERSION[VERSION]["ah"] * 1000
            cap = 0.5 * sc["mah_mission"] + p["BATT_LOW_MAH"]          # ce que croit l'autopilote
            s.param("SIM_BATT_VOLTAGE", tension_repos(100 * cap / cap_vrai))
            s.param("BATT_CAPACITY", int(cap))
        if not s.envoie_mission(mission()):
            res["notes"].append("mission refusée par l'autopilote")
            return res, s
        s.pompe(jusqua=lambda: any("EKF3" in t and "using GPS" in t for _, t in s.textes), limite_sim=120)
        s.pompe(10)
        s.change_mode("QLOITER")
        if not s.arme_moteurs():
            res["notes"].append("armement refusé : " + "; ".join(t for _, t in s.textes[-6:]))
            return res, s
        t_arm = s.t
        s.change_mode("AUTO")
        if sc["panne"] == "radio":
            # couper la radio une fois en croisière, loin de la maison
            s.pompe(jusqua=lambda: len(s.trace) and math.hypot(s.trace[-1][1], s.trace[-1][2]) > 500
                    and s.trace[-1][4] > 12 and s.trace[-1][3] > 30, limite_sim=600)
            res["t_panne"] = s.t
            s.param("SIM_RC_FAIL", 1)
        fini = s.pompe(jusqua=lambda: s.t - t_arm > 20 and not s.arme, limite_sim=1500)
        res["ok"] = fini
        res["duree"] = s.t - t_arm
        if not fini:
            res["notes"].append("l'avion ne s'est pas posé dans le temps imparti")
    except Exception as e:  # noqa: BLE001
        res["notes"].append(f"erreur : {e}")
    finally:
        s.arrete()
    return res, s


def analyse(res, s):
    tr = s.trace
    if not tr:
        return res
    t0 = tr[0][0]
    vol_ = [r for r in tr if r[3] > 1.0]
    res["alt_max"] = max(r[3] for r in tr)
    res["roulis_max"] = max(abs(r[7]) for r in vol_) if vol_ else 0
    res["tangage_max"] = max(abs(r[8]) for r in vol_) if vol_ else 0
    # vol en avion : entre la fin de la première transition et le début de l'approche VTOL
    t_av = next((t for t, x in s.textes if "Transition done" in x), None)
    t_ap = next((t for t, x in s.textes if t_av and t > t_av and any(
        m in x for m in ("VTOL approach", "VTOL airbrake", "VTOL position", "Land descend", "Battery 1 is critical"))), None)
    avion = [r for r in tr if t_av and t_ap and t_av + 5 < r[0] < t_ap]
    res["vitesse_min_avion"] = min((r[4] for r in avion), default=0)
    res["vitesse_croisiere"] = sorted(r[4] for r in avion)[len(avion) // 2] if avion else 0
    res["roulis_max"] = max((abs(r[7]) for r in avion), default=0)
    fin = tr[-1]
    res["distance_pose"] = math.hypot(fin[1], fin[2])
    # gaz VTOL en stationnaire stable (au-dessus de 5 m, vitesse sol < 1 m/s) et temps passé à fond
    import bisect
    tm = [m[0] for m in s.moteurs_max]
    def mot(t):
        return s.moteurs_max[min(bisect.bisect_left(tm, t), len(tm) - 1)][1] if tm else 0
    stat = sorted(mot(r[0]) for r in tr if r[3] > 5 and r[5] < 1.0)
    res["gaz_stationnaire"] = stat[len(stat) // 2] if stat else 0
    vtol = [mot(r[0]) for r in tr if r[3] > 0.5 and r[4] < 10]
    res["part_a_fond"] = sum(1 for m in vtol if m >= 0.94) / len(vtol) if vtol else 0
    if s.batt:
        res["mah"] = s.batt[-1][2]
        res["tension_min"] = min(b[1] for b in s.batt if b[1] > 1)
    transit = []
    for t, txt in s.textes:
        if "Transition" in txt or "transition" in txt:
            transit.append((t, txt))
    res["transitions"] = transit
    res["textes"] = s.textes
    alt_trans = [r[3] for r in tr if any(0 <= r[0] - t <= 15 for t, _ in transit)]
    res["alt_min_transition"] = min(alt_trans, default=None)
    res["modes"] = []
    for r in tr:
        if not res["modes"] or res["modes"][-1][1] != r[9]:
            res["modes"].append((r[0] - t0, r[9]))
    return res


def images(resultats, suf):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    bleu, orange, aqua, jaune, magenta, gris, encre, encre2 = ("#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4",
                                                               "#8a8984", "#0b0b0b", "#52514e")
    coul = [bleu, orange, aqua, jaune, magenta]
    plt.rcParams.update({"font.size": 10, "axes.edgecolor": gris, "axes.labelcolor": encre2,
                         "xtick.color": encre2, "ytick.color": encre2})
    fig, axs = plt.subplots(len(resultats), 1, figsize=(11, 3.1 * len(resultats)), dpi=100, sharex=False)
    for ax, (res, s), c in zip(axs, resultats, coul):
        tr = s.trace
        if not tr:
            continue
        t0 = tr[0][0]
        t = [(r[0] - t0) / 60 for r in tr]
        ax.plot(t, [r[3] for r in tr], color=c, lw=2)
        ax2 = ax.twinx()
        ax2.plot(t, [r[4] for r in tr], color=gris, lw=1.2)
        ax2.set_ylabel("vitesse air (m/s)", color=gris)
        ax.set_ylabel("hauteur (m)")
        ax.set_title(res["sc"]["titre"], color=encre, fontsize=11, loc="left")
        for tm, mode in res.get("modes", []):
            ax.axvline(tm / 60, color="#e4e3df", lw=0.8)
            ax.text(tm / 60, ax.get_ylim()[1] * 0.97, mode, fontsize=7, color=encre2, rotation=90, va="top")
        ax.grid(color="#efeeea", lw=0.5)
        for sp in ("top",):
            ax.spines[sp].set_visible(False)
    axs[-1].set_xlabel("temps (min)")
    fig.tight_layout()
    fig.savefig(os.path.join(RACINE, "docs", "images", f"simulation_profils{suf}.png"))
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 7), dpi=100)
    for (res, s), c in zip(resultats, coul):
        if s.trace:
            ax.plot([r[2] for r in s.trace], [r[1] for r in s.trace], color=c, lw=1.6, label=res["sc"]["titre"])
    for cmd, *_, lat, lon, alt in mission()[1:]:
        ax.plot((lon - MAISON[1]) * 111320 * math.cos(math.radians(MAISON[0])), (lat - MAISON[0]) * 111320,
                "o", color=encre, ms=4)
    ax.plot(0, 0, "s", color=encre, ms=8)
    ax.annotate("décollage / atterrissage", (0, 0), xytext=(15, -40), textcoords="offset points", color=encre2)
    ax.set_aspect("equal")
    ax.set_xlabel("est (m)")
    ax.set_ylabel("nord (m)")
    ax.legend(fontsize=8, loc="upper left", frameon=False)
    ax.grid(color="#efeeea", lw=0.5)
    ax.set_title("Trajectoires simulées (points noirs : mission)", color=encre)
    fig.tight_layout()
    fig.savefig(os.path.join(RACINE, "docs", "images", f"simulation_trajectoires{suf}.png"))
    plt.close(fig)


def main():
    chemin_json, info = MS.main()
    params = lire_params()
    defauts = os.path.join(tempfile.mkdtemp(prefix="huard_parm_"), "huard_sitl.parm")
    shutil.copy(DEFAUTS_SITL, defauts)
    with open(defauts, "a") as f:
        f.write("\n# --- paramètres du Huard (ardupilot/huard_*.param) ---\n")
        for k, v in params.items():
            if k not in PROPRES_A_LA_CARTE:
                f.write(f"{k} {v:g}\n")
        f.write("\n# --- sorties du simulateur ---\n")
        for k, v in SORTIES_SITL.items():
            f.write(f"{k} {v:g}\n")
        if params.get("ARSPD_TYPE", 0) != 0:   # capteur de vitesse : celui du simulateur
            f.write("ARSPD_TYPE 100\n")
        if params.get("MNT1_TYPE", 0) != 0:    # pas de nacelle caméra dans le simulateur
            f.write("MNT1_TYPE 0\n")
    resultats = []
    for i, sc in enumerate(SCENARIOS):
        print(f"--- {sc['titre']}", flush=True)
        if sc["panne"] == "batterie":
            sc["mah_mission"] = resultats[0][0].get("mah") or 1000
        res, s = vol(sc, chemin_json, defauts, params if i == 0 else None)
        res = analyse(res, s)
        resultats.append((res, s))
        print({k: v for k, v in res.items() if k not in ("textes", "modes", "sc", "transitions")}, flush=True)
    suf = "" if VERSION == "dfr" else f"_{VERSION}"
    images(resultats, suf)
    rapport(resultats, info, suf)


def rapport(resultats, info, suf):
    titre = "Huard DFR" if VERSION == "dfr" else "Huard Mini"
    L = [f"# Vols simulés — {titre}\n",
         "Généré par `simulation/vol_simule.py`. Le **vrai logiciel ArduPilot** (ArduPlane, compilé pour "
         "ordinateur : SITL) pilote un modèle de l'avion calculé à partir de nos cotes "
         "(`simulation/modele_sitl.py` : masse, aérodynamique, stabilité, moteurs, batterie), avec les "
         "paramètres de `ardupilot/huard_*.param`. Seules les sorties de la carte sont remappées sur celles "
         "du simulateur.\n",
         f"Modèle : {info['masse']:.2f} kg, marge statique {info['marge']:.0%}, gaz de stationnaire "
         f"{info['hover']:.0%} (estimation du bilan, batterie affaissée), moteur propulsif {info['poussee']:g} N au point fixe "
         f"(nulle à {info['pas'] * 3.6:.0f} km/h, vitesse de pas de l'hélice).\n",
         "## Résultats\n",
         "| Scénario | Résultat | Durée | Croisière (air) | Vitesse mini en avion | Roulis max en avion | "
         "Gaz VTOL en stationnaire | Temps moteurs VTOL à fond | Posé à | Batterie consommée | Tension mini |",
         "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for res, s in resultats:
        ok = "✅ posé" if res["ok"] else "❌ " + "; ".join(res["notes"])
        L.append(f"| {res['sc']['titre']} | {ok} | {res.get('duree', 0) / 60:.1f} min | "
                 f"{res.get('vitesse_croisiere', 0) * 3.6:.0f} km/h | {res.get('vitesse_min_avion', 0) * 3.6:.0f} km/h | "
                 f"{res.get('roulis_max', 0):.0f}° | {res.get('gaz_stationnaire', 0):.0%} | {res.get('part_a_fond', 0):.0%} | "
                 f"{res.get('distance_pose', 0):.1f} m du point prévu | {res.get('mah', 0):.0f} mAh | "
                 f"{res.get('tension_min', 0):.1f} V |")
    L.append("")
    inconnus = resultats[0][0].get("inconnus", [])
    L.append("## Paramètres ArduPilot\n")
    if inconnus:
        L.append("Paramètres de `ardupilot/huard_*.param` **inconnus** d'ArduPlane (version simulée) : "
                 + ", ".join(f"`{k}`" for k in inconnus)
                 + (" : ils règlent le DShot de la vraie carte et n'existent pas dans le simulateur. Tous les autres "
                    "ont été acceptés.\n" if all(k.startswith("SERVO_BLH") for k in inconnus) else ".\n"))
    else:
        L.append("Tous les paramètres de `ardupilot/huard_*.param` existent dans la version d'ArduPlane "
                 "simulée et ont été acceptés.\n")
    L.append(f"![profils](images/simulation_profils{suf}.png)\n")
    L.append(f"![trajectoires](images/simulation_trajectoires{suf}.png)\n")
    L.append("## Déroulement (messages de l'autopilote)\n")
    for res, s in resultats:
        L.append(f"### {res['sc']['titre']}\n")
        if res.get("t_panne"):
            L.append(f"- radio coupée à t = {res['t_panne'] - s.trace[0][0]:.0f} s")
        t0 = s.trace[0][0] if s.trace else 0
        for t, txt in res.get("textes", []):
            if any(m in txt for m in ("Transition", "transition", "Mission", "Land", "land", "Failsafe", "failsafe",
                                      "Battery", "battery", "Takeoff", "takeoff", "RTL", "Disarm", "Arm", "Q_ASSIST",
                                      "assist", "Reached", "QRTL", "VTOL")):
                L.append(f"- {max(0, t - t0):5.0f} s : {txt}")
        L.append("")
    L.append("## Limites de la simulation\n")
    L.append("- Le modèle aérodynamique est calculé, pas mesuré : il sera recalé avec les logs des vrais vols.")
    L.append("- Le moteur propulsif a une poussée constante (pas de baisse avec la vitesse) ; les capteurs "
             "sont parfaits (pas de vibrations). Le Mini vole sans capteur de vitesse, comme en vrai.")
    L.append("- Les réglages (PID) sont ceux d'origine d'ArduPilot ; QAUTOTUNE et AUTOTUNE restent à faire en vrai.")
    with open(os.path.join(RACINE, "docs", f"simulation{suf}.md"), "w") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
