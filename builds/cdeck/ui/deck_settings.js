"use strict";
// deck_settings.js — Settings popup: status / usage / spend cards; vendor payment links only.
(function () {
  var POP_ID = "cdeck-settings-pop";
  var KEITH_MONEY =
    "Keith does money; this TUI does not complete a charge.";

  function esc(s) {
    if (s == null) return "";
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/"/g, "&quot;");
  }

  function apiGet(path) {
    var h = window.cdeckHeader;
    if (!h || typeof h.apiGet !== "function") {
      return Promise.reject(new Error("apiGet unavailable"));
    }
    return h.apiGet(path);
  }

  function $(id) {
    return document.getElementById(id);
  }

  /** Tokens stay UNMEASURED until Core reports n_obs >= 1 (usage fold). */
  function tokField(v, usage) {
    var nObs = usage && usage.n_obs;
    var kind = usage && usage.kind;
    if (!nObs || nObs < 1 || kind === "UNMEASURED") return "UNMEASURED";
    if (v == null || v === "") return "UNMEASURED";
    return String(v);
  }

  function cachedField(usage) {
    var nObs = usage && usage.n_obs;
    if (!nObs || nObs < 1) return "UNMEASURED";
    var last = usage && usage.last;
    if (!last || typeof last !== "object") return "UNMEASURED";
    var c = last.cached_tokens;
    if (c == null || c === "") return "UNMEASURED";
    return String(c);
  }

  function paintStatus(body) {
    var el = $("set-card-status");
    if (!el) return;
    body = body || {};
    var ready = body.ready === true ? "ready" : String(body.ready);
    var tree = body.tree_id != null ? String(body.tree_id) : "UNMEASURED";
    var head = body.ledger_head && body.ledger_head.seq != null
      ? String(body.ledger_head.seq)
      : "UNMEASURED";
    el.innerHTML =
      '<h3>Status</h3>' +
      '<p class="dim tiny">GET /api/v1/status</p>' +
      '<dl class="set-kv">' +
      "<dt>ready</dt><dd>" + esc(ready) + "</dd>" +
      "<dt>tree_id</dt><dd>" + esc(tree) + "</dd>" +
      "<dt>ledger_head</dt><dd>" + esc(head) + "</dd>" +
      "</dl>";
  }

  function paintUsage(body) {
    var el = $("set-card-usage");
    if (!el) return;
    body = body || {};
    var nObs = body.n_obs != null ? body.n_obs : 0;
    var kind = body.kind != null ? String(body.kind) : "UNMEASURED";
    el.innerHTML =
      '<h3>Quota · Usage</h3>' +
      '<p class="dim tiny">GET /api/v1/usage — in/out/cached; missing = UNMEASURED</p>' +
      '<dl class="set-kv">' +
      "<dt>n_obs</dt><dd>" + esc(String(nObs)) + "</dd>" +
      "<dt>kind</dt><dd>" + esc(kind) + "</dd>" +
      "<dt>prompt (in)</dt><dd>" + esc(tokField(body.prompt_tokens, body)) + "</dd>" +
      "<dt>completion (out)</dt><dd>" +
      esc(tokField(body.completion_tokens, body)) + "</dd>" +
      "<dt>cached</dt><dd>" + esc(cachedField(body)) + "</dd>" +
      "</dl>";
  }

  function spendSummary(body) {
    body = body || {};
    var rails = body.rails && typeof body.rails === "object" ? body.rails : {};
    var keys = Object.keys(rails);
    if (!keys.length) return "UNMEASURED";
    var parts = [];
    keys.slice(0, 6).forEach(function (k) {
      var row = rails[k] || {};
      var cap = row.cap_usd != null ? row.cap_usd : "?";
      var settled = row.settled_usd != null ? row.settled_usd : "?";
      parts.push(k + " cap=" + cap + " settled=" + settled);
    });
    if (keys.length > 6) parts.push("+" + (keys.length - 6) + " more");
    return parts.join("; ");
  }

  function paintSpend(body) {
    var el = $("set-card-spend");
    if (!el) return;
    body = body || {};
    var at = body.measured_at_epoch != null
      ? String(body.measured_at_epoch)
      : "UNMEASURED";
    el.innerHTML =
      '<h3>Spend gate</h3>' +
      '<p class="dim tiny">GET /api/v1/spend — audit only; POST is Keith-gated widen</p>' +
      '<dl class="set-kv">' +
      "<dt>measured_at_epoch</dt><dd>" + esc(at) + "</dd>" +
      "<dt>rails</dt><dd>" + esc(spendSummary(body)) + "</dd>" +
      "</dl>";
  }

  /** Payment rows = vendor homepages (docs URLs from GET /api/v1/cred). No checkout. */
  function paintPayments(body) {
    var host = $("set-pay-rows");
    if (!host) return;
    body = body || {};
    var rows = Array.isArray(body.sources) ? body.sources : [];
    var h = '<div class="set-cards set-pay" role="list" data-stub="payment-rows">';
    var n = 0;
    rows.forEach(function (s) {
      if (!s || typeof s !== "object") return;
      var href = s.docs ? String(s.docs).trim() : "";
      if (!href || !/^https?:\/\//i.test(href)) return;
      n += 1;
      h +=
        '<a class="set-card set-pay-row" role="listitem" data-vendor="' +
        esc(s.id || "") +
        '" href="' +
        esc(href) +
        '" target="_blank" rel="noopener noreferrer">' +
        esc(s.label || s.id || "vendor") +
        "</a>";
    });
    h += "</div>";
    if (!n) {
      h =
        '<p class="dim tiny">Billing links UNMEASURED — Core sent no cred.sources docs URLs.</p>';
    }
    h += '<p class="dim tiny set-money-note">' + esc(KEITH_MONEY) + "</p>";
    host.innerHTML = h;
  }

  function paintError(msg) {
    var note = $("set-settings-err");
    if (note) note.textContent = msg ? String(msg) : "";
  }

  function refresh() {
    paintError("");
    return Promise.all([
      apiGet("/api/v1/status"),
      apiGet("/api/v1/usage"),
      apiGet("/api/v1/spend"),
      apiGet("/api/v1/cred"),
    ])
      .then(function (parts) {
        paintStatus(parts[0]);
        paintUsage(parts[1]);
        paintSpend(parts[2]);
        paintPayments(parts[3]);
      })
      .catch(function (e) {
        paintError(e && e.message ? e.message : String(e));
      });
  }

  function openPop() {
    var pop = $(POP_ID);
    if (!pop) return;
    pop.hidden = false;
    pop.classList.add("open");
    refresh();
  }

  function closePop() {
    var pop = $(POP_ID);
    if (!pop) return;
    pop.hidden = true;
    pop.classList.remove("open");
  }

  function bindChrome() {
    var pop = $(POP_ID);
    if (!pop) return;
    var closeBtn = pop.querySelector("[data-action=close-settings]");
    if (closeBtn) {
      closeBtn.addEventListener("click", function (ev) {
        ev.preventDefault();
        closePop();
      });
    }
    pop.addEventListener("click", function (ev) {
      if (ev.target === pop) closePop();
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bindChrome);
  } else {
    bindChrome();
  }

  window.deckSettings = {
    open: openPop,
    close: closePop,
    refresh: refresh,
    tokField: tokField,
    cachedField: cachedField,
  };
})();
