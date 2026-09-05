#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Suite wrapper for cosmos_rail_base, plus the migration invariant.

Phase 3.1: four rails carried a byte-identical `_ledger_is_authority`, and the
process helpers `_real_run` / `_real_which` / `write_probe_record` lived inside
the CODEX vendor rail, which four unrelated modules imported as if it were a
library. They now live in cosmos_rail_base.

Two properties are pinned here, and they are different:

  1. NO FORK -- no rail module may hold a helper object that is not the base's.
     A local copy re-appearing (or a re-export silently forking) is the failure
     this file exists to catch, and it catches it for every rail, not just the
     ones listed in (2).
  2. ON THE SEAM -- the rails that genuinely use a helper must actually expose
     it, so the invariant cannot be satisfied by deleting the import.

`_real_run` / `_real_which` are required of the rails that shell out (codex,
claude, forge) and NOT of cursor / firecrawl / playwright, which are HTTP and DOM
rails that never spawn a child. Importing a process helper into a rail that
cannot use it would be dead weight, and net complexity is supposed to trend
down. `_ledger_is_authority` and `write_probe_record` are required of all five.

Catch-compatibility is pinned too: `CodexRailError` must remain a subclass of
the base `RailError`, because the moved `_real_run` raises the base type while
the `except CodexRailError` sites in the codex rail expect the narrow one.
(Measured 2026-08-31 by cosmos_refusals: 12 `except CodexRailError` handlers
across cosmos/, 9 of them in the codex rail, against 19 raise sites. The "~40"
this docstring used to claim was the raise count of the whole rail family, not
the catch count -- the same prose-as-specification slip Phase 1 exists to
catch, corrected here rather than left standing.)

PHASE 5 VERDICT -- the two RailErrors STAY SEPARATE (2026-08-31, surveyed by
cosmos/cosmos_refusals.py). The last check below used to be labelled "Phase 5
open". Phase 5 has now run, and its answer is NO MERGE:

  1. Nothing is gained. Phase 5 asks that a caller be able to branch on `kind`
     without knowing which module raised. The two classes' kind sets are already
     DISJOINT -- {NO_KEY, BAD_SPEC, BAD_ROOT, UNREACHABLE, BROKE, REFUSED} vs
     {NO_LIVE_LINK, RAIL_FAILED, NOT_PERMITTED} -- so that property HOLDS today
     without merging. cosmos_refusals pins the disjointness, so if a future edit
     makes the sets overlap this argument dies loudly instead of quietly.
  2. The blast radius cannot be bounded statically. Aliasing the two would
     widen SEVEN existing handlers -- codex_rail:1063/1135/1493,
     claude_rail:880/1114, cursor_rail:806/1018 -- each catching the
     Dispatcher's `RailError` around a `disp.dispatch(...)` call. Four are the
     operator CLI verbs (`launch_run` / `vet_run`, reached by `--launch` /
     `--vet`); three are selftests. None is in a resident daemon -- the workers
     and cosmos_service call `adapter.dispatch` directly inside
     `spend.guarded_call` and never construct a Dispatcher, and while
     `cosmos_kernel._disp()` builds one, nothing under `serve` calls it. So the
     exposure is operator-facing rather than fleet-facing, which lowers the
     stakes but does not change the answer. For an
     unmetered adapter, cosmos_rails.py:126 calls `adapter.dispatch(payload)`
     outside any handler, so whatever the adapter raises reaches those seven.
     Merged, they would ALSO swallow every `cosmos_rail_base.RailError`
     subclass -- `CodexRailError` (19 raise sites) and the bare `RailError` that
     `_real_run` raises -- converting a propagating refusal into a soft
     `{"ok": False}` record. Whether a given one of those is reachable through a
     particular adapter is a whole-path question a survey cannot settle:
     `CodexRail.coder` catches its own refusals at 615/620 but then calls
     `_argv` (which raises) unguarded at 624. Unbounded risk for the zero gain
     in (1) is not a trade worth making on a running fleet.
  3. The real defect is the opposite one. The survey found ONE concept wearing
     THREE kind strings -- DENIED / NOT_PERMITTED / REFUSED -- with
     cosmos_rails.py:124 relabelling a SpendError("DENIED") as
     RailError("NOT_PERMITTED") as it crosses the seam. Merging two classes
     whose kinds do not collide would not have touched it.

So this check is no longer a placeholder for pending work; it is a pin on a
decision. Merging remains possible later, but it is now a change that has to
argue with the reasons above, which is what a deliberate act looks like.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "cosmos"))

import cosmos_rail_base as base  # noqa: E402
from cosmos_rail_base import selftest  # noqa: E402

MISSING = object()

# helper -> the rails REQUIRED to expose it (see the module docstring).
SHELLS_OUT = ("codex", "claude", "forge")
ALL_RAILS = ("codex", "cursor", "firecrawl", "playwright", "claude", "forge")
REQUIRED = {
    "_ledger_is_authority": ALL_RAILS,
    "write_probe_record": ALL_RAILS,
    "_real_run": SHELLS_OUT,
    "_real_which": SHELLS_OUT,
}


def main() -> int:
    rc = selftest()
    if rc != 0:
        return rc

    import cosmos_claude_rail as claude
    import cosmos_codex_rail as codex
    import cosmos_cursor_rail as cursor
    import cosmos_firecrawl_rail as firecrawl
    import cosmos_forge_rail as forge
    import cosmos_playwright_rail as playwright

    rails = {"codex": codex, "cursor": cursor, "firecrawl": firecrawl,
             "playwright": playwright, "claude": claude, "forge": forge}

    results = []
    forked = []
    absent = []

    for helper, required in REQUIRED.items():
        canonical = getattr(base, helper)
        for name, mod in rails.items():
            got = getattr(mod, helper, MISSING)
            if got is MISSING:
                ok = name not in required
                if not ok:
                    absent.append(f"{name}.{helper}")
            else:
                ok = got is canonical
                if not ok:
                    forked.append(f"{name}.{helper}")
            results.append((f"{name} rail: {helper} is the base object"
                            if got is not MISSING else
                            f"{name} rail: {helper} absent (does not shell out)",
                            ok))

    # The catch-compatibility claim, as a test rather than as an assurance:
    # _real_run now raises the BASE RailError, so every `except CodexRailError`
    # must still see a type that covers what the codex rail itself raises.
    results.append((
        "CodexRailError is a subclass of the base RailError",
        issubclass(codex.CodexRailError, base.RailError)))
    results.append((
        "CodexRailError keeps the (kind, detail) refusal shape",
        _refusal_shape(codex.CodexRailError)))
    results.append((
        "an `except CodexRailError` still catches a codex refusal",
        _caught(codex.CodexRailError,
                lambda: codex.merge_spec({"schema": "wrong"}))))
    results.append((
        "an `except RailError` catches that same codex refusal too",
        _caught(base.RailError,
                lambda: codex.merge_spec({"schema": "wrong"}))))
    # cosmos_rails.RailError is a DIFFERENT, older Dispatcher class. Phase 5 ran
    # on 2026-08-31 and decided AGAINST merging them -- the reasoning is in the
    # module docstring above. This pin therefore records a decision, not a
    # pending task: they stay separate, and a merge must argue with the docstring
    # before it edits this line.
    import cosmos_rails  # noqa: E402
    results.append((
        "the Dispatcher's RailError stays a distinct class (Phase 5: NO MERGE)",
        cosmos_rails.RailError is not base.RailError))

    for label, ok in results:
        print(f"  {'OK  ' if ok else 'FAIL'}  {label}")
    bad = [r for r in results if not r[1]]
    print("live_value: " + repr({
        "rails": len(rails),
        "helpers": sorted(REQUIRED),
        "forked": forked,
        "absent_but_required": absent,
        "base_module": base.__file__,
    }))
    print(f"result: {'ok' if not bad else 'FAIL'}  "
          f"{len(results) - len(bad)}/{len(results)} on the shared rail seam")
    return 1 if bad else 0


def _refusal_shape(cls) -> bool:
    e = cls("REFUSED", "detail here")
    return (e.kind == "REFUSED" and e.detail == "detail here"
            and str(e) == "[REFUSED] detail here")


def _caught(catch_cls, fn) -> bool:
    try:
        fn()
    except catch_cls:
        return True
    except Exception:                                                # noqa: BLE001
        return False
    return False


if __name__ == "__main__":
    raise SystemExit(main())
