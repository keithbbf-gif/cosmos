"""Wake-word gate: on-device arming, cooldown floor, session descriptor."""

from __future__ import annotations

from pathlib import Path
from typing import cast

import pytest

from cosmos_hermes import PathJail, Refuse, secret_shape
from wake_word import (
    MAX_COOLDOWN_S,
    MIN_COOLDOWN_S,
    MISS,
    SCHEMA,
    THRESHOLD,
    Arm,
    Cooldown,
    SessionRequest,
    WakeStatus,
    WakeWord,
)


def test_schema_default_phrase_and_closed_device() -> None:
    gate = WakeWord()
    assert SCHEMA == "cosmos-hermes-wake_word/1"
    assert THRESHOLD == 0.5
    assert MIN_COOLDOWN_S == 2
    assert gate.phrase == "hey hermes"
    assert gate.cooldown == Cooldown(requested=2, effective=2)
    status = gate.status()
    assert status.schema == SCHEMA
    assert status.armed is False
    assert status.on_device is False
    assert status.opens_device is False
    assert status.engine == "openwakeword"
    assert status.provider == "auto"
    assert status.detector == "hey_hermes"
    assert status.threshold == 0.5
    assert status.last_hit_at is None
    arm = gate.enable(True)
    assert isinstance(arm, Arm)
    assert arm.on_device is True
    assert arm.opens_device is False
    assert arm.effective == 2
    assert gate.status().armed is True


def test_cloud_wake_does_not_arm() -> None:
    gate = WakeWord()
    with pytest.raises(Refuse) as caught:
        gate.enable(False)
    assert caught.value.code == "CLOUD_WAKE"
    assert gate.status().armed is False
    gate.enable(True)
    with pytest.raises(Refuse) as again:
        gate.enable(False)
    assert again.value.code == "CLOUD_WAKE"
    assert gate.status().armed is True
    assert gate.status().opens_device is False


def test_miss_hit_cooldown_floor_and_rewind() -> None:
    gate = WakeWord(cooldown_s=1)
    assert gate.cooldown.requested == 1
    assert gate.cooldown.effective == MIN_COOLDOWN_S
    gate.enable(True)
    assert gate.hear(0.0, 10) == MISS
    assert gate.hear(0.49, 10) == MISS
    assert gate.status().last_hit_at is None
    first = gate.hear(0.5, 10)
    assert isinstance(first, SessionRequest)
    assert first.schema == SCHEMA
    assert first.kind == "session-request"
    assert first.phrase == "hey hermes"
    assert first.heard_at == 10
    assert first.score == 0.5
    assert first.start_new_session is True
    assert first.opens_device is False
    assert first.engine == "openwakeword"
    assert gate.status().last_hit_at == 10
    with pytest.raises(Refuse) as rewound:
        gate.hear(0.9, 9)
    assert rewound.value.code == "REWOUND"
    with pytest.raises(Refuse) as low:
        gate.hear(0.1, 11)
    assert low.value.code == "COOLDOWN"
    with pytest.raises(Refuse) as high:
        gate.hear(0.99, 11)
    assert high.value.code == "COOLDOWN"
    second = gate.hear(1, 12)
    assert isinstance(second, SessionRequest)
    assert second.heard_at == 12
    assert second.score == 1.0
    assert second.opens_device is False
    with pytest.raises(AttributeError):
        setattr(second, "opens_device", True)
    assert hash(second) == hash(second)


def test_cooldown_cap_is_recorded() -> None:
    high = WakeWord(cooldown_s=121)
    assert high.cooldown.requested == 121
    assert high.cooldown.effective == MAX_COOLDOWN_S
    assert high.set_cooldown(500) == Cooldown(requested=500, effective=120)
    assert high.set_cooldown(120) == Cooldown(requested=120, effective=120)
    assert high.set_cooldown(0) == Cooldown(requested=0, effective=2)
    high.set_cooldown(121)
    high.enable(True)
    assert isinstance(high.hear(0.8, 0), SessionRequest)
    with pytest.raises(Refuse) as caught:
        high.hear(0.8, 119)
    assert caught.value.code == "COOLDOWN"
    assert isinstance(high.hear(0.8, 120), SessionRequest)
    with pytest.raises(Refuse) as huge:
        high.set_cooldown(1_000_001)
    assert huge.value.code == "OUT_OF_RANGE"
    assert high.cooldown.effective == 120
    with pytest.raises(Refuse) as flag:
        high.set_cooldown(True)
    assert flag.value.code == "NOT_INT"
    with pytest.raises(Refuse) as negative:
        WakeWord(cooldown_s=-1)
    assert negative.value.code == "OUT_OF_RANGE"


def test_unarmed_disable_keeps_cooldown() -> None:
    gate = WakeWord()
    with pytest.raises(Refuse) as bare:
        gate.hear(0.9, 5)
    assert bare.value.code == "NOT_ARMED"
    gate.enable(True)
    assert isinstance(gate.hear(0.9, 50), SessionRequest)
    disarmed = gate.disable()
    assert disarmed.armed is False
    assert disarmed.opens_device is False
    with pytest.raises(Refuse) as dark:
        gate.hear(0.9, 1000)
    assert dark.value.code == "NOT_ARMED"
    gate.enable(True)
    with pytest.raises(Refuse) as cool:
        gate.hear(0.9, 51)
    assert cool.value.code == "COOLDOWN"
    assert isinstance(gate.hear(0.9, 52), SessionRequest)


def test_bad_score_and_time() -> None:
    gate = WakeWord()
    gate.enable(True)
    for score in (True, "0.9", None, float("nan"), float("inf"), -0.01, 1.01):
        with pytest.raises(Refuse) as caught:
            gate.hear(score, 3)
        assert caught.value.code == "BAD_SCORE"
    assert gate.hear(0, 3) == MISS
    for moment in (True, 1.5, "3", None):
        with pytest.raises(Refuse) as caught:
            gate.hear(0.9, moment)
        assert caught.value.code == "NOT_INT"
    with pytest.raises(Refuse) as late:
        gate.hear(0.9, -1)
    assert late.value.code == "OUT_OF_RANGE"
    assert gate.status().last_hit_at is None


def test_not_bool_and_continue_session() -> None:
    gate = WakeWord()
    for value in (1, "yes", None):
        with pytest.raises(Refuse) as caught:
            gate.enable(value)
        assert caught.value.code == "NOT_BOOL"
    assert gate.status().armed is False
    with pytest.raises(Refuse) as flagged:
        WakeWord(start_new_session=cast(bool, 1))
    assert flagged.value.code == "NOT_BOOL"
    continued = WakeWord(start_new_session=False)
    continued.enable(True)
    heard = continued.hear(0.7, 4)
    assert isinstance(heard, SessionRequest)
    assert heard.start_new_session is False
    assert heard.opens_device is False


def test_phrase_bounds() -> None:
    with pytest.raises(Refuse) as empty:
        WakeWord(phrase="  ")
    assert empty.value.code == "EMPTY_PHRASE"
    with pytest.raises(Refuse) as shaped:
        WakeWord(phrase="Hey Hermes")
    assert shaped.value.code == "BAD_PHRASE"
    with pytest.raises(Refuse) as huge:
        WakeWord(phrase="a" * 65)
    assert huge.value.code == "OVERSIZE"
    with pytest.raises(Refuse) as nul:
        WakeWord(phrase="hey\x00hermes")
    assert nul.value.code == "NULL_BYTE"
    with pytest.raises(Refuse) as text:
        WakeWord(phrase=cast(str, 3))
    assert text.value.code == "NOT_TEXT"
    gate = WakeWord(phrase="a" * 64, provider="sherpa")
    assert gate.phrase == "a" * 64


def test_surfaces_and_allowlist() -> None:
    with pytest.raises(Refuse) as remote:
        WakeWord(surface="telegram")
    assert remote.value.code == "NOT_LOCAL"
    with pytest.raises(Refuse) as gateway:
        WakeWord(surface="gateway")
    assert gateway.value.code == "NOT_LOCAL"
    with pytest.raises(Refuse) as bad:
        WakeWord(surface="desktop")
    assert bad.value.code == "BAD_SURFACE"
    with pytest.raises(Refuse) as empty:
        WakeWord(surfaces=cast(tuple[str, ...], ()))
    assert empty.value.code == "EMPTY_ALLOW"
    with pytest.raises(Refuse) as kind:
        WakeWord(surfaces=cast(tuple[str, ...], ["cli"]))
    assert kind.value.code == "BAD_ALLOW"
    with pytest.raises(Refuse) as duplicate:
        WakeWord(surfaces=("cli", "tui", "cli"))
    assert duplicate.value.code == "DUPLICATE"
    with pytest.raises(Refuse) as denied:
        WakeWord(surface="tui", surfaces=("cli",))
    assert denied.value.code == "SURFACE_DENIED"
    pinned = WakeWord(surface="cli", surfaces=("cli", "tui"), capture="local")
    pinned.enable(True)
    heard = pinned.hear(0.6, 8)
    assert isinstance(heard, SessionRequest)
    assert heard.surface == "cli"
    assert heard.capture == "local"
    assert heard.opens_device is False


def test_modes_and_engines() -> None:
    with pytest.raises(Refuse) as capture:
        WakeWord(capture="mic")
    assert capture.value.code == "BAD_CAPTURE"
    with pytest.raises(Refuse) as provider:
        WakeWord(provider="whisper")
    assert provider.value.code == "BAD_PROVIDER"
    with pytest.raises(Refuse) as cloud_engine:
        WakeWord(phrase="hey cosmos", provider="cloud")
    assert cloud_engine.value.code == "CLOUD_WAKE"
    with pytest.raises(Refuse) as platform:
        WakeWord(platform="windows")
    assert platform.value.code == "BAD_PLATFORM"
    for host in ("windows-arm64", "macos-x64", "linux-arm64"):
        with pytest.raises(Refuse) as unsupported:
            WakeWord(provider="openwakeword", platform=host)
        assert unsupported.value.code == "UNSUPPORTED_ENGINE"
    assert WakeWord(platform="windows-arm64").status().engine == "sherpa"
    assert WakeWord(platform="macos-x64").status().engine == "sherpa"
    assert WakeWord(platform="linux-arm64").status().engine == "sherpa"
    assert WakeWord(platform="macos-arm64").status().engine == "openwakeword"
    assert WakeWord(platform="windows-x64").status().engine == "openwakeword"
    explicit = WakeWord(provider="sherpa", platform="linux-x64")
    assert explicit.status().provider == "sherpa"
    assert explicit.status().engine == "sherpa"
    client = WakeWord(capture="client", surface="gui")
    client.enable(True)
    heard = client.hear(0.8, 9)
    assert isinstance(heard, SessionRequest)
    assert heard.capture == "client"
    assert heard.surface == "gui"
    assert heard.opens_device is False


def test_secrets_and_porcupine() -> None:
    raw = "sk-livekeyvalue"
    with pytest.raises(Refuse) as missing:
        WakeWord(provider="porcupine", credential_id="")
    assert missing.value.code == "MISSING_CRED"
    with pytest.raises(Refuse) as secret:
        WakeWord(provider="porcupine", credential_id=raw)
    assert secret.value.code == "SECRET_SHAPE"
    assert raw not in str(secret.value)
    with pytest.raises(Refuse) as phrase:
        WakeWord(phrase="token=supersecret")
    assert phrase.value.code == "SECRET_SHAPE"
    with pytest.raises(Refuse) as shaped:
        WakeWord(provider="porcupine", credential_id=" pico")
    assert shaped.value.code == "BAD_CRED"
    gate = WakeWord(provider="porcupine", credential_id="pico-1", platform="macos-x64")
    assert gate.status().engine == "porcupine"
    assert gate.status().detector == "jarvis"
    assert gate.status().cred_set is True
    assert "pico-1" not in repr(gate)
    assert secret_shape(repr(gate)) is False
    with pytest.raises(Refuse) as cloud:
        gate.enable(False)
    assert cloud.value.code == "CLOUD_WAKE"
    gate.enable(True)
    heard = gate.hear(0.75, 2)
    assert isinstance(heard, SessionRequest)
    assert heard.engine == "porcupine"
    assert heard.opens_device is False
    assert secret_shape(repr(heard)) is False


def test_models_stay_in_the_grant() -> None:
    with pytest.raises(Refuse) as need:
        WakeWord(phrase="hey coder", provider="openwakeword", platform="linux-x64")
    assert need.value.code == "NEED_MODEL"
    root = Path(__file__).resolve().parent / "grant"
    model = root / "computer.tflite"
    jail = PathJail([str(root)])
    with pytest.raises(Refuse) as naked:
        WakeWord(
            phrase="hey coder",
            provider="openwakeword",
            model_path=str(model),
            jail=None,
        )
    assert naked.value.code == "NO_GRANT"
    with pytest.raises(Refuse) as wrong:
        WakeWord(
            phrase="hey coder",
            provider="openwakeword",
            model_path=str(model),
            jail=cast(PathJail, "nope"),
        )
    assert wrong.value.code == "BAD_GRANT"
    with pytest.raises(Refuse) as suffix:
        WakeWord(
            provider="openwakeword",
            model_path=str(root / "computer.txt"),
            jail=jail,
        )
    assert suffix.value.code == "BAD_MODEL"
    with pytest.raises(Refuse) as dotted:
        WakeWord(
            phrase="hey coder",
            provider="openwakeword",
            model_path=str(root / ".." / "computer.tflite"),
            jail=jail,
        )
    assert dotted.value.code == "DOTDOT"
    with pytest.raises(Refuse) as outside:
        WakeWord(
            phrase="hey coder",
            provider="openwakeword",
            model_path=str(root.parent / "computer.tflite"),
            jail=jail,
        )
    assert outside.value.code == "OUTSIDE_GRANT"
    with pytest.raises(Refuse) as relative:
        WakeWord(
            phrase="hey coder",
            provider="openwakeword",
            model_path="computer.tflite",
            jail=jail,
        )
    assert relative.value.code == "RELATIVE_PATH"
    custom = WakeWord(
        phrase="hey coder",
        provider="openwakeword",
        platform="macos-arm64",
        model_path=str(model),
        jail=jail,
    )
    assert custom.status().detector == "computer.tflite"
    custom.enable(True)
    heard = custom.hear(0.91, 5)
    assert isinstance(heard, SessionRequest)
    assert heard.phrase == "hey coder"
    assert heard.detector == "computer.tflite"
    assert heard.engine == "openwakeword"
    assert heard.opens_device is False
    spoken = WakeWord(phrase="hey coder", provider="sherpa", platform="windows-arm64")
    spoken.enable(True)
    sherpa_hit = spoken.hear(0.5, 3)
    assert isinstance(sherpa_hit, SessionRequest)
    assert sherpa_hit.detector == "hey coder"
    assert sherpa_hit.engine == "sherpa"
    assert sherpa_hit.opens_device is False


def test_malformed_sample_is_not_relabeled() -> None:
    gate = WakeWord()
    gate.enable(True)
    assert isinstance(gate.hear(0.8, 10), SessionRequest)
    for sample in (True, "0.9", None, float("nan"), 10**400, -1):
        with pytest.raises(Refuse) as caught:
            gate.hear(sample, 11)
        assert caught.value.code == "BAD_SCORE"
    with pytest.raises(Refuse) as rewound:
        gate.hear(float("inf"), 9)
    assert rewound.value.code == "BAD_SCORE"
    with pytest.raises(Refuse) as clock:
        gate.hear(0.9, 1.5)
    assert clock.value.code == "NOT_INT"
    assert gate.status().last_hit_at == 10
    with pytest.raises(Refuse) as cooling:
        gate.hear(0.8, 11)
    assert cooling.value.code == "COOLDOWN"
    assert isinstance(gate.hear(0.8, 12), SessionRequest)


def test_model_path_shapes() -> None:
    root = Path(__file__).resolve().parent / "grant"
    jail = PathJail([str(root)])
    cases = (
        ("file:///wake/computer.tflite", "FILE_URL"),
        (str(root) + "\\%2e%2e\\computer.tflite", "ENCODED_DOTDOT"),
        ("\\\\nas\\wake\\computer.tflite", "UNC"),
        ("C:\\", "DRIVE_ROOT"),
        ("C:computer.tflite", "DRIVE_RELATIVE"),
        ("C:\\wake:word.tflite", "ALT_STREAM"),
        (str(root) + "\\computer.tflite.", "TRAILING_DOT"),
    )
    for raw, code in cases:
        with pytest.raises(Refuse) as caught:
            WakeWord(
                phrase="hey coder",
                provider="openwakeword",
                model_path=raw,
                jail=jail,
            )
        assert caught.value.code == code


def _arm(story: tuple[Arm, SessionRequest, WakeStatus, str]) -> Arm:
    return story[0]


def _session(story: tuple[Arm, SessionRequest, WakeStatus, str]) -> SessionRequest:
    return story[1]


def _status(story: tuple[Arm, SessionRequest, WakeStatus, str]) -> WakeStatus:
    return story[2]


def _cloud_code(story: tuple[Arm, SessionRequest, WakeStatus, str]) -> str:
    return story[3]


def test_example_wake_word() -> None:
    """Ada's desk card says hey cosmos. The studio light arms on the device."""

    def run() -> tuple[Arm, SessionRequest, WakeStatus, str]:
        card = "hey cosmos"
        light = WakeWord(
            phrase=card,
            provider="sherpa",
            surface="cli",
            capture="local",
        )
        armed = light.enable(True)
        session = light.hear(0.86, 1_726_531_200)
        assert isinstance(session, SessionRequest)
        note = "UNCAUGHT"
        try:
            WakeWord(phrase=card, provider="cloud", surface="cli", capture="local")
        except Refuse as refused:
            note = refused.code
        return armed, session, light.status(), note

    first = run()
    second = run()
    assert first == second
    armed = _arm(first)
    session = _session(first)
    status = _status(first)
    assert armed.phrase == "hey cosmos"
    assert armed.on_device is True
    assert armed.opens_device is False
    assert session.phrase == "hey cosmos"
    assert session.kind == "session-request"
    assert session.engine == "sherpa"
    assert session.heard_at == 1_726_531_200
    assert session.opens_device is False
    assert session.start_new_session is True
    assert status.phrase == "hey cosmos"
    assert status.armed is True
    assert status.on_device is True
    assert status.opens_device is False
    assert status.last_hit_at == 1_726_531_200
    assert _cloud_code(first) == "CLOUD_WAKE"


def test_same_inputs_match_and_source_stays_closed() -> None:
    def once() -> SessionRequest:
        gate = WakeWord(capture="local", surface="tui")
        gate.enable(True)
        assert gate.hear(0.2, 1) == MISS
        heard = gate.hear(0.64, 7)
        assert isinstance(heard, SessionRequest)
        return heard

    assert once() == once()
    text = Path(__file__).with_name("wake_word.py").read_text(encoding="utf-8")
    for banned in (
        "socket",
        "subprocess",
        "sounddevice",
        "urllib",
        "requests",
        "pickle",
        "eval(",
        "exec(",
        "compile(",
        "sys.platform",
    ):
        assert banned not in text
