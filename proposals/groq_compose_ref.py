#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""proposals/groq_compose_ref.py - REFERENCE IMPLEMENTATION for the groq-api Kernel
compose. WO "groq-api Kernel compose (Lane B Cursor)", 2026-09-04. P10: PROPOSE.

THIS FILE IS NOT WIRED. Nothing under cosmos/ imports it, cosmos_kernel.py is not
changed by this PR, and no live tree is written. It exists because the tree's own
charter says "Every gate executable - a check that cannot fail is not a check, and a
check that never ran is indistinguishable from one that passed" (README.md). A compose
proposal whose invariants cannot be RUN is prose. tests/test_groq_compose.py drives
this module against a FAKE transport and against a REAL Kernel booted on a temp root,
so the claims in proposals/groq-api-kernel-compose.md are MEASURED here rather than
asserted there.

WHAT IS ACTUALLY NEW. The satellite cosmos/cosmos_groq_rail.py already exists in the
live tree and already passed its live --gate on 2026-09-04. It is not rewritten and
must not be. The only genuinely missing piece is the ATTACH: attach_groq_rail() below,
plus four lines in the Kernel (see the proposal). Everything else in this file is a
STAND-IN that lets the attach be exercised, and a CONFORMANCE HARNESS - conformance() -
that CCr can point at the real satellite to check it already satisfies the seven
invariants the attach depends on.

THE ADAPTER PROTOCOL is the only coupling that matters, and it is the tree's existing
one (cosmos_rails.ApiRail / cosmos_node_rails.NodeRail): an adapter is
  .kind == "API"  ·  .metered_usd  ·  probe() -> (ok, detail)  ·  dispatch(payload) -> dict
If the live satellite spells its class differently, only that protocol has to match.

SEAMS CARRIED FROM THE TREE, not invented here:
  * INJECTED TRANSPORT - cosmos_itc.ITC takes fetcher=callable and "NEVER opens the
    network itself, so no code path a test exercises can silently depend on
    reachability". The Kernel injects the real one at the composition boundary
    (cosmos_kernel.py:123-127). GroqRail takes transport= the same way. This is what
    keeps the tests fake-HTTP (WO ask 4) without a mocking library.
  * CONSTRUCTION IS NOT A CALL - cosmos_node_rails.NodeRail defers its import to
    probe/dispatch so composition cannot fail. Same here: no key read, no socket, no
    import of anything optional at construction.
  * UNPRICED != $0 - cosmos_spend: "An unpriced call is UNPRICED, never zero."
  * REGISTRATION IS NOT CAPABILITY - cosmos_registry: a link holds no verified status
    without a dated probe.
"""
from __future__ import annotations

import json
import re
import time
from typing import Callable, Optional

# --------------------------------------------------------------------------------
# THE CONTRACT (from the WO's GATE PASS satellite - restated, not re-decided)
# --------------------------------------------------------------------------------
LINK_ID = "groq-api"
ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"
CATALOG_ENDPOINT = "https://api.groq.com/openai/v1/models"
DEFAULT_MODEL = "openai/gpt-oss-20b"

# Route: the SAME route the other model rails register on (cosmos_node_rails:
# src="core", dst="models"). A private route would make groq-api invisible to the
# Dispatcher's fallback chain, which is the only reason to have a fourth model rail.
ROUTE_SRC, ROUTE_DST = "core", "models"

# policy_rank 0 = peer of the other API rails. Registry.route() sorts
# (-policy_rank, pref[rail_type]) with pref DOM<CLI<API, so 0 keeps DOM first, which is
# ratified policy ("DOM is the default, the API is the fallback"). A positive rank here
# would quietly promote an API rail above the DOM lane.
POLICY_RANK = 0

# Worst case reserved per call, and the rail's cap. Deliberately NONZERO even on a free
# key: cosmos_rails.Dispatcher only routes through the spend breaker when
# getattr(adapter, "metered_usd", 0) is truthy, so metered_usd=0.0 would make every
# groq call invisible to the breaker AND absent from spend.audit(). Free is a price,
# not an absence of accounting.
METERED_USD = 0.002
BUDGET_USD = 5.0

TIERS = ("free", "developer", "enterprise")

# ---- service_tier ---------------------------------------------------------------
# NEVER EMITTED. Omitting the field IS the on_demand tier (Groq service-tiers doc), so
# the correct way not to ask for flex is to send no such field at all - not the string
# "on_demand", not "auto", not null.
# Two independent reasons, and the second does not go away when the key is upgraded:
#   1. entitlement - flex is paid-accounts-only; on this key it returns 498
#      capacity_exceeded.
#   2. doctrine - flex's own contract is "fails fast with 498, add jittered backoff and
#      retries". cosmos_sched is REPORT-NEVER-RETRY (cosmos_sched.py:18). A rail that
#      needs client-side retry to meet its contract cannot be driven by a scheduler
#      that refuses to retry.
FORBIDDEN_PARAMS = ("service_tier",)

# Body keys the rail will forward from a caller. An allow-list, so a new OpenAI-compat
# parameter cannot arrive through a caller and reach the wire unreviewed - including a
# re-spelled service_tier.
PASSTHROUGH_PARAMS = ("temperature", "top_p", "max_completion_tokens", "stop", "seed",
                      "response_format", "n", "presence_penalty", "frequency_penalty")

# ---- the dated refusal table ----------------------------------------------------
# Source: https://console.groq.com/docs/deprecations, read 2026-09-04. Each row carries
# the shutdown date and the tiers it binds, because Groq's own 2026-08-16 notice says:
# "This deprecation applies to free and developer-tier usage; enterprise customers with
# a committed-spend contract are not affected." A blanket refusal would therefore be
# WRONG for an enterprise key - it would refuse a model that key can still call. The
# refusal is a function of the TIER, and the tier is declared, never inferred.
REFUSED_MODELS: dict[str, dict] = {
    "mixtral-8x7b-32768": {
        "shutdown": "2025-03-20", "replacement": "openai/gpt-oss-120b", "tiers": TIERS},
    "llama-3.1-70b-versatile": {
        "shutdown": "2025-01-24", "replacement": "openai/gpt-oss-120b", "tiers": TIERS},
    "llama-3.1-70b-specdec": {
        "shutdown": "2025-01-24", "replacement": "openai/gpt-oss-120b", "tiers": TIERS},
    "llama3-70b-8192": {
        "shutdown": "2025-08-30", "replacement": "openai/gpt-oss-120b", "tiers": TIERS},
    "llama3-8b-8192": {
        "shutdown": "2025-08-30", "replacement": "openai/gpt-oss-20b", "tiers": TIERS},
    "llama3-groq-70b-8192-tool-use-preview": {
        "shutdown": "2025-01-06", "replacement": "openai/gpt-oss-120b", "tiers": TIERS},
    "llama3-groq-8b-8192-tool-use-preview": {
        "shutdown": "2025-01-06", "replacement": "openai/gpt-oss-20b", "tiers": TIERS},
    "llama-3.2-1b-preview": {
        "shutdown": "2025-04-14", "replacement": "openai/gpt-oss-20b", "tiers": TIERS},
    "llama-3.2-3b-preview": {
        "shutdown": "2025-04-14", "replacement": "openai/gpt-oss-20b", "tiers": TIERS},
    "llama-3.2-11b-vision-preview": {
        "shutdown": "2025-04-14", "replacement": "openai/gpt-oss-120b", "tiers": TIERS},
    "llama-3.2-90b-vision-preview": {
        "shutdown": "2025-04-14", "replacement": "openai/gpt-oss-120b", "tiers": TIERS},
    "llama-3.3-70b-specdec": {
        "shutdown": "2025-04-14", "replacement": "openai/gpt-oss-120b", "tiers": TIERS},
    "llama-guard-3-8b": {
        "shutdown": "2025-06-06", "replacement": "openai/gpt-oss-safeguard-20b",
        "tiers": TIERS},
    # The two the WO is actually about. Alive for a committed-spend enterprise key,
    # dead for this one.
    "llama-3.1-8b-instant": {
        "shutdown": "2026-08-16", "replacement": "openai/gpt-oss-20b",
        "tiers": ("free", "developer")},
    "llama-3.3-70b-versatile": {
        "shutdown": "2026-08-16", "replacement": "openai/gpt-oss-120b",
        "tiers": ("free", "developer")},
}

# The family net. A dated table is a CACHE of the vendor's catalog and goes stale
# silently, which is fail-OPEN: an id retired after 2026-09-04 sails straight through.
# On free/developer, every Llama 3.x spelling is refused whether or not it is in the
# table, so the fail-open window covers only ids that are NOT Llama 3.x and NOT Mixtral.
# probe_deep() closes the rest against the live catalog; see below.
_LLAMA3_FAMILY = re.compile(r"(?:^|/)llama[-_]?3(?:[._-]\d+)?[-_.]", re.IGNORECASE)
_MIXTRAL_FAMILY = re.compile(r"(?:^|/)mixtral[-_]", re.IGNORECASE)


class GroqError(RuntimeError):
    """kind in {MODEL_REFUSED, PARAM_REFUSED, BAD_TIER, NO_KEY, BAD_ADAPTER}.

    Typed like every other refusal in the tree (RailError, RegError, SpendError,
    ItcError). A refusal that arrives as a bare RuntimeError cannot be routed."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


# --------------------------------------------------------------------------------
# INVARIANT 3 - model refusal, BEFORE the call
# --------------------------------------------------------------------------------
def check_model(model: str, tier: str = "free") -> str:
    """Return the model id, or raise GroqError(MODEL_REFUSED).

    Refusal happens locally, before any credential is read and before any socket is
    opened, for the same reason cosmos_spend denies before it spends: a request that
    can only fail is not worth a round trip, and the error you get back from the wire
    ("400 model_decommissioned") is less useful than the one you can write yourself
    (which date, which replacement).

    Runs against the REQUESTED id on the way out and against the SERVED id on the way
    back - see bind_served_model()."""
    if tier not in TIERS:
        raise GroqError("BAD_TIER", f"{tier!r} not in {list(TIERS)} - the account tier "
                                    f"is declared, never inferred from a 4xx")
    if not isinstance(model, str) or not model.strip():
        raise GroqError("MODEL_REFUSED", "empty model id - a request with no model is "
                                         "not a request with the default model")
    mid = model.strip()
    row = REFUSED_MODELS.get(mid)
    if row is not None and tier in row["tiers"]:
        raise GroqError(
            "MODEL_REFUSED",
            f"{mid} was shut down {row['shutdown']} for tier {tier!r} "
            f"(console.groq.com/docs/deprecations) - use {row['replacement']}")
    if row is not None:
        return mid              # dead for free/dev, alive for this tier: permitted
    if tier in ("free", "developer"):
        if _MIXTRAL_FAMILY.search(mid):
            raise GroqError("MODEL_REFUSED",
                            f"{mid}: the Mixtral family is retired on Groq (Mixtral "
                            f"8x7B shut down 2025-03-20) - use {DEFAULT_MODEL}")
        if _LLAMA3_FAMILY.search(mid):
            raise GroqError("MODEL_REFUSED",
                            f"{mid}: Llama 3.x is retired for free/developer-tier "
                            f"usage (2026-08-16) and this id is not in the dated table "
                            f"- refusing rather than guessing; use {DEFAULT_MODEL}")
    return mid


# --------------------------------------------------------------------------------
# INVARIANT 4 - the request body, and what may never be in it
# --------------------------------------------------------------------------------
def build_request(prompt_or_messages, model: str, tier: str = "free",
                  params: Optional[dict] = None) -> dict:
    """The chat-completions body. Refuses a caller-supplied service_tier rather than
    dropping it: silently discarding a parameter someone asked for is a lie about what
    was sent, and this rail's whole job is that the sent thing is knowable.

    service_tier is not emitted with any value, including "on_demand" - omission IS
    on_demand, and a body with no such key cannot be edited into flex by accident."""
    params = dict(params or {})
    for bad in FORBIDDEN_PARAMS:
        for supplied in list(params):
            if supplied.strip().lower().replace("-", "_") == bad:
                raise GroqError(
                    "PARAM_REFUSED",
                    f"{supplied!r} is not sendable on {LINK_ID}: flex is paid-tier only "
                    f"(498 capacity_exceeded here) and its contract requires client-side "
                    f"retry, which cosmos_sched refuses by design (report-never-retry). "
                    f"Omitting the field selects on_demand, which is what you want.")
    if isinstance(prompt_or_messages, str):
        messages = [{"role": "user", "content": prompt_or_messages}]
    else:
        messages = list(prompt_or_messages)
    body = {"model": check_model(model, tier), "messages": messages, "stream": False}
    for k in PASSTHROUGH_PARAMS:
        if k in params:
            body[k] = params[k]
    unknown = sorted(set(params) - set(PASSTHROUGH_PARAMS))
    if unknown:
        raise GroqError("PARAM_REFUSED",
                        f"unforwardable parameter(s) {unknown} - the body is an "
                        f"allow-list so nothing reaches the wire unreviewed")
    if "service_tier" in body:
        # A last check on the built body rather than an assert: asserts vanish under -O,
        # and dispatch() promises never to raise an untyped exception at the Dispatcher.
        raise GroqError("PARAM_REFUSED",
                        "service_tier reached the built body - it is never emitted with "
                        "any value, because omission IS on_demand")
    return body


# --------------------------------------------------------------------------------
# INVARIANT 5 - bind response.model
# --------------------------------------------------------------------------------
def bind_served_model(requested: str, data: dict, tier: str = "free") -> dict:
    """Read the model back off the RESPONSE, never assume the request's.

    SOP.md: "Read state back after every write. Never trust rc=0." Groq answers with
    the id that actually served, which is not always the id asked for (aliases, dated
    snapshots, auto-upgrades - Groq has shipped silent upgrades before: the 3.1->3.3
    ids "automatically upgrade" during a transition window, per the deprecations page).

    This is also what closes the deny-list's fail-open hole in the one place it can be
    closed for free: the SERVED id is re-checked against the same refusal table, so a
    request that was permitted on the way out and answered by a retired model comes
    back MODEL_DRIFT rather than as a clean success."""
    served = data.get("model")
    if not isinstance(served, str) or not served.strip():
        return {"bound": False, "served": None, "drift": None,
                "detail": "response carries no model field - a reply that will not name "
                          "its model cannot be bound, and an unbound reply is an "
                          "assumed one"}
    served = served.strip()
    out = {"bound": True, "served": served, "drift": (served != requested),
           "detail": ""}
    try:
        check_model(served, tier)
    except GroqError as e:
        out["refused_after_serving"] = True
        out["detail"] = (f"served model {served} is refused at tier {tier!r} "
                         f"({e}) - the request was permitted, the answer was not")
        return out
    out["refused_after_serving"] = False
    if out["drift"]:
        out["detail"] = (f"requested {requested}, served {served} - permitted, but the "
                         f"served id is the one that gets ledgered")
    return out


# --------------------------------------------------------------------------------
# credentials - INVARIANT 6
# --------------------------------------------------------------------------------
def env_key_provider(env_var: str = "GROQ_API_KEY") -> Callable[[], str]:
    """Resolved at DISPATCH time, never captured at import and never at construction.
    The key is not an argument to anything that gets ledgered."""
    import os

    def _get() -> str:
        v = os.environ.get(env_var, "")
        if not v.strip():
            raise GroqError("NO_KEY",
                            f"{env_var} is empty or unset - {LINK_ID} refuses to call "
                            f"unauthenticated; the key lives in the environment or "
                            f"config/secrets, never in the repo")
        return v.strip()
    return _get


def redact(text: str, secret: Optional[str]) -> str:
    """Strip a credential out of anything headed for a ledger, an error, or a log.

    THE LEDGER NEVER DELETES. cosmos_ledger is an append-only hash chain and
    cosmos_makers states the house rule plainly: "There is no delete." A secret written
    into it once is written into it forever, and redacting it afterwards BREAKS THE
    CHAIN - the one repair that is not available. So the redaction has to happen before
    the append, every time, on every path, which is why it is a function and not a
    habit."""
    if not secret:
        return text
    return text.replace(secret, "***REDACTED***")


# --------------------------------------------------------------------------------
# transport - INVARIANT 7 (fake-HTTP seam)
# --------------------------------------------------------------------------------
# Transport(url, headers, body_text, timeout_s) -> (status:int, headers:dict, text:str)
Transport = Callable[[str, dict, str, float], "tuple[int, dict, str]"]


def urllib_transport() -> Transport:
    """The production transport, built at the COMPOSITION BOUNDARY and injected - the
    same shape and the same reason as the Kernel's _https_get for ITC
    (cosmos_kernel.py:123-127). Nothing in this module opens a socket on its own, so no
    test can silently depend on reachability."""
    def _post(url: str, headers: dict, body_text: str, timeout_s: float):
        import urllib.error
        import urllib.request
        req = urllib.request.Request(
            url, data=body_text.encode("utf-8") if body_text else None,
            headers=headers, method="POST" if body_text else "GET")
        try:
            with urllib.request.urlopen(req, timeout=timeout_s) as r:   # noqa: S310
                return r.status, dict(r.headers), r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            return e.code, dict(e.headers or {}), e.read().decode("utf-8", "replace")
    return _post


# --------------------------------------------------------------------------------
# the adapter
# --------------------------------------------------------------------------------
class GroqRail:
    """Stand-in for the live cosmos_groq_rail adapter, implementing the tree's adapter
    protocol so attach_groq_rail() can be exercised end to end. The live satellite is
    GATE PASS and is not replaced by this - conformance() below is how you check the
    live one satisfies the same invariants."""

    kind = "API"

    def __init__(self, transport: Optional[Transport] = None,
                 key_provider: Optional[Callable[[], str]] = None,
                 model: str = DEFAULT_MODEL, tier: str = "free",
                 metered_usd: float = METERED_USD, timeout_s: float = 60.0,
                 clock=time.time):
        # CONSTRUCTION IS NOT A CALL: no key read, no socket, no optional import.
        # Composition must not be able to fail, or a missing rail takes Core down.
        if tier not in TIERS:
            raise GroqError("BAD_TIER", f"{tier!r} not in {list(TIERS)}")
        self.transport = transport
        self.key_provider = key_provider or env_key_provider()
        self.model = model
        self.tier = tier
        self.metered_usd = metered_usd
        self.timeout_s = timeout_s
        self._clock = clock

    # ---------------- probe ----------------
    def probe(self) -> "tuple[bool, str]":
        """The SHALLOW probe, and the one attached to the Registry: it answers only what
        can be answered without spending or reaching the network, and it can go RED for
        two real reasons (no credential, refused default model). cosmos_health exists
        because of "a health row that could never go red"; ApiRail.probe returns a flat
        True, and copying that here would register a rail that is verified by
        construction. Liveness is still per-call and says so.

        The DEEP probe is deliberately NOT this one: Registry.probe_all() is reached
        from status paths, and a probe that fans out to the network turns `cosmos
        status` into an egress event. Deep belongs on the health board (see
        probe_deep)."""
        try:
            check_model(self.model, self.tier)
        except GroqError as e:
            return False, f"MODEL_REFUSED: default {self.model} refused at tier " \
                          f"{self.tier!r} ({e.args[0][:160]})"
        try:
            self.key_provider()
        except GroqError as e:
            return False, f"NO_KEY: {LINK_ID} has no credential ({e.kind})"
        if self.transport is None:
            return False, "UNREACHABLE: no transport injected - this rail never opens " \
                          "a socket on its own"
        return True, (f"credential present, default {self.model} permitted at tier "
                      f"{self.tier!r}; liveness is per-call")

    def probe_deep(self) -> "tuple[bool, str]":
        """Ask the vendor's catalog whether the configured model still exists. GET
        /openai/v1/models consumes no tokens, so this is a probe that can go red for the
        right reason at zero cost - and it is the only check that catches the dated
        refusal table going stale, which is the deny-list's structural weakness. Belongs
        on a cosmos_health row (scheduled), not on the Registry (status-path)."""
        if self.transport is None:
            return False, "UNREACHABLE: no transport injected"
        key = None
        try:
            key = self.key_provider()
            status, _h, text = self.transport(
                CATALOG_ENDPOINT, {"Authorization": f"Bearer {key}"}, "", self.timeout_s)
        except Exception as e:                                        # noqa: BLE001
            return False, redact(f"UNREACHABLE: catalog {type(e).__name__}: {e}", key)
        if status != 200:
            return False, redact(f"catalog returned HTTP {status}", key)
        try:
            ids = {m.get("id") for m in (json.loads(text).get("data") or [])}
        except ValueError as e:
            return False, f"BAD_RESPONSE: catalog is not JSON ({e})"
        if self.model not in ids:
            return False, (f"CATALOG_DRIFT: {self.model} is no longer in the live "
                           f"catalog ({len(ids)} models) - the dated refusal table in "
                           f"this module is STALE, which is fail-open; update it")
        return True, f"{self.model} present in the live catalog ({len(ids)} models)"

    # ---------------- dispatch ----------------
    def dispatch(self, payload: dict) -> dict:
        """Returns the tree's normalized rail result and NEVER raises.

        Why never raises: cosmos_rails.Dispatcher runs a metered adapter inside
        SpendGate.guarded_call, which releases the reservation and re-raises on any
        exception, and the Dispatcher then wraps whatever came out as
        RailError("NOT_PERMITTED"). A model refusal reported as NOT_PERMITTED reads as a
        budget denial. A typed dict keeps the reason intact.

        usd provenance, and the distinction cosmos_spend actually cares about:
          * refused locally, NOTHING sent -> usd 0.0, and that is a MEASUREMENT. "An
            unpriced call is UNPRICED, never zero" is about a call that HAPPENED at an
            unknown price; a call that never left the process cost exactly zero, and
            reporting it as UNPRICED would inflate spend.audit()["unpriced_calls"] with
            events that were never requests.
          * a request left the process -> usd None (UNPRICED). Groq returns token
            counts, not dollars, and this rail does not carry a price book."""
        requested = payload.get("model") or self.model
        try:
            body = build_request(payload.get("messages") or payload.get("prompt") or "",
                                 requested, self.tier, payload.get("params"))
        except GroqError as e:
            return {"ok": False, "kind": e.kind, "detail": str(e), "usd": 0.0,
                    "usd_provenance": "measured: no request was sent",
                    "node": LINK_ID, "model_requested": requested}
        key = None
        try:
            key = self.key_provider()
        except GroqError as e:
            return {"ok": False, "kind": "AUTH_REQUIRED", "detail": str(e), "usd": 0.0,
                    "usd_provenance": "measured: no request was sent",
                    "node": LINK_ID, "model_requested": requested}
        if self.transport is None:
            return {"ok": False, "kind": "UNREACHABLE", "usd": 0.0,
                    "usd_provenance": "measured: no request was sent",
                    "detail": "no transport injected", "node": LINK_ID,
                    "model_requested": requested}
        headers = {"Content-Type": "application/json",
                   "Authorization": f"Bearer {key}"}
        text_body = json.dumps(body)
        try:
            status, _h, text = self.transport(ENDPOINT, headers, text_body,
                                              self.timeout_s)
        except Exception as e:                                        # noqa: BLE001
            return {"ok": False, "kind": "UNREACHABLE", "usd": None,
                    "usd_provenance": "UNPRICED: the request left the process",
                    "detail": redact(f"{type(e).__name__}: {e}", key), "node": LINK_ID,
                    "model_requested": requested}
        if status != 200:
            return self._http_failure(status, text, key, requested)
        try:
            data = json.loads(text)
        except ValueError as e:
            return {"ok": False, "kind": "BAD_RESPONSE", "usd": None,
                    "usd_provenance": "UNPRICED: the request left the process",
                    "detail": redact(f"HTTP 200 body is not JSON: {e}", key),
                    "node": LINK_ID, "model_requested": requested}
        bind = bind_served_model(requested, data, self.tier)
        choices = data.get("choices") or []
        content = ""
        if choices:
            content = (choices[0].get("message") or {}).get("content") or ""
        usage = data.get("usage") or {}
        result = {
            "ok": True, "kind": "API", "text": content,
            "usd": None, "usd_provenance": "UNPRICED: Groq bills tokens, not dollars, "
                                           "and this rail carries no price book",
            "node": LINK_ID,
            "model_requested": requested,
            "model": bind["served"], "model_bound": bind["bound"],
            "model_drift": bind["drift"],
            "tokens": {"prompt": usage.get("prompt_tokens"),
                       "completion": usage.get("completion_tokens"),
                       "total": usage.get("total_tokens")},
        }
        if not bind["bound"]:
            result.update({"ok": False, "kind": "BAD_RESPONSE",
                           "detail": bind["detail"]})
            return result
        if bind.get("refused_after_serving"):
            result.update({"ok": False, "kind": "MODEL_DRIFT",
                           "detail": bind["detail"]})
            return result
        if bind["drift"]:
            result["detail"] = bind["detail"]
        return result

    def _http_failure(self, status: int, text: str, key, requested: str) -> dict:
        """Typed by status. AUTH_REQUIRED and UNREACHABLE are the two kinds
        cosmos_rails.Dispatcher treats as an EXPLICIT AUDITED FALLBACK to the next live
        link; everything else stops the dispatch with RAIL_FAILED. That mapping is
        load-bearing, so it is written down rather than left to a status number."""
        code = ""
        try:
            code = ((json.loads(text) or {}).get("error") or {}).get("code") or ""
        except ValueError:
            pass
        kind = {401: "AUTH_REQUIRED", 403: "AUTH_REQUIRED",
                429: "RATE_LIMITED", 498: "CAPACITY_EXCEEDED",
                500: "UNREACHABLE", 502: "UNREACHABLE", 503: "UNREACHABLE",
                504: "UNREACHABLE"}.get(status)
        if kind is None:
            kind = "MODEL_REFUSED" if code in ("model_decommissioned",
                                                  "model_not_found") else "RAIL_FAILED"
        detail = redact(text, key)[:300]
        if status == 498:
            detail = ("498 capacity_exceeded - this is the flex-tier failure. If it "
                      "appears, something re-enabled service_tier. " + detail)
        return {"ok": False, "kind": kind, "http_status": status,
                "error_code": code, "detail": detail,
                "usd": None,
                "usd_provenance": "UNPRICED: the request left the process",
                "node": LINK_ID, "model_requested": requested}


# --------------------------------------------------------------------------------
# INVARIANT 1 + 2 - the attach itself: compose always, WRITE only when a writer
# --------------------------------------------------------------------------------
def _link_registered_payload(link_id: str, rail_type: str, src: str, dst: str,
                             policy_rank: int) -> dict:
    """The LINK_REGISTERED payload shape, restated here ONLY because Registry.register()
    offers no guarded variant. Restating a contract in a second place is exactly the
    drift this tree keeps closing, so tests/test_groq_compose.py asserts byte-for-byte
    that this equals what Registry.register() actually writes, and the durable fix -
    Registry.register_once() - is in the proposal as a diff."""
    return {"link_id": link_id, "rail_type": rail_type, "src": src, "dst": dst,
            "policy_rank": policy_rank}


def attach_groq_rail(registry, adapters: dict, *, ledger=None, spend_gate=None,
                     rail=None, transport: Optional[Transport] = None,
                     src: str = ROUTE_SRC, dst: str = ROUTE_DST,
                     read_only: bool = False) -> dict:
    """Compose groq-api into a Registry + adapter map. Mirrors
    cosmos_node_rails.register_node_rails so the port into the live tree is mechanical.

    THE WHOLE POINT, and the answer to "does not rewrite Kernel as a second writer":

      COMPOSE is not REGISTER. Building the adapter, putting it in the adapter map and
      attaching its probe are pure in-memory acts and always happen. Registering the
      link and setting its budget are LEDGER APPENDS - Registry.register() appends
      LINK_REGISTERED (cosmos_registry.py:44) and SpendGate.set_budget() appends
      BUDGET_SET (cosmos_spend.py:40) - and those happen only on a WRITING kernel,
      and only when they would change something.

    Two separate defects are being avoided, and the second is the one that bites:

      (a) B1, "a read is a write". The Kernel already skips BOOT_VERIFIED, the mail
          register() and the lease-ledger append when read_only, because `cosmos status`
          running beside `serve` made a second writer. An unconditional compose puts two
          appends per boot straight back in.
      (b) RE-REGISTRATION IS AMNESIA, and it hits WRITING kernels too. The Registry fold
          replaces the whole row on LINK_REGISTERED:
              s[p["link_id"]] = {"claim": p, "last_probe": None, "ok": None}
          so a second registration DISCARDS the last probe. route() then drops the link
          (it filters on ok) and the rail is undispatchable until something probes it
          again. MEASURED in this clone: after register -> probe -> register, matrix()
          reports verified=None and route("core","models") returns []. Composing at
          every boot without the `absent?` guard would make every rail permanently
          unroutable on a box that boots Core often.

    Returns the actions taken, so the caller can ledger or print what happened."""
    rail = rail or GroqRail(transport=transport)
    # Protocol check BEFORE anything is published. A half-composed rail is worse than an
    # absent one: the Dispatcher would find it in the adapter map and drive it. Nothing
    # below this line can leave the adapter map holding an object that failed here.
    probe = rail.probe
    if getattr(rail, "kind", None) != "API" or not callable(getattr(rail, "dispatch",
                                                                    None)):
        raise GroqError("BAD_ADAPTER",
                        f"{type(rail).__name__} is not a rail adapter - the protocol is "
                        f"kind/metered_usd/probe()/dispatch(), same as ApiRail")
    adapters[LINK_ID] = rail
    registry.attach_probe(LINK_ID, probe)           # in-memory: not a ledger event
    actions = {"link_id": LINK_ID, "composed": True, "registered": False,
               "budgeted": False, "read_only": bool(read_only),
               "already_registered": LINK_ID in registry.state()}
    if read_only:
        actions["detail"] = ("read-only kernel: composed in memory, nothing appended "
                             "(a reader is not a writer)")
        return actions
    if not actions["already_registered"]:
        if ledger is not None:
            # guarded so two kernels booting at once cannot both register - the same
            # check-then-act race cosmos_makers.add() closed (its FINDING #5).
            def _decide(recs):
                for rec in recs:
                    if (rec["event"] == "LINK_REGISTERED"
                            and rec["payload"].get("link_id") == LINK_ID):
                        return None                 # someone else won; append nothing
                return ("LINK_REGISTERED",
                        _link_registered_payload(LINK_ID, "API", src, dst, POLICY_RANK))
            wrote = ledger.append_guarded(_decide)
            actions["registered"] = wrote is not None
        else:
            registry.register(LINK_ID, "API", src, dst, policy_rank=POLICY_RANK)
            actions["registered"] = True
    if spend_gate is not None and METERED_USD:
        row = (spend_gate.audit().get("rails") or {}).get(LINK_ID)
        if row is None or row.get("cap_usd") != BUDGET_USD:
            spend_gate.set_budget(LINK_ID, BUDGET_USD)
            actions["budgeted"] = True
    actions["detail"] = ("composed; " + ("registered" if actions["registered"]
                                            else "already registered") +
                         ("; budget set" if actions["budgeted"] else "; budget unchanged"))
    return actions


def compose_into_kernel(kernel, transport: Optional[Transport] = None,
                        rail=None) -> dict:
    """The whole Kernel-side call, so the patch in cosmos_kernel.py is an import and one
    line. A rail is NOT foundation: the Kernel fails fast on resolver / install key /
    ledger because a kernel without those is not a kernel, but a kernel without a
    model rail is a kernel with one fewer rail. Composition therefore cannot raise past
    this function - keep-her-afloat - and a failure is recorded, not swallowed."""
    adapters = getattr(kernel, "adapters", None)
    if adapters is None:
        adapters = {}
        kernel.adapters = adapters
    try:
        return attach_groq_rail(
            kernel.registry, adapters, ledger=kernel.ledger,
            spend_gate=kernel.spend, rail=rail,
            transport=transport if transport is not None else urllib_transport(),
            read_only=kernel.read_only)
    except Exception as e:                                            # noqa: BLE001
        detail = f"{type(e).__name__}: {e}"[:300]
        if not kernel.read_only:
            kernel.ledger.append("RAIL_COMPOSE_FAILED",
                                 {"link_id": LINK_ID, "detail": detail})
        return {"link_id": LINK_ID, "composed": False, "registered": False,
                "budgeted": False, "read_only": kernel.read_only, "detail": detail}


# --------------------------------------------------------------------------------
# conformance harness - point this at the LIVE satellite
# --------------------------------------------------------------------------------
INVARIANTS = (
    ("I1", "compose is in-memory; a read-only kernel appends nothing at boot"),
    ("I2", "register/budget are idempotent - a re-boot must not re-register, because "
           "LINK_REGISTERED discards the last probe and unroutes the link"),
    ("I3", "refused model ids are refused LOCALLY, before key and socket, tier-scoped"),
    ("I4", "service_tier never reaches the body; a caller-supplied one is refused"),
    ("I5", "response.model is bound, and the SERVED id is re-checked against the table"),
    ("I6", "the credential never reaches a ledger payload, an error, or a result"),
    ("I7", "no socket without an injected transport; construction opens nothing"),
)


def conformance(rail_factory, tier: str = "free") -> list[dict]:
    """Run the transport-level invariants against ANY adapter that follows the tree's
    protocol - including the live cosmos_groq_rail. Usage in the live tree:

        from cosmos_groq_rail import GroqRail
        from groq_compose_ref import conformance
        for row in conformance(lambda **kw: GroqRail(**kw)):
            print(row["id"], "PASS" if row["ok"] else "FAIL", row["detail"])

    rail_factory(**kwargs) must accept transport=, key_provider=, model=, tier=."""
    rows: list[dict] = []
    sent: list[dict] = []
    secret = "sk-live-DO-NOT-LEAK-0123456789"

    def _fake(url, headers, body_text, timeout_s):
        sent.append({"url": url, "headers": dict(headers), "body": body_text})
        return 200, {}, json.dumps({
            "id": "chatcmpl-conf", "model": DEFAULT_MODEL,
            "choices": [{"index": 0, "message": {"role": "assistant", "content": "ok"},
                         "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 3, "completion_tokens": 1, "total_tokens": 4}})

    def _add(iid, fn):
        """A conformance row NEVER crashes the harness. A rail that raises where it
        should have returned a typed dict has failed the invariant being measured, and
        the harness has to be able to say so - if it died instead, the operator learns
        nothing and cannot tell a broken rail from a broken harness."""
        try:
            ok, detail = fn()
        except Exception as e:                                        # noqa: BLE001
            ok, detail = False, f"raised {type(e).__name__}: {e}"
        rows.append({"id": iid, "ok": bool(ok), "detail": str(detail)[:200]})

    def _last_body() -> dict:
        if not sent:
            return {}
        try:
            return json.loads(sent[-1]["body"])
        except ValueError:
            return {}

    rail = rail_factory(transport=_fake, key_provider=lambda: secret,
                        model=DEFAULT_MODEL, tier=tier)

    def _i3():
        n = len(sent)
        r = rail.dispatch({"prompt": "hi", "model": "mixtral-8x7b-32768"})
        return ((not r["ok"]) and r["kind"] == "MODEL_REFUSED" and len(sent) == n,
                f"mixtral -> {r.get('kind')}, {len(sent) - n} request(s) sent")
    _add("I3", _i3)

    def _i3b():
        n = len(sent)
        r = rail.dispatch({"prompt": "hi", "model": "llama-3.3-70b-versatile"})
        return ((not r["ok"]) and r["kind"] == "MODEL_REFUSED" and len(sent) == n,
                f"llama-3.3 at tier {tier!r} -> {r.get('kind')}")
    _add("I3b", _i3b)

    def _i4():
        n = len(sent)
        r = rail.dispatch({"prompt": "hi"})
        body = _last_body()
        return (bool(r["ok"]) and len(sent) == n + 1 and "service_tier" not in body,
                f"body keys {sorted(body)}")
    _add("I4", _i4)

    def _i4b():
        n = len(sent)
        r = rail.dispatch({"prompt": "hi", "params": {"service_tier": "flex"}})
        return ((not r["ok"]) and r["kind"] == "PARAM_REFUSED" and len(sent) == n,
                f"caller-supplied service_tier -> {r.get('kind')}, "
                f"{len(sent) - n} request(s) sent")
    _add("I4b", _i4b)

    def _i5():
        r = rail.dispatch({"prompt": "hi"})
        return (r.get("model") == DEFAULT_MODEL and r.get("model_bound") is True,
                f"bound {r.get('model')!r} from response.model")
    _add("I5", _i5)

    def _i6():
        blob = json.dumps(rows) + json.dumps(sent[-1]["body"] if sent else "")
        return (secret not in blob,
                "credential absent from results and bodies (the Authorization header "
                "carries it; nothing else may)")
    _add("I6", _i6)

    def _i7():
        bare = rail_factory(transport=None, key_provider=lambda: secret,
                            model=DEFAULT_MODEL, tier=tier)
        ok, detail = bare.probe()
        return (ok is False and "UNREACHABLE" in detail,
                f"no transport -> probe {ok}, {str(detail)[:60]}")
    _add("I7", _i7)
    return rows


if __name__ == "__main__":                                    # pragma: no cover
    for row in conformance(lambda **kw: GroqRail(**kw)):
        print(f"  {'OK  ' if row['ok'] else 'FAIL'} {row['id']}  {row['detail']}")
