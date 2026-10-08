"""Seat an approved HERO on this rail and write the pack into the attempt.

The native door is not started. grok.exe is not started. The provider stays locked.
"""

from __future__ import annotations

from pathlib import Path

from g47.seat import Seat, seat
from g47.summon import materialize


def seat_here(agent: str, worktree: Path, task: str, *, via: str = "cosmos-code") -> Seat:
    built = seat(agent, via=via, task=task, where=str(worktree))
    materialize(built.plan, worktree)
    return built
