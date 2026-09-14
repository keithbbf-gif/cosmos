/* builds/cdeck/ui/deck_studio.js — Studio MOTIF seats + Runs list/detail from /jukebox. */
(function () {
  "use strict";

  var STAGES = [
    "DEFINE", "RESEARCH", "ARCH", "CONSENSUS", "BUILD",
    "CRITICS", "CONSENSUS2", "IMPROVE", "ITERATE"
  ];

  var JOB_ORDER = ["QUEUED", "RUNNING", "FINDINGS", "BROKE", "CLEAN"];
  var INFLIGHT = { QUEUED: true, RUNNING: true };

  /* Survives 10s poll — paintRunsList always reads this, never resets on refresh. */
  var runsFilter = "ALL";
  var selectedJobId = null;
  var lastBody = null;

  function esc(s) {
    return window.cdeckEsc
      ? window.cdeckEsc(s)
      : String(s == null ? "" : s)
          .replace(/&/g, "&amp;")
          .replace(/</g, "&lt;")
          .replace(/>/g, "&gt;");
  }

  function $(id) {
    return window.cdeck$ ? window.cdeck$(id) : document.getElementById(id);
  }

  function jobsFromBody(body) {
    if (window.jobsFromJukebox) return window.jobsFromJukebox(body);
    var q = body && body.queue;
    if (q && Array.isArray(q.jobs)) return q.jobs.slice();
    return [];
  }

  function countsFromBody(body) {
    if (!body) return {};
    var c = body.counts || (body.queue && body.queue.counts) || {};
    return typeof c === "object" ? c : {};
  }

  function findingsInEmit(body) {
    var c = countsFromBody(body);
    if (Number(c.FINDINGS) > 0) return true;
    return jobsFromBody(body).some(function (j) {
      return String(j.st || j.state || "").toUpperCase() === "FINDINGS";
    });
  }

  function stateOf(job) {
    return String(job.st || job.state || "UNMEASURED").toUpperCase();
  }

  function isInflight(job) {
    var st = stateOf(job);
    if (st === "BROKE") return false;
    return !!INFLIGHT[st];
  }

  function jobSortKey(job) {
    var st = stateOf(job);
    var idx = JOB_ORDER.indexOf(st);
    return idx >= 0 ? idx : JOB_ORDER.length + 1;
  }

  function filterJobs(jobs, body) {
    if (runsFilter === "ALL") return jobs.slice();
    if (runsFilter === "INFLIGHT") {
      return jobs.filter(function (j) { return isInflight(j); });
    }
    if (runsFilter === "STALE") {
      return jobs.filter(function (j) {
        return stateOf(j) === "RUNNING" && !!j.stale_flag;
      });
    }
    return jobs.filter(function (j) { return stateOf(j) === runsFilter; });
  }

  function rowHtml(job, selected) {
    var id = job.job_id || job.order_id || job.id || "—";
    var st = stateOf(job);
    var stale = job.stale_flag ? " stale" : "";
    var sel = selected ? " runs-row-selected" : "";
    var cmd = esc(String(job.command || job.task || "").slice(0, 120));
    return (
      '<button type="button" class="runs-row' + sel + stale + '" data-job-id="' + esc(id) + '">' +
      '<span class="runs-st runs-st-' + esc(st) + '">' + esc(st) + "</span>" +
      '<span class="runs-id">' + esc(id) + "</span>" +
      '<span class="runs-cmd dim">' + (cmd || "—") + "</span>" +
      "</button>"
    );
  }

  function detailHtml(job) {
    if (!job) {
      return '<div class="runs-detail empty">select a run</div>';
    }
    var st = stateOf(job);
    var lines = [
      "<dl class=\"kv runs-detail-kv\">",
      "<dt>job_id</dt><dd>" + esc(job.job_id || job.id) + "</dd>",
      "<dt>state</dt><dd class=\"runs-st-" + esc(st) + "\">" + esc(st) + "</dd>",
      "<dt>command</dt><dd>" + esc(job.command || job.task || "—") + "</dd>",
      "<dt>priority</dt><dd>" + esc(job.priority != null ? job.priority : "—") + "</dd>",
      "<dt>age_s</dt><dd>" + esc(job.age_s != null ? job.age_s : "—") + "</dd>",
      "<dt>stale</dt><dd>" + (job.stale_flag ? "flagged" : "—") + "</dd>"
    ];
    if (st === "FINDINGS") {
      lines.push(
        "<dt>HITL</dt><dd>FINDINGS — awaiting CCr. Resume via drop / <code>--accept</code> " +
        "(file a NEW job; never retry the same job_id).</dd>"
      );
    }
    lines.push("</dl>");
    return '<div class="runs-detail">' + lines.join("") + "</div>";
  }

  function chipHtml(id, label, active, hidden) {
    if (hidden) return "";
    var cls = "runs-chip" + (active ? " runs-chip-on" : "");
    return (
      '<button type="button" class="' + cls + '" data-runs-filter="' + esc(id) + '">' +
      esc(label) + "</button>"
    );
  }

  function paintRunsList(body) {
    lastBody = body;
    var root = $("panel-runs");
    if (!root) return;

    var all = jobsFromBody(body);
    all.sort(function (a, b) {
      var d = jobSortKey(a) - jobSortKey(b);
      if (d !== 0) return d;
      return String(a.job_id || "").localeCompare(String(b.job_id || ""));
    });

    var filtered = filterJobs(all, body);
    var showFindingsChip = findingsInEmit(body);

    var chips =
      chipHtml("ALL", "ALL", runsFilter === "ALL", false) +
      chipHtml("INFLIGHT", "IN-FLIGHT", runsFilter === "INFLIGHT", false) +
      chipHtml("QUEUED", "QUEUED", runsFilter === "QUEUED", false) +
      chipHtml("RUNNING", "RUNNING", runsFilter === "RUNNING", false) +
      chipHtml("FINDINGS", "FINDINGS", runsFilter === "FINDINGS", !showFindingsChip) +
      chipHtml("BROKE", "BROKE", runsFilter === "BROKE", false) +
      chipHtml("CLEAN", "CLEAN", runsFilter === "CLEAN", false) +
      chipHtml("STALE", "STALE", runsFilter === "STALE", false);

    var kept = filtered.length;
    var dropped = all.length - kept;
    var census = runsFilter === "ALL"
      ? ""
      : ('<span class="runs-census dim">kept ' + kept + " · dropped " + dropped + "</span>");

    var list = filtered.map(function (j) {
      var id = j.job_id || j.id;
      return rowHtml(j, id && id === selectedJobId);
    }).join("");

    if (!list) {
      list = '<div class="empty">no runs for filter ' + esc(runsFilter) + "</div>";
    }

    var sel = null;
    if (selectedJobId) {
      sel = all.filter(function (j) { return (j.job_id || j.id) === selectedJobId; })[0] || null;
    }
    if (!sel && filtered.length) {
      sel = filtered[0];
      selectedJobId = sel.job_id || sel.id;
    }

    root.innerHTML =
      '<div class="runs-toolbar">' +
      '<div class="runs-chips chip-row" id="runs-chips">' + chips + census + "</div>" +
      '<form class="runs-file-form" id="runs-file-form">' +
      '<input type="text" id="runs-new-cmd" placeholder="command" autocomplete="off" />' +
      '<select id="runs-new-priority">' +
      '<option value="normal">normal</option>' +
      '<option value="high">high</option>' +
      '<option value="critical">critical</option>' +
      '<option value="low">low</option>' +
      "</select>" +
      '<button type="submit" id="runs-file-new">file NEW job</button>' +
      "</form></div>" +
      '<div class="runs-split">' +
      '<div class="runs-list" id="runs-list">' + list + "</div>" +
      detailHtml(sel) +
      "</div>";

    var chipRoot = $("runs-chips");
    if (chipRoot) {
      chipRoot.querySelectorAll("[data-runs-filter]").forEach(function (btn) {
        btn.addEventListener("click", function () {
          runsFilter = btn.getAttribute("data-runs-filter") || "ALL";
          paintRunsList(lastBody || body);
        });
      });
    }

    var listRoot = $("runs-list");
    if (listRoot) {
      listRoot.querySelectorAll("[data-job-id]").forEach(function (btn) {
        btn.addEventListener("click", function () {
          selectedJobId = btn.getAttribute("data-job-id");
          paintRunsList(lastBody || body);
        });
      });
    }

    var form = $("runs-file-form");
    if (form && !form.dataset.bound) {
      form.dataset.bound = "1";
      form.addEventListener("submit", function (ev) {
        ev.preventDefault();
        fileNewJob(
          ($("runs-new-cmd") && $("runs-new-cmd").value) || "",
          ($("runs-new-priority") && $("runs-new-priority").value) || "normal"
        ).then(function () {
          if ($("runs-new-cmd")) $("runs-new-cmd").value = "";
          if (window.pollJukebox) return window.pollJukebox();
        }).catch(function (e) {
          var msg = (e && e.message) ? e.message : String(e);
          if (root.querySelector(".runs-file-err")) {
            root.querySelector(".runs-file-err").textContent = msg;
          } else {
            var err = document.createElement("div");
            err.className = "runs-file-err bad";
            err.textContent = msg;
            root.insertBefore(err, root.firstChild);
          }
        });
      });
    }
  }

  /** POST /api/v1/jobs — always a fresh submit; never re-post a prior job_id. */
  function fileNewJob(command, priority) {
    var cmd = String(command || "").trim();
    if (!cmd) return Promise.reject(new Error("command required"));
    var body = { command: cmd, priority: priority || "normal" };
    return apiPost("/api/v1/jobs", body);
  }

  function stagePanRoot() {
    var stage = $("deck-stage");
    if (!stage) return null;
    return stage.querySelector(".deck-page-pan") || stage;
  }

  function mountRunsPanel() {
    var root = stagePanRoot();
    if (!root) return;
    if (window.deckScroll && window.deckScroll.setPageId) {
      window.deckScroll.setPageId($("deck-stage"), "extra:runs");
    }
    root.innerHTML =
      '<section id="panel-runs" class="runs-pane" aria-label="Runs"></section>';
    if (window.startJukeboxPoll) window.startJukeboxPoll();
    else if (window.pollJukebox) window.pollJukebox().catch(function () {});
  }

  window.deckStudio = {
    STAGES: STAGES,
    JOB_ORDER: JOB_ORDER,
    paintRunsList: paintRunsList,
    rowHtml: rowHtml,
    fileNewJob: fileNewJob,
    mountRunsPanel: mountRunsPanel,
    getRunsFilter: function () { return runsFilter; },
    setRunsFilter: function (f) { runsFilter = f || "ALL"; }
  };
}());
