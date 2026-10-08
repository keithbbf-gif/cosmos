"""Projection tests for session_search. No network. No sqlite."""

from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path

import pytest

from cosmos_hermes import Refuse, redact, secret_shape
from cosmos_hermes.bounds import MAX_TEXT
from session_search import (
    DEFAULT_LIMIT,
    INDEX_CAP,
    MAX_TERMS,
    PAGE_TOKENS,
    POLICY_CAP,
    SCHEMA,
    Hit,
    IndexState,
    SearchResult,
    SessionSearch,
    Turn,
    clear,
    rebuild,
    records,
    search,
    stat_index,
)


def _hit(result: SearchResult, index: int) -> Hit:
    return result.hits[index]


def _turn(turns: tuple[Turn, ...], index: int) -> Turn:
    return turns[index]


def _story_turns() -> tuple[Turn, ...]:
    return (
        Turn("Mira", "porch-light", "The porch light stays on after dusk.", 1),
        Turn(
            "Mira",
            "library-card",
            "Renew the library card before Friday and check the porch light.",
            2,
        ),
        Turn(
            "Mira",
            "field-note",
            "Field note: porch light porch light and the library card.",
            3,
        ),
        Turn("Nia", "cellar-light", "porch light porch light porch light", 1),
    )


def _example() -> tuple[IndexState, SearchResult]:
    idx = SessionSearch()
    with pytest.raises(Refuse) as missing:
        idx.search("Mira", "porch light")
    assert missing.value.code == "UNMEASURED"
    state = idx.rebuild(_story_turns())
    found = idx.search("Mira", "porch light")
    again = idx.search("Mira", "porch light")
    assert again == found
    assert state.count == 4
    assert state.cap == POLICY_CAP
    assert found.schema == SCHEMA
    assert found.matched == 3
    assert found.terms == ("porch", "light")
    assert _hit(found, 0).session == "field-note"
    assert _hit(found, 0).weight == 4
    assert _hit(found, 0).place == 1
    assert _hit(found, 0).seq == 3
    assert _hit(found, 1).session == "porch-light"
    assert _hit(found, 1).weight == 2
    assert _hit(found, 2).session == "library-card"
    assert _hit(found, 2).owner == "Mira"
    assert found.hits[-1].session != "cellar-light"
    return state, found


def test_example_session_search() -> None:
    first = _example()
    second = _example()
    assert first == second
    _state, found = first
    assert _hit(found, 0).session == "field-note"
    assert _hit(found, 1).session == "porch-light"
    assert _hit(found, 2).session == "library-card"
    assert _hit(found, 0).text.startswith("Field note:")


def test_schema_and_unmeasured_before_rebuild() -> None:
    assert SCHEMA == "cosmos-hermes-session_search/1"
    idx = SessionSearch()
    assert repr(idx) == "SessionSearch(measured=False)"
    with pytest.raises(Refuse) as caught:
        idx.search("Mira", "porch")
    assert caught.value.code == "UNMEASURED"
    with pytest.raises(Refuse) as rows:
        idx.records()
    assert rows.value.code == "UNMEASURED"


def test_three_named_sessions_rank_and_hide_a_foreign_owner() -> None:
    idx = SessionSearch()
    state = idx.rebuild(_story_turns())
    found = idx.search("Mira", "porch   light", 1)
    assert state.index_cap == INDEX_CAP
    assert found.matched == 3
    assert found.limit == 1
    assert found.requested == 1
    assert _hit(found, 0).session == "field-note"
    assert idx.search("Nia", "porch light").matched == 1
    assert _hit(idx.search("Nia", "porch light"), 0).session == "cellar-light"
    fresh = SessionSearch()
    again = fresh.rebuild(idx.records())
    assert again.digest == state.digest
    assert fresh.search("Mira", "porch light") == idx.search("Mira", "porch light")


def test_success_owner_scope_and_casefold() -> None:
    idx = SessionSearch()
    idx.rebuild(
        (
            Turn("ada", "s1", "Auth refactor landed", 1),
            Turn("bob", "s2", "auth refactor elsewhere", 1),
            Turn("ada", "s3", "unrelated note", 1),
        )
    )
    found = idx.search("ada", "auth   Refactor")
    assert isinstance(found, SearchResult)
    assert found.schema == SCHEMA
    assert found.terms == ("auth", "Refactor")
    assert found.cap == POLICY_CAP
    assert found.page_tokens == PAGE_TOKENS
    assert found.limit == DEFAULT_LIMIT
    assert found.requested == DEFAULT_LIMIT
    assert found.matched == 1
    assert _hit(found, 0).owner == "ada"
    assert _hit(found, 0).session == "s1"
    assert _hit(found, 0).text == "Auth refactor landed"
    assert idx.search("ada", "auth missing").hits == ()
    with pytest.raises(Refuse) as padded:
        idx.search("ada ", "auth")
    assert padded.value.code == "BAD_PRINCIPAL"


def test_word_token_does_not_match_inside_a_longer_word() -> None:
    idx = SessionSearch()
    idx.rebuild(
        (
            Turn("ada", "notes", "author guidelines", 1),
            Turn("ada", "notes", "auth refactor landed", 2),
        )
    )
    found = idx.search("ada", "auth")
    assert found.matched == 1
    assert _hit(found, 0).seq == 2
    assert idx.search("ada", "auth refactor").matched == 1


def test_shorter_text_outranks_an_earlier_tie() -> None:
    idx = SessionSearch()
    idx.rebuild(
        (
            Turn("ada", "early-long", "porch light stays on after dusk tonight", 1),
            Turn("ada", "late-short", "porch light", 1),
        )
    )
    found = idx.search("ada", "porch light")
    assert _hit(found, 0).session == "late-short"
    assert _hit(found, 1).session == "early-long"
    assert _hit(found, 0).weight == _hit(found, 1).weight


def test_equal_weight_keeps_rebuild_order() -> None:
    idx = SessionSearch()
    idx.rebuild(
        (
            Turn("ada", "zeta", "porch light", 1),
            Turn("ada", "alpha", "porch light", 1),
        )
    )
    found = idx.search("ada", "porch light")
    assert _hit(found, 0).session == "zeta"
    assert _hit(found, 1).session == "alpha"


def test_page_budget_skips_a_huge_row_and_keeps_later_fits() -> None:
    idx = SessionSearch()
    giant = "needle " * (PAGE_TOKENS + 10)
    idx.rebuild(
        (
            Turn("ada", "small-note", "needle", 1),
            Turn("ada", "giant-note", giant, 1),
            Turn("ada", "mid-note", "needle later", 1),
        )
    )
    found = idx.search("ada", "needle")
    assert found.matched == 3
    assert found.page_tokens == PAGE_TOKENS
    assert tuple(hit.session for hit in found.hits) == ("small-note", "mid-note")
    stored = tuple(turn.session for turn in idx.records())
    assert "giant-note" in stored


def test_captain_sees_every_owner_and_plain_prefix_does_not() -> None:
    idx = SessionSearch()
    idx.rebuild(
        (
            Turn("ada", "s1", "shared topic", 1),
            Turn("bob", "s2", "shared topic", 1),
        )
    )
    seen = idx.search("captain:ada", "SHARED")
    assert {hit.owner for hit in seen.hits} == {"ada", "bob"}
    assert {hit.owner for hit in idx.search("captain:", "shared").hits} == {"ada", "bob"}
    assert [hit.owner for hit in idx.search("Captain:ada", "shared").hits] == []
    assert [hit.owner for hit in idx.search("ada", "shared").hits] == ["ada"]
    assert idx.search("captain-ada", "shared").hits == ()
    assert idx.search("stranger", "shared").hits == ()


def test_rebuild_replaces_and_failed_rebuild_keeps_prior() -> None:
    idx = SessionSearch()
    first = idx.rebuild((Turn("ada", "s1", "alpha", 1),))
    assert isinstance(first, IndexState)
    assert first.schema == SCHEMA
    assert first.count == 1
    assert first.cap == POLICY_CAP
    assert first.index_cap == INDEX_CAP
    with pytest.raises(Refuse) as secret:
        Turn("sk-livekeyvalue", "s2", "secret row", 1)
    assert secret.value.code == "SECRET"
    with pytest.raises(Refuse) as bad:
        idx.rebuild((Turn("ada", "s9", "beta", 1), object()))
    assert bad.value.code == "BAD_TURN"
    assert _hit(idx.search("ada", "alpha"), 0).text == "alpha"
    assert idx.search("ada", "beta").hits == ()
    with pytest.raises(Refuse) as duplicate:
        idx.rebuild(
            (
                Turn("ada", "s1", "beta", 1),
                Turn("ada", "s1", "beta again", 1),
            )
        )
    assert duplicate.value.code == "DUPLICATE"
    with pytest.raises(Refuse) as owners:
        idx.rebuild(
            (
                Turn("ada", "shared", "one note", 1),
                Turn("bob", "shared", "two note", 2),
            )
        )
    assert owners.value.code == "SESSION_OWNER"
    assert _hit(idx.search("ada", "alpha"), 0).session == "s1"
    second = idx.rebuild((Turn("ada", "s9", "beta", 1),))
    assert second.count == 1
    assert second.digest != first.digest
    assert idx.search("ada", "alpha").hits == ()
    assert _hit(idx.search("ada", "beta"), 0).session == "s9"
    copied = SessionSearch()
    assert copied.rebuild(idx.records()).digest == second.digest


def test_clear_makes_the_next_search_unmeasured() -> None:
    idx = SessionSearch()
    idx.rebuild((Turn("ada", "s1", "alpha", 1),))
    idx.clear()
    assert repr(idx) == "SessionSearch(measured=False)"
    with pytest.raises(Refuse) as caught:
        idx.search("ada", "alpha")
    assert caught.value.code == "UNMEASURED"
    with pytest.raises(Refuse) as rows:
        idx.records()
    assert rows.value.code == "UNMEASURED"
    state = idx.rebuild(())
    assert state.count == 0
    assert idx.search("ada", "alpha").hits == ()
    assert idx.search("ada", "alpha").matched == 0


def test_query_refuses_star_quotes_and_empty() -> None:
    idx = SessionSearch()
    idx.rebuild((Turn("ada", "s1", 'deploy* said "hi"', 1),))
    for query in ("deploy*", "*", 'auth "refactor"', "it's", "   \n\t", "...", "??"):
        with pytest.raises(Refuse) as caught:
            idx.search("ada", query)
        assert caught.value.code == "BAD_QUERY"
    words = " ".join(f"t{i}" for i in range(MAX_TERMS + 1))
    with pytest.raises(Refuse) as over_terms:
        idx.search("ada", words)
    assert over_terms.value.code == "BAD_QUERY"
    allowed = " ".join(f"t{i}" for i in range(MAX_TERMS))
    assert idx.search("ada", allowed).hits == ()
    found = idx.search("ada", "deploy")
    assert found.matched == 1
    assert "*" in _hit(found, 0).text


def test_secret_text_is_stored_only_after_redact() -> None:
    raw = "see sk-livekeyvalue Bearer abcdefghij token=supersecret"
    turn = Turn("ada", "s1", raw, 1)
    idx = SessionSearch()
    idx.rebuild((turn,))
    found = idx.search("ada", "see")
    stored = _hit(found, 0).text
    assert stored == redact(raw)
    assert "sk-livekeyvalue" not in stored
    assert "supersecret" not in stored
    assert secret_shape(stored) is False
    blob = repr(idx) + repr(found) + repr(_hit(found, 0)) + repr(turn)
    assert "sk-livekeyvalue" not in blob
    assert "supersecret" not in blob
    assert idx.search("ada", "livekeyvalue").hits == ()
    assert _hit(idx.search("ada", "redacted"), 0).text == stored


def test_policy_cap_is_recorded_and_not_raised() -> None:
    turns = tuple(Turn("ada", f"s{i}", "needle", 1) for i in range(POLICY_CAP + 10))
    idx = SessionSearch()
    state = idx.rebuild(turns)
    assert state.count == POLICY_CAP + 10
    assert state.cap == POLICY_CAP
    assert state.index_cap == INDEX_CAP
    high = idx.search("ada", "NEEDLE", POLICY_CAP + 1000)
    assert high.cap == POLICY_CAP
    assert high.page_tokens == PAGE_TOKENS
    assert high.limit == POLICY_CAP
    assert high.requested == POLICY_CAP + 1000
    assert len(high.hits) == POLICY_CAP
    assert _hit(high, 0).session == "s0"
    assert _hit(high, 1).session == "s1"
    assert _hit(high, POLICY_CAP - 1).session == f"s{POLICY_CAP - 1}"
    default = idx.search("ada", "needle")
    assert default.limit == DEFAULT_LIMIT
    assert default.requested == DEFAULT_LIMIT
    assert default.cap == POLICY_CAP
    assert len(default.hits) == DEFAULT_LIMIT
    exact = idx.search("ada", "needle", 3)
    assert exact.limit == 3
    assert exact.requested == 3
    assert len(exact.hits) == 3
    assert exact.cap == POLICY_CAP


def test_index_cap_refuses_and_keeps_prior() -> None:
    idx = SessionSearch()
    idx.rebuild((Turn("ada", "kept", "alpha", 1),))
    extra = tuple(Turn("ada", f"n{index}", "noise", 1) for index in range(INDEX_CAP + 1))
    with pytest.raises(Refuse) as caught:
        idx.rebuild(extra)
    assert caught.value.code == "OVER_COUNT"
    assert _hit(idx.search("ada", "alpha"), 0).session == "kept"
    assert idx.search("ada", "noise").hits == ()


def test_remaining_refusal_codes() -> None:
    idx = SessionSearch()
    idx.rebuild((Turn("ada", "s1", "hello", 1),))
    with pytest.raises(Refuse) as shape:
        idx.rebuild("nope")
    assert shape.value.code == "BAD_TURN"
    with pytest.raises(Refuse) as raw:
        idx.rebuild(b"nope")
    assert raw.value.code == "BAD_TURN"
    with pytest.raises(Refuse) as blank:
        Turn("ada", "  ", "hello", 1)
    assert blank.value.code == "BAD_TURN"
    with pytest.raises(Refuse) as empty_text:
        Turn("ada", "s2", "   ", 1)
    assert empty_text.value.code == "BAD_TURN"
    with pytest.raises(Refuse) as tokens:
        Turn("ada", "s2", "???", 1)
    assert tokens.value.code == "BAD_TURN"
    with pytest.raises(Refuse) as item:
        idx.rebuild((object(),))
    assert item.value.code == "BAD_TURN"
    assert _hit(idx.search("ada", "hello"), 0).text == "hello"
    with pytest.raises(Refuse) as who:
        idx.search("", "hello")
    assert who.value.code == "BAD_PRINCIPAL"
    with pytest.raises(Refuse) as secret_query:
        idx.search("ada", "sk-livekeyvalue")
    assert secret_query.value.code == "SECRET"
    with pytest.raises(Refuse) as secret_who:
        idx.search("sk-livekeyvalue", "hello")
    assert secret_who.value.code == "SECRET"
    with pytest.raises(Refuse) as secret_session:
        Turn("ada", "sk-livekeyvalue", "hello", 1)
    assert secret_session.value.code == "SECRET"
    with pytest.raises(Refuse) as not_text:
        idx.search(3, "hello")
    assert not_text.value.code == "NOT_TEXT"
    with pytest.raises(Refuse) as nul:
        idx.search("ada", "bad\x00term")
    assert nul.value.code == "NULL_BYTE"
    with pytest.raises(Refuse) as over:
        idx.search("ada", "a" * (MAX_TEXT + 1))
    assert over.value.code == "OVERSIZE"
    with pytest.raises(Refuse) as not_int:
        idx.search("ada", "hello", "9")
    assert not_int.value.code == "NOT_INT"
    with pytest.raises(Refuse) as flag:
        idx.search("ada", "hello", True)
    assert flag.value.code == "NOT_INT"
    with pytest.raises(Refuse) as seq_flag:
        Turn("ada", "s2", "hello", True)
    assert seq_flag.value.code == "NOT_INT"
    with pytest.raises(Refuse) as low:
        idx.search("ada", "hello", 0)
    assert low.value.code == "OUT_OF_RANGE"
    with pytest.raises(Refuse) as seq_low:
        Turn("ada", "s2", "hello", -1)
    assert seq_low.value.code == "OUT_OF_RANGE"


def test_stat_index_missing_file_is_unmeasured_and_creates_nothing() -> None:
    folder = tempfile.mkdtemp(prefix="session_search_")
    try:
        missing_root = os.path.join(folder, "no-such-index")
        with pytest.raises(Refuse) as missing:
            stat_index(missing_root, "recall.sqlite")
        assert missing.value.code == "UNMEASURED"
        assert os.path.exists(missing_root) is False
        assert os.listdir(folder) == []
        target = Path(folder) / "recall.sqlite"
        assert target.exists() is False
        with pytest.raises(Refuse) as absent:
            stat_index(folder, "recall.sqlite")
        assert absent.value.code == "UNMEASURED"
        assert target.exists() is False
        assert not os.path.exists(str(target) + "-wal")
        assert not os.path.exists(str(target) + "-shm")
        target.write_bytes(b"")
        with pytest.raises(Refuse) as foreign:
            stat_index(folder, "recall.sqlite")
        assert foreign.value.code == "FOREIGN_INDEX"
        assert target.read_bytes() == b""
        assert list(Path(folder).iterdir()) == [target]
        assert not os.path.exists(str(target) + "-wal")
        assert not os.path.exists(str(target) + "-shm")
    finally:
        shutil.rmtree(folder)


def test_stat_index_path_shapes() -> None:
    samples = (
        ("", "recall.sqlite", "NO_GRANT"),
        ("relative-root", "recall.sqlite", "RELATIVE_GRANT"),
        ("C:\\", "recall.sqlite", "DRIVE_ROOT"),
        ("C:recall.sqlite", "recall.sqlite", "DRIVE_RELATIVE"),
        ("\\\\host\\share", "recall.sqlite", "UNC"),
        ("file:///C:/temp", "recall.sqlite", "FILE_URL"),
        ("C:/temp/%2e%2e/x", "recall.sqlite", "ENCODED_DOTDOT"),
        ("C:/temp/../x", "recall.sqlite", "DOTDOT"),
        ("C:/temp/foo:bar", "recall.sqlite", "ALT_STREAM"),
        ("C:/temp/foo./bar", "recall.sqlite", "TRAILING_DOT"),
        ("C:/temp/\x00", "recall.sqlite", "NULL_BYTE"),
        ("C:/temp/ok", "..", "BAD_PATH"),
        ("C:/temp/ok", "", "BAD_PATH"),
        ("C:/temp/ok", "a/b", "BAD_PATH"),
        ("C:/temp/sk-livekeyvalue", "recall.sqlite", "SECRET"),
        ("C:/temp/ok", "sk-livekeyvalue", "SECRET"),
    )
    for root, name, code in samples:
        with pytest.raises(Refuse) as caught:
            stat_index(root, name)
        assert caught.value.code == code
    with pytest.raises(Refuse) as kind:
        stat_index(1, "recall.sqlite")
    assert kind.value.code == "BAD_PATH"


def test_module_index_follows_rebuild_and_clear() -> None:
    clear()
    try:
        with pytest.raises(Refuse) as before:
            search("Mira", "alpha")
        assert before.value.code == "UNMEASURED"
        with pytest.raises(Refuse) as no_rows:
            records()
        assert no_rows.value.code == "UNMEASURED"
        state = rebuild((Turn("Mira", "porch-light", "alpha lamp", 1),))
        assert state.count == 1
        assert len(search("Mira", "alpha").hits) == 1
        assert search("Nia", "alpha").hits == ()
        assert _turn(records(), 0).session == "porch-light"
        clear()
        with pytest.raises(Refuse) as after:
            search("Mira", "alpha")
        assert after.value.code == "UNMEASURED"
    finally:
        clear()
