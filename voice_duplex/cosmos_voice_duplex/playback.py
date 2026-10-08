"""Speaker queue. Barge-in drops every unplayed byte before the next quantum.

The cap is the latency budget (default 300 ms). Audio already inside the
hardware buffer can still sound for one frame; this queue is the part we
control. ``played_ms`` counts bytes actually handed to the device, which is
the value ``conversation.item.truncate`` wants.
"""

from __future__ import annotations


class Playback:
    def __init__(self, sample_rate: int = 24000, cap_ms: int = 300) -> None:
        self.sample_rate = sample_rate
        self.cap_bytes = max(2, int(sample_rate * 2 * cap_ms / 1000))
        self._buf = bytearray()
        self._played = 0
        self.dropped_bytes = 0
        self.cleared_bytes = 0

    def __len__(self) -> int:
        return len(self._buf)

    @property
    def pending(self) -> bool:
        return bool(self._buf)

    def played_ms(self) -> int:
        if self.sample_rate <= 0:
            return 0
        return int(self._played / 2 / self.sample_rate * 1000)

    def reset_played(self) -> None:
        self._played = 0

    def write(self, pcm: bytes) -> None:
        if not pcm:
            return
        self._buf += pcm
        overflow = len(self._buf) - self.cap_bytes
        if overflow > 0:
            # Drop the oldest queued audio so a slow pull cannot grow lag.
            drop = overflow + (overflow % 2)
            del self._buf[:drop]
            self.dropped_bytes += drop

    def read(self, n: int) -> bytes:
        if n < 0:
            raise ValueError("n")
        n -= n % 2
        take = bytes(self._buf[:n])
        del self._buf[: len(take)]
        self._played += len(take)
        if len(take) < n:
            take += b"\x00" * (n - len(take))
        return take

    def clear(self) -> int:
        n = len(self._buf)
        self._buf.clear()
        self.cleared_bytes += n
        return n
