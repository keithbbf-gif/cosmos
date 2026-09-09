# PROMPT CACHE — prompting rule (Keith 2026-09-08)

**Canon for every COSMOS LLM call.** Static first, volatile last. Measure
`cached_tokens` (and `cache_write_tokens` when the vendor sends them). A claim
of a cache hit without those fields is fabricated compliance.

Version: **policy:v1**. Change the version string only when this file’s bytes
change. Do not put the current date, a request UUID, a branch name, or a
timestamp in the reusable prefix.

Live farm prefix: `work_orders/ccr/CREW/IN/PREFIX.md` then this rule
(`work_orders/ccr/CREW/IN/CACHE_RULE.md`). Item / diff / pytest / user task
are the **tail**.

## SOP — preload every prompt (Keith 2026-09-08)

**No naked questions.** Every workflow that calls a model **preloads** the
stable needed-info block first, then appends the query:

| Workflow | Prefix (preload) | Tail |
|---|---|---|
| Farm / cheap seats | `PREFIX.md` + `CACHE_RULE.md` | ITEMS/*.md |
| Cursor / Gitur check | same PREFIX + CACHE_RULE | tab prompt |
| Work order | DHx + AGENT_BOUNDARIES + PREFIX | Task paragraph |
| MOTIF stages | frozen PROBLEM STATEMENT file | stage instruction |
| Vertex GF38 | PREFIX + CACHE_RULE + this file + AGENT_BOUNDARIES as `systemInstruction` (≥4096) | `# ITEM` user turn |
| Luna/Terra Flex | PREFIX + CACHE_RULE + `prompt_cache_key` ≤64 + explicit breakpoint | user task |
| Grok 4.6 (this TUI / Cursor Grok) | stable prefix + cache key; stay **under 200K** | task / diff / pytest |

A call that sends only the question is out of SOP. Auto-attach the prefix;
do not wait for the operator to paste it.

## The rule

1. **Prefix must clear the vendor floor.** OpenAI/Luna **1,024**. Gemini 3.x
   implicit **4,096**. COSMOS PREFIX alone was ~926 — Luna miss until
   CACHE_RULE; Gemini still misses until BOUNDARIES is on the Vertex
   systemInstruction. Pad with canon files, not timestamps.
2. **Exact prefix.** Message order, roles, whitespace, tool JSON, schema JSON,
   and images must match byte-for-byte. Semantic similarity does not cache.
3. **Matching is incremental** after the floor. An early one-character edit
   drops everything after it.
4. **`prompt_cache_key` is routing affinity**, not a substitute for a matching
   prefix. OpenAI max **64 chars**. COSMOS form:
   `cdeck-{luna|terra|or}-pv1-t{tools}-{sha12}`. Never a request id.
5. **Cache is best-effort and short-TTL.** Keep related calls close. Prime
   once, then fan out. Do not launch N cold starts in parallel.
6. **Quote the usage fold.** `cached_tokens` / `cache_write_tokens` /
   `prompt_tokens` / `cost`. Never assume a hit.
7. **Sticky provider.** Luna/Terra stay on `openai/flex`. Fallbacks off.
   A provider bounce is a cache miss. Luna cache is not Sol cache.
8. **Append-only history.** Do not rebuild or reorder prior turns. Compact
   only as a versioned summary at a fixed location (new cache family).
9. **Tools and schemas are prefix.** Fixed catalog, fixed JSON key order,
   versioned (`tools:v3`). Do not inject live repo state into tool
   descriptions.
10. **Repo context is prefix.** Canonical path sort. Changed files, diffs,
    stack traces, and the current task go last.
11. **RAG:** immutable working-set in the prefix; new chunks in the tail,
    sorted `(source_path, chunk_start)`. Score-order every turn kills cache.
12. **OpenRouter:** same model id, `provider.only` pin, `allow_fallbacks:
    false`. Anthropic/Qwen need explicit `cache_control` on the stable
    block. OpenAI GPT-5.6 uses automatic prefix + `prompt_cache_key`.

## Killers (refuse these in a prefix)

Timestamp, request UUID, “today”, changing branch, usage-status line, random
few-shots, score-sorted file lists, dynamic tool text, rewriting history,
provider auto-failover, idle > TTL, assuming a hit.

## Luna Flex economics (OpenRouter page)

Input $0.20/M · cache read $0.02/M (90% off) · Flex input $0.10/M · Flex
output $0.60/M. Cache read is cheaper than Flex input. Hits are the point.

## Grok 4.6 vs Gemini 3.8 Flash (cache economics)

High-context **Python coding-agent loops** use **GF38 Vertex**, not G46, for
cache dollars. G46 stays the CCr / behavior seat. Measure hits; do not assume.

| Dimension | Grok 4.6 (xAI API) | Gemini 3.8 Flash (Kelly Vertex) |
|---|---|---|
| Normal input | $2.00/M | $0.75/M intro through **2026-12-31** |
| Cached input | $0.50/M (75% off) | $0.075/M (90% off) |
| Output | $6.00/M | $3.75/M intro |
| Long-context cliff | **200K** prompt tokens → whole request doubles to $4/$1/$12 | No equivalent cliff in the Google cache guide |
| Implicit cache | Yes, repeated eligible prefixes + stable cache key | Yes; min **4,096** tokens; discount automatic |
| Explicit cache | Key/routing consistency; no cache object confirmed | Yes — cache object + TTL; storage $0.50 / 1M cached tokens / hour (intro) |
| Best use | When G46 behavior wins (ambiguous debug, architecture) | Repeated repo context, RAG, high-volume coding-agent loops |

After **2027-01-01** Gemini 3.8 Flash intro rates are reported to double — re-measure; do not invent a new table.

**Grok SOP:** prefix first, tail last, stable cache key, calls close together, **stay under 200K**. New key when baseline repo / tools / policy bytes change. Never timestamp the key.

**Gemini SOP:** same prefix rules. Implicit when traffic is frequent and the systemInstruction is ≥4096 and byte-stable. Explicit cache objects (TTL) when the corpus is huge, workers share it, or the session pauses past implicit TTL. COSMOS farm uses **implicit** first (systemInstruction = canon stack). Explicit `caches.create` is a later bind — do not invent a second Core.

## Bind

Rail: `cosmos/cosmos_openrouter_rail.py` (`prompt_cache_key` on Flex seats;
`fold_usage` copies `cached_tokens` / `cache_write_tokens`). Vertex:
`cosmos_vertex_rail.py` copies `cachedContentTokenCount`. Farm:
`work_orders/ccr/_propose_seat.py`. Principle **P11**. Boundaries item **15**.
