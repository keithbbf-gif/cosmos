(function () {
  "use strict";

  var cfg = {
    base: "",
    token: "",
    clientId: "cdeck-" + Math.random().toString(16).slice(2, 10)
  };

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

  function httpError(status, json) {
    var e = new Error("HTTP " + status);
    e.status = status;
    e.json = json;
    return e;
  }

  function shell() {
    if (window.__TAURI__ && window.__TAURI__.core && window.__TAURI__.core.invoke) {
      return function (cmd, args) {
        return window.__TAURI__.core.invoke(cmd, args || {});
      };
    }
    if (typeof window.cdeckInvoke === "function") {
      return window.cdeckInvoke;
    }
    return null;
  }

  function resolveBase() {
    if (cfg.base) return cfg.base;
    var loc = window.location;
    if (loc.protocol === "http:" || loc.protocol === "https:") {
      cfg.base = loc.protocol + "//" + loc.host;
    } else {
      cfg.base = "http://127.0.0.1:8770";
    }
    return cfg.base;
  }

  function fetchCall(path, method, body) {
    resolveBase();
    var headers = {};
    if (cfg.token) headers.Authorization = "Bearer " + cfg.token;
    var init = { method: method, headers: headers };
    if (body != null) {
      headers["Content-Type"] = "application/json";
      init.body = typeof body === "string" ? body : JSON.stringify(body);
    }
    return fetch(cfg.base.replace(/\/$/, "") + path, init).then(function (r) {
      return r.text().then(function (text) {
        var json = null;
        if (text) {
          try {
            json = JSON.parse(text);
          } catch (e) {
            json = { raw: text };
          }
        }
        if (!r.ok) throw httpError(r.status, json);
        return json;
      });
    });
  }

  function apiCall(path, opts) {
    var method = (opts && opts.method) || "GET";
    var body = opts && opts.body !== undefined ? opts.body : null;
    var inv = shell();
    if (inv) {
      return inv("api_request", {
        method: method,
        path: path,
        serverUrl: resolveBase(),
        bearer: cfg.token || null,
        body: body
      }).then(function (r) {
        if (!r.ok) {
          if (r.status === 503) throw httpError(503, "CDECK_PANEL_NOT_COMPOSED");
          throw httpError(r.status, r.json);
        }
        return r.json;
      });
    }
    if (typeof fetch !== "function") {
      return Promise.reject(new Error(
        "NO_TRANSPORT — no cDeck shell and no fetch in this host; nothing here can reach COSMOS"));
    }
    return fetchCall(path, method, body);
  }

  function apiGet(path) {
    return apiCall(path);
  }

  function apiPost(path, body) {
    return apiCall(path, { method: "POST", body: body });
  }

  function say(msg) {
    var el = $("headerSay");
    if (el) el.textContent = msg == null ? "" : String(msg);
  }

  function addConsole(kind, title, detail, pretty) {
    say(title + (detail ? ": " + detail : ""));
    if (pretty && window.console) console.log(kind, pretty);
  }

  function panelBusy() {}

  function kitForTab() {
    return null;
  }

  window.$ = $;
  window.esc = esc;
  window.apiGet = apiGet;
  window.apiPost = apiPost;
  window.api = apiCall;
  window.addConsole = addConsole;
  window.panelBusy = panelBusy;
  window.kitForTab = kitForTab;
  window.cdeckCfg = cfg;

  function bindTypeSize() {
    var key = "cdeck.typeSize";
    var saved = "m";
    try {
      saved = localStorage.getItem(key) || "m";
    } catch (e) {}
    applyTypeSize(saved);
    ["S", "M", "L"].forEach(function (label) {
      var id = "btnTypeSize" + label;
      var btn = $(id);
      if (!btn) return;
      btn.addEventListener("click", function () {
        applyTypeSize(btn.getAttribute("data-type-size") || "m");
        try {
          localStorage.setItem(key, btn.getAttribute("data-type-size") || "m");
        } catch (e2) {}
      });
    });
  }

  function applyTypeSize(size) {
    var s = String(size || "m").toLowerCase();
    if (s !== "s" && s !== "l") s = "m";
    document.body.classList.remove("cdeck-type-s", "cdeck-type-m", "cdeck-type-l");
    document.body.classList.add("cdeck-type-" + s);
    ["s", "m", "l"].forEach(function (x) {
      var b = $("btnTypeSize" + x.toUpperCase());
      if (b) b.classList.toggle("on", x === s);
    });
  }

  function bindHomeCode() {
    var btn = $("btnHomeCode");
    if (!btn) return;
    btn.addEventListener("click", function () {
      var mode = document.body.getAttribute("data-orch-mode") === "code" ? "home" : "code";
      document.body.setAttribute("data-orch-mode", mode);
      btn.textContent = mode === "code" ? "CODE" : "HOME";
      btn.setAttribute("data-orch-mode", mode);
      btn.setAttribute("aria-pressed", mode === "home" ? "true" : "false");
    });
  }

  function bindInstance() {
    var btn = $("btnInstance");
    if (!btn) return;
    btn.addEventListener("click", function () {
      var inv = shell();
      if (inv) {
        inv("open_profile_window", { profile: "forge" }).then(function (rec) {
          say((rec && rec.detail) || "INSTANCE native second window requested.");
        }).catch(function (e) {
          say("INSTANCE refused: " + (e && e.message ? e.message : String(e)));
        });
        return;
      }
      say("INSTANCE refused — browser shell cannot open a native second window. Use cdeck.exe on DT.");
    });
  }

  function bindKill() {
    var btn = $("btnKill");
    if (!btn) return;
    btn.addEventListener("click", function () {
      apiPost("/api/v1/kill", { client_id: cfg.clientId }).then(function (rec) {
        say("KILL " + JSON.stringify(rec && rec.ok != null ? rec.ok : rec));
      }).catch(function (e) {
        var j = e && e.json;
        say("KILL refused: " + ((j && j.error) || e.message || String(e)));
      });
    });
  }

  function bindControlResume() {
    var btn = $("btnControlResume");
    if (!btn) return;
    btn.addEventListener("click", function () {
      apiGet("/api/v1/control?client_id=" + encodeURIComponent(cfg.clientId)).then(function () {
        return apiPost("/api/v1/control/resume", { client_id: cfg.clientId });
      }).then(function (rec) {
        say("control/resume: " + ((rec && rec.resumed) ? "resumed" : JSON.stringify(rec)));
      }).catch(function (e) {
        var j = e && e.json;
        say("control/resume refused: " + ((j && j.error) || e.message || String(e)));
      });
    });
  }

  function bindNewCoding() {
    var btn = $("btnNewCoding");
    if (!btn) return;
    btn.addEventListener("click", function () {
      apiPost("/api/v1/session_tools", {
        action: "scan",
        families: ["coding"],
        note: "NEW coding from cDeck header"
      }).then(function (rec) {
        say("NEW coding scan: " + (rec && rec.kind ? rec.kind : "OK"));
      }).catch(function (e) {
        var j = e && e.json;
        say("NEW coding refused: " + ((j && j.detail) || (j && j.error) || e.message || String(e)));
      });
    });
  }

  function bindGemSearch() {
    var btn = $("btnGemSearch");
    if (!btn) return;
    btn.addEventListener("click", function () {
      var inv = shell();
      if (inv) {
        inv("gem_search_toggle", {}).then(function (rec) {
          say((rec && rec.detail) || "GEM search toggled (Chrome Profile 2 · Alt+G).");
        }).catch(function () {
          say("GEM search — native host missing Chrome bridge. Keith BBF Chrome Profile 2 + Alt+G. NOT_ADDRESSABLE from browser.");
        });
        return;
      }
      say("GEM search NOT_ADDRESSABLE in browser — Keith BBF Chrome Profile 2 + Alt+G. Copy query locally; no window.open gemini.");
    });
  }

  function bindSnaps() {
    var ow = $("btnOpenWorkSnap");
    if (ow) {
      ow.addEventListener("click", function () {
        var inv = shell();
        if (inv) {
          inv("snap_openwork_right", {}).then(function (rec) {
            say((rec && rec.detail) || "OpenWork snap-right");
          }).catch(function (e) {
            say("OpenWork snap-right refused: " + (e.message || String(e)));
          });
          return;
        }
        say("OpenWork snap-right refused — focus OpenWork.exe on DT; browser cannot snap native windows.");
      });
    }
    var gbw = $("btnGbwSnap");
    if (gbw) {
      gbw.addEventListener("click", function () {
        var inv = shell();
        if (inv) {
          inv("snap_gbw", {}).then(function (rec) {
            say((rec && rec.detail) || "GBW snap");
          }).catch(function (e) {
            say("GBW snap refused: " + (e.message || String(e)));
          });
          return;
        }
        say("GBW snap refused — native GBW window only on DT.");
      });
    }
  }

  function bindOrc() {
    var sel = $("selOrcStream");
    var boot = $("btnOrcBoot");
    if (boot) {
      boot.addEventListener("click", function () {
        var stream = (sel && sel.value) || "Cm";
        apiGet("/api/v1/orc").then(function (inspect) {
          say("ORC inspect stream=" + stream + " pointer=" + ((inspect && inspect.running_stream) || "?"));
          return apiPost("/api/v1/orc", { stream: stream });
        }).then(function (rec) {
          say("POST /api/v1/orc " + stream + ": " + JSON.stringify(rec && rec.ok != null ? rec.ok : rec));
        }).catch(function (e) {
          var j = e && e.json;
          say("ORC refused: " + ((j && j.detail) || (j && j.error) || e.message || String(e)));
        });
      });
    }
  }

  function bindReload() {
    var btn = $("btnReload");
    if (btn) {
      btn.addEventListener("click", function () {
        window.location.reload();
      });
    }
  }

  function paintMeshStatus() {
    apiGet("/api/v1/status").then(function (d) {
      var el = $("meshStatus");
      if (el) {
        el.textContent = "ready=" + d.ready + " tree_id=" + (d.tree_id || "?");
      }
      var base = $("coreBaseLabel");
      if (base) base.textContent = resolveBase();
    }).catch(function (e) {
      var el = $("meshStatus");
      if (el) el.textContent = "Core unreachable: " + (e.message || String(e));
    });
  }

  function initHeader() {
    bindTypeSize();
    bindHomeCode();
    bindInstance();
    bindKill();
    bindControlResume();
    bindNewCoding();
    bindGemSearch();
    bindSnaps();
    bindOrc();
    bindReload();
    paintMeshStatus();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initHeader);
  } else {
    initHeader();
  }
})();
