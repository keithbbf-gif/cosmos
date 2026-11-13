var rules = require("./chess_rules.js");
var Chess = rules.Chess;

function fail(msg) {
  console.error("FAIL " + msg);
  process.exit(1);
}

function eq(got, want, msg) {
  if (got !== want) fail(msg + " got " + got + " want " + want);
}

function hasUci(chess, uci) {
  var moves = chess.legalMoves();
  var i;
  for (i = 0; i < moves.length; i++) if (chess.uci(moves[i]) === uci) return true;
  return false;
}

function play(chess, uci) {
  var move = chess.playUci(uci);
  if (!move) fail("illegal " + uci + " fen " + chess.fen());
  return move;
}

var start = new Chess();
eq(start.fen(), rules.START, "start fen");
eq(start.playUci("e2e5"), null, "illegal pawn");
eq(hasUci(start, "e2e4"), true, "e4");
eq(hasUci(start, "g1f3"), true, "nf3");
eq(hasUci(start, "e1g1"), false, "no castle yet");

var castle = new Chess("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1");
eq(hasUci(castle, "e1g1"), true, "white O-O");
eq(hasUci(castle, "e1c1"), true, "white O-O-O");
var oos = null;
var moves = castle.legalMoves();
var i;
for (i = 0; i < moves.length; i++) if (castle.uci(moves[i]) === "e1g1") oos = moves[i];
eq(rules.san(castle, oos), "O-O", "san castle");
play(castle, "e1g1");
eq(castle.board[6], "K", "king g1");
eq(castle.board[5], "R", "rook f1");
eq(castle.board[4], "", "e1 empty");
eq(castle.board[7], "", "h1 empty");
eq(castle.castle.K, false, "lose K");
eq(castle.castle.Q, false, "lose Q");
eq(castle.fen().split(" ")[2].indexOf("K") < 0, true, "fen no K");

var blocked = new Chess("5r2/8/8/8/8/8/8/R3K2R w KQ - 0 1");
eq(hasUci(blocked, "e1g1"), false, "kingside through rook");
eq(hasUci(blocked, "e1c1"), true, "queenside still open");
play(blocked, "e1c1");
eq(blocked.board[2], "K", "king c1");
eq(blocked.board[3], "R", "rook d1");
eq(blocked.board[0], "", "a1 empty");

var checked = new Chess("4r3/8/8/8/8/8/8/R3K2R w KQ - 0 1");
eq(hasUci(checked, "e1g1"), false, "no castle in check K");
eq(hasUci(checked, "e1c1"), false, "no castle in check Q");

var ep = new Chess("4k3/8/8/3pP3/8/8/8/4K3 w - d6 0 1");
eq(hasUci(ep, "e5d6"), true, "ep move");
play(ep, "e5d6");
eq(ep.board[43], "P", "pawn on d6");
eq(ep.board[35], "", "d5 captured");
eq(ep.board[36], "", "e5 empty");
eq(ep.ep, -1, "ep cleared");

var epGone = new Chess("4k3/8/8/3pP3/8/8/8/4K3 w - d6 0 1");
play(epGone, "e1e2");
eq(hasUci(epGone, "e5d6"), false, "ep expired");

var promo = new Chess("8/P7/8/8/8/8/k7/7K w - - 0 1");
eq(hasUci(promo, "a7a8q"), true, "queen promo");
eq(hasUci(promo, "a7a8r"), true, "rook promo");
eq(hasUci(promo, "a7a8b"), true, "bishop promo");
eq(hasUci(promo, "a7a8n"), true, "knight promo");
play(promo, "a7a8n");
eq(promo.board[56], "N", "underpromote");

var mate = new Chess();
["e2e4", "e7e5", "d1h5", "b8c6", "f1c4", "g8f6", "h5f7"].forEach(function (u) { play(mate, u); });
eq(mate.status(), "checkmate", "scholar");
eq(mate.result().kind, "white", "white wins");
eq(rules.san(new Chess("rnbqkb1r/pppp1ppp/5n2/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq - 2 3"), (function () {
  var c = new Chess("rnbqkb1r/pppp1ppp/5n2/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq - 2 3");
  var mv = c.legalMoves();
  var j;
  for (j = 0; j < mv.length; j++) if (c.uci(mv[j]) === "h5f7") return mv[j];
  return null;
})()), "Qxf7#", "san mate");

var stale = new Chess("7k/5Q2/6K1/8/8/8/8/8 b - - 0 1");
eq(stale.status(), "stalemate", "stalemate");
eq(stale.result().kind, "draw", "stalemate draw");

var fifty = new Chess("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 99 40");
play(fifty, "g1f3");
eq(fifty.half, 100, "half 100");
eq(fifty.status(), "fifty-move", "fifty");
eq(new Chess("4k3/8/8/8/8/8/8/4K3 w - - 100 80").status(), "fifty-move", "loaded fifty");

var rep = new Chess();
["g1f3", "g8f6", "f3g1", "f6g8", "g1f3", "g8f6", "f3g1", "f6g8"].forEach(function (u) { play(rep, u); });
eq(rep.status(), "threefold", "threefold");
eq(rep.fen().split(" ")[0], rules.START.split(" ")[0], "back to start pieces");

eq(new Chess("7k/8/8/8/8/8/8/7K w - - 0 1").status(), "insufficient-material", "kk");
eq(new Chess("7k/8/8/8/8/8/8/6NK w - - 0 1").status(), "insufficient-material", "knk");
eq(new Chess("7k/8/8/8/8/8/8/6RK w - - 0 1").status() === "insufficient-material", false, "krk not draw");
eq(new Chess("7b/8/8/8/8/8/k7/2B4K w - - 0 1").status(), "insufficient-material", "same bishops");
eq(new Chess("b7/8/8/8/8/8/k7/2B4K w - - 0 1").status() === "insufficient-material", false, "opposite bishops");

console.log("RULES_OK");
