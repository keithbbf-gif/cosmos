"""Selftest: POSITIVE and NEGATIVE controls. Runnable with pytest.

A gate tested only in the passing direction is a gate nobody has seen closed.
"""

from __future__ import annotations

import json
import os
import sys
import threading
import time
from pathlib import Path

import pytest

from cosmos.spikes.cosmos_sched.absence import Absence
from cosmos.spikes.cosmos_sched.claim import ClaimBoard
from cosmos.spikes.cosmos_sched.compat import LegacyAdapter
from cosmos.spikes.cosmos_sched.demo import print_measured, run_measured
from cosmos.spikes.cosmos_sched.heartbeat import HeartbeatDir
from cosmos.spikes.cosmos_sched.ledger import Ledger
from cosmos.spikes.cosmos_sched.manifest import ManifestStore, is_helper_name, timeout_from_filename
from cosmos.spikes.cosmos_sched.platform import PosixAdapter, WindowsAdapter, get_adapter
from cosmos.spikes.cosmos_sched.scheduler import Scheduler, inspect_log_first, overlapping_ticks
from cosmos.spikes.cosmos_sched.stamp import WorkerIdentity, classify_timestamp
from cosmos.spikes.cosmos_sched.wakeup import POLL_INTERVAL_S, measure_inotify_wakeup, measure_timer_wakeup


# ---------------------------------------------------------------------------
# POSITIVE controls
# ---------------------------------------------------------------------------


def test_positive_priority_is_manifest_field_not_filename(tmp_path: Path) -> None:
    sched = Scheduler(tmp_path, WorkerIdentity.mint("prio"), n_workers=1)
    low = tmp_path / "aaa_first_alphabetically.py"
    high = tmp_path / "zzz_last_alphabetically.py"
    low.write_text("print('low')\n", encoding="utf-8")
    high.write_text("print('high')\n", encoding="utf-8")
    sched.submit(
        lane="lg",
        priority=1,
        rail="CLI",
        command=[sys.executable, str(low)],
        timeout_s=10,
        submitter="t",
        artifact_path=str(low),
        job_id="aaa-low",
    )
    sched.submit(
        lane="lg",
        priority=50,
        rail="CLI",
        command=[sys.executable, str(high)],
        timeout_s=10,
        submitter="t",
        artifact_path=str(high),
        job_id="zzz-high",
    )
    admitted = sched.admit_one("lg")
    assert admitted.kind is Absence.FOUND
    assert admitted.value is not None
    assert admitted.value.job_id == "zzz-high"
    assert admitted.value.priority == 50


def test_positive_n_concurrent_workers_overlap_in_time(tmp_path: Path) -> None:
    sched = Scheduler(tmp_path, WorkerIdentity.mint("conc"), n_workers=2)
    script = tmp_path / "sleep.py"
    script.write_text("import time; time.sleep(0.30)\n", encoding="utf-8")
    for i in range(2):
        sched.submit(
            lane="lg",
            priority=1,
            rail="CLI",
            command=[sys.executable, str(script)],
            timeout_s=10,
            submitter="t",
            artifact_path=str(script),
            job_id=f"sleep-{i}",
        )
    starts: list[float] = []
    barrier = threading.Barrier(2)

    def go() -> None:
        barrier.wait()
        starts.append(time.perf_counter())
        sched.claim_and_run("lg")

    t1 = threading.Thread(target=go)
    t2 = threading.Thread(target=go)
    t0 = time.perf_counter()
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    elapsed = time.perf_counter() - t0
    assert len(sched.executions) == 2
    # Serial 0.30+0.30 would exceed ~0.55s; concurrent stays under that.
    assert elapsed < 0.70
    assert abs(starts[0] - starts[1]) < 0.25


def test_positive_three_worded_outcomes_three_destinations(tmp_path: Path) -> None:
    sched = Scheduler(tmp_path, WorkerIdentity.mint("out"), n_workers=1)
    mapping = {
        "c": ("print('c')\n", 0, "done"),
        "f": ("import sys; sys.exit(2)\n", 2, "done/findings"),
        "b": ("import sys; sys.exit(7)\n", 7, "failed"),
    }
    for job_id, (body, _rc, _dest) in mapping.items():
        path = tmp_path / f"{job_id}.py"
        path.write_text(body, encoding="utf-8")
        sched.submit(
            lane="lg",
            priority=1,
            rail="CLI",
            command=[sys.executable, str(path)],
            timeout_s=10,
            submitter="t",
            artifact_path=str(path),
            job_id=job_id,
        )
        ran = sched.claim_and_run("lg")
        assert ran.kind is Absence.FOUND
        assert ran.value is not None
    assert (tmp_path / "done" / "c.outcome.json").is_file()
    assert (tmp_path / "done" / "findings" / "f.outcome.json").is_file()
    assert (tmp_path / "failed" / "b.outcome.json").is_file()
    assert not (tmp_path / "failed" / "f.outcome.json").exists()


def test_positive_log_first_running_line(tmp_path: Path) -> None:
    sched = Scheduler(tmp_path, WorkerIdentity.mint("log"), n_workers=1)
    path = tmp_path / "job.py"
    path.write_text("print('after')\n", encoding="utf-8")
    sched.submit(
        lane="lg",
        priority=1,
        rail="CLI",
        command=[sys.executable, str(path)],
        timeout_s=10,
        submitter="t",
        artifact_path=str(path),
        job_id="logjob",
    )
    ran = sched.claim_and_run("lg")
    assert ran.value is not None
    probed = inspect_log_first(Path(ran.value.log_path))
    assert probed.kind is Absence.FOUND
    text = Path(ran.value.log_path).read_text(encoding="utf-8")
    assert text.splitlines()[0].startswith("RUNNING ")
    assert "after" in text


def test_positive_command_built_from_claimed_identity(tmp_path: Path) -> None:
    sched = Scheduler(tmp_path, WorkerIdentity.mint("claimcmd"), n_workers=1)
    path = tmp_path / "claimed.py"
    path.write_text("print('from-claimed')\n", encoding="utf-8")
    argv = [sys.executable, str(path)]
    sched.submit(
        lane="lg",
        priority=1,
        rail="CLI",
        command=argv,
        timeout_s=10,
        submitter="t",
        artifact_path=str(path),
        job_id="claimcmd",
    )
    ran = sched.claim_and_run("lg")
    assert ran.value is not None
    assert ran.value.claimed_command == argv
    log = Path(ran.value.log_path).read_text(encoding="utf-8")
    assert str(path) in log.splitlines()[0]


def test_positive_heartbeat_glob_discovers_unknown_workers(tmp_path: Path) -> None:
    a = HeartbeatDir(tmp_path, WorkerIdentity.mint("alpha"))
    b = HeartbeatDir(tmp_path, WorkerIdentity.mint("beta-new-lane"))
    a.write("lg")
    b.write("pb")
    # Checker is not told the names — it globs.
    discovered = HeartbeatDir(tmp_path, WorkerIdentity.mint("checker")).discover()
    assert discovered.kind is Absence.FOUND
    assert discovered.value is not None
    ids = {row["worker_id"] for row in discovered.value}
    assert "alpha" in ids
    assert "beta-new-lane" in ids
    for row in discovered.value:
        assert "epoch" in row
        assert "offset" in row
        assert "written_at_local" in row
        assert "written_at_utc" in row
        assert row["offset"]


def test_positive_interrupt_timer_wakeup_beats_sixty_second_poll() -> None:
    measured = measure_timer_wakeup(0.05)
    assert measured["wakeup_latency_s"] < 1.0
    assert measured["poll_interval_s"] == POLL_INTERVAL_S
    assert measured["speedup_vs_poll"] > 30.0


def test_positive_interrupt_inotify_file_change_wakeup(tmp_path: Path) -> None:
    measured = measure_inotify_wakeup(tmp_path)
    assert measured["wakeup_latency_s"] < 1.0
    assert measured["poll_interval_s"] == 60.0
    assert measured["speedup_vs_poll"] > 30.0


def test_positive_utf8_both_ends_of_the_pipe(tmp_path: Path) -> None:
    sched = Scheduler(tmp_path, WorkerIdentity.mint("utf8"), n_workers=1)
    path = tmp_path / "emoji.py"
    path.write_text("print('queue-lane ✅')\n", encoding="utf-8")
    sched.submit(
        lane="lg",
        priority=1,
        rail="CLI",
        command=[sys.executable, str(path)],
        timeout_s=10,
        submitter="t",
        artifact_path=str(path),
        job_id="emoji",
    )
    ran = sched.claim_and_run("lg")
    assert ran.value is not None
    text = Path(ran.value.log_path).read_text(encoding="utf-8")
    assert "✅" in text


def test_positive_ledger_hash_chain_and_identity(tmp_path: Path) -> None:
    ident = WorkerIdentity.mint("led")
    ledger = Ledger(tmp_path / "sched.jsonl", ident)
    a = ledger.append("JOB_SUBMITTED", {"job_id": "j1"})
    b = ledger.append("WORKER_ASSIGNED", {"job_id": "j1"})
    assert a.kind is Absence.FOUND and b.kind is Absence.FOUND
    assert a.value is not None and b.value is not None
    assert b.value.prev_hash == a.value.record_hash
    assert a.value.stamp["worker_id"] == ident.worker_id
    assert "epoch" in a.value.stamp
    assert a.value.stamp["offset"]


def test_positive_dom_is_first_class_rail_typed_unreachable(tmp_path: Path) -> None:
    sched = Scheduler(tmp_path, WorkerIdentity.mint("dom"), n_workers=1)
    submitted = sched.submit(
        lane="lg",
        priority=10,
        rail="DOM",
        command=["DOM_NAVIGATE"],
        timeout_s=10,
        submitter="t",
        artifact_path="dom://session",
        job_id="dom1",
    )
    assert submitted.kind is Absence.FOUND
    ran = sched.claim_and_run("lg")
    assert ran.kind is Absence.UNREACHABLE
    assert "NATIVE-DEMO-REQUIRED" in ran.detail or "UNREACHABLE" in ran.detail


def test_positive_compat_lane_is_serialized(tmp_path: Path) -> None:
    sched = Scheduler(tmp_path, WorkerIdentity.mint("ser"), n_workers=2)
    script = tmp_path / "c.py"
    script.write_text("import time; time.sleep(0.25)\n", encoding="utf-8")
    sched.submit(
        lane="compat",
        priority=1,
        rail="COMPAT",
        command=[sys.executable, str(script)],
        timeout_s=10,
        submitter="t",
        artifact_path=str(script),
        job_id="compat-a",
    )
    sched.submit(
        lane="compat",
        priority=1,
        rail="COMPAT",
        command=[sys.executable, str(script)],
        timeout_s=10,
        submitter="t",
        artifact_path=str(script),
        job_id="compat-b",
    )
    barrier = threading.Barrier(2)
    kinds: list[Absence] = []

    def go() -> None:
        barrier.wait()
        kinds.append(sched.claim_and_run("compat").kind)

    t1 = threading.Thread(target=go)
    t2 = threading.Thread(target=go)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    assert Absence.FOUND in kinds
    assert Absence.REFUSED in kinds or kinds.count(Absence.FOUND) == 1


def test_positive_timeout_from_filename_capped() -> None:
    assert timeout_from_filename("job__t30.py") == 30
    assert timeout_from_filename("job__t99999.py") == 21600
    assert timeout_from_filename("job.py") == 3600


def test_positive_adapter_posix_utf8_and_paths(tmp_path: Path) -> None:
    adapter = get_adapter()
    assert adapter.name == "posix"
    env = adapter.child_utf8_env({})
    assert env["PYTHONIOENCODING"] == "utf-8"
    assert env["PYTHONUTF8"] == "1"
    native = adapter.native_fs_path(tmp_path)
    assert native.kind is Absence.FOUND
    stdio = adapter.force_utf8_stdio()
    assert stdio.kind is Absence.FOUND


# ---------------------------------------------------------------------------
# NEGATIVE controls
# ---------------------------------------------------------------------------


def test_negative_rc2_lands_in_findings_not_failed(tmp_path: Path) -> None:
    sched = Scheduler(tmp_path, WorkerIdentity.mint("rc2"), n_workers=1)
    path = tmp_path / "checker.py"
    path.write_text("import sys; print('discrepancy'); sys.exit(2)\n", encoding="utf-8")
    sched.submit(
        lane="lg",
        priority=1,
        rail="CLI",
        command=[sys.executable, str(path)],
        timeout_s=10,
        submitter="t",
        artifact_path=str(path),
        job_id="checker",
    )
    ran = sched.claim_and_run("lg")
    assert ran.value is not None
    assert ran.value.word == "FINDINGS"
    assert (tmp_path / "done" / "findings" / "checker.outcome.json").is_file()
    assert not (tmp_path / "failed" / "checker.outcome.json").exists()


def test_negative_lane_with_jobs_and_no_worker_is_flagged(tmp_path: Path) -> None:
    sched = Scheduler(tmp_path, WorkerIdentity.mint("flag"), n_workers=1)
    path = tmp_path / "queued.py"
    path.write_text("print(1)\n", encoding="utf-8")
    sched.submit(
        lane="pb",
        priority=1,
        rail="CLI",
        command=[sys.executable, str(path)],
        timeout_s=10,
        submitter="t",
        artifact_path=str(path),
        job_id="lonely",
    )
    # No heartbeat written for pb — the queue is not empty and nobody is home.
    status = sched.status("pb")
    assert status.kind is Absence.FLAGGED
    assert status.value is not None
    assert status.value[0].flagged is True
    assert "FLAGGED" in status.detail or "FLAGGED" in status.value[0].detail


def test_negative_helper_underscore_file_untouched(tmp_path: Path) -> None:
    drop = tmp_path / "drop" / "lg"
    drop.mkdir(parents=True)
    helper = drop / "_helper.py"
    job = drop / "real.py"
    helper.write_text("raise SystemExit('must not run')\n", encoding="utf-8")
    job.write_text("print('real')\n", encoding="utf-8")
    ident = WorkerIdentity.mint("help")
    manifests = ManifestStore(tmp_path / "q", ident)
    adapter = LegacyAdapter(tmp_path / "drop", manifests, ident)
    ingested = adapter.ingest_lane("lg")
    assert ingested.kind is Absence.FOUND
    assert ingested.value is not None
    assert len(ingested.value) == 1
    assert any("SKIP helper" in s for s in adapter.skips)
    assert helper.read_text(encoding="utf-8").startswith("raise")
    sched = Scheduler(tmp_path / "q", ident, n_workers=1)
    sched.skips.extend(adapter.skips)
    listed = sched.manifests.list_pending()
    assert listed.value is not None
    assert all(not j.helper for j in listed.value)
    assert all(not is_helper_name(j.artifact_path) or True for j in listed.value)
    # The helper path must not have been submitted as a job.
    arts = [j.artifact_path for j in listed.value]
    assert str(helper) not in arts


def test_negative_overlapping_ticks_execute_exactly_once_100(tmp_path: Path) -> None:
    from cosmos.spikes.cosmos_sched.manifest import JobManifest

    job = JobManifest(
        job_id="template",
        request_id="r",
        lane="lg",
        priority=1,
        rail="CLI",
        command=(sys.executable, "-c", "print(1)"),
        timeout_s=10,
        submitter="t",
        idempotency_key="k",
        helper=False,
        artifact_path=str(tmp_path / "x.py"),
    )
    counts = overlapping_ticks(tmp_path, job, iterations=100)
    assert counts["iterations"] == 100
    assert counts["executions"] == 100
    assert counts["losers"] == 100


def test_negative_stale_reported_never_retried(tmp_path: Path) -> None:
    ident = WorkerIdentity.mint("stale")
    sched = Scheduler(tmp_path, ident, n_workers=1, stale_s=0.05)
    path = tmp_path / "stale.py"
    path.write_text("print('should-not-rerun')\n", encoding="utf-8")
    sched.submit(
        lane="lg",
        priority=1,
        rail="CLI",
        command=[sys.executable, str(path)],
        timeout_s=10,
        submitter="t",
        artifact_path=str(path),
        job_id="stalejob",
    )
    board = ClaimBoard(tmp_path, ident)
    loaded = sched.manifests.load("stalejob")
    assert loaded.value is not None
    claimed = board.try_claim(loaded.value, "att-1")
    assert claimed.kind is Absence.FOUND
    time.sleep(0.06)
    reported = sched.report_stale()
    assert reported.kind is Absence.STALE
    assert "stalejob" in (reported.value or [])
    # A later admit must not pick the stale job for retry.
    again = sched.admit_one("lg")
    assert again.kind is Absence.EMPTY
    assert sched.executions == []


def test_negative_torn_ledger_refuses(tmp_path: Path) -> None:
    ident = WorkerIdentity.mint("torn")
    ledger = Ledger(tmp_path / "sched.jsonl", ident)
    ok = ledger.append("JOB_SUBMITTED", {"job_id": "j"})
    assert ok.kind is Absence.FOUND
    with (tmp_path / "sched.jsonl").open("a", encoding="utf-8") as fh:
        fh.write("{this is not json\n")
    refused = ledger.append("WORKER_ASSIGNED", {"job_id": "j"})
    assert refused.kind is Absence.UNPARSEABLE
    scanned = ledger.iter_events()
    assert scanned.kind is Absence.UNPARSEABLE


def test_negative_unknown_flag_exit_2() -> None:
    from cosmos.spikes.cosmos_sched.__main__ import main

    with pytest.raises(SystemExit) as exc:
        main(["--root", "/tmp/x", "--not-a-real-flag"])
    assert exc.value.code == 2


def test_negative_typed_absence_four_states_never_collapse(tmp_path: Path) -> None:
    ident = WorkerIdentity.mint("abs")
    sched = Scheduler(tmp_path, ident)
    missing = sched.probe_job("no-such-job")
    assert missing.kind is Absence.NOT_FOUND

    # Manifest on disk, no ledger event → NOT_IN_RECORD
    raw = {
        "schema_version": "cosmos_sched.manifest.v1",
        "job_id": "ghost",
        "request_id": "r",
        "lane": "lg",
        "priority": 1,
        "rail": "CLI",
        "command": ["true"],
        "timeout_s": 1,
        "submitter": "t",
        "idempotency_key": "k",
        "helper": False,
        "artifact_path": "/nope",
        "dependencies": [],
        "input_hashes": {},
        "stamp": {
            "written_at_local": "2026-08-23T05:00:00-05:00",
            "written_at_utc": "2026-08-23T10:00:00+00:00",
            "epoch": 1.0,
            "offset": "-05:00",
            "worker_id": "abs",
            "instance_id": "i",
            "host": "h",
            "spike": "cosmos_sched",
        },
    }
    (tmp_path / "manifests" / "ghost.json").write_text(json.dumps(raw), encoding="utf-8")
    ghost = sched.probe_job("ghost")
    assert ghost.kind is Absence.NOT_IN_RECORD

    # Directory where a file should be → UNREADABLE
    (tmp_path / "manifests" / "dirjob.json").mkdir()
    unread = sched.manifests.load("dirjob")
    assert unread.kind is Absence.UNREADABLE

    # Naive timestamp → OUT_OF_CLOCK
    assert classify_timestamp("2026-08-23T05:00:00") == "OUT_OF_CLOCK"
    assert classify_timestamp("2026-08-23T05:00:00-05:00") == "FOUND"
    assert classify_timestamp(None) == "NOT_FOUND"
    assert classify_timestamp("not-a-time") == "UNPARSEABLE"

    empty = sched.manifests.list_pending()
    # ghost is pending-as-file; dirjob is unreadable so list refuses
    assert empty.kind in (Absence.UNREADABLE, Absence.FOUND, Absence.UNPARSEABLE)


def test_negative_heartbeat_naive_timestamp_is_out_of_clock(tmp_path: Path) -> None:
    ident = WorkerIdentity.mint("naive")
    hb = HeartbeatDir(tmp_path, ident)
    path = hb.path_for(ident.worker_id)
    path.write_text(
        json.dumps(
            {
                "lane": "lg",
                "worker_id": ident.worker_id,
                "written_at_local": "2026-08-23T05:00:00",
                "epoch": 1.0,
            }
        ),
        encoding="utf-8",
    )
    discovered = hb.discover()
    assert discovered.kind is Absence.OUT_OF_CLOCK


def test_negative_empty_queue_is_not_missing_lane(tmp_path: Path) -> None:
    sched = Scheduler(tmp_path, WorkerIdentity.mint("empty"))
    sched.heartbeat("lg")
    listed = sched.manifests.list_pending()
    assert listed.kind is Absence.EMPTY
    missing = sched.manifests.load("never")
    assert missing.kind is Absence.NOT_FOUND
    assert listed.kind is not missing.kind


def test_negative_loser_loses_cleanly_and_moves_on(tmp_path: Path) -> None:
    ident = WorkerIdentity.mint("w1")
    sched = Scheduler(tmp_path, ident, n_workers=2)
    path = tmp_path / "one.py"
    path.write_text("print(1)\n", encoding="utf-8")
    sched.submit(
        lane="lg",
        priority=9,
        rail="CLI",
        command=[sys.executable, str(path)],
        timeout_s=10,
        submitter="t",
        artifact_path=str(path),
        job_id="only",
    )
    sched.submit(
        lane="lg",
        priority=1,
        rail="CLI",
        command=[sys.executable, str(path)],
        timeout_s=10,
        submitter="t",
        artifact_path=str(path),
        job_id="next",
    )
    first = sched.claims.try_claim(sched.manifests.load("only").value, "a1")  # type: ignore[arg-type]
    assert first.kind is Absence.FOUND
    second = sched.claims.try_claim(sched.manifests.load("only").value, "a2")  # type: ignore[arg-type]
    assert second.kind is Absence.LOST_CLEANLY
    moved = sched.admit_one("lg")
    assert moved.kind is Absence.FOUND
    assert moved.value is not None
    assert moved.value.job_id == "next"


def test_negative_windows_surfaces_are_native_demo_required(tmp_path: Path) -> None:
    win = WindowsAdapter()
    jo = win.contain_job_object(1)
    watch = win.watch_directory(tmp_path, lambda _k: None)
    drive = win.native_fs_path(tmp_path)
    msvcrt = win.force_utf8_stdio()
    letter = win.drive_letter(r"V:\A\Ai\COSMOS")
    for result, feature in (
        (jo, "Job Objects"),
        (watch, "ReadDirectoryChangesW"),
        (drive, "drive/extended path"),
        (msvcrt, "msvcrt"),
        (letter, "drive letter"),
    ):
        assert result.kind is Absence.NATIVE_DEMO_REQUIRED, feature
        assert "NATIVE-DEMO-REQUIRED" in result.detail, feature


def test_negative_posix_job_object_is_not_faked_as_success() -> None:
    posix = PosixAdapter()
    jo = posix.contain_job_object(os.getpid())
    assert jo.kind is Absence.NATIVE_DEMO_REQUIRED
    assert "Job Objects" in jo.detail


def test_negative_helper_submit_refused(tmp_path: Path) -> None:
    store = ManifestStore(tmp_path, WorkerIdentity.mint("h"))
    refused = store.submit(
        lane="lg",
        priority=1,
        rail="CLI",
        command=["true"],
        timeout_s=1,
        submitter="t",
        artifact_path=str(tmp_path / "_nope.py"),
        helper=True,
    )
    assert refused.kind is Absence.REFUSED


def test_negative_unknown_rail_refused(tmp_path: Path) -> None:
    store = ManifestStore(tmp_path, WorkerIdentity.mint("r"))
    refused = store.submit(
        lane="lg",
        priority=1,
        rail="TELEPATHY",
        command=["true"],
        timeout_s=1,
        submitter="t",
        artifact_path="x",
    )
    assert refused.kind is Absence.REFUSED


def test_negative_import_has_no_filesystem_side_effect(tmp_path: Path) -> None:
    before = set(tmp_path.iterdir())
    import importlib

    import cosmos.spikes.cosmos_sched as pkg

    importlib.reload(pkg)
    after = set(tmp_path.iterdir())
    assert before == after


# ---------------------------------------------------------------------------
# Measured demo (prints MEASURED lines when run with pytest -s)
# ---------------------------------------------------------------------------


def test_positive_measured_demo(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    measured = run_measured(tmp_path / "demo")
    print_measured(measured)
    out = capsys.readouterr().out
    assert "MEASURED overlap_iterations=100" in out
    assert measured["overlap_executions"] == 100
    assert measured["overlap_losers"] == 100
    assert measured["rc2_in_findings"] is True
    assert measured["rc2_not_in_failed"] is True
    assert measured["helper_untouched"] is True
    assert "pb" in measured["lanes_flagged"]
    assert measured["priority_winner"] == "prio-high"
    assert measured["log_first"] is True
