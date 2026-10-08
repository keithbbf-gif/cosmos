"""Typed OracleSpec + failing-before-edit (freeze spine Q1).

{cmd, cwd, expect_fail_pre, expect_pass_post, property_id}
Before any Edit/Write/apply_patch: cmd must fail (expect_fail_pre).
After structured edit: same oracle must pass (expect_pass_post).
Missing OracleSpec on nontrivial WO → refuse DraftPatch.
"""

from __future__ import annotations

import hashlib
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional


class OracleGateError(RuntimeError):
    def __init__(self, code: str, detail: str = ""):
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}" if detail else code)


@dataclass(frozen=True)
class OracleSpec:
    cmd: str
    cwd: str
    expect_fail_pre: bool
    expect_pass_post: bool
    property_id: str

    def __post_init__(self) -> None:
        if not self.cmd:
            raise OracleGateError("NO_ORACLE_CMD", "cmd required")
        if not self.property_id:
            raise OracleGateError("NO_PROPERTY_ID", "property_id required")
        # cwd must not be a live/ tree
        cwd_s = str(self.cwd).replace("\\", "/").lower()
        if cwd_s.rstrip("/").endswith("/live") or "/live/" in cwd_s:
            raise OracleGateError("ORACLE_CWD_LIVE", self.cwd)

    @staticmethod
    def from_mapping(d: dict[str, Any]) -> "OracleSpec":
        required = ("cmd", "cwd", "expect_fail_pre", "expect_pass_post", "property_id")
        missing = [k for k in required if k not in d]
        if missing:
            raise OracleGateError("NO_ORACLE_SPEC", f"missing fields: {missing}")
        return OracleSpec(
            cmd=str(d["cmd"]),
            cwd=str(d["cwd"]),
            expect_fail_pre=bool(d["expect_fail_pre"]),
            expect_pass_post=bool(d["expect_pass_post"]),
            property_id=str(d["property_id"]),
        )

    @property
    def oracle_id(self) -> str:
        return hashlib.sha256(f"{self.property_id}|{self.cmd}".encode()).hexdigest()[:16]


@dataclass
class OracleResult:
    exit_code: int
    stdout: str
    stderr: str
    log_hash: str

    @property
    def ok(self) -> bool:
        return self.exit_code == 0


class OracleGate:
    """Fail-before-edit gate for nontrivial WOs."""

    def __init__(self, attempt_root: str | Path):
        self.attempt_root = Path(attempt_root)
        self._edited = False
        self._pre_ran = False
        self._pre_failed: Optional[bool] = None

    def require_spec(self, wo: dict[str, Any] | None, *, nontrivial: bool = True) -> OracleSpec:
        if not nontrivial:
            raise OracleGateError("TRIVIAL_WO", "oracle gate is for nontrivial WOs")
        if not wo or "oracle" not in wo:
            raise OracleGateError("NO_ORACLE_SPEC", "nontrivial WO missing OracleSpec")
        return OracleSpec.from_mapping(wo["oracle"])

    def run(self, spec: OracleSpec) -> OracleResult:
        import os
        import shutil

        cwd = Path(spec.cwd)
        if not cwd.is_absolute():
            cwd = self.attempt_root / cwd
        cwd.mkdir(parents=True, exist_ok=True)
        # Avoid same-second .pyc masking a just-applied edit (fail-before-edit spine).
        for d in cwd.glob("**/__pycache__"):
            shutil.rmtree(d, ignore_errors=True)
        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        proc = subprocess.run(
            spec.cmd,
            shell=True,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            env=env,
        )
        blob = f"{proc.returncode}\n{proc.stdout}\n{proc.stderr}".encode()
        return OracleResult(
            exit_code=proc.returncode,
            stdout=proc.stdout,
            stderr=proc.stderr,
            log_hash=hashlib.sha256(blob).hexdigest(),
        )

    def assert_fail_pre(self, spec: OracleSpec) -> OracleResult:
        if not spec.expect_fail_pre:
            raise OracleGateError("BAD_SPEC", "expect_fail_pre must be True for fail-before-edit")
        result = self.run(spec)
        self._pre_ran = True
        self._pre_failed = not result.ok
        if result.ok:
            raise OracleGateError(
                "ORACLE_ALREADY_GREEN",
                "pre-edit oracle passed; Edit refused (nothing to fix / wrong WO)",
            )
        return result

    def allow_edit(self, spec: OracleSpec | None, wo: dict[str, Any] | None = None) -> None:
        """Call before any Edit/Write/apply_patch. Raises if blocked."""
        if spec is None:
            if wo is not None:
                spec = self.require_spec(wo)
            else:
                raise OracleGateError("NO_ORACLE_SPEC", "Edit refused without OracleSpec")
        if not self._pre_ran:
            self.assert_fail_pre(spec)
        elif self._pre_failed is False:
            raise OracleGateError("ORACLE_ALREADY_GREEN", "Edit blocked while oracle green")
        # mark that edit is now permitted (caller performs edit)
        self._edited = True

    def assert_pass_post(self, spec: OracleSpec) -> OracleResult:
        if not self._edited:
            raise OracleGateError("NO_EDIT", "post-edit check before any edit")
        if not spec.expect_pass_post:
            raise OracleGateError("BAD_SPEC", "expect_pass_post must be True")
        result = self.run(spec)
        if not result.ok:
            raise OracleGateError("ORACLE_STILL_RED", f"exit={result.exit_code}")
        return result
