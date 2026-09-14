(function () {
  "use strict";

  var PANE_CELL_W = 160;
  var PANE_CELL_H = 120;

  var FILL_TABS = {
    recents: "recents",
    clock: "clock",
    runs: "runs",
    backup: "backup",
    tools: "tools",
    system: "system",
    open: "open",
    profiles: "profiles",
    forge: "forge",
    session: "session-kit",
  };

  var cdeckPaneBoard = {
    schema: "cdeckPaneBoard:v4",
    cell: { w: PANE_CELL_W, h: PANE_CELL_H },
    defaults: {
      system: { x: 0, y: 0, w: PANE_CELL_W, h: PANE_CELL_H },
    },
  };

  function showTab(tabId) {
    var stage = document.getElementById("deck-stage");
    if (!stage) return;
    stage.querySelectorAll(".deck-panel").forEach(function (p) {
      p.hidden = p.id !== "panel-" + FILL_TABS[tabId];
    });
    var rail = document.getElementById("deck-tab-rail");
    if (rail) {
      rail.querySelectorAll(".deck-tab-btn").forEach(function (btn) {
        btn.classList.toggle("on", btn.getAttribute("data-tab") === tabId);
      });
    }
    document.dispatchEvent(
      new CustomEvent("cdeck:tab-selected", { detail: { tab: tabId } }),
    );
  }

  function ensurePanels() {
    var stage = document.getElementById("deck-stage");
    if (!stage) return;
    Object.keys(FILL_TABS).forEach(function (name) {
      var pid = "panel-" + FILL_TABS[name];
      if (!document.getElementById(pid)) {
        var panel = document.createElement("div");
        panel.id = pid;
        panel.className = "deck-panel";
        panel.hidden = true;
        stage.appendChild(panel);
      }
    });
  }

  function buildRail() {
    var rail =
      document.getElementById("deck-tab-rail") ||
      document.querySelector(".deck-tabs-rail") ||
      document.querySelector(".tab-rail");
    if (!rail || rail.dataset.built === "1") return;
    rail.dataset.built = "1";
    ensurePanels();
    Object.keys(FILL_TABS).forEach(function (name) {
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "deck-tab-btn";
      btn.setAttribute("data-tab", name);
      btn.textContent = name;
      btn.addEventListener("click", function () {
        showTab(name);
      });
      rail.appendChild(btn);
    });
    showTab("backup");
  }

  function loadFillTabs() {
    buildRail();
  }

  window.cdeckPaneBoard = cdeckPaneBoard;
  window.FILL_TABS = FILL_TABS;
  window.cdeckLoadFillTabs = loadFillTabs;
  window.cdeckShowTab = showTab;

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", buildRail);
  } else {
    buildRail();
  }
})();
