"""Positive and negative controls for cosmos_lock. Runnable with pytest."""

from __future__ import annotations

import importlib
import subprocess
import sys
from pathlib import Path

import pytest

from cosmos.spikes.cosmos_lock.absence import (
    REQUIRED_ABSENCES,
    AbsenceKind,
    RefusalCode,
)
from cosmos.spikes.cosmos_lock.arbiter import Arbiter
from cosmos.spikes.cosmos_lock.clock import FrozenClock
from cosmos.spikes.cosmos_lock.demo import run_measured
from cosmos.spikes.cosmos_lock.identity import Stamp, WorkerIdentity
from cosmos.spikes.cosmos_lock.ingress import IngressEnvelope, write_envelope
from cosmos.spikes.cosmos_lock.ledger import sha256_hex
from cosmos.spikes.cosmos_lock.platform import (
    PathShape,
    PlatformAdapter,
    classify_path_shape,
    extended_win_path,
)


def _arbiter(
    tmp_path: Path,
    *,
    ttl: float = 30.0,
    skew: float = 60.0,
    reader=None,
) -> tuple[Arbiter, FrozenClock, WorkerIdentity, WorkerIdentity]:
    clock = FrozenClock()
    native = WorkerIdentity.mint("native-a", lane="native", attempt_id="att-1")
    other = WorkerIdentity.mint("native-b", lane="native", attempt_id="att-2")
    kwargs = {}
    if reader is not None:
        kwargs["byte_reader"] = reader
    built = Arbiter.instantiate(
        root=tmp_path / "core",
        clock=clock,
        service_key=b"test-service-key",
        installation_id="spike-test",
        adapter=PlatformAdapter(),
        ttl_seconds=ttl,
        max_skew_seconds=skew,
        **kwargs,
    )
    assert built.ok, built.reason
    arbiter = built.unwrap()
    arbiter.register_worker(native)
    arbiter.register_worker(other)
    return arbiter, clock, native, other


# ---------------------------------------------------------------------------
# POSITIVE controls
# ---------------------------------------------------------------------------


def test_positive_typed_absences_are_four_distinct_identities() -> None:
    kinds = list(REQUIRED_ABSENCES)
    assert kinds == [
        AbsenceKind.NOT_FOUND,
        AbsenceKind.OUT_OF_CLOCK,
        AbsenceKind.UNREADABLE,
        AbsenceKind.NOT_IN_RECORD,
    ]
    assert len({k.value for k in kinds}) == 4
    assert AbsenceKind.NOT_FOUND != AbsenceKind.OUT_OF_CLOCK
    assert AbsenceKind.NOT_FOUND != AbsenceKind.UNREADABLE
    assert AbsenceKind.NOT_FOUND != AbsenceKind.NOT_IN_RECORD
    assert AbsenceKind.OUT_OF_CLOCK != AbsenceKind.UNREADABLE
    assert AbsenceKind.OUT_OF_CLOCK != AbsenceKind.NOT_IN_RECORD
    assert AbsenceKind.UNREADABLE != AbsenceKind.NOT_IN_RECORD


def test_positive_grant_uses_arbiter_clock_and_monotonic_token(tmp_path: Path) -> None:
    arbiter, clock, native, other = _arbiter(tmp_path, ttl=90.0)
    first = arbiter.grant(native, "tree-write").unwrap()
    assert first.fencing_token == 1
    assert first.expires_at_epoch == pytest.approx(clock.epoch() + 90.0)
    holder = arbiter.current_holder("tree-write").unwrap()
    assert holder is not None
    assert holder.holder.worker_id == native.worker_id
    arbiter.release(first, native)
    second = arbiter.grant(other, "tree-write").unwrap()
    assert second.fencing_token == 2
    assert second.fencing_token > first.fencing_token


def test_positive_fenced_commit_accepts_current_token(tmp_path: Path) -> None:
    arbiter, _clock, native, _other = _arbiter(tmp_path)
    cap = arbiter.grant(
        native,
        "tree-write",
        expected_inputs={"manifest": "abc"},
    ).unwrap()
    result = arbiter.commit(
        worker=native,
        resource_id="tree-write",
        fencing_token=cap.fencing_token,
        artifact_bytes=b"protected-payload",
        expected_inputs={"manifest": "abc"},
    )
    assert result.ok, result.reason
    receipt = result.unwrap()
    assert receipt.artifact_sha256 == sha256_hex(b"protected-payload")
    assert (arbiter.cas_dir / receipt.cas_name).read_bytes() == b"protected-payload"
    assert arbiter.ledger.of_type("COMMIT_ACCEPTED")


def test_positive_dying_holder_recovery_without_cleanup(tmp_path: Path) -> None:
    arbiter, clock, native, other = _arbiter(tmp_path, ttl=10.0)
    cap = arbiter.grant(native, "tree-write").unwrap()
    del cap
    assert arbiter.release_calls == 0
    clock.advance(11)
    recovered = arbiter.grant(other, "tree-write")
    assert recovered.ok, recovered.reason
    assert arbiter.release_calls == 0
    assert recovered.unwrap().fencing_token == 2


def test_positive_takeover_chain_is_expired_then_granted(tmp_path: Path) -> None:
    arbiter, clock, native, other = _arbiter(tmp_path, ttl=5.0)
    arbiter.grant(native, "tree-write")
    clock.advance(6)
    arbiter.grant(other, "tree-write")
    chain = arbiter.takeover_chain("tree-write")
    assert chain == ["LEASE_GRANTED", "LEASE_EXPIRED", "LEASE_GRANTED"]
    expired = arbiter.ledger.of_type("LEASE_EXPIRED")
    granted = arbiter.ledger.of_type("LEASE_GRANTED")
    assert expired[0].payload["reason"] == "ARBITER_CLOCK"
    assert granted[1].payload["takeover"] is True
    assert granted[1].payload["supersedes_lease_id"] == expired[0].payload["lease_id"]


def test_positive_two_universes_only_native_holds(tmp_path: Path) -> None:
    arbiter, clock, native, _other = _arbiter(tmp_path)
    sandbox = WorkerIdentity.mint("sandbox-claimant", lane="sandbox")
    arbiter.register_worker(sandbox)
    cap = arbiter.grant(native, "tree-write").unwrap()
    fake = tmp_path / "sandbox" / r"V:\Ai\_queue\tree_lock.json"
    fake.parent.mkdir(parents=True)
    fake.write_text('{"holder":"sandbox","token":1}\n', encoding="utf-8")
    env = IngressEnvelope.build(
        sandbox,
        Stamp.from_clock(sandbox, clock, time_source=clock.source_name),
        {"resource_id": "tree-write", "invented_token": 1},
    )
    path = write_envelope(arbiter.ingress_dir, env)
    ingested = arbiter.ingest_ingress(path)
    assert ingested.ok
    holder = arbiter.current_holder("tree-write").unwrap()
    assert holder is not None
    assert holder.holder.worker_id == native.worker_id
    assert holder.fencing_token == cap.fencing_token
    sandbox_pub = arbiter.commit_from_ingress(
        env,
        resource_id="tree-write",
        fencing_token=1,
        artifact_bytes=b"nope",
    )
    assert sandbox_pub.code == RefusalCode.INGRESS_CANNOT_COMMIT.value
    held = arbiter.current_holder("tree-write").unwrap()
    assert held is not None
    assert held.holder.worker_id == native.worker_id


def test_positive_ingress_accepted_does_not_commit(tmp_path: Path) -> None:
    arbiter, clock, native, _other = _arbiter(tmp_path)
    sandbox = WorkerIdentity.mint("sandbox-claimant", lane="sandbox")
    arbiter.register_worker(sandbox)
    arbiter.grant(native, "tree-write")
    env = IngressEnvelope.build(
        sandbox,
        Stamp.from_clock(sandbox, clock, time_source=clock.source_name),
        {"please": "commit"},
    )
    arbiter.ingest_ingress(write_envelope(arbiter.ingress_dir, env))
    assert arbiter.ledger.of_type("INGRESS_ACCEPTED")
    assert not arbiter.ledger.of_type("COMMIT_ACCEPTED")


def test_positive_verify_unchanged_fingerprints(tmp_path: Path) -> None:
    watched = tmp_path / "watched.txt"
    watched.write_bytes(b"control-file-v1")
    arbiter, _clock, native, _other = _arbiter(tmp_path)
    arbiter.grant(native, "tree-write", watched={"control": watched})
    checks = arbiter.verify("tree-write", {"control": watched}).unwrap()
    assert checks == [
        checks[0].__class__(
            "control",
            "UNCHANGED",
            sha256_hex(b"control-file-v1"),
            sha256_hex(b"control-file-v1"),
        )
    ]


def test_positive_release_by_holder(tmp_path: Path) -> None:
    arbiter, _clock, native, other = _arbiter(tmp_path)
    cap = arbiter.grant(native, "tree-write").unwrap()
    released = arbiter.release(cap, native)
    assert released.ok
    assert arbiter.current_holder("tree-write").unwrap() is None
    assert arbiter.grant(other, "tree-write").ok


def test_positive_artifacts_carry_identity_and_offset_epoch(tmp_path: Path) -> None:
    arbiter, _clock, native, _other = _arbiter(tmp_path)
    arbiter.grant(native, "tree-write")
    event = arbiter.ledger.of_type("LEASE_GRANTED")[0]
    assert event.writer.worker_id == "cosmos-core"
    assert event.stamp.tz_offset.startswith(("+", "-"))
    assert ":" in event.stamp.tz_offset
    assert event.stamp.epoch_seconds > 0
    assert event.stamp.aware_iso
    assert event.payload["holder"]["worker_id"] == native.worker_id
    assert event.payload["holder"]["instance_id"] == native.instance_id


def test_positive_posix_advisory_lock(tmp_path: Path) -> None:
    adapter = PlatformAdapter()
    target = tmp_path / "advisory.lock"
    first = adapter.try_exclusive_lock(target)
    assert first.ok, first.reason
    second = adapter.try_exclusive_lock(target)
    assert not second.ok
    assert second.code == RefusalCode.ADVISORY_LOCK_HELD.value
    first.unwrap().release()
    third = adapter.try_exclusive_lock(target)
    assert third.ok
    third.unwrap().release()


def test_positive_posix_same_volume(tmp_path: Path) -> None:
    adapter = PlatformAdapter()
    a = tmp_path / "a"
    b = tmp_path / "b"
    a.write_text("x")
    b.write_text("y")
    same = adapter.same_volume(a, b)
    assert same.ok and same.unwrap() is True


def test_positive_reload_projection_from_ledger(tmp_path: Path) -> None:
    arbiter, clock, native, _other = _arbiter(tmp_path, ttl=60.0)
    cap = arbiter.grant(native, "tree-write").unwrap()
    rebuilt = Arbiter.instantiate(
        root=arbiter.root,
        clock=clock,
        service_key=b"test-service-key",
        installation_id="spike-test",
    ).unwrap()
    rebuilt.register_worker(native)
    holder = rebuilt.current_holder("tree-write").unwrap()
    assert holder is not None
    assert holder.fencing_token == cap.fencing_token
    assert rebuilt.commit(
        worker=native,
        resource_id="tree-write",
        fencing_token=cap.fencing_token,
        artifact_bytes=b"after-reload",
    ).ok


def test_positive_path_shape_detects_windows_drive() -> None:
    assert classify_path_shape(r"V:\Ai\BTS_MESH") is PathShape.WIN_DRIVE
    assert classify_path_shape(r"\\?\V:\Ai\COSMOS") is PathShape.WIN_EXTENDED
    assert classify_path_shape(r"\\server\share\x") is PathShape.WIN_UNC
    assert classify_path_shape("/workspace") is PathShape.POSIX_ABSOLUTE
    assert extended_win_path(r"V:\Ai\COSMOS") == r"\\?\V:\Ai\COSMOS"
    assert extended_win_path(r"\\server\share") == r"\\?\UNC\server\share"


def test_positive_demo_prints_measured(tmp_path: Path) -> None:
    lines = run_measured(tmp_path / "demo-root", ttl=8.0)
    joined = "\n".join(lines)
    assert "MEASURED grant_latency_ms=" in joined
    assert "MEASURED stale_token_refusal=STALE_TOKEN" in joined
    assert "MEASURED takeover_chain=LEASE_GRANTED,LEASE_EXPIRED,LEASE_GRANTED" in joined
    assert "MEASURED dying_holder_cleanup_calls=0" in joined
    assert "MEASURED two_universes_holders=1" in joined
    assert "MEASURED sandbox_commit=INGRESS_CANNOT_COMMIT" in joined
    assert "MEASURED torn_state=UNPARSEABLE:TORN_STATE" in joined
    assert "MEASURED job_objects=NATIVE_DEMO_REQUIRED" in joined


# ---------------------------------------------------------------------------
# NEGATIVE controls
# ---------------------------------------------------------------------------


def test_negative_stale_token_commit_refused_and_ledgered(tmp_path: Path) -> None:
    arbiter, clock, native, other = _arbiter(tmp_path, ttl=5.0)
    old = arbiter.grant(native, "tree-write").unwrap()
    clock.advance(6)
    arbiter.grant(other, "tree-write")
    result = arbiter.commit(
        worker=native,
        resource_id="tree-write",
        fencing_token=old.fencing_token,
        artifact_bytes=b"stale",
    )
    assert result.kind is AbsenceKind.REFUSED
    assert result.code == RefusalCode.STALE_TOKEN.value
    ledgered = arbiter.ledger.of_type("COMMIT_REFUSED")
    assert ledgered
    assert ledgered[-1].payload["code"] == "STALE_TOKEN"


def test_negative_torn_lease_mirror_refuses(tmp_path: Path) -> None:
    arbiter, _clock, _native, _other = _arbiter(tmp_path)
    torn = tmp_path / "torn.lease.json"
    torn.write_bytes(b"{")
    view = arbiter.read_lease_mirror(torn)
    assert view.kind is AbsenceKind.UNPARSEABLE
    assert view.code == RefusalCode.TORN_STATE.value
    assert "free" in view.reason


def test_negative_missing_mirror_is_not_free(tmp_path: Path) -> None:
    arbiter, _clock, _native, _other = _arbiter(tmp_path)
    view = arbiter.read_lease_mirror(tmp_path / "absent.lease.json")
    assert view.kind is AbsenceKind.NOT_FOUND
    assert view.kind is not AbsenceKind.UNREADABLE
    assert "not free" in view.reason


def test_negative_torn_ledger_refuses_new_grants(tmp_path: Path) -> None:
    arbiter, _clock, native, _other = _arbiter(tmp_path)
    arbiter.grant(native, "tree-write")
    with arbiter.ledger.path.open("ab") as handle:
        handle.write(b"{this line is torn")
    rebuilt = Arbiter.instantiate(
        root=arbiter.root,
        clock=FrozenClock(),
        service_key=b"test-service-key",
        installation_id="spike-test",
    )
    assert not rebuilt.ok
    assert rebuilt.kind in {AbsenceKind.UNPARSEABLE, AbsenceKind.REFUSED}
    # The live arbiter that still has a clean in-memory view is not the point:
    # a new composition against the torn file must refuse.
    assert rebuilt.value is None


def test_negative_expired_holder_cannot_publish(tmp_path: Path) -> None:
    arbiter, clock, native, _other = _arbiter(tmp_path, ttl=5.0)
    cap = arbiter.grant(native, "tree-write").unwrap()
    clock.advance(6)
    result = arbiter.commit(
        worker=native,
        resource_id="tree-write",
        fencing_token=cap.fencing_token,
        artifact_bytes=b"too-late",
    )
    assert result.code == RefusalCode.EXPIRED_HOLDER.value
    assert arbiter.ledger.of_type("LEASE_EXPIRED")
    assert not arbiter.ledger.of_type("COMMIT_ACCEPTED")


def test_negative_takeover_is_not_silent_clear(tmp_path: Path) -> None:
    arbiter, clock, native, other = _arbiter(tmp_path, ttl=3.0)
    arbiter.grant(native, "tree-write")
    clock.advance(4)
    arbiter.grant(other, "tree-write")
    types = arbiter.ledger.event_types()
    assert "LEASE_EXPIRED" in types
    assert types.count("LEASE_GRANTED") == 2
    idx_exp = types.index("LEASE_EXPIRED")
    idx_second = max(i for i, name in enumerate(types) if name == "LEASE_GRANTED")
    assert idx_exp < idx_second


def test_negative_second_writer_refused_while_live(tmp_path: Path) -> None:
    arbiter, _clock, native, other = _arbiter(tmp_path)
    assert arbiter.grant(native, "tree-write").ok
    second = arbiter.grant(other, "tree-write")
    assert second.kind is AbsenceKind.REFUSED
    assert second.code == RefusalCode.RESOURCE_HELD.value
    held = arbiter.current_holder("tree-write").unwrap()
    assert held is not None
    assert held.holder.worker_id == native.worker_id


def test_negative_unknown_worker_refused(tmp_path: Path) -> None:
    arbiter, _clock, _native, _other = _arbiter(tmp_path)
    stranger = WorkerIdentity.mint("not-on-the-list", lane="native")
    result = arbiter.grant(stranger, "tree-write")
    assert result.code == RefusalCode.UNKNOWN_WORKER.value


def test_negative_sandbox_cannot_commit(tmp_path: Path) -> None:
    arbiter, clock, native, _other = _arbiter(tmp_path)
    sandbox = WorkerIdentity.mint("sandbox-claimant", lane="sandbox")
    arbiter.register_worker(sandbox)
    cap = arbiter.grant(native, "tree-write").unwrap()
    env = IngressEnvelope.build(
        sandbox,
        Stamp.from_clock(sandbox, clock, time_source=clock.source_name),
        {"token": cap.fencing_token},
    )
    denied = arbiter.commit_from_ingress(
        env, resource_id="tree-write", fencing_token=cap.fencing_token, artifact_bytes=b"x"
    )
    assert denied.code == RefusalCode.INGRESS_CANNOT_COMMIT.value
    invented = arbiter.commit(
        worker=sandbox,
        resource_id="tree-write",
        fencing_token=cap.fencing_token,
        artifact_bytes=b"x",
    )
    assert invented.code == RefusalCode.STALE_TOKEN.value


def test_negative_sandbox_lock_file_is_not_a_hold(tmp_path: Path) -> None:
    arbiter, _clock, native, _other = _arbiter(tmp_path)
    arbiter.grant(native, "tree-write")
    planted = arbiter.root / "ingress" / "tree_lock.json"
    planted.write_text('{"holder":"sandbox","fencing_token":99}\n', encoding="utf-8")
    holder = arbiter.current_holder("tree-write").unwrap()
    assert holder is not None
    assert holder.fencing_token != 99
    assert holder.holder.worker_id == native.worker_id


def test_negative_unreadable_not_collapsed_to_changed(tmp_path: Path) -> None:
    watched = tmp_path / "watched.txt"
    watched.write_bytes(b"v1")
    arbiter, _clock, native, _other = _arbiter(tmp_path)
    arbiter.grant(native, "tree-write", watched={"control": watched})

    def reader(path: Path):
        from cosmos.spikes.cosmos_lock.absence import Outcome
        from cosmos.spikes.cosmos_lock.arbiter import filesystem_read

        if path == watched:
            return Outcome.absent(AbsenceKind.UNREADABLE, reason="permission denied")
        return filesystem_read(path)

    arbiter.byte_reader = reader
    checks = arbiter.verify("tree-write", {"control": watched}).unwrap()
    assert checks[0].state == "UNREADABLE"
    assert checks[0].state != "CHANGED"
    assert checks[0].state != "NOT_FOUND"


def test_negative_missing_not_collapsed_to_unreadable(tmp_path: Path) -> None:
    watched = tmp_path / "watched.txt"
    watched.write_bytes(b"v1")
    arbiter, _clock, native, _other = _arbiter(tmp_path)
    arbiter.grant(native, "tree-write", watched={"control": watched})
    watched.unlink()
    checks = arbiter.verify("tree-write", {"control": watched}).unwrap()
    assert checks[0].state == "NOT_FOUND"
    assert checks[0].state != "UNREADABLE"
    assert checks[0].state != "CHANGED"


def test_negative_changed_under_holder_is_changed_not_unreadable(tmp_path: Path) -> None:
    watched = tmp_path / "watched.txt"
    watched.write_bytes(b"v1")
    arbiter, _clock, native, _other = _arbiter(tmp_path)
    arbiter.grant(native, "tree-write", watched={"control": watched})
    watched.write_bytes(b"v2")
    checks = arbiter.verify("tree-write", {"control": watched}).unwrap()
    assert checks[0].state == "CHANGED"
    assert checks[0].state != "UNREADABLE"
    assert checks[0].state != "NOT_FOUND"


def test_negative_out_of_clock_distinct(tmp_path: Path) -> None:
    arbiter, clock, _native, _other = _arbiter(tmp_path, skew=30.0)
    result = arbiter.probe_client_clock(clock.epoch() + 10_000)
    assert result.kind is AbsenceKind.OUT_OF_CLOCK
    assert result.kind is not AbsenceKind.NOT_FOUND
    assert result.kind is not AbsenceKind.UNREADABLE
    assert result.kind is not AbsenceKind.NOT_IN_RECORD
    assert result.code == RefusalCode.CLOCK_SKEW.value


def test_negative_not_in_record_distinct(tmp_path: Path) -> None:
    arbiter, _clock, _native, _other = _arbiter(tmp_path)
    missing_lease = arbiter.inspect_lease("no-such-lease")
    missing_event = arbiter.ledger.get("no-such-event")
    assert missing_lease.kind is AbsenceKind.NOT_IN_RECORD
    assert missing_event.kind is AbsenceKind.NOT_IN_RECORD
    assert missing_lease.kind is not AbsenceKind.NOT_FOUND
    assert missing_event.kind is not AbsenceKind.UNREADABLE


def test_negative_import_has_no_fs_side_effect(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    import cosmos.spikes.cosmos_lock as pkg

    importlib.reload(pkg)
    leftover = [p.name for p in tmp_path.iterdir()]
    assert leftover == []


def test_negative_unknown_flag_exits_2() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "cosmos.spikes.cosmos_lock", "--not-a-flag"],
        cwd="/workspace",
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 2


def test_negative_job_object_native_demo_required() -> None:
    result = PlatformAdapter().create_job_object("cosmos-lock")
    assert result.kind is AbsenceKind.NATIVE_DEMO_REQUIRED
    assert result.details["feature"] == "Job Objects"


def test_negative_rdcw_native_demo_required(tmp_path: Path) -> None:
    result = PlatformAdapter().watch_directory_rdcw(tmp_path)
    assert result.kind is AbsenceKind.NATIVE_DEMO_REQUIRED
    assert result.details["feature"] == "ReadDirectoryChangesW"


def test_negative_msvcrt_native_demo_required(tmp_path: Path) -> None:
    result = PlatformAdapter().msvcrt_try_lock(tmp_path / "x.lock")
    assert result.kind is AbsenceKind.NATIVE_DEMO_REQUIRED
    assert result.details["feature"] == "msvcrt.locking"


def test_negative_windows_volume_api_native_demo_required(tmp_path: Path) -> None:
    adapter = PlatformAdapter()
    assert adapter.windows_volume_name(tmp_path).kind is AbsenceKind.NATIVE_DEMO_REQUIRED
    assert adapter.open_extended(str(tmp_path)).kind is AbsenceKind.NATIVE_DEMO_REQUIRED


def test_negative_windows_path_on_posix_is_wrong_universe() -> None:
    result = PlatformAdapter().native_authoritative_path(r"V:\Ai\_queue\tree_lock.json")
    assert result.kind is AbsenceKind.IDENTITY_MISMATCH
    assert result.code == RefusalCode.WRONG_UNIVERSE.value


def test_negative_client_supplied_expiry_ignored(tmp_path: Path) -> None:
    arbiter, clock, native, _other = _arbiter(tmp_path, ttl=40.0)
    cap = arbiter.grant(
        native,
        "tree-write",
        client_expires_at_epoch=clock.epoch() + 1.0,
    ).unwrap()
    assert cap.expires_at_epoch == pytest.approx(clock.epoch() + 40.0)
    clock.advance(2)
    assert arbiter.current_holder("tree-write").unwrap() is not None


def test_negative_hmac_tamper_refuses_reload(tmp_path: Path) -> None:
    arbiter, clock, native, _other = _arbiter(tmp_path)
    arbiter.grant(native, "tree-write")
    raw = arbiter.ledger.path.read_bytes()
    arbiter.ledger.path.write_bytes(raw.replace(b"tree-write", b"tree-wrote", 1))
    rebuilt = Arbiter.instantiate(
        root=arbiter.root,
        clock=clock,
        service_key=b"test-service-key",
        installation_id="spike-test",
    )
    assert not rebuilt.ok
    assert rebuilt.code in {RefusalCode.LEDGER_INTEGRITY.value, RefusalCode.TORN_STATE.value}


@pytest.mark.skipif(sys.platform == "win32", reason="POSIX container control")
def test_negative_native_windows_paths_are_demo_required_on_this_host() -> None:
    adapter = PlatformAdapter()
    assert adapter.create_job_object("x").kind is AbsenceKind.NATIVE_DEMO_REQUIRED
    assert adapter.watch_directory_rdcw(Path("/tmp")).kind is AbsenceKind.NATIVE_DEMO_REQUIRED
    assert adapter.msvcrt_try_lock(Path("/tmp/x.lock")).kind is AbsenceKind.NATIVE_DEMO_REQUIRED
    assert adapter.windows_volume_name(Path("/tmp")).kind is AbsenceKind.NATIVE_DEMO_REQUIRED
