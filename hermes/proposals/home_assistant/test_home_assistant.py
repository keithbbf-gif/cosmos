"""Home Assistant descriptors confirm and never call a device."""

from __future__ import annotations

import ast
from collections.abc import Callable
from dataclasses import replace
from pathlib import Path

import pytest

import home_assistant
from cosmos_hermes import Refuse, secret_shape
from home_assistant import (
    AREA_CAP,
    BLOCKED_DOMAINS,
    CALL_DOMAINS,
    CONFIRM,
    CRED_CAP,
    ENTITY_CAP,
    FAILURE,
    MAX_STAMP,
    NAME_CAP,
    POLICY_BUDGET,
    POLICY_FIELDS,
    POLICY_ITEMS,
    POLICY_LIST,
    POLICY_STATE,
    READ_DOMAINS,
    SCHEMA,
    SERVICES,
    TOOLS,
    Call,
    Field,
    Home,
    Plan,
    Skip,
    Step,
    catalog,
    classify,
    rebuild,
    retry,
    run,
    weight,
)


def _home() -> Home:
    home = Home()
    home.enable("hass-kiln")
    return home


def _expect(code: str, func: Callable[[], object]) -> None:
    with pytest.raises(Refuse) as caught:
        func()
    assert caught.value.code == code


def _code(func: Callable[[], object]) -> str:
    with pytest.raises(Refuse) as caught:
        func()
    return caught.value.code


def _kept(plan: Plan) -> int:
    return len(plan.steps)


def _held(plan: Plan) -> int:
    return len(plan.skipped)


def _step(plan: Plan, index: int) -> Step:
    return plan.steps[index]


def _skip(plan: Plan, index: int) -> Skip:
    return plan.skipped[index]


def _kept_sources(plan: Plan) -> tuple[int, ...]:
    return tuple(step.source for step in plan.steps)


def _skip_sources(plan: Plan) -> tuple[int, ...]:
    return tuple(skip.source for skip in plan.skipped)


def _field(call: Call, index: int) -> Field:
    return call.data[index]


def _launch(call: Call) -> Callable[[], object]:
    def go() -> None:
        run(call)

    return go


def test_example_home_assistant() -> None:
    def once() -> tuple[object, ...]:
        home = Home()

        def before() -> Call:
            return home.service("light.kitchen", "turn_on")

        disabled = _code(before)
        home.enable("hass-kiln")
        call = home.service("light.kitchen", "turn_on")
        reading = home.state("sensor.kiln_temp")
        lights = home.list_entities("light", "kitchen")
        actions = home.list_services("light")
        batch = home.plan(
            (call, reading),
            now=1_721_000_000,
            seen=1_700_000_000,
            budget=10_000,
        )
        replay = rebuild(batch)

        def shell_entity() -> Call:
            return home.service("light.kitchen; rm", "turn_on")

        def shell_action() -> Call:
            return home.service("light.kitchen", "on; rm")

        assert SCHEMA == "cosmos-hermes-home_assistant/1"
        assert disabled == "DISABLED"
        assert home.enabled is True
        assert classify(call) == CONFIRM
        assert classify(reading) == CONFIRM
        assert call.kind == "service"
        assert call.entity == "light.kitchen"
        assert call.action == "turn_on"
        assert reading.kind == "state"
        assert reading.entity == "sensor.kiln_temp"
        assert reading.action == ""
        assert _code(_launch(call)) == "NOT_RUN"
        assert _code(_launch(reading)) == "NOT_RUN"
        assert _code(shell_entity) == "BAD_ENTITY"
        assert _code(shell_action) == "BAD_ENTITY"
        assert batch.budget == POLICY_BUDGET
        assert batch.requested_budget == 10_000
        assert batch.clamped == ("budget",)
        assert _kept(batch) == 2
        assert _held(batch) == 0
        assert replay == batch
        assert replay is not batch
        return (disabled, call, reading, lights, actions, batch, replay)

    assert once() == once()


def test_public_surface_and_domain_sets() -> None:
    for name in home_assistant.__all__:
        assert hasattr(home_assistant, name)
    assert TOOLS == (
        "ha_list_entities",
        "ha_get_state",
        "ha_list_services",
        "ha_call_service",
    )
    assert set(CALL_DOMAINS) <= set(READ_DOMAINS)
    assert set(BLOCKED_DOMAINS).isdisjoint(READ_DOMAINS)
    assert SERVICES == tuple(sorted(SERVICES))
    assert "light.turn_on" in SERVICES
    assert "shell_command.turn_on" not in SERVICES
    assert "python_script.turn_on" not in SERVICES
    assert catalog("light") == ("toggle", "turn_off", "turn_on")
    sensor = catalog("sensor")
    assert "turn_on" not in sensor
    assert sensor == ()


def test_disabled_until_enable_and_flag_is_not_a_switch() -> None:
    home = Home()
    assert home.enabled is False
    assert home.credential_id == ""
    assert not hasattr(home, "disable")

    def service() -> Call:
        return home.service("light.kitchen", "turn_on")

    def reading() -> Call:
        return home.state("sensor.kiln_temp")

    def listed() -> Call:
        return home.list_entities("light")

    def services() -> Call:
        return home.list_services("light")

    def planned() -> Plan:
        return home.plan((), now=1)

    for func in (service, reading, listed, services, planned):
        _expect("DISABLED", func)

    def arm() -> None:
        home.enabled = True

    def rewrite() -> None:
        home.credential_id = "hass-kiln"

    _expect("UNCLASSIFIED", arm)
    _expect("UNCLASSIFIED", rewrite)
    assert home.enabled is False
    assert catalog("scene") == ("turn_on",)

    def still_dark() -> Call:
        return home.list_services("light")

    _expect("DISABLED", still_dark)


def test_credential_id_rules() -> None:
    home = Home()

    def missing() -> None:
        home.enable()

    def blank() -> None:
        home.enable("")

    def spaced() -> None:
        home.enable("hass kiln")

    def leading() -> None:
        home.enable("-hass")

    def huge() -> None:
        home.enable("a" * (CRED_CAP + 1))

    _expect("NO_CRED", missing)
    _expect("NO_CRED", blank)
    _expect("BAD_CRED", spaced)
    _expect("BAD_CRED", leading)
    _expect("OVERSIZE", huge)
    assert home.enabled is False

    def leaked() -> None:
        home.enable("sk-abcdefghij")

    with pytest.raises(Refuse) as caught:
        leaked()
    assert caught.value.code == "SECRET"
    assert caught.value.detail == ""
    assert "sk-" not in str(caught.value)
    assert secret_shape(str(caught.value)) is False
    assert home.enabled is False
    assert "sk-" not in repr(home)

    def bearer() -> None:
        home.enable("Bearer abcdefghij")

    def assigned() -> None:
        home.enable("api_key=abcdefgh")

    _expect("SECRET", bearer)
    _expect("SECRET", assigned)
    home.enable("hass-kiln")
    home.enable("hass-kiln")
    assert home.enabled is True
    assert home.credential_id == "hass-kiln"

    def swap() -> None:
        home.enable("hass-porch")

    _expect("MISMATCH", swap)
    assert home.credential_id == "hass-kiln"


def test_shell_metacharacters_and_bad_entities() -> None:
    home = _home()
    samples = (
        "light.kitchen; rm",
        "light.kitchen;rm",
        "light.kitchen|rm",
        "light.kitchen&rm",
        "light.kitchen`rm`",
        "light.kitchen$(rm)",
        "light.kitchen>out",
        "light.kitchen\nrm",
        "light.kitchen%PATH%",
        "light.kitchen^rm",
    )
    for entity in samples:
        def go(text: str = entity) -> Call:
            return home.service(text, "turn_on")

        _expect("BAD_ENTITY", go)
    actions = ("on; rm", "turn_on|id", "turn_on&&true", "turn_on`id`")
    for action in actions:
        def go_action(text: str = action) -> Call:
            return home.service("light.kitchen", text)

        _expect("BAD_ENTITY", go_action)

    def area() -> Call:
        return home.list_entities("light", "kitchen; rm")

    def color() -> Call:
        return home.service(
            "light.kitchen",
            "turn_on",
            {"color_name": "blue;rm"},
        )

    _expect("BAD_ENTITY", area)
    _expect("BAD_ENTITY", color)
    for entity in (
        "1light.kitchen",
        "Light.kitchen",
        "light.kitchen.lamp",
        "light.",
        ".kitchen",
        "light",
        "light.kitchen ",
    ):
        def bad(text: str = entity) -> Call:
            return home.service(text, "turn_on")

        _expect("BAD_ENTITY", bad)

    def empty_entity() -> Call:
        return home.service("", "turn_on")

    def empty_action() -> Call:
        return home.service("light.kitchen", "")

    _expect("EMPTY", empty_entity)
    _expect("EMPTY", empty_action)


def test_blocked_domains_and_unlisted_services() -> None:
    home = _home()
    for domain in BLOCKED_DOMAINS:
        def state_of(name: str = domain) -> Call:
            return home.state(f"{name}.dump")

        def call_of(name: str = domain) -> Call:
            return home.service(f"{name}.dump", "turn_on")

        def list_of(name: str = domain) -> Call:
            return home.list_services(name)

        def catalog_of(name: str = domain) -> tuple[str, ...]:
            return catalog(name)

        _expect("BLOCKED_DOMAIN", state_of)
        _expect("BLOCKED_DOMAIN", call_of)
        _expect("BLOCKED_DOMAIN", list_of)
        _expect("BLOCKED_DOMAIN", catalog_of)

    reading = home.state("sensor.kiln_temp")

    def forged() -> Call:
        return replace(reading, entity="shell_command.dump", domain="shell_command")

    _expect("BLOCKED_DOMAIN", forged)

    def sensor_on() -> Call:
        return home.service("sensor.kiln_temp", "turn_on")

    def toaster() -> Call:
        return home.state("toaster.oven")

    def cover_on_light() -> Call:
        return home.service("light.kitchen", "open_cover")

    def raw_rm() -> Call:
        return home.service("light.kitchen", "rm")

    def shouted() -> Call:
        return home.service("light.kitchen", "TURN_ON")

    _expect("BAD_DOMAIN", sensor_on)
    _expect("BAD_DOMAIN", toaster)
    _expect("BAD_SERVICE", cover_on_light)
    _expect("BAD_SERVICE", raw_rm)
    _expect("BAD_SERVICE", shouted)

    def mismatch() -> Call:
        return replace(reading, domain="switch")

    _expect("BAD_DOMAIN", mismatch)


def test_service_data_cap_and_climate() -> None:
    home = _home()
    call = home.service(
        "light.kitchen",
        "turn_on",
        {"color_name": "blue", "brightness": 128},
        cap=99,
    )
    assert classify(call) == CONFIRM
    assert call.cap == POLICY_FIELDS
    assert call.requested_cap == 99
    assert call.clamped == ("cap",)
    assert _field(call, 0) == Field(key="brightness", value="128")
    assert _field(call, 1) == Field(key="color_name", value="blue")
    _expect("NOT_RUN", _launch(call))

    climate = home.service(
        "climate.thermostat",
        "set_temperature",
        {"temperature": 22, "hvac_mode": "heat"},
    )
    assert classify(climate) == CONFIRM
    assert _field(climate, 0).key == "hvac_mode"
    assert _field(climate, 1).value == "22"
    mode = home.service(
        "climate.thermostat",
        "set_hvac_mode",
        {"hvac_mode": "off"},
    )
    assert classify(mode) == CONFIRM
    assert mode.code == CONFIRM
    _expect("NOT_RUN", _launch(mode))

    volume = home.service(
        "media_player.kitchen_speaker",
        "set_volume_level",
        {"volume_level": 40},
    )
    cover = home.service("cover.shade", "set_cover_position", {"position": 50})
    fan = home.service("fan.bench", "set_percentage", {"percentage": 30})
    assert classify(volume) == CONFIRM
    assert classify(cover) == CONFIRM
    assert classify(fan) == CONFIRM

    def low_cap() -> Call:
        return home.service(
            "light.kitchen",
            "turn_on",
            {"brightness": 10, "color_name": "blue"},
            cap=1,
        )

    def extra() -> Call:
        return home.service("light.kitchen", "turn_on", {"transition": 1})

    def five() -> Call:
        payload: dict[str, object] = {f"k{index}": index for index in range(5)}
        return home.service("light.kitchen", "turn_on", payload, cap=100)

    def bad_color() -> Call:
        return home.service("light.kitchen", "turn_on", {"color_name": "Blue"})

    def hot() -> Call:
        return home.service(
            "climate.thermostat",
            "set_temperature",
            {"temperature": 1200},
        )

    def bright() -> Call:
        return home.service("light.kitchen", "turn_on", {"brightness": 256})

    def flag() -> Call:
        return home.service("light.kitchen", "turn_on", {"brightness": True})

    def text_level() -> Call:
        return home.service("light.kitchen", "turn_on", {"brightness": "128"})

    def fraction() -> Call:
        return home.service(
            "media_player.kitchen_speaker",
            "set_volume_level",
            {"volume_level": 0.4},
        )

    def not_map() -> Call:
        return home.service("light.kitchen", "turn_on", ["brightness", 10])

    def turn_off_data() -> Call:
        return home.service("light.kitchen", "turn_off", {"brightness": 1})

    _expect("BAD_DATA", low_cap)
    _expect("BAD_DATA", extra)
    _expect("BAD_DATA", five)
    _expect("BAD_DATA", bad_color)
    _expect("OUT_OF_RANGE", hot)
    _expect("OUT_OF_RANGE", bright)
    _expect("NOT_INT", flag)
    _expect("NOT_INT", text_level)
    _expect("NOT_INT", fraction)
    _expect("NOT_MAP", not_map)
    _expect("BAD_DATA", turn_off_data)

    plain = home.service("light.kitchen", "turn_on")

    def duplicate() -> Call:
        return replace(
            plain,
            data=(
                Field(key="brightness", value="10"),
                Field(key="brightness", value="10"),
            ),
        )

    def unsorted() -> Call:
        return replace(
            plain,
            data=(
                Field(key="color_name", value="blue"),
                Field(key="brightness", value="10"),
            ),
        )

    _expect("DUPLICATE", duplicate)
    _expect("BAD_RECORD", unsorted)


def test_reads_lists_and_scripts_do_not_run() -> None:
    home = _home()
    names = (
        "binary_sensor.front_door",
        "alarm_control_panel.home",
        "lock.front_door",
        "weather.porch",
        "camera.driveway",
        "person.ada",
    )
    for name in names:
        reading = home.state(name)
        assert classify(reading) == CONFIRM
        _expect("NOT_RUN", _launch(reading))
    scene = home.service("scene.movie_night", "turn_on")
    script = home.service("script.morning", "turn_on")
    assert classify(scene) == CONFIRM
    assert classify(script) == CONFIRM
    _expect("NOT_RUN", _launch(scene))
    _expect("NOT_RUN", _launch(script))
    listed = home.list_entities("sensor", "kiln shed", cap=1_000)
    assert listed.cap == POLICY_LIST
    assert listed.requested_cap == 1_000
    assert listed.clamped == ("cap",)
    assert listed.area == "kiln shed"
    services = home.list_services()
    assert services.domain == ""
    assert services.cap == POLICY_LIST
    state = home.state("sensor.kiln_temp", cap=9)
    assert state.cap == POLICY_STATE
    assert state.requested_cap == 9
    assert state.clamped == ("cap",)

    def bad_area() -> Call:
        return home.list_entities("light", "Kitchen")

    def blank_domain() -> tuple[str, ...]:
        return catalog("")

    _expect("BAD_AREA", bad_area)
    _expect("EMPTY", blank_domain)


def test_budget_skips_without_dropping_later_calls() -> None:
    home = _home()
    huge = home.state("sensor." + ("h" * 73))
    big = home.state("sensor." + ("k" * 60))
    mid = home.state("sensor.kiln_temp")
    tiny = home.list_entities()
    assert weight(huge) > POLICY_BUDGET
    assert weight(big) <= POLICY_BUDGET
    assert weight(big) + weight(mid) > POLICY_BUDGET
    assert weight(big) + weight(tiny) <= POLICY_BUDGET
    items = (huge, big, mid, tiny)
    planned = home.plan(items, now=80)
    assert _kept_sources(planned) == (1, 3)
    assert _skip_sources(planned) == (0, 2)
    assert _skip(planned, 0).reason == "BUDGET"
    assert _step(planned, 0).call == big
    assert _step(planned, 1).call == tiny
    assert rebuild(planned) == planned
    assert planned.budget == POLICY_BUDGET
    assert planned.clamped == ()
    raised = home.plan(list(items), now=80, budget=10_000)
    assert raised.budget == POLICY_BUDGET
    assert raised.requested_budget == 10_000
    assert raised.clamped == ("budget",)
    assert _kept_sources(raised) == (1, 3)
    tight = home.plan(items, now=80, budget=10)
    assert tight.budget == 10
    assert tight.requested_budget == 10
    assert _kept_sources(tight) == (3,)
    assert _skip_sources(tight) == (0, 1, 2)
    assert home.plan([tiny], now=3) == home.plan((tiny,), now=3)
    empty = home.plan((), now=10, seen=10)
    assert rebuild(empty) == empty
    assert _kept(empty) == 0

    def over() -> Plan:
        return home.plan((tiny,) * (POLICY_ITEMS + 1), now=1)

    def bare() -> Plan:
        return home.plan("light.kitchen", now=1)

    def early() -> Plan:
        return home.plan((tiny,), now=4, seen=5)

    def dup() -> Plan:
        call = home.service("light.kitchen", "turn_on")
        return home.plan((call, home.service("light.kitchen", "turn_on")), now=1)

    def foreign() -> Plan:
        other = Home()
        other.enable("hass-porch")
        return home.plan((other.service("light.kitchen", "turn_on"),), now=1)

    def number() -> Plan:
        return home.plan((1,), now=1)

    _expect("OVERSIZE", over)
    _expect("NOT_LIST", bare)
    _expect("STALE", early)
    _expect("DUPLICATE", dup)
    _expect("MISMATCH", foreign)
    _expect("BAD_KIND", number)


def test_retry_is_one_confirm_and_still_does_not_run() -> None:
    home = _home()
    call = home.state("sensor.kiln_temp")
    again = retry(call, FAILURE)
    assert again.attempt == 2
    assert again.digest == call.digest
    assert classify(again) == CONFIRM
    _expect("NOT_RUN", _launch(again))

    def third() -> Call:
        return retry(again, FAILURE)

    def other() -> Call:
        return retry(call, "TRANSIENT")

    def blank() -> Call:
        return retry(call, "")

    def secret() -> Call:
        return retry(call, "api_key=abcdefgh")

    def missing() -> Call:
        return retry(call, None)

    _expect("RETRY_CAP", third)
    _expect("NO_RETRY", other)
    _expect("EMPTY", blank)
    _expect("SECRET", secret)
    _expect("EMPTY", missing)
    edge = home.plan((call,), now=MAX_STAMP)
    assert edge.now == MAX_STAMP

    def past() -> Plan:
        return home.plan((call,), now=MAX_STAMP + 1)

    def bad_now() -> Plan:
        return home.plan((call,), now=None)

    def flag_now() -> Plan:
        return home.plan((call,), now=True)

    def zero_budget() -> Plan:
        return home.plan((call,), now=1, budget=0)

    _expect("OUT_OF_RANGE", past)
    _expect("NOT_INT", bad_now)
    _expect("NOT_INT", flag_now)
    _expect("OUT_OF_RANGE", zero_budget)


def test_records_refuse_tampering() -> None:
    home = _home()
    call = home.service("light.kitchen", "turn_on")
    reading = home.state("sensor.kiln_temp")

    def schema() -> Call:
        return replace(call, schema="cosmos-hermes-other/1")

    def yolo() -> Call:
        return replace(call, code="yolo")

    def off() -> Call:
        return replace(call, code="off")

    def kind() -> Call:
        return replace(call, kind="exec")

    def cap() -> Call:
        return replace(call, cap=9)

    def chain() -> Call:
        return replace(call, digest="ab" * 32)

    def attempt() -> Call:
        return replace(call, attempt=3)

    def flag() -> Call:
        return replace(call, attempt=True)

    _expect("BAD_SCHEMA", schema)
    _expect("UNCLASSIFIED", yolo)
    _expect("UNCLASSIFIED", off)
    _expect("BAD_KIND", kind)
    _expect("BAD_CAP", cap)
    _expect("BROKEN_CHAIN", chain)
    _expect("OUT_OF_RANGE", attempt)
    _expect("NOT_INT", flag)

    wide = home.plan((call,), now=5)
    step = _step(wide, 0)

    def broken() -> Plan:
        return replace(wide, steps=(replace(step, digest="ab" * 32),))

    def over_budget() -> Plan:
        return Plan(
            schema=SCHEMA,
            cred_id=home.credential_id,
            now=5,
            seen=None,
            budget=10,
            requested_budget=10,
            clamped=(),
            steps=(step,),
            skipped=(),
            digest="ab" * 32,
        )

    def bad_skip() -> Skip:
        return Skip(call=reading, source=0, cost=0, reason="BUDGET")

    def bad_reason() -> Skip:
        return Skip(call=reading, source=0, cost=weight(reading), reason="NOPE")

    _expect("BROKEN_CHAIN", broken)
    _expect("BAD_RECORD", over_budget)
    _expect("BAD_RECORD", bad_skip)
    _expect("BAD_RECORD", bad_reason)

    def unclassified() -> str:
        return classify(None)

    def run_plan() -> None:
        run(wide)

    def rebuild_call() -> Plan:
        return rebuild(call)

    def weigh() -> int:
        return weight(None)

    _expect("UNCLASSIFIED", unclassified)
    _expect("UNCLASSIFIED", run_plan)
    _expect("BAD_RECORD", rebuild_call)
    _expect("BAD_KIND", weigh)

    def nul() -> Call:
        return home.service("light.kit\x00chen", "turn_on")

    def huge_entity() -> Call:
        return home.service("light." + ("k" * ENTITY_CAP), "turn_on")

    def huge_action() -> Call:
        return home.service("light.kitchen", "a" * (NAME_CAP + 1))

    def huge_area() -> Call:
        return home.list_entities("light", "a" * (AREA_CAP + 1))

    def missing_entity() -> Call:
        return home.service(None, "turn_on")

    def secret_entity() -> Call:
        return home.service("light.sk-abcdefghij", "turn_on")

    def secret_action() -> Call:
        return home.service("light.kitchen", "api_key=abcdefgh")

    def secret_area() -> Call:
        return home.list_entities("light", "api_key=abcdefgh")

    _expect("NULL_BYTE", nul)
    _expect("OVERSIZE", huge_entity)
    _expect("OVERSIZE", huge_action)
    _expect("OVERSIZE", huge_area)
    _expect("NOT_TEXT", missing_entity)
    _expect("SECRET", secret_entity)
    _expect("SECRET", secret_action)
    _expect("SECRET", secret_area)


def test_repr_and_source_stay_clean() -> None:
    home = _home()
    call = home.service(
        "light.kitchen",
        "turn_on",
        {"brightness": 128, "color_name": "blue"},
    )
    plan = home.plan((call, home.state("sensor.kiln_temp")), now=1_721_000_000)
    blob = "\n".join(repr(item) for item in (home, call, plan, _field(call, 0)))
    assert secret_shape(blob) is False
    assert "sk-" not in blob
    assert "Bearer" not in blob
    assert "api_key=" not in blob
    path = home_assistant.__file__
    assert path is not None
    tree = ast.parse(Path(path).read_text(encoding="utf-8"))
    banned = {
        "asyncio",
        "ctypes",
        "http",
        "pickle",
        "requests",
        "socket",
        "subprocess",
        "urllib",
    }
    found: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".", 1)[0]
                if root in banned:
                    found.append(root)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            root = module.split(".", 1)[0]
            if root in banned:
                found.append(root)
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id in {"__import__", "compile", "eval", "exec"}:
                found.append(node.func.id)
    assert found == []
