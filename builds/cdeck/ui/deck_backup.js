(function () {
  "use strict";
  /* B7-013 Backup tab — test / generate / scheduler / search / profiles / restore.
     GET /api/v1/backup — fold only; GET never runs a backup. */

  function $(id) {
    return document.getElementById(id);
  }

  function esc(s) {
    if (s == null) return "";
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/"/g, "&quot;");
  }

  function apiGet(path) {
    if (typeof window.apiGet !== "function") {
      return Promise.reject(new Error("apiGet unavailable"));
    }
    return window.apiGet(path);
  }

  function apiPost(path, body) {
    if (typeof window.apiPost !== "function") {
      return Promise.reject(new Error("apiPost unavailable"));
    }
    return window.apiPost(path, body);
  }

  function say(el, txt) {
    if (el) el.textContent = txt;
  }

  function paintScheduler(host, fold) {
    var hours = (fold && fold.hours) || [7, 11, 19, 23];
    var hb = fold && fold.heartbeat;
    var h =
      '<section class="backup-panel-scheduler" id="backup-panel-scheduler">' +
      '<h3>Scheduler</h3>' +
      '<p class="dim tiny">COSMOS Backup hours (GET fold — does not run a backup).</p>' +
      '<div class="chip-row">';
    hours.forEach(function (hr) {
      h += '<span class="chip">' + esc(String(hr).padStart(2, "0")) + ":00</span>";
    });
    h += "</div>";
    if (hb) {
      h +=
        '<pre class="dim tiny">' +
        esc(JSON.stringify(hb, null, 2)) +
        "</pre>";
    } else {
      h += '<p class="dim tiny">heartbeat: NO_SOURCE</p>';
    }
    h += "</section>";
    host.insertAdjacentHTML("beforeend", h);
  }

  function paintProfileDestChips(host, fold) {
    var profiles = (fold && fold.profiles) || [];
    var h =
      '<section class="backup-panel-profiles" id="backup-panel-profiles">' +
      '<h3>Profiles</h3>' +
      '<p class="dim tiny">Per-profile IMPLEMENT dest chips (from GET /api/v1/backup fold).</p>' +
      '<div class="chip-row profile-backup-dest-list">';
    profiles.forEach(function (p) {
      var dest = (p && p.dest) || {};
      var label =
        (dest.kind || "unset") +
        (dest.path ? " · " + dest.path : "");
      h +=
        '<button type="button" class="chip profile-backup-dest-chip" ' +
        'data-profile-id="' +
        esc(p.id || "") +
        '" title="' +
        esc(label) +
        '">' +
        esc(p.label || p.id || "?") +
        " · " +
        esc(label) +
        "</button>";
    });
    if (!profiles.length) {
      h += '<span class="dim tiny">no profiles in fold</span>';
    }
    h += "</div></section>";
    host.insertAdjacentHTML("beforeend", h);
  }

  function paintPanels(host) {
    host.innerHTML =
      '<div class="panel-hd"><h2>Backup</h2>' +
      '<span class="dim tiny">GET never runs a backup · POST suite verbs only</span></div>' +
      '<div class="panel-bd backup-panel-root">' +
      '<section class="backup-panel-test" id="backup-panel-test">' +
      '<h3>Test</h3>' +
      '<p class="dim tiny">POST surface_test (measure_all) — qualifies surfaces, not a backup run.</p>' +
      '<button type="button" id="backup-btn-surface-test">Run surface test</button>' +
      "</section>" +
      '<section class="backup-panel-search" id="backup-panel-search">' +
      '<h3>Search</h3>' +
      '<p class="dim tiny">POST search — dest candidates from Core surfaces.</p>' +
      '<button type="button" id="backup-btn-search">Search dest candidates</button>' +
      "</section>" +
      '<section class="backup-panel-generate" id="backup-panel-generate">' +
      '<h3>Generate</h3>' +
      '<p class="dim tiny">POST generate refuses without explicit dest.</p>' +
      '<label>dest <input id="backup-generate-dest" type="text" placeholder="surface id" /></label>' +
      '<button type="button" id="backup-btn-generate">Generate (POST)</button>' +
      "</section>" +
      '<section class="backup-panel-restore" id="backup-panel-restore">' +
      '<h3>Restore</h3>' +
      '<p class="dim tiny">POST restore refuses without verified bak name.</p>' +
      '<label>bak <input id="backup-restore-bak" type="text" placeholder="verified set name" /></label>' +
      '<button type="button" id="backup-btn-restore">Restore (POST)</button>' +
      "</section>" +
      '<div id="backup-scheduler-slot"></div>' +
      '<div id="backup-profiles-slot"></div>' +
      '<pre class="backup-say dim tiny" id="backup-say" aria-live="polite"></pre>' +
      "</div>";

    var schedSlot = host.querySelector("#backup-scheduler-slot");
    var profSlot = host.querySelector("#backup-profiles-slot");
    var sayEl = host.querySelector("#backup-say");

    host.querySelector("#backup-btn-surface-test").addEventListener("click", function () {
      say(sayEl, 'POST /api/v1/backup action=surface_test measure_all …');
      apiPost("/api/v1/backup", { action: "surface_test", measure_all: true })
        .then(function (rec) {
          say(sayEl, JSON.stringify(rec, null, 2));
        })
        .catch(function (e) {
          say(sayEl, String((e && e.message) || e));
        });
    });

    host.querySelector("#backup-btn-search").addEventListener("click", function () {
      say(sayEl, 'POST /api/v1/backup action=search …');
      apiPost("/api/v1/backup", { action: "search" })
        .then(function (rec) {
          say(sayEl, JSON.stringify(rec, null, 2));
        })
        .catch(function (e) {
          say(sayEl, String((e && e.message) || e));
        });
    });

    host.querySelector("#backup-btn-generate").addEventListener("click", function () {
      var destEl = host.querySelector("#backup-generate-dest");
      var dest = destEl ? destEl.value.trim() : "";
      say(sayEl, 'POST /api/v1/backup action=generate dest=' + (dest || "(missing)"));
      apiPost("/api/v1/backup", { action: "generate", dest: dest })
        .then(function (rec) {
          say(sayEl, JSON.stringify(rec, null, 2));
        })
        .catch(function (e) {
          say(sayEl, String((e && e.message) || e));
        });
    });

    host.querySelector("#backup-btn-restore").addEventListener("click", function () {
      var bakEl = host.querySelector("#backup-restore-bak");
      var bak = bakEl ? bakEl.value.trim() : "";
      say(sayEl, 'POST /api/v1/backup action=restore bak=' + (bak || "(missing)"));
      apiPost("/api/v1/backup", { action: "restore", bak: bak })
        .then(function (rec) {
          say(sayEl, JSON.stringify(rec, null, 2));
        })
        .catch(function (e) {
          say(sayEl, String((e && e.message) || e));
        });
    });

    return { schedSlot: schedSlot, profSlot: profSlot, sayEl: sayEl };
  }

  function refreshFold(slots) {
    if (!slots) return;
    say(slots.sayEl, 'GET /api/v1/backup …');
    apiGet("/api/v1/backup")
      .then(function (fold) {
        if (slots.schedSlot) {
          slots.schedSlot.innerHTML = "";
          paintScheduler(slots.schedSlot, fold);
        }
        if (slots.profSlot) {
          slots.profSlot.innerHTML = "";
          paintProfileDestChips(slots.profSlot, fold);
        }
        say(
          slots.sayEl,
          "GET fold kind=" +
            (fold && fold.kind) +
            " — GET never runs a backup."
        );
      })
      .catch(function (e) {
        say(slots.sayEl, String((e && e.message) || e));
      });
  }

  function boot() {
    var host = $("panel-backup");
    if (!host || host.dataset.backupBoot === "1") return;
    host.dataset.backupBoot = "1";
    var slots = paintPanels(host);
    refreshFold(slots);
    document.addEventListener("cdeck:refresh", function () {
      refreshFold(slots);
    });
  }

  document.addEventListener("cdeck:tab-selected", function (ev) {
    if (ev && ev.detail && ev.detail.tab === "backup") boot();
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }

  window.cdeckBackupBoot = boot;
})();
