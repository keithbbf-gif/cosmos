# WOMBAT seat — Luna 6.0 MAX (seated 2026-09-23, swapped from SOL 6)

- **Model:** `openai/gpt-6-luna` → request sends `openai/gpt-6-luna:floor`.
- **Effort:** MAX (`model_reasoning_effort = "max"`).
- **Harness:** Codex (`codex.cmd exec -p cosmos-openrouter --sandbox read-only`).
- **Routing:** OpenRouter provider, runtime-loaded `OPENROUTER_API_KEY`, never
  printed. FLEX = `:floor`.
- **Legend:** `live/work/codex/hero-wombat-luna/AGENTS.md` (stable PREFIX) +
  `TASK.md` (ITEM tail). Prefix ~2–3k tok; floor assumed 1024 (confirm via
  `cached_tokens`).
- **Tenure:** until wish queue dry +30m; then TidyUP + `BUwbt.json`. **Never idle.**
  Write one bite, then run that row (CCrew pair). Board full (every open
  WISHLIST line has a **mouth** ITEM, not gold-fill) → close her.
- **Job:** 42 wishes → six-field drops (verbatim reuse); CCrew pairs seat per
  tab after singles. Good output to Judge, bad rerun hot-cache/other agent.
- **Does NOT:** grade; merge; hold the pen.
- **Second-Judge rule (Keith 2026-09-23, for WOMBAT to enforce):** first Judge
  is SOL 6 (family `openai`). Later, ANY finished set containing an `openai`
  family member (e.g. C1 luna6 outputs) must go to a SECOND Judge from another
  family — never SOL, never Luna. Candidate pool: GLM 5.3 (`zai`, JUDGE_ORDER
  first), DeepSeek, Qwen. Tag such sets `needs-second-judge` at file time so
  the routing is automatic, not remembered.
- **Canon:** `docs/CANON_AGENT_CALLS.md`, `docs/CANON_4C_JUDGE.md`,
  `docs/CACHE_TTL.md`.
- **This run:** 3 coders per job after singles (recorded run config).
