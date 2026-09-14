/* builds/cdeck/ui/app.js — transport, live events inspector, map pulse contract. */

(function () {
  "use strict";

  var FETCH_TO_MS = 8000;
  var cfg = window.__CDECK_CFG || { base: "http://127.0.0.1:8770", token: "" };

  function apiCall(path, opts) {
    var method = (opts && opts.method) || "GET";
    var ctl = new AbortController();
    var timer = setTimeout(function () { ctl.abort(); }, FETCH_TO_MS);
    var url = cfg.base.replace(/\/+$/, "") + path;
    var headers = cfg.token ? { "Authorization": "Bearer " + cfg.token } : {};
    var init = { method: method, headers: headers, signal: ctl.signal, cache: "no-store" };
    if (opts && opts.body !== undefined) {
      headers["Content-Type"] = "application/json";
      init.body = JSON.stringify(opts.body);
    }
    return fetch(url, init).then(function (r) {
      clearTimeout(timer);
      return r.text().then(function (txt) {
        var j = {};
        try { j = txt ? JSON.parse(txt) : {}; } catch (_) { j = {}; }
        if (r.status === 503) {
          var detail = j.error ? String(j.error) : "CDECK_PANEL_NOT_COMPOSED";
          var e503 = new Error(detail);
          e503.status = 503;
          e503.json = j;
          throw e503;
        }
        if (!r.ok) {
          var msg = j.error ? String(j.error) : ("HTTP " + r.status);
          var eN = new Error(msg);
          eN.status = r.status;
          eN.json = j;
          throw eN;
        }
        return j;
      });
    }).catch(function (e) {
      clearTimeout(timer);
      throw e;
    });
  }

  window.apiCall = apiCall;
  window.apiGet = function (path) { return apiCall(path); };
  window.apiPost = function (path, body) { return apiCall(path, { method: "POST", body: body }); };

  /* --- live events inspector (EVT-1) --- */
  var FOLLOW_KEYS = ["link_id", "rail", "node", "job_id", "sid", "rid"];
  var feedPinned = true;
  var feedUnseen = 0;
  var feedFollow = null;

  function eventIds(ev) {
    var p = ev && ev.payload, out = [];
    if (!p || typeof p !== "object") return out;
    FOLLOW_KEYS.forEach(function (k) {
      var v = p[k];
      if (v === null || v === undefined || typeof v === "object") return;
      var s = String(v).trim();
      if (s !== "") out.push({ key: k, value: s });
    });
    return out;
  }

  function inspectHtml(ev) {
    var h = '<div class="finspect"><pre>' + JSON.stringify(ev.payload || null, null, 1) + "</pre></div>";
    return h;
  }

  function toggleInspect(row) {
    var open = row.querySelector(".finspect");
    if (open) { open.remove(); row.classList.remove("open"); return; }
    row.classList.add("open");
    row.insertAdjacentHTML("beforeend", inspectHtml(row.__ev || {}));
  }

  var feedEl = document.getElementById("feed");
  if (feedEl) {
    feedEl.addEventListener("click", function (e) {
      var row = e.target && e.target.closest ? e.target.closest(".fevent") : null;
      if (row) toggleInspect(row);
    });
    feedEl.addEventListener("scroll", function () {
      var atTail = (feedEl.scrollHeight - feedEl.scrollTop - feedEl.clientHeight) <= 4;
      if (atTail !== feedPinned) {
        feedPinned = atTail;
        if (atTail) feedUnseen = 0;
      }
    });
  }

  /* --- map pulse (PULSE-1) ---
   * PULSE-1: a node the map does not already hold is NEVER created by an event.
   * Ids come from eventIds(); the only typed home map is PULSE_HOME for events
   * that name no harvestable id. Pending pulses wait for nmapDomReady once. */
  var PULSE_HOME = {
    COMMAND_HANDLED: "CVM"
  };
  var nmapPulsePending = [];
  var nmapDomReady = false;
  var nmapKnown = Object.create(null);

  function nodeOnMap(nodeId) {
    return !!(nodeId && nmapKnown[nodeId]);
  }

  function registerMapNode(nodeId) {
    if (nodeId) nmapKnown[nodeId] = true;
  }

  function pulseFromEvent(ev) {
    var ids = eventIds(ev);
    var nodeId = null;
    if (ids.length) {
      for (var i = 0; i < ids.length; i++) {
        if (ids[i].key === "node") { nodeId = ids[i].value; break; }
        if (ids[i].key === "link_id" || ids[i].key === "rail") {
          nodeId = ids[i].value;
          break;
        }
      }
    }
    if (!nodeId && ev && ev.event && PULSE_HOME[ev.event]) {
      nodeId = PULSE_HOME[ev.event];
    }
    if (!nodeId) return false;
    if (!nmapDomReady) {
      nmapPulsePending.push({ ev: ev, nodeId: nodeId });
      return false;
    }
    if (!nodeOnMap(nodeId)) return false;
    return true;
  }

  function flushPendingPulses() {
    if (!nmapDomReady || !nmapPulsePending.length) return;
    var q = nmapPulsePending.slice();
    nmapPulsePending.length = 0;
    q.forEach(function (item) { pulseFromEvent(item.ev); });
  }

  function nmapDomReadyHook() {
    nmapDomReady = true;
    flushPendingPulses();
  }

  window.__cdeck_pulse = {
    PULSE_HOME: PULSE_HOME,
    pulseFromEvent: pulseFromEvent,
    registerMapNode: registerMapNode,
    nmapDomReady: nmapDomReadyHook,
    nmapPulsePending: nmapPulsePending,
    flushPendingPulses: flushPendingPulses
  };

  /* --- Tools extra pane: live GETs only (no embedded maker/tool catalog) --- */
  var CREATE_KINDS = ["AGENT", "TOOL", "CONNECTOR", "SKILL"];
  var toolsCreateKind = CREATE_KINDS[0];
  var toolsPaneHost = null;

  function escHtml(s) {
    if (s == null) return "";
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/"/g, "&quot;");
  }

  function renderTools(d) {
    var rep = (d && d.report) || [];
    if (!rep.length) {
      return '<div class="empty">no tools reported</div>';
    }
    var rows = rep.map(function (t) {
      var v = t.verified === true ? "yes" : t.verified === false ? "no" : "—";
      return "<tr><td>" + escHtml(t.name) + "</td><td>" + escHtml(t.disposition) +
        "</td><td>" + escHtml(v) + "</td><td>" + escHtml(t.age_s) + "</td></tr>";
    }).join("");
    return '<details open class="tooltable"><summary>tool contracts (' + rep.length +
      ')</summary><table><thead><tr><th>name</th><th>disposition</th><th>verified</th>' +
      "<th>age_s</th></tr></thead><tbody>" + rows + "</tbody></table></details>";
  }

  function kitSection(title, rows, cols) {
    if (!rows || !rows.length) {
      return "<section><h3>" + escHtml(title) + '</h3><div class="empty">empty</div></section>';
    }
    var head = cols.map(function (c) { return "<th>" + escHtml(c) + "</th>"; }).join("");
    var body = rows.map(function (r) {
      return "<tr>" + cols.map(function (c) {
        return "<td>" + escHtml(r[c]) + "</td>";
      }).join("") + "</tr>";
    }).join("");
    return "<section><h3>" + escHtml(title) + " (" + rows.length + ")</h3><table><thead><tr>" +
      head + "</tr></thead><tbody>" + body + "</tbody></table></section>";
  }

  function renderToolsKit(d) {
    d = d || {};
    var cosmos = d.cosmos || [];
    var local = d.local || [];
    var customRows = (d.custom && d.custom.rows) || [];
    var other = d.other || {};
    var hands = other.hands || [];
    var h = '<div class="tools-kit">';
    h += kitSection("COSMOS components", cosmos, ["id", "label", "kind", "lane"]);
    h += kitSection("local callables", local, ["id", "label", "kind", "lane"]);
    h += kitSection("makers seed (GET /makers is authoritative)", customRows,
      ["id", "maker_kind", "location"]);
    h += kitSection("PATH hands", hands, ["id", "label", "kind", "channel"]);
    if (other.contracts && other.contracts.rows && other.contracts.rows.length) {
      h += kitSection("contracts fold", other.contracts.rows,
        ["name", "disposition", "verified"]);
    }
    h += "</div>";
    return h;
  }

  function makerCard(m) {
    var srcs = (m.potential_sources && m.potential_sources.length)
      ? m.potential_sources.join(" · ") : "—";
    return '<div class="mcard"><div><b>' + escHtml(m.id) + '</b> <span class="chip">' +
      escHtml(m.kind) + '</span></div><details><summary>open maker</summary><dl class="kv">' +
      "<dt>where</dt><dd>" + escHtml(m.location) + "</dd><dt>do</dt><dd>" +
      escHtml(m.function) + "</dd><dt>how</dt><dd>" + escHtml(m.access) +
      "</dd><dt>sources</dt><dd>" + escHtml(srcs) + "</dd></dl></details></div>";
  }

  function renderToolsCreate(d, kind) {
    var rows = (d && d.makers) || [];
    if (!rows.length) {
      return '<div class="empty">no makers of kind ' + escHtml(kind) +
        " — none registered, not an error</div>";
    }
    return rows.map(makerCard).join("");
  }

  function renderToolsMakers(d) {
    var rows = (d && d.makers) || [];
    if (!rows.length) {
      return '<div class="empty">no makers registered</div>';
    }
    return rows.map(makerCard).join("");
  }

  function readMakerForm(host) {
    return {
      id: (host.querySelector("#tools-maker-id") || {}).value || "",
      kind: (host.querySelector("#tools-maker-kind") || {}).value || "",
      location: (host.querySelector("#tools-maker-location") || {}).value || "",
      function: (host.querySelector("#tools-maker-function") || {}).value || "",
      access: (host.querySelector("#tools-maker-access") || {}).value || ""
    };
  }

  function readJobForm(host) {
    return {
      command: (host.querySelector("#tools-job-command") || {}).value || "",
      priority: (host.querySelector("#tools-job-priority") || {}).value || "normal"
    };
  }

  function paintToolsPane(host, kitRec, toolsRec, makersRec, createRec) {
    var kindChips = CREATE_KINDS.map(function (k) {
      var on = k === toolsCreateKind ? " on" : "";
      return '<button type="button" class="chip tools-create-kind' + on +
        '" data-create-kind="' + k + '">' + k + "</button>";
    }).join("");
    host.innerHTML =
      '<div class="panel-hd"><h2>TOOLS</h2><span class="dim tiny">GET tools_kit · tools · makers</span></div>' +
      '<div class="panel-bd">' +
      renderToolsKit(kitRec) +
      renderTools(toolsRec) +
      '<section><h3>maker map</h3>' + renderToolsMakers(makersRec) + "</section>" +
      '<section><h3>CREATE</h3><div class="chip-row">' + kindChips +
      '</div><div id="tools-create-cards">' + renderToolsCreate(createRec, toolsCreateKind) +
      "</div></section>" +
      '<section><h3>register maker</h3>' +
      '<label>id <input id="tools-maker-id" type="text" autocomplete="off"></label>' +
      '<label>kind <input id="tools-maker-kind" type="text" autocomplete="off"></label>' +
      '<label>location <input id="tools-maker-location" type="text"></label>' +
      '<label>function <input id="tools-maker-function" type="text"></label>' +
      '<label>access <input id="tools-maker-access" type="text"></label>' +
      '<button type="button" id="tools-register-maker">POST /makers</button>' +
      '<pre class="tools-maker-say dim tiny" aria-live="polite"></pre></section>' +
      '<section><h3>queue job</h3>' +
      '<label>command <input id="tools-job-command" type="text"></label>' +
      '<label>priority <select id="tools-job-priority">' +
      '<option>normal</option><option>low</option><option>high</option><option>critical</option>' +
      "</select></label>" +
      '<button type="button" id="tools-queue-job">POST /jobs</button>' +
      '<pre class="tools-job-say dim tiny" aria-live="polite"></pre></section>' +
      "</div>";

    host.querySelectorAll(".tools-create-kind").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var k = btn.getAttribute("data-create-kind");
        if (CREATE_KINDS.indexOf(k) < 0) return;
        toolsCreateKind = k;
        loadToolsPane(host);
      });
    });

    var reg = host.querySelector("#tools-register-maker");
    if (reg) {
      reg.addEventListener("click", function () {
        var body = readMakerForm(host);
        var say = host.querySelector(".tools-maker-say");
        if (say) say.textContent = "POST /api/v1/makers …";
        apiPost("/api/v1/makers", body).then(function (rec) {
          if (say) say.textContent = JSON.stringify(rec, null, 2);
          return loadToolsPane(host);
        }).catch(function (e) {
          if (say) say.textContent = String((e && e.message) || e);
        });
      });
    }

    var jobBtn = host.querySelector("#tools-queue-job");
    if (jobBtn) {
      jobBtn.addEventListener("click", function () {
        var body = readJobForm(host);
        var say = host.querySelector(".tools-job-say");
        if (say) say.textContent = "POST /api/v1/jobs …";
        apiPost("/api/v1/jobs", body).then(function (rec) {
          if (say) say.textContent = JSON.stringify(rec, null, 2);
        }).catch(function (e) {
          if (say) say.textContent = String((e && e.message) || e);
        });
      });
    }
  }

  function loadToolsPane(host) {
    toolsPaneHost = host;
    host.innerHTML = '<div class="empty">loading tools…</div>';
    var createPath = "/api/v1/makers?kind=" + encodeURIComponent(toolsCreateKind);
    return Promise.all([
      apiGet("/api/v1/tools_kit"),
      apiGet("/api/v1/tools"),
      apiGet("/api/v1/makers"),
      apiGet(createPath)
    ]).then(function (parts) {
      paintToolsPane(host, parts[0], parts[1], parts[2], parts[3]);
    }).catch(function (e) {
      host.innerHTML = '<div class="empty">' + escHtml((e && e.message) || e) + "</div>";
    });
  }

  function onToolsTabSelected() {
    var stage = document.getElementById("deck-stage");
    if (!stage) return;
    var host = document.getElementById("panel-tools");
    if (!host) {
      host = document.createElement("div");
      host.id = "panel-tools";
      host.className = "tools-pane";
    }
    stage.innerHTML = "";
    stage.appendChild(host);
    loadToolsPane(host);
  }

  document.addEventListener("click", function (e) {
    var btn = e.target && e.target.closest ? e.target.closest("[data-tab]") : null;
    if (!btn) return;
    if (btn.getAttribute("data-tab") === "tools") onToolsTabSelected();
  });

  window.__cdeck_tools = {
    renderToolsKit: renderToolsKit,
    renderTools: renderTools,
    loadToolsPane: loadToolsPane
  };
})();
