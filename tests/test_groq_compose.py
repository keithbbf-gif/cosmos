#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: the groq-api Kernel compose PROPOSAL (WO 2026-09-04, Lane B / Cursor).

Runs the reference implementation in proposals/groq_compose_ref.py against
  * a FAKE transport - no socket is opened by this suite, ever (WO ask 4: tests stay
    fake-HTTP; the live --gate is already PASS and is not re-run here), and
  * a REAL Kernel booted on a temp root, because the load-bearing claim of this
    proposal is about what the Kernel appends at boot, and that cannot be checked
    against a mock of the Kernel.

It also validates proposals/groq-api-kernel-compose.json the way cosmos_port_plan's
decisions are validated: dispositions checked against cosmos_tools.DISPOSITIONS rather
than a vocabulary invented here, and the accounting COUNTED, not quoted.

Carries a planted failure per cosmos_health: a board that cannot go red is not a board.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parent
sys.path.insert(0, str(_HERE))
sys.path.insert(0, str(_ROOT / "cosmos"))
sys.path.insert(0, str(_ROOT / "proposals"))

from cosmos_kernel import Kernel, install                              # noqa: E402
from cosmos_ledger import Ledger                                       # noqa: E402
from cosmos_registry import Registry                                   # noqa: E402
from cosmos_rails import Dispatcher, RailError                         # noqa: E402
from cosmos_tools import DISPOSITIONS                                  # noqa: E402

import groq_compose_ref as G                                           # noqa: E402

RESULTS: list[tuple[str, bool, str]] = []
SECRET = "gsk_TEST_DO_NOT_LEAK_9f8e7d6c5b4a"


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                             # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


# ---------------------------------------------------------------- fake transport
class FakeGroq:
    """Records every request and answers from a script. The ONLY way this suite can
    reach anything that looks like Groq - proposals/groq_compose_ref.py opens no socket
    of its own, so a test that forgot to inject this would fail UNREACHABLE rather than
    quietly hitting the network."""

    def __init__(self):
        self.sent: list[dict] = []
        self.status = 200
        self.served_model = G.DEFAULT_MODEL
        self.body_override = None

    def __call__(self, url, headers, body_text, timeout_s):
        self.sent.append({"url": url, "headers": dict(headers), "body": body_text})
        if self.body_override is not None:
            return self.status, {}, self.body_override
        if self.status != 200:
            return self.status, {}, json.dumps(
                {"error": {"message": "nope", "type": "invalid_request_error",
                           "code": "model_decommissioned"}})
        return 200, {}, json.dumps({
            "id": "chatcmpl-fake", "object": "chat.completion", "created": 1,
            "model": self.served_model,
            "choices": [{"index": 0, "finish_reason": "stop",
                         "message": {"role": "assistant", "content": "pong"}}],
            "usage": {"prompt_tokens": 7, "completion_tokens": 2, "total_tokens": 9}})

    @property
    def last_body(self) -> dict:
        return json.loads(self.sent[-1]["body"]) if self.sent else {}


def _rail(fake, **kw):
    kw.setdefault("key_provider", lambda: SECRET)
    kw.setdefault("tier", "free")
    return G.GroqRail(transport=fake, **kw)


# ---------------------------------------------------------------- the suite
def main() -> int:                                                     # noqa: C901
    td = Path(tempfile.mkdtemp(prefix="cosmos_groq_"))

    # ============================================================ I3: refusals
    fake = FakeGroq()
    rail = _rail(fake)

    for dead in ("mixtral-8x7b-32768", "llama-3.3-70b-versatile", "llama-3.1-8b-instant",
                 "llama3-70b-8192", "llama-3.2-1b-preview", "llama-3.1-70b-versatile"):
        n = len(fake.sent)
        r = rail.dispatch({"prompt": "hi", "model": dead})
        check(f"REFUSED before the wire: {dead}",
              lambda r=r, n=n: (not r["ok"]) and r["kind"] == "MODEL_REFUSED"
              and len(fake.sent) == n)

    check("a refusal names the shutdown DATE and the replacement, not just 'no'",
          lambda: all(k in rail.dispatch({"prompt": "x", "model": "mixtral-8x7b-32768"})
                      ["detail"] for k in ("2025-03-20", "openai/gpt-oss-120b")))

    check("an UNLISTED llama-3.x id is refused too (a dated table is fail-open; the "
          "family net is not)",
          lambda: rail.dispatch({"prompt": "x", "model": "llama-3.9-imaginary-42b"}
                                )["kind"] == "MODEL_REFUSED")

    check("refusal needs NO credential - it happens before the key is read",
          lambda: G.GroqRail(transport=fake, key_provider=_boom,
                             tier="free").dispatch(
              {"prompt": "x", "model": "mixtral-8x7b-32768"})["kind"] == "MODEL_REFUSED")

    # tier-scoping: the 2026-08-16 notice binds free/developer ONLY
    ent = _rail(fake, tier="enterprise")
    check("TIER-SCOPED: llama-3.3-70b-versatile is refused on free but PERMITTED on an "
          "enterprise committed-spend key (Groq's own carve-out)",
          lambda: ent.dispatch({"prompt": "x", "model": "llama-3.3-70b-versatile"})["ok"])
    check("TIER-SCOPED: mixtral stays refused on EVERY tier (no carve-out exists)",
          lambda: ent.dispatch({"prompt": "x", "model": "mixtral-8x7b-32768"}
                               )["kind"] == "MODEL_REFUSED")
    check("an undeclared tier REFUSES rather than defaulting (a tier is declared, "
          "never inferred from a 4xx)", lambda: _raises_badtier())

    check(f"the default model is the WO's, and it survives its own refusal table: "
          f"{G.DEFAULT_MODEL}",
          lambda: G.check_model(G.DEFAULT_MODEL, "free") == G.DEFAULT_MODEL
          == "openai/gpt-oss-20b")

    # ============================================================ I4: service_tier
    r = rail.dispatch({"prompt": "ping"})
    check("happy path reaches the documented endpoint",
          lambda: r["ok"] and fake.sent[-1]["url"] == G.ENDPOINT
          == "https://api.groq.com/openai/v1/chat/completions")
    check("service_tier is ABSENT from the request body (omission IS on_demand; not "
          "'on_demand', not null)",
          lambda: "service_tier" not in fake.last_body)
    check("no key in the body resembles a tier selector",
          lambda: not [k for k in fake.last_body if "tier" in k.lower()])
    n = len(fake.sent)
    r = rail.dispatch({"prompt": "x", "params": {"service_tier": "flex"}})
    check("a caller-supplied service_tier=flex is REFUSED, not silently dropped "
          "(dropping it lies about what was sent)",
          lambda: (not r["ok"]) and r["kind"] == "PARAM_REFUSED" and len(fake.sent) == n)
    check("the refusal cites BOTH reasons - paid-tier entitlement AND report-never-retry",
          lambda: "498" in r["detail"] and "report-never-retry" in r["detail"])
    check("a re-spelled Service-Tier is caught by the same guard",
          lambda: rail.dispatch({"prompt": "x", "params": {"Service-Tier": "flex"}}
                                )["kind"] == "PARAM_REFUSED")
    check("an unlisted body parameter is refused (the body is an allow-list)",
          lambda: rail.dispatch({"prompt": "x", "params": {"reasoning_effort": "high"}}
                                )["kind"] == "PARAM_REFUSED")
    check("a listed body parameter passes through",
          lambda: rail.dispatch({"prompt": "x", "params": {"temperature": 0.1}})["ok"]
          and fake.last_body["temperature"] == 0.1)

    # ============================================================ I5: bind response.model
    fake.served_model = G.DEFAULT_MODEL
    r = rail.dispatch({"prompt": "x"})
    check("response.model is BOUND onto the result",
          lambda: r["model"] == G.DEFAULT_MODEL and r["model_bound"] is True
          and r["model_drift"] is False)
    fake.served_model = "openai/gpt-oss-120b"
    r = rail.dispatch({"prompt": "x", "model": G.DEFAULT_MODEL})
    check("a SERVED model different from the requested one is reported as drift, and "
          "the served id is what gets carried",
          lambda: r["ok"] and r["model"] == "openai/gpt-oss-120b"
          and r["model_requested"] == G.DEFAULT_MODEL and r["model_drift"] is True)
    fake.served_model = "llama-3.3-70b-versatile"
    r = rail.dispatch({"prompt": "x", "model": G.DEFAULT_MODEL})
    check("THE FAIL-OPEN HOLE CLOSES ON THE WAY BACK: a permitted request answered by a "
          "refused model is MODEL_DRIFT, not a clean success",
          lambda: (not r["ok"]) and r["kind"] == "MODEL_DRIFT"
          and r["model"] == "llama-3.3-70b-versatile")
    fake.served_model = G.DEFAULT_MODEL
    fake.body_override = json.dumps({"choices": [{"message": {"content": "hi"}}]})
    r = rail.dispatch({"prompt": "x"})
    check("a 200 that will not name its model is BAD_RESPONSE, never an assumed bind",
          lambda: (not r["ok"]) and r["kind"] == "BAD_RESPONSE")
    fake.body_override = None

    # ============================================================ typed HTTP failures
    for status, kind in ((401, "AUTH_REQUIRED"), (429, "RATE_LIMITED"),
                         (498, "CAPACITY_EXCEEDED"), (503, "UNREACHABLE")):
        fake.status = status
        r = rail.dispatch({"prompt": "x"})
        check(f"HTTP {status} -> {kind}", lambda r=r, k=kind: r["kind"] == k)
    fake.status = 498
    check("498 says out loud that it is the flex failure mode",
          lambda: "flex" in rail.dispatch({"prompt": "x"})["detail"])
    fake.status = 401
    check("401 maps to AUTH_REQUIRED, which is one of the three kinds "
          "cosmos_rails.Dispatcher treats as an EXPLICIT AUDITED FALLBACK",
          lambda: rail.dispatch({"prompt": "x"})["kind"]
          in ("UNREACHABLE", "SESSION_EXPIRED", "AUTH_REQUIRED"))
    fake.status = 200

    # ============================================================ I6: the credential
    fake_leak = FakeGroq()
    fake_leak.status = 400
    fake_leak.body_override = json.dumps(
        {"error": {"message": f"bad request from Bearer {SECRET}"}})
    leaky = _rail(fake_leak)
    r = leaky.dispatch({"prompt": "x"})
    check("a response body that echoes the key is REDACTED before it can be carried "
          "(the ledger is append-only: a secret written once is written forever, and "
          "redacting it afterwards breaks the chain)",
          lambda: SECRET not in json.dumps(r) and "***REDACTED***" in r["detail"])
    check("the key travels in the Authorization header and nowhere else",
          lambda: SECRET in fake.sent[-1]["headers"]["Authorization"]
          and SECRET not in fake.sent[-1]["body"])

    # ============================================================ I7: no accidental socket
    check("construction opens nothing: a rail built with no transport still constructs",
          lambda: G.GroqRail(key_provider=lambda: SECRET).kind == "API")
    ok, detail = G.GroqRail(key_provider=lambda: SECRET).probe()
    check("...and then probes RED, rather than pretending", lambda: not ok)
    ok, detail = _rail(fake, model="mixtral-8x7b-32768").probe()
    check("the probe can go RED for a refused default model (a health row that cannot "
          "go red is the scar cosmos_health closes)",
          lambda: not ok and "MODEL_REFUSED" in detail)
    ok, detail = G.GroqRail(transport=fake, key_provider=_boom).probe()
    check("the probe can go RED for a missing credential", lambda: not ok
          and "NO_KEY" in detail)
    ok, detail = _rail(fake).probe()
    check("a healthy probe says LIVENESS IS PER-CALL rather than claiming the API is up",
          lambda: ok and "per-call" in detail)
    n = len(fake.sent)
    _rail(fake).probe()
    check("the registry-attached probe costs ZERO requests (probe_all() is on status "
          "paths; a network fan-out there turns `cosmos status` into egress)",
          lambda: len(fake.sent) == n)

    cat = FakeGroq()
    cat.body_override = json.dumps({"data": [{"id": "openai/gpt-oss-120b"}]})
    ok, detail = _rail(cat).probe_deep()
    check("the DEEP probe catches the dated refusal table going stale against the live "
          "catalog - the only free check that closes fail-open",
          lambda: not ok and "CATALOG_DRIFT" in detail)
    cat.body_override = json.dumps({"data": [{"id": G.DEFAULT_MODEL}]})
    check("...and passes when the model is still listed",
          lambda: _rail(cat).probe_deep()[0])

    # ================================================ MEASURED: re-register amnesia
    led0 = Ledger(td / "amnesia.jsonl", b"k", "core")
    reg0 = Registry(led0)
    reg0.register(G.LINK_ID, "API", "core", "models", policy_rank=0)
    reg0.attach_probe(G.LINK_ID, lambda: (True, "live"))
    reg0.probe(G.LINK_ID)
    routed_before = [c["link_id"] for c in reg0.route("core", "models")]
    reg0.register(G.LINK_ID, "API", "core", "models", policy_rank=0)     # a second boot
    routed_after = [c["link_id"] for c in reg0.route("core", "models")]
    check("MEASURED, and the reason the compose must guard: a second LINK_REGISTERED "
          "DISCARDS the last probe and drops the link out of route() - an unguarded "
          "boot-time register makes every rail permanently unroutable",
          lambda: routed_before == [G.LINK_ID] and routed_after == []
          and reg0.matrix()[0]["verified"] is None)

    # ================================================ I1/I2 against a REAL Kernel
    root_ro = td / "RootRO"
    install(root_ro, tree_id="groq-compose-ro")
    kro = Kernel(root_ro, worker="status", read_only=True)
    before = len(list(kro.ledger.verify()))
    act = G.compose_into_kernel(kro, rail=_rail(FakeGroq()))
    after = len(list(kro.ledger.verify()))
    check("I1 THE HEADLINE: composing on a READ-ONLY kernel appends NOTHING - the "
          "adapter is built in memory and the two ledger writes are skipped, so "
          "boot_compose does not put the B1 'a read is a write' scar back",
          lambda: before == after and act["composed"] and not act["registered"]
          and not act["budgeted"])
    check("...and the read-only kernel still HAS the adapter and the probe (composed "
          "means usable, not merely intended)",
          lambda: kro.adapters[G.LINK_ID].kind == "API"
          and G.LINK_ID in kro.registry._probes)
    check("...and the link is NOT claimed as registered, because nothing was written",
          lambda: G.LINK_ID not in kro.registry.state())

    root = td / "Root"
    install(root, tree_id="groq-compose-rw")
    k = Kernel(root, worker="core", clock=_tick())
    n0 = len(list(k.ledger.verify()))
    a1 = G.compose_into_kernel(k, rail=_rail(FakeGroq()))
    n1 = len(list(k.ledger.verify()))
    check("a WRITING kernel registers the link and sets the budget - exactly two "
          "appends, once", lambda: a1["registered"] and a1["budgeted"] and n1 - n0 == 2)
    check("the link lands on the SAME route as the other model rails (core->models), "
          "or it can never be a fallback for them",
          lambda: k.registry.state()[G.LINK_ID]["claim"]["src"] == "core"
          and k.registry.state()[G.LINK_ID]["claim"]["dst"] == "models")
    check("policy_rank 0 keeps DOM ahead of it - an API rail must not outrank the DOM "
          "lane", lambda: k.registry.state()[G.LINK_ID]["claim"]["policy_rank"] == 0)

    k.registry.probe(G.LINK_ID)
    n2 = len(list(k.ledger.verify()))
    a2 = G.compose_into_kernel(k, rail=_rail(FakeGroq()))
    n3 = len(list(k.ledger.verify()))
    check("I2 THE OTHER HALF: a SECOND boot appends nothing at all - not a duplicate "
          "registration, not a duplicate budget",
          lambda: n3 == n2 and not a2["registered"] and not a2["budgeted"]
          and a2["already_registered"])
    check("...so the probe measurement SURVIVES the re-boot and the link stays routable",
          lambda: k.registry.state()[G.LINK_ID]["ok"] is True
          and G.LINK_ID in [c["link_id"] for c in k.registry.route("core", "models")])
    check("boot compose does not PROBE (a probe is a ledger write, and registration is "
          "not capability - the rail is known, not yet verified)",
          lambda: not [r for r in Kernel(root, worker="core2").ledger.verify()
                       if r["event"] == "PROBE_RESULT"
                       and r["payload"]["link_id"] == G.LINK_ID][1:])

    check("the shim's LINK_REGISTERED payload is byte-identical to what "
          "Registry.register() writes - the guarded append restates a contract, so the "
          "restatement is checked rather than trusted", _payload_parity)
    check("idempotence has TWO independent layers and each holds ALONE: with the "
          "state() pre-check blinded, the guarded append still refuses the second "
          "registration, so two kernels booting at once cannot both write",
          _guarded_layer_alone)

    # ================================================ keep-her-afloat
    root2 = td / "RootAfloat"
    install(root2, tree_id="groq-compose-afloat")
    k2 = Kernel(root2, worker="core")
    afloat: dict = {}
    check("KEEP-HER-AFLOAT: a rail that blows up during composition does NOT take the "
          "kernel down - a rail is not foundation",
          lambda: _afloat_writing(k2, afloat))
    check("...and the failure is RECORDED, not swallowed (RAIL_COMPOSE_FAILED)",
          lambda: afloat.get("recorded"))
    check("...and the broken rail is NOT left in the adapter map - a half-composed rail "
          "is worse than an absent one, because the Dispatcher would drive it",
          lambda: afloat.get("map_clean"))
    check("a read-only kernel whose compose fails records nothing and still boots",
          _afloat_readonly)

    # ================================================ spend accounting
    fake2 = FakeGroq()
    k3root = td / "RootSpend"
    install(k3root, tree_id="groq-compose-spend")
    k3 = Kernel(k3root, worker="core")
    G.compose_into_kernel(k3, rail=_rail(fake2))
    k3.registry.probe(G.LINK_ID)
    disp = Dispatcher(k3.registry, k3.adapters, k3.ledger, spend=k3.spend)
    check("end to end through the real Dispatcher, spend-gated",
          lambda: _e2e(disp, k3))
    check("a real call settles UNPRICED, never $0 - Groq bills tokens, not dollars",
          lambda: _audit(k3)["unpriced_calls"] == 1 and _audit(k3)["settled_usd"] == 0.0)
    try:
        disp.dispatch("core", "models",
                      {"prompt": "x", "model": "mixtral-8x7b-32768"})
        refused_typed = False
    except RailError as e:
        refused_typed = e.kind == "RAIL_FAILED"
    check("a model refusal surfaces as RAIL_FAILED, NOT as NOT_PERMITTED - a refusal "
          "reported as a budget denial sends you to the wrong ledger",
          lambda: refused_typed)
    check("a LOCAL refusal settles at a MEASURED $0.00 and does not inflate "
          "unpriced_calls - 'unpriced != zero' is about calls that HAPPENED; a call "
          "that never left the process cost exactly zero",
          lambda: _audit(k3)["unpriced_calls"] == 1 and _audit(k3)["settled_usd"] == 0.0)
    check("metered_usd is NONZERO, or cosmos_rails skips the breaker entirely and the "
          "rail vanishes from spend.audit()",
          lambda: G.METERED_USD > 0 and G.LINK_ID in k3.spend.audit()["rails"])
    check("no credential reached the authority ledger, on any path",
          lambda: SECRET not in "".join(json.dumps(r) for r in k3.ledger.verify()))

    # ================================================ P10 / scope
    kernel_src = (_ROOT / "cosmos" / "cosmos_kernel.py").read_text(encoding="utf-8")
    check("P10: this PR does NOT wire the Kernel - cosmos/cosmos_kernel.py is untouched "
          "and mentions no rail compose", lambda: "groq" not in kernel_src.lower()
          and "boot_compose" not in kernel_src)
    check("P10: nothing under cosmos/ imports the reference module",
          lambda: not [p for p in (_ROOT / "cosmos").glob("*.py")
                       if "groq_compose_ref" in p.read_text(encoding="utf-8")])
    md = (_ROOT / "proposals" / "groq-api-kernel-compose.md").read_text(encoding="utf-8")
    check("the proposed Kernel patch declares NO Groq fact of its own - no endpoint, no "
          "model id - so there is no second declaration to drift from the satellite",
          lambda: _patch_is_clean(md))
    check("the proposal states the P10 boundary and the do-not-merge instruction",
          lambda: "PROPOSE only" in md and "Do not merge" in md
          and "V:\\Ai" in md)

    # ================================================ the JSON decision record
    spec = json.loads((_ROOT / "proposals" / "groq-api-kernel-compose.json")
                      .read_text(encoding="utf-8"))
    check("every disposition in the record is one of the tree's own four "
          "(cosmos_tools.DISPOSITIONS), not a vocabulary invented here",
          lambda: all(d["disposition"] in DISPOSITIONS
                      for d in spec["dispositions"].values()))
    check("every REPLACED/ADAPTED entry names a successor that EXISTS - 'a successor "
          "that does not exist is a claim, not a port'",
          lambda: all((_ROOT / "cosmos" / f"{s}.py").exists()
                      for d in spec["dispositions"].values()
                      for s in _cosmos_tokens(d.get("successor"))))
    check("the record's invariant ids match the code's INVARIANTS exactly - the doc "
          "cannot drift from the harness",
          lambda: [i["id"] for i in spec["invariants"]] == [i for i, _ in G.INVARIANTS])
    check("every invariant names the check that proves it, and that check ran here",
          lambda: all(i["proved_by"] == "tests/test_groq_compose.py"
                      for i in spec["invariants"]))
    check("every refusal row carries a shutdown DATE, a replacement and its tiers - a "
          "refusal without a date is folklore",
          lambda: all(r.get("shutdown") and r.get("replacement")
                      and set(r["tiers"]) <= set(G.TIERS)
                      for r in spec["refusals"].values()))
    check("the record's refusal table is COUNTED against the code's, not quoted",
          lambda: spec["refusals"] == {k: {"shutdown": v["shutdown"],
                                           "replacement": v["replacement"],
                                           "tiers": list(v["tiers"])}
                                       for k, v in G.REFUSED_MODELS.items()})
    check("the record's link facts equal the code's (endpoint, default model, route, "
          "link_id) - one declaration, checked",
          lambda: spec["link"] == {"link_id": G.LINK_ID, "endpoint": G.ENDPOINT,
                                   "default_model": G.DEFAULT_MODEL,
                                   "rail_type": "API", "src": G.ROUTE_SRC,
                                   "dst": G.ROUTE_DST, "policy_rank": G.POLICY_RANK,
                                   "metered_usd": G.METERED_USD,
                                   "budget_usd": G.BUDGET_USD})
    check("the record refuses service_tier in every spelling the code refuses",
          lambda: spec["never_sent"] == list(G.FORBIDDEN_PARAMS))

    # ================================================ conformance harness
    rows = G.conformance(lambda **kw: G.GroqRail(**kw))
    check("the conformance harness CCr points at the live satellite passes against the "
          f"reference ({len(rows)} rows)", lambda: all(r["ok"] for r in rows))
    check("...and the harness can FAIL - a rail that forgets the model refusal is "
          "caught by it", lambda: not all(r["ok"] for r in
                                          G.conformance(_Permissive)))

    # ================================================ negative control
    check("negative control (must be RED): the planted failure", lambda: False)

    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    planted = [l for l, ok, _ in RESULTS if l.startswith("negative control")]
    for label, ok, err in RESULTS:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    if len(bad) == 1 and bad[0][0].startswith("negative control"):
        print("SELFTEST PASS - %d checks, 1 planted failure RED as required "
              "(groq-api compose proposal: read-safe, idempotent, refusals typed, "
              "fake-HTTP throughout)" % len(RESULTS))
        return 0
    if not planted:
        print("SELFTEST BOARD-BROKEN - the planted failure is missing")
        return 2
    if not bad:
        print("SELFTEST BOARD-BROKEN - the planted failure showed GREEN, so this board "
              "cannot go red and proves nothing")
        return 2
    print("SELFTEST FAIL - %d real failure(s) of %d checks"
          % (len(bad) - 1, len(RESULTS)))
    return 1


# ---------------------------------------------------------------- helpers
def _boom():
    raise G.GroqError("NO_KEY", "no credential in this test")


def _tick():
    box = {"t": 1_760_000_000.0}

    def _clock():
        box["t"] += 1.0
        return box["t"]
    return _clock


def _raises_badtier() -> bool:
    try:
        G.check_model(G.DEFAULT_MODEL, "hobbyist")
    except G.GroqError as e:
        return e.kind == "BAD_TIER"
    return False


class _Exploding:
    """A rail whose every attribute blows up - the satellite half-installed, renamed, or
    mid-edit. Composition has to survive it."""

    kind = "API"
    metered_usd = G.METERED_USD

    def __getattr__(self, name):
        raise RuntimeError(f"this rail is broken at compose time (asked for {name!r})")


class _Permissive:
    """A rail that sends whatever it is asked to. The harness must catch it."""
    kind = "API"
    metered_usd = G.METERED_USD

    def __init__(self, transport=None, key_provider=None, model=G.DEFAULT_MODEL,
                 tier="free"):
        self.transport, self.key_provider = transport, key_provider
        self.model, self.tier = model, tier

    def probe(self):
        return True, "always green, which is the defect"

    def dispatch(self, payload):
        model = payload.get("model") or self.model
        body = {"model": model, "messages": [{"role": "user",
                                              "content": payload.get("prompt", "")}]}
        body.update(payload.get("params") or {})
        status, _h, text = self.transport(G.ENDPOINT, {}, json.dumps(body), 30)
        data = json.loads(text)
        return {"ok": True, "kind": "API", "text": "x", "model": data.get("model"),
                "model_bound": True, "model_requested": model, "usd": None}


def _afloat_writing(kernel, out: dict) -> bool:
    """compose_into_kernel() must absorb a broken rail. If it raises instead, this
    helper raises with it and check() records the failure - which is the point: the
    keep-her-afloat promise is a code path, not an intention."""
    act = G.compose_into_kernel(kernel, rail=_Exploding())
    out["recorded"] = any(r["event"] == "RAIL_COMPOSE_FAILED"
                          for r in kernel.ledger.verify())
    out["map_clean"] = G.LINK_ID not in kernel.adapters
    return bool(kernel.ready) and not act["composed"]


def _afloat_readonly() -> bool:
    td = Path(tempfile.mkdtemp(prefix="cosmos_groq_ro2_"))
    root = td / "R"
    install(root, tree_id="groq-afloat-ro")
    k = Kernel(root, worker="status", read_only=True)
    before = len(list(k.ledger.verify()))
    act = G.compose_into_kernel(k, rail=_Exploding())
    return (k.ready and not act["composed"]
            and len(list(k.ledger.verify())) == before)


def _e2e(disp, kernel) -> bool:
    out = disp.dispatch("core", "models", {"prompt": "through the dispatcher"})
    return (out["ok"] and out["text"] == "pong"
            and any(e["event"] == "SPEND_SETTLED" for e in kernel.ledger.verify()))


def _audit(kernel) -> dict:
    return kernel.spend.audit()["rails"][G.LINK_ID]


class _BlindRegistry(Registry):
    """A Registry whose projection always reports 'nothing registered'. It stands in for
    the window between two concurrently booting kernels, where both see absent. The
    attach's outer pre-check is useless here on purpose - what is left is the guarded
    append, and it has to hold on its own."""

    def state(self) -> dict:
        return {}


def _guarded_layer_alone() -> bool:
    td = Path(tempfile.mkdtemp(prefix="cosmos_groq_race_"))
    led = Ledger(td / "r.jsonl", b"k", "core")
    reg = _BlindRegistry(led)
    for _ in range(3):
        G.attach_groq_rail(reg, {}, ledger=led, rail=_rail(FakeGroq()))
    return len([r for r in led.verify() if r["event"] == "LINK_REGISTERED"]) == 1


def _payload_parity() -> bool:
    """Registry.register() has no guarded variant, so attach_groq_rail restates the
    LINK_REGISTERED payload. Restating a contract is drift waiting to happen, so the
    restatement is compared against what the Registry really writes."""
    td = Path(tempfile.mkdtemp(prefix="cosmos_groq_par_"))
    led = Ledger(td / "p.jsonl", b"k", "core")
    Registry(led).register(G.LINK_ID, "API", G.ROUTE_SRC, G.ROUTE_DST,
                           policy_rank=G.POLICY_RANK)
    real = [r for r in led.verify() if r["event"] == "LINK_REGISTERED"][0]["payload"]
    mine = G._link_registered_payload(G.LINK_ID, "API", G.ROUTE_SRC, G.ROUTE_DST,
                                      G.POLICY_RANK)
    return real == mine


def _patch_is_clean(md: str) -> bool:
    """The Kernel patch quoted in the proposal must carry no Groq fact of its own: no
    endpoint, no model id, no refusal list. Two declarations of one fact is the drift
    this tree keeps closing ('a second declaration of the same id is a drift')."""
    start = md.find("<!-- KERNEL-PATCH-BEGIN -->")
    end = md.find("<!-- KERNEL-PATCH-END -->")
    if start < 0 or end < 0:
        return False
    patch = md[start:end]
    forbidden = ("api.groq.com", "gpt-oss", "mixtral", "llama-3", "service_tier",
                 "GROQ_API_KEY")
    return not [f for f in forbidden if f in patch]


def _cosmos_tokens(successor):
    if not successor:
        return []
    return [t for t in successor.replace("+", " ").split() if t.startswith("cosmos_")]


def test_groq_compose():
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())
