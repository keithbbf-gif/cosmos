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

  function suiteVerbBody(verb) {
    var body = { verb: verb };
    if (verb === "scan") {
      var store = window.prompt("scan: store path (optional, Enter to skip)", "");
      if (store) body.store = store;
      var fam = window.prompt("scan: family (optional, Enter to skip)", "");
      if (fam) body.families = [fam];
      return body;
    }
    if (verb === "load") {
      body.id = window.prompt("load: session id (required)", "") || "";
      body.store = window.prompt("load: store path (required)", "") || "";
      if (!body.id || !body.store) return null;
      return body;
    }
    if (verb === "convert" || verb === "anonymize") {
      body.id = window.prompt(verb + ": session id (required)", "") || "";
      body.store = window.prompt(verb + ": store path (required)", "") || "";
      body.out_dir = window.prompt(verb + ": out_dir (required)", "") || "";
      if (!body.id || !body.store || !body.out_dir) return null;
      return body;
    }
    if (verb === "diff") {
      body.left = window.prompt("diff: left path (required)", "") || "";
      body.right = window.prompt("diff: right path (required)", "") || "";
      if (!body.left || !body.right) return null;
      return body;
    }
    if (verb === "check") {
      body.path = window.prompt("check: path or store (required)", "") || "";
      if (!body.path) return null;
      body.what = window.prompt("check: what (default catalog)", "catalog") || "catalog";
      return body;
    }
    if (verb === "crash-recover") {
      body.target = window.prompt("crash-recover: target path (required)", "") || "";
      if (!body.target) return null;
      var bak = window.prompt("crash-recover: bak path (optional)", "");
      if (bak) body.bak = bak;
      return body;
    }
    return body;
  }

  function runSuiteVerb(verb, sayEl) {
    if (!verb) return;
    var body = suiteVerbBody(verb);
    if (!body) {
      if (sayEl) sayEl.textContent = "Cancelled — " + verb + " requires arguments.";
      return;
    }
    if (sayEl) sayEl.textContent = "POST /api/v1/session_tools verb=" + verb + " …";
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

  /* Server marks missing path refs UNRESOLVED; client parseRolledFeeds sorts by (t, seq). */
  var ROLLED_EVENT_SCHEMA = "rolled-event/1";

  function parseRolledEventLine(line, autoSeq) {
    var stripped = String(line || "").trim();
    if (stripped.indexOf(ROLLED_EVENT_SCHEMA) !== 0) return null;
    var body = stripped.slice(ROLLED_EVENT_SCHEMA.length).trim();
    var parts = body.split("|").map(function (p) { return p.trim(); });
    if (parts.length < 4) return null;
    var seq = autoSeq;
    if (parts.length > 5 && parts[5] !== "") {
      var n = parseInt(parts[5], 10);
      if (!isNaN(n)) seq = n;
    }
    var ref = parts.length > 4 ? parts[4] : "";
    return {
      t: parts[0] || "",
      seat: parts[1] || "",
      kind: parts[2] || "",
      title: parts[3] || "",
      ref: ref,
      seq: seq
    };
  }

  function parseRolledFeeds(feeds) {
    var events = [];
    var autoSeq = 0;
    (feeds || []).forEach(function (fd) {
      var text = fd && fd.text != null ? String(fd.text) : "";
      text.split(/\r?\n/).forEach(function (line) {
        autoSeq += 1;
        var ev = parseRolledEventLine(line, autoSeq);
        if (ev) events.push(ev);
      });
    });
    events.sort(function (a, b) {
      var ta = String(a.t || "");
      var tb = String(b.t || "");
      if (ta !== tb) return ta < tb ? -1 : 1;
      return (a.seq || 0) - (b.seq || 0);
    });
    return events;
  }

  function paintRolledTimeline(host) {
    if (!host) return;
    host.textContent = "GET /api/v1/rolled …";
    apiGet("/api/v1/rolled").then(function (d) {
      d = d || {};
      var feeds = Array.isArray(d.feeds) ? d.feeds : [];
      var events = [];
      if (Array.isArray(d.events) && d.events.length) {
        events = d.events;
      } else if (feeds.length) {
        events = parseRolledFeeds(feeds);
      }
      var available = !!d.available;
      var kind = String(d.kind || "");
      if (!available || events.length === 0) {
        var why = !available
          ? (kind === "NO_SOURCE"
              ? "COSMOS_ROLLED_FEED / ROLLED.md not present — explicit empty"
              : "ROLLED feed unavailable (" + esc(kind) + ")")
          : "ROLLED feed present but no rolled-event/1 lines — explicit empty";
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
    if (!kitHost && !suiteHost && !rolledHost) return false;
    paintKit(kitHost);
    paintSuite(suiteHost, say);
    paintRolledTimeline(rolledHost);
    return true;
  }

  window.__cdeck_bootSessionKit = boot;

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
