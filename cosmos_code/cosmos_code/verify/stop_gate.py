"""DoneBundle refuse — DONE needs full hash tuple (freeze spine Q3).

(diff_hash, oracle_id, oracle_log_hash, pack_hash, cmd_hash)
Any missing field → DONE refused. Green model prose ≠ done.
Worker Stop is propose-only; CCr publish is separate.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class StopGateError(RuntimeError):
    def __init__(self, code: str, detail: str = ""):
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}" if detail else code)


BUNDLE_FIELDS = ("diff_hash", "oracle_id", "oracle_log_hash", "pack_hash", "cmd_hash")


@dataclass(frozen=True)
class DoneBundle:
    diff_hash: str
    oracle_id: str
    oracle_log_hash: str
    pack_hash: str
    cmd_hash: str

    def __post_init__(self) -> None:
        for name in BUNDLE_FIELDS:
            val = getattr(self, name)
            if not val or not str(val).strip():
                raise StopGateError("INCOMPLETE_BUNDLE", f"missing/empty {name}")

    @staticmethod
    def from_mapping(d: dict[str, Any] | None) -> "DoneBundle":
        if not d:
            raise StopGateError("INCOMPLETE_BUNDLE", "empty bundle")
        missing = [k for k in BUNDLE_FIELDS if not d.get(k)]
        if missing:
            raise StopGateError("INCOMPLETE_BUNDLE", f"missing: {missing}")
        return DoneBundle(**{k: str(d[k]) for k in BUNDLE_FIELDS})

    def as_dict(self) -> dict[str, str]:
        return {k: getattr(self, k) for k in BUNDLE_FIELDS}


def _sha_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def _sha_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


class StopGate:
    """Refuse DONE unless full DoneBundle present and hashes match artifacts."""

    def __init__(self, attempt_root: str | Path):
        self.attempt_root = Path(attempt_root)

    def refuse_if_incomplete(self, bundle: dict[str, Any] | None) -> DoneBundle:
        return DoneBundle.from_mapping(bundle)

    def verify_against_artifacts(
        self,
        bundle: DoneBundle,
        *,
        diff_path: str | Path | None = None,
        diff_bytes: bytes | None = None,
        oracle_log: str | None = None,
        oracle_log_path: str | Path | None = None,
        pack_hash_expected: str | None = None,
        cmd: str | None = None,
    ) -> None:
        # diff
        if diff_bytes is not None:
            actual_diff = hashlib.sha256(diff_bytes).hexdigest()
        elif diff_path is not None:
            p = Path(diff_path)
            if not p.is_absolute():
                p = self.attempt_root / p
            if not p.exists():
                raise StopGateError("DIFF_MISSING", str(p))
            actual_diff = _sha_file(p)
        else:
            raise StopGateError("DIFF_MISSING", "no diff artifact")
        if actual_diff != bundle.diff_hash:
            raise StopGateError("DIFF_HASH_MISMATCH", f"{actual_diff} != {bundle.diff_hash}")

        # oracle log
        if oracle_log is not None:
            actual_olog = _sha_text(oracle_log)
        elif oracle_log_path is not None:
            p = Path(oracle_log_path)
            if not p.is_absolute():
                p = self.attempt_root / p
            if not p.exists():
                raise StopGateError("ORACLE_LOG_MISSING", str(p))
            actual_olog = _sha_file(p)
        else:
            raise StopGateError("ORACLE_LOG_MISSING", "no oracle log")
        if actual_olog != bundle.oracle_log_hash:
            raise StopGateError(
                "ORACLE_LOG_HASH_MISMATCH", f"{actual_olog} != {bundle.oracle_log_hash}"
            )

        if pack_hash_expected is not None and pack_hash_expected != bundle.pack_hash:
            raise StopGateError(
                "PACK_HASH_MISMATCH", f"{pack_hash_expected} != {bundle.pack_hash}"
            )

        if cmd is not None:
            actual_cmd = _sha_text(cmd)
            if actual_cmd != bundle.cmd_hash:
                raise StopGateError("CMD_HASH_MISMATCH", f"{actual_cmd} != {bundle.cmd_hash}")

    def accept_done(
        self,
        bundle: dict[str, Any] | DoneBundle | None,
        *,
        artifacts: dict[str, Any] | None = None,
    ) -> DoneBundle:
        """Full bundle + matching artifacts → DONE (still propose-only)."""
        if isinstance(bundle, DoneBundle):
            b = bundle
        else:
            b = self.refuse_if_incomplete(bundle)
        arts = artifacts or {}
        self.verify_against_artifacts(
            b,
            diff_path=arts.get("diff_path"),
            diff_bytes=arts.get("diff_bytes"),
            oracle_log=arts.get("oracle_log"),
            oracle_log_path=arts.get("oracle_log_path"),
            pack_hash_expected=arts.get("pack_hash"),
            cmd=arts.get("cmd"),
        )
        return b

    def session_success_is_not_done(self, session_event: dict[str, Any]) -> bool:
        """Green log / session JSONL success without DoneBundle → not publishable."""
        if session_event.get("status") in ("success", "ok", "green") and not session_event.get(
            "done_bundle"
        ):
            return True  # is_not_done
        try:
            DoneBundle.from_mapping(session_event.get("done_bundle"))
            return False
        except StopGateError:
            return True
