#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Replace the in-file job-source defs with a re-export banner."""
from __future__ import annotations

from pathlib import Path

SRC = Path(__file__).resolve().parent / "cosmos_dispatch.py"
BANNER = """# ---------------------------------------------------------------------------
# job source (R4: grok flags locked; cursor/claude provisional)
# PHASE 4 seam: builders live in cosmos_dispatch_jobs and are re-exported
# above -- same objects, not copies -- so dispatch() and the grok/cursor/
# claude job files keep working unchanged. Additive.
# ---------------------------------------------------------------------------


"""


def main() -> int:
    text = SRC.read_text(encoding="utf-8")
    start = text.find(
        "# ---------------------------------------------------------------------------\n"
        "# job source (R4: grok flags locked; cursor/claude provisional)\n"
        "# ---------------------------------------------------------------------------\n"
    )
    end = text.find(
        "# ---------------------------------------------------------------------------\n"
        "# stamps, DHx, collector index (R5 ACCEPT, R6 lock ` · `, R7 sidecar+lock)\n"
        "# ---------------------------------------------------------------------------\n"
    )
    if start < 0 or end < 0 or end <= start:
        raise SystemExit(f"seam markers missing start={start} end={end}")
    new = text[:start] + BANNER + text[end:]
    SRC.write_text(new, encoding="utf-8")
    print("spliced", SRC, "bytes", SRC.stat().st_size,
          "lines", new.count("\n") + 1)
    print("removed", text.count("\n") - new.count("\n"), "lines")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
