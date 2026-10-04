# Bilan de masse, centrage et performances — Huard DFR

Généré par `calc/dimensionnement.py`. Les chiffres aérodynamiques sont des estimations, à recaler avec les logs des premiers vols.

## Masse et position (x depuis le bord d'attaque, vers l'arrière)

| Élément | Qté | Masse unitaire (g) | Total (g) | x (mm) |
|---|---:|---:|---:|---:|
| Pièces imprimées (cad/out/masses.csv) | 1 | 1539 | 1539 | 169 |
| Moteur VTOL T-Motor MN4014 KV400 | 4 | 171 | 684 | 62 |
| Hélice VTOL T-Motor P15x5 (2 CW + 2 CCW) | 4 | 22 | 88 | 62 |
| ESC VTOL Holybro Tekko32 F4 45A + condensateur | 4 | 10 | 40 | 62 |
| Moteur propulsif SunnySky X2820 V3 KV570 | 1 | 150 | 150 | 385 |
| Hélice propulsive APC 10x7EP | 1 | 20 | 20 | 420 |
| ESC propulsif Holybro Tekko32 F4 45A | 1 | 10 | 10 | 300 |
| Contrôleur de vol TBS Lucid H7 Wing | 1 | 30 | 30 | 122 |
| GPS + compas Holybro Micro M10 | 1 | 16 | 16 | 230 |
| Capteur de vitesse Matek ASPD-4525 + Pitot | 1 | 10 | 10 | -225 |
| Récepteur RadioMaster RP3 V2 (pilote de sécurité) | 1 | 5 | 5 | 122 |
| Servo EMAX ES08MD II (ailerons) | 2 | 12 | 24 | 121 |
| Servo EMAX ES08MD II (profondeur) | 1 | 12 | 12 | 758 |
| Nacelle SIYI ZT6 avec plaque anti-vibration | 1 | 197 | 197 | -145 |
| Raspberry Pi 5 4 Go + Active Cooler | 1 | 67 | 67 | 190 |
| Modem Waveshare SIM7600G-H (clé USB, sans boîtier) + antennes | 1 | 60 | 60 | 200 |
| BEC Holybro UBEC 5A (Pi et modem) | 2 | 7 | 14 | 150 |
| Tube carbone 16x14x1000 (poutres) | 2 | 73 | 146 | 175 |
| Tube carbone 12x10x1000 (longeron principal) | 1 | 54 | 54 | 55 |
| Tube carbone 8x6x1000 (longerons extérieurs, coupé en 2) | 1 | 34 | 34 | 88 |
| Jonc carbone 6 mm x 300 (goupille d'aile) | 1 | 13 | 13 | 143 |
| Tube carbone 6x4 x 720 (longeron du stab) | 1 | 18 | 18 | 667 |
| Joncs carbone 3 mm et 2 mm (stab, gouvernes) | 1 | 15 | 15 | 600 |
| Câblage, connecteurs | 1 | 170 | 170 | 40 |
| Visserie, guignols, colle, ruban | 1 | 70 | 70 | 100 |
| **Sans batterie** | | | **3486** | 133 |

## Centrage

Le centre de gravité doit tomber à **x = 62 mm** (28 % de corde), au milieu des 4 moteurs VTOL. On le règle en déplaçant la batterie sur le plateau.

| Batterie | Centre de la batterie requis | Plage possible | Lest |
|---|---:|---:|---|
| GAONENG GNB 6S3P P45B 13,5 Ah | x = -123 mm | -126 à -27 mm | aucun |

## Performances estimées

| | GAONENG GNB 6S3P P45B 13,5 Ah |
|---|---:|
| Masse au décollage | 4.82 kg |
| Charge alaire | 12.2 kg/m² |
| Vitesse de décrochage | 12.2 m/s (44 km/h) |
| Rapport poussée/poids VTOL | 2.17 (≈ 1.74 batterie affaissée) |
| Puissance en stationnaire | 656 W (30 A) |
| Transit à 90 km/h | 392 W |
| Vol en cercle au-dessus des lieux | 60 km/h, 165 W |
| Autonomie en cercle seulement | **82 min** |
| Temps sur les lieux, intervention à 5 km | **66 min** (aller 3 min) |
| Temps sur les lieux, intervention à 10 km | **50 min** (aller 7 min) |
| Temps sur les lieux, intervention à 15 km | **35 min** (aller 10 min) |
| Temps sur les lieux, intervention à 20 km | **19 min** (aller 13 min) |

Surface alaire 0.396 m², allongement 8.2. Hypothèses : Cd0 = 0.05, e = 0.8, rendement de propulsion 0.55, figure de mérite VTOL 0.6, 15 W pour l'électronique de bord, 85% de la batterie utilisée (le reste est la réserve), 2 min de vol stationnaire par mission, 2.62 kg de poussée max par moteur VTOL (× 0.8 batterie affaissée).
