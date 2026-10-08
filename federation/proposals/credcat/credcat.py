"""Credential phases for a stranger's two-minute install.

Keith's manifest records which files already exist on his machine.
A SATISFIED row is not a file this installer ships. The peer mints the
bearer and the install key, pastes one day-one model key, and is not
asked for anything else during the 120-second clock.
"""

from __future__ import annotations

from dataclasses import dataclass

from cosmos_federation import Refuse, bound_text, secret_shape

SCHEMA = "cosmos-federation-credcat/1"

DAY_ONE = "DAY_ONE"
LATER = "LATER"
REFUSED = "REFUSED"

_PHASES = frozenset({DAY_ONE, LATER, REFUSED})
_NAME_LIMIT = 64
_FILE_LIMIT = 80
_WHY_LIMIT = 240


def _reject_secret(text: str, name: str) -> None:
    # `sk-` is the public prefix of several vendor keys. A row that carries
    # it would put key material in repr, so the row is refused.
    if secret_shape(text) or "sk-" in text.lower():
        raise Refuse("SECRET", name)


def _one_sentence(why: str) -> str:
    text = bound_text(why, limit=_WHY_LIMIT, name="why")
    _reject_secret(text, "why")
    if text.count(".") != 1 or not text.endswith("."):
        raise Refuse("WHY", "one sentence")
    return text


def _basename(filename: str | None, phase: str) -> str | None:
    # Day-one rows are files the installer mints or the peer pastes.
    # Tailscale is a login, and the cloner store is not a config file,
    # so only LATER and REFUSED may omit a filename.
    if filename is None:
        if phase == DAY_ONE:
            raise Refuse("FILE", "day-one credential needs a filename")
        return None
    text = bound_text(filename, limit=_FILE_LIMIT, name="filename")
    if (
        "/" in text
        or "\\" in text
        or (len(text) >= 2 and text[1] == ":")
        or text.startswith(".")
    ):
        raise Refuse("PATH", "filename is a basename")
    _reject_secret(text, "filename")
    return text


@dataclass(frozen=True, slots=True)
class Cred:
    """One ask. The filename is a config basename or None. Never key bytes."""

    name: str
    phase: str
    filename: str | None
    why: str

    def __post_init__(self) -> None:
        name = bound_text(self.name, limit=_NAME_LIMIT, name="name")
        phase = bound_text(self.phase, limit=16, name="phase")
        if phase not in _PHASES:
            raise Refuse("PHASE", "unknown phase")
        filename = _basename(self.filename, phase)
        why = _one_sentence(self.why)
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "phase", phase)
        object.__setattr__(self, "filename", filename)
        object.__setattr__(self, "why", why)


def _unique(rows: tuple[Cred, ...]) -> None:
    names: set[str] = set()
    files: set[str] = set()
    for row in rows:
        if row.name in names:
            raise Refuse("DUP", "name")
        names.add(row.name)
        if row.filename is None:
            continue
        if row.filename in files:
            raise Refuse("DUP", "filename")
        files.add(row.filename)


def catalog() -> tuple[Cred, ...]:
    """Return the fixed phases a peer is asked about. No secret values."""
    rows = (
        Cred(
            name="bearer",
            phase=DAY_ONE,
            filename="api_token.txt",
            why="The installer mints this loopback bearer on the peer so Core can authenticate local calls.",
        ),
        Cred(
            name="install_key",
            phase=DAY_ONE,
            filename="install_key.bin",
            why="The installer mints this 32-byte ledger key on the peer so spend-gated writes do not copy another install.",
        ),
        Cred(
            name="openrouter",
            phase=DAY_ONE,
            filename="openrouter_api_key.txt",
            why="The peer pastes one OpenRouter key here so day-one chat has a model door under the spend cap.",
        ),
        Cred(
            name="xai",
            phase=DAY_ONE,
            filename="xai_api_key.txt",
            why="The peer may paste an xAI key here instead, because xAI is the other day-one door.",
        ),
        Cred(
            name="r2",
            phase=LATER,
            filename="r2_credentials.json",
            why="Cloudflare backup is outside the two-minute chat, so this credential waits for a later step.",
        ),
        Cred(
            name="tailscale",
            phase=LATER,
            filename=None,
            why="Remote reach is an interactive Tailscale login, not a file, and loopback chat does not need it.",
        ),
        Cred(
            name="cursor",
            phase=LATER,
            filename="cursor_cosmos_key.txt",
            why="The Cursor agent lane is a later dispatch door, so the peer does not paste that key during install.",
        ),
        Cred(
            name="codex",
            phase=LATER,
            filename="openai_api_key.txt",
            why="The Codex CLI rail is outside day-one chat, so its OpenAI key waits until that lane is offered.",
        ),
        Cred(
            name="firecrawl",
            phase=LATER,
            filename="firecrawl_api_key.txt",
            why="Web fetch already runs without a key, so a Firecrawl key is not part of the first chat.",
        ),
        Cred(
            name="kill_token",
            phase=LATER,
            filename="kill_token.txt",
            why="The off-switch can stay behind the bearer until the peer chooses a separate kill token later.",
        ),
        Cred(
            name="anthropic",
            phase=REFUSED,
            filename="anthropic_api_key.txt",
            why="Anthropic is off the day-one route, so the installer never asks for that key and never creates the file.",
        ),
        Cred(
            name="r2cloner",
            phase=REFUSED,
            filename=None,
            why="Any path under D:\\R2Cloner is refused because that plaintext store is not a peer credential and is not read.",
        ),
    )
    _unique(rows)
    return rows


__all__ = [
    "DAY_ONE",
    "LATER",
    "REFUSED",
    "SCHEMA",
    "Cred",
    "catalog",
]
