#!/usr/bin/env py -3.14
"""Review fold: GET only. Model-rater roles + per-model cap."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cosmos"))

from cosmos_review import _selftest as review_selftest  # noqa: E402
from cosmos_model_rater import _selftest as rater_selftest  # noqa: E402


def test_review_fold():
    assert review_selftest() == 0


def test_model_rater_roles_and_cap():
    assert rater_selftest() == 0


def test_service_names_review_and_cap():
    src = (ROOT / "cosmos" / "cosmos_service.py").read_text(encoding="utf-8")
    assert 'parsed.path == "/api/v1/review"' in src
    assert "review_snapshot" in src
    assert "/api/v1/model_rater/cap" in src
    assert "set_model_cap" in src


if __name__ == "__main__":
    raise SystemExit(review_selftest() or rater_selftest())
