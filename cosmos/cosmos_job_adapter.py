#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Legacy Job Adapter (decision 9) — file-drop → scheduler job.

Satellite next to cosmos_run. Does not edit cosmos_sched. Claim-by-rename on
this volume into running\\ BEFORE execution; the command is built from a copy
of the *claimed* file under the tools role (never the pre-claim queue path).
Exit codes map through Runner: 0 CLEAN / 2 FINDINGS / else BROKE. After
JOB_DONE the claimed file is projected into done\\ / findings\\ / failed\\.
"""
from __future__ import annotations

import json
import re
import shutil
import time
import uuid
from pathlib import Path

from cosmos_sched import Scheduler

SKIP_DIR_NAMES = frozenset({
    "done", "failed", "findings", "running", "logs", "returns", "manifests",
    "jobs", "dispatch_jobs", "adapter_jobs", "_lanes", "_delme", "_hold",
    "_superseded", "__pycache__", ".git", "staged",
})
_TIMEOUT_RE = re.compile(r"__t(\d+)$")
_CLAIM_NAME = "adapter_claims.jsonl"


class LegacyJobAdapter:
    """One ingress for queue-role *.py file-drops that are not Scheduler manifests."""

    def __init__(self, queue: Path, tools_root: Path, work_root: Path,
                 sched: Scheduler):
        self.queue = Path(queue)
        self.tools_root = Path(tools_root)
        self.work = Path(work_root)
        self.sched = sched

    def claims_path(self) -> Path:
        return self.queue / _CLAIM_NAME

    def scan(self) -> list[Path]:
        """Runnable file-drops still sitting on the queue role (not yet claimed).

        Newest mtime first so a just-dropped gate proof is not starved by older
        stranded Motif files. `_`-prefixed names are helpers, never jobs.
        """
        found: list[Path] = []
        for root, _lane in self._lane_roots():
            if not root.is_dir():
                continue
            for p in root.iterdir():
                if not p.is_file() or p.suffix.lower() != ".py":
                    continue
                if p.name.startswith("_"):
                    continue
                found.append(p)
        found.sort(key=lambda p: (-p.stat().st_mtime, p.name))
        return found

    def adapt(self, max_n: int = 1) -> list[dict]:
        """Claim up to max_n file-drops, copy under tools, Scheduler.submit py:copy."""
        out: list[dict] = []
        for src in self.scan()[: max(0, int(max_n))]:
            rec = self._adapt_one(src)
            if rec is not None:
                out.append(rec)
        return out

    def project_outcomes(self, results: list[dict]) -> list[dict]:
        """Move claimed files to done/findings/failed after a worded outcome."""
        projected = []
        by_id = {r.get("job_id"): r for r in (results or []) if r.get("job_id")}
        if not by_id:
            return projected
        claims = self._load_claims()
        for jid, result in by_id.items():
            claim = claims.get(jid)
            if not claim:
                continue
            moved = self._project_one(claim, result.get("outcome") or "BROKE")
            if moved:
                projected.append(moved)
        return projected

    def _lane_roots(self) -> list[tuple[Path, str]]:
        roots: list[tuple[Path, str]] = [(self.queue, "default")]
        lanes = self.queue / "_lanes"
        if lanes.is_dir():
            for p in sorted(lanes.iterdir()):
                if p.is_dir() and p.name not in SKIP_DIR_NAMES and not p.name.startswith("_"):
                    roots.append((p, p.name))
        return roots

    def _lane_of(self, path: Path) -> str:
        try:
            rel = path.resolve().relative_to(self.queue.resolve())
        except ValueError:
            return "default"
        parts = rel.parts
        if len(parts) >= 2 and parts[0] == "_lanes":
            return parts[1]
        return "default"

    @staticmethod
    def _timeout_of(path: Path) -> int:
        m = _TIMEOUT_RE.search(path.stem)
        if not m:
            return 1800
        try:
            n = int(m.group(1))
        except ValueError:
            return 1800
        return n if n > 0 else 1800

    def _running_dir(self, src: Path) -> Path:
        lane = self._lane_of(src)
        if lane == "default":
            d = self.queue / "running"
        else:
            d = self.queue / "_lanes" / lane / "running"
        d.mkdir(parents=True, exist_ok=True)
        return d

    def _outcome_dir(self, claimed: Path, outcome: str) -> Path:
        lane = self._lane_of(claimed)
        name = {"CLEAN": "done", "FINDINGS": "findings", "BROKE": "failed"}.get(
            outcome, "failed")
        if lane == "default":
            d = self.queue / name
        else:
            d = self.queue / "_lanes" / lane / name
        d.mkdir(parents=True, exist_ok=True)
        return d

    def _adapt_one(self, src: Path) -> dict | None:
        src = Path(src)
        if not src.is_file():
            return None
        running = self._running_dir(src)
        claimed = running / src.name
        if claimed.exists():
            claimed = running / f"{src.stem}_{uuid.uuid4().hex[:6]}{src.suffix}"
        try:
            src.replace(claimed)
        except OSError:
            return None
        dest_dir = self.tools_root / "adapter_jobs"
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / claimed.name
        if dest.exists():
            dest = dest_dir / f"{claimed.stem}_{uuid.uuid4().hex[:6]}{claimed.suffix}"
        try:
            shutil.copy2(claimed, dest)
        except OSError as e:
            rec = {"src": str(src), "claimed": str(claimed), "copy_error": str(e)}
            self._append_claim({**rec, "job_id": None, "t": time.time()})
            return rec
        timeout_s = self._timeout_of(claimed)
        lane = self._lane_of(claimed)
        command = f"py:{dest}"
        job_id = self.sched.submit(command, "normal", timeout_s=timeout_s, lane=lane)
        rec = {
            "job_id": job_id,
            "src": str(src),
            "claimed": str(claimed),
            "copy": str(dest),
            "lane": lane,
            "name": claimed.name,
            "timeout_s": timeout_s,
            "command": command,
            "t": time.time(),
        }
        self._append_claim(rec)
        return rec

    def _project_one(self, claim: dict, outcome: str) -> dict | None:
        claimed = Path(claim.get("claimed") or "")
        if not claimed.is_file():
            return None
        dest_dir = self._outcome_dir(claimed, outcome)
        dest = dest_dir / claimed.name
        if dest.exists():
            dest = dest_dir / f"{claimed.stem}_{uuid.uuid4().hex[:6]}{claimed.suffix}"
        try:
            claimed.replace(dest)
        except OSError as e:
            return {"job_id": claim.get("job_id"), "error": str(e),
                    "claimed": str(claimed)}
        return {"job_id": claim.get("job_id"), "outcome": outcome,
                "projected": str(dest)}

    def _append_claim(self, rec: dict) -> None:
        path = self.claims_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(rec, default=str) + "\n")

    def _load_claims(self) -> dict[str, dict]:
        path = self.claims_path()
        out: dict[str, dict] = {}
        if not path.is_file():
            return out
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            return out
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except ValueError:
                continue
            jid = rec.get("job_id")
            if jid:
                out[jid] = rec
        return out
