/* builds/cdeck/ui/header.js — shared Core transport for pane scripts. */
(function () {
  "use strict";

  var FETCH_TO_MS = 8000;
  var cfg = window.__CDECK_CFG || { base: "http://127.0.0.1:8770", token: "" };

  function shell() {
    return window.__TAURI__ && window.__TAURI__.core
      ? window.__TAURI__.core.invoke
      : null;
  }

  function httpError(status, json) {
    var msg = "HTTP " + status;
    if (json && json.error) msg = String(json.error);
    var e = new Error(msg);
    e.status = status;
    e.json = json;
    return e;
  }

  function fetchCall(path, method, body) {
    var ctl = new AbortController();
    var timer = setTimeout(function () { ctl.abort(); }, FETCH_TO_MS);
    var url = cfg.base.replace(/\/+$/, "") + path;
    var headers = cfg.token ? { Authorization: "Bearer " + cfg.token } : {};
    var init = { method: method, headers: headers, signal: ctl.signal, cache: "no-store" };
    if (body !== undefined && body !== null) {
      headers["Content-Type"] = "application/json";
      init.body = JSON.stringify(body);
    }
    return fetch(url, init)
      .then(function (r) {
        clearTimeout(timer);
        return r.text().then(function (txt) {
          var j = {};
          try { j = txt ? JSON.parse(txt) : {}; } catch (_) { j = {}; }
          if (r.status === 503) {
            throw httpError(503, j.error ? j : { error: "CDECK_PANEL_NOT_COMPOSED" });
          }
          if (!r.ok) throw httpError(r.status, j);
          return j;
        });
      })
      .catch(function (e) {
        clearTimeout(timer);
        if (e.name === "AbortError") throw new Error("timeout after " + (FETCH_TO_MS / 1000) + "s");
        throw e;
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
        serverUrl: cfg.base,
        bearer: cfg.token || null,
        body: body
      }).then(function (r) {
        if (!r.ok) {
          if (r.status === 503) throw httpError(503, { error: "CDECK_PANEL_NOT_COMPOSED" });
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

  function apiGet(path) { return apiCall(path); }
  function apiPost(path, body) { return apiCall(path, { method: "POST", body: body }); }

  window.apiCall = apiCall;
  window.apiGet = apiGet;
  window.apiPost = apiPost;
}());
