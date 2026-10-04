"""Paramètres du quadplane « Huard DFR » (drone premier intervenant).

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
AILERON_FIN = 896.0

# --- Poutres (booms) et propulsion VTOL ---------------------------------------
POUTRE_Y = 330.0          # entraxe des poutres : ±330
POUTRE_D = 16.0           # tube carbone 16x14 mm, 1000 mm
POUTRE_Z = -25.0          # axe des poutres
CG_X = 62.0               # centre de gravité visé (28 % de corde)
MOTEUR_ECART = 365.0      # moteurs VTOL à CG_X ± 365
POUTRE_DEBUT = CG_X - MOTEUR_ECART - 22.0   # = -325
POUTRE_LONG = 1000.0
HELICE_VTOL = 13 * 25.4   # 13 pouces

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
COUPES_FUS = [-285.0, -190.0, 45.0, 255.0, 360.0]
PLATEAU_X = (-185.0, 45.0)      # plateau électronique (batterie + contrôleur de vol)
POUSSEUR_Z = -5.0         # axe du moteur propulsif
HELICE_POUSSEUR = 10 * 25.4

# --- Charge utile -------------------------------------------------------------
NACELLE_X = -140.0        # centre de la nacelle caméra sous le fuselage
NACELLE_Z = -96.0         # face de fixation de la nacelle (dessous du support)
BATTERIE = (150.0, 70.0, 68.0)   # 6S3P 21700 : longueur, largeur, hauteur avec emballage

# --- Empennage en H -----------------------------------------------------------
STAB_CORDE = 110.0
STAB_BA_X = 625.0
STAB_PROFIL = "0009"
STAB_Z = -8.0            # au-dessus des poutres, dans le souffle du propulseur
STAB_DEMI_ENV = 315.0     # entre les deux blocs de queue
STAB_N_SEG = 3
PROFONDEUR_X = 0.70
STAB_LONGERON_D = 6.0     # tube 6x4 mm, 700 mm
STAB_LONGERON_X = 0.25
STAB_JONC_D = 3.0         # jonc 3 mm, 700 mm
STAB_JONC_X = 0.55
DERIVE_CORDE_PIED = 140.0
DERIVE_CORDE_SAUMON = 90.0
DERIVE_HAUTEUR = 130.0
DERIVE_BA_X = 625.0

# --- Atterrisseur -------------------------------------------------------------
PATTE_LONG = 180.0        # sol à POUTRE_Z - PATTE_LONG = -205 mm (garde sous la nacelle)

# --- Densités (g/cm³) pour l'estimation de masse ------------------------------
DENSITE = {"PLA Aero": 0.65, "PLA": 1.24, "PETG": 1.27, "TPU 95A": 1.21}
