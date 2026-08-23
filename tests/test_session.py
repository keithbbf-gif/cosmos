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
                            SEED_NAME, SEED_DECL_NAME, SEED_SCHEMA)
from cosmos_validate import write_declared

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


def _write_seed_bytes(seed_path: Path, decl_path: Path, payload: bytes) -> None:
    decl = write_declared(seed_path, payload)
    write_declared(decl_path, json.dumps(
        {"len": decl["len"], "sha": decl["sha"], "schema": SEED_SCHEMA},
        indent=1, sort_keys=True).encode("utf-8"))


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
    check("close_session wrote a declaration sidecar (bytes-declared)",
          lambda: k.paths.role("state", SEED_DECL_NAME).is_file())
    body = json.loads(seed.read_text(encoding="utf-8"))
    check("seed captures inherited facts (repo + lane)",
          lambda: body["facts"]["repo"] == "keithbbf-gif/cosmos"
          and body["facts"]["lane"] == "f5")
    check("seed captures open watchers + handoff via boot_inherit",
          lambda: body["watchers"]["w-grok"] == "grok stage 4 return"
          and body["handoff"] == "s2")
    check("seed names itself a COSMOS_SEED with the schema",
          lambda: body["kind"] == "COSMOS_SEED" and body["schema"] == SEED_SCHEMA)
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
          and ctx["stream"] == "pb" and ctx["sid"] == "s2")
    check("start left SESSION_SEED_INJECTED on the ledger",
          lambda: any(r["event"] == "SESSION_SEED_INJECTED" for r in k.ledger.verify()))
    check("module-level start_session is the manager (facts already injected)",
          lambda: start_session is not None and sm.session._facts["lane"] == "f5")

    # clean the inherited watcher so later closes do not need force
    sm.session.resolve_watcher("w-grok", "landed")
    sm.close_session(handoff_to="s3")

    # ================= POSITIVE: facts survive a process-shaped restart =============
    # Record on kernel A, drop the object (no close), TidyUP on kernel B.
    k.sessions.open("s-recon", "pb")
    k.sessions.session.record_fact("carried", "across-process")
    k2 = Kernel(root, worker="sess-b")
    recon_seed = k2.sessions.close_session(handoff_to="s-recon-next")
    recon_body = json.loads(recon_seed.read_text(encoding="utf-8"))
    check("TidyUP on a new kernel reconstructs unclosed FACT_RECORDED into the seed",
          lambda: recon_body["facts"]["carried"] == "across-process"
          and recon_body["facts"]["repo"] == "keithbbf-gif/cosmos")
    recon_ctx = k2.sessions.start_session("pb")
    check("start after reconstructed close still carries the fact",
          lambda: recon_ctx["facts"]["carried"] == "across-process"
          and k2.sessions.session._facts["carried"] == "across-process")
    k2.sessions.close_session(handoff_to="s4")

    # inherit-only close (no in-memory session) still writes a seed
    seed2 = close_session(k2, handoff_to="next")
    check("close with no open session still writes a seed from boot_inherit",
          lambda: seed2.is_file()
          and json.loads(seed2.read_text(encoding="utf-8"))["facts"]["repo"]
          == "keithbbf-gif/cosmos")

    # ================= NEGATIVE: typed refusals BY KIND =================
    check("start with empty stream -> BAD_STREAM",
          expect(SessionError, "BAD_STREAM")(lambda: k2.sessions.start_session("")))
    check("start with whitespace stream -> BAD_STREAM",
          expect(SessionError, "BAD_STREAM")(lambda: k2.sessions.start_session("   ")))

    seed_path = k2.paths.role("state", SEED_NAME)
    decl_path = k2.paths.role("state", SEED_DECL_NAME)

    parked = seed_path.with_name("SEED.json.parked")
    seed_path.rename(parked)
    check("start without a seed -> NO_SEED",
          expect(SessionError, "NO_SEED")(lambda: k2.sessions.start_session("pb")))
    parked.rename(seed_path)

    parked_decl = decl_path.with_name("SEED.decl.json.parked")
    decl_path.rename(parked_decl)
    check("start with seed but no declaration sidecar -> BAD_SEED",
          expect(SessionError, "BAD_SEED")(lambda: k2.sessions.start_session("pb")))
    parked_decl.rename(decl_path)

    good = seed_path.read_bytes()
    seed_path.write_bytes(good + b"\n")          # bytes change, declaration does not
    check("tampered seed (declared hash disagrees) -> BAD_SEED",
          expect(SessionError, "BAD_SEED")(lambda: k2.sessions.start_session("pb")))

    _write_seed_bytes(seed_path, decl_path, b"{ torn")
    check("torn seed with matching declaration -> BAD_SEED",
          expect(SessionError, "BAD_SEED")(lambda: k2.sessions.start_session("pb")))

    _write_seed_bytes(seed_path, decl_path,
                      json.dumps(["not", "a", "seed"]).encode("utf-8"))
    check("seed that parses but is not a COSMOS_SEED -> BAD_SEED",
          expect(SessionError, "BAD_SEED")(lambda: k2.sessions.start_session("pb")))

    # restore a valid seed so later CLI start works
    _write_seed_bytes(seed_path, decl_path, good)

    k2.sessions.open("live-a", "pb")
    check("open a second live session -> ALREADY_OPEN",
          expect(SessionError, "ALREADY_OPEN")(lambda: k2.sessions.open("live-b", "pb")))
    k2.sessions.close_session(handoff_to="next")

    # torn sentinel: TidyUP must refuse UNPARSEABLE (parse-and-validate, not parse-only)
    sent = root / ".cosmos-root.json"
    sent_ok = sent.read_text(encoding="utf-8")
    sent.write_text("{ torn-sentinel", encoding="utf-8")
    check("close with torn sentinel -> UNPARSEABLE",
          expect(SessionError, "UNPARSEABLE")(lambda: k2.sessions.close_session()))
    sent.write_text(json.dumps({"system": "NOT-COSMOS", "tree_id": "x"}), encoding="utf-8")
    check("close with wrong-identity sentinel -> IDENTITY_MISMATCH",
          expect(SessionError, "IDENTITY_MISMATCH")(lambda: k2.sessions.close_session()))
    sent.write_text(sent_ok, encoding="utf-8")

    rec = root / "config" / "install_record.json"
    rec_ok = rec.read_text(encoding="utf-8")
    rec.write_text(json.dumps({"root": str(root), "tree_id": "OTHER-TREE"}),
                   encoding="utf-8")
    check("close with install-record tree_id mismatch -> IDENTITY_MISMATCH",
          expect(SessionError, "IDENTITY_MISMATCH")(lambda: k2.sessions.close_session()))
    rec_parked = rec.with_name("install_record.json.parked")
    rec.rename(rec_parked)
    check("close with missing install record -> NOT_FOUND",
          expect(SessionError, "NOT_FOUND")(lambda: k2.sessions.close_session()))
    rec_parked.rename(rec)
    rec.write_text(rec_ok, encoding="utf-8")

    extra = root / "config" / "extra_control.json"
    extra.write_text("{ torn-extra", encoding="utf-8")
    check("close with torn extra config JSON -> UNPARSEABLE",
          expect(SessionError, "UNPARSEABLE")(lambda: k2.sessions.close_session()))
    extra.write_text(json.dumps({"ok": True}), encoding="utf-8")

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

    # Windows-only: seed is written through write_declared -> extended().
    if os.name == "nt":
        from cosmos_paths import extended
        check("Windows: seed is readable via extended() (MAX_PATH-safe write path)",
              lambda: Path(extended(seed_path)).is_file()
              and "keithbbf-gif/cosmos" in Path(extended(seed_path)).read_text(
                  encoding="utf-8"))
    else:
        RESULTS.append(("Windows: seed is readable via extended() (MAX_PATH-safe write path)",
                        True, "SKIPPED-NON-NATIVE"))

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
