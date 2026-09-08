#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: cosmos_dispatch harness. Isolated from the live BTS queue and live DHx.

Proves: least-loaded lane pick; proven grok/cursor/claude argv in the job file;
DHx marker auto-stamped from datetime.now().astimezone().isoformat() (not a
hand-typed time); collector assignment row; idempotent filename + no double stamp.
Does not invoke grok/cursor/claude and does not write V:\\Ai\\_queue.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUNDLE = HERE.parent
LIVE_COSMOS = Path(r"V:\A\Ai\COSMOS\cosmos")
# Live helpers (kernel/paths) then THIS bundle's dispatch/node_worker first.
if LIVE_COSMOS.exists():
    sys.path.insert(0, str(LIVE_COSMOS))
sys.path.insert(0, str(BUNDLE / "cosmos"))
sys.path.insert(0, str(HERE))

from cosmos_kernel import install
from cosmos_dispatch import (
    DEFAULT_MODEL, GROK_MAX_TURNS, GROK_TIMEOUT_S, CLAUDE_MODEL,
    SONNET_MODEL, HAIKU_MODEL, KIND_LIVE,
    CURSOR_BASE, CODING_DEFAULT_AGENT, RESEARCH_DEFAULT_AGENT,
    DispatchError,
    append_dhx_marker, compose_critique_prompt, dispatch, infer_kind,
    infer_task_class, infer_default_agent, job_filename, job_status,
    measure_lanes, pick_least_loaded, render_job, returns_dir,
    worker_bucket_dir, worker_compat_dir,
)
from cosmos_node_worker import execute_handoff
from cosmos_paths import CosmosPaths

RESULTS = []


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                            # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def _write(p: Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def _setup():
    td = Path(tempfile.mkdtemp(prefix="cosmos_dispatch_"))
    root = install(td / "live", tree_id="spike-dispatch")
    queue = td / "queue"
    for lane, extra in (("root", queue),
                        ("lg", queue / "_lanes" / "lg"),
                        ("pb", queue / "_lanes" / "pb")):
        extra.mkdir(parents=True, exist_ok=True)
        (extra / "running").mkdir(parents=True, exist_ok=True)
        (extra / "done").mkdir(parents=True, exist_ok=True)
    dhx = td / "docs" / "AGENT_BRIEF.md"
    _write(dhx, (
        "# DHx — the DHot box (AGENT BRIEF).\n\n"
        "## Assignment log — APPEND-ONLY markers\n"
        "- 2026-08-25T~20:39-05 · G46 · preexisting · root/old\n\n"
        "## Active assignments\n"
        "- something live\n"
    ))
    cwd = td / "workdir"
    cwd.mkdir()
    return td, root, queue, dhx, cwd


def main() -> int:
    td, root, queue, dhx, cwd = _setup()

    # ---- load accounting (bts_runner semantics) ----
    _write(queue / "heavy_root__t60.py", "print(1)\n")
    _write(queue / "running" / "run_root.py", "print(1)\n")
    _write(queue / "_lanes" / "lg" / "lg_q1__t60.py", "print(1)\n")
    _write(queue / "_lanes" / "lg" / "lg_q2__t60.py", "print(1)\n")
    _write(queue / "_lanes" / "lg" / "running" / "lg_run.py", "print(1)\n")
    # pb empty -> least loaded
    loads = measure_lanes(queue)
    check("root load is queued+running (2)",
          lambda: loads["root"]["load"] == 2)
    check("lg load is 3", lambda: loads["lg"]["load"] == 3)
    check("pb load is 0", lambda: loads["pb"]["load"] == 0)
    check("pick_least_loaded prefers pb (empty)",
          lambda: pick_least_loaded(queue) == "pb")
    _write(queue / "_lanes" / "pb" / "_helper.py", "x\n")
    check("_-prefixed files are not counted as jobs",
          lambda: measure_lanes(queue)["pb"]["load"] == 0)

    t_before = datetime.now().astimezone()
    rec = dispatch(
        "G46", "Reply with the single word PONG. Do not edit files.",
        str(cwd), kind="grok", queue=queue, runtime_root=root, dhx=dhx,
    )
    t_after = datetime.now().astimezone()

    check("dispatch ok", lambda: rec["ok"] is True)
    check("created the job file", lambda: rec["created"] is True)
    check("least-loaded lane was pb", lambda: rec["lane"] == "pb")
    job = Path(rec["job_path"])
    check("job file exists in pb lane root",
          lambda: job.exists() and job.parent == queue / "_lanes" / "pb")
    src = job.read_text(encoding="utf-8")
    check("grok job uses --single", lambda: '"--single"' in src)
    check("grok job uses proven --output-format plain",
          lambda: '"--output-format", "plain"' in src)
    check("grok job uses --always-approve",
          lambda: '"--always-approve"' in src)
    check("grok job uses proven --max-turns 60",
          lambda: f'"--max-turns", "{GROK_MAX_TURNS}"' in src)
    check("grok job uses --cwd", lambda: '"--cwd"' in src)
    check("grok job prepares attempt-private workspace (P10)",
          lambda: "prepare_grok_workspace" in src
          and "workspace_policy" in src
          and "fenced_commit" in src)
    check("grok job --cwd is the clone CWD, not baked live SOURCE",
          lambda: '"--cwd", CWD' in src and "SOURCE =" in src
          and "CWD = str(ws)" in src)
    check("grok job never falls back to live SOURCE as cwd",
          lambda: "NEVER fall back to SOURCE" in src
          and "cwd=CWD" in src)
    check("grok job uses default model grok-4.6",
          lambda: DEFAULT_MODEL in src)
    check("dispatch reports attempt-private workspace policy",
          lambda: rec.get("workspace_policy") == "attempt-private")
    check("grok job files stream/folder/returns",
          lambda: "RETURNS = Path(" in src and "returns" in src)
    check("dispatch reports returns_path under lane/returns",
          lambda: Path(rec["returns_path"]).parent == returns_dir(
              queue / "_lanes" / "pb"))
    st0 = rec["status"]
    check("dispatch status is queued (job sitting in lane root)",
          lambda: st0["state"] == "queued" and st0["lane"] == "pb")
    check("job filename is not helper-prefixed",
          lambda: not rec["job_file"].startswith("_"))
    check("job filename is idempotent for same inputs",
          lambda: rec["job_file"] == job_filename(
              "G46", "grok",
              "Reply with the single word PONG. Do not edit files.",
              str(Path(cwd).resolve()), rec["timeout_s"]))

    # DHx auto-stamp
    dhx_text = dhx.read_text(encoding="utf-8")
    check("DHx contains the auto-stamped marker",
          lambda: rec["marker"] in dhx_text)
    check("DHx marker lives in the Assignment log (before Active assignments)",
          lambda: dhx_text.find(rec["marker"]) < dhx_text.find("## Active assignments"))
    check("stamp is ISO with offset (not a hand-typed ~ time)",
          lambda: "T" in rec["stamp"] and rec["stamp"][-6] in "+-"
          and "~" not in rec["stamp"])
    check("stamp parses as aware datetime in the call window",
          lambda: (lambda s: (
              t_before <= datetime.fromisoformat(s) <= t_after
          ))(rec["stamp"]))
    check("marker format is iso · agent · task · lane/file (protocol grammar)",
          lambda: rec["marker"].startswith(rec["stamp"] + " · G46 · ")
          and rec["marker"].endswith(f"pb/{rec['job_file']}"))
    check("grok kind_live is proven", lambda: rec.get("kind_live") == "proven")

    # collector row
    idx = Path(rec["index"])
    rows = [json.loads(ln) for ln in idx.read_text(encoding="utf-8").splitlines()
            if ln.strip()]
    check("collector index has one assignment row", lambda: len(rows) == 1)
    check("assignment source is dispatch_assignment",
          lambda: rows[0]["source"] == "dispatch_assignment")
    check("assignment status is assigned", lambda: rows[0]["status"] == "assigned")
    check("assignment artifact is the job path",
          lambda: rows[0]["artifact"] == rec["job_path"])
    check("assignment agent is G46", lambda: rows[0]["agent"] == "G46")
    check("assignment schema is cosmos-collector/2",
          lambda: rows[0]["schema"] == "cosmos-collector/2")
    check("assignment row carries returns_path",
          lambda: rows[0].get("returns_path") == rec["returns_path"])

    # idempotent retry
    rec2 = dispatch(
        "G46", "Reply with the single word PONG. Do not edit files.",
        str(cwd), kind="grok", queue=queue, runtime_root=root, dhx=dhx,
    )
    check("second dispatch is idempotent (not created)",
          lambda: rec2["idempotent"] is True and rec2["created"] is False)
    check("second dispatch reuses the same job path",
          lambda: rec2["job_path"] == rec["job_path"])
    dhx2 = dhx.read_text(encoding="utf-8")
    check("second dispatch does not double-stamp DHx",
          lambda: dhx2.count(rec["job_file"]) == 1)
    rows2 = [json.loads(ln) for ln in idx.read_text(encoding="utf-8").splitlines()
             if ln.strip()]
    check("second dispatch does not double-write the index",
          lambda: len(rows2) == 1)

    # explicit lane override
    rec3 = dispatch(
        "G46", "a different task for lane override",
        str(cwd), kind="grok", lane="lg", queue=queue, runtime_root=root,
        dhx=dhx,
    )
    check("explicit --lane lg is honored", lambda: rec3["lane"] == "lg")
    check("lg job landed in _lanes/lg",
          lambda: Path(rec3["job_path"]).parent == queue / "_lanes" / "lg")

    # H6: missing Cursor key is a typed NO_KEY, never a silent drop and
    # never a key chase. kind_live stays UNPROVEN when a dummy key exists
    # so the job source can be pinned without hitting Cloud Agents.
    check("cursor without key is typed NO_KEY (H6, no key chase)",
          lambda: _raises_kind("NO_KEY",
                               lambda: dispatch(
                                   "Cursor",
                                   "Append one line to docs/CURSOR_HARNESS.md and stop.",
                                   str(cwd), kind="cursor", queue=queue,
                                   runtime_root=root, dhx=dhx)))

    # cursor job (needs a key file; dummy, never sent)
    keyp = root / "config" / "cursor_cosmos_key.txt"
    _write(keyp, "crsr_" + ("ab" * 32) + "31ab")
    rec_c = dispatch(
        "Cursor", "Append one line to docs/CURSOR_HARNESS.md and stop.",
        str(cwd), kind="cursor", queue=queue, runtime_root=root, dhx=dhx,
    )
    csrc = Path(rec_c["job_path"]).read_text(encoding="utf-8")
    check("cursor job POSTs /v1/agents", lambda: '"/v1/agents"' in csrc)
    check("cursor job pins Composer 2.5 (Cursor Models, not Other Models Opus)",
          lambda: '"composer-2.5"' in csrc
          and '"claude-opus-5"' not in csrc)
    check("cursor job uses Cloud Agents base", lambda: CURSOR_BASE in csrc)
    check("cursor job reads the key path, does not bake the secret",
          lambda: "cursor_cosmos_key.txt" in csrc
          and "crsr_" not in csrc)
    check("cursor job polls /v1/agents/{id}/runs/{runId}",
          lambda: "/runs/" in csrc and "FINISHED" in csrc)
    check("cursor job uses Basic auth (key:)",
          lambda: "Basic " in csrc and 'key + ":"' in csrc)
    check("cursor kind_live is UNPROVEN",
          lambda: rec_c.get("kind_live") == "UNPROVEN")
    check("cursor job does not take the grok private-clone path",
          lambda: "prepare_grok_workspace" not in csrc)
    check("cursor workspace_policy is not grok-private",
          lambda: rec_c.get("workspace_policy") in (None, ""))

    # claude/F5/SSA — Keith 2026-09-01: Anthropic off the route. No job files.
    check("F5 dispatch is ANTHROPIC_OFF",
          lambda: _raises_kind("ANTHROPIC_OFF",
                               lambda: dispatch(
                                   "F5", "Reply PONG. Do not edit files.",
                                   str(cwd), kind="F5", queue=queue,
                                   runtime_root=root, dhx=dhx)))
    check("sonnet dispatch is ANTHROPIC_OFF",
          lambda: _raises_kind("ANTHROPIC_OFF",
                               lambda: dispatch(
                                   "sonnet", "RESEARCH the reachable Claude tiers.",
                                   str(cwd), queue=queue, runtime_root=root,
                                   dhx=dhx)))
    check("haiku dispatch is ANTHROPIC_OFF",
          lambda: _raises_kind("ANTHROPIC_OFF",
                               lambda: dispatch(
                                   "haiku", "Summarize the DHx standing rules.",
                                   str(cwd), queue=queue, runtime_root=root,
                                   dhx=dhx)))
    rec_ssa = dispatch(
        "SSA", "Vet the dispatch alias table.",
        str(cwd), queue=queue, runtime_root=root, dhx=dhx)
    ssa_src = Path(rec_ssa["job_path"]).read_text(encoding="utf-8")
    check("SSA dispatch remaps to groq (not ANTHROPIC_OFF)",
          lambda: rec_ssa.get("kind") == "groq"
          and rec_ssa.get("kind_live") == "adapter"
          and rec_ssa.get("model") == "openai/gpt-oss-20b")
    check("SSA/groq job calls groq-api gpt-oss-20b, not claude CLI",
          lambda: "gpt-oss-20b" in ssa_src
          and "GroqRail" in ssa_src
          and "--permission-mode" not in ssa_src
          and "gsk_" not in ssa_src)
    rec_omit = dispatch(
        "", "RESEARCH how the collector indexes returns.",
        str(cwd), queue=queue, runtime_root=root, dhx=dhx,
    )
    check("omitted agent on research task defaults to G46 (Anthropic off)",
          lambda: rec_omit["agent"] == "G46" and rec_omit["kind"] == "grok"
          and rec_omit.get("model") == DEFAULT_MODEL)
    rec_omit_c = dispatch(
        "", "implement a py_compile gate for dispatch.",
        str(cwd), queue=queue, runtime_root=root, dhx=dhx,
    )
    check("omitted agent on coding task defaults to G46/grok",
          lambda: rec_omit_c["agent"] == "G46" and rec_omit_c["kind"] == "grok"
          and rec_omit_c.get("model") == DEFAULT_MODEL)

    # auto-route by agent TYPE (kind omitted)
    rec_auto = dispatch(
        "G46", "auto-route grok from G46 type",
        str(cwd), queue=queue, runtime_root=root, dhx=dhx,
    )
    check("G46 without kind infers grok",
          lambda: rec_auto["kind"] == "grok" and rec_auto["kind_inferred"] is True)
    check("infer_kind(G46) is grok", lambda: infer_kind("G46") == "grok")
    check("infer_kind(Cursor) is cursor", lambda: infer_kind("Cursor") == "cursor")
    check("infer_kind(F5) is claude", lambda: infer_kind("F5") == "claude")
    check("infer_kind(GW) is grok", lambda: infer_kind("GW") == "grok")
    check("infer_kind(SGH) is grok", lambda: infer_kind("SGH") == "grok")
    check("infer_kind(GEM) is gem", lambda: infer_kind("GEM") == "gem")
    check("infer_kind(OAi) is oa", lambda: infer_kind("OAi") == "oa")
    check("infer_kind(SSA) is groq", lambda: infer_kind("SSA") == "groq")
    check("infer_kind(sonnet) is sonnet", lambda: infer_kind("sonnet") == "sonnet")
    check("infer_kind(haiku) is haiku", lambda: infer_kind("haiku") == "haiku")
    check("infer_kind(Sonnet SubAgent) is groq",
          lambda: infer_kind("Sonnet SubAgent") == "groq")
    check("infer_kind(groq) is groq", lambda: infer_kind("groq") == "groq")
    check("infer_kind(gemma) is openrouter",
          lambda: infer_kind("gemma") == "openrouter")
    rec_or = dispatch(
        "Gemma", "Explain REST in one sentence.",
        str(cwd), queue=queue, runtime_root=root, dhx=dhx)
    or_src = Path(rec_or["job_path"]).read_text(encoding="utf-8")
    check("Gemma dispatch is openrouter named Gemma 4, not rotator",
          lambda: rec_or.get("kind") == "openrouter"
          and rec_or.get("model") == "google/gemma-4-26b-a4b-it:free"
          and "OpenRouterRail" in or_src
          and "google/gemma-4-26b-a4b-it:free" in or_src
          and "sk-or-" not in or_src)
    check("coding default agent is G46",
          lambda: infer_default_agent("implement the runner pool") == "G46"
          and infer_task_class("implement the runner pool") == "coding"
          and CODING_DEFAULT_AGENT == "G46")
    check("research default agent is G46 (Anthropic off; was SSA)",
          lambda: infer_default_agent("RESEARCH present-day model access") == "G46"
          and infer_task_class("RESEARCH present-day model access") == "research"
          and RESEARCH_DEFAULT_AGENT == "G46")
    check("coding wins over research tokens (never Sonnet)",
          lambda: infer_default_agent(
              "implement the research collector") == "G46")
    check("ambiguous task stays coding/Grok",
          lambda: infer_default_agent("Reply with the single word PONG.") == "G46")
    rec_auto_c = dispatch(
        "Cursor", "auto-route cursor from Cursor type",
        str(cwd), queue=queue, runtime_root=root, dhx=dhx,
    )
    check("Cursor without kind infers cursor",
          lambda: rec_auto_c["kind"] == "cursor" and rec_auto_c["kind_inferred"] is True)
    check("F5 without kind still infers claude identity, then refuses the call",
          lambda: infer_kind("F5") == "claude"
          and _raises_kind("ANTHROPIC_OFF",
                           lambda: dispatch(
                               "F5", "auto-route claude from F5 type",
                               str(cwd), queue=queue, runtime_root=root,
                               dhx=dhx)))

    # monitor: move the auto grok job into running/ and read status
    auto_job = Path(rec_auto["job_path"])
    running = auto_job.parent / "running" / auto_job.name
    auto_job.replace(running)
    st_run = job_status(auto_job.name, queue=queue, runtime_root=root)
    check("job_status sees running after move into running/",
          lambda: st_run["state"] == "running")
    done = auto_job.parent / "done" / auto_job.name
    running.replace(done)
    st_done = job_status(auto_job.name, queue=queue, runtime_root=root)
    check("job_status sees done after move into done/",
          lambda: st_done["state"] == "done" and st_done["terminal"] is True)

    # refusals
    check("empty task is BAD_INPUT",
          lambda: _raises_kind("BAD_INPUT",
                               lambda: dispatch("G46", "  ", str(cwd),
                                                queue=queue, runtime_root=root,
                                                dhx=dhx)))
    check("missing dir is NO_DIR",
          lambda: _raises_kind("NO_DIR",
                               lambda: dispatch("G46", "x", str(cwd / "nope"),
                                                queue=queue, runtime_root=root,
                                                dhx=dhx)))
    check("unknown kind is BAD_INPUT",
          lambda: _raises_kind("BAD_INPUT",
                               lambda: dispatch("G46", "x", str(cwd),
                                                kind="nope", queue=queue,
                                                runtime_root=root, dhx=dhx)))
    check("unknown agent type without kind is BAD_INPUT",
          lambda: _raises_kind("BAD_INPUT",
                               lambda: dispatch("NotAMaker", "x", str(cwd),
                                                queue=queue, runtime_root=root,
                                                dhx=dhx)))
    check("unknown lane is NO_LANE",
          lambda: _raises_kind("NO_LANE",
                               lambda: dispatch("G46", "x", str(cwd),
                                                lane="zz", queue=queue,
                                                runtime_root=root, dhx=dhx)))
    check("missing queue is NO_QUEUE",
          lambda: _raises_kind("NO_QUEUE",
                               lambda: dispatch("G46", "x", str(cwd),
                                                queue=str(td / "no_such_queue"),
                                                runtime_root=root, dhx=dhx)))

    # ---- HIGH/MED additive: default dir, native queue, leftover result, no drive literal
    rec_dd = dispatch(
        "G46", "default dir from install repo tree",
        queue=queue, runtime_root=root, dhx=dhx,
    )
    check("omitted --dir defaults to repo tree (parent of live)",
          lambda: Path(rec_dd["target_dir"]) == td)
    check("grok except path sets rc=2 (L1)",
          lambda: 'out["rc"] = 2' in src)

    leftover = Path(rec["result_path"])
    _write(leftover, json.dumps({"rc": 0, "leftover": True}))
    os.utime(leftover, (time.time() - 3600, time.time() - 3600))
    st_stale = job_status(rec["job_file"], queue=queue, runtime_root=root)
    check("M5 leftover older result is not terminal while queued",
          lambda: st_stale["terminal"] is False and st_stale["state"] == "queued")
    leftover.unlink()

    rec_n = dispatch(
        "G46", "native queue identity gate",
        str(cwd), runtime_root=root, dhx=dhx,
    )
    man = root / "queue" / "manifests" / (str(rec_n.get("native_job_id")) + ".json")
    check("native default queue is the resolver queue role",
          lambda: rec_n.get("queue_identity") == "native"
          and Path(rec_n["queue"]) == root / "queue")
    check("native dispatch submitted an immutable manifest",
          lambda: rec_n.get("native_job_id") and man.exists())
    check("native job script sits under tools/dispatch_jobs (runner confine)",
          lambda: Path(rec_n["job_path"]).parent == root / "cosmos" / "dispatch_jobs")
    check("native returns path is queue/returns/<stream>/ (R9 locked)",
          lambda: Path(rec_n["returns_path"]).parent == root / "queue" / "returns" / "cm")
    check("native marker uses protocol · grammar",
          lambda: " · " in rec_n["marker"] and rec_n["marker"].endswith(
              f"cm/{rec_n['job_file']}"))
    check("native job path is under this install, not a foreign queue",
          lambda: str(Path(rec_n["job_path"]).resolve()).startswith(
              str(root.resolve())))

    mod = Path(__file__).resolve().parent.parent / "cosmos" / "cosmos_dispatch.py"
    src_mod = mod.read_text(encoding="utf-8")
    check("module has no BTS drive-literal default (H1)",
          lambda: "V:\\Ai\\_queue" not in src_mod and "V:/Ai/_queue" not in src_mod)
    check("re-export: render_job off cosmos_dispatch is cosmos_dispatch_jobs",
          lambda: render_job.__module__ == "cosmos_dispatch_jobs")
    check("re-export: dispatch source no longer defines _grok_job",
          lambda: "def _grok_job" not in src_mod
          and "from cosmos_dispatch_jobs import" in src_mod)
    check("re-export: compose_critique_prompt off cosmos_dispatch is cosmos_dispatch_critique",
          lambda: compose_critique_prompt.__module__ == "cosmos_dispatch_critique")
    check("re-export: dispatch source no longer defines compose_critique_prompt",
          lambda: "def compose_critique_prompt" not in src_mod
          and "from cosmos_dispatch_critique import" in src_mod)
    check("re-export: measure_lanes off cosmos_dispatch is cosmos_dispatch_lanes",
          lambda: measure_lanes.__module__ == "cosmos_dispatch_lanes")
    check("re-export: dispatch source no longer defines measure_lanes",
          lambda: "def measure_lanes" not in src_mod
          and "from cosmos_dispatch_lanes import" in src_mod)
    check("re-export: append_dhx_marker off cosmos_dispatch is cosmos_dispatch_stamps",
          lambda: append_dhx_marker.__module__ == "cosmos_dispatch_stamps")
    check("re-export: dispatch source no longer defines append_dhx_marker",
          lambda: "def append_dhx_marker" not in src_mod
          and "from cosmos_dispatch_stamps import" in src_mod)

    # F-29 / F-39: test_dispatch.py is the caller suite F-39 cuts actually run.
    # The stamps/jobs split kept this suite green while test_work_order.py
    # went red (cursor lane grep of dispatch.py alone). Pin the work-order
    # assertion and the family follow so the next cut cannot drop either.
    wo_run = Path(__file__).resolve().parent.parent / "cosmos" / "cosmos_work_order_run.py"
    wo_src = wo_run.read_text(encoding="utf-8") if wo_run.is_file() else ""
    jobs_mod = Path(__file__).resolve().parent.parent / "cosmos" / "cosmos_dispatch_jobs.py"
    jobs_src = jobs_mod.read_text(encoding="utf-8") if jobs_mod.is_file() else ""
    family = src_mod + "\n" + jobs_src
    check("F-29 caller: work-order still asserts dispatch cursor lane",
          lambda: "existing dispatch cursor lane still present" in wo_src
          and "api.cursor.com" in wo_src
          and "autoCreatePR" in wo_src)
    check("F-29 caller: work-order cursor-lane grep follows the dispatch family",
          lambda: "_dispatch_family_text" in wo_src
          and "cosmos_dispatch_jobs.py" in wo_src)
    check("F-29 caller: work-order family scan follows from cosmos_dispatch_* import",
          lambda: r"from (cosmos_dispatch_\w+) import" in wo_src
          or "cosmos_dispatch_\\w+" in wo_src)
    check("F-29 caller: dispatch family still carries api.cursor.com + autoCreatePR",
          lambda: "api.cursor.com" in family and "autoCreatePR" in family)

    # The P10 attempt-private workspace rows moved with their code to
    # tests/test_dispatch_workspace.py (PHASE 4 seam). What stays here is the
    # dispatch harness: lanes, job source, DHx stamp, collector index, refusals.

    # HIGH (critique-rail): gem/oa identity is live/buckets/<node>, timeout
    # is model-length, and the job SOURCE calls execute_handoff (spawn the
    # rail) rather than packet-and-exit SystemExit(0). The prior
    # diff_tests.patch hunk header was corrupt; these asserts are the
    # full-file re-emit. Isolated execute_handoff uses a fake rail — no
    # live spend.
    rec_gem = dispatch(
        "GEM", "Reply with the single word PONG. Do not edit files.",
        str(cwd), queue=queue, runtime_root=root, dhx=dhx,
    )
    gsrc = Path(rec_gem["job_path"]).read_text(encoding="utf-8")
    paths_live = CosmosPaths(root)
    check("GEM kind is gem", lambda: rec_gem["kind"] == "gem")
    check("GEM timeout is model-length not 120s stub",
          lambda: rec_gem["timeout_s"] == GROK_TIMEOUT_S)
    check("GEM worker_bucket is resolver live/buckets/gem",
          lambda: rec_gem.get("worker_bucket") == str(worker_bucket_dir(paths_live, "gem"))
          and Path(rec_gem["worker_bucket"]).as_posix().endswith("buckets/gem"))
    check("GEM compat copy path is state/dispatch/workers/gem (kept)",
          lambda: rec_gem.get("worker_compat") == str(worker_compat_dir(paths_live, "gem")))
    check("GEM job calls execute_handoff (not packet-and-exit)",
          lambda: "execute_handoff" in gsrc
          and "raise SystemExit(0 if out.get(\"done\") else 2)" in gsrc)
    check("GEM job does not fake-DONE on packet write",
          lambda: "kind_live\": \"handoff\"" in gsrc
          and "worker_packet" not in gsrc.split("execute_handoff")[0])
    rec_oa = dispatch(
        "OAi", "Reply with the single word PONG. Do not edit files.",
        str(cwd), queue=queue, runtime_root=root, dhx=dhx,
    )
    osrc = Path(rec_oa["job_path"]).read_text(encoding="utf-8")
    check("OA kind is oa", lambda: rec_oa["kind"] == "oa")
    check("OA timeout is model-length",
          lambda: rec_oa["timeout_s"] == GROK_TIMEOUT_S)
    check("OA job calls execute_handoff",
          lambda: "execute_handoff" in osrc
          and "raise SystemExit(0 if out.get(\"done\") else 2)" in osrc)
    check("OAi worker_bucket is live/buckets/oa",
          lambda: Path(rec_oa["worker_bucket"]).as_posix().endswith("buckets/oa"))

    def _fake_gem(prompt: str) -> dict:
        return {"ok": True, "kind": "API", "text": "PONG",
                "usd": 0.01, "node": "fake_gem", "model": "fake-gemini",
                "link_id": "gem-api"}

    def _fake_oa(prompt: str) -> dict:
        return {"ok": True, "kind": "API", "text": "PONG-OA",
                "usd": 0.01, "node": "fake_oa", "model": "fake-oa",
                "link_id": "oa-api"}

    gem_result = paths_live.root / "queue" / "returns" / "cm" / "gem_handoff_result.json"
    grec2 = execute_handoff(
        str(root), "gem", "GEM", "Reply PONG.", str(gem_result),
        rail_call=_fake_gem, dhx_path=dhx)
    check("GEM execute_handoff done binds nonempty stdout",
          lambda: grec2.get("done") is True
          and "PONG" in (grec2.get("stdout_tail") or "")
          and Path(grec2["stdout_full"]).stat().st_size > 0)
    check("GEM execute_handoff packet is live/buckets/gem (processed)",
          lambda: "buckets" in str(grec2.get("worker_packet") or "").replace("\\", "/")
          and "/gem/" in str(grec2.get("worker_packet") or "").replace("\\", "/"))
    check("GEM result bound to gem-api",
          lambda: (grec2.get("rail") or {}).get("link_id") == "gem-api")

    oa_result = paths_live.root / "queue" / "returns" / "cm" / "oa_handoff_result.json"
    orec = execute_handoff(
        str(root), "oa", "OAi", "Reply PONG.", str(oa_result),
        rail_call=_fake_oa, dhx_path=dhx)
    check("OA execute_handoff emits nonempty stdout",
          lambda: orec.get("done") is True
          and "PONG-OA" in (orec.get("stdout_tail") or "")
          and Path(orec["stdout_full"]).stat().st_size > 0)
    check("OA result bound to oa-api",
          lambda: (orec.get("rail") or {}).get("link_id") == "oa-api")
    check("OA execute_handoff packet is live/buckets/oa",
          lambda: "buckets" in str(orec.get("worker_packet") or "").replace("\\", "/")
          and "/oa/" in str(orec.get("worker_packet") or "").replace("\\", "/"))

    def _empty_gem(prompt: str) -> dict:
        return {"ok": True, "kind": "API", "text": "",
                "usd": 0.0, "node": "fake_gem", "model": "fake-gemini",
                "link_id": "gem-api"}

    empty_p = paths_live.root / "queue" / "returns" / "cm" / "gem_empty_result.json"
    erec = execute_handoff(
        str(root), "gem", "GEM", "Reply PONG.", str(empty_p),
        rail_call=_empty_gem, dhx_path=dhx)
    check("empty rail text is NOT fake-DONE (rc=2, done=False)",
          lambda: erec.get("done") is False and erec.get("rc") == 2
          and erec.get("done_why") == "empty_stdout")

    # ONE row: critic-visibility. Fake _propose set -> prompt body is
    # byte-identical to the source files and sha256 matches disk.
    propose = td / "crit_tree" / "_propose"
    src_a = b"def alpha():\n    return 'A-body-unique-9173'\n"
    src_b = b"beta = 42  # B-body-unique-4801\n"
    _write(propose / "BIND.json", json.dumps({
        "schema": "cosmos-p10-bind/1",
        "files": [
            {"target_path": "mod_a.py",
             "sha256": hashlib.sha256(src_a).hexdigest()},
            {"target_path": "pkg/mod_b.py",
             "sha256": hashlib.sha256(src_b).hexdigest()},
        ],
    }, indent=1))
    (propose / "mod_a.py").write_bytes(src_a)
    (propose / "pkg").mkdir(parents=True, exist_ok=True)
    (propose / "pkg" / "mod_b.py").write_bytes(src_b)
    assignment = (
        "STAGE-5 different-family critique of the disposed _propose artifacts "
        "mod_a.py and pkg/mod_b.py. Verify the bodies.")
    built = compose_critique_prompt(assignment, propose_dir=propose,
                                    tree=td / "crit_tree")
    sha_a = hashlib.sha256(src_a).hexdigest()
    sha_b = hashlib.sha256(src_b).hexdigest()
    text_a, text_b = src_a.decode("utf-8"), src_b.decode("utf-8")
    prompt = built.get("prompt") or ""
    recs = {r["path"]: r for r in (built.get("files") or [])}
    print("ROW critique-inline body actual_a="
          + repr(text_a if text_a in prompt else prompt[prompt.find("mod_a.py"):prompt.find("mod_a.py")+80])
          + " expected_a=" + repr(text_a))
    print("ROW critique-inline body actual_b="
          + repr(text_b if text_b in prompt else "MISSING")
          + " expected_b=" + repr(text_b))
    print("ROW critique-inline sha256 actual_a="
          + str((recs.get("mod_a.py") or {}).get("sha256"))
          + " expected_a=" + sha_a)
    print("ROW critique-inline sha256 actual_b="
          + str((recs.get("pkg/mod_b.py") or {}).get("sha256"))
          + " expected_b=" + sha_b)
    rec_oa_c = dispatch(
        "OA", assignment, str(td / "crit_tree"), queue=queue,
        runtime_root=root, dhx=dhx)
    oa_src = Path(rec_oa_c["job_path"]).read_text(encoding="utf-8")
    # Job source JSON-escapes the prompt; unique body tokens + sha256 survive.
    print("ROW critique-job payload sha256_in_job="
          + str(sha_a in oa_src and sha_b in oa_src)
          + " body_in_job=" + str(
              "A-body-unique-9173" in oa_src and "B-body-unique-4801" in oa_src))

    def _critic_row():
        disk_a = (propose / "mod_a.py").read_bytes()
        disk_b = (propose / "pkg" / "mod_b.py").read_bytes()
        ok = (
            built.get("inlined") is True
            and text_a in prompt and text_b in prompt
            and text_a == disk_a.decode("utf-8")
            and text_b == disk_b.decode("utf-8")
            and (recs.get("mod_a.py") or {}).get("sha256") == sha_a
            and (recs.get("pkg/mod_b.py") or {}).get("sha256") == sha_b
            and f"sha256={sha_a}" in prompt
            and f"sha256={sha_b}" in prompt
            and "A-body-unique-9173" in oa_src
            and "B-body-unique-4801" in oa_src
            and f"sha256={sha_a}" in oa_src
            and sha_a == hashlib.sha256(disk_a).hexdigest()
            and sha_b == hashlib.sha256(disk_b).hexdigest()
        )
        if not ok:
            print("ROW critique-inline FAIL built=" + json.dumps(
                {k: built.get(k) for k in ("inlined", "files")}, default=str))
        return ok

    check("critique builder inlines body byte-identical + sha256 matches disk",
          _critic_row)

    h6 = {
        "ok": True,
        "cursor_missing_key": "NO_KEY",
        "cursor_kind_live": rec_c.get("kind_live"),
        "claude_kind_live": KIND_LIVE.get("claude"),
        "sonnet_kind_live": KIND_LIVE.get("sonnet"),
        "ssa_kind_live": KIND_LIVE.get("ssa"),
        "note": "H6: Anthropic off 2026-09-01. claude-family KIND_LIVE is "
                "ANTHROPIC_OFF. cursor stays UNPROVEN. Missing Cursor key is "
                "typed NO_KEY. No key chase. No claude -p.",
    }
    h6["ok"] = (h6["cursor_kind_live"] == "UNPROVEN"
                and h6["claude_kind_live"] == "ANTHROPIC_OFF")
    (BUNDLE / "cosmos" / "_f69_h6.json").write_text(
        json.dumps(h6, indent=2) + "\n", encoding="utf-8")
    check("H6 artifact names claude ANTHROPIC_OFF and cursor UNPROVEN/NO_KEY",
          lambda: h6["ok"] is True
          and h6["cursor_missing_key"] == "NO_KEY")

    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for l, ok, e in RESULTS:
        print(("  OK  " if ok else "  FAIL") + f" {l}" + (f"  {e}" if e else ""))
    print(f"{len(RESULTS) - len(bad)}/{len(RESULTS)} passed")
    return 1 if bad else 0


def _raises_kind(kind, fn) -> bool:
    try:
        fn()
    except DispatchError as e:
        return e.kind == kind
    return False


def test_dispatch():
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
