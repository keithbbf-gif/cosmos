"""Gateway enablement and call descriptors. No network and no subprocess."""

from __future__ import annotations

import ast
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import pytest

from cosmos_hermes import Refuse, secret_shape
from tool_gateway import (
    BATCH_BUDGET,
    CALL_CAP,
    CRED_CAP,
    DEFAULT_MODEL,
    GENESIS,
    NAME_CAP,
    RETRY_CLASS,
    SCHEMA,
    TOOLS,
    Call,
    CapNote,
    Offer,
    Route,
    Snapshot,
    ToolGateway,
    rebuild,
)


def _code(fn: Callable[[], object]) -> str:
    with pytest.raises(Refuse) as caught:
        fn()
    return caught.value.code


def _nth(calls: tuple[Call, ...], index: int) -> Call:
    if index < 0 or index >= len(calls):
        raise AssertionError("missing call")
    return calls[index]


def _paid() -> ToolGateway:
    gate = ToolGateway()
    gate.entitle("paid")
    return gate


def _arm(gate: ToolGateway, name: str, cred_id: str) -> Route:
    return gate.enable(name, cred_id)


@dataclass(frozen=True, slots=True)
class _Story:
    empty_code: str
    plan: tuple[str, ...]
    web_name: str
    vision_name: str
    web_op: str
    vision_tool: str
    vision_op: str
    web_code: str
    vision_code: str
    terminal_code: str
    fence: str
    rebuilt_fence: str
    loaded_plan: tuple[str, ...]
    loaded_fence: str
    repr_gate: str
    repr_web: str
    repr_vision: str


def _story() -> _Story:
    gate = ToolGateway()
    gate.entitle("paid")

    def empty() -> object:
        return gate.admit((), {})

    web = _arm(gate, "web", "cred-web-card")
    vision = _arm(gate, "vision", "cred-vision-session")
    web_call = gate.call("web", "search", "Ada light note", 1_711_000_000)
    vision_call = gate.call("vision", "vision", "north light on the session card", 1_711_000_030)

    def terminal() -> object:
        return gate.call("terminal", "run", "status", 1_711_000_040, None)

    snap = gate.snapshot()
    rebuilt = rebuild(snap)
    loaded = ToolGateway.load(snap)
    return _Story(
        empty_code=_code(empty),
        plan=gate.plan(),
        web_name=web.name,
        vision_name=vision.name,
        web_op=web_call.op,
        vision_tool=vision_call.tool,
        vision_op=vision_call.op,
        web_code=web_call.code,
        vision_code=vision_call.code,
        terminal_code=_code(terminal),
        fence=snap.fence,
        rebuilt_fence=rebuilt.fence,
        loaded_plan=loaded.plan(),
        loaded_fence=loaded.snapshot().fence,
        repr_gate=repr(gate),
        repr_web=repr(web),
        repr_vision=repr(vision),
    )


def _web_call(seq: int, prev: str, arg: str, at: int) -> Call:
    return Call(
        schema=SCHEMA,
        tool="web",
        op="search",
        arg=arg,
        model="",
        at=at,
        seq=seq,
        prev=prev,
        code="READY",
    )


def _snap(
    calls: tuple[Call, ...] = (),
    fence: str = GENESIS,
    retried: tuple[str, ...] = (),
    entitled: str = "",
    model: str = DEFAULT_MODEL,
    routes: tuple[tuple[str, str], ...] = (),
) -> Snapshot:
    return Snapshot(
        schema=SCHEMA,
        cap=CapNote(applied=CRED_CAP, requested=CRED_CAP, clamped=False),
        routes=routes,
        declined=(),
        pinned=(),
        env=(),
        model=model,
        entitled=entitled,
        calls=calls,
        retried=retried,
        fence=fence,
    )


def test_schema_and_catalog() -> None:
    assert SCHEMA == "cosmos-hermes-tool_gateway/1"
    assert TOOLS == ("web", "image", "tts", "browser")
    assert "vision" not in TOOLS
    assert "terminal" not in TOOLS
    assert DEFAULT_MODEL == "flux-2-klein"
    assert RETRY_CLASS == "RATE_LIMIT"


def test_example_tool_gateway() -> None:
    first = _story()
    second = _story()
    assert first == second
    assert first.empty_code == "EMPTY_ALLOW"
    assert first.plan == ("web", "browser")
    assert first.web_name == "web"
    assert first.vision_name == "browser"
    assert first.web_op == "search"
    assert first.vision_tool == "browser"
    assert first.vision_op == "vision"
    assert first.web_code == "READY"
    assert first.vision_code == "READY"
    assert first.terminal_code == "NO_CRED"
    assert first.rebuilt_fence == first.fence
    assert first.loaded_plan == first.plan
    assert first.loaded_fence == first.fence
    assert "cred-web-card" not in first.repr_gate
    assert "cred-web-card" not in first.repr_web
    assert "cred-vision-session" not in first.repr_vision
    assert secret_shape(first.repr_gate) is False
    assert secret_shape(first.repr_web) is False
    assert secret_shape(first.repr_vision) is False


def test_success_descriptors_and_catalog_order() -> None:
    gate = _paid()
    assert gate.plan() == ()
    assert gate.cap_note == CapNote(applied=CRED_CAP, requested=CRED_CAP, clamped=False)
    assert gate.snapshot().fence == GENESIS
    _arm(gate, "browser", "cred-browser")
    _arm(gate, "web", "cred-web")
    assert gate.plan() == ("web", "browser")
    again = _arm(gate, "web", "cred-web-2")
    assert again.cred_id == "cred-web-2"
    assert again.via == "gateway"
    assert again.provider == "nous"
    assert gate.plan() == ("web", "browser")
    _arm(gate, "image", "cred-image")
    _arm(gate, "tts", "cred-tts")
    assert gate.plan() == TOOLS
    drawn = gate.call("image", "generate", "a light card", 5)
    spoken = gate.call("tts", "speak", "north light", 6)
    opened = gate.call("browser", "navigate", "https://example.com/card", 7)
    clicked = gate.call("browser", "click", "@e3", 8)
    assert drawn.model == DEFAULT_MODEL
    assert drawn.code == "READY"
    assert spoken.model == ""
    assert opened.op == "navigate"
    assert clicked.arg == "@e3"
    snap = gate.snapshot()
    assert rebuild(snap) == snap
    loaded = ToolGateway.load(snap)
    assert loaded.snapshot() == snap
    assert loaded.plan() == TOOLS
    assert secret_shape(repr(snap)) is False
    assert "cred-web-2" not in repr(snap)
    assert "cred-web-2" not in repr(gate)


def test_empty_allow_enables_nothing() -> None:
    gate = _paid()
    _arm(gate, "tts", "cred-tts")

    def empty_tuple() -> object:
        return gate.admit((), {})

    def empty_list() -> object:
        return gate.admit([], {})

    def missing() -> object:
        return gate.admit(None, {})

    assert _code(empty_tuple) == "EMPTY_ALLOW"
    assert _code(empty_list) == "EMPTY_ALLOW"
    assert _code(missing) == "EMPTY_ALLOW"
    assert gate.plan() == ("tts",)

    def as_text() -> object:
        return gate.admit("web", {"web": "cred-web"})

    def as_map() -> object:
        return gate.admit(("web",), ["cred-web"])

    assert _code(as_text) == "NOT_LIST"
    assert _code(as_map) == "NOT_MAP"
    assert gate.plan() == ("tts",)


def test_each_tool_needs_its_own_cred_id() -> None:
    gate = ToolGateway()

    def missing() -> object:
        return gate.admit(
            ("web", "image", "tts", "browser"),
            {"web": "cred-web", "image": "cred-image", "tts": "cred-tts"},
        )

    assert _code(missing) == "NO_CRED"
    assert gate.plan() == ()
    gate.admit(
        ("browser", "web", "image", "tts"),
        {
            "web": "cred-portal",
            "image": "cred-portal",
            "tts": "cred-portal",
            "browser": "cred-portal",
        },
    )
    assert gate.plan() == TOOLS

    fresh = ToolGateway()

    def duplicate() -> object:
        return fresh.admit(("vision", "browser"), {"vision": "cred-v", "browser": "cred-b"})

    assert _code(duplicate) == "DUPLICATE"
    assert fresh.plan() == ()
    fresh.admit(("vision",), {"vision": "cred-vision-session"})
    assert fresh.plan() == ("browser",)


def test_terminal_without_id_and_with_id() -> None:
    gate = _paid()
    _arm(gate, "web", "cred-web")

    def missing() -> object:
        return gate.call("terminal", "run", "status", 4, None)

    def blank() -> object:
        return gate.call("modal", "run", "status", 4, "   ")

    def present() -> object:
        return gate.enable("terminal", "cred-terminal")

    def present_call() -> object:
        return gate.call("terminal", "run", "status", 4, "cred-terminal")

    assert _code(missing) == "NO_CRED"
    assert _code(blank) == "NO_CRED"
    assert _code(present) == "NOT_GATEWAY"
    assert _code(present_call) == "NOT_GATEWAY"
    assert gate.plan() == ("web",)
    assert gate.snapshot().calls == ()


def test_secrets_repr_and_bad_cred() -> None:
    gate = _paid()
    _arm(gate, "tts", "cred-tts")
    poison = "sk-" + "abcdefgh"

    def secret_browser() -> object:
        return gate.enable("browser", poison)

    def secret_assign() -> object:
        return gate.enable("tts", "api_key=supersecretvalue")

    def secret_bearer() -> object:
        return gate.enable("web", "Bearer abcdefghijklmnop")

    def secret_route() -> object:
        return Route(name="web", cred_id=poison, provider="nous", via="gateway")

    assert _code(secret_browser) == "SECRET"
    assert _code(secret_assign) == "SECRET"
    assert _code(secret_bearer) == "SECRET"
    assert _code(secret_route) == "SECRET"
    assert gate.plan() == ("tts",)
    assert poison not in repr(gate)
    assert secret_shape(repr(gate)) is False

    def spaced() -> object:
        return gate.enable("image", "has space")

    def slashed() -> object:
        return gate.enable("image", "bad/id")

    assert _code(spaced) == "BAD_CRED"
    assert _code(slashed) == "BAD_CRED"
    assert gate.plan() == ("tts",)


def test_blank_cred_clears_only_that_tool() -> None:
    gate = ToolGateway()
    _arm(gate, "image", "cred-image")
    _arm(gate, "web", "cred-web")

    def blank() -> object:
        return gate.enable("image", "   ")

    def none_cred() -> object:
        return gate.enable("image", None)

    assert _code(blank) == "NO_CRED"
    assert gate.plan() == ("web",)
    _arm(gate, "image", "cred-image")
    assert _code(none_cred) == "NO_CRED"
    assert gate.plan() == ("web",)


def test_cap_is_policy() -> None:
    gate = ToolGateway(cred_cap=CRED_CAP + 40)
    note = gate.cap_note
    assert note.applied == CRED_CAP
    assert note.requested == CRED_CAP + 40
    assert note.clamped is True
    _arm(gate, "web", "a" * CRED_CAP)

    def over() -> object:
        return gate.enable("image", "b" * (CRED_CAP + 1))

    assert _code(over) == "OVERSIZE"
    assert gate.plan() == ("web",)
    tight = ToolGateway(cred_cap=8)
    assert tight.cap_note == CapNote(applied=8, requested=8, clamped=False)
    _arm(tight, "browser", "abcd1234")

    def tight_over() -> object:
        return tight.enable("web", "abcdefghi")

    assert _code(tight_over) == "OVERSIZE"
    assert tight.plan() == ("browser",)

    def flag() -> object:
        return ToolGateway(cred_cap=True)

    def text_cap() -> object:
        return ToolGateway(cred_cap="64")

    def zero() -> object:
        return ToolGateway(cred_cap=0)

    def negative() -> object:
        return ToolGateway(cred_cap=-1)

    def lie_applied() -> object:
        return CapNote(applied=CRED_CAP + 1, requested=CRED_CAP + 1, clamped=True)

    def lie_clamp() -> object:
        return CapNote(applied=8, requested=CRED_CAP + 1, clamped=True)

    assert _code(flag) == "NOT_INT"
    assert _code(text_cap) == "NOT_INT"
    assert _code(zero) == "BAD_LIMIT"
    assert _code(negative) == "BAD_LIMIT"
    assert _code(lie_applied) == "BAD_CAP"
    assert _code(lie_clamp) == "BAD_CAP"


def test_malformed_names_and_args() -> None:
    gate = _paid()
    _arm(gate, "web", "cred-web")
    _arm(gate, "browser", "cred-browser")

    def unknown() -> object:
        return gate.enable("video", "cred-video")

    def upper() -> object:
        return gate.enable("WEB", "cred-web")

    def none_name() -> object:
        return gate.enable(None, "cred-web")

    def number() -> object:
        return gate.enable("image", 12)

    def nul_name() -> object:
        return gate.enable("web\x00", "cred-web")

    def nul_cred() -> object:
        return gate.enable("image", "cred\x00id")

    def long_name() -> object:
        return gate.enable("n" * (NAME_CAP + 1), "cred-web")

    def bad_op() -> object:
        return gate.call("web", "fly", "Ada note", 1)

    def vision_nav() -> object:
        return gate.call("vision", "navigate", "https://example.com/card", 1)

    def empty_arg() -> object:
        return gate.call("web", "search", "   ", 1)

    def file_url() -> object:
        return gate.call("browser", "navigate", "file:///tmp/card", 2)

    def dots() -> object:
        return gate.call("web", "extract", "https://example.com/../secret", 3)

    def bad_click() -> object:
        return gate.call("browser", "click", "e3", 4)

    def early() -> object:
        return gate.call("web", "search", "Ada note", -1)

    def flag_at() -> object:
        return gate.call("web", "search", "Ada note", True)

    assert _code(unknown) == "BAD_TOOL"
    assert _code(upper) == "BAD_TOOL"
    assert _code(none_name) == "NOT_TEXT"
    assert _code(number) == "NOT_TEXT"
    assert _code(nul_name) == "NULL_BYTE"
    assert _code(nul_cred) == "NULL_BYTE"
    assert _code(long_name) == "OVERSIZE"
    assert _code(bad_op) == "BAD_OP"
    assert _code(vision_nav) == "BAD_OP"
    assert _code(empty_arg) == "EMPTY"
    assert _code(file_url) == "BAD_URL"
    assert _code(dots) == "BAD_URL"
    assert _code(bad_click) == "BAD_ARG"
    assert _code(early) == "OUT_OF_RANGE"
    assert _code(flag_at) == "NOT_INT"
    assert gate.plan() == ("web", "browser")
    assert gate.snapshot().calls == ()


def test_entitlement_model_and_override() -> None:
    bare = ToolGateway()
    _arm(bare, "web", "cred-web")

    def unpaid() -> object:
        return bare.call("web", "search", "Ada note", 1)

    def off_kind() -> object:
        return bare.entitle("off")

    def yolo_kind() -> object:
        return bare.entitle("yolo")

    assert _code(unpaid) == "NO_ENTITLE"
    assert _code(off_kind) == "BAD_KIND"
    assert _code(yolo_kind) == "BAD_KIND"
    assert bare.snapshot().entitled == ""

    pooled = _paid()
    pooled.entitle("pool")
    _arm(pooled, "image", "cred-image")

    def krea() -> object:
        return pooled.pin_model("krea-2-medium")

    def unknown_model() -> object:
        return pooled.pin_model("nope")

    assert _code(krea) == "POOL"
    assert _code(unknown_model) == "BAD_MODEL"
    drawn = pooled.call("image", "generate", "pool card", 2)
    assert drawn.model == DEFAULT_MODEL

    paid = _paid()
    assert paid.pin_model("krea-2-large") == "krea-2-large"

    def downgrade() -> object:
        return paid.entitle("pool")

    assert _code(downgrade) == "POOL"
    assert paid.snapshot().entitled == "paid"
    _arm(paid, "image", "cred-image")
    kept = paid.call("image", "generate", "paid card", 3)
    assert kept.model == "krea-2-large"

    def override() -> object:
        return paid.call("image", "generate", "paid card", 4, model="flux-2-pro")

    assert _code(override) == "OVERRIDE"
    assert len(paid.snapshot().calls) == 1


def test_direct_pin_decline_legacy_and_offers() -> None:
    gate = ToolGateway()
    assert gate.note_env("web") == "web"
    direct = gate.select("image", "fal", "cred-fal")
    assert direct.via == "direct"
    assert direct.provider == "fal"
    assert gate.decline("tts") == "tts"
    rows = gate.offers()
    web = _nth_offer(rows, 0)
    image = _nth_offer(rows, 1)
    tts = _nth_offer(rows, 2)
    browser = _nth_offer(rows, 3)
    assert web.reason == "env" and web.checked is False and web.offered is True
    assert image.reason == "explicit" and image.offered is False
    assert tts.reason == "declined" and tts.checked is False
    assert browser.reason == "open" and browser.checked is True
    assert gate.plan() == ()

    def env_over_pin() -> object:
        return gate.note_env("image")

    def admit_pin() -> object:
        return gate.admit(("image",), {"image": "cred-nous"})

    def admit_declined() -> object:
        return gate.admit(("tts", "web"), {"tts": "cred-tts", "web": "cred-web"})

    def fal_on_web() -> object:
        return gate.select("web", "fal", "cred-fal")

    def off_provider() -> object:
        return gate.select("web", "off", "cred-web")

    def yolo_provider() -> object:
        return gate.select("browser", "yolo", "cred-browser")

    def legacy_flag() -> object:
        return gate.legacy("browser", "yes", "cred-browser")

    def legacy_false() -> object:
        return gate.legacy("web", False, "cred-web")

    def clear_missing() -> object:
        return gate.clear_decline("browser")

    assert _code(env_over_pin) == "PINNED"
    assert _code(admit_pin) == "PINNED"
    assert _code(admit_declined) == "DECLINED"
    assert _code(fal_on_web) == "BAD_PROVIDER"
    assert _code(off_provider) == "BAD_PROVIDER"
    assert _code(yolo_provider) == "BAD_PROVIDER"
    assert _code(legacy_flag) == "NOT_BOOL"
    assert _code(legacy_false) == "LEGACY"
    assert _code(clear_missing) == "BAD_STATE"
    assert gate.plan() == ()

    gate.entitle("paid")
    _arm(gate, "web", "cred-web")

    def direct_call() -> object:
        return gate.call("image", "generate", "a card", 1)

    def off_call() -> object:
        return gate.call("browser", "vision", "a card", 1)

    assert gate.offers()[0].reason == "active"
    assert _code(direct_call) == "DIRECT"
    assert _code(off_call) == "OFF"
    assert gate.snapshot().calls == ()
    gate.clear_decline("tts")
    gate.legacy("tts", True, "cred-tts")
    assert gate.plan() == ("web", "tts")
    gate.select("image", "nous", "cred-nous-image")
    assert "image" in gate.plan()

    def bad_offer() -> object:
        return Offer("web", True, True, "nope")

    def bad_via() -> object:
        return Route(name="web", cred_id="cred-web", provider="nous", via="side")

    assert _code(bad_offer) == "BAD_STATE"
    assert _code(bad_via) == "BAD_STATE"


def _nth_offer(rows: tuple[Offer, ...], index: int) -> Offer:
    if index < 0 or index >= len(rows):
        raise AssertionError("missing offer")
    return rows[index]


def test_dispatch_skips_items_that_do_not_fit() -> None:
    gate = _paid()
    _arm(gate, "web", "cred-web")
    batch = gate.dispatch(
        (
            ("web", "search", "a" * 20),
            ("web", "search", "b" * 20),
            ("web", "search", "c" * 10),
        ),
        15,
        budget=30,
    )
    assert batch.skipped == 1
    assert batch.budget == 30
    assert batch.clamped is False
    assert len(batch.calls) == 2
    assert _nth(batch.calls, 0).arg == "a" * 20
    assert _nth(batch.calls, 1).arg == "c" * 10
    assert len(gate.snapshot().calls) == 2

    clamped = gate.dispatch((("web", "search", "Ada"),), 16, budget=BATCH_BUDGET + 25)
    assert clamped.clamped is True
    assert clamped.budget == BATCH_BUDGET
    assert clamped.requested == BATCH_BUDGET + 25

    def empty() -> object:
        return gate.dispatch((), 17)

    def text() -> object:
        return gate.dispatch("web", 17)

    def short() -> object:
        return gate.dispatch((("web", "search"),), 17)

    def flag() -> object:
        return gate.dispatch((("web", "search", "Ada"),), 17, budget=True)

    def zero() -> object:
        return gate.dispatch((("web", "search", "Ada"),), 17, budget=0)

    before = len(gate.snapshot().calls)
    assert _code(empty) == "EMPTY"
    assert _code(text) == "NOT_LIST"
    assert _code(short) == "BAD_CALL"
    assert _code(flag) == "NOT_INT"
    assert _code(zero) == "BAD_LIMIT"
    assert len(gate.snapshot().calls) == before


def test_call_cap_and_retry() -> None:
    gate = _paid()
    _arm(gate, "web", "cred-web")
    for index in range(7):
        gate.call("web", "search", f"note {index}", index + 1)

    def overflow() -> object:
        return gate.dispatch(
            (("web", "search", "one"), ("web", "search", "two")),
            40,
            budget=100,
        )

    assert _code(overflow) == "CALL_CAP"
    assert len(gate.snapshot().calls) == 7
    gate.call("web", "search", "note 7", 8)
    assert len(gate.snapshot().calls) == CALL_CAP

    def ninth() -> object:
        return gate.call("web", "search", "overflow", 9)

    assert _code(ninth) == "CALL_CAP"

    fresh = _paid()
    _arm(fresh, "web", "cred-web")
    first = fresh.call("web", "search", "Ada note", 3, cred_id="cred-web")

    def mismatch() -> object:
        return fresh.call("web", "search", "Ada note", 4, cred_id="cred-other")

    assert _code(mismatch) == "STALE"
    assert len(fresh.snapshot().calls) == 1
    retried = fresh.retry(first.call_id, RETRY_CLASS, 5)
    assert retried.code == "RETRY"
    assert retried.tool == "web"

    def second() -> object:
        return fresh.retry(first.call_id, RETRY_CLASS, 6)

    def other() -> object:
        return fresh.retry(retried.call_id, "TIMEOUT", 7)

    def blank() -> object:
        return fresh.retry(first.call_id, "", 8)

    def missing() -> object:
        return fresh.retry("ab" * 32, RETRY_CLASS, 9)

    def bad_code() -> object:
        return Call(
            schema=SCHEMA,
            tool="web",
            op="search",
            arg="Ada note",
            model="",
            at=1,
            seq=1,
            prev=GENESIS,
            code="NOPE",
        )

    assert _code(second) == "RETRY_CAP"
    assert _code(other) == "NO_RETRY"
    assert _code(blank) == "BAD_FAILURE"
    assert _code(missing) == "BAD_CALL"
    assert _code(bad_code) == "BAD_CALL"
    loaded = ToolGateway.load(fresh.snapshot())

    def again() -> object:
        return loaded.retry(first.call_id, RETRY_CLASS, 10)

    assert _code(again) == "RETRY_CAP"
    assert loaded.plan() == ("web",)


def test_rebuild_refuses_a_bad_chain() -> None:
    first = _web_call(1, GENESIS, "Ada note", 1)
    second = _web_call(2, GENESIS, "later note", 2)

    def broken() -> object:
        return _snap(calls=(first, second), fence=second.digest)

    def stale() -> object:
        return _snap(calls=(first,), fence="ab" * 32)

    def duplicate() -> object:
        twin = _web_call(1, GENESIS, "Ada note", 1)
        return _snap(calls=(first, twin), fence=first.digest)

    def bad_type() -> object:
        return rebuild(None)

    def bad_fence() -> object:
        return _snap(fence="z" * 64)

    def pool() -> object:
        return _snap(model="krea-2-medium", entitled="pool")

    def kind() -> object:
        return _snap(entitled="yolo")

    def backwards() -> object:
        return _snap(routes=(("browser", "cred-browser"), ("web", "cred-web")))

    def missing_retry() -> object:
        return _snap(retried=("ab" * 32,))

    assert _code(broken) == "BROKEN_CHAIN"
    assert _code(stale) == "STALE"
    assert _code(duplicate) == "DUPLICATE"
    assert _code(bad_type) == "BAD_SNAPSHOT"
    assert _code(bad_fence) == "BAD_SNAPSHOT"
    assert _code(pool) == "POOL"
    assert _code(kind) == "BAD_KIND"
    assert _code(backwards) == "BAD_SNAPSHOT"
    assert _code(missing_retry) == "BAD_SNAPSHOT"
    assert rebuild(_snap()) == _snap()


def test_no_network_surface() -> None:
    module_file = ToolGateway.__module__
    loaded = __import__(module_file).__file__
    assert loaded is not None
    tree = ast.parse(Path(loaded).read_text(encoding="utf-8"))
    banned = {"socket", "subprocess", "urllib", "requests", "http", "pickle", "threading"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name.split(".")[0] not in banned
        if isinstance(node, ast.ImportFrom) and node.module is not None:
            assert node.module.split(".")[0] not in banned
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            assert node.func.id not in {"exec", "eval", "compile", "__import__"}
