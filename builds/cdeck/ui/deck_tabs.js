"use strict";
// deck_tabs.js — left rail + FILL_TABS + Sessions pane host inject (cdeckPaneBoard:v4)
(function () {
  // FILL_TABS maps tab name to pane constructor key.
  // Order follows CODER_BRIEF extra-pane tab order.
  var FILL_TABS = {
    studio: "studio",
    runs: "runs",
    orders: "orders",
    review: "review",
    gitur: "gitur",
    surfaces: "surfaces",
    recents: "recents",
    voice: "voice",
    system: "system",
    models: "models",
    backup: "backup",
    tools: "tools",
    clock: "clock",
    open: "open",
    settings: "settings",
    profiles: "profiles",
    forge: "forge",
    crucible: "crucible",
    diligence: "diligence",
    docket: "docket",
    ups: "ups",
    differentiator: "differentiator",
    website: "website",
  };

  var _sessionsHostReady = false;

  function ensureSessionsHosts(done) {
    var host = document.getElementById("cdeck-pane-host");
    if (!host) {
      if (done) done(false);
      return;
    }
    function afterHosts() {
      _sessionsHostReady = true;
      if (typeof window.__cdeck_bootSessionKit === "function") {
        window.__cdeck_bootSessionKit();
      }
      if (done) done(true);
    }
    if (document.getElementById("pane-sessions-recents")) {
      afterHosts();
      return;
    }
    fetch("deck_more.html", { cache: "no-store" })
      .then(function (r) { return r.ok ? r.text() : Promise.reject(new Error("deck_more.html")); })
      .then(function (html) {
        host.insertAdjacentHTML("beforeend", html);
        afterHosts();
      })
      .catch(function () {
        if (done) done(false);
      });
  }

  function activateRecents() {
    ensureSessionsHosts(function (ok) {
      if (!ok) return;
      var fill = window.__cdeck_fillTab && window.__cdeck_fillTab.recents;
      if (typeof fill === "function") fill();
    });
  }

  function buildRail() {
    var rail = document.querySelector(".tab-rail");
    if (!rail) return;
    Object.keys(FILL_TABS).forEach(function (name) {
      var btn = document.createElement("button");
      btn.className = "tab-btn";
      btn.setAttribute("data-tab", name);
      btn.textContent = name;
      rail.appendChild(btn);
    });
    rail.addEventListener("click", function (e) {
      var btn = e.target && e.target.closest ? e.target.closest(".tab-btn[data-tab]") : null;
      if (!btn) return;
      if (btn.getAttribute("data-tab") === "recents") activateRecents();
    });
    /* Prefetch Sessions hosts so kit + ROLLED can bind without waiting for a click. */
    ensureSessionsHosts(function () {});
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", buildRail);
  } else {
    buildRail();
  }
})();
