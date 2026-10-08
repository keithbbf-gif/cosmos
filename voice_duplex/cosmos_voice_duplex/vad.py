"""Local energy VAD. This is the fast barge-in trip, not the turn decider.

The speech rail's server VAD (xAI ``server_vad``, threshold 0.85, prefix
333 ms) decides when a turn is finished. This detector only notices that
the user has started, so playback can stop before the server event returns.
It keeps a prefix ring so the first syllable is not clipped if a local
cascade rail has to commit the utterance itself.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

from cosmos_voice_duplex.pcm import rms


@dataclass(frozen=True)
class VadEvent:
    kind: str  # "start" | "end"
    utterance: bytes = b""


class EnergyVad:
    def __init__(
        self,
        sample_rate: int = 24000,
        threshold: float = 0.02,
        silence_ms: int = 500,
        prefix_ms: int = 333,
        min_speech_ms: int = 80,
    ) -> None:
        self.sample_rate = sample_rate
        self.threshold = threshold
        self.silence_ms = silence_ms
        self.prefix_ms = prefix_ms
        self.min_speech_ms = min_speech_ms
        self._speaking = False
        self._speech_ms = 0
        self._silence_run = 0
        self._prefix: deque[bytes] = deque()
        self._prefix_ms = 0
        self._utt = bytearray()

    @property
    def speaking(self) -> bool:
        return self._speaking

    def reset(self) -> None:
        self._speaking = False
        self._speech_ms = 0
        self._silence_run = 0
        self._prefix.clear()
        self._prefix_ms = 0
        self._utt.clear()

    def push(self, pcm: bytes) -> list[VadEvent]:
        if not pcm:
            return []
        samples = len(pcm) // 2
        frame_ms = int(samples * 1000 / self.sample_rate) if self.sample_rate else 0
        loud = rms(pcm) >= self.threshold
        events: list[VadEvent] = []
        if not self._speaking:
            self._prefix.append(pcm)
            self._prefix_ms += frame_ms
            # Keep the newest frame even when it is longer than the prefix
            # budget. Dropping it would clip the syllable that opened the turn.
            while len(self._prefix) > 1 and self._prefix_ms > self.prefix_ms:
                dropped = self._prefix.popleft()
                dropped_ms = int((len(dropped) // 2) * 1000 / self.sample_rate)
                self._prefix_ms -= dropped_ms
            if loud:
                self._speech_ms += frame_ms
                if self._speech_ms >= self.min_speech_ms:
                    self._speaking = True
                    self._silence_run = 0
                    self._utt = bytearray(b"".join(self._prefix))
                    events.append(VadEvent("start"))
            else:
                self._speech_ms = 0
            return events
        self._utt += pcm
        if loud:
            self._silence_run = 0
            self._speech_ms += frame_ms
        else:
            self._silence_run += frame_ms
            if self._silence_run >= self.silence_ms:
                utterance = bytes(self._utt)
                self.reset()
                events.append(VadEvent("end", utterance))
        return events
