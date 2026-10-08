"""OpenCode door. The npm binary stays where the installer put it.

A strong door already owns the loop and the tools. This module writes the
pack, builds the argv OpenCode was measured with, and grades the worktree.
The mouth is not the grade. ``--auto`` is not passed. The key is an
environment variable, never an argument and never a file this module writes.

Chat returns HTTP 403 for Inkling :free. Those pins, and the roster Ling
pin ``inclusionai/ling-3.0-flash``, are the models this door seats. A
written AGENTS.md is not activation. ``wipe_proof`` stays false. The
journal line keeps ``seated`` false. ``seat`` returns seated only when the
child was assigned, the process emitted one served id, ``same_pin`` matches,
and ``constants()`` passes on the host.

The process tree does not fit in the default active-process cap of 4.
``seat`` calls ``run_child`` with ``active_limit=None`` (kill-on-close, no
count cap). If assignment fails, the child is killed and this function
does not start another process outside the job.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import sqlite3
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

from cosmos_harness.job import run_child
from cosmos_harness.learn import host_constants, step
from cosmos_harness.refuse import Refuse

_G47 = Path(__file__).resolve().parents[2] / "harness" / "G47"
if str(_G47) not in sys.path:
    sys.path.insert(0, str(_G47))

from g47.contracts import FIRST_LINE  # noqa: E402
from g47.pack import Projection  # noqa: E402
from g47.scars import same_pin  # noqa: E402
from g47.summon import ARGV_LIMIT, _accept_model_id, _prompt_text  # noqa: E402

# Pins whose measured door is OpenCode. Inkling :free is also matched by
# seats_on_opencode when the slug contains "inkling", so a new free Inkling
# id does not need a table edit. Paid Ling's native door is this one.
OPENCODE_PINS = (
    "thinkingmachines/inkling:free",
    "thinkingmachines/inkling-small:free",
    "inclusionai/ling-3.0-flash",
)

WRAP = (
    "Stay in this directory.\n"
    "Write only the file TASK.md names.\n"
    "Do not read other drives.\n"
    "Do not ask what the task is.\n"
)

TASK = (
    "Write constants.py in this directory only.\n"
    "First line is import math.\n"
    "Define constants() and return math.pi, math.sqrt(2), math.e, and math.log(1) in that order.\n"
    "No fence.\n"
)

# The catalog run asked for V:\\workspace\\* and OpenCode auto-rejected it.
# Deny that leave. Allow the edit inside this directory. Do not pass --auto.
_PERMISSION = {
    "$schema": "https://opencode.ai/config.json",
    "permission": {
        "external_directory": "deny",
        "edit": "allow",
        "bash": "deny",
        "webfetch": "deny",
        "websearch": "deny",
    },
}

_KEYS = ("served_model", "response_model", "model", "modelID")
_SECRET = re.compile(r"sk-[A-Za-z0-9_\-]{8,}")
_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
_BANNED = ("--auto", "--yolo", "--dangerously-skip-permissions")
_KEEP = (
    "SYSTEMROOT",
    "WINDIR",
    "PATH",
    "PATHEXT",
    "TEMP",
    "TMP",
    "COMSPEC",
    "USERPROFILE",
    "APPDATA",
    "LOCALAPPDATA",
    "HOME",
    "HOMEDRIVE",
    "HOMEPATH",
    "SYSTEMDRIVE",
)


@dataclass(frozen=True)
class OpenCodeResult:
    """One OpenCode process. ``wipe_proof`` is always false."""

    pin: str
    served: str
    code: int
    matched: bool
    host_ok: bool
    seated: bool
    enclosed: bool
    wipe_proof: bool
    scar: str
    argv: tuple[str, ...]
    journal_seated: tuple[bool, ...]

    def to_json(self) -> str:
        payload = asdict(self)
        payload["argv"] = list(self.argv)
        payload["journal_seated"] = list(self.journal_seated)
        return json.dumps(payload, indent=1) + "\n"


def seats_on_opencode(pin: str) -> bool:
    """True for a pin whose chat door cannot seat it, or whose roster door is OpenCode."""
    low = pin.strip().lower()
    if low.startswith("openrouter/"):
        low = low[len("openrouter/"):]
    known = {item.lower() for item in OPENCODE_PINS}
    if low in known:
        return True
    return "inkling" in low and low.endswith(":free")


def model_arg(pin: str) -> str:
    """Prefix ``openrouter/`` once. A second call does not add it again."""
    text = pin.strip()
    low = text.lower()
    if not text or low in {"openrouter/free", "free", ":free"} or low.endswith("/free"):
        raise Refuse("NOT_A_PIN", text)
    if ":free" in low and ":floor" in low:
        raise Refuse("FLOOR_ON_FREE", text)
    if text.startswith("openrouter/"):
        return text
    return "openrouter/" + text


def redact(text: str) -> str:
    """Hide a key that leaked into a process stream. The argv never carries one."""
    return _SECRET.sub("sk-redacted", text or "")


def session_ids(text: str) -> list[str]:
    """Session ids this process printed. Other rows in the database are not this run."""
    found: list[str] = []
    for node in _nodes(text):
        _collect_key(node, "sessionID", found)
    return list(dict.fromkeys(found))


def session_db() -> Path | None:
    """The local OpenCode database. Absent when this machine has no install data."""
    home = os.environ.get("USERPROFILE") or os.environ.get("HOME") or ""
    if not home:
        return None
    path = Path(home) / ".local" / "share" / "opencode" / "opencode.db"
    return path if path.is_file() else None


def served_from_sessions(text: str, db: Path) -> str:
    """The model id OpenCode stored for a session id that appears in ``text``.

    ``session.model`` is a JSON object. The served id is its ``id`` field.
    ``providerID`` is not a second model. Two different ids return empty.
    A database that cannot be read returns empty. This does not invent the
    argv pin.
    """
    ids = session_ids(text)
    if not ids or not db.is_file():
        return ""
    found: list[str] = []
    try:
        con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    except sqlite3.Error:
        return ""
    try:
        for sid in ids:
            try:
                row = con.execute("SELECT model FROM session WHERE id = ?", (sid,)).fetchone()
            except sqlite3.Error:
                return ""
            if row is None:
                continue
            got = _model_cell(row[0])
            if got:
                found.append(got)
    finally:
        con.close()
    unique = list(dict.fromkeys(found))
    if len(unique) == 1:
        return unique[0]
    return ""


def served_for_run(text: str, db: Path | None) -> str:
    """Stream id, otherwise the session row. Disagreement is empty."""
    streamed = served_from_stream(text)
    stored = served_from_sessions(text, db) if db is not None else ""
    if streamed and stored and streamed != stored:
        return ""
    return streamed or stored


def served_from_stream(text: str) -> str:
    """One model id from the process stream. The argv pin is not a substitute.

    The keys are ``model``, ``served_model``, ``response_model``, and
    OpenCode's ``modelID``. Two different ids return empty. Prose returns
    empty. String fields are not parsed again.
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
        _collect(node, found)
    unique = list(dict.fromkeys(found))
    if len(unique) == 1:
        return unique[0]
    return ""


def guard(argv: list[str]) -> None:
    """Refuse ``--auto`` and its aliases when they are flags. The prompt may name them."""
    head = argv[: argv.index("--")] if "--" in argv else argv
    for flag in _BANNED:
        if flag in head:
            raise Refuse("FORBID_FLAG", flag)


def argv_for(pin: str, where: Path, prompt: str) -> list[str]:
    """The measured spawn, plus ``--pure`` and ``--format json``.

    ``--pure`` is a global flag, so it sits before ``run``. ``--format``
    belongs to ``run``. ``--auto`` is absent.
    """
    return [
        "opencode.cmd",
        "--pure",
        "run",
        "--format",
        "json",
        "--dir",
        str(where),
        "-m",
        model_arg(pin),
        "--",
        prompt,
    ]


def prompt_for(pin: str, task: str) -> str:
    """Positional text. A mission longer than the fit limit stays in TASK.md."""
    body = _mission(pin, task).strip()
    files = {"AGENTS.md": WRAP, "TASK.md": body + "\n"}
    return _prompt_text(Projection("strong", "", body, files, ""))


def write_pack(where: Path, *, pin: str, task: str = TASK, wrap: str = WRAP) -> Path:
    """Write TASK.md, SKILL.md, and the permission file. Leave an existing AGENTS.md."""
    root = Path(where).resolve()
    if any(part.lower() == "live" for part in root.parts):
        raise Refuse("LIVE_TREE", str(root))
    if _DATE.search(wrap) or "PR #" in wrap:
        raise Refuse("PREFIX_VOLATILE", "AGENTS.md")
    root.mkdir(parents=True, exist_ok=True)
    agents = root / "AGENTS.md"
    if not agents.exists():
        agents.write_text(wrap if wrap.endswith("\n") else wrap + "\n", encoding="utf-8", newline="\n")
    (root / "TASK.md").write_text(_mission(pin, task), encoding="utf-8", newline="\n")
    (root / "SKILL.md").write_text("none extra\n", encoding="utf-8", newline="\n")
    (root / "opencode.json").write_text(
        json.dumps(_PERMISSION, indent=1) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return root


def child_env(key: str) -> dict[str, str]:
    """A short environment. The key is set here and nowhere else."""
    env = {name: os.environ[name] for name in _KEEP if os.environ.get(name)}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["OPENROUTER_API_KEY"] = key
    return env


def seat(
    pin: str,
    where: Path,
    *,
    key: str,
    task: str = TASK,
    wrap: str = WRAP,
    timeout: float = 300,
) -> OpenCodeResult:
    """One OpenCode process inside the job. No second process if the job refuses."""
    if not key or not key.strip():
        raise Refuse("NO_KEY", "opencode")
    model_arg(pin)
    root = write_pack(where, pin=pin, task=task, wrap=wrap)
    prompt = prompt_for(pin, task)
    built = argv_for(pin, root, prompt)
    guard(built)
    if len(" ".join(built)) > ARGV_LIMIT:
        raise Refuse("ARGV_TOO_LONG", str(len(" ".join(built))))
    found = shutil.which("opencode.cmd")
    if not found:
        _journal(root, pin, served="", http=None, detail="opencode.cmd missing", mouth="")
        raise Refuse("NO_BINARY", "opencode.cmd")
    env = child_env(key)
    launched = [found, *built[1:]]
    try:
        code, out, err = run_child(
            launched,
            cwd=root,
            env=env,
            timeout=timeout,
            active_limit=None,
        )
    except Refuse as exc:
        _journal(root, pin, served="", http=None, detail=exc.reason, mouth="")
        raise
    except OSError as exc:
        _journal(root, pin, served="", http=None, detail="opencode.cmd missing", mouth="")
        raise Refuse("NO_BINARY", str(exc)[:160]) from exc
    clean_out = redact(out)
    clean_err = redact(err)
    (root / "events.jsonl").write_text(clean_out, encoding="utf-8", newline="\n")
    (root / "stderr.txt").write_text(clean_err, encoding="utf-8", newline="\n")
    served = served_for_run(clean_out, session_db())
    http = _http_from_stream(clean_out)
    # The event stream is not a chat mouth. An empty mouth journals a stop
    # instead of a prefill SOP. The file on disk is the grade.
    _journal(root, pin, served=served, http=http, detail="worktree", mouth="")
    source = _constants(root)
    matched = same_pin(pin, served)
    if http == 429:
        host_ok = False
        scar = "UPSTREAM_POOL"
        seated = False
    elif not matched:
        host_ok = False
        scar = "SKU_UNBOUND" if not served else "MOUTH_FOREIGN"
        seated = False
    else:
        host = host_constants(source)
        host_ok = bool(host.get("ok"))
        scar = "" if host_ok else "HOST_FAIL"
        seated = host_ok
    flags = tuple(_journal_flags(root / "seat.jsonl"))
    if any(flags):
        seated = False
        scar = scar or "JOURNAL"
    return OpenCodeResult(
        pin=pin,
        served=served,
        code=code,
        matched=matched,
        host_ok=host_ok,
        seated=seated,
        enclosed=True,
        wipe_proof=False,
        scar=scar,
        argv=tuple(built),
        journal_seated=flags,
    )


def _mission(pin: str, task: str) -> str:
    allowed = "|".join(FIRST_LINE["CODER"])
    line = f"CONTRACT role=CODER what=python first_line={allowed} model={pin}"
    body = task.strip()
    text = f"{body}\n\n{line}\n"
    return text


def _constants(root: Path) -> str:
    path = root / "constants.py"
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8")


def _nodes(text: str) -> list[object]:
    blob = (text or "").strip()
    if not blob:
        return []
    try:
        return [json.loads(blob)]
    except json.JSONDecodeError:
        nodes: list[object] = []
        for line in blob.splitlines():
            piece = line.strip()
            if not piece:
                continue
            try:
                nodes.append(json.loads(piece))
            except json.JSONDecodeError:
                continue
        return nodes


def _collect_key(node: object, key: str, found: list[str]) -> None:
    if isinstance(node, dict):
        if key in node:
            got = _accept_model_id(node[key])
            if got and (key != "sessionID" or got.startswith("ses_")):
                found.append(got)
        for name, value in node.items():
            if name == key:
                continue
            if isinstance(value, (dict, list)):
                _collect_key(value, key, found)
        return
    if isinstance(node, list):
        for item in node:
            _collect_key(item, key, found)


def _model_cell(value: object) -> str:
    """One id from a session.model cell. The JSON object itself is not an id."""
    if not isinstance(value, str):
        return ""
    text = value.strip()
    if text.startswith("{"):
        try:
            node = json.loads(text)
        except json.JSONDecodeError:
            return ""
        if isinstance(node, dict):
            return _accept_model_id(node.get("id"))
        return ""
    return _accept_model_id(text)


def _collect(node: object, found: list[str]) -> None:
    if isinstance(node, dict):
        for key in _KEYS:
            if key in node:
                got = _accept_model_id(node[key])
                if got:
                    found.append(got)
        for key, value in node.items():
            if key in _KEYS:
                continue
            if isinstance(value, (dict, list)):
                _collect(value, found)
        return
    if isinstance(node, list):
        for item in node:
            _collect(item, found)


def _http_from_stream(text: str) -> int | None:
    """Read a status only from an OpenCode error event, not from a timestamp."""
    for line in (text or "").splitlines():
        try:
            node = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(node, dict) or node.get("type") != "error":
            continue
        message = _error_message(node.get("error")).lower()
        if "429" in message or "rate limit" in message or "too many requests" in message:
            return 429
        if re.search(r"\b502\b", message) or "bad gateway" in message:
            return 502
        if re.search(r"\b500\b", message):
            return 500
    return None


def _error_message(error: object) -> str:
    if isinstance(error, str):
        return error
    if not isinstance(error, dict):
        return ""
    data = error.get("data")
    if isinstance(data, dict) and isinstance(data.get("message"), str):
        return data["message"]
    if isinstance(error.get("message"), str):
        return str(error["message"])
    return ""


def _journal(
    where: Path,
    pin: str,
    *,
    served: str,
    http: int | None,
    detail: str,
    mouth: str,
) -> None:
    step(
        pin,
        http=http,
        detail=redact(detail),
        mouth=redact(mouth),
        served=served,
        door="opencode",
        journal=where / "seat.jsonl",
    )


def _journal_flags(path: Path) -> list[bool]:
    if not path.is_file():
        return []
    flags: list[bool] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        flags.append(bool(row.get("seated")))
    return flags
