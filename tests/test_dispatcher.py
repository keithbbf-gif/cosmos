#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: auto-context dispatcher. Isolated from the live tree.

Proves: shared bucket drop -> TAG parse -> context pull -> boundaries
attached -> agent created (native dispatch) -> DHx + session assignments
jsonl filed -> output folder stamped -> PAUSE idle (drain=False) leaves
the drop. No BTS import. Does not modify kernel/ledger/sched/service.
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
from cosmos_dispatcher_daemon import (  # noqa: E402
    TASK_NAME, bucket_root, list_drop_files, pause_flag, poll_once,
    process_drop, load_config,
)
from cosmos_dispatch import (  # noqa: E402
    compose_agent_prompt, load_boundaries_text, parse_agent_tag,
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


def main() -> int:
    src_disp = (COSMOS_DIR / "cosmos_dispatcher_daemon.py").read_text(
        encoding="utf-8")
    src_pull = (COSMOS_DIR / "cosmos_context_pull.py").read_text(encoding="utf-8")
    check("dispatcher imports no bts_*", lambda: not BTS_IMPORT.search(src_disp))
    check("context_pull imports no bts_*", lambda: not BTS_IMPORT.search(src_pull))
    check("task name is COSMOS Dispatcher", lambda: TASK_NAME == "COSMOS Dispatcher")

    parsed = parse_agent_tag("G46")
    check("G46 -> tag G46 kind grok",
          lambda: parsed["tag"] == "G46" and parsed["kind"] == "grok")
    check("GW -> Grok Build tag",
          lambda: parse_agent_tag("GW")["tag"] == "GW"
          and parse_agent_tag("GW")["kind"] == "grok")
    check("GEM -> gem handoff kind",
          lambda: parse_agent_tag("GEM")["kind"] == "gem")
    check("OAi -> oa", lambda: parse_agent_tag("OAi")["kind"] == "oa")
    check("SSA -> groq", lambda: parse_agent_tag("SSA")["kind"] == "groq")
    check("CURSOR -> cursor", lambda: parse_agent_tag("CURSOR")["kind"] == "cursor")

    bounds = load_boundaries_text()
    check("boundaries file is non-empty", lambda: "Orchestrator" in bounds)
    prompt = compose_agent_prompt(
        "reply PONG", context_blob="[user]\nhello", context_hint="cm",
        boundaries=bounds, provenance={"session_id": "s1",
                                       "byte_start": 0, "byte_end": 10,
                                       "path": "x.jsonl"})
    check("prompt carries assignment", lambda: "reply PONG" in prompt)
    check("prompt carries context blob", lambda: "[user]\nhello" in prompt)
    check("prompt auto-attaches AGENT_BOUNDARIES",
          lambda: "MANDATORY ADDENDUM" in prompt and "Propose" in prompt)

    td = Path(tempfile.mkdtemp(prefix="cosmos_dispatcher_"))
    root = install(td / "live", tree_id="spike-dispatcher")
    paths = CosmosPaths(root)
    dhx = td / "docs" / "AGENT_BRIEF.md"
    _write(dhx, (
        "# DHx\n\n"
        "## Assignment log — APPEND-ONLY markers\n\n"
        "## Active assignments\n"
        "- none\n"
    ))
    sess = td / "sessions" / "sess-test-42"
    transcript = sess / "chat_history.jsonl"
    _write(transcript, json.dumps({
        "type": "user",
        "content": [{"type": "text", "text": "Keith: build the dispatcher"}],
    }) + "\n" + json.dumps({
        "type": "assistant",
        "content": [{"type": "text", "text": "on it"}],
    }) + "\n")
    cfg_path = paths.config("dispatcher.json")
    _write(cfg_path, json.dumps({
        "schema": "cosmos-dispatcher/1",
        "bucket_mode": "shared",
        "tail_turns": 8,
        "tail_kb": 32,
        "sessions_roots": [str(td / "sessions")],
    }, indent=1))

    # PAUSE idle: drop sits, drain=False does not create an agent
    drop = bucket_root(paths) / "pong.json"
    _write(drop, json.dumps({"agent": "G46", "assignment": "reply PONG"}))
    pause_p = paths.state("control", "PAUSE.flag")
    _write(pause_p, json.dumps({
        "state": "PAUSED", "mode": "hold", "reason": "selftest",
        "set_by": "test",
    }))
    paused_rec = poll_once(str(root), drain=False)
    check("PAUSE present is detected",
          lambda: pause_flag(paths) is not None)
    check("drain=False heartbeat is PAUSED",
          lambda: paused_rec.get("state") == "PAUSED"
          and paused_rec.get("tick") == "paused")
    check("PAUSE idle does not consume the drop",
          lambda: drop.exists() and paused_rec.get("dropped_this_tick") == 0)
    check("heartbeat file emitted",
          lambda: paths.logs("dispatcher_heartbeat.json").exists())

    # Commanded drain (--once): process even with PAUSE present
    rec = poll_once(str(root), drain=True)
    check("once_while_paused still drains",
          lambda: rec.get("dropped_this_tick") == 1 and rec.get("ok") is True)
    job = rec["jobs"][0]
    out_dir = Path(job["out_dir"])
    check("output folder exists", lambda: out_dir.is_dir())
    check("output folder is tagged G46", lambda: "G46" in str(out_dir))
    check("assignment.json emitted in out dir",
          lambda: (out_dir / "assignment.json").exists())
    check("context.txt emitted", lambda: (out_dir / "context.txt").exists())
    pkt = json.loads((out_dir / "assignment.json").read_text(encoding="utf-8"))
    check("packet timestamp is ISO",
          lambda: "T" in pkt["timestamp"] and pkt["tag"] == "G46")
    check("context pulled from fake transcript",
          lambda: pkt["context"]["ok"] is True
          and "Keith: build the dispatcher" in (out_dir / "context.txt").read_text(
              encoding="utf-8"))
    check("context provenance has byte range",
          lambda: pkt["context"]["byte_start"] is not None
          and pkt["context"]["byte_end"] is not None)
    prompt_txt = (out_dir / "prompt.txt").read_text(encoding="utf-8")
    check("fed assignment + boundaries addendum",
          lambda: "reply PONG" in prompt_txt and "MANDATORY ADDENDUM" in prompt_txt)
    check("drop staged to processed (never deleted to nowhere)",
          lambda: not drop.exists()
          and list((bucket_root(paths) / "processed").glob("*pong.json")))
    check("agent job created",
          lambda: bool(job.get("job_file"))
          and str(job["job_file"]).endswith(".py"))
    dj = json.loads((out_dir / "dispatch.json").read_text(encoding="utf-8"))
    check("dispatch created the grok job",
          lambda: dj.get("created") is True and dj.get("kind") == "grok")
    check("native_job_id bound", lambda: bool(dj.get("native_job_id")))
    check("DHx marker auto-stamped",
          lambda: dj.get("dhx", {}).get("wrote") is True
          or (dj.get("marker") and dj["marker"] in dhx.read_text(encoding="utf-8")))
    dhx_text = dhx.read_text(encoding="utf-8")
    check("DHx assignment log has G46 marker",
          lambda: "G46" in dhx_text and " · " in dhx_text)
    apath = Path(job["assignments_path"])
    check("session-scoped assignments jsonl exists", lambda: apath.exists())
    arows = [json.loads(ln) for ln in apath.read_text(encoding="utf-8").splitlines()
             if ln.strip()]
    check("assignment row names tag + out_dir + timestamp",
          lambda: arows and arows[-1]["tag"] == "G46"
          and arows[-1]["out_dir"] == str(out_dir)
          and arows[-1]["timestamp"] == pkt["timestamp"])
    check("assignment row bound to real out_dir",
          lambda: Path(arows[-1]["out_dir"]).is_dir())
    idx = paths.state("collector", "index.jsonl")
    check("collector assignment row registered",
          lambda: idx.exists() and "dispatch_assignment" in idx.read_text(
              encoding="utf-8"))

    # per_agent config option
    cfg = load_config(paths)
    check("default after write is shared",
          lambda: cfg.get("bucket_mode") == "shared")
    _write(cfg_path, json.dumps({"bucket_mode": "per_agent",
                                 "sessions_roots": [str(td / "sessions")]}))
    cfg2 = load_config(paths)
    check("per_agent config option honored",
          lambda: cfg2.get("bucket_mode") == "per_agent")
    per = bucket_root(paths) / "GEM"
    _write(per / "gem.json", json.dumps(
        {"agent": "GEM", "assignment": "say hi", "out": "gem-hi"}))
    listed = list_drop_files(paths, cfg2)
    check("per_agent lists the GEM drop",
          lambda: any(p.name == "gem.json" for p in listed))

    passed = sum(1 for _, ok, _ in RESULTS if ok)
    failed = [(lab, err) for lab, ok, err in RESULTS if not ok]
    print(f"test_dispatcher {passed}/{len(RESULTS)}")
    for lab, err in failed:
        print(f"  FAIL {lab} {err}")
    return 0 if not failed else 2


if __name__ == "__main__":
    raise SystemExit(main())
