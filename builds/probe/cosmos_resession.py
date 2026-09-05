#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_resession - AUTO-RESESSION satellite (PROBE build; proposed CLOCKS id 18).

WHAT THIS IS
    Layer A (Core :8770, WD2, runner, collector, motif driver) already survives an
    orchestrator death. Layer B - the COW process itself - does not. Nothing in the
    tree spawns the next COW when the current one fills its context window. This
    satellite is that missing piece, and NOTHING else: it detects the Layer-B
    boundary WHILE THE WINDOW STILL HAS ROOM, runs TidyUP through the CLI kernel,
    arms the P3 resume gate, fences on one orchestrator, and spawns a FRESH vendor
    session seeded from the signed SEED.

    It is a satellite in the class of cosmos_watchdog2 / cosmos_motif_driver /
    cosmos_work_order_run. It does NOT edit kernel / ledger / sched / service, and
    it does not restart Core. The live tree stays up through its own modification.

WHY THE AUTHENTICITY CHECK IS NOT DUPLICATED HERE
    cosmos_session.start_session is the single authority for a seed: declared
    len/sha (INTEGRITY), install-key HMAC (AUTHENTICITY), tree_id vs sentinel
    (IDENTITY). Re-implementing that here would be a second key handler and a
    second verifier - the exact bloat P8 forbids. This module does a cheap
    READ-ONLY structural pre-check to refuse early and loudly, then delegates the
    real verification to `cosmos.py session start`, whose SESSION_SEED_INJECTED
    ledger event is the runtime binding. Pre-check refuses cheaply; the authority
    refuses authoritatively.

WHY THE VENDOR SESSION ID IS MINTED, NOT SCRAPED
    The gate's fresh-window proof is `vendor_session_id != prev_vendor_session_id`.
    Capturing it from stdout requires holding the orchestrator's pipe for its whole
    life - which is exactly what a detached satellite must not do. Both rails accept
    a caller-supplied id for a NEW conversation (claude --session-id <uuid>;
    grok --session-id <uuid>, new-only). So the satellite mints it. That alone
    would weaken the gate - a minted uuid proves nothing - so the gate additionally
    requires the VENDOR-WRITTEN TRANSCRIPT for that id to exist and to be newer
    than spawned_at. A uuid the satellite invented plus a transcript only the vendor
    binary can write is a value the pre-satellite tree cannot emit.

    py -3.14 cosmos_resession.py --root <live> --once
    py -3.14 cosmos_resession.py --root <live> --once --dry-run   # decide, write nothing
    py -3.14 cosmos_resession.py --root <live> --loop
    py -3.14 cosmos_resession.py --root <live> --status
    py -3.14 cosmos_resession.py --selftest

PROBE NOTE: this copy lives under builds/probe/ (agent write-fence). The proposed
target is cosmos/cosmos_resession.py, where --repo defaults correctly. Nothing here
writes live/state/control; --dry-run is how the probe was measured.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
import urllib.parse
import uuid
from datetime import datetime, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
for _cand in (HERE, HERE.parent.parent / "cosmos", HERE.parent / "cosmos"):
    if (_cand / "cosmos_paths.py").is_file() and str(_cand) not in sys.path:
        sys.path.insert(0, str(_cand))

WORKER = "cosmos-resession"
SCHEMA = "cosmos-resession/1"
TASK_NAME = "COSMOS Resession"
TASK_NAME_LOGON = "COSMOS Resession Logon"
HEARTBEAT_NAME = "resession_heartbeat.json"
NO_WINDOW = 0x08000000 if os.name == "nt" else 0
PROJECTION_NAME = "RESESSION.json"
COW_HEARTBEAT_NAME = "COW_HEARTBEAT.json"
PAUSE_NAME = "PAUSE.flag"
PROMPT_RELPATH = ("docs", "AUTO_RESESSION_PROMPT.md")
SEED_NAME = "SEED.json"
SEED_DECL_NAME = "SEED.decl.json"

# Named constants, not magic numbers in prose (arch S4).
AUTO_RESUME_GRACE_S = 15.0        # one WD2 Activity Clock cycle
SESSION_AGE_WATERMARK_S = 2700.0  # 45 min: fire while the window still has room
TURN_WATERMARK = 40               # dispatch caps at 60; 20 turns reserved for TidyUP
HEARTBEAT_STALE_S = 180.0         # COW quiet -> W3 backstop, never the engine
COW_LEASE_TTL_S = 600.0

RAILS = ("grok", "claude")


class ResessionRefusal(RuntimeError):
    """kind in {HOLD, NO_SEED, NO_DECL, BAD_SEED, IDENTITY_MISMATCH, NO_PROMPT,
    HELD, CLOSE_REFUSED, NO_RAIL, BAD_DIRS, BAD_FLAG}. Typed and machine-readable:
    a refusal that only stops is forbidden (PAUSE_PROTOCOL) - every one of these
    heartbeats."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


# ---------------------------------------------------------------------------
# pure decision core (no I/O below this line except explicit readers)
# ---------------------------------------------------------------------------

def classify_pause(flag: dict | None) -> dict:
    """H10 - HOLD is sacred; the TidyUP handoff hold is the P3 arming case.

    An operator hold (Keith says stop / mesh boundary / anything this satellite
    cannot prove is a handoff) is NEVER rewritten. Only a COW-written TidyUP
    handoff hold is promoted to resume_gate. Anything unrecognised is HOLD:
    fail-closed means a visible stall beats a wrong resume.
    """
    if flag is None:
        return {"class": "RUNNING", "why": "no PAUSE.flag"}
    if not isinstance(flag, dict):
        return {"class": "HOLD",
                "why": ("unrecognised flag type=%r - fail-closed to HOLD"
                        % type(flag).__name__)}
    if str(flag.get("state", "PAUSED")).upper() == "RUNNING":
        return {"class": "RUNNING", "why": "flag present but state=RUNNING"}
    mode = str(flag.get("mode") or "").strip().lower()
    if mode == "resume_gate":
        return {"class": "GATE", "why": "resume_gate already armed; WD2 owns it"}
    if mode != "hold":
        return {"class": "HOLD",
                "why": f"unrecognised mode={mode!r} - fail-closed to HOLD"}
    set_by = str(flag.get("set_by") or "").strip().lower()
    reason = str(flag.get("reason") or "").lower()
    if set_by in ("cow", "cosmos", "tidyup") and "tidyup" in reason:
        return {"class": "ARM",
                "why": "TidyUP handoff hold (set_by=%s) - P3 arming case" % set_by}
    return {"class": "HOLD",
            "why": "operator hold (set_by=%s) - never rewritten" % (set_by or "?")}


def precheck_seed(seed_path: Path, decl_path: Path, live_tree_id: str) -> dict:
    """READ-ONLY structural pre-check. Not the authority - cosmos.py session start
    is. Returns {ok, kind, detail, sha, sid, schema, thin, cursor}.

    THIN is not CORRUPT. A MAC-valid /1 seed with empty facts is a packing bug to
    surface (SESSION_SEED_THIN) and resume from the tracker; a seed whose bytes do
    not match its declaration is a lie and refuses.
    """
    out = {"ok": False, "kind": None, "detail": "", "sha": None, "sid": None,
           "schema": None, "thin": None, "cursor": None}
    if not seed_path.is_file():
        out.update(kind="NO_SEED", detail=f"no seed at {seed_path}")
        return out
    if not decl_path.is_file():
        out.update(kind="NO_DECL", detail=f"no declaration sidecar at {decl_path}")
        return out
    try:
        decl = json.loads(decl_path.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeDecodeError) as e:
        out.update(kind="BAD_SEED", detail=f"{decl_path}: {e}")
        return out
    if not isinstance(decl, dict) or "len" not in decl or "sha" not in decl:
        out.update(kind="BAD_SEED", detail=f"{decl_path} is not a seed declaration")
        return out
    raw = seed_path.read_bytes()
    if len(raw) != int(decl["len"]):
        out.update(kind="BAD_SEED",
                   detail=f"declared len={decl['len']} consumed={len(raw)}")
        return out
    sha = hashlib.sha256(raw).hexdigest()
    if sha != str(decl["sha"]):
        out.update(kind="BAD_SEED", detail="declared sha != consumed sha")
        return out
    if not str(decl.get("mac") or "").strip():
        out.update(kind="BAD_SEED", detail="sidecar carries no MAC")
        return out
    try:
        seed = json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeDecodeError) as e:
        out.update(kind="BAD_SEED", detail=f"{seed_path}: {e}")
        return out
    if not isinstance(seed, dict) or seed.get("kind") != "COSMOS_SEED":
        out.update(kind="BAD_SEED", detail="body is not a COSMOS_SEED")
        return out
    schema = str(seed.get("schema") or "")
    if schema not in ("cosmos-session-seed/1", "cosmos-session-seed/2"):
        out.update(kind="BAD_SEED", detail=f"unknown seed schema {schema!r}")
        return out
    seed_tree = str(seed.get("tree_id") or "").strip()
    if not seed_tree or seed_tree != str(live_tree_id):
        out.update(kind="IDENTITY_MISMATCH",
                   detail=f"seed tree_id={seed_tree!r} != live {live_tree_id!r}")
        return out
    facts = seed.get("facts")
    if not isinstance(facts, dict):
        out.update(kind="BAD_SEED", detail="facts is not an object")
        return out
    if schema.endswith("/2"):
        for key in ("motif", "leases", "inflight"):
            if key not in seed:
                out.update(kind="BAD_SEED",
                           detail=f"/2 seed missing required key {key!r}")
                return out
    cursor = None
    motif = seed.get("motif")
    if isinstance(motif, dict) and isinstance(motif.get("cursor"), dict):
        cur = motif["cursor"]
        if cur.get("slug"):
            cursor = {"slug": str(cur.get("slug")), "stage": cur.get("stage")}
    if cursor is None and facts.get("motif_cursor"):
        text = str(facts["motif_cursor"])
        slug, _, stage = text.partition("@")
        cursor = {"slug": slug, "stage": int(stage) if stage.isdigit() else None}
    out.update(ok=True, kind="SEED_THIN" if not facts else None,
               detail="MAC-valid shape; authenticity is start_session's call",
               sha=sha, sid=seed.get("sid"), schema=schema,
               thin=not facts, cursor=cursor)
    return out


def watermark(cow_hb: dict | None, now: float,
              age_s: float = SESSION_AGE_WATERMARK_S,
              turns: int = TURN_WATERMARK,
              stale_s: float = HEARTBEAT_STALE_S,
              pid_is_alive: bool | None = None) -> dict:
    """H9 - fire BEFORE truncation. W1/W2 are the engine (PID still alive), W3 is
    the self-heal backstop. Returns {fire, reason, detectors}.

    'Prompt is too long' and 'process gone' are both AFTER the bite. A design that
    waits for them has not implemented the wish, only survived it.
    """
    det = {"w1_age": False, "w1_turns": False, "w2_context": False,
           "w3_quiet": False, "w3_dead": False}
    if cow_hb is None or not isinstance(cow_hb, dict):
        # A list/string/bool heartbeat is not a reading — same as absent.
        # AttributeError on .get crashed the satellite (bite
        # `_bite_unpinned_round8.json`). Fail-closed: do not fire unless
        # the pid is proven dead.
        return {"fire": bool(pid_is_alive is False), "detectors": det,
                "reason": "quiet" if pid_is_alive is False else None,
                "why": "no COW heartbeat"}
    alive = pid_is_alive
    spawned = float(cow_hb.get("spawned_at_epoch") or 0)
    if spawned and (now - spawned) >= age_s:
        det["w1_age"] = True
    if int(cow_hb.get("turn_n") or 0) >= turns:
        det["w1_turns"] = True
    pct = cow_hb.get("context_pct")
    if isinstance(pct, (int, float)) and float(pct) >= 0.70:
        det["w2_context"] = True
    last = float(cow_hb.get("last_act_epoch") or 0)
    if last and (now - last) >= stale_s:
        det["w3_quiet"] = True
    if alive is False:
        det["w3_dead"] = True

    if alive is not False and (det["w1_age"] or det["w1_turns"] or det["w2_context"]):
        return {"fire": True, "reason": "watermark", "detectors": det,
                "why": "boundary detected while the window still has room"}
    if det["w3_dead"] or det["w3_quiet"]:
        return {"fire": True, "reason": "quiet", "detectors": det,
                "why": "backstop: orchestrator gone or silent"}
    return {"fire": False, "reason": None, "detectors": det, "why": "in window"}


def mint_session_id() -> str:
    return str(uuid.uuid4())


def spawn_argv(rail: str, prompt: str, cwd: str, session_id: str,
               model: str | None = None, add_dirs: tuple[str, ...] = ()) -> list[str]:
    """PROVEN dispatch flag sets (cosmos_dispatch.py / cosmos_work_order.build_argv),
    with exactly two deliberate divergences, both named:

      1. --output-format json  (dispatch uses plain) - the spawn must be machine
         readable so a refusal is a field, not a log line to eyeball.
      2. --session-id <uuid>   - mints the NEW conversation id so the fresh-window
         proof does not require holding the orchestrator's stdout pipe.

    NOT used, and why: --continue / --resume / --fork-session replay the same full
    transcript (the failure being fixed); --bare skips CLAUDE.md (BootUP needs it);
    --restore-code would snapshot-restore the LIVE tree; --prompt-file is not
    combined with --single (passing a prompt twice is undefined on both rails).
    """
    if isinstance(add_dirs, (str, bytes)) or not isinstance(
            add_dirs, (list, tuple)):
        # A string iterates as characters (`add_dirs="cwd"` → --add-dir c/w/d)
        # — the green-log. None TypeErrors. Bite `_bite_unpinned_round8.json`.
        raise ResessionRefusal(
            "BAD_DIRS",
            f"add_dirs is {type(add_dirs).__name__}, not a list of paths")
    if rail == "grok":
        argv = ["grok", "--single", prompt]
        if model:
            argv += ["-m", model]
        return argv + ["--output-format", "json", "--always-approve",
                       "--max-turns", "60", "--cwd", cwd,
                       "--session-id", session_id]
    if rail == "claude":
        argv = ["claude", "-p", prompt]
        if model:
            argv += ["--model", model]
        argv += ["--permission-mode", "dontAsk", "--output-format", "json",
                 "--session-id", session_id, "--add-dir", cwd]
        for d in add_dirs:
            argv += ["--add-dir", d]
        return argv
    raise ResessionRefusal("NO_RAIL", f"unknown rail {rail!r}")


def transcript_path(rail: str, cwd: str, session_id: str, home: Path) -> Path:
    """The vendor-written artifact that proves a spawn actually happened.

    claude: ~/.claude/projects/<cwd with non-alphanumerics -> '-'>/<uuid>.jsonl
    grok:   ~/.grok/sessions/<url-quoted cwd>/  (id-keyed entry inside)

    Bound to docs/research/AUTO_RESESSION.md 1.3 / 2.1, which measured both
    directories on this machine. The satellite never PARSES these files (the
    format is version-unstable) - existence + mtime is the whole signal.
    """
    if rail == "claude":
        slug = "".join(c if c.isalnum() else "-" for c in cwd)
        return home / ".claude" / "projects" / slug / f"{session_id}.jsonl"
    if rail == "grok":
        return home / ".grok" / "sessions" / urllib.parse.quote(cwd, safe="")
    raise ResessionRefusal("NO_RAIL", f"unknown rail {rail!r}")


def arm_gate_flag(prev: dict | None, now_dt: datetime,
                  grace_s: float = AUTO_RESUME_GRACE_S,
                  set_by: str = WORKER) -> dict:
    """P3 arming: rewrite a TidyUP handoff hold into a resume_gate carrying
    auto_resume_at. WD2.maybe_auto_resume unlinks it at that instant. Reason and
    timestamp are REQUIRED by PAUSE_PROTOCOL - a bound control, never a silent one.
    """
    due = now_dt + timedelta(seconds=float(grace_s))
    if prev is None:
        prev = {}
    if not isinstance(prev, dict):
        # dict([]) silently armed a resume_gate; dict("hold") ValueError.
        # Bite `_bite_unpinned_round8.json`.
        raise ResessionRefusal(
            "BAD_FLAG",
            f"prev is {type(prev).__name__}, not a pause flag object")
    flag = dict(prev)
    flag.update({
        "state": "PAUSED",
        "mode": "resume_gate",
        "scope": "retask",
        "auto_resume_at": due.isoformat(timespec="seconds"),
        "origin": "auto-resession",
        "set_by": set_by,
        "set_at": now_dt.isoformat(timespec="seconds"),
        "reason": "auto-resession handoff: fresh orchestrator spawning; the route "
                  "auto-resumes on the WD2 15s clock (P3, no human turn)",
        "effect": "NEW retask drops pause until auto_resume_at. In-flight jobs, "
                  "runner and collector keep moving (PAUSE is a gate, not a kill).",
    })
    return flag


def decide(*, pause: dict | None, seed: dict, cow_hb: dict | None,
           pid_alive: bool | None, now: float, prompt_sha: str | None,
           rail: str, lease_held_by: str | None) -> dict:
    """The whole state machine, pure and testable. Returns the RESESSION projection.

    Order is mandatory (H8 verify-then-spawn): HOLD wins over everything; a bad
    seed refuses before any gate is armed; the cow lease is the last check before
    a spawn, so a live orchestrator can never be doubled.
    """
    if not isinstance(seed, dict):
        # A list/None/string seed AttributeError'd on .get before HOLD
        # could win (bite `_bite_unpinned_round8.json`). Coerce to a
        # BAD_SEED record so HOLD still outranks, then the bad-seed
        # refuse runs on the existing path.
        seed = {"ok": False, "kind": "BAD_SEED",
                "detail": f"seed is {type(seed).__name__}, not an object",
                "sha": None, "sid": None, "schema": None, "thin": None,
                "cursor": None}
    rec = {"schema": SCHEMA, "state": "IDLE", "spawn_reason": None, "rail": rail,
           "refused_kind": None, "refused_detail": None,
           "seed_sha": seed.get("sha"), "seed_sid": seed.get("sid"),
           "seed_schema": seed.get("schema"), "seed_thin": seed.get("thin"),
           "resumed_from": seed.get("cursor"), "prompt_sha": prompt_sha,
           "detectors": {}, "why": ""}

    cls = classify_pause(pause)
    rec["pause_class"] = cls["class"]
    if cls["class"] == "HOLD":
        rec.update(state="HOLD", refused_kind="HOLD", refused_detail=cls["why"],
                   why=cls["why"])
        return rec

    wm = watermark(cow_hb, now, pid_is_alive=pid_alive)
    rec["detectors"] = wm["detectors"]
    if not wm["fire"]:
        rec["why"] = wm["why"]
        return rec
    rec["spawn_reason"] = wm["reason"]

    if not seed.get("ok"):
        rec.update(state="REFUSED", refused_kind=seed.get("kind"),
                   refused_detail=seed.get("detail"),
                   why="fail-closed: never spawn around a bad manifest")
        return rec
    if not prompt_sha:
        rec.update(state="REFUSED", refused_kind="NO_PROMPT",
                   refused_detail="docs/AUTO_RESESSION_PROMPT.md missing",
                   why="a BootUP prompt invented at fire time is not carry-over")
        return rec
    if lease_held_by:
        rec.update(state="REFUSED", refused_kind="HELD",
                   refused_detail=f"cow lease held by {lease_held_by}",
                   why="H7: exactly one orchestrator")
        return rec

    rec.update(state="ARMED",
               why="gate armed; TidyUP + fresh spawn is the next act")
    return rec


# ---------------------------------------------------------------------------
# I/O edges
# ---------------------------------------------------------------------------

def read_json(path: Path) -> dict | None:
    try:
        obj = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeDecodeError):
        return None
    return obj if isinstance(obj, dict) else None


def pid_is_alive(pid) -> bool | None:
    if not pid:
        return None
    try:
        from cosmos_clock import pid_alive
        return bool(pid_alive(int(pid)))
    except Exception:                                                 # noqa: BLE001
        return None


def sha256_file(path: Path) -> str | None:
    try:
        return hashlib.sha256(Path(path).read_bytes()).hexdigest()
    except OSError:
        return None


def tick(root: Path, repo: Path, *, rail: str = "grok",
         dry_run: bool = True, now: float | None = None) -> dict:
    """One pass. dry_run computes and returns the projection without writing it or
    spawning - which is how this probe build was measured against the live tree."""
    now = time.time() if now is None else now
    from cosmos_paths import CosmosPaths
    paths = CosmosPaths(str(root))
    control = paths.role("state") / "control"
    seed_rec = precheck_seed(paths.role("state", SEED_NAME),
                             paths.role("state", SEED_DECL_NAME),
                             paths.sentinel.tree_id)
    pause = read_json(control / PAUSE_NAME)
    cow_hb = read_json(control / COW_HEARTBEAT_NAME)
    prompt = repo.joinpath(*PROMPT_RELPATH)
    rec = decide(pause=pause, seed=seed_rec, cow_hb=cow_hb,
                 pid_alive=pid_is_alive((cow_hb or {}).get("pid")),
                 now=now, prompt_sha=sha256_file(prompt), rail=rail,
                 lease_held_by=None)
    rec["tree_id"] = paths.sentinel.tree_id
    rec["ts"] = datetime.now().astimezone().isoformat(timespec="seconds")
    rec["dry_run"] = bool(dry_run)
    rec["prompt_path"] = str(prompt)
    rec["projection_path"] = str(control / PROJECTION_NAME)
    return rec


def _pythonw() -> str:
    cand = Path(sys.executable).with_name("pythonw.exe")
    return str(cand) if cand.exists() else sys.executable


def plan_task_argv(root: Path) -> list[str]:
    """schtasks /create plan. Current user, no /rl highest. Registers nothing.

    Cadence is minute/1: the satellite decides; WD2 owns the 15s activity clock.
    `--once` is one decide cycle; the Windows clock re-invokes. Promotion into
    `cosmos/` + CLOCKS remains COW's fence — this is the clock *vehicle*.
    """
    tr = subprocess.list2cmdline([
        _pythonw(), str(Path(__file__).resolve()),
        "--root", str(root), "--once",
    ])
    return ["schtasks", "/create", "/tn", TASK_NAME, "/tr", tr,
            "/sc", "minute", "/mo", "1", "/f"]


def install_task(root: Path) -> dict:
    """Register the clock. A nonzero rc is REPORTED, never swallowed."""
    argv = plan_task_argv(root)
    try:
        p = subprocess.run(argv, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=60, creationflags=NO_WINDOW)
    except OSError as e:
        return {"ok": False, "rc": -1, "argv": argv, "out": str(e)}
    return {"ok": p.returncode == 0, "rc": p.returncode, "argv": argv,
            "out": ((p.stdout or "") + (p.stderr or "")).strip()}


def main() -> int:
    ap = argparse.ArgumentParser(description="COSMOS auto-resession satellite (probe)")
    ap.add_argument("--root", help="runtime root (live/)")
    ap.add_argument("--repo", default=str(Path(__file__).resolve().parent.parent),
                    help="repo tree holding docs/ (in cosmos/ the default is right)")
    ap.add_argument("--rail", default="grok", choices=RAILS)
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--dry-run", action="store_true",
                    help="decide and print; write nothing, spawn nothing")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--plan-task", action="store_true",
                    help="print the schtasks argv, register nothing")
    ap.add_argument("--install-task", action="store_true")
    a = ap.parse_args()

    if a.selftest:
        return selftest()
    if a.plan_task:
        if not a.root:
            print(json.dumps({"ok": False, "kind": "NO_ROOT",
                              "detail": "--root is required"}), file=sys.stderr)
            return 2
        print(json.dumps({"task": TASK_NAME, "argv": plan_task_argv(Path(a.root)),
                          "heartbeat": HEARTBEAT_NAME}, indent=1))
        return 0
    if a.install_task:
        if not a.root:
            print(json.dumps({"ok": False, "kind": "NO_ROOT",
                              "detail": "--root is required"}), file=sys.stderr)
            return 2
        rec = install_task(Path(a.root))
        print(json.dumps(rec, indent=1))
        return 0 if rec["ok"] else 1
    if not a.root:
        print(json.dumps({"ok": False, "kind": "NO_ROOT",
                          "detail": "--root is required"}), file=sys.stderr)
        return 2
    rec = tick(Path(a.root), Path(a.repo), rail=a.rail,
               dry_run=bool(a.dry_run or a.status))
    print(json.dumps(rec, indent=1, sort_keys=True, default=str))
    return 0 if rec.get("state") not in ("REFUSED",) else 1


# ---------------------------------------------------------------------------
# selftest (the pure core; no live tree, no spawn)
# ---------------------------------------------------------------------------

def selftest() -> int:
    results = []

    def check(label, fn):
        try:
            ok = bool(fn())
            results.append((label, ok, ""))
        except Exception as e:                                        # noqa: BLE001
            results.append((label, False, f"{type(e).__name__}: {e}"))

    check("operator hold is never rewritten",
          lambda: classify_pause({"state": "PAUSED", "mode": "hold",
                                  "set_by": "Keith",
                                  "reason": "stop"})["class"] == "HOLD")
    check("TidyUP handoff hold is the arming case",
          lambda: classify_pause({"state": "PAUSED", "mode": "hold",
                                  "set_by": "COW",
                                  "reason": "TidyUP + resession"})["class"] == "ARM")
    check("unknown pause mode fails closed to HOLD",
          lambda: classify_pause({"state": "PAUSED",
                                  "mode": "siesta"})["class"] == "HOLD")
    check("armed gate is left to WD2",
          lambda: classify_pause({"state": "PAUSED", "mode": "resume_gate",
                                  "auto_resume_at": "x"})["class"] == "GATE")
    check("age watermark fires while the pid is alive",
          lambda: watermark({"spawned_at_epoch": 1.0, "last_act_epoch": 3600.0,
                             "turn_n": 0}, 3600.0,
                            pid_is_alive=True)["reason"] == "watermark")
    check("a dead pid is the backstop, not the engine",
          lambda: watermark({"spawned_at_epoch": 999, "last_act_epoch": 1000,
                             "turn_n": 0}, 1000.0,
                            pid_is_alive=False)["reason"] == "quiet")
    check("in-window does not fire",
          lambda: watermark({"spawned_at_epoch": 999, "last_act_epoch": 1000,
                             "turn_n": 0}, 1000.0,
                            pid_is_alive=True)["fire"] is False)
    check("spawn argv never carries a replay flag",
          lambda: not ({"--continue", "-c", "--resume", "--fork-session", "--bare",
                        "--restore-code"}
                       & set(spawn_argv("grok", "p", "C:/x", "u"))))
    check("claude argv mints the new session id",
          lambda: spawn_argv("claude", "p", "C:/x", "u-1")[
              spawn_argv("claude", "p", "C:/x", "u-1").index("--session-id") + 1]
              == "u-1")
    check("an unknown rail is a typed refusal",
          lambda: _raises(lambda: spawn_argv("cursor", "p", "C:/x", "u"),
                          "NO_RAIL"))
    check("armed gate carries auto_resume_at and a reason",
          lambda: all(arm_gate_flag(None, datetime(2026, 1, 1)).get(k)
                      for k in ("auto_resume_at", "reason", "set_at", "mode")))
    check("claude transcript path is the vendor's, keyed by the minted id",
          lambda: transcript_path("claude", "V:/A", "abc",
                                  Path("/h")).name == "abc.jsonl")

    bad = [r for r in results if not r[1]]
    for label, ok, err in results:
        print(f"  {'OK  ' if ok else 'FAIL'}  {label}{('  ' + err) if err else ''}")
    print(f"result: {'ok' if not bad else 'FAIL'}  "
          f"{len(results) - len(bad)}/{len(results)}")
    return 1 if bad else 0


def _raises(fn, kind: str) -> bool:
    try:
        fn()
    except ResessionRefusal as e:
        return e.kind == kind
    return False


if __name__ == "__main__":
    raise SystemExit(main())
