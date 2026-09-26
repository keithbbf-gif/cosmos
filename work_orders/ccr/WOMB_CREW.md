# CCrew on the WOMB — pairs, cache, porosity, ortho

Assigned **before Judge**. Axis = **coding**. Never invent a score: missing cell = UNMEASURED.

## Roster (6)

| Seat | Model | Via | Window (cache size) | Cache floor | $/M out |
|---|---|---|---|---|---|
| CODER1 GLM Flash | z-ai/glm-5.3-flash | cli:pi | 1000000 | UNMEASURED | 0.25 |
| CODER2 GF38 | google/gemini-3.8-flash | vertex-coding | 1048576 | 4096 | 3.75 |
| CODER3 DS Flash | deepseek/deepseek-v4-flash | cli:dsh | 1000000 | UNMEASURED | 0.16 |
| CODER4 5.4-mini | openai/gpt-5.4-mini | codex-cli | 272000 | 1024 | 4.5 |
| CODER5 Ling Flash | inclusionai/ling-3.0-flash | cli:opencode | 262144 | UNMEASURED | 0.063 |
| CODER6 Grok 4.6 | x-ai/grok-4.6 | cli:grok | 131072 | UNMEASURED | SuperGrokHeavy |

## Measured pair on coding axis (live tensor n_obs=619)

| A | B | orth_sketch | porosity mag | kind |
|---|---|---|---|---|
| CODER1 GLM z-ai/glm-5.3-flash | CODER2 GF38 gemini-3.8-flash | **1.0** | **6.0** | MEASURED |

All other CCrew×CCrew cells: **UNMEASURED** (skip, not 0). pick_pair among CCrew-only slugs therefore returns this one MEASURED pair.

## Partner rule on this board

- DAEMON/MOTIF: no LLM partner (WD2).
- CODER1 ↔ CODER2 (MEASURED orth=1.0 mag=6.0).
- CODER3/4/5/6 primary + GLM partner (paid-low mix). ortho/mag UNMEASURED until a cell exists.
- ORC Gitur-shaped ITEM: primary CODER6 + partner GLM.
- RESEARCH: primary CODER1 + partner CODER2 (same MEASURED pair); Judge Luna is not a coder competitor.

Paired coding singles: **276**. Daemon skip: **224**. UNMEASURED partner scores: **273**.

Full rows: work_orders/ccr/WOMB_BOARD_PAIRED.jsonl