"""Vérification d'intégration : tout ce qu'on achète rentre, tout ce qui bouge bouge.

    python verification.py                     # Huard DFR  -> docs/verification.md
    HUARD_VERSION=mini python verification.py  # Huard Mini -> docs/verification_mini.md

Monte l'avion complet en 3D (pièces imprimées + pièces achetées à leurs cotes) et vérifie :
  1. aucune collision entre deux éléments (volume commun > 0,5 mm³) ;
  2. débattement des ailerons et de la profondeur (±25°) sans toucher ;
  3. disques des hélices (VTOL et propulseur) libres de tout obstacle ;
  4. garde au sol de tout ce qui pend sous l'avion ;
  5. chemins libres : conduit de câbles de l'aile, alésages des poutres, fourreaux des tubes ;
  6. longueurs de tubes carbone à couper, comparées aux tubes achetés ;
  7. toutes les pièces imprimées tiennent sur le plateau et s'impriment sans supports :
     surplombs à plus de 45° limités, et aucune couche qui part dans le vide (la pièce est
     tranchée couche par couche comme dans le trancheur).
Le script s'arrête avec un code d'erreur si un contrôle échoue.
"""
import math
import os
import sys

import cadquery as cq

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pieces as P  # noqa: E402
from params import *  # noqa: E402,F403

V = cq.Vector
TOL = 0.5          # mm³ : en dessous, simple contact (surfaces qui se touchent)
DEBATTEMENT = 25.0  # degrés, gouvernes
SURPLOMB_MAX = 3000  # mm² de surfaces en surplomb tolérées (ponts de petites cavités)
PORTE_A_FAUX_MAX = 6.0  # mm : pièces à 1 paroi (aile, fuselage) : tout est périmètre (pont ≤ 12 mm)
PONT_MAX = 12.5         # mm : pièces pleines avec remplissage : vrais ponts du trancheur (≤ 25 mm)


# ---------------------------------------------------------------------------
# Assemblage : (nom, solide)
# ---------------------------------------------------------------------------
def boite(dims, centre):
    return cq.Workplane().box(*dims).translate(centre)


def cylindre(r, p0, p1):
    p0, p1 = V(*p0), V(*p1)
    d = p1 - p0
    return cq.Workplane().add(cq.Solid.makeCylinder(r, d.Length, p0, d.normalized()))


def cale(x, z):
    a = math.radians(CALAGE_AILE)
    return x * math.cos(a) + z * math.sin(a), -x * math.sin(a) + z * math.cos(a)


def imprime():
    """Pièces imprimées placées dans l'avion."""
    out = []
    dx_m = P.X_MOT_AR - P.X_MOT_AV
    dx_p = P.X_PATTE_AR - P.X_PATTE_AV
    for nom, fn, qte, mat, orient, paroi, rempl, mir in P.inventaire():
        piece = fn()
        cotes = [("d", piece)] + ([("g", P.miroir(piece))] if mir else [])
        for c, wp in cotes:
            n = nom + ("_" + c if mir else "")
            if nom in ("support_moteur", "platine_moteur"):
                for k, (dx, inv) in enumerate([(0, False), (dx_m, False), (0, True), (dx_m, True)]):
                    w = P.miroir(wp) if inv else wp
                    out.append((f"{nom}_{k + 1}", w.translate((dx, 0, 0))))
            elif nom == "patte_atterrissage":
                for k, (dx, inv) in enumerate([(0, False), (dx_p, False), (0, True), (dx_p, True)]):
                    w = P.miroir(wp) if inv else wp
                    out.append((f"{nom}_{k + 1}", w.translate((dx, 0, 0))))
            else:
                out.append((n, wp))
    return out


def achete():
    """Pièces achetées, à leurs cotes (enveloppes simplifiées)."""
    out = []
    zb = POUTRE_Z
    xs_av, xs_ar = P.X_MOT_AV, P.X_MOT_AR
    zm = zb + (POUTRE_D + JEU_TUBE) / 2 + 8.8     # dessus de la platine moteur
    for s in (1, -1):
        y = s * POUTRE_Y
        c = "d" if s > 0 else "g"
        out.append((f"poutre_{c}", cylindre(POUTRE_D / 2, (POUTRE_DEBUT, y, zb), (POUTRE_DEBUT + POUTRE_LONG, y, zb))))
        for k, xm in enumerate((xs_av, xs_ar)):
            out.append((f"moteur_vtol_{c}{k}", cylindre(MOTEUR_VTOL_DIAM / 2, (xm, y, zm + 0.01), (xm, y, zm + MOTEUR_VTOL_HAUT))))
            zh = zm + MOTEUR_VTOL_HAUT + 6
            out.append((f"helice_vtol_{c}{k}", cylindre(HELICE_VTOL / 2, (xm, y, zh - 4), (xm, y, zh + 4))))
        # ESC sur le flanc intérieur de la poutre, entre la patte et le pylône / le support
        for k, xe in enumerate((P.X_PATTE_AV + 40, P.X_PATTE_AR - 40)):
            out.append((f"esc_vtol_{c}{k}", boite((34.5, 5, 17.5), (xe, y - s * (POUTRE_D / 2 + 2.6), zb))))
        # longeron extérieur
        x, z = P.position_tube(PROFIL_AILE, CORDE, LONGERON_EXT_X, CALAGE_AILE)
        out.append((f"longeron_ext_{c}", cylindre(LONGERON_EXT_D / 2, (x, s * LONGERON_EXT_DEBUT, z), (x, s * LONGERON_EXT_FIN, z))))
        # jonc d'aileron
        x, z = P.position_tube(PROFIL_AILE, CORDE, AILERON_JONC[0], CALAGE_AILE)
        out.append((f"jonc_aileron_{c}", cylindre(AILERON_JONC[1] / 2, (x, s * (AILERON_DEBUT + 3), z), (x, s * (AILERON_FIN - 3), z))))
        # servo d'aileron dans son cadre (boîtier + oreilles)
        g = P._servo_aile()
        L, W, H = SERVO["L"], SERVO["W"], SERVO["H"]
        corps = boite((L, H, W), (g["xc"], g["yb"] + H / 2, g["z0"] + W / 2))
        orl = boite((SERVO["oreilles"], SERVO["oreille_ep"], W), (g["xc"], g["yb"] + SERVO["oreille_y"] + SERVO["oreille_ep"] / 2, g["z0"] + W / 2))
        srv = P.caler(corps.union(orl), CALAGE_AILE)
        out.append((f"servo_aileron_{c}", srv if s > 0 else P.miroir(srv)))
    x, z = P.position_tube(PROFIL_AILE, CORDE, LONGERON_PRINC_X, CALAGE_AILE)
    out.append(("longeron_principal", cylindre(LONGERON_PRINC_D / 2, (x, -LONGERON_PRINC_FIN, z), (x, LONGERON_PRINC_FIN, z))))
    x, z = P.position_tube(PROFIL_AILE, CORDE, GOUPILLE_X, CALAGE_AILE)
    out.append(("goupille", cylindre(GOUPILLE_D / 2, (x, -GOUPILLE_FIN, z), (x, GOUPILLE_FIN, z))))
    prise = STAB_DEMI_ENV + 12
    for nom, (xc, d) in (("longeron_stab", (STAB_LONGERON_X, STAB_LONGERON_D)), ("jonc_stab", (STAB_JONC_X, STAB_JONC_D))):
        xs = STAB_BA_X + xc * STAB_CORDE
        zs = STAB_Z + P.naca_cambrure(STAB_PROFIL, xc) * STAB_CORDE
        out.append((nom, cylindre(d / 2, (xs, -prise, zs), (xs, prise, zs))))
    xj = STAB_BA_X + PROFONDEUR_JONC[0] * STAB_CORDE
    out.append(("jonc_profondeur", cylindre(PROFONDEUR_JONC[1] / 2, (xj, -STAB_DEMI_ENV + 2, STAB_Z), (xj, STAB_DEMI_ENV - 2, STAB_Z))))
    # servo de profondeur : boîtier enfoncé dans le bloc droit jusqu'aux oreilles
    L, W, H = SERVO["L"], SERVO["W"], SERVO["H"]
    face = POUTRE_Y - (POUTRE_D / 2 + 7)
    y_fond = face + SERVO["oreille_y"]
    zc = STAB_Z + 6 + 0.2 + W / 2
    corps = boite((L, H, W), (P.X_SERVO_PROF, y_fond - H / 2, zc))
    orl = boite((SERVO["oreilles"], SERVO["oreille_ep"], W), (P.X_SERVO_PROF, face - SERVO["oreille_ep"] / 2, zc))
    out.append(("servo_profondeur", corps.union(orl)))
    # propulseur
    xm = SECTIONS_FUS[-1][0]
    dp, lp = POUSSEUR_DIMS
    out.append(("moteur_propulseur", cylindre(dp / 2, (xm + 0.01, 0, POUSSEUR_Z), (xm + lp, 0, POUSSEUR_Z))))
    out.append(("helice_propulseur", cylindre(HELICE_POUSSEUR / 2, (xm + lp + 4, 0, POUSSEUR_Z), (xm + lp + 14, 0, POUSSEUR_Z))))
    # batterie, électronique
    lb, wb, hb = BATTERIE
    out.append(("batterie", boite((lb - 0.05, wb, hb), (X_BATTERIE, 0, PLATEAU_Z + 2 + hb / 2 + 0.01))))
    x0c, x1c = COMPAGNON_X
    xf = x0c + FC_DIMS[0] / 2 - 5
    out.append(("controleur_de_vol", boite(FC_DIMS, (xf, 0, COMPAGNON_Z + 8 + FC_DIMS[2] / 2 + 0.01))))
    w, h, zc_f = P._section_a((TRAPPE_ACCES_X[0] + TRAPPE_ACCES_X[1]) / 2)
    gps = (34, 28, 11) if VERSION == "dfr" else (20, 20, 8)
    xg = (TRAPPE_ACCES_X[0] + TRAPPE_ACCES_X[1]) / 2 + 20
    out.append(("gps_sous_trappe", boite(gps, (xg, 0, zc_f + h / 2 - 1.6 - 3.0 - gps[2] / 2))))   # mousse adhésive 3 mm
    if PI5:
        out.append(("raspberry_pi", boite((85, 56, 20), (x1c - 38, 0, COMPAGNON_Z + 7 + 10 + 0.01))))
        out.append(("modem_4g", boite((89.5, 45.5, 15), (-100, 0, 10))))   # à plat sous le plafond, au-dessus de la batterie
        out.append(("capteur_vitesse", boite((20, 20, 8), (SECTIONS_FUS[3][0] + 20, 0, 6))))
    if NACELLE_X is not None:
        out.append(("nacelle_boitier", boite((70, 70, 30), (NACELLE_X, 0, NACELLE_Z - 15.01))))
        sph = cq.Workplane().add(cq.Solid.makeSphere(37)).translate((NACELLE_X, 0, NACELLE_Z - 131.5 + 37))
        out.append(("nacelle_boule", sph))
    # ESC du propulseur : debout contre le flanc droit, dans la partie droite du fuselage
    xe = COMPAGNON_X[0] + 80 if PI5 else COMPAGNON_X[0] + 35
    we, he, zce = P._section_a(xe)
    out.append(("esc_propulseur", boite((34.5, 5, 17.5), (xe, we / 2 - PAROI_FUS - 6.5, zce + (0.2 if PI5 else -0.1) * he))))
    return out


# ---------------------------------------------------------------------------
# Contrôles
# ---------------------------------------------------------------------------
def bb_chevauche(a, b, marge=0.0):
    return not (a.xmax < b.xmin - marge or b.xmax < a.xmin - marge or a.ymax < b.ymin - marge or
                b.ymax < a.ymin - marge or a.zmax < b.zmin - marge or b.zmax < a.zmin - marge)


def volume_commun(a, b):
    try:
        r = a.intersect(b)
        return sum(s.Volume() for s in r.solids().vals())
    except Exception:
        return -1.0


# collisions voulues : serrage volontaire (patte TPU serrée sur la poutre)
ATTENDU = [("patte_atterrissage", "poutre")]


def attendu(a, b):
    return any((x in a and y in b) or (x in b and y in a) for x, y in ATTENDU)


LIMITES = """
## Ce que ce contrôle ne peut pas garantir

- Les cotes des pièces achetées viennent des fiches techniques. Les oreilles des servos (non publiées) et la taille réelle des tubes carbone sont à mesurer au pied à coulisse à la réception ; une différence se corrige dans les paramètres et tout se régénère.
- Les tolérances d'impression (retrait du PETG, moussage du PLA Aero) : imprimer d'abord un segment d'aile, un support moteur et un cadre de servo pour valider les ajustements.
- Les câbles sont supposés passer dans les conduits prévus (Ø9 mm DFR, Ø7 mm Mini) : utiliser les sections de fil indiquées dans la nomenclature.
- Le comportement en vol (réglages, vibrations, autonomie réelle) ne se vérifie qu'en volant, en suivant le plan d'essais du README.
"""


def main():
    rapport, echecs = [], []
    ok = lambda c, txt: (rapport.append(("✅" if c else "❌") + " " + txt), None if c else echecs.append(txt))

    print("Assemblage...")
    items = imprime() + achete()
    bbs = [(n, w, w.val().BoundingBox()) for n, w in items]
    print(f"{len(items)} éléments")

    # 1. collisions statiques
    collisions = []
    for i in range(len(bbs)):
        for j in range(i + 1, len(bbs)):
            (na, wa, ba), (nb, wb, bb) = bbs[i], bbs[j]
            if not bb_chevauche(ba, bb) or attendu(na, nb):
                continue
            v = volume_commun(wa, wb)
            if v > TOL or v < 0:
                collisions.append((na, nb, v))
    rapport.append("\n## 1. Collisions entre éléments\n")
    ok(not collisions, f"{len(items)} éléments montés ({len(P.inventaire())} modèles de pièces imprimées + pièces achetées) : "
       + ("aucune collision" if not collisions else f"{len(collisions)} collision(s)"))
    for na, nb, v in collisions:
        rapport.append(f"   - {na} ↔ {nb} : {v:.1f} mm³")

    # 2. débattement des gouvernes
    rapport.append("\n## 2. Débattement des gouvernes (±%g°)\n" % DEBATTEMENT)
    fixes = {n: w for n, w, _ in bbs if n.startswith(("aile_segment", "saumon", "stab_segment", "bloc_queue", "cadre_servo", "trappe_servo",
                                                    "longeron", "jonc_stab", "servo_profondeur", "servo_aileron"))}
    xh = AILERON_X * CORDE
    zh = P.naca_surfaces(PROFIL_AILE, CORDE, AILERON_X)[0]
    hx, hz = cale(xh, zh)
    gouv = [(n, w, (hx, hz)) for n, w, _ in bbs if n.startswith(("aileron_", "guignol_aileron"))]
    xh2 = STAB_BA_X + PROFONDEUR_X * STAB_CORDE
    zh2 = STAB_Z + P.naca_surfaces(STAB_PROFIL, STAB_CORDE, PROFONDEUR_X)[0]
    gouv += [(n, w, (xh2, zh2)) for n, w, _ in bbs if n.startswith(("profondeur_", "guignol_profondeur"))]
    gouv += [(n, w, (xh2, zh2)) for n, w, _ in bbs if n == "jonc_profondeur"]
    gouv += [(n, w, (hx, hz)) for n, w, _ in bbs if n.startswith("jonc_aileron")]
    probleme_g = []
    for ang in (-DEBATTEMENT, -DEBATTEMENT / 2, DEBATTEMENT / 2, DEBATTEMENT):
        for n, w, (ax, az) in gouv:
            wr = w.rotate((ax, 0, az), (ax, 1, az), ang)
            bw = wr.val().BoundingBox()
            for nf, wf in fixes.items():
                if bb_chevauche(bw, wf.val().BoundingBox()):
                    v = volume_commun(wr, wf)
                    if v > TOL:
                        probleme_g.append(f"{n} à {ang:+.0f}° touche {nf} ({v:.1f} mm³)")
    ok(not probleme_g, "ailerons, profondeurs, guignols et joncs tournent librement de -%g° à +%g°" % (DEBATTEMENT, DEBATTEMENT)
       if not probleme_g else f"{len(probleme_g)} contact(s) en braquant les gouvernes")
    rapport += ["   - " + p for p in probleme_g[:20]]

    # 3. hélices : déjà dans le contrôle 1 (disques balayés) ; on le rappelle
    rapport.append("\n## 3. Hélices\n")
    h_coll = [c for c in collisions if "helice" in c[0] or "helice" in c[1]]
    ok(not h_coll, f"les 4 disques d'hélices VTOL ({HELICE_VTOL / 25.4:.0f} po) et le disque propulsif "
       f"({HELICE_POUSSEUR / 25.4:.0f} po) ne touchent rien (aile, stab, dérives, fuselage, autres hélices)")

    # 4. garde au sol
    rapport.append("\n## 4. Garde au sol\n")
    sol = POUTRE_Z - PATTE_LONG
    bas = sorted(((b.zmin - sol, n) for n, w, b in bbs if not n.startswith("patte")), key=lambda t: t[0])[:4]
    ok(bas[0][0] >= 10, f"sol à z = {sol:.0f} mm ; plus bas élément : {bas[0][1]} à {bas[0][0]:.0f} mm du sol"
       + "".join(f" ; {n} {d:.0f} mm" for d, n in bas[1:]))

    # 5. chemins libres
    rapport.append("\n## 5. Chemins libres (câbles et tubes)\n")
    solides = {n: w.val() for n, w, _ in bbs if not any(n.startswith(p) for p in (
        "poutre", "longeron", "goupille", "jonc", "moteur", "helice", "servo", "batterie", "controleur", "gps", "raspberry",
        "modem", "capteur", "nacelle", "esc"))}

    def libre(points, exclus=()):
        bloque = []
        for p in points:
            for n, s in solides.items():
                if n in exclus:
                    continue
                bb = s.BoundingBox()
                if bb.xmin <= p.x <= bb.xmax and bb.ymin <= p.y <= bb.ymax and bb.zmin <= p.z <= bb.zmax and s.isInside(p):
                    bloque.append((n, p))
        return bloque

    # conduit de câbles, du pylône/servo jusqu'au fuselage
    xc, zc = cale(CONDUIT[0] * CORDE, P.naca_cambrure(PROFIL_AILE, CONDUIT[0]) * CORDE)
    pts = [V(xc + dx, y, zc + dz) for y in [DEMI_LARGEUR_FUS + 2 + k * 6 for k in range(int((P._servo_aile()["y0"] - DEMI_LARGEUR_FUS) / 6))]
           for dx, dz in ((0, 0), (1.5, 0), (-1.5, 0), (0, 1.5), (0, -1.5))]
    b = libre(pts)
    ok(not b, f"conduit de câbles de l'aile (Ø{2 * CONDUIT[1]:.0f} mm) libre du flanc du fuselage jusqu'au servo d'aileron, "
       "en passant au-dessus du pylône" if not b else f"conduit bloqué : {sorted(set(n for n, _ in b))}")
    # alésages des poutres
    pts = [V(POUTRE_DEBUT + 1 + k * 5, POUTRE_Y, POUTRE_Z + dz) for k in range(int((POUTRE_LONG - 2) / 5) + 1) for dz in (0, POUTRE_D / 2 - 0.5, -(POUTRE_D / 2 - 0.5))]
    b = [x for x in libre(pts) if not x[0].startswith("patte")]
    ok(not b, f"la poutre de {POUTRE_D:.0f} mm passe dans les supports moteurs, le pylône et le bloc de queue"
       if not b else f"poutre bloquée par : {sorted(set(n for n, _ in b))}")
    # longerons et goupille
    for nom, xcf, d, y0, y1 in (("longeron principal", LONGERON_PRINC_X, LONGERON_PRINC_D, -LONGERON_PRINC_FIN, LONGERON_PRINC_FIN),
                                ("goupille d'aile", GOUPILLE_X, GOUPILLE_D, -GOUPILLE_FIN, GOUPILLE_FIN),
                                ("longeron extérieur", LONGERON_EXT_X, LONGERON_EXT_D, LONGERON_EXT_DEBUT, LONGERON_EXT_FIN)):
        x, z = P.position_tube(PROFIL_AILE, CORDE, xcf, CALAGE_AILE)
        pts = [V(x + dx, y0 + (y1 - y0) * k / 60, z + dz) for k in range(61) for dx, dz in ((0, 0), (d / 2 - 0.4, 0), (0, d / 2 - 0.4), (0, -(d / 2 - 0.4)))]
        b = libre(pts)
        ok(not b, f"{nom} Ø{d:g} mm : passage libre de Y = {y0:.0f} à {y1:.0f} mm" if not b else f"{nom} bloqué par {sorted(set(n for n, _ in b))}")
    # vis de retenue de l'aile : trou dégagé au-dessus et au-dessous du longeron
    x, z = P.position_tube(PROFIL_AILE, CORDE, LONGERON_PRINC_X, CALAGE_AILE)
    pts = [V(x, P.Y_VIS_AILE, z + dz) for dz in (-20, -14, -10, 10, 14, 20)]
    b = [p for p in libre(pts) if p[0].startswith("aile_segment_1")]
    ok(not b, f"trou de la vis nylon de retenue d'aile (Y = {P.Y_VIS_AILE:.0f} mm) dégagé à travers l'aile")
    # prises du longeron de stab dans les blocs de queue
    xs = STAB_BA_X + STAB_LONGERON_X * STAB_CORDE
    face = POUTRE_Y - (POUTRE_D / 2 + 7)
    pts = [V(xs, face + k, STAB_Z) for k in (2, 6, 10)]
    b = libre(pts)
    ok(not b, "prises du longeron de stab ouvertes côté intérieur des blocs de queue (12 mm)")

    # 6. tubes à couper
    rapport.append("\n## 6. Tubes carbone : longueurs à couper\n")
    coupes = [("poutres", f"{POUTRE_D:g} x {POUTRE_D - 2:g}", 2, POUTRE_LONG, 1000),
              ("longeron principal", f"{LONGERON_PRINC_D:g} x {LONGERON_PRINC_D - 2:g}", 1, 2 * LONGERON_PRINC_FIN, 1000),
              ("longerons extérieurs", f"{LONGERON_EXT_D:g} x {LONGERON_EXT_D - 2:g}", 2, LONGERON_EXT_FIN - LONGERON_EXT_DEBUT, 1000),
              ("goupille d'aile", f"jonc {GOUPILLE_D:g}", 1, 2 * GOUPILLE_FIN, 1000),
              ("longeron de stab", f"{STAB_LONGERON_D:g} x {STAB_LONGERON_D - 2:g}", 1, 2 * STAB_DEMI_ENV + 24, 1000),
              ("jonc de stab", f"jonc {STAB_JONC_D:g}", 1, 2 * STAB_DEMI_ENV + 24, 1000),
              ("joncs d'aileron", f"jonc {AILERON_JONC[1]:g}", 2, AILERON_FIN - AILERON_DEBUT - 6, 1000),
              ("jonc de profondeur", f"jonc {PROFONDEUR_JONC[1]:g}", 1, 2 * STAB_DEMI_ENV - 4, 1000)]
    rapport.append("| Usage | Tube (mm) | Qté | Longueur à couper | Tube acheté |")
    rapport.append("|---|---|---:|---:|---:|")
    for nom, t, q, l, achat in coupes:
        rapport.append(f"| {nom} | {t} | {q} | {l:.0f} mm | {achat} mm |")
    ok(all(l <= achat for _, _, _, l, achat in coupes), "chaque tube se coupe dans un tube du commerce de 1000 mm")

    # 7. plateau
    rapport.append("\n## 7. Impression\n")
    trop = []
    for nom, fn, *_ in P.inventaire():
        bb = fn().val().BoundingBox()
        if sorted((bb.xlen, bb.ylen, bb.zlen))[1] > PLATEAU - MARGE_PLATEAU:
            trop.append(nom)
    ok(not trop, f"toutes les pièces tiennent sur le plateau {PLATEAU:.0f} mm (voir build.py pour l'orientation)")
    # imprimabilité sans supports : surfaces tournées vers le bas (> 45°) hors plateau,
    # dans l'orientation d'impression choisie par build.py
    import numpy as np
    import build as B
    lignes, mauvais = [], []
    for nom, fn, qte, mat, orient, *_ in P.inventaire():
        m = B.vers_trimesh(B.orienter(fn(), orient), 0.1)
        n, c, a = m.face_normals, m.triangles_center, m.area_faces
        bas = (n[:, 2] < -0.71) & (c[:, 2] > m.bounds[0, 2] + 0.4)
        surf = a[bas].sum()
        lignes.append((surf, nom))
        if surf > SURPLOMB_MAX:
            mauvais.append(nom)
    ok(not mauvais, f"toutes les pièces s'impriment sans supports dans leur orientation (surplombs ≤ {SURPLOMB_MAX} mm² : "
       "plafonds de petites cavités et trous horizontaux, qui se font en pont)" if not mauvais else
       f"pièces à surplomb trop grand : {mauvais}")
    rapport.append("\n| Pièce | Surplombs > 45° (mm²) |\n|---|---:|")
    rapport += [f"| {n} | {s:.0f} |" for s, n in sorted(lignes, reverse=True)[:8]]
    # porte-à-faux : couche par couche, comme le trancheur (attrape les fines bandes et les
    # plafonds imprimés dans le vide, trop petits en surface pour le contrôle précédent)
    import porte_a_faux as F
    pires, vide = [], []
    for nom, fn, qte, mat, orient, paroi, *_ in P.inventaire():
        d, z = F.pire_porte_a_faux(B.vers_trimesh(B.orienter(fn(), orient), 0.1))
        pires.append((d, z, nom))
        if d > (PORTE_A_FAUX_MAX if paroi is None else PONT_MAX):
            vide.append(f"{nom} ({d:.0f} mm à {z:.0f} mm du plateau)")
    ok(not vide, f"aucune couche ne part dans le vide : pièces à 1 paroi (aile, fuselage) ≤ {PORTE_A_FAUX_MAX:g} mm "
       f"du bord soutenu (pont ≤ {2 * PORTE_A_FAUX_MAX:g} mm) ; pièces pleines ≤ {PONT_MAX:g} mm (pont ≤ "
       f"{2 * PONT_MAX:g} mm, comme le plafond de la baie du servo de profondeur)"
       if not vide else f"couches imprimées dans le vide : {vide}")
    rapport.append("\n| Pièce | Pire porte-à-faux (mm) | Hauteur (mm) |\n|---|---:|---:|")
    rapport += [f"| {n} | {d:.1f} | {z:.0f} |" for d, z, n in sorted(pires, reverse=True)[:8]]

    titre = "Huard DFR" if VERSION == "dfr" else "Huard Mini"
    entete = [f"# Vérification d'intégration — {titre}\n",
              "Généré par `cad/verification.py` : l'avion est monté en 3D avec toutes les pièces imprimées et "
              "toutes les pièces achetées à leurs cotes (moteurs, hélices, servos, ESC, batterie, contrôleur de vol, "
              "GPS" + (", Raspberry Pi, modem, capteur de vitesse, nacelle" if PI5 else "") + ", tubes carbone), "
              "puis chaque contrôle est fait par calcul.\n",
              f"**Résultat : {'tout est bon' if not echecs else str(len(echecs)) + ' contrôle(s) en échec'}.**\n"]
    texte = "\n".join(entete + rapport) + "\n" + LIMITES
    racine = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    nom = "verification.md" if VERSION == "dfr" else f"verification_{VERSION}.md"
    with open(os.path.join(racine, "docs", nom), "w") as f:
        f.write(texte)
    print(texte)
    sys.exit(1 if echecs else 0)


if __name__ == "__main__":
    main()
