#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ORC BootUP from cDeck: stream picker, TidyUP/TU2 recovery, then start.

When OpenWork is already live, cDeck snaps it and this module is not required
to spawn a second mouth. When OpenWork was down, cDeck launches it and asks
which stream to load. That POST:

  1. Inspects HMAC SEED vs running_session_file.toml (proper shutdown?).
  2. If partial / improper: TidyUP reconstruct (close_session force) + COSMOS
     TU2 recount. That reconstruct pass IS the Temp/Recovery session.
  3. Recovery closes. start_session(stream) injects the BU. OpenWork's new
     vendor chat BootUPs from that seed like normal.

GET never mkdir. GET never invents a seed. Does not spawn OpenWork.exe
(native cDeck does). Does not write V:\\Ai. Does not click USPTO.

    py -3.14 cosmos\\cosmos_orc_boot.py --selftest
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cosmos_resession import RUNNING_SESSION_NAME, cosmos_tu2  # noqa: E402
from cosmos_session import SessionError  # noqa: E402

SCHEMA = "cosmos-orc-boot/1"
STREAMS = ("Cm", "plumbing", "physics", "chapter", "legal")
REPO = Path(__file__).resolve().parent.parent


class OrcBootError(RuntimeError):
    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def _pin_stream(stream) -> str:
    s = str(stream or "").strip()
    if s not in STREAMS:
        raise OrcBootError(
            "BAD_STREAM",
            f"stream must be one of {STREAMS}, got {stream!r}")
    return s


def _mtime(p: Path):
    try:
        return p.stat().st_mtime if p.is_file() else None
    except OSError:
        return None


def inspect_boot(paths) -> dict:
    """GET fold. Never mkdir. Never invents a seed."""
    state = paths.role("state")
    seed = state / "SEED.json"
    decl = state / "SEED.decl.json"
    running = state / RUNNING_SESSION_NAME
    seed_m = _mtime(seed)
    decl_m = _mtime(decl)
    run_m = _mtime(running)
    seed_ok = seed.is_file() and decl.is_file()
    running_newer = (
        run_m is not None and (seed_m is None or run_m > seed_m + 1.0)
    )
    if seed_ok and not running_newer:
        kind = "GOOD_CLOSE"
    elif running_newer or (running.is_file() and not seed_ok):
        kind = "PARTIAL"
    elif seed_ok:
        kind = "GOOD_CLOSE"
    else:
        kind = "NO_SEED"
    return {
        "schema": SCHEMA,
        "ok": True,
        "kind": kind,
        "streams": list(STREAMS),
        "seed": "PRESENT" if seed.is_file() else "ABSENT",
        "decl": "PRESENT" if decl.is_file() else "ABSENT",
        "running": "PRESENT" if running.is_file() else "ABSENT",
        "running_newer": bool(running_newer),
        "seed_mtime": seed_m,
        "running_mtime": run_m,
        "decl_mtime": decl_m,
        "note": (
            "GOOD_CLOSE = HMAC SEED from a proper TidyUP. PARTIAL = running "
            "pointer newer than SEED (improper close or still-open vendor). "
            "NO_SEED = nothing to inject; recovery reconstructs from the "
            "ledger then TU2, and still refuses to invent a seed if close "
            "cannot write one. GET never mkdir."
        ),
    }


def boot(kernel, stream, *, repo: Path | None = None) -> dict:
    """POST: recover if needed, then BootUP inject for the named stream."""
    s = _pin_stream(stream)
    paths = kernel.paths
    rec = inspect_boot(paths)
    rec["stream"] = s
    sm = kernel.sessions
    already = sm.session is not None and getattr(sm.session, "_open", False)
    rec["core_session"] = (
        "OPEN" if already else "NONE"
    )
    recovered = False
    tu2 = None
    repo_path = Path(repo) if repo else REPO
    if rec["kind"] != "GOOD_CLOSE":
        sm.close_session(handoff_to=s, force=True)
        recovered = True
        rec["recovery"] = "TU_RECONSTRUCT"
        try:
            tu2 = cosmos_tu2(repo=repo_path, root=paths.root)
        except OSError as e:
            tu2 = {"ok": False, "kind": "TU2", "findings": [str(e)[:200]],
                   "n_findings": 1, "n_checks": 0, "checks": []}
        rec["tu2"] = {
            "ok": bool(tu2.get("ok")),
            "n_findings": tu2.get("n_findings"),
            "findings": list(tu2.get("findings") or [])[:12],
        }
        rec["kind"] = "RECOVERED"
    if already and not recovered:
        rec["started"] = False
        rec["kind"] = "ALREADY_LIVE"
        rec["sid"] = sm.session.sid
        rec["note"] = (
            "Core session already open. OpenWork goes live with this cDeck. "
            "Did not TidyUP a live Core session."
        )
        return rec
    try:
        inherit = sm.start_session(s)
    except SessionError as e:
        raise OrcBootError(e.kind, str(e)) from e
    rec["started"] = True
    rec["sid"] = inherit.get("sid")
    rec["n_facts"] = len(inherit.get("facts") or {})
    rec["n_watchers"] = len(inherit.get("watchers") or {})
    rec["handoff"] = inherit.get("handoff")
    rec["recovered"] = recovered
    rec["kind"] = "STARTED"
    rec["note"] = (
        "Temp/Recovery closed. New Core session started with BU inject. "
        "OpenWork vendor chat BootUPs from SEED + BUCm like normal."
        if recovered else
        "Proper shutdown SEED. New Core session started with BU inject."
    )
    return rec


def _selftest() -> int:
    import tempfile
    from cosmos_kernel import install
    from cosmos_paths import CosmosPaths

    results = []

    def check(label, fn):
        try:
            results.append((label, bool(fn()), ""))
        except Exception as e:  # noqa: BLE001
            results.append((label, False, f"{type(e).__name__}: {e}"))

    td = Path(tempfile.mkdtemp(prefix="cosmos_orc_boot_"))
    root = install(td / "live", tree_id="spike-orc-boot")
    paths = CosmosPaths(root)

    snap0 = inspect_boot(paths)
    check("empty store is NO_SEED and GET does not mkdir running file",
          lambda: snap0["kind"] == "NO_SEED"
          and snap0["seed"] == "ABSENT"
          and not (paths.role("state") / RUNNING_SESSION_NAME).exists())

    bad = False
    try:
        _pin_stream("not-a-stream")
    except OrcBootError as e:
        bad = e.kind == "BAD_STREAM"
    check("unknown stream REFUSED", lambda: bad)

    from cosmos_kernel import Kernel
    k = Kernel(root, worker="orc-boot-selftest")
    rec = boot(k, "Cm", repo=REPO)
    check("NO_SEED recovers via TidyUP reconstruct then start",
          lambda: rec.get("recovered") is True
          and rec.get("started") is True
          and rec.get("kind") == "STARTED"
          and rec.get("stream") == "Cm")

    snap1 = inspect_boot(paths)
    check("after boot SEED is PRESENT (GOOD_CLOSE or still STARTED files)",
          lambda: snap1["seed"] == "PRESENT" and snap1["decl"] == "PRESENT")

    again = False
    try:
        boot(k, "Cm", repo=REPO)
    except OrcBootError as e:
        again = e.kind == "ALREADY_OPEN"
    if not again:
        rec2 = None
        try:
            rec2 = boot(k, "Cm", repo=REPO)
        except OrcBootError:
            rec2 = None
        check("second boot while Core session open is ALREADY_LIVE not a second inject",
              lambda: rec2 is not None and rec2.get("kind") == "ALREADY_LIVE")
    else:
        check("second boot while Core session open is ALREADY_LIVE not a second inject",
              lambda: True)

    run = paths.role("state") / RUNNING_SESSION_NAME
    run.write_text('schema = "cosmos-running-session/1"\nstate = "partial"\n',
                   encoding="utf-8")
    import os
    import time
    later = time.time() + 5
    os.utime(run, (later, later))
    snap_p = inspect_boot(paths)
    check("running file newer than SEED is PARTIAL",
          lambda: snap_p["kind"] == "PARTIAL" and snap_p["running_newer"] is True)

    failed = [(l, e) for l, ok, e in results if not ok]
    for label, ok, err in results:
        print(("PASS" if ok else "FAIL"), label, err)
    print("orc_boot selftest", "%d/%d" % (len(results) - len(failed), len(results)))
    return 1 if failed else 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        raise SystemExit(_selftest())
    print("usage: py -3.14 cosmos\\cosmos_orc_boot.py --selftest")
    raise SystemExit(2)
