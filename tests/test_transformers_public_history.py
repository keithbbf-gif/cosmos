"""Staged public-history pack: structure, length, novelty fence."""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATE = ROOT / "content" / "transformers-public-history" / "validate.py"


def test_transformers_public_history_validate():
    assert VALIDATE.is_file(), VALIDATE
    ns = runpy.run_path(str(VALIDATE), run_name="not_main")
    # Re-invoke main() so pytest sees the return code.
    rc = ns["main"]()
    assert rc == 0


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT / "content" / "transformers-public-history"))
    from validate import main

    raise SystemExit(main())
