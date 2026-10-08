"""DOM descriptors: http(s) only, file and dot-dot refuse, no launch."""

from __future__ import annotations

import dataclasses
from collections.abc import Callable
from typing import NamedTuple

import pytest

import browser
from browser import (
    MAX_ATTEMPT,
    MIN_SNAPSHOT,
    PAGE_CAP,
    PLAN_CAP,
    SCHEMA,
    SELECTOR_CAP,
    SNAPSHOT_CAP,
    TEXT_CAP,
    URL_CAP,
    BrowserPlan,
    DomDescriptor,
    SnapshotView,
    back,
    click,
    dialog,
    open_page,
    pack_snapshot,
    plan,
    press,
    rebuild,
    retry,
    run,
    scroll,
    snapshot,
    type_text,
)
from cosmos_hermes import Refuse, secret_shape


def _expect(code: str, func: Callable[[], object]) -> None:
    with pytest.raises(Refuse) as caught:
        func()
    assert caught.value.code == code


def _run(func: Callable[..., object], *args: object) -> Callable[[], object]:
    def call() -> object:
        return func(*args)

    return call


class _Story(NamedTuple):
    opened: DomDescriptor
    packed: SnapshotView
    note: DomDescriptor
    built: BrowserPlan
    rebuilt: BrowserPlan
    file_code: str
    dot_code: str


def _story() -> _Story:
    """Ada opens the Light plan on the pricing card. The session is a descriptor."""
    opened = open_page("https://example.com/pricing", "pricing-card", "open-card")
    page = "Light plan\n" + ("H" * (MIN_SNAPSHOT + 50)) + "\nAda note"
    packed = pack_snapshot(page, threshold=MIN_SNAPSHOT)
    note = type_text("#note", "Light plan note", "pricing-card", "type-note")
    hidden = type_text(
        "#card-secret",
        "",
        "pricing-card",
        "type-secret",
        password=True,
        credential_id="vault-card",
    )
    clicked = click("@e4", "pricing-card", "click-buy")
    built = plan("pricing-card", (opened, note, hidden, clicked))
    rebuilt = rebuild(built.steps, built.session)
    file_code = ""
    try:
        open_page("file:///etc/passwd", "pricing-card", "open-file")
    except Refuse as err:
        file_code = err.code
    dot_code = ""
    try:
        open_page("https://example.com/../pricing", "pricing-card", "open-dot")
    except Refuse as err:
        dot_code = err.code
    return _Story(
        opened=opened,
        packed=packed,
        note=note,
        built=built,
        rebuilt=rebuilt,
        file_code=file_code,
        dot_code=dot_code,
    )


def _step(record: BrowserPlan, index: int) -> DomDescriptor:
    return record.steps[index]


def test_example_browser() -> None:
    first = _story()
    second = _story()
    assert first == second
    assert first.opened.url == "https://example.com/pricing"
    assert first.opened.op == "navigate"
    assert first.opened.code == "READY"
    assert first.opened.session == "pricing-card"
    assert first.opened.attempt == 1
    assert first.file_code == "FILE_URL"
    assert first.dot_code == "DOTDOT"
    assert first.rebuilt == first.built
    assert first.packed.text == "Light plan\nAda note"
    assert first.packed.skipped == 1
    assert first.packed.cap == MIN_SNAPSHOT
    assert "H" * 20 not in first.packed.text
    assert first.note.text == "Light plan note"
    hidden = _step(first.built, 2)
    assert hidden.code == "CONFIRM"
    assert hidden.credential_id == "vault-card"
    assert hidden.text == ""
    assert secret_shape(repr(first.opened)) is False
    assert secret_shape(repr(hidden)) is False
    assert secret_shape(repr(first.built)) is False
    _expect("NO_LAUNCH", _run(run, first.opened))


def test_schema_and_success_urls() -> None:
    assert browser.SCHEMA == "cosmos-hermes-browser/1"
    assert SCHEMA == browser.SCHEMA
    job = open_page("https://example.com/pricing?plan=pro#buy", "pricing-card", "open-card")
    assert job == open_page("https://example.com/pricing?plan=pro#buy", "pricing-card", "open-card")
    assert job.schema == SCHEMA
    plain = open_page("HTTP://Example.COM/a", "pricing-card", "open-card")
    assert plain.url == "HTTP://Example.COM/a"
    local = open_page("http://127.0.0.1:9/", "pricing-card", "open-card")
    assert local.url == "http://127.0.0.1:9/"
    v6 = open_page("http://[::1]/", "pricing-card", "open-card")
    assert v6.url == "http://[::1]/"
    ported = open_page("http://[::1]:8080/pricing", "pricing-card", "open-card")
    assert ported.code == "READY"
    mailed = open_page(
        "https://example.com/pricing?email=ada@example.com",
        "pricing-card",
        "open-card",
    )
    assert mailed.url.endswith("ada@example.com")
    encoded = open_page("https://example.com/pricing?q=a%20b", "pricing-card", "open-card")
    assert encoded.op == "navigate"
    flagged = open_page(
        "https://example.com/pricing",
        "pricing-card",
        "open-card",
        require_session=True,
    )
    assert flagged.require_session is True


@pytest.mark.parametrize(
    "raw",
    [
        "file:///etc/passwd",
        "file:///C:/Windows/system.ini",
        "FILE:/tmp/x",
        "file:foo",
        "file://localhost/etc/passwd",
        "File:///etc/passwd",
        "file:///C:/Windows/../secret",
    ],
)
def test_file_url_refuses(raw: str) -> None:
    _expect("FILE_URL", _run(open_page, raw, "pricing-card", "open-card"))


@pytest.mark.parametrize(
    "raw",
    [
        "https://example.com/../pricing",
        "https://example.com/a/../../etc/passwd",
        "https://example.com/%2e%2e/pricing",
        "https://example.com/%2E%2E/secret",
        "https://example.com/foo/%2e./bar",
        "https://example.com/foo/.%2e/bar",
        "https://example.com/%252e%252e/pricing",
        "https://example..com/pricing",
        "https://example.com/pricing?next=../admin",
        "http://[::1]/../x",
    ],
)
def test_dotdot_url_refuses(raw: str) -> None:
    _expect("DOTDOT", _run(open_page, raw, "pricing-card", "open-card"))


@pytest.mark.parametrize(
    "raw",
    [
        "javascript:alert(1)",
        "data:text/html,hi",
        "ftp://example.com/a",
        "about:blank",
        "ws://127.0.0.1:9222",
        "wss://example.com/",
        "http://",
        "http:///x",
        "http://user:pass@example.com",
        "http://user@example.com/a",
        "http://example.com:99999/",
        "http://example.com:0/",
        "http://example.com:abc/",
        " http://example.com",
        "http://example.com/a b",
        "http://example.com\\@evil",
        "//example.com",
        "http:/example.com",
        "chrome://version",
        "https://example.com/%00",
        "https://example.com:\u00b2/",
        "https://example.com:\u0661/",
        "https://example.com/foo%2fbar",
        "https://example.com/a%0ab",
        "http://[::1",
        "http://::1/",
        "https://example.com:65536/pricing",
    ],
)
def test_bad_url(raw: str) -> None:
    _expect("BAD_URL", _run(open_page, raw, "pricing-card", "open-card"))


def test_url_bounds_and_secret() -> None:
    _expect("NOT_TEXT", _run(open_page, None, "pricing-card", "open-card"))
    _expect("NULL_BYTE", _run(open_page, "https://example.com/\x00", "pricing-card", "open-card"))
    _expect("OVERSIZE", _run(open_page, "https://example.com/" + ("a" * URL_CAP), "pricing-card", "open-card"))
    _expect("SECRET", _run(open_page, "https://example.com/?api_key=abcdef", "pricing-card", "open-card"))
    _expect("SECRET", _run(open_page, "https://example.com/sk-livekeyvalue", "pricing-card", "open-card"))
    _expect("BAD_ID", _run(open_page, "https://example.com/pricing", "", "open-card"))
    _expect("BAD_ID", _run(open_page, "https://example.com/pricing", "Pricing", "open-card"))


def test_not_bool_require_session() -> None:
    def ask() -> object:
        return open_page(
            "https://example.com/pricing",
            "pricing-card",
            "open-card",
            require_session="yes",
        )

    _expect("NOT_BOOL", ask)


def test_click_snapshot_scroll_press_back_dialog() -> None:
    clicked = click("@e5", "pricing-card", "click-buy")
    assert clicked.op == "click"
    assert clicked.selector == "@e5"
    assert click("button span", "pricing-card", "click-buy").selector == "button span"
    shot = snapshot("pricing-card", "shot-card")
    assert shot.op == "snapshot"
    assert shot.full is False
    assert shot.snapshot_cap == SNAPSHOT_CAP
    moved = scroll("down", "pricing-card", "scroll-card")
    assert moved.direction == "down"
    keyed = press("Enter", "pricing-card", "press-enter")
    assert keyed.key == "Enter"
    assert keyed.code == "READY"
    previous = back("pricing-card", "back-card")
    assert previous.op == "back"
    accepted = dialog("accept", "pricing-card", "dialog-card", "Ada note")
    assert accepted.dialog == "accept"
    assert accepted.prompt == "Ada note"
    dismissed = dialog("dismiss", "pricing-card", "dialog-card")
    assert dismissed.prompt == ""
    for job in (clicked, shot, moved, keyed, previous, accepted):
        assert isinstance(job, DomDescriptor)
        params = getattr(job, "__dataclass_params__")
        assert params.frozen is True
        with pytest.raises(dataclasses.FrozenInstanceError):
            setattr(job, "op", "navigate")
    _expect("BAD_SELECTOR", _run(click, "", "pricing-card", "click-buy"))
    _expect("BAD_SELECTOR", _run(click, "  #id", "pricing-card", "click-buy"))
    _expect("BAD_SELECTOR", _run(click, "javascript:alert(1)", "pricing-card", "click-buy"))
    _expect("SECRET", _run(click, "sk-livekeyvalue", "pricing-card", "click-buy"))
    _expect("NOT_TEXT", _run(click, 12, "pricing-card", "click-buy"))
    _expect("OVERSIZE", _run(click, "a" * (SELECTOR_CAP + 1), "pricing-card", "click-buy"))
    _expect("BAD_DIRECTION", _run(scroll, "left", "pricing-card", "scroll-card"))
    _expect("BAD_DIRECTION", _run(scroll, "UP", "pricing-card", "scroll-card"))
    _expect("BAD_KEY", _run(press, "enter", "pricing-card", "press-enter"))
    _expect("BAD_KEY", _run(press, "Control", "pricing-card", "press-enter"))
    _expect("BAD_DIALOG", _run(dialog, "cancel", "pricing-card", "dialog-card"))

    def dismiss_with_prompt() -> object:
        return dialog("dismiss", "pricing-card", "dialog-card", "nope")

    _expect("BAD_DIALOG", dismiss_with_prompt)
    _expect("SECRET", _run(dialog, "accept", "pricing-card", "dialog-card", "api_key=abcdef"))


def test_snapshot_cap_is_policy() -> None:
    asked = SNAPSHOT_CAP + 50
    job = snapshot("pricing-card", "shot-card", full=True, threshold=asked)
    assert job.full is True
    assert job.snapshot_cap == SNAPSHOT_CAP
    assert job.snapshot_cap != asked
    tight = snapshot("pricing-card", "shot-card", threshold=MIN_SNAPSHOT)
    assert tight.snapshot_cap == MIN_SNAPSHOT
    mid = snapshot("pricing-card", "shot-card", threshold=4_000)
    assert mid.snapshot_cap == 4_000
    assert snapshot("pricing-card", "shot-card").snapshot_cap == SNAPSHOT_CAP

    def too_small() -> object:
        return snapshot("pricing-card", "shot-card", threshold=MIN_SNAPSHOT - 1)

    def flag() -> object:
        return snapshot("pricing-card", "shot-card", threshold=True)

    def fractional() -> object:
        return snapshot("pricing-card", "shot-card", threshold=1.5)

    def bad_full() -> object:
        return snapshot("pricing-card", "shot-card", full="yes")

    _expect("OUT_OF_RANGE", too_small)
    _expect("NOT_INT", flag)
    _expect("NOT_INT", fractional)
    _expect("NOT_BOOL", bad_full)


def test_pack_skips_line_that_does_not_fit() -> None:
    cap = MIN_SNAPSHOT
    huge = "H" * (cap + 1)
    view = pack_snapshot("head\n" + huge + "\ntail", threshold=cap)
    assert view.text == "head\ntail"
    assert view.kept == 2
    assert view.skipped == 1
    assert view.truncated is True
    assert view.cap == cap
    exact = "E" * cap
    full = pack_snapshot(exact + "\nZ", threshold=cap)
    assert full.text == exact
    assert full.skipped == 1
    assert pack_snapshot("", threshold=cap).kept == 0
    late = pack_snapshot(huge + "\nAda note", threshold=cap)
    assert late.text == "Ada note"
    assert late.skipped == 1
    clamped = pack_snapshot("Light plan", threshold=SNAPSHOT_CAP + 10)
    assert clamped.cap == SNAPSHOT_CAP
    assert clamped.text == "Light plan"
    _expect("SECRET", _run(pack_snapshot, "api_key=abcdef"))
    _expect("OVERSIZE", _run(pack_snapshot, "a" * (PAGE_CAP + 1)))
    _expect("NOT_TEXT", _run(pack_snapshot, None))


def test_type_text_credential_and_repr() -> None:
    plain = type_text("#note", "Light plan note", "pricing-card", "type-note")
    assert plain.code == "READY"
    assert plain.text == "Light plan note"
    assert plain.password is False
    hidden = type_text(
        "#card-secret",
        "",
        "pricing-card",
        "type-secret",
        password=True,
        credential_id="vault-card",
    )
    assert hidden.code == "CONFIRM"
    assert hidden.password is True
    assert hidden.text == ""
    assert hidden.credential_id == "vault-card"
    assert "sk-" not in repr(hidden)
    assert "Bearer " not in repr(hidden)
    assert "api_key=" not in repr(hidden)
    assert secret_shape(repr(hidden)) is False
    _expect("SECRET", _run(type_text, "#note", "sk-livekeyvalue", "pricing-card", "type-note"))
    _expect("SECRET", _run(type_text, "#note", "Bearer abcdefghijk", "pricing-card", "type-note"))

    def password_body() -> object:
        return type_text(
            "#card-secret",
            "s3cret-value",
            "pricing-card",
            "type-secret",
            password=True,
            credential_id="vault-card",
        )

    def missing_credential() -> object:
        return type_text(
            "#card-secret",
            "",
            "pricing-card",
            "type-secret",
            password=True,
            credential_id="",
        )

    def secret_credential() -> object:
        return type_text(
            "#card-secret",
            "",
            "pricing-card",
            "type-secret",
            password=True,
            credential_id="sk-livekeyvalue",
        )

    _expect("BAD_TEXT", password_body)
    _expect("BAD_ID", missing_credential)
    _expect("SECRET", secret_credential)
    _expect("NOT_TEXT", _run(type_text, "#note", 12, "pricing-card", "type-note"))
    _expect("NULL_BYTE", _run(type_text, "#note", "a\x00b", "pricing-card", "type-note"))
    _expect("OVERSIZE", _run(type_text, "#note", "a" * (TEXT_CAP + 1), "pricing-card", "type-note"))
    _expect("BAD_TEXT", _run(type_text, "#note", "a\nb", "pricing-card", "type-note"))

    def bad_password() -> object:
        return type_text("#note", "x", "pricing-card", "type-note", password=1)

    _expect("NOT_BOOL", bad_password)

    def credential_without_password() -> object:
        return type_text("#note", "x", "pricing-card", "type-note", credential_id="vault-card")

    _expect("BAD_JOB", credential_without_password)


def test_retry_cap_and_named_failure() -> None:
    job = open_page("https://example.com/pricing", "pricing-card", "open-card")
    again = retry(job, "UNREACHABLE")
    assert again.attempt == 2
    assert again.url == job.url
    assert job.attempt == 1
    assert again == retry(open_page("https://example.com/pricing", "pricing-card", "open-card"), "UNREACHABLE")
    _expect("RETRY_CAP", _run(retry, again, "UNREACHABLE"))
    _expect("NO_RETRY", _run(retry, job, "BROKE"))
    _expect("NO_RETRY", _run(retry, job, "AUTH_REQUIRED"))
    _expect("NO_RETRY", _run(retry, job, "SESSION_EXPIRED"))
    _expect("NO_RETRY", _run(retry, job, "unreachable"))
    hidden = type_text(
        "#card-secret",
        "",
        "pricing-card",
        "type-secret",
        password=True,
        credential_id="vault-card",
    )
    _expect("NO_RETRY", _run(retry, hidden, "UNREACHABLE"))
    _expect("BAD_JOB", _run(retry, "https://example.com/pricing", "UNREACHABLE"))
    _expect("NOT_TEXT", _run(retry, job, 3))
    _expect("SECRET", _run(retry, job, "api_key=abcdef"))
    assert MAX_ATTEMPT == 2
    shot = snapshot("pricing-card", "shot-card", threshold=SNAPSHOT_CAP + 1)
    retried = retry(shot, "UNREACHABLE")
    assert retried.snapshot_cap == SNAPSHOT_CAP
    assert retried.attempt == MAX_ATTEMPT


def test_run_refuses_launch() -> None:
    _expect("NO_LAUNCH", _run(run, click("@e1", "pricing-card", "click-buy")))
    _expect("NO_LAUNCH", run)


def test_plan_rebuild_and_duplicates() -> None:
    opened = open_page("https://example.com/pricing", "pricing-card", "open-card")
    note = type_text("#note", "Light plan note", "pricing-card", "type-note")
    built = plan("pricing-card", [opened, note], threshold=SNAPSHOT_CAP + 9)
    assert built.snapshot_cap == SNAPSHOT_CAP
    assert rebuild(built.steps, built.session, SNAPSHOT_CAP + 9) == built
    assert rebuild(built.steps, built.session) == plan("pricing-card", built.steps)
    _expect("DUPLICATE", _run(plan, "pricing-card", (opened, opened)))
    _expect("BAD_PLAN", _run(plan, "pricing-card", ()))
    _expect("BAD_PLAN", _run(plan, "pricing-card", "open-card"))
    _expect("BAD_JOB", _run(plan, "pricing-card", (back("other-card", "back-card"),)))
    _expect("BAD_JOB", _run(plan, "pricing-card", ("nope",)))
    steps: list[DomDescriptor] = []
    for index in range(PLAN_CAP + 1):
        steps.append(back("pricing-card", f"step-{index:02d}"))
    _expect("OVERSIZE", _run(plan, "pricing-card", steps))


def test_direct_construct_refusals() -> None:
    _expect(
        "BAD_JOB",
        _run(
            DomDescriptor,
            "other",
            "pricing-card",
            "open-card",
            "click",
            "READY",
            "",
            "@e1",
            "",
            False,
            0,
            "",
            "",
            "",
            "",
            "",
            False,
            False,
            1,
        ),
    )
    _expect(
        "BAD_CODE",
        _run(
            DomDescriptor,
            SCHEMA,
            "pricing-card",
            "click-buy",
            "click",
            "CONFIRM",
            "",
            "@e1",
            "",
            False,
            0,
            "",
            "",
            "",
            "",
            "",
            False,
            False,
            1,
        ),
    )
    _expect(
        "BAD_CAP",
        _run(
            DomDescriptor,
            SCHEMA,
            "pricing-card",
            "shot-card",
            "snapshot",
            "READY",
            "",
            "",
            "",
            False,
            SNAPSHOT_CAP + 1,
            "",
            "",
            "",
            "",
            "",
            False,
            False,
            1,
        ),
    )
    _expect(
        "BAD_ATTEMPT",
        _run(
            DomDescriptor,
            SCHEMA,
            "pricing-card",
            "click-buy",
            "click",
            "READY",
            "",
            "@e1",
            "",
            False,
            0,
            "",
            "",
            "",
            "",
            "",
            False,
            False,
            3,
        ),
    )
    _expect(
        "SECRET",
        _run(
            DomDescriptor,
            SCHEMA,
            "pricing-card",
            "type-note",
            "type_text",
            "READY",
            "",
            "#note",
            "sk-livekeyvalue",
            False,
            0,
            "",
            "",
            "",
            "",
            "",
            False,
            False,
            1,
        ),
    )
    _expect(
        "FILE_URL",
        _run(
            DomDescriptor,
            SCHEMA,
            "pricing-card",
            "open-card",
            "navigate",
            "READY",
            "file:///etc/passwd",
            "",
            "",
            False,
            0,
            "",
            "",
            "",
            "",
            "",
            False,
            False,
            1,
        ),
    )
    _expect(
        "BAD_PLAN",
        _run(
            BrowserPlan,
            SCHEMA,
            "pricing-card",
            (),
            SNAPSHOT_CAP,
        ),
    )
    _expect(
        "BAD_CAP",
        _run(
            SnapshotView,
            SCHEMA,
            "x" * (MIN_SNAPSHOT + 1),
            MIN_SNAPSHOT,
            1,
            0,
            False,
        ),
    )
