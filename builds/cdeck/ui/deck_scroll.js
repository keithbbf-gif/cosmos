/* Page-level horizontal pan — grid + panels move as one plane (house panelGeom discipline). */
(function () {
  "use strict";

  var STORE_PREFIX = "deck.pagePan:";
  var activeDrag = null;
  var hosts = [];

  function pagePanKey(pageId) {
    return STORE_PREFIX + String(pageId || "default");
  }

  function readPagePan(pageId) {
    try {
      var raw = localStorage.getItem(pagePanKey(pageId));
      if (!raw) return 0;
      var o = JSON.parse(raw);
      return typeof o.x === "number" && isFinite(o.x) ? o.x : 0;
    } catch (e) {
      return 0;
    }
  }

  function writePagePan(pageId, x) {
    try {
      localStorage.setItem(pagePanKey(pageId), JSON.stringify({ x: x }));
    } catch (e2) {}
  }

  function panPlane(host) {
    return host.querySelector(".deck-page-pan");
  }

  function pageIdForPlane(plane) {
    return (plane && plane.getAttribute("data-deck-page-id")) || "default";
  }

  function applyPan(plane, x) {
    if (!plane) return;
    plane.style.transform = "translate3d(" + x + "px,0,0)";
    plane.setAttribute("data-deck-pan-x", String(x));
  }

  function restorePagePan(host) {
    var plane = panPlane(host);
    if (!plane) return;
    applyPan(plane, readPagePan(pageIdForPlane(plane)));
  }

  function pathHasInnerScroller(event, host) {
    var path = event.composedPath ? event.composedPath() : [event.target];
    for (var i = 0; i < path.length; i++) {
      var n = path[i];
      if (!n || n.nodeType !== 1) continue;
      if (n === host) break;
      if (n.classList && (n.classList.contains("twrap") || n.classList.contains("chip-row"))) {
        return true;
      }
      if (n.classList && n.classList.contains("deck-page-pan")) continue;
      try {
        var st = window.getComputedStyle(n);
        var ox = st.overflowX;
        if ((ox === "auto" || ox === "scroll") && n.scrollWidth > n.clientWidth + 1) {
          return true;
        }
      } catch (e) {}
    }
    return false;
  }

  function wheelDeltaX(event) {
    var dx = event.deltaX || 0;
    if (event.shiftKey && Math.abs(event.deltaY) > Math.abs(dx)) {
      dx = event.deltaY;
    }
    return dx;
  }

  function onWheel(event) {
    var host = event.currentTarget;
    if (pathHasInnerScroller(event, host)) return;
    var dx = wheelDeltaX(event);
    if (!dx) return;
    var plane = panPlane(host);
    if (!plane) return;
    var pageId = pageIdForPlane(plane);
    var x = readPagePan(pageId) - dx;
    writePagePan(pageId, x);
    applyPan(plane, x);
    event.preventDefault();
  }

  function isShellDragTarget(el, plane) {
    if (!plane || !plane.contains(el)) return false;
    if (el.closest(".twrap, .chip-row, button, input, textarea, select, a, label, .panel")) {
      return false;
    }
    return el === plane || el.classList.contains("deck-pan-grid-bg");
  }

  function onPointerDown(event) {
    if (event.button !== 0) return;
    var host = event.currentTarget;
    var plane = panPlane(host);
    if (!isShellDragTarget(event.target, plane)) return;
    var pageId = pageIdForPlane(plane);
    activeDrag = {
      host: host,
      plane: plane,
      pageId: pageId,
      startX: event.clientX,
      startPan: readPagePan(pageId),
      pointerId: event.pointerId
    };
    try {
      host.setPointerCapture(event.pointerId);
    } catch (e) {}
    host.classList.add("deck-pan-dragging");
    event.preventDefault();
  }

  function onPointerMove(event) {
    if (!activeDrag || activeDrag.host !== event.currentTarget) return;
    var dx = event.clientX - activeDrag.startX;
    var x = activeDrag.startPan + dx;
    writePagePan(activeDrag.pageId, x);
    applyPan(activeDrag.plane, x);
  }

  function endDrag(host, event) {
    if (!activeDrag || activeDrag.host !== host) return;
    try {
      host.releasePointerCapture(activeDrag.pointerId);
    } catch (e) {}
    host.classList.remove("deck-pan-dragging");
    activeDrag = null;
  }

  function bindPanHost(host) {
    if (!host || host.__deckPanBound) return;
    host.__deckPanBound = true;
    hosts.push(host);
    restorePagePan(host);
    host.addEventListener("wheel", onWheel, { passive: false });
    host.addEventListener("pointerdown", onPointerDown);
    host.addEventListener("pointermove", onPointerMove);
    host.addEventListener("pointerup", function (ev) {
      endDrag(host, ev);
    });
    host.addEventListener("pointercancel", function (ev) {
      endDrag(host, ev);
    });
    var plane = panPlane(host);
    if (plane) {
      var obs = new MutationObserver(function () {
        restorePagePan(host);
      });
      obs.observe(plane, { attributes: true, attributeFilter: ["data-deck-page-id"] });
    }
  }

  function setPageId(hostOrSelector, pageId) {
    var host =
      typeof hostOrSelector === "string"
        ? document.querySelector(hostOrSelector)
        : hostOrSelector;
    if (!host) return;
    var plane = panPlane(host);
    if (!plane) return;
    plane.setAttribute("data-deck-page-id", pageId);
    restorePagePan(host);
  }

  function stageRoot() {
    var stage = document.getElementById("deck-stage");
    if (!stage) return null;
    return stage.querySelector(".deck-page-pan") || stage;
  }

  function initDeckScroll() {
    document.querySelectorAll(".deck-pan-host").forEach(bindPanHost);
  }

  window.deckScroll = {
    pagePanKey: pagePanKey,
    readPagePan: readPagePan,
    writePagePan: writePagePan,
    restorePagePan: restorePagePan,
    bindPanHost: bindPanHost,
    setPageId: setPageId,
    stageRoot: stageRoot,
    init: initDeckScroll
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initDeckScroll);
  } else {
    initDeckScroll();
  }
}());
