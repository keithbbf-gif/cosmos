#!/usr/bin/env python3
"""cosmos_xtalk — Core HTTP face of the XTalk stream.

Wire format matches V:\\OpenWork\\XTalk\\cosmos_msg.py (canonical JSON +
sha256 chain). GET never mkdir and never advances a cursor (always peek).

POST Transport B appends to the Core-local stream (live/state/xtalk.jsonl).
POST Transport A is 501 NOT_COMPOSED — inject stays in cosmos_msg.py CLI
until a driver is composed here. Do not fake inject.

GET ?bind=openwork reads the OpenWork research stream read-only
(V:\\OpenWork\\XTalk\\live\\state\\xtalk.jsonl). Persistent pointer:
V:\\Streams\\XTalk\\BUxt.toml. Does not write OpenWork.

    py -3.14 cosmos\\cosmos_xtalk.py --selftest
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
import time
import uuid
from pathlib import Path

SCHEMA = "cosmos-msg/1"
STREAM_SCHEMA = "cosmos-xtalk/1"
GENESIS = "genesis"
TAIL_MAX = 200
DEDUP_WINDOW = 100
LOCK_STALE_SECS = 10.0
OPENWORK_STREAM = Path(r"V:\OpenWork\XTalk\live\state\xtalk.jsonl")
OPENWORK_ROLES = Path(r"V:\OpenWork\XTalk\live\state\roles.json")


class XTalkError(RuntimeError):
    def __init__(self, kind: str, detail: str = ""):
        super().__init__(detail or kind)
        self.kind = kind
        self.detail = detail or kind


def _canonical(obj: dict) -> bytes:
    """Same bytes cosmos_msg.py hashes and writes."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")


def _line_hash(line_bytes: bytes) -> str:
    return "sha256:" + hashlib.sha256(line_bytes).hexdigest()


def resolve_bind(paths, bind: str = "") -> dict:
    """Pick stream + roles. GET/POST never invent a bind file."""
    want = str(bind or "").strip().lower()
    if want in ("openwork", "ow", "workspace"):
        return {
            "kind": "openwork" if OPENWORK_STREAM.is_file() else "UNMEASURED",
            "name": "openwork",
            "stream": OPENWORK_STREAM,
            "roles": OPENWORK_ROLES,
            "writable": False,
            "note": "OpenWork research stream (BUxt). GET only from Core.",
        }
    if paths is None:
        raise XTalkError("NO_PATHS", "need --root or XTALK_BASE for the local stream")
    cfg = Path(paths.config("xtalk.json")) if hasattr(paths, "config") else None
    if cfg is not None and cfg.is_file():
        try:
            rec = json.loads(cfg.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            raise XTalkError("BAD_BIND", f"xtalk.json: {type(e).__name__}: {e}") from e
        if isinstance(rec, dict) and rec.get("stream"):
            return {
                "kind": "config",
                "name": "config",
                "stream": Path(rec["stream"]),
                "roles": Path(rec["roles"]) if rec.get("roles") else Path(paths.role("state")) / "roles.json",
                "writable": bool(rec.get("writable", False)),
                "note": "live/config/xtalk.json",
            }
    state = Path(paths.role("state"))
    return {
        "kind": "local",
        "name": "local",
        "stream": state / "xtalk.jsonl",
        "roles": state / "roles.json",
        "writable": True,
        "note": "COSMOS live/state. Not the OpenWork workspace copy.",
    }


def fence_check(roles: dict, to: str) -> tuple[str, str | None]:
    """Match cosmos_msg.Fence.check. unknown is not Transport A."""
    row = roles.get(to)
    # A list or string is not a role row.
    if not isinstance(row, dict) or not row:
        return "unknown", f"role {to!r} not in registry"
    owner = row.get("owner")
    alive = bool(row.get("alive", False))
    if owner in ("server", "none") or not alive:
        return "A", None
    return "B", f"owner={owner!r} alive — live-owner fence (R3), use the stream"


def _roles_fold(roles: dict) -> dict:
    """Fence projection. Never echoes session ids."""
    out = {}
    if not isinstance(roles, dict):
        return out
    for name, row in roles.items():
        if not isinstance(row, dict):
            continue
        transport, reason = fence_check(roles, str(name))
        out[str(name)] = {
            "harness": row.get("harness"),
            "owner": row.get("owner"),
            "alive": bool(row.get("alive")),
            "transport": transport,
            "reason": reason,
        }
    return out


def _load_roles(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        rec = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return rec if isinstance(rec, dict) else {}


def _read_records(path: Path) -> list[dict]:
    if not path.is_file() or path.stat().st_size == 0:
        return []
    rows = []
    with path.open("rb") as fh:
        for raw in fh:
            raw = raw.strip()
            if not raw:
                continue
            try:
                parsed = json.loads(raw.decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                parsed = None
            # Keep non-objects. The walker must see every line.
            if not isinstance(parsed, dict):
                parsed = {
                    "kind": "BROKE",
                    "raw": raw[:160].decode("utf-8", "replace"),
                }
            rows.append(parsed)
    return rows


def verify_chain(path: Path) -> list[str]:
    """Forward walk. Empty problems list is not used — clean is one 'chain clean' line."""
    problems: list[str] = []
    prev = GENESIS
    seq = 0
    for rec in _read_records(path):
        if rec.get("kind") == "BROKE":
            problems.append(f"unreadable line after seq {seq}")
            continue
        seq += 1
        if rec.get("seq") != seq:
            problems.append(f"seq gap at line {seq}: expected {seq}, got {rec.get('seq')}")
        if rec.get("prev") != prev:
            problems.append(
                f"chain break at seq {seq}: prev={rec.get('prev')!r}, expected {prev!r}")
        prev = _line_hash(_canonical(rec))
    if not problems:
        problems.append(f"chain clean: {seq} records, head={prev}")
    return problems


def snapshot(paths, *, role: str = "", tail: int = 40, bind: str = "",
             verify: bool = False) -> dict:
    """GET fold. Never mkdir. Never advance a cursor."""
    try:
        n = int(tail)
    except (TypeError, ValueError) as e:
        raise XTalkError("BAD_TAIL", f"tail must be an integer, got {tail!r}") from e
    if n < 1 or n > TAIL_MAX:
        raise XTalkError("BAD_TAIL", f"tail must be 1..{TAIL_MAX}")
    loc = resolve_bind(paths, bind)
    p = loc["stream"]
    roles = _roles_fold(_load_roles(loc["roles"]))
    if loc["kind"] == "UNMEASURED" or not p.is_file():
        out = {
            "schema": STREAM_SCHEMA,
            "kind": "UNMEASURED",
            "bind": loc["name"],
            "n": 0,
            "lines": [],
            "inbox": [],
            "roles": roles,
            "path": str(p),
            "writable": loc["writable"],
            "note": loc["note"] + " GET never mkdir.",
        }
        if verify:
            out["verify"] = ["UNMEASURED: xtalk.jsonl absent"]
        return out
    rows = _read_records(p)
    me = (role or "").strip()
    inbox = []
    if me:
        for rec in rows:
            msg = rec.get("msg") or {}
            if isinstance(msg, dict) and str(msg.get("to") or "") == me:
                inbox.append(rec)
    out = {
        "schema": STREAM_SCHEMA,
        "kind": "MEASURED",
        "bind": loc["name"],
        "n": len(rows),
        "lines": rows[-n:],
        "inbox": inbox[-n:] if me else [],
        "roles": roles,
        "role": me or None,
        "path": str(p),
        "writable": loc["writable"],
        "note": loc["note"] + " inbox is peek-only (GET never consumes a cursor).",
    }
    if rows:
        last = rows[-1]
        seq = last.get("seq")
        if last.get("kind") == "BROKE" or isinstance(seq, bool) or not isinstance(seq, int):
            out["head"] = "UNMEASURED"
        else:
            out["seq"] = seq
            try:
                out["head"] = _line_hash(_canonical(last))
            except (TypeError, ValueError):
                out["head"] = "UNMEASURED"
    if verify:
        out["verify"] = verify_chain(p)
    return out


def _lock(lockdir: Path) -> Path:
    lockdir.mkdir(parents=True, exist_ok=True)
    lock = lockdir / "stream.lock"
    deadline = time.monotonic() + 5.0
    while True:
        try:
            fd = os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, str(os.getpid()).encode())
            os.close(fd)
            return lock
        except FileExistsError:
            try:
                age = time.time() - lock.stat().st_mtime
            except FileNotFoundError:
                continue
            if age > LOCK_STALE_SECS:
                try:
                    lock.unlink()
                except FileNotFoundError:
                    pass
                continue
            if time.monotonic() >= deadline:
                raise XTalkError("LOCK", f"stream lock held too long: {lock}")
            time.sleep(0.02)


def _unlock(lock: Path) -> None:
    try:
        lock.unlink()
    except FileNotFoundError:
        pass


def _next_link(last: dict | None) -> tuple[int, str]:
    """Next seq and prev hash. An unreadable tail is not a link."""
    if last is None:
        return 1, GENESIS
    seq = last.get("seq")
    if last.get("kind") == "BROKE" or isinstance(seq, bool) or not isinstance(seq, int):
        raise XTalkError("CHAIN", "stream tail is unreadable; refusing to append")
    try:
        prev = _line_hash(_canonical(last))
    except (TypeError, ValueError) as e:
        raise XTalkError("CHAIN", f"stream tail is not canonical: {type(e).__name__}") from e
    return seq + 1, prev


def send(paths, body: dict) -> dict:
    """POST. Transport B appends Core-local stream. Transport A is a typed hole."""
    if not isinstance(body, dict):
        raise XTalkError("BAD_REQUEST", "body must be a JSON object")
    if str(body.get("bind") or "").strip():
        raise XTalkError("BIND_READONLY", "POST writes the Core-local stream only")
    loc = resolve_bind(paths, "")
    if not loc["writable"]:
        raise XTalkError("BIND_READONLY", loc["note"])
    to = str(body.get("to") or "").strip()
    frm = str(body.get("from") or "").strip()
    text = str(body.get("body") or "").strip()
    if not to or not frm or not text:
        raise XTalkError("BAD_MSG", "from, to, body required")
    roles = _load_roles(loc["roles"])
    transport, reason = fence_check(roles, to)
    if transport == "unknown":
        raise XTalkError("BAD_ROLE", reason or f"role {to!r} not in registry")
    if transport == "A":
        row = roles.get(to) or {}
        want_inject = str(body.get("inject") or "").strip().lower() in (
            "1", "true", "yes")
        if want_inject:
            raise XTalkError(
                "NOT_COMPOSED",
                "Transport A inject stays in cosmos_msg.py. "
                "Do not fake inject from Core.",
            )
        return {
            "schema": STREAM_SCHEMA,
            "kind": "DRY_RUN",
            "transport": "A",
            "inject": False,
            "harness": row.get("harness"),
            "owner": row.get("owner"),
            "alive": bool(row.get("alive")),
            "to": to,
            "note": "would inject via cosmos_msg CLI. Core does not fake inject. No stream append.",
        }
    nonce = str(body.get("nonce") or uuid.uuid4().hex)
    msg = {
        "schema": SCHEMA,
        "from": frm,
        "to": to,
        "body": text[:8000],
        "nonce": nonce,
        "turn": body.get("turn"),
        "phase": body.get("phase"),
        "reply_to": body.get("reply_to"),
    }
    p = loc["stream"]
    lockdir = p.parent / "locks"
    p.parent.mkdir(parents=True, exist_ok=True)
    lock = _lock(lockdir)
    try:
        rows = _read_records(p)
        for rec in reversed(rows[-DEDUP_WINDOW:]):
            m = rec.get("msg") or {}
            if isinstance(m, dict) and str(m.get("nonce") or "") == nonce:
                return {
                    "schema": STREAM_SCHEMA,
                    "kind": "ACCEPTED",
                    "duplicate": True,
                    "transport": rec.get("transport") or "B",
                    "seq": rec.get("seq"),
                    "nonce": nonce,
                    "reply": rec.get("reply"),
                    "note": "idempotent nonce. not a second line.",
                }
        last = rows[-1] if rows else None
        seq, prev = _next_link(last)
        rec = {
            "seq": seq,
            "prev": prev,
            "ts": int(time.time() * 1000),
            "transport": "B",
            "reply": None,
            "msg": msg,
        }
        line = _canonical(rec) + b"\n"
        with p.open("ab") as fh:
            fh.write(line)
            fh.flush()
            os.fsync(fh.fileno())
    finally:
        _unlock(lock)
    return {
        "schema": STREAM_SCHEMA,
        "kind": "ACCEPTED",
        "duplicate": False,
        "transport": "B",
        "seq": rec["seq"],
        "nonce": nonce,
        "reply": None,
        "reason": reason,
        "path": str(p),
        "note": "Transport B: stream is the inbox. No harness inject.",
    }


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

    p = Paths(Path(tempfile.mkdtemp(prefix="xtalk_")))
    rec0 = snapshot(p)
    check("GET missing file is UNMEASURED",
          lambda: rec0["kind"] == "UNMEASURED" and rec0["n"] == 0)
    check("GET did not mkdir xtalk.jsonl",
          lambda: not (p.role("state") / "xtalk.jsonl").is_file())

    try:
        send(p, {"from": "captain", "to": "orc", "body": "hi"})
        unknown_ok = False
    except XTalkError as e:
        unknown_ok = e.kind == "BAD_ROLE"
    check("unknown role is BAD_ROLE not a fake inject",
          lambda: unknown_ok)

    (p.role("state") / "roles.json").write_text(json.dumps({
        "orc": {"harness": "grok", "owner": "leader", "alive": True},
        "crew": {"harness": "opencode", "owner": "server", "alive": True},
    }), encoding="utf-8")
    acc = send(p, {"from": "captain", "to": "orc", "body": "hello", "nonce": "n1"})
    check("live-owner send is Transport B",
          lambda: acc["kind"] == "ACCEPTED" and acc["transport"] == "B" and acc["seq"] == 1)
    fold = snapshot(p).get("roles") or {}
    check("roles fold names orc B and crew A, no session id",
          lambda: fold.get("orc", {}).get("transport") == "B"
          and fold.get("crew", {}).get("transport") == "A"
          and "session" not in fold.get("orc", {}))
    dup = send(p, {"from": "captain", "to": "orc", "body": "hello", "nonce": "n1"})
    check("same nonce does not append",
          lambda: dup.get("duplicate") is True and snapshot(p)["n"] == 1)
    rec = snapshot(p, role="orc")
    check("peek inbox to==orc",
          lambda: rec["kind"] == "MEASURED" and rec["n"] == 1
          and rec["inbox"][0]["msg"]["to"] == "orc")
    rec2 = snapshot(p, role="orc")
    check("GET peek does not consume inbox",
          lambda: len(rec2["inbox"]) == 1)
    dry = send(p, {"from": "wombat", "to": "crew", "body": "task"})
    check("server-owned crew is DRY_RUN A, no append",
          lambda: dry.get("kind") == "DRY_RUN" and dry.get("transport") == "A"
          and dry.get("harness") == "opencode" and snapshot(p)["n"] == 1)
    try:
        send(p, {"from": "wombat", "to": "crew", "body": "task", "inject": True})
        inj_ok = False
    except XTalkError as e:
        inj_ok = e.kind == "NOT_COMPOSED"
    check("inject:true on A is still NOT_COMPOSED",
          lambda: inj_ok)
    acc2 = send(p, {"from": "captain", "to": "orc", "body": "second"})
    v = verify_chain(p.role("state") / "xtalk.jsonl")
    check("canonical chain clean after two B appends",
          lambda: acc2["seq"] == 2 and v[0].startswith("chain clean"))

    saved_roles = (p.role("state") / "roles.json").read_text(encoding="utf-8")
    (p.role("state") / "roles.json").write_text(json.dumps({
        "orc": {"harness": "grok", "owner": "leader", "alive": True},
        "blob": ["nope"],
    }), encoding="utf-8")
    try:
        send(p, {"from": "captain", "to": "blob", "body": "x"})
        role_ok = False
    except XTalkError as e:
        role_ok = e.kind == "BAD_ROLE"
    except Exception:  # noqa: BLE001 — a crash is a failed check
        role_ok = False
    check("non-object role is BAD_ROLE", lambda: role_ok)
    (p.role("state") / "roles.json").write_text(saved_roles, encoding="utf-8")

    stream_p = p.role("state") / "xtalk.jsonl"
    good = stream_p.read_bytes()
    stream_p.write_bytes(good + b"null\n")
    hid = verify_chain(stream_p)
    check("non-object line is not chain clean",
          lambda: bool(hid) and not hid[0].startswith("chain clean")
          and any("unreadable" in line for line in hid))
    snap_bad = snapshot(p)
    check("unreadable tail head is not a fake sha256",
          lambda: snap_bad.get("head") == "UNMEASURED")
    try:
        send(p, {"from": "captain", "to": "orc", "body": "third"})
        tail_ok = False
    except XTalkError as e:
        tail_ok = e.kind == "CHAIN"
    check("unreadable tail refuses append", lambda: tail_ok)
    stream_p.write_bytes(good)

    # Wire-compatible with cosmos_msg.py: hash of canonical record.
    sample = {
        "msg": {"body": "x", "from": "a", "nonce": "n", "phase": None,
                "reply_to": None, "schema": SCHEMA, "to": "b", "turn": None},
        "prev": GENESIS, "reply": None, "seq": 1, "transport": "B", "ts": 1,
    }
    check("canonical matches cosmos_msg sort_keys compact",
          lambda: _canonical(sample) == json.dumps(
              sample, sort_keys=True, separators=(",", ":"),
              ensure_ascii=False).encode("utf-8"))

    try:
        send(p, {"from": "xtalk", "to": "ccr", "body": "no", "bind": "openwork"})
        ow_post = False
    except XTalkError as e:
        ow_post = e.kind == "BIND_READONLY"
    check("POST cannot target OpenWork bind", lambda: ow_post)
    if OPENWORK_STREAM.is_file():
        ow = verify_chain(OPENWORK_STREAM)
        check("OpenWork live jsonl verifies with Core hasher",
              lambda: ow and ow[0].startswith("chain clean"))
        ow_snap = snapshot(p, bind="openwork", verify=True)
        check("GET ?bind=openwork is MEASURED read-only",
              lambda: ow_snap["kind"] == "MEASURED" and ow_snap["writable"] is False
              and ow_snap["bind"] == "openwork")

    failed = [(label, e) for label, ok, e in results if not ok]
    for label, ok, err in results:
        print(("PASS" if ok else "FAIL"), label, err)
    print("xtalk selftest", f"{len(results) - len(failed)}/{len(results)}")
    return 1 if failed else 0


def _cli_paths(root: str | None):
    env = (root or os.environ.get("XTALK_BASE") or os.environ.get("COSMOS_ROOT") or "").strip()
    if not env:
        return None

    class Paths:
        def __init__(self, r: Path):
            self._root = r

        def role(self, name: str, *parts: str) -> Path:
            return self._root.joinpath(name, *parts)

        def config(self, name: str) -> Path:
            return self._root / "config" / name

    r = Path(env)
    # A COSMOS live root has state/; XTALK_BASE may already be the state parent.
    if (r / "state").is_dir() or (r / "config").is_dir():
        return Paths(r)
    return Paths(r)


def _cli(argv: list[str]) -> int:
    import argparse
    p = argparse.ArgumentParser(
        prog="cosmos_xtalk",
        description="XTalk CLI — same stream Core serves at GET/POST /api/v1/xtalk",
    )
    p.add_argument("--root", help="COSMOS live root (or XTALK_BASE / COSMOS_ROOT)")
    p.add_argument("--bind", default="", help="local (default) or openwork (read-only)")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("send", help="Transport B append (A is NOT_COMPOSED)")
    s.add_argument("--to", required=True)
    s.add_argument("--body", required=True)
    s.add_argument("--from", dest="from_", default="captain")
    s.add_argument("--nonce")

    i = sub.add_parser("inbox", help="peek inbox (never consumes a cursor)")
    i.add_argument("--role", default="")
    i.add_argument("--tail", default="40")

    sub.add_parser("verify", help="hash-chain walk")
    sub.add_parser("roles", help="fence projection")
    g = sub.add_parser("get", help="full GET fold as JSON")
    g.add_argument("--role", default="")
    g.add_argument("--tail", default="40")
    sub.add_parser("selftest", help="built-in tests")

    a = p.parse_args(argv)
    if a.cmd == "selftest":
        return _selftest()
    paths = _cli_paths(a.root)
    bind = a.bind
    if a.cmd == "send":
        rec = send(paths, {
            "from": a.from_, "to": a.to, "body": a.body,
            "nonce": a.nonce, "bind": bind,
        })
    elif a.cmd == "inbox":
        rec = snapshot(paths, role=a.role, tail=a.tail, bind=bind)
        rec = {"kind": rec.get("kind"), "n": rec.get("n"),
               "inbox": rec.get("inbox"), "role": rec.get("role")}
    elif a.cmd == "verify":
        rec = snapshot(paths, bind=bind, verify=True, tail=1)
        rec = {"kind": rec.get("kind"), "path": rec.get("path"),
               "verify": rec.get("verify")}
    elif a.cmd == "roles":
        rec = snapshot(paths, bind=bind, tail=1)
        rec = {"kind": rec.get("kind"), "roles": rec.get("roles")}
    else:
        rec = snapshot(paths, role=getattr(a, "role", ""),
                       tail=getattr(a, "tail", 40), bind=bind, verify=True)
    print(json.dumps(rec, indent=2, default=str))
    return 0 if rec.get("kind") in ("ACCEPTED", "MEASURED", "UNMEASURED", "DRY_RUN") else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv and len(sys.argv) == 2:
        raise SystemExit(_selftest())
    if len(sys.argv) == 1:
        print("usage: py -3.14 cosmos\\cosmos_xtalk.py --selftest")
        print("       py -3.14 cosmos\\cosmos_xtalk.py [--root LIVE] [--bind openwork] "
              "send|inbox|verify|roles|get|selftest")
        raise SystemExit(2)
    try:
        raise SystemExit(_cli(sys.argv[1:]))
    except XTalkError as e:
        print(json.dumps({"error": e.kind, "detail": str(e)[:300]}))
        raise SystemExit(1)
