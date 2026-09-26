# SCAR — creator docs vs our harness (2026-09-24)

## GPT-6 Luna / Luna Pro — OpenAI

https://developers.openai.com/api/docs/guides/latest-model

- Family is **Responses API** first. Chat Completions: Luna/Sol **function calling only with `reasoning_effort: "none"`**.
- Luna **supports** `reasoning_effort: none`. Astra does not.
- When effort is not `none`, drop `temperature` / `top_p`.
- OpenRouter: **reasoning tokens count against `max_tokens`**. If the budget is tiny, `content` is empty and `finish_reason=length`. Our pings used **256** — that starved Luna/Muse.

**Fix that worked:** `openai/gpt-6-luna` + `reasoning.effort=none` + `max_tokens=4096` → **NONE**.  
Luna Pro still 200/`response_model=None` with `:floor`; retry routing off.

**SOP:** Coder Luna on OR = `effort none` + large max. WOMBAT/Judge MAX stays **Codex** `:floor`.

## Muse Spark — OpenRouter reasoning

https://openrouter.ai/docs/guides/best-practices/reasoning-tokens  
https://openrouter.ai/meta/muse-spark-1.3-contributor

Muse advertises `reasoning`. Empty mouth was the 256-token starve, not a dead model.

**Fix that worked:** `max_tokens=4096` → **NONE** on 1.2 and 1.3 Contributor.

## Dots3-Note Preview

Catalog id is `dots-studio/dots-3-note-preview:free` (hyphens). `dots3-note-preview` is a **400**. Correct slug → **NONE**.

## Nemotron Nano Omni / Ultra

`reasoning` default-on. Cap with `reasoning.max_tokens` or the mouth is empty. HTTP **200** can still carry `error` (NVIDIA ISE / overloaded) — rail now surfaces that instead of `response_model=None`.

**Fix:** Nano Omni `:free` + `reasoning.max_tokens=256` → **NONE**. Ultra `:free` → **NONE** after NVIDIA overload cleared. Paid Ultra slug has no `:free` twin endpoints.

## Inkling `:free`

403: *only available on agentic harnesses* (OpenRouter apps: Codex, pi, Cline, OpenCode, …). Chat Completions from our rail will never pass.

**Fix:** paid `thinkingmachines/inkling` + `effort none` → **NONE**. `:free` via **OpenCode** (`opencode run -m openrouter/thinkingmachines/inkling:free`) EXIT 0, mouth NONE. Do not steal WOMBAT `CODEX_HOME`.

## Gemma / Qwen `:free`

OpenRouter **429** = upstream free pool, retry/backoff. Not our weekly cap.

**Fix that worked:** paid pins `google/gemma-4-26b-a4b-it`, `google/gemma-4-31b-it`, `qwen/qwen3.8-27b` → **NONE**. `:free` still 429 this pass.
