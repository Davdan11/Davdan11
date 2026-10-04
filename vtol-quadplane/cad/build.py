"""Génère toutes les pièces imprimées du quadplane.

    python build.py            # STL + STEP + masses + rendus
    python build.py --rapide   # STL seulement (pas de rendus)

Sorties dans cad/out/ :
  stl/      pièces orientées pour l'impression (Bambu Lab A1, plateau 256 mm)
  step/     pièces dans le repère avion, pour modifier dans Fusion / Onshape
  assemblage.glb   avion complet (pièces + tubes + moteurs) pour visualiser
  masses.csv       masse estimée de chaque pièce
  rendus/   images de l'assemblage
"""
import csv
import math
import os
import sys

import cadquery as cq
import numpy as np
import trimesh

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pieces as P  # noqa: E402
from params import VERSION  # noqa: E402
from params import *  # noqa: E402,F403

ICI = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ICI, "out" if VERSION == "dfr" else f"out_{VERSION}")

COULEURS = {
    "PLA Aero": (235, 235, 228),
    "PETG": (240, 120, 30),
    "TPU 95A": (40, 40, 40),
    "carbone": (35, 35, 38),
    "moteur": (200, 40, 40),
    "helice": (120, 160, 220),
    "batterie": (60, 120, 200),
    "electronique": (30, 150, 70),
}


def vers_trimesh(wp, tol=0.05):
    verts, tris = wp.val().tessellate(tol, 0.2)
    return trimesh.Trimesh([(v.x, v.y, v.z) for v in verts], tris, process=True)


def orienter(wp, mode, gauche=False):
    if mode == "Y":  # emplanture (côté fuselage) sur le plateau
        wp = wp.rotate((0, 0, 0), (1, 0, 0), -90 if gauche else 90)
    elif mode == "X":
        wp = wp.rotate((0, 0, 0), (0, 1, 0), -90)
    elif mode == "Xinv":
        wp = wp.rotate((0, 0, 0), (0, 1, 0), 90)
    elif mode == "Zinv":
        wp = wp.rotate((0, 0, 0), (1, 0, 0), 180)
    bb = wp.val().BoundingBox()
    return wp.translate((-(bb.xmin + bb.xmax) / 2, -(bb.ymin + bb.ymax) / 2, -bb.zmin))


def masse(m, materiau, paroi, remplissage):
    rho = DENSITE[materiau]
    v = m.volume / 1000.0
    if paroi is None:  # pièce déjà modélisée creuse : imprimée telle quelle
        return rho * v
    coque = min(v, m.area * paroi / 1000.0)
    return rho * (coque + remplissage * (v - coque))


def placements(nom):
    """Copies de la pièce dans l'assemblage (transformations sur la pièce droite)."""
    dx = P.X_MOT_AR - P.X_MOT_AV
    dxp = P.X_PATTE_AR - P.X_PATTE_AV
    if nom == "support_moteur":
        return [(0, False), (dx, False), (0, True), (dx, True)]
    if nom == "patte_atterrissage":
        return [(0, False), (dxp, False), (0, True), (dxp, True)]
    return None


def materiel():
    """Pièces achetées, pour l'assemblage seulement (cylindres simplifiés)."""
    objs = []

    def cyl(r, p0, p1, couleur, sections=32):
        p0, p1 = np.array(p0, float), np.array(p1, float)
        c = trimesh.creation.cylinder(radius=r, segment=[p0, p1], sections=sections)
        objs.append((c, couleur))

    zb = POUTRE_Z
    for s in (-1, 1):
        y = s * POUTRE_Y
        cyl(POUTRE_D / 2, (POUTRE_DEBUT, y, zb), (POUTRE_DEBUT + POUTRE_LONG, y, zb), "carbone")
        for xm in (P.X_MOT_AV, P.X_MOT_AR):
            zm = zb + (POUTRE_D + JEU_TUBE) / 2 + 4.8   # dessus de la platine moteur
            hm = MOTEUR_VTOL_HAUT
            cyl(MOTEUR_VTOL_DIAM / 2, (xm, y, zm), (xm, y, zm + hm), "moteur")
            cyl(2.5, (xm, y, zm + hm), (xm, y, zm + hm + 10), "carbone", 12)
            cyl(HELICE_VTOL / 2, (xm, y, zm + hm + 9), (xm, y, zm + hm + 10), "helice", 48)
        # longerons d'aile extérieurs
        x, z = P.position_tube(PROFIL_AILE, CORDE, LONGERON_EXT_X, CALAGE_AILE)
        cyl(LONGERON_EXT_D / 2, (x, s * LONGERON_EXT_DEBUT, z), (x, s * LONGERON_EXT_FIN, z), "carbone")
    x, z = P.position_tube(PROFIL_AILE, CORDE, LONGERON_PRINC_X, CALAGE_AILE)
    cyl(LONGERON_PRINC_D / 2, (x, -LONGERON_PRINC_FIN, z), (x, LONGERON_PRINC_FIN, z), "carbone")
    xs = STAB_BA_X + STAB_LONGERON_X * STAB_CORDE
    cyl(STAB_LONGERON_D / 2, (xs, -POUTRE_Y - 10, STAB_Z), (xs, POUTRE_Y + 10, STAB_Z), "carbone")
    # propulseur
    xm = SECTIONS_FUS[-1][0]
    dp, lp = POUSSEUR_DIMS
    cyl(dp / 2, (xm, 0, POUSSEUR_Z), (xm + lp, 0, POUSSEUR_Z), "moteur")
    cyl(HELICE_POUSSEUR / 2, (xm + lp + 10, 0, POUSSEUR_Z), (xm + lp + 11, 0, POUSSEUR_Z), "helice", 48)
    # batterie et électronique
    lb, wb, hb = BATTERIE
    bat = trimesh.creation.box(extents=(lb, wb, hb))
    bat.apply_translation((X_BATTERIE, 0, PLATEAU_Z + 2 + hb / 2))
    objs.append((bat, "batterie"))
    x0c, x1c = COMPAGNON_X
    blocs = [(FC_DIMS, (x0c + FC_DIMS[0] / 2 - 5, 0, COMPAGNON_Z + 8 + FC_DIMS[2] / 2))]
    if PI5:
        blocs.append(((85, 56, 20), (x1c - 38, 0, COMPAGNON_Z + 17)))   # Raspberry Pi + modem 4G
    for ext, pos in blocs:
        b = trimesh.creation.box(extents=ext)
        b.apply_translation(pos)
        objs.append((b, "electronique"))
    if NACELLE_X is not None:  # nacelle caméra (boîtier + boule), SIYI ZT6 : 73,5 x 75 x 131,5 mm
        n = trimesh.creation.box(extents=(70, 70, 30))
        n.apply_translation((NACELLE_X, 0, NACELLE_Z - 15))
        objs.append((n, "electronique"))
        boule = trimesh.creation.icosphere(subdivisions=2, radius=37)
        boule.apply_translation((NACELLE_X, 0, NACELLE_Z - 131.5 + 37))
        objs.append((boule, "TPU 95A"))
    return objs


def rendu(scene_objs, chemin, elev, azim, titre, zoom=1.6):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    fig = plt.figure(figsize=(12, 8), dpi=110)
    ax = fig.add_subplot(111, projection="3d")
    lum = np.array([0.4, -0.5, 0.8])
    lum /= np.linalg.norm(lum)
    tous = []
    for m, coul in scene_objs:
        mm = m
        # repère d'affichage : X avant -> on inverse X pour que le nez pointe vers +X
        v = mm.vertices * np.array([-1, 1, 1])
        tri = v[mm.faces]
        n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
        n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-9
        k = 0.45 + 0.55 * np.abs(n @ lum)
        base = np.array(COULEURS[coul]) / 255.0
        cols = np.clip(base[None, :] * k[:, None], 0, 1)
        alpha = 0.25 if coul == "helice" else 1.0
        pc = Poly3DCollection(tri, facecolors=np.c_[cols, np.full(len(cols), alpha)], linewidths=0)
        ax.add_collection3d(pc)
        tous.append(v)
    v = np.vstack(tous)
    lo, hi = v.min(0), v.max(0)
    ax.set_xlim(lo[0], hi[0])
    ax.set_ylim(lo[1], hi[1])
    ax.set_zlim(lo[2], hi[2])
    ax.set_box_aspect(tuple(hi - lo), zoom=zoom)
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()
    ax.set_title(titre)
    fig.subplots_adjust(0, 0, 1, 0.95)
    fig.savefig(chemin, bbox_inches="tight")
    plt.close(fig)


def main():
    rapide = "--rapide" in sys.argv
    for d in ("stl", "step", "rendus"):
        os.makedirs(os.path.join(OUT, d), exist_ok=True)

    lignes, scene, problemes = [], [], []
    limite = PLATEAU - MARGE_PLATEAU
    for nom, fn, qte, mat, orient, paroi, rempl, mir in P.inventaire():
        piece = fn()
        cotes = [(nom + ("_droit" if mir else ""), piece)]
        if mir:
            cotes.append((nom + "_gauche", P.miroir(piece)))
        for nom_f, wp in cotes:
            cq.exporters.export(wp, os.path.join(OUT, "step", nom_f + ".step"))
            imp = orienter(wp, orient, nom_f.endswith("_gauche"))
            cq.exporters.export(imp, os.path.join(OUT, "stl", nom_f + ".stl"),
                                tolerance=0.03, angularTolerance=0.15)
            bb = imp.val().BoundingBox()
            dims = (bb.xlen, bb.ylen, bb.zlen)
            if max(dims) > limite:
                problemes.append(f"{nom_f} : {dims[0]:.0f} x {dims[1]:.0f} x {dims[2]:.0f} mm")
            m = vers_trimesh(wp, 0.05)
            g = masse(m, mat, paroi, rempl)
            copies = placements(nom)
            xg = m.center_mass[0] + (np.mean([dx for dx, _ in copies]) if copies else 0.0)
            lignes.append([nom_f, qte, mat, f"{dims[0]:.0f}x{dims[1]:.0f}x{dims[2]:.0f}",
                           f"{g:.1f}", f"{g * qte:.1f}", f"{xg:.0f}"])
            print(f"  {nom_f:28s} x{qte}  {mat:8s} {lignes[-1][3]:>13s} mm  {g:6.1f} g")

            mr = vers_trimesh(wp, 0.3)
            coul = mat
            if copies is None:
                scene.append((mr, coul))
            else:
                for dx, inv in copies:
                    c = mr.copy()
                    if inv:
                        c.apply_transform(np.diag([1, -1, 1, 1]))
                        c.invert()
                    c.apply_translation((dx, 0, 0))
                    scene.append((c, coul))

    total = sum(float(l[5]) for l in lignes)
    x_cg = sum(float(l[5]) * float(l[6]) for l in lignes) / total
    with open(os.path.join(OUT, "masses.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["piece", "quantite", "materiau", "dimensions_impression_mm", "masse_g",
                    "masse_totale_g", "x_cg_mm"])
        w.writerows(lignes)
        w.writerow(["TOTAL pièces imprimées", "", "", "", "", f"{total:.0f}", f"{x_cg:.0f}"])
    print(f"\nMasse totale des pièces imprimées : {total:.0f} g")
    if problemes:
        print("ATTENTION, pièces trop grandes pour le plateau :")
        for p in problemes:
            print("  ", p)
    else:
        print(f"Toutes les pièces tiennent dans {limite:.0f} x {limite:.0f} x {limite:.0f} mm.")

    scene += materiel()
    sc = trimesh.Scene()
    for i, (m, coul) in enumerate(scene):
        mm = m.copy()
        c = COULEURS[coul]
        mm.visual.face_colors = [*c, 90 if coul == "helice" else 255]
        sc.add_geometry(mm, node_name=f"{coul}_{i}")
    sc.export(os.path.join(OUT, "assemblage.glb"))

    if not rapide:
        r = os.path.join(OUT, "rendus")
        rendu(scene, os.path.join(r, "vue_3-4.png"), 25, -130, f"Huard {VERSION.upper()} — vue 3/4", zoom=1.25)
        rendu(scene, os.path.join(r, "vue_dessus.png"), 90, -90, "Vue de dessus", zoom=1.0)
        rendu(scene, os.path.join(r, "vue_cote.png"), 0, -90, "Vue de côté")
        rendu(scene, os.path.join(r, "vue_face.png"), 5, 180, "Vue de face", zoom=1.0)


if __name__ == "__main__":
    main()
