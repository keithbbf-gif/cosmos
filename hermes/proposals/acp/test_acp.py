"""Editor messages as data. No editor is started."""

from __future__ import annotations

import ast
import json
import shutil
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import cast

import pytest

from acp import (
    AGENT_NAME,
    DEPTH_CAP,
    KINDS,
    MESSAGE_CAP,
    METHODS,
    NEED_APPROVAL,
    NODE_CAP,
    PROTOCOL,
    SCHEMA,
    SEEN_CAP,
    SESSION_CAP,
    TEXT_CAP,
    Approval,
    Desk,
    DisplayRecord,
    Exchange,
    Reply,
    Session,
    TerminalRecord,
    Turn,
    answer,
    decide,
    message,
    open_desk,
    rebuild,
)
from cosmos_hermes import PathJail, Refuse, secret_shape


def refused(exc: object) -> Refuse:
    assert isinstance(exc, Refuse)
    assert secret_shape(str(exc)) is False
    assert secret_shape(repr(exc)) is False
    return exc


def frame(
    method: str,
    request_id: object,
    params: dict[str, object] | None,
    *,
    notify: bool = False,
) -> str:
    payload: dict[str, object] = {"jsonrpc": "2.0", "method": method}
    if not notify:
        payload["id"] = request_id
    if params is not None:
        payload["params"] = params
    return json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def init_body(version: object = 2) -> dict[str, object]:
    return {
        "capabilities": {},
        "info": {"name": "zed", "title": "Zed", "version": "0.9.1"},
        "protocolVersion": version,
    }


def obj(raw: str) -> dict[str, object]:
    loaded: object = json.loads(raw)
    if not isinstance(loaded, dict):
        raise AssertionError("object")
    out: dict[str, object] = {}
    for key, value in loaded.items():
        if not isinstance(key, str):
            raise AssertionError("key")
        out[key] = value
    return out


def field(raw: dict[str, object], key: str) -> dict[str, object]:
    value = raw[key]
    if not isinstance(value, dict):
        raise AssertionError(key)
    out: dict[str, object] = {}
    for name, item in value.items():
        if not isinstance(name, str):
            raise AssertionError(name)
        out[name] = item
    return out


def session_at(desk: Desk, index: int) -> Session:
    if index < 0 or index >= len(desk.sessions):
        raise AssertionError(index)
    return desk.sessions[index]


def turn_at(turns: tuple[Turn, ...], index: int) -> Turn:
    if index < 0 or index >= len(turns):
        raise AssertionError(index)
    return turns[index]


def note_at(notes: tuple[Reply, ...], index: int) -> Reply:
    if index < 0 or index >= len(notes):
        raise AssertionError(index)
    return notes[index]


def ids_of(value: object) -> list[object]:
    if not isinstance(value, list):
        raise AssertionError("list")
    found: list[object] = []
    for item in value:
        if not isinstance(item, dict):
            raise AssertionError("row")
        found.append(item.get("sessionId"))
    return found


@contextmanager
def lab() -> Iterator[tuple[PathJail, str]]:
    root = tempfile.mkdtemp(prefix="acp-north-lab-")
    try:
        yield PathJail((root,)), root
    finally:
        shutil.rmtree(root)


@contextmanager
def yard() -> Iterator[tuple[PathJail, str, str]]:
    parent = Path(tempfile.mkdtemp(prefix="acp-yard-"))
    north = parent / "north-lab"
    south = parent / "south-lab"
    north.mkdir()
    south.mkdir()
    try:
        yield PathJail((str(parent),)), str(north), str(south)
    finally:
        shutil.rmtree(parent)


def ready(jail: PathJail, cap: object = None, allow: object = None) -> Desk:
    desk = open_desk(jail, cap=cap, allow=allow)
    opened = answer(desk, frame("initialize", 0, init_body()), jail)
    return opened.desk


Story = tuple[Exchange, Exchange, Exchange, DisplayRecord, TerminalRecord, Approval, str]


def _story(jail: PathJail, root: str) -> Story:
    desk = open_desk(jail)
    init = answer(desk, frame("initialize", 0, init_body()), jail)
    opened = answer(
        init.desk,
        frame(
            "session/new",
            1,
            {"cwd": root, "mcpServers": [], "model": "lab-note"},
        ),
        jail,
    )
    session = session_at(opened.desk, 0)
    prompted = answer(
        opened.desk,
        frame(
            "session/prompt",
            2,
            {
                "sessionId": session.session_id,
                "prompt": [
                    {"type": "text", "text": "Mara hangs the lumen card on the hook."},
                    {"type": "text", "text": "The calibration note sits under the aisle light."},
                ],
            },
        ),
        jail,
    )
    shown = message("diff", "the aisle light stays at dusk")
    held = message("terminal", "git status")
    if not isinstance(shown, DisplayRecord) or not isinstance(held, TerminalRecord):
        raise AssertionError("record")
    choice = decide("allow_once")
    code = "UNCAUGHT"
    try:
        answer(prompted.desk, frame("session/fork", 9, {}), jail)
    except Refuse as refused:
        code = refused.code
    return init, opened, prompted, shown, held, choice, code


def test_schema_and_closed_source() -> None:
    assert SCHEMA == "cosmos-hermes-acp/1"
    assert PROTOCOL == 2
    assert TEXT_CAP == 32_000
    assert NEED_APPROVAL == "NEED_APPROVAL"
    assert KINDS == ("prompt", "tool", "diff", "terminal")
    assert METHODS == (
        "initialize",
        "session/cancel",
        "session/close",
        "session/list",
        "session/new",
        "session/prompt",
        "session/resume",
    )
    assert AGENT_NAME == "cosmos-hermes"
    source = Path(__file__).with_name("acp.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported.add(alias.name)
        if isinstance(node, ast.ImportFrom) and node.module is not None:
            imported.add(node.module)
    assert imported <= {"__future__", "json", "re", "dataclasses", "typing", "cosmos_hermes"}
    banned = ("subprocess", "socket", "urllib", "requests", "pickle", "eval", "exec")
    assert all(word not in source for word in banned)


def test_example_acp() -> None:
    with lab() as (jail, root):
        first = _story(jail, root)
        second = _story(jail, root)
        assert first == second
        assert repr(first) == repr(second)
        assert secret_shape(repr(first)) is False
        init, opened, prompted, shown, held, choice, code = first
        body = field(obj(init.reply.body), "result")
        assert body["protocolVersion"] == PROTOCOL
        assert body["authMethods"] == []
        assert field(body, "capabilities") == {"session": {}}
        assert "stdio" not in init.reply.body
        assert init.reply.sent is False
        assert init.desk.client_name == "zed"
        assert init.desk.client_title == "Zed"
        assert init.desk.protocol == PROTOCOL
        created = field(obj(opened.reply.body), "result")
        session = session_at(opened.desk, 0)
        assert created["sessionId"] == "sess-1"
        assert session.session_id == "sess-1"
        assert session.model == "lab-note"
        assert session.cancelled is False
        assert session.closed is False
        assert session.cwd != ""
        inserted = field(obj(prompted.reply.body), "result")
        assert inserted["messageId"] == "msg-1"
        turn = turn_at(session_at(prompted.desk, 0).history, 0)
        assert turn.blocks == (
            "Mara hangs the lumen card on the hook.",
            "The calibration note sits under the aisle light.",
        )
        note = note_at(prompted.notes, 0)
        assert note.method == "session/update"
        assert note.sent is False
        assert "lumen card" in note.body
        assert prompted.reply.sent is False
        assert isinstance(shown, DisplayRecord)
        assert shown.kind == "diff"
        assert shown.text == "the aisle light stays at dusk"
        assert isinstance(held, TerminalRecord)
        assert held.code == "NEED_APPROVAL"
        assert held.text == "git status"
        assert choice.choice == "allow_once"
        assert choice.code == "ALLOW_ONCE"
        assert choice.runs is False
        assert choice.persisted is False
        assert code == "UNKNOWN_METHOD"
        desk = prompted.desk
        assert (
            rebuild(
                desk.sessions,
                desk.seen,
                initialized=desk.initialized,
                protocol=desk.protocol,
                client_name=desk.client_name,
                client_title=desk.client_title,
                client_version=desk.client_version,
                client_protocol=desk.client_protocol,
                next_message=desk.next_message,
                grants=desk.grants,
                methods=desk.methods,
                cap=desk.cap,
            )
            == desk
        )


def test_same_inputs_and_key_order() -> None:
    with lab() as (jail, _root):
        desk = open_desk(jail)
        raw = frame("initialize", 0, init_body())
        assert answer(desk, raw, jail) == answer(desk, raw, jail)
        other = json.dumps(
            {
                "params": init_body(),
                "id": 0,
                "method": "initialize",
                "jsonrpc": "2.0",
            }
        )
        assert answer(desk, raw, jail) == answer(desk, other, jail)


def test_round_trip_version_and_narrow_allow() -> None:
    with lab() as (jail, root):
        desk = open_desk(jail)
        opened = answer(desk, frame("initialize", 3, init_body(1)), jail)
        assert opened.desk.client_protocol == 1
        assert opened.desk.protocol == PROTOCOL
        assert field(obj(opened.reply.body), "result")["protocolVersion"] == PROTOCOL
        created = answer(opened.desk, frame("session/new", 4, {"cwd": root}), jail)
        assert field(obj(created.reply.body), "result")["sessionId"] == "sess-1"
        narrow = open_desk(jail, allow=("session/new", "initialize"))
        assert narrow.methods == ("initialize", "session/new")
        live = answer(narrow, frame("initialize", 0, init_body()), jail)
        with pytest.raises(Refuse) as caught:
            answer(live.desk, frame("session/prompt", 1, {}), jail)
        assert refused(caught.value).code == "UNKNOWN_METHOD"
        with pytest.raises(Refuse) as caught:
            answer(live.desk, frame("auth/login", 2, {}), jail)
        assert refused(caught.value).code == "UNKNOWN_METHOD"
        with pytest.raises(Refuse) as caught:
            answer(live.desk, frame("yolo", 3, {}), jail)
        assert refused(caught.value).code == "UNKNOWN_METHOD"
        with pytest.raises(Refuse) as caught:
            answer(live.desk, frame("off", 4, {}), jail)
        assert refused(caught.value).code == "UNKNOWN_METHOD"


def test_malformed_editor_messages() -> None:
    with lab() as (jail, _root):
        desk = open_desk(jail)
        samples: tuple[tuple[object, str], ...] = (
            ("{", "BAD_MESSAGE"),
            ("[]", "BAD_MESSAGE"),
            ("null", "BAD_MESSAGE"),
            ("", "BAD_MESSAGE"),
            ('{"jsonrpc":"2.0","id":1,"result":{}}', "BAD_MESSAGE"),
            ('{"jsonrpc":"2.0","id":1,"error":{"code":-32601}}', "BAD_MESSAGE"),
            ('{"id":1,"method":"initialize","params":{}}', "BAD_MESSAGE"),
            ('{"jsonrpc":2,"id":1,"method":"initialize","params":{}}', "BAD_MESSAGE"),
            (frame("initialize", 1.5, init_body()), "BAD_MESSAGE"),
            (1, "NOT_TEXT"),
            (None, "NOT_TEXT"),
            (b"{}", "NOT_TEXT"),
            ("\x00", "NULL_BYTE"),
        )
        for raw, code in samples:
            with pytest.raises(Refuse) as caught:
                answer(desk, raw, jail)
            assert refused(caught.value).code == code
        with pytest.raises(Refuse) as caught:
            answer("desk", frame("initialize", 0, init_body()), jail)
        assert refused(caught.value).code == "BAD_MESSAGE"
        missing = json.dumps({"jsonrpc": "2.0", "id": 1, "params": {}})
        with pytest.raises(Refuse) as caught:
            answer(desk, missing, jail)
        assert refused(caught.value).code == "BAD_METHOD"
        for raw, code in (
            (frame("Initialize", 1, init_body()), "BAD_METHOD"),
            (frame("", 1, init_body()), "BAD_METHOD"),
            (frame("session/new ", 1, {}), "BAD_METHOD"),
        ):
            with pytest.raises(Refuse) as caught:
                answer(desk, raw, jail)
            assert refused(caught.value).code == code
        for raw in (
            frame("initialize", None, init_body()),
            frame("initialize", True, init_body()),
            frame("initialize", "", init_body()),
            frame("initialize", "bad id", init_body()),
        ):
            with pytest.raises(Refuse) as caught:
                answer(desk, raw, jail)
            assert refused(caught.value).code == "BAD_ID"
        with pytest.raises(Refuse) as caught:
            answer(desk, frame("initialize", -1, init_body()), jail)
        assert refused(caught.value).code == "OUT_OF_RANGE"
        with pytest.raises(Refuse) as caught:
            answer(desk, frame("initialize", 3_000_000_000, init_body()), jail)
        assert refused(caught.value).code == "OUT_OF_RANGE"
        with pytest.raises(Refuse) as caught:
            answer(desk, frame("initialize", 1, {}), jail)
        assert refused(caught.value).code == "BAD_VERSION"
        with pytest.raises(Refuse) as caught:
            answer(desk, frame("initialize", 1, init_body(True)), jail)
        assert refused(caught.value).code == "NOT_INT"
        with pytest.raises(Refuse) as caught:
            answer(desk, frame("initialize", 1, init_body(0)), jail)
        assert refused(caught.value).code == "OUT_OF_RANGE"
        with pytest.raises(Refuse) as caught:
            answer(desk, frame("initialize", 1, {"protocolVersion": 2}), jail)
        assert refused(caught.value).code == "BAD_PARAMS"
        with pytest.raises(Refuse) as caught:
            answer(desk, frame("initialize", 1, init_body()) + "x", jail)
        assert refused(caught.value).code == "BAD_MESSAGE"


def test_caps_and_replay() -> None:
    with lab() as (jail, root):
        raw = frame("initialize", 0, init_body())
        tight = open_desk(jail, cap=len(raw))
        assert tight.cap == len(raw)
        assert tight.policy_cap == TEXT_CAP
        assert answer(tight, raw, jail).reply.cap == len(raw)
        with pytest.raises(Refuse) as caught:
            answer(tight, raw + " ", jail)
        assert refused(caught.value).code == "OVERSIZE"
        assert refused(caught.value).detail == str(len(raw))
        wide = open_desk(jail, cap=TEXT_CAP * 4)
        assert wide.cap == TEXT_CAP
        assert wide.policy_cap == TEXT_CAP
        for bad in (True, False, 0, -1, "32000", 1.5):
            with pytest.raises(Refuse) as caught:
                open_desk(jail, cap=bad)
            assert refused(caught.value).code == "BAD_LIMIT"
        opened = answer(open_desk(jail), raw, jail)
        with pytest.raises(Refuse) as caught:
            answer(opened.desk, raw, jail)
        assert refused(caught.value).code == "DUPLICATE"
        with pytest.raises(Refuse) as caught:
            answer(opened.desk, frame("initialize", 8, init_body()), jail)
        assert refused(caught.value).code == "ALREADY"
        fresh = open_desk(jail)
        with pytest.raises(Refuse) as caught:
            answer(fresh, frame("session/new", 1, {"cwd": root}), jail)
        assert refused(caught.value).code == "NOT_READY"
        with pytest.raises(Refuse) as caught:
            answer(fresh, frame("session/cancel", None, {"sessionId": "sess-1"}, notify=True), jail)
        assert refused(caught.value).code == "NOT_READY"
        with pytest.raises(Refuse) as caught:
            open_desk(jail, allow=())
        assert refused(caught.value).code == "EMPTY_ALLOW"
        with pytest.raises(Refuse) as caught:
            open_desk(jail, allow=("initialize", "initialize"))
        assert refused(caught.value).code == "DUPLICATE"
        with pytest.raises(Refuse) as caught:
            open_desk(jail, allow=("session/delete",))
        assert refused(caught.value).code == "BAD_METHOD"
        with pytest.raises(Refuse) as caught:
            open_desk(jail, allow="initialize")
        assert refused(caught.value).code == "BAD_PARAMS"
        with pytest.raises(Refuse) as caught:
            open_desk("nope")
        assert refused(caught.value).code == "BAD_JAIL"
        other = tempfile.mkdtemp(prefix="acp-other-")
        try:
            with pytest.raises(Refuse) as caught:
                answer(fresh, raw, PathJail((other,)))
            assert refused(caught.value).code == "BAD_JAIL"
        finally:
            shutil.rmtree(other)


def test_session_lifecycle_skips_closed() -> None:
    with lab() as (jail, root):
        desk = ready(jail)
        one = answer(desk, frame("session/new", 1, {"cwd": root, "model": "card"}), jail)
        two = answer(one.desk, frame("session/new", 2, {"cwd": root, "model": "note"}), jail)
        three = answer(two.desk, frame("session/new", 3, {"cwd": root, "model": "light"}), jail)
        closed = answer(three.desk, frame("session/close", 4, {"sessionId": "sess-2"}), jail)
        assert session_at(closed.desk, 1).closed is True
        listed = answer(closed.desk, frame("session/list", 5, {}), jail)
        assert ids_of(field(obj(listed.reply.body), "result")["sessions"]) == ["sess-1", "sess-3"]
        prompted = answer(
            listed.desk,
            frame(
                "session/prompt",
                6,
                {
                    "sessionId": "sess-1",
                    "prompt": [{"type": "text", "text": "Mara leaves the lumen card."}],
                },
            ),
            jail,
        )
        assert session_at(prompted.desk, 0).cancelled is False
        cancelled = answer(
            prompted.desk,
            frame("session/cancel", None, {"sessionId": "sess-1"}, notify=True),
            jail,
        )
        assert cancelled.reply.code == "CANCELLED"
        assert cancelled.reply.method == "session/update"
        assert cancelled.reply.sent is False
        assert session_at(cancelled.desk, 0).cancelled is True
        assert cancelled.notes == ()
        resumed = answer(
            cancelled.desk,
            frame(
                "session/resume",
                7,
                {"cwd": root, "sessionId": "sess-1", "replayFrom": {"type": "start"}},
            ),
            jail,
        )
        assert resumed.reply.sent is False
        assert field(obj(resumed.reply.body), "result") == {}
        assert note_at(resumed.notes, 0).method == "session/update"
        assert "lumen card" in note_at(resumed.notes, 0).body
        quiet = answer(
            resumed.desk,
            frame("session/resume", 8, {"cwd": root, "sessionId": "sess-3"}),
            jail,
        )
        assert quiet.notes == ()
        with pytest.raises(Refuse) as caught:
            answer(
                quiet.desk,
                frame("session/cancel", 9, {"sessionId": "sess-1"}),
                jail,
            )
        assert refused(caught.value).code == "BAD_NOTIFY"
        with pytest.raises(Refuse) as caught:
            answer(quiet.desk, frame("session/close", 10, {"sessionId": "sess-2"}), jail)
        assert refused(caught.value).code == "STALE"
        with pytest.raises(Refuse) as caught:
            answer(
                quiet.desk,
                frame("session/resume", 11, {"cwd": root, "sessionId": "sess-2"}),
                jail,
            )
        assert refused(caught.value).code == "STALE"
        with pytest.raises(Refuse) as caught:
            answer(
                quiet.desk,
                frame(
                    "session/prompt",
                    12,
                    {"sessionId": "sess-2", "prompt": [{"type": "text", "text": "later"}]},
                ),
                jail,
            )
        assert refused(caught.value).code == "CLOSED"
        with pytest.raises(Refuse) as caught:
            answer(
                quiet.desk,
                frame("session/cancel", None, {"sessionId": "sess-2"}, notify=True),
                jail,
            )
        assert refused(caught.value).code == "CLOSED"
        with pytest.raises(Refuse) as caught:
            answer(quiet.desk, frame("session/prompt", 13, {"sessionId": "sess-9", "prompt": []}), jail)
        assert refused(caught.value).code == "UNKNOWN_SESSION"
        with pytest.raises(Refuse) as caught:
            answer(quiet.desk, frame("session/prompt", 14, {"sessionId": "nope"}), jail)
        assert refused(caught.value).code == "BAD_ID"


def test_prompt_shape_and_secrets() -> None:
    with lab() as (jail, root):
        desk = ready(jail)
        opened = answer(desk, frame("session/new", 1, {"cwd": root}), jail)
        current = opened.desk
        samples: tuple[tuple[dict[str, object], str], ...] = (
            ({"sessionId": "sess-1", "prompt": "hello"}, "BAD_PARAMS"),
            ({"sessionId": "sess-1", "prompt": []}, "EMPTY"),
            ({"sessionId": "sess-1", "prompt": [{"type": "text", "text": "  "}]}, "EMPTY"),
            ({"sessionId": "sess-1", "prompt": [{"type": "image", "data": "aa"}]}, "BAD_CONTENT"),
            ({"sessionId": "sess-1", "prompt": [{"type": "text", "text": "bad\x01byte"}]}, "BAD_TEXT"),
            (
                {"sessionId": "sess-1", "prompt": [{"type": "text", "text": "api_key=supersecret"}]},
                "SECRET",
            ),
            (
                {
                    "sessionId": "sess-1",
                    "prompt": [{"type": "text", "text": "Authorization: Bearer abcdefghijk"}],
                },
                "SECRET",
            ),
            (
                {"sessionId": "sess-1", "prompt": [{"type": "text", "text": "sk-livekeyvalue"}]},
                "SECRET",
            ),
        )
        for params, code in samples:
            with pytest.raises(Refuse) as caught:
                answer(current, frame("session/prompt", 2, params), jail)
            assert refused(caught.value).code == code
        assert current == opened.desk
        with pytest.raises(Refuse) as caught:
            answer(
                current,
                frame(
                    "session/new",
                    3,
                    {
                        "cwd": root,
                        "mcpServers": [
                            {"command": "C:/tools/mcp", "name": "tools", "type": "stdio"}
                        ],
                    },
                ),
                jail,
            )
        assert refused(caught.value).code == "MCP_REFUSED"
        assert "C:/tools/mcp" not in str(caught.value)
        with pytest.raises(Refuse) as caught:
            answer(
                current,
                frame(
                    "session/new",
                    4,
                    {"cwd": root, "additionalDirectories": [root]},
                ),
                jail,
            )
        assert refused(caught.value).code == "UNSUPPORTED"
        with pytest.raises(Refuse) as caught:
            answer(current, frame("session/new", 5, {"cwd": root, "mcpServers": {}}), jail)
        assert refused(caught.value).code == "BAD_PARAMS"
        marked = answer(
            current,
            frame(
                "session/prompt",
                6,
                {"sessionId": "sess-1", "prompt": [{"type": "text", "text": "caf\u00e9"}]},
            ),
            jail,
        )
        assert turn_at(session_at(marked.desk, 0).history, 0).blocks == ("café",)
        assert "\\u00e9" in note_at(marked.notes, 0).body


def test_path_refusals() -> None:
    with yard() as (jail, north, south):
        desk = ready(jail)
        opened = answer(desk, frame("session/new", 1, {"cwd": north}), jail)
        with pytest.raises(Refuse) as caught:
            answer(
                opened.desk,
                frame("session/resume", 2, {"cwd": south, "sessionId": "sess-1"}),
                jail,
            )
        assert refused(caught.value).code == "MISMATCH"
    with lab() as (jail, root):
        desk = ready(jail)
        drive = Path(root).drive
        samples: tuple[tuple[str, str], ...] = (
            ("", "BAD_PATH"),
            ("notes/card", "RELATIVE_PATH"),
            (str(Path(root).parent), "OUTSIDE_GRANT"),
            ("file:///C:/north-lab", "FILE_URL"),
            (str(Path(root) / ".." / "other"), "DOTDOT"),
            (root + "/%2e%2e/secret", "ENCODED_DOTDOT"),
            ("\\\\server\\share", "UNC"),
            (drive + "\\", "DRIVE_ROOT"),
            (drive + "notes", "DRIVE_RELATIVE"),
            (root + ":stream", "ALT_STREAM"),
            (str(Path(root) / "card."), "TRAILING_DOT"),
        )
        for cwd, code in samples:
            with pytest.raises(Refuse) as caught:
                answer(desk, frame("session/new", 1, {"cwd": cwd}), jail)
            assert refused(caught.value).code == code


def test_display_terminal_and_decide() -> None:
    prompt = message("prompt", "hello editor")
    tool = message("tool", "read_file note.txt")
    diff = message("diff", "line\n+add\n-del\n")
    assert tool.kind == "tool"
    assert isinstance(prompt, DisplayRecord)
    assert prompt.kind == "prompt"
    assert prompt.schema == SCHEMA
    assert prompt.cap == TEXT_CAP
    assert prompt.policy_cap == TEXT_CAP
    assert diff.text == "line\n+add\n-del\n"
    terminal = message("terminal", "git status")
    assert isinstance(terminal, TerminalRecord)
    assert terminal.code == "NEED_APPROVAL"
    assert terminal == message("terminal", "git status")
    assert not hasattr(terminal, "run")
    with pytest.raises(AttributeError):
        setattr(terminal, "code", "RUN")
    body = "a" * TEXT_CAP
    held = message("tool", body, 10**18)
    assert held.cap == TEXT_CAP
    assert held.policy_cap == TEXT_CAP
    with pytest.raises(Refuse) as caught:
        message("tool", body + "a", 10**18)
    assert refused(caught.value).code == "OVERSIZE"
    assert refused(caught.value).detail == str(TEXT_CAP)
    tight = message("diff", "abcd", 4)
    assert isinstance(tight, DisplayRecord)
    assert tight.cap == 4
    assert tight.text == "abcd"
    mark = message("prompt", "é", 1)
    assert mark.cap == 1
    assert mark.text == "é"
    with pytest.raises(Refuse) as caught:
        message("diff", "abcde", 4)
    assert refused(caught.value).code == "OVERSIZE"
    assert refused(caught.value).detail == "4"
    kinds: tuple[tuple[object, object, str], ...] = (
        ("yolo", "hello", "BAD_MESSAGE"),
        ("off", "hello", "BAD_MESSAGE"),
        ("", "hello", "BAD_MESSAGE"),
        ("TERMINAL", "hello", "BAD_MESSAGE"),
        ("prompt ", "hello", "BAD_MESSAGE"),
        ("sk-abcdefghij", "hello", "SECRET"),
        (None, "hello", "NOT_TEXT"),
        (1, "hello", "NOT_TEXT"),
        ("pro\x00mpt", "hello", "NULL_BYTE"),
        ("prompt", "", "EMPTY"),
        ("terminal", "   \n", "EMPTY"),
        ("tool", "bad\x00byte", "NULL_BYTE"),
        ("diff", 12, "NOT_TEXT"),
        ("diff", b"bytes", "NOT_TEXT"),
        ("prompt", "sk-livekeyvalue", "SECRET"),
        ("tool", "Authorization: Bearer abcdefghijk", "SECRET"),
        ("terminal", "api_key=supersecret", "SECRET"),
        ("prompt", "password = hunter22", "SECRET"),
        ("prompt", "bad\x01text", "BAD_TEXT"),
        ("x" * (TEXT_CAP + 1), "hello", "OVERSIZE"),
    )
    for kind, text, code in kinds:
        with pytest.raises(Refuse) as caught:
            message(kind, text)
        assert refused(caught.value).code == code
    for bad_cap in (True, False, 0, -1, "32000", 1.5):
        with pytest.raises(Refuse) as caught:
            message("prompt", "hello", bad_cap)
        assert refused(caught.value).code == "BAD_LIMIT"
    choices: tuple[tuple[str, str], ...] = (
        ("allow_once", "ALLOW_ONCE"),
        ("allow_session", "ALLOW_SESSION"),
        ("allow_always", "ALLOW_ALWAYS"),
        ("deny", "DENY"),
        ("timeout", "DENY"),
        ("error", "DENY"),
    )
    for choice, code in choices:
        record = decide(choice)
        assert record.code == code
        assert record.runs is False
        assert record.persisted is False
        assert record == decide(choice)
        assert secret_shape(repr(record)) is False
    for bad, code in (
        ("yolo", "BAD_CHOICE"),
        ("off", "BAD_CHOICE"),
        ("", "BAD_CHOICE"),
        (None, "NOT_TEXT"),
        ("sk-abcdefghij", "SECRET"),
    ):
        with pytest.raises(Refuse) as caught:
            decide(bad)
        assert refused(caught.value).code == code
    shown = message("prompt", "hello")
    object.__setattr__(shown, "text", "sk-abcdefghij")
    assert secret_shape(repr(shown)) is False
    object.__setattr__(shown, "text", "Bearer abcdefghijk")
    assert secret_shape(repr(shown)) is False


def test_record_refusals() -> None:
    with pytest.raises(Refuse) as caught:
        DisplayRecord(kind="terminal", text="hello", cap=TEXT_CAP, policy_cap=TEXT_CAP, schema=SCHEMA)
    assert refused(caught.value).code == "BAD_KIND"
    with pytest.raises(Refuse) as caught:
        DisplayRecord(kind="nope", text="hello", cap=TEXT_CAP, policy_cap=TEXT_CAP, schema=SCHEMA)
    assert refused(caught.value).code == "BAD_KIND"
    with pytest.raises(Refuse) as caught:
        TerminalRecord(
            kind="prompt",
            text="hello",
            code=NEED_APPROVAL,
            cap=TEXT_CAP,
            policy_cap=TEXT_CAP,
            schema=SCHEMA,
        )
    assert refused(caught.value).code == "BAD_KIND"
    with pytest.raises(Refuse) as caught:
        TerminalRecord(
            kind="terminal",
            text="hello",
            code="RUN",
            cap=TEXT_CAP,
            policy_cap=TEXT_CAP,
            schema=SCHEMA,
        )
    assert refused(caught.value).code == "BAD_CODE"
    with pytest.raises(Refuse) as caught:
        DisplayRecord(kind="prompt", text="hello", cap=TEXT_CAP, policy_cap=TEXT_CAP, schema="other")
    assert refused(caught.value).code == "BAD_SCHEMA"
    with pytest.raises(Refuse) as caught:
        DisplayRecord(kind="prompt", text="hello", cap=TEXT_CAP + 1, policy_cap=TEXT_CAP, schema=SCHEMA)
    assert refused(caught.value).code == "BAD_LIMIT"
    with pytest.raises(Refuse) as caught:
        DisplayRecord(kind="prompt", text="hello", cap=cast(int, True), policy_cap=TEXT_CAP, schema=SCHEMA)
    assert refused(caught.value).code == "BAD_LIMIT"
    with pytest.raises(Refuse) as caught:
        TerminalRecord(
            kind="terminal",
            text="  ",
            code=NEED_APPROVAL,
            cap=8,
            policy_cap=TEXT_CAP,
            schema=SCHEMA,
        )
    assert refused(caught.value).code == "EMPTY"
    with pytest.raises(Refuse) as caught:
        Approval(schema=SCHEMA, choice="allow_once", code="ALLOW_ONCE", runs=True, persisted=False)
    assert refused(caught.value).code == "NOT_RUN"
    with pytest.raises(Refuse) as caught:
        Approval(schema=SCHEMA, choice="allow_always", code="ALLOW_ALWAYS", runs=False, persisted=True)
    assert refused(caught.value).code == "PERSIST"
    with pytest.raises(Refuse) as caught:
        Approval(schema=SCHEMA, choice="yolo", code="DENY", runs=False, persisted=False)
    assert refused(caught.value).code == "BAD_CHOICE"
    with pytest.raises(Refuse) as caught:
        Reply(
            schema=SCHEMA,
            method="initialize",
            request_id="n:0",
            body='{"id":0,"jsonrpc":"2.0","result":{}}',
            code="OK",
            sent=True,
            cap=TEXT_CAP,
            policy_cap=TEXT_CAP,
        )
    assert refused(caught.value).code == "NOT_SENT"
    with pytest.raises(Refuse) as caught:
        Reply(
            schema=SCHEMA,
            method="nope",
            request_id="n:0",
            body='{"id":0,"jsonrpc":"2.0","result":{}}',
            code="OK",
            sent=False,
            cap=TEXT_CAP,
            policy_cap=TEXT_CAP,
        )
    assert refused(caught.value).code == "BAD_METHOD"
    with pytest.raises(Refuse) as caught:
        Desk(
            schema=SCHEMA,
            initialized=False,
            protocol=0,
            client_name="",
            client_title="",
            client_version="",
            client_protocol=0,
            sessions=(),
            seen=(),
            next_message=1,
            grants=(),
            methods=METHODS,
            cap=TEXT_CAP,
            policy_cap=TEXT_CAP,
        )
    assert refused(caught.value).code == "NO_GRANT"
    with pytest.raises(Refuse) as caught:
        Desk(
            schema=SCHEMA,
            initialized=False,
            protocol=0,
            client_name="",
            client_title="",
            client_version="",
            client_protocol=0,
            sessions=(),
            seen=(),
            next_message=1,
            grants=("notes",),
            methods=METHODS,
            cap=TEXT_CAP,
            policy_cap=TEXT_CAP,
        )
    assert refused(caught.value).code == "RELATIVE_GRANT"
    with pytest.raises(Refuse) as caught:
        Desk(
            schema=SCHEMA,
            initialized=False,
            protocol=4,
            client_name="",
            client_title="",
            client_version="",
            client_protocol=0,
            sessions=(),
            seen=(),
            next_message=1,
            grants=("C:/north-lab",),
            methods=METHODS,
            cap=TEXT_CAP,
            policy_cap=TEXT_CAP,
        )
    assert refused(caught.value).code == "BAD_VERSION"


def test_depth_and_count_caps() -> None:
    with lab() as (jail, root):
        desk = open_desk(jail)
        nested = '{"a":' * (DEPTH_CAP + 4) + "1" + "}" * (DEPTH_CAP + 4)
        raw = '{"jsonrpc":"2.0","id":1,"method":"initialize","params":' + nested + "}"
        with pytest.raises(Refuse) as caught:
            answer(desk, raw, jail)
        assert refused(caught.value).code == "TOO_DEEP"
        wide: dict[str, object] = {}
        number = 0
        while number <= NODE_CAP:
            wide[f"k{number}"] = number
            number += 1
        with pytest.raises(Refuse) as caught:
            answer(desk, frame("initialize", 1, wide), jail)
        assert refused(caught.value).code == "TOO_MANY"
        live = ready(jail)
        current = live
        for count in range(1, SESSION_CAP + 1):
            current = answer(current, frame("session/new", count, {"cwd": root}), jail).desk
        with pytest.raises(Refuse) as caught:
            answer(current, frame("session/new", SESSION_CAP + 1, {"cwd": root}), jail)
        assert refused(caught.value).code == "TOO_MANY"
        prompted = ready(jail)
        opened = answer(prompted, frame("session/new", 1, {"cwd": root}), jail)
        current = opened.desk
        session_id = session_at(current, 0).session_id
        for count in range(MESSAGE_CAP):
            current = answer(
                current,
                frame(
                    "session/prompt",
                    count + 2,
                    {
                        "sessionId": session_id,
                        "prompt": [{"type": "text", "text": f"note {count}"}],
                    },
                ),
                jail,
            ).desk
        with pytest.raises(Refuse) as caught:
            answer(
                current,
                frame(
                    "session/prompt",
                    MESSAGE_CAP + 2,
                    {
                        "sessionId": session_id,
                        "prompt": [{"type": "text", "text": "one more note"}],
                    },
                ),
                jail,
            )
        assert refused(caught.value).code == "TOO_MANY"
        listed = ready(jail)
        current = listed
        next_id = 1
        while len(current.seen) < SEEN_CAP:
            current = answer(current, frame("session/list", next_id, {}), jail).desk
            next_id += 1
        with pytest.raises(Refuse) as caught:
            answer(current, frame("session/list", next_id, {}), jail)
        assert refused(caught.value).code == "TOO_MANY"
