(function (global) {
  "use strict";
  function apiGet(path) {
    return fetch(path, { credentials: "same-origin" }).then(function (r) {
      return r.json().then(function (j) {
        if (!r.ok) {
          var e = new Error(j && j.error ? j.error : String(r.status));
          e.status = r.status;
          e.json = j;
          throw e;
        }
        return j;
      });
    });
  }
  global.apiGet = apiGet;
})(typeof globalThis !== "undefined" ? globalThis : this);
