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
    h += '<pre class="session-suite-say dim tiny" aria-live="polite"></pre></div>';
    host.innerHTML = h;
    host.querySelectorAll("[data-suite-verb]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        runSuiteVerb(btn.getAttribute("data-suite-verb"), sayEl || host.querySelector(".session-suite-say"));
      });
    });
  }

  function runSuiteVerb(verb, sayEl) {
    if (!verb) return;
    if (sayEl) sayEl.textContent = "POST /api/v1/session_tools verb=" + verb + " …";
    apiPost("/api/v1/session_tools", { verb: verb }).then(function (rec) {
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

  function boot() {
    var kitHost = $("panel-session-kit");
    var suiteHost = $("panel-open-sessions-suite") || $("panel-recents-sessions");
    var say = $("panel-session-say");
    paintKit(kitHost);
    paintSuite(suiteHost, say);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
