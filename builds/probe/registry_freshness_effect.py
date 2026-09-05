#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""What the F-25 fix does to THIS tree - measured on a faithful replica.

A regression test proves the fix is correct. It does not tell COW what will
change on the live tree the moment the proposal is applied, and "apply it and
find out" is not an acceptable answer for a running mesh (keep-her-afloat).

So: read the CURRENT `live/registry/rails.json`, rebuild an equivalent ledger in
a temp dir with each node's real measured age preserved, and run BOTH the live
and the proposed `Registry` against it. The diff between the two projections is
the diff Keith will see.

READ-ONLY with respect to the live tree. It reads two files under `live/` -
`registry/rails.json` and, through `cosmos_paths`, the existence (never the
contents) of the two claude-credential filenames. It never opens the authority
ledger, never reads key material, and writes only under `builds/probe/`.

    py -3.14 builds/probe/registry_freshness_effect.py
    py -3.14 builds/probe/registry_freshness_effect.py --root V:/A/Ai/COSMOS/live
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
OUT = REPO / "builds" / "probe" / "_registry_freshness_effect.json"
IMPLS = {
    "live": REPO / "cosmos" / "cosmos_registry.py",
    "proposed": REPO / "builds" / "probe" / "proposed" / "cosmos_registry.py",
}


class _Clock:
    def __init__(self, base):
        self.t = float(base)

    def __call__(self):
        return self.t


def _load(name: str):
    """Fresh module object per implementation - they share a module NAME, so
    they cannot both live in sys.modules at once."""
    impl = IMPLS[name]
    spec = importlib.util.spec_from_file_location(f"cosmos_registry__{name}",
                                                  impl)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _replica(reg_mod, rows: list[dict], now: float, td: Path, tag: str):
    """Rebuild `rows` as ledger events whose ages match the live projection."""
    from cosmos_ledger import Ledger
    clk = _Clock(now)
    led = Ledger(td / f"{tag}.jsonl", b"replica-key-not-authority", "core",
                 clock=clk)
    reg = reg_mod.Registry(led, clock=clk)
    for r in sorted(rows, key=lambda r: -(r.get("age_s") or 0)):
        clk.t = now - float(r.get("age_s") or 0)
        reg.register(r["link_id"], r["rail_type"], r["src"], r["dst"],
                     policy_rank=r.get("policy_rank", 0))
        led.append("PROBE_RESULT", {
            "link_id": r["link_id"], "ok": True, "detail": "replica",
            "model": r.get("model"), "rc": r.get("rc"),
            "body_bytes": r.get("body_bytes")})
    clk.t = now
    return reg


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(REPO / "live"))
    a = ap.parse_args(argv)
    sys.path.insert(0, str(REPO / "cosmos"))

    src = Path(a.root) / "registry" / "rails.json"
    if not src.exists():
        print(f"REFUSED: no live projection at {src}")
        return 2
    live_proj = json.loads(src.read_text(encoding="utf-8"))
    rows = live_proj.get("matrix") or []
    now = float(live_proj.get("measured_at") or 0.0)

    result = {
        "source": str(src),
        "source_measured_at": now,
        "source_count": live_proj.get("count"),
        "source_rows": [{"link_id": r["link_id"], "verified": r.get("verified"),
                         "age_s": r.get("age_s"), "model": r.get("model")}
                        for r in rows],
        "impls": {},
    }

    with tempfile.TemporaryDirectory() as tds:
        td = Path(tds)
        for name in ("live", "proposed"):
            mod = _load(name)
            reg = _replica(mod, rows, now, td, name)
            body = reg.file_runtime(td / name)
            result["impls"][name] = {
                "impl": str(IMPLS[name]),
                "count": body["count"],
                "nodes": body["nodes"],
                "proof_ttl_s": body.get("proof_ttl_s"),
                "stale": [{"link_id": s["link_id"], "age_s": round(s["age_s"], 1),
                           "verified": s.get("verified")}
                          for s in (body.get("stale") or [])],
                "verified_true_over_ttl": [
                    {"link_id": r["link_id"], "age_s": round(r["age_s"], 1)}
                    for r in body["matrix"]
                    if r.get("verified") is True
                    and (r.get("age_s") or 0) > mod.__dict__.get(
                        "PROOF_TTL_S", 3600.0)],
            }
            # The downstream half: what the PROBER does with each verdict. It
            # asks live_nodes() first, so the projection decides the label.
            try:
                from cosmos_paths import CosmosPaths
                import cosmos_rails_prober as prober
                paths = CosmosPaths(a.root)
                labels = {}
                for spec in prober.WIRED_NODES:
                    should = prober._should_live_probe(
                        paths, reg, spec, live=False,
                        ttl_s=prober.NODE_PROOF_TTL_S)
                    if should:
                        labels[spec["link_id"]] = "WOULD_PROBE_LIVE"
                    else:
                        row = reg.live_nodes().get(spec["link_id"])
                        labels[spec["link_id"]] = (
                            "skipped=fresh" if row else
                            "skipped=no-hands-configured")
                result["impls"][name]["prober_labels"] = labels
            except Exception as e:                                # noqa: BLE001
                result["impls"][name]["prober_labels"] = {
                    "UNMEASURED": f"{type(e).__name__}: {e}"}

    lv, pr = result["impls"]["live"], result["impls"]["proposed"]
    result["delta"] = {
        "nodes_live_only": sorted(set(lv["nodes"]) - set(pr["nodes"])),
        "count": [lv["count"], pr["count"]],
        "stale_rows_named_by_proposed": [s["link_id"] for s in pr["stale"]],
        "false_verified_removed": [r["link_id"]
                                   for r in lv["verified_true_over_ttl"]],
        "prober_label_changes": {
            k: [lv.get("prober_labels", {}).get(k),
                pr.get("prober_labels", {}).get(k)]
            for k in set(lv.get("prober_labels", {}))
            | set(pr.get("prober_labels", {}))
            if lv.get("prober_labels", {}).get(k)
            != pr.get("prober_labels", {}).get(k)},
    }

    OUT.write_text(json.dumps(result, indent=1), encoding="utf-8")
    print(json.dumps(result, indent=1))
    print(f"\nwrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
