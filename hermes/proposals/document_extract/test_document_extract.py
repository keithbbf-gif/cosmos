"""Refusal and cap coverage for in-process txt and md extraction."""

from __future__ import annotations

from typing import cast

import pytest

from cosmos_hermes import Refuse
from document_extract import POLICY_CAP, SCHEMA, Extract, extract


def test_schema_and_import_name() -> None:
    assert SCHEMA == "cosmos-hermes-document_extract/1"
    assert POLICY_CAP == 256_000


def test_txt_and_md_return_text() -> None:
    txt = extract("txt", "hello\n".encode())
    md = extract("md", "# Title\n\nbody\n".encode())
    assert isinstance(txt, Extract)
    assert txt.kind == "txt"
    assert txt.text == "hello\n"
    assert txt.cap == POLICY_CAP
    assert md.kind == "md"
    assert md.text == "# Title\n\nbody\n"
    assert md.cap == POLICY_CAP


def test_example_document_extract() -> None:
    brief = (
        "# Session brief\n"
        "\n"
        "Mara opens the north lab and starts the evening session.\n"
        "\n"
        "- Card: the lumen card stays on the hook by the door.\n"
        "- Note: the calibration note sits under the aisle light.\n"
        "- Light: the aisle light stays at dusk until the session ends.\n"
    )
    raw = brief.encode("utf-8")
    first = extract("md", raw, cap=POLICY_CAP * 4)
    second = extract("md", raw, cap=POLICY_CAP * 4)
    assert first == second
    assert repr(first) == repr(second)
    assert first.kind == "md"
    assert first.cap == POLICY_CAP
    assert first.text == brief
    lines = first.text.splitlines()
    assert lines[0] == "# Session brief"
    assert lines[2] == "Mara opens the north lab and starts the evening session."
    listed = [line for line in lines if line.startswith("- ")]
    assert listed == [
        "- Card: the lumen card stays on the hook by the door.",
        "- Note: the calibration note sits under the aisle light.",
        "- Light: the aisle light stays at dusk until the session ends.",
    ]


def test_utf8_and_empty_and_bytearray() -> None:
    assert extract("txt", "東京".encode()).text == "東京"
    assert extract("md", b"").text == ""
    assert extract("txt", bytearray(b"ab")).text == "ab"
    assert extract("txt", b"%PDF-1.4 still text").text == "%PDF-1.4 still text"


def test_zip_magic_under_txt_stays_text() -> None:
    got = extract("txt", b"PK\x03\x04")
    assert got.kind == "txt"
    assert got.text == "PK\x03\x04"


def test_same_input_same_record() -> None:
    assert extract("md", b"same", cap=8) == extract("md", b"same", cap=8)


def test_cap_ignores_a_higher_request() -> None:
    exact = b"z" * POLICY_CAP
    got = extract("txt", exact, cap=POLICY_CAP * 10)
    assert got.cap == POLICY_CAP
    assert got.text == "z" * POLICY_CAP
    with pytest.raises(Refuse) as caught:
        extract("md", exact + b"z", cap=9_999_999)
    assert caught.value.code == "OVERSIZE"
    assert caught.value.detail == str(POLICY_CAP)


def test_lower_cap_is_recorded() -> None:
    got = extract("txt", b"abcd", cap=4)
    assert got.cap == 4
    assert got.text == "abcd"
    one = extract("txt", b"a", cap=1)
    assert one.cap == 1
    assert one.text == "a"
    with pytest.raises(Refuse) as caught:
        extract("txt", b"abcde", cap=4)
    assert caught.value.code == "OVERSIZE"
    assert caught.value.detail == "4"


def test_decode_refuses_invalid_utf8() -> None:
    with pytest.raises(Refuse) as caught:
        extract("txt", b"\xff")
    assert caught.value.code == "DECODE"
    with pytest.raises(Refuse) as caught:
        extract("md", b"# Title\n\n- item\n\xff")
    assert caught.value.code == "DECODE"
    assert caught.value.detail == ""


def test_null_byte_in_decoded_text() -> None:
    with pytest.raises(Refuse) as caught:
        extract("md", b"a\x00b")
    assert caught.value.code == "NULL_BYTE"


def test_kind_null_byte() -> None:
    with pytest.raises(Refuse) as caught:
        extract("md\x00", b"hello")
    assert caught.value.code == "NULL_BYTE"


def test_pdf_and_docx_need_extractor_and_do_not_parse() -> None:
    payload = b"%PDF-1.7\n\xff\x00(not actually parsed)"
    for kind in ("pdf", "docx"):
        with pytest.raises(Refuse) as caught:
            extract(kind, payload, cap=POLICY_CAP * 3)
        assert caught.value.code == "NEED_EXTRACTOR"
        assert caught.value.detail == kind


def test_zip_is_archive_and_is_not_unpacked() -> None:
    with pytest.raises(Refuse) as caught:
        extract("zip", b"PK\x03\x04\xff\x00hello")
    assert caught.value.code == "ARCHIVE"
    assert caught.value.detail == "zip"


def test_other_kinds_are_bad() -> None:
    for kind in ("", "TXT", "MD", "markdown", "xlsx", "ipynb", "doc", "PDF", "zip ", "sqlite"):
        with pytest.raises(Refuse) as caught:
            extract(kind, b"hello")
        assert caught.value.code == "BAD_KIND"
        assert caught.value.detail == ""


def test_kind_not_text_and_data_not_bytes() -> None:
    with pytest.raises(Refuse) as caught:
        extract(cast(str, 12), b"hello")
    assert caught.value.code == "NOT_TEXT"
    with pytest.raises(Refuse) as caught:
        extract("txt", cast(bytes, "hello"))
    assert caught.value.code == "NOT_BYTES"
    with pytest.raises(Refuse) as caught:
        extract("txt", cast(bytes, memoryview(b"ab")))
    assert caught.value.code == "NOT_BYTES"


def test_bad_cap() -> None:
    with pytest.raises(Refuse) as caught:
        extract("txt", b"a", cap=cast(int, "256"))
    assert caught.value.code == "BAD_LIMIT"
    with pytest.raises(Refuse) as caught:
        extract("txt", b"a", cap=cast(int, 1.5))
    assert caught.value.code == "BAD_LIMIT"
    with pytest.raises(Refuse) as caught:
        extract("txt", b"a", cap=True)
    assert caught.value.code == "BAD_LIMIT"
    with pytest.raises(Refuse) as caught:
        extract("txt", b"a", cap=0)
    assert caught.value.code == "OUT_OF_RANGE"
    with pytest.raises(Refuse) as caught:
        extract("txt", b"a", cap=-3)
    assert caught.value.code == "OUT_OF_RANGE"


def test_record_refuses_malformed_fields() -> None:
    with pytest.raises(Refuse) as caught:
        Extract(kind="pdf", text="hello", cap=POLICY_CAP)
    assert caught.value.code == "NEED_EXTRACTOR"
    with pytest.raises(Refuse) as caught:
        Extract(kind="docx", text="hello", cap=4)
    assert caught.value.code == "NEED_EXTRACTOR"
    with pytest.raises(Refuse) as caught:
        Extract(kind="zip", text="PK", cap=4)
    assert caught.value.code == "ARCHIVE"
    with pytest.raises(Refuse) as caught:
        Extract(kind="xlsx", text="a", cap=4)
    assert caught.value.code == "BAD_KIND"
    with pytest.raises(Refuse) as caught:
        Extract(kind="txt", text="ab\x00", cap=8)
    assert caught.value.code == "NULL_BYTE"
    with pytest.raises(Refuse) as caught:
        Extract(kind="txt", text="abcd", cap=2)
    assert caught.value.code == "OVERSIZE"
    with pytest.raises(Refuse) as caught:
        Extract(kind="txt", text="a", cap=POLICY_CAP * 3)
    assert caught.value.code == "BAD_LIMIT"
    with pytest.raises(Refuse) as caught:
        Extract(kind="txt", text="a", cap=cast(int, True))
    assert caught.value.code == "BAD_LIMIT"
    with pytest.raises(Refuse) as caught:
        Extract(kind=cast(str, None), text="a", cap=4)
    assert caught.value.code == "NOT_TEXT"


def test_repr_hides_secret_shapes() -> None:
    samples = (
        b"sk-livekeyvalue in a note",
        b"Authorization: Bearer abcdefghijk",
        b"api_key=supersecret",
    )
    hidden = f"Extract(kind='txt', cap={POLICY_CAP}, text='[redacted]')"
    for raw in samples:
        got = extract("txt", raw)
        shown = repr(got)
        assert shown == hidden
        assert "livekeyvalue" not in shown
        assert "abcdefghijk" not in shown
        assert "supersecret" not in shown
        assert got.text == raw.decode("utf-8")
    late = b"visible-prefix " + (b"n" * 40) + b" sk-livekeyvalue"
    late_shown = repr(extract("txt", late))
    assert late_shown == hidden
    assert "visible-prefix" not in late_shown
    plain = extract("md", b"plain note")
    assert repr(plain) == f"Extract(kind='md', cap={POLICY_CAP}, text='plain note')"
    long_plain = extract("txt", b"n" * 100)
    long_shown = repr(long_plain)
    assert "n" * 80 in long_shown
    assert "n" * 81 not in long_shown
