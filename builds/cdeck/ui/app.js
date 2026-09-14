/* builds/cdeck/ui/app.js — transport + Recents painters (OPENED card, explicit empty).
 * Coding history must not steal Recents — do not paint the nav session list.
 * Consolidated from b7-009 + b6-004 (paintCoworkRecents OPENED) + b6-010 (ROLLED lives in kit).
 */

(function () {
  "use strict";

  var FETCH_TO_MS = 8000;
  var OPENED_HEAD_CHARS = 400;
  var cfg = window.__CDECK_CFG || { base: "http://127.0.0.1:8770", token: "" };

  var _state = {
    lastOpenResult: null,
    lastRecentsBody: null,
    selectedId: null
  };

  function isLoopbackBase(base) {
    var h = "";
    try { h = String(new URL(base).hostname || "").toLowerCase(); }
    catch (_) {
      var m = String(base || "").match(/^https?:\/\/(\[::1\]|[^/:]+)/i);
      h = m ? String(m[1]).toLowerCase() : "";
    }
    return h === "127.0.0.1" || h === "localhost" || h === "[::1]" || h === "::1";
  }

  function apiCall(path, opts) {
    var method = (opts && opts.method) || "GET";
    var ctl = new AbortController();
    var timer = setTimeout(function () { ctl.abort(); }, FETCH_TO_MS);
    var url = cfg.base.replace(/\/+$/, "") + path;
    /* live Core :8770 — loopback skip, bearer non-loopback */
    var headers = {};
    if (cfg.token && !isLoopbackBase(cfg.base)) {
      headers["Authorization"] = "Bearer " + cfg.token;
    }
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
      if (e.name === "AbortError") throw new Error("timeout after " + (FETCH_TO_MS / 1000) + "s");
      throw e;
    });
  }

  function apiGet(path) { return apiCall(path); }
  function apiPost(path, body) { return apiCall(path, { method: "POST", body: body }); }

  window.apiCall = apiCall;
  window.apiGet = apiGet;
  window.apiPost = apiPost;

  function esc(s) {
    if (s == null) return "";
    return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/"/g, "&quot;");
  }

  function paintOpenedCard(host, rec) {
    if (!host) return;
    if (!rec || rec.kind !== "OPENED") {
      host.innerHTML = "";
      host.hidden = true;
      return;
    }
    host.hidden = false;
    var title = esc(rec.title || rec.id || "Session");
    var rawText = rec.text != null ? String(rec.text) : "";
    var head = rawText.slice(0, OPENED_HEAD_CHARS);
    var headEsc = esc(head);
    if (rawText.length > OPENED_HEAD_CHARS) {
      headEsc += "<span class=\"recents-ellipsis\">\u2026</span>";
    }
    host.innerHTML =
      '<div class="recents-opened-card" aria-label="Opened session">' +
      '<div class="panel-hd"><h2>OPENED</h2>' +
      '<span class="dim tiny">' + esc(rec.id || "") + "</span></div>" +
      '<div class="panel-bd">' +
      '<div class="recents-opened-title">' + title + "</div>" +
      '<div class="recents-opened-head">' + headEsc + "</div>" +
      '<button type="button" class="recents-close-btn" data-clear-opened>Dismiss</button>' +
      "</div></div>";
    var btn = host.querySelector("[data-clear-opened]");
    if (btn) {
      btn.addEventListener("click", function () { clearOpenResult(); });
    }
  }

  function paintRecentsList(host, rec) {
    if (!host) return;
    rec = rec || {};
    if (!rec.available) {
      var kind = String(rec.kind || "NO_SOURCE");
      host.innerHTML = '<div class="recents-empty explicit-empty">' +
        esc(rec.detail || ("recents unavailable — " + kind)) + "</div>";
      return;
    }
    var rows = Array.isArray(rec.rows) ? rec.rows : [];
    var leaked = 0;
    rows = rows.filter(function (row) {
      if (String((row && row.stream) || "").toLowerCase() === "legal") {
        leaked += 1;
        return false;
      }
      return true;
    });
    if (rows.length === 0) {
      host.innerHTML = '<div class="recents-empty explicit-empty">No session rows — explicit empty</div>' +
        _legalOmittedHtml(rec.n_omitted_legal, leaked);
      return;
    }
    var html = '<ul class="recents-rows">';
    rows.forEach(function (row) {
      var id = row.id || row.session_id || "—";
      var sel = (_state.selectedId && _state.selectedId === id) ? " selected" : "";
      html += '<li><button type="button" class="recents-row' + sel + '" data-recents-id="' + esc(id) + '">' +
        esc(id) + " · " + esc(row.title || "") + "</button></li>";
    });
    html += "</ul>";
    html += _legalOmittedHtml(rec.n_omitted_legal, leaked);
    host.innerHTML = html;
    host.querySelectorAll(".recents-row").forEach(function (btn) {
      btn.addEventListener("click", function () {
        _state.selectedId = btn.getAttribute("data-recents-id");
        host.querySelectorAll(".recents-row").forEach(function (b) { b.classList.remove("selected"); });
        btn.classList.add("selected");
        openRecentsId(_state.selectedId);
      });
    });
  }

  function _legalOmittedHtml(n, leaked) {
    var count = n;
    if (count == null && leaked) count = leaked;
    else if (typeof count === "number") count = count + (leaked || 0);
    if (count == null) {
      return '<div class="recents-omitted dim tiny">legal omitted: UNMEASURED</div>';
    }
    return '<div class="recents-omitted dim tiny">' +
      esc(String(count)) + " legal session(s) omitted.</div>";
  }

  /* paintCoworkRecents — OPENED card (title + transcript head) above the list. */
  function paintCoworkRecents(listBody) {
    _state.lastRecentsBody = listBody || null;
    var listHost = document.getElementById("panel-recents-list");
    var cardHost = document.getElementById("recents-opened-card");
    paintOpenedCard(cardHost, _state.lastOpenResult);
    if (listHost) paintRecentsList(listHost, listBody);
  }

  function clearOpenResult() {
    _state.lastOpenResult = null;
    paintCoworkRecents(_state.lastRecentsBody);
  }

  function openSelected() {
    var id = _state.selectedId;
    var card = document.getElementById("recents-opened-card");
    if (!id) {
      if (card) {
        card.hidden = false;
        card.innerHTML = '<div class="recents-empty explicit-empty">' +
          esc("no session selected — pick a LIST row") + "</div>";
      }
      return;
    }
    openRecentsId(id);
  }

  function openRecentsId(id) {
    if (!id) return;
    var q = "/api/v1/recents?open=1&id=" + encodeURIComponent(id);
    apiGet(q).then(function (rec) {
      _state.lastOpenResult = (rec && rec.kind === "OPENED") ? rec : null;
      paintCoworkRecents(_state.lastRecentsBody);
      if (!_state.lastOpenResult && rec) {
        var card = document.getElementById("recents-opened-card");
        if (card) {
          card.hidden = false;
          if (rec.kind === "LEGAL_OMITTED") {
            card.innerHTML = '<div class="recents-empty explicit-empty">' +
              esc("LEGAL_OMITTED — count-not-content") + "</div>";
          } else {
            card.textContent = String(rec.kind || rec.error || "open failed");
          }
        }
      }
    }).catch(function (e) {
      _state.lastOpenResult = null;
      var card = document.getElementById("recents-opened-card");
      if (card) {
        card.hidden = false;
        var kind = (e && e.json && e.json.kind) || "";
        if (kind === "LEGAL_OMITTED") {
          card.innerHTML = '<div class="recents-empty explicit-empty">' +
            esc("LEGAL_OMITTED — count-not-content") + "</div>";
        } else {
          card.textContent = String((e && e.message) || e);
        }
      }
    });
  }

  /* Recents tab fill — GET /api/v1/recents once per paint (not a poll loop). */
  function paintRecentsTab() {
    var listHost = document.getElementById("panel-recents-list");
    if (!listHost) return;
    listHost.textContent = "GET /api/v1/recents …";
    apiGet("/api/v1/recents").then(function (rec) {
      paintCoworkRecents(rec);
    }).catch(function (e) {
      listHost.textContent = String((e && e.message) || e);
    });
  }

  window.clearOpenResult = clearOpenResult;
  window.paintCoworkRecents = paintCoworkRecents;
  window.__cdeck_openSelected = openSelected;
  window.__cdeck_fillTab = window.__cdeck_fillTab || {};
  window.__cdeck_fillTab.recents = paintRecentsTab;

  document.addEventListener("click", function (e) {
    var act = e.target && e.target.closest ? e.target.closest("[data-sessions-act]") : null;
    if (act) {
      var verb = act.getAttribute("data-sessions-act");
      if (verb === "list") paintRecentsTab();
      else if (verb === "open") openSelected();
      return;
    }
    var btn = e.target && e.target.closest ? e.target.closest(".tab-btn[data-tab]") : null;
    if (!btn) return;
    if (btn.getAttribute("data-tab") === "recents") paintRecentsTab();
  });

  if (document.querySelector('.tab-btn[data-tab="recents"]')) {
    paintRecentsTab();
  }
})();
