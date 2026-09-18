# CANON — WARN BEFORE ERROR ×3

Keith: humans are distracted. See the danger → **say it three times** → fail-closed.

Code: `cosmos/cosmos_warn.py` `warn3` / `WarnRefuse`.

1. Print `WARN BEFORE ERROR: {kind}` **three times** (stderr), then refuse.
2. Two heads (`origin/main..HEAD` ≠ 0) — warn×3, do not join-commit.
3. `grok.exe` / `grok --single` as WO worker — warn×3, do not spawn (runner hooked).
4. Concat Context source ` · ` — warn×3, NO_CONTEXT.
5. Judge cache dead and n_board < 20 — warn×3, leave the chair.
6. Gitur PR that deletes more than it adds on a working file — warn×3, do not squash.
7. Bundle PR duplicating already-merged KEEP — warn×3, do not squash.
8. Every attempt scored in JSONL. Crowds: pair + judge.
