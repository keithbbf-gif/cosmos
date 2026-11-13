var fs = require("fs");
var models = require("./models.js");
var mock = require("./mock_opponent.js");
var rules = require("./chess_rules.js");
var talk = require("./commentary.js");
var bench = require("./bench.js");
var bets = require("./bets.js");
var config = require("./config.js");

function fail(msg) {
  console.error("FAIL " + msg);
  process.exit(1);
}

function eq(got, want, msg) {
  if (got !== want) fail(msg + " got " + JSON.stringify(got) + " want " + JSON.stringify(want));
}

var seatsPath = "V:\\A\\Ai\\COSMOS\\tokenctr\\mdata\\src\\seats.json";
var seats = JSON.parse(fs.readFileSync(seatsPath, "utf8"));
var ids = Object.keys(seats);
eq(Object.keys(models.SEATS).length, ids.length, "seat count");
ids.forEach(function (id) {
  if (models.SEATS[id] !== seats[id]) fail("seat mismatch " + id);
});
eq(ids.length, 54, "54 seats");

var gf = null;
var muse = null;
models.NAMED.forEach(function (row) {
  if (row.key === "gf38") gf = row;
  if (row.key === "muse13") muse = row;
  if (row.seats_id && !seats[row.seats_id]) fail("invented id " + row.seats_id);
  if (row.rating != null || row.empirical_score != null) fail("invented rating " + row.key);
});
eq(gf.enabled, false, "gf38 off");
eq(gf.seats_id, null, "gf38 has no seats id");
eq(gf.note, config.gf38Note, "gf38 note");
eq(muse.seats_id, "meta/muse-spark-1.3-contributor", "muse id");
eq(models.byKey("spark").seats_id, null, "spark has no id");
eq(models.enabled().some(function (m) { return m.key === "gf38"; }), false, "gf38 not playable");

var threw = false;
try { mock.choose(gf, new rules.Chess()); } catch (e) { threw = e.code === "model-off"; }
if (!threw) fail("gf38 choose should throw");

var spark = models.byKey("spark");
var a = mock.choose(spark, new rules.Chess());
var b = mock.choose(spark, new rules.Chess());
eq(a.uci, b.uci, "deterministic");
eq(a.illegal_attempts, 0, "no illegal attempts");
eq(a.tokens_in, null, "no token in");
eq(a.tokens_out, null, "no token out");
eq(a.label, "mock", "labelled mock");
if (typeof a.latency_ms !== "number" || a.latency_ms < 0) fail("latency");
var probe = new rules.Chess();
if (!probe.playUci(a.uci)) fail("mock move illegal " + a.uci);

var grok = models.byKey("grok47");
var sim = mock.playSim(spark, grok, 6);
eq(sim.log.length, 6, "six plies");
sim.log.forEach(function (choice) {
  if (choice.illegal_attempts !== 0) fail("sim illegal");
  if (choice.label !== "mock") fail("sim label");
});
eq(sim.result.kind, "abort", "short sim aborts at max plies");

var book = bets.createBook({
  houseCutRate: config.houseCutRate,
  refundOnDraw: config.refundOnDraw,
  refundOnAbort: config.refundOnAbort,
  noWinnerPolicy: config.noWinnerPolicy
});
bets.placeBet(book, { id: "w", name: "Ada", side: "white", amount: 25 });
bets.placeBet(book, { id: "k", name: "Bo", side: "black", amount: 15 });
bets.lock(book);
var settled = bets.settle(book, sim.result);
eq(settled.reason, "abort", "sim abort settles");
eq(settled.house, 0, "sim abort no house");

var line = talk.commentMove({
  color: "w",
  san: "Nf3",
  piece: "N",
  from: "g1",
  to: "f3",
  capture: false,
  ep: false,
  castle: "",
  promotion: "",
  check: false,
  mate: false
}, 0);
if (line.indexOf("Mock commentary from the move list. Not a claim about a model.") < 0) fail("disclaimer");
if (/blunder|brilliant|prefers|thinks|style/i.test(line)) fail("model claim in commentary");

var brow = bench.row(a);
eq(brow.label, "mock", "bench label");
eq(brow.prompt_stored, false, "no prompt");
eq(brow.response_stored, false, "no response");
eq(brow.tokens_in, null, "bench tokens");
eq(brow.legal_move_rate, 1, "legal rate");
var sum = bench.summary([brow], { kind: "abort", reason: "test" });
eq(sum.result.kind, "abort", "bench summary");
eq(sum.label, "mock", "summary label");

var blind = models.pickBlind(models.enabled(), function () { return 0; });
eq(blind.key, models.enabled()[0].key, "blind rng");
if (blind.key === "gf38") fail("blind picked gf38");

console.log("MOCK_OK seats " + ids.length);
