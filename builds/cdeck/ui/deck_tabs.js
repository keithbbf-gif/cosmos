"use strict";
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

  function paneHost() {
    return document.getElementById("cdeck-pane-host")
      || document.querySelector(".deck-tab-shell")
      || document.getElementById("deck-stage");
  }

  function ensurePanel(slot) {
    var host = paneHost();
    if (!host) return null;
    var id = "panel-" + slot;
    var el = document.getElementById(id);
    if (!el) {
      el = document.createElement("div");
      el.id = id;
      el.className = "deck-pane";
      el.hidden = true;
      host.appendChild(el);
    }
    return el;
  }

  function fillTab(name) {
    var slot = FILL_TABS[name];
    if (!slot) return;
    var el = ensurePanel(slot);
    if (!el || el.dataset.filled === "1") return;
    el.dataset.filled = "1";
    if (slot === "clock" && typeof window.renderClockPane === "function") {
      window.renderClockPane(el);
    }
    if (slot === "backup" && typeof window.paintClock === "function") {
      window.paintClock(el);
    }
  }

  function showTab(name) {
    var slot = FILL_TABS[name];
    if (!slot) return;
    fillTab(name);
    var host = paneHost();
    if (!host) return;
    host.querySelectorAll(".deck-pane").forEach(function (p) {
      p.hidden = p.id !== "panel-" + slot;
    });
    var el = document.getElementById("panel-" + slot);
    if (el) el.hidden = false;
  }

  function buildRail() {
    var rail = document.querySelector(".tab-rail")
      || document.querySelector(".deck-tabs-rail");
    if (!rail) return;
    Object.keys(FILL_TABS).forEach(function (name) {
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "tab-btn";
      btn.setAttribute("data-tab", name);
      btn.textContent = name;
      btn.addEventListener("click", function () { showTab(name); });
      rail.appendChild(btn);
    });
  }

  window.FILL_TABS = FILL_TABS;
  window.cdeckLoadFillTabs = function () {
    Object.keys(FILL_TABS).forEach(fillTab);
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", buildRail);
  } else {
    buildRail();
  }
})();
