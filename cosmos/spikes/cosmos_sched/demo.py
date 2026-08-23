"""Measured demo. A spike whose claims are prose has not run."""

from __future__ import annotations

import json
import sys
import tempfile
import threading
import time
from pathlib import Path

from cosmos.spikes.cosmos_sched.absence import Absence
from cosmos.spikes.cosmos_sched.claim import Claim
from cosmos.spikes.cosmos_sched.manifest import JobManifest
from cosmos.spikes.cosmos_sched.outcomes import WordedOutcome
from cosmos.spikes.cosmos_sched.platform import WindowsAdapter, get_adapter
from cosmos.spikes.cosmos_sched.scheduler import RunRecord, Scheduler, overlapping_ticks
from cosmos.spikes.cosmos_sched.stamp import WorkerIdentity, now_stamp
from cosmos.spikes.cosmos_sched.wakeup import POLL_INTERVAL_S, measure_inotify_wakeup, measure_timer_wakeup


def _script(dir_path: Path, name: str, body: str) -> Path:
    path = dir_path / name
    path.write_text(body, encoding="utf-8")
    return path


def run_measured(tmp: Path | None = None) -> dict[str, object]:
    identity = WorkerIdentity.mint("demo-sched")
    stamp = now_stamp(identity)
    root = Path(tmp) if tmp is not None else Path(tempfile.mkdtemp(prefix="cosmos_sched_demo_"))
    jobs = root / "jobsrc"
    jobs.mkdir(parents=True, exist_ok=True)
    clean = _script(jobs, "clean.py", "print('ok')\n")
    findings = _script(jobs, "findings.py", "import sys\nprint('discrepancy')\nsys.exit(2)\n")
    broke = _script(jobs, "broke.py", "import sys\nprint('boom')\nsys.exit(1)\n")
    emoji = _script(jobs, "emoji.py", "print('queue-lane ✅')\n")
    helper = _script(jobs, "_helper.py", "raise SystemExit('helper must not run')\n")

    sched = Scheduler(root / "q", identity, n_workers=3)
    sched.skips.append(f"SKIP helper {helper} (never claimed)")
    for path, prio, rc_name in (
        (clean, 5, "clean"),
        (findings, 5, "findings"),
        (broke, 5, "broke"),
        (emoji, 5, "emoji"),
    ):
        submitted = sched.submit(
            lane="lg",
            priority=prio,
            rail="CLI",
            command=[sys.executable, str(path)],
            timeout_s=30,
            submitter=identity.worker_id,
            artifact_path=str(path),
            job_id=rc_name,
        )
        assert submitted.kind is Absence.FOUND, submitted.detail

    high = _script(jobs, "aaa_should_not_win_by_name.py", "print('low')\n")
    low_name_high_prio = _script(jobs, "zzz_filename_last.py", "print('high')\n")
    sched.submit(
        lane="lg",
        priority=1,
        rail="CLI",
        command=[sys.executable, str(high)],
        timeout_s=30,
        submitter=identity.worker_id,
        artifact_path=str(high),
        job_id="prio-low",
    )
    sched.submit(
        lane="lg",
        priority=99,
        rail="CLI",
        command=[sys.executable, str(low_name_high_prio)],
        timeout_s=30,
        submitter=identity.worker_id,
        artifact_path=str(low_name_high_prio),
        job_id="prio-high",
    )
    first = sched.admit_one("lg")
    assert first.kind is Absence.FOUND and first.value is not None
    priority_winner = first.value.job_id

    orphan = Scheduler(root / "q", WorkerIdentity.mint("demo-status"))
    orphan.submit(
        lane="pb",
        priority=1,
        rail="CLI",
        command=[sys.executable, str(clean)],
        timeout_s=30,
        submitter="demo",
        artifact_path=str(clean),
        job_id="orphan-pb",
    )
    lane_status = orphan.status()
    flagged = [p.lane for p in (lane_status.value or []) if p.flagged]

    drained = sched.drain("lg", max_jobs=16)
    words = [r.value.word for r in drained if r.value is not None]
    dest_findings = (sched.root / "done" / "findings" / "findings.outcome.json").exists()
    dest_failed_for_findings = (sched.root / "failed" / "findings.outcome.json").exists()
    dest_clean = (sched.root / "done" / "clean.outcome.json").exists()
    dest_broke = (sched.root / "failed" / "broke.outcome.json").exists()

    log_ok = False
    if drained and drained[0].value is not None:
        from cosmos.spikes.cosmos_sched.scheduler import inspect_log_first

        log_ok = inspect_log_first(Path(drained[0].value.log_path)).kind is Absence.FOUND

    hearts = sched.heartbeats.discover()

    overlap_job = JobManifest(
        job_id="template",
        request_id="r",
        lane="lg",
        priority=1,
        rail="CLI",
        command=(sys.executable, "-c", "print(1)"),
        timeout_s=10,
        submitter="demo",
        idempotency_key="k",
        helper=False,
        artifact_path=str(clean),
    )
    overlap = overlapping_ticks(root / "overlap", overlap_job, iterations=100)

    timer = measure_timer_wakeup(0.05)
    try:
        inotify = measure_inotify_wakeup(root)
        inotify_note = "container-inotify"
    except Exception as exc:  # noqa: BLE001 — demo records the typed miss
        inotify = {
            "wakeup_latency_s": None,
            "poll_interval_s": POLL_INTERVAL_S,
            "speedup_vs_poll": None,
            "error": str(exc),
        }
        inotify_note = "inotify-unavailable"

    starts: list[float] = []
    barrier = threading.Barrier(2)
    conc = Scheduler(root / "conc", WorkerIdentity.mint("conc"), n_workers=2)

    def sleeper(job_id: str) -> None:
        conc.submit(
            lane="lg",
            priority=1,
            rail="CLI",
            command=[sys.executable, "-c", "import time; time.sleep(0.25)"],
            timeout_s=10,
            submitter="demo",
            artifact_path=str(clean),
            job_id=job_id,
        )

    sleeper("c1")
    sleeper("c2")

    def hook(claim: Claim, _job: JobManifest) -> RunRecord | None:
        starts.append(time.perf_counter())
        time.sleep(0.2)
        return RunRecord(claim.job_id, claim.worker_id, WordedOutcome.CLEAN, 0, "", list(claim.command))

    def _hook(claim: Claim, job: JobManifest):
        rec = hook(claim, job)
        from cosmos.spikes.cosmos_sched.absence import TypedResult

        return TypedResult(Absence.FOUND, "CLEAN", rec)

    conc._execute_hook = _hook

    def go() -> None:
        barrier.wait()
        conc.claim_and_run("lg")

    t1 = threading.Thread(target=go)
    t2 = threading.Thread(target=go)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    overlap_s = abs(starts[0] - starts[1]) if len(starts) == 2 else 999.0

    win = WindowsAdapter()
    native = {
        "job_objects": win.contain_job_object(1).kind.value,
        "readdirectorychangesw": win.watch_directory(root, lambda _k: None).kind.value,
        "drive_semantics": win.native_fs_path(root).kind.value,
        "msvcrt": win.force_utf8_stdio().kind.value,
    }

    adapter = get_adapter()
    measured = {
        "worker": stamp.to_dict(),
        "overlap_iterations": overlap["iterations"],
        "overlap_executions": overlap["executions"],
        "overlap_losers": overlap["losers"],
        "priority_winner": priority_winner,
        "words": words,
        "rc2_in_findings": dest_findings,
        "rc2_not_in_failed": not dest_failed_for_findings,
        "clean_in_done": dest_clean,
        "broke_in_failed": dest_broke,
        "helper_untouched": helper.exists() and helper.read_text(encoding="utf-8").startswith("raise"),
        "lanes_flagged": flagged,
        "log_first": log_ok,
        "heartbeats_glob": hearts.kind.value,
        "heartbeat_count": len(hearts.value or []),
        "timer_wakeup_s": timer["wakeup_latency_s"],
        "poll_interval_s": POLL_INTERVAL_S,
        "timer_speedup_vs_poll": timer["speedup_vs_poll"],
        "inotify": inotify,
        "inotify_note": inotify_note,
        "concurrent_start_delta_s": overlap_s,
        "platform": adapter.name,
        "windows_native_demo": native,
    }
    return measured


def print_measured(measured: dict[str, object]) -> None:
    print(f"MEASURED overlap_iterations={measured['overlap_iterations']} "
          f"executions={measured['overlap_executions']} losers={measured['overlap_losers']}")
    print(f"MEASURED priority_winner={measured['priority_winner']}")
    print(f"MEASURED rc2_in_findings={measured['rc2_in_findings']} "
          f"rc2_not_in_failed={measured['rc2_not_in_failed']}")
    print(f"MEASURED destinations clean={measured['clean_in_done']} "
          f"broke={measured['broke_in_failed']}")
    print(f"MEASURED helper_untouched={measured['helper_untouched']}")
    print(f"MEASURED lanes_flagged={measured['lanes_flagged']}")
    print(f"MEASURED log_first={measured['log_first']} "
          f"heartbeats={measured['heartbeat_count']} glob={measured['heartbeats_glob']}")
    print(f"MEASURED wakeup_timer_s={measured['timer_wakeup_s']:.6f} "
          f"poll_interval_s={measured['poll_interval_s']} "
          f"speedup={measured['timer_speedup_vs_poll']:.1f}x")
    print(f"MEASURED concurrent_start_delta_s={measured['concurrent_start_delta_s']:.6f}")
    print(f"MEASURED platform={measured['platform']} "
          f"windows={json.dumps(measured['windows_native_demo'], sort_keys=True)}")
    print(f"MEASURED inotify_note={measured['inotify_note']} inotify={measured['inotify']}")
    print("NATIVE-DEMO-REQUIRED: Job Objects, ReadDirectoryChangesW, drive semantics, msvcrt")


def main() -> int:
    measured = run_measured()
    print_measured(measured)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
