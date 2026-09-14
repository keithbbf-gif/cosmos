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

  function paneHost() {
    return document.getElementById("cdeck-pane-host");
  }

  function activateTab(name) {
    var host = paneHost();
    if (!host) return;
    document.querySelectorAll(".tab-btn").forEach(function (b) {
      b.classList.toggle("tab-active", b.getAttribute("data-tab") === name);
    });
    host.innerHTML = "";
    if (name === "studio" && window.DeckStudio && typeof window.DeckStudio.mount === "function") {
      var kit = window.cdeckHeader && window.cdeckHeader.kitForTab("studio");
      window.DeckStudio.mount(host, kit);
      return;
    }
    var stub = document.createElement("div");
    stub.className = "deck-pane-stub";
    stub.textContent = name + " pane";
    host.appendChild(stub);
  }

  function buildRail() {
    var rail = document.querySelector(".tab-rail");
    if (!rail) return;
    Object.keys(FILL_TABS).forEach(function (name) {
      var btn = document.createElement("button");
      btn.className = "tab-btn";
      btn.setAttribute("data-tab", name);
      btn.textContent = name;
      btn.addEventListener("click", function () {
        activateTab(name);
      });
      rail.appendChild(btn);
    });
    activateTab("studio");
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", buildRail);
  } else {
    buildRail();
  }
})();
