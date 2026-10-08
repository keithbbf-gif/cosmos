"""Plugin record and the four tools. The bearer stays on the client, not the table."""

from __future__ import annotations

import inspect
from collections.abc import Callable
from typing import cast

import cosmos_voice.plugin as plugin
from cosmos_voice.plugin import manifest, register
from cosmos_voice.session import VoiceSession
from cosmos_voice.transport import CoreClient, MemoryTransport


def _call(tool: object, *args: object) -> dict[str, object]:
    """Call a registered tool and copy the result into a plain dict."""

    assert callable(tool)
    fn = cast(Callable[..., object], tool)
    raw = fn(*args)
    assert isinstance(raw, dict)
    out: dict[str, object] = {}
    for key, value in raw.items():
        out[str(key)] = value
    return out


def test_manifest_writes_live_tree_false() -> None:
    """The plugin record is the architecture record and does not write the live tree."""

    record = manifest()
    assert record["writes_live_tree"] is False
    assert record["id"] == "cosmos-voice"
    assert record["plugin_of"] == "cosmos-code"
    assert record["authority"] == "core-http-client"
    assert record["anthropic"] == "off"
    layers = record["layers"]
    assert layers == {
        "l1_role": "file",
        "l2_model": "none",
        "l3_harness": "native",
        "l4_wrapper": "file",
        "l5_skills": "none",
        "l6_tools": "native",
        "l7_enviro": "file",
        "l8_mission": "file",
    }
    assert record["tools"] == ["voice.say", "voice.status", "voice.kill", "voice.queue"]


def test_register_hides_bearer_and_spies_headers() -> None:
    """The table does not contain the bearer. The transport still sees the header."""

    bearer = "test-bearer-value"
    reply: dict[str, object] = {"spoken": "said", "needs_confirm": False}
    status: dict[str, object] = {"ok": True}
    killed: dict[str, object] = {"killed": True}
    transport = MemoryTransport(
        [
            ("POST", "/api/v1/voice", 200, reply),
            ("GET", "/api/v1/status", 200, status),
            ("POST", "/api/v1/kill", 200, killed),
        ]
    )
    client = CoreClient("https://core.example", bearer, transport=transport)
    session = VoiceSession(client_id="handset")
    table: dict[str, object] = {"kept": "yes"}
    same = register(table, client=client, session=session)
    assert same is table
    leaked = bearer in repr(table)
    assert not leaked
    for name in ("voice.say", "voice.status", "voice.kill", "voice.queue"):
        tool = table[name]
        assert callable(tool)
        text = inspect.getsource(tool)
        leaked_source = bearer in text
        assert not leaked_source
    said = _call(table["voice.say"], "ping")
    assert said.get("spoken") == "said"
    state = _call(table["voice.status"])
    assert state.get("ok") is True
    done = _call(table["voice.kill"], "handset")
    assert done.get("killed") is True
    waiting = _call(table["voice.queue"])
    assert waiting == {"pending": []}
    saw_header = False
    for _method, _url, headers, _body, _timeout in transport.calls:
        auth = headers.get("Authorization", "")
        if auth == "Bearer " + bearer:
            saw_header = True
        leaked_table = bearer in repr(table)
        assert not leaked_table
    assert saw_header is True
    assert table["kept"] == "yes"


def test_register_queue_lists_pending() -> None:
    """A queue object supplies pending rows. None stays an empty list."""

    transport = MemoryTransport([])
    client = CoreClient("https://core.example", "", transport=transport)
    session = VoiceSession(client_id="handset")

    class _Road:
        def list_pending(self) -> list[object]:
            return [{"id": "row-1"}]

    filled = register({}, client=client, session=session, queue=_Road())
    pending = _call(filled["voice.queue"])
    assert pending == {"pending": [{"id": "row-1"}]}
    empty = register({}, client=client, session=session, queue=None)
    assert _call(empty["voice.queue"]) == {"pending": []}


def test_plugin_does_not_read_environment() -> None:
    """Tool registration does not touch the process environment."""

    source = inspect.getsource(plugin)
    assert "os.environ" not in source
    assert "getenv" not in source


def test_register_say_uses_core_mouth() -> None:
    """voice.say posts /api/v1/voice through CoreMouth."""

    reply: dict[str, object] = {"spoken": "from-core"}
    transport = MemoryTransport([("POST", "/api/v1/voice", 200, reply)])
    client = CoreClient("https://core.example", "", transport=transport)
    table = register({}, client=client, session=VoiceSession(client_id="handset"))
    result = _call(table["voice.say"], "turn")
    assert result.get("spoken") == "from-core"
    posted = False
    for method, url, _headers, _body, _timeout in transport.calls:
        if method == "POST" and "/api/v1/voice" in url:
            posted = True
    assert posted is True
