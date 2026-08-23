#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_dom - THE DOM WORKER PROTOCOL (F5 builder). DOM is a first-class scheduler
rail run by a CONTAINED worker with typed failures - never a side channel, never a
silent fallback to API (ratified decision 6).

THE DRIVER IS INJECTED. This module owns the PROTOCOL: ephemeral profiles per attempt,
evidence capture, typed failure mapping (UNREACHABLE / SESSION_EXPIRED / AUTH_REQUIRED /
BROKE), report-never-retry, and the rule that a screenshot is never proof of a paid
action. A real Chrome/Edge driver plugs in behind Driver; the fake driver in the tests
proves every failure path - which no real browser can be asked to do on demand.
"""
from __future__ import annotations

import json
import shutil
import time
import uuid
from pathlib import Path
from typing import Protocol

from cosmos_ledger import Ledger
from cosmos_platform import makedirs


class DomError(RuntimeError):
    """kind in {UNREACHABLE, SESSION_EXPIRED, AUTH_REQUIRED, BROKE}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


class Driver(Protocol):
    """What a browser driver must provide. Implementations: real (CDP/Playwright-class,
    6b work) and FakeDriver (tests)."""

    def start(self, profile_dir: str) -> None: ...
    def navigate(self, url: str) -> str: ...          # returns page text
    def session_ok(self) -> bool: ...
    def stop(self) -> None: ...


class DomWorker:
    def __init__(self, ledger: Ledger, work_root: Path, worker_id: str,
                 driver: Driver):
        self.ledger = ledger
        self.work_root = Path(work_root)
        self.worker_id = worker_id
        self.driver = driver

    def run_attempt(self, job_id: str, url: str,
                    require_session: bool = False) -> dict:
        """One DOM attempt: ephemeral profile -> preflight -> act -> evidence -> typed
        result. The profile dir is attempt-private and staged (never deleted here)."""
        attempt = uuid.uuid4().hex[:10]
        profile = self.work_root / job_id / attempt / "profile"
        evidence_dir = self.work_root / job_id / attempt / "evidence"
        makedirs(profile)
        makedirs(evidence_dir)
        self.ledger.append("DOM_ATTEMPT_STARTED",
                           {"job_id": job_id, "attempt": attempt,
                            "worker": self.worker_id, "url": url,
                            "profile": str(profile)})
        try:
            try:
                self.driver.start(str(profile))
            except Exception as e:                                    # noqa: BLE001
                return self._fail(job_id, attempt, "UNREACHABLE",
                                  f"browser/transport did not start: {e}")
            try:
                if require_session and not self.driver.session_ok():
                    return self._fail(job_id, attempt, "SESSION_EXPIRED",
                                      "preflight: authenticated session is not valid - "
                                      "AUTH is Keith's click, never automated")
                text = self.driver.navigate(url)
            except PermissionError as e:
                return self._fail(job_id, attempt, "AUTH_REQUIRED", str(e))
            except ConnectionError as e:
                return self._fail(job_id, attempt, "UNREACHABLE", str(e))
            except Exception as e:                                    # noqa: BLE001
                return self._fail(job_id, attempt, "BROKE",
                                  f"mid-action failure - outcome cannot be safely "
                                  f"established: {type(e).__name__}: {e}. "
                                  f"REPORT-NEVER-RETRY: side effects may exist.")
            # evidence: what the page said, hashed - and evidence is EVIDENCE, not proof
            # of a remote commitment (a screenshot never proves a paid action landed).
            ev = evidence_dir / "page_text.txt"
            ev.write_text(text, encoding="utf-8")
            self.ledger.append("DOM_ATTEMPT_OK",
                               {"job_id": job_id, "attempt": attempt,
                                "worker": self.worker_id, "chars": len(text),
                                "evidence": str(ev)})
            return {"ok": True, "kind": "OK", "attempt": attempt,
                    "text": text, "evidence": str(ev)}
        finally:
            try:
                self.driver.stop()
            except Exception:                                         # noqa: BLE001
                pass

    def _fail(self, job_id: str, attempt: str, kind: str, detail: str) -> dict:
        self.ledger.append("DOM_ATTEMPT_FAILED",
                           {"job_id": job_id, "attempt": attempt,
                            "worker": self.worker_id, "kind": kind,
                            "detail": detail[:300]})
        return {"ok": False, "kind": kind, "attempt": attempt, "detail": detail}
