# SCAR — catalog smoke 2026-09-24

Keith pasted OpenRouter rows. Pins added. Full-pack pings.

## ACTIVE (NONE)

| Slug | Note |
|---|---|
| `stealth/space-bunny-alpha` | $0, 76 t/s — **new ACTIVE** |
| `poolside/laguna-xs-2.1:free` | full pack 10_lagunaxs |
| `poolside/laguna-s-2.1:free` | full pack 20_lagunas |
| `poolside/laguna-s-2.1` | paid; NONE with trailing space |
| `qwen/qwen3.7-flash` | CoT until `--prefill-none` |
| `prism-ml/ternary-bonsai-2-27b` | **new ACTIVE** |
| `upstage/solar-mini4` | **new ACTIVE** |
| `deepseek/deepseek-v4.1-flash` | prefill NONE |
| `google/gemma-4-31b-it` | **paid** works; `:free` still 429 |

## SCARs

1. **Luna 6 / Luna Pro on OR chat** — HTTP 200, `response_model=None`. Flex lives on **Codex** `-m openai/gpt-6-luna:floor`, not `OpenRouterRail.dispatch`. Judge-seat scars from 2026-09-25: `SCAR_MODEL_CALL_20260925.md`.
2. **Dots3 `:free`** — HTTP 400, no model. Pack exists; provider rejects this pin today.
3. **Muse 1.2 / 1.3 Contributor** — 200 + SKU, **empty mouth**. Not coder-ACTIVE.
4. **Qwen 3.7 Flash** — class 6 CoT without prefill. Pack on; mouth fails until `--prefill-none`.
5. **Gemma `:free` vs paid** — 26B/31B `:free` 429 pool; **31B paid** ACTIVE.
6. **Laguna / Dots / Qwen3.7 were unpinned** — `_code_or_seat.py` already named them; rail PINNED did not. Now pinned.

Log: `CCREW_CATALOG_SMOKE.jsonl`. SOP: `SOP_CCREW_CATALOG.md`.
