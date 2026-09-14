/* builds/cdeck/ui/app.js — transport, live events inspector, map pulse contract. */

(function () {
  "use strict";

  var FETCH_TO_MS = 8000;
  var cfg = window.__CDECK_CFG || { base: "http://127.0.0.1:8770", token: "" };

  function apiCall(path, opts) {
    var method = (opts && opts.method) || "GET";
    var ctl = new AbortController();
    var timer = setTimeout(function () { ctl.abort(); }, FETCH_TO_MS);
    var url = cfg.base.replace(/\/+$/, "") + path;
    var headers = cfg.token ? { "Authorization": "Bearer " + cfg.token } : {};
    var init = { method: method, headers: headers, signal: ctl.signal, cache: "no-store" };
    if (opts && opts.body !== undefined) {
      headers["Content-Type"] = "application/json";
      init.body = JSON.stringify(opts.body);
    }
    return fetch(url, init).then(function (r) {
      clearTimeout(timer);
      return r.text().then(function (txt) {
        var j = {};
        try { j = txt ? JSON.parse(txt) : {}; } catch (_) { j = {}; }
        if (r.status === 503) {
          var detail = j.error ? String(j.error) : "CDECK_PANEL_NOT_COMPOSED";
          var e503 = new Error(detail);
          e503.status = 503;
          e503.json = j;
          throw e503;
        }
        if (!r.ok) {
          var msg = j.error ? String(j.error) : ("HTTP " + r.status);
          var eN = new Error(msg);
          eN.status = r.status;
          eN.json = j;
          throw eN;
        }
        return j;
      });
    }).catch(function (e) {
      clearTimeout(timer);
      throw e;
    });
  }

  window.apiCall = apiCall;
  window.apiGet = function (path) { return apiCall(path); };
  window.apiPost = function (path, body) { return apiCall(path, { method: "POST", body: body }); };

  /* --- live events inspector (EVT-1) --- */
  var FOLLOW_KEYS = ["link_id", "rail", "node", "job_id", "sid", "rid"];
  var feedPinned = true;
  var feedUnseen = 0;
  var feedFollow = null;

  function eventIds(ev) {
    var p = ev && ev.payload, out = [];
    if (!p || typeof p !== "object") return out;
    FOLLOW_KEYS.forEach(function (k) {
      var v = p[k];
      if (v === null || v === undefined || typeof v === "object") return;
      var s = String(v).trim();
      if (s !== "") out.push({ key: k, value: s });
    });
    return out;
  }

  function inspectHtml(ev) {
    var h = '<div class="finspect"><pre>' + JSON.stringify(ev.payload || null, null, 1) + "</pre></div>";
    return h;
  }

  function toggleInspect(row) {
    var open = row.querySelector(".finspect");
    if (open) { open.remove(); row.classList.remove("open"); return; }
    row.classList.add("open");
    row.insertAdjacentHTML("beforeend", inspectHtml(row.__ev || {}));
  }

  var feedEl = document.getElementById("feed");
  if (feedEl) {
    feedEl.addEventListener("click", function (e) {
      var row = e.target && e.target.closest ? e.target.closest(".fevent") : null;
      if (row) toggleInspect(row);
    });
    feedEl.addEventListener("scroll", function () {
      var atTail = (feedEl.scrollHeight - feedEl.scrollTop - feedEl.clientHeight) <= 4;
      if (atTail !== feedPinned) {
        feedPinned = atTail;
        if (atTail) feedUnseen = 0;
      }
    });
  }

  /* --- map pulse (PULSE-1) ---
   * PULSE-1: a node the map does not already hold is NEVER created by an event.
   * Ids come from eventIds(); the only typed home map is PULSE_HOME for events
   * that name no harvestable id. Pending pulses wait for nmapDomReady once. */
  var PULSE_HOME = {
    COMMAND_HANDLED: "CVM"
  };
  var nmapPulsePending = [];
  var nmapDomReady = false;
  var nmapKnown = Object.create(null);

  function nodeOnMap(nodeId) {
    return !!(nodeId && nmapKnown[nodeId]);
  }

  function registerMapNode(nodeId) {
    if (nodeId) nmapKnown[nodeId] = true;
  }

  function pulseFromEvent(ev) {
    var ids = eventIds(ev);
    var nodeId = null;
    if (ids.length) {
      for (var i = 0; i < ids.length; i++) {
        if (ids[i].key === "node") { nodeId = ids[i].value; break; }
        if (ids[i].key === "link_id" || ids[i].key === "rail") {
          nodeId = ids[i].value;
          break;
        }
      }
    }
    if (!nodeId && ev && ev.event && PULSE_HOME[ev.event]) {
      nodeId = PULSE_HOME[ev.event];
    }
    if (!nodeId) return false;
    if (!nmapDomReady) {
      nmapPulsePending.push({ ev: ev, nodeId: nodeId });
      return false;
    }
    if (!nodeOnMap(nodeId)) return false;
    return true;
  }

  function flushPendingPulses() {
    if (!nmapDomReady || !nmapPulsePending.length) return;
    var q = nmapPulsePending.slice();
    nmapPulsePending.length = 0;
    q.forEach(function (item) { pulseFromEvent(item.ev); });
  }

  function nmapDomReadyHook() {
    nmapDomReady = true;
    flushPendingPulses();
  }

  window.__cdeck_pulse = {
    PULSE_HOME: PULSE_HOME,
    pulseFromEvent: pulseFromEvent,
    registerMapNode: registerMapNode,
    nmapDomReady: nmapDomReadyHook,
    nmapPulsePending: nmapPulsePending,
    flushPendingPulses: flushPendingPulses
  };
})();
