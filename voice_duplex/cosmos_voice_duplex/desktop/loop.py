"""One duplex quantum for the desktop.

The card callback copies microphone bytes into a ring and speaker bytes out
of a ring. It does not call the rail. ``pump`` drains the mic ring into the
session and fills the play ring. That keeps a WebSocket off the WASAPI
thread. ``mix_callback`` is the same feed and pull without a card, so tests
can run the quantum with no hardware.

Shared-mode WASAPI only. Exclusive mode is not used.
"""

from __future__ import annotations

import importlib
import threading
from typing import Any

from cosmos_voice_duplex.config import VoiceConfig
from cosmos_voice_duplex.session import DuplexSession


class ByteRings:
    """Mic and speaker byte rings guarded by one lock."""

    def __init__(self, cap_bytes: int) -> None:
        self.cap_bytes = max(2, cap_bytes)
        self._mic = bytearray()
        self._play = bytearray()
        self._lock = threading.Lock()

    def push_mic(self, pcm: bytes) -> None:
        with self._lock:
            self._mic += pcm

    def take_mic(self) -> bytes:
        with self._lock:
            data = bytes(self._mic)
            self._mic.clear()
            return data

    def push_play(self, pcm: bytes) -> None:
        if not pcm:
            return
        with self._lock:
            self._play += pcm
            overflow = len(self._play) - self.cap_bytes
            if overflow > 0:
                drop = overflow + (overflow % 2)
                del self._play[:drop]

    def take_play(self, n: int) -> bytes:
        if n < 0:
            raise ValueError("n")
        n -= n % 2
        with self._lock:
            take = bytes(self._play[:n])
            del self._play[: len(take)]
        if len(take) < n:
            take += b"\x00" * (n - len(take))
        return take

    def mic_waiting(self) -> int:
        with self._lock:
            return len(self._mic)


def choose_blocksize(cfg: VoiceConfig) -> int:
    """10 ms (240) or 20 ms (480) at 24 kHz. Other rates use the frame size."""

    samples = cfg.frame_samples
    if samples in {240, 480}:
        return samples
    return samples if samples > 0 else 480


def mix_callback(indata: bytes, outdata: bytearray, session: DuplexSession) -> None:
    """Feed ``indata`` and write the next speaker bytes into ``outdata``."""

    session.feed(indata)
    even = len(outdata) - (len(outdata) % 2)
    spoken = session.pull(even)
    outdata[: len(spoken)] = spoken
    if len(spoken) < len(outdata):
        outdata[len(spoken) :] = b"\x00" * (len(outdata) - len(spoken))


class SoundDeviceLoop:
    """Shared-mode duplex stream. ``start`` is the only import of sounddevice."""

    def __init__(self, session: DuplexSession, blocksize: int | None = None) -> None:
        self.session = session
        self.blocksize = choose_blocksize(session.cfg) if blocksize is None else blocksize
        cap = session.cfg.sample_rate * 2 * 300 // 1000
        self.rings = ByteRings(cap)
        self.started = False
        self._stream: object | None = None

    def callback(self, indata: bytes, outdata: bytearray) -> None:
        """Card thread. Rings only."""

        self.rings.push_mic(indata)
        spoken = self.rings.take_play(len(outdata))
        outdata[: len(spoken)] = spoken

    def pump(self) -> None:
        """Session thread. Safe to call with an empty mic ring."""

        mic = self.rings.take_mic()
        if mic and self.session.opened:
            self.session.feed(mic)
        if self.session.opened:
            self.rings.push_play(self.session.pull())

    def start(self) -> None:
        sd = importlib.import_module("sounddevice")
        wasapi_cls = getattr(sd, "WasapiSettings", None)
        wasapi = wasapi_cls(exclusive=False, auto_convert=True) if wasapi_cls else None
        raw_stream = getattr(sd, "RawStream")
        loop = self

        def _on_audio(
            indata: Any,
            outdata: Any,
            frames: int,
            time_info: Any,
            status: Any,
        ) -> None:
            del time_info, status
            speaker = bytearray(frames * 2)
            loop.callback(bytes(indata), speaker)
            outdata[:] = speaker

        device = (self.session.cfg.input_device, self.session.cfg.output_device)
        self._stream = raw_stream(
            samplerate=self.session.cfg.sample_rate,
            channels=1,
            dtype="int16",
            blocksize=self.blocksize,
            callback=_on_audio,
            extra_settings=wasapi,
            device=device,
            latency="low",
        )
        start = getattr(self._stream, "start", None)
        if not callable(start):
            raise RuntimeError("sounddevice RawStream has no start")
        start()
        self.started = True

    def stop(self) -> None:
        stream = self._stream
        if stream is not None:
            stop = getattr(stream, "stop", None)
            close = getattr(stream, "close", None)
            if callable(stop):
                stop()
            if callable(close):
                close()
        self._stream = None
        self.started = False
