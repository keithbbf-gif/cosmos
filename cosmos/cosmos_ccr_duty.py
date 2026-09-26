#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""What Gitur does, and what CCr does after it.

Gitur publishes. CCr keeps one head. Neither grades the pile (that is the
Judge) and CCr does not run the Composer check (that is Gitur).

This module measures. It does not merge, pull, or push.

    py -3.14 cosmos\\cosmos_ccr_duty.py --selftest
"""
from __future__ import annotations

import subprocess

SCHEMA = "cosmos-ccr-duty/1"

GITUR_DOES = (
    "Read the Judge KEEP in gitur_inbox. Do not grade it again.",
    "Open one GitHub PR whose base is origin/main.",
    "Open the GitLab MR at that same commit.",
    "Run Composer 2.5 on that diff. Composer checks. Composer does not merge.",
    "PASS copies the row to ccr_inbox. FAIL stays in gitur_inbox.",
    "Stop. Do not write V:\\. Do not fast-forward. Do not squash-merge.",
)
CCR_DOES = (
    "Read Gitur's three legs (GitHub, GitLab, Cursor). A dark leg is a warning. Do not merge while one is dark.",
    "Measure V:\\ against origin/main and gitlab/main. Synced means both ahead and behind are 0.",
    "If V:\\ is ahead of a remote, stop. Those commits go back through Gitur. Do not join-commit.",
    "If V:\\ is behind a remote, fast-forward only: git merge --ff-only.",
    "When a ccr_inbox row is Composer PASS: review that one PR, squash-merge it, then fast-forward V:\\ so HEAD matches origin/main and gitlab/main.",
    "Do not open the PR. Do not run Composer. Do not grade the pile.",
)


def _run_git(repo: str, args: list) -> tuple:
    try:
        proc = subprocess.run(
            ["git", *args], cwd=repo, capture_output=True, text=True, timeout=20,
        )
    except (OSError, subprocess.TimeoutExpired) as e:
        return 1, "", str(e)
    return proc.returncode, proc.stdout or "", proc.stderr or ""


def _counts(text: str) -> tuple:
    parts = str(text or "").replace("\t", " ").split()
    if len(parts) < 2:
        raise ValueError(text)
    return int(parts[0]), int(parts[1])


def measure_sync(repo, *, run=None) -> dict:
    """left = remote commits V:\\ lacks. right = V:\\ commits the remote lacks."""
    run = run or _run_git
    root = str(repo)
    legs = []
    rc, out, _err = run(root, ["remote"])
    names = set((out or "").split()) if rc == 0 else set()
    wanted = [("origin", "origin/main")]
    if "gitlab" in names or rc != 0:
        wanted.append(("gitlab", "gitlab/main"))
    for remote, ref in wanted:
        if rc == 0 and remote not in names:
            legs.append({
                "remote": remote, "ref": ref, "status": "ABSENT",
                "behind": None, "ahead": None,
            })
            continue
        code, text, err = run(root, ["rev-list", "--left-right", "--count", f"{ref}...HEAD"])
        if code != 0:
            legs.append({
                "remote": remote, "ref": ref, "status": "UNMEASURED",
                "behind": None, "ahead": None,
                "detail": (err or text)[:160],
            })
            continue
        try:
            behind, ahead = _counts(text)
        except ValueError:
            legs.append({
                "remote": remote, "ref": ref, "status": "UNMEASURED",
                "behind": None, "ahead": None, "detail": text[:160],
            })
            continue
        if behind == 0 and ahead == 0:
            status = "SYNCED"
        elif ahead and behind:
            status = "TWO_HEADS"
        elif ahead:
            status = "AHEAD"
        else:
            status = "BEHIND"
        legs.append({
            "remote": remote, "ref": ref, "status": status,
            "behind": behind, "ahead": ahead,
        })
    return {"schema": SCHEMA, "repo": root, "legs": legs}


def gitur_warnings(snap: dict | None) -> list:
    if not isinstance(snap, dict):
        return ["Gitur legs UNMEASURED — no snapshot was passed"]
    out = []
    if snap.get("rails_err"):
        out.append(f"Gitur rails: {snap.get('rails_err')}")
    panes = snap.get("panes") if isinstance(snap.get("panes"), dict) else {}
    for leg in ("github", "gitlab", "cursor"):
        pane = panes.get(leg) if isinstance(panes.get(leg), dict) else {}
        live = pane.get("live") if isinstance(pane.get("live"), dict) else {}
        if live.get("ok") is not True:
            out.append(f"Gitur {leg} is not smooth")
    return out


def _pass_waiting(paths) -> int:
    try:
        inbox = paths.state("crew_pipe") / "ccr_inbox"
    except Exception:  # noqa: BLE001
        return 0
    if not inbox.is_dir():
        return 0
    n = 0
    for path in inbox.glob("*.json"):
        try:
            import json
            row = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if str(row.get("gitur_status") or "").upper() == "PASS":
            n += 1
    return n


def next_action(sync: dict, *, passes: int, warnings: list, head=None) -> str:
    legs = sync.get("legs") or []
    origin = next((r for r in legs if r.get("remote") == "origin"), None)
    if origin is None or origin.get("status") == "UNMEASURED":
        return "Measure origin/main before any fast-forward."
    if any(r.get("status") == "TWO_HEADS" for r in legs):
        return "Stop. Two heads. Send the work through Gitur. Do not join-commit."
    if any(r.get("status") == "AHEAD" for r in legs):
        return "Stop. V:\\ is ahead of a remote. Those commits go back through Gitur."
    if any(r.get("status") == "BEHIND" for r in legs):
        return "Fast-forward only: git merge --ff-only. Do not merge histories."
    if isinstance(head, dict) and head.get("synced") is not True:
        kind = head.get("kind") or "NOT_SYNCED"
        return "Stop. Head gate %s. Refuse synced. Do not join-commit." % kind
    if warnings:
        return "Synced. Gitur is not smooth. Do not squash-merge until the dark leg answers."
    if passes:
        return (
            "Composer PASS is waiting. Review that one PR, squash-merge it, "
            "then fast-forward V:\\ so HEAD matches the remotes."
        )
    return "Synced. Nothing in ccr_inbox. Idle."


def head_claim(repo, run=None) -> dict:
    """The one-head gate. Unmeasured or ahead is not synced."""
    from cosmos_head_gate import head_gate
    from cosmos_warn import WarnRefuse

    try:
        if run is None:
            return head_gate(repo)

        def adapted(cmd, root):
            args = list(cmd)[1:] if cmd and cmd[0] == "git" else list(cmd)
            rc, out, err = run(str(root), args)
            if rc != 0:
                raise OSError((err or out or "git failed")[:200])
            return out

        return head_gate(repo, run=adapted)
    except WarnRefuse as e:
        return {
            "schema": "cosmos-head-gate/1",
            "synced": False,
            "kind": e.kind,
            "detail": e.detail,
        }


def report(paths, repo, *, gitur=None, run=None) -> dict:
    sync = measure_sync(repo, run=run)
    warnings = gitur_warnings(gitur)
    passes = _pass_waiting(paths)
    head = head_claim(repo, run=run)
    return {
        "schema": SCHEMA,
        "gitur_does": list(GITUR_DOES),
        "ccr_does": list(CCR_DOES),
        "sync": sync,
        "head_gate": head,
        "warnings": warnings,
        "composer_pass_waiting": passes,
        "next": next_action(sync, passes=passes, warnings=warnings, head=head),
        "writes": False,
    }


def _selftest() -> int:
    ok = True

    def check(label, cond):
        nonlocal ok
        print(("  OK  " if cond else "  FAIL") + " " + label)
        if not cond:
            ok = False

    calls = []

    def fake(repo, args):
        calls.append(args)
        if args == ["remote"]:
            return 0, "origin\ngitlab\n", ""
        if args[0] == "rev-list" and "origin/main...HEAD" in args:
            return 0, "0\t2\n", ""
        if args[0] == "rev-list" and "gitlab/main...HEAD" in args:
            return 0, "0\t0\n", ""
        return 1, "", "no"

    sync = measure_sync(".", run=fake)
    by = {r["remote"]: r for r in sync["legs"]}
    check("ahead of origin is AHEAD, not a fake sync",
          by["origin"]["status"] == "AHEAD" and by["origin"]["ahead"] == 2
          and by["gitlab"]["status"] == "SYNCED")
    action = next_action(sync, passes=1, warnings=[])
    check("ahead stops the pen", action.startswith("Stop."))
    behind = {"legs": [
        {"remote": "origin", "status": "BEHIND", "behind": 3, "ahead": 0},
        {"remote": "gitlab", "status": "SYNCED", "behind": 0, "ahead": 0},
    ]}
    check("behind is fast-forward only",
          next_action(behind, passes=0, warnings=[]).startswith("Fast-forward"))
    split = {"legs": [
        {"remote": "origin", "status": "TWO_HEADS", "behind": 1, "ahead": 1},
    ]}
    check("two heads do not join-commit",
          "join-commit" in next_action(split, passes=0, warnings=[]))
    clean = {"legs": [
        {"remote": "origin", "status": "SYNCED", "behind": 0, "ahead": 0},
    ]}
    dark = gitur_warnings({"panes": {"github": {"live": {"ok": False}},
                                    "gitlab": {"live": {"ok": True}},
                                    "cursor": {"live": {"ok": True}}}})
    check("a dark GitHub leg warns and holds the merge",
          any("github" in w for w in dark)
          and "not smooth" in next_action(clean, passes=1, warnings=dark))
    check("a clean idle names no write",
          next_action(clean, passes=0, warnings=[]) == "Synced. Nothing in ccr_inbox. Idle."
          and len(GITUR_DOES) == 6 and len(CCR_DOES) == 6)
    check("head gate refuse is not Synced",
          next_action(clean, passes=0, warnings=[],
                      head={"synced": False, "kind": "NOT_SYNCED"}).startswith("Stop."))
    check("head gate zero still says Synced",
          next_action(clean, passes=0, warnings=[],
                      head={"synced": True, "ahead": 0})
          == "Synced. Nothing in ccr_inbox. Idle.")
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        raise SystemExit(_selftest())
    print("cosmos_ccr_duty: --selftest", file=sys.stderr)
    raise SystemExit(2)
