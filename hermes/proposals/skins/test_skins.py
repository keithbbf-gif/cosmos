"""Terminal-safe skins: strip controls, cap fields, refuse an empty banner."""

from __future__ import annotations

from pathlib import Path
from typing import cast

import pytest

from cosmos_hermes import Refuse, secret_shape
from skins import (
    CUSTOM_CAP,
    FIELD_CAP,
    SCHEMA,
    Catalog,
    Hold,
    Pick,
    Skin,
    Snapshot,
    Status,
    builtin_skins,
    catalog,
    define,
    hold,
    pick,
    rebuild,
    render,
    snapshot,
)

_CONTROLS = (
    "\x1b",
    "\u202a",
    "\u202b",
    "\u202c",
    "\u202d",
    "\u202e",
    "\u2066",
    "\u2067",
    "\u2068",
    "\u2069",
)
_BUILTIN_NAMES = (
    "default",
    "ares",
    "mono",
    "slate",
    "daylight",
    "warm-lightmode",
    "poseidon",
    "sisyphus",
    "charizard",
)


def test_schema_and_builtin_success() -> None:
    assert SCHEMA == "cosmos-hermes-skins/1"
    rows = builtin_skins()
    assert tuple(row.name for row in rows) == _BUILTIN_NAMES
    listed = catalog()
    assert isinstance(listed, Catalog)
    assert listed.schema == SCHEMA
    assert listed.cap == FIELD_CAP
    assert listed.names == _BUILTIN_NAMES
    for row in rows:
        assert row.schema == SCHEMA
        assert row.cap == FIELD_CAP
        assert row.banner != ""
        for field in (row.name, row.banner, row.spinner, row.label, row.prefix):
            assert len(field) <= FIELD_CAP
            assert all(char not in field for char in _CONTROLS)
            assert secret_shape(field) is False
        chosen = pick(row.name)
        assert isinstance(chosen, Pick)
        assert chosen.origin == "builtin"
        assert chosen.schema == SCHEMA
        assert chosen.banner == row.banner
        assert chosen.spinner == row.spinner
        assert chosen.label == row.label
        assert chosen.prefix == row.prefix
        assert chosen.cap == FIELD_CAP
        kept = hold(row.name)
        assert isinstance(kept, Hold)
        assert kept.schema == SCHEMA
        assert kept.name == row.name
        assert kept.cap == FIELD_CAP
        assert kept.note == "Set display.skin by hand. This call writes nothing."
        assert secret_shape(repr(row)) is False
        assert secret_shape(repr(chosen)) is False


def test_define_strips_controls_and_keeps_the_rest() -> None:
    banner = "Gold\x1b[31m\u202e!"
    made = define("mine", banner, "sp\x1bin", "la\u202ebel", "pre\u2066fix")
    assert made.banner == "Gold[31m!"
    assert made.spinner == "spin"
    assert made.label == "label"
    assert made.prefix == "prefix"
    assert made.cap == FIELD_CAP
    again = define(made.name, made.banner, made.spinner, made.label, made.prefix, made.cap)
    assert again == made
    direct = Skin("mine", "A\x1bB", "s\u202e", "l\u2066", "p\u202a")
    assert direct.banner == "AB"
    assert direct.spinner == "s"
    assert direct.label == "l"
    assert direct.prefix == "p"
    for control in _CONTROLS:
        cleaned = define("mine", f"A{control}B", f"s{control}", f"l{control}", f"p{control}")
        assert cleaned.banner == "AB"
        assert cleaned.spinner == "s"
        assert cleaned.label == "l"
        assert cleaned.prefix == "p"
        assert control not in repr(cleaned)


def test_empty_banner_is_bad_skin_after_strip() -> None:
    for banner in (
        "",
        "\x1b",
        "\u202e\u2066",
        "\x1b\u202a\u202b\u202c\u202d\u202e\u2066\u2067\u2068\u2069",
        "\n\r\t\u007f\u009b\u2028",
    ):
        with pytest.raises(Refuse) as caught:
            define("mine", banner, "spin", "label", "|")
        assert caught.value.code == "BAD_SKIN"
    blank = define("mine", "  x  ", "", "", "")
    assert blank.banner == "  x  "
    assert blank.spinner == ""
    assert blank.label == ""
    assert blank.prefix == ""


def test_cap_is_80_and_a_higher_request_is_ignored() -> None:
    made = define("mine", "b" * FIELD_CAP, "s" * FIELD_CAP, "l" * FIELD_CAP, "p" * FIELD_CAP, cap=10_000)
    assert made.cap == FIELD_CAP
    assert made.banner == "b" * FIELD_CAP
    direct = Skin("mine", "banner", "s", "l", "p", cap=FIELD_CAP + 50)
    assert direct.cap == FIELD_CAP
    for slot in ("banner", "spinner", "label", "prefix"):
        values: dict[str, object] = {
            "name": "mine",
            "banner": "banner",
            "spinner": "spin",
            "label": "label",
            "prefix": "|",
            "cap": 10_000,
        }
        values[slot] = "q" * (FIELD_CAP + 1)
        with pytest.raises(Refuse) as over:
            define(values["name"], values["banner"], values["spinner"], values["label"], values["prefix"], values["cap"])
        assert over.value.code == "OVERSIZE"
        assert over.value.detail == "80"
    within = define("ab", "b" * 4, "s" * 4, "l" * 4, "p" * 4, cap=4)
    assert within.cap == 4
    with pytest.raises(Refuse) as tight:
        define("ab", "b" * 5, "s", "l", "p", cap=4)
    assert tight.value.code == "OVERSIZE"
    assert tight.value.detail == "4"
    edged = "\x1b" + ("a" * (FIELD_CAP - 1))
    assert len(edged) == FIELD_CAP
    assert define("mine", edged, "s", "l", "p").banner == "a" * (FIELD_CAP - 1)
    with pytest.raises(Refuse) as sneaky:
        define("mine", "\x1b" + ("a" * FIELD_CAP), "s", "l", "p")
    assert sneaky.value.code == "OVERSIZE"


def test_custom_overrides_builtin_and_catalog_appends() -> None:
    custom = (
        define("mono", "Custom Mono", "spin", "Lab", ">"),
        define("zeta", "Zed", "spin", "Lab", ">"),
        define("alpha", "Aye", "spin", "Lab", ">"),
    )
    names = catalog(custom).names
    assert names[: len(_BUILTIN_NAMES)] == _BUILTIN_NAMES
    assert names.count("mono") == 1
    assert names[-2:] == ("zeta", "alpha")
    chosen = pick("mono", custom)
    assert chosen.origin == "custom"
    assert chosen.banner == "Custom Mono"
    assert chosen.cap == FIELD_CAP
    assert pick("mono").origin == "builtin"
    assert pick("zeta", custom).banner == "Zed"
    low = define("mytheme", "Hi", "s", "l", "p", cap=8)
    assert pick("mytheme", (low,)).cap == 8
    kept = hold("mytheme", (low,))
    assert kept.name == "mytheme"
    assert kept.cap == 8
    assert "writes nothing" in kept.note
    high = define("mytheme", "Hi", "s", "l", "p", cap=800)
    assert hold("mytheme", (high,)).cap == FIELD_CAP


def test_names_and_unknown() -> None:
    for name in ("", "-", "warm-", "-warm", "warm--light", "Ares", "has space", "slash/name", "dot.name", "bad\u202ename"):
        with pytest.raises(Refuse) as bad:
            define(name, "banner", "s", "l", "p")
        assert bad.value.code == "BAD_NAME"
    with pytest.raises(Refuse) as unknown:
        pick("nope")
    assert unknown.value.code == "UNKNOWN"
    with pytest.raises(Refuse) as held:
        hold("defaults")
    assert held.value.code == "UNKNOWN"
    with pytest.raises(Refuse) as shaped:
        define("ar\x1bes", "banner", "s", "l", "p")
    assert shaped.value.code == "BAD_NAME"


def test_secrets_are_refused_and_absent_from_repr() -> None:
    secret = "sk-livekeyvalue"
    hidden = "sk-\u202eabcdefghij"
    assert secret_shape(hidden) is False
    for banner in (secret, hidden, "see Bearer abcdefghij", "token=supersecret"):
        with pytest.raises(Refuse) as caught:
            define("mine", banner, "s", "l", "p")
        assert caught.value.code == "SECRET"
        assert secret not in str(caught.value)
        assert "supersecret" not in str(caught.value)
    for slot in ("spinner", "label", "prefix"):
        values: dict[str, object] = {
            "name": "mine",
            "banner": "banner",
            "spinner": "spin",
            "label": "label",
            "prefix": "|",
        }
        values[slot] = secret
        with pytest.raises(Refuse) as caught:
            define(values["name"], values["banner"], values["spinner"], values["label"], values["prefix"])
        assert caught.value.code == "SECRET"
    with pytest.raises(Refuse) as named:
        define(secret, "banner", "s", "l", "p")
    assert named.value.code == "SECRET"
    with pytest.raises(Refuse) as buried:
        define(hidden, "banner", "s", "l", "p")
    assert buried.value.code == "SECRET"
    made = define("mine", "Hello", "spin", "Lab", "|")
    blob = repr(made) + repr(pick("mine", (made,))) + repr(hold("mine", (made,)))
    assert "Hello" in repr(made)
    assert secret_shape(blob) is False
    assert secret not in blob


def test_custom_collection_and_record_codes() -> None:
    with pytest.raises(Refuse) as text:
        catalog("default")
    assert text.value.code == "BAD_SKIN"
    with pytest.raises(Refuse) as empty:
        pick("default", None)
    assert empty.value.code == "BAD_SKIN"
    with pytest.raises(Refuse) as item:
        catalog([object()])
    assert item.value.code == "BAD_SKIN"
    twin = define("mytheme", "One", "s", "l", "p")
    other = define("mytheme", "Two", "s", "l", "p")
    with pytest.raises(Refuse) as dup:
        pick("mytheme", (twin, other))
    assert dup.value.code == "DUPLICATE"
    rows = tuple(define(f"n{index}", "banner", "sp", "lb", "px") for index in range(CUSTOM_CAP))
    listed = catalog(rows)
    assert listed.cap == FIELD_CAP
    assert listed.names[-CUSTOM_CAP:] == tuple(row.name for row in rows)
    with pytest.raises(Refuse) as over:
        catalog(rows + (define("overflow", "banner", "sp", "lb", "px"),))
    assert over.value.code == "OVER_COUNT"
    with pytest.raises(Refuse) as over_snap:
        snapshot(rows + (define("overflow", "banner", "sp", "lb", "px"),))
    assert over_snap.value.code == "OVER_COUNT"
    with pytest.raises(Refuse) as flag:
        define("mine", "banner", "s", "l", "p", cap=True)
    assert flag.value.code == "NOT_INT"
    with pytest.raises(Refuse) as word:
        define("mine", "banner", "s", "l", "p", cap="80")
    assert word.value.code == "NOT_INT"
    with pytest.raises(Refuse) as zero:
        define("mine", "banner", "s", "l", "p", cap=0)
    assert zero.value.code == "BAD_LIMIT"
    with pytest.raises(Refuse) as direct_flag:
        Skin("mine", "banner", "s", "l", "p", cap=cast(int, True))
    assert direct_flag.value.code == "NOT_INT"
    with pytest.raises(Refuse) as schema:
        Skin("mine", "banner", "s", "l", "p", FIELD_CAP, "other")
    assert schema.value.code == "BAD_SCHEMA"
    with pytest.raises(Refuse) as origin:
        Pick(SCHEMA, "default", "Hermes Agent", "(._.)", "Hermes", "|", FIELD_CAP, "file")
    assert origin.value.code == "BAD_ORIGIN"
    with pytest.raises(Refuse) as bad_schema:
        Pick("nope", "default", "Hermes Agent", "(._.)", "Hermes", "|", FIELD_CAP, "builtin")
    assert bad_schema.value.code == "BAD_SCHEMA"
    with pytest.raises(Refuse) as not_text:
        define(cast(object, 3), "banner", "s", "l", "p")
    assert not_text.value.code == "NOT_TEXT"
    with pytest.raises(Refuse) as nul:
        define("mine", "bad\x00", "s", "l", "p")
    assert nul.value.code == "NULL_BYTE"
    for slot in ("banner", "spinner", "label", "prefix"):
        values: dict[str, object] = {
            "name": "mine",
            "banner": "banner",
            "spinner": "spin",
            "label": "label",
            "prefix": "|",
        }
        values[slot] = "bad\x00"
        with pytest.raises(Refuse) as nul_field:
            define(values["name"], values["banner"], values["spinner"], values["label"], values["prefix"])
        assert nul_field.value.code == "NULL_BYTE"
        values[slot] = 3
        with pytest.raises(Refuse) as typed:
            define(values["name"], values["banner"], values["spinner"], values["label"], values["prefix"])
        assert typed.value.code == "NOT_TEXT"


def _ansi_banner() -> str:
    return "Ember" + "\x1b" + chr(0x5B) + "31m"


def _plain_banner() -> str:
    return "Ember" + chr(0x5B) + "31m"


def _evening() -> tuple[Status, Catalog]:
    ember = define("ember", _ansi_banner(), "glow", "ember", "|")
    custom = (ember,)
    listed = rebuild(snapshot(custom))
    shown = render(
        "ember",
        "north-lamp",
        "lumen card",
        "dusk note",
        "aisle light",
        custom=custom,
        policy="plain",
        cap=FIELD_CAP * 4,
    )
    return shown, listed


def test_example_skins() -> None:
    """Mara's north-lamp session keeps the lumen card, the dusk note, and the aisle light on one plain line."""
    first_status, first_catalog = _evening()
    second_status, second_catalog = _evening()
    assert first_status == second_status
    assert first_catalog == second_catalog
    assert repr(first_status) == repr(second_status)
    assert secret_shape(repr(first_status)) is False
    assert first_status.policy == "plain"
    assert first_status.cap == FIELD_CAP
    assert first_status.name == "ember"
    assert first_status.skipped == ()
    assert "\x1b" not in first_status.line
    assert "\u009b" not in first_status.line
    assert first_status.line == "|".join(
        (
            "ember",
            _plain_banner(),
            "glow",
            "north-lamp",
            "lumen card",
            "dusk note",
            "aisle light",
        )
    )
    assert "ember" in first_catalog.names
    with pytest.raises(Refuse) as unknown:
        render(
            "cinder",
            "north-lamp",
            "lumen card",
            "dusk note",
            "aisle light",
            policy="plain",
        )
    assert unknown.value.code == "UNKNOWN"


def test_wider_controls_are_stripped_from_the_status_line() -> None:
    made = define("mine", "A\u009b[31m\nB\r\t\u007f\u2028C", "sp\n", "la\t", "pre\u007f")
    assert made.banner == "A[31mBC"
    assert made.spinner == "sp"
    assert made.label == "la"
    assert made.prefix == "pre"
    shown = render(
        "default",
        "north\x1b[2Jlamp",
        "card",
        "note",
        "lite",
        policy="plain",
    )
    assert "\x1b" not in shown.line
    assert "\u009b" not in shown.line
    assert "north[2Jlamp" in shown.line
    assert shown.policy == "plain"


def test_plain_line_skips_segments_that_do_not_fit() -> None:
    wide = define("ember", "123456789", "", "ember", "|")
    shown = render(
        "ember",
        "north-lamp",
        "ab",
        "n",
        "lamp",
        custom=(wide,),
        policy="plain",
        cap=10,
    )
    assert shown.cap == 10
    assert shown.line == "ember|ab|n"
    assert shown.skipped == ("banner", "session", "light")
    raised = render(
        "default",
        "lamp",
        "card",
        "note",
        "lite",
        policy="plain",
        cap=10_000,
    )
    assert raised.cap == FIELD_CAP
    spaced = define("mine", "Banner", "spin", "Lab", "")
    plain = render("mine", "lamp", "card", "note", "lite", custom=(spaced,), policy="plain")
    assert plain.line == "Lab Banner spin lamp card note lite"
    for policy in ("", "Plain", "ansi", "color"):
        with pytest.raises(Refuse) as caught:
            render("default", "lamp", "card", "note", "lite", policy=policy)
        assert caught.value.code == "BAD_POLICY"
    with pytest.raises(Refuse) as flagged:
        render("default", "lamp", "card", "note", "lite", policy=cast(object, True))
    assert flagged.value.code == "NOT_TEXT"


def test_joined_line_secret_is_refused() -> None:
    row = define("edge", "abcdefghij", "spin", "Bearer", " ")
    assert secret_shape(repr(row)) is False
    with pytest.raises(Refuse) as caught:
        render("edge", "lamp", "card", "note", "lite", custom=(row,), policy="plain")
    assert caught.value.code == "SECRET"
    assert "abcdefghij" not in str(caught.value)


def test_rebuild_reproduces_the_catalog() -> None:
    ember = define("ember", "Ember", "glow", "ember", "|")
    mono = define("mono", "Custom Mono", "spin", "Lab", ">")
    custom = (mono, ember)
    snap = snapshot(custom)
    assert isinstance(snap, Snapshot)
    assert snap.cap == FIELD_CAP
    assert rebuild(snap) == catalog(custom)
    assert pick("mono", snap.skins) == pick("mono", custom)
    assert pick("ember", snap.skins).origin == "custom"
    assert pick("default", snap.skins).origin == "builtin"
    assert rebuild(snapshot(snap.skins)) == rebuild(snap)
    with pytest.raises(Refuse) as raw:
        rebuild(custom)
    assert raw.value.code == "BAD_SKIN"
    with pytest.raises(Refuse) as dup:
        Snapshot(SCHEMA, (ember, define("ember", "Other", "g", "e", "|")), FIELD_CAP)
    assert dup.value.code == "DUPLICATE"
    with pytest.raises(Refuse) as schema:
        Snapshot("nope", (), FIELD_CAP)
    assert schema.value.code == "BAD_SCHEMA"
    with pytest.raises(Refuse) as bad_row:
        Snapshot(SCHEMA, cast(tuple[Skin, ...], ("ember",)), FIELD_CAP)
    assert bad_row.value.code == "BAD_SKIN"


def test_record_boundaries() -> None:
    names = tuple(row.name for row in builtin_skins())
    with pytest.raises(Refuse) as short:
        Catalog(SCHEMA, ("default",), FIELD_CAP)
    assert short.value.code == "BAD_SKIN"
    with pytest.raises(Refuse) as dup:
        Catalog(SCHEMA, names + ("ember", "ember"), FIELD_CAP)
    assert dup.value.code == "DUPLICATE"
    with pytest.raises(Refuse) as low:
        Catalog(SCHEMA, names, 4)
    assert low.value.code == "BAD_LIMIT"
    with pytest.raises(Refuse) as flag:
        Catalog(SCHEMA, names, cast(int, True))
    assert flag.value.code == "NOT_INT"
    note = hold("default").note
    forged = Hold(SCHEMA, "default", 10_000, note)
    assert forged.cap == FIELD_CAP
    with pytest.raises(Refuse) as bad_note:
        Hold(SCHEMA, "default", FIELD_CAP, "write the file")
    assert bad_note.value.code == "BAD_SKIN"
    shown = Status(SCHEMA, "default", "hi", "plain", 10_000, ())
    assert isinstance(shown, Status)
    assert shown.cap == FIELD_CAP
    with pytest.raises(Refuse) as escape:
        Status(SCHEMA, "default", "hi\x1b[31m", "plain", FIELD_CAP, ())
    assert escape.value.code == "BAD_SKIN"
    with pytest.raises(Refuse) as policy:
        Status(SCHEMA, "default", "hi", "ansi", FIELD_CAP, ())
    assert policy.value.code == "BAD_POLICY"
    with pytest.raises(Refuse) as skip:
        Status(SCHEMA, "default", "hi", "plain", FIELD_CAP, ("nope",))
    assert skip.value.code == "BAD_SKIN"
    with pytest.raises(Refuse) as over:
        Status(SCHEMA, "default", "q" * (FIELD_CAP + 1), "plain", 10_000, ())
    assert over.value.code == "OVERSIZE"
    assert over.value.detail == "80"


def test_module_does_not_touch_a_terminal() -> None:
    source = Path(__file__).with_name("skins.py").read_text(encoding="utf-8")
    for banned in (
        "isatty",
        "get_terminal_size",
        "subprocess",
        "socket",
        "urllib",
        "requests",
        "pickle",
        "eval(",
        "exec(",
        "open(",
    ):
        assert banned not in source
