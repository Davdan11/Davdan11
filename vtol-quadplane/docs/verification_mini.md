# Vérification d'intégration — Huard Mini

Généré par `cad/verification.py` : l'avion est monté en 3D avec toutes les pièces imprimées et toutes les pièces achetées à leurs cotes (moteurs, hélices, servos, ESC, batterie, contrôleur de vol, GPS, tubes carbone), puis chaque contrôle est fait par calcul.

**Résultat : tout est bon.**


## 1. Collisions entre éléments

✅ 78 éléments montés (27 modèles de pièces imprimées + pièces achetées) : aucune collision

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
| joncs d'aileron | jonc 2 | 2 | 294 mm | 1000 mm |
| jonc de profondeur | jonc 1.5 | 1 | 390 mm | 1000 mm |
✅ chaque tube se coupe dans un tube du commerce de 1000 mm

## 7. Impression

✅ toutes les pièces tiennent sur le plateau 256 mm (voir build.py pour l'orientation)
✅ toutes les pièces s'impriment sans supports dans leur orientation (surplombs ≤ 3000 mm² : plafonds de petites cavités et trous horizontaux, qui se font en pont)

| Pièce | Surplombs > 45° (mm²) |
|---|---:|
| bloc_queue | 1473 |
| fuselage_milieu | 1213 |
| fuselage_nez | 1136 |
| cadre_servo_aile | 836 |
| fuselage_queue | 729 |
| support_moteur | 681 |
| fuselage_avant | 407 |
| patte_atterrissage | 309 |
✅ aucune couche ne part dans le vide : pièces à 1 paroi (aile, fuselage) ≤ 6 mm du bord soutenu (pont ≤ 12 mm) ; pièces pleines ≤ 12.5 mm (pont ≤ 25 mm, comme le plafond de la baie du servo de profondeur)

| Pièce | Pire porte-à-faux (mm) | Hauteur (mm) |
|---|---:|---:|
| fuselage_milieu | 4.2 | 138 |
| aile_segment_1 | 4.1 | 22 |
| aileron_1 | 3.5 | 43 |
| aile_segment_2 | 3.3 | 73 |
| profondeur_2 | 1.6 | 188 |
| bloc_queue | 1.5 | 17 |
| patte_atterrissage | 1.5 | 116 |
| fuselage_nez | 1.4 | 10 |

## Ce que ce contrôle ne peut pas garantir

- Les cotes des pièces achetées viennent des fiches techniques. Les oreilles des servos (non publiées) et la taille réelle des tubes carbone sont à mesurer au pied à coulisse à la réception ; une différence se corrige dans les paramètres et tout se régénère.
- Les tolérances d'impression (retrait du PETG, moussage du PLA Aero) : imprimer d'abord un segment d'aile, un support moteur et un cadre de servo pour valider les ajustements.
- Les câbles sont supposés passer dans les conduits prévus (Ø9 mm DFR, Ø7 mm Mini) : utiliser les sections de fil indiquées dans la nomenclature.
- Le comportement en vol (réglages, vibrations, autonomie réelle) ne se vérifie qu'en volant, en suivant le plan d'essais du README.
