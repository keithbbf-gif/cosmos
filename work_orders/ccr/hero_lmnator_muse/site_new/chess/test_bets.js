var fs = require("fs");
var path = require("path");
var bets = require("./bets.js");
var config = require("./config.js");

function fail(msg) {
  console.error("FAIL " + msg);
  process.exit(1);
}

function eq(got, want, msg) {
  if (got !== want) fail(msg + " got " + JSON.stringify(got) + " want " + JSON.stringify(want));
}

var src = fs.readFileSync(path.join(__dirname, "bets.js"), "utf8");
if (src.indexOf("0.05") >= 0) fail("house cut hard-coded in bets.js");
eq(config.houseCutRate, 0.05, "default cut");
eq(config.refundOnDraw, "full-stake", "draw policy");
eq(config.refundOnAbort, "full-stake", "abort policy");

function book(rate) {
  return bets.createBook({
    houseCutRate: rate,
    refundOnDraw: config.refundOnDraw,
    refundOnAbort: config.refundOnAbort,
    noWinnerPolicy: config.noWinnerPolicy,
    currency: config.currency
  });
}

function returned(settlement, id) {
  var i;
  for (i = 0; i < settlement.payouts.length; i++) {
    if (settlement.payouts[i].id === id) return settlement.payouts[i].returned;
  }
  return null;
}

var open = book(config.houseCutRate);
bets.placeBet(open, { id: "w", name: "Ada", side: "white", amount: 60 });
bets.placeBet(open, { id: "k", name: "Bo", side: "black", amount: 40 });
var cancelled = bets.cancelBet(open, "k");
eq(cancelled.amount, 40, "cancel amount");
eq(open.bets.length, 1, "one bet left");
bets.placeBet(open, { id: "k", name: "Bo", side: "black", amount: 40 });
var lockedThrow = false;
try { bets.lock(open); bets.placeBet(open, { id: "z", name: "You", side: "white", amount: 1 }); }
catch (e) { lockedThrow = e.message === "window-closed"; }
if (!lockedThrow) fail("lock did not close the window");

var win = bets.settle(open, { kind: "white" });
eq(win.stakes, 100, "stakes");
eq(win.house, 5, "house 5%");
eq(win.pool, 95, "pool");
eq(returned(win, "w"), 95, "winner takes pool");
eq(returned(win, "k"), 0, "loser");
eq(open.state, "settled", "settled");

var cut10 = book(0.1);
bets.placeBet(cut10, { id: "w", name: "Ada", side: "white", amount: 60 });
bets.placeBet(cut10, { id: "k", name: "Bo", side: "black", amount: 40 });
bets.lock(cut10);
var win10 = bets.settle(cut10, { kind: "white" });
eq(win10.house, 10, "house follows book rate");
eq(win10.pool, 90, "pool at 10%");

var split = book(0.05);
bets.placeBet(split, { id: "a", name: "Ada", side: "white", amount: 10 });
bets.placeBet(split, { id: "b", name: "Bo", side: "white", amount: 20 });
bets.placeBet(split, { id: "c", name: "Cy", side: "white", amount: 30 });
bets.placeBet(split, { id: "d", name: "Di", side: "black", amount: 40 });
bets.lock(split);
var parts = bets.settle(split, { kind: "white" });
eq(parts.pool, 95, "split pool");
eq(returned(parts, "a") + returned(parts, "b") + returned(parts, "c"), 95, "shares sum to pool");
eq(returned(parts, "d"), 0, "black share");

var drawn = book(0.05);
bets.placeBet(drawn, { id: "w", name: "Ada", side: "white", amount: 60 });
bets.placeBet(drawn, { id: "k", name: "Bo", side: "black", amount: 40 });
bets.lock(drawn);
var draw = bets.settle(drawn, { kind: "draw" });
eq(draw.reason, "draw", "draw reason");
eq(draw.house, 0, "no house on draw");
eq(returned(draw, "w"), 60, "draw refund white");
eq(returned(draw, "k"), 40, "draw refund black");
eq(drawn.state, "refunded", "draw state");

var aborted = book(0.05);
bets.placeBet(aborted, { id: "w", name: "Ada", side: "white", amount: 60 });
var abort = bets.settle(aborted, { kind: "abort" });
eq(abort.reason, "abort", "abort from open");
eq(returned(abort, "w"), 60, "abort refund");
eq(abort.house, 0, "no house on abort");

var none = book(0.05);
bets.placeBet(none, { id: "k", name: "Bo", side: "black", amount: 40 });
bets.lock(none);
var missed = bets.settle(none, { kind: "white" });
eq(missed.reason, "no-winning-bets", "no winner");
eq(returned(missed, "k"), 40, "refund when nobody picked the winner");
eq(missed.house, 0, "no house when refunded");

var odd = book(0.05);
bets.placeBet(odd, { id: "w", name: "Ada", side: "white", amount: 30 });
bets.lock(odd);
var rounded = bets.settle(odd, { kind: "white" });
eq(rounded.house, 2, "Math.round 1.5 to 2");
eq(rounded.pool, 28, "pool after round");
eq(returned(rounded, "w"), 28, "sole winner gets pool");

console.log("BETS_OK");
