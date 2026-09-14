#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Live evidence: Registry.prove() for sgh-api via default_live_call (bts_sgh).

Does not call poll_once(--live) for other wired rails. Never prints key material.

    py -3.14 cosmos\\_emit_sgh_api_rail_live.py --root V:\\A\\Ai\\COSMOS\\live

When Core :8770 or credentials are absent, reports UNMEASURED — never fake GREEN.
"""
from __future__ import annotations

import json
import socket
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "cosmos"))

from cosmos_paths import CosmosPaths  # noqa: E402
from cosmos_rails_prober import WIRED_NODES, default_live_call, open_registry  # noqa: E402

OUT = REPO / "builds" / "probe" / "_sgh_api_rail_live.json"
LID = "sgh-api"
KEEP = ("ok", "rc", "model", "model_source", "body", "body_bytes",
        "registered", "detail", "kind", "link_id")


def _core_reachable() -> dict:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.8)
    try:
        s.connect(("127.0.0.1", 8770))
        s.close()
        return {"ok": True, "detail": "tcp:8770 listening"}
    except OSError as e:
        return {"ok": False, "detail": f"{type(e).__name__}: {e}"}


def _core_status() -> dict:
    try:
        req = urllib.request.Request("http://127.0.0.1:8770/api/v1/status")
        with urllib.request.urlopen(req, timeout=2.0) as r:  # noqa: S310
            body = json.loads(r.read().decode("utf-8"))
            return {"ok": True, "http": int(r.status), "tree_id": body.get("tree_id")}
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as e:
        return {"ok": False, "detail": f"{type(e).__name__}: {e}"}


def _slim(rec: dict) -> dict:
    out = {k: rec.get(k) for k in KEEP}
    body = str(out.get("body") or "")
    if len(body) > 240:
        out["body"] = body[:240] + "…"
    dumped = json.dumps(out)
    if "sk-" in dumped.lower() or "xai-" in dumped.lower():
        out["body"] = "<redacted: key-shaped token in body>"
        out["detail"] = str(out.get("detail") or "")[:80]
    return out


def _probe_tail(paths: CosmosPaths, n: int = 3) -> list[dict]:
    led = paths.ledger("authority.jsonl")
    if not led.is_file():
        return []
    rows = []
    for line in led.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        if rec.get("event") != "PROBE_RESULT":
            continue
        p = rec.get("payload") or {}
        if p.get("link_id") != LID:
            continue
        rows.append({
            "seq": rec.get("seq"),
            "ok": p.get("ok"),
            "model": p.get("model"),
            "rc": p.get("rc"),
            "body_bytes": p.get("body_bytes"),
        })
    return rows[-n:]


def main() -> int:
    root = Path(sys.argv[sys.argv.index("--root") + 1]) if "--root" in sys.argv else (
        REPO / "live")
    spec_by = {s["link_id"]: s for s in WIRED_NODES}
    spec = spec_by.get(LID)
    if spec is None:
        rec = {"ok": False, "error": f"{LID} not in WIRED_NODES"}
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
        print(json.dumps(rec, indent=1))
        return 2
    try:
        paths = CosmosPaths(root)
    except Exception as e:  # noqa: BLE001
        rec = {"ok": False, "measurement": "UNMEASURED",
               "error": f"paths: {type(e).__name__}: {e}"}
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
        print(json.dumps(rec, indent=1))
        return 2
    key_path = paths.config("xai_api_key.txt")
    core_tcp = _core_reachable()
    core_http = _core_status() if core_tcp.get("ok") else {"ok": False,
                                                            "detail": "core down"}
    reg = open_registry(paths)
    proof = None
    runtime = {}
    ledger_probe = []
    if reg is None:
        measurement = "UNMEASURED"
        prove_err = "NO install_key.bin — registry authority closed"
    elif not key_path.exists():
        measurement = "UNMEASURED"
        prove_err = "NO xai_api_key.txt — credential absent"
    else:
        measurement = "LIVE"
        prove_err = None
        rec = reg.prove(
            LID, spec["rail_type"], spec["src"], spec["dst"],
            default_live_call(paths, spec))
        proof = _slim(rec)
        runtime = reg.file_runtime(paths.role("registry"))
        ledger_probe = _probe_tail(paths)
        if not proof.get("ok"):
            measurement = "FAILED"
    out = {
        "schema": "cosmos-sgh-api-rail-live/1",
        "link_id": LID,
        "tree_id": getattr(paths.sentinel, "tree_id", None),
        "measurement": measurement,
        "core_8770": core_tcp,
        "core_status": core_http,
        "key_present": key_path.exists(),
        "key_bytes": key_path.stat().st_size if key_path.exists() else None,
        "wired": {
            "rail_type": spec["rail_type"],
            "src": spec["src"],
            "dst": spec["dst"],
            "module": spec.get("module"),
            "family": spec.get("family"),
        },
        "prove_error": prove_err,
        "proof": proof,
        "ledger_probe_result_tail": ledger_probe,
        "runtime": {
            "count": runtime.get("count"),
            "nodes": list(runtime.get("nodes") or []),
            "sgh_in_nodes": LID in (runtime.get("nodes") or []),
        },
        "ok": measurement == "LIVE" and bool(proof and proof.get("ok")),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=1, default=str) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=1, default=str))
    return 0 if out["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
