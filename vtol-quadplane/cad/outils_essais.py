"""Kit d'essai : quelques grammes de filament pour valider tous les ajustements critiques
avant d'imprimer l'avion complet.

    python outils_essais.py                     # Huard DFR  -> cad/out/essais/
    HUARD_VERSION=mini python outils_essais.py  # Huard Mini -> cad/out_mini/essais/
"""
import os
import sys

import cadquery as cq

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build as B  # noqa: E402
import pieces as P  # noqa: E402
from params import *  # noqa: E402,F403

JEUX = (0.1, 0.3, 0.5)   # jeux diamétraux essayés ; 0,3 mm est celui du modèle


def jauge_tubes():
    """Barrette PETG : pour chaque tube carbone, 3 trous (jeu 0,1 / 0,3 / 0,5 mm)."""
    diam = sorted({POUTRE_D, LONGERON_PRINC_D, LONGERON_EXT_D, GOUPILLE_D, STAB_LONGERON_D,
                   STAB_JONC_D, AILERON_JONC[1], PROFONDEUR_JONC[1]}, reverse=True)
    pas = [max(d + 0.5 + 4.0, 8.0) for d in diam]
    long = 3 * sum(pas) + 10
    ep, larg = 5.0, max(diam) + 12
    j = cq.Workplane("XY").box(long, larg, ep, centered=False)
    x = 5.0
    for d, p in zip(diam, pas):
        for k, jeu in enumerate(JEUX):
            cx = x + p / 2
            j = j.cut(cq.Workplane("XY", origin=(cx, larg / 2 + 2.5, -1)).circle((d + jeu) / 2).extrude(ep + 2))
            j = j.cut(cq.Workplane("XY", origin=(cx, 3.2, ep - 0.6)).text(f"{d:g}" if k == 1 else ("-" if k == 0 else "+"),
                                                                          3.2, 1, combine=False))
            x += p
    return j


def tranche_aile():
    """Tranche de 20 mm d'un segment d'aile, là où passent le longeron principal, le longeron
    extérieur et le conduit de câbles : valide le PLA Aero et l'ajustement des tubes."""
    y = (LONGERON_EXT_DEBUT + LONGERON_PRINC_FIN) / 2
    i = next(k for k, (a, b) in enumerate(P.bornes_segments()) if a < y < b)
    seg = P.segment_aile(i)
    boite = cq.Workplane().box(400, 20, 200).translate((100, y, 0))
    return seg.intersect(boite)


def tranches_jonction():
    """Les deux côtés d'une jonction du fuselage (avant / milieu), 25 mm chacun :
    valide l'emboîtement de la lèvre."""
    x = COUPES_FUS[2]
    fp = P.fuselage_pieces()
    k = NOMS_TRONCONS_FUS.index("avant")
    a = fp[k].intersect(cq.Workplane().box(25 + 10, 400, 400, centered=(False, True, True)).translate((x - 25, 0, 0)))
    b = fp[k + 1].intersect(cq.Workplane().box(25, 400, 400, centered=(False, True, True)).translate((x, 0, 0)))
    return a, b


def main():
    dos = os.path.join(B.OUT, "essais")
    os.makedirs(dos, exist_ok=True)
    a, b = tranches_jonction()
    kit = [
        ("1_jauge_tubes", jauge_tubes(), "PETG", "Z"),   # 3 parois, 15 %
        ("2_tranche_aile", tranche_aile(), P.MATERIAU_LEGER, "Y"),
        ("3_jonction_cote_avant", a, P.MATERIAU_LEGER, "X"),
        ("3_jonction_cote_milieu", b, P.MATERIAU_LEGER, "X"),
        ("4_support_moteur", P.support_moteur(P.X_MOT_AV), "PETG", "Zinv"),
        ("4_platine_moteur", P.platine_moteur(P.X_MOT_AV), "PETG", "Z"),
        ("5_cadre_servo_aile", P.cadre_servo_aile(), "PETG", "Zcal"),
        ("5_trappe_servo_aile", P.trappe_servo_aile(), "PETG", "Zcal"),
        ("6_guignol_aileron", P.guignol_aileron(), "PETG", "Y"),
    ]
    total = {}
    for nom, wp, mat, orient in kit:
        imp = B.orienter(wp, orient)
        cq.exporters.export(imp, os.path.join(dos, nom + ".stl"), tolerance=0.03, angularTolerance=0.15)
        m = B.vers_trimesh(wp, 0.1)
        g = B.masse(m, mat, None if mat == P.MATERIAU_LEGER else 1.6, 0.4)
        total[mat] = total.get(mat, 0) + g
        print(f"  {nom:26s} {mat:9s} {g:5.1f} g")
    print("  total : " + ", ".join(f"{k} {v:.0f} g" for k, v in total.items()))


if __name__ == "__main__":
    main()
