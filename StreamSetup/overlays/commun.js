// Code partagé par tous les écrans. Pas besoin de le modifier :
// les réglages sont dans config.js.
(function () {
  "use strict";

  var DEFAUTS = {
    nom: "TonNom",
    couleur: "#8B5CF6",
    couleur2: "#22D3EE",
    reseaux: [],
    horaire: "",
    messages: [],
    debut: { titre: "Le stream commence bientôt", minutes: 5, heure: "", zero: "C'est parti!" },
    pause: { titre: "Je reviens dans un instant" },
    fin: { titre: "Merci d'avoir été là!", sousTitre: "" },
    bandeau: { heure: true },
    cadre: { anime: true },
    chat: {
      chaineTwitch: "",
      maxMessages: 12,
      dureeSecondes: 0,
      masquerCommandes: true,
      ignorer: [],
      demo: false,
    },
  };

  function estObjet(v) {
    return v !== null && typeof v === "object" && !Array.isArray(v);
  }

  function fusion(base, ajout) {
    var resultat = {};
    Object.keys(base).forEach(function (cle) {
      resultat[cle] = base[cle];
    });
    if (!estObjet(ajout)) return resultat;
    Object.keys(ajout).forEach(function (cle) {
      if (estObjet(base[cle]) && estObjet(ajout[cle])) {
        resultat[cle] = fusion(base[cle], ajout[cle]);
      } else if (ajout[cle] !== undefined && ajout[cle] !== null) {
        resultat[cle] = ajout[cle];
      }
    });
    return resultat;
  }

  var CFG = fusion(DEFAUTS, window.STREAM_CONFIG);
  window.CFG = CFG;

  function couleurValide(c, repli) {
    return /^#([0-9a-f]{3}|[0-9a-f]{6})$/i.test(String(c || "").trim()) ? String(c).trim() : repli;
  }

  var racine = document.documentElement.style;
  racine.setProperty("--accent", couleurValide(CFG.couleur, DEFAUTS.couleur));
  racine.setProperty("--accent-2", couleurValide(CFG.couleur2, DEFAUTS.couleur2));

  function el(tag, classe, texte) {
    var n = document.createElement(tag);
    if (classe) n.className = classe;
    if (texte !== undefined && texte !== null) n.textContent = String(texte);
    return n;
  }

  // Remplit tous les éléments [data-cfg="chemin.vers.valeur"].
  function remplir() {
    var noeuds = document.querySelectorAll("[data-cfg]");
    Array.prototype.forEach.call(noeuds, function (n) {
      var valeur = n.getAttribute("data-cfg").split(".").reduce(function (o, k) {
        return o == null ? o : o[k];
      }, CFG);
      if (valeur === undefined || valeur === null || valeur === "") {
        n.hidden = true;
      } else {
        n.textContent = String(valeur);
      }
    });
  }

  function listeTextes(liste) {
    return (Array.isArray(liste) ? liste : [])
      .map(function (t) { return String(t == null ? "" : t).trim(); })
      .filter(Boolean);
  }

  // Fait défiler des éléments un par un dans `conteneur`, en fondu.
  function rotation(conteneur, elements, delaiMs) {
    if (!conteneur) return;
    conteneur.textContent = "";
    if (!elements.length) {
      conteneur.hidden = true;
      return;
    }
    conteneur.hidden = false;
    var index = 0;
    var actuel = null;

    function suivant() {
      var nouveau = elements[index % elements.length];
      index += 1;
      if (actuel === nouveau && elements.length === 1) return;
      nouveau.classList.add("rotation-item");
      conteneur.appendChild(nouveau);
      // Force le calcul du style avant d'ajouter la classe visible.
      void nouveau.offsetWidth;
      nouveau.classList.add("visible");
      if (actuel) {
        var ancien = actuel;
        ancien.classList.remove("visible");
        setTimeout(function () {
          if (ancien !== nouveau && ancien.parentNode === conteneur) conteneur.removeChild(ancien);
        }, 700);
      }
      actuel = nouveau;
    }

    suivant();
    if (elements.length > 1) setInterval(suivant, delaiMs || 7000);
  }

  function messages(conteneur, delaiMs) {
    rotation(
      conteneur,
      listeTextes(CFG.messages).map(function (t) { return el("span", "message-texte", t); }),
      delaiMs
    );
  }

  function elementReseau(r) {
    var bloc = el("span", "reseau");
    bloc.appendChild(el("span", "reseau-type", r.type));
    bloc.appendChild(el("span", "reseau-texte", r.texte));
    return bloc;
  }

  function reseauxValides() {
    return (Array.isArray(CFG.reseaux) ? CFG.reseaux : []).filter(function (r) {
      return r && String(r.texte || "").trim();
    });
  }

  // Affiche tous les réseaux côte à côte.
  function reseaux(conteneur) {
    if (!conteneur) return;
    conteneur.textContent = "";
    var liste = reseauxValides();
    conteneur.hidden = !liste.length;
    liste.forEach(function (r) { conteneur.appendChild(elementReseau(r)); });
  }

  // Affiche les réseaux un à la fois.
  function reseauxRotation(conteneur, delaiMs) {
    rotation(conteneur, reseauxValides().map(elementReseau), delaiMs);
  }

  function deuxChiffres(n) {
    return (n < 10 ? "0" : "") + n;
  }

  function formatDuree(ms) {
    var total = Math.max(0, Math.round(ms / 1000));
    var h = Math.floor(total / 3600);
    var m = Math.floor((total % 3600) / 60);
    var s = total % 60;
    return (h ? h + ":" + deuxChiffres(m) : deuxChiffres(m)) + ":" + deuxChiffres(s);
  }

  window.Habillage = {
    CFG: CFG,
    el: el,
    remplir: remplir,
    rotation: rotation,
    messages: messages,
    reseaux: reseaux,
    reseauxRotation: reseauxRotation,
    formatDuree: formatDuree,
    deuxChiffres: deuxChiffres,
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", remplir);
  } else {
    remplir();
  }
})();
