(function (root, factory) {
  var api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  root.LMNChessBench = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  function row(choice) {
    var offered = choice.legal_moves_offered;
    var illegal = choice.illegal_attempts;
    var rate = null;
    if (typeof offered === "number" && offered > 0 && typeof illegal === "number") {
      rate = (offered - illegal) / offered;
    }
    return {
      label: "mock",
      model_label: choice.model_label || "",
      seats_id: choice.seats_id || null,
      uci: choice.uci || "",
      legal_moves_offered: offered,
      illegal_attempts: illegal,
      legal_move_rate: rate,
      result: choice.result || null,
      latency_ms: choice.latency_ms,
      tokens_in: null,
      tokens_out: null,
      token_note: "mock opponent does not report tokens",
      prompt_stored: false,
      response_stored: false
    };
  }

  function summary(rows, result) {
    var offered = 0;
    var illegal = 0;
    var latency = 0;
    var i;
    for (i = 0; i < rows.length; i++) {
      offered += rows[i].legal_moves_offered || 0;
      illegal += rows[i].illegal_attempts || 0;
      latency += rows[i].latency_ms || 0;
    }
    return {
      label: "mock",
      moves: rows.length,
      legal_moves_offered: offered,
      illegal_attempts: illegal,
      legal_move_rate: offered > 0 ? (offered - illegal) / offered : null,
      result: result || null,
      latency_ms: latency,
      tokens_in: null,
      tokens_out: null,
      token_note: "mock opponent does not report tokens",
      prompt_stored: false,
      response_stored: false
    };
  }

  return { row: row, summary: summary };
});
