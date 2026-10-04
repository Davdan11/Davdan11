# Bilan de masse, centrage et performances — Huard Mini

Généré par `calc/dimensionnement.py`. Les chiffres aérodynamiques sont des estimations, à recaler avec les logs des premiers vols.

## Masse et position (x depuis le bord d'attaque, vers l'arrière)

| Élément | Qté | Masse unitaire (g) | Total (g) | x (mm) |
|---|---:|---:|---:|---:|
| Pièces imprimées (cad/out/masses.csv) | 1 | 753 | 753 | 105 |
| Moteur VTOL Emax ECO III 2807 1300KV | 4 | 56 | 224 | 45 |
| Hélice VTOL HQProp Cine7 7x4x3 | 4 | 10 | 40 | 45 |
| ESC Skystars Talon32 40A AM32 (VTOL) | 4 | 7 | 28 | 45 |
| Moteur propulsif Emax ECO III 2807 1300KV | 1 | 56 | 56 | 283 |
| Hélice propulsive Gemfan 7x6E | 1 | 12 | 12 | 310 |
| ESC propulsif Skystars Talon32 40A | 1 | 7 | 7 | 200 |
| Contrôleur de vol AtomRC F405 NAVI | 1 | 21 | 21 | 95 |
| GPS + compas MicoAir M10G-5883 | 1 | 7 | 7 | 150 |
| Récepteur RadioMaster RP1 V2 | 1 | 3 | 3 | 125 |
| Servo JX PDI-1109MG (ailerons) | 2 | 10 | 20 | 88 |
| Servo JX PDI-1109MG (profondeur) | 1 | 10 | 10 | 458 |
| Tubes carbone 12x10 x 610 (poutres) | 2 | 33 | 66 | 107 |
| Tube carbone 10x8 x 720 (longeron principal) | 1 | 32 | 32 | 40 |
| Tube carbone 6x4 x 310 (longerons extérieurs) | 2 | 8 | 16 | 64 |
| Jonc carbone 4 mm x 200 (goupille d'aile) | 1 | 4 | 4 | 104 |
| Tube carbone 5x3 x 420 (longeron du stab) | 1 | 8 | 8 | 402 |
| Joncs carbone 2 mm et 1,5 mm (stab, gouvernes) | 1 | 8 | 8 | 300 |
| Câblage, connecteurs, condensateurs | 1 | 60 | 60 | 30 |
| Visserie, guignols, colle, ruban | 1 | 25 | 25 | 80 |
| **Sans batterie** | | | **1400** | 102 |

## Centrage

Le centre de gravité doit tomber à **x = 45 mm** (28 % de corde), au milieu des 4 moteurs VTOL. On le règle en déplaçant la batterie sur le plateau.

| Batterie | Centre de la batterie requis | Plage possible | Lest |
|---|---:|---:|---|
| CNHL G+Plus 4S 4000 mAh 70C (LiPo) | x = -145 mm | -155 à -65 mm | aucun |

## Performances estimées

| | CNHL G+Plus 4S 4000 mAh 70C (LiPo) |
|---|---:|
| Masse au décollage | 1.82 kg |
| Charge alaire | 9.5 kg/m² |
| Vitesse de décrochage | 10.8 m/s (39 km/h) |
| Rapport poussée/poids VTOL | 2.64 (≈ 2.38 batterie affaissée) |
| Puissance en stationnaire | 321 W (22 A) |
| Transit à 72 km/h | 134 W |
| Vol en cercle au-dessus des lieux | 53 km/h, 70 W |
| Autonomie en cercle seulement | **34 min** |
| Temps sur les lieux, intervention à 1 km | **31 min** (aller 1 min) |
| Temps sur les lieux, intervention à 2 km | **28 min** (aller 2 min) |
| Temps sur les lieux, intervention à 3 km | **25 min** (aller 2 min) |
| Temps sur les lieux, intervention à 5 km | **18 min** (aller 4 min) |

Surface alaire 0.192 m², allongement 7.5. Hypothèses : Cd0 = 0.055, e = 0.8, rendement de propulsion 0.45, figure de mérite VTOL 0.6, 3 W pour l'électronique de bord, 85% de la batterie utilisée (le reste est la réserve), 2 min de vol stationnaire par mission, 1.2 kg de poussée max par moteur VTOL (× 0.9 batterie affaissée).
