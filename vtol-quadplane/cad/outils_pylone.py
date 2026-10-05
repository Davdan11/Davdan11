"""Vue éclatée du pylône vissé sous l'aile : python outils_pylone.py image.png"""
import sys

import cadquery as cq
import trimesh

import build as B
import pieces as P
from params import *  # noqa: F403

i = next(k for k, (a, b) in enumerate(P.bornes_segments()) if a < POUTRE_Y < b)
seg = P.segment_aile(i).intersect(cq.Workplane().box(400, 90, 200).translate((100, POUTRE_Y, 0)))
aile = B.vers_trimesh(seg, 0.1)
pyl = B.vers_trimesh(P.pylone(), 0.1)
ecart = 45.0
pyl.apply_translation((0, 0, -ecart))
tube = trimesh.creation.cylinder(radius=POUTRE_D / 2, segment=[(-60, POUTRE_Y, POUTRE_Z - 2.2 * ecart),
                                                                (CORDE + 60, POUTRE_Y, POUTRE_Z - 2.2 * ecart)], sections=40)
import math
ca, sa = math.cos(math.radians(CALAGE_AILE)), math.sin(math.radians(CALAGE_AILE))
def cale(x, z):
    return x * ca + z * sa, -x * sa + z * ca
objs = [(aile, "PLA Aero"), (pyl, "PETG"), (tube, "carbone")]
for x, zl, zh in P.vis_pylone():
    (x0, z0), (x1, z1) = cale(x, zh + 30), cale(x, zl - 4 - ecart)
    vis = trimesh.creation.cylinder(radius=1.5, segment=[(x0, POUTRE_Y, z0), (x1, POUTRE_Y, z1)], sections=20)
    xi, zi = cale(x, zl - 2.5)
    insert = trimesh.creation.cylinder(radius=2.4, segment=[(xi, POUTRE_Y, zi - ecart - 2), (xi, POUTRE_Y, zi - ecart + 2)],
                                       sections=20)
    objs += [(vis, "electronique"), (insert, "moteur")]
B.rendu(objs, sys.argv[1], 28, -60,
        f"Pylône vissé sous l'aile — Huard {VERSION.upper()} : 2 vis M3 fraisées (vert) dans 2 inserts laiton (rouge)",
        zoom=1.0)
