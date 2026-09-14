(function () {
  "use strict";
  /* Open Sessions suite panes + Session kit (COS panes, autosave, auto-resession).
     Suite verbs are CLI via builds/session-tools/session_tools.py — POST only;
     no GET /api/v1/session_tools poll. */

  var SUITE_PANES = [
    { id: "scan", label: "Scan" },
    { id: "load", label: "Load" },
    { id: "convert", label: "Convert" },
    { id: "diff", label: "Diff" },
    { id: "check", label: "Check" },
    { id: "anonymize", label: "Anonymize" },
    { id: "crash-recover", label: "Crash recover" },
    { id: "strip", label: "leftover strip" },
    { id: "doi", label: "DOI named" }
  ];
  var AUTOSAVE_MIN = [5, 10, 20, 30];
  var COS_IDS = ["rold", "tidyup", "tu2", "bu"];
  var SUITE_NAMED = { strip: 1, doi: 1 };
  var MEASURED_ID = /^(cow-|grok-|ow-)/;
  var SCAN_MEASURED = { cowork: 1, grok_tui: 1, openwork_native: 1 };
  /* field: [key, label, required] — matches cosmos_session_tools_kit.run body keys */
  var SUITE_FIELDS = {
    scan: [
      ["store", "catalog store path", true],
      ["families", "families (comma-separated, optional)", false]
    ],
    load: [
      ["id", "session id (cow-|grok-|ow-)", true],
      ["store", "store path", true]
    ],
    convert: [
      ["id", "session id", true],
      ["store", "store path", true],
      ["out_dir", "out_dir path", true]
    ],
    diff: [
      ["left", "left file path", true],
      ["right", "right file path", true]
    ],
    check: [
      ["path", "path (or store)", true],
      ["what", "what (catalog|sqlite|seed|sit)", false]
    ],
    anonymize: [
      ["id", "session id", true],
      ["store", "store path", true],
      ["out_dir", "out_dir path", true]
    ],
    "crash-recover": [
      ["target", "target path", true],
      ["bak", "bak path (optional)", false],
      ["stage", "stage path (optional)", false]
    ]
  };

  function $(id) { return document.getElementById(id); }
  function esc(s) {
    if (s == null) return "";
    return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/"/g, "&quot;");
  }

  function paintSuite(host, sayEl) {
    if (!host) return;
    var h = '<div class="panel-hd"><h2>Open Sessions suite</h2>' +
      '<span class="dim tiny">Open Sessions · suite panes · Legal OMITTED</span></div>';
    h += '<div class="panel-bd"><div class="set-cards" role="list">';
    SUITE_PANES.forEach(function (p) {
      h += '<button type="button" class="set-card session-suite-pane" role="listitem" ' +
        'data-suite-verb="' + esc(p.id) + '"><h3>' + esc(p.label) + '</h3>' +
        '<p class="dim tiny">POST /api/v1/session_tools · verb=' + esc(p.id) + "</p></button>";
    });
    h += "</div>";
    h += '<p class="dim tiny">leftover strip and DOI named are suite panes, not silent polls.</p>';
    h += '<div class="session-suite-form formrow dim tiny" hidden></div>';
    h += '<pre class="session-suite-say dim tiny" aria-live="polite"></pre></div>';
    host.innerHTML = h;
    var formEl = host.querySelector(".session-suite-form");
    var say = sayEl || host.querySelector(".session-suite-say");
    host.querySelectorAll("[data-suite-verb]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        openSuiteVerb(btn.getAttribute("data-suite-verb"), formEl, say);
      });
    });
  }

  function suiteSayJson(sayEl, rec) {
    if (sayEl) sayEl.textContent = JSON.stringify(rec, null, 2);
  }

  function refuseUnmeasuredScan(familiesRaw, sayEl) {
    if (!familiesRaw) return false;
    var parts = String(familiesRaw).split(/[,\s]+/).filter(Boolean);
    if (!parts.length) return false;
    var any = parts.some(function (f) { return SCAN_MEASURED[f]; });
    if (any) return false;
    suiteSayJson(sayEl, {
      verb: "scan",
      kind: "UNMEASURED",
      gate: {
        detail: "no measured family in list — adapters not opened this slice",
        families: parts
      }
    });
    return true;
  }

  function refuseUnmeasuredId(verb, id, sayEl) {
    if (!id || MEASURED_ID.test(id)) return false;
    suiteSayJson(sayEl, {
      verb: verb,
      kind: "UNMEASURED",
      gate: { detail: "id prefix not measured this slice — use cow-, grok-, or ow-", id: id }
    });
    return true;
  }

  function bodyFromSuiteForm(verb, formEl, sayEl) {
    var fields = SUITE_FIELDS[verb];
    if (!fields) {
      suiteSayJson(sayEl, { kind: "BAD_INPUT", error: "verb not wired in UI: " + verb });
      return null;
    }
    var body = { verb: verb };
    var missing = [];
    fields.forEach(function (row) {
      var key = row[0];
      var req = row[2];
      var inp = formEl.querySelector('[data-suite-field="' + key + '"]');
      var val = inp ? String(inp.value || "").trim() : "";
      if (!val) {
        if (req) missing.push(key);
        return;
      }
      if (key === "families") {
        body.families = val.split(/[,\s]+/).filter(Boolean);
      } else if (key === "what") {
        body.what = val;
      } else {
        body[key] = val;
      }
    });
    if (missing.length) {
      suiteSayJson(sayEl, {
        kind: "BAD_INPUT",
        error: verb + " requires " + missing.join(", ")
      });
      return null;
    }
    if (verb === "scan" && refuseUnmeasuredScan(
        body.families ? body.families.join(",") : "", sayEl)) {
      return null;
    }
    if ((verb === "load" || verb === "convert" || verb === "anonymize")
        && refuseUnmeasuredId(verb, body.id, sayEl)) {
      return null;
    }
    if (verb === "check" && !body.what) body.what = "catalog";
    return body;
  }

  function openSuiteVerb(verb, formEl, sayEl) {
    if (!verb) return;
    if (SUITE_NAMED[verb]) {
      runSuiteVerb(verb, sayEl, { verb: verb });
      if (formEl) formEl.hidden = true;
      return;
    }
    var fields = SUITE_FIELDS[verb];
    if (!fields || !formEl) {
      suiteSayJson(sayEl, { kind: "UNMEASURED", error: "verb not wired: " + verb });
      return;
    }
    var h = '<span class="dim tiny">verb=' + esc(verb) + "</span>";
    fields.forEach(function (row) {
      h += '<label>' + esc(row[1]) + ' <input type="text" data-suite-field="' +
        esc(row[0]) + '" autocomplete="off"></label>';
    });
    h += '<button type="button" class="session-suite-run">RUN</button>';
    formEl.innerHTML = h;
    formEl.hidden = false;
    formEl.querySelector(".session-suite-run").addEventListener("click", function () {
      var body = bodyFromSuiteForm(verb, formEl, sayEl);
      if (body) runSuiteVerb(verb, sayEl, body);
    });
  }

  function runSuiteVerb(verb, sayEl, body) {
    if (!verb) return;
    body = body || { verb: verb };
    if (sayEl) {
      sayEl.textContent = "POST /api/v1/session_tools " + JSON.stringify(body) + " …";
    }
    apiPost("/api/v1/session_tools", body).then(function (rec) {
      if (sayEl) sayEl.textContent = JSON.stringify(rec, null, 2);
    }).catch(function (e) {
      if (sayEl) sayEl.textContent = String((e && e.message) || e);
    });
  }

  function paintKit(host) {
    if (!host) return;
    apiGet("/api/v1/session_kit").then(function (rec) {
      rec = rec || {};
      var cos = rec.cos || {};
      var rs = rec.resession || {};
      var mins = rec.autosave_min != null ? rec.autosave_min : 10;
      var h = '<div class="panel-hd"><h2>Session kit</h2>' +
        '<span class="dim tiny">COS panes · autosave · auto-resession triggers</span></div>';
      h += '<div class="panel-bd">';
      h += '<div class="formrow"><span class="dim tiny">COS panes</span><div class="chip-row">';
      COS_IDS.forEach(function (cid) {
        var on = cos[cid] !== false;
        h += '<label class="chip' + (on ? " on" : "") + '">' +
          '<input type="checkbox" data-cos="' + esc(cid) + '"' + (on ? " checked" : "") + "> " +
          esc(cid) + "</label>";
      });
      h += "</div></div>";
      h += '<div class="formrow"><span class="dim tiny">autosave min</span><div class="chip-row">';
      AUTOSAVE_MIN.forEach(function (m) {
        h += '<label class="chip' + (mins === m ? " on" : "") + '">' +
          '<input type="radio" name="autosave_min" value="' + m + '"' +
          (mins === m ? " checked" : "") + "> " + m + " min</label>";
      });
      h += "</div></div>";
      h += '<div class="formrow dim tiny">auto-resession triggers (config only — SAVE does not fire a resession)</div>';
      h += '<label class="chip"><input type="checkbox" data-rs="on_compaction"' +
        (rs.on_compaction !== false ? " checked" : "") + "> on_compaction</label>";
      h += '<label class="chip"><input type="checkbox" data-rs="on_token_count"' +
        (rs.on_token_count !== false ? " checked" : "") + "> on_token_count</label>";
      h += '<label>time_s <input type="number" id="session-kit-time-s" min="0" value="' +
        esc(rs.time_s != null ? rs.time_s : 0) + '"></label>';
      h += '<label>context_tokens <input type="number" id="session-kit-ctx-tok" min="0" value="' +
        esc(rs.context_tokens != null ? rs.context_tokens : 0) + '"></label>';
      h += '<div class="formrow"><button type="button" id="session-kit-save">SAVE session kit</button></div>';
      h += '<pre class="session-kit-say dim tiny" aria-live="polite"></pre></div>';
      host.innerHTML = h;
      var saveBtn = host.querySelector("#session-kit-save");
      if (saveBtn) {
        saveBtn.addEventListener("click", function () { saveKit(host); });
      }
    }).catch(function (e) {
      host.textContent = String((e && e.message) || e);
    });
  }

  function saveKit(host) {
    var body = { cos: {}, resession: {} };
    host.querySelectorAll("[data-cos]").forEach(function (inp) {
      body.cos[inp.getAttribute("data-cos")] = inp.checked;
    });
    var picked = host.querySelector('input[name="autosave_min"]:checked');
    if (picked) body.autosave_min = parseInt(picked.value, 10);
    host.querySelectorAll("[data-rs]").forEach(function (inp) {
      body.resession[inp.getAttribute("data-rs")] = inp.checked;
    });
    var ts = host.querySelector("#session-kit-time-s");
    var ct = host.querySelector("#session-kit-ctx-tok");
    if (ts) body.resession.time_s = parseInt(ts.value, 10) || 0;
    if (ct) body.resession.context_tokens = parseInt(ct.value, 10) || 0;
    var say = host.querySelector(".session-kit-say");
    if (say) say.textContent = "POST /api/v1/session_kit …";
    apiPost("/api/v1/session_kit", body).then(function (rec) {
      if (say) say.textContent = JSON.stringify(rec, null, 2);
    }).catch(function (e) {
      if (say) say.textContent = String((e && e.message) || e);
    });
  }

  function _tlKindCls(kind) {
    var k = String(kind || "").toUpperCase();
    if (/APPLIED|VERIFIED|OK|PASS|DONE/.test(k)) return "ok";
    if (/FAIL|ROLL|ERROR|BAD/.test(k)) return "err";
    if (/WARN|WATCH|HOLD|BLOCK/.test(k)) return "warn";
    return "dim";
  }

  /* ROLLED milestone timeline — one GET when Core serves /api/v1/rolled (no poll). */
  function paintRolledTimeline(host) {
    if (!host) return;
    host.textContent = "GET /api/v1/rolled …";
    apiGet("/api/v1/rolled").then(function (d) {
      d = d || {};
      var events = Array.isArray(d.events) ? d.events : [];
      var available = !!d.available;
      var kind = String(d.kind || "");
      if (!available || events.length === 0) {
        var why = !available
          ? (kind === "NO_SOURCE"
              ? "ROLLED.md not present — no milestones recorded yet"
              : "ROLLED.md unavailable (" + kind + ")")
          : "ROLLED.md present but contains no rolled-event/1 lines"; /* schema rolled-event/1 */
        host.innerHTML = '<div class="tl-empty">' + esc(why) + "</div>";
        return;
      }
      var hdr = '<div class="tl-hdr"><span>TIME</span><span>SEAT</span><span>KIND</span>' +
        "<span>TITLE</span><span>REF</span></div>";
      var rows = events.map(function (ev) {
        var kCls = _tlKindCls(ev.kind);
        return '<div class="tl-row">' +
          '<span class="tl-t">' + esc(ev.t || "—") + "</span>" +
          '<span class="tl-seat">' + esc(ev.seat || "—") + "</span>" +
          '<span class="tl-kind ' + kCls + '">' + esc(ev.kind || "—") + "</span>" +
          '<span class="tl-title">' + esc(ev.title || "—") + "</span>" +
          '<span class="tl-ref">' + esc(ev.ref || "") + "</span></div>";
      }).join("");
      host.innerHTML = hdr + '<div class="tl-body">' + rows + "</div>";
    }).catch(function (e) {
      host.textContent = String((e && e.message) || e);
    });
  }

  function boot() {
    var kitHost = $("panel-session-kit");
    var suiteHost = $("panel-open-sessions-suite") || $("panel-recents-sessions");
    var rolledHost = $("panel-rolled-timeline");
    var say = $("panel-session-say");
    paintKit(kitHost);
    paintSuite(suiteHost, say);
    paintRolledTimeline(rolledHost);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
