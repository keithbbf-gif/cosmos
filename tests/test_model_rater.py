#!/usr/bin/env py -3.14
"""model_rater: local OpenRouter catalog, seats, cost estimate."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "cosmos"))

from cosmos_model_rater import _selftest  # noqa: E402


def main() -> int:
    return _selftest()


if __name__ == "__main__":
    raise SystemExit(main())
