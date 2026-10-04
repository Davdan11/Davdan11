# Concept : drone premier intervenant pour la police

## L'idée

Lors d'un appel 911 (accident, personne disparue, incendie, poursuite), un drone part automatiquement d'une station proche, arrive en quelques minutes, tourne au-dessus des lieux et transmet l'image en direct aux policiers. Ceux-ci voient la situation **avant d'arriver** : nombre de véhicules, blessés, danger, circulation, suspect qui s'enfuit.

Le concept existe déjà aux États-Unis sous le nom de « Drone as First Responder » (DFR), surtout avec des multirotors qui volent 20 à 40 minutes. Le Huard DFR est un **VTOL à aile** : il décolle et se pose à la verticale comme un multirotor, mais vole comme un avion. Il va donc plus vite et plus loin, et **une seule station couvre un rayon d'environ 15 km au lieu de 3 à 5 km**.

## Déroulement d'une intervention

```
 1. Appel 911 ─► le répartiteur clique sur l'adresse dans la carte ─► « Envoyer le drone »
 2. Le logiciel au sol envoie la mission au drone le plus proche (par 4G)
 3. Décollage vertical automatique depuis la station (≈ 30 s)
 4. Transition en vol d'avion, transit à 90 km/h (10 km en ≈ 7 min)
 5. Cercle de 120 m au-dessus des lieux, caméra pointée automatiquement sur les coordonnées
 6. Vidéo en direct ─► tablettes des patrouilleurs + écran du centre de répartition
    Un policier peut prendre la main sur la caméra (zoom, thermique, suivi)
 7. Fin de mission ou batterie basse ─► retour à la station, atterrissage vertical
 8. Recharge ou échange de batterie, prêt pour la prochaine mission
```

## Les quatre morceaux du système

### 1. Le drone (ce dépôt)

| Fonction | Choix |
|---|---|
| Plateforme | Quadplane imprimé en 3D, 1,8 m, ≈ 4,7 kg |
| Pilote automatique | ArduPilot : décollage et atterrissage verticaux, missions, retour automatique, failsafes |
| Caméra | Nacelle stabilisée zoom + thermique, pointée par ArduPilot (mode « ROI » vers les coordonnées de l'appel) |
| Ordinateur de bord | Raspberry Pi 5 : relaie la vidéo et la télémétrie par 4G |
| Liens | 4G/LTE principal (vidéo + commande), ExpressLRS en secours pour le pilote de sécurité |

### 2. La chaîne vidéo en direct

```
 Nacelle ──Ethernet/RTSP──► Raspberry Pi ──4G (SRT ou WebRTC)──► Serveur vidéo ──► navigateurs
 (H.265, 1080p)              (relais, pas de                     (MediaMTX,          (tablettes,
                              réencodage)                         infonuagique ou     centre 911)
                                                                  serveur du poste)
```

- **Débit** : 2 à 4 Mbit/s suffisent pour du 1080p en H.265, soit environ 1 à 2 Go par heure.
- **Délai** visé : moins d'une seconde avec SRT ou WebRTC.
- **Logiciel** : MediaMTX (libre) côté serveur. Les policiers ouvrent une simple page web, sans application à installer.
- **Sécurité** : flux chiffré, accès par compte, enregistrement de chaque mission pour la preuve et la reddition de comptes.

### 3. Le logiciel au sol

- **Commande** : la télémétrie MAVLink passe aussi par la 4G, via mavlink-router sur le Pi et un serveur relais. Mission Planner ou QGroundControl suffisent pour la mise au point.
- **Pour le répartiteur**, une page web simple à développer : carte, bouton « envoyer », état du drone (position, batterie, temps restant sur place) et vidéo intégrée.
- **Pilote de sécurité** : la réglementation exige une personne responsable du vol. Elle surveille depuis le centre et peut reprendre la main ou ordonner le retour.

### 4. La station

C'est la partie la plus exigeante. Il faut un abri qui protège le drone de la pluie et du froid, avec une recharge et une connexion réseau. On peut y aller par étapes :

| Étape | Station | Commentaire |
|---|---|---|
| Démo | Aucune : drone dans le véhicule de patrouille ou au poste | Un policier le pose au sol et lance la mission de la tablette |
| Pilote | Abri simple sur un toit de poste, porte motorisée, échange manuel de batterie | Le drone attend batterie chargée, prêt en moins d'une minute |
| Déploiement | Station automatique (toit ouvrant, recharge par contacts, chauffage) | Projet en soi ; l'envergure de 1,8 m impose une station d'environ 2 × 1,3 m |

Pour une station compacte, une version future pourrait avoir des ailes repliables.

## Couverture d'un territoire

Avec un transit à 90 km/h et environ 36 minutes sur place à 15 km, une station couvre environ 700 km². À titre d'exemple, 3 ou 4 stations couvriraient l'essentiel d'une MRC rurale ; en ville, les distances sont plus courtes et le temps sur place plus long.

## Réglementation et acceptabilité

- **Transports Canada** : le vol hors de portée visuelle (BVLOS) au-dessus de routes et de personnes demande, au-delà des certificats de pilote, une autorisation spéciale (certificat d'opérations aériennes spécialisées, COAS) avec une analyse de risque. Les règles évoluent : à vérifier au moment du projet pilote, idéalement avec le service de police comme exploitant.
- **Fiabilité exigée** : parachute, double lien, surveillance de l'état du drone, procédures et carnets de vol. Il faudra des centaines d'heures d'essais documentés.
- **Vie privée** : Loi 25 au Québec et Charte. Il faut des règles claires sur quand on filme, qui voit les images et combien de temps on les garde. C'est ce qui rend le projet acceptable pour la population.
- **Espace aérien** : coordination avec NAV CANADA près des aéroports et des hélicoptères (ambulances aériennes).

## Feuille de route proposée

| Étape | Contenu | Résultat |
|---|---|---|
| 1. Plateforme | Construire le Huard DFR, vols à vue : stationnaire, transitions, accordage | Drone fiable en vol manuel et automatique |
| 2. Mission | Missions AUTO : décollage, transit, cercle sur un point, retour, atterrissage | Mission complète sans toucher à la radio |
| 3. Vidéo | Caméra simple puis nacelle, chaîne 4G vers une page web | Vidéo en direct, délai < 1 s |
| 4. Démonstration | Page « répartiteur » : clic sur la carte → drone sur place, vidéo en direct | Démo à présenter à un service de police ou une municipalité |
| 5. Projet pilote | Avec le partenaire : COAS, procédures, redondances, essais documentés | Premières interventions réelles encadrées |

## Prochains développements possibles dans ce dépôt

- Script Raspberry Pi : relais vidéo SRT/WebRTC et mavlink-router, avec reconnexion automatique.
- Page web du répartiteur : carte, envoi de mission, vidéo.
- Logement de parachute dans le fuselage.
- Ailes repliables pour une station plus compacte.
