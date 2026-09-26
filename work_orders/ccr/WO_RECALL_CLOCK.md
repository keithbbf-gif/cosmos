# Gitur BUILD — Recall clock schtask standup (own_clocks id 27, --once 15m)

**Repo (PRIVATE):** `keithbbf-gif/cosmos`
**Branch:** `ccr/recall-clock` from GitHub `main`. Not unique HEAD `8b5ad84`.
**Lane B:** Cursor Cloud Agent, Opus 5 / Sonnet class. Composer 2.5 / Auto refused. Do not change Opus T.
**P10:** PROPOSE only. CCr writes CORE. Schtasks create may need Keith elevation — emit `keith_cmd`, never fake registered.
**Do not:** spawn grok.exe, pull 8b5ad84, merge leftover PRs, USPTO, in-process cron, agent loop, a 28th CLOCKS row, `/delete` Logon tasks, take Core :8770 down.

FIRST read `docs/AGENT_BRIEF.md` and `docs/AGENT_BOUNDARIES.md`. Then `docs/STEAL_MAP.md` (NL cron = Hermes job language on schtasks + WD2).

## Already on this tree (do not re-build)

- `cosmos/cosmos_recall_clock.py` — `--root <live> --once` refreshes FTS5 recall, writes `live/logs/recall_clock_heartbeat.json`. **No `standup()`.**
- `cosmos_own_clocks.CLOCKS` id **27**: clock `COSMOS Recall Refresh`, cadence `15m`, script `cosmos_recall_clock.py`, task `COSMOS Recall Refresh`, `logon: None`, vehicle `schtasks /sc minute /mo 15 --once`, heartbeat `recall_clock_heartbeat.json`, standup key `"recall"`.
- `_call_standup("recall")` currently falls through to `unknown standup recall`. That is the gap.
- `GET /api/v1/recall` **200**, never mkdir.

A thinner drop `work_orders/drop/wo-20260917T161200.json` already named this job. This brief is the Gitur BUILD prompt; do not duplicate CLOCKS id 27.

## Job

Stand up the **native** recall clock.

1. Add `standup(root)` on `cosmos_recall_clock.py` following `cosmos_backup_clock.standup` / `cosmos_clock.create_task`:
   - Task name `COSMOS Recall Refresh`
   - `tr_cmdline(script, root, "--once")`
   - `create_task(..., "minute", mo=15)` — **not** `--loop`, not an in-process thread
   - If already registered → `started: already`
   - If schtasks denied → `keith_cmd` + `needs_elevation`; do not invent `registered: true`
   - Optional `run_now` once so heartbeat exists; do not storm
2. Wire `_call_standup` in `cosmos_own_clocks.py`: `if name == "recall": from cosmos_recall_clock import standup; return standup(root)`
3. Keep `--once` as the only worker mode. A missing `--once` still rc=2.
4. Proof: `schtasks /query /tn "COSMOS Recall Refresh"` ok **or** typed elevation refuse; heartbeat schema after a real `--once`; `GET /api/v1/recall` still never mkdir.

Native Windows clock, not an agent loop. WD2 / 15s Activity Clock is a different vehicle — do not fold recall into WD2.

## Bite

- `--once` still refreshes and writes heartbeat (existing).
- `standup` is idempotent if the task exists.
- `_call_standup("recall")` no longer `unknown standup`.
- `cosmos_own_clocks.py --matrix` row id 27 reports the task name; registered is MEASURED from schtasks, never assumed.

## Output

Unified diffs under `proposals | RECALL_CLOCK.json`. PR `WO: recall clock schtask standup`. Gitur BUILD. autoCreatePR. Quote schtasks query or `keith_cmd` — a claim is not evidence.
