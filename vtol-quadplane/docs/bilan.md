# Bilan de masse et performances

Généré par `calc/dimensionnement.py`. Les chiffres aérodynamiques sont des estimations, à recaler avec les logs des premiers vols.

## Masse

| Élément | Qté | Masse unitaire (g) | Total (g) |
|---|---:|---:|---:|
| Pièces imprimées (cad/out/masses.csv) | 1 | 1226 | 1226 |
| Moteur VTOL 3510 ~700 KV | 4 | 100 | 400 |
| Hélice VTOL 12x4.5 (2 CW + 2 CCW) | 4 | 22 | 88 |
| ESC VTOL 40 A (AM32 / BLHeli_32) | 4 | 25 | 100 |
| Moteur propulsif 2814 ~900 KV | 1 | 110 | 110 |
| Hélice propulsive 10x7E | 1 | 20 | 20 |
| ESC propulsif 40 A | 1 | 30 | 30 |
| Contrôleur de vol Matek H743-WING V3 | 1 | 30 | 30 |
| GPS + compas Matek M10Q-5883 | 1 | 15 | 15 |
| Capteur de vitesse Matek ASPD-4525 + Pitot | 1 | 10 | 10 |
| Récepteur ExpressLRS | 1 | 5 | 5 |
| Radio télémétrie SiK 915 MHz | 1 | 25 | 25 |
| Servo 9 g pignons métal | 3 | 13 | 39 |
| Tube carbone 16x14x1000 (poutres) | 2 | 73 | 146 |
| Tube carbone 12x10x1000 (longeron principal) | 1 | 54 | 54 |
| Tube carbone 8x6x1000 (longerons extérieurs, coupé en 2) | 1 | 34 | 34 |
| Jonc carbone 6 mm x 300 (goupille d'aile) | 1 | 13 | 13 |
| Tube carbone 6x4x700 (longeron du stab) | 1 | 17 | 17 |
| Joncs carbone 3 mm et 2 mm (stab, gouvernes) | 1 | 15 | 15 |
| Câblage, connecteurs, BEC | 1 | 150 | 150 |
| Visserie, guignols, colle, ruban | 1 | 70 | 70 |
| **Sans batterie** | | | **2597** |

## Performances estimées

| | 4S2P 21700 Molicel P45B (9 Ah) | 4S3P 21700 Molicel P45B (13,5 Ah) |
|---|---:|---:|
| Masse au décollage | 3.20 kg | 3.50 kg |
| Charge alaire | 8.1 kg/m² | 8.8 kg/m² |
| Vitesse de décrochage | 10.0 m/s (36 km/h) | 10.4 m/s (38 km/h) |
| Rapport poussée/poids VTOL | 2.00 | 1.83 |
| Puissance en stationnaire | 439 W (30 A) | 501 W (34 A) |
| Vitesse d'autonomie max | 13.5 m/s (49 km/h) | 14.5 m/s (52 km/h) |
| Finesse à cette vitesse | 10.2 | 10.0 |
| Puissance en croisière | 81 W | 96 W |
| Autonomie estimée | **70 min** (~57 km) | **93 min** (~81 km) |

Surface alaire 0.396 m², allongement 8.2. Hypothèses : Cd0 = 0.045, e = 0.8, rendement de propulsion en croisière 0.55, figure de mérite VTOL 0.6, 85% de la batterie utilisée, 2 min de vol stationnaire par vol, 1.6 kg de poussée max par moteur VTOL.

Sensibilité (4S2P) : Cd0 + 0,01 → -8 min ; 100 g de plus → -6 min. La vitesse de croisière est limitée à 1.35 x Vs pour garder une marge au décrochage.
