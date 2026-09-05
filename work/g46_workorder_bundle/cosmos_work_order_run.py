#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_work_order_run - native Windows poller for typed work orders.

The OS runs the machine. This clock picks up a DROPPED order, creates the
named agent (Family|Clade|Version -> rail), runs it WRITE-PRIVATE (cwd is
the attempt-private workspace, never the live tree), and files DONE in
assigned-tasks. COMPLETED is a separate COW step (--accept / accept_order).

    py -3.14 cosmos\\cosmos_work_order_run.py --root V:\\A\\Ai\\COSMOS\\live --once
    py -3.14 cosmos\\cosmos_work_order_run.py --root ... --loop
    py -3.14 cosmos\\cosmos_work_order_run.py --root ... --standup
    py -3.14 cosmos\\cosmos_work_order_run.py --root ... --status
    py -3.14 cosmos\\cosmos_work_order_run.py --root ... --accept <order_id>
    py -3.14 cosmos\\cosmos_work_order_run.py --root ... --reject <order_id>
    py -3.14 cosmos\\cosmos_work_order_run.py --selftest

--loop honors live/state/control/PAUSE.flag (idle, heartbeat state=PAUSED).
--once is a commanded drain even while paused.

Does not modify kernel / ledger / sched / service. No bts_* import.
Does not edit cosmos_dispatch.py grok/claude/cursor job templates.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
for _cand in (HERE, HERE.parent.parent / "cosmos", HERE.parent / "cosmos"):
    if (_cand / "cosmos_paths.py").is_file() and str(_cand) not in sys.path:
        sys.path.append(str(_cand))

from cosmos_clock import (  # noqa: E402
    acquire_lock, create_task, heartbeat_age_s, pid_alive, pythonw_exe,
    query_task, read_heartbeat, spawn_detached, tr_cmdline, wait_fresh,
    write_heartbeat,
)
from cosmos_paths import CosmosPaths, CosmosPathError, write_sentinel  # noqa: E402
from cosmos_work_order import (  # noqa: E402
    OrderError, SPEC_FIELDS, accept_order, build_argv, compose_prompt,
    drop_order, file_done, infer_repo_tree, parse_agent,
    parse_context_source, parse_order, parse_output, pickup_order,
    reject_order, route_agent, work_order_dirs,
)
from cosmos_workspace import (  # noqa: E402
    WorkspaceError, order_workspace, refuse_tree_cwd,
)

WORKER = "cosmos-work-order"
TASK_NAME = "COSMOS Work-Order Runner"
TASK_NAME_LOGON = "COSMOS Work-Order Runner Logon"
HEARTBEAT_NAME = "work_order_runner_heartbeat.json"
LOCK_NAME = "work_order_runner.lock"
SCHEMA = "cosmos-work-order-run/1"
DEFAULT_INTERVAL_S = 15.0
FRESH_S = 90.0
DEFAULT_TIMEOUT_S = 1800.0
CREATE_NO_WINDOW = 0x08000000 if os.name == "nt" else 0


def pause_flag(paths: CosmosPaths) -> dict | None:
    """Presence of live/state/control/PAUSE.flag is the whole signal."""
    p = paths.state("control", "PAUSE.flag")
    if not p.exists() or not p.is_file():
        return None
    rec: dict = {"path": str(p), "state": "PAUSED"}
    try:
        raw = p.read_text(encoding="utf-8").strip()
    except OSError as e:
        rec["read_error"] = str(e)
        return rec
    if raw.startswith("{"):
        try:
            obj = json.loads(raw)
        except ValueError:
            obj = None
        if isinstance(obj, dict):
            rec.update(obj)
            rec.setdefault("state", "PAUSED")
            rec["path"] = str(p)
            return rec
    rec["reason"] = raw[:240] or "(empty flag file)"
    return rec


def list_drops(dirs: dict) -> list[Path]:
    bucket = dirs["bucket"]
    if not bucket.is_dir():
        return []
    out = []
    for p in sorted(bucket.iterdir(), key=lambda x: x.name):
        if p.is_file() and p.suffix.lower() == ".json" and not p.name.startswith("_"):
            out.append(p)
    return out


def _real_run(argv: list, *, cwd: Path | str, timeout_s: float) -> dict:
    t0 = time.time()
    try:
        p = subprocess.run(
            argv, capture_output=True, text=True, encoding="utf-8",
            errors="replace", cwd=str(cwd), timeout=float(timeout_s),
            shell=False,
            creationflags=CREATE_NO_WINDOW)
        return {
            "rc": p.returncode,
            "out": (p.stdout or "")[:4000],
            "err": (p.stderr or "")[:1500],
            "timed_out": False,
            "elapsed_s": round(time.time() - t0, 3),
        }
    except subprocess.TimeoutExpired as e:
        return {
            "rc": None,
            "out": (e.stdout or "")[:4000] if isinstance(e.stdout, str) else "",
            "err": (e.stderr or str(e))[:1500] if e.stderr or True else "",
            "timed_out": True,
            "elapsed_s": round(time.time() - t0, 3),
        }
    except FileNotFoundError as e:
        return {"rc": -1, "out": "", "err": str(e), "timed_out": False,
                "elapsed_s": round(time.time() - t0, 3)}
    except Exception as e:  # noqa: BLE001
        return {"rc": -1, "out": "", "err": f"{type(e).__name__}: {e}",
                "timed_out": False, "elapsed_s": round(time.time() - t0, 3)}


def _invoke(rec: dict, argv: list, workspace: Path, prompt: str,
            timeout_s: float) -> dict:
    """Live rail. Codex prefers CodexRail.coder (workspace= + skip_clone)."""
    routed = route_agent(rec["_agent"])
    if routed["rail"] == "codex":
        try:
            from cosmos_codex_rail import CodexRail, key_path_for
            from cosmos_paths import CosmosPaths as _P
            live = Path(rec.get("_live_root") or workspace).resolve()
            # live_root is the runtime root, not the workspace
            root = None
            try:
                # walk up to a sentinel
                cur = Path(workspace)
                for _ in range(6):
                    if (cur / ".cosmos-root.json").is_file():
                        root = cur
                        break
                    cur = cur.parent
            except OSError:
                root = None
            if root is not None:
                paths = _P(root)
                keyp = key_path_for(paths)
                rail = CodexRail(keyp, live_root=root)
                crec = rail.coder({
                    "prompt": prompt,
                    "workspace": str(workspace),
                    "skip_clone": True,
                    "model": routed.get("model"),
                    "timeout_s": timeout_s,
                })
                return {
                    "rc": crec.get("rc"),
                    "out": (crec.get("last_message") or "")[:4000],
                    "err": (crec.get("detail") or "")[:1500],
                    "timed_out": bool(crec.get("timed_out")),
                    "elapsed_s": crec.get("elapsed_s"),
                    "codex": {
                        "done": crec.get("done"),
                        "model": crec.get("model"),
                        "workspace": crec.get("workspace"),
                    },
                }
        except Exception as e:  # noqa: BLE001
            return _real_run(argv, cwd=workspace, timeout_s=timeout_s) | {
                "codex_fallback": f"{type(e).__name__}: {e}",
            }
    return _real_run(argv, cwd=workspace, timeout_s=timeout_s)


def _fail_drop(paths, drop: Path, kind: str, detail: str) -> dict:
    dirs = work_order_dirs(paths)
    try:
        raw = json.loads(Path(drop).read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raw = {"raw": raw}
    except (OSError, ValueError):
        raw = {}
    oid = str(raw.get("order_id") or drop.stem)
    rec = dict(raw)
    rec["order_id"] = oid
    rec["state"] = "FAILED"
    rec["fail_kind"] = kind
    rec["fail_detail"] = detail
    dest = dirs["failed"] / f"{oid}.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_name(dest.name + ".tmp")
    tmp.write_text(json.dumps(rec, indent=1, default=str), encoding="utf-8")
    tmp.replace(dest)
    try:
        Path(drop).unlink()
    except OSError:
        pass
    return rec


def process_one(paths, drop: Path, *, run_fn=None, repo_tree=None,
                timeout_s: float = DEFAULT_TIMEOUT_S) -> dict:
    repo = Path(repo_tree) if repo_tree is not None else infer_repo_tree(paths.root)
    try:
        rec = pickup_order(paths, drop, repo_tree=repo, live_root=paths.root)
    except (OrderError, WorkspaceError) as e:
        return _fail_drop(paths, drop, e.kind, e.detail)
    except Exception as e:  # noqa: BLE001
        return _fail_drop(paths, drop, "BROKE", f"{type(e).__name__}: {e}")
    ws = Path(rec["_workspace"])
    outp = Path(rec["_output_path"])
    refuse_tree_cwd(ws, paths.root, repo_tree=repo)
    prompt = compose_prompt(rec, workspace=ws, output=outp)
    argv = build_argv(rec, ws, prompt=prompt, output=outp)
    rec["_argv"] = argv
    rec["_prompt"] = prompt
    rec["_live_root"] = str(paths.root)
    t0 = time.time()
    if run_fn is not None:
        run = run_fn(argv, cwd=str(ws), output=outp)
        if not isinstance(run, dict):
            run = {"rc": -1, "err": "run_fn did not return a dict"}
    else:
        run = _invoke(rec, argv, ws, prompt, timeout_s)
    run["argv"] = argv
    run["cwd"] = str(ws)
    run.setdefault("elapsed_s", round(time.time() - t0, 3))
    return file_done(paths, rec, run_rec=run)


def poll_once(root: str, polls: int = 0, interval_s: float | None = None,
              *, drain: bool = True, run_fn=None, repo_tree=None,
              timeout_s: float = DEFAULT_TIMEOUT_S) -> dict:
    """One tick. Heartbeat always. PAUSE + drain=False picks up nothing.

    --loop passes drain=False when paused. --once always drains (commanded).
    """
    paths = CosmosPaths(root)
    dirs = work_order_dirs(paths)
    interval = (interval_s if interval_s is not None else DEFAULT_INTERVAL_S)
    hb_path = paths.logs(HEARTBEAT_NAME)
    paused = pause_flag(paths)
    extra = {
        "schema": SCHEMA,
        "tick": "poll",
        "state": "RUNNING",
        "pause_present": paused is not None,
        "bucket": str(dirs["bucket"]),
        "assigned": str(dirs["assigned"]),
        "tree_id": paths.sentinel.tree_id,
        "dropped_this_tick": 0,
        "jobs": [],
    }
    if paused is not None and str(paused.get("state", "PAUSED")).upper() != "RUNNING":
        extra["state"] = "PAUSED"
        extra["tick"] = "paused"
        extra["mode"] = str(paused.get("mode") or "hold")
        extra["auto_resume_at"] = paused.get("auto_resume_at")
        extra["pause"] = {
            "reason": paused.get("reason"),
            "set_by": paused.get("set_by"),
            "set_at": paused.get("set_at"),
            "path": paused.get("path"),
        }
        if not drain:
            hb = write_heartbeat(hb_path, WORKER, extra=extra, polls=polls,
                                 interval_s=interval)
            extra["ok"] = True
            extra["heartbeat"] = hb
            extra["heartbeat_path"] = str(hb_path)
            return extra
        extra["tick"] = "once_while_paused"

    jobs = []
    errors = []
    if drain:
        drops = list_drops(dirs)
        extra["drops_seen"] = len(drops)
        extra["drop_names"] = [p.name for p in drops]
        for dp in drops:
            try:
                rec = process_one(
                    paths, dp, run_fn=run_fn, repo_tree=repo_tree,
                    timeout_s=timeout_s)
                jobs.append({
                    "ok": rec.get("state") == "DONE",
                    "order_id": rec.get("order_id"),
                    "state": rec.get("state"),
                    "workspace": rec.get("_workspace"),
                    "output": rec.get("_output_path"),
                    "observed_rc": rec.get("observed_rc"),
                })
            except Exception as e:  # noqa: BLE001
                errors.append({"drop": str(dp),
                               "kind": type(e).__name__, "error": str(e)})
    extra["dropped_this_tick"] = len(jobs)
    extra["jobs"] = jobs
    extra["errors"] = errors
    extra["tick"] = extra.get("tick") if extra.get("tick") != "poll" else (
        "drained" if jobs else "idle")
    extra["ok"] = not errors
    hb = write_heartbeat(hb_path, WORKER, extra=extra, polls=polls,
                         interval_s=interval)
    extra["heartbeat"] = hb
    extra["heartbeat_path"] = str(hb_path)
    return extra


def loop(root: str, interval_s: float) -> int:
    paths = CosmosPaths(root)
    out_path = paths.logs("work_order_runner.out")
    err_path = paths.logs("work_order_runner.err")
    lock_path = paths.logs(LOCK_NAME)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    log_fh = open(out_path, "a", encoding="utf-8", buffering=1)
    sys.stdout = log_fh
    sys.stderr = log_fh
    fd = acquire_lock(lock_path)
    if fd is None:
        rec = read_heartbeat(paths.logs(HEARTBEAT_NAME))
        age = heartbeat_age_s(rec)
        pid = (rec or {}).get("pid")
        if age is not None and age < FRESH_S and pid_alive(int(pid or 0)):
            print(json.dumps({"already_running": True, "pid": pid,
                              "age_s": round(age, 3)}), flush=True)
            return 0
        print("work-order runner lock held and heartbeat not fresh - refusing",
              flush=True)
        return 2
    polls = 0
    print(json.dumps({"loop": True, "pid": os.getpid(),
                      "interval_s": interval_s}, indent=1), flush=True)
    try:
        while True:
            polls += 1
            paused = pause_flag(paths)
            drain = not (paused is not None
                         and str(paused.get("state", "PAUSED")).upper()
                         != "RUNNING")
            try:
                poll_once(root, polls=polls, interval_s=interval_s,
                          drain=drain)
            except Exception:
                import traceback
                tb = traceback.format_exc()
                try:
                    err_path.write_text(tb, encoding="utf-8")
                except OSError:
                    pass
                try:
                    write_heartbeat(paths.logs(HEARTBEAT_NAME), WORKER,
                                    extra={"tick": "error", "error": tb[-500:]},
                                    polls=polls, interval_s=interval_s)
                except OSError:
                    pass
            time.sleep(interval_s)
    finally:
        os.close(fd)
    return 0


def standup(root: str, interval_s: float = DEFAULT_INTERVAL_S) -> dict:
    """1-min self-heal + onlogon + detached pythonw. Proof is a FRESH heartbeat."""
    paths = CosmosPaths(root)
    hb = paths.logs(HEARTBEAT_NAME)
    t0 = time.time()
    proof = wait_fresh(hb, timeout_s=1.2, max_age_s=FRESH_S)
    if proof["ok"]:
        return {"started": "already", "proof": proof, "keith_cmd": None,
                "task_name": TASK_NAME}

    script = Path(__file__).resolve()
    tr = tr_cmdline(script, root, "--loop")
    minute = create_task(TASK_NAME, tr, "minute", mo=1, run_now=True)
    logon = create_task(TASK_NAME_LOGON, tr, "onlogon")
    launched_via = None
    detach = None
    if minute.get("ok") and minute.get("run_ok"):
        launched_via = "schtasks"
        proof = wait_fresh(hb, timeout_s=12.0, min_epoch=t0, max_age_s=FRESH_S)
    if not proof.get("ok"):
        argv = [pythonw_exe(), str(script), "--root", str(Path(root).resolve()),
                "--loop"]
        detach = spawn_detached(argv, str(script.parent),
                                paths.logs("work_order_runner.out"))
        launched_via = detach.get("method") or "detached"
        expect = detach.get("pid") if isinstance(detach.get("pid"), int) else None
        proof = wait_fresh(hb, timeout_s=15.0, min_epoch=t0, max_age_s=FRESH_S,
                           expect_pid=expect)

    keith = []
    for rec in (minute, logon):
        if rec.get("keith_cmd") and (rec.get("needs_elevation") or not rec.get("ok")):
            keith.append(rec["keith_cmd"])
        h = rec.get("harden") or {}
        if h.get("keith_cmd") and not h.get("ok"):
            keith.append(h["keith_cmd"])
    return {
        "started": launched_via,
        "task_minute": minute,
        "task_logon": logon,
        "detach": detach,
        "proof": proof,
        "heartbeat_path": str(hb),
        "keith_cmd": " & ".join(keith) if keith else None,
        "keith_cmds": keith,
        "task_name": TASK_NAME,
        "ok": bool((proof or {}).get("ok")),
    }


def status_probe(root: str) -> dict:
    paths = CosmosPaths(root)
    hb = paths.logs(HEARTBEAT_NAME)
    rec = read_heartbeat(hb)
    age = heartbeat_age_s(rec)
    paused = pause_flag(paths)
    dirs = work_order_dirs(paths)
    waiting = len(list_drops(dirs))
    return {
        "path": str(hb),
        "age_s": age,
        "heartbeat": rec,
        "pause_present": paused is not None,
        "pause": paused,
        "bucket": str(dirs["bucket"]),
        "assigned": str(dirs["assigned"]),
        "completed": str(dirs["completed"]),
        "drops_waiting": waiting,
        "task": query_task(TASK_NAME),
    }


def _dispatch_py() -> Path | None:
    here = Path(__file__).resolve().parent
    for cand in (
            here / "cosmos_dispatch.py",
            here.parent.parent / "cosmos" / "cosmos_dispatch.py",
            here.parent / "cosmos" / "cosmos_dispatch.py"):
        if cand.is_file():
            return cand
    return None


def _selftest() -> int:
    """Isolated install, fake rails, no live spend, no live-tree writes."""
    results: list[tuple[str, bool, str]] = []

    def check(label, fn):
        try:
            results.append((label, bool(fn()), ""))
        except Exception as e:  # noqa: BLE001
            results.append((label, False, f"{type(e).__name__}: {e}"))

    td = Path(tempfile.mkdtemp(prefix="cosmos_workorder_"))
    repo = td
    live = td / "live"
    write_sentinel(live, tree_id="wo-selftest")
    for name in ("cosmos", "docs", "tests", "kdash", "builds"):
        (repo / name).mkdir(parents=True, exist_ok=True)
    ctx = repo / "docs" / "WORK_ORDER_SPEC.md"
    ctx.write_text("# COSMOS Work Order — schema + lifecycle\n", encoding="utf-8")
    (live / "state").mkdir(parents=True, exist_ok=True)
    (live / "work").mkdir(parents=True, exist_ok=True)
    (live / "logs").mkdir(parents=True, exist_ok=True)
    paths = CosmosPaths(live)

    grok_raw = {
        "Agent": "xAI | Grok | grok-4.6",
        "Context source": ["docs/WORK_ORDER_SPEC.md"],
        "Task": "emit a one-line result",
        "Target & scope": "workspace out/ only",
        "Timestamp": "2026-08-27T12:00:00-05:00",
        "Output": "proposals | result.md",
    }
    parsed = parse_order(grok_raw)
    check("spec fields present after parse",
          lambda: all(f in parsed for f in SPEC_FIELDS))

    rg = route_agent(parsed["_agent"])
    check("xAI|Grok|grok-4.6 -> grok rail", lambda: rg["rail"] == "grok")
    check("grok binary is grok", lambda: rg["binary"] == "grok")
    check("grok model is grok-4.6", lambda: rg["model"] == "grok-4.6")

    rs = route_agent("Anthropic | Sonnet | sonnet-5")
    check("Anthropic|Sonnet|sonnet-5 -> claude rail",
          lambda: rs["rail"] == "claude")
    check("sonnet-5 model is claude-sonnet-5",
          lambda: rs["model"] == "claude-sonnet-5")

    ro = route_agent("OpenAI | Codex | gpt-5.3-codex")
    check("OpenAI|Codex -> codex rail",
          lambda: ro["rail"] == "codex" and ro["binary"] == "codex")

    rgem = route_agent("Google | Gemini | gemini-3.7-flash")
    check("Google -> gemini binary (not Ruby gem)",
          lambda: rgem["rail"] == "gemini"
          and Path(str(rgem["binary"])).name.lower() != "gem"
          and "gem" != str(rgem["binary"]).lower()
          and "gemini" in str(rgem["binary"]).lower())

    def _raises(kind, fn):
        try:
            fn()
        except OrderError as e:
            return e.kind == kind
        except WorkspaceError as e:
            return e.kind == kind
        return False

    check("2-part Agent refused",
          lambda: _raises("BAD_INPUT", lambda: parse_agent("xAI | Grok")))
    check("Cursor family refused",
          lambda: _raises("BAD_INPUT",
                          lambda: parse_agent("Cursor | Composer | composer-1.5")))
    check("write-mode context refused",
          lambda: _raises("REFUSED",
                          lambda: parse_context_source(
                              [{"path": "docs/x.md", "mode": "write"}])))
    check("absolute Output refused",
          lambda: _raises("REFUSED",
                          lambda: parse_output(r"V:\A\Ai\COSMOS | result.md")))

    check("live root refused as workspace",
          lambda: _raises("REFUSED",
                          lambda: refuse_tree_cwd(live, live, repo_tree=repo)))
    check("repo root refused as cwd",
          lambda: _raises("REFUSED",
                          lambda: refuse_tree_cwd(repo, live, repo_tree=repo)))

    ws = order_workspace(live, "argv-probe", repo_tree=repo)
    check("work-order workspace sits under work/orders",
          lambda: ws.resolve().is_relative_to((live / "work").resolve())
          and "orders" in ws.parts)
    gargv = build_argv(parsed, ws)
    check("grok proven flags kept",
          lambda: gargv[:2] == ["grok", "--single"]
          and "--always-approve" in gargv
          and "--output-format" in gargv
          and gargv[gargv.index("--output-format") + 1] == "plain"
          and "--max-turns" in gargv
          and str(gargv[gargv.index("--max-turns") + 1]) == "60")
    check("grok --cwd is the workspace",
          lambda: gargv[gargv.index("--cwd") + 1] == str(ws))

    claude_order = parse_order({
        **grok_raw,
        "Agent": "Anthropic | Sonnet | sonnet-5",
        "Output": "out | note.md",
    })
    cargv = build_argv(claude_order, ws)
    check("claude --permission-mode dontAsk",
          lambda: "--permission-mode" in cargv
          and cargv[cargv.index("--permission-mode") + 1] == "dontAsk")
    check("claude --add-dir is the workspace",
          lambda: "--add-dir" in cargv
          and cargv[cargv.index("--add-dir") + 1] == str(ws))

    gem_order = parse_order({
        **grok_raw,
        "Agent": "Google | Flash | gemini-3.7-flash",
        "Output": "out | g.md",
    })
    gemargv = build_argv(gem_order, ws)
    check("gemini argv uses -p and --approval-mode auto_edit",
          lambda: "-p" in gemargv
          and "--approval-mode" in gemargv
          and gemargv[gemargv.index("--approval-mode") + 1] == "auto_edit"
          and "gem" not in {a.lower() for a in gemargv[:1]})

    src = _dispatch_py()
    text = src.read_text(encoding="utf-8") if src and src.is_file() else ""
    check("existing dispatch grok flags still present",
          lambda: bool(src) and "--always-approve" in text
          and "--max-turns" in text and "--single" in text)
    check("existing dispatch claude flags still present",
          lambda: bool(src) and "--permission-mode" in text
          and "dontAsk" in text and "--add-dir" in text)
    check("existing dispatch cursor lane still present",
          lambda: bool(src) and "api.cursor.com" in text
          and "autoCreatePR" in text)

    def fake_write(argv, cwd, output, body="hello from fake rail\n"):
        Path(output).parent.mkdir(parents=True, exist_ok=True)
        Path(output).write_text(body, encoding="utf-8")
        return {"rc": 7, "out": "", "err": "", "timed_out": False}

    drop = drop_order(paths, grok_raw, order_id="wo-done-1")
    rec = process_one(paths, drop, run_fn=fake_write, repo_tree=repo)
    dirs = work_order_dirs(paths)
    check("runner files DONE in assigned-tasks",
          lambda: rec.get("state") == "DONE"
          and (dirs["assigned"] / "wo-done-1.json").is_file())
    check("DONE record is not COMPLETED",
          lambda: rec.get("state") == "DONE"
          and not (dirs["completed"] / "wo-done-1.json").is_file())
    check("output path is under workspace/out",
          lambda: str(rec.get("_output_path") or "").replace("\\", "/").endswith(
              "/out/proposals/result.md")
          or "out" in Path(rec["_output_path"]).parts)
    check("context staged as copies not live originals",
          lambda: rec.get("_staged")
          and Path(rec["_staged"][0]["dest"]).resolve() != ctx.resolve()
          and Path(rec["_staged"][0]["dest"]).is_file())
    check("rc is recorded, not the DONE predicate (rc=7 still DONE)",
          lambda: rec.get("observed_rc") == 7 and rec.get("state") == "DONE")

    accepted = accept_order(live, "wo-done-1", note="selftest", paths=paths)
    check("accept_order is the only COMPLETED transition",
          lambda: accepted.get("state") == "COMPLETED"
          and (dirs["completed"] / "wo-done-1.json").is_file()
          and not (dirs["assigned"] / "wo-done-1.json").is_file())
    check("accept_order returns output_head",
          lambda: "hello from fake rail" in str(accepted.get("output_head") or ""))

    drop2 = drop_order(paths, grok_raw, order_id="wo-reject-1")
    process_one(paths, drop2, run_fn=fake_write, repo_tree=repo)
    rejected = reject_order(live, "wo-reject-1", note="nope", paths=paths)
    check("reject stays DONE",
          lambda: rejected.get("state") == "DONE"
          and rejected.get("rejected") is True
          and (dirs["assigned"] / "wo-reject-1.json").is_file()
          and not (dirs["completed"] / "wo-reject-1.json").is_file())

    def fake_silent(argv, cwd, output):
        return {"rc": 0, "out": "said ok", "err": "", "timed_out": False}

    drop3 = drop_order(paths, grok_raw, order_id="wo-empty-1")
    missed = process_one(paths, drop3, run_fn=fake_silent, repo_tree=repo)
    check("missing output is FAILED",
          lambda: missed.get("state") == "FAILED"
          and (dirs["failed"] / "wo-empty-1.json").is_file())

    def _accept_failed():
        try:
            accept_order(live, "wo-empty-1", paths=paths)
            return False
        except OrderError as e:
            return e.kind == "FAILED"

    check("FAILED cannot be accepted", _accept_failed)

    pause_p = live / "state" / "control" / "PAUSE.flag"
    pause_p.parent.mkdir(parents=True, exist_ok=True)
    pause_p.write_text(json.dumps({
        "state": "PAUSED", "reason": "selftest", "set_by": "selftest",
        "set_at": "2026-08-27T12:00:00-05:00", "mode": "hold",
    }), encoding="utf-8")
    drop4 = drop_order(paths, grok_raw, order_id="wo-pause-1")
    paused_tick = poll_once(str(live), drain=False, run_fn=fake_write,
                            repo_tree=repo)
    check("PAUSE + drain=False picks up nothing",
          lambda: paused_tick.get("dropped_this_tick") == 0
          and drop4.is_file()
          and paused_tick.get("state") == "PAUSED")
    check("PAUSE heartbeat state=PAUSED",
          lambda: (paused_tick.get("heartbeat") or {}).get("state") == "PAUSED"
          and (live / "logs" / HEARTBEAT_NAME).is_file())

    commanded = poll_once(str(live), drain=True, run_fn=fake_write,
                          repo_tree=repo)
    check("--once drain=True still picks up under PAUSE",
          lambda: commanded.get("dropped_this_tick") == 1
          and any(j.get("order_id") == "wo-pause-1" for j in commanded.get("jobs") or []))

    modules = (
        Path(__file__).resolve(),
        HERE / "cosmos_work_order.py",
        HERE / "cosmos_workspace.py",
    )
    import re as _re
    bts = _re.compile(r"^\s*(?:from|import)\s+bts_\w+", _re.M)

    def _no_bts():
        for p in modules:
            if p.is_file() and bts.search(p.read_text(encoding="utf-8")):
                return False
        return True

    check("no bts_ import in the new modules", _no_bts)

    bad = [(l, e) for l, ok, e in results if not ok]
    for l, ok, e in results:
        print(("  OK  " if ok else "  FAIL") + f" {l}" + (f"  {e}" if e else ""))
    print(f"{len(results) - len(bad)}/{len(results)} passed")
    return 1 if bad else 0


def main() -> int:
    ap = argparse.ArgumentParser(prog="cosmos_work_order_run")
    ap.add_argument("--root", default=None)
    ap.add_argument("--loop", action="store_true")
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--standup", action="store_true")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--accept", metavar="ORDER_ID")
    ap.add_argument("--reject", metavar="ORDER_ID")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--interval", type=float, default=DEFAULT_INTERVAL_S)
    ap.add_argument("--note", default=None)
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.root:
        print("cosmos_work_order_run: --root is required "
              "(except --selftest)", file=sys.stderr)
        return 2
    if a.status:
        rec = status_probe(a.root)
        print(json.dumps(rec, indent=1, default=str))
        age = rec.get("age_s")
        return 0 if age is not None and age < FRESH_S else 2
    if a.standup:
        r = standup(a.root, a.interval)
        print(json.dumps(r, indent=1, default=str))
        return 0 if (r.get("proof") or {}).get("ok") else 2
    if a.accept:
        rec = accept_order(a.root, a.accept, note=a.note)
        print(json.dumps({
            "ok": rec.get("state") == "COMPLETED",
            "order_id": rec.get("order_id"),
            "state": rec.get("state"),
            "accepted_by": rec.get("accepted_by"),
            "output_head": rec.get("output_head"),
            "output_path": rec.get("_output_path"),
        }, indent=1, default=str))
        return 0 if rec.get("state") == "COMPLETED" else 2
    if a.reject:
        rec = reject_order(a.root, a.reject, note=a.note)
        print(json.dumps({
            "ok": rec.get("state") == "DONE" and rec.get("rejected"),
            "order_id": rec.get("order_id"),
            "state": rec.get("state"),
            "rejected": rec.get("rejected"),
        }, indent=1, default=str))
        return 0 if rec.get("state") == "DONE" else 2
    if a.once:
        r = poll_once(a.root, interval_s=a.interval, drain=True)
        out = {k: r[k] for k in r if k != "heartbeat"}
        print(json.dumps(out, indent=1, default=str))
        return 0 if r.get("ok") else 2
    return loop(a.root, a.interval)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CosmosPathError as e:
        print(e, file=sys.stderr)
        raise SystemExit(2)
    except OrderError as e:
        print(json.dumps({"ok": False, "kind": e.kind, "error": str(e)},
                         indent=1))
        raise SystemExit(2)
    except WorkspaceError as e:
        print(json.dumps({"ok": False, "kind": e.kind, "error": str(e)},
                         indent=1))
        raise SystemExit(2)
