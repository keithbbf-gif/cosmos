(function () {
  var CHIPS = "lmnator-house-chips";
  var pool = [];
  var pair = [null, null];
  var voted = false;
  var spinning = false;

  function chips() {
    var n = parseInt(localStorage.getItem(CHIPS) || "12", 10);
    if (!isFinite(n) || n < 0) n = 12;
    return n;
  }

  function setChips(n) {
    localStorage.setItem(CHIPS, String(n));
    var el = document.getElementById("chip-count");
    if (el) el.textContent = "House chips: " + n;
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

  function money(value, label) {
    return typeof value === "number" ? "$" + value + " / M " + label : label + " not listed";
  }

  function unique(board) {
    var seen = {};
    var out = [];
    var rings = board.rings || {};
    Object.keys(rings).forEach(function (key) {
      (rings[key] || []).forEach(function (row) {
        var id = row.dossier_id || row.name;
        if (!id || seen[id]) return;
        seen[id] = 1;
        out.push(row);
      });
    });
    return out;
  }

  function card(row, label) {
    return '<article class="slip keep"><div class="slip-stub">' + esc(label) + '</div><div class="slip-body"><h3>' +
      esc(row.name) + '</h3><p class="price">' + esc(row.maker) + ' \u00b7 score ' + esc(row.empirical_score) +
      ' \u00b7 ' + esc(money(row.prompt_price_per_m, "in")) + ' \u00b7 ' + esc(money(row.completion_price_per_m, "out")) +
      '</p><p class="price">' + esc(row.dossier_id) + '</p></div></article>';
  }

  function paintBlind(id, row, label) {
    var el = document.getElementById(id);
    if (!el) return;
    el.innerHTML = "<h3>" + label + "</h3><p>" + weight(row.weights) + "</p><p class=\"secondary\">" + band(row.prompt_price_per_m) + "</p>";
  }

  function drawPair() {
    voted = false;
    var reveal = document.getElementById("bout-reveal");
    if (reveal) reveal.innerHTML = "";
    if (pool.length < 2) return;
    var i = Math.floor(Math.random() * pool.length);
    var j = Math.floor(Math.random() * (pool.length - 1));
    if (j >= i) j += 1;
    pair = [pool[i], pool[j]];
    paintBlind("seat-a", pair[0], "Left");
    paintBlind("seat-b", pair[1], "Right");
  }

  function reveal(choice) {
    if (voted || !pair[0]) return;
    voted = true;
    var box = document.getElementById("bout-reveal");
    var cheapLeft = typeof pair[0].prompt_price_per_m === "number" && (typeof pair[1].prompt_price_per_m !== "number" || pair[0].prompt_price_per_m <= pair[1].prompt_price_per_m);
    var openLeft = String(pair[0].weights || "").toLowerCase().indexOf("open") >= 0;
    var openRight = String(pair[1].weights || "").toLowerCase().indexOf("open") >= 0;
    var librarian = cheapLeft ? "Left" : "Right";
    var sprinter = openLeft === openRight ? "Either" : (openLeft ? "Left" : "Right");
    if (window.LMN_SAVE) {
      window.LMN_SAVE({
        game: "pit",
        event: "blind_vote",
        models: [window.LMN_MODEL(pair[0]), window.LMN_MODEL(pair[1])],
        calls: [
          { role: "you", kind: "human", pick: choice },
          { role: "enemy", kind: "ai", ai: "Sprinter", pick: sprinter },
          { role: "teammate", kind: "ai", ai: "Librarian", pick: librarian }
        ]
      });
    }
    box.innerHTML = "<h3>Names, after the vote</h3>" + card(pair[0], "Left") + card(pair[1], "Right") +
      "<p class=\"secondary\">You picked " + esc(choice) + " while the names were hidden. Sprinter called " + sprinter + ". The Librarian called " + librarian + ".</p>";
  }

  function spin() {
    if (spinning || pool.length < 1) return;
    var n = chips();
    if (n < 1) return;
    spinning = true;
    setChips(n - 1);
    var reels = [0, 1, 2].map(function (i) { return document.getElementById("reel-" + i); });
    reels.forEach(function (el) { el.className = "reel spinning"; });
    var ticks = 0;
    var timer = setInterval(function () {
      ticks += 1;
      reels.forEach(function (el) {
        var row = pool[Math.floor(Math.random() * pool.length)];
        el.textContent = row ? row.name : "\u2014";
      });
      if (ticks <= 14) return;
      clearInterval(timer);
      var landed = [0, 1, 2].map(function () { return pool[Math.floor(Math.random() * pool.length)]; });
      reels.forEach(function (el, i) {
        el.className = "reel";
        el.textContent = landed[i].name;
      });
      document.getElementById("landed").innerHTML = "<p class=\"secondary\">Middle reel is the seat a call would use. Worth it when the ask needs that seat, not because the name is famous.</p>" + card(landed[1], "Call");
      spinning = false;
    }, 70);
  }

  function boot(board) {
    pool = unique(board);
    setChips(chips());
    drawPair();
    document.getElementById("vote-a").onclick = function () { reveal("Left"); };
    document.getElementById("vote-b").onclick = function () { reveal("Right"); };
    document.getElementById("vote-tie").onclick = function () { reveal("Either"); };
    document.getElementById("vote-none").onclick = function () { reveal("Neither"); };
    document.getElementById("bout-next").onclick = drawPair;
    document.getElementById("spin").onclick = spin;
    document.getElementById("refill").onclick = function () { setChips(12); };
  }

  fetch("board.json")
    .then(function (res) { if (!res.ok) throw new Error("catalog"); return res.json(); })
    .then(boot)
    .catch(function () {
      var seat = document.getElementById("seat-a");
      if (seat) seat.innerHTML = "<h3>Left</h3><p>The catalog did not load.</p>";
    });
})();
