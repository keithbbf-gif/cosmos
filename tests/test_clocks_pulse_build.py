#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: the CLOCKS Pulse BUILD proposal (proposals/clocks-pulse-build.json +
proposals/pulse/cosmos_pulse.py + proposals/pulse/pulse_bind.py).

House rules, applied to a proposal instead of to the tree:
  * every row RUNS - no row asserts a document's prose
  * refusals are checked BY KIND, never by "it raised something"
  * a PLANTED-FAILURE row must be RED on every pass; a board where it goes green is broken
  * runnable two ways: `python tests/test_clocks_pulse_build.py` (GitLab CI runs tests this
    way) and `pytest tests/test_clocks_pulse_build.py`
"""
from __future__ import annotations

import contextlib
import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "proposals" / "pulse"))

from cosmos_pulse import (
    TICK_S, Clock, Done, LostClaim, Pulse, PulseError, Running, Wheel, clocks_from_plan,
    main as pulse_main,
)
from pulse_bind import ALLOWED_SCHTASK_ACTIONS, bind

PLAN_PATH = ROOT / "proposals" / "clocks-pulse-build.json"
PLAN = json.loads(PLAN_PATH.read_text(encoding="utf-8"))

RESULTS: list[tuple[str, bool, str]] = []


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                              # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def refuses(kind, fn):
    """Assert a REFUSAL BY KIND. 'It raised' is not a measurement."""
    try:
        fn()
    except PulseError as e:
        return e.kind == kind
    return False


def kinds(report):
    return {r["kind"] for r in report.refusals}


# ------------------------------------------------------------------ fixtures
def leaf(cid="leaf", **kw):
    kw.setdefault("disposition", "pulse.inproc")
    kw.setdefault("period_s", 15)
    kw.setdefault("deadline_s", 60)
    return Clock(id=cid, **kw)


def synthetic_registry(n=26):
    return [f"cosmos.clock.{i:02d}" for i in range(n)]


def synthetic_bindings(names, **overrides):
    out = []
    for i, name in enumerate(names):
        row = {"clock": name, "disposition": "pulse.inproc", "period_s": 15,
               "deadline_s": 60, "role": f"role.{i:02d}"}
        row.update(overrides.get(name, {}))
        out.append(row)
    return out


def plan_with(bound, **plan_overrides):
    p = json.loads(json.dumps(PLAN))
    p["bindings"]["bound"] = bound
    p.update(plan_overrides)
    return p


# ------------------------------------------------------------------ clock validation
def rows_clock_validation():
    check("clock: unknown disposition refuses BY KIND",
          lambda: refuses("UNKNOWN_DISPOSITION",
                          lambda: Clock(id="x", disposition="daemon", period_s=15,
                                        deadline_s=60)))
    check("clock: pulse.once without a command refuses",
          lambda: refuses("MISSING_COMMAND",
                          lambda: Clock(id="x", disposition="pulse.once", period_s=15,
                                        deadline_s=60)))
    check("clock: zero period refuses",
          lambda: refuses("BAD_PERIOD",
                          lambda: Clock(id="x", disposition="pulse.inproc", period_s=0,
                                        deadline_s=60)))
    check("clock: a HOLD-required duty cannot be parked",
          lambda: refuses("HOLD_DUTY_PARKED",
                          lambda: Clock(id="collector", disposition="parked", period_s=30,
                                        deadline_s=60, hold_required=True)))
    check("clock: an undeclared cadence change REFUSES (nobody assumes the tolerance)",
          lambda: refuses("QUANTIZATION_UNDECLARED",
                          lambda: Clock(id="tight", disposition="pulse.inproc",
                                        period_s=20, deadline_s=120)))
    check("clock: quantization past the declared tolerance REFUSES",
          lambda: refuses("QUANTIZATION_EXCEEDS_TOLERANCE",
                          lambda: Clock(id="tight", disposition="pulse.inproc",
                                        period_s=20, deadline_s=120, max_interval_s=25)))
    check("clock: 20s quantizes to 30s on the 15s grid, and says so",
          lambda: leaf("q", period_s=20, deadline_s=120,
                       max_interval_s=30).effective_period_s == 30.0)
    check("clock: quantization is flagged, not hidden",
          lambda: leaf("q", period_s=20, deadline_s=120, max_interval_s=30).quantized)
    check("clock: an exact-grid period needs no tolerance and is not flagged",
          lambda: not leaf("exact", period_s=30, deadline_s=120).quantized)
    check("clock: a daily calendar-shaped duty is not refused for having a short deadline",
          lambda: Clock(id="nightly", disposition="pulse.once", period_s=86400,
                        deadline_s=600, command="x --once").effective_period_s == 86400)
    check("clock: stale_after_s = 2*effective + deadline, published per clock",
          lambda: leaf("s", period_s=30, deadline_s=45).stale_after_s == 105.0)
    check("clock: phase offset is deterministic across constructions",
          lambda: leaf("same", period_s=150, deadline_s=600).phase
                  == leaf("same", period_s=150, deadline_s=600).phase)


# ------------------------------------------------------------------ wheel
def rows_wheel():
    def spread():
        clocks = [leaf(f"c{i}", period_s=150, deadline_s=600) for i in range(26)]
        w = Wheel(clocks)
        counts = [len(w.due(t)) for t in range(10)]
        # 26 clocks over 10 slots: no single tick may carry them all
        return max(counts) < 26 and sum(counts) == 26

    check("wheel: duplicate clock id refuses",
          lambda: refuses("DUPLICATE_CLOCK", lambda: Wheel([leaf("dup"), leaf("dup")])))
    check("wheel: deterministic phases spread 26 clocks over the period",
          spread)
    check("wheel: a 15s clock is due every tick",
          lambda: all(leaf("t").due_at(t) for t in range(5)))
    check("wheel: registry keeps non-dispatched entries (census counts all 26)",
          lambda: sum(Wheel(
              [leaf(f"p{i}") for i in range(24)]
              + [Clock(id="core", disposition="resident.keep", period_s=15, deadline_s=60),
                 Clock(id="nightly", disposition="calendar.once", period_s=86400,
                       deadline_s=3600, command="x --once")]
          ).residency_census().values()) == 26)
    check("wheel: calendar/resident clocks are never in the due set",
          lambda: Wheel([
              Clock(id="core", disposition="resident.keep", period_s=15, deadline_s=60),
              Clock(id="nightly", disposition="calendar.once", period_s=86400,
                    deadline_s=3600, command="x --once")]).due(0) == [])
    check("wheel: cheapest-first admission order",
          lambda: [c.id for c in Wheel([leaf("fat", budget_ms=4000),
                                        leaf("thin", budget_ms=10)]).due(0)]
                  == ["thin", "fat"])


# ------------------------------------------------------------------ pulse tick
def _pulse(clocks, dispatch, **kw):
    kw.setdefault("identity", "pulse@test")
    return Pulse(Wheel(clocks), dispatch, **kw)


def rows_tick():
    def single_flight():
        state = {"done": False}
        c = leaf("slow", deadline_s=3600)
        p = _pulse([c], lambda _c: Running(lambda: "CLEAN" if state["done"] else None))
        r1 = p.tick()
        r2 = p.tick()
        state["done"] = True
        r3 = p.tick()
        return (r1["ran"]["slow"] == "RUNNING"
                and r2["skipped"].get("slow") == "INFLIGHT"
                and "slow" not in r2["ran"]
                and p.last["slow"]["outcome"] == "CLEAN"
                and r3["skipped"].get("slow") is None)

    def budget_defers():
        clocks = [leaf(f"fat{i}", budget_ms=3000) for i in range(4)]
        p = _pulse(clocks, lambda _c: Done("CLEAN"), tick_budget_s=5.0)
        r = p.tick()
        deferred = [i for i, why in r["skipped"].items() if why == "BUDGET"]
        return (len(r["ran"]) >= 1 and len(deferred) >= 1
                and set(deferred) == set(r["deferred"]))

    def deferred_run_first():
        clocks = [leaf(f"fat{i}", budget_ms=3000) for i in range(4)]
        p = _pulse(clocks, lambda _c: Done("CLEAN"), tick_budget_s=5.0)
        r1 = p.tick()
        first_deferred = r1["deferred"][0]
        r2 = p.tick()
        return first_deferred in r2["ran"]

    def hold_keeps_collector():
        clocks = [leaf("collector", hold_required=True), leaf("discretionary")]
        p = _pulse(clocks, lambda _c: Done("CLEAN"), hold=lambda: True)
        r = p.tick()
        return (r["ran"].get("collector") == "CLEAN"
                and r["skipped"].get("discretionary") == "HOLD")

    def stale_reported_not_retried():
        c = leaf("wedged", deadline_s=15)
        p = _pulse([c], lambda _c: Running(lambda: None))
        p.tick()
        p.tick()
        r3 = p.tick()
        return ("wedged" in r3["stale"] and "wedged" in p.quarantined
                and p.tick()["skipped"].get("wedged") == "QUARANTINED")

    def idempotent_not_quarantined():
        c = leaf("retryable", deadline_s=15, idempotent=True)
        p = _pulse([c], lambda _c: Running(lambda: None))
        p.tick(); p.tick(); p.tick()
        return "retryable" not in p.quarantined

    def core_spawn_refused():
        c = leaf("core.spawner", spawns_core=True)
        p = _pulse([c], lambda _c: Done("CLEAN"))
        r = p.tick()
        return (r["skipped"].get("core.spawner") == "CORE_SPAWN_NOT_OWNED"
                and any("Health" in x for x in r["refusals"]))

    def core_spawn_allowed_after_handoff():
        c = leaf("core.spawner", spawns_core=True)
        p = _pulse([c], lambda _c: Done("CLEAN"), core_spawn_owner=True)
        return p.tick()["ran"].get("core.spawner") == "CLEAN"

    def dispatch_raise_is_broke():
        def boom(_c):
            raise RuntimeError("child would not start")
        p = _pulse([leaf("bad"), leaf("red", planted_red=True)], boom)
        r = p.tick()
        return r["ran"]["bad"] == "BROKE" and r["verdict"].startswith("RED")

    def grid_does_not_drift():
        t = {"v": 0.0}
        p = _pulse([leaf("c")], lambda _c: Done("CLEAN"), mono=lambda: t["v"])
        p.tick()                       # establishes t0 at 0.0, tick 0
        t["v"] = TICK_S + 4.0          # a slow pass: 4s late
        s1 = p.tick()["tick_seq"]
        t["v"] = 2 * TICK_S            # next boundary is still 2*tick, not 2*tick+4
        s2 = p.tick()["tick_seq"]
        return s1 == 1 and s2 == 2 and p.skew_ticks == 0

    def skew_reported():
        t = {"v": 0.0}
        p = _pulse([leaf("c")], lambda _c: Done("CLEAN"), mono=lambda: t["v"])
        p.tick()
        t["v"] = 10 * TICK_S           # Pulse was away for ~10 slots
        p.tick()
        return p.skew_ticks == 9 and p.tick_seq == 10

    def tick_budget_must_fit_grid():
        try:
            Pulse(Wheel([leaf("c")]), lambda _c: Done("CLEAN"), tick_budget_s=TICK_S)
        except PulseError as e:
            return e.kind == "BAD_PERIOD"
        return False

    check("tick: single-flight - a slow clock never doubles up", single_flight)
    check("tick: over-budget work is DEFERRED, never dropped", budget_defers)
    check("tick: a deferred clock runs at the head of the next tick", deferred_run_first)
    check("tick: HOLD runs the collector and skips the rest, with reasons",
          hold_keeps_collector)
    check("tick: stale in-flight is REPORTED and quarantined, never retried",
          stale_reported_not_retried)
    check("tick: a clock that declares idempotent is not quarantined",
          idempotent_not_quarantined)
    check("tick: Pulse REFUSES to spawn Core before the handoff", core_spawn_refused)
    check("tick: after the handoff, the same clock runs", core_spawn_allowed_after_handoff)
    check("tick: a dispatch that raises is BROKE, not a crash", dispatch_raise_is_broke)
    check("tick: grid deadlines do not drift after a slow pass", grid_does_not_drift)
    check("tick: missed slots are reported as skew, with at most one catch-up", skew_reported)
    check("tick: a budget that can eat the whole period refuses", tick_budget_must_fit_grid)


# ------------------------------------------------------------------ negative control
def rows_negative_control():
    def planted_red_green_breaks_board():
        p = _pulse([leaf("pulse.selftest.planted_red", planted_red=True)],
                   lambda _c: Done("CLEAN"))
        return p.tick()["verdict"].startswith("PULSE-BROKEN")

    def planted_red_red_is_green_board():
        p = _pulse([leaf("pulse.selftest.planted_red", planted_red=True), leaf("ok")],
                   lambda c: Done("BROKE" if c.planted_red else "CLEAN"))
        return p.tick()["verdict"] == "GREEN"

    def no_control_is_unverified():
        p = _pulse([leaf("ok")], lambda _c: Done("CLEAN"))
        return p.tick()["verdict"].startswith("PULSE-UNVERIFIED")

    def control_is_never_deferred_by_budget():
        clocks = [leaf(f"fat{i}", budget_ms=3000) for i in range(6)]
        clocks.append(leaf("pulse.selftest.planted_red", planted_red=True,
                           budget_ms=3000))
        p = _pulse(clocks, lambda c: Done("BROKE" if c.planted_red else "CLEAN"),
                   tick_budget_s=5.0)
        r = p.tick()
        return (r["deferred"] and "pulse.selftest.planted_red" in r["ran"]
                and r["verdict"] == "GREEN")

    def control_that_did_not_run_is_not_a_pass():
        c = leaf("pulse.selftest.planted_red", planted_red=True)
        p = _pulse([c, leaf("ok")], lambda _c: Done("CLEAN"))
        p.quarantined[c.id] = "planted by the test: the control cannot run"
        r = p.tick()
        return (r["verdict"].startswith("PULSE-UNVERIFIED")
                and "QUARANTINED" in r["verdict"])

    check("control: planted-red going GREEN publishes PULSE-BROKEN",
          planted_red_green_breaks_board)
    check("control: planted-red RED with everything else clean is GREEN",
          planted_red_red_is_green_board)
    check("control: a wheel with no planted row reports PULSE-UNVERIFIED",
          no_control_is_unverified)
    check("control: budget pressure never defers the control row",
          control_is_never_deferred_by_budget)
    check("control: a control that could not run publishes PULSE-UNVERIFIED, not GREEN",
          control_that_did_not_run_is_not_a_pass)


# ------------------------------------------------------------------ claims
def rows_claims():
    def pool_only_drain_is_bounded():
        calls = {"n": 0}

        def claim():
            calls["n"] += 1
            return {"job": calls["n"]}
        p = _pulse([leaf("c")], lambda _c: Done("CLEAN"), claim_next=claim,
                   max_claims_per_tick=4)
        r = p.tick()
        return r["claims"]["taken"] == 4 and calls["n"] == 4

    def empty_queue_stops_early():
        p = _pulse([leaf("c")], lambda _c: Done("CLEAN"), claim_next=lambda: None)
        r = p.tick()
        return r["claims"]["empty"] and r["claims"]["taken"] == 0

    def lost_claim_is_counted_not_fatal():
        seq = [LostClaim("head moved"), {"job": 1}, None]

        def claim():
            item = seq.pop(0)
            if isinstance(item, LostClaim):
                raise item
            return item
        p = _pulse([leaf("c"), leaf("red", planted_red=True)],
                   lambda c: Done("BROKE" if c.planted_red else "CLEAN"),
                   claim_next=claim)
        r = p.tick()
        return (r["claims"]["lost"] == 1 and r["claims"]["taken"] == 1
                and r["verdict"] == "GREEN")

    def no_claim_surface_is_silent():
        p = _pulse([leaf("c")], lambda _c: Done("CLEAN"))
        return p.tick()["claims"] == {"taken": 0, "lost": 0, "empty": False}

    check("claims: pool-only drain is bounded per tick", pool_only_drain_is_bounded)
    check("claims: an empty pool stops the drain immediately", empty_queue_stops_early)
    check("claims: a LOST_CLAIM is typed, counted and non-fatal",
          lost_claim_is_counted_not_fatal)
    check("claims: Pulse holds no claim logic when no surface is wired",
          no_claim_surface_is_silent)


# ------------------------------------------------------------------ heartbeat
def rows_heartbeat():
    def hb():
        p = _pulse([leaf("ran"), leaf("never", period_s=3600, deadline_s=600,
                                      max_interval_s=3600),
                    Clock(id="nightly", disposition="calendar.once", period_s=86400,
                          deadline_s=3600, command="x --once")],
                   lambda _c: Done("CLEAN"))
        p.tick()
        return p, p.heartbeat()

    def identity_and_time():
        _, h = hb()
        return all(h.get(k) for k in ("writer", "utc", "local", "tz_offset", "mechanism")) \
            and isinstance(h["epoch"], float)

    def carries_every_clock():
        _, h = hb()
        return h["clock_count"] == 3 and len(h["clocks"]) == 3

    def four_states_not_collapsed():
        _, h = hb()
        return (h["clocks"]["never"]["state"] == "NEVER-RUN"
                and h["clocks"]["ran"]["state"] == "IDLE"
                and h["clocks"]["never"]["last_run_epoch"] is None)

    def publishes_staleness_threshold():
        _, h = hb()
        return all(row["stale_after_s"] > 0 for row in h["clocks"].values())

    def residency_visible():
        _, h = hb()
        return h["clocks"]["nightly"]["residency"] == "calendar.once"

    def legacy_shim_covers_every_clock():
        p, h = hb()
        shim = p.legacy_heartbeats()
        return (len(shim) == len(h["clocks"])
                and all(v["via"] == "pulse" and "stale_after_s" in v
                        for v in shim.values()))

    check("heartbeat: writer identity + epoch + UTC + aware-local + offset",
          identity_and_time)
    check("heartbeat: one file carries every clock", carries_every_clock)
    check("heartbeat: NEVER-RUN is its own state, not stale and not green",
          four_states_not_collapsed)
    check("heartbeat: every clock publishes its own stale_after_s",
          publishes_staleness_threshold)
    check("heartbeat: residency is visible to the index", residency_visible)
    check("heartbeat: legacy shim re-emits every clock under the old filenames",
          legacy_shim_covers_every_clock)


# ------------------------------------------------------------------ binding gate
def rows_bind():
    live = synthetic_registry(26)

    def happy_path():
        r = bind(plan_with(synthetic_bindings(live)), live)
        return r.ok and r.bound == 26 and r.census["pulse.inproc"] == 26

    def unbound_ships_refusing():
        r = bind(PLAN, live)
        return not r.ok and "UNBOUND_CLOCK" in kinds(r) and "CLOCKS_SHRUNK" in kinds(r)

    def self_consistency_only():
        r = bind(PLAN, [])
        return not r.ok and kinds(r) == {"UNBOUND_PLAN"}

    def shrink_refused():
        r = bind(plan_with(synthetic_bindings(live[:25])), live)
        return "CLOCKS_SHRUNK" in kinds(r) and "UNBOUND_CLOCK" in kinds(r)

    def invented_clock_refused():
        rows = synthetic_bindings(live)
        rows[0] = dict(rows[0], clock="cosmos.clock.invented")
        return "UNKNOWN_CLOCK" in kinds(bind(plan_with(rows), live))

    def duplicate_binding_refused():
        rows = synthetic_bindings(live)
        rows.append(dict(rows[0]))
        return "DUPLICATE_BINDING" in kinds(bind(plan_with(rows), live))

    def count_mismatch_refused():
        return "REGISTRY_COUNT_MISMATCH" in kinds(
            bind(plan_with(synthetic_bindings(synthetic_registry(25))),
                 synthetic_registry(25)))

    def quantization_undeclared_refused():
        rows = synthetic_bindings(live, **{live[0]: {"period_s": 20, "deadline_s": 300}})
        return "QUANTIZATION_UNDECLARED" in kinds(bind(plan_with(rows), live))

    def quantization_over_tolerance_refused():
        rows = synthetic_bindings(live, **{live[0]: {"period_s": 20, "deadline_s": 300,
                                                     "max_interval_s": 25}})
        return "QUANTIZATION_EXCEEDS_TOLERANCE" in kinds(bind(plan_with(rows), live))

    def quantization_noted_when_safe():
        rows = synthetic_bindings(live, **{live[0]: {"period_s": 20, "deadline_s": 300,
                                                     "max_interval_s": 45}})
        r = bind(plan_with(rows), live)
        return r.ok and any("-> 30" in n for n in r.notes)

    def hold_duty_parked_refused():
        rows = synthetic_bindings(
            live, **{live[0]: {"disposition": "parked", "hold_required": True}})
        return "HOLD_DUTY_PARKED" in kinds(bind(plan_with(rows), live))

    def core_spawn_unphased_refused():
        rows = synthetic_bindings(live, **{live[0]: {"spawns_core": True}})
        return "CORE_SPAWN_UNPHASED" in kinds(bind(plan_with(rows), live))

    def supervise_dropped_early_refused():
        rows = synthetic_bindings(
            live, **{live[0]: {"role": "health.supervise", "disposition": "pulse.once",
                               "command": "cosmos_health.py --once"}})
        plan = plan_with(rows)
        for ph in plan["phases"]:
            ph.pop("grants_core_spawn", None)
        return "SUPERVISE_DROPPED_EARLY" in kinds(bind(plan, live))

    def schtask_delete_refused():
        plan = plan_with(synthetic_bindings(live))
        plan["schtasks"] = plan["schtasks"] + [
            {"name": "COSMOS Old Loop", "action": "delete", "read_back": "x"}]
        k = kinds(bind(plan, live))
        return "FORBIDDEN_SCHTASK_ACTION" in k

    def delete_in_a_command_refused():
        plan = plan_with(synthetic_bindings(live))
        plan["schtasks"] = plan["schtasks"] + [
            {"name": "sneaky", "action": "change_disable", "read_back": "q",
             "command": "schtasks /delete /tn \"COSMOS Old Loop\" /f"}]
        return "SCHTASK_DELETE" in kinds(bind(plan, live))

    def read_back_required():
        plan = plan_with(synthetic_bindings(live))
        plan["schtasks"] = plan["schtasks"] + [
            {"name": "no-readback", "action": "register"}]
        return "NO_READ_BACK" in kinds(bind(plan, live))

    def core_down_phase_refused():
        plan = plan_with(synthetic_bindings(live))
        plan["phases"][1]["core_restart"] = True
        return "CORE_DOWN" in kinds(bind(plan, live))

    def early_handoff_refused():
        plan = plan_with(synthetic_bindings(live))
        for ph in plan["phases"]:
            ph.pop("grants_core_spawn", None)
        plan["phases"][1]["grants_core_spawn"] = True
        return "SPAWN_HANDOFF_EARLY" in kinds(bind(plan, live))

    def two_spawn_owners_refused():
        plan = plan_with(synthetic_bindings(live))
        plan["phases"][1]["grants_core_spawn"] = True
        return "TWO_SPAWN_OWNERS" in kinds(bind(plan, live))

    def phase_without_gate_refused():
        plan = plan_with(synthetic_bindings(live))
        plan["phases"][0].pop("gate")
        plan["phases"][0].pop("rollback")
        k = kinds(bind(plan, live))
        return "PHASE_WITHOUT_GATE" in k and "PHASE_WITHOUT_ROLLBACK" in k

    def hold_lift_refused():
        plan = plan_with(synthetic_bindings(live))
        plan["guards"]["hold"] = "lifted"
        return "HOLD_LIFT" in kinds(bind(plan, live))

    def anthropic_on_refused():
        plan = plan_with(synthetic_bindings(live))
        plan["guards"]["anthropic_off"] = False
        return "ANTHROPIC_ON" in kinds(bind(plan, live))

    def grokbot_pen_refused():
        rows = synthetic_bindings(
            live, **{live[0]: {"disposition": "pulse.once",
                               "command": "py -3.14 V:\\Ai\\cosmos_leaf.py --once"}})
        return "GROKBOT_PEN" in kinds(bind(plan_with(rows), live))

    def write_fence_refused():
        plan = plan_with(synthetic_bindings(live))
        plan["outputs"] = plan["outputs"] + ["cosmos/cosmos_own_clocks.py"]
        return "WRITE_FENCE" in kinds(bind(plan, live))

    check("bind: 26 live clocks bound to 26 dispositions passes", happy_path)
    check("bind: the SHIPPED manifest refuses against a live registry (fail-closed)",
          unbound_ships_refusing)
    check("bind: shipped manifest alone refuses with exactly UNBOUND_PLAN",
          self_consistency_only)
    check("bind: a dropped clock refuses - CLOCKS may not shrink", shrink_refused)
    check("bind: an invented clock name refuses", invented_clock_refused)
    check("bind: the same clock bound twice refuses", duplicate_binding_refused)
    check("bind: plan count vs export count mismatch refuses", count_mismatch_refused)
    check("bind: an undeclared cadence change refuses", quantization_undeclared_refused)
    check("bind: quantization past the declared tolerance refuses",
          quantization_over_tolerance_refused)
    check("bind: safe quantization is NOTED, not silent", quantization_noted_when_safe)
    check("bind: a HOLD-required duty cannot be parked", hold_duty_parked_refused)
    check("bind: a Core-spawn clock with no phase refuses", core_spawn_unphased_refused)
    check("bind: Health --supervise cannot be stood down early",
          supervise_dropped_early_refused)
    check("bind: a schtask delete ACTION refuses", schtask_delete_refused)
    check("bind: /delete hidden in a command string refuses", delete_in_a_command_refused)
    check("bind: a schtask edit with no read-back refuses", read_back_required)
    check("bind: a phase that restarts Core refuses", core_down_phase_refused)
    check("bind: a Core-spawn handoff before the last phase refuses", early_handoff_refused)
    check("bind: two phases granting Core spawn refuses", two_spawn_owners_refused)
    check("bind: a phase with no gate or no rollback refuses", phase_without_gate_refused)
    check("bind: lifting HOLD refuses", hold_lift_refused)
    check("bind: turning Anthropic back on refuses", anthropic_on_refused)
    check("bind: a command writing V:\\Ai refuses", grokbot_pen_refused)
    check("bind: an output outside the write fence refuses", write_fence_refused)


# ------------------------------------------------------------------ shipped manifest
def rows_manifest():
    check("manifest: posture is PROPOSE-ONLY",
          lambda: PLAN["guards"]["posture"] == "PROPOSE-ONLY")
    check("manifest: tick is 15s", lambda: PLAN["pulse"]["tick_s"] == 15)
    check("manifest: 26 clocks required, 0 bound - it ships fail-closed",
          lambda: PLAN["bindings"]["bind_required"] == 26
                  and PLAN["bindings"]["bound"] == [])
    check("manifest: registry entries after the collapse are still 26",
          lambda: PLAN["classification"]["residency_target"]["registry_entries_after"] == 26)
    check("manifest: exactly two resident python processes remain",
          lambda: PLAN["classification"]["residency_target"]
                  ["resident_python_processes_after"] == 2)
    check("manifest: no schtask action is outside the allow-list",
          lambda: all(t["action"] in ALLOWED_SCHTASK_ACTIONS for t in PLAN["schtasks"]))
    check("manifest: no phase stops or restarts Core",
          lambda: not any(p.get("core_stop") or p.get("core_restart")
                          for p in PLAN["phases"]))
    check("manifest: every phase has a gate and a rollback",
          lambda: all(p.get("gate") and p.get("rollback") for p in PLAN["phases"]))
    check("manifest: the Core-spawn handoff is the last phase",
          lambda: [p["id"] for p in PLAN["phases"] if p.get("grants_core_spawn")]
                  == [PLAN["phases"][-1]["id"]])
    check("manifest: all six named couplings are addressed",
          lambda: len(PLAN["couplings"]) == 6)
    check("manifest: every output stays inside the write fence",
          lambda: all(any(o.startswith(f) for f in PLAN["guards"]["write_fence"])
                      for o in PLAN["outputs"]))
    check("manifest: the missing context docs are recorded, not glossed",
          lambda: any("AGENT_BRIEF" in g["detail"] for g in PLAN["context_gaps"]))
    check("manifest: live-host checks are marked UNMEASURED, never invented green",
          lambda: any(a["status"].startswith("UNMEASURED") for a in PLAN["acceptance"])
                  and all("green" not in a["status"].lower() for a in PLAN["acceptance"]))
    check("manifest: every declared output exists in this branch",
          lambda: all((ROOT / o).exists() for o in PLAN["outputs"]))
    check("manifest: clocks_from_plan on the unbound manifest yields an empty wheel",
          lambda: clocks_from_plan(PLAN) == [])


# ------------------------------------------------------------------ cli
def rows_cli():
    def quiet(*argv):
        """Run the CLI without its report landing in the middle of this board."""
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = pulse_main(list(argv))
        return rc, buf.getvalue()

    def unbound_plan_refuses_to_serve():
        rc, out = quiet("--plan", str(PLAN_PATH))
        return rc == 2 and "UNBOUND_PLAN" in out

    def execute_is_refused():
        try:
            quiet("--plan", str(PLAN_PATH), "--execute")
        except PulseError as e:
            return e.kind == "REFUSED_PROPOSAL_ONLY"
        return False

    def bound_plan_runs_dry():
        import tempfile
        live = synthetic_registry(26)
        rows = synthetic_bindings(live)
        rows.append({"clock": "pulse.selftest.planted_red", "disposition": "pulse.inproc",
                     "period_s": 15, "deadline_s": 60, "planted_red": True})
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False,
                                         encoding="utf-8") as fh:
            json.dump(plan_with(rows), fh)
            path = fh.name
        rc, out = quiet("--plan", path, "--ticks", "2")
        return rc == 0 and '"verdict": "GREEN"' in out

    check("cli: an unbound plan REFUSES to serve (an empty wheel is a silent outage)",
          unbound_plan_refuses_to_serve)
    check("cli: --execute is refused - this engine is a proposal", execute_is_refused)
    check("cli: a bound plan runs a dry tick", bound_plan_runs_dry)


# ------------------------------------------------------------------ board
def rows_planted():
    check("PLANTED FAILURE (must be RED - green here means this board is broken)",
          lambda: False)


def run_board() -> int:
    RESULTS.clear()
    rows_clock_validation()
    rows_wheel()
    rows_tick()
    rows_negative_control()
    rows_claims()
    rows_heartbeat()
    rows_bind()
    rows_manifest()
    rows_cli()
    rows_planted()

    planted = [r for r in RESULTS if r[0].startswith("PLANTED FAILURE")]
    real = [r for r in RESULTS if not r[0].startswith("PLANTED FAILURE")]
    reds = [r for r in real if not r[1]]

    print("== CLOCKS Pulse BUILD - proposal selftest ==")
    for label, ok, err in RESULTS:
        mark = "ok  " if ok else "RED "
        if label.startswith("PLANTED FAILURE"):
            mark = "RED " if not ok else "BAD "
        print(f"  {mark} {label}" + (f"  <- {err}" if err else ""))

    control_red = all(not r[1] for r in planted)
    print(f"-- {len(real) - len(reds)}/{len(real)} rows green, "
          f"negative control {'RED (good)' if control_red else 'GREEN (BOARD BROKEN)'}")
    if not control_red:
        print("VERDICT: BOARD-BROKEN - the planted failure passed; no green here means anything")
        return 1
    if reds:
        print(f"VERDICT: RED x{len(reds)}")
        return 1
    print("VERDICT: GREEN")
    return 0


def test_clocks_pulse_build_board():
    """pytest entry point: the same board, as one assertion."""
    assert run_board() == 0


if __name__ == "__main__":
    sys.exit(run_board())
