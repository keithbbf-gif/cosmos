"""Caller-facing checks for the agent turn machine. The model is a fake callable."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace

import pytest

from agent_loop import (
    FAILURE_CLASSES,
    POLICY_MAX_TURNS,
    SCHEMA,
    STATES,
    AgentLoop,
    Note,
    Policy,
    Record,
    Snapshot,
    ToolAsk,
    ToolResult,
    clamp_turns,
    rebuild,
    run,
)
from cosmos_hermes import Refuse, secret_shape
from cosmos_hermes.bounds import MAX_TEXT


def _clean(halt: object) -> str:
    return repr(halt)


def _body(_args: str) -> ToolResult:
    return ToolResult(True, "", "a")


def _roundtrip(machine: AgentLoop) -> None:
    snap = machine.snapshot()
    assert rebuild(snap) == snap


def test_schema_and_states() -> None:
    assert SCHEMA == "cosmos-hermes-agent_loop/1"
    assert STATES == ("idle", "tool", "observe", "stop")
    assert POLICY_MAX_TURNS == 8
    assert FAILURE_CLASSES == ("DENIED", "MISSING", "TIMEOUT", "TOOL_FAULT")


def test_success_final_answer() -> None:
    def model(_notes: tuple[Note, ...]) -> str:
        return "The capital is Paris."

    halt = run(model, task="name the capital")
    assert halt.schema == SCHEMA
    assert halt.state == "stop"
    assert halt.code == "DONE"
    assert halt.text == "The capital is Paris."
    assert halt.turns == 1
    assert halt.policy == Policy(8, 8, False)
    assert [note.role for note in halt.notes] == ["user", "assistant"]
    assert not secret_shape(_clean(halt))


def test_success_after_one_tool() -> None:
    calls: list[str] = []

    def model(notes: tuple[Note, ...]) -> str:
        if any(note.role == "tool" for note in notes):
            return "ready"
        return "tool:read\nnote.txt"

    def tool(args: str) -> ToolResult:
        calls.append(args)
        return ToolResult(True, "", "body")

    halt = run(model, task="look", tools={"read": tool})
    assert halt.code == "DONE"
    assert halt.text == "ready"
    assert calls == ["note.txt"]
    assert [note.role for note in halt.notes] == ["user", "assistant", "tool", "assistant"]
    assert any(record.state == "observe" and record.text == "body" for record in halt.records)
    assert not secret_shape(_clean(halt))


def test_interrupted_before_tool() -> None:
    calls: list[str] = []
    seen: list[str] = []

    def model(_notes: tuple[Note, ...]) -> str:
        return "tool:read\nnote.txt"

    def tool(args: str) -> ToolResult:
        calls.append(args)
        return ToolResult(True, "", "body")

    def before(machine: AgentLoop, ask: ToolAsk) -> None:
        assert ask.name == "read"
        assert machine.state == "tool"
        seen.append(machine.interrupt().code)

    halt = run(model, task="look", tools={"read": tool}, before_tool=before)
    assert seen == ["INTERRUPTED"]
    assert halt.code == "INTERRUPTED"
    assert halt.state == "stop"
    assert calls == []
    assert all(note.role != "tool" for note in halt.notes)


def test_latched_interrupt_runs_no_tool() -> None:
    calls: list[str] = []

    def _unused(args: str) -> ToolResult:
        calls.append(args)
        return ToolResult(True, "", "body")

    machine = AgentLoop("look", {"read": _unused})

    def model(_notes: tuple[Note, ...]) -> str:
        machine.interrupt()
        return "tool:read\nnote.txt"

    halt = machine.run(model)
    assert halt.code == "INTERRUPTED"
    assert calls == []


def test_interrupt_does_not_drop_a_final_answer() -> None:
    machine = AgentLoop("task")

    def model(_notes: tuple[Note, ...]) -> str:
        latched = machine.interrupt()
        assert latched.code == ""
        assert latched.detail == "latched"
        return "answer"

    halt = machine.run(model)
    assert halt.code == "DONE"
    assert halt.text == "answer"


def test_empty_assistant_text() -> None:
    samples = {"n": 0}

    def model(_notes: tuple[Note, ...]) -> str:
        samples["n"] += 1
        return ""

    halt = run(model, task="speak")
    assert halt.code == "EMPTY"
    assert halt.turns == 1
    assert samples["n"] == 1
    assert [note.role for note in halt.notes] == ["user"]


def test_whitespace_assistant_text_is_empty() -> None:
    def model(_notes: tuple[Note, ...]) -> str:
        return " \n\t "

    halt = run(model, task="speak")
    assert halt.code == "EMPTY"


def test_tool_loop_on_second_identical_code() -> None:
    seen: list[str] = []
    bodies = ["one", "two"]
    calls: list[int] = []

    def model(notes: tuple[Note, ...]) -> str:
        for note in notes:
            if note.role == "tool":
                seen.append(note.text)
        return "tool:read\npath"

    def tool(_args: str) -> ToolResult:
        calls.append(1)
        return ToolResult(False, "MISSING", bodies[len(calls) - 1])

    halt = run(model, task="find", tools={"read": tool})
    assert seen == ["MISSING\none"]
    assert calls == [1, 1]
    assert halt.code == "TOOL_LOOP"
    assert halt.state == "stop"
    assert halt.turns == 2
    observed = [record for record in halt.records if record.state == "observe"]
    assert len(observed) == 1
    assert observed[0].code == "MISSING"
    assert halt.records[-1].code == "TOOL_LOOP"
    assert halt.records[-1].detail == "MISSING"


def test_distinct_tool_errors_are_returned_then_done() -> None:
    codes = ["MISSING", "DENIED"]
    calls: list[int] = []

    def model(notes: tuple[Note, ...]) -> str:
        if any(note.role == "tool" and note.text.startswith("DENIED") for note in notes):
            return "finished"
        return "tool:read\npath"

    def tool(_args: str) -> ToolResult:
        calls.append(1)
        return ToolResult(False, codes[len(calls) - 1], "detail")

    halt = run(model, task="find", tools={"read": tool})
    assert halt.code == "DONE"
    assert calls == [1, 1]
    assert [record.code for record in halt.records if record.state == "observe"] == ["MISSING", "DENIED"]


def test_same_code_after_a_success_still_loops() -> None:
    calls: list[int] = []

    def model(_notes: tuple[Note, ...]) -> str:
        return "tool:read\npath"

    def tool(_args: str) -> ToolResult:
        calls.append(1)
        if len(calls) == 2:
            return ToolResult(True, "", "ok")
        return ToolResult(False, "MISSING", "again")

    halt = run(model, task="find", tools={"read": tool})
    assert len(calls) == 3
    assert halt.code == "TOOL_LOOP"
    assert halt.turns == 3


def test_unclassified_failure_does_not_retry() -> None:
    calls = {"n": 0}
    samples = {"n": 0}

    def model(_notes: tuple[Note, ...]) -> str:
        samples["n"] += 1
        return "tool:read\npath"

    def tool(_args: str) -> ToolResult:
        calls["n"] += 1
        return ToolResult(False, "WEIRD", "no")

    halt = run(model, task="find", tools={"read": tool})
    assert halt.code == "UNCLASSIFIED"
    assert halt.records[-1].detail == "WEIRD"
    assert calls["n"] == 1
    assert samples["n"] == 1
    assert halt.turns == 1


def test_ignored_cap_stops_at_eight() -> None:
    samples: list[int] = []
    calls: list[str] = []

    def model(_notes: tuple[Note, ...]) -> str:
        samples.append(1)
        return "tool:read\n" + str(len(samples))

    def tool(args: str) -> ToolResult:
        calls.append(args)
        return ToolResult(True, "", args)

    halt = run(model, task="keep going", tools={"read": tool}, requested_turns=30)
    assert halt.code == "MAX_TURNS"
    assert halt.turns == 8
    assert len(samples) == 8
    assert len(calls) == 8
    assert halt.policy.requested == 30
    assert halt.policy.applied == POLICY_MAX_TURNS
    assert halt.policy.ignored is True
    assert halt.records[-1].detail == "8"


def test_high_cap_is_recorded_on_a_short_success() -> None:
    def model(_notes: tuple[Note, ...]) -> str:
        return "ok"

    halt = run(model, task="hi", requested_turns=9)
    assert halt.code == "DONE"
    assert halt.turns == 1
    assert halt.policy == Policy(9, 8, True)


def test_lower_cap_is_honored() -> None:
    samples: list[int] = []

    def model(_notes: tuple[Note, ...]) -> str:
        samples.append(1)
        return "tool:read\nx"

    def tool(_args: str) -> ToolResult:
        return ToolResult(True, "", "x")

    halt = run(model, task="go", tools={"read": tool}, requested_turns=2)
    assert halt.code == "MAX_TURNS"
    assert halt.turns == 2
    assert len(samples) == 2
    assert halt.policy == Policy(2, 2, False)


def test_clamp_turns_records_the_policy() -> None:
    assert clamp_turns(1) == Policy(1, 1, False)
    assert clamp_turns(8) == Policy(8, 8, False)
    assert clamp_turns(9) == Policy(9, 8, True)
    assert clamp_turns(10**18) == Policy(100_000, 8, True)
    with pytest.raises(Refuse) as flagged:
        clamp_turns(True)
    assert flagged.value.code == "NOT_INT"
    with pytest.raises(Refuse) as fractional:
        clamp_turns(1.5)
    assert fractional.value.code == "NOT_INT"
    with pytest.raises(Refuse) as text:
        clamp_turns("8")
    assert text.value.code == "NOT_INT"
    with pytest.raises(Refuse) as zero:
        clamp_turns(0)
    assert zero.value.code == "OUT_OF_RANGE"
    with pytest.raises(Refuse) as negative:
        clamp_turns(-3)
    assert negative.value.code == "OUT_OF_RANGE"


def test_policy_cannot_raise_the_cap() -> None:
    with pytest.raises(Refuse) as caught:
        Policy(9, 9, True)
    assert caught.value.code == "BAD_POLICY"


def test_direct_step_past_the_cap() -> None:
    loop = AgentLoop("task", {"read": _body}, requested_turns=1)
    assert loop.step("tool:read\na").state == "tool"
    assert loop.step("", ToolResult(True, "", "a")).state == "observe"
    stopped = loop.step("again")
    assert stopped.code == "MAX_TURNS"
    assert loop.turn == 1
    assert loop.halt().code == "MAX_TURNS"


def test_state_progression() -> None:
    loop = AgentLoop("task", {"read": _body})
    assert loop.state == "idle"
    assert loop.transcript()[0].text == "task"
    assert loop.step("tool:read\nnote").state == "tool"
    assert loop.step("", ToolResult(True, "", "body")).state == "observe"
    done = loop.step("ready")
    assert done.code == "DONE"
    assert done.state == "stop"
    assert loop.halt().text == "ready"


def test_secret_model_text_is_redacted() -> None:
    def model(_notes: tuple[Note, ...]) -> str:
        return "sk-livekeyvalue"

    halt = run(model, task="hello")
    assert halt.code == "SECRET"
    blob = _clean(halt) + halt.text + "".join(record.text + record.detail for record in halt.records)
    assert "sk-livekeyvalue" not in blob
    assert not secret_shape(blob)


def test_secret_tool_text_is_redacted() -> None:
    def model(_notes: tuple[Note, ...]) -> str:
        return "tool:read\nnote"

    def tool(_args: str) -> ToolResult:
        return ToolResult(True, "", "Bearer abcdefghijk")

    halt = run(model, task="look", tools={"read": tool})
    assert halt.code == "SECRET"
    blob = _clean(halt) + halt.text
    assert "abcdefghijk" not in blob
    assert not secret_shape(blob)


def test_tool_result_repr_redacts() -> None:
    result = ToolResult(True, "", "Bearer abcdefghijk")
    assert result.ok is False
    assert result.code == "SECRET"
    assert "abcdefghijk" not in repr(result)
    assert not secret_shape(repr(result))


def test_secret_task_refuses() -> None:
    with pytest.raises(Refuse) as caught:
        AgentLoop("sk-livekeyvalue")
    assert caught.value.code == "SECRET"


def test_empty_task_refuses() -> None:
    with pytest.raises(Refuse) as blank:
        AgentLoop("")
    assert blank.value.code == "EMPTY_TASK"
    with pytest.raises(Refuse) as space:
        AgentLoop(" \n ")
    assert space.value.code == "EMPTY_TASK"


def test_not_text_null_and_oversize() -> None:
    loop = AgentLoop("task")
    with pytest.raises(Refuse) as kind:
        loop.step(None)
    assert kind.value.code == "NOT_TEXT"
    assert loop.state == "idle"
    assert loop.turn == 0
    with pytest.raises(Refuse) as nul:
        loop.step("a\x00b")
    assert nul.value.code == "NULL_BYTE"
    with pytest.raises(Refuse) as huge:
        loop.step("x" * (MAX_TEXT + 1))
    assert huge.value.code == "OVERSIZE"
    assert loop.turn == 0


def test_empty_allowlist_enables_nothing() -> None:
    def model(_notes: tuple[Note, ...]) -> str:
        return "tool:read\nnote"

    halt = run(model, task="look", tools={})
    assert halt.code == "NO_ALLOW"
    assert halt.records[-1].state == "stop"


def test_empty_allowlist_still_accepts_a_final_answer() -> None:
    def model(_notes: tuple[Note, ...]) -> str:
        return "plain"

    halt = run(model, task="look")
    assert halt.code == "DONE"


def test_unknown_and_bad_tool_lines() -> None:
    def unknown(_notes: tuple[Note, ...]) -> str:
        return "tool:missing\nnote"

    halt = run(unknown, task="look", tools={"read": _body})
    assert halt.code == "UNKNOWN_TOOL"

    def malformed(_notes: tuple[Note, ...]) -> str:
        return "tool:Read\nnote"

    refused = run(malformed, task="look", tools={"read": _body})
    assert refused.code == "BAD_TOOL"

    def bare(_notes: tuple[Note, ...]) -> str:
        return "tool:"

    bare_halt = run(bare, task="look", tools={"read": _body})
    assert bare_halt.code == "BAD_TOOL"


def test_bad_tool_registration() -> None:
    with pytest.raises(Refuse) as named:
        AgentLoop("task", tools={"Read": _body})
    assert named.value.code == "BAD_TOOL"
    with pytest.raises(Refuse) as kind:
        AgentLoop("task", tools=["read"])
    assert kind.value.code == "BAD_TOOLS"
    with pytest.raises(Refuse) as dead:
        AgentLoop("task", tools={"read": "not-callable"})
    assert dead.value.code == "BAD_TOOL"


def test_bad_state_and_tool_result() -> None:
    loop = AgentLoop("task", {"read": _body})
    with pytest.raises(Refuse) as early:
        loop.step("", ToolResult(True, "", "x"))
    assert early.value.code == "BAD_STATE"
    loop.step("tool:read\nnote")
    with pytest.raises(Refuse) as missing:
        loop.step()
    assert missing.value.code == "NEED_TOOL_RESULT"
    with pytest.raises(Refuse) as both:
        loop.step("extra", ToolResult(True, "", "x"))
    assert both.value.code == "BAD_STATE"
    with pytest.raises(Refuse) as shape:
        loop.step("", "nope")
    assert shape.value.code == "BAD_TOOL_RESULT"
    with pytest.raises(Refuse) as coded:
        loop.step("", ToolResult(True, "OK", "x"))
    assert coded.value.code == "BAD_TOOL_RESULT"
    with pytest.raises(Refuse) as lower:
        loop.step("", ToolResult(False, "lower", "x"))
    assert lower.value.code == "BAD_TOOL_RESULT"
    assert loop.state == "tool"


def test_bad_note_and_record() -> None:
    with pytest.raises(Refuse) as note:
        Note("system", "hello")
    assert note.value.code == "BAD_NOTE"
    with pytest.raises(Refuse) as record:
        Record("nope", 1, "", "", "", "0" * 64, "0" * 64)
    assert record.value.code == "BAD_RECORD"


def test_already_stopped_and_not_stopped() -> None:
    loop = AgentLoop("task")
    with pytest.raises(Refuse) as open_halt:
        loop.halt()
    assert open_halt.value.code == "NOT_STOPPED"

    def _nope(_notes: tuple[Note, ...]) -> str:
        return "nope"

    loop.step("done")
    with pytest.raises(Refuse) as again:
        loop.step("more")
    assert again.value.code == "ALREADY_STOPPED"
    with pytest.raises(Refuse) as stopped:
        loop.interrupt()
    assert stopped.value.code == "ALREADY_STOPPED"
    with pytest.raises(Refuse) as second:
        loop.run(_nope)
    assert second.value.code == "ALREADY_STOPPED"


def test_tool_refuse_is_a_record_the_model_sees() -> None:
    def model(notes: tuple[Note, ...]) -> str:
        if any(note.role == "tool" for note in notes):
            return "stopped"
        return "tool:read\npath"

    def tool(_args: str) -> ToolResult:
        raise Refuse("DENIED", "no")

    halt = run(model, task="find", tools={"read": tool})
    assert halt.code == "DONE"
    assert any(record.code == "DENIED" and record.state == "observe" for record in halt.records)
    assert any(note.role == "tool" and note.text.startswith("DENIED") for note in halt.notes)


def test_tool_fault_hides_the_exception_text() -> None:
    def model(notes: tuple[Note, ...]) -> str:
        if any(note.role == "tool" for note in notes):
            return "done"
        return "tool:read\npath"

    def tool(_args: str) -> ToolResult:
        raise RuntimeError("sk-livekeyvalue")

    halt = run(model, task="find", tools={"read": tool})
    assert halt.code == "DONE"
    assert any(record.code == "TOOL_FAULT" and record.state == "observe" for record in halt.records)
    blob = _clean(halt) + "".join(note.text for note in halt.notes)
    assert "sk-livekeyvalue" not in blob
    assert not secret_shape(blob)


def test_repeated_tool_fault_is_tool_loop() -> None:
    def model(_notes: tuple[Note, ...]) -> str:
        return "tool:read\npath"

    def tool(_args: str) -> ToolResult:
        raise RuntimeError("boom")

    halt = run(model, task="find", tools={"read": tool})
    assert halt.code == "TOOL_LOOP"
    assert halt.records[-1].detail == "TOOL_FAULT"


def test_error_note_keeps_the_class_when_the_body_is_huge() -> None:
    body = "m" * MAX_TEXT

    def model(notes: tuple[Note, ...]) -> str:
        if any(note.role == "tool" for note in notes):
            return "enough"
        return "tool:read\npath"

    def tool(_args: str) -> ToolResult:
        return ToolResult(False, "MISSING", body)

    halt = run(model, task="find", tools={"read": tool})
    assert halt.code == "DONE"
    shown = [note.text for note in halt.notes if note.role == "tool"]
    assert len(shown) == 1
    assert shown[0].startswith("MISSING\n")
    assert len(shown[0]) == MAX_TEXT


def test_prose_that_mentions_a_tool_is_a_final_answer() -> None:
    def model(_notes: tuple[Note, ...]) -> str:
        return "use tool:read only if asked"

    halt = run(model, task="look", tools={"read": _body})
    assert halt.code == "DONE"
    assert halt.text == "use tool:read only if asked"


def test_rebuild_replays_live_paths() -> None:
    def _paris(_notes: tuple[Note, ...]) -> str:
        return "The capital is Paris."

    finished = AgentLoop("name the capital")
    finished.run(_paris)
    _roundtrip(finished)

    loop = AgentLoop("look", {"read": _body})
    _roundtrip(loop)
    loop.step("tool:read\nnote")
    _roundtrip(loop)
    loop.step("", ToolResult(True, "", "body"))
    _roundtrip(loop)
    loop.step("ready")
    _roundtrip(loop)

    blank = AgentLoop("speak")
    blank.step("  ")
    _roundtrip(blank)

    held = AgentLoop("look", {"read": _body})
    held.interrupt()
    _roundtrip(held)
    held.step("answer")
    _roundtrip(held)

    cut = AgentLoop("look", {"read": _body})
    cut.step("tool:read\nnote")
    cut.interrupt()
    _roundtrip(cut)

    secret = AgentLoop("hello")
    secret.step("sk-livekeyvalue")
    _roundtrip(secret)

    short = AgentLoop("go", {"read": _body}, requested_turns=1)
    short.step("tool:read\na")
    short.step("", ToolResult(True, "", "a"))
    short.step("again")
    _roundtrip(short)

    def _weird(_args: str) -> ToolResult:
        return ToolResult(False, "WEIRD", "no")

    odd = AgentLoop("find", {"read": _weird})
    odd.step("tool:read\npath")
    odd.step("", ToolResult(False, "WEIRD", "no"))
    _roundtrip(odd)
    assert odd.snapshot().code == "UNCLASSIFIED"

    def _miss(_args: str) -> ToolResult:
        return ToolResult(False, "MISSING", "again")

    stuck = AgentLoop("find", {"read": _miss})
    stuck.step("tool:read\npath")
    stuck.step("", ToolResult(False, "MISSING", "again"))
    stuck.step("tool:read\npath")
    stuck.step("", ToolResult(False, "MISSING", "again"))
    _roundtrip(stuck)
    assert stuck.snapshot().code == "TOOL_LOOP"
    assert stuck.snapshot().seen == ("MISSING",)


def test_rebuild_refuses_a_broken_or_stale_chain() -> None:
    machine = AgentLoop("task")
    machine.step("done")
    snap = machine.snapshot()
    assert rebuild(snap) == snap
    with pytest.raises(Refuse) as stale:
        rebuild(replace(snap, turn=0))
    assert stale.value.code == "STALE"
    bad = Record("stop", 1, "DONE", "x", "x", "1" * 64, "2" * 64)
    with pytest.raises(Refuse) as broken:
        rebuild(replace(snap, records=(bad,)))
    assert broken.value.code == "BROKEN_CHAIN"
    with pytest.raises(Refuse) as shape:
        rebuild("nope")
    assert shape.value.code == "BAD_SNAPSHOT"
    with pytest.raises(Refuse) as schema:
        replace(snap, schema="cosmos-hermes-agent_loop/2")
    assert schema.value.code == "BAD_SNAPSHOT"


def _porch_session() -> tuple[Snapshot, str]:
    pages = {
        "lamp-note": "The porch light is off.",
        "hall-card": "Guest Ada arrives at dusk.",
    }
    placed = {"lamp-note": False}
    lamps = {"porch": "off"}

    def read(args: str) -> ToolResult:
        key = args.strip()
        if key == "lamp-note" and not placed["lamp-note"]:
            placed["lamp-note"] = True
            return ToolResult(False, "MISSING", "lamp-note is not on the hook")
        body = pages.get(key)
        if body is None:
            return ToolResult(False, "MISSING", "not on the hook")
        return ToolResult(True, "", body)

    def light_set(args: str) -> ToolResult:
        if args.strip() != "porch on":
            return ToolResult(False, "DENIED", "only the porch light")
        lamps["porch"] = "on"
        pages["lamp-note"] = "The porch light is on."
        return ToolResult(True, "", "porch light on")

    tools: dict[str, Callable[[str], ToolResult]] = {"read": read, "light": light_set}
    machine = AgentLoop(
        "In session porch-evening, read lamp-note and hall-card, then turn the porch light on.",
        tools,
    )
    lines = (
        "tool:read\nlamp-note",
        "tool:read\nlamp-note",
        "tool:read\nhall-card",
        "tool:light\nporch on",
        "tool:read\nlamp-note",
        "tool:read\nhall-card",
        "tool:light\nporch on",
        "tool:read\nlamp-note",
    )
    assert len(lines) == POLICY_MAX_TURNS
    for line in lines:
        asked = machine.step(line)
        assert asked.state == "tool"
        fn = tools.get(asked.detail)
        if fn is None:
            raise AssertionError(asked.detail)
        followed = machine.step("", fn(asked.text))
        assert followed.state == "observe"
    snap = machine.snapshot()
    assert snap.turn == POLICY_MAX_TURNS
    assert snap.state == "observe"
    assert snap.seen == ("MISSING",)
    assert snap.code == ""
    assert any(note.role == "tool" and note.text == "porch light on" for note in snap.notes)
    assert any(note.role == "tool" and "Ada" in note.text for note in snap.notes)
    assert any(note.role == "tool" and note.text == "The porch light is on." for note in snap.notes)
    assert rebuild(snap) == snap
    try:
        machine.step("The porch light is on for Ada.")
    except Refuse as exc:
        refused = exc.code
    else:
        raise AssertionError("ninth step")
    assert refused == "POLICY_CAP"
    assert machine.turn == POLICY_MAX_TURNS
    assert machine.snapshot() == snap
    return snap, refused


def test_example_agent_loop() -> None:
    assert _porch_session() == _porch_session()
