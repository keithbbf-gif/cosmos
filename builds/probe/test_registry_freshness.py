#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regression selftest for F-25 - the registry PROJECTION must apply a freshness
filter, not just `route()`.

THE DEFECT, measured on the live tree 2026-08-31 before this test existed:

    live/registry/rails.json  measured_at 1788160741
      claude-cli   verified True   age_s 318547.6   model haiku      <-- 3.69 DAYS

`Registry.route()` carries the STAGE-7 H-05 fix ("a link probed live ONCE was
dispatch-eligible forever") and drops any measurement older than max_age_s.
`Registry.live_nodes()` - the function `file_runtime()` projects to disk, and the
one `cosmos_rails_prober` and `Kernel` read - carries no such filter and hard-codes
`"verified": True`. The same scar, one function over.

WHY THIS IS THE FAILURE CLASS THE CANON NAMES: nothing in the tree contradicts the
row. A consumer reading the projection sees `verified: True` and has no reason to
look at `age_s`; the projection reports a capability the mesh has not demonstrated
since Wednesday. That is coverage claimed over a hole - the F-44 shape, in the
registry instead of the backup.

HOW TO RUN
    # against the PROPOSED module - expect PASS
    py -3.14 builds/probe/test_registry_freshness.py \
        --impl builds/probe/proposed/cosmos_registry.py

    # against the LIVE module - expect FAIL (this is the proof the test bites)
    py -3.14 builds/probe/test_registry_freshness.py --impl-live

`--impl` binds the module under test into `sys.modules["cosmos_registry"]` BEFORE
anything imports it, so the same checks run against either implementation without
touching sys.path order (`tests/*.py` insert `cosmos/` at position 0, which no
PYTHONPATH can outrank).

The pytest entry point runs against the PROPOSED file, because that is the artifact
this shift is asking COW to dispose of; it is not a claim about `cosmos/`. The live
module's failure is reproduced by the `--impl-live` verb above and recorded in
`docs/REGISTRY_FRESHNESS_FINDING.md`.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
LIVE_IMPL = REPO / "cosmos" / "cosmos_registry.py"
PROPOSED_IMPL = REPO / "builds" / "probe" / "proposed" / "cosmos_registry.py"

TTL = 3600.0
RESULTS: list[tuple[str, bool, str]] = []


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                            # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def _bind(impl: Path):
    """Load `impl` as the module named cosmos_registry, ahead of any import."""
    sys.path.insert(0, str(REPO / "cosmos"))          # for its own imports
    spec = importlib.util.spec_from_file_location("cosmos_registry", impl)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["cosmos_registry"] = mod
    spec.loader.exec_module(mod)
    return mod


class _Clock:
    """Mutable clock. The LEDGER stamps last_probe with real time, so the only way
    to age a proof without sleeping is to move the registry's own clock forward."""

    def __init__(self, base):
        self.t = float(base)

    def __call__(self):
        return self.t


def _pong(model="grok-4.6"):
    return lambda: {"ok": True, "rc": 0, "body": "PONG", "model": model,
                    "text": "PONG"}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--impl", default=None,
                    help="path to the cosmos_registry.py under test")
    ap.add_argument("--impl-live", action="store_true",
                    help="shorthand for --impl cosmos/cosmos_registry.py")
    a = ap.parse_args(argv)
    impl = LIVE_IMPL if a.impl_live else Path(a.impl or PROPOSED_IMPL)
    impl = impl if impl.is_absolute() else (REPO / impl)
    if not impl.exists():
        print(f"REFUSED: no such implementation: {impl}")
        return 2

    reg_mod = _bind(impl)
    from cosmos_ledger import Ledger                                  # noqa: E402
    Registry = reg_mod.Registry

    print(f"IMPL {impl}")
    RESULTS.clear()

    with tempfile.TemporaryDirectory() as tds:
        td = Path(tds)
        import time as _t
        clk = _Clock(_t.time())
        # ONE clock for the ledger AND the registry. The ledger stamps
        # `last_probe`; the registry computes `age_s` against its own clock. Two
        # clocks means age is meaningless, so they share this one.
        reg = Registry(Ledger(td / "r.jsonl", b"k", "core", clock=clk),
                       clock=clk)

        # Two nodes, both PROVEN LIVE right now. Nothing here is stale yet.
        reg.prove("sgh-api", "API", "core", "models", _pong("grok-4.6"))
        reg.prove("claude-cli", "CLI", "core", "code", _pong("haiku"))
        check("both nodes are live the moment they are proven",
              lambda: set(reg.live_nodes()) == {"sgh-api", "claude-cli"})
        check("a fresh proof is dispatch-eligible on route()",
              lambda: len(reg.route("core", "code")) == 1)

        # Age ONE of them past the TTL. This is exactly what happened on the live
        # tree: sgh/gem/oa are re-probed hourly, claude-cli is not probeable
        # (no key) so its last real proof kept getting projected as verified.
        clk.t += TTL + 1000.0

        check("STALE row is NOT in live_nodes() "
              "[live code FAILS here: it has no freshness filter]",
              lambda: "claude-cli" not in reg.live_nodes())
        check("no row in live_nodes() carries verified=True on a stale proof",
              lambda: all(r.get("age_s") is not None and r["age_s"] <= TTL
                          for r in reg.live_nodes().values()
                          if r.get("verified") is True))
        check("route() and live_nodes() agree - the contradiction that opened "
              "the hole is closed",
              lambda: (len(reg.route("core", "code")) == 0)
              == ("claude-cli" not in reg.live_nodes()))
        check("the OTHER node is still stale too (clock moved for both) - "
              "measured-empty, not selectively empty",
              lambda: reg.live_nodes() == {})

        # Re-prove one: freshness is recoverable, not a tombstone.
        reg.prove("sgh-api", "API", "core", "models", _pong("grok-4.6"))
        check("a re-proven node returns to live_nodes()",
              lambda: "sgh-api" in reg.live_nodes())
        check("the un-reproven node stays out",
              lambda: "claude-cli" not in reg.live_nodes())

        # The escape hatch route() already documents must exist here too.
        check("max_age_s=None disables the filter (parity with route())",
              lambda: set(reg.live_nodes(max_age_s=None))
              == {"sgh-api", "claude-cli"})

        # A drop must not be SILENT. The projection has to say what it dropped.
        dest = td / "registry"
        body = reg.file_runtime(dest)
        disk = json.loads((dest / "rails.json").read_text(encoding="utf-8"))
        check("file_runtime inherits the filter (count excludes the stale row)",
              lambda: body["count"] == 1 and body["nodes"] == ["sgh-api"])
        check("nodes.json and rails.json are the same projection",
              lambda: disk == body
              and json.loads((dest / "nodes.json").read_text(
                  encoding="utf-8")) == body)
        check("the dropped row is NAMED, not silently vanished "
              "[live code FAILS here: no such key]",
              lambda: [r["link_id"] for r in disk.get("stale") or []]
              == ["claude-cli"])
        check("the named stale row carries its age and is NOT verified",
              lambda: disk["stale"][0]["age_s"] > TTL
              and disk["stale"][0].get("verified") is False)
        check("the projection declares the TTL it applied "
              "[live code FAILS here: no such key]",
              lambda: disk.get("proof_ttl_s") == TTL)

        # Never-probed and failed rows must still be absent for the OLD reasons -
        # the new filter must not become the only gate.
        reg.register("ghost", "API", "core", "models")
        check("a registered-but-never-probed link is still absent "
              "(registration is not capability)",
              lambda: "ghost" not in reg.live_nodes()
              and "ghost" in reg.state())
        reg.prove("dead-api", "API", "core", "models",
                  lambda: {"ok": False, "rc": 2, "body": "", "model": ""})
        check("a link that did not answer is still absent",
              lambda: "dead-api" not in reg.live_nodes())
        reg.prove("nomodel", "API", "core", "models",
                  lambda: {"ok": True, "rc": 0, "body": "PONG", "model": ""})
        check("a proof with no model that answered is still absent",
              lambda: "nomodel" not in reg.live_nodes())

        # ONE TTL for the whole mesh. The registry and the prober do not import
        # each other (layering), so nothing but this check keeps them equal - and
        # a projection TTL shorter than the re-probe cadence would flap every row
        # between every probe.
        check("registry PROOF_TTL_S == cosmos_rails_prober.NODE_PROOF_TTL_S "
              "[live code FAILS here: no such constant]",
              lambda: float(reg_mod.PROOF_TTL_S) == float(
                  __import__("cosmos_rails_prober").NODE_PROOF_TTL_S))
        check("route()'s default IS that constant, not a second literal",
              lambda: __import__("inspect").signature(
                  Registry.route).parameters["max_age_s"].default
              == reg_mod.PROOF_TTL_S)

        # NEGATIVE CONTROL: a test that cannot fail is not a test.
        clk.t += TTL + 1.0
        check("NEGATIVE CONTROL - with everything aged out, live_nodes() is "
              "empty and the harness would notice a filter that did nothing",
              lambda: reg.live_nodes() == {}
              and set(reg.live_nodes(max_age_s=None)) == {"sgh-api",
                                                          "claude-cli"})

    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for label, ok, err in RESULTS:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (F-25 registry projection freshness)"
          % ("PASS" if not bad else "FAIL", len(RESULTS)))
    print("live_value " + json.dumps({
        "impl": str(impl),
        "checks": len(RESULTS),
        "failed": [l for l, _ in bad],
        "ttl_s": TTL,
    }))
    return 0 if not bad else 1


def test_registry_freshness():
    """Gate entry - binds the PROPOSED module (see the module docstring)."""
    assert main(["--impl", str(PROPOSED_IMPL)]) == 0


if __name__ == "__main__":
    sys.exit(main())
