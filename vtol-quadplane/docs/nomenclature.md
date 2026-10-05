# Liste d'achats : modèles exacts (Huard DFR)

Liens et fiches vérifiés le 4 octobre 2026. Les prix sont ceux affichés ce jour-là, en dollars américains (US$) sauf mention CA$. Ils n'incluent ni la livraison, ni les droits de douane, ni la TPS/TVQ. Le CAD (perçages, logements, centrage) est fait pour **ces modèles précis**. Si tu en changes un, dis-le-moi pour que j'ajuste les pièces.

## 1. Propulsion verticale (×4)

| Qté | Pièce | Lien | Prix | Notes pour le montage |
|---:|---|---|---:|---|
| 4 | **T-Motor MN4014 KV400** | [store.tmotor.com](https://store.tmotor.com/product/mn4014-kv400-motor-navigator-type.html) | 96,90 US$ ch. | 171 g, Ø44,7 mm. Base : 4 × M3 sur Ø25 mm (le support imprimé est percé à cette cote). 2,62 kg de poussée max avec une P15×5 en 6S |
| 2 paires | **T-Motor P15×5 carbone** (1 paire = 1 CW + 1 CCW) | [store.tmotor.com](https://store.tmotor.com/product/polish-carbon-fiber-15x5-prop.html) | 55,90 US$ la paire | Se fixent directement sur le dessus du MN4014. Vérifier à la réception que chaque paire contient bien une L et une R |
| 4 | **Holybro Tekko32 F4 45A** (AM32) | [holybro.com](https://holybro.com/products/tekko32-f4-45a-esc) | 82,59 US$ le lot de 4 | 34 × 17 × 4,5 mm. Souder le condensateur 330 µF fourni (obligatoire en 6S) |

T-Motor offre la livraison gratuite au-delà de 200 US$.

## 2. Propulsion avant

| Qté | Pièce | Lien | Prix | Notes |
|---:|---|---|---:|---|
| 1 | **SunnySky X2820 V3 KV570** | [sunnyskyusa.com](https://sunnyskyusa.com/products/sunnysky-x2820) | 44,95 US$ | Choisir la version **570 KV**. Base : 4 × M3 en croix 19 × 25 mm (la cloison est percée à cette cote). Arbre 5 mm, adaptateur M6 |
| 2 | **APC 10×7EP** (pousseur) | [innov8tivedesigns.com](https://innov8tivedesigns.com/apc-10x7e-pusher-propeller-black.html) | 3,69 US$ ch. | Utiliser la bague d'alésage de 6 mm fournie |
| 1 | **Holybro Tekko32 F4 45A** | [holybro.com](https://holybro.com/products/tekko32-f4-45a-esc) | 23,99 US$ | Même ESC que les moteurs VTOL : une seule configuration à apprendre |

## 3. Pilotage et navigation

| Qté | Pièce | Lien | Prix | Notes |
|---:|---|---|---:|---|
| 1 | **TBS Lucid H7 Wing** | [team-blacksheep.com](https://www.team-blacksheep.com/products/prod:lucid_h7_wing) | 74,95 US$ | 54 × 36 mm, fixation 30,5 × 30,5 mm. Capteur de courant 165 A. ArduPilot officiel (cible `TBS_LUCID_H7_WING`) |
| 1 | **Holybro Micro M10** GPS + compas, avec boîtier, IST8310 | [holybro.com](https://holybro.com/products/micro-m10-gps) | 27,99 US$ | 34 × 28 × 11 mm, 16 g. À coller à plat sur le dessus du fuselage milieu |
| 1 | **Matek ASPD-4525** capteur de vitesse + Pitot | [mateksys.com](https://www.mateksys.com/?portfolio=aspd-4525) · [ReadyMadeRC](https://www.readymaderc.com/products/details/matek-digital-airspeed-sensor-aspd-4525) | ≈ 50 US$ | Souvent en rupture de stock : surveiller. Mesurer le tube de Pitot reçu : le trou du nez fait Ø4,2 mm |
| 1 | **RadioMaster RP3 V2** ExpressLRS 2,4 GHz, version FCC | [radiomasterrc.com](https://www.radiomasterrc.com/products/rp3-expresslrs-2-4ghz-nano-receiver) | 19,99 US$ | Lien du pilote de sécurité |
| 3 | **EMAX ES08MD II** (servo 12 g, pignons métal) | [RaceDayQuads](https://www.racedayquads.com/products/emax-es08md-ii-12g-digital-metal-gear-servo) | 13,49 US$ ch. | 23 × 11,5 × 24 mm : logent dans les baies de l'aile et du bloc de queue |

**Pourquoi pas le Matek H743-WING ?** Matek a arrêté sa fabrication, ainsi que celle du H7A3-WING et du GPS M10Q-5883. Le TBS Lucid H7 Wing le remplace avec le même encombrement.

## 4. Caméra et vidéo en direct

| Qté | Pièce | Lien | Prix | Notes |
|---:|---|---|---:|---|
| 1 | **SIYI A8 mini** : nacelle 3 axes, 4K, zoom numérique 6×, sortie Ethernet, **pour commencer** | [shop.siyi.biz](https://shop.siyi.biz/products/siyi-a8-mini-gimbal-camera) | 257,40 US$ | 95 g. 4 × M2.5 en 30 × 25 mm (percé dans la selle). Même protocole ArduPilot et même vidéo que la ZT6 : tout le logiciel se met au point avec elle |
| (plus tard) | **SIYI ZT6** : 4K + **caméra thermique** 640 × 512 | [Aeromao (Canada)](https://aeromao.com/product/siyi-zt6-dual-sensor-4k-8mp-640-x-512-thermal-camera/) · [UAS Factory](https://shop.uasfactory.com/products/siyi-zt6-mini-dual-sensor-thermal-gimbal-camera) | 5 000 CA$ · 2 899 US$ | 197 g. 4 × M3 en 45 × 40 mm (aussi percé dans la selle). À acheter pour un projet pilote avec la police |
| 1 | **Raspberry Pi 5 4 Go** | [CanaKit](https://www.canakit.com/raspberry-pi-5-4gb.html) · [PiShop.ca](https://www.pishop.ca/product/raspberry-pi-5-4gb/) | 110 US$ · 153,95 CA$ | Entretoises 58 × 49 mm M2.5 sur le plateau compagnon |
| 1 | **Raspberry Pi Active Cooler** | [PiShop.ca](https://www.pishop.ca/product/raspberry-pi-active-cooler/) | 7 CA$ | |
| 1 | **Waveshare SIM7600G-H 4G DONGLE** | [waveshare.com](https://www.waveshare.com/sim7600g-h-4g-dongle.htm) | 101,99 US$ | Couvre les bandes LTE de Bell, Rogers et Telus (B2, B4, B5, B7, B12, B13, B66). Sortir la carte du boîtier pour gagner du poids |
| 2 | **Taoglas FXUB63** antenne LTE souple | [taoglas.com](https://www.taoglas.com/product/fxub63-ultra-wide-band-flex-antenna/) | ≈ 10 US$ | Collée à l'intérieur de la coque. Vérifier le connecteur du modem (adaptateur u.FL vers SMA au besoin) |
| 2 | **Holybro UBEC 5A** (un pour le Pi, un pour le modem) | [holybro.com](https://holybro.com/products/ubec-5a-3-14s) | 20,99 US$ ch. | Dans `config.txt` du Pi, mettre `usb_max_current_enable=1` pour alimenter le modem |
| 1 | Carte SIM données (Bell, Rogers, Telus ou revendeur) | — | / mois | Environ 1 à 2 Go par heure de vidéo |

## 5. Énergie

| Qté | Pièce | Lien | Prix | Notes |
|---:|---|---|---:|---|
| 1 | **GAONENG GNB 6S 13500 mAh 10C** (Li-ion 6S3P, cellules Molicel P45B) | [gaoneng.shop](https://www.gaoneng.shop/products/gaoneng-gnb-6s-22.2v-13500mah-10c-xt60-li-ion-battery-made-with-molicel-21700-p45b) | 283 US$ | 1337 g, 130 × 81 × 65 mm : le plateau est fait pour. Prise XT60. Livraison depuis la Chine en 2 à 3 semaines ; vérifier la livraison au Canada |
| (option) | Cellules Molicel P45B pour un pack sur mesure (18 cellules) | [RaceDayQuads (en stock)](https://www.racedayquads.com/products/molicel-p45b-21700-4500mah-45a-3-7v-li-ion-battery-2pcs) | 25,99 US$ les 2 | Assemblage par soudure par points chez un pro, par exemple [BBM Battery (Mississauga)](https://bbmbattery.ca/pages/custom-battery-packs) |
| 1 | **ToolkitRC M8AC** chargeur 600 W, 1 à 8S, branchement direct au 120 V | [RaceDayQuads](https://www.racedayquads.com/products/toolkitrc-m8ac-600w-20a-1-8s-ac-dc-smart-charger-xt60) | 113,99 US$ | Mode Li-ion. Charger à 13 A au plus (1C) |

## 6. Carbone

| Qté | Pièce | Lien | Prix | Usage |
|---:|---|---|---:|---|
| 3 | Tube 16 × 14 × 1000 mm | [Amazon.ca](https://www.amazon.ca/High-Strength-Glossy-Carbon-Fiber-16x14x1000mm/dp/B0F3CNHP25) · [Rock West 46705 (2 m, à couper ; 2 tubes donnent les 3 longueurs)](https://www.rockwestcomposites.com/46705.html) | ≈ 69 CA$ · 102,99 US$ | 2 poutres VTOL + le longeron principal (un 12 mm serait trop faible : voir docs/essais_virtuels.md) |
| 1 | Tube 8 × 6 × 1000 mm | [Amazon.ca](https://www.amazon.ca/Abesterxox-Carbon-Length-Airplane-8x6x1000mm/dp/B0CP3SSSSK) · [Rock West T-RND-314-L39](https://www.rockwestcomposites.com/t-rnd-314-l39.html) | — · 23,99 US$ | Longerons extérieurs (2 × 500 mm) |
| 1 | Tube 6 × 4 × 1000 mm | [Amazon.ca (WHABEST)](https://amazon.ca/WHABEST-Carbon-1000mm-Composite-Material/dp/B08DNNVPZP) | — | Longeron du stab (couper à 720 mm) |
| 1 | Jonc plein 6 mm × 2 m | [Rock West R-RND-236](https://www.rockwestcomposites.com/r-rnd-236.html) | 41,99 US$ | Goupille d'aile (300 mm) |
| 1 | Jonc plein 3 mm × 2 m | [Rock West R-RND-118](https://www.rockwestcomposites.com/r-rnd-118.html) | 7,49 US$ | Jonc arrière du stab (720 mm) |
| 1 | Jonc plein 2 mm × 2 m | [Rock West R-RND-079](https://www.rockwestcomposites.com/r-rnd-079.html) | 5,49 US$ | Raidisseurs d'ailerons et de profondeur |

Les pages Amazon.ca n'ont pas pu être ouvertes (CAPTCHA) : liens trouvés en recherche, prix non confirmés. **Mesure le diamètre réel des tubes reçus** : s'il diffère de plus de 0,2 mm, change `POUTRE_D` ou `JEU_TUBE` dans `cad/params.py` et régénère les pièces.

## 7. Filament (Bambu Lab, boutique Canada)

| Qté | Filament | Lien | Pièces |
|---:|---|---|---|
| 2 | **PLA Aero** | [ca.store.bambulab.com](https://ca.store.bambulab.com/products/pla-aero) | Ailes, fuselage, stab, blocs de queue. À sécher avant usage |
| 1 | **PETG HF** | [ca.store.bambulab.com](https://ca.store.bambulab.com/products/petg-hf) | Supports moteurs, pylônes, cloison, selle, plateaux |
| 1 | **TPU 95A HF** | [ca.store.bambulab.com](https://ca.store.bambulab.com/products/tpu-95a-hf) | Pattes d'atterrissage (pas compatible AMS : charger à la main) |

## 8. Quincaillerie et câblage (liste complète, vérifiée pièce par pièce)

| Où | Quoi | Qté |
|---|---|---:|
| Supports moteurs VTOL | Vis M3 × 16 + écrous M3 (serrage des colliers) | 8 + 8 |
| | Vis M3 × 8 (vis de coin platine → bride, passées par-dessous) | 16 |
| | Vis M3 pour les moteurs (4 mm de platine + profondeur filetée du moteur − 0,5 mm ; souvent × 6 ou × 8) | 16 |
| Moteur propulsif | Vis M3 (souvent fournies) pour le fixer sur la cloison | 4 |
| | Vis M2 × 6 autotaraudeuses (cloison → fuselage, radiales) | 3 |
| Ailes | Vis nylon M3 × 40 + écrou nylon (retenue de chaque aile sur le longeron) | 2 + 2 |
| Pylônes (vissés sous l'aile) | Inserts laiton M3 **courts : longueur 4 mm** (Ø ext. 4,5 à 5 mm) ; vis M3 **tête fraisée** × 25 (avant) et × 20 (arrière) | 4 ; 2 + 2 |
| Servos d'aileron | Vis M2 × 6 autotaraudeuses (trappes) | 4 |
| Servo de profondeur | Vis fournies avec le servo (oreilles) | 2 |
| Trappe d'accès | Vis M2 × 6 autotaraudeuses | 2 |
| Contrôleur de vol | Inserts laiton M3 (Ø4 × 5,7) + vis M3 × 10 en nylon | 4 + 4 |
| Raspberry Pi | Inserts laiton M2.5 + vis M2.5 × 6 | 4 + 4 |
| Nacelle | Vis M3 × 35 tête plate (selle → plateau) ; vis M2.5 × 8 (A8 mini) ou M3 × 8 (ZT6) | 2 ; 4 |
| Gouvernes | Tringles acier 1,5 mm + chapes réglables + bagues de serrage (2 ailerons, 1 profondeur) | 3 |
| | Ruban de charnière (Blenderm ou équivalent) | 1 rouleau |
| Rallonges | **Rallonges de servo 50 cm** (2 servos d'aileron) | 2 |
| | **Rallonges de servo 80 cm** (servo de profondeur, et signal des 4 ESC VTOL qui passent par la poutre et l'aile) | 5 |
| Puissance | Câble silicone **12 AWG rouge et noir, 3 m de chaque** (une paire par côté : fuselage → aile → poutre, Y vers les 2 ESC) ; **connecteurs balles 4 mm** (4 paires) | 2 × 3 m |
| | Câble silicone 16 AWG rouge et noir, 1 m (ESC du propulseur) ; prises XT60, gaine thermo | — |
| Batterie | 2 sangles de 20 mm, velcro adhésif | — |
| Divers | Colle CA moyenne + activateur, époxy 30 min, mousse adhésive 1 mm (sous le GPS dans son berceau) ; 2 vis M2 × 5 autotaraudeuses (berceau du GPS), colliers de serrage | — |

## Ce qu'il te faut peut-être déjà

- Une radiocommande ExpressLRS 2,4 GHz (RadioMaster Pocket ou Boxer, par exemple)
- Mission Planner (gratuit, Windows)

## Budget

| | US$ |
|---|---:|
| Propulsion (verticale + avant) | ≈ 660 |
| Pilotage et navigation | ≈ 215 |
| Vidéo avec l'A8 mini (Pi, modem, antennes, BEC) | ≈ 540 |
| Batterie + chargeur | ≈ 400 |
| Carbone | ≈ 230 |
| Filament et quincaillerie | ≈ 190 |
| **Total pour commencer** | **≈ 2 250 US$, soit environ 3 100 CA$** avant taxes et livraison |
| Passage à la ZT6 thermique plus tard | + 2 900 US$ à 5 000 CA$ |
