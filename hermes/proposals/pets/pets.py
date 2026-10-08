"""Cosmetic pet lines. A pet does not start a command."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
from types import MappingProxyType
from typing import Final

from cosmos_hermes import Refuse, bound_text, secret_shape

SCHEMA: Final = "cosmos-hermes-pets/1"
MOODS: Final = frozenset({"idle", "run", "sleep"})
SCALE_FLOOR: Final = 100
SCALE_CAP: Final = 3000
SCALE_DEFAULT: Final = 330
ROSTER_CAP: Final = 8
SPRITE_MAX: Final = 24

_MOOD_LIMIT: Final = 16
_KEY_LIMIT: Final = 32
_WALK_TEXT: Final = 256
_KEY_SCAN: Final = 16
_SEQ_CAP: Final = 32
_DEPTH: Final = 4
_SCALE_DOMAIN: Final = 1_000_000
_CAP_DOMAIN: Final = 1_000_000
_FORBIDDEN: Final = frozenset({"command", "exec", "shell", "url"})
_ALLOWED: Final = frozenset({"enabled", "mood", "scale", "sprite"})
_FIELD_TEXT: Final = frozenset({"mood", "sprite"})
_ACTIVITIES: Final[dict[str, str]] = {
    "idle": "idle",
    "nothing": "idle",
    "waiting": "idle",
    "run": "run",
    "tool": "run",
    "inflight": "run",
    "sleep": "sleep",
}
_SPRITE_RE: Final = re.compile(r"^[a-z0-9-]{1,24}$")


def _freeze(raw: dict[str, dict[str, str]]) -> Mapping[str, Mapping[str, str]]:
    locked: dict[str, Mapping[str, str]] = {}
    for name, poses in raw.items():
        locked[name] = MappingProxyType(poses)
    return MappingProxyType(locked)


_CATALOG: Final = _freeze(
    {
        "ember": {
            "idle": "ember waits by the card, idle",
            "run": "ember crosses the note",
            "sleep": "ember rests under the lamp",
        },
        "boba": {
            "idle": "boba sits beside the card",
            "run": "boba rolls along the desk",
            "sleep": "boba cools by the cup",
        },
        "pebble": {
            "idle": "pebble stays on the card",
            "run": "pebble hops toward the note",
            "sleep": "pebble stills in the shade",
        },
        "moss": {
            "idle": "moss holds on the stone",
            "run": "moss creeps to the light",
            "sleep": "moss folds for the night",
        },
        "nib": {
            "idle": "nib lies by the ink",
            "run": "nib traces the note",
            "sleep": "nib sleeps in the tray",
        },
        "kettle": {
            "idle": "kettle ticks, idle",
            "run": "kettle sings on the hob",
            "sleep": "kettle cools in the dark",
        },
        "crumb": {
            "idle": "crumb waits on the plate",
            "run": "crumb skitters off the card",
            "sleep": "crumb hides by the cup",
        },
        "wisp": {
            "idle": "wisp hovers, idle",
            "run": "wisp darts past the lamp",
            "sleep": "wisp fades to a spark",
        },
        "thimble": {
            "idle": "thimble stands on the card",
            "run": "thimble taps down the note",
            "sleep": "thimble tips and rests",
        },
        "soot": {
            "idle": "soot dusts the hearth, idle",
            "run": "soot swirls in the draft",
            "sleep": "soot settles on the brick",
        },
    }
)
PET_NAMES: Final[tuple[str, ...]] = tuple(_CATALOG)


def _pose_line(sprite: str, mood: str) -> str:
    poses = _CATALOG.get(sprite)
    if poses is None:
        raise Refuse("UNKNOWN")
    line = poses.get(mood)
    if line is None:
        raise Refuse("BAD_MOOD")
    return line


def _sprite(value: object) -> str:
    text = bound_text(value, SPRITE_MAX)
    if secret_shape(text):
        raise Refuse("SECRET")
    if _SPRITE_RE.fullmatch(text) is None:
        raise Refuse("BAD_SPRITE")
    if text not in _CATALOG:
        raise Refuse("UNKNOWN")
    return text


def _accept_sprite(value: object) -> str:
    if isinstance(value, str) and value in _CATALOG:
        return value
    return _sprite(value)


def _mood(value: object) -> str:
    text = bound_text(value, _MOOD_LIMIT)
    if secret_shape(text):
        raise Refuse("SECRET")
    if text.casefold() in _FORBIDDEN:
        raise Refuse("PET_EXEC")
    if text not in MOODS:
        raise Refuse("BAD_MOOD")
    return text


def _accept_mood(value: object) -> str:
    if isinstance(value, str) and value in MOODS:
        return value
    return _mood(value)


def _plain_int(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise Refuse("NOT_INT")
    return value


def _stored_scale(requested_value: object, scale_value: object) -> tuple[int, int]:
    requested = _plain_int(requested_value)
    scale = _plain_int(scale_value)
    if (
        requested < SCALE_FLOOR
        or requested > _SCALE_DOMAIN
        or scale < SCALE_FLOOR
        or scale > _SCALE_DOMAIN
    ):
        raise Refuse("OUT_OF_RANGE", f"{SCALE_FLOOR}..{_SCALE_DOMAIN}")
    effective = SCALE_CAP if requested > SCALE_CAP else requested
    return requested, effective


def _stored_cap(requested_value: object, cap_value: object) -> tuple[int, int]:
    requested = _plain_int(requested_value)
    cap = _plain_int(cap_value)
    if requested < 1 or requested > _CAP_DOMAIN or cap < 1 or cap > _CAP_DOMAIN:
        raise Refuse("OUT_OF_RANGE", f"1..{_CAP_DOMAIN}")
    effective = ROSTER_CAP if requested > ROSTER_CAP else requested
    return requested, effective


def _network(value: object) -> None:
    if type(value) is not bool:
        raise Refuse("NOT_BOOL")
    if value is not False:
        raise Refuse("BAD_VALUE")


def _length(value: object, code: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise Refuse(code)
    return value


@dataclass(frozen=True, slots=True)
class Line:
    """One cosmetic pose. `text` is a catalog line, never a command."""

    schema: str
    sprite: str
    mood: str
    text: str
    network: bool

    def __post_init__(self) -> None:
        if self.schema != SCHEMA:
            raise Refuse("BAD_SCHEMA")
        sprite = _accept_sprite(self.sprite)
        mood = _accept_mood(self.mood)
        if self.text != _pose_line(sprite, mood):
            raise Refuse("BAD_VALUE")
        _network(self.network)


@dataclass(frozen=True, slots=True)
class Pet:
    """One mascot. `scale` is milli-units and never above SCALE_CAP."""

    schema: str
    sprite: str
    mood: str
    enabled: bool
    scale: int
    requested_scale: int
    network: bool

    def __post_init__(self) -> None:
        if self.schema != SCHEMA:
            raise Refuse("BAD_SCHEMA")
        sprite = _accept_sprite(self.sprite)
        mood = _accept_mood(self.mood)
        if type(self.enabled) is not bool:
            raise Refuse("NOT_BOOL")
        requested, effective = _stored_scale(self.requested_scale, self.scale)
        _network(self.network)
        if sprite != self.sprite:
            object.__setattr__(self, "sprite", sprite)
        if mood != self.mood:
            object.__setattr__(self, "mood", mood)
        if self.scale != effective or self.requested_scale != requested:
            object.__setattr__(self, "requested_scale", requested)
            object.__setattr__(self, "scale", effective)


@dataclass(frozen=True, slots=True)
class Roster:
    """Installed pets under the policy cap. Extra valid rows are `dropped`."""

    schema: str
    pets: tuple[Pet, ...]
    dropped: int
    cap: int
    requested_cap: int
    network: bool

    def __post_init__(self) -> None:
        if self.schema != SCHEMA:
            raise Refuse("BAD_SCHEMA")
        requested, effective = _stored_cap(self.requested_cap, self.cap)
        if type(self.dropped) is not int:
            raise Refuse("NOT_INT")
        if self.dropped < 0 or self.dropped > _SEQ_CAP:
            raise Refuse("OUT_OF_RANGE", f"0..{_SEQ_CAP}")
        if type(self.pets) is not tuple or len(self.pets) > effective:
            raise Refuse("BAD_ROWS")
        seen: set[str] = set()
        for pet in self.pets:
            if type(pet) is not Pet:
                raise Refuse("BAD_PET")
            if pet.sprite in seen:
                raise Refuse("DUPLICATE")
            seen.add(pet.sprite)
        _network(self.network)
        if self.cap != effective or self.requested_cap != requested:
            object.__setattr__(self, "requested_cap", requested)
            object.__setattr__(self, "cap", effective)


@dataclass(frozen=True, slots=True)
class Status:
    """Doctor line. `ready` is `enabled`. This module does not paint."""

    schema: str
    sprite: str
    mood: str
    enabled: bool
    scale: int
    requested_scale: int
    ready: bool
    network: bool

    def __post_init__(self) -> None:
        if self.schema != SCHEMA:
            raise Refuse("BAD_SCHEMA")
        sprite = _accept_sprite(self.sprite)
        mood = _accept_mood(self.mood)
        if type(self.enabled) is not bool or type(self.ready) is not bool:
            raise Refuse("NOT_BOOL")
        if self.ready is not self.enabled:
            raise Refuse("BAD_VALUE")
        requested, effective = _stored_scale(self.requested_scale, self.scale)
        _network(self.network)
        if sprite != self.sprite:
            object.__setattr__(self, "sprite", sprite)
        if mood != self.mood:
            object.__setattr__(self, "mood", mood)
        if self.scale != effective or self.requested_scale != requested:
            object.__setattr__(self, "requested_scale", requested)
            object.__setattr__(self, "scale", effective)


def _mapping(value: object) -> Mapping[object, object]:
    if isinstance(value, (str, bytes, bytearray)) or not isinstance(value, Mapping):
        raise Refuse("BAD_MAP")
    return value


def _rows(value: object) -> Sequence[object]:
    if isinstance(value, (str, bytes, bytearray, Mapping)) or not isinstance(value, Sequence):
        raise Refuse("BAD_ROWS")
    return value


def _walk(value: object, depth: int) -> None:
    if depth > _DEPTH:
        raise Refuse("BAD_MAP")
    if isinstance(value, str):
        text = bound_text(value, _WALK_TEXT)
        if secret_shape(text):
            raise Refuse("SECRET")
        return
    if isinstance(value, (bytes, bytearray)):
        raise Refuse("NOT_TEXT")
    if isinstance(value, Mapping):
        _scan_mapping(value, depth)
        return
    if isinstance(value, Sequence):
        size = _length(len(value), "BAD_ROWS")
        if size > _SEQ_CAP:
            raise Refuse("OVERSIZE", str(_SEQ_CAP))
        count = 0
        for item in value:
            count += 1
            if count > _SEQ_CAP:
                raise Refuse("OVERSIZE", str(_SEQ_CAP))
            _walk(item, depth + 1)
        return
    if value is None or type(value) is bool or type(value) is int:
        return
    raise Refuse("BAD_VALUE")


def _scan_mapping(value: Mapping[object, object], depth: int) -> None:
    size = _length(len(value), "BAD_MAP")
    if size > _KEY_SCAN:
        raise Refuse("OVERSIZE", str(_KEY_SCAN))
    seen: set[str] = set()
    count = 0
    for key in value:
        count += 1
        if count > _KEY_SCAN:
            raise Refuse("OVERSIZE", str(_KEY_SCAN))
        name = bound_text(key, _KEY_LIMIT)
        if secret_shape(name):
            raise Refuse("SECRET")
        if name.casefold() in _FORBIDDEN:
            raise Refuse("PET_EXEC")
        if name in seen:
            raise Refuse("DUPLICATE")
        seen.add(name)
        _walk(value[key], depth + 1)


def _fields(mapping: Mapping[object, object]) -> dict[str, object]:
    size = _length(len(mapping), "BAD_MAP")
    if size > _KEY_SCAN:
        raise Refuse("OVERSIZE", str(_KEY_SCAN))
    found: dict[str, object] = {}
    seen: set[str] = set()
    count = 0
    for key in mapping:
        count += 1
        if count > _KEY_SCAN:
            raise Refuse("OVERSIZE", str(_KEY_SCAN))
        name = bound_text(key, _KEY_LIMIT)
        if secret_shape(name):
            raise Refuse("SECRET")
        if name.casefold() in _FORBIDDEN:
            raise Refuse("PET_EXEC")
        if name in seen:
            raise Refuse("DUPLICATE")
        seen.add(name)
        child = mapping[key]
        if name not in _ALLOWED:
            _walk(child, 1)
            raise Refuse("BAD_KEY")
        if not (name in _FIELD_TEXT and isinstance(child, str)):
            _walk(child, 1)
        found[name] = child
    return found


def _flag(value: object) -> bool:
    if type(value) is not bool:
        raise Refuse("NOT_BOOL")
    return value


def present(mapping: object) -> Pet:
    """Validate one cosmetic mapping. Command keys raise PET_EXEC."""
    found = _fields(_mapping(mapping))
    if "sprite" not in found:
        raise Refuse("MISSING_SPRITE")
    if "mood" not in found:
        raise Refuse("MISSING_MOOD")
    enabled = _flag(found["enabled"]) if "enabled" in found else False
    raw_scale = found["scale"] if "scale" in found else SCALE_DEFAULT
    requested, scale = _stored_scale(raw_scale, raw_scale)
    return Pet(
        schema=SCHEMA,
        sprite=_accept_sprite(found["sprite"]),
        mood=_accept_mood(found["mood"]),
        enabled=enabled,
        scale=scale,
        requested_scale=requested,
        network=False,
    )


def select(mapping: object) -> Pet:
    """Adopt a pet. `enabled` is true. There is no off mode."""
    pet = present(mapping)
    if pet.enabled:
        return pet
    return replace(pet, enabled=True)


def collect(rows: object, *, limit: object = None) -> Roster:
    """Keep at most ROSTER_CAP pets. A higher limit is ignored. Every row is checked."""
    sequence = _rows(rows)
    size = _length(len(sequence), "BAD_ROWS")
    if size > _SEQ_CAP:
        raise Refuse("OVERSIZE", str(_SEQ_CAP))
    if limit is None:
        requested, cap = ROSTER_CAP, ROSTER_CAP
    else:
        requested, cap = _stored_cap(limit, limit)
    seen: set[str] = set()
    kept: list[Pet] = []
    count = 0
    for row in sequence:
        count += 1
        if count > _SEQ_CAP:
            raise Refuse("OVERSIZE", str(_SEQ_CAP))
        pet = present(row)
        if pet.sprite in seen:
            raise Refuse("DUPLICATE")
        seen.add(pet.sprite)
        if len(kept) < cap:
            kept.append(pet)
    return Roster(
        schema=SCHEMA,
        pets=tuple(kept),
        dropped=len(seen) - len(kept),
        cap=cap,
        requested_cap=requested,
        network=False,
    )


def activity_mood(activity: object) -> str:
    """Map one activity label onto idle, run, or sleep.

    `waiting` and `nothing` are idle. `tool` and `inflight` are run.
    `shell` and `exec` are PET_EXEC.
    """
    if isinstance(activity, str):
        mood = _ACTIVITIES.get(activity)
        if mood is not None:
            return mood
    text = bound_text(activity, _MOOD_LIMIT)
    if secret_shape(text):
        raise Refuse("SECRET")
    if text.casefold() in _FORBIDDEN:
        raise Refuse("PET_EXEC")
    raise Refuse("BAD_ACTIVITY")


def describe(pet: object) -> Status:
    """Return the cosmetic status. `network` is false. `ready` follows `enabled`."""
    if type(pet) is not Pet:
        raise Refuse("BAD_PET")
    return Status(
        schema=SCHEMA,
        sprite=pet.sprite,
        mood=pet.mood,
        enabled=pet.enabled,
        scale=pet.scale,
        requested_scale=pet.requested_scale,
        ready=pet.enabled,
        network=False,
    )


def rebuild(snapshot: object) -> Pet:
    """Reproduce the pet `describe` emitted."""
    if type(snapshot) is not Status:
        raise Refuse("BAD_PET")
    return Pet(
        schema=snapshot.schema,
        sprite=snapshot.sprite,
        mood=snapshot.mood,
        enabled=snapshot.enabled,
        scale=snapshot.scale,
        requested_scale=snapshot.requested_scale,
        network=False,
    )


def render(pet: object) -> Line:
    """Return one short cosmetic line. A name uses idle. A Pet uses its mood."""
    if type(pet) is Pet:
        name = pet.sprite
        pose = pet.mood
    else:
        name = _accept_sprite(pet)
        pose = "idle"
    return Line(
        schema=SCHEMA,
        sprite=name,
        mood=pose,
        text=_pose_line(name, pose),
        network=False,
    )


def act(sprite: object, action: object) -> Line:
    """Return a cosmetic pose. `shell` and `exec` refuse. Nothing is started."""
    if isinstance(action, str) and action in MOODS:
        pose = action
    else:
        text = bound_text(action, _MOOD_LIMIT)
        if secret_shape(text):
            raise Refuse("SECRET")
        if text.casefold() in _FORBIDDEN:
            raise Refuse("PET_EXEC")
        raise Refuse("BAD_ACTIVITY")
    name = _accept_sprite(sprite)
    return Line(
        schema=SCHEMA,
        sprite=name,
        mood=pose,
        text=_pose_line(name, pose),
        network=False,
    )


__all__ = [
    "MOODS",
    "PET_NAMES",
    "ROSTER_CAP",
    "SCALE_CAP",
    "SCALE_DEFAULT",
    "SCALE_FLOOR",
    "SCHEMA",
    "SPRITE_MAX",
    "Line",
    "Pet",
    "Roster",
    "Status",
    "act",
    "activity_mood",
    "collect",
    "describe",
    "present",
    "rebuild",
    "render",
    "select",
]
