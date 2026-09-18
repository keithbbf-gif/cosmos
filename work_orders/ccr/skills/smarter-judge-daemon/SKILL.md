---
name: smarter-judge-daemon
description: Native daemon sits one Judge per run only when WOMB has 20-40 WOs or cache is alive. FAIL autopsies the partner. JSONL attempts. No new fat Judge prefix on an empty board.
---
Activate only via SkillRegistry.propose then CCr accept.

Read `WRAP/DAEMON.md` and `WRAP/JUDGE.md`. Daemon is code (`--once` clock). Judge is a model with STYLE append.

When implementing: `judge_idle_gate`, `wo_partner`, `fail_xfer`, `judge_run` in DEFINE_JUDGE_RUN.md. GET never mkdir. Occupancy unchanged. Pen f47bad79.
