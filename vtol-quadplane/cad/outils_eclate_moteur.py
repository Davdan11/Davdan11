"""Vue éclatée du support moteur VTOL : python outils_eclate_moteur.py image.png"""
import sys

import matplotlib
import numpy as np
import trimesh

import build as B
import pieces as P
from params import *  # noqa: F403

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from mpl_toolkits.mplot3d.art3d import Poly3DCollection  # noqa: E402

x0, y0, zb = P.X_MOT_AV, POUTRE_Y, POUTRE_Z
r_int, r_ext, zp, s, cote, lg = P._geom_support()
ecart = 22.0  # écartement de la vue éclatée
objs = []
sup = B.vers_trimesh(P.support_moteur(x0), 0.1)
pla = B.vers_trimesh(P.platine_moteur(x0), 0.1)
pla.apply_translation((0, 0, ecart))
mot = trimesh.creation.cylinder(radius=MOTEUR_VTOL_DIAM / 2, height=MOTEUR_VTOL_HAUT, sections=40)
mot.apply_translation((x0, y0, zb + zp + 8 + 2 * ecart + MOTEUR_VTOL_HAUT / 2))
tube = trimesh.creation.cylinder(radius=POUTRE_D / 2, segment=[(x0 - 60, y0, zb), (x0 + 60, y0, zb)], sections=32)
objs = [(sup, "#f08a30"), (pla, "#f0b060"), (mot, "#c03030")]

fig = plt.figure(figsize=(11, 9), dpi=110)
ax = fig.add_subplot(111, projection="3d")
lum = np.array([0.4, -0.5, 0.8]) / np.linalg.norm([0.4, -0.5, 0.8])
for m, c in objs:
    tri = m.vertices[m.faces]
    n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-9
    k = 0.45 + 0.55 * np.abs(n @ lum)
    base = np.array(matplotlib.colors.to_rgb(c))
    ax.add_collection3d(Poly3DCollection(tri, facecolors=np.clip(base * k[:, None], 0, 1), linewidths=0))


def vis(p0, p1, coul, lab):
    ax.plot(*zip(p0, p1), color=coul, lw=2.2, label=lab)


z_bride, z_plat = zb + zp + 4, zb + zp + 4 + ecart
for dx, dy in MOTEUR_VTOL_TROUS:  # vis moteur : par-dessous la platine, dans le moteur
    vis((x0 + dx, y0 + dy, z_plat - 4), (x0 + dx, y0 + dy, z_plat + 4 + ecart + 6), "#1060c0",
        "vis M3 du moteur (posées avant, platine hors de la poutre)" if (dx, dy) == MOTEUR_VTOL_TROUS[0] else None)
for k, (sx, sy) in enumerate(((-1, -1), (-1, 1), (1, -1), (1, 1))):  # vis de coin
    vis((x0 + sx * s, y0 + sy * s, z_bride - 4 - 10), (x0 + sx * s, y0 + sy * s, z_plat + 3), "#10a040",
        "4 vis de coin M3 x 8, par-dessous, à côté du collier" if k == 0 else None)
for dx in (-lg / 4, lg / 4):  # serrage du collier
    zz = zb - r_ext - 3.5
    vis((x0 + dx, y0 - 14, zz), (x0 + dx, y0 + 14, zz), "#8040c0",
        "2 vis de serrage M3 x 16 + écrous (logés)" if dx < 0 else None)
ax.set_xlim(x0 - 45, x0 + 45)
ax.set_ylim(y0 - 45, y0 + 45)
ax.set_zlim(zb - 30, zb + 60 + 2 * ecart)
ax.set_box_aspect((90, 90, 90 + 2 * ecart))
ax.view_init(18, -55)
ax.set_axis_off()
ax.legend(loc="upper left", fontsize=9)
ax.set_title(f"Support moteur VTOL en vue éclatée — Huard {VERSION.upper()}\n(la poutre de carbone passe dans le collier, non dessinée)")
fig.savefig(sys.argv[1], bbox_inches="tight")
