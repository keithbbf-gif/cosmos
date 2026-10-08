"""Events a rail emits. The session applies them. Rails do not touch the speaker."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from cosmos_voice_duplex.config import VoiceConfig


@dataclass
class RailEvent:
    kind: str
    pcm: bytes = b""
    text: str = ""
    name: str = ""
    arguments: str = ""
    call_id: str = ""
    item_id: str = ""
    response_id: str = ""
    final: bool = False
    extra: dict[str, object] = field(default_factory=dict)


class Rail(Protocol):
    name: str

    def open(self, cfg: VoiceConfig) -> list[RailEvent]: ...

    def push_audio(self, pcm: bytes) -> list[RailEvent]: ...

    def poll(self) -> list[RailEvent]: ...

    def barge(self, item_id: str, played_ms: int) -> list[RailEvent]: ...

    def submit_tool_result(self, call_id: str, output: str) -> list[RailEvent]: ...

    def continue_after_playback(self) -> list[RailEvent]: ...

    def force_say(self, text: str) -> list[RailEvent]: ...

    def close(self) -> None: ...
