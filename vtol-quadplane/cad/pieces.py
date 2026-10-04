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

    if i == segments_aileron()[0]:  # baie de servo d'aileron (servo 9 g couché, palonnier sous l'aile)
        profil = Polygon(naca_points(PROFIL_AILE, CORDE))
        bloc = profil.intersection(box(0.45 * CORDE, -50, 0.64 * CORDE, 50))
        poche = bloc.intersection(box(0.47 * CORDE, -50, 0.62 * CORDE, 10.0))
        yc = max(ya, AILERON_DEBUT) + 42
        seg = seg.union(extrude_xz(bloc, yc - 22, yc + 22))
        seg = seg.cut(extrude_xz(poche, yc - 15, yc + 15))

    if ya < POUTRE_Y < yb:  # passage des câbles vers la poutre
        trou = (cq.Workplane("XY").workplane(offset=-30)
                .center(0.45 * CORDE, POUTRE_Y).circle(5).extrude(30))
        seg = seg.cut(trou)

    return caler(seg, CALAGE_AILE)


def segments_aileron():
    return [i for i, (ya, yb) in enumerate(bornes_segments())
            if yb > AILERON_DEBUT and ya < AILERON_FIN]


def aileron(i):
    ya, yb = bornes_segments()[i]
    a0, a1 = max(ya, AILERON_DEBUT), min(yb, AILERON_FIN)
    segs = segments_aileron()
    if i != segs[0]:
        a0 += AILERON_JEU / 2
    if i != segs[-1]:
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
    """Carénage collé sous l'aile : reçoit la poutre."""
    l, zb, k = POUTRE_D + 8, POUTRE_Z, CORDE / 220.0
    e = POUTRE_D / 2 + 3
    cote = [(0, zb + 2), (14 * k, zb - e), (180 * k, zb - e), (204 * k, zb - 3), (204 * k, -5),
            (110 * k, 6), (14 * k, 4), (0, -6)]
    corps = (cq.Workplane("XZ", origin=(0, POUTRE_Y + l / 2, 0))
             .polyline(cote).close().extrude(l))
    aile = caler(extrude_xz(Polygon(naca_points(PROFIL_AILE, CORDE)),
                            POUTRE_Y - l, POUTRE_Y + l), CALAGE_AILE)
    corps = corps.cut(aile)
    try:
        corps = corps.edges("|Y").fillet(3)
    except Exception:
        pass
    alesage = (cq.Workplane("YZ", origin=(-10, POUTRE_Y, POUTRE_Z))
               .circle((POUTRE_D + JEU_TUBE) / 2).extrude(CORDE + 40))
    cable = (cq.Workplane("XY", origin=(0.45 * CORDE, POUTRE_Y, POUTRE_Z))
             .circle(min(5.0, POUTRE_D / 2 - 1)).extrude(40))
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
    inte = _loft_fus(SECTIONS_FUS[1:], PAROI_FUS)  # pointe du nez pleine
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
        trou = (cq.Workplane("XZ", origin=(0, DEMI_LARGEUR_FUS + 15, 0)).center(x, z)
                .circle(r).extrude(2 * DEMI_LARGEUR_FUS + 30))
        fus = fus.cut(trou)

    # passages de câbles vers les ailes (servos, ESC)
    xp, zp = position_tube(PROFIL_AILE, CORDE, 0.45, CALAGE_AILE)
    fus = fus.cut(cq.Workplane("XZ", origin=(0, DEMI_LARGEUR_FUS + 15, 0)).center(xp, zp).circle(5)
                  .extrude(2 * DEMI_LARGEUR_FUS + 30))

    # ouverture du dessous pour les câbles de la nacelle caméra
    if NACELLE_X is not None:
        fus = fus.cut(cq.Workplane("XY", origin=(NACELLE_X, 0, -100)).rect(20, 16).extrude(20)
                      .edges("|Z").fillet(4))
        for dx in (-32.0, 32.0):  # vis de la selle de nacelle
            fus = fus.cut(cq.Workplane("XY", origin=(NACELLE_X + dx, 0, -100)).circle(1.7).extrude(20))

    # tube de Pitot dans le nez
    fus = fus.cut(cq.Workplane("YZ", origin=(SECTIONS_FUS[0][0] - 5, 0, SECTIONS_FUS[0][3]))
                  .circle(2.1).extrude(40))

    return fus, ext


def cloison_moteur():
    """Cloison en PETG collée au bout du fuselage, reçoit le moteur propulsif."""
    xm, ep = SECTIONS_FUS[-1][0], 5.0
    cloison = _lamelle(xm - ep, ep, PAROI_FUS + 0.15, None)
    o = (xm - 10, 0, POUSSEUR_Z)
    perc = cq.Workplane("YZ", origin=o).circle(5).extrude(20)
    a, b = POUSSEUR_TROUS  # vis M3 en croix
    for cy, cz in ((a / 2, 0), (-a / 2, 0), (0, b / 2), (0, -b / 2)):
        perc = perc.union(cq.Workplane("YZ", origin=o).center(cy, cz).circle(1.7).extrude(20))
    w, h, _ = _section_a(xm)
    for sy in (-1, 1):  # ouïes de refroidissement
        perc = perc.union(cq.Workplane("YZ", origin=o).center(sy * 0.33 * w, sy * 0.2 * h)
                          .circle(min(3.0, 0.06 * w)).extrude(20))
    return cloison.cut(perc)


def fuselage_pieces():
    fus, _ = fuselage_complet()
    c = COUPES_FUS
    morceaux = []
    for k, (a, b) in enumerate(zip(c, c[1:])):
        a -= 20 if k == 0 else 0
        b += 20 if k == len(c) - 2 else 0
        boite = cq.Workplane().box(b - a, 400, 400, centered=(False, True, True)).translate((a, 0, 0))
        morceaux.append(fus.intersect(boite))

    # lèvres d'emboîtement : chaque tronçon s'emboîte dans le suivant (le nez reste amovible)
    for k, x in enumerate(c[1:-1]):
        levre = _lamelle(x, 10, PAROI_FUS + 0.25, PAROI_FUS + 1.45)
        morceaux[k] = morceaux[k].union(levre)
    return morceaux  # dans l'ordre de NOMS_TRONCONS_FUS


def plateau_electronique():
    """Plateau de batterie glissé dans le fuselage, posé sur 2 plots vissés à la selle de nacelle."""
    z0, ep, larg = PLATEAU_Z, 2.0, PLATEAU_LARG
    x0, x1 = PLATEAU_X
    p = (cq.Workplane("XY", origin=(0, 0, z0)).center((x0 + x1) / 2, 0)
         .rect(x1 - x0, larg).extrude(ep).edges("|Z").fillet(6))
    # fentes pour sangles de batterie
    for xs in (x0 + 12, x0 + 0.53 * (x1 - x0)):
        for ys in (-(larg / 2 - 10), larg / 2 - 10):
            p = p.cut(cq.Workplane("XY", origin=(0, 0, z0 - 1)).center(xs, ys)
                      .slot2D(22, 4, 90).extrude(ep + 2))
    # plots jusqu'au fond du fuselage, traversés par les vis M3 de la selle
    for dx in ((-32.0, 32.0) if NACELLE_X is not None else ()):
        _, h, zc = _section_a(NACELLE_X + dx)
        fond = zc - h / 2 + PAROI_FUS + 0.3
        p = p.union(cq.Workplane("XY", origin=(NACELLE_X + dx, 0, fond)).circle(5).extrude(z0 - fond))
        p = p.cut(cq.Workplane("XY", origin=(NACELLE_X + dx, 0, fond - 1)).circle(1.7).extrude(z0 - fond + ep + 2))
    return p


def support_nacelle():
    """Selle collée et vissée sous le fuselage : face plane pour la nacelle caméra."""
    x0, lx, ly = NACELLE_X, 82.0, 60.0
    bloc = (cq.Workplane("XY", origin=(x0, 0, NACELLE_Z)).rect(lx, ly).extrude(25)
            .edges("|Z").fillet(8))
    _, ext = fuselage_complet()
    selle = bloc.cut(ext)
    # passage de câbles au centre, vis M3 vers les plots du plateau
    selle = selle.cut(cq.Workplane("XY", origin=(x0, 0, NACELLE_Z - 1)).rect(20, 16).extrude(40)
                      .edges("|Z").fillet(4))
    for dx in (-32.0, 32.0):
        selle = selle.cut(cq.Workplane("XY", origin=(x0 + dx, 0, NACELLE_Z - 1)).circle(1.7).extrude(40))
    # perçages de la nacelle (A8 mini et ZT6), taraudés dans le PETG
    for ex, ey, d in NACELLE_TROUS:
        for sx in (-1, 1):
            for sy in (-1, 1):
                selle = selle.cut(cq.Workplane("XY", origin=(x0 + sx * ex / 2, sy * ey / 2, NACELLE_Z - 1))
                                  .circle(d / 2 - 0.25).extrude(12))
    return selle


def plateau_compagnon():
    """Plateau du fuselage milieu : contrôleur de vol (entretoises M3) et, sur le DFR,
    Raspberry Pi 5 (58 x 49 mm, M2.5) ; le modem 4G se colle à côté."""
    z0, ep = COMPAGNON_Z, 2.0
    (x0, x1), larg = COMPAGNON_X, COMPAGNON_LARG
    p = (cq.Workplane("XY", origin=(0, 0, z0)).center((x0 + x1) / 2, 0)
         .rect(x1 - x0, larg).extrude(ep).edges("|Z").fillet(6))
    xf = x0 + FC_DIMS[0] / 2 - 5
    for sx in (-1, 1):  # entretoises du contrôleur de vol
        for sy in (-1, 1):
            pos = (xf + sx * FC_TROUS / 2, sy * FC_TROUS / 2)
            p = p.union(cq.Workplane("XY", origin=(0, 0, z0 + ep)).center(*pos).circle(3.2).extrude(6))
            p = p.cut(cq.Workplane("XY", origin=(0, 0, z0 - 1)).center(*pos).circle(1.35).extrude(ep + 8))
    if PI5:
        cx = x1 - 38
        for sx in (-1, 1):  # trous de fixation Raspberry Pi : 58 x 49 mm
            for sy in (-1, 1):
                pos = (cx + sx * 29, sy * 24.5)
                p = p.union(cq.Workplane("XY", origin=(0, 0, z0 + ep)).center(*pos).circle(3.2).extrude(5))
                p = p.cut(cq.Workplane("XY", origin=(0, 0, z0 - 1)).center(*pos).circle(1.1).extrude(ep + 7))
        p = p.cut(cq.Workplane("XY", origin=(0, 0, z0 - 1)).center(cx, 0).rect(30, 20).extrude(ep + 2)
                  .edges("|Z").fillet(4))
    return p


# ---------------------------------------------------------------------------
# Propulsion VTOL et atterrisseur
# ---------------------------------------------------------------------------
def support_moteur(x0, y0=POUTRE_Y):
    zb = POUTRE_Z
    r_int = (POUTRE_D + JEU_TUBE) / 2
    r_ext = r_int + 4.8
    zp = r_ext - 4                       # dessous de la platine moteur
    cote = MOTEUR_VTOL_DIAM + 4          # platine carrée
    lg = min(36.0, cote - 6)             # longueur du collier
    wp = cq.Workplane("YZ", origin=(x0 - lg / 2, y0, zb))
    corps = wp.circle(r_ext).extrude(lg)
    corps = corps.union(cq.Workplane("XY", origin=(x0, y0, zb)).box(lg, POUTRE_D + 4, zp, centered=(True, True, False)))
    corps = corps.union(cq.Workplane("XY", origin=(x0, y0, zb + zp)).box(cote, cote, 4, centered=(True, True, False))
                        .edges("|Z").fillet(6))
    corps = corps.union(cq.Workplane("XY", origin=(x0, y0, zb - r_ext - 8)).box(lg, 12, 9, centered=(True, True, False)))
    corps = corps.cut(cq.Workplane("YZ", origin=(x0 - lg / 2 - 2, y0, zb)).circle(r_int).extrude(lg + 4))
    corps = corps.cut(cq.Workplane("XY", origin=(x0, y0, zb - r_ext - 12)).box(lg + 4, 1.5, r_ext + 12, centered=(True, True, False)))
    for dx in (-lg / 4, lg / 4):  # vis de serrage M3
        corps = corps.cut(cq.Workplane("XZ", origin=(0, y0 + 10, 0)).center(x0 + dx, zb - r_ext - 3.5)
                          .circle(1.65).extrude(20))
    # perçage exact du moteur (vis M3 dégagées sur toute la hauteur) et logement central
    plat = cq.Workplane("XY", origin=(x0, y0, zb + 1))
    corps = corps.cut(cq.Workplane("XY", origin=(x0, y0, zb + zp - 2)).circle(5.5).extrude(10))
    for dx, dy in MOTEUR_VTOL_TROUS:
        corps = corps.cut(plat.center(dx, dy).circle(1.7).extrude(zp + 8))
    return corps


def patte(x0, y0=POUTRE_Y):
    """Patte d'atterrissage en TPU, enfilée sur la poutre."""
    zb = POUTRE_Z
    (b0, b1), (b2, b3) = PATTE_SECTION
    bague = (cq.Workplane("YZ", origin=(x0 - 9, y0, zb)).circle(POUTRE_D / 2 + 4).extrude(18)
             .cut(cq.Workplane("YZ", origin=(x0 - 10, y0, zb)).circle(POUTRE_D / 2 - 0.1).extrude(20)))
    jambe = (cq.Workplane("XY", origin=(x0, y0, zb - PATTE_LONG + 5))
             .rect(b0, b1).workplane(offset=PATTE_LONG - 15).rect(b2, b3).loft())
    pied = (cq.Workplane("XY", origin=(x0, y0, zb - PATTE_LONG)).rect(*PATTE_PIED).extrude(6)
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
    sect = section_coque(STAB_PROFIL, STAB_CORDE, xmin=xp, tubes=[PROFONDEUR_JONC], peau=0.5)
    return extrude_xz(sect, ya + 0.5, yb - 0.5).translate((STAB_BA_X, 0, STAB_Z))


def bloc_queue():
    """Bloc de queue droit : fourreau de poutre, dérive, prises du stab, baie servo."""
    y0, zb = POUTRE_Y, POUTRE_Z
    fin_tube = POUTRE_DEBUT + POUTRE_LONG
    dl = POUTRE_D / 2 + 7                # demi-largeur du bloc
    x0, x1, z0, z1 = BLOC_QUEUE_X0, DERIVE_BA_X + DERIVE_CORDE_PIED, zb - POUTRE_D / 2 - 5, STAB_Z + 22
    cote = [(x0 + 6, z0), (x1 - 4, z0), (x1, z0 + 8), (x1, z1), (x0 + 18, z1),
            (x0, z1 - 14), (x0, z0 + 10)]
    bloc = (cq.Workplane("XZ", origin=(0, y0 + dl, 0)).polyline(cote).close().extrude(2 * dl))
    try:
        bloc = bloc.edges("|X").fillet(5)
    except Exception:
        pass

    # dérive : profil symétrique effilé
    def fil(corde, xba, z):
        pts = naca_points("0009", corde, 50)
        return cq.Wire.makePolygon([cq.Vector(xba + x, y0 + t, z) for x, t in pts], close=True)
    derive = cq.Solid.makeLoft([fil(DERIVE_CORDE_PIED, DERIVE_BA_X, z1 - 2),
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
    prof = min(25.5, 2 * dl - 2.5)
    xs = x1 - 22
    bloc = bloc.cut(cq.Workplane("XY", origin=(0, 0, STAB_Z + 6)).center(xs, y0 - dl + prof / 2)
                    .rect(33, prof).extrude(13))
    # passage de câble poutre -> servo
    bloc = bloc.cut(cq.Workplane("XY", origin=(0, 0, zb)).center(xs - 6, y0).circle(min(3.0, POUTRE_D / 2 - 1.5))
                    .extrude(STAB_Z + 7 - zb))
    return bloc


# ---------------------------------------------------------------------------
# Inventaire des pièces imprimées
# ---------------------------------------------------------------------------
X_MOT_AV = CG_X - MOTEUR_ECART
X_MOT_AR = CG_X + MOTEUR_ECART
X_PATTE_AV = X_MOT_AV + PATTE_DECALAGE
X_PATTE_AR = X_MOT_AR - PATTE_DECALAGE
X_SERVO_PROF = DERIVE_BA_X + DERIVE_CORDE_PIED - 22


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
    for k, i in enumerate(segments_aileron()):
        inv.append((f"aileron_{k + 1}", lambda i=i: aileron(i), 1, "PLA Aero", "Y", None, 0, True))
    inv += [
        ("saumon", saumon, 1, "PLA Aero", "Y", 1.2, 0.05, True),
        ("pylone_poutre", pylone, 1, "PETG", "X", 1.2, 0.10, True),
    ]
    noms_fus = NOMS_TRONCONS_FUS
    for k, nom in enumerate(noms_fus):
        inv.append((f"fuselage_{nom}", lambda k=k: fuselage_pieces()[k], 1, "PLA Aero",
                    "Xinv" if k == 0 else "X", None, 0, False))
    inv += [
        ("cloison_moteur", cloison_moteur, 1, "PETG", "X", 1.6, 0.50, False),
        ("plateau_electronique", plateau_electronique, 1, "PETG", "Z", 1.2, 0.30, False),
        ("plateau_compagnon", plateau_compagnon, 1, "PETG", "Z", 1.2, 0.30, False),
        ("support_moteur", lambda: support_moteur(X_MOT_AV), 4, "PETG", "Zinv", 1.6, 0.40, False),
        ("patte_atterrissage", lambda: patte(X_PATTE_AV), 4, "TPU 95A", "Z", 1.6, 0.25, False),
        ("bloc_queue", bloc_queue, 1, "PLA Aero", "Z", 1.2, 0.08, True),
    ]
    if NACELLE_X is not None:
        inv.append(("support_nacelle", support_nacelle, 1, "PETG", "Z", 1.6, 0.30, False))
    for i in range(STAB_N_SEG):
        inv.append((f"stab_segment_{i + 1}", lambda i=i: stab_segment(i), 1, "PLA Aero", "Y", None, 0, False))
        inv.append((f"profondeur_{i + 1}", lambda i=i: profondeur(i), 1, "PLA Aero", "Y", None, 0, False))
    return inv
