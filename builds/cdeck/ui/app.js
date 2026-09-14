(function () {
  "use strict";
  /* MESH widgets + shared apiCall (header.js owns apiGet/apiPost globals). */
  if (typeof apiCall !== "function") {
    console.warn("app.js loaded before header transport");
  }
})();
