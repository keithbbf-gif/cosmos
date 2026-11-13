var rules = require("./chess_rules.js");
var Chess = rules.Chess;
var perft = rules.perft;

function fail(msg) {
  console.error("FAIL " + msg);
  process.exit(1);
}

function expect(fen, depth, nodes) {
  var chess = new Chess(fen);
  var got = perft(chess, depth);
  if (got !== nodes) {
    console.error("DIVIDE " + fen + " depth " + depth);
    var moves = chess.legalMoves();
    var i;
    for (i = 0; i < moves.length; i++) {
      chess.make(moves[i]);
      var sub = depth === 1 ? 1 : perft(chess, depth - 1);
      chess.unmake();
      console.error("  " + chess.uci(moves[i]) + " " + sub);
    }
    fail(fen + " depth " + depth + " got " + got + " want " + nodes);
  }
  if (chess.fen() !== new Chess(fen).fen()) fail("perft mutated " + fen);
  console.log("perft " + depth + " " + got + " " + fen.split(" ")[0]);
}

function walk(chess, depth) {
  var fen = chess.fen();
  if (depth === 0) return;
  var moves = chess.legalMoves();
  var i;
  for (i = 0; i < moves.length; i++) {
    chess.make(moves[i]);
    if (depth > 1) walk(chess, depth - 1);
    chess.unmake();
    if (chess.fen() !== fen) fail("undo " + fen + " -> " + chess.fen());
  }
}

var start = rules.START;
expect(start, 1, 20);
expect(start, 2, 400);
expect(start, 3, 8902);

var t0 = Date.now();
expect(start, 4, 197281);
console.log("perft4_ms " + (Date.now() - t0));

walk(new Chess(start), 3);
console.log("undo walk depth 3 ok");

var kiwi = "r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1";
expect(kiwi, 1, 48);
expect(kiwi, 2, 2039);
t0 = Date.now();
expect(kiwi, 3, 97862);
console.log("kiwi3_ms " + (Date.now() - t0));

var pos3 = "8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 1";
expect(pos3, 1, 14);
expect(pos3, 2, 191);
expect(pos3, 3, 2812);

var pos4 = "r3k2r/Pppp1ppp/1b3nbN/nP6/BBP1P3/q4N2/Pp1P2PP/R2Q1RK1 w kq - 0 1";
expect(pos4, 1, 6);
expect(pos4, 2, 264);
expect(pos4, 3, 9467);

var pos5 = "rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8";
expect(pos5, 1, 44);
expect(pos5, 2, 1486);

console.log("PERFT_OK");
