(function () {
  var root = document.getElementById("line-root");
  var meta = document.getElementById("line-meta");
  if (!root) return;

  var RINGS = [
    ["still_standing", "Still standing", "Highest empirical score in the catalog. A keep on the dyno, not a poster."],
    ["cheap_seat", "Cheap seat", "Lowest listed prompt price among models that already have a score."],
    ["open_weighin", "Open weigh-in", "Highest score among rows whose weights say open. Inspection is not a win by itself."],
    ["headroom", "Headroom", "Largest gap between the high projection and the score already on the card."]
  ];

  function text(value) {
    return value === null || value === undefined || value === "" ? "—" : String(value);
  }

  function money(value) {
    return typeof value === "number" ? "$" + value + " / M" : "—";
  }

  function slip(row) {
    var bits = [
      text(row.maker),
      text(row.weights),
      "ctx " + text(row.context_length),
      "in " + money(row.prompt_price_per_m),
      "out " + money(row.completion_price_per_m)
    ];
    return (
      '<article class="slip keep"><div class="slip-stub">' + text(row.empirical_score) + '</div>' +
      '<div class="slip-body"><h3>' + text(row.name) + '</h3>' +
      '<p class="price">' + bits.join(" · ") + '</p>' +
      '<p>' + text(row.what_it_is_for) + '</p></div></article>'
    );
  }

  function draw(board) {
    var when = board.updated_at ? board.updated_at : "unknown time";
    meta.textContent = board.total_models + " engines in the catalog. Cut taken " + when + ". Source: mdata.modelraters.com/v1/leaderboard.json";
    root.innerHTML = RINGS.map(function (ring) {
      var rows = board.rings[ring[0]] || [];
      return '<section class="ring" aria-label="' + ring[1] + '"><h2>' + ring[1] + '</h2><p class="secondary">' + ring[2] + '</p>' +
        rows.map(slip).join("") + '</section>';
    }).join("");
  }

  fetch("board.json")
    .then(function (res) { if (!res.ok) throw new Error("catalog"); return res.json(); })
    .then(draw)
    .catch(function () { meta.textContent = "The catalog file did not load."; });
})();
