# Huard DFR : quadplane VTOL premier intervenant, imprimé en 3D

C'est un drone à décollage vertical de 1,8 m d'envergure, pensé pour être **le premier sur les lieux d'une intervention** (accident, recherche de personne, incendie). Il part seul d'une station, file à 90 km/h vers les coordonnées reçues, tourne au-dessus des lieux et transmet **en direct** l'image d'une caméra zoom et thermique aux policiers par le réseau cellulaire. Il revient ensuite se poser à la verticale.

Les pièces imprimées sont conçues pour une **Bambu Lab A1** (plateau 256 mm) et assemblées sur des tubes de carbone. Le concept complet (stations, logiciel, vidéo, réglementation, étapes) est dans [docs/concept_dfr.md](docs/concept_dfr.md).

![Vue 3/4](cad/out/rendus/vue_3-4.png)

| | |
|---|---|
| Envergure / corde | 1800 mm / 220 mm (aile rectangulaire, NACA 4412, calage 2,5°) |
| Longueur | ≈ 1050 mm |
| Masse au décollage | ≈ 4,8 kg |
| Propulsion VTOL | 4 × T-Motor MN4014 KV400, hélices P15×5, poussée/poids ≈ 2,2 (≈ 1,8 batterie affaissée) |
| Croisière | SunnySky X2820 V3 KV570 en pousseur, hélice APC 10×7EP |
| Batterie | GAONENG 6S3P Molicel P45B (13,5 Ah, 290 Wh, 1,34 kg) |
| Vitesses | transit 90 km/h, vol en cercle au-dessus des lieux ≈ 58 km/h |
| Charge utile | nacelle SIYI A8 mini (puis ZT6 thermique), Raspberry Pi 5, modem 4G Waveshare SIM7600G-H |
| Pilote automatique | ArduPilot sur TBS Lucid H7 Wing |

**Temps disponible au-dessus des lieux** (estimation, avec 15 % de réserve) :

| Distance de l'intervention | 5 km | 10 km | 15 km | 20 km |
|---|---|---|---|---|
| Temps pour arriver | 3 min | 7 min | 10 min | 13 min |
| Temps sur place | ≈ 68 min | ≈ 52 min | ≈ 35 min | ≈ 19 min |

Le détail des calculs (masse, centrage, puissances) est dans [docs/bilan.md](docs/bilan.md). La **liste d'achats avec les modèles exacts et les liens** est dans [docs/nomenclature.md](docs/nomenclature.md) : le CAD est percé pour ces modèles.

## Deux versions : commencer petit

| | **Huard Mini** (pour apprendre) | **Huard DFR** (la mission) |
|---|---|---|
| Envergure | 1,2 m | 1,8 m |
| Masse au décollage | ≈ 1,8 kg | ≈ 4,8 kg |
| Batterie | LiPo 4S 4000 mAh | Li-ion 6S3P 13,5 Ah |
| Moteurs | 5 × Emax ECO III 2807 (pièces FPV) | 4 × T-Motor MN4014 + SunnySky X2820 |
| Caméra / 4G | non (caméra d'action en option) | SIYI A8 mini puis ZT6, Raspberry Pi, modem 4G |
| Autonomie estimée | ≈ 34 min | ≈ 84 min |
| Budget de l'avion | **≈ 670 $ CA** | ≈ 3 100 $ CA |
| Liste d'achats | [docs/nomenclature_mini.md](docs/nomenclature_mini.md) | [docs/nomenclature.md](docs/nomenclature.md) |
| Bilan | [docs/bilan_mini.md](docs/bilan_mini.md) | [docs/bilan.md](docs/bilan.md) |
| Paramètres ArduPilot | `ardupilot/huard_mini.param` | `ardupilot/huard_dfr.param` |
| Pièces à imprimer | `cad/out_mini/stl/` | `cad/out/stl/` |

Le Mini a exactement la même architecture : aile segmentée, poutres carbone, empennage en H, propulseur arrière, ArduPilot quadplane. Tout ce qu'on apprend dessus (impression, collage, réglages, transitions, missions automatiques) s'applique au grand. Les réglages d'impression et l'ordre d'assemblage plus bas valent pour les deux.

![Huard Mini](cad/out_mini/rendus/vue_3-4.png)

## Contenu

```
cad/params_dfr.py       toutes les cotes du DFR (changer une valeur et régénérer)
cad/params_mini.py      toutes les cotes du Mini
cad/pieces.py           géométrie de chaque pièce (CadQuery)
cad/build.py            génère STL, STEP, masses, centre de gravité et rendus
cad/out/stl/            pièces prêtes à trancher, déjà orientées pour l'impression
cad/out/step/           pièces dans le repère avion, pour modifier dans Fusion ou Onshape
cad/out/assemblage.glb  avion complet en 3D
calc/dimensionnement.py bilan de masse, centrage, poussée, autonomie, rayon d'action
ardupilot/huard_dfr.param  paramètres de départ ArduPilot (TBS Lucid H7 Wing)
docs/                   concept du système, nomenclature, bilan
```

### Régénérer les pièces

```bash
pip install cadquery trimesh shapely matplotlib networkx
cd cad && python build.py                        # Huard DFR  -> cad/out/
HUARD_VERSION=mini python build.py               # Huard Mini -> cad/out_mini/
cd .. && python calc/dimensionnement.py          # bilan DFR  -> docs/bilan.md
HUARD_VERSION=mini python calc/dimensionnement.py  # bilan Mini -> docs/bilan_mini.md
# Sous Windows (PowerShell) : $env:HUARD_VERSION="mini"; python build.py
```

## Configuration

```
              vue de dessus (nez vers la droite)
   bloc de queue    M2 ●────────────────────────────● M3   (arrière / avant gauche)
   + dérive            ║        ┌──────────────┐    ║
   stab + profondeur   ║  ◐ ═══ │   fuselage   │ ═══════   ← aile 1,8 m
   (empennage en H)    ║ pousseur└──────────────┘    ║
                    M4 ●────────────────────────────● M1   (arrière / avant droit)
                                       ▼ nacelle caméra sous l'avant du fuselage
```

- **Deux poutres carbone** à ±360 mm sous l'aile, tenues par des pylônes collés. Elles portent les 4 moteurs VTOL (±365 mm autour du centre de gravité, hélices de 15 po) et l'empennage en H au bout.
- **Le fuselage** est en 4 tronçons. Le nez est amovible pour glisser la batterie sur le plateau avant. Le contrôleur de vol, le Raspberry Pi et le modem 4G sont sur un second plateau dans le tronçon du milieu. Le moteur propulsif est boulonné sur une cloison en PETG au bout de la queue.
- **La nacelle caméra** est fixée sous l'avant du fuselage, sur une selle en PETG vissée à travers le plateau. Elle voit vers l'avant et vers le bas sans être gênée par les hélices.
- **L'aile** est en 2 demi-ailes de 4 segments chacune, enfilées sur un longeron de 12 mm qui traverse le fuselage. Un longeron de 8 mm prend le relais vers les bouts d'aile et une goupille de 6 mm fixe l'incidence.
- **Le centre de gravité** visé est à 62 mm du bord d'attaque (28 % de corde), au milieu des 4 moteurs VTOL. Avec la batterie GAONENG, il tombe en place quand **le centre de la batterie est à 116 mm devant le bord d'attaque**, c'est-à-dire batterie poussée presque au bout du plateau, sans lest (voir docs/bilan.md).

## Impression (Bambu Studio)

Les STL de `cad/out/stl/` sont déjà dans la bonne orientation et s'impriment sans supports : les segments d'aile et de stab sont debout sur leur face d'emplanture, les tronçons de fuselage debout (le nez pointe en haut) et les pattes debout sur leur pied.

| Pièces | Filament | Réglages |
|---|---|---|
| `aile_segment_*`, `stab_segment_*` | PLA Aero | **1 paroi, 0 % de remplissage, 0 couche dessus/dessous**, détection des parois fines activée. Les parois, âmes et fourreaux sont déjà modélisés. Exception : le segment qui porte la baie du servo d'aileron (segment 3 du DFR, segment 2 du Mini) avec 2 couches dessus/dessous pour fermer la baie. |
| `aileron_*`, `profondeur_*` | PLA Aero | **2 parois** (peau de 0,8 mm), 0 % de remplissage, **3 couches dessus/dessous** pour fermer les bouts |
| `guignol_aileron` (×2), `guignol_profondeur` | PETG | À plat, 100 % de remplissage : petites pièces qui travaillent |
| `fuselage_avant`, `fuselage_milieu`, `fuselage_queue` | PLA Aero | 1 paroi, 0 % de remplissage, 0 couche dessus/dessous |
| `fuselage_nez` | PLA Aero | 1 paroi, 0 % de remplissage, **3 couches dessus** (la pointe est fermée) |
| `saumon_*`, `bloc_queue_*` | PLA Aero | 3 parois, 8 % gyroïde |
| `pylone_poutre_*` | PETG | 3 parois, 10 % gyroïde, bordure de 5 mm |
| `support_moteur` (×4) | PETG | 4 parois, 40 % gyroïde |
| `cloison_moteur`, `support_nacelle` | PETG | 4 parois, 50 % |
| `plateau_electronique`, `plateau_compagnon` | PETG | 3 parois, 30 % |
| `patte_atterrissage` (×4) | TPU 95A | 3 parois, 25 %, vitesse lente |

Conseils pour la A1 : son plateau bouge d'avant en arrière, donc place les pièces hautes et minces (segments d'aile) avec la corde dans l'axe avant-arrière. Ajoute une bordure (brim) de 5 mm et ralentis les parois extérieures à environ 150 mm/s. Imprime d'abord **un seul segment d'aile** pour valider le profil PLA Aero (température, moussage, masse ≈ 60 g).

Masse estimée de chaque pièce : `cad/out/masses.csv`. Pèse tes pièces : si elles sont nettement plus lourdes, ajuste le débit du PLA Aero avant d'imprimer le reste.

## Assemblage, dans l'ordre

1. **Aile** : coller les segments de chaque côté à la CA en les enfilant sur le longeron pour l'alignement. Coller le saumon.
   - **Ailerons** : enfiler les deux morceaux d'aileron sur le jonc carbone de 2 mm, glisser le **guignol PETG** par-dessous dans sa fente (le jonc passe dans son trou), puis coller le tout à la CA. Poser l'aileron avec une charnière en ruban sur l'extrados.
   - **Servo d'aileron** : il se loge couché dans la baie ouverte sous l'aile, palonnier vers le bas. Son fil passe par le trou vers l'emplanture et suit les alvéoles de l'aile jusqu'au fuselage. La tringle de 1,5 mm relie le palonnier au trou du bas du guignol. Coupe à travers l'aile : [DFR](docs/images/coupe_servo_aileron_dfr.png), [Mini](docs/images/coupe_servo_aileron_mini.png).
2. **Longerons** : le tube de 8 mm × 500 mm est collé à l'époxy dans les segments 2 à 4. Le tube de 12 mm et la goupille de 6 mm restent démontables.
3. **Pylônes** : les coller à l'époxy sous le segment 2, centrés à 330 mm de l'axe. Le trou de câble du pylône doit tomber sur celui de l'aile. Percer la poutre au même endroit (Ø 8 mm) pour passer les fils.
4. **Poutres** : enfiler dans l'ordre la patte avant, le support moteur avant, le pylône, la patte arrière, le support moteur arrière, puis coller le bloc de queue au bout. Distances depuis le bout avant du tube : moteur avant 22 mm, moteur arrière 752 mm.
5. **Empennage** : coller les 3 segments de stab sur le tube de 6 mm et le jonc de 3 mm, puis les insérer dans les deux blocs de queue. Enfiler les profondeurs sur leur jonc carbone, glisser le **guignol de profondeur** par le dessus dans sa fente (côté droit, près du bloc de queue), coller, et poser avec une charnière en ruban. Le servo de profondeur va dans la baie du bloc droit (palonnier côté intérieur) et ses fils passent dans la poutre.
6. **Fuselage** : coller la cloison moteur en PETG à l'époxy au bout de la queue. Glisser le plateau électronique dans l'avant et le plateau compagnon dans le milieu, puis coller avant, milieu et queue (lèvres d'emboîtement). Le nez reste amovible, tenu par du ruban ou deux aimants. Le tube de Pitot sort par la pointe du nez.
7. **Nacelle** : coller la selle sous l'avant du fuselage, puis la visser avec 2 vis M3 × 35 qui traversent le fond et les plots du plateau de batterie (têtes plates sous la batterie). La nacelle se visse sous la selle : 4 × M2.5 pour l'A8 mini, 4 × M3 pour la ZT6. Les câbles passent par l'ouverture centrale.
8. **Électronique** : TBS Lucid H7 Wing sur les entretoises 30,5 mm du plateau compagnon, Raspberry Pi sur les entretoises 58 × 49 mm, modem 4G collé à côté. GPS Micro M10 et antennes LTE sur le dessus du fuselage milieu, loin des câbles de puissance. Les ESC Tekko32 sont fixés sur les poutres près des moteurs, à l'air, avec leur condensateur.

### Moteurs et sens de rotation (ordre ArduPilot Quad X)

| Sortie | Moteur | Position | Sens |
|---|---|---|---|
| S1 | 1 | avant droit | anti-horaire (CCW) |
| S2 | 2 | arrière gauche | anti-horaire (CCW) |
| S3 | 3 | avant gauche | horaire (CW) |
| S4 | 4 | arrière droit | horaire (CW) |
| S5 | propulseur | arrière du fuselage | hélice pousseur |
| S7 / S8 | ailerons gauche / droit | | |
| S9 | profondeur | | |

## ArduPilot

1. Flasher ArduPlane sur le Lucid H7 Wing, cible `TBS_LUCID_H7_WING` (Mission Planner > Install Firmware).
2. Charger `ardupilot/huard_dfr.param`, écrire, puis redémarrer **deux fois** : `Q_ENABLE` fait apparaître les autres paramètres.
3. Calibrer l'accéléromètre, le compas et la radio, et vérifier le capteur de vitesse.
4. Dans Mission Planner, ouvrir Motor Test et vérifier l'ordre et le sens de chaque moteur VTOL **sans hélices**.
5. Vérifier le sens des gouvernes en mode FBWA : quand on penche l'avion à droite, l'aileron droit doit se baisser.
6. Câbler selon le fichier de paramètres : GPS sur UART2, récepteur sur UART6, nacelle sur UART4, Raspberry Pi sur UART7. Vérifier la tension de batterie au multimètre (`BATT_VOLT_MULT`).

## Plan d'essais en vol

1. **Sol** : centre de gravité à 62 mm (± 5 mm), failsafe radio testé, batterie chargée.
2. **Stationnaire** en QSTABILIZE puis QHOVER, à 2–3 m, par vent calme, dans un grand champ. Ensuite **QAUTOTUNE** axe par axe.
3. **Première transition** en QLOITER à 40 m ou plus, puis passer en FBWA : le propulseur accélère et les moteurs VTOL s'arrêtent vers 16 m/s. Repasser en QLOITER pour revenir.
4. **AUTOTUNE** avion, puis réglage de `TRIM_THROTTLE` et de `AIRSPEED_CRUISE`.
5. **Missions AUTO** avec `VTOL_TAKEOFF`, transit, `LOITER_UNLIM` puis `VTOL_LAND`, en allongeant la durée par paliers et en surveillant la consommation (mAh/km) dans les logs.
6. **Vidéo** : vérifier la qualité et le délai de l'image en direct par 4G, au sol puis en vol. Voir docs/concept_dfr.md.

## Réglementation (Canada)

Au-dessus de 250 g, le drone doit être **immatriculé auprès de Transports Canada** et tu dois avoir au minimum le **certificat de pilote pour opérations de base**. Pour la mise au point, il faut voler à vue, sous 122 m, loin des aéroports et des personnes. L'usage « premier intervenant » demande de voler **hors de portée visuelle** au-dessus de routes et de gens : ça exige des certificats et des autorisations spéciales de Transports Canada, normalement obtenus avec le service de police partenaire. Vérifie les règles à jour.

## Limites connues et points à valider

- Les performances viennent d'un modèle simple (Cd0 estimé à 0,05 avec la nacelle). Seuls les logs des premiers vols donneront la vraie consommation.
- La masse des pièces imprimées est une estimation à partir du CAD. Pèse-les.
- Avec une batterie Li-ion qui s'affaisse sous charge, la poussée VTOL réelle tombe à environ 80 % de la table T-Motor (poussée/poids ≈ 1,8). C'est suffisant mais sans grande marge : si le stationnaire est juste, passer aux hélices P16×5,4.
- Le contrôle en lacet en stationnaire vient seulement du couple des moteurs. S'il est mou, incliner les supports moteurs de 3 à 5° (voir la documentation ArduPilot sur l'inclinaison des moteurs de quadplane).
- Le poids du Lucid H7 Wing n'est pas publié (≈ 30 g supposé) et le moteur X2820 KV570 n'a pas de fiche de poussée publiée : à mesurer.
- C'est un **prototype de démonstration**. Un usage réel par la police demandera des redondances (parachute, double lien de contrôle), des essais documentés et une certification.
