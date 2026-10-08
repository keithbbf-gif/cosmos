"""Mode machine tests: wake strip, follow window, and push-to-talk."""

from __future__ import annotations

from cosmos_voice.modes import ModeMachine
from cosmos_voice.types import FOLLOW_WINDOW_S


def test_wake_strip() -> None:
    """A leading hey cosmos or cosmos is stripped. The remainder is the command."""
    machine = ModeMachine()
    heard = machine.accept(
        "Hey Cosmos, open the door",
        held=False,
        tapped=False,
        now=0.0,
        mode="wake",
    )
    assert heard.accepted is True
    assert heard.kind == "wake"
    assert heard.mode == "wake"
    assert heard.transcript == "open the door"
    short = machine.accept("COSMOS status", held=False, tapped=False, now=0.0, mode="wake")
    assert short.accepted is True
    assert short.kind == "wake"
    assert short.transcript == "status"
    glued = machine.accept(
        "cosmosology today",
        held=False,
        tapped=False,
        now=0.0,
        mode="wake",
    )
    assert glued.accepted is False
    assert glued.kind == "ignored"


def test_wake_only() -> None:
    """A bare wake word is not a command and does not open the follow window."""
    machine = ModeMachine()
    bare = machine.accept("hey cosmos", held=False, tapped=False, now=0.0, mode="wake")
    assert bare.accepted is False
    assert bare.kind == "wake_only"
    assert bare.transcript == ""
    cosmos = machine.accept("Cosmos", held=False, tapped=False, now=0.0, mode="wake")
    assert cosmos.accepted is False
    assert cosmos.kind == "wake_only"
    nxt = machine.accept("lights", held=False, tapped=False, now=1.0, mode="wake")
    assert nxt.accepted is False
    assert nxt.kind == "ignored"


def test_follow_window() -> None:
    """After note_spoken, one utterance without a wake word is accepted."""
    machine = ModeMachine(follow_s=10.0)
    machine.note_spoken(5.0)
    heard = machine.accept(
        "turn on the light",
        held=False,
        tapped=False,
        now=6.0,
        mode="wake",
    )
    assert heard.accepted is True
    assert heard.kind == "follow"
    assert heard.mode == "wake"
    assert heard.transcript == "turn on the light"
    again = machine.accept("and the fan", held=False, tapped=False, now=7.0, mode="wake")
    assert again.accepted is False
    assert again.kind == "ignored"


def test_follow_window_expires() -> None:
    """The free utterance is inside the window, including the last instant."""
    open_edge = ModeMachine(follow_s=FOLLOW_WINDOW_S)
    open_edge.note_spoken(0.0)
    edge = open_edge.accept(
        "still here",
        held=False,
        tapped=False,
        now=FOLLOW_WINDOW_S,
        mode="wake",
    )
    assert edge.accepted is True
    assert edge.kind == "follow"
    late_machine = ModeMachine(follow_s=FOLLOW_WINDOW_S)
    late_machine.note_spoken(0.0)
    late = late_machine.accept(
        "too late",
        held=False,
        tapped=False,
        now=FOLLOW_WINDOW_S + 0.01,
        mode="wake",
    )
    assert late.accepted is False
    assert late.kind == "ignored"


def test_ptt() -> None:
    """Push-to-talk accepts only while held, and it does not strip a wake word."""
    machine = ModeMachine()
    heard = machine.accept("cosmos status", held=True, tapped=False, now=0.0, mode="ptt")
    assert heard.accepted is True
    assert heard.kind == "ptt"
    assert heard.transcript == "cosmos status"
    missed = machine.accept("status", held=False, tapped=True, now=0.0, mode="ptt")
    assert missed.accepted is False
    assert missed.kind == "ignored"
    assert missed.transcript == ""
    blank = machine.accept("   ", held=True, tapped=False, now=0.0, mode="ptt")
    assert blank.accepted is False
    assert blank.kind == "ignored"


def test_tap() -> None:
    """Tap accepts only when tapped."""
    machine = ModeMachine()
    heard = machine.accept("status", held=False, tapped=True, now=0.0, mode="tap")
    assert heard.accepted is True
    assert heard.kind == "tap"
    assert heard.transcript == "status"
    missed = machine.accept("status", held=True, tapped=False, now=0.0, mode="tap")
    assert missed.accepted is False
    assert missed.kind == "ignored"


def test_off_and_unknown_are_bad_mode() -> None:
    """Off and an unknown mode do not accept an utterance."""
    machine = ModeMachine()
    off = machine.accept("status", held=True, tapped=True, now=0.0, mode="off")
    assert off.accepted is False
    assert off.kind == "BAD_MODE"
    unknown = machine.accept("status", held=True, tapped=True, now=0.0, mode="shout")
    assert unknown.accepted is False
    assert unknown.kind == "BAD_MODE"
