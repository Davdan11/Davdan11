"""Paramètres du quadplane « Huard DFR » (drone premier intervenant, 1,8 m).

Les cotes des composants achetés viennent de leurs fiches techniques (docs/nomenclature.md).

Repère global (mm) :
  X vers l'arrière, origine au bord d'attaque de l'aile
  Y vers la droite (envergure)
  Z vers le haut, Z = 0 sur la corde d'emplanture au bord d'attaque

Changer une valeur ici puis relancer `python build.py` régénère toutes les pièces.
"""

# --- Imprimante (Bambu Lab A1) ---------------------------------------------
PLATEAU = 256.0           # volume utile 256 x 256 x 256
MARGE_PLATEAU = 4.0       # on garde 4 mm de marge

# --- Aile ---------------------------------------------------------------------
CORDE = 220.0             # corde constante (aile rectangulaire, facile à imprimer)
ENVERGURE = 1800.0
PROFIL_AILE = "4412"      # NACA 4 chiffres (cambré 4 %, épais 12 %)
CALAGE_AILE = 2.5         # incidence de l'aile / fuselage, en degrés
DEMI_LARGEUR_FUS = 55.0   # l'aile commence à Y = ±55 (flancs du fuselage)
N_SEGMENTS = 4            # segments par demi-aile
PEAU = 0.6                # épaisseur du revêtement (1 ligne de PLA Aero)
AME = 0.5                 # épaisseur des âmes internes en zigzag
N_AMES = 6                # nombre de diagonales du zigzag

# Longerons (tubes carbone)
LONGERON_PRINC_D = 12.0   # tube 12x10 mm, 1000 mm, traverse le fuselage
LONGERON_PRINC_X = 0.25   # position en fraction de corde
LONGERON_PRINC_FIN = 500.0  # le tube va de Y = -500 à +500
LONGERON_EXT_D = 8.0      # tube 8x6 mm, 500 mm par côté
LONGERON_EXT_X = 0.40
LONGERON_EXT_DEBUT = 380.0  # de Y = 380 à 880 (120 mm de recouvrement)
LONGERON_EXT_FIN = 880.0
GOUPILLE_D = 6.0          # jonc 6 mm, 300 mm : bloque l'incidence
GOUPILLE_X = 0.65
GOUPILLE_FIN = 150.0
JEU_TUBE = 0.3            # jeu diamétral dans les fourreaux imprimés
FOURREAU = 1.2            # épaisseur des fourreaux autour des tubes

# Ailerons
AILERON_X = 0.75          # charnière à 75 % de corde
AILERON_JEU = 1.0
AILERON_DEBUT = 480.0     # sur les segments 3 et 4
AILERON_JONC = (0.80, 2.0)   # jonc carbone dans l'aileron (fraction de corde, Ø)
PEAU_GOUVERNE = 0.8        # peau des ailerons et profondeurs (2 lignes)
GUIGNOL_HAUT = 0.065        # hauteur de la patte du guignol, en fraction de corde
AILERON_FIN = 896.0

# --- Poutres (booms) et propulsion VTOL ---------------------------------------
POUTRE_Y = 360.0          # entraxe des poutres : ±360 (garde entre hélices VTOL et propulseur)
POUTRE_D = 16.0           # tube carbone 16x14 mm, 1000 mm
POUTRE_Z = -25.0          # axe des poutres
CG_X = 62.0               # centre de gravité visé (28 % de corde)
MOTEUR_ECART = 365.0      # moteurs VTOL à CG_X ± 365
POUTRE_DEBUT = CG_X - MOTEUR_ECART - 22.0   # = -325
POUTRE_LONG = 1000.0
HELICE_VTOL = 15 * 25.4   # 15 pouces (T-Motor P15x5)
# T-Motor MN4014 KV400 : 4 vis M3 sur un cercle de Ø25 mm
MOTEUR_VTOL_TROUS = [(12.5, 0.0), (0.0, 12.5), (-12.5, 0.0), (0.0, -12.5)]
MOTEUR_VTOL_DIAM = 44.7
MOTEUR_VTOL_HAUT = 35.0

# --- Fuselage -----------------------------------------------------------------
PAROI_FUS = 1.0
# (x, largeur, hauteur, z_centre) ; exposant de super-ellipse commun
SECTIONS_FUS = [
    (-285.0, 14.0, 14.0, -20.0),
    (-270.0, 44.0, 44.0, -22.0),
    (-240.0, 82.0, 84.0, -27.0),
    (-190.0, 104.0, 108.0, -31.0),
    (-130.0, 110.0, 118.0, -29.0),
    (225.0, 110.0, 118.0, -29.0),     # pleine section sur toute la corde d'emplanture
    (290.0, 94.0, 96.0, -21.0),
    (340.0, 62.0, 60.0, -9.0),
    (360.0, 52.0, 50.0, -5.0),
]
SUPER_ELLIPSE_N = 3.0
# nez (amovible) | avant | milieu | queue ; chaque tronçon fait au plus 250 mm
COUPES_FUS = [-285.0, -205.0, 35.0, 255.0, 360.0]
NOMS_TRONCONS_FUS = ["nez", "avant", "milieu", "queue"]
PLATEAU_X = (-192.0, 45.0)      # plateau de batterie
PLATEAU_Z = -72.0               # dessus du fond du fuselage, sur 2 plots
PLATEAU_LARG = 80.0
# plateau compagnon : contrôleur de vol (TBS Lucid H7 Wing, 30,5 mm M3) + Raspberry Pi 5
COMPAGNON_X = (100.0, 228.0)
COMPAGNON_Z = -62.0
COMPAGNON_LARG = 70.0
FC_TROUS = (30.5, 30.5)         # entraxe des trous du contrôleur de vol (x, y)
FC_DIMS = (54.0, 36.0, 13.0)
TRAPPE_ACCES_X = (70.0, 215.0)   # trappe sur le dessus du fuselage, au-dessus du contrôleur
TRAPPE_ACCES_DEMI_LARG = 33.0
TRAPPE_ACCES_Z = 20.0           # bas de la découpe (au-dessus des fourreaux de longeron)
PI5 = True                      # entretoises Raspberry Pi 5 (58 x 49 mm)
POUSSEUR_Z = -5.0         # axe du moteur propulsif
# SunnySky X2820 V3 : 4 vis M3 en croix, 19 mm et 25 mm
POUSSEUR_TROUS = [(9.5, 0.0), (-9.5, 0.0), (0.0, 12.5), (0.0, -12.5)]
POUSSEUR_DIMS = (35.0, 42.0)   # diamètre, longueur du moteur
HELICE_POUSSEUR = 10 * 25.4

# --- Charge utile -------------------------------------------------------------
NACELLE_X = -145.0        # centre de la nacelle caméra sous le fuselage (None = pas de nacelle)
NACELLE_Z = -96.0         # face de fixation de la nacelle (dessous du support)
# perçages de nacelle (entraxe x, entraxe y, Ø) : SIYI A8 mini M2.5 et SIYI ZT6 M3
NACELLE_TROUS = [(30.0, 25.0, 2.7), (45.0, 40.0, 3.3)]
BATTERIE = (134.0, 83.0, 67.0)   # GAONENG GNB 6S3P P45B : 130 x 81 x 65 mm + jeu
X_BATTERIE = -122.0       # centre de la batterie pour le centrage (voir docs/bilan.md)

# --- Empennage en H -----------------------------------------------------------
STAB_CORDE = 110.0
STAB_BA_X = 640.0
STAB_PROFIL = "0009"
STAB_Z = -8.0            # au-dessus des poutres, dans le souffle du propulseur
STAB_DEMI_ENV = POUTRE_Y - (POUTRE_D / 2 + 7)   # entre les deux blocs de queue
STAB_N_SEG = 3
PROFONDEUR_X = 0.70
PROFONDEUR_JONC = (0.74, 2.0)     # jonc carbone dans la profondeur (fraction de corde, Ø)
STAB_LONGERON_D = 6.0     # tube 6x4 mm, 700 mm
STAB_LONGERON_X = 0.25
STAB_JONC_D = 3.0         # jonc 3 mm, 700 mm
STAB_JONC_X = 0.55
DERIVE_CORDE_PIED = 140.0
DERIVE_CORDE_SAUMON = 90.0
DERIVE_HAUTEUR = 130.0
DERIVE_BA_X = 640.0
BLOC_QUEUE_X0 = 600.0     # le bloc commence avant la dérive pour bien tenir la poutre

# --- Atterrisseur -------------------------------------------------------------
PATTE_LONG = 222.0        # sol à -247 mm : 20 mm sous la nacelle SIYI ZT6 (131,5 mm de haut)
PATTE_SECTION = ((16.0, 10.0), (24.0, 13.0))   # jambe : bas, haut (x, y)
PATTE_PIED = (44.0, 26.0)
PATTE_DECALAGE = 38.0     # distance patte - moteur le long de la poutre

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

# --- Densités (g/cm³) pour l'estimation de masse ------------------------------
DENSITE = {"PLA Aero": 0.65, "PLA": 1.24, "PETG": 1.27, "TPU 95A": 1.21}
