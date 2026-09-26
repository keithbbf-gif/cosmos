# WOMB — all surfaces (not only GET /work_orders)

cDeck **work_orders pane** = `live/state/work_orders/` only.
GET `/api/v1/work_orders` n_total=217 truncated note: **bucket 0, picked 0**.
That pane does **not** show `work_orders/drop/` or GitHub PRs.

## Surface 1 — Core (what cDeck shows)

| folder | n | what it is |
|---|---|---|
| bucket | 0 | nothing waiting to spawn |
| picked | 0 | nothing inflight |
| assigned | 35 | all **DONE** (mostly 2026-09-05 grok-4.6 P10 clones) |
| completed | 25 | 2026-09-02 retries + gem ping |
| failed | 157 | filed copy in `CREW/OUT/TRANSFER/FAILED_FILED/` — **not thrown away** |

Assigned/DONE is Sep 3–9 P10 propose clones, not today’s KEEP.

## Surface 2 — drop inbox (102 files, not ingested)

Today’s WOMB lives here (`work_orders/drop/`). Newest:

- scar-1..5 + canon-spawn (`T220523`)
- restate-profiles / session-tools (`T215011`)
- wo-partner / judge-run / judge-idle / fail-xfer (`T213847`)
- opus-ledger / opus-resume (`T212414`)
- womb-seat / makers-role / learn-clock / cdeck-create (`T210153–56`)
- steal-map T181010–181100
- keep-hitl/stagehand/packets `T165800–02`

Not in GET because we did not `drop_order` (that path still spawned grok.exe).

## Surface 3 — Gitur FIFO (open, pen disposes)

cosmos **#563 → #576** oldest first: plugin, Daytona, packets, Stagehand, NL cron, HITL, packets+guard, Stagehand dup, makers, WOMB pick_pair, learn-clock, Opus resume **#574**, Opus ledger **#575**, CANON spawn **#576**.
cdeck **#320** chamber, **#321** CREATE ROLE, plus spawn-page agent if PR not numbered yet.

## Surface 4 — DEFINE / WRAP / skills (sections, not WO rows)

`DEFINE_WOMB.md`, `DEFINE_JUDGE_RUN.md`, `DEFINE_AGENT_LEARN.md`, `docs/CANON_SPAWN.md`, `WRAP/{WOMBAT,CODER,JUDGE,DAEMON}.md`, `STYLES/`, `skills/wombat-womb-board` (+ SCAR).
