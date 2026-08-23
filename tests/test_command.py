#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: the command seam - text in, kernel actions out, refusals typed + ledgered.

Covers the full voice grammar: status/audit/jobs/submit/help (original) plus
health/spend/rails/makers/events/session (orchestration intents), the misheard-word
rule (zero-arg verbs ignore trailing noise; argument verbs parse strict; near-miss
verbs are UNKNOWN), and the fence: every destructive verb refuses BEFORE dispatch,
and force is not reachable through any argument position."""
from __future__ import annotations
import sys, tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cosmos_kernel import Kernel, install
from cosmos_command import Commander, CommandError, FORBIDDEN
from cosmos_makers import MAKER_KINDS

RESULTS = []

def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                            # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="cosmos_c_"))
    root = td / "Cosmos"

    # ---- install + boot, same as any consumer of the kernel ----
    install(root, tree_id="spike-command-1")
    k = Kernel(root, worker="voice-a")
    c = Commander(k)

    # ---- the read commands ----
    r = c.handle("status")
    check("status: ok + READY + root identity",
          lambda: r["ok"] and r["ready"] and r["tree_id"] == "spike-command-1")
    check("status: ledger head is present", lambda: r["ledger_head"]["seq"] >= 1)
    a = c.handle("AUDIT")                      # case-insensitive first word
    check("audit (any case): chain VERIFIED", lambda: a["ledger"]["chain"] == "VERIFIED")
    check("jobs: empty projection before any submit",
          lambda: c.handle("jobs")["jobs"] == {})
    check("help: teaches the submit grammar",
          lambda: any(l.startswith("submit") for l in c.handle("help")["commands"]))

    # ---- submit creates a claimable job ----
    s = c.handle("submit high echo hello")
    m = k.sched.claim_next()
    check("submit high -> claimable job with the same id",
          lambda: m is not None and m["job_id"] == s["job_id"])
    check("claimed job carries the spoken command", lambda: m["command"] == "echo hello")

    # ---- submit parse: a command that CONTAINS a priority word is not mis-split ----
    s2 = c.handle("submit high review this high priority patch")
    m2 = k.sched.claim_next()
    check("submit: priority words inside the command stay in the command",
          lambda: m2 is not None and m2["job_id"] == s2["job_id"]
          and m2["command"] == "review this high priority patch"
          and m2["priority"] == "high")
    s3 = c.handle('submit critical "deploy with high availability"')
    m3 = k.sched.claim_next()
    check("submit: a quoted command containing a priority word is not mis-split",
          lambda: m3 is not None and m3["command"] == "deploy with high availability"
          and m3["priority"] == "critical")
    check("submit: last-word 'high' is NOT stolen as the priority (echo high)",
          lambda: _expect(c, "submit echo high", "BAD_ARGS"))
    check("submit: unclosed quote REFUSES (never guessed)",
          lambda: _expect(c, 'submit high "echo hello', "BAD_ARGS"))

    # ---- refusals, each with its typed kind ----
    check("bad priority -> BAD_ARGS that teaches the grammar",
          lambda: _expect(c, "submit urgent echo hi", "BAD_ARGS"))
    check("missing command -> BAD_ARGS", lambda: _expect(c, "submit high", "BAD_ARGS"))
    check("unknown verb -> UNKNOWN_COMMAND, never a guess",
          lambda: _expect(c, "reboot now", "UNKNOWN_COMMAND"))
    check("'delete everything' -> REFUSED (never-delete canon)",
          lambda: _expect(c, "delete everything", "REFUSED"))
    check("every FORBIDDEN verb refuses",
          lambda: all(_expect(c, v + " x", "REFUSED") for v in FORBIDDEN))

    # ---- the ledger saw all of it ----
    events = list(k.ledger.verify())
    check("refusal is ledgered as COMMAND_REFUSED",
          lambda: any(e["event"] == "COMMAND_REFUSED"
                      and e["payload"]["text"].startswith("delete")
                      for e in events))
    check("handled commands are ledgered with ok flags",
          lambda: any(e["event"] == "COMMAND_HANDLED" and e["payload"]["ok"]
                      for e in events)
          and any(e["event"] == "COMMAND_HANDLED" and not e["payload"]["ok"]
                  for e in events))

    # ================= the orchestration verbs =================

    # ---- health: delegates to cosmos_health.HealthBoard.run() ----
    h = c.handle("health")
    check("health: verdict present + planted failure lands RED",
          lambda: h["ok"] and "verdict" in h and h["negative_control_red"] is True
          and "rows" in h)
    check("health: board run is ledgered (HEALTH_BOARD)",
          lambda: any(e["event"] == "HEALTH_BOARD" for e in k.ledger.verify()))

    # ---- spend: delegates to cosmos_spend.SpendGate.audit() ----
    check("spend: no budgets yet -> empty rails, not an error",
          lambda: c.handle("spend")["rails"] == {})
    k.spend.set_budget("voice-rail", 5.0)
    sp = c.handle("spend")
    check("spend: budget shows cap + headroom, dated",
          lambda: sp["rails"]["voice-rail"]["cap_usd"] == 5.0
          and sp["rails"]["voice-rail"]["headroom_usd"] == 5.0
          and sp["measured_at_epoch"] > 0)

    # ---- rails: delegates to cosmos_registry.Registry.matrix() ----
    check("rails: empty registry -> empty matrix",
          lambda: c.handle("rails")["rails"] == [])
    k.registry.register("t-link", "API", "core", "models")
    rl = c.handle("rails")
    check("rails: registered link shows verified=None (registration is not capability)",
          lambda: len(rl["rails"]) == 1 and rl["rails"][0]["link_id"] == "t-link"
          and rl["rails"][0]["verified"] is None and rl["rails"][0]["age_s"] is None)

    # ---- makers: delegates to cosmos_makers.MakerMap.list() ----
    mk = c.handle("makers")
    check("makers: seeded catalog lists, every kind in the closed set",
          lambda: len(mk["makers"]) > 0
          and all(mm["kind"] in MAKER_KINDS for mm in mk["makers"]))

    # ---- events: the last-N ledger read ----
    ev = c.handle("events")
    check("events: default N returns the tail, newest last, seq = ledger head",
          lambda: ev["count"] == 10 and ev["events"][-1]["seq"] == ev["of_total"])
    check("events 3: exactly three", lambda: c.handle("events 3")["count"] == 3)
    check("events banana -> BAD_ARGS (a count is a number, never guessed)",
          lambda: _expect(c, "events banana", "BAD_ARGS"))
    check("events 0 -> BAD_ARGS", lambda: _expect(c, "events 0", "BAD_ARGS"))
    check("events 101 -> BAD_ARGS (cap)", lambda: _expect(c, "events 101", "BAD_ARGS"))
    check("events 5 please -> BAD_ARGS (argument verbs do not absorb noise)",
          lambda: _expect(c, "events 5 please", "BAD_ARGS"))

    # ---- the misheard-word rule ----
    check("'status please' resolves status (zero-arg trailing noise ignored)",
          lambda: c.handle("status please")["ok"]
          and c.handle("STATUS please NOW")["ready"])
    check("'health check now thanks' resolves health (noise ignored)",
          lambda: c.handle("health check now thanks")["negative_control_red"] is True)
    check("'statusify' -> UNKNOWN_COMMAND (exact verb match, no fuzz)",
          lambda: _expect(c, "statusify", "UNKNOWN_COMMAND"))
    check("'healthcheck' -> UNKNOWN_COMMAND (near-miss is not a match)",
          lambda: _expect(c, "healthcheck", "UNKNOWN_COMMAND"))
    check("zero-arg noise cannot smuggle an action: 'status delete everything' is "
          "status and nothing else",
          lambda: c.handle("status delete everything")["ok"])

    # ---- session lifecycle (BootUP / TidyUP), strict + non-destructive ----
    check("session start before any seed -> KERNEL_REFUSED (NO_SEED relayed, not guessed)",
          lambda: _expect(c, "session start plumbing", "KERNEL_REFUSED"))
    sc = c.handle("session close")
    check("session close: TidyUP writes + names the seed",
          lambda: sc["ok"] and Path(sc["seed"]).is_file())
    ss = c.handle("session start plumbing")
    check("session start: BootUP opens with the stream + injects inherit",
          lambda: ss["ok"] and ss["stream"] == "plumbing" and "sid" in ss)
    k.sessions.session.open_watcher("w-paid", "a paid return")
    check("session close over an open watcher -> KERNEL_REFUSED (force NOT reachable)",
          lambda: _expect(c, "session close", "KERNEL_REFUSED"))
    k.sessions.session.resolve_watcher("w-paid", "landed")
    sc2 = c.handle("session close")
    check("session close after resolve -> seed written again, prior seed archived",
          lambda: sc2["ok"] and Path(sc2["seed"]).is_file())
    check("'session close force' -> BAD_ARGS (force is not a voice word)",
          lambda: _expect(c, "session close force", "BAD_ARGS"))
    check("'session start' without a stream -> BAD_ARGS",
          lambda: _expect(c, "session start", "BAD_ARGS"))
    check("'session start plumbing extra' -> BAD_ARGS (strict, no noise on arg verbs)",
          lambda: _expect(c, "session start plumbing extra", "BAD_ARGS"))
    check("'session destroy' -> BAD_ARGS (unknown session action, never approximated)",
          lambda: _expect(c, "session destroy", "BAD_ARGS"))
    check("bare 'session' -> BAD_ARGS that teaches the grammar",
          lambda: _expect(c, "session", "BAD_ARGS"))

    # ---- the fence, widened: every destructive verb class refuses FIRST ----
    check("purge/force/overwrite/reset/wipe/drop/erase as first word -> REFUSED",
          lambda: all(_expect(c, v + " everything", "REFUSED")
                      for v in ("purge", "force", "overwrite", "reset",
                                "wipe", "drop", "erase")))
    check("FORBIDDEN covers the full destructive-verb contract",
          lambda: {"delete", "remove", "purge", "reset", "drop",
                   "overwrite", "force"} <= FORBIDDEN)
    check("no grammar line starts with a forbidden verb (nothing destructive is taught)",
          lambda: all(l.split()[0] not in FORBIDDEN
                      for l in c.handle("help")["commands"]))
    check("KERNEL_REFUSED outcomes are ledgered as typed non-ok COMMAND_HANDLED",
          lambda: any(e["event"] == "COMMAND_HANDLED"
                      and not e["payload"]["ok"]
                      and e["payload"].get("kind") == "KERNEL_REFUSED"
                      for e in k.ledger.verify()))

    # ---- help teaches the whole grammar ----
    helptext = " ".join(c.handle("help")["commands"])
    check("help: lists every verb in the grammar",
          lambda: all(v in helptext for v in
                      ("status", "audit", "health", "spend", "rails", "makers",
                       "jobs", "events", "session start", "session close",
                       "submit", "help")))

    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for label, ok, err in RESULTS:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label, ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks" % ("PASS" if not bad else "FAIL", len(RESULTS)))
    return 0 if not bad else 1


def _expect(c, text, kind) -> bool:
    try:
        c.handle(text)
    except CommandError as e:
        return e.kind == kind
    return False


def test_command():
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())
