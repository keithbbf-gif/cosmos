# SUMMON BY HARNESS — ORC / WOMBAT / CCr

Who reads this: ORC seating CCrew, WOMBAT filling Agent field, anyone who fires a HERO.
Canon: `docs/CANON_SPAWN.md`. Pack files: `SOP_SUMMON_HERO.md`. Scar: ROLD **S-156**.

**Do not** treat HTTP 200 as ACTIVE. ACTIVE = first line matches Role (`NONE`/`diff --git` coder, `ITEM`/`NONE` WOMBAT, `KEEP|DROP|HOLD` judge) **and** SKU bound.

## Board = values, not pointers

Do **not** put `<pointer>`, `see docs/…`, or a path in Task/prompt/MAX/scores.
Read the file if you must, then **copy the text into the cell**. Pointers
break; nobody can check them. Context source may list `[read*]` paths
(location only).

## Harness recipes

### Codex 0.147 (Luna WOMBAT / Judge)

Isolated `CODEX_HOME`. **Never** `--ignore-user-config`.  
`--ephemeral --approve-for-me -m <sku>:floor -c model_reasoning_effort=max`  
Windows stamps `sandbox_policy: read-only` even with workspace-write. **Host harvest** writes drops.  
Do not resume old threads.

### OpenRouter chat (`OpenRouterRail.dispatch`)

Named pin only. Not `openrouter/free`. Key weekly cap is **not** the usual 429.

| Symptom | Cause | What to do |
|---|---|---|
| 429 `upstream_provider_shared_pool` | Gemma=Google AI Studio, Qwen=ModelRun **shared free pool** | Wait, other pin, or BYOK. Not your $150 weekly. |
| REFUSED `not a pinned OpenRouter id` | Roster slug missing from `PINNED` in `cosmos_openrouter_rail.py` | Do not invent a call. Pin first (CCr) or skip. |
| 404 Ling VL `:free` | Free slug **gone**. Paid: `inclusionai/ling-3.0-flash-vl` | Use paid slug or skip. |
| 403 Inkling `:free` | Gate: **agentic harness only** | Chat ping will never work. Codex/agent app only. |
| 200, `response_model=None` | `:floor` on some `:free` (Nano Omni) | Call catalog id **without** extra `:floor`. |
| 200, first line CoT/preamble | Nemotron Lightning, Hy3 preview | Pack is on; mouth fails form. Do not seat as coder until harvest strips or STYLE holds. |
| 200, first line `NONE` | **ACTIVE** | Nex Mini, North Mini (measured). |

### `pi -p` (GLM Flash)

CODER 1. `--provider zai --model glm-5.3-flash`. Fallback OR `z-ai/glm-5.3-flash`. Not ZCode desktop.

### `dsh --profile headless` (DeepSeek)

CODER 3. Native via when bound.

### `opencode run` (Ling Flash paid)

CODER 5. Not Ling VL `:free`.

### Vertex Kelly (GF38)

CODER 2. Not OpenRouter.

### Grok 4.6

**REFUSE** `grok.exe` as CCrew worker. Gitur Cursor BUILD only.

## Seats measured 2026-09-23 (TPS walk)

ACTIVE: `nex-agi/nex-n2.5-mini:free`, `cohere/north-mini-code:free`, WOMBAT `openai/gpt-6-luna:floor`.  
Skip until pool cools: Gemma `:free`, Qwen 27B `:free`.  
Skip until pin: Laguna, Dots3, Qwen3.7/3.6/omni, Hy3 (non-preview), Solar, MiMo.
