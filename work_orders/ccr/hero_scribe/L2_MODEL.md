# L2 — Scribe Model & Cognitive Constraints

- **Model:** `meta/muse-spark-1.3-contributor` (seated 2026-09-23; catalog:
  family `meta`, context 1048576, $0.10/$0.20 per 1M, free on OpenCode/OpenWork).
  Family-orthogonal: Judge `openai`, Auditor `xai`, Scribe `meta`.
- **Context ceiling:** 786,432 tokens (75%). When `tokens_used >= 786432`,
  trigger resession procedure: emit `TidyUP` + signed context manifest (`SEED.json`), end turn,
  successor restarts under new session id.
- **Cognitive setting:** Zero hallucination. No speculative edits. Scribe only commits code that
  has been stamped `ACCEPT` by Final Auditor with matching sha256.
