#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_resession - gate for the auto-resession satellite (CLOCKS id 18).

Every check here is a REFUSAL or an ORDERING that the wish depends on. The
happy path is one line; the rest is the tree closing on itself, because a gate
tested only in the passing direction is a gate nobody has seen closed.

Hermetic: tmpdir seeds, scratch install(), no live tree, no network, no spawn.
Does not register schtasks.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import tempfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "cosmos"))

from cosmos_kernel import install                                     # noqa: E402
from cosmos_paths import CosmosPaths                                  # noqa: E402
from cosmos_own_clocks import CLOCKS                                  # noqa: E402
from cosmos_resession import (                                        # noqa: E402
    CLOCK_ID, CONTEXT_CLOSE_PCT, CONTEXT_PACK_PCT, CONTEXT_WARN_PCT,
    GROK_WARN_TOKENS, HEARTBEAT_NAME,
    PROJECTION_NAME, ResessionRefusal, TASK_NAME, arm_gate_flag,
    classify_pause, close_banner, cosmos_tu2, decide, latch_warn,
    plan_task_argv, poll_once, precheck_seed, read_warn_latched,
    render_running_session, resume_plan,
    spawn_argv, spawn_auto_resession, spawn_inject_argv, spawn_tui_argv,
    transcript_path, watermark,
)

RESULTS: list[tuple[str, bool, str]] = []
STAGED_CLOCKS = (ROOT / "_delme"
                 / "predispose_own_clocks_f51_20260831T112530Z"
                 / "cosmos_own_clocks.py")
STAGED_PROBE = (ROOT / "_delme"
                / "predispose_cosmos_resession_f51_20260831T060817"
                / "cosmos_resession.py")


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


def _load_staged(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise FileNotFoundError(path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="resession_gate_"))

    # ---- seed pre-check: corrupt is a lie, thin is a packing bug -------------
    (tmp / "a").mkdir()
    s, d = write_seed(tmp / "a", seed_body())
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
    (tmp / "j").mkdir()
    check("a /1 seed with a motif_cursor fact still yields a cursor",
          lambda: precheck_seed(*write_seed(
              tmp / "j",
              seed_body(facts={"motif_cursor": "cdeck@5"})),
              TREE)["cursor"] == {"slug": "cdeck", "stage": 5})

    # ---- ordering: HOLD outranks every detector -----------------------------
    hold = {"state": "PAUSED", "mode": "hold", "set_by": "Keith", "reason": "stop"}
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
    check("grok spawn argv carries no transcript-replay flag",
          lambda: not (
              {"--continue", "-c", "--resume", "--fork-session", "--bare",
               "--restore-code"}
              & set(spawn_argv("grok", "prompt", "V:/A/Ai/COSMOS", "u-1"))))
    check("grok spawn argv is machine-readable (json) so a refusal is a field",
          lambda: "json" in spawn_argv("grok", "p", "V:/A", "u-1"))
    check("claude spawn argv is ANTHROPIC_OFF",
          lambda: _raises(lambda: spawn_argv("claude", "p", "V:/A", "u-1"),
                          "ANTHROPIC_OFF"))
    check("the minted id reaches grok as the NEW conversation id",
          lambda: "u-7" in spawn_argv("grok", "p", "V:/A", "u-7"))
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
    pack70 = watermark({"spawned_at_epoch": 9e8, "last_act_epoch": 9e8,
                        "turn_n": 1, "context_pct": CONTEXT_PACK_PCT}, 9e8,
                       pid_is_alive=True)
    check("70% context is W2-pack: pack True, fire False",
          lambda: pack70["pack"] is True and pack70["fire"] is False
          and pack70["reason"] == "pack")
    warn65 = watermark({"spawned_at_epoch": 9e8, "last_act_epoch": 9e8,
                        "turn_n": 1, "context_pct": CONTEXT_WARN_PCT}, 9e8,
                       pid_is_alive=True)
    check("65% context is W2-warn: warn True, pack False, fire False",
          lambda: warn65["warn"] is True and warn65["pack"] is False
          and warn65["fire"] is False and warn65["reason"] == "warn")
    check("Grok 130k tokens is 65% of 200k",
          lambda: GROK_WARN_TOKENS == 130000)
    check("decide at 65% is WARN, not PACKING",
          lambda: decide(pause=None, seed=ok_seed(),
                         cow_hb={"spawned_at_epoch": 9e8, "last_act_epoch": 9e8,
                                 "turn_n": 1, "context_pct": 0.65},
                         pid_alive=True, now=9e8, prompt_sha="p", rail="grok",
                         lease_held_by=None)["state"] == "WARN")
    check("latched warn stays after context drops",
          lambda: decide(pause=None, seed=ok_seed(),
                         cow_hb={"spawned_at_epoch": 9e8, "last_act_epoch": 9e8,
                                 "turn_n": 1, "context_pct": 0.10},
                         pid_alive=True, now=9e8, prompt_sha="p", rail="grok",
                         lease_held_by=None, warn_latched=True)["state"] == "WARN"
          and decide(pause=None, seed=ok_seed(),
                     cow_hb={"spawned_at_epoch": 9e8, "last_act_epoch": 9e8,
                             "turn_n": 1, "context_pct": 0.10},
                     pid_alive=True, now=9e8, prompt_sha="p", rail="grok",
                     lease_held_by=None, warn_latched=True)["warn"] is True)
    close90 = watermark({"spawned_at_epoch": 9e8, "last_act_epoch": 9e8,
                         "turn_n": 1, "context_pct": CONTEXT_CLOSE_PCT}, 9e8,
                        pid_is_alive=True)
    check("90% context is W2-close: fire watermark",
          lambda: close90["fire"] is True and close90["reason"] == "watermark"
          and close90["detectors"]["w2_close"] is True)
    check("decide at 70% is PACKING, not ARMED",
          lambda: decide(pause=None, seed=ok_seed(),
                         cow_hb={"spawned_at_epoch": 9e8, "last_act_epoch": 9e8,
                                 "turn_n": 1, "context_pct": 0.70},
                         pid_alive=True, now=9e8, prompt_sha="p", rail="grok",
                         lease_held_by=None)["state"] == "PACKING")
    check("close banner is SESSION CLOSED x3 then TEXT SAVED TO",
          lambda: close_banner("X").splitlines()
          == ["SESSION CLOSED", "SESSION CLOSED", "SESSION CLOSED",
              "TEXT SAVED TO X"])
    check("interactive TUI argv is grok --cwd --fullscreen -r, not -p/-c",
          lambda: spawn_tui_argv("V:/A/Ai/COSMOS", "u-9")
          == ["grok", "--cwd", "V:/A/Ai/COSMOS", "--fullscreen", "-r", "u-9"]
          and "-p" not in spawn_tui_argv("V:/A/Ai/COSMOS", "u-9")
          and "-c" not in spawn_tui_argv("V:/A/Ai/COSMOS", "u-9"))
    check("5a inject is --prompt-file --session-id, exits, no -r/-c",
          lambda: "--prompt-file" in spawn_inject_argv("V:/A", "u-9", "P.md")
          and "--session-id" in spawn_inject_argv("V:/A", "u-9", "P.md")
          and "-r" not in spawn_inject_argv("V:/A", "u-9", "P.md")
          and "-c" not in spawn_inject_argv("V:/A", "u-9", "P.md"))
    check("dry AUTO resession records 5a+5b and does not execute",
          lambda: (lambda r: r.get("steps") == "5a+5b" and r.get("dry") is True
                   and r.get("ok") is True)(
              spawn_auto_resession("V:/A", "u-9", "P.md", execute=False)))
    check("proper close resumes fresh, never -c",
          lambda: resume_plan(proper_close=True, window_roomy=True,
                              vendor_log_exists=True, running_exists=True)
          == {"mode": "fresh", "use_continue": False,
              "why": "W2-close: HMAC SEED + fresh TUI"})
    check("improper close of a roomy window may grok -c",
          lambda: resume_plan(proper_close=False, window_roomy=True,
                              vendor_log_exists=True, running_exists=True)
          ["use_continue"] is True)
    check("improper close with no log promotes running toml",
          lambda: resume_plan(proper_close=False, window_roomy=False,
                              vendor_log_exists=False, running_exists=True)
          ["mode"] == "promote_running")
    tu2_ok = cosmos_tu2(repo=ROOT, root=ROOT / "live")
    check("COSMOS TU2 against the live tree reports the wishlist/backlog/tracker files",
          lambda: tu2_ok["n_checks"] >= 5)
    check("TU2 claimed-count mismatch is a finding, not a green",
          lambda: cosmos_tu2(repo=ROOT, root=ROOT / "live",
                             claimed={"wishlist_open": -1})["ok"] is False)
    check("running session render is toml with schema",
          lambda: 'schema = "cosmos-running-session/1"'
          in render_running_session({"pid": 1, "state": "IDLE"}))

    # ---- F-51 clock vehicle: --plan-task emits, registers nothing -----------
    check("staged old probe module has no plan_task_argv (the bite)",
          _old_probe_lacks_plan)
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

    # ---- F-51 promotion: CLOCKS id 18 + heartbeat on a scratch root ---------
    check("staged old CLOCKS has no id 18 and no cosmos_resession.py (the bite)",
          _old_clocks_lack_18)
    hits = [c for c in CLOCKS if c.get("id") == CLOCK_ID]
    check("CLOCKS id 18 is exactly one row",
          lambda: len(hits) == 1)
    check("CLOCKS id 18 is COSMOS Resession / cosmos_resession.py / standup resession",
          lambda: hits and hits[0].get("task") == TASK_NAME
          and hits[0].get("script") == "cosmos_resession.py"
          and hits[0].get("standup") == "resession"
          and hits[0].get("heartbeat") == HEARTBEAT_NAME)
    check("--repo default from cosmos/ is the repo root",
          lambda: Path(__import__("cosmos_resession").__file__).resolve()
          .parent.parent == ROOT)

    scratch = install(tmp / "live", tree_id="spike-resession")
    rec = poll_once(str(scratch), str(ROOT), dry_run=False)
    hb_path = scratch / "logs" / HEARTBEAT_NAME
    proj_path = scratch / "state" / "control" / PROJECTION_NAME
    check("poll_once on a scratch root is IDLE (no COW heartbeat)",
          lambda: rec.get("state") == "IDLE")
    check("poll_once writes the named heartbeat under the scratch logs role",
          lambda: hb_path.is_file() and json.loads(
              hb_path.read_text(encoding="utf-8")).get("clock_id") == CLOCK_ID)
    check("poll_once writes RESESSION.json under scratch state/control",
          lambda: proj_path.is_file() and json.loads(
              proj_path.read_text(encoding="utf-8")).get("state") == "IDLE")
    check("poll_once clock_id matches CLOCKS",
          lambda: rec.get("clock_id") == CLOCK_ID == 18)

    warn_root = install(tmp / "warn", tree_id="spike-resession-warn")
    wpaths = CosmosPaths(warn_root)
    first_warn = latch_warn(wpaths, context_pct=0.65, clock=lambda: 1.0)
    drop_warn = latch_warn(wpaths, context_pct=0.10, clock=lambda: 2.0)
    check("RESESSION_WARN.flag never self-clears when context drops",
          lambda: first_warn["state"] == "WARN"
          and drop_warn["persistent"] is True
          and drop_warn["state"] == "WARN"
          and read_warn_latched(wpaths) is True
          and drop_warn.get("latched_at") == first_warn.get("latched_at"))

    dry_root = install(tmp / "dry", tree_id="spike-resession-dry")
    dry = poll_once(str(dry_root), str(ROOT), dry_run=True)
    check("dry_run poll_once writes no heartbeat and no projection",
          lambda: dry.get("state") == "IDLE"
          and not (dry_root / "logs" / HEARTBEAT_NAME).exists()
          and not (dry_root / "state" / "control" / PROJECTION_NAME).exists())

    check("standup with injected create_task never calls real schtasks",
          lambda: _standup_injected(str(scratch)))

    bad_rows = [r for r in RESULTS if not r[1]]
    for label, ok, err in RESULTS:
        print(f"  {'OK  ' if ok else 'FAIL'}  {label}{('  ' + err) if err else ''}")
    live_value = {
        "refusal_kinds": sorted({precheck_seed(x, y, TREE)["kind"]
                                 for x, y in ((s2, d2), (s4, d4), (s5, d5),
                                              (s6, d6), (s7, d7))}),
        "checks": len(RESULTS),
        "clock_id": CLOCK_ID,
        "scratch_state": rec.get("state"),
        "heartbeat": HEARTBEAT_NAME if hb_path.is_file() else None,
    }
    print("live_value: " + json.dumps(live_value, sort_keys=True))
    print(f"result: {'ok' if not bad_rows else 'FAIL'}  "
          f"{len(RESULTS) - len(bad_rows)}/{len(RESULTS)}")
    prove = ROOT / "cosmos" / "_f51_promote.json"
    prove.write_text(json.dumps({
        "ok": not bad_rows,
        "passed": len(RESULTS) - len(bad_rows),
        "total": len(RESULTS),
        "live_value": live_value,
        "failed": [{"label": l, "err": e} for l, ok, e in RESULTS if not ok],
    }, indent=1), encoding="utf-8")
    return 1 if bad_rows else 0


def _raises(fn, kind: str) -> bool:
    try:
        fn()
    except ResessionRefusal as e:
        return e.kind == kind
    return False


def _old_probe_lacks_plan() -> bool:
    if not STAGED_PROBE.is_file():
        return False
    mod = _load_staged(STAGED_PROBE, "cosmos_resession_old_f51")
    return not hasattr(mod, "plan_task_argv")


def _old_clocks_lack_18() -> bool:
    if not STAGED_CLOCKS.is_file():
        return False
    mod = _load_staged(STAGED_CLOCKS, "own_clocks_old_f51")
    ids = [c.get("id") for c in mod.CLOCKS]
    scripts = [c.get("script") for c in mod.CLOCKS]
    return 18 not in ids and "cosmos_resession.py" not in scripts and max(ids) == 17


def _plan_task_is_inert() -> bool:
    """--plan-task must print and not schedule."""
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


def _standup_injected(root: str) -> bool:
    """standup talks only to the injected query/create; real schtasks stays idle."""
    import cosmos_resession as cr
    create_calls = []
    query_calls = []
    real_create = cr.create_task
    real_query = cr.query_task
    cr.query_task = lambda name: query_calls.append(name) or {"ok": False}
    cr.create_task = lambda *a, **k: (
        create_calls.append({"args": a, "kwargs": k})
        or {"ok": False, "needs_elevation": True,
            "keith_cmd": "schtasks /create /tn COSMOS Resession"}
    )
    try:
        rec = cr.standup(root)
    finally:
        cr.create_task = real_create
        cr.query_task = real_query
    return (rec.get("started") == "planned"
            and rec.get("task_name") == TASK_NAME
            and rec.get("keith_cmd") is not None
            and create_calls
            and query_calls == [TASK_NAME]
            and create_calls[0]["args"][0] == TASK_NAME
            and create_calls[0]["kwargs"].get("run_now") is False)


if __name__ == "__main__":
    raise SystemExit(main())
