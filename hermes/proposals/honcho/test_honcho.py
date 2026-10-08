"""Honcho evidence log: dialectic notes rebuild, unknown peers refuse."""

from __future__ import annotations

from dataclasses import replace

import pytest

from cosmos_hermes import Refuse, secret_shape
from honcho import (
    DEPTH_CAP,
    GENESIS,
    NOTE_BUDGET,
    POLICY_CAP,
    SCHEMA,
    STORE_CAP,
    TEXT_CAP,
    Claim,
    DataRecord,
    Dialectic,
    Honcho,
    evidence_sha,
    rebuild,
)


def _enabled() -> Honcho:
    model = Honcho()
    model.enable()
    return model


def _nth_claim(items: tuple[Claim, ...], index: int) -> Claim:
    return items[index]


def _row(
    prev: str,
    text: str,
    seq: int,
    kind: str = "observe",
    pair: int = 0,
    principal: str = "ada",
    now: int | None = None,
) -> DataRecord:
    stamp = seq if now is None else now
    digest = evidence_sha(prev, principal, text, stamp, seq, kind, pair)
    return DataRecord(
        SCHEMA,
        "projection",
        principal,
        text,
        stamp,
        seq,
        kind,
        pair,
        POLICY_CAP,
        prev,
        digest,
    )


def _observe_rows(count: int) -> tuple[DataRecord, ...]:
    prev = GENESIS
    rows: list[DataRecord] = []
    for seq in range(1, count + 1):
        row = _row(prev, f"n{seq}", seq)
        rows.append(row)
        prev = row.sha
    return tuple(rows)


def test_disabled_until_enable() -> None:
    model = Honcho()
    with pytest.raises(Refuse) as observe_disabled:
        model.observe("ada", "likes tea", 1)
    assert observe_disabled.value.code == "DISABLED"
    with pytest.raises(Refuse) as contradict_disabled:
        model.contradict("ada", "likes tea", "hates tea", 1)
    assert contradict_disabled.value.code == "DISABLED"
    with pytest.raises(Refuse) as profile_disabled:
        model.profile("ada")
    assert profile_disabled.value.code == "DISABLED"
    with pytest.raises(Refuse) as notes_disabled:
        model.dialectic("ada")
    assert notes_disabled.value.code == "DISABLED"
    with pytest.raises(Refuse) as export_disabled:
        model.export_projection()
    assert export_disabled.value.code == "DISABLED"
    model.enable()
    model.enable()
    claim = model.observe("ada", "likes tea", 0)
    assert claim.now == 0
    assert claim.kind == "observe"
    assert claim.prev == GENESIS
    exported = model.export_projection()
    assert _nth_claim_record(exported).authority == "projection"


def _nth_claim_record(items: tuple[DataRecord, ...]) -> DataRecord:
    return items[0]


def test_secret_shape_raises_secret() -> None:
    model = _enabled()
    samples = (
        "sk-livekeyvalue",
        "Authorization: Bearer abcdefghijk",
        "token=supersecret",
        "password = hunter22",
    )
    for text in samples:
        with pytest.raises(Refuse) as caught:
            model.observe("ada", text, 1)
        assert caught.value.code == "SECRET"
    with pytest.raises(Refuse) as named:
        model.observe("api_key=supersecret", "likes tea", 1)
    assert named.value.code == "SECRET"
    with pytest.raises(Refuse) as paired:
        model.contradict("ada", "likes tea", "sk-livekeyvalue", 2)
    assert paired.value.code == "SECRET"
    assert model.export_projection() == ()
    with pytest.raises(Refuse) as built:
        Claim("ada", "sk-livekeyvalue", 1, 1, "observe", 0, GENESIS, "ab" * 32)
    assert built.value.code == "SECRET"
    kept = model.observe("ada", "likes tea", 1)
    with pytest.raises(Refuse):
        model.observe("ada", "sk-livekeyvalue", 2)
    nxt = model.observe("ada", "still here", 3)
    assert kept.seq == 1
    assert nxt.seq == 2


def test_contradict_keeps_both_and_profile_is_newest_first() -> None:
    model = _enabled()
    early = model.observe("ada", "likes tea", 1)
    left, right = model.contradict("ada", "morning person", "night owl", 5)
    later = model.observe("ada", "writes tests first", 5)
    other = model.observe("bea", "uses short replies", 9)
    assert left.pair == right.pair
    assert left.pair > 0
    assert right.prev == left.sha
    ada = model.profile("ada")
    assert [claim.text for claim in ada] == [
        "writes tests first",
        "night owl",
        "morning person",
        "likes tea",
    ]
    assert _nth_claim(ada, 0) == later
    assert _nth_claim(ada, 2) == left
    assert _nth_claim(ada, 3) == early
    assert model.profile("bea") == (other,)
    with pytest.raises(Refuse) as unknown:
        model.profile("cy")
    assert unknown.value.code == "UNKNOWN_PEER"
    with pytest.raises(Refuse) as unknown_notes:
        model.dialectic("Ada")
    assert unknown_notes.value.code == "UNKNOWN_PEER"
    records = model.export_projection()
    assert [record.seq for record in records] == [1, 2, 3, 4, 5]
    assert records[1].prev == records[0].sha
    assert {record.authority for record in records} == {"projection"}
    assert {record.schema for record in records} == {SCHEMA}
    assert {record.cap for record in records} == {POLICY_CAP}
    assert records[1].text == "morning person"
    assert records[2].text == "night owl"
    restored = rebuild(records)
    assert restored.export_projection() == records
    assert restored.profile("ada") == ada
    assert restored.dialectic("ada") == model.dialectic("ada")
    assert restored.dialectic("ada").authority == "projection"
    model.observe("ada", "one more", 10)
    assert restored.export_projection() == records


def test_profile_cap_is_policy() -> None:
    model = _enabled()
    for index in range(40):
        model.observe("ada", f"claim-{index}", index)
    view = model.profile("ada")
    assert len(view) == POLICY_CAP
    assert _nth_claim(view, 0).text == "claim-39"
    assert view[-1].text == "claim-8"
    inflated = model.profile("ada", 10_000)
    assert len(inflated) == POLICY_CAP
    assert model.recorded_cap == POLICY_CAP
    assert _nth_claim(inflated, 0).text == "claim-39"
    tight = model.profile("ada", 2)
    assert [claim.text for claim in tight] == ["claim-39", "claim-38"]
    assert model.recorded_cap == POLICY_CAP
    assert not secret_shape(repr(view[0]))
    assert not secret_shape(repr(model))
    assert not secret_shape(repr(model.export_projection()[0]))
    assert not secret_shape(repr(model.dialectic("ada")))


def test_store_cap_keeps_contradiction_atomic() -> None:
    model = _enabled()
    for index in range(STORE_CAP - 1):
        model.observe("ada", f"n{index}", index)
    with pytest.raises(Refuse) as blocked:
        model.contradict("ada", "left", "right", 1)
    assert blocked.value.code == "FULL"
    assert len(model.export_projection()) == STORE_CAP - 1
    model.observe("bea", "separate", 1)
    model.observe("ada", "last", STORE_CAP)
    with pytest.raises(Refuse) as overflow:
        model.observe("ada", "more", STORE_CAP)
    assert overflow.value.code == "FULL"
    assert len(model.profile("ada")) == POLICY_CAP
    seqs = [row.seq for row in model.export_projection()]
    assert seqs == list(range(1, len(seqs) + 1))
    with pytest.raises(Refuse) as replay_full:
        rebuild(_observe_rows(STORE_CAP + 1))
    assert replay_full.value.code == "FULL"
    fitted = rebuild(_observe_rows(STORE_CAP))
    assert len(fitted.profile("ada")) == POLICY_CAP


def test_edge_refusals() -> None:
    model = _enabled()
    cases: tuple[tuple[object, object, object], ...] = (
        ("", "likes tea", 1),
        ("ada", "   ", 1),
        ("ada", 12, 1),
        ("ada", "bad\x00byte", 1),
        ("ada", "x" * (TEXT_CAP + 1), 1),
        ("ada", "likes tea", True),
        ("ada", "likes tea", -1),
    )
    expected = (
        "EMPTY",
        "EMPTY",
        "NOT_TEXT",
        "NULL_BYTE",
        "OVERSIZE",
        "NOT_INT",
        "OUT_OF_RANGE",
    )
    for args, code in zip(cases, expected, strict=True):
        with pytest.raises(Refuse) as caught:
            model.observe(args[0], args[1], args[2])
        assert caught.value.code == code
    with pytest.raises(Refuse) as bad_cap:
        model.profile("ada", True)
    assert bad_cap.value.code == "NOT_INT"
    with pytest.raises(Refuse) as low_cap:
        model.profile("ada", 0)
    assert low_cap.value.code == "OUT_OF_RANGE"
    assert model.export_projection() == ()


def test_record_refuses_seed_handoff_and_bad_shape() -> None:
    digest = evidence_sha(GENESIS, "ada", "likes tea", 1, 1, "observe", 0)
    with pytest.raises(Refuse) as seed:
        DataRecord(SCHEMA, "seed", "ada", "likes tea", 1, 1, "observe", 0, POLICY_CAP, GENESIS, digest)
    assert seed.value.code == "NOT_SEED"
    with pytest.raises(Refuse) as handoff:
        DataRecord(
            SCHEMA,
            "handoff",
            "ada",
            "likes tea",
            1,
            1,
            "observe",
            0,
            POLICY_CAP,
            GENESIS,
            digest,
        )
    assert handoff.value.code == "NOT_HANDOFF"
    with pytest.raises(Refuse) as schema:
        DataRecord(
            "other",
            "projection",
            "ada",
            "likes tea",
            1,
            1,
            "observe",
            0,
            POLICY_CAP,
            GENESIS,
            digest,
        )
    assert schema.value.code == "BAD_SCHEMA"
    with pytest.raises(Refuse) as cap:
        DataRecord(
            SCHEMA,
            "projection",
            "ada",
            "likes tea",
            1,
            1,
            "observe",
            0,
            POLICY_CAP + 1,
            GENESIS,
            digest,
        )
    assert cap.value.code == "CAP"
    with pytest.raises(Refuse) as kind:
        DataRecord(
            SCHEMA,
            "projection",
            "ada",
            "likes tea",
            1,
            1,
            "seed",
            0,
            POLICY_CAP,
            GENESIS,
            "ab" * 32,
        )
    assert kind.value.code == "BAD_KIND"
    with pytest.raises(Refuse) as pair:
        Claim("ada", "likes tea", 1, 1, "observe", 1, GENESIS, GENESIS)
    assert pair.value.code == "BAD_PAIR"
    with pytest.raises(Refuse) as unpaired:
        Claim("ada", "likes tea", 1, 1, "contradict", 0, GENESIS, GENESIS)
    assert unpaired.value.code == "BAD_PAIR"
    with pytest.raises(Refuse) as bad_hash:
        Claim("ada", "likes tea", 1, 1, "observe", 0, "not-a-hash", "ab" * 32)
    assert bad_hash.value.code == "BAD_HASH"
    with pytest.raises(Refuse) as chain:
        Claim("ada", "likes tea", 1, 1, "observe", 0, GENESIS, "ab" * 32)
    assert chain.value.code == "CHAIN"


def test_notes_skip_items_that_do_not_fit() -> None:
    model = _enabled()
    model.observe("ada", "short", 1)
    model.observe("ada", "b" * 400, 2)
    model.observe("ada", "c" * 400, 3)
    tight = model.dialectic("ada", budget=450)
    assert [note.text for note in tight.notes] == ["c" * 400, "short"]
    assert tight.budget == 450
    assert tight.budget_cap == NOTE_BUDGET
    assert tight.used == 405
    assert model.recorded_budget == NOTE_BUDGET
    wide = model.dialectic("ada", budget=10_000)
    assert wide.budget == NOTE_BUDGET
    assert [note.text for note in wide.notes] == ["c" * 400, "short"]
    assert model.recorded_budget == NOTE_BUDGET
    tiny = model.dialectic("ada", budget=10)
    assert [note.text for note in tiny.notes] == ["short"]
    deep = model.dialectic("ada", depth=9)
    assert deep.depth == DEPTH_CAP
    assert deep.depth_cap == DEPTH_CAP
    assert model.recorded_depth == DEPTH_CAP
    mid = model.dialectic("ada", depth=2)
    assert mid.depth == 2
    assert mid.notes == deep.notes
    assert deep.authority == "projection"
    with pytest.raises(Refuse) as bad_depth:
        model.dialectic("ada", depth=True)
    assert bad_depth.value.code == "NOT_INT"
    with pytest.raises(Refuse) as low_depth:
        model.dialectic("ada", depth=0)
    assert low_depth.value.code == "OUT_OF_RANGE"
    with pytest.raises(Refuse) as low_budget:
        model.dialectic("ada", budget=0)
    assert low_budget.value.code == "OUT_OF_RANGE"
    huge = _enabled()
    huge.observe("ada", "x" * 50, 1)
    empty = huge.dialectic("ada", budget=10)
    assert empty.notes == ()
    assert huge.profile("ada")[0].text == "x" * 50
    with pytest.raises(Refuse) as bad_note:
        replace(empty, used=1)
    assert bad_note.value.code == "BAD_NOTE"
    with pytest.raises(Refuse) as handed:
        replace(empty, authority="handoff")
    assert handed.value.code == "NOT_HANDOFF"


def test_rebuild_refuses_malformed_chain() -> None:
    model = _enabled()
    model.observe("ada", "one", 1)
    model.observe("ada", "two", 2)
    model.observe("ada", "three", 3)
    rows = model.export_projection()
    first = rows[0]
    third = rows[2]
    with pytest.raises(Refuse) as dup:
        rebuild((first, first))
    assert dup.value.code == "DUP_ID"
    skipped = _row(GENESIS, "skip", 2)
    with pytest.raises(Refuse) as gap:
        rebuild((skipped,))
    assert gap.value.code == "BAD_SEQ"
    stale = _row(first.sha, "four", 4)
    with pytest.raises(Refuse) as stale_fence:
        rebuild((first, rows[1], third, stale))
    assert stale_fence.value.code == "STALE"
    broken = _row("cd" * 32, "x", 2)
    with pytest.raises(Refuse) as chain:
        rebuild((first, broken))
    assert chain.value.code == "CHAIN"
    with pytest.raises(Refuse) as dangling:
        rebuild((_row(GENESIS, "only", 1, "contradict", 1),))
    assert dangling.value.code == "BAD_PAIR"
    with pytest.raises(Refuse) as notes:
        rebuild(model.dialectic("ada").notes)
    assert notes.value.code == "BAD_RECORD"
    with pytest.raises(Refuse) as projected:
        rebuild(model.dialectic("ada"))
    assert projected.value.code == "BAD_RECORD"
    with pytest.raises(Refuse) as text:
        rebuild("projection")
    assert text.value.code == "BAD_RECORD"
    with pytest.raises(Refuse) as missing:
        rebuild(None)
    assert missing.value.code == "BAD_RECORD"
    empty = rebuild(())
    with pytest.raises(Refuse) as unknown:
        empty.dialectic("milo")
    assert unknown.value.code == "UNKNOWN_PEER"


def _story() -> tuple[Dialectic, tuple[DataRecord, ...]]:
    model = Honcho()
    model.enable()
    model.observe("ada", "session north-lamp starts with the desk card face up", 1_700_000_100)
    model.observe("ada", "the note on the card says the lamp stays warm", 1_700_000_200)
    model.observe("ada", "Ada prefers that lamp to the overhead light", 1_700_000_300)
    projected = model.dialectic("ada")
    rows = model.export_projection()
    restored = rebuild(rows)
    assert restored.dialectic("ada") == projected
    assert restored.export_projection() == rows
    assert projected.authority == "projection"
    assert projected.schema == SCHEMA
    assert tuple(note.text for note in projected.notes) == (
        "Ada prefers that lamp to the overhead light",
        "the note on the card says the lamp stays warm",
        "session north-lamp starts with the desk card face up",
    )
    with pytest.raises(Refuse) as unknown:
        restored.dialectic("milo")
    assert unknown.value.code == "UNKNOWN_PEER"
    return projected, rows


def test_example_honcho() -> None:
    assert _story() == _story()


def test_schema() -> None:
    assert SCHEMA == "cosmos-hermes-honcho/1"
