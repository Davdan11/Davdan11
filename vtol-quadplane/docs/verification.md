# Vérification d'intégration — Huard DFR

Généré par `cad/verification.py` : l'avion est monté en 3D avec toutes les pièces imprimées et toutes les pièces achetées à leurs cotes (moteurs, hélices, servos, ESC, batterie, contrôleur de vol, GPS, Raspberry Pi, modem, capteur de vitesse, nacelle, tubes carbone), puis chaque contrôle est fait par calcul.

**Résultat : tout est bon.**


## 1. Collisions entre éléments

✅ 88 éléments montés (31 modèles de pièces imprimées + pièces achetées) : aucune collision

## 2. Débattement des gouvernes (±25°)

✅ ailerons, profondeurs, guignols et joncs tournent librement de -25° à +25°

## 3. Hélices

✅ les 4 disques d'hélices VTOL (15 po) et le disque propulsif (10 po) ne touchent rien (aile, stab, dérives, fuselage, autres hélices)

## 4. Garde au sol

✅ sol à z = -247 mm ; plus bas élément : nacelle_boule à 56 mm du sol ; helice_propulseur 115 mm ; nacelle_boitier 121 mm ; support_nacelle 151 mm

## 5. Chemins libres (câbles et tubes)

✅ conduit de câbles de l'aile (Ø9 mm) libre du flanc du fuselage jusqu'au servo d'aileron, en passant au-dessus du pylône
✅ la poutre de 16 mm passe dans les supports moteurs, le pylône et le bloc de queue
✅ longeron principal Ø12 mm : passage libre de Y = -500 à 500 mm
✅ goupille d'aile Ø6 mm : passage libre de Y = -150 à 150 mm
✅ longeron extérieur Ø8 mm : passage libre de Y = 380 à 880 mm
✅ trou de la vis nylon de retenue d'aile (Y = 70 mm) dégagé à travers l'aile
✅ prises du longeron de stab ouvertes côté intérieur des blocs de queue (12 mm)

## 6. Tubes carbone : longueurs à couper

| Usage | Tube (mm) | Qté | Longueur à couper | Tube acheté |
|---|---|---:|---:|---:|
| poutres | 16 x 14 | 2 | 1000 mm | 1000 mm |
| longeron principal | 12 x 10 | 1 | 1000 mm | 1000 mm |
| longerons extérieurs | 8 x 6 | 2 | 500 mm | 1000 mm |
| goupille d'aile | jonc 6 | 1 | 300 mm | 1000 mm |
| longeron de stab | 6 x 4 | 1 | 714 mm | 1000 mm |
| jonc de stab | jonc 3 | 1 | 714 mm | 1000 mm |
| joncs d'aileron | jonc 2 | 2 | 410 mm | 1000 mm |
| jonc de profondeur | jonc 2 | 1 | 686 mm | 1000 mm |
✅ chaque tube se coupe dans un tube du commerce de 1000 mm

## 7. Impression

✅ toutes les pièces tiennent sur le plateau 256 mm (voir build.py pour l'orientation)

## Ce que ce contrôle ne peut pas garantir

- Les cotes des pièces achetées viennent des fiches techniques. Les oreilles des servos (non publiées) et la taille réelle des tubes carbone sont à mesurer au pied à coulisse à la réception ; une différence se corrige dans les paramètres et tout se régénère.
- Les tolérances d'impression (retrait du PETG, moussage du PLA Aero) : imprimer d'abord un segment d'aile, un support moteur et un cadre de servo pour valider les ajustements.
- Les câbles sont supposés passer dans les conduits prévus (Ø9 mm DFR, Ø7 mm Mini) : utiliser les sections de fil indiquées dans la nomenclature.
- Le comportement en vol (réglages, vibrations, autonomie réelle) ne se vérifie qu'en volant, en suivant le plan d'essais du README.
