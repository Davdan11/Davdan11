"""Géométrie des pièces imprimées du quadplane.

Chaque fonction renvoie un solide CadQuery placé dans le repère global de
l'avion (voir params.py). build.py se charge de les orienter pour
l'impression et de les exporter.
"""
import math

import cadquery as cq
from shapely.affinity import scale as sh_scale
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

from params import *  # noqa: F403


# ---------------------------------------------------------------------------
# Profils NACA 4 chiffres
# ---------------------------------------------------------------------------
def _naca_params(code):
    return int(code[0]) / 100, int(code[1]) / 10, int(code[2:]) / 100


def naca_epaisseur(code, xc):
    _, _, t = _naca_params(code)
    return 5 * t * (0.2969 * math.sqrt(xc) - 0.1260 * xc - 0.3516 * xc**2
                    + 0.2843 * xc**3 - 0.1036 * xc**4)  # bord de fuite fermé


def naca_cambrure(code, xc):
    m, p, _ = _naca_params(code)
    if m == 0:
        return 0.0
    if xc < p:
        return m / p**2 * (2 * p * xc - xc**2)
    return m / (1 - p) ** 2 * ((1 - 2 * p) + 2 * p * xc - xc**2)


def naca_points(code, corde, n=90):
    """Contour fermé dans le repère de corde : x vers l'arrière, z vers le haut."""
    m, p, _ = _naca_params(code)
    haut, bas = [], []
    for i in range(n + 1):
        xc = 0.5 * (1 - math.cos(math.pi * i / n))
        yt = naca_epaisseur(code, xc)
        yc = naca_cambrure(code, xc)
        if m and xc < p:
            dy = 2 * m / p**2 * (p - xc)
        elif m:
            dy = 2 * m / (1 - p) ** 2 * (p - xc)
        else:
            dy = 0.0
        th = math.atan(dy)
        haut.append(((xc - yt * math.sin(th)) * corde, (yc + yt * math.cos(th)) * corde))
        bas.append(((xc + yt * math.sin(th)) * corde, (yc - yt * math.cos(th)) * corde))
    pts = list(reversed(haut)) + bas[1:-1]
    return pts


def naca_surfaces(code, corde, xc):
    """(z extrados, z intrados) à la fraction de corde xc, repère de corde."""
    yt = naca_epaisseur(code, xc) * corde
    yc = naca_cambrure(code, xc) * corde
    return yc + yt, yc - yt


# ---------------------------------------------------------------------------
# Outils 2D (shapely) -> 3D (CadQuery)
# ---------------------------------------------------------------------------
def _polys(geom):
    if geom.is_empty:
        return []
    if geom.geom_type == "Polygon":
        return [geom]
    return [g for g in geom.geoms if g.geom_type == "Polygon" and g.area > 0.01]


def _wire_xz(coords, y):
    pts = [cq.Vector(x, y, z) for x, z in list(coords)[:-1]]
    return cq.Wire.makePolygon(pts, close=True)


def extrude_xz(geom, y0, y1):
    """Extrude une section 2D (plan XZ) de Y = y0 à Y = y1."""
    solides = []
    for poly in _polys(geom):
        poly = poly.simplify(0.02)
        ext = _wire_xz(poly.exterior.coords, y0)
        ints = [_wire_xz(r.coords, y0) for r in poly.interiors]
        face = cq.Face.makeFromWires(ext, ints)
        solides.append(cq.Solid.extrudeLinear(face, cq.Vector(0, y1 - y0, 0)))
    res = cq.Workplane().add(solides[0])
    for s in solides[1:]:
        res = res.union(cq.Workplane().add(s))
    return res


def section_coque(code, corde, xmin=0.0, xmax=1.0, tubes=(), ames=0, peau=PEAU,
                  ame=AME):
    """Section creuse d'un profil : peau + âmes en zigzag + fourreaux de tubes.

    tubes : liste de (fraction de corde, diamètre du tube)
    """
    profil = Polygon(naca_points(code, corde))
    x0, x1 = xmin * corde, xmax * corde
    zone = profil.intersection(box(x0, -100, x1, 100))
    ferme0 = peau if xmin > 0 else 0
    ferme1 = peau if xmax < 1 else 0
    interieur = profil.buffer(-peau, join_style=2).intersection(
        box(x0 + ferme0, -100, x1 - ferme1, 100))
    coque = zone.difference(interieur)

    if ames:
        a, b = max(x0, 0.06 * corde), min(x1, 0.92 * corde)
        xs = [a + (b - a) * i / ames for i in range(ames + 1)]
        lignes = []
        for i in range(ames):
            za = naca_surfaces(code, corde, xs[i] / corde)
            zb = naca_surfaces(code, corde, xs[i + 1] / corde)
            if i % 2 == 0:
                p, q = (xs[i], za[1] - 2), (xs[i + 1], zb[0] + 2)
            else:
                p, q = (xs[i], za[0] + 2), (xs[i + 1], zb[1] - 2)
            lignes.append(LineString([p, q]).buffer(ame / 2, cap_style=2))
        coque = coque.union(unary_union(lignes).intersection(zone))

    trous = []
    for xc, d in tubes:
        cz = naca_cambrure(code, xc) * corde
        c = Point(xc * corde, cz)
        coque = coque.union(c.buffer(d / 2 + JEU_TUBE / 2 + FOURREAU).intersection(zone))
        trous.append(c.buffer(d / 2 + JEU_TUBE / 2))
    if trous:
        coque = coque.difference(unary_union(trous))
    return coque


def caler(wp, angle, x0=0.0, z0=0.0):
    """Applique une incidence (cabrer = bord de fuite vers le bas) autour de (x0, z0)."""
    return wp.rotate((x0, 0, z0), (x0, 1, z0), angle)


def miroir(wp):
    return wp.mirror("XZ")


def position_tube(code, corde, xc, angle):
    """Coordonnées globales (x, z) d'un tube logé sur la ligne de cambrure."""
    x, z = xc * corde, naca_cambrure(code, xc) * corde
    a = math.radians(angle)
    return x * math.cos(a) + z * math.sin(a), -x * math.sin(a) + z * math.cos(a)


# ---------------------------------------------------------------------------
# Aile
# ---------------------------------------------------------------------------
def bornes_segments():
    y0, y1 = DEMI_LARGEUR_FUS, ENVERGURE / 2
    return [(y0 + (y1 - y0) * i / N_SEGMENTS, y0 + (y1 - y0) * (i + 1) / N_SEGMENTS)
            for i in range(N_SEGMENTS)]


def _tubes_aile(ya, yb):
    tubes = []
    if ya < LONGERON_PRINC_FIN:
        tubes.append((LONGERON_PRINC_X, LONGERON_PRINC_D))
    if yb > LONGERON_EXT_DEBUT and ya < LONGERON_EXT_FIN:
        tubes.append((LONGERON_EXT_X, LONGERON_EXT_D))
    if ya < GOUPILLE_FIN:
        tubes.append((GOUPILLE_X, GOUPILLE_D))
    return tubes


def segment_aile(i):
    """Segment i (0 = emplanture) de la demi-aile droite, sans aileron."""
    ya, yb = bornes_segments()[i]
    tubes = _tubes_aile(ya, yb)
    pleine = section_coque(PROFIL_AILE, CORDE, tubes=tubes, ames=N_AMES)

    a0 = max(ya, AILERON_DEBUT) if yb > AILERON_DEBUT else None
    if a0 is None:
        seg = extrude_xz(pleine, ya, yb)
    else:
        a1 = min(yb, AILERON_FIN)
        xa = AILERON_X - AILERON_JEU / 2 / CORDE
        avant = section_coque(PROFIL_AILE, CORDE, xmax=xa, tubes=tubes,
                              ames=N_AMES - 2)
        seg = extrude_xz(avant, a0, a1)
        if a0 > ya:
            seg = seg.union(extrude_xz(pleine, ya, a0))
        if a1 < yb:
            seg = seg.union(extrude_xz(pleine, a1, yb))

    if i == 2:  # baie de servo d'aileron (servo 9 g couché, palonnier sous l'aile)
        profil = Polygon(naca_points(PROFIL_AILE, CORDE))
        bloc = profil.intersection(box(0.45 * CORDE, -50, 0.64 * CORDE, 50))
        poche = bloc.intersection(box(0.47 * CORDE, -50, 0.62 * CORDE, 10.0))
        yc = ya + 45
        seg = seg.union(extrude_xz(bloc, yc - 22, yc + 22))
        seg = seg.cut(extrude_xz(poche, yc - 15, yc + 15))

    if ya < POUTRE_Y < yb:  # passage des câbles vers la poutre
        trou = (cq.Workplane("XY").workplane(offset=-30)
                .center(0.45 * CORDE, POUTRE_Y).circle(5).extrude(30))
        seg = seg.cut(trou)

    return caler(seg, CALAGE_AILE)


def aileron(i):
    ya, yb = bornes_segments()[i]
    a0, a1 = max(ya, AILERON_DEBUT), min(yb, AILERON_FIN)
    if i == 3:
        a0 += AILERON_JEU / 2
    else:
        a1 -= AILERON_JEU / 2
    xa = AILERON_X + AILERON_JEU / 2 / CORDE
    sect = section_coque(PROFIL_AILE, CORDE, xmin=xa, tubes=[(0.80, 2.0)])
    pleine = Polygon(naca_points(PROFIL_AILE, CORDE)).intersection(
        box(xa * CORDE, -50, CORDE, 50))
    pleine = pleine.difference(Point(0.80 * CORDE, naca_cambrure(PROFIL_AILE, 0.80) * CORDE)
                               .buffer(1.0 + JEU_TUBE / 2))
    ail = extrude_xz(sect, a0, a1)
    ail = ail.union(extrude_xz(pleine, a0, a0 + 1.0)).union(extrude_xz(pleine, a1 - 1.0, a1))
    return caler(ail, CALAGE_AILE)


def saumon():
    y0 = ENVERGURE / 2
    prof = naca_points(PROFIL_AILE, CORDE)
    w0 = cq.Wire.makePolygon([cq.Vector(x, y0, z) for x, z in prof], close=True)
    cx = 0.3 * CORDE
    w1 = cq.Wire.makePolygon([cq.Vector(cx + (x - cx) * 0.55, y0 + 18, z * 0.45)
                              for x, z in prof], close=True)
    s = cq.Workplane().add(cq.Solid.makeLoft([w0, w1], True))
    return caler(s, CALAGE_AILE)


def pylone():
    """Carénage collé sous le segment 2 : reçoit la poutre de 16 mm."""
    l, zb = 24.0, POUTRE_Z
    cote = [(0, zb + 2), (14, zb - 11), (180, zb - 11), (204, zb - 3), (204, -5),
            (110, 6), (14, 4), (0, -6)]
    corps = (cq.Workplane("XZ", origin=(0, POUTRE_Y + l / 2, 0))
             .polyline(cote).close().extrude(l))
    aile = caler(extrude_xz(Polygon(naca_points(PROFIL_AILE, CORDE)),
                            POUTRE_Y - 20, POUTRE_Y + 20), CALAGE_AILE)
    corps = corps.cut(aile)
    try:
        corps = corps.edges("|Y").fillet(3)
    except Exception:
        pass
    alesage = (cq.Workplane("YZ", origin=(-10, POUTRE_Y, POUTRE_Z))
               .circle((POUTRE_D + JEU_TUBE) / 2).extrude(260))
    cable = (cq.Workplane("XY", origin=(0.45 * CORDE, POUTRE_Y, POUTRE_Z))
             .circle(5).extrude(40))
    return corps.cut(alesage).cut(cable)


# ---------------------------------------------------------------------------
# Fuselage
# ---------------------------------------------------------------------------
def _super_ellipse(x, w, h, zc, n=SUPER_ELLIPSE_N, k=64):
    pts = []
    for i in range(k):
        t = 2 * math.pi * i / k
        c, s = math.cos(t), math.sin(t)
        y = w / 2 * math.copysign(abs(c) ** (2 / n), c)
        z = zc + h / 2 * math.copysign(abs(s) ** (2 / n), s)
        pts.append(cq.Vector(x, y, z))
    return cq.Wire.assembleEdges([cq.Edge.makeSpline(pts, periodic=True)])


def _loft_fus(sections, retrait=0.0):
    fils = [_super_ellipse(x, w - 2 * retrait, h - 2 * retrait, zc)
            for x, w, h, zc in sections]
    return cq.Workplane().add(cq.Solid.makeLoft(fils, True))


def _section_a(x):
    """Section interpolée (w, h, zc) à la station x."""
    s = SECTIONS_FUS
    for a, b in zip(s, s[1:]):
        if a[0] <= x <= b[0]:
            t = (x - a[0]) / (b[0] - a[0])
            return tuple(a[i] + t * (b[i] - a[i]) for i in (1, 2, 3))
    raise ValueError(x)


def _lamelle(x, ep, retrait_ext, retrait_int):
    w, h, zc = _section_a(x)
    ext = _super_ellipse(x, w - 2 * retrait_ext, h - 2 * retrait_ext, zc)
    face = cq.Face.makeFromWires(ext)
    s = cq.Workplane().add(cq.Solid.extrudeLinear(face, cq.Vector(ep, 0, 0)))
    if retrait_int is not None:
        inte = _super_ellipse(x, w - 2 * retrait_int, h - 2 * retrait_int, zc)
        f2 = cq.Face.makeFromWires(inte)
        s = s.cut(cq.Workplane().add(cq.Solid.extrudeLinear(f2, cq.Vector(ep, 0, 0))))
    return s


def fuselage_complet():
    ext = _loft_fus(SECTIONS_FUS)
    inte = _loft_fus([s for s in SECTIONS_FUS if s[0] >= -200], PAROI_FUS)
    fus = ext.cut(inte)

    # fourreaux de longeron et de goupille traversant le fuselage
    for xc, d in ((LONGERON_PRINC_X, LONGERON_PRINC_D), (GOUPILLE_X, GOUPILLE_D)):
        x, z = position_tube(PROFIL_AILE, CORDE, xc, CALAGE_AILE)
        r = (d + JEU_TUBE) / 2
        tube = (cq.Workplane("XZ", origin=(0, DEMI_LARGEUR_FUS, 0)).center(x, z)
                .circle(r + 2.0).extrude(2 * DEMI_LARGEUR_FUS))
        # goutte vers le nez : le fourreau s'imprime sans support, fuselage debout
        R = r + 2.0
        k = R * math.cos(math.radians(45))
        goutte = (cq.Workplane("XZ", origin=(0, DEMI_LARGEUR_FUS, 0))
                  .polyline([(x - k, z + k), (x - R * math.sqrt(2), z), (x - k, z - k), (x, z)])
                  .close().extrude(2 * DEMI_LARGEUR_FUS))
        fus = fus.union(tube.union(goutte).intersect(ext))
        trou = (cq.Workplane("XZ", origin=(0, 70, 0)).center(x, z)
                .circle(r).extrude(140))
        fus = fus.cut(trou)

    # passages de câbles vers les ailes (servos, ESC)
    xp, zp = position_tube(PROFIL_AILE, CORDE, 0.45, CALAGE_AILE)
    fus = fus.cut(cq.Workplane("XZ", origin=(0, 70, 0)).center(xp, zp).circle(5)
                  .extrude(140))

    # tube de Pitot dans le nez
    fus = fus.cut(cq.Workplane("YZ", origin=(-230, 0, SECTIONS_FUS[0][3]))
                  .circle(2.1).extrude(40))

    return fus, ext


def cloison_moteur():
    """Cloison en PETG collée au bout du fuselage, reçoit le moteur propulsif."""
    xm, ep = SECTIONS_FUS[-1][0], 5.0
    cloison = _lamelle(xm - ep, ep, PAROI_FUS + 0.15, None)
    o = (xm - 10, 0, POUSSEUR_Z)
    perc = cq.Workplane("YZ", origin=o).circle(5).extrude(20)
    for k in range(8):  # fentes de Ø16 à Ø25 mm, 8 directions
        a = 45 * k
        perc = perc.union(cq.Workplane("YZ", origin=o)
                          .center(10.25 * math.cos(math.radians(a)), 10.25 * math.sin(math.radians(a)))
                          .slot2D(4.5 + 3.3, 3.3, a).extrude(20))
    for sy in (-1, 1):  # ouïes de refroidissement
        perc = perc.union(cq.Workplane("YZ", origin=o).center(sy * 18, 0).rect(5, 14).extrude(20))
    return cloison.cut(perc)


def fuselage_pieces():
    fus, ext = fuselage_complet()
    c = COUPES_FUS
    morceaux = []
    for k, (a, b) in enumerate(zip(c, c[1:])):
        a -= 20 if k == 0 else 0
        b += 20 if k == len(c) - 2 else 0
        boite = cq.Workplane().box(b - a, 400, 400, centered=(False, True, True)).translate((a, 0, 0))
        morceaux.append(fus.intersect(boite))

    # lèvres d'emboîtement : le nez s'emboîte dans l'avant, l'avant dans l'arrière
    for idx, x in ((0, c[1]), (1, c[2])):
        levre = _lamelle(x, 10, PAROI_FUS + 0.25, PAROI_FUS + 1.45)
        morceaux[idx] = morceaux[idx].union(levre)
    return morceaux  # [nez, avant, arriere]


def plateau_electronique():
    """Plancher glissé dans le fuselage : batterie devant, électronique derrière."""
    z0, ep, larg = -78.0, 2.0, 76.0
    x0, x1 = -115.0, 105.0
    p = (cq.Workplane("XY", origin=(0, 0, z0)).center((x0 + x1) / 2, 0)
         .rect(x1 - x0, larg).extrude(ep).edges("|Z").fillet(6))
    # fentes pour sangles de batterie
    for xs in (-95.0, -35.0):
        for ys in (-28.0, 28.0):
            p = p.cut(cq.Workplane("XY", origin=(0, 0, z0 - 1)).center(xs, ys)
                      .slot2D(22, 4, 90).extrude(ep + 2))
    # entretoises 30,5 mm (contrôleur de vol) et 20 mm (récepteur)
    for cx, pas, h in ((60.0, 30.5, 6.0), (20.0, 20.0, 5.0)):
        for sx in (-1, 1):
            for sy in (-1, 1):
                pos = (cx + sx * pas / 2, sy * pas / 2)
                p = p.union(cq.Workplane("XY", origin=(0, 0, z0 + ep)).center(*pos)
                            .circle(3.2).extrude(h))
                p = p.cut(cq.Workplane("XY", origin=(0, 0, z0 - 1)).center(*pos)
                          .circle(1.35).extrude(ep + h + 2))
    # passage de câbles sous le contrôleur de vol
    p = p.cut(cq.Workplane("XY", origin=(0, 0, z0 - 1)).center(88, 0)
              .rect(14, 40).extrude(ep + 2).edges("|Z").fillet(3))
    return p


# ---------------------------------------------------------------------------
# Propulsion VTOL et atterrisseur
# ---------------------------------------------------------------------------
def support_moteur(x0, y0=POUTRE_Y):
    zb = POUTRE_Z
    r_ext, r_int = 13.0, (POUTRE_D + JEU_TUBE) / 2
    wp = cq.Workplane("YZ", origin=(x0 - 18, y0, zb))
    corps = wp.circle(r_ext).extrude(36)
    corps = corps.union(cq.Workplane("XY", origin=(x0, y0, zb)).box(36, 20, 9, centered=(True, True, False)))
    corps = corps.union(cq.Workplane("XY", origin=(x0, y0, zb + 9)).box(42, 42, 4, centered=(True, True, False))
                        .edges("|Z").fillet(6))
    corps = corps.union(cq.Workplane("XY", origin=(x0, y0, zb - 21)).box(36, 12, 9, centered=(True, True, False)))
    corps = corps.cut(cq.Workplane("YZ", origin=(x0 - 20, y0, zb)).circle(r_int).extrude(40))
    corps = corps.cut(cq.Workplane("XY", origin=(x0, y0, zb - 25)).box(40, 1.5, 25, centered=(True, True, False)))
    for dx in (-9.0, 9.0):  # vis de serrage M3
        corps = corps.cut(cq.Workplane("XZ", origin=(0, y0 + 10, 0)).center(x0 + dx, zb - 16.5)
                          .circle(1.65).extrude(20))
    # perçage universel : fentes de Ø16 à Ø25 sur 8 directions
    plat = cq.Workplane("XY", origin=(x0, y0, zb + 5))
    corps = corps.cut(plat.circle(4.5).extrude(10))
    for k in range(8):
        a = math.radians(45 * k)
        corps = corps.cut(plat.center(10.25 * math.cos(a), 10.25 * math.sin(a))
                          .slot2D(4.5 + 3.3, 3.3, 45 * k).extrude(10))
    return corps


def patte(x0, y0=POUTRE_Y):
    """Patte d'atterrissage en TPU, enfilée sur la poutre."""
    zb = POUTRE_Z
    bague = (cq.Workplane("YZ", origin=(x0 - 9, y0, zb)).circle(12).extrude(18)
             .cut(cq.Workplane("YZ", origin=(x0 - 10, y0, zb)).circle(POUTRE_D / 2 - 0.1).extrude(20)))
    jambe = (cq.Workplane("XY", origin=(x0, y0, zb - PATTE_LONG + 5))
             .rect(12, 8).workplane(offset=PATTE_LONG - 15).rect(18, 10).loft())
    pied = (cq.Workplane("XY", origin=(x0, y0, zb - PATTE_LONG)).rect(44, 26).extrude(6)
            .edges("|Z").fillet(8))
    return bague.union(jambe).union(pied)


# ---------------------------------------------------------------------------
# Empennage
# ---------------------------------------------------------------------------
def _stab_bornes():
    n, d = STAB_N_SEG, STAB_DEMI_ENV
    return [(-d + 2 * d * i / n, -d + 2 * d * (i + 1) / n) for i in range(n)]


def stab_segment(i):
    ya, yb = _stab_bornes()[i]
    xp = PROFONDEUR_X - 0.5 / STAB_CORDE
    sect = section_coque(STAB_PROFIL, STAB_CORDE, xmax=xp, ames=3,
                         tubes=[(STAB_LONGERON_X, STAB_LONGERON_D), (STAB_JONC_X, STAB_JONC_D)])
    return extrude_xz(sect, ya, yb).translate((STAB_BA_X, 0, STAB_Z))


def profondeur(i):
    ya, yb = _stab_bornes()[i]
    xp = PROFONDEUR_X + 0.5 / STAB_CORDE
    sect = section_coque(STAB_PROFIL, STAB_CORDE, xmin=xp, tubes=[(0.74, 2.0)], peau=0.5)
    return extrude_xz(sect, ya + 0.5, yb - 0.5).translate((STAB_BA_X, 0, STAB_Z))


def bloc_queue():
    """Bloc de queue droit : fourreau de poutre, dérive, prises du stab, baie servo."""
    y0, zb = POUTRE_Y, POUTRE_Z
    fin_tube = POUTRE_DEBUT + POUTRE_LONG
    x0, x1, z0, z1 = DERIVE_BA_X, DERIVE_BA_X + DERIVE_CORDE_PIED, zb - 13, 14.0
    cote = [(x0 + 6, z0), (x1 - 4, z0), (x1, z0 + 8), (x1, z1), (x0 + 18, z1),
            (x0, z1 - 14), (x0, z0 + 10)]
    bloc = (cq.Workplane("XZ", origin=(0, y0 + 15, 0)).polyline(cote).close().extrude(30))
    try:
        bloc = bloc.edges("|X").fillet(5)
    except Exception:
        pass

    # dérive : profil symétrique effilé
    def fil(corde, xba, z):
        pts = naca_points("0009", corde, 50)
        return cq.Wire.makePolygon([cq.Vector(xba + x, y0 + t, z) for x, t in pts], close=True)
    derive = cq.Solid.makeLoft([fil(DERIVE_CORDE_PIED, x0, z1 - 2),
                                fil(DERIVE_CORDE_SAUMON, x1 - DERIVE_CORDE_SAUMON, z1 + DERIVE_HAUTEUR)], True)
    bloc = bloc.union(cq.Workplane().add(derive))

    # fourreau de poutre (borgne)
    bloc = bloc.cut(cq.Workplane("YZ", origin=(x0 - 5, y0, zb)).circle((POUTRE_D + JEU_TUBE) / 2)
                    .extrude(fin_tube - x0 + 5))
    # prises du longeron (6 mm) et du jonc (3 mm) du stab, côté intérieur
    for xc, d in ((STAB_LONGERON_X, STAB_LONGERON_D), (STAB_JONC_X, STAB_JONC_D)):
        bloc = bloc.cut(cq.Workplane("XZ", origin=(0, y0, 0))
                        .center(STAB_BA_X + xc * STAB_CORDE, STAB_Z)
                        .circle((d + JEU_TUBE) / 2).extrude(-20))
    # baie de servo de profondeur, ouverte côté intérieur
    bloc = bloc.cut(cq.Workplane("XY", origin=(0, 0, -2)).center(686, y0 - 15 + 12.5)
                    .rect(33, 25.5).extrude(13))
    # passage de câble poutre -> servo
    bloc = bloc.cut(cq.Workplane("XY", origin=(0, 0, zb)).center(680, y0).circle(3).extrude(20))
    return bloc


# ---------------------------------------------------------------------------
# Inventaire des pièces imprimées
# ---------------------------------------------------------------------------
X_MOT_AV = CG_X - MOTEUR_ECART
X_MOT_AR = CG_X + MOTEUR_ECART
X_PATTE_AV = X_MOT_AV + 38
X_PATTE_AR = X_MOT_AR - 38


def inventaire():
    """(nom, fonction, quantité, matériau, orientation, parois mm, remplissage, miroir)

    orientation : 'Y' = l'envergure devient verticale (emplanture sur le plateau),
                  'X' = l'axe X devient vertical (nez en bas), 'Xinv' = nez en haut,
                  'Z' = tel quel, 'Zinv' = retourné.
    miroir : True -> on exporte aussi la version gauche.
    """
    inv = []
    for i in range(N_SEGMENTS):
        inv.append((f"aile_segment_{i + 1}", lambda i=i: segment_aile(i), 1, "PLA Aero", "Y", None, 0, True))
    for i in (2, 3):
        inv.append((f"aileron_{i - 1}", lambda i=i: aileron(i), 1, "PLA Aero", "Y", None, 0, True))
    inv += [
        ("saumon", saumon, 1, "PLA Aero", "Y", 1.2, 0.05, True),
        ("pylone_poutre", pylone, 1, "PETG", "X", 1.2, 0.10, True),
        ("fuselage_nez", lambda: fuselage_pieces()[0], 1, "PLA Aero", "Xinv", None, 0, False),
        ("fuselage_avant", lambda: fuselage_pieces()[1], 1, "PLA Aero", "X", None, 0, False),
        ("fuselage_arriere", lambda: fuselage_pieces()[2], 1, "PLA Aero", "X", None, 0, False),
        ("cloison_moteur", cloison_moteur, 1, "PETG", "X", 1.6, 0.50, False),
        ("plateau_electronique", plateau_electronique, 1, "PETG", "Z", 1.2, 0.30, False),
        ("support_moteur", lambda: support_moteur(X_MOT_AV), 4, "PETG", "Zinv", 1.6, 0.40, False),
        ("patte_atterrissage", lambda: patte(X_PATTE_AV), 4, "TPU 95A", "Z", 1.6, 0.25, False),
        ("bloc_queue", bloc_queue, 1, "PLA Aero", "Z", 1.2, 0.08, True),
    ]
    for i in range(STAB_N_SEG):
        inv.append((f"stab_segment_{i + 1}", lambda i=i: stab_segment(i), 1, "PLA Aero", "Y", None, 0, False))
        inv.append((f"profondeur_{i + 1}", lambda i=i: profondeur(i), 1, "PLA Aero", "Y", None, 0, False))
    return inv
