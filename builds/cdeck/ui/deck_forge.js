(function () {
  "use strict";

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

  function paintForgeTab() {
    var panel = $("panel-forge");
    if (!panel) return;
    if (panel.dataset.shell !== "1") {
      panel.dataset.shell = "1";
      panel.innerHTML =
        '<section id="forge-gem-rail" class="sys-block" aria-label="GEM rail"></section>' +
        '<section id="forge-independence" class="sys-block" aria-label="family notes"></section>';
    }
    var gemEl = $("forge-gem-rail");
    var indEl = $("forge-independence");
    if (gemEl) gemEl.innerHTML = '<p class="dim tiny">GET /api/v1/nodemap …</p>';
    apiGet("/api/v1/nodemap").then(function (d) {
      var reg = (d && d.registry) || {};
      var cat = reg.catalog || {};
      var mx = (reg.matrix || []).concat(reg.stale || []);
      var gemProof = null;
      var i;
      for (i = 0; i < mx.length; i++) {
        if (mx[i].link_id === "gem-api") {
          gemProof = mx[i];
          break;
        }
      }
      var gemCat = cat["gem-api"] || {};
      if (gemEl) {
        if (!gemProof && !gemCat.agent) {
          gemEl.innerHTML = '<div class="empty">gem-api not in registry projection</div>';
        } else {
          var model = gemProof && gemProof.model ? esc(String(gemProof.model)) : "—";
          var stale = gemProof && gemProof.proof_state === "STALE";
          var ver = stale ? '<span class="bad">STALE</span>'
            : (gemProof && gemProof.verified === true ? '<span class="ok">verified live</span>'
              : '<span class="warn">unverified</span>');
          gemEl.innerHTML =
            "<h3 class=\"sys-hd\">GEM · gem-api</h3>" +
            '<p class="dim tiny">Forge reads Core nodemap — vendor model only after live prove</p>' +
            '<p>model <b>' + model + "</b> · " + ver + "</p>" +
            (gemCat.role ? '<p class="tiny">' + esc(gemCat.role) + "</p>" : "");
        }
      }
      if (indEl) {
        var lines = [];
        if (cat["gem-api"] && cat["gem-api"].independence) {
          lines.push("<li><b>GEM</b> " + esc(cat["gem-api"].independence) + "</li>");
        }
        if (cat["sgh-api"] && cat["sgh-api"].independence) {
          lines.push("<li><b>SGH</b> " + esc(cat["sgh-api"].independence) + "</li>");
        }
        if (cat["gw-api"] && cat["gw-api"].independence) {
          lines.push("<li><b>GBW</b> " + esc(cat["gw-api"].independence) + "</li>");
        }
        indEl.innerHTML =
          "<h3 class=\"sys-hd\">Family / independence</h3>" +
          "<ul class=\"sys-list\">" + (lines.join("") || "<li class=\"dim\">—</li>") + "</ul>";
      }
    }).catch(function (e) {
      if (gemEl) {
        gemEl.innerHTML = '<div class="sys-err">' + esc(e.message || String(e)) + "</div>";
      }
    });
  }

  window.paintForgeTab = paintForgeTab;

  function assign(profile, seat, model, where, via) {
    if (!seat) return;
    var body = { profile: profile, seat: seat, model: model || "" };
    if (via) body.via = via;
    var pane = where || "adv";
    panelBusy(pane, true);
    apiPost("/api/v1/model_rater/seat", body).then(function (rec) {
      panelBusy(pane, false);
      if (rec && rec.error != null && rec.error !== "") {
        var detail = rec.detail != null && String(rec.detail) !== "" ? String(rec.detail) : String(rec.error);
        var pretty = JSON.stringify(rec, null, 2);
        addConsole("err", String(rec.error).toUpperCase(), detail, pretty);
        var el = $("panel-forge-" + pane);
        if (el) el.innerHTML = esc(detail);
        return;
      }
      var got = ((rec && rec.seats) || []).filter(function (s) {
        return s.profile === profile && s.seat === seat;
      })[0];
      var now = (got && got.model) || model || "unassigned";
      var nowVia = (got && got.via) || via || "";
      var msg = profile + "." + seat + " = " + now +
        (nowVia ? " via " + nowVia : "") +
        (model && now !== model ? " — Core kept its own model, not " + model : "");
      var el2 = $("panel-forge-" + pane);
      if (el2) el2.textContent = msg;
    }).catch(function (e) {
      panelBusy(pane, false);
      var j = e && e.json;
      var kind = (j && j.error) ? String(j.error).toUpperCase() : "REFUSED";
      var detail = (j && j.detail != null && String(j.detail) !== "") ? String(j.detail)
        : (e.message || String(e));
      var pretty = j ? JSON.stringify(j, null, 2) : null;
      addConsole("err", kind, detail, pretty);
      var el = $("panel-forge-" + pane);
      if (el) el.innerHTML = esc(detail);
    });
  }

})();
