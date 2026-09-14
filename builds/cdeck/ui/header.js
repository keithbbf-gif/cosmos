"use strict";
// header.js — beige header; apiGet/apiPost; kitForTab
(function () {
  var cfg = { base: "http://127.0.0.1:8770", token: "" };

  function isLoopbackBase(base) {
    var h = "";
    try { h = String(new URL(base).hostname || "").toLowerCase(); }
    catch (_) { h = ""; }
    return h === "127.0.0.1" || h === "localhost" || h === "[::1]" || h === "::1";
  }

  function authHeaders() {
    /* live Core :8770 — loopback skip, bearer non-loopback */
    if (cfg.token && !isLoopbackBase(cfg.base)) {
      return { Authorization: "Bearer " + cfg.token };
    }
    return {};
  }

  function apiGet(path) {
    return fetch(cfg.base + path, {
      headers: authHeaders(),
      cache: "no-store",
    }).then(function (r) { return r.json(); });
  }

  function apiPost(path, body) {
    return fetch(cfg.base + path, {
      method: "POST",
      headers: Object.assign(
        { "Content-Type": "application/json" },
        authHeaders()
      ),
      body: JSON.stringify(body),
    }).then(function (r) { return r.json(); });
  }

  function kitForTab(name) {
    return { apiGet: apiGet, apiPost: apiPost, tab: name };
  }

  window.cdeckHeader = { cfg: cfg, apiGet: apiGet, apiPost: apiPost, kitForTab: kitForTab };
})();
