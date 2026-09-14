(function () {
  "use strict";

  function esc(s) {
    if (s == null) return "";
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/"/g, "&quot;");
  }

  function getApi() {
    if (typeof window.apiGet === "function") return window.apiGet;
    if (typeof window.apiCall === "function") {
      return function (path) { return window.apiCall(path); };
    }
    return null;
  }

  /** Backup pane clock fold: GET /api/v1/backup only; never invents a run. */
  function paintClock(host) {
    if (!host) return;
    var apiGet = getApi();
    if (!apiGet) {
      host.textContent = "UNMEASURED — no Core transport";
      return;
    }
    host.innerHTML = '<p class="dim tiny">Backup clock — loading…</p>';
    apiGet("/api/v1/backup").then(function (body) {
      body = body || {};
      var kind = body.kind || "UNMEASURED";
      var hours = Array.isArray(body.hours) ? body.hours.join(", ") : "UNMEASURED";
      var hb = body.heartbeat;
      var hbKind = hb && typeof hb === "object" ? "OK" : "UNMEASURED";
      var age = hb && hb.last_run_epoch != null ? hb.last_run_epoch : "UNMEASURED";
      host.innerHTML =
        '<div class="backup-clock-fold" data-kind="' + esc(kind) + '">' +
        "<p><strong>Backup fold</strong> " + esc(kind) + "</p>" +
        "<p>Scheduled hours (Core): " + esc(hours) + "</p>" +
        "<p>Heartbeat: " + esc(hbKind) + " · last_run_epoch: " + esc(age) + "</p>" +
        '<p class="dim tiny">' + esc(body.note || "") + "</p>" +
        "</div>";
    }).catch(function () {
      host.textContent = "UNMEASURED — backup GET failed";
    });
  }

  window.paintClock = paintClock;
})();
