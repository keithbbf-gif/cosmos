/* builds/cdeck/ui/app.js — MESH jukebox poll + System tab live GET painters. */
(function () {
  "use strict";

  var RUNS_POLL_MS = 10000;
  var SYSTEM_POLL_MS = 15000;

  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function $(id) {
    return document.getElementById(id);
  }

  function jobsFromJukebox(d) {
    if (!d || typeof d !== "object") return [];
    var q = d.queue;
    if (q && Array.isArray(q.jobs)) return q.jobs.slice();
    if (Array.isArray(d.jobs)) return d.jobs.slice();
    if (Array.isArray(d.shown)) return d.shown.slice();
    return [];
  }

  function renderJobs(d) {
    if (!d) return;
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
    pollJukebox().catch(function () { /* empty */ });
    setInterval(function () {
      pollJukebox().catch(function () { /* keep runsFilter in deck_studio */ });
    }, RUNS_POLL_MS);
  }

  function errDetail(err) {
    if (!err) return "unknown";
    if (err.status === 503) {
      var j = err.json;
      if (typeof j === "string" && j) return j;
      if (j && j.error) return String(j.error);
      return "CDECK_PANEL_NOT_COMPOSED";
    }
    return err.message || String(err);
  }

  function panelErr(el, err) {
    if (!el) return;
    el.innerHTML = '<div class="sys-err">' + esc(errDetail(err)) + "</div>";
  }

  function renderStatus(d) {
    var el = $("sys-status");
    if (!el) return;
    d = d || {};
    var lh = d.ledger_head || {};
    var readyCls = d.ready ? "ok" : "bad";
    var readyTxt = d.ready ? "READY" : "NOT READY";
    el.innerHTML =
      '<h3 class="sys-hd">Status</h3>' +
      '<p class="dim tiny">GET /api/v1/status</p>' +
      '<dl class="kv">' +
      '<dt>ready</dt><dd class="big ' + readyCls + '">' + esc(readyTxt) + "</dd>" +
      "<dt>root</dt><dd>" + esc(d.root != null ? d.root : "—") + "</dd>" +
      "<dt>tree_id</dt><dd>" + esc(d.tree_id != null ? d.tree_id : "—") + "</dd>" +
      "<dt>ledger head</dt><dd>seq " + esc(lh.seq != null ? lh.seq : "—") +
      ' · <span class="dim">' + esc(lh.event != null ? lh.event : "—") + "</span></dd>" +
      "</dl>";
  }

  function renderHealth(d) {
    var el = $("sys-health");
    if (!el) return;
    d = d || {};
    var verdict = d.verdict != null ? String(d.verdict) : "UNKNOWN";
    var vu = verdict.toUpperCase();
    var vCls = "unknown";
    if (vu === "GREEN") vCls = "green";
    else if (vu === "RED") vCls = "red";
    else if (vu === "BOARD-BROKEN") vCls = "broken";
    var h = '<h3 class="sys-hd">Health</h3>' +
      '<p class="dim tiny">GET /api/v1/health — System tab only</p>' +
      '<div class="verdict ' + vCls + '">' + esc(vu) + "</div>";
    if (d.diagnosis) h += '<div class="diagnosis">' + esc(d.diagnosis) + "</div>";
    var rows = d.rows || {};
    var names = Object.keys(rows);
    var ncOk = typeof d.negative_control_red === "boolean" ? d.negative_control_red : null;
    if (names.length === 0) {
      h += '<div class="empty">no health rows reported</div>';
    } else {
      var body = names.map(function (name) {
        var r = rows[name] || {};
        var isNC = /negative[\s_-]?control/i.test(name);
        var dot = r.ok === true ? '<span class="dot g"></span>'
          : r.ok === false ? '<span class="dot r"></span>'
            : '<span class="warn">?</span>';
        var label = isNC ? ' <span class="nclabel">SUPPOSED TO BE RED</span>' : "";
        return "<tr" + (isNC ? ' class="ncrow"' : "") + ">" +
          "<td>" + dot + "</td><td>" + esc(name) + label + "</td>" +
          '<td class="dim">' + esc(r.detail != null ? r.detail : "") + "</td></tr>";
      }).join("");
      h += '<div class="twrap"><table><thead><tr><th></th><th>ROW</th><th>DETAIL</th></tr></thead><tbody>' +
        body + "</tbody></table></div>";
    }
    var ncTxt = ncOk === true ? '<span class="ok">RED as designed</span>'
      : ncOk === false ? '<span class="bad">NOT RED — the checker may be incapable of failing</span>'
        : '<span class="dim">—</span>';
    h += '<dl class="kv sys-nc"><dt>reds</dt><dd>' + esc(d.reds != null ? String(d.reds) : "—") +
      "</dd><dt>negative control</dt><dd>" + ncTxt + "</dd></dl>";
    el.innerHTML = h;
  }

  function renderSpend(d) {
    var el = $("sys-spend");
    if (!el) return;
    d = d || {};
    var rails = d.rails || {};
    var names = Object.keys(rails);
    if (names.length === 0) {
      el.innerHTML = '<h3 class="sys-hd">Spend</h3><p class="dim tiny">GET /api/v1/spend</p>' +
        '<div class="empty">no rails reported</div>';
      return;
    }
    var parts = names.sort().map(function (name) {
      var r = rails[name] || {};
      var cap = typeof r.cap_usd === "number" ? r.cap_usd : null;
      return "<li><b>" + esc(name) + "</b> cap " + (cap != null ? esc(String(cap)) : "—") + "</li>";
    }).join("");
    el.innerHTML = '<h3 class="sys-hd">Spend</h3><p class="dim tiny">GET /api/v1/spend</p>' +
      "<ul class=\"sys-list\">" + parts + "</ul>";
  }

  function _proofCell(r) {
    var ps = String(r.proof_state || "").toUpperCase();
    if (ps === "STALE" || (r.verified === false && ps !== "UNMEASURED")) {
      return '<span class="bad red">STALE</span>';
    }
    if (r.verified === true || ps === "LIVE") return '<span class="ok">LIVE</span>';
    if (r.verified === false) return '<span class="bad">✗</span>';
    return '<span class="warn">UNMEASURED</span>';
  }

  function renderRails(d) {
    var el = $("sys-rails");
    if (!el) return;
    d = d || {};
    var m = d.matrix || [];
    if (m.length === 0) {
      el.innerHTML = '<h3 class="sys-hd">Rails</h3><p class="dim tiny">GET /api/v1/nodemap (registry matrix)</p>' +
        '<div class="empty">no rails reported</div>';
      return;
    }
    var rows = m.map(function (r) {
      var model = r.model != null && String(r.model).trim() !== ""
        ? esc(String(r.model)) : '<span class="dim">UNMEASURED</span>';
      return "<tr><td>" + esc(r.link_id || r.rail || "?") + "</td><td>" + model +
        "</td><td>" + _proofCell(r) + "</td></tr>";
    }).join("");
    el.innerHTML = '<h3 class="sys-hd">Rails</h3><p class="dim tiny">GET /api/v1/nodemap (registry matrix)</p>' +
      '<div class="twrap"><table><thead><tr><th>link</th><th>model</th><th>proof</th></tr></thead><tbody>' +
      rows + "</tbody></table></div>";
  }

  function renderFleet(d) {
    var el = $("sys-fleet");
    if (!el) return;
    d = d || {};
    var fleet = d.fleet || {};
    if (fleet.available === false) {
      el.innerHTML = '<h3 class="sys-hd">Fleet</h3><p class="dim tiny">GET /api/v1/fleet</p>' +
        '<div class="empty">' + esc(fleet.kind || "feed unavailable") + "</div>";
      return;
    }
    var clocks = fleet.clocks || [];
    var lines = clocks.slice(0, 12).map(function (c) {
      return "<li>" + esc(c.worker || c.name || "?") + "</li>";
    }).join("");
    el.innerHTML = '<h3 class="sys-hd">Fleet</h3><p class="dim tiny">GET /api/v1/fleet</p>' +
      '<p class="tiny">clocks ' + esc(String(clocks.length)) + "</p>" +
      "<ul class=\"sys-list\">" + (lines || "<li class=\"dim\">none</li>") + "</ul>";
  }

  function _oaRailLine(rail) {
    var ctx = rail.context_tokens != null ? String(rail.context_tokens) : "—";
    var label = rail.ceiling_label ? esc(rail.ceiling_label) + " " : "";
    var model = rail.model && String(rail.model).trim()
      ? esc(String(rail.model)) : '<span class="dim">UNMEASURED</span>';
    var ps = String(rail.proof_state || "UNMEASURED").toUpperCase();
    var st = ps === "STALE" ? '<span class="bad red">STALE</span>'
      : ps === "LIVE" ? '<span class="ok">LIVE</span>'
        : '<span class="warn">UNMEASURED</span>';
    return "<li>" + esc(rail.link_id || "?") + " · " + label +
      "ctx " + esc(ctx) + " · model " + model + " · " + st + "</li>";
  }

  function renderNodemap(d) {
    var el = $("sys-nodemap");
    if (!el) return;
    d = d || {};
    if (d.error === "CDECK_PANEL_NOT_COMPOSED") {
      el.innerHTML = '<h3 class="sys-hd">Nodemap</h3><p class="dim tiny">GET /api/v1/nodemap</p>' +
        '<div class="sys-err">CDECK_PANEL_NOT_COMPOSED</div>';
      return;
    }
    var topo = d.topology || {};
    var nodes = topo.nodes || [];
    var reg = d.registry || {};
    var mx = reg.matrix || [];
    var blocks = nodes.map(function (n) {
      if (n.id === "OA" && n.rails && n.rails.length) {
        var hands = n.hands ? '<p class="tiny">' + esc(n.hands) + "</p>" : "";
        return "<div class=\"sys-node\"><b>" + esc(n.label || n.id) + "</b>" + hands +
          "<ul class=\"sys-list\">" + n.rails.map(_oaRailLine).join("") + "</ul></div>";
      }
      var note = n.independence_note
        ? '<p class="tiny dim">' + esc(n.independence_note) + "</p>" : "";
      return "<div class=\"sys-node\"><b>" + esc(n.label || n.id) + "</b>" + note + "</div>";
    }).join("");
    el.innerHTML = '<h3 class="sys-hd">Nodemap</h3><p class="dim tiny">GET /api/v1/nodemap</p>' +
      '<p class="tiny">routing nodes ' + esc(String(nodes.length)) + " · registry rows " +
      esc(String(mx.length)) + (reg.stale_count != null ? " · stale " + esc(String(reg.stale_count)) : "") +
      "</p>" + (blocks || '<div class="empty">none</div>');
  }

  function paintSystemTab() {
    apiGet("/api/v1/status").then(renderStatus).catch(function (e) {
      panelErr($("sys-status"), e);
    });
    apiGet("/api/v1/health").then(renderHealth).catch(function (e) {
      panelErr($("sys-health"), e);
    });
    apiGet("/api/v1/spend").then(renderSpend).catch(function (e) {
      panelErr($("sys-spend"), e);
    });
    apiGet("/api/v1/fleet").then(renderFleet).catch(function (e) {
      panelErr($("sys-fleet"), e);
    });
    apiGet("/api/v1/nodemap").then(function (nm) {
      renderNodemap(nm);
      renderRails({ matrix: (nm.registry || {}).matrix || [] });
    }).catch(function (e) {
      panelErr($("sys-nodemap"), e);
      panelErr($("sys-rails"), e);
    });
  }

  function startSystemPoll() {
    if (window.__systemPollStarted) return;
    window.__systemPollStarted = true;
    setInterval(function () {
      if ($("panel-system") && !$("panel-system").hidden) paintSystemTab();
    }, SYSTEM_POLL_MS);
  }

  window.RUNS_POLL_MS = RUNS_POLL_MS;
  window.renderJobs = renderJobs;
  window.jobsFromJukebox = jobsFromJukebox;
  window.pollJukebox = pollJukebox;
  window.startJukeboxPoll = startJukeboxPoll;
  window.cdeckEsc = esc;
  window.cdeck$ = $;
  window.renderStatus = renderStatus;
  window.renderHealth = renderHealth;
  window.renderSpend = renderSpend;
  window.renderRails = renderRails;
  window.renderFleet = renderFleet;
  window.renderNodemap = renderNodemap;
  window.paintSystemTab = paintSystemTab;

  if (typeof window.cdeckLoadFillTabs === "function") window.cdeckLoadFillTabs();
  startJukeboxPoll();
  startSystemPoll();
}());
