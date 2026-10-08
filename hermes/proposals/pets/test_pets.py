"""Cosmetic pet tests. No network and no process."""

from __future__ import annotations

from collections.abc import Callable, Iterator, Mapping
from dataclasses import dataclass

import pytest

from cosmos_hermes import Refuse, secret_shape
from pets import (
    MOODS,
    PET_NAMES,
    ROSTER_CAP,
    SCALE_CAP,
    SCALE_DEFAULT,
    SCALE_FLOOR,
    SCHEMA,
    SPRITE_MAX,
    Line,
    Pet,
    Roster,
    Status,
    act,
    activity_mood,
    collect,
    describe,
    present,
    rebuild,
    render,
    select,
)


def _pet(sprite: object = "ember", mood: object = "idle", **extra: object) -> dict[str, object]:
    row: dict[str, object] = {"sprite": sprite, "mood": mood}
    row.update(extra)
    return row


def _code(func: Callable[[], object]) -> str:
    with pytest.raises(Refuse) as caught:
        func()
    return caught.value.code


def _nth(pets: tuple[Pet, ...], index: int) -> Pet:
    if index < 0 or index >= len(pets):
        raise AssertionError(index)
    return pets[index]


class _DupKeys(Mapping[str, object]):
    """Yields sprite twice. A real dict cannot."""

    def __iter__(self) -> Iterator[str]:
        yield "sprite"
        yield "mood"
        yield "sprite"

    def __len__(self) -> int:
        return 3

    def __getitem__(self, key: str) -> object:
        if key == "sprite":
            return "ember"
        if key == "mood":
            return "idle"
        raise KeyError(key)


@dataclass(frozen=True, slots=True)
class _Story:
    card: Line
    note: Line
    light: Line
    rest: Line
    session: Pet
    status: Status
    rebuilt: Pet
    roster: Roster
    shell_code: str
    exec_code: str
    unknown_code: str


def _act_shell() -> object:
    return act("ember", "shell")


def _act_exec() -> object:
    return act("ember", "exec")


def _unknown_pet() -> object:
    return render("lantern")


def _story() -> _Story:
    card = render("ember")
    note = act("pebble", "run")
    light = act("wisp", "run")
    session = select({"sprite": "ember", "mood": "sleep", "scale": 500, "enabled": False})
    rest = render(session)
    status = describe(session)
    rebuilt = rebuild(status)
    roster = collect(
        (
            {"sprite": "ember", "mood": "idle"},
            {"sprite": "pebble", "mood": "run"},
            {"sprite": "moss", "mood": "sleep"},
        ),
        limit=2,
    )
    return _Story(
        card=card,
        note=note,
        light=light,
        rest=rest,
        session=session,
        status=status,
        rebuilt=rebuilt,
        roster=roster,
        shell_code=_code(_act_shell),
        exec_code=_code(_act_exec),
        unknown_code=_code(_unknown_pet),
    )


def test_example_pets() -> None:
    first = _story()
    second = _story()
    assert first == second
    assert first.card.sprite == "ember"
    assert first.card.mood == "idle"
    assert first.card.text == "ember waits by the card, idle"
    assert len(first.card.text) <= 64
    assert first.card.network is False
    assert first.note.sprite == "pebble"
    assert first.note.text == "pebble hops toward the note"
    assert first.light.sprite == "wisp"
    assert "lamp" in first.light.text
    assert first.rest.mood == "sleep"
    assert first.rest.text == "ember rests under the lamp"
    assert first.session.enabled is True
    assert first.session.mood == "sleep"
    assert first.session.sprite == "ember"
    assert first.status.ready is True
    assert first.rebuilt == first.session
    assert first.roster.cap == 2
    assert first.roster.dropped == 1
    assert _nth(first.roster.pets, 0).sprite == "ember"
    assert _nth(first.roster.pets, 1).sprite == "pebble"
    assert first.shell_code == "PET_EXEC"
    assert first.exec_code == "PET_EXEC"
    assert first.unknown_code == "UNKNOWN"
    assert secret_shape(repr(first)) is False


def test_schema_catalog_and_caps() -> None:
    assert SCHEMA == "cosmos-hermes-pets/1"
    assert set(MOODS) == {"idle", "run", "sleep"}
    assert SPRITE_MAX == 24
    assert SCALE_FLOOR == 100
    assert SCALE_DEFAULT == 330
    assert SCALE_CAP == 3000
    assert ROSTER_CAP == 8
    assert "ember" in PET_NAMES
    assert "boba" in PET_NAMES
    assert len(PET_NAMES) == len(set(PET_NAMES))
    assert len(PET_NAMES) > ROSTER_CAP
    for name in PET_NAMES:
        idle = render(name)
        assert idle == act(name, "idle")
        assert idle.mood == "idle"
        assert idle.text != ""
        assert len(idle.text) <= 64
        assert "\n" not in idle.text
        assert "://" not in idle.text
        for mood in ("idle", "run", "sleep"):
            line = act(name, mood)
            assert line.sprite == name
            assert line.mood == mood
            assert line.network is False
            assert secret_shape(line.text) is False


def test_present_success_select_and_defaults() -> None:
    pet = present(_pet())
    assert pet == Pet(
        schema=SCHEMA,
        sprite="ember",
        mood="idle",
        enabled=False,
        scale=SCALE_DEFAULT,
        requested_scale=SCALE_DEFAULT,
        network=False,
    )
    assert pet == present(_pet())
    again = present(_pet("boba", "run", enabled=True, scale=SCALE_FLOOR))
    assert again.mood == "run"
    assert again.enabled is True
    assert again.scale == SCALE_FLOOR
    picked = select(_pet("ember", "sleep", enabled=False))
    assert picked.enabled is True
    assert picked.mood == "sleep"
    assert describe(picked).ready is True
    assert describe(pet).ready is False
    assert select(_pet(enabled=True)) == present(_pet(enabled=True))
    assert rebuild(describe(picked)) == picked


def test_scale_and_roster_caps_are_recorded_not_raised() -> None:
    pet = present(_pet(scale=10_000))
    assert pet.requested_scale == 10_000
    assert pet.scale == SCALE_CAP
    exact = present(_pet(scale=SCALE_CAP))
    assert exact.scale == SCALE_CAP
    assert exact.requested_scale == SCALE_CAP
    built = Pet(
        schema=SCHEMA,
        sprite="ember",
        mood="idle",
        enabled=False,
        scale=9_999,
        requested_scale=9_999,
        network=False,
    )
    assert built.scale == SCALE_CAP
    assert built.requested_scale == 9_999
    assert built.network is False
    assert rebuild(describe(built)) == built
    rows = [_pet(name) for name in PET_NAMES]
    roster = collect(rows, limit=10_000)
    assert roster.cap == ROSTER_CAP
    assert roster.requested_cap == 10_000
    assert len(roster.pets) == ROSTER_CAP
    assert roster.dropped == len(PET_NAMES) - ROSTER_CAP
    assert _nth(roster.pets, 0).sprite == PET_NAMES[0]
    assert _nth(roster.pets, ROSTER_CAP - 1).sprite == PET_NAMES[ROSTER_CAP - 1]
    tight = collect(rows, limit=3)
    assert tight.cap == 3
    assert tight.requested_cap == 3
    assert tight.dropped == len(PET_NAMES) - 3
    empty = collect(())
    assert empty.pets == ()
    assert empty.dropped == 0
    assert empty.cap == ROSTER_CAP


def test_activity_mood_table() -> None:
    assert activity_mood("idle") == "idle"
    assert activity_mood("nothing") == "idle"
    assert activity_mood("waiting") == "idle"
    assert activity_mood("run") == "run"
    assert activity_mood("tool") == "run"
    assert activity_mood("inflight") == "run"
    assert activity_mood("sleep") == "sleep"
    for name in ("wave", "jump", "review", "failed", "off", "WAITING", ""):
        assert _code(_activity(name)) == "BAD_ACTIVITY"


def _activity(name: object) -> Callable[[], object]:
    def run() -> object:
        return activity_mood(name)

    return run


def test_command_actions_refuse() -> None:
    samples: tuple[tuple[Callable[[], object], str], ...] = (
        (_act_shell, "PET_EXEC"),
        (_act_exec, "PET_EXEC"),
        (_call_act("ember", "SHELL"), "PET_EXEC"),
        (_call_act("ember", "Exec"), "PET_EXEC"),
        (_call_act("ember", "command"), "PET_EXEC"),
        (_call_act("ember", "url"), "PET_EXEC"),
        (_call_act("lantern", "exec"), "PET_EXEC"),
        (_call_present(_pet(mood="exec")), "PET_EXEC"),
        (_call_present(_pet(mood="shell")), "PET_EXEC"),
        (_activity("shell"), "PET_EXEC"),
        (_activity("EXEC"), "PET_EXEC"),
        (_unknown_pet, "UNKNOWN"),
        (_call_act("lantern", "idle"), "UNKNOWN"),
        (_call_present(_pet("exec")), "UNKNOWN"),
        (_call_present(_pet("shell")), "UNKNOWN"),
        (_call_act("ember", "wave"), "BAD_ACTIVITY"),
    )
    for func, code in samples:
        assert _code(func) == code


def _call_act(sprite: object, action: object) -> Callable[[], object]:
    def run() -> object:
        return act(sprite, action)

    return run


def _call_present(mapping: object) -> Callable[[], object]:
    def run() -> object:
        return present(mapping)

    return run


def test_pet_exec_keys_win_over_bad_key() -> None:
    samples: tuple[object, ...] = (
        {"command": "ls"},
        {"url": "http://example.test"},
        {"exec": "rm"},
        {"shell": "nope"},
        {"Command": "id"},
        {"URL": "http://example.test"},
        {"Exec": "rm"},
        {"Shell": "nope"},
        {"sprite": "ember", "mood": "idle", "url": "http://example.test"},
        {"sprite": "ember", "mood": "idle", "extra": {"exec": "rm"}},
        {"sprite": "ember", "mood": "idle", "blob": [{"command": "nope"}]},
        {"sprite": {"exec": "nope"}, "mood": "idle"},
        {"sprite": "ember", "mood": "idle", "note": {"shell": "nope"}},
    )
    for mapping in samples:
        assert _code(_call_present(mapping)) == "PET_EXEC"


def test_bad_mood_sprite_and_tail() -> None:
    for mood in ("wave", "failed", "jump", "review", "waiting", "off", "IDLE", "run "):
        assert _code(_call_present(_pet(mood=mood))) == "BAD_MOOD"
    for sprite in ("", "Ember", "em_ber", "ember.png", "em ber", "a/b", "A"):
        assert _code(_call_present(_pet(sprite))) == "BAD_SPRITE"
    assert _code(_call_present(_pet("-"))) == "UNKNOWN"
    assert _code(_call_collect([_pet("ember"), {"exec": "nope"}], 1)) == "PET_EXEC"
    assert _code(_call_collect([_pet("ember"), _pet("BAD")], 1)) == "BAD_SPRITE"
    assert _code(_call_collect([_pet("ember"), _pet("lantern")], 1)) == "UNKNOWN"
    assert _code(_call_collect([_pet("ember"), _pet("ember")], 1)) == "DUPLICATE"


def _call_collect(rows: object, limit: object) -> Callable[[], object]:
    def run() -> object:
        return collect(rows, limit=limit)

    return run


def test_refusal_codes() -> None:
    checks: tuple[tuple[str, object], ...] = (
        ("BAD_MAP", "ember"),
        ("BAD_MAP", ["ember"]),
        ("BAD_MAP", {"a": {"b": {"c": {"d": {"e": {"f": "z"}}}}}}),
        ("MISSING_SPRITE", {}),
        ("MISSING_MOOD", {"sprite": "ember"}),
        ("BAD_KEY", _pet(note="hi")),
        ("BAD_VALUE", _pet(scale=1.5)),
        ("NOT_BOOL", _pet(enabled="true")),
        ("NOT_BOOL", _pet(enabled=1)),
        ("NOT_INT", _pet(scale=True)),
        ("NOT_INT", _pet(scale=None)),
        ("NOT_TEXT", _pet(sprite=12)),
        ("NOT_TEXT", _pet(mood=1)),
        ("NOT_TEXT", _pet(sprite=b"ember")),
        ("NULL_BYTE", _pet(sprite="a\x00")),
        ("OVERSIZE", _pet(sprite="a" * (SPRITE_MAX + 1))),
        ("SECRET", _pet(sprite="sk-abcdefgh")),
        ("SECRET", _pet(note="api_key=abc")),
        ("OUT_OF_RANGE", _pet(scale=SCALE_FLOOR - 1)),
        ("OUT_OF_RANGE", _pet(scale=0)),
        ("OUT_OF_RANGE", _pet(scale=1_000_001)),
        ("UNKNOWN", _pet("quartz")),
        ("DUPLICATE", _DupKeys()),
    )
    for code, mapping in checks:
        assert _code(_call_present(mapping)) == code
    assert _code(_call_present(_pet(mood="x" * 17))) == "OVERSIZE"
    wide = {f"k{index}": "v" for index in range(17)}
    assert _code(_call_present(wide)) == "OVERSIZE"
    assert _code(_call_present({None: "ember"})) == "NOT_TEXT"
    assert _code(_collect_map) == "BAD_ROWS"
    assert _code(_collect_text) == "BAD_ROWS"
    assert _code(_collect_limit_zero) == "OUT_OF_RANGE"
    assert _code(_collect_limit_bool) == "NOT_INT"
    assert _code(_collect_many) == "OVERSIZE"
    assert _code(_activity(None)) == "NOT_TEXT"
    assert _code(_activity("sk-abcdefgh")) == "SECRET"
    assert _code(_describe_map) == "BAD_PET"
    assert _code(_rebuild_map) == "BAD_PET"
    assert _code(_bad_schema) == "BAD_SCHEMA"
    assert _code(_bad_line) == "BAD_VALUE"
    assert _code(_line_network) == "BAD_VALUE"
    assert _code(_pet_network) == "BAD_VALUE"
    assert _code(_status_ready) == "BAD_VALUE"
    assert _code(_roster_dup) == "DUPLICATE"
    assert _code(_roster_bad_pet) == "BAD_PET"
    assert _code(_roster_network) == "BAD_VALUE"
    assert _code(_roster_schema) == "BAD_SCHEMA"
    assert _code(_status_schema) == "BAD_SCHEMA"
    assert _code(_line_schema) == "BAD_SCHEMA"
    assert _code(_dropped_negative) == "OUT_OF_RANGE"
    assert _code(_act_secret) == "SECRET"


def _collect_map() -> object:
    return collect({"sprite": "ember", "mood": "idle"})


def _collect_text() -> object:
    return collect("ember")


def _collect_limit_zero() -> object:
    return collect([], limit=0)


def _collect_limit_bool() -> object:
    return collect([], limit=True)


def _collect_many() -> object:
    rows = [{"sprite": "ember", "mood": "idle"} for _ in range(33)]
    return collect(rows)


def _describe_map() -> object:
    return describe({"sprite": "ember"})


def _rebuild_map() -> object:
    return rebuild({"sprite": "ember"})


def _bad_schema() -> object:
    return Pet(
        schema="other",
        sprite="ember",
        mood="idle",
        enabled=False,
        scale=SCALE_DEFAULT,
        requested_scale=SCALE_DEFAULT,
        network=False,
    )


def _bad_line() -> object:
    return Line(
        schema=SCHEMA,
        sprite="ember",
        mood="idle",
        text="run a shell",
        network=False,
    )


def _line_network() -> object:
    return Line(
        schema=SCHEMA,
        sprite="ember",
        mood="idle",
        text="ember waits by the card, idle",
        network=True,
    )


def _pet_network() -> object:
    return Pet(
        schema=SCHEMA,
        sprite="ember",
        mood="idle",
        enabled=False,
        scale=SCALE_DEFAULT,
        requested_scale=SCALE_DEFAULT,
        network=True,
    )


def _status_ready() -> object:
    return Status(
        schema=SCHEMA,
        sprite="ember",
        mood="run",
        enabled=False,
        scale=SCALE_DEFAULT,
        requested_scale=SCALE_DEFAULT,
        ready=True,
        network=False,
    )


def _roster_dup() -> object:
    one = present(_pet())
    return Roster(
        schema=SCHEMA,
        pets=(one, present(_pet("ember", "run"))),
        dropped=0,
        cap=ROSTER_CAP,
        requested_cap=ROSTER_CAP,
        network=False,
    )


def _roster_bad_pet() -> object:
    return Roster(
        schema=SCHEMA,
        pets=("nope",),  # type: ignore[arg-type]
        dropped=0,
        cap=ROSTER_CAP,
        requested_cap=ROSTER_CAP,
        network=False,
    )


def _roster_network() -> object:
    return Roster(
        schema=SCHEMA,
        pets=(),
        dropped=0,
        cap=ROSTER_CAP,
        requested_cap=ROSTER_CAP,
        network=True,
    )


def _roster_schema() -> object:
    return Roster(
        schema="other",
        pets=(),
        dropped=0,
        cap=ROSTER_CAP,
        requested_cap=ROSTER_CAP,
        network=False,
    )


def _status_schema() -> object:
    return Status(
        schema="other",
        sprite="ember",
        mood="idle",
        enabled=False,
        scale=SCALE_DEFAULT,
        requested_scale=SCALE_DEFAULT,
        ready=False,
        network=False,
    )


def _line_schema() -> object:
    return Line(schema="other", sprite="ember", mood="idle", text="x", network=False)


def _dropped_negative() -> object:
    return Roster(
        schema=SCHEMA,
        pets=(),
        dropped=-1,
        cap=ROSTER_CAP,
        requested_cap=ROSTER_CAP,
        network=False,
    )


def _act_secret() -> object:
    return act("ember", "sk-abcdefgh")


def test_roster_rows_and_repr() -> None:
    one = present(_pet())
    roster = Roster(
        schema=SCHEMA,
        pets=(one,),
        dropped=0,
        cap=100,
        requested_cap=100,
        network=False,
    )
    assert roster.cap == ROSTER_CAP
    assert roster.requested_cap == 100
    assert roster.network is False
    with pytest.raises(AttributeError):
        setattr(one, "mood", "sleep")
    text = repr((one, roster, describe(one), render(one), act("boba", "sleep")))
    assert secret_shape(text) is False
    assert "network=False" in text
