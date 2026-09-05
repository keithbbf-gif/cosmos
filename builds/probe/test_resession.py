#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_resession - gate for the auto-resession satellite's decision core.

Every check here is a REFUSAL or an ORDERING that the wish depends on. The
happy path is one line; the rest is the tree closing on itself, because a gate
tested only in the passing direction is a gate nobody has seen closed.

Hermetic: tmpdir seeds, no live tree, no network, no spawn.
"""
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from cosmos_resession import (                                        # noqa: E402
    PROMPT_RELPATH, ResessionRefusal, TASK_NAME, arm_gate_flag,
    classify_pause, decide, plan_task_argv, precheck_seed, sha256_file,
    spawn_argv, transcript_path, watermark,
)

RESULTS: list[tuple[str, bool, str]] = []


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                            # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


TREE = "KMesh-COSMOS-live"


def write_seed(dirpath: Path, body: dict, *, mac: str | None = "m",
               break_sha: bool = False, break_len: bool = False,
               no_decl: bool = False) -> tuple[Path, Path]:
    seed = dirpath / "SEED.json"
    decl = dirpath / "SEED.decl.json"
    raw = json.dumps(body, indent=1, sort_keys=True).encode("utf-8")
    seed.write_bytes(raw)
    if no_decl:
        return seed, decl
    d = {"len": len(raw) + (1 if break_len else 0),
         "sha": ("0" * 64) if break_sha else hashlib.sha256(raw).hexdigest()}
    if mac is not None:
        d["mac"] = mac
    decl.write_text(json.dumps(d), encoding="utf-8")
    return seed, decl


def seed_body(**over) -> dict:
    body = {"schema": "cosmos-session-seed/1", "kind": "COSMOS_SEED",
            "tree_id": TREE, "sid": "Cm-9", "facts": {}, "watchers": {},
            "handoff": "Cm", "incidents": [], "closed_epoch": 1.0}
    body.update(over)
    return body


def ok_seed() -> dict:
    return {"ok": True, "kind": None, "detail": "", "sha": "s", "sid": "Cm-9",
            "schema": "cosmos-session-seed/2", "thin": False,
            "cursor": {"slug": "auto-resession", "stage": 4}}


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="resession_gate_"))

    # ---- seed pre-check: corrupt is a lie, thin is a packing bug -------------
    s, d = write_seed(tmp / "a", seed_body()) if (tmp / "a").mkdir() or True else (0, 0)
    check("a MAC-valid thin /1 seed passes the pre-check and is flagged THIN",
          lambda: (lambda r: r["ok"] and r["thin"] and r["kind"] == "SEED_THIN")(
              precheck_seed(s, d, TREE)))
    check("the pre-check reports the real sha of the real bytes",
          lambda: precheck_seed(s, d, TREE)["sha"]
          == hashlib.sha256(s.read_bytes()).hexdigest())

    (tmp / "b").mkdir()
    s2, d2 = write_seed(tmp / "b", seed_body(), break_sha=True)
    check("declared sha != consumed sha is BAD_SEED",
          lambda: precheck_seed(s2, d2, TREE)["kind"] == "BAD_SEED")

    (tmp / "c").mkdir()
    s3, d3 = write_seed(tmp / "c", seed_body(), break_len=True)
    check("declared len != consumed len is BAD_SEED",
          lambda: precheck_seed(s3, d3, TREE)["kind"] == "BAD_SEED")

    (tmp / "e").mkdir()
    s4, d4 = write_seed(tmp / "e", seed_body(), mac=None)
    check("a sidecar with no MAC is BAD_SEED, never 'just unsigned'",
          lambda: precheck_seed(s4, d4, TREE)["kind"] == "BAD_SEED")

    (tmp / "f").mkdir()
    s5, d5 = write_seed(tmp / "f", seed_body(tree_id="KMesh-OTHER"))
    check("another tree's seed is IDENTITY_MISMATCH, not a resume",
          lambda: precheck_seed(s5, d5, TREE)["kind"] == "IDENTITY_MISMATCH")

    (tmp / "g").mkdir()
    s6, d6 = write_seed(tmp / "g", seed_body(), no_decl=True)
    check("a seed with no declaration sidecar is NO_DECL",
          lambda: precheck_seed(s6, d6, TREE)["kind"] == "NO_DECL")
    check("a missing seed is NO_SEED, distinct from a corrupt one",
          lambda: precheck_seed(tmp / "nope.json", d, TREE)["kind"] == "NO_SEED")

    (tmp / "h").mkdir()
    s7, d7 = write_seed(tmp / "h", seed_body(schema="cosmos-session-seed/2",
                                             facts={"motif_cursor": "cvm@4"}))
    check("a /2 seed missing motif/leases/inflight is BAD_SEED (corrupt shape)",
          lambda: precheck_seed(s7, d7, TREE)["kind"] == "BAD_SEED")

    (tmp / "i").mkdir()
    s8, d8 = write_seed(tmp / "i", seed_body(
        schema="cosmos-session-seed/2", facts={"motif_cursor": "cvm@4"},
        motif={"cursor": {"slug": "cvm", "stage": 4}}, leases=[], inflight=[]))
    check("a well-formed /2 seed yields the signed MOTIF cursor",
          lambda: precheck_seed(s8, d8, TREE)["cursor"] == {"slug": "cvm",
                                                            "stage": 4})
    check("a /1 seed with a motif_cursor fact still yields a cursor",
          lambda: precheck_seed(*write_seed(
              (tmp / "j").mkdir() or (tmp / "j"),
              seed_body(facts={"motif_cursor": "cdeck@5"})),
              TREE)["cursor"] == {"slug": "cdeck", "stage": 5})

    # ---- ordering: HOLD outranks every detector -----------------------------
    hold = {"state": "PAUSED", "mode": "hold", "set_by": "Keith", "reason": "stop"}
    check("an unrecognised pause mode (M10 'resumed') fails closed to HOLD "
          "even when set_by=COW and reason contains TidyUP",
          lambda: classify_pause({"state": "PAUSED", "mode": "resumed",
                                  "set_by": "COW",
                                  "reason": "TidyUP + resession"})["class"]
          == "HOLD")
    check("a JSON array flag is HOLD, not AttributeError (round-6b)",
          lambda: classify_pause([])["class"] == "HOLD")
    check("watermark of a list heartbeat is no-fire, not AttributeError (round-8)",
          lambda: watermark([], 0.0)["fire"] is False
          and "heartbeat" in (watermark([], 0.0).get("why") or ""))
    check("watermark of a string heartbeat is no-fire, not AttributeError",
          lambda: watermark("hb", 0.0)["fire"] is False)
    check("a list seed is BAD_SEED REFUSED, not AttributeError (round-8)",
          lambda: (lambda r: r["state"] == "REFUSED"
                   and r["refused_kind"] == "BAD_SEED")(
              decide(pause=None, seed=[], cow_hb=None, pid_alive=False,
                     now=1.0, prompt_sha="p", rail="grok",
                     lease_held_by=None)))
    check("HOLD still outranks a garbage seed (round-8)",
          lambda: decide(pause=hold, seed=[], cow_hb=None, pid_alive=False,
                         now=1.0, prompt_sha="p", rail="grok",
                         lease_held_by=None)["refused_kind"] == "HOLD")
    check("spawn add_dirs string is BAD_DIRS not character --add-dir (round-8)",
          lambda: _raises(lambda: spawn_argv("claude", "p", "V:/A", "u-1",
                                             add_dirs="cwd"),
                          "BAD_DIRS"))
    check("spawn add_dirs None is BAD_DIRS not TypeError",
          lambda: _raises(lambda: spawn_argv("claude", "p", "V:/A", "u-1",
                                             add_dirs=None),
                          "BAD_DIRS"))
    check("arm_gate_flag of a string prev is BAD_FLAG not ValueError",
          lambda: _raises(lambda: arm_gate_flag("hold",
                                                datetime(2026, 1, 1)),
                          "BAD_FLAG"))
    check("a string flag 'hold' is HOLD not ARM — a string is not a flag dict",
          lambda: classify_pause("hold")["class"] == "HOLD")
    check("a boolean flag is HOLD, not AttributeError",
          lambda: classify_pause(True)["class"] == "HOLD")
    check("a TidyUP handoff hold (mode=hold, set_by=COW) is ARM, not operator HOLD",
          lambda: classify_pause({"state": "PAUSED", "mode": "hold",
                                  "set_by": "COW",
                                  "reason": "TidyUP + resession"})["class"]
          == "ARM")
    check("sha256_file of a directory is None (NO_PROMPT input), not a crash",
          lambda: sha256_file(tmp) is None)
    check("an operator HOLD refuses even with a fired watermark and a good seed",
          lambda: (lambda r: r["state"] == "HOLD" and r["refused_kind"] == "HOLD")(
              decide(pause=hold, seed=ok_seed(),
                     cow_hb={"spawned_at_epoch": 1.0, "last_act_epoch": 9e9,
                             "turn_n": 99},
                     pid_alive=True, now=9e9, prompt_sha="p", rail="grok",
                     lease_held_by=None)))
    check("a HOLD decision never proposes a spawn reason",
          lambda: decide(pause=hold, seed=ok_seed(), cow_hb=None, pid_alive=False,
                         now=1.0, prompt_sha="p", rail="grok",
                         lease_held_by=None)["spawn_reason"] is None)

    # ---- ordering: a bad manifest refuses before anything is armed ----------
    bad = {"ok": False, "kind": "BAD_SEED", "detail": "mac", "sha": None,
           "sid": None, "schema": None, "thin": None, "cursor": None}
    check("a fired watermark over a BAD_SEED is REFUSED, not resumed",
          lambda: (lambda r: r["state"] == "REFUSED"
                   and r["refused_kind"] == "BAD_SEED")(
              decide(pause=None, seed=bad, cow_hb=None, pid_alive=False, now=1.0,
                     prompt_sha="p", rail="grok", lease_held_by=None)))
    check("a missing BootUP prompt refuses rather than inventing one at fire time",
          lambda: decide(pause=None, seed=ok_seed(), cow_hb=None, pid_alive=False,
                         now=1.0, prompt_sha=None, rail="grok",
                         lease_held_by=None)["refused_kind"] == "NO_PROMPT")
    check("a held cow lease refuses the second orchestrator",
          lambda: decide(pause=None, seed=ok_seed(), cow_hb=None, pid_alive=False,
                         now=1.0, prompt_sha="p", rail="grok",
                         lease_held_by="resession-42")["refused_kind"] == "HELD")

    armed = decide(pause=None, seed=ok_seed(), cow_hb=None, pid_alive=False,
                   now=1.0, prompt_sha="p", rail="grok", lease_held_by=None)
    check("the happy path arms and carries the signed cursor forward",
          lambda: armed["state"] == "ARMED"
          and armed["resumed_from"] == {"slug": "auto-resession", "stage": 4})
    check("an in-window session is IDLE - the satellite does not churn",
          lambda: decide(pause=None, seed=ok_seed(),
                         cow_hb={"spawned_at_epoch": 999.0,
                                 "last_act_epoch": 1000.0, "turn_n": 1},
                         pid_alive=True, now=1000.0, prompt_sha="p", rail="grok",
                         lease_held_by=None)["state"] == "IDLE")

    # ---- the fresh-window rule, enforced in the argv ------------------------
    for rail in ("grok", "claude"):
        check(f"{rail} spawn argv carries no transcript-replay flag",
              lambda rail=rail: not (
                  {"--continue", "-c", "--resume", "--fork-session", "--bare",
                   "--restore-code"}
                  & set(spawn_argv(rail, "prompt", "V:/A/Ai/COSMOS", "u-1"))))
        check(f"{rail} spawn argv is machine-readable (json) so a refusal is a field",
              lambda rail=rail: "json" in spawn_argv(rail, "p", "V:/A", "u-1"))
    check("the minted id reaches both rails as the NEW conversation id",
          lambda: all("u-7" in spawn_argv(r, "p", "V:/A", "u-7")
                      for r in ("grok", "claude")))
    check("an unknown rail is a typed refusal, not a silent default",
          lambda: _raises(lambda: spawn_argv("cursor", "p", "V:/A", "u"),
                          "NO_RAIL"))
    check("the fresh-window proof is a vendor path keyed by the minted id",
          lambda: transcript_path("claude", "V:/A/Ai/COSMOS", "u-7",
                                  Path("/h")).name == "u-7.jsonl")

    # ---- the armed gate is a bound control ---------------------------------
    flag = arm_gate_flag({"scope": "old"}, datetime(2026, 1, 1, 0, 0, 0))
    check("arming produces mode=resume_gate with auto_resume_at at now+grace",
          lambda: flag["mode"] == "resume_gate"
          and flag["auto_resume_at"] == "2026-01-01T00:00:15")
    check("the armed flag carries the reason and timestamp PAUSE_PROTOCOL requires",
          lambda: bool(flag.get("reason")) and bool(flag.get("set_at")))
    check("arming leaves the flag PAUSED so a paused clock is not a dead one",
          lambda: flag["state"] == "PAUSED")
    check("an already-armed gate is left alone for WD2 to clear",
          lambda: classify_pause(flag)["class"] == "GATE")

    # ---- watermark: engine vs backstop -------------------------------------
    check("the turn watermark reserves TidyUP budget below the dispatch cap",
          lambda: watermark({"spawned_at_epoch": 9e8, "last_act_epoch": 9e8,
                             "turn_n": 40}, 9e8,
                            pid_is_alive=True)["reason"] == "watermark")
    check("a quiet-but-alive COW below the watermark does not fire",
          lambda: watermark({"spawned_at_epoch": 9e8, "last_act_epoch": 9e8,
                             "turn_n": 1}, 9e8,
                            pid_is_alive=True)["fire"] is False)
    check("firing on a live pid is labelled watermark, never quiet",
          lambda: watermark({"spawned_at_epoch": 1.0, "last_act_epoch": 9e8,
                             "turn_n": 99}, 9e8,
                            pid_is_alive=True)["reason"] == "watermark")

    # ---- F-51 clock vehicle: --plan-task emits, registers nothing -----------
    _old_path = (HERE.parents[1] / "_delme"
                 / "predispose_cosmos_resession_f51_20260831T060817"
                 / "cosmos_resession.py")

    def _old_lacks_plan():
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "cosmos_resession_old_f51", _old_path)
        if spec is None or spec.loader is None:
            return False
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return not hasattr(mod, "plan_task_argv")

    check("staged old module has no plan_task_argv (the bite)",
          _old_lacks_plan)
    argv = plan_task_argv(Path("V:/A/Ai/COSMOS/live"))
    check("plan_task_argv is schtasks /create for COSMOS Resession",
          lambda: argv[:4] == ["schtasks", "/create", "/tn", TASK_NAME])
    check("plan_task_argv is minute/1, points at this file, --once, no elevation",
          lambda: ("/sc" in argv and "minute" in argv
                   and "--once" in " ".join(argv)
                   and "cosmos_resession.py" in " ".join(argv)
                   and "/rl" not in argv))
    check("--plan-task registers nothing (subprocess.run is never called)",
          lambda: _plan_task_is_inert())
    check("CLI without --root is NO_ROOT rc=2, never rc=0",
          lambda: _cli_without_root_is_NO_ROOT())

    # ---- P1.3 tracked BootUP prompt (fence-artifact close of F-51 leftover) --
    prompt = HERE.parents[1].joinpath(*PROMPT_RELPATH)
    check("tracked BootUP prompt exists at docs/AUTO_RESESSION_PROMPT.md",
          lambda: prompt.is_file())
    check("sha256_file of the tracked prompt is 64 hex (not null / NO_PROMPT)",
          lambda: (lambda h: isinstance(h, str) and len(h) == 64
                   and all(c in "0123456789abcdef" for c in h))(
              sha256_file(prompt)))
    check("P1.3 prompt names COW, session start, HOLD, P9 and P10",
          lambda: _prompt_carries_p13(prompt))
    check("sha256_file of a missing path is None (the NO_PROMPT input)",
          lambda: sha256_file(prompt.parent / "NO_SUCH_PROMPT.md") is None)
    check("the bite recorded the unfiled prompt before this pin",
          lambda: _bite_recorded_absent())

    bad_rows = [r for r in RESULTS if not r[1]]
    for label, ok, err in RESULTS:
        print(f"  {'OK  ' if ok else 'FAIL'}  {label}{('  ' + err) if err else ''}")
    print("live_value: " + json.dumps(
        {"refusal_kinds": sorted({precheck_seed(x, y, TREE)["kind"]
                                  for x, y in ((s2, d2), (s4, d4), (s5, d5),
                                               (s6, d6), (s7, d7))}),
         "checks": len(RESULTS)}, sort_keys=True))
    print(f"result: {'ok' if not bad_rows else 'FAIL'}  "
          f"{len(RESULTS) - len(bad_rows)}/{len(RESULTS)}")
    return 1 if bad_rows else 0


def _raises(fn, kind: str) -> bool:
    try:
        fn()
    except ResessionRefusal as e:
        return e.kind == kind
    return False


def _cli_without_root_is_NO_ROOT() -> bool:
    """main() prints JSON kind=NO_ROOT on stderr and returns 2. argparse
    does not require --root; the typed refusal is the contract."""
    import io
    from contextlib import redirect_stderr
    import cosmos_resession as cr
    old = sys.argv
    buf = io.StringIO()
    sys.argv = ["cosmos_resession.py", "--once"]
    try:
        with redirect_stderr(buf):
            rc = cr.main()
    finally:
        sys.argv = old
    try:
        rec = json.loads(buf.getvalue())
    except ValueError:
        return False
    return rc == 2 and rec.get("kind") == "NO_ROOT" and rec.get("ok") is False


REQUIRED_PROMPT_PHRASES = (
    "You are COW",
    "session start",
    "BUCm.toml",
    "Never rewrite an operator HOLD",
    "ORCHESTRATOR (P9)",
    "you dispose (P10)",
    "do not run searches in your own context",
    "verified SEED",
)


def _prompt_carries_p13(path: Path) -> bool:
    if not path.is_file():
        return False
    body = path.read_text(encoding="utf-8")
    return all(p in body for p in REQUIRED_PROMPT_PHRASES)


def _bite_recorded_absent() -> bool:
    bite = HERE / "_bite_f51_prompt.json"
    if not bite.is_file():
        return False
    rec = json.loads(bite.read_text(encoding="utf-8"))
    return (rec.get("all_bite") is True
            and rec.get("prompt_exists") is False
            and rec.get("dry_run_prompt_sha") is None
            and rec.get("fire_without_prompt_kind") == "NO_PROMPT")


def _plan_task_is_inert() -> bool:
    """--plan-task must print and not schedule. Root is unused by plan_task_argv."""
    import cosmos_resession as cr
    calls = []
    real = cr.subprocess.run
    cr.subprocess.run = lambda *a, **k: calls.append(a) or real(*a, **k)
    try:
        old = sys.argv
        sys.argv = ["cosmos_resession.py", "--root", "V:/A/Ai/COSMOS/live",
                    "--plan-task"]
        try:
            rc = cr.main()
        finally:
            sys.argv = old
    finally:
        cr.subprocess.run = real
    return rc == 0 and calls == []


if __name__ == "__main__":
    raise SystemExit(main())
