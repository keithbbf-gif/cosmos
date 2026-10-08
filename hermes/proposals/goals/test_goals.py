"""Named goal predicates stay data. Unmet goals refuse until named evidence."""

from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError, replace
from pathlib import Path

import pytest

import goals
from cosmos_hermes import Refuse, secret_shape

_BANNED_CALLS = frozenset({"eval", "exec", "compile", "__import__"})
_BANNED_MODULES = frozenset({"subprocess", "socket", "urllib", "requests", "pickle", "http"})
_ASK_OVER = 1_000_001


def _code(caught: pytest.ExceptionInfo[Refuse]) -> str:
    return caught.value.code


def _ship_note() -> tuple[goals.Goal, goals.Continuation, goals.Goal]:
    """Mira ships a note onto the library card during the porch-light session."""
    goal = goals.create(
        "ship-note",
        "ship_note",
        now=1_710_000_100,
        max_turns=6,
        allow=("porch_light", "ship_note"),
    )
    assert goal.text == "ship-note"
    assert goal.predicate_id == "ship_note"
    assert goal.evidence_id == ""
    assert goal.status() == "open"
    assert goal.policy.turn_cap == 6
    assert goal.policy.capped is False
    with pytest.raises(Refuse) as missing:
        goal.mark("done", now=1_710_000_180, reason="session porch-light looks finished")
    assert missing.value.code == "UNMET"
    assert goal.status() == "open"
    with pytest.raises(Refuse) as wrong:
        goal.mark("done", now=1_710_000_180, evidence="porch_light")
    assert wrong.value.code == "UNMET"
    stepped, step = goal.advance(
        now=1_710_000_140,
        note="session porch-light: draft the ship-note for the library card",
    )
    assert step.predicate_id == "ship_note"
    assert step.turn == 1
    assert stepped.status() == "open"
    proof = goals.prove("ship_note", "library card holds the porch-light note")
    met = stepped.mark(
        "done",
        now=1_710_000_180,
        reason="the library card in session porch-light holds the note",
        evidence=proof,
    )
    assert met.status() == "done"
    assert met.evidence_id == "ship_note"
    assert met.text == "ship-note"
    assert goals.rebuild(goals.emit(met)) == met
    return goal, step, met


def test_example_goals() -> None:
    first = _ship_note()
    second = _ship_note()
    assert first == second
    open_goal, step, met = first
    assert open_goal.text == "ship-note"
    assert open_goal.status() == "open"
    assert step.turn == 1
    assert met.status() == "done"
    assert met.evidence_id == "ship_note"


def test_schema_and_import_name() -> None:
    assert goals.__name__ == "goals"
    assert goals.SCHEMA == "cosmos-hermes-goals/1"
    assert goals.TURN_CAP == 20
    assert goals.RETRY_FAILURE == "JUDGE_GAP"
    assert "create" in goals.__all__
    assert "Goal" in goals.__all__
    assert "prove" in goals.__all__
    assert "emit" in goals.__all__
    assert "rebuild" in goals.__all__


def test_success_open_until_mark() -> None:
    goal = goals.create("fix the lint and stop", "lint_clean", now=5)
    assert goal.status() == "open"
    assert goal.predicate_id == "lint_clean"
    assert goal.evidence_id == ""
    assert goal.text == "fix the lint and stop"
    assert goal.policy.turn_cap == goals.TURN_CAP
    assert goal.policy.asked_turns == goals.TURN_CAP
    assert goal.policy.capped is False
    assert goal.turns_used == 0
    again = goals.create("fix the lint and stop", "lint_clean", now=5)
    assert goal == again
    done = goal.mark("done", now=6, reason="lint is clean", evidence="lint_clean")
    assert done.status() == "done"
    assert done.reason == "lint is clean"
    assert done.evidence_id == "lint_clean"
    assert goal.status() == "open"
    refused = goal.mark("refused", now=6, reason="needs a human")
    assert refused.status() == "refused"
    assert refused.evidence_id == ""
    same_instant = goal.mark("done", now=5, evidence="lint_clean")
    assert same_instant.status() == "done"
    assert same_instant.updated_at == 5


def test_predicate_is_a_name_not_code() -> None:
    source = Path(__file__).with_name("goals.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name):
                assert func.id not in _BANNED_CALLS
        elif isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name.split(".")[0] not in _BANNED_MODULES
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            assert module.split(".")[0] not in _BANNED_MODULES
    goal = goals.create("call f(x) then stop", "eval")
    assert goal.predicate_id == "eval"
    assert goal.text == "call f(x) then stop"
    assert isinstance(goal.predicate_id, str)
    assert not callable(goal.predicate_id)
    assert not callable(goal)
    for record in (goals.Goal, goals.Continuation, goals.Policy, goals.Evidence, goals.Record):
        assert "predicate" not in record.__dataclass_fields__ or record is goals.Goal
        for field in record.__dataclass_fields__.values():
            assert "Callable" not in str(field.type)
    assert "predicate_id" in goals.Goal.__dataclass_fields__
    wide = "a" * 32
    held = goals.create("ship it", wide)
    assert held.predicate_id == wide
    numbered = goals.create("ship it", "1")
    assert numbered.predicate_id == "1"


def test_bad_predicate() -> None:
    samples = ("eval(", "print(1)", "HasCaps", "a" * 33, "", "ok-name", "has space", "a" * 256)
    for sample in samples:
        with pytest.raises(Refuse) as caught:
            goals.create("ship it", sample)
        assert _code(caught) == "BAD_PREDICATE"
    with pytest.raises(Refuse) as caught:
        goals.create("ship it", "ok", allow=("ok", "Bad"))
    assert _code(caught) == "BAD_PREDICATE"
    with pytest.raises(Refuse) as caught:
        goals.prove("ship-note")
    assert _code(caught) == "BAD_PREDICATE"


def test_unmet_without_named_evidence() -> None:
    goal = goals.create("ship-note", "ship_note", now=1)
    with pytest.raises(Refuse) as caught:
        goal.mark("done", now=2, reason="ship_note")
    assert _code(caught) == "UNMET"
    assert goal.status() == "open"
    assert goal.evidence_id == ""
    with pytest.raises(Refuse) as caught:
        goal.mark("done", now=2, evidence="porch_light")
    assert _code(caught) == "UNMET"
    with pytest.raises(Refuse) as caught:
        goal.mark("done", now=2, evidence="Ship")
    assert _code(caught) == "BAD_PREDICATE"
    with pytest.raises(Refuse) as caught:
        goal.mark("done", now=2, evidence=1)
    assert _code(caught) == "BAD_EVIDENCE"
    with pytest.raises(Refuse) as caught:
        goal.mark("refused", now=2, evidence="ship_note")
    assert _code(caught) == "BAD_EVIDENCE"
    assert goal.status() == "open"
    with pytest.raises(Refuse) as caught:
        replace(goal, state="done")
    assert _code(caught) == "UNMET"
    with pytest.raises(Refuse) as caught:
        replace(goal, evidence_id="ship_note")
    assert _code(caught) == "BAD_EVIDENCE"
    met = goal.mark("done", now=2, evidence=goals.prove("ship_note", "card updated"))
    assert met.evidence_id == "ship_note"
    with pytest.raises(Refuse) as caught:
        replace(met, evidence_id="other")
    assert _code(caught) == "UNMET"
    gapped = goal.gap(now=2)
    with pytest.raises(Refuse) as caught:
        gapped.mark("done", now=3)
    assert _code(caught) == "UNMET"


def test_guard_escape() -> None:
    phrases = (
        "disable approval",
        "Please DISABLE APPROVAL now",
        "disable\u200b approval",
        "disable\napproval",
        "sk-live-abcdefghij",
        "Bearer abcdefghijk",
        "api_key=supersecretvalue",
    )
    for text in phrases:
        with pytest.raises(Refuse) as caught:
            goals.create(text, "safe_id")
        assert _code(caught) == "GUARD_ESCAPE"
        assert "supersecretvalue" not in str(caught.value)
        assert "abcdefgh" not in str(caught.value)
    secret = "api_key=supersecretvalue"
    assert secret_shape(secret) is True
    goal = goals.create("ask for approval before the patch", "ask_ok")
    assert goal.status() == "open"
    with pytest.raises(Refuse) as caught:
        goal.mark("done", reason="disable approval", evidence="ask_ok")
    assert _code(caught) == "GUARD_ESCAPE"
    assert goal.status() == "open"
    with pytest.raises(Refuse) as caught:
        goal.advance(note="Bearer abcdefghijk")
    assert _code(caught) == "GUARD_ESCAPE"
    assert goal.turns_used == 0
    with pytest.raises(Refuse) as caught:
        goal.gap("sk-live-abcdefghij")
    assert _code(caught) == "GUARD_ESCAPE"
    assert goal.retries == 0
    with pytest.raises(Refuse) as caught:
        goals.prove("ask_ok", "disable approval")
    assert _code(caught) == "GUARD_ESCAPE"


def test_bad_status_and_not_open() -> None:
    goal = goals.create("ship it", "ship")
    for bad in ("open", "continue", "paused", "clear", "blocked", "DONE", "nope", "", "done "):
        with pytest.raises(Refuse) as caught:
            goal.mark(bad)
        assert _code(caught) == "BAD_STATUS"
    assert goal.status() == "open"
    done = goal.mark("done", evidence="ship")
    with pytest.raises(Refuse) as caught:
        done.mark("refused")
    assert _code(caught) == "NOT_OPEN"
    with pytest.raises(Refuse) as caught:
        done.advance()
    assert _code(caught) == "NOT_OPEN"
    with pytest.raises(Refuse) as caught:
        done.gap()
    assert _code(caught) == "NOT_OPEN"
    refused = goal.mark("refused")
    with pytest.raises(Refuse) as caught:
        refused.mark("done", evidence="ship")
    assert _code(caught) == "NOT_OPEN"


def test_turn_cap_is_policy() -> None:
    high = goals.create("keep going", "keep", max_turns=100)
    assert high.policy.asked_turns == 100
    assert high.policy.turn_cap == goals.TURN_CAP
    assert high.policy.capped is True
    current = high
    last_turn = 0
    for _ in range(goals.TURN_CAP):
        current, step = current.advance()
        last_turn = step.turn
        assert step.predicate_id == "keep"
        assert step.turn_cap == goals.TURN_CAP
        assert isinstance(step.note, str)
    assert last_turn == goals.TURN_CAP
    assert current.turns_used == goals.TURN_CAP
    assert current.status() == "open"
    with pytest.raises(Refuse) as caught:
        current.advance()
    assert _code(caught) == "BUDGET"
    assert current.status() == "open"
    closed = current.mark("refused", reason="budget spent")
    assert closed.status() == "refused"
    low = goals.create("short", "short", max_turns=2)
    assert low.policy.asked_turns == 2
    assert low.policy.turn_cap == 2
    assert low.policy.capped is False
    once, _step = low.advance(now=1)
    twice, _step = once.advance(now=2)
    with pytest.raises(Refuse) as caught:
        twice.advance(now=3)
    assert _code(caught) == "BUDGET"


def test_judge_gap_retries_once() -> None:
    goal = goals.create("judge me", "judge_me")
    with pytest.raises(Refuse) as caught:
        goal.gap("OTHER")
    assert _code(caught) == "UNCLASSIFIED"
    assert goal.retries == 0
    once = goal.gap()
    assert once.retries == 1
    assert once.turns_used == 0
    assert once.status() == "open"
    named = goal.gap(goals.RETRY_FAILURE)
    assert named.retries == 1
    with pytest.raises(Refuse) as caught:
        once.gap()
    assert _code(caught) == "RETRY_CAP"
    assert once.retries == 1
    with pytest.raises(Refuse) as caught:
        once.mark("done")
    assert _code(caught) == "UNMET"
    done = once.mark("done", evidence="judge_me")
    assert done.status() == "done"


def test_allowlist_fail_closed() -> None:
    with pytest.raises(Refuse) as caught:
        goals.create("ship it", "named", allow=())
    assert _code(caught) == "EMPTY_ALLOW"
    with pytest.raises(Refuse) as caught:
        goals.create("ship it", "named", allow=("other",))
    assert _code(caught) == "NOT_LISTED"
    with pytest.raises(Refuse) as caught:
        goals.create("ship it", "named", allow="named")
    assert _code(caught) == "NOT_LIST"
    with pytest.raises(Refuse) as caught:
        goals.create("ship it", "named", allow={"named": "named"})
    assert _code(caught) == "NOT_LIST"
    with pytest.raises(Refuse) as caught:
        goals.create("ship it", "named", allow=(item for item in ("named",)))
    assert _code(caught) == "NOT_LIST"
    with pytest.raises(Refuse) as caught:
        goals.create("ship it", "named", allow=("named", "named"))
    assert _code(caught) == "DUPLICATE"
    goal = goals.create("ship it", "named", allow=("other_id", "named"))
    assert goal.predicate_id == "named"
    from_set = goals.create("ship it", "named", allow={"other_id", "named"})
    assert from_set.predicate_id == "named"
    too_many = tuple(f"n{index}" for index in range(goals.ALLOW_CAP + 1))
    with pytest.raises(Refuse) as caught:
        goals.create("ship it", "n0", allow=too_many)
    assert _code(caught) == "OVERSIZE"


def test_bounds_clock_and_records() -> None:
    with pytest.raises(Refuse) as caught:
        goals.create("bad\x00text", "ok")
    assert _code(caught) == "NULL_BYTE"
    with pytest.raises(Refuse) as caught:
        goals.create("ok text", "bad\x00")
    assert _code(caught) == "NULL_BYTE"
    with pytest.raises(Refuse) as caught:
        goals.create(None, "ok")
    assert _code(caught) == "NOT_TEXT"
    with pytest.raises(Refuse) as caught:
        goals.create("ok text", None)
    assert _code(caught) == "NOT_TEXT"
    with pytest.raises(Refuse) as caught:
        goals.create("bad\ud800text", "ok")
    assert _code(caught) == "NOT_TEXT"
    goal = goals.create("ok text", "ok")
    with pytest.raises(Refuse) as caught:
        goal.mark(None)
    assert _code(caught) == "NOT_TEXT"
    with pytest.raises(Refuse) as caught:
        goals.create("ok text", "ok", max_turns=True)
    assert _code(caught) == "NOT_INT"
    with pytest.raises(Refuse) as caught:
        goals.create("ok text", "ok", max_turns=0)
    assert _code(caught) == "OUT_OF_RANGE"
    with pytest.raises(Refuse) as caught:
        goals.create("ok text", "ok", max_turns=_ASK_OVER)
    assert _code(caught) == "OUT_OF_RANGE"
    with pytest.raises(Refuse) as caught:
        goals.create("", "ok")
    assert _code(caught) == "EMPTY_GOAL"
    with pytest.raises(Refuse) as caught:
        goals.create("   ", "ok")
    assert _code(caught) == "EMPTY_GOAL"
    with pytest.raises(Refuse) as caught:
        goals.create("\u200b", "ok")
    assert _code(caught) == "EMPTY_GOAL"
    with pytest.raises(Refuse) as caught:
        goals.create("z" * (goals.TEXT_CAP + 1), "ok")
    assert _code(caught) == "OVERSIZE"
    stamped = goals.create("ship it", "ship", now=10)
    with pytest.raises(Refuse) as caught:
        stamped.mark("done", now=9, evidence="ship")
    assert _code(caught) == "CLOCK"
    assert stamped.status() == "open"
    with pytest.raises(Refuse) as caught:
        replace(stamped, schema="cosmos-hermes-goals/2")
    assert _code(caught) == "BAD_SCHEMA"
    raised = goals.Policy(asked_turns=40, turn_cap=40, capped=True)
    with pytest.raises(Refuse) as caught:
        replace(stamped, policy=raised)
    assert _code(caught) == "BAD_POLICY"
    lied = goals.Policy(asked_turns=40, turn_cap=goals.TURN_CAP, capped=False)
    with pytest.raises(Refuse) as caught:
        replace(stamped, policy=lied)
    assert _code(caught) == "BAD_POLICY"


def test_rebuild_roundtrip_and_broken_record() -> None:
    goal = goals.create("ship the note", "ship_note", now=4)
    assert goals.rebuild(goals.emit(goal)) == goal
    moved, step = goal.advance(now=5, note="one pass on the library card")
    assert step.turn == 1
    assert goals.rebuild(goals.emit(moved)) == moved
    gapped = goal.gap(now=6)
    assert goals.rebuild(goals.emit(gapped)) == gapped
    met = goal.mark("done", now=7, evidence=goals.prove("ship_note"))
    assert goals.rebuild(goals.emit(met)) == met
    record = goals.emit(goal)
    with pytest.raises(Refuse) as caught:
        replace(record, digest="0" * 64)
    assert _code(caught) == "CHAIN"
    with pytest.raises(Refuse) as caught:
        replace(record, text="a different note")
    assert _code(caught) == "CHAIN"
    with pytest.raises(Refuse) as caught:
        goals.rebuild(goal)
    assert _code(caught) == "BAD_RECORD"
    with pytest.raises(Refuse) as caught:
        goals.emit(record)
    assert _code(caught) == "BAD_RECORD"
    with pytest.raises(Refuse) as caught:
        goals.rebuild(())
    assert _code(caught) == "BAD_RECORD"
    with pytest.raises(Refuse) as caught:
        goals.emit(None)
    assert _code(caught) == "BAD_RECORD"


def test_repr_omits_text_and_frozen() -> None:
    goal = goals.create("ordinary goal text", "ordinary", now=1)
    moved, step = goal.advance(now=2, note="still ordinary")
    proof = goals.prove("ordinary", "still ordinary")
    blob = repr(moved) + repr(step) + repr(moved.policy) + repr(proof) + repr(goals.emit(moved))
    assert "ordinary goal text" not in blob
    assert "still ordinary" not in blob
    assert "sk-" not in blob
    assert "api_key" not in blob
    assert "Bearer" not in blob
    with pytest.raises(FrozenInstanceError):
        setattr(goal, "state", "done")
    assert goal.status() == "open"
