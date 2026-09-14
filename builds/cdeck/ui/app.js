/* builds/cdeck/ui/app.js — transport + Recents tab (OPENED card, explicit empty).
 * Coding history must not steal Recents — do not paint the nav session list.
 */

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
    var text = rec.text != null ? String(rec.text) : "";
    host.innerHTML =
      '<div class="recents-opened-card panel-hd"><h2>OPENED</h2>' +
      '<span class="dim tiny">' + esc(rec.id || "") + "</span></div>" +
      '<div class="panel-bd"><pre class="recents-opened-text">' + esc(text) + "</pre></div>";
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
    if (rows.length === 0) {
      host.innerHTML = '<div class="recents-empty explicit-empty">No session rows — explicit empty</div>';
      return;
    }
    var html = '<ul class="recents-rows">';
    rows.forEach(function (row) {
      var id = row.id || row.session_id || "—";
      html += '<li><button type="button" class="recents-row" data-recents-id="' + esc(id) + '">' +
        esc(id) + " · " + esc(row.title || "") + "</button></li>";
    });
    html += "</ul>";
    host.innerHTML = html;
    host.querySelectorAll(".recents-row").forEach(function (btn) {
      btn.addEventListener("click", function () {
        openRecentsId(btn.getAttribute("data-recents-id"));
      });
    });
  }

  function openRecentsId(id) {
    if (!id) return;
    var q = "/api/v1/recents?open=1&id=" + encodeURIComponent(id);
    apiGet(q).then(function (rec) {
      paintOpenedCard(document.getElementById("recents-opened-card"), rec);
    }).catch(function (e) {
      var card = document.getElementById("recents-opened-card");
      if (card) {
        card.hidden = false;
        card.textContent = String((e && e.message) || e);
      }
    });
  }

  /* Recents tab fill — GET /api/v1/recents once per paint (not a poll loop). */
  function paintRecentsTab() {
    var listHost = document.getElementById("panel-recents-list");
    var cardHost = document.getElementById("recents-opened-card");
    if (!listHost) return;
    listHost.textContent = "GET /api/v1/recents …";
    apiGet("/api/v1/recents").then(function (rec) {
      paintRecentsList(listHost, rec);
      if (cardHost && (!cardHost.innerHTML || cardHost.hidden)) {
        paintOpenedCard(cardHost, null);
      }
    }).catch(function (e) {
      listHost.textContent = String((e && e.message) || e);
    });
  }

  window.__cdeck_fillTab = window.__cdeck_fillTab || {};
  window.__cdeck_fillTab.recents = paintRecentsTab;

  document.addEventListener("click", function (e) {
    var btn = e.target && e.target.closest ? e.target.closest(".tab-btn[data-tab]") : null;
    if (!btn) return;
    if (btn.getAttribute("data-tab") === "recents") paintRecentsTab();
  });

  if (document.querySelector('.tab-btn[data-tab="recents"]')) {
    paintRecentsTab();
  }
})();
