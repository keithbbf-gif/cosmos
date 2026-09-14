(function () {
  "use strict";

  var LAST = null;

  function $(id) {
    return document.getElementById(id);
  }

  function e(s) {
    return typeof esc === "function" ? esc(s) : String(s == null ? "" : s);
  }

  function fmtNum(v) {
    if (v == null || v === "" || (typeof v === "number" && !isFinite(v))) {
      return "UNMEASURED";
    }
    return String(v);
  }

  function fmtUsdPerM(v) {
    if (v == null || v === "") return "UNMEASURED";
    var n = Number(v);
    if (!isFinite(n)) return "UNMEASURED";
    if (n === 0) return "$0";
    return "$" + n.toFixed(4) + "/M";
  }

  function refused(el, err) {
    var j = err && err.json;
    var msg = (j && j.detail) || (j && j.error) || err.message || String(err);
    if (el) el.innerHTML = "<p class=\"err\">" + e(msg) + "</p>";
  }

  function paintBlend(rec) {
    var el = $("mr-blend");
    if (!el) return;
    var b = rec && rec.blend;
    if (!b || typeof b !== "object") {
      el.innerHTML = "<h3>Blend</h3><p>UNMEASURED</p>";
      return;
    }
    el.innerHTML =
      "<h3>Blend (Core)</h3><p>" +
      e(String(Math.round((b.in || 0) * 100))) + "% in · " +
      e(String(Math.round((b.out || 0) * 100))) + "% out — " +
      "blended $/M on each row is 75% prompt + 25% completion when rates exist.</p>";
  }

  function paintBenchDefs(rec) {
    var el = $("mr-benches");
    if (!el) return;
    var defs = (rec && rec.bench_defs) || [];
    var cite = (rec && rec.bench_cite) || "";
    if (!defs.length) {
      el.innerHTML = "<h3>Benchmarks</h3><p>UNMEASURED — Core sent no bench_defs.</p>";
      return;
    }
    var rows = defs.map(function (d) {
      return "<tr><td>" + e(d.label || d.id) + "</td><td>" + e(d.def || "") + "</td></tr>";
    }).join("");
    el.innerHTML =
      "<h3>Benchmarks</h3>" +
      (cite ? "<p class=\"dim\">" + e(cite) + "</p>" : "") +
      "<table class=\"mr-table\"><thead><tr><th>Axis</th><th>Definition</th></tr></thead><tbody>" +
      rows + "</tbody></table>";
  }

  function paintCatalog(rec) {
    var el = $("mr-catalog");
    if (!el) return;
    var models = (rec && rec.models) || [];
    if (!models.length) {
      el.innerHTML =
        "<h3>Catalog</h3><p>empty — no models in Core projection (not a local fake list).</p>";
      return;
    }
    var head =
      "<tr><th>Model</th><th>blended $/M</th><th>INT</th><th>COD</th><th>GPQA</th></tr>";
    var rows = models.slice(0, 40).map(function (m) {
      return (
        "<tr><td>" + e(m.id || m.name) + "</td>" +
        "<td>" + e(fmtUsdPerM(m.blended_per_m)) + "</td>" +
        "<td>" + e(fmtNum(m.intelligence)) + "</td>" +
        "<td>" + e(fmtNum(m.coding)) + "</td>" +
        "<td>" + e(fmtNum(m.gpqa)) + "</td></tr>"
      );
    }).join("");
    el.innerHTML =
      "<h3>Catalog (" + e(String(rec.n || models.length)) + " shown)</h3>" +
      "<table class=\"mr-table\"><thead>" + head + "</thead><tbody>" + rows + "</tbody></table>";
  }

  function paintSeats(rec) {
    var el = $("mr-seats");
    if (!el) return;
    var seats = (rec && rec.seats) || [];
    if (!seats.length) {
      el.innerHTML = "<h3>Seats</h3><p>UNMEASURED</p>";
      return;
    }
    var rows = seats.map(function (s) {
      var model = s.model ? String(s.model) : "unassigned";
      return (
        "<tr data-profile=\"" + e(s.profile) + "\" data-seat=\"" + e(s.seat) + "\">" +
        "<td>" + e(s.label || s.seat) + "</td>" +
        "<td>" + e(model) + "</td>" +
        "<td>" + e(s.via || "") + "</td>" +
        "<td><button type=\"button\" class=\"mr-seat-est\" data-model=\"" + e(model) + "\">estimate</button></td>" +
        "</tr>"
      );
    }).join("");
    el.innerHTML =
      "<h3>Seats</h3>" +
      "<table class=\"mr-table\"><thead><tr><th>Role</th><th>Model</th><th>Via</th><th></th></tr></thead><tbody>" +
      rows + "</tbody></table>";
    el.querySelectorAll(".mr-seat-est").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var model = btn.getAttribute("data-model");
        if (!model || model === "unassigned") {
          addConsole("warn", "seat estimate", "pick a model on Core first");
          return;
        }
        postEstimate(model);
      });
    });
  }

  function paintJobCosts(rec) {
    var el = $("mr-estimate");
    if (!el) return;
    var job = (rec && rec.job_estimate) || {};
    var costs = (rec && rec.job_costs) || {};
    var ti = job.tokens_in != null ? job.tokens_in : (rec && rec.ccr_initial && rec.ccr_initial.tokens_in);
    var to = job.tokens_out != null ? job.tokens_out : (rec && rec.ccr_initial && rec.ccr_initial.tokens_out);
    el.innerHTML =
      "<h3>CCr job estimate</h3>" +
      "<p>tokens_in=" + e(fmtNum(ti)) + " tokens_out=" + e(fmtNum(to)) + "</p>" +
      "<button type=\"button\" id=\"btnMrJobEstimate\">POST /api/v1/model_rater/job_estimate</button>" +
      "<pre id=\"mr-job-costs\" class=\"tiny\">" + e(JSON.stringify(costs, null, 2)) + "</pre>";
    var btn = $("btnMrJobEstimate");
    if (btn) {
      btn.addEventListener("click", function () {
        apiPost("/api/v1/model_rater/job_estimate", {
          tokens_in: ti,
          tokens_out: to,
          override: true
        }).then(function (ans) {
          var pre = $("mr-job-costs");
          if (pre) pre.textContent = JSON.stringify(ans.job_costs || ans, null, 2);
          addConsole("ok", "job_estimate", JSON.stringify(ans.error || "ok"));
        }).catch(function (err) {
          refused($("mr-job-costs"), err);
        });
      });
    }
  }

  function paint(rec) {
    LAST = rec;
    var st = $("mr-status");
    if (st) {
      st.textContent = rec && rec.ok
        ? "GET /api/v1/model_rater — n=" + (rec.n || 0) + " stale=" + Boolean(rec.stale)
        : "REFUSED";
    }
    paintBlend(rec);
    paintBenchDefs(rec);
    paintSeats(rec);
    paintCatalog(rec);
    paintJobCosts(rec);
  }

  function load() {
    var body = $("modelRaterBody");
    if (body && !LAST) {
      var st = $("mr-status");
      if (st) st.textContent = "Loading GET /api/v1/model_rater …";
    }
    return apiGet("/api/v1/model_rater?limit=80").then(paint).catch(function (err) {
      refused(body, err);
      throw err;
    });
  }

  function postSeat(profile, seat, model, via) {
    var body = { profile: profile, seat: seat, model: model || "" };
    if (via) body.via = via;
    return apiPost("/api/v1/model_rater/seat", body).then(function (ans) {
      addConsole("ok", "seat", JSON.stringify(ans.error || profile + "." + seat));
      return load();
    }).catch(function (err) {
      addConsole("err", "seat", (err && err.message) || String(err));
      throw err;
    });
  }

  function postEstimate(model) {
    var job = (LAST && LAST.job_estimate) || {};
    var ti = job.tokens_in != null ? job.tokens_in : 24000;
    var to = job.tokens_out != null ? job.tokens_out : 8000;
    return apiPost("/api/v1/model_rater/estimate", {
      model: model,
      tokens_in: ti,
      tokens_out: to
    }).then(function (ans) {
      addConsole("ok", "estimate", JSON.stringify(ans));
      return ans;
    }).catch(function (err) {
      addConsole("err", "estimate", (err && err.message) || String(err));
      throw err;
    });
  }

  function refreshCatalog() {
    panelBusy(true);
    return apiPost("/api/v1/model_rater/refresh", {}).then(function () {
      return load();
    }).finally(function () {
      panelBusy(false);
    });
  }

  function openDrawer() {
    var drawer = $("model-rater-drawer");
    if (!drawer) return;
    drawer.classList.remove("hidden");
    load().catch(function () { /* painted refusal */ });
  }

  function bind() {
    var open = $("btnModelRater");
    var close = $("btnModelRaterClose");
    var refresh = $("btnModelRaterRefresh");
    if (open) open.addEventListener("click", openDrawer);
    if (close) {
      close.addEventListener("click", function () {
        var drawer = $("model-rater-drawer");
        if (drawer) drawer.classList.add("hidden");
      });
    }
    if (refresh) {
      refresh.addEventListener("click", function () {
        refreshCatalog().catch(function () { /* refusal shown */ });
      });
    }
  }

  window.deckModelRater = {
    load: load,
    paint: paint,
    postSeat: postSeat,
    postEstimate: postEstimate
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bind);
  } else {
    bind();
  }
})();
