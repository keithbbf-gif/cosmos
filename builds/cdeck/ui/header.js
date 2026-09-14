(function () {
  "use strict";

  var cfg = { base: "http://127.0.0.1:8770", token: "" };

  function httpError(status, json) {
    var e = new Error("HTTP " + status);
    e.status = status;
    e.json = json;
    return e;
  }

  function apiCall(path, opts) {
    var method = (opts && opts.method) || "GET";
    var body = opts && opts.body !== undefined ? opts.body : null;
    var inv = typeof window.__TAURI__ !== "undefined" && window.__TAURI__.core
      ? window.__TAURI__.core.invoke
      : null;
    if (inv) {
      return inv("api_request", {
        method: method,
        path: path,
        serverUrl: cfg.base,
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
        "NO_TRANSPORT — no cDeck shell and no fetch in this host"));
    }
    var hdrs = { Accept: "application/json" };
    if (cfg.token) hdrs.Authorization = "Bearer " + cfg.token;
    if (body != null) hdrs["Content-Type"] = "application/json";
    return fetch(cfg.base + path, {
      method: method,
      headers: hdrs,
      body: body != null ? JSON.stringify(body) : undefined
    }).then(function (resp) {
      return resp.text().then(function (text) {
        var json = null;
        try { json = text ? JSON.parse(text) : null; } catch (_e) { json = { raw: text }; }
        if (!resp.ok) {
          if (resp.status === 503) throw httpError(503, "CDECK_PANEL_NOT_COMPOSED");
          throw httpError(resp.status, json);
        }
        return json;
      });
    });
  }

  function apiGet(path) {
    return apiCall(path, { method: "GET" });
  }

  function apiPost(path, body) {
    return apiCall(path, { method: "POST", body: body || {} });
  }

  function api(path, opts) {
    return apiCall(path, opts || { method: "GET" });
  }

  window.cdeckApiConfig = cfg;
  window.apiCall = apiCall;
  window.apiGet = apiGet;
  window.apiPost = apiPost;
  window.api = api;
})();
