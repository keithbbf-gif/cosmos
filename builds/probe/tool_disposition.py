#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""tool_disposition.py — F-41: propose the port rulings; never write the live ledger.

WHY THIS EXISTS. `cosmos_migrate` declared 143 incumbent tools and applied 8
REPLACED spikes. `cosmos_port_plan.PORT_DECISIONS` already holds 35 recorded
rulings (25 REPLACED, 10 ADAPTED). Live, 19 of those names are still
UNDECIDED and 8 are not even declared. The previous ranking of F-41 as Low/L
assumed 135 judgements still needed inventing. They do not: the first slice
is applying rulings that already exist, with successors that already exist
on disk.

WHAT THIS DOES, WITHOUT TOUCHING AUTHORITY:
  * Measures live ToolContracts via a read-only Kernel (zero writes).
  * Diffs the projection against PORT_DECISIONS.
  * Proposes APPLY only when the successor cosmos_ module is on disk
    (a successor that does not exist is SUCCESSOR_ABSENT, not a ruling).
  * apply() writes TOOL_DISPOSITION events to an INJECTED ledger only.
  * apply() against the live authority.jsonl REFUSES LIVE_LEDGER_FORBIDDEN
    and does not open the file. That is P10: agents propose, the
    Orchestrator disposes.

WHAT IT DOES NOT DO:
  * Invent a ruling for an UNPLANNED tool. HOLD is the honest default.
  * Overwrite a live disposition that disagrees with the plan (DRIFT).
  * Verify a contract (registration is not capability).
  * Read, print, or copy key material. Kernel opens install_key.bin to
    read the ledger; this tool never emits those bytes.

UNPLANNED CARDS (the remaining F-41 slice this fence can close):
  * cards_for_unplanned() writes one HOLD card per UNPLANNED name, with
    successor_candidates drawn only from cosmos_*.py files that exist
    and whose stem overlaps a name token. A candidate is EVIDENCE a
    module exists, not a ruling. disposition stays None. PORT_DECISIONS
    (cosmos/, outside this fence) is the only place a ruling is recorded.

    py -3.14 builds/probe/tool_disposition.py --root V:\A\Ai\COSMOS\live
    py -3.14 builds/probe/tool_disposition.py --root ... --write-md
    py -3.14 builds/probe/tool_disposition.py --root ... --write-cards
    py -3.14 builds/probe/tool_disposition.py --root ... --apply --ledger <scratch.jsonl>
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "cosmos"))

from cosmos_paths import CosmosPaths, CosmosPathError               # noqa: E402
from cosmos_port_plan import PORT_DECISIONS, DISPOSITIONS           # noqa: E402
from cosmos_tools import ToolContracts, ToolsError                  # noqa: E402

SCHEMA = "cosmos-tool-disposition/1"
CARD_SCHEMA = "cosmos-tool-card/1"
WORKER = "tool-disposition"
CMOD = re.compile(r"cosmos_[a-z][a-z0-9_]*")
PROPOSAL_NAME = "_f41_proposals.json"
CARDS_NAME = "_f41_unplanned_cards.json"
DOC_NAME = "TOOL_DISPOSITION.md"
# Tokens too short or too generic to be evidence of a successor.
_STOP = frozenset({"bts", "the", "a", "an", "to", "of", "and", "for", "on",
                   "in", "or", "by", "at", "is", "it", "as"})


class DispositionError(RuntimeError):
    """kind in {BAD_ROOT, LIVE_LEDGER_FORBIDDEN, NO_LEDGER, BAD_LEDGER, BAD_BUNDLE}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        self.detail = detail
        super().__init__(f"[{kind}] {detail}")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def cosmos_tokens(successor: str | None) -> list[str]:
    return CMOD.findall(successor or "")


def existing_modules(cosmos_dir: Path) -> set[str]:
    p = Path(cosmos_dir)
    if not p.is_dir():
        return set()
    return {f.stem for f in p.glob("cosmos_*.py")}


def live_authority(root: Path) -> Path:
    return CosmosPaths(root).ledger("authority.jsonl")


def guard_ledger(ledger_path: Path, live_root: Path) -> Path:
    """Refuse the live authority ledger by resolved path, before opening it."""
    target = Path(ledger_path).resolve()
    try:
        live = live_authority(live_root).resolve()
    except CosmosPathError as e:
        raise DispositionError("BAD_ROOT", str(e)) from e
    except (AttributeError, TypeError, ValueError) as e:
        # A JSON bool/array/number sentinel crashes CosmosPaths on .get
        # (bite `_bite_unpinned_round7.json`). cosmos_paths is outside this
        # fence; wrap as BAD_ROOT so F-41 never AttributeErrors.
        raise DispositionError(
            "BAD_ROOT",
            f"sentinel unreadable: {type(e).__name__}: {e}") from e
    if target == live:
        raise DispositionError(
            "LIVE_LEDGER_FORBIDDEN",
            f"{target} is the live authority ledger — agents propose, the "
            "Orchestrator disposes (P10). Pass --ledger <scratch.jsonl>.")
    if target.exists() and target.is_dir():
        raise DispositionError(
            "BAD_LEDGER",
            f"{target} is a directory, not a jsonl ledger")
    return target


def require_apply_ledger(ledger: str | None) -> Path:
    """--apply without --ledger is a typed refusal, not argparse noise."""
    if not ledger:
        raise DispositionError(
            "NO_LEDGER",
            "--apply requires --ledger <scratch.jsonl>")
    return Path(ledger)


def name_tokens(name: str) -> list[str]:
    """Tokens from an incumbent tool name, minus generic noise. Length >= 3
    so 'to'/'of' cannot match half the tree."""
    return [t for t in re.split(r"[^a-z0-9]+", (name or "").lower())
            if t and t not in _STOP and len(t) >= 3]


def successor_candidates(name: str, existing: set[str]) -> list[str]:
    """cosmos_ modules whose stem overlaps a name token. Evidence, not a ruling."""
    toks = name_tokens(name)
    if not toks:
        return []
    hits = []
    for mod in sorted(existing):
        stem = mod[7:] if mod.startswith("cosmos_") else mod
        if any(t == stem or t in stem or stem in t for t in toks):
            hits.append(mod)
    return hits


def cards_for_unplanned(bundle: dict, *, cosmos_dir: Path | None = None) -> dict:
    """One HOLD card per UNPLANNED name. Never invents a disposition."""
    existing = existing_modules(cosmos_dir or (REPO / "cosmos"))
    cards = []
    for p in bundle.get("proposals") or []:
        if p.get("kind") != "UNPLANNED":
            continue
        cards.append({
            "name": p["name"],
            "action": "HOLD",
            "kind": "UNPLANNED",
            "disposition": None,
            "plan": None,
            "successor": None,
            "successor_candidates": successor_candidates(p["name"], existing),
            "live": p.get("live") or "UNDECIDED",
            "reason": ("card review owed — no PORT_DECISIONS ruling; HOLD, "
                       "do not invent a mapping"),
        })
    return {
        "schema": CARD_SCHEMA,
        "ts": _now(),
        "worker": WORKER,
        "card_count": len(cards),
        "with_candidates": sum(1 for c in cards if c["successor_candidates"]),
        "without_candidates": sum(1 for c in cards if not c["successor_candidates"]),
        "note": ("Cards are HOLD. A candidate is evidence a cosmos_ module "
                 "exists whose name overlaps; it is NOT a ruling. "
                 "PORT_DECISIONS is the only place a ruling is recorded, "
                 "and that module is outside this fence."),
        "cards": cards,
    }


def successors_ok(decision: dict, existing: set[str]) -> tuple[bool, list[str]]:
    toks = cosmos_tokens(decision.get("successor"))
    missing = [t for t in toks if t not in existing]
    # ADAPTED + successor=None is a recorded external-helper ruling, not a claim.
    if not toks and decision.get("disposition") in DISPOSITIONS:
        return True, []
    return (not missing, missing)


def propose(rows: list[dict], *, plan: dict | None = None,
            cosmos_dir: Path | None = None) -> dict:
    """Diff a ToolContracts.report() against PORT_DECISIONS. No I/O besides glob."""
    plan = plan if plan is not None else PORT_DECISIONS
    existing = existing_modules(cosmos_dir or (REPO / "cosmos"))
    live = {r["name"]: r for r in rows}
    proposals = []

    for name, d in sorted(plan.items()):
        disp = d["disposition"]
        ok, missing = successors_ok(d, existing)
        live_row = live.get(name)
        live_disp = (live_row or {}).get("disposition")
        base = {
            "name": name,
            "plan": disp,
            "successor": d.get("successor"),
            "reason": d["reason"],
            "live": live_disp or "UNDECIDED",
            "successor_missing": missing,
        }
        if not ok:
            base.update({"action": "HOLD", "kind": "SUCCESSOR_ABSENT"})
        elif live_row is None:
            base.update({"action": "DECLARE_AND_APPLY", "kind": "DECLARE_READY"})
        elif live_disp is None:
            base.update({"action": "APPLY", "kind": "PLAN_READY"})
        elif live_disp == disp:
            base.update({"action": "SKIP", "kind": "PLAN_MATCH"})
        else:
            base.update({"action": "HOLD", "kind": "DRIFT"})
        proposals.append(base)

    planned = set(plan)
    for name in sorted(live):
        if name in planned:
            continue
        r = live[name]
        proposals.append({
            "name": name,
            "plan": None,
            "successor": None,
            "reason": "no PORT_DECISIONS card — HOLD, do not invent a ruling",
            "live": r.get("disposition") or "UNDECIDED",
            "successor_missing": [],
            "action": "HOLD",
            "kind": "UNPLANNED",
        })

    by_kind: dict[str, int] = {}
    by_action: dict[str, int] = {}
    for p in proposals:
        by_kind[p["kind"]] = by_kind.get(p["kind"], 0) + 1
        by_action[p["action"]] = by_action.get(p["action"], 0) + 1
    ready = [p["name"] for p in proposals if p["action"] in ("APPLY", "DECLARE_AND_APPLY")]
    return {
        "schema": SCHEMA,
        "ts": _now(),
        "worker": WORKER,
        "live_total": len(live),
        "plan_total": len(plan),
        "by_kind": by_kind,
        "by_action": by_action,
        "apply_ready": ready,
        "apply_ready_count": len(ready),
        "proposals": proposals,
        "note": ("APPLY/DECLARE_AND_APPLY are proposals. apply() on the live "
                 "authority ledger REFUSES LIVE_LEDGER_FORBIDDEN."),
    }


def apply_proposals(contracts: ToolContracts, bundle: dict, *,
                    ledger_path: Path, live_root: Path) -> dict:
    """Record proposed rulings on an injected ToolContracts. Never the live ledger."""
    guard_ledger(ledger_path, live_root)
    if not isinstance(bundle, dict):
        raise DispositionError(
            "BAD_BUNDLE",
            f"bundle is {type(bundle).__name__}, not an object")
    raw = bundle.get("proposals")
    if raw is None:
        raw = []
    if not isinstance(raw, list):
        raise DispositionError(
            "BAD_BUNDLE",
            f"proposals is {type(raw).__name__}, not a list")
    applied, skipped, held = [], [], []
    for p in raw:
        if not isinstance(p, dict):
            raise DispositionError(
                "BAD_BUNDLE",
                f"proposal is {type(p).__name__}, not an object")
        action = p.get("action")
        if action not in ("APPLY", "DECLARE_AND_APPLY"):
            held.append(p["name"])
            continue
        name = p["name"]
        decision = p["plan"]
        reason = p["reason"]
        try:
            # Scratch ledgers start empty: a PLAN_READY name is declared on
            # the live projection but not here. Declare-if-missing, then
            # record the ruling. DUPLICATE is the live-shaped case.
            try:
                contracts.declare(
                    name, ["run"],
                    f"incumbent {name} -> {decision}: {p.get('successor') or reason}")
            except ToolsError as e:
                if e.kind != "DUPLICATE":
                    raise
            contracts.disposition(name, decision, reason)
            applied.append(name)
        except ToolsError as e:
            skipped.append({"name": name, "kind": e.kind, "detail": str(e)})
    return {
        "schema": SCHEMA,
        "ts": _now(),
        "ok": True,
        "ledger": str(Path(ledger_path).resolve()),
        "applied": applied,
        "applied_count": len(applied),
        "held": held,
        "skipped": skipped,
    }


def measure_live(root: Path) -> tuple[list[dict], dict]:
    """Read-only Kernel + ToolContracts.report(). Zero writes."""
    from cosmos_kernel import Kernel
    k = Kernel(root, read_only=True)
    if not k.read_only:
        raise DispositionError("BAD_ROOT", "Kernel did not honor read_only=True")
    tc = ToolContracts(k.ledger)
    rows = tc.report()
    by: dict[str, int] = {}
    for r in rows:
        key = r.get("disposition") or "UNDECIDED"
        by[key] = by.get(key, 0) + 1
    return rows, {
        "total": len(rows),
        "by_disposition": by,
        "verified_true": sum(1 for r in rows if r.get("verified") is True),
        "read_only": True,
        "writes": 0,
    }


def render_md(bundle: dict, live_counts: dict | None = None) -> str:
    lines = [
        "# TOOL DISPOSITION — F-41 proposals (not applied to the live ledger)",
        "",
        f"**Generated** {bundle.get('ts')} by `{WORKER}`. This document is a "
        "rebuildable projection of `cosmos_port_plan.PORT_DECISIONS` against the "
        "live ToolContracts report. **It is not a disposition.** Applying these "
        "rulings to `live/ledger/authority.jsonl` is the Orchestrator's door.",
        "",
        "## Counts",
        "",
        f"- plan total: **{bundle.get('plan_total')}**",
        f"- live total: **{bundle.get('live_total')}**",
        f"- apply-ready: **{bundle.get('apply_ready_count')}** "
        f"(`{'`, `'.join(bundle.get('apply_ready') or []) or 'none'}`)",
        f"- by kind: `{json.dumps(bundle.get('by_kind') or {}, sort_keys=True)}`",
        f"- by action: `{json.dumps(bundle.get('by_action') or {}, sort_keys=True)}`",
    ]
    if live_counts:
        lines.append(
            f"- live projection: `{json.dumps(live_counts.get('by_disposition') or {}, sort_keys=True)}` "
            f"verified_true={live_counts.get('verified_true')}"
        )
    lines += [
        "",
        "## Ready to apply (scratch ledger only)",
        "",
        "| name | plan | successor | kind |",
        "|---|---|---|---|",
    ]
    for p in bundle.get("proposals") or []:
        if p["action"] in ("APPLY", "DECLARE_AND_APPLY"):
            lines.append(
                f"| `{p['name']}` | {p['plan']} | `{p.get('successor') or '—'}` | {p['kind']} |"
            )
    lines += [
        "",
        "## Held",
        "",
        "| name | kind | live | plan | why |",
        "|---|---|---|---|---|",
    ]
    held_n = 0
    for p in bundle.get("proposals") or []:
        if p["action"] != "HOLD":
            continue
        if p["kind"] == "UNPLANNED":
            held_n += 1
            continue  # listed as a count, not 100 rows of the same sentence
        lines.append(
            f"| `{p['name']}` | {p['kind']} | {p['live']} | {p.get('plan') or '—'} | "
            f"{(p.get('reason') or '')[:80]} |"
        )
    lines += [
        "",
        f"UNPLANNED HOLD rows (card review owed, no invented ruling): **{held_n}**.",
        "",
    ]
    cards = bundle.get("unplanned_cards") or {}
    if cards:
        lines += [
            "## UNPLANNED cards (HOLD — not a ruling)",
            "",
            f"- card count: **{cards.get('card_count')}**",
            f"- with successor_candidates (evidence only): **{cards.get('with_candidates')}**",
            f"- with no name-overlap on disk: **{cards.get('without_candidates')}**",
            "",
            "| name | live | successor_candidates |",
            "|---|---|---|",
        ]
        for c in cards.get("cards") or []:
            cands = ", ".join(f"`{x}`" for x in (c.get("successor_candidates") or [])) or "—"
            lines.append(f"| `{c['name']}` | {c.get('live') or 'UNDECIDED'} | {cands} |")
        lines += [
            "",
            cards.get("note") or "",
            "",
        ]
    lines += [
        "Apply: `py -3.14 builds/probe/tool_disposition.py --root <live> "
        "--apply --ledger <scratch.jsonl>` — LIVE_LEDGER_FORBIDDEN on authority.jsonl.",
        "",
    ]
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", required=True)
    ap.add_argument("--out", help="proposal JSON (default: builds/probe/_f41_proposals.json)")
    ap.add_argument("--write-md", action="store_true",
                    help=f"write docs/{DOC_NAME} from the proposal")
    ap.add_argument("--write-cards", action="store_true",
                    help=f"write builds/probe/{CARDS_NAME} — HOLD cards, no invented ruling")
    ap.add_argument("--apply", action="store_true",
                    help="record APPLY rows on --ledger (scratch). Refuses the live ledger.")
    ap.add_argument("--ledger", help="scratch ledger jsonl; required with --apply")
    ap.add_argument("--cosmos-dir", default=str(REPO / "cosmos"))
    a = ap.parse_args(argv)

    if a.apply:
        try:
            require_apply_ledger(a.ledger)
        except DispositionError as e:
            print(json.dumps({"refused": True, "kind": e.kind, "detail": e.detail,
                              "ledger_untouched": True}, indent=1))
            return 2

    try:
        rows, live_counts = measure_live(Path(a.root))
    except CosmosPathError as e:
        print(json.dumps({"refused": True, "kind": e.kind, "detail": str(e)}), file=sys.stderr)
        return 2
    except DispositionError as e:
        print(json.dumps({"refused": True, "kind": e.kind, "detail": e.detail}), file=sys.stderr)
        return 2

    bundle = propose(rows, cosmos_dir=Path(a.cosmos_dir))
    bundle["live_counts"] = live_counts
    bundle["root"] = str(Path(a.root))
    cards = cards_for_unplanned(bundle, cosmos_dir=Path(a.cosmos_dir))
    bundle["unplanned_cards"] = {
        "card_count": cards["card_count"],
        "with_candidates": cards["with_candidates"],
        "without_candidates": cards["without_candidates"],
        "note": cards["note"],
        "cards": cards["cards"],
    }
    out_path = Path(a.out) if a.out else HERE / PROPOSAL_NAME
    out_path.write_text(json.dumps(bundle, indent=1), encoding="utf-8")
    bundle["out"] = str(out_path)

    if a.write_cards:
        cards_path = HERE / CARDS_NAME
        cards_path.write_text(json.dumps(cards, indent=1), encoding="utf-8")
        bundle["cards_out"] = str(cards_path)

    if a.write_md:
        md_path = REPO / "docs" / DOC_NAME
        md_path.write_text(render_md(bundle, live_counts), encoding="utf-8")
        bundle["md"] = str(md_path)

    if a.apply:
        try:
            target = guard_ledger(require_apply_ledger(a.ledger), Path(a.root))
        except DispositionError as e:
            print(json.dumps({"refused": True, "kind": e.kind, "detail": e.detail,
                              "ledger_untouched": True}, indent=1))
            return 2
        from cosmos_ledger import Ledger
        # Scratch key, not the install key. The live kernel is never opened for write.
        led = Ledger(target, b"f41-scratch-not-an-install-key", "f41")
        rec = apply_proposals(ToolContracts(led), bundle,
                              ledger_path=target, live_root=Path(a.root))
        print(json.dumps(rec, indent=1))
        return 0

    print(json.dumps({
        "ok": True, "schema": SCHEMA,
        "live_total": bundle["live_total"],
        "plan_total": bundle["plan_total"],
        "by_kind": bundle["by_kind"],
        "by_action": bundle["by_action"],
        "apply_ready_count": bundle["apply_ready_count"],
        "apply_ready": bundle["apply_ready"],
        "unplanned_card_count": cards["card_count"],
        "unplanned_with_candidates": cards["with_candidates"],
        "out": str(out_path),
        "cards_out": bundle.get("cards_out"),
        "md": bundle.get("md"),
        "live_counts": live_counts,
    }, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
