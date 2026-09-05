#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_grok_worker - GROK's own Windows-native bucket worker.

Thin wrapper around cosmos_node_worker. Polls live/buckets/grok/, executes
via the sgh then gw COSMOS rails (spend-gated, ledgered), writes the result
DIRECTLY to the designated folder (V default/BEST, or GDX/ODX).

    py -3.14 cosmos\\cosmos_grok_worker.py --root V:\\A\\Ai\\COSMOS\\live --once
    py -3.14 cosmos\\cosmos_grok_worker.py --root ... --loop
    py -3.14 cosmos\\cosmos_grok_worker.py --root ... --standup
    py -3.14 cosmos\\cosmos_grok_worker.py --root ... --status

Task name: 'COSMOS Grok Worker'. Heartbeat: live/logs/grok_worker_heartbeat.json.
NO BTS. Does not modify kernel/ledger/sched/service.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cosmos_node_worker import WorkerError, run_cli  # noqa: E402
from cosmos_paths import CosmosPathError  # noqa: E402


def main() -> int:
    return run_cli(node="grok")


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
