/* builds/cdeck/ui/app.js — transport + Clock pane (fleet heartbeats only). */

(function () {
  "use strict";

  var FETCH_TO_MS = 8000;
  var cfg = window.__CDECK_CFG || { base: "http://127.0.0.1:8770", token: "" };

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
          var msg = j.error ? String(j.error) : "HTTP " + r.status;
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

  function esc(s) {
    if (s == null) return "";
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/"/g, "&quot;");
  }

  window.apiCall = apiCall;
  window.apiGet = function (path) { return apiCall(path); };
  window.apiPost = function (path, body) { return apiCall(path, { method: "POST", body: body }); };

  function clockCell(v) {
    if (v === null || v === undefined || v === "") return "UNMEASURED";
    return esc(v);
  }

  /** Clock tab: table rows only from GET /api/v1/fleet (feed heartbeats). */
  function renderClockPane(host) {
    if (!host) return;
    host.innerHTML = '<p class="dim tiny">Clock — loading fleet…</p>';
    apiGet("/api/v1/fleet").then(function (body) {
      var fleet = body && body.fleet;
      if (!fleet || fleet.available !== true) {
        host.innerHTML =
          '<table class="clock-table" data-kind="UNMEASURED"><tbody>' +
          '<tr><th>heartbeat</th><th>worker</th><th>age_s</th><th>state</th><th>pid</th></tr>' +
          '<tr><td colspan="5">UNMEASURED — no fleet GET / feed unavailable</td></tr>' +
          "</tbody></table>";
        return;
      }
      var rows = fleet.clocks;
      if (!Array.isArray(rows) || rows.length === 0) {
        host.innerHTML =
          '<table class="clock-table" data-kind="UNMEASURED"><tbody>' +
          '<tr><th>heartbeat</th><th>worker</th><th>age_s</th><th>state</th><th>pid</th></tr>' +
          '<tr><td colspan="5">UNMEASURED — fleet returned no clock rows</td></tr>' +
          "</tbody></table>";
        return;
      }
      var html =
        '<table class="clock-table" data-source="fleet"><thead><tr>' +
        "<th>heartbeat</th><th>worker</th><th>age_s</th><th>state</th><th>pid</th>" +
        "</tr></thead><tbody>";
      rows.forEach(function (row) {
        if (!row || typeof row !== "object") return;
        html += "<tr>" +
          "<td>" + clockCell(row.heartbeat) + "</td>" +
          "<td>" + clockCell(row.worker) + "</td>" +
          "<td>" + clockCell(row.age_s) + "</td>" +
          "<td>" + clockCell(row.state) + "</td>" +
          "<td>" + clockCell(row.pid) + "</td>" +
          "</tr>";
      });
      html += "</tbody></table>";
      host.innerHTML = html;
    }).catch(function () {
      host.innerHTML =
        '<table class="clock-table" data-kind="UNMEASURED"><tbody>' +
        '<tr><th>heartbeat</th><th>worker</th><th>age_s</th><th>state</th><th>pid</th></tr>' +
        '<tr><td colspan="5">UNMEASURED — fleet GET failed</td></tr>' +
        "</tbody></table>";
    });
  }

  window.renderClockPane = renderClockPane;
})();
