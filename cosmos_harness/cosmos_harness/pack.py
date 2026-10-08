"""Write the eight layer files for one attempt.

Markdown, TOML, JSON, and the Python loop note are the layer bodies. This
module fills the slots the attempt already decided. It does not ask the
model what the pin is.
"""

from __future__ import annotations

import json
from pathlib import Path

from cosmos_harness.layers import LAYER_LANGUAGE, Stack

_ROOT = Path(__file__).resolve().parents[1]
PACK = _ROOT / "pack"


def _read(name: str) -> str:
    return (PACK / name).read_text(encoding="utf-8")


def _fill(text: str, stack: Stack) -> str:
    skills = "\n".join(f"- {item}" for item in stack.skills)
    return (
        text.replace("{{ROLE}}", stack.role)
        .replace("{{MODEL}}", stack.model)
        .replace("{{WHAT}}", stack.what)
        .replace("{{FIRST}}", stack.first_line)
        .replace("{{WRAP}}", stack.wrap)
        .replace("{{STYLE}}", stack.style or "(none)")
        .replace("{{SKILLS}}", skills)
        .replace("{{TASK}}", stack.task)
        .replace("{{CONTRACT}}", stack.contract_line())
        .replace("{{WHERE}}", str(stack.where))
        .replace("{{DOOR}}", stack.door)
        .replace("{{MODE}}", stack.mode)
        .replace("{{ORACLE}}", " ".join(stack.oracle_argv))
    )


def materialize(stack: Stack, dest: Path) -> dict[str, str]:
    """Write the attempt pack. Return the filename to body map.

    L6 is copied as JSON and checked for the eight hand names. L2 is TOML
    the attempt fills. The loop note is the Python control law in Markdown
    so the pack the model can read and the code that runs it say the same cap.
    """
    dest.mkdir(parents=True, exist_ok=True)
    files = {
        "L1_ROLE.md": _fill(_read("L1_ROLE.md"), stack),
        "PIN.toml": _fill(_read("pin.toml"), stack),
        "HARNESS.md": _fill(_read("HARNESS.md"), stack),
        "WRAP.md": stack.wrap + "\n",
        "STYLE.md": (stack.style or "(none)") + "\n",
        "SKILL.md": _fill(_read("L5_SKILLS.md"), stack),
        "TOOLS.json": _read("L6_TOOLS.json"),
        "ENV.md": _fill(_read("ENV.md"), stack),
        "TASK.md": _fill(_read("L8_MISSION.md"), stack),
        "LOOP.md": _read("LOOP.md"),
    }
    tools = json.loads(files["TOOLS.json"])
    names = [item["function"]["name"] for item in tools["tools"]]
    if names != ["read", "glob", "grep", "edit", "write", "archive", "oracle", "worktree"]:
        raise ValueError("L6 hand list drifted")
    if stack.style and stack.style in files["WRAP.md"]:
        raise ValueError("style leaked into WRAP")
    for name, body in files.items():
        (dest / name).write_text(body, encoding="utf-8", newline="\n")
    note = dest / "LAYERS.txt"
    lines = [f"{layer} {language}" for layer, language in LAYER_LANGUAGE.items()]
    note.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    files["LAYERS.txt"] = note.read_text(encoding="utf-8")
    return files
