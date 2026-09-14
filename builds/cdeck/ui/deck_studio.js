/* deck_studio.js — MOTIF Studio extra pane (9 stages, config only).
 *
 * GET  /api/v1/studio  — load DEFINE→ITERATE pack (header apiGet only).
 * POST /api/v1/studio  — save stage config. Does NOT start MOTIF.
 * GET  /api/v1/jukebox — heat overlay from queue words only.
 *
 * SAVE never IMPLEMENTs: no CCr apply, no WD2 motif driver, no queue submit.
 */
(function (global) {
  "use strict";

  var JUKEBOX_WORDS = ["QUEUED", "RUNNING", "BROKE", "CLEAN", "FINDINGS"];
  var STAGES = [
    { id: "define", n: 1, name: "DEFINE", packKey: "define", field: "text" },
    { id: "research", n: 2, name: "RESEARCH", packKey: "research" },
    { id: "arch", n: 3, name: "ARCH", packKey: "arch" },
    { id: "consensus", n: 4, name: "CONSENSUS", packKey: "consensus" },
    { id: "build", n: 5, name: "BUILD", packKey: "build" },
    { id: "critics", n: 6, name: "CRITICS", packKey: "critics" },
    { id: "consensus2", n: 7, name: "CONSENSUS", packKey: "consensus" },
    { id: "implement", n: 8, name: "IMPLEMENT", packKey: "implement" },
    { id: "iterate", n: 9, name: "ITERATE", packKey: "iterate" },
  ];

  var state = {
    pack: null,
    activeId: "define",
    heat: {},
    jukeboxNote: "",
  };

  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function kitApi(kit) {
    var g = global.cdeckHeader || {};
    return {
      get: (kit && kit.apiGet) || g.apiGet,
      post: (kit && kit.apiPost) || g.apiPost,
    };
  }

  function stageFromJobRow(row) {
    if (!row || typeof row !== "object") return null;
    var blob = [
      row.command,
      row.job_id,
      row.id,
      row.name,
      row.token,
      row.outcome,
    ]
      .filter(Boolean)
      .join(" ");
    var m = /motif[_\w-]*_s(\d)/i.exec(blob) || /_s(\d)(?:_|$)/i.exec(blob);
    if (m) return parseInt(m[1], 10);
    return null;
  }

  function heatClassForOutcome(outcome, stale) {
    var o = String(outcome || "").toUpperCase();
    if (JUKEBOX_WORDS.indexOf(o) < 0 && o) return "";
    if (stale && o === "RUNNING") return "studio-heat-stale";
    if (o === "RUNNING" || o === "QUEUED") return "studio-heat-hot";
    if (o === "FINDINGS" || o === "BROKE") return "studio-heat-warn";
    if (o === "CLEAN") return "studio-heat-clean";
    return "";
  }

  function paintHeatFromJukebox(juke) {
    var heat = {};
    var rows = (juke && (juke.jobs || juke.queue || juke.rows)) || [];
    if (!Array.isArray(rows)) rows = [];
    for (var i = 0; i < rows.length; i++) {
      var row = rows[i];
      var sn = stageFromJobRow(row);
      if (!sn || sn < 1 || sn > 9) continue;
      var out = row.outcome || row.state || row.status || "";
      var stale = row.stale_flag === true || row.stale === true;
      if (String(out).toUpperCase() === "RUNNING" && stale) {
        out = "RUNNING";
      }
      var cls = heatClassForOutcome(out, stale);
      if (cls) heat[sn] = cls;
    }
    state.heat = heat;
    state.jukeboxNote = juke && juke.kind ? String(juke.kind) : "";
    var host = global.document && global.document.getElementById("studio-stage-rail");
    if (!host) return;
    var btns = host.querySelectorAll("[data-motif-n]");
    btns.forEach(function (btn) {
      var n = parseInt(btn.getAttribute("data-motif-n"), 10);
      btn.classList.remove(
        "studio-heat-hot",
        "studio-heat-warn",
        "studio-heat-clean",
        "studio-heat-stale"
      );
      if (heat[n]) btn.classList.add(heat[n]);
    });
  }

  function loadPack(kit) {
    var api = kitApi(kit);
    if (typeof api.get !== "function") return Promise.resolve(null);
    /* apiGet("/api/v1/studio") */
    return api.get("/api/v1/studio").then(function (p) {
      state.pack = p;
      return p;
    });
  }

  function refreshHeat(kit) {
    var api = kitApi(kit);
    if (typeof api.get !== "function") return Promise.resolve();
    /* apiGet("/api/v1/jukebox") */
    return api.get("/api/v1/jukebox").then(function (j) {
      paintHeatFromJukebox(j);
    });
  }

  function bodyForStage(stageId, host) {
    var st = STAGES.filter(function (s) { return s.id === stageId; })[0];
    if (!st) return {};
    if (st.id === "define") {
      var ta = host.querySelector('[name="define_text"]');
      return { define: { text: ta ? ta.value : "" } };
    }
    if (st.id === "implement") {
      var note = host.querySelector('[name="implement_note"]');
      return {
        implement: { note: note ? note.value : "" },
      };
    }
    if (st.id === "iterate") {
      var rounds = host.querySelector('[name="iterate_rounds"]');
      return {
        iterate: {
          max_rounds: rounds ? parseInt(rounds.value, 10) || 0 : 0,
        },
      };
    }
    if (st.id === "research") {
      return { research: { extra_urls: [] } };
    }
    return {};
  }

  /** POST config only. Does not start MOTIF and does not IMPLEMENT (CCr apply). */
  function saveStage(kit, stageId, host, statusEl) {
    var api = kitApi(kit);
    if (typeof api.post !== "function") return Promise.resolve();
    var body = bodyForStage(stageId, host);
    if (stageId === "implement") {
      body = bodyForStage("implement", host);
    }
    /* apiPost("/api/v1/studio") — config only */
    return api
      .post("/api/v1/studio", body)
      .then(function (rec) {
        state.pack = rec;
        if (statusEl) {
          statusEl.textContent = "SAVED (config only — MOTIF not started)";
        }
        return rec;
      })
      .catch(function (e) {
        if (statusEl) statusEl.textContent = "SAVE failed: " + (e.message || e);
      });
  }

  function renderStageRail(activeId) {
    return STAGES.map(function (s) {
      var active = s.id === activeId ? " studio-tab-active" : "";
      var heat = state.heat[s.n] ? " " + state.heat[s.n] : "";
      return (
        '<button type="button" class="studio-tab' + active + heat + '" data-stage="' +
        esc(s.id) +
        '" data-motif-n="' +
        s.n +
        '">' +
        s.n +
        " " +
        esc(s.name) +
        "</button>"
      );
    }).join("");
  }

  function renderPane(stageId) {
    var st = STAGES.filter(function (s) { return s.id === stageId; })[0] || STAGES[0];
    var pack = state.pack || {};
    if (st.id === "define") {
      var txt = (pack.define && pack.define.text) || "";
      return (
        '<div class="studio-pane" data-pane="' +
        esc(st.id) +
        '">' +
        '<label class="studio-field"><span>DEFINE (frozen prompt)</span>' +
        '<textarea name="define_text" rows="8">' +
        esc(txt) +
        "</textarea></label>" +
        '<p class="studio-hint">DEFINE→ITERATE pack. SAVE writes config only.</p>' +
        "</div>"
      );
    }
    if (st.id === "implement") {
      var imp = pack.implement || {};
      return (
        '<div class="studio-pane" data-pane="' +
        esc(st.id) +
        '">' +
        '<p class="studio-hint">IMPLEMENT is CCr apply once continuation is met. SAVE stores note only — never runs IMPLEMENT.</p>' +
        '<label class="studio-field"><span>Note</span>' +
        '<textarea name="implement_note" rows="4">' +
        esc(imp.note || "") +
        "</textarea></label>" +
        "</div>"
      );
    }
    if (st.id === "iterate") {
      var it = pack.iterate || {};
      return (
        '<div class="studio-pane" data-pane="' +
        esc(st.id) +
        '">' +
        '<label class="studio-field"><span>Max rounds</span>' +
        '<input name="iterate_rounds" type="number" min="0" max="99" value="' +
        esc(it.max_rounds != null ? it.max_rounds : 1) +
        '"></label>' +
        "</div>"
      );
    }
    return (
      '<div class="studio-pane" data-pane="' +
      esc(st.id) +
      '">' +
      '<p class="studio-hint">' +
      esc(st.name) +
      " setup is saved via POST /api/v1/studio. Heat comes from GET /api/v1/jukebox queue words (" +
      JUKEBOX_WORDS.join(" / ") +
      ") only.</p>" +
      "</div>"
    );
  }

  function render(host) {
    host.innerHTML =
      '<section class="studio-root" id="studio-root">' +
      '<div class="studio-heat-legend">Heat: GET /api/v1/jukebox — ' +
      esc(JUKEBOX_WORDS.join(" · ")) +
      (state.jukeboxNote ? " · " + esc(state.jukeboxNote) : "") +
      "</div>" +
      '<nav class="studio-stage-rail" id="studio-stage-rail">' +
      renderStageRail(state.activeId) +
      "</nav>" +
      '<div class="studio-body" id="studio-body">' +
      renderPane(state.activeId) +
      "</div>" +
      '<div class="studio-actions">' +
      '<button type="button" class="studio-save" data-action="save">SAVE</button>' +
      '<span class="studio-status" id="studio-status"></span>' +
      "</div>" +
      "</section>";
  }

  function wire(host, kit) {
    var rail = host.querySelector("#studio-stage-rail");
    var statusEl = host.querySelector("#studio-status");
    if (rail) {
      rail.addEventListener("click", function (ev) {
        var btn = ev.target.closest("[data-stage]");
        if (!btn) return;
        state.activeId = btn.getAttribute("data-stage");
        render(host);
        wire(host, kit);
        paintHeatFromJukebox({ jobs: [] });
        refreshHeat(kit);
      });
    }
    var saveBtn = host.querySelector('[data-action="save"]');
    if (saveBtn) {
      saveBtn.addEventListener("click", function () {
        saveStage(kit, state.activeId, host, statusEl);
      });
    }
  }

  function mount(host, kit) {
    if (!host) return Promise.resolve();
    kit = kit || (global.cdeckHeader && global.cdeckHeader.kitForTab("studio"));
    render(host);
    wire(host, kit);
    return loadPack(kit).then(function () {
      render(host);
      wire(host, kit);
      return refreshHeat(kit);
    });
  }

  global.DeckStudio = {
    STAGES: STAGES,
    JUKEBOX_WORDS: JUKEBOX_WORDS,
    mount: mount,
    loadPack: loadPack,
    saveStage: saveStage,
    refreshHeat: refreshHeat,
    paintHeatFromJukebox: paintHeatFromJukebox,
  };
})(typeof globalThis !== "undefined" ? globalThis : this);
