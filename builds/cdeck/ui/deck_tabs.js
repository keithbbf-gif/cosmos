"use strict";
// deck_tabs.js — left rail + FILL_TABS + pane geom cdeckPaneBoard:v4
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
  }

  function onTabClick(ev) {
    var btn = ev.target && ev.target.closest ? ev.target.closest(".tab-btn") : null;
    if (!btn) return;
    var tab = btn.getAttribute("data-tab");
    if (tab === "settings" && window.deckSettings && typeof window.deckSettings.open === "function") {
      ev.preventDefault();
      window.deckSettings.open();
    }
  }

  function init() {
    buildRail();
    document.addEventListener("click", onTabClick);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
