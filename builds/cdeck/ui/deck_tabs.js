(function () {
  "use strict";

  /* Left-rail tabs that lazy-fill pane bodies (not the extra-pane studio/forge set). */
  var PANE_CELL_W = 160;
  var PANE_CELL_H = 120;

  var FILL_TABS = {
    studio: "studio",
    runs: "runs",
    orders: "orders",
    gitur: "gitur",
    forge: "forge",
    crucible: "crucible",
    recents: "recents",
    clock: "clock",
    backup: "backup",
    tools: "tools",
    system: "system",
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
    if (el && !el.dataset.filled) el.dataset.filled = "1";
  }

  function loadFillTabs() {
    Object.keys(FILL_TABS).forEach(fillTab);
  }

  window.cdeckPaneBoard = cdeckPaneBoard;
  window.FILL_TABS = FILL_TABS;
  window.cdeckLoadFillTabs = loadFillTabs;
})();
