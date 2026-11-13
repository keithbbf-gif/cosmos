(function () {
  var STAKE = 10;
  var pool = [];
  var hand = [];
  var picked = [];
  var busy = false;

  function purse() {
    return window.LMNPurse ? window.LMNPurse.get() : 0;
  }

  function setPurse(n) {
    if (window.LMNPurse) window.LMNPurse.set(n);
  }

  function esc(value) {
    return String(value == null || value === "" ? "\u2014" : value).replace(/[&<>"]/g, function (ch) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[ch];
    });
  }

  function shuffle(list) {
    var a = list.slice();
    for (var i = a.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var t = a[i]; a[i] = a[j]; a[j] = t;
    }
    return a;
  }

  function roster(board) {
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

  function best(team, fn) {
    var top = team[0];
    team.forEach(function (row) {
      if (fn(row, top) > 0) top = row;
    });
    return top;
  }

  function deal() {
    busy = false;
    picked = [];
    hand = shuffle(pool).slice(0, 6);
    var box = document.getElementById("hand");
    box.innerHTML = "";
    hand.forEach(function (row, index) {
      var b = document.createElement("button");
      b.type = "button";
      b.className = "pick";
      b.innerHTML = "<strong>" + esc(row.name) + "</strong><p class=\"price\">score " + esc(row.empirical_score) +
        " \u00b7 in " + (typeof row.prompt_price_per_m === "number" ? "$" + row.prompt_price_per_m : "\u2014") +
        " \u00b7 ctx " + esc(row.context_length) + "</p><p class=\"secondary\">" + esc(row.weights) + "</p>";
      b.addEventListener("click", function () { toggle(index, b); });
      box.appendChild(b);
    });
    document.getElementById("arena").innerHTML = "";
    syncFight();
  }

  function toggle(index, button) {
    if (busy) return;
    var at = picked.indexOf(index);
    if (at >= 0) {
      picked.splice(at, 1);
      button.className = "pick";
    } else if (picked.length < 3) {
      picked.push(index);
      button.className = "pick on";
    }
    syncFight();
  }

  function syncFight() {
    var btn = document.getElementById("fight");
    btn.disabled = busy || picked.length !== 3;
    btn.textContent = picked.length === 3 ? "Stake 10 and watch" : "Pick 3 of 6";
  }

  function lane(title, yours, theirs, youWin, note) {
    return '<div class="bout-lane"><div class="fighter ' + (youWin ? "win" : "lose") + '"><strong>You</strong><p>' +
      esc(yours.name) + "</p><p class=\"price\">" + esc(note.you) + '</p></div><div class="lane-mid">' + esc(title) +
      '</div><div class="fighter ' + (youWin ? "lose" : "win") + '"><strong>Them</strong><p>' + esc(theirs.name) +
      "</p><p class=\"price\">" + esc(note.them) + "</p></div></div>";
  }

  function fight() {
    if (busy || picked.length !== 3) return;
    if (purse() < STAKE) {
      document.getElementById("arena").innerHTML = "<p>You need 10 game tokens. The shelf is under the hand.</p>";
      var shop = document.getElementById("in-game-shop");
      if (shop && shop.scrollIntoView) shop.scrollIntoView({ behavior: "smooth", block: "start" });
      return;
    }
    busy = true;
    syncFight();
    setPurse(purse() - STAKE);
    var mine = picked.map(function (i) { return hand[i]; });
    var used = {};
    mine.forEach(function (row) { used[row.dossier_id || row.name] = 1; });
    var rest = shuffle(pool.filter(function (row) { return !used[row.dossier_id || row.name]; }));
    function pull(mode) {
      rest.sort(function (a, b) {
        if (mode === "score") return b.empirical_score - a.empirical_score;
        if (mode === "price") {
          var ap = typeof a.prompt_price_per_m === "number" ? a.prompt_price_per_m : 9999;
          var bp = typeof b.prompt_price_per_m === "number" ? b.prompt_price_per_m : 9999;
          return ap - bp;
        }
        return (b.context_length || 0) - (a.context_length || 0);
      });
      var team = rest.splice(0, Math.min(3, rest.length));
      return team;
    }
    var seats = [
      { name: "You", you: true, team: mine, pts: 0 },
      { name: "Sprinter", team: pull("score"), pts: 0 },
      { name: "Librarian", team: pull("price"), pts: 0 },
      { name: "Novelist", team: pull("reach"), pts: 0 }
    ].filter(function (s) { return s.team.length; });
    function metric(team, mode) {
      var top = team[0];
      team.forEach(function (row) {
        if (mode === "score" && row.empirical_score > top.empirical_score) top = row;
        if (mode === "price") {
          var rp = typeof row.prompt_price_per_m === "number" ? row.prompt_price_per_m : 9999;
          var tp = typeof top.prompt_price_per_m === "number" ? top.prompt_price_per_m : 9999;
          if (rp < tp) top = row;
        }
        if (mode === "reach" && (row.context_length || 0) > (top.context_length || 0)) top = row;
      });
      if (mode === "score") return { row: top, n: top.empirical_score, text: "score " + top.empirical_score };
      if (mode === "price") return { row: top, n: typeof top.prompt_price_per_m === "number" ? -top.prompt_price_per_m : -9999, text: "in " + top.prompt_price_per_m };
      return { row: top, n: top.context_length || 0, text: "ctx " + top.context_length };
    }
    var rounds = [
      { title: "Score", mode: "score" },
      { title: "Price", mode: "price" },
      { title: "Reach", mode: "reach" }
    ];
    var arena = document.getElementById("arena");
    arena.innerHTML = "<p class=\"secondary\">Four squads. One lane at a time. Best number takes 3, then 2, then 1.</p>";
    var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var step = 0;
    function show() {
      var round = rounds[step];
      var ranked = seats.map(function (s) {
        var m = metric(s.team, round.mode);
        return { seat: s, row: m.row, n: m.n, text: m.text };
      }).sort(function (a, b) { return b.n - a.n; });
      var award = [3, 2, 1, 0];
      var html = "<h3>" + esc(round.title) + "</h3><div class=\"field\">";
      ranked.forEach(function (item, i) {
        item.seat.pts += award[i] || 0;
        html += "<div class=\"seat-row" + (item.seat.you ? " you" : "") + "\"><strong>" + esc(item.seat.name) + " +" + (award[i] || 0) + "</strong><p>" + esc(item.row.name) + "</p><p class=\"price\">" + esc(item.text) + "</p></div>";
      });
      html += "</div>";
      arena.insertAdjacentHTML("beforeend", html);
      step += 1;
      if (step < rounds.length) {
        if (reduce) show();
        else setTimeout(show, 800);
        return;
      }
      var board = seats.slice().sort(function (a, b) { return b.pts - a.pts; });
      var you = seats.filter(function (s) { return s.you; })[0];
      var won = you && board[0].name === "You" && (board.length < 2 || board[0].pts > board[1].pts);
      var tied = you && board[0].pts === you.pts && board.filter(function (s) { return s.pts === you.pts; }).length > 1;
      if (won) setPurse(purse() + STAKE * 2);
      else if (tied) setPurse(purse() + STAKE);
      if (window.LMN_SAVE) {
        window.LMN_SAVE({
          game: "derby",
          event: "match",
          models: seats.reduce(function (all, s) { return all.concat((s.team || []).map(window.LMN_MODEL)); }, []),
          outcome: { winner: won ? "you" : (tied ? "tie" : "field"), table: board.map(function (s) { return { name: s.you ? "you" : s.name, points: s.pts, models: (s.team || []).map(function (r) { return r.dossier_id || r.name; }) }; }) }
        });
      }
      var headline = won ? "You take the table. Stake comes back doubled." : (tied ? "Tie for the lead. Stake comes back." : board[0].name + " takes the table. The stake stays down.");
      arena.insertAdjacentHTML("beforeend", "<h2>" + esc(headline) + "</h2><p class=\"secondary\">" + board.map(function (s) { return esc(s.name) + " " + s.pts; }).join(" \u00b7 ") + "</p>");
      busy = false;
      syncFight();
    }
    if (reduce) show();
    else setTimeout(show, 400);
  }

  fetch("board.json")
    .then(function (res) { if (!res.ok) throw new Error("catalog"); return res.json(); })
    .then(function (board) {
      pool = roster(board);
      document.getElementById("fight").onclick = fight;
      window.LMN_BEGIN = function (match) {
        var line = (match.seats || []).map(function (s) {
          return s.role + " " + s.name + (s.kind === "human" ? "" : " AI");
        }).join(" · ");
        document.getElementById("arena").innerHTML = "<p class=\"secondary\">" + line + "</p>";
        deal();
      };
      document.getElementById("redeal").onclick = function () { if (!busy) deal(); };
    })
    .catch(function () {
      document.getElementById("hand").innerHTML = "<p>The catalog did not load.</p>";
    });
})();
