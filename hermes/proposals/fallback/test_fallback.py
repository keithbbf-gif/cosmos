"""One confirming backup, then the chain ends."""

from __future__ import annotations

import pytest

from cosmos_hermes import Refuse, secret_shape
from fallback import (
    CHANNELS,
    ELIGIBLE,
    POLICY_CAP,
    SCHEMA,
    TERMINAL,
    Choice,
    Endpoint,
    Policy,
    Record,
    Snapshot,
    Turn,
    configure,
    fail,
    rebuild,
    switch,
)


def _endpoint(endpoint_id: str, provider: str, model: str, credential_id: str) -> Endpoint:
    return Endpoint(endpoint_id, provider, model, credential_id)


def _policy(*extras: Endpoint, cap: int = POLICY_CAP) -> Policy:
    primary = _endpoint("desk", "anthropic", "claude-sonnet-4", "cred-nora")
    spare = _endpoint("spare", "openrouter", "anthropic/claude-sonnet-4", "cred-lane")
    allow = ["anthropic", "openrouter"]
    rows: list[Endpoint] = [spare]
    for extra in extras:
        rows.append(extra)
        if extra.provider not in allow:
            allow.append(extra.provider)
    return configure(primary, tuple(rows), tuple(allow), cap)


def _at(turns: tuple[Turn, ...], index: int) -> Turn:
    return turns[index]


def _refusal(policy: Policy, turn_id: str, channel: str, records: tuple[Record, ...]) -> str:
    try:
        switch(policy, turn_id, channel, records)
    except Refuse as err:
        return err.code
    raise AssertionError("expected refuse")


def _story() -> tuple[Choice, str, Choice, Snapshot]:
    """Nora writes the field-notes card. The porch light is the next session turn."""
    extra = _endpoint("extra", "nous", "nous-hermes-3", "cred-nous")
    policy = _policy(extra, cap=4)
    assert policy.cap == POLICY_CAP
    assert policy.requested == 4
    assert policy.kept == 1
    assert policy.dropped == 1
    assert policy.fallback == _endpoint("spare", "openrouter", "anthropic/claude-sonnet-4", "cred-lane")
    primary = fail(policy, "field-notes", "chat", "desk", "RATE", 1_725_000_100)
    choice = switch(policy, "field-notes", "chat", (primary,))
    assert choice.fallback_id == "spare"
    assert choice.provider == "openrouter"
    assert choice.used_after == 1
    assert choice.error_code == "RATE"
    assert choice.credential_id == "cred-lane"
    backup = fail(policy, "field-notes", "chat", "spare", "RATE", 1_725_000_160, (primary,))
    ended = _refusal(policy, "field-notes", "chat", (primary, backup))
    assert ended == "EXHAUSTED"
    later_fail = fail(
        policy,
        "porch-light",
        "chat",
        "desk",
        "TIMEOUT",
        1_725_003_000,
        (primary, backup),
    )
    later = switch(policy, "porch-light", "chat", (primary, backup, later_fail))
    assert later.fallback_id == "spare"
    assert later.record.turn_id == "porch-light"
    snap = rebuild(policy, (primary, backup, later_fail))
    assert snap == rebuild(policy, (primary, backup, later_fail))
    first = _at(snap.turns, 0)
    second = _at(snap.turns, 1)
    assert first.turn_id == "field-notes"
    assert first.ended is True
    assert first.active_id == ""
    assert first.spent == 1
    assert first.codes == ("RATE", "RATE")
    assert second.turn_id == "porch-light"
    assert second.ended is False
    assert second.active_id == "spare"
    assert second.codes == ("TIMEOUT",)
    return (choice, ended, later, snap)


def test_example_fallback() -> None:
    assert _story() == _story()


def test_schema_channels_and_repr() -> None:
    assert SCHEMA == "cosmos-hermes-fallback/1"
    assert POLICY_CAP == 1
    assert CHANNELS == ("chat", "vision", "compress")
    assert "RATE" in ELIGIBLE
    assert "HTTP_401" in TERMINAL
    policy = _policy()
    chat = fail(policy, "field-notes", "chat", "desk", "RATE", 10)
    vision = fail(policy, "field-notes", "vision", "desk", "HTTP_500", 11, (chat,))
    compress = fail(policy, "field-notes", "compress", "desk", "TIMEOUT", 12, (chat, vision))
    log = (chat, vision, compress)
    chat_choice = switch(policy, "field-notes", "chat", log)
    vision_choice = switch(policy, "field-notes", "vision", log)
    compress_choice = switch(policy, "field-notes", "compress", log)
    assert chat_choice.channel == "chat"
    assert vision_choice.error_code == "HTTP_500"
    assert compress_choice.fallback_id == "spare"
    assert chat_choice == switch(policy, "field-notes", "chat", log)
    closed = fail(policy, "field-notes", "chat", "spare", "HTTP_503", 13, log)
    assert _refusal(policy, "field-notes", "chat", log + (closed,)) == "EXHAUSTED"
    still = switch(policy, "field-notes", "vision", log + (closed,))
    assert still.channel == "vision"
    blob = repr((policy, chat_choice, closed, rebuild(policy, log)))
    assert "sk-" not in blob
    assert "Bearer" not in blob
    assert "api_key=" not in blob
    assert not secret_shape(blob)


def test_cap_keeps_first_fallback_only() -> None:
    third = _endpoint("fourth", "deepseek", "deepseek-v3", "cred-deepseek")
    extra = _endpoint("extra", "nous", "nous-hermes-3", "cred-nous")
    policy = _policy(extra, third, cap=9)
    assert policy.cap == 1
    assert policy.requested == 9
    assert policy.kept == 1
    assert policy.dropped == 2
    assert policy.fallback is not None
    assert policy.fallback.endpoint_id == "spare"
    primary = fail(policy, "field-notes", "compress", "desk", "HTTP_503", 40)
    choice = switch(policy, "field-notes", "compress", (primary,))
    assert choice.fallback_id == "spare"
    assert choice.used_after == 1
    bare_primary = policy.primary
    bare = configure(bare_primary, (), ("anthropic",), cap=9)
    assert bare.cap == 1
    assert bare.requested == 9
    assert bare.kept == 0
    assert bare.dropped == 0
    assert bare.fallback is None
    again = configure(bare_primary, [policy.fallback], ["anthropic", "openrouter"])
    assert again == configure(bare_primary, (policy.fallback,), ("anthropic", "openrouter"))


def test_rate_backup_refusal_ends_chain() -> None:
    policy = _policy()
    primary = fail(policy, "field-notes", "chat", "desk", "HTTP_429", 30)
    choice = switch(policy, "field-notes", "chat", (primary,))
    assert choice.error_code == "HTTP_429"
    assert choice.used_after == 1
    assert choice.fallback_id == "spare"
    backup = fail(policy, "field-notes", "chat", "spare", "HTTP_429", 31, (primary,))
    assert _refusal(policy, "field-notes", "chat", (primary, backup)) == "EXHAUSTED"
    with pytest.raises(Refuse) as third:
        fail(policy, "field-notes", "chat", "spare", "RATE", 32, (primary, backup))
    assert third.value.code == "EXHAUSTED"
    fresh = fail(policy, "porch-light", "chat", "desk", "RATE", 90)
    assert switch(policy, "porch-light", "chat", (fresh,)).fallback_id == "spare"
    vision = fail(policy, "field-notes", "vision", "desk", "TIMEOUT", 33, (primary, backup))
    vision_end = fail(
        policy,
        "field-notes",
        "vision",
        "spare",
        "HTTP_401",
        34,
        (primary, backup, vision),
    )
    assert vision_end.code == "HTTP_401"
    assert _refusal(policy, "field-notes", "vision", (primary, backup, vision, vision_end)) == "EXHAUSTED"


def test_rebuild_reproduces_public_state() -> None:
    policy = _policy()
    primary = fail(policy, "field-notes", "chat", "desk", "RATE", 100)
    mid = rebuild(policy, (primary,))
    backup = fail(policy, "field-notes", "chat", "spare", "SERVER", 110, (primary,))
    ended = rebuild(policy, (primary, backup))
    assert mid == rebuild(policy, (primary,))
    assert ended == rebuild(policy, (primary, backup))
    open_turn = _at(mid.turns, 0)
    shut = _at(ended.turns, 0)
    assert open_turn.active_id == "spare"
    assert open_turn.ended is False
    assert open_turn.spent == 1
    assert open_turn.codes == ("RATE",)
    assert shut.ended is True
    assert shut.active_id == ""
    assert shut.codes == ("RATE", "SERVER")
    assert shut.spent == 1
    assert switch(policy, "field-notes", "chat", (primary,)).fallback_id == "spare"
    assert _refusal(policy, "field-notes", "chat", (primary, backup)) == "EXHAUSTED"


def test_refusal_codes() -> None:
    policy = _policy()
    primary = fail(policy, "field-notes", "chat", "desk", "RATE", 10)
    with pytest.raises(Refuse) as terminal:
        fail(policy, "field-notes", "vision", "desk", "HTTP_401", 11, (primary,))
    assert terminal.value.code == "NO_FALLBACK"
    for code in TERMINAL:
        with pytest.raises(Refuse) as caught:
            fail(policy, "other-turn", "chat", "desk", code, 12)
        assert caught.value.code == "NO_FALLBACK"
    with pytest.raises(Refuse) as empty_log:
        switch(policy, "field-notes", "chat", ())
    assert empty_log.value.code == "NO_FALLBACK"
    bare = configure(policy.primary, (), ("anthropic",))
    with pytest.raises(Refuse) as no_backup:
        fail(bare, "field-notes", "chat", "desk", "RATE", 12)
    assert no_backup.value.code == "NO_FALLBACK"
    with pytest.raises(Refuse) as unknown:
        fail(policy, "field-notes", "chat", "desk", "HTTP_418", 12)
    assert unknown.value.code == "UNCLASSIFIED"
    with pytest.raises(Refuse) as bad_code:
        fail(policy, "field-notes", "chat", "desk", "timeout", 12)
    assert bad_code.value.code == "BAD_CODE"
    with pytest.raises(Refuse) as blank_code:
        fail(policy, "field-notes", "chat", "desk", "", 12)
    assert blank_code.value.code == "BAD_CODE"
    with pytest.raises(Refuse) as channel:
        fail(policy, "field-notes", "audio", "desk", "RATE", 12)
    assert channel.value.code == "BAD_CHANNEL"
    with pytest.raises(Refuse) as turn:
        fail(policy, "bad turn", "chat", "desk", "RATE", 12)
    assert turn.value.code == "BAD_TURN"
    with pytest.raises(Refuse) as not_text:
        fail(policy, "field-notes", "chat", "desk", 12, 12)
    assert not_text.value.code == "NOT_TEXT"
    with pytest.raises(Refuse) as nul:
        fail(policy, "field-notes", "chat", "desk", "RATE\x00", 12)
    assert nul.value.code == "NULL_BYTE"
    with pytest.raises(Refuse) as huge:
        fail(policy, "field-notes", "chat", "desk", "H" * 33, 12)
    assert huge.value.code == "OVERSIZE"
    with pytest.raises(Refuse) as flag:
        fail(policy, "field-notes", "chat", "desk", "RATE", True)
    assert flag.value.code == "NOT_INT"
    with pytest.raises(Refuse) as negative:
        fail(policy, "field-notes", "chat", "desk", "RATE", -1)
    assert negative.value.code == "OUT_OF_RANGE"
    with pytest.raises(Refuse) as stale:
        fail(policy, "field-notes", "chat", "spare", "RATE", 10, (primary,))
    assert stale.value.code == "STALE"
    with pytest.raises(Refuse) as chain:
        fail(policy, "field-notes", "chat", "desk", "RATE", 11, "nope")
    assert chain.value.code == "BAD_CHAIN"
    with pytest.raises(Refuse) as dup:
        rebuild(policy, (primary, primary))
    assert dup.value.code == "DUPLICATE"
    other = fail(policy, "porch-light", "chat", "desk", "RATE", 50)
    with pytest.raises(Refuse) as broken:
        rebuild(policy, (primary, other))
    assert broken.value.code == "BROKEN_CHAIN"
    with pytest.raises(Refuse) as forged:
        Record(
            primary.turn_id,
            primary.channel,
            primary.primary_id,
            primary.fallback_id,
            primary.endpoint_id,
            primary.code,
            primary.at,
            primary.prev,
            "0" * 64,
        )
    assert forged.value.code == "BROKEN_CHAIN"
    with pytest.raises(Refuse) as missing:
        _endpoint("desk", "anthropic", "claude-sonnet-4", "")
    assert missing.value.code == "MISSING_CRED"
    with pytest.raises(Refuse) as secret:
        _endpoint("desk", "anthropic", "claude-sonnet-4", "sk-abcdefghij")
    assert secret.value.code == "SECRET"
    with pytest.raises(Refuse) as bearer:
        _endpoint("desk", "anthropic", "Bearer abcdefghijk", "cred-nora")
    assert bearer.value.code == "SECRET"
    with pytest.raises(Refuse) as assigned:
        _endpoint("desk", "api_key=abcdefgh", "claude-sonnet-4", "cred-nora")
    assert assigned.value.code == "SECRET"
    with pytest.raises(Refuse) as route:
        _endpoint("desk", "anthropic", "bad model", "cred-nora")
    assert route.value.code == "BAD_ROUTE"
    with pytest.raises(Refuse) as url:
        _endpoint("desk", "anthropic", "http://localhost/v1", "cred-nora")
    assert url.value.code == "BAD_ROUTE"
    with pytest.raises(Refuse) as started:
        fail(policy, "field-notes", "chat", "spare", "RATE", 12)
    assert started.value.code == "BAD_ROUTE"
    with pytest.raises(Refuse) as empty_allow:
        configure(policy.primary, (), ())
    assert empty_allow.value.code == "EMPTY_ALLOW"
    with pytest.raises(Refuse) as bad_allow:
        configure(policy.primary, (), "anthropic")
    assert bad_allow.value.code == "BAD_ALLOW"
    with pytest.raises(Refuse) as blank_allow:
        configure(policy.primary, (), ("",))
    assert blank_allow.value.code == "BAD_ALLOW"
    with pytest.raises(Refuse) as duplicate_allow:
        configure(policy.primary, (), ("anthropic", "anthropic"))
    assert duplicate_allow.value.code == "DUPLICATE"
    backup = policy.fallback
    assert backup is not None
    with pytest.raises(Refuse) as denied:
        configure(policy.primary, (backup,), ("openrouter",))
    assert denied.value.code == "NOT_ALLOWED"
    with pytest.raises(Refuse) as outside:
        configure(policy.primary, (backup,), ("anthropic",))
    assert outside.value.code == "NOT_ALLOWED"
    same = _endpoint("other", "anthropic", "claude-haiku", "cred-other")
    with pytest.raises(Refuse) as same_provider:
        configure(policy.primary, (same,), ("anthropic",))
    assert same_provider.value.code == "SAME_PROVIDER"
    with pytest.raises(Refuse) as dup_id:
        configure(policy.primary, (backup, backup), ("anthropic", "openrouter"))
    assert dup_id.value.code == "BAD_ROUTE"
    with pytest.raises(Refuse) as off:
        configure(policy.primary, (), ("anthropic",), cap=0)
    assert off.value.code == "BAD_CAP"
    with pytest.raises(Refuse) as flag_cap:
        configure(policy.primary, (), ("anthropic",), cap=True)
    assert flag_cap.value.code == "NOT_INT"
    with pytest.raises(Refuse) as high:
        configure(policy.primary, (), ("anthropic",), cap=1_000_001)
    assert high.value.code == "OUT_OF_RANGE"
    with pytest.raises(Refuse) as raised:
        Policy(policy.primary, None, ("anthropic",), 2, 2, 0, 0)
    assert raised.value.code == "BAD_CAP"
    with pytest.raises(Refuse) as used:
        Choice(
            primary.turn_id,
            primary.channel,
            "spare",
            "openrouter",
            "anthropic/claude-sonnet-4",
            "cred-lane",
            2,
            "RATE",
            primary,
        )
    assert used.value.code == "BAD_CAP"
    rows = tuple(
        _endpoint(f"id{i}", "openrouter", f"model-{i}", f"cred-{i}") for i in range(9)
    )
    with pytest.raises(Refuse) as over_list:
        configure(policy.primary, rows, ("anthropic", "openrouter"))
    assert over_list.value.code == "OVERSIZE"
    wide = tuple(f"p{i}" for i in range(33))
    with pytest.raises(Refuse) as over_allow:
        configure(policy.primary, (), wide)
    assert over_allow.value.code == "OVERSIZE"
    later = _endpoint("extra", "nous", "nous-hermes-3", "cred-nous")
    with pytest.raises(Refuse) as later_denied:
        configure(policy.primary, (backup, later), ("anthropic", "openrouter"))
    assert later_denied.value.code == "NOT_ALLOWED"


def test_record_cap_and_foreign_policy() -> None:
    policy = _policy()
    prior: tuple[Record, ...] = ()
    stamp = 10
    last: Record | None = None
    for index in range(64):
        last = fail(policy, f"t{index}", "chat", "desk", "RATE", stamp, prior)
        prior = prior + (last,)
        stamp += 1
    assert last is not None
    with pytest.raises(Refuse) as over:
        fail(policy, "t64", "chat", "desk", "RATE", stamp, prior)
    assert over.value.code == "OVERSIZE"
    other = configure(
        _endpoint("other-desk", "anthropic", "claude-sonnet-4", "cred-nora"),
        (_endpoint("other-spare", "openrouter", "anthropic/claude-sonnet-4", "cred-lane"),),
        ("anthropic", "openrouter"),
    )
    solo = fail(policy, "solo-turn", "chat", "desk", "RATE", 1)
    with pytest.raises(Refuse) as foreign:
        rebuild(other, (solo,))
    assert foreign.value.code == "BAD_ROUTE"
