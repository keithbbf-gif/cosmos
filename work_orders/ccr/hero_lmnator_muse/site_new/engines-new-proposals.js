/* engines-new-proposals.js
   PROPOSAL ONLY. This file does not modify site/engines.js and does not replace
   window.LMN_PLAY. Loading it does not change the arcade. Call the functions on
   window.LMN_ENGINES_NEW yourself.

   Why these exist, from the current engines.js:
   - snake has Left, Right, and Up. It has no Down control.
   - slide shuffles with 20 cut-point splices, which can be an illegal position,
     and it ignores goal, speed, and lives.
   - breakout always builds 18 bricks and ignores goal and lives. Speed scales the ball.
   - lane ignores goal. Both bars start at 20.
   - memory ignores goal. The deck is fixed at 6 pairs, and every pair attempt
     spends one life, including a match.
   - word ignores goal, speed, and lives, and the word is a catalog name.
   - quiz is an alias of cards. It asks which of two scores is higher.
   - stack counts every drop. It does not check whether the slab was centered.
   The functions below are the proposals for the first four of those limits.
   memory, word, quiz, and stack are described here and not reimplemented. */
(function () {
  function esc(v) {
    return String(v == null ? "" : v).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }
  function shell(root, def) {
    root.innerHTML = "";
    var box = document.createElement("div");
    box.innerHTML = '<p class="kicker">PROPOSAL · ' + esc(def.engine) + '</p><h2>' + esc(def.title || def.engine) + '</h2><p class="chip-count" id="gstat"></p><div id="gstage"></div>';
    root.appendChild(box);
    return { stat: box.querySelector("#gstat"), stage: box.querySelector("#gstage") };
  }
  function endLine(ui, text) {
    var p = document.createElement("p");
    p.innerHTML = "<strong>" + esc(text) + "</strong>";
    ui.stage.appendChild(p);
  }

  function snake4(def, root) {
    var ui = shell(root, def);
    var n = 12, body = [{ x: 3, y: 3 }], dir = { x: 1, y: 0 }, food = { x: 8, y: 6 }, alive = true;
    var goal = def.goal || 8;
    ui.stage.innerHTML = '<div id="sn" style="display:grid;grid-template-columns:repeat(12,1fr);gap:1px;background:#0B1220;padding:4px;border-radius:12px"></div><div class="pit-bar"><button type="button" class="btn" id="l">Left</button><button type="button" class="btn" id="r">Right</button><button type="button" class="btn" id="u">Up</button><button type="button" class="btn" id="d">Down</button></div>';
    var grid = ui.stage.querySelector("#sn");
    function turn(x, y) { if (dir.x + x === 0 && dir.y + y === 0) return; dir = { x: x, y: y }; }
    ui.stage.querySelector("#l").onclick = function () { turn(-1, 0); };
    ui.stage.querySelector("#r").onclick = function () { turn(1, 0); };
    ui.stage.querySelector("#u").onclick = function () { turn(0, -1); };
    ui.stage.querySelector("#d").onclick = function () { turn(0, 1); };
    function step() {
      if (!alive) return;
      var head = { x: body[0].x + dir.x, y: body[0].y + dir.y };
      if (head.x < 0 || head.y < 0 || head.x >= n || head.y >= n || body.some(function (p) { return p.x === head.x && p.y === head.y; })) {
        alive = false; endLine(ui, "Stopped at " + body.length + "."); return;
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
      if (body.length >= goal) { alive = false; endLine(ui, "Fed."); return; }
      setTimeout(step, Math.max(120, 220 - (def.speed || 1) * 20));
    }
    step();
  }

  function slideCounted(def, root) {
    var ui = shell(root, def);
    var scramble = (def.settings && def.settings.scramble) || 12;
    var tiles = [1, 2, 3, 4, 5, 6, 7, 8, 0];
    function neighbors(z) {
      var out = [];
      if (z % 3 > 0) out.push(z - 1);
      if (z % 3 < 2) out.push(z + 1);
      if (z >= 3) out.push(z - 3);
      if (z < 6) out.push(z + 3);
      return out;
    }
    var prev = -1;
    for (var k = 0; k < scramble; k++) {
      var z0 = tiles.indexOf(0);
      var opts = neighbors(z0).filter(function (j) { return j !== prev; });
      if (!opts.length) opts = neighbors(z0);
      var j = opts[Math.floor(Math.random() * opts.length)];
      tiles[z0] = tiles[j];
      tiles[j] = 0;
      prev = z0;
    }
    function won() { return tiles.slice(0, 8).every(function (n, i) { return n === i + 1; }); }
    function draw() {
      ui.stat.textContent = "Legal slides " + scramble;
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
            if (Math.abs(z - i) === 1 && Math.floor(z / 3) !== Math.floor(i / 3)) return;
            tiles[z] = n; tiles[i] = 0; draw();
            if (won()) endLine(ui, "Solved.");
          }
        };
        grid.appendChild(b);
      });
      ui.stage.appendChild(grid);
    }
    draw();
  }

  function breakoutRows(def, root) {
    var ui = shell(root, def);
    var bricksN = (def.settings && def.settings.bricks) || 18;
    if (bricksN < 6) bricksN = 6;
    if (bricksN > 24) bricksN = 24;
    ui.stage.innerHTML = '<canvas id="cv" width="320" height="200" style="width:100%;background:#0B1220;border-radius:16px;touch-action:none"></canvas>';
    var cv = ui.stage.querySelector("#cv"), ctx = cv.getContext("2d");
    var pad = 140, ball = { x: 160, y: 140, vx: 2, vy: -2 }, bricks = [], left = 0;
    for (var i = 0; i < bricksN; i++) bricks.push({ x: 8 + (i % 6) * 52, y: 16 + Math.floor(i / 6) * 18, on: 1 });
    var speed = def.speed || 1;
    function loop() {
      ball.x += ball.vx * speed; ball.y += ball.vy * speed;
      if (ball.x < 6 || ball.x > 314) ball.vx *= -1;
      if (ball.y < 6) ball.vy *= -1;
      if (ball.y > 188) { endLine(ui, "Ball dropped."); return; }
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
      ui.stat.textContent = "Bricks " + left + " / " + bricksN;
      if (!left) { endLine(ui, "Cleared."); return; }
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

  function laneBars(def, root) {
    var ui = shell(root, def);
    var bar = def.goal || 12;
    var you = bar, them = bar;
    var drain = 1 + Math.floor(def.speed || 1);
    ui.stage.innerHTML = '<button type="button" class="btn thumb" id="hit">Strike</button>';
    function paint() { ui.stat.textContent = "You " + you + " · field " + them + " · bar " + bar; }
    var foe = setInterval(function () {
      you -= drain;
      paint();
      if (you <= 0) { clearInterval(foe); endLine(ui, "The field takes it."); }
    }, 700);
    ui.stage.querySelector("#hit").onclick = function () {
      them -= 2;
      paint();
      if (them <= 0) { clearInterval(foe); endLine(ui, "You take the lane."); }
    };
    paint();
  }

  window.LMN_ENGINES_NEW = {
    snake4: snake4,
    slideCounted: slideCounted,
    breakoutRows: breakoutRows,
    laneBars: laneBars
  };
})();
