#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_contracts.py -- machine-checked subsystem contracts.

PHASE 1, docs/CORE_RESTRUCTURE.md. `cosmos_principles.toml` + --audit already
proves this pattern works for P1-P10; it just never covered subsystem contracts,
so a docstring could contradict two tests indefinitely.

That is not hypothetical. On 2026-08-30 `register_node_rails`' docstring claimed
unreachable rails ARE registered so "absence must be visible", while
`tests/test_boot_attach.py` and `Registry.file_runtime` both encode the opposite.
An auditor read the prose, changed the call site to match it, and regressed a
passing suite. In a system that treats prose as specification, a stale sentence
is a live defect -- so it gets a gate like any other.

A contract is a statement plus EVIDENCE: files that must (or must not) contain a
marker. Evidence spans code, tests and prose deliberately, because drift is
precisely the case where they stop agreeing.

Typed refusals only. rc=0 is not the proof -- the emitted result is.

Run:
  py -3.14 cosmos\\cosmos_contracts.py --audit --root V:\\A\\Ai\\COSMOS
  py -3.14 cosmos\\cosmos_contracts.py --selftest
"""
from __future__ import annotations

import argparse
import json
import sys
import tomllib
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "cosmos-contract-audit/1"
CONTRACTS_DIR = "docs/contracts"


class ContractError(RuntimeError):
    """kind in {NO_CONTRACTS, BAD_CONTRACT, NO_ROOT}."""

    def __init__(self, kind: str, detail: str = "") -> None:
        self.kind = kind
        super().__init__(f"[{kind}] {detail}" if detail else f"[{kind}]")


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_contracts(root: Path) -> list[dict]:
    """Every contract across every subsystem file. A malformed file is a typed
    refusal, never a silent skip -- an unreadable contract must not look like a
    satisfied one."""
    d = root / CONTRACTS_DIR
    if not d.is_dir():
        raise ContractError("NO_CONTRACTS", str(d))
    out = []
    for p in sorted(d.glob("*.toml")):
        try:
            body = tomllib.loads(p.read_text(encoding="utf-8"))
        except (OSError, tomllib.TOMLDecodeError) as e:
            raise ContractError("BAD_CONTRACT", f"{p}: {e}") from e
        subsystem = body.get("subsystem") or p.stem
        for c in body.get("contract") or []:
            c = dict(c)
            c["subsystem"] = subsystem
            c["source"] = str(p)
            out.append(c)
    return out


def check_evidence(root: Path, ev: dict) -> dict:
    """One evidence item. A missing FILE is a failure, not an excuse."""
    rel = ev.get("file") or ""
    p = root / rel
    rec = {"kind": ev.get("kind"), "file": rel, "why": ev.get("why")}
    try:
        text = p.read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        rec.update({"ok": False, "detail": "FILE_MISSING"})
        return rec
    except OSError as e:
        rec.update({"ok": False, "detail": f"UNREADABLE: {e}"})
        return rec

    need = ev.get("must_contain")
    forbid = ev.get("must_not_contain")
    if need is not None:
        ok = need in text
        rec.update({"ok": ok, "detail": ("found" if ok else "MISSING_MARKER"),
                    "marker": need})
        return rec
    if forbid is not None:
        ok = forbid not in text
        rec.update({"ok": ok,
                    "detail": ("absent" if ok else "FORBIDDEN_MARKER_PRESENT"),
                    "marker": forbid})
        return rec
    rec.update({"ok": False, "detail": "NO_ASSERTION: evidence states nothing"})
    return rec


def audit(root: Path) -> dict:
    root = Path(root)
    contracts = load_contracts(root)
    rows = []
    for c in contracts:
        evs = [check_evidence(root, e) for e in (c.get("evidence") or [])]
        broken = [e for e in evs if not e["ok"]]
        rows.append({
            "id": c.get("id"),
            "subsystem": c.get("subsystem"),
            "severity": c.get("severity", "medium"),
            "ok": not broken,
            "statement": " ".join((c.get("statement") or "").split()),
            "evidence": evs,
            "broken_count": len(broken),
            "source": c.get("source"),
        })
    failed = [r for r in rows if not r["ok"]]
    return {
        "schema": SCHEMA,
        "ts": _now(),
        "root": str(root),
        "contracts": len(rows),
        "verified": len(rows) - len(failed),
        "contradictions": len(failed),
        "ok": not failed,
        "rows": rows,
        "_readme": ("A contradiction means code, tests and prose disagree about "
                    "the same promise. Fix the disagreement -- do not delete the "
                    "contract to make this green."),
    }


def selftest() -> int:
    """Bind the claim to an emitted value: the auditor must be able to DETECT a
    contradiction, not merely always pass. A checker that cannot fail is not a
    checker."""
    import tempfile

    results = []

    def check(label, fn):
        try:
            results.append((label, bool(fn()), ""))
        except Exception as e:                                        # noqa: BLE001
            results.append((label, False, f"{type(e).__name__}: {e}"))

    td = Path(tempfile.mkdtemp(prefix="cosmos_contracts_"))
    (td / CONTRACTS_DIR).mkdir(parents=True)
    (td / "mod").mkdir()
    (td / "mod" / "good.py").write_text("# marker: PRESENT\n", encoding="utf-8")
    (td / "mod" / "stale.py").write_text("# absence must be visible\n",
                                         encoding="utf-8")
    (td / CONTRACTS_DIR / "t.toml").write_text(
        'schema = "cosmos-contracts/1"\n'
        'subsystem = "t"\n'
        '[[contract]]\n'
        'id = "t.holds"\n'
        'statement = "a satisfied contract"\n'
        '[[contract.evidence]]\n'
        'kind = "code"\n'
        'file = "mod/good.py"\n'
        'must_contain = "marker: PRESENT"\n'
        '[[contract]]\n'
        'id = "t.contradicted"\n'
        'statement = "a contract the prose contradicts"\n'
        '[[contract.evidence]]\n'
        'kind = "prose"\n'
        'file = "mod/stale.py"\n'
        'must_not_contain = "absence must be visible"\n'
        '[[contract]]\n'
        'id = "t.missing_file"\n'
        'statement = "evidence pointing at a file that is gone"\n'
        '[[contract.evidence]]\n'
        'kind = "code"\n'
        'file = "mod/gone.py"\n'
        'must_contain = "anything"\n',
        encoding="utf-8")

    rec = audit(td)
    by = {r["id"]: r for r in rec["rows"]}
    check("loads contracts from docs/contracts", lambda: rec["contracts"] == 3)
    check("a satisfied contract verifies", lambda: by["t.holds"]["ok"] is True)
    check("DETECTS a prose contradiction",
          lambda: by["t.contradicted"]["ok"] is False)
    check("names the forbidden marker it found",
          lambda: by["t.contradicted"]["evidence"][0]["detail"]
          == "FORBIDDEN_MARKER_PRESENT")
    check("a missing evidence file is a FAILURE, not a skip",
          lambda: by["t.missing_file"]["ok"] is False
          and by["t.missing_file"]["evidence"][0]["detail"] == "FILE_MISSING")
    check("overall ok is false when any contract is contradicted",
          lambda: rec["ok"] is False and rec["contradictions"] == 2)
    check("verified count excludes the contradicted ones",
          lambda: rec["verified"] == 1)

    def _no_contracts():
        try:
            audit(td / "nope")
            return False
        except ContractError as e:
            return e.kind == "NO_CONTRACTS"
    check("a missing contracts dir is a TYPED refusal", _no_contracts)

    for label, ok, err in results:
        print(f"  {'OK  ' if ok else 'FAIL'}  {label}{('  ' + err) if err else ''}")
    bad = [r for r in results if not r[1]]
    print("live_value: " + json.dumps(
        {"contracts": rec["contracts"], "verified": rec["verified"],
         "contradictions": rec["contradictions"],
         "detected": sorted(r["id"] for r in rec["rows"] if not r["ok"])},
        sort_keys=True))
    print(f"result: {'ok' if not bad else 'FAIL'}  "
          f"{len(results) - len(bad)}/{len(results)}")
    return 1 if bad else 0


def main() -> int:
    ap = argparse.ArgumentParser(prog="cosmos_contracts")
    ap.add_argument("--root", default=None, help="repo tree (contains docs/contracts)")
    ap.add_argument("--audit", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--out", default=None, help="write the audit result here")
    a = ap.parse_args()

    if a.selftest or not (a.audit or a.root):
        return selftest()

    root = Path(a.root or Path(__file__).resolve().parent.parent)
    try:
        rec = audit(root)
    except ContractError as e:
        print(json.dumps({"schema": SCHEMA, "ok": False, "kind": e.kind,
                          "detail": str(e)}, indent=1))
        return 2
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(json.dumps(rec, indent=1), encoding="utf-8")
    for r in rec["rows"]:
        mark = "OK  " if r["ok"] else "FAIL"
        print(f"  {mark}  [{r['severity']}] {r['id']}")
        for e in r["evidence"]:
            if not e["ok"]:
                print(f"          {e['detail']}: {e['file']}"
                      + (f"  ({e['why']})" if e.get("why") else ""))
    print(f"result: {'ok' if rec['ok'] else 'FAIL'}  "
          f"{rec['verified']}/{rec['contracts']} contracts verified, "
          f"{rec['contradictions']} contradiction(s)")
    return 0 if rec["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
