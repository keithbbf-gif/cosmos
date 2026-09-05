#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_prepaid_orch - F-53 second/parallel orchestrator on a PREPAID rail.

Disposed winner: grok (docs/research/AUTO_RESESSION.md ranked #1; already
on PATH; already the dispatch recipe; prepaid login). Claude is the
resource this wish exists to free — this satellite never invokes claude.

WHAT IT IS
    A satellite in the resession/askmine class. One tick:
      1. verify runtime root
      2. HOLD wins (PAUSE.flag mode=hold never self-clears)
      3. winner is grok; missing binary is NO_RAIL
      4. register mailbox writer_id=gbot; COW mailbox is cow (F-55 channel)
      5. if COW heartbeat is fresh: PARALLEL — mailbox ping AND drop one
         MOTIF work-order into the resolver bucket when none is already
         open (queue drop only; never write kernel/ledger/sched/service).
         One open prepaid-orch order at a time — a live COW is not a
         reason to idle, and not a reason to flood the bucket. Spawn
         only if --spawn (always-approve on the live tree is Keith-shaped)
      6. if COW is quiet/absent: ORCHESTRATE — same drop (no flood guard
         needed: COW is not writing the route); spawn only if --spawn
    It does NOT write kernel / ledger / sched / service.

CLOCKS id 24. --plan-task / --standup never register a task from a test;
--install-task is Keith's elevated line.

    py -3.14 cosmos\\cosmos_prepaid_orch.py --root <live> --once
    py -3.14 cosmos\\cosmos_prepaid_orch.py --root <live> --once --dry-run
    py -3.14 cosmos\\cosmos_prepaid_orch.py --root <live> --plan-task

Does not modify kernel/ledger/sched/service.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cosmos_clock import (  # noqa: E402
    create_task, plan_create, query_task, tr_cmdline, write_heartbeat,
)
from cosmos_mail import Mailbox  # noqa: E402
from cosmos_paths import CosmosPathError, CosmosPaths  # noqa: E402
from cosmos_resession import (  # noqa: E402
    COW_HEARTBEAT_NAME, HEARTBEAT_STALE_S, PAUSE_NAME, classify_pause,
    spawn_argv as resession_spawn_argv,
)
from cosmos_work_order import drop_order, work_order_dirs  # noqa: E402

WORKER = "cosmos-prepaid-orch"
SCHEMA = "cosmos-prepaid-orch/1"
CLOCK_ID = 24
TASK_NAME = "COSMOS Prepaid Orchestrator"
HEARTBEAT_NAME = "prepaid_orch_heartbeat.json"
PROJECTION_NAME = "prepaid_orch.json"
NO_WINDOW = 0x08000000 if os.name == "nt" else 0

WINNER = "grok"
WINNER_SOURCE = "docs/research/AUTO_RESESSION.md ranked 1"
WRITER_ID = "gbot"
COW_ID = "cow"
PROMPT = (
    "You are GrokBot, the prepaid parallel orchestrator. Drive the MOTIF "
    "route. Drop work in the box. Do not search in your own context. "
    "Do not invoke claude."
)


class PrepaidOrchError(RuntimeError):
    """kind in {NO_ROOT, HOLD, NO_RAIL, CLAUDE_SPEND}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def repo_tree() -> Path:
    return Path(__file__).resolve().parent.parent


def _iso(ts: float | None = None) -> str:
    if ts is None:
        return datetime.now().astimezone().isoformat(timespec="seconds")
    return datetime.fromtimestamp(ts).astimezone().isoformat(timespec="seconds")


def _read_json(path: Path) -> dict | None:
    if not path.is_file():
        return None
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeDecodeError):
        return None
    return obj if isinstance(obj, dict) else None


def spawn_argv(prompt: str, cwd: str, session_id: str) -> list[str]:
    """Grok dispatch recipe only. Claude is CLAUDE_SPEND."""
    return resession_spawn_argv("grok", prompt, cwd, session_id)


def refuse_rail(rail: str) -> str:
    r = str(rail or "").strip().lower()
    if r == "claude":
        raise PrepaidOrchError(
            "CLAUDE_SPEND",
            "F-53 never invokes claude; grok is the prepaid winner")
    if r != WINNER:
        raise PrepaidOrchError("NO_RAIL", f"unknown rail {rail!r}; winner is {WINNER}")
    return r


def bind(root: str) -> dict:
    paths = CosmosPaths(root)
    logs = paths.logs()
    logs.mkdir(parents=True, exist_ok=True)
    state = paths.state("prepaid_orch")
    state.mkdir(parents=True, exist_ok=True)
    control = paths.state("control")
    control.mkdir(parents=True, exist_ok=True)
    mail_root = paths.state("mail")
    mail_root.mkdir(parents=True, exist_ok=True)
    return {
        "paths": paths,
        "heartbeat": logs / HEARTBEAT_NAME,
        "projection": state / PROJECTION_NAME,
        "control": control,
        "mail_root": mail_root,
        "repo": repo_tree(),
    }


def cow_fresh(hb: dict | None, now: float) -> bool:
    if not hb:
        return False
    epoch = hb.get("last_run_epoch")
    if epoch is None:
        epoch = hb.get("last_act_epoch")
    if epoch is None:
        stamped = hb.get("stamped_at") or hb.get("last_run")
        if stamped:
            try:
                epoch = datetime.fromisoformat(
                    str(stamped).replace("Z", "+00:00")).timestamp()
            except ValueError:
                return False
        else:
            return False
    try:
        age = now - float(epoch)
    except (TypeError, ValueError):
        return False
    return age <= HEARTBEAT_STALE_S


OPEN_ORDER_STATES = frozenset({"DROPPED", "PICKED_UP"})


def open_prepaid_orders(paths) -> list[Path]:
    """Flood guard: DROPPED/PICKED_UP prepaid-orch orders still in the box.

    PARALLEL drops at most one MOTIF work-order while an earlier one is
    open. The box is the IPC surface (P9); this is not a tree write.
    `paths` is a CosmosPaths or a runtime-root Path.
    """
    if not hasattr(paths, "state"):
        paths = CosmosPaths(paths)
    dirs = work_order_dirs(paths)
    found: list[Path] = []
    for name in ("bucket", "picked"):
        folder = dirs[name]
        if not folder.is_dir():
            continue
        for p in folder.glob("*.json"):
            obj = _read_json(p)
            if not obj:
                continue
            agent = str(obj.get("Agent") or "").lower()
            if "prepaid-orch" not in agent:
                continue
            if obj.get("state") in OPEN_ORDER_STATES:
                found.append(p)
    return found


def _drop_one(paths, repo: Path) -> Path:
    wishlist = repo / "docs" / "WISHLIST.md"
    raw = {
        "Agent": "xAI | grok | prepaid-orch",
        "Context source": str(wishlist) + " [read*]",
        "Task": (
            "Drive the MOTIF route from WISHLIST/BACKLOG. Drop work in the "
            "box. Do not search in your own context. Do not invoke claude."
        ),
        "Target & scope": (
            "queue drop only; never write kernel/ledger/sched/service"
        ),
        "Timestamp": _iso(),
        "Output": "prepaid | result.json",
    }
    return drop_order(paths, raw)


def poll_once(root: str, *, which=None, spawn=None, dry_run: bool = False,
              now: float | None = None, rail: str = WINNER) -> dict:
    """One tick. Always heartbeats unless dry_run. Never invokes claude."""
    refuse_rail(rail)
    bound = bind(root)
    now = time.time() if now is None else float(now)
    which = which or shutil.which
    pause = _read_json(bound["control"] / PAUSE_NAME)
    cls = classify_pause(pause)
    grok_path = which("grok")
    cow_hb = _read_json(bound["control"] / COW_HEARTBEAT_NAME)
    session_id = str(uuid.uuid4())
    planned = spawn_argv(PROMPT, str(bound["repo"]), session_id)
    rec = {
        "schema": SCHEMA,
        "clock_id": CLOCK_ID,
        "ok": True,
        "winner": WINNER,
        "winner_source": WINNER_SOURCE,
        "rail": WINNER,
        "dry_run": bool(dry_run),
        "tree_id": bound["paths"].sentinel.tree_id,
        "writes": 0,
        "dropped": 0,
        "spawned": 0,
        "mail_sent": 0,
        "spawn_argv": planned,
        "grok_present": bool(grok_path),
        "cow_fresh": cow_fresh(cow_hb, now),
        "_readme": (
            "Prepaid parallel orchestrator. Winner=grok. Never claude. "
            "PARALLEL while COW is alive (mailbox ping + one MOTIF drop "
            "if none open). ORCHESTRATE when COW is quiet (drop one "
            "work-order). --spawn is opt-in."
        ),
    }
    if grok_path:
        rec["grok_path"] = grok_path

    if cls["class"] == "HOLD":
        rec.update(ok=False, state="HOLD", kind="HOLD", detail=cls["why"])
        return _finish(bound, rec, dry_run)

    if not grok_path:
        rec.update(ok=False, state="NO_RAIL", kind="NO_RAIL",
                   detail="grok binary not on PATH")
        return _finish(bound, rec, dry_run)

    gbot = Mailbox(bound["mail_root"], WRITER_ID)
    cow = Mailbox(bound["mail_root"], COW_ID)
    if not dry_run:
        gbot.register()
        cow.register()

    if rec["cow_fresh"]:
        rec["state"] = "PARALLEL"
        if not dry_run:
            gbot.send(COW_ID, "gbot-alive",
                      json.dumps({"winner": WINNER, "clock_id": CLOCK_ID,
                                  "state": "PARALLEL"}))
            rec["mail_sent"] = 1
            rec["writes"] = 3  # heartbeat + projection + mail
            open_n = len(open_prepaid_orders(bound["paths"]))
            rec["open_prepaid"] = open_n
            if open_n == 0:
                dest = _drop_one(bound["paths"], bound["repo"])
                rec["dropped"] = 1
                rec["order_path"] = str(dest)
                rec["writes"] = 4
                if spawn is not None:
                    spawn(planned)
                    rec["spawned"] = 1
                    rec["writes"] = 5
        return _finish(bound, rec, dry_run)

    rec["state"] = "ORCHESTRATE"
    if not dry_run:
        dest = _drop_one(bound["paths"], bound["repo"])
        rec["dropped"] = 1
        rec["order_path"] = str(dest)
        rec["writes"] = 3  # heartbeat + projection + order
        if spawn is not None:
            spawn(planned)
            rec["spawned"] = 1
            rec["writes"] = 4
    return _finish(bound, rec, dry_run)


def _finish(bound: dict, rec: dict, dry_run: bool) -> dict:
    rec["heartbeat"] = HEARTBEAT_NAME
    rec["projection"] = str(bound["projection"])
    if dry_run:
        rec["writes"] = 0
        return rec
    bound["projection"].parent.mkdir(parents=True, exist_ok=True)
    tmp = bound["projection"].with_suffix(".tmp")
    tmp.write_text(json.dumps(rec, indent=1, default=str), encoding="utf-8")
    os.replace(tmp, bound["projection"])
    extra = {
        "schema": SCHEMA,
        "tick": "done",
        "ok": rec.get("ok"),
        "state": rec.get("state"),
        "clock_id": CLOCK_ID,
        "winner": WINNER,
        "tree_id": rec.get("tree_id"),
        "dropped": rec.get("dropped"),
        "spawned": rec.get("spawned"),
    }
    write_heartbeat(bound["heartbeat"], WORKER, extra=extra)
    rec["path"] = str(bound["heartbeat"])
    rec["projection_path"] = str(bound["projection"])
    if rec.get("writes", 0) < 2:
        rec["writes"] = 2
    return rec


def plan_task_argv(root: str | Path) -> list[str]:
    """schtasks /create plan. minute/1 one-shot. Registers nothing."""
    tr = tr_cmdline(Path(__file__).resolve(), str(root), "--once")
    return plan_create(TASK_NAME, tr, "minute", mo=1)


def install_task(root: str | Path) -> dict:
    argv = plan_task_argv(root)
    try:
        p = subprocess.run(
            argv, capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=60,
            creationflags=NO_WINDOW)
    except OSError as e:
        return {"ok": False, "rc": -1, "argv": argv, "out": str(e)}
    return {"ok": p.returncode == 0, "rc": p.returncode, "argv": argv,
            "out": ((p.stdout or "") + (p.stderr or "")).strip()}


def standup(root: str) -> dict:
    """Register the minute/1 --once task if missing. Never called by tests."""
    existing = query_task(TASK_NAME)
    script = Path(__file__).resolve()
    tr = tr_cmdline(script, root, "--once")
    if existing.get("ok"):
        tick_rec = poll_once(root)
        return {"started": "already", "task": existing, "tick": tick_rec,
                "keith_cmd": None, "task_name": TASK_NAME}
    task = create_task(TASK_NAME, tr, "minute", mo=1, run_now=False)
    return {
        "started": "schtasks" if task.get("ok") else "planned",
        "task": task,
        "keith_cmd": task.get("keith_cmd") if (
            task.get("needs_elevation") or not task.get("ok")) else None,
        "task_name": TASK_NAME,
        "proof": {"ok": True, "heartbeat": HEARTBEAT_NAME},
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="cosmos_prepaid_orch",
                                 description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", help="runtime root (live/)")
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--spawn", action="store_true",
                    help="actually spawn grok -p (opt-in; default plans argv)")
    ap.add_argument("--rail", default=WINNER,
                    help="must be grok; claude is CLAUDE_SPEND")
    ap.add_argument("--plan-task", action="store_true",
                    help="print the schtasks argv, register nothing")
    ap.add_argument("--install-task", action="store_true")
    ap.add_argument("--standup", action="store_true")
    a = ap.parse_args(argv)

    if a.plan_task:
        if not a.root:
            print(json.dumps({"ok": False, "kind": "NO_ROOT",
                              "detail": "--root is required"}))
            return 2
        print(json.dumps({"task": TASK_NAME, "argv": plan_task_argv(a.root),
                          "heartbeat": HEARTBEAT_NAME, "clock_id": CLOCK_ID},
                         indent=1))
        return 0
    if a.install_task:
        if not a.root:
            print(json.dumps({"ok": False, "kind": "NO_ROOT",
                              "detail": "--root is required"}))
            return 2
        rec = install_task(a.root)
        print(json.dumps(rec, indent=1))
        return 0 if rec["ok"] else 1
    if a.standup:
        if not a.root:
            print(json.dumps({"ok": False, "kind": "NO_ROOT",
                              "detail": "--root is required"}))
            return 2
        rec = standup(a.root)
        print(json.dumps(rec, indent=1, default=str))
        return 0
    if a.once:
        if not a.root:
            print(json.dumps({"ok": False, "kind": "NO_ROOT",
                              "detail": "--root is required"}))
            return 2
        try:
            refuse_rail(a.rail)
        except PrepaidOrchError as e:
            print(json.dumps({"ok": False, "kind": e.kind, "error": str(e)}))
            return 2
        rec = poll_once(a.root, dry_run=a.dry_run, rail=a.rail,
                        spawn=(subprocess.run if a.spawn else None))
        print(json.dumps(rec, indent=1, default=str))
        return 0 if rec.get("ok") else 2
    ap.print_help()
    return 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CosmosPathError as e:
        print(json.dumps({"ok": False, "kind": "NO_ROOT", "error": str(e)}),
              file=sys.stderr)
        raise SystemExit(2)
    except PrepaidOrchError as e:
        print(json.dumps({"ok": False, "kind": e.kind, "error": str(e)}))
        raise SystemExit(2)
