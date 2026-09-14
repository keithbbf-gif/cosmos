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

  function cowFromNodemap(d) {
    if (d && d.cow && typeof d.cow === "object") return d.cow;
    var list = (d && d.nodes) || [];
    for (var i = 0; i < list.length; i++) {
      if (list[i] && (list[i].id === "cow" || list[i].link_id === "cow")) return list[i];
    }
    return null;
  }

  function paintForgeCow(d) {
    var el = $("panel-forge-cow") || $("forge-cow") || $("panel-forge-adv");
    if (!el) return;
    var cow = cowFromNodemap(d);
    if (!cow) {
      el.innerHTML = '<div class="empty">' + esc("COW UNMEASURED") + "</div>";
      return;
    }
    var stale = cow.proof_state === "STALE" || cow.verified === false;
    var cls = stale ? "cow-stale stale-red" : (cow.verified === true ? "cow-live" : "cow-unmeasured");
    var model = cow.model ? esc(cow.model) : "UNMEASURED";
    var indep = (cow.independence && cow.independence.note)
      ? cow.independence.note
      : "SGH+GBW are not independent checks of each other";
    el.innerHTML = '<div class="cow-node ' + cls + '">' +
      "<b>" + esc(cow.label || "CoW") + "</b> " +
      esc(cow.role || "VERIFY, SYNTHESISE, ORCHESTRATE") +
      "<div>model " + model + "</div>" +
      '<div class="tiny indep">' + esc(indep) + "</div></div>";
  }

  function paintForgeFromCore() {
    if (typeof apiGet !== "function") return;
    apiGet("/api/v1/nodemap").then(paintForgeCow).catch(function (e) {
      var el = $("panel-forge-cow") || $("forge-cow") || $("panel-forge-adv");
      if (!el) return;
      var kind = (e && e.json && e.json.error) ? String(e.json.error) : (e && e.message) || "REFUSED";
      el.innerHTML = '<div class="sys-err">' + esc(kind) + "</div>";
    });
  }

  function assign(profile, seat, model, where, via) {
    if (!seat) return;
    var body = { profile: profile, seat: seat, model: model || "" };
    if (via) body.via = via;
    var pane = where || "adv";
    if (typeof panelBusy === "function") panelBusy(pane, true);
    apiPost("/api/v1/model_rater/seat", body).then(function (rec) {
      if (typeof panelBusy === "function") panelBusy(pane, false);
      if (rec && rec.error != null && rec.error !== "") {
        var detail = rec.detail != null && String(rec.detail) !== "" ? String(rec.detail) : String(rec.error);
        var pretty = JSON.stringify(rec, null, 2);
        if (typeof addConsole === "function") addConsole("err", String(rec.error).toUpperCase(), detail, pretty);
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
      if (typeof panelBusy === "function") panelBusy(pane, false);
      var j = e && e.json;
      var kind = (j && j.error) ? String(j.error).toUpperCase() : "REFUSED";
      var detail = (j && j.detail != null && String(j.detail) !== "") ? String(j.detail)
        : (e.message || String(e));
      var pretty = j ? JSON.stringify(j, null, 2) : null;
      if (typeof addConsole === "function") addConsole("err", kind, detail, pretty);
      var el = $("panel-forge-" + pane);
      if (el) el.innerHTML = esc(detail);
    });
  }

  window.paintForgeCow = paintForgeCow;
  window.paintForgeFromCore = paintForgeFromCore;
  window.assignForgeSeat = assign;
  paintForgeFromCore();
})();
