#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bite: P13 Voice Drop validation (PLAN phase E — ingress).

Malformed GitHub work_orders/drop JSON refuses typed (BAD_INPUT). Valid drop
from work_orders/drop lands in live/state/work_orders/bucket/ with provenance.
Reuses cosmos_sgh_drop_ingest poll_once + file_drop; no network; no Actions.

    py -3.14 cosmos/_bite_p13_voice_drop.py
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent / "cosmos"
sys.path.insert(0, str(HERE))

from cosmos_paths import CosmosPaths, write_sentinel  # noqa: E402
from cosmos_sgh_drop_ingest import (  # noqa: E402
    GH_DROP_PATH,
    GH_REPO,
    IngestError,
    file_drop,
    poll_once,
)
from cosmos_work_order import OrderError, work_order_dirs  # noqa: E402

OUT = HERE / "_bite_p13_voice_drop.json"

GROK_VALID = {
    "Agent": "xAI | Grok | grok-4.6",
    "Context source": "docs/AGENT_BRIEF.md [read*]",
    "Task": "emit one line",
    "Target & scope": "Output only",
    "Timestamp": "2026-09-02T11:31:00-05:00",
    "Output": "proposals | RESULT.json",
}


def _live(root: Path) -> CosmosPaths:
    write_sentinel(root, tree_id="p13-voice-drop-bite")
    (root / "state").mkdir(parents=True, exist_ok=True)
    (root / "logs").mkdir(parents=True, exist_ok=True)
    return CosmosPaths(root)


def _entry(name: str, *, text: str, sha: str) -> dict:
    path = f"{GH_DROP_PATH}/{name}"
    return {
        "name": name,
        "path": path,
        "sha": sha,
        "type": "file",
        "html_url": f"https://github.com/{GH_REPO}/blob/main/{path}",
        "text": text,
    }


def _poll(paths: CosmosPaths, *entries: dict) -> dict:
    listed = [
        {k: e[k] for k in ("name", "path", "sha", "type", "html_url")}
        for e in entries
    ]
    by_name = {e["name"]: e for e in entries}

    def list_fn():
        return listed

    def fetch_fn(row):
        return dict(by_name[row["name"]])

    return poll_once(str(paths.root), list_fn=list_fn, fetch_fn=fetch_fn)


def naive_bucket_write(paths: CosmosPaths, fetched: dict) -> Path:
    """Pre-validation scar: JSON object written to bucket without parse_order."""
    raw = json.loads(fetched["text"])
    dest = work_order_dirs(paths)["bucket"] / fetched["name"]
    dest.write_text(json.dumps(raw), encoding="utf-8")
    return dest


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="cosmos_bite_p13_"))
    paths = _live(td / "live")
    dirs = work_order_dirs(paths)

    malformed = {
        "Context source": "docs/AGENT_BRIEF.md [read*]",
        "Task": "missing Agent field",
        "Target & scope": "Output only",
        "Timestamp": "2026-09-10T12:00:00-05:00",
        "Output": "proposals | RESULT.json",
    }
    bad_entry = _entry("wo-malformed.json", text=json.dumps(malformed), sha="sha-mal")
    bad_tick = _poll(paths, bad_entry)
    bad_err = (bad_tick.get("errors") or [{}])[0]
    malformed_refused = (
        bad_tick.get("filed_this_tick") == 0
        and bad_err.get("kind") == "BAD_INPUT"
        and "Agent" in str(bad_err.get("error") or "")
        and not any(dirs["bucket"].glob("wo-malformed*.json"))
    )

    not_json = _entry("wo-not-json.json", text="{not json", sha="sha-njson")
    njson_tick = _poll(paths, not_json)
    njson_err = (njson_tick.get("errors") or [{}])[0]
    not_json_refused = (
        njson_tick.get("filed_this_tick") == 0
        and njson_err.get("kind") == "BAD_INPUT"
    )

    valid_entry = _entry("wo-valid.json", text=json.dumps(GROK_VALID), sha="sha-valid")
    good_tick = _poll(paths, valid_entry)
    bucket_path = dirs["bucket"] / "wo-valid.json"
    bucket_rec = json.loads(bucket_path.read_text(encoding="utf-8")) if bucket_path.is_file() else {}
    valid_landed = (
        good_tick.get("filed_this_tick") == 1
        and bucket_path.is_file()
        and bucket_rec.get("state") == "DROPPED"
        and str(bucket_rec.get("github_path") or "").startswith(f"{GH_DROP_PATH}/")
        and bucket_rec.get("github_repo") == GH_REPO
    )

    direct_kind = None
    try:
        file_drop(
            paths,
            _entry("direct-bad.json", text=json.dumps(malformed), sha="x"),
        )
    except OrderError as e:
        direct_kind = e.kind

    stale = dirs["bucket"] / "wo-naive-scar.json"
    naive_bucket_write(
        paths,
        _entry("wo-naive-scar.json", text=json.dumps(malformed), sha="sha-naive"),
    )
    naive_body = json.loads(stale.read_text(encoding="utf-8")) if stale.is_file() else {}
    old_wrote_malformed = stale.is_file() and "Agent" not in naive_body

    src = (HERE / "cosmos_sgh_drop_ingest.py").read_text(encoding="utf-8")
    prod = src.split("def _selftest", 1)[0]
    no_github_delete = (
        " -X DELETE" not in prod
        and "method=DELETE" not in prod
    )
    drop_path_is_github_inbox = GH_DROP_PATH == "work_orders/drop"

    rec = {
        "malformed_refused_typed": malformed_refused,
        "not_json_refused_typed": not_json_refused,
        "valid_lands_bucket_from_drop_path": valid_landed,
        "file_drop_refuses_malformed_kind": direct_kind,
        "old_naive_write_would_land_malformed": old_wrote_malformed,
        "no_github_delete": no_github_delete,
        "github_drop_path": GH_DROP_PATH,
        "drop_path_is_work_orders_drop": drop_path_is_github_inbox,
    }
    rec["all_bite"] = (
        rec["malformed_refused_typed"] is True
        and rec["not_json_refused_typed"] is True
        and rec["valid_lands_bucket_from_drop_path"] is True
        and rec["file_drop_refuses_malformed_kind"] == "BAD_INPUT"
        and rec["old_naive_write_would_land_malformed"] is True
        and rec["no_github_delete"] is True
        and rec["drop_path_is_work_orders_drop"] is True
    )
    OUT.write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(rec, indent=2))
    return 0 if rec["all_bite"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
