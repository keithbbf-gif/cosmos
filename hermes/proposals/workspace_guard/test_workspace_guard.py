"""Grant containment, spill refusal, and the policy cap."""

from __future__ import annotations

import shutil
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import pytest

import workspace_guard
from cosmos_hermes import PathJail, Refuse, redact, secret_shape
from workspace_guard import (
    POLICY_CAP,
    SCHEMA,
    AppliedCap,
    applied_cap,
    check_outbound,
    check_write,
)


@contextmanager
def _pair() -> Iterator[tuple[Path, Path]]:
    grant = Path(tempfile.mkdtemp(prefix="workspace_guard_"))
    other = Path(tempfile.mkdtemp(prefix="workspace_guard_out_"))
    try:
        yield grant, other
    finally:
        shutil.rmtree(grant, ignore_errors=True)
        shutil.rmtree(other, ignore_errors=True)


def _write_code(jail: PathJail, raw: str) -> str:
    try:
        check_write(jail, raw)
    except Refuse as caught:
        return caught.code
    raise AssertionError("expected refuse")


def _text_code(text: str) -> str:
    try:
        check_outbound(text)
    except Refuse as caught:
        return caught.code
    raise AssertionError("expected refuse")


def _file_url(path: Path) -> str:
    return "file:///" + str(path).replace("\\", "/")


def test_schema_and_exports() -> None:
    assert SCHEMA == "cosmos-hermes-workspace_guard/1"
    assert workspace_guard.SCHEMA == SCHEMA
    assert POLICY_CAP == 32_000
    assert workspace_guard.__all__ == [
        "POLICY_CAP",
        "SCHEMA",
        "AppliedCap",
        "applied_cap",
        "check_outbound",
        "check_write",
    ]


def test_write_inside_grant_and_plain_outbound() -> None:
    with _pair() as (grant, other):
        jail = PathJail((str(grant), str(other)))
        inside = grant / "note.txt"
        side = other / "a.txt"
        assert not inside.exists()
        contained = check_write(jail, str(inside))
        assert contained == inside.resolve()
        assert check_write(jail, str(grant)) == grant.resolve()
        assert check_write(jail, str(side)) == side.resolve()
        assert check_write(jail, str(inside)) == contained
        assert not inside.exists()
        assert list(grant.iterdir()) == []
        plain = "workspace note"
        assert check_outbound(plain) == redact(plain) == plain
        assert check_outbound("") == ""
        assert check_outbound(plain) == check_outbound(plain)
        assert secret_shape(repr(contained)) is False
        assert secret_shape(check_outbound(plain)) is False


def test_outside_grant_raises_outside() -> None:
    with _pair() as (grant, other):
        jail = PathJail([str(grant)])
        outside = other / "x"
        with pytest.raises(Refuse) as caught:
            check_write(jail, str(outside))
        assert caught.value.code == "OUTSIDE_GRANT"
        assert caught.value.detail == ""
        assert not outside.exists()
        assert list(grant.iterdir()) == []


def test_jail_refusals_pass_through() -> None:
    with _pair() as (grant, _other):
        jail = PathJail([str(grant)])
        card = grant / "session" / "card.txt"
        samples = {
            "": "BAD_PATH",
            "card.txt": "RELATIVE_PATH",
            str(grant / "session" / ".." / "card.txt"): "DOTDOT",
            str(grant / "session" / "%2e%2e" / "card.txt"): "ENCODED_DOTDOT",
            _file_url(card): "FILE_URL",
            "\\\\server\\share\\session\\card.txt": "UNC",
            "//server/share/session/card.txt": "UNC",
            "C:\\": "DRIVE_ROOT",
            "C:card.txt": "DRIVE_RELATIVE",
            str(card) + ":stream": "ALT_STREAM",
            str(grant / "session" / "card."): "TRAILING_DOT",
            str(grant / "session" / "card\n.txt"): "BAD_PATH",
        }
        for raw, code in samples.items():
            with pytest.raises(Refuse) as caught:
                check_write(jail, raw)
            assert caught.value.code == code
            assert caught.value.detail == ""
            assert secret_shape(str(caught.value)) is False
        assert list(grant.iterdir()) == []


def test_shape_wins_over_spill() -> None:
    with _pair() as (grant, _other):
        jail = PathJail([str(grant)])
        shaped = (
            str(grant / ".." / "sk-livekeyvalue"),
            "\\\\server\\share\\sk-livekeyvalue",
            "file:///C:/session/sk-livekeyvalue",
        )
        expect = ("DOTDOT", "UNC", "FILE_URL")
        for raw, code in zip(shaped, expect, strict=True):
            with pytest.raises(Refuse) as caught:
                check_write(jail, raw)
            assert caught.value.code == code
            assert "sk-livekeyvalue" not in str(caught.value)
            assert "sk-livekeyvalue" not in repr(caught.value)
            assert secret_shape(str(caught.value)) is False
        assert list(grant.iterdir()) == []


def test_empty_grant_refuses() -> None:
    with pytest.raises(Refuse) as empty_list:
        PathJail([])
    assert empty_list.value.code == "NO_GRANT"
    with pytest.raises(Refuse) as empty_tuple:
        PathJail(())
    assert empty_tuple.value.code == "NO_GRANT"
    with pytest.raises(Refuse) as relative:
        PathJail(["session/card"])
    assert relative.value.code == "RELATIVE_GRANT"


def test_bad_jail() -> None:
    for jail in (None, "C:\\grant", Path("C:\\grant"), 0):
        with pytest.raises(Refuse) as caught:
            check_write(jail, "C:\\grant\\a")
        assert caught.value.code == "BAD_JAIL"


def test_bound_refusals() -> None:
    with _pair() as (grant, _other):
        jail = PathJail([str(grant)])
        for value in (None, 1, b"abc", ["a"], Path(grant)):
            with pytest.raises(Refuse) as outbound:
                check_outbound(value)
            assert outbound.value.code == "NOT_TEXT"
            with pytest.raises(Refuse) as write:
                check_write(jail, value)
            assert write.value.code == "NOT_TEXT"
        with pytest.raises(Refuse) as nul:
            check_outbound("a\x00b")
        assert nul.value.code == "NULL_BYTE"
        with pytest.raises(Refuse) as nul_path:
            check_write(jail, str(grant) + "\x00note")
        assert nul_path.value.code == "NULL_BYTE"


def test_spill_refuses_without_echo() -> None:
    samples = (
        "sk-livekeyvalue",
        "Authorization: Bearer abcdefghijk",
        "api_key=abcdef",
        "token=supersecret",
    )
    for sample in samples:
        assert secret_shape(sample) is True
        with pytest.raises(Refuse) as caught:
            check_outbound(sample)
        assert caught.value.code == "SPILL"
        assert caught.value.detail == ""
        assert sample not in str(caught.value)
        assert sample not in repr(caught.value)
        assert secret_shape(str(caught.value)) is False
        assert redact(sample) != sample
    with _pair() as (grant, _other):
        jail = PathJail([str(grant)])
        secret_path = str(grant / "sk-livekeyvalue")
        with pytest.raises(Refuse) as caught:
            check_write(jail, secret_path)
        assert caught.value.code == "SPILL"
        assert "sk-livekeyvalue" not in str(caught.value)
        assert secret_shape(str(caught.value)) is False
        assert not (grant / "sk-livekeyvalue").exists()


def test_policy_cap_is_recorded_and_not_raised() -> None:
    high = applied_cap(POLICY_CAP + 25)
    assert high.asked_cap == POLICY_CAP + 25
    assert high.cap == POLICY_CAP
    assert high.policy_cap == POLICY_CAP
    assert high.schema == SCHEMA
    assert high == applied_cap(POLICY_CAP + 25)
    assert not hasattr(high, "__dict__")
    assert secret_shape(repr(high)) is False
    low = applied_cap(4)
    assert low.asked_cap == 4
    assert low.cap == 4
    assert low.policy_cap == POLICY_CAP
    default = applied_cap()
    assert default.asked_cap == POLICY_CAP
    assert default.cap == POLICY_CAP
    body = "a" * POLICY_CAP
    assert check_outbound(body, cap=POLICY_CAP + 25) == body
    with pytest.raises(Refuse) as over:
        check_outbound(body + "a", cap=POLICY_CAP + 25)
    assert over.value.code == "OVERSIZE"
    assert over.value.detail == str(POLICY_CAP)
    assert check_outbound("abcd", cap=4) == "abcd"
    with pytest.raises(Refuse) as tight:
        check_outbound("abcde", cap=4)
    assert tight.value.code == "OVERSIZE"
    assert tight.value.detail == "4"
    with _pair() as (grant, _other):
        jail = PathJail([str(grant)])
        long = str(grant / ("n" * POLICY_CAP))
        with pytest.raises(Refuse) as write_over:
            check_write(jail, long, POLICY_CAP + 10)
        assert write_over.value.code == "OVERSIZE"
        assert write_over.value.detail == str(POLICY_CAP)
        target = str(grant / "note.txt")
        assert check_write(jail, target, cap=len(target)) == (grant / "note.txt").resolve()
        with pytest.raises(Refuse) as write_tight:
            check_write(jail, target, cap=4)
        assert write_tight.value.code == "OVERSIZE"
        assert write_tight.value.detail == "4"
        assert list(grant.iterdir()) == []


def test_bad_cap_and_bad_record() -> None:
    for asked in (True, False, 1.5, "9", b"9"):
        with pytest.raises(Refuse) as caught:
            applied_cap(asked)
        assert caught.value.code == "NOT_INT"
        with pytest.raises(Refuse) as outbound:
            check_outbound("hi", cap=asked)
        assert outbound.value.code == "NOT_INT"
    for asked in (0, -1):
        with pytest.raises(Refuse) as caught:
            applied_cap(asked)
        assert caught.value.code == "OUT_OF_RANGE"
        assert caught.value.detail == f"1..{POLICY_CAP}"
    with _pair() as (grant, _other):
        jail = PathJail([str(grant)])
        target = str(grant / "session" / "card.txt")
        for asked in (True, False, 1.5, "9", b"9"):
            with pytest.raises(Refuse) as write:
                check_write(jail, target, cap=asked)
            assert write.value.code == "NOT_INT"
        for asked in (0, -1):
            with pytest.raises(Refuse) as write:
                check_write(jail, target, asked)
            assert write.value.code == "OUT_OF_RANGE"
            assert write.value.detail == f"1..{POLICY_CAP}"
        assert list(grant.iterdir()) == []
    with pytest.raises(Refuse) as schema:
        AppliedCap(asked_cap=4, cap=4, policy_cap=POLICY_CAP, schema="other")
    assert schema.value.code == "BAD_SCHEMA"
    with pytest.raises(Refuse) as limit:
        AppliedCap(asked_cap=4, cap=3, policy_cap=POLICY_CAP, schema=SCHEMA)
    assert limit.value.code == "BAD_LIMIT"
    with pytest.raises(Refuse) as raised:
        AppliedCap(
            asked_cap=POLICY_CAP + 1,
            cap=POLICY_CAP + 1,
            policy_cap=POLICY_CAP,
            schema=SCHEMA,
        )
    assert raised.value.code == "BAD_LIMIT"
    with pytest.raises(Refuse) as policy:
        AppliedCap(asked_cap=4, cap=4, policy_cap=4, schema=SCHEMA)
    assert policy.value.code == "BAD_LIMIT"


def _story() -> tuple[str, str, AppliedCap, tuple[str, ...]]:
    grant = Path(tempfile.mkdtemp(prefix="workspace_guard_"))
    outside: Path | None = None
    try:
        outside = Path(tempfile.mkdtemp(prefix="workspace_guard_out_"))
        jail = PathJail((str(grant),))
        card = grant / "session" / "card.txt"
        contained = check_write(jail, str(card), POLICY_CAP + 25)
        again = check_write(jail, str(card), POLICY_CAP + 25)
        assert again == contained
        assert contained == card.resolve()
        assert grant.resolve() in contained.parents
        assert contained.parent.name == "session"
        assert contained.name == "card.txt"
        assert not contained.exists()
        body = "note under the light for the session card"
        note = check_outbound(body, POLICY_CAP + 25)
        assert note == body
        assert note == redact(body)
        assert note == check_outbound(body)
        recorded = applied_cap(POLICY_CAP + 25)
        codes = (
            _write_code(jail, str(outside / "card.txt")),
            _text_code("sk-livekeyvalue"),
            _write_code(jail, str(grant / "session" / ".." / "card.txt")),
            _write_code(jail, "\\\\server\\share\\session\\card.txt"),
            _write_code(jail, _file_url(card)),
        )
        assert list(grant.iterdir()) == []
        assert list(outside.iterdir()) == []
        assert secret_shape(repr(contained)) is False
        assert secret_shape(repr(recorded)) is False
        assert secret_shape(note) is False
        return ("session/card.txt", note, recorded, codes)
    finally:
        shutil.rmtree(grant, ignore_errors=True)
        if outside is not None:
            shutil.rmtree(outside, ignore_errors=True)


def test_example_workspace_guard() -> None:
    first = _story()
    second = _story()
    assert first == second
    name, note, cap, codes = first
    assert name == "session/card.txt"
    assert note == "note under the light for the session card"
    assert cap.asked_cap == POLICY_CAP + 25
    assert cap.cap == POLICY_CAP
    assert cap.policy_cap == POLICY_CAP
    assert cap.schema == SCHEMA
    assert codes == ("OUTSIDE_GRANT", "SPILL", "DOTDOT", "UNC", "FILE_URL")
    assert secret_shape(repr(cap)) is False
