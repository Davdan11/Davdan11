"""Modèle de vol du Huard pour le simulateur d'ArduPilot (SITL), calculé à partir des cotes réelles.

    python simulation/modele_sitl.py                      # Huard DFR  -> simulation/huard_dfr.json
    HUARD_VERSION=mini python simulation/modele_sitl.py   # Huard Mini -> simulation/huard_mini.json

Un seul fichier JSON sert au simulateur « quadplane » d'ArduPilot :
  - coefficients aérodynamiques de l'avion (SIM_Plane) : surface, envergure, corde, portance,
    traînée, stabilité et efficacité des gouvernes, calculés comme dans calc/essais_virtuels.py ;
  - modèle des 4 moteurs VTOL (SIM_Frame) : masse, diagonale, surface des hélices, gaz de
    stationnaire, batterie.
Dans le simulateur, la masse totale vaut 1,5 x la masse « frame » : on en tient compte.
"""
import json
import math
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, os.path.join(RACINE, "cad"))
sys.path.insert(0, os.path.join(RACINE, "calc"))
import dimensionnement as D  # noqa: E402
from params import *  # noqa: E402,F403

DEBATTEMENT = math.radians(20.0)   # ±20° de gouverne (voir calc/essais_virtuels.py)
EXPO = 0.65                        # Q_M_THST_EXPO
PAR_VERSION = {
    # cellules, capacité Ah, poussée statique max du propulseur (N), vitesse de pas de son hélice
    # (m/s : la poussée y tombe à zéro), courant du propulseur à plein gaz (A),
    # résistance interne du pack + câblage (ohm)
    # Mini : Emax 2807 1300KV + 7x6 en 4S (~16 000 tr/min plein gaz) ; DFR : X2820 570KV + 10x7 en 6S
    "mini": dict(cellules=4, ah=4.0, poussee=13.0, pas=41.0, courant=25.0, resistance=0.02),  # LiPo 70C
    "dfr": dict(cellules=6, ah=13.5, poussee=25.0, pas=32.0, courant=35.0, resistance=0.04),  # Li-ion 6S3P
}


def helmbold(ar):
    return 2 * math.pi * ar / (2 + math.sqrt(4 + ar * ar))


def masse_kg():
    m_imp, _ = D.imprime()
    m_comp = sum(q * m for _, q, m, _ in D.COMPOSANTS)
    m_bat = list(D.BATTERIES.values())[0][0]
    return (m_imp + m_comp + m_bat) / 1000


def inerties():
    """Moments d'inertie (kg.m²) autour du centre de gravité, à partir des masses des pièces
    imprimées (cad/out*/masses.csv) et des composants achetés (calc/dimensionnement.py)."""
    import csv
    import pieces as P
    pts = []   # (masse kg, x m, y m, étalement en y m)
    bornes = P.bornes_segments()
    out = os.path.join(RACINE, "cad", "out" if VERSION == "dfr" else f"out_{VERSION}", "masses.csv")
    with open(out) as fh:
        for r in csv.DictReader(fh):
            if r["piece"].startswith("TOTAL"):
                continue
            m, x, nom = float(r["masse_totale_g"]) / 1000, float(r["x_cg_mm"]), r["piece"]
            y, etal = 0.0, 0.0
            if nom.startswith("aile_segment_"):
                a_, b_ = bornes[int(nom.split("_")[2]) - 1]
                y, etal = (a_ + b_) / 2, b_ - a_
            elif nom.startswith("aileron_"):
                y, etal = (AILERON_DEBUT + AILERON_FIN) / 2, (AILERON_FIN - AILERON_DEBUT) / 2
            elif nom.startswith("saumon"):
                y = ENVERGURE / 2
            elif nom.startswith(("pylone", "support_moteur", "platine", "patte", "bloc_queue")):
                y = POUTRE_Y
            elif nom.startswith(("cadre_servo", "trappe_servo", "guignol_aileron")):
                y = AILERON_DEBUT
            elif nom.startswith(("stab_segment", "profondeur")):
                y, etal = STAB_DEMI_ENV / 2, STAB_DEMI_ENV
            if nom.startswith(("support_moteur", "platine", "patte")):   # 4 exemplaires, avant et arrière
                for dx in (-MOTEUR_ECART, MOTEUR_ECART):
                    pts.append((m / 2, CG_X + dx, y, 0))
                continue
            pts.append((m, x, y, etal))
    for nom, q, mg, x in D.COMPOSANTS:
        m = q * mg / 1000
        if "VTOL" in nom:
            for dx in (-MOTEUR_ECART, MOTEUR_ECART):
                pts.append((m / 2, CG_X + dx, POUTRE_Y, 0))
        elif "poutres" in nom:
            pts.append((m, x, POUTRE_Y, 0))
        elif "longeron principal" in nom:
            pts.append((m, x, 0, 2 * LONGERON_PRINC_FIN))
        elif "longerons extérieurs" in nom:
            pts.append((m, x, (LONGERON_EXT_DEBUT + LONGERON_EXT_FIN) / 2, LONGERON_EXT_FIN - LONGERON_EXT_DEBUT))
        elif "ailerons" in nom:
            pts.append((m, x, AILERON_DEBUT, 0))
        else:
            pts.append((m, x, 0, 0))
    pts.append((list(D.BATTERIES.values())[0][0] / 1000, X_BATTERIE, 0, 0))
    ixx = sum(m * ((y / 1000) ** 2 + (e / 1000) ** 2 / 12 + 0.03 ** 2) for m, x, y, e in pts)
    iyy = sum(m * (((x - CG_X) / 1000) ** 2 + 0.03 ** 2) for m, x, y, e in pts)
    izz = sum(m * (((x - CG_X) / 1000) ** 2 + (y / 1000) ** 2 + (e / 1000) ** 2 / 12) for m, x, y, e in pts)
    return ixx, iyy, izz


def gaz_stationnaire(m):
    """Sortie moteur (0..1) qui soutient l'avion, avec la courbe de poussée MOT_THST_EXPO."""
    f = 1 / (4 * D.POUSSEE_MAX_MOTEUR * D.AFFAISSEMENT / m)
    return (-(1 - EXPO) + math.sqrt((1 - EXPO) ** 2 + 4 * EXPO * f)) / (2 * EXPO)


def modele():
    v = PAR_VERSION[VERSION]
    m = masse_kg()
    S = CORDE * ENVERGURE / 1e6
    b = ENVERGURE / 1000
    c = CORDE / 1000
    AR = b * b / S
    a_w = helmbold(AR)
    # empennage horizontal (H, dérives en bout : effet de plaque)
    S_t = 2 * STAB_DEMI_ENV * STAB_CORDE / 1e6
    a_t = helmbold(2 * STAB_DEMI_ENV / STAB_CORDE * 1.2)
    eta, deps, tau_e = 0.9, 2 * a_w / (math.pi * AR), 0.55
    l_t = (STAB_BA_X + 0.25 * STAB_CORDE - CG_X) / 1000
    V_H = S_t * l_t / (S * c)
    a_tot = a_w + eta * a_t * S_t / S * (1 - deps)
    # point neutre et marge statique (comme calc/essais_virtuels.py)
    w_f = max(s[1] for s in SECTIONS_FUS) / 1000
    L_f = (SECTIONS_FUS[-1][0] - SECTIONS_FUS[0][0]) / 1000
    dcm_fus = 0.012 * w_f ** 2 * L_f / (c * S) * 180 / math.pi
    x_np = ((a_w * 0.25 + eta * a_t * S_t / S * (1 - deps) * (STAB_BA_X + 0.25 * STAB_CORDE) / CORDE - dcm_fus)
            / (a_w + eta * a_t * S_t / S * (1 - deps)))
    marge = x_np - CG_X / CORDE
    # portance : aile calée à CALAGE_AILE, profil NACA 4412 (portance nulle à -4°)
    cl0 = a_w * math.radians(CALAGE_AILE + 4.0)
    alpha_dec = (D.CL_MAX - cl0) / a_tot
    # équilibre : moment nul vers la vitesse de croisière, gouverne au neutre
    q_cr = 0.5 * 1.225 * D.V_TRANSIT ** 2
    cl_cr = m * 9.81 / (q_cr * S)
    alpha_cr = (cl_cr - cl0) / a_tot
    cm_a = -a_tot * marge
    # dérives (2, en bout de stab)
    S_v = 2 * (DERIVE_CORDE_PIED + DERIVE_CORDE_SAUMON) / 2 * DERIVE_HAUTEUR / 1e6
    a_v = helmbold(2 * DERIVE_HAUTEUR ** 2 / ((DERIVE_CORDE_PIED + DERIVE_CORDE_SAUMON) / 2 * DERIVE_HAUTEUR))
    l_v = (DERIVE_BA_X + 0.3 * DERIVE_CORDE_PIED - CG_X) / 1000
    V_V = S_v * l_v / (S * b)
    # ailerons (bande de théorie des profils) : efficacité d'une gouverne à 25 % de corde ~ 0,5
    y1, y2 = AILERON_DEBUT / 1000, AILERON_FIN / 1000
    cl_da = 2 * a_w * 0.5 * c * (y2 ** 2 - y1 ** 2) / 2 / (S * b)
    coeffs = {
        "s": S, "b": b, "c": c,
        "c_lift_0": cl0, "c_lift_a": a_tot, "c_lift_deltae": 0.0, "c_lift_q": 0.0,
        "mcoeff": 50.0, "oswald": D.OSWALD, "alpha_stall": alpha_dec,
        "c_drag_p": D.CD0, "c_drag_q": 0.0, "c_drag_deltae": 0.02,
        "c_y_0": 0.0, "c_y_b": -(eta * a_v * S_v / S + 0.1), "c_y_p": 0.0, "c_y_r": 0.0,
        "c_y_deltaa": 0.0, "c_y_deltar": 0.0,
        "c_l_0": 0.0, "c_l_p": -a_w / 6, "c_l_b": -0.05, "c_l_r": cl_cr / 4,
        "c_l_deltaa": cl_da * DEBATTEMENT, "c_l_deltar": 0.0,
        "c_m_0": -cm_a * alpha_cr, "c_m_a": cm_a,
        "c_m_q": -2 * eta * a_t * V_H * l_t / c - 2.0,
        "c_m_deltae": eta * a_t * tau_e * V_H * DEBATTEMENT,
        "c_n_0": 0.0, "c_n_b": eta * a_v * V_V - 0.01, "c_n_p": -cl_cr / 8,
        "c_n_r": -2 * eta * a_v * V_V * l_v / b - D.CD0 / 4,
        "c_n_deltaa": -0.1 * cl_cr * cl_da * DEBATTEMENT, "c_n_deltar": 0.0,
        "deltaa_max": DEBATTEMENT, "deltae_max": DEBATTEMENT, "deltar_max": DEBATTEMENT,
        "CGOffset": [0.0, 0.0, 0.0],
    }
    # le simulateur d'avion applique les moments comme des accélérations (inertie unité) :
    # on divise chaque coefficient de moment par l'inertie réelle autour de son axe
    ixx, iyy, izz = inerties()
    for k in list(coeffs):
        if k.startswith("c_l_"):
            coeffs[k] /= ixx
        elif k.startswith("c_m_"):
            coeffs[k] /= iyy
        elif k.startswith("c_n_"):
            coeffs[k] /= izz
    diag = 2 * math.hypot(MOTEUR_ECART, POUTRE_Y) / 1000
    hover = gaz_stationnaire(m)
    # Calibration des moteurs VTOL du simulateur (SIM_Motor) : poussée totale à la commande c et
    # à la tension V = (V/Vmax)² x (m_frame g / hoverThrOut) x ((1-expo) c + expo c²).
    # On choisit hoverThrOut pour que plein gaz donne la poussée max réelle
    # (table du fabricant, à la tension nominale) ; le gaz de stationnaire et l'effet de la batterie
    # qui faiblit en découlent.
    # La poussée max du fabricant est donnée à la tension nominale (3,7 V par élément) ; le
    # simulateur la fait varier comme le carré de la tension (régime moteur proportionnel à la tension).
    m_frame = m / 1.5          # le simulateur multiplie la masse « frame » par 1,5
    hover_json = m_frame / (4 * D.POUSSEE_MAX_MOTEUR * (4.2 / 3.7) ** 2)
    # puissance : le simulateur suppose un courant proportionnel à la poussée
    u_nom = 3.7 * v["cellules"]
    p_stat = D.analyse(m)["p_stat"]
    frame = {
        "mass": m / 1.5,
        "diagonal_size": diag,
        "disc_area": 4 * math.pi * (HELICE_VTOL / 2000) ** 2,
        "hoverThrOut": hover_json,
        "propExpo": EXPO,
        "maxVoltage": 4.2 * v["cellules"],
        "refVoltage": u_nom,
        "refCurrent": p_stat / (1.5 * u_nom),
        "refBatRes": v["resistance"],
        "moment_inertia": [ixx, iyy, izz],
        "battCapacityAh": v["ah"],
        "num_motors": 4,
    }
    info = dict(masse=m, marge=marge, hover=hover, V_H=V_H, V_V=V_V, poussee=v["poussee"], pas=v["pas"], inerties=(ixx, iyy, izz),
                cellules=v["cellules"], ah=v["ah"])
    return {**coeffs, **frame}, info


def main():
    mod, info = modele()
    chemin = os.path.join(ICI, f"huard_{VERSION}.json")
    with open(chemin, "w") as f:
        json.dump(mod, f, indent=2)
    print(f"{chemin} : masse {info['masse']:.2f} kg, marge statique {info['marge']:.0%}, "
          f"gaz de stationnaire {info['hover']:.2f}, inerties {', '.join(f'{i:.3f}' for i in info['inerties'])} kg.m²")
    return chemin, info


if __name__ == "__main__":
    main()
