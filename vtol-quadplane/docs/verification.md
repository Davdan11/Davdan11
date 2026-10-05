# Vérification d'intégration — Huard DFR

Généré par `cad/verification.py` : l'avion est monté en 3D avec toutes les pièces imprimées et toutes les pièces achetées à leurs cotes (moteurs, hélices, servos, ESC, batterie, contrôleur de vol, GPS, Raspberry Pi, modem, capteur de vitesse, nacelle, tubes carbone), puis chaque contrôle est fait par calcul.

**Résultat : tout est bon.**


## 1. Collisions entre éléments

✅ 91 éléments montés (34 modèles de pièces imprimées + pièces achetées) : aucune collision

## 2. Débattement des gouvernes (±25°)

✅ ailerons, profondeurs, guignols et joncs tournent librement de -25° à +25°

## 3. Hélices

✅ les 4 disques d'hélices VTOL (15 po) et le disque propulsif (10 po) ne touchent rien (aile, stab, dérives, fuselage, autres hélices)

## 4. Garde au sol

✅ sol à z = -247 mm ; plus bas élément : nacelle_boule à 56 mm du sol ; helice_propulseur 115 mm ; nacelle_boitier 121 mm ; support_nacelle 151 mm

## 5. Chemins libres (câbles et tubes)

✅ conduit de câbles de l'aile (Ø10 mm) libre du flanc du fuselage jusqu'au servo d'aileron, en passant au-dessus du pylône
✅ la poutre de 16 mm passe dans les supports moteurs, le pylône et le bloc de queue
✅ longeron principal Ø16 mm : passage libre de Y = -500 à 500 mm
✅ goupille d'aile Ø6 mm : passage libre de Y = -150 à 150 mm
✅ longeron extérieur Ø8 mm : passage libre de Y = 380 à 880 mm
✅ trou de la vis nylon de retenue d'aile (Y = 70 mm) dégagé à travers l'aile
✅ prises du longeron de stab ouvertes côté intérieur des blocs de queue (12 mm)

## 6. Tubes carbone : longueurs à couper

| Usage | Tube (mm) | Qté | Longueur à couper | Tube acheté |
|---|---|---:|---:|---:|
| poutres | 16 x 14 | 2 | 1000 mm | 1000 mm |
| longeron principal | 16 x 14 | 1 | 1000 mm | 1000 mm |
| longerons extérieurs | 8 x 6 | 2 | 500 mm | 1000 mm |
| goupille d'aile | jonc 6 | 1 | 300 mm | 1000 mm |
| longeron de stab | 6 x 4 | 1 | 714 mm | 1000 mm |
| jonc de stab | jonc 3 | 1 | 714 mm | 1000 mm |
| joncs d'aileron | jonc 2 | 2 | 416 mm | 1000 mm |
| jonc de profondeur | jonc 2 | 1 | 686 mm | 1000 mm |
✅ chaque tube se coupe dans un tube du commerce de 1000 mm

## 7. Impression

✅ toutes les pièces tiennent sur le plateau 256 mm (voir build.py pour l'orientation)
✅ toutes les pièces s'impriment sans supports dans leur orientation (surplombs ≤ 3000 mm² : plafonds de petites cavités et trous horizontaux, qui se font en pont)

| Pièce | Surplombs > 45° (mm²) |
|---|---:|
| fuselage_nez | 2171 |
| bloc_queue | 2114 |
| fuselage_milieu | 2066 |
| cadre_servo_aile | 836 |
| fuselage_queue | 831 |
| support_moteur | 791 |
| fuselage_avant | 585 |
| support_gps | 356 |
✅ aucune couche ne part dans le vide : pièces à 1 paroi (aile, fuselage) ≤ 6 mm du bord soutenu (pont ≤ 12 mm) ; pièces pleines ≤ 12.5 mm (pont ≤ 25 mm, comme le plafond de la baie du servo de profondeur)

| Pièce | Pire porte-à-faux (mm) | Hauteur (mm) |
|---|---:|---:|
| bloc_queue | 9.3 | 48 |
| aileron_1 | 4.9 | 43 |
| fuselage_milieu | 4.2 | 108 |
| trappe_acces | 3.0 | 102 |
| support_gps | 2.9 | 13 |
| aile_segment_2 | 2.8 | 90 |
| profondeur_3 | 2.0 | 221 |
| patte_atterrissage | 1.7 | 230 |

## Ce que ce contrôle ne peut pas garantir

- Les cotes des pièces achetées viennent des fiches techniques. Les oreilles des servos (non publiées) et la taille réelle des tubes carbone sont à mesurer au pied à coulisse à la réception ; une différence se corrige dans les paramètres et tout se régénère.
- Les tolérances d'impression (retrait du PETG, moussage du PLA Aero) : imprimer d'abord un segment d'aile, un support moteur et un cadre de servo pour valider les ajustements.
- Les câbles : le conduit de l'aile (Ø10 mm) est dimensionné pour le câblage du README (une paire d'alimentation par côté, en Y vers les 2 ESC, et des rallonges de servo), rempli à environ 37 %. Avec d'autres fils, refaire le compte.
- Le comportement en vol (réglages, vibrations, autonomie réelle) ne se vérifie qu'en volant, en suivant le plan d'essais du README.
