(function () {
  var KEY = "lmnator-slip-streak";
  var pool = [];
  var current = null;
  var locked = false;

  function streak() {
    var n = parseInt(localStorage.getItem(KEY) || "0", 10);
    return isFinite(n) && n > 0 ? n : 0;
  }

  function setStreak(n) {
    localStorage.setItem(KEY, String(n));
    var el = document.getElementById("slip-score");
    if (el) el.textContent = "Streak: " + n;
  }

  function esc(value) {
    return String(value == null || value === "" ? "\u2014" : value).replace(/[&<>"]/g, function (ch) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[ch];
    });
  }

  function band(price) {
    if (typeof price !== "number") return "price not listed";
    if (price < 0.5) return "cheap seat";
    if (price < 3) return "mid seat";
    return "steep seat";
  }

  function weight(value) {
    var text = String(value || "").toLowerCase();
    if (text.indexOf("open") >= 0) return "open weights";
    if (!text) return "weights not listed";
    return "closed weights";
  }

  function scored(board) {
    var seen = {};
    var out = [];
    var rings = board.rings || {};
    Object.keys(rings).forEach(function (key) {
      (rings[key] || []).forEach(function (row) {
        var id = row.dossier_id || row.name;
        if (!id || seen[id]) return;
        if (typeof row.empirical_score !== "number") return;
        seen[id] = 1;
        out.push(row);
      });
    });
    return out;
  }

  function draw() {
    locked = false;
    var box = document.getElementById("slip-reveal");
    if (box) box.innerHTML = "";
    if (!pool.length) return;
    current = pool[Math.floor(Math.random() * pool.length)];
    var card = document.getElementById("slip-card");
    card.innerHTML = "<h3>Hidden seat</h3><p>" + weight(current.weights) + "</p><p class=\"secondary\">" + band(current.prompt_price_per_m) + "</p><p class=\"secondary\">Cut under 50. Keep at 50 or more.</p>";
  }

  function guess(keep) {
    if (locked || !current) return;
    locked = true;
    var high = current.empirical_score >= 50;
    var right = keep === high;
    var next = right ? streak() + 1 : 0;
    setStreak(next);
    var verdict = right ? "On the number." : "Off the number.";
    document.getElementById("slip-reveal").innerHTML =
      "<h3>" + verdict + "</h3><article class=\"slip " + (high ? "keep" : "cut") + "\"><div class=\"slip-stub\">" +
      esc(current.empirical_score) + "</div><div class=\"slip-body\"><h3>" + esc(current.name) +
      "</h3><p class=\"price\">" + esc(current.maker) + " \u00b7 " + esc(current.dossier_id) +
      "</p><p><button type=\"button\" class=\"btn thumb\" id=\"slip-next\">Next seat</button></p></div></article>";
    document.getElementById("slip-next").onclick = draw;
  }

  fetch("board.json")
    .then(function (res) { if (!res.ok) throw new Error("catalog"); return res.json(); })
    .then(function (board) {
      pool = scored(board);
      setStreak(streak());
      draw();
      document.getElementById("slip-cut").onclick = function () { guess(false); };
      document.getElementById("slip-keep").onclick = function () { guess(true); };
    })
    .catch(function () {
      var card = document.getElementById("slip-card");
      if (card) card.innerHTML = "<h3>Hidden seat</h3><p>The catalog did not load.</p>";
    });
})();
