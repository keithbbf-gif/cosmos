"""Project a legend onto a door.

Strong doors already own the loop, the tool pool, and the worktree. They get a thin
user message: the mission and one contract line. The wrapper lands in the file that
door actually loads (AGENTS.md), and only if that file is absent.

Weak doors get WRAP on the system turn and STYLE on the user tail. Skills are not
pasted. A none-door gets the outfit card in the user turn and nothing that claims
a harness ran.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from g47.contracts import FIRST_LINE, Legend
from g47.doors import Door
from g47.refuse import Refuse

_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")


@dataclass(frozen=True)
class Projection:
    strength: str
    system: str
    user: str
    files: dict[str, str] = field(default_factory=dict)
    contract_line: str = ""


def _contract_line(legend: Legend) -> str:
    allowed = FIRST_LINE.get(legend.role, ())
    shown = "|".join(allowed) if allowed else "NONE"
    ping = " ping=NONE then HERO_OK" if legend.ping else ""
    return (
        f"CONTRACT role={legend.role} first_line={shown} "
        f"what={legend.what} where={legend.where or 'worktree'}{ping}"
    )


def _check(legend: Legend, door: Door) -> None:
    if not legend.role or not legend.model:
        raise Refuse("PACK_INCOMPLETE", "role and model are required")
    if legend.kind() == "daemon":
        raise Refuse("DAEMON_NOT_LLM")
    if legend.kind() == "dispose":
        raise Refuse("CCR_NOT_A_DOOR", "CCr is the pen, not a spawned coder")
    if legend.role == "ORC" and door.id in ("codex", "pi", "opencode", "dsh", "claude", "copilot"):
        raise Refuse("ORC_NO_CODING", door.id)
    for item in legend.context:
        if " · " in item or "\n" in item:
            raise Refuse("NO_CONTEXT", "context is a list of paths, not a joined string")
    if door.strength == "strong" and legend.kind() == "orch":
        raise Refuse("ORC_NO_CODING", door.id)
    blob = "\n".join((legend.task, legend.style, legend.wrap))
    lowered = blob.lower()
    if "<pointer>" in lowered or "see docs/" in lowered:
        raise Refuse("POINTER_IN_TASK", "copy the bytes into the cell; a pointer is not a mission")
    if door.id == "codex" and not legend.wrap.strip():
        raise Refuse("EMPTY_HOUSE", "Codex cwd needs AGENTS.md. An empty attempt is not a review.")
    if door.agents_file and legend.wrap and (_DATE.search(legend.wrap) or "PR #" in legend.wrap):
        raise Refuse("PREFIX_VOLATILE", "AGENTS.md has no dates and no PR ids")
    if legend.prefill_none and door.id != "openrouter":
        raise Refuse("PREFILL_NOT_THIS_DOOR", door.id)
    for skill in legend.skills:
        if "\n" in skill or len(skill) > 240:
            raise Refuse("SKILL_BODY", "skills are paths, not pasted bodies")


def project(legend: Legend, door: Door) -> Projection:
    _check(legend, door)
    line = _contract_line(legend)
    files: dict[str, str] = {}
    mission = _join(legend.task, line)
    if mission:
        files["TASK.md"] = mission + "\n"
    files["SKILL.md"] = (
        "\n".join(legend.skills) + "\n" if legend.skills else "none extra\n"
    )

    if door.strength == "strong":
        # Native loop owns tools. WRAP is not restuffed into the user turn.
        # STYLE is a tail only when the caller named one.
        if door.agents_file and legend.wrap:
            files[door.agents_file] = _nl(legend.wrap)
        elif legend.wrap:
            files["WRAP.md"] = _nl(legend.wrap)
        user = _join(legend.style, legend.task, line)
        return Projection("strong", "", user, files, line)

    if door.strength == "weak":
        # STYLE on the system turn canceled tool calls. It stays on the user tail.
        system = legend.wrap.strip()
        tail = _join(legend.style, legend.task, line)
        if legend.wrap:
            files["WRAP.md"] = _nl(legend.wrap)
        return Projection("weak", system, tail, files, line)

    card = _outfit_card(legend, line)
    return Projection("none", "", card, files, line)


def _join(*parts: str) -> str:
    return "\n\n".join(p.strip() for p in parts if p and p.strip())


def _nl(text: str) -> str:
    return text if text.endswith("\n") else text + "\n"


def _outfit_card(legend: Legend, line: str) -> str:
    paths = "\n".join(f"- {p}" for p in legend.context) or "- (none)"
    return _join(
        "OUTFIT (no harness is running; do not claim one ran)",
        f"Role: {legend.role}",
        f"Model pin: {legend.model}",
        line,
        "Context paths:\n" + paths,
        legend.wrap,
        legend.style,
        legend.task,
    )
