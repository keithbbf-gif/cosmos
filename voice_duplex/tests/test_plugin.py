from __future__ import annotations

import json
from pathlib import Path

from cosmos_voice_duplex.config import VoiceConfig
from cosmos_voice_duplex.plugin.voice_plugin import VoicePlugin
from cosmos_voice_duplex.rails.local_mouth import LocalRail
from cosmos_voice_duplex.session import DuplexSession


class _Host:
    def __init__(self) -> None:
        self.user: list[str] = []
        self.assistant: list[str] = []

    def on_user_text(self, text: str) -> None:
        self.user.append(text)

    def on_assistant_text(self, text: str) -> None:
        self.assistant.append(text)

    def call_tool(self, name: str, arguments: dict[str, object]) -> str:
        return json.dumps({"ok": True, "tool": name})

    def spend_snapshot(self) -> dict[str, object]:
        return {"authority": "host", "audio_ms": 0}


def test_plugin_tools_do_not_import_cosmos_code() -> None:
    text = (
        Path(__file__)
        .resolve()
        .parents[1]
        .joinpath("cosmos_voice_duplex", "plugin", "voice_plugin.py")
        .read_text(encoding="utf-8")
    )
    assert "import cosmos_code" not in text
    assert "cosmos_code" not in text


def test_propose_call_honors_confirm() -> None:
    host = _Host()
    plugin = VoicePlugin(host)
    blocked = json.loads(plugin.registry.call("propose", '{"text": "note"}'))
    assert blocked["ok"] is False
    assert blocked["error"] == "confirm required"
    assert host.user == []
    allowed = json.loads(plugin.registry.call("propose", '{"text": "note"}', confirmed=True))
    assert allowed["ok"] is True
    assert allowed["proposed"] is True
    assert allowed["text"] == "note"
    status = json.loads(plugin.registry.call("status", "{}"))
    assert status["ok"] is True


def test_status_check_and_propose_confirm() -> None:
    host = _Host()
    plugin = VoicePlugin(host)
    assert plugin.registry.tools["propose"].confirm is True
    assert plugin.registry.tools["status"].confirm is False
    status = json.loads(plugin.registry.call("status", "{}"))
    assert status["spend"]["authority"] == "host"
    check = json.loads(plugin.registry.call("check", "{}"))
    assert check["tool"] == "check"
    session = DuplexSession(VoiceConfig(rail="local"), LocalRail())
    plugin.attach(session)
    assert "propose" in session.tools.tools
    assert session.on_user == host.on_user_text
    assert session.on_assistant == host.on_assistant_text
