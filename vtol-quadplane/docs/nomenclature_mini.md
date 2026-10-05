# Liste d'achats : Huard Mini (version d'essai, 1,2 m)

Le Mini a la même architecture que le Huard DFR, en plus petit et avec des pièces de drone FPV bon marché. Il sert à apprendre la construction, les réglages ArduPilot, les transitions et les missions automatiques avant de bâtir le grand.

Liens et fiches vérifiés le 4 octobre 2026. Prix en dollars canadiens (CA$), sauf mention US$, sans taxes ni livraison. La plupart des pièces viennent de boutiques canadiennes : Rotor Village, Epic FPV et Drone Dynamics. Le CAD est percé pour **ces modèles précis**.

## Moteurs et hélices

| Qté | Pièce | Lien | Prix | Notes pour le montage |
|---:|---|---|---:|---|
| **5** | **Emax ECO III 2807 1300KV** | [Rotor Village](https://rotorvillage.ca/emax-eco-iii-series-2807-1300kv-motor/) | 27,99 $ ch. | 4 moteurs pour la verticale + 1 pour l'avant (le même modèle). Ø34,8 mm, 4 × M3 en carré de 19 × 19 mm : supports et cloison percés à cette cote |
| 4 paires | **HQProp Cine7 7×4×3** (1 CW + 1 CCW par paire) | [Rotor Village](https://rotorvillage.ca/hqprop-cine7-7x4x3-1cw-1ccw/) | 5,79 $ la paire | 2 paires pour voler, 2 de rechange |
| 2 | **Gemfan Vortex 7×6E** (hélice avant) | [Epic FPV](https://epicfpv.ca/products/gemfan-vortex-7x6e-electric-propeller-glass-fiber-nylon-eal) | 5,99 $ | Monter l'hélice à l'envers (face imprimée vers le nez) et inverser le sens du moteur dans l'ESC |
| 5 | **Skystars Talon32 40A AM32** | [Rotor Village](https://rotorvillage.ca/skystars-talon32-40a-am32-esc/) | 18,99 $ ch. | 37,5 × 9 × 5,8 mm. Un par moteur, fixé sur la poutre. DShot, compatible ArduPilot |

## Pilotage

| Qté | Pièce | Lien | Prix | Notes |
|---:|---|---|---:|---|
| 1 | **AtomRC F405 NAVI** | [Drone Dynamics](https://dronedynamics.ca/products/atomrc-f405-navi-fixed-wing-flight-controller) | 59,99 $ | 50 × 30 mm, trous Ø3 en 30 × 24 mm (plateau percé à cette cote). Capteur de courant 120 A. ArduPilot officiel, cible `AtomRCF405NAVI`. Exactement 8 sorties : 4 moteurs + 1 propulseur + 3 servos |
| 1 | **MicoAir M10G-5883** GPS + compas | [Epic FPV](https://epicfpv.ca/products/micoair-m10g-5883-gps) | 21,99 $ | 20 × 20 × 8 mm, 7 g |
| 1 | **RadioMaster RP1 V2** ExpressLRS 2,4 GHz | [Rotor Village](https://rotorvillage.ca/radiomaster-rp1-v2-tcxo-expresslrs-2-4ghz-receiver/) | 27,99 $ | À brancher sur un vrai port série (UART), pas sur la broche SBUS |
| 3 | **JX PDI-1109MG** servo 10 g, pignons métal | [Rotor Village](https://rotorvillage.ca/jx-pdi-1109mg-9g-metal-gear-digital-servo/) | 9,99 $ ch. | 23,2 × 12 × 24,8 mm : rentre dans les baies |

**Capteur de vitesse : pas au début.** ArduPilot sait voler en quadplane sans lui, en estimant la vitesse. On pourra en ajouter un plus tard, par exemple le [Holybro MS4525DO](https://epicfpv.ca/products/holybro-standard-precision-digital-airspeed-sensors-ms4525do-pt60-pitot-tube) à environ 107 $.

## Batterie

| Qté | Pièce | Lien | Prix | Notes |
|---:|---|---|---:|---|
| 1 | **CNHL G+Plus 4S 4000 mAh 70C** | [chinahobbyline.com](https://chinahobbyline.com/products/cnhl-gplus-series-4000mah-14-8v-4s-70c-lipo-battery-with-xt90-plug) | 41,99 US$ | 147 × 51 × 28 mm, 416 g. Prise XT90 : la remplacer par une XT60, ou prendre un adaptateur |
| (option) | GNB 4S 4000 mAh 70C | [Epic FPV](https://epicfpv.ca/products/gaoneng-gnb-4s-14-8v-4000mah-70c-lipo-battery-xt60) | 78,99 $ | En stock au Canada, prise XT60. 139 × 43 × 26 mm |

## Carbone (carbonfibertubes.net, prix en US$)

| Qté | Pièce | Usage | Prix |
|---:|---|---|---:|
| 2 | Tube 12 × 10 × 1000 mm | Poutres (2 × 610 mm) | 20,79 US$ les 2 |
| 1 | Tube 10 × 8 × 1000 mm | Longeron principal (720 mm) | 11,55 US$ |
| 1 | Tube 6 × 4 × 1000 mm | Longerons extérieurs (2 × 310 mm) | 9,82 US$ |
| 1 | Tube 5 × 3 × 1000 mm | Longeron du stab (420 mm) | 9,82 US$ |
| 2 | Jonc plein Ø4 | Goupille d'aile (200 mm) | 5,50 US$ |
| 5 | Jonc plein Ø2 (et un Ø1,5 si offert) | Stab, ailerons, profondeur | 10,45 US$ |

Boutique : [carbonfibertubes.net](https://carbonfibertubes.net). La livraison vers le Canada n'a pas été vérifiée. Mesure les tubes reçus : si le diamètre diffère, change `POUTRE_D` ou `JEU_TUBE` dans `cad/params_mini.py` et régénère les pièces.

## Filament

Environ 1 bobine de [PLA Aero](https://ca.store.bambulab.com/products/pla-aero), ¼ de bobine de [PETG HF](https://ca.store.bambulab.com/products/petg-hf) et 100 g de [TPU 95A HF](https://ca.store.bambulab.com/products/tpu-95a-hf).

## Quincaillerie et câblage (≈ 60 à 80 $, liste complète vérifiée pièce par pièce)

| Où | Quoi | Qté |
|---|---|---:|
| Supports moteurs VTOL | Vis M3 × 16 + écrous M3 (colliers) ; vis M3 × 8 (vis de coin) | 8 + 8 ; 16 |
| Moteurs (5) | Vis M3 × 6 (moteur → platine ou cloison ; vérifier la profondeur filetée) | 20 |
| Cloison du propulseur | Vis M2 × 6 autotaraudeuses, radiales | 3 |
| Ailes | Vis nylon M3 × 30 + écrou nylon (retenue sur le longeron) | 2 + 2 |
| Pylônes (vissés sous l'aile) | Inserts laiton M3 **courts : longueur 4 mm** (Ø ext. 4,5 à 5 mm), dans un assortiment d'inserts M3 ; vis M3 **tête fraisée** × 20 (avant) et × 16 (arrière) | 4 ; 2 + 2 |
| Servos d'aileron / trappe d'accès | Vis M2 × 6 autotaraudeuses | 4 + 2 |
| Servo de profondeur | Vis fournies avec le servo | 2 |
| Contrôleur de vol | Inserts laiton M3 (Ø4 × 5,7) + vis M3 × 10 nylon | 4 + 4 |
| Gouvernes | Tringles acier 1,5 mm + chapes + bagues de serrage ; ruban de charnière | 3 |
| Rallonges | **Rallonges de servo 30 cm** (2 ailerons, 1 profondeur) et **40 cm** (signal des 4 ESC VTOL) | 3 + 4 |
| Puissance | Câble silicone **14 AWG rouge et noir, 2 m de chaque** (une paire par côté : fuselage → aile → poutre, Y vers les 2 ESC) ; **connecteurs balles 3,5 mm** (4 paires) ; 5 condensateurs 220–470 µF 35 V (un par ESC), prises XT60, gaine thermo | — |
| Signaux | 4 rallonges de servo 50 cm (une par côté pour les 2 ESC, aileron, profondeur) + 2 de 30 cm | 6 |
| Batterie | 2 sangles de 20 mm, velcro adhésif | — |
| Divers | Colle CA + activateur, époxy, mousse adhésive 1 mm (sous le GPS dans son berceau) ; 2 vis M2 × 5 autotaraudeuses (berceau du GPS), colliers de serrage | — |

## Si tu ne les as pas déjà

| Pièce | Lien | Prix |
|---|---|---:|
| Radiocommande **RadioMaster Pocket ELRS** | [Rotor Village](https://rotorvillage.ca/radiomaster-pocket-transmitter-elrs-charcoal-edition/) | ≈ 96 $ |
| Chargeur **ToolkitRC M6AC** (branchement direct au 120 V) | [Rotor Village](https://rotorvillage.ca/toolkitrc-m6ac-1-6s-15a-charger/) | 88,99 $ |

## Budget

| | CA$ |
|---|---:|
| Moteurs (5) | 140 |
| Hélices | 35 |
| ESC (5) | 95 |
| Contrôleur de vol | 60 |
| GPS + récepteur | 50 |
| Servos (3) | 30 |
| Batterie | 58 |
| Carbone | ≈ 95 |
| Filament, quincaillerie et câblage | ≈ 130 |
| **Total de l'avion** | **≈ 690 $** avant taxes et livraison |
| Radiocommande + chargeur, si tu ne les as pas | + 185 $ |

Tout ce matériel resservira : la radiocommande, le chargeur et le savoir-faire passent au grand Huard DFR.
