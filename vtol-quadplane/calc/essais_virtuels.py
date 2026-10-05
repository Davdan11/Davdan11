"""Essais virtuels : pression sur l'aile, charges de vol, résistance, stabilité, servos.

    python calc/essais_virtuels.py                       # Huard DFR  -> docs/essais_virtuels.md
    HUARD_VERSION=mini python calc/essais_virtuels.py    # Huard Mini -> docs/essais_virtuels_mini.md

Méthodes classiques de pré-dimensionnement d'avion léger, appliquées aux cotes réelles
du modèle (cad/params_*.py) :
  1. pression sur le profil (méthode des panneaux, tourbillons linéaires) ;
  2. facteurs de charge : manœuvre et rafale (formule de Pratt) ;
  3. flexion de l'aile (répartition de Schrenk) : longerons carbone et peau imprimée ;
  4. torsion de l'aile, goupille, inversion d'ailerons et divergence ;
  5. peau entre les âmes : flexion sous la pression et voilement ;
  6. stabilité longitudinale (point neutre, marge statique), volumes d'empennage, braquage
     de profondeur pour équilibrer ;
  7. couple demandé aux servos ;
  8. poutres en vol stationnaire plein gaz, fréquence propre, atterrissage dur.
Les propriétés des matériaux imprimés sont prudentes (pas de mesure) : voir HYPOTHÈSES.
"""
import math
import os
import sys

import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, os.path.join(RACINE, "cad"))
sys.path.insert(0, ICI)
import dimensionnement as D  # noqa: E402
import pieces as P  # noqa: E402
from params import *  # noqa: E402,F403

G, RHO = 9.81, 1.225

# --- Hypothèses -----------------------------------------------------------------
PLA_AERO = dict(E=900.0, G=330.0, nu=0.35, sigma=12.0, tau=7.0)   # MPa, PLA Aero moussé (prudent)
CARBONE_TUBE = dict(E=100e3, sigma=500.0, tau=150.0)              # MPa, tube roulé (prudent)
CARBONE_JONC = dict(E=120e3, sigma=900.0, tau=250.0)              # MPa, jonc pultrudé
N_MANOEUVRE = 3.8          # facteur de charge limite (catégorie normale)
N_NEGATIF = -1.5
SECURITE = 1.5             # charge extrême = 1,5 x charge limite
RAFALE = 7.6               # m/s (25 ft/s), rafale verticale à la vitesse de croisière
CM_AC = -0.09              # NACA 4412, moment au foyer
CH_DELTA, CH_ALPHA = -0.60, -0.35    # moment de charnière par radian (gouverne simple)
TAU_PROF = 0.55            # efficacité de la profondeur (30 % de corde)
K_FUS = 0.012              # Raymer : effet déstabilisant du fuselage, par degré
DEBATTEMENT = 20.0         # degrés de braquage des gouvernes (SERVO_MIN/MAX dans ArduPilot)
COURSE_SERVO = 45.0        # degrés de rotation du servo de part et d'autre du neutre
COURSE_PATTE = 10.0        # mm d'écrasement des pattes TPU à l'atterrissage dur
V_ATTERRISSAGE_DUR = 2.0   # m/s (atterrissage normal ArduPilot : 0,5 m/s)
if VERSION == "dfr":
    SERVO_COUPLE = 2.0     # kg.cm, EMAX ES08MD II à 4,8 V
    MASSE_POD = 0.171 + 0.022 + 0.010 + 0.030   # moteur, hélice, ESC, support : kg
    KV, TENSION, PALES = 400, 22.2, 2
else:
    SERVO_COUPLE = 2.2     # kg.cm, JX PDI-1109MG à 4,8 V
    MASSE_POD = 0.056 + 0.010 + 0.007 + 0.015
    KV, TENSION, PALES = 1300, 14.8, 3
V_MAX = {"dfr": 30.0, "mini": 22.0}[VERSION]      # AIRSPEED_MAX des paramètres ArduPilot
V_CROISIERE = {"dfr": 25.0, "mini": 16.0}[VERSION]
V_PLONGEE = 1.25 * V_MAX


# ---------------------------------------------------------------------------
# 1. Méthode des panneaux (Kuethe & Chow, tourbillons d'intensité linéaire)
# ---------------------------------------------------------------------------
def naca4(code, n=80):
    m, p, t = int(code[0]) / 100, int(code[1]) / 10, int(code[2:]) / 100
    beta = np.linspace(0, math.pi, n + 1)
    x = 0.5 * (1 - np.cos(beta))
    yt = 5 * t * (0.2969 * np.sqrt(x) - 0.1260 * x - 0.3516 * x ** 2 + 0.2843 * x ** 3 - 0.1036 * x ** 4)
    if m == 0:
        yc, dyc = np.zeros_like(x), np.zeros_like(x)
    else:
        yc = np.where(x < p, m / p ** 2 * (2 * p * x - x ** 2), m / (1 - p) ** 2 * (1 - 2 * p + 2 * p * x - x ** 2))
        dyc = np.where(x < p, 2 * m / p ** 2 * (p - x), 2 * m / (1 - p) ** 2 * (p - x))
    th = np.arctan(dyc)
    xu, yu = x - yt * np.sin(th), yc + yt * np.cos(th)
    xl, yl = x + yt * np.sin(th), yc - yt * np.cos(th)
    # bord de fuite -> intrados -> bord d'attaque -> extrados -> bord de fuite (sens horaire)
    X = np.concatenate([xl[::-1], xu[1:]])
    Y = np.concatenate([yl[::-1], yu[1:]])
    return X, Y


def panneaux(code, alpha_deg, n=80):
    """Retourne (x milieu, Cp, extrados?) et (Cl, Cm au quart de corde)."""
    X, Y = naca4(code, n)
    N = len(X) - 1
    a = math.radians(alpha_deg)
    xc, yc = (X[:-1] + X[1:]) / 2, (Y[:-1] + Y[1:]) / 2
    S = np.hypot(np.diff(X), np.diff(Y))
    th = np.arctan2(np.diff(Y), np.diff(X))
    CN1, CN2, CT1, CT2 = (np.zeros((N, N)) for _ in range(4))
    for i in range(N):
        for j in range(N):
            if i == j:
                CN1[i, j], CN2[i, j], CT1[i, j], CT2[i, j] = -1.0, 1.0, math.pi / 2, math.pi / 2
                continue
            A = -(xc[i] - X[j]) * math.cos(th[j]) - (yc[i] - Y[j]) * math.sin(th[j])
            B = (xc[i] - X[j]) ** 2 + (yc[i] - Y[j]) ** 2
            C = math.sin(th[i] - th[j])
            Dd = math.cos(th[i] - th[j])
            E = (xc[i] - X[j]) * math.sin(th[j]) - (yc[i] - Y[j]) * math.cos(th[j])
            F = math.log(1 + S[j] * (S[j] + 2 * A) / B)
            Gg = math.atan2(E * S[j], B + A * S[j])
            Pp = (xc[i] - X[j]) * math.sin(th[i] - 2 * th[j]) + (yc[i] - Y[j]) * math.cos(th[i] - 2 * th[j])
            Q = (xc[i] - X[j]) * math.cos(th[i] - 2 * th[j]) - (yc[i] - Y[j]) * math.sin(th[i] - 2 * th[j])
            CN2[i, j] = Dd + 0.5 * Q * F / S[j] - (A * C + Dd * E) * Gg / S[j]
            CN1[i, j] = 0.5 * Dd * F + C * Gg - CN2[i, j]
            CT2[i, j] = C + 0.5 * Pp * F / S[j] + (A * Dd - C * E) * Gg / S[j]
            CT1[i, j] = 0.5 * C * F - Dd * Gg - CT2[i, j]
    AN, AT = np.zeros((N + 1, N + 1)), np.zeros((N, N + 1))
    AN[:N, 0], AN[:N, N] = CN1[:, 0], CN2[:, N - 1]
    AT[:, 0], AT[:, N] = CT1[:, 0], CT2[:, N - 1]
    AN[:N, 1:N] = CN1[:, 1:] + CN2[:, :-1]
    AT[:, 1:N] = CT1[:, 1:] + CT2[:, :-1]
    AN[N, 0] = AN[N, N] = 1.0     # condition de Kutta
    rhs = np.concatenate([np.sin(th - a), [0.0]])
    gam = np.linalg.solve(AN, rhs)
    V = np.cos(th - a) + AT @ gam
    cp = 1 - V ** 2
    # efforts : pression sur chaque panneau, normale extérieure
    nx, ny = -np.sin(th), np.cos(th)
    fx, fy = -cp * S * nx, -cp * S * ny
    cl = fy.sum() * math.cos(a) - fx.sum() * math.sin(a)
    cm = (-(xc - 0.25) * fy + yc * fx).sum()
    extrados = np.arange(N) >= N // 2
    return xc, cp, extrados, cl, cm


def alpha_pour_cl(code, cl_vise):
    a0, a1 = -4.0, 10.0
    for _ in range(30):
        am = (a0 + a1) / 2
        if panneaux(code, am, 60)[3] < cl_vise:
            a0 = am
        else:
            a1 = am
    return (a0 + a1) / 2


# ---------------------------------------------------------------------------
# Outils
# ---------------------------------------------------------------------------
def tube_I(d, ep=1.0):
    di = d - 2 * ep
    return math.pi * (d ** 4 - di ** 4) / 64


def jonc_I(d):
    return math.pi * d ** 4 / 64


def surfaces(code, corde, x):
    return P.naca_surfaces(code, corde, x)


def courbure_extrados(code, corde, x):
    h = 0.002
    z = [surfaces(code, corde, min(max(x + k * h, 0.01), 0.99))[0] / corde for k in (-1, 0, 1)]
    d1 = (z[2] - z[0]) / (2 * h)
    d2 = (z[2] - 2 * z[1] + z[0]) / h ** 2
    return corde * (1 + d1 ** 2) ** 1.5 / max(abs(d2), 1e-6)


def appuis_peau(i):
    """Positions (mm) où la peau d'extrados et d'intrados du segment i est tenue (âmes, fourreaux)."""
    ya, yb = P.bornes_segments()[i]
    tubes = P._tubes_aile(ya, yb)
    ames, x1 = P.ames_segment(i), 0.92 * CORDE
    if yb > AILERON_DEBUT:  # partie fixe devant la charnière
        fixe, _, _ = P.charniere(PROFIL_AILE, CORDE, AILERON_X)
        ames, x1 = P.ames_segment(i) - 2, min(0.92 * CORDE, fixe.bounds[2])
    a = 0.06 * CORDE
    xs = [a + (x1 - a) * i / ames for i in range(ames + 1)]
    haut = [x for i, x in enumerate(xs) if i % 2 == 1] + [a, x1]
    bas = [x for i, x in enumerate(xs) if i % 2 == 0] + [x1]
    for xc, _ in tubes:
        haut.append(xc * CORDE)
        bas.append(xc * CORDE)
    return sorted(haut), sorted(bas), tubes


def section_I_peau(i):
    """Moment quadratique (mm⁴) de la coque imprimée du segment i autour de l'axe des longerons."""
    ya, yb = P.bornes_segments()[i]
    tubes = P._tubes_aile(ya, yb)
    sect = P.section_coque(PROFIL_AILE, CORDE, tubes=tubes, ames=P.ames_segment(i), conduit=CONDUIT)
    zc = P.naca_cambrure(PROFIL_AILE, LONGERON_PRINC_X) * CORDE
    I = 0.0
    geoms = getattr(sect, "geoms", [sect])
    for g in geoms:
        for anneau, signe in [(g.exterior, 1)] + [(r, -1) for r in g.interiors]:
            c = np.array(anneau.coords)
            x, z = c[:, 0], c[:, 1] - zc
            cross = x[:-1] * z[1:] - x[1:] * z[:-1]
            ixx = np.sum(cross * (z[:-1] ** 2 + z[:-1] * z[1:] + z[1:] ** 2)) / 12
            I += signe * abs(ixx)
    return I


# ---------------------------------------------------------------------------
# Essais
# ---------------------------------------------------------------------------
def main():
    m_imp, _ = D.imprime()
    m_comp = sum(q * m for _, q, m, _ in D.COMPOSANTS)
    m_bat = list(D.BATTERIES.values())[0][0]
    m = (m_imp + m_comp + m_bat) / 1000
    W = m * G
    S = CORDE * ENVERGURE / 1e6
    AR = ENVERGURE / CORDE
    c = CORDE / 1000
    s = ENVERGURE / 2000
    a_w = 2 * math.pi * AR / (2 + math.sqrt(4 + AR ** 2))
    vs = math.sqrt(2 * W / (RHO * S * D.CL_MAX))
    q = lambda v: 0.5 * RHO * v * v  # noqa: E731
    lignes, verdicts = [], []
    p = lignes.append

    def verdict(ok, txt, attention=False):
        verdicts.append(("✅" if ok else ("⚠️" if attention else "❌")) + " " + txt)

    titre = "Huard DFR" if VERSION == "dfr" else "Huard Mini"
    suf = "" if VERSION == "dfr" else f"_{VERSION}"

    # --- facteurs de charge ------------------------------------------------
    ws = W / S
    mu = 2 * ws / (RHO * c * a_w * G)
    kg = 0.88 * mu / (5.3 + mu)
    n_rafale = 1 + RHO * RAFALE * V_CROISIERE * a_w * kg / (2 * ws)
    n_lim = max(N_MANOEUVRE, n_rafale)
    n_ult = SECURITE * n_lim
    va = vs * math.sqrt(n_lim)

    # --- 1. pression ---------------------------------------------------------
    cas = []
    cl_crois = W / (q(V_CROISIERE) * S)
    cas.append((f"Croisière {V_CROISIERE * 3.6:.0f} km/h (1 g)", V_CROISIERE, cl_crois))
    cas.append((f"Ressource à {va * 3.6:.0f} km/h ({n_lim:.1f} g, portance max)", va, D.CL_MAX))
    cl_plong = min(n_lim * W / (q(V_PLONGEE) * S), D.CL_MAX)
    cas.append((f"Ressource à {V_PLONGEE * 3.6:.0f} km/h ({n_lim:.1f} g)", V_PLONGEE, cl_plong))
    res_p = []
    for nom, v, cl in cas:
        # portance 3D -> 2D (allongement) puis incidence du profil seul
        al = alpha_pour_cl(PROFIL_AILE, cl * 1.05)
        xc, cp, ext, cl2, cm2 = panneaux(PROFIL_AILE, al)
        res_p.append((nom, v, cl, al, xc, cp, ext, cm2))

    # peau entre appuis : flexion sous la pression la plus forte du panneau
    t = PEAU
    Dp = PLA_AERO["E"] * t ** 3 / (12 * (1 - PLA_AERO["nu"] ** 2))
    pire_p = (0, None)
    for i_s, (ya, yb) in enumerate(P.bornes_segments()):
        haut, bas, _ = appuis_peau(i_s)
        for nom, v, cl, al, xc, cp, ext, _ in res_p:
            for appuis, face in ((haut, ext), (bas, ~ext)):
                for x0, x1 in zip(appuis, appuis[1:]):
                    sel = face & (xc * CORDE >= x0) & (xc * CORDE <= x1)
                    if not sel.any():
                        continue
                    pr = q(v) * np.abs(cp[sel]).max() * 1e-6       # MPa
                    b = x1 - x0
                    sig = pr * b * b / (2 * t * t)
                    w = pr * b ** 4 / (384 * Dp)
                    if sig > pire_p[0]:
                        pire_p = (sig, dict(cas=nom, b=b, p=pr * 1e6, w=w, seg=(ya, yb)))

    # --- 3. flexion de l'aile ---------------------------------------------
    ys = np.linspace(0, s, 400)
    eta = ys / s

    def moment(y, n):
        L = n * W
        lp = (L / 2) / s * 0.5 * (1 + 4 / math.pi * np.sqrt(np.clip(1 - eta ** 2, 0, 1)))
        sel = ys >= y
        return np.trapezoid(lp[sel] * (ys[sel] - y), ys[sel])           # N.m

    y_rac = DEMI_LARGEUR_FUS / 1000
    y_ext0, y_pr1 = LONGERON_EXT_DEBUT / 1000, LONGERON_PRINC_FIN / 1000
    I_pr = tube_I(LONGERON_PRINC_D)
    I_ext = tube_I(LONGERON_EXT_D)
    M_rac = moment(y_rac, n_ult)
    M_ext = moment(y_pr1, n_ult)
    sig_pr = M_rac * 1e3 * (LONGERON_PRINC_D / 2) / I_pr
    sig_ext = M_ext * 1e3 * (LONGERON_EXT_D / 2) / I_ext
    # VTOL : poussée max de 2 moteurs ramenée au fuselage par l'aile
    T_mot = D.POUSSEE_MAX_MOTEUR * G
    M_vtol = (2 * T_mot - 0) * (POUTRE_Y - DEMI_LARGEUR_FUS) / 1000 * SECURITE
    sig_vtol = M_vtol * 1e3 * (LONGERON_PRINC_D / 2) / I_pr
    # flèche en bout d'aile à 1 g (longerons seuls)
    EI_pr, EI_ext = CARBONE_TUBE["E"] * I_pr * 1e-6, CARBONE_TUBE["E"] * I_ext * 1e-6   # N.m²
    yy = ys[ys >= y_rac]
    kap = np.array([moment(y, 1.0) / (EI_pr if y < y_pr1 else EI_ext) for y in yy])
    pente = np.concatenate([[0], np.cumsum((kap[1:] + kap[:-1]) / 2 * np.diff(yy))])
    fleche = np.trapezoid(pente, yy) * 1000

    # peau d'extrados entraînée par la flexion : contrainte et voilement, segment par segment
    nu = PLA_AERO["nu"]
    voile = []
    for i_s, (ya, yb) in enumerate(P.bornes_segments()):
        tubes = P._tubes_aile(ya, yb)
        EI_c = sum(CARBONE_TUBE["E"] * tube_I(d) for _, d in tubes if d >= LONGERON_EXT_D)
        I_peau = section_I_peau(i_s)
        EI_tot = EI_c + PLA_AERO["E"] * I_peau          # N.mm²
        xl = LONGERON_PRINC_X if ya < LONGERON_PRINC_FIN else LONGERON_EXT_X
        z_max = max(surfaces(PROFIL_AILE, CORDE, x)[0] for x in np.linspace(0.1, 0.6, 30)) - \
            P.naca_cambrure(PROFIL_AILE, xl) * CORDE
        y0 = max(ya, DEMI_LARGEUR_FUS) / 1000
        sig1 = PLA_AERO["E"] * moment(y0, 1.0) * 1e3 / EI_tot * z_max
        haut, _, _ = appuis_peau(i_s)
        b_max, x_b = max((x1 - x0, (x0 + x1) / 2) for x0, x1 in zip(haut, haut[1:]))
        R = courbure_extrados(PROFIL_AILE, CORDE, x_b / CORDE)
        scr = 4 * math.pi ** 2 * PLA_AERO["E"] / (12 * (1 - nu ** 2)) * (PEAU / b_max) ** 2 + \
            0.18 * PLA_AERO["E"] * PEAU / R
        voile.append(dict(seg=i_s + 1, ames=P.ames_segment(i_s), b=b_max, R=R, sig1=sig1, scr=scr,
                          n=scr / sig1, part=PLA_AERO["E"] * I_peau / EI_tot))
    n_voile = min(v["n"] for v in voile)

    # transfert longeron extérieur -> principal (zone de recouvrement)
    L_rec = (LONGERON_PRINC_FIN - LONGERON_EXT_DEBUT)
    F_tr = M_ext * 1e3 / L_rec * 2          # N, couple de forces aux deux bouts
    colle = F_tr / (math.pi * LONGERON_EXT_D * 20)       # MPa, 20 mm de collage efficace par bout
    portee = F_tr / (LONGERON_EXT_D * 15)                 # MPa, appui du tube sur 15 mm de fourreau

    # --- 4. torsion -----------------------------------------------------------
    cm_tot = abs(CM_AC) + 0.10       # + aileron braqué
    T_dem = q(V_PLONGEE) * c * c * cm_tot * (s - y_rac) * SECURITE      # N.m, à l'emplanture
    A_cell = 0.685 * 0.12 * CORDE ** 2 * 0.8      # mm², partie fixe (sans l'aileron)
    perim = 2.03 * CORDE * 0.8
    tau_peau = T_dem * 1e3 / (2 * A_cell * PEAU)
    F_goup = T_dem * 1e3 / ((GOUPILLE_X - LONGERON_PRINC_X) * CORDE)
    tau_goup = F_goup / (math.pi * GOUPILLE_D ** 2 / 4)
    portee_goup = F_goup / (GOUPILLE_D * (PAROI_FUS + 4.0))
    GJ = 4 * A_cell ** 2 * PLA_AERO["G"] / (perim / PEAU) * 1e-6      # N.m²
    th_f = math.acos(1 - 2 * (1 - AILERON_X))
    cl_d = 2 * (math.pi - th_f + math.sin(th_f))
    cm_d = -0.5 * math.sin(th_f) * (1 - math.cos(th_f))
    L_ail = s - y_rac
    q_inv = math.pi ** 2 * GJ / (4 * L_ail ** 2) * cl_d / (c * c * 2 * math.pi * abs(cm_d))
    v_inv = math.sqrt(2 * q_inv / RHO)
    e_ax = 0.12 * c            # foyer (25 %) devant l'axe élastique (~37 %)
    q_div = math.pi ** 2 * GJ / (4 * L_ail ** 2 * c * e_ax * 2 * math.pi)
    v_div = math.sqrt(2 * q_div / RHO)

    # --- 6. stabilité -----------------------------------------------------
    S_t = 2 * STAB_DEMI_ENV * STAB_CORDE / 1e6
    AR_t = 2 * STAB_DEMI_ENV / STAB_CORDE * 1.2       # dérives en bout : effet de plaque
    a_t = 2 * math.pi * AR_t / (2 + math.sqrt(4 + AR_t ** 2))
    deps = 2 * a_w / (math.pi * AR)
    x_acw = 0.25 * CORDE
    x_act = STAB_BA_X + 0.25 * STAB_CORDE
    l_t = (x_act - CG_X) / 1000
    eta_t = 0.9
    V_H = S_t * l_t / (S * c)
    w_f = max(sec[1] for sec in SECTIONS_FUS) / 1000
    L_f = (SECTIONS_FUS[-1][0] - SECTIONS_FUS[0][0]) / 1000
    dcm_fus = K_FUS * w_f ** 2 * L_f / (c * S) * 180 / math.pi       # par radian
    num = a_w * x_acw / CORDE + eta_t * a_t * (S_t / S) * (1 - deps) * x_act / CORDE - dcm_fus
    den = a_w + eta_t * a_t * (S_t / S) * (1 - deps)
    x_np = num / den * CORDE
    marge = (x_np - CG_X) / CORDE
    S_v = 2 * (DERIVE_CORDE_PIED + DERIVE_CORDE_SAUMON) / 2 * DERIVE_HAUTEUR / 1e6
    l_v = (DERIVE_BA_X + 0.3 * DERIVE_CORDE_PIED - CG_X) / 1000
    V_V = S_v * l_v / (S * ENVERGURE / 1000)

    def braquage(v, n=1.0):
        L = n * W
        M_ac = q(v) * S * c * CM_AC
        Lt = (L * (CG_X - x_acw) / 1000 + M_ac) / l_t
        Lw = L - Lt
        clw = Lw / (q(v) * S)
        a_w_deg = clw / a_w + math.radians(-4.0)            # incidence absolue -> géométrique
        a_corps = a_w_deg - math.radians(CALAGE_AILE)
        eps = 2 * clw / (math.pi * AR)
        a_queue = a_corps - eps
        clt = Lt / (q(v) * S_t * eta_t)
        return math.degrees((clt / a_t - a_queue) / TAU_PROF), math.degrees(a_corps)
    trims = [(f"{v * 3.6:.0f} km/h", *braquage(v)) for v in (1.3 * vs, V_CROISIERE, V_MAX)]
    trim_ressource = braquage(va, n_lim)

    # --- 7. servos ----------------------------------------------------------
    def servo(code, corde, xh, envergure, haut):
        """Couple au servo, comme la norme : plein braquage à la vitesse de manœuvre, un tiers du
        braquage à la vitesse de piqué. Trou du palonnier choisi pour obtenir le braquage."""
        cf = (1 - xh) * corde / 1000
        zh, zl = P.naca_surfaces(code, corde, xh)
        bras = (zh - zl) + 0.55 * haut                    # mm, charnière -> trou intérieur du guignol
        palonnier = bras * math.sin(math.radians(DEBATTEMENT)) / math.sin(math.radians(COURSE_SERVO))
        H = max(abs(CH_DELTA * math.radians(d) + CH_ALPHA * math.radians(4)) * q(v) * cf * cf * envergure / 1000
                for v, d in ((va, DEBATTEMENT), (V_PLONGEE, DEBATTEMENT / 3)))   # N.m
        couple_servo = H * palonnier / bras / G * 100                # kg.cm
        return H, bras, couple_servo, couple_servo / SERVO_COUPLE, palonnier
    ail = servo(PROFIL_AILE, CORDE, AILERON_X, AILERON_FIN - AILERON_DEBUT, GUIGNOL_HAUT * CORDE)
    prof = servo(STAB_PROFIL, STAB_CORDE, PROFONDEUR_X, 2 * STAB_DEMI_ENV, GUIGNOL_HAUT * 2 * STAB_CORDE)

    # --- 8. poutres -----------------------------------------------------------
    k_pyl = CORDE / 220.0
    x_pyl0, x_pyl1 = 0.0, 204 * k_pyl
    bras_av = (x_pyl0 - P.X_MOT_AV) / 1000
    bras_ar = (P.X_MOT_AR - x_pyl1) / 1000
    I_p = tube_I(POUTRE_D)
    M_p = T_mot * max(bras_av, bras_ar) * SECURITE
    sig_p = M_p * 1e3 * (POUTRE_D / 2) / I_p
    l_b = max(bras_av, bras_ar) * 1000
    fl_p = T_mot * l_b ** 3 / (3 * CARBONE_TUBE["E"] * I_p)
    k_b = 3 * CARBONE_TUBE["E"] * I_p / l_b ** 3 * 1000                    # N/m
    f_b = math.sqrt(k_b / MASSE_POD) / (2 * math.pi)
    tr_resonance = f_b * 60
    tr_max = KV * TENSION * 0.8
    tr_stat = tr_max * math.sqrt(1 / (4 * D.POUSSEE_MAX_MOTEUR / m))      # poussée ~ tr²
    # atterrissage dur sur les pattes (posées sur les poutres)
    a_choc = V_ATTERRISSAGE_DUR ** 2 / (2 * COURSE_PATTE / 1000) + G
    F_patte = m * a_choc / 4
    bras_patte = max(x_pyl0 - P.X_PATTE_AV, P.X_PATTE_AR - x_pyl1) / 1000
    sig_patte = F_patte * bras_patte * 1e3 * (POUTRE_D / 2) / I_p

    # ======================================================================
    # Rapport
    # ======================================================================
    verdict(sig_pr < CARBONE_TUBE["sigma"],
            f"longeron principal Ø{LONGERON_PRINC_D:g} à {n_ult:.1f} g (charge extrême) : "
            f"{sig_pr:.0f} MPa pour {CARBONE_TUBE['sigma']:.0f} admissibles")
    verdict(sig_ext < CARBONE_TUBE["sigma"],
            f"longeron extérieur Ø{LONGERON_EXT_D:g} : {sig_ext:.0f} MPa pour {CARBONE_TUBE['sigma']:.0f}")
    verdict(sig_vtol < CARBONE_TUBE["sigma"],
            f"aile en VTOL plein gaz : {sig_vtol:.0f} MPa dans le longeron principal")
    verdict(sig_p < CARBONE_TUBE["sigma"],
            f"poutres en VTOL plein gaz : {sig_p:.0f} MPa, flèche {fl_p:.1f} mm")
    verdict(sig_patte < CARBONE_TUBE["sigma"],
            f"atterrissage dur à {V_ATTERRISSAGE_DUR:g} m/s : {sig_patte:.0f} MPa dans les poutres "
            f"({a_choc / G:.0f} g d'impact si les pattes s'écrasent de {COURSE_PATTE:g} mm)")
    verdict(pire_p[0] < PLA_AERO["sigma"],
            f"peau sous la pression de l'air : {pire_p[0]:.1f} MPa au pire panneau pour "
            f"{PLA_AERO['sigma']:g} MPa (flèche {pire_p[1]['w']:.2f} mm)")
    verdict(n_voile > n_lim, f"peau d'extrados comprimée par la flexion : elle n'ondule pas avant "
            f"{n_voile:.1f} g (charge limite {n_lim:.1f} g)" if n_voile > n_lim else
            f"peau d'extrados : elle commence à onduler vers {n_voile:.1f} g, sous la charge limite "
            f"{n_lim:.1f} g (les tubes portent la charge, mais la peau peut fissurer à la longue)",
            attention=n_voile > 2.5)
    verdict(tau_peau < PLA_AERO["tau"] and tau_goup < CARBONE_JONC["tau"] and portee_goup < PLA_AERO["sigma"],
            f"torsion à {V_PLONGEE * 3.6:.0f} km/h : peau {tau_peau:.2f} MPa, goupille {tau_goup:.0f} MPa, "
            f"appui de la goupille dans le fuselage {portee_goup:.1f} MPa")
    verdict(colle < 5 and portee < PLA_AERO["sigma"],
            f"relais des longerons (recouvrement de {L_rec:.0f} mm) : colle {colle:.2f} MPa, "
            f"appui dans le fourreau {portee:.1f} MPa")
    verdict(v_inv > 1.2 * V_PLONGEE and v_div > 1.2 * V_PLONGEE,
            f"inversion des ailerons vers {v_inv * 3.6:.0f} km/h, divergence vers {v_div * 3.6:.0f} km/h "
            f"(il faut plus de 1,2 × {V_PLONGEE * 3.6:.0f} = {1.2 * V_PLONGEE * 3.6:.0f} km/h)")
    verdict(0.05 <= marge <= 0.20, f"marge statique {marge:.0%} (bien entre 5 et 20 %) : point neutre "
            f"à {x_np:.0f} mm, centre de gravité à {CG_X:.0f} mm" if marge <= 0.20 else
            f"marge statique {marge:.0%} : très stable (un peu lourd du nez à piloter, pas dangereux). "
            f"Le centre de gravité reste à {CG_X:.0f} mm, au milieu des moteurs VTOL, pour le vol stationnaire",
            attention=marge > 0.20)
    verdict(0.35 <= V_H <= 0.8, f"volume d'empennage horizontal {V_H:.2f} (habituel 0,35 à 0,6)")
    verdict(V_V >= 0.02, f"volume d'empennage vertical {V_V:.3f} (habituel 0,02 à 0,04)")
    pire_trim = max(abs(t[1]) for t in trims + [("", *trim_ressource)])
    verdict(pire_trim < 15, f"braquage de profondeur pour équilibrer : au plus {pire_trim:.0f}° "
            f"sur ±25° disponibles")
    pire_servo = max(ail[3], prof[3])
    verdict(pire_servo < 0.5,
            f"servos (±{DEBATTEMENT:g}° à {va * 3.6:.0f} km/h, ±{DEBATTEMENT / 3:.0f}° à {V_PLONGEE * 3.6:.0f} km/h) : "
            f"aileron {ail[2]:.2f} kg·cm, profondeur {prof[2]:.2f} kg·cm, pour {SERVO_COUPLE:g} kg·cm "
            f"({pire_servo:.0%} ; à garder sous 50 %)", attention=pire_servo < 0.75)
    verdict(not (0.6 * tr_stat < tr_resonance < 1.2 * tr_stat),
            f"résonance des poutres à {f_b:.0f} Hz ({tr_resonance:.0f} tr/min) ; moteurs ≈ {tr_stat:.0f} tr/min "
            f"en stationnaire : on ne fait que la traverser en montant les gaz", attention=True)

    p(f"# Essais virtuels — {titre}\n")
    p("Généré par `calc/essais_virtuels.py`. Ce sont des calculs d'ingénieur classiques de "
      "pré-dimensionnement, faits sur les cotes réelles du modèle. Ils disent si la conception tient, "
      "avec quelle marge, et où sont les points faibles. Ils ne remplacent pas les essais au sol "
      "(test de charge de l'aile, voir plus bas) ni les premiers vols prudents.\n")
    p(f"Masse au décollage {m:.2f} kg, surface alaire {S:.3f} m², charge alaire {ws / G:.1f} kg/m², "
      f"décrochage {vs * 3.6:.0f} km/h, vitesse max réglée dans ArduPilot {V_MAX * 3.6:.0f} km/h, "
      f"vitesse de calcul en piqué {V_PLONGEE * 3.6:.0f} km/h.\n")
    p("## Résumé\n")
    lignes.extend(verdicts)
    p("\n✅ tient avec marge · ⚠️ à connaître (pas dangereux) · ❌ à corriger\n")

    p("## 1. Pression de l'air sur l'aile\n")
    p(f"Méthode des panneaux sur le profil NACA {PROFIL_AILE} (Cp = 1 − (V/V∞)²). "
      f"Dépression = Cp négatif, sur le dessus. Image : `docs/images/pression_aile{suf}.png`.\n")
    p("| Cas | Vitesse | CL | Incidence du profil | Dépression max (bord d'attaque) |")
    p("|---|---:|---:|---:|---:|")
    for nom, v, cl, al, xc, cp, ext, cm2 in res_p:
        p(f"| {nom} | {v * 3.6:.0f} km/h | {cl:.2f} | {al:.1f}° | {q(v) * -cp.min():.0f} Pa "
          f"({-cp.min() * q(v) / 1000 * 100:.1f} g/cm²) |")
    d = pire_p[1]
    p(f"\nPeau de {PEAU:g} mm entre deux âmes : le pire panneau fait {d['b']:.0f} mm de large "
      f"({d['cas']}, segment {d['seg'][0]:.0f}–{d['seg'][1]:.0f} mm). Sous {d['p']:.0f} Pa il fléchit de "
      f"{d['w']:.2f} mm et travaille à {pire_p[0]:.2f} MPa, pour environ {PLA_AERO['sigma']:g} MPa de "
      "résistance : la peau ne se creuse pas visiblement.\n")

    p("## 2. Charges de vol\n")
    p(f"- Manœuvre : {N_MANOEUVRE:g} g (catégorie normale). Rafale verticale de {RAFALE:g} m/s à "
      f"{V_CROISIERE * 3.6:.0f} km/h : **{n_rafale:.1f} g** (formule de Pratt ; un petit avion léger "
      "est très secoué par les rafales).")
    p(f"- Charge limite retenue **{n_lim:.1f} g**, charge extrême ({SECURITE:g} ×) **{n_ult:.1f} g**.")
    p(f"- Vitesse de manœuvre (décroche avant de casser) : {va * 3.6:.0f} km/h.\n")

    p("## 3. Flexion de l'aile\n")
    p(f"Répartition de portance de Schrenk. Image : `docs/images/flexion_aile{suf}.png`.\n")
    p("| Endroit | Moment à charge extrême | Tube | Contrainte | Admissible |")
    p("|---|---:|---|---:|---:|")
    p(f"| Emplanture (y = {DEMI_LARGEUR_FUS:.0f} mm) | {M_rac:.1f} N·m | Ø{LONGERON_PRINC_D:g} × 1 mm | "
      f"{sig_pr:.0f} MPa | {CARBONE_TUBE['sigma']:.0f} MPa |")
    p(f"| Fin du longeron principal (y = {LONGERON_PRINC_FIN:.0f} mm) | {M_ext:.1f} N·m | "
      f"Ø{LONGERON_EXT_D:g} × 1 mm | {sig_ext:.0f} MPa | {CARBONE_TUBE['sigma']:.0f} MPa |")
    p(f"| Emplanture en VTOL plein gaz | {M_vtol:.1f} N·m | Ø{LONGERON_PRINC_D:g} × 1 mm | {sig_vtol:.0f} MPa | "
      f"{CARBONE_TUBE['sigma']:.0f} MPa |")
    p(f"\nFlèche en bout d'aile en vol normal (1 g) : **{fleche:.0f} mm** (longerons seuls ; la peau "
      "raidit un peu).\n")
    p("**La peau suit la flexion.** Collée aux longerons par les âmes, la coque imprimée porte une "
      "partie de la flexion : l'extrados est comprimé. Une peau mince et large entre deux âmes ondule "
      "(voilement) quand la compression dépasse sa limite. Ce n'est pas une rupture (les tubes portent "
      "la charge), mais à répétition la peau peut fissurer. On veut donc que ça n'arrive pas avant la "
      "charge limite.\n")
    p("| Segment | Diagonales | Panneau le plus large | Part de la peau dans la raideur | "
      "Compression à 1 g | Limite d'ondulation | Ondule à partir de |")
    p("|---:|---:|---:|---:|---:|---:|---:|")
    for v in voile:
        p(f"| {v['seg']} | {v['ames']} | {v['b']:.0f} mm | {v['part']:.0%} | {v['sig1']:.2f} MPa | "
          f"{v['scr']:.2f} MPa | **{v['n']:.1f} g** |")
    p("")
    p(f"Relais entre les longerons (recouvrement de {L_rec:.0f} mm) : le tube extérieur pousse sur son "
      f"fourreau avec ≈ {F_tr:.0f} N à charge extrême, soit {portee:.1f} MPa d'appui sur le PLA Aero et "
      f"{colle:.2f} MPa dans la colle époxy (elle tient 10 à 20 MPa).\n")

    p("## 4. Torsion, goupille, inversion d'ailerons\n")
    p(f"- Couple de torsion à l'emplanture ({V_PLONGEE * 3.6:.0f} km/h, aileron braqué, × {SECURITE:g}) : "
      f"{T_dem:.2f} N·m.")
    p(f"- Cisaillement dans la peau : {tau_peau:.2f} MPa (≈ {PLA_AERO['tau']:g} admissibles).")
    p(f"- Goupille Ø{GOUPILLE_D:g} : effort {F_goup:.0f} N, cisaillement {tau_goup:.0f} MPa, appui dans le "
      f"bossage du fuselage {portee_goup:.1f} MPa.")
    p(f"- Raideur en torsion de l'aile (coque seule) : GJ ≈ {GJ:.0f} N·m². Les ailerons s'inverseraient "
      f"vers **{v_inv * 3.6:.0f} km/h** et l'aile divergerait vers **{v_div * 3.6:.0f} km/h** : loin "
      "au-dessus de ce que l'avion peut faire.\n")

    p("## 5. Stabilité et équilibre\n")
    p(f"- Point neutre à **{x_np:.0f} mm** du bord d'attaque ({x_np / CORDE:.0%} de corde), centre de "
      f"gravité à {CG_X:.0f} mm : **marge statique {marge:.0%}**. Un avion se pilote bien entre 5 et 15 %.")
    p(f"- Volume d'empennage horizontal {V_H:.2f}, vertical {V_V:.3f}.")
    p(f"- Effet du fuselage pris en compte (Raymer) ; descente du flux de l'aile sur le stab "
      f"dε/dα = {deps:.2f}.\n")
    p("| Vol en palier | Braquage de profondeur pour équilibrer | Assiette du fuselage |")
    p("|---|---:|---:|")
    for nom, d_, a_ in trims:
        p(f"| {nom} | {d_:+.1f}° | {a_:+.1f}° |")
    p(f"| Ressource {n_lim:.1f} g à {va * 3.6:.0f} km/h | {trim_ressource[0]:+.1f}° | |")
    p("\n(+ = bord de fuite de la profondeur vers le bas.) La profondeur garde de la réserve sur ses "
      "±25°. ArduPilot règle le reste tout seul (TRIM_PITCH_DEG, autotune).\n")

    p("## 6. Servos et débattements\n")
    p(f"Comme la norme des avions légers : plein braquage (±{DEBATTEMENT:g}°) à la vitesse de manœuvre "
      f"({va * 3.6:.0f} km/h), un tiers du braquage à la vitesse de piqué ({V_PLONGEE * 3.6:.0f} km/h). "
      f"Servo qui tourne de ±{COURSE_SERVO:g}°.\n")
    p("| Gouverne | Moment de charnière | Bras du guignol (trou intérieur) | Trou du palonnier pour "
      f"±{DEBATTEMENT:g}° | Couple au servo | Servo |")
    p("|---|---:|---:|---:|---:|---:|")
    for nom, r in (("Aileron (chacun)", ail), ("Profondeur (les deux)", prof)):
        p(f"| {nom} | {r[0] * 100:.1f} N·cm | {r[1]:.0f} mm | **{r[4]:.0f} mm** de l'axe | {r[2]:.2f} kg·cm | "
          f"{r[3]:.0%} de {SERVO_COUPLE:g} kg·cm |")
    p(f"\nRégler les fins de course dans ArduPilot (SERVOx_MIN / MAX) pour ±{DEBATTEMENT:g}° de gouverne, "
      "mesurés au rapporteur. Plus de débattement n'apporte rien à cet avion et charge les servos.\n")
    p("## 7. Poutres, vibrations, atterrissage\n")
    p(f"- Plein gaz en stationnaire ({D.POUSSEE_MAX_MOTEUR:g} kg par moteur, × {SECURITE:g}) : "
      f"{sig_p:.0f} MPa dans la poutre, flèche {fl_p:.1f} mm au moteur.")
    p(f"- Fréquence propre d'une poutre avec son moteur : **{f_b:.0f} Hz** ({tr_resonance:.0f} tr/min). "
      f"En stationnaire les moteurs tournent vers {tr_stat:.0f} tr/min : on ne fait que traverser la "
      "résonance en montant les gaz. Équilibrer les hélices et activer le filtre anti-vibration "
      "d'ArduPilot (INS_HNTCH_*) après le premier vol.")
    p(f"- Atterrissage dur à {V_ATTERRISSAGE_DUR:g} m/s (4 fois la vitesse normale) : si les pattes TPU "
      f"s'écrasent de {COURSE_PATTE:g} mm, l'impact fait {a_choc / G:.0f} g, {F_patte:.0f} N par patte, "
      f"{sig_patte:.0f} MPa dans les poutres.\n")

    p("## Ce qu'il faut vérifier en vrai\n")
    p(f"1. **Test de charge de l'aile au sol** (le plus important) : aile montée sur le fuselage, posée "
      f"à l'envers sur deux tréteaux sous le fuselage, répartir des sacs de sable sur l'intrados. "
      f"{n_lim:.1f} g, c'est {n_lim * m:.1f} kg en tout, dont 60 % sur la moitié intérieure de chaque "
      "aile. Monter par paliers ; l'aile doit revenir droite. Ne pas aller jusqu'à la charge extrême.")
    p("2. **Les servos** : avec l'avion branché, pousser une gouverne au doigt : elle ne doit pas "
      "bouger, et le servo ne doit pas grogner au neutre.")
    p("3. **Le centrage** : soulever l'avion du bout des doigts sous l'aile au point de centrage "
      f"({CG_X:.0f} mm du bord d'attaque) : il doit rester à plat ou piquer très légèrement du nez.")
    p("4. **Les vibrations** : premier vol stationnaire, puis lire le log (VIBE) dans Mission Planner.\n")
    p("## Hypothèses\n")
    p(f"- PLA Aero moussé : module {PLA_AERO['E']:.0f} MPa, résistance {PLA_AERO['sigma']:g} MPa, "
      f"cisaillement {PLA_AERO['tau']:g} MPa (valeurs prudentes, non mesurées).")
    p(f"- Tubes carbone roulés : module {CARBONE_TUBE['E'] / 1000:.0f} GPa, {CARBONE_TUBE['sigma']:.0f} MPa "
      "admissibles en flexion (les tubes du commerce tiennent 600 à 1000 MPa) ; épaisseur 1 mm.")
    p(f"- Servo {SERVO_COUPLE:g} kg·cm à 4,8 V (fiche technique), à garder sous 50 % en continu. Moment de charnière : coefficients "
      "habituels d'une gouverne simple ; peau de gouverne étanche (ruban).")
    p("- Méthode des panneaux sans viscosité : elle surestime un peu la dépression (côté sûr).")
    p(f"- Poussée max d'un moteur VTOL : {D.POUSSEE_MAX_MOTEUR:g} kg (même valeur que le bilan).\n")

    with open(os.path.join(RACINE, "docs", f"essais_virtuels{suf}.md"), "w") as f:
        f.write("\n".join(lignes))
    print("\n".join(verdicts))
    images(res_p, ys, y_rac, n_lim, n_ult, moment, I_pr, I_ext, suf, titre)


def images(res_p, ys, y_rac, n_lim, n_ult, moment, I_pr, I_ext, suf, titre):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    bleu, orange, gris, encre, encre2 = "#2a78d6", "#eb6834", "#8a8984", "#0b0b0b", "#52514e"
    plt.rcParams.update({"font.size": 11, "axes.edgecolor": gris, "axes.labelcolor": encre2,
                         "xtick.color": encre2, "ytick.color": encre2})

    # pression
    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=110)
    for (nom, v, cl, al, xc, cp, ext, _), coul in zip(res_p[:2], (bleu, orange)):
        for face, style in ((ext, "-"), (~ext, "--")):
            o = np.argsort(xc[face])
            ax.plot(xc[face][o] * 100, cp[face][o], style, color=coul, lw=2)
        ax.annotate(f"{nom}", xy=(xc[ext][np.argmin(cp[ext])] * 100, cp.min()),
                    xytext=(25, cp.min() + 0.2), color=encre, fontsize=10,
                    arrowprops=dict(arrowstyle="-", color=gris, lw=0.8))
    ax.invert_yaxis()
    ax.axhline(0, color=gris, lw=0.8)
    ax.set_xlabel("Position le long de la corde (% depuis le bord d'attaque)")
    ax.set_ylabel("Coefficient de pression Cp (dépression vers le haut)")
    ax.set_title(f"Pression sur le profil NACA {PROFIL_AILE} — {titre}\n"
                 "trait plein : dessus de l'aile · tirets : dessous", color=encre, fontsize=12)
    ax.grid(color="#e4e3df", lw=0.6)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    fig.tight_layout()
    fig.savefig(os.path.join(RACINE, "docs", "images", f"pression_aile{suf}.png"))
    plt.close(fig)

    # flexion
    yy = ys[ys >= y_rac]
    M = np.array([moment(y, n_ult) for y in yy])
    cap = np.array([CARBONE_TUBE["sigma"] * (I_pr / (LONGERON_PRINC_D / 2) if y * 1000 < LONGERON_PRINC_FIN
                                              else I_ext / (LONGERON_EXT_D / 2)) / 1000 for y in yy])
    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=110)
    ax.plot(yy * 1000, cap, color=gris, lw=2)
    ax.plot(yy * 1000, M, color=bleu, lw=2)
    ax.fill_between(yy * 1000, M, cap, where=cap > M, color=bleu, alpha=0.08, lw=0)
    ax.text(yy[5] * 1000, cap[5] * 1.03, "ce que les tubes carbone supportent", color=encre2, fontsize=10)
    i = len(yy) // 6
    ax.text(yy[i] * 1000, M[i] * 1.1 + 0.3, f"moment de flexion à {n_ult:.1f} g (charge extrême)",
            color=encre, fontsize=10)
    ax.axvline(LONGERON_PRINC_FIN, color=gris, lw=0.8, ls=":")
    ax.text(LONGERON_PRINC_FIN + 5, ax.get_ylim()[1] * 0.9, "fin du longeron principal", color=encre2,
            fontsize=9)
    ax.set_xlabel("Distance depuis le centre de l'avion (mm)")
    ax.set_ylabel("Moment de flexion (N·m)")
    ax.set_title(f"Flexion d'une demi-aile — {titre}", color=encre, fontsize=12)
    ax.grid(color="#e4e3df", lw=0.6)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    fig.tight_layout()
    fig.savefig(os.path.join(RACINE, "docs", "images", f"flexion_aile{suf}.png"))
    plt.close(fig)


if __name__ == "__main__":
    main()
