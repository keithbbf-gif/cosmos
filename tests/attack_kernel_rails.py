#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Adversarial probes against the kernel-rails cluster.

Cluster: cosmos_kernel, cosmos_registry, cosmos_rails, cosmos_node_rails,
         cosmos_dom, cosmos_ingress (composition + dispatch).

Does NOT modify cosmos/ or existing tests/. Each probe tries to break a
ratified contract (docs/FINAL_ARCHITECTURE.md) or a harvest gap from the
Grok critic review (B1-B7 / M1-M10).

A probe LANDS when the hole is confirmed at runtime.
A probe HOLDS when the contract held under attack.

Run:
  PYTHONPATH=cosmos python3 tests/attack_kernel_rails.py
"""
from __future__ import annotations

import inspect
import json
import os
import sys
import tempfile
import threading
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "cosmos"))

from cosmos_kernel import Kernel, install
from cosmos_ledger import Ledger
from cosmos_registry import Registry, RegError
from cosmos_rails import Dispatcher, ApiRail, DomRail, CliRail, RailError
from cosmos_node_rails import NodeRail, register_node_rails
from cosmos_dom import DomWorker
from cosmos_ingress import IngressGate, write_envelope, IngressError
from cosmos_spend import SpendGate, SpendError
from cosmos_lock import LockError


RESULTS = []  # (name, landed, severity, detail)


def record(name, landed, severity, detail):
    RESULTS.append((name, bool(landed), severity, str(detail)))
    tag = "LANDS" if landed else "HOLDS"
    print("  [%s] %-7s %s — %s" % (tag, severity, name, detail))


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _root(prefix="atk_"):
    td = Path(tempfile.mkdtemp(prefix=prefix))
    root = td / "Cosmos"
    install(root, tree_id=prefix.rstrip("_"))
    return td, root


class _FakeDriver:
    def __init__(self, text="PAGE", mode="ok"):
        self.text = text
        self.mode = mode
        self.started = []
        self.stopped = 0

    def start(self, profile_dir):
        self.started.append(profile_dir)
        if self.mode == "no_start":
            raise ConnectionError("no browser")

    def navigate(self, url):
        if self.mode == "auth":
            raise PermissionError("login wall")
        if self.mode == "broke":
            raise RuntimeError("mid-action")
        return self.text

    def session_ok(self):
        return self.mode != "expired"

    def stop(self):
        self.stopped += 1


# ===========================================================================
# KERNEL COMPOSITION
# ===========================================================================

def p_b6_kernel_arbiter_unsigned():
    """Harvest B6: Kernel composes Arbiter WITHOUT the install key.
    A well-formed unsigned GRANT must not become a live lease."""
    td, root = _root("b6_")
    k = Kernel(root, worker="core")
    lease_path = k.paths.ledger("leases.jsonl")
    # Plant a well-formed unsigned GRANT (the measured B6 attack).
    forged = {"t": 1, "event": "GRANT", "resource": "crown",
              "holder": "ATTACKER", "token": 99, "expires_at": 1e18}
    with open(lease_path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(forged) + "\n")
    k2 = Kernel(root, worker="core-b")
    live = k2.arbiter.status("crown")
    landed = live is not None and live.holder == "ATTACKER" and live.token == 99
    record("B6 unsigned Kernel arbiter loads forged GRANT",
           landed, "BLOCKER",
           "forged lease=%r (Kernel.__init__ passes no key to Arbiter)" % (live,))


def p_m4_protected_write_omits_hashes():
    """Harvest M4 / Decision 2: fenced commit must present expected input hashes.
    Kernel.protected_write must pass them through."""
    td, root = _root("m4_")
    k = Kernel(root, worker="core")
    seen = []
    orig = k.arbiter.fenced_commit

    def spy(lease, commit, expected_inputs=None):
        seen.append(expected_inputs)
        return orig(lease, commit, expected_inputs)

    k.arbiter.fenced_commit = spy
    k.protected_write("tree", "notes/a.txt", "hello")
    omitted = seen == [None] or (seen and seen[0] in (None, {}))
    record("M4 Kernel.protected_write omits expected_inputs",
           omitted, "BLOCKER",
           "fenced_commit expected_inputs captured=%r" % (seen,))


def p_decision5_ready_without_install_record():
    """Decision 5: service cannot go READY without sentinel-verified root
    AND installation record. Kernel only checks install_key.bin."""
    td, root = _root("d5_")
    rec = root / "config" / "install_record.json"
    rec.unlink()
    k = Kernel(root, worker="core")
    record("Decision 5 Kernel READY with install_record deleted",
           k.ready is True, "MAJOR",
           "ready=%s after unlink of %s" % (k.ready, rec))


def p_m10_audit_hardcodes_tree():
    """Harvest M10: audit.leases_live only inspects resource 'tree'."""
    td, root = _root("m10_")
    k = Kernel(root, worker="core")
    k.arbiter.acquire("crown", "core")
    a = k.audit()
    landed = a["leases_live"] == 0
    record("M10 audit.leases_live ignores non-'tree' leases",
           landed, "MAJOR",
           "live crown lease present, audit.leases_live=%s" % a["leases_live"])


def p_b1_readonly_still_writes_mail():
    """Harvest B1 leftover: read_only Kernel must append NOTHING and write
    no mailbox state. mail.register() mkdirs on construct."""
    td, root = _root("b1ro_")
    kw = Kernel(root, worker="writer")
    inbox = kw.paths.role("state", "mail") / "reader" / "inbox"
    if inbox.exists():
        # fresh reader should not exist yet
        pass
    kr = Kernel(root, worker="reader", read_only=True)
    created = (kr.paths.role("state", "mail") / "reader" / "inbox").is_dir()
    record("B1 read_only Kernel still mail.register() writes",
           created, "MAJOR",
           "read_only=True created inbox at %s" % (kr.paths.role("state", "mail") / "reader" / "inbox"))


def p_b4_import_around_kernel():
    """Harvest B4 / Decision 11: workers cannot import around kernel
    primitives. Any holder of the install key file writes the authority ledger."""
    td, root = _root("b4_")
    k = Kernel(root, worker="core")
    key = (root / "config" / "install_key.bin").read_bytes()
    led = Ledger(k.paths.ledger("authority.jsonl"), key, "ATTACKER")
    led.append("I_AM_THE_KERNEL", {"lie": True})
    evs = [r["event"] for r in k.ledger.verify()]
    record("B4 worker imports Ledger and forges authority events",
           "I_AM_THE_KERNEL" in evs, "BLOCKER",
           "authority events after import-around: %s" % evs[-3:])


def p_kernel_does_not_compose_rails_ingress_dom():
    """Critic: composition in a test is not composition in Core.
    Dispatcher / IngressGate / DomWorker must be kernel verbs."""
    td, root = _root("comp_")
    k = Kernel(root, worker="core")
    missing = [n for n in ("dispatcher", "ingress", "dom", "rails")
               if getattr(k, n, None) is None]
    record("Kernel does not compose dispatcher/ingress/dom",
           len(missing) == 4, "BLOCKER",
           "absent attributes: %s (registry/spend/validator ARE composed)" % missing)


def p_protected_write_escapes_state_role():
    """role('state', relpath) must not walk out of the state tree.
    A mount-shaped relpath is a two-universes attack."""
    td, root = _root("esc_")
    k = Kernel(root, worker="core")
    out = k.protected_write("tree", "../escaped.txt", "PWN")
    escaped = out.resolve() == (root / "escaped.txt").resolve() and out.is_file()
    record("protected_write relpath escapes state role",
           escaped, "BLOCKER",
           "wrote %s (state dir is %s)" % (out, k.paths.role("state")))


def p_b1_overlapping_kernel_writes():
    """Harvest B1 at composition: two writing Kernels overlapping
    protected_write on one root. Chain must verify; exactly-once of content
    is a bonus. A torn chain LANDS the original B1."""
    td, root = _root("b1ov_")
    k1 = Kernel(root, worker="W1")
    k2 = Kernel(root, worker="W2")
    errors = []

    def hammer(k, n):
        for i in range(20):
            try:
                k.protected_write("res-%s-%d" % (k.worker, i),
                                  "notes/%s-%d.txt" % (k.worker, i),
                                  "body-%d" % i)
            except Exception as e:                                    # noqa: BLE001
                errors.append(repr(e))

    t1 = threading.Thread(target=hammer, args=(k1, 20))
    t2 = threading.Thread(target=hammer, args=(k2, 20))
    t1.start(); t2.start(); t1.join(); t2.join()
    try:
        recs = list(Kernel(root, worker="R", read_only=True).ledger.verify())
        chain_ok = True
        n = len(recs)
    except Exception as e:                                            # noqa: BLE001
        chain_ok = False
        n = str(e)
    # B1-closed means chain verifies and no exception leak.
    landed = (not chain_ok) or bool(errors)
    record("B1 overlapping Kernel.protected_write tears or errors",
           landed, "BLOCKER",
           "errors=%d chain_ok=%s recs=%s" % (len(errors), chain_ok, n))


# ===========================================================================
# REGISTRY
# ===========================================================================

def p_registry_stale_probe_never_expires():
    """H6 / dated probes: a year-old ok=True measurement must not remain
    a routing candidate. Age is reported; routing ignores it."""
    td = Path(tempfile.mkdtemp(prefix="reg_stale_"))
    fake = [1_000.0]
    led = Ledger(td / "a.jsonl", b"k", "core", clock=lambda: fake[0])
    reg = Registry(led, clock=lambda: fake[0])
    reg.register("dom1", "DOM", "core", "web", policy_rank=1)
    reg.attach_probe("dom1", lambda: (True, "once"))
    reg.probe("dom1")
    fake[0] = 1_000.0 + 365 * 86400
    live = reg.route("core", "web")
    rows = reg.matrix()
    landed = bool(live) and rows[0]["age_s"] > 30 * 86400
    record("Registry route uses year-old probe as live",
           landed, "MAJOR",
           "route=%s age_s=%s verified=%s" % (
               [c["link_id"] for c in live],
               rows[0]["age_s"] if rows else None,
               rows[0]["verified"] if rows else None))


def p_registry_reregister_wipes_measurement():
    """Re-register of the same link_id is silent and resets ok to None —
    a measurement disappears because a claim was restated."""
    td = Path(tempfile.mkdtemp(prefix="reg_re_"))
    led = Ledger(td / "a.jsonl", b"k", "core")
    reg = Registry(led)
    reg.register("x", "API", "a", "b")
    reg.attach_probe("x", lambda: (True, "live"))
    reg.probe("x")
    before = reg.state()["x"]["ok"]
    reg.register("x", "CLI", "a", "b")  # different type, same id
    after = reg.state()["x"]
    landed = before is True and after["ok"] is None and after["claim"]["rail_type"] == "CLI"
    record("Registry re-register silently restamps and wipes probe",
           landed, "MAJOR",
           "ok before=%s after=%s type=%s" % (before, after["ok"], after["claim"]["rail_type"]))


def p_registry_empty_vs_missing_route():
    """missing-vs-empty: route with no links returns [] (empty), same as
    registered-but-never-probed. The kinds collapse."""
    td = Path(tempfile.mkdtemp(prefix="reg_mv_"))
    led = Ledger(td / "a.jsonl", b"k", "core")
    reg = Registry(led)
    empty_unknown = reg.route("no", "such")
    reg.register("ghost", "API", "core", "web")
    empty_unprobed = reg.route("core", "web")
    # Both are [] — caller cannot tell MISSING route from EMPTY-unprobed.
    landed = empty_unknown == [] and empty_unprobed == []
    record("Registry route collapses missing vs unprobed-empty",
           landed, "MINOR",
           "unknown=%r unprobed=%r (same [])" % (empty_unknown, empty_unprobed))


# ===========================================================================
# RAILS / DISPATCHER
# ===========================================================================

def p_apirail_probe_is_always_live():
    """Registration is not capability. ApiRail.probe() always returns True
    without calling anything. A registered API link becomes route-live after
    probe_all even when the function would raise."""
    td = Path(tempfile.mkdtemp(prefix="api_lie_"))
    led = Ledger(td / "a.jsonl", b"k", "core")
    reg = Registry(led)

    def boom(_):
        raise RuntimeError("endpoint dead")

    rail = ApiRail(boom)
    ok, detail = rail.probe()
    reg.register("dead-api", "API", "core", "web")
    reg.attach_probe("dead-api", rail.probe)
    reg.probe_all()
    live = reg.route("core", "web")
    landed = ok is True and bool(live)
    record("ApiRail.probe always True (registration is capability)",
           landed, "MAJOR",
           "probe=%s %r route=%s" % (ok, detail, [c["link_id"] for c in live]))


def p_missing_adapter_silent_skip():
    """A measured-live link with no adapter is skipped with no ledger event —
    silent fallback, H2 banned."""
    td = Path(tempfile.mkdtemp(prefix="noad_"))
    led = Ledger(td / "a.jsonl", b"k", "core")
    reg = Registry(led)
    reg.register("ghost", "DOM", "core", "web", policy_rank=9)
    reg.register("api", "API", "core", "web")
    api = ApiRail(lambda p: {"ok": True, "kind": "API", "via": "api"})
    reg.attach_probe("ghost", lambda: (True, "claims live"))
    reg.attach_probe("api", api.probe)
    reg.probe_all()
    disp = Dispatcher(reg, {"api": api}, led)  # ghost has NO adapter
    r = disp.dispatch("core", "web", {})
    evs = [e["event"] for e in led.verify()]
    # LANDS if we reached API without RAIL_FALLBACK / any ghost dispatch record
    ghost_mentioned = any(
        e["event"] in ("RAIL_DISPATCH", "RAIL_FALLBACK")
        and e["payload"].get("link_id") == "ghost" or e["payload"].get("from") == "ghost"
        for e in led.verify())
    landed = r.get("via") == "api" and not ghost_mentioned
    record("Dispatcher silently skips missing adapter (no RAIL_FALLBACK)",
           landed, "MAJOR",
           "result=%s ghost_mentioned=%s events=%s" % (r, ghost_mentioned, evs))


def p_dispatch_raise_mislabeled_not_permitted():
    """A raising adapter inside a metered guarded_call is remapped to
    NOT_PERMITTED even though the call RAN. SpendError vs dispatch BROKE
    collapse."""
    td = Path(tempfile.mkdtemp(prefix="np_"))
    led = Ledger(td / "a.jsonl", b"k", "core")
    reg = Registry(led)
    ran = []

    def boom(_):
        ran.append(1)
        raise RuntimeError("model 500")

    rail = ApiRail(boom, metered_usd=0.02)
    spend = SpendGate(led)
    spend.set_budget("m", 10.0)
    reg.register("m", "API", "core", "models")
    reg.attach_probe("m", rail.probe)
    reg.probe_all()
    disp = Dispatcher(reg, {"m": rail}, led, spend=spend)
    kind = None
    try:
        disp.dispatch("core", "models", {})
    except RailError as e:
        kind = e.kind
    landed = kind == "NOT_PERMITTED" and ran == [1]
    record("Dispatcher maps dispatch exception to NOT_PERMITTED (call RAN)",
           landed, "MAJOR",
           "kind=%s ran=%s (spend-gated path remaps any Exception)" % (kind, ran))


def p_spend_rid_collision_under_overlap():
    """Harvest m2 + exactly-once: rid = r%%d %% int(clock*1000).
    Two overlapping guarded_calls at the same clock share a reservation
    slot; cap of 0.03 should admit only one 0.02 call."""
    td = Path(tempfile.mkdtemp(prefix="rid_"))
    fake = [1_000.500]  # frozen clock -> same millisecond
    led = Ledger(td / "a.jsonl", b"k", "core", clock=lambda: fake[0])
    spend = SpendGate(led, clock=lambda: fake[0])
    spend.set_budget("rail", 0.03)
    barrier = threading.Barrier(2)
    outcomes = []

    def race():
        try:
            barrier.wait(timeout=5)
            spend.guarded_call("rail", 0.02, lambda: {"ok": True, "usd": 0.02})
            outcomes.append("ran")
        except SpendError as e:
            outcomes.append("denied:" + e.kind)
        except Exception as e:                                        # noqa: BLE001
            outcomes.append("err:" + type(e).__name__)

    t1 = threading.Thread(target=race)
    t2 = threading.Thread(target=race)
    t1.start(); t2.start(); t1.join(); t2.join()
    ran = outcomes.count("ran")
    landed = ran == 2
    record("Spend rid collision: two overlapping 0.02 on 0.03 cap both RAN",
           landed, "BLOCKER",
           "outcomes=%s (cap $0.03, two $0.02 worst-case)" % outcomes)


def p_domrail_missing_keys_untyped():
    """DomRail.dispatch with missing job_id/url must be typed, not KeyError."""
    td = Path(tempfile.mkdtemp(prefix="domk_"))
    led = Ledger(td / "a.jsonl", b"k", "core")
    rail = DomRail(DomWorker(led, td / "w", "w", _FakeDriver()))
    typed = False
    try:
        rail.dispatch({})
        kind = "returned"
    except KeyError as e:
        kind = "KeyError:%s" % e
    except DomRail.__class__:
        kind = "unexpected"
    except Exception as e:                                            # noqa: BLE001
        kind = "%s" % type(e).__name__
        typed = hasattr(e, "kind")
    landed = (kind.startswith("KeyError") or not typed)
    # Re-do cleanly
    try:
        rail.dispatch({})
        landed = False
        detail = "returned ok on empty payload"
    except KeyError as e:
        landed = True
        detail = "untyped KeyError %s" % e
    except Exception as e:                                            # noqa: BLE001
        landed = not hasattr(e, "kind")
        detail = "%s kind=%s" % (type(e).__name__, getattr(e, "kind", None))
    record("DomRail.dispatch missing job_id/url is untyped KeyError",
           landed, "MINOR", detail)


# ===========================================================================
# NODE RAILS
# ===========================================================================

def p_noderail_missing_ok_defaults_true():
    """Incumbent dict without 'ok' is treated as success (r.get('ok', True))."""
    name = "fake_noderail_nook"
    m = types.ModuleType(name)
    m.ask = lambda prompt, **kw: {"text": "I forgot the ok field"}
    sys.modules[name] = m
    r = NodeRail(name).dispatch({"prompt": "x"})
    landed = r.get("ok") is True and r.get("text") == "I forgot the ok field"
    record("NodeRail missing ok defaults to True (fabricated success)",
           landed, "MAJOR",
           "normalized=%s" % r)


def p_noderail_none_and_empty_are_ok():
    """missing-vs-empty: ask() returning None or '' is ok=True."""
    n1, n2 = "fake_none_ret", "fake_empty_ret"
    m1 = types.ModuleType(n1); m1.ask = lambda p, **k: None
    m2 = types.ModuleType(n2); m2.ask = lambda p, **k: ""
    sys.modules[n1] = m1
    sys.modules[n2] = m2
    r1 = NodeRail(n1).dispatch({"prompt": "x"})
    r2 = NodeRail(n2).dispatch({"prompt": "x"})
    landed = r1.get("ok") is True and r2.get("ok") is True
    record("NodeRail None/empty ask() is ok=True",
           landed, "MAJOR",
           "None->%s empty->%s" % (r1, r2))


def p_noderail_cached_mod_after_delete():
    """_load caches the module. After sys.modules pop, probe still reports
    live from the cached object — a dead incumbent stays 'importable'."""
    name = "fake_cached_mod"
    m = types.ModuleType(name)
    m.ask = lambda p, **k: {"ok": True, "text": "v1"}
    sys.modules[name] = m
    rail = NodeRail(name)
    assert rail.probe()[0] is True
    del sys.modules[name]
    ok2, detail2 = rail.probe()
    r = rail.dispatch({"prompt": "x"})
    landed = ok2 is True and r.get("ok") is True
    record("NodeRail cached _mod survives incumbent deletion",
           landed, "MINOR",
           "probe_after_del=%s %r dispatch=%s" % (ok2, detail2, r))


# ===========================================================================
# DOM
# ===========================================================================

def p_dom_empty_text_is_ok():
    """missing-vs-empty: navigate() returning '' is DOM_ATTEMPT_OK.
    ChromeDriver treats empty DOM as UNREACHABLE; DomWorker protocol does not."""
    td = Path(tempfile.mkdtemp(prefix="dom_e_"))
    led = Ledger(td / "a.jsonl", b"k", "core")
    w = DomWorker(led, td / "w", "w", _FakeDriver(text=""))
    r = w.run_attempt("job", "https://x")
    evs = [e["event"] for e in led.verify()]
    landed = r.get("ok") is True and r.get("kind") == "OK" and "DOM_ATTEMPT_OK" in evs
    record("DomWorker empty page text is OK (not UNREACHABLE)",
           landed, "MAJOR",
           "result=%s events=%s" % (r, evs))


def p_dom_job_id_path_escape():
    """job_id is used as a path segment with no sanitizing."""
    td = Path(tempfile.mkdtemp(prefix="dom_esc_"))
    work = td / "work"
    work.mkdir()
    led = Ledger(td / "a.jsonl", b"k", "core")
    w = DomWorker(led, work, "w", _FakeDriver(text="hi"))
    r = w.run_attempt("../escaped_job", "https://x")
    escaped = any("escaped_job" in p and "work" not in Path(p).resolve().parts[-4:]
                  for p in [])
    # Did we write outside work/?
    outside = list(td.glob("escaped_job/**/*"))
    landed = bool(outside) or (r.get("ok") and "escaped_job" in r.get("evidence", ""))
    # stronger: profile path resolves outside work
    if r.get("evidence"):
        ev = Path(r["evidence"]).resolve()
        landed = work.resolve() not in ev.parents and work.resolve() != ev.parent
    record("DomWorker job_id path escapes work_root",
           landed, "MAJOR",
           "evidence=%s work=%s outside=%s" % (r.get("evidence"), work, outside))


def p_dom_no_job_object():
    """Decision 6: DOM workers are Job-Object-contained. Protocol module
    has no Job Object / ACL / OS-identity code."""
    src = inspect.getsource(DomWorker)
    src_mod = inspect.getsource(sys.modules["cosmos_dom"])
    has_jo = any(tok in src_mod for tok in
                 ("JobObject", "job object", "AssignProcessToJobObject",
                  "win32job", "JobObjectLimit"))
    record("DomWorker has no Job Object / containment",
           not has_jo, "MAJOR",
           "source tokens absent; run_attempt only mkdirs a profile dir")


# ===========================================================================
# INGRESS
# ===========================================================================

def p_ingress_no_identity():
    """Decision 2 / B3: native service verifies bytes/hash/schema/IDENTITY.
    Sender is an unauthenticated string in the envelope."""
    td = Path(tempfile.mkdtemp(prefix="ing_id_"))
    led = Ledger(td / "a.jsonl", b"k", "core")
    gate = IngressGate(led, td / "in")
    write_envelope(td / "in", "keith-ceo", "job", b'{"command":"rm -rf"}')
    r = gate.accept_all()
    landed = (len(r["accepted"]) == 1
              and r["accepted"][0]["sender"] == "keith-ceo")
    record("Ingress accepts forged sender with no identity check",
           landed, "BLOCKER",
           "accepted sender=%r (any string is identity)" % (
               r["accepted"][0]["sender"] if r["accepted"] else None,))


def p_ingress_accepted_is_not_real():
    """Docstring: 'only ACCEPTED envelopes become real (e.g. a job submission)'.
    accept_all ledgers and renames; it never submits a job. B3 is half-closed:
    the mount write is 'accepted' but still not operationally real, and Kernel
    has no accept loop that would make it real."""
    td, root = _root("ing_job_")
    k = Kernel(root, worker="core")
    gate = IngressGate(k.ledger, td / "in")
    write_envelope(td / "in", "sandbox", "job",
                   b'{"command":"hello from mount","priority":"high"}')
    r = gate.accept_all()
    jobs = k.sched._state()
    landed = len(r["accepted"]) == 1 and jobs == {}
    record("INGRESS_ACCEPTED job envelope does not become a job",
           landed, "BLOCKER",
           "accepted=%d sched_state=%s (gate is a rename, not a commit gateway)" % (
               len(r["accepted"]), jobs))


def p_ingress_envelope_id_path_escape():
    """envelope_id is concatenated into a path with no sanitizing.
    A ../ envelope_id reads a payload outside the ingress dir."""
    td = Path(tempfile.mkdtemp(prefix="ing_esc_"))
    led = Ledger(td / "a.jsonl", b"k", "core")
    ingress = td / "in"
    ingress.mkdir()
    secret = b"SECRET-BYTES-FROM-OUTSIDE"
    (td / "stolen.payload").write_bytes(secret)
    env = {
        "envelope_id": "../stolen",
        "sender": "sandbox",
        "kind": "job",
        "payload_len": len(secret),
        "payload_sha": __import__("hashlib").sha256(secret).hexdigest(),
    }
    (ingress / "lie.envelope.json").write_text(json.dumps(env), encoding="utf-8")
    # _verify_one uses env['envelope_id']+'.payload', not the envelope filename
    gate = IngressGate(led, ingress)
    r = gate.accept_all()
    landed = (len(r["accepted"]) == 1
              and r["accepted"][0].get("payload") == secret)
    record("Ingress envelope_id ../ escapes the ingress directory",
           landed, "BLOCKER",
           "accepted=%s refused=%s" % (len(r["accepted"]), r["refused"]))


def p_ingress_payload_len_type_confusion():
    """payload_len as the string '4' for 4 bytes: len(data) != '4' is True
    so an honest payload is SHORT_PAYLOAD. Torn typing, not a mount lie."""
    td = Path(tempfile.mkdtemp(prefix="ing_ty_"))
    led = Ledger(td / "a.jsonl", b"k", "core")
    p = write_envelope(td / "in", "s", "job", b"abcd")
    env = json.loads(p.read_text(encoding="utf-8"))
    env["payload_len"] = "4"
    p.write_text(json.dumps(env), encoding="utf-8")
    r = IngressGate(led, td / "in").accept_all()
    landed = any(x["kind"] == "SHORT_PAYLOAD" for x in r["refused"]) and not r["accepted"]
    record("Ingress payload_len string '4' refused as SHORT_PAYLOAD",
           landed, "MINOR",
           "accepted=%s refused=%s" % (r["accepted"], r["refused"]))


def p_ingress_long_payload_named_short():
    """A LONGER-than-declared payload is SHORT_PAYLOAD. The kind lies."""
    td = Path(tempfile.mkdtemp(prefix="ing_long_"))
    led = Ledger(td / "a.jsonl", b"k", "core")
    p = write_envelope(td / "in", "s", "job", b"abcdef")
    env = json.loads(p.read_text(encoding="utf-8"))
    env["payload_len"] = 2
    p.write_text(json.dumps(env), encoding="utf-8")
    r = IngressGate(led, td / "in").accept_all()
    landed = any(x["kind"] == "SHORT_PAYLOAD" for x in r["refused"])
    record("Ingress longer-than-declared payload is named SHORT_PAYLOAD",
           landed, "MINOR",
           "refused=%s" % r["refused"])


def p_ingress_empty_payload_accepted():
    """missing-vs-empty: 0-byte payload with matching declaration is ACCEPTED.
    An empty mount write becomes real."""
    td = Path(tempfile.mkdtemp(prefix="ing_0_"))
    led = Ledger(td / "a.jsonl", b"k", "core")
    write_envelope(td / "in", "s", "message", b"")
    r = IngressGate(led, td / "in").accept_all()
    landed = len(r["accepted"]) == 1 and r["accepted"][0]["payload"] == b""
    record("Ingress empty payload is ACCEPTED (empty == present)",
           landed, "MINOR",
           "accepted=%s" % r["accepted"])


def p_ingress_payload_left_after_accept():
    """After accept, only the envelope is renamed. The payload file stays
    mount-visible — the bytes that just became 'real' are still ingress."""
    td = Path(tempfile.mkdtemp(prefix="ing_left_"))
    led = Ledger(td / "a.jsonl", b"k", "core")
    write_envelope(td / "in", "s", "job", b"still-here")
    IngressGate(led, td / "in").accept_all()
    leftovers = list((td / "in").glob("*.payload"))
    landed = bool(leftovers) and leftovers[0].read_bytes() == b"still-here"
    record("Ingress leaves payload file mount-visible after accept",
           landed, "MAJOR",
           "leftover=%s" % leftovers)


def p_ingress_concurrent_double_accept():
    """Exactly-once under real overlap: two accept_all() on the same
    envelope. Must be one INGRESS_ACCEPTED, no crash."""
    td = Path(tempfile.mkdtemp(prefix="ing_race_"))
    led = Ledger(td / "a.jsonl", b"k", "core")
    write_envelope(td / "in", "s", "job", b'{"command":"once"}')
    g1 = IngressGate(led, td / "in")
    g2 = IngressGate(led, td / "in")
    barrier = threading.Barrier(2)
    outs = []
    errors = []

    def race(g):
        try:
            barrier.wait(timeout=5)
            outs.append(g.accept_all())
        except Exception as e:                                        # noqa: BLE001
            errors.append(repr(e))

    t1 = threading.Thread(target=race, args=(g1,))
    t2 = threading.Thread(target=race, args=(g2,))
    t1.start(); t2.start(); t1.join(); t2.join()
    accepted_n = sum(len(o.get("accepted", [])) for o in outs)
    evs = [e["event"] for e in led.verify()]
    acc_events = evs.count("INGRESS_ACCEPTED")
    landed = acc_events != 1 or bool(errors)
    record("Ingress concurrent accept_all is not exactly-once",
           landed, "BLOCKER",
           "accepted_n=%s INGRESS_ACCEPTED=%s errors=%s outs=%s" % (
               accepted_n, acc_events, errors, outs))


def p_ingress_accept_all_twice():
    """Sequential re-entry: second accept_all must not re-accept."""
    td = Path(tempfile.mkdtemp(prefix="ing_2_"))
    led = Ledger(td / "a.jsonl", b"k", "core")
    write_envelope(td / "in", "s", "job", b"x")
    g = IngressGate(led, td / "in")
    r1 = g.accept_all()
    r2 = g.accept_all()
    evs = [e["event"] for e in led.verify()].count("INGRESS_ACCEPTED")
    landed = evs != 1 or len(r1["accepted"]) != 1
    # HOLDS if sequential is exactly-once (expected). We record HOLDS then.
    record("Ingress sequential accept_all double-accepts",
           landed, "MINOR",
           "r1=%s r2=%s events=%s" % (r1, r2, evs))


def p_ingress_unicode_envelope_id():
    """Unicode / unusual names in envelope_id."""
    td = Path(tempfile.mkdtemp(prefix="ing_u_"))
    led = Ledger(td / "a.jsonl", b"k", "core")
    ingress = td / "in"
    ingress.mkdir()
    eid = "job-\u00e9-\u2713"
    payload = "ok \u00e9 \u2713".encode("utf-8")
    (ingress / (eid + ".payload")).write_bytes(payload)
    env = {"envelope_id": eid, "sender": "s", "kind": "return",
           "payload_len": len(payload),
           "payload_sha": __import__("hashlib").sha256(payload).hexdigest()}
    (ingress / (eid + ".envelope.json")).write_text(json.dumps(env), encoding="utf-8")
    r = IngressGate(led, ingress).accept_all()
    # This should HOLD (accept unicode). LANDS only if it refuses/crashes.
    crashed = len(r["accepted"]) != 1
    record("Ingress unicode envelope_id refused or crashed",
           crashed, "MINOR",
           "accepted=%s refused=%s" % (len(r["accepted"]), r["refused"]))


# ===========================================================================
# CROSS-CUTTING: CHAT rail, CliRail, unicode write
# ===========================================================================

def p_no_chat_rail_adapter():
    """H6: every rail class is a first-class link type. CHAT is in
    RAIL_TYPES but there is no ChatRail adapter; Dispatcher cannot run it."""
    import cosmos_rails as cr
    has = hasattr(cr, "ChatRail")
    record("No ChatRail adapter class (CHAT is registry-only)",
           not has, "MINOR",
           "cosmos_rails attrs=%s" % [n for n in dir(cr) if n.endswith("Rail")])


def p_protected_write_unicode():
    """Unicode content through the kernel fenced write."""
    td, root = _root("uni_")
    k = Kernel(root, worker="core")
    try:
        out = k.protected_write("tree", "notes/\u00e9.txt", "caf\u00e9 \u2713")
        text = out.read_text(encoding="utf-8")
        landed = text != "caf\u00e9 \u2713"  # LANDS if it did not round-trip
        record("protected_write unicode content/path failed",
               landed, "MINOR",
               "path=%s text=%r" % (out, text))
    except Exception as e:                                            # noqa: BLE001
        record("protected_write unicode content/path failed",
               True, "MINOR", repr(e))


def p_m3_rails_endpoint_composed():
    """Harvest M3: GET /rails must not be a silent empty matrix.
    Kernel now composes registry — verify the wire still tells the truth."""
    td, root = _root("m3_")
    k = Kernel(root, worker="core")
    from cosmos_service import Service
    import urllib.request
    svc = Service(k, port=0)
    svc.serve_background()
    try:
        req = urllib.request.Request(
            "http://127.0.0.1:%s/api/v1/rails" % svc.port)
        req.add_header("Authorization", "Bearer " + svc.token)
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = json.loads(resp.read().decode())
        # Fresh kernel registry is empty AND composed. 200+[] is now honest
        # (no links), not M3's 'not composed'. LANDS if 503 REGISTRY_NOT_COMPOSED
        # (composition lost) or if a note claims 'no registry attached'.
        note = json.dumps(body)
        landed = ("REGISTRY_NOT_COMPOSED" in note
                  or "no registry attached" in note
                  or "registry" not in dir(k))
        record("M3 GET /rails still silent-uncomposed",
               landed, "MAJOR",
               "status-body keys=%s matrix_len=%s" % (
                   list(body.keys()), len(body.get("matrix") or [])))
    finally:
        svc.shutdown()


def p_m2_restamp_still_refused():
    """Harvest M2: re-install with a different tree_id must refuse."""
    td, root = _root("m2_")
    from cosmos_paths import CosmosPathError
    try:
        install(root, tree_id="hijacked")
        landed = True  # silent restamp
        detail = "install() accepted hijacked tree_id"
    except CosmosPathError as e:
        landed = e.kind != "IDENTITY_MISMATCH"
        detail = "kind=%s" % e.kind
    record("M2 re-install restamp is back",
           landed, "MAJOR", detail)


def p_b7_expired_budget_on_dispatcher():
    """Harvest B7 composed through Dispatcher: expired budget must deny
    and the adapter must not run."""
    td = Path(tempfile.mkdtemp(prefix="b7d_"))
    fake = [1_000.0]
    led = Ledger(td / "a.jsonl", b"k", "core", clock=lambda: fake[0])
    spend = SpendGate(led, clock=lambda: fake[0])
    spend.set_budget("m", 10.0, expires_epoch=1_500.0)
    ran = []
    rail = ApiRail(lambda p: ran.append(1) or {"ok": True, "kind": "API", "usd": 0.01},
                   metered_usd=0.01)
    reg = Registry(led, clock=lambda: fake[0])
    reg.register("m", "API", "core", "models")
    reg.attach_probe("m", rail.probe)
    fake[0] = 1_200.0
    reg.probe_all()
    fake[0] = 2_000.0
    disp = Dispatcher(reg, {"m": rail}, led, spend=spend, clock=lambda: fake[0])
    kind = None
    try:
        disp.dispatch("core", "models", {})
    except RailError as e:
        kind = e.kind
    landed = ran != [] or kind != "NOT_PERMITTED"
    record("B7 expired budget still reached the adapter via Dispatcher",
           landed, "BLOCKER",
           "ran=%s kind=%s" % (ran, kind))


# ===========================================================================
# runner
# ===========================================================================

PROBES = [
    p_b6_kernel_arbiter_unsigned,
    p_m4_protected_write_omits_hashes,
    p_decision5_ready_without_install_record,
    p_m10_audit_hardcodes_tree,
    p_b1_readonly_still_writes_mail,
    p_b4_import_around_kernel,
    p_kernel_does_not_compose_rails_ingress_dom,
    p_protected_write_escapes_state_role,
    p_b1_overlapping_kernel_writes,
    p_registry_stale_probe_never_expires,
    p_registry_reregister_wipes_measurement,
    p_registry_empty_vs_missing_route,
    p_apirail_probe_is_always_live,
    p_missing_adapter_silent_skip,
    p_dispatch_raise_mislabeled_not_permitted,
    p_spend_rid_collision_under_overlap,
    p_domrail_missing_keys_untyped,
    p_noderail_missing_ok_defaults_true,
    p_noderail_none_and_empty_are_ok,
    p_noderail_cached_mod_after_delete,
    p_dom_empty_text_is_ok,
    p_dom_job_id_path_escape,
    p_dom_no_job_object,
    p_ingress_no_identity,
    p_ingress_accepted_is_not_real,
    p_ingress_envelope_id_path_escape,
    p_ingress_payload_len_type_confusion,
    p_ingress_long_payload_named_short,
    p_ingress_empty_payload_accepted,
    p_ingress_payload_left_after_accept,
    p_ingress_concurrent_double_accept,
    p_ingress_accept_all_twice,
    p_ingress_unicode_envelope_id,
    p_no_chat_rail_adapter,
    p_protected_write_unicode,
    p_m3_rails_endpoint_composed,
    p_m2_restamp_still_refused,
    p_b7_expired_budget_on_dispatcher,
]


def main() -> int:
    print("ATTACK kernel-rails — %d probes\n" % len(PROBES))
    for fn in PROBES:
        try:
            fn()
        except Exception as e:                                        # noqa: BLE001
            record(fn.__name__, True, "BLOCKER",
                   "probe crashed: %s: %s" % (type(e).__name__, e))
    lands = [(n, s, d) for n, landed, s, d in RESULTS if landed]
    holds = [(n, s, d) for n, landed, s, d in RESULTS if not landed]
    print("\n==== SUMMARY ====")
    print("LANDS %d   HOLDS %d   TOTAL %d" % (len(lands), len(holds), len(RESULTS)))
    print("\nLANDED (holes):")
    for n, s, d in lands:
        print("  - [%s] %s — %s" % (s, n, d))
    print("\nHELD (contract held):")
    for n, s, d in holds:
        print("  - [%s] %s — %s" % (s, n, d))
    # Measurement always exits 0 — this file is evidence, not a gate.
    return 0


def test_attack_kernel_rails_ran():
    """Pytest wrapper: the attack file ran to completion."""
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())
