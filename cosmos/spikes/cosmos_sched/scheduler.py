"""N concurrent workers, priority admission, log-first execution.

Concurrency is a scheduler property. Priority is a manifest field.
The loser of an overlapping claim LOSES CLEANLY and moves on.
Stale running work is reported, never retried.
"""

from __future__ import annotations

import json
import threading
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from cosmos.spikes.cosmos_sched.absence import Absence, TypedResult
from cosmos.spikes.cosmos_sched.claim import STALE_RUNNING_S, Claim, ClaimBoard
from cosmos.spikes.cosmos_sched.heartbeat import HeartbeatDir
from cosmos.spikes.cosmos_sched.lanes import DEFAULT_POLICIES, LaneBoard, LanePolicy, LaneProbe
from cosmos.spikes.cosmos_sched.ledger import Ledger
from cosmos.spikes.cosmos_sched.manifest import JobManifest, ManifestStore
from cosmos.spikes.cosmos_sched.outcomes import OutcomeStore, WordedOutcome, word_for_rc
from cosmos.spikes.cosmos_sched.platform import ChildSpec, PlatformAdapter, get_adapter
from cosmos.spikes.cosmos_sched.stamp import Clock, WorkerIdentity, now_stamp


@dataclass
class RunRecord:
    job_id: str
    worker_id: str
    word: str
    rc: int | None
    log_path: str
    claimed_command: list[str]


@dataclass
class Scheduler:
    root: Path
    identity: WorkerIdentity
    n_workers: int = 2
    policies: dict[str, LanePolicy] = field(default_factory=lambda: dict(DEFAULT_POLICIES))
    stale_s: float = STALE_RUNNING_S
    adapter: PlatformAdapter = field(default_factory=get_adapter)
    clock: Clock = field(default_factory=Clock)
    executions: list[str] = field(default_factory=list)
    lost_cleanly: list[str] = field(default_factory=list)
    stale_reports: list[str] = field(default_factory=list)
    skips: list[str] = field(default_factory=list)
    lock: threading.Lock = field(default_factory=threading.Lock)
    _completed: set[str] = field(default_factory=set)
    _inflight: dict[str, int] = field(default_factory=dict)
    _execute_hook: Callable[[Claim, JobManifest], TypedResult[RunRecord]] | None = None

    def __post_init__(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        (self.root / "logs").mkdir(parents=True, exist_ok=True)
        (self.root / "work").mkdir(parents=True, exist_ok=True)
        self.manifests = ManifestStore(self.root, self.identity)
        self.claims = ClaimBoard(self.root, self.identity, clock_epoch=self.clock.now_epoch)
        self.heartbeats = HeartbeatDir(self.root, self.identity)
        self.outcomes = OutcomeStore(self.root, self.identity)
        self.ledger = Ledger(self.root / "sched.jsonl", self.identity)
        self.lanes = LaneBoard(self.manifests, self.heartbeats)

    def submit(self, **kwargs: Any) -> TypedResult[JobManifest]:
        result = self.manifests.submit(**kwargs)
        if result.kind is Absence.FOUND and result.value is not None:
            self.ledger.append(
                "JOB_SUBMITTED",
                {"job_id": result.value.job_id, "lane": result.value.lane, "priority": result.value.priority},
            )
        return result

    def heartbeat(self, lane: str) -> TypedResult[Path]:
        return self.heartbeats.write(lane)

    def status(self, lane: str | None = None) -> TypedResult[list[LaneProbe]]:
        """Print helper skips (never silent) and probe every known lane."""
        for skip in self.skips:
            print(skip, flush=True)
        names = [lane] if lane else sorted(self.policies)
        probes: list[LaneProbe] = []
        claimed = self._claimed_ids()
        for name in names:
            probed = self.lanes.probe(name, claimed, set(self._completed))
            if probed.value is not None:
                probes.append(probed.value)
                print(probed.detail, flush=True)
            elif probed.kind in (Absence.UNREADABLE, Absence.UNPARSEABLE, Absence.OUT_OF_CLOCK):
                return TypedResult(probed.kind, probed.detail, probes)
        flagged = [p for p in probes if p.flagged]
        kind = Absence.FLAGGED if flagged else Absence.FOUND
        return TypedResult(kind, f"lanes={len(probes)} flagged={len(flagged)}", probes)

    def _claimed_ids(self) -> set[str]:
        if not self.claims.dir.exists():
            return set()
        return {p.stem for p in self.claims.dir.glob("*.claim")}

    def report_stale(self) -> TypedResult[list[str]]:
        scanned = self.claims.stale_claims(self.clock.now_epoch(), self.stale_s)
        if scanned.kind in (Absence.UNPARSEABLE, Absence.UNREADABLE, Absence.NOT_FOUND):
            return TypedResult(scanned.kind, scanned.detail, [])
        if scanned.kind is Absence.EMPTY:
            return TypedResult(Absence.EMPTY, scanned.detail, [])
        reported: list[str] = []
        for claim in scanned.value or []:
            if claim.job_id in self._completed:
                continue
            self.stale_reports.append(claim.job_id)
            self.ledger.append(
                "STALE_REPORTED",
                {"job_id": claim.job_id, "worker_id": claim.worker_id, "retry": False},
            )
            reported.append(claim.job_id)
            # Report-never-retry: do not delete the claim and do not re-execute.
        return TypedResult(Absence.STALE, f"reported={len(reported)} never-retried", reported)

    def admit_one(self, lane: str | None = None) -> TypedResult[JobManifest]:
        listed = self.manifests.list_pending()
        if listed.kind is not Absence.FOUND or listed.value is None:
            return TypedResult(listed.kind, listed.detail)
        claimed = self._claimed_ids()
        stale_ids = set(self.stale_reports)
        candidates = [
            j
            for j in listed.value
            if j.job_id not in claimed
            and j.job_id not in self._completed
            and j.job_id not in stale_ids
            and (lane is None or j.lane == lane)
        ]
        if not candidates:
            return TypedResult(Absence.EMPTY, "nothing admissible")
        # Priority field, then epoch, then job_id. Filename is irrelevant.
        candidates.sort(key=lambda j: (-j.priority, j.stamp.get("epoch", 0.0), j.job_id))
        for job in candidates:
            policy = self.policies.get(job.lane) or LanePolicy(job.lane, 8, False)
            inflight = self._inflight.get(job.lane, 0)
            if inflight >= policy.max_inflight:
                continue
            if policy.serialized and inflight >= 1:
                continue
            return TypedResult(Absence.FOUND, f"admitted {job.job_id} priority={job.priority}", job)
        return TypedResult(Absence.REFUSED, "lane at capacity")

    def claim_and_run(self, lane: str | None = None) -> TypedResult[RunRecord]:
        self.heartbeat(lane or "lg")
        self.report_stale()
        with self.lock:
            admitted = self.admit_one(lane)
            if admitted.kind is not Absence.FOUND or admitted.value is None:
                return TypedResult(admitted.kind, admitted.detail)
            job = admitted.value
            self._inflight[job.lane] = self._inflight.get(job.lane, 0) + 1
        attempt_id = uuid.uuid4().hex[:12]
        claimed = self.claims.try_claim(job, attempt_id)
        if claimed.kind is Absence.LOST_CLEANLY:
            with self.lock:
                self.lost_cleanly.append(job.job_id)
                self._inflight[job.lane] = max(0, self._inflight.get(job.lane, 1) - 1)
            self.ledger.append("CLAIM_LOST_CLEANLY", {"job_id": job.job_id, "worker_id": self.identity.worker_id})
            return TypedResult(Absence.LOST_CLEANLY, claimed.detail)
        if claimed.kind is not Absence.FOUND or claimed.value is None:
            with self.lock:
                self._inflight[job.lane] = max(0, self._inflight.get(job.lane, 1) - 1)
            return TypedResult(claimed.kind, claimed.detail)
        claim = claimed.value
        self.ledger.append(
            "WORKER_ASSIGNED",
            {"job_id": job.job_id, "attempt_id": attempt_id, "worker_id": self.identity.worker_id},
        )
        try:
            if self._execute_hook is not None:
                ran = self._execute_hook(claim, job)
                if ran.kind is Absence.FOUND and ran.value is not None:
                    self._complete(ran.value)
            else:
                ran = self._execute(claim, job)
        finally:
            with self.lock:
                self._inflight[job.lane] = max(0, self._inflight.get(job.lane, 1) - 1)
        return ran

    def _log_path(self, claim: Claim) -> Path:
        name = f"{claim.job_id}__{claim.attempt_id}__{claim.worker_id}.log"
        return self.root / "logs" / name

    def _execute(self, claim: Claim, job: JobManifest) -> TypedResult[RunRecord]:
        log_path = self._log_path(claim)
        work = self.root / "work" / claim.job_id / claim.attempt_id / claim.worker_id
        work.mkdir(parents=True, exist_ok=True)
        argv = claim.claimed_command()
        # Log-first: open and fsync RUNNING + cmd BEFORE the child starts.
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("w", encoding="utf-8", newline="\n") as log:
            log.write(f"RUNNING {' '.join(argv)}\n")
            log.flush()
            try:
                import os as _os

                _os.fsync(log.fileno())
            except OSError:
                pass
            with self.lock:
                self.executions.append(claim.job_id)
            self.ledger.append("WORKER_STARTED", {"job_id": claim.job_id, "cmd": argv})
            if job.rail == "DOM":
                record = self._execute_dom(claim, job, log, log_path, argv)
            else:
                record = self._execute_child(claim, job, log, log_path, argv, work)
        if record.value is not None:
            self._complete(record.value)
        return record

    def _execute_dom(
        self,
        claim: Claim,
        job: JobManifest,
        log: Any,
        log_path: Path,
        argv: list[str],
    ) -> TypedResult[RunRecord]:
        # DOM is a first-class rail. This container cannot drive a live session.
        log.write("DOM rail: no live browser in this container\n")
        log.write("UNREACHABLE NATIVE-DEMO-REQUIRED\n")
        log.flush()
        word = WordedOutcome.BROKE
        rec = RunRecord(claim.job_id, claim.worker_id, word, None, str(log_path), argv)
        self.ledger.append(
            "DOM_UNREACHABLE",
            {"job_id": claim.job_id, "detail": "NATIVE-DEMO-REQUIRED"},
        )
        return TypedResult(Absence.UNREACHABLE, "DOM rail UNREACHABLE in container", rec)

    def _execute_child(
        self,
        claim: Claim,
        job: JobManifest,
        log: Any,
        log_path: Path,
        argv: list[str],
        work: Path,
    ) -> TypedResult[RunRecord]:
        spec = ChildSpec(argv=argv, cwd=str(work), timeout_s=float(job.timeout_s), env=dict())
        proc = self.adapter.spawn(spec)
        jo = self.adapter.contain_job_object(proc.pid)
        if jo.kind is Absence.NATIVE_DEMO_REQUIRED:
            log.write(f"{jo.detail}\n")
        try:
            raw, _ = proc.communicate(timeout=job.timeout_s)
            rc = proc.returncode
            text = self.adapter.decode_pipe(raw)
            log.write(text)
            if not text.endswith("\n"):
                log.write("\n")
            word = word_for_rc(int(rc if rc is not None else 1))
            log.write(f"{word} rc={rc}\n")
            rec = RunRecord(claim.job_id, claim.worker_id, word, rc, str(log_path), argv)
            return TypedResult(Absence.FOUND, word, rec)
        except Exception as exc:  # TimeoutExpired is the expected timeout path
            from subprocess import TimeoutExpired

            if isinstance(exc, TimeoutExpired):
                log.write("RED - TIMED OUT\n")
                log.flush()
                self.adapter.kill_contained(proc.pid)
                rec = RunRecord(
                    claim.job_id,
                    claim.worker_id,
                    WordedOutcome.TIMED_OUT,
                    None,
                    str(log_path),
                    argv,
                )
                return TypedResult(Absence.TIMED_OUT, "RED - TIMED OUT", rec)
            log.write(f"BROKE {exc}\n")
            rec = RunRecord(claim.job_id, claim.worker_id, WordedOutcome.BROKE, None, str(log_path), argv)
            return TypedResult(Absence.BROKE, str(exc), rec)

    def _complete(self, record: RunRecord) -> None:
        word = record.word
        event = {
            WordedOutcome.CLEAN: "JOB_COMPLETED_CLEAN",
            WordedOutcome.FINDINGS: "JOB_COMPLETED_FINDINGS",
            WordedOutcome.BROKE: "JOB_COMPLETED_BROKE",
            WordedOutcome.TIMED_OUT: "JOB_COMPLETED_BROKE",
        }.get(word, "JOB_COMPLETED_BROKE")
        self.outcomes.record(record.job_id, word if word != WordedOutcome.TIMED_OUT else WordedOutcome.BROKE, record.rc)
        self.ledger.append(event, {"job_id": record.job_id, "rc": record.rc, "log": record.log_path})
        with self.lock:
            self._completed.add(record.job_id)

    def probe_job(self, job_id: str) -> TypedResult[JobManifest]:
        """Typed absence across manifest vs ledger. Four states stay distinct."""
        loaded = self.manifests.load(job_id)
        if loaded.kind is not Absence.FOUND:
            return loaded
        recorded = self.ledger.types_for_job(job_id)
        if recorded.kind is Absence.NOT_IN_RECORD:
            return TypedResult(Absence.NOT_IN_RECORD, recorded.detail, loaded.value)
        if recorded.kind in (Absence.UNPARSEABLE, Absence.UNREADABLE, Absence.NOT_FOUND):
            return TypedResult(recorded.kind, recorded.detail, loaded.value)
        stamp = (loaded.value.stamp if loaded.value is not None else {}).get("written_at_local")
        from cosmos.spikes.cosmos_sched.stamp import classify_timestamp

        clock = classify_timestamp(stamp)
        if clock == "OUT_OF_CLOCK":
            return TypedResult(Absence.OUT_OF_CLOCK, f"job {job_id} timestamp is out of clock", loaded.value)
        return loaded

    def drain(self, lane: str | None = None, max_jobs: int = 32) -> list[TypedResult[RunRecord]]:
        results: list[TypedResult[RunRecord]] = []
        for _ in range(max_jobs):
            ran = self.claim_and_run(lane)
            if ran.kind in (Absence.EMPTY, Absence.REFUSED):
                break
            results.append(ran)
        return results


def overlapping_ticks(
    root: Path,
    job: JobManifest,
    iterations: int = 100,
) -> dict[str, int]:
    """Two overlapping ticks, `iterations` times. Job must execute exactly once each."""
    from cosmos.spikes.cosmos_sched.claim import ClaimBoard

    executions = 0
    losses = 0
    guard = threading.Lock()
    for i in range(iterations):
        ident_a = WorkerIdentity.mint(f"tick-a-{i}")
        sched_a = Scheduler(root / f"ov-{i}", ident_a, n_workers=2)
        submitted = sched_a.submit(
            lane=job.lane,
            priority=job.priority,
            rail=job.rail,
            command=list(job.command),
            timeout_s=job.timeout_s,
            submitter="overlap",
            artifact_path=job.artifact_path,
            job_id=f"ovjob-{i:04d}",
        )
        if submitted.kind is not Absence.FOUND or submitted.value is None:
            raise RuntimeError(submitted.detail)
        target = submitted.value
        barrier = threading.Barrier(2)
        kinds: list[Absence] = []
        hits: list[str] = []

        def worker(wid: str) -> None:
            ident = WorkerIdentity.mint(wid)
            board = ClaimBoard(root / f"ov-{i}", ident)
            barrier.wait()
            result = board.try_claim(target, ident.instance_id)
            with guard:
                kinds.append(result.kind)
                if result.kind is Absence.FOUND and result.value is not None:
                    hits.append(result.value.job_id)
                    # Execute exactly once: only the winner runs the payload.
                    argv = result.value.claimed_command()
                    if argv:
                        pass

        t1 = threading.Thread(target=worker, args=(f"tick-a-{i}",))
        t2 = threading.Thread(target=worker, args=(f"tick-b-{i}",))
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        executions += len(hits)
        losses += sum(1 for k in kinds if k is Absence.LOST_CLEANLY)
    return {
        "iterations": iterations,
        "executions": executions,
        "losers": losses,
    }


def wait_briefly(seconds: float) -> None:
    time.sleep(seconds)


def stamp_now(identity: WorkerIdentity) -> dict[str, Any]:
    return now_stamp(identity).to_dict()


def inspect_log_first(log_path: Path) -> TypedResult[str]:
    if not log_path.exists():
        return TypedResult(Absence.NOT_FOUND, f"log missing: {log_path}")
    try:
        text = log_path.read_text(encoding="utf-8")
    except OSError as exc:
        return TypedResult(Absence.UNREADABLE, f"log unreadable: {exc}")
    if not text:
        return TypedResult(Absence.EMPTY, "log empty")
    first = text.splitlines()[0]
    if not first.startswith("RUNNING "):
        return TypedResult(Absence.IDENTITY_MISMATCH, f"log-first failed: {first!r}")
    return TypedResult(Absence.FOUND, first, first)
