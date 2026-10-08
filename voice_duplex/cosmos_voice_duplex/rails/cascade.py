"""Cascade rail: local end-of-turn, then STT, then a text brain, then TTS.

Still full duplex at the microphone. Barge-in drops the TTS that has not
played. This is the path when speech-to-speech is down and a key remains.
Endpoints, verified 2026-10-01:

* ``POST https://api.x.ai/v1/stt`` model ``grok-voice-transcribe-2.0``
* ``POST https://api.x.ai/v1/tts`` voice id, language, PCM 24 kHz

The HTTP functions take an opener so tests never touch the network.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Protocol
from urllib.request import Request

from cosmos_voice_duplex.config import VoiceConfig, trim_spoken
from cosmos_voice_duplex.pcm import to_wav
from cosmos_voice_duplex.rails.base import RailEvent
from cosmos_voice_duplex.vad import EnergyVad


class _HttpBody(Protocol):
    def read(self) -> bytes: ...

    def __enter__(self) -> _HttpBody: ...

    def __exit__(self, *args: object) -> None: ...


Transcriber = Callable[[bytes, int], str]
Asker = Callable[[str], str]
Synthesizer = Callable[[str], bytes]
Opener = Callable[[Request, float], _HttpBody]


def stt_request(cfg: VoiceConfig, wav: bytes, api_key: str) -> Request:
    boundary = "cosmos-voice-boundary"
    model = "grok-voice-transcribe-2.0"
    disp = f"--{boundary}\r\nContent-Disposition: form-data; name=\""
    parts = [
        f"{disp}model\"\r\n\r\n{model}\r\n".encode(),
        f"{disp}language\"\r\n\r\n{cfg.language}\r\n".encode(),
        (
            f"{disp}file\"; filename=\"turn.wav\"\r\nContent-Type: audio/wav\r\n\r\n"
        ).encode()
        + wav
        + f"\r\n--{boundary}--\r\n".encode(),
    ]
    body = b"".join(parts)
    return Request(
        cfg.base_url.rstrip("/") + "/stt",
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        },
        method="POST",
    )


def tts_request(cfg: VoiceConfig, text: str, api_key: str) -> Request:
    payload = {
        "text": text,
        "voice_id": cfg.voice,
        "language": cfg.language or "en",
        "speed": cfg.speed,
        "output_format": {"codec": "pcm", "sample_rate": cfg.sample_rate},
    }
    return Request(
        cfg.base_url.rstrip("/") + "/tts",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )


def parse_stt(body: bytes) -> str:
    data = json.loads(body.decode("utf-8"))
    if not isinstance(data, dict):
        return ""
    return str(data.get("text") or "")


class CascadeRail:
    name = "cascade"

    def __init__(
        self,
        transcribe: Transcriber | None = None,
        ask: Asker | None = None,
        synthesize: Synthesizer | None = None,
    ) -> None:
        self.transcribe = transcribe
        self.ask = ask
        self.synthesize = synthesize
        self._vad: EnergyVad | None = None
        self._cfg: VoiceConfig | None = None
        self._cancelled = False

    def open(self, cfg: VoiceConfig) -> list[RailEvent]:
        self._cfg = cfg
        self._vad = EnergyVad(
            sample_rate=cfg.sample_rate,
            threshold=cfg.local_rms,
            silence_ms=cfg.silence_ms,
            prefix_ms=cfg.prefix_padding_ms,
        )
        return [RailEvent("ready", text="cascade")]

    def push_audio(self, pcm: bytes) -> list[RailEvent]:
        if self._vad is None or self._cfg is None:
            return []
        events: list[RailEvent] = []
        for vad_event in self._vad.push(pcm):
            if vad_event.kind == "start":
                events.append(RailEvent("speech_started"))
            elif vad_event.kind == "end":
                events.append(RailEvent("speech_stopped"))
                events.extend(self._turn(vad_event.utterance))
        return events

    def _turn(self, utterance: bytes) -> list[RailEvent]:
        cfg = self._cfg
        if cfg is None or self.transcribe is None or self.ask is None:
            return [RailEvent("error", text="cascade is missing transcribe or ask")]
        self._cancelled = False
        text = self.transcribe(utterance, cfg.sample_rate).strip()
        if not text:
            return [RailEvent("user_transcript", text="", final=True)]
        out = [RailEvent("user_transcript", text=text, final=True), RailEvent("response_created")]
        reply = trim_spoken(self.ask(text))
        if self._cancelled:
            return out + [RailEvent("response_done", text="cancelled")]
        out.append(RailEvent("assistant_transcript", text=reply, final=True))
        if self.synthesize is not None and reply:
            pcm = self.synthesize(reply)
            if pcm and not self._cancelled:
                out.append(RailEvent("audio", pcm=pcm))
        out.append(RailEvent("response_done"))
        return out

    def poll(self) -> list[RailEvent]:
        return []

    def barge(self, item_id: str, played_ms: int) -> list[RailEvent]:
        self._cancelled = True
        return [RailEvent("barge", item_id=item_id, text=str(played_ms))]

    def submit_tool_result(self, call_id: str, output: str) -> list[RailEvent]:
        return []

    def continue_after_playback(self) -> list[RailEvent]:
        return []

    def force_say(self, text: str) -> list[RailEvent]:
        events = [RailEvent("assistant_transcript", text=text, final=True)]
        if self.synthesize is not None:
            pcm = self.synthesize(text)
            if pcm:
                events.append(RailEvent("audio", pcm=pcm))
        return events

    def close(self) -> None:
        self._vad = None


def http_transcribe(cfg: VoiceConfig, api_key: str, opener: Opener) -> Transcriber:
    def _run(pcm: bytes, rate: int) -> str:
        req = stt_request(cfg, to_wav(pcm, rate), api_key)
        with opener(req, 30.0) as resp:
            body = resp.read()
        return parse_stt(body)

    return _run


def http_synthesize(cfg: VoiceConfig, api_key: str, opener: Opener) -> Synthesizer:
    def _run(text: str) -> bytes:
        req = tts_request(cfg, text, api_key)
        with opener(req, 30.0) as resp:
            return resp.read()

    return _run
