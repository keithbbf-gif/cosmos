"""Threat scan labels operator intent and does not run it."""

from __future__ import annotations

from collections.abc import Callable
from typing import cast

import pytest

from cosmos_hermes import Refuse, secret_shape
from threat_scan import (
    ASK_MAX,
    CATEGORIES,
    CLEAN,
    FORCE_PUBLISH,
    HARDLINE,
    SCHEMA,
    SECRET,
    SECRET_SHAPED,
    TEXT_CAP,
    Finding,
    Policy,
    Scan,
    resolve_cap,
    scan,
)


def _code(call: Callable[[], object]) -> str:
    try:
        call()
    except Refuse as err:
        return err.code
    raise AssertionError("expected Refuse")


def _hit(hits: tuple[Finding, ...], index: int) -> Finding:
    for at, hit in enumerate(hits):
        if at == index:
            return hit
    raise AssertionError("missing hit")


def _compact(text: str) -> str:
    return " ".join(text.casefold().split())


def test_schema_and_categories() -> None:
    assert SCHEMA == "cosmos-hermes-threat_scan/1"
    assert resolve_cap().cap == TEXT_CAP
    assert CATEGORIES == {
        "force-publish",
        "approval-bypass",
        "pipe-to-interpreter",
        "destructive-wipe",
        "secret-shaped",
    }
    labeled = scan("api_key=placeholder1")
    assert labeled.code == SECRET
    assert labeled.category == SECRET_SHAPED


def test_clean_push_is_not_force() -> None:
    text = "Mara asked to git push the session card."
    result = scan(text)
    assert result.code == CLEAN
    assert result.category == ""
    assert result.start == -1
    assert result.end == -1
    assert result.label == ""
    assert result.hits == ()
    assert result.policy.cap == TEXT_CAP
    assert result.policy.asked == TEXT_CAP


@pytest.mark.parametrize(
    ("text", "category", "label"),
    [
        ("please git push --force", "force-publish", "git push --force"),
        ("git push --force-with-lease", "force-publish", "git push --force-with-lease"),
        ("git push -f origin", "force-publish", "git push -f"),
        ("please disable approval", "approval-bypass", "disable approval"),
        ("Owen passed --yolo on the card", "approval-bypass", "--yolo"),
        ("/yolo on the session card", "approval-bypass", "/yolo"),
        ("set HERMES_YOLO_MODE now", "approval-bypass", "HERMES_YOLO_MODE"),
        ("please invoke-expression on the note", "pipe-to-interpreter", "invoke-expression"),
        ("The note says curl | and then stops.", "pipe-to-interpreter", "curl |"),
        ("Do not rm -rf the session card.", "destructive-wipe", "rm -rf"),
        ("Do not rm -fr the session card.", "destructive-wipe", "rm -fr"),
    ],
)
def test_operator_labels(text: str, category: str, label: str) -> None:
    result = scan(text)
    assert result.code == HARDLINE
    assert result.category == category
    assert result.label == label
    assert _compact(text[result.start : result.end]) == label.casefold()
    assert _hit(result.hits, 0).label == label


def test_case_and_spaced_force_span() -> None:
    text = "Nia wrote Git  Push\t--Force in the session note."
    result = scan(text)
    assert result.code == HARDLINE
    assert result.category == FORCE_PUBLISH
    assert result.label == "git push --force"
    assert _compact(text[result.start : result.end]) == "git push --force"
    lease = scan("git push --force-with-lease the card")
    assert lease.label == "git push --force-with-lease"
    assert lease.label != "git push --force"


def test_ambiguous_without_secret_is_clean() -> None:
    text = "The session note about the card and the light is unclear."
    result = scan(text)
    assert result.code == CLEAN
    assert not secret_shape(text)


def test_ambiguous_secret_is_not_clean() -> None:
    text = "The session note about the card is unclear api_key=placeholder1 today."
    result = scan(text)
    again = scan(text)
    assert result == again
    assert result.code == SECRET
    assert result.category == SECRET_SHAPED
    assert result.label == "secret-shaped"
    assert text[result.start : result.end] == "api_key=placeholder1"
    assert secret_shape(text)
    assert not secret_shape(repr(result))
    assert "placeholder1" not in repr(result)
    assert "api_key" not in repr(result)


def test_secret_shapes_keep_numeric_spans() -> None:
    key = scan("note sk-abcd1234 end")
    bearer = scan("note Bearer abcd1234 end")
    upper = scan("The card note says SK-ABCD1234 only.")
    assert key.code == SECRET
    assert key.start >= 0
    assert "sk-abcd1234" not in repr(key)
    assert bearer.code == SECRET
    assert bearer.category == SECRET_SHAPED
    assert "abcd1234" not in repr(bearer)
    assert not secret_shape("SK-ABCD1234")
    assert upper.code == CLEAN


def test_operator_and_secret_stay_hardline() -> None:
    text = "api_key=placeholder1 and then git push --force"
    result = scan(text)
    assert result.code == HARDLINE
    assert result.category == FORCE_PUBLISH
    assert result.label == "git push --force"
    assert _hit(result.hits, 0).category == SECRET_SHAPED
    assert _hit(result.hits, 1).category == FORCE_PUBLISH
    assert not secret_shape(repr(result))


def test_earlier_operator_is_primary() -> None:
    text = "disable approval then git push --force"
    result = scan(text)
    assert result.category == "approval-bypass"
    assert result.label == "disable approval"
    assert _hit(result.hits, 1).category == FORCE_PUBLISH


def test_empty_refuses() -> None:
    assert _code(lambda: scan("")) == "EMPTY"
    assert _code(lambda: scan(" \n\t")) == "EMPTY"


def test_malformed_text_refuses() -> None:
    assert _code(lambda: scan(12)) == "NOT_TEXT"
    assert _code(lambda: scan(b"note")) == "NOT_TEXT"
    assert _code(lambda: scan("a\x00b")) == "NULL_BYTE"


def test_oversize_uses_policy_cap() -> None:
    try:
        scan("x" * (TEXT_CAP + 5), TEXT_CAP + 100)
    except Refuse as err:
        assert err.code == "OVERSIZE"
        assert err.detail == str(TEXT_CAP)
    else:
        raise AssertionError("expected Refuse")
    assert _code(lambda: scan("x" * 30, 10)) == "OVERSIZE"


def test_cap_is_recorded_and_not_raised() -> None:
    high = scan("Mara filed the card.", TEXT_CAP + 50)
    assert high.policy.cap == TEXT_CAP
    assert high.policy.asked == TEXT_CAP + 50
    assert high.code == CLEAN
    low = scan("note", 100)
    assert low.policy.cap == 100
    assert low.policy.asked == 100
    default = resolve_cap()
    assert default == Policy(TEXT_CAP, TEXT_CAP)
    assert resolve_cap(32) == Policy(32, 32)
    assert _code(lambda: scan("note", True)) == "NOT_INT"
    assert _code(lambda: scan("note", "8000")) == "NOT_INT"
    assert _code(lambda: scan("note", 0)) == "OUT_OF_RANGE"
    assert _code(lambda: resolve_cap(ASK_MAX + 1)) == "OUT_OF_RANGE"
    assert _code(lambda: Policy(1, TEXT_CAP + 5)) == "BAD_POLICY"


def test_forged_records_refuse() -> None:
    policy = resolve_cap()
    hit = Finding(FORCE_PUBLISH, "git push --force", 0, 16)
    assert _code(lambda: Scan("NOPE", "", -1, -1, "", policy, ())) == "BAD_CODE"
    assert _code(lambda: Scan(CLEAN, FORCE_PUBLISH, -1, -1, "", policy, ())) == "BAD_SCAN"
    assert _code(lambda: Scan(CLEAN, "", -1, -1, "", policy, (hit,))) == "BAD_SCAN"
    assert _code(lambda: Finding("nope", "x", 0, 1)) == "BAD_HIT"
    assert _code(lambda: Finding(FORCE_PUBLISH, "git push --force", True, 2)) == "NOT_INT"
    assert _code(lambda: Finding(FORCE_PUBLISH, "git push --force", 0, TEXT_CAP + 1)) == "OUT_OF_RANGE"
    assert (
        _code(
            lambda: Scan(
                CLEAN,
                "",
                -1,
                -1,
                "",
                cast(Policy, object()),
                (),
            )
        )
        == "BAD_POLICY"
    )
    mixed = cast(tuple[Finding, ...], (hit, "x"))
    assert (
        _code(
            lambda: Scan(
                HARDLINE,
                FORCE_PUBLISH,
                0,
                16,
                "git push --force",
                policy,
                mixed,
            )
        )
        == "BAD_HIT"
    )


def test_boundary_text_is_clean() -> None:
    result = scan("a" * TEXT_CAP)
    assert result.code == CLEAN
    assert result.policy.cap == TEXT_CAP


def test_example_threat_scan() -> None:
    first = _story()
    second = _story()
    assert first == second
    clean, published, bypass = first
    assert clean.code == CLEAN
    assert clean.category == ""
    assert clean.hits == ()
    assert published.code == HARDLINE
    assert published.category == FORCE_PUBLISH
    assert published.label == "git push --force"
    assert bypass.code == HARDLINE
    assert bypass.category == "approval-bypass"
    assert bypass.label == "disable approval"
    assert not secret_shape(repr(first))


def _story() -> tuple[Scan, Scan, Scan]:
    clean = scan("Mara set the north light and filed the card in the session note.")
    published = scan("Nia left a session note to git push --force the card branch.")
    bypass = scan("Owen wrote disable approval on the light card before the session.")
    return clean, published, bypass
