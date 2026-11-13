(function (root, factory) {
  var api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  root.LMNChessBets = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  function isPositiveInt(n) {
    return typeof n === "number" && isFinite(n) && n > 0 && Math.floor(n) === n;
  }

  function createBook(opts) {
    if (!opts || typeof opts.houseCutRate !== "number" || !isFinite(opts.houseCutRate)) throw new Error("houseCutRate");
    if (opts.houseCutRate < 0 || opts.houseCutRate >= 1) throw new Error("houseCutRate");
    if (opts.refundOnDraw !== "full-stake") throw new Error("refundOnDraw");
    if (opts.refundOnAbort !== "full-stake") throw new Error("refundOnAbort");
    if (opts.noWinnerPolicy !== "full-stake") throw new Error("noWinnerPolicy");
    return {
      state: "open",
      currency: opts.currency || "play-money-mock",
      houseCutRate: opts.houseCutRate,
      refundOnDraw: opts.refundOnDraw,
      refundOnAbort: opts.refundOnAbort,
      noWinnerPolicy: opts.noWinnerPolicy,
      bets: [],
      seq: 1,
      settlement: null
    };
  }

  function placeBet(book, bet) {
    if (!book || book.state !== "open") throw new Error("window-closed");
    if (!bet || (bet.side !== "white" && bet.side !== "black")) throw new Error("side");
    if (!isPositiveInt(bet.amount)) throw new Error("amount");
    var id = bet.id ? String(bet.id) : "b" + book.seq;
    var i;
    for (i = 0; i < book.bets.length; i++) if (book.bets[i].id === id) throw new Error("id");
    book.seq += 1;
    var row = {
      id: id,
      name: String(bet.name || "spectator").replace(/[\r\n]/g, " ").slice(0, 24),
      side: bet.side,
      amount: bet.amount
    };
    book.bets.push(row);
    return row;
  }

  function cancelBet(book, id) {
    if (!book || book.state !== "open") throw new Error("window-closed");
    var next = [];
    var found = null;
    var i;
    for (i = 0; i < book.bets.length; i++) {
      if (!found && book.bets[i].id === id) found = book.bets[i];
      else next.push(book.bets[i]);
    }
    if (!found) throw new Error("missing");
    book.bets = next;
    return found;
  }

  function lock(book) {
    if (!book || book.state !== "open") throw new Error("state");
    book.state = "locked";
    return book;
  }

  function sum(rows) {
    var n = 0;
    var i;
    for (i = 0; i < rows.length; i++) n += rows[i].amount;
    return n;
  }

  function finish(book, state, settlement) {
    book.state = state;
    book.settlement = settlement;
    return settlement;
  }

  function refund(book, reason) {
    var payouts = [];
    var i;
    for (i = 0; i < book.bets.length; i++) {
      var b = book.bets[i];
      payouts.push({ id: b.id, name: b.name, side: b.side, amount: b.amount, returned: b.amount });
    }
    return finish(book, "refunded", {
      reason: reason,
      currency: book.currency,
      stakes: sum(book.bets),
      house: 0,
      pool: 0,
      houseCutRate: book.houseCutRate,
      payouts: payouts
    });
  }

  function settle(book, result) {
    if (!book || !result) throw new Error("result");
    var kind = result.kind;
    if (kind !== "white" && kind !== "black" && kind !== "draw" && kind !== "abort") throw new Error("result");
    if (kind === "abort") {
      if (book.state !== "open" && book.state !== "locked") throw new Error("state");
      if (book.refundOnAbort !== "full-stake") throw new Error("refundOnAbort");
      return refund(book, "abort");
    }
    if (book.state !== "locked") throw new Error("state");
    if (kind === "draw") {
      if (book.refundOnDraw !== "full-stake") throw new Error("refundOnDraw");
      return refund(book, "draw");
    }
    var winners = [];
    var i;
    for (i = 0; i < book.bets.length; i++) if (book.bets[i].side === kind) winners.push(book.bets[i]);
    if (!winners.length) {
      if (book.noWinnerPolicy !== "full-stake") throw new Error("noWinnerPolicy");
      return refund(book, "no-winning-bets");
    }
    var stakes = sum(book.bets);
    var winStake = sum(winners);
    var house = Math.round(stakes * book.houseCutRate);
    if (house < 0) house = 0;
    if (house > stakes) house = stakes;
    var pool = stakes - house;
    var returnedById = {};
    var allocated = 0;
    for (i = 0; i < winners.length; i++) {
      var share;
      if (i === winners.length - 1) share = pool - allocated;
      else {
        share = Math.floor(pool * winners[i].amount / winStake);
        allocated += share;
      }
      returnedById[winners[i].id] = share;
    }
    var payouts = [];
    for (i = 0; i < book.bets.length; i++) {
      var b = book.bets[i];
      payouts.push({
        id: b.id,
        name: b.name,
        side: b.side,
        amount: b.amount,
        returned: returnedById[b.id] || 0
      });
    }
    return finish(book, "settled", {
      reason: kind,
      currency: book.currency,
      stakes: stakes,
      house: house,
      pool: pool,
      houseCutRate: book.houseCutRate,
      payouts: payouts
    });
  }

  return {
    createBook: createBook,
    placeBet: placeBet,
    cancelBet: cancelBet,
    lock: lock,
    settle: settle
  };
});
