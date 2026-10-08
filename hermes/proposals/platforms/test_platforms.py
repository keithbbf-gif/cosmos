"""Platform enablement, parse, format cap, and refusal codes. No network."""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Callable, cast

import pytest

from cosmos_hermes import Refuse, secret_shape
from cosmos_hermes.bounds import MAX_TEXT
from platforms import (
    PLATFORM_IDS,
    REQUEST_CAP,
    SAFE_TOOLS,
    SCHEMA,
    TERMINAL_TOOLS,
    TEXT_CAP,
    Enabled,
    Inbound,
    Outbound,
    Platforms,
    ToolNote,
    rebuild,
)

_IDS = (
    "cli",
    "telegram",
    "discord",
    "slack",
    "whatsapp",
    "signal",
    "matrix",
    "mattermost",
    "email",
    "sms",
    "dingtalk",
    "feishu",
    "wecom",
    "weixin",
    "qq",
    "yuanbao",
    "bluebubbles",
    "homeassistant",
    "teams",
    "google_chat",
)


def _code(action: Callable[[], object]) -> str:
    with pytest.raises(Refuse) as caught:
        action()
    return caught.value.code


def _ready() -> Platforms:
    return Platforms().enable("telegram", "id-telegram")


def test_schema_and_ids() -> None:
    assert SCHEMA == "cosmos-hermes-platforms/1"
    assert TEXT_CAP == 4000
    assert PLATFORM_IDS == _IDS
    assert len(PLATFORM_IDS) == 20
    assert len(set(PLATFORM_IDS)) == 20
    import platforms as module

    assert set(module.__all__) == {
        "PLATFORM_IDS",
        "REQUEST_CAP",
        "SAFE_TOOLS",
        "SCHEMA",
        "TERMINAL_TOOLS",
        "TEXT_CAP",
        "Enabled",
        "Inbound",
        "Outbound",
        "Platforms",
        "ToolNote",
        "rebuild",
    }
    assert frozenset(SAFE_TOOLS).isdisjoint(TERMINAL_TOOLS)
    assert "terminal" in TERMINAL_TOOLS
    assert "hermes-telegram" in TERMINAL_TOOLS
    assert "cli" in PLATFORM_IDS
    assert REQUEST_CAP >= TEXT_CAP


def test_success_path_and_independence() -> None:
    base = Platforms()
    assert base.enabled == ()
    desk = base
    for name in PLATFORM_IDS:
        desk = desk.enable(name, "id-" + name)
    assert base.enabled == ()
    assert len(desk.enabled) == 20
    again = Platforms()
    for name in PLATFORM_IDS:
        again = again.enable(name, "id-" + name)
    assert desk == again
    for name in PLATFORM_IDS:
        inbound = desk.parse(name, "ping " + name)
        assert inbound == Inbound(name, "ping " + name)
        outbound = desk.format_out(name, "pong " + name)
        assert outbound.text == "pong " + name
        assert outbound.cap == TEXT_CAP
        assert outbound.requested == TEXT_CAP
        assert outbound.truncated is False
    rotated = desk.enable("qq", "id-qq-next")
    assert len(rotated.enabled) == 20
    assert rotated.enabled[PLATFORM_IDS.index("qq")].secret_id == "id-qq-next"
    assert desk.parse("qq", "still").text == "still"
    with pytest.raises(Refuse) as caught:
        base.parse("email", "hi")
    assert caught.value.code == "DISABLED"


def test_disabled_before_text_and_unknown() -> None:
    desk = Platforms()
    assert _code(lambda: desk.parse("discord", "")) == "DISABLED"
    assert _code(lambda: desk.parse("discord", "sk-" + "abcdefgh")) == "DISABLED"
    assert _code(lambda: desk.format_out("discord", "\n")) == "DISABLED"
    assert _code(lambda: desk.enable("line", "id-line")) == "UNKNOWN_PLATFORM"
    assert _code(lambda: desk.parse("Telegram", "hi")) == "UNKNOWN_PLATFORM"
    assert _code(lambda: desk.format_out("google-chat", "hi")) == "UNKNOWN_PLATFORM"
    assert _code(lambda: desk.enable("", "id-cli")) == "UNKNOWN_PLATFORM"
    with pytest.raises(Refuse) as caught:
        desk.enable("sk-" + "abcdefghij", "id-ok")
    assert caught.value.code == "UNKNOWN_PLATFORM"
    assert "sk-" not in str(caught.value)


@pytest.mark.parametrize("secret_id", ["", " ", "\t", "\n"])
def test_empty_secret(secret_id: str) -> None:
    assert _code(lambda: Platforms().enable("cli", secret_id)) == "NO_SECRET"


@pytest.mark.parametrize(
    "secret_id",
    [
        "sk-" + "abcdEF12",
        "Bearer abcdefgh",
        "api_key=abcd",
        "password = hunter2xx",
        "token:abcdefgh",
    ],
)
def test_secret_id_and_message(secret_id: str) -> None:
    assert secret_shape(secret_id)
    with pytest.raises(Refuse) as caught:
        Platforms().enable("slack", secret_id)
    assert caught.value.code == "SECRET"
    assert not secret_shape(str(caught.value))
    desk = _ready()
    assert _code(lambda: desk.parse("telegram", secret_id)) == "SECRET"
    assert _code(lambda: desk.format_out("telegram", secret_id)) == "SECRET"
    hidden = "hello " + ("z" * 5000) + " " + secret_id
    assert _code(lambda: desk.format_out("telegram", hidden, cap=10)) == "SECRET"


def test_empty_text_and_bad_id() -> None:
    desk = _ready()
    assert _code(lambda: desk.parse("telegram", "")) == "EMPTY"
    assert _code(lambda: desk.parse("telegram", "  \n")) == "EMPTY"
    assert _code(lambda: desk.format_out("telegram", "\t")) == "EMPTY"
    assert _code(lambda: Inbound("telegram", " ")) == "EMPTY"
    assert _code(lambda: Platforms().enable("signal", "bad id")) == "BAD_ID"
    assert _code(lambda: Platforms().enable("signal", ".hidden")) == "BAD_ID"
    assert _code(lambda: Platforms().enable("signal", "a/b")) == "BAD_ID"
    assert Platforms().enable("signal", "a" * 128).enabled[0].secret_id == "a" * 128


def test_format_cap() -> None:
    desk = _ready()
    long = "m" * 4500
    outbound = desk.format_out("telegram", long, cap=8000)
    assert outbound.cap == TEXT_CAP
    assert outbound.requested == 8000
    assert outbound.truncated is True
    assert outbound.text == long[:TEXT_CAP]
    assert len(outbound.text) == TEXT_CAP
    exact = desk.format_out("telegram", "z" * TEXT_CAP)
    assert exact.truncated is False
    assert exact.cap == TEXT_CAP
    assert len(exact.text) == TEXT_CAP
    tight = desk.format_out("telegram", "abcdefghij", cap=4)
    assert tight.text == "abcd"
    assert tight.cap == 4
    assert tight.requested == 4
    assert tight.truncated is True
    inbound = desk.parse("telegram", "b" * 5000)
    assert inbound.text == "b" * 5000
    assert _code(lambda: desk.format_out("telegram", "hi", cap=True)) == "BAD_CAP"
    assert _code(lambda: desk.format_out("telegram", "hi", cap=0)) == "BAD_CAP"
    assert _code(lambda: desk.format_out("telegram", "hi", cap=-3)) == "BAD_CAP"
    assert _code(lambda: desk.format_out("telegram", "hi", cap="10")) == "BAD_CAP"
    assert _code(lambda: desk.format_out("telegram", "hi", cap=1.5)) == "BAD_CAP"
    assert _code(lambda: desk.format_out("telegram", "hi", cap=REQUEST_CAP + 1)) == "BAD_CAP"
    assert _code(lambda: Outbound("telegram", "hi", TEXT_CAP, REQUEST_CAP + 1, False)) == "BAD_CAP"
    recorded = desk.format_out("telegram", "hi", cap=REQUEST_CAP)
    assert recorded.cap == TEXT_CAP
    assert recorded.requested == REQUEST_CAP
    blank_prefix = desk.send("telegram", "   hello harbor", cap=2)
    assert blank_prefix.text == "  "
    assert blank_prefix.truncated is True
    assert blank_prefix == desk.format_out("telegram", "   hello harbor", cap=2)
    assert _code(lambda: Outbound("telegram", "hi", 9000, 9000, False)) == "BAD_CAP"
    assert _code(lambda: Outbound("telegram", "hi", TEXT_CAP, TEXT_CAP, True)) == "BAD_RECORD"
    assert _code(lambda: Outbound("telegram", "hello", 2, 2, True)) == "BAD_RECORD"


def test_bound_and_record_refusals() -> None:
    desk = _ready()
    assert _code(lambda: Platforms().enable("telegram", None)) == "NOT_TEXT"
    assert _code(lambda: Platforms().enable(None, "id-cli")) == "NOT_TEXT"
    assert _code(lambda: desk.parse("telegram", None)) == "NOT_TEXT"
    assert _code(lambda: desk.format_out("telegram", b"hi")) == "NOT_TEXT"
    assert _code(lambda: desk.parse("telegram", "a\x00b")) == "NULL_BYTE"
    assert _code(lambda: Platforms().enable("cli\x00", "id-cli")) == "NULL_BYTE"
    assert _code(lambda: Platforms().enable("sms", "a" * 129)) == "OVERSIZE"
    assert _code(lambda: desk.parse("telegram", "m" * (MAX_TEXT + 1))) == "OVERSIZE"
    assert _code(lambda: Platforms().enable("p" * 65, "id-ok")) == "OVERSIZE"
    assert _code(lambda: Platforms().enable("p" * 64, "id-ok")) == "UNKNOWN_PLATFORM"
    row = Enabled("teams", "id-teams")
    other = Enabled("teams", "id-teams-2")
    assert _code(lambda: Platforms(enabled=(row, other))) == "DUPLICATE"
    assert _code(lambda: Platforms(enabled=cast(tuple[Enabled, ...], (row, "x")))) == "BAD_RECORD"
    assert _code(lambda: Platforms(enabled=cast(tuple[Enabled, ...], [row]))) == "BAD_RECORD"


def test_repr_stays_free_of_key_shapes() -> None:
    desk = Platforms().enable("weixin", "id-weixin")
    inbound = desk.parse("weixin", "hello weixin")
    outbound = desk.format_out("weixin", "hello weixin", cap=TEXT_CAP + 5)
    blob = repr((desk, inbound, outbound, desk.enabled[0]))
    assert outbound.cap == TEXT_CAP
    assert outbound.requested == TEXT_CAP + 5
    assert secret_shape(blob) is False
    assert "sk-" not in blob
    assert "Bearer" not in blob
    assert "api_key=" not in blob


_RAW_BOT = "123456789:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw"


def _terminal_code(desk: Platforms, platform_id: str, tool: str) -> str:
    return _code(lambda: desk.request_tool(platform_id, tool))


def _parse_code(desk: Platforms, text: str) -> str:
    return _code(lambda: desk.parse("telegram", text))


def _send_code(desk: Platforms, text: str) -> str:
    return _code(lambda: desk.send("telegram", text, cap=10))


def test_messaging_terminal_and_raw_bot_tokens() -> None:
    idle = Platforms()
    assert _terminal_code(idle, "telegram", "terminal") == "DISABLED"
    assert _code(lambda: idle.send("telegram", _RAW_BOT)) == "DISABLED"
    assert idle.enabled == ()
    for name in PLATFORM_IDS:
        desk = Platforms().enable(name, "cred-" + name)
        sent = desk.send(name, "note for " + name)
        assert sent.text == "note for " + name
        assert sent.truncated is False
        if name == "cli":
            note = desk.request_tool(name, "terminal")
            assert note == ToolNote("cli", "terminal", False)
            assert note.runs is False
        else:
            assert _terminal_code(desk, name, "terminal") == "MESSAGING_TERMINAL"
            assert _terminal_code(desk, name, "hermes-telegram") == "MESSAGING_TERMINAL"
            assert desk == Platforms().enable(name, "cred-" + name)
    harbor = _ready()
    for tool in TERMINAL_TOOLS:
        assert _terminal_code(harbor, "telegram", tool) == "MESSAGING_TERMINAL"
    for tool in SAFE_TOOLS:
        assert harbor.request_tool("telegram", tool) == ToolNote("telegram", tool, False)
    cli = Platforms().enable("cli", "cred-cli")
    for tool in TERMINAL_TOOLS:
        assert cli.request_tool("cli", tool) == ToolNote("cli", tool, False)
    assert _terminal_code(harbor, "telegram", "all") == "UNKNOWN_TOOL"
    assert _code(lambda: harbor.request_tool("telegram", "*")) == "BAD_NAME"
    assert _code(lambda: harbor.request_tool("telegram", "Terminal")) == "BAD_NAME"
    assert _code(lambda: harbor.request_tool("telegram", "")) == "BAD_NAME"
    assert _code(lambda: harbor.request_tool("telegram", "a/b")) == "BAD_NAME"
    assert _code(lambda: harbor.request_tool("telegram", None)) == "NOT_TEXT"
    assert _code(lambda: harbor.request_tool("telegram", ["terminal"])) == "NOT_TEXT"
    assert _code(lambda: harbor.request_tool("telegram", "a\x00b")) == "NULL_BYTE"
    assert _code(lambda: harbor.request_tool("telegram", "t" * 65)) == "OVERSIZE"
    assert _code(lambda: harbor.request_tool("telegram", "sk-" + "abcdefgh")) == "SECRET"
    assert _code(lambda: ToolNote("telegram", "terminal", False)) == "MESSAGING_TERMINAL"
    assert _code(lambda: ToolNote("telegram", "vision", True)) == "BAD_RECORD"
    assert _code(lambda: ToolNote("cli", "terminal", True)) == "BAD_RECORD"
    assert _code(lambda: ToolNote("cli", "nope", False)) == "UNKNOWN_TOOL"
    tokens = (
        _RAW_BOT,
        ("xox" + "b-fixture-not-a-token"),
        "Bot " + ("A" * 24),
        "bot_token=not-a-real-bot-secret",
        "TELEGRAM_BOT_TOKEN=" + _RAW_BOT,
    )
    for token in tokens:
        held = Platforms()
        with pytest.raises(Refuse) as caught:
            held.enable("telegram", token)
        assert caught.value.code == "SECRET"
        assert token not in str(caught.value)
        assert secret_shape(str(caught.value)) is False
        assert held.enabled == ()
        assert _parse_code(harbor, token) == "SECRET"
        hidden = "hello " + ("z" * 5000) + " " + token
        assert _send_code(harbor, hidden) == "SECRET"


def test_rebuild_matches_enabled_rows() -> None:
    desk = Platforms().enable("telegram", "cred-tg").enable("slack", "cred-slack")
    copy = rebuild(desk.enabled)
    assert copy == desk
    assert copy is not desk
    assert rebuild(()) == Platforms()
    assert _code(lambda: rebuild(list(desk.enabled))) == "BAD_RECORD"
    assert _code(lambda: rebuild(desk.enabled + desk.enabled)) == "DUPLICATE"


def test_example_platforms() -> None:
    def once() -> tuple[object, ...]:
        idle = Platforms()
        desk = idle.enable("telegram", "cred-tg")
        sent = desk.send("telegram", "Mira, slip 4 is clear for the evening note.")
        photo = desk.request_tool("telegram", "vision")
        terminal = _terminal_code(desk, "telegram", "terminal")
        preset = _terminal_code(desk, "telegram", "hermes-telegram")
        refused = _code(lambda: idle.enable("telegram", _RAW_BOT))
        copy = rebuild(desk.enabled)
        return (idle.enabled, desk, sent, photo, terminal, preset, refused, copy, copy == desk)

    first = once()
    second = once()
    assert first == second
    assert first[0] == ()
    sent = first[2]
    assert isinstance(sent, Outbound)
    assert sent.platform_id == "telegram"
    assert sent.text == "Mira, slip 4 is clear for the evening note."
    assert sent.cap == TEXT_CAP
    assert sent.requested == TEXT_CAP
    assert sent.truncated is False
    photo = first[3]
    assert isinstance(photo, ToolNote)
    assert photo == ToolNote("telegram", "vision", False)
    assert photo.runs is False
    assert first[4] == "MESSAGING_TERMINAL"
    assert first[5] == "MESSAGING_TERMINAL"
    assert first[6] == "SECRET"
    assert first[8] is True
    blob = repr(first[1]) + repr(sent) + repr(photo)
    assert _RAW_BOT not in blob
    assert secret_shape(blob) is False


def test_source_has_no_network() -> None:
    source = Path(__file__).with_name("platforms.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    modules: set[str] = set()
    names: set[str] = set()
    attrs: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.add(alias.name.split(".", 1)[0])
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            modules.add(node.module.split(".", 1)[0])
        elif isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name):
                names.add(func.id)
            elif isinstance(func, ast.Attribute):
                attrs.add(func.attr)
    assert modules.isdisjoint(
        {
            "subprocess",
            "threading",
            "asyncio",
            "socket",
            "urllib",
            "requests",
            "pickle",
            "http",
            "multiprocessing",
            "ctypes",
            "sched",
            "time",
        }
    )
    assert names.isdisjoint({"sleep", "exec", "eval", "compile", "system"})
    assert attrs.isdisjoint({"sleep", "Popen", "urlopen", "create_connection"})
