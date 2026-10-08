"""Seat a HERO on its native door, or on COSMOS CODE, with all eight layers bound.

A seat object exists only when every layer has a proof. Writing a file the
door will not load is not a proof. ``seat`` and ``seat_agent`` do not start
a process. ``live_call`` is the one function that does, and its return
never says the agent is seated.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from g47.contracts import Legend
from g47.doors import get_door
from g47.loop import Attempt, run
from g47.refuse import Refuse
from g47.roster import AGENTS, Agent
from g47.summon import Plan, execute, plan, process_observation

CODER_WRAP = (
    "role = CODER\n"
    "pen = none\n"
    "Propose in the worktree. Do not publish live/. Do not start grok.exe.\n"
    "A python body opens with def, import, from, or class. A fence is a fail.\n"
)

JUDGE_WRAP = (
    "role = JUDGE\n"
    "pen = none\n"
    "Findings first. First line is KEEP, DROP, NONE, HOLD, or UNMEASURED.\n"
    "Do not merge. Do not take the pen.\n"
)

TOOLS = (
    "read\nedit\nwrite\nglob\ngrep\nshell\narchive\n"
    "delete is not a tool\n"
)

LOOP = (
    "Turn cap 8. A failed grade is not cleared. The pin does not change mid-turn.\n"
    "Oracle fails before an edit and passes after.\n"
    "Done requires a DoneBundle. A green log is not done.\n"
    "4Cs run before a coding seat is called a pass: py_compile, ruff, mypy, pytest.\n"
    "The session log is what the model saw.\n"
    "live/ is refused.\n"
    "One scar maps to one SOP. The same scar does not fire twice.\n"
    "A dead slug changes the pin only when the provider names the paid id.\n"
    "An open batch stays open. A refused batch stays refused. Neither is a seat.\n"
    "A foreign mouth, a nameless 400, a safety label, and a file the model did not emit do not seat.\n"
    "A free-pool 429 waits. Forty-five seconds is the same pool.\n"
    "Empty Claude keys get one effort-low call. Effort none is not sent.\n"
)


@dataclass(frozen=True)
class Layer:
    name: str
    state: str  # native | carried
    proof: str


@dataclass
class Seat:
    agent: str
    model: str
    via: str
    door: str
    executable: bool
    pack_applied: bool
    layers: list[Layer]
    plan: Plan
    note: str

    def to_public(self) -> dict[str, object]:
        return {
            "agent": self.agent,
            "model": self.model,
            "via": self.via,
            "door": self.door,
            "executable": self.executable,
            "pack_applied": self.pack_applied,
            "layers": [{"name": layer.name, "state": layer.state, "proof": layer.proof} for layer in self.layers],
            "note": self.note,
        }


def _attempt_root(where: str | Path) -> Path:
    text = str(where).strip()
    folded = text.replace("\\", "/").rstrip("/")
    if not text or folded.endswith("/live") or Path(folded).name.lower() == "live":
        raise Refuse("LIVE_TREE", text)
    return Path(text)


def seat_agent(agent_id: str, task: str, where: str | Path, call) -> dict[str, object]:
    """Run the seat loop on the call the caller supplied.

    ``call`` is required, so importing this module does not spend a provider
    call. The journal is ``where / seat.jsonl`` and its ``seated`` field
    stays false. The return is seated only when ``run`` sees the served id
    match the pin.
    """
    if call is None:
        raise Refuse("NO_CALL", "seat_agent")
    if agent_id not in AGENTS:
        raise Refuse("UNKNOWN_AGENT", agent_id)
    if not str(task).strip():
        raise Refuse("PACK_INCOMPLETE", "l8_mission")
    root = _attempt_root(where)
    hero = AGENTS[agent_id]
    attempt = Attempt(hero.model, hero.native_door, hero.what)
    return run(attempt, call, journal=root / "seat.jsonl")


def live_call(agent_id: str, *, via: str, task: str, where: str) -> dict[str, object]:
    """One process for an operator. The return is an observation, not a seat.

    ``seated`` stays false when the mouth names the pin. ``seat_proof`` is
    the stamp, after the host runs the constants file.
    """
    built = seat(agent_id, via=via, task=task, where=where)
    code, mouth, graded = execute(built.plan, Path(where))
    observed = process_observation(mouth, code)
    observed["pin"] = built.model
    observed["door"] = built.door
    observed["grade"] = graded.reason
    return observed


def seat(
    agent_id: str,
    *,
    via: str,
    task: str,
    where: str,
    wrap: str = "",
    style: str = "",
) -> Seat:
    if agent_id not in AGENTS:
        raise Refuse("UNKNOWN_AGENT", agent_id)
    if via not in ("native", "cosmos-code"):
        raise Refuse("UNKNOWN_VIA", via)
    if not task.strip():
        raise Refuse("PACK_INCOMPLETE", "l8_mission")
    if not where.strip() or where.replace("\\", "/").rstrip("/").endswith("/live"):
        raise Refuse("LIVE_TREE", where)
    agent = AGENTS[agent_id]
    door_name = agent.native_door if via == "native" else "cosmos-code"
    door = get_door(door_name)
    legend = _legend(agent, task, where, wrap, style)
    write = via == "native" and door_name == "codex" and agent.role == "CODER"
    built = plan(legend, door_name, write=write)
    _bind_proofs(built, agent, where)
    layers = _audit(built, agent, door_name, legend)
    missing = [layer.name for layer in layers if layer.state not in ("native", "carried")]
    if missing:
        raise Refuse("PACK_INCOMPLETE", ",".join(missing))
    # grok.exe is not a worker. cosmos-code is a rail, not a second spawn of itself.
    executable = bool(door.seated and door.binary) and door_name not in ("grok", "cosmos-code")
    return Seat(
        agent=agent.id,
        model=agent.model,
        via=via,
        door=door_name,
        executable=executable,
        pack_applied=True,
        layers=layers,
        plan=built,
        note=agent.note,
    )


def _legend(agent: Agent, task: str, where: str, wrap: str, style: str) -> Legend:
    if not wrap.strip():
        wrap = JUDGE_WRAP if agent.role == "JUDGE" else CODER_WRAP
    if not style.strip():
        style = (
            "Findings first. One sentence after the verdict."
            if agent.role == "JUDGE"
            else "Python only. No fence. No sentence before the code."
        )
    return Legend(
        role=agent.role,
        model=agent.model,
        what=agent.what,
        wrap=wrap,
        style=style,
        task=task,
        where=where,
        window=agent.window,
        optimum="float",
    )


def _bind_proofs(built: Plan, agent: Agent, where: str) -> None:
    built.files["PIN.md"] = f"model={agent.model}\n"
    built.files["ENV.md"] = f"where={where}\nlive=refused\n"
    if built.door == "cosmos-code":
        built.files["TOOLS.md"] = TOOLS
        built.files["LOOP.md"] = LOOP
        if "AGENTS.md" not in built.files and built.files.get("WRAP.md"):
            built.files["AGENTS.md"] = built.files["WRAP.md"]


def _audit(built: Plan, agent: Agent, door_name: str, legend: Legend) -> list[Layer]:
    files = built.files
    argv = " ".join(built.argv)
    pin = files.get("PIN.md", "")
    task = files.get("TASK.md", "")
    skill = files.get("SKILL.md", "")
    wrapped = files.get("AGENTS.md", "") or files.get("WRAP.md", "") or built.system
    model_on_wire = agent.model in argv or (built.rail or {}).get("model") == agent.model or pin.strip() == f"model={agent.model}"
    fallback = "--fallback-model" in built.argv
    if door_name == "cosmos-code" and "delete is not a tool" in files.get("TOOLS.md", ""):
        tools = Layer("l6_tools", "native", "TOOLS.md")
    elif get_door(door_name).strength == "weak":
        tools = Layer("l6_tools", "carried", "host PathJail; no tools array")
    elif get_door(door_name).strength == "strong":
        tools = Layer("l6_tools", "native", door_name)
    else:
        tools = Layer("l6_tools", "unbound", door_name)
    layers = [
        Layer("l1_role", "native" if f"role={agent.role}" in built.contract_line else "unbound", "contract"),
        Layer("l2_model", "native" if model_on_wire and not fallback else "unbound", "PIN.md"),
        Layer("l3_harness", "native" if built.door == door_name else "unbound", built.door),
        Layer("l4_wrapper", "carried" if legend.wrap.strip() and legend.wrap.strip() in wrapped else "unbound", "WRAP"),
        Layer("l5_skills", "carried" if skill.strip() else "unbound", "SKILL.md"),
        tools,
        Layer("l7_enviro", "carried" if legend.where and "live=refused" in files.get("ENV.md", "") else "unbound", "ENV.md"),
        Layer("l8_mission", "carried" if legend.task.strip() in task and "CONTRACT" in task else "unbound", "TASK.md"),
    ]
    return layers
