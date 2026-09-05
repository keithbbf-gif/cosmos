#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_spend_admin - THE WRITE SIDE OF THE MONEY SURFACE (F-03, 2026-08-31).

WHAT THIS CLOSES: `/api/v1/spend` existed only in the GET block - the operator
could SEE every cap and change none of them ("the ability to set/adjust them,
not just view", builds/cdeck/FEATURES_KEITH.md:16,35). This module is the
validated, audited, fail-closed body of `POST /api/v1/spend`; cosmos_service
owns only the dispatch line and the bearer check.

Two targets, exactly one per request (a request that names both, or neither, is
a typed refusal - a money route does not guess what it was asked to change):
  * a RAIL CAP     {"rail": "sgh-api", "cap_usd": 12.5, "expires_epoch": null}
                   -> SpendGate's own BUDGET_SET on the authority ledger
  * the THRESHOLDS {"thresholds": {"session_usd": .., "day_usd": ..,
                                   "rate_per_min": .., "opus_turns_per_session": ..}}
                   -> the SpendGuard/TurnGuard config file, re-read live

THE FOUR RULES THIS MODULE EXISTS TO ENFORCE
1. NEVER SILENTLY WIDEN. Any change that gives the system MORE room to spend -
   a higher cap, a later (or removed) expiry, a bigger session/day/rate/turn
   threshold, or the first budget on a rail that could not spend at all - is
   refused 409 WIDEN_REQUIRES_CONFIRM unless the body carries a literal JSON
   `true` in "allow_widen". Narrowing needs no ceremony: tightening a limit is
   always allowed, which is the asymmetry the control channel already uses (OFF
   is cheap, ON is deliberate). `allow_widen` must be a real bool - the string
   "false" is truthy in Python and would have widened a cap while SAYING no.
2. ONE ATOMIC DECISION. The read-decide-write runs inside Ledger.append_guarded,
   so two overlapping cap writes cannot both pass the widen check against the
   same stale projection (the RG-B1 overlap scar, measured, in cosmos_spend).
3. THE RECORD ANSWERS "WHO CHANGED WHAT FROM WHAT TO WHAT". The audit fields
   ride INSIDE the BUDGET_SET payload rather than in a second event, so the
   change and its provenance land in ONE signed append that cannot half-happen:
   actor (the bearer's sha256 prefix - never key material), prev_cap_usd,
   prev_expires_epoch, direction, confirmed_widen, reason, client_id, source.
   SpendGate's fold reads rail/cap_usd/expires_epoch and ignores the rest.
   A semantic refusal appends SPEND_CAP_REFUSED - a denied money change is
   itself worth a trace.
4. rc=0 IS NOT THE PROOF. Every apply re-derives the state from the on-disk
   chain (SpendGate.audit -> project -> verify, which re-verifies every HMAC)
   and refuses ROUND_TRIP_UNVERIFIED rather than report a write the artifact
   does not show. The threshold write ROLLS BACK to the prior bytes if the
   re-read disagrees - a half-written config would fail voice closed.

Stdlib only. No hard-coded paths (the config path is handed in). Nothing here
prints, spawns, or reads key material.
"""
from __future__ import annotations

import json
import math
import os
import re
import time
from pathlib import Path
from typing import Any, Optional

SCHEMA = "cosmos-spend-admin/1"
SOURCE = "POST /api/v1/spend"

#: Every refusal this module can raise, enumerated so a caller branches on a
#: token instead of parsing prose.
KINDS = (
    "BAD_REQUEST",            # body is not a JSON object
    "BAD_TARGET",             # neither, or both, of rail / thresholds
    "BAD_FIELD",              # unknown key, or a flag that is not a real bool
    "BAD_RAIL",               # rail is not a usable rail id
    "BAD_CAP",                # cap is not a finite, non-negative, bounded USD
    "BAD_EXPIRY",             # expiry is not a finite, bounded epoch
    "BAD_THRESHOLD",          # a threshold is missing, mistyped, or out of range
    "WIDEN_REQUIRES_CONFIRM",  # the change would give MORE room; say so explicitly
    "BELOW_OUTSTANDING",      # cap under settled+reserved: every later call DENIES
    "CURRENT_UNREADABLE",     # cannot establish the BEFORE state -> cannot prove
    "ROUND_TRIP_UNVERIFIED",  # the re-read does not show the write
    "LEDGER_REFUSED",         # the chain would not verify
    "SPEND_NOT_COMPOSED",     # kernel has no SpendGate
    "GUARD_NOT_COMPOSED",     # no SpendGuard / no config path
)

#: HTTP status per kind. Anything unlisted is a 400 - a refusal never 500s by
#: default, and a 500 is reserved for "we wrote and cannot prove it".
_STATUS = {
    "WIDEN_REQUIRES_CONFIRM": 409,
    "BELOW_OUTSTANDING": 409,
    "CURRENT_UNREADABLE": 500,
    "ROUND_TRIP_UNVERIFIED": 500,
    "LEDGER_REFUSED": 500,
    "SPEND_NOT_COMPOSED": 503,
    "GUARD_NOT_COMPOSED": 503,
}

MAX_CAP_USD = 100_000.0          # a cap above this is a typo, not a budget
MAX_EXPIRY_HORIZON_S = 10 * 365 * 86400   # ten years out; past that is a typo
MAX_REASON = 200
MAX_CLIENT_ID = 120
_RAIL_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:+-]{0,63}$")

_TOP_KEYS = frozenset({
    "rail", "cap_usd", "expires_epoch", "thresholds",
    "allow_widen", "allow_below_outstanding", "reason", "client_id",
})

#: threshold key -> (python type, min, max). Every one of these is a live knob
#: already read on every check by SpendGuard._caps / TurnGuard._cap_now.
THRESHOLD_SPEC = {
    "session_usd": (float, 0.0, 1_000.0),
    "day_usd": (float, 0.0, 10_000.0),
    "rate_per_min": (int, 0, 10_000),
    "opus_turns_per_session": (int, 0, 10_000),
}


class SpendAdminError(RuntimeError):
    """kind in KINDS. `detail` names the number, never the secret."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")

    @property
    def status(self) -> int:
        return _STATUS.get(self.kind, 400)

    def as_dict(self) -> dict:
        return {"ok": False, "error": self.kind, "kind": self.kind,
                "detail": str(self)[:400], "schema": SCHEMA}


# ------------------------------------------------------------- validation ---
def _num(value: Any, kind: str, label: str) -> float:
    """A finite JSON number. bool is not a number (True would read as $1)."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise SpendAdminError(kind, f"{label} {value!r} is not a number")
    f = float(value)
    if math.isnan(f) or math.isinf(f):
        raise SpendAdminError(kind, f"{label} {value!r} is not finite")
    return f


def _flag(payload: dict, name: str) -> bool:
    """A confirmation flag must be a LITERAL JSON bool. `bool("false")` is True
    and `bool("no")` is True - accepting a truthy string here would widen a cap
    on a body that said the opposite."""
    v = payload.get(name, False)
    if not isinstance(v, bool):
        raise SpendAdminError(
            "BAD_FIELD",
            f"{name} must be a JSON true/false, not {type(v).__name__} {v!r} - "
            f"a truthy string is not consent")
    return v


def validate(payload: Any, *, now: float) -> dict:
    """Body -> normalized request, or a typed refusal. No side effects."""
    if not isinstance(payload, dict):
        raise SpendAdminError("BAD_REQUEST", "body is not a JSON object")
    unknown = sorted(set(payload) - _TOP_KEYS)
    if unknown:
        raise SpendAdminError(
            "BAD_FIELD",
            f"unknown field(s) {unknown} - a money route refuses what it does "
            f"not understand rather than ignoring it")
    reason = payload.get("reason", "")
    if not isinstance(reason, str) or len(reason) > MAX_REASON:
        raise SpendAdminError("BAD_FIELD",
                              f"reason must be a string of <= {MAX_REASON} chars")
    client_id = payload.get("client_id", "")
    if not isinstance(client_id, str) or len(client_id) > MAX_CLIENT_ID:
        raise SpendAdminError("BAD_FIELD",
                              f"client_id must be a string of <= {MAX_CLIENT_ID} chars")
    req = {"allow_widen": _flag(payload, "allow_widen"),
           "allow_below_outstanding": _flag(payload, "allow_below_outstanding"),
           "reason": reason, "client_id": client_id}

    has_rail = "rail" in payload or "cap_usd" in payload
    has_thr = "thresholds" in payload
    if has_rail and has_thr:
        raise SpendAdminError(
            "BAD_TARGET",
            "name a rail cap OR thresholds, never both in one request - a money "
            "route does not guess which half of a body it was meant to apply")
    if not has_rail and not has_thr:
        raise SpendAdminError(
            "BAD_TARGET",
            'nothing to set: send {"rail","cap_usd"} or {"thresholds":{...}}')

    if has_rail:
        rail = payload.get("rail")
        if not isinstance(rail, str) or not _RAIL_RE.match(rail):
            raise SpendAdminError(
                "BAD_RAIL",
                f"rail {rail!r} is not a usable rail id "
                f"(1-64 chars of A-Za-z0-9 . _ : + -)")
        if "cap_usd" not in payload:
            raise SpendAdminError("BAD_CAP", "cap_usd is required with a rail")
        cap = _num(payload.get("cap_usd"), "BAD_CAP", "cap_usd")
        if cap < 0:
            raise SpendAdminError("BAD_CAP", f"cap_usd {cap} is negative - a cap "
                                             f"is not a debt")
        if cap > MAX_CAP_USD:
            raise SpendAdminError("BAD_CAP",
                                  f"cap_usd {cap} exceeds the ${MAX_CAP_USD:,.0f} "
                                  f"sanity ceiling - that is a typo, not a budget")
        exp = payload.get("expires_epoch", None)
        if exp is not None:
            exp = _num(exp, "BAD_EXPIRY", "expires_epoch")
            if exp <= 0 or exp > now + MAX_EXPIRY_HORIZON_S:
                raise SpendAdminError(
                    "BAD_EXPIRY",
                    f"expires_epoch {exp} is not a bounded future-shaped epoch "
                    f"(0 < t <= now + 10 years)")
        req.update({"target": "rail", "rail": rail, "cap_usd": cap,
                    "expires_epoch": exp,
                    "expiry_given": "expires_epoch" in payload})
        return req

    thr = payload.get("thresholds")
    if not isinstance(thr, dict) or not thr:
        raise SpendAdminError("BAD_THRESHOLD",
                              "thresholds must be a non-empty JSON object")
    bad = sorted(set(thr) - set(THRESHOLD_SPEC))
    if bad:
        raise SpendAdminError(
            "BAD_THRESHOLD",
            f"unknown threshold(s) {bad} - known: {sorted(THRESHOLD_SPEC)}")
    out = {}
    for k, v in thr.items():
        typ, lo, hi = THRESHOLD_SPEC[k]
        f = _num(v, "BAD_THRESHOLD", k)
        if typ is int and f != int(f):
            raise SpendAdminError("BAD_THRESHOLD",
                                  f"{k} {v!r} must be a whole number")
        if not (lo <= f <= hi):
            raise SpendAdminError("BAD_THRESHOLD",
                                  f"{k} {f} is outside [{lo}, {hi}]")
        out[k] = int(f) if typ is int else float(f)
    req.update({"target": "thresholds", "thresholds": out})
    return req


# ------------------------------------------------------------- rail caps ----
def _direction(prev: Optional[dict], cap: float, exp: Optional[float],
               expiry_given: bool) -> str:
    """create | widen | narrow | unchanged. Widening is MORE ROOM TO SPEND, and
    that includes a later or removed expiry - time is budget."""
    if prev is None:
        return "create"
    prev_cap = float(prev.get("cap_usd") or 0.0)
    prev_exp = prev.get("expires_epoch")
    if cap > prev_cap:
        return "widen"
    if expiry_given and prev_exp is not None:
        if exp is None or exp > float(prev_exp):
            return "widen"
    if cap < prev_cap:
        return "narrow"
    if expiry_given and exp is not None and (prev_exp is None
                                             or exp < float(prev_exp)):
        return "narrow"          # putting a clock on a budget only takes room away
    return "unchanged"


def _prev_from_state(gate, rail: str) -> Optional[dict]:
    """The rail's raw fold row (cap + expiry + committed), or None. Uses the
    gate's private _state so the EXPIRY is visible - audit() only surfaces
    expiry as a relative day count."""
    st = gate._state()
    b = st.get(rail)
    if b is None:
        return None
    reserved = sum(r["usd"] for r in b["reserved"].values())
    return {"cap_usd": float(b["cap"]),
            "expires_epoch": b.get("expires"),
            "settled_usd": round(float(b["settled"]), 6),
            "reserved_usd": round(reserved, 6),
            "headroom_usd": round(float(b["cap"]) - float(b["settled"]) - reserved, 6)}


def apply_rail_cap(kernel, req: dict, actor: str, remote: str = "") -> dict:
    """RE-DECIDE-AND-WRITE under the ledger lock, then prove it from disk.

    The whole decision (before-state, widen check, below-outstanding check) is
    re-derived INSIDE append_guarded, so an overlapping writer cannot slip a
    widen past a check made on a stale projection."""
    gate = getattr(kernel, "spend", None)
    if gate is None:
        raise SpendAdminError("SPEND_NOT_COMPOSED",
                              "kernel has no SpendGate - a composition fault, "
                              "not an empty budget")
    rail, cap = req["rail"], req["cap_usd"]
    exp, expiry_given = req["expires_epoch"], req["expiry_given"]
    try:
        before = _prev_from_state(gate, rail)
    except Exception as e:                                        # noqa: BLE001
        raise SpendAdminError("LEDGER_REFUSED",
                             f"cannot read the current spend state: "
                             f"{type(e).__name__}: {e}") from e
    decided: dict = {}

    def _decide(_recs):
        prev = _prev_from_state(gate, rail)            # re-derived UNDER the lock
        direction = _direction(prev, cap, exp, expiry_given)
        if direction in ("widen", "create") and not req["allow_widen"]:
            prev_txt = (f"${prev['cap_usd']:.2f}" if prev else "no budget at all")
            raise SpendAdminError(
                "WIDEN_REQUIRES_CONFIRM",
                f"{rail}: {prev_txt} -> ${cap:.2f} gives MORE room to spend. A "
                f"cap is never widened silently - resend with "
                f'"allow_widen": true to mean it')
        if prev is not None and not req["allow_below_outstanding"]:
            outstanding = prev["settled_usd"] + prev["reserved_usd"]
            if cap < outstanding:
                raise SpendAdminError(
                    "BELOW_OUTSTANDING",
                    f"{rail}: cap ${cap:.2f} is under settled+reserved "
                    f"${outstanding:.2f} - every later call would DENY while the "
                    f"spend already happened. Pass allow_below_outstanding to mean it")
        decided["prev"] = prev
        decided["direction"] = direction
        # ONE signed append carries both the change and its provenance: the fold
        # reads rail/cap_usd/expires_epoch, the audit reads the rest.
        return ("BUDGET_SET", {
            "rail": rail, "cap_usd": cap, "expires_epoch": exp,
            "actor": actor, "source": SOURCE,
            "prev_cap_usd": (prev["cap_usd"] if prev else None),
            "prev_expires_epoch": (prev["expires_epoch"] if prev else None),
            "direction": direction,
            "confirmed_widen": bool(req["allow_widen"]),
            "confirmed_below_outstanding": bool(req["allow_below_outstanding"]),
            "reason": req["reason"], "client_id": req["client_id"],
            "remote": remote})

    try:
        rec = kernel.ledger.append_guarded(_decide)
    except SpendAdminError as e:
        # a REFUSED money change is worth a trace of its own (bearer-gated, so
        # this cannot be spammed by an anonymous caller)
        _try_append(kernel, "SPEND_CAP_REFUSED", {
            "rail": rail, "requested_cap_usd": cap, "requested_expires_epoch": exp,
            "refused": e.kind, "actor": actor, "source": SOURCE,
            "reason": req["reason"], "client_id": req["client_id"],
            "remote": remote})
        raise
    except Exception as e:                                        # noqa: BLE001
        raise SpendAdminError("LEDGER_REFUSED",
                              f"the cap write did not land: "
                              f"{type(e).__name__}: {e}") from e

    # THE PROOF: re-fold from the on-disk chain (project -> verify re-checks
    # every record's hmac). A 2xx off the append alone is the fake-DONE class.
    after = _prev_from_state(gate, rail)
    if after is None or abs(after["cap_usd"] - cap) > 1e-9:
        raise SpendAdminError(
            "ROUND_TRIP_UNVERIFIED",
            f"{rail}: wrote cap ${cap:.2f} at ledger seq {rec['seq']} but the "
            f"re-read shows {after['cap_usd'] if after else 'no such rail'} - "
            f"refusing to report a write the ledger does not show")
    return {"ok": True, "schema": SCHEMA, "target": "rail", "rail": rail,
            "actor": actor, "direction": decided["direction"],
            "before": decided["prev"], "after": after,
            "round_trip": {
                "verified": True,
                "via": "Ledger.append_guarded(BUDGET_SET) -> SpendGate._state() "
                       "re-folded from the verified on-disk chain",
                "ledger_seq": rec["seq"], "ledger_event": rec["event"],
                "cap_usd": after["cap_usd"],
                "headroom_usd": after["headroom_usd"]}}


def _try_append(kernel, event: str, payload: dict) -> None:
    """Best-effort receipt. A failed trace must never convert a clean typed
    refusal into a 500 - the refusal is the safety behavior."""
    try:
        kernel.ledger.append(event, payload)
    except Exception:                                             # noqa: BLE001
        pass


# ------------------------------------------------------------ thresholds ----
def current_thresholds(guard, config_path: Path, turn_default: int) -> dict:
    """The EFFECTIVE values the breakers are running on right now. Unreadable
    is a refusal, never a default: if the BEFORE state cannot be established,
    non-widening cannot be proven."""
    a = guard.audit()
    if not isinstance(a, dict) or "error" in a:
        raise SpendAdminError(
            "CURRENT_UNREADABLE",
            f"the spend breaker cannot report its own caps "
            f"({(a or {}).get('detail', 'no audit')}) - refusing to change a "
            f"limit whose current value is unknown")
    cur = {"session_usd": float(a["session_cap_usd"]),
           "day_usd": float(a["day_cap_usd"]),
           "rate_per_min": int(a["rate_per_min"]),
           "opus_turns_per_session": int(turn_default)}
    raw = _read_config(config_path)
    if "opus_turns_per_session" in raw:
        try:
            cur["opus_turns_per_session"] = int(raw["opus_turns_per_session"])
        except (TypeError, ValueError) as e:
            raise SpendAdminError(
                "CURRENT_UNREADABLE",
                f"opus_turns_per_session in the config is not an integer: "
                f"{raw['opus_turns_per_session']!r}") from e
    return cur


def _read_config(config_path: Path) -> dict:
    """Absent is an empty config (a legitimate state). Present-and-unparseable
    is a REFUSAL - overwriting it would silently discard live knobs."""
    if not config_path.exists():
        return {}
    try:
        obj = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise SpendAdminError(
            "CURRENT_UNREADABLE",
            f"{config_path.name} exists and does not parse ({e}) - refusing to "
            f"overwrite a config whose current contents are unknown") from e
    if not isinstance(obj, dict):
        raise SpendAdminError("CURRENT_UNREADABLE",
                              f"{config_path.name} is not a JSON object")
    return obj


def apply_thresholds(kernel, guard, config_path, req: dict, actor: str,
                     turn_default: int, remote: str = "") -> dict:
    """Merge the named knobs into the live config, widen-gated, then prove the
    re-read - and ROLL BACK the exact prior bytes if it disagrees."""
    if guard is None or config_path is None:
        raise SpendAdminError("GUARD_NOT_COMPOSED",
                              "no spend breaker is composed - a composition "
                              "fault, not an unlimited budget")
    config_path = Path(config_path)
    before = current_thresholds(guard, config_path, turn_default)
    want = req["thresholds"]
    widened = {k: (before[k], v) for k, v in want.items() if v > before[k]}
    if widened and not req["allow_widen"]:
        detail = ", ".join(f"{k} {a} -> {b}" for k, (a, b) in sorted(widened.items()))
        raise SpendAdminError(
            "WIDEN_REQUIRES_CONFIRM",
            f"{detail} gives MORE room to spend. A threshold is never widened "
            f'silently - resend with "allow_widen": true to mean it')
    changed = {k: {"from": before[k], "to": v}
               for k, v in want.items() if v != before[k]}

    raw = _read_config(config_path)
    prior_bytes = (config_path.read_bytes() if config_path.exists() else None)
    merged = dict(raw)
    merged.update(want)
    _write_config_atomic(config_path, merged)

    after = None
    try:
        after = current_thresholds(guard, config_path, turn_default)
        mismatch = {k: (v, after[k]) for k, v in want.items() if after[k] != v}
    except SpendAdminError:
        mismatch = {k: (v, "unreadable") for k, v in want.items()}
    if mismatch:
        _rollback(config_path, prior_bytes)
        raise SpendAdminError(
            "ROUND_TRIP_UNVERIFIED",
            f"wrote {want} but the breaker re-reads {mismatch} - the prior "
            f"config was restored rather than leave the breaker on a value "
            f"nobody can read back")

    _try_append(kernel, "SPEND_THRESHOLD_CHANGED", {
        "changed": changed, "requested": want, "before": before, "after": after,
        "actor": actor, "source": SOURCE, "config": config_path.name,
        "widened": sorted(widened), "confirmed_widen": bool(req["allow_widen"]),
        "reason": req["reason"], "client_id": req["client_id"], "remote": remote})
    return {"ok": True, "schema": SCHEMA, "target": "thresholds",
            "actor": actor,
            "direction": ("widen" if widened else
                          ("narrow" if changed else "unchanged")),
            "before": before, "after": after, "changed": changed,
            "round_trip": {
                "verified": True,
                "via": "config write -> SpendGuard.audit()/TurnGuard config "
                       "re-read from disk",
                "config": str(config_path)}}


def _write_config_atomic(path: Path, obj: dict) -> None:
    """tmp -> validate -> os.replace. A torn config fails the breakers CLOSED
    (SpendGuard._caps raises, check() refuses), so the half-written file is the
    one outcome worth engineering against."""
    body = json.dumps(obj, indent=1, sort_keys=True)
    json.loads(body)                       # never replace with bytes we cannot read
    tmp = path.with_suffix(path.suffix + ".newcap")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp.write_text(body, encoding="utf-8")
        os.replace(str(tmp), str(path))
    except OSError as e:
        raise SpendAdminError("ROUND_TRIP_UNVERIFIED",
                              f"could not write {path.name}: {e}") from e


def _rollback(path: Path, prior: Optional[bytes]) -> None:
    """Put back exactly what was there. Nothing is deleted: a config that did
    not exist before is emptied to `{}`, which is the same effective state."""
    try:
        path.write_bytes(prior if prior is not None else b"{}\n")
    except OSError:
        pass


# --------------------------------------------------------------- the route --
def handle_post(kernel, guard, config_path, payload: Any, actor: str, *,
                turn_default: int = 0, remote: str = "",
                now: Optional[float] = None) -> tuple:
    """(http_status, body). The whole body of POST /api/v1/spend; the service
    supplies the bearer check, the bounded read, and the actor identity."""
    try:
        req = validate(payload, now=(time.time() if now is None else now))
        if req["target"] == "rail":
            return 200, apply_rail_cap(kernel, req, actor, remote=remote)
        return 200, apply_thresholds(kernel, guard, config_path, req, actor,
                                     turn_default, remote=remote)
    except SpendAdminError as e:
        return e.status, e.as_dict()
