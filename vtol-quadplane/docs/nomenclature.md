# Nomenclature : pièces à acheter (Huard DFR, 6S)

Les prix sont des ordres de grandeur en dollars canadiens (2026), à vérifier au moment de commander. Les modèles cités sont des exemples : un équivalent aux mêmes caractéristiques fait l'affaire.

## Propulsion VTOL (×4)

| Pièce | Qté | Caractéristiques à respecter | Exemple | Prix ≈ |
|---|---:|---|---|---:|
| Moteur | 4 | Taille 3515 à 4010, 350 à 450 KV, 6S. **Au moins 2,3 kg de poussée max avec une hélice de 13 po** (vérifier la table de poussée du fabricant) | T-Motor MN3515 KV400 ou équivalent | 400 $ |
| Hélice | 4 | 13 × 4,4, deux CW et deux CCW | T-Motor / APC 13x4.4 MR | 45 $ |
| ESC | 4 | 40 A, 6S, DShot, firmware AM32 ou BLHeli_32 | ESC simple 40 A 6S AM32 | 120 $ |

## Propulsion en croisière

| Pièce | Qté | Caractéristiques à respecter | Exemple | Prix ≈ |
|---|---:|---|---|---:|
| Moteur propulsif | 1 | Taille 2814, 650 à 750 KV, 6S, perçage 16/19 mm | SunnySky X2814 700KV ou équivalent | 55 $ |
| Hélice | 2 | 10 × 7, électrique, version pousseur (P) | APC 10x7EP | 20 $ |
| ESC | 1 | 50 A, 6S | ESC 50 A | 40 $ |

## Pilotage et navigation

| Pièce | Qté | Rôle | Exemple | Prix ≈ |
|---|---:|---|---|---:|
| Contrôleur de vol | 1 | ArduPilot, capteur de courant intégré, 13 sorties | Matek H743-WING V3 | 120 $ |
| GPS + compas | 1 | Navigation, retour au point de départ | Matek M10Q-5883 | 45 $ |
| Capteur de vitesse air | 1 | **Indispensable** pour les transitions | Matek ASPD-4525 + tube de Pitot | 50 $ |
| Récepteur | 1 | Lien de secours du pilote de sécurité | ExpressLRS 2,4 GHz (RadioMaster RP3) | 25 $ |
| Servos | 3 | 2 ailerons + 1 profondeur, 9 g, pignons métal, numériques | EMAX ES08MD II | 45 $ |

## Mission : caméra et vidéo en direct

| Pièce | Qté | Rôle | Exemple | Prix ≈ |
|---|---:|---|---|---:|
| Nacelle stabilisée | 1 | Caméra zoom + caméra thermique sur 3 axes, sortie IP (Ethernet), contrôlable par ArduPilot. **Masse visée : 300 g au plus** | Nacelle SIYI double capteur ou équivalent (vérifier masse et compatibilité ArduPilot) | 900 à 1 500 $ |
| Ordinateur de bord | 1 | Reçoit la vidéo de la nacelle et la télémétrie, envoie tout par 4G | Raspberry Pi 5 (4 Go) + refroidisseur | 110 $ |
| Modem cellulaire | 1 | Lien 4G/LTE, bandes canadiennes | Clé USB ou module LTE Cat 4 (Quectel EC25 ou équivalent) | 80 $ |
| Antennes LTE | 2 | Montées sur le dessus du fuselage | Antennes souples LTE | 20 $ |
| Carte SIM données | 1 | Forfait données canadien (≈ 1 à 2 Go par heure de vidéo) | — | /mois |
| BEC 5 V 5 A | 1 | Alimentation du Raspberry Pi | Matek UBEC Duo ou équivalent | 20 $ |
| Câble Ethernet court | 1 | Nacelle vers Raspberry Pi | — | 10 $ |

Pour les premiers essais, une petite caméra USB ou RTSP sans stabilisation (≈ 80 $) suffit à mettre au point la chaîne vidéo avant d'acheter la nacelle.

## Énergie

| Pièce | Qté | Notes | Prix ≈ |
|---|---:|---|---:|
| Batterie Li-ion 6S3P 21700 | 1 | 18 cellules Molicel P45B (4,5 Ah, 45 A), soit 13,5 Ah et 290 Wh. Pack assemblé et soudé par points, câble 10 AWG, prise XT90. Dimensions visées : 150 × 70 × 68 mm au plus | 300 $ |
| Batterie de mise au point 6S2P | 1 | Optionnelle : plus légère pour les premiers vols (+150 g de lest dans le nez) | 200 $ |
| Chargeur 6S | 1 | 200 W ou plus (ISDT, ToolkitRC…) | 120 $ |
| Connecteurs et fils | — | XT90, XT60, câble silicone 12 AWG et 20 AWG, fils de servo, gaine | 50 $ |

## Carbone

| Pièce | Qté | Usage | Prix ≈ |
|---|---:|---|---:|
| Tube 16 × 14 × 1000 mm | 2 | Poutres VTOL | 50 $ |
| Tube 12 × 10 × 1000 mm | 1 | Longeron principal (traverse le fuselage) | 20 $ |
| Tube 8 × 6 × 1000 mm | 1 | Longerons extérieurs (2 × 500 mm) | 12 $ |
| Jonc plein 6 mm × 300 mm | 1 | Goupille d'incidence de l'aile | 6 $ |
| Tube 6 × 4 × 700 mm | 1 | Longeron du stabilisateur | 8 $ |
| Jonc 3 mm × 700 mm | 1 | Jonc arrière du stabilisateur | 4 $ |
| Jonc 2 mm × 1000 mm | 2 | Raidisseurs d'ailerons et de profondeur | 6 $ |

## Filament (Bambu Lab A1)

| Filament | Quantité | Pièces |
|---|---|---|
| Bambu PLA Aero (PLA allégé moussant) | 2 bobines | Ailes, ailerons, saumons, fuselage, stabilisateur, profondeur, blocs de queue |
| PETG | 1 bobine | Pylônes, supports moteurs, cloison moteur, selle de nacelle, plateaux |
| TPU 95A | 250 g | Pattes d'atterrissage |

## Petite quincaillerie

- Vis M3 : 8 × 20 mm pour les colliers des supports moteurs, 4 × 25 mm à tête plate pour la selle de nacelle, plus les vis des moteurs (fournies)
- 4 amortisseurs caoutchouc pour la nacelle (souvent fournis avec)
- 3 guignols de commande, 3 tringles de 1,5 mm avec chapes
- Ruban adhésif renforcé ou ruban de charnière (Blenderm) pour les ailerons et la profondeur
- Colle cyanoacrylate (CA) moyenne + activateur, époxy 30 min pour les pylônes et la cloison
- Velcro et 2 sangles de batterie de 20 mm

## Ce qu'il te faut peut-être déjà

- Radiocommande ExpressLRS (RadioMaster Pocket ou Boxer) : 100 à 200 $
- Mission Planner (gratuit, Windows) ou QGroundControl

**Total approximatif sans radiocommande : environ 2 000 $ CA sans la nacelle, 2 900 à 3 500 $ CA avec une nacelle zoom + thermique.**
