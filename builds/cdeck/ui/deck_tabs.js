(function () {
  "use strict";

  var PANE_CELL_W = 160;
  var PANE_CELL_H = 120;

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
    website: "website"
  };

  var cdeckPaneBoard = {
    schema: "cdeckPaneBoard:v4",
    cell: { w: PANE_CELL_W, h: PANE_CELL_H },
    defaults: {
      system: { x: 0, y: 0, w: PANE_CELL_W, h: PANE_CELL_H }
    }
  };

  function applyPaneGeom(panel, tabId) {
    if (!panel || tabId !== "system") return;
    var def = cdeckPaneBoard.defaults.system;
    panel.style.gridColumn = String(def.x + 1) + " / span " + Math.max(1, Math.round(def.w / PANE_CELL_W));
    panel.style.gridRow = String(def.y + 1) + " / span " + Math.max(1, Math.round(def.h / PANE_CELL_H));
    panel.dataset.paneW = String(def.w);
    panel.dataset.paneH = String(def.h);
  }

  function ensureSystemShell(panel) {
    if (!panel || panel.dataset.shell === "1") return;
    panel.dataset.shell = "1";
    panel.innerHTML =
      '<div class="sys-grid">' +
      '<section id="sys-status" class="sys-block" aria-label="status"></section>' +
      '<section id="sys-health" class="sys-block" aria-label="health"></section>' +
      '<section id="sys-spend" class="sys-block" aria-label="spend"></section>' +
      '<section id="sys-rails" class="sys-block" aria-label="rails"></section>' +
      '<section id="sys-fleet" class="sys-block" aria-label="fleet"></section>' +
      '<section id="sys-nodemap" class="sys-block" aria-label="nodemap"></section>' +
      "</div>";
  }

  function ensureForgeShell(panel) {
    if (!panel || panel.dataset.shell === "1") return;
    panel.dataset.shell = "1";
    panel.innerHTML =
      '<div class="sys-grid">' +
      '<section id="panel-forge-ccr" class="sys-block" aria-label="forge ccr"></section>' +
      '<section id="panel-forge-adv" class="sys-block" aria-label="forge adv"></section>' +
      '<section id="panel-forge-job" class="sys-block" aria-label="forge job"></section>' +
      '<section id="panel-forge-porosity" class="sys-block" aria-label="forge porosity"></section>' +
      '<section id="panel-forge-nodes" class="sys-block" aria-label="forge nodes"></section>' +
      "</div>";
  }

  function showPanel(tabId) {
    var stage = document.getElementById("deck-stage");
    if (!stage) return;
    stage.querySelectorAll(".deck-panel").forEach(function (p) {
      p.hidden = p.getAttribute("data-tab") !== tabId;
    });
    if (tabId === "system" && typeof window.paintSystemTab === "function") {
      window.paintSystemTab();
    }
    if (tabId === "forge" && window.DeckForge && typeof window.DeckForge.refresh === "function") {
      window.DeckForge.refresh();
    }
  }

  function buildRail() {
    var rail = document.getElementById("deck-tab-rail");
    var stage = document.getElementById("deck-stage");
    if (!rail || !stage) return;

    Object.keys(FILL_TABS).forEach(function (name) {
      var slot = FILL_TABS[name];
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "deck-tab-btn";
      btn.setAttribute("data-tab", name);
      btn.textContent = name;
      rail.appendChild(btn);

      var panel = document.createElement("div");
      panel.className = "deck-panel";
      panel.id = "panel-" + slot;
      panel.setAttribute("data-tab", name);
      panel.hidden = true;
      if (name === "system") {
        ensureSystemShell(panel);
        applyPaneGeom(panel, name);
      }
      if (name === "forge") {
        ensureForgeShell(panel);
      }
      stage.appendChild(panel);
    });

    rail.addEventListener("click", function (ev) {
      var btn = ev.target && ev.target.closest ? ev.target.closest(".deck-tab-btn") : null;
      if (!btn) return;
      var tab = btn.getAttribute("data-tab");
      showPanel(tab);
    });
  }

  function loadFillTabs() {
    buildRail();
  }

  window.cdeckPaneBoard = cdeckPaneBoard;
  window.FILL_TABS = FILL_TABS;
  window.cdeckLoadFillTabs = loadFillTabs;

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", loadFillTabs);
  } else {
    loadFillTabs();
  }
})();
