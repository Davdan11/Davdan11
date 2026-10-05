"""Détection des porte-à-faux : on tranche la pièce couche par couche, comme le trancheur,
et on mesure jusqu'où chaque couche dépasse dans le vide au-dessus de la précédente."""
import numpy as np
from shapely.geometry import Point, Polygon

PAS = 0.3          # mm entre deux tranches
PENTE = 0.3        # dépassement toléré par couche (≈ 45°)


def _couche(m, z):
    s = m.section(plane_origin=(0, 0, z), plane_normal=(0, 0, 1))
    if s is None:
        return None
    forme = None   # pair-impair : les boucles intérieures creusent les extérieures
    for b in s.discrete:
        if len(b) < 4:
            continue
        g = Polygon(b[:, :2]).buffer(0)
        forme = g if forme is None else forme.symmetric_difference(g)
    return forme


def pire_porte_a_faux(m):
    """Retourne (distance max dans le vide en mm, hauteur z) pour un maillage déjà orienté."""
    z0, z1 = m.bounds[0, 2], m.bounds[1, 2]
    prec, pire = None, (0.0, 0.0)
    for z in np.arange(z0 + PAS / 2, z1, PAS):
        c = _couche(m, z)
        if c is None or c.is_empty:
            prec = None
            continue
        if prec is not None:
            vide = c.difference(prec.buffer(PENTE))
            for g in getattr(vide, "geoms", [vide]):
                if g.area < 1.0:
                    continue
                pts = list(g.exterior.coords)
                d = max(prec.distance(Point(q)) for q in pts)
                if d > pire[0]:
                    pire = (d, z - z0)
        prec = c
    return pire
