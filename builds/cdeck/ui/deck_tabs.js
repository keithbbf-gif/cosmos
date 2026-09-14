/* builds/cdeck/ui/deck_tabs.js — extra-pane tab registry
 * FILL_TABS maps tab name -> extra-pane element id.
 * Do not add JACK'S MESH / Signal Core / RING_NODES here.
 */
"use strict";

var FILL_TABS = {
  forge:    "forge-extra",
  gitur:    "gitur-extra",
  studio:   "studio-extra",
  runs:     "runs-extra",
  review:   "review-extra",
  prompts:  "prompts-extra",
  surfaces: "surfaces-extra",
  talk:     "talk-extra",
  tools:    "tools-extra",
  clock:    "clock-extra",
  voice:    "voice-extra",
  open:     "open-extra",
  system:   "system-extra",
  orders:   "orders-extra",
  crucible: "crucible-extra",
};

function showExtraPane(name) {
  var target = FILL_TABS[name];
  if (!target) return;
  var panes = document.querySelectorAll(".extra-pane");
  for (var i = 0; i < panes.length; i++) {
    panes[i].style.display = panes[i].id === target ? "" : "none";
  }
}

window.FILL_TABS = FILL_TABS;
window.showExtraPane = showExtraPane;
