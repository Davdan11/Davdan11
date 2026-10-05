# Audit des fichiers STL — Huard DFR

Généré par `cad/audit_stl.py`. Contrôle des **fichiers STL livrés** (pas du modèle CAD) : maillage, pose sur le plateau, et **tranchage réel avec PrusaSlicer 2.7** (buse 0,4 mm, couches de 0,2 mm, réglages de la notice). Pour les pièces dont les parois sont dessinées (0 % de remplissage), le plastique déposé doit égaler, couche par couche, ce que les parois peuvent couvrir (le long des bords, sur parois x 0,45 mm) : sinon, des parois ou des âmes trop fines disparaîtraient au tranchage. Les zones plus épaisses (autour des fourreaux) restent creuses à 0 %, c'est normal.

**Résultat : 54 fichiers, aucun défaut.**

| Fichier | Maillage | Morceaux | Au plateau | Réglages | Déposé / parois attendues | Temps | Défauts |
|---|---|---:|---:|---|---:|---:|---|
| essais/1_jauge_tubes | fermé | 1 | 4359 mm² | 3 paroi(s), 15%, 4 couche(s) | — | 1h 48m 55s | ✅ |
| essais/2_tranche_aile | fermé | 1 | 510 mm² | 1 paroi(s), 0%, 0 couche(s) | 101% | 1h 41m 51s | ✅ |
| essais/3_jonction_cote_avant | fermé | 1 | 399 mm² | 2 paroi(s), 0%, 0 couche(s) | 95% | 1h 27m 32s | ✅ |
| essais/3_jonction_cote_milieu | fermé | 1 | 513 mm² | 2 paroi(s), 0%, 0 couche(s) | 95% | 1h 22m 29s | ✅ |
| essais/4_platine_moteur | fermé | 1 | 2180 mm² | 3 paroi(s), 30%, 4 couche(s) | — | 51m 50s | ✅ |
| essais/4_support_moteur | fermé | 1 | 2066 mm² | 3 paroi(s), 30%, 4 couche(s) | — | 2h 1m 9s | ✅ |
| essais/5_cadre_servo_aile | fermé | 1 | 411 mm² | 3 paroi(s), 30%, 4 couche(s) | — | 1h 13m 27s | ✅ |
| essais/5_trappe_servo_aile | fermé | 1 | 1456 mm² | 3 paroi(s), 30%, 4 couche(s) | — | 23m 7s | ✅ |
| essais/6_guignol_aileron | fermé | 1 | 506 mm² | 3 paroi(s), 30%, 4 couche(s) | — | 8m 43s | ✅ |
| stl/aile_segment_1_droit | fermé | 1 | 551 mm² | 1 paroi(s), 0%, 0 couche(s) | 100% | 20h 55m 23s | ✅ |
| stl/aile_segment_1_gauche | fermé | 1 | 551 mm² | 1 paroi(s), 0%, 0 couche(s) | 101% | 16h 20m 32s | ✅ |
| stl/aile_segment_2_droit | fermé | 1 | 510 mm² | 1 paroi(s), 0%, 0 couche(s) | 101% | 18h 3m 15s | ✅ |
| stl/aile_segment_2_gauche | fermé | 1 | 510 mm² | 1 paroi(s), 0%, 0 couche(s) | 102% | 17h 11m 18s | ✅ |
| stl/aile_segment_3_droit | fermé | 1 | 417 mm² | 1 paroi(s), 0%, 0 couche(s) | 102% | 11h 7m 45s | ✅ |
| stl/aile_segment_3_gauche | fermé | 1 | 417 mm² | 1 paroi(s), 0%, 0 couche(s) | 102% | 12h 1m 21s | ✅ |
| stl/aile_segment_4_droit | fermé | 1 | 325 mm² | 1 paroi(s), 0%, 0 couche(s) | 98% | 9h 23m 8s | ✅ |
| stl/aile_segment_4_gauche | fermé | 1 | 325 mm² | 1 paroi(s), 0%, 0 couche(s) | 98% | 8h 58m 40s | ✅ |
| stl/aileron_1_droit | fermé | 1 | 351 mm² | 2 paroi(s), 0%, 3 couche(s) | 101% | 4h 6m 39s | ✅ |
| stl/aileron_1_gauche | fermé | 1 | 351 mm² | 2 paroi(s), 0%, 3 couche(s) | 101% | 3h 34m 23s | ✅ |
| stl/aileron_2_droit | fermé | 1 | 351 mm² | 2 paroi(s), 0%, 3 couche(s) | 101% | 4h 6m 28s | ✅ |
| stl/aileron_2_gauche | fermé | 1 | 351 mm² | 2 paroi(s), 0%, 3 couche(s) | 101% | 3h 33m 27s | ✅ |
| stl/bloc_queue_droit | fermé | 1 | 3595 mm² | 3 paroi(s), 8%, 4 couche(s) | — | 9h 2m 39s | ✅ |
| stl/bloc_queue_gauche | fermé | 1 | 3595 mm² | 3 paroi(s), 8%, 4 couche(s) | — | 9h 2m 29s | ✅ |
| stl/cadre_servo_aile_droit | fermé | 1 | 411 mm² | 3 paroi(s), 30%, 4 couche(s) | — | 1h 13m 27s | ✅ |
| stl/cadre_servo_aile_gauche | fermé | 1 | 411 mm² | 3 paroi(s), 30%, 4 couche(s) | — | 1h 13m 41s | ✅ |
| stl/cloison_moteur | fermé | 1 | 2152 mm² | 4 paroi(s), 50%, 4 couche(s) | — | 1h 6m 26s | ✅ |
| stl/entretoise_plateau_arriere | fermé | 1 | 69 mm² | 4 paroi(s), 100%, 4 couche(s) | — | 14m 35s | ✅ |
| stl/entretoise_plateau_avant | fermé | 1 | 69 mm² | 4 paroi(s), 100%, 4 couche(s) | — | 12m 21s | ✅ |
| stl/fuselage_avant | fermé | 1 | 346 mm² | 2 paroi(s), 0%, 0 couche(s) | 98% | 9h 35m 4s | ✅ |
| stl/fuselage_milieu | fermé | 1 | 513 mm² | 2 paroi(s), 0%, 0 couche(s) | 98% | 11h 22m 2s | ✅ |
| stl/fuselage_nez | fermé | 1 | 423 mm² | 2 paroi(s), 0%, 3 couche(s) | 100% | 2h 35m 42s | ✅ |
| stl/fuselage_queue | fermé | 1 | 368 mm² | 2 paroi(s), 0%, 0 couche(s) | 97% | 2h 58m 41s | ✅ |
| stl/guignol_aileron | fermé | 1 | 506 mm² | 4 paroi(s), 100%, 4 couche(s) | — | 9m 1s | ✅ |
| stl/guignol_profondeur | fermé | 1 | 193 mm² | 4 paroi(s), 100%, 4 couche(s) | — | 3m 38s | ✅ |
| stl/patte_atterrissage | fermé | 1 | 1089 mm² | 4 paroi(s), 25%, 4 couche(s) | — | 3h 38m 12s | ✅ |
| stl/plateau_compagnon | fermé | 1 | 9495 mm² | 3 paroi(s), 30%, 4 couche(s) | — | 2h 53m 20s | ✅ |
| stl/plateau_electronique | fermé | 1 | 18582 mm² | 3 paroi(s), 30%, 4 couche(s) | — | 5h 17m 15s | ✅ |
| stl/platine_moteur | fermé | 1 | 2180 mm² | 4 paroi(s), 100%, 4 couche(s) | — | 1h 1m 34s | ✅ |
| stl/profondeur_1 | fermé | 1 | 55 mm² | 2 paroi(s), 0%, 3 couche(s) | 98% | 2h 14m 13s | ✅ |
| stl/profondeur_2 | fermé | 1 | 55 mm² | 2 paroi(s), 0%, 3 couche(s) | 98% | 2h 14m 13s | ✅ |
| stl/profondeur_3 | fermé | 1 | 55 mm² | 2 paroi(s), 0%, 3 couche(s) | 98% | 2h 21m 16s | ✅ |
| stl/pylone_poutre_droit | fermé | 1 | 302 mm² | 3 paroi(s), 10%, 4 couche(s) | — | 4h 8m 6s | ✅ |
| stl/pylone_poutre_gauche | fermé | 1 | 302 mm² | 3 paroi(s), 10%, 4 couche(s) | — | 4h 8m 9s | ✅ |
| stl/saumon_droit | fermé | 1 | 3523 mm² | 3 paroi(s), 5%, 4 couche(s) | — | 1h 20m 41s | ✅ |
| stl/saumon_gauche | fermé | 1 | 3523 mm² | 3 paroi(s), 5%, 4 couche(s) | — | 1h 19m 35s | ✅ |
| stl/stab_segment_1 | fermé | 1 | 163 mm² | 1 paroi(s), 0%, 0 couche(s) | 105% | 5h 48m 38s | ✅ |
| stl/stab_segment_2 | fermé | 1 | 163 mm² | 1 paroi(s), 0%, 0 couche(s) | 105% | 5h 48m 30s | ✅ |
| stl/stab_segment_3 | fermé | 1 | 163 mm² | 1 paroi(s), 0%, 0 couche(s) | 105% | 5h 48m 39s | ✅ |
| stl/support_gps | fermé | 1 | 356 mm² | 3 paroi(s), 100%, 4 couche(s) | — | 22m 13s | ✅ |
| stl/support_moteur | fermé | 1 | 2066 mm² | 4 paroi(s), 40%, 4 couche(s) | — | 2h 18m 26s | ✅ |
| stl/support_nacelle | fermé | 1 | 4501 mm² | 4 paroi(s), 30%, 4 couche(s) | — | 3h 2m 16s | ✅ |
| stl/trappe_acces | fermé | 1 | 111 mm² | 4 paroi(s), 100%, 4 couche(s) | — | 1h 41m 29s | ✅ |
| stl/trappe_servo_aile_droit | fermé | 1 | 1456 mm² | 3 paroi(s), 100%, 4 couche(s) | — | 23m 7s | ✅ |
| stl/trappe_servo_aile_gauche | fermé | 1 | 1456 mm² | 3 paroi(s), 100%, 4 couche(s) | — | 23m 4s | ✅ |

Temps total estimé par PrusaSlicer (pièces + kit d'essai, un exemplaire de chaque fichier) : **245 h**. Bambu Studio sur la A1 est en général plus rapide.

## Messages du trancheur

- 3_jonction_cote_milieu : print warning: Detected print stability issues:
- 5_cadre_servo_aile : print warning: Detected print stability issues:
- aileron_1_droit : Floating bridge anchors, Long bridging extrusions
- aileron_1_droit : print warning: Detected print stability issues:
- aileron_1_gauche : Floating bridge anchors
- aileron_1_gauche : print warning: Detected print stability issues:
- aileron_2_droit : Floating bridge anchors, Long bridging extrusions
- aileron_2_droit : print warning: Detected print stability issues:
- aileron_2_gauche : Floating bridge anchors
- aileron_2_gauche : print warning: Detected print stability issues:
- bloc_queue_droit : print warning: Detected print stability issues:
- bloc_queue_gauche : print warning: Detected print stability issues:
- cadre_servo_aile_droit : print warning: Detected print stability issues:
- cadre_servo_aile_gauche : print warning: Detected print stability issues:
- fuselage_milieu : print warning: Detected print stability issues:
- fuselage_nez : Floating bridge anchors, Long bridging extrusions
- fuselage_nez : print warning: Detected print stability issues:
- profondeur_1 : print warning: Detected print stability issues:
- profondeur_2 : print warning: Detected print stability issues:
- profondeur_3 : print warning: Detected print stability issues:
- pylone_poutre_droit : print warning: Detected print stability issues:
- pylone_poutre_gauche : print warning: Detected print stability issues:
- trappe_acces : print warning: Detected print stability issues:
