"""Text-to-speech descriptors for the COSMOS voice rail.

``synthesize`` returns a frozen script. It does not play audio.
"""

from __future__ import annotations

import math
import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import cast

from cosmos_hermes import Refuse, bound_int, bound_text, const_eq, redact, secret_shape

SCHEMA = "cosmos-hermes-tts/1"
TEXT_CAP = 4000
_NAME_CAP = 32
_KEY_CAP = 64
_ID_CAP = 128
_VOICE_CAP = 128
_DEPTH_CAP = 6
_WIDTH_CAP = 64
_SPEED_UNIT = 1000

_CRED = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_PATH_MARK = re.compile(r"\.\.|[/\\:]")
_REGIONS = frozenset({"global", "cn"})
_CAP_KEYS = ("cap", "max_text_length")
_SECRET_KEY = "api_key"
_EXEC_KEYS = frozenset(
    {
        "base_url",
        "command",
        "endpoint",
        "env_passthrough",
        "input_path",
        "output_path",
        "persona_prompt_file",
        "ref_audio",
        "release_command",
        "url",
        "voices_dir",
        "warm_command",
    }
)
_SPEED_REMAP = frozenset({"NOT_INT", "OUT_OF_RANGE"})


@dataclass(frozen=True, slots=True)
class _Profile:
    """One allowlisted provider. Speeds are thousandths of 1.0."""

    audio_format: str
    voice: str
    speed_lo: int
    speed_hi: int
    local: bool = False
    cloud: bool = False
    minimax: bool = False


_PROFILES: dict[str, _Profile] = {
    "edge": _Profile("mp3", "en-US-AriaNeural", 500, 2000, local=True),
    "elevenlabs": _Profile("opus", "pNInz6obpgDQGcFmaJgB", 500, 2000, cloud=True),
    "openai": _Profile("opus", "alloy", 250, 4000, cloud=True),
    "minimax": _Profile(
        "mp3",
        "English_expressive_narrator",
        500,
        2000,
        cloud=True,
        minimax=True,
    ),
    "mistral": _Profile(
        "opus",
        "c69964a6-ab8b-4f8a-9465-ec0925096ec8",
        500,
        2000,
        cloud=True,
    ),
    "gemini": _Profile("pcm", "Kore", 500, 2000, cloud=True),
    "xai": _Profile("mp3", "eve", 700, 1500, cloud=True),
    "neutts": _Profile("wav", "", 500, 2000, local=True),
    "kitten": _Profile("wav", "Jasper", 500, 2000, local=True),
    "piper": _Profile("wav", "en_US-lessac-medium", 500, 2000, local=True),
    "command": _Profile("mp3", "", 500, 2000),
}

PROVIDERS: tuple[str, ...] = tuple(_PROFILES)


def _profile(name: str) -> _Profile:
    found = _PROFILES.get(name)
    if found is None:
        raise Refuse("UNKNOWN_PROVIDER")
    return found


def _checked_speed(milli: object, lo: int, hi: int) -> int:
    if isinstance(milli, bool):
        raise Refuse("BAD_SPEED")
    try:
        return bound_int(milli, lo, hi)
    except Refuse as refusal:
        if refusal.code in _SPEED_REMAP:
            raise Refuse("BAD_SPEED") from None
        raise


def _policy_cap(fields: Mapping[str, object]) -> int:
    """Record TEXT_CAP. A higher caller cap is not applied. Bool is not an int."""
    for key in _CAP_KEYS:
        asked = fields.get(key)
        if isinstance(asked, bool) or not isinstance(asked, int):
            continue
        if asked > TEXT_CAP:
            return TEXT_CAP
    return TEXT_CAP


def _refuse_exec(item: object, depth: int) -> None:
    if item is None:
        return
    if isinstance(item, str):
        if item == "":
            return
        checked = bound_text(item, TEXT_CAP)
        if secret_shape(checked):
            raise Refuse("SECRET")
        raise Refuse("BAD_FIELD")
    if isinstance(item, (Mapping, list, tuple)):
        _scan(item, depth)
    raise Refuse("BAD_FIELD")


def _scan(value: object, depth: int) -> None:
    if isinstance(value, str):
        checked = bound_text(value, TEXT_CAP)
        if secret_shape(checked):
            raise Refuse("SECRET")
        return
    if value is None or isinstance(value, (bool, int, float)):
        return
    if isinstance(value, Mapping):
        _scan_mapping(cast(Mapping[object, object], value), depth)
        return
    if isinstance(value, list):
        _scan_seq(cast(list[object], value), depth)
        return
    if isinstance(value, tuple):
        _scan_seq(tuple(value), depth)
        return
    raise Refuse("BAD_FIELD")


def _scan_mapping(value: Mapping[object, object], depth: int) -> None:
    if depth > _DEPTH_CAP:
        raise Refuse("TOO_DEEP")
    if len(value) > _WIDTH_CAP:
        raise Refuse("TOO_WIDE")
    for key, item in value.items():
        if not isinstance(key, str):
            raise Refuse("BAD_FIELD")
        checked = bound_text(key, _KEY_CAP)
        if secret_shape(checked):
            raise Refuse("SECRET")
        folded = checked.casefold()
        if folded == _SECRET_KEY:
            raise Refuse("SECRET")
        if folded in _EXEC_KEYS:
            _refuse_exec(item, depth + 1)
            continue
        _scan(item, depth + 1)


def _scan_seq(value: tuple[object, ...] | list[object], depth: int) -> None:
    if depth > _DEPTH_CAP:
        raise Refuse("TOO_DEEP")
    if len(value) > _WIDTH_CAP:
        raise Refuse("TOO_WIDE")
    for item in value:
        _scan(item, depth + 1)


def _scan_composite(value: object) -> None:
    if isinstance(value, (Mapping, list, tuple)):
        _scan(value, 0)


def _credential(fields: Mapping[str, object]) -> str:
    if "credential_id" not in fields or fields["credential_id"] is None:
        return ""
    raw = fields["credential_id"]
    if not isinstance(raw, str):
        raise Refuse("BAD_CREDENTIAL")
    if raw == "":
        return ""
    token = bound_text(raw, _ID_CAP)
    if secret_shape(token):
        raise Refuse("SECRET")
    if _CRED.fullmatch(token) is None:
        raise Refuse("BAD_CREDENTIAL")
    return token


def _region(profile: _Profile, fields: Mapping[str, object]) -> str:
    """MiniMax region is global or cn. Other providers take no region."""
    if "region" not in fields or fields["region"] is None:
        if profile.minimax:
            return "global"
        return ""
    if not profile.minimax:
        raise Refuse("BAD_REGION")
    raw = fields["region"]
    if not isinstance(raw, str):
        raise Refuse("BAD_REGION")
    token = bound_text(raw, 16)
    if token not in _REGIONS:
        raise Refuse("BAD_REGION")
    return token


def _voice(profile: _Profile, fields: Mapping[str, object]) -> str:
    if "voice" not in fields or fields["voice"] is None or fields["voice"] == "":
        return profile.voice
    raw = fields["voice"]
    if not isinstance(raw, str):
        raise Refuse("BAD_VOICE")
    voice = bound_text(raw, _VOICE_CAP)
    if secret_shape(voice):
        raise Refuse("SECRET")
    if _PATH_MARK.search(voice) is not None:
        raise Refuse("BAD_VOICE")
    return voice


def _speed(profile: _Profile, fields: Mapping[str, object]) -> int:
    """Resolve a speed multiplier to thousandths inside the provider window."""
    if "speed" not in fields or fields["speed"] is None:
        return _SPEED_UNIT
    raw = fields["speed"]
    if isinstance(raw, bool) or not isinstance(raw, (int, float)):
        raise Refuse("BAD_SPEED")
    if isinstance(raw, int):
        milli = raw * _SPEED_UNIT
    else:
        number = float(raw)
        if not math.isfinite(number):
            raise Refuse("BAD_SPEED")
        scaled = number * float(_SPEED_UNIT)
        milli = round(scaled)
        if abs(scaled - float(milli)) > 1e-4:
            raise Refuse("BAD_SPEED")
    return _checked_speed(milli, profile.speed_lo, profile.speed_hi)


def _script(text: object) -> str:
    raw = bound_text(text, TEXT_CAP)
    if raw != redact(raw):
        raise Refuse("SECRET")
    if raw.strip() == "":
        raise Refuse("EMPTY")
    return raw


def _validate(record: AudioRequest) -> None:
    provider = bound_text(record.provider, _NAME_CAP)
    if secret_shape(provider):
        raise Refuse("SECRET")
    profile = _profile(provider)
    if isinstance(record.cap, bool) or not isinstance(record.cap, int) or record.cap != TEXT_CAP:
        raise Refuse("BAD_LIMIT")
    script = bound_text(record.text, TEXT_CAP)
    if script.strip() == "":
        raise Refuse("EMPTY")
    if script != redact(script):
        raise Refuse("SECRET")
    if not isinstance(record.credential_id, str):
        raise Refuse("BAD_CREDENTIAL")
    if secret_shape(record.credential_id):
        raise Refuse("SECRET")
    if record.credential_id == "":
        if profile.cloud:
            raise Refuse("MISSING_CREDENTIAL")
    else:
        token = bound_text(record.credential_id, _ID_CAP)
        if _CRED.fullmatch(token) is None:
            raise Refuse("BAD_CREDENTIAL")
    if not isinstance(record.region, str):
        raise Refuse("BAD_REGION")
    if profile.minimax:
        if record.region not in _REGIONS:
            raise Refuse("BAD_REGION")
    elif record.region != "":
        raise Refuse("BAD_REGION")
    if not isinstance(record.audio_format, str) or record.audio_format != profile.audio_format:
        raise Refuse("BAD_FORMAT")
    if not isinstance(record.local, bool) or record.local is not profile.local:
        raise Refuse("BAD_FIELD")
    if not isinstance(record.voice, str):
        raise Refuse("BAD_VOICE")
    voice = bound_text(record.voice, _VOICE_CAP)
    if secret_shape(voice):
        raise Refuse("SECRET")
    if voice != "" and _PATH_MARK.search(voice) is not None:
        raise Refuse("BAD_VOICE")
    _checked_speed(record.speed_milli, profile.speed_lo, profile.speed_hi)
    if not isinstance(record.command, str) or record.command != "":
        raise Refuse("BAD_FIELD")


@dataclass(frozen=True, slots=True)
class AudioRequest:
    """Frozen speech descriptor. ``text`` is redacted. ``command`` stays empty."""

    provider: str
    text: str
    credential_id: str
    cap: int
    region: str
    audio_format: str
    local: bool
    voice: str
    speed_milli: int
    command: str

    def __post_init__(self) -> None:
        _validate(self)


class Tts:
    """One selected provider. The rail returns a descriptor and stops."""

    __slots__ = ("_provider", "_credential_id", "_region", "_voice", "_speed_milli")

    _provider: str | None
    _credential_id: str
    _region: str
    _voice: str
    _speed_milli: int

    def __init__(self) -> None:
        self._provider = None
        self._credential_id = ""
        self._region = ""
        self._voice = ""
        self._speed_milli = _SPEED_UNIT

    def select(self, name: object, **fields: object) -> str:
        """Bind an allowlisted provider id."""
        _scan_composite(name)
        _scan(fields, 0)
        provider = bound_text(name, _NAME_CAP)
        if secret_shape(provider):
            raise Refuse("SECRET")
        profile = _profile(provider)
        credential_id = _credential(fields)
        if profile.cloud and credential_id == "":
            raise Refuse("MISSING_CREDENTIAL")
        region = _region(profile, fields)
        voice = _voice(profile, fields)
        speed_milli = _speed(profile, fields)
        self._provider = provider
        self._credential_id = credential_id
        self._region = region
        self._voice = voice
        self._speed_milli = speed_milli
        return provider

    def synthesize(self, text: object, **fields: object) -> AudioRequest:
        """Return a redacted request. Malformed text refuses before the selection check."""
        _scan(fields, 0)
        _scan_composite(text)
        script = _script(text)
        provider = self._provider
        if provider is None:
            raise Refuse("NO_PROVIDER")
        profile = _profile(provider)
        if "credential_id" in fields and fields["credential_id"] is not None:
            presented = _credential(fields)
            if not const_eq(presented, self._credential_id):
                raise Refuse("BAD_CREDENTIAL")
        voice = _voice(profile, fields) if "voice" in fields else self._voice
        speed_milli = _speed(profile, fields) if "speed" in fields else self._speed_milli
        region = _region(profile, fields) if "region" in fields else self._region
        return AudioRequest(
            provider=provider,
            text=script,
            credential_id=self._credential_id,
            cap=_policy_cap(fields),
            region=region,
            audio_format=profile.audio_format,
            local=profile.local,
            voice=voice,
            speed_milli=speed_milli,
            command="",
        )


__all__ = [
    "PROVIDERS",
    "SCHEMA",
    "TEXT_CAP",
    "AudioRequest",
    "Tts",
]
