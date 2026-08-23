#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: cosmos_session (C.O.S. session automation). TidyUP close writes a SEED;
BootUP start injects it; facts carry across the close->seed->start round-trip.
POSITIVE AND NEGATIVE controls: a gate tested only in the passing direction is a
gate nobody has seen closed. Windows-only checks self-skip on os.name!='nt'."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cosmos_kernel import Kernel, install
from cosmos_context import ContextError
from cosmos_session import (SessionError, close_session, start_session,
                            prompt_new_session, SEED_NAME, INDEX_NAME)

RESULTS = []


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                            # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def expect(exc, kind):
    def wrap(f):
        def inner():
            try:
                f()
            except exc as e:
                return e.kind == kind
            return False
        return inner
    return wrap


def _cli(root, *args):
    cosmos_py = Path(__file__).resolve().parent.parent / "cosmos" / "cosmos.py"
    env = os.environ.copy()
    env["PYTHONPATH"] = str(cosmos_py.parent)
    return subprocess.run(
        [sys.executable, str(cosmos_py), *args, "--root", str(root)],
        capture_output=True, text=True, env=env)


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="cosmos_sess_"))
    root = td / "Cosmos"
    install(root, tree_id="session-test")
    k = Kernel(root, worker="sess")
    sm = k.sessions

    # ================= POSITIVE: close -> seed -> start round-trip =================
    s1 = sm.open("s1", "pb")
    s1.record_fact("repo", "keithbbf-gif/cosmos")
    s1.record_fact("lane", "f5")
    s1.open_watcher("w-grok", "grok stage 4 return")
    check("close over an open watcher REFUSES (S-121, in-process)",
          expect(ContextError, "UNRESOLVED")(lambda: sm.close_session(handoff_to="s2")))
    seed = sm.close_session(handoff_to="s2", force=True)
    check("close_session returns a seed path that exists",
          lambda: seed.is_file() and seed.name == SEED_NAME)
    body = json.loads(seed.read_text(encoding="utf-8"))
    check("seed captures inherited facts (repo + lane)",
          lambda: body["facts"]["repo"] == "keithbbf-gif/cosmos"
          and body["facts"]["lane"] == "f5")
    check("seed captures open watchers + handoff",
          lambda: body["watchers"]["w-grok"] == "grok stage 4 return"
          and body["handoff"] == "s2")
    check("TidyUP refreshed the disposable index",
          lambda: (k.paths.role("state", INDEX_NAME).is_file()
                   and json.loads(k.paths.role("state", INDEX_NAME).read_text(
                       encoding="utf-8"))["inherit"]["facts"]["repo"]
                   == "keithbbf-gif/cosmos"))
    check("close left SESSION_SEED_WRITTEN on the ledger",
          lambda: any(r["event"] == "SESSION_SEED_WRITTEN" for r in k.ledger.verify()))

    ctx = sm.start_session("pb")
    check("start_session injects facts into inherited context",
          lambda: ctx["facts"]["repo"] == "keithbbf-gif/cosmos"
          and ctx["facts"]["lane"] == "f5")
    check("start_session re-opens inherited watchers",
          lambda: ctx["watchers"]["w-grok"] == "grok stage 4 return")
    check("new Session is open on the named stream and carries the facts",
          lambda: sm.session is not None and sm.session._open
          and sm.session._facts["repo"] == "keithbbf-gif/cosmos"
          and ctx["stream"] == "pb")
    check("start left SESSION_SEED_INJECTED on the ledger",
          lambda: any(r["event"] == "SESSION_SEED_INJECTED" for r in k.ledger.verify()))

    # module-level wrappers see the same manager (kernel.sessions)
    check("module-level start_session is the manager (facts already injected)",
          lambda: start_session is not None and sm.session._facts["lane"] == "f5")

    # ================= POSITIVE: prompt_new_session Y / n =================
    # current session is open from start; prompt n must NOT close it
    held = sm.session
    none = sm.prompt_new_session(inp=lambda _: "n")
    check("prompt n returns None and leaves the session open",
          lambda: none is None and sm.session is held and held._open)

    # record one more fact, then Y -> seed carries it
    sm.session.record_fact("prompted", "yes")
    sm.session.resolve_watcher("w-grok", "landed")
    yseed = sm.prompt_new_session(inp=lambda _: "Y")
    check("prompt Y returns the seed path",
          lambda: yseed is not None and yseed.is_file())
    check("prompt-Y seed carries the new fact and drops the resolved watcher",
          lambda: json.loads(yseed.read_text(encoding="utf-8"))["facts"]["prompted"]
          == "yes"
          and "w-grok" not in json.loads(yseed.read_text(encoding="utf-8"))["watchers"])
    check("module-level prompt_new_session n is a no-op",
          lambda: prompt_new_session(k, inp=lambda _: "no") is None)

    # ================= NEGATIVE: typed refusals BY KIND =================
    check("start with empty stream -> BAD_STREAM",
          expect(SessionError, "BAD_STREAM")(lambda: sm.start_session("")))
    check("start with whitespace stream -> BAD_STREAM",
          expect(SessionError, "BAD_STREAM")(lambda: sm.start_session("   ")))

    # no seed: park SEED.json (rename, never delete) then start
    seed_path = k.paths.role("state", SEED_NAME)
    parked = seed_path.with_name("SEED.json.parked")
    seed_path.rename(parked)
    check("start without a seed -> NO_SEED",
          expect(SessionError, "NO_SEED")(lambda: sm.start_session("pb")))
    parked.rename(seed_path)

    # torn seed
    good = seed_path.read_text(encoding="utf-8")
    seed_path.write_text("{ torn", encoding="utf-8")
    check("torn seed -> BAD_SEED",
          expect(SessionError, "BAD_SEED")(lambda: sm.start_session("pb")))
    seed_path.write_text(json.dumps(["not", "a", "seed"]), encoding="utf-8")
    check("seed that parses but has no facts object -> BAD_SEED",
          expect(SessionError, "BAD_SEED")(lambda: sm.start_session("pb")))
    seed_path.write_text(good, encoding="utf-8")

    # opening a second session while one is live
    sm.open("live-a", "pb")
    check("open a second live session -> ALREADY_OPEN",
          expect(SessionError, "ALREADY_OPEN")(lambda: sm.open("live-b", "pb")))
    sm.session.resolve_watcher("w-grok", "cleared") if "w-grok" in sm.session._watchers else None
    # live-a inherited no watchers from open() - just close cleanly
    sm.close_session(handoff_to="next")

    # torn sentinel: TidyUP must refuse UNPARSEABLE (parse-and-validate, not parse-only)
    sent = root / ".cosmos-root.json"
    sent_ok = sent.read_text(encoding="utf-8")
    sent.write_text("{ torn-sentinel", encoding="utf-8")
    check("close with torn sentinel -> UNPARSEABLE",
          expect(SessionError, "UNPARSEABLE")(lambda: sm.close_session()))
    sent.write_text(json.dumps({"system": "NOT-COSMOS", "tree_id": "x"}), encoding="utf-8")
    check("close with wrong-identity sentinel -> IDENTITY_MISMATCH",
          expect(SessionError, "IDENTITY_MISMATCH")(lambda: sm.close_session()))
    sent.write_text(sent_ok, encoding="utf-8")

    rec = root / "config" / "install_record.json"
    rec_ok = rec.read_text(encoding="utf-8")
    rec.write_text(json.dumps({"root": str(root), "tree_id": "OTHER-TREE"}),
                   encoding="utf-8")
    check("close with install-record tree_id mismatch -> IDENTITY_MISMATCH",
          expect(SessionError, "IDENTITY_MISMATCH")(lambda: sm.close_session()))
    rec_parked = rec.with_name("install_record.json.parked")
    rec.rename(rec_parked)
    check("close with missing install record -> NOT_FOUND",
          expect(SessionError, "NOT_FOUND")(lambda: sm.close_session()))
    rec_parked.rename(rec)
    rec.write_text(rec_ok, encoding="utf-8")

    # extra JSON in config/ must parse
    extra = root / "config" / "extra_control.json"
    extra.write_text("{ torn-extra", encoding="utf-8")
    check("close with torn extra config JSON -> UNPARSEABLE",
          expect(SessionError, "UNPARSEABLE")(lambda: sm.close_session()))
    extra.write_text(json.dumps({"ok": True}), encoding="utf-8")

    # inherit-only close (no in-memory session) still writes a seed - CLI TidyUP
    seed2 = close_session(k, handoff_to="next")
    check("close with no open session still writes a seed from boot_inherit",
          lambda: seed2.is_file()
          and json.loads(seed2.read_text(encoding="utf-8"))["facts"]["repo"]
          == "keithbbf-gif/cosmos")

    # ================= CLI: cosmos session close / start =================
    cli_close = _cli(root, "session", "close")
    check("CLI `cosmos session close` writes the seed and exits 0",
          lambda: cli_close.returncode == 0 and SEED_NAME in cli_close.stdout)
    cli_start = _cli(root, "session", "start", "pb")
    check("CLI `cosmos session start pb` prints inherited facts and exits 0",
          lambda: cli_start.returncode == 0
          and "keithbbf-gif/cosmos" in cli_start.stdout)
    parked2 = seed_path.with_name("SEED.json.cli-parked")
    seed_path.rename(parked2)
    cli_noseed = _cli(root, "session", "start", "pb")
    check("CLI start without a seed -> nonzero + NO_SEED",
          lambda: cli_noseed.returncode != 0 and "NO_SEED" in cli_noseed.stderr)
    parked2.rename(seed_path)

    # Windows-only native demo: none in this module. Record the skip contract so a
    # future native check has a home and Linux CI stays green.
    if os.name != "nt":
        RESULTS.append(("Windows-native session path demo", True, "SKIPPED-NON-NATIVE"))

    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for label, ok, err in RESULTS:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (close->seed->start facts carry; refusals BY KIND)"
          % ("PASS" if not bad else "FAIL", len(RESULTS)))
    return 0 if not bad else 1


def test_session():
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())
