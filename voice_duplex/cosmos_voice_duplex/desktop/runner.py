"""Run a duplex session against a device. The scripted device needs no card."""

from __future__ import annotations

from typing import Protocol

from cosmos_voice_duplex.config import VoiceConfig
from cosmos_voice_duplex.factory import select_rail
from cosmos_voice_duplex.pcm import silence
from cosmos_voice_duplex.session import DuplexSession


class DuplexDevice(Protocol):
    def read(self, n: int) -> bytes: ...

    def write(self, pcm: bytes) -> None: ...


class ScriptedDevice:
    """Yields prepared microphone frames and records speaker frames."""

    def __init__(self, frames: list[bytes] | None = None) -> None:
        self.frames = list(frames or [])
        self.played: list[bytes] = []
        self._index = 0

    def read(self, n: int) -> bytes:
        if self._index >= len(self.frames):
            return silence(n)
        frame = self.frames[self._index]
        self._index += 1
        if len(frame) >= n:
            return frame[:n]
        return frame + silence(n - len(frame))

    def write(self, pcm: bytes) -> None:
        self.played.append(pcm)


def run_frames(session: DuplexSession, device: DuplexDevice, n: int) -> None:
    """Pull ``n`` frames. The session must already be open."""

    for _ in range(n):
        session.feed(device.read(session.cfg.frame_bytes))
        device.write(session.pull())


def build_session(cfg: VoiceConfig | None = None) -> DuplexSession:
    chosen = cfg if cfg is not None else VoiceConfig()
    return DuplexSession(chosen, select_rail(chosen))
