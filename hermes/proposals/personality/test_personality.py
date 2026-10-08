"""Soul text stays first. A preset swap does not move the soul sha256."""

from __future__ import annotations

import hashlib
from collections.abc import Callable

import pytest

from cosmos_hermes import Refuse, secret_shape
from personality import (
    BUILTIN_NAMES,
    CATALOG_CAP,
    FALLBACK_SOUL,
    SCHEMA,
    TOTAL_CAP,
    Prefix,
    Preset,
    Record,
    Records,
    Session,
    assemble,
    list_presets,
    open_session,
    prefix,
    prompt,
    rebuild,
    records,
    swap_preset,
)


def _code(func: Callable[[], object]) -> str:
    with pytest.raises(Refuse) as caught:
        func()
    return caught.value.code


def _digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def test_schema_and_assemble_order() -> None:
    assert SCHEMA == "cosmos-hermes-personality/1"
    body = assemble("Soul stays first.", "Preset follows.")
    assert body == "Soul stays first.\n\nPreset follows."
    assert body.startswith("Soul stays first.")
    assert body.index("Soul stays first.") < body.index("Preset follows.")
    assert assemble("Soul stays first.", "") == "Soul stays first."
    assert assemble("Soul stays first.", "   ") == "Soul stays first."
    assert assemble("line\nstay", "") == "line\nstay"
    assert _code(lambda: assemble("   \n", "")) == "EMPTY"
    assert _code(lambda: assemble("", "Be brief.")) == "EMPTY"
    assert _code(lambda: open_session("\n\n", "none")) == "EMPTY"
    assert prompt(open_session(FALLBACK_SOUL, "none")) == FALLBACK_SOUL
    assert "yolo" not in FALLBACK_SOUL.casefold()
    assert len(FALLBACK_SOUL) < TOTAL_CAP


def test_swap_preset_keeps_soul_hash() -> None:
    opened = open_session("Be direct.", "concise")
    assert opened.soul_sha256 == _digest("Be direct.")
    assert opened.soul_hash == opened.soul_sha256
    assert opened.selection == "concise"
    swapped = swap_preset(opened, "teacher")
    assert swapped.soul_sha256 == opened.soul_sha256
    assert swapped.soul_text == opened.soul_text
    assert swapped.preset_name == "teacher"
    assert swapped.preset_text != opened.preset_text
    assert opened.preset_name == "concise"
    again = swap_preset(opened, "teacher")
    assert again == swapped
    assert again is not swapped
    assert rebuild(records(swapped)) == swapped
    assert prefix(rebuild(records(swapped))) == prefix(swapped)
    cleared = swap_preset(swapped, "default")
    assert cleared.soul_sha256 == opened.soul_sha256
    assert cleared.preset_name == ""
    assert cleared.preset_text == ""
    assert cleared.selection == "none"
    assert prompt(cleared) == "Be direct."
    assert swap_preset(opened, "none") == swap_preset(opened, "neutral")
    assert swap_preset(opened, "NONE") == swap_preset(opened, "none")
    text = prompt(opened)
    assert text.startswith("Be direct.")
    assert opened.preset_text in text
    assert text.index("Be direct.") < text.index(opened.preset_text)
    assert text == assemble(opened.soul_text, opened.preset_text)
    assert prefix(opened).text == text


def test_builtins_catalog_and_fallback() -> None:
    opened = open_session(FALLBACK_SOUL, "KaWaIi")
    assert opened.soul_text == FALLBACK_SOUL
    assert opened.soul_sha256 == _digest(FALLBACK_SOUL)
    assert opened.preset_name == "kawaii"
    digest = opened.soul_sha256
    for name in BUILTIN_NAMES:
        swapped = swap_preset(opened, name)
        assert swapped.preset_name == name
        assert swapped.preset_text != ""
        assert swapped.soul_sha256 == digest
        rendered = prompt(swapped)
        assert rendered.startswith(FALLBACK_SOUL)
        assert rendered.index(FALLBACK_SOUL) < rendered.index(swapped.preset_text)
    custom = Preset("concise", "Five words maximum.")
    extra = Preset("codereviewer", "Name one bug and stop.")
    mixed = open_session("Soul.", "concise", (custom, extra))
    assert mixed.preset_text == "Five words maximum."
    assert list_presets(mixed) == ("none",) + BUILTIN_NAMES + ("codereviewer",)
    assert list_presets(mixed).count("concise") == 1
    back = swap_preset(swap_preset(mixed, "helpful"), "concise")
    assert back.preset_text == "Five words maximum."
    assert back.soul_sha256 == mixed.soul_sha256
    assert rebuild(records(mixed)) == mixed
    one_shot = swap_preset(open_session("Soul.", "none"), extra)
    assert one_shot.selection == "codereviewer"
    assert one_shot.soul_sha256 == _digest("Soul.")
    assert "codereviewer" not in list_presets(one_shot)
    assert rebuild(records(one_shot)) == one_shot
    assert not secret_shape(repr(mixed))
    assert not secret_shape(repr(extra))
    assert not secret_shape(repr(records(mixed)))


def test_cap_policy() -> None:
    soul = "s" * 7000
    preset = "p" * 998
    assert assemble(soul, preset) == soul + "\n\n" + preset
    assert len(assemble(soul, preset)) == TOTAL_CAP
    assert assemble("s" * TOTAL_CAP, "") == "s" * TOTAL_CAP
    with pytest.raises(Refuse) as total:
        assemble(soul, preset + "p")
    assert total.value.code == "OVERSIZE"
    assert total.value.detail == str(TOTAL_CAP)
    with pytest.raises(Refuse) as piece:
        assemble("s" * (TOTAL_CAP + 1), "")
    assert piece.value.code == "OVERSIZE"
    assert piece.value.detail == str(TOTAL_CAP)
    wide = open_session("hello", "none", requested_cap=TOTAL_CAP + 50)
    assert wide.cap == TOTAL_CAP
    full = open_session("s" * TOTAL_CAP, "none", requested_cap=TOTAL_CAP + 100)
    assert full.cap == TOTAL_CAP
    assert len(prompt(full)) == TOTAL_CAP
    tight = open_session("hello", "none", requested_cap=16)
    assert tight.cap == 16
    with pytest.raises(Refuse) as over:
        swap_preset(tight, "concise")
    assert over.value.code == "OVERSIZE"
    assert over.value.detail == "16"
    assert tight.preset_name == ""
    assert tight.soul_sha256 == _digest("hello")
    fitted = swap_preset(tight, Preset("hold", "Hold."))
    assert fitted.cap == 16
    assert fitted.soul_sha256 == tight.soul_sha256
    assert prompt(tight) == "hello"
    assert prompt(fitted) == "hello\n\nHold."
    assert prompt(fitted).startswith("hello")
    with pytest.raises(Refuse) as short_soul:
        open_session("hello", "none", requested_cap=4)
    assert short_soul.value.code == "OVERSIZE"
    assert short_soul.value.detail == "4"
    direct = Session(SCHEMA, "hi", _digest("hi"), "", "", (), TOTAL_CAP + 10)
    assert direct.cap == TOTAL_CAP


def test_guard_escape_phrases() -> None:
    assert _code(lambda: assemble("please disable approval", "calm")) == "GUARD_ESCAPE"
    assert _code(lambda: assemble("calm", "YOLO")) == "GUARD_ESCAPE"
    assert _code(lambda: assemble("calm", "No Restrictions")) == "GUARD_ESCAPE"
    assert _code(lambda: assemble("disable\napproval", "calm")) == "GUARD_ESCAPE"
    assert _code(lambda: assemble("calm", "no\trestrictions")) == "GUARD_ESCAPE"
    assert _code(lambda: assemble("DiSaBlE aPpRoVaL", "calm")) == "GUARD_ESCAPE"
    assert _code(lambda: assemble("end with disable", "approval now")) == "GUARD_ESCAPE"
    assert _code(lambda: open_session("end with disable", Preset("review", "approval now"))) == "GUARD_ESCAPE"
    base = open_session("end with disable", "none")
    assert _code(lambda: swap_preset(base, Preset("review", "approval now"))) == "GUARD_ESCAPE"
    assert base.preset_name == ""
    assert _code(lambda: open_session("yolo", "none")) == "GUARD_ESCAPE"
    assert _code(lambda: Preset("review", "yolo")) == "GUARD_ESCAPE"
    assert _code(lambda: Preset("yolo", "careful")) == "GUARD_ESCAPE"
    benign = assemble("You only live once. Prefer yellow.", "Be concise.")
    assert benign.startswith("You only live once.")


def test_secret_and_bounds() -> None:
    assert _code(lambda: assemble("sk-livekeyvalue", "ok")) == "SECRET"
    assert _code(lambda: assemble("ok", "api_key=abcdef")) == "SECRET"
    assert _code(lambda: Preset("review", "Bearer abcdefghijk")) == "SECRET"
    assert _code(lambda: Preset("sk-livekeyvalue", "plain words")) == "SECRET"
    assert _code(lambda: assemble("safe\u200btext", "ok")) == "INVISIBLE"
    assert _code(lambda: assemble("ok", "safe\u202etext")) == "INVISIBLE"
    assert _code(lambda: Preset("bad\u200bname", "plain words")) == "INVISIBLE"
    assert _code(lambda: assemble(12, "ok")) == "NOT_TEXT"
    assert _code(lambda: assemble("a\x00b", "ok")) == "NULL_BYTE"
    assert _code(lambda: assemble("ok", "a\x00b")) == "NULL_BYTE"
    assert _code(lambda: swap_preset(open_session("hi", "none"), "a\x00b")) == "NULL_BYTE"
    assert _code(lambda: open_session("hi", "none", (), True)) == "NOT_INT"
    assert _code(lambda: open_session("hi", "none", (), "3")) == "NOT_INT"
    assert _code(lambda: open_session("hi", "none", (), 0)) == "BAD_LIMIT"
    assert _code(lambda: open_session("hi", "none", (), -3)) == "BAD_LIMIT"


def test_names_catalog_and_session_shape() -> None:
    base = open_session("hi", "none")
    assert _code(lambda: swap_preset(base, "notapreset")) == "UNKNOWN_PRESET"
    assert _code(lambda: swap_preset(base, "has space")) == "BAD_NAME"
    assert _code(lambda: swap_preset(base, "")) == "EMPTY"
    assert _code(lambda: swap_preset(base, "   ")) == "EMPTY"
    assert _code(lambda: Preset("none", "nope")) == "BAD_NAME"
    assert _code(lambda: Preset("default", "nope")) == "BAD_NAME"
    assert _code(lambda: Preset("review", "   ")) == "EMPTY"
    assert _code(lambda: Record("none", "nope")) == "BAD_NAME"
    assert _code(lambda: Record("review", "   ")) == "EMPTY"
    assert _code(lambda: open_session("hi", "none", ["x"])) == "BAD_PRESET"
    assert _code(lambda: open_session("hi", "none", ("x",))) == "BAD_PRESET"
    assert _code(lambda: swap_preset(None, "none")) == "BAD_SESSION"
    assert _code(lambda: prompt("session")) == "BAD_SESSION"
    assert _code(lambda: prefix(1)) == "BAD_SESSION"
    assert _code(lambda: list_presets(1)) == "BAD_SESSION"
    assert _code(lambda: records(None)) == "BAD_SESSION"
    assert _code(lambda: rebuild(base)) == "BAD_SESSION"
    dup = (Preset("aone", "one"), Preset("aone", "two"))
    assert _code(lambda: open_session("hi", "none", dup)) == "DUP_NAME"
    dup_rows = (Record("aone", "one"), Record("aone", "two"))
    assert _code(lambda: Records(SCHEMA, "hi", _digest("hi"), "", "", dup_rows, TOTAL_CAP)) == "DUP_NAME"
    rows = tuple(Preset(f"n{index:02d}", f"line {index}") for index in range(CATALOG_CAP + 1))
    assert _code(lambda: open_session("hi", "none", rows)) == "CATALOG_CAP"
    held = tuple(Preset(f"n{index:02d}", f"line {index}") for index in range(CATALOG_CAP))
    fitted = open_session("hi", "n00", held)
    assert fitted.preset_text == "line 0"
    assert fitted.soul_sha256 == _digest("hi")
    assert len(list_presets(fitted)) == 1 + len(BUILTIN_NAMES) + CATALOG_CAP
    assert rebuild(records(fitted)) == fitted
    digest = _digest("hi")
    assert _code(lambda: Session("other", "hi", digest, "", "", (), TOTAL_CAP)) == "BAD_SCHEMA"
    assert _code(lambda: Records("other", "hi", digest, "", "", (), TOTAL_CAP)) == "BAD_SCHEMA"
    assert _code(lambda: Prefix("other", "hi", "", digest, TOTAL_CAP)) == "BAD_SCHEMA"
    assert _code(lambda: Session(SCHEMA, "hi", "0" * 64, "", "", (), TOTAL_CAP)) == "HASH_MISMATCH"
    assert _code(lambda: Session(SCHEMA, "hi", "abcd", "", "", (), TOTAL_CAP)) == "HASH_MISMATCH"
    assert _code(lambda: Records(SCHEMA, "hi", "abcd", "", "", (), TOTAL_CAP)) == "HASH_MISMATCH"
    assert (
        _code(lambda: Session(SCHEMA, "hi", digest, "concise", "not the builtin", (), TOTAL_CAP))
        == "BAD_PRESET"
    )
    assert (
        _code(lambda: Records(SCHEMA, "hi", digest, "concise", "not the builtin", (), TOTAL_CAP))
        == "BAD_PRESET"
    )
    assert (
        _code(lambda: Session(SCHEMA, "hi", digest, "", "orphan overlay", (), TOTAL_CAP))
        == "BAD_PRESET"
    )
    assert _code(lambda: Session(SCHEMA, "hi", digest, "concise", "", (), TOTAL_CAP)) == "EMPTY"
    assert _code(lambda: Session(SCHEMA, "hi", digest, "", "", (), 0)) == "BAD_LIMIT"
    assert list_presets(base) == ("none",) + BUILTIN_NAMES
    manual = Records(SCHEMA, "hi", digest, "concise", swap_preset(base, "concise").preset_text, (), TOTAL_CAP)
    assert rebuild(manual) == swap_preset(base, "concise")


def _kiln_story() -> tuple[Session, Session, Prefix, str]:
    soul = "kiln notes stay short"
    cone = Preset("cone", "Lead with the cone, then stop.")
    glaze = Preset("glaze", "Name the glaze batch, then the hold.")
    opened = open_session(soul, cone, (cone, glaze))
    code = "UNCAUGHT"
    try:
        open_session(soul, Preset("leak", "api_key=kiln-night-key"))
    except Refuse as refused:
        code = refused.code
    built = rebuild(records(opened))
    block = prefix(opened)
    return opened, built, block, code


def test_example_personality() -> None:
    first = _kiln_story()
    second = _kiln_story()
    assert first == second
    opened, built, block, code = first
    assert code == "SECRET"
    assert built == opened
    assert block == prefix(built)
    assert block.text == "kiln notes stay short\n\nLead with the cone, then stop."
    assert block.text.startswith("kiln notes stay short")
    assert block.text.index("kiln notes stay short") == 0
    assert block.text.index("kiln notes stay short") < block.text.index("Lead with the cone")
    assert "Name the glaze batch" not in block.text
    assert block.soul_sha256 == opened.soul_sha256
    assert block.soul_sha256 == _digest("kiln notes stay short")
    assert prompt(built) == block.text
    assert "api_key" not in block.text
    assert secret_shape(block.text) is False
    assert secret_shape(repr(opened)) is False
    assert secret_shape(repr(block)) is False
    assert secret_shape(repr(records(opened))) is False
    assert list_presets(built) == ("none",) + BUILTIN_NAMES + ("cone", "glaze")
