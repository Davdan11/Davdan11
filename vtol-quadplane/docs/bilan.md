# Bilan de masse, centrage et performances — Huard DFR

Généré par `calc/dimensionnement.py`. Les chiffres aérodynamiques sont des estimations, à recaler avec les logs des premiers vols.

## Masse et position (x depuis le bord d'attaque, vers l'arrière)

| Élément | Qté | Masse unitaire (g) | Total (g) | x (mm) |
|---|---:|---:|---:|---:|
| Pièces imprimées (cad/out/masses.csv) | 1 | 1329 | 1329 | 167 |
| Moteur VTOL 3515 ~400 KV (6S) | 4 | 135 | 540 | 62 |
| Hélice VTOL 13x4.4 (2 CW + 2 CCW) | 4 | 28 | 112 | 62 |
| ESC VTOL 40 A 6S (AM32 / BLHeli_32) | 4 | 30 | 120 | 62 |
| Moteur propulsif 2814 ~700 KV (6S) | 1 | 110 | 110 | 380 |
| Hélice propulsive 10x7E pousseur | 1 | 20 | 20 | 405 |
| ESC propulsif 50 A 6S | 1 | 35 | 35 | 300 |
| Contrôleur de vol Matek H743-WING V3 | 1 | 30 | 30 | 122 |
| GPS + compas Matek M10Q-5883 | 1 | 15 | 15 | 230 |
| Capteur de vitesse Matek ASPD-4525 + Pitot | 1 | 10 | 10 | -225 |
| Récepteur ExpressLRS (pilote de sécurité) | 1 | 5 | 5 | 122 |
| Servo 9 g pignons métal (ailerons) | 2 | 13 | 26 | 121 |
| Servo 9 g pignons métal (profondeur) | 1 | 13 | 13 | 711 |
| Nacelle caméra zoom + thermique | 1 | 300 | 300 | -140 |
| Ordinateur de bord Raspberry Pi 5 + refroidisseur | 1 | 55 | 55 | 190 |
| Modem 4G/LTE + 2 antennes | 1 | 50 | 50 | 200 |
| BEC 5 V 5 A (ordinateur de bord) | 1 | 20 | 20 | 150 |
| Tube carbone 16x14x1000 (poutres) | 2 | 73 | 146 | 175 |
| Tube carbone 12x10x1000 (longeron principal) | 1 | 54 | 54 | 55 |
| Tube carbone 8x6x1000 (longerons extérieurs, coupé en 2) | 1 | 34 | 34 | 88 |
| Jonc carbone 6 mm x 300 (goupille d'aile) | 1 | 13 | 13 | 143 |
| Tube carbone 6x4x700 (longeron du stab) | 1 | 17 | 17 | 652 |
| Joncs carbone 3 mm et 2 mm (stab, gouvernes) | 1 | 15 | 15 | 600 |
| Câblage, connecteurs | 1 | 170 | 170 | 40 |
| Visserie, guignols, colle, ruban | 1 | 70 | 70 | 100 |
| **Sans batterie** | | | **3309** | 120 |

## Centrage

Le centre de gravité doit tomber à **x = 62 mm** (28 % de corde), au milieu des 4 moteurs VTOL. On le règle en déplaçant la batterie sur le plateau.

| Batterie | Centre de la batterie requis | Plage possible | Lest |
|---|---:|---:|---|
| 6S3P 21700 Molicel P45B (13,5 Ah) | x = -85 mm | -110 à -35 mm | aucun |
| 6S2P 21700 Molicel P45B (9 Ah), essais | x = -156 mm | -110 à -35 mm | ≈ 154 g dans le nez |

## Performances estimées

| | 6S3P 21700 Molicel P45B (13,5 Ah) | 6S2P 21700 Molicel P45B (9 Ah), essais |
|---|---:|---:|
| Masse au décollage | 4.61 kg | 4.19 kg |
| Charge alaire | 11.6 kg/m² | 10.6 kg/m² |
| Vitesse de décrochage | 12.0 m/s (43 km/h) | 11.4 m/s (41 km/h) |
| Rapport poussée/poids VTOL | 2.08 | 2.29 |
| Puissance en stationnaire | 706 W (33 A) | 614 W (28 A) |
| Transit à 90 km/h | 389 W | 384 W |
| Vol en cercle au-dessus des lieux | 58 km/h, 155 W | 56 km/h, 137 W |
| Autonomie en cercle seulement | **87 min** | **63 min** |
| Temps sur les lieux, intervention à 5 km | **70 min** (aller 3 min) | **45 min** (aller 3 min) |
| Temps sur les lieux, intervention à 10 km | **53 min** (aller 7 min) | **26 min** (aller 7 min) |
| Temps sur les lieux, intervention à 15 km | **37 min** (aller 10 min) | **7 min** (aller 10 min) |
| Temps sur les lieux, intervention à 20 km | **20 min** (aller 13 min) | hors de portée |

Surface alaire 0.396 m², allongement 8.2. Hypothèses : Cd0 = 0.05, e = 0.8, rendement de propulsion 0.55, figure de mérite VTOL 0.6, 15 W pour l'électronique de bord, 85% de la batterie utilisée (le reste est la réserve), 2 min de vol stationnaire par mission, 2.4 kg de poussée max par moteur VTOL.
