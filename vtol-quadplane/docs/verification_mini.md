# Vérification d'intégration — Huard Mini

Généré par `cad/verification.py` : l'avion est monté en 3D avec toutes les pièces imprimées et toutes les pièces achetées à leurs cotes (moteurs, hélices, servos, ESC, batterie, contrôleur de vol, GPS, tubes carbone), puis chaque contrôle est fait par calcul.

**Résultat : 1 contrôle(s) en échec.**


## 1. Collisions entre éléments

❌ 78 éléments montés (27 modèles de pièces imprimées + pièces achetées) : 5 collision(s)
   - aile_segment_1_d ↔ pylone_poutre_d : 5.1 mm³
   - aile_segment_1_g ↔ pylone_poutre_g : 5.1 mm³
   - aile_segment_2_d ↔ cadre_servo_aile_d : 1.6 mm³
   - aile_segment_2_g ↔ cadre_servo_aile_g : 1.6 mm³
   - fuselage_queue ↔ esc_propulseur : 188.2 mm³

## 2. Débattement des gouvernes (±25°)

✅ ailerons, profondeurs, guignols et joncs tournent librement de -25° à +25°

## 3. Hélices

✅ les 4 disques d'hélices VTOL (7 po) et le disque propulsif (7 po) ne touchent rien (aile, stab, dérives, fuselage, autres hélices)

## 4. Garde au sol

✅ sol à z = -129 mm ; plus bas élément : helice_propulseur à 36 mm du sol ; fuselage_avant 65 mm ; fuselage_milieu 65 mm ; fuselage_queue 65 mm

## 5. Chemins libres (câbles et tubes)

✅ conduit de câbles de l'aile (Ø7 mm) libre du flanc du fuselage jusqu'au servo d'aileron, en passant au-dessus du pylône
✅ la poutre de 12 mm passe dans les supports moteurs, le pylône et le bloc de queue
✅ longeron principal Ø10 mm : passage libre de Y = -360 à 360 mm
✅ goupille d'aile Ø4 mm : passage libre de Y = -100 à 100 mm
✅ longeron extérieur Ø6 mm : passage libre de Y = 280 à 590 mm
✅ trou de la vis nylon de retenue d'aile (Y = 55 mm) dégagé à travers l'aile
✅ prises du longeron de stab ouvertes côté intérieur des blocs de queue (12 mm)

## 6. Tubes carbone : longueurs à couper

| Usage | Tube (mm) | Qté | Longueur à couper | Tube acheté |
|---|---|---:|---:|---:|
| poutres | 12 x 10 | 2 | 610 mm | 1000 mm |
| longeron principal | 10 x 8 | 1 | 720 mm | 1000 mm |
| longerons extérieurs | 6 x 4 | 2 | 310 mm | 1000 mm |
| goupille d'aile | jonc 4 | 1 | 200 mm | 1000 mm |
| longeron de stab | 5 x 3 | 1 | 418 mm | 1000 mm |
| jonc de stab | jonc 2 | 1 | 418 mm | 1000 mm |
| joncs d'aileron | jonc 2 | 2 | 290 mm | 1000 mm |
| jonc de profondeur | jonc 1.5 | 1 | 390 mm | 1000 mm |
✅ chaque tube se coupe dans un tube du commerce de 1000 mm

## 7. Impression

✅ toutes les pièces tiennent sur le plateau 256 mm (voir build.py pour l'orientation)
