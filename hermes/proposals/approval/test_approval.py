"""Refusal codes, the allow path, and the TTL cap for the approval gate."""

from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import cast

import pytest

from approval import (
    ALLOW,
    CONFIRM,
    FIELD_CAP,
    GRANT_TTL_CAP,
    HARDLINE,
    REQUEST_TTL_CAP,
    RETRY_FAILURE,
    SCHEMA,
    ApprovalGate,
    LedgerEvent,
    canonical_json,
)
from cosmos_hermes import Refuse

PUSH: dict[str, object] = {"kind": "shell", "command": "git push origin main"}


def scratch() -> Path:
    """Private directory. The shared pytest basetemp on this machine is not writable."""
    return Path(tempfile.mkdtemp(prefix="hermes-approval-"))


def make(
    tmp_path: Path,
    *,
    mode: str = "enforce",
    request_ttl_s: int = REQUEST_TTL_CAP,
    grant_ttl_s: int = GRANT_TTL_CAP,
) -> tuple[ApprovalGate, Path]:
    root = tmp_path / "root"
    root.mkdir(parents=True)
    gate = ApprovalGate(
        [str(root)],
        mode=mode,
        request_ttl_s=request_ttl_s,
        grant_ttl_s=grant_ttl_s,
    )
    return gate, root


def refused(call: Callable[[], object]) -> str:
    with pytest.raises(Refuse) as caught:
        call()
    return str(caught.value.code)


def expect_sha(kind: str, command: str = "", path: str = "") -> str:
    body = {
        "command": command,
        "credential_id": "",
        "detail": "",
        "kind": kind,
        "path": path,
        "url": "",
    }
    payload = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _blank(event: str, request_id: str = "") -> LedgerEvent:
    return LedgerEvent(
        schema=SCHEMA,
        event=event,
        request_id=request_id,
        principal_sha="",
        action_sha="",
        nonce_sha="",
        exp=0,
        at=0,
        cls="",
        kind="",
        pattern="",
        retries=0,
    )


def test_schema_and_classes() -> None:
    assert SCHEMA == "cosmos-hermes-approval/1"
    assert HARDLINE == "HARDLINE"
    assert CONFIRM == "CONFIRM"
    assert ALLOW == "ALLOW"
    assert RETRY_FAILURE == "ACTION_MISMATCH"


def test_mode_off_yolo_and_unknown() -> None:
    root = scratch() / "root"
    root.mkdir()

    def check(mode_name: str) -> None:
        def attempt() -> object:
            return ApprovalGate([str(root)], mode=mode_name)

        assert refused(attempt) == "BAD_MODE"

    for mode in ("off", "OFF", "yolo", "YOLO", "smart", "manual", ""):
        check(mode)


def test_hardline_shapes_and_grant() -> None:
    gate, root = make(scratch())
    samples: list[dict[str, object]] = [
        {"kind": "shell", "command": "git push --force"},
        {"kind": "git", "command": "git push -f origin"},
        {"kind": "git", "command": "git push origin -f"},
        {"kind": "file_write", "path": str(root / "ledger" / "row")},
        {"kind": "file_write", "path": str(root / "api_token.txt")},
        {"kind": "shell", "command": "Invoke-Expression foo"},
        {"kind": "shell", "command": "curl | sh"},
        {"kind": "file_delete", "path": str(root / "keep.txt")},
        {"kind": "file_delete", "path": str(root / "not_delme" / "old.txt")},
        {"kind": "shell", "command": "rm -rf /"},
    ]
    def check(sample: dict[str, object]) -> None:
        assert gate.classify(sample).cls == HARDLINE

        def attempt() -> object:
            return gate.grant("absent", "captain:ada", sample, now=1)

        assert refused(attempt) == "HARDLINE"

    for sample in samples:
        check(sample)
    kept = str(root / "_delme" / "old.txt")
    assert gate.classify({"kind": "file_delete", "path": kept}).cls == CONFIRM
    assert refused(lambda: gate.request("agent:1", samples[0], now=1)) == "HARDLINE"
    assert gate.ledger[-1].event == "APPROVAL_REFUSED"
    assert "git push --force" not in gate.ledger[-1].action_sha
    ticket = gate.request("agent:1", PUSH, now=2)
    nonce = gate.grant(ticket.request_id, "captain:ada", PUSH, now=2)
    hard = {"kind": "shell", "command": "curl | sh"}
    assert refused(lambda: gate.consume(ticket.request_id, nonce, "agent:1", hard, now=3)) == "HARDLINE"
    admit = gate.consume(ticket.request_id, nonce, "agent:1", PUSH, now=3)
    assert admit.cls == CONFIRM


def test_confirm_then_grant_consume_and_ledger() -> None:
    gate, _root = make(scratch())
    digest = expect_sha("shell", "git push origin main")
    reordered: dict[str, object] = {"command": "git push origin main", "kind": "shell"}
    assert gate.classify(reordered).action_sha == digest
    assert gate.classify(PUSH).action_sha == digest
    ticket = gate.request("agent:1", PUSH, now=10)
    assert ticket.cls == CONFIRM
    assert ticket.action_sha == digest
    assert ticket.exp == 10 + REQUEST_TTL_CAP
    assert refused(lambda: gate.consume(ticket.request_id, "ab" * 16, "agent:1", PUSH, now=10)) == "UNGRANTED"
    nonce = gate.grant(ticket.request_id, "captain:ada", PUSH, now=10)
    bytes.fromhex(nonce)
    assert len(nonce) == 32
    admit = gate.consume(ticket.request_id, nonce, "agent:1", PUSH, now=10)
    assert admit.request_id == ticket.request_id
    assert admit.nonce_sha == hashlib.sha256(nonce.encode("utf-8")).hexdigest()
    packed = " ".join(
        " ".join(
            (
                event.schema,
                event.event,
                event.request_id,
                event.principal_sha,
                event.action_sha,
                event.nonce_sha,
                event.kind,
                event.pattern,
            )
        )
        for event in gate.ledger
    )
    assert SCHEMA in packed
    assert nonce not in packed
    assert "git push origin main" not in packed
    assert admit.nonce_sha in packed
    assert digest in packed
    assert refused(lambda: gate.consume(ticket.request_id, nonce, "agent:1", PUSH, now=11)) == "REPLAY"


def test_const_eq_of_canonical_hashes(monkeypatch: pytest.MonkeyPatch) -> None:
    gate, _root = make(scratch())
    ticket = gate.request("agent:1", PUSH, now=10)
    nonce = gate.grant(ticket.request_id, "captain:ada", PUSH, now=10)
    seen: list[tuple[str, str]] = []
    real = canonical_json.__module__

    def wrapped(left: str, right: str) -> bool:
        seen.append((left, right))
        from cosmos_hermes import const_eq

        return const_eq(left, right)

    assert real == "approval"
    monkeypatch.setattr("approval.const_eq", wrapped)
    gate.consume(ticket.request_id, nonce, "agent:1", PUSH, now=11)
    assert any(left == ticket.action_sha and right == ticket.action_sha for left, right in seen)


def test_expiry_is_strictly_after_exp() -> None:
    gate, _root = make(scratch(), request_ttl_s=30, grant_ttl_s=10)
    first = gate.request("agent:1", PUSH, now=100)
    assert first.exp == 130
    gate.grant(first.request_id, "captain:ada", PUSH, now=130)
    second = gate.request("agent:1", PUSH, now=100)
    assert refused(lambda: gate.grant(second.request_id, "captain:ada", PUSH, now=131)) == "EXPIRED"
    third = gate.request("agent:1", PUSH, now=50)
    nonce = gate.grant(third.request_id, "captain:ada", PUSH, now=50)
    gate.consume(third.request_id, nonce, "agent:1", PUSH, now=60)
    fourth = gate.request("agent:1", PUSH, now=50)
    late = gate.grant(fourth.request_id, "captain:ada", PUSH, now=50)
    assert refused(lambda: gate.consume(fourth.request_id, late, "agent:1", PUSH, now=61)) == "EXPIRED"


def test_self_and_not_approver() -> None:
    gate, _root = make(scratch())
    own = gate.request("captain:ada", PUSH, now=1)
    assert refused(lambda: gate.grant(own.request_id, "captain:ada", PUSH, now=1)) == "SELF"
    assert refused(lambda: gate.deny(own.request_id, "captain:ada", now=1)) == "SELF"
    other = gate.request("agent:1", PUSH, now=1)
    assert refused(lambda: gate.grant(other.request_id, "agent:2", PUSH, now=1)) == "NOT_APPROVER"
    assert refused(lambda: gate.allow_rule("captain:ada", "shell", "echo *", "captain:ada", now=1, ttl_s=10)) == "SELF"
    assert refused(lambda: gate.allow_rule("agent:1", "shell", "echo *", "agent:2", now=1, ttl_s=10)) == "NOT_APPROVER"


def test_mismatch_retry_then_cap() -> None:
    gate, _root = make(scratch())
    ticket = gate.request("agent:1", PUSH, now=1)
    nonce = gate.grant(ticket.request_id, "captain:ada", PUSH, now=1)
    wrong: dict[str, object] = {"kind": "shell", "command": "git status"}
    assert refused(lambda: gate.consume(ticket.request_id, nonce, "agent:1", wrong, now=2)) == "ACTION_MISMATCH"
    gate.consume(ticket.request_id, nonce, "agent:1", PUSH, now=2)
    again = gate.request("agent:1", PUSH, now=3)
    nonce_b = gate.grant(again.request_id, "captain:ada", PUSH, now=3)
    assert refused(lambda: gate.consume(again.request_id, nonce_b, "agent:1", wrong, now=4)) == "ACTION_MISMATCH"
    assert refused(lambda: gate.consume(again.request_id, nonce_b, "agent:1", wrong, now=4)) == "RETRY_CAP"
    assert refused(lambda: gate.consume(again.request_id, nonce_b, "agent:1", PUSH, now=4)) == "RETRY_CAP"


def test_bad_nonce_does_not_burn_grant() -> None:
    gate, _root = make(scratch())
    ticket = gate.request("agent:1", PUSH, now=1)
    nonce = gate.grant(ticket.request_id, "captain:ada", PUSH, now=1)
    assert refused(lambda: gate.consume(ticket.request_id, "00" * 16, "agent:1", PUSH, now=1)) == "BAD_NONCE"
    gate.consume(ticket.request_id, nonce, "agent:1", PUSH, now=1)


def test_deny_already_and_owner() -> None:
    gate, _root = make(scratch())
    denied = gate.request("agent:1", PUSH, now=1)
    gate.deny(denied.request_id, "captain:ada", now=1)
    assert refused(lambda: gate.consume(denied.request_id, "ab", "agent:1", PUSH, now=1)) == "DENIED"
    assert refused(lambda: gate.grant(denied.request_id, "captain:ada", PUSH, now=1)) == "ALREADY"
    live = gate.request("agent:1", PUSH, now=1)
    nonce = gate.grant(live.request_id, "captain:ada", PUSH, now=1)
    assert refused(lambda: gate.grant(live.request_id, "captain:bea", PUSH, now=1)) == "ALREADY"
    assert refused(lambda: gate.consume(live.request_id, nonce, "agent:2", PUSH, now=1)) == "NOT_OWNER"
    assert refused(lambda: gate.grant("missing", "captain:ada", PUSH, now=1)) == "UNGRANTED"
    assert refused(lambda: gate.consume("missing", nonce, "agent:1", PUSH, now=1)) == "UNGRANTED"


def test_grant_mismatch_stays_pending() -> None:
    gate, _root = make(scratch())
    ticket = gate.request("agent:1", PUSH, now=1)
    other: dict[str, object] = {"kind": "shell", "command": "git status"}
    assert refused(lambda: gate.grant(ticket.request_id, "captain:ada", other, now=1)) == "ACTION_MISMATCH"
    gate.grant(ticket.request_id, "captain:ada", PUSH, now=1)


def test_empty_allow_missing_cred_and_unclassified() -> None:
    gate, _root = make(scratch())
    echo: dict[str, object] = {"kind": "shell", "command": "echo hi"}
    assert gate.classify(echo, "agent:1", now=1).cls == CONFIRM
    assert refused(lambda: gate.authorize("agent:1", echo, now=1)) == "EMPTY_ALLOW"
    http: dict[str, object] = {"kind": "http", "url": "https://example.com/a"}
    assert refused(lambda: gate.classify(http)) == "MISSING_CREDENTIAL"
    assert refused(lambda: gate.classify({"kind": "rm"})) == "UNCLASSIFIED"
    assert refused(lambda: gate.classify(cast(Mapping[str, object], ["no"]))) == "BAD_ACTION"
    assert refused(lambda: canonical_json({"kind": "shell"})) == "BAD_ACTION"
    assert refused(lambda: gate.request("", echo, now=1)) == "BAD_ACTOR"
    bad_id: dict[str, object] = {"kind": "shell", "command": "echo hi", "credential_id": "has space"}
    assert refused(lambda: gate.classify(bad_id)) == "BAD_CREDENTIAL"


def test_allow_success_and_secret_repr() -> None:
    gate, root = make(scratch())
    gate.allow_rule("agent:1", "shell", "shell echo *", "captain:ada", now=10, ttl_s=5)
    echo: dict[str, object] = {"kind": "shell", "command": "echo hi"}
    assert gate.classify(echo, "agent:1", now=15).cls == ALLOW
    assert gate.classify(echo, "agent:1", now=16).cls == CONFIRM
    verdict = gate.authorize("agent:1", echo, now=15)
    assert verdict.cls == ALLOW
    ticket = gate.request("agent:1", echo, now=15)
    assert ticket.cls == ALLOW
    assert ticket.request_id == ""
    hidden: dict[str, object] = {"kind": "shell", "command": "echo hi\u200b"}
    assert "hidden-text" in gate.classify(hidden, "agent:1", now=15).rules
    assert gate.classify(hidden, "agent:1", now=15).cls == CONFIRM
    paid: dict[str, object] = {
        "kind": "http",
        "url": "https://example.com/a",
        "credential_id": "cred.http",
    }
    gate.allow_rule("agent:1", "http", "*", "captain:ada", now=10, ttl_s=20)
    assert gate.classify(paid, "agent:1", now=11).cls == CONFIRM
    kept = str(root / "_delme" / "old.txt")
    gate.allow_rule("agent:1", "file_delete", "file_delete *", "captain:ada", now=10, ttl_s=20)
    assert gate.authorize("agent:1", {"kind": "file_delete", "path": kept}, now=11).cls == ALLOW
    assert refused(lambda: gate.allow_rule("agent:1", "shell", "", "captain:ada", now=1, ttl_s=5)) == "BAD_PATTERN"
    assert refused(lambda: gate.authorize("agent:1", PUSH, now=11)) == "NOT_LISTED"
    secret = "echo sk-abcdefghij"
    assert refused(lambda: gate.classify({"kind": "shell", "command": secret})) == "SECRET"
    with pytest.raises(Refuse) as caught:
        gate.classify({"kind": "shell", "command": secret})
    assert "sk-" not in str(caught.value)
    assert "sk-" not in repr(caught.value)
    blob = " ".join(repr(item) for item in (gate, gate.policy, verdict, ticket, gate.ledger[0]))
    assert "sk-" not in blob
    assert "Bearer " not in blob
    assert "api_key=" not in blob


def test_cap_ignores_higher_ask() -> None:
    gate, _root = make(scratch(), request_ttl_s=50_000, grant_ttl_s=9_999)
    assert gate.policy.request_ttl_s == REQUEST_TTL_CAP
    assert gate.policy.grant_ttl_s == GRANT_TTL_CAP
    assert gate.policy.asked_request_ttl_s == 50_000
    assert gate.policy.asked_grant_ttl_s == 9_999
    assert gate.policy.request_capped is True
    assert gate.policy.grant_capped is True
    ticket = gate.request("agent:1", PUSH, now=5)
    assert ticket.exp == 5 + REQUEST_TTL_CAP
    assert ticket.applied_ttl_s == REQUEST_TTL_CAP
    assert ticket.capped is True
    nonce = gate.grant(ticket.request_id, "captain:ada", PUSH, now=5)
    granted = [event for event in gate.ledger if event.event == "APPROVAL_GRANTED"]
    assert granted[0].exp == 5 + GRANT_TTL_CAP
    gate.consume(ticket.request_id, nonce, "agent:1", PUSH, now=5 + GRANT_TTL_CAP)
    plain, _root2 = make(scratch() / "plain", request_ttl_s=30, grant_ttl_s=10)
    assert plain.policy.request_capped is False
    assert plain.request("agent:1", PUSH, now=5).exp == 35


def test_rebuild_and_bad_event() -> None:
    gate, _root = make(scratch())
    ticket = gate.request("agent:1", PUSH, now=10)
    nonce = gate.grant(ticket.request_id, "captain:ada", PUSH, now=10)
    saved = gate.ledger
    fresh, _root = make(scratch() / "fresh")
    fresh.rebuild(saved)
    admit = fresh.consume(ticket.request_id, nonce, "agent:1", PUSH, now=11)
    assert admit.action_sha == ticket.action_sha
    assert all(event.nonce_sha != nonce for event in fresh.ledger)
    before = gate.ledger
    assert refused(lambda: gate.rebuild((_blank("NOPE"),))) == "BAD_EVENT"
    assert gate.ledger == before
    assert refused(lambda: gate.rebuild((_blank("APPROVAL_GRANTED", "ap-missing"),))) == "BAD_EVENT"
    assert gate.ledger == before


def test_bounds_and_jail() -> None:
    gate, root = make(scratch())
    huge: dict[str, object] = {"kind": "shell", "command": "x" * (FIELD_CAP + 1)}
    assert refused(lambda: gate.classify(huge)) == "OVERSIZE"
    assert refused(lambda: gate.classify({"kind": "shell", "command": "a\x00b"})) == "NULL_BYTE"
    bad_type: dict[str, object] = {"kind": "shell", "command": 1}
    assert refused(lambda: gate.classify(bad_type)) == "NOT_TEXT"
    assert refused(lambda: gate.classify({"kind": "shell", "command": "echo hi"}, now=cast(int, True))) == "NOT_INT"
    assert refused(lambda: ApprovalGate([str(root)], request_ttl_s=0)) == "OUT_OF_RANGE"
    assert refused(lambda: ApprovalGate([])) == "NO_GRANT"
    relative: dict[str, object] = {"kind": "file_write", "path": "note.txt"}
    assert refused(lambda: gate.request("agent:1", relative, now=1)) == "RELATIVE_PATH"
    outside: dict[str, object] = {"kind": "file_write", "path": str(scratch() / "other" / "a.txt")}
    assert refused(lambda: gate.request("agent:1", outside, now=1)) == "OUTSIDE_GRANT"
    inside: dict[str, object] = {"kind": "file_write", "path": str(root / "note.txt")}
    assert gate.request("agent:1", inside, now=1).cls == CONFIRM


def test_allow_cannot_cover_hardline() -> None:
    gate, _root = make(scratch())
    gate.allow_rule("agent:1", "shell", "*", "captain:ada", now=1, ttl_s=30)
    force: dict[str, object] = {"kind": "shell", "command": "git push --force"}
    assert gate.classify(force, "agent:1", now=2).cls == HARDLINE
    assert "Bearer " not in repr(gate)
    assert "api_key=" not in repr(gate.policy)


def test_silence_deadline_retry_and_empty_allow() -> None:
    base = scratch()
    try:
        gate, root = make(base)
        echo: dict[str, object] = {"kind": "shell", "command": "echo hi"}
        wipe: dict[str, object] = {"kind": "shell", "command": "rm -rf /"}
        assert refused(lambda: gate.authorize("agent:ada", wipe, now=1)) == "HARDLINE"
        gate.allow_rule("agent:ada", "shell", "shell echo *", "captain:mina", now=10, ttl_s=5)
        assert gate.authorize("agent:ada", echo, now=15).cls == ALLOW
        saved = gate.ledger
        fresh, _fresh_root = make(base / "fresh")
        fresh.rebuild(saved)
        assert fresh.classify(echo, "agent:ada", now=15).cls == ALLOW
        assert refused(lambda: gate.authorize("agent:ada", echo, now=16)) == "EMPTY_ALLOW"
        before = gate.ledger
        assert refused(lambda: gate.rebuild((_blank("NOPE"),))) == "BAD_EVENT"
        assert gate.ledger == before
        assert gate.classify(echo, "agent:ada", now=15).cls == ALLOW
        mixed = str(root / "_Delme" / "old.txt")
        assert gate.classify({"kind": "file_delete", "path": mixed}).cls == CONFIRM
        assert refused(lambda: gate.classify({"kind": "file_read"})) == "BAD_ACTION"
        outside = str(base / "other" / "note.txt")
        outside_read: dict[str, object] = {"kind": "file_read", "path": outside}
        assert refused(lambda: gate.request("agent:ada", outside_read, now=20)) == "OUTSIDE_GRANT"
        note = str(root / "note.txt")
        read: dict[str, object] = {"kind": "file_read", "path": note, "detail": "read note"}
        assert gate.classify(read, "agent:ada", now=20).cls == CONFIRM
        early = gate.request("agent:ada", read, now=20, deadline=30)
        assert early.exp == 30
        assert early.applied_ttl_s == 10
        assert refused(lambda: gate.unanswered(early.request_id, now=30)) == "NOT_DUE"
        nonce = gate.grant(early.request_id, "captain:mina", read, now=30)
        admit = gate.consume(early.request_id, nonce, "agent:ada", read, now=31)
        assert admit.cls == CONFIRM
        high = gate.request("agent:ada", PUSH, now=40, deadline=50_000)
        assert high.exp == 40 + gate.policy.request_ttl_s
        assert high.applied_ttl_s == gate.policy.request_ttl_s
        assert high.capped is True
        assert refused(lambda: gate.request("agent:ada", PUSH, now=40, deadline=40)) == "OUT_OF_RANGE"
        assert refused(lambda: gate.request("agent:ada", PUSH, now=40, deadline=cast(int, True))) == "NOT_INT"
        pending = gate.request("agent:ada", PUSH, now=50, deadline=80)
        assert refused(lambda: gate.consume(pending.request_id, "ab", "agent:ada", PUSH, now=81)) == "DENIED"
        assert refused(lambda: gate.consume(pending.request_id, "ab", "agent:ada", PUSH, now=82)) == "DENIED"
        denied = [
            event
            for event in gate.ledger
            if event.event == "APPROVAL_DENIED" and event.request_id == pending.request_id
        ]
        assert len(denied) == 1
        assert denied[0].pattern == "timeout"
        assert refused(lambda: gate.grant(pending.request_id, "captain:mina", PUSH, now=82)) == "ALREADY"
        again = gate.request("agent:1", PUSH, now=90, deadline=100)
        wrong: dict[str, object] = {"kind": "shell", "command": "git status"}
        assert refused(lambda: gate.grant(again.request_id, "captain:mina", wrong, now=90)) == "ACTION_MISMATCH"
        assert refused(lambda: gate.grant(again.request_id, "captain:mina", wrong, now=90)) == "RETRY_CAP"
        assert refused(lambda: gate.grant(again.request_id, "captain:mina", PUSH, now=90)) == "RETRY_CAP"
    finally:
        shutil.rmtree(base, ignore_errors=True)


def test_example_approval() -> None:
    base = scratch()
    try:
        root = base / "desk"
        root.mkdir()
        note = str(root / "note.txt")
        when = 1_700_000_000

        def once() -> tuple[object, ...]:
            gate = ApprovalGate([str(root)])
            yolo = refused(lambda: ApprovalGate([str(root)], mode="yolo"))
            off = refused(lambda: ApprovalGate([str(root)], mode="off"))
            shell: dict[str, object] = {"kind": "shell", "command": "Get-ChildItem"}
            empty = refused(lambda: gate.authorize("agent:ada", shell, now=when))
            read: dict[str, object] = {
                "kind": "file_read",
                "path": note,
                "detail": "read note",
            }
            seen = gate.classify(read, "agent:ada", now=when)
            ticket = gate.request("agent:ada", read, now=when)
            nonce = gate.grant(ticket.request_id, "captain:mina", read, now=when)
            admit = gate.consume(ticket.request_id, nonce, "agent:ada", read, now=when + 1)
            pending_action: dict[str, object] = {"kind": "shell", "command": "git status"}
            waiting = gate.request(
                "agent:ada",
                pending_action,
                now=when + 10,
                deadline=when + 70,
            )
            denied = refused(lambda: gate.unanswered(waiting.request_id, now=waiting.exp + 1))
            events = tuple(event.event for event in gate.ledger)
            return (
                yolo,
                off,
                empty,
                seen.cls,
                admit.cls,
                admit.action_sha == ticket.action_sha,
                waiting.exp,
                denied,
                events,
            )

        first = once()
        second = once()
        assert first == second
        assert first == (
            "BAD_MODE",
            "BAD_MODE",
            "EMPTY_ALLOW",
            CONFIRM,
            CONFIRM,
            True,
            when + 70,
            "DENIED",
            (
                "APPROVAL_REQUESTED",
                "APPROVAL_GRANTED",
                "APPROVAL_CONSUMED",
                "APPROVAL_REQUESTED",
                "APPROVAL_DENIED",
            ),
        )
    finally:
        shutil.rmtree(base, ignore_errors=True)
