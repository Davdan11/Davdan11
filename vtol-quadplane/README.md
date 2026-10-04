# Huard : quadplane VTOL imprimé en 3D

C'est un avion à décollage vertical de 1,8 m d'envergure. Il décolle comme un drone sur 4 moteurs, passe en vol d'avion grâce à un moteur propulsif arrière, puis revient se poser à la verticale. Les pièces imprimées sont conçues pour une **Bambu Lab A1** (plateau 256 mm) et assemblées sur des tubes de carbone.

![Vue 3/4](cad/out/rendus/vue_3-4.png)

| | |
|---|---|
| Envergure / corde | 1800 mm / 220 mm (aile rectangulaire, NACA 4412, calage 2,5°) |
| Longueur | ≈ 1050 mm (poutres de 1000 mm) |
| Masse au décollage | ≈ 3,2 kg avec la batterie 4S2P |
| Propulsion VTOL | 4 moteurs 3510 ~700 KV, hélices 12 po, poussée/poids ≈ 2 |
| Croisière | 1 moteur 2814 ~900 KV en pousseur, hélice 10 × 7 |
| Batterie | Li-ion 4S2P 21700 (9 Ah, 130 Wh) |
| Autonomie estimée | **≈ 70 min à 49 km/h** (≈ 90 min avec une 4S3P) |
| Pilote automatique | ArduPilot sur Matek H743-WING V3 |

Le détail des calculs est dans [docs/bilan.md](docs/bilan.md) et la liste d'achats dans [docs/nomenclature.md](docs/nomenclature.md).

## Contenu

```
cad/params.py          toutes les cotes (changer une valeur et régénérer)
cad/pieces.py          géométrie de chaque pièce (CadQuery)
cad/build.py           génère STL, STEP, masses et rendus
cad/out/stl/           pièces prêtes à trancher, déjà orientées pour l'impression
cad/out/step/          pièces dans le repère avion, pour modifier dans Fusion ou Onshape
cad/out/assemblage.glb avion complet en 3D
calc/dimensionnement.py bilan de masse, poussée, puissance, autonomie
ardupilot/huard_quadplane.param  paramètres de départ ArduPilot
docs/                  nomenclature et bilan
```

### Régénérer les pièces

```bash
pip install cadquery trimesh shapely matplotlib networkx
cd cad && python build.py        # environ 30 s
cd .. && python calc/dimensionnement.py
```

## Configuration

```
              vue de dessus (nez vers la droite)
   bloc de queue    M2 ●────────────────────────────● M3   (arrière / avant gauche)
   + dérive            ║        ┌──────────┐        ║
   stab + profondeur   ║  ◐ ═══ │ fuselage │ ═══════════   ← aile 1,8 m
   (empennage en H)    ║ pousseur└──────────┘        ║
                    M4 ●────────────────────────────● M1   (arrière / avant droit)
```

- **Deux poutres carbone** à ±330 mm sous l'aile, tenues par des pylônes collés. Elles portent les 4 moteurs VTOL (±350 mm autour du centre de gravité) et l'empennage en H au bout.
- **Le fuselage** loge la batterie à l'avant, accessible en retirant le nez (emboîtement à lèvre), puis l'électronique sur un plateau. Le moteur propulsif est boulonné sur la cloison arrière.
- **L'aile** est en 2 demi-ailes de 4 segments chacune, enfilées sur un longeron de 12 mm qui traverse le fuselage. Un longeron de 8 mm prend le relais vers les bouts d'aile et une goupille de 6 mm fixe l'incidence.
- **Le centre de gravité** visé est à 62 mm du bord d'attaque (28 % de corde). Il doit être au milieu des 4 moteurs VTOL ; on l'ajuste en avançant ou reculant la batterie.

## Impression (Bambu Studio)

Les STL de `cad/out/stl/` sont déjà dans la bonne orientation et s'impriment sans supports : les segments d'aile et de stab sont debout sur leur face d'emplanture, les tronçons de fuselage debout (le nez pointe en haut) et les pattes debout sur leur pied.

| Pièces | Filament | Réglages |
|---|---|---|
| `aile_segment_*`, `aileron_*`, `stab_segment_*`, `profondeur_*` | PLA Aero | **1 paroi, 0 % de remplissage, 0 couche dessus/dessous**, détection des parois fines activée. Les parois, âmes et fourreaux sont déjà modélisés. Exception : `aile_segment_3_*` avec 2 couches dessus/dessous pour fermer la baie de servo. |
| `fuselage_avant`, `fuselage_arriere` | PLA Aero | 1 paroi, 0 % de remplissage, 0 couche dessus/dessous |
| `fuselage_nez` | PLA Aero | 1 paroi, 0 % de remplissage, **3 couches dessus** (la pointe est fermée) |
| `saumon_*`, `bloc_queue_*` | PLA Aero | 3 parois, 8 % gyroïde |
| `pylone_poutre_*` | PETG | 3 parois, 10 % gyroïde, bordure de 5 mm |
| `support_moteur` (×4) | PETG | 4 parois, 40 % gyroïde |
| `cloison_moteur` | PETG | 4 parois, 50 % |
| `plateau_electronique` | PETG | 3 parois, 30 % |
| `patte_atterrissage` (×4) | TPU 95A | 3 parois, 25 %, vitesse lente |

Conseils pour la A1 : son plateau bouge d'avant en arrière, donc place les pièces hautes et minces (segments d'aile) avec la corde dans l'axe avant-arrière. Ajoute une bordure (brim) de 5 mm et ralentis les parois extérieures à environ 150 mm/s. Imprime d'abord **un seul segment d'aile** pour valider le profil PLA Aero (température, moussage, masse ≈ 60 g).

Masse estimée de chaque pièce : `cad/out/masses.csv`. Pèse tes pièces : si elles sont nettement plus lourdes, ajuste le débit du PLA Aero avant d'imprimer le reste.

## Assemblage, dans l'ordre

1. **Aile** : coller les segments 1→4 de chaque côté à la CA en les enfilant sur un tube de 12 mm pour l'alignement. Coller le saumon. Poser les ailerons (segments 3 et 4, réunis par un jonc de 2 mm) avec une charnière en ruban sur l'extrados. Loger le servo d'aileron dans la baie du segment 3.
2. **Longerons** : le tube de 8 mm × 500 mm est collé à l'époxy dans les segments 2 à 4. Le tube de 12 mm et la goupille de 6 mm restent démontables.
3. **Pylônes** : les coller à l'époxy sous le segment 2, centrés à 330 mm de l'axe. Le trou de câble du pylône doit tomber sur celui de l'aile. Percer la poutre au même endroit (Ø 8 mm) pour passer les fils.
4. **Poutres** : enfiler dans l'ordre la patte avant, le support moteur avant, le pylône, la patte arrière, le support moteur arrière, puis coller le bloc de queue au bout. Distances depuis le bout avant du tube : moteur avant 22 mm, moteur arrière 722 mm.
5. **Empennage** : coller les 3 segments de stab sur le tube de 6 mm et le jonc de 3 mm, puis les insérer dans les deux blocs de queue. Coller les 3 profondeurs sur le jonc de 2 mm et les poser avec une charnière en ruban. Le servo de profondeur va dans la baie du bloc droit et ses fils passent dans la poutre.
6. **Fuselage** : coller la cloison moteur en PETG à l'époxy dans le bout arrière. Glisser le plateau électronique dans l'avant, puis coller l'avant et l'arrière (lèvre d'emboîtement). Le nez reste amovible, tenu par du ruban ou deux aimants. Le tube de Pitot sort par la pointe du nez.
7. **Électronique** : contrôleur de vol sur les entretoises 30,5 mm, récepteur sur les 20 mm, GPS collé sous le dessus de la partie arrière, loin des câbles de puissance. Les ESC VTOL sont fixés sur les poutres près des moteurs, à l'air.

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

1. Flasher ArduPlane sur le H743-WING (Mission Planner > Install Firmware).
2. Charger `ardupilot/huard_quadplane.param`, écrire, puis redémarrer **deux fois** : `Q_ENABLE` fait apparaître les autres paramètres.
3. Calibrer l'accéléromètre, le compas et la radio, et vérifier le capteur de vitesse.
4. Dans Mission Planner, ouvrir Motor Test et vérifier l'ordre et le sens de chaque moteur VTOL **sans hélices**.
5. Vérifier le sens des gouvernes en mode FBWA : quand on penche l'avion à droite, l'aileron droit doit se baisser.

## Plan d'essais en vol

1. **Sol** : CG à 62 mm (± 5 mm), failsafe radio testé, batterie chargée.
2. **Stationnaire** en QSTABILIZE puis QHOVER, à 2–3 m, par vent calme, dans un grand champ. Ensuite **QAUTOTUNE** axe par axe.
3. **Première transition** en QLOITER à 40 m ou plus, puis passer en FBWA : le propulseur accélère et les moteurs VTOL s'arrêtent vers 13 m/s. Repasser en QLOITER pour revenir.
4. **AUTOTUNE** avion, puis réglage de `TRIM_THROTTLE` et de `AIRSPEED_CRUISE`.
5. **Missions AUTO** avec `VTOL_TAKEOFF` et `VTOL_LAND`, en allongeant la durée par paliers de 10 minutes et en surveillant la consommation (mAh/km) dans les logs.

## Réglementation (Canada)

Au-dessus de 250 g, le drone doit être **immatriculé auprès de Transports Canada** et tu dois avoir au minimum le **certificat de pilote pour opérations de base**. Il faut voler à vue, sous 122 m, loin des aéroports et des personnes. Pour voler hors de portée visuelle, il faut un certificat et des autorisations supplémentaires. Vérifie les règles à jour sur le site de Transports Canada avant le premier vol.

## Limites connues et points à valider

- Les performances viennent d'un modèle simple (Cd0 estimé à 0,045). Seuls les logs des premiers vols donneront la vraie consommation.
- La masse des pièces imprimées est une estimation à partir du CAD. Pèse-les.
- Le profil NACA 4412 a été choisi parce qu'il est simple et tolérant. Un profil basse vitesse dédié (SD7062, S4083) pourrait ajouter quelques minutes d'autonomie.
- Le contrôle en lacet en stationnaire vient seulement du couple des moteurs. S'il est mou, incliner les supports moteurs de 3 à 5° (voir la documentation ArduPilot sur l'inclinaison des moteurs de quadplane).
- Les répartitions de sorties DShot dépendent des groupes de timers du H743-WING. Vérifier dans la documentation ArduPilot de la carte.
