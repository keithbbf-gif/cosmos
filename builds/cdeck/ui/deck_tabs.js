// builds/cdeck/ui/deck_tabs.js — left rail + FILL_TABS + pane geom cdeckPaneBoard:v4
// IIFE; no ES export. No fetch() — uses apiGet/apiPost from header.js.
(function () {
  "use strict";

  // Tab order for the extra-pane left rail under #cdeck-more.
  // Keys are pane IDs used in deck_more.html and deck_*.js.
  // Previously only the short "extra-pane set" was listed here.
  const FILL_TABS = {
    studio:         { label: "Studio",         api: "/api/v1/studio" },
    runs:           { label: "Runs",           api: "/api/v1/runs_ops" },
    orders:         { label: "Orders",         api: "/api/v1/work_orders" },
    review:         { label: "Review",         api: "/api/v1/review" },
    gitur:          { label: "Gitur",          api: "/api/v1/gitur" },
    surfaces:       { label: "Surfaces",       api: "/api/v1/surfaces_kit" },
    recents:        { label: "Sessions",       api: "/api/v1/recents" },
    voice:          { label: "Voice",          api: "/api/v1/voice_loop" },
    system:         { label: "System",         api: "/api/v1/health" },
    models:         { label: "Models",         api: "/api/v1/model_rater" },
    backup:         { label: "Backup",         api: "/api/v1/backup" },
    tools:          { label: "Tools",          api: "/api/v1/tools_kit" },
    clock:          { label: "Clock",          api: "/api/v1/fleet" },
    open:           { label: "Open",           api: "/api/v1/recents" },
    settings:       { label: "Settings",       api: null },
    forge:          { label: "Forge",          api: null },
    crucible:       { label: "Crucible",       api: null },
    diligence:      { label: "Diligence",      api: null },
    docket:         { label: "Docket",         api: null },
    ups:            { label: "UPS",            api: null },
    differentiator: { label: "Differentiator", api: null },
    website:        { label: "Website",        api: null },
  };

  // Default pane geometry stored under cdeckPaneBoard:v4 in localStorage.
  // w and h are the content-area pixel dimensions for the deck-stage.
  // system pane: 640×340 is the reference size (1280×680 would be doubled).
  const PANE_DEFAULTS = {
    studio:         { w: 900, h: 480 },
    runs:           { w: 760, h: 400 },
    orders:         { w: 760, h: 400 },
    review:         { w: 760, h: 400 },
    gitur:          { w: 820, h: 440 },
    surfaces:       { w: 720, h: 360 },
    recents:        { w: 720, h: 360 },
    voice:          { w: 640, h: 340 },
    system:         { w: 640, h: 340 },
    models:         { w: 720, h: 360 },
    backup:         { w: 640, h: 340 },
    tools:          { w: 720, h: 360 },
    clock:          { w: 640, h: 340 },
    open:           { w: 720, h: 400 },
    settings:       { w: 520, h: 280 },
    forge:          { w: 900, h: 480 },
    crucible:       { w: 900, h: 480 },
    diligence:      { w: 720, h: 360 },
    docket:         { w: 720, h: 360 },
    ups:            { w: 720, h: 360 },
    differentiator: { w: 720, h: 360 },
    website:        { w: 720, h: 360 },
  };

  const PANE_BOARD_KEY = "cdeckPaneBoard:v4";

  function _loadBoard() {
    try {
      var raw = localStorage.getItem(PANE_BOARD_KEY);
      return raw ? JSON.parse(raw) : {};
    } catch (e) {
      return {};
    }
  }

  function _saveBoard(board) {
    try {
      localStorage.setItem(PANE_BOARD_KEY, JSON.stringify(board));
    } catch (e) {}
  }

  function getPaneGeom(tabId) {
    var board = _loadBoard();
    var saved = board[tabId];
    var def = PANE_DEFAULTS[tabId] || { w: 720, h: 360 };
    return saved || def;
  }

  function setPaneGeom(tabId, w, h) {
    var board = _loadBoard();
    board[tabId] = { w: Math.max(200, w | 0), h: Math.max(100, h | 0) };
    _saveBoard(board);
  }

  function buildRail(activeId, onClick) {
    var rail = document.getElementById("deck-rail");
    if (!rail) return;
    rail.innerHTML = "";
    Object.keys(FILL_TABS).forEach(function (id) {
      var cfg = FILL_TABS[id];
      var btn = document.createElement("button");
      btn.className = "rail-tab" + (id === activeId ? " active" : "");
      btn.dataset.pane = id;
      btn.textContent = cfg.label;
      btn.addEventListener("click", function () { onClick(id); });
      rail.appendChild(btn);
    });
  }

  window._deckTabs = {
    FILL_TABS: FILL_TABS,
    PANE_DEFAULTS: PANE_DEFAULTS,
    PANE_BOARD_KEY: PANE_BOARD_KEY,
    getPaneGeom: getPaneGeom,
    setPaneGeom: setPaneGeom,
    buildRail: buildRail,
  };
})();
