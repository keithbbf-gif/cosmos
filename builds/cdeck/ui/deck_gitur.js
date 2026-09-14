(function () {
  "use strict";

  var LEG_ORDER = ["github-forge", "gitlab-forge", "cursor-api"];
  var LAST_GOOD = null;
  var filterQ = "";

  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }

  function $(id) {
    return document.getElementById(id);
  }

  function legClass(leg) {
    if (!leg) return "gitur-leg gitur-unmeasured";
    if (leg.verified === true) return "gitur-leg gitur-verified";
    if (leg.verified === false) return "gitur-leg gitur-fail";
    if (leg.present === false) return "gitur-leg gitur-absent";
    return "gitur-leg gitur-unmeasured";
  }

  function paintLegs(rec) {
    var host = $("gitur-legs");
    if (!host) return;
    var by = {};
    (rec.legs || []).forEach(function (L) {
      if (L && L.id) by[L.id] = L;
    });
    host.innerHTML = LEG_ORDER.map(function (id) {
      var L = by[id] || { id: id, name: id, present: false, verified: null };
      var st = L.verified === true ? "verified"
        : (L.verified === false ? "fail"
          : (L.present ? "present" : "UNMEASURED"));
      return (
        "<div class=\"" + legClass(L) + "\" data-leg=\"" + esc(id) + "\">" +
        "<strong>" + esc(L.name || id) + "</strong> " +
        "<span class=\"gitur-leg-st\">" + esc(st) + "</span>" +
        (L.bound ? "<div class=\"gitur-leg-bound\">" + esc(L.bound) + "</div>" : "") +
        "</div>"
      );
    }).join("");
  }

  function paintProbeLaunch(rec) {
    var probeEl = $("gitur-probe");
    var launchEl = $("gitur-launch");
    var cur = (rec.panes && rec.panes.cursor) || {};
    var probe = cur.probe || rec.cursor || null;
    var launch = cur.launch || rec.launch || null;
    if (probeEl) {
      if (!probe) {
        probeEl.textContent = "UNMEASURED";
      } else if (probe.kind === "BROKE") {
        probeEl.textContent = "BROKE: " + (probe.detail || probe.kind);
      } else {
        probeEl.textContent = [
          probe.gate || probe.kind || "probe",
          probe.apiKeyName ? "apiKeyName=" + probe.apiKeyName : "",
          probe.http != null ? "http=" + probe.http : ""
        ].filter(Boolean).join(" · ");
      }
    }
    if (launchEl) {
      if (!launch) {
        launchEl.textContent = "UNMEASURED";
      } else if (launch.kind === "BROKE") {
        launchEl.textContent = "BROKE: " + (launch.detail || launch.kind);
      } else {
        launchEl.textContent = [
          launch.ok ? "ok" : (launch.kind || "launch"),
          launch.agent_id ? "agent=" + launch.agent_id : "",
          launch.detail ? String(launch.detail).slice(0, 120) : ""
        ].filter(Boolean).join(" · ");
      }
    }
  }

  function jobHay(j) {
    return [
      j.job_id, j.command, j.stage, j.st, j.outcome, j.leg, j.source, j.detail
    ].map(function (x) { return String(x || ""); }).join(" ").toLowerCase();
  }

  function filterJobs(jobs, q) {
    var all = Array.isArray(jobs) ? jobs.slice() : [];
    var qq = String(q || "").trim().toLowerCase();
    if (!qq) {
      return { kept: all, dropped: 0, total: all.length };
    }
    var kept = all.filter(function (j) { return jobHay(j).indexOf(qq) >= 0; });
    return { kept: kept, dropped: all.length - kept.length, total: all.length };
  }

  function paintCensus(el, kept, dropped, q) {
    if (!el) return;
    if (!String(q || "").trim()) {
      el.textContent = "";
      el.hidden = true;
      return;
    }
    el.hidden = false;
    el.textContent = "kept " + kept + " · dropped " + dropped;
  }

  function paintGithubLive(rec) {
    var el = $("gitur-github-prs");
    if (!el) return;
    var gh = (rec.panes && rec.panes.github) || {};
    var live = gh.live || {};
    var prs = live.prs;
    if (!live.ok && (!prs || !prs.length)) {
      el.textContent = live.kind ? String(live.kind) : "UNMEASURED";
      return;
    }
    if (!Array.isArray(prs)) {
      el.textContent = "UNMEASURED";
      return;
    }
    if (!prs.length) {
      el.textContent = "0 open PRs (measured empty — not invented)";
      return;
    }
    el.innerHTML = prs.slice(0, 12).map(function (p) {
      var tag = p.parked ? " parked" : "";
      return "<div class=\"gitur-pr-row\">#" + esc(p.number) + " " +
        esc(p.title || "") + tag + "</div>";
    }).join("");
  }

  function paintJukeboxRows(rec, q) {
    var el = $("gitur-jobs");
    var census = $("gitur-filter-census");
    if (!el) return;
    var jobs = rec.jobs;
    if (!Array.isArray(jobs)) {
      el.textContent = rec.jobs_kind ? String(rec.jobs_kind) : "UNMEASURED";
      paintCensus(census, 0, 0, q);
      return;
    }
    var juke = jobs.filter(function (j) {
      return j && (j.source === "jukebox" || rec.jobs_kind === "jukebox");
    });
    if (!juke.length && jobs.length) {
      juke = jobs.slice();
    }
    var f = filterJobs(juke, q);
    paintCensus(census, f.kept.length, f.dropped, q);
    if (!f.kept.length) {
      el.textContent = f.total ? "0 match filter" : "0 jukebox-named rows";
      return;
    }
    el.innerHTML = f.kept.slice(0, 40).map(function (j) {
      return "<div class=\"gitur-job-row\">" +
        esc(j.st || j.outcome || j.stage || "job") + " · " +
        esc(j.command || j.job_id || j.detail || "") +
        (j.source ? " <span class=\"gitur-src\">" + esc(j.source) + "</span>" : "") +
        "</div>";
    }).join("");
  }

  function paintMeta(rec) {
    var note = $("gitur-note");
    if (note) note.textContent = rec.note || "";
    var jk = $("gitur-jobs-kind");
    if (jk) jk.textContent = rec.jobs_kind != null ? String(rec.jobs_kind) : "UNMEASURED";
  }

  function paintAll(rec) {
    paintLegs(rec);
    paintProbeLaunch(rec);
    paintGithubLive(rec);
    paintJukeboxRows(rec, filterQ);
    paintMeta(rec);
  }

  function refreshGitur() {
    var errEl = $("gitur-err");
    return apiGet("/api/v1/gitur").then(function (rec) {
      if (errEl) errEl.textContent = "";
      LAST_GOOD = rec;
      paintAll(rec);
      return rec;
    }).catch(function (e) {
      var msg = (e && e.json && e.json.detail) ? String(e.json.detail)
        : (e && e.message ? e.message : String(e));
      if (errEl) errEl.textContent = msg;
      if (LAST_GOOD) {
        paintAll(LAST_GOOD);
      }
      throw e;
    });
  }

  function runProbe() {
    var body = {
      command: "py:cosmos_cursor_rail.py --gate",
      priority: "normal",
      note: "gitur-tab-probe"
    };
    return apiPost("/api/v1/jobs", body).then(function (rec) {
      addConsole("ok", "PROBE QUEUED", rec.job_id || rec.detail || "", JSON.stringify(rec, null, 2));
      return refreshGitur();
    }).catch(function (e) {
      var j = e && e.json;
      addConsole("err", (j && j.error) || "REFUSED", e.message || "", j ? JSON.stringify(j, null, 2) : null);
    });
  }

  function runLaunch() {
    var body = {
      command: "py:cosmos_cursor_rail.py --launch",
      priority: "normal",
      note: "gitur-tab-launch"
    };
    return apiPost("/api/v1/jobs", body).then(function (rec) {
      addConsole("ok", "LAUNCH QUEUED", rec.job_id || rec.detail || "", JSON.stringify(rec, null, 2));
      return refreshGitur();
    }).catch(function (e) {
      var j = e && e.json;
      addConsole("err", (j && j.error) || "REFUSED", e.message || "", j ? JSON.stringify(j, null, 2) : null);
    });
  }

  function bindGiturTab() {
    var root = $("panel-gitur");
    if (!root || root.dataset.bound === "1") return;
    root.dataset.bound = "1";
    root.innerHTML =
      "<div class=\"gitur-pane\">" +
      "<div class=\"gitur-actions\">" +
      "<button type=\"button\" id=\"gitur-btn-refresh\">Refresh</button>" +
      "<button type=\"button\" id=\"gitur-btn-probe\">Probe</button>" +
      "<button type=\"button\" id=\"gitur-btn-launch\">Launch</button>" +
      "<input id=\"gitur-filter\" placeholder=\"filter jobs\" aria-label=\"Filter Gitur jobs\" />" +
      "</div>" +
      "<div id=\"gitur-filter-census\" class=\"gitur-census\" hidden></div>" +
      "<div id=\"gitur-err\" class=\"gitur-err\"></div>" +
      "<div id=\"gitur-legs\" class=\"gitur-legs\"></div>" +
      "<div class=\"gitur-cursor\">" +
      "<div>Probe: <span id=\"gitur-probe\">UNMEASURED</span></div>" +
      "<div>Launch: <span id=\"gitur-launch\">UNMEASURED</span></div>" +
      "</div>" +
      "<div class=\"gitur-github\"><strong>GitHub PRs</strong> <span id=\"gitur-jobs-kind\"></span>" +
      "<div id=\"gitur-github-prs\">UNMEASURED</div></div>" +
      "<div class=\"gitur-jukebox\"><strong>Jukebox rows</strong>" +
      "<div id=\"gitur-jobs\"></div></div>" +
      "<div id=\"gitur-note\" class=\"gitur-note\"></div>" +
      "</div>";
    var btnR = $("gitur-btn-refresh");
    var btnP = $("gitur-btn-probe");
    var btnL = $("gitur-btn-launch");
    var inp = $("gitur-filter");
    if (btnR) btnR.addEventListener("click", function () { refreshGitur(); });
    if (btnP) btnP.addEventListener("click", function () { runProbe(); });
    if (btnL) btnL.addEventListener("click", function () { runLaunch(); });
    if (inp) {
      inp.addEventListener("input", function () {
        filterQ = inp.value || "";
        if (LAST_GOOD) paintJukeboxRows(LAST_GOOD, filterQ);
      });
    }
    refreshGitur();
  }

  window.cdeckGiturRefresh = refreshGitur;
  window.cdeckBindGiturTab = bindGiturTab;
})();
