(function () {
  window.LMN_SAVE = function (record) {
    var match = window.LMN_MATCH || {};
    var body = record || {};
    body.match_id = match.id || body.match_id || "";
    body.seed = match.seed || body.seed || 0;
    if (match.seats) {
      body.seats = match.seats.map(function (s) {
        return { role: s.role, kind: s.kind, ai: s.kind === "ai" ? s.name : "" };
      });
    }
    var pid = window.LMN_PID || "run";
    return fetch("queue.php", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ op: "save", pid: pid, record: body })
    }).catch(function () { return null; });
  };
  window.LMN_MODEL = function (row) {
    if (!row) return {};
    return {
      dossier_id: row.dossier_id || "",
      name: row.name || "",
      maker: row.maker || "",
      empirical_score: row.empirical_score,
      prompt_price_per_m: row.prompt_price_per_m,
      context_length: row.context_length,
      weights: row.weights || ""
    };
  };
})();
