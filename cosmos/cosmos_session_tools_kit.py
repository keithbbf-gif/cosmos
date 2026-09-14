#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_session_tools_kit — Core POST/GET bridge to session-tools verbs.

POST body must name the verb and every path/id the suite requires — missing
fields refuse BAD_INPUT before the suite runs (no fake OK).

    py -3.14 cosmos\\\\cosmos_session_tools_kit.py --selftest
"""
from __future__ import annotations

import sys
from pathlib import Path

SCHEMA = "cosmos-session-tools-kit/1"
REPO = Path(__file__).resolve().parent.parent
SUITE = REPO / "builds" / "session-tools"

# Verbs implemented in the suite (strip is not — honest UNBOUND at the app layer).
BOUND = frozenset({
    "scan", "load", "convert", "migrate", "diff", "check", "anonymize",
})


class SessionToolsKitError(RuntimeError):
    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def _suite():
    for p in (str(SUITE), str(REPO / "cosmos")):
        if p not in sys.path:
            sys.path.insert(0, p)
    import session_tools  # noqa: PLC0415
    return session_tools


def _require_path(value, name: str) -> Path:
    if value is None or value == "":
        raise SessionToolsKitError("BAD_INPUT", f"{name} is required")
    return Path(str(value))


def _require_str(value, name: str) -> str:
    if not value or not str(value).strip():
        raise SessionToolsKitError("BAD_INPUT", f"{name} is required")
    return str(value).strip()


def snapshot(paths) -> dict:
    """GET — verb bind counts; never mutates."""
    return {
        "schema": SCHEMA,
        "tree_id": paths.sentinel.tree_id,
        "kind": "OK",
        "engine": "builds/session-tools",
        "n_verbs": 8,
        "n_bound": len(BOUND),
        "bound": sorted(BOUND),
        "declared": ["strip"],
    }


def _path(raw) -> Path | None:
    if raw is None or raw == "":
        return None
    return Path(str(raw))


def run(body: dict, paths=None) -> dict:  # noqa: ARG001
    if not isinstance(body, dict):
        raise SessionToolsKitError("BAD_INPUT", "body must be a JSON object")
    verb = body.get("verb")
    if not verb or not str(verb).strip():
        raise SessionToolsKitError("BAD_INPUT", "verb is required")
    verb = str(verb).strip()
    if verb not in BOUND:
        if verb == "strip":
            raise SessionToolsKitError("VERB_NOT_BOUND", f"{verb} is DECLARED")
        raise SessionToolsKitError("UNKNOWN_VERB", verb)

    from refusals import SessionToolsRefusal  # noqa: PLC0415

    st = _suite()
    fams = body.get("families") or body.get("family")
    if isinstance(fams, str):
        fams = [fams]
    try:
        if verb == "scan":
            store = _path(body.get("store"))
            root = body.get("root")
            if store is None and root is None:
                raise SessionToolsKitError("BAD_INPUT", "scan needs store or root")
            rec = st.cmd_scan(list(fams or st.DEFAULT_FAMS), store, root)
        elif verb == "load":
            rec = st.cmd_load(
                _require_str(body.get("id") or body.get("rec_id"), "id"),
                _require_path(body.get("store"), "store"),
                _path(body.get("out_dir")),
            )
        elif verb == "convert":
            rec = st.cmd_convert(
                _require_str(body.get("id") or body.get("rec_id"), "id"),
                _require_path(body.get("store"), "store"),
                _require_path(body.get("out_dir"), "out_dir"),
                bool(body.get("force")),
            )
        elif verb == "diff":
            rec = st.cmd_diff(
                _require_path(body.get("left"), "left"),
                _require_path(body.get("right"), "right"),
            )
        elif verb == "check":
            rec = st.cmd_check(
                _require_str(body.get("what"), "what"),
                _require_path(body.get("path"), "path"),
                body.get("chair") or body.get("sit"),
            )
        elif verb == "anonymize":
            rec = st.cmd_anonymize(
                _require_str(body.get("id") or body.get("rec_id"), "id"),
                _require_path(body.get("store"), "store"),
                _require_path(body.get("out_dir"), "out_dir"),
            )
        elif verb == "migrate":
            rec = st.cmd_migrate(
                _require_str(body.get("id") or body.get("rec_id"), "id"),
                _require_path(body.get("store"), "store"),
                _require_str(body.get("workspace_id"), "workspace_id"),
                _require_path(body.get("directory"), "directory"),
                _path(body.get("out")),
                bool(body.get("dry_run")),
            )
        else:
            raise SessionToolsKitError("UNKNOWN_VERB", verb)
    except SessionToolsRefusal as e:
        raise SessionToolsKitError(e.kind, str(e)) from e
    rec["schema"] = SCHEMA
    rec["kit_verb"] = verb
    return rec


def _selftest() -> int:
    sys.path.insert(0, str(REPO / "cosmos"))
    from cosmos_kernel import install
    from cosmos_paths import CosmosPaths

    results = []

    def check(label, fn):
        try:
            results.append((label, bool(fn()), ""))
        except Exception as e:  # noqa: BLE001
            results.append((label, False, f"{type(e).__name__}: {e}"))

    import tempfile

    td = REPO / "tests" / "fixtures" / "session_tools"
    paths = CosmosPaths(
        install(Path(tempfile.mkdtemp(prefix="st_kit_")) / "live", tree_id="st-kit"))
    snap = snapshot(paths)
    check("snapshot lists 7 bound", lambda: snap["n_bound"] == 7)

    try:
        run({"verb": "load"}, paths=paths)
    except SessionToolsKitError as e:
        bad = e.kind == "BAD_INPUT"
    else:
        bad = False
    check("load without store/id is BAD_INPUT", lambda: bad)

    rec = run({"verb": "check", "what": "catalog", "path": str(td)}, paths=paths)
    check("check catalog via kit", lambda: rec.get("kind") == "VERIFIED")

    bad = [(l, e) for l, ok, e in results if not ok]
    for label, ok, err in results:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (session tools kit)"
          % ("PASS" if not bad else "FAIL", len(results)))
    return 0 if not bad else 1


if __name__ == "__main__":
    raise SystemExit(_selftest())
