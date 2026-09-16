#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The Sessions verb set, and its bind status per verb.

The suite lives in `builds/session-tools/` and is not moved: this app is the
surface, the suite is the engine. A verb is **BOUND** here only when this app
runs it end-to-end and returns the suite's own `cosmos-session-tools-result/1`
gate. Everything else is **DECLARED** and refuses with VERB_NOT_BOUND — a route
is not a proof, and a verb that reports OK without a gate is the fake-DONE class.

This slice binds `scan`.
"""
from __future__ import annotations

import sys
from pathlib import Path

from sessions_refusals import SessionsAppRefusal

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
SUITE = REPO / "builds" / "session-tools"

VERB_SCHEMA = "sessions-app-verb/1"
RESULT_SCHEMA = "cosmos-session-tools-result/1"

# name -> (status, what it does, what proves it)
VERBS = {
    "scan":      ("BOUND",    "discover stores without writing",
                  "family rows with a path + count, legal counted"),
    "load":      ("DECLARED", "read one session into a typed record",
                  "schema + turn count + source sha"),
    "convert":   ("DECLARED", "family store -> canonical cosmos-transcript/1",
                  "byte-identical round-trip, spans_ok"),
    "migrate":   ("DECLARED", "canonical -> OpenWork session",
                  "ses_* id + row counts from the live db"),
    "diff":      ("DECLARED", "two transcripts / two catalogs",
                  "sha pair + turn delta"),
    "check":     ("DECLARED", "integrity: SEED mac, sqlite, missing parts, sit",
                  "typed REFUSE vs VERIFIED"),
    "anonymize": ("DECLARED", "redact secrets/PII into a derived export",
                  "redaction count, original sha unchanged"),
    "strip":     ("DECLARED", "drop non-transcript payload from an export",
                  "not implemented anywhere yet - no gate to claim"),
}
BOUND = tuple(n for n, (s, _d, _g) in VERBS.items() if s == "BOUND")


def registry() -> dict:
    """What the shell renders. Status is per verb; never one green banner."""
    return {
        "schema": "sessions-app-verbs/1",
        "engine": str(SUITE.relative_to(REPO)).replace("\\", "/"),
        "canonical": "cosmos-transcript/1 JSONL + {id}.ctr.decl.json (sha-only)",
        "n_verbs": len(VERBS),
        "n_bound": len(BOUND),
        "verbs": [
            {"verb": n, "status": s, "does": d, "gate": g,
             "cli": f"py -3.14 builds/session-tools/session_tools.py {n} ..."}
            for n, (s, d, g) in VERBS.items()
        ],
    }


def _suite():
    """Import the suite with its own directory on sys.path. It owns the bare
    names `verbs`/`schema`/`refusals`; this app deliberately owns none of them,
    so nothing here shadows the engine."""
    for p in (str(SUITE), str(REPO / "cosmos")):
        if p not in sys.path:
            sys.path.insert(0, p)
    if not SUITE.is_dir():
        raise SessionsAppRefusal("ENGINE_MISSING", str(SUITE))
    import session_tools  # noqa: PLC0415
    return session_tools


def run(verb: str, *, store: Path | None = None, families: list[str] | None = None,
        root: str | None = None) -> dict:
    status = VERBS.get(verb, (None, "", ""))[0]
    if status is None:
        raise SessionsAppRefusal("UNKNOWN_VERB", verb)
    if status != "BOUND":
        raise SessionsAppRefusal("VERB_NOT_BOUND", f"{verb} is {status} in this slice")
    if store is None:
        raise SessionsAppRefusal("NO_STORE", f"{verb} needs a declared --store")
    st = _suite()
    from refusals import SessionToolsRefusal  # noqa: PLC0415
    try:
        rec = st.cmd_scan(list(families or st.DEFAULT_FAMS), Path(store), root)
    except SessionToolsRefusal as e:
        # the suite's kind is the product; do not re-label it
        raise SessionsAppRefusal(e.kind, str(e)) from e
    return {
        "schema": VERB_SCHEMA,
        "verb": verb,
        "status": status,
        "kind": rec.get("kind"),
        "store": str(store),
        "upstream_schema": rec.get("schema"),
        "legal_omitted": rec.get("legal_omitted"),
        "gate": rec.get("gate"),
    }
