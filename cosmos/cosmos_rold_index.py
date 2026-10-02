#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ROLD pointer index for seats, credentials, and demonstrated skills.

One row is a path, a name, and a time. The body stays in the file the path
names. A credential row stores the path of the file Keith acquired. It does
not read that file and it does not store the secret.

    py -3.14 cosmos\\cosmos_rold_index.py --selftest
"""
from __future__ import annotations

import json
import re
import tomllib
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "cosmos-rold-index/1"
KINDS = ("seat", "credential", "skill")
FILES = {
    "seat": "seats.toml",
    "credential": "credentials.toml",
    "skill": "skills.toml",
}
KEY_FIELD = {"seat": "id", "credential": "path", "skill": "slug"}
_SECRET = re.compile(
    r"(sk-[A-Za-z0-9][A-Za-z0-9_-]*|sk-ant-\S+|sk-or-\S+|"
    r"Bearer\s+\S+|-----BEGIN [A-Z ]+-----|"
    r"api[_-]?key\s*[:=]\s*\S+)",
    re.I,
)
_POINTER_LINES = (
    ("seats.toml",
     "POINTER: Ai\\ROLD\\seats.toml         seated models — path to the seat record"),
    ("credentials.toml",
     "POINTER: Ai\\ROLD\\credentials.toml   acquired credentials — path to the file"),
    ("skills.toml",
     "POINTER: Ai\\ROLD\\skills.toml        demonstrated skills — path to SKILL.md"),
)
_RULES = {
    "seats": "seated models — pointer to the seat record, never a copy",
    "credentials": "acquired credentials — path to the file, never the secret",
    "skills": "demonstrated skills — path to SKILL.md",
}


class RoldIndexError(RuntimeError):
    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def _now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def _confine(root: Path, name: str) -> Path:
    base = Path(root).resolve()
    dest = (base / name).resolve()
    try:
        dest.relative_to(base)
    except ValueError as e:
        raise RoldIndexError("ESCAPE", f"{name} leaves the ROLD root") from e
    return dest


def _toml_str(value: str) -> str:
    return json.dumps(str(value), ensure_ascii=False)


def refuse_if_secret(row: dict) -> None:
    """A credential index row is a pointer. A value, or a key-shaped string, refuses."""
    banned = {"value", "secret", "token", "key", "password", "bearer"}
    found = banned.intersection(str(k).lower() for k in row)
    if found:
        raise RoldIndexError("SECRET", "credential index stores a path, not a value")
    blob = " ".join(str(v) for v in row.values())
    if _SECRET.search(blob):
        raise RoldIndexError("SECRET", "row looks like a secret")


def _dump(kind: str, rows: list[dict]) -> str:
    lines = [f'schema = "{SCHEMA}"', f'kind = "{kind}"', ""]
    for row in rows:
        lines.append("[[row]]")
        for key in sorted(row):
            val = row[key]
            if isinstance(val, bool):
                lines.append("%s = %s" % (key, "true" if val else "false"))
            elif isinstance(val, (int, float)) and not isinstance(val, bool):
                lines.append("%s = %s" % (key, val))
            else:
                lines.append("%s = %s" % (key, _toml_str(val)))
        lines.append("")
    return "\n".join(lines)


def _load(path: Path, kind: str) -> list[dict]:
    if not path.is_file():
        return []
    try:
        rec = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError) as e:
        raise RoldIndexError("BROKE", f"{path.name}: {e}") from e
    rows = rec.get("row") if isinstance(rec, dict) else None
    if rows is None:
        return []
    if isinstance(rows, dict):
        rows = [rows]
    if not isinstance(rows, list):
        raise RoldIndexError("BROKE", f"{path.name} row is not a list")
    out = []
    for row in rows:
        if isinstance(row, dict):
            out.append(dict(row))
    return out


def _write(path: Path, kind: str, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(_dump(kind, rows), encoding="utf-8")
    tmp.replace(path)


def ensure_entry(rold: Path) -> dict:
    """Add the three POINTER lines and registry rows once. Later notes do not rewrite them."""
    root = Path(rold)
    if not root.is_dir():
        raise RoldIndexError("NO_ROLD", f"no ROLD directory at {root}")
    idx = _confine(root, "00_INDEX.md")
    text = idx.read_text(encoding="utf-8") if idx.is_file() else "# ROLD — 00_INDEX\n"
    added = []
    for filename, line in _POINTER_LINES:
        if filename not in text:
            if not text.endswith("\n"):
                text += "\n"
            text += line + "\n"
            added.append(filename)
    if added or not idx.is_file():
        idx.write_text(text, encoding="utf-8")
    reg = _confine(root, "registries.toml")
    body = reg.read_text(encoding="utf-8") if reg.is_file() else (
        "# registries.toml — POINTERS ONLY. NEVER COPIES.\n"
        "schema = 1\n"
    )
    blocks = []
    for filename, _line in _POINTER_LINES:
        name = filename.replace(".toml", "")
        if f'name = "{name}"' in body:
            continue
        target = _confine(root, filename)
        blocks.append(
            "[[registry]]\n"
            "name = %s\npath = %s\nrule = %s\n" % (
                _toml_str(name), _toml_str(str(target)), _toml_str(_RULES[name]))
        )
    if blocks:
        if not body.endswith("\n"):
            body += "\n"
        reg.write_text(body + "\n" + "\n".join(blocks), encoding="utf-8")
    return {"added": added, "index": str(idx), "registries": str(reg)}


def note(rold: Path, kind: str, row: dict) -> dict:
    """Upsert one pointer. The same key updates in place."""
    if kind not in KINDS:
        raise RoldIndexError("BAD_KIND", kind)
    if not isinstance(row, dict):
        raise RoldIndexError("BAD_ROW", "row must be an object")
    if kind == "credential":
        refuse_if_secret(row)
    field = KEY_FIELD[kind]
    key = str(row.get(field) or "").strip()
    path = str(row.get("path") or "").strip()
    if not key or not path:
        raise RoldIndexError("BAD_ROW", f"{kind} needs {field} and path")
    if not Path(path).is_file():
        raise RoldIndexError("NO_TARGET", path)
    clean = {str(k): row[k] for k in row if str(k).lower() not in
             {"value", "secret", "token", "key", "password", "bearer"}}
    clean[field] = key
    clean["path"] = path
    clean["indexed_at"] = _now()
    if kind == "credential":
        refuse_if_secret(clean)
    dest = _confine(Path(rold), FILES[kind])
    rows = [r for r in _load(dest, kind) if str(r.get(field) or "") != key]
    rows.append(clean)
    _write(dest, kind, rows)
    return {"kind": kind, "key": key, "path": path, "indexed_at": clean["indexed_at"]}


def lookup(rold: Path, kind: str, key: str) -> dict | None:
    if kind not in KINDS:
        raise RoldIndexError("BAD_KIND", kind)
    field = KEY_FIELD[kind]
    want = str(key)
    for row in _load(_confine(Path(rold), FILES[kind]), kind):
        if str(row.get(field) or "") == want or str(row.get("slug") or "") == want:
            return row
        if kind == "credential" and str(row.get("rail") or "") == want:
            return row
    return None


def index_seat(rold: Path, *, model_id: str, harness: str, path: str,
               seated_at: str = "") -> dict:
    ensure_entry(rold)
    return note(rold, "seat", {
        "id": model_id,
        "harness": harness,
        "path": path,
        "seated_at": seated_at or _now(),
    })


def index_credential(rold: Path, *, rail: str, kind: str, path: str,
                     acquired_at: str = "") -> dict:
    ensure_entry(rold)
    return note(rold, "credential", {
        "rail": rail,
        "cred_kind": kind,
        "path": path,
        "acquired_at": acquired_at or _now(),
    })


def index_skill(rold: Path, *, slug: str, description: str, path: str,
                demonstrated_at: str = "", routine: str = "") -> dict:
    ensure_entry(rold)
    row = {
        "slug": slug,
        "description": description,
        "path": path,
        "demonstrated_at": demonstrated_at or _now(),
    }
    if routine:
        row["routine"] = routine
    return note(rold, "skill", row)


def _selftest() -> int:
    import tempfile

    results = []

    def check(label, fn):
        try:
            results.append((label, bool(fn()), ""))
        except Exception as e:  # noqa: BLE001
            results.append((label, False, f"{type(e).__name__}: {e}"))

    td = Path(tempfile.mkdtemp(prefix="cosmos_rold_"))
    rold = td / "ROLD"
    rold.mkdir()
    (rold / "00_INDEX.md").write_text(
        "# ROLD — 00_INDEX\nPOINTER: Ai\\ROLD\\RULES.md\n", encoding="utf-8")
    seat_body = td / "seat.json"
    seat_body.write_text('{"seated": true}\n', encoding="utf-8")
    cred = td / "openrouter_api_key.txt"
    cred.write_text("sk-live-secret-value\n", encoding="utf-8")
    skill = td / "SKILL.md"
    skill.write_text("# Ask\nAsk before close.\n", encoding="utf-8")

    first = index_seat(rold, model_id="openai/gpt-5.6-luna", harness="codex",
                       path=str(seat_body))
    again = index_seat(rold, model_id="openai/gpt-5.6-luna", harness="codex",
                       path=str(seat_body))
    check("seat indexes once and updates in place",
          lambda: first["key"] == "openai/gpt-5.6-luna"
          and again["indexed_at"] >= first["indexed_at"]
          and (rold / "seats.toml").read_text(encoding="utf-8").count("[[row]]") == 1)
    check("00_INDEX points at the three registries once",
          lambda: (rold / "00_INDEX.md").read_text(encoding="utf-8").count("seats.toml") == 1
          and "credentials.toml" in (rold / "00_INDEX.md").read_text(encoding="utf-8")
          and "skills.toml" in (rold / "00_INDEX.md").read_text(encoding="utf-8"))
    ensure_entry(rold)
    check("a second ensure does not duplicate the pointer",
          lambda: (rold / "00_INDEX.md").read_text(encoding="utf-8").count("seats.toml") == 1)

    index_credential(rold, rail="openrouter", kind="api_key_file", path=str(cred))
    cred_text = (rold / "credentials.toml").read_text(encoding="utf-8")
    stored = lookup(rold, "credential", str(cred))
    check("credential index stores the path and not the secret",
          lambda: stored is not None and stored["path"] == str(cred)
          and "sk-live-secret-value" not in cred_text)
    refused = False
    try:
        note(rold, "credential", {"rail": "x", "path": str(cred), "value": "sk-nope"})
    except RoldIndexError as e:
        refused = e.kind == "SECRET"
    check("a credential value is SECRET", lambda: refused)
    missing = False
    try:
        note(rold, "seat", {"id": "gone", "path": str(td / "nope.json")})
    except RoldIndexError as e:
        missing = e.kind == "NO_TARGET"
    check("a missing target is NO_TARGET", lambda: missing)
    index_skill(rold, slug="resession-ask", description="Ask, then close.",
                path=str(skill))
    found = lookup(rold, "skill", "resession-ask")
    check("lookup returns the skill path",
          lambda: found is not None and found["path"] == str(skill))
    by_rail = lookup(rold, "credential", "openrouter")
    check("lookup finds a credential by rail",
          lambda: by_rail is not None and by_rail["path"] == str(cred))

    failed = [label for label, ok, _err in results if not ok]
    for label, ok, err in results:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (rold index)"
          % ("PASS" if not failed else "FAIL", len(results)))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(_selftest())
