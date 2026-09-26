#!/usr/bin/env python3
"""Thin adapter. The sessions page already POSTs here.

The engine lives in builds/sessions-page/ and is also a standalone program.
This module does not change the service, the ledger, or the cDeck scripts.
GET never walks transcripts and never creates directories.

    py -3.14 cosmos/cosmos_session_tools_kit.py
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

SCHEMA = "cosmos-session-tools-kit/1"
ENGINE = Path(__file__).resolve().parents[1] / "builds" / "sessions-page" / "engine.py"

_MOD = None


class SessionToolsKitError(RuntimeError):
    def __init__(self, kind: str, detail: str = ""):
        self.kind = kind
        super().__init__(detail or kind)


def _engine():
    global _MOD
    if _MOD is not None:
        return _MOD
    if not ENGINE.is_file():
        raise SessionToolsKitError("ENGINE_MISSING", str(ENGINE))
    spec = importlib.util.spec_from_file_location("sessions_page_engine", ENGINE)
    if spec is None or spec.loader is None:
        raise SessionToolsKitError("ENGINE_MISSING", str(ENGINE))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _MOD = mod
    return mod


def snapshot(paths=None) -> dict:
    """Presence and the verb list. Does not scan session bodies."""
    del paths
    try:
        eng = _engine()
    except SessionToolsKitError as exc:
        return {"schema": SCHEMA, "kind": exc.kind, "detail": str(exc), "verbs": []}
    return {
        "schema": SCHEMA,
        "kind": "OK",
        "engine": "builds/sessions-page",
        "verbs": list(eng.VERBS),
        "harnesses": list(eng.HARNESSES),
        "homes": eng.home_status(),
        "note": "GET does not walk transcripts and does not mkdir. crash-recover restores from a sibling bak.",
    }


def _shape(action: str, body: dict, rec: dict) -> dict:
    """Pane keys the Sessions suite already paints. kind and gate stay."""
    if action == "strip_dry":
        gate = rec.get("gate") or {}
        dropped = int(gate.get("dropped_markers") or 0)
        rec["class"] = rec.get("kind")
        rec["would_strip"] = dropped > 0
        rec["src"] = str(body.get("id") or body.get("path") or "")
    elif action == "strip":
        gate = rec.get("gate") or {}
        written = rec.get("written") or {}
        rec["result"] = {
            "status": rec.get("kind"),
            "turns": gate.get("kept"),
            "dest": written.get("jsonl") or "",
        }
    return rec


def run(body: dict, paths=None, homes=None) -> dict:
    """POST /api/v1/session_tools. Typed refusals stay visible."""
    del paths
    if not isinstance(body, dict):
        raise SessionToolsKitError("BAD_REQUEST", "body must be an object")
    eng = _engine()
    action = str(body.get("action") or body.get("verb") or "")
    payload = dict(body)
    if action == "crash-recover":
        payload["apply"] = payload.get("apply") is True
    try:
        rec = eng.dispatch(action, payload, homes=homes)
    except eng.PageError as exc:
        raise SessionToolsKitError(exc.kind, str(exc)) from exc
    if isinstance(rec, dict):
        return _shape(action, payload, rec)
    return rec


def _selftest() -> int:
    import tempfile

    results = []

    def check(label, fn):
        try:
            results.append((label, bool(fn()), ""))
        except Exception as exc:  # noqa: BLE001
            results.append((label, False, f"{type(exc).__name__}: {exc}"))

    temp_before = set(Path(tempfile.gettempdir()).iterdir())
    snap = snapshot(None)
    temp_after = set(Path(tempfile.gettempdir()).iterdir())
    check("snapshot kind OK and names crash-recover",
          lambda: snap.get("kind") == "OK" and "crash-recover" in snap.get("verbs", []))
    check("snapshot leaves n null until a walk",
          lambda: all(row.get("n") is None for row in snap.get("homes") or []))
    check("snapshot does not create a temp directory", lambda: temp_before == temp_after)

    root = Path(tempfile.mkdtemp(prefix="sesspage_kit_"))
    sid = "11111111-1111-1111-1111-111111111111"
    folder = root / "encoded" / sid
    folder.mkdir(parents=True)
    (folder / "summary.json").write_text(
        '{"info":{"id":"' + sid + '","cwd":"V:\\\\work","generated_title":"kit"}}',
        encoding="utf-8")
    (folder / "chat_history.jsonl").write_text(
        '{"role":"user","text":"hello from kit"}\n'
        '{"role":"tool_call","text":"run a tool"}\n',
        encoding="utf-8")
    homes: dict[str, Path | None] = {name: None for name in (
        "grok", "claude", "codex", "cursor", "cowork", "openwork", "claude_desktop", "gemini")}
    homes["grok"] = root
    found = run({"action": "find", "limit": 10}, homes=homes)
    check("find sees the grok fixture",
          lambda: found["kind"] == "OK" and found["gate"]["n"] == 1)
    bad_kind = ""
    try:
        run({"action": "nope"}, homes=homes)
        check("bad action raises", lambda: False)
    except SessionToolsKitError as exc:
        bad_kind = exc.kind
    check("bad action is BAD_ACTION", lambda: bad_kind == "BAD_ACTION")
    closed = run({"action": "migrate"}, homes=homes)
    check("migrate stays closed", lambda: closed["kind"] == "DO_NOT_REINGEST")
    doi = run({"action": "doi"}, homes=homes)
    check("doi is unproven", lambda: doi["kind"] == "UNPROVEN")
    src_bytes = (folder / "chat_history.jsonl").read_bytes()
    dry_strip = run({"action": "strip_dry", "id": sid}, homes=homes)
    check("strip_dry names would_strip and leaves the source",
          lambda: dry_strip.get("would_strip") is True
          and dry_strip.get("src") == sid
          and dry_strip.get("kind") == "OK"
          and "gate" in dry_strip
          and (folder / "chat_history.jsonl").read_bytes() == src_bytes)
    stripped = run({"action": "strip", "id": sid, "out": str(root / "out")}, homes=homes)
    check("strip result names kept turns and dest",
          lambda: stripped.get("result", {}).get("turns") == 1
          and str(stripped.get("result", {}).get("dest") or "").endswith(".ctr.jsonl")
          and (folder / "chat_history.jsonl").read_bytes() == src_bytes)
    broken = root / "store.jsonl"
    broken.write_bytes(b'{"a": 1}\n{"b":\n')
    bak = root / "store.jsonl.bak"
    bak.write_bytes(b'{"a": 1}\n')
    broken_before = broken.read_bytes()
    dry_rec = run({"action": "crash-recover", "target": str(broken)})
    lied = run({"action": "crash-recover", "target": str(broken), "apply": "false"})
    check("crash-recover without boolean true is a dry run",
          lambda: dry_rec.get("kind") == "DRY_RUN"
          and lied.get("kind") == "DRY_RUN"
          and broken.read_bytes() == broken_before)
    applied = run({"action": "crash-recover", "target": str(broken), "apply": True})
    check("crash-recover apply replaces from the sibling bak",
          lambda: applied.get("kind") == "OK" and broken.read_bytes() == bak.read_bytes())

    failed = [f"FAIL {label} — {detail}" for label, ok, detail in results if not ok]
    for label, ok, detail in results:
        print(("ok  " if ok else "FAIL") + " " + label + (f" — {detail}" if detail else ""))
    print(f"{len(results) - len(failed)}/{len(results)}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(_selftest())
