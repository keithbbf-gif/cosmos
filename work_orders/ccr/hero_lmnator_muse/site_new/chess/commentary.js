(function (root, factory) {
  var api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  root.LMNChessTalk = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  var NAMES = { P: "Pawn", N: "Knight", B: "Bishop", R: "Rook", Q: "Queen", K: "King" };

  function commentMove(entry, index) {
    var side = entry.color === "w" ? "White" : "Black";
    var n = Math.floor(index / 2) + 1;
    var piece = NAMES[String(entry.piece || "").toUpperCase()] || "Piece";
    var parts = [
      "Move " + n + ". " + side + " plays " + entry.san + ".",
      piece + " goes from " + entry.from + " to " + entry.to + "."
    ];
    if (entry.ep) parts.push("En passant capture.");
    else if (entry.capture) parts.push("Capture.");
    if (entry.castle) parts.push("Castling.");
    if (entry.promotion) parts.push("Promotion to " + entry.promotion + ".");
    if (entry.mate) parts.push("Checkmate.");
    else if (entry.check) parts.push("Check.");
    parts.push("Mock commentary from the move list. Not a claim about a model.");
    return parts.join(" ");
  }

  return { commentMove: commentMove };
});
