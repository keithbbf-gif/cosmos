"""Messages between the phone and the PC gateway.

Text frames are JSON objects with a ``type`` field. A binary frame is raw
PCM16 mono, little-endian, at the session rate (20 ms is 960 bytes at
24 kHz). The phone does not send ``input_audio_buffer.commit`` and it does
not send a Send button. Barge-in is more audio, or the server ``barge``
message that tells the handset to flush its track.
"""

from __future__ import annotations

import base64

MESSAGE_TYPES = ("hello", "session.start", "audio", "mute", "ptt", "stop")
SERVER_TYPES = ("ready", "audio", "caption", "state", "barge", "error")


def audio_message(pcm: bytes) -> dict[str, object]:
    return {"type": "audio", "pcm": base64.b64encode(pcm).decode("ascii")}


def decode_pcm(value: object) -> bytes:
    if not isinstance(value, str) or value == "":
        raise ValueError("audio pcm must be base64")
    try:
        return base64.b64decode(value, validate=True)
    except Exception as exc:
        raise ValueError("audio pcm is not base64") from exc


def caption_message(role: str, text: str, final: bool) -> dict[str, object]:
    return {"type": "caption", "role": role, "text": text, "final": final}


def state_message(state: str, reason: str = "") -> dict[str, object]:
    message: dict[str, object] = {"type": "state", "state": state}
    if reason:
        message["reason"] = reason
    return message
