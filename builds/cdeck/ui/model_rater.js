(function () {
  "use strict";

  function $(id) {
    return document.getElementById(id);
  }

  function openDrawer() {
    var drawer = $("model-rater-drawer");
    var body = $("modelRaterBody");
    if (!drawer || !body) return;
    drawer.classList.remove("hidden");
    body.textContent = "Loading GET /api/v1/model_rater …";
    apiGet("/api/v1/model_rater?limit=40").then(function (rec) {
      body.textContent = JSON.stringify(rec, null, 2);
    }).catch(function (e) {
      var j = e && e.json;
      body.textContent = "MODEL RATER refused: " +
        ((j && j.detail) || (j && j.error) || e.message || String(e));
    });
  }

  function bind() {
    var open = $("btnModelRater");
    var close = $("btnModelRaterClose");
    if (open) open.addEventListener("click", openDrawer);
    if (close) {
      close.addEventListener("click", function () {
        var drawer = $("model-rater-drawer");
        if (drawer) drawer.classList.add("hidden");
      });
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bind);
  } else {
    bind();
  }
})();
