"""Refusal, cap, and id-only resolve coverage for the credential vault."""

from __future__ import annotations

from dataclasses import dataclass, replace

import pytest

import credential_vault as vault_mod
from cosmos_hermes import Refuse, secret_shape
from credential_vault import (
    FIELD_CAP,
    POLICY_BUDGET,
    POLICY_CAP,
    POLICY_HISTORY,
    POLICY_ORIGINS,
    SCHEMA,
    CapNote,
    CredentialVault,
    Item,
    Record,
    Resolution,
    rebuild,
    store_plaintext,
)

_ORIGIN = "https://kiln.example"
_LIGHT = "https://lights.example"
_KEY = "sk-" + ("k" * 40)
_BEARER = "Bearer " + ("k" * 16)


def _code(err: BaseException) -> str:
    if not isinstance(err, Refuse):
        raise AssertionError("expected Refuse")
    return err.code


def _detail(err: BaseException) -> str:
    if not isinstance(err, Refuse):
        raise AssertionError("expected Refuse")
    return err.detail


def _nth(records: tuple[Record, ...], index: int) -> Record:
    if index < 0 or index >= len(records):
        raise AssertionError("missing record")
    return records[index]


def _put(
    vault: CredentialVault,
    cred_id: str,
    origins: tuple[str, ...],
    *,
    kind: str,
    label: str,
    stamp: int,
    login_id: str = "",
    source: str = "local",
    fields: int = 1,
) -> None:
    vault.put(
        cred_id,
        origins,
        kind=kind,
        label=label,
        stamp=stamp,
        login_id=login_id,
        source=source,
        fields=fields,
    )


@dataclass(frozen=True, slots=True)
class _Story:
    opened: Resolution
    note: Resolution
    light: Resolution
    picked_ids: tuple[str, ...]
    clamped: bool
    secret_code: str
    bearer_code: str
    headless_card: str
    unchanged: bool
    same_snapshot: bool
    shown_clean: bool
    ids: tuple[str, ...]


def _clean(text: str) -> bool:
    if secret_shape(text):
        return False
    if "sk-" in text or "Bearer" in text:
        return False
    return True


def _story() -> _Story:
    detected = ("onepassword", "bitwarden")
    vault = CredentialVault("interactive", detected=detected)
    _put(
        vault,
        "cred-kiln",
        (_ORIGIN,),
        kind="card",
        label="Kiln glaze card",
        login_id="ada",
        fields=2,
        stamp=1_720_000_000,
    )
    _put(
        vault,
        "note-ship",
        (_ORIGIN,),
        kind="address",
        label="Kiln ship note",
        login_id="ada",
        fields=3,
        stamp=1_720_000_100,
    )
    _put(
        vault,
        "porch-light",
        (_LIGHT,),
        kind="login",
        label="Porch light",
        login_id="ada",
        stamp=1_720_000_200,
    )
    opened = vault.resolve("cred-kiln", _ORIGIN, stamp=1_720_000_300, confirm=True)
    note = vault.resolve("note-ship", _ORIGIN, stamp=1_720_000_300)
    picked = vault.select(_ORIGIN, 10_000, stamp=1_720_000_300)
    before = vault.snapshot()
    secret_code = "MISSING"
    try:
        vault.put(_KEY, (_ORIGIN,), kind="login", label="Nope", stamp=1_720_000_400)
    except Refuse as err:
        secret_code = err.code
        assert _KEY not in str(err)
        assert _KEY not in repr(vault)
    bearer_code = "MISSING"
    try:
        store_plaintext(_BEARER)
    except Refuse as err:
        bearer_code = err.code
        assert _BEARER not in str(err)
    after = vault.snapshot()
    quiet = rebuild(vault.records(), "headless", detected=detected)
    light = quiet.resolve("porch-light", _LIGHT, stamp=1_720_000_300)
    headless_card = "MISSING"
    try:
        quiet.resolve("cred-kiln", _ORIGIN, stamp=1_720_000_300, confirm=True)
    except Refuse as err:
        headless_card = err.code
    shown = " ".join(
        (
            repr(vault),
            repr(opened),
            repr(note),
            repr(light),
            repr(picked),
            repr(after),
            repr(vault.records()),
        )
    )
    return _Story(
        opened=opened,
        note=note,
        light=light,
        picked_ids=tuple(item.cred_id for item in picked.items),
        clamped=picked.clamped,
        secret_code=secret_code,
        bearer_code=bearer_code,
        headless_card=headless_card,
        unchanged=before == after,
        same_snapshot=after == rebuild(vault.records(), "interactive", detected=detected).snapshot(),
        shown_clean=_clean(shown),
        ids=vault.list_ids(),
    )


def test_example_credential_vault() -> None:
    first = _story()
    second = _story()
    assert first == second
    assert first.opened == Resolution(
        cred_id="cred-kiln",
        purpose=_ORIGIN,
        action="FILL",
        filled_fields=2,
        kind="card",
    )
    assert first.note.cred_id == "note-ship"
    assert first.note.kind == "address"
    assert first.note.action == "FILL"
    assert first.light.cred_id == "porch-light"
    assert first.light.action == "FILL"
    assert first.picked_ids == ("cred-kiln", "note-ship")
    assert first.clamped is True
    assert first.secret_code == "SECRET"
    assert first.bearer_code == "SECRET"
    assert first.headless_card == "HEADLESS"
    assert first.unchanged is True
    assert first.same_snapshot is True
    assert first.shown_clean is True
    assert first.ids == ("cred-kiln", "note-ship", "porch-light")


def test_schema_public_names_and_login() -> None:
    assert SCHEMA == "cosmos-hermes-credential_vault/1"
    assert list(vault_mod.__all__) == [
        "FIELD_CAP",
        "POLICY_BUDGET",
        "POLICY_CAP",
        "POLICY_HISTORY",
        "POLICY_ORIGINS",
        "SCHEMA",
        "CapNote",
        "CredentialVault",
        "Item",
        "Record",
        "Resolution",
        "Selection",
        "Snapshot",
        "rebuild",
        "store_plaintext",
    ]
    vault = CredentialVault("interactive")
    note = vault.put(
        "github-login",
        ("https://github.com",),
        kind="login",
        label="GitHub",
        login_id="ada@kiln.example",
        stamp=50,
    )
    opened = vault.resolve("github-login", "https://github.com", stamp=50)
    again = vault.resolve("github-login", "https://github.com", stamp=50)
    assert note.cred_id == "github-login"
    assert opened == again
    assert opened == Resolution(
        cred_id="github-login",
        purpose="https://github.com",
        action="FILL",
        filled_fields=1,
        kind="login",
    )
    assert type(opened) is Resolution
    assert vault.list_ids() == ("github-login",)
    assert vault.cap_note == CapNote(POLICY_CAP, POLICY_CAP, False)
    assert vault.session == "interactive"
    rebuilt = rebuild(vault.records(), "interactive")
    assert rebuilt.snapshot() == vault.snapshot()
    assert rebuilt.resolve("github-login", "https://github.com", stamp=50) == opened
    assert rebuild((), "interactive").snapshot() == CredentialVault("interactive").snapshot()


def test_cap_is_policy_and_small_cap_binds() -> None:
    high = CredentialVault("interactive", cap=90_000)
    assert high.cap_note == CapNote(applied=POLICY_CAP, requested=90_000, clamped=True)
    low = CredentialVault("interactive", cap=2)
    assert low.cap_note == CapNote(applied=2, requested=2, clamped=False)
    _put(low, "one", (_ORIGIN,), kind="login", label="One", stamp=1)
    _put(low, "two", (_ORIGIN,), kind="login", label="Two", stamp=2)
    with pytest.raises(Refuse) as caught:
        _put(low, "three", (_ORIGIN,), kind="login", label="Three", stamp=3)
    assert _code(caught.value) == "CAP"
    assert _detail(caught.value) == "2"
    assert low.list_ids() == ("one", "two")
    with pytest.raises(Refuse) as huge:
        CredentialVault("interactive", cap=1_000_001)
    assert _code(huge.value) == "OUT_OF_RANGE"


def test_select_skips_item_that_does_not_fit() -> None:
    vault = CredentialVault("interactive")
    _put(
        vault,
        "a-wide",
        (_ORIGIN,),
        kind="login",
        label="A" * 40,
        fields=FIELD_CAP,
        stamp=1,
    )
    _put(vault, "b-note", (_ORIGIN,), kind="address", label="Note", stamp=2)
    _put(vault, "c-lamp", (_LIGHT,), kind="login", label="Lamp", stamp=3)
    _put(vault, "d-fit", (_ORIGIN,), kind="login", label="Fit", stamp=4)
    wide = vault.item("a-wide", stamp=4)
    note = vault.item("b-note", stamp=4)
    fit = vault.item("d-fit", stamp=4)
    budget = note.weight() + fit.weight()
    assert wide.weight() > budget
    picked = vault.select(_ORIGIN, budget, stamp=4)
    assert tuple(item.cred_id for item in picked.items) == ("b-note", "d-fit")
    assert picked.skipped == ("a-wide",)
    assert picked.clamped is False
    assert picked.applied_budget == budget
    total = 0
    for item in picked.items:
        total += item.weight()
    assert total == budget
    clamped = vault.select(_ORIGIN, 10_000, stamp=4)
    assert clamped.applied_budget == POLICY_BUDGET
    assert clamped.requested_budget == 10_000
    assert clamped.clamped is True
    other = vault.select("https://other.example", 32, stamp=4)
    assert other.items == ()
    assert other.skipped == ()


def test_exact_origins_manager_and_wait() -> None:
    origins = (
        "https://amazon.co.uk",
        "https://www.amazon.co.uk",
        "https://eu.account.amazon.com",
    )
    vault = CredentialVault("interactive", detected=("bitwarden", "onepassword"))
    _put(
        vault,
        "shop-login",
        origins,
        kind="login",
        label="Shop",
        login_id="ada",
        source="bitwarden",
        stamp=1,
    )
    with pytest.raises(Refuse) as locked:
        vault.resolve("shop-login", "https://amazon.co.uk", stamp=1)
    assert _code(locked.value) == "LOCKED"
    vault.unlock("bitwarden", stamp=2)
    for origin in origins:
        got = vault.resolve("shop-login", origin, stamp=2)
        assert got.cred_id == "shop-login"
        assert got.purpose == origin
        assert got.action == "FILL"
    with pytest.raises(Refuse) as mismatch:
        vault.resolve("shop-login", "https://notamazon.co.uk", stamp=2)
    assert _code(mismatch.value) == "PURPOSE"
    assert str(mismatch.value) == "PURPOSE"
    _put(vault, "door-key", (_ORIGIN,), kind="passkey", label="Door", stamp=3)
    waited = vault.resolve("door-key", _ORIGIN, stamp=3)
    assert waited.action == "WAIT"
    assert waited.filled_fields == 0
    _put(vault, "duo-tap", (_ORIGIN,), kind="approval", label="Duo", stamp=4)
    approval = vault.resolve("duo-tap", _ORIGIN, stamp=4)
    assert approval.action == "WAIT"
    assert approval.kind == "approval"
    _put(vault, "totp-ada", (_ORIGIN,), kind="totp", label="Ada totp", stamp=5)
    minted = vault.resolve("totp-ada", _ORIGIN, stamp=5)
    assert minted.action == "FILL"
    with pytest.raises(Refuse) as sealed:
        vault.mint("totp-ada", stamp=5)
    assert _code(sealed.value) == "SEALED"
    with pytest.raises(Refuse) as reveal:
        vault.reveal()
    assert _code(reveal.value) == "SEALED"


def test_card_confirm_headless_and_disable() -> None:
    vault = CredentialVault("interactive", detected=("bitwarden",))
    _put(vault, "cred-kiln", (_ORIGIN,), kind="card", label="Kiln card", fields=2, stamp=1)
    with pytest.raises(Refuse) as need:
        vault.resolve("cred-kiln", _ORIGIN, stamp=1)
    assert _code(need.value) == "NEED_CONFIRM"
    filled = vault.resolve("cred-kiln", _ORIGIN, stamp=1, confirm=True)
    assert filled.filled_fields == 2
    _put(
        vault,
        "bw-shop",
        (_ORIGIN,),
        kind="login",
        label="Shop",
        source="bitwarden",
        stamp=2,
    )
    vault.disable("bitwarden", stamp=3)
    with pytest.raises(Refuse) as disabled:
        vault.resolve("bw-shop", _ORIGIN, stamp=3)
    assert _code(disabled.value) == "DISABLED"
    with pytest.raises(Refuse) as again:
        vault.unlock("bitwarden", stamp=4)
    assert _code(again.value) == "DISABLED"
    with pytest.raises(Refuse) as put_disabled:
        _put(
            vault,
            "bw-two",
            (_ORIGIN,),
            kind="login",
            label="Two",
            source="bitwarden",
            stamp=4,
        )
    assert _code(put_disabled.value) == "DISABLED"
    quiet = CredentialVault("headless", detected=("bitwarden",))
    _put(
        quiet,
        "bw-shop",
        (_ORIGIN,),
        kind="login",
        label="Shop",
        source="bitwarden",
        stamp=1,
    )
    with pytest.raises(Refuse) as unavailable:
        quiet.resolve("bw-shop", _ORIGIN, stamp=1)
    assert _code(unavailable.value) == "UNAVAILABLE"
    _put(quiet, "porch-light", (_LIGHT,), kind="login", label="Porch light", stamp=2)
    assert quiet.resolve("porch-light", _LIGHT, stamp=2).cred_id == "porch-light"
    with pytest.raises(Refuse) as missing:
        quiet.resolve("missing-id", _LIGHT, stamp=2)
    assert _code(missing.value) == "PROMPT_UNAVAILABLE"
    with pytest.raises(Refuse) as unlock:
        quiet.unlock("bitwarden", stamp=3)
    assert _code(unlock.value) == "HEADLESS"


def test_duplicate_remove_replay_and_stale() -> None:
    vault = CredentialVault("interactive", detected=("onepassword",))
    _put(vault, "cred-kiln", (_ORIGIN,), kind="login", label="Kiln", stamp=10)
    with pytest.raises(Refuse) as duplicate:
        _put(vault, "cred-kiln", (_LIGHT,), kind="login", label="Other", stamp=11)
    assert _code(duplicate.value) == "DUPLICATE"
    assert vault.resolve("cred-kiln", _ORIGIN, stamp=11).purpose == _ORIGIN
    with pytest.raises(Refuse) as stale:
        _put(vault, "other", (_ORIGIN,), kind="login", label="Other", stamp=10)
    assert _code(stale.value) == "STALE"
    with pytest.raises(Refuse) as early:
        vault.resolve("cred-kiln", _ORIGIN, stamp=9)
    assert _code(early.value) == "STALE"
    vault.remove("cred-kiln", stamp=12)
    assert vault.list_ids() == ()
    _put(vault, "cred-kiln", (_LIGHT,), kind="login", label="Moved", stamp=13)
    assert vault.resolve("cred-kiln", _LIGHT, stamp=13).kind == "login"
    with pytest.raises(Refuse) as old:
        vault.resolve("cred-kiln", _ORIGIN, stamp=13)
    assert _code(old.value) == "PURPOSE"
    with pytest.raises(Refuse) as missing:
        vault.remove("gone", stamp=14)
    assert _code(missing.value) == "UNKNOWN"
    with pytest.raises(Refuse) as unknown:
        vault.resolve("gone", _ORIGIN, stamp=14)
    assert _code(unknown.value) == "UNKNOWN"
    with pytest.raises(Refuse) as item:
        vault.item("gone", stamp=14)
    assert _code(item.value) == "UNKNOWN"
    with pytest.raises(Refuse) as mint:
        vault.mint("gone", stamp=14)
    assert _code(mint.value) == "UNKNOWN"
    vault.unlock("onepassword", stamp=15)
    with pytest.raises(Refuse) as replay:
        vault.unlock("onepassword", stamp=16)
    assert _code(replay.value) == "REPLAY"
    vault.disable("onepassword", stamp=17)
    with pytest.raises(Refuse) as disabled_again:
        vault.disable("onepassword", stamp=18)
    assert _code(disabled_again.value) == "REPLAY"
    ids = vault.list_ids()
    _put(vault, "zzz-extra", (_ORIGIN,), kind="login", label="Extra", stamp=19)
    assert ids == ("cred-kiln",)
    assert vault.list_ids() == ("cred-kiln", "zzz-extra")


def test_chain_and_bad_record() -> None:
    vault = CredentialVault("interactive")
    _put(vault, "cred-kiln", (_ORIGIN,), kind="login", label="Kiln", stamp=1)
    _put(vault, "note-ship", (_ORIGIN,), kind="address", label="Note", stamp=2)
    records = vault.records()
    broken = (_nth(records, 0), replace(_nth(records, 1), label="Tampered"))
    with pytest.raises(Refuse) as chain:
        rebuild(broken, "interactive")
    assert _code(chain.value) == "CHAIN"
    with pytest.raises(Refuse) as kind:
        rebuild((object(),), "interactive")
    assert _code(kind.value) == "BAD_RECORD"
    bad = Record(
        seq=1,
        stamp=1,
        op="NOPE",
        cred_id="cred-kiln",
        kind="login",
        origins=(_ORIGIN,),
        label="Kiln",
        login_id="",
        source="local",
        fields=1,
        prev="0" * 64,
        digest="0" * 64,
    )
    with pytest.raises(Refuse) as shape:
        rebuild((bad,), "interactive")
    assert _code(shape.value) == "BAD_RECORD"
    with pytest.raises(Refuse) as listed:
        rebuild([_nth(records, 0)], "interactive")
    assert _code(listed.value) == "NOT_TUPLE"
    with pytest.raises(Refuse) as tight:
        rebuild(records, "interactive", cap=1)
    assert _code(tight.value) == "CAP"


def test_secret_plaintext_and_repr() -> None:
    vault = CredentialVault("interactive")
    _put(vault, "kept", (_ORIGIN,), kind="login", label="Kept", stamp=1)
    samples = (_KEY, "sk-kilnkey1", _BEARER, "token=supersecret")
    for raw in samples:
        with pytest.raises(Refuse) as caught:
            vault.put(raw, (_ORIGIN,), kind="login", label="Nope", stamp=2)
        assert _code(caught.value) == "SECRET"
        assert raw not in str(caught.value)
        assert raw not in repr(vault)
    with pytest.raises(Refuse) as plain:
        vault.store_plaintext("a note for the kiln")
    assert _code(plain.value) == "PLAINTEXT"
    with pytest.raises(Refuse) as bearer:
        store_plaintext(_BEARER)
    assert _code(bearer.value) == "SECRET"
    assert vault.list_ids() == ("kept",)
    shown = " ".join((repr(vault), repr(vault.snapshot()), repr(vault.item("kept", stamp=1))))
    assert _clean(shown)
    assert "Kept" in repr(vault.item("kept", stamp=1))


def test_shape_and_type_refusals() -> None:
    vault = CredentialVault("interactive")
    with pytest.raises(Refuse) as empty:
        vault.put("", (_ORIGIN,), kind="login", label="Nope", stamp=1)
    assert _code(empty.value) == "EMPTY"
    with pytest.raises(Refuse) as blank_label:
        vault.put("cred-kiln", (_ORIGIN,), kind="login", label="", stamp=1)
    assert _code(blank_label.value) == "EMPTY"
    with pytest.raises(Refuse) as no_origin:
        vault.put("cred-kiln", (), kind="login", label="Kiln", stamp=1)
    assert _code(no_origin.value) == "EMPTY"
    with pytest.raises(Refuse) as bad_id:
        vault.put("HasCaps", (_ORIGIN,), kind="login", label="Kiln", stamp=1)
    assert _code(bad_id.value) == "BAD_ID"
    with pytest.raises(Refuse) as long_id:
        vault.put("a" * 33, (_ORIGIN,), kind="login", label="Kiln", stamp=1)
    assert _code(long_id.value) == "OVERSIZE"
    assert _detail(long_id.value) == "32"
    with pytest.raises(Refuse) as nul:
        vault.put("ab\x00", (_ORIGIN,), kind="login", label="Kiln", stamp=1)
    assert _code(nul.value) == "NULL_BYTE"
    with pytest.raises(Refuse) as kind:
        vault.put(3, (_ORIGIN,), kind="login", label="Kiln", stamp=1)
    assert _code(kind.value) == "NOT_TEXT"
    with pytest.raises(Refuse) as blob:
        vault.put(b"sealed-blob", (_ORIGIN,), kind="login", label="Kiln", stamp=1)
    assert _code(blob.value) == "NOT_TEXT"
    with pytest.raises(Refuse) as bad_origin:
        vault.put("cred-kiln", ("https://kiln.example/pay",), kind="login", label="Kiln", stamp=1)
    assert _code(bad_origin.value) == "BAD_ORIGIN"
    with pytest.raises(Refuse) as http:
        vault.put("cred-kiln", ("http://kiln.example",), kind="login", label="Kiln", stamp=1)
    assert _code(http.value) == "BAD_ORIGIN"
    with pytest.raises(Refuse) as label:
        vault.put("cred-kiln", (_ORIGIN,), kind="login", label="bad/label", stamp=1)
    assert _code(label.value) == "BAD_LABEL"
    with pytest.raises(Refuse) as login:
        vault.put("cred-kiln", (_ORIGIN,), kind="login", label="Kiln", login_id="has space", stamp=1)
    assert _code(login.value) == "BAD_LOGIN"
    with pytest.raises(Refuse) as bad_kind:
        vault.put("cred-kiln", (_ORIGIN,), kind="password", label="Kiln", stamp=1)
    assert _code(bad_kind.value) == "BAD_KIND"
    with pytest.raises(Refuse) as bad_source:
        vault.put("cred-kiln", (_ORIGIN,), kind="login", label="Kiln", source="keeper", stamp=1)
    assert _code(bad_source.value) == "BAD_SOURCE"
    with pytest.raises(Refuse) as not_tuple:
        vault.put("cred-kiln", _ORIGIN, kind="login", label="Kiln", stamp=1)
    assert _code(not_tuple.value) == "NOT_TUPLE"
    with pytest.raises(Refuse) as dup_origin:
        vault.put(
            "cred-kiln",
            (_ORIGIN, _ORIGIN),
            kind="login",
            label="Kiln",
            stamp=1,
        )
    assert _code(dup_origin.value) == "DUPLICATE"
    four = (
        "https://a.example",
        "https://b.example",
        "https://c.example",
        "https://d.example",
    )
    assert len(four) == POLICY_ORIGINS
    _put(vault, "many", four, kind="login", label="Many", stamp=1)
    with pytest.raises(Refuse) as too_many:
        vault.put("more", four + ("https://e.example",), kind="login", label="More", stamp=2)
    assert _code(too_many.value) == "CAP"
    assert _detail(too_many.value) == str(POLICY_ORIGINS)
    with pytest.raises(Refuse) as fields:
        vault.put("edge", (_ORIGIN,), kind="login", label="Edge", fields=0, stamp=2)
    assert _code(fields.value) == "OUT_OF_RANGE"
    with pytest.raises(Refuse) as flag:
        vault.put("edge", (_ORIGIN,), kind="login", label="Edge", fields=True, stamp=2)
    assert _code(flag.value) == "NOT_INT"
    with pytest.raises(Refuse) as confirm:
        vault.resolve("many", "https://a.example", stamp=1, confirm=1)
    assert _code(confirm.value) == "NOT_BOOL"
    assert vault.list_ids() == ("many",)


@pytest.mark.parametrize("mode", ["off", "yolo", "interactive "])
def test_no_off_switch(mode: str) -> None:
    with pytest.raises(Refuse) as caught:
        CredentialVault(mode)
    assert _code(caught.value) == "BAD_SESSION"


def test_remaining_bounds() -> None:
    with pytest.raises(Refuse) as missing:
        CredentialVault()
    assert _code(missing.value) == "NOT_TEXT"
    with pytest.raises(Refuse) as blank:
        CredentialVault("")
    assert _code(blank.value) == "EMPTY"
    with pytest.raises(Refuse) as flag:
        CredentialVault("interactive", cap=True)
    assert _code(flag.value) == "NOT_INT"
    with pytest.raises(Refuse) as zero:
        CredentialVault("interactive", cap=0)
    assert _code(zero.value) == "OUT_OF_RANGE"
    with pytest.raises(Refuse) as detected:
        CredentialVault("interactive", detected="bitwarden")
    assert _code(detected.value) == "NOT_TUPLE"
    with pytest.raises(Refuse) as local:
        CredentialVault("interactive", detected=("local",))
    assert _code(local.value) == "BAD_SOURCE"
    with pytest.raises(Refuse) as dup:
        CredentialVault("interactive", detected=("bitwarden", "bitwarden"))
    assert _code(dup.value) == "DUPLICATE"
    vault = CredentialVault("interactive")
    with pytest.raises(Refuse) as stamp:
        vault.put("cred-kiln", (_ORIGIN,), kind="login", label="Kiln", stamp=-1)
    assert _code(stamp.value) == "OUT_OF_RANGE"
    with pytest.raises(Refuse) as budget:
        vault.select(_ORIGIN, -1, stamp=0)
    assert _code(budget.value) == "OUT_OF_RANGE"
    with pytest.raises(Refuse) as budget_flag:
        vault.select(_ORIGIN, True, stamp=0)
    assert _code(budget_flag.value) == "NOT_INT"
    with pytest.raises(Refuse) as plain_kind:
        store_plaintext(None)
    assert _code(plain_kind.value) == "NOT_TEXT"
    with pytest.raises(Refuse) as nul:
        vault.store_plaintext("a\x00b")
    assert _code(nul.value) == "NULL_BYTE"
    other = CredentialVault("interactive")
    _put(vault, "cred-kiln", (_ORIGIN,), kind="login", label="Kiln", stamp=1)
    with pytest.raises(Refuse) as isolated:
        other.resolve("cred-kiln", _ORIGIN, stamp=1)
    assert _code(isolated.value) == "UNKNOWN"


def test_history_cap() -> None:
    vault = CredentialVault("interactive", cap=1)
    _put(vault, "box", (_ORIGIN,), kind="login", label="Box", stamp=1)
    stamp = 2
    for _ in range(63):
        vault.remove("box", stamp=stamp)
        stamp += 1
        _put(vault, "box", (_ORIGIN,), kind="login", label="Box", stamp=stamp)
        stamp += 1
    assert len(vault.records()) == 127
    vault.remove("box", stamp=stamp)
    stamp += 1
    assert len(vault.records()) == POLICY_HISTORY
    with pytest.raises(Refuse) as caught:
        _put(vault, "box", (_ORIGIN,), kind="login", label="Box", stamp=stamp)
    assert _code(caught.value) == "CAP"
    assert _detail(caught.value) == str(POLICY_HISTORY)


def test_item_fields_are_metadata_only() -> None:
    vault = CredentialVault("interactive")
    _put(vault, "cred-kiln", (_ORIGIN,), kind="card", label="Kiln card", fields=FIELD_CAP, stamp=1)
    found = vault.item("cred-kiln", stamp=1)
    assert isinstance(found, Item)
    assert found.fields == FIELD_CAP
    assert not hasattr(found, "sealed")
    assert not hasattr(found, "secret")
    text = repr(found)
    assert _ORIGIN in text
    assert "Kiln card" in text
    assert _clean(text)
