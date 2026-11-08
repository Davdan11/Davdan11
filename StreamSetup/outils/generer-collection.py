#!/usr/bin/env python3
"""Génère obs/StreamSetup.json, la collection de scènes à importer dans OBS.

Tu n'as pas besoin de lancer ce script : le fichier est déjà fourni.
Il sert seulement à régénérer la collection si tu installes le dossier
ailleurs que dans C:\\StreamSetup :

    python generer-collection.py --dossier "D:/Stream/StreamSetup"

Base de travail : canevas 1920 × 1080 (Paramètres > Vidéo > Résolution de base).
"""
import argparse
import json
import pathlib
import uuid

ICI = pathlib.Path(__file__).resolve().parent
NAMESPACE = uuid.UUID("6f1c3d2e-8a4b-4c1d-9e7f-5a6b7c8d9e0f")

# Raccourcis clavier (Ctrl + Alt + touche) : faciles à atteindre en jeu
# et peu utilisés par les jeux eux-mêmes.
def touche(cle):
    return [{"control": True, "alt": True, "key": cle}]


def id_stable(nom):
    """UUID déterministe : régénérer le fichier donne le même résultat."""
    return str(uuid.uuid5(NAMESPACE, nom))


def source(nom, type_id, reglages=None, filtres=None, hotkeys=None, mixers=0, **extra):
    s = {
        "name": nom,
        "uuid": id_stable("source:" + nom),
        "id": type_id,
        "versioned_id": extra.pop("versioned_id", type_id),
        "settings": reglages or {},
        "mixers": mixers,
        "sync": 0,
        "flags": 0,
        "volume": 1.0,
        "balance": 0.5,
        "enabled": True,
        "muted": extra.pop("muted", False),
        "push-to-mute": False,
        "push-to-mute-delay": 0,
        "push-to-talk": False,
        "push-to-talk-delay": 0,
        "hotkeys": hotkeys or {},
        "deinterlace_mode": 0,
        "deinterlace_field_order": 0,
        "monitoring_type": extra.pop("monitoring_type", 0),
        "private_settings": {},
    }
    if filtres:
        s["filters"] = filtres
    s.update(extra)
    return s


def filtre(nom, type_id, versioned_id, reglages, audio=False, parent=""):
    f = source(nom, type_id, reglages, mixers=255 if audio else 0, versioned_id=versioned_id)
    f["uuid"] = id_stable("filtre:" + parent + ":" + nom)
    return f


def navigateur(nom, dossier, fichier, largeur, hauteur, eteindre_si_cache=False, recharger_si_actif=False):
    return source(nom, "browser_source", {
        "is_local_file": True,
        "local_file": f"{dossier}/overlays/{fichier}",
        "width": largeur,
        "height": hauteur,
        "fps_custom": False,
        "reroute_audio": False,
        "restart_when_active": recharger_si_actif,
        "shutdown": eteindre_si_cache,
        "css": "body { background-color: rgba(0, 0, 0, 0); margin: 0px auto; overflow: hidden; }",
    })


def element(src, item_id, x=0.0, y=0.0, echelle=1.0, visible=True, verrou=True, cadre=None, mode_cadre=2):
    """Un élément de scène. `cadre` = (largeur, hauteur) de la boîte englobante."""
    it = {
        "name": src["name"],
        "source_uuid": src["uuid"],
        "visible": visible,
        "locked": verrou,
        "rot": 0.0,
        "pos": {"x": float(x), "y": float(y)},
        "scale": {"x": float(echelle), "y": float(echelle)},
        "align": 5,  # haut-gauche
        "bounds_type": 0,
        "bounds_align": 0,
        "bounds": {"x": 0.0, "y": 0.0},
        "crop_left": 0,
        "crop_top": 0,
        "crop_right": 0,
        "crop_bottom": 0,
        "id": item_id,
        "group_item_backup": False,
        "scale_filter": "disable",
        "blend_method": "default",
        "blend_type": "normal",
        "show_transition": {"duration": 0},
        "hide_transition": {"duration": 0},
        "private_settings": {},
    }
    if cadre:
        # 2 = adapter à l'intérieur (tout visible), 3 = remplir (rogne le surplus).
        it["bounds_type"] = mode_cadre
        it["bounds"] = {"x": float(cadre[0]), "y": float(cadre[1])}
    return it


def scene(nom, elements, raccourci=None, raccourcis_elements=None, filtres=None):
    hotkeys = {"OBSBasic.SelectScene": raccourci or []}
    for it in elements:
        lien = (raccourcis_elements or {}).get(it["name"], [])
        hotkeys[f"libobs.show_scene_item.{it['id']}"] = lien
        hotkeys[f"libobs.hide_scene_item.{it['id']}"] = lien
    s = source(nom, "scene", {
        "id_counter": max([it["id"] for it in elements] or [0]),
        "custom_size": False,
        "items": elements,
    }, hotkeys=hotkeys, filtres=filtres)
    return s


def construire(dossier):
    dossier = dossier.replace("\\", "/").rstrip("/")

    # ── Audio global ────────────────────────────────────────────
    micro = source(
        "Micro",
        "wasapi_input_capture",
        {"device_id": "default"},
        mixers=255,
        hotkeys={
            # Même touche pour « muet » et « réactiver » = bascule.
            "libobs.mute": touche("OBS_KEY_M"),
            "libobs.unmute": touche("OBS_KEY_M"),
            "libobs.push-to-mute": [],
            "libobs.push-to-talk": [],
        },
        filtres=[
            filtre("1. Suppression du bruit", "noise_suppress_filter", "noise_suppress_filter_v2",
                   {"method": "rnnoise", "suppress_level": -30}, audio=True, parent="Micro"),
            filtre("2. Gain", "gain_filter", "gain_filter",
                   {"db": 0.0}, audio=True, parent="Micro"),
            filtre("3. Compresseur", "compressor_filter", "compressor_filter",
                   {"ratio": 4.0, "threshold": -20.0, "attack_time": 6, "release_time": 60,
                    "output_gain": 4.0, "sidechain_source": "none"}, audio=True, parent="Micro"),
            filtre("4. Limiteur", "limiter_filter", "limiter_filter",
                   {"threshold": -3.0, "release_time": 60}, audio=True, parent="Micro"),
        ],
    )
    bureau = source("Audio du bureau", "wasapi_output_capture", {"device_id": "default"}, mixers=255)

    # ── Sources visuelles ───────────────────────────────────────
    ecran_debut = navigateur("Écran début", dossier, "debut.html", 1920, 1080, True, True)
    ecran_pause = navigateur("Écran pause", dossier, "pause.html", 1920, 1080, True, True)
    ecran_fin = navigateur("Écran fin", dossier, "fin.html", 1920, 1080, True, True)
    fond = navigateur("Fond animé", dossier, "fond.html", 1920, 1080, True, False)
    bandeau = navigateur("Bandeau", dossier, "bandeau.html", 1920, 90)
    chat = navigateur("Chat", dossier, "chat.html", 480, 720)
    cadre = navigateur("Cadre caméra", dossier, "cadre-camera.html", 1920, 1080)
    alertes = source("Alertes", "browser_source", {
        "is_local_file": False,
        "url": "",
        "width": 1920,
        "height": 1080,
        "fps_custom": False,
        "reroute_audio": False,
        "restart_when_active": False,
        "shutdown": False,
        "css": "body { background-color: rgba(0, 0, 0, 0); margin: 0px auto; overflow: hidden; }",
    })

    jeu = source("Jeu", "game_capture", {
        "capture_mode": "any_fullscreen",
        "capture_cursor": True,
        "allow_transparency": False,
        "anti_cheat_hook": True,
        "capture_overlays": False,
        "limit_framerate": False,
    })
    jeu_fenetre = source("Jeu (fenêtre)", "window_capture", {
        "method": 0,
        "cursor": True,
        "client_area": True,
    })

    # La Facecam n'est JAMAIS ajoutée ici : seul le logiciel d'IA la lit.
    cam_fenetre = source("Caméra IA - fenêtre", "window_capture", {
        "method": 0,
        "cursor": False,
        "client_area": True,
    })
    cam_virtuelle = source("Caméra IA - caméra virtuelle", "dshow_input", {
        "video_device_id": "",
        "res_type": 0,
        "active": True,
        "deactivate_when_not_showing": False,
    })
    fond_cam = source("Fond caméra", "color_source_v3", {
        "color": 0xFF1B1220,  # ABGR : violet très foncé
        "width": 1920,
        "height": 1080,
    }, versioned_id="color_source_v3")

    # ── Scène imbriquée : la caméra, réutilisée partout ─────────
    masque = filtre("Coins arrondis", "mask_filter", "mask_filter_v2", {
        "type": "mask_alpha_filter.effect",
        "image_path": f"{dossier}/overlays/img/masque-camera.png",
        "stretch": True,
    }, parent="[Source] Caméra")
    scene_cam = scene("[Source] Caméra", [
        element(fond_cam, 1),
        element(cam_fenetre, 2, cadre=(1920, 1080), mode_cadre=3),
        element(cam_virtuelle, 3, visible=False, cadre=(1920, 1080), mode_cadre=3),
        element(cadre, 4),
    ], filtres=[masque])

    # ── Scènes ──────────────────────────────────────────────────
    s_debut = scene("Début", [
        element(ecran_debut, 1),
        element(alertes, 2),
    ], raccourci=touche("OBS_KEY_1"))

    # Mode « remplir » : un jeu 16:9 occupe tout l'écran ; un jeu en 32:9
    # (écran ultralarge comme l'Odyssey G9) montre le centre en grand au lieu
    # d'une mince bande entourée de noir.
    s_jeu = scene("En jeu", [
        element(jeu, 1, cadre=(1920, 1080), mode_cadre=3),
        element(jeu_fenetre, 2, visible=False, cadre=(1920, 1080), mode_cadre=3),
        element(scene_cam, 3, x=32, y=778, echelle=0.25),        # 480 × 270, coin bas-gauche
        element(chat, 4, x=1408, y=96, visible=False),
        element(bandeau, 5, y=990, visible=False),
        element(alertes, 6),
    ], raccourci=touche("OBS_KEY_2"),
       raccourcis_elements={"[Source] Caméra": touche("OBS_KEY_C")})

    s_discussion = scene("Discussion", [
        element(fond, 1),
        element(scene_cam, 2, x=64, y=135, echelle=2 / 3),         # 1280 × 720
        element(chat, 3, x=1376, y=135),                           # 480 × 720
        element(bandeau, 4, y=990),
        element(alertes, 5),
    ], raccourci=touche("OBS_KEY_3"),
       raccourcis_elements={"[Source] Caméra": touche("OBS_KEY_C")})

    s_pause = scene("Pause", [
        element(ecran_pause, 1),
        element(alertes, 2),
    ], raccourci=touche("OBS_KEY_4") + touche("OBS_KEY_P"))

    s_fin = scene("Fin", [
        element(ecran_fin, 1),
        element(alertes, 2),
    ], raccourci=touche("OBS_KEY_5"))

    scenes = [s_debut, s_jeu, s_discussion, s_pause, s_fin, scene_cam]
    autres = [ecran_debut, ecran_pause, ecran_fin, fond, bandeau, chat, cadre, alertes,
              jeu, jeu_fenetre, cam_fenetre, cam_virtuelle, fond_cam]

    return {
        "current_scene": "Début",
        "current_program_scene": "Début",
        "scene_order": [{"name": s["name"]} for s in scenes],
        "name": "StreamSetup",
        "DesktopAudioDevice1": bureau,
        "AuxAudioDevice1": micro,
        "sources": scenes + autres,
        "groups": [],
        "quick_transitions": [],
        "transitions": [],
        "saved_projectors": [],
        "current_transition": "Fade",
        "transition_duration": 300,
        "preview_locked": False,
        "scaling_enabled": False,
        "scaling_level": 0,
        "scaling_off_x": 0.0,
        "scaling_off_y": 0.0,
        "modules": {},
    }


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--dossier", default="C:/StreamSetup",
                   help="Emplacement du dossier StreamSetup sur le PC de stream (défaut : C:/StreamSetup)")
    p.add_argument("--sortie", default=str(ICI.parent / "obs" / "StreamSetup.json"))
    args = p.parse_args()
    data = construire(args.dossier)
    pathlib.Path(args.sortie).write_text(json.dumps(data, indent=4, ensure_ascii=False) + "\n", encoding="utf-8")
    print("Collection écrite :", args.sortie)


if __name__ == "__main__":
    main()
