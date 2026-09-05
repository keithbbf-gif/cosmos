#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cvm-phone PULL CONTRACT — capability-gated kinds + phone reachability.

The PC pulls; the phone stays thin (docs/CVM_ARCH.md §§5.2-5.3, 8.3).
Two halves of that contract were missing from builds/cvm-phone:

  * The ticket's `kinds[]` was never honored. The clock pushed one
    hard-coded `device` blob and ignored what the PC asked for, so the
    pull was a pull in name only.
  * A capability the phone does not hold was an ABSENT key — which
    reads exactly like "nothing to report". CVM_ARCH §5.3: a denied
    permission is `PERM_DENIED:<kind>`, never []. The string appeared
    nowhere in the tree, though `cosmos_cvm_push.pcm_pointer` already
    tests for it.
  * Nothing measured whether the phone is still THERE. A stale
    projection is not a live phone; the drain folded it forever.

`collect_kinds` answers every asked kind with a typed status — data,
`PERM_DENIED:<kind>` (no capability) or `NO_COLLECTOR:<kind>` (granted,
but this build has no reader). It never answers with an empty list and
never omits an asked kind. `phone_reach` measures the age of the last
real check-in; `require_phone` turns a stale/never-seen phone into
`RefusalKind.UNREACHABLE` instead of an optimistic empty snapshot.

Read-only on Core state; writes nothing but its own gate proof. Never
claims audio ownership — desktop is the heavy-local owner.

    py -3.14 builds\\cvm-phone\\cvm_phone_pull.py --root <RUNTIME> --reach
    py -3.14 builds\\cvm-phone\\cvm_phone_pull.py --root <RUNTIME> --gate

rc=0 is not the gate. `--gate` quotes live_value.kind_status (the real
PERM_DENIED / NO_COLLECTOR strings this build emits), live_value.age_s
(measured against the live projection) and the sentinel tree_id into
STAGE6_PHONE_PULL.json.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path
from typing import Any, Iterable, Optional

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
_DT = _HERE.parent / "cvm-dt"
if _DT.is_dir() and str(_DT) not in sys.path:
    sys.path.insert(0, str(_DT))
_COSMOS_LIB = _HERE.parents[1] / "cosmos"      # builds/cvm-phone -> repo/cosmos
if _COSMOS_LIB.is_dir() and str(_COSMOS_LIB) not in sys.path:
    sys.path.insert(0, str(_COSMOS_LIB))

from cosmos_cvm_push import PULL_INTERVAL_S, phone_state  # noqa: E402
from cosmos_paths import SENTINEL_NAME  # noqa: E402

from cvm_dt import CvmDtError, RefusalKind, load_paths  # noqa: E402
from cvm_snap import KNOWN_KINDS, filter_kinds  # noqa: E402

STATUS_OK = "ok"
# §5.3: "A denied permission is PERM_DENIED:<kind>, never []."
DENIED = "PERM_DENIED:%s"
# Granted, but this build ships no reader for it. Honest absence of a
# collector is NOT an empty result set — that distinction is the point.
NO_COLLECTOR = "NO_COLLECTOR:%s"
# The only kind a headless phone clock can answer for itself.
DEFAULT_GRANTS = ("device",)
# Three missed pull cadences. Derived, not a magic constant.
PHONE_DEADLINE_S = 3.0 * PULL_INTERVAL_S
TURN_REL = ("cvm", "phone_turn.json")
PHONE_REL = ("cvm", "phone.json")
PROOF_NAME = "STAGE6_PHONE_PULL.json"
WIRE = "cvm-phone-pull/1"


def device_kind() -> dict:
    """The one kind this clock answers from its own process, no permission."""
    return {"status": STATUS_OK, "audio_route": "none",
            "surface": "capture+playback"}


def statuses(kinds: Optional[dict]) -> dict:
    """{kind: status} — the machine-readable answer for every asked kind."""
    return {str(k): str((v or {}).get("status") or STATUS_OK)
            for k, v in (kinds or {}).items()}


def unsupported(requested: Iterable[Any]) -> list:
    """Asked kinds this contract version does not know (forward compatible)."""
    return [str(k) for k in (requested or ()) if str(k) not in KNOWN_KINDS]


def collect_kinds(requested: Iterable[Any] = (), *,
                  grants: Iterable[Any] = DEFAULT_GRANTS,
                  data: Optional[dict] = None) -> dict:
    """Answer the ticket. Every asked known kind gets a typed status.

    Fail-closed: a kind not in `grants` is `PERM_DENIED:<kind>`; a
    granted kind with no collector is `NO_COLLECTOR:<kind>`. Neither is
    an empty list, and neither is a missing key. An empty ask falls back
    to what this build can actually speak for (granted ∪ held).
    Validated through the one contract (`cvm_snap.filter_kinds`), so a
    body this returns is a body Core accepts.
    """
    granted = {str(g) for g in (grants or ())}
    have = dict(data or {})
    req = [str(k) for k in (requested or ()) if str(k) in KNOWN_KINDS]
    if not req:
        req = sorted((granted | set(map(str, have))) & set(KNOWN_KINDS))
    out: dict[str, Any] = {}
    for k in dict.fromkeys(req):
        if k not in granted:
            out[k] = {"status": DENIED % k}
            continue
        blob = have.get(k)
        if isinstance(blob, dict) and blob:
            blob = dict(blob)
            blob.setdefault("status", STATUS_OK)
            out[k] = blob
        else:
            out[k] = {"status": NO_COLLECTOR % k}
    return filter_kinds(out)


def _turn(paths, tree_id: str) -> Optional[dict]:
    """Local phone_turn.json. Identity mismatch is a refusal, not a shrug."""
    path = paths.state(*TURN_REL)
    if not path.is_file():
        return None
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(obj, dict):
        return None
    got = str(obj.get("tree_id") or "")
    if got and got != tree_id:
        raise CvmDtError(
            RefusalKind.IDENTITY_MISMATCH,
            "phone_turn.json tree_id=%r != sentinel %r" % (got, tree_id))
    return obj


def _epoch(obj: Optional[dict], keys: tuple) -> float:
    best = 0.0
    if not isinstance(obj, dict):
        return best
    for key in keys:
        try:
            ep = float(obj.get(key) or 0.0)
        except (TypeError, ValueError):
            ep = 0.0
        if ep > best:
            best = ep
    return best


def phone_seen(paths, tree_id: str) -> dict:
    """Newest evidence the phone half actually ran. Local files, no HTTP.

    `phone.json` is Core's record of a real POST (received_epoch);
    `phone_turn.json` is the phone clock's own cycle stamp. Newest wins,
    and the winning file is named — a reach claim quotes its source.
    """
    turn = _turn(paths, tree_id)
    phone = phone_state(paths, tree_id)
    best, source = 0.0, ""
    for obj, name, keys in (
            (phone, "/".join(("state",) + PHONE_REL),
             ("received_epoch", "last_push_epoch")),
            (turn, "/".join(("state",) + TURN_REL), ("last_seen_epoch",))):
        ep = _epoch(obj, keys)
        if ep > best:
            best, source = ep, name
    cursor = ""
    for obj in (phone, turn):
        if isinstance(obj, dict):
            cursor = str(obj.get("cursor_out") or obj.get("cursor") or cursor)
            if cursor:
                break
    kind_status = statuses((turn or {}).get("kinds")) if turn else {}
    if not kind_status and isinstance(phone, dict):
        kind_status = statuses(phone.get("kinds"))
    return {"last_seen_epoch": best, "source": source, "cursor": cursor,
            "kind_status": kind_status}


def phone_reach(paths, tree_id: str, *, now: Optional[float] = None,
                deadline_s: float = PHONE_DEADLINE_S) -> dict:
    """Is the thin phone still on the road? Measured, never assumed."""
    now = time.time() if now is None else float(now)
    seen = phone_seen(paths, tree_id)
    ep = float(seen["last_seen_epoch"] or 0.0)
    age = round(now - ep, 3) if ep else None
    if not ep:
        reachable, reason = False, "never_seen"
    elif age is not None and age > float(deadline_s):
        reachable, reason = False, "stale"
    else:
        reachable, reason = True, "fresh"
    rec = {
        "cvm": 1, "tree_id": tree_id, "subject": "phone",
        "reachable": reachable,
        "kind": None if reachable else str(RefusalKind.UNREACHABLE),
        "reason": reason, "last_seen_epoch": ep or None, "age_s": age,
        "deadline_s": float(deadline_s), "source": seen["source"] or None,
        "cursor": seen["cursor"], "kind_status": seen["kind_status"],
        "measured_epoch": now,
    }
    rec["live_value"] = {k: rec[k] for k in (
        "reachable", "kind", "reason", "age_s", "deadline_s",
        "last_seen_epoch", "source", "cursor", "kind_status")}
    return rec


def require_phone(paths, tree_id: str, *, now: Optional[float] = None,
                  deadline_s: float = PHONE_DEADLINE_S) -> dict:
    """phone_reach, but an unreachable phone is a typed refusal.

    The caller that would otherwise fold a stale projection as if it
    were this minute's phone gets UNREACHABLE instead. Empty is not
    "no SMS"; old is not "still here".
    """
    rec = phone_reach(paths, tree_id, now=now, deadline_s=deadline_s)
    if not rec["reachable"]:
        raise CvmDtError(
            RefusalKind.UNREACHABLE,
            "phone %s: last_seen=%s age_s=%s deadline_s=%s source=%s" % (
                rec["reason"], rec["last_seen_epoch"], rec["age_s"],
                rec["deadline_s"], rec["source"]))
    return rec


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    try:
        h.update(path.read_bytes())
    except OSError:
        return ""
    return h.hexdigest()


def run_gate(root: str, proof_path: Optional[str] = None) -> dict:
    """Stage-6 proof bound to values only a real run against the live root emits."""
    paths = load_paths(root)
    tree_id = paths.sentinel.tree_id
    asked = sorted(KNOWN_KINDS)
    kinds = collect_kinds(asked, data={"device": device_kind()})
    kind_status = statuses(kinds)
    reach = phone_reach(paths, tree_id)
    clock_src = _HERE / "cvm_phone_clock.py"
    denied = sorted(k for k, v in kind_status.items() if v.startswith("PERM_"))
    live = {
        "live_tree_id": tree_id,
        "sentinel": str(Path(paths.root) / SENTINEL_NAME),
        "asked_kinds": asked,
        "answered_kinds": sorted(kinds),
        "kind_status": kind_status,
        "denied_kinds": denied,
        "unanswered_kinds": sorted(set(asked) - set(kinds)),
        "phone_reachable": reach["reachable"],
        "phone_reach_kind": reach["kind"],
        "phone_reach_reason": reach["reason"],
        "age_s": reach["age_s"],
        "deadline_s": reach["deadline_s"],
        "last_seen_epoch": reach["last_seen_epoch"],
        "source": reach["source"],
        "cursor": reach["cursor"],
    }
    # Every asked kind answered with a typed status, and the phone's
    # presence MEASURED (either verdict is honest). An unreachable phone
    # is a passing refusal here, exactly as AUDIO_NONE is for cvm-dt.
    ok = bool(tree_id) and not live["unanswered_kinds"] and bool(kind_status)
    rec = {
        "ok": ok,
        "stage": 6,
        "deliverable": "cvm-phone",
        "slice": "pull-contract",
        "gated_at_epoch": time.time(),
        "source_path": str(Path(__file__).resolve()),
        "source_sha256": _sha256(Path(__file__).resolve()),
        "clock_path": str(clock_src),
        "clock_sha256": _sha256(clock_src),
        "live_root": str(paths.root),
        "python": "%d.%d.%d" % sys.version_info[:3],
        "live_value": live,
        "wire": WIRE,
        "note": ("rc=0 is not the gate. The live_value fields are. An "
                 "UNREACHABLE phone is a passing refusal, not a green log: "
                 "it is the measurement, not its absence."),
        "emitted": "cvm-phone:%s:%s:%s:%d/%d:%s" % (
            tree_id, reach["reason"],
            "NO_SEEN" if reach["age_s"] is None else ("%.3f" % reach["age_s"]),
            len(denied), len(asked), _sha256(clock_src)[:16]),
    }
    out = Path(proof_path) if proof_path else (_HERE / PROOF_NAME)
    out.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    rec["proof_path"] = str(out)
    return rec


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(prog="cvm-phone-pull")
    ap.add_argument("--root", required=True,
                    help="COSMOS runtime root (handed in; sentinel verified)")
    ap.add_argument("--reach", action="store_true",
                    help="measure phone reachability (typed, never assumed)")
    ap.add_argument("--gate", action="store_true",
                    help="write " + PROOF_NAME + " bound to emitted values")
    ap.add_argument("--proof", default="")
    ap.add_argument("--deadline", type=float, default=PHONE_DEADLINE_S)
    ns = ap.parse_args(argv)
    if not ns.reach and not ns.gate:
        ap.error("one of --reach / --gate is required")
    if ns.gate:
        rec = run_gate(ns.root, ns.proof or None)
        print(json.dumps(rec, indent=1, default=str))
        return 0
    paths = load_paths(ns.root)
    rec = phone_reach(paths, paths.sentinel.tree_id, deadline_s=ns.deadline)
    print(json.dumps(rec, indent=1, default=str))
    return 0 if rec["reachable"] else 3


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CvmDtError as e:
        print(json.dumps({"ok": False, "kind": str(e.kind), "detail": str(e)},
                         indent=1), file=sys.stderr)
        raise SystemExit(2)
