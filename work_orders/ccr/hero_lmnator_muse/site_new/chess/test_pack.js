var fs = require("fs");
var path = require("path");
var vm = require("vm");

function fail(msg) {
  console.error("FAIL " + msg);
  process.exit(1);
}

var file = path.join(__dirname, "..", "pack-teamF-chess.js");
var code = fs.readFileSync(file, "utf8");
if (code.indexOf("LMN_PACK = {}") >= 0 || code.indexOf("LMN_PACK={}") >= 0) fail("pack replaces the array");
var window = { LMN_PACK: [{ id: "s01" }] };
vm.runInNewContext(code, { window: window });
if (!Array.isArray(window.LMN_PACK)) fail("not an array");
if (window.LMN_PACK[0].id !== "s01") fail("existing entry dropped");
var ids = {};
window.LMN_PACK.forEach(function (row) {
  if (!row || !row.id) fail("missing id");
  if (ids[row.id]) fail("duplicate " + row.id);
  ids[row.id] = true;
});
["t901", "t902", "t903", "t904"].forEach(function (id) {
  if (!ids[id]) fail("missing " + id);
  var n = parseInt(id.slice(1), 10);
  if (n < 901) fail("id below t901");
});
var added = window.LMN_PACK.filter(function (row) { return String(row.id).charAt(0) === "t"; });
if (added.length !== 4) fail("count " + added.length);
added.forEach(function (row) {
  if (row.players !== "multi") fail("players");
  if (row.engine !== "chess") fail("engine");
  if (row.blurb !== "After Chess") fail("blurb");
});
console.log("PACK_OK " + added.length);
