# COSMOS — Model Access Roster

_Generated 2026-08-27 by SSA (Sonnet) research; disposed to the tree by COW per P10 — from
vendor-official live docs (Anthropic model-deprecations table, xAI pricing/models pages, OpenAI
models + deprecations pages, Google Gemini API models page) cross-referenced against the live rail
specs (`cosmos_node_rails.py`), model constants (`cosmos_brain.py`, `cosmos_dispatch.py`,
`cosmos_codex_rail.py`) and the Cursor lane (DHx, `docs/AGENT_BRIEF.md`)._

## Taxonomy — how we count

- **FAMILY** = a vendor's whole model line (Claude, GPT, Grok, Gemini). 4 total, fixed.
- **CLADE** = a lineage/tier within a family (Claude: Opus / Sonnet / Haiku / Fable; GPT: GPT-5
  line / o-series / Codex; Grok: reasoning / code; Gemini: Pro / Flash).
- **VERSION** = a specific numbered release within a clade (Opus 4.8, Sonnet 5, grok-4.6,
  gpt-5.3-codex, gemini-3.7-flash, ...). **This is the leaf we count for the grand total.**
  Aliases (e.g. `opus` resolving to the current Opus version) are NOT counted separately from the
  version they resolve to.

Only **chat / reasoning / coding text-model versions** are counted in the totals. Single-modality
models (image gen, TTS, transcription, embeddings, video, music, robotics) are in the Appendix and
excluded from the version count. A version counts as **tappable** if the vendor has not shut it down
(`Active` or `Deprecated`-but-pre-shutdown); `Retired`/`Shut down` versions are excluded.

**4 families · 11 clades · 44 tappable versions (± ~4) · 6 wired-in-COSMOS today.**

---

## Anthropic — Claude family (4 clades, 10 versions)

| Clade | Version | API model ID | State | Path |
|---|---|---|---|---|
| Fable | Fable 5 | `claude-fable-5` | Active | **wired** — `cosmos_dispatch.py CLAUDE_MODEL` |
| Opus | Opus 5 | `claude-opus-5` | Active | **wired** — `cosmos_brain.py OPUS_MODEL` (`opus` alias) |
| Opus | Opus 4.8 | `claude-opus-4-8` | Active | reachable — `claude` CLI pinned |
| Opus | Opus 4.7 | `claude-opus-4-7` | Active | reachable — `claude` CLI pinned |
| Opus | Opus 4.6 | `claude-opus-4-6` | Active | reachable — `claude` CLI pinned |
| Opus | Opus 4.5 | `claude-opus-4-5-20251101` | Active | reachable — `claude` CLI pinned |
| Sonnet | Sonnet 5 | `claude-sonnet-5` / CLI `sonnet` | Active | **wired** — SSA / `--agent sonnet` — `cosmos_dispatch.py SONNET_MODEL` (`claude -p --model sonnet`) |
| Sonnet | Sonnet 4.6 | `claude-sonnet-4-6` | Active | reachable — `claude` CLI pinned |
| Sonnet | Sonnet 4.5 | `claude-sonnet-4-5-20250929` | Active | reachable — `claude` CLI pinned |
| Haiku | Haiku 4.5 | `claude-haiku-4-5-20251001` / CLI `haiku` | Active | **wired** — `--agent haiku` — `cosmos_dispatch.py HAIKU_MODEL` (`claude -p --model haiku`) |

Retired (excluded): Opus 4.1, Opus 4 / Sonnet 4 originals, Sonnet 3.7, Haiku 3.5/3.
**5th-clade watch:** `claude-mythos-*` appears in Anthropic's deprecation table but isn't one of
the 4 named clades — flagged, not counted.

---

## xAI — Grok family (2 clades, 7 versions)

| Clade | Version | Model ID | Path |
|---|---|---|---|
| Reasoning | Grok 4.6 | `grok-4.6` | **wired** — `DEFAULT_MODEL`; + `sgh-api`, `gw-api`, Cursor — 4 paths |
| Reasoning | Grok 4.5 | `grok-4.5` | reachable — xAI API |
| Reasoning | Grok 4.3 | `grok-4.3` | reachable — xAI API (redirect target for retired 4/3/4.1 slugs) |
| Reasoning | Grok 4.20 reasoning | `grok-4.20-0309-reasoning` | reachable — xAI API |
| Reasoning | Grok 4.20 non-reasoning | `grok-4.20-0309-non-reasoning` | reachable — xAI API |
| Reasoning | Grok 4.20 multi-agent | `grok-4.20-multi-agent-0309` | reachable — xAI API |
| Code | Grok Build 0.1 | `grok-build-0.1` | reachable — xAI API (replaces retired grok-code-fast-1) |

Retired May 15 2026 (excluded): grok-4, grok-4-fast, grok-4.1-fast, grok-3, grok-code-fast-1.
GrokBot is a bot wrapper, not a distinct version — not counted.

---

## OpenAI — GPT / o-series / Codex family (3 clades, 17 versions)

| Clade | Version | Model ID | Lifecycle | Path |
|---|---|---|---|---|
| GPT-5 | GPT-5.6 Sol | `gpt-5.6-sol` | current flagship | `oa-api`, Codex CLI |
| GPT-5 | GPT-5.6 Terra | `gpt-5.6-terra` | current | `oa-api`, Codex CLI |
| GPT-5 | GPT-5.6 Luna | `gpt-5.6-luna` | current | `oa-api`, Codex CLI |
| GPT-5 | GPT-5.6 Cyber | `gpt-5.6-cyber` | current, specialized | `oa-api` |
| GPT-5 | GPT-5.5 | `gpt-5.5` | prev-gen, selectable | reachable |
| GPT-5 | GPT-5.4 | `gpt-5.4` | deprecating (API path OK) | reachable |
| GPT-5 | GPT-5.4 mini | `gpt-5.4-mini` | deprecating (API path OK) | reachable |
| GPT-5 | GPT-5 | `gpt-5-2025-08-07` | deprecated, shutdown Dec 11 2026 | reachable |
| GPT-5 | GPT-5 mini | `gpt-5-mini-2025-08-07` | deprecated | reachable |
| GPT-5 | GPT-5 nano | `gpt-5-nano-2025-08-07` | deprecated | reachable |
| GPT-5 | GPT-5 Pro | `gpt-5-pro-2025-10-06` | deprecated | reachable |
| o-series | o3 | `o3-2025-04-16` | deprecated, shutdown Dec 11 2026 | reachable |
| o-series | o3-pro | `o3-pro-2025-06-10` | deprecated | reachable |
| o-series | o4-mini | `o4-mini-2025-04-16` | deprecated, shutdown Oct 23 2026 | reachable |
| Codex | GPT-5.3-Codex | `gpt-5.3-codex` | live via API key | **wired** — `cosmos_codex_rail.py` (stale-pin risk; probe) |
| Codex | GPT-5.3-Codex Spark | `gpt-5.3-codex-spark` | research preview | reachable, narrow |
| Codex | GPT-5-Codex mini | `gpt-5-codex-mini` | current | reachable |

Retired (excluded): gpt-5.2/5.3-chat-latest, gpt-5-codex original, gpt-5.1/5.2-codex, o1-*, and the
pre-GPT-5 legacy tail.

---

## Google — Gemini family (2 clades, 10 versions)

| Clade | Version | Model ID | Path |
|---|---|---|---|
| Pro | Gemini 3.1 Pro | `gemini-3.1-pro-preview` | `gem-api` Vertex (probe project access) |
| Pro | Gemini 2.5 Pro | `gemini-2.5-pro` | Vertex |
| Flash | Gemini 3.7 Flash | `gemini-3.7-flash` | Vertex |
| Flash | Gemini 3.6 Flash | `gemini-3.6-flash` | Vertex |
| Flash | Gemini 3.5 Flash | `gemini-3.5-flash` | Vertex |
| Flash | Gemini 3.5 Flash-Lite | `gemini-3.5-flash-lite` | Vertex |
| Flash | Gemini 3.1 Flash-Lite | `gemini-3.1-flash-lite` | Vertex |
| Flash | Gemini 3 Flash | `gemini-3-flash-preview` | Vertex |
| Flash | Gemini 2.5 Flash | `gemini-2.5-flash` | Vertex |
| Flash | Gemini 2.5 Flash-Lite | `gemini-2.5-flash-lite` | Vertex |

Shut down (excluded): Gemini 2.0 Flash/Flash-Lite, Gemini 3 Pro Preview (orig), 3.1 Flash-Lite
Preview. `gem-api`'s actual pinned version isn't set in `cosmos_node_rails.py` — needs a probe.

### Gemma 4 via OpenRouter (named pin, Keith 2026-09-07)

Not Gemini. Not the rejected `openrouter/free` rotator. COSMOS rail `openrouter-api`.

| Version | API model ID | Path |
|---|---|---|
| Gemma 4 26B A4B IT (free) | `google/gemma-4-26b-a4b-it:free` | **wired** — default `openrouter-api` |
| Gemma 4 31B IT (free) | `google/gemma-4-31b-it:free` | **wired** — explicit `--model` |
| GLM 5.3 Flash (value coder) | `z-ai/glm-5.3-flash` | **wired 2026-09-07** — Keith: high skill, low cost. Live rater coding **71.5**, **$0.075 / $0.250** per 1M. Named pin, not the rotator. |

Key: `live/config/openrouter_api_key.txt`. Rotator `openrouter/free` stays REFUSED.

**ChatBot phone picker (Keith 2026-09-07):** consumer product, not a Core
dispatch pin change this tick. **Freemium free tier.** Human picks a
**named** `:free` id (starts with the two Gemma 4 pins above). Pitch
**FREE FOREVER — YOU PICK THE MODEL**. Vendor caps still apply: **20 RPM**;
**50 RPD** until $10 lifetime credits, then **1000 RPD**. Do not claim
OpenRouter is unlimited. Do not sell unlimited `:free` as Premium. Premium
= named paid models / desktop hands / later P06 — price = Keith. DEFINE:
`work_orders/ccr/DEFINE_CHATBOT_PHONE.md`. BUILD may add named `:free` ids
(low latency, family-diverse); never the rotator.

### Vertex coding wallet (Keith 2026-09-07: $300 GEM tokens)

`vertex-coding` · `orders.ggn@gmail.com` · **$300** · expires **2026-12-04**. Not Joanna `gem-api`. Not Studio Free.

| Use | Model ID | Notes |
|---|---|---|
| **Top-tier coder** | `gemini-3.1-pro-preview` | Google's most advanced (model card Feb 2026). Live ping **VERTEX-PRO-PONG** 2026-09-07, `ok true`, $0.000269. |
| Default ping (cheap) | `gemini-2.5-flash` | Stays the spec default so routine probes do not burn Pro. |

---

## Grand totals

| Metric | Count |
|---|---|
| Vendor families | **4** (Anthropic, xAI, OpenAI, Google) |
| Clades across all families | **11** (Claude 4, Grok 2, GPT/o/Codex 3, Gemini 2) |
| **Distinct tappable model VERSIONS (text/reasoning/coding)** | **44** (± ~4) |
| — Anthropic | 10 |
| — xAI | 7 |
| — OpenAI | 17 |
| — Google | 10 |
| Wired into a named COSMOS rail today | **6** (Opus, Fable 5, Sonnet 5/SSA, Haiku 4.5, Grok 4.6, GPT-5.3-Codex; Gemini wired but version unconfirmed) |
| Reachable but not wired | remainder (~40) — via local CLIs, Cursor Ultra, direct API key, or DOM |

## Uncertainty (why ± ~4)

- OpenAI's deprecated-but-not-yet-shutdown tail (11 of 17) is fuzziest — confirm `gpt-5.5-pro` /
  `gpt-5-codex-mini` are separate live IDs.
- Gemini 3.1 Pro / 3 Flash (preview) provisioning on Keith's Vertex project/credit unconfirmed.
- Cursor Ultra's exposed roster changes often (plus its own Composer/Fusion models, not counted).

**Probe commands to bind the count to a live artifact (don't trust this doc past today):**

```bash
# Anthropic
curl -s https://api.anthropic.com/v1/models -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" | jq '.data[].id'
# xAI
curl -s https://api.x.ai/v1/models -H "Authorization: Bearer $XAI_API_KEY" | jq '.data[].id'
# OpenAI
curl -s https://api.openai.com/v1/models -H "Authorization: Bearer $OPENAI_API_KEY" | jq '.data[].id'
# Google Vertex (publisher/Gemini catalog)
curl -s -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  "https://us-central1-aiplatform.googleapis.com/v1/publishers/google/models" | jq '.publisherModels[].name'
# Cursor — no public models-list endpoint; check console.cursor.com usage
```

---

## Appendix — modality-specialized models (NOT in the 44)

Each family also has image / voice / video / embeddings / robotics rosters (xAI Grok Imagine +
Voice; OpenAI gpt-image-2, gpt-realtime, transcription; Google Nano Banana, Veo, Lyria, Live/TTS,
Robotics ER). Real additional surfaces, but a different kind of thing than the versioned-tier count —
sized on request.

---

## Notes

- Every API rail is the **metered fallback**; by canon the **DOM/browser path to the same vendors is
  the preferred, free-thinking route** (no quota/billing), API as backup.
- Each rail is **spend-gated** per `link_id` (budgets: sgh $10, gem $300, gw $5, oa $5).
- **Deepest bench:** Claude (10 versions / 4 clades). **Widest tail:** OpenAI GPT-5 line (11,
  mostly legacy-but-live). **Most consolidated:** xAI (7, after the May 15 2026 retirement wave).
- **Claude CLI lanes (all four clades first-class):** Opus (brain) · Sonnet 5 (SSA / research
  default, `claude -p --model sonnet`) · Haiku 4.5 (`claude -p --model haiku`) · Fable 5 (F5).
  Coding default stays Grok 4.6 / Cursor (never Sonnet). Research/SSA default is Sonnet.
  Spend: local `claude` CLI rides the prepaid subscription (same as F5/Opus — no USD rail;
  timeout `CLAUDE_TIMEOUT_S`). Probe `gem-api`'s Gemini version; re-pin `cosmos_codex_rail.py`
  if Codex's default moved past gpt-5.3-codex.
