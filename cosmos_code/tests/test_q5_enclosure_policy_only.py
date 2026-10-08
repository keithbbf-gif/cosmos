"""Q5 — enclosure labeled policy_only only (NOT wipe-proof).

Do not claim Job Object / wipe-replay until Q1–Q4 green AND real enclosure attaches.
"""

from __future__ import annotations

import pytest
from cosmos_code.safety.enclosure import (
    UnsandboxedRetryRefused,
    detect_enclosure,
    enclosure_is_wipe_proof,
    refuse_unsandboxed_retry,
)


def test_enclosure_labeled_policy_only():
    status = detect_enclosure()
    assert status.reason == "policy_only"
    assert status.label() == "policy_only"
    assert status.wipe_proof is False
    assert status.available is False or status.kind == "none"


def test_not_wipe_proof():
    status = detect_enclosure()
    assert enclosure_is_wipe_proof(status) is False
    # explicit: policy_only must never be advertised as wipe-complete
    assert "policy_only" in status.reason
    assert not (status.wipe_proof and status.reason == "policy_only")


def test_refuse_unsandboxed_retry_always_raises():
    with pytest.raises(UnsandboxedRetryRefused):
        refuse_unsandboxed_retry()
    with pytest.raises(UnsandboxedRetryRefused):
        refuse_unsandboxed_retry(why="bwrap_missing")
