# Audit des fichiers STL — Huard Mini

Généré par `cad/audit_stl.py`. Contrôle des **fichiers STL livrés** (pas du modèle CAD) : maillage, pose sur le plateau, et **tranchage réel avec PrusaSlicer 2.7** (buse 0,4 mm, couches de 0,2 mm, réglages de la notice). Pour les pièces dont les parois sont dessinées (0 % de remplissage), le plastique déposé doit égaler, couche par couche, ce que les parois peuvent couvrir (le long des bords, sur parois x 0,45 mm) : sinon, des parois ou des âmes trop fines disparaîtraient au tranchage. Les zones plus épaisses (autour des fourreaux) restent creuses à 0 %, c'est normal.

**Résultat : 47 fichiers, aucun défaut.**

| Fichier | Maillage | Morceaux | Au plateau | Réglages | Déposé / parois attendues | Temps | Défauts |
|---|---|---:|---:|---|---:|---:|---|
| essais/1_jauge_tubes | fermé | 1 | 4847 mm² | 3 paroi(s), 15%, 4 couche(s) | — | 2h 9m 50s | ✅ |
| essais/2_tranche_aile | fermé | 1 | 280 mm² | 1 paroi(s), 0%, 0 couche(s) | 104% | 41m 37s | ✅ |
| essais/3_jonction_cote_avant | fermé | 1 | 289 mm² | 2 paroi(s), 0%, 0 couche(s) | 95% | 1h 0m 52s | ✅ |
| essais/3_jonction_cote_milieu | fermé | 1 | 289 mm² | 2 paroi(s), 0%, 0 couche(s) | 96% | 38m 52s | ✅ |
| essais/4_platine_moteur | fermé | 1 | 1313 mm² | 3 paroi(s), 30%, 4 couche(s) | — | 34m 59s | ✅ |
| essais/4_support_moteur | fermé | 1 | 1200 mm² | 3 paroi(s), 30%, 4 couche(s) | — | 1h 30m 14s | ✅ |
| essais/5_cadre_servo_aile | fermé | 1 | 411 mm² | 3 paroi(s), 30%, 4 couche(s) | — | 55m 1s | ✅ |
| essais/5_trappe_servo_aile | fermé | 1 | 1456 mm² | 3 paroi(s), 30%, 4 couche(s) | — | 23m 7s | ✅ |
| essais/6_guignol_aileron | fermé | 1 | 258 mm² | 3 paroi(s), 30%, 4 couche(s) | — | 4m 42s | ✅ |
| stl/aile_segment_1_droit | fermé | 1 | 347 mm² | 1 paroi(s), 0%, 0 couche(s) | 101% | 10h 56m 11s | ✅ |
| stl/aile_segment_1_gauche | fermé | 1 | 347 mm² | 1 paroi(s), 0%, 0 couche(s) | 102% | 9h 29m 59s | ✅ |
| stl/aile_segment_2_droit | fermé | 1 | 337 mm² | 1 paroi(s), 0%, 0 couche(s) | 103% | 8h 3m 36s | ✅ |
| stl/aile_segment_2_gauche | fermé | 1 | 337 mm² | 1 paroi(s), 0%, 0 couche(s) | 103% | 8h 14m 51s | ✅ |
| stl/aile_segment_3_droit | fermé | 1 | 233 mm² | 1 paroi(s), 0%, 0 couche(s) | 99% | 5h 31m 39s | ✅ |
| stl/aile_segment_3_gauche | fermé | 1 | 233 mm² | 1 paroi(s), 0%, 0 couche(s) | 99% | 5h 37m 21s | ✅ |
| stl/aileron_1_droit | fermé | 1 | 182 mm² | 2 paroi(s), 0%, 3 couche(s) | 102% | 1h 36m 48s | ✅ |
| stl/aileron_1_gauche | fermé | 1 | 182 mm² | 2 paroi(s), 0%, 3 couche(s) | 102% | 1h 26m 4s | ✅ |
| stl/aileron_2_droit | fermé | 1 | 182 mm² | 2 paroi(s), 0%, 3 couche(s) | 100% | 2h 39m 33s | ✅ |
| stl/aileron_2_gauche | fermé | 1 | 182 mm² | 2 paroi(s), 0%, 3 couche(s) | 101% | 2h 21m 13s | ✅ |
| stl/bloc_queue_droit | fermé | 1 | 1972 mm² | 3 paroi(s), 8%, 4 couche(s) | — | 5h 17m 40s | ✅ |
| stl/bloc_queue_gauche | fermé | 1 | 1972 mm² | 3 paroi(s), 8%, 4 couche(s) | — | 5h 17m 49s | ✅ |
| stl/cadre_servo_aile_droit | fermé | 1 | 411 mm² | 3 paroi(s), 30%, 4 couche(s) | — | 55m 1s | ✅ |
| stl/cadre_servo_aile_gauche | fermé | 1 | 411 mm² | 3 paroi(s), 30%, 4 couche(s) | — | 55m 0s | ✅ |
| stl/cloison_moteur | fermé | 1 | 1647 mm² | 4 paroi(s), 50%, 4 couche(s) | — | 55m 0s | ✅ |
| stl/fuselage_avant | fermé | 1 | 248 mm² | 2 paroi(s), 0%, 0 couche(s) | 96% | 5h 39m 31s | ✅ |
| stl/fuselage_milieu | fermé | 1 | 289 mm² | 2 paroi(s), 0%, 0 couche(s) | 98% | 7h 10m 2s | ✅ |
| stl/fuselage_nez | fermé | 1 | 343 mm² | 2 paroi(s), 0%, 3 couche(s) | 101% | 1h 25m 51s | ✅ |
| stl/fuselage_queue | fermé | 1 | 289 mm² | 2 paroi(s), 0%, 0 couche(s) | 97% | 2h 24m 50s | ✅ |
| stl/guignol_aileron | fermé | 1 | 258 mm² | 4 paroi(s), 100%, 4 couche(s) | — | 4m 48s | ✅ |
| stl/guignol_profondeur | fermé | 1 | 127 mm² | 4 paroi(s), 100%, 4 couche(s) | — | 2m 50s | ✅ |
| stl/patte_atterrissage | fermé | 1 | 521 mm² | 4 paroi(s), 25%, 4 couche(s) | — | 2h 41m 37s | ✅ |
| stl/plateau_compagnon | fermé | 1 | 3846 mm² | 3 paroi(s), 30%, 4 couche(s) | — | 1h 13m 33s | ✅ |
| stl/plateau_electronique | fermé | 1 | 12871 mm² | 3 paroi(s), 30%, 4 couche(s) | — | 3h 41m 56s | ✅ |
| stl/platine_moteur | fermé | 1 | 1313 mm² | 4 paroi(s), 100%, 4 couche(s) | — | 40m 53s | ✅ |
| stl/profondeur_1 | fermé | 1 | 42 mm² | 2 paroi(s), 0%, 3 couche(s) | 101% | 1h 38m 36s | ✅ |
| stl/profondeur_2 | fermé | 1 | 42 mm² | 2 paroi(s), 0%, 3 couche(s) | 101% | 1h 38m 21s | ✅ |
| stl/pylone_poutre_droit | fermé | 1 | 162 mm² | 3 paroi(s), 10%, 4 couche(s) | — | 2h 38m 9s | ✅ |
| stl/pylone_poutre_gauche | fermé | 1 | 162 mm² | 3 paroi(s), 10%, 4 couche(s) | — | 2h 37m 58s | ✅ |
| stl/saumon_droit | fermé | 1 | 1862 mm² | 3 paroi(s), 5%, 4 couche(s) | — | 51m 14s | ✅ |
| stl/saumon_gauche | fermé | 1 | 1862 mm² | 3 paroi(s), 5%, 4 couche(s) | — | 50m 13s | ✅ |
| stl/stab_segment_1 | fermé | 1 | 129 mm² | 1 paroi(s), 0%, 0 couche(s) | 105% | 4h 5m 53s | ✅ |
| stl/stab_segment_2 | fermé | 1 | 129 mm² | 1 paroi(s), 0%, 0 couche(s) | 105% | 4h 5m 46s | ✅ |
| stl/support_gps | fermé | 1 | 285 mm² | 3 paroi(s), 100%, 4 couche(s) | — | 14m 5s | ✅ |
| stl/support_moteur | fermé | 1 | 1200 mm² | 4 paroi(s), 40%, 4 couche(s) | — | 1h 42m 28s | ✅ |
| stl/trappe_acces | fermé | 1 | 79 mm² | 4 paroi(s), 100%, 4 couche(s) | — | 49m 41s | ✅ |
| stl/trappe_servo_aile_droit | fermé | 1 | 1456 mm² | 3 paroi(s), 100%, 4 couche(s) | — | 23m 7s | ✅ |
| stl/trappe_servo_aile_gauche | fermé | 1 | 1456 mm² | 3 paroi(s), 100%, 4 couche(s) | — | 23m 3s | ✅ |

Temps total estimé par PrusaSlicer (pièces + kit d'essai, un exemplaire de chaque fichier) : **124 h**. Bambu Studio sur la A1 est en général plus rapide.

## Messages du trancheur

- 5_cadre_servo_aile : Floating bridge anchors, Low bed adhesion, Long bridging extrusions
- 5_cadre_servo_aile : print warning: Detected print stability issues:
- aileron_1_droit : Floating bridge anchors, Long bridging extrusions
- aileron_1_droit : print warning: Detected print stability issues:
- aileron_1_gauche : Floating bridge anchors
- aileron_1_gauche : print warning: Detected print stability issues:
- aileron_2_droit : Floating bridge anchors, Low bed adhesion, Long bridging extrusions
- aileron_2_droit : print warning: Detected print stability issues:
- aileron_2_gauche : Floating bridge anchors
- aileron_2_gauche : print warning: Detected print stability issues:
- bloc_queue_droit : print warning: Detected print stability issues:
- bloc_queue_gauche : print warning: Detected print stability issues:
- cadre_servo_aile_droit : Floating bridge anchors, Low bed adhesion, Long bridging extrusions
- cadre_servo_aile_droit : print warning: Detected print stability issues:
- cadre_servo_aile_gauche : Floating bridge anchors, Low bed adhesion, Long bridging extrusions
- cadre_servo_aile_gauche : print warning: Detected print stability issues:
- fuselage_nez : print warning: Detected print stability issues:
- profondeur_1 : print warning: Detected print stability issues:
- profondeur_2 : print warning: Detected print stability issues:
- pylone_poutre_droit : print warning: Detected print stability issues:
- pylone_poutre_gauche : print warning: Detected print stability issues:
- trappe_acces : print warning: Detected print stability issues:
