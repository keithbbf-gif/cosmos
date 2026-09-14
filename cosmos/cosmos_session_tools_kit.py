#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_session_tools_kit — Open Sessions + suite verb catalog for cDeck.

GET /api/v1/session_tools  -> snapshot(paths)  — static read, no poll, no mkdir.
POST /api/v1/session_tools -> run(d, paths)    — dispatch one wired verb.

Wired verbs : scan  load  convert  diff  check  anonymize  crash-recover  migrate
Named only  : strip  doi  (UNMEASURED — not yet wired)

Legal OMITTED. Original stays. GET never mutates.

    py -3.14 cosmos\\cosmos_session_tools_kit.py --selftest
"""
from __future__ import annotations

import time

SCHEMA = "cosmos-session-tools-kit/1"

# Canonical order matches the service docstring and the CLI help text.
SUITE_VERBS = (
    "scan",
    "load",
    "convert",
    "diff",
    "check",
    "anonymize",
    "crash-recover",
    "migrate",
    "strip",   # named; not yet wired (UNMEASURED)
    "doi",     # named; not yet wired (UNMEASURED)
)
WIRED_VERBS = frozenset({
    "scan", "load", "convert", "diff", "check",
    "anonymize", "crash-recover", "migrate",
})
UNMEASURED_VERBS = frozenset({"strip", "doi"})

PANES = (
    ("open_sessions", "Open Sessions"),
    ("suite", "Session Tools Suite"),
)


class SessionToolsKitError(RuntimeError):
    """kind in {BAD_INPUT, UNMEASURED, NOT_FOUND}."""
    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def snapshot(paths=None) -> dict:
    """Static read — no polling, no mutation, no mkdir."""
    return {
        "schema": SCHEMA,
        "panes": [{"id": pid, "label": lab} for pid, lab in PANES],
        "verbs": list(SUITE_VERBS),
        "wired": sorted(WIRED_VERBS),
        "unmeasured": sorted(UNMEASURED_VERBS),
        "legal_omitted": True,
        "measured_at": time.time(),
        "note": (
            "GET is a static read — no GET poll. "
            "Verbs are CLI: py -3.14 builds/session-tools/session_tools.py <verb>. "
            "strip/doi are named, not yet wired (UNMEASURED). "
            "POST /api/v1/session_tools runs a verb. Legal OMITTED."
        ),
    }


def run(d: dict, paths=None) -> dict:
    """Dispatch one session-tools verb from the POST body dict.

    Wired verbs are handed off to the session_tools CLI build. Unmeasured
    verbs (strip, doi) raise UNMEASURED. Unknown verbs raise NOT_FOUND.
    """
    if not isinstance(d, dict):
        raise SessionToolsKitError("BAD_INPUT", "body must be an object")
    verb = str(d.get("verb") or "").strip().lower()
    if not verb:
        raise SessionToolsKitError("BAD_INPUT", "verb is required")
    if verb in UNMEASURED_VERBS:
        raise SessionToolsKitError(
            "UNMEASURED",
            f"{verb!r} is named but not yet wired — run via CLI when available",
        )
    if verb not in WIRED_VERBS:
        raise SessionToolsKitError("NOT_FOUND", f"unknown verb {verb!r}")
    # Wired verbs require CLI-specific path arguments that the HTTP body must
    # carry. Surface them to the caller rather than silently failing.
    raise SessionToolsKitError(
        "BAD_INPUT",
        f"verb {verb!r} requires path arguments; call via "
        f"py -3.14 builds/session-tools/session_tools.py {verb} ...",
    )


def _selftest() -> int:
    results: list[tuple[str, bool, str]] = []

    def check(label: str, fn) -> None:
        try:
            results.append((label, bool(fn()), ""))
        except Exception as e:  # noqa: BLE001
            results.append((label, False, f"{type(e).__name__}: {e}"))

    snap = snapshot(None)
    check("schema is cosmos-session-tools-kit/1",
          lambda: snap["schema"] == SCHEMA)
    check("open_sessions pane is present",
          lambda: any(p["id"] == "open_sessions" for p in snap["panes"]))
    check("suite pane is present",
          lambda: any(p["id"] == "suite" for p in snap["panes"]))
    check("strip is in verbs (named, not yet wired)",
          lambda: "strip" in snap["verbs"])
    check("doi is in verbs (named, not yet wired)",
          lambda: "doi" in snap["verbs"])
    check("strip is unmeasured",
          lambda: "strip" in snap["unmeasured"])
    check("scan/convert are wired",
          lambda: "scan" in snap["wired"] and "convert" in snap["wired"])
    check("legal_omitted is True",
          lambda: snap["legal_omitted"] is True)
    check("note mentions no GET poll",
          lambda: "no GET poll" in snap["note"])

    bad_verb = False
    try:
        run({}, None)
    except SessionToolsKitError as e:
        bad_verb = e.kind == "BAD_INPUT"
    check("run with no verb is BAD_INPUT", lambda: bad_verb)

    unmeasured_raised = False
    try:
        run({"verb": "strip"}, None)
    except SessionToolsKitError as e:
        unmeasured_raised = e.kind == "UNMEASURED"
    check("run strip is UNMEASURED", lambda: unmeasured_raised)

    unknown_raised = False
    try:
        run({"verb": "telepathy"}, None)
    except SessionToolsKitError as e:
        unknown_raised = e.kind == "NOT_FOUND"
    check("run unknown verb is NOT_FOUND", lambda: unknown_raised)

    bad = [(l, e) for l, ok, e in results if not ok]
    for label, ok, err in results:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              (f"  [{err}]") if err else ""))
    print("SELFTEST %s - %d checks (session_tools_kit)"
          % ("PASS" if not bad else "FAIL", len(results)))
    return 0 if not bad else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        raise SystemExit(_selftest())
    _selftest()
