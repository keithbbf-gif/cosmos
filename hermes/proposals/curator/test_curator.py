"""Curator select skips oversized notes and does not call a model."""

from __future__ import annotations

from typing import cast

import pytest

from cosmos_hermes import Refuse, secret_shape
from curator import (
    ID_LIMIT,
    POLICY_BUDGET,
    PRIORITY_MAX,
    PRIORITY_MIN,
    SCHEMA,
    TEXT_LIMIT,
    Candidate,
    Drop,
    Records,
    Selection,
    curate,
    rebuild,
    records,
    select,
)

_LIGHT = (
    "Mira walked the porch light and wrote down every bulb, switch, and timer. " * 6
)


def _at(items: tuple[Candidate, ...], index: int) -> Candidate:
    if index < 0 or index >= len(items):
        raise AssertionError(index)
    return items[index]


def _drop(review: Selection, index: int) -> Drop:
    if index < 0 or index >= len(review.dropped):
        raise AssertionError(index)
    return review.dropped[index]


def _mira_notes() -> tuple[Candidate, ...]:
    return (
        Candidate("porch-light", _LIGHT, 9),
        Candidate("vault-note", "sk-livekeyvalue", 8),
        Candidate("porch-card", "Card for the lamp Mira fixed.", 4),
        Candidate("bench-note", "Bench checklist is longer than the card and does not fit.", 2),
        Candidate("session-note", "Session closed.", 1),
    )


def test_example_curator() -> None:
    """Mira's porch card stays, and the later session note still fits."""
    notes = _mira_notes()
    first = select(notes, 50)
    second = select(notes, 50)
    assert first == second
    assert tuple(item.id for item in first) == ("porch-card", "session-note")
    assert _at(first, 0).text == "Card for the lamp Mira fixed."
    assert _at(first, 1).id == "session-note"
    assert _at(first, 1).text == "Session closed."
    review = curate(notes, 50)
    assert review.schema == SCHEMA == "cosmos-hermes-curator/1"
    assert review.chosen == first
    assert review.cap == POLICY_BUDGET
    assert review.budget == 50
    assert curate(notes, 50) == review
    assert rebuild(records(review)) == review
    assert secret_shape(repr(review)) is False
    assert "sk-" not in repr(review)


def test_later_smaller_note_is_kept() -> None:
    notes = (
        Candidate("large-note", "x" * 40, 9),
        Candidate("small-note", "lamp", 1),
    )
    assert tuple(item.id for item in select(notes, 10)) == ("small-note",)
    review = curate(notes, 10)
    assert _drop(review, 0).id == "large-note"
    assert _drop(review, 0).reason == "OVERSIZE"
    assert _at(review.chosen, 0).id == "small-note"


def test_rank_is_priority_then_id() -> None:
    tied = (
        Candidate("z-note", "zz", 4),
        Candidate("m-note", "mm", 4),
        Candidate("a-note", "aa", 4),
    )
    assert tuple(item.id for item in select(tied, 100)) == ("a-note", "m-note", "z-note")
    ranked = (
        Candidate("a-note", "aa", 1),
        Candidate("z-note", "zz", 7),
    )
    assert tuple(item.id for item in select(ranked, 100)) == ("z-note", "a-note")
    floor = Candidate("low-note", "ok", PRIORITY_MIN)
    ceiling = Candidate("top-note", "ok", PRIORITY_MAX)
    assert tuple(item.id for item in select((floor, ceiling), 10)) == ("top-note", "low-note")


def test_zero_budget_returns_empty_tuple() -> None:
    notes = _mira_notes()
    assert all(len(item.text.encode("utf-8")) > 0 for item in notes)
    assert select(notes, 0) == ()
    review = curate(notes, 0)
    assert review.chosen == ()
    assert review.used == 0
    assert review.budget == 0
    assert review.cap == POLICY_BUDGET
    assert rebuild(records(review)) == review
    assert rebuild(records(review)) is not review


def test_secret_text_is_dropped_and_repr_stays_clean() -> None:
    shapes = (
        ("vault-note", "sk-livekeyvalue"),
        ("bearer-note", "Bearer abcdefghijk"),
        ("assign-note", "api_key=abcdefghij"),
    )
    notes = tuple(Candidate(note_id, raw, 3 - index) for index, (note_id, raw) in enumerate(shapes))
    for note in notes:
        assert secret_shape(repr(note)) is False
    kept = Candidate("session-note", "Session closed.", 0)
    review = curate(notes + (kept,), 100)
    assert review.chosen == (kept,)
    assert tuple(item.reason for item in review.dropped) == ("SECRET", "SECRET", "SECRET")
    assert secret_shape(repr(review)) is False
    secrets_only = curate(notes, 100)
    assert secrets_only.chosen == ()
    assert secrets_only.used == 0
    assert rebuild(records(secrets_only)) == secrets_only


def test_duplicate_ids_refuse() -> None:
    notes = (
        Candidate("porch-card", "one card", 1),
        Candidate("porch-card", "other card", 2),
    )
    with pytest.raises(Refuse) as caught:
        select(notes, 100)
    assert caught.value.code == "DUP_ID"
    with pytest.raises(Refuse) as secret_dup:
        select(
            (
                Candidate("vault-note", "sk-livekeyvalue", 1),
                Candidate("vault-note", "plain", 2),
            ),
            100,
        )
    assert secret_dup.value.code == "DUP_ID"


def test_higher_budget_is_ignored() -> None:
    body = "x" * 4000
    count = POLICY_BUDGET // 4000 + 1
    notes = tuple(Candidate(f"n{index:03d}", body, 1) for index in range(count))
    review = curate(notes, POLICY_BUDGET + 4000)
    assert review.cap == POLICY_BUDGET
    assert review.budget == POLICY_BUDGET
    assert review.used == POLICY_BUDGET
    assert len(review.chosen) == POLICY_BUDGET // 4000
    assert len(review.dropped) == 1
    assert _drop(review, 0).id == f"n{POLICY_BUDGET // 4000:03d}"
    assert _drop(review, 0).reason == "OVERSIZE"
    lower = curate(notes[:2], 4000)
    assert lower.budget == 4000
    assert lower.cap == POLICY_BUDGET
    assert tuple(item.id for item in lower.chosen) == ("n000",)
    wide = Candidate("wide-note", "y" * TEXT_LIMIT, 1)
    assert select((wide,), TEXT_LIMIT) == (wide,)


def test_utf8_bytes_and_newline() -> None:
    accent = Candidate("accent-note", "é", 1)
    assert select((accent,), 1) == ()
    assert select((accent,), 2) == (accent,)
    lines = Candidate("session-note", "line one\nline two", 1)
    assert select((lines,), 100) == (lines,)


def test_rebuild_and_record_refusals() -> None:
    review = curate(_mira_notes(), 50)
    bundle = records(review)
    again = rebuild(bundle)
    assert again == review
    assert again is not review
    stale = Records(
        bundle.schema,
        bundle.cap,
        bundle.budget,
        bundle.chosen,
        bundle.dropped,
        bundle.used,
        "0" * 64,
    )
    with pytest.raises(Refuse) as bad_digest:
        rebuild(stale)
    assert bad_digest.value.code == "STALE"
    shape = Records(
        bundle.schema,
        bundle.cap,
        bundle.budget,
        bundle.chosen,
        bundle.dropped,
        bundle.used,
        "z" * 64,
    )
    with pytest.raises(Refuse) as bad_shape:
        rebuild(shape)
    assert bad_shape.value.code == "BAD_RECORD"
    with pytest.raises(Refuse) as mismatch:
        rebuild(
            Records(
                "cosmos-hermes-curator/9",
                bundle.cap,
                bundle.budget,
                bundle.chosen,
                bundle.dropped,
                bundle.used,
                bundle.digest,
            )
        )
    assert mismatch.value.code == "MISMATCH"
    with pytest.raises(Refuse) as raised_cap:
        rebuild(
            Records(
                SCHEMA,
                POLICY_BUDGET + 5,
                bundle.budget,
                bundle.chosen,
                bundle.dropped,
                bundle.used,
                bundle.digest,
            )
        )
    assert raised_cap.value.code == "MISMATCH"
    with pytest.raises(Refuse) as not_records:
        rebuild(review)
    assert not_records.value.code == "BAD_RECORD"
    with pytest.raises(Refuse) as not_selection:
        records(bundle)
    assert not_selection.value.code == "BAD_RECORD"
    with pytest.raises(Refuse) as bad_row:
        rebuild(
            Records(
                SCHEMA,
                POLICY_BUDGET,
                50,
                cast(tuple[Candidate, ...], ("nope",)),
                (),
                0,
                "ab" * 32,
            )
        )
    assert bad_row.value.code == "BAD_RECORD"
    planted = Candidate("vault-note", "sk-livekeyvalue", 1)
    with pytest.raises(Refuse) as planted_secret:
        rebuild(
            Records(
                SCHEMA,
                POLICY_BUDGET,
                100,
                (planted,),
                (),
                len(planted.text.encode("utf-8")),
                "cd" * 32,
            )
        )
    assert planted_secret.value.code == "SECRET"


def test_input_refusals() -> None:
    with pytest.raises(Refuse) as empty_notes:
        select((), 10)
    assert empty_notes.value.code == "EMPTY"
    with pytest.raises(Refuse) as empty_text:
        Candidate("porch-card", "", 1)
    assert empty_text.value.code == "EMPTY"
    with pytest.raises(Refuse) as empty_id:
        Candidate("", "lamp", 1)
    assert empty_id.value.code == "EMPTY"
    with pytest.raises(Refuse) as bad_items:
        select([Candidate("porch-card", "lamp", 1)], 10)
    assert bad_items.value.code == "BAD_ITEMS"
    with pytest.raises(Refuse) as bad_member:
        select((Candidate("porch-card", "lamp", 1), "nope"), 10)
    assert bad_member.value.code == "BAD_ITEMS"
    with pytest.raises(Refuse) as bad_id:
        Candidate("a/b", "lamp", 1)
    assert bad_id.value.code == "BAD_ID"
    with pytest.raises(Refuse) as hidden:
        Candidate("porch-card", "lamp\u202e", 1)
    assert hidden.value.code == "INVISIBLE"
    with pytest.raises(Refuse) as nul:
        Candidate("porch-card", "a\x00b", 1)
    assert nul.value.code == "NULL_BYTE"
    with pytest.raises(Refuse) as over_text:
        Candidate("porch-card", "x" * (TEXT_LIMIT + 1), 1)
    assert over_text.value.code == "OVERSIZE"
    assert over_text.value.detail == str(TEXT_LIMIT)
    with pytest.raises(Refuse) as over_id:
        Candidate("a" * (ID_LIMIT + 1), "lamp", 1)
    assert over_id.value.code == "OVERSIZE"
    with pytest.raises(Refuse) as not_text:
        Candidate(cast(str, 3), "lamp", 1)
    assert not_text.value.code == "NOT_TEXT"
    with pytest.raises(Refuse) as raw_bytes:
        Candidate("porch-card", cast(str, b"lamp"), 1)
    assert raw_bytes.value.code == "NOT_TEXT"
    with pytest.raises(Refuse) as surrogate:
        Candidate("porch-card", "\ud800", 1)
    assert surrogate.value.code == "NOT_TEXT"
    with pytest.raises(Refuse) as flag:
        Candidate("porch-card", "lamp", True)
    assert flag.value.code == "NOT_INT"
    with pytest.raises(Refuse) as budget_flag:
        select((Candidate("porch-card", "lamp", 1),), True)
    assert budget_flag.value.code == "NOT_INT"
    with pytest.raises(Refuse) as low:
        Candidate("porch-card", "lamp", PRIORITY_MIN - 1)
    assert low.value.code == "OUT_OF_RANGE"
    with pytest.raises(Refuse) as high:
        Candidate("porch-card", "lamp", PRIORITY_MAX + 1)
    assert high.value.code == "OUT_OF_RANGE"
    with pytest.raises(Refuse) as negative:
        select((Candidate("porch-card", "lamp", 1),), -1)
    assert negative.value.code == "OUT_OF_RANGE"
    for raw in ("sk-livekeyvalue", "Bearer abcdefghijk", "api_key=abcdefghij"):
        with pytest.raises(Refuse) as secret:
            Candidate(raw, "lamp", 1)
        assert secret.value.code == "SECRET"
