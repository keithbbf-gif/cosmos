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

  function pollJukebox() {
    return apiGet("/api/v1/jukebox").then(function (body) {
      renderJobs(body);
      if (window.deckStudio && typeof window.deckStudio.paintRunsList === "function") {
        window.deckStudio.paintRunsList(body);
      }
      return body;
    });
  }

  function startJukeboxPoll() {
    if (window.__jukeboxPollStarted) return;
    window.__jukeboxPollStarted = true;
    pollJukebox().catch(function () { /* pane shows last-good or empty */ });
    setInterval(function () {
      pollJukebox().catch(function () { /* keep filter chip state in deck_studio */ });
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
