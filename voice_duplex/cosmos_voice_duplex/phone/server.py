"""PC-side phone gateway. Testable with dicts and bytes. No listening socket.

Default transport is a WebSocket from the phone to this PC (Tailscale,
``cosmos up``). This object is what that socket calls. The xAI key is not a
field here. A binary frame is microphone PCM. The reply can mix JSON
messages and one raw PCM frame for the speaker.
"""

from __future__ import annotations

import base64

from cosmos_voice_duplex.phone.protocol import (
    caption_message,
    decode_pcm,
    state_message,
)
from cosmos_voice_duplex.session import DuplexSession

Outbound = dict[str, object] | bytes


class PhoneGateway:
    def __init__(self, session: DuplexSession) -> None:
        self.session = session
        self._caption_at = 0
        self._reported_error = ""

    def handle_message(self, message: dict[str, object] | bytes) -> list[Outbound]:
        if isinstance(message, bytes):
            return self._on_audio(message, as_json=False)
        kind = str(message.get("type") or "")
        if kind == "hello":
            return [
                {
                    "type": "ready",
                    "sample_rate": self.session.cfg.sample_rate,
                    "frame_bytes": self.session.cfg.frame_bytes,
                }
            ]
        if kind == "session.start":
            return self._start(message)
        if kind == "audio":
            try:
                pcm = decode_pcm(message.get("pcm"))
            except ValueError as exc:
                return [{"type": "error", "text": str(exc)}]
            return self._on_audio(pcm, as_json=True)
        if kind == "mute":
            self.session.set_mute(bool(message.get("on")))
            return [state_message(self.session.state)]
        if kind == "ptt":
            if not self.session.cfg.push_to_talk:
                return [{"type": "error", "text": "push_to_talk is off"}]
            self.session.set_ptt(bool(message.get("held")))
            return [state_message(self.session.state)]
        if kind == "stop":
            self.session.close("phone_stop")
            return [state_message("idle", "phone_stop")]
        return [{"type": "error", "text": f"unknown message {kind}"}]

    def _start(self, message: dict[str, object]) -> list[Outbound]:
        if self.session.opened:
            return [{"type": "error", "text": "session already open"}]
        self._apply_options(message)
        if not self.session.open():
            return [{"type": "error", "text": self.session.last_error or "open refused"}]
        return [
            {"type": "ready", "sample_rate": self.session.cfg.sample_rate},
            state_message(self.session.state),
        ]

    def _apply_options(self, message: dict[str, object]) -> None:
        if "push_to_talk" in message:
            self.session.cfg.push_to_talk = bool(message["push_to_talk"])
            self.session.turn.push_to_talk = self.session.cfg.push_to_talk
        if "barge_in" in message:
            self.session.cfg.barge_in = bool(message["barge_in"])
        if "captions" in message:
            self.session.cfg.captions = bool(message["captions"])
        if "half_duplex" in message:
            self.session.cfg.half_duplex = bool(message["half_duplex"])
        if "mute" in message:
            self.session.set_mute(bool(message["mute"]))
        voice = message.get("voice")
        if isinstance(voice, str) and voice:
            self.session.cfg.voice = voice

    def _on_audio(self, pcm: bytes, *, as_json: bool) -> list[Outbound]:
        if not self.session.opened:
            return [{"type": "error", "text": "session is not open"}]
        before = self.session.barge_count
        self.session.feed(pcm)
        spoken = self.session.pull()
        out: list[Outbound] = []
        if self.session.barge_count > before:
            out.append({"type": "barge", "played_ms": self.session.play.played_ms()})
        out.extend(self._captions())
        out.append(state_message(self.session.state))
        if as_json:
            out.append({"type": "audio", "pcm": base64.b64encode(spoken).decode("ascii")})
        else:
            out.append(spoken)
        if self.session.last_error and self.session.last_error != self._reported_error:
            self._reported_error = self.session.last_error
            out.append({"type": "error", "text": self.session.last_error})
        return out

    def _captions(self) -> list[dict[str, object]]:
        fresh = self.session.captions[self._caption_at :]
        self._caption_at = len(self.session.captions)
        return [caption_message(item.role, item.text, item.final) for item in fresh]
