"""Bilan de masse et performances du quadplane.

    python calc/dimensionnement.py

Lit la masse des pièces imprimées dans cad/out/masses.csv (générée par
cad/build.py) et écrit docs/bilan.md. Les coefficients aérodynamiques sont
des estimations ; les premiers vols (logs ArduPilot) serviront à les recaler.
"""
import csv
import math
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, os.path.join(RACINE, "cad"))
from params import CORDE, ENVERGURE, HELICE_VTOL  # noqa: E402

G, RHO = 9.81, 1.225

# (élément, quantité, masse unitaire g)
COMPOSANTS = [
    ("Moteur VTOL 3510 ~700 KV", 4, 100),
    ("Hélice VTOL 12x4.5 (2 CW + 2 CCW)", 4, 22),
    ("ESC VTOL 40 A (AM32 / BLHeli_32)", 4, 25),
    ("Moteur propulsif 2814 ~900 KV", 1, 110),
    ("Hélice propulsive 10x7E", 1, 20),
    ("ESC propulsif 40 A", 1, 30),
    ("Contrôleur de vol Matek H743-WING V3", 1, 30),
    ("GPS + compas Matek M10Q-5883", 1, 15),
    ("Capteur de vitesse Matek ASPD-4525 + Pitot", 1, 10),
    ("Récepteur ExpressLRS", 1, 5),
    ("Radio télémétrie SiK 915 MHz", 1, 25),
    ("Servo 9 g pignons métal", 3, 13),
    ("Tube carbone 16x14x1000 (poutres)", 2, 73),
    ("Tube carbone 12x10x1000 (longeron principal)", 1, 54),
    ("Tube carbone 8x6x1000 (longerons extérieurs, coupé en 2)", 1, 34),
    ("Jonc carbone 6 mm x 300 (goupille d'aile)", 1, 13),
    ("Tube carbone 6x4x700 (longeron du stab)", 1, 17),
    ("Joncs carbone 3 mm et 2 mm (stab, gouvernes)", 1, 15),
    ("Câblage, connecteurs, BEC", 1, 150),
    ("Visserie, guignols, colle, ruban", 1, 70),
]

BATTERIES = {
    "4S2P 21700 Molicel P45B (9 Ah)": (600, 14.4 * 9.0),
    "4S3P 21700 Molicel P45B (13,5 Ah)": (900, 14.4 * 13.5),
}

# Hypothèses aérodynamiques
CD0 = 0.045           # traînée parasite (poutres, moteurs VTOL arrêtés, fuselage)
OSWALD = 0.80
CL_MAX = 1.30
ETA_CROISIERE = 0.55  # hélice x moteur x ESC
FM = 0.60             # figure de mérite des hélices VTOL
ETA_MOTEUR = 0.80
P_AVIONIQUE = 6.0     # W
UTILISABLE = 0.85     # fraction de l'énergie batterie utilisée
MARGE_DECROCHAGE = 1.35  # vitesse mini de croisière = 1,35 x Vs
T_VTOL_S = 120        # temps total de vol stationnaire (décollage + atterrissage)
POUSSEE_MAX_MOTEUR = 1.6  # kg par moteur VTOL, 4S, hélice 12 po (table du fabricant)


def masse_imprimee():
    f = os.path.join(RACINE, "cad", "out", "masses.csv")
    if not os.path.exists(f):
        return 1220.0, False
    with open(f) as fh:
        for ligne in csv.reader(fh):
            if ligne and ligne[0].startswith("TOTAL"):
                return float(ligne[-1]), True
    return 1220.0, False


def autonomie(m_kg, e_wh, cd0=None):
    global CD0
    ancien = CD0
    if cd0 is not None:
        CD0 = cd0
    r = analyse(m_kg)
    CD0 = ancien
    v, _, _, pc = r["meilleure"]
    return (e_wh * UTILISABLE - r["P_vol_stat"] * T_VTOL_S / 3600) / pc * 60, r


def analyse(m_kg):
    s = CORDE * ENVERGURE / 1e6
    ar = ENVERGURE / CORDE
    k = 1 / (math.pi * ar * OSWALD)
    w = m_kg * G
    vs = math.sqrt(2 * w / (RHO * s * CL_MAX))
    res = {"S": s, "AR": ar, "W": w, "Vs": vs, "charge": m_kg / s}
    courbe = []
    for v10 in range(110, 241, 5):
        v = v10 / 10
        cl = w / (0.5 * RHO * v * v * s)
        if v < MARGE_DECROCHAGE * vs:  # on garde de la marge au décrochage
            continue
        cd = CD0 + k * cl * cl
        p = w * v / (cl / cd) / ETA_CROISIERE + P_AVIONIQUE
        courbe.append((v, cl, cl / cd, p))
    res["courbe"] = courbe
    res["meilleure"] = min(courbe, key=lambda c: c[3])
    a = 4 * math.pi * (HELICE_VTOL / 2000) ** 2
    p_ideal = w ** 1.5 / math.sqrt(2 * RHO * a)
    res["P_vol_stat"] = p_ideal / (FM * ETA_MOTEUR) + P_AVIONIQUE
    res["T/W"] = 4 * POUSSEE_MAX_MOTEUR / m_kg
    return res


def main():
    m_imp, mesuree = masse_imprimee()
    m_comp = sum(q * m for _, q, m in COMPOSANTS)
    out = []
    p = out.append
    p("# Bilan de masse et performances\n")
    p("Généré par `calc/dimensionnement.py`. Les chiffres aérodynamiques sont des "
      "estimations, à recaler avec les logs des premiers vols.\n")
    p("## Masse\n")
    p("| Élément | Qté | Masse unitaire (g) | Total (g) |")
    p("|---|---:|---:|---:|")
    src = "cad/out/masses.csv" if mesuree else "estimation"
    p(f"| Pièces imprimées ({src}) | 1 | {m_imp:.0f} | {m_imp:.0f} |")
    for nom, q, m in COMPOSANTS:
        p(f"| {nom} | {q} | {m} | {q * m} |")
    p(f"| **Sans batterie** | | | **{m_imp + m_comp:.0f}** |\n")

    p("## Performances estimées\n")
    p("| | " + " | ".join(BATTERIES) + " |")
    p("|---|" + "---:|" * len(BATTERIES))
    lignes = {k: [] for k in ("Masse au décollage", "Charge alaire", "Vitesse de décrochage",
                              "Rapport poussée/poids VTOL", "Puissance en stationnaire",
                              "Vitesse d'autonomie max", "Finesse à cette vitesse",
                              "Puissance en croisière", "Autonomie estimée")}
    for nom, (mb, e_wh) in BATTERIES.items():
        m = (m_imp + m_comp + mb) / 1000
        t, r = autonomie(m, e_wh)
        v, cl, ld, pc = r["meilleure"]
        lignes["Masse au décollage"].append(f"{m:.2f} kg")
        lignes["Charge alaire"].append(f"{r['charge']:.1f} kg/m²")
        lignes["Vitesse de décrochage"].append(f"{r['Vs']:.1f} m/s ({r['Vs'] * 3.6:.0f} km/h)")
        lignes["Rapport poussée/poids VTOL"].append(f"{r['T/W']:.2f}")
        lignes["Puissance en stationnaire"].append(f"{r['P_vol_stat']:.0f} W ({r['P_vol_stat'] / 14.8:.0f} A)")
        lignes["Vitesse d'autonomie max"].append(f"{v:.1f} m/s ({v * 3.6:.0f} km/h)")
        lignes["Finesse à cette vitesse"].append(f"{ld:.1f}")
        lignes["Puissance en croisière"].append(f"{pc:.0f} W")
        lignes["Autonomie estimée"].append(f"**{t:.0f} min** (~{t / 60 * v * 3.6:.0f} km)")
    for k, vals in lignes.items():
        p(f"| {k} | " + " | ".join(vals) + " |")
    p("")
    r = analyse((m_imp + m_comp + 600) / 1000)
    p(f"Surface alaire {r['S']:.3f} m², allongement {r['AR']:.1f}. Hypothèses : "
      f"Cd0 = {CD0}, e = {OSWALD}, rendement de propulsion en croisière {ETA_CROISIERE}, "
      f"figure de mérite VTOL {FM}, {UTILISABLE:.0%} de la batterie utilisée, "
      f"{T_VTOL_S // 60} min de vol stationnaire par vol, "
      f"{POUSSEE_MAX_MOTEUR} kg de poussée max par moteur VTOL.\n")
    mb, e = list(BATTERIES.values())[0]
    m0 = (m_imp + m_comp + mb) / 1000
    t0 = autonomie(m0, e)[0]
    t_cd = autonomie(m0, e, CD0 + 0.01)[0]
    t_m = autonomie(m0 + 0.1, e)[0]
    p(f"Sensibilité (4S2P) : Cd0 + 0,01 → {t_cd - t0:+.0f} min ; 100 g de plus → "
      f"{t_m - t0:+.0f} min. La vitesse de croisière est limitée à "
      f"{MARGE_DECROCHAGE} x Vs pour garder une marge au décrochage.\n")
    texte = "\n".join(out)
    os.makedirs(os.path.join(RACINE, "docs"), exist_ok=True)
    with open(os.path.join(RACINE, "docs", "bilan.md"), "w") as f:
        f.write(texte)
    print(texte)


if __name__ == "__main__":
    main()
