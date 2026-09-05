#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""One-shot splice: drop DHx/stamps/index defs from cosmos_dispatch.py.

Does not delete. Predecessor already staged under
_delme/predispose_dispatch_f39_stamps_20260831T182020Z/.
"""
from __future__ import annotations

from pathlib import Path

P = Path(__file__).resolve().parent / "cosmos_dispatch.py"
POINTER = """# ---------------------------------------------------------------------------
# stamps, DHx, collector index (R5 ACCEPT, R6 lock ` · `, R7 sidecar+lock)
# PHASE 4 seam: helpers live in cosmos_dispatch_stamps and are re-exported
# above -- same objects, not copies -- so dispatch() / job_status /
# cosmos_node_worker / cosmos_dispatcher_daemon keep working unchanged.
# Additive.
# ---------------------------------------------------------------------------


"""
SIDECAR = '''def write_inbox_sidecar(inbox: Path, row: dict) -> dict:
    inbox.parent.mkdir(parents=True, exist_ok=True)
    tmp = inbox.with_suffix(inbox.suffix + ".tmp")
    tmp.write_text(json.dumps(row, indent=1, default=str), encoding="utf-8")
    tmp.replace(inbox)
    return {"wrote": True, "path": str(inbox)}


'''


def main() -> int:
    src = P.read_text(encoding="utf-8")
    start = src.find(
        "# ---------------------------------------------------------------------------\n"
        "# stamps, DHx, collector index"
    )
    if start < 0:
        print("NO_START")
        return 2
    crit = src.find(
        "# ---------------------------------------------------------------------------\n"
        "# stage-5 critic visibility",
        start,
    )
    if crit < 0:
        print("NO_CRIT")
        return 2
    rest = src[crit:]
    if SIDECAR not in rest:
        print("NO_SIDECAR")
        return 2
    rest = rest.replace(SIDECAR, "", 1)
    new = src[:start] + POINTER + rest
    P.write_text(new, encoding="utf-8", newline="\n")
    print("lines", new.count("\n") + 1)
    print("bytes", len(new.encode("utf-8")))
    print("defines_iso", "def _iso_now" in new)
    print("defines_dhx", "def append_dhx_marker" in new)
    print("defines_inbox", "def write_inbox_sidecar" in new)
    print("import_stamps", "from cosmos_dispatch_stamps import" in new)
    print("pointer", "live in cosmos_dispatch_stamps" in new)
    print("dispatch_fn", "def dispatch" in new)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
