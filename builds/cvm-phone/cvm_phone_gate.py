#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cvm_phone_gate — stage 6 for cvm-phone, split at the seam where Core matters.

The desktop half of this lane was already unchained (`cvm-dt/cvm_gate.py`);
the phone half was not. `cvm_phone_pull.py --gate` proves ONE slice (the
pull contract's kind statuses plus a reachability measurement) and stops.
Everything else the thin phone must prove — that it refuses a ticket that
was never published, that it never becomes the audio owner, that an idle
tick costs no radio, that it is not a second writer of the desktop's
files — was ungated, and chaining it to a Core that is down would have
left it ungated indefinitely.

    local  — provable on this box right now, Core up or down:
             sentinel identity; the live phone-reachability measurement
             (read-only); and, against a LOOPBACK DOUBLE running the real
             route code, the whole phone wire — empty-ticket refusal,
             kinds[] honored, every asked kind typed, no audio claim, the
             idle tick that skips HTTP, write attribution, the pcm pointer
             contract, plus the two local fail-closed refusals (dead Core,
             foreign tree_id).
             -> STAGE6_PHONE.json

    core   — needs the resident authority on :8770 and nothing else will do:
             /status tree_id and ledger head, an authoritative pull ticket
             stamped off the LIVE projection, a push Core accepts, the live
             cursor advancing, and the live phone projection going fresh.
             -> STAGE6_PHONE_CORE.json, and when Core is down that file is a
                TYPED PENDING_CORE artifact in which EVERY check names the
                exact thing it needs, plus the command to re-run it.

    split  — both halves -> STAGE6_PHONE_SPLIT.json.

The :8791 trial kernel is refused by port, here as in the desktop gate. A
substitute answering proves the substitute is up; that is not the claim the
core half makes. The loopback double is allowed in the LOCAL half only, is
typed LOOPBACK_DOUBLE, and `run_core` has no path to it.

rc: 0 passed · 1 FAILED (measured and wrong) · 3 PENDING (Core not up yet —
retry) · 2 refused before the gate could run.

    py -3.14 builds\\cvm-phone\\cvm_phone_gate.py local --root <RUNTIME>
    py -3.14 builds\\cvm-phone\\cvm_phone_gate.py core  --root <RUNTIME>
    py -3.14 builds\\cvm-phone\\cvm_phone_gate.py core  --root <RUNTIME> --watch 3600
    py -3.14 builds\\cvm-phone\\cvm_phone_gate.py split --root <RUNTIME>
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path
from typing import Optional

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
_DT = _HERE.parent / "cvm-dt"
if _DT.is_dir() and str(_DT) not in sys.path:
    sys.path.insert(0, str(_DT))
_COSMOS_LIB = _HERE.parents[1] / "cosmos"
if _COSMOS_LIB.is_dir() and str(_COSMOS_LIB) not in sys.path:
    sys.path.insert(0, str(_COSMOS_LIB))

from cosmos_cvm_push import PULL_CLOCK_ID, PUSH_PATH, stamp_desktop_pull  # noqa: E402
from cosmos_paths import SENTINEL_NAME                                   # noqa: E402

from cvm_dt import (                                                     # noqa: E402
    FAST_READ_S, CoreClient, CvmDtError, RefusalKind,
    _atomic_install, _now, _sha256_file, core_get, core_post,
    load_paths, load_token, pull_url,
)
from cvm_double import CoreDouble, dead_loopback_base                    # noqa: E402
# The verdict algebra is single-sourced from the desktop gate on purpose: two
# gates that disagree about what PENDING outranks are two different gates.
from cvm_gate import (                                                   # noqa: E402
    DEFAULT_BASE, FAIL, PASS, PENDING, REFUSED, TRIAL_PORTS, UNMEASURED,
    WATCH_POLL_S, _ms, _roll, check, wait_for_core,
)
from cvm_snap import KNOWN_KINDS                                         # noqa: E402

from cvm_phone_clock import CvmPhoneClock, PHONE_ID                      # noqa: E402
from cvm_phone_pull import (                                             # noqa: E402
    DENIED, NO_COLLECTOR, PHONE_DEADLINE_S, STATUS_OK, phone_reach,
    require_phone,
)

LOCAL_PROOF = "STAGE6_PHONE.json"
CORE_PROOF = "STAGE6_PHONE_CORE.json"
SPLIT_PROOF = "STAGE6_PHONE_SPLIT.json"
WIRE_LOCAL = "cvm-phone-gate-local/1"
WIRE_CORE = "cvm-phone-gate-core/1"
WIRE_SPLIT = "cvm-phone-gate-split/1"

# One ask exercising all three typed answers at once: `device` is granted and
# readable (data), `sms` is granted with no reader (NO_COLLECTOR), `calls` and
# `pcm` are ungranted (PERM_DENIED), `fax_over_ip` is not in this contract
# version at all (reported as unsupported, never smuggled into the body).
ASK = ("device", "sms", "calls", "pcm", "fax_over_ip")
GRANTS = ("device", "sms")
UNKNOWN_ASK = "fax_over_ip"
# The desktop's files. The phone quotes them; it is never their writer.
DESKTOP_FILES = ("pull.json", "phone.json")
TURN_FILE = "phone_turn.json"


def _fingerprint(paths, names=DESKTOP_FILES) -> dict:
    """sha256 of each named projection, or None when absent. Content, not
    mtime: attribution must not depend on a filesystem clock's resolution."""
    out = {}
    for name in names:
        p = paths.state("cvm", name)
        try:
            out[name] = hashlib.sha256(p.read_bytes()).hexdigest()
        except OSError:
            out[name] = None
    return out


# ---------------- half A: local (no Core, ever) ----------------
def _check_live_reach(paths, tree_id: str) -> dict:
    """The live phone projection, MEASURED. Read-only on the runtime root.

    Either verdict is honest: `fresh` means the phone checked in inside the
    deadline, `stale`/`never_seen` means it did not and `require_phone`
    refuses UNREACHABLE rather than folding an old projection as if it were
    this minute's phone. What would be dishonest is not looking.
    """
    t0 = time.perf_counter()
    rec = phone_reach(paths, tree_id)
    refused = None
    if not rec["reachable"]:
        try:
            require_phone(paths, tree_id)
            refused = "NO REFUSAL"
        except CvmDtError as e:
            refused = str(e.kind)
    typed = rec["reason"] in ("fresh", "stale", "never_seen")
    fail_closed = rec["reachable"] or (
        rec["kind"] == str(RefusalKind.UNREACHABLE)
        and refused == str(RefusalKind.UNREACHABLE))
    ok = typed and fail_closed
    return check("live_phone_reach_measured", PASS if ok else FAIL, {
        "reachable": rec["reachable"], "reason": rec["reason"],
        "kind": rec["kind"], "age_s": rec["age_s"],
        "deadline_s": rec["deadline_s"],
        "last_seen_epoch": rec["last_seen_epoch"],
        "source": rec["source"], "cursor": rec["cursor"],
        "require_phone_kind": refused,
        "read_only": True,
    }, ms=_ms(t0),
        why="" if ok else "reachability was not typed, or did not fail closed")


def _check_phone_wire() -> list:
    """The whole phone wire against the LOOPBACK DOUBLE — real route code.

    Every value here is labelled `is_core: false`. A double answering proves
    the double is up; none of this is evidence about :8770. What it IS
    evidence about is the phone client, which is the half this gate owns.
    """
    t0 = time.perf_counter()
    try:
        dbl = CoreDouble(worker="cvm-phone-gate").start()
    except Exception as e:                                          # noqa: BLE001
        return [check("phone_wire", UNMEASURED, None, kind="DOUBLE_BOOT_FAILED",
                      why="%s: %s" % (type(e).__name__, e))]
    checks: list = []
    try:
        core = CoreClient(dbl.base, dbl.token)
        provenance = dbl.describe()

        # 1. No ticket was ever published. The phone must REFUSE, not invent
        #    one and not report an empty snapshot as "nothing to report".
        t1 = time.perf_counter()
        try:
            CvmPhoneClock(core, dbl.paths).cycle_once()
            checks.append(check("empty_ticket_refused", FAIL, "pulled a ticket",
                                why="a ticket that was never published was accepted"))
        except CvmDtError as e:
            checks.append(check(
                "empty_ticket_refused",
                PASS if e.kind == RefusalKind.UNREACHABLE else FAIL,
                {"kind": str(e.kind), "detail": str(e)},
                kind=str(e.kind), ms=_ms(t1)))

        # 2. The desktop publishes a ticket asking for ASK. The ticket's
        #    kinds[] IS the pull.
        seeded = stamp_desktop_pull(dbl.paths, {"kinds": list(ASK),
                                                "cursor": "gate-desk-1"})
        clk = CvmPhoneClock(core, dbl.paths, grants=GRANTS)
        body = clk._turn_body()
        t2 = time.perf_counter()
        r1 = clk.cycle_once()
        tick1_ms = _ms(t2)
        ks = r1["kind_status"]
        answered = clk._kinds()          # the blobs behind those statuses
        known_ask = [k for k in ASK if k in KNOWN_KINDS]

        honored = (list(r1["requested"]) == list(ASK)
                   and r1["unsupported_kinds"] == [UNKNOWN_ASK]
                   and not (set(known_ask) - set(ks)))
        checks.append(check("ticket_kinds_honored", PASS if honored else FAIL, {
            "ticket_asked": seeded.get("kinds"),
            "clock_requested": r1["requested"],
            "answered": sorted(ks),
            "unanswered": sorted(set(known_ask) - set(ks)),
            "unsupported_reported": r1["unsupported_kinds"],
            "quoted_from": r1["quoted_from"],
        }, ms=tick1_ms,
            why="" if honored else "the ask was not the answer"))

        # 3. Three distinct typed answers, none of them an empty list and none
        #    of them a missing key (CVM_ARCH 5.3).
        typed = (ks.get("device") == STATUS_OK
                 and ks.get("sms") == NO_COLLECTOR % "sms"
                 and ks.get("calls") == DENIED % "calls"
                 and ks.get("pcm") == DENIED % "pcm"
                 # never [] and never a missing key: every answer is a
                 # non-empty object carrying a status
                 and bool(answered)
                 and all(isinstance(v, dict) and v and v.get("status")
                         for v in answered.values())
                 and UNKNOWN_ASK not in ks)
        checks.append(check("typed_status_per_kind", PASS if typed else FAIL, {
            "kind_status": ks,
            "granted": list(GRANTS),
            "data": [k for k, v in ks.items() if v == STATUS_OK],
            "no_collector": [k for k, v in ks.items()
                             if v.startswith("NO_COLLECTOR:")],
            "perm_denied": [k for k, v in ks.items()
                            if v.startswith("PERM_DENIED:")],
            "unknown_kind_not_in_body": UNKNOWN_ASK not in ks,
            "answered_blobs": answered,
        }, why="" if typed else "a kind answered empty, absent, or untyped"))

        # 4. The thin phone never becomes the audio owner. Not in the body it
        #    sends, not in the ticket it quotes, not in the file it publishes.
        ticket = json.loads(
            dbl.paths.state("cvm", "pull.json").read_text(encoding="utf-8"))
        turn = json.loads(
            dbl.paths.state("cvm", TURN_FILE).read_text(encoding="utf-8"))
        no_claim = ("audio_owner" not in body
                    and r1["claimed"] is False
                    and turn.get("claimed") is False
                    and r1["audio_owner"] == "desktop"
                    and ticket.get("audio_owner") == "desktop"
                    and str(ticket.get("writer") or "") != r1["writer"]
                    and int(ticket.get("clock_id") or 0) == int(PULL_CLOCK_ID))
        checks.append(check("phone_never_claims_audio", PASS if no_claim else FAIL, {
            "push_body_keys": sorted(body),
            "body_has_audio_owner": "audio_owner" in body,
            "tick_audio_owner": r1["audio_owner"],
            "tick_claimed": r1["claimed"],
            "published_claimed": turn.get("claimed"),
            "ticket_audio_owner": ticket.get("audio_owner"),
            "ticket_writer": ticket.get("writer"),
            "phone_writer": r1["writer"],
            "ticket_clock_id": ticket.get("clock_id"),
            "sole_writer_id": int(PULL_CLOCK_ID),
        }, why="" if no_claim else "the phone touched the owner it must only quote"))

        # 5. An idle tick costs no radio. A replay POST of an identical body is
        #    battery and bandwidth spent to say nothing.
        before = _fingerprint(dbl.paths)
        turn_before = _fingerprint(dbl.paths, (TURN_FILE,))[TURN_FILE]
        t3 = time.perf_counter()
        r2 = clk.cycle_once()
        tick2_ms = _ms(t3)
        after = _fingerprint(dbl.paths)
        turn_after = _fingerprint(dbl.paths, (TURN_FILE,))[TURN_FILE]
        quiet = (r2["skipped_http"] is True
                 and r2["http_gets"] == r1["http_gets"]
                 and r2["http_posts"] == r1["http_posts"]
                 and r2["push_bytes"] == 0
                 and r2["quoted_from"] == "local phone_turn.json"
                 and r2["cursor"] == r1["cursor"])
        checks.append(check("idle_tick_skips_http", PASS if quiet else FAIL, {
            "tick1": {"skipped_http": r1["skipped_http"],
                      "http_gets": r1["http_gets"],
                      "http_posts": r1["http_posts"],
                      "push_bytes": r1["push_bytes"], "tick_ms": tick1_ms},
            "tick2": {"skipped_http": r2["skipped_http"],
                      "http_gets": r2["http_gets"],
                      "http_posts": r2["http_posts"],
                      "push_bytes": r2["push_bytes"], "tick_ms": tick2_ms,
                      "quoted_from": r2["quoted_from"]},
            "cursor_stable": r2["cursor"] == r1["cursor"],
        }, ms=tick2_ms, why="" if quiet else "an idle tick spent radio"))

        # 6. Attribution. Tick 2 made no HTTP call, so nothing the server could
        #    have written moved during it — anything that changed was changed by
        #    the phone process, and it must be its own turn file alone.
        moved = sorted(k for k in after if after[k] != before[k])
        alone = not moved
        checks.append(check("phone_writes_only_its_turn_file",
                            PASS if alone else FAIL, {
                                "window": "one tick with skipped_http=true (no HTTP)",
                                "desktop_files_changed": moved,
                                "desktop_files": list(DESKTOP_FILES),
                                "turn_file_changed": turn_before != turn_after,
                                "published": r2.get("published"),
                            },
                            why="" if alone else
                            "the phone wrote a file the desktop owns"))

        # 7. pcm crosses as a POINTER. Inline bytes on the thin-phone wire is
        #    the radio bill this architecture exists to not pay.
        t4 = time.perf_counter()
        pcm_clk = CvmPhoneClock(core, dbl.paths, client_id="cvm-phone-gate-pcm",
                                push_request_id="cvm-phone-gate-pcm",
                                grants=("device", "pcm"),
                                kinds={"device": {"status": STATUS_OK},
                                       "pcm": {"status": STATUS_OK,
                                               "bytes": "AAAA"}})
        pcm_clk.requested = ("device", "pcm")
        try:
            core_post(core, PUSH_PATH, pcm_clk._turn_body(), FAST_READ_S,
                      default_400=RefusalKind.BAD_SNAPSHOT)
            checks.append(check("pcm_pointer_contract", FAIL, "ACCEPTED",
                                why="inline pcm bytes crossed the wire"))
        except CvmDtError as e:
            checks.append(check(
                "pcm_pointer_contract",
                PASS if e.kind == RefusalKind.BAD_SNAPSHOT else FAIL,
                {"kind": str(e.kind), "detail": str(e)},
                kind=str(e.kind), ms=_ms(t4)))

        # 8. A projection stamped for another tree is refused, not adopted.
        t5 = time.perf_counter()
        foreign = dbl.paths.state("cvm", TURN_FILE)
        keep = foreign.read_text(encoding="utf-8")
        foreign.write_text(json.dumps(
            {"cvm": 1, "tree_id": "KMesh-NOT-THIS-TREE", "cursor": "x"}),
            encoding="utf-8")
        try:
            CvmPhoneClock(core, dbl.paths, client_id="cvm-phone-gate-foreign")
            checks.append(check("foreign_tree_refused", FAIL, "adopted",
                                why="a projection from another tree was loaded"))
        except CvmDtError as e:
            checks.append(check(
                "foreign_tree_refused",
                PASS if e.kind == RefusalKind.IDENTITY_MISMATCH else FAIL,
                {"kind": str(e.kind), "detail": str(e)},
                kind=str(e.kind), ms=_ms(t5)))
        finally:
            foreign.write_text(keep, encoding="utf-8")

        checks.append(check("loopback_double_provenance", PASS, provenance,
                            ms=_ms(t0)))
        return checks
    except CvmDtError as e:
        checks.append(check("phone_wire", FAIL, str(e), kind=str(e.kind),
                            ms=_ms(t0)))
        return checks
    finally:
        dbl.stop()


def _check_dead_core(paths) -> dict:
    """Core down is UNREACHABLE, never an optimistic empty snapshot."""
    t0 = time.perf_counter()
    dead = dead_loopback_base()
    try:
        CvmPhoneClock(CoreClient(dead, "no-token"), paths,
                      client_id="cvm-phone-gate-dead").cycle_once()
        return check("dead_core_typed_refusal", FAIL, dead,
                     why="a closed port answered")
    except CvmDtError as e:
        return check("dead_core_typed_refusal",
                     PASS if e.kind == RefusalKind.UNREACHABLE else FAIL,
                     {"base": dead, "kind": str(e.kind)},
                     kind=str(e.kind), ms=_ms(t0))


def run_local(root, *, proof_path: Optional[str] = None) -> dict:
    """Half A. Everything stage 6 can prove about the phone with Core down."""
    paths = load_paths(root)
    tree_id = paths.sentinel.tree_id
    checks: list = []

    t0 = time.perf_counter()
    load_token(paths)                        # AUTH_REQUIRED if absent/blank
    checks.append(check("root_identity", PASS, {
        "tree_id": tree_id, "system": paths.sentinel.system,
        "sentinel": str(paths.root / SENTINEL_NAME), "token_loaded": True,
    }, ms=_ms(t0)))

    checks.append(_check_live_reach(paths, tree_id))
    checks.extend(_check_phone_wire())
    # Read-only on the live root: constructing the clock loads phone_turn.json
    # and refuses before any write, and the GET never leaves the box.
    checks.append(_check_dead_core(paths))

    reach = next(c for c in checks if c["name"] == "live_phone_reach_measured")
    ks = next((c["value"].get("kind_status")
               for c in checks if c["name"] == "typed_status_per_kind"
               and isinstance(c.get("value"), dict)), {}) or {}
    return _record("local", WIRE_LOCAL, root, paths, checks, {
        "core_used": False,
        "core_substitute_used": False,
        "note": ("rc=0 is not the gate; the checks[] values are. This half "
                 "quotes NO Core measurement — the loopback double is typed "
                 "LOOPBACK_DOUBLE and is not evidence about :8770. An "
                 "unreachable live phone is a passing MEASUREMENT here, not a "
                 "green log."),
        "emitted": "cvm-phone-local:%s:%s:%s:%d/%d:%s" % (
            tree_id,
            reach["value"].get("reason") or "NO_REACH",
            ("NO_SEEN" if reach["value"].get("age_s") is None
             else "%.3f" % reach["value"]["age_s"]),
            sum(1 for v in ks.values() if v.startswith("PERM_DENIED:")),
            len(ks) or 0,
            _sha256_file(Path(__file__).resolve())[:16],
        ),
    }, proof_path, LOCAL_PROOF)


# ---------------- half B: core (nothing else will do) ----------------
# Each entry: (check name, what it needs — named exactly, so the artifact is
# a work order and not a shrug).
CORE_CHECKS = (
    ("core_status_tree_id",
     "GET /api/v1/status from the resident Core, answering with the live "
     "sentinel tree_id"),
    ("core_ledger_head_seq",
     "the ledger_head.seq in that same /status — a value only the single "
     "signing ledger writer can emit"),
    ("core_pull_ticket_authoritative",
     "GET /api/v1/cvm/pull?client_id=" + PHONE_ID + " returning a ticket off "
     "the LIVE state/cvm/pull.json, stamped with projection_mtime / "
     "projection_owner / projection_size"),
    ("core_push_accepted_owner_desktop",
     "POST " + PUSH_PATH + " accepted by the resident Core, answering "
     "audio_owner=desktop and claimed=false"),
    ("core_cursor_advances_live",
     "the GET /api/v1/cvm/pull after that push, carrying the cursor_out the "
     "push returned"),
    ("phone_reach_fresh_after_push",
     "live state/cvm/phone.json written by Core in response to the push, so "
     "cvm_phone_pull.phone_reach flips to reachable/fresh inside "
     "deadline_s=%.1f" % PHONE_DEADLINE_S),
)


def _pending(base: str, kind: str) -> list:
    verdict = PENDING if kind == RefusalKind.UNREACHABLE else FAIL
    return [check(name, verdict, None, kind=kind,
                  why="Core at %s did not answer GET /api/v1/status" % base)
            | {"needs": needs}
            for name, needs in CORE_CHECKS]


def run_core(root, base: str = DEFAULT_BASE, *,
             proof_path: Optional[str] = None,
             watch_s: float = 0.0, poll_s: float = WATCH_POLL_S) -> dict:
    """Half B. Passes only against the resident authority — or says PENDING.

    Starts nothing. Polling a port is not booting a service, and no
    stand-in is accepted in Core's place.
    """
    paths = load_paths(root)
    tree_id = paths.sentinel.tree_id
    core = CoreClient(base, load_token(paths))
    if core.port in TRIAL_PORTS:
        raise CvmDtError(
            RefusalKind.BAD_REQUEST,
            "port %d is the trial kernel, not Core. The core half has no "
            "stand-in; a substitute answering proves the substitute is up."
            % core.port)

    waited = wait_for_core(core, watch_s, poll_s)
    live = {k: None for k in (
        "status_tree_id", "ledger_seq", "ticket_cursor", "projection_mtime",
        "push_cursor_out", "pulled_cursor", "reach_reason", "reach_age_s")}
    if not waited["up"]:
        checks = _pending(base, waited["last_kind"] or str(RefusalKind.UNREACHABLE))
    else:
        checks, live = _measure_core(core, paths, tree_id, base)

    rerun = ("py -3.14 %s core --root %s --base %s"
             % (Path(__file__).resolve(), Path(root).resolve(), base))
    return _record("core", WIRE_CORE, root, paths, checks, {
        "base": base,
        "core_reachable": bool(waited["up"]),
        "reach": waited,
        "core_kind": None if waited["up"] else (
            waited["last_kind"] or str(RefusalKind.UNREACHABLE)),
        "core_substitute_used": False,
        "loopback_double_used": False,
        "trial_ports_refused": sorted(TRIAL_PORTS),
        "needs": {
            "authority": "the resident COSMOS Core service on " + base,
            "started_by": "Keith — `cosmos.py serve --root <RUNTIME> --port 8770`; "
                          "this gate never starts, installs or repairs a service",
            "token": "config/api_token.txt under the handed-in runtime root",
            "routes": ["GET /api/v1/status", "GET " + pull_url(PHONE_ID),
                       "POST " + PUSH_PATH],
            "per_check": {name: needs for name, needs in CORE_CHECKS},
            "mutates_live": [
                "state/cvm/phone.json (Core replaces it on the push)",
                "state/cvm/pull.json (Core stamps audio_owner=desktop)",
            ],
        },
        "live_value": live,
        "rerun": rerun,
        "note": ("PENDING_CORE is an ABSENCE WITH A REASON, not a pass and not "
                 "a failure: the resident authority was not up, and no "
                 "substitute was accepted in its place — not the :8791 trial "
                 "kernel and not the loopback double the local half uses. Every "
                 "check above names what it needs. Re-run `rerun` the moment "
                 "Core is serving, or arm `core --watch <seconds>`."),
        "emitted": "cvm-phone-core:%s:%s:%s:%s" % (
            tree_id,
            live["status_tree_id"] or (waited["last_kind"] or "PENDING"),
            live["ledger_seq"] if live["ledger_seq"] is not None else "NO_SEQ",
            _sha256_file(Path(__file__).resolve())[:16],
        ),
    }, proof_path, CORE_PROOF)


def _measure_core(core: CoreClient, paths, tree_id: str, base: str) -> tuple:
    """The six core claims, against the resident authority only."""
    needs = dict(CORE_CHECKS)
    checks: list = []
    live: dict = {}

    def add(name, verdict, value=None, **kw):
        checks.append(check(name, verdict, value, **kw) | {"needs": needs[name]})

    t0 = time.perf_counter()
    status = core.status()
    got = str(status.get("tree_id") or "")
    live["status_tree_id"] = got
    add("core_status_tree_id", PASS if got == tree_id else FAIL,
        {"status_tree_id": got, "live_tree_id": tree_id,
         "served_at": status.get("served_at")},
        kind=None if got == tree_id else str(RefusalKind.IDENTITY_MISMATCH),
        ms=_ms(t0))
    seq = (status.get("ledger_head") or {}).get("seq")
    live["ledger_seq"] = seq
    add("core_ledger_head_seq", PASS if seq is not None else FAIL,
        {"ledger_seq": seq, "event": (status.get("ledger_head") or {}).get("event")},
        why="" if seq is not None else "/status carried no ledger head")

    t1 = time.perf_counter()
    pulled = core_get(core, pull_url(PHONE_ID), FAST_READ_S)
    live["ticket_cursor"] = str(pulled.get("cursor") or "")
    live["projection_mtime"] = pulled.get("projection_mtime")
    authoritative = (pulled.get("pull") is not False
                     and str(pulled.get("tree_id") or "") == tree_id
                     and pulled.get("projection_mtime") is not None)
    add("core_pull_ticket_authoritative", PASS if authoritative else FAIL, {
        "pull": pulled.get("pull"), "tree_id": pulled.get("tree_id"),
        "kinds": pulled.get("kinds"), "cursor": pulled.get("cursor"),
        "audio_owner": pulled.get("audio_owner"),
        "projection_mtime": pulled.get("projection_mtime"),
        "projection_owner": pulled.get("projection_owner"),
        "projection_size": pulled.get("projection_size"),
    }, ms=_ms(t1),
        why="" if authoritative else "no live projection behind the ticket")

    clk = CvmPhoneClock(core, paths, client_id=PHONE_ID,
                        push_request_id="cvm-phone-gate-core", grants=GRANTS)
    t2 = time.perf_counter()
    pushed = core_post(core, PUSH_PATH, clk._turn_body(), FAST_READ_S,
                       default_400=RefusalKind.BAD_SNAPSHOT)
    push_ms = _ms(t2)
    cursor_out = str(pushed.get("cursor_out") or pushed.get("cursor") or "")
    live["push_cursor_out"] = cursor_out
    accepted = (bool(cursor_out) and pushed.get("audio_owner") == "desktop"
                and pushed.get("claimed") is False)
    add("core_push_accepted_owner_desktop", PASS if accepted else FAIL, {
        "cursor_out": cursor_out, "audio_owner": pushed.get("audio_owner"),
        "claimed": pushed.get("claimed"), "stored": pushed.get("stored"),
        "idempotent": pushed.get("idempotent"), "push_ms": push_ms,
    }, ms=push_ms,
        why="" if accepted else "the resident Core did not land the phone turn")

    t3 = time.perf_counter()
    again = core_get(core, pull_url(PHONE_ID), FAST_READ_S)
    live["pulled_cursor"] = str(again.get("cursor") or "")
    moved = bool(cursor_out) and live["pulled_cursor"] == cursor_out
    add("core_cursor_advances_live", PASS if moved else FAIL, {
        "push_cursor_out": cursor_out, "pull_cursor": live["pulled_cursor"],
        "audio_owner": again.get("audio_owner"),
    }, ms=_ms(t3), why="" if moved else "the live cursor did not advance")

    t4 = time.perf_counter()
    rec = phone_reach(paths, tree_id)
    live["reach_reason"], live["reach_age_s"] = rec["reason"], rec["age_s"]
    fresh = rec["reachable"] and rec["reason"] == "fresh"
    add("phone_reach_fresh_after_push", PASS if fresh else FAIL, {
        "reachable": rec["reachable"], "reason": rec["reason"],
        "age_s": rec["age_s"], "deadline_s": rec["deadline_s"],
        "source": rec["source"], "cursor": rec["cursor"],
    }, ms=_ms(t4), kind=None if fresh else rec["kind"],
        why="" if fresh else "Core did not refresh the live phone projection")
    return checks, live


# ---------------- the record + the rollup ----------------
def _record(half: str, wire: str, root, paths, checks: list, extra: dict,
            proof_path: Optional[str], default_name: str) -> dict:
    ok, verdict = _roll(checks)
    t, off = _now()
    src = Path(__file__).resolve()
    rec = {
        "ok": ok,
        "verdict": verdict,
        "stage": 6,
        "deliverable": "cvm-phone",
        "half": half,
        "gated_at_epoch": t,
        "utc_offset_s": off,
        "source_path": str(src),
        "source_sha256": _sha256_file(src),
        "clock_sha256": _sha256_file(src.with_name("cvm_phone_clock.py")),
        "pull_sha256": _sha256_file(src.with_name("cvm_phone_pull.py")),
        "live_root": str(Path(root).resolve()),
        "live_tree_id": paths.sentinel.tree_id,
        "live_system": paths.sentinel.system,
        "sentinel": str(paths.root / SENTINEL_NAME),
        "python": sys.version.split()[0],
        "executable": sys.executable,
        "checks": checks,
        "counts": {v: sum(1 for c in checks if c["verdict"] == v)
                   for v in (PASS, REFUSED, UNMEASURED, PENDING, FAIL)},
        "wire": wire,
    }
    rec.update(extra)
    dest = Path(proof_path) if proof_path else (src.parent / default_name)
    rec["proof_path"] = str(dest.resolve())
    _atomic_install(dest, rec)
    return rec


def run_split(root, base: str = DEFAULT_BASE, *, watch_s: float = 0.0,
              proof_path: Optional[str] = None) -> dict:
    """Both halves, independently recorded, plus a rollup naming the block."""
    local = run_local(root)
    core = run_core(root, base, watch_s=watch_s)
    paths = load_paths(root)
    blocked = [{"check": c["name"], "needs": c.get("needs")}
               for c in core["checks"] if c["verdict"] == PENDING]
    t, off = _now()
    rec = {
        "ok": bool(local["ok"] and core["ok"]),
        # The rollup takes the WORSE of the two halves, so a green local can
        # never round a pending core up to "done".
        "verdict": (FAIL if FAIL in (local["verdict"], core["verdict"])
                    else PENDING if PENDING in (local["verdict"], core["verdict"])
                    else local["verdict"] if not local["ok"] else core["verdict"]),
        "stage": 6,
        "deliverable": "cvm-phone",
        "half": "split",
        "gated_at_epoch": t,
        "utc_offset_s": off,
        "live_root": str(Path(root).resolve()),
        "live_tree_id": paths.sentinel.tree_id,
        "python": sys.version.split()[0],
        "local": {k: local[k] for k in
                  ("ok", "verdict", "counts", "emitted", "proof_path")},
        "core": {k: core[k] for k in
                 ("ok", "verdict", "counts", "emitted", "proof_path",
                  "core_reachable", "core_kind", "rerun")},
        "blocked_on_core": blocked,
        "wire": WIRE_SPLIT,
        "note": ("Two claims, two records. The local half stands on its own "
                 "numbers; the core half is PENDING until the resident "
                 "authority answers. No substitute was accepted."),
    }
    dest = Path(proof_path) if proof_path else (
        Path(__file__).resolve().parent / SPLIT_PROOF)
    rec["proof_path"] = str(dest.resolve())
    _atomic_install(dest, rec)
    return rec


def _rc(rec: dict) -> int:
    if rec.get("ok"):
        return 0
    return 3 if rec.get("verdict") in (PENDING, REFUSED, UNMEASURED) else 1


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        prog="cvm-phone-gate",
        description="stage-6 for cvm-phone, split into local (no Core) and core")
    sub = ap.add_subparsers(dest="half", required=True)

    def common(p, base: bool = True):
        p.add_argument("--root", required=True,
                       help="COSMOS runtime root (handed in; sentinel verified)")
        if base:
            p.add_argument("--base", default=DEFAULT_BASE, help="Core base URL")
        p.add_argument("--proof", default="", help="proof JSON path")
        return p

    common(sub.add_parser("local", help="the half provable with Core down"),
           base=False)
    co = common(sub.add_parser("core", help="the half that needs the resident Core"))
    co.add_argument("--watch", type=float, default=0.0,
                    help="poll GET /status up to N seconds, fire the instant "
                         "Core answers (polling is not starting)")
    co.add_argument("--poll", type=float, default=WATCH_POLL_S)
    sp = common(sub.add_parser("split", help="both halves + " + SPLIT_PROOF))
    sp.add_argument("--watch", type=float, default=0.0)

    ns = ap.parse_args(argv)
    try:
        if ns.half == "local":
            rec = run_local(ns.root, proof_path=ns.proof or None)
        elif ns.half == "core":
            rec = run_core(ns.root, ns.base, proof_path=ns.proof or None,
                           watch_s=ns.watch, poll_s=ns.poll)
        else:
            rec = run_split(ns.root, ns.base, watch_s=ns.watch,
                            proof_path=ns.proof or None)
    except CvmDtError as e:
        print(json.dumps({"ok": False, "status": "refused",
                          "kind": str(e.kind), "detail": str(e)}, indent=1))
        return 2
    print(json.dumps(rec, indent=1, default=str))
    return _rc(rec)


if __name__ == "__main__":
    sys.exit(main())
