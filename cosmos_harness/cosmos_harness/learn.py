"""Seat a pin the way the catalog pass seated one.

The method is fixed:

1. Classify the observation with ``g47.scars.classify``.
2. Ask ``g47.loop.action_for`` for the one SOP.
3. Append that outcome to the journal, including a stop.
4. Do not edit the SOP table from here. A sentence that matches nothing is
   journaled as ``stop`` and the loop does not sample again.
5. Do not stamp ``seated``. A seat also needs ``same_pin`` and a host that
   actually ran the file. ``seat_proof`` is that second check. It does not
   call a provider.

A new model is seated by a new observation hitting the same function. When
the provider names a shape the table already knows (pcm16, a batch adapter,
empty Claude keys, a foreign mouth), the one confirming call is that shape.
When it names nothing, the detail waits in the journal for a person to add
one row to G47. The harness does not invent the row at runtime. That is how
the October scars were added, and it is how the next one is added.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

from cosmos_harness.job import run_child
from cosmos_harness.layers import scrub_env
from cosmos_harness.refuse import Refuse

_G47 = Path(__file__).resolve().parents[2] / "harness" / "G47"
if str(_G47) not in sys.path:
    sys.path.insert(0, str(_G47))

from g47.loop import Attempt, action_for  # noqa: E402
from g47.scars import classify, same_pin  # noqa: E402

_HOST = r"""
import importlib.util, json, math, sys
path = sys.argv[1]
spec = importlib.util.spec_from_file_location("constants", path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
got = mod.constants()
want = (math.pi, math.sqrt(2), math.e, math.log(1))
tols = (1e-6, 1e-6, 1e-6, 1e-9)
ok = isinstance(got, tuple) and len(got) == 4 and all(abs(float(a) - b) <= t for a, b, t in zip(got, want, tols))
print(json.dumps({"ok": bool(ok)}))
"""


@dataclass(frozen=True)
class SeatStep:
    """One observation, one SOP. ``again`` is the confirming call, not a loop."""

    pin: str
    scar: str
    sop: str
    again: bool
    shape: str
    reason: str


def step(
    pin: str,
    *,
    http: int | None = None,
    detail: str = "",
    mouth: str = "",
    served: str | None = None,
    applied: tuple[str, ...] = (),
    door: str = "openrouter",
    form: str = "text",
    journal: Path | None = None,
) -> SeatStep:
    """Map one provider observation to the one SOP in the G47 table.

    When ``journal`` is set, the outcome is appended, including a stop.
    The line's ``seated`` field stays false. ``seat_proof`` is the only
    function that may say the pin is seated, and only after ``same_pin``
    and a host pass.
    """
    if not pin.strip():
        raise Refuse("EMPTY_PIN", "seat")
    scar = str(classify(http=http, detail=detail, mouth=mouth, served_model=served)["class"])
    action = action_for(Attempt(pin, door, form, applied=applied), scar, detail)
    taken = SeatStep(pin, scar, action.sop, bool(action.again), action.shape, action.reason)
    if journal is not None:
        remember(journal, taken, method=taken.sop, http=http)
    return taken


def remember(path: Path, taken: SeatStep, *, method: str, http: int | None = None) -> None:
    """Append one JSONL line. The line is the memory. It is not a new SOP."""
    path.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "pin": taken.pin,
        "scar": taken.scar,
        "sop": taken.sop,
        "again": taken.again,
        "shape": taken.shape,
        "method": method,
        "http": http,
        "reason": taken.reason,
        "seated": False,
    }
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(row, sort_keys=True) + "\n")


def unmapped(path: Path) -> list[dict[str, object]]:
    """Journal lines whose SOP is a stop. Those details are waiting for a named row."""
    if not path.is_file():
        return []
    rows: list[dict[str, object]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("sop") in {"stop", "no_shape", "batch_unsupported", "batch_open", "foreign_mouth", "not_code", "task_ask", "unemitted", "pool_hold"}:
            rows.append(row)
    return rows


def host_constants(source: str, *, timeout: float = 15.0) -> dict[str, object]:
    """Run ``constants()`` in a child. Credential-shaped env vars are dropped.

    The child prints ``{"ok": true}`` only when the four values match the
    seating tolerances. A classifier label or a story fails this host.
    """
    with tempfile.TemporaryDirectory(prefix="cosmos-host-") as folder:
        target = Path(folder) / "constants.py"
        text = source if source.endswith("\n") else source + "\n"
        target.write_text(text, encoding="utf-8", newline="\n")
        try:
            code, out, err = run_child(
                [sys.executable, "-c", _HOST, str(target)],
                cwd=Path(folder),
                env=scrub_env(dict(os.environ)) | {"PYTHONDONTWRITEBYTECODE": "1"},
                timeout=timeout,
            )
        except Refuse as exc:
            return {"ok": False, "detail": exc.reason}
        except OSError as exc:
            return {"ok": False, "detail": str(exc)[:160]}
        if code == 124:
            return {"ok": False, "detail": "timeout"}
        line = out.strip().splitlines()
        if code != 0 or not line:
            err_lines = (err or out or "host crash").strip().splitlines()
            return {"ok": False, "detail": (err_lines[-1] if err_lines else "host crash")[:160]}
        try:
            payload = json.loads(line[-1])
        except json.JSONDecodeError:
            return {"ok": False, "detail": "host bad json"}
        return payload if isinstance(payload, dict) else {"ok": False, "detail": "host bad json"}


def seat_proof(pin: str, served: object, source: str) -> dict[str, object]:
    """A seat is the pin's own file plus a host pass. Either miss stays unseated."""
    if not same_pin(pin, served):
        return {"seated": False, "scar": "MOUTH_FOREIGN", "served": str(served or ""), "host_ok": False}
    host = host_constants(source)
    ok = bool(host.get("ok"))
    return {
        "seated": ok,
        "scar": None if ok else "HOST_FAIL",
        "served": str(served or ""),
        "host_ok": ok,
    }
