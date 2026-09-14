(function () {
  "use strict";

  var WO_GET = "/api/v1/work_orders";
  var WO_PICKED = "/api/v1/work_orders/picked";
  var STATE_CHIPS = [
    { state: "ALL", label: "ALL" },
    { state: "BUCKET", label: "BUCKET" },
    { state: "PICKED", label: "PICKED" },
    { state: "ASSIGNED", label: "ASSIGNED" },
    { state: "COMPLETED", label: "DONE" },
    { state: "FAILED", label: "FAILED" }
  ];

  var activeState = "ALL";
  var lastRec = null;

  function rowStamp(row) {
    if (!row) return "—";
    return String(
      row.picked_at || row.filed_at || row.dropped_at || row.timestamp || "—"
    );
  }

  function paintKind(rec) {
    var el = $("panel-orders");
    if (!el) return;
    var kind = rec && rec.kind != null ? String(rec.kind) : "";
    if (kind === "NO_SOURCE") {
      el.innerHTML =
        '<div class="panel-hd"><h2>Orders</h2><span class="dim tiny">GET ' +
        esc(WO_GET) + "</span></div>" +
        '<div class="panel-bd"><p class="wo-honest-kind"><b>NO_SOURCE</b> — ' +
        esc(rec.note || "work_orders tree not present on Core; not an empty queue") +
        "</p></div>";
      return true;
    }
    return false;
  }

  function paintList(rec) {
    var el = $("panel-orders");
    if (!el) return;
    lastRec = rec || null;
    if (paintKind(rec)) return;

    var rows = (rec && rec.rows) || [];
    var counts = (rec && rec.counts) || {};
    var chips = '<div class="wo-chips chips" role="toolbar" aria-label="Order state">';
    STATE_CHIPS.forEach(function (c) {
      var on = activeState === c.state ? " wo-chip-on" : "";
      var n = c.state === "ALL"
        ? (rec && rec.n_total != null ? rec.n_total : rows.length)
        : (counts[c.state.toLowerCase()] != null
          ? counts[c.state.toLowerCase()]
          : counts[c.state] || 0);
      chips += '<button type="button" class="chip wo-state-chip' + on +
        '" data-wo-state="' + esc(c.state) + '">' + esc(c.label) +
        ' <b>' + esc(String(n)) + "</b></button>";
    });
    chips += "</div>";

    var list = '<ul class="wo-list" role="list">';
    if (!rows.length) {
      list += '<li class="dim tiny">No orders in this filter.</li>';
    } else {
      rows.forEach(function (row) {
        var oid = row.order_id || "—";
        var stamp = rowStamp(row);
        var canPickup = row.folder === "bucket";
        list += '<li class="wo-row" role="listitem" data-order-id="' + esc(oid) + '">' +
          '<span class="wo-stamp tabular-nums">' + esc(stamp) + "</span> " +
          '<span class="wo-id">' + esc(oid) + "</span> " +
          '<span class="wo-agent dim tiny">' + esc(row.agent || "") + "</span> " +
          '<span class="wo-folder chip">' + esc(row.folder || row.state || "") + "</span>";
        if (canPickup) {
          list += ' <button type="button" class="wo-pickup-btn" data-pickup="' +
            esc(oid) + '">Pickup</button>';
        }
        list += "</li>";
      });
    }
    list += "</ul>";

    el.innerHTML =
      '<div class="panel-hd"><h2>Orders</h2><span class="dim tiny">GET ' +
      esc(WO_GET) + (activeState !== "ALL" ? (" ?state=" + esc(activeState)) : "") +
      "</span></div>" +
      '<div class="panel-bd">' + chips + list + "</div>";

    el.querySelectorAll(".wo-state-chip").forEach(function (btn) {
      btn.addEventListener("click", function () {
        activeState = btn.getAttribute("data-wo-state") || "ALL";
        refreshOrders();
      });
    });
    el.querySelectorAll(".wo-pickup-btn").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var oid = btn.getAttribute("data-pickup");
        if (oid) pickupOrder(oid);
      });
    });
  }

  function refreshOrders() {
    var path = WO_GET;
    if (activeState && activeState !== "ALL") {
      path += "?state=" + encodeURIComponent(activeState);
    }
    panelBusy("orders", true);
    return apiGet(path).then(function (rec) {
      panelBusy("orders", false);
      paintList(rec);
      return rec;
    }).catch(function (e) {
      panelBusy("orders", false);
      var el = $("panel-orders");
      var j = e && e.json;
      var kind = (j && j.error) ? String(j.error).toUpperCase() : "REFUSED";
      var detail = (j && j.detail) ? String(j.detail) : (e.message || String(e));
      if (el) {
        el.innerHTML =
          '<div class="panel-hd"><h2>Orders</h2></div><div class="panel-bd"><p><b>' +
          esc(kind) + "</b> — " + esc(detail) + "</p></div>";
      }
    });
  }

  function pickupOrder(orderId) {
    if (!orderId) return;
    panelBusy("orders", true);
    return apiPost(WO_PICKED, { order_id: orderId }).then(function (rec) {
      panelBusy("orders", false);
      if (rec && rec.error) {
        addConsole("err", String(rec.error).toUpperCase(),
          String(rec.detail || rec.error), JSON.stringify(rec, null, 2));
        return rec;
      }
      addConsole("ok", "WORK_ORDER_PICKED",
        orderId + (rec && rec.already ? " (already)" : ""), null);
      return refreshOrders();
    }).catch(function (e) {
      panelBusy("orders", false);
      var j = e && e.json;
      addConsole("err", (j && j.error) ? String(j.error).toUpperCase() : "REFUSED",
        (j && j.detail) || (e.message || String(e)), j ? JSON.stringify(j, null, 2) : null);
    });
  }

  window.cdeckOrdersRefresh = refreshOrders;
  window.cdeckOrdersPaint = paintList;
})();
