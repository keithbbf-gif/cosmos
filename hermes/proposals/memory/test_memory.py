"""Curated memory: two sections, fixed ceilings, and a human persist nudge."""

from __future__ import annotations

from typing import cast

import pytest

from cosmos_hermes import Refuse, secret_shape
from memory import (
    ENTRY_CAP,
    HISTORY_CAP,
    KEY_LIMIT,
    MEMORY_CHARS,
    SCHEMA,
    SECTIONS,
    TEXT_LIMIT,
    USER_CHARS,
    Entry,
    Memory,
    Record,
    Records,
    Snapshot,
    add,
    empty,
    nudge,
    rebuild,
    records,
    remove,
    render,
    snapshot,
)


def _at(store: Memory, index: int) -> Entry:
    if index < 0 or index >= len(store.entries):
        raise AssertionError(index)
    return store.entries[index]


def _row(bundle: Records, index: int) -> Record:
    if index < 0 or index >= len(bundle.rows):
        raise AssertionError(index)
    return bundle.rows[index]


def test_schema_and_sections() -> None:
    assert SCHEMA == "cosmos-hermes-memory/1"
    assert SECTIONS == frozenset({"memory", "user"})
    assert KEY_LIMIT == 64
    assert MEMORY_CHARS == 2200
    assert USER_CHARS == 1375
    assert empty().cap == ENTRY_CAP
    store = add(add(empty(), "user", "tone", "terse"), "memory", "os", "Debian 12")
    assert [_at(store, 0).section, _at(store, 1).section] == ["user", "memory"]
    assert _at(store, 0).history == ()
    assert _at(store, 0).note_id == "4:user:tone"


def test_replace_keeps_previous_text_in_history() -> None:
    store = add(empty(), "user", "name", "Ada")
    once = add(store, "user", "name", "Ada Lovelace")
    twice = add(once, "user", "name", "A. Lovelace")
    same = add(twice, "user", "name", "A. Lovelace")
    assert same is twice
    assert len(twice.entries) == 1
    entry = _at(twice, 0)
    assert entry.text == "A. Lovelace"
    assert entry.history == ("Ada", "Ada Lovelace")
    shown = render(twice)
    assert "name: A. Lovelace" in shown
    assert "name: Ada\n" not in shown
    assert rebuild(records(twice)) == twice


def test_same_key_in_each_section() -> None:
    store = add(add(empty(), "user", "editor", "VS Code"), "memory", "editor", "vim")
    assert len(store.entries) == 2
    assert _at(store, 0).text == "VS Code"
    assert _at(store, 1).text == "vim"
    assert _at(store, 0).note_id != _at(store, 1).note_id


def test_same_words_on_two_keys_both_stay() -> None:
    store = add(add(empty(), "memory", "one", "same words"), "memory", "two", "same words")
    assert len(store.entries) == 2


def test_secret_and_bad_section() -> None:
    store = add(empty(), "memory", "os", "Debian 12")
    with pytest.raises(Refuse) as secret:
        add(store, "memory", "token", "sk-livekeyvalue")
    assert secret.value.code == "SECRET"
    assert _at(store, 0).text == "Debian 12"
    with pytest.raises(Refuse) as key_secret:
        add(store, "user", "api_key=abcdef", "monthly")
    assert key_secret.value.code == "SECRET"
    with pytest.raises(Refuse) as both:
        add(store, "notes", "k", "Bearer abcdefghijk")
    assert both.value.code == "SECRET"
    with pytest.raises(Refuse) as section:
        add(store, "profile", "k", "terse")
    assert section.value.code == "BAD_SECTION"
    with pytest.raises(Refuse) as built:
        Entry("user", "k", "password=hunter2", ())
    assert built.value.code == "SECRET"
    with pytest.raises(Refuse) as prior:
        Entry("user", "k", "ok", ("password=hunter2",))
    assert prior.value.code == "SECRET"
    with pytest.raises(Refuse) as row_secret:
        Record("sk-livekeyvalue", "user", "k", "ok")
    assert row_secret.value.code == "SECRET"
    with pytest.raises(Refuse) as shown:
        Snapshot("sk-livekeyvalue", 0)
    assert shown.value.code == "SECRET"


def test_bad_key_empty_and_invisible() -> None:
    store = empty()
    with pytest.raises(Refuse) as empty_key:
        add(store, "user", "", "text")
    assert empty_key.value.code == "EMPTY"
    with pytest.raises(Refuse) as empty_text:
        add(store, "memory", "k", "")
    assert empty_text.value.code == "EMPTY"
    with pytest.raises(Refuse) as blank_history:
        Entry("user", "k", "ok", ("",))
    assert blank_history.value.code == "EMPTY"
    with pytest.raises(Refuse) as bad_key:
        add(store, "user", "Ada Lovelace", "nope")
    assert bad_key.value.code == "BAD_KEY"
    with pytest.raises(Refuse) as hidden:
        add(store, "memory", "note", "hidden\u200btext")
    assert hidden.value.code == "INVISIBLE"
    with pytest.raises(Refuse) as bidi:
        add(store, "memory", "note", "left\u202eto right")
    assert bidi.value.code == "INVISIBLE"
    kept = add(store, "memory", "note", "line one\nline two")
    assert _at(kept, 0).text == "line one\nline two"


def test_bounds() -> None:
    store = empty()
    with pytest.raises(Refuse) as not_text:
        add(store, "user", "k", 12)
    assert not_text.value.code == "NOT_TEXT"
    with pytest.raises(Refuse) as raw:
        add(store, "user", "k", b"text")
    assert raw.value.code == "NOT_TEXT"
    with pytest.raises(Refuse) as nul:
        add(store, "user", "k", "a\x00b")
    assert nul.value.code == "NULL_BYTE"
    with pytest.raises(Refuse) as size:
        add(store, "memory", "k", "x" * (TEXT_LIMIT + 1))
    assert size.value.code == "OVERSIZE"
    assert size.value.detail == str(TEXT_LIMIT)


def test_entry_cap_and_ignored_higher_request() -> None:
    store = empty(ENTRY_CAP + 50)
    assert store.cap == ENTRY_CAP
    assert Memory(entries=(), cap=100).cap == ENTRY_CAP
    assert Records(ENTRY_CAP + 9, ()).cap == ENTRY_CAP
    assert rebuild(Records(ENTRY_CAP + 9, ())) == empty()
    for index in range(ENTRY_CAP):
        section = "memory" if index % 2 == 0 else "user"
        store = add(store, section, f"k{index}", f"fact {index}")
    assert len(store.entries) == ENTRY_CAP
    with pytest.raises(Refuse) as over:
        add(store, "user", "extra", "one more")
    assert over.value.code == "OVER_COUNT"
    replaced = add(store, "user", "k1", "fact 1 revised")
    assert len(replaced.entries) == ENTRY_CAP
    kept = next(item for item in replaced.entries if item.key == "k1")
    assert kept.text == "fact 1 revised"
    assert kept.history == ("fact 1",)
    with pytest.raises(Refuse) as flag:
        empty(True)
    assert flag.value.code == "NOT_INT"
    with pytest.raises(Refuse) as low:
        empty(0)
    assert low.value.code == "BAD_LIMIT"
    with pytest.raises(Refuse) as direct:
        Memory(entries=(), cap=True)
    assert direct.value.code == "NOT_INT"
    with pytest.raises(Refuse) as count_flag:
        Snapshot("MEMORY [0% 0/2200]\n\nUSER [0% 0/1375]\n", True)
    assert count_flag.value.code == "NOT_INT"
    with pytest.raises(Refuse) as count_low:
        Snapshot("ok", -1)
    assert count_low.value.code == "BAD_LIMIT"


def test_tighter_cap_is_recorded() -> None:
    store = add(add(empty(2), "user", "a", "one"), "memory", "b", "two")
    assert store.cap == 2
    with pytest.raises(Refuse) as over:
        add(store, "user", "c", "three")
    assert over.value.code == "OVER_COUNT"
    assert rebuild(records(store)) == store


def test_section_char_ceiling_skips_nothing_later() -> None:
    room = add(empty(), "user", "room", "a")
    with pytest.raises(Refuse) as huge:
        add(room, "user", "big", "b" * USER_CHARS)
    assert huge.value.code == "OVER_CHARS"
    assert huge.value.detail == str(USER_CHARS)
    later = add(room, "user", "fit", "short note")
    assert _at(later, 1).key == "fit"
    full = "c" * USER_CHARS
    packed = add(empty(), "user", "bio", full)
    revised = add(packed, "user", "bio", "d" * USER_CHARS)
    assert _at(revised, 0).history == (full,)
    with pytest.raises(Refuse) as extra:
        add(revised, "user", "more", "e")
    assert extra.value.code == "OVER_CHARS"
    left = "m" * 1100
    right = "n" * 1100
    memory = add(add(empty(), "memory", "left", left), "memory", "right", right)
    assert len(_at(memory, 0).text) + len(_at(memory, 1).text) == MEMORY_CHARS
    with pytest.raises(Refuse) as spill:
        add(memory, "memory", "left", "n" * 1101)
    assert spill.value.code == "OVER_CHARS"
    assert spill.value.detail == str(MEMORY_CHARS)
    assert _at(memory, 0).text == left


def test_history_cap() -> None:
    store = add(empty(), "memory", "note", "v0")
    for index in range(1, HISTORY_CAP + 1):
        store = add(store, "memory", "note", f"v{index}")
    entry = _at(store, 0)
    assert entry.history == tuple(f"v{index}" for index in range(HISTORY_CAP))
    assert entry.text == f"v{HISTORY_CAP}"
    with pytest.raises(Refuse) as over:
        add(store, "memory", "note", "overflow")
    assert over.value.code == "OVER_HISTORY"
    assert _at(store, 0).text == f"v{HISTORY_CAP}"
    piled = tuple(f"v{index}" for index in range(HISTORY_CAP + 1))
    with pytest.raises(Refuse) as direct:
        Entry("memory", "note", "now", piled)
    assert direct.value.code == "OVER_HISTORY"


def test_duplicate_ids() -> None:
    one = Entry("user", "name", "Ada")
    with pytest.raises(Refuse) as dup:
        Memory(entries=(one, Entry("user", "name", "other")), cap=ENTRY_CAP)
    assert dup.value.code == "DUP_ID"
    row = Record(one.note_id, one.section, one.key, one.text, one.history)
    again = Record(one.note_id, one.section, one.key, "Ada Lovelace")
    with pytest.raises(Refuse) as rows:
        Records(ENTRY_CAP, (row, again))
    assert rows.value.code == "DUP_ID"


def test_bad_id_and_store_shape() -> None:
    with pytest.raises(Refuse) as bad_id:
        Record("not-an-id", "user", "name", "Ada")
    assert bad_id.value.code == "BAD_ID"
    with pytest.raises(Refuse) as blank_id:
        Record("", "user", "name", "Ada")
    assert blank_id.value.code == "BAD_ID"
    with pytest.raises(Refuse) as entry_id:
        Entry("user", "name", "Ada", (), "wrong")
    assert entry_id.value.code == "BAD_ID"
    with pytest.raises(Refuse) as bad_add:
        add("store", "user", "k", "text")
    assert bad_add.value.code == "BAD_STORE"
    with pytest.raises(Refuse) as bad_nudge:
        nudge(None)
    assert bad_nudge.value.code == "BAD_STORE"
    with pytest.raises(Refuse) as bad_remove:
        remove(1, "user", "k")
    assert bad_remove.value.code == "BAD_STORE"
    with pytest.raises(Refuse) as bad_rebuild:
        rebuild(())
    assert bad_rebuild.value.code == "BAD_STORE"
    with pytest.raises(Refuse) as shape:
        Memory(entries=cast(tuple[Entry, ...], ("nope",)), cap=ENTRY_CAP)
    assert shape.value.code == "BAD_STORE"
    with pytest.raises(Refuse) as listed:
        Memory(entries=cast(tuple[Entry, ...], [Entry("user", "k", "one")]), cap=ENTRY_CAP)
    assert listed.value.code == "BAD_STORE"
    with pytest.raises(Refuse) as hist:
        Entry("user", "k", "one", cast(tuple[str, ...], ["one"]))
    assert hist.value.code == "BAD_STORE"
    with pytest.raises(Refuse) as row_shape:
        Records(ENTRY_CAP, cast(tuple[Record, ...], ("nope",)))
    assert row_shape.value.code == "BAD_STORE"
    piled = tuple(Entry("memory", f"k{index}", f"t{index}", ()) for index in range(ENTRY_CAP + 1))
    with pytest.raises(Refuse) as count:
        Memory(entries=piled, cap=ENTRY_CAP)
    assert count.value.code == "OVER_COUNT"


def test_remove_then_rebuild() -> None:
    store = add(add(empty(), "user", "name", "Ada"), "memory", "os", "Debian 12")
    cut = remove(store, "user", "name")
    assert [item.key for item in cut.entries] == ["os"]
    assert rebuild(records(cut)) == cut
    with pytest.raises(Refuse) as missing:
        remove(cut, "user", "name")
    assert missing.value.code == "MISSING"
    with pytest.raises(Refuse) as bad_key:
        remove(cut, "user", "No Key")
    assert bad_key.value.code == "BAD_KEY"
    with pytest.raises(Refuse) as secret:
        remove(cut, "memory", "api_key=abcdef")
    assert secret.value.code == "SECRET"
    assert cut == remove(store, "user", "name")


def test_rebuild_preserves_lowered_cap() -> None:
    store = add(empty(3), "memory", "os", "Debian 12")
    bundle = records(store)
    assert bundle.cap == 3
    assert _row(bundle, 0).text == "Debian 12"
    assert rebuild(bundle) == store
    grown = add(store, "user", "tone", "terse")
    assert rebuild(records(grown)) == grown
    assert grown.cap == 3


def test_snapshot_stays_frozen() -> None:
    store = add(empty(), "user", "style", "concise")
    frozen = snapshot(store)
    later = add(store, "memory", "os", "Debian 12")
    assert snapshot(store) == frozen
    assert snapshot(later) != frozen
    assert frozen.count == 1
    assert "style: concise" in frozen.text
    assert "Debian 12" not in frozen.text
    assert secret_shape(frozen.text) is False


def test_nudge_writes_nothing() -> None:
    store = add(empty(), "user", "style", "concise")
    before = store.entries
    text = nudge(store)
    assert store.entries is before
    assert "persist" in text.lower()
    assert "writes nothing" in text.lower()
    assert not secret_shape(text)
    assert not secret_shape(repr(store))
    assert not secret_shape(repr(_at(store, 0)))
    assert not secret_shape(repr(records(store)))
    assert not secret_shape(render(store))


def _atlas_story() -> tuple[Memory, Memory, str, Snapshot, str]:
    store = empty()
    store = add(
        store,
        "memory",
        "atlas-stack",
        "Project atlas is a Rust service at ~/code/atlas using Axum and SQLx.",
    )
    store = add(
        store,
        "memory",
        "atlas-host",
        "The atlas host runs Debian 12 with PostgreSQL 16.\nShell on that host is zsh.",
    )
    store = add(
        store,
        "user",
        "ada-style",
        "Ada prefers terse notes on project atlas and dislikes verbose status.",
    )
    code = "UNCAUGHT"
    try:
        add(store, "memory", "atlas-token", "sk-atlaslivekeyvalue")
    except Refuse as refused:
        code = refused.code
    built = rebuild(records(store))
    frozen = snapshot(store)
    return store, built, code, frozen, render(store)


def test_example_memory() -> None:
    first = _atlas_story()
    second = _atlas_story()
    assert first == second
    store, built, code, frozen, shown = first
    assert code == "SECRET"
    assert built == store
    assert len(store.entries) == 3
    assert [item.key for item in store.entries] == ["atlas-stack", "atlas-host", "ada-style"]
    assert all(item.key != "atlas-token" for item in store.entries)
    assert "Project atlas" in shown
    assert "sk-" not in shown
    assert secret_shape(shown) is False
    assert frozen.text == shown
    assert frozen.count == 3
    assert "\n" in _at(store, 1).text
