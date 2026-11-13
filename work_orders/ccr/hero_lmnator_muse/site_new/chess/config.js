(function (root, factory) {
  var api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  root.LMN_CHESS_CONFIG = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  return {
    schema: "lmn-chess-config/1",
    currency: "play-money-mock",
    houseCutRate: 0.05,
    refundOnDraw: "full-stake",
    refundOnAbort: "full-stake",
    noWinnerPolicy: "full-stake",
    maxPlies: 400,
    gf38Note: "off per Keith; future calls only via Joanna Vertex account after Keith re-enables",
    blindNote: "Blind hides the name on this page. The id stays in this browser. A server has to withhold it before the agent is actually unknown."
  };
});
