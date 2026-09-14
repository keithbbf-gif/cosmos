/* builds/cdeck/ui/app.js — cDeck UI transport
 *
 * apiCall: fetch-based transport for cDeck panels hitting Core at cfg.base.
 * 503 from Core always carries {"error":"CDECK_PANEL_NOT_COMPOSED"}; that
 * string is surfaced verbatim so panels can name the composition failure.
 */

(function () {
  "use strict";

  var FETCH_TO_MS = 8000;

  /* cfg is written by the host page before any panel calls apiCall. */
  var cfg = window.__CDECK_CFG || { base: "http://127.0.0.1:8770", token: "" };

  /**
   * apiCall(path, opts?) → Promise<object>
   *
   * Resolves with the parsed JSON body on 2xx.
   * Rejects with an Error whose .status and .json are set on any non-2xx.
   *
   * 503 branch: Core composition failures return {"error":"CDECK_PANEL_NOT_COMPOSED"}.
   * That j.error value is thrown verbatim so every panel that catches the
   * rejection can display it with e.message === "CDECK_PANEL_NOT_COMPOSED".
   */
  function apiCall(path, opts) {
    var method  = (opts && opts.method) || "GET";
    var budget  = FETCH_TO_MS;
    var ctl     = new AbortController();
    var timer   = setTimeout(function () { ctl.abort(); }, budget);
    var url     = cfg.base.replace(/\/+$/, "") + path;
    var headers = cfg.token ? { "Authorization": "Bearer " + cfg.token } : {};
    var init    = {
      method:  method,
      headers: headers,
      signal:  ctl.signal,
      cache:   "no-store"
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
            var e401 = new Error("UNAUTHORIZED");
            e401.status = 401;
            e401.json   = j;
            throw e401;
          }

          if (r.status === 503) {
            /* Surface the verbatim Core error string so panels can name the
             * composition failure (e.g. CDECK_PANEL_NOT_COMPOSED). */
            var detail = (j.error) ? String(j.error) : "CDECK_PANEL_NOT_COMPOSED";
            var e503   = new Error(detail);
            e503.status = 503;
            e503.json   = j;
            throw e503;
          }

          if (!r.ok) {
            var msg  = j.error ? String(j.error) : ("HTTP " + r.status + " " + r.statusText);
            if (j.detail) msg += " \u2014 " + j.detail;
            var eN   = new Error(msg);
            eN.status = r.status;
            eN.json   = j;
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

  function apiGet(path)        { return apiCall(path); }
  function apiPost(path, body) { return apiCall(path, { method: "POST", body: body }); }

  /* Expose on window for panel scripts loaded after this file. */
  window.apiCall = apiCall;
  window.apiGet  = apiGet;
  window.apiPost = apiPost;

}());
