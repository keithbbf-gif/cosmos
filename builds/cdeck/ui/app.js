/* builds/cdeck/ui/app.js — MESH widgets + System tab live GET painters. */
(function () {
  "use strict";

  var SYSTEM_POLL_MS = 15000;

  function esc(s) {
    if (s == null) return "";
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/"/g, "&quot;");
  }

  function $(id) {
    return document.getElementById(id);
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

  /**
   * renderHealth — System tab only (GET /api/v1/health).
   * Negative control row stays red when r.ok === false (never placate to green).
   */
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
    if (d.diagnosis) {
      h += '<div class="diagnosis">' + esc(d.diagnosis) + "</div>";
    }

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
          "<td>" + dot + "</td>" +
          "<td>" + esc(name) + label + "</td>" +
          '<td class="dim">' + esc(r.detail != null ? r.detail : "") + "</td>" +
          "</tr>";
      }).join("");
      h += '<div class="twrap"><table>' +
        "<thead><tr><th></th><th>ROW</th><th>DETAIL</th></tr></thead>" +
        "<tbody>" + body + "</tbody></table></div>";
    }

    var redsTxt = d.reds != null ? String(d.reds) : "—";
    var ncTxt;
    if (ncOk === true) ncTxt = '<span class="ok">RED as designed</span>';
    else if (ncOk === false) {
      ncTxt = '<span class="bad">NOT RED — the checker may be incapable of failing</span>';
    } else ncTxt = '<span class="dim">—</span>';

    h += '<dl class="kv sys-nc">' +
      "<dt>reds</dt><dd>" + esc(redsTxt) + "</dd>" +
      "<dt>negative control</dt><dd>" + ncTxt + "</dd>" +
      "</dl>";
    el.innerHTML = h;
  }

  function renderSpend(d) {
    var el = $("sys-spend");
    if (!el) return;
    d = d || {};
    var rails = d.rails || {};
    var names = Object.keys(rails);
    if (names.length === 0) {
      el.innerHTML =
        '<h3 class="sys-hd">Spend</h3>' +
        '<p class="dim tiny">GET /api/v1/spend</p>' +
        '<div class="empty">no rails reported</div>';
      return;
    }
    var parts = names.sort().map(function (name) {
      var r = rails[name] || {};
      var cap = typeof r.cap_usd === "number" ? r.cap_usd : null;
      return "<li><b>" + esc(name) + "</b> cap " + (cap != null ? esc(String(cap)) : "—") + "</li>";
    }).join("");
    el.innerHTML =
      '<h3 class="sys-hd">Spend</h3>' +
      '<p class="dim tiny">GET /api/v1/spend</p>' +
      "<ul class=\"sys-list\">" + parts + "</ul>";
  }

  function railRowClass(r) {
    if (r.proof_state === "STALE" || (r.verified === false && r.model)) {
      return " stale-row";
    }
    return "";
  }

  function verifiedCell(r) {
    if (r.proof_state === "STALE") {
      return '<span class="bad">STALE</span>';
    }
    var v = r.verified;
    if (v === true) return '<span class="ok">✓</span>';
    if (v === false) return '<span class="bad">✗</span>';
    return '<span class="warn">?</span>';
  }

  function renderRails(d) {
    var el = $("sys-rails");
    if (!el) return;
    d = d || {};
    var m = (d.matrix || []).concat(d.stale || []);
    if (m.length === 0) {
      el.innerHTML =
        '<h3 class="sys-hd">Rails</h3>' +
        '<p class="dim tiny">GET /api/v1/rails</p>' +
        '<div class="empty">no rails reported</div>';
      return;
    }
    var rows = m.map(function (r) {
      var model = r.model != null && String(r.model) !== "" ? esc(String(r.model)) : "—";
      var age = r.age_s != null ? esc(String(Math.round(r.age_s))) + "s" : "—";
      return "<tr class=\"" + esc(railRowClass(r).trim()) + "\">" +
        "<td>" + esc(r.link_id || r.rail || "?") + "</td>" +
        "<td>" + model + "</td>" +
        "<td>" + verifiedCell(r) + "</td>" +
        "<td class=\"dim\">" + age + "</td></tr>";
    }).join("");
    el.innerHTML =
      '<h3 class="sys-hd">Rails</h3>' +
      '<p class="dim tiny">GET /api/v1/rails</p>' +
      '<div class="twrap"><table><thead><tr><th>link</th><th>model</th><th>verified</th><th>age</th></tr></thead><tbody>' +
      rows + "</tbody></table></div>";
  }

  function renderFleet(d) {
    var el = $("sys-fleet");
    if (!el) return;
    d = d || {};
    var fleet = d.fleet || {};
    if (fleet.available === false) {
      el.innerHTML =
        '<h3 class="sys-hd">Fleet</h3>' +
        '<p class="dim tiny">GET /api/v1/fleet</p>' +
        '<div class="empty">' + esc(fleet.kind || "feed unavailable") + "</div>";
      return;
    }
    var clocks = fleet.clocks || [];
    var lines = clocks.slice(0, 12).map(function (c) {
      return "<li>" + esc(c.worker || c.name || "?") + "</li>";
    }).join("");
    el.innerHTML =
      '<h3 class="sys-hd">Fleet</h3>' +
      '<p class="dim tiny">GET /api/v1/fleet</p>' +
      '<p class="tiny">clocks ' + esc(String(clocks.length)) + "</p>" +
      "<ul class=\"sys-list\">" + (lines || "<li class=\"dim\">none</li>") + "</ul>";
  }

  function renderNodemap(d) {
    var el = $("sys-nodemap");
    if (!el) return;
    d = d || {};
    if (d.error === "CDECK_PANEL_NOT_COMPOSED") {
      el.innerHTML =
        '<h3 class="sys-hd">Nodemap</h3>' +
        '<p class="dim tiny">GET /api/v1/nodemap</p>' +
        '<div class="sys-err">CDECK_PANEL_NOT_COMPOSED</div>';
      return;
    }
    var topo = d.topology || {};
    var nodes = topo.nodes || [];
    var reg = d.registry || {};
    var mx = (reg.matrix || []).concat(reg.stale || []);
    var gem = null;
    var i;
    for (i = 0; i < nodes.length; i++) {
      if (nodes[i].id === "gem-api" || nodes[i].link_id === "gem-api") {
        gem = nodes[i];
        break;
      }
    }
    if (!gem) {
      for (i = 0; i < mx.length; i++) {
        if (mx[i].link_id === "gem-api") {
          gem = mx[i];
          break;
        }
      }
    }
    var nodeLines = nodes.slice(0, 16).map(function (n) {
      var model = n.model != null && String(n.model) !== "" ? " · " + esc(String(n.model)) : "";
      var stale = n.proof_state === "STALE" ? ' <span class="bad">STALE</span>' : "";
      return "<li>" + esc(n.label || n.id || "?") + model + stale + "</li>";
    }).join("");
    var gemBlock = "";
    if (gem) {
      var gModel = gem.model != null && String(gem.model) !== "" ? esc(String(gem.model)) : "—";
      var gVer = verifiedCell(gem);
      var gNote = gem.independence ? '<p class="tiny dim">' + esc(gem.independence) + "</p>" : "";
      if (!gNote && reg.catalog && reg.catalog["gem-api"]) {
        gNote = '<p class="tiny dim">' + esc(reg.catalog["gem-api"].independence || "") + "</p>";
      }
      gemBlock =
        '<div class="sys-gem' + (gem.proof_state === "STALE" ? " stale-row" : "") + '">' +
        "<b>GEM</b> gem-api · model " + gModel + " · " + gVer +
        (gem.role ? '<p class="tiny">' + esc(gem.role) + "</p>" : "") +
        gNote + "</div>";
    }
    el.innerHTML =
      '<h3 class="sys-hd">Nodemap</h3>' +
      '<p class="dim tiny">GET /api/v1/nodemap</p>' +
      gemBlock +
      '<p class="tiny">nodes ' + esc(String(nodes.length)) +
      " · matrix " + esc(String(mx.length)) + "</p>" +
      "<ul class=\"sys-list\">" + (nodeLines || "<li class=\"dim\">none</li>") + "</ul>";
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
    apiGet("/api/v1/rails").then(renderRails).catch(function (e) {
      panelErr($("sys-rails"), e);
    });
    apiGet("/api/v1/fleet").then(renderFleet).catch(function (e) {
      panelErr($("sys-fleet"), e);
    });
    apiGet("/api/v1/nodemap").then(renderNodemap).catch(function (e) {
      panelErr($("sys-nodemap"), e);
    });
  }

  function startSystemPoll() {
    if (window.__systemPollStarted) return;
    window.__systemPollStarted = true;
    setInterval(function () {
      if ($("panel-system") && !$("panel-system").hidden) {
        paintSystemTab();
      }
    }, SYSTEM_POLL_MS);
  }

  window.renderStatus = renderStatus;
  window.renderHealth = renderHealth;
  window.renderSpend = renderSpend;
  window.renderRails = renderRails;
  window.renderFleet = renderFleet;
  window.renderNodemap = renderNodemap;
  window.paintSystemTab = paintSystemTab;

  if (typeof window.cdeckLoadFillTabs === "function") {
    window.cdeckLoadFillTabs();
  }
  startSystemPoll();
})();
