#!/usr/bin/env python3
"""cosmos_or_fill_first — Hermes fill_first selector, COSMOS-native.

Source: 11_PROPOSAL_20260922_PILOT_WOMB_GITUR.md §4
Land: cosmos/cosmos_or_fill_first.py
Rail attachment (cosmos_openrouter_rail live HTTP):
    chosen = pick(paths)
    note_status(paths, status)    # 429 retries once; 402 rotates now

Stick on the current key file until 402, or until a second 429. The first
429 stays so the next call retries that same key. Round-robin is refused:
a rotate is one prompt-cache miss, and only when a different file exists.
A 2xx clears the retry. Any other status leaves the cursor alone.
The cursor is the key filename, not a bare index.

Does not bind the Hermes binary. Does not return or print key bytes.
Presence reads a file only to reject whitespace; the text stays local.
pick never mkdir. Missing keys = UNMEASURED. Broken state = BROKE.

    py -3.14 cosmos\\cosmos_or_fill_first.py --selftest
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import threading
import time
from pathlib import Path

SCHEMA = "cosmos-or-fill-first/1"
KEY_NAMES = (
    "openrouter_api_key.txt",
    "openrouter_api_key_2.txt",
    "openrouter_api_key_3.txt",
)
ROTATE_ON = frozenset({402, 429})
STATE_NAME = "fill_first.json"
VIEW_KEYS = (
    "schema", "kind", "key_name", "index", "n",
    "last_status", "retries", "rotated", "note",
)
_POOL = threading.Lock()


class FillFirstError(RuntimeError):
    def __init__(self, kind: str, detail: str = ""):
        super().__init__(detail or kind)
        self.kind = kind
        self.detail = detail or kind


def _state_file(paths) -> Path:
    # live/state/openrouter/fill_first.json — note_status may mkdir; pick does not.
    return Path(paths.role("state")) / "openrouter" / STATE_NAME


def _nonempty_file(path: Path) -> bool:
    """True when the file has non-whitespace text. The text is not returned."""
    try:
        if not path.is_file():
            return False
        return bool(path.read_text(encoding="utf-8").strip())
    except OSError:
        return False


def _present_keys(paths) -> list[str]:
    found = []
    for name in KEY_NAMES:
        if _nonempty_file(Path(paths.config(name))):
            found.append(name)
    return found


def _read_state(paths) -> dict:
    p = _state_file(paths)
    if not p.is_file():
        return {"schema": SCHEMA, "index": 0, "last_status": None, "retries": 0}
    try:
        rec = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"index": 0, "kind": "BROKE"}
    if not isinstance(rec, dict):
        return {"index": 0, "kind": "BROKE"}
    return rec


def _cursor(found: list[str], st: dict) -> int:
    """Filename wins. A vanished file walks forward through KEY_NAMES."""
    if st.get("kind") == "BROKE":
        return 0
    name = st.get("key_name")
    if isinstance(name, str) and name in found:
        return found.index(name)
    if isinstance(name, str) and name in KEY_NAMES:
        start = KEY_NAMES.index(name) + 1
        order = list(KEY_NAMES[start:]) + list(KEY_NAMES[:start])
        for nxt in order:
            if nxt in found:
                return found.index(nxt)
    try:
        idx = int(st.get("index") or 0)
    except (TypeError, ValueError):
        idx = 0
    return idx % len(found)


def _write_state(paths, rec: dict) -> None:
    p = _state_file(paths)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    os.replace(tmp, p)


def view(rec: dict) -> dict:
    """Allowlist. Key bytes never have a field here."""
    if not isinstance(rec, dict):
        return {}
    return {k: rec.get(k) for k in VIEW_KEYS if k in rec}


def _pick_unlocked(paths) -> dict:
    found = _present_keys(paths)
    if not found:
        return {
            "schema": SCHEMA,
            "kind": "UNMEASURED",
            "key_name": None,
            "index": None,
            "n": 0,
            "note": "no openrouter_api_key.txt (_2/_3). Keith pastes. pick never mkdir.",
        }
    st = _read_state(paths)
    broke = st.get("kind") == "BROKE"
    idx = 0 if broke else _cursor(found, st)
    return {
        "schema": SCHEMA,
        "kind": "BROKE" if broke else "MEASURED",
        "key_name": found[idx],
        "index": idx,
        "n": len(found),
        "last_status": None if broke else st.get("last_status"),
        "retries": 0 if broke else int(st.get("retries") or 0),
        "note": (
            "state unreadable; first present key"
            if broke else "fill_first. Not round-robin. Secret not echoed."
        ),
    }


def pick(paths) -> dict:
    """Choose the current key file name. Never returns the secret."""
    with _POOL:
        return _pick_unlocked(paths)


def _status_code(status) -> int:
    try:
        return int(status)
    except (TypeError, ValueError) as e:
        raise FillFirstError("BAD_STATUS", "HTTP status is not an int") from e


def note_status(paths, status: object, *, retry: bool | None = None) -> dict:
    """Record HTTP status. 402 rotates now. 429 retries the same key once.

    retry defaults to True only for 429. A rotate that would land on the
    same filename stays put and does not claim a cache miss.
    """
    code = _status_code(status)
    if retry is None:
        retry = code == 429
    with _POOL:
        return _note_unlocked(paths, code, retry=bool(retry))


def _note_unlocked(paths, code: int, *, retry: bool) -> dict:
    if code < 0:
        cur = _pick_unlocked(paths)
        cur["note"] = "no http status; pool unchanged"
        return cur
    found = _present_keys(paths)
    if not found:
        raise FillFirstError("NO_KEYS", "no OpenRouter key files")
    st = _read_state(paths)
    if st.get("kind") == "BROKE":
        idx = 0
        retries = 0
    else:
        idx = _cursor(found, st)
        try:
            retries = int(st.get("retries") or 0)
        except (TypeError, ValueError):
            retries = 0
    prev = found[idx]
    rotated = False
    if code in ROTATE_ON:
        if retry and retries < 1:
            retries += 1
            note = "stuck on key (cache warm)"
        else:
            nxt = found[(idx + 1) % len(found)]
            if nxt == prev:
                retries = 1
                note = "only one key; stayed"
            else:
                idx = found.index(nxt)
                retries = 0
                rotated = True
                note = "rotated"
    elif 200 <= code < 300:
        retries = 0
        note = "stuck on key (cache warm)"
    else:
        note = "status recorded; pool unchanged"
    rec = {
        "schema": SCHEMA,
        "index": idx,
        "last_status": code,
        "retries": retries,
        "rotated": rotated,
        "at": time.time(),
        "key_name": found[idx],
    }
    _write_state(paths, rec)
    rec["kind"] = "MEASURED"
    rec["n"] = len(found)
    rec["note"] = note
    return rec


def _selftest() -> int:
    class Paths:
        def __init__(self, root: Path):
            self._root = root
            (root / "state").mkdir(parents=True, exist_ok=True)
            (root / "config").mkdir(parents=True, exist_ok=True)

        def role(self, name: str, *parts: str) -> Path:
            return self._root.joinpath(name, *parts)

        def config(self, name: str) -> Path:
            return self._root / "config" / name

    results = []

    def check(label, fn):
        try:
            results.append((label, bool(fn()), ""))
        except Exception as e:  # noqa: BLE001
            results.append((label, False, f"{type(e).__name__}: {e}"))

    p = Paths(Path(tempfile.mkdtemp(prefix="fill_first_")))
    state = _state_file(p)
    rec0 = pick(p)
    check("missing keys are UNMEASURED",
          lambda: rec0["kind"] == "UNMEASURED" and rec0["n"] == 0
          and rec0["key_name"] is None)
    check("pick did not mkdir fill_first.json",
          lambda: not state.exists() and not state.parent.exists())

    secret_a = "kA-selftest"
    secret_b = "kB-selftest"
    secret_c = "kC-selftest"
    p.config("openrouter_api_key.txt").write_text(secret_a + "\n", encoding="utf-8")
    p.config("openrouter_api_key_2.txt").write_text(secret_b + "\n", encoding="utf-8")
    p.config("openrouter_api_key_3.txt").write_text(secret_c + "\n", encoding="utf-8")
    a = pick(p)
    check("sticks on key A",
          lambda: a["kind"] == "MEASURED"
          and a["key_name"] == "openrouter_api_key.txt" and a["index"] == 0)
    check("pick does not echo the secret",
          lambda: secret_a not in json.dumps(a) and secret_b not in json.dumps(view(a)))

    note_status(p, 429)
    b = pick(p)
    check("first 429 stays on A",
          lambda: b["key_name"] == "openrouter_api_key.txt")
    held = note_status(p, 500)
    check("500 keeps the 429 strike on A",
          lambda: held["rotated"] is False and held["retries"] == 1
          and held["key_name"] == "openrouter_api_key.txt")
    noted = note_status(p, 200)
    check("200 clears the retry and stays on A",
          lambda: noted["rotated"] is False and noted["retries"] == 0
          and noted["key_name"] == "openrouter_api_key.txt")
    note_status(p, 429)
    note_status(p, 429)
    c = pick(p)
    check("second 429 rotates to _2",
          lambda: c["key_name"] == "openrouter_api_key_2.txt" and c["index"] == 1)

    fresh = Paths(Path(tempfile.mkdtemp(prefix="fill_first_402_")))
    fresh.config("openrouter_api_key.txt").write_text(secret_a + "\n", encoding="utf-8")
    fresh.config("openrouter_api_key_2.txt").write_text(secret_b + "\n", encoding="utf-8")
    pay = note_status(fresh, 402, retry=False)
    check("402 rotates immediately",
          lambda: pay["rotated"] is True
          and pay["key_name"] == "openrouter_api_key_2.txt")
    blob = _state_file(fresh).read_text(encoding="utf-8")
    check("state file has no key bytes",
          lambda: secret_a not in blob and secret_b not in blob
          and "openrouter_api_key_2.txt" in blob)

    solo = Paths(Path(tempfile.mkdtemp(prefix="fill_first_solo_")))
    solo.config("openrouter_api_key.txt").write_text(secret_a + "\n", encoding="utf-8")
    one = note_status(solo, 402, retry=False)
    check("402 on one key does not claim a rotate",
          lambda: one["rotated"] is False
          and one["key_name"] == "openrouter_api_key.txt"
          and one["note"] == "only one key; stayed")

    blank = Paths(Path(tempfile.mkdtemp(prefix="fill_first_blank_")))
    blank.config("openrouter_api_key.txt").write_text(" \n", encoding="utf-8")
    blank.config("openrouter_api_key_2.txt").write_text(secret_b + "\n", encoding="utf-8")
    check("whitespace file is not a key",
          lambda: pick(blank)["key_name"] == "openrouter_api_key_2.txt")

    gone = Paths(Path(tempfile.mkdtemp(prefix="fill_first_gone_")))
    gone.config("openrouter_api_key.txt").write_text(secret_a + "\n", encoding="utf-8")
    gone.config("openrouter_api_key_3.txt").write_text(secret_c + "\n", encoding="utf-8")
    _write_state(gone, {
        "schema": SCHEMA, "index": 0, "retries": 0,
        "key_name": "openrouter_api_key_2.txt", "last_status": 402,
    })
    check("vanished _2 walks forward to _3",
          lambda: pick(gone)["key_name"] == "openrouter_api_key_3.txt"
          and pick(gone)["kind"] == "MEASURED")

    broke = Paths(Path(tempfile.mkdtemp(prefix="fill_first_broke_")))
    broke.config("openrouter_api_key.txt").write_text(secret_a + "\n", encoding="utf-8")
    dest = _state_file(broke)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text("{", encoding="utf-8")
    bad = pick(broke)
    check("broken state is BROKE on the first key",
          lambda: bad["kind"] == "BROKE"
          and bad["key_name"] == "openrouter_api_key.txt")

    empty = Paths(Path(tempfile.mkdtemp(prefix="fill_first_empty_")))
    try:
        note_status(empty, 429)
        no_keys = False
    except FillFirstError as e:
        no_keys = e.kind == "NO_KEYS"
    check("note_status without files is NO_KEYS", lambda: no_keys)
    try:
        note_status(p, "nope")
        bad_status = False
    except FillFirstError as e:
        bad_status = e.kind == "BAD_STATUS"
    check("non-int status is BAD_STATUS", lambda: bad_status)

    race = Paths(Path(tempfile.mkdtemp(prefix="fill_first_race_")))
    race.config("openrouter_api_key.txt").write_text(secret_a + "\n", encoding="utf-8")
    race.config("openrouter_api_key_2.txt").write_text(secret_b + "\n", encoding="utf-8")
    errs = []

    def _hit():
        try:
            note_status(race, 429)
        except Exception as e:  # noqa: BLE001
            errs.append(type(e).__name__)

    t1 = threading.Thread(target=_hit)
    t2 = threading.Thread(target=_hit)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    after = pick(race)
    check("two 429s under the lock rotate once",
          lambda: not errs and after["key_name"] == "openrouter_api_key_2.txt")

    failed = [(label, err) for label, ok, err in results if not ok]
    for label, ok, err in results:
        print(("PASS" if ok else "FAIL"), label, err)
    print("fill_first selftest", f"{len(results) - len(failed)}/{len(results)}")
    return 1 if failed else 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        raise SystemExit(_selftest())
    print("usage: py -3.14 cosmos\\cosmos_or_fill_first.py --selftest")
    raise SystemExit(2)
