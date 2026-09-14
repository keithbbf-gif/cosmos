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
  function $(id) { return document.getElementById(id); }
  function esc(s) {
    if (s == null) return "";
    return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/"/g, "&quot;");
  }
  function api(url, opts) {
    if (typeof window.api === "function") return window.api(url, opts);
    return Promise.reject(new Error("api unavailable"));
  }
  function takeStack(f) {
    var m = String(f || "").match(/^\[stack:([^\]]+)\]\s*/);
    return m ? { stack: m[1], text: String(f).slice(m[0].length) } : { stack: "", text: String(f || "") };
  }
  function bindProfileSkin(box, pid) {
    var wrap = box.querySelector('[data-stub="profile-skin"]');
    if (!wrap) return;
    var sel = wrap.querySelector("select.profile-skin-stub");
    if (!sel) return;
    var key = "cdeck.profileSkin." + pid;
    var saved = "default";
    try { saved = localStorage.getItem(key) || "default"; } catch (e) {}
    if (!PROFILE_SKINS[saved]) saved = "default";
    sel.value = saved;
    applyProfileSkin(box, pid);
  }
  function applyProfileSkin(box, pid) {
    var wrap = box.querySelector('[data-stub="profile-skin"]');
    if (!wrap) return;
    var sel = wrap.querySelector("select.profile-skin-stub");
    var id = (sel && sel.value) || "default";
    if (!PROFILE_SKINS[id]) id = "default";
    var key = "cdeck.profileSkin." + pid;
    try { localStorage.setItem(key, id); } catch (e2) {}
    box.setAttribute("data-profile-skin", id);
    var gfx = wrap.querySelector(".profile-skin-graphic");
    if (gfx) gfx.setAttribute("data-skin", id);
  }
  var SKIN_ORDER = Object.keys(PROFILE_SKINS);
  var ROLE_HINT = {};
  var PROFILE_SEATS = {};
  var WEBSITE_STACK = [];

    function paintProfilePage(pid, rec) {
      var box = $("pfPage-" + pid);
      if (!box) return;
      rec = rec || {};
      var en = rec.engine || {};
      var stages = rec.stages || [];
      var setup = en.step_setup || {};
      var dests = rec.dest_catalog || [];
      var seats = PROFILE_SEATS[pid] || [];
      var savedStack = pid === "website"
        ? takeStack(((setup.improve) || {}).files || "").stack : "";
      var h = '<div class="panel-hd"><h2>' + esc(rec.label || pid) +
        "</h2><span class=\"dim tiny\">MOTIF setup · SAVE does not start MOTIF</span></div>";
      var skinOpts = "";
      Object.keys(PROFILE_SKINS).forEach(function (id) {
        skinOpts += '<option value="' + esc(id) + '">' + esc(id) + "</option>";
      });
      h += '<div class="profile-skin-stub" data-stub="profile-skin" data-profile="' +
        esc(pid) + '"><label class="dim tiny">Skin — default graphic + colors per Profile' +
        '<select class="profile-skin-stub" aria-label="Profile skin">' + skinOpts +
        "</select></label>" +
        '<div class="profile-skin-graphic" aria-hidden="true"></div></div>';
      h += '<div class="panel-bd">';
      h += '<div class="pf-motif-top pf-page-motif">';
      h += '<div class="pf-motif-h">MOTIF sequence</div><div class="pf-pipe" role="list">';
      stages.forEach(function (s, i) {
        if (i) h += '<span class="pf-arrow">→</span>';
        h += '<span class="pf-node" role="listitem"><b>' + s.n + "</b> " +
          esc(s.name) + "</span>";
      });
      h += "</div></div>";
      h += '<p class="dim tiny">Each MOTIF step is its own section: data folders, files, prompt, and who fills the seats. ' +
        esc(ROLE_HINT[pid] || "") + "</p>";
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
          var on = savedStack && savedStack === card.id ? " on" : "";
          h += '<div class="set-card pf-seat-card' + on + '" role="listitem" data-stack="' +
            esc(card.id) + '"><h3>' + esc(card.label) + "</h3>" +
            '<p class="dim tiny">' + esc(card.hint || "") + "</p></div>";
        });
        h += "</div>";
        h += '<p class="dim tiny">Own-your-stack: MochaHost cPanel + NameCheap/CloudFlare + OceanWP Pro + GeneratePress Pro. ~60 .coms is a named count, not a fabricated list. 10Web-like WordPress dest. Durable: DEFINE → RESEARCH. v0: staged, you own it. This TUI does not publish.</p>';
        h += '<div class="formrow"><button type="button" class="studio-go pf-jump-rc">' +
          "Studio research_call · DEFINE brief</button></div>";
      }
      if (pid === "ups" || pid === "crucible" || pid === "diligence"
          || pid === "docket" || pid === "differentiator") {
        h += '<div class="formrow"><button type="button" class="studio-go pf-jump-rc">' +
          "Studio research_call · FILE / INGEST</button></div>";
        var jumpNote = "Not a second Core. ";
        if (pid === "ups") {
          jumpNote += "UPS-JUDGE is NAMED until Physics Profile. ";
        } else if (pid === "crucible" || pid === "docket") {
          jumpNote += "Legal invoke LEGAL_OMITTED. Not USPTO. This TUI does not click USPTO. ";
        } else if (pid === "differentiator") {
          jumpNote += "Anonymize is a gate — no PHI. ";
        } else {
          jumpNote += "Deal diligence ingest via research_call FILE/INGEST. ";
        }
        h += '<p class="dim tiny">MOTIF RESEARCH ingest is GET/POST /api/v1/research_call on Core :8770. ' +
          jumpNote +
          "Crucible and UPS are both occupancy, not one-or-the-other.</p>";
      }
      if (pid === "crucible") {
        h += '<section class="pf-step pf-cru-round" id="pfCruRound">';
        h += "<h3>RUN CRUCIBLE ROUND</h3>";
        h += '<p class="dim tiny">POST /api/v1/crucible — composed critics on Core. Empty critics = the attached pool. Sources are docs-role names only (not V:\\\\, not Legal). 501 CRUCIBLE_NOT_RUNNABLE if none attached. Not occupancy POST. Not USPTO.</p>';
        h += '<label class="dim tiny">sources (one docs name per line)<textarea id="pfCruSources" rows="3" spellcheck="false">FINAL_ARCHITECTURE.md</textarea></label>';
        h += '<div class="mr-chiprow" id="pfCruDocChips">';
        ["FINAL_ARCHITECTURE.md", "COSMOS_PIPELINE.md", "CCR.md", "MOTIF.md",
         "AGENT_BOUNDARIES.md"].forEach(function (n, i) {
          h += '<button type="button" class="chip' + (i === 0 ? " on" : "") +
            '" data-doc="' + esc(n) + '">' + esc(n) + "</button>";
        });
        h += "</div>";
        h += '<button type="button" class="studio-go" id="pfCruRun">RUN ROUND</button>';
        h += '<button type="button" class="studio-go" id="pfCruRuns">open RUNS</button>';
        h += '<div class="tiny" id="pfCruRunSay"></div>';
        h += '<pre class="tiny" id="pfCruRunLog"></pre>';
        h += "</section>";
      }
      stages.forEach(function (s) {
        var st = setup[s.id] || {};
        h += '<section class="pf-step" data-step="' + esc(s.id) + '">';
        h += "<h3>" + s.n + " · " + esc(s.name) + "</h3>";
        h += '<p class="dim tiny">' + esc(s.hint || "") + "</p>";
        if (s.id === "define") {
          h += '<label class="dim tiny">PROBLEM STATEMENT / STATED GOAL<textarea class="pf-page-define" rows="8" spellcheck="false">' +
            esc((en.define && en.define.text) || "") + "</textarea></label>";
        }
        if (s.id === "research" && (pid === "ups" || pid === "crucible"
            || pid === "diligence" || pid === "docket"
            || pid === "differentiator")) {
          h += '<div class="formrow"><button type="button" class="studio-go pf-jump-rc">' +
            "jump · Studio research_call FILE / INGEST</button></div>";
        }
        h += '<label class="dim tiny">prompt instructions<textarea class="pf-page-prompt" rows="4" spellcheck="false">' +
          esc(st.prompt || (en.stages && en.stages[s.id]) || "") + "</textarea></label>";
        h += '<label class="dim tiny">data folders (path)<input class="pf-page-folders" type="text" spellcheck="false" value="' +
          esc(st.folders || "") + '"></label>';
        var filesShow = st.files || "";
        if (pid === "website" && s.id === "improve") filesShow = takeStack(filesShow).text;
        h += '<label class="dim tiny">files (names; upload lists names only — no blob store)<input class="pf-page-files" type="text" spellcheck="false" value="' +
          esc(filesShow) + '"><input class="pf-page-upload" type="file" multiple></label>';
        h += '<label class="dim tiny">agent roles / who fills them<textarea class="pf-page-roles" rows="3" spellcheck="false" placeholder="' +
          esc(ROLE_HINT[pid] || "named seats") + '">' +
          esc(st.roles || "") + "</textarea></label>";
        if (s.id === "improve") {
          h += '<div class="studio-targets pf-page-dest">';
          dests.forEach(function (d) {
            var kind = (en.dest && en.dest.kind) || "staged";
            var on = kind === d.id;
            var lab = d.label || d.id;
            if (d.id === "staged") lab += " · READY";
            if (d.id === "publish") lab += " · REFUSED this TUI";
            h += '<label><input type="radio" name="pfPageDest-' + esc(pid) + '" value="' +
              esc(d.id) + '"' + (on ? " checked" : "") +
              (d.id === "publish" ? " data-publish-refuse=\"1\"" : "") +
              "> " + esc(lab) + "</label>";
          });
          h += "</div>";
          h += '<label class="dim tiny">dest path<textarea class="pf-page-destpath" rows="2">' +
            esc((en.dest && en.dest.path) || "") + "</textarea></label>";
        }
        h += "</section>";
      });
      h += '<div class="formrow"><button type="button" class="studio-go pf-page-save">SAVE SETUP</button></div>';
      h += '<div class="tiny pf-page-say"></div>';
      h += "</div>";
      box.innerHTML = h;
      bindProfileSkin(box, pid);
      var pfSkinSel = box.querySelector('[data-stub="profile-skin"] select.profile-skin-stub');
      if (pfSkinSel) {
        pfSkinSel.addEventListener("change", function () {
          applyProfileSkin(box, pid);
        });
      }
      var up = box.querySelectorAll(".pf-page-upload");
      up.forEach(function (inp) {
        inp.addEventListener("change", function () {
          var names = [];
          var i;
          for (i = 0; i < (inp.files || []).length; i++) names.push(inp.files[i].name);
          var dest = inp.parentNode && inp.parentNode.querySelector(".pf-page-files");
          if (dest) dest.value = names.join("\n");
        });
      });
      box.querySelectorAll(".pf-seat-card").forEach(function (card) {
        card.addEventListener("click", function () {
          var stack = card.getAttribute("data-stack") || "";
          var sid = card.getAttribute("data-seat") || "";
          if (stack) {
            box.querySelectorAll("[data-stack]").forEach(function (c) {
              c.classList.toggle("on", c === card);
            });
            return;
          }
          var lab = (card.querySelector("h3") && card.querySelector("h3").textContent) || sid;
          var roles = box.querySelector(".pf-step[data-step=\"research\"] .pf-page-roles") ||
            box.querySelector(".pf-page-roles");
          if (roles) {
            var cur = String(roles.value || "").trim();
            if (cur.indexOf(lab) < 0) {
              roles.value = cur ? (cur + "\n" + lab) : lab;
            }
          }
          box.querySelectorAll("[data-seat]").forEach(function (c) {
            c.classList.toggle("on", c === card);
          });
          if (pid === "crucible" && typeof window.openModelRater === "function") {
            window.openModelRater();
          }
        });
      });
      box.querySelectorAll(".pf-jump-rc").forEach(function (b) {
        b.addEventListener("click", function () {
          if (typeof window.openStudioResearchCall === "function") {
            window.openStudioResearchCall();
          }
        });
      });
      var runsBtn = box.querySelector("#pfCruRuns");
      if (runsBtn) {
        runsBtn.addEventListener("click", function () {
          if (window.showDeckTab) window.showDeckTab("runs");
        });
      }
      var runBtn = box.querySelector("#pfCruRun");
      if (runBtn) {
        runBtn.addEventListener("click", function () {
          var say = box.querySelector("#pfCruRunSay");
          var log = box.querySelector("#pfCruRunLog");
          var raw = ((box.querySelector("#pfCruSources") || {}).value || "").split(/\n/);
          var sources = raw.map(function (s) { return String(s || "").trim(); }).filter(Boolean);
          box.querySelectorAll("#pfCruDocChips [data-doc].on").forEach(function (c) {
            var n = c.getAttribute("data-doc") || "";
            if (n && sources.indexOf(n) < 0) sources.push(n);
          });
          var bad = sources.filter(function (s) {
            var l = s.toLowerCase();
            return l.indexOf("legal") >= 0 || l.indexOf(":\\") >= 0
              || s.charAt(0) === "/" || s.indexOf("..") >= 0;
          });
          if (bad.length) {
            if (say) say.textContent = "LEGAL_OMITTED / IDENTITY_MISMATCH — docs-role names only";
            return;
          }
          if (!sources.length) sources = ["FINAL_ARCHITECTURE.md"];
          if (say) say.textContent = "POST /api/v1/crucible …";
          api("/api/v1/crucible", {
            method: "POST",
            body: { sources: sources, priority: "high" }
          }).then(function (rec) {
            if (say) {
              say.textContent = rec && rec.job_id
                ? ("201 job " + rec.job_id + " · " + (rec.outcome || rec.error || "queued"))
                : String((rec && (rec.error || rec.detail)) || "returned");
            }
            if (log) log.textContent = JSON.stringify({
              job_id: rec && rec.job_id,
              outcome: rec && rec.outcome,
              error: rec && rec.error,
              detail: rec && rec.detail
            }, null, 2);
          }).catch(function (e) {
            if (say) say.textContent = String((e && e.message) || e);
          });
        });
      }
      var saveBtn = box.querySelector(".pf-page-save");
      if (saveBtn) saveBtn.addEventListener("click", function () {
        harvestPage(box, pid, rec);
        var en = rec.engine || {};
        var sayEl = box.querySelector(".pf-page-say");
        api("/api/v1/profiles", {
          method: "POST",
          body: {
            profile: pid,
            define: { text: (en.define && en.define.text) || "" },
            stages: en.stages || {},
            dest: en.dest || {},
            step_setup: en.step_setup || {}
          }
        }).then(function (out) {
          if (out && out.error) {
            if (sayEl) sayEl.textContent = String(out.error || out.detail || "refused");
            return;
          }
          paintProfilePage(pid, out);
          if (box.querySelector(".pf-page-say")) {
            box.querySelector(".pf-page-say").textContent =
              "skin saved. Does not start MOTIF. Does not publish.";
          }
        }).catch(function (e) {
          if (sayEl) sayEl.textContent = String((e && e.message) || e);
        });
      });
    }

  function harvestPage() {}
})();
