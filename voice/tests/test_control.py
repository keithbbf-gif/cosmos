"""ControlView fail-closed poll, local kill, and local resume."""

from __future__ import annotations

from cosmos_voice.control import ControlView


def test_unread_blocks_until_a_poll() -> None:
    """No poll has been applied, so speech stays shut."""
    view = ControlView()
    assert view.blocked() == (True, "CONTROL_UNREAD")
    assert view.clear_requested() is False


def test_local_commands_do_not_count_as_a_poll() -> None:
    """Kill and resume do not clear CONTROL_UNREAD."""
    view = ControlView()
    view.resume_local()
    assert view.blocked() == (True, "CONTROL_UNREAD")
    view.kill_local()
    assert view.blocked() == (True, "CONTROL_UNREAD")
    view.resume_local()
    assert view.blocked() == (True, "CONTROL_UNREAD")


def test_effective_flags_block_in_order() -> None:
    """mic_off wins over pause. A later clear poll opens the gate."""
    view = ControlView()
    view.apply_poll(
        {
            "pause": False,
            "mic_off": False,
            "effective": {"pause": True, "mic_off": True, "clear_queue": True},
        }
    )
    assert view.blocked() == (True, "MIC_OFF")
    assert view.clear_requested() is True
    view.apply_poll(
        {"effective": {"pause": True, "mic_off": False, "clear_queue": False}}
    )
    assert view.blocked() == (True, "PAUSED")
    assert view.clear_requested() is False
    view.apply_poll(
        {"effective": {"pause": False, "mic_off": False, "clear_queue": False}}
    )
    assert view.blocked() == (False, "ok")


def test_effective_false_beats_root_true() -> None:
    """A dict under effective is the flag row, even when every flag is false."""
    view = ControlView()
    view.apply_poll(
        {
            "pause": True,
            "mic_off": True,
            "clear_queue": True,
            "effective": {"pause": False, "mic_off": False, "clear_queue": False},
        }
    )
    assert view.blocked() == (False, "ok")
    assert view.clear_requested() is False


def test_missing_effective_reads_the_body() -> None:
    """Without an effective dict, the body itself is the flag row."""
    paused = ControlView()
    paused.apply_poll({"pause": True, "mic_off": False, "clear_queue": True})
    assert paused.blocked() == (True, "PAUSED")
    assert paused.clear_requested() is True

    muted = ControlView()
    muted.apply_poll({"effective": None, "mic_off": True, "pause": False})
    assert muted.blocked() == (True, "MIC_OFF")

    listed = ControlView()
    listed.apply_poll({"effective": ["mic_off"], "pause": True})
    assert listed.blocked() == (True, "PAUSED")


def test_clear_queue_alone_does_not_block() -> None:
    """clear_queue is recorded and does not refuse a new utterance."""
    view = ControlView()
    view.apply_poll({"clear_queue": True})
    assert view.blocked() == (False, "ok")
    assert view.clear_requested() is True
    view.apply_poll({})
    assert view.blocked() == (False, "ok")
    assert view.clear_requested() is False


def test_only_boolean_true_arms_a_flag() -> None:
    """Missing keys and non-booleans stay off."""
    view = ControlView()
    view.apply_poll(
        {
            "effective": {
                "pause": 1,
                "mic_off": "true",
                "clear_queue": "yes",
            }
        }
    )
    assert view.blocked() == (False, "ok")
    assert view.clear_requested() is False


def test_kill_and_resume_after_a_poll() -> None:
    """Local kill sets mic_off. Local resume clears pause and mic_off."""
    view = ControlView()
    view.apply_poll(
        {"effective": {"pause": False, "mic_off": False, "clear_queue": True}}
    )
    assert view.blocked() == (False, "ok")
    view.kill_local()
    assert view.blocked() == (True, "MIC_OFF")
    assert view.clear_requested() is True
    view.resume_local()
    assert view.blocked() == (False, "ok")
    assert view.clear_requested() is True


def test_resume_clears_polled_pause_and_mic_off() -> None:
    """resume_local is the local road back. A later poll can shut it again."""
    view = ControlView()
    view.apply_poll({"pause": True, "mic_off": True, "clear_queue": False})
    assert view.blocked() == (True, "MIC_OFF")
    view.resume_local()
    assert view.blocked() == (False, "ok")
    view.apply_poll({"effective": {"pause": True, "mic_off": False, "clear_queue": False}})
    assert view.blocked() == (True, "PAUSED")


def test_poll_replaces_a_local_kill() -> None:
    """The newest poll is the flag row, including one that clears mic_off."""
    view = ControlView()
    view.apply_poll({"mic_off": False, "pause": False, "clear_queue": False})
    view.kill_local()
    assert view.blocked() == (True, "MIC_OFF")
    view.apply_poll({"effective": {"mic_off": False, "pause": False, "clear_queue": False}})
    assert view.blocked() == (False, "ok")
