#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_gem_bucket_worker - GEM's own Windows-native bucket daemon.

Polls ONLY live/buckets/gem/ on the 5-15s cadence. Claims a task packet,
executes via vertex-coding (orders.ggn $300; cosmos_vertex_rail through
cosmos_bucket_daemon.execute_handoff), and writes the result DIRECTLY to
the designated folder (V default = live/returns/gem, GDX/ODX from config).

Heartbeat: live/logs/cosmos_gem_bucket_worker_heartbeat.json
  last_run_epoch, polls, pending, worker_id — written on EVERY poll.

    py -3.14 cosmos\\cosmos_gem_bucket_worker.py --root <live> --once
    py -3.14 cosmos\\cosmos_gem_bucket_worker.py --root <live> --loop
    py -3.14 cosmos\\cosmos_gem_bucket_worker.py --root <live> --standup
    py -3.14 cosmos\\cosmos_gem_bucket_worker.py --root <live> --status

Windowless (pythonw + creationflags 0x08000000). PAUSE-aware (HOLD vs
RESUME-GATE). schtasks 1-min self-heal + ONLOGON like cosmos_run.
NO BTS. No drive literals. Does not modify kernel/ledger/sched/service.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cosmos_bucket_daemon import WorkerError, run_cli  # noqa: E402
from cosmos_paths import CosmosPathError  # noqa: E402


def main() -> int:
    return run_cli(node="gem")


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CosmosPathError as e:
        print(e, file=sys.stderr)
        raise SystemExit(2)
    except WorkerError as e:
        import json
        print(json.dumps({"ok": False, "kind": e.kind, "error": str(e)},
                         indent=1))
        raise SystemExit(2)
