"""Clarify returns bounded questions. A todo list is stored and does not run."""

from __future__ import annotations

from typing import cast

import pytest

from clarify_todo import (
    KINDS,
    QUESTION_CAP,
    SCHEMA,
    TEXT_LIMIT,
    TODO_CAP,
    Clarify,
    Record,
    Snapshot,
    Todo,
    TodoList,
    add_todo,
    clarify,
    done,
    open_list,
    rebuild,
    run,
    snapshot,
)
from cosmos_hermes import Refuse


def _item(items: tuple[Todo, ...], index: int) -> Todo:
    if index < 0 or index >= len(items):
        raise AssertionError(index)
    return items[index]


def _question(questions: tuple[str, ...], index: int) -> str:
    if index < 0 or index >= len(questions):
        raise AssertionError(index)
    return questions[index]


def test_schema_and_kinds() -> None:
    assert SCHEMA == "cosmos-hermes-clarify_todo/1"
    assert QUESTION_CAP == 5
    assert TODO_CAP == 32
    assert KINDS == frozenset({"plan", "shell"})


def test_clarify_copies_bounded_text() -> None:
    raw = ["  which cone?  ", "ship Friday?"]
    asked = clarify(raw)
    assert isinstance(asked, Clarify)
    assert asked.cap == QUESTION_CAP
    assert asked.questions == ("which cone?", "ship Friday?")
    raw.append("sk-abcdefghijklmnop")
    raw[0] = ""
    assert asked.questions == ("which cone?", "ship Friday?")
    pair = ("hold", "ship")
    assert clarify(pair) == Clarify(questions=pair, cap=QUESTION_CAP)
    shell_question = clarify(["run a shell?"])
    assert _question(shell_question.questions, 0) == "run a shell?"
    assert clarify(["which cone?"]) == clarify(["which cone?"])


def test_nothing_to_ask_and_bad_questions() -> None:
    with pytest.raises(Refuse) as empty:
        clarify([])
    assert empty.value.code == "NOTHING_TO_ASK"
    with pytest.raises(Refuse) as empty_tuple:
        clarify(())
    assert empty_tuple.value.code == "NOTHING_TO_ASK"
    for bad in ("Which port?", None, 1, {"q": "x"}, b""):
        with pytest.raises(Refuse) as refused:
            clarify(bad)
        assert refused.value.code == "BAD_QUESTIONS"
    with pytest.raises(Refuse) as direct:
        Clarify(questions=cast(tuple[str, ...], ["which cone?"]), cap=1)
    assert direct.value.code == "BAD_QUESTIONS"


def test_question_bounds_secret_and_cap() -> None:
    with pytest.raises(Refuse) as not_text:
        clarify([1])
    assert not_text.value.code == "NOT_TEXT"
    with pytest.raises(Refuse) as nul:
        clarify(["a\x00b"])
    assert nul.value.code == "NULL_BYTE"
    with pytest.raises(Refuse) as size:
        clarify(["q" * (TEXT_LIMIT + 1)])
    assert size.value.code == "OVERSIZE"
    assert size.value.detail == str(TEXT_LIMIT)
    kept = clarify(["q" * TEXT_LIMIT])
    assert _question(kept.questions, 0) == "q" * TEXT_LIMIT
    with pytest.raises(Refuse) as blank:
        clarify(["ready", "   "])
    assert blank.value.code == "EMPTY"
    with pytest.raises(Refuse) as spaces:
        clarify([" \n\t"])
    assert spaces.value.code == "EMPTY"
    with pytest.raises(Refuse) as secret:
        clarify(["use Bearer abcdefghijk"])
    assert secret.value.code == "SECRET"
    assert "abcdefgh" not in str(secret.value)
    with pytest.raises(Refuse) as assigned:
        clarify(["password=hunter2"])
    assert assigned.value.code == "SECRET"
    batch = [f"cone {index}?" for index in range(QUESTION_CAP)]
    full = clarify(batch, requested_cap=10**6)
    assert full.cap == QUESTION_CAP
    assert len(full.questions) == QUESTION_CAP
    with pytest.raises(Refuse) as over:
        clarify(batch + ["one more?"])
    assert over.value.code == "QUESTION_CAP"
    tight = clarify(["which cone?"], requested_cap=1)
    assert tight.cap == 1
    with pytest.raises(Refuse) as tight_over:
        clarify(["which cone?", "which glaze?"], requested_cap=1)
    assert tight_over.value.code == "QUESTION_CAP"
    with pytest.raises(Refuse) as boolean_cap:
        clarify(["which cone?"], True)
    assert boolean_cap.value.code == "NOT_INT"
    with pytest.raises(Refuse) as text_cap:
        clarify(["which cone?"], "4")
    assert text_cap.value.code == "NOT_INT"
    with pytest.raises(Refuse) as zero:
        clarify(["which cone?"], 0)
    assert zero.value.code == "BAD_LIMIT"
    with pytest.raises(Refuse) as negative:
        clarify((), -3)
    assert negative.value.code == "BAD_LIMIT"


def test_add_and_done_changes_only_the_record() -> None:
    kiln = add_todo("load kiln", add_todo("mix glaze"))
    assert [item.id for item in kiln.items] == [1, 2]
    assert [item.text for item in kiln.items] == ["mix glaze", "load kiln"]
    assert [item.kind for item in kiln.items] == ["plan", "plan"]
    assert [item.done for item in kiln.items] == [False, False]
    before = _item(kiln.items, 0)
    marked = done(1, kiln)
    after = _item(marked.items, 0)
    assert after is not before
    assert before.done is False
    assert after.done is True
    assert after.id == before.id
    assert after.text == before.text
    assert after.kind == before.kind
    assert _item(marked.items, 1) is _item(kiln.items, 1)
    assert _item(marked.items, 1).done is False
    assert done(1, marked) is marked
    padded = add_todo("  mix glaze  ")
    assert _item(padded.items, 0).text == "mix glaze"
    assert "sk-" not in repr(padded)
    assert "Bearer" not in repr(padded)
    assert "api_key" not in repr(padded)


def test_cap_policy() -> None:
    opened = open_list(TODO_CAP + 50)
    assert opened.cap == TODO_CAP
    assert TodoList(items=(), cap=100).cap == TODO_CAP
    started = add_todo("first", requested_cap=10**6)
    assert started.cap == TODO_CAP
    todo_list = opened
    for index in range(TODO_CAP):
        todo_list = add_todo(f"item {index}", todo_list, requested_cap=1)
    assert len(todo_list.items) == TODO_CAP
    assert todo_list.cap == TODO_CAP
    with pytest.raises(Refuse) as over:
        add_todo("extra", todo_list)
    assert over.value.code == "TODO_CAP"
    assert len(todo_list.items) == TODO_CAP
    with pytest.raises(Refuse) as secret_when_full:
        add_todo("sk-abcdefghijklmnop", todo_list)
    assert secret_when_full.value.code == "SECRET"
    tight = add_todo("only", requested_cap=1)
    assert tight.cap == 1
    with pytest.raises(Refuse) as tight_over:
        add_todo("second", tight, requested_cap=TODO_CAP)
    assert tight_over.value.code == "TODO_CAP"
    held = open_list(4)
    grown = add_todo("mix glaze", held, requested_cap=TODO_CAP)
    assert grown.cap == 4
    with pytest.raises(Refuse) as bad_request:
        add_todo("load kiln", grown, requested_cap=0)
    assert bad_request.value.code == "BAD_LIMIT"
    with pytest.raises(Refuse) as bad_flag:
        add_todo("load kiln", grown, requested_cap=True)
    assert bad_flag.value.code == "NOT_INT"


def test_direct_over_cap_refuses() -> None:
    with pytest.raises(Refuse) as over:
        TodoList(
            items=(
                Todo(id=1, text="one", done=False),
                Todo(id=2, text="two", done=False),
            ),
            cap=1,
        )
    assert over.value.code == "TODO_CAP"


def test_shell_line_stays_inert() -> None:
    plan = Todo(id=1, text="run the kiln", done=False)
    assert plan.kind == "plan"
    cone = Todo(id=1, text="the shell of the cone", done=False)
    assert cone.kind == "plan"
    shell = add_todo("run a shell")
    assert _item(shell.items, 0).kind == "shell"
    assert _item(shell.items, 0).done is False
    bash = add_todo("bash -c echo hi")
    assert _item(bash.items, 0).kind == "shell"
    piped = add_todo("warm the kiln | sh")
    assert _item(piped.items, 0).kind == "shell"
    with pytest.raises(Refuse) as refused:
        run(shell, 1)
    assert refused.value.code == "NOT_A_TOOL"
    assert refused.value.detail == ""
    assert "shell" not in str(refused.value)
    assert _item(shell.items, 0).done is False
    assert _item(shell.items, 0).text == "run a shell"
    marked = done(1, shell)
    assert _item(marked.items, 0).done is True
    assert _item(marked.items, 0).kind == "shell"
    assert _item(marked.items, 0).text == "run a shell"
    with pytest.raises(Refuse) as again:
        run(marked, 1)
    assert again.value.code == "NOT_A_TOOL"
    assert _item(marked.items, 0).done is True


def test_unknown_todo_and_run() -> None:
    todo_list = add_todo("ship the note")
    with pytest.raises(Refuse) as missing:
        done(2, todo_list)
    assert missing.value.code == "UNKNOWN_TODO"
    with pytest.raises(Refuse) as zero:
        done(0, todo_list)
    assert zero.value.code == "UNKNOWN_TODO"
    with pytest.raises(Refuse) as negative:
        done(-1, open_list())
    assert negative.value.code == "UNKNOWN_TODO"
    with pytest.raises(Refuse) as huge:
        done(10**9, todo_list)
    assert huge.value.code == "UNKNOWN_TODO"
    with pytest.raises(Refuse) as bare:
        run()
    assert bare.value.code == "NOT_A_TOOL"
    with pytest.raises(Refuse) as whole:
        run(todo_list)
    assert whole.value.code == "NOT_A_TOOL"
    with pytest.raises(Refuse) as known:
        run(todo_list, 1)
    assert known.value.code == "NOT_A_TOOL"
    assert _item(todo_list.items, 0).done is False
    with pytest.raises(Refuse) as absent:
        run(todo_list, 2)
    assert absent.value.code == "UNKNOWN_TODO"
    with pytest.raises(Refuse) as no_list:
        run(None, 1)
    assert no_list.value.code == "BAD_LIST"
    with pytest.raises(Refuse) as bad_id:
        run(todo_list, True)
    assert bad_id.value.code == "NOT_INT"
    hidden = "sk-abcdefghijklmnop"
    with pytest.raises(Refuse) as leaked:
        run(hidden)
    assert leaked.value.code == "BAD_LIST"
    assert "abcdefgh" not in str(leaked.value)


def test_text_cap_secret_and_empty() -> None:
    exact = add_todo("t" * TEXT_LIMIT)
    assert _item(exact.items, 0).text == "t" * TEXT_LIMIT
    with pytest.raises(Refuse) as size:
        add_todo("t" * (TEXT_LIMIT + 1))
    assert size.value.code == "OVERSIZE"
    assert size.value.detail == str(TEXT_LIMIT)
    with pytest.raises(Refuse) as secret:
        add_todo("sk-abcdefghijklmnop")
    assert secret.value.code == "SECRET"
    assert "abcdefgh" not in str(secret.value)
    with pytest.raises(Refuse) as key:
        Todo(id=1, text="api_key=abcd", done=False)
    assert key.value.code == "SECRET"
    with pytest.raises(Refuse) as blank:
        add_todo("")
    assert blank.value.code == "EMPTY"
    with pytest.raises(Refuse) as spaces:
        add_todo("  \t")
    assert spaces.value.code == "EMPTY"
    with pytest.raises(Refuse) as not_text:
        add_todo(12)
    assert not_text.value.code == "NOT_TEXT"
    with pytest.raises(Refuse) as nul:
        add_todo("a\x00b")
    assert nul.value.code == "NULL_BYTE"


def test_list_shape_ids_and_kind() -> None:
    with pytest.raises(Refuse) as bad_add:
        add_todo("text", "list")
    assert bad_add.value.code == "BAD_LIST"
    with pytest.raises(Refuse) as bad_done:
        done(1, ())
    assert bad_done.value.code == "BAD_LIST"
    with pytest.raises(Refuse) as bad_items:
        TodoList(items=cast(tuple[Todo, ...], [Todo(id=1, text="a", done=False)]))
    assert bad_items.value.code == "BAD_LIST"
    with pytest.raises(Refuse) as gap:
        TodoList(items=(Todo(id=1, text="a", done=False), Todo(id=3, text="b", done=False)))
    assert gap.value.code == "BAD_LIST"
    with pytest.raises(Refuse) as dup:
        TodoList(items=(Todo(id=1, text="a", done=False), Todo(id=1, text="b", done=False)))
    assert dup.value.code == "DUPLICATE"
    with pytest.raises(Refuse) as flag:
        Todo(id=1, text="a", done=cast(bool, 0))
    assert flag.value.code == "BAD_LIST"
    with pytest.raises(Refuse) as low:
        Todo(id=0, text="a", done=False)
    assert low.value.code == "OUT_OF_RANGE"
    assert low.value.detail == f"1..{TODO_CAP}"
    with pytest.raises(Refuse) as high:
        Todo(id=TODO_CAP + 1, text="a", done=False)
    assert high.value.code == "OUT_OF_RANGE"
    edge = Todo(id=TODO_CAP, text="last", done=False)
    assert edge.id == TODO_CAP
    assert edge.kind == "plan"
    with pytest.raises(Refuse) as boolean_id:
        Todo(id=cast(int, True), text="a", done=False)
    assert boolean_id.value.code == "NOT_INT"
    with pytest.raises(Refuse) as bad_done_id:
        done(True, open_list())
    assert bad_done_id.value.code == "NOT_INT"
    with pytest.raises(Refuse) as named:
        done("1", open_list())
    assert named.value.code == "NOT_INT"
    with pytest.raises(Refuse) as claimed:
        Todo(id=1, text="mix glaze", done=False, kind="shell")
    assert claimed.value.code == "BAD_KIND"
    with pytest.raises(Refuse) as denied:
        Todo(id=1, text="run a shell", done=False, kind="plan")
    assert denied.value.code == "BAD_KIND"
    with pytest.raises(Refuse) as unknown:
        Todo(id=1, text="mix glaze", done=False, kind="nope")
    assert unknown.value.code == "BAD_KIND"
    derived = Todo(id=1, text="run a shell", done=False)
    assert derived.kind == "shell"


def test_cap_arguments_and_stale_schema() -> None:
    with pytest.raises(Refuse) as boolean_cap:
        open_list(True)
    assert boolean_cap.value.code == "NOT_INT"
    with pytest.raises(Refuse) as text_cap:
        open_list("4")
    assert text_cap.value.code == "NOT_INT"
    with pytest.raises(Refuse) as zero:
        open_list(0)
    assert zero.value.code == "BAD_LIMIT"
    with pytest.raises(Refuse) as negative:
        open_list(-3)
    assert negative.value.code == "BAD_LIMIT"
    with pytest.raises(Refuse) as constructed:
        TodoList(cap=cast(int, True))
    assert constructed.value.code == "NOT_INT"
    with pytest.raises(Refuse) as low:
        TodoList(cap=0)
    assert low.value.code == "BAD_LIMIT"
    with pytest.raises(Refuse) as bad_new:
        add_todo("text", requested_cap=0)
    assert bad_new.value.code == "BAD_LIMIT"
    with pytest.raises(Refuse) as stale:
        TodoList(items=(), cap=1, schema="cosmos-hermes-other/1")
    assert stale.value.code == "STALE"
    with pytest.raises(Refuse) as stale_type:
        TodoList(items=(), cap=1, schema=cast(str, None))
    assert stale_type.value.code == "STALE"


def test_snapshot_rebuild_duplicate_and_stale() -> None:
    original = done(1, add_todo("load kiln", add_todo("mix glaze")))
    shot = snapshot(original)
    assert isinstance(shot, Snapshot)
    assert shot.schema == SCHEMA
    assert shot.cap == original.cap
    restored = rebuild(shot)
    assert restored == original
    assert rebuild(snapshot(restored)) == original
    empty = open_list(2)
    assert rebuild(snapshot(empty)) == empty
    with pytest.raises(Refuse) as bad:
        rebuild(())
    assert bad.value.code == "BAD_LIST"
    with pytest.raises(Refuse) as stale:
        Snapshot(schema="cosmos-hermes-other/1", cap=1, items=())
    assert stale.value.code == "STALE"
    with pytest.raises(Refuse) as stale_row:
        Record(schema="nope", id=1, text="mix glaze", done=False, kind="plan")
    assert stale_row.value.code == "STALE"
    with pytest.raises(Refuse) as bad_kind:
        Record(schema=SCHEMA, id=1, text="mix glaze", done=False, kind="shell")
    assert bad_kind.value.code == "BAD_KIND"
    with pytest.raises(Refuse) as bad_flag:
        Record(schema=SCHEMA, id=1, text="mix glaze", done=cast(bool, 1), kind="plan")
    assert bad_flag.value.code == "BAD_LIST"
    first = Record(schema=SCHEMA, id=1, text="mix glaze", done=False, kind="plan")
    second = Record(schema=SCHEMA, id=1, text="load kiln", done=False, kind="plan")
    with pytest.raises(Refuse) as dup:
        Snapshot(schema=SCHEMA, cap=TODO_CAP, items=(first, second))
    assert dup.value.code == "DUPLICATE"
    third = Record(schema=SCHEMA, id=3, text="load kiln", done=False, kind="plan")
    with pytest.raises(Refuse) as gap:
        Snapshot(schema=SCHEMA, cap=TODO_CAP, items=(first, third))
    assert gap.value.code == "BAD_LIST"
    with pytest.raises(Refuse) as row_type:
        Snapshot(schema=SCHEMA, cap=1, items=cast(tuple[Record, ...], (Todo(id=1, text="a", done=False),)))
    assert row_type.value.code == "BAD_LIST"
    with pytest.raises(Refuse) as over:
        Snapshot(schema=SCHEMA, cap=1, items=(first, Record(schema=SCHEMA, id=2, text="b", done=True, kind="plan")))
    assert over.value.code == "TODO_CAP"


def test_example_clarify_todo() -> None:
    """The kiln card asks which cone, then stores two inert steps."""
    first = _kiln_story()
    second = _kiln_story()
    assert first == second
    asked, listed, shot, restored, code = first
    assert _question(asked.questions, 0) == "which cone?"
    assert asked.cap == QUESTION_CAP
    assert _item(listed.items, 0).text == "mix glaze"
    assert _item(listed.items, 0).done is True
    assert _item(listed.items, 0).kind == "plan"
    assert _item(listed.items, 1).text == "load kiln"
    assert _item(listed.items, 1).done is False
    assert _item(listed.items, 2).text == "run a shell"
    assert _item(listed.items, 2).kind == "shell"
    assert _item(listed.items, 2).done is False
    assert restored == listed
    assert shot.items[0].text == "mix glaze"
    assert code == "NOT_A_TOOL"


def _kiln_story() -> tuple[Clarify, TodoList, Snapshot, TodoList, str]:
    asked = clarify(["which cone?"], requested_cap=100)
    glaze = add_todo("mix glaze")
    kiln = add_todo("load kiln", glaze)
    before = _item(kiln.items, 0)
    marked = done(1, kiln)
    after = _item(marked.items, 0)
    assert after is not before
    assert before.done is False
    assert after.done is True
    assert after.text == "mix glaze"
    assert after.kind == "plan"
    assert _item(marked.items, 1) is _item(kiln.items, 1)
    assert _item(marked.items, 1).text == "load kiln"
    assert _item(marked.items, 1).done is False
    listed = add_todo("run a shell", marked)
    shell = _item(listed.items, 2)
    assert shell.kind == "shell"
    assert shell.done is False
    shot = snapshot(listed)
    restored = rebuild(shot)
    assert restored == listed
    try:
        run(listed, 3)
    except Refuse as refused:
        code = refused.code
    else:
        raise AssertionError("run returned")
    assert shell.done is False
    assert shell.text == "run a shell"
    assert shell.kind == "shell"
    return (asked, listed, shot, restored, code)
