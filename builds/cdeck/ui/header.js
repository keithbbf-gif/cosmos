"use strict";
// header.js — beige header; apiGet/apiPost; kitForTab
(function () {
  var cfg = window.__CDECK_CFG || {};
  var base = cfg.base != null && String(cfg.base) !== "" ? String(cfg.base) : "";
  var token = cfg.token != null ? String(cfg.token) : "";

  function url(path) {
    return base.replace(/\/$/, "") + path;
  }

  function apiGet(path) {
    return fetch(url(path), {
      headers: token ? { Authorization: "Bearer " + token } : {},
      cache: "no-store",
    }).then(function (r) { return r.json(); });
  }

  function apiPost(path, body) {
    return fetch(url(path), {
      method: "POST",
      headers: Object.assign(
        { "Content-Type": "application/json" },
        token ? { Authorization: "Bearer " + token } : {}
      ),
      body: JSON.stringify(body),
    }).then(function (r) { return r.json(); });
  }

  function kitForTab(name) {
    return { apiGet: apiGet, apiPost: apiPost, tab: name };
  }

  window.cdeckHeader = {
    cfg: { base: base, token: token },
    apiGet: apiGet,
    apiPost: apiPost,
    kitForTab: kitForTab,
  };
})();
