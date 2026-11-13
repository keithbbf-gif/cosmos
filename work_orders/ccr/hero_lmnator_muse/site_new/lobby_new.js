(function (root) {
  if (!root.document) return;
  var doc = root.document;
  var api = root.LMN_MOCK_QUEUE;
  var FILL_AFTER_S = api ? api.FILL_AFTER_S : 8;
  var MIN_SEATS = api ? api.MIN_SEATS : 2;
  var MAX_SEATS = api ? api.MAX_SEATS : 8;
  var mountSeq = 0;

  function pid() {
    var key = "lmn-pid";
    var id = "";
    try { id = localStorage.getItem(key) || ""; } catch (e) { id = ""; }
    if (!id) {
      id = "p" + Math.random().toString(36).slice(2) + Date.now().toString(36);
      try { localStorage.setItem(key, id); } catch (e2) {}
    }
    root.LMN_PID = id;
    return id;
  }

  function store() {
    if (!api) return null;
    if (!root.LMN_MOCK_STORE) root.LMN_MOCK_STORE = api.createStore();
    return root.LMN_MOCK_STORE;
  }

  function flag(name) {
    try {
      return new URLSearchParams(root.location.search).get(name) || "";
    } catch (e) {
      return "";
    }
  }

  function queryMode() {
    return flag("queue");
  }

  function probe() {
    var mode = queryMode();
    if (mode === "mock" || mode === "legacy") return Promise.resolve(mode);
    if (!api) return Promise.resolve("legacy");
    if (root.location.protocol === "file:" && mode !== "php") return Promise.resolve("mock");
    return fetch("queue.php", {
      method: "POST",
      headers: { "Content-Type": "application/json", "Accept": "application/json" },
      body: JSON.stringify({ op: "caps", pid: pid() })
    }).then(function (res) { return res.json(); }).then(function (data) {
      if (data && data.n_player === true) return "php";
      if (mode === "php") return "legacy";
      return "mock";
    }).catch(function () {
      return mode === "php" ? "down" : "mock";
    });
  }

  function gameRows() {
    var map = root.LMN_LOBBY_MAP;
    var seen = {};
    var rows = [];
    function add(def) {
      if (!def || !def.id || seen[def.id]) return;
      seen[def.id] = 1;
      rows.push(def);
    }
    if (map && map.priority && map.index) {
      map.priority.forEach(function (id) { add(map.index[id]); });
    }
    if (map && map.index) Object.keys(map.index).forEach(function (id) { add(map.index[id]); });
    (root.LMN_PACK || []).forEach(function (g) {
      add(map && map.resolve ? map.resolve(g) : { id: g.id, title: g.title, players: g.players, engine: g.engine });
    });
    return rows;
  }

  function profileFor(id) {
    var map = root.LMN_LOBBY_MAP;
    if (map && map.index && map.index[id]) return map.index[id];
    var found = null;
    (root.LMN_PACK || []).forEach(function (g) { if (g.id === id) found = g; });
    if (found && map && map.resolve) return map.resolve(found);
    if (found) return { id: found.id, title: found.title, players: found.players, min_players: MIN_SEATS, max_players: MAX_SEATS, default_seats: found.players === "multi" ? 4 : 2, layout: found.players === "multi" ? "2v2" : "ffa" };
    return { id: id, title: id, players: "", min_players: MIN_SEATS, max_players: MAX_SEATS, default_seats: 4, layout: "ffa" };
  }

  function esc(v) {
    return String(v == null ? "" : v).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  function mount(host) {
    if (!host) return;
    mountSeq += 1;
    var uid = "lmnq" + mountSeq;
    var desk = host.getAttribute("data-desk") === "1";
    var game = host.getAttribute("data-game") || (desk ? "m01" : "");
    var info = profileFor(game);
    var transport = "mock";
    var timer = null;
    var matchedId = "";

    host.innerHTML = "";
    var panel = doc.createElement("section");
    panel.className = "lmn-lobby card";
    panel.setAttribute("aria-label", desk ? "Matchmaking desk" : "Game lobby");
    host.appendChild(panel);

    function htmlForm() {
      var games = gameRows();
      var gameField = desk
        ? '<label class="lmn-field">Game <select class="lmn-game">' + games.map(function (g) {
          return '<option value="' + esc(g.id) + '"' + (g.id === game ? " selected" : "") + ">" + esc(g.id + " " + (g.title || "")) + "</option>";
        }).join("") + "</select></label>"
        : '<p class="lmn-game-name"><strong class="lmn-game-label"></strong></p>';
      return '<h2>' + (desk ? "Queue and lobby" : "Lobby") + '</h2>' +
        '<p class="secondary lmn-transport" role="status"></p>' +
        gameField +
        '<label class="lmn-field">Name <input class="lmn-name" maxlength="16" value="Player"></label>' +
        '<div class="lmn-n">' +
          '<label class="lmn-field">Seats <input class="lmn-seats" type="number" min="' + MIN_SEATS + '" max="' + MAX_SEATS + '" value="' + (info.default_seats || 4) + '"></label>' +
          '<label class="lmn-field lmn-layout-wrap">Table <select class="lmn-layout"><option value="ffa">Free for all</option><option value="2v2">Two teams of two</option></select></label>' +
          '<fieldset class="lmn-fill"><legend>Empty seats</legend>' +
            '<label><input type="radio" name="' + uid + '-fill" value="either" checked> People, then AI after ' + FILL_AFTER_S + ' seconds</label>' +
            '<label><input type="radio" name="' + uid + '-fill" value="human"> People only</label>' +
            '<label><input type="radio" name="' + uid + '-fill" value="ai"> AI only</label>' +
          "</fieldset>" +
          '<label class="lmn-field">Difficulty <select class="lmn-diff">' +
            '<option value="legacy">Current table (Librarian, Sprinter, Novelist)</option>' +
            '<option value="easy">Easy</option><option value="medium">Medium</option><option value="hard">Hard</option>' +
          "</select></label>" +
          '<div class="lmn-slots"></div>' +
          '<div class="pit-bar lmn-actions">' +
            '<button type="button" class="btn lmn-go">Join queue</button>' +
            '<button type="button" class="btn lmn-open">Open a lobby</button>' +
            '<button type="button" class="btn lmn-leave">Leave</button>' +
          "</div>" +
          '<div class="lmn-code-row"><label class="lmn-field">Code <input class="lmn-code" maxlength="6" autocapitalize="characters"></label>' +
            '<button type="button" class="btn lmn-join-code">Join code</button></div>' +
          '<div class="pit-bar lmn-mock-only">' +
            '<button type="button" class="btn lmn-practice">Seat a practice human</button>' +
            '<button type="button" class="btn lmn-fillnow">Fill empty seats now</button>' +
          "</div>" +
        "</div>" +
        '<div class="lmn-legacy" hidden>' +
          '<p><strong>Teammate</strong></p><div class="pit-bar">' +
            '<label class="btn"><input type="checkbox" class="lmn-th"> Human</label>' +
            '<label class="btn"><input type="checkbox" class="lmn-ta" checked> AI</label></div>' +
          '<p><strong>Enemy</strong></p><div class="pit-bar">' +
            '<label class="btn"><input type="checkbox" class="lmn-eh"> Human</label>' +
            '<label class="btn"><input type="checkbox" class="lmn-ea" checked> AI</label></div>' +
          '<p><button type="button" class="btn lmn-legacy-go">Play the live queue</button></p>' +
        "</div>" +
        '<p class="secondary lmn-status" role="status"></p>' +
        '<ol class="lmn-roster"></ol>';
    }

    panel.innerHTML = htmlForm();
    var status = panel.querySelector(".lmn-status");
    var transportNote = panel.querySelector(".lmn-transport");
    var roster = panel.querySelector(".lmn-roster");

    function say(text) { status.textContent = text; }

    function currentGame() {
      var sel = panel.querySelector(".lmn-game");
      return sel ? sel.value : game;
    }

    function seatsValue() {
      var n = parseInt(panel.querySelector(".lmn-seats").value, 10);
      var prof = profileFor(currentGame());
      var min = prof.min_players || MIN_SEATS;
      var max = prof.max_players || MAX_SEATS;
      if (!n || n < min) n = min;
      if (n > max) n = max;
      panel.querySelector(".lmn-seats").value = String(n);
      return n;
    }

    function paintGame() {
      var label = panel.querySelector(".lmn-game-label");
      var prof = profileFor(currentGame());
      if (label) label.textContent = (prof.title || currentGame()) + " · " + (prof.players || "lobby") + " · " + (prof.engine || "");
      var seats = panel.querySelector(".lmn-seats");
      seats.min = String(prof.min_players || MIN_SEATS);
      seats.max = String(prof.max_players || MAX_SEATS);
      seats.value = String(prof.default_seats || 4);
      var layout = panel.querySelector(".lmn-layout");
      if (prof.players === "multi") layout.value = "2v2";
      syncLayout();
      var diff = panel.querySelector(".lmn-diff");
      diff.value = (prof.players === "multi") ? "legacy" : "medium";
      buildSlots();
    }

    function syncLayout() {
      var n = seatsValue();
      var wrap = panel.querySelector(".lmn-layout-wrap");
      var layout = panel.querySelector(".lmn-layout");
      var show = n === 4;
      wrap.hidden = !show;
      if (!show) layout.value = "ffa";
      var diff = panel.querySelector(".lmn-diff");
      var legacyOpt = diff.querySelector('option[value="legacy"]');
      if (legacyOpt) legacyOpt.disabled = layout.value !== "2v2";
      if (legacyOpt && legacyOpt.disabled && diff.value === "legacy") diff.value = "medium";
    }

    function buildSlots() {
      var n = seatsValue();
      var box = panel.querySelector(".lmn-slots");
      var table = panel.querySelector(".lmn-diff").value;
      var html = "<p><strong>Seat difficulty</strong></p>";
      var i;
      for (i = 0; i < n; i++) {
        if (i === 0) {
          html += '<p class="lmn-slot">Seat 1 · you</p>';
        } else {
          html += '<label class="lmn-field lmn-slot">Seat ' + (i + 1) +
            ' <select data-slot="' + i + '"><option value="">Use the table</option>' +
            '<option value="easy">Easy</option><option value="medium">Medium</option><option value="hard">Hard</option></select></label>';
        }
      }
      box.innerHTML = html;
      if (table === "easy" || table === "medium" || table === "hard") {
        box.querySelectorAll("select").forEach(function (sel) { sel.value = table; });
      }
    }

    function fillValue() {
      var picked = panel.querySelector('input[name="' + uid + '-fill"]:checked');
      return picked ? picked.value : "either";
    }

    function slotDifficulty() {
      var out = [""];
      panel.querySelectorAll(".lmn-slots select").forEach(function (sel) {
        out[Number(sel.getAttribute("data-slot"))] = sel.value;
      });
      return out;
    }

    function nBody(op) {
      return {
        op: op,
        game: currentGame(),
        name: panel.querySelector(".lmn-name").value,
        seats: seatsValue(),
        fill: fillValue(),
        difficulty: panel.querySelector(".lmn-diff").value,
        layout: panel.querySelector(".lmn-layout").value,
        slot_difficulty: slotDifficulty()
      };
    }

    function mode(humanSel, aiSel) {
      var h = panel.querySelector(humanSel).checked;
      var a = panel.querySelector(aiSel).checked;
      if (h && a) return "either";
      if (h) return "human";
      return "ai";
    }

    function post(body) {
      body.pid = pid();
      if (transport === "mock") {
        var live = store();
        if (!live) return Promise.reject(new Error("mock"));
        return Promise.resolve(api.handle(live, body));
      }
      return fetch("queue.php", {
        method: "POST",
        headers: { "Content-Type": "application/json", "Accept": "application/json" },
        body: JSON.stringify(body)
      }).then(function (res) { return res.json(); });
    }

    function stop() {
      if (timer) clearInterval(timer);
      timer = null;
    }

    function watch() {
      stop();
      timer = setInterval(pull, 1500);
    }

    function renderRoster(match) {
      var lines = (match.seats || []).map(function (s) {
        var kind = s.kind === "human" ? "person" : "AI";
        var diff = s.difficulty ? " · " + s.difficulty : "";
        return "<li>" + esc(s.role) + ": " + esc(s.name) + " · " + kind + diff + "</li>";
      });
      roster.innerHTML = lines.join("");
    }

    function showMatch(match) {
      if (!match || matchedId === match.id) return;
      matchedId = match.id;
      stop();
      root.LMN_MATCH = match;
      renderRoster(match);
      say("Matched. " + (match.seats || []).length + " seats.");
      var board = doc.getElementById("match-board");
      if (board) board.hidden = false;
      if (root.LMN_BEGIN) root.LMN_BEGIN(match);
      if (root.LMN_ON_MATCH) root.LMN_ON_MATCH(match, host);
    }

    function showLobby(data) {
      say("Lobby " + data.code + ". " + data.have + " of " + data.seats + " here. " + (data.wait || 0) + "s.");
      roster.innerHTML = (data.members || []).map(function (m) {
        return "<li>" + esc(m.slot) + ": " + esc(m.name) + " · person</li>";
      }).join("");
      var code = panel.querySelector(".lmn-code");
      if (code && !code.value) code.value = data.code;
    }

    function apply(data) {
      if (!data) return;
      if (data.error) {
        say(data.error === "op" ? "This queue does not have that operation." : "Queue said " + data.error + ".");
        return;
      }
      if (data.status === "matched" && data.match) showMatch(data.match);
      else if (data.status === "lobby") showLobby(data);
      else if (data.status === "queued") say("In queue " + (data.wait || 0) + "s. " + (data.queued || 1) + " waiting on this game.");
      else if (data.status === "left") say("You left the queue.");
      else if (data.status === "none") say("You are not in a queue.");
      else say("Waiting.");
    }

    function pull() { post({ op: "poll" }).then(apply).catch(function () { say("The queue did not answer."); }); }

    function setTransport(next) {
      transport = next;
      var nBlock = panel.querySelector(".lmn-n");
      var legacy = panel.querySelector(".lmn-legacy");
      var mockTools = panel.querySelector(".lmn-mock-only");
      if (next === "legacy") {
        nBlock.hidden = true;
        legacy.hidden = false;
        mockTools.hidden = true;
        transportNote.textContent = "Live four-seat queue. Teammate is a2, enemy is b1, and b2 stays the Novelist AI. A full table of people, a free seat count, and a lobby code need the API in LOBBY_API_DESIGN.md.";
      } else if (next === "php") {
        nBlock.hidden = false;
        legacy.hidden = true;
        mockTools.hidden = true;
        transportNote.textContent = "queue.php answered caps with n_player. Joins go to that API.";
      } else if (next === "down") {
        nBlock.hidden = false;
        legacy.hidden = true;
        mockTools.hidden = true;
        transportNote.textContent = "queue.php did not answer. Nothing was queued.";
      } else {
        nBlock.hidden = false;
        legacy.hidden = true;
        mockTools.hidden = false;
        transportNote.textContent = "Local mock in this browser only. A second phone is not in this queue. Use the practice seat to add another person here. The live queue.php file is still the four-seat table.";
      }
    }

    panel.querySelector(".lmn-seats").addEventListener("change", function () { syncLayout(); buildSlots(); });
    panel.querySelector(".lmn-layout").addEventListener("change", function () { syncLayout(); buildSlots(); });
    panel.querySelector(".lmn-diff").addEventListener("change", buildSlots);
    var gameSel = panel.querySelector(".lmn-game");
    if (gameSel) gameSel.addEventListener("change", function () { matchedId = ""; paintGame(); });
    paintGame();

    panel.querySelector(".lmn-go").onclick = function () {
      matchedId = "";
      say("Joining the queue.");
      post(nBody("join")).then(function (data) {
        apply(data);
        if (!data || data.status === "queued" || data.status === "lobby") watch();
      }).catch(function () { say("The queue did not answer."); });
    };
    panel.querySelector(".lmn-open").onclick = function () {
      matchedId = "";
      say("Opening a lobby.");
      post(nBody("lobby_open")).then(function (data) {
        apply(data);
        if (data && data.status === "lobby") watch();
      }).catch(function () { say("The queue did not answer."); });
    };
    panel.querySelector(".lmn-join-code").onclick = function () {
      matchedId = "";
      post({ op: "lobby_join", code: panel.querySelector(".lmn-code").value, name: panel.querySelector(".lmn-name").value })
        .then(function (data) {
          apply(data);
          if (data && data.status === "lobby") watch();
        }).catch(function () { say("The queue did not answer."); });
    };
    panel.querySelector(".lmn-leave").onclick = function () {
      stop();
      matchedId = "";
      roster.innerHTML = "";
      post({ op: "leave" }).then(apply).catch(function () { say("The queue did not answer."); });
    };
    panel.querySelector(".lmn-practice").onclick = function () {
      if (transport !== "mock" || !store()) return;
      var body = nBody("join");
      var code = panel.querySelector(".lmn-code").value;
      if (code) {
        body = { op: "lobby_join", code: code, name: "Guest", pid: "g" + Math.random().toString(36).slice(2, 8) };
      } else {
        body.pid = "g" + Math.random().toString(36).slice(2, 8);
        body.name = "Guest";
      }
      api.handle(store(), body);
      pull();
    };
    panel.querySelector(".lmn-fillnow").onclick = function () {
      if (transport !== "mock" || !store()) return;
      store().advance(FILL_AFTER_S);
      pull();
    };
    panel.querySelector(".lmn-legacy-go").onclick = function () {
      if (!panel.querySelector(".lmn-th").checked && !panel.querySelector(".lmn-ta").checked) panel.querySelector(".lmn-ta").checked = true;
      if (!panel.querySelector(".lmn-eh").checked && !panel.querySelector(".lmn-ea").checked) panel.querySelector(".lmn-ea").checked = true;
      matchedId = "";
      say("Joining the live queue.");
      post({
        op: "join",
        game: currentGame(),
        name: panel.querySelector(".lmn-name").value,
        teammate: mode(".lmn-th", ".lmn-ta"),
        enemy: mode(".lmn-eh", ".lmn-ea")
      }).then(function (data) {
        apply(data);
        if (!data || data.status === "queued") watch();
      }).catch(function () { say("The queue did not answer."); });
    };

    var again = doc.createElement("p");
    var againBtn = doc.createElement("button");
    againBtn.type = "button";
    againBtn.className = "btn";
    againBtn.textContent = "New match";
    againBtn.onclick = function () {
      stop();
      matchedId = "";
      roster.innerHTML = "";
      root.LMN_MATCH = null;
      say("Pick the table again.");
      if (root.LMN_REMATCH) root.LMN_REMATCH(host);
    };
    again.appendChild(againBtn);
    panel.appendChild(again);

    if (root.LMN_MATCH && root.LMN_MATCH.game === game && !desk) {
      matchedId = root.LMN_MATCH.id;
      renderRoster(root.LMN_MATCH);
      say("Matched. " + (root.LMN_MATCH.seats || []).length + " seats.");
      if (root.LMN_ON_MATCH) root.LMN_ON_MATCH(root.LMN_MATCH, host);
    }

    probe().then(function (next) {
      setTransport(next);
      if (next === "down") say("The queue did not answer.");
      if (!desk && transport === "mock" && flag("demo") === "1" && !matchedId) {
        var aiFill = panel.querySelector('input[name="' + uid + '-fill"][value="ai"]');
        if (aiFill) aiFill.checked = true;
        var go = panel.querySelector(".lmn-go");
        if (go) go.click();
      }
    });
  }

  root.LMN_MOUNT_LOBBY = mount;
  var nodes = doc.querySelectorAll("#lobby, #lobby-desk, [data-lmn-lobby]");
  nodes.forEach(function (node) { mount(node); });
})(typeof window !== "undefined" ? window : globalThis);
