(function () {
  "use strict";
  var FILL_TABS = {
    studio: "Studio",
    runs: "Runs",
    orders: "Orders",
    review: "Review",
    gitur: "Gitur",
    forge: "Forge",
    crucible: "Crucible"
  };

  function paintTabRail() {
    var rail = document.getElementById("deck-tab-rail");
    if (!rail) return;
    rail.innerHTML = Object.keys(FILL_TABS)
      .map(function (id) {
        return (
          '<button type="button" class="deck-tab-btn" data-deck-tab="' +
          id +
          '">' +
          FILL_TABS[id] +
          "</button>"
        );
      })
      .join("");
    rail.querySelectorAll(".deck-tab-btn").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var tab = btn.getAttribute("data-deck-tab") || "stage";
        rail.querySelectorAll(".deck-tab-btn").forEach(function (b) {
          b.classList.toggle("on", b === btn);
        });
        if (window.deckScroll && window.deckScroll.setPageId) {
          window.deckScroll.setPageId("#deck-stage", "extra:" + tab);
        }
        if (tab === "runs" && window.deckStudio && window.deckStudio.mountRunsPanel) {
          window.deckStudio.mountRunsPanel();
        }
      });
    });
  }

  window.FILL_TABS = FILL_TABS;

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", paintTabRail);
  } else {
    paintTabRail();
  }
})();
