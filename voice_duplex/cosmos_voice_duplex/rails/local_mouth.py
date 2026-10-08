"""Credit-out rail. The mic still turns. Nobody presses Send.

There is no neural voice here. Captions say so. A short tone marks the end
of the turn so the speaker path is exercised, and the utterance bytes are
kept on the event for a later DOM or local model. This is the path that
still runs when ``XAI_API_KEY`` is missing or the spend hook denies the
cloud rails.
"""

from __future__ import annotations

from cosmos_voice_duplex.config import VoiceConfig
from cosmos_voice_duplex.pcm import tone
from cosmos_voice_duplex.rails.base import RailEvent
from cosmos_voice_duplex.vad import EnergyVad


class LocalRail:
    name = "local"

    def __init__(self) -> None:
        self._vad: EnergyVad | None = None
        self._cfg: VoiceConfig | None = None
        self.utterances: list[bytes] = []

    def open(self, cfg: VoiceConfig) -> list[RailEvent]:
        self._cfg = cfg
        self._vad = EnergyVad(
            sample_rate=cfg.sample_rate,
            threshold=cfg.local_rms,
            silence_ms=cfg.silence_ms,
            prefix_ms=cfg.prefix_padding_ms,
        )
        return [RailEvent("ready", text="local")]

    def push_audio(self, pcm: bytes) -> list[RailEvent]:
        if self._vad is None or self._cfg is None:
            return []
        events: list[RailEvent] = []
        for vad_event in self._vad.push(pcm):
            if vad_event.kind == "start":
                events.append(RailEvent("speech_started"))
            elif vad_event.kind == "end":
                self.utterances.append(vad_event.utterance)
                events.append(RailEvent("speech_stopped"))
                events.append(
                    RailEvent(
                        "user_transcript",
                        text="(local capture, no cloud transcript)",
                        pcm=vad_event.utterance,
                        final=True,
                    )
                )
                note = "Grok voice is not connected. I kept what you said on this machine."
                events.append(RailEvent("assistant_transcript", text=note, final=True))
                beep = tone(self._cfg.sample_rate // 5, self._cfg.sample_rate)
                events.append(RailEvent("audio", pcm=beep))
                events.append(RailEvent("response_done"))
        return events

    def poll(self) -> list[RailEvent]:
        return []

    def barge(self, item_id: str, played_ms: int) -> list[RailEvent]:
        return [RailEvent("barge", text=str(played_ms))]

    def submit_tool_result(self, call_id: str, output: str) -> list[RailEvent]:
        return [RailEvent("assistant_transcript", text=output, final=True)]

    def continue_after_playback(self) -> list[RailEvent]:
        return []

    def force_say(self, text: str) -> list[RailEvent]:
        cfg = self._cfg
        rate = cfg.sample_rate if cfg else 24000
        return [
            RailEvent("assistant_transcript", text=text, final=True),
            RailEvent("audio", pcm=tone(rate // 10, rate, freq=660.0)),
        ]

    def close(self) -> None:
        self._vad = None
