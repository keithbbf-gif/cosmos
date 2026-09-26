#!/usr/bin/env python3
"""cosmos_pilot — Pilot seat transcript (ORC talk). Propose-only.

GET never mkdir. POST never writes cosmos/ source. ORC has no pen.
Does not bind Hermes. Does not spawn a model. Does not iframe OpenWork.

Live splice target: cosmos/cosmos_pilot.py
Routes: GET/POST /api/v1/pilot  (do NOT reuse /api/v1/orc — that is BootUP)

Schema: cosmos-pilot/1
"""
from __future__ import annotations

import json
import threading
import time
from pathlib import Path, PurePosixPath

SCHEMA = "cosmos-pilot/1"
STREAMS = ("Cm", "plumbing", "physics", "chapter")
MAX_TEXT = 8000
TAIL_DEFAULT = 80
TAIL_MAX = 200
# Component prefixes, not substrings. "notcosmos" is not "cosmos".
_PEN_PARTS = (
    ("cosmos",),
    ("builds",),
    ("live", "ledger"),
    ("live", "registry"),
)
_APPEND_LOCK = threading.Lock()


class PilotError(RuntimeError):
    def __init__(self, kind: str, detail: str = ""):
        super().__init__(detail or kind)
        self.kind = kind
        self.detail = detail or kind


def _pin_stream(stream: str) -> str:
    s = (stream or "Cm").strip()
    if s not in STREAMS:
        raise PilotError("BAD_STREAM", f"stream must be one of {STREAMS}, got {s!r}")
    return s


def _pilot_file(paths, stream: str) -> Path:
    # paths.state("pilot") may mkdir in some resolvers — never call it on GET.
    state = paths.role("state")
    return Path(state) / "pilot" / f"{stream}.jsonl"


def _unmeasured(stream: str, note: str) -> dict:
    return {
        "schema": SCHEMA,
        "kind": "UNMEASURED",
        "stream": stream,
        "turns": [],
        "n": 0,
        "occupant": "ORC",
        "pen": "NONE",
        "note": note,
    }


def snapshot(paths, *, stream: str = "Cm", tail: int = TAIL_DEFAULT) -> dict:
    """GET /api/v1/pilot. Never mkdir. Missing file = UNMEASURED, not empty-zero."""
    s = _pin_stream(stream)
    n = int(tail)
    if n < 1 or n > TAIL_MAX:
        raise PilotError("BAD_TAIL", f"tail must be 1..{TAIL_MAX}")
    p = _pilot_file(paths, s)
    if not p.is_file():
        return _unmeasured(
            s,
            "no Pilot transcript on disk. POST /api/v1/pilot files the first "
            "turn. GET never mkdir. ORC has no pen.",
        )
    rows: list[dict] = []
    try:
        text = p.read_text(encoding="utf-8")
    except OSError as e:
        return _unmeasured(s, f"READ_FAILED: {type(e).__name__}: {e}"[:240])
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            rec = {"kind": "BROKE", "text": line[:200]}
        if isinstance(rec, dict):
            rows.append(rec)
    tail_rows = rows[-n:]
    return {
        "schema": SCHEMA,
        "kind": "MEASURED",
        "stream": s,
        "turns": tail_rows,
        "n": len(rows),
        "tail": len(tail_rows),
        "path": str(p),
        "occupant": "ORC",
        "pen": "NONE",
        "note": "append-only. ORC replies land as role=orc. Captain as role=captain.",
    }


def _refuse_pen(body: dict) -> None:
    for key in ("path", "write", "target", "file"):
        val = body.get(key)
        if not val:
            continue
        s = str(val).replace("\\", "/").strip()
        if len(s) > 1 and s[1] == ":":
            s = s[2:]
        parts = tuple(
            p.casefold() for p in PurePosixPath(s).parts
            if p not in ("/", ".", "")
        )
        for pref in _PEN_PARTS:
            n = len(pref)
            if len(parts) >= n and parts[:n] == pref:
                raise PilotError(
                    "PEN_REFUSED",
                    "ORC/Pilot never writes the COSMOS live tree. "
                    "File a work order; CCr disposes.",
                )


def post_turn(kernel, body: dict) -> dict:
    """POST /api/v1/pilot {stream, text, role?}.

    Core (CCr pen) appends the captain turn. Does not call an LLM.
    Does not bind Hermes. Optional mail drop if kernel.mail is composed.
    """
    if not isinstance(body, dict):
        raise PilotError("BAD_REQUEST", "body must be a JSON object")
    _refuse_pen(body)
    s = _pin_stream(str(body.get("stream") or "Cm"))
    text = str(body.get("text") or "").strip()
    if not text:
        raise PilotError("EMPTY", "text is required")
    if len(text) > MAX_TEXT:
        raise PilotError("TOO_LONG", f"text max {MAX_TEXT}")
    role = str(body.get("role") or "captain").strip().lower()
    if role != "captain":
        raise PilotError(
            "ORC_REPLY_REFUSED",
            "HTTP posts role=captain only. ORC replies are not a request field.",
        )

    paths = kernel.paths
    p = _pilot_file(paths, s)
    rec = {
        "schema": SCHEMA,
        "at": time.time(),
        "stream": s,
        "role": "captain",
        "principal": str(body.get("principal") or "captain:cdeck"),
        "text": text[:MAX_TEXT],
        "pen": "NONE",
    }
    line = json.dumps(rec, default=str) + "\n"
    with _APPEND_LOCK:
        p.parent.mkdir(parents=True, exist_ok=True)  # POST only
        with p.open("a", encoding="utf-8") as fh:
            fh.write(line)
            fh.flush()

    mail_note = "MAIL_NOT_COMPOSED"
    mail = getattr(kernel, "mail", None)
    if mail is not None and role == "captain":
        to = getattr(mail, "orc", None)
        if isinstance(to, str) and to.strip() and hasattr(mail, "send"):
            try:
                mail.send(to.strip(), "PILOT_IN", text[:MAX_TEXT])
                mail_note = "MAILED"
            except Exception as e:  # noqa: BLE001
                mail_note = f"MAIL_FAILED:{type(e).__name__}"
        else:
            mail_note = "MAIL_NO_ORC_SLOT"

    ledger_note = "APPENDED"
    try:
        kernel.ledger.append(
            "PILOT_TURN",
            {"stream": s, "role": role, "n": len(text), "mail": mail_note, "pen": "NONE"},
        )
    except Exception as e:  # noqa: BLE001 — the turn is on disk; say the chain missed it
        ledger_note = f"APPEND_FAILED:{type(e).__name__}"

    return {
        "schema": SCHEMA,
        "kind": "ACCEPTED",
        "stream": s,
        "role": role,
        "mail": mail_note,
        "ledger": ledger_note,
        "pen": "NONE",
        "path": str(p),
        "note": "queued for ORC. Not an LLM call. Not Hermes. Not a CORE write.",
    }


def _selftest() -> int:
    class _P:
        def role(self, name: str) -> Path:
            import tempfile
            root = Path(tempfile.mkdtemp())
            return root / name

    class _K:
        paths = _P()
        mail = None
        class ledger:
            @staticmethod
            def append(*_a, **_k):
                return None

    # GET missing file is UNMEASURED, not n=0 MEASURED
    rec = snapshot(_K.paths, stream="Cm")
    assert rec["kind"] == "UNMEASURED", rec
    assert rec["n"] == 0
    try:
        post_turn(_K, {"stream": "Cm", "text": "hello", "path": "cosmos/foo.py"})
        raise SystemExit("pen write must refuse")
    except PilotError as e:
        assert e.kind == "PEN_REFUSED"
    return 0


if __name__ == "__main__":
    raise SystemExit(_selftest())
