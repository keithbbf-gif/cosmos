#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bite: P13 Voice Drop — malformed refuses typed; valid lands work_orders/drop.

Hermetic poll via cosmos_sgh_drop_ingest (fake list/fetch). No GitHub Actions.
No network. No live-tree writes.

    py -3.14 cosmos/_bite_p13_voice_drop.py
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from cosmos_paths import CosmosPaths, write_sentinel  # noqa: E402
from cosmos_sgh_drop_ingest import (  # noqa: E402
    GH_DROP_PATH,
    GH_REPO,
    drop_order,
    poll_once,
)
from cosmos_work_order import work_order_dirs  # noqa: E402

OUT = HERE / "_bite_p13_voice_drop.json"


def _voice_valid_raw() -> dict:
    return {
        "Agent": "xAI | Grok | grok-4.6",
        "Context source": "docs/AGENT_BRIEF.md [read*]",
        "Task": "emit one line for P13 bite",
        "Target & scope": "Output only; never kernel/ledger/sched/service",
        "Timestamp": "2026-09-10T11:00:00-05:00",
        "Output": "work_orders/ccr/CREW/OUT | P13_BITE.json",
    }


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="cosmos_bite_p13_"))
    live = td / "live"
    write_sentinel(live, tree_id="p13-voice-drop-bite")
    (live / "state").mkdir(parents=True, exist_ok=True)
    (live / "logs").mkdir(parents=True, exist_ok=True)
    paths = CosmosPaths(live)

    valid_name = "wo-p13-valid.json"
    drops = {
        "wo-p13-malformed.json": {
            "name": "wo-p13-malformed.json",
            "path": f"{GH_DROP_PATH}/wo-p13-malformed.json",
            "sha": "sha-malformed",
            "type": "file",
            "html_url": f"https://github.com/{GH_REPO}/blob/main/"
            f"{GH_DROP_PATH}/wo-p13-malformed.json",
            "text": json.dumps({"Task": "not six fields"}),
        },
        "wo-p13-broken.json": {
            "name": "wo-p13-broken.json",
            "path": f"{GH_DROP_PATH}/wo-p13-broken.json",
            "sha": "sha-broken",
            "type": "file",
            "html_url": f"https://github.com/{GH_REPO}/blob/main/"
            f"{GH_DROP_PATH}/wo-p13-broken.json",
            "text": "<<<< not json",
        },
        valid_name: {
            "name": valid_name,
            "path": f"{GH_DROP_PATH}/{valid_name}",
            "sha": "sha-valid-p13",
            "type": "file",
            "html_url": f"https://github.com/{GH_REPO}/blob/main/"
            f"{GH_DROP_PATH}/{valid_name}",
            "text": json.dumps(_voice_valid_raw()),
        },
    }
    listed = [
        {k: drops[n][k] for k in ("name", "path", "sha", "type", "html_url")}
        for n in drops
    ]
    filed_ids: list[str] = []

    def track_drop(p, raw, *, order_id=None):
        filed_ids.append(order_id or "")
        return drop_order(p, raw, order_id=order_id)

    tick = poll_once(
        str(live),
        drain=True,
        list_fn=lambda: listed,
        fetch_fn=lambda e: dict(drops[e["name"]]),
        drop_fn=track_drop,
    )
    err = {e.get("name"): e for e in (tick.get("errors") or [])}
    dirs = work_order_dirs(paths)
    bucket_path = dirs["bucket"] / f"{Path(valid_name).stem}.json"
    bucket_rec = {}
    if bucket_path.is_file():
        bucket_rec = json.loads(bucket_path.read_text(encoding="utf-8"))

    gh_path = str(bucket_rec.get("github_path") or "").replace("\\", "/")

    rec = {
        "drop_path": GH_DROP_PATH,
        "repo": GH_REPO,
        "malformed_kind": err.get("wo-p13-malformed.json", {}).get("kind"),
        "malformed_typed": err.get("wo-p13-malformed.json", {}).get("kind")
        == "BAD_INPUT",
        "broken_kind": err.get("wo-p13-broken.json", {}).get("kind"),
        "broken_typed": err.get("wo-p13-broken.json", {}).get("kind") == "BAD_INPUT",
        "valid_filed": tick.get("filed_this_tick") == 1 and len(filed_ids) == 1,
        "valid_lands_drop_path": gh_path.startswith(f"{GH_DROP_PATH}/"),
        "valid_in_bucket": bucket_path.is_file(),
        "errors_n": len(tick.get("errors") or []),
    }
    rec["all_bite"] = (
        rec["malformed_typed"] is True
        and rec["broken_typed"] is True
        and rec["valid_filed"] is True
        and rec["valid_lands_drop_path"] is True
        and rec["valid_in_bucket"] is True
        and rec["drop_path"] == "work_orders/drop"
    )
    OUT.write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(rec, indent=2))
    return 0 if rec["all_bite"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
