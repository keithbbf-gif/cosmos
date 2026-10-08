"""Projection tests for built-in memory and one external provider."""

from __future__ import annotations

import shutil
import tempfile
from dataclasses import replace
from pathlib import Path

import pytest

from cosmos_hermes import Refuse, secret_shape
from memory_providers import (
    BUDGET,
    GENESIS,
    INPUT_CAP,
    POLICY_CAP,
    PROVIDERS,
    SCHEMA,
    TEXT_CAP,
    Binding,
    Fact,
    Hit,
    Lookup,
    MemoryProviders,
    Note,
    Prefetch,
    ProviderStatus,
    SearchResult,
    Snapshot,
    assemble,
    probe_index,
)


def _row(rows: tuple[Hit, ...], index: int) -> Hit:
    if index < 0 or index >= len(rows):
        raise AssertionError("missing row")
    return rows[index]


def _fact_at(rows: tuple[Fact, ...], index: int) -> Fact:
    if index < 0 or index >= len(rows):
        raise AssertionError("missing fact")
    return rows[index]


def _status_at(rows: tuple[ProviderStatus, ...], index: int) -> ProviderStatus:
    if index < 0 or index >= len(rows):
        raise AssertionError("missing status")
    return rows[index]


def _builtin_board() -> MemoryProviders:
    board = MemoryProviders()
    board.rebuild(assemble((Binding("builtin", ""),), ()))
    return board


def _pair() -> MemoryProviders:
    board = MemoryProviders()
    board.rebuild(
        assemble(
            (Binding("builtin", ""), Binding("honcho", "cred-honcho")),
            (),
        )
    )
    return board


def test_schema_and_provider_names() -> None:
    assert SCHEMA == "cosmos-hermes-memory_providers/1"
    assert PROVIDERS == (
        "builtin",
        "honcho",
        "openviking",
        "mem0",
        "holographic",
        "retaindb",
        "byterover",
        "supermemory",
        "hindsight",
    )
    assert POLICY_CAP == 8
    assert BUDGET == 512
    assert len(GENESIS) == 64


def test_missing_index_is_unmeasured() -> None:
    board = MemoryProviders()
    assert "measured=False" in repr(board)
    with pytest.raises(Refuse) as looked:
        board.lookup("builtin")
    assert looked.value.code == "UNMEASURED"
    with pytest.raises(Refuse) as status:
        board.status()
    assert status.value.code == "UNMEASURED"
    with pytest.raises(Refuse) as exported:
        board.export()
    assert exported.value.code == "UNMEASURED"
    with pytest.raises(Refuse) as searched:
        board.search("builtin", "tea card")
    assert searched.value.code == "UNMEASURED"
    with pytest.raises(Refuse) as external:
        _ = board.external
    assert external.value.code == "UNMEASURED"
    with pytest.raises(Refuse) as generation:
        _ = board.generation
    assert generation.value.code == "UNMEASURED"
    with pytest.raises(Refuse) as held:
        board.holds_credential("builtin", "")
    assert held.value.code == "UNMEASURED"


def test_configure_does_not_create_an_index() -> None:
    board = MemoryProviders()
    with pytest.raises(Refuse) as caught:
        board.configure("honcho", "cred-honcho", seen=0)
    assert caught.value.code == "UNMEASURED"
    assert "measured=False" in repr(board)


def test_two_configured_third_name_refuses() -> None:
    board = _pair()
    assert board.external == "honcho"
    named = tuple(item.name for item in board.status())
    assert named == ("builtin", "honcho")
    with pytest.raises(Refuse) as looked:
        board.lookup("mem0")
    assert looked.value.code == "UNMEASURED"
    with pytest.raises(Refuse) as searched:
        board.search("mem0", "tea card")
    assert searched.value.code == "UNMEASURED"
    with pytest.raises(Refuse) as remembered:
        board.remember("mem0", "tea card", seen=0)
    assert remembered.value.code == "UNMEASURED"
    assert board.generation == 0


def test_measured_miss_is_empty() -> None:
    board = _builtin_board()
    found = board.search("builtin", "absent phrase")
    assert found.rows == ()
    assert found.cap == POLICY_CAP
    assert found.generation == 0
    assert found.provider == "builtin"
    assert found.satellite is False


def test_each_external_name_is_satellite() -> None:
    for name in PROVIDERS:
        if name == "builtin":
            continue
        board = MemoryProviders()
        board.rebuild(assemble((Binding("builtin", ""), Binding(name, f"cred-{name}")), ()))
        found = board.lookup(name)
        assert found.satellite is True
        assert found.name == name
        assert board.external == name
        assert board.holds_credential(name, f"cred-{name}") is True
        assert board.holds_credential(name, "cred-other") is False


def test_remember_mirrors_builtin_and_forget_stops_at_satellite() -> None:
    board = _pair()
    primary = board.remember("builtin", "tea card", session="kitchen-morning", seen=0)
    assert primary.satellite is False
    assert primary.entry_id == "mem-000001"
    mirror = _row(board.lookup("honcho").rows, 0)
    assert mirror.satellite is True
    assert mirror.text == "tea card"
    assert mirror.entry_id == "mem-000002"
    removed = board.forget("builtin", primary.entry_id, seen=1)
    assert removed.entry_id == primary.entry_id
    assert board.lookup("builtin").rows == ()
    assert _row(board.lookup("honcho").rows, 0).text == "tea card"
    with pytest.raises(Refuse) as satellite:
        board.forget("honcho", mirror.entry_id, seen=2)
    assert satellite.value.code == "SATELLITE"
    assert board.generation == 2
    with pytest.raises(Refuse) as absent:
        board.forget("builtin", "mem-000099", seen=2)
    assert absent.value.code == "ABSENT"
    with pytest.raises(Refuse) as malformed:
        board.forget("builtin", "nope", seen=2)
    assert malformed.value.code == "ABSENT"
    assert board.generation == 2


def test_second_external_replaces_the_first() -> None:
    board = _pair()
    board.remember("honcho", "pendant light", session="kitchen-morning", seen=0)
    status = board.configure("hindsight", "cred-hindsight", seen=1)
    assert status.name == "hindsight"
    assert status.satellite is True
    assert board.external == "hindsight"
    with pytest.raises(Refuse) as caught:
        board.lookup("honcho")
    assert caught.value.code == "UNMEASURED"
    assert board.holds_credential("hindsight", "cred-hindsight") is True
    assert board.holds_credential("hindsight", "cred-honcho") is False
    with pytest.raises(Refuse) as old:
        board.holds_credential("honcho", "cred-honcho")
    assert old.value.code == "UNMEASURED"
    same = board.configure("hindsight", "cred-hindsight", seen=board.generation)
    assert same.generation == board.generation


def test_same_configure_keeps_the_fence() -> None:
    board = _pair()
    status = board.configure("honcho", "cred-honcho", seen=0)
    assert status.generation == 0
    assert board.generation == 0
    assert board.holds_credential("builtin", "") is True


def test_sync_turn_is_a_descriptor() -> None:
    board = _pair()
    plan = board.sync_turn("kitchen-morning", "Mina warmed the pendant light", seen=0)
    assert plan.executed is False
    assert plan.providers == ("builtin", "honcho")
    assert plan.entry_ids == ("mem-000001", "mem-000002")
    assert plan.generation == 1
    assert _row(board.lookup("builtin").rows, 0).satellite is False
    assert _row(board.lookup("honcho").rows, 0).satellite is True
    assert _row(board.lookup("honcho").rows, 0).text == "Mina warmed the pendant light"
    assert "executed=False" in repr(plan)
    assert "Mina warmed" not in repr(plan)


def test_cap_ignores_a_higher_request() -> None:
    notes = tuple(Note("builtin", "desk", f"row-{index}") for index in range(POLICY_CAP + 5))
    board = MemoryProviders()
    board.rebuild(assemble((Binding("builtin", ""),), notes))
    raised = board.search("builtin", "row", limit=POLICY_CAP + 100)
    assert raised.cap == POLICY_CAP
    assert raised.applied == POLICY_CAP
    assert raised.budget == BUDGET
    assert len(raised.rows) == POLICY_CAP
    assert tuple(row.text for row in raised.rows) == tuple(f"row-{index}" for index in range(POLICY_CAP))
    trimmed = board.search("builtin", "row", limit=2)
    assert trimmed.cap == POLICY_CAP
    assert trimmed.applied == 2
    assert tuple(row.text for row in trimmed.rows) == ("row-0", "row-1")
    assert board.cap == POLICY_CAP


def test_query_keeps_matching_rows_in_order() -> None:
    board = MemoryProviders()
    board.rebuild(
        assemble(
            (Binding("builtin", ""),),
            (
                Note("builtin", "desk", "alpha"),
                Note("builtin", "desk", "beta"),
                Note("builtin", "desk", "alpine"),
            ),
        )
    )
    found = board.search("builtin", "ALP")
    assert tuple(row.text for row in found.rows) == ("alpha", "alpine")
    assert found.satellite is False


def test_budget_skips_without_stopping() -> None:
    huge = "x" + ("A" * 600)
    later = "x" + ("b" * 20)
    mid = "x" + ("C" * 400)
    board = MemoryProviders()
    board.rebuild(
        assemble(
            (Binding("builtin", ""), Binding("honcho", "cred-honcho")),
            (
                Note("builtin", "desk", mid),
                Note("honcho", "desk", huge),
                Note("builtin", "desk", later),
            ),
        )
    )
    found = board.prefetch("x", limit=POLICY_CAP + 5)
    assert found.providers == ("builtin", "honcho")
    assert found.cap == POLICY_CAP
    assert found.applied == POLICY_CAP
    assert found.budget == BUDGET
    assert tuple(row.text for row in found.rows) == (mid, later)
    assert found.spent == len(mid) + len(later)
    wide = MemoryProviders()
    wide.rebuild(
        assemble(
            (Binding("builtin", ""),),
            (Note("builtin", "desk", huge), Note("builtin", "desk", later)),
        )
    )
    scanned = wide.search("builtin", "x")
    assert tuple(row.text for row in scanned.rows) == (later,)
    assert scanned.spent == len(later)


def test_unknown_provider() -> None:
    board = _pair()
    with pytest.raises(Refuse) as looked:
        board.lookup("Honcho")
    assert looked.value.code == "UNKNOWN_PROVIDER"
    with pytest.raises(Refuse) as remembered:
        board.remember("memori", "tea card", seen=0)
    assert remembered.value.code == "UNKNOWN_PROVIDER"
    with pytest.raises(Refuse) as configured:
        board.configure("memori", "cred-memori", seen=0)
    assert configured.value.code == "UNKNOWN_PROVIDER"
    assert board.generation == 0


def test_secret_shape_refuses() -> None:
    board = _builtin_board()
    samples = (
        "sk-livekeyvalue",
        "Authorization: Bearer abcdefghijk",
        "api_key=supersecretvalue",
    )
    for sample in samples:
        assert secret_shape(sample)
        with pytest.raises(Refuse) as remembered:
            board.remember("builtin", sample, seen=0)
        assert remembered.value.code == "SECRET"
        assert secret_shape(str(remembered.value)) is False
        with pytest.raises(Refuse) as searched:
            board.search("builtin", sample)
        assert searched.value.code == "SECRET"
    with pytest.raises(Refuse) as configured:
        board.configure("honcho", "sk-livekeyvalue", seen=0)
    assert configured.value.code == "SECRET"
    assert board.external is None
    assert board.generation == 0


def test_builtin_rejects_a_credential() -> None:
    with pytest.raises(Refuse) as assembled:
        assemble((Binding("builtin", "cred-builtin"),), ())
    assert assembled.value.code == "LOCAL_ONLY"
    board = _builtin_board()
    with pytest.raises(Refuse) as configured:
        board.configure("builtin", "cred-builtin", seen=0)
    assert configured.value.code == "LOCAL_ONLY"
    assert board.generation == 0
    kept = board.configure("builtin", "", seen=0)
    assert kept.name == "builtin"
    assert kept.satellite is False
    assert board.generation == 0


def test_empty_text_and_query() -> None:
    board = _builtin_board()
    with pytest.raises(Refuse) as remembered:
        board.remember("builtin", "   ", seen=0)
    assert remembered.value.code == "EMPTY"
    with pytest.raises(Refuse) as searched:
        board.search("builtin", "   ")
    assert searched.value.code == "EMPTY"
    with pytest.raises(Refuse) as synced:
        board.sync_turn("   ", "hello", seen=0)
    assert synced.value.code == "EMPTY"
    assert board.generation == 0


def test_limit_and_fence_types() -> None:
    board = _builtin_board()
    with pytest.raises(Refuse) as boolean:
        board.search("builtin", "tea", limit=True)
    assert boolean.value.code == "NOT_INT"
    with pytest.raises(Refuse) as zero:
        board.search("builtin", "tea", limit=0)
    assert zero.value.code == "OUT_OF_RANGE"
    with pytest.raises(Refuse) as seen:
        board.remember("builtin", "tea card", seen=True)
    assert seen.value.code == "NOT_INT"
    with pytest.raises(Refuse) as negative:
        board.remember("builtin", "tea card", seen=-1)
    assert negative.value.code == "OUT_OF_RANGE"
    assert board.generation == 0


def test_text_bounds() -> None:
    board = _builtin_board()
    with pytest.raises(Refuse) as text:
        board.remember("builtin", 12, seen=0)
    assert text.value.code == "NOT_TEXT"
    with pytest.raises(Refuse) as nul:
        board.remember("builtin", "a\x00b", seen=0)
    assert nul.value.code == "NULL_BYTE"
    with pytest.raises(Refuse) as over:
        board.remember("builtin", "x" * (TEXT_CAP + 1), seen=0)
    assert over.value.code == "OVERSIZE"
    notes = tuple(Note("builtin", "desk", f"n{index}") for index in range(INPUT_CAP + 1))
    with pytest.raises(Refuse) as many:
        assemble((Binding("builtin", ""),), notes)
    assert many.value.code == "OVERSIZE"
    with pytest.raises(Refuse) as wide:
        board.search("builtin", " ".join(["a"] * 17))
    assert wide.value.code == "OVERSIZE"
    assert board.generation == 0


def test_stale_fence_does_not_apply() -> None:
    board = _builtin_board()
    board.remember("builtin", "tea card", session="kitchen-morning", seen=0)
    assert board.generation == 1
    with pytest.raises(Refuse) as caught:
        board.remember("builtin", "another card", session="kitchen-morning", seen=0)
    assert caught.value.code == "STALE"
    assert board.generation == 1
    assert _status_at(board.status(), 0).count == 1


def test_duplicate_entry_id_refuses() -> None:
    fact = Fact("builtin", "mem-000001", "desk", "tea card", False, GENESIS)
    snap = Snapshot(SCHEMA, (Binding("builtin", ""),), (fact, fact), 0, 2, GENESIS)
    board = MemoryProviders()
    with pytest.raises(Refuse) as caught:
        board.rebuild(snap)
    assert caught.value.code == "DUPLICATE"
    with pytest.raises(Refuse) as cold:
        board.lookup("builtin")
    assert cold.value.code == "UNMEASURED"


def test_broken_chain_keeps_the_prior_snapshot() -> None:
    board = _builtin_board()
    board.remember("builtin", "tea card", session="desk", seen=0)
    good = board.export()
    broken = replace(good, tip="f" * 64)
    with pytest.raises(Refuse) as caught:
        board.rebuild(broken)
    assert caught.value.code == "BROKEN_CHAIN"
    assert board.export() == good
    fresh = MemoryProviders()
    with pytest.raises(Refuse) as again:
        fresh.rebuild(broken)
    assert again.value.code == "BROKEN_CHAIN"
    with pytest.raises(Refuse) as cold:
        fresh.status()
    assert cold.value.code == "UNMEASURED"


def test_tampered_link_is_a_broken_chain() -> None:
    snap = assemble((Binding("builtin", ""),), (Note("builtin", "desk", "tea card"),))
    fact = _fact_at(snap.facts, 0)
    tampered = replace(snap, facts=(replace(fact, link="e" * 64),))
    board = MemoryProviders()
    with pytest.raises(Refuse) as caught:
        board.rebuild(tampered)
    assert caught.value.code == "BROKEN_CHAIN"


def test_snapshot_shape() -> None:
    builtin = (Binding("builtin", ""),)
    with pytest.raises(Refuse) as rows:
        assemble(builtin, "alpha")
    assert rows.value.code == "NOT_ROWS"
    with pytest.raises(Refuse) as bad:
        assemble("builtin", ())
    assert bad.value.code == "BAD_SNAPSHOT"
    with pytest.raises(Refuse) as missing:
        assemble((Binding("honcho", "cred-honcho"),), ())
    assert missing.value.code == "MISSING_BUILTIN"
    with pytest.raises(Refuse) as conflict:
        assemble(
            (
                Binding("builtin", ""),
                Binding("honcho", "cred-honcho"),
                Binding("mem0", "cred-mem0"),
            ),
            (),
        )
    assert conflict.value.code == "CONFLICT"
    with pytest.raises(Refuse) as duplicate:
        assemble((Binding("builtin", ""), Binding("builtin", "")), ())
    assert duplicate.value.code == "DUPLICATE"
    with pytest.raises(Refuse) as third:
        assemble(
            (Binding("builtin", ""), Binding("honcho", "cred-honcho")),
            (Note("mem0", "kitchen-morning", "a tea card"),),
        )
    assert third.value.code == "UNMEASURED"
    snap = assemble(builtin, ())
    board = MemoryProviders()
    with pytest.raises(Refuse) as schema:
        board.rebuild(replace(snap, schema="nope"))
    assert schema.value.code == "BAD_SNAPSHOT"
    with pytest.raises(Refuse) as seq:
        board.rebuild(replace(snap, seq=0))
    assert seq.value.code == "BAD_SNAPSHOT"
    with pytest.raises(Refuse) as flag:
        board.rebuild(replace(snap, generation=True))
    assert flag.value.code == "BAD_SNAPSHOT"
    with pytest.raises(Refuse) as raw:
        board.rebuild(object())
    assert raw.value.code == "BAD_SNAPSHOT"
    assert "measured=False" in repr(board)


def test_rebuild_reproduces_public_state() -> None:
    board = _pair()
    board.remember("builtin", "tea card on the counter", session="kitchen-morning", seen=0)
    board.forget("builtin", "mem-000001", seen=1)
    board.configure("hindsight", "cred-hindsight", seen=2)
    exported = board.export()
    other = MemoryProviders()
    restored = other.rebuild(exported)
    assert restored == exported
    assert other.export() == exported
    assert other.status() == board.status()
    assert other.lookup("builtin") == board.lookup("builtin")
    assert other.lookup("hindsight") == board.lookup("hindsight")
    assert other.generation == board.generation
    assert other.external == "hindsight"
    with pytest.raises(Refuse) as caught:
        other.lookup("honcho")
    assert caught.value.code == "UNMEASURED"


def test_repr_hides_text_and_credentials() -> None:
    board = _pair()
    status = board.configure("honcho", "cred-honcho", seen=0)
    entry = board.remember("builtin", "tea card", session="kitchen-morning", seen=0)
    found = board.search("builtin", "tea", limit=2)
    blob = " ".join(
        (
            repr(board),
            repr(status),
            repr(entry),
            repr(found),
            repr(_row(found.rows, 0)),
            repr(board.export()),
            repr(board.prefetch("tea")),
            repr(board.lookup("honcho")),
            repr(Binding("honcho", "cred-honcho")),
            repr(Note("honcho", "kitchen-morning", "tea card")),
        )
    )
    assert "cred-honcho" not in blob
    assert "tea card" not in blob
    assert secret_shape(blob) is False


def test_probe_missing_index_creates_no_file() -> None:
    root = tempfile.mkdtemp(prefix="memprov-")
    try:
        missing = str(Path(root) / "memory.index")
        assert Path(missing).exists() is False
        with pytest.raises(Refuse) as caught:
            probe_index([root], missing)
        assert caught.value.code == "UNMEASURED"
        assert Path(missing).exists() is False
    finally:
        shutil.rmtree(root)


def test_probe_existing_file_is_not_authority() -> None:
    root = tempfile.mkdtemp(prefix="memprov-")
    try:
        present = Path(root) / "memory.index"
        payload = b"not-an-index"
        present.write_bytes(payload)
        with pytest.raises(Refuse) as caught:
            probe_index([root], str(present))
        assert caught.value.code == "FOREIGN_INDEX"
        assert present.read_bytes() == payload
    finally:
        shutil.rmtree(root)


def test_probe_path_shapes() -> None:
    root = tempfile.mkdtemp(prefix="memprov-")
    try:
        cases = (
            ("", "BAD_PATH"),
            ("file:///memory.index", "FILE_URL"),
            (root + "\\%2e%2e\\memory.index", "ENCODED_DOTDOT"),
            (root + "\\..\\memory.index", "DOTDOT"),
            ("\\\\nas\\memory\\index.db", "UNC"),
            ("C:\\", "DRIVE_ROOT"),
            ("C:memory.index", "DRIVE_RELATIVE"),
            ("C:\\memory:index.db", "ALT_STREAM"),
            (root + "\\memory.index.", "TRAILING_DOT"),
            ("memory.index", "RELATIVE_PATH"),
            ("C:\\Windows", "OUTSIDE_GRANT"),
        )
        for raw, code in cases:
            with pytest.raises(Refuse) as caught:
                probe_index([root], raw)
            assert caught.value.code == code
        with pytest.raises(Refuse) as relative_grant:
            probe_index(["memory"], str(Path(root) / "memory.index"))
        assert relative_grant.value.code == "RELATIVE_GRANT"
        secret_path = str(Path(root) / "sk-livekeyvalue")
        with pytest.raises(Refuse) as secret:
            probe_index([root], secret_path)
        assert secret.value.code == "SECRET"
        assert Path(secret_path).exists() is False
        with pytest.raises(Refuse) as empty:
            probe_index([], secret_path)
        assert empty.value.code == "NO_GRANT"
        with pytest.raises(Refuse) as text:
            probe_index([root], 12)
        assert text.value.code == "NOT_TEXT"
        with pytest.raises(Refuse) as huge:
            probe_index([root], "x" * 4097)
        assert huge.value.code == "OVERSIZE"
        with pytest.raises(Refuse) as nul:
            probe_index([root], "a\x00b")
        assert nul.value.code == "NULL_BYTE"
    finally:
        shutil.rmtree(root)


def _built(story: tuple[Snapshot, Lookup, Lookup, SearchResult, Prefetch, str]) -> Snapshot:
    return story[0]


def _honcho(story: tuple[Snapshot, Lookup, Lookup, SearchResult, Prefetch, str]) -> Lookup:
    return story[1]


def _local(story: tuple[Snapshot, Lookup, Lookup, SearchResult, Prefetch, str]) -> Lookup:
    return story[2]


def _found(story: tuple[Snapshot, Lookup, Lookup, SearchResult, Prefetch, str]) -> SearchResult:
    return story[3]


def _warm(story: tuple[Snapshot, Lookup, Lookup, SearchResult, Prefetch, str]) -> Prefetch:
    return story[4]


def _third(story: tuple[Snapshot, Lookup, Lookup, SearchResult, Prefetch, str]) -> str:
    return story[5]


def test_example_memory_providers() -> None:
    """Mina's tea card sits by the north window. The pendant light is a morning note."""

    def run() -> tuple[Snapshot, Lookup, Lookup, SearchResult, Prefetch, str]:
        board = MemoryProviders()
        snap = assemble(
            (Binding("builtin", ""), Binding("honcho", "cred-honcho-mina")),
            (
                Note("builtin", "kitchen-morning", "Mina left a tea card by the north window"),
                Note("honcho", "kitchen-morning", "Mina likes the pendant light warm"),
                Note("builtin", "kitchen-morning", "A short note says the sconce is for reading"),
            ),
        )
        built = board.rebuild(snap)
        honcho = board.lookup("honcho")
        local = board.lookup("builtin")
        found = board.search("builtin", "tea card", limit=4)
        warm = board.prefetch("pendant light", limit=4)
        third = ""
        try:
            board.lookup("mem0")
        except Refuse as refused:
            third = refused.code
        assert third == "UNMEASURED"
        assert board.external == "honcho"
        assert board.cap == POLICY_CAP
        assert board.holds_credential("honcho", "cred-honcho-mina") is True
        assert tuple(item.name for item in board.status()) == ("builtin", "honcho")
        return (built, honcho, local, found, warm, third)

    first = run()
    second = run()
    assert first == second
    honcho = _honcho(first)
    local = _local(first)
    found = _found(first)
    warm = _warm(first)
    assert _built(first).generation == 0
    assert _third(first) == "UNMEASURED"
    assert honcho.satellite is True
    assert _row(honcho.rows, 0).text == "Mina likes the pendant light warm"
    assert local.satellite is False
    assert tuple(row.text for row in local.rows) == (
        "Mina left a tea card by the north window",
        "A short note says the sconce is for reading",
    )
    assert _row(found.rows, 0).text == "Mina left a tea card by the north window"
    assert found.cap == POLICY_CAP
    assert tuple(row.text for row in warm.rows) == ("Mina likes the pendant light warm",)
    assert warm.providers == ("builtin", "honcho")
