(function () {
  var rules = window.LMNChess;
  var models = window.LMNChessModels;
  var mock = window.LMNChessMock;
  var betsApi = window.LMNChessBets;
  var talk = window.LMNChessTalk;
  var bench = window.LMNChessBench;
  var config = window.LMN_CHESS_CONFIG;
  var GLYPH = {
    K: "\u2654", Q: "\u2655", R: "\u2656", B: "\u2657", N: "\u2658", P: "\u2659",
    k: "\u265A", q: "\u265B", r: "\u265C", b: "\u265D", n: "\u265E", p: "\u265F"
  };
  var PURSE_KEY = "lmn-chess-mock-balances-v1";

  var state = {
    mode: "human",
    started: false,
    chess: new rules.Chess(),
    humanColor: "w",
    blind: false,
    opponent: null,
    modelWhite: null,
    modelBlack: null,
    flip: false,
    line: [],
    benchRows: [],
    book: null,
    balances: { You: 1000, Ada: 500, Bo: 500 },
    result: null,
    paid: false,
    timer: null,
    selected: -1,
    drawArmed: false
  };

  function $(id) { return document.getElementById(id); }

  function say(text) { $("status").textContent = text; }

  function loadBalances() {
    try {
      var raw = JSON.parse(localStorage.getItem(PURSE_KEY) || "null");
      if (!raw || typeof raw !== "object") return;
      ["You", "Ada", "Bo"].forEach(function (name) {
        if (typeof raw[name] === "number" && isFinite(raw[name]) && raw[name] >= 0) {
          state.balances[name] = Math.floor(raw[name]);
        }
      });
    } catch (e) {}
  }

  function saveBalances() {
    try { localStorage.setItem(PURSE_KEY, JSON.stringify(state.balances)); } catch (e) {}
  }

  function bookOpts() {
    return {
      houseCutRate: config.houseCutRate,
      refundOnDraw: config.refundOnDraw,
      refundOnAbort: config.refundOnAbort,
      noWinnerPolicy: config.noWinnerPolicy,
      currency: config.currency
    };
  }

  function fillSelect(id) {
    var sel = $(id);
    sel.innerHTML = "";
    var groups = {};
    var labels = { named: "Named in the brief", "seats.json": "seats.json ids" };
    models.all().forEach(function (m) {
      if (!groups[m.group]) {
        var group = document.createElement("optgroup");
        group.label = labels[m.group] || m.group;
        sel.appendChild(group);
        groups[m.group] = group;
      }
      var opt = document.createElement("option");
      opt.value = m.key;
      opt.textContent = m.enabled ? m.label : m.label + " (off)";
      opt.disabled = !m.enabled;
      groups[m.group].appendChild(opt);
    });
  }

  function selectedModel(id) {
    return models.byKey($(id).value);
  }

  function showModelNote() {
    var m = selectedModel("model-pick");
    $("model-note").textContent = m ? m.note : "";
  }

  function renderRoster() {
    var list = $("roster");
    list.innerHTML = "";
    models.NAMED.forEach(function (m) {
      var li = document.createElement("li");
      var where = m.seats_id ? ("seats.json id " + m.seats_id + ". ") : "not in seats.json. ";
      li.textContent = m.label + " — " + where + (m.enabled ? "Local mock. " : "Disabled. ") + m.note;
      list.appendChild(li);
    });
    var extra = document.createElement("li");
    extra.textContent = "Picker also lists the other seats.json ids (" + (Object.keys(models.SEATS).length - 1) + " besides Muse Spark 1.3). seats.json has no rating field. None is shown.";
    list.appendChild(extra);
  }

  function paintBalances() {
    var bits = ["You " + state.balances.You, "Ada " + state.balances.Ada, "Bo " + state.balances.Bo];
    $("purses").textContent = "Play-money mock purses: " + bits.join(" · ") + ". Not TokenCTR. Not game tokens.";
  }

  function stopTimer() {
    if (state.timer) clearTimeout(state.timer);
    state.timer = null;
  }

  function releaseOpenBook() {
    if (!state.book || state.book.state !== "open") return;
    state.book.bets.forEach(function (b) {
      if (state.balances[b.name] == null) state.balances[b.name] = 0;
      state.balances[b.name] += b.amount;
    });
    state.book = null;
    state.paid = false;
    saveBalances();
  }

  function clearMatch() {
    stopTimer();
    state.started = false;
    state.chess = new rules.Chess();
    state.opponent = null;
    state.modelWhite = null;
    state.modelBlack = null;
    state.line = [];
    state.benchRows = [];
    state.result = null;
    state.selected = -1;
    state.drawArmed = false;
    state.pending = null;
    $("promo").hidden = true;
    $("reveal").textContent = "";
    $("settlement").textContent = "";
  }

  function sideName(color) {
    var model = color === "w" ? state.modelWhite : state.modelBlack;
    if (state.mode === "human" && color === state.humanColor) return "You";
    if (state.mode === "hotseat") return color === "w" ? "White" : "Black";
    if (state.blind && !state.result) return "Unknown agent";
    if (!model) return color === "w" ? "White" : "Black";
    return model.label;
  }

  function resultText(result) {
    if (!result) return "";
    if (result.kind === "white" || result.kind === "black") {
      var how = result.reason === "resign" ? " by resign" : (result.reason === "checkmate" ? " by checkmate" : "");
      return sideName(result.kind === "white" ? "w" : "b") + " wins" + how + ".";
    }
    if (result.kind === "draw") return "Draw (" + result.reason + ").";
    if (result.kind === "abort") return "Aborted (" + result.reason + "). Stakes refunded when a book was open or locked.";
    return result.kind;
  }

  function reveal() {
    var box = $("reveal");
    if (state.mode !== "human" || !state.blind || !state.opponent) {
      box.textContent = "";
      return;
    }
    var m = state.opponent;
    var id = m.seats_id ? m.seats_id : "no seats.json id";
    box.textContent = "The agent was " + m.label + " (" + id + "). " + config.blindNote;
  }

  function pushLine(move, sanText, choice) {
    var entry = {
      color: move.prevTurn,
      san: sanText,
      piece: move.piece,
      from: rules.alg(move.from),
      to: rules.alg(move.to),
      capture: !!(move.captured || move.ep),
      ep: !!move.ep,
      castle: move.castle || "",
      promotion: move.promotion ? move.promotion.toUpperCase() : "",
      check: /\+$/.test(sanText),
      mate: /#$/.test(sanText)
    };
    entry.text = talk.commentMove(entry, state.line.length);
    state.line.push(entry);
    if (choice) state.benchRows.push(bench.row(choice));
  }

  function applySettlement(settlement) {
    if (state.paid) return;
    state.paid = true;
    settlement.payouts.forEach(function (p) {
      if (state.balances[p.name] == null) state.balances[p.name] = 0;
      state.balances[p.name] += p.returned;
    });
    saveBalances();
    var lines = [
      "Settlement " + settlement.reason + ". Stakes " + settlement.stakes +
      ". House " + settlement.house + ". Pool " + settlement.pool +
      ". Rate " + settlement.houseCutRate + " from the book, not a baked-in cut."
    ];
    settlement.payouts.forEach(function (p) {
      lines.push(p.name + " bet " + p.amount + " on " + p.side + ", returned " + p.returned + ".");
    });
    lines.push("House cut is recorded here only. It is not sent to TokenCTR or a card.");
    $("settlement").textContent = lines.join(" ");
  }

  function endGame(result) {
    if (state.result) return;
    stopTimer();
    state.result = result;
    state.selected = -1;
    if (state.book && (state.book.state === "open" || state.book.state === "locked")) {
      if ((result.kind === "white" || result.kind === "black") && state.book.state === "open") {
        betsApi.lock(state.book);
      }
      applySettlement(betsApi.settle(state.book, result));
    }
    if (state.benchRows.length) {
      state.benchRows.push(bench.summary(state.benchRows.filter(function (r) { return r.uci; }), result));
    }
    reveal();
    paint();
  }

  function afterMove() {
    var natural = state.chess.result();
    if (natural) {
      endGame(natural);
      return;
    }
    if (state.line.length >= config.maxPlies) {
      endGame({ kind: "abort", reason: "max-plies" });
      return;
    }
    paint();
    if (agentToMove()) state.timer = setTimeout(agentStep, 320);
  }

  function agentToMove() {
    if (!state.started || state.result) return false;
    if (state.mode === "agents") return true;
    if (state.mode === "human") return state.chess.turn !== state.humanColor;
    return false;
  }

  function modelForTurn() {
    return state.chess.turn === "w" ? state.modelWhite : state.modelBlack;
  }

  function agentStep() {
    state.timer = null;
    if (!agentToMove()) return;
    var model = modelForTurn();
    if (!model) return;
    var choice;
    try { choice = mock.choose(model, state.chess); }
    catch (e) {
      say("The local mock refused that model.");
      endGame({ kind: "abort", reason: "mock-error" });
      return;
    }
    if (!choice) {
      endGame(state.chess.result() || { kind: "abort", reason: "no-move" });
      return;
    }
    var move = null;
    var legal = state.chess.legalMoves();
    var i;
    for (i = 0; i < legal.length; i++) if (state.chess.uci(legal[i]) === choice.uci) move = legal[i];
    if (!move) {
      endGame({ kind: "abort", reason: "mock-illegal" });
      return;
    }
    var sanText = rules.san(state.chess, move);
    state.chess.make(move);
    pushLine(move, sanText, choice);
    afterMove();
  }

  function humanCanMove() {
    if (!state.started || state.result) return false;
    if (state.mode === "agents") return false;
    if (state.mode === "hotseat") return true;
    return state.chess.turn === state.humanColor;
  }

  function commitHuman(move) {
    $("promo").hidden = true;
    var sanText = rules.san(state.chess, move);
    state.chess.make(move);
    state.selected = -1;
    state.drawArmed = false;
    pushLine(move, sanText, null);
    afterMove();
  }

  function onSquare(sq) {
    if (!humanCanMove()) return;
    var legal = state.chess.legalMoves();
    if (state.selected >= 0) {
      var hits = legal.filter(function (m) { return m.from === state.selected && m.to === sq; });
      if (hits.length === 1) {
        commitHuman(hits[0]);
        return;
      }
      if (hits.length > 1) {
        state.pending = hits;
        $("promo").hidden = false;
        return;
      }
    }
    $("promo").hidden = true;
    state.pending = null;
    var piece = state.chess.board[sq];
    var mine = state.chess.turn === "w" ? (piece && piece === piece.toUpperCase()) : (piece && piece === piece.toLowerCase());
    state.selected = mine ? sq : -1;
    paint();
  }

  function paint() {
    var board = $("board");
    board.innerHTML = "";
    var legal = state.started ? state.chess.legalMoves() : [];
    var last = state.chess.hist.length ? state.chess.hist[state.chess.hist.length - 1] : null;
    var ranks = state.flip ? [0, 1, 2, 3, 4, 5, 6, 7] : [7, 6, 5, 4, 3, 2, 1, 0];
    var files = state.flip ? [7, 6, 5, 4, 3, 2, 1, 0] : [0, 1, 2, 3, 4, 5, 6, 7];
    var checkSq = -1;
    if (state.started && state.chess.inCheck()) {
      try { checkSq = state.chess.findKing(state.chess.turn === "w"); } catch (e) { checkSq = -1; }
    }
    ranks.forEach(function (r) {
      files.forEach(function (f) {
        var sq = r * 8 + f;
        var btn = document.createElement("button");
        btn.type = "button";
        btn.className = "sq " + (((f + r) & 1) === 0 ? "dark" : "light");
        if (sq === state.selected) btn.className += " sel";
        if (last && (sq === last.from || sq === last.to)) btn.className += " last";
        if (sq === checkSq) btn.className += " check";
        if (state.selected >= 0 && legal.some(function (m) { return m.from === state.selected && m.to === sq; })) {
          btn.className += " dest";
        }
        btn.setAttribute("aria-label", rules.alg(sq));
        btn.textContent = GLYPH[state.chess.board[sq]] || "";
        btn.addEventListener("click", function () { onSquare(sq); });
        board.appendChild(btn);
      });
    });
    $("fen").textContent = state.chess.fen();
    var pgn = [];
    state.line.forEach(function (entry, i) {
      if (i % 2 === 0) pgn.push(Math.floor(i / 2) + 1 + ".");
      pgn.push(entry.san);
    });
    $("pgn").textContent = pgn.join(" ") || "No moves yet.";
    var talkBox = $("talk");
    talkBox.innerHTML = "";
    state.line.forEach(function (entry) {
      var li = document.createElement("li");
      li.textContent = entry.text;
      talkBox.appendChild(li);
    });
    var benchBox = $("bench");
    benchBox.innerHTML = "";
    state.benchRows.forEach(function (row) {
      var li = document.createElement("li");
      if (row.uci) {
        li.textContent = "mock " + (row.model_label || "") + " " + row.uci +
          " legal " + row.legal_moves_offered + " illegal " + row.illegal_attempts +
          " rate " + row.legal_move_rate + " latency_ms " + row.latency_ms +
          " tokens null";
      } else {
        li.textContent = "mock summary moves " + row.moves + " legal rate " + row.legal_move_rate +
          " illegal " + row.illegal_attempts + " latency_ms " + row.latency_ms +
          " result " + (row.result && row.result.kind) + " tokens null";
      }
      benchBox.appendChild(li);
    });
    paintBalances();
    var idle = "Set the mode, then start. Nothing calls a model.";
    if (!state.started && state.mode === "hotseat") idle = "Hotseat: two people on this device. Press Start hotseat.";
    if (!state.started && state.mode === "agents") idle = "Place play-money bets, then lock and start. Nothing calls a model.";
    var status = state.result ? resultText(state.result) : (state.started ? (sideName(state.chess.turn) + " to move.") : idle);
    if (state.started && !state.result && state.chess.inCheck()) status = "Check. " + status;
    say(status);
    $("agents-panel").hidden = state.mode !== "agents";
    $("human-panel").hidden = state.mode !== "human";
    $("blind-help").hidden = !($("blind") && $("blind").checked);
    $("model-pick").hidden = $("blind").checked;
    $("mode-human").setAttribute("aria-pressed", state.mode === "human" ? "true" : "false");
    $("mode-agents").setAttribute("aria-pressed", state.mode === "agents" ? "true" : "false");
    $("mode-hotseat").setAttribute("aria-pressed", state.mode === "hotseat" ? "true" : "false");
    $("start-hotseat").hidden = state.mode !== "hotseat";
    renderBets();
  }

  function resetGame() {
    var note = "";
    if (state.book && state.book.state === "locked" && !state.paid) {
      applySettlement(betsApi.settle(state.book, { kind: "abort" }));
      note = $("settlement").textContent;
    } else {
      releaseOpenBook();
    }
    state.book = null;
    state.paid = false;
    clearMatch();
    if (note) $("settlement").textContent = note;
    paint();
  }

  function begin(opts) {
    if (opts.mode !== "agents") {
      if (state.book && state.book.state === "locked" && !state.paid) {
        applySettlement(betsApi.settle(state.book, { kind: "abort" }));
      } else {
        releaseOpenBook();
      }
      state.book = null;
    }
    var kept = opts.mode === "agents" ? (opts.book || state.book) : null;
    clearMatch();
    state.mode = opts.mode;
    state.started = true;
    state.paid = false;
    state.humanColor = opts.humanColor || "w";
    state.blind = !!opts.blind;
    state.opponent = opts.opponent || null;
    state.modelWhite = opts.modelWhite || null;
    state.modelBlack = opts.modelBlack || null;
    state.flip = opts.mode === "human" && state.humanColor === "b";
    if (opts.mode === "agents") {
      state.book = kept || betsApi.createBook(bookOpts());
      if (state.book.state === "open") betsApi.lock(state.book);
    }
    paint();
    if (agentToMove()) state.timer = setTimeout(agentStep, 320);
  }

  function startHuman() {
    var blind = $("blind").checked;
    var color = $("color").value === "b" ? "b" : "w";
    var model = blind ? models.pickBlind(models.enabled()) : selectedModel("model-pick");
    if (!model || model.enabled === false || model.key === "gf38") {
      say("Pick an enabled model. Gemini 3.8 Flash stays off.");
      return;
    }
    begin({
      mode: "human",
      blind: blind,
      humanColor: color,
      opponent: model,
      modelWhite: color === "w" ? null : model,
      modelBlack: color === "b" ? null : model
    });
  }

  function startAgents() {
    var white = selectedModel("white-pick");
    var black = selectedModel("black-pick");
    if (!white || !black || !white.enabled || !black.enabled || white.key === "gf38" || black.key === "gf38") {
      say("Pick two enabled models. Gemini 3.8 Flash stays off.");
      return;
    }
    if (state.book && state.book.state === "locked" && !state.paid) {
      applySettlement(betsApi.settle(state.book, { kind: "abort" }));
      state.book = null;
      state.paid = false;
    }
    if (state.book && state.book.state !== "open") state.book = null;
    if (!state.book) state.book = betsApi.createBook(bookOpts());
    var book = state.book;
    begin({ mode: "agents", modelWhite: white, modelBlack: black, book: book });
  }

  function startHotseat() {
    begin({ mode: "hotseat" });
  }

  function placeBet(ev) {
    ev.preventDefault();
    if (state.mode !== "agents") {
      say("Bets are for agent vs agent, before the match starts.");
      return;
    }
    if (state.started) {
      say("The window is locked.");
      return;
    }
    var name = $("bet-name").value;
    var side = $("bet-side").value === "black" ? "black" : "white";
    var amount = parseInt($("bet-amount").value, 10);
    if (!isFinite(amount) || amount < 1) {
      say("Bet a whole play-money amount of at least 1.");
      return;
    }
    if ((state.balances[name] || 0) < amount) {
      say(name + " does not have that much play-money.");
      return;
    }
    if (!state.book || state.book.state !== "open") state.book = betsApi.createBook(bookOpts());
    state.balances[name] -= amount;
    betsApi.placeBet(state.book, { name: name, side: side, amount: amount });
    saveBalances();
    renderBets();
    paint();
    say("Bet placed. It locks when the match starts.");
  }

  function renderBets() {
    var box = $("bet-list");
    box.innerHTML = "";
    var rows = state.book ? state.book.bets : [];
    if (!rows.length) {
      box.textContent = "No bets yet. Window is open until you start the match.";
      return;
    }
    rows.forEach(function (b) {
      var li = document.createElement("li");
      li.textContent = b.name + " " + b.amount + " on " + b.side;
      if (state.book.state === "open") {
        var undo = document.createElement("button");
        undo.type = "button";
        undo.textContent = "Remove";
        undo.addEventListener("click", function () {
          betsApi.cancelBet(state.book, b.id);
          state.balances[b.name] += b.amount;
          saveBalances();
          renderBets();
          paint();
        });
        li.appendChild(undo);
      }
      box.appendChild(li);
    });
  }

  function runPerft() {
    var a = rules.perft(new rules.Chess(), 1);
    var b = rules.perft(new rules.Chess(), 2);
    var c = rules.perft(new rules.Chess(), 3);
    var text = "perft " + a + " " + b + " " + c;
    $("perft-line").textContent = text;
    window.LMN_CHESS_PERFT = text;
  }

  function attachLobby() {
    var script = document.createElement("script");
    script.src = "../lobby_new.js";
    script.onload = function () {
      var note = $("lobby-note");
      if (window.LMN_MOUNT_LOBBY) {
        try { window.LMN_MOUNT_LOBBY($("lobby")); } catch (e) {}
        note.textContent = "lobby_new.js loaded and LMN_MOUNT_LOBBY was called on #lobby. queue.php in the live site accepts higher, tiles, derby, and ids matching ^[sm][0-9]{2}$. t904 is outside that list, so a queued chess match still needs a backend change. Hotseat on this page works now.";
      } else {
        note.textContent = "../lobby_new.js loaded but did not set LMN_MOUNT_LOBBY. Hotseat works now. See LOBBY_HOOK.md.";
      }
    };
    script.onerror = function () {
      $("lobby-note").textContent = "lobby_new.js is not in site_new. Hotseat works on this page. See LOBBY_HOOK.md.";
    };
    document.head.appendChild(script);
  }

  function boot() {
    loadBalances();
    fillSelect("model-pick");
    fillSelect("white-pick");
    fillSelect("black-pick");
    var enabled = models.enabled();
    if (enabled[0]) $("model-pick").value = enabled[0].key;
    if (enabled[0]) $("white-pick").value = enabled[0].key;
    var second = enabled.length > 1 ? enabled[1] : enabled[0];
    if (second) $("black-pick").value = second.key;
    renderRoster();
    showModelNote();
    $("cut-line").textContent = "House cut default " + config.houseCutRate + " (config.js). Pool = stakes minus Math.round(stakes * rate). Draw, abort, and a result nobody bet: full stake refund, house 0. " +
      "Betting real tokens on outcomes may be regulated as gambling depending on how tokens are bought or cashed out. That needs Keith's OK plus a legal check before it goes live.";
    $("gf38-note").textContent = "Gemini 3.8 Flash (GF38): " + config.gf38Note;
    $("blind-help").textContent = config.blindNote;
    $("mode-human").addEventListener("click", function () {
      if (state.started) return;
      releaseOpenBook();
      state.mode = "human";
      paint();
    });
    $("mode-agents").addEventListener("click", function () {
      if (state.started) return;
      state.mode = "agents";
      paint();
    });
    $("mode-hotseat").addEventListener("click", function () {
      if (state.started) return;
      releaseOpenBook();
      state.mode = "hotseat";
      paint();
    });
    $("model-pick").addEventListener("change", showModelNote);
    $("blind").addEventListener("change", paint);
    $("start-human").addEventListener("click", startHuman);
    $("start-agents").addEventListener("click", startAgents);
    $("start-hotseat").addEventListener("click", startHotseat);
    $("resign").addEventListener("click", function () {
      if (!state.started || state.result) return;
      var loser = state.mode === "human" ? state.humanColor : state.chess.turn;
      endGame({ kind: loser === "w" ? "black" : "white", reason: "resign" });
    });
    $("abort").addEventListener("click", function () {
      if (state.result) return;
      if (!state.started) {
        releaseOpenBook();
        renderBets();
        paint();
        say("Open bets removed.");
        return;
      }
      endGame({ kind: "abort", reason: "abort" });
    });
    $("draw").addEventListener("click", function () {
      if (!state.started || state.result) return;
      if (state.mode === "human") {
        say("Local mock does not accept draw offers.");
        return;
      }
      if (state.mode !== "hotseat") return;
      if (!state.drawArmed) {
        state.drawArmed = true;
        say("Draw offered. Press Agree draw again.");
        return;
      }
      endGame({ kind: "draw", reason: "agreement" });
    });
    $("new-game").addEventListener("click", function () {
      var mode = state.mode;
      resetGame();
      state.mode = mode;
      renderBets();
      paint();
    });
    $("flip").addEventListener("click", function () { state.flip = !state.flip; paint(); });
    $("bet-form").addEventListener("submit", placeBet);
    $("reset-purse").addEventListener("click", function () {
      if (state.started && !state.result) {
        say("Finish or abort the match before resetting purses.");
        return;
      }
      state.balances = { You: 1000, Ada: 500, Bo: 500 };
      saveBalances();
      paint();
    });
    ["Q", "R", "B", "N"].forEach(function (kind) {
      $("promo-" + kind).addEventListener("click", function () {
        if (!state.pending) return;
        var want = state.chess.turn === "w" ? kind : kind.toLowerCase();
        var i;
        for (i = 0; i < state.pending.length; i++) {
          if (state.pending[i].promotion === want) {
            var move = state.pending[i];
            state.pending = null;
            commitHuman(move);
            return;
          }
        }
      });
    });
    runPerft();
    paint();
    attachLobby();
    window.LMN_CHESS_LOBBY_START = function (spec) {
      if (!spec || spec.white !== "human" || spec.black !== "human") return false;
      startHotseat();
      return true;
    };
    $("boot").textContent = "ready";
    window.LMN_CHESS_PAGE = "ready";
  }

  try {
    boot();
  } catch (e) {
    window.LMN_CHESS_PAGE = "error";
    var boot = document.getElementById("boot");
    if (boot) boot.textContent = "error";
  }
})();
