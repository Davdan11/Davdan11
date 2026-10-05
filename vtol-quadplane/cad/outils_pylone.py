"""Vue éclatée du collage du pylône sous l'aile : python outils_pylone.py image.png"""
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
xc, zc = P.position_tube(PROFIL_AILE, CORDE, CONDUIT[0], CALAGE_AILE)
tige = trimesh.creation.cylinder(radius=3.5, segment=[(xc, POUTRE_Y, zc + 25), (xc, POUTRE_Y, POUTRE_Z - 2.2 * ecart - 10)],
                                 sections=24)
B.rendu([(aile, "PLA Aero"), (pyl, "PETG"), (tube, "carbone"), (tige, "electronique")], sys.argv[1], -22, -60,
        f"Pylône sous l'aile — Huard {VERSION.upper()} (vert : tige de centrage dans les trous de câbles)", zoom=1.0)
