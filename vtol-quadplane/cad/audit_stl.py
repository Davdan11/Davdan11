"""Audit des fichiers STL livrés, indépendant du modèle CAD : on contrôle ce que l'imprimante recevra.

    python audit_stl.py                      # Huard DFR  -> docs/audit_stl.md
    HUARD_VERSION=mini python audit_stl.py   # Huard Mini -> docs/audit_stl_mini.md

Pour chaque fichier de cad/out*/stl et cad/out*/essais :
  1. maillage : fermé (étanche), sans facette inversée, un seul morceau (PrusaSlicer --info + trimesh) ;
  2. plateau : posé à z = 0, surface de contact au premier calque, tient dans 256 mm ;
  3. tranchage réel avec PrusaSlicer (buse 0,4, couches de 0,2 mm) et les réglages de la notice :
     le trancheur doit réussir, et pour les pièces dont les parois sont dessinées (1 paroi, 0 %),
     le volume de plastique déposé doit correspondre au volume du modèle (sinon des parois fines
     ou des âmes ont disparu au tranchage) ;
  4. temps et filament de chaque pièce.
"""
import concurrent.futures as cf
import os
import re
import subprocess
import sys
import tempfile

import numpy as np
import trimesh

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
import build as B  # noqa: E402
import pieces as P  # noqa: E402
from porte_a_faux import _couche  # noqa: E402
from params import *  # noqa: E402,F403

RACINE = os.path.dirname(ICI)
TMP = tempfile.mkdtemp(prefix="audit_")
LARGEUR = 0.45      # largeur de ligne (buse 0,4)


def reglages(nom):
    """(parois, remplissage, couches dessus/dessous, matériau) d'après l'inventaire et la notice."""
    base = re.sub(r"_(droit|gauche)$", "", nom)
    for n, fn, q, mat, orient, paroi, rempl, mir in P.inventaire():
        if n == base:
            if paroi is None:          # parois déjà dessinées : 1 paroi, 0 %, rien dessus/dessous
                couches = 3 if base.startswith(("aileron", "profondeur", "fuselage_nez")) else 0
                # nombre de lignes pour remplir l'épaisseur dessinée : aile 0,6 mm -> 1 ;
                # gouvernes 0,8 mm et fuselage 1,0 mm -> 2
                if base.startswith(("aileron", "profondeur")):
                    parois = 2
                elif base.startswith("fuselage"):
                    parois = max(1, round(PAROI_FUS / LARGEUR))
                else:
                    parois = 1
                return parois, 0.0, couches, mat, True
            return max(2, round(paroi / LARGEUR)), rempl, 4, mat, False
    # pièces du kit d'essai
    if nom.startswith("3_"):           # tranches de fuselage : mêmes réglages que le fuselage
        return max(1, round(PAROI_FUS / LARGEUR)), 0.0, 0, P.MATERIAU_LEGER, True
    if nom.startswith("2_"):
        return 1, 0.0, 0, P.MATERIAU_LEGER, True
    if nom.startswith("1_"):
        return 3, 0.15, 4, "PETG", False
    return 3, 0.3, 4, "PETG", False


def volume_parois(m, parois, pas=0.5):
    """Volume (cm³) que les parois peuvent occuper : dans chaque couche, la bande de
    parois x largeur le long des bords. Les zones plus épaisses restent creuses à 0 % de
    remplissage (normal) ; une paroi trop fine pour le trancheur, elle, manquerait au dépôt."""
    e, v = parois * LARGEUR, 0.0
    for z in np.arange(pas / 2, m.bounds[1, 2], pas):
        c = _couche(m, z)
        if c is not None and not c.is_empty:
            v += (c.area - c.buffer(-e).area) * pas
    return v / 1000.0


def config(parois, rempl, couches, mat, hauteur):
    temp = {"PETG": 240, "TPU 95A": 225}.get(mat, 215)
    lignes = {
        "bed_shape": "0x0,256x0,256x256,0x256", "max_print_height": 256, "nozzle_diameter": 0.4,
        "filament_diameter": 1.75, "layer_height": 0.2, "first_layer_height": 0.2,
        "perimeters": parois, "fill_density": f"{rempl * 100:.0f}%", "fill_pattern": "rectilinear" if rempl >= 0.99 else "gyroid",
        "top_solid_layers": couches, "bottom_solid_layers": couches, "perimeter_generator": "arachne",
        "temperature": temp, "first_layer_temperature": temp, "bed_temperature": 60,
        "first_layer_bed_temperature": 60, "skirts": 0, "brim_width": 5 if hauteur > 60 else 0,
        "support_material": 0, "gcode_flavor": "marlin2", "extrusion_width": LARGEUR,
        "perimeter_extrusion_width": LARGEUR, "external_perimeter_extrusion_width": LARGEUR,
        "infill_extrusion_width": LARGEUR, "complete_objects": 0,
    }
    chemin = os.path.join(TMP, f"c_{parois}_{rempl}_{couches}_{temp}_{lignes['brim_width']}.ini")
    with open(chemin, "w") as f:
        for k, v in lignes.items():
            f.write(f"{k} = {v}\n")
    return chemin


def info(chemin):
    out = subprocess.run(["prusa-slicer", "--info", chemin], capture_output=True, text=True).stdout
    d = dict(re.findall(r"^(\w+) = (.*)$", out, re.M))
    return d


def un_fichier(chemin):
    nom = os.path.splitext(os.path.basename(chemin))[0]
    r = dict(nom=nom, dossier=os.path.basename(os.path.dirname(chemin)), defauts=[])
    m = trimesh.load(chemin)
    r["volume"] = m.volume / 1000.0
    # morceaux réels : les coques de volume négatif sont des cavités fermées à l'intérieur
    # d'une pièce creuse (aileron entre ses âmes), imprimées normalement par le trancheur
    r["corps"] = sum(1 for c in m.split(only_watertight=False) if c.volume > 0)
    r["etanche"] = bool(m.is_watertight)
    r["dims"] = m.extents
    zmin = m.bounds[0, 2]
    bas = (m.face_normals[:, 2] < -0.99) & (m.triangles_center[:, 2] < zmin + 0.05)
    r["contact"] = m.area_faces[bas].sum()
    d = info(chemin)
    r["manifold"] = d.get("manifold", "?").strip() == "yes"
    r["open_edges"] = int(d.get("open_edges", "0") or 0)
    if not (r["etanche"] and r["manifold"] and r["open_edges"] == 0):
        r["defauts"].append("maillage non fermé")
    if r["corps"] != 1:
        r["defauts"].append(f"{r['corps']} morceaux séparés")
    if abs(zmin) > 0.01:
        r["defauts"].append(f"pas posé sur le plateau (z min = {zmin:.2f})")
    if max(r["dims"][:2]) > PLATEAU - MARGE_PLATEAU or r["dims"][2] > PLATEAU - MARGE_PLATEAU:
        r["defauts"].append("trop grand pour le plateau")
    if r["contact"] < 25:
        r["defauts"].append(f"très petite surface au plateau ({r['contact']:.0f} mm²)")
    parois, rempl, couches, mat, dessinee = reglages(nom)
    r.update(parois=parois, rempl=rempl, couches=couches, mat=mat, dessinee=dessinee)
    gcode = os.path.join(TMP, nom + "_" + r["dossier"] + ".gcode")
    p = subprocess.run(["prusa-slicer", "--export-gcode", "--load", config(parois, rempl, couches, mat, r["dims"][2]),
                        "--output", gcode, chemin], capture_output=True, text=True, timeout=900)
    texte = p.stdout + p.stderr
    r["avertissements"] = sorted(set(l.strip() for l in texte.splitlines()
                                     if re.search(r"(?i)warning|error|empty|floating|unsupported|failed", l)
                                     and "Reversing even wall line" not in l))   # message interne d'Arachne
    if p.returncode != 0 or not os.path.exists(gcode):
        r["defauts"].append("le tranchage a échoué")
        return r
    g = open(gcode, errors="ignore").read()
    cm3 = re.search(r"filament used \[cm3\] = ([\d.]+)", g)
    tps = re.search(r"estimated printing time \(normal mode\) = (.+)", g)
    r["depose"] = float(cm3.group(1)) if cm3 else 0.0
    r["temps"] = tps.group(1).strip() if tps else "?"
    if dessinee and r["volume"] > 0:
        r["attendu"] = volume_parois(m, parois)
        r["ratio"] = r["depose"] / r["attendu"]
        if r["ratio"] < 0.90:
            r["defauts"].append(f"seulement {r['ratio']:.0%} des parois déposées : des parois fines disparaissent")
    os.remove(gcode)
    return r


def minutes(t):
    tot = 0
    for v, u in re.findall(r"(\d+)([dhms])", t):
        tot += int(v) * {"d": 1440, "h": 60, "m": 1, "s": 1 / 60}[u]
    return tot


def main():
    out = os.path.join(ICI, "out" if VERSION == "dfr" else f"out_{VERSION}")
    fichiers = sorted([os.path.join(out, "stl", f) for f in os.listdir(os.path.join(out, "stl")) if f.endswith(".stl")]
                      + [os.path.join(out, "essais", f) for f in os.listdir(os.path.join(out, "essais"))
                         if f.endswith(".stl")])
    with cf.ProcessPoolExecutor(4) as ex:
        res = list(ex.map(un_fichier, fichiers))
    titre = "Huard DFR" if VERSION == "dfr" else "Huard Mini"
    mauvais = [r for r in res if r["defauts"]]
    L = [f"# Audit des fichiers STL — {titre}\n",
         "Généré par `cad/audit_stl.py`. Contrôle des **fichiers STL livrés** (pas du modèle CAD) : maillage, "
         "pose sur le plateau, et **tranchage réel avec PrusaSlicer 2.7** (buse 0,4 mm, couches de 0,2 mm, "
         "réglages de la notice). Pour les pièces dont les parois sont dessinées (0 % de remplissage), "
         "le plastique déposé doit égaler, couche par couche, ce que les parois peuvent couvrir (le long des "
         "bords, sur parois x 0,45 mm) : sinon, des parois ou des âmes trop fines disparaîtraient au "
         "tranchage. Les zones plus épaisses (autour des fourreaux) restent creuses à 0 %, c'est normal.\n",
         f"**Résultat : {len(res)} fichiers, " + ("aucun défaut.**\n" if not mauvais else
                                                  f"{len(mauvais)} avec défaut.**\n")]
    L.append("| Fichier | Maillage | Morceaux | Au plateau | Réglages | Déposé / parois attendues | Temps | Défauts |")
    L.append("|---|---|---:|---:|---|---:|---:|---|")
    tot = 0
    for r in res:
        reg = f"{r['parois']} paroi(s), {r['rempl']:.0%}, {r['couches']} couche(s)"
        ratio = f"{r.get('ratio', 0):.0%}" if r.get("dessinee") else "—"
        tot += minutes(r.get("temps", ""))
        L.append(f"| {r['dossier']}/{r['nom']} | {'fermé' if r['etanche'] and r['manifold'] else '**ouvert**'} | "
                 f"{r['corps']} | {r['contact']:.0f} mm² | {reg} | {ratio} | {r.get('temps', '?')} | "
                 f"{'; '.join(r['defauts']) or '✅'} |")
    L.append(f"\nTemps total estimé par PrusaSlicer (pièces + kit d'essai, un exemplaire de chaque fichier) : "
             f"**{tot / 60:.0f} h**. Bambu Studio sur la A1 est en général plus rapide.\n")
    av = [(r["nom"], a) for r in res for a in r["avertissements"]]
    if av:
        L.append("## Messages du trancheur\n")
        L += [f"- {n} : {a}" for n, a in av]
    suf = "" if VERSION == "dfr" else f"_{VERSION}"
    with open(os.path.join(RACINE, "docs", f"audit_stl{suf}.md"), "w") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))
    return 1 if mauvais else 0


if __name__ == "__main__":
    sys.exit(main())
