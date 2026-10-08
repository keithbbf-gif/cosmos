"""On-device wake gate. A hit is a session-request descriptor. No microphone."""

from __future__ import annotations

from dataclasses import dataclass

from cosmos_hermes import PathJail, Refuse, bound_int, bound_text, secret_shape

SCHEMA = "cosmos-hermes-wake_word/1"
DEFAULT_PHRASE = "hey hermes"
MISS = "MISS"
THRESHOLD = 0.5
MIN_COOLDOWN_S = 2
MAX_COOLDOWN_S = 120
_COOLDOWN_DOMAIN = 1_000_000
_MAX_NOW = 4_000_000_000
_PHRASE_LIMIT = 64
_PATH_LIMIT = 4096
_LABEL_LIMIT = 32
_CRED_LIMIT = 64
_UNIT_INTS = frozenset((0, 1))
_UNREAL = frozenset((float("inf"), float("-inf")))
_DEFAULT_PLATFORM = "linux-x64"
_DEFAULT_SURFACES = ("auto", "cli", "tui", "gui")
_SURFACES = frozenset(_DEFAULT_SURFACES)
_CAPTURES = frozenset({"auto", "local", "client"})
_PROVIDERS = frozenset({"auto", "openwakeword", "sherpa", "porcupine"})
_CLOUD_ENGINES = frozenset({"cloud"})
_REMOTE = frozenset(
    {
        "gateway",
        "telegram",
        "discord",
        "slack",
        "whatsapp",
        "signal",
        "matrix",
        "email",
        "sms",
        "imessage",
        "bot",
    }
)
_AUTO_ENGINE = {
    "windows-x64": "openwakeword",
    "windows-arm64": "sherpa",
    "macos-x64": "sherpa",
    "macos-arm64": "openwakeword",
    "linux-x64": "openwakeword",
    "linux-arm64": "sherpa",
}
_OPENWAKEWORD_OK = frozenset({"windows-x64", "macos-arm64", "linux-x64"})
_PHRASE_MARKS = frozenset(" '-")
_CRED_MARKS = frozenset("._-")


@dataclass(frozen=True, slots=True)
class Cooldown:
    """Caller request beside the policy cooldown that actually applies."""

    requested: int
    effective: int


@dataclass(frozen=True, slots=True)
class Arm:
    """Logical arming. `opens_device` stays false."""

    schema: str
    phrase: str
    on_device: bool
    opens_device: bool
    requested: int
    effective: int
    provider: str
    engine: str
    surface: str
    capture: str


@dataclass(frozen=True, slots=True)
class Disarm:
    """Listener is dark. `opens_device` stays false."""

    schema: str
    armed: bool
    opens_device: bool


@dataclass(frozen=True, slots=True)
class SessionRequest:
    """Frozen descriptor a later voice service would run. No device is opened."""

    schema: str
    kind: str
    phrase: str
    detector: str
    surface: str
    capture: str
    provider: str
    engine: str
    heard_at: int
    score: float
    start_new_session: bool
    opens_device: bool


@dataclass(frozen=True, slots=True)
class WakeStatus:
    """Readable gate state. `opens_device` stays false."""

    schema: str
    armed: bool
    on_device: bool
    opens_device: bool
    phrase: str
    detector: str
    surface: str
    capture: str
    provider: str
    engine: str
    platform: str
    requested: int
    effective: int
    threshold: float
    start_new_session: bool
    cred_set: bool
    last_hit_at: int | None


def _labeled(value: object, allowed: frozenset[str], code: str) -> str:
    text = bound_text(value, _LABEL_LIMIT)
    if text not in allowed:
        raise Refuse(code)
    return text


def _surface(value: object) -> str:
    text = bound_text(value, _LABEL_LIMIT)
    if text in _REMOTE:
        raise Refuse("NOT_LOCAL")
    if text not in _SURFACES:
        raise Refuse("BAD_SURFACE")
    return text


def _allow(value: object) -> tuple[str, ...]:
    if value is None:
        return _DEFAULT_SURFACES
    if isinstance(value, str) or not isinstance(value, tuple):
        raise Refuse("BAD_ALLOW")
    if len(value) == 0:
        raise Refuse("EMPTY_ALLOW")
    if len(value) > len(_SURFACES):
        raise Refuse("OVERSIZE", str(len(_SURFACES)))
    cleaned: list[str] = []
    seen: set[str] = set()
    for item in value:
        name = _surface(item)
        if name in seen:
            raise Refuse("DUPLICATE")
        seen.add(name)
        cleaned.append(name)
    return tuple(cleaned)


def _phrase(value: object) -> str:
    text = bound_text(value, _PHRASE_LIMIT)
    if text.strip() == "":
        raise Refuse("EMPTY_PHRASE")
    if secret_shape(text):
        raise Refuse("SECRET_SHAPE")
    if text != text.strip() or len(text) < 2:
        raise Refuse("BAD_PHRASE")
    for ch in text:
        if ch.isascii() and (ch.islower() or ch.isdigit() or ch in _PHRASE_MARKS):
            continue
        raise Refuse("BAD_PHRASE")
    if not any("a" <= ch <= "z" for ch in text):
        raise Refuse("BAD_PHRASE")
    return text


def _cooldown_of(requested: object) -> tuple[int, int]:
    raw = bound_int(requested, 0, _COOLDOWN_DOMAIN)
    if raw < MIN_COOLDOWN_S:
        return raw, MIN_COOLDOWN_S
    if raw > MAX_COOLDOWN_S:
        return raw, MAX_COOLDOWN_S
    return raw, raw


def _flag(value: object) -> bool:
    if not isinstance(value, bool):
        raise Refuse("NOT_BOOL")
    return value


def _cred(value: object, required: bool) -> str:
    text = bound_text(value, _CRED_LIMIT)
    if text == "":
        if required:
            raise Refuse("MISSING_CRED")
        return ""
    if secret_shape(text):
        raise Refuse("SECRET_SHAPE")
    if text[0] in _CRED_MARKS or not all(
        ch.isascii() and (ch.isalnum() or ch in _CRED_MARKS) for ch in text
    ):
        raise Refuse("BAD_CRED")
    return text


def _provider(value: object) -> str:
    text = bound_text(value, _LABEL_LIMIT)
    if text in _CLOUD_ENGINES:
        raise Refuse("CLOUD_WAKE")
    if text not in _PROVIDERS:
        raise Refuse("BAD_PROVIDER")
    return text


def _engine(provider: str, platform: str) -> str:
    if platform not in _AUTO_ENGINE:
        raise Refuse("BAD_PLATFORM")
    if provider == "auto":
        return _AUTO_ENGINE[platform]
    if provider == "openwakeword" and platform not in _OPENWAKEWORD_OK:
        raise Refuse("UNSUPPORTED_ENGINE", platform)
    return provider


def _score(value: object) -> float:
    if isinstance(value, float):
        if value != value or value in _UNREAL:
            raise Refuse("BAD_SCORE")
        if value < 0.0 or value > 1.0:
            raise Refuse("BAD_SCORE")
        return value
    if isinstance(value, bool) or not isinstance(value, int):
        raise Refuse("BAD_SCORE")
    if value not in _UNIT_INTS:
        raise Refuse("BAD_SCORE")
    return float(value)


def _detector(engine: str, phrase: str, model: str) -> str:
    if model != "":
        slash = max(model.rfind("/"), model.rfind("\\"))
        return model[slash + 1 :]
    if engine == "porcupine":
        return "jarvis"
    if engine == "openwakeword":
        return "hey_hermes"
    return phrase


def _model(engine: str, phrase: str, model_path: object, jail: object) -> str:
    text = bound_text(model_path, _PATH_LIMIT)
    if secret_shape(text):
        raise Refuse("SECRET_SHAPE")
    if jail is not None and not isinstance(jail, PathJail):
        raise Refuse("BAD_GRANT")
    if text == "":
        if engine == "openwakeword" and phrase != DEFAULT_PHRASE:
            raise Refuse("NEED_MODEL")
        return ""
    if not isinstance(jail, PathJail):
        raise Refuse("NO_GRANT")
    resolved = jail.contain(text)
    suffix = resolved.suffix.lower()
    if engine == "openwakeword" and suffix == ".tflite":
        return str(resolved)
    if engine == "porcupine" and suffix == ".ppn":
        return str(resolved)
    raise Refuse("BAD_MODEL")


class WakeWord:
    """Score gate for one wake phrase. Cloud engines and the microphone stay closed."""

    __slots__ = (
        "_phrase",
        "_detector",
        "_armed",
        "_requested",
        "_effective",
        "_surface",
        "_surfaces",
        "_capture",
        "_provider",
        "_platform",
        "_engine",
        "_start_new",
        "_cred",
        "_model",
        "_last_hit",
    )

    _phrase: str
    _detector: str
    _armed: bool
    _requested: int
    _effective: int
    _surface: str
    _surfaces: tuple[str, ...]
    _capture: str
    _provider: str
    _platform: str
    _engine: str
    _start_new: bool
    _cred: str
    _model: str
    _last_hit: int | None

    def __init__(
        self,
        *,
        phrase: str = DEFAULT_PHRASE,
        cooldown_s: int = MIN_COOLDOWN_S,
        surface: str = "auto",
        surfaces: tuple[str, ...] | None = None,
        capture: str = "auto",
        provider: str = "auto",
        platform: str = _DEFAULT_PLATFORM,
        start_new_session: bool = True,
        credential_id: str = "",
        model_path: str = "",
        jail: PathJail | None = None,
    ) -> None:
        chosen_phrase = _phrase(phrase)
        requested, effective = _cooldown_of(cooldown_s)
        chosen_surface = _surface(surface)
        chosen_surfaces = _allow(surfaces)
        if chosen_surface not in chosen_surfaces:
            raise Refuse("SURFACE_DENIED")
        chosen_capture = _labeled(capture, _CAPTURES, "BAD_CAPTURE")
        chosen_provider = _provider(provider)
        chosen_platform = _labeled(platform, frozenset(_AUTO_ENGINE), "BAD_PLATFORM")
        chosen_engine = _engine(chosen_provider, chosen_platform)
        chosen_cred = _cred(credential_id, required=chosen_engine == "porcupine")
        chosen_model = _model(chosen_engine, chosen_phrase, model_path, jail)
        self._phrase = chosen_phrase
        self._detector = _detector(chosen_engine, chosen_phrase, chosen_model)
        self._armed = False
        self._requested = requested
        self._effective = effective
        self._surface = chosen_surface
        self._surfaces = chosen_surfaces
        self._capture = chosen_capture
        self._provider = chosen_provider
        self._platform = chosen_platform
        self._engine = chosen_engine
        self._start_new = _flag(start_new_session)
        self._cred = chosen_cred
        self._model = chosen_model
        self._last_hit = None

    def __repr__(self) -> str:
        return (
            f"WakeWord(phrase={self._phrase!r}, armed={self._armed}, "
            f"provider={self._provider!r}, engine={self._engine!r}, "
            f"effective={self._effective})"
        )

    @property
    def phrase(self) -> str:
        return self._phrase

    @property
    def cooldown(self) -> Cooldown:
        return Cooldown(requested=self._requested, effective=self._effective)

    def set_cooldown(self, requested: object) -> Cooldown:
        """Store `requested`. Effective stays inside the 2..120 policy."""
        self._requested, self._effective = _cooldown_of(requested)
        return self.cooldown

    def status(self) -> WakeStatus:
        armed = self._armed
        return WakeStatus(
            schema=SCHEMA,
            armed=armed,
            on_device=armed,
            opens_device=False,
            phrase=self._phrase,
            detector=self._detector,
            surface=self._surface,
            capture=self._capture,
            provider=self._provider,
            engine=self._engine,
            platform=self._platform,
            requested=self._requested,
            effective=self._effective,
            threshold=THRESHOLD,
            start_new_session=self._start_new,
            cred_set=self._cred != "",
            last_hit_at=self._last_hit,
        )

    def enable(self, on_device: object) -> Arm:
        """Arm when `on_device` is true. False raises `CLOUD_WAKE`."""
        if not isinstance(on_device, bool):
            raise Refuse("NOT_BOOL")
        if not on_device:
            raise Refuse("CLOUD_WAKE")
        self._armed = True
        return Arm(
            schema=SCHEMA,
            phrase=self._phrase,
            on_device=True,
            opens_device=False,
            requested=self._requested,
            effective=self._effective,
            provider=self._provider,
            engine=self._engine,
            surface=self._surface,
            capture=self._capture,
        )

    def disable(self) -> Disarm:
        """Drop arming. A prior hit still anchors the cooldown."""
        self._armed = False
        return Disarm(schema=SCHEMA, armed=False, opens_device=False)

    def hear(self, score: object, now: object) -> str | SessionRequest:
        """Return `MISS` under 0.5, or a frozen session request at or above it."""
        if not self._armed:
            raise Refuse("NOT_ARMED")
        moment = bound_int(now, 0, _MAX_NOW)
        number = _score(score)
        if self._last_hit is not None:
            if moment < self._last_hit:
                raise Refuse("REWOUND")
            if moment < self._last_hit + self._effective:
                raise Refuse("COOLDOWN")
        if number < THRESHOLD:
            return MISS
        self._last_hit = moment
        return SessionRequest(
            schema=SCHEMA,
            kind="session-request",
            phrase=self._phrase,
            detector=self._detector,
            surface=self._surface,
            capture=self._capture,
            provider=self._provider,
            engine=self._engine,
            heard_at=moment,
            score=number,
            start_new_session=self._start_new,
            opens_device=False,
        )


__all__ = [
    "SCHEMA",
    "DEFAULT_PHRASE",
    "MISS",
    "THRESHOLD",
    "MIN_COOLDOWN_S",
    "MAX_COOLDOWN_S",
    "Arm",
    "Cooldown",
    "Disarm",
    "SessionRequest",
    "WakeStatus",
    "WakeWord",
]
