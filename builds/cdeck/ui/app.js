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
