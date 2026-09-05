#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""One-shot extract of the dispatch job-source seam into cosmos_dispatch_jobs."""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "cosmos" / "cosmos_dispatch.py"
OUT = REPO / "cosmos" / "cosmos_dispatch_jobs.py"

HEADER = r'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_dispatch_jobs - job-source builders (R4: grok flags locked).

Split out of `cosmos_dispatch.py` (PHASE 4, `docs/CORE_RESTRUCTURE.md`) along a
seam that already existed:

    # ---------------------------------------------------------------------------
    # job source (R4: grok flags locked; cursor/claude provisional)
    # ---------------------------------------------------------------------------

This is the dispatch harness's *pure* job-source layer. Kind + task + paths
in, a Python job script string out -- no runtime root identity, no DHx stamp,
no collector index, no queue drop. `cosmos_dispatch` re-exports every name
below, so every existing importer of these names off cosmos_dispatch keeps
working unchanged.

What lives here, and why it is one piece:
  * `_py_path` / `_job_helpers_block` -- the emitted job's bind/emit prelude
  * `_grok_job` / `_cursor_job` / `_codex_job` / `_claude_job` / `_worker_job`
    -- one builder per kind
  * `render_job` -- the kind switch that callers (dispatch()) already used

What deliberately did NOT move: `dispatch()` / `job_status` / `run_gate`.
Those own the queue drop, the collector index, and the stage-6 live-tree
gate. Pulling them out would mean passing the harness into a free function
-- coupling wearing a module's clothes, not a seam. The seam is exactly
here, at the boundary where a job script is a string.

Closed-over constants (`WORKER`, `DEFAULT_MODEL`, `GROK_MAX_TURNS`,
`CURSOR_*`, `CLAUDE_MODEL`, `CLAUDE_KINDS`, `WORKER_KINDS`) are duplicated
here with the same values dispatch already published. Dispatch re-exports
the FUNCTIONS as the same objects (not copies). Importing the constants
the other way would cycle (dispatch imports this module).

Does not modify kernel / ledger / sched / service. No hard-coded drive
literals. Cursor/codex keys are READ at job runtime from a path; never
baked. kind_live for cursor/claude stays UNPROVEN (F-69 H6; no key chase).
"""
from __future__ import annotations

import json
from pathlib import Path

from cosmos_dispatch_workspace import DispatchError  # noqa: E402

# Values MUST match cosmos_dispatch.py. Dispatch re-exports the FUNCTIONS
# (same objects). These names are the builders' closed-over vocabulary, not
# a second identity table.
WORKER = "cosmos-dispatch"
DEFAULT_MODEL = "grok-4.6"
GROK_MAX_TURNS = "60"
CURSOR_BASE = "https://api.cursor.com"
CURSOR_REPO = "https://github.com/keithbbf-gif/cosmos"
CURSOR_REF = "main"
CLAUDE_MODEL = "claude-fable-5"
CLAUDE_KINDS = frozenset({"claude", "sonnet", "haiku", "ssa"})
WORKER_KINDS = frozenset({"gem", "oa"})


def _lane_model(kind: str, model: str) -> str:
    """Preserve render_job's previous call to resolve_lane_model.

    Lazy-imported so this module does not import cosmos_dispatch at load
    time (dispatch imports us). By the time a job is rendered, dispatch
    is fully loaded.
    """
    from cosmos_dispatch import resolve_lane_model
    return resolve_lane_model(kind, model)


# ---------------------------------------------------------------------------
# job source (R4: grok flags locked; cursor/claude provisional)
# ---------------------------------------------------------------------------

'''


def main() -> int:
    lines = SRC.read_text(encoding="utf-8").splitlines(True)
    chunk = "".join(lines[636:1085])
    old = "                           resolve_lane_model(kind, model), kind)"
    new = "                           _lane_model(kind, model), kind)"
    if old not in chunk:
        raise SystemExit("resolve_lane_model call not found in chunk")
    chunk = chunk.replace(old, new, 1)
    OUT.write_text(HEADER + chunk, encoding="utf-8")
    print("wrote", OUT, "bytes", OUT.stat().st_size)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
