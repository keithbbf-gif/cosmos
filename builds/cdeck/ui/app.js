/* builds/cdeck/ui/app.js — MESH widgets + jukebox job projection for Runs. */
(function () {
  "use strict";

  var RUNS_POLL_MS = 10000;
  var lastJukeboxBody = null;

  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function $(id) { return document.getElementById(id); }

  /** Normalize jukebox GET body → job rows (never GET /api/v1/jobs for Runs). */
  function jobsFromJukebox(d) {
    if (!d || typeof d !== "object") return [];
    var q = d.queue;
    if (q && Array.isArray(q.jobs)) return q.jobs.slice();
    if (Array.isArray(d.jobs)) return d.jobs.slice();
    if (Array.isArray(d.shown)) return d.shown.slice();
    return [];
  }

  /**
   * renderJobs — paint hook for jukebox fold (list+detail source is GET /jukebox).
   * Legacy { jobs: { id: st } } maps are accepted for MESH summary only.
   */
  function renderJobs(d) {
    if (!d) return;
    lastJukeboxBody = d;
    window.__lastJukeboxBody = d;

    var rows = jobsFromJukebox(d);
    if (rows.length === 0 && d.jobs && typeof d.jobs === "object" && !Array.isArray(d.jobs)) {
      rows = Object.keys(d.jobs).map(function (id) {
        return { job_id: id, st: d.jobs[id] };
      });
    }

    var el = $("mesh-jobs-summary");
    if (!el) return;

    if (rows.length === 0) {
      el.innerHTML = '<span class="dim">no jobs in jukebox fold</span>';
      return;
    }
    var by = {};
    rows.forEach(function (j) {
      var st = String(j.st || j.state || "UNMEASURED").toUpperCase();
      by[st] = (by[st] || 0) + 1;
    });
    var parts = Object.keys(by).sort().map(function (st) {
      return esc(st) + "×" + by[st];
    });
    el.innerHTML = parts.join(" · ");
  }

  function markJukeboxStale(msg) {
    if (lastJukeboxBody && typeof lastJukeboxBody === "object") {
      lastJukeboxBody._pollStale = true;
      lastJukeboxBody._pollStaleReason = msg;
      window.__lastJukeboxBody = lastJukeboxBody;
    }
  }

  function onJukeboxPollError(e) {
    var msg = (e && e.message) ? e.message : String(e);
    markJukeboxStale(msg);
    var el = $("mesh-jobs-summary");
    if (el) {
      el.innerHTML =
        '<span class="bad">' + esc(msg) +
        ' <span class="dim">(poll failed — cached data stale)</span></span>';
    }
    var runs = $("panel-runs");
    if (runs) {
      var box = runs.querySelector(".jukebox-poll-err");
      if (!box) {
        box = document.createElement("div");
        box.className = "jukebox-poll-err bad";
        runs.insertBefore(box, runs.firstChild);
      }
      box.textContent = msg;
    }
    if (typeof addConsole === "function") {
      addConsole("err", "GET /api/v1/jukebox", msg,
        e && e.json ? JSON.stringify(e.json, null, 2) : null);
    }
    if (window.deckStudio && typeof window.deckStudio.paintRunsList === "function" &&
        lastJukeboxBody) {
      window.deckStudio.paintRunsList(lastJukeboxBody);
    }
  }

  function pollJukebox() {
    return apiGet("/api/v1/jukebox").then(function (body) {
      if (body && typeof body === "object") {
        delete body._pollStale;
        delete body._pollStaleReason;
      }
      renderJobs(body);
      var errBox = $("panel-runs") && $("panel-runs").querySelector(".jukebox-poll-err");
      if (errBox) errBox.remove();
      if (window.deckStudio && typeof window.deckStudio.paintRunsList === "function") {
        window.deckStudio.paintRunsList(body);
      }
      return body;
    });
  }

  function startJukeboxPoll() {
    if (window.__jukeboxPollStarted) return;
    window.__jukeboxPollStarted = true;
    pollJukebox().catch(onJukeboxPollError);
    setInterval(function () {
      pollJukebox().catch(onJukeboxPollError);
    }, RUNS_POLL_MS);
  }

  window.RUNS_POLL_MS = RUNS_POLL_MS;
  window.renderJobs = renderJobs;
  window.jobsFromJukebox = jobsFromJukebox;
  window.pollJukebox = pollJukebox;
  window.startJukeboxPoll = startJukeboxPoll;
  window.cdeckEsc = esc;
  window.cdeck$ = $;
}());
