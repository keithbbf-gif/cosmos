"""Day-one installer payload and clock.

The installer file is already on disk when the clock starts, and it already
holds the embeddable CPython 3.14 zip. Unpack is local extraction. The steps
do not fetch, and they do not run npm, cargo, git clone, or a compiler.
cDeck stays out of the payload because a Rust build does not fit the clock.

Live ``install()`` writes ``config/install_key.bin`` in the same call as the
sentinel. This clock leaves that file to ``mint_secrets`` so cold root and
secrets do not both own it. The key and the bearer are created on the peer
machine. They are not members.
"""

from __future__ import annotations

from dataclasses import dataclass

from cosmos_federation import (
    DEFAULT_HOST,
    DEFAULT_PORT,
    INSTALL_BUDGET_S,
    KEY_PASTE_BUDGET_S,
    SOFTWARE_BUDGET_S,
    Refuse,
    bound_int,
    bound_text,
    repo_disposition,
    secret_shape,
)

SCHEMA = "cosmos-federation-package/1"

# Substrings that mean a step left the two-minute clock. Matched on the
# step name and detail, case-insensitive, so a build tool cannot hide in prose.
_BLOCKED: tuple[str, ...] = ("npm", "npx", "cargo", "git clone", "rustc", "compiler")

# Installer-built trees. repo_disposition marks these DEV; they are still
# legal payload when the installer creates them and the name is not a secret.
_BUILT_ROOTS: frozenset[str] = frozenset({"runtime", "app", "wizard"})

# A bare directory is SHIP for cosmos, docs, and kdash, and it would copy
# probes, bytecode, and drafts. Explicit files are the copy set.
_BARE_DIRS: frozenset[str] = frozenset({"cosmos", "docs", "kdash"})


def _parts(rel: str) -> tuple[str, ...]:
    norm = rel.replace("\\", "/")
    return tuple(part for part in norm.split("/") if part not in ("", "."))


@dataclass(frozen=True, slots=True)
class Step:
    """One allowance on the installer clock. ``seconds`` is an int allowance."""

    name: str
    seconds: int
    detail: str

    def __post_init__(self) -> None:
        name = bound_text(self.name, limit=64, name="step")
        seconds = bound_int(self.seconds, lo=1, hi=INSTALL_BUDGET_S, name="seconds")
        detail = bound_text(self.detail, limit=240, name="detail")
        blob = f"{name}\n{detail}".lower()
        if any(token in blob for token in _BLOCKED):
            raise Refuse("TOOL", "blocked tool")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "seconds", seconds)
        object.__setattr__(self, "detail", detail)


@dataclass(frozen=True, slots=True)
class Member:
    """One relative path the installer file already contains."""

    rel: str
    why: str

    def __post_init__(self) -> None:
        rel = bound_text(self.rel, limit=240, name="rel")
        why = bound_text(self.why, limit=240, name="why")
        if secret_shape(why):
            raise Refuse("DENY_MEMBER", "secret shape")
        consider(rel)
        object.__setattr__(self, "rel", rel)
        object.__setattr__(self, "why", why)


def consider(rel: str) -> None:
    """Raise ``DENY_MEMBER`` when ``repo_disposition`` is ``DENY``.

    A SHIP file is accepted. A path under ``runtime/``, ``app/``, or
    ``wizard/`` is accepted when it is not a secret name. Anything else,
    including a bare ``cosmos/`` directory, is ``NOT_SHIP``.
    """
    checked = bound_text(rel, limit=240, name="rel")
    if secret_shape(checked):
        raise Refuse("DENY_MEMBER", "secret shape")
    kind = repo_disposition(checked)
    if kind == "DENY":
        raise Refuse("DENY_MEMBER", "denied path")
    parts = _parts(checked)
    if len(parts) == 1 and parts[0] in _BARE_DIRS:
        raise Refuse("NOT_SHIP", "bare directory")
    if kind == "SHIP":
        return
    if parts and parts[0] in _BUILT_ROOTS:
        return
    raise Refuse("NOT_SHIP", "not a ship path")


def _clock(table: tuple[Step, ...]) -> None:
    names = [step.name for step in table]
    if len(names) != len(set(names)) or names.count("key_paste") != 1:
        raise Refuse("BUDGET", "key paste")
    paste = next(step for step in table if step.name == "key_paste")
    if paste.seconds != KEY_PASTE_BUDGET_S:
        raise Refuse("BUDGET", "key paste")
    software = sum(step.seconds for step in table if step.name != "key_paste")
    if software > SOFTWARE_BUDGET_S:
        raise Refuse("BUDGET", "software")
    if software + paste.seconds > INSTALL_BUDGET_S:
        raise Refuse("BUDGET", "install")


def steps() -> tuple[Step, ...]:
    """Ordered allowances from unpack to the chat page."""
    table = (
        Step(
            "unpack_runtime",
            20,
            "Extracts the embeddable CPython 3.14 zip already stored under "
            "runtime/. The installer file holds it before the clock starts.",
        ),
        Step(
            "apply_cold_root",
            10,
            "Writes the sentinel, the role directories, and the install record. "
            "The record keeps the tree id. It does not keep a drive letter as "
            "identity, and it does not write the install key.",
        ),
        Step(
            "key_paste",
            KEY_PASTE_BUDGET_S,
            "The person pastes one OpenRouter or xAI key into the wizard. "
            "The installer does not read a browser profile.",
        ),
        Step(
            "mint_secrets",
            10,
            "Mints the loopback bearer and the 32-byte install key on this "
            "machine. Those files are created here and are not payload members.",
        ),
        Step(
            "write_account",
            10,
            "Records the display name, the door, the credential id, and the cap. "
            "The account object does not hold key bytes.",
        ),
        Step(
            "bind_loopback",
            15,
            f"Listens on {DEFAULT_HOST}:{DEFAULT_PORT} with bearer auth. "
            "Remote bind is outside this step.",
        ),
        Step(
            "open_chat_page",
            25,
            "Opens the day-one chat page from app/dayone.html on the loopback "
            "origin. The page holds neither the bearer nor the pasted key.",
        ),
    )
    _clock(table)
    return table


def total_seconds() -> int:
    """Sum of ``steps()``. Equal to that sum and within the install budget."""
    table = steps()
    total = sum(step.seconds for step in table)
    if total > INSTALL_BUDGET_S:
        raise Refuse("BUDGET", "install")
    return total


_MEMBER_ROWS: tuple[tuple[str, str], ...] = (
    (
        "runtime/python-3.14.8-embed-amd64.zip",
        "Embeddable CPython 3.14.8 already packed in the installer. Unpack extracts it.",
    ),
    (
        "cosmos/__init__.py",
        "Package marker for the kernel slice. The cosmos directory itself is not a member.",
    ),
    (
        "cosmos/cosmos.py",
        "CLI entry. The peer runs it with the unpacked interpreter.",
    ),
    (
        "cosmos/cosmos_kernel.py",
        "install and Kernel. The module is copied. The key file is not.",
    ),
    (
        "cosmos/cosmos_paths.py",
        "Sentinel and role table. Identity is the tree id.",
    ),
    (
        "cosmos/cosmos_ledger.py",
        "Append-only ledger the kernel opens. One ledger, not a second wallet.",
    ),
    (
        "cosmos/cosmos_lock.py",
        "Kernel import, copied as a file.",
    ),
    (
        "cosmos/cosmos_mail.py",
        "Kernel import, copied as a file.",
    ),
    (
        "cosmos/cosmos_sched.py",
        "Kernel import, copied as a file.",
    ),
    (
        "cosmos/cosmos_validate.py",
        "Kernel import, copied as a file.",
    ),
    (
        "cosmos/cosmos_service.py",
        "Loopback serve behavior. The chat step opens the day-one page, not kdash.",
    ),
    (
        "cosmos/cosmos_spend.py",
        "Spend reserve the kernel already uses. The day-one cap stays the policy cap.",
    ),
    (
        "cosmos/cosmos_openrouter_rail.py",
        "OpenRouter door module. The vendor key file is created on the machine.",
    ),
    (
        "cosmos/cosmos_packet.py",
        "Imported by the OpenRouter rail at load. Copied as a file.",
    ),
    (
        "cosmos/cosmos_rail_base.py",
        "Imported by the OpenRouter rail at load. Copied as a file.",
    ),
    (
        "kdash/index.html",
        "Telemetry page the serve banner already names. Not the wizard and not the chat.",
    ),
    (
        "wizard/wizard.html",
        "Day-one wizard page. Static file the installer already contains.",
    ),
    (
        "wizard/wizard.css",
        "Wizard style. Static file, no build step.",
    ),
    (
        "wizard/wizard.js",
        "Wizard script. Static file. The pasted key is not stored in the page.",
    ),
    (
        "app/dayone.html",
        "Day-one chat page. Static file served on loopback.",
    ),
)


def members() -> tuple[Member, ...]:
    """Installer payload. Each name has already passed ``consider``."""
    table = tuple(Member(rel, why) for rel, why in _MEMBER_ROWS)
    rels = [item.rel for item in table]
    if len(rels) != len(set(rels)):
        raise Refuse("NOT_SHIP", "duplicate member")
    return table


def missing_for_serve(imports: tuple[str, ...]) -> tuple[str, ...]:
    """``cosmos_*.py`` filenames in ``imports`` that ``members()`` does not name.

    Comparison is the filename, so a member ``cosmos/cosmos_kernel.py`` covers
    ``cosmos_kernel.py``. Input order is kept. This does not add files to the
    payload. Names that are not ``cosmos_*.py`` are ignored.
    """
    named = {_parts(item.rel)[-1] for item in members()}
    missing: list[str] = []
    seen: set[str] = set()
    for raw in imports:
        parts = _parts(raw)
        if not parts:
            continue
        name = parts[-1]
        if not name.startswith("cosmos_") or not name.endswith(".py"):
            continue
        if name in named or name in seen:
            continue
        seen.add(name)
        missing.append(name)
    return tuple(missing)


__all__ = [
    "SCHEMA",
    "Member",
    "Step",
    "consider",
    "members",
    "missing_for_serve",
    "steps",
    "total_seconds",
]
