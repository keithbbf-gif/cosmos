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

Version **policy:v1** — bump only when prefix bytes change.

Live farm prefix: `work_orders/ccr/CREW/IN/PREFIX.md` then
`work_orders/ccr/CREW/IN/CACHE_RULE.md`. Item is the tail.

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

`cosmos/cosmos_openrouter_rail.py` — `prompt_cache_key` on Flex seats;
`fold_usage` copies `cached_tokens` / `cache_write_tokens`.
`cosmos/cosmos_vertex_rail.py` — `ensure_cache` / `cachedContent`; copies
`cachedContentTokenCount`. Farm: `work_orders/ccr/_propose_seat.py`.

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

Sticky `openai/flex` for Luna/Terra is occupancy (Keith pin flex), not a
cache-economics doctrine.
