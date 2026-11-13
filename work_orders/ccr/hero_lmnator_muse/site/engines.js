(function () {
  function esc(v) {
    return String(v == null ? "" : v).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }
  function rnd(arr) { return arr[Math.floor(Math.random() * arr.length)]; }
  function names() {
    var rows = window.LMN_MODELS || [];
    var out = [];
    rows.forEach(function (r) { if (r && r.name && out.indexOf(r.name) < 0) out.push(r.name); });
    if (out.length < 4) return ["Librarian", "Sprinter", "Novelist", "Clerk", "Old Hand", "Understudy"];
    return out;
  }
  function modelRows() {
    var rows = (window.LMN_MODELS || []).filter(function (r) { return r && r.name; });
    return rows.length ? rows : [{ name: "Librarian", empirical_score: 40 }, { name: "Sprinter", empirical_score: 55 }, { name: "Novelist", empirical_score: 22 }];
  }
  function save(def, outcome, picked) {
    if (!window.LMN_SAVE) return;
    window.LMN_SAVE({
      game: def.id,
      event: "arcade",
      models: (picked || modelRows().slice(0, 4)).map(function (r) { return window.LMN_MODEL ? window.LMN_MODEL(r) : { name: r.name || r }; }),
      outcome: outcome
    });
  }
  function shell(root, def) {
    root.innerHTML = "";
    var box = document.createElement("div");
    var pay = "";
    try {
      var first = localStorage.getItem("lmn-first-play");
      if (!first) localStorage.setItem("lmn-first-play", String(Date.now()));
      else if ((Date.now() - Number(first)) > 14 * 86400000) pay = "<p class=\"secondary\">If you ever want more benches, TokenCenter has them. No rush.</p>";
    } catch (e) {}
    box.innerHTML = '<p class="kicker">' + (def.players === "multi" ? "MULTIPLAYER" : "SINGLE") + " · AFTER " + esc(def.inspired) + "</p><h2>" + esc(def.title) + "</h2><p class=\"secondary\">" + esc(def.better) + "</p><p class=\"chip-count\" id=\"gstat\"></p><div id=\"gstage\"></div>" + pay + (def.players === "multi" ? '<div id="lobby" data-game="' + esc(def.id) + '"></div>' : "");
    root.appendChild(box);
    if (def.players === "multi" && window.LMN_MOUNT_LOBBY) window.LMN_MOUNT_LOBBY(box.querySelector("#lobby"));
    return { stat: box.querySelector("#gstat"), stage: box.querySelector("#gstage") };
  }
  function endLine(ui, text) {
    var p = document.createElement("p");
    p.innerHTML = "<strong>" + esc(text) + "</strong>";
    ui.stage.appendChild(p);
  }

  function match3(def, root) {
    var ui = shell(root, def);
    var kinds = names().slice(0, 5);
    var w = 6, h = 5, cells = [], score = 0, left = def.lives || 5;
    function draw() {
      ui.stat.textContent = "Cleared " + score + " / " + (def.goal || 12) + " · misses " + left;
      ui.stage.innerHTML = "";
      var grid = document.createElement("div");
      grid.style.cssText = "display:grid;grid-template-columns:repeat(6,1fr);gap:4px";
      cells.forEach(function (name, i) {
        var b = document.createElement("button");
        b.type = "button";
        b.className = "tile";
        b.style.minHeight = "52px";
        b.style.fontSize = "12px";
        b.textContent = name.split(" ")[0];
        b.onclick = function () { tap(i); };
        grid.appendChild(b);
      });
      ui.stage.appendChild(grid);
    }
    function tap(i) {
      var col = i % w, row = Math.floor(i / w);
      var sib = [i - 1, i + 1, i - w, i + w].filter(function (j) {
        if (j < 0 || j >= cells.length) return false;
        if (Math.abs((j % w) - col) + Math.abs(Math.floor(j / w) - row) !== 1) return false;
        return true;
      });
      var leftOk = col > 0 && cells[i - 1] === cells[i];
      var rightOk = col < w - 1 && cells[i + 1] === cells[i];
      var upOk = row > 0 && cells[i - w] === cells[i];
      var downOk = row < h - 1 && cells[i + w] === cells[i];
      var line = [];
      if (leftOk && rightOk) line = [i - 1, i, i + 1];
      else if (upOk && downOk) line = [i - w, i, i + w];
      if (line.length === 3) {
        line.forEach(function (j) { cells[j] = rnd(kinds); });
        score += 1;
      } else left -= 1;
      draw();
      if (score >= (def.goal || 12)) { endLine(ui, "Board clear."); save(def, { result: "clear", score: score }); }
      else if (left <= 0) { endLine(ui, "Out of misses."); save(def, { result: "miss", score: score }); }
    }
    for (var n = 0; n < w * h; n++) cells.push(rnd(kinds));
    draw();
  }

  function blast(def, root) {
    var ui = shell(root, def);
    var kinds = names().slice(0, 4);
    var cells = [], score = 0;
    for (var i = 0; i < 36; i++) cells.push(rnd(kinds));
    function flood(start, bag) {
      var want = cells[start], seen = {}, stack = [start];
      while (stack.length) {
        var i = stack.pop();
        if (seen[i] || cells[i] !== want) continue;
        seen[i] = 1; bag.push(i);
        [i - 1, i + 1, i - 6, i + 6].forEach(function (j) {
          if (j < 0 || j >= cells.length) return;
          if (Math.abs((j % 6) - (i % 6)) + Math.abs(Math.floor(j / 6) - Math.floor(i / 6)) !== 1) return;
          stack.push(j);
        });
      }
    }
    function draw() {
      ui.stat.textContent = "Groups " + score + " / " + (def.goal || 8);
      ui.stage.innerHTML = "";
      var grid = document.createElement("div");
      grid.style.cssText = "display:grid;grid-template-columns:repeat(6,1fr);gap:4px";
      cells.forEach(function (name, i) {
        var b = document.createElement("button");
        b.type = "button"; b.className = "tile"; b.style.minHeight = "48px"; b.style.fontSize = "11px";
        b.textContent = name.split(" ")[0];
        b.onclick = function () {
          var bag = []; flood(i, bag);
          if (bag.length < 2) return;
          bag.forEach(function (j) { cells[j] = rnd(kinds); });
          score += 1; draw();
          if (score >= (def.goal || 8)) { endLine(ui, "Field cleared."); save(def, { result: "clear", score: score }); }
        };
        grid.appendChild(b);
      });
      ui.stage.appendChild(grid);
    }
    draw();
  }

  function runner(def, root) {
    var ui = shell(root, def);
    var y = 0, vy = 0, x = 0, alive = true, obstacles = [];
    var goal = (def.goal || 20) * 40;
    ui.stage.innerHTML = '<div id="run" style="position:relative;height:180px;background:#0B1220;border-radius:16px;overflow:hidden"></div><button type="button" class="btn thumb" id="jump">Jump</button>';
    var field = ui.stage.querySelector("#run");
    var guy = document.createElement("div");
    guy.style.cssText = "position:absolute;left:24px;width:28px;height:28px;border-radius:8px;background:#A5BB00";
    field.appendChild(guy);
    function frame() {
      if (!alive) return;
      vy -= 0.4; y = Math.max(0, y + vy);
      x += 2 + (def.speed || 1);
      if (Math.random() < 0.02) obstacles.push({ x: 320 });
      obstacles.forEach(function (o) { o.x -= 3 + (def.speed || 1); });
      obstacles = obstacles.filter(function (o) { return o.x > -20; });
      guy.style.bottom = (16 + y) + "px";
      field.querySelectorAll(".ob").forEach(function (n) { n.remove(); });
      obstacles.forEach(function (o) {
        var d = document.createElement("div");
        d.className = "ob";
        d.style.cssText = "position:absolute;bottom:16px;width:18px;height:36px;background:#FF7A7A;border-radius:4px;left:" + o.x + "px";
        field.appendChild(d);
        if (o.x < 48 && o.x > 20 && y < 20) alive = false;
      });
      ui.stat.textContent = "Run " + Math.floor(x / 40) + " / " + (def.goal || 20);
      if (!alive) { endLine(ui, "Caught."); save(def, { result: "hit", distance: Math.floor(x / 40) }); return; }
      if (x >= goal) { alive = false; endLine(ui, "Finished."); save(def, { result: "finish", distance: def.goal || 20 }); return; }
      requestAnimationFrame(frame);
    }
    ui.stage.querySelector("#jump").onclick = function () { if (y < 2) vy = 8; };
    frame();
  }

  function stack(def, root) {
    var ui = shell(root, def);
    var w = 80, pos = 0, dir = 1, dropped = 0, goal = def.goal || 8, timer;
    ui.stage.innerHTML = '<div id="stk" style="position:relative;height:220px;background:#0B1220;border-radius:16px"></div><button type="button" class="btn thumb" id="drop">Drop</button>';
    var field = ui.stage.querySelector("#stk");
    var block = document.createElement("div");
    block.style.cssText = "position:absolute;top:12px;height:16px;background:#A5BB00;border-radius:4px";
    field.appendChild(block);
    function place() {
      block.style.width = w + "%";
      block.style.left = pos + "%";
    }
    function tick() {
      pos += dir * (1.2 + (def.speed || 1));
      if (pos < 0 || pos > 100 - w) dir *= -1;
      place();
    }
    timer = setInterval(tick, 30);
    ui.stage.querySelector("#drop").onclick = function () {
      dropped += 1;
      w = Math.max(18, w - 6);
      ui.stat.textContent = "Height " + dropped + " / " + goal;
      if (dropped >= goal) { clearInterval(timer); endLine(ui, "Tower stands."); save(def, { result: "stack", height: dropped }); }
    };
    place();
  }

  function merge(def, root) {
    var ui = shell(root, def);
    var slots = [1, 1, 0, 0, 2, 0];
    var goal = def.goal || 6;
    function draw() {
      var best = Math.max.apply(null, slots);
      ui.stat.textContent = "Tier " + best + " / " + goal;
      ui.stage.innerHTML = "";
      var row = document.createElement("div");
      row.className = "tile-grid";
      slots.forEach(function (n, i) {
        var b = document.createElement("button");
        b.type = "button"; b.className = "tile"; b.style.minHeight = "72px";
        b.textContent = n ? (names()[n % names().length].split(" ")[0] + " " + n) : "+";
        b.onclick = function () {
          var j = slots.findIndex(function (m, k) { return k !== i && m === n && n > 0; });
          if (j < 0 && n === 0) { slots[i] = 1; }
          else if (j >= 0) { slots[j] = 0; slots[i] = n + 1; }
          draw();
          if (best >= goal || Math.max.apply(null, slots) >= goal) { endLine(ui, "Merged."); save(def, { result: "merge", tier: Math.max.apply(null, slots) }); }
        };
        row.appendChild(b);
      });
      ui.stage.appendChild(row);
    }
    draw();
  }

  function memory(def, root) {
    var ui = shell(root, def);
    var deck = names().slice(0, 6);
    var cards = deck.concat(deck).sort(function () { return Math.random() - 0.5; });
    var open = [], gone = {}, flips = 0, left = def.lives || 8;
    function draw() {
      ui.stat.textContent = "Pairs left " + (deck.length - Object.keys(gone).length / 2) + " · flips " + left;
      ui.stage.innerHTML = "";
      var grid = document.createElement("div");
      grid.className = "tile-grid";
      cards.forEach(function (name, i) {
        var b = document.createElement("button");
        b.type = "button"; b.className = "tile"; b.style.minHeight = "64px"; b.style.fontSize = "13px";
        b.textContent = gone[i] || open.indexOf(i) >= 0 ? name.split(" ")[0] : "?";
        b.onclick = function () {
          if (gone[i] || open.indexOf(i) >= 0 || open.length === 2) return;
          open.push(i); draw();
          if (open.length === 2) {
            left -= 1;
            if (cards[open[0]] === cards[open[1]]) { gone[open[0]] = gone[open[1]] = 1; }
            setTimeout(function () { open = []; draw(); if (Object.keys(gone).length === cards.length) { endLine(ui, "All pairs."); save(def, { result: "pairs" }); } else if (left <= 0) { endLine(ui, "Out of flips."); save(def, { result: "miss" }); } }, 500);
          }
        };
        grid.appendChild(b);
      });
      ui.stage.appendChild(grid);
    }
    draw();
  }

  function snake(def, root) {
    var ui = shell(root, def);
    var n = 12, body = [{ x: 3, y: 3 }], dir = { x: 1, y: 0 }, food = { x: 8, y: 6 }, alive = true;
    var goal = def.goal || 8;
    ui.stage.innerHTML = '<div id="sn" style="display:grid;grid-template-columns:repeat(12,1fr);gap:1px;background:#0B1220;padding:4px;border-radius:12px"></div><div class="pit-bar"><button type="button" class="btn" id="l">Left</button><button type="button" class="btn" id="r">Right</button><button type="button" class="btn" id="u">Up</button></div>';
    var grid = ui.stage.querySelector("#sn");
    function turn(x, y) { if (dir.x + x === 0 && dir.y + y === 0) return; dir = { x: x, y: y }; }
    ui.stage.querySelector("#l").onclick = function () { turn(-1, 0); };
    ui.stage.querySelector("#r").onclick = function () { turn(1, 0); };
    ui.stage.querySelector("#u").onclick = function () { turn(0, -1); };
    function step() {
      if (!alive) return;
      var head = { x: body[0].x + dir.x, y: body[0].y + dir.y };
      if (head.x < 0 || head.y < 0 || head.x >= n || head.y >= n || body.some(function (p) { return p.x === head.x && p.y === head.y; })) {
        alive = false; endLine(ui, "Stopped at " + body.length + "."); save(def, { result: "stop", length: body.length }); return;
      }
      body.unshift(head);
      if (head.x === food.x && head.y === food.y) food = { x: Math.floor(Math.random() * n), y: Math.floor(Math.random() * n) };
      else body.pop();
      ui.stat.textContent = "Length " + body.length + " / " + goal;
      grid.innerHTML = "";
      for (var y = 0; y < n; y++) for (var x = 0; x < n; x++) {
        var c = document.createElement("div");
        var on = body.some(function (p) { return p.x === x && p.y === y; });
        c.style.cssText = "aspect-ratio:1;border-radius:2px;background:" + (on ? "#A5BB00" : (food.x === x && food.y === y ? "#FFB52E" : "#121B2E"));
        grid.appendChild(c);
      }
      if (body.length >= goal) { alive = false; endLine(ui, "Fed."); save(def, { result: "fed", length: body.length }); return; }
      setTimeout(step, Math.max(120, 220 - (def.speed || 1) * 20));
    }
    step();
  }

  function breakout(def, root) {
    var ui = shell(root, def);
    ui.stage.innerHTML = '<canvas id="cv" width="320" height="200" style="width:100%;background:#0B1220;border-radius:16px;touch-action:none"></canvas>';
    var cv = ui.stage.querySelector("#cv"), ctx = cv.getContext("2d");
    var pad = 140, ball = { x: 160, y: 140, vx: 2, vy: -2 }, bricks = [], left = 0;
    for (var i = 0; i < 18; i++) bricks.push({ x: 8 + (i % 6) * 52, y: 16 + Math.floor(i / 6) * 18, on: 1 });
    function loop() {
      ball.x += ball.vx * (def.speed || 1); ball.y += ball.vy * (def.speed || 1);
      if (ball.x < 6 || ball.x > 314) ball.vx *= -1;
      if (ball.y < 6) ball.vy *= -1;
      if (ball.y > 188) { endLine(ui, "Ball dropped."); save(def, { result: "drop", left: left }); return; }
      if (ball.y > 170 && ball.x > pad && ball.x < pad + 64) ball.vy = -Math.abs(ball.vy);
      left = 0;
      bricks.forEach(function (b) {
        if (!b.on) return; left += 1;
        if (ball.x > b.x && ball.x < b.x + 48 && ball.y > b.y && ball.y < b.y + 14) { b.on = 0; ball.vy *= -1; }
      });
      ctx.fillStyle = "#0B1220"; ctx.fillRect(0, 0, 320, 200);
      ctx.fillStyle = "#A5BB00"; ctx.fillRect(pad, 176, 64, 8);
      ctx.beginPath(); ctx.arc(ball.x, ball.y, 5, 0, 7); ctx.fill();
      ctx.fillStyle = "#FFB52E";
      bricks.forEach(function (b) { if (b.on) ctx.fillRect(b.x, b.y, 48, 12); });
      ui.stat.textContent = "Bricks " + left;
      if (!left) { endLine(ui, "Cleared."); save(def, { result: "clear" }); return; }
      requestAnimationFrame(loop);
    }
    function move(clientX) {
      var r = cv.getBoundingClientRect();
      pad = Math.max(0, Math.min(256, (clientX - r.left) / r.width * 320 - 32));
    }
    cv.addEventListener("pointermove", function (e) { move(e.clientX); });
    cv.addEventListener("pointerdown", function (e) { move(e.clientX); });
    loop();
  }

  function whack(def, root) {
    var ui = shell(root, def);
    var hits = 0, miss = 0, goal = def.goal || 8, lives = def.lives || 5, hole = 0;
    function draw() {
      ui.stat.textContent = "Hits " + hits + " / " + goal + " · misses " + miss + "/" + lives;
      ui.stage.innerHTML = "";
      var grid = document.createElement("div");
      grid.className = "tile-grid";
      for (var i = 0; i < 6; i++) {
        var b = document.createElement("button");
        b.type = "button"; b.className = "tile"; b.style.minHeight = "72px";
        b.textContent = i === hole ? rnd(names()).split(" ")[0] : "";
        (function (i) {
          b.onclick = function () {
            if (i === hole) hits += 1; else miss += 1;
            hole = Math.floor(Math.random() * 6);
            if (hits >= goal) { endLine(ui, "Caught."); save(def, { result: "caught", hits: hits }); return; }
            if (miss >= lives) { endLine(ui, "Too many misses."); save(def, { result: "miss", hits: hits }); return; }
            draw();
          };
        })(i);
        grid.appendChild(b);
      }
      ui.stage.appendChild(grid);
    }
    draw();
  }

  function slide(def, root) {
    var ui = shell(root, def);
    var tiles = [1, 2, 3, 4, 5, 6, 7, 8, 0];
    for (var k = 0; k < 20; k++) tiles.splice(Math.floor(Math.random() * 9), 0, tiles.pop());
    function won() { return tiles.slice(0, 8).every(function (n, i) { return n === i + 1; }); }
    function draw() {
      ui.stat.textContent = "Slide the gap";
      ui.stage.innerHTML = "";
      var grid = document.createElement("div");
      grid.style.cssText = "display:grid;grid-template-columns:repeat(3,1fr);gap:6px";
      tiles.forEach(function (n, i) {
        var b = document.createElement("button");
        b.type = "button"; b.className = "tile"; b.style.minHeight = "64px";
        b.textContent = n ? n : "";
        b.onclick = function () {
          var z = tiles.indexOf(0);
          if (Math.abs(z - i) === 1 || Math.abs(z - i) === 3) {
            tiles[z] = n; tiles[i] = 0; draw();
            if (won()) { endLine(ui, "Solved."); save(def, { result: "solved" }); }
          }
        };
        grid.appendChild(b);
      });
      ui.stage.appendChild(grid);
    }
    draw();
  }

  function word(def, root) {
    var ui = shell(root, def);
    var word = rnd(names()).replace(/[^a-z]/ig, "").slice(0, 6).toUpperCase() || "MODEL";
    var letters = word.split("").sort(function () { return Math.random() - 0.5; });
    var built = "";
    function draw() {
      ui.stat.textContent = built;
      ui.stage.innerHTML = "";
      var row = document.createElement("div");
      row.className = "pit-bar";
      letters.forEach(function (ch, i) {
        var b = document.createElement("button");
        b.type = "button"; b.className = "btn"; b.textContent = ch;
        b.onclick = function () { built += ch; letters.splice(i, 1); if (built === word) { endLine(ui, "Named."); save(def, { result: "word", word: word }); } else draw(); };
        row.appendChild(b);
      });
      ui.stage.appendChild(row);
    }
    draw();
  }

  function idle(def, root) {
    var ui = shell(root, def);
    var coins = 0, power = 1, goal = (def.goal || 20) * 5;
    ui.stage.innerHTML = '<button type="button" class="btn thumb" id="tap">Tap</button><button type="button" class="btn thumb" id="up" style="background:transparent;color:#F6F2EA;border:1px solid rgba(246,242,234,.28)">Upgrade (10)</button>';
    function paint() { ui.stat.textContent = coins + " / " + goal + " · power " + power; }
    ui.stage.querySelector("#tap").onclick = function () { coins += power; paint(); if (coins >= goal) { endLine(ui, "Shift done."); save(def, { result: "idle", coins: coins }); } };
    ui.stage.querySelector("#up").onclick = function () { if (coins >= 10) { coins -= 10; power += 1; paint(); } };
    paint();
  }

  function cards(def, root) {
    var ui = shell(root, def);
    var rows = modelRows(), score = 0, goal = def.goal || 5, left = def.lives || 4;
    function round() {
      var a = rnd(rows), b = rnd(rows);
      ui.stat.textContent = "Calls " + score + " / " + goal + " · misses " + left;
      ui.stage.innerHTML = "<p>Which score is higher?</p>";
      [a, b].forEach(function (row) {
        var btn = document.createElement("button");
        btn.type = "button"; btn.className = "btn thumb";
        btn.textContent = row.name;
        btn.onclick = function () {
          var win = (row.empirical_score || 0) >= Math.max(a.empirical_score || 0, b.empirical_score || 0);
          if (win) score += 1; else left -= 1;
          ui.stage.insertAdjacentHTML("beforeend", "<p>" + esc(a.name) + " " + (a.empirical_score || 0) + " · " + esc(b.name) + " " + (b.empirical_score || 0) + "</p>");
          if (score >= goal) { endLine(ui, "Called it."); save(def, { result: "cards", score: score }, [a, b]); }
          else if (left <= 0) { endLine(ui, "Missed."); save(def, { result: "miss", score: score }, [a, b]); }
          else setTimeout(round, 600);
        };
        ui.stage.appendChild(btn);
      });
    }
    round();
  }

  function lane(def, root) {
    var ui = shell(root, def);
    var you = 20, them = 20;
    ui.stage.innerHTML = '<button type="button" class="btn thumb" id="hit">Strike</button>';
    function paint() { ui.stat.textContent = "You " + you + " · field " + them; }
    var foe = setInterval(function () {
      you -= 1 + Math.floor(def.speed || 1);
      paint();
      if (you <= 0) { clearInterval(foe); endLine(ui, "The field takes it."); save(def, { result: "loss" }); }
    }, 700);
    ui.stage.querySelector("#hit").onclick = function () {
      them -= 2;
      paint();
      if (them <= 0) { clearInterval(foe); endLine(ui, "You take the lane."); save(def, { result: "win" }); }
    };
    paint();
  }

  function board(def, root) {
    var ui = shell(root, def);
    var you = 0, them = 0, goal = def.goal || 12;
    ui.stage.innerHTML = '<button type="button" class="btn thumb" id="roll">Roll</button>';
    ui.stage.querySelector("#roll").onclick = function () {
      you += 1 + Math.floor(Math.random() * 3);
      them += 1 + Math.floor(Math.random() * 3);
      ui.stat.textContent = "You " + you + " · field " + them + " / " + goal;
      if (you >= goal || them >= goal) {
        var win = you >= them;
        endLine(ui, win ? "You land first." : "The field lands first.");
        save(def, { result: win ? "win" : "loss", you: you, them: them });
        ui.stage.querySelector("#roll").disabled = true;
      }
    };
  }

  function rhythm(def, root) {
    var ui = shell(root, def);
    var hits = 0, goal = def.goal || 8, lit = 0, lives = def.lives || 4;
    function draw() {
      ui.stat.textContent = "Hits " + hits + " / " + goal;
      ui.stage.innerHTML = "";
      var row = document.createElement("div");
      row.className = "tile-grid";
      for (var i = 0; i < 4; i++) {
        var b = document.createElement("button");
        b.type = "button"; b.className = "tile"; b.style.minHeight = "80px";
        b.style.background = i === lit ? "#A5BB00" : "#0B1220";
        b.style.color = i === lit ? "#070B14" : "#F6F2EA";
        b.textContent = i === lit ? "Hit" : "";
        (function (i) {
          b.onclick = function () {
            if (i === lit) hits += 1; else lives -= 1;
            lit = Math.floor(Math.random() * 4);
            if (hits >= goal) { endLine(ui, "In time."); save(def, { result: "rhythm", hits: hits }); return; }
            if (lives <= 0) { endLine(ui, "Off beat."); save(def, { result: "miss", hits: hits }); return; }
            draw();
          };
        })(i);
        row.appendChild(b);
      }
      ui.stage.appendChild(row);
    }
    draw();
  }

  function farm(def, root) {
    var ui = shell(root, def);
    var plots = [0, 0, 0], got = 0, goal = def.goal || 4;
    function draw() {
      ui.stat.textContent = "Harvests " + got + " / " + goal;
      ui.stage.innerHTML = "";
      var row = document.createElement("div");
      row.className = "tile-grid";
      plots.forEach(function (state, i) {
        var b = document.createElement("button");
        b.type = "button"; b.className = "tile"; b.style.minHeight = "80px";
        b.textContent = state === 0 ? "Plant" : (state === 1 ? "Growing" : "Harvest");
        b.onclick = function () {
          if (plots[i] === 0) { plots[i] = 1; setTimeout(function () { plots[i] = 2; draw(); }, 900 / (def.speed || 1)); }
          else if (plots[i] === 2) { plots[i] = 0; got += 1; if (got >= goal) { endLine(ui, "Harvested."); save(def, { result: "harvest", got: got }); return; } }
          draw();
        };
        row.appendChild(b);
      });
      ui.stage.appendChild(row);
    }
    draw();
  }

  function quiz(def, root) {
    cards(def, root);
  }

  var engines = { match3: match3, blast: blast, runner: runner, stack: stack, merge: merge, memory: memory, snake: snake, breakout: breakout, whack: whack, slide: slide, word: word, idle: idle, cards: cards, lane: lane, board: board, rhythm: rhythm, farm: farm, quiz: quiz };
  var caps = { match3: 12, blast: 8, runner: 24, stack: 8, merge: 6, memory: 8, snake: 10, breakout: 18, whack: 10, slide: 1, word: 1, idle: 80, cards: 5, lane: 20, board: 12, rhythm: 10, farm: 4, quiz: 5 };
  window.LMN_PLAY = function (def, root) {
    var play = {};
    Object.keys(def).forEach(function (k) { play[k] = def[k]; });
    var cap = caps[play.engine] || 12;
    if (typeof play.goal === "number" && play.goal > cap) play.goal = cap;
    if (typeof play.speed === "number" && play.speed > 4) play.speed = 3;
    (engines[play.engine] || idle)(play, root);
  };
})();
