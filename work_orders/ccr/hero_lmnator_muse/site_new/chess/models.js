(function (root, factory) {
  var config = (typeof module === "object" && module.exports) ? require("./config.js") : root.LMN_CHESS_CONFIG;
  var api = factory(config || { gf38Note: "" });
  if (typeof module === "object" && module.exports) module.exports = api;
  root.LMNChessModels = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function (config) {
  var SEATS = {
    "anthropic/claude-haiku-5.5": "anthropic_claude-haiku-5.5",
    "bytedance-seed/seed-1.6-flash": "bytedance-seed_seed-1.6-flash",
    "bytedance-seed/seed-2.0-mini": "bytedance-seed_seed-2.0-mini",
    "cohere/north-mini-code:free": "cohere_north-mini-code_free",
    "dots-studio/dots-3-note-preview:free": "dots-studio_dots-3-note-preview_free",
    "google/gemma-4-26b-a4b-it": "google_gemma-4-26b-a4b-it",
    "google/gemma-4-26b-a4b-it:free": "google_gemma-4-26b-a4b-it_free",
    "google/gemma-4-31b-it": "google_gemma-4-31b-it",
    "google/gemma-4-31b-it:free": "google_gemma-4-31b-it_free",
    "google/lyria-3-clip-preview": "google_lyria-3-clip-preview",
    "google/lyria-3-pro-preview": "google_lyria-3-pro-preview",
    "ibm-granite/granite-4.0-h-micro": "ibm-granite_granite-4.0-h-micro",
    "ibm-granite/granite-4.2-8b": "ibm-granite_granite-4.2-8b",
    "inception/mercury-2.5": "inception_mercury-2.5",
    "inclusionai/ling-3.0-flash": "inclusionai_ling-3.0-flash",
    "inclusionai/ling-3.0-flash-vl": "inclusionai_ling-3.0-flash-vl",
    "inclusionai/ling-3.1-flash": "inclusionai_ling-3.1-flash",
    "inference-net/schematron-v2-small": "inference-net_schematron-v2-small",
    "inference-net/schematron-v2-turbo": "inference-net_schematron-v2-turbo",
    "liquid/lfm-2.5-2.6b:free": "liquid_lfm-2.5-2.6b_free",
    "meta/muse-spark-1.2-contributor": "meta_muse-spark-1.2-contributor",
    "meta/muse-spark-1.3-contributor": "meta_muse-spark-1.3-contributor",
    "mistralai/ministral-3b-2512": "mistralai_ministral-3b-2512",
    "mistralai/voxtral-small-24b-2507": "mistralai_voxtral-small-24b-2507",
    "nex-agi/nex-n2.5-mini": "nex-agi_nex-n2.5-mini",
    "nex-agi/nex-n2.5-pro": "nex-agi_nex-n2.5-pro",
    "nvidia/nemotron-3-nano-30b-a3b": "nvidia_nemotron-3-nano-30b-a3b",
    "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free": "nvidia_nemotron-3-nano-omni-30b-a3b-reasoning_free",
    "nvidia/nemotron-3-super-120b-a12b": "nvidia_nemotron-3-super-120b-a12b",
    "nvidia/nemotron-3-super-120b-a12b:free": "nvidia_nemotron-3-super-120b-a12b_free",
    "nvidia/nemotron-3-ultra-550b-a55b:free": "nvidia_nemotron-3-ultra-550b-a55b_free",
    "nvidia/nemotron-3.5-content-safety:free": "nvidia_nemotron-3.5-content-safety_free",
    "nvidia/nemotron-3.5-lightning": "nvidia_nemotron-3.5-lightning",
    "nvidia/nemotron-3.5-lightning:free": "nvidia_nemotron-3.5-lightning_free",
    "openai/gpt-oss-safeguard-20b": "openai_gpt-oss-safeguard-20b",
    "poolside/laguna-s-2.1": "poolside_laguna-s-2.1",
    "poolside/laguna-s-2.1:free": "poolside_laguna-s-2.1_free",
    "poolside/laguna-xs-2.1": "poolside_laguna-xs-2.1",
    "poolside/laguna-xs-2.1:free": "poolside_laguna-xs-2.1_free",
    "prism-ml/ternary-bonsai-2-27b": "prism-ml_ternary-bonsai-2-27b",
    "qwen/qwen3.5-9b": "qwen_qwen3.5-9b",
    "qwen/qwen3.5-flash-02-23": "qwen_qwen3.5-flash-02-23",
    "qwen/qwen3.7-flash": "qwen_qwen3.7-flash",
    "rekaai/reka-edge": "rekaai_reka-edge",
    "stepfun/step-3.5-flash": "stepfun_step-3.5-flash",
    "tencent/hy-mt2-1.8b": "tencent_hy-mt2-1.8b",
    "tencent/hy-mt2-30b-a3b": "tencent_hy-mt2-30b-a3b",
    "tencent/hy-mt2-7b": "tencent_hy-mt2-7b",
    "tencent/hy3": "tencent_hy3",
    "thinkingmachines/inkling-small:free": "thinkingmachines_inkling-small_free",
    "thinkingmachines/inkling:free": "thinkingmachines_inkling_free",
    "upstage/solar-mini4": "upstage_solar-mini4",
    "upstage/solar-pro4": "upstage_solar-pro4",
    "z-ai/glm-4.7-flash": "z-ai_glm-4.7-flash"
  };

  var NAMED = [
    {
      key: "spark",
      label: "Spark",
      seats_id: null,
      enabled: true,
      group: "named",
      note: "No seats.json key is Spark. Muse Spark 1.3 is the separate row meta/muse-spark-1.3-contributor. This entry is a local mock label only."
    },
    {
      key: "gf38",
      label: "Gemini 3.8 Flash",
      short: "GF38",
      seats_id: null,
      enabled: false,
      group: "named",
      note: config.gf38Note
    },
    {
      key: "grok47",
      label: "Grok 4.7",
      seats_id: null,
      enabled: true,
      group: "named",
      note: "Local mock label only. No rating in that file."
    },
    {
      key: "argon4",
      label: "Argon 4",
      seats_id: null,
      enabled: true,
      group: "named",
      note: "Local mock label only. No rating in that file."
    },
    {
      key: "sol6",
      label: "Sol 6",
      seats_id: null,
      enabled: true,
      group: "named",
      note: "upstage/solar-mini4 and upstage/solar-pro4 are different rows. Local mock label only. No rating in that file."
    },
    {
      key: "luna6",
      label: "Luna 6",
      seats_id: null,
      enabled: true,
      group: "named",
      note: "Local mock label only. No rating in that file."
    },
    {
      key: "max",
      label: "Max",
      seats_id: null,
      enabled: true,
      group: "named",
      note: "Local mock label only. No rating in that file."
    },
    {
      key: "muse13",
      label: "Muse Spark 1.3",
      seats_id: "meta/muse-spark-1.3-contributor",
      seats_file: "meta_muse-spark-1.3-contributor",
      enabled: true,
      group: "named",
      note: "seats.json id meta/muse-spark-1.3-contributor. That file has no rating."
    }
  ];

  function seatRows() {
    var out = [];
    Object.keys(SEATS).forEach(function (id) {
      if (id === "meta/muse-spark-1.3-contributor") return;
      out.push({
        key: "seat:" + id,
        label: id,
        seats_id: id,
        seats_file: SEATS[id],
        enabled: true,
        group: "seats.json",
        note: "seats.json id. That file has no rating. Local mock only."
      });
    });
    return out;
  }

  function all() {
    return NAMED.concat(seatRows());
  }

  function enabled() {
    return all().filter(function (m) { return m.enabled && m.key !== "gf38"; });
  }

  function byKey(key) {
    var rows = all();
    var i;
    for (i = 0; i < rows.length; i++) if (rows[i].key === key) return rows[i];
    return null;
  }

  function pickBlind(list, rng) {
    var rows = list || enabled();
    if (!rows.length) return null;
    var roll = (rng || Math.random)();
    if (roll < 0) roll = 0;
    if (roll >= 1) roll = 0.999999;
    return rows[Math.floor(roll * rows.length)];
  }

  return {
    SEATS: SEATS,
    NAMED: NAMED,
    all: all,
    enabled: enabled,
    byKey: byKey,
    pickBlind: pickBlind
  };
});
