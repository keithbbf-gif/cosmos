#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gbridge - T1 slice 1: synchronous ask() facade between COW and the GrokBot team.

CONTRACT (docs/T1_ARCH.md): one blocking call returns a structured Answer or a TYPED
refusal - never a silent wait. Transport is injected (rubric R6): MailboxTransport is
PRIMARY (real team identity via files; depends on nothing that can run out),
XaiApiTransport is the API-second FALLBACK (Grok model, NOT the team) and refuses in
this slice. Wire shape is versioned; validation is fail-closed; a reply that never
verifies is TORN_REPLY, absence is TIMEOUT, and the request file is left in place so
a late reply stays collectible.

Scar lineage: cosmos_mail - atomic tmp->replace install, send-side read-back, sha256
on every body, one root HANDED IN (this module resolves nothing), and a missing
endpoint is THE PHONE IS DEAD, never a quiet mkdir.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Optional, Protocol

WIRE_VERSION = 1
STATUSES = frozenset({"ok", "needs_input", "blocked", "error"})
DEFAULT_TIMEOUT_S = 120.0
# Deadline pass: a present-but-unparseable reply is retried briefly so a bot
# finishing an in-place write is not immediately TORN_REPLY (HIGH: poll race).
_FINAL_PARSE_ATTEMPTS = 3
_FINAL_PARSE_RETRY_S = 0.03


class RefusalKind(StrEnum):
    """Closed set of typed-refusal kinds. StrEnum so kind == "TIMEOUT" still holds."""

    BAD_REQUEST = "BAD_REQUEST"
    ROOT_MISSING = "ROOT_MISSING"
    TORN_REQUEST = "TORN_REQUEST"
    TIMEOUT = "TIMEOUT"
    TORN_REPLY = "TORN_REPLY"
    BAD_STATUS = "BAD_STATUS"
    NO_KEY = "NO_KEY"
    NOT_WIRED = "NOT_WIRED"


class GBridgeError(RuntimeError):
    """Typed refusal. `kind` is a RefusalKind (also a str). Unknown kinds fail-closed
    at construction so a typo like TIME_OUT cannot leak past type checking."""

    def __init__(self, kind: RefusalKind | str, detail: str):
        if not isinstance(kind, RefusalKind):
            try:
                kind = RefusalKind(kind)
            except ValueError as e:
                raise ValueError(
                    f"unknown GBridgeError kind {kind!r}; must be one of "
                    f"{[k.value for k in RefusalKind]}"
                ) from e
        self.kind: RefusalKind = kind
        super().__init__(f"[{kind}] {detail}")


def _sha256(s: str) -> str:
    """SHA-256 of one hashed wire field (request `text` or reply `answer`), UTF-8.

    The JSON key is `body_sha256` (T1_ARCH §5). That name is the wire name for the
    hash of that single field — not a hash of the whole JSON document.
    """
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _now():
    """Current epoch + UTC offset in seconds, from the local tz-aware clock.

    datetime.now().astimezone() is the current offset (DST-aware). time.timezone
    + tm_isdst is the historical-Windows shortcut the stage-5 critique named.
    """
    dt = datetime.now().astimezone()
    off = dt.utcoffset()
    off_s = int(off.total_seconds()) if off is not None else 0
    return dt.timestamp(), off_s


def _atomic_install(final_p: Path, payload: dict) -> None:
    """Write JSON via tmp -> os.replace so a reader never sees a partial file."""
    tmp = final_p.with_name(final_p.stem + ".part")
    tmp.write_text(json.dumps(payload, indent=1), encoding="utf-8")
    os.replace(tmp, final_p)


@dataclass(frozen=True)
class Ask:
    request_id: str
    text: str
    context: str
    timeout_s: float
    epoch: float
    utc_offset_s: int


@dataclass(frozen=True)
class Answer:
    request_id: str
    status: str
    answer: str


class Transport(Protocol):
    def send(self, ask: Ask) -> None: ...

    def poll(self, ask: Ask, final: bool = False) -> Optional[Answer]:
        """None means 'not yet'. final=True is the deadline pass: a reply that is
        present but never validates must raise TORN_REPLY instead of returning None."""
        ...


# ---------------- PRIMARY transport: the file mailbox ----------------
class MailboxTransport:
    """Request/reply file mailbox under ONE handed-in root: to_gbot/ and from_gbot/.
    Synchronous at COW, still asynchronous at grok.com - the honest architecture until
    a Teams API exists. The team's instructions gain one line: answer request files in
    to_gbot/ by writing the reply shape to from_gbot/ (prefer write_reply() so the
    install is atomic; poll still treats a mid-write as 'not yet' until the deadline).
    """

    def __init__(self, mail_root: str | os.PathLike):
        self.root = Path(mail_root)
        self.to_dir = self.root / "to_gbot"
        self.from_dir = self.root / "from_gbot"

    def register(self) -> None:
        """Explicit, like cosmos_mail: an endpoint that appears as a side effect of a
        send is an endpoint nobody knows they own."""
        self.to_dir.mkdir(parents=True, exist_ok=True)
        self.from_dir.mkdir(parents=True, exist_ok=True)

    def send(self, ask: Ask) -> None:
        if not (self.to_dir.is_dir() and self.from_dir.is_dir()):
            raise GBridgeError(RefusalKind.ROOT_MISSING,
                               f"mailbox not registered under {self.root} - THE PHONE "
                               f"IS DEAD, not 'no news'")
        # body_sha256 = sha256 of the `text` field (not the whole JSON document).
        text_sha256 = _sha256(ask.text)
        payload = {"gbridge": WIRE_VERSION, "request_id": ask.request_id,
                   "from": "COW", "to": "GBOT",
                   "epoch": ask.epoch, "utc_offset_s": ask.utc_offset_s,
                   "text": ask.text, "context": ask.context,
                   "timeout_s": ask.timeout_s, "body_sha256": text_sha256}
        final_p = self.to_dir / (ask.request_id + ".json")
        _atomic_install(final_p, payload)
        back = json.loads(final_p.read_text(encoding="utf-8"))
        if back.get("body_sha256") != text_sha256:
            raise GBridgeError(RefusalKind.TORN_REQUEST,
                               f"read-back hash mismatch for {final_p}")

    def write_reply(self, request_id: str, status: str, answer: str) -> Path:
        """Bot-side atomic reply install (tmp -> os.replace). Same contract as send().

        Direct write_text of from_gbot/<id>.json is still tolerated: poll treats a
        present-but-unparseable file as 'not yet' until the deadline. write_reply is
        the path that does not rely on that tolerance.
        """
        if not self.from_dir.is_dir():
            raise GBridgeError(RefusalKind.ROOT_MISSING,
                               f"mailbox not registered under {self.root} - THE PHONE "
                               f"IS DEAD, not 'no news'")
        # body_sha256 = sha256 of the `answer` field (not the whole JSON document).
        payload = {"gbridge": WIRE_VERSION, "request_id": request_id,
                   "status": status, "answer": answer,
                   "body_sha256": _sha256(answer)}
        final_p = self.from_dir / (request_id + ".json")
        _atomic_install(final_p, payload)
        return final_p

    def poll(self, ask: Ask, final: bool = False) -> Optional[Answer]:
        p = self.from_dir / (ask.request_id + ".json")
        attempts = _FINAL_PARSE_ATTEMPTS if final else 1
        last_err: BaseException | None = None
        for i in range(attempts):
            if not p.exists():
                return None
            try:
                return self._parse_reply(p, ask)
            except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError,
                    UnicodeError) as e:
                last_err = e
                if i + 1 < attempts:
                    time.sleep(_FINAL_PARSE_RETRY_S)
                    continue
                if final:
                    raise GBridgeError(RefusalKind.TORN_REPLY, f"{p}: {e}") from e
                return None  # the bot may still be mid-write; 'not yet' until deadline
        if final and last_err is not None:
            raise GBridgeError(RefusalKind.TORN_REPLY, f"{p}: {last_err}") from last_err
        return None

    def _parse_reply(self, p: Path, ask: Ask) -> Answer:
        raw = p.read_bytes()
        if not raw.strip():
            raise ValueError("empty reply - writer may still be in progress")
        d = json.loads(raw.decode("utf-8"))
        if d.get("gbridge") != WIRE_VERSION:
            raise ValueError(f"wire version {d.get('gbridge')!r} != {WIRE_VERSION}")
        # T1_ARCH §5: request_id must match BOTH filename stem and field.
        field_id = d.get("request_id")
        if p.stem != ask.request_id or field_id != ask.request_id or p.stem != field_id:
            raise ValueError(
                f"request_id mismatch filename={p.stem!r} field={field_id!r} "
                f"ask={ask.request_id!r}"
            )
        answer = d["answer"]
        status = d["status"]
        # body_sha256 is sha256 of the answer FIELD, not of the JSON document.
        if _sha256(answer) != d["body_sha256"]:
            raise ValueError("answer hash mismatch - half-written")
        return Answer(request_id=ask.request_id, status=status, answer=answer)


# ---------------- FALLBACK transport: xAI chat completions (API-second) ----------------
class XaiApiTransport:
    """Documented sync path (POST api.x.ai/v1/chat/completions) - same Grok model
    family, NOT the persistent team. Slice 1 ships the refusals only; live HTTP wiring
    is slice 2, after Keith provides the key. Fail-closed either way."""

    BASE_URL = "https://api.x.ai/v1/chat/completions"

    def __init__(self, model: str = "grok-4", api_key: Optional[str] = None):
        self.model = model
        self.api_key = api_key if api_key is not None else os.environ.get("XAI_API_KEY", "")

    def send(self, ask: Ask) -> None:
        if not self.api_key:
            raise GBridgeError(RefusalKind.NO_KEY, "XAI_API_KEY not set - fallback refuses")
        raise GBridgeError(RefusalKind.NOT_WIRED,
                           "live xAI call is slice 2 - this slice refuses rather than "
                           "pretending the fallback works")

    def poll(self, ask: Ask, final: bool = False) -> Optional[Answer]:
        return None


# ---------------- Loopback: no network, no bot - the selftest transport ----------------
class LoopbackTransport:
    """Echoes a hash of the request back. Exists so the slice can PROVE it runs
    end-to-end with a live value only executing code can compute (runtime-bind style),
    with zero external dependencies."""

    def __init__(self):
        self._pending: dict[str, Ask] = {}

    def send(self, ask: Ask) -> None:
        self._pending[ask.request_id] = ask

    def poll(self, ask: Ask, final: bool = False) -> Optional[Answer]:
        a = self._pending.get(ask.request_id)
        if a is None:
            return None
        return Answer(ask.request_id, "ok", "loopback:" + _sha256(a.text))


# ---------------- the bridge ----------------
class GBridge:
    def __init__(self, transport: Transport, poll_interval_s: float = 0.25):
        self.transport = transport
        self.poll_interval_s = poll_interval_s

    def ask(self, text: str, context: str = "",
            timeout_s: float = DEFAULT_TIMEOUT_S) -> Answer:
        if not text or not text.strip():
            raise GBridgeError(RefusalKind.BAD_REQUEST, "empty ask - nothing to send")
        t, off = _now()
        rid = "%d-%s" % (int(t * 1000), uuid.uuid4().hex[:12])
        ask = Ask(request_id=rid, text=text, context=context,
                  timeout_s=timeout_s, epoch=t, utc_offset_s=off)
        self.transport.send(ask)
        deadline = time.monotonic() + timeout_s
        while time.monotonic() < deadline:
            ans = self._poll_validated(ask, rid, final=False)
            if ans is not None:
                return ans
            time.sleep(self.poll_interval_s)
        ans = self._poll_validated(ask, rid, final=True)  # TORN_REPLY if present-but-invalid
        if ans is not None:
            return ans
        raise GBridgeError(RefusalKind.TIMEOUT,
                           f"no valid reply for {rid} within {timeout_s}s - request "
                           f"file left in place, a late reply stays collectible")

    def _poll_validated(self, ask: Ask, rid: str, final: bool = False) -> Optional[Answer]:
        """Single poll + validate path (deadline pass and in-loop share this)."""
        ans = self.transport.poll(ask, final=final)
        if ans is None:
            return None
        return self._validated(ans, rid)

    def _validated(self, ans: Answer, rid: str) -> Answer:
        if ans.request_id != rid:
            raise GBridgeError(RefusalKind.TORN_REPLY,
                               f"reply id {ans.request_id!r} does not match ask {rid!r}")
        if ans.status not in STATUSES:
            raise GBridgeError(RefusalKind.BAD_STATUS,
                               f"status {ans.status!r} not in {sorted(STATUSES)}")
        return ans


# ---------------- STAGE-6 runtime-binding gate ----------------
SENTINEL_NAME = ".cosmos-root.json"
PROOF_NAME = "STAGE6_GATE.json"


def _file_sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _read_sentinel(live_root: str | os.PathLike) -> dict:
    """Fail-closed identity of the runtime root. Root is HANDED IN; we do not
    walk parents or guess a drive. Existence is not identity (empty-dir scar)."""
    root = Path(live_root)
    p = root / SENTINEL_NAME
    if not p.is_file():
        raise GBridgeError(RefusalKind.ROOT_MISSING,
                           f"sentinel {p} missing - THE PHONE IS DEAD, not 'no news'")
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError, json.JSONDecodeError) as e:
        raise GBridgeError(RefusalKind.TORN_REPLY, f"sentinel unreadable: {p}: {e}") from e
    if d.get("system") != "COSMOS" or not d.get("tree_id"):
        raise GBridgeError(RefusalKind.BAD_STATUS,
                           f"sentinel {p} is not a COSMOS root (system={d.get('system')!r} "
                           f"tree_id={d.get('tree_id')!r})")
    return d


class _GateAnsweringBot(MailboxTransport):
    """Same-process team-double: after send() writes to_gbot/, the first poll
    answers atomically via write_reply. Proves the PRIMARY transport round-trip
    on real files, not LoopbackTransport."""

    def __init__(self, mail_root, nonce: str, source_sha256: str):
        super().__init__(mail_root)
        self.nonce = nonce
        self.source_sha256 = source_sha256

    def poll(self, ask, final=False):
        reply = self.from_dir / (ask.request_id + ".json")
        if not reply.exists():
            req_p = self.to_dir / (ask.request_id + ".json")
            if not req_p.is_file():
                return super().poll(ask, final)
            req = json.loads(req_p.read_text(encoding="utf-8"))
            body = "gate:%s:%s" % (req["body_sha256"], self.nonce)
            self.write_reply(ask.request_id, "ok", body)
        return super().poll(ask, final)


def run_gate(mail_root: str | os.PathLike, live_root: str | os.PathLike,
             proof_path: str | os.PathLike | None = None) -> dict:
    """Stage-6 runtime-binding: PRIMARY mailbox ask() against files on this
    tree, bound to the bytes of the executing gbridge.py and the live sentinel.

    A loopback sha256 of a constant string is NOT this gate — that value is
    computable without the tree. The emitted value is the request_id minted
    here + the source_sha256 of THIS file + the on-disk request/reply hashes
    + live_tree_id from the handed-in sentinel. An old snapshot that did not
    contain write_reply / RefusalKind / this gate cannot emit this record.
    """
    src = Path(__file__).resolve()
    source_sha256 = _file_sha256(src)
    sentinel = _read_sentinel(live_root)
    tree_id = sentinel["tree_id"]
    nonce = uuid.uuid4().hex
    text = "gbridge-s6-gate " + nonce
    text_sha256 = _sha256(text)

    mail_root = Path(mail_root)
    happy_root = mail_root / "happy"
    timeout_root = mail_root / "timeout"
    bot = _GateAnsweringBot(happy_root, nonce=nonce, source_sha256=source_sha256)
    bot.register()
    context = json.dumps({"gate": "s6", "source_sha256": source_sha256,
                          "nonce": nonce, "live_tree_id": tree_id},
                         separators=(",", ":"))
    br = GBridge(bot, poll_interval_s=0.02)
    ans = br.ask(text, context=context, timeout_s=8.0)

    req_p = bot.to_dir / (ans.request_id + ".json")
    rep_p = bot.from_dir / (ans.request_id + ".json")
    if not req_p.is_file() or not rep_p.is_file():
        raise GBridgeError(RefusalKind.TORN_REPLY,
                           "gate round-trip did not leave request+reply files on disk")
    req = json.loads(req_p.read_text(encoding="utf-8"))
    expected_answer = "gate:%s:%s" % (text_sha256, nonce)
    ok_happy = (
        ans.status == "ok"
        and ans.answer == expected_answer
        and req.get("body_sha256") == text_sha256
        and req.get("context") == context
        and req.get("text") == text
        and json.loads(req["context"]).get("source_sha256") == source_sha256
        and json.loads(req["context"]).get("live_tree_id") == tree_id
        and not (bot.from_dir / (ans.request_id + ".part")).exists()
    )

    # Negative control: empty mailbox → TIMEOUT, request file left collectible.
    empty = MailboxTransport(timeout_root)
    empty.register()
    timeout_kind = None
    timeout_detail = ""
    try:
        GBridge(empty, poll_interval_s=0.02).ask(
            "gbridge-s6-timeout " + nonce, timeout_s=0.2)
    except GBridgeError as e:
        timeout_kind = str(e.kind)
        timeout_detail = str(e)
    timeout_left = list(empty.to_dir.glob("*.json"))
    ok_timeout = timeout_kind == RefusalKind.TIMEOUT and len(timeout_left) == 1

    t, off = _now()
    rec = {
        "ok": bool(ok_happy and ok_timeout),
        "stage": 6,
        "deliverable": "gbridge",
        "agent": "G46",
        "gated_at_epoch": t,
        "utc_offset_s": off,
        "source_path": str(src),
        "source_sha256": source_sha256,
        "source_bytes": src.stat().st_size,
        "live_root": str(Path(live_root).resolve()),
        "live_tree_id": tree_id,
        "live_system": sentinel.get("system"),
        "sentinel": str((Path(live_root) / SENTINEL_NAME).resolve()),
        "mail_root": str(mail_root.resolve()),
        "python": sys.version.split()[0],
        "executable": sys.executable,
        "live_value": {
            "live_tree_id": tree_id,
            "request_id": ans.request_id,
            "nonce": nonce,
            "source_sha256": source_sha256,
            "text_sha256": text_sha256,
            "answer": ans.answer,
            "request_file_sha256": _file_sha256(req_p),
            "reply_file_sha256": _file_sha256(rep_p),
            "timeout_kind": timeout_kind,
            "timeout_request_left": str(timeout_left[0]) if timeout_left else None,
        },
        "happy": {
            "status": ans.status,
            "request_id": ans.request_id,
            "answer": ans.answer,
            "expected_answer": expected_answer,
            "request_path": str(req_p.resolve()),
            "reply_path": str(rep_p.resolve()),
            "request_file_sha256": _file_sha256(req_p),
            "reply_file_sha256": _file_sha256(rep_p),
            "text_sha256": text_sha256,
            "ok": ok_happy,
        },
        "timeout": {
            "kind": timeout_kind,
            "detail": timeout_detail,
            "request_left": str(timeout_left[0].resolve()) if timeout_left else None,
            "ok": ok_timeout,
        },
        "wire": "gbridge/%d" % WIRE_VERSION,
        "note": "rc=0 is not the gate. The live_value fields are. "
                "Loopback selftest is a green log, not this record.",
    }
    rec["emitted"] = (
        "gbridge:%(live_tree_id)s:%(request_id)s:%(nonce)s:%(source_sha256)s"
        % rec["live_value"]
    )
    dest = Path(proof_path) if proof_path else (src.parent / PROOF_NAME)
    rec["proof_path"] = str(dest.resolve())
    run_copy = happy_root / PROOF_NAME
    rec["run_copy"] = str(run_copy.resolve())
    _atomic_install(dest, rec)
    _atomic_install(run_copy, rec)
    return rec


# ---------------- CLI ----------------
def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(prog="gbridge",
                                 description="Synchronous COW <-> GrokBot-team ask")
    sub = ap.add_subparsers(dest="verb", required=True)

    a = sub.add_parser("ask", help="block on the file mailbox until the team answers")
    a.add_argument("text")
    a.add_argument("--root", required=True, help="mail root (handed in, never resolved)")
    a.add_argument("--context", default="")
    a.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT_S)
    a.add_argument("--register", action="store_true",
                   help="create to_gbot/ and from_gbot/ first (explicit, one-time)")

    sub.add_parser("selftest", help="loopback round-trip, no network, emits a live value")

    g = sub.add_parser("gate", help="stage-6 runtime-binding: mailbox round-trip + sentinel")
    g.add_argument("--root", required=True,
                   help="mail root (handed in; gate writes happy/ and timeout/ under it)")
    g.add_argument("--live-root", required=True,
                   help="COSMOS runtime root (handed in; sentinel is read, never resolved)")
    g.add_argument("--proof", default="",
                   help="proof JSON path (default: STAGE6_GATE.json beside this module)")

    ns = ap.parse_args(argv)

    if ns.verb == "selftest":
        br = GBridge(LoopbackTransport(), poll_interval_s=0.01)
        ans = br.ask("gbridge selftest")
        expected = "loopback:" + _sha256("gbridge selftest")
        ok = ans.answer == expected
        print(json.dumps({"selftest": "ok" if ok else "FAIL",
                          "live_value": ans.answer, "request_id": ans.request_id,
                          "note": "loopback selftest is a green log, not stage 6"}))
        return 0 if ok else 1

    if ns.verb == "gate":
        try:
            rec = run_gate(ns.root, ns.live_root,
                           proof_path=ns.proof or None)
        except GBridgeError as e:
            print(json.dumps({"ok": False, "status": "refused",
                              "kind": str(e.kind), "detail": str(e)}))
            return 2
        print(json.dumps({
            "ok": rec["ok"],
            "stage": 6,
            "proof_path": rec["proof_path"],
            "emitted": rec["emitted"],
            "live_value": rec["live_value"],
        }, indent=1))
        return 0 if rec["ok"] else 1

    tr = MailboxTransport(ns.root)
    if ns.register:
        tr.register()
    br = GBridge(tr)
    try:
        ans = br.ask(ns.text, context=ns.context, timeout_s=ns.timeout)
    except GBridgeError as e:
        print(json.dumps({"status": "refused", "kind": e.kind, "detail": str(e)}))
        return 2
    print(json.dumps({"status": ans.status, "request_id": ans.request_id,
                      "answer": ans.answer}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
