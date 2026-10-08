"""Fail-closed local view of Core control flags.

No files and no network. Until ``apply_poll`` runs, a new utterance stays
blocked. A later poll replaces the stored flags. It does not open a socket.
"""

from __future__ import annotations

from collections.abc import Mapping


def _is_true(row: Mapping[str, object], name: str) -> bool:
    return row.get(name) is True


def _flag_row(body: dict[str, object]) -> Mapping[str, object]:
    raw = body.get("effective")
    if isinstance(raw, dict):
        return {str(key): value for key, value in raw.items()}
    return body


class ControlView:
    """Last known ``pause``, ``mic_off``, and ``clear_queue`` flags.

    ``mic_off`` blocks before ``pause``. ``clear_queue`` never blocks a new
    utterance by itself. Only the boolean ``True`` turns a flag on.
    """

    def __init__(self) -> None:
        """Start unread so capture is blocked until a poll is applied."""
        self._seen = False
        self._pause = False
        self._mic_off = False
        self._clear_queue = False

    def apply_poll(self, body: dict[str, object]) -> None:
        """Store flags from ``effective``, or from ``body`` when that is not a dict.

        ``effective`` wins only when it is a dict, including an empty one.
        A flag is on only when its value is the boolean ``True``.
        """
        row = _flag_row(body)
        self._pause = _is_true(row, "pause")
        self._mic_off = _is_true(row, "mic_off")
        self._clear_queue = _is_true(row, "clear_queue")
        self._seen = True

    def blocked(self) -> tuple[bool, str]:
        """Return ``(blocked, reason)`` for a new utterance.

        No poll yet is ``CONTROL_UNREAD``. ``mic_off`` is ``MIC_OFF``.
        ``pause`` is ``PAUSED``. Otherwise ``(False, "ok")``.
        """
        if not self._seen:
            return (True, "CONTROL_UNREAD")
        if self._mic_off:
            return (True, "MIC_OFF")
        if self._pause:
            return (True, "PAUSED")
        return (False, "ok")

    def kill_local(self) -> None:
        """Set ``mic_off``. Does not count as a poll and does not write a file."""
        self._mic_off = True

    def resume_local(self) -> None:
        """Clear ``pause`` and ``mic_off``. Does not count as a poll."""
        self._pause = False
        self._mic_off = False

    def clear_requested(self) -> bool:
        """True when the latest poll set ``clear_queue`` to boolean ``True``.

        A local kill or resume does not change this flag. It does not block
        a new utterance by itself.
        """
        return self._clear_queue
