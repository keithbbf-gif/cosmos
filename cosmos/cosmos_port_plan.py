#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_port_plan - THE COSMOS PORT PLAN (F5 builder). For every incumbent BTS
tool, a RECORDED disposition decision and its COSMOS successor (or the reason it is
ADAPTED / ABANDONED). This is the decision record the Migrator's UNDECIDED gaps
resolve into: cosmos_migrate DECLARES the backlog and marks it UNDECIDED; this module
carries the actual rulings, keyed by incumbent tool name.

architecture wins where a contract conflicts; every decision recorded, never drifted.

The four dispositions are cosmos_tools' own (PRESERVED / ADAPTED / REPLACED /
ABANDONED). A fifth sentinel, UNDECIDED, is NOT a disposition - it is the absence of
one, the same gap cosmos_migrate counts. A tool marked UNDECIDED here is declared but
gets NO disposition event: nothing was decided, so nothing is ledgered as decided, and
the reason names the debt ("card review owed"). Inventing a mapping to avoid an
UNDECIDED would be exactly the drift this module exists to prevent.

REPLACED entries name an existing cosmos_ module - a successor that does not exist is
a claim, not a port. ADAPTED entries either name the COSMOS surface the tool now plugs
into (cosmos_rails for the API rails, cosmos_surfaces for the SMART probe,
cosmos_context for the carry-over docs) or carry successor=None when the tool survives
as an external helper the OS calls but does not absorb (the elevated-ops worker).
"""
from __future__ import annotations

from cosmos_tools import DISPOSITIONS, ToolsError

# UNDECIDED is the decision GAP, not a fifth decision. Kept distinct from the four so a
# declared-but-unruled tool is counted, never silently defaulted into a real disposition.
UNDECIDED = "UNDECIDED"
VALID_DISPOSITIONS = set(DISPOSITIONS) | {UNDECIDED}

# incumbent tool name -> {disposition, successor (str|None), reason}
# successor names the COSMOS module(s) that now hold the contract. Non-cosmos tokens
# (e.g. "kdash") are descriptive; only cosmos_ tokens are validated to exist.
PORT_DECISIONS: dict[str, dict] = {
    # ---- core OS primitives: the spikes already replaced these ----
    "bts_paths": {
        "disposition": "REPLACED", "successor": "cosmos_paths",
        "reason": "spike successor cosmos_paths: resolve-or-raise, one configured root, "
                  "explicit boot instantiation, import-time side effects dropped"},
    "tree_lock": {
        "disposition": "REPLACED", "successor": "cosmos_lock",
        "reason": "spike successor cosmos_lock: advisory cooperative lock cannot be "
                  "ported - leases + fencing tokens + fenced commit replace it"},
    "bts_phone": {
        "disposition": "REPLACED", "successor": "cosmos_mail",
        "reason": "spike successor cosmos_mail: probe-not-assume kept, dead != no-news, "
                  "adds send + per-worker identity + staleness policy"},
    "bts_runner": {
        "disposition": "REPLACED", "successor": "cosmos_sched + cosmos_runner",
        "reason": "queue tick splits: cosmos_sched owns concurrency/priority/registry, "
                  "cosmos_runner keeps claim-by-rename, worded outcomes, log-first, "
                  "report-never-retry, append-only ledger"},

    # ---- health, service, dashboard ----
    "bts_health": {
        "disposition": "REPLACED", "successor": "cosmos_health",
        "reason": "cosmos_health on kernel selftests with positive AND negative "
                  "controls - a health row that could never go red is the scar it closes"},
    "bts_kdash_feed": {
        "disposition": "REPLACED", "successor": "cosmos_service + kdash",
        "reason": "KDash becomes an API projection client of cosmos_service /api/v1; "
                  "no file-reading dashboard, so writer-splits-from-launcher cannot recur"},
    "bts_serve": {
        "disposition": "REPLACED", "successor": "cosmos_service",
        "reason": "static file serving folds into cosmos_service, the single API surface"},

    # ---- schedule / task registry ----
    "task_registry": {
        "disposition": "REPLACED", "successor": "cosmos_sched",
        "reason": "scheduled-task registry role absorbed by cosmos_sched: zero red, "
                  "machine count == registry count, no drive literals or relative paths"},

    # ---- rails matrix / registry ----
    "rail_check": {
        "disposition": "REPLACED", "successor": "cosmos_registry + cosmos_rails",
        "reason": "rails matrix becomes measured registry probes: cosmos_registry holds "
                  "the entries, cosmos_rails probes them - no new .bat"},

    # ---- backup ----
    "backup_to_onedrive": {
        "disposition": "REPLACED", "successor": "cosmos_backup + cosmos_surfaces",
        "reason": "backup is policy+verification+evidence in cosmos_backup with the "
                  "OneDrive destination probed as a cosmos_surfaces surface (hash "
                  "compare, off-machine, scope by irreplaceability)"},
    "backup_watchdog": {
        "disposition": "REPLACED", "successor": "cosmos_backup + cosmos_surfaces",
        "reason": "a watchdog that never executed is not a backup; cosmos_backup carries "
                  "the scheduled verification, cosmos_surfaces the reachability probe"},

    # ---- validation / pointer integrity ----
    "verify_pointers": {
        "disposition": "REPLACED", "successor": "cosmos_validate",
        "reason": "pointer integrity becomes a cosmos_validate gate; a point-in-time "
                  "green run is replaced by content-hash notarization (TOCTOU closed)"},
    "verify_conf": {
        "disposition": "REPLACED", "successor": "cosmos_validate",
        "reason": "every control file must parse AND validate - cosmos_validate enforces "
                  "both, refusing to close on a file that only parses"},

    # ---- fan-out / crucible ----
    "mesh_fanout": {
        "disposition": "REPLACED", "successor": "cosmos_crucible",
        "reason": "vendor-plural fan-out becomes cosmos_crucible; single-family agreement "
                  "proves nothing, so the crucible requires disagreeing families by design"},

    # ---- legacy bus / node / monitors: absorbed by the OS primitives ----
    "bts_bus": {
        "disposition": "REPLACED", "successor": "cosmos_mail + cosmos_sched + cosmos_health",
        "reason": "message bus role is IPC (cosmos_mail) + scheduling (cosmos_sched) + "
                  "liveness (cosmos_health); no standalone bus survives"},
    "bts_node": {
        "disposition": "REPLACED", "successor": "cosmos_mail + cosmos_sched + cosmos_health",
        "reason": "node loop decomposes into the same three OS primitives"},
    "bts_dymon": {
        "disposition": "REPLACED", "successor": "cosmos_mail + cosmos_sched + cosmos_health",
        "reason": "the dynamic monitor becomes health checks on a schedule with mail "
                  "notification - cosmos_health + cosmos_sched + cosmos_mail"},
    "bts_watchdog": {
        "disposition": "REPLACED", "successor": "cosmos_mail + cosmos_sched + cosmos_health",
        "reason": "watchdog is a scheduled health probe that mails on failure - the same "
                  "three primitives, no bespoke daemon"},
    "bts_poller": {
        "disposition": "REPLACED", "successor": "cosmos_mail + cosmos_sched + cosmos_health",
        "reason": "polling becomes scheduled probes (cosmos_sched) reporting to "
                  "cosmos_health and mailing via cosmos_mail"},

    # ---- identity ----
    "bts_identity": {
        "disposition": "REPLACED", "successor": "cosmos_identity",
        "reason": "MESH_ID + PEERS move to cosmos_identity; federation blockers tracked "
                  "as a function return, not a remembered count"},

    # ---- spend / cost / policy ----
    "bts_spend": {
        "disposition": "REPLACED", "successor": "cosmos_spend",
        "reason": "spend ledger centralizes in cosmos_spend: append-only, per-rail "
                  "ceilings, breaker-in-the-caller"},
    "bts_cop": {
        "disposition": "REPLACED", "successor": "cosmos_spend",
        "reason": "cost projection folds into cosmos_spend; thinking billed at output "
                  "rate is priced there, not re-derived per rail"},
    "bts_policy": {
        "disposition": "REPLACED", "successor": "cosmos_spend",
        "reason": "the speed<->cost knob and DOM-vs-API routing live with the ledger in "
                  "cosmos_spend that enforces them"},

    # ================= ADAPTED - contract kept, home moved =================
    "bts_elevated_ops": {
        "disposition": "ADAPTED", "successor": None,
        "reason": "COSMOS uses the same elevated queue; the privileged worker survives as "
                  "an EXTERNAL helper the OS dispatches to (one UAC click), not a module "
                  "it absorbs - the credential boundary stays outside Core"},
    "bts_drive_health": {
        "disposition": "ADAPTED", "successor": "cosmos_surfaces",
        "reason": "the SMART probe attaches as a cosmos_surfaces surface probe: report "
                  "reachability + uncorrected reads, evacuate not monitor for an opaque "
                  "USB-bridged single copy"},
    "tools_sync": {
        "disposition": "ADAPTED", "successor": "cosmos_context",
        "reason": "the tools index flows through cosmos_context + ledger; keep the "
                  "check-then-write doc renderer, OWNER names the live index path first"},
    "corrections": {
        "disposition": "ADAPTED", "successor": "cosmos_context",
        "reason": "carry-over corrections flow through cosmos_context + ledger (count-"
                  "weighted, printed at boot); keep the doc renderer, validate on close"},
    "scars": {
        "disposition": "ADAPTED", "successor": "cosmos_context",
        "reason": "scars-as-query moves to cosmos_context + ledger, the evidence "
                  "primitive; keep the doc renderer, replace the silent --selftest no-op"},
    "bts_sgh": {
        "disposition": "ADAPTED", "successor": "cosmos_rails",
        "reason": "becomes a cosmos_rails ApiRail adapter (SuperGrok link driver): "
                  "metered rail, not the floor; DOM-first, spend-gated"},
    "bts_gem": {
        "disposition": "ADAPTED", "successor": "cosmos_rails",
        "reason": "cosmos_rails ApiRail adapter for the Vertex/GEM link; keep-separate "
                  "from the Studio wrapper, Never Activate boundary preserved"},
    "bts_gw": {
        "disposition": "ADAPTED", "successor": "cosmos_rails",
        "reason": "cosmos_rails ApiRail adapter sharing the SGH ceiling; unpriced != $0 "
                  "is enforced by the spend gate, not the driver"},
    "bts_oa_api": {
        "disposition": "ADAPTED", "successor": "cosmos_rails",
        "reason": "cosmos_rails ApiRail adapter (OpenAI link); the two-ledger / two-"
                  "ceiling split rides on cosmos_spend, breaker in the caller"},
    "bts_cursor": {
        "disposition": "ADAPTED", "successor": "cosmos_rails",
        "reason": "cosmos_rails ApiRail adapter (Cursor link driver), dispatchable from a "
                  "queue lane; key stays in .secrets, never the repo"},

    # ---- C.O.S. session lifecycle (TidyUP / BootUP) ----
    "tidyup": {
        "disposition": "REPLACED", "successor": "cosmos_session",
        "reason": "TidyUP/T2 is close_session: validate every control file parses, "
                  "refresh the index, write a next-session SEED of inherited facts + "
                  "open watchers + handoff via cosmos_context.Session/boot_inherit"},
    "bootup": {
        "disposition": "REPLACED", "successor": "cosmos_session",
        "reason": "BootUP is start_session: read the prior SEED, inject facts and "
                  "watchers, open a new cosmos_context.Session, return inherited context"},
}


def apply(contracts) -> dict:
    """Declare each incumbent and record its disposition against the ToolContracts
    registry. Idempotent: a re-declare raises DUPLICATE (the registry's drift guard) and
    is skipped; re-recording an identical disposition appends an event whose projection
    is the same state, so the ruling does not drift on replay. UNDECIDED tools are
    declared but get NO disposition event - the gap is counted, never defaulted."""
    for name, d in PORT_DECISIONS.items():
        behavior = "incumbent %s -> %s: %s" % (
            name, d["disposition"], (d.get("successor") or d["reason"]))
        try:
            contracts.declare(name, ["run"], behavior)
        except ToolsError as e:
            if e.kind != "DUPLICATE":
                raise
        disp = d["disposition"]
        if disp in DISPOSITIONS:  # one of the four; UNDECIDED is a gap, not a decision
            contracts.disposition(name, disp, d["reason"])
    return summary()


def summary() -> dict:
    """Counts by disposition + the list of UNDECIDED (the debt still owed). Counted from
    the plan, never quoted from memory."""
    by: dict[str, int] = {}
    undecided: list[str] = []
    for name, d in PORT_DECISIONS.items():
        disp = d["disposition"]
        by[disp] = by.get(disp, 0) + 1
        if disp == UNDECIDED:
            undecided.append(name)
    return {"total": len(PORT_DECISIONS), "by_disposition": by,
            "undecided": sorted(undecided),
            "note": "architecture wins where a contract conflicts; every decision "
                    "recorded, never drifted"}
