# PROMPT CACHE

## Orthodoxy (Keith 2026-09-08 — P11)

**Static first, volatile last.** Every LLM call is a stable prefix plus an
append-only tail. Measure `cached_tokens` (and `cache_write_tokens` when the
vendor sends them). A claimed hit without those fields is fabricated
compliance.

- Preload needed info (rules, tools, schemas, repo map, `PREFIX.md`,
  `CACHE_RULE.md`). The task, diff, pytest, and user query are the tail.
  Naked questions are out of SOP.
- Exact byte match. Semantic similarity does not cache.
- No dates, request UUIDs, timestamps, or status lines in the prefix.
- `prompt_cache_key` is routing affinity, not a substitute for a matching
  prefix. Never key on a request id.
- Pad the prefix with canon files, not clocks.
- Auto-attach the prefix. Do not wait for the operator to paste it.

Version **policy:v2** — bump only when prefix bytes change.

### Precache — first query to an agent (Keith 2026-09-09)

SOP **throughout**. The **first** call to a new agent/session **writes** the
optimized prefix (preload). Later calls in that cache family are hits.
Naked first queries are out of SOP.

**When** (MOTIF / Profile decide; skip if the table says no):

| Context | First-query preload | Not in the prefix |
|---|---|---|
| MOTIF any stage | PREFIX + CACHE_RULE + **frozen PROBLEM STATEMENT** | stage instruction (tail) |
| Farm / CREW | PREFIX + CACHE_RULE (+ guidelines if that seat always sends them) | ITEM |
| Forge | PREFIX + pane/file map | the ticket / diff |
| Crucible / Diligence / Docket | occupancy + schema | the live packet / casefile |
| Spidercaster | frozen problem prompt | dest / publish |
| Gitur GLM review | short review rules | the PR diff (tail; cap it) |
| Grok Bot QA | DHx + tab list (compact) | the overhaul item |
| UPS | HOLD until Keith | — |
| User-only ping | **none** (`tag_preload` leaves it untagged) | the ping |

**Size** depends on the **agent/model** (remeasure; not a seat lock):

| Seat | First write | Cap |
|---|---|---|
| Luna / OpenAI Flex | floor **1024**; `tag_preload` + breakpoint | key ≤64 |
| Luna Pro Flex | same family `cdeck-luna-`; **1.1M** window | can hold CACHE_FAT; measure hit |
| GLM / DeepSeek | PREFIX; auto-cache ignores `cache_control` | named pin |
| GF38 Vertex | VERTEX_PRELOAD; implicit floor **4096** | Kelly $300 |
| Qwen explicit | tagged system; 5 min TTL | no fat on user |
| Ling 3.0 Flash | **compact** PREFIX only | window **262,144** — never CACHE_FAT |
| Grok 4.6 / Grok Bot | stable DHx + tabs | this TUI is Heavy — keep compact |
| Cursor Cloud Agent | grok-4.6 native pool; same PREFIX family | not Other Models |

Prime once, then fan the same prefix. Measure `cached_tokens`. A first
call with `cached=0` and `cache_write>0` is the write, not a miss.

Live farm prefix: `work_orders/ccr/CREW/IN/PREFIX.md` then
`work_orders/ccr/CREW/IN/CACHE_RULE.md` (**policy:v2**). Item is the tail.

Boundaries item **15**. Principle **P11**.

### SOP — preload every prompt

| Workflow | Prefix (preload) | Tail |
|---|---|---|
| Farm / cheap seats | `PREFIX.md` + `CACHE_RULE.md` | ITEMS/*.md |
| Cursor / Gitur check | same | tab prompt |
| Work order | DHx + AGENT_BOUNDARIES + PREFIX | Task paragraph |
| MOTIF stages | frozen PROBLEM STATEMENT | stage instruction |
| Vertex GF38 | PREFIX + CACHE_RULE + this file + AGENT_BOUNDARIES | `# ITEM` |
| Luna/Terra Flex | PREFIX + CACHE_RULE + `prompt_cache_key` ≤64 | user task |
| Grok 4.6 | stable prefix + cache key | task / diff / pytest |

### Killers (prefix)

Timestamp, request UUID, “today”, changing branch, usage-status, random
few-shots, score-sorted file lists, dynamic tool text, rewriting history,
assuming a hit.

### Bind

`cosmos/cosmos_openrouter_rail.py` — `tag_preload()` puts
`cache_control: {type: "ephemeral"}` on the **first system/developer**
block by default (Keith 2026-09-09). Auto-cache vendors (OpenAI, DeepSeek,
Z.AI/GLM) ignore the extra field. Picky vendors (Qwen/Alibaba explicit,
Anthropic, Gemini explicit on OpenRouter) need it. Flex seats also get
`prompt_cache_breakpoint` plus `prompt_cache_key`. User-only pings stay
untagged. `fold_usage` copies `cached_tokens` / `cache_write_tokens`.
`cosmos/cosmos_vertex_rail.py` — `ensure_cache` / `cachedContent`; copies
`cachedContentTokenCount` (and Gemini `promptTokensDetails.cachedTokens`).
Farm: `work_orders/ccr/_propose_seat.py`. Package: `_pkg_v3_run.py`.

### Package-v3 fat reviews (measured 2026-09-09)

DeepSeek V4 Pro `deepseek/deepseek-v4-pro-0813` and Qwen3.8 Max
`qwen/qwen3.8-max-0902` are **skip_pin**, not occupancy PINNED. Cache them
the same P11 way:

- **System** = frozen `PACKAGE_V3/CACHE_FAT.md` (PREFIX + live slices).
  `cache_control: ephemeral`. `prompt_cache_key` = `cache_family(model,
  prefix=CACHE_FAT)` — hash the fat bytes, not PREFIX.md alone.
- **User** = short ITEM (the review question). No `cache_control` on the
  tail. Slices in the user turn were the miss: first DS review
  `cached_tokens=0` `$0.170`; first Qwen `cached=0` `cache_write=7187`
  `$0.597` (PREFIX only).
- Prime: `_pkg_v3_cache_prime.py`. Measured hit (same fat, key
  `cdeck-or-pv1-tv1-60761f2fc91f`):

| Seat | Write | Hit |
|---|---|---|
| DS V4 Pro 0813 | `$0.152` cached 7168 / prompt 268679 | `$0.016` **cached 268288 / 268680** |
| Qwen3.8 Max 0902 | `$0.681` write 272362 / prompt 272387 | `$0.046` **cached 272362 / 272388** |

Do not put live slices on the user turn after that write. Ling 3.0 Flash
window is **262,144** — CACHE_FAT (~272k tokens) overruns it; Ling stays
on compact slices. Do not occupancy-pin DS Pro / Qwen Max from this table.

## Guidelines (vendor pages — not orthodoxy)

Rates, floors, TTL, and “pick this model for cache dollars” are **guidelines**.
Re-measure. Do not treat them as P11 or as a seat lock. Occupancy (CCr = G46,
quality farm = GF38, cheap = OR named pins) is still Keith’s routing, not a
cache table.

**Floors (re-measure):** OpenAI/Luna often **1,024** tokens before a cache;
Gemini 3.x implicit often **4,096**. Luna Flex page: Flex **$0.10/$0.60**,
cache read cheaper than Flex input. Grok 4.6 page: cached input **$0.50/M**;
a **200K** prompt may double the whole request. Gemini 3.8 Flash intro
(through **2026-12-31**, reported): **$0.75 / $0.075 cached / $3.75**; explicit
storage **$0.50 / 1M cached tokens / hour**. After 2027-01-01 intro rates may
double.

**Explicit Vertex cache (wired, optional):** `POST …/cachedContents` with
`ttl="3600s"`, then `generateContent` `cachedContent=<name>`. Holds stable
bytes only. Display `cdeck-38-pv1-<sha12>`. Rebuild when those bytes change.
Farm tries this, falls back to `systemInstruction` if create fails.

Illustrative 100K-token hour (intro rates, not a COSMOS score): storage
**$0.05**; each reuse **$0.0075**; uncached **$0.075**. Output is not
discounted. One reuse can start to pay the hour; several turns help. Include
population, TTL, and whether implicit would have hit anyway.

**Auth scar (measured 2026-09-08):** `cachedContents.create` **401** on API
keys (wants ADC). Kelly then **403** `aiplatform.cachedContents.create` until
Keith grants it on `orders.ggn`. Do not click Upgrade.

Sticky `openai/flex` for Luna/Terra/Luna Pro is occupancy (Keith pin flex),
not a cache-economics doctrine.

**Luna Pro page 2026-09-10 (guidelines, not occupancy scores).** Context
**1.1M** (catalog GET **1,050,000**). Pricing-table cache hit rates
**differ by provider**: OpenAI **76.3%** (92.2% of tokens) · Azure **77.6%**
(6.4%) · **OpenAI Flex 45.3%** (4.0%) · Azure US2 **81.1%** (0.0%). Flex
list is ½ ($0.10/$0.875 vs $0.20/$1.75); Flex **hit rate is not**. Effective
on that page still cheaper on Flex ($0.0677 / $0.6557 vs OpenAI $0.09873 /
$1.27) because list is ½, not because cache is better. P11 is more
load-bearing on Flex: miss pays Flex input, not cache read. Measure
`cached_tokens` on `--seat luna-pro`. Do not override `openai/flex` to
Azure EU / Azure US2. Weighted page average ($0.09849 / $1.204) is
dominated by OpenAI's 92.2% token share — that is not the Flex pin's bill.

**Gemini — use it on Vertex, not as an OpenRouter Pro dump (Keith 2026-09-09).**
Occupancy quality Gemini is **GF38** `gemini-3.8-flash` on Kelly
`vertex-coding`. Implicit cache is on for Gemini 2.5+ (floor **4,096**
tokens): stable `systemInstruction` first, short ITEM in `contents`.
Explicit `cachedContents` needs ADC (API keys 401 — measured scar); farm
falls back to implicit, which is the correct path when ADC is missing.
Do **not** send 900k of slices on the user turn. Do **not** treat
OpenRouter `google/gemini-3.1-pro-preview` as the Gemini quality seat
(Q2b: PREFIX 26k / ITEM 914k / `cached=7265` / `$1.33` — fat sat after
the tagged block). OpenRouter `google/*` is skip_pin fallback only, and
then `tag_preload` cache_control on **system** (OpenRouter uses the
**last** Gemini breakpoint). Vertex 3.8 thinking stays vendor-default
(dynamic); do not copy the 2.5 `thinkingBudget` 512/1024 onto 3.8.
