(function () {
  var pool = [];
  var cur = null;
  var nxt = null;
  var locked = false;
  var round = 0;
  var you = { name: "You", you: true, lives: 2, pts: 0, out: false, note: "" };
  var rivals = [
    { name: "Sprinter", skill: 0.58, delay: 260, lives: 2, pts: 0, out: false, note: "" },
    { name: "Librarian", skill: 0.76, delay: 680, lives: 2, pts: 0, out: false, note: "" },
    { name: "Novelist", skill: 0.4, delay: 440, lives: 2, pts: 0, out: false, note: "" }
  ];

  function purse() { return window.LMNPurse ? window.LMNPurse.get() : 0; }
  function setPurse(n) { if (window.LMNPurse) window.LMNPurse.set(n); }
  function esc(value) {
    return String(value == null || value === "" ? "\u2014" : value).replace(/[&<>"]/g, function (ch) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[ch];
    });
  }
  function money(value) { return typeof value === "number" ? "$" + value + " / M in" : "price not listed"; }
  function seats() { return [you].concat(rivals); }
  function paintField() {
    var box = document.getElementById("field");
    if (!box) return;
    box.innerHTML = seats().map(function (s) {
      return '<div class="seat-row' + (s.you ? " you" : "") + (s.out ? " out" : "") + '"><strong>' + esc(s.name) +
        "</strong><p class=\"price\">" + s.pts + " right \u00b7 " + Math.max(0, s.lives) + " lives</p><p class=\"secondary\">" + esc(s.note) + "</p></div>";
    }).join("");
  }
  function drawNext(except) {
    var pick = pool[Math.floor(Math.random() * pool.length)];
    var guard = 0;
    while (pick === except && guard < 8) {
      pick = pool[Math.floor(Math.random() * pool.length)];
      guard += 1;
    }
    return pick;
  }
  function showCard() {
    document.getElementById("higher-now").innerHTML = "<p class=\"secondary\">On the table</p><h2>" + esc(cur.name) +
      "</h2><p class=\"hl-score\">" + esc(cur.empirical_score) + "</p><p class=\"price\">" + esc(cur.maker) + " \u00b7 " + esc(money(cur.prompt_price_per_m)) + "</p>";
    document.getElementById("higher-next").innerHTML = "<h3>Next, score hidden</h3><p>" + esc(nxt.name) + "</p><p class=\"secondary\">" +
      esc(nxt.maker) + " \u00b7 " + esc(money(nxt.prompt_price_per_m)) + " \u00b7 ctx " + esc(nxt.context_length) + "</p>";
  }
  function mark(seat, ok) {
    if (seat.out) return;
    if (ok) {
      seat.pts += 1;
      seat.note = "right";
    } else {
      seat.lives -= 1;
      seat.note = "wrong";
      if (seat.lives <= 0) seat.out = true;
    }
  }
  function living() { return seats().filter(function (s) { return !s.out; }); }
  function onSide(seat) { return seat && (seat.you || seat.role === "teammate"); }
  function finish(winner) {
    locked = true;
    var youWon = onSide(winner);
    if (youWon) setPurse(purse() + 3);
    if (window.LMN_SAVE) {
      window.LMN_SAVE({
        game: "higher",
        event: "match",
        outcome: { winner: winner ? (youWon ? "your_side" : "other_side") : "none", table: seats().map(function (s) { return { role: s.you ? "you" : s.role, kind: s.human ? "human" : "ai", right: s.pts, lives: s.lives }; }) }
      });
    }
    document.getElementById("higher-end").innerHTML = "<h2>" + esc(winner ? (youWon ? "Your side" : winner.name) : "Nobody") + " takes the table</h2><p class=\"secondary\">" +
      (youWon ? "3 game tokens for the win." : "The other side takes it.") + "</p><p><button type=\"button\" class=\"btn thumb\" id=\"higher-again\">Queue again</button></p>";
    document.getElementById("higher-again").onclick = function () { location.reload(); };
  }
  function advance() {
    if (window.LMN_SAVE && cur && nxt) {
      window.LMN_SAVE({
        game: "higher",
        event: "round",
        models: [window.LMN_MODEL(cur), window.LMN_MODEL(nxt)],
        calls: seats().map(function (s) {
          return { role: s.you ? "you" : s.role, kind: s.human ? "human" : "ai", note: s.note || "" };
        })
      });
    }
    var alive = living();
    var topped = null;
    alive.forEach(function (s) { if (s.pts >= 5) topped = s; });
    if (topped) { finish(topped); return; }
    if (alive.length <= 1) { finish(alive[0] || null); return; }
    if (you.out && !rivals.some(function (r) { return r.role === "teammate" && !r.out; })) {
      finish(alive.slice().sort(function (a, b) { return b.pts - a.pts; })[0]);
      return;
    }
    cur = nxt;
    nxt = drawNext(cur);
    locked = false;
    showCard();
    paintField();
  }
  function rightPick(pick) {
    var up = nxt.empirical_score > cur.empirical_score;
    var same = nxt.empirical_score === cur.empirical_score;
    if (pick === "higher") return same || up;
    if (pick === "lower") return same || nxt.empirical_score < cur.empirical_score;
    return false;
  }
  function sendMove(pick) {
    var match = window.LMN_MATCH;
    if (!match || !window.LMN_PID) return Promise.resolve(null);
    return fetch("queue.php", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ op: "move", pid: window.LMN_PID, match: match.id, round: round, pick: pick })
    }).then(function (res) { return res.json(); }).catch(function () { return null; });
  }
  function guess(higher) {
    if (locked || you.out || !nxt) return;
    locked = true;
    round += 1;
    var token = round;
    rivals.forEach(function (r) { r._done = false; });
    mark(you, rightPick(higher ? "higher" : "lower"));
    paintField();
    sendMove(higher ? "higher" : "lower");
    var movedOn = false;
    function maybeAdvance() {
      if (movedOn || token !== round) return;
      var still = rivals.some(function (r) { return !r.out && !r._done; });
      if (still) return;
      movedOn = true;
      advance();
    }
    rivals.forEach(function (r) {
      if (r.out || r.human) return;
      setTimeout(function () {
        if (token !== round || r._done) return;
        r._done = true;
        mark(r, Math.random() < r.skill);
        paintField();
        maybeAdvance();
      }, r.delay);
    });
    var humans = rivals.filter(function (r) { return r.human && !r.out; });
    if (!humans.length) { maybeAdvance(); return; }
    var started = Date.now();
    function tick() {
      if (token !== round || movedOn) return;
      sendMove(higher ? "higher" : "lower").then(function (data) {
        var moves = data && data.match && data.match.moves && data.match.moves[String(round)];
        humans.forEach(function (h) {
          if (h._done) return;
          var pick = moves && moves[h.pid];
          if (!pick) return;
          h._done = true;
          mark(h, rightPick(pick));
        });
        var waiting = humans.some(function (h) { return !h._done; });
        if (waiting && Date.now() - started > 9000) {
          humans.forEach(function (h) {
            if (!h._done) { h._done = true; mark(h, false); }
          });
          waiting = false;
        }
        paintField();
        if (!waiting) maybeAdvance();
        else setTimeout(tick, 700);
      });
    }
    tick();
  }
  function boot() {
    you.lives = 2; you.pts = 0; you.out = false; you.note = "";
    rivals.forEach(function (r) { r.lives = 2; r.pts = 0; r.out = false; r.note = ""; });
    round = 0;
    locked = false;
    cur = pool[Math.floor(Math.random() * pool.length)];
    nxt = drawNext(cur);
    document.getElementById("higher-end").innerHTML = "";
    showCard();
    paintField();
  }
  document.getElementById("higher-up").onclick = function () { guess(true); };
  document.getElementById("higher-down").onclick = function () { guess(false); };
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
    if (pool.length < 2) throw new Error("short");
    window.LMN_BEGIN = function (match) {
      var by = {};
      (match.seats || []).forEach(function (s) { by[s.role] = s; });
      function one(role, fallbackSkill, delay) {
        var s = by[role] || { kind: "ai", name: role, skill: fallbackSkill, pid: "" };
        return { name: s.name, skill: s.kind === "ai" ? (s.skill || fallbackSkill) : 0, delay: delay, human: s.kind === "human", pid: s.pid || "", lives: 2, pts: 0, out: false, note: "", role: role, _done: false };
      }
      rivals = [one("teammate", 0.76, 680), one("enemy", 0.58, 400), one("enemy2", 0.4, 520)];
      boot();
    };
  }).catch(function () {
    document.getElementById("higher-now").innerHTML = "<h2>The catalog did not load.</h2>";
  });
})();
