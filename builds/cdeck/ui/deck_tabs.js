"use strict";
// deck_tabs.js — left rail + FILL_TABS + pane geom cdeckPaneBoard:v4
(function () {
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

  var PANE_LOADERS = {
    open: function (stage) {
      if (window.cdeckPaneOpen && typeof window.cdeckPaneOpen.paint === "function") {
        window.cdeckPaneOpen.paint(stage);
      } else {
        stage.textContent = "open pane UNMEASURED";
      }
    },
  };

  function stageEl() {
    return document.getElementById("deck-stage");
  }

  function selectTab(name) {
    var stage = stageEl();
    if (!stage) return;
    var loader = PANE_LOADERS[name];
    if (loader) {
      loader(stage);
      return;
    }
    stage.textContent = name + " — UNMEASURED this slice";
  }

  function buildRail() {
    var rail = document.querySelector(".deck-tabs-rail") || document.querySelector(".tab-rail");
    if (!rail) return;
    rail.innerHTML = "";
    Object.keys(FILL_TABS).forEach(function (name) {
      var btn = document.createElement("button");
      btn.className = "tab-btn";
      btn.setAttribute("data-tab", name);
      btn.textContent = name;
      btn.addEventListener("click", function () {
        selectTab(name);
      });
      rail.appendChild(btn);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", buildRail);
  } else {
    buildRail();
  }
})();
