from __future__ import annotations

import base64
import json

from cosmos_voice_duplex.config import VoiceConfig
from cosmos_voice_duplex.rails.base import RailEvent
from cosmos_voice_duplex.rails.xai_realtime import MemoryTransport, XaiRealtimeRail
from cosmos_voice_duplex.session import DuplexSession
from cosmos_voice_duplex.spend import CeilingSpend
from cosmos_voice_duplex.tools import Tool, ToolRegistry

from tests.support import loud, silence


class _Script:
    name = "script"

    def __init__(self) -> None:
        self.events: list[RailEvent] = []
        self.pushed: list[bytes] = []
        self.said: list[str] = []
        self.barges: list[tuple[str, int]] = []
        self.tools: list[tuple[str, str]] = []
        self.continued = 0

    def open(self, cfg: VoiceConfig) -> list[RailEvent]:
        del cfg
        return [RailEvent("ready", text="script")]

    def push_audio(self, pcm: bytes) -> list[RailEvent]:
        self.pushed.append(pcm)
        batch = list(self.events)
        self.events.clear()
        return batch

    def poll(self) -> list[RailEvent]:
        return []

    def barge(self, item_id: str, played_ms: int) -> list[RailEvent]:
        self.barges.append((item_id, played_ms))
        return [RailEvent("barge", item_id=item_id, text=str(played_ms))]

    def submit_tool_result(self, call_id: str, output: str) -> list[RailEvent]:
        self.tools.append((call_id, output))
        return []

    def continue_after_playback(self) -> list[RailEvent]:
        self.continued += 1
        return []

    def force_say(self, text: str) -> list[RailEvent]:
        self.said.append(text)
        return [RailEvent("assistant_transcript", text=text, final=True)]

    def close(self) -> None:
        return None


def test_ceiling_denies_cloud_and_allows_local() -> None:
    rail = XaiRealtimeRail(MemoryTransport())
    session = DuplexSession(VoiceConfig(rail="xai"), rail, spend=CeilingSpend(1.0, used_usd=1.0))
    assert session.open() is False
    assert session.last_error == "ceiling"
    local = _Script()
    local.name = "local"
    allowed = DuplexSession(VoiceConfig(rail="local"), local, spend=CeilingSpend(1.0, used_usd=5.0))
    assert allowed.open() is True


def test_barge_flushes_playback_and_keeps_the_mic_frame() -> None:
    transport = MemoryTransport()
    rail = XaiRealtimeRail(transport)
    session = DuplexSession(VoiceConfig(rail="xai"), rail)
    assert session.open()
    pcm = b"\x10\x00" * 400
    transport.inbox.append({"type": "response.created", "response": {"id": "resp_1"}})
    transport.inbox.append(
        {
            "type": "response.output_audio.delta",
            "delta": base64.b64encode(pcm).decode("ascii"),
            "item_id": "item-9",
        }
    )
    session.feed(silence(20))
    assert session.state == "assistant_speaking"
    assert session.play.pending
    session.pull(480)
    played = session.play.played_ms()
    assert played > 0
    transport.sent.clear()
    session.feed(loud(100))
    assert session.barge_count == 1
    assert session.play.pending is False
    kinds = [message["type"] for message in transport.sent]
    assert kinds[0] == "response.cancel"
    assert "conversation.item.truncate" in kinds
    assert "input_audio_buffer.clear" not in kinds
    truncate = next(
        item for item in transport.sent if item["type"] == "conversation.item.truncate"
    )
    assert truncate["audio_end_ms"] == played
    appended = next(
        item for item in transport.sent if item["type"] == "input_audio_buffer.append"
    )
    assert base64.b64decode(str(appended["audio"])) == loud(100)


def test_consequential_line_is_held_until_yes() -> None:
    class _Voice:
        def handle(
            self,
            session_id: str,
            transcript: str,
            mode: str = "voice",
            confirm_id: str | None = None,
        ) -> dict[str, object]:
            del session_id, mode
            if confirm_id is None:
                return {"confirm_id": "n1", "spoken": "Say yes to submit."}
            assert transcript == "submit the job"
            assert confirm_id == "n1"
            return {"spoken": "Submitted."}

    rail = _Script()
    session = DuplexSession(VoiceConfig(), rail, voice=_Voice())
    assert session.open()
    rail.events.append(RailEvent("user_transcript", text="submit the job", final=True))
    session.feed(silence(20))
    assert rail.said == ["Say yes to submit."]
    rail.events.append(RailEvent("user_transcript", text="yes", final=True))
    session.feed(silence(20))
    assert rail.said[-1] == "Submitted."


def test_destructive_transcript_is_refused() -> None:
    rail = _Script()
    session = DuplexSession(VoiceConfig(), rail)
    session.open()
    rail.events.append(RailEvent("user_transcript", text="delete the ledger", final=True))
    session.feed(silence(20))
    assert rail.said
    assert "refused" in rail.said[-1].lower()


def test_confirmed_tool_waits_for_playback() -> None:
    def _propose(arguments: dict[str, object]) -> str:
        return json.dumps({"ok": True, "text": arguments.get("text")})

    registry = ToolRegistry()
    registry.add(Tool("propose", "hold a change", {"type": "object"}, _propose, confirm=True))
    rail = _Script()
    session = DuplexSession(VoiceConfig(), rail, tools=registry)
    session.open()
    rail.events.append(
        RailEvent("tool_call", name="propose", arguments='{"text": "note"}', call_id="c1")
    )
    session.feed(silence(20))
    assert rail.tools == []
    assert "propose" in rail.said[-1]
    rail.events.append(RailEvent("user_transcript", text="yes", final=True))
    session.feed(silence(20))
    assert rail.tools == [("c1", json.dumps({"ok": True, "text": "note"}))]
    assert rail.continued == 0
    session.turn.on("response_created")
    session.turn.on("audio_delta")
    assert session.state == "assistant_speaking"
    session.pull()
    assert rail.continued == 1


def test_half_duplex_sends_silence_while_the_assistant_speaks() -> None:
    rail = _Script()
    session = DuplexSession(VoiceConfig(half_duplex=True), rail)
    session.open()
    session.turn.on("response_created")
    session.turn.on("audio_delta")
    assert session.state == "assistant_speaking"
    session.feed(loud(20))
    assert rail.pushed[-1] == silence(20)
    assert session.barge_count == 0
