"""Portal plan hash, credential ids, policy cap, and refused disk or port."""

from __future__ import annotations

import ast
import hashlib
from pathlib import Path

import pytest

from cosmos_hermes import Refuse, secret_shape
from setup_portal import (
    CRED_CAP,
    CRED_LEN,
    LOOPBACK,
    MAX_CONFIRMING_RETRIES,
    NAME_CAP,
    RETRY_CLASS,
    SCHEMA,
    TOOL_CAP,
    TOOLS,
    Confirm,
    Plan,
    confirm,
    open_port,
    persist,
    plan,
    rebuild,
    same,
    save,
    snapshot,
)


def _chain(levels: int) -> dict[str, object]:
    node: dict[str, object] = {"leaf": "ok"}
    for _ in range(levels):
        node = {"child": node}
    return node


def _cred(made: Plan, index: int) -> str:
    return made.cred_ids[index]


def _story_plan(story: tuple[Plan, Plan, str, str, str]) -> Plan:
    return story[0]


def _story_seal(story: tuple[Plan, Plan, str, str, str]) -> Plan:
    return story[1]


def _story_secret(story: tuple[Plan, Plan, str, str, str]) -> str:
    return story[2]


def _story_disk(story: tuple[Plan, Plan, str, str, str]) -> str:
    return story[3]


def _story_port(story: tuple[Plan, Plan, str, str, str]) -> str:
    return story[4]


def test_schema_success_and_canonical_hash() -> None:
    assert SCHEMA == "cosmos-hermes-setup_portal/1"
    assert TOOLS == ("browser", "image", "tts", "web")
    assert NAME_CAP == 32
    assert TOOL_CAP == 4
    assert CRED_CAP == 8
    assert CRED_LEN == 64
    assert LOOPBACK == "127.0.0.1"
    assert RETRY_CLASS == "CALLBACK_UNREACHABLE"
    assert MAX_CONFIRMING_RETRIES == 1
    made = plan("nous", ["tts", "browser", "web"], ["cred-voice", "cred-model"])
    assert isinstance(made, Plan)
    assert made.provider == "nous"
    assert made.tools == ("browser", "tts", "web")
    assert made.cred_ids == ("cred-model", "cred-voice")
    assert made.schema == SCHEMA
    assert made.name_cap == NAME_CAP
    assert made.tool_cap == TOOL_CAP
    assert made.cred_cap == CRED_CAP
    assert made.requested_name_cap == NAME_CAP
    assert made.clamped is False
    assert made.listens is False
    payload = (
        '{"cred_ids":["cred-model","cred-voice"],"provider":"nous",'
        '"schema":"cosmos-hermes-setup_portal/1","tools":["browser","tts","web"]}'
    )
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    assert made.plan_hash == digest
    again = plan("nous", ("web", "browser", "tts"), ("cred-model", "cred-voice"))
    assert again == made
    assert same(again, made) is True
    assert plan("other-1", ["web"], ["cred-model"]).plan_hash != digest
    assert set(setup_portal_all()) >= {
        "CRED_CAP",
        "CRED_LEN",
        "Confirm",
        "LOOPBACK",
        "MAX_CONFIRMING_RETRIES",
        "NAME_CAP",
        "Plan",
        "RETRY_CLASS",
        "SCHEMA",
        "TOOL_CAP",
        "TOOLS",
        "confirm",
        "open_port",
        "persist",
        "plan",
        "rebuild",
        "same",
        "save",
        "snapshot",
    }


def setup_portal_all() -> set[str]:
    import setup_portal

    return set(setup_portal.__all__)


def test_each_tool_and_full_subset() -> None:
    for name in TOOLS:
        one = plan("nous", [name], ["cred-model"])
        assert one.tools == (name,)
        assert one.cred_ids == ("cred-model",)
    full = plan("self-hosted", list(reversed(TOOLS)), ["cred-voice", "cred-model"])
    assert full.tools == TOOLS
    assert full.provider == "self-hosted"
    assert full.cred_ids == ("cred-model", "cred-voice")


def test_hash_ignores_cap_request() -> None:
    base = plan("nous", ["web"], ["cred-model"])
    high = plan("nous", ["web"], ["cred-model"], name_cap=100, tool_cap=9, cred_cap=50)
    assert high.plan_hash == base.plan_hash
    assert same(high, base) is True
    assert high != base
    assert high.clamped is True
    assert high.name_cap == NAME_CAP
    assert high.tool_cap == TOOL_CAP
    assert high.cred_cap == CRED_CAP
    assert high.requested_name_cap == 100
    assert high.requested_tool_cap == 9
    assert high.requested_cred_cap == 50
    tight = plan("nous", ["web"], ["cred-model"], name_cap=4, tool_cap=1, cred_cap=1)
    assert tight.clamped is False
    assert tight.name_cap == 4
    assert tight.tool_cap == 1
    assert tight.cred_cap == 1
    assert tight.plan_hash == base.plan_hash
    with pytest.raises(Refuse) as over_name:
        plan("portal", ["web"], ["cred-model"], name_cap=4)
    assert over_name.value.code == "OVERSIZE"
    assert over_name.value.detail == "4"
    with pytest.raises(Refuse) as over_policy:
        plan("a" * (NAME_CAP + 1), ["web"], ["cred-model"], name_cap=10_000)
    assert over_policy.value.code == "OVERSIZE"
    assert over_policy.value.detail == str(NAME_CAP)
    with pytest.raises(Refuse) as over_cred:
        plan("nous", ["web"], ["c" * (CRED_LEN + 1)])
    assert over_cred.value.code == "OVERSIZE"
    assert over_cred.value.detail == str(CRED_LEN)


def test_tool_provider_and_cred_refusals() -> None:
    cases: tuple[tuple[object, object, object, str], ...] = (
        ("nous", [], ["cred-model"], "EMPTY_ALLOW"),
        ("nous", (), ["cred-model"], "EMPTY_ALLOW"),
        ("nous", ["web"], [], "MISSING_ID"),
        ("nous", ["web"], (), "MISSING_ID"),
        ("nous", ["web", "image", "tts", "browser", "web"], ["cred-model"], "TOO_MANY"),
        ("nous", ["web", "image"], ["cred-model"], "TOO_MANY"),
        ("nous", ["web"], ["cred-model", "cred-voice"], "TOO_MANY"),
        ("nous", ["web", "shell"], ["cred-model"], "BAD_TOOL"),
        ("nous", "web", ["cred-model"], "BAD_TOOL"),
        ("nous", None, ["cred-model"], "BAD_TOOL"),
        ("nous", {"web"}, ["cred-model"], "BAD_TOOL"),
        ("nous", ["web", "web"], ["cred-model"], "DUPLICATE"),
        ("nous", ["web"], ["cred-model", "cred-model"], "DUPLICATE"),
        ("Nous", ["web"], ["cred-model"], "BAD_PROVIDER"),
        ("", ["web"], ["cred-model"], "BAD_PROVIDER"),
        ("no_us", ["web"], ["cred-model"], "BAD_PROVIDER"),
        ("a.b", ["web"], ["cred-model"], "BAD_PROVIDER"),
        ("a-", ["web"], ["cred-model"], "BAD_PROVIDER"),
        ("nous", ["web"], ["cred_model"], "BAD_CRED"),
        ("nous", ["web"], ["-cred"], "BAD_CRED"),
        ("nous", ["web"], [""], "BAD_CRED"),
    )
    for provider, tools, cred_ids, code in cases:
        with pytest.raises(Refuse) as caught:
            if code == "TOO_MANY" and tools == ["web", "image"]:
                plan(provider, tools, cred_ids, tool_cap=1)
            elif code == "TOO_MANY" and cred_ids == ["cred-model", "cred-voice"]:
                plan(provider, tools, cred_ids, cred_cap=1)
            else:
                plan(provider, tools, cred_ids)
        assert caught.value.code == code
    with pytest.raises(Refuse) as kind:
        plan(None, ["web"], ["cred-model"])
    assert kind.value.code == "NOT_TEXT"
    with pytest.raises(Refuse) as nul:
        plan("ab\x00", ["web"], ["cred-model"])
    assert nul.value.code == "NULL_BYTE"
    with pytest.raises(Refuse) as tool_type:
        plan("nous", ["web", 1], ["cred-model"])
    assert tool_type.value.code == "NOT_TEXT"
    with pytest.raises(Refuse) as cred_type:
        plan("nous", ["web"], ["cred-model", 2])
    assert cred_type.value.code == "NOT_TEXT"
    with pytest.raises(Refuse) as tool_nul:
        plan("nous", ["a\x00"], ["cred-model"])
    assert tool_nul.value.code == "NULL_BYTE"
    with pytest.raises(Refuse) as tool_over:
        plan("nous", ["t" * (NAME_CAP + 1)], ["cred-model"])
    assert tool_over.value.code == "OVERSIZE"
    with pytest.raises(Refuse) as flag:
        plan("nous", ["web"], ["cred-model"], name_cap=True)
    assert flag.value.code == "NOT_INT"
    with pytest.raises(Refuse) as text_cap:
        plan("nous", ["web"], ["cred-model"], tool_cap="4")
    assert text_cap.value.code == "NOT_INT"
    with pytest.raises(Refuse) as cred_flag:
        plan("nous", ["web"], ["cred-model"], cred_cap=False)
    assert cred_flag.value.code == "NOT_INT"
    with pytest.raises(Refuse) as zero:
        plan("nous", ["web"], ["cred-model"], name_cap=0)
    assert zero.value.code == "BAD_LIMIT"
    with pytest.raises(Refuse) as negative:
        plan("nous", ["web"], ["cred-model"], tool_cap=-3)
    assert negative.value.code == "BAD_LIMIT"
    with pytest.raises(Refuse) as huge:
        plan("nous", ["web"], ["cred-model"], cred_cap=1_000_000_001)
    assert huge.value.code == "BAD_LIMIT"


def test_secret_fields_do_not_echo() -> None:
    raw = "sk-abcdefghij"
    with pytest.raises(Refuse) as provider:
        plan(raw, ["web"], ["cred-model"])
    assert provider.value.code == "SECRET"
    assert raw not in str(provider.value)
    assert raw not in repr(provider.value)
    with pytest.raises(Refuse) as tool:
        plan("nous", [raw], ["cred-model"])
    assert tool.value.code == "SECRET"
    assert raw not in str(tool.value)
    with pytest.raises(Refuse) as cred:
        plan("nous", ["web"], [raw])
    assert cred.value.code == "SECRET"
    assert raw not in str(cred.value)
    assert raw not in repr(cred.value)
    made = plan("nous", ["image", "web"], ["cred-model", "cred-voice"])
    assert secret_shape(repr(made)) is False
    with pytest.raises(AttributeError):
        setattr(made, "provider", "other")


def test_rebuild_same_and_chain() -> None:
    made = plan(
        "nous",
        ["web", "tts"],
        ["cred-voice", "cred-model"],
        name_cap=100,
        tool_cap=2,
    )
    record = snapshot(made)
    sealed = rebuild(record)
    assert sealed == made
    assert sealed is not made
    assert same(sealed, made) is True
    record["tools"] = ["tts", "web"]
    assert rebuild(record) == made
    broken = snapshot(made)
    broken["plan_hash"] = "0" * 64
    with pytest.raises(Refuse) as chain:
        rebuild(broken)
    assert chain.value.code == "CHAIN"
    extra = snapshot(made)
    extra["note"] = "porch"
    with pytest.raises(Refuse) as shape:
        rebuild(extra)
    assert shape.value.code == "BAD_RECORD"
    missing = snapshot(made)
    del missing["schema"]
    with pytest.raises(Refuse) as gone:
        rebuild(missing)
    assert gone.value.code == "BAD_RECORD"
    listened = snapshot(made)
    listened["listens"] = True
    with pytest.raises(Refuse) as port:
        rebuild(listened)
    assert port.value.code == "NO_SOCKET"
    flagged = snapshot(made)
    flagged["clamped"] = 1
    with pytest.raises(Refuse) as flag:
        rebuild(flagged)
    assert flag.value.code == "NOT_BOOL"
    with pytest.raises(Refuse) as kind:
        rebuild(["nous"])
    assert kind.value.code == "BAD_RECORD"
    with pytest.raises(Refuse) as bad_plan:
        snapshot("nous")
    assert bad_plan.value.code == "BAD_PLAN"
    with pytest.raises(Refuse) as bad_same:
        same(made, "nous")
    assert bad_same.value.code == "BAD_PLAN"
    lied = snapshot(made)
    lied["name_cap"] = NAME_CAP - 1
    with pytest.raises(Refuse) as applied:
        rebuild(lied)
    assert applied.value.code == "BAD_RECORD"
    other = snapshot(made)
    other["schema"] = "cosmos-hermes-setup_portal/2"
    with pytest.raises(Refuse) as schema:
        rebuild(other)
    assert schema.value.code == "BAD_RECORD"


def test_forged_plan_refuses() -> None:
    with pytest.raises(Refuse) as chain:
        Plan(
            provider="nous",
            tools=("web",),
            cred_ids=("cred-model",),
            plan_hash="0" * 64,
            name_cap=NAME_CAP,
            tool_cap=TOOL_CAP,
            cred_cap=CRED_CAP,
            requested_name_cap=NAME_CAP,
            requested_tool_cap=TOOL_CAP,
            requested_cred_cap=CRED_CAP,
            clamped=False,
            listens=False,
            schema=SCHEMA,
        )
    assert chain.value.code == "CHAIN"
    with pytest.raises(Refuse) as port:
        Plan(
            provider="nous",
            tools=("web",),
            cred_ids=("cred-model",),
            plan_hash="",
            name_cap=NAME_CAP,
            tool_cap=TOOL_CAP,
            cred_cap=CRED_CAP,
            requested_name_cap=NAME_CAP,
            requested_tool_cap=TOOL_CAP,
            requested_cred_cap=CRED_CAP,
            clamped=False,
            listens=True,
            schema=SCHEMA,
        )
    assert port.value.code == "NO_SOCKET"
    with pytest.raises(Refuse) as skew:
        Plan(
            provider="nous",
            tools=("web",),
            cred_ids=("cred-model",),
            plan_hash="",
            name_cap=NAME_CAP,
            tool_cap=TOOL_CAP,
            cred_cap=CRED_CAP,
            requested_name_cap=NAME_CAP,
            requested_tool_cap=TOOL_CAP,
            requested_cred_cap=CRED_CAP,
            clamped=True,
            listens=False,
            schema=SCHEMA,
        )
    assert skew.value.code == "BAD_RECORD"


def test_confirm_is_one_named_class() -> None:
    made = plan("nous", ["web", "tts"], ["cred-model", "cred-voice"])
    first = confirm(made, RETRY_CLASS, 0)
    assert isinstance(first, Confirm)
    assert first.failure == RETRY_CLASS
    assert first.retries == 1
    assert first.plan_hash == made.plan_hash
    assert secret_shape(repr(first)) is False
    again = confirm(made, "CALLBACK_UNREACHABLE", 0)
    assert again == first
    with pytest.raises(Refuse) as second:
        confirm(made, RETRY_CLASS, first.retries)
    assert second.value.code == "RETRY"
    with pytest.raises(Refuse) as other:
        confirm(made, "HTTP_500", 0)
    assert other.value.code == "UNCLASSIFIED"
    with pytest.raises(Refuse) as flag:
        confirm(made, RETRY_CLASS, True)
    assert flag.value.code == "NOT_INT"
    with pytest.raises(Refuse) as negative:
        confirm(made, RETRY_CLASS, -1)
    assert negative.value.code == "BAD_LIMIT"
    with pytest.raises(Refuse) as kind:
        confirm("nous", RETRY_CLASS, 0)
    assert kind.value.code == "BAD_PLAN"
    raw = "sk-abcdefghij"
    with pytest.raises(Refuse) as secret:
        confirm(made, raw, 0)
    assert secret.value.code == "SECRET"
    assert raw not in str(secret.value)


def test_open_port_and_save_refuse() -> None:
    with pytest.raises(Refuse) as bound:
        open_port(LOOPBACK, 8642)
    assert bound.value.code == "NO_SOCKET"
    with pytest.raises(Refuse) as host:
        open_port("10.0.0.8", 80)
    assert host.value.code == "BAD_HOST"
    with pytest.raises(Refuse) as flag:
        open_port(LOOPBACK, True)
    assert flag.value.code == "NOT_INT"
    with pytest.raises(Refuse) as low:
        open_port(LOOPBACK, -1)
    assert low.value.code == "BAD_LIMIT"
    raw = "sk-abcdefghij"
    with pytest.raises(Refuse) as secret:
        open_port(raw, 1)
    assert secret.value.code == "SECRET"
    assert raw not in str(secret.value)
    with pytest.raises(Refuse) as disk:
        save({"provider": "nous", "cred_ids": ["cred-model"]})
    assert disk.value.code == "NO_DISK"
    with pytest.raises(Refuse) as leaked:
        save({"note": raw})
    assert leaked.value.code == "SECRET"
    assert raw not in str(leaked.value)


def test_persist_returns_mapping_and_refuses_secrets() -> None:
    made = plan("nous", ["image", "web"], ["cred-model", "cred-voice"])
    mapping: dict[str, object] = {
        "provider": made.provider,
        "tools": list(made.tools),
        "cred_ids": list(made.cred_ids),
        "plan_hash": made.plan_hash,
        "note": "plain",
        "count": 1,
        "flag": True,
        "empty": None,
        "nested": {"ok": ["still", 0, False]},
    }
    assert persist(mapping) is mapping
    assert persist({}) == {}
    assert persist(_chain(7))["child"] is not None
    assert persist({"n": 1_000_000})["n"] == 1_000_000
    raw = "sk-abcdefghij"
    with pytest.raises(Refuse) as top:
        persist({"note": raw})
    assert top.value.code == "SECRET"
    assert raw not in str(top.value)
    assert raw not in repr(top.value)
    with pytest.raises(Refuse) as nested:
        persist({"outer": [{"token": "Bearer abcdefghijk"}]})
    assert nested.value.code == "SECRET"
    with pytest.raises(Refuse) as assigned:
        persist({"note": "api_key=abcdef"})
    assert assigned.value.code == "SECRET"
    with pytest.raises(Refuse) as key:
        persist({"password=hunter2": "no"})
    assert key.value.code == "SECRET"
    assert persist({"label": "secret"})["label"] == "secret"


def test_persist_shape_refusals() -> None:
    with pytest.raises(Refuse) as kind:
        persist(["web"])
    assert kind.value.code == "BAD_MAPPING"
    with pytest.raises(Refuse) as text:
        persist("nous")
    assert text.value.code == "BAD_MAPPING"
    with pytest.raises(Refuse) as bad_key:
        persist({1: "a"})
    assert bad_key.value.code == "BAD_KEY"
    with pytest.raises(Refuse) as empty_key:
        persist({"": "a"})
    assert empty_key.value.code == "BAD_KEY"
    with pytest.raises(Refuse) as fractional:
        persist({"n": 1.5})
    assert fractional.value.code == "BAD_VALUE"
    with pytest.raises(Refuse) as blob:
        persist({"n": b"abcd"})
    assert blob.value.code == "BAD_VALUE"
    with pytest.raises(Refuse) as bag:
        persist({"n": {"web"}})
    assert bag.value.code == "BAD_VALUE"
    with pytest.raises(Refuse) as deep:
        persist(_chain(8))
    assert deep.value.code == "TOO_DEEP"
    cycle: dict[str, object] = {}
    cycle["self"] = cycle
    with pytest.raises(Refuse) as loop:
        persist(cycle)
    assert loop.value.code == "TOO_DEEP"
    with pytest.raises(Refuse) as wide:
        persist({str(i): i for i in range(33)})
    assert wide.value.code == "TOO_MANY"
    with pytest.raises(Refuse) as wide_list:
        persist({"row": list(range(33))})
    assert wide_list.value.code == "TOO_MANY"
    with pytest.raises(Refuse) as nul:
        persist({"k": "a\x00b"})
    assert nul.value.code == "NULL_BYTE"
    with pytest.raises(Refuse) as over:
        persist({"k": "a" * 256_001})
    assert over.value.code == "OVERSIZE"
    with pytest.raises(Refuse) as low:
        persist({"n": -1})
    assert low.value.code == "OUT_OF_RANGE"
    with pytest.raises(Refuse) as high:
        persist({"n": 1_000_001})
    assert high.value.code == "OUT_OF_RANGE"


def test_persist_does_not_open_or_import_io(monkeypatch: pytest.MonkeyPatch) -> None:
    def _blocked(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("open")

    monkeypatch.setattr("builtins.open", _blocked)
    mapping = {"provider": "nous", "tools": ["web", "tts"], "cred_ids": ["cred-model"]}
    assert persist(mapping) is mapping
    with pytest.raises(Refuse) as disk:
        save(mapping)
    assert disk.value.code == "NO_DISK"
    source = Path(__file__).with_name("setup_portal.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    modules: set[str] = set()
    names: set[str] = set()
    attrs: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.add(alias.name.split(".", 1)[0])
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            modules.add(node.module.split(".", 1)[0])
        elif isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name):
                names.add(func.id)
            elif isinstance(func, ast.Attribute):
                attrs.add(func.attr)
    assert modules.isdisjoint(
        {
            "subprocess",
            "socket",
            "urllib",
            "requests",
            "pickle",
            "http",
            "asyncio",
            "threading",
            "multiprocessing",
            "webbrowser",
            "ctypes",
            "time",
        }
    )
    assert names.isdisjoint({"open", "eval", "exec", "compile", "__import__"})
    assert attrs.isdisjoint({"urlopen", "write_text", "write_bytes", "mkdir", "system", "popen"})


def test_example_setup_portal() -> None:
    """Mira's evening session names model and voice creds. The porch-light card stays a hash."""

    def once() -> tuple[Plan, Plan, str, str, str]:
        made = plan(
            "nous",
            ["browser", "tts", "web"],
            ["cred-voice", "cred-model"],
        )
        again = plan(
            "nous",
            ("web", "tts", "browser"),
            ("cred-model", "cred-voice"),
        )
        assert made == again
        assert same(made, again) is True
        assert made.plan_hash == again.plan_hash
        note = persist(
            {
                "session": "mira-evening",
                "card": "porch-light",
                "note": "Tape the porch light card above the bench.",
                "provider": made.provider,
                "plan_hash": made.plan_hash,
                "cred_ids": list(made.cred_ids),
            }
        )
        assert note["card"] == "porch-light"
        secret_code = "UNCAUGHT"
        try:
            plan("nous", ["web"], ["cred-model", "sk-porchlight"])
        except Refuse as refused:
            secret_code = refused.code
            assert "sk-" not in str(refused)
            assert "porchlight" not in str(refused)
        disk_code = "UNCAUGHT"
        try:
            save(note)
        except Refuse as refused:
            disk_code = refused.code
        port_code = "UNCAUGHT"
        try:
            open_port(LOOPBACK, 0)
        except Refuse as refused:
            port_code = refused.code
        sealed = rebuild(snapshot(made))
        assert sealed == made
        assert sealed.listens is False
        return made, sealed, secret_code, disk_code, port_code

    first = once()
    second = once()
    assert first == second
    made = _story_plan(first)
    sealed = _story_seal(first)
    assert made == sealed
    assert _cred(made, 0) == "cred-model"
    assert _cred(made, 1) == "cred-voice"
    assert made.listens is False
    assert _story_secret(first) == "SECRET"
    assert _story_disk(first) == "NO_DISK"
    assert _story_port(first) == "NO_SOCKET"
    assert secret_shape(repr(made)) is False
