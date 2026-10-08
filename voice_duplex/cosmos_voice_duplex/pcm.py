"""PCM16 little-endian helpers. The speech rails use 24 kHz mono."""

from __future__ import annotations

import struct
import wave
from io import BytesIO


def rms(pcm: bytes) -> float:
    """Root-mean-square of PCM16 samples, scaled to 0..1."""

    if len(pcm) < 2:
        return 0.0
    count = len(pcm) // 2
    total = 0.0
    for (sample,) in struct.iter_unpack("<h", pcm[: count * 2]):
        total += (sample / 32768.0) ** 2
    return (total / count) ** 0.5


def silence(n_bytes: int) -> bytes:
    if n_bytes < 0:
        raise ValueError("n_bytes")
    return b"\x00" * (n_bytes - (n_bytes % 2))


def tone(n_samples: int, rate: int = 24000, freq: float = 440.0, amp: float = 0.2) -> bytes:
    """A short sine burst. Local-rail stand-in when no neural TTS is composed."""

    import math

    out = bytearray()
    for i in range(n_samples):
        sample = int(amp * 32767 * math.sin(2 * math.pi * freq * i / rate))
        out += struct.pack("<h", sample)
    return bytes(out)


def resample(pcm: bytes, src_rate: int, dst_rate: int) -> bytes:
    """Linear resample. Good enough to feed 48 kHz device audio into a 24 kHz rail."""

    if src_rate == dst_rate:
        return pcm
    if src_rate <= 0 or dst_rate <= 0:
        raise ValueError("rate")
    count = len(pcm) // 2
    if count == 0:
        return b""
    samples = list(struct.unpack("<" + "h" * count, pcm[: count * 2]))
    dst_count = max(1, int(round(count * dst_rate / src_rate)))
    out = bytearray()
    for i in range(dst_count):
        pos = i * (count - 1) / max(1, dst_count - 1) if dst_count > 1 else 0.0
        left = int(pos)
        right = min(left + 1, count - 1)
        frac = pos - left
        mixed = samples[left] * (1 - frac) + samples[right] * frac
        out += struct.pack("<h", int(max(-32768, min(32767, round(mixed)))))
    return bytes(out)


def to_wav(pcm: bytes, rate: int = 24000) -> bytes:
    """Wrap raw PCM16 mono so POST /v1/stt can auto-detect a container."""

    buf = BytesIO()
    with wave.open(buf, "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(rate)
        handle.writeframes(pcm)
    return buf.getvalue()


def chunk(pcm: bytes, frame_bytes: int) -> list[bytes]:
    if frame_bytes < 2 or frame_bytes % 2:
        raise ValueError("frame_bytes")
    end = len(pcm) - (len(pcm) % frame_bytes)
    return [pcm[i : i + frame_bytes] for i in range(0, end, frame_bytes)]
