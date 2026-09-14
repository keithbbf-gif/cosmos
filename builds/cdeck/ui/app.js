/* builds/cdeck/ui/app.js — transport + extra-pane surfaces (renderSurfaces). */

(function () {
  "use strict";

  var FETCH_TO_MS = 8000;
  var cfg = window.__CDECK_CFG || { base: "http://127.0.0.1:8770", token: "" };

  /** Five canon storage names — always painted; missing payload → UNMEASURED. */
  var CANON_SURFACES = ["ROLD", "ITC", "GDX", "ODX", "TB1"];

  function apiCall(path, opts) {
    var method = (opts && opts.method) || "GET";
    var ctl = new AbortController();
    var timer = setTimeout(function () { ctl.abort(); }, FETCH_TO_MS);
    var url = cfg.base.replace(/\/+$/, "") + path;
    var headers = cfg.token ? { Authorization: "Bearer " + cfg.token } : {};
    var init = { method: method, headers: headers, signal: ctl.signal, cache: "no-store" };
    if (opts && opts.body !== undefined) {
      headers["Content-Type"] = "application/json";
      init.body = JSON.stringify(opts.body);
    }
    return fetch(url, init)
      .then(function (r) {
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
            var msg = j.error ? String(j.error) : "HTTP " + r.status;
            var eN = new Error(msg);
            eN.status = r.status;
            eN.json = j;
            throw eN;
          }
          return j;
        });
      })
      .catch(function (e) {
        clearTimeout(timer);
        throw e;
      });
  }

  function apiGet(path) { return apiCall(path); }
  function apiPost(path, body) { return apiCall(path, { method: "POST", body: body }); }

  window.apiCall = apiCall;
  window.apiGet = apiGet;
  window.apiPost = apiPost;
  if (window.cdeckHeader) {
    window.cdeckHeader.apiGet = apiGet;
    window.cdeckHeader.apiPost = apiPost;
  }

  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }

  function canonId(row) {
    if (!row) return "";
    var raw = row.id != null ? row.id : row.label;
    return String(raw || "").trim().toUpperCase();
  }

  function indexPayload(rows) {
    var map = Object.create(null);
    (rows || []).forEach(function (r) {
      var k = canonId(r);
      if (k) map[k] = r;
    });
    return map;
  }

  function cellReach(row) {
    if (!row || row.reachable === null || row.reachable === undefined) {
      return "UNMEASURED";
    }
    return row.reachable ? "yes" : "no";
  }

  function cellNum(v) {
    if (v === null || v === undefined) return "UNMEASURED";
    return String(v);
  }

  /**
   * Paint canon rows (never omitted) and off-canon payload rows in a separate block.
   * @param {HTMLElement} host
   * @param {{surfaces?: object[], error?: string}} payload
   */
  function renderSurfaces(host, payload) {
    if (!host) return;
    var rows = payload && payload.surfaces;
    if (!Array.isArray(rows)) rows = [];
    var byId = indexPayload(rows);
    var offCanon = rows.filter(function (r) {
      return CANON_SURFACES.indexOf(canonId(r)) < 0;
    });

    var err = payload && payload.error ? esc(payload.error) : "";
    var html = '<section class="surfaces-pane" data-pane="surfaces">';
    html += '<div class="surfaces-toolbar">';
    html += '<button type="button" id="surfaces-check-btn" class="surfaces-check">check</button>';
    if (err) html += '<span class="surfaces-err">' + err + "</span>";
    html += "</div>";

    html += '<table class="surfaces-canon" aria-label="Canon surfaces">';
    html += "<thead><tr><th>surface</th><th>reachable</th><th>free_gb</th><th>age_s</th></tr></thead><tbody>";
    CANON_SURFACES.forEach(function (name) {
      var row = byId[name] || null;
      html += "<tr data-canon-surface=\"" + esc(name) + "\">";
      html += "<td>" + esc(name) + "</td>";
      html += "<td>" + esc(cellReach(row)) + "</td>";
      html += "<td>" + esc(cellNum(row && row.free_gb)) + "</td>";
      html += "<td>" + esc(cellNum(row && row.age_s)) + "</td>";
      html += "</tr>";
    });
    html += "</tbody></table>";

    html += '<div class="surfaces-off-canon">';
    html += "<h3>off-canon</h3>";
    if (!offCanon.length) {
      html += '<p class="surfaces-off-canon-empty">none</p>';
    } else {
      html += '<table class="surfaces-off-canon-table"><thead><tr>';
      html += "<th>id</th><th>kind</th><th>reachable</th><th>free_gb</th><th>age_s</th>";
      html += "</tr></thead><tbody>";
      offCanon.forEach(function (r) {
        html += "<tr>";
        html += "<td>" + esc(r.id || canonId(r)) + "</td>";
        html += "<td>" + esc(r.kind || "UNMEASURED") + "</td>";
        html += "<td>" + esc(cellReach(r)) + "</td>";
        html += "<td>" + esc(cellNum(r.free_gb)) + "</td>";
        html += "<td>" + esc(cellNum(r.age_s)) + "</td>";
        html += "</tr>";
      });
      html += "</tbody></table>";
    }
    html += "</div></section>";

    host.innerHTML = html;
    var btn = host.querySelector("#surfaces-check-btn");
    if (btn) {
      btn.addEventListener("click", function () {
        refreshSurfaces(host);
      });
    }
  }

  function refreshSurfaces(host) {
    return apiGet("/api/v1/surfaces")
      .then(function (body) {
        renderSurfaces(host, body || {});
      })
      .catch(function (e) {
        renderSurfaces(host, {
          surfaces: [],
          error: e && e.message ? e.message : String(e),
        });
      });
  }

  function loadSurfacesPane(host) {
    renderSurfaces(host, { surfaces: [] });
    return refreshSurfaces(host);
  }

  window.CANON_SURFACES = CANON_SURFACES.slice();
  window.renderSurfaces = renderSurfaces;
  window.loadSurfacesPane = loadSurfacesPane;
})();
