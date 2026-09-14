#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The Sessions verb set, and its bind status per verb.

The suite lives in `builds/session-tools/` and is not moved: this app is the
surface, the suite is the engine. A verb is **BOUND** here only when this app
runs it end-to-end and returns the suite's own `cosmos-session-tools-result/1`
gate. Everything else is **DECLARED** and refuses with VERB_NOT_BOUND — a route
is not a proof, and a verb that reports OK without a gate is the fake-DONE class.

Bound this slice: scan, load, convert, migrate, diff, check, anonymize.
`strip` is not implemented in the suite — honest DECLARED / VERB_NOT_BOUND.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

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
    "load":      ("BOUND",    "read one session into a typed record",
                  "schema + turn count + source sha"),
    "convert":   ("BOUND",    "family store -> canonical cosmos-transcript/1",
                  "byte-identical round-trip, spans_ok"),
    "migrate":   ("BOUND",    "canonical -> OpenWork session",
                  "ses_* id + row counts from the live db"),
    "diff":      ("BOUND",    "two transcripts / two catalogs",
                  "sha pair + turn delta"),
    "check":     ("BOUND",    "integrity: SEED mac, sqlite, missing parts, sit",
                  "typed REFUSE vs VERIFIED"),
    "anonymize": ("BOUND",    "redact secrets/PII into a derived export",
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


def _require_path(value: Path | None, name: str) -> Path:
    if value is None:
        raise SessionsAppRefusal("BAD_INPUT", f"{name} is required")
    return Path(value)


def _require_str(value: str | None, name: str) -> str:
    if not value or not str(value).strip():
        raise SessionsAppRefusal("BAD_INPUT", f"{name} is required")
    return str(value).strip()


def _envelope(verb: str, status: str, rec: dict, **extra: Any) -> dict:
    out = {
        "schema": VERB_SCHEMA,
        "verb": verb,
        "status": status,
        "kind": rec.get("kind"),
        "upstream_schema": rec.get("schema"),
        "legal_omitted": rec.get("legal_omitted", 0),
        "gate": rec.get("gate"),
    }
    out.update(extra)
    return out


def _dispatch(st, verb: str, **kw: Any) -> dict:
    from refusals import SessionToolsRefusal  # noqa: PLC0415
    try:
        if verb == "scan":
            return st.cmd_scan(
                list(kw["families"] or st.DEFAULT_FAMS),
                kw["store"],
                kw.get("root"),
            )
        if verb == "load":
            return st.cmd_load(kw["rec_id"], kw["store"], kw.get("out_dir"))
        if verb == "convert":
            return st.cmd_convert(
                kw["rec_id"], kw["store"], kw["out_dir"], bool(kw.get("force")))
        if verb == "diff":
            return st.cmd_diff(kw["left"], kw["right"])
        if verb == "check":
            return st.cmd_check(kw["check_what"], kw["check_path"], kw.get("chair"))
        if verb == "anonymize":
            return st.cmd_anonymize(kw["rec_id"], kw["store"], kw["out_dir"])
        if verb == "migrate":
            return st.cmd_migrate(
                kw["rec_id"],
                kw["store"],
                kw.get("workspace_id"),
                kw.get("directory"),
                kw.get("migrate_out"),
                bool(kw.get("dry_run")),
            )
        raise SessionsAppRefusal("UNKNOWN_VERB", verb)
    except SessionToolsRefusal as e:
        raise SessionsAppRefusal(e.kind, str(e)) from e


def run(verb: str, *, store: Path | None = None, root: str | None = None,
        families: list[str] | None = None, rec_id: str | None = None,
        out_dir: Path | None = None, force: bool = False,
        left: Path | None = None, right: Path | None = None,
        check_what: str | None = None, check_path: Path | None = None,
        chair: str | None = None, workspace_id: str | None = None,
        directory: Path | None = None, migrate_out: Path | None = None,
        dry_run: bool = False) -> dict:
    status = VERBS.get(verb, (None, "", ""))[0]
    if status is None:
        raise SessionsAppRefusal("UNKNOWN_VERB", verb)
    if status != "BOUND":
        raise SessionsAppRefusal("VERB_NOT_BOUND", f"{verb} is {status} in this slice")

    st = _suite()
    extra: dict[str, Any] = {}

    if verb == "scan":
        if store is None and root is None:
            raise SessionsAppRefusal("BAD_INPUT", "scan needs --store or --root")
        rec = _dispatch(st, verb, store=store, root=root, families=families)
        if store is not None:
            extra["store"] = str(store)
        return _envelope(verb, status, rec, **extra)

    if verb == "load":
        store = _require_path(store, "store")
        rec_id = _require_str(rec_id, "id")
        out = Path(out_dir) if out_dir else None
        rec = _dispatch(st, verb, store=store, rec_id=rec_id, out_dir=out)
        return _envelope(verb, status, rec, store=str(store), id=rec_id)

    if verb == "convert":
        store = _require_path(store, "store")
        rec_id = _require_str(rec_id, "id")
        out = _require_path(out_dir, "out_dir")
        rec = _dispatch(st, verb, store=store, rec_id=rec_id, out_dir=out, force=force)
        return _envelope(verb, status, rec, store=str(store), id=rec_id, out_dir=str(out))

    if verb == "diff":
        left_p = _require_path(left, "left")
        right_p = _require_path(right, "right")
        rec = _dispatch(st, verb, left=left_p, right=right_p)
        return _envelope(verb, status, rec, left=str(left_p), right=str(right_p))

    if verb == "check":
        what = _require_str(check_what, "what")
        path = _require_path(check_path, "path")
        rec = _dispatch(st, verb, check_what=what, check_path=path, chair=chair)
        return _envelope(verb, status, rec, what=what, path=str(path))

    if verb == "anonymize":
        store = _require_path(store, "store")
        rec_id = _require_str(rec_id, "id")
        out = _require_path(out_dir, "out_dir")
        rec = _dispatch(st, verb, store=store, rec_id=rec_id, out_dir=out)
        return _envelope(verb, status, rec, store=str(store), id=rec_id, out_dir=str(out))

    if verb == "migrate":
        store = _require_path(store, "store")
        rec_id = _require_str(rec_id, "id")
        ws = _require_str(workspace_id, "workspace_id")
        directory = _require_path(directory, "directory")
        out = Path(migrate_out) if migrate_out else None
        rec = _dispatch(
            st, verb,
            store=store,
            rec_id=rec_id,
            workspace_id=ws,
            directory=directory,
            migrate_out=out,
            dry_run=dry_run,
        )
        return _envelope(
            verb, status, rec,
            store=str(store), id=rec_id, workspace_id=ws, directory=str(directory),
            dry_run=dry_run,
        )

    raise SessionsAppRefusal("UNKNOWN_VERB", verb)
