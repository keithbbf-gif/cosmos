/* builds/cdeck/ui/header.js — beige header transport + CONNECT / PAUSE / RELOAD
 *
 * Pane scripts call apiGet/apiPost from here (no fetch in deck_*.js).
 * Same-origin Core (:8770) loopback needs no bearer; remote peers still do.
 */
(function () {
  "use strict";

  var FETCH_TO_MS = 8000;
  var REFRESH_S = 10;
  var UNAUTH_CHIP = "UNAUTHORIZED \u2014 paste a bearer";

  var cfg = { base: "", token: "" };
  var connected = false;
  var paused = false;
  var inflight = false;
  var connectGen = 0;
  var nextAt = 0;
  var dueAt = Object.create(null);

  function $(id) {
    return document.getElementById(id);
  }

  function defaultBase() {
    if (window.location && window.location.origin
        && window.location.protocol !== "file:") {
      return window.location.origin;
    }
    return "http://127.0.0.1:8770";
  }

  function syncCfgExport() {
    window.__CDECK_CFG = { base: cfg.base, token: cfg.token };
  }

  function apiCall(path, opts) {
    var method = (opts && opts.method) || "GET";
    var budget = FETCH_TO_MS;
    var ctl = new AbortController();
    var timer = setTimeout(function () { ctl.abort(); }, budget);
    var base = (cfg.base || "").replace(/\/+$/, "");
    var url = base + path;
    var headers = cfg.token ? { Authorization: "Bearer " + cfg.token } : {};
    var init = {
      method: method,
      headers: headers,
      signal: ctl.signal,
      cache: "no-store",
    };
    if (opts && opts.body !== undefined) {
      headers["Content-Type"] = "application/json";
      init.body = JSON.stringify(opts.body);
    }
    return fetch(url, init)
      .then(function (r) {
        clearTimeout(timer);
        return r.text().then(function (txt) {
          var j = {};
          try { j = txt ? JSON.parse(txt) : {}; } catch (_) { j = {}; }
          if (r.status === 401) {
            var e401 = new Error(UNAUTH_CHIP);
            e401.status = 401;
            e401.json = j;
            throw e401;
          }
          if (r.status === 503) {
            var detail = j.error ? String(j.error) : "CDECK_PANEL_NOT_COMPOSED";
            var e503 = new Error(detail);
            e503.status = 503;
            e503.json = j;
            throw e503;
          }
          if (!r.ok) {
            var msg = j.error ? String(j.error) : ("HTTP " + r.status + " " + r.statusText);
            if (j.detail) msg += " \u2014 " + j.detail;
            var eN = new Error(msg);
            eN.status = r.status;
            eN.json = j;
            throw eN;
          }
          return j;
        });
      })
      .catch(function (e) {
        clearTimeout(timer);
        if (e.name === "AbortError") {
          throw new Error("timeout after " + (budget / 1000) + "s");
        }
        throw e;
      });
  }

  function apiGet(path) {
    return apiCall(path);
  }

  function apiPost(path, body) {
    return apiCall(path, { method: "POST", body: body });
  }

  function kitForTab(/* tabName */) {
    return {
      apiGet: apiGet,
      apiPost: apiPost,
      base: function () { return cfg.base; },
      token: function () { return cfg.token; },
      connected: function () { return connected; },
      paused: function () { return paused; },
    };
  }

  function setConnState(text, cls) {
    var cs = $("connState");
    if (!cs) return;
    cs.textContent = text;
    cs.className = cls || "";
  }

  function setRefreshControlsEnabled(on) {
    var bp = $("btnPause");
    var br = $("btnReload");
    if (bp) {
      bp.disabled = !on;
      if (!on) {
        bp.textContent = "PAUSE";
        paused = false;
      }
    }
    if (br) br.disabled = !on;
  }

  function paintConnOutcome(results, t0, gen) {
    if (gen !== connectGen) return;
    var all401 = results.every(function (r) {
      return r && r.err && r.err.status === 401;
    });
    var anyOk = results.some(function (r) { return r && r.ok; });
    var allBad = results.every(function (r) { return !r || !r.ok; });
    if (all401) {
      setConnState(UNAUTH_CHIP, "bad");
      try { $("token").focus(); } catch (_) { /* no-op */ }
    } else if (allBad) {
      setConnState("SERVER DOWN", "bad");
    } else if (anyOk) {
      setConnState(
        "connected \u00b7 " + cfg.base + " \u00b7 rtt " + (Date.now() - t0) + "ms",
        "ok",
      );
    }
  }

  function refreshAll(force) {
    if (!connected) return;
    if (paused && !force) return;
    if (inflight) return;
    inflight = true;
    var gen = connectGen;
    var t0 = Date.now();
    var paths = ["/api/v1/status", "/api/v1/health"];
    Promise.all(paths.map(function (p) {
      return apiGet(p).then(function (j) {
        return { ok: true, path: p, body: j };
      }).catch(function (err) {
        return { ok: false, path: p, err: err };
      });
    })).then(function (results) {
      if (gen !== connectGen) return;
      inflight = false;
      paintConnOutcome(results, t0, gen);
      document.dispatchEvent(new CustomEvent("cdeck:refresh", {
        detail: { force: !!force, results: results },
      }));
      nextAt = Date.now() + REFRESH_S * 1000;
      tickCountdown();
    });
  }

  function tickCountdown() {
    var cd = $("countdown");
    if (!cd) return;
    if (!connected) {
      cd.textContent = "refresh idle";
      return;
    }
    if (paused) {
      cd.textContent = "refresh PAUSED";
      cd.className = "paused";
      return;
    }
    cd.className = "";
    var left = Math.max(0, Math.ceil((nextAt - Date.now()) / 1000));
    cd.textContent = "next refresh in " + left + "s";
  }

  function doConnect() {
    var baseEl = $("apiBase");
    var tokEl = $("token");
    var newBase = baseEl ? baseEl.value.trim() : "";
    if (!newBase) newBase = defaultBase();
    if (baseEl && !baseEl.value.trim()) baseEl.value = newBase;
    cfg.base = newBase;
    cfg.token = tokEl ? tokEl.value.trim() : "";
    syncCfgExport();
    if (!cfg.base) {
      setConnState("API base required", "bad");
      connected = false;
      setRefreshControlsEnabled(false);
      return;
    }
    connectGen += 1;
    connected = true;
    paused = false;
    dueAt = Object.create(null);
    setRefreshControlsEnabled(true);
    var bp = $("btnPause");
    if (bp) bp.textContent = "PAUSE";
    setConnState("connecting\u2026", "");
    nextAt = Date.now();
    refreshAll(true);
  }

  function onPauseClick() {
    var btn = $("btnPause");
    if (!btn || btn.disabled || !connected) return;
    paused = !paused;
    btn.textContent = paused ? "RESUME" : "PAUSE";
    if (!paused) {
      nextAt = Date.now();
      refreshAll(true);
    } else {
      tickCountdown();
    }
  }

  function onReloadClick() {
    var btn = $("btnReload");
    if (!btn || btn.disabled || !connected) return;
    dueAt = Object.create(null);
    nextAt = Date.now();
    refreshAll(true);
  }

  function wireHeader() {
    var bc = $("btnConnect");
    var bp = $("btnPause");
    var br = $("btnReload");
    if (bc) bc.addEventListener("click", doConnect);
    if (bp) bp.addEventListener("click", onPauseClick);
    if (br) br.addEventListener("click", onReloadClick);
    ["apiBase", "token"].forEach(function (id) {
      var el = $(id);
      if (!el) return;
      el.addEventListener("keydown", function (e) {
        if (e.key === "Enter" && bc) bc.click();
      });
    });
    setInterval(function () {
      if (!connected || paused || inflight) {
        tickCountdown();
        return;
      }
      if (Date.now() >= nextAt) refreshAll(false);
      tickCountdown();
    }, 1000);
  }

  function connectOnLoad() {
    var baseEl = $("apiBase");
    if (baseEl && !baseEl.value.trim()) baseEl.value = defaultBase();
    doConnect();
  }

  function init() {
    wireHeader();
    connectOnLoad();
  }

  window.apiCall = apiCall;
  window.apiGet = apiGet;
  window.apiPost = apiPost;
  window.kitForTab = kitForTab;
  window.cdeckHeaderRefresh = function () { refreshAll(true); };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
}());
