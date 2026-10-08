"""Door specs are data. Argv stays in G47. A bad row refuses at load."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path

from g47.doors import DOORS
from g47.refuse import Refuse

LAYERS = (
    "l1_role", "l2_model", "l3_harness", "l4_wrapper",
    "l5_skills", "l6_tools", "l7_enviro", "l8_mission",
)
STATES = frozenset({"native", "carried", "none", "file"})
SPEC_DIR = Path(__file__).resolve().parent / "specs"


@dataclass(frozen=True)
class DoorSpec:
    id: str
    family: str
    strength: str
    grade: str
    binds: dict[str, str]
    via: str


def load_spec(path: Path) -> DoorSpec:
    try:
        raw = tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:
        raise Refuse("SPEC_INVALID", f"{path.name}: {exc}") from exc
    binds = raw.get("binds")
    if not isinstance(binds, dict):
        raise Refuse("SPEC_INVALID", f"{path.name}: binds")
    missing = [layer for layer in LAYERS if layer not in binds]
    if missing:
        raise Refuse("SPEC_INVALID", f"{path.name}: missing {missing}")
    for layer, state in binds.items():
        if layer not in LAYERS or state not in STATES:
            raise Refuse("SPEC_INVALID", f"{path.name}: {layer}={state}")
    strength = str(raw.get("strength") or "")
    if strength not in ("strong", "weak", "none"):
        raise Refuse("SPEC_INVALID", f"{path.name}: strength")
    door_id = str(raw.get("id") or "")
    if door_id not in DOORS:
        raise Refuse("SPEC_UNKNOWN_DOOR", door_id)
    if str(raw.get("via") or "") != "g47":
        raise Refuse("SPEC_INVALID", f"{path.name}: via must be g47")
    return DoorSpec(
        id=door_id,
        family=str(raw.get("family") or ""),
        strength=strength,
        grade=str(raw.get("grade") or ""),
        binds={str(k): str(v) for k, v in binds.items()},
        via="g47",
    )


def load_all(directory: Path | None = None) -> dict[str, DoorSpec]:
    root = directory or SPEC_DIR
    found: dict[str, DoorSpec] = {}
    for path in sorted(root.glob("*.toml")):
        spec = load_spec(path)
        found[spec.id] = spec
    if not found:
        raise Refuse("SPEC_INVALID", "no door specs")
    return found


def negotiate(spec: DoorSpec) -> DoorSpec:
    """A strong door does not get its native loop restuffed. An unbound mission refuses."""
    if spec.binds["l8_mission"] == "none" or spec.binds["l1_role"] == "none":
        raise Refuse("LAYER_UNBOUND", spec.id)
    if spec.strength == "strong" and spec.binds["l4_wrapper"] == "carried":
        raise Refuse("RESTUFF", spec.id)
    if spec.strength == "weak" and spec.binds["l6_tools"] == "native":
        raise Refuse("FAKE_TOOLS", spec.id)
    return spec
