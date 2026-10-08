"""Kernel refusals used by every proposal."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from cosmos_hermes import (
    PathJail,
    Refuse,
    bound_bytes,
    bound_int,
    bound_text,
    const_eq,
    redact,
    secret_shape,
)


def test_bounds_accept_and_refuse() -> None:
    assert bound_text("ok", 4) == "ok"
    assert bound_bytes(b"ab", 2) == b"ab"
    assert bound_int(3, 1, 5) == 3
    with pytest.raises(Refuse) as over:
        bound_text("abcdef", 4)
    assert over.value.code == "OVERSIZE"
    with pytest.raises(Refuse) as nul:
        bound_text("a\x00b", 8)
    assert nul.value.code == "NULL_BYTE"
    with pytest.raises(Refuse) as flag:
        bound_int(True, 0, 1)
    assert flag.value.code == "NOT_INT"


def test_const_eq_and_redact() -> None:
    assert const_eq("same", "same")
    assert not const_eq("same", "same ")
    assert secret_shape("sk-livekeyvalue")
    assert secret_shape("Authorization: Bearer abcdefghijk")
    scrubbed = redact("token=supersecret sk-livekeyvalue")
    assert "supersecret" not in scrubbed
    assert "sk-livekeyvalue" not in scrubbed
    assert not secret_shape(scrubbed)


def test_jail_contains_and_refuses() -> None:
    # A private directory: the shared pytest basetemp on this machine is not writable.
    root = Path(tempfile.mkdtemp(prefix="hermes-jail-"))
    grant = root / "attempt"
    grant.mkdir()
    inside = grant / "note.txt"
    inside.write_text("x", encoding="utf-8")
    jail = PathJail([str(grant)])
    assert jail.contain(str(inside)) == inside.resolve()
    escapes = [
        str(grant) + "\\..\\outside.txt",
        str(grant) + "%2e%2e",
        "file:///etc/passwd",
        "C:foo",
        "C:\\",
        "\\\\server\\share\\x",
        str(grant / "note.txt:stream"),
        str(root / "other" / "x"),
    ]
    codes: list[str] = []
    for raw in escapes:
        with pytest.raises(Refuse) as caught:
            jail.contain(raw)
        codes.append(caught.value.code)
    assert "DOTDOT" in codes
    assert "OUTSIDE_GRANT" in codes
    assert "FILE_URL" in codes
    with pytest.raises(Refuse) as empty:
        PathJail([])
    assert empty.value.code == "NO_GRANT"
