#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: GROK/GEM node workers. Isolated from the live tree.

Proves: own buckets, PAUSE idle (drain=False picks up NOTHING), commanded
--once drain, V: result file, rail binding (model/usd/link_id), DHx pickup
stamp, collector registration. Fake rail_call so no live spend. No BTS import.
Does not modify kernel/ledger/sched/service.
"""
from __future__ import annotations

import json
import re
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "cosmos"))

from cosmos_kernel import install  # noqa: E402
from cosmos_node_worker import (  # noqa: E402
    NODES, bucket_dir, canon_node, dest_dir, execute_handoff, execute_via_rail,
    list_drop_files, parse_task, pause_flag, poll_once, v_returns,
)
from cosmos_paths import CosmosPaths  # noqa: E402

RESULTS = []
BTS_IMPORT = re.compile(r"^\s*(?:from|import)\s+bts_\w+", re.M)
COSMOS_DIR = Path(__file__).resolve().parent.parent / "cosmos"


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:  # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def _write(p: Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def _fake_rail(prompt: str) -> dict:
    return {
        "ok": True, "kind": "API", "text": "PONG",
        "usd": 0.004, "node": "fake_sgh", "model": "fake-grok",
        "link_id": "sgh-api",
    }


def main() -> int:
    for name in ("cosmos_node_worker.py", "cosmos_grok_worker.py",
                 "cosmos_gem_worker.py"):
        src = (COSMOS_DIR / name).read_text(encoding="utf-8")
        check(f"{name} imports no bts_*", lambda s=src: not BTS_IMPORT.search(s))

    check("grok task name",
          lambda: NODES["grok"]["task_name"] == "COSMOS Grok Worker")
    check("gem task name",
          lambda: NODES["gem"]["task_name"] == "COSMOS GEM Worker")
    check("g46 aliases to grok", lambda: canon_node("g46") == "grok")
    check("gemini aliases to gem", lambda: canon_node("gemini") == "gem")

    td = Path(tempfile.mkdtemp(prefix="cosmos_node_worker_"))
    root = install(td / "live", tree_id="spike-node-worker")
    paths = CosmosPaths(root)
    dhx = td / "docs" / "AGENT_BRIEF.md"
    _write(dhx, (
        "# DHx\n\n"
        "## Assignment log — APPEND-ONLY markers\n\n"
        "## Active assignments\n"
        "- none\n"
    ))

    grok_bucket = bucket_dir(paths, "grok")
    gem_bucket = bucket_dir(paths, "gem")
    check("grok bucket is live/buckets/grok",
          lambda: grok_bucket == paths.root / "buckets" / "grok")
    check("gem bucket is live/buckets/gem",
          lambda: gem_bucket == paths.root / "buckets" / "gem")
    check("V returns is live/returns/grok",
          lambda: v_returns(paths, "grok") == paths.root / "returns" / "grok")

    drop = grok_bucket / "pong.json"
    _write(drop, json.dumps({
        "prompt": "Reply with the single word PONG.",
        "out": "V",
        "id": "proof-pong",
    }))
    parsed = parse_task(drop)
    check("json drop parses prompt + out V",
          lambda: parsed["prompt"].startswith("Reply") and parsed["out"] == "V")
    txt = grok_bucket / "hello.txt"
    _write(txt, "say hello from a txt drop")
    check("txt drop is the prompt",
          lambda: parse_task(txt)["prompt"] == "say hello from a txt drop")
    txt.unlink()

    pause_p = paths.state("control", "PAUSE.flag")
    _write(pause_p, json.dumps({
        "state": "PAUSED", "mode": "hold", "reason": "selftest",
        "set_by": "test",
    }))
    paused_rec = poll_once(str(root), "grok", drain=False, rail_call=_fake_rail,
                           dhx_path=dhx)
    check("PAUSE present is detected", lambda: pause_flag(paths) is not None)
    check("drain=False heartbeat is PAUSED",
          lambda: paused_rec.get("state") == "PAUSED"
          and paused_rec.get("tick") == "paused")
    check("PAUSE idle picks up NOTHING",
          lambda: drop.exists() and paused_rec.get("picked_this_tick") == 0)
    check("grok heartbeat file emitted while paused",
          lambda: paths.logs("grok_worker_heartbeat.json").exists())

    rec = poll_once(str(root), "grok", drain=True, rail_call=_fake_rail,
                    dhx_path=dhx)
    check("once_while_paused still drains",
          lambda: rec.get("picked_this_tick") == 1)
    job = rec["jobs"][0]
    v_path = Path(job["v_path"])
    check("V result file exists", lambda: v_path.is_file())
    body = json.loads(v_path.read_text(encoding="utf-8"))
    check("result bound to rail model",
          lambda: body["rail"]["model"] == "fake-grok")
    check("result bound to spend usd",
          lambda: body["rail"]["usd"] == 0.004)
    check("result bound to link_id sgh-api",
          lambda: body["rail"]["link_id"] == "sgh-api")
    check("result text is the real rail answer",
          lambda: body["rail"]["text"] == "PONG")
    check("drop staged to processed (never deleted)",
          lambda: not drop.exists()
          and list((grok_bucket / "processed").glob("*pong.json")))
    dhx_text = dhx.read_text(encoding="utf-8")
    check("DHx pickup marker for GROK",
          lambda: "GROK" in dhx_text and "pickup" in dhx_text
          and " · " in dhx_text)
    idx = paths.state("collector", "index.jsonl")
    check("collector return row registered",
          lambda: idx.exists() and "node_worker_return" in idx.read_text(
              encoding="utf-8"))

    gem_drop = gem_bucket / "gem_pong.json"
    _write(gem_drop, json.dumps({"prompt": "Reply PONG.", "out": "V"}))

    def _fake_gem(prompt: str) -> dict:
        return {"ok": True, "kind": "API", "text": "PONG",
                "usd": 0.01, "node": "fake_gem", "model": "fake-gemini",
                "link_id": "gem-api"}

    grec = poll_once(str(root), "gem", drain=True, rail_call=_fake_gem,
                     dhx_path=dhx)
    check("gem --once drains its own bucket",
          lambda: grec.get("picked_this_tick") == 1)
    gjob = grec["jobs"][0]
    gpath = Path(gjob["v_path"])
    check("gem result landed under live/returns/gem",
          lambda: gpath.is_file()
          and gpath.parent.name == "gem"
          and gpath.parent.parent.name == "returns")
    gbody = json.loads(Path(gjob["v_path"]).read_text(encoding="utf-8"))
    check("gem result bound to gem-api",
          lambda: gbody["rail"]["link_id"] == "gem-api"
          and gbody["rail"]["model"] == "fake-gemini")
    check("gem heartbeat file emitted",
          lambda: paths.logs("gem_worker_heartbeat.json").exists())
    check("grok worker does not pick gem drops",
          lambda: list_drop_files(gem_bucket) == [])

    def _empty(prompt: str) -> dict:
        return {"ok": True, "kind": "API", "text": "", "rc": 0,
                "stderr": "no stdout"}

    for node_id in ("grok", "gem", "oa"):
        empty = execute_via_rail(paths, NODES[node_id], "x", rail_call=_empty)
        check(f"{node_id} empty rail body is FAILED not rc=0",
              lambda e=empty: e.get("ok") is False
              and e.get("kind") == "EMPTY_OUTPUT"
              and e.get("rc") != 0
              and "no stdout" in (e.get("stderr_tail") or ""))

    def _kept_rc(prompt: str) -> dict:
        return {"ok": True, "text": "", "rc": 7, "stderr": "model flag missing"}

    kept = execute_via_rail(paths, NODES["gem"], "x", rail_call=_kept_rc)
    check("empty body preserves the real rc (not swallowed to 0)",
          lambda: kept.get("ok") is False and kept.get("rc") == 7
          and "model flag missing" in (kept.get("stderr_tail") or ""))

    empty_p = paths.root / "queue" / "returns" / "cm" / "oa_empty.json"
    empty_p.parent.mkdir(parents=True, exist_ok=True)
    eh = execute_handoff(str(root), "oa", "OAi", "Reply PONG.", str(empty_p),
                         rail_call=_empty, dhx_path=dhx)
    check("OA execute_handoff empty is not fake-DONE",
          lambda: eh.get("done") is False and eh.get("rc") != 0
          and eh.get("done_why") == "empty_stdout")

    worker_src = (COSMOS_DIR / "cosmos_node_worker.py").read_text(encoding="utf-8")
    check("node_worker has no BTS drive literal",
          lambda: "V:\\Ai\\BTS_MESH" not in worker_src
          and "_BTS =" not in worker_src)
    check("process_drop has no bare except Exception",
          lambda: "except Exception" not in worker_src.split(
              "def process_drop", 1)[-1].split("def execute_handoff", 1)[0])

    check("dest V resolves under the runtime root",
          lambda: dest_dir(paths, "grok", "V") == paths.root / "returns" / "grok")

    passed = sum(1 for _, ok, _ in RESULTS if ok)
    failed = [(lab, err) for lab, ok, err in RESULTS if not ok]
    print(f"test_node_worker {passed}/{len(RESULTS)}")
    for lab, err in failed:
        print(f"  FAIL {lab} {err}")
    return 0 if not failed else 2


if __name__ == "__main__":
    raise SystemExit(main())
