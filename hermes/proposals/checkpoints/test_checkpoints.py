"""Checkpoints store sha256 and bytes and roll back one generation."""

from __future__ import annotations

import hashlib
from collections.abc import Callable
from typing import cast

import pytest

import checkpoints
from cosmos_hermes import Refuse


def _code(func: Callable[[], object]) -> str:
    with pytest.raises(Refuse) as caught:
        func()
    return caught.value.code


def _fence(rows: tuple[checkpoints.Fence, ...], index: int) -> checkpoints.Fence:
    if index < 0 or index >= len(rows):
        raise AssertionError("fence")
    return rows[index]


def _file(rows: tuple[checkpoints.FileRecord, ...], index: int) -> checkpoints.FileRecord:
    if index < 0 or index >= len(rows):
        raise AssertionError("file")
    return rows[index]


def _sha_of(rows: tuple[checkpoints.FileRecord, ...], name: str) -> str:
    for row in rows:
        if row.name == name:
            return row.sha256
    raise AssertionError(name)


def test_schema() -> None:
    assert checkpoints.SCHEMA == "cosmos-hermes-checkpoints/1"
    assert checkpoints.GENESIS == "0" * 64


def test_snapshot_stores_sha256_and_one_level_rollback() -> None:
    store = checkpoints.Checkpoints()
    first = hashlib.sha256(b"one").hexdigest()
    second = hashlib.sha256(b"two").hexdigest()
    opened = store.snapshot({"b.txt": b"side", "rel/a.txt": b"one"})
    assert opened.schema == checkpoints.SCHEMA
    assert opened.policy == store.policy
    assert [row.name for row in opened.files] == ["b.txt", "rel/a.txt"]
    assert opened.fence.files == store.catalog()
    assert store.digest("rel/a.txt") == first
    again = store.snapshot({"rel/a.txt": b"two"})
    assert [row.name for row in again.files] == ["rel/a.txt"]
    assert _file(again.files, 0).sha256 == second
    assert [row.name for row in again.fence.files] == ["b.txt", "rel/a.txt"]
    assert store.read("rel/a.txt") == b"two"
    assert store.rollback("rel/a.txt") == b"one"
    assert store.rollback("rel/a.txt") == b"one"
    assert store.read("b.txt") == b"side"

    def no_prior() -> bytes:
        return store.rollback("b.txt")

    assert _code(no_prior) == "NO_PRIOR"
    before = len(store.fences())
    same = store.snapshot({"rel/a.txt": b"two"})
    assert _file(same.files, 0).sha256 == second
    assert len(store.fences()) == before
    assert same.fence == _fence(store.fences(), before - 1)
    assert store.rollback("rel/a.txt") == b"one"
    store.snapshot({"rel/a.txt": b"three"})
    assert store.read("rel/a.txt") == b"three"
    assert store.rollback("rel/a.txt") == b"two"
    assert hashlib.sha256(store.rollback("rel/a.txt")).hexdigest() == second
    listed = store.catalog()
    assert [row.name for row in listed] == ["b.txt", "rel/a.txt"]
    assert "one" not in repr(listed)
    assert "two" not in repr(store.policy)
    assert len(store.fences()) == 3
    assert _sha_of(_fence(store.fences(), 1).files, "rel/a.txt") == second
    restored = checkpoints.rebuild(store.records())
    assert restored.files == store.catalog()
    assert restored.fences == store.fences()
    assert checkpoints.rebuild(store.fences()).files == listed


def test_third_step_rolls_back_to_step_two() -> None:
    store = checkpoints.Checkpoints(max_file_bytes=4, max_total_bytes=8)
    store.snapshot({"n": b"aaaa"})
    store.snapshot({"n": b"bbbb"})
    store.snapshot({"n": b"cccc"})
    assert store.read("n") == b"cccc"
    assert store.rollback("n") == b"bbbb"
    assert hashlib.sha256(b"aaaa").hexdigest() == _sha_of(_fence(store.fences(), 0).files, "n")
    assert store.rollback("n") != b"aaaa"


def test_example_checkpoints() -> None:
    first = _example()
    second = _example()
    assert first == second
    rolled, current, digest, catalog, fences = first
    assert rolled == b"note under the light"
    assert rolled != b"note beside the lamp"
    assert current == b"note filed with the card"
    assert digest == hashlib.sha256(current).hexdigest()
    assert _file(catalog, 0).name == "session/card.txt"
    assert len(fences) == 3
    oldest = _fence(fences, 0)
    middle = _fence(fences, 1)
    newest = _fence(fences, 2)
    assert oldest.prev == checkpoints.GENESIS
    assert middle.prev == oldest.sha
    assert newest.prev == middle.sha
    assert _sha_of(oldest.files, "session/card.txt") == hashlib.sha256(
        b"note beside the lamp"
    ).hexdigest()
    assert hashlib.sha256(rolled).hexdigest() == _sha_of(middle.files, "session/card.txt")
    assert "light" not in repr(fences)
    assert "lamp" not in repr(catalog)


def _example() -> tuple[
    bytes,
    bytes,
    str,
    tuple[checkpoints.FileRecord, ...],
    tuple[checkpoints.Fence, ...],
]:
    store = checkpoints.Checkpoints()
    path = "session/card.txt"
    store.snapshot({path: b"note beside the lamp"})
    store.snapshot({path: b"note under the light"})
    store.snapshot({path: b"note filed with the card"})
    rolled = store.rollback(path)
    again = store.rollback(path)
    assert rolled == again
    current = store.read(path)
    live = checkpoints.rebuild(store.fences())
    text = checkpoints.rebuild(store.records())
    assert live.files == store.catalog()
    assert live.fences == store.fences()
    assert text.files == live.files
    assert text.fences == live.fences
    return (rolled, current, store.digest(path), store.catalog(), store.fences())


def test_bad_names() -> None:
    store = checkpoints.Checkpoints()
    samples = [
        "/etc/passwd",
        "C:/Windows/note",
        "C:note",
        "../secret",
        "foo/../../etc/passwd",
        "foo\\bar",
        "\\\\server\\share",
        "foo//bar",
        "foo/",
        "",
        "ok/%2e%2e/passwd",
        "dir/%5Cetc",
    ]

    def refuse_name(name: str) -> str:
        def run() -> None:
            store.snapshot({name: b"x"})

        return _code(run)

    for name in samples:
        assert refuse_name(name) == "BAD_NAME"

    def bad_rollback() -> bytes:
        return store.rollback("../secret")

    assert _code(bad_rollback) == "BAD_NAME"
    kept = store.snapshot({"./note.txt": b"ok"})
    assert _file(kept.files, 0).name == "./note.txt"
    assert store.read("./note.txt") == b"ok"


def test_unknown_name() -> None:
    store = checkpoints.Checkpoints()
    store.snapshot({"a": b"1"})

    def roll() -> bytes:
        return store.rollback("missing")

    def read() -> bytes:
        return store.read("missing")

    def digest() -> str:
        return store.digest("missing")

    assert _code(roll) == "NO_SNAPSHOT"
    assert _code(read) == "NO_SNAPSHOT"
    assert _code(digest) == "NO_SNAPSHOT"


def test_single_snapshot_has_no_prior() -> None:
    store = checkpoints.Checkpoints()
    store.snapshot({"a": b"only"})

    def roll() -> bytes:
        return store.rollback("a")

    assert _code(roll) == "NO_PRIOR"


def test_other_refusals() -> None:
    store = checkpoints.Checkpoints()

    def not_map_none() -> None:
        store.snapshot(cast(dict[str, bytes], None))

    def not_map_pairs() -> None:
        store.snapshot(cast(dict[str, bytes], [("a", b"b")]))

    def empty() -> None:
        store.snapshot({})

    def not_text() -> None:
        store.snapshot(cast(dict[str, bytes], {3: b"a"}))

    def not_bytes() -> None:
        store.snapshot({"a": cast(bytes, "text")})

    def nul_name() -> None:
        store.snapshot({"a\x00b": b"z"})

    def nul_encoded() -> None:
        store.snapshot({"a%00b": b"z"})

    def oversize_name() -> None:
        store.snapshot({"n" * (checkpoints.POLICY_MAX_NAME + 1): b"z"})

    def bad_files() -> None:
        checkpoints.Checkpoints(max_files=0)

    def bad_total() -> None:
        checkpoints.Checkpoints(max_total_bytes=-3)

    def bad_history() -> None:
        checkpoints.Checkpoints(history=True)

    def bad_generations() -> None:
        checkpoints.Checkpoints(max_generations=0)

    def bad_type() -> None:
        checkpoints.Checkpoints(max_files=cast(int, "9"))

    assert _code(not_map_none) == "NOT_MAP"
    assert _code(not_map_pairs) == "NOT_MAP"
    assert _code(empty) == "EMPTY"
    assert _code(not_text) == "NOT_TEXT"
    assert _code(not_bytes) == "NOT_BYTES"
    assert _code(nul_name) == "NULL_BYTE"
    assert _code(nul_encoded) == "NULL_BYTE"
    assert _code(oversize_name) == "OVERSIZE"
    small = checkpoints.Checkpoints(max_file_bytes=4)

    def oversize_bytes() -> None:
        small.snapshot({"a": b"12345"})

    assert _code(oversize_bytes) == "OVERSIZE"
    assert _code(bad_files) == "BAD_LIMIT"
    assert _code(bad_total) == "BAD_LIMIT"
    assert _code(bad_history) == "NOT_INT"
    assert _code(bad_generations) == "BAD_LIMIT"
    assert _code(bad_type) == "NOT_INT"
    assert store.catalog() == ()


def test_secret_refuses_and_stays_out_of_repr() -> None:
    store = checkpoints.Checkpoints()
    store.snapshot({"keep.txt": b"safe"})
    key = b"sk-livekeyvalue"

    def body() -> None:
        store.snapshot({"keep.txt": b"next", "b": key})

    def named() -> None:
        store.snapshot({"sk-livekeyvalue": b"a"})

    def assigned() -> None:
        store.snapshot({"note": b"api_key=supersecret"})

    def bearer() -> None:
        store.snapshot({"note": b"Bearer abcdefghijk"})

    def split_nul() -> None:
        store.snapshot({"x": b"sk-live\x00keyvalue"})

    assert _code(body) == "SECRET"
    assert _code(named) == "SECRET"
    assert _code(assigned) == "SECRET"
    assert _code(bearer) == "SECRET"
    assert _code(split_nul) == "SECRET"
    assert store.read("keep.txt") == b"safe"
    visible = repr(store.catalog()) + repr(store.policy) + repr(store) + repr(store.fences())
    assert "sk-livekeyvalue" not in visible
    assert "supersecret" not in visible
    assert "abcdefghijk" not in visible


def test_bad_batch_does_not_commit() -> None:
    store = checkpoints.Checkpoints()
    store.snapshot({"keep.txt": b"v1"})

    def bad() -> None:
        store.snapshot({"keep.txt": b"v2", "../x": b"no"})

    assert _code(bad) == "BAD_NAME"
    assert store.read("keep.txt") == b"v1"

    def no_prior() -> bytes:
        return store.rollback("keep.txt")

    assert _code(no_prior) == "NO_PRIOR"
    assert len(store.fences()) == 1


def test_duplicate_alias_does_not_commit() -> None:
    store = checkpoints.Checkpoints()
    store.snapshot({"keep.txt": b"v1"})

    def dup() -> None:
        store.snapshot({"keep.txt": b"v2", "%6beep.txt": b"no"})

    assert _code(dup) == "DUP"
    assert store.read("keep.txt") == b"v1"

    def no_prior() -> bytes:
        return store.rollback("keep.txt")

    assert _code(no_prior) == "NO_PRIOR"
    row = checkpoints.FileRecord("note.txt", "ab" * 32, 1)

    def dup_rows() -> None:
        checkpoints.Fence(
            index=1,
            prev=checkpoints.GENESIS,
            files=(row, row),
            sha="cd" * 32,
        )

    assert _code(dup_rows) == "DUP"


def test_cap_is_policy_and_lower_cap_holds() -> None:
    huge = checkpoints.Checkpoints(
        max_files=10_000,
        max_file_bytes=50_000_000,
        max_total_bytes=80_000_000,
        history=40,
        max_generations=10_000,
    )
    assert huge.policy.max_files == checkpoints.POLICY_MAX_FILES
    assert huge.policy.max_file_bytes == checkpoints.POLICY_MAX_FILE_BYTES
    assert huge.policy.max_total_bytes == checkpoints.POLICY_MAX_TOTAL_BYTES
    assert huge.policy.history == checkpoints.POLICY_HISTORY
    assert huge.policy.max_generations == checkpoints.POLICY_MAX_GENERATIONS

    def over_file() -> None:
        huge.snapshot({"a.bin": b"q" * (huge.policy.max_file_bytes + 1)})

    assert _code(over_file) == "OVERSIZE"
    taken = huge.snapshot({"a.bin": b"q"})
    assert taken.policy.history == checkpoints.POLICY_HISTORY
    assert taken.policy.max_generations == checkpoints.POLICY_MAX_GENERATIONS
    small = checkpoints.Checkpoints(max_files=1, max_file_bytes=4, max_total_bytes=4)
    assert small.policy.max_files == 1
    assert small.policy.max_file_bytes == 4
    got = small.snapshot({"a": b"wxyz"})
    assert got.policy == small.policy
    assert small.read("a") == b"wxyz"

    def two_names() -> None:
        small.snapshot({"a": b"ab", "b": b"cd"})

    def new_name() -> None:
        small.snapshot({"b": b"q"})

    assert _code(two_names) == "CAP"
    assert _code(new_name) == "CAP"
    assert small.read("a") == b"wxyz"
    tight = checkpoints.Checkpoints(max_files=3, max_file_bytes=8, max_total_bytes=5)
    tight.snapshot({"a": b"123"})

    def grow() -> None:
        tight.snapshot({"a": b"456"})

    assert _code(grow) == "CAP"
    assert tight.read("a") == b"123"

    def tight_roll() -> bytes:
        return tight.rollback("a")

    assert _code(tight_roll) == "NO_PRIOR"

    def default_ceiling() -> None:
        payload = {
            f"f{index:02d}.txt": b"x" for index in range(checkpoints.POLICY_MAX_FILES + 1)
        }
        checkpoints.Checkpoints().snapshot(payload)

    assert _code(default_ceiling) == "CAP"


def test_generation_cap_blocks_the_next_write() -> None:
    store = checkpoints.Checkpoints(max_generations=2)
    store.snapshot({"session/card.txt": b"one"})
    store.snapshot({"session/card.txt": b"two"})

    def third() -> None:
        store.snapshot({"session/card.txt": b"three"})

    assert _code(third) == "CAP"
    assert store.read("session/card.txt") == b"two"
    assert store.rollback("session/card.txt") == b"one"
    assert len(store.fences()) == 2
    same = store.snapshot({"session/card.txt": b"two"})
    assert same.fence.index == 2
    assert len(store.fences()) == 2


def test_binary_bytes_are_copied() -> None:
    store = checkpoints.Checkpoints()
    buf = bytearray(b"a\x00c")
    store.snapshot({"bin.dat": cast(bytes, buf)})
    store.snapshot({"raw.bin": b"\xff\xfe"})
    assert store.read("raw.bin") == b"\xff\xfe"
    buf[0] = ord("z")
    assert store.read("bin.dat") == b"a\x00c"
    store.snapshot({"bin.dat": b"next"})
    assert store.rollback("bin.dat") == b"a\x00c"


def test_hash_mismatch_and_stale_fence() -> None:
    store = checkpoints.Checkpoints()
    store.snapshot({"note.txt": b"alpha"})
    store.snapshot({"note.txt": b"beta"})
    store.snapshot({"note.txt": b"gamma"})
    fences = store.fences()
    good = _fence(fences, 0)

    def mismatch() -> None:
        checkpoints.Fence(
            index=good.index,
            prev=good.prev,
            files=good.files,
            sha="ab" * 32,
        )

    assert _code(mismatch) == "CHAIN"
    raw = store.records()
    head, _sep, tail = raw[0].partition("\n")
    bits = head.split("\t")
    bits[2] = "ab" * 32
    tampered = "\t".join(bits) + "\n" + tail

    def tampered_chain() -> None:
        checkpoints.rebuild((tampered,))

    assert _code(tampered_chain) == "CHAIN"

    def skip_middle() -> None:
        checkpoints.rebuild((_fence(fences, 0), _fence(fences, 2)))

    assert _code(skip_middle) == "STALE"

    def empty_chain() -> None:
        checkpoints.rebuild(())

    assert _code(empty_chain) == "EMPTY"


def test_malformed_records_are_refuse() -> None:
    samples: tuple[object, ...] = (
        None,
        "nope",
        b"nope",
        object(),
        ("²",),
        ("",),
        ("1\tzz",),
        (1, 2, 3),
        ("AB" * 32,),
    )
    for sample in samples:
        try:
            checkpoints.rebuild(sample)
        except Refuse as caught:
            assert caught.code == "BAD_RECORD"
        except (ValueError, KeyError, IndexError, UnicodeDecodeError) as exc:
            raise AssertionError(type(exc).__name__) from exc
        else:
            raise AssertionError("expected Refuse")

    def bad_sha() -> None:
        checkpoints.FileRecord("note.txt", "nope", 1)

    def bad_size() -> None:
        checkpoints.FileRecord("note.txt", "ab" * 32, cast(int, "3"))

    def negative_size() -> None:
        checkpoints.FileRecord("note.txt", "ab" * 32, -1)

    def bool_size() -> None:
        checkpoints.FileRecord("note.txt", "ab" * 32, cast(int, True))

    def bool_index() -> None:
        checkpoints.Fence(
            index=cast(int, True),
            prev=checkpoints.GENESIS,
            files=(checkpoints.FileRecord("note.txt", "ab" * 32, 1),),
            sha="cd" * 32,
        )

    def unsorted() -> None:
        later = checkpoints.FileRecord("b.txt", "ab" * 32, 1)
        earlier = checkpoints.FileRecord("a.txt", "cd" * 32, 1)
        checkpoints.Fence(
            index=1,
            prev=checkpoints.GENESIS,
            files=(later, earlier),
            sha="ef" * 32,
        )

    def empty_files() -> None:
        checkpoints.Fence(index=1, prev=checkpoints.GENESIS, files=(), sha="ab" * 32)

    assert _code(bad_sha) == "BAD_RECORD"
    assert _code(bad_size) == "BAD_RECORD"
    assert _code(negative_size) == "BAD_RECORD"
    assert _code(bool_size) == "NOT_INT"
    assert _code(bool_index) == "NOT_INT"
    assert _code(unsorted) == "BAD_RECORD"
    assert _code(empty_files) == "BAD_RECORD"

    def too_many_rows() -> None:
        rows = tuple(
            checkpoints.FileRecord(f"f{index:02d}.txt", "ab" * 32, 1)
            for index in range(checkpoints.POLICY_MAX_FILES + 1)
        )
        checkpoints.Fence(index=1, prev=checkpoints.GENESIS, files=rows, sha="cd" * 32)

    assert _code(too_many_rows) == "CAP"

    def wrong_schema() -> None:
        checkpoints.Chain(schema="other", fences=(), files=())

    assert _code(wrong_schema) == "BAD_RECORD"
