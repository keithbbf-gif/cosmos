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
    settings: "settings",
    forge: "forge",
    crucible: "crucible",
    clock: "clock",
    backup: "backup",
    tools: "tools",
    open: "open"
  };

  var cdeckPaneBoard = {
    schema: "cdeckPaneBoard:v4",
    cell: { w: PANE_CELL_W, h: PANE_CELL_H },
    defaults: {
      system: { x: 0, y: 0, w: PANE_CELL_W, h: PANE_CELL_H }
    }
  };

  function fillTab(id) {
    var slot = FILL_TABS[id];
    if (!slot) return;
    var el = document.getElementById("panel-" + slot);
    if (!el) return;
    if (id === "gitur" && typeof window.cdeckBindGiturTab === "function") {
      window.cdeckBindGiturTab();
    }
    el.dataset.filled = "1";
  }

  function loadFillTabs() {
    Object.keys(FILL_TABS).forEach(fillTab);
  }

  window.cdeckPaneBoard = cdeckPaneBoard;
  window.FILL_TABS = FILL_TABS;
  window.cdeckLoadFillTabs = loadFillTabs;
})();
