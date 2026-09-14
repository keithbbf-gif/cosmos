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

  function activateTab(name) {
    var host = document.getElementById("cdeck-pane-host");
    if (!host) return;
    var rail = document.querySelector(".tab-rail");
    if (rail) {
      rail.querySelectorAll(".tab-btn").forEach(function (b) {
        b.classList.toggle("active", b.getAttribute("data-tab") === name);
      });
    }
    if (name === "surfaces" && typeof window.loadSurfacesPane === "function") {
      window.loadSurfacesPane(host);
      return;
    }
    host.innerHTML = '<div class="pane-stub" data-tab="' + name + '">' + name + "</div>";
  }

  function buildRail() {
    var rail = document.querySelector(".tab-rail");
    if (!rail) return;
    Object.keys(FILL_TABS).forEach(function (name) {
      var btn = document.createElement("button");
      btn.className = "tab-btn";
      btn.setAttribute("data-tab", name);
      btn.textContent = name;
      btn.addEventListener("click", function () { activateTab(name); });
      rail.appendChild(btn);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", buildRail);
  } else {
    buildRail();
  }
})();
