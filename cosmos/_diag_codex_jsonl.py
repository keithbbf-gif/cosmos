#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Inspect Codex --json event shape. Types + model-key locations only.

Never prints key material, never prints full event bodies.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "cosmos"))

from cosmos_codex_rail import (  # noqa: E402
    CodexRail, key_path_for, load_spec, spec_path_for, _lift_jsonl,
)
from cosmos_paths import CosmosPaths  # noqa: E402
from cosmos_rails_prober import LIVE_PROMPT, LIVE_TIMEOUT_S  # noqa: E402

OUT = REPO / "cosmos" / "_diag_codex_jsonl.json"


def _walk_models(obj, path=""):
    found = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{path}.{k}" if path else k
            if k == "model" and isinstance(v, str) and v.strip():
                found.append({"path": p, "value": v.strip()[:80]})
            found.extend(_walk_models(v, p))
    elif isinstance(obj, list):
        for i, v in enumerate(obj[:20]):
            found.extend(_walk_models(v, f"{path}[{i}]"))
    return found


def main() -> int:
    paths = CosmosPaths(REPO / "live")
    spec = load_spec(spec_path_for(paths))
    keyp = key_path_for(paths, spec)
    ws = Path(tempfile.mkdtemp(prefix="codex_jsonl_"))
    rail = CodexRail(keyp, spec, live_root=paths.root)
    rec = rail.dispatch({
        "prompt": LIVE_PROMPT,
        "workspace": str(ws),
        "timeout_s": LIVE_TIMEOUT_S,
    })
    stdout = rec.get("stdout_tail") or rec.get("out") or ""
    events = []
    models = []
    for raw in stdout.splitlines():
        line = raw.strip()
        if not line.startswith("{"):
            continue
        try:
            ev = json.loads(line)
        except ValueError:
            events.append({"parse": "unparseable", "keys": []})
            continue
        if not isinstance(ev, dict):
            continue
        events.append({
            "type": ev.get("type"),
            "keys": sorted(ev.keys()),
        })
        models.extend(_walk_models(ev))
    lifted = _lift_jsonl(stdout)
    out = {
        "schema": "cosmos-codex-jsonl-diag/1",
        "ok": rec.get("ok"),
        "rc": rec.get("rc"),
        "kind": rec.get("kind"),
        "detail": rec.get("detail") or rec.get("done_why"),
        "last_message_head": (rec.get("last_message") or rec.get("text") or "")[:80],
        "lifted_model": lifted.get("model"),
        "event_count": len(events),
        "event_types": [e.get("type") for e in events],
        "event_keys": events,
        "model_fields": models,
        "stdout_bytes": len(stdout.encode("utf-8")),
        "stderr_head": (rec.get("stderr_tail") or "")[:200],
    }
    dumped = json.dumps(out)
    if "sk-" in dumped.lower() and "sk-…" not in dumped.lower():
        out["stderr_head"] = "<redacted>"
    OUT.write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
