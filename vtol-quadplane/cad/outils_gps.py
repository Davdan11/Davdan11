"""Vue éclatée, de dessous, du berceau du GPS vissé sous la trappe : python outils_gps.py image.png"""
import sys

import trimesh

import build as B
import pieces as P
from params import *  # noqa: F403

g = P.geom_gps()
trappe = B.vers_trimesh(P.trappe_acces(), 0.1)
berceau = B.vers_trimesh(P.support_gps(), 0.1)
berceau.apply_translation((0, 0, -32))
gps = trimesh.creation.box(extents=GPS_DIMS)
gps.apply_translation((g["xg"], 0, g["z_plot"] - 0.5 - GPS_DIMS[2] / 2 - 16))
objs = [(trappe, "PETG"), (gps, "batterie"), (berceau, "PETG")]
for x, y in g["vis"]:
    v = trimesh.creation.cylinder(radius=1.0, segment=[(x, y, g["z_plot"] - 44), (x, y, g["z_plot"] + 2)], sections=16)
    objs.append((v, "electronique"))
B.rendu(objs, sys.argv[1], -32, -55,
        f"Berceau du GPS sous la trappe (vue de dessous) — Huard {VERSION.upper()} : GPS (bleu), 2 vis M2 (vert)",
        zoom=1.0)
