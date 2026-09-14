/* deck_forge.js — Forge tab: seats + nodemap payload (CoP / stale RED).
 *
 *   GET /api/v1/model_rater
 *   GET /api/v1/nodemap          — paint cop-chat from Core payload
 *   GET /api/v1/porosity?profile=forge
 *
 * Independence note kept: SGH+GBW are not independent checks of each other.
 * Do NOT invent /api/v1/cop. Stale proof_state renders RED.
 */
(function (global) {
  "use strict";

  var PROFILE = "forge";
  var INDEPENDENCE_NOTE = "SGH+GBW are not independent checks of each other";
  var COP_LINK = "cop-chat";

  function $(id) {
    if (typeof global.$ === "function") return global.$(id);
    return global.document ? global.document.getElementById(id) : null;
  }

  function esc(s) {
    if (typeof global.esc === "function") return global.esc(s);
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function apiGet(path) {
    var fn = global.apiGet || global.apiCall;
    if (typeof fn !== "function") {
      return Promise.reject(new Error("apiGet unavailable"));
    }
    return fn(path);
  }

  function findRow(rows, lid) {
    for (var i = 0; i < (rows || []).length; i++) {
      if ((rows[i].link_id || rows[i].id) === lid) return rows[i];
    }
    return null;
  }

  function paintForgeNodes(d) {
    var el = $("forge-nodes");
    if (!el) return;
    d = d || {};
    if (d.error === "CDECK_PANEL_NOT_COMPOSED") {
      el.innerHTML = '<div class="sys-err">CDECK_PANEL_NOT_COMPOSED</div>';
      return;
    }
    var reg = d.registry || {};
    var mx = reg.matrix || [];
    var stale = reg.stale || [];
    var all = mx.concat(stale);
    var note = d.independence_note || INDEPENDENCE_NOTE;
    var cop = findRow(all, COP_LINK);
    var copLine;
    if (!cop) {
      copLine = '<div class="empty">cop-chat — empty (not in payload)</div>';
    } else {
      var st = String(cop.proof_state || "").toUpperCase();
      var cls = (st === "STALE" || cop.verified === false) ? "stale-red" : "";
      var model = (cop.model == null || cop.model === "") ? "UNMEASURED" : String(cop.model);
      copLine = '<div class="' + cls + '">cop-chat model=' + esc(model) +
        " state=" + esc(st || "UNMEASURED") + "</div>";
    }
    el.innerHTML =
      '<h3 class="sys-hd">Forge nodes</h3>' +
      '<p class="dim tiny">GET /api/v1/nodemap</p>' +
      '<p class="independence-note">' + esc(note) + "</p>" +
      copLine;
  }

  function paintCcr(seats) {
    var el = $("panel-forge-ccr");
    if (!el) return;
    var ccr = (seats || []).filter(function (s) {
      return s.profile === PROFILE && s.seat === "ccr";
    })[0];
    if (!ccr) {
      el.textContent = PROFILE + ".ccr — UNMEASURED";
      return;
    }
    el.textContent = PROFILE + ".ccr = " + (ccr.model || "unassigned");
  }

  function paintAdv(seats) {
    var el = $("panel-forge-adv");
    if (!el) return;
    var adv = (seats || []).filter(function (s) {
      return s.profile === PROFILE && String(s.seat || "").indexOf("adv_") === 0;
    });
    if (!adv.length) {
      el.textContent = "No adversarial seats — UNMEASURED";
      return;
    }
    el.textContent = adv.map(function (s) {
      return (s.seat || "?") + " = " + (s.model || "unassigned");
    }).join("\n");
  }

  function paintPorosity(rec) {
    var el = $("panel-forge-porosity");
    if (!el) return;
    if (!rec) {
      el.textContent = "porosity — UNMEASURED";
      return;
    }
    el.textContent = "kind=" + (rec.kind || "UNMEASURED");
  }

  function refresh() {
    return apiGet("/api/v1/model_rater")
      .then(function (snap) {
        var seats = (snap && snap.seats) || [];
        paintCcr(seats);
        paintAdv(seats);
        return apiGet("/api/v1/nodemap").then(function (nm) {
          paintForgeNodes(nm);
          return apiGet("/api/v1/porosity?profile=forge").then(function (por) {
            paintPorosity(por);
            return { snapshot: snap, nodemap: nm, porosity: por };
          });
        });
      })
      .catch(function (e) {
        var el = $("forge-nodes");
        if (el) el.innerHTML = '<div class="sys-err">' + esc(e.message || String(e)) + "</div>";
      });
  }

  var DeckForge = {
    refresh: refresh,
    paintForgeNodes: paintForgeNodes,
    paintCcr: paintCcr,
    paintAdv: paintAdv,
    paintPorosity: paintPorosity,
  };

  global.DeckForge = DeckForge;
  global.paintForgeTab = refresh;
})(typeof globalThis !== "undefined" ? globalThis : this);
