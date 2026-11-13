(function () {
  var pool = [];
  var alive = false;
  var roundId = 0;
  var claimed = false;
  var you = { name: "You", you: true, pts: 0, note: "waiting" };
  var rivals = [
    { name: "Sprinter", skill: 0.62, delay: 420, pts: 0, note: "" },
    { name: "Librarian", skill: 0.84, delay: 980, pts: 0, note: "" },
    { name: "Novelist", skill: 0.38, delay: 640, pts: 0, note: "" }
  ];

  function purse() { return window.LMNPurse ? window.LMNPurse.get() : 0; }
  function setPurse(n) { if (window.LMNPurse) window.LMNPurse.set(n); }
  function esc(value) {
    return String(value == null || value === "" ? "\u2014" : value).replace(/[&<>"]/g, function (ch) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[ch];
    });
  }
  function seats() { return [you].concat(rivals); }
  function paintField() {
    var box = document.getElementById("field");
    if (!box) return;
    box.innerHTML = seats().map(function (s) {
      return '<div class="seat-row' + (s.you ? " you" : "") + '"><strong>' + esc(s.name) + '</strong><p class="price">' +
        s.pts + " / 6</p><p class=\"secondary\">" + esc(s.note) + "</p></div>";
    }).join("");
  }
  function shuffle(list) {
    var a = list.slice();
    for (var i = a.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var t = a[i]; a[i] = a[j]; a[j] = t;
    }
    return a;
  }
  function valueOf(row, mode) {
    if (mode === "score") return row.empirical_score;
    if (mode === "cheap") return typeof row.prompt_price_per_m === "number" ? row.prompt_price_per_m : null;
    return typeof row.context_length === "number" ? row.context_length : null;
  }
  function face(mode, row) {
    var n = valueOf(row, mode);
    if (mode === "score") return "score " + n;
    if (mode === "cheap") return "$" + n + " in";
    return "ctx " + n;
  }
  function ask(mode) {
    if (mode === "score") return "Highest score";
    if (mode === "cheap") return "Cheapest prompt";
    return "Longest context";
  }
  function winner() {
    var top = null;
    seats().forEach(function (s) { if (!top || s.pts > top.pts) top = s; });
    return top && top.pts >= 6 ? top : null;
  }
  function end(msg) {
    alive = false;
    if (window.LMN_SAVE) {
      window.LMN_SAVE({
        game: "tiles",
        event: "match",
        models: (window.LMN_LAST_TILES || []).map(window.LMN_MODEL),
        outcome: { table: seats().map(function (s) { return { role: s.you ? "you" : (s.role || ""), kind: s.human ? "human" : "ai", hits: s.pts }; }) }
      });
    }
    roundId += 1;
    var top = seats().slice().sort(function (a, b) { return b.pts - a.pts; })[0];
    if (top && top.you && top.pts >= 6) setPurse(purse() + 3);
    document.getElementById("tile-end").innerHTML = "<h2>" + esc(msg) + "</h2><p><button type=\"button\" class=\"btn thumb\" id=\"tile-again\">New table</button></p>";
    document.getElementById("tile-again").onclick = start;
  }
  function score(seat, note) {
    if (claimed || !alive) return;
    claimed = true;
    seat.pts += 1;
    seat.note = note;
    if (seat === you && window.LMN_MATCH && window.LMN_PID) {
      fetch("queue.php", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ op: "move", pid: window.LMN_PID, match: window.LMN_MATCH.id, round: seat.pts, pick: "hit" }) }).catch(function () {});
    }
    paintField();
    var top = winner();
    if (top) { end(top.name + " takes the table"); return; }
    setTimeout(deal, 280);
  }
  function deal() {
    if (!alive) return;
    roundId += 1;
    var token = roundId;
    claimed = false;
    var modes = ["score", "cheap", "reach"];
    var mode = modes[Math.floor(Math.random() * modes.length)];
    var usable = pool.filter(function (row) { return valueOf(row, mode) != null; });
    if (usable.length < 4) { mode = "score"; usable = pool; }
    var four = shuffle(usable).slice(0, 4);
    var best = four[0];
    four.forEach(function (row) {
      var a = valueOf(row, mode);
      var b = valueOf(best, mode);
      if (mode === "cheap") { if (a < b) best = row; }
      else if (a > b) best = row;
    });
    window.LMN_LAST_TILES = four.slice();
    window.LMN_LAST_ASK = mode;
    document.getElementById("tile-ask").textContent = ask(mode);
    var grid = document.getElementById("tile-grid");
    grid.innerHTML = "";
    shuffle(four).forEach(function (row) {
      var b = document.createElement("button");
      b.type = "button";
      b.className = "tile";
      b.innerHTML = esc(row.name) + "<br><span class=\"price\">" + esc(face(mode, row)) + "</span>";
      b.addEventListener("click", function () {
        if (!alive || claimed || token !== roundId) return;
        if (row !== best) { you.note = "miss"; paintField(); return; }
        you.note = "hit";
        score(you, "hit");
      });
      grid.appendChild(b);
    });
    rivals.forEach(function (r) {
      if (r.human) return;
      setTimeout(function () {
        if (!alive || claimed || token !== roundId) return;
        if (Math.random() < r.skill) score(r, "hit");
        else r.note = "miss";
        paintField();
      }, r.delay);
    });
  }
  function start() {
    alive = true;
    you.pts = 0; you.note = "go";
    rivals.forEach(function (r) { r.pts = 0; r.note = "waiting"; });
    document.getElementById("tile-end").innerHTML = "";
    paintField();
    deal();
  }
  fetch("board.json").then(function (res) { if (!res.ok) throw new Error("catalog"); return res.json(); }).then(function (board) {
    var seen = {};
    var rings = board.rings || {};
    Object.keys(rings).forEach(function (key) {
      (rings[key] || []).forEach(function (row) {
        var id = row.dossier_id || row.name;
        if (!id || seen[id] || typeof row.empirical_score !== "number") return;
        seen[id] = 1;
        pool.push(row);
      });
    });
    if (pool.length < 4) throw new Error("short");
    window.LMN_BEGIN = function (match) {
      var by = {};
      (match.seats || []).forEach(function (s) { by[s.role] = s; });
      function one(role, skill, delay) {
        var s = by[role] || { kind: "ai", name: role, skill: skill };
        return { name: s.name, skill: s.kind === "human" ? 0 : (s.skill || skill), delay: s.kind === "human" ? 1200 : delay, pts: 0, note: "", you: false, human: s.kind === "human", pid: s.pid || "" };
      }
      rivals = [one("teammate", 0.84, 980), one("enemy", 0.62, 420), one("enemy2", 0.38, 640)];
      if (rivals.some(function (r) { return r.human; })) {
        setInterval(function () {
          if (!window.LMN_MATCH) return;
          fetch("queue.php", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ op: "poll", pid: window.LMN_PID }) })
            .then(function (res) { return res.json(); })
            .then(function (data) {
              var moves = data && data.match && data.match.moves;
              if (!moves) return;
              rivals.forEach(function (r) {
                if (!r.human) return;
                var n = 0;
                Object.keys(moves).forEach(function (key) {
                  if (moves[key] && moves[key][r.pid] === "hit") n += 1;
                });
                r.pts = n;
                r.note = n ? "in the match" : "waiting";
              });
              paintField();
            }).catch(function () {});
        }, 1000);
      }
      start();
    };
  }).catch(function () {
    document.getElementById("tile-ask").textContent = "The catalog did not load.";
  });
})();
