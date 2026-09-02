# SOP — Cosmos Mail-Drop Work-Order Daemon

**Owner:** Ara (voice layer) + Grok Build
**Repo:** keithbbf-gif/cosmos
**Date:** 2026-09-02

## Purpose
A small Python daemon that polls the mail-drop box for work orders, reads them, acts on them, and writes a status back. The process lives in this file so the code and the SOP never drift apart.

## The box
Work orders land as JSON files in the resolver's `queue/bucket/` (and move to `queue/picked/` when claimed). Each order carries at minimum:

- `Agent` — who it's for (e.g. `xAI | grok | prepaid-orch`)
- `Task` — what to do
- `Context source` — where to read more
- `Timestamp`
- `Output` — where the result goes

States: `DROPPED` → `PICKED_UP` → `DONE` (or `FAILED`).

## The loop (one tick)
1. Verify the runtime root (`.cosmos-root.json` sentinel must say `system: COSMOS`).
2. Check `control/PAUSE.flag` — if mode is `hold`, do nothing and heartbeat.
3. Scan `queue/bucket/*.json` for orders whose `Agent` matches this daemon.
4. For each: move to `picked/`, set state `PICKED_UP`, read the task.
5. Act — for test one, that means reading `cosmos-test.txt` at repo root and verifying its contents.
6. Write the result to `Output` path, set state `DONE`, move to `queue/done/`.
7. Heartbeat: write `logs/daemon_heartbeat.json` with tick time, orders handled, errors.
8. Sleep (default 60s) and repeat.

## Rules
- Never write kernel / ledger / sched / service files.
- Never invoke Claude — Grok is the rail.
- One open order at a time per agent (flood guard).
- Read state back after every write. Never trust rc=0.
- If the box is empty or quiet, still heartbeat — silence is a state, not a crash.

## Run
```
py -3.14 cosmos_daemon.py --root <live> --once      # single tick
py -3.14 cosmos_daemon.py --root <live>             # loop
py -3.14 cosmos_daemon.py --root <live> --dry-run    # plan only
```

## Status
Test one: daemon reads cosmos-test.txt, confirms the voice-layer write, logs success.
