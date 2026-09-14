(function () {
  "use strict";

  var PROFILE_SKINS = {
    default: {},
    forge: {},
    crucible: {},
    diligence: {},
    docket: {},
    ups: {},
    differentiator: {},
    website: {}
  };

  var PROFILE_ORDER = [
    "forge", "crucible", "diligence", "docket", "ups", "differentiator", "website"
  ];

  var SKIN_WALLPAPERS = {
    forge: "skins/forge-engineroom.jpg",
    crucible: "skins/crucible-chamber.jpg",
    diligence: "skins/diligence-dealroom.jpg",
    docket: "skins/docket-archive.jpg",
    ups: "skins/ups-lab.jpg",
    differentiator: "skins/differentiator-clinic.jpg",
    website: "skins/website-studio.jpg"
  };

  function $(id) { return document.getElementById(id); }

  function esc(s) {
    if (s == null) return "";
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function apiGet(path) {
    if (window.cdeckHeader && window.cdeckHeader.apiGet) {
      return window.cdeckHeader.apiGet(path);
    }
    if (typeof window.apiGet === "function") return window.apiGet(path);
    return Promise.reject(new Error("apiGet unavailable"));
  }

  function apiPost(path, body) {
    if (window.cdeckHeader && window.cdeckHeader.apiPost) {
      return window.cdeckHeader.apiPost(path, body);
    }
    if (typeof window.apiPost === "function") return window.apiPost(path, body);
    return Promise.reject(new Error("apiPost unavailable"));
  }

  function api(url, opts) {
    if (opts && (opts.method === "POST" || opts.method === "post")) {
      return apiPost(url, opts.body);
    }
    return apiGet(url);
  }

  function bindProfileSkin(box, pid) {
    var wrap = box.querySelector('[data-stub="profile-skin"]');
    if (!wrap) return;
    var sel = wrap.querySelector("select.profile-skin-stub");
    if (!sel) return;
    var key = "cdeck.profileSkin." + pid;
    var saved = "default";
    try { saved = localStorage.getItem(key) || "default"; } catch (_) {}
    if (!Object.prototype.hasOwnProperty.call(PROFILE_SKINS, saved)) saved = "default";
    sel.value = saved;
    applyProfileSkin(box, pid);
  }

  function applyProfileSkin(box, pid) {
    var wrap = box.querySelector('[data-stub="profile-skin"]');
    if (!wrap) return;
    var sel = wrap.querySelector("select.profile-skin-stub");
    var id = (sel && sel.value) || "default";
    if (!Object.prototype.hasOwnProperty.call(PROFILE_SKINS, id)) id = "default";
    var key = "cdeck.profileSkin." + pid;
    try { localStorage.setItem(key, id); } catch (_) {}
    box.setAttribute("data-profile-skin", id);
    var gfx = wrap.querySelector(".profile-skin-graphic");
    if (gfx) {
      gfx.setAttribute("data-skin", id);
      var wp = SKIN_WALLPAPERS[id] || SKIN_WALLPAPERS[pid] || "";
      if (wp) gfx.style.backgroundImage = "url('" + wp + "')";
    }
  }

  function skinSelectHTML(pid) {
    var opts = "";
    Object.keys(PROFILE_SKINS).forEach(function (k) {
      opts += '<option value="' + esc(k) + '">' + esc(k) + "</option>";
    });
    return (
      '<div class="profile-skin-stub" data-stub="profile-skin" data-profile="' + esc(pid) + '">' +
        '<label class="dim tiny">Skin — default graphic + colors per Profile' +
          '<select class="profile-skin-stub" aria-label="Profile skin">' +
            opts +
          "</select>" +
        "</label>" +
        '<div class="profile-skin-graphic" aria-hidden="true"></div>' +
      "</div>"
    );
  }

  var ROLE_HINT = {};
  var PROFILE_SEATS = {};
  var WEBSITE_STACK = [];

  function takeStack(f) {
    var m = String(f || "").match(/^\[stack:([^\]]+)\]\s*/);
    return m
      ? { stack: m[1], text: String(f).slice(m[0].length) }
      : { stack: "", text: String(f || "") };
  }

  function harvestPage(box, pid, rec) {
    rec = rec || { engine: {} };
    if (!rec.engine) rec.engine = {};
    var en = rec.engine;
    if (!en.define) en.define = {};
    if (!en.step_setup) en.step_setup = {};
    if (!en.stages) en.stages = {};
    if (!en.dest) en.dest = { kind: "staged", path: "" };

    var defTa = box.querySelector(".pf-page-define");
    if (defTa) en.define.text = defTa.value;

    box.querySelectorAll(".pf-step[data-step]").forEach(function (sec) {
      var sid = sec.getAttribute("data-step") || "";
      if (!sid) return;
      var st = en.step_setup[sid] || {};
      var pr = sec.querySelector(".pf-page-prompt");
      var fo = sec.querySelector(".pf-page-folders");
      var fi = sec.querySelector(".pf-page-files");
      var ro = sec.querySelector(".pf-page-roles");
      if (pr) st.prompt = pr.value;
      if (fo) st.folders = fo.value;
      if (fi) st.files = fi.value;
      if (ro) st.roles = ro.value;
      en.step_setup[sid] = st;
      var note = sec.querySelector(".pf-page-prompt");
      if (note) en.stages[sid] = note.value;
    });

    var destRadio = box.querySelector('input[name="pfPageDest-' + pid + '"]:checked');
    if (destRadio) en.dest.kind = destRadio.value;
    var destPath = box.querySelector(".pf-page-destpath");
    if (destPath) en.dest.path = destPath.value;
    return rec;
  }

  function paintProfilePage(pid, rec) {
    var box = $("pfPage-" + pid);
    if (!box) return;
    rec = rec || {};
    var en = rec.engine || {};
    var stages = rec.stages || [];
    var setup = en.step_setup || {};
    var dests = rec.dest_catalog || [];
    var seats = PROFILE_SEATS[pid] || [];

    var savedStack = "";
    if (pid === "website") {
      savedStack = takeStack(((setup.improve) || {}).files || "").stack;
    }

    var h =
      '<div class="panel-hd">' +
        "<h2>" + esc(rec.label || pid) + "</h2>" +
        '<span class="dim tiny">MOTIF setup · SAVE does not start MOTIF</span>' +
      "</div>";

    h += skinSelectHTML(pid);

    h += '<div class="panel-bd">';
    h += '<div class="pf-motif-top pf-page-motif pf-schematic" data-schematic="profiles-get">';
    h += '<div class="pf-motif-h">MOTIF sequence (from GET /api/v1/profiles)</div>';
    h += '<div class="pf-pipe" role="list">';
    stages.forEach(function (s, i) {
      if (i) h += '<span class="pf-arrow">→</span>';
      h += '<span class="pf-node" role="listitem"><b>' + s.n + "</b> " + esc(s.name) + "</span>";
    });
    h += "</div></div>";

    h += '<p class="dim tiny">Each MOTIF step is its own section: data folders, files, prompt, ' +
      "and who fills the seats. " + esc(ROLE_HINT[pid] || "") + "</p>";

    if (seats.length) {
      h += '<div class="set-cards pf-seat-cards" role="list">';
      seats.forEach(function (seat) {
        h += '<div class="set-card pf-seat-card" role="listitem" data-seat="' +
          esc(seat.id) + '"><h3>' + esc(seat.label) + "</h3>" +
          '<p class="dim tiny">' + esc(seat.hint || "") + "</p></div>";
      });
      h += "</div>";
    }

    if (pid === "website") {
      h += '<div class="set-cards pf-seat-cards" role="list">';
      WEBSITE_STACK.forEach(function (card) {
        var on = (savedStack && savedStack === card.id) ? " on" : "";
        h += '<div class="set-card pf-seat-card' + on + '" role="listitem" data-stack="' +
          esc(card.id) + '"><h3>' + esc(card.label) + "</h3>" +
          '<p class="dim tiny">' + esc(card.hint || "") + "</p></div>";
      });
      h += "</div>";
    }

    stages.forEach(function (s) {
      var st = setup[s.id] || {};
      h += '<section class="pf-step" data-step="' + esc(s.id) + '">';
      h += "<h3>" + s.n + " · " + esc(s.name) + "</h3>";
      h += '<p class="dim tiny">' + esc(s.hint || "") + "</p>";

      if (s.id === "define") {
        h += '<label class="dim tiny">PROBLEM STATEMENT / STATED GOAL' +
          '<textarea class="pf-page-define" rows="8" spellcheck="false">' +
          esc((en.define && en.define.text) || "") + "</textarea></label>";
      }

      h += '<label class="dim tiny">prompt instructions' +
        '<textarea class="pf-page-prompt" rows="4" spellcheck="false">' +
        esc(st.prompt || (en.stages && en.stages[s.id]) || "") + "</textarea></label>";

      h += '<label class="dim tiny">data folders (path)' +
        '<input class="pf-page-folders" type="text" spellcheck="false" value="' +
        esc(st.folders || "") + '"></label>';

      var filesShow = st.files || "";
      if (pid === "website" && s.id === "improve") filesShow = takeStack(filesShow).text;
      h += '<label class="dim tiny">files' +
        '<input class="pf-page-files" type="text" spellcheck="false" value="' +
        esc(filesShow) + '"></label>';

      h += '<label class="dim tiny">agent roles / who fills them' +
        '<textarea class="pf-page-roles" rows="3" spellcheck="false">' +
        esc(st.roles || "") + "</textarea></label>";

      if (s.id === "improve") {
        h += '<div class="studio-targets pf-page-dest">';
        dests.forEach(function (d) {
          var kind = (en.dest && en.dest.kind) || "staged";
          var on = kind === d.id;
          h += '<label><input type="radio" name="pfPageDest-' + esc(pid) +
            '" value="' + esc(d.id) + '"' + (on ? " checked" : "") +
            "> " + esc(d.label || d.id) + "</label>";
        });
        h += "</div>";
        h += '<label class="dim tiny">dest path' +
          '<textarea class="pf-page-destpath" rows="2">' +
          esc((en.dest && en.dest.path) || "") + "</textarea></label>";
      }

      h += "</section>";
    });

    h += '<div class="formrow"><button type="button" class="studio-go pf-page-save">SAVE SETUP</button></div>';
    h += '<div class="tiny pf-page-say"></div>';
    h += "</div>";

    box.innerHTML = h;
    box.hidden = false;

    bindProfileSkin(box, pid);
    var skinSel = box.querySelector('[data-stub="profile-skin"] select.profile-skin-stub');
    if (skinSel) {
      skinSel.addEventListener("change", function () { applyProfileSkin(box, pid); });
    }

    var saveBtn = box.querySelector(".pf-page-save");
    if (saveBtn) {
      saveBtn.addEventListener("click", function () {
        var working = harvestPage(box, pid, { engine: JSON.parse(JSON.stringify(en)) });
        var payload = working.engine || {};
        var sayEl = box.querySelector(".pf-page-say");
        apiPost("/api/v1/profiles", {
          profile: pid,
          define: payload.define || { text: "" },
          stages: payload.stages || {},
          dest: payload.dest || {},
          step_setup: payload.step_setup || {}
        }).then(function (out) {
          if (out && out.error) {
            if (sayEl) sayEl.textContent = String(out.error || out.detail || "refused");
            return;
          }
          paintProfilePage(pid, out);
          var s2 = box.querySelector(".pf-page-say");
          if (s2) {
            s2.textContent = "skin saved. Does not start MOTIF. Does not publish.";
          }
        }).catch(function (e) {
          if (sayEl) sayEl.textContent = String((e && e.message) || e);
        });
      });
    }
  }

  function hideAllProfilePages() {
    PROFILE_ORDER.forEach(function (pid) {
      var el = $("pfPage-" + pid);
      if (el) el.hidden = true;
    });
    var hub = $("pfProfilesHub");
    if (hub) hub.hidden = true;
  }

  function ensureProfilePage(pid) {
    if (PROFILE_ORDER.indexOf(pid) < 0) return Promise.resolve();
    hideAllProfilePages();
    var box = $("pfPage-" + pid);
    if (box) box.hidden = false;
    return apiGet("/api/v1/profiles?profile=" + encodeURIComponent(pid)).then(function (rec) {
      paintProfilePage(pid, rec);
      return rec;
    }).catch(function (e) {
      if (box) {
        box.innerHTML = '<p class="dim tiny">profiles GET failed: ' + esc(e.message || e) + "</p>";
        box.hidden = false;
      }
    });
  }

  function showProfilesHub() {
    hideAllProfilePages();
    var hub = $("pfProfilesHub");
    if (hub) hub.hidden = false;
    return Promise.all(PROFILE_ORDER.map(function (pid) {
      return apiGet("/api/v1/profiles?profile=" + encodeURIComponent(pid)).then(function (rec) {
        paintProfilePage(pid, rec);
        var el = $("pfPage-" + pid);
        if (el) el.hidden = true;
      });
    })).then(function () {
      if (hub) hub.hidden = false;
    });
  }

  function onDeckTab(tab) {
    if (tab === "profiles") {
      showProfilesHub();
      return;
    }
    if (PROFILE_ORDER.indexOf(tab) >= 0) {
      ensureProfilePage(tab);
    }
  }

  window.paintProfilePage = paintProfilePage;
  window.applyProfileSkin = applyProfileSkin;
  window.bindProfileSkin = bindProfileSkin;
  window.PROFILE_SKINS = PROFILE_SKINS;
  window.PROFILE_ORDER = PROFILE_ORDER;
  window.ensureProfilePage = ensureProfilePage;
  window.onProfilesDeckTab = onDeckTab;
})();
