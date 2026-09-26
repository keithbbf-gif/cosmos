# Gitur BUILD — every agent is a harness (kind by role)

**Repo:** `keithbbf-gif/cosmos`  
**Branch:** `ccr/harness-seat` from `origin/main`. Not unique-head.  
**Lane B:** Cursor Cloud Agent, grok-4.6. Composer 2.5 = CHECK not BUILD.  
**P10:** PROPOSE only. CCr `f47bad79` disposes.  
**After:** Luna KEEP thin PRs in `CCR_ORC_NOW.md` unless Keith names this first.

FIRST read `docs/AGENT_BRIEF.md`, `docs/AGENT_BOUNDARIES.md`, `docs/CANON_SPAWN.md`, `docs/ORCH_SEAT.md`, `docs/ROUTING.md` (Ori refuse), `work_orders/ccr/DEFINE_HARNESS_SEAT.md`.

## Job (one PR)

1. `SpawnSpec`: `role`, `model`, `harness_kind`, `harness_via`, wrapper_paths[], skill_names[], tools[], params{}.
2. Order: Role → Model → Harness → Wrapper → Skills → Tools → Enviro.
3. `defaults(role, model)` fills **kind** from Role (`orch` / `board` / `review` / `coding` / `dispose`; DAEMON refuses LLM).
4. Same WRAP + STYLE + skills + toolbox are arguments to that harness.
5. Kind gates tools: `orch`/`board`/`review` cannot take coding write tools; `coding` cannot take CCr dispose; `review` sandbox read-only.
6. Degenerate `mouth:*` only when native via unbound; `warn3` then refuse if a native via **is** bound.
7. Role `ORC` is valid. Default via = OpenWork/GFO pin (document; do not grant `V:\A`). Refuse ORC spawn as `grok.exe` / Cursor BUILD / `codex exec`.
8. OpenAI CODER via = `codex-cli`. Refuse extra `grok.exe` / `ori`.
9. `--selftest`: ORC → kind `orch` not `coding`; JUDGE → `review` read-only; CODER+Luna → `codex-cli`; CODER+mouth while codex bound → refuse.

**Expected:** unified diff first, 3 VERIFY.

**Must not:** restore `8b5ad84e`; USPTO; Ori; extra grok.exe; grant orch the COSMOS tree; merge cDeck #320.

Title: `WO: every agent is a harness; kind by role; ORC=orch not coding`
