/*
 * engines-lobby-n.js
 * Does not edit site/engines.js. Load this file after engines.js.
 * engines.js runs the board at once and adds #lobby only when players
 * is "multi". This wrapper holds the original LMN_PLAY until the lobby
 * match exists, then calls it. The 18 engine functions are not copied
 * and are not changed. They still do not read LMN_MATCH.
 * higher.html, tiles.html, and derby.html are separate pages. This file
 * does not wrap them. Those pages still read the four role names.
 */
(function (root) {
  if (!root.document || typeof root.LMN_PLAY !== "function") return;
  var enginePlay = root.LMN_PLAY;

  function esc(v) {
    return String(v == null ? "" : v).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  function waitScreen(def, playRoot) {
    playRoot.innerHTML = '<p class="kicker">' + (def.players === "multi" ? "MULTIPLAYER" : "SINGLE") +
      " · AFTER " + esc(def.inspired) + "</p><h2>" + esc(def.title) + "</h2><p class=\"secondary\">" +
      esc(def.better) + "</p><p class=\"secondary\">The board starts when the match is full, or when the fill clock puts AI in the open seats. The engine loop on this page is still local.</p>" +
      '<div id="lobby" data-game="' + esc(def.id) + '"></div>';
    if (root.LMN_MOUNT_LOBBY) root.LMN_MOUNT_LOBBY(playRoot.querySelector("#lobby"));
  }

  root.LMN_PLAY = function (def, playRoot) {
    if (!def || !playRoot) return;
    playRoot._lmnDef = def;
    playRoot.setAttribute("data-lmn-play", "1");
    if (playRoot.getAttribute("data-lmn-started") === "1") {
      enginePlay(def, playRoot);
      return;
    }
    waitScreen(def, playRoot);
  };

  root.LMN_ON_MATCH = function (match, lobbyHost) {
    var playRoot = lobbyHost && lobbyHost.closest ? lobbyHost.closest("[data-lmn-play]") : null;
    if (!playRoot || !playRoot._lmnDef || !match) return;
    if (playRoot.getAttribute("data-lmn-started") === "1") return;
    if (match.game !== playRoot._lmnDef.id) return;
    playRoot.setAttribute("data-lmn-started", "1");
    enginePlay(playRoot._lmnDef, playRoot);
  };

  root.LMN_REMATCH = function (lobbyHost) {
    var playRoot = lobbyHost && lobbyHost.closest ? lobbyHost.closest("[data-lmn-play]") : null;
    if (!playRoot || !playRoot._lmnDef) return;
    playRoot.removeAttribute("data-lmn-started");
    root.LMN_PLAY(playRoot._lmnDef, playRoot);
  };
})(typeof window !== "undefined" ? window : globalThis);
