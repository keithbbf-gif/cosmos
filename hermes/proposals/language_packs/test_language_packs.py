"""Language-pack catalog tests. No network."""

from __future__ import annotations

import ast
from collections.abc import Callable
from dataclasses import FrozenInstanceError, replace
from pathlib import Path
from typing import cast

import pytest

import language_packs
from cosmos_hermes import Refuse, secret_shape
from language_packs import (
    DEPTH_CAP,
    LOCALE_CAP,
    SCHEMA,
    STEP_CAP,
    TABLE_CAP,
    VALUE_CAP,
    Catalog,
    LanguageChoice,
    LocaleMeta,
    LookupHit,
    Phrase,
    add,
    choose,
    fallback,
    fetch,
    languages,
    lookup,
    rebuild,
)


def _code(call: Callable[[], object]) -> str:
    try:
        call()
    except Refuse as err:
        return err.code
    raise AssertionError("expected Refuse")


def _tag(index: int) -> str:
    return chr(ord("a") + index // 26) + chr(ord("a") + index % 26)


def _table(count: int) -> dict[str, str]:
    return {f"k{index:03d}": f"v{index}" for index in range(count)}


def _deep(levels: int) -> dict[str, object]:
    node: dict[str, object] = {"leaf": "x"}
    for _ in range(levels):
        node = {"nest": node}
    return node


def test_schema_and_success() -> None:
    assert language_packs.SCHEMA == "cosmos-hermes-language_packs/1"
    assert SCHEMA == "cosmos-hermes-language_packs/1"
    book = add(
        "pl",
        {"approval": {"denied": "Odrzucono"}, "gateway.goal_cleared": "Cel wyczyszczony"},
        endonym="Polski",
    )
    again = add(
        "pl",
        {"approval": {"denied": "Odrzucono"}, "gateway.goal_cleared": "Cel wyczyszczony"},
        endonym="Polski",
    )
    hit = lookup("pl", "approval.denied", book)
    other = lookup("pl", "gateway.goal_cleared", book)
    assert book == again
    assert hit == lookup("pl", "approval.denied", again)
    assert hit.status == "HIT"
    assert hit.text == "Odrzucono"
    assert hit.text != ""
    assert hit.layer == "plugin"
    assert hit.surface == "core"
    assert hit.source == "pl"
    assert hit.step == 0
    assert hit.step_cap == STEP_CAP
    assert hit.schema == SCHEMA
    assert rebuild(book) == book
    assert rebuild(book) is not book
    assert other.text == "Cel wyczyszczony"
    assert languages(book) == ("pl",)
    picked = choose("pl", book)
    assert picked == LanguageChoice(SCHEMA, "pl", "display", "Polski", False)
    assert not secret_shape(repr(book))
    assert not secret_shape(repr(hit))
    assert not secret_shape(repr(picked))
    assert "Odrzucono" not in repr(hit)


def _shown(locale: str, key: str, catalog: Catalog, *, surface: str = "core") -> str:
    try:
        found = lookup(locale, key, catalog, surface=surface)
    except Refuse as err:
        return err.code
    return found.text


def test_missing_key_raises_missing() -> None:
    book = add("en", {"status": {"ready": "Ready"}}, endonym="English")
    assert lookup("en", "status.ready", book).text == "Ready"
    assert _shown("en", "status.ready", book) == "Ready"
    assert _shown("en", "status.missing", book) == "MISSING"
    assert _code(lambda: lookup("en", "status.missing", book)) == "MISSING"
    empty = add("de", {})
    assert _shown("de", "approval.allowed", empty) == "MISSING"
    assert _code(lambda: lookup("en", "approval.denied")) == "BAD_LOCALE"


def test_unknown_and_bad_locale() -> None:
    book = add("en", {"a": "Alpha"})
    assert _code(lambda: lookup("pl", "a", book)) == "BAD_LOCALE"
    assert _code(lambda: add("pt-br", {"a": "x"})) == "BAD_LOCALE"
    assert _code(lambda: add("EN", {"a": "x"})) == "BAD_LOCALE"
    assert _code(lambda: add("en-us", {"a": "x"})) == "BAD_LOCALE"
    assert _code(lambda: add("zh-Hant", {"a": "x"})) == "BAD_LOCALE"
    assert _code(lambda: add("e", {})) == "BAD_LOCALE"
    assert _code(lambda: add("", {})) == "BAD_LOCALE"
    assert _code(lambda: add(12, {})) == "NOT_TEXT"
    assert _code(lambda: add("en\x00", {})) == "NULL_BYTE"
    regional = add("pt-BR", {"approval": {"denied": "Negado"}}, endonym="Portugues")
    assert lookup("pt-BR", "approval.denied", regional).text == "Negado"
    assert lookup("en-US", "a", add("en-US", {"a": "Hi"})).status == "HIT"


def test_layers_and_surfaces() -> None:
    book = add("pl", {"only.bundled": "B", "shared": "bundled"}, layer="bundled")
    book = add("pl", {"only.overlay": "O", "shared": "overlay"}, book, layer="overlay")
    book = add("pl", {"shared": "plugin-old"}, book, layer="plugin")
    book = add("pl", {"shared": "plugin-new"}, book, layer="plugin", endonym="Polski")
    book = add("pl", {"title": "Tui"}, book, surface="tui", endonym="Polski")
    assert lookup("pl", "shared", book).text == "plugin-new"
    assert lookup("pl", "shared", book).layer == "plugin"
    assert lookup("pl", "only.bundled", book).text == "B"
    assert lookup("pl", "only.overlay", book).layer == "overlay"
    assert _code(lambda: lookup("pl", "title", book)) == "MISSING"
    assert lookup("pl", "title", book, surface="tui").text == "Tui"
    assert _code(lambda: lookup("pl", "title", book, surface="desktop")) == "MISSING"
    assert choose("pl", book).endonym == "Polski"
    assert any(phrase.layer == "bundled" and phrase.text == "B" for phrase in book.phrases)


def test_placeholders_and_reserved_keys() -> None:
    book = add("en", {"drain": "Draining {count} agents", "hint": "Type {{name}} then {name}"})
    book = add("pl", {"drain": "Odplyw {count} agentow"}, book)
    book = add("pl", {"hint": "Wpisz {{name}} i {name}"}, book)
    assert lookup("pl", "drain", book).text == "Odplyw {count} agentow"
    assert _code(lambda: add("de", {"drain": "X"}, book)) == "BAD_PLACEHOLDER"
    assert _code(lambda: add("de", {"hint": "Nur {name} {extra}"}, book)) == "BAD_PLACEHOLDER"
    early = add("pl", {"drain": "Czekaj {count}"})
    matched = add("en", {"drain": "Wait {count}"}, early)
    assert lookup("pl", "drain", matched).status == "HIT"
    bare = add("pl", {"drain": "Czekaj"})
    assert _code(lambda: add("en", {"drain": "Wait {count}"}, bare)) == "BAD_PLACEHOLDER"
    assert _code(lambda: add("en", {"n": "{0}"})) == "BAD_PLACEHOLDER"
    assert _code(lambda: add("en", {"n": "{"})) == "BAD_PLACEHOLDER"
    assert _code(lambda: add("en", {"n": "}"})) == "BAD_PLACEHOLDER"
    assert _code(lambda: add("en", {"n": "{bad-name}"})) == "BAD_PLACEHOLDER"
    tui = add("en", {"progress": "{0} of {1}"}, surface="tui")
    tui = add("pl", {"progress": "{0} z {1}"}, tui, surface="tui")
    assert lookup("pl", "progress", tui, surface="tui").text == "{0} z {1}"
    assert _code(lambda: add("de", {"progress": "{count}"}, tui, surface="tui")) == "BAD_PLACEHOLDER"
    assert _code(lambda: add("en", {"progress": "{count}"}, surface="desktop")) == "BAD_PLACEHOLDER"
    assert _code(lambda: add("en", {"on": "x"})) == "BAD_KEY"
    assert _code(lambda: add("en", {"approval": {"yes": "x"}})) == "BAD_KEY"
    assert _code(lambda: add("en", {"Off": "x"})) == "BAD_KEY"
    assert _code(lambda: add("en", {"1a": "x"})) == "BAD_KEY"
    assert _code(lambda: add("en", {"": "x"})) == "BAD_KEY"
    assert _code(lambda: add("en", {"a..b": "x"})) == "BAD_KEY"
    assert _code(lambda: add("en", {"a.": "x"})) == "BAD_KEY"
    assert _code(lambda: add("en", {".a": "x"})) == "BAD_KEY"


def test_table_shape_and_secrets() -> None:
    assert _code(lambda: add("en", {"n": 1})) == "NOT_TEXT"
    assert _code(lambda: add("en", {"n": True})) == "NOT_TEXT"
    assert _code(lambda: add("en", {"n": ["a"]})) == "NOT_TEXT"
    assert _code(lambda: add("en", {"n": None})) == "NOT_TEXT"
    assert _code(lambda: add("en", {1: "x"})) == "NOT_TEXT"
    assert _code(lambda: add("en", {"n": ""})) == "EMPTY"
    assert _code(lambda: add("en", {"approval": {}})) == "EMPTY"
    assert _code(lambda: add("en", {"n": "b"}, endonym="")) == "EMPTY"
    assert _code(lambda: add("en", [])) == "BAD_TABLE"
    assert _code(lambda: add("en", "nope")) == "BAD_TABLE"
    assert _code(lambda: add("en", {"a": {"b": "1"}, "a.b": "2"})) == "DUPLICATE"
    assert _code(lambda: add("en", {"a": "bad\x00"})) == "NULL_BYTE"
    assert _code(lambda: add("en", {"a\x00": "b"})) == "NULL_BYTE"
    assert _code(lambda: add("en", {"a": "x" * (VALUE_CAP + 1)})) == "OVERSIZE"
    assert _code(lambda: add("en", {"a": "sk-abcdefghij"})) == "SECRET"
    assert _code(lambda: add("en", {"a": "Bearer abcdefgh"})) == "SECRET"
    assert _code(lambda: add("en", {"a": "ok"}, endonym="token=abcdef")) == "SECRET"
    assert _code(lambda: add("en", {"a": "b"}, surface="mobile")) == "BAD_SURFACE"
    assert _code(lambda: add("en", {"a": "b"}, layer="remote")) == "BAD_LAYER"
    assert _code(lambda: add("en", {"a": "b"}, rtl="no")) == "BAD_FLAG"
    assert _code(lambda: add("en", {"a": "b"}, catalog=[])) == "BAD_CATALOG"
    assert _code(lambda: lookup("en", "a", catalog="nope")) == "BAD_CATALOG"
    kept = add("en", {"a": "one", "b": "bee"})
    kept = add("en", {"a": "two"}, kept)
    assert lookup("en", "a", kept).text == "two"
    assert lookup("en", "b", kept).text == "bee"
    assert len(kept.phrases) == 2
    blank = add("pl", {"a": "x"})
    blank = add("pl", {}, blank, endonym="Polski")
    assert lookup("pl", "a", blank).text == "x"
    assert choose("pl", blank).endonym == "Polski"


def test_cap_is_policy() -> None:
    book = add(
        "en",
        {"a": "one", "b": "two"},
        table_cap=10**9,
        locale_cap=10**9,
        value_cap=10**9,
    )
    assert book.table_cap == TABLE_CAP
    assert book.locale_cap == LOCALE_CAP
    assert book.value_cap == VALUE_CAP
    assert len(book.phrases) == 2
    assert _code(lambda: add("en", {"a": "b"}, table_cap=1)) == "BAD_LIMIT"
    assert _code(lambda: add("en", {"a": "b"}, table_cap=0)) == "BAD_LIMIT"
    assert _code(lambda: add("en", {"a": "b"}, table_cap=True)) == "BAD_LIMIT"
    assert _code(lambda: add("en", {"a": "b"}, locale_cap="9")) == "BAD_LIMIT"
    full = add("en", _table(TABLE_CAP), table_cap=10**6)
    assert len(full.phrases) == TABLE_CAP
    assert full.table_cap == TABLE_CAP
    assert _code(lambda: add("en", _table(TABLE_CAP + 1), table_cap=10**6)) == "OVER_CAP"
    assert _code(lambda: add("en", {"extra": "z"}, full, table_cap=10**6)) == "OVER_CAP"
    tui = add("en", {"progress": "{0}"}, full, surface="tui")
    assert lookup("en", "progress", tui, surface="tui").text == "{0}"
    replaced = add("en", {"k000": "changed"}, full)
    assert lookup("en", "k000", replaced).text == "changed"
    assert len([phrase for phrase in replaced.phrases if phrase.surface == "core"]) == TABLE_CAP
    stacked: Catalog | None = None
    for index in range(LOCALE_CAP):
        stacked = add(_tag(index), {"ok": "x"}, stacked, locale_cap=10**6)
    assert stacked is not None
    held = stacked
    assert len(languages(held)) == LOCALE_CAP
    assert _code(lambda: add("zz", {"ok": "x"}, held, locale_cap=10**6)) == "OVER_CAP"
    updated = add("aa", {"ok": "y"}, held)
    assert lookup("aa", "ok", updated).text == "y"
    meta = LocaleMeta("en", "English", False)
    clamped = Catalog(SCHEMA, (meta,), (), TABLE_CAP + 9, LOCALE_CAP + 9, VALUE_CAP + 9)
    assert clamped.table_cap == TABLE_CAP
    assert clamped.locale_cap == LOCALE_CAP
    assert clamped.value_cap == VALUE_CAP
    assert _code(lambda: Catalog(SCHEMA, (meta,), (), TABLE_CAP - 1, LOCALE_CAP, VALUE_CAP)) == "BAD_LIMIT"
    phrases = tuple(
        Phrase("en", f"k{index:03d}", "v", "core", "plugin") for index in range(TABLE_CAP + 1)
    )
    assert (
        _code(lambda: Catalog(SCHEMA, (meta,), phrases, TABLE_CAP + 50, LOCALE_CAP, VALUE_CAP))
        == "OVER_CAP"
    )


def test_depth_choose_and_records() -> None:
    levels = DEPTH_CAP - 1
    deep = add("en", _deep(levels))
    deep_key = ".".join(["nest"] * levels + ["leaf"])
    assert lookup("en", deep_key, deep).text == "x"
    assert _code(lambda: add("en", _deep(DEPTH_CAP))) == "BAD_TABLE"
    book = add("ar", {"a": "Ahlan"}, endonym="Arabic", rtl=True)
    book = add("de", {"a": "Hallo"}, book, endonym="Deutsch")
    assert languages(book) == ("ar", "de")
    assert choose("ar", book).rtl is True
    forced = choose("zz", book, env="ar")
    assert forced.locale == "ar"
    assert forced.source == "env"
    assert choose("de", book, env="").source == "display"
    book = add("ar", {"b": "Y"}, book, endonym="Arabic")
    assert choose("ar", book).rtl is False
    assert _code(lambda: choose("fr", book)) == "BAD_LOCALE"
    assert _code(lambda: choose("ar", book, env="nope")) == "BAD_LOCALE"
    assert _code(lambda: choose("ar", book, env=4)) == "NOT_TEXT"
    assert _code(lambda: choose("en", None)) == "BAD_CATALOG"
    assert _code(lambda: languages([])) == "BAD_CATALOG"
    base = add("en", {"a": "hello"})
    assert _code(lambda: replace(base, schema="cosmos-hermes-other/1")) == "BAD_SCHEMA"
    meta = LocaleMeta("en", "English", False)
    phrase = Phrase("en", "a", "hello", "core", "plugin")
    assert _code(lambda: Catalog(SCHEMA, (meta, meta), (), TABLE_CAP, LOCALE_CAP, VALUE_CAP)) == "DUPLICATE"
    assert (
        _code(lambda: Catalog(SCHEMA, (meta,), (phrase, phrase), TABLE_CAP, LOCALE_CAP, VALUE_CAP))
        == "DUPLICATE"
    )
    other = LocaleMeta("pl", "Polski", False)
    assert _code(lambda: Catalog(SCHEMA, (other,), (phrase,), TABLE_CAP, LOCALE_CAP, VALUE_CAP)) == "BAD_CATALOG"
    assert (
        _code(
            lambda: Catalog(
                SCHEMA,
                (meta,),
                cast(tuple[Phrase, ...], ("x",)),
                TABLE_CAP,
                LOCALE_CAP,
                VALUE_CAP,
            )
        )
        == "BAD_CATALOG"
    )
    assert _code(lambda: LookupHit("en", "a", "hello", "GONE", "core", "plugin", "en", 0)) == "BAD_STATUS"
    assert _code(lambda: LookupHit("en", "a", "hello", "MISSING", "core", "plugin", "en", 0)) == "BAD_STATUS"
    assert _code(lambda: LookupHit("en", "a", "hello", "HIT", "core", "plugin", "pl", 0)) == "BAD_RECORD"
    assert _code(lambda: LookupHit("en", "a", "hello", "FALLBACK", "core", "plugin", "en", 1)) == "BAD_RECORD"
    assert _code(lambda: LookupHit("en", "a", "hello", "HIT", "core", "plugin", "en", 1)) == "BAD_RECORD"
    assert _code(lambda: LookupHit("en", "a", "hello", "FALLBACK", "core", "plugin", "pl", 0)) == "BAD_RECORD"
    assert _code(lambda: LookupHit("en", "a", "hello", "HIT", "core", "plugin", "en", True)) == "BAD_RECORD"
    assert _code(lambda: LookupHit("en", "a", "", "HIT", "core", "plugin", "en", 0)) == "EMPTY"
    assert _code(lambda: LookupHit("en", "a", "hello", "HIT", "core", "plugin", "en", 0, 0)) == "BAD_LIMIT"
    raised = LookupHit("pl", "note.field", "Field note", "FALLBACK", "core", "plugin", "en", 1, 9)
    assert raised.step == 1
    assert raised.step_cap == STEP_CAP
    assert raised.source == "en"
    assert _code(lambda: replace(base, schema="cosmos-\ud800")) == "BAD_SCHEMA"
    assert _code(lambda: LanguageChoice(SCHEMA, "en", "disk", "English", False)) == "BAD_SOURCE"
    assert _code(lambda: LocaleMeta("en", "English", cast(bool, 1))) == "BAD_FLAG"
    with pytest.raises(FrozenInstanceError):
        setattr(base, "schema", "other")
    hit = lookup("en", "a", base)
    with pytest.raises(FrozenInstanceError):
        LookupHit.__setattr__(hit, "status", "MISSING")


def test_fallback_is_one_recorded_step() -> None:
    book = add(
        "en",
        {"status": {"ready": "Ready"}, "light": {"porch": "Porch light"}},
        endonym="English",
    )
    book = add("en", {"progress": "{0}"}, book, surface="tui")
    book = add("pl", {"status": {"ready": "Gotowe"}}, book, endonym="Polski")
    book = add("de", {"card": {"title": "Karte"}}, book, endonym="Deutsch")
    direct = fallback("pl", "status.ready", book, "en")
    assert direct.status == "HIT"
    assert direct.step == 0
    assert direct.source == "pl"
    assert direct.text == "Gotowe"
    stepped = fallback("pl", "light.porch", book, "en", step_cap=10**6)
    assert stepped.status == "FALLBACK"
    assert stepped.step == 1
    assert stepped.step_cap == STEP_CAP
    assert stepped.locale == "pl"
    assert stepped.source == "en"
    assert stepped.layer == "plugin"
    assert stepped.text == "Porch light"
    assert stepped.text != ""
    assert _shown("pl", "light.porch", book) == "MISSING"
    assert _code(lambda: fallback("de", "light.porch", book, "pl")) == "MISSING"
    assert fallback("pl", "progress", book, "en", surface="tui").text == "{0}"
    assert _code(lambda: fallback("pl", "progress", book, "en")) == "MISSING"
    assert _code(lambda: fallback("en", "status.ready", book, "en")) == "BAD_FALLBACK"
    assert _code(lambda: fallback("en", "status.ready", book, ["pl", "de"])) == "BAD_FALLBACK"
    assert _code(lambda: fallback("en", "status.ready", book, ("pl",))) == "BAD_FALLBACK"
    assert _code(lambda: fallback("fr", "status.ready", book, "en")) == "BAD_LOCALE"
    assert _code(lambda: fallback("en", "status.ready", book, "fr")) == "BAD_LOCALE"
    assert _code(lambda: fallback("pl", "light.porch", book, "en", step_cap=0)) == "BAD_LIMIT"
    assert _code(lambda: fallback("pl", "light.porch", None, "en")) == "BAD_CATALOG"
    assert _code(lambda: rebuild(())) == "BAD_CATALOG"
    assert rebuild(book) == book


def test_example_language_packs() -> None:
    """Mira's session shows a porch card, a field note, and a light."""

    def once() -> tuple[object, ...]:
        book = add(
            "en",
            {
                "card": {"porch": "Porch card"},
                "note": {"field": "Field note"},
                "light": {"porch": "Porch light"},
                "status": {"ready": "Ready"},
                "session": {"open": "Session open"},
            },
            endonym="English",
        )
        book = add(
            "pl",
            {"card": {"porch": "Karta ganku"}, "status": {"ready": "Gotowe"}},
            book,
            endonym="Polski",
        )
        ready = lookup("en", "status.ready", book)
        missing = _shown("en", "status.missing", book)
        card = lookup("pl", "card.porch", book)
        note_miss = _shown("pl", "note.field", book)
        note = fallback("pl", "note.field", book, "en")
        light = fallback("pl", "light.porch", book, "en")
        session = fallback("pl", "session.open", book, "en")
        wider = add("de", {"card": {"porch": "Karten"}}, book, endonym="Deutsch")
        chain = "NONE"
        try:
            fallback("de", "note.field", wider, "pl")
        except Refuse as err:
            chain = err.code
        choice = choose("de", wider, env="pl")
        restored = rebuild(wider)
        assert ready.text == "Ready"
        assert ready.status == "HIT"
        assert ready.source == "en"
        assert ready.step == 0
        assert ready.text != ""
        assert missing == "MISSING"
        assert card.text == "Karta ganku"
        assert card.status == "HIT"
        assert note_miss == "MISSING"
        assert note.status == "FALLBACK"
        assert note.source == "en"
        assert note.locale == "pl"
        assert note.step == 1
        assert note.text == "Field note"
        assert light.text == "Porch light"
        assert light.status == "FALLBACK"
        assert session.text == "Session open"
        assert session.source == "en"
        assert chain == "MISSING"
        assert choice == LanguageChoice(SCHEMA, "pl", "env", "Polski", False)
        assert restored == wider
        assert languages(wider) == ("en", "pl", "de")
        assert not secret_shape(repr(note))
        return (ready, missing, card, note_miss, note, light, session, chain, choice, restored)

    assert once() == once()


def test_fetch_refuses() -> None:
    source = Path(language_packs.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    banned = {"socket", "urllib", "requests", "subprocess", "pickle"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name.split(".")[0] not in banned
        if isinstance(node, ast.ImportFrom) and node.module is not None:
            assert node.module.split(".")[0] not in banned
        if isinstance(node, ast.Name) and node.id in {"eval", "exec", "compile"}:
            raise AssertionError(node.id)
    assert _code(lambda: fetch()) == "NO_FETCH"
    assert _code(lambda: fetch("")) == "NO_FETCH"
    assert _code(lambda: fetch("https://example.invalid/hermes-lang-pl")) == "NO_FETCH"
    assert _code(lambda: fetch("sk-abcdefghij")) == "SECRET"
    assert _code(lambda: fetch(12)) == "NOT_TEXT"
    assert _code(lambda: fetch("a\x00")) == "NULL_BYTE"
    assert _code(lambda: fetch("u" * (VALUE_CAP + 1))) == "OVERSIZE"
