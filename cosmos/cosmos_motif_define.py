#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""P01 MOTIF DEFINE-first — frozen PROBLEM STATEMENT / STATED GOAL before BUILD/CRITICS.

On-disk pack key remains ``define``. Display name is PROBLEM STATEMENT / STATED GOAL.
Studio pack (``state/studio/pack.json``) is checked first, then the profile engine.
Does not start Gitur, does not invent traces, does not mix cDeck repos.

    py -3.14 cosmos\\cosmos_motif_define.py --selftest
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cosmos_profiles import MOTIF_STAGES  # noqa: E402

SCHEMA = "cosmos-motif-define/1"
RUN_STAGES = frozenset({"build", "critics"})
MOTIF_STEP_1 = "PROBLEM STATEMENT / STATED GOAL"


class MotifDefineError(RuntimeError):
    """kind in {REFUSED, BAD_STAGE}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def stage_graph() -> list[dict]:
    """Reuse the occupancy 9-stage MOTIF skin (studio / profiles)."""
    return [dict(s) for s in MOTIF_STAGES]


def frozen_statement(paths, *, profile: str = "forge") -> dict:
    """Load the frozen statement from studio, then profile engine."""
    text = ""
    saved_at = None
    source = None
    try:
        from cosmos_studio import load_pack

        pack = load_pack(paths)
        d = pack.get("define") if isinstance(pack.get("define"), dict) else {}
        text = str(d.get("text") or "").strip()
        saved_at = d.get("saved_at")
        if text:
            source = "studio"
    except Exception:  # noqa: BLE001
        pass
    if not text:
        from cosmos_profiles import load_engine

        eng = load_engine(paths, profile)
        d = eng.get("define") if isinstance(eng.get("define"), dict) else {}
        text = str(d.get("text") or "").strip()
        saved_at = d.get("saved_at")
        if text:
            source = "profile"
    return {"text": text, "saved_at": saved_at, "source": source}


def require_frozen_statement(stage: str, statement: dict) -> None:
    """BUILD and CRITICS refuse when the frozen statement is empty."""
    sid = str(stage or "").strip().lower()
    if sid not in RUN_STAGES:
        return
    if not str((statement or {}).get("text") or "").strip():
        raise MotifDefineError(
            "REFUSED",
            f"{MOTIF_STEP_1} empty — {sid.upper()} does not start",
        )


def assert_run_stage(stage: str) -> str:
    sid = str(stage or "").strip().lower()
    if sid not in RUN_STAGES:
        raise MotifDefineError("BAD_STAGE", f"unknown MOTIF run stage {stage!r}")
    return sid


def _selftest() -> int:
    import tempfile

    from cosmos_kernel import install
    from cosmos_paths import CosmosPaths
    from cosmos_profiles import save_engine
    from cosmos_studio import save_pack

    results = []

    def check(label, fn):
        try:
            results.append((label, bool(fn()), ""))
        except Exception as e:  # noqa: BLE001
            results.append((label, False, f"{type(e).__name__}: {e}"))

    graph = stage_graph()
    check(
        "nine-stage graph; step 1 is define / PROBLEM GOAL",
        lambda: len(graph) == 9
        and graph[0]["id"] == "define"
        and graph[0]["n"] == 1,
    )

    td = Path(tempfile.mkdtemp(prefix="cosmos_motif_define_"))
    root = install(td / "live", tree_id="spike-motif-define")
    paths = CosmosPaths(root)

    build_refused = False
    try:
        require_frozen_statement("build", frozen_statement(paths))
    except MotifDefineError as e:
        build_refused = e.kind == "REFUSED"
    check("empty statement REFUSED before BUILD", lambda: build_refused)

    critics_refused = False
    try:
        require_frozen_statement("critics", frozen_statement(paths))
    except MotifDefineError as e:
        critics_refused = e.kind == "REFUSED"
    check("empty statement REFUSED before CRITICS", lambda: critics_refused)

    save_pack(paths, {"define": {"text": "WHAT: gate. WHY: P01."}})
    stmt = frozen_statement(paths)
    check(
        "studio define wins when present",
        lambda: stmt["text"].startswith("WHAT: gate")
        and stmt["source"] == "studio",
    )
    require_frozen_statement("build", stmt)
    check("BUILD allowed when statement on disk", lambda: True)

    failed = [(l, e) for l, ok, e in results if not ok]
    for label, ok, err in results:
        print(
            "  %s  %s%s"
            % ("OK  " if ok else "FAIL", label, ("  [" + err + "]") if err else "")
        )
    print(
        "SELFTEST %s - %d checks (MOTIF DEFINE-first; BUILD/CRITICS gate)"
        % ("PASS" if not failed else "FAIL", len(results))
    )
    return 0 if not failed else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(_selftest())
    raise SystemExit(2)
