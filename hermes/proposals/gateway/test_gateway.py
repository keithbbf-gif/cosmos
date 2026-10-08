"""Idempotent ingest, signature and fence refusal, drain, and the policy cap."""

from __future__ import annotations

import threading
from collections.abc import Callable
from dataclasses import replace

import pytest

from cosmos_hermes import Refuse
from gateway import (
    _GENESIS,
    FENCE_WINDOW,
    MESSAGE_CAP,
    PLATFORM_CAP,
    QUEUE_CAP,
    SCHEMA,
    Delivery,
    Gateway,
    IngestResult,
    Platform,
    Policy,
    Receipt,
    Snapshot,
    _link,
    rebuild,
    sign,
)

_NOW = 1_720_000_000
_SIGNER = "cred-mira-chat"
_PLATFORM = "telegram"
_CARD = "Mira moved the porch-light card to today's list."
_NOTE = "Leave a note: the porch light stays on for the evening session."


def refusal(call: Callable[[], object]) -> Refuse:
    with pytest.raises(Refuse) as caught:
        call()
    return caught.value


def _at(rows: tuple[Receipt, ...], index: int) -> Receipt:
    return rows[index]


def _platform_at(rows: tuple[Platform, ...], index: int) -> Platform:
    return rows[index]


def post(
    gate: Gateway,
    message_id: str,
    message: str,
    fence: int = _NOW,
    now: int = _NOW,
    platform: str = _PLATFORM,
    signer: str = _SIGNER,
) -> IngestResult:
    return gate.ingest(
        platform,
        message_id,
        message,
        sign(signer, platform, message_id, message, fence),
        fence,
        now,
    )


def _flip(signature: str) -> str:
    replacement = "0" if signature[-1] != "0" else "1"
    return signature[:-1] + replacement


def _hand(
    platform: str,
    signer: str,
    message_id: str,
    message: str,
    fence: int,
    index: int,
    prev: str,
) -> Receipt:
    signature = sign(signer, platform, message_id, message, fence)
    return Receipt(
        schema=SCHEMA,
        platform=platform,
        message_id=message_id,
        message=message,
        fence=fence,
        signature=signature,
        index=index,
        prev=prev,
        sha=_link(prev, platform, message_id, fence, signature),
    )


def test_schema_starts_running_and_instances_are_isolated() -> None:
    assert SCHEMA == "cosmos-hermes-gateway/1"
    assert FENCE_WINDOW == 300
    gate = Gateway()
    other = Gateway()
    assert gate.draining is False
    assert gate.policy.message_cap == MESSAGE_CAP
    assert gate.policy.queue_cap == QUEUE_CAP
    assert gate.policy.platform_cap == PLATFORM_CAP
    assert gate.policy.message_capped is False
    assert gate.policy.asked_message_cap == MESSAGE_CAP
    snap = gate.status()
    assert snap.schema == SCHEMA
    assert snap.state == "running"
    assert snap.platforms == ()
    assert snap.accepted == 0
    assert snap.deliveries == 0
    gate.register_platform(_PLATFORM, _SIGNER)
    assert other.platforms == ()

    def unknown() -> IngestResult:
        return post(other, "msg-card-14", _CARD)

    assert refusal(unknown).code == "UNKNOWN_PLATFORM"
    assert other.messages == ()


def test_example_gateway() -> None:
    """Three telegram events. The middle one repeats the porch-light card.

    Two unique receipts and one replay mark. A second run matches the first.
    """

    def story() -> tuple[IngestResult, IngestResult, IngestResult, Delivery, Snapshot]:
        gate = Gateway()
        gate.register_platform(_PLATFORM, _SIGNER)
        first = post(gate, "msg-card-14", _CARD)
        middle = post(gate, "msg-card-14", _CARD)
        assert middle.receipt is first.receipt
        assert middle.replay is True
        assert len(gate.messages) == 1
        assert gate.status().accepted == 1
        second = post(gate, "msg-note-15", _NOTE, fence=_NOW + 20, now=_NOW + 20)
        sent = gate.deliver(_PLATFORM, "The porch light stays on for the session.")
        assert len(gate.messages) == 2
        assert gate.status().accepted == 2
        return (first, middle, second, sent, gate.snapshot())

    left = story()
    right = story()
    assert left == right
    first, middle, second, sent, snap = left
    assert (first.replay, middle.replay, second.replay) == (False, True, False)
    assert middle.receipt is first.receipt
    assert first.receipt.message_id == "msg-card-14"
    assert second.receipt.message_id == "msg-note-15"
    assert first.receipt.message == _CARD
    assert second.receipt.message == _NOTE
    assert first.receipt.index == 0
    assert middle.receipt.index == 0
    assert second.receipt.index == 1
    assert first.receipt is not second.receipt
    assert snap.schema == SCHEMA
    assert snap.state == "running"
    assert snap.accepted == 2
    assert len(snap.receipts) == 2
    assert len(snap.deliveries) == 1
    assert sent.target == _PLATFORM
    assert sent.index == 0
    assert _at(snap.receipts, 0).prev == _GENESIS
    assert _at(snap.receipts, 1).prev == _at(snap.receipts, 0).sha
    assert rebuild(snap) == snap
    unique = 0
    for result in (first, middle, second):
        if not result.replay:
            unique += 1
    assert unique == 2


def test_replay_does_not_double_apply() -> None:
    gate = Gateway()
    gate.register_platform(_PLATFORM, _SIGNER)
    gate.register_platform("discord", "cred-mira-discord")
    first = post(gate, "msg-card-14", _CARD)
    assert first.schema == SCHEMA
    assert first.replay is False
    assert _at(gate.messages, 0) is first.receipt
    late_now = _NOW + FENCE_WINDOW + 50
    late = post(gate, "msg-card-14", _CARD, fence=_NOW, now=late_now)
    assert late.replay is True
    assert late.receipt is first.receipt
    assert len(gate.messages) == 1
    assert gate.status().accepted == 1

    def changed() -> IngestResult:
        return post(gate, "msg-card-14", _NOTE, fence=_NOW + 5, now=_NOW + 5)

    assert refusal(changed).code == "MISMATCH"
    assert len(gate.messages) == 1
    assert first.receipt.message == _CARD

    def other_platform() -> IngestResult:
        return post(
            gate,
            "msg-card-14",
            _CARD,
            fence=_NOW,
            now=_NOW,
            platform="discord",
            signer="cred-mira-discord",
        )

    assert refusal(other_platform).code == "MISMATCH"
    assert gate.platforms == (_PLATFORM, "discord")
    assert len(gate.messages) == 1

    def stale_new() -> IngestResult:
        return post(gate, "msg-note-15", _NOTE, fence=_NOW, now=late_now)

    stale = refusal(stale_new)
    assert stale.code == "STALE"
    assert stale.detail == "window"
    assert len(gate.messages) == 1

    def backward() -> IngestResult:
        return post(gate, "msg-note-15", _NOTE, fence=_NOW - 1, now=_NOW)

    ordered = refusal(backward)
    assert ordered.code == "STALE"
    assert ordered.detail == "order"
    assert len(gate.messages) == 1
    fresh = post(gate, "msg-note-15", _NOTE, fence=_NOW + FENCE_WINDOW, now=_NOW)
    assert fresh.replay is False
    assert fresh.receipt.index == 1
    assert len(gate.messages) == 2
    again = gate.register_platform(_PLATFORM, _SIGNER)
    assert again is _platform_at(gate.snapshot().platforms, 0)

    def clash() -> Platform:
        return gate.register_platform(_PLATFORM, "cred-other-chat")

    assert refusal(clash).code == "MISMATCH"
    assert gate.platforms == (_PLATFORM, "discord")


def test_signature_and_fence_refuse() -> None:
    gate = Gateway()
    gate.register_platform(_PLATFORM, _SIGNER)
    good = sign(_SIGNER, _PLATFORM, "msg-card-14", _CARD, _NOW)

    def bad_sig() -> IngestResult:
        return gate.ingest(_PLATFORM, "msg-card-14", _CARD, _flip(good), _NOW, _NOW)

    assert refusal(bad_sig).code == "BAD_SIGNATURE"

    def shaped() -> IngestResult:
        return gate.ingest(_PLATFORM, "msg-card-14", _CARD, "zz", _NOW, _NOW)

    assert refusal(shaped).code == "BAD_SIGNATURE"

    def not_hex() -> IngestResult:
        return gate.ingest(_PLATFORM, "msg-card-14", _CARD, 12, _NOW, _NOW)

    assert refusal(not_hex).code == "BAD_SIGNATURE"

    def bad_fence() -> IngestResult:
        return gate.ingest(_PLATFORM, "msg-card-14", _CARD, good, "1700", _NOW)

    assert refusal(bad_fence).code == "BAD_FENCE"

    def bool_fence() -> IngestResult:
        return gate.ingest(_PLATFORM, "msg-card-14", _CARD, good, True, _NOW)

    assert refusal(bool_fence).code == "BAD_FENCE"

    def negative_fence() -> IngestResult:
        return gate.ingest(_PLATFORM, "msg-card-14", _CARD, good, -1, _NOW)

    assert refusal(negative_fence).code == "BAD_FENCE"
    assert gate.messages == ()
    edge = post(gate, "msg-card-14", _CARD, fence=_NOW + FENCE_WINDOW, now=_NOW)
    assert edge.replay is False

    def too_far() -> IngestResult:
        return post(gate, "msg-note-15", _NOTE, fence=_NOW + FENCE_WINDOW + 1, now=_NOW)

    assert refusal(too_far).code == "STALE"
    assert len(gate.messages) == 1


def test_shutdown_drains_ingest_and_still_delivers() -> None:
    gate = Gateway()
    gate.register_platform(_PLATFORM, _SIGNER)
    first = post(gate, "msg-card-14", _CARD)
    done = gate.shutdown()
    assert done.schema == SCHEMA
    assert done.state == "draining"
    assert done.accepted == 1
    assert gate.draining is True
    assert gate.status().state == "draining"

    def replay_while_draining() -> IngestResult:
        return post(gate, "msg-card-14", _CARD)

    assert refusal(replay_while_draining).code == "DRAINING"

    def garbage() -> IngestResult:
        return gate.ingest(1, 1, 1, 1, 1, 1)

    assert refusal(garbage).code == "DRAINING"

    def register_while_draining() -> Platform:
        return gate.register_platform("discord", "cred-mira-discord")

    assert refusal(register_while_draining).code == "DRAINING"
    assert gate.platforms == (_PLATFORM,)
    assert gate.messages == (first.receipt,)
    sent = gate.deliver(_PLATFORM, "Flush the porch-light note.")
    assert sent.target == _PLATFORM
    assert sent.index == 0
    assert gate.status().deliveries == 1

    def unknown() -> Delivery:
        return gate.deliver("discord", "Flush the porch-light note.")

    assert refusal(unknown).code == "UNKNOWN_PLATFORM"
    assert len(gate.deliveries) == 1
    second = gate.shutdown()
    assert second.accepted == 1
    assert gate.draining is True
    snap = gate.snapshot()
    assert snap.state == "draining"
    assert rebuild(snap) == snap


def test_lower_caps_are_honored() -> None:
    gate = Gateway(message_cap=4, queue_cap=1, platform_cap=1)
    policy = gate.policy
    assert policy.message_cap == 4
    assert policy.queue_cap == 1
    assert policy.platform_cap == 1
    assert policy.message_capped is False
    assert policy.queue_capped is False
    assert policy.platform_capped is False
    assert policy.asked_message_cap == 4
    registered = gate.register_platform(_PLATFORM, _SIGNER)
    assert gate.register_platform(_PLATFORM, _SIGNER) is registered

    def platform_full() -> Platform:
        return gate.register_platform("discord", "cred-mira-discord")

    full = refusal(platform_full)
    assert full.code == "PLATFORM_CAP"
    assert full.detail == "1"
    row = post(gate, "msg-card-14", "abcd")
    assert row.receipt.message == "abcd"
    replay = post(gate, "msg-card-14", "abcd")
    assert replay.replay is True
    assert replay.receipt is row.receipt
    assert len(gate.messages) == 1

    def queue_full() -> IngestResult:
        return post(gate, "msg-note-15", "more")

    queued = refusal(queue_full)
    assert queued.code == "QUEUE_CAP"
    assert queued.detail == "1"

    def oversize() -> IngestResult:
        return gate.ingest(_PLATFORM, "msg-note-16", "abcde", "0" * 64, _NOW, _NOW)

    sized = refusal(oversize)
    assert sized.code == "OVERSIZE"
    assert sized.detail == "4"
    gate.deliver(_PLATFORM, "out")

    def delivery_full() -> Delivery:
        return gate.deliver(_PLATFORM, "out")

    delivered = refusal(delivery_full)
    assert delivered.code == "DELIVERY_CAP"
    assert delivered.detail == "1"
    assert len(gate.deliveries) == 1
    assert len(gate.messages) == 1


def test_asked_caps_do_not_rise() -> None:
    gate = Gateway(
        message_cap=MESSAGE_CAP + 25,
        queue_cap=QUEUE_CAP + 25,
        platform_cap=PLATFORM_CAP + 25,
    )
    policy = gate.policy
    assert policy.message_cap == MESSAGE_CAP
    assert policy.queue_cap == QUEUE_CAP
    assert policy.platform_cap == PLATFORM_CAP
    assert policy.asked_message_cap == MESSAGE_CAP + 25
    assert policy.asked_queue_cap == QUEUE_CAP + 25
    assert policy.asked_platform_cap == PLATFORM_CAP + 25
    assert policy.message_capped is True
    assert policy.queue_capped is True
    assert policy.platform_capped is True
    for index in range(PLATFORM_CAP):
        gate.register_platform(f"p{index:02d}", f"cred-p{index:02d}")

    def overflow_platform() -> Platform:
        return gate.register_platform("overflow", "cred-overflow")

    assert refusal(overflow_platform).code == "PLATFORM_CAP"
    assert gate.register_platform("p00", "cred-p00").name == "p00"
    body = "m" * MESSAGE_CAP
    for index in range(QUEUE_CAP):
        text = body if index == 0 else "m"
        post(gate, f"id-{index:03d}", text, platform="p00", signer="cred-p00")

    def overflow_queue() -> IngestResult:
        return post(gate, "id-overflow", "m", platform="p00", signer="cred-p00")

    assert refusal(overflow_queue).code == "QUEUE_CAP"
    replay = post(gate, "id-000", body, platform="p00", signer="cred-p00")
    assert replay.replay is True
    assert replay.receipt.message == body
    assert len(gate.messages) == QUEUE_CAP

    def changed_while_full() -> IngestResult:
        return post(gate, "id-000", "changed", platform="p00", signer="cred-p00")

    assert refusal(changed_while_full).code == "MISMATCH"
    assert len(gate.messages) == QUEUE_CAP

    def oversize() -> IngestResult:
        return gate.ingest("p00", "id-longer", body + "x", "0" * 64, _NOW, _NOW)

    sized = refusal(oversize)
    assert sized.code == "OVERSIZE"
    assert sized.detail == str(MESSAGE_CAP)
    assert len(gate.messages) == QUEUE_CAP
    for _index in range(QUEUE_CAP):
        gate.deliver("p00", "out")

    def overflow_delivery() -> Delivery:
        return gate.deliver("p00", "out")

    assert refusal(overflow_delivery).code == "DELIVERY_CAP"
    assert len(gate.deliveries) == QUEUE_CAP


def test_refusal_shapes() -> None:
    gate = Gateway()

    def missing_signer() -> Platform:
        return gate.register_platform(_PLATFORM, "")

    assert refusal(missing_signer).code == "MISSING"

    def blank_signer() -> str:
        return sign("", _PLATFORM, "msg-card-14", _CARD, _NOW)

    assert refusal(blank_signer).code == "MISSING"
    gate.register_platform(_PLATFORM, _SIGNER)

    def bad_name() -> Platform:
        return gate.register_platform("Telegram", _SIGNER)

    assert refusal(bad_name).code == "BAD_NAME"

    def empty_name() -> Platform:
        return gate.register_platform("", _SIGNER)

    assert refusal(empty_name).code == "BAD_NAME"

    def digit_name() -> Platform:
        return gate.register_platform("9abc", _SIGNER)

    assert refusal(digit_name).code == "BAD_NAME"

    def space_name() -> Platform:
        return gate.register_platform("has space", _SIGNER)

    assert refusal(space_name).code == "BAD_NAME"

    def secret_name() -> Platform:
        return gate.register_platform("sk-abcdefgh", _SIGNER)

    assert refusal(secret_name).code == "SECRET"

    def bad_id() -> IngestResult:
        return gate.ingest(_PLATFORM, "", _CARD, "0" * 64, _NOW, _NOW)

    assert refusal(bad_id).code == "BAD_ID"

    def space_id() -> IngestResult:
        return gate.ingest(_PLATFORM, "has space", _CARD, "0" * 64, _NOW, _NOW)

    assert refusal(space_id).code == "BAD_ID"

    def slash_id() -> IngestResult:
        return gate.ingest(_PLATFORM, "a/b", _CARD, "0" * 64, _NOW, _NOW)

    assert refusal(slash_id).code == "BAD_ID"

    def secret_id() -> IngestResult:
        return gate.ingest(_PLATFORM, "sk-abcdefgh", _CARD, "0" * 64, _NOW, _NOW)

    assert refusal(secret_id).code == "SECRET"

    def empty_message() -> IngestResult:
        return gate.ingest(_PLATFORM, "msg-card-14", "", "0" * 64, _NOW, _NOW)

    assert refusal(empty_message).code == "EMPTY_MESSAGE"

    def blank_message() -> IngestResult:
        return gate.ingest(_PLATFORM, "msg-card-14", "   ", "0" * 64, _NOW, _NOW)

    assert refusal(blank_message).code == "EMPTY_MESSAGE"

    def newline_message() -> IngestResult:
        return gate.ingest(_PLATFORM, "msg-card-14", "\n", "0" * 64, _NOW, _NOW)

    assert refusal(newline_message).code == "EMPTY_MESSAGE"

    def empty_delivery() -> Delivery:
        return gate.deliver(_PLATFORM, "   ")

    assert refusal(empty_delivery).code == "EMPTY_MESSAGE"

    def bearer() -> IngestResult:
        return gate.ingest(_PLATFORM, "msg-card-14", "Bearer abcdefghij", "0" * 64, _NOW, _NOW)

    secret = refusal(bearer)
    assert secret.code == "SECRET"
    assert secret.detail == ""
    assert "Bearer" not in str(secret)

    def assigned() -> IngestResult:
        return gate.ingest(_PLATFORM, "msg-card-14", "api_key=abcdef", "0" * 64, _NOW, _NOW)

    assert refusal(assigned).code == "SECRET"

    def not_text() -> IngestResult:
        return gate.ingest(1, "msg-card-14", _CARD, "0" * 64, _NOW, _NOW)

    assert refusal(not_text).code == "NOT_TEXT"

    def none_message() -> IngestResult:
        return gate.ingest(_PLATFORM, "msg-card-14", None, "0" * 64, _NOW, _NOW)

    assert refusal(none_message).code == "NOT_TEXT"

    def bytes_id() -> IngestResult:
        return gate.ingest(_PLATFORM, b"msg-card-14", _CARD, "0" * 64, _NOW, _NOW)

    assert refusal(bytes_id).code == "NOT_TEXT"

    def nul() -> IngestResult:
        return gate.ingest(_PLATFORM, "msg-card-14", "a\x00b", "0" * 64, _NOW, _NOW)

    assert refusal(nul).code == "NULL_BYTE"
    assert gate.messages == ()

    def bool_cap() -> Gateway:
        return Gateway(message_cap=True)

    assert refusal(bool_cap).code == "NOT_INT"

    def text_cap() -> Gateway:
        return Gateway(queue_cap="3")

    assert refusal(text_cap).code == "NOT_INT"

    def float_cap() -> Gateway:
        return Gateway(platform_cap=1.5)

    assert refusal(float_cap).code == "NOT_INT"

    def zero_cap() -> Gateway:
        return Gateway(message_cap=0)

    assert refusal(zero_cap).code == "OUT_OF_RANGE"

    def negative_cap() -> Gateway:
        return Gateway(queue_cap=-1)

    assert refusal(negative_cap).code == "OUT_OF_RANGE"

    def zero_platform() -> Gateway:
        return Gateway(platform_cap=0)

    assert refusal(zero_platform).code == "OUT_OF_RANGE"

    def bool_now() -> IngestResult:
        good = sign(_SIGNER, _PLATFORM, "msg-card-14", _CARD, _NOW)
        return gate.ingest(_PLATFORM, "msg-card-14", _CARD, good, _NOW, True)

    assert refusal(bool_now).code == "NOT_INT"

    def negative_now() -> IngestResult:
        good = sign(_SIGNER, _PLATFORM, "msg-card-14", _CARD, _NOW)
        return gate.ingest(_PLATFORM, "msg-card-14", _CARD, good, _NOW, -1)

    assert refusal(negative_now).code == "OUT_OF_RANGE"

    def bad_policy() -> Policy:
        return Policy(
            message_cap=MESSAGE_CAP + 1,
            queue_cap=QUEUE_CAP,
            platform_cap=PLATFORM_CAP,
            asked_message_cap=MESSAGE_CAP + 1,
            asked_queue_cap=QUEUE_CAP,
            asked_platform_cap=PLATFORM_CAP,
            message_capped=False,
            queue_capped=False,
            platform_capped=False,
        )

    assert refusal(bad_policy).code == "BAD_POLICY"
    kept = post(gate, "msg-with-line", "Porch light\nstays on for the session.")
    assert kept.receipt.message == "Porch light\nstays on for the session."
    assert post(gate, "msg-with-line", "Porch light\nstays on for the session.").receipt is kept.receipt


def test_rebuild_refuses_a_broken_chain() -> None:
    gate = Gateway()
    registered = gate.register_platform(_PLATFORM, _SIGNER)
    post(gate, "msg-card-14", _CARD)
    post(gate, "msg-note-15", _NOTE, fence=_NOW + 1, now=_NOW + 1)
    snap = gate.snapshot()
    assert rebuild(snap) is snap

    def not_snapshot() -> Snapshot:
        return rebuild(None)

    assert refusal(not_snapshot).code == "BAD_RECORD"

    def broken() -> Snapshot:
        first = _at(snap.receipts, 0)
        second = _at(snap.receipts, 1)
        bad = replace(first, sha="ab" * 32)
        return replace(snap, receipts=(bad, second))

    assert refusal(broken).code == "CHAIN"

    def duplicate() -> Snapshot:
        first = _at(snap.receipts, 0)
        second = _at(snap.receipts, 1)
        cloned = replace(second, message_id=first.message_id)
        return replace(snap, receipts=(first, cloned))

    assert refusal(duplicate).code == "DUPLICATE"

    def forged() -> Snapshot:
        first = _at(snap.receipts, 0)
        second = _at(snap.receipts, 1)
        bad = replace(first, signature=_flip(first.signature))
        return replace(snap, receipts=(bad, second))

    assert refusal(forged).code == "BAD_SIGNATURE"

    def bad_count() -> Snapshot:
        return replace(snap, accepted=0)

    assert refusal(bad_count).code == "BAD_RECORD"

    def stale() -> Snapshot:
        first = _hand(registered.name, registered.signer, "msg-card-14", _CARD, _NOW + 10, 0, _GENESIS)
        second = _hand(
            registered.name,
            registered.signer,
            "msg-note-15",
            _NOTE,
            _NOW + 9,
            1,
            first.sha,
        )
        return Snapshot(
            schema=SCHEMA,
            state="running",
            policy=gate.policy,
            platforms=(registered,),
            receipts=(first, second),
            deliveries=(),
            accepted=2,
        )

    ordered = refusal(stale)
    assert ordered.code == "STALE"
    assert ordered.detail == "order"
    assert rebuild(gate.snapshot()) == gate.snapshot()


def test_repr_omits_ledger_text_and_starts_no_thread() -> None:
    before = threading.active_count()
    gate = Gateway()
    gate.register_platform(_PLATFORM, _SIGNER)
    row = post(gate, "msg-card-14", _CARD)
    sent = gate.deliver(_PLATFORM, "reply")
    gate.shutdown()
    assert "porch" not in repr(gate)
    assert "porch" not in repr(row)
    assert "porch" not in repr(row.receipt)
    assert "reply" not in repr(sent)
    blob = " ".join(
        repr(item)
        for item in (gate, gate.policy, gate.status(), gate.snapshot(), row, row.receipt, sent)
    )
    assert "sk-" not in blob
    assert "Bearer" not in blob
    assert "api_key=" not in blob
    assert threading.active_count() == before
