(function () {
  var list = document.getElementById("list");
  var play = document.getElementById("play");
  var filter = "all";
  fetch("board.json").then(function (r) { return r.json(); }).then(function (board) {
    var rows = [];
    var rings = board.rings || {};
    Object.keys(rings).forEach(function (k) { rows = rows.concat(rings[k] || []); });
    window.LMN_MODELS = rows;
  }).catch(function () { window.LMN_MODELS = []; });

  function pack() { return window.LMN_PACK || []; }

  function draw() {
    var games = pack().filter(function (g) { return filter === "all" || g.players === filter; });
    list.innerHTML = "<p class=\"secondary\">" + games.length + " games</p>" + games.map(function (g) {
      return '<article class="shop-card"><p class="kicker">' + (g.players === "multi" ? "MULTIPLAYER" : "SINGLE") + " · " + g.engine + '</p><h3>' + g.title + '</h3><p class="secondary">After ' + g.inspired + '. ' + g.better + '</p><p><a class="btn" href="#/' + g.id + '">Play</a></p></article>';
    }).join("");
  }

  function openGame(id) {
    var def = pack().filter(function (g) { return g.id === id; })[0];
    if (!def) { play.hidden = true; list.hidden = false; draw(); return; }
    list.hidden = true;
    play.hidden = false;
    play.innerHTML = '<p><a href="#/">All games</a></p><div id="stage"></div>';
    window.LMN_PLAY(def, play.querySelector("#stage"));
    play.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function route() {
    var id = (location.hash || "").replace("#/", "");
    if (!id) { play.hidden = true; list.hidden = false; draw(); return; }
    openGame(id);
  }

  document.getElementById("tab-all").onclick = function () { filter = "all"; route(); };
  document.getElementById("tab-single").onclick = function () { filter = "single"; if (location.hash) location.hash = "/"; else draw(); };
  document.getElementById("tab-multi").onclick = function () { filter = "multi"; if (location.hash) location.hash = "/"; else draw(); };
  window.addEventListener("hashchange", route);

  var install = document.getElementById("install");
  var note = document.getElementById("install-note");
  var prompt = null;
  window.addEventListener("beforeinstallprompt", function (e) { e.preventDefault(); prompt = e; });
  install.onclick = function () {
    if (prompt) { prompt.prompt(); return; }
    note.textContent = "On a phone: Share or the browser menu, then Add to Home Screen. The download link is the same app as files.";
  };
  if ("serviceWorker" in navigator) navigator.serviceWorker.register("sw.js").catch(function () {});
  route();
})();
