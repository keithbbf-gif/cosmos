(function (root, factory) {
  var rules = (typeof module === "object" && module.exports) ? require("./chess_rules.js") : root.LMNChess;
  var api = factory(rules);
  if (typeof module === "object" && module.exports) module.exports = api;
  root.LMNChessMock = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function (rules) {
  var VALUES = { P: 100, N: 320, B: 330, R: 500, Q: 900 };

  function hash(text) {
    var h = 2166136261;
    var i;
    for (i = 0; i < text.length; i++) {
      h ^= text.charCodeAt(i);
      h = Math.imul(h, 16777619);
    }
    return h >>> 0;
  }

  function evalWhite(chess) {
    var score = 0;
    var i;
    for (i = 0; i < 64; i++) {
      var p = chess.board[i];
      if (!p || p === "K" || p === "k") continue;
      var kind = p.toUpperCase();
      var value = VALUES[kind] || 0;
      var file = i & 7;
      var rank = i >> 3;
      if (file >= 2 && file <= 5 && rank >= 2 && rank <= 5) value += 4;
      if (p === "K" || p === "k") value = 0;
      score += (p === kind) ? value : -value;
    }
    return score;
  }

  function assertPlayable(model) {
    if (!model || model.enabled === false || model.key === "gf38" || model.short === "GF38") {
      var err = new Error("model-off");
      err.code = "model-off";
      throw err;
    }
  }

  function choose(model, chess) {
    assertPlayable(model);
    var moves = chess.legalMoves();
    if (!moves.length) return null;
    var label = model.seats_id || model.key || model.label || "mock";
    var best = null;
    var bestScore = -1e15;
    var t0 = Date.now();
    var i;
    for (i = 0; i < moves.length; i++) {
      var mv = moves[i];
      chess.make(mv);
      var whiteScore = evalWhite(chess);
      var over = chess.legalMoves();
      var check = chess.inCheck();
      var mate = check && over.length === 0;
      var moverWhite = chess.turn === "b";
      var score = moverWhite ? whiteScore : -whiteScore;
      if (mate) score += 1000000;
      else if (check) score += 15;
      chess.unmake();
      score += (hash(label + ":" + chess.uci(mv)) % 31) - 15;
      if (score > bestScore) {
        bestScore = score;
        best = mv;
      }
    }
    return {
      uci: chess.uci(best),
      move: best,
      label: "mock",
      model_label: model.label,
      seats_id: model.seats_id || null,
      legal_moves_offered: moves.length,
      illegal_attempts: 0,
      latency_ms: Date.now() - t0,
      tokens_in: null,
      tokens_out: null
    };
  }

  function playSim(whiteModel, blackModel, maxPlies, fen) {
    var chess = new rules.Chess(fen);
    var log = [];
    var guard = maxPlies || 40;
    var i;
    for (i = 0; i < guard; i++) {
      if (chess.result()) break;
      var model = chess.turn === "w" ? whiteModel : blackModel;
      var choice = choose(model, chess);
      if (!choice || !chess.playUci(choice.uci)) {
        return { chess: chess, log: log, result: { kind: "abort", reason: "mock-illegal" } };
      }
      log.push(choice);
    }
    return { chess: chess, log: log, result: chess.result() || { kind: "abort", reason: "max-plies" } };
  }

  return { choose: choose, playSim: playSim, hash: hash };
});
