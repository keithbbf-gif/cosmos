/* builds/cdeck/ui/app.js — transport, events inspector, map pulse, extra-pane paints. */

(function () {
  "use strict";

  var FETCH_TO_MS = 8000;
  var cfg = window.__CDECK_CFG || { base: "http://127.0.0.1:8770", token: "" };

  function headerKit() {
    return (window.cdeckHeader && window.cdeckHeader.kitForTab)
      ? window.cdeckHeader.kitForTab("app")
      : { apiGet: window.apiGet, apiPost: window.apiPost, tab: "app" };
  }

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
    return '<div class="finspect"><pre>' + JSON.stringify(ev.payload || null, null, 1) + "</pre></div>";
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

  /* --- Talk tab: Web Speech mic state (micHint) stays on Talk, not Voice --- */
  var talkMicRec = null;
  var talkMicOn = false;

  function setMicHint(text) {
    var el = document.getElementById("micHint");
    if (el) el.textContent = text || "";
  }

  function renderTalk(host, kit) {
    if (!host) return;
    host.innerHTML =
      '<section class="pane talk-pane" data-pane="talk">' +
      '<h2>Talk</h2>' +
      '<p class="pane-note">POST /api/v1/voice — transcript never auto-executes.</p>' +
      '<p id="micHint" class="mic-hint" aria-live="polite"></p>' +
      '<button type="button" id="btnTalkMic" class="btn">Talk (mic)</button>' +
      '<textarea id="talkDraft" rows="3" placeholder="review before send"></textarea>' +
      "</section>";
    setMicHint("mic idle — click Talk to arm");
    var btn = document.getElementById("btnTalkMic");
    if (!btn) return;
    btn.addEventListener("click", function () {
      var SR = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (!SR) {
        setMicHint("voice unavailable in this browser — type below");
        return;
      }
      if (talkMicOn && talkMicRec) {
        talkMicRec.stop();
        return;
      }
      talkMicRec = new SR();
      talkMicRec.interimResults = true;
      talkMicRec.onstart = function () {
        talkMicOn = true;
        setMicHint("listening…");
      };
      talkMicRec.onend = function () {
        talkMicOn = false;
        setMicHint("mic idle — click Talk to arm");
      };
      talkMicRec.onerror = function (ev) {
        talkMicOn = false;
        setMicHint("mic error: " + (ev.error || "unknown"));
      };
      talkMicRec.onresult = function (ev) {
        var txt = "";
        for (var i = ev.resultIndex; i < ev.results.length; i++) {
          txt += ev.results[i][0].transcript;
        }
        var box = document.getElementById("talkDraft");
        if (box) box.value = txt.trim();
        setMicHint("captured — review before send (never auto-runs)");
      };
      talkMicRec.start();
    });
  }

  /* --- Voice tab: SGH comm loop status (GET /api/v1/voice_loop); controls are explicit --- */
  function esc(s) {
    return String(s || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }

  function paintVoiceLoop(host, rec, err) {
    var status = document.getElementById("voiceLoopStatus");
    if (!status) return;
    if (err) {
      status.innerHTML = '<div class="errbox">' + esc(err) + "</div>";
      return;
    }
    var legs = (rec && rec.legs) || [];
    var rows = legs.map(function (leg) {
      return "<tr><td>" + esc(leg.id) + "</td><td>" + esc(leg.kind) + "</td><td>" +
        esc(leg.detail || leg.label || "") + "</td></tr>";
    }).join("");
    status.innerHTML =
      "<p class=\"loop-title\">" + esc(rec && rec.loop ? rec.loop : "") + "</p>" +
      "<table class=\"loop-legs\"><tbody>" + rows + "</tbody></table>" +
      "<pre class=\"loop-note\">" + esc(rec && rec.note ? rec.note : "") + "</pre>";
  }

  function refreshVoiceLoop(kit) {
    var host = document.getElementById("deck-stage");
    if (!host || !host.querySelector('[data-pane="voice"]')) return;
    var status = document.getElementById("voiceLoopStatus");
    if (status) status.textContent = "loading GET /api/v1/voice_loop…";
    var get = kit.apiGet || window.apiGet;
    return get("/api/v1/voice_loop").then(function (rec) {
      paintVoiceLoop(host, rec, null);
    }).catch(function (e) {
      paintVoiceLoop(host, null, e.message || String(e));
    });
  }

  function renderVoiceLoop(host, kit) {
    if (!host) return;
    kit = kit || headerKit();
    host.innerHTML =
      '<section class="pane voice-pane" data-pane="voice">' +
      '<h2>Voice loop</h2>' +
      '<p class="pane-note">SGH → GitHub → daemon → GDX → SGH. Status via GET /api/v1/voice_loop only.</p>' +
      '<div class="voice-loop-controls">' +
      '<button type="button" id="btnVoiceRefresh" class="btn">Refresh loop</button>' +
      '<button type="button" id="btnVoiceNewSop" class="btn">File drop SOP</button>' +
      '<input type="text" id="voiceSopName" placeholder="SOP name" aria-label="SOP name" />' +
      "</div>" +
      '<div id="voiceLoopStatus" class="voice-loop-status">click Refresh loop — no auto-run on load</div>' +
      "</section>";
    var refBtn = document.getElementById("btnVoiceRefresh");
    var sopBtn = document.getElementById("btnVoiceNewSop");
    if (refBtn) {
      refBtn.addEventListener("click", function () { refreshVoiceLoop(kit); });
    }
    if (sopBtn) {
      sopBtn.addEventListener("click", function () {
        var nameEl = document.getElementById("voiceSopName");
        var name = nameEl && nameEl.value ? String(nameEl.value).trim() : "";
        if (!name) {
          paintVoiceLoop(host, null, "SOP name required");
          return;
        }
        var post = kit.apiPost || window.apiPost;
        post("/api/v1/voice_loop", { action: "new_sop", name: name }).then(function (rec) {
          paintVoiceLoop(host, rec, null);
        }).catch(function (e) {
          paintVoiceLoop(host, null, e.message || String(e));
        });
      });
    }
    /* Voice tab never paints micHint — mic state is on Talk only (DEFINE). */
  }

  var PANE_RENDER = {
    talk: renderTalk,
    voice: renderVoiceLoop
  };

  function selectTab(name) {
    var host = document.getElementById("deck-stage");
    if (!host) return;
    var kit = headerKit();
    var fn = PANE_RENDER[name];
    if (typeof fn === "function") {
      fn(host, kit);
      return;
    }
    host.innerHTML =
      '<section class="pane empty-pane" data-pane="' + esc(name) + '">' +
      "<h2>" + esc(name) + "</h2>" +
      "<p class=\"pane-note\">pane not composed on this host</p></section>";
  }

  function wireTabRail() {
    var rail = document.getElementById("deck-tab-rail");
    if (!rail) return;
    rail.addEventListener("click", function (e) {
      var btn = e.target && e.target.closest ? e.target.closest("[data-tab]") : null;
      if (!btn) return;
      var tab = btn.getAttribute("data-tab");
      if (!tab) return;
      rail.querySelectorAll(".tab-btn").forEach(function (b) {
        b.classList.toggle("active", b === btn);
      });
      selectTab(tab);
    });
  }

  function boot() {
    wireTabRail();
    /* Extra-pane paints wait for tab click — no loop poll on load. */
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }

  window.cdeckApp = {
    renderVoiceLoop: renderVoiceLoop,
    renderTalk: renderTalk,
    refreshVoiceLoop: refreshVoiceLoop,
    selectTab: selectTab
  };
})();
