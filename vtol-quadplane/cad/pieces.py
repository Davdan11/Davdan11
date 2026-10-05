"""Géométrie des pièces imprimées du quadplane.

Chaque fonction renvoie un solide CadQuery placé dans le repère global de
l'avion (voir params.py). build.py se charge de les orienter pour
l'impression et de les exporter.
"""
import functools
import math

import cadquery as cq
from shapely.affinity import scale as sh_scale, translate
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
                  ame=AME, ame_tube=0.8, clip=None, fourreau=FOURREAU, conduit=None):
    """Section creuse d'un profil : peau + âmes en zigzag + fourreaux de tubes.

    tubes   : liste de (fraction de corde, diamètre du tube)
    clip    : polygone qui remplace la découpe [xmin, xmax] (charnières en V)
    conduit : (fraction de corde, rayon) : passage de câbles percé dans les âmes
    """
    profil = Polygon(naca_points(code, corde))
    if clip is None:
        x0, x1 = xmin * corde, xmax * corde
        zone = profil.intersection(box(x0, -100, x1, 100))
        ferme0 = peau if xmin > 0 else 0
        ferme1 = peau if xmax < 1 else 0
        interieur = profil.buffer(-peau, join_style=2).intersection(
            box(x0 + ferme0, -100, x1 - ferme1, 100))
    else:
        zone = profil.intersection(clip)
        x0, _, x1, _ = zone.bounds
        interieur = profil.buffer(-peau, join_style=2).intersection(clip.buffer(-peau, join_style=2))
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
    if conduit is not None:  # passage de câbles : on perce les âmes, jamais la peau
        xc, rc = conduit
        trou_c = Point(xc * corde, naca_cambrure(code, xc) * corde).buffer(rc)
        coque = coque.difference(trou_c.intersection(interieur))

    trous = []
    for xc, d in tubes:
        cz = naca_cambrure(code, xc) * corde
        c = Point(xc * corde, cz)
        coque = coque.union(c.buffer(d / 2 + JEU_TUBE / 2 + fourreau).intersection(zone))
        # âme verticale : relie le fourreau aux deux peaux (sinon il flotte dans le vide)
        coque = coque.union(box(xc * corde - ame_tube / 2, -100, xc * corde + ame_tube / 2, 100)
                            .intersection(zone))
        trous.append(c.buffer(d / 2 + JEU_TUBE / 2))
    if trous:
        coque = coque.difference(unary_union(trous))
    return coque


def caler(wp, angle, x0=0.0, z0=0.0):
    """Applique une incidence (cabrer = bord de fuite vers le bas) autour de (x0, z0)."""
    return wp.rotate((x0, 0, z0), (x0, 1, z0), angle)


ANGLE_V = 22.0   # demi-ouverture du V sous la charnière (débattement vers le haut ≈ 2 x 22°)


def charniere(code, corde, xh):
    """Découpes 2D d'une charnière sur l'extrados : (partie fixe, gouverne, x avant-bas de la gouverne).

    La charnière (ruban) est sur le dessus, au point (xh, extrados). Les deux faces
    s'écartent en V vers le bas : la gouverne peut monter jusqu'à ~2 x ANGLE_V et
    descendre sans rien toucher."""
    xh *= corde
    z_haut, z_bas = naca_surfaces(code, corde, xh / corde)
    t = math.tan(math.radians(ANGLE_V))
    j = AILERON_JEU / 2
    fixe = Polygon([(-1e3, 1e3), (xh - j, 1e3), (xh - j, z_haut), (xh - j - t * 300, z_haut - 300), (-1e3, z_haut - 300)])
    mobile = Polygon([(1e3, 1e3), (xh + j, 1e3), (xh + j, z_haut), (xh + j + t * 300, z_haut - 300), (1e3, z_haut - 300)])
    return fixe, mobile, xh + j + t * (z_haut - z_bas)


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


def _servo_aile():
    """Position du servo d'aileron, couché dans l'aile (repère de corde, avant calage).

    Servo : longueur L le long de la corde, épaisseur W verticale, hauteur H le long de
    l'envergure, fond du boîtier côté emplanture et axe côté saumon. Le palonnier sort
    sous l'aile, en face du guignol.
    """
    L, W, H = SERVO["L"], SERVO["W"], SERVO["H"]
    demi = SERVO["oreilles"] / 2 + 2.2           # demi-largeur du cadre (le long de la corde)
    # place libre entre le fourreau du longeron extérieur et la charnière d'aileron
    xmin = LONGERON_EXT_X * CORDE + LONGERON_EXT_D / 2 + FOURREAU + 1.0
    zh, zl = naca_surfaces(PROFIL_AILE, CORDE, AILERON_X)
    xmax = AILERON_X * CORDE - AILERON_JEU / 2 - math.tan(math.radians(ANGLE_V)) * (zh - zl) - 1.0
    if xmax - xmin < 2 * demi:
        raise ValueError("cadre de servo trop large pour la place entre longeron et aileron")
    def hauteur(xc):
        zs = [naca_surfaces(PROFIL_AILE, CORDE, (xc + d) / CORDE) for d in (-demi, -demi / 2, 0, demi / 2, demi)]
        z_trappe = max(z[1] for z in zs)            # dessous de la trappe, au ras de l'intrados
        z0 = z_trappe + SERVO_TRAPPE_EP             # dessus de la trappe = dessous du servo
        return min(z[0] for z in zs) - PEAU - z0, z_trappe, z0
    # position la plus épaisse dans la place libre
    xcs = [xmin + demi + 0.5 * k for k in range(int((xmax - xmin - 2 * demi) / 0.5) + 1)]
    xc = max(xcs, key=lambda x: hauteur(x)[0])
    haut_dispo, z_trappe, z0 = hauteur(xc)
    if haut_dispo < W + 0.4:
        raise ValueError(f"aile trop mince pour le servo : {haut_dispo:.1f} mm < {W + 0.4:.1f} mm")
    yb = Y_GUIGNOL_AILERON - H - 3.0               # fond du boîtier (palonnier en face du guignol)
    y0, y1 = yb - 3.0, yb + H + 6.0                # étendue du cadre
    profil = Polygon(naca_points(PROFIL_AILE, CORDE))
    sous_peau = profil.intersection(translate(profil, 0, -PEAU))   # garde la peau d'extrados
    baie = sous_peau.intersection(box(xc - demi, -100, xc + demi, 100))
    xs = xc + L / 2 - SERVO["axe"]                 # axe du servo, côté bord de fuite
    vis = [(xc - demi + 2.0, y0 + 2.5), (xc + demi - 2.0, y1 - 2.5)]
    return dict(xc=xc, demi=demi, z0=z0, z_trappe=z_trappe, yb=yb, y0=y0, y1=y1,
                baie=baie, sous_peau=sous_peau, xs=xs, vis=vis)


def _prisme_xy(poly, z0, z1):
    """Prisme vertical (Z) à partir d'un contour shapely dans le plan XY."""
    return (cq.Workplane("XY", origin=(0, 0, z0)).polyline(list(poly.exterior.coords)[:-1])
            .close().extrude(z1 - z0))


def _empreinte_servo(g, marge=0.0):
    """Empreinte de la baie du servo vue de dessous. Le bout côté saumon est en pointe à 45° :
    le segment s'imprime debout (emplanture en bas), le haut de la baie se referme donc
    progressivement au lieu de faire un pont de 35 mm dans le vide."""
    xc, d, y0, y1 = g["xc"], g["demi"], g["y0"], g["y1"]
    p = Polygon([(xc - d, y0), (xc + d, y0), (xc + d, y1), (xc, y1 + d), (xc - d, y1)])
    return p.buffer(marge, join_style=2) if marge else p


def cadre_servo_aile():
    """Cadre PETG collé dans l'aile : le servo s'y emboîte, oreilles dans leurs encoches."""
    g = _servo_aile()
    L, W, H = SERVO["L"], SERVO["W"], SERVO["H"]
    bloc = extrude_xz(Polygon(naca_points(PROFIL_AILE, CORDE)).buffer(-(PEAU + 0.2)).intersection(
        box(g["xc"] - g["demi"], g["z0"], g["xc"] + g["demi"], 100)), g["y0"], g["y1"])
    def boite(x0, x1, y0, y1, z0, z1):
        return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))
    xc, z0, yb = g["xc"], g["z0"], g["yb"]
    # logement du boîtier, ouvert aux deux bouts (fil côté emplanture, palonnier côté saumon)
    bloc = bloc.cut(boite(xc - L / 2 - 0.3, xc + L / 2 + 0.3, g["y0"] - 1, g["y1"] + 1, z0 - 1, z0 + W + 0.4))
    # encoches des oreilles : bloquent le servo le long de l'envergure
    ty = yb + SERVO["oreille_y"]
    o = SERVO["oreilles"] / 2 + 0.3
    bloc = bloc.cut(boite(xc - o, xc + o, ty - 0.2, ty + SERVO["oreille_ep"] + 0.3, z0 - 1, z0 + W + 0.4))
    for x, y in g["vis"]:  # avant-trous des vis M2 de la trappe
        bloc = bloc.cut(cq.Workplane("XY", origin=(x, y, z0 - 1)).circle(0.8).extrude(9))
    return caler(bloc, CALAGE_AILE)


def trappe_servo_aile():
    """Trappe PETG vissée sous le cadre (2 vis M2) : tient le servo, laisse passer le palonnier."""
    g = _servo_aile()
    H = SERVO["H"]
    # même contour que la baie (pointe comprise) : referme tout le trou de l'intrados
    t = _prisme_xy(_empreinte_servo(g, -0.2), g["z_trappe"], g["z_trappe"] + SERVO_TRAPPE_EP)
    fente = (cq.Workplane("XY").box(16, 6, 10).translate((g["xs"], g["yb"] + H + 3.0, g["z_trappe"]))
             .edges("|Z").fillet(2))
    t = t.cut(fente)
    for x, y in g["vis"]:
        t = t.cut(cq.Workplane("XY", origin=(x, y, g["z_trappe"] - 1)).circle(1.1).extrude(5))
    return caler(t, CALAGE_AILE)


# --- Pylône vissé sous l'aile : 2 vis M3 tête fraisée par le dessus de l'aile, dans 2 inserts
# laiton M3 posés au fer dans le pylône (PETG). Le PLA Aero mince de l'aile ne tient pas un insert :
# l'aile est seulement serrée entre la tête de vis et le pylône, par des piliers pleins.
VIS_PYLONE_X = (0.12, 0.72)   # fractions de corde : devant le longeron, derrière le conduit de câbles
INSERT_PYLONE = (4.0, 5.0)    # perçage de l'insert M3 (Ø, profondeur)
PILIER_PYLONE = 4.5           # demi-diagonale du pilier en losange


def vis_pylone():
    """[(x, z intrados, z extrados)] des 2 vis du pylône, repère de corde (avant calage)."""
    out = []
    for f in VIS_PYLONE_X:
        zh, zl = naca_surfaces(PROFIL_AILE, CORDE, f)
        out.append((f * CORDE, zl, zh))
    return out


def _piliers_pylone(i, y0, y1):
    """Piliers pleins des vis du pylône dans le segment i (repère de corde) et perçages."""
    profil = extrude_xz(Polygon(naca_points(PROFIL_AILE, CORDE)), y0, y1)
    bas = 1 if i == 0 else -1          # sens du plateau en Y (segment d'emplanture imprimé à l'envers)
    y, a = POUTRE_Y, PILIER_PYLONE
    plein, trous = None, None
    for x, zl, zh in vis_pylone():
        pil = (cq.Workplane("XY", origin=(0, 0, zl - 1))
               .polyline([(x - a, y), (x, y - a), (x + a, y), (x, y + a)]).close().extrude(zh - zl + 2))
        # voiles à 45° accrochés aux deux peaux : le pilier s'imprime sans pont dans le vide
        ya, h, zm = y + bas * a, zh - zl, (zh + zl) / 2
        for zp in (zl - 1, zh + 1):
            v = (cq.Workplane("YZ", origin=(x - 0.6, 0, 0))
                 .polyline([(ya, zp), (ya, zm), (ya + bas * (h / 2 + 1), zp)]).close().extrude(1.2))
            pil = pil.union(v)
        plein = pil if plein is None else plein.union(pil)
        t = cq.Workplane("XY", origin=(x, y, zl - 5)).circle(1.7).extrude(h + 10)
        fraise = cq.Workplane().add(cq.Solid.makeCone(1.7, 3.3, 1.6, cq.Vector(x, y, zh - 1.6), cq.Vector(0, 0, 1)))
        t = t.union(fraise).union(cq.Workplane("XY", origin=(x, y, zh)).circle(3.3).extrude(3))
        trous = t if trous is None else trous.union(t)
    return plein.intersect(profil), trous


def ames_segment(i):
    """Nombre de diagonales du zigzag du segment i : plus serré près de l'emplanture, où la
    flexion comprime le plus la peau (panneaux plus étroits = la peau n'ondule pas)."""
    return globals().get("N_AMES_SEGMENTS", [N_AMES] * N_SEGMENTS)[i]


def segment_aile(i):
    """Segment i (0 = emplanture) de la demi-aile droite, sans aileron."""
    ya, yb = bornes_segments()[i]
    tubes = _tubes_aile(ya, yb)
    pleine = section_coque(PROFIL_AILE, CORDE, tubes=tubes, ames=ames_segment(i), conduit=CONDUIT)

    a0 = max(ya, AILERON_DEBUT) if yb > AILERON_DEBUT else None
    if i == 0:  # l'emplanture déborde dans le fuselage, puis est découpée à sa forme
        ya = DEMI_LARGEUR_FUS - 15
    if a0 is None:
        seg = extrude_xz(pleine, ya, yb)
    else:
        a1 = min(yb, AILERON_FIN)
        fixe, _, _ = charniere(PROFIL_AILE, CORDE, AILERON_X)
        avant = section_coque(PROFIL_AILE, CORDE, clip=fixe, tubes=tubes,
                              ames=ames_segment(i) - 2, conduit=CONDUIT)
        seg = extrude_xz(avant, a0, a1)
        if a0 > ya:
            seg = seg.union(extrude_xz(pleine, ya, a0))
        if a1 < yb:
            seg = seg.union(extrude_xz(pleine, a1, yb))

    if i == segments_aileron()[0]:  # baie du cadre de servo d'aileron, ouverte par-dessous
        g = _servo_aile()
        assert i > 0, "la baie doit être sur un segment imprimé emplanture en bas"
        seg = seg.cut(extrude_xz(g["baie"], g["y0"] - 0.3, g["y1"] + g["demi"] + 1)
                      .intersect(_prisme_xy(_empreinte_servo(g, 0.3), -100, 100)))
        # le fil du servo sort du cadre côté emplanture et file dans le conduit jusqu'au fuselage

    if i == 0:  # vis nylon M3 de retenue : traverse l'aile et le longeron (percé à travers ce trou)
        xv = LONGERON_PRINC_X * CORDE
        seg = seg.cut(cq.Workplane("XY", origin=(xv, Y_VIS_AILE, -60)).circle(1.65).extrude(120))

    if ya < POUTRE_Y < yb:  # piliers et perçages des 2 vis du pylône
        plein, trous = _piliers_pylone(i, ya, yb)
        seg = seg.union(plein).cut(trous)

    if ya < POUTRE_Y < yb:  # passage des câbles vers la poutre
        trou = (cq.Workplane("XY").workplane(offset=-30)
                .center(CONDUIT[0] * CORDE, POUTRE_Y).circle(5).extrude(30 + naca_cambrure(PROFIL_AILE, CONDUIT[0]) * CORDE))
        seg = seg.cut(trou)

    seg = caler(seg, CALAGE_AILE)
    if i == 0:
        seg = seg.cut(fuselage_complet()[1])   # l'emplanture épouse le flanc du fuselage
    return seg


Y_VIS_AILE = DEMI_LARGEUR_FUS + 15          # vis de retenue de l'aile, près de l'emplanture
Y_GUIGNOL_AILERON = AILERON_DEBUT + 42      # en face de la baie du servo d'aileron
Y_GUIGNOL_PROF = STAB_DEMI_ENV - 10          # près du bloc de queue droit (servo de profondeur)


def segments_aileron():
    return [i for i, (ya, yb) in enumerate(bornes_segments())
            if yb > AILERON_DEBUT and ya < AILERON_FIN]


def aileron(i):
    ya, yb = bornes_segments()[i]
    a0, a1 = max(ya, AILERON_DEBUT), min(yb, AILERON_FIN)
    segs = segments_aileron()
    if i != segs[0]:
        a0 += AILERON_JEU / 2
    a1 -= AILERON_JEU if i == segs[-1] else AILERON_JEU / 2   # jeu avec le saumon au bout
    _, mobile, _ = charniere(PROFIL_AILE, CORDE, AILERON_X)
    xj, dj = AILERON_JONC
    sect = section_coque(PROFIL_AILE, CORDE, clip=mobile, tubes=[AILERON_JONC], ames=2,
                         peau=PEAU_GOUVERNE, fourreau=0.6)
    pleine = Polygon(naca_points(PROFIL_AILE, CORDE)).intersection(mobile)
    pleine = pleine.difference(Point(xj * CORDE, naca_cambrure(PROFIL_AILE, xj) * CORDE)
                               .buffer(dj / 2 + JEU_TUBE / 2))
    ail = extrude_xz(sect, a0, a1)
    ail = ail.union(extrude_xz(pleine, a0, a0 + 1.2)).union(extrude_xz(pleine, a1 - 1.2, a1))
    if i == segs[0]:  # fente du guignol (le guignol PETG s'y glisse par-dessous)
        yh = Y_GUIGNOL_AILERON
        ail = ail.cut(extrude_xz(_fente_guignol(PROFIL_AILE, CORDE, AILERON_X, -1), yh - 1.1, yh + 1.1))
    return caler(ail, CALAGE_AILE)


def _x_guignol(code, corde, xh):
    """Étendue du guignol le long de la corde : juste derrière l'avant (en V) de la gouverne."""
    _, _, x_av = charniere(code, corde, xh)
    x0 = x_av + PEAU_GOUVERNE + 0.3
    return x0, x0 + 0.10 * corde


def _fente_guignol(code, corde, xh, sens):
    """Volume (2D) retiré dans la gouverne pour loger le guignol : tout sauf la peau opposée.

    sens = -1 : guignol sous la gouverne ; +1 : guignol sur le dessus."""
    profil = Polygon(naca_points(code, corde))
    x0, x1 = _x_guignol(code, corde, xh)
    garde = translate(profil, 0, sens * PEAU_GOUVERNE)  # garde la peau du côté opposé
    return profil.intersection(garde).intersection(box(x0 - 0.1, -100, x1 + 0.1, 100))


def guignol(code, corde, xh, jonc, sens, haut):
    """Guignol en PETG imprimé à plat : plaque de 2 mm qui remplit la gouverne sur sa
    hauteur, enfilée sur le jonc carbone et collée aux deux peaux, avec une patte qui
    sort de 'haut' mm pour la chape de la tringle."""
    profil = Polygon(naca_points(code, corde))
    x0, x1 = _x_guignol(code, corde, xh)
    dedans = _fente_guignol(code, corde, xh, sens).buffer(-0.1)
    zs = [z for x in (x0, x1) for z in naca_surfaces(code, corde, x / corde)]
    if sens < 0:
        z_bord = min(zs)
        patte = box(x0, z_bord - haut, x1, z_bord + 2)
    else:
        z_bord = max(zs)
        patte = box(x0, z_bord - 2, x1, z_bord + haut)
    plaque = dedans.union(patte.difference(profil)).union(patte.intersection(dedans.buffer(0.5)))
    plaque = plaque.buffer(0.8).buffer(-0.8)  # arrondit les angles
    xj, dj = jonc
    trous = [Point(xj * corde, naca_cambrure(code, xj) * corde).buffer(dj / 2 + 0.15)]
    for f in (0.55, 0.85):  # deux trous Ø1,6 pour le Z de la tringle
        trous.append(Point(x0 + 3.0, z_bord + sens * f * haut).buffer(0.8))
    return plaque.difference(unary_union(trous))


def guignol_aileron():
    g = guignol(PROFIL_AILE, CORDE, AILERON_X, AILERON_JONC, -1, GUIGNOL_HAUT * CORDE)
    yh = Y_GUIGNOL_AILERON
    return caler(extrude_xz(g, yh - 1.0, yh + 1.0), CALAGE_AILE)


def guignol_profondeur():
    g = guignol(STAB_PROFIL, STAB_CORDE, PROFONDEUR_X, PROFONDEUR_JONC, +1, GUIGNOL_HAUT * 2 * STAB_CORDE)
    yh = Y_GUIGNOL_PROF
    return extrude_xz(g, yh - 1.0, yh + 1.0).translate((STAB_BA_X, 0, STAB_Z))


def saumon():
    y0 = ENVERGURE / 2
    prof = naca_points(PROFIL_AILE, CORDE)
    w0 = cq.Wire.makePolygon([cq.Vector(x, y0, z) for x, z in prof], close=True)
    cx = 0.3 * CORDE
    w1 = cq.Wire.makePolygon([cq.Vector(cx + (x - cx) * 0.55, y0 + 18, z * 0.45)
                              for x, z in prof], close=True)
    s = cq.Workplane().add(cq.Solid.makeLoft([w0, w1], True))
    fixe, _, _ = charniere(PROFIL_AILE, CORDE, AILERON_X)   # l'aileron va jusqu'au bout de l'aile
    s = s.intersect(extrude_xz(fixe, y0 - 1, y0 + 20))
    return caler(s, CALAGE_AILE)


def pylone():
    """Carénage sous l'aile, vissé (2 vis M3 dans des inserts laiton) : reçoit la poutre."""
    l, zb, k = POUTRE_D + 8, POUTRE_Z, CORDE / 220.0
    e = POUTRE_D / 2 + 3
    cote = [(0, zb + 2), (14 * k, zb - e), (180 * k, zb - e), (204 * k, zb - 3), (204 * k, -5),
            (110 * k, 6), (14 * k, 4), (0, -6)]
    corps = (cq.Workplane("XZ", origin=(0, POUTRE_Y + l / 2, 0))
             .polyline(cote).close().extrude(l))
    aile = caler(extrude_xz(Polygon(naca_points(PROFIL_AILE, CORDE)).buffer(0.15),   # 0,15 mm pour la colle
                            POUTRE_Y - l, POUTRE_Y + l), CALAGE_AILE)
    try:  # arrondis d'abord (sinon l'arrondi des angles rentrants déborderait dans l'aile)
        corps = corps.edges("|Y").fillet(3)
    except Exception:
        pass
    corps = corps.cut(aile)
    alesage = (cq.Workplane("YZ", origin=(-10, POUTRE_Y, POUTRE_Z))
               .circle((POUTRE_D + JEU_TUBE) / 2).extrude(CORDE + 40))
    xcd, _ = position_tube(PROFIL_AILE, CORDE, CONDUIT[0], CALAGE_AILE)
    cable = (cq.Workplane("XY", origin=(xcd, POUTRE_Y, POUTRE_Z))
             .circle(min(5.0, POUTRE_D / 2 - 1)).extrude(40))
    # 2 perçages pour inserts laiton M3, depuis le dessus du pylône (contre l'aile)
    d, p = INSERT_PYLONE
    for x, zl, zh in vis_pylone():
        ins = cq.Workplane("XY", origin=(x, POUTRE_Y, zl - p)).circle(d / 2).extrude(p + 2)
        corps = corps.cut(caler(ins, CALAGE_AILE))
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


@functools.lru_cache(maxsize=None)
def fuselage_complet():
    ext = _loft_fus(SECTIONS_FUS)
    x0, w0, h0, z0 = SECTIONS_FUS[0]
    pointe = (x0 + 1.0, w0, h0, z0)     # intérieur conique jusqu'à la pointe : pas de plafond plat
    inte = _loft_fus([pointe] + SECTIONS_FUS[1:], PAROI_FUS)
    fus = ext.cut(inte)

    # fourreau du longeron principal traversant le fuselage ; la goupille (anti-rotation) n'a
    # qu'un bossage court dans chaque paroi (le conduit de câbles passe juste devant)
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
        if xc == GOUPILLE_X:
            bossages = ext.cut(_loft_fus(SECTIONS_FUS[1:], PAROI_FUS + 4.0))
            fus = fus.union(tube.union(goutte).intersect(bossages))
            fus = fus.cut(cq.Workplane("XZ", origin=(0, DEMI_LARGEUR_FUS + 15, 0)).center(x, z)
                          .circle(r).extrude(2 * DEMI_LARGEUR_FUS + 30))
            continue
        # voile sous la pointe de la goutte : part des parois à 45° et la porte sur toute la
        # largeur (sinon la pointe ferait un pont d'une paroi à l'autre dans le vide)
        xa, Y = x - R * math.sqrt(2) + 0.5, DEMI_LARGEUR_FUS + 5
        voile = (cq.Workplane("XY", origin=(0, 0, z - 0.8))
                 .polyline([(xa, 0), (xa, Y), (xa - Y, Y)]).close().extrude(1.6))
        voile = voile.union(voile.mirror("XZ")).intersect(ext)
        for c in COUPES_FUS[1:-1]:   # le voile s'arrête au joint, hors de la lèvre de l'autre tronçon
            if xa - Y < c < xa:
                voile = voile.cut(cq.Workplane().box(400, 400, 400).translate((c - 200, 0, 0)))
                anneau = ext.cut(_loft_fus(SECTIONS_FUS[1:], PAROI_FUS + 1.75))
                voile = voile.cut(anneau.intersect(cq.Workplane().box(14, 400, 400).translate((c + 5, 0, 0))))
        fus = fus.union(tube.union(goutte).union(voile).intersect(ext))
        trou = (cq.Workplane("XZ", origin=(0, DEMI_LARGEUR_FUS + 15, 0)).center(x, z)
                .circle(r).extrude(2 * DEMI_LARGEUR_FUS + 30))
        fus = fus.cut(trou)

    # passages de câbles vers les ailes (servos, ESC)
    xp, zp = position_tube(PROFIL_AILE, CORDE, CONDUIT[0], CALAGE_AILE)
    fus = fus.cut(cq.Workplane("XZ", origin=(0, DEMI_LARGEUR_FUS + 15, 0)).center(xp, zp).circle(CONDUIT[1])
                  .extrude(2 * DEMI_LARGEUR_FUS + 30))

    # ouverture du dessous pour les câbles de la nacelle caméra
    if NACELLE_X is not None:
        fus = fus.cut(cq.Workplane("XY", origin=(NACELLE_X, 0, -100)).rect(20, 16).extrude(20)
                      .edges("|Z").fillet(4))
        for dx in (-32.0, 32.0):  # vis de la selle de nacelle
            fus = fus.cut(cq.Workplane("XY", origin=(NACELLE_X + dx, 0, -100)).circle(1.7).extrude(20))

    # tube de Pitot dans le nez (seulement avec un capteur de vitesse)
    if PITOT:
        fus = fus.cut(cq.Workplane("YZ", origin=(SECTIONS_FUS[0][0] - 5, 0, SECTIONS_FUS[0][3]))
                      .circle(2.1).extrude(40))

    # trappe d'accès sur le dessus du fuselage : feuillure (rebord d'appui) + ouverture
    a, b = TRAPPE_ACCES_X
    hw, zt = TRAPPE_ACCES_DEMI_LARG, TRAPPE_ACCES_Z
    l16 = _loft_fus(SECTIONS_FUS[1:], 1.6)
    l31 = _loft_fus(SECTIONS_FUS[1:], 3.1)
    bande = (_prisme_xy(_contour_trappe_acces(3.0), zt - 4, 200)
             .cut(_prisme_xy(_contour_trappe_acces(-4.0), zt - 10, 200)))
    fus = fus.union(bande.intersect(inte.cut(l31)))
    for xv in _vis_trappe_acces():  # bossages des 2 vis M2 de la trappe
        w, h, zc = _section_a(xv)
        z_haut = zc + h / 2 - 2.5
        bos = cq.Workplane("XY", origin=(xv, 0, z_haut - 7)).circle(3.5).extrude(7)
        # dessous chanfreiné à 45° côté nez : le tronçon s'imprime nez en bas
        chanfrein = (cq.Workplane("XZ", origin=(0, 10, 0))
                     .polyline([(xv - 10, z_haut + 5), (xv + 10, z_haut - 15), (xv + 10, z_haut - 30),
                                (xv - 10, z_haut - 30)]).close().extrude(20))
        bos = bos.cut(chanfrein)
        fus = fus.union(bos.intersect(inte))
    # anneau d'appui de la cloison moteur (en escalier : s'imprime sans support) et
    # trous des 3 vis radiales M2 qui la retiennent
    xm = SECTIONS_FUS[-1][0]
    for k, ext_k in enumerate(_anneau_cloison()):
        fus = fus.union(_lamelle(xm - 5 - 2 * (k + 1), 2, PAROI_FUS - 0.2, PAROI_FUS + ext_k))
    for ang in ANGLES_VIS_CLOISON:
        fus = fus.cut(_vis_radiale(xm - 2.5, ang, 1.1, 20))

    # (les avant-trous Ø1,6 des vis se percent à la main en se servant de la trappe comme gabarit)
    fus = fus.cut(_prisme_xy(_contour_trappe_acces(), zt, 200).intersect(ext.cut(l16)))

    return fus, ext


def _contour_trappe_acces(marge=0.0):
    """Contour de la trappe d'accès vu de dessus. L'arrière est en pointe à 45° : le tronçon
    s'imprime nez en bas, le bout arrière de l'ouverture se referme donc progressivement au
    lieu de faire un pont de toute la largeur dans le vide."""
    a, b = TRAPPE_ACCES_X
    hw = TRAPPE_ACCES_DEMI_LARG
    p = Polygon([(a, -hw), (b - hw, -hw), (b, 0), (b - hw, hw), (a, hw)])
    return p.buffer(marge, join_style=2) if marge else p


def _vis_trappe_acces():
    a, b = TRAPPE_ACCES_X
    return (a + 2.0, b - 4.5)   # la vis arrière dans la pointe, sur la feuillure


def _z_interieur_trappe(x, y):
    """Hauteur de la face intérieure de la peau du dessus du fuselage (paroi de la trappe 1,6 mm)."""
    w, h, zc = _section_a(x)
    a, b = w / 2 - 1.6, h / 2 - 1.6
    u = min(abs(y) / a, 1.0)
    return zc + b * (1 - u ** SUPER_ELLIPSE_N) ** (1 / SUPER_ELLIPSE_N)


def geom_gps():
    """Berceau du GPS sous la trappe : centre, plan des plots, cotes de la cuvette, vis."""
    L, W, H = GPS_DIMS
    a, b = TRAPPE_ACCES_X
    xg = (a + b) / 2 + 10.0
    li, wi = L + 0.6, W + 0.6                 # logement du GPS (jeu 0,3 mm)
    lo, wo = li + 3.2, wi + 3.2               # cuvette (parois 1,6 mm)
    vis = [(xg - lo / 2 - 4.0, 0.0), (xg + lo / 2 + 4.0, 0.0)]
    pts = [(x, y) for x in (xg - lo / 2 - 8, xg, xg + lo / 2 + 8) for y in (-wo / 2, 0.0, wo / 2)]
    z_plot = min(_z_interieur_trappe(x, y) for x, y in pts) - 2.5   # plan d'appui, sous la peau
    profondeur = H + 1.5                      # GPS + 1 mm de mousse + 0,5 mm de jeu
    return dict(xg=xg, li=li, wi=wi, lo=lo, wo=wo, vis=vis, z_plot=z_plot, profondeur=profondeur, H=H)


def support_gps():
    """Berceau PETG vissé sous la trappe (2 vis M2 autotaraudeuses) : le GPS s'y pose antenne
    vers le haut, sur 1 mm de mousse, retenu par un rebord ; fenêtre et encoche pour le fil."""
    g = geom_gps()
    z0, d = g["z_plot"], g["profondeur"]
    cuve = (cq.Workplane("XY", origin=(g["xg"], 0, z0 - d - 1.6)).rect(g["lo"], g["wo"]).extrude(d + 1.6)
            .edges("|Z").fillet(1.5))
    cuve = cuve.cut(cq.Workplane("XY", origin=(g["xg"], 0, z0 - d)).rect(g["li"], g["wi"]).extrude(d + 1))
    cuve = cuve.cut(cq.Workplane("XY", origin=(g["xg"], 0, z0 - d - 3)).rect(g["li"] - 6, g["wi"] - 6).extrude(5))
    cuve = cuve.cut(cq.Workplane("XY", origin=(g["xg"] + g["lo"] / 2, 0, z0 - d)).rect(4, 8).extrude(d + 1))
    for x, y in g["vis"]:   # oreilles au niveau du rebord
        o = cq.Workplane("XY", origin=(x, y, z0 - 2.0)).rect(10, 9).extrude(2.0).edges("|Z").fillet(2)
        cuve = cuve.union(o).cut(cq.Workplane("XY", origin=(x, y, z0 - 5)).circle(1.1).extrude(10))
    return cuve


def trappe_acces():
    """Trappe PETG sur le dessus du fuselage : accès au contrôleur de vol (USB, carte SD,
    câblage) sans démonter l'avion. Elle repose sur une feuillure et tient par 2 vis M2."""
    a, b = TRAPPE_ACCES_X
    hw, zt = TRAPPE_ACCES_DEMI_LARG, TRAPPE_ACCES_Z
    ext = _loft_fus(SECTIONS_FUS)
    l16 = _loft_fus(SECTIONS_FUS[1:], 1.6)
    t = _prisme_xy(_contour_trappe_acces(-0.3), zt, 200).intersect(ext.cut(l16))
    for xv in _vis_trappe_acces():
        t = t.cut(cq.Workplane("XY", origin=(xv, 0, zt - 5)).circle(1.2).extrude(60))
    # 2 plots sous la peau pour visser le berceau du GPS (avant-trous Ø1,6, sans traverser la peau)
    g = geom_gps()
    for x, y in g["vis"]:
        z_peau = _z_interieur_trappe(x, y)
        plot = cq.Workplane("XY", origin=(x, y, g["z_plot"])).circle(3.5).extrude(z_peau - g["z_plot"] + 0.8)
        t = t.union(plot.intersect(ext))
        t = t.cut(cq.Workplane("XY", origin=(x, y, g["z_plot"] - 1)).circle(0.8).extrude(z_peau - g["z_plot"] + 1.6))
    return t


ANGLES_VIS_CLOISON = (90.0, 210.0, 330.0)


def _anneau_cloison():
    """Largeurs (vers l'intérieur) des 3 marches de l'anneau d'appui, laissant passer les
    têtes des vis du moteur."""
    xm = SECTIONS_FUS[-1][0]
    w, h, _ = _section_a(xm)
    r_int = min(w, h) / 2 - PAROI_FUS
    r_tetes = max(math.hypot(a, b) for a, b in POUSSEUR_TROUS) + 3.0
    largeur = max(1.5, min(5.0, r_int - r_tetes - 0.5))
    return (largeur / 3, 2 * largeur / 3, largeur)


def _vis_radiale(x, ang, r, longueur):
    """Cylindre radial (depuis l'extérieur vers l'axe du moteur) à l'angle donné (0° = côté droit)."""
    w, h, zc = _section_a(x)
    a = math.radians(ang)
    d = cq.Vector(0, math.cos(a), math.sin(a))
    rayon = max(w, h) / 2 + 5
    base = cq.Vector(x, rayon * d.y, POUSSEUR_Z + rayon * d.z)
    return cq.Workplane().add(cq.Solid.makeCylinder(r, longueur, base, -d))


def cloison_moteur():
    """Cloison PETG glissée par l'arrière dans le bout du fuselage, en appui sur l'anneau
    intérieur et retenue par 3 vis M2 radiales : le moteur se boulonne dessus à l'établi
    et l'ensemble se démonte sans rien couper."""
    xm, ep = SECTIONS_FUS[-1][0], 5.0
    cloison = _lamelle(xm - ep, ep, PAROI_FUS + 0.15, None)
    for ang in ANGLES_VIS_CLOISON:  # avant-trous Ø1,6 des vis radiales, dans la tranche
        cloison = cloison.cut(_vis_radiale(xm - 2.5, ang, 0.8, 12))
    o = (xm - 10, 0, POUSSEUR_Z)
    perc = cq.Workplane("YZ", origin=o).circle(5).extrude(20)
    for cy, cz in POUSSEUR_TROUS:  # vis M3 du moteur
        perc = perc.union(cq.Workplane("YZ", origin=o).center(cy, cz).circle(1.7).extrude(20))
    return cloison.cut(perc)


def _levre(x, long=10.0, collet=6.0):
    """Lèvre d'emboîtement qui suit la forme du fuselage (même là où il rétrécit).

    Le collet (côté du tronçon qui la porte) fusionne avec la peau : la lèvre est
    portée par son tronçon et s'imprime dans le prolongement de la paroi."""
    def fil(xx, r):
        w, h, zc = _section_a(xx)
        return _super_ellipse(xx, w - 2 * r, h - 2 * r, zc)
    ext = cq.Solid.makeLoft([fil(x - 1.0, PAROI_FUS + 0.25), fil(x + long, PAROI_FUS + 0.25)], True)
    col = cq.Solid.makeLoft([fil(x - collet, PAROI_FUS - 0.3), fil(x, PAROI_FUS - 0.3)], True)
    inte = cq.Solid.makeLoft([fil(x - collet - 1, PAROI_FUS + 1.45), fil(x + long + 1, PAROI_FUS + 1.45)], True)
    return cq.Workplane().add(ext).union(cq.Workplane().add(col)).cut(cq.Workplane().add(inte))


@functools.lru_cache(maxsize=None)
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
        morceaux[k] = morceaux[k].union(_levre(x))
    return morceaux  # dans l'ordre de NOMS_TRONCONS_FUS


def plateau_electronique():
    """Plateau de batterie glissé dans le fuselage (posé sur 2 plots vissés à la selle de
    nacelle sur le DFR) : butée arrière de centrage, fentes pour 2 sangles."""
    z0, ep, larg = PLATEAU_Z, 2.0, PLATEAU_LARG
    x0, x1 = PLATEAU_X
    p = (cq.Workplane("XY", origin=(0, 0, z0)).center((x0 + x1) / 2, 0)
         .rect(x1 - x0, larg).extrude(ep).edges("|Z").fillet(6))
    # butée arrière : la batterie poussée contre elle est au bon endroit pour le centrage
    lb, wb, hb = BATTERIE
    xr = X_BATTERIE + lb / 2
    poteau = (larg - 18) / 2                  # encoche centrale de 18 mm pour les fils
    for sy in (-1, 1):
        p = p.union(cq.Workplane("XY", origin=(xr + 1.5, sy * (9 + poteau / 2), z0 + ep))
                    .box(3, poteau, 15, centered=(True, True, False)))
        p = p.union(cq.Workplane("XY", origin=(xr + 6, sy * (9 + poteau / 2), z0 + ep))   # gousset
                    .box(9, 3, 10, centered=(True, True, False)))
    # fentes pour 2 sangles, près du nez pour pouvoir les fermer par l'ouverture
    xav = X_BATTERIE - lb / 2              # avant de la batterie
    for xs in (xav + 10, xav + 42):
        for ys in (-(larg / 2 - 10), larg / 2 - 10):
            p = p.cut(cq.Workplane("XY", origin=(0, 0, z0 - 1)).center(xs, ys)
                      .slot2D(22, 4, 90).extrude(ep + 2))
    # trous des vis M3 de la selle de nacelle (entretoises séparées sous le plateau)
    for dx in ((-32.0, 32.0) if NACELLE_X is not None else ()):
        p = p.cut(cq.Workplane("XY", origin=(NACELLE_X + dx, 0, z0 - 1)).circle(1.7).extrude(ep + 2))
    return p


def entretoise_plateau(k):
    """Entretoise PETG entre le fond du fuselage et le plateau de batterie (vis M3 de la selle)."""
    dx = (-32.0, 32.0)[k]
    _, h, zc = _section_a(NACELLE_X + dx)
    fond = zc - h / 2 + PAROI_FUS + 0.3
    return (cq.Workplane("XY", origin=(NACELLE_X + dx, 0, fond)).circle(5).extrude(PLATEAU_Z - fond)
            .cut(cq.Workplane("XY", origin=(NACELLE_X + dx, 0, fond - 1)).circle(1.7).extrude(PLATEAU_Z - fond + 2)))


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
            pos = (xf + sx * FC_TROUS[0] / 2, sy * FC_TROUS[1] / 2)
            p = p.union(cq.Workplane("XY", origin=(0, 0, z0 + ep)).center(*pos).circle(4.0).extrude(6))
            p = p.cut(cq.Workplane("XY", origin=(0, 0, z0 - 1)).center(*pos).circle(1.35).extrude(ep + 8))
            # logement d'insert laiton M3 (Ø4 x 5,7) posé au fer à souder
            p = p.cut(cq.Workplane("XY", origin=(0, 0, z0 + ep + 0.2)).center(*pos).circle(2.0).extrude(6))
    # flèche « avant » : la flèche du contrôleur de vol doit pointer dans le même sens
    fl = [(xf - FC_DIMS[0] / 2 - 2, 0), (xf - FC_DIMS[0] / 2 + 6, -4), (xf - FC_DIMS[0] / 2 + 6, 4)]
    p = p.cut(cq.Workplane("XY", origin=(0, 0, z0 + ep - 0.6)).polyline(fl).close().extrude(1))
    if PI5:
        cx = x1 - 38
        for sx in (-1, 1):  # trous de fixation Raspberry Pi : 58 x 49 mm
            for sy in (-1, 1):
                pos = (cx + sx * 29, sy * 24.5)
                p = p.union(cq.Workplane("XY", origin=(0, 0, z0 + ep)).center(*pos).circle(3.5).extrude(5))
                p = p.cut(cq.Workplane("XY", origin=(0, 0, z0 - 1)).center(*pos).circle(1.1).extrude(ep + 7))
                # logement d'insert laiton M2.5 (Ø3,5 x 4)
                p = p.cut(cq.Workplane("XY", origin=(0, 0, z0 + ep + 1)).center(*pos).circle(1.75).extrude(5))
        p = p.cut(cq.Workplane("XY", origin=(0, 0, z0 - 1)).center(cx, 0).rect(30, 20).extrude(ep + 2)
                  .edges("|Z").fillet(4))
    return p


# ---------------------------------------------------------------------------
# Propulsion VTOL et atterrisseur
# ---------------------------------------------------------------------------
def _geom_support():
    r_int = (POUTRE_D + JEU_TUBE) / 2
    r_ext = r_int + 4.8
    zp = r_ext - 4                       # dessous de la bride (au-dessus de l'axe de la poutre)
    s = r_ext + 4.0                      # vis de coin : à côté du collier, accessibles par-dessous
    cote = max(MOTEUR_VTOL_DIAM + 4, 2 * s + 8)
    lg = min(36.0, cote - 6)             # longueur du collier
    return r_int, r_ext, zp, s, cote, lg


def support_moteur(x0, y0=POUTRE_Y):
    """Collier serré sur la poutre (2 vis M3 + écrous) surmonté d'une bride carrée.

    La platine moteur se visse sur la bride par 4 vis M3 x 8 passées par-dessous, à côté
    du collier : on les atteint avec un tournevis même quand le support est sur la poutre.
    """
    zb = POUTRE_Z
    r_int, r_ext, zp, s, cote, lg = _geom_support()
    corps = cq.Workplane("YZ", origin=(x0 - lg / 2, y0, zb)).circle(r_ext).extrude(lg)
    corps = corps.union(cq.Workplane("XY", origin=(x0, y0, zb)).box(lg, POUTRE_D + 4, zp, centered=(True, True, False)))
    corps = corps.union(cq.Workplane("XY", origin=(x0, y0, zb + zp)).box(cote, cote, 4, centered=(True, True, False))
                        .edges("|Z").fillet(5))
    corps = corps.union(cq.Workplane("XY", origin=(x0, y0, zb - r_ext - 8)).box(lg, 12, 9, centered=(True, True, False)))
    corps = corps.cut(cq.Workplane("YZ", origin=(x0 - lg / 2 - 2, y0, zb)).circle(r_int).extrude(lg + 4))
    corps = corps.cut(cq.Workplane("XY", origin=(x0, y0, zb - r_ext - 12)).box(lg + 4, 1.5, r_ext + 12, centered=(True, True, False)))
    for dx in (-lg / 4, lg / 4):  # vis de serrage M3 + écrou logé dans un hexagone
        corps = corps.cut(cq.Workplane("XZ", origin=(0, y0 + 10, 0)).center(x0 + dx, zb - r_ext - 3.5)
                          .circle(1.65).extrude(20))
        corps = corps.cut(cq.Workplane("XZ", origin=(0, y0 + 6.01, 0)).center(x0 + dx, zb - r_ext - 3.5)
                          .polygon(6, 6.4).extrude(2.6))
    # vis de coin M3 (passage) et logements des têtes de vis du moteur
    for sx in (-1, 1):
        for sy in (-1, 1):
            corps = corps.cut(cq.Workplane("XY", origin=(x0 + sx * s, y0 + sy * s, zb + zp - 1)).circle(1.65).extrude(6))
    for dx, dy in MOTEUR_VTOL_TROUS:
        corps = corps.cut(cq.Workplane("XY", origin=(x0 + dx, y0 + dy, zb + zp + 0.8)).circle(3.3).extrude(4))
    corps = corps.cut(cq.Workplane("XY", origin=(x0, y0, zb + zp + 1)).circle(6.0).extrude(4))
    return corps


def platine_moteur(x0, y0=POUTRE_Y):
    """Platine vissée sous le moteur (vis M3 par-dessous, têtes logées dans la bride),
    puis posée sur la bride et tenue par 4 vis de coin M3 x 8 qui s'y taraudent."""
    zb = POUTRE_Z
    r_int, r_ext, zp, s, cote, lg = _geom_support()
    z0 = zb + zp + 4
    p = (cq.Workplane("XY", origin=(x0, y0, z0)).box(cote, cote, 4, centered=(True, True, False))
         .edges("|Z").fillet(5))
    for dx, dy in MOTEUR_VTOL_TROUS:
        p = p.cut(cq.Workplane("XY", origin=(x0 + dx, y0 + dy, z0 - 1)).circle(1.7).extrude(6))
    for sx in (-1, 1):
        for sy in (-1, 1):  # avant-trous des vis de coin
            p = p.cut(cq.Workplane("XY", origin=(x0 + sx * s, y0 + sy * s, z0 - 1)).circle(1.3).extrude(4.5))
    p = p.cut(cq.Workplane("XY", origin=(x0, y0, z0 - 1)).circle(6.0).extrude(6))
    return p


def patte(x0, y0=POUTRE_Y):
    """Patte d'atterrissage en TPU, enfilée sur la poutre."""
    zb = POUTRE_Z
    (b0, b1), (b2, b3) = PATTE_SECTION
    bague = (cq.Workplane("YZ", origin=(x0 - 9, y0, zb)).circle(POUTRE_D / 2 + 4).extrude(18)
             .cut(cq.Workplane("YZ", origin=(x0 - 10, y0, zb)).circle(POUTRE_D / 2 - 0.1).extrude(20)))
    jambe = (cq.Workplane("XY", origin=(x0, y0, zb - PATTE_LONG + 5))
             .rect(b0, b1).workplane(offset=PATTE_LONG - 5 - (POUTRE_D / 2 + 1)).rect(b2, b3).loft())
    pied = (cq.Workplane("XY", origin=(x0, y0, zb - PATTE_LONG)).rect(*PATTE_PIED).extrude(6)
            .edges("|Z").fillet(8))
    alesage = cq.Workplane("YZ", origin=(x0 - 10, y0, zb)).circle(POUTRE_D / 2 - 0.1).extrude(20)
    return bague.union(jambe).union(pied).cut(alesage)


# ---------------------------------------------------------------------------
# Empennage
# ---------------------------------------------------------------------------
def _stab_bornes():
    n, d = STAB_N_SEG, STAB_DEMI_ENV
    return [(-d + 2 * d * i / n, -d + 2 * d * (i + 1) / n) for i in range(n)]


def stab_segment(i):
    ya, yb = _stab_bornes()[i]
    fixe, _, _ = charniere(STAB_PROFIL, STAB_CORDE, PROFONDEUR_X)
    sect = section_coque(STAB_PROFIL, STAB_CORDE, clip=fixe, ames=3,
                         tubes=[(STAB_LONGERON_X, STAB_LONGERON_D), (STAB_JONC_X, STAB_JONC_D)])
    return extrude_xz(sect, ya, yb).translate((STAB_BA_X, 0, STAB_Z))


def profondeur(i):
    ya, yb = _stab_bornes()[i]
    _, mobile, _ = charniere(STAB_PROFIL, STAB_CORDE, PROFONDEUR_X)
    sect = section_coque(STAB_PROFIL, STAB_CORDE, clip=mobile, tubes=[PROFONDEUR_JONC], ames=2,
                         peau=PEAU_GOUVERNE, fourreau=0.6)
    prof = extrude_xz(sect, ya + 0.5, yb - 0.5)
    if i == STAB_N_SEG - 1:  # fente du guignol, côté droit près du servo
        yh = Y_GUIGNOL_PROF
        prof = prof.cut(extrude_xz(_fente_guignol(STAB_PROFIL, STAB_CORDE, PROFONDEUR_X, +1), yh - 1.1, yh + 1.1))
    return prof.translate((STAB_BA_X, 0, STAB_Z))


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
        xs_ = STAB_BA_X + xc * STAB_CORDE
        bloc = bloc.cut(cq.Workplane().add(cq.Solid.makeCylinder(
            (d + JEU_TUBE) / 2, 15, cq.Vector(xs_, y0 - dl - 1, STAB_Z), cq.Vector(0, 1, 0))))
    # baie de servo de profondeur, ouverte côté intérieur : le boîtier s'enfonce jusqu'aux
    # oreilles, qui s'appuient sur la face du bloc et s'y vissent (vis M2 fournies avec le servo)
    L, W = SERVO["L"], SERVO["W"]
    prof = SERVO["oreille_y"] + 0.5
    xs = X_SERVO_PROF            # axe du servo ~15 mm devant la charnière : palonnier au-dessus du stab
    zc = STAB_Z + 6 + (W + 0.4) / 2
    bloc = bloc.cut(cq.Workplane("XY", origin=(0, 0, STAB_Z + 6)).center(xs, y0 - dl + prof / 2)
                    .rect(L + 0.6, prof).extrude(W + 0.4))
    for sx in (-1, 1):
        bloc = bloc.cut(cq.Workplane("XZ", origin=(0, y0 - dl - 1, 0)).center(xs + sx * SERVO["entraxe"] / 2, zc)
                        .circle(0.75).extrude(-9))
    # passage de câble poutre -> servo
    bloc = bloc.cut(cq.Workplane("XY", origin=(0, 0, zb)).center(xs - 8, y0).circle(min(3.0, POUTRE_D / 2 - 1.5))
                    .extrude(STAB_Z + 7 - zb))
    return bloc


# ---------------------------------------------------------------------------
# Inventaire des pièces imprimées
# ---------------------------------------------------------------------------
X_MOT_AV = CG_X - MOTEUR_ECART
X_MOT_AR = CG_X + MOTEUR_ECART
X_PATTE_AV = X_MOT_AV + PATTE_DECALAGE
X_PATTE_AR = X_MOT_AR - PATTE_DECALAGE
X_AXE_SERVO_PROF = STAB_BA_X + PROFONDEUR_X * STAB_CORDE - 15
X_SERVO_PROF = X_AXE_SERVO_PROF - (SERVO["L"] / 2 - SERVO["axe"])   # centre du boîtier


def inventaire():
    """(nom, fonction, quantité, matériau, orientation, parois mm, remplissage, miroir)

    orientation : 'Y' = l'envergure devient verticale (emplanture sur le plateau),
                  'X' = l'axe X devient vertical (nez en bas), 'Xinv' = nez en haut,
                  'Z' = tel quel, 'Zinv' = retourné, 'Zcal' = calage d'aile annulé (à plat).
    miroir : True -> on exporte aussi la version gauche.
    """
    inv = []
    for i in range(N_SEGMENTS):
        inv.append((f"aile_segment_{i + 1}", lambda i=i: segment_aile(i), 1, "PLA Aero",
                    "Yinv" if i == 0 else "Y", None, 0, True))
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
        ("platine_moteur", lambda: platine_moteur(X_MOT_AV), 4, "PETG", "Z", 1.6, 1.0, False),
        ("patte_atterrissage", lambda: patte(X_PATTE_AV), 4, "TPU 95A", "Z", 1.6, 0.25, False),
        ("bloc_queue", bloc_queue, 1, "PLA Aero", "Z", 1.2, 0.08, True),
    ]
    inv.append(("trappe_acces", trappe_acces, 1, "PETG", "X", 1.6, 1.0, False))
    inv.append(("support_gps", support_gps, 1, "PETG", "Zinv", 1.2, 1.0, False))
    inv.append(("guignol_aileron", guignol_aileron, 2, "PETG", "Y", 2.0, 1.0, False))
    inv.append(("cadre_servo_aile", cadre_servo_aile, 1, "PETG", "Zcal", 1.2, 0.30, True))
    inv.append(("trappe_servo_aile", trappe_servo_aile, 1, "PETG", "Zcal", 1.2, 1.0, True))
    inv.append(("guignol_profondeur", guignol_profondeur, 1, "PETG", "Y", 2.0, 1.0, False))
    if NACELLE_X is not None:
        inv.append(("support_nacelle", support_nacelle, 1, "PETG", "Z", 1.6, 0.30, False))
        inv.append(("entretoise_plateau_avant", lambda: entretoise_plateau(0), 1, "PETG", "Z", 1.6, 1.0, False))
        inv.append(("entretoise_plateau_arriere", lambda: entretoise_plateau(1), 1, "PETG", "Z", 1.6, 1.0, False))
    for i in range(STAB_N_SEG):
        inv.append((f"stab_segment_{i + 1}", lambda i=i: stab_segment(i), 1, "PLA Aero", "Y", None, 0, False))
        inv.append((f"profondeur_{i + 1}", lambda i=i: profondeur(i), 1, "PLA Aero", "Y", None, 0, False))
    return inv
