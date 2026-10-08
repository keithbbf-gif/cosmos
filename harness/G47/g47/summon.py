"""One spawn plan. Build the pack, the argv, and the size. Do not loop.

Execute is a single process, and only when the caller passes execute=True,
the door is seated, and the binary was found by doctor. There is no fallback
model and no retry that clears a failed grade.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import asdict, dataclass, field
from pathlib import Path

from g47.contracts import Legend, OutputContract
from g47.doors import Door, get_door
from g47.grade import Grade, grade
from g47.pack import Projection, project
from g47.refuse import Refuse
from g47.scars import check_slug
from g47.size import Size, approx_tokens, compute

ARGV_LIMIT = 7000
PROMPT_FIT = 1200


@dataclass
class Plan:
    door: str
    seated: bool
    strength: str
    argv: list[str]
    system: str
    user: str
    files: dict[str, str]
    size: Size
    turns: int
    grade_mode: str
    contract_line: str
    note: str
    env: dict[str, str] = field(default_factory=dict)
    rail: dict | None = None

    def to_json(self) -> str:
        payload = asdict(self)
        payload["size"] = asdict(self.size)
        return json.dumps(payload, indent=1) + "\n"


def _model_arg(door: Door, model: str) -> str:
    if door.id == "opencode" and not model.startswith("openrouter/"):
        return "openrouter/" + model
    return model


def _prompt_text(proj: Projection) -> str:
    """Long tails were dropped by OpenCode and hung Codex. The mission stays in TASK.md."""
    if len(proj.user) <= PROMPT_FIT:
        return proj.user
    names = [n for n in ("AGENTS.md", "WRAP.md", "TASK.md") if n in proj.files]
    shown = " and ".join(names) if names else "TASK.md"
    return f"Read {shown} in this directory. Complete TASK.md. Stay in this directory."


def _finish(door: Door, argv: list[str]) -> list[str]:
    for flag in door.forbid:
        if flag in argv:
            raise Refuse("FORBID_FLAG", flag)
    joined = " ".join(argv)
    if len(joined) > ARGV_LIMIT:
        raise Refuse("ARGV_TOO_LONG", f"{len(joined)} chars")
    return argv


def _pi(door: Door, legend: Legend, proj: Projection) -> list[str]:
    # call_pi_glm.py measured this order. -p is the mode; the item is the last arg.
    argv = [
        "pi.cmd", "-p",
        "--provider", "zai",
        "--model", legend.model,
        "--tools", "read,write,edit",
    ]
    body = proj.files.get("WRAP.md", "")
    if body:
        if len(body) <= 1500:
            argv.extend(("--system-prompt", body.rstrip("\n")))
        else:
            argv.extend(("--system-prompt", "Read WRAP.md in this directory. It is the wrapper."))
    argv.append("--no-session")
    argv.append(_prompt_text(proj))
    return _finish(door, argv)


def _openrouter_pin(model: str) -> bool:
    """A slash id or a :floor suffix is an OpenRouter pin, not a native Codex sku."""
    low = model.lower()
    return "/" in low or low.endswith(":floor")


def _codex(door: Door, legend: Legend, proj: Projection, *, write: bool) -> list[str]:
    # Do not pass service_tier. Do not pass --ignore-user-config.
    # Current Codex rejects wire_api=chat. An OpenRouter pin carries the
    # responses provider on the argv so the call does not depend on a profile
    # file that still says chat.
    argv = [
        "codex", "exec",
        "--skip-git-repo-check", "--json", "--color", "never",
        "--ephemeral", "-m", legend.model,
    ]
    if _openrouter_pin(legend.model):
        argv.extend((
            "-c", 'model_provider="openrouter"',
            "-c", 'model_providers.openrouter.name="OpenRouter"',
            "-c", 'model_providers.openrouter.base_url="https://openrouter.ai/api/v1"',
            "-c", 'model_providers.openrouter.env_key="OPENROUTER_API_KEY"',
            "-c", 'model_providers.openrouter.wire_api="responses"',
        ))
    if legend.role in ("JUDGE", "WOMBAT"):
        argv.extend(("--sandbox", "read-only"))
    elif write:
        argv.append("--approve-for-me")
    argv.append("--")
    argv.append(_prompt_text(proj))
    return _finish(door, argv)


def _opencode(door: Door, legend: Legend, proj: Projection) -> list[str]:
    argv = ["opencode.cmd", "run", "--dir", legend.where or ".", "-m", _model_arg(door, legend.model)]
    argv.extend(("--", _prompt_text(proj)))
    return _finish(door, argv)


def _dsh(door: Door, proj: Projection) -> list[str]:
    argv = ["dsh.cmd", "--profile", "headless", _prompt_text(proj)]
    return _finish(door, argv)


def _argv(door: Door, legend: Legend, proj: Projection, *, write: bool) -> list[str]:
    if door.id in ("openrouter", "none", "antigravity"):
        return []
    if door.id == "pi":
        return _pi(door, legend, proj)
    if door.id == "codex":
        return _codex(door, legend, proj, write=write)
    if door.id == "opencode":
        return _opencode(door, legend, proj)
    if door.id == "dsh":
        return _dsh(door, proj)
    if door.id == "grok":
        return _finish(door, ["grok.exe"])
    if not door.seated and door.id != "claude" and not door.binary:
        return []
    argv: list[str] = list(door.binary)
    argv.extend(door.extra)
    if door.model_flag:
        argv.extend(door.model_flag)
        argv.append(_model_arg(door, legend.model))
    if door.work_flag and legend.where:
        argv.extend(door.work_flag)
        argv.append(legend.where)
    if door.prompt_flag:
        argv.extend(door.prompt_flag)
        argv.append(_prompt_text(proj))
    return _finish(door, argv)


def plan(
    legend: Legend,
    door_name: str,
    *,
    prompt_tokens: int | None = None,
    write: bool = False,
) -> Plan:
    door = get_door(door_name)
    check_slug(door.id, legend.model)
    proj = project(legend, door)
    argv = _argv(door, legend, proj, write=write)
    blob = proj.system + "\n" + proj.user
    tokens = prompt_tokens if prompt_tokens is not None else approx_tokens(blob)
    sized = compute(
        legend.window if legend.window is not None else None,
        legend.cached_tokens,
        tokens,
        legend.optimum,
        keep_under=door.keep_under,
        estimate=prompt_tokens is None,
    )
    rail = None
    if door.id == "openrouter":
        # The rail owns HTTP. Routing stays off so the pin cannot be swapped.
        # max_tokens is the computed MAX, never a baked 2048.
        rail = {
            "model": legend.model,
            "allow_fallbacks": False,
            "routing": "off",
            "max_tokens": sized.max_tokens,
            "optimum": sized.optimum,
            "system": proj.system,
            "user": proj.user,
            "prefill": "NONE\n" if legend.prefill_none else None,
            "wrapper_bound": not legend.prefill_none,
            "tools": "not invented",
        }
    return Plan(
        door=door.id,
        seated=door.seated,
        strength=door.strength,
        argv=argv,
        system=proj.system,
        user=proj.user,
        files=dict(proj.files),
        size=sized,
        turns=door.turns,
        grade_mode=door.grade,
        contract_line=proj.contract_line,
        note=door.note,
        rail=rail,
    )


def materialize(plan_obj: Plan, worktree: Path) -> list[Path]:
    """Write pack files inside the attempt worktree. Refuse a live/ path."""
    root = worktree.resolve()
    if root.name.lower() == "live" or "\\live\\" in str(root).lower() or "/live/" in str(root).lower():
        raise Refuse("LIVE_TREE", str(root))
    written: list[Path] = []
    root.mkdir(parents=True, exist_ok=True)
    for name, body in plan_obj.files.items():
        if name.startswith(("/", "\\")) or ":" in name or ".." in Path(name).parts:
            raise Refuse("PATH_ESCAPE", name)
        dest = (root / name).resolve()
        try:
            dest.relative_to(root)
        except ValueError:
            raise Refuse("PATH_ESCAPE", name)
        if dest.exists() and name == "AGENTS.md":
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(body, encoding="utf-8", newline="\n")
        written.append(dest)
    (root / "g47-plan.json").write_text(plan_obj.to_json(), encoding="utf-8", newline="\n")
    return written


_MODEL_KEYS = ("served_model", "response_model", "model")


def _accept_model_id(value: object) -> str:
    """A model id is one token, at most 120 characters. Null and prose are empty."""
    if not isinstance(value, str):
        return ""
    text = value.strip()
    if not text or text in {"None", "null"} or " " in text or len(text) > 120:
        return ""
    return text


def _collect_model_ids(node: object, found: list[str]) -> None:
    """Walk objects and arrays. String fields are not parsed again."""
    if isinstance(node, dict):
        for key in _MODEL_KEYS:
            if key in node:
                got = _accept_model_id(node[key])
                if got:
                    found.append(got)
        for key, value in node.items():
            if key in _MODEL_KEYS:
                continue
            if isinstance(value, (dict, list)):
                _collect_model_ids(value, found)
        return
    if isinstance(node, list):
        for item in node:
            _collect_model_ids(item, found)


def served_model(text: str) -> str:
    """The model id a process actually returned.

    Accepts one JSON document or JSONL. The keys are ``model``,
    ``served_model``, and ``response_model``. Two different ids, a missing
    key, a null, or prose inside a string field all return empty. The argv
    pin is not a substitute.
    """
    blob = (text or "").strip()
    if not blob:
        return ""
    nodes: list[object] = []
    try:
        nodes.append(json.loads(blob))
    except json.JSONDecodeError:
        for line in blob.splitlines():
            piece = line.strip()
            if not piece:
                continue
            try:
                nodes.append(json.loads(piece))
            except json.JSONDecodeError:
                continue
    found: list[str] = []
    for node in nodes:
        _collect_model_ids(node, found)
    unique = list(dict.fromkeys(found))
    if len(unique) == 1:
        return unique[0]
    return ""


def process_observation(mouth: str, code: int) -> dict[str, object]:
    """What a finished process may claim. It never claims a seat."""
    return {
        "seated": False,
        "served": served_model(mouth),
        "code": code,
        "mouth": mouth,
    }


def execute(plan_obj: Plan, worktree: Path) -> tuple[int, str, Grade]:
    """One process. No retry. No model swap."""
    door = get_door(plan_obj.door)
    if door.id == "grok":
        raise Refuse("GROK_NOT_A_WORKER", "Gitur Cursor BUILD only. Do not start grok.exe.")
    if door.id == "cosmos-code":
        raise Refuse("EXECUTE_IS_RAIL", "cosmos-code runs in its own package; G47 only builds its thin pack")
    if not door.seated:
        raise Refuse("UNSEATED", door.id)
    if not door.binary:
        raise Refuse("NO_BINARY", door.id)
    if door.key_file and not Path(door.key_file).is_file():
        raise Refuse("NO_KEY", door.id)
    exe = door.binary[0]
    if shutil.which(exe) is None:
        raise Refuse("NO_BINARY", exe)
    materialize(plan_obj, worktree)
    flags = subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0
    # Stdin closed: an open stdin made Codex wait on "additional input" and hide the model id.
    proc = subprocess.run(
        plan_obj.argv,
        cwd=str(worktree),
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        creationflags=flags,
        shell=False,
    )
    mouth = proc.stdout or ""
    contract = OutputContract(
        role=_role_from_line(plan_obj.contract_line),
        what=_what_from_line(plan_obj.contract_line),
        ping="ping=" in plan_obj.contract_line,
    )
    graded = grade(mouth, contract, door_grade=plan_obj.grade_mode, worktree_obeyed=None)
    return proc.returncode, mouth, graded


def _role_from_line(line: str) -> str:
    for part in line.split():
        if part.startswith("role="):
            return part.split("=", 1)[1]
    return "CODER"


def _what_from_line(line: str) -> str:
    for part in line.split():
        if part.startswith("what="):
            return part.split("=", 1)[1]
    return "text"
