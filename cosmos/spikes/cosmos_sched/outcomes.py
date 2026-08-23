"""Three worded outcomes to three destinations.

0 = CLEAN    -> done/
2 = FINDINGS -> done/findings/   (a checker that did its job is not broken)
else = BROKE -> failed/

Nothing is deleted. Destination files are receipts; the manifest stays put.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from cosmos.spikes.cosmos_sched.absence import Absence, TypedResult
from cosmos.spikes.cosmos_sched.stamp import WorkerIdentity, now_stamp


class WordedOutcome:
    CLEAN = "CLEAN"
    FINDINGS = "FINDINGS"
    BROKE = "BROKE"
    TIMED_OUT = "TIMED_OUT"


def word_for_rc(rc: int) -> str:
    if rc == 0:
        return WordedOutcome.CLEAN
    if rc == 2:
        return WordedOutcome.FINDINGS
    return WordedOutcome.BROKE


def destination_for(word: str) -> str:
    if word == WordedOutcome.CLEAN:
        return "done"
    if word == WordedOutcome.FINDINGS:
        return "done/findings"
    return "failed"


class OutcomeStore:
    def __init__(self, root: Path, identity: WorkerIdentity) -> None:
        self.root = root
        self.identity = identity
        (root / "done" / "findings").mkdir(parents=True, exist_ok=True)
        (root / "failed").mkdir(parents=True, exist_ok=True)

    def record(
        self,
        job_id: str,
        word: str,
        rc: int | None,
        extra: dict[str, Any] | None = None,
    ) -> TypedResult[Path]:
        dest_rel = destination_for(word)
        dest_dir = self.root / dest_rel
        dest_dir.mkdir(parents=True, exist_ok=True)
        stamp = now_stamp(self.identity)
        payload = {
            "job_id": job_id,
            "outcome": word,
            "rc": rc,
            "destination": dest_rel,
            "stamp": stamp.to_dict(),
        }
        if extra:
            payload.update(extra)
        path = dest_dir / f"{job_id}.outcome.json"
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return TypedResult(Absence.FOUND, word, path)

    def load(self, job_id: str) -> TypedResult[dict[str, Any]]:
        candidates = [
            self.root / "done" / f"{job_id}.outcome.json",
            self.root / "done" / "findings" / f"{job_id}.outcome.json",
            self.root / "failed" / f"{job_id}.outcome.json",
        ]
        existing = [p for p in candidates if p.exists()]
        if not existing:
            return TypedResult(Absence.NOT_FOUND, f"no outcome receipt for {job_id}")
        path = existing[0]
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            return TypedResult(Absence.UNREADABLE, f"outcome unreadable: {exc}")
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            return TypedResult(Absence.UNPARSEABLE, f"torn outcome: {exc}")
        return TypedResult(Absence.FOUND, str(data.get("outcome")), data)
