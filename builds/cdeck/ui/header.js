/* builds/cdeck/ui/header.js — cDeck header chrome
 * Handles stream picker and connection banner.
 * Do not touch JACK'S MESH / Signal Core / RING_NODES here.
 */
"use strict";

(function () {
  /* ORC BootUP stream picker — read from Core /api/v1/status */
  function updateConnectionBanner(baseUrl, token) {
    var url = baseUrl + "/api/v1/status";
    var headers = token ? { "Authorization": "Bearer " + token } : {};
    fetch(url, { headers: headers })
      .then(function (r) { return r.json(); })
      .then(function (body) {
        var lbl = document.getElementById("cdeck-conn-label");
        if (lbl) {
          lbl.textContent = body.ok ? "Connected" : "Disconnected";
          lbl.className = body.ok ? "conn-ok" : "conn-fail";
        }
      })
      .catch(function () {
        var lbl = document.getElementById("cdeck-conn-label");
        if (lbl) { lbl.textContent = "Offline"; lbl.className = "conn-fail"; }
      });
  }

  document.addEventListener("DOMContentLoaded", function () {
    /* btnReload — kept per cdeck-shell-v12 */
    var btn = document.getElementById("btnReload");
    if (btn) {
      btn.addEventListener("click", function () { location.reload(); });
    }
    updateConnectionBanner(
      (window._cosmosState && window._cosmosState.baseUrl) || "http://127.0.0.1:8770",
      (window._cosmosState && window._cosmosState.token) || ""
    );
  });
})();
