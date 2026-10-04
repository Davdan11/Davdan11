"""Dessine la coupe de l'aile au droit du servo d'aileron.

    python outils_coupe_servo.py image.png
    HUARD_VERSION=mini python outils_coupe_servo.py image.png
"""
import math
import sys

import matplotlib
import numpy as np
from matplotlib.path import Path
from matplotlib.patches import PathPatch, Polygon as MP
from shapely.geometry import Polygon as SP

import build as B
import pieces as P
from params import *  # noqa: F403

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

i = P.segments_aileron()[0]
g = P._servo_aile()
a = math.radians(CALAGE_AILE)


def R(x, z):
    return x * math.cos(a) + z * math.sin(a), -x * math.sin(a) + z * math.cos(a)


def dessine(ax, wp, y, col, lab):
    m = B.vers_trimesh(wp, 0.05)
    s = m.section([0, 1, 0], [0, y, 0])
    if s is None:
        return
    geom = None
    for e in s.discrete:
        p = SP(np.c_[e[:, 0], e[:, 2]]).buffer(0)
        geom = p if geom is None else geom.symmetric_difference(p)
    polys = [geom] if geom.geom_type == "Polygon" else list(geom.geoms)
    for k, pg in enumerate(polys):
        verts, codes = [], []
        for ring in [pg.exterior, *pg.interiors]:
            xy = np.asarray(ring.coords)
            verts += list(xy)
            codes += [Path.MOVETO] + [Path.LINETO] * (len(xy) - 2) + [Path.CLOSEPOLY]
        ax.add_patch(PathPatch(Path(verts, codes), fc=col, ec="k", lw=0.5, alpha=0.9,
                               label=lab if k == 0 else None))


fig, ax = plt.subplots(figsize=(13, 5.8))
y_corps = g["yb"] + SERVO["oreille_y"] + SERVO["oreille_ep"] / 2   # coupe au niveau des oreilles
dessine(ax, P.segment_aile(i), y_corps, "#a8a8a0", "aile")
dessine(ax, P.aileron(i), y_corps, "#5577aa", "aileron")
dessine(ax, P.cadre_servo_aile(), y_corps, "#f0a040", "cadre de servo PETG (collé dans l'aile)")
dessine(ax, P.trappe_servo_aile(), g["y0"] + 3, "#c05000", "trappe PETG (2 vis M2)")
dessine(ax, P.guignol_aileron(), P.Y_GUIGNOL_AILERON, "#e07020", "guignol PETG (projeté)")
L, W = SERVO["L"], SERVO["W"]
xc, z0 = g["xc"], g["z0"]
o = SERVO["oreilles"] / 2
ax.add_patch(MP([R(xc - o, z0), R(xc + o, z0), R(xc + o, z0 + W), R(xc - o, z0 + W)], closed=True,
                fc="#2a9a50", ec="k", alpha=0.95, label="servo : oreilles dans leurs encoches"))
p0, p1 = R(g["xs"], z0 - SERVO_TRAPPE_EP), R(g["xs"], z0 - 12)
ax.plot([p0[0], p1[0]], [p0[1], p1[1]], color="#c03030", lw=4, label="palonnier (sort par la fente de la trappe)")
x0g, _ = P._x_guignol(CORDE, AILERON_X + AILERON_JEU / 2 / CORDE)
zl = min(P.naca_surfaces(PROFIL_AILE, CORDE, x0g / CORDE))
gq = R(x0g + 3, zl - 0.85 * GUIGNOL_HAUT * CORDE)
ax.plot([p1[0], gq[0]], [p1[1], gq[1]], color="k", lw=1.8, ls="--", label="tringle 1,5 mm")
ax.autoscale_view()
ax.set_aspect("equal")
ax.grid(alpha=0.25)
ax.legend(loc="upper right", fontsize=8.5)
ax.set_title(f"Servo d'aileron, coupe à travers l'aile — Huard {VERSION.upper()}")
ax.set_xlabel("mm (bord d'attaque à gauche)")
plt.tight_layout()
plt.savefig(sys.argv[1], dpi=110)
