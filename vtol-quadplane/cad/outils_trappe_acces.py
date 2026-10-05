"""Vue de la trappe d'accès au contrôleur de vol : python outils_trappe_acces.py image.png"""
import sys

import trimesh

import build as B
import pieces as P
from params import *  # noqa: F403

k = NOMS_TRONCONS_FUS.index("milieu")
fus = B.vers_trimesh(P.fuselage_pieces()[k], 0.3)
trappe = B.vers_trimesh(P.trappe_acces(), 0.1)
trappe.apply_translation((0, 0, 45))              # trappe soulevée
plateau = B.vers_trimesh(P.plateau_compagnon(), 0.1)
x0c, _ = COMPAGNON_X
fc = trimesh.creation.box(extents=FC_DIMS)
fc.apply_translation((x0c + FC_DIMS[0] / 2 - 5, 0, COMPAGNON_Z + 8 + FC_DIMS[2] / 2))
g = P.geom_gps()
berceau = B.vers_trimesh(P.support_gps(), 0.1)
gps = trimesh.creation.box(extents=GPS_DIMS)
gps.apply_translation((g["xg"], 0, g["z_plot"] - 0.5 - GPS_DIMS[2] / 2))
for m in (berceau, gps):
    m.apply_translation((0, 0, 45))               # soulevés avec la trappe
objs = [(fus, "PLA Aero"), (plateau, "PETG"), (fc, "electronique"), (trappe, "PETG"), (berceau, "PETG"), (gps, "batterie")]
B.rendu(objs, sys.argv[1], 35, -60,
        f"Trappe d'accès (2 vis M2) et berceau du GPS vissé dessous (bleu) — Huard {VERSION.upper()}", zoom=1.0)
