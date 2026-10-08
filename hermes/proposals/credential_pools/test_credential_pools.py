"""Credential-pool refusals, rotation, and the policy cap."""

from __future__ import annotations

import hashlib

import pytest

from cosmos_hermes import Refuse, secret_shape
from credential_pools import (
    COOLDOWN_S,
    MAX_CONFIRMING_RETRIES,
    POLICY_CAP,
    RETRY_CLASS,
    SCHEMA,
    CredentialPool,
    PoolRecord,
    rebuild,
    reveal,
)


def _pool(
    *ids: str,
    strategy: str = "fill_first",
    cap: int | None = None,
) -> CredentialPool:
    pool = CredentialPool("openrouter", strategy=strategy, cap=cap)
    for cred_id in ids:
        pool.add(cred_id)
    return pool


def test_schema() -> None:
    assert SCHEMA == "cosmos-hermes-credential_pools/1"
    pool = CredentialPool("custom:together.ai")
    view = pool.status(0)
    assert view.schema == SCHEMA
    assert view.provider == "custom:together.ai"
    assert view.cap == POLICY_CAP
    assert view.requested_cap == POLICY_CAP
    assert COOLDOWN_S == 60
    assert RETRY_CLASS == "HTTP_429"
    assert MAX_CONFIRMING_RETRIES == 1


def test_success_path() -> None:
    pool = CredentialPool("openrouter")
    first = pool.add("cred.alpha")
    second = pool.add("cred-beta")
    assert first.cred_id == "cred.alpha"
    assert second.request_count == 0
    assert pool.next_id(1_700_000_000) == "cred.alpha"
    held = pool.report("cred.alpha", "HTTP_200", 1_700_000_000)
    assert held.action == "HOLD"
    assert held.code == "HTTP_200"
    assert held.cool_until is None
    assert pool.next_id(1_700_000_000) == "cred.alpha"
    view = pool.status(1_700_000_000)
    assert view.strategy == "fill_first"
    assert view.ids == ("cred.alpha", "cred-beta")
    assert view.selected == "cred.alpha"
    assert view.cooling == ()
    assert view.counts == (("cred.alpha", 2), ("cred-beta", 0))
    assert view.provider == "openrouter"
    assert not secret_shape(repr(pool))
    assert not secret_shape(repr(view))
    assert not secret_shape(repr(held))
    assert not secret_shape(repr(first))


def test_default_429_and_401_cool_for_60() -> None:
    pool = _pool("alpha", "beta")
    assert pool.next_id(100) == "alpha"
    rate = pool.report("alpha", "HTTP_429", 100)
    assert rate.action == "ROTATE"
    assert rate.cool_until == 160
    assert pool.next_id(100) == "beta"
    assert pool.next_id(159) == "beta"
    assert pool.next_id(160) == "alpha"
    auth = pool.report("alpha", "HTTP_401", 160)
    assert auth.action == "ROTATE"
    assert auth.cool_until == 220
    assert pool.status(219).cooling == ("alpha",)
    assert pool.next_id(219) == "beta"
    assert pool.next_id(220) == "alpha"
    assert pool.status(220).provider == "openrouter"


@pytest.mark.parametrize("code", ["HTTP_200", "OK", "HTTP_400", "HTTP_402", "HTTP_500"])
def test_other_codes_do_not_rotate(code: str) -> None:
    pool = _pool("alpha", "beta")
    assert pool.next_id(5) == "alpha"
    outcome = pool.report("alpha", code, 5)
    assert outcome.action == "HOLD"
    assert outcome.code == code
    assert outcome.cool_until is None
    assert pool.status(5).cooling == ()
    assert pool.next_id(5) == "alpha"
    assert pool.status(5).provider == "openrouter"


def test_confirming_retry_is_once() -> None:
    pool = _pool("alpha", "beta")
    assert pool.next_id(10) == "alpha"
    first = pool.report("alpha", "HTTP_429", 10, confirm=True)
    assert first.action == "RETRY"
    assert first.cool_until is None
    assert pool.next_id(10) == "alpha"
    assert pool.status(10).retries == (("alpha", 1), ("beta", 0))
    second = pool.report("alpha", "HTTP_429", 10, confirm=True)
    assert second.action == "ROTATE"
    assert second.cool_until == 70
    assert pool.next_id(10) == "beta"
    third = pool.report("alpha", "HTTP_429", 20, confirm=True)
    assert third.action == "ROTATE"
    assert third.cool_until == 80
    assert pool.status(20).retries == (("alpha", 0), ("beta", 0))
    assert pool.status(20).retries[0][1] <= MAX_CONFIRMING_RETRIES


def test_success_resets_confirming_retry() -> None:
    pool = _pool("alpha", "beta")
    pool.next_id(0)
    assert pool.report("alpha", "HTTP_429", 0, confirm=True).action == "RETRY"
    assert pool.report("alpha", "HTTP_200", 0).action == "HOLD"
    assert pool.status(0).retries == (("alpha", 0), ("beta", 0))
    assert pool.next_id(0) == "alpha"
    again = pool.report("alpha", "HTTP_429", 0, confirm=True)
    assert again.action == "RETRY"
    assert pool.next_id(0) == "alpha"


def test_hold_keeps_the_retry_latch() -> None:
    pool = _pool("alpha", "beta")
    pool.report("alpha", "HTTP_429", 0, confirm=True)
    held = pool.report("alpha", "HTTP_400", 0)
    assert held.action == "HOLD"
    assert pool.status(0).retries == (("alpha", 1), ("beta", 0))
    assert pool.next_id(0) == "alpha"
    rotated = pool.report("alpha", "HTTP_429", 0, confirm=True)
    assert rotated.action == "ROTATE"
    assert rotated.cool_until == COOLDOWN_S
    assert pool.next_id(0) == "beta"


def test_confirm_does_not_apply_to_401() -> None:
    pool = _pool("alpha", "beta")
    outcome = pool.report("alpha", "HTTP_401", 0, confirm=True)
    assert outcome.action == "ROTATE"
    assert outcome.cool_until == COOLDOWN_S
    assert pool.next_id(0) == "beta"


def test_confirm_ignored_on_other_codes() -> None:
    pool = _pool("alpha", "beta")
    assert pool.next_id(0) == "alpha"
    outcome = pool.report("alpha", "HTTP_500", 0, confirm=True)
    assert outcome.action == "HOLD"
    assert pool.next_id(0) == "alpha"


def test_confirm_does_not_exhaust() -> None:
    pool = _pool("only")
    outcome = pool.report("only", "HTTP_429", 0, confirm=True)
    assert outcome.action == "RETRY"
    assert pool.next_id(0) == "only"
    bench = pool.report("only", "HTTP_429", 0)
    assert bench.action == "ROTATE"
    assert bench.cool_until == COOLDOWN_S
    with pytest.raises(Refuse) as caught:
        pool.next_id(0)
    assert caught.value.code == "POOL_EXHAUSTED"
    assert pool.next_id(COOLDOWN_S) == "only"


def test_pool_exhausted() -> None:
    pool = _pool("alpha", "beta")
    pool.report("alpha", "HTTP_429", 1)
    pool.report("beta", "HTTP_401", 1)
    with pytest.raises(Refuse) as caught:
        pool.next_id(1)
    assert caught.value.code == "POOL_EXHAUSTED"
    assert pool.status(1).provider == "openrouter"
    assert pool.status(1).cooling == ("alpha", "beta")
    assert pool.next_id(1 + COOLDOWN_S) == "alpha"


def test_empty() -> None:
    pool = CredentialPool("openrouter")
    with pytest.raises(Refuse) as caught:
        pool.next_id(0)
    assert caught.value.code == "EMPTY"


def test_cap_is_policy() -> None:
    pool = CredentialPool("openrouter", cap=100)
    view = pool.status(0)
    assert view.cap == POLICY_CAP
    assert view.requested_cap == 100
    for index in range(POLICY_CAP):
        pool.add(f"id{index}")
    with pytest.raises(Refuse) as caught:
        pool.add("id-extra")
    assert caught.value.code == "CAP"
    assert caught.value.detail == str(POLICY_CAP)
    assert len(pool.status(0).ids) == POLICY_CAP


def test_lower_cap_is_honored() -> None:
    pool = CredentialPool("anthropic", cap=2)
    assert pool.status(0).cap == 2
    assert pool.status(0).requested_cap == 2
    pool.add("one")
    pool.add("two")
    with pytest.raises(Refuse) as caught:
        pool.add("three")
    assert caught.value.code == "CAP"
    assert caught.value.detail == "2"
    assert pool.status(0).provider == "anthropic"


def test_provider_fixed() -> None:
    pool = _pool("alpha")
    with pytest.raises(Refuse) as same:
        pool.change_provider("openrouter")
    assert same.value.code == "PROVIDER_FIXED"
    with pytest.raises(Refuse) as other:
        pool.change_provider("anthropic")
    assert other.value.code == "PROVIDER_FIXED"
    with pytest.raises(Refuse) as secret:
        pool.change_provider("sk-livekeyvalue")
    assert secret.value.code == "SECRET"
    with pytest.raises(Refuse) as bad:
        pool.change_provider("nope nope")
    assert bad.value.code == "BAD_PROVIDER"
    with pytest.raises(Refuse) as missing:
        pool.change_provider("")
    assert missing.value.code == "MISSING_PROVIDER"
    assert pool.status(0).provider == "openrouter"
    assert pool.status(0).ids == ("alpha",)


def test_plaintext() -> None:
    pool = _pool("alpha")
    with pytest.raises(Refuse) as module_level:
        reveal()
    assert module_level.value.code == "PLAINTEXT"
    with pytest.raises(Refuse) as method:
        pool.reveal()
    assert method.value.code == "PLAINTEXT"
    assert pool.next_id(0) == "alpha"
    assert "alpha" not in str(method.value)


def test_duplicate() -> None:
    pool = _pool("alpha")
    with pytest.raises(Refuse) as caught:
        pool.add("alpha")
    assert caught.value.code == "DUPLICATE"
    assert pool.status(0).ids == ("alpha",)


def test_unknown_id_does_not_mutate() -> None:
    pool = _pool("alpha")
    before = pool.status(0)
    with pytest.raises(Refuse) as caught:
        pool.report("missing", "HTTP_401", 0)
    assert caught.value.code == "UNKNOWN_ID"
    assert pool.status(0) == before


def test_bad_clock_does_not_mutate() -> None:
    pool = _pool("alpha")
    before = pool.status(0)
    with pytest.raises(Refuse) as caught:
        pool.report("alpha", "HTTP_401", -1)
    assert caught.value.code == "OUT_OF_RANGE"
    with pytest.raises(Refuse) as big:
        pool.next_id(4_000_000_000)
    assert big.value.code == "OUT_OF_RANGE"
    with pytest.raises(Refuse) as peek:
        pool.status(-1)
    assert peek.value.code == "OUT_OF_RANGE"
    with pytest.raises(Refuse) as huge:
        CredentialPool("openrouter", cap=1_000_000_001)
    assert huge.value.code == "OUT_OF_RANGE"
    assert pool.status(0) == before


def test_not_int() -> None:
    with pytest.raises(Refuse) as caught:
        CredentialPool("openrouter", cap=True)
    assert caught.value.code == "NOT_INT"
    pool = _pool("alpha")
    with pytest.raises(Refuse) as clock:
        pool.next_id(False)
    assert clock.value.code == "NOT_INT"
    with pytest.raises(Refuse) as text:
        pool.report("alpha", "HTTP_200", "0")
    assert text.value.code == "NOT_INT"


def test_not_text() -> None:
    with pytest.raises(Refuse) as caught:
        CredentialPool(None)
    assert caught.value.code == "NOT_TEXT"
    pool = CredentialPool("openrouter")
    with pytest.raises(Refuse) as added:
        pool.add(None)
    assert added.value.code == "NOT_TEXT"
    with pytest.raises(Refuse) as coded:
        pool.report("alpha", None, 0)
    assert coded.value.code == "NOT_TEXT"
    with pytest.raises(Refuse) as strategy:
        CredentialPool("openrouter", strategy=None)
    assert strategy.value.code == "NOT_TEXT"


def test_id_shape_refusals() -> None:
    pool = CredentialPool("openrouter")
    cases: tuple[tuple[object, str], ...] = (
        ("", "MISSING_ID"),
        ("bad id", "BAD_ID"),
        ("../nope", "BAD_ID"),
        ("a\x00b", "NULL_BYTE"),
        ("a" * 65, "OVERSIZE"),
        ("sk-livekeyvalue", "SECRET"),
        ("Bearer abcdefghijk", "SECRET"),
        ("api_key=supersecret", "SECRET"),
    )
    for value, code in cases:
        with pytest.raises(Refuse) as caught:
            pool.add(value)
        assert caught.value.code == code
        assert secret_shape(str(caught.value)) is False
    assert pool.status(0).ids == ()


def test_provider_and_strategy_refusals() -> None:
    with pytest.raises(Refuse) as missing:
        CredentialPool("")
    assert missing.value.code == "MISSING_PROVIDER"
    with pytest.raises(Refuse) as bad:
        CredentialPool("has space")
    assert bad.value.code == "BAD_PROVIDER"
    with pytest.raises(Refuse) as secret:
        CredentialPool("sk-livekeyvalue")
    assert secret.value.code == "SECRET"
    for raw in ("sk-livekeyvalue", "Bearer abcdefghijk", "api_key=supersecret"):
        with pytest.raises(Refuse) as strategy_secret:
            CredentialPool("openrouter", strategy=raw)
        assert strategy_secret.value.code == "SECRET"
        assert raw not in str(strategy_secret.value)
        assert secret_shape(str(strategy_secret.value)) is False
    with pytest.raises(Refuse) as random_strategy:
        CredentialPool("openrouter", strategy="random")
    assert random_strategy.value.code == "NONDETERMINISTIC"
    for name in ("off", "yolo", "auto", ""):
        with pytest.raises(Refuse) as caught:
            CredentialPool("openrouter", strategy=name)
        assert caught.value.code == "UNKNOWN_STRATEGY"


def test_unclassified() -> None:
    pool = _pool("alpha")
    for code in ("HTTP_418", "429", "yolo", "off", ""):
        with pytest.raises(Refuse) as caught:
            pool.report("alpha", code, 0)
        assert caught.value.code == "UNCLASSIFIED"
    raw = "sk-livekeyvalue"
    with pytest.raises(Refuse) as secret_code:
        pool.report("alpha", raw, 0)
    assert secret_code.value.code == "SECRET"
    assert raw not in str(secret_code.value)
    with pytest.raises(Refuse) as flag:
        pool.report("alpha", "HTTP_429", 0, confirm=1)
    assert flag.value.code == "UNCLASSIFIED"
    with pytest.raises(Refuse) as none_flag:
        pool.report("alpha", "HTTP_200", 0, confirm=None)
    assert none_flag.value.code == "UNCLASSIFIED"
    view = pool.status(0)
    assert view.cooling == ()
    assert view.retries == (("alpha", 0),)
    assert view.counts == (("alpha", 0),)


def test_repr_has_no_secret_shape() -> None:
    pool = _pool("alpha")
    secret = "sk-livekeyvalue"
    with pytest.raises(Refuse) as caught:
        pool.add(secret)
    assert caught.value.code == "SECRET"
    assert secret not in str(caught.value)
    assert secret not in repr(caught.value)
    texts = (
        repr(pool),
        repr(pool.status(0)),
        repr(pool.report("alpha", "HTTP_200", 0)),
        repr(pool.add("cred-b")),
    )
    for text in texts:
        assert secret not in text
        assert not secret_shape(text)


def test_status_is_a_peek() -> None:
    pool = _pool("alpha", "beta")
    assert pool.status(0).counts == (("alpha", 0), ("beta", 0))
    assert pool.status(0).counts == (("alpha", 0), ("beta", 0))
    assert pool.next_id(0) == "alpha"
    assert pool.status(0).counts == (("alpha", 1), ("beta", 0))
    pool.report("alpha", "HTTP_200", 0)
    assert pool.status(0).counts == (("alpha", 1), ("beta", 0))
    assert pool.status(0).selected == "alpha"


def test_least_used_is_deterministic() -> None:
    pool = _pool("a", "b", "c", strategy="least_used")
    seen = [pool.next_id(0) for _ in range(5)]
    assert seen == ["a", "b", "c", "a", "b"]
    assert pool.status(0).counts == (("a", 2), ("b", 2), ("c", 1))
    pool.report("a", "HTTP_401", 0)
    assert pool.next_id(0) == "c"
    assert pool.status(0).provider == "openrouter"


def test_round_robin_skips_cooling() -> None:
    pool = _pool("a", "b", "c", strategy="round_robin")
    assert [pool.next_id(0) for _ in range(4)] == ["a", "b", "c", "a"]
    pool.report("a", "HTTP_401", 0)
    assert pool.next_id(0) == "b"
    assert pool.next_id(0) == "c"
    assert pool.next_id(0) == "b"
    other = _pool("a", "b", "c", strategy="round_robin")
    assert other.next_id(0) == "a"
    assert other.next_id(0) == "b"
    other.report("c", "HTTP_401", 0)
    assert other.next_id(0) == "a"
    assert other.status(0).cooling == ("c",)
    assert other.status(0).selected == "a"


def _at(records: tuple[PoolRecord, ...], index: int) -> PoolRecord:
    if index < 0 or index >= len(records):
        raise AssertionError(index)
    return records[index]


def _record(prev: str, body: str) -> PoolRecord:
    digest = hashlib.sha256(f"{prev}\n{body}".encode("utf-8")).hexdigest()
    return PoolRecord(prev, body, digest)


def test_stale_clock_does_not_mutate() -> None:
    pool = _pool("alpha", "beta")
    assert pool.next_id(40) == "alpha"
    before = pool.status(40)
    chain = pool.records()
    with pytest.raises(Refuse) as earlier:
        pool.next_id(39)
    assert earlier.value.code == "STALE"
    with pytest.raises(Refuse) as reported:
        pool.report("alpha", "HTTP_401", 39)
    assert reported.value.code == "STALE"
    assert pool.status(40) == before
    assert pool.records() == chain
    pool.next_id(100)
    pool.report("alpha", "HTTP_429", 100)
    assert pool.next_id(160) == "alpha"
    assert pool.report("alpha", "HTTP_200", 160).action == "HOLD"
    held = pool.status(160)
    with pytest.raises(Refuse) as reopened:
        pool.next_id(100)
    assert reopened.value.code == "STALE"
    assert pool.status(160) == held


def test_rebuild_replays_public_state() -> None:
    wide = CredentialPool("openrouter", cap=100)
    wide.add("alpha")
    restored_cap = rebuild(wide.records())
    assert restored_cap.status(0).cap == POLICY_CAP
    assert restored_cap.status(0).requested_cap == 100
    assert restored_cap.status(0).ids == ("alpha",)
    for strategy in ("fill_first", "round_robin", "least_used"):
        pool = _pool("a", "b", "c", strategy=strategy)
        pool.next_id(3)
        pool.report("a", "HTTP_429", 3)
        pool.next_id(3)
        restored = rebuild(pool.records())
        assert restored.status(3) == pool.status(3)
        assert restored.records() == pool.records()
        with pytest.raises(Refuse) as stale:
            restored.next_id(2)
        assert stale.value.code == "STALE"
        assert restored.status(3) == pool.status(3)
        assert restored.next_id(3) == pool.next_id(3)
        assert restored.status(3) == pool.status(3)
    continued = rebuild(wide.records())
    continued.add("beta")
    assert rebuild(continued.records()).status(0) == continued.status(0)


def test_chain_and_bad_record() -> None:
    pool = _pool("alpha")
    chain = pool.records()
    header = _at(chain, 0)
    added = _at(chain, 1)
    with pytest.raises(Refuse) as again:
        rebuild((header, header))
    assert again.value.code == "CHAIN"
    duplicate = _record(added.digest, "add\talpha")
    with pytest.raises(Refuse) as dup:
        rebuild((header, added, duplicate))
    assert dup.value.code == "DUPLICATE"
    with pytest.raises(Refuse) as empty:
        rebuild(())
    assert empty.value.code == "BAD_RECORD"
    with pytest.raises(Refuse) as kinds:
        rebuild(None)
    assert kinds.value.code == "BAD_RECORD"
    with pytest.raises(Refuse) as item:
        rebuild((header, "tail"))
    assert item.value.code == "BAD_RECORD"
    with pytest.raises(Refuse) as shape:
        PoolRecord(header.prev, "add", "0" * 64)
    assert shape.value.code == "BAD_RECORD"
    with pytest.raises(Refuse) as broken:
        PoolRecord(header.prev, "add\tbeta", "0" * 64)
    assert broken.value.code == "CHAIN"
    raw = "sk-livekeyvalue"
    body = f"add\t{raw}"
    digest = hashlib.sha256(f"{header.prev}\n{body}".encode("utf-8")).hexdigest()
    with pytest.raises(Refuse) as secret:
        PoolRecord(header.prev, body, digest)
    assert secret.value.code == "SECRET"
    assert raw not in str(secret.value)
    assert secret_shape(repr(header)) is False
    fresh = CredentialPool("openrouter")
    assert rebuild(fresh.records()).status(0) == fresh.status(0)


def test_example_credential_pools() -> None:
    """Mina's session keeps one openrouter pool.

    card.studio, note.field, and light.porch are three ids. A plain HTTP_429
    on the studio card selects the field note next. The provider stays
    openrouter. A raw key string is refused.
    """

    def run() -> tuple[object, ...]:
        pool = CredentialPool("openrouter")
        raw = "sk-or-v1-studiokey"
        secret_code = "NONE"
        try:
            pool.add(raw)
        except Refuse as refused:
            secret_code = refused.code
            assert raw not in str(refused)
        now = 1_720_000_000
        pool.add("card.studio")
        pool.add("note.field")
        pool.add("light.porch")
        first = pool.next_id(now)
        outcome = pool.report(first, "HTTP_429", now)
        second = pool.next_id(now)
        fixed = "NONE"
        try:
            pool.change_provider("anthropic")
        except Refuse as refused:
            fixed = refused.code
        view = pool.status(now)
        restored = rebuild(pool.records()).status(now)
        assert secret_code == "SECRET"
        assert first == "card.studio"
        assert outcome.action == "ROTATE"
        assert outcome.code == "HTTP_429"
        assert outcome.cool_until == now + COOLDOWN_S
        assert second == "note.field"
        assert second != first
        assert fixed == "PROVIDER_FIXED"
        assert view.provider == "openrouter"
        assert view.selected == "note.field"
        assert view.ids == ("card.studio", "note.field", "light.porch")
        assert view.cooling == ("card.studio",)
        assert view.counts == (("card.studio", 1), ("note.field", 1), ("light.porch", 0))
        assert view == restored
        assert not secret_shape(repr(pool))
        return (secret_code, first, outcome, second, fixed, view, restored)

    assert run() == run()
