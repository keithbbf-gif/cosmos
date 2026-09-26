#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Choose Head. One host sits the ORC. The others stay installed.

Overlapping features (session, skills, MCP, browser, terminal, keys,
Gitur) get one owner. The head owns a feature it can do. A feature it
cannot do stays with the incumbent. The others are shadow: present, not
a second runner. This is the deconflict. It does not load a plugin and
it does not start a host.

    py -3.14 cosmos\\cosmos_head.py --selftest
"""
from __future__ import annotations

import json
from datetime import datetime

SCHEMA = "cosmos-head/1"
NAME = "head.json"
# Keith 2026-09-22: any of these can be the head. Muse is on OpenWork now.
DEFAULT = "openwork"
HEADS = (
    {"id": "cosmos", "label": "COSMOS",
     "note": "Core, cDeck, the ledger."},
    {"id": "openwork", "label": "OpenWork",
     "note": "Muse Spark 1.3 on OpenCode. Skills, plugins, MCP, browser."},
    {"id": "cowork", "label": "CoWork",
     "note": "A head choice. Does not turn the fenced Cowork lane into a writer."},
    {"id": "hermes", "label": "Hermes",
     "note": "Solar Pro4 is free here. Keys and the terminal stay here when Hermes is not head."},
    {"id": "cursor", "label": "Cursor",
     "note": "Gitur check and the desktop agent."},
)
# Who can run the feature. First id is the incumbent when the head cannot.
FEATURES = {
    "session": ("cosmos", "openwork", "cowork", "hermes", "cursor"),
    "skills": ("openwork", "cosmos"),
    "mcp": ("openwork", "cosmos", "cursor"),
    "browser": ("openwork", "cosmos"),
    "terminal": ("hermes", "cursor", "cosmos"),
    "keys": ("hermes", "cosmos"),
    "gitur": ("cursor", "cosmos"),
}


class HeadError(Exception):
    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def _iso_now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _path(paths):
    d = paths.role("state", "cdeck")
    d.mkdir(parents=True, exist_ok=True)
    return d / NAME


def _known(head: str) -> str:
    hid = str(head or "").strip().lower()
    ids = {row["id"] for row in HEADS}
    if hid not in ids:
        raise HeadError("BAD_HEAD", "head is " + ", ".join(row["id"] for row in HEADS))
    return hid


def harmonize(head: str) -> dict:
    """One owner per feature. Shadow hosts do not also run it."""
    hid = _known(head)
    features = {}
    for name, hosts in FEATURES.items():
        if hid in hosts:
            owner = hid
        else:
            owner = hosts[0]
        features[name] = {
            "owner": owner,
            "shadow": [h for h in hosts if h != owner],
        }
    return features


def _blank() -> dict:
    return {
        "schema": SCHEMA,
        "head": DEFAULT,
        "heads": [dict(row) for row in HEADS],
        "plugin": {
            "id": "head-harmonize",
            "does": "One owner per overlapping feature. Shadow hosts stay installed and do not run it.",
            "runs": False,
        },
        "features": harmonize(DEFAULT),
    }


def load_head(paths) -> dict:
    path = _path(paths)
    if not path.is_file():
        return _blank()
    try:
        rec = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise HeadError("UNREADABLE", str(e)) from e
    if not isinstance(rec, dict):
        raise HeadError("UNPARSEABLE", "head file is not an object")
    hid = _known(rec.get("head") or DEFAULT)
    rec["head"] = hid
    rec["heads"] = [dict(row) for row in HEADS]
    rec["features"] = harmonize(hid)
    rec["plugin"] = _blank()["plugin"]
    rec["schema"] = SCHEMA
    return rec


def set_head(paths, head: str) -> dict:
    hid = _known(head)
    rec = _blank()
    rec["head"] = hid
    rec["at"] = _iso_now()
    rec["features"] = harmonize(hid)
    rec["model"] = "meta/muse-spark-1.3-contributor"
    rec["model_note"] = (
        "Muse stays the ORC model. Solar Pro4 is the free model when the head is Hermes."
    )
    if hid == "hermes":
        rec["model"] = "upstage/solar-pro4"
        rec["model_note"] = "Solar Pro4, free on Hermes."
    path = _path(paths)
    path.write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
    return rec


def _selftest() -> int:
    import tempfile
    from pathlib import Path

    from cosmos_paths import CosmosPaths, write_sentinel

    ok = True

    def check(label, cond):
        nonlocal ok
        print(("  OK  " if cond else "  FAIL") + " " + label)
        if not cond:
            ok = False

    check("OpenWork owns session, skills, and browser",
          harmonize("openwork")["session"]["owner"] == "openwork"
          and harmonize("openwork")["skills"]["owner"] == "openwork"
          and "cosmos" in harmonize("openwork")["skills"]["shadow"]
          and harmonize("openwork")["keys"]["owner"] == "hermes")
    check("Hermes does not take Gitur from Cursor",
          harmonize("hermes")["gitur"]["owner"] == "cursor"
          and harmonize("hermes")["keys"]["owner"] == "hermes")
    bad = False
    try:
        _known("notepad")
    except HeadError as e:
        bad = e.kind == "BAD_HEAD"
    check("an unknown head is refused", bad)
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        write_sentinel(root, tree_id="head-test")
        (root / "state").mkdir()
        paths = CosmosPaths(root)
        check("unset head is OpenWork", load_head(paths)["head"] == "openwork")
        saved = set_head(paths, "Hermes")
        check("Hermes seats Solar and still shadows Gitur",
              saved["head"] == "hermes"
              and saved["model"] == "upstage/solar-pro4"
              and saved["features"]["gitur"]["owner"] == "cursor"
              and saved["plugin"]["runs"] is False)
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        raise SystemExit(_selftest())
    print("cosmos_head: --selftest", file=sys.stderr)
    raise SystemExit(2)
