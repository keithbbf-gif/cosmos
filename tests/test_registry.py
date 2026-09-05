#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: fail-closed runtime registry (wishlist #64).

A node is registered at RUNTIME only after a live rail call returns rc=0 +
non-empty body + the model that answered. Claims are not proofs. The
live/registry projection is rebuildable; the ledger is authority.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "cosmos"))

from cosmos_ledger import Ledger
from cosmos_registry import Registry, RegError, proof_ok

RESULTS = []


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                            # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def _reg(td, name="r.jsonl"):
    return Registry(Ledger(td / name, b"k", "core"))


def _pong(model="grok-4.6"):
    return lambda: {"ok": True, "rc": 0, "body": "PONG", "model": model,
                    "text": "PONG"}


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="cosmos_reg_"))

    check("proof_ok requires rc=0 + body + model",
          lambda: proof_ok({"ok": True, "rc": 0, "body": "PONG",
                            "model": "grok-4.6"}))
    check("proof_ok rejects empty body",
          lambda: not proof_ok({"ok": True, "rc": 0, "body": "  ",
                                "model": "x"}))
    check("proof_ok rejects missing model",
          lambda: not proof_ok({"ok": True, "rc": 0, "body": "PONG",
                                "model": ""}))
    check("proof_ok rejects rc!=0",
          lambda: not proof_ok({"ok": True, "rc": 2, "body": "PONG",
                                "model": "x"}))
    check("proof_ok rejects ok=False even with body",
          lambda: not proof_ok({"ok": False, "rc": 0, "body": "PONG",
                                "model": "x"}))

    reg = _reg(td)
    rec = reg.prove("sgh-api", "API", "core", "models", _pong())
    check("prove: live rc=0+body+model IS registered",
          lambda: rec["ok"] and rec["registered"] and rec["model"] == "grok-4.6"
          and rec["rc"] == 0 and rec["body_bytes"] > 0
          and "sgh-api" in reg.state()
          and "sgh-api" in reg.live_nodes())
    check("prove: LINK_REGISTERED + PROBE_RESULT ledgered",
          lambda: {"LINK_REGISTERED", "PROBE_RESULT"}
          <= {e["event"] for e in reg.ledger.verify()})

    dead = _reg(td, "d.jsonl")
    empty = dead.prove("gem-api", "API", "core", "models",
                       lambda: {"ok": True, "rc": 0, "body": "",
                                "model": "gemini-2.5-flash"})
    check("empty body is NOT registered (fail-closed)",
          lambda: not empty["ok"] and not empty["registered"]
          and "gem-api" not in dead.state()
          and "gem-api" not in dead.live_nodes())

    nomodel = _reg(td, "n.jsonl")
    nm = nomodel.prove("oa-api", "API", "core", "models",
                       lambda: {"ok": True, "rc": 0, "body": "PONG",
                                "model": ""})
    check("missing model is NOT registered",
          lambda: not nm["ok"] and "oa-api" not in nomodel.state())

    badrc = _reg(td, "b.jsonl")
    br = badrc.prove("claude-cli", "CLI", "core", "code",
                     lambda: {"ok": True, "rc": 2, "body": "PONG",
                              "model": "claude-haiku-4-5"})
    check("rc!=0 is NOT registered",
          lambda: not br["ok"] and "claude-cli" not in badrc.state())

    boom = _reg(td, "x.jsonl")
    bx = boom.prove("sgh-api", "API", "core", "models",
                    lambda: (_ for _ in ()).throw(RuntimeError("rail down")))
    check("raised live_call is NOT registered and is ledgered",
          lambda: not bx["ok"] and "sgh-api" not in boom.state()
          and any(e["event"] == "PROBE_RESULT" and e["payload"]["ok"] is False
                  for e in boom.ledger.verify()))

    check("unanswered prove still ledgers PROBE_RESULT (no LINK_REGISTERED)",
          lambda: [e["event"] for e in dead.ledger.verify()]
          == ["PROBE_RESULT"])

    dest = td / "registry"
    written = reg.file_runtime(dest)
    disk = json.loads((dest / "nodes.json").read_text(encoding="utf-8"))
    rails = json.loads((dest / "rails.json").read_text(encoding="utf-8"))
    check("file_runtime writes nodes.json with the proven link",
          lambda: written["count"] == 1 and disk["nodes"] == ["sgh-api"]
          and disk["matrix"][0]["model"] == "grok-4.6"
          and disk["matrix"][0]["rc"] == 0
          and disk["matrix"][0]["body_bytes"] > 0)
    check("rails.json is the same projection (not a second authority)",
          lambda: rails == disk)
    check("empty-dir is not identity: files carry schema + measurement",
          lambda: disk.get("schema") == "cosmos-registry/1"
          and disk.get("measured_at") is not None)

    dead.file_runtime(td / "emptyreg")
    empty_disk = json.loads(
        (td / "emptyreg" / "nodes.json").read_text(encoding="utf-8"))
    check("failed rails leave a MEASURED-empty projection, not a fake node",
          lambda: empty_disk["count"] == 0 and empty_disk["nodes"] == [])

    # a later failed prove drops the node from the runtime map
    drop = reg.prove("sgh-api", "API", "core", "models",
                     lambda: {"ok": False, "rc": 2, "body": "", "model": ""})
    check("dead re-prove drops the node from live_nodes (claim may remain)",
          lambda: not drop["ok"] and "sgh-api" not in reg.live_nodes()
          and "sgh-api" in reg.state())

    # existing claim/probe path still works (do not break wave4/v1)
    classic = _reg(td, "c.jsonl")
    classic.register("f5-api", "API", "core", "f5")
    classic.attach_probe("f5-api", lambda: (True, "api alive"))
    classic.probe("f5-api")
    check("classic register+probe still verifies (claim path unchanged)",
          lambda: classic.matrix()[0]["verified"] is True)
    check("classic import-liveness is NOT a runtime live_node (no model/body)",
          lambda: "f5-api" not in classic.live_nodes())
    check("bad rail type still BAD_TYPE",
          lambda: _bad_type(classic))

    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for label, ok, err in RESULTS:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (fail-closed prove; claim != proof)"
          % ("PASS" if not bad else "FAIL", len(RESULTS)))
    return 0 if not bad else 1


def _bad_type(reg):
    try:
        reg.register("x", "TELEPATHY", "a", "b")
    except RegError as e:
        return e.kind == "BAD_TYPE"
    return False


def test_registry():
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())
