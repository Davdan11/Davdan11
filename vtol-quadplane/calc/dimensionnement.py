"""Bilan de masse, centrage et performances du quadplane Huard.

    python calc/dimensionnement.py                       # Huard DFR
    HUARD_VERSION=mini python calc/dimensionnement.py    # Huard Mini

Lit la masse et le centre de gravité des pièces imprimées dans
cad/out/masses.csv (générée par cad/build.py) et écrit docs/bilan.md.
Les coefficients aérodynamiques sont des estimations ; les premiers vols
(logs ArduPilot) serviront à les recaler.
"""
import csv
import math
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, os.path.join(RACINE, "cad"))
from params import (BATTERIE, CG_X, COMPAGNON_X, CORDE, DERIVE_BA_X,  # noqa: E402
                    DERIVE_CORDE_PIED, ENVERGURE, HELICE_VTOL, NACELLE_X, PLATEAU_X,
                    POUTRE_DEBUT, POUTRE_LONG, PROFONDEUR_X, SECTIONS_FUS, STAB_BA_X,
                    STAB_CORDE, VERSION)

G, RHO = 9.81, 1.225

X_SERVO_PROF = STAB_BA_X + PROFONDEUR_X * STAB_CORDE - 21  # baie du servo de profondeur, devant la charnière
X_POUSSEUR = SECTIONS_FUS[-1][0]

# Hypothèses communes
OSWALD = 0.80
CL_MAX = 1.30
FM = 0.60             # figure de mérite des hélices VTOL
ETA_MOTEUR = 0.80
UTILISABLE = 0.85     # fraction de l'énergie batterie utilisée (le reste = réserve)
MARGE_DECROCHAGE = 1.35  # vitesse mini de vol en cercle = 1,35 x Vs
T_VTOL_S = 120        # temps total de vol stationnaire (décollage + atterrissage)

if VERSION == "dfr":
    TITRE = "Huard DFR"
    # (élément, quantité, masse unitaire g, position x du centre en mm)
    COMPOSANTS = [
        ("Moteur VTOL T-Motor MN4014 KV400", 4, 171, CG_X),
        ("Hélice VTOL T-Motor P15x5 (2 CW + 2 CCW)", 4, 22, CG_X),
        ("ESC VTOL Holybro Tekko32 F4 45A + condensateur", 4, 10, CG_X),
        ("Moteur propulsif SunnySky X2820 V3 KV570", 1, 150, X_POUSSEUR + 25),
        ("Hélice propulsive APC 10x7EP", 1, 20, X_POUSSEUR + 60),
        ("ESC propulsif Holybro Tekko32 F4 45A", 1, 10, 175),
        ("Contrôleur de vol TBS Lucid H7 Wing", 1, 30, 122),
        ("GPS + compas Holybro Micro M10", 1, 16, 230),
        ("Capteur de vitesse Matek ASPD-4525 + Pitot", 1, 10, SECTIONS_FUS[0][0] + 60),
        ("Récepteur RadioMaster RP3 V2 (pilote de sécurité)", 1, 5, 122),
        ("Servo EMAX ES08MD II (ailerons)", 2, 12, 0.55 * CORDE),
        ("Servo EMAX ES08MD II (profondeur)", 1, 12, X_SERVO_PROF),
        ("Nacelle SIYI ZT6 avec plaque anti-vibration", 1, 197, NACELLE_X),
        ("Raspberry Pi 5 4 Go + Active Cooler", 1, 67, 190),
        ("Modem Waveshare SIM7600G-H (clé USB, sans boîtier) + antennes", 1, 60, -100),
        ("BEC Holybro UBEC 5A (Pi et modem)", 2, 7, 150),
        ("Tube carbone 16x14x1000 (poutres)", 2, 73, POUTRE_DEBUT + POUTRE_LONG / 2),
        ("Tube carbone 16x14x1000 (longeron principal)", 1, 73, 55),
        ("Tube carbone 8x6x1000 (longerons extérieurs, coupé en 2)", 1, 34, 88),
        ("Jonc carbone 6 mm x 300 (goupille d'aile)", 1, 13, 143),
        ("Tube carbone 6x4 x 720 (longeron du stab)", 1, 18, STAB_BA_X + 27),
        ("Joncs carbone 3 mm et 2 mm (stab, gouvernes)", 1, 15, 600),
        ("Câblage, connecteurs", 1, 170, 40),
        ("Visserie, guignols, colle, ruban", 1, 70, 100),
    ]
    # nom : (masse g, énergie Wh, tension nominale)
    BATTERIES = {"GAONENG GNB 6S3P P45B 13,5 Ah": (1337, 21.6 * 13.5, 21.6)}
    # réserve de 30 % (BATT_LOW_MAH 4000) : en fin de pack Li-ion, la tension chute et les moteurs
    # VTOL n'ont plus assez de marge pour l'atterrissage (simulation/vol_simule.py)
    UTILISABLE = 0.70
    CD0 = 0.050           # traînée parasite (poutres, moteurs VTOL arrêtés, nacelle caméra)
    ETA_CROISIERE = 0.55  # hélice x moteur x ESC
    P_BORD = 15.0         # W : avionique + ordinateur de bord + modem + nacelle
    V_TRANSIT = 22.0      # m/s (79 km/h) : l'hélice 10x7 ne pousse plus assez au-delà (vols simulés)
    POUSSEE_MAX_MOTEUR = 2.62  # kg, MN4014 KV400 + P15x5 à 22,2 V (table T-Motor)
    AFFAISSEMENT = 0.80   # poussée réelle sous la tension affaissée d'un pack Li-ion
    RAYONS_KM = (5, 10, 15, 20)
else:
    TITRE = "Huard Mini"
    COMPOSANTS = [
        ("Moteur VTOL Emax ECO III 2807 1300KV", 4, 56, CG_X),
        ("Hélice VTOL HQProp Cine7 7x4x3", 4, 10, CG_X),
        ("ESC Skystars Talon32 40A AM32 (VTOL)", 4, 7, CG_X),
        ("Moteur propulsif Emax ECO III 2807 1300KV", 1, 56, X_POUSSEUR + 18),
        ("Hélice propulsive Gemfan 7x6E", 1, 12, X_POUSSEUR + 45),
        ("ESC propulsif Skystars Talon32 40A", 1, 7, 110),
        ("Contrôleur de vol AtomRC F405 NAVI", 1, 21, COMPAGNON_X[0] + 20),
        ("GPS + compas MicoAir M10G-5883", 1, 7, 150),
        ("Récepteur RadioMaster RP1 V2", 1, 3, COMPAGNON_X[0] + 50),
        ("Servo JX PDI-1109MG (ailerons)", 2, 10, 0.55 * CORDE),
        ("Servo JX PDI-1109MG (profondeur)", 1, 10, X_SERVO_PROF),
        ("Tubes carbone 12x10 x 610 (poutres)", 2, 33, POUTRE_DEBUT + POUTRE_LONG / 2),
        ("Tube carbone 10x8 x 720 (longeron principal)", 1, 32, 40),
        ("Tube carbone 6x4 x 310 (longerons extérieurs)", 2, 8, 64),
        ("Jonc carbone 4 mm x 200 (goupille d'aile)", 1, 4, 104),
        ("Tube carbone 5x3 x 420 (longeron du stab)", 1, 8, STAB_BA_X + 22),
        ("Joncs carbone 2 mm et 1,5 mm (stab, gouvernes)", 1, 8, 300),
        ("Câblage, connecteurs, condensateurs", 1, 60, 30),
        ("Visserie, guignols, colle, ruban", 1, 25, 80),
    ]
    BATTERIES = {"CNHL G+Plus 4S 4000 mAh 70C (LiPo)": (416, 14.8 * 4.0, 14.8)}
    CD0 = 0.055           # petit avion : poutres et moteurs pèsent plus dans la traînée
    ETA_CROISIERE = 0.45  # moteur 2807 et hélice 7x6 : efficaces mais pas optimisés pour la croisière
    P_BORD = 3.0
    V_TRANSIT = 22.0
    POUSSEE_MAX_MOTEUR = 1.2  # kg, estimation (2807 1300KV + 7x4 en 4S, à mesurer)
    AFFAISSEMENT = 0.90   # une LiPo s'affaisse moins qu'une Li-ion
    RAYONS_KM = (1, 2, 3, 5)

# la batterie se glisse sur le plateau : son centre doit rester dans cette plage
X_BATTERIE_MIN = PLATEAU_X[0] + BATTERIE[0] / 2
X_BATTERIE_MAX = PLATEAU_X[1] - 5 - BATTERIE[0] / 2


def imprime():
    f = os.path.join(RACINE, "cad", "out" if VERSION == "dfr" else f"out_{VERSION}", "masses.csv")
    with open(f) as fh:
        for ligne in csv.reader(fh):
            if ligne and ligne[0].startswith("TOTAL"):
                return float(ligne[5]), float(ligne[6])
    raise SystemExit("Lancer d'abord cad/build.py")


def puissance(w, v, s, k):
    cl = w / (0.5 * RHO * v * v * s)
    cd = CD0 + k * cl * cl
    return w * v / (cl / cd) / ETA_CROISIERE + P_BORD, cl / cd


def analyse(m_kg):
    s = CORDE * ENVERGURE / 1e6
    ar = ENVERGURE / CORDE
    k = 1 / (math.pi * ar * OSWALD)
    w = m_kg * G
    vs = math.sqrt(2 * w / (RHO * s * CL_MAX))
    vitesses = [v / 10 for v in range(int(MARGE_DECROCHAGE * vs * 10) + 1, 300)]
    v_loiter = min(vitesses, key=lambda v: puissance(w, v, s, k)[0])
    a = 4 * math.pi * (HELICE_VTOL / 2000) ** 2
    p_stat = w ** 1.5 / math.sqrt(2 * RHO * a) / (FM * ETA_MOTEUR) + P_BORD
    return {
        "S": s, "AR": ar, "Vs": vs, "charge": m_kg / s,
        "v_loiter": v_loiter, "p_loiter": puissance(w, v_loiter, s, k),
        "p_transit": puissance(w, V_TRANSIT, s, k),
        "p_stat": p_stat, "T/W": 4 * POUSSEE_MAX_MOTEUR / m_kg,
        "T/W_reel": 4 * POUSSEE_MAX_MOTEUR * AFFAISSEMENT / m_kg,
    }


def mission(r, e_wh, rayon_km):
    """Minutes disponibles au-dessus des lieux pour une intervention à rayon_km."""
    e = e_wh * UTILISABLE - r["p_stat"] * T_VTOL_S / 3600
    t_transit_h = 2 * rayon_km * 1000 / V_TRANSIT / 3600
    e -= r["p_transit"][0] * t_transit_h
    return e / r["p_loiter"][0] * 60


def main():
    m_imp, x_imp = imprime()
    m_comp = sum(q * m for _, q, m, _ in COMPOSANTS)
    mx_comp = sum(q * m * x for _, q, m, x in COMPOSANTS)
    out = []
    p = out.append
    p(f"# Bilan de masse, centrage et performances — {TITRE}\n")
    p("Généré par `calc/dimensionnement.py`. Les chiffres aérodynamiques sont des "
      "estimations, à recaler avec les logs des premiers vols.\n")
    p("## Masse et position (x depuis le bord d'attaque, vers l'arrière)\n")
    p("| Élément | Qté | Masse unitaire (g) | Total (g) | x (mm) |")
    p("|---|---:|---:|---:|---:|")
    p(f"| Pièces imprimées (cad/out/masses.csv) | 1 | {m_imp:.0f} | {m_imp:.0f} | {x_imp:.0f} |")
    for nom, q, m, x in COMPOSANTS:
        p(f"| {nom} | {q} | {m} | {q * m} | {x:.0f} |")
    m_sans = m_imp + m_comp
    p(f"| **Sans batterie** | | | **{m_sans:.0f}** | {(m_imp * x_imp + mx_comp) / m_sans:.0f} |\n")

    p("## Centrage\n")
    p(f"Le centre de gravité doit tomber à **x = {CG_X:.0f} mm** (28 % de corde), au milieu des "
      "4 moteurs VTOL. On le règle en déplaçant la batterie sur le plateau.\n")
    p("| Batterie | Centre de la batterie requis | Plage possible | Lest |")
    p("|---|---:|---:|---|")
    for nom, (mb, _, _) in BATTERIES.items():
        m_tot = m_sans + mb
        xb = (CG_X * m_tot - m_imp * x_imp - mx_comp) / mb
        if X_BATTERIE_MIN <= xb <= X_BATTERIE_MAX:
            lest = "aucun"
        else:
            borne = X_BATTERIE_MIN if xb < X_BATTERIE_MIN else X_BATTERIE_MAX
            x_lest = -200.0 if xb < X_BATTERIE_MIN else 300.0
            moment = mb * (borne - xb)
            lest = f"≈ {abs(moment / (x_lest - CG_X)):.0f} g {'dans le nez' if x_lest < 0 else 'à l arrière'}"
        p(f"| {nom} | x = {xb:.0f} mm | {X_BATTERIE_MIN:.0f} à {X_BATTERIE_MAX:.0f} mm | {lest} |")
    p("")

    p("## Performances estimées\n")
    p("| | " + " | ".join(BATTERIES) + " |")
    p("|---|" + "---:|" * len(BATTERIES))
    lignes = {}
    for nom, (mb, e_wh, u) in BATTERIES.items():
        m = (m_sans + mb) / 1000
        r = analyse(m)
        val = {
            "Masse au décollage": f"{m:.2f} kg",
            "Charge alaire": f"{r['charge']:.1f} kg/m²",
            "Vitesse de décrochage": f"{r['Vs']:.1f} m/s ({r['Vs'] * 3.6:.0f} km/h)",
            "Rapport poussée/poids VTOL": f"{r['T/W']:.2f} (≈ {r['T/W_reel']:.2f} batterie affaissée)",
            "Puissance en stationnaire": f"{r['p_stat']:.0f} W ({r['p_stat'] / u:.0f} A)",
            f"Transit à {V_TRANSIT * 3.6:.0f} km/h": f"{r['p_transit'][0]:.0f} W",
            "Vol en cercle au-dessus des lieux": f"{r['v_loiter'] * 3.6:.0f} km/h, {r['p_loiter'][0]:.0f} W",
            "Autonomie en cercle seulement": f"**{mission(r, e_wh, 0):.0f} min**",
        }
        for rayon in RAYONS_KM:
            t = mission(r, e_wh, rayon)
            val[f"Temps sur les lieux, intervention à {rayon} km"] = (
                f"**{t:.0f} min** (aller {rayon * 1000 / V_TRANSIT / 60:.0f} min)" if t > 0
                else "hors de portée")
        for k, v in val.items():
            lignes.setdefault(k, []).append(v)
    for k, vals in lignes.items():
        p(f"| {k} | " + " | ".join(vals) + " |")
    p("")
    r = analyse((m_sans + list(BATTERIES.values())[0][0]) / 1000)
    p(f"Surface alaire {r['S']:.3f} m², allongement {r['AR']:.1f}. Hypothèses : "
      f"Cd0 = {CD0}, e = {OSWALD}, rendement de propulsion {ETA_CROISIERE}, "
      f"figure de mérite VTOL {FM}, {P_BORD:.0f} W pour l'électronique de bord, "
      f"{UTILISABLE:.0%} de la batterie utilisée (le reste est la réserve), "
      f"{T_VTOL_S // 60} min de vol stationnaire par mission, "
      f"{POUSSEE_MAX_MOTEUR} kg de poussée max par moteur VTOL "
      f"(× {AFFAISSEMENT} batterie affaissée).\n")
    texte = "\n".join(out)
    nom = "bilan.md" if VERSION == "dfr" else f"bilan_{VERSION}.md"
    with open(os.path.join(RACINE, "docs", nom), "w") as f:
        f.write(texte)
    print(texte)


if __name__ == "__main__":
    main()
