// ─────────────────────────────────────────────────────────────
//  RÉGLAGES DE TON HABILLAGE — le seul fichier à modifier.
//  Ouvre-le avec le Bloc-notes, change le texte entre les
//  guillemets, enregistre, puis dans OBS : clic droit sur la
//  source > Actualiser (ou attends le prochain changement de scène).
// ─────────────────────────────────────────────────────────────
window.STREAM_CONFIG = {
  // Ton nom de streamer, affiché sur les écrans et le bandeau.
  nom: "TonNom",

  // Couleurs principales (format #RRGGBB). Essaie #FF4D6D, #22C55E, #F59E0B…
  couleur: "#8B5CF6",
  couleur2: "#22D3EE",

  // Tes réseaux. Enlève les lignes que tu n'utilises pas.
  reseaux: [
    { type: "Twitch", texte: "twitch.tv/tonnom" },
    { type: "TikTok", texte: "@tonnom" },
    { type: "YouTube", texte: "@tonnom" },
    { type: "Discord", texte: "discord.gg/tonserveur" },
  ],

  // Ton horaire, affiché au début et à la fin du stream.
  horaire: "Lun · Mer · Ven — 19 h",

  // Messages qui défilent (écran de début, pause, bandeau).
  messages: [
    "Bienvenue dans le stream!",
    "Suis la chaîne pour savoir quand je suis en direct",
    "Sois respectueux dans le chat, merci",
    "Tape !discord pour rejoindre la communauté",
  ],

  debut: {
    titre: "Le stream commence bientôt",
    // Durée du compte à rebours en minutes…
    minutes: 5,
    // …ou une heure précise, ex. "19:00" (laisse "" pour utiliser les minutes).
    heure: "",
    // Texte affiché quand le compte à rebours arrive à zéro.
    zero: "C'est parti!",
  },

  pause: {
    titre: "Je reviens dans un instant",
  },

  fin: {
    titre: "Merci d'avoir été là!",
    sousTitre: "On se revoit au prochain stream",
  },

  bandeau: {
    // Affiche l'heure à droite du bandeau.
    heure: true,
  },

  cadre: {
    // Lueur animée autour de la caméra (false = cadre fixe).
    anime: true,
  },

  chat: {
    // Nom de ta chaîne Twitch (sans twitch.tv/). Laisse "" si tu
    // n'es pas sur Twitch : voir le guide pour YouTube, Kick, TikTok.
    chaineTwitch: "",
    // Nombre de messages affichés en même temps.
    maxMessages: 12,
    // Les messages disparaissent après X secondes (0 = jamais).
    dureeSecondes: 0,
    // Cache les commandes (!discord…) et les bots.
    masquerCommandes: true,
    ignorer: ["streamelements", "nightbot", "streamlabs", "moobot", "fossabot", "sery_bot"],
    // true = affiche de faux messages pour placer le chat dans OBS.
    demo: false,
  },
};
