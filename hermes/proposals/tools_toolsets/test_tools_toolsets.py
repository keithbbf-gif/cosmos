"""Allow, deny, preset expansion, and messaging-terminal resolution."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import cast

from cosmos_hermes import Refuse, secret_shape
from tools_toolsets import (
    LIST_CAP,
    NAME_CAP,
    PLATFORMS,
    PRESETS,
    REGISTRY_CAP,
    SCHEMA,
    Catalog,
    Effective,
    Tool,
    effective,
    new_catalog,
    rebuild,
    register,
)


def _code(call: Callable[[], object]) -> str:
    try:
        call()
    except Refuse as err:
        return err.code
    raise AssertionError("expected Refuse")


def _tool_at(tools: tuple[Tool, ...], index: int) -> Tool:
    if index < 0 or index >= len(tools):
        raise AssertionError("index")
    return tools[index]


def _catalog() -> Catalog:
    cat = new_catalog(name_cap=10_000, registry_cap=10_000)
    cat = register(cat, "read_file", "file", "read", name_cap=10_000)
    cat = register(cat, "write_file", "file", "write")
    cat = register(cat, "terminal", "terminal", "terminal")
    cat = register(cat, "process", "terminal", "terminal")
    cat = register(cat, "web_search", "web", "net")
    cat = register(cat, "ha_call_service", "homeassistant", "admin")
    return cat


def _register_members(members: tuple[str, ...]) -> Catalog:
    catalog = new_catalog()
    for member in members:
        risk = "terminal" if member == "terminal" else "read"
        catalog = register(catalog, f"use_{member}", member, risk)
    return catalog


def test_schema_and_cli_success() -> None:
    cat = _catalog()
    got = effective("cli", ["file", "terminal"], catalog=cat)
    again = effective("cli", ["file", "terminal"], None, catalog=cat)
    assert SCHEMA == "cosmos-hermes-tools_toolsets/1"
    assert got == again
    assert got.platform == "cli"
    assert got.name_cap == NAME_CAP
    assert got.list_cap == LIST_CAP
    assert got.toolsets == ("file", "terminal")
    assert [(tool.name, tool.toolset, tool.risk) for tool in got.tools] == [
        ("read_file", "file", "read"),
        ("write_file", "file", "write"),
        ("terminal", "terminal", "terminal"),
        ("process", "terminal", "terminal"),
    ]
    assert all(tool.name != "web_search" for tool in got.tools)
    assert not secret_shape(repr(got))
    assert not secret_shape(repr(cat))
    members = PRESETS["hermes-cli"]
    covered = _register_members(members)
    preset = effective("cli", ["hermes-cli"], catalog=covered)
    assert preset.toolsets == members
    assert "terminal" in preset.toolsets
    assert rebuild(covered.tools) == covered


def test_example_tools_toolsets() -> None:
    def once() -> tuple[Effective, Catalog]:
        catalog = new_catalog()
        catalog = register(catalog, "kanban_show", "kanban", "read")
        catalog = register(catalog, "memory", "memory", "write")
        catalog = register(catalog, "ha_call_service", "homeassistant", "admin")
        catalog = register(catalog, "terminal", "terminal", "terminal")
        resolved = effective(
            "telegram",
            ["kanban", "memory", "homeassistant"],
            catalog=catalog,
        )
        return resolved, rebuild(catalog.tools)

    first = once()
    second = once()
    assert first == second
    resolved = first[0]
    assert resolved.platform == "telegram"
    assert [tool.name for tool in resolved.tools] == [
        "kanban_show",
        "memory",
        "ha_call_service",
    ]
    assert resolved.toolsets == ("kanban", "memory", "homeassistant")
    assert "terminal" not in resolved.toolsets
    assert all(tool.risk != "terminal" for tool in resolved.tools)
    assert first[1].tools == second[1].tools


def test_preset_table_is_data() -> None:
    assert PRESETS["hermes-telegram"] == PRESETS["hermes-cli"]
    assert "terminal" in PRESETS["hermes-telegram"]
    assert "terminal" in PRESETS["hermes-discord"]
    assert "terminal" in PRESETS["debugging"]
    assert "terminal" in PRESETS["coding"]
    assert "terminal" not in PRESETS["hermes-webhook"]
    assert "terminal" not in PRESETS["safe"]
    assert len(PLATFORMS) == len(set(PLATFORMS))
    assert "cli" in PLATFORMS
    assert "yolo" not in PLATFORMS
    assert "off" not in PLATFORMS
    for members in PRESETS.values():
        assert len(members) <= LIST_CAP
        seen: set[str] = set()
        for member in members:
            assert member not in PRESETS
            assert member not in seen
            seen.add(member)
    assert len(PRESETS["hermes-gateway"]) <= LIST_CAP


def test_empty_allow() -> None:
    cat = _catalog()

    def missing() -> Effective:
        return effective("cli", None, catalog=cat)

    def empty_list() -> Effective:
        return effective("telegram", [], ["terminal"], catalog=cat)

    def empty_tuple() -> Effective:
        return effective("cli", (), catalog=cat)

    assert _code(missing) == "EMPTY_ALLOW"
    assert _code(empty_list) == "EMPTY_ALLOW"
    assert _code(empty_tuple) == "EMPTY_ALLOW"


def test_messaging_terminal() -> None:
    cat = _catalog()
    bare = register(new_catalog(), "read_file", "file", "read")
    covered = _register_members(PRESETS["hermes-cli"])

    def telegram_names() -> Effective:
        return effective("telegram", ["file", "terminal"], catalog=cat)

    def discord_denied() -> Effective:
        return effective("discord", ["terminal"], ["terminal"], catalog=cat)

    def slack_unknown_too() -> Effective:
        return effective("slack", ["terminal", "nope"], catalog=bare)

    def stock_preset() -> Effective:
        return effective("telegram", ["hermes-telegram"], catalog=covered)

    def debugging_bundle() -> Effective:
        return effective("telegram", ["debugging"], ["debugging"], catalog=cat)

    def coding_bundle() -> Effective:
        return effective("slack", ["coding"], catalog=cat)

    assert _code(telegram_names) == "MESSAGING_TERMINAL"
    assert _code(discord_denied) == "MESSAGING_TERMINAL"
    assert _code(slack_unknown_too) == "MESSAGING_TERMINAL"
    assert _code(stock_preset) == "MESSAGING_TERMINAL"
    assert _code(debugging_bundle) == "MESSAGING_TERMINAL"
    assert _code(coding_bundle) == "MESSAGING_TERMINAL"
    kept = effective("telegram", ["file", "homeassistant"], ["homeassistant"], catalog=cat)
    assert [tool.name for tool in kept.tools] == ["read_file", "write_file"]
    assert kept.toolsets == ("file",)
    assert all(tool.toolset != "terminal" for tool in kept.tools)
    hook = register(new_catalog(), "read_file", "ops", "read")
    hook = register(hook, "process", "ops", "terminal")

    def smuggle() -> Effective:
        return effective("telegram", ["ops"], catalog=hook)

    assert _code(smuggle) == "MESSAGING_TERMINAL"
    dropped = effective("telegram", ["ops"], disabled_tools=["process"], catalog=hook)
    assert [tool.name for tool in dropped.tools] == ["read_file"]
    assert dropped.toolsets == ("ops",)
    wh = new_catalog()
    wh = register(wh, "web_search", "web", "net")
    wh = register(wh, "web_extract", "web", "net")
    wh = register(wh, "vision_analyze", "vision", "read")
    wh = register(wh, "clarify", "clarify", "read")
    wh = register(wh, "terminal", "terminal", "terminal")
    safe = effective("telegram", ["hermes-webhook"], catalog=wh)
    assert [tool.name for tool in safe.tools] == [
        "web_search",
        "web_extract",
        "vision_analyze",
        "clarify",
    ]
    assert safe.toolsets == ("web", "vision", "clarify")
    assert "terminal" not in safe.toolsets

    def built() -> Effective:
        tool = Tool("process", "file", "terminal")
        return Effective(platform="telegram", tools=(tool,), toolsets=("file",))

    assert _code(built) == "MESSAGING_TERMINAL"


def test_deny_wins() -> None:
    cat = _catalog()
    got = effective("cli", ["file", "web", "terminal"], ["file", "terminal"], catalog=cat)
    assert [tool.name for tool in got.tools] == ["web_search"]
    assert got.toolsets == ("web",)
    wiped = effective("cli", ["web"], ["web"], catalog=cat)
    assert wiped.tools == ()
    assert wiped.toolsets == ()
    assert wiped.name_cap == NAME_CAP
    bundle = effective("cli", ["debugging"], catalog=cat)
    assert bundle.toolsets == ("file", "terminal", "web")
    assert [tool.name for tool in bundle.tools] == [
        "read_file",
        "write_file",
        "terminal",
        "process",
        "web_search",
    ]
    denied_bundle = effective(
        "cli",
        ["debugging", "homeassistant"],
        ["debugging"],
        catalog=cat,
    )
    assert [tool.name for tool in denied_bundle.tools] == ["ha_call_service"]
    kept = effective("cli", ["file"], disabled_tools=["read_file"], catalog=cat)
    assert [tool.name for tool in kept.tools] == ["write_file"]
    assert kept.toolsets == ("file",)


def test_unknown_toolset() -> None:
    cat = _catalog()

    def missing_allow() -> Effective:
        return effective("cli", ["file", "nope"], catalog=cat)

    def missing_deny() -> Effective:
        return effective("cli", ["file"], ["nope"], catalog=cat)

    def star_all() -> Effective:
        return effective("cli", ["all"], catalog=cat)

    def star() -> Effective:
        return effective("cli", ["*"], catalog=cat)

    def pager() -> Effective:
        return effective("pager", ["file"], catalog=cat)

    def missing_tool() -> Effective:
        return effective("cli", ["file"], disabled_tools=["no_tool"], catalog=cat)

    assert _code(missing_allow) == "UNKNOWN_TOOLSET"
    assert _code(missing_deny) == "UNKNOWN_TOOLSET"
    assert _code(star_all) == "UNKNOWN_TOOLSET"
    assert _code(star) == "BAD_NAME"
    assert _code(pager) == "UNKNOWN_PLATFORM"
    assert _code(missing_tool) == "UNKNOWN_TOOL"


def test_cap_stays_policy() -> None:
    made = new_catalog(name_cap=1, registry_cap=1)
    assert made.name_cap == NAME_CAP
    assert made.registry_cap == REGISTRY_CAP
    direct = Catalog(name_cap=100_000, registry_cap=100_000)
    assert direct.name_cap == NAME_CAP
    assert direct.registry_cap == REGISTRY_CAP
    wide = "a" * NAME_CAP
    named = register(new_catalog(), wide, "file", "read", name_cap=99_999, registry_cap=99_999)
    assert _tool_at(named.tools, 0).name == wide
    assert named.name_cap == NAME_CAP

    def oversized() -> Catalog:
        return register(named, "b" * (NAME_CAP + 1), "file", "write", name_cap=99_999)

    assert _code(oversized) == "OVERSIZE"
    filled = new_catalog()
    for index in range(REGISTRY_CAP):
        filled = register(filled, f"tool{index}", "file", "read", registry_cap=50_000)
    assert len(filled.tools) == REGISTRY_CAP
    assert filled.registry_cap == REGISTRY_CAP

    def overflow() -> Catalog:
        return register(filled, "overflow", "file", "read", registry_cap=50_000)

    assert _code(overflow) == "OVER_CAP"
    too_many = tuple(f"n{index}" for index in range(LIST_CAP + 1))

    def long_allow() -> Effective:
        return effective("cli", too_many, catalog=named)

    assert _code(long_allow) == "OVER_CAP"
    wide_allow = ["hermes-cli", *[f"extra{index}" for index in range(LIST_CAP - 1)]]

    def expanded() -> Effective:
        return effective("cli", wide_allow, catalog=named)

    assert len(wide_allow) == LIST_CAP
    assert _code(expanded) == "OVER_CAP"
    forced = Effective(platform="cli", tools=(), name_cap=1)
    assert forced.name_cap == NAME_CAP
    assert forced.list_cap == LIST_CAP
    both = effective("cli", ["file", "web"], catalog=_catalog(), list_cap=1, name_cap=99_999)
    assert both.list_cap == LIST_CAP
    assert both.name_cap == NAME_CAP
    assert len(both.tools) > 1

    def zero() -> Catalog:
        return new_catalog(name_cap=0)

    def flagged() -> Catalog:
        return new_catalog(name_cap=True)

    def text_cap() -> Catalog:
        return new_catalog(registry_cap="64")

    assert _code(zero) == "BAD_CAP"
    assert _code(flagged) == "BAD_CAP"
    assert _code(text_cap) == "BAD_CAP"


def test_rebuild_round_trip() -> None:
    cat = _catalog()
    assert rebuild(cat.tools) == cat
    assert rebuild(()) == new_catalog()

    def from_text() -> Catalog:
        return rebuild("read_file")

    def broken() -> Catalog:
        return rebuild(("x",))

    assert _code(from_text) == "NOT_LIST"
    assert _code(broken) == "BAD_RECORD"


def test_other_refusals() -> None:
    cat = _catalog()

    def bad_risk() -> Catalog:
        return register(new_catalog(), "read_file", "file", "exec")

    def bad_name() -> Catalog:
        return register(new_catalog(), "File", "file", "read")

    def secret() -> Catalog:
        return register(new_catalog(), "sk-abcdefghij", "file", "read")

    assert _code(bad_risk) == "BAD_RISK"
    assert _code(bad_name) == "BAD_NAME"
    try:
        secret()
    except Refuse as err:
        assert err.code == "SECRET_SHAPE"
        assert not secret_shape(str(err))
    else:
        raise AssertionError("expected Refuse")
    once = register(new_catalog(), "read_file", "file", "read")

    def duplicate() -> Catalog:
        return register(once, "read_file", "web", "net")

    def duplicate_allow() -> Effective:
        return effective("cli", ["file", "file"], catalog=cat)

    def not_list() -> Effective:
        return effective("cli", "file", catalog=cat)

    def nul() -> Effective:
        return effective("cli\x00", ["file"], catalog=cat)

    def missing_platform() -> Effective:
        return effective(None, ["file"], catalog=cat)

    mixed: Sequence[object] = ["file", 1]

    def mixed_item() -> Effective:
        return effective("cli", mixed, catalog=cat)

    def bad_catalog() -> Effective:
        return effective("cli", ["file"], catalog="nope")

    def bad_tools() -> Catalog:
        return Catalog(tools=cast(tuple[Tool, ...], ("x",)))

    assert _code(duplicate) == "DUPLICATE"
    assert _code(duplicate_allow) == "DUPLICATE"
    assert _code(not_list) == "NOT_LIST"
    assert _code(nul) == "NULL_BYTE"
    assert _code(missing_platform) == "NOT_TEXT"
    assert _code(mixed_item) == "NOT_TEXT"
    assert _code(bad_catalog) == "BAD_RECORD"
    assert _code(bad_tools) == "BAD_RECORD"
    tool = _tool_at(cat.tools, 0)
    try:
        setattr(tool, "name", "other")
    except AttributeError:
        frozen = True
    else:
        frozen = False
    assert frozen
