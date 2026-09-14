"use strict";
// header.js — beige header; apiGet/apiPost; kitForTab
(function () {
  var cfg = { base: "http://127.0.0.1:8770", token: "" };

  function apiGet(path) {
    return fetch(cfg.base + path, {
      headers: cfg.token ? { Authorization: "Bearer " + cfg.token } : {},
      cache: "no-store",
    }).then(function (r) { return r.json(); });
  }

  function apiPost(path, body) {
    return fetch(cfg.base + path, {
      method: "POST",
      headers: Object.assign(
        { "Content-Type": "application/json" },
        cfg.token ? { Authorization: "Bearer " + cfg.token } : {}
      ),
      body: JSON.stringify(body),
    }).then(function (r) { return r.json(); });
  }

  function kitForTab(name) {
    return { apiGet: apiGet, apiPost: apiPost, tab: name };
  }

  window.cdeckHeader = { cfg: cfg, apiGet: apiGet, apiPost: apiPost, kitForTab: kitForTab };
})();
