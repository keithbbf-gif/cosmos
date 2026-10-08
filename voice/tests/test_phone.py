"""Phone mule tests: permission, PCM pointer, and desktop silence."""

from __future__ import annotations

from collections.abc import Callable

from cosmos_voice.errors import VoiceError
from cosmos_voice.phone import PhoneMule, kind_status, plan_pull
from cosmos_voice.types import PullPlan


def _refused(kind: str, call: Callable[[], object]) -> None:
    """``call`` must raise ``VoiceError`` of ``kind``."""
    try:
        call()
    except VoiceError as exc:
        assert exc.kind == kind
        return
    raise AssertionError(kind)


def test_perm_denied() -> None:
    """A missing grant is PERM_DENIED, not a collected blob."""
    collected: dict[str, object] = {"status": "ok", "n": 1}
    denied = kind_status("sms", granted=False, collected=collected)
    assert denied == {"status": "PERM_DENIED"}
    assert collected == {"status": "ok", "n": 1}
    also = kind_status("sms", granted=False, collected=None)
    assert also == {"status": "PERM_DENIED"}


def test_no_collector() -> None:
    """A grant with no reader is NO_COLLECTOR, not an empty object."""
    assert kind_status("calendar", granted=True, collected=None) == {"status": "NO_COLLECTOR"}


def test_kind_status_copies_and_defaults_ok() -> None:
    """Collected fields are copied and status defaults to ok."""
    collected: dict[str, object] = {"battery_pct": 40}
    out = kind_status("device", granted=True, collected=collected)
    assert out == {"battery_pct": 40, "status": "ok"}
    assert collected == {"battery_pct": 40}
    partial: dict[str, object] = {"status": "partial", "n": 1}
    kept = kind_status("notifications", granted=True, collected=partial)
    assert kept == {"status": "partial", "n": 1}
    assert kept is not partial


def test_inline_pcm_refused() -> None:
    """pcm cannot carry bytes, pcm, data, or b64."""
    mule = PhoneMule("phone", "tree")

    def once(blob: dict[str, object]) -> None:
        _refused("BAD_SNAPSHOT", lambda: mule.snapshot({"pcm": blob}))

    for key in ("bytes", "pcm", "data", "b64"):
        once({"sha256": "abc123", key: "inline"})


def test_empty_kind_refused() -> None:
    """A known kind that is an empty object is BAD_SNAPSHOT."""
    mule = PhoneMule("phone", "tree")
    _refused("BAD_SNAPSHOT", lambda: mule.snapshot({"device": {}}))


def test_pcm_requires_sha256() -> None:
    """pcm must include a non-empty sha256 string."""
    mule = PhoneMule("phone", "tree")
    blobs: tuple[dict[str, object], ...] = (
        {"n_bytes": 8},
        {"sha256": ""},
        {"sha256": "   "},
        {"sha256": 12},
    )

    def once(blob: dict[str, object]) -> None:
        _refused("BAD_SNAPSHOT", lambda: mule.snapshot({"pcm": blob}))

    for blob in blobs:
        once(blob)


def test_snapshot_drops_unknown_and_ids() -> None:
    """Unknown kinds are dropped. The body carries client, tree, and request ids."""
    mule = PhoneMule("phone-1", "tree-1")
    pcm: dict[str, object] = {"sha256": "abc", "n_bytes": 4}
    body = mule.snapshot({"pcm": pcm, "not_a_kind": {}, "device": {"status": "ok"}})
    assert body["client_id"] == "phone-1"
    assert body["tree_id"] == "tree-1"
    request_id = body["request_id"]
    assert isinstance(request_id, str)
    assert len(request_id) == 32
    assert request_id.lower() == request_id
    kinds = body["kinds"]
    assert isinstance(kinds, dict)
    assert set(kinds) == {"pcm", "device"}
    assert kinds["pcm"] == {"sha256": "abc", "n_bytes": 4}
    pcm["sha256"] = "changed"
    assert kinds["pcm"] == {"sha256": "abc", "n_bytes": 4}
    empty = mule.snapshot({"nope": {}})
    assert empty["kinds"] == {}


def test_desktop_owner_silences_phone_tts() -> None:
    """Desktop ownership plays no phone TTS and does not fight Bluetooth."""
    plan = plan_pull({"pull": True, "core_kind": "LIVE", "audio_owner": "desktop"})
    assert plan == PullPlan(
        play_tts=False,
        capture=True,
        fight_bluetooth=False,
        core_kind="LIVE",
        audio_owner="desktop",
    )


def test_phone_owner_does_not_fight_bluetooth() -> None:
    """The phone may speak and capture, and still must not force SCO."""
    plan = plan_pull(
        {
            "pull": True,
            "core_kind": "LIVE",
            "audio_owner": "phone",
            "fight_bluetooth": True,
        }
    )
    assert plan.play_tts is True
    assert plan.capture is True
    assert plan.fight_bluetooth is False


def test_pull_false_and_unreachable_are_silent() -> None:
    """No pull, or an unreachable core, captures nothing and speaks nothing."""
    quiet = plan_pull({"pull": False, "core_kind": "LIVE", "audio_owner": "phone"})
    assert quiet.play_tts is False
    assert quiet.capture is False
    assert quiet.fight_bluetooth is False
    down = plan_pull({"pull": True, "core_kind": "UNREACHABLE", "audio_owner": "phone"})
    assert down == PullPlan(
        play_tts=False,
        capture=False,
        fight_bluetooth=False,
        core_kind="UNREACHABLE",
        audio_owner="phone",
    )
    desktop = plan_pull({"pull": False, "core_kind": "LIVE", "audio_owner": "desktop"})
    assert desktop.capture is False
    assert desktop.play_tts is False


def test_missing_or_none_owner_is_idle() -> None:
    """A missing owner is none: no TTS and no capture."""
    missing = plan_pull({"pull": True, "core_kind": "LIVE"})
    assert missing == PullPlan(False, False, False, "LIVE", "none")
    idle = plan_pull({"pull": True, "core_kind": "LIVE", "audio_owner": "none"})
    assert idle.play_tts is False
    assert idle.capture is False
    assert idle.fight_bluetooth is False
