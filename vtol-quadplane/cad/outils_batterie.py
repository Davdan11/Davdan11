"""Coupe de côté du montage de la batterie : python outils_batterie.py image.png"""
import sys

import matplotlib
import numpy as np
from matplotlib.patches import Rectangle

import build as B
import pieces as P
from params import *  # noqa: F403

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

L, W, H = BATTERIE
x0, x1 = PLATEAU_X
y_coupe = (PLATEAU_LARG - 18) / 4 + 9          # passe dans un poteau de la butée
fig, ax = plt.subplots(figsize=(13, 5))
for k, morceau in enumerate(P.fuselage_pieces()[:3]):
    m = B.vers_trimesh(morceau, 0.2)
    s = m.section([0, 1, 0], [0, y_coupe, 0])
    for e in (s.discrete if s is not None else []):
        ax.plot(e[:, 0], e[:, 2], color="#888", lw=0.8)
m = B.vers_trimesh(P.plateau_electronique(), 0.05)
s = m.section([0, 1, 0], [0, y_coupe, 0])
for i, e in enumerate(s.discrete):
    ax.fill(e[:, 0], e[:, 2], color="#e07020", ec="k", lw=0.5, label="plateau PETG + butée arrière" if i == 0 else None)
zb = PLATEAU_Z + 2
ax.add_patch(Rectangle((X_BATTERIE - L / 2, zb), L - 1, H - 1, fc="#3a6ab0", ec="k", alpha=0.85, label="batterie"))
for i, xs in enumerate((x0 + 12, x0 + 45)):
    ax.add_patch(Rectangle((xs - 10, zb - 4), 20, H + 6, fill=False, ec="k", lw=2.2, ls="-",
                           label="2 sangles 20 mm (fermées par l'ouverture du nez)" if i == 0 else None))
ax.axvline(COUPES_FUS[1], color="#c03030", ls="--", lw=1.2)
ax.annotate("ouverture du nez\n(nez amovible)", (COUPES_FUS[1], zb + H + 18), ha="center", color="#c03030", fontsize=9)
ax.annotate("", xy=(X_BATTERIE + L / 2, zb + H / 2), xytext=(X_BATTERIE + L / 2 - 40, zb + H / 2),
            arrowprops=dict(arrowstyle="->", lw=2))
ax.text(X_BATTERIE + L / 2 - 38, zb + H / 2 + 3, "pousser jusqu'à la butée", fontsize=9)
ax.text(X_BATTERIE - L / 2 + 5, zb + 3, "velcro adhésif dessous", fontsize=8, color="w")
ax.set_xlim(COUPES_FUS[0] - 10, X_BATTERIE + L / 2 + 120)
ax.set_aspect("equal")
ax.grid(alpha=0.25)
ax.legend(loc="lower right", fontsize=8.5)
ax.set_title(f"Montage de la batterie, coupe de côté — Huard {VERSION.upper()} (nez à gauche)")
plt.tight_layout()
plt.savefig(sys.argv[1], dpi=110)
