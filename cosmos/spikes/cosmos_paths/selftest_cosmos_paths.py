"""cosmos_paths selftest — POSITIVE and NEGATIVE controls.

Runnable with: pytest cosmos/spikes/cosmos_paths/selftest_cosmos_paths.py -v

A gate tested only in the passing direction is a gate nobody has seen closed.
"""

from __future__ import annotations

import importlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

from cosmos.spikes.cosmos_paths.absence import AbsenceKind, Absent, Found, TypedRefusal
from cosmos.spikes.cosmos_paths.platform import (
    LONG_PATH_DEMO_CHARS,
    DriveSemantics,
    PlatformAdapter,
)
from cosmos.spikes.cosmos_paths.plant import plant_installation
from cosmos.spikes.cosmos_paths.records import sha256_hex, write_json
from cosmos.spikes.cosmos_paths.resolver import RootResolver
from cosmos.spikes.cosmos_paths.roles import MESH_IDENTITY_NAME, ROLE_SPECS, SENTINEL_NAME
from cosmos.spikes.cosmos_paths.stamp import now_stamp

MEASURED: dict[str, object] = {}


def _measure(name: str, value: object) -> None:
    MEASURED[name] = value
    print(f"MEASURED {name}={value}")


@pytest.fixture
def adapter() -> PlatformAdapter:
    return PlatformAdapter()


@pytest.fixture
def planted(tmp_path: Path) -> tuple[Path, Path]:
    root = tmp_path / "root"
    record = tmp_path / "machine" / "installation-record.json"
    plant_installation(root, record)
    return root, record


# ---------------------------------------------------------------------------
# POSITIVE controls
# ---------------------------------------------------------------------------


class TestPositiveControls:
    def test_instantiate_against_valid_root(self, planted: tuple[Path, Path]) -> None:
        root, record = planted
        t0 = time.perf_counter()
        resolver = RootResolver.instantiate(record)
        ms = (time.perf_counter() - t0) * 1000.0
        _measure("instantiate_ok_ms", round(ms, 3))
        assert resolver.ready is True
        assert resolver.root() == root.resolve()
        assert resolver.installation_id
        _measure("instantiate_ok_kind", AbsenceKind.FOUND.value)

    def test_role_api_resolves_under_one_root(self, planted: tuple[Path, Path]) -> None:
        _root, record = planted
        resolver = RootResolver.instantiate(record)
        resolved = 0
        for name in sorted(ROLE_SPECS):
            path = resolver.role(name)
            assert path.is_dir()
            path.resolve().relative_to(resolver.root())
            resolved += 1
        assert resolver.root().is_dir()
        _measure("roles_resolved", resolved + 1)
        assert resolver.queue().name == "queue"
        assert resolver.mesh().name == "mesh"
        assert resolver.secrets().name == ".secrets"

    def test_secrets_is_sibling_of_publish_by_location(self, planted: tuple[Path, Path]) -> None:
        _root, record = planted
        resolver = RootResolver.instantiate(record)
        assert resolver.secrets_is_sibling_of_publish() is True
        secrets = resolver.secrets().resolve()
        publish = resolver.publish().resolve()
        assert secrets.parent == publish.parent == resolver.root()
        with pytest.raises(ValueError):
            secrets.relative_to(publish)

    def test_second_install_at_different_path(self, tmp_path: Path) -> None:
        a = plant_installation(tmp_path / "A" / "root", tmp_path / "A" / "record.json")
        b = plant_installation(tmp_path / "B" / "root", tmp_path / "B" / "record.json")
        ra = RootResolver.instantiate(a.record_path)
        rb = RootResolver.instantiate(b.record_path)
        assert ra.installation_id != rb.installation_id
        assert ra.root() != rb.root()
        assert ra.queue() != rb.queue()
        assert ra.mesh() != rb.mesh()
        _measure("second_install_roots", 2)
        _measure("second_install_ids_distinct", True)

    def test_second_install_drive_letters_are_distinct_identities(self) -> None:
        v_root = r"V:\A\Ai\COSMOS"
        d_root = r"D:\Ai\COSMOS"
        assert DriveSemantics.roots_are_distinct(v_root, d_root)
        assert DriveSemantics.same_drive(v_root, d_root) is False
        assert DriveSemantics.split(v_root).drive == "V:"
        assert DriveSemantics.split(d_root).drive == "D:"
        _measure("drive_letter_settability_algebra", "V: != D:")

    def test_max_path_safe_walk_275_plus(self, planted: tuple[Path, Path], adapter: PlatformAdapter) -> None:
        _root, record = planted
        resolver = RootResolver.instantiate(record, adapter=adapter)
        target = adapter.long_path_demo_target(resolver.work())
        assert len(str(target)) >= LONG_PATH_DEMO_CHARS
        t0 = time.perf_counter()
        written = adapter.write_bytes(target, b"cosmos-long-path\n")
        walked = adapter.walk(resolver.work())
        ms = (time.perf_counter() - t0) * 1000.0
        assert isinstance(written, Found)
        assert isinstance(walked, Found)
        assert any("payload.txt" in hit.filenames for hit in walked.value)
        read = adapter.read_bytes(target)
        assert isinstance(read, Found)
        assert read.value == b"cosmos-long-path\n"
        _measure("long_path_chars", len(str(target)))
        _measure("long_path_walk_ms", round(ms, 3))

    def test_extended_length_algebra_does_not_double_prefix(self) -> None:
        local = DriveSemantics.to_extended_length(r"V:\A\Ai\COSMOS")
        assert local == r"\\?\V:\A\Ai\COSMOS"
        assert DriveSemantics.to_extended_length(local) == local
        unc = DriveSemantics.to_extended_length(r"\\server\share\cosmos")
        assert unc == r"\\?\UNC\server\share\cosmos"
        assert DriveSemantics.from_extended_length(unc) == r"\\server\share\cosmos"
        _measure("extended_length_local", local)
        _measure("extended_length_unc", unc)

    def test_mesh_content_assertion_passes_when_identity_matches(self, planted: tuple[Path, Path]) -> None:
        _root, record = planted
        resolver = RootResolver.instantiate(record)
        mesh = resolver.mesh()
        identity = json.loads((mesh / MESH_IDENTITY_NAME).read_text(encoding="utf-8"))
        assert identity["phrase"] == "COSMOS_MESH_IDENTITY"
        assert identity["installation_id"] == resolver.installation_id

    def test_typed_absence_kinds_are_four_distinct_values(self) -> None:
        kinds = {
            AbsenceKind.NOT_FOUND,
            AbsenceKind.OUT_OF_CLOCK,
            AbsenceKind.UNREADABLE,
            AbsenceKind.NOT_IN_RECORD,
        }
        assert len(kinds) == 4
        assert len({k.value for k in kinds}) == 4
        assert AbsenceKind.NOT_FOUND is not AbsenceKind.UNREADABLE
        _measure("typed_absence_core_count", 4)

    def test_every_artifact_carries_worker_offset_epoch(self, planted: tuple[Path, Path]) -> None:
        root, record = planted
        stamp = now_stamp()
        assert stamp.worker_id
        assert stamp.written_at
        assert ("+" in stamp.written_at or stamp.written_at.endswith("Z"))
        assert stamp.epoch > 0
        payload = json.loads(record.read_text(encoding="utf-8"))
        assert payload["worker_id"]
        assert payload["epoch"]
        assert payload["written_at"]
        sentinel = json.loads((root / SENTINEL_NAME).read_text(encoding="utf-8"))
        assert sentinel["worker_id"]
        assert sentinel["epoch"]

    def test_posix_advisory_lock_fcntl(self, tmp_path: Path, adapter: PlatformAdapter) -> None:
        if adapter.windows:
            pytest.skip("fcntl path is the container control")
        lock_path = tmp_path / "advisory.lock"
        lock_path.write_bytes(b"x")
        first = adapter.advisory_lock(lock_path)
        assert isinstance(first, Found)
        # flock is per-process; a second lock in THIS process is not a conflict.
        # A child process must lose cleanly.
        repo = Path(__file__).resolve().parents[3]
        child = subprocess.run(
            [
                sys.executable,
                "-c",
                (
                    "from pathlib import Path\n"
                    "from cosmos.spikes.cosmos_paths.absence import Absent\n"
                    "from cosmos.spikes.cosmos_paths.platform import PlatformAdapter\n"
                    f"r = PlatformAdapter().advisory_lock(Path({str(lock_path)!r}))\n"
                    "raise SystemExit(0 if isinstance(r, Absent) else 1)\n"
                ),
            ],
            check=False,
            cwd=str(repo),
            capture_output=True,
            text=True,
        )
        assert child.returncode == 0, child.stderr
        first.value.release()
        third = adapter.advisory_lock(lock_path)
        assert isinstance(third, Found)
        third.value.release()
        _measure("fcntl_lock_held_then_conflict", True)

    def test_cli_report_on_valid_record(self, planted: tuple[Path, Path]) -> None:
        _root, record = planted
        proc = subprocess.run(
            [sys.executable, "-m", "cosmos.spikes.cosmos_paths", "--record", str(record), "--report"],
            check=False,
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).resolve().parents[3]),
        )
        assert proc.returncode == 0, proc.stderr
        payload = json.loads(proc.stdout)
        assert payload["ready"] is True
        _measure("cli_report_rc", proc.returncode)


# ---------------------------------------------------------------------------
# NEGATIVE controls
# ---------------------------------------------------------------------------


class TestNegativeControls:
    def test_missing_root_refuses(self, tmp_path: Path) -> None:
        planted = plant_installation(tmp_path / "root", tmp_path / "record.json")
        payload = json.loads(planted.record_path.read_text(encoding="utf-8"))
        payload["configured_root"] = str(tmp_path / "no-such-root")
        write_json(planted.record_path, payload)
        t0 = time.perf_counter()
        with pytest.raises(TypedRefusal) as exc:
            RootResolver.instantiate(planted.record_path)
        ms = (time.perf_counter() - t0) * 1000.0
        assert exc.value.kind is AbsenceKind.NOT_FOUND
        _measure("missing_root_refusal", exc.value.kind.value)
        _measure("missing_root_ms", round(ms, 3))

    def test_sentinel_wrong_identity_refuses(self, planted: tuple[Path, Path]) -> None:
        root, record = planted
        sentinel_path = root / SENTINEL_NAME
        payload = json.loads(sentinel_path.read_text(encoding="utf-8"))
        payload["system"] = "NOT_COSMOS"
        data = write_json(sentinel_path, payload)
        rec = json.loads(record.read_text(encoding="utf-8"))
        rec["sentinel_digest"] = sha256_hex(data)
        write_json(record, rec)
        with pytest.raises(TypedRefusal) as exc:
            RootResolver.instantiate(record)
        assert exc.value.kind is AbsenceKind.IDENTITY_MISMATCH
        _measure("wrong_identity_refusal", exc.value.kind.value)

    def test_empty_dir_sentinel_trap_detected_on_instantiate(self, tmp_path: Path) -> None:
        planted = plant_installation(
            tmp_path / "root",
            tmp_path / "record.json",
            empty_mesh=True,
            skip_mesh_identity=True,
        )
        assert (planted.root / "mesh").is_dir()
        assert not (planted.root / "mesh" / MESH_IDENTITY_NAME).exists()
        with pytest.raises(TypedRefusal) as exc:
            RootResolver.instantiate(planted.record_path)
        assert exc.value.kind is AbsenceKind.EMPTY_DIR_TRAP
        assert exc.value.observed.get("trap") == "EMPTY_DIR_SENTINEL"
        _measure("empty_dir_trap_instantiate", exc.value.kind.value)

    def test_empty_dir_sentinel_trap_detected_on_mesh_call(self, planted: tuple[Path, Path]) -> None:
        _root, record = planted
        resolver = RootResolver.instantiate(record)
        identity = resolver.mesh() / MESH_IDENTITY_NAME
        identity.unlink()
        with pytest.raises(TypedRefusal) as exc:
            resolver.mesh()
        assert exc.value.kind is AbsenceKind.EMPTY_DIR_TRAP
        _measure("empty_dir_trap_mesh", exc.value.kind.value)

    def test_import_causes_no_filesystem_side_effect(self, monkeypatch: pytest.MonkeyPatch) -> None:
        touches: list[str] = []
        real_open = open

        def spy_open(file, *args, **kwargs):  # type: ignore[no-untyped-def]
            text = str(file)
            if ".cosmos-" in text or "installation-record" in text:
                touches.append(text)
            return real_open(file, *args, **kwargs)

        monkeypatch.setattr("builtins.open", spy_open)
        modules = [name for name in list(sys.modules) if name.startswith("cosmos")]
        for name in modules:
            del sys.modules[name]
        importlib.import_module("cosmos.spikes.cosmos_paths")
        importlib.import_module("cosmos.spikes.cosmos_paths.resolver")
        assert touches == []
        _measure("import_cosmos_sentinel_opens", len(touches))

    def test_unknown_cli_flag_exits_2(self) -> None:
        proc = subprocess.run(
            [sys.executable, "-m", "cosmos.spikes.cosmos_paths", "--typo-flag"],
            check=False,
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).resolve().parents[3]),
        )
        assert proc.returncode == 2
        _measure("unknown_flag_rc", proc.returncode)

    def test_missing_record_flag_exits_2_does_not_guess_env(
        self, planted: tuple[Path, Path], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _root, record = planted
        monkeypatch.setenv("COSMOS_ROOT", str(_root))
        proc = subprocess.run(
            [sys.executable, "-m", "cosmos.spikes.cosmos_paths", "--report"],
            check=False,
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).resolve().parents[3]),
            env={**os.environ, "COSMOS_ROOT": str(_root)},
        )
        assert proc.returncode == 2
        assert "COSMOS_ROOT is not consulted" in proc.stderr
        _ = record

    def test_env_is_not_a_fallback_for_instantiate(
        self, planted: tuple[Path, Path], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root, _record = planted
        monkeypatch.setenv("COSMOS_ROOT", str(root))
        with pytest.raises(TypedRefusal) as exc:
            RootResolver.instantiate(tmp_path / "no-such-record.json")
        assert exc.value.kind is AbsenceKind.NOT_FOUND

    def test_does_not_search_a_plausible_neighbor_root(self, tmp_path: Path) -> None:
        good = plant_installation(tmp_path / "good" / "root", tmp_path / "good" / "record.json")
        bad_root = tmp_path / "missing-root"
        payload = json.loads(good.record_path.read_text(encoding="utf-8"))
        payload["configured_root"] = str(bad_root)
        bad_record = tmp_path / "bad-record.json"
        write_json(bad_record, payload)
        with pytest.raises(TypedRefusal) as exc:
            RootResolver.instantiate(bad_record)
        assert exc.value.kind is AbsenceKind.NOT_FOUND
        # The healthy neighbor must not have been selected.
        healthy = RootResolver.instantiate(good.record_path)
        assert healthy.root() == good.root.resolve()

    def test_unknown_role_refuses_do_not_guess(self, planted: tuple[Path, Path]) -> None:
        _root, record = planted
        resolver = RootResolver.instantiate(record)
        with pytest.raises(TypedRefusal) as exc:
            resolver.role("plausible_cache")
        assert exc.value.kind is AbsenceKind.REFUSED
        assert "do not guess" in exc.value.detail
        _measure("unknown_role_refusal", exc.value.kind.value)

    def test_torn_sentinel_refuses_unparseable(self, planted: tuple[Path, Path]) -> None:
        root, record = planted
        sentinel_path = root / SENTINEL_NAME
        torn = b"{not-json"
        sentinel_path.write_bytes(torn)
        rec = json.loads(record.read_text(encoding="utf-8"))
        rec["sentinel_digest"] = sha256_hex(torn)
        write_json(record, rec)
        with pytest.raises(TypedRefusal) as exc:
            RootResolver.instantiate(record)
        assert exc.value.kind is AbsenceKind.UNPARSEABLE
        _measure("torn_sentinel_refusal", exc.value.kind.value)

    def test_unreadable_sentinel_is_not_not_found(self, planted: tuple[Path, Path]) -> None:
        root, record = planted
        sentinel_path = root / SENTINEL_NAME
        sentinel_path.unlink()
        sentinel_path.mkdir()
        with pytest.raises(TypedRefusal) as exc:
            RootResolver.instantiate(record)
        assert exc.value.kind is AbsenceKind.UNREADABLE
        assert exc.value.kind is not AbsenceKind.NOT_FOUND
        _measure("unreadable_sentinel_refusal", exc.value.kind.value)

    def test_digest_mismatch_is_identity_mismatch(self, planted: tuple[Path, Path]) -> None:
        root, record = planted
        sentinel_path = root / SENTINEL_NAME
        payload = json.loads(sentinel_path.read_text(encoding="utf-8"))
        payload["root_identity"] = "tampered"
        write_json(sentinel_path, payload)
        with pytest.raises(TypedRefusal) as exc:
            RootResolver.instantiate(record)
        assert exc.value.kind is AbsenceKind.IDENTITY_MISMATCH

    def test_windows_drive_path_refused_as_posix_filename(self, tmp_path: Path) -> None:
        planted = plant_installation(tmp_path / "root", tmp_path / "record.json")
        payload = json.loads(planted.record_path.read_text(encoding="utf-8"))
        payload["configured_root"] = r"V:\A\Ai\COSMOS"
        write_json(planted.record_path, payload)
        with pytest.raises(TypedRefusal) as exc:
            RootResolver.instantiate(planted.record_path)
        assert exc.value.kind is AbsenceKind.REFUSED
        # Must not have created a backslash-literal filename.
        stray = list(tmp_path.rglob("*\\*"))
        assert stray == []
        _measure("two_universes_backslash_refused", exc.value.kind.value)

    def test_future_timestamp_is_out_of_clock(self, planted: tuple[Path, Path]) -> None:
        _root, record = planted
        payload = json.loads(record.read_text(encoding="utf-8"))
        payload["written_at"] = "2099-01-01T00:00:00+00:00"
        payload["utc_written_at"] = "2099-01-01T00:00:00Z"
        payload["epoch"] = 4070908800.0
        write_json(record, payload)
        with pytest.raises(TypedRefusal) as exc:
            RootResolver.instantiate(record)
        assert exc.value.kind is AbsenceKind.OUT_OF_CLOCK
        assert exc.value.kind is not AbsenceKind.NOT_FOUND
        _measure("out_of_clock_refusal", exc.value.kind.value)

    def test_omitted_role_is_not_in_record(self, tmp_path: Path) -> None:
        planted = plant_installation(
            tmp_path / "root",
            tmp_path / "record.json",
            omit_roles=frozenset({"board"}),
        )
        with pytest.raises(TypedRefusal) as exc:
            RootResolver.instantiate(planted.record_path)
        assert exc.value.kind is AbsenceKind.NOT_IN_RECORD
        assert exc.value.kind is not AbsenceKind.NOT_FOUND
        _measure("not_in_record_refusal", exc.value.kind.value)

    def test_path_escaping_root_is_refused(self, planted: tuple[Path, Path], adapter: PlatformAdapter) -> None:
        root, _record = planted
        outside = root.parent / "escape"
        result = adapter.normalize_under_root(root, outside)
        assert isinstance(result, Absent)
        assert result.kind is AbsenceKind.REFUSED

    def test_job_object_is_native_demo_required_on_posix(self, adapter: PlatformAdapter) -> None:
        if adapter.windows:
            pytest.skip("this control is the container-side typed refusal")
        result = adapter.create_job_object("cosmos_paths_selftest")
        assert isinstance(result, Absent)
        assert result.kind is AbsenceKind.NATIVE_DEMO_REQUIRED
        _measure("job_object", result.kind.value)

    def test_read_directory_changes_is_native_demo_required_on_posix(self, adapter: PlatformAdapter) -> None:
        if adapter.windows:
            pytest.skip("this control is the container-side typed refusal")
        result = adapter.read_directory_changes("/tmp")
        assert isinstance(result, Absent)
        assert result.kind is AbsenceKind.NATIVE_DEMO_REQUIRED
        _measure("read_directory_changes", result.kind.value)

    def test_msvcrt_locking_is_native_demo_required_on_posix(self, adapter: PlatformAdapter) -> None:
        if adapter.windows:
            pytest.skip("this control is the container-side typed refusal")
        result = adapter.msvcrt_locking("/tmp/msvcrt.lock")
        assert isinstance(result, Absent)
        assert result.kind is AbsenceKind.NATIVE_DEMO_REQUIRED
        _measure("msvcrt_locking", result.kind.value)

    def test_live_volume_info_is_native_demo_required_on_posix(self, adapter: PlatformAdapter) -> None:
        if adapter.windows:
            pytest.skip("this control is the container-side typed refusal")
        result = adapter.windows_volume_info(r"V:\A\Ai\COSMOS")
        assert isinstance(result, Absent)
        assert result.kind is AbsenceKind.NATIVE_DEMO_REQUIRED

    def test_max_path_winerror3_is_native_demo_required_on_posix(
        self, planted: tuple[Path, Path], adapter: PlatformAdapter
    ) -> None:
        if adapter.windows:
            pytest.skip("this control is the container-side typed refusal")
        _root, record = planted
        resolver = RootResolver.instantiate(record, adapter=adapter)
        target = adapter.long_path_demo_target(resolver.work())
        result = adapter.max_path_winerror3_without_prefix(target)
        assert isinstance(result, Absent)
        assert result.kind is AbsenceKind.NATIVE_DEMO_REQUIRED
        _measure("max_path_winerror3", result.kind.value)


def test_native_demo_checklist_names_queue_lane_items(adapter: PlatformAdapter) -> None:
    items = {row["item"] for row in adapter.native_demo_checklist()}
    assert "Job Objects" in items
    assert "ReadDirectoryChangesW" in items
    assert "msvcrt.locking" in items
    assert "live drive/volume" in items
    assert "MAX_PATH WinError 3" in items
    _measure("native_demo_required_count", len(items))


def test_measured_summary_printed() -> None:
    """Always-on sink so pytest output carries the MEASURED map."""
    _measure("selftest_controls_note", "positive+negative")
    print("MEASURED_SUMMARY " + json.dumps(MEASURED, sort_keys=True, default=str))
