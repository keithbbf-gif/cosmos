# CRON — scheduled task for the Cosmos daemon

**Owner:** Ara (voice layer) + Grok Build
**Repo:** keithbbf-gif/cosmos
**Date:** 2026-09-02
**Status:** NOT FOUND in repo — write this, then install on the desktop.

## What I found
- `cosmos_daemon.py` exists and polls `queue/bucket/` for work orders.
- `cosmos/cosmos_sched.py` is an internal job scheduler (ledger-based), not the OS clock.
- No `cron`, `crontab`, `systemd`, or `OnCalendar` references anywhere in the tree.
- No install script for a system timer. The daemon loop (`--loop`) exists but nothing wakes it from outside.

## What to do
1. Confirm the live root path (the `--root` the daemon expects, e.g. `~/cosmos/live`).
2. Install a system timer that fires the daemon on the clock:
   - **Linux:** systemd user timer, `OnCalendar=*:0/1` (every minute), `ExecStart=py -3.14 /path/to/cosmos_daemon.py --root <live> --once`.
   - **Windows:** Task Scheduler, trigger every 1 minute, action `py -3.14 cosmos_daemon.py --root <live> --once`.
   - **macOS:** `launchd` plist, `StartInterval` 60.
3. Make sure the machine never sleeps (desktop — already true) and Python 3.14 is on PATH.
4. Add a heartbeat check: if `logs/daemon_heartbeat.json` is older than 3 minutes, alert.
5. Keep this file next to `cosmos_daemon.py` and `SOP.md` so the schedule, the process, and the code stay locked together.

## Verify
After install, drop a test order in `queue/bucket/`, wait one tick, confirm it moved to `queue/done/` with `state: DONE`.
