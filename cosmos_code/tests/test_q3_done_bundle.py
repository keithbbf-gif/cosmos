"""Q3 — DoneBundle refuse."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest
from cosmos_code.verify.stop_gate import DoneBundle, StopGate, StopGateError


def _h(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


@pytest.fixture
def gate(tmp_path: Path):
    return StopGate(tmp_path), tmp_path


def test_done_without_bundle_refused(gate):
    sg, root = gate
    with pytest.raises(StopGateError) as ei:
        sg.refuse_if_incomplete(None)
    assert ei.value.code == "INCOMPLETE_BUNDLE"
    with pytest.raises(StopGateError):
        sg.refuse_if_incomplete({"diff_hash": "abc"})  # partial


def test_done_mismatched_diff_hash_refused(gate):
    sg, root = gate
    diff = b"real-diff-bytes"
    bundle = DoneBundle(
        diff_hash=_h("wrong"),
        oracle_id="oid1",
        oracle_log_hash=_h("olog"),
        pack_hash=_h("pack"),
        cmd_hash=_h("cmd"),
    )
    with pytest.raises(StopGateError) as ei:
        sg.accept_done(
            bundle,
            artifacts={
                "diff_bytes": diff,
                "oracle_log": "olog",
                "pack_hash": _h("pack"),
                "cmd": "cmd",
            },
        )
    assert ei.value.code == "DIFF_HASH_MISMATCH"


def test_done_full_bundle_accepted(gate):
    sg, root = gate
    diff = b"patch-v1"
    olog = "oracle ok\n"
    cmd = "pytest -q"
    pack = _h("head+paths")
    bundle = DoneBundle(
        diff_hash=hashlib.sha256(diff).hexdigest(),
        oracle_id="oid-add",
        oracle_log_hash=_h(olog),
        pack_hash=pack,
        cmd_hash=_h(cmd),
    )
    accepted = sg.accept_done(
        bundle,
        artifacts={
            "diff_bytes": diff,
            "oracle_log": olog,
            "pack_hash": pack,
            "cmd": cmd,
        },
    )
    assert accepted.diff_hash == bundle.diff_hash
    # still propose-only — no live/ write implied


def test_green_log_is_not_done(gate):
    sg, root = gate
    event = {"status": "success", "message": "all tests green"}
    assert sg.session_success_is_not_done(event) is True
    # with full bundle it is done (publishable evidence)
    full = {
        "status": "success",
        "done_bundle": {
            "diff_hash": _h("d"),
            "oracle_id": "o",
            "oracle_log_hash": _h("l"),
            "pack_hash": _h("p"),
            "cmd_hash": _h("c"),
        },
    }
    assert sg.session_success_is_not_done(full) is False
