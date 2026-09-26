# SOP — SUMMON HERO (varies by model)

**HERO** = Agent + DUDs. **DUDs** = legend pack (layers 1–7) + mission pack (TASK).
No DUD = not a HERO = no spawn. Canon: `docs/CANON_SPAWN.md`.

## Full install (confirm before spawn)

On disk in the occupant cwd:

| Layer | Must exist |
|---|---|
| 1 Role | `AGENTS.md` §1 |
| 2 Model | exact SKU on CALL + `AGENTS.md` §2 |
| 3 Harness | CALL for **this** via (not a sibling’s) |
| 4 Wrapper | `WRAP.md` (copy of `cosmos/WRAP/{Role}` or `_CODER_WRAP.md`) |
| 5 Skills | `SKILL.md` hydrated **or** explicit “none extra” |
| 6 Tools | allow/forbid in AGENTS |
| 7 Enviro | isolated cwd, ctx **list**, pointer + read budget |
| Mission | `TASK.md` (volatile) |

**Confirm ACTIVE:** spawn `--ephemeral` (Codex) or a new OR chat; injected AGENTS
contains WRAP+STYLE+SKILL (or “none extra”); first line matches Role; response
`model` matches SKU (or runtime omits SKU — proceed). Product lands (harvest or
diff). Stale “None extra” while SKILL is accepted = **not** this spawn.

## Pointer + cache (all HEROs)

Small PREFIX. Need more context → `<pointer>path [read*]</pointer>` then read.
`read_budget_tokens = min(0.15×window, remaining − 0.20×window)`. Follow-on cache
PREFIX = legend + pointed bytes + this prompt + this output. Do not rewrite legend.

## Per via (do not mix)

| Family / model | Via | Summon |
|---|---|---|
| Luna 6 WOMBAT / Judge | Codex 0.147 OpenRouter | Isolated `CODEX_HOME`. **No** `--ignore-user-config`. `-m …:floor -c model_reasoning_effort=max --ephemeral --approve-for-me`. Windows stamps sandbox read-only → **host harvest** writes. |
| Gemma / Nemo / Qwen / Ling **`:free`** | OpenRouter rail | Named pin only (not `openrouter/free`). `OpenRouterRail.dispatch({model, text})`. First line `NONE` or `diff --git`. |
| GLM Flash | `pi -p` | Native via when bound. |
| DeepSeek | `dsh --profile headless` | Native via when bound. |
| Ling paid | `opencode run` | Native via when bound. |
| GF38 | Kelly Vertex | Not this SOP’s Codex path. |
| Grok 4.6 CCrew worker | **REFUSE** `grok.exe` | Gitur Cursor BUILD only. |

## Do not

`--ignore-user-config` on Codex 0.147. Extra `grok.exe`. Resume old Codex thread
(use `--ephemeral`). `danger-full-access`. USPTO. Rewrite PREFIX with dates/WO ids.

Companion: `SUMMON_BY_HARNESS.md` (ORC/WOMBAT). Scar: ROLD **S-156**, `SCAR_HERO_SUMMON_20260923.md`.

## Measured installs (2026-09-23 TPS walk)

| HERO | Model | ACTIVE? | Process |
|---|---|---|---|
| WOMBAT Luna 6 MAX | `openai/gpt-6-luna:floor` | **yes** | Codex isolated home, `--ephemeral`, harvest writes |
| CODER Nex Mini `:free` | `nex-agi/nex-n2.5-mini:free` | **yes** | OR dispatch, first line `NONE` |
| CODER North Mini `:free` | `cohere/north-mini-code:free` | **yes** | OR dispatch, first line `NONE` (full pack) |
| Hy3 preview | `tencent/hy3-preview` | no | 200 + SKU; preamble. Not coder form |
| Nemotron 3.5 `:free` | `nvidia/nemotron-3.5-lightning:free` | no | 200 + SKU; CoT dump |
| Gemma/Qwen `:free` | gemma-4-26b/31b, qwen3.8-27b | no | **429 upstream pool** (not our weekly cap) |
| Ling VL `:free` | `inclusionai/ling-3.0-flash-vl:free` | no | **404** — free slug gone; paid slug without `:free` |
| Inkling `:free` | `thinkingmachines/inkling:free` | no | **403** agentic-harness gate |
| Nano Omni `:free` | `…nano-omni…:free` | no | 200 but `response_model=None` if `:floor` appended |
| Laguna, Dots3, Qwen3.7/3.6/omni, Hy3, Solar, MiMo | roster slugs | no | **REFUSED** — not in `PINNED` |
