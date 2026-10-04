"""Paramètres du « Huard Mini » : version d'essai à petit budget (1,2 m, 4S LiPo, hélices 7 po).

Même architecture que le Huard DFR, à l'échelle : on y apprend la construction, les réglages
ArduPilot, les transitions et les missions automatiques avant de bâtir le grand.

Les cotes des composants achetés viennent de leurs fiches techniques (docs/nomenclature_mini.md).

Repère global (mm) : X vers l'arrière depuis le bord d'attaque, Y vers la droite, Z vers le haut.
"""

# --- Imprimante (Bambu Lab A1) ---------------------------------------------
PLATEAU = 256.0
MARGE_PLATEAU = 4.0

# --- Aile ---------------------------------------------------------------------
CORDE = 160.0
ENVERGURE = 1200.0
PROFIL_AILE = "4412"
CALAGE_AILE = 2.5
DEMI_LARGEUR_FUS = 40.0
N_SEGMENTS = 3
PEAU = 0.6
AME = 0.5
N_AMES = 5

# Longerons (tubes carbone)
LONGERON_PRINC_D = 10.0   # tube 10x8 mm, 720 mm, traverse le fuselage
LONGERON_PRINC_X = 0.25
LONGERON_PRINC_FIN = 360.0
LONGERON_EXT_D = 6.0      # tube 6x4 mm, 310 mm par côté
LONGERON_EXT_X = 0.33      # avancé pour laisser la place au servo d'aileron
LONGERON_EXT_DEBUT = 280.0
LONGERON_EXT_FIN = 590.0
GOUPILLE_D = 4.0          # jonc 4 mm, 200 mm
GOUPILLE_X = 0.65
GOUPILLE_FIN = 100.0
JEU_TUBE = 0.3
FOURREAU = 1.2

# Ailerons
AILERON_X = 0.75
AILERON_JEU = 1.0
AILERON_DEBUT = 300.0
AILERON_JONC = (0.80, 2.0)   # jonc carbone dans l'aileron (fraction de corde, Ø)
PEAU_GOUVERNE = 0.8        # peau des ailerons et profondeurs (2 lignes)
GUIGNOL_HAUT = 0.065        # hauteur de la patte du guignol, en fraction de corde
AILERON_FIN = 596.0

# --- Poutres et propulsion VTOL -----------------------------------------------
POUTRE_Y = 210.0          # entraxe des poutres : ±210
POUTRE_D = 12.0           # tube carbone 12x10 mm
POUTRE_Z = -19.0
CG_X = 45.0               # 28 % de corde
MOTEUR_ECART = 225.0
POUTRE_DEBUT = CG_X - MOTEUR_ECART - 18.0
POUTRE_LONG = 610.0       # coupé dans un tube de 1000 mm
HELICE_VTOL = 7 * 25.4
# Emax ECO III 2807 1300KV : Ø34,8 x 34,9 mm, 4 vis M3 en carré de 19 x 19 mm
MOTEUR_VTOL_TROUS = [(9.5, 9.5), (-9.5, 9.5), (-9.5, -9.5), (9.5, -9.5)]
MOTEUR_VTOL_DIAM = 34.8
MOTEUR_VTOL_HAUT = 35.0

# --- Fuselage -----------------------------------------------------------------
PAROI_FUS = 1.0
SECTIONS_FUS = [
    (-300.0, 10.0, 10.0, -15.0),
    (-290.0, 30.0, 30.0, -16.0),
    (-270.0, 58.0, 60.0, -19.0),
    (-235.0, 74.0, 78.0, -22.0),
    (-195.0, 80.0, 86.0, -21.0),
    (165.0, 80.0, 86.0, -21.0),      # pleine section sur toute la corde d'emplanture
    (215.0, 66.0, 68.0, -15.0),
    (250.0, 44.0, 42.0, -7.0),
    (265.0, 38.0, 36.0, -4.0),
]
SUPER_ELLIPSE_N = 3.0
# nez allongé : la batterie doit être loin devant pour équilibrer poutres et empennage
COUPES_FUS = [-300.0, -235.0, -40.0, 160.0, 265.0]
NOMS_TRONCONS_FUS = ["nez", "avant", "milieu", "queue"]
PLATEAU_X = (-230.0, 15.0)
PLATEAU_Z = -52.0
PLATEAU_LARG = 54.0
COMPAGNON_X = (75.0, 150.0)
COMPAGNON_Z = -50.0
COMPAGNON_LARG = 52.0
FC_TROUS = (30.0, 24.0)    # AtomRC F405 NAVI : 50 x 30 x 12 mm, trous Ø3 en 30 x 24 mm
FC_DIMS = (50.0, 30.0, 12.0)
TRAPPE_ACCES_X = (52.0, 150.0)   # trappe sur le dessus du fuselage, au-dessus du contrôleur
TRAPPE_ACCES_DEMI_LARG = 24.0
TRAPPE_ACCES_Z = 15.5
PI5 = False
POUSSEUR_Z = -4.0
# 5e moteur Emax ECO III 2807 1300KV (le même que les moteurs VTOL), hélice Gemfan 7x6E
POUSSEUR_TROUS = [(9.5, 9.5), (-9.5, 9.5), (-9.5, -9.5), (9.5, -9.5)]
POUSSEUR_DIMS = (34.8, 35.0)
HELICE_POUSSEUR = 7 * 25.4

# --- Charge utile -------------------------------------------------------------
NACELLE_X = None          # pas de nacelle : caméra d'action collée sur le dessus pour les essais
NACELLE_Z = None
NACELLE_TROUS = []
BATTERIE = (150.0, 53.0, 30.0)   # CNHL G+Plus 4S 4000 mAh : 147 x 51 x 28 mm + jeu
X_BATTERIE = -147.0       # centre de la batterie pour le centrage (voir docs/bilan_mini.md)

# --- Empennage en H -----------------------------------------------------------
STAB_CORDE = 90.0
STAB_BA_X = 380.0
STAB_PROFIL = "0009"
STAB_Z = POUTRE_Z + 17.0
STAB_DEMI_ENV = POUTRE_Y - (POUTRE_D / 2 + 7)
STAB_N_SEG = 2
PROFONDEUR_X = 0.70
PROFONDEUR_JONC = (0.73, 1.5)
STAB_LONGERON_D = 5.0     # tube 5x3 mm
STAB_LONGERON_X = 0.25
STAB_JONC_D = 2.0
STAB_JONC_X = 0.55
DERIVE_CORDE_PIED = 100.0
DERIVE_CORDE_SAUMON = 65.0
DERIVE_HAUTEUR = 90.0
DERIVE_BA_X = 380.0
BLOC_QUEUE_X0 = 355.0

# --- Atterrisseur -------------------------------------------------------------
PATTE_LONG = 110.0        # sol à -129 mm, 36 mm sous l'hélice propulsive de 7 po
PATTE_SECTION = ((11.0, 7.0), (16.0, 9.0))
PATTE_PIED = (32.0, 18.0)
PATTE_DECALAGE = 31.0

# --- Servos 9-12 g (cotes courantes : à vérifier au pied à coulisse sur tes servos) ---
SERVO = dict(
    L=23.2,           # longueur du boîtier
    W=12.0,           # épaisseur
    H=24.8,           # hauteur du boîtier (fond -> dessus, sans l'axe)
    oreilles=32.5,    # longueur totale d'une oreille à l'autre
    oreille_ep=2.5,   # épaisseur des oreilles
    oreille_y=16.0,   # distance du fond du boîtier au dessous des oreilles
    entraxe=27.8,     # entraxe des trous des oreilles (vis M2)
    axe=5.9,          # distance de l'axe au bout du boîtier
)
SERVO_TRAPPE_EP = 1.6

# --- Densités (g/cm³) ---------------------------------------------------------
DENSITE = {"PLA Aero": 0.65, "PLA": 1.24, "PETG": 1.27, "TPU 95A": 1.21}
