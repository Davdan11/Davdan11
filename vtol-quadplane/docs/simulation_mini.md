# Vols simulés — Huard Mini

Généré par `simulation/vol_simule.py`. Le **vrai logiciel ArduPilot** (ArduPlane, compilé pour ordinateur : SITL) pilote un modèle de l'avion calculé à partir de nos cotes (`simulation/modele_sitl.py` : masse, aérodynamique, stabilité, moteurs, batterie), avec les paramètres de `ardupilot/huard_*.param`. Seules les sorties de la carte sont remappées sur celles du simulateur.

Modèle : 1.86 kg, marge statique 14%, gaz de stationnaire 59% (estimation du bilan, batterie affaissée), moteur propulsif 13 N au point fixe (nulle à 148 km/h, vitesse de pas de l'hélice).

## Résultats

| Scénario | Résultat | Durée | Croisière (air) | Vitesse mini en avion | Roulis max en avion | Gaz VTOL en stationnaire | Temps moteurs VTOL à fond | Posé à | Batterie consommée | Tension mini |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Mission complète, sans vent | ✅ posé | 4.7 min | 77 km/h | 53 km/h | 51° | 55% | 0% | 0.0 m du point prévu | 971 mAh | 15.4 V |
| Vent 25 km/h avec rafales | ✅ posé | 4.9 min | 79 km/h | 64 km/h | 52° | 63% | 0% | 0.1 m du point prévu | 1022 mAh | 15.3 V |
| Vent 32 km/h, rafales fortes (test de limite) | ✅ posé | 5.1 min | 80 km/h | 60 km/h | 53° | 60% | 0% | 0.2 m du point prévu | 1054 mAh | 15.3 V |
| Perte de la radio en croisière | ✅ posé | 2.3 min | 78 km/h | 54 km/h | 51° | 53% | 0% | 0.0 m du point prévu | 585 mAh | 15.8 V |
| Batterie presque vide pendant la mission | ✅ posé | 2.9 min | 79 km/h | 62 km/h | 51° | 64% | 0% | 0.2 m du point prévu | 740 mAh | 13.0 V |

## Paramètres ArduPilot

Paramètres de `ardupilot/huard_*.param` **inconnus** d'ArduPlane (version simulée) : `SERVO_BLH_MASK`, `SERVO_BLH_OTYPE` : ils règlent le DShot de la vraie carte et n'existent pas dans le simulateur. Tous les autres ont été acceptés.

![profils](images/simulation_profils_mini.png)

![trajectoires](images/simulation_trajectoires_mini.png)

## Déroulement (messages de l'autopilote)

### Mission complète, sans vent

-     0 s : Throttle failsafe off
-    24 s : Mission: 1 VTOLTakeoff
-    41 s : Mission: 2 WP
-    41 s : Transition started airspeed 0.0
-    45 s : Transition airspeed reached 14.5
-    49 s : Transition done
-    58 s : Reached waypoint #2 dist 25m
-    58 s : Mission: 3 WP
-    81 s : Reached waypoint #3 dist 40m
-    81 s : Mission: 4 WP
-   108 s : Reached waypoint #4 dist 68m
-   108 s : Mission: 5 WP
-   130 s : Reached waypoint #5 dist 69m
-   130 s : Mission: 6 LoitTurns
-   192 s : Mission: 7 WP
-   238 s : Reached waypoint #7 dist 70m
-   238 s : Mission: 8 VTOLLand
-   238 s : VTOL approach d=344.6
-   251 s : VTOL airbrake v=21.9 d=162 sd=164 h=41.7
-   252 s : VTOL position1 v=21.8 d=140.4 h=41.9 dc=16.1
-   262 s : VTOL position2 started v=4.8 d=9.9 h=43.1
-   264 s : Land descend started
-   293 s : Land final started
-   307 s : Land complete

### Vent 25 km/h avec rafales

-     0 s : Throttle failsafe off
-    24 s : Mission: 1 VTOLTakeoff
-    41 s : Mission: 2 WP
-    41 s : Transition started airspeed 0.0
-    45 s : Transition airspeed reached 14.2
-    49 s : Transition done
-    57 s : Reached waypoint #2 dist 29m
-    57 s : Mission: 3 WP
-    75 s : Reached waypoint #3 dist 51m
-    75 s : Mission: 4 WP
-    94 s : Reached waypoint #4 dist 90m
-    94 s : Mission: 5 WP
-   120 s : Reached waypoint #5 dist 59m
-   120 s : Mission: 6 LoitTurns
-   190 s : Mission: 7 WP
-   251 s : Reached waypoint #7 dist 56m
-   251 s : Mission: 8 VTOLLand
-   251 s : VTOL approach d=355.6
-   262 s : VTOL airbrake v=24.7 d=201 sd=201 h=41.1
-   263 s : VTOL position1 v=24.0 d=176.5 h=41.4 dc=16.1
-   274 s : VTOL position2 started v=4.9 d=10.0 h=41.7
-   277 s : Land descend started
-   305 s : Land final started
-   318 s : Land complete

### Vent 32 km/h, rafales fortes (test de limite)

-     0 s : Throttle failsafe off
-    24 s : Mission: 1 VTOLTakeoff
-    41 s : Mission: 2 WP
-    41 s : Transition started airspeed 0.0
-    45 s : Transition airspeed reached 14.8
-    49 s : Transition done
-    56 s : Reached waypoint #2 dist 32m
-    56 s : Mission: 3 WP
-    73 s : Reached waypoint #3 dist 51m
-    73 s : Mission: 4 WP
-    92 s : Reached waypoint #4 dist 89m
-    92 s : Mission: 5 WP
-   119 s : Reached waypoint #5 dist 56m
-   119 s : Mission: 6 LoitTurns
-   196 s : Mission: 7 WP
-   265 s : Reached waypoint #7 dist 51m
-   265 s : Mission: 8 VTOLLand
-   265 s : VTOL approach d=358.8
-   275 s : VTOL airbrake v=25.0 d=204 sd=206 h=41.9
-   276 s : VTOL position1 v=24.4 d=179.3 h=41.9 dc=16.1
-   287 s : VTOL Overshoot d=14.5 cs=5.4 yerr=60.0
-   288 s : VTOL position2 started v=4.4 d=9.7 h=42.7
-   290 s : Land descend started
-   319 s : Land final started
-   332 s : Land complete

### Perte de la radio en croisière

- radio coupée à t = 67 s
-     0 s : Throttle failsafe off
-    24 s : Mission: 1 VTOLTakeoff
-    41 s : Mission: 2 WP
-    41 s : Transition started airspeed 0.2
-    45 s : Transition airspeed reached 14.6
-    49 s : Transition done
-    56 s : Reached waypoint #2 dist 31m
-    56 s : Mission: 3 WP
-    68 s : Throttle failsafe on
-    68 s : RC Short Failsafe On
-    72 s : RC Long Failsafe On: switched to RTL
-   110 s : VTOL airbrake v=18.3 d=83 sd=84 h=44.6
-   112 s : VTOL position1 v=16.9 d=50.7 h=45.3 dc=14.1
-   115 s : VTOL position2 started v=6.3 d=9.6 h=54.5
-   121 s : Land descend started
-   149 s : Land final started
-   162 s : Land complete
-   163 s : PreArm: Radio failsafe on
-   163 s : PreArm: QRTL mode not armable

### Batterie presque vide pendant la mission

-     0 s : Throttle failsafe off
-    24 s : Mission: 1 VTOLTakeoff
-    41 s : Mission: 2 WP
-    41 s : Transition started airspeed 0.0
-    45 s : Transition airspeed reached 14.4
-    49 s : Transition done
-    57 s : Reached waypoint #2 dist 29m
-    57 s : Mission: 3 WP
-    76 s : Reached waypoint #3 dist 48m
-    76 s : Mission: 4 WP
-    92 s : Battery 1 is low 14.01V used 330 mAh
-   149 s : VTOL airbrake v=18.0 d=80 sd=81 h=42.8
-   151 s : VTOL position1 v=16.9 d=49.9 h=43.2 dc=14.1
-   154 s : VTOL position2 started v=6.4 d=9.7 h=52.7
-   160 s : Land descend started
-   186 s : Land final started
-   188 s : Battery 1 is critical 13.14V used 700 mAh
-   200 s : Land complete
-   200 s : PreArm: Battery 1 low voltage failsafe
-   200 s : PreArm: QLand mode not armable

## Limites de la simulation

- Le modèle aérodynamique est calculé, pas mesuré : il sera recalé avec les logs des vrais vols.
- Le moteur propulsif a une poussée constante (pas de baisse avec la vitesse) ; les capteurs sont parfaits (pas de vibrations). Le Mini vole sans capteur de vitesse, comme en vrai.
- Les réglages (PID) sont ceux d'origine d'ArduPilot ; QAUTOTUNE et AUTOTUNE restent à faire en vrai.
