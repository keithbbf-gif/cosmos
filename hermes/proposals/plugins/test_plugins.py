"""Allowlisted injected callables, the policy cap, and a closed disk import."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import fields, replace
from pathlib import Path

import pytest

from cosmos_hermes import Refuse, secret_shape
from plugins import (
    CATALOG_BUDGET,
    GENESIS,
    KINDS,
    PERMISSIONS,
    POLICY_CAP,
    SCHEMA,
    TEXT_CAP,
    Catalog,
    Link,
    Plugin,
    Registry,
    Result,
    load_from_path,
    seal,
)

_SIGNER = "lab-signer"
_BLURB = "Tool line."


def _echo(text: str) -> str:
    return text


def _refuse(action: Callable[[], object], code: str, detail: str | None = None) -> None:
    with pytest.raises(Refuse) as caught:
        action()
    assert caught.value.code == code
    if detail is not None:
        assert caught.value.detail == detail


def _add(
    registry: Registry,
    name: str,
    *,
    kind: str = "tool",
    permissions: object = (),
    grant: object = (),
    handler: Callable[[str], str] = _echo,
    description: str = _BLURB,
) -> Plugin:
    return registry.register(
        name,
        kind,
        permissions,
        grant,
        handler,
        seal(_SIGNER, name),
        description,
    )


def test_schema_kinds_and_caps() -> None:
    assert SCHEMA == "cosmos-hermes-plugins/1"
    assert POLICY_CAP == 32
    assert CATALOG_BUDGET == 512
    assert TEXT_CAP == 256
    assert GENESIS == "0" * 64
    assert KINDS == ("tool", "memory", "context")
    assert "tools.override" in PERMISSIONS
    assert "gateway.platform_actions" in PERMISSIONS
    registry = Registry(("clock",), _SIGNER)
    assert registry.cap == POLICY_CAP
    assert registry.requested == POLICY_CAP
    assert registry.fence == GENESIS
    assert registry.entries() == ()
    assert registry.links() == ()


def test_example_plugins() -> None:
    called: list[str] = []

    def clock(text: str) -> str:
        called.append("clock")
        return (
            f"Session {text}: the lumen card stays on the hook, "
            "the note sits under the aisle light, and the clock matches the stamp."
        )

    def shell(text: str) -> str:
        called.append("shell")
        return text

    def note(text: str) -> str:
        called.append("note")
        return text

    def run() -> tuple[object, ...]:
        registry = Registry(("clock", "note"), _SIGNER, POLICY_CAP * 4)

        def reject_shell() -> None:
            registry.register(
                "shell",
                "tool",
                (),
                (),
                shell,
                seal(_SIGNER, "shell"),
                "Not on the lab allowlist.",
            )

        def reject_note() -> None:
            registry.register(
                "note",
                "tool",
                (),
                (),
                note,
                "0" * 64,
                "Holds the lumen card note.",
            )

        plugin = registry.register(
            "clock",
            "tool",
            (),
            (),
            clock,
            seal(_SIGNER, "clock"),
            "Shows the session clock beside the aisle light.",
        )
        _refuse(reject_shell, "NOT_ALLOWED", "shell")
        _refuse(reject_note, "UNSIGNED")
        result = registry.call("clock", "evening")

        def call_shell() -> None:
            registry.call("shell", "evening")

        def call_note() -> None:
            registry.call("note", "evening")

        _refuse(call_shell, "NOT_ALLOWED", "shell")
        _refuse(call_note, "UNKNOWN", "note")
        return (
            plugin,
            result,
            registry.entries(),
            registry.links(),
            registry.catalog(),
            registry.cap,
            registry.requested,
            registry.fence,
            repr(plugin),
            repr(result),
            repr(registry),
        )

    first = run()
    second = run()
    assert first == second
    assert called == ["clock", "clock"]
    plugin = first[0]
    result = first[1]
    assert isinstance(plugin, Plugin)
    assert isinstance(result, Result)
    assert plugin == Plugin("clock", "call-0001", "tool")
    assert result.text == (
        "Session evening: the lumen card stays on the hook, "
        "the note sits under the aisle light, and the clock matches the stamp."
    )
    assert result.callable_id == "call-0001"
    assert first[5] == POLICY_CAP
    assert first[6] == POLICY_CAP * 4
    assert secret_shape(repr(plugin)) is False
    assert secret_shape(repr(result)) is False
    assert secret_shape(str(first[10])) is False
    assert "<function" not in str(first[10])
    assert "sk-" not in str(first[10])


def test_register_runs_the_injected_callable() -> None:
    seen: list[str] = []

    def clock(text: str) -> str:
        seen.append(text)
        return f"stamp {text}"

    registry = Registry(("clock", "notes", "pack"), _SIGNER)
    tool = _add(
        registry,
        "clock",
        handler=clock,
        permissions=PERMISSIONS,
        grant=PERMISSIONS,
        description="Shows the session clock beside the aisle light.",
    )
    memory = _add(registry, "notes", kind="memory", description="Holds the lumen card note.")
    context = _add(registry, "pack", kind="context", description="Packs the session light.")
    assert tool == Plugin("clock", "call-0001", "tool")
    assert memory == Plugin("notes", "call-0002", "memory")
    assert context.kind == "context"
    assert registry.call("clock", "evening") == Result("clock", "call-0001", "stamp evening")
    assert seen == ["evening"]
    assert registry.get("notes") == memory
    assert registry.entries() == (tool, memory, context)
    assert tuple(field.name for field in fields(tool)) == ("name", "callable_id", "kind")
    assert not hasattr(tool, "__dict__")
    assert not hasattr(tool, "handler")
    assert not callable(tool)
    link = registry.links()[0]
    assert link.prior == GENESIS
    assert link.permissions == PERMISSIONS
    assert registry.fence == registry.links()[2].digest
    assert "Shows the session clock" not in repr(tool)


def test_exclusive_second_provider() -> None:
    registry = Registry(("notes", "other", "pack", "more"), _SIGNER)
    _add(registry, "notes", kind="memory", description="Holds the lumen card note.")
    _add(registry, "pack", kind="context", description="Packs the session light.")

    def second_memory() -> None:
        _add(registry, "other", kind="memory", description="Holds another note.")

    def second_context() -> None:
        _add(registry, "more", kind="context", description="Packs another light.")

    _refuse(second_memory, "EXCLUSIVE", "memory")
    _refuse(second_context, "EXCLUSIVE", "context")
    assert tuple(row.name for row in registry.entries()) == ("notes", "pack")
    assert registry.fence != GENESIS


def test_permission_grant_and_unclassified() -> None:
    registry = Registry(("clock",), _SIGNER)

    def missing() -> None:
        registry.register(
            "clock",
            "tool",
            ("tools.override", "llm.model_override"),
            ("tools.override",),
            _echo,
            seal(_SIGNER, "clock"),
            _BLURB,
        )

    def empty_grant() -> None:
        registry.register(
            "clock",
            "tool",
            ("tools.override",),
            (),
            _echo,
            seal(_SIGNER, "clock"),
            _BLURB,
        )

    def unknown() -> None:
        registry.register(
            "clock",
            "tool",
            ("clipboard.read",),
            ("clipboard.read",),
            _echo,
            seal(_SIGNER, "clock"),
            _BLURB,
        )

    def repeated() -> None:
        registry.register(
            "clock",
            "tool",
            ("tools.override", "tools.override"),
            ("tools.override",),
            _echo,
            seal(_SIGNER, "clock"),
            _BLURB,
        )

    _refuse(missing, "PERMISSION", "llm.model_override")
    _refuse(empty_grant, "PERMISSION", "tools.override")
    _refuse(unknown, "UNCLASSIFIED")
    _refuse(repeated, "DUPLICATE")
    assert registry.entries() == ()
    assert registry.fence == GENESIS
    admitted = _add(registry, "clock", permissions=(), grant=())
    assert admitted.name == "clock"

    def again() -> None:
        _add(registry, "clock")

    _refuse(again, "DUPLICATE")
    assert len(registry.entries()) == 1


def test_deny_wins_and_unknown_is_absent() -> None:
    blocked = Registry(("clock",), _SIGNER, deny=("clock",))

    def register_blocked() -> None:
        _add(blocked, "clock")

    def call_blocked() -> None:
        blocked.call("clock", "evening")

    _refuse(register_blocked, "DENIED", "clock")
    _refuse(call_blocked, "DENIED", "clock")
    assert blocked.entries() == ()
    registry = Registry(("clock", "note"), _SIGNER)
    _add(registry, "clock")

    def missing_call() -> None:
        registry.call("note", "evening")

    def missing_get() -> None:
        registry.get("note")

    _refuse(missing_call, "UNKNOWN", "note")
    _refuse(missing_get, "ABSENT", "note")
    assert registry.get("clock").callable_id == "call-0001"


def test_cap_ignores_higher_request_and_fills() -> None:
    names = tuple(f"p{index}" for index in range(POLICY_CAP))
    registry = Registry(names, _SIGNER, 10_000)
    assert registry.cap == POLICY_CAP
    assert registry.requested == 10_000
    for index, name in enumerate(names):
        row = _add(registry, name)
        assert row.callable_id == f"call-{index + 1:04d}"
    assert len(registry.entries()) == POLICY_CAP
    assert registry.entries()[-1].callable_id == "call-0032"

    def overflow() -> None:
        _add(registry, "overflow")

    def duplicate() -> None:
        _add(registry, "p0")

    _refuse(overflow, "NOT_ALLOWED", "overflow")
    _refuse(duplicate, "DUPLICATE")
    assert len(registry.entries()) == POLICY_CAP
    tight = Registry(("one", "two", "three"), _SIGNER, 2)
    assert tight.cap == 2
    assert tight.requested == 2
    _add(tight, "one")
    _add(tight, "two")

    def third() -> None:
        _add(tight, "three")

    _refuse(third, "FULL")
    assert len(tight.entries()) == 2


def test_catalog_skips_and_continues() -> None:
    short = "Ace."
    long = "This description is far too long for a tiny budget."
    tail = "Note."
    registry = Registry(("ace", "ledger", "note"), _SIGNER)
    _add(registry, "ace", description=short)
    _add(registry, "ledger", description=long)
    _add(registry, "note", description=tail)
    budget = len(short) + len(tail)
    picked = registry.catalog(budget)
    assert picked == Catalog(("ace", "note"), ("ledger",), budget, budget)
    assert picked.names == ("ace", "note")
    assert picked.skipped == ("ledger",)
    wide = registry.catalog(CATALOG_BUDGET * 4)
    assert wide.budget == CATALOG_BUDGET
    assert wide.requested == CATALOG_BUDGET * 4
    assert wide.names == ("ace", "ledger", "note")
    assert wide.skipped == ()

    def bad_budget() -> None:
        registry.catalog(True)

    def zero_budget() -> None:
        registry.catalog(0)

    _refuse(bad_budget, "NOT_INT")
    _refuse(zero_budget, "OUT_OF_RANGE")


def test_cap_type_and_range() -> None:
    def flag() -> None:
        Registry(("clock",), _SIGNER, True)

    def text() -> None:
        Registry(("clock",), _SIGNER, "32")

    def fraction() -> None:
        Registry(("clock",), _SIGNER, 2.0)

    def zero() -> None:
        Registry(("clock",), _SIGNER, 0)

    def negative() -> None:
        Registry(("clock",), _SIGNER, -3)

    def huge() -> None:
        Registry(("clock",), _SIGNER, 1_000_001)

    _refuse(flag, "NOT_INT")
    _refuse(text, "NOT_INT")
    _refuse(fraction, "NOT_INT")
    _refuse(zero, "OUT_OF_RANGE")
    _refuse(negative, "OUT_OF_RANGE")
    _refuse(huge, "OUT_OF_RANGE")


def test_allow_deny_and_signer_shapes() -> None:
    def empty() -> None:
        Registry((), _SIGNER)

    def allow_text() -> None:
        Registry("clock", _SIGNER)

    def allow_dup() -> None:
        Registry(("clock", "clock"), _SIGNER)

    def allow_over() -> None:
        Registry(tuple(f"n{index}" for index in range(33)), _SIGNER)

    def missing_signer() -> None:
        Registry(("clock",), "")

    def bad_signer() -> None:
        Registry(("clock",), "Clock")

    def signer_none() -> None:
        Registry(("clock",), None)

    _refuse(empty, "EMPTY_ALLOW")
    _refuse(allow_text, "NOT_LIST")
    _refuse(allow_dup, "DUPLICATE")
    _refuse(allow_over, "OVERSIZE")
    _refuse(missing_signer, "MISSING_CRED")
    _refuse(bad_signer, "BAD_CRED")
    _refuse(signer_none, "NOT_TEXT")


def test_secret_shape_is_refused() -> None:
    registry = Registry(("clock",), _SIGNER)
    samples = (
        "sk-livekeyvalue",
        "Bearer abcdefghijk",
        "api_key=supersecret",
        "password = hunter22",
    )
    for text in samples:
        assert secret_shape(text) is True

        def use_name(value: str = text) -> None:
            registry.register(value, "tool", (), (), _echo, seal(_SIGNER, "clock"), _BLURB)

        def use_kind(value: str = text) -> None:
            registry.register("clock", value, (), (), _echo, seal(_SIGNER, "clock"), _BLURB)

        def use_perm(value: str = text) -> None:
            registry.register("clock", "tool", (value,), (value,), _echo, seal(_SIGNER, "clock"), _BLURB)

        def use_grant(value: str = text) -> None:
            registry.register("clock", "tool", (), (value,), _echo, seal(_SIGNER, "clock"), _BLURB)

        def use_desc(value: str = text) -> None:
            registry.register("clock", "tool", (), (), _echo, seal(_SIGNER, "clock"), value)

        def use_sig(value: str = text) -> None:
            registry.register("clock", "tool", (), (), _echo, value, _BLURB)

        _refuse(use_name, "SECRET")
        _refuse(use_kind, "SECRET")
        _refuse(use_perm, "SECRET")
        _refuse(use_grant, "SECRET")
        _refuse(use_desc, "SECRET")
        _refuse(use_sig, "SECRET")

    def secret_signer() -> None:
        Registry(("clock",), "sk-livekeyvalue")

    _refuse(secret_signer, "SECRET")

    def leak(text: str) -> str:
        del text
        return "sk-livekeyvalue"

    _add(registry, "clock", handler=leak)

    def secret_arg() -> None:
        registry.call("clock", "sk-livekeyvalue")

    def secret_result() -> None:
        registry.call("clock", "evening")

    _refuse(secret_arg, "SECRET")
    _refuse(secret_result, "SECRET")
    assert "sk-" not in repr(registry)
    assert secret_shape(repr(registry)) is False
    assert secret_shape(repr(Plugin("clock", "call-0001", "tool"))) is False


def test_malformed_text_and_handlers() -> None:
    registry = Registry(("clock", "wide"), _SIGNER)

    def name_type() -> None:
        registry.register(1, "tool", (), (), _echo, seal(_SIGNER, "clock"), _BLURB)

    def kind_none() -> None:
        registry.register("clock", None, (), (), _echo, seal(_SIGNER, "clock"), _BLURB)

    def token_type() -> None:
        registry.register("clock", "tool", (1,), ("tools.override",), _echo, seal(_SIGNER, "clock"), _BLURB)

    def nul_name() -> None:
        registry.register("clo\x00ck", "tool", (), (), _echo, "0" * 64, _BLURB)

    def long_name() -> None:
        registry.register("a" * 65, "tool", (), (), _echo, "0" * 64, _BLURB)

    def long_desc() -> None:
        registry.register("clock", "tool", (), (), _echo, seal(_SIGNER, "clock"), "A" * 129)

    def bad_desc() -> None:
        registry.register("clock", "tool", (), (), _echo, seal(_SIGNER, "clock"), "bad/name")

    def empty_desc() -> None:
        registry.register("clock", "tool", (), (), _echo, seal(_SIGNER, "clock"), "")

    def long_list() -> None:
        registry.register("clock", "tool", (), ("tools.override",) * 33, _echo, seal(_SIGNER, "clock"), _BLURB)

    def not_list() -> None:
        registry.register("clock", "tool", "tools.override", (), _echo, seal(_SIGNER, "clock"), _BLURB)

    def bad_kind() -> None:
        registry.register("clock", "platform", (), (), _echo, seal(_SIGNER, "clock"), _BLURB)

    def bad_name() -> None:
        registry.register("Clock", "tool", (), (), _echo, seal(_SIGNER, "clock"), _BLURB)

    def not_callable() -> None:
        registry.register("clock", "tool", (), (), None, seal(_SIGNER, "clock"), _BLURB)

    def class_handler() -> None:
        registry.register("clock", "tool", (), (), str, seal(_SIGNER, "clock"), _BLURB)

    _refuse(name_type, "NOT_TEXT")
    _refuse(kind_none, "NOT_TEXT")
    _refuse(token_type, "NOT_TEXT")
    _refuse(nul_name, "NULL_BYTE")
    _refuse(long_name, "OVERSIZE")
    _refuse(long_desc, "OVERSIZE")
    _refuse(bad_desc, "BAD_TEXT")
    _refuse(empty_desc, "BAD_TEXT")
    _refuse(long_list, "OVERSIZE")
    _refuse(not_list, "NOT_LIST")
    _refuse(bad_kind, "BAD_KIND")
    _refuse(bad_name, "BAD_NAME")
    _refuse(not_callable, "NOT_CALLABLE")
    _refuse(class_handler, "NOT_CALLABLE")
    assert registry.entries() == ()
    wide = _add(registry, "wide", description="A" * 128)
    assert wide.name == "wide"

    def bad_plugin() -> None:
        Plugin("clock", "fn.hello", "tool")

    def bad_plugin_kind() -> None:
        Plugin("clock", "call-0001", "platform")

    def bad_link_seq() -> None:
        Link(0, "clock", "call-0001", "tool", (), "Ace.", GENESIS, GENESIS)

    _refuse(bad_plugin, "BAD_ID")
    _refuse(bad_plugin_kind, "BAD_KIND")
    _refuse(bad_link_seq, "OUT_OF_RANGE")


def test_call_bounds_and_handler_failures() -> None:
    hits: list[str] = []

    def broken(text: str) -> str:
        hits.append(text)
        data: dict[str, str] = {}
        return data["missing"]

    def refuse_perm(text: str) -> str:
        hits.append("refuse")
        raise Refuse("PERMISSION", "tools.override")

    def bad_value(text: str) -> int:
        del text
        return 5

    registry = Registry(("clock", "boom", "odd"), _SIGNER)
    _add(registry, "clock", handler=broken)
    _add(registry, "boom", handler=refuse_perm)
    registry.register("odd", "tool", (), (), bad_value, seal(_SIGNER, "odd"), _BLURB)

    def fail() -> None:
        registry.call("clock", "evening")

    def propagated() -> None:
        registry.call("boom", "evening")

    def bad_result() -> None:
        registry.call("odd", "evening")

    def nul_arg() -> None:
        registry.call("clock", "eve\x00ning")

    def byte_arg() -> None:
        registry.call("clock", b"evening")

    def long_arg() -> None:
        registry.call("clock", "a" * (TEXT_CAP + 1))

    _refuse(fail, "PLUGIN_FAIL")
    _refuse(propagated, "PERMISSION", "tools.override")
    _refuse(bad_result, "BAD_RESULT")
    _refuse(nul_arg, "NULL_BYTE")
    _refuse(byte_arg, "NOT_TEXT")
    _refuse(long_arg, "OVERSIZE")
    assert hits == ["evening", "refuse"]
    assert "missing" not in repr(registry)

    def long_result(text: str) -> str:
        del text
        return "a" * (TEXT_CAP + 1)

    sized = Registry(("clock",), _SIGNER)
    _add(sized, "clock", handler=long_result)

    def over_result() -> None:
        sized.call("clock", "evening")

    _refuse(over_result, "OVERSIZE")
    edge = Registry(("clock",), _SIGNER)
    _add(edge, "clock")
    assert edge.call("clock", "a" * TEXT_CAP).text == "a" * TEXT_CAP


def test_load_from_path_always_import() -> None:
    registry = Registry(("clock",), _SIGNER)
    _add(registry, "clock")
    before = registry.entries()

    class _PathTrap:
        def __fspath__(self) -> str:
            raise AssertionError("path was touched")

        def __str__(self) -> str:
            raise AssertionError("path was touched")

    samples: tuple[object, ...] = (
        None,
        "",
        "plugins/demo",
        "C:\\plugins\\demo",
        0,
        b"nope",
        "sk-abcdefghijklmnop",
        "..\\evil",
        _PathTrap(),
    )
    for path in samples:

        def load_one(value: object = path) -> None:
            load_from_path(value)

        def load_method(value: object = path) -> None:
            registry.load_from_path(value)

        _refuse(load_one, "IMPORT")
        _refuse(load_method, "IMPORT")
    assert registry.entries() == before
    source = Path(__file__).with_name("plugins.py").read_text(encoding="utf-8")
    assert "importlib" not in source


def test_rebuild_roundtrip_broken_and_stale() -> None:
    def clock(text: str) -> str:
        return f"stamp {text}"

    allow = ("clock", "note")
    registry = Registry(allow, _SIGNER, 4)
    _add(registry, "clock", handler=clock, description="Shows the session clock beside the aisle light.")
    _add(registry, "note", description="Holds the lumen card note.")
    handlers: dict[str, Callable[[str], str]] = {"clock": clock, "note": _echo}
    signatures = {"clock": seal(_SIGNER, "clock"), "note": seal(_SIGNER, "note")}
    again = Registry.rebuild(
        registry.links(),
        handlers,
        signatures,
        allow,
        _SIGNER,
        registry.fence,
        4,
    )
    assert again.entries() == registry.entries()
    assert again.links() == registry.links()
    assert again.fence == registry.fence
    assert again.catalog() == registry.catalog()
    assert again.call("clock", "evening") == registry.call("clock", "evening")
    assert again.cap == 4
    assert again.requested == 4
    empty = Registry(("clock",), _SIGNER)
    rebuilt_empty = Registry.rebuild((), {}, {}, ("clock",), _SIGNER, empty.fence)
    assert rebuilt_empty.entries() == ()
    assert rebuilt_empty.fence == GENESIS

    def too_small() -> None:
        Registry.rebuild(
            registry.links(),
            handlers,
            signatures,
            allow,
            _SIGNER,
            registry.fence,
            1,
        )

    _refuse(too_small, "FULL")
    link = registry.links()[0]
    forged = (
        link,
        Link(
            2,
            "clock",
            "call-0002",
            "tool",
            (),
            _BLURB,
            link.digest,
            GENESIS,
        ),
    )

    def duplicate() -> None:
        Registry.rebuild(forged, {"clock": clock}, {"clock": seal(_SIGNER, "clock")}, ("clock",), _SIGNER, GENESIS)

    _refuse(duplicate, "DUPLICATE")

    def broken_seq() -> None:
        Registry.rebuild(
            (replace(link, seq=2),),
            {"clock": clock},
            {"clock": seal(_SIGNER, "clock")},
            allow,
            _SIGNER,
            GENESIS,
        )

    def broken_id() -> None:
        Registry.rebuild(
            (replace(link, callable_id="call-0009"),),
            {"clock": clock},
            {"clock": seal(_SIGNER, "clock")},
            allow,
            _SIGNER,
            GENESIS,
        )

    def broken_prior() -> None:
        Registry.rebuild(
            (replace(link, prior="ab" * 32),),
            {"clock": clock},
            {"clock": seal(_SIGNER, "clock")},
            allow,
            _SIGNER,
            GENESIS,
        )

    def broken_digest() -> None:
        Registry.rebuild(
            (replace(link, digest="ab" * 32),),
            {"clock": clock},
            {"clock": seal(_SIGNER, "clock")},
            allow,
            _SIGNER,
            GENESIS,
        )

    def not_a_link() -> None:
        Registry.rebuild((object(),), handlers, signatures, allow, _SIGNER, GENESIS)

    def stale() -> None:
        Registry.rebuild(registry.links(), handlers, signatures, allow, _SIGNER, "ab" * 32)

    def bad_fence() -> None:
        Registry.rebuild(registry.links(), handlers, signatures, allow, _SIGNER, "zz" * 32)

    def missing_handler() -> None:
        Registry.rebuild(registry.links(), {"clock": clock}, signatures, allow, _SIGNER, registry.fence)

    def bad_handler() -> None:
        Registry.rebuild(
            (link,),
            {"clock": None},
            {"clock": seal(_SIGNER, "clock")},
            ("clock",),
            _SIGNER,
            link.digest,
        )

    def unsigned() -> None:
        Registry.rebuild(
            (link,),
            {"clock": clock},
            {"clock": "0" * 64},
            ("clock",),
            _SIGNER,
            link.digest,
        )

    def extra() -> None:
        Registry.rebuild(
            (link,),
            {"clock": clock, "note": _echo},
            {"clock": seal(_SIGNER, "clock")},
            allow,
            _SIGNER,
            link.digest,
        )

    def not_map() -> None:
        Registry.rebuild((link,), ["clock"], {"clock": seal(_SIGNER, "clock")}, ("clock",), _SIGNER, link.digest)

    def oversize_links() -> None:
        Registry.rebuild(("x",) * 33, {}, {}, ("clock",), _SIGNER, GENESIS)

    def denied() -> None:
        Registry.rebuild(
            registry.links(),
            handlers,
            signatures,
            allow,
            _SIGNER,
            registry.fence,
            deny=("clock",),
        )

    _refuse(broken_seq, "BROKEN_CHAIN", "seq")
    _refuse(broken_id, "BROKEN_CHAIN", "id")
    _refuse(broken_prior, "BROKEN_CHAIN", "prior")
    _refuse(broken_digest, "BROKEN_CHAIN", "digest")
    _refuse(not_a_link, "BROKEN_CHAIN")
    _refuse(stale, "STALE")
    _refuse(bad_fence, "BAD_FENCE")
    _refuse(missing_handler, "NOT_CALLABLE")
    _refuse(bad_handler, "NOT_CALLABLE")
    _refuse(unsigned, "UNSIGNED")
    _refuse(extra, "UNKNOWN", "note")
    _refuse(not_map, "NOT_MAP")
    _refuse(oversize_links, "OVERSIZE")
    _refuse(denied, "DENIED", "clock")

    def bad_catalog() -> None:
        Catalog((), (), 1, 50)

    _refuse(bad_catalog, "OUT_OF_RANGE")
