# Gitur BUILD — COSMOS-learns STYLE clock + xfer JSONL

Repo: keithbbf-gif/cosmos. Branch `ccr/learn-style-clock` from origin/main. P10 PR. CCr disposes LiT.

FIRST read docs/AGENT_BRIEF.md, docs/AGENT_BOUNDARIES.md, cosmos/cosmos_recall_clock.py (pattern only).

**Problem:** DEFINE_AGENT_LEARN — farm xfer loops (prompt→mouth→judge→STYLE append) must run on a **native clock**, not an LLM loop. Periodic spawn reviews WRAP/STYLE/skills/package sets.

**Do**
1. `cosmos/cosmos_learn_clock.py` modeled on recall `--once`:
   - Read a JSONL path under a declared paths role or `state/session-ideas/` (GET never mkdir).
   - For each new FAIL/DROP/HTTP_429 row without `xfer_applied`, append one line to a STYLE file in a **propose** dir (not live PREFIX). Never rewrite PREFIX.md.
   - `--once` required for CLI (missing `--once` → rc=2), plus schtask pattern in a `standup()` that is idempotent (`started: already`).
2. JSONL schema `cosmos-xfer-loop/2` fields: model, chair, pack, cached_tokens, http, checker.score, xfer.kind, prompt_path. Missing = UNMEASURED skip.
3. `--selftest` hermetic tmp dir. No OpenRouter.

**Expected:** unified diff first. Do not vendor Graphiti/Letta. Do not in-process cron.

Title: `WO: learn-style clock --once JSONL authority`
