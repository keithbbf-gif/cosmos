"""xAI speech-to-speech codec and rail.

Wire facts, from docs.x.ai on 2026-10-01:

* ``wss://api.x.ai/v1/realtime?model=grok-voice-think-fast-2.0``
* Auth: ``Authorization: Bearer`` on the server. Browsers and phones use an
  ephemeral token from ``POST /v1/realtime/client_secrets`` as subprotocol
  ``xai-client-secret.<token>``. The long-lived key never leaves the PC.
* ``turn_detection.type = server_vad`` commits turns. The client does not
  send ``input_audio_buffer.commit`` and does not press Send.
* Barge-in in VAD mode is automatic on the server. The client still stops
  playback locally, sends ``response.cancel``, and
  ``conversation.item.truncate`` with the milliseconds actually played.
* Audio default is PCM16 little-endian, 24 kHz, mono, base64 in JSON.

The rail is tested with an in-memory transport. Nothing here opens a socket
unless ``connect`` is called, and ``connect`` is not used by the unit tests.
"""

from __future__ import annotations

import base64
import json
import os
from dataclasses import dataclass, field
from typing import Protocol
from urllib.request import Request

from cosmos_voice_duplex.config import VoiceConfig
from cosmos_voice_duplex.rails.base import RailEvent


class Transport(Protocol):
    def send_json(self, obj: dict[str, object]) -> None: ...

    def recv(self) -> list[dict[str, object] | bytes]: ...

    def close(self) -> None: ...


def build_session_update(
    cfg: VoiceConfig,
    tools: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    """The ``session.update`` body. Pure. Tests lock this shape."""

    turn: dict[str, object] | None
    if cfg.push_to_talk:
        turn = None
    else:
        turn = {
            "type": "server_vad",
            "threshold": cfg.vad_threshold,
            "silence_duration_ms": cfg.silence_ms,
            "prefix_padding_ms": cfg.prefix_padding_ms,
        }
    transcription: dict[str, object] = {}
    if cfg.language:
        transcription["language_hint"] = cfg.language
    if cfg.keyterms:
        transcription["keyterms"] = list(cfg.keyterms)
    session: dict[str, object] = {
        "voice": cfg.voice,
        "instructions": cfg.instructions,
        "reasoning": {"effort": cfg.reasoning_effort},
        "turn_detection": turn,
        "audio": {
            "input": {
                "format": {"type": "audio/pcm", "rate": cfg.sample_rate},
                "transcription": transcription,
            },
            "output": {
                "format": {"type": "audio/pcm", "rate": cfg.sample_rate},
                "speed": cfg.speed,
            },
        },
    }
    if cfg.replace:
        session["replace"] = dict(cfg.replace)
    if tools:
        session["tools"] = tools
    return {"type": "session.update", "session": session}


def encode_append(pcm: bytes) -> dict[str, object]:
    return {"type": "input_audio_buffer.append", "audio": base64.b64encode(pcm).decode("ascii")}


def encode_cancel() -> dict[str, object]:
    return {"type": "response.cancel"}


def encode_truncate(item_id: str, played_ms: int) -> dict[str, object]:
    return {
        "type": "conversation.item.truncate",
        "item_id": item_id,
        "content_index": 0,
        "audio_end_ms": max(0, played_ms),
    }


def encode_force(text: str, *, interruptible: bool = True) -> dict[str, object]:
    return {
        "type": "conversation.item.create",
        "item": {
            "type": "force_message",
            "role": "assistant",
            "interruptible": interruptible,
            "content": [{"type": "output_text", "text": text}],
        },
    }


def encode_tool_output(call_id: str, output: str) -> dict[str, object]:
    return {
        "type": "conversation.item.create",
        "item": {"type": "function_call_output", "call_id": call_id, "output": output},
    }


def encode_response_create() -> dict[str, object]:
    return {"type": "response.create"}


def decode_event(event: dict[str, object] | bytes) -> list[RailEvent]:
    """Map one server frame onto rail events. Unknown types are ignored."""

    if isinstance(event, bytes):
        return [RailEvent("audio", pcm=event)] if event else []
    kind = str(event.get("type") or "")
    if kind == "input_audio_buffer.speech_started":
        return [RailEvent("speech_started", item_id=str(event.get("item_id") or ""))]
    if kind == "input_audio_buffer.speech_stopped":
        return [RailEvent("speech_stopped", item_id=str(event.get("item_id") or ""))]
    if kind in {"response.output_audio.delta", "response.audio.delta"}:
        raw = event.get("delta") or ""
        pcm = base64.b64decode(str(raw)) if raw else b""
        return [
            RailEvent(
                "audio",
                pcm=pcm,
                item_id=str(event.get("item_id") or ""),
                response_id=str(event.get("response_id") or ""),
            )
        ]
    if kind in {"response.output_audio_transcript.delta", "response.audio_transcript.delta"}:
        return [
            RailEvent(
                "assistant_transcript",
                text=str(event.get("delta") or ""),
                item_id=str(event.get("item_id") or ""),
                final=False,
            )
        ]
    if kind in {
        "conversation.item.input_audio_transcription.completed",
        "conversation.item.input_audio_transcription.updated",
    }:
        text = str(event.get("transcript") or event.get("delta") or "")
        final = kind.endswith("completed")
        return [RailEvent("user_transcript", text=text, final=final)]
    if kind == "response.function_call_arguments.done":
        return [
            RailEvent(
                "tool_call",
                name=str(event.get("name") or ""),
                arguments=str(event.get("arguments") or ""),
                call_id=str(event.get("call_id") or ""),
            )
        ]
    if kind == "response.created":
        response = event.get("response")
        rid = ""
        if isinstance(response, dict):
            rid = str(response.get("id") or "")
        response_id = rid or str(event.get("response_id") or "")
        return [RailEvent("response_created", response_id=response_id)]
    if kind in {"response.done", "response.cancelled"}:
        return [RailEvent("response_done", text=kind)]
    if kind == "conversation.created":
        convo = event.get("conversation")
        cid = str(convo.get("id")) if isinstance(convo, dict) else ""
        return [RailEvent("ready", text=cid)]
    if kind == "error":
        err = event.get("error")
        if isinstance(err, dict):
            message = str(err.get("message"))
        else:
            message = str(event.get("message") or kind)
        return [RailEvent("error", text=message)]
    if kind == "session.updated":
        return [RailEvent("ready", text="session.updated")]
    return []


@dataclass
class MemoryTransport:
    """Records outbound JSON and returns a scripted inbox. No network."""

    sent: list[dict[str, object]] = field(default_factory=list)
    inbox: list[dict[str, object] | bytes] = field(default_factory=list)
    closed: bool = False

    def send_json(self, obj: dict[str, object]) -> None:
        self.sent.append(obj)

    def recv(self) -> list[dict[str, object] | bytes]:
        batch = list(self.inbox)
        self.inbox.clear()
        return batch

    def close(self) -> None:
        self.closed = True


class XaiRealtimeRail:
    name = "xai"

    def __init__(
        self,
        transport: Transport | None = None,
        tools: list[dict[str, object]] | None = None,
    ) -> None:
        self.transport = transport
        self.tools = tools or []
        self.item_id = ""
        self.response_id = ""
        self._pending_outputs: list[tuple[str, str]] = []
        self._continue = False
        self.cfg: VoiceConfig | None = None

    def open(self, cfg: VoiceConfig) -> list[RailEvent]:
        self.cfg = cfg
        if self.transport is None:
            return [RailEvent("error", text="xai transport is not connected")]
        self.transport.send_json(build_session_update(cfg, self.tools))
        return [RailEvent("ready", text="session.update sent")]

    def push_audio(self, pcm: bytes) -> list[RailEvent]:
        if self.transport is None or not pcm:
            return []
        self.transport.send_json(encode_append(pcm))
        return []

    def poll(self) -> list[RailEvent]:
        if self.transport is None:
            return []
        events: list[RailEvent] = []
        for frame in self.transport.recv():
            decoded = decode_event(frame)
            for ev in decoded:
                if ev.item_id and ev.kind == "audio":
                    self.item_id = ev.item_id
                if ev.response_id:
                    self.response_id = ev.response_id
            events.extend(decoded)
        return events

    def barge(self, item_id: str, played_ms: int) -> list[RailEvent]:
        if self.transport is None:
            return []
        self.transport.send_json(encode_cancel())
        target = item_id or self.item_id
        if target:
            self.transport.send_json(encode_truncate(target, played_ms))
        return [RailEvent("barge", item_id=target, text=str(played_ms))]

    def submit_tool_result(self, call_id: str, output: str) -> list[RailEvent]:
        self._pending_outputs.append((call_id, output))
        self._continue = True
        return []

    def continue_after_playback(self) -> list[RailEvent]:
        if self.transport is None or not self._continue:
            return []
        for call_id, output in self._pending_outputs:
            self.transport.send_json(encode_tool_output(call_id, output))
        self._pending_outputs.clear()
        self._continue = False
        self.transport.send_json(encode_response_create())
        return [RailEvent("ready", text="response.create")]

    def force_say(self, text: str) -> list[RailEvent]:
        if self.transport is None:
            return [RailEvent("assistant_transcript", text=text, final=True)]
        self.transport.send_json(encode_force(text))
        return [RailEvent("assistant_transcript", text=text, final=True)]

    def close(self) -> None:
        if self.transport is not None:
            self.transport.close()


def client_secret_request(cfg: VoiceConfig, api_key: str, seconds: int = 300) -> Request:
    """Build the mint call. The key is a header. Callers must not log the request."""

    body = json.dumps({"expires_after": {"seconds": seconds}}).encode("utf-8")
    return Request(
        cfg.base_url.rstrip("/") + "/realtime/client_secrets",
        data=body,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )


def api_key_from_env(cfg: VoiceConfig) -> str:
    return os.environ.get(cfg.api_key_env, "")
