"""Majority tally: counts, ties, caps, and secret refusal."""

from __future__ import annotations

import inspect
from typing import cast

import pytest

import mixture
from cosmos_hermes import Refuse, secret_shape
from mixture import (
    MODEL_ID_CAP,
    OUTPUT_CAP,
    POLICY_CAP,
    POLICY_MIN,
    SCHEMA,
    Verdict,
    aggregate,
    rebuild,
)


def _ids(count: int) -> list[str]:
    return [f"m{index}" for index in range(count)]


def _verdict(
    *,
    schema: str = SCHEMA,
    text: str = "yes",
    model_id: str = "aa",
    model_ids: tuple[str, ...] = ("aa", "bb"),
    texts: tuple[str, ...] = ("yes", "yes"),
    index: int = 0,
    votes: int = 2,
    spend_count: int = 2,
    cap: int = POLICY_CAP,
    applied_cap: int = POLICY_CAP,
    requested_cap: int = POLICY_CAP,
) -> Verdict:
    return Verdict(
        schema=schema,
        text=text,
        model_id=model_id,
        model_ids=model_ids,
        texts=texts,
        index=index,
        votes=votes,
        spend_count=spend_count,
        cap=cap,
        applied_cap=applied_cap,
        requested_cap=requested_cap,
    )


def _session_panel() -> tuple[tuple[str, str, str], tuple[str, str, str]]:
    reviewers = ("mira-card", "nolan-note", "ade-light")
    scores = (
        "Keep the porch card with the session note.",
        "Revise the porch light line.",
        "Keep the porch card with the session note.",
    )
    return reviewers, scores


def test_example_mixture() -> None:
    def once() -> tuple[Verdict, str]:
        reviewers, scores = _session_panel()
        winner = aggregate(reviewers, scores, requested_cap=3)
        assert rebuild(winner) == winner
        with pytest.raises(Refuse) as caught:
            aggregate(
                ("mira-card", "nolan-note"),
                (
                    "Keep the porch card with the session note.",
                    "Revise the porch light line.",
                ),
            )
        message = str(caught.value)
        assert "porch" not in message
        assert "session" not in message
        assert caught.value.code == "TIE"
        return winner, caught.value.code

    first = once()
    second = once()
    assert first == second
    winner = first[0]
    assert winner.schema == SCHEMA
    assert winner.text == "Keep the porch card with the session note."
    assert winner.model_id == "mira-card"
    assert winner.index == 0
    assert winner.votes == 2
    assert winner.spend_count == 3
    assert winner.cap == POLICY_CAP == 5
    assert winner.applied_cap == 3
    assert winner.requested_cap == 3
    assert winner.texts[2] == winner.text
    assert first[1] == "TIE"


def test_schema_and_public_names() -> None:
    assert SCHEMA == "cosmos-hermes-mixture/1"
    assert POLICY_MIN == 2
    assert POLICY_CAP == 5
    assert set(mixture.__all__) == {
        "MODEL_ID_CAP",
        "OUTPUT_CAP",
        "POLICY_CAP",
        "POLICY_MIN",
        "SCHEMA",
        "Verdict",
        "aggregate",
        "rebuild",
    }


def test_majority_spend_and_first_model() -> None:
    got = aggregate(
        ["openai-codex:gpt-5.5", "openrouter:deepseek/deepseek-v4-pro", "aa"],
        ["plan", "other", "plan"],
    )
    assert got.schema == SCHEMA
    assert got.text == "plan"
    assert got.model_id == "openai-codex:gpt-5.5"
    assert got.model_ids == (
        "openai-codex:gpt-5.5",
        "openrouter:deepseek/deepseek-v4-pro",
        "aa",
    )
    assert got.texts == ("plan", "other", "plan")
    assert got.index == 0
    assert got.votes == 2
    assert got.spend_count == 3
    assert got.spend_count == len(got.model_ids)
    assert got.cap == POLICY_CAP
    assert got.applied_cap == POLICY_CAP
    assert got.requested_cap == POLICY_CAP
    later = aggregate(["aa", "bb", "cc"], ["no", "yes", "yes"])
    assert later.text == "yes"
    assert later.model_id == "bb"
    assert later.index == 1
    assert later.votes == 2
    assert later.spend_count == 3
    assert later.texts[1] == "yes"
    empty = aggregate(["aa", "bb", "cc"], ["", "", "x"])
    assert empty.text == ""
    assert empty.votes == 2
    assert empty.model_id == "aa"
    full = aggregate(_ids(5), ["same"] * 5)
    assert full.votes == 5
    assert full.spend_count == 5
    assert full.text == "same"
    split = aggregate(_ids(5), ["same", "other", "same", "third", "fourth"])
    assert split.text == "same"
    assert split.votes == 2
    assert split.spend_count == 5
    four = aggregate(_ids(4), ["a", "b", "a", "a"])
    assert four.text == "a"
    assert four.votes == 3
    assert four.spend_count == 4
    blob = repr(got) + repr(later) + repr(full)
    assert secret_shape(blob) is False
    assert "sk-" not in blob
    assert "api_key" not in blob
    assert "Bearer" not in blob
    assert rebuild(got) == got
    assert rebuild(got) is not got


def test_same_inputs_match_and_default_cap_matches_explicit() -> None:
    ids = ["aa", "bb"]
    texts = ["plan", "plan"]
    assert aggregate(ids, texts) == aggregate(tuple(ids), tuple(texts), requested_cap=5)


def test_tie_does_not_pick() -> None:
    cases: tuple[tuple[tuple[str, ...], tuple[str, ...]], ...] = (
        (("aa", "bb"), ("left", "right")),
        (("a1", "a2", "b1", "b2"), ("red", "blue", "red", "blue")),
        (("aa", "bb", "cc"), ("one", "two", "three")),
        (tuple(_ids(5)), ("a", "a", "b", "b", "c")),
        (("aa", "bb"), ("Yes", "yes")),
        (("aa", "bb"), ("plan", "plan ")),
    )
    for ids, texts in cases:
        with pytest.raises(Refuse) as caught:
            aggregate(ids, texts)
        assert caught.value.code == "TIE"
        message = str(caught.value)
        for text in texts:
            if text != "":
                assert text not in message


def test_bad_count_and_mismatch() -> None:
    with pytest.raises(Refuse) as caught:
        aggregate(["aa"], ["only"])
    assert caught.value.code == "BAD_COUNT"
    assert caught.value.detail == "1"
    with pytest.raises(Refuse) as caught:
        aggregate([], [])
    assert caught.value.code == "BAD_COUNT"
    assert caught.value.detail == "0"
    with pytest.raises(Refuse) as caught:
        aggregate(_ids(6), ["a"] * 6)
    assert caught.value.code == "BAD_COUNT"
    assert caught.value.detail == "6"
    with pytest.raises(Refuse) as caught:
        aggregate(["aa"], ["x", "y"])
    assert caught.value.code == "BAD_COUNT"
    assert caught.value.detail == "1"
    with pytest.raises(Refuse) as caught:
        aggregate(["aa", "bb"], ["x", "y", "z"])
    assert caught.value.code == "MISMATCH"
    assert caught.value.detail == "2:3"
    with pytest.raises(Refuse) as caught:
        aggregate("abcd", ["aa", "bb"])
    assert caught.value.code == "BAD_COUNT"
    with pytest.raises(Refuse) as caught:
        aggregate(["aa", "bb"], b"abcd")
    assert caught.value.code == "BAD_COUNT"
    with pytest.raises(Refuse) as caught:
        aggregate(None, ["aa", "bb"])
    assert caught.value.code == "BAD_COUNT"

    class Pair(tuple[str, ...]):
        pass

    with pytest.raises(Refuse) as caught:
        aggregate(Pair(("aa", "bb")), ["x", "x"])
    assert caught.value.code == "BAD_COUNT"
    with pytest.raises(Refuse) as caught:
        aggregate(range(2), ["x", "x"])
    assert caught.value.code == "BAD_COUNT"


def test_bad_model_and_secret() -> None:
    with pytest.raises(Refuse) as caught:
        aggregate(["aa", ""], ["x", "x"])
    assert caught.value.code == "BAD_MODEL"
    with pytest.raises(Refuse) as caught:
        aggregate(["aa", " "], ["x", "x"])
    assert caught.value.code == "BAD_MODEL"
    with pytest.raises(Refuse) as caught:
        aggregate(["aa", "a..b"], ["x", "x"])
    assert caught.value.code == "BAD_MODEL"
    with pytest.raises(Refuse) as caught:
        aggregate(["same", "same"], ["x", "x"])
    assert caught.value.code == "BAD_MODEL"
    with pytest.raises(Refuse) as caught:
        aggregate(["aa", "sk-abcdefghij"], ["x", "x"])
    assert caught.value.code == "SECRET"
    assert "sk-" not in str(caught.value)
    with pytest.raises(Refuse) as caught:
        aggregate(["aa", "bb"], ["ok", "Bearer abcdefghijklmn"])
    assert caught.value.code == "SECRET"
    assert "Bearer" not in str(caught.value)
    with pytest.raises(Refuse) as caught:
        aggregate(["aa", "bb", "cc"], ["ok", "ok", "api_key=supersecret"])
    assert caught.value.code == "SECRET"
    assert "supersecret" not in str(caught.value)
    winner = aggregate(["bb", "aa"], ["yes", "yes"], requested_cap=2)
    assert winner.spend_count == 2
    assert "sk-" not in repr(winner)


def test_text_and_id_bounds() -> None:
    with pytest.raises(Refuse) as caught:
        aggregate(["aa", 1], ["x", "x"])
    assert caught.value.code == "NOT_TEXT"
    with pytest.raises(Refuse) as caught:
        aggregate(["aa", "bb"], ["x", None])
    assert caught.value.code == "NOT_TEXT"
    with pytest.raises(Refuse) as caught:
        aggregate(["aa", "b\x00"], ["x", "x"])
    assert caught.value.code == "NULL_BYTE"
    with pytest.raises(Refuse) as caught:
        aggregate(["aa", "bb"], ["x", "y\x00"])
    assert caught.value.code == "NULL_BYTE"
    with pytest.raises(Refuse) as caught:
        aggregate(["aa", "bb"], ["plan", "plan\ud800"])
    assert caught.value.code == "NOT_TEXT"
    assert caught.value.detail == ""
    huge = "z" * (OUTPUT_CAP + 1)
    with pytest.raises(Refuse) as caught:
        aggregate(["aa", "bb"], [huge, huge])
    assert caught.value.code == "OVERSIZE"
    assert caught.value.detail == str(OUTPUT_CAP)
    edge = "z" * OUTPUT_CAP
    got = aggregate(["aa", "bb"], [edge, edge])
    assert got.text == edge
    assert got.votes == 2
    assert len(repr(got)) < 400
    long_id = "a" * (MODEL_ID_CAP + 1)
    with pytest.raises(Refuse) as caught:
        aggregate([long_id, "bb"], ["x", "x"])
    assert caught.value.code == "OVERSIZE"
    assert caught.value.detail == str(MODEL_ID_CAP)
    wide = "b" * MODEL_ID_CAP
    other = "c" * MODEL_ID_CAP
    named = aggregate([wide, other], ["q", "q"])
    assert named.model_id == wide
    assert named.spend_count == 2


def test_cap_ignores_a_higher_request() -> None:
    got = aggregate(_ids(5), ["a", "a", "a", "b", "c"], requested_cap=9)
    assert got.cap == POLICY_CAP == 5
    assert got.applied_cap == 5
    assert got.requested_cap == 9
    assert got.spend_count == 5
    assert got.text == "a"
    assert got.votes == 3
    assert rebuild(got) == got
    with pytest.raises(Refuse) as caught:
        aggregate(_ids(6), ["a"] * 6, requested_cap=99)
    assert caught.value.code == "BAD_COUNT"
    assert caught.value.detail == "6"
    top = aggregate(_ids(2), ["a", "a"], requested_cap=1_000_000_000)
    assert top.cap == POLICY_CAP
    assert top.applied_cap == POLICY_CAP
    assert top.requested_cap == 1_000_000_000
    tight = aggregate(_ids(3), ["a", "a", "b"], requested_cap=3)
    assert tight.applied_cap == 3
    assert tight.cap == POLICY_CAP
    assert tight.spend_count == 3
    with pytest.raises(Refuse) as caught:
        aggregate(_ids(4), ["a", "a", "a", "b"], requested_cap=3)
    assert caught.value.code == "BAD_COUNT"
    assert caught.value.detail == "4"
    with pytest.raises(Refuse) as caught:
        aggregate(_ids(2), ["a", "a", "a"], requested_cap=2)
    assert caught.value.code == "BAD_COUNT"
    assert caught.value.detail == "3"
    with pytest.raises(Refuse) as caught:
        aggregate(_ids(2), ["a", "a"], requested_cap=1)
    assert caught.value.code == "OUT_OF_RANGE"
    with pytest.raises(Refuse) as caught:
        aggregate(_ids(2), ["a", "a"], requested_cap=1_000_000_001)
    assert caught.value.code == "OUT_OF_RANGE"
    with pytest.raises(Refuse) as caught:
        aggregate(_ids(2), ["a", "a"], requested_cap=True)
    assert caught.value.code == "NOT_INT"
    with pytest.raises(Refuse) as caught:
        aggregate(_ids(2), ["a", "a"], requested_cap="5")
    assert caught.value.code == "NOT_INT"

    class Ask(int):
        pass

    with pytest.raises(Refuse) as caught:
        aggregate(_ids(2), ["a", "a"], requested_cap=Ask(4))
    assert caught.value.code == "NOT_INT"


def test_record_refuses_a_forged_verdict() -> None:
    with pytest.raises(Refuse) as caught:
        _verdict(schema="other")
    assert caught.value.code == "BAD_SCHEMA"
    with pytest.raises(Refuse) as caught:
        _verdict(cap=9)
    assert caught.value.code == "BAD_CAP"
    with pytest.raises(Refuse) as caught:
        _verdict(applied_cap=4, requested_cap=9)
    assert caught.value.code == "BAD_CAP"
    with pytest.raises(Refuse) as caught:
        _verdict(model_id="bb")
    assert caught.value.code == "BAD_MODEL"
    with pytest.raises(Refuse) as caught:
        _verdict(text="sk-abcdefghij")
    assert caught.value.code == "SECRET"
    assert "sk-" not in str(caught.value)
    with pytest.raises(Refuse) as caught:
        _verdict(
            text="yes",
            model_id="aa",
            model_ids=("aa", "bb", "cc"),
            texts=("yes", "yes", "no"),
            index=0,
            votes=3,
            spend_count=3,
        )
    assert caught.value.code == "BAD_COUNT"
    with pytest.raises(Refuse) as caught:
        _verdict(
            text="other",
            model_id="aa",
            model_ids=("aa", "bb", "cc"),
            texts=("yes", "yes", "no"),
            index=0,
            votes=2,
            spend_count=3,
        )
    assert caught.value.code == "MISMATCH"
    with pytest.raises(Refuse) as caught:
        _verdict(
            text="left",
            model_id="aa",
            model_ids=("aa", "bb"),
            texts=("left", "right"),
            index=0,
            votes=1,
            spend_count=2,
        )
    assert caught.value.code == "TIE"
    with pytest.raises(Refuse) as caught:
        _verdict(votes=cast(int, True))
    assert caught.value.code == "NOT_INT"
    with pytest.raises(Refuse) as caught:
        _verdict(requested_cap=1)
    assert caught.value.code == "OUT_OF_RANGE"
    with pytest.raises(Refuse) as caught:
        _verdict(model_ids=cast(tuple[str, ...], ["aa", "bb"]))
    assert caught.value.code == "BAD_COUNT"
    with pytest.raises(Refuse) as caught:
        rebuild("nope")
    assert caught.value.code == "BAD_SCHEMA"
    with pytest.raises(Refuse) as caught:
        rebuild(None)
    assert caught.value.code == "BAD_SCHEMA"
    made = _verdict()
    assert rebuild(made) == made
    assert rebuild(made) == aggregate(("aa", "bb"), ("yes", "yes"))


def test_no_model_call() -> None:
    module = inspect.getmodule(aggregate)
    assert module is not None
    source = inspect.getsource(module)
    for token in ("urllib", "requests", "subprocess", "socket", "pickle", "eval(", "exec("):
        assert token not in source
