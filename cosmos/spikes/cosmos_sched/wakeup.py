"""Interrupt-driven wakeup. No polling loop.

Container-run: threading.Timer and inotify.
Windows-run: ReadDirectoryChangesW is NATIVE-DEMO-REQUIRED.
"""

from __future__ import annotations

import ctypes
import ctypes.util
import os
import select
import struct
import threading
from pathlib import Path
from typing import Callable

from cosmos.spikes.cosmos_sched.absence import Absence, TypedResult


POLL_INTERVAL_S = 60.0  # incumbent Task Scheduler tick; measurement baseline

IN_CLOSE_WRITE = 0x00000008
IN_CREATE = 0x00000100
IN_MOVED_TO = 0x00000080
IN_ATTRIB = 0x00000004
IN_MODIFY = 0x00000002


class TimerWakeup:
    """threading.Timer — a timer event fires a job with no polling loop."""

    def __init__(self, delay_s: float, on_fire: Callable[[], None]) -> None:
        self.delay_s = delay_s
        self.on_fire = on_fire
        self._timer: threading.Timer | None = None
        self.fired = threading.Event()

    def arm(self) -> TypedResult[str]:
        if self._timer is not None:
            return TypedResult(Absence.REFUSED, "timer already armed")

        def _fire() -> None:
            self.fired.set()
            self.on_fire()

        self._timer = threading.Timer(self.delay_s, _fire)
        self._timer.daemon = True
        self._timer.start()
        return TypedResult(Absence.FOUND, f"timer armed delay_s={self.delay_s}", "armed")

    def cancel(self) -> None:
        if self._timer is not None:
            self._timer.cancel()
            self._timer = None


class InotifyWatch:
    """Linux inotify. Proves file-change wakeup without a 60 s poll."""

    def __init__(self, directory: Path, on_event: Callable[[str], None]) -> None:
        self.directory = directory
        self.on_event = on_event
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._fd = -1
        self.events: list[str] = []

    def start(self) -> TypedResult[str]:
        libc_name = ctypes.util.find_library("c")
        if libc_name is None:
            return TypedResult(Absence.UNREACHABLE, "libc not found; inotify unavailable")
        libc = ctypes.CDLL(libc_name, use_errno=True)
        libc.inotify_init.restype = ctypes.c_int
        libc.inotify_add_watch.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_uint32]
        libc.inotify_add_watch.restype = ctypes.c_int
        fd = libc.inotify_init()
        if fd < 0:
            return TypedResult(Absence.UNREACHABLE, "inotify_init failed")
        mask = IN_CLOSE_WRITE | IN_CREATE | IN_MOVED_TO | IN_ATTRIB | IN_MODIFY
        wd = libc.inotify_add_watch(fd, str(self.directory).encode("utf-8"), mask)
        if wd < 0:
            os.close(fd)
            return TypedResult(Absence.UNREADABLE, f"inotify_add_watch failed on {self.directory}")
        self._fd = fd
        self._thread = threading.Thread(target=self._loop, name="cosmos-inotify", daemon=True)
        self._thread.start()
        return TypedResult(Absence.FOUND, f"inotify wd={wd} fd={fd}", "armed")

    def _loop(self) -> None:
        buf = bytearray(4096)
        while not self._stop.is_set():
            try:
                ready, _, _ = select.select([self._fd], [], [], 0.25)
            except (ValueError, OSError):
                break
            if not ready:
                continue
            try:
                n = os.read(self._fd, 4096)
            except OSError:
                break
            if not n:
                continue
            buf = n
            offset = 0
            while offset + 16 <= len(buf):
                _wd, mask, _cookie, name_len = struct.unpack_from("iIII", buf, offset)
                name = ""
                if name_len:
                    raw = buf[offset + 16 : offset + 16 + name_len]
                    name = raw.split(b"\x00", 1)[0].decode("utf-8", errors="replace")
                offset += 16 + name_len
                kind = f"mask=0x{mask:x}:{name}"
                self.events.append(kind)
                self.on_event(kind)

    def stop(self) -> None:
        self._stop.set()
        if self._fd >= 0:
            try:
                os.close(self._fd)
            except OSError:
                pass
            self._fd = -1
        if self._thread is not None:
            self._thread.join(timeout=1.0)


def measure_timer_wakeup(delay_s: float = 0.05) -> dict[str, float]:
    import time

    started = time.perf_counter()
    hit_at: list[float] = []

    def on_fire() -> None:
        hit_at.append(time.perf_counter())

    wake = TimerWakeup(delay_s, on_fire)
    armed = wake.arm()
    if armed.kind is not Absence.FOUND:
        raise RuntimeError(armed.detail)
    if not wake.fired.wait(timeout=delay_s + 2.0):
        raise TimeoutError("timer wakeup did not fire")
    latency = (hit_at[0] if hit_at else time.perf_counter()) - started
    return {
        "wakeup_latency_s": latency,
        "poll_interval_s": POLL_INTERVAL_S,
        "speedup_vs_poll": POLL_INTERVAL_S / latency if latency > 0 else float("inf"),
        "delay_s": delay_s,
    }


def measure_inotify_wakeup(directory: Path, write_name: str = "wake.probe") -> dict[str, float]:
    import time

    hit = threading.Event()
    hit_at: list[float] = []

    def on_event(_kind: str) -> None:
        hit_at.append(time.perf_counter())
        hit.set()

    watch = InotifyWatch(directory, on_event)
    started_ok = watch.start()
    if started_ok.kind is not Absence.FOUND:
        raise RuntimeError(started_ok.detail)
    try:
        time.sleep(0.05)
        t0 = time.perf_counter()
        (directory / write_name).write_text("wake\n", encoding="utf-8")
        if not hit.wait(timeout=2.0):
            raise TimeoutError("inotify wakeup did not fire")
        latency = (hit_at[0] if hit_at else time.perf_counter()) - t0
    finally:
        watch.stop()
    return {
        "wakeup_latency_s": latency,
        "poll_interval_s": POLL_INTERVAL_S,
        "speedup_vs_poll": POLL_INTERVAL_S / latency if latency > 0 else float("inf"),
    }
