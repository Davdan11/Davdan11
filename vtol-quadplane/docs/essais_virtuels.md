# Essais virtuels — Huard DFR

Généré par `calc/essais_virtuels.py`. Ce sont des calculs d'ingénieur classiques de pré-dimensionnement, faits sur les cotes réelles du modèle. Ils disent si la conception tient, avec quelle marge, et où sont les points faibles. Ils ne remplacent pas les essais au sol (test de charge de l'aile, voir plus bas) ni les premiers vols prudents.

Masse au décollage 4.89 kg, surface alaire 0.396 m², charge alaire 12.3 kg/m², décrochage 44 km/h, vitesse max réglée dans ArduPilot 108 km/h, vitesse de calcul en piqué 135 km/h.

## Résumé

✅ longeron principal Ø16 à 6.4 g (charge extrême) : 333 MPa pour 500 admissibles
✅ longeron extérieur Ø8 : 318 MPa pour 500
✅ aile en VTOL plein gaz : 141 MPa dans le longeron principal
✅ poutres en VTOL plein gaz : 70 MPa, flèche 1.8 mm
✅ atterrissage dur à 2 m/s : 408 MPa dans les poutres (21 g d'impact si les pattes s'écrasent de 10 mm)
✅ peau sous la pression de l'air : 2.0 MPa au pire panneau pour 12 MPa (flèche 1.12 mm)
✅ peau d'extrados comprimée par la flexion : elle n'ondule pas avant 5.3 g (charge limite 4.2 g)
✅ torsion à 135 km/h : peau 2.63 MPa, goupille 4 MPa, appui de la goupille dans le fuselage 3.8 MPa
✅ relais des longerons (recouvrement de 120 mm) : colle 0.36 MPa, appui dans le fourreau 1.5 MPa
✅ inversion des ailerons vers 384 km/h, divergence vers 212 km/h (il faut plus de 1,2 × 135 = 162 km/h)
⚠️ marge statique 22% : très stable (un peu lourd du nez à piloter, pas dangereux). Le centre de gravité reste à 62 mm, au milieu des moteurs VTOL, pour le vol stationnaire
✅ volume d'empennage horizontal 0.53 (habituel 0,35 à 0,6)
✅ volume d'empennage vertical 0.026 (habituel 0,02 à 0,04)
✅ braquage de profondeur pour équilibrer : au plus 8° sur ±25° disponibles
✅ servos (±20° à 91 km/h, ±7° à 135 km/h) : aileron 0.58 kg·cm, profondeur 0.34 kg·cm, pour 2 kg·cm (29% ; à garder sous 50 %)
✅ résonance des poutres à 40 Hz (2370 tr/min) ; moteurs ≈ 4852 tr/min en stationnaire : on ne fait que la traverser en montant les gaz

✅ tient avec marge · ⚠️ à connaître (pas dangereux) · ❌ à corriger

## 1. Pression de l'air sur l'aile

Méthode des panneaux sur le profil NACA 4412 (Cp = 1 − (V/V∞)²). Dépression = Cp négatif, sur le dessus. Image : `docs/images/pression_aile.png`.

| Cas | Vitesse | CL | Incidence du profil | Dépression max (bord d'attaque) |
|---|---:|---:|---:|---:|
| Croisière 90 km/h (1 g) | 90 km/h | 0.32 | -1.5° | 248 Pa (24.8 g/cm²) |
| Ressource à 91 km/h (4.2 g, portance max) | 91 km/h | 1.30 | 7.2° | 1169 Pa (116.9 g/cm²) |
| Ressource à 135 km/h (4.2 g) | 135 km/h | 0.60 | 0.9° | 751 Pa (75.1 g/cm²) |

Peau de 0.6 mm entre deux âmes : le pire panneau fait 75 mm de large (Ressource à 91 km/h (4.2 g, portance max), segment 689–900 mm). Sous 254 Pa il fléchit de 1.12 mm et travaille à 1.97 MPa, pour environ 12 MPa de résistance : la peau ne se creuse pas visiblement.

## 2. Charges de vol

- Manœuvre : 3.8 g (catégorie normale). Rafale verticale de 7.6 m/s à 90 km/h : **4.2 g** (formule de Pratt ; un petit avion léger est très secoué par les rafales).
- Charge limite retenue **4.2 g**, charge extrême (1.5 ×) **6.4 g**.
- Vitesse de manœuvre (décroche avant de casser) : 91 km/h.

## 3. Flexion de l'aile

Répartition de portance de Schrenk. Image : `docs/images/flexion_aile.png`.

| Endroit | Moment à charge extrême | Tube | Contrainte | Admissible |
|---|---:|---|---:|---:|
| Emplanture (y = 55 mm) | 55.4 N·m | Ø16 × 1 mm | 333 MPa | 500 MPa |
| Fin du longeron principal (y = 500 mm) | 10.9 N·m | Ø8 × 1 mm | 318 MPa | 500 MPa |
| Emplanture en VTOL plein gaz | 23.5 N·m | Ø16 × 1 mm | 141 MPa | 500 MPa |

Flèche en bout d'aile en vol normal (1 g) : **15 mm** (longerons seuls ; la peau raidit un peu).

**La peau suit la flexion.** Collée aux longerons par les âmes, la coque imprimée porte une partie de la flexion : l'extrados est comprimé. Une peau mince et large entre deux âmes ondule (voilement) quand la compression dépasse sa limite. Ce n'est pas une rupture (les tubes portent la charge), mais à répétition la peau peut fissurer. On veut donc que ça n'arrive pas avant la charge limite.

| Segment | Diagonales | Panneau le plus large | Part de la peau dans la raideur | Compression à 1 g | Limite d'ondulation | Ondule à partir de |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 20 | 19 mm | 20% | 0.66 MPa | 3.55 MPa | **5.3 g** |
| 2 | 14 | 27 mm | 18% | 0.33 MPa | 1.81 MPa | **5.5 g** |
| 3 | 10 | 38 mm | 18% | 0.14 MPa | 1.02 MPa | **7.4 g** |
| 4 | 6 | 39 mm | 67% | 0.12 MPa | 1.01 MPa | **8.4 g** |

Relais entre les longerons (recouvrement de 120 mm) : le tube extérieur pousse sur son fourreau avec ≈ 182 N à charge extrême, soit 1.5 MPa d'appui sur le PLA Aero et 0.36 MPa dans la colle époxy (elle tient 10 à 20 MPa).

## 4. Torsion, goupille, inversion d'ailerons

- Couple de torsion à l'emplanture (135 km/h, aileron braqué, × 1.5) : 10.04 N·m.
- Cisaillement dans la peau : 2.63 MPa (≈ 7 admissibles).
- Goupille Ø6 : effort 114 N, cisaillement 4 MPa, appui dans le bossage du fuselage 3.8 MPa.
- Raideur en torsion de l'aile (coque seule) : GJ ≈ 22 N·m². Les ailerons s'inverseraient vers **384 km/h** et l'aile divergerait vers **212 km/h** : loin au-dessus de ce que l'avion peut faire.

## 5. Stabilité et équilibre

- Point neutre à **110 mm** du bord d'attaque (50% de corde), centre de gravité à 62 mm : **marge statique 22%**. Un avion se pilote bien entre 5 et 15 %.
- Volume d'empennage horizontal 0.53, vertical 0.026.
- Effet du fuselage pris en compte (Raymer) ; descente du flux de l'aile sur le stab dε/dα = 0.38.

| Vol en palier | Braquage de profondeur pour équilibrer | Assiette du fuselage |
|---|---:|---:|
| 58 km/h | -1.5° | +2.7° |
| 90 km/h | +3.7° | -2.5° |
| 108 km/h | +4.8° | -3.6° |
| Ressource 4.2 g à 91 km/h | -7.5° | |

(+ = bord de fuite de la profondeur vers le bas.) La profondeur garde de la réserve sur ses ±25°. ArduPilot règle le reste tout seul (TRIM_PITCH_DEG, autotune).

## 6. Servos et débattements

Comme la norme des avions légers : plein braquage (±20°) à la vitesse de manœuvre (91 km/h), un tiers du braquage à la vitesse de piqué (135 km/h). Servo qui tourne de ±45°.

| Gouverne | Moment de charnière | Bras du guignol (trou intérieur) | Trou du palonnier pour ±20° | Couple au servo | Servo |
|---|---:|---:|---:|---:|---:|
| Aileron (chacun) | 11.8 N·cm | 22 mm | **10 mm** de l'axe | 0.58 kg·cm | 29% de 2 kg·cm |
| Profondeur (les deux) | 6.9 N·cm | 14 mm | **7 mm** de l'axe | 0.34 kg·cm | 17% de 2 kg·cm |

Régler les fins de course dans ArduPilot (SERVOx_MIN / MAX) pour ±20° de gouverne, mesurés au rapporteur. Plus de débattement n'apporte rien à cet avion et charge les servos.

## 7. Poutres, vibrations, atterrissage

- Plein gaz en stationnaire (2.62 kg par moteur, × 1.5) : 70 MPa dans la poutre, flèche 1.8 mm au moteur.
- Fréquence propre d'une poutre avec son moteur : **40 Hz** (2370 tr/min). En stationnaire les moteurs tournent vers 4852 tr/min : on ne fait que traverser la résonance en montant les gaz. Équilibrer les hélices et activer le filtre anti-vibration d'ArduPilot (INS_HNTCH_*) après le premier vol.
- Atterrissage dur à 2 m/s (4 fois la vitesse normale) : si les pattes TPU s'écrasent de 10 mm, l'impact fait 21 g, 256 N par patte, 408 MPa dans les poutres.

## Ce qu'il faut vérifier en vrai

1. **Test de charge de l'aile au sol** (le plus important) : aile montée sur le fuselage, posée à l'envers sur deux tréteaux sous le fuselage, répartir des sacs de sable sur l'intrados. 4.2 g, c'est 20.8 kg en tout, dont 60 % sur la moitié intérieure de chaque aile. Monter par paliers ; l'aile doit revenir droite. Ne pas aller jusqu'à la charge extrême.
2. **Les servos** : avec l'avion branché, pousser une gouverne au doigt : elle ne doit pas bouger, et le servo ne doit pas grogner au neutre.
3. **Le centrage** : soulever l'avion du bout des doigts sous l'aile au point de centrage (62 mm du bord d'attaque) : il doit rester à plat ou piquer très légèrement du nez.
4. **Les vibrations** : premier vol stationnaire, puis lire le log (VIBE) dans Mission Planner.

## Hypothèses

- PLA Aero moussé : module 900 MPa, résistance 12 MPa, cisaillement 7 MPa (valeurs prudentes, non mesurées).
- Tubes carbone roulés : module 100 GPa, 500 MPa admissibles en flexion (les tubes du commerce tiennent 600 à 1000 MPa) ; épaisseur 1 mm.
- Servo 2 kg·cm à 4,8 V (fiche technique), à garder sous 50 % en continu. Moment de charnière : coefficients habituels d'une gouverne simple ; peau de gouverne étanche (ruban).
- Méthode des panneaux sans viscosité : elle surestime un peu la dépression (côté sûr).
- Poussée max d'un moteur VTOL : 2.62 kg (même valeur que le bilan).
