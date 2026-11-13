(function (root, factory) {
  var api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  root.LMNChess = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  var START = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
  var KNIGHT = [-17, -15, -10, -6, 6, 10, 15, 17];
  var KING = [-9, -8, -7, -1, 1, 7, 8, 9];
  var BISHOP = [-9, -7, 7, 9];
  var ROOK = [-8, -1, 1, 8];

  function fileOf(sq) { return sq & 7; }
  function rankOf(sq) { return sq >> 3; }

  function alg(sq) {
    return "abcdefgh"[fileOf(sq)] + String(rankOf(sq) + 1);
  }

  function algToSq(text) {
    if (!text || text.length < 2) return -1;
    var f = text.charCodeAt(0) - 97;
    var r = text.charCodeAt(1) - 49;
    if (f < 0 || f > 7 || r < 0 || r > 7) return -1;
    return r * 8 + f;
  }

  function onBoard(sq) { return sq >= 0 && sq < 64; }

  function neighbor(from, to) {
    if (!onBoard(to)) return false;
    return Math.abs(fileOf(from) - fileOf(to)) <= 1;
  }

  function isWhitePiece(p) {
    return p === "P" || p === "N" || p === "B" || p === "R" || p === "Q" || p === "K";
  }

  function isBlackPiece(p) {
    return p === "p" || p === "n" || p === "b" || p === "r" || p === "q" || p === "k";
  }

  function sidePiece(p, white) {
    return white ? isWhitePiece(p) : isBlackPiece(p);
  }

  function Chess(fen) {
    this.board = new Array(64);
    this.turn = "w";
    this.castle = { K: false, Q: false, k: false, q: false };
    this.ep = -1;
    this.half = 0;
    this.full = 1;
    this.hist = [];
    this.seen = {};
    this.load(fen || START);
  }

  Chess.prototype.load = function (fen) {
    var parts = String(fen).trim().split(/\s+/);
    if (parts.length < 4) throw new Error("fen");
    var ranks = parts[0].split("/");
    if (ranks.length !== 8) throw new Error("fen");
    var board = new Array(64);
    var r;
    for (r = 0; r < 64; r++) board[r] = "";
    for (r = 0; r < 8; r++) {
      var rankIndex = 7 - r;
      var file = 0;
      var row = ranks[r];
      var i;
      for (i = 0; i < row.length; i++) {
        var c = row.charAt(i);
        if (c >= "1" && c <= "8") {
          file += c.charCodeAt(0) - 48;
        } else if (isWhitePiece(c) || isBlackPiece(c)) {
          if (file > 7) throw new Error("fen");
          board[rankIndex * 8 + file] = c;
          file += 1;
        } else {
          throw new Error("fen");
        }
      }
      if (file !== 8) throw new Error("fen");
    }
    if (parts[1] !== "w" && parts[1] !== "b") throw new Error("fen");
    var castle = { K: false, Q: false, k: false, q: false };
    if (parts[2] !== "-") {
      var k;
      for (k = 0; k < parts[2].length; k++) {
        var bit = parts[2].charAt(k);
        if (castle[bit] === false || castle[bit] === true) castle[bit] = true;
        else throw new Error("fen");
      }
    }
    var ep = -1;
    if (parts[3] !== "-") {
      ep = algToSq(parts[3]);
      if (ep < 0) throw new Error("fen");
    }
    this.board = board;
    this.turn = parts[1];
    this.castle = castle;
    this.ep = ep;
    this.half = parts.length > 4 ? parseInt(parts[4], 10) : 0;
    this.full = parts.length > 5 ? parseInt(parts[5], 10) : 1;
    if (!isFinite(this.half) || this.half < 0) throw new Error("fen");
    if (!isFinite(this.full) || this.full < 1) throw new Error("fen");
    this.hist = [];
    this.seen = {};
    this.seen[this.key()] = 1;
    return this;
  };

  Chess.prototype.fen = function () {
    var ranks = [];
    var r;
    for (r = 7; r >= 0; r--) {
      var row = "";
      var empty = 0;
      var f;
      for (f = 0; f < 8; f++) {
        var p = this.board[r * 8 + f];
        if (!p) {
          empty += 1;
        } else {
          if (empty) {
            row += String(empty);
            empty = 0;
          }
          row += p;
        }
      }
      if (empty) row += String(empty);
      ranks.push(row);
    }
    var castle = "";
    if (this.castle.K) castle += "K";
    if (this.castle.Q) castle += "Q";
    if (this.castle.k) castle += "k";
    if (this.castle.q) castle += "q";
    if (!castle) castle = "-";
    return ranks.join("/") + " " + this.turn + " " + castle + " " +
      (this.ep < 0 ? "-" : alg(this.ep)) + " " + this.half + " " + this.full;
  };

  Chess.prototype.key = function () {
    var parts = this.fen().split(" ");
    return parts[0] + " " + parts[1] + " " + parts[2] + " " + parts[3];
  };

  Chess.prototype.findKing = function (white) {
    var want = white ? "K" : "k";
    var i;
    for (i = 0; i < 64; i++) if (this.board[i] === want) return i;
    throw new Error("king");
  };

  Chess.prototype.attacked = function (target, byWhite) {
    var board = this.board;
    var pawnD = byWhite ? [-7, -9] : [7, 9];
    var pawn = byWhite ? "P" : "p";
    var i;
    for (i = 0; i < 2; i++) {
      var from = target + pawnD[i];
      if (!onBoard(from)) continue;
      if (Math.abs(fileOf(from) - fileOf(target)) !== 1) continue;
      if (board[from] === pawn) return true;
    }
    var knight = byWhite ? "N" : "n";
    for (i = 0; i < KNIGHT.length; i++) {
      var nsq = target + KNIGHT[i];
      if (!onBoard(nsq)) continue;
      var df = Math.abs(fileOf(nsq) - fileOf(target));
      var dr = Math.abs(rankOf(nsq) - rankOf(target));
      if (!((df === 1 && dr === 2) || (df === 2 && dr === 1))) continue;
      if (board[nsq] === knight) return true;
    }
    if (this.rayHit(target, BISHOP, byWhite ? "BQ" : "bq")) return true;
    if (this.rayHit(target, ROOK, byWhite ? "RQ" : "rq")) return true;
    var king = byWhite ? "K" : "k";
    for (i = 0; i < KING.length; i++) {
      var ksq = target + KING[i];
      if (!neighbor(target, ksq)) continue;
      if (board[ksq] === king) return true;
    }
    return false;
  };

  Chess.prototype.rayHit = function (target, deltas, letters) {
    var d;
    for (d = 0; d < deltas.length; d++) {
      var prev = target;
      var delta = deltas[d];
      for (;;) {
        var n = prev + delta;
        if (!onBoard(n) || Math.abs(fileOf(n) - fileOf(prev)) > 1) break;
        var p = this.board[n];
        if (p) {
          if (letters.indexOf(p) >= 0) return true;
          break;
        }
        prev = n;
      }
    }
    return false;
  };

  function pushMove(list, from, to, piece, captured, promotion, castle, ep) {
    list.push({
      from: from,
      to: to,
      piece: piece,
      captured: captured || "",
      promotion: promotion || "",
      castle: castle || "",
      ep: !!ep
    });
  }

  Chess.prototype.pseudoMoves = function () {
    var list = [];
    var white = this.turn === "w";
    var board = this.board;
    var sq;
    for (sq = 0; sq < 64; sq++) {
      var piece = board[sq];
      if (!sidePiece(piece, white)) continue;
      var kind = piece.toUpperCase();
      if (kind === "P") this.pawnMoves(list, sq, piece, white);
      else if (kind === "N") this.stepMoves(list, sq, piece, KNIGHT, false);
      else if (kind === "B") this.slideMoves(list, sq, piece, BISHOP);
      else if (kind === "R") this.slideMoves(list, sq, piece, ROOK);
      else if (kind === "Q") this.slideMoves(list, sq, piece, BISHOP.concat(ROOK));
      else if (kind === "K") this.kingMoves(list, sq, piece, white);
    }
    return list;
  };

  Chess.prototype.pawnMoves = function (list, sq, piece, white) {
    var dir = white ? 8 : -8;
    var startRank = white ? 1 : 6;
    var promoRank = white ? 7 : 0;
    var one = sq + dir;
    if (onBoard(one) && Math.abs(fileOf(one) - fileOf(sq)) === 0 && !this.board[one]) {
      this.addPawn(list, sq, one, piece, "", rankOf(one) === promoRank);
      if (rankOf(sq) === startRank) {
        var two = sq + dir * 2;
        if (!this.board[two]) this.addPawn(list, sq, two, piece, "", false);
      }
    }
    var caps = white ? [7, 9] : [-7, -9];
    var c;
    for (c = 0; c < caps.length; c++) {
      var to = sq + caps[c];
      if (!onBoard(to) || Math.abs(fileOf(to) - fileOf(sq)) !== 1) continue;
      var occ = this.board[to];
      if (occ && !sidePiece(occ, white)) {
        this.addPawn(list, sq, to, piece, occ, rankOf(to) === promoRank);
      }
    }
    if (this.ep >= 0) {
      var epRank = white ? 5 : 2;
      var pawnRank = white ? 4 : 3;
      var capSq = this.ep + (white ? -8 : 8);
      var victim = white ? "p" : "P";
      if (rankOf(sq) === pawnRank && rankOf(this.ep) === epRank &&
          Math.abs(fileOf(this.ep) - fileOf(sq)) === 1 &&
          !this.board[this.ep] && this.board[capSq] === victim) {
        pushMove(list, sq, this.ep, piece, victim, "", "", true);
      }
    }
  };

  Chess.prototype.addPawn = function (list, from, to, piece, captured, promote) {
    if (!promote) {
      pushMove(list, from, to, piece, captured, "", "", false);
      return;
    }
    var options = piece === "P" ? ["Q", "R", "B", "N"] : ["q", "r", "b", "n"];
    var i;
    for (i = 0; i < options.length; i++) {
      pushMove(list, from, to, piece, captured, options[i], "", false);
    }
  };

  Chess.prototype.stepMoves = function (list, sq, piece, deltas) {
    var white = isWhitePiece(piece);
    var i;
    for (i = 0; i < deltas.length; i++) {
      var to = sq + deltas[i];
      if (!onBoard(to)) continue;
      var df = Math.abs(fileOf(to) - fileOf(sq));
      var dr = Math.abs(rankOf(to) - rankOf(sq));
      var knight = (df === 1 && dr === 2) || (df === 2 && dr === 1);
      var king = df <= 1 && dr <= 1 && (df + dr) > 0;
      if (deltas === KNIGHT ? !knight : !king) continue;
      var occ = this.board[to];
      if (occ && sidePiece(occ, white)) continue;
      pushMove(list, sq, to, piece, occ, "", "", false);
    }
  };

  Chess.prototype.slideMoves = function (list, sq, piece, deltas) {
    var white = isWhitePiece(piece);
    var d;
    for (d = 0; d < deltas.length; d++) {
      var prev = sq;
      var delta = deltas[d];
      for (;;) {
        var to = prev + delta;
        if (!onBoard(to) || Math.abs(fileOf(to) - fileOf(prev)) > 1) break;
        var occ = this.board[to];
        if (!occ) {
          pushMove(list, sq, to, piece, "", "", "", false);
        } else {
          if (!sidePiece(occ, white)) pushMove(list, sq, to, piece, occ, "", "", false);
          break;
        }
        prev = to;
      }
    }
  };

  Chess.prototype.kingMoves = function (list, sq, piece, white) {
    this.stepMoves(list, sq, piece, KING);
    var board = this.board;
    var enemyWhite = !white;
    if (white && sq === 4 && board[4] === "K") {
      if (this.castle.K && board[7] === "R" && !board[5] && !board[6] &&
          !this.attacked(4, enemyWhite) && !this.attacked(5, enemyWhite) && !this.attacked(6, enemyWhite)) {
        pushMove(list, 4, 6, piece, "", "", "K", false);
      }
      if (this.castle.Q && board[0] === "R" && !board[1] && !board[2] && !board[3] &&
          !this.attacked(4, enemyWhite) && !this.attacked(3, enemyWhite) && !this.attacked(2, enemyWhite)) {
        pushMove(list, 4, 2, piece, "", "", "Q", false);
      }
    }
    if (!white && sq === 60 && board[60] === "k") {
      if (this.castle.k && board[63] === "r" && !board[61] && !board[62] &&
          !this.attacked(60, enemyWhite) && !this.attacked(61, enemyWhite) && !this.attacked(62, enemyWhite)) {
        pushMove(list, 60, 62, piece, "", "", "k", false);
      }
      if (this.castle.q && board[56] === "r" && !board[57] && !board[58] && !board[59] &&
          !this.attacked(60, enemyWhite) && !this.attacked(59, enemyWhite) && !this.attacked(58, enemyWhite)) {
        pushMove(list, 60, 58, piece, "", "", "q", false);
      }
    }
  };

  Chess.prototype.legalMoves = function () {
    var pseudo = this.pseudoMoves();
    var out = [];
    var i;
    for (i = 0; i < pseudo.length; i++) {
      this.make(pseudo[i]);
      var moverWhite = this.turn === "b";
      var safe = !this.attacked(this.findKing(moverWhite), !moverWhite);
      this.unmake();
      if (safe) out.push(pseudo[i]);
    }
    return out;
  };

  Chess.prototype.make = function (move) {
    var board = this.board;
    var piece = move.piece;
    var captured = move.captured;
    if (move.ep) {
      var capSq = move.to + (piece === "P" ? -8 : 8);
      captured = board[capSq];
      board[capSq] = "";
      move.captured = captured;
      move.epCapSq = capSq;
    }
    board[move.from] = "";
    board[move.to] = move.promotion || piece;
    if (move.castle) {
      var rookFrom = 0;
      var rookTo = 0;
      if (move.to === 6) { rookFrom = 7; rookTo = 5; }
      else if (move.to === 2) { rookFrom = 0; rookTo = 3; }
      else if (move.to === 62) { rookFrom = 63; rookTo = 61; }
      else if (move.to === 58) { rookFrom = 56; rookTo = 59; }
      board[rookTo] = board[rookFrom];
      board[rookFrom] = "";
      move.rookFrom = rookFrom;
      move.rookTo = rookTo;
    }
    move.prevCastle = { K: this.castle.K, Q: this.castle.Q, k: this.castle.k, q: this.castle.q };
    move.prevEp = this.ep;
    move.prevHalf = this.half;
    move.prevFull = this.full;
    move.prevTurn = this.turn;
    if (piece === "K") { this.castle.K = false; this.castle.Q = false; }
    if (piece === "k") { this.castle.k = false; this.castle.q = false; }
    if (move.from === 0 || move.to === 0) this.castle.Q = false;
    if (move.from === 7 || move.to === 7) this.castle.K = false;
    if (move.from === 56 || move.to === 56) this.castle.q = false;
    if (move.from === 63 || move.to === 63) this.castle.k = false;
    var pawn = piece === "P" || piece === "p";
    this.half = (pawn || captured || move.ep) ? 0 : this.half + 1;
    if (this.turn === "b") this.full += 1;
    this.ep = -1;
    if (piece === "P" && move.to - move.from === 16) this.ep = move.from + 8;
    if (piece === "p" && move.from - move.to === 16) this.ep = move.from - 8;
    this.turn = this.turn === "w" ? "b" : "w";
    var key = this.key();
    this.seen[key] = (this.seen[key] || 0) + 1;
    move.key = key;
    this.hist.push(move);
    return move;
  };

  Chess.prototype.unmake = function () {
    var move = this.hist.pop();
    if (!move) throw new Error("unmake");
    this.seen[move.key] = (this.seen[move.key] || 1) - 1;
    if (this.seen[move.key] <= 0) delete this.seen[move.key];
    var board = this.board;
    if (move.castle) {
      board[move.rookFrom] = board[move.rookTo];
      board[move.rookTo] = "";
    }
    board[move.to] = "";
    board[move.from] = move.piece;
    if (move.ep) board[move.epCapSq] = move.captured;
    else if (move.captured) board[move.to] = move.captured;
    this.castle = move.prevCastle;
    this.ep = move.prevEp;
    this.half = move.prevHalf;
    this.full = move.prevFull;
    this.turn = move.prevTurn;
    return move;
  };

  Chess.prototype.inCheck = function () {
    var white = this.turn === "w";
    return this.attacked(this.findKing(white), !white);
  };

  Chess.prototype.insufficient = function () {
    var minors = [];
    var i;
    for (i = 0; i < 64; i++) {
      var p = this.board[i];
      if (!p || p === "K" || p === "k") continue;
      var kind = p.toUpperCase();
      if (kind === "P" || kind === "R" || kind === "Q") return false;
      minors.push({ piece: p, sq: i });
    }
    if (minors.length <= 1) return true;
    if (minors.length === 2 && minors[0].piece.toUpperCase() === "B" && minors[1].piece.toUpperCase() === "B") {
      var a = (fileOf(minors[0].sq) + rankOf(minors[0].sq)) & 1;
      var b = (fileOf(minors[1].sq) + rankOf(minors[1].sq)) & 1;
      return a === b;
    }
    return false;
  };

  Chess.prototype.status = function () {
    var moves = this.legalMoves();
    if (moves.length === 0) return this.inCheck() ? "checkmate" : "stalemate";
    if (this.half >= 100) return "fifty-move";
    if ((this.seen[this.key()] || 0) >= 3) return "threefold";
    if (this.insufficient()) return "insufficient-material";
    if (this.inCheck()) return "check";
    return "active";
  };

  Chess.prototype.result = function () {
    var st = this.status();
    if (st === "checkmate") {
      return { kind: this.turn === "w" ? "black" : "white", reason: "checkmate" };
    }
    if (st === "stalemate" || st === "fifty-move" || st === "threefold" || st === "insufficient-material") {
      return { kind: "draw", reason: st };
    }
    return null;
  };

  Chess.prototype.uci = function (move) {
    return alg(move.from) + alg(move.to) + (move.promotion ? move.promotion.toLowerCase() : "");
  };

  function baseSan(chess, move) {
    if (move.castle === "K" || move.castle === "k") {
      return (move.to === 6 || move.to === 62) ? "O-O" : "O-O-O";
    }
    var promo = move.promotion ? "=" + move.promotion.toUpperCase() : "";
    if (move.piece === "P" || move.piece === "p") {
      if (move.captured || move.ep) return alg(move.from).charAt(0) + "x" + alg(move.to) + promo;
      return alg(move.to) + promo;
    }
    var letter = move.piece.toUpperCase();
    var moves = chess.legalMoves();
    var sameFile = false;
    var sameRank = false;
    var any = false;
    var i;
    for (i = 0; i < moves.length; i++) {
      var m = moves[i];
      if (m.from === move.from) continue;
      if (m.to !== move.to) continue;
      if (m.piece.toUpperCase() !== letter) continue;
      any = true;
      if (fileOf(m.from) === fileOf(move.from)) sameFile = true;
      if (rankOf(m.from) === rankOf(move.from)) sameRank = true;
    }
    var dis = "";
    if (any) {
      if (!sameFile) dis = alg(move.from).charAt(0);
      else if (!sameRank) dis = String(rankOf(move.from) + 1);
      else dis = alg(move.from);
    }
    var cap = (move.captured || move.ep) ? "x" : "";
    return letter + dis + cap + alg(move.to) + promo;
  }

  function san(chess, move) {
    var base = baseSan(chess, move);
    chess.make(move);
    var mate = chess.legalMoves().length === 0 && chess.inCheck();
    var check = chess.inCheck();
    chess.unmake();
    if (mate) return base + "#";
    if (check) return base + "+";
    return base;
  }

  Chess.prototype.playUci = function (uci) {
    var moves = this.legalMoves();
    var i;
    for (i = 0; i < moves.length; i++) {
      if (this.uci(moves[i]) === uci) {
        this.make(moves[i]);
        return moves[i];
      }
    }
    return null;
  };

  function perft(chess, depth) {
    var moves = chess.legalMoves();
    if (depth === 1) return moves.length;
    var n = 0;
    var i;
    for (i = 0; i < moves.length; i++) {
      chess.make(moves[i]);
      n += perft(chess, depth - 1);
      chess.unmake();
    }
    return n;
  }

  return {
    START: START,
    Chess: Chess,
    alg: alg,
    algToSq: algToSq,
    san: san,
    perft: perft
  };
});
