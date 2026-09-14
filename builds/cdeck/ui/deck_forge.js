(function () {
  "use strict";

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
