# Essais virtuels — Huard Mini

Généré par `calc/essais_virtuels.py`. Ce sont des calculs d'ingénieur classiques de pré-dimensionnement, faits sur les cotes réelles du modèle. Ils disent si la conception tient, avec quelle marge, et où sont les points faibles. Ils ne remplacent pas les essais au sol (test de charge de l'aile, voir plus bas) ni les premiers vols prudents.

Masse au décollage 1.86 kg, surface alaire 0.192 m², charge alaire 9.7 kg/m², décrochage 39 km/h, vitesse max réglée dans ArduPilot 79 km/h, vitesse de calcul en piqué 99 km/h.

## Résumé

✅ longeron principal Ø10 à 6.0 g (charge extrême) : 224 MPa pour 500 admissibles
✅ longeron extérieur Ø6 : 121 MPa pour 500
✅ aile en VTOL plein gaz : 104 MPa dans le longeron principal
✅ poutres en VTOL plein gaz : 36 MPa, flèche 0.4 mm
✅ atterrissage dur à 2 m/s : 166 MPa dans les poutres (21 g d'impact si les pattes s'écrasent de 10 mm)
✅ peau sous la pression de l'air : 2.8 MPa au pire panneau pour 12 MPa (flèche 1.26 mm)
✅ peau d'extrados comprimée par la flexion : elle n'ondule pas avant 4.7 g (charge limite 4.0 g)
✅ torsion à 99 km/h : peau 0.94 MPa, goupille 2 MPa, appui de la goupille dans le fuselage 1.5 MPa
✅ relais des longerons (recouvrement de 80 mm) : colle 0.14 MPa, appui dans le fourreau 0.6 MPa
✅ inversion des ailerons vers 494 km/h, divergence vers 273 km/h (il faut plus de 1,2 × 99 = 119 km/h)
✅ marge statique 14% (bien entre 5 et 20 %) : point neutre à 67 mm, centre de gravité à 45 mm
✅ volume d'empennage horizontal 0.41 (habituel 0,35 à 0,6)
✅ volume d'empennage vertical 0.024 (habituel 0,02 à 0,04)
✅ braquage de profondeur pour équilibrer : au plus 8° sur ±25° disponibles
✅ servos (±20° à 78 km/h, ±7° à 99 km/h) : aileron 0.16 kg·cm, profondeur 0.10 kg·cm, pour 2.2 kg·cm (7% ; à garder sous 50 %)
✅ résonance des poutres à 88 Hz (5300 tr/min) ; moteurs ≈ 9594 tr/min en stationnaire : on ne fait que la traverser en montant les gaz

✅ tient avec marge · ⚠️ à connaître (pas dangereux) · ❌ à corriger

## 1. Pression de l'air sur l'aile

Méthode des panneaux sur le profil NACA 4412 (Cp = 1 − (V/V∞)²). Dépression = Cp négatif, sur le dessus. Image : `docs/images/pression_aile_mini.png`.

| Cas | Vitesse | CL | Incidence du profil | Dépression max (bord d'attaque) |
|---|---:|---:|---:|---:|
| Croisière 65 km/h (1 g) | 65 km/h | 0.48 | -0.1° | 153 Pa (15.3 g/cm²) |
| Ressource à 78 km/h (4.0 g, portance max) | 78 km/h | 1.30 | 7.2° | 860 Pa (86.0 g/cm²) |
| Ressource à 99 km/h (4.0 g) | 99 km/h | 0.82 | 2.9° | 511 Pa (51.1 g/cm²) |

Peau de 0.6 mm entre deux âmes : le pire panneau fait 67 mm de large (Ressource à 99 km/h (4.0 g), segment 413–600 mm). Sous 453 Pa il fléchit de 1.26 mm et travaille à 2.80 MPa, pour environ 12 MPa de résistance : la peau ne se creuse pas visiblement.

## 2. Charges de vol

- Manœuvre : 3.8 g (catégorie normale). Rafale verticale de 7.6 m/s à 65 km/h : **4.0 g** (formule de Pratt ; un petit avion léger est très secoué par les rafales).
- Charge limite retenue **4.0 g**, charge extrême (1.5 ×) **6.0 g**.
- Vitesse de manœuvre (décroche avant de casser) : 78 km/h.

## 3. Flexion de l'aile

Répartition de portance de Schrenk. Image : `docs/images/flexion_aile_mini.png`.

| Endroit | Moment à charge extrême | Tube | Contrainte | Admissible |
|---|---:|---|---:|---:|
| Emplanture (y = 40 mm) | 13.0 N·m | Ø10 × 1 mm | 224 MPa | 500 MPa |
| Fin du longeron principal (y = 360 mm) | 2.1 N·m | Ø6 × 1 mm | 121 MPa | 500 MPa |
| Emplanture en VTOL plein gaz | 6.0 N·m | Ø10 × 1 mm | 104 MPa | 500 MPa |

Flèche en bout d'aile en vol normal (1 g) : **6 mm** (longerons seuls ; la peau raidit un peu).

**La peau suit la flexion.** Collée aux longerons par les âmes, la coque imprimée porte une partie de la flexion : l'extrados est comprimé. Une peau mince et large entre deux âmes ondule (voilement) quand la compression dépasse sa limite. Ce n'est pas une rupture (les tubes portent la charge), mais à répétition la peau peut fissurer. On veut donc que ça n'arrive pas avant la charge limite.

| Segment | Diagonales | Panneau le plus large | Part de la peau dans la raideur | Compression à 1 g | Limite d'ondulation | Ondule à partir de |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 12 | 23 mm | 29% | 0.50 MPa | 2.52 MPa | **5.0 g** |
| 2 | 8 | 37 mm | 25% | 0.18 MPa | 1.17 MPa | **6.3 g** |
| 3 | 5 | 67 mm | 67% | 0.11 MPa | 0.53 MPa | **4.7 g** |

Relais entre les longerons (recouvrement de 80 mm) : le tube extérieur pousse sur son fourreau avec ≈ 52 N à charge extrême, soit 0.6 MPa d'appui sur le PLA Aero et 0.14 MPa dans la colle époxy (elle tient 10 à 20 MPa).

## 4. Torsion, goupille, inversion d'ailerons

- Couple de torsion à l'emplanture (99 km/h, aileron braqué, × 1.5) : 1.89 N·m.
- Cisaillement dans la peau : 0.94 MPa (≈ 7 admissibles).
- Goupille Ø4 : effort 30 N, cisaillement 2 MPa, appui dans le bossage du fuselage 1.5 MPa.
- Raideur en torsion de l'aile (coque seule) : GJ ≈ 9 N·m². Les ailerons s'inverseraient vers **494 km/h** et l'aile divergerait vers **273 km/h** : loin au-dessus de ce que l'avion peut faire.

## 5. Stabilité et équilibre

- Point neutre à **67 mm** du bord d'attaque (42% de corde), centre de gravité à 45 mm : **marge statique 14%**. Un avion se pilote bien entre 5 et 15 %.
- Volume d'empennage horizontal 0.41, vertical 0.024.
- Effet du fuselage pris en compte (Raymer) ; descente du flux de l'aile sur le stab dε/dα = 0.41.

| Vol en palier | Braquage de profondeur pour équilibrer | Assiette du fuselage |
|---|---:|---:|
| 51 km/h | -2.6° | +3.0° |
| 65 km/h | +0.4° | -0.4° |
| 79 km/h | +2.1° | -2.3° |
| Ressource 4.0 g à 78 km/h | -8.2° | |

(+ = bord de fuite de la profondeur vers le bas.) La profondeur garde de la réserve sur ses ±25°. ArduPilot règle le reste tout seul (TRIM_PITCH_DEG, autotune).

## 6. Servos et débattements

Comme la norme des avions légers : plein braquage (±20°) à la vitesse de manœuvre (78 km/h), un tiers du braquage à la vitesse de piqué (99 km/h). Servo qui tourne de ±45°.

| Gouverne | Moment de charnière | Bras du guignol (trou intérieur) | Trou du palonnier pour ±20° | Couple au servo | Servo |
|---|---:|---:|---:|---:|---:|
| Aileron (chacun) | 3.3 N·cm | 16 mm | **8 mm** de l'axe | 0.16 kg·cm | 7% de 2.2 kg·cm |
| Profondeur (les deux) | 2.0 N·cm | 11 mm | **5 mm** de l'axe | 0.10 kg·cm | 4% de 2.2 kg·cm |

Régler les fins de course dans ArduPilot (SERVOx_MIN / MAX) pour ±20° de gouverne, mesurés au rapporteur. Plus de débattement n'apporte rien à cet avion et charge les servos.

## 7. Poutres, vibrations, atterrissage

- Plein gaz en stationnaire (1.2 kg par moteur, × 1.5) : 36 MPa dans la poutre, flèche 0.4 mm au moteur.
- Fréquence propre d'une poutre avec son moteur : **88 Hz** (5300 tr/min). En stationnaire les moteurs tournent vers 9594 tr/min : on ne fait que traverser la résonance en montant les gaz. Équilibrer les hélices et activer le filtre anti-vibration d'ArduPilot (INS_HNTCH_*) après le premier vol.
- Atterrissage dur à 2 m/s (4 fois la vitesse normale) : si les pattes TPU s'écrasent de 10 mm, l'impact fait 21 g, 98 N par patte, 166 MPa dans les poutres.

## Ce qu'il faut vérifier en vrai

1. **Test de charge de l'aile au sol** (le plus important) : aile montée sur le fuselage, posée à l'envers sur deux tréteaux sous le fuselage, répartir des sacs de sable sur l'intrados. 4.0 g, c'est 7.4 kg en tout, dont 60 % sur la moitié intérieure de chaque aile. Monter par paliers ; l'aile doit revenir droite. Ne pas aller jusqu'à la charge extrême.
2. **Les servos** : avec l'avion branché, pousser une gouverne au doigt : elle ne doit pas bouger, et le servo ne doit pas grogner au neutre.
3. **Le centrage** : soulever l'avion du bout des doigts sous l'aile au point de centrage (45 mm du bord d'attaque) : il doit rester à plat ou piquer très légèrement du nez.
4. **Les vibrations** : premier vol stationnaire, puis lire le log (VIBE) dans Mission Planner.

## Hypothèses

- PLA Aero moussé : module 900 MPa, résistance 12 MPa, cisaillement 7 MPa (valeurs prudentes, non mesurées).
- Tubes carbone roulés : module 100 GPa, 500 MPa admissibles en flexion (les tubes du commerce tiennent 600 à 1000 MPa) ; épaisseur 1 mm.
- Servo 2.2 kg·cm à 4,8 V (fiche technique), à garder sous 50 % en continu. Moment de charnière : coefficients habituels d'une gouverne simple ; peau de gouverne étanche (ruban).
- Méthode des panneaux sans viscosité : elle surestime un peu la dépression (côté sûr).
- Poussée max d'un moteur VTOL : 1.2 kg (même valeur que le bilan).
