"""Day-one product constants shared by every federation proposal.

These match the live kernel as read on 2026-10-01. Proposals re-express
that behavior. They do not import `cosmos` from V:\\A\\Ai\\COSMOS.

The two-minute clock starts when the installer file is already on disk.
It ends when a chat window on 127.0.0.1 is showing a live model reply,
or a typed refusal that a key is still required. The download of the
installer is outside the clock. A Rust or npm build is inside no plan:
those builds do not fit the clock, so the day-one window is a static page
served by Core, not the cDeck Tauri shell.
"""

from __future__ import annotations

import re

from cosmos_federation.errors import Refuse
from cosmos_federation.redact import secret_shape

SCHEMA = "cosmos-federation/1"

# Role table copied from cosmos/cosmos_paths.py ROLES. The directory name
# `cosmos` is the tools role inside a runtime root. It is not the git checkout.
ROLES: dict[str, str] = {
    "root": ".",
    "state": "state",
    "ledger": "ledger",
    "queue": "queue",
    "work": "work",
    "logs": "logs",
    "registry": "registry",
    "backups": "backups",
    "publish": "publish",
    "tools": "cosmos",
    "config": "config",
    "docs": "docs",
}

INSTALL_BUDGET_S = 120
SOFTWARE_BUDGET_S = 90
KEY_PASTE_BUDGET_S = 30

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8770

# Proposed routes. They do not exist on Core today. GET /dayone is the page.
# POST setup redeems a one-time loopback nonce. POST chat is the live turn.
ROUTE_PAGE = "/dayone"
ROUTE_SETUP = "/api/v1/dayone/setup"
ROUTE_CHAT = "/api/v1/dayone/chat"
NONCE_TTL_S = 60

# $0.25 default, $1.00 hard policy cap. A wizard cannot raise the cap.
DEFAULT_CAP_USD_MICROS = 250_000
MAX_CAP_USD_MICROS = 1_000_000

DOORS = frozenset({"openrouter", "xai"})

# Identity is the sentinel tree_id, never a drive letter. These ids are
# already somebody's install or a scar name, so a new machine cannot take them.
_FORBIDDEN_IDS = frozenset({
    "GMesh",
    "KMesh-COSMOS-live",
    "COSMOS",
    "live",
    "main",
})
_TREE_ID = re.compile(r"[A-Za-z][A-Za-z0-9-]{1,39}\Z")

_DENY_NAMES = frozenset({
    "api_token.txt",
    "install_key.bin",
    "secrets.json",
    ".env",
    "id_rsa",
    ".npmrc",
    "BUCm.toml",
    "BUcr.toml",
    "BUhar.toml",
    "BUorc.toml",
})
_DENY_SEGMENTS = frozenset({
    "live",
    "node_modules",
    "__pycache__",
    ".git",
    "_delme",
    "tmp",
    ".secrets",
})


def check_tree_id(tree_id: str) -> str:
    """Return the id, or refuse. The detail does not echo the rejected text."""
    if not isinstance(tree_id, str) or secret_shape(tree_id):
        raise Refuse("TREE_ID", "rejected")
    if tree_id in _FORBIDDEN_IDS or _TREE_ID.fullmatch(tree_id) is None:
        raise Refuse("TREE_ID", "rejected")
    return tree_id


def check_door(door: str) -> str:
    """Day-one doors are OpenRouter and xAI. Anthropic stays off the route."""
    if not isinstance(door, str):
        raise Refuse("DOOR", "unknown door")
    folded = door.strip().lower()
    if folded in {"anthropic", "claude"} or "claude" in folded or "anthropic" in folded:
        raise Refuse("ANTHROPIC_OFF", "anthropic is off the route")
    if folded not in DOORS:
        raise Refuse("DOOR", "unknown door")
    return folded


def check_cap(micros: int) -> int:
    """Refuse a cap outside 1 micro-dollar through the $1 policy ceiling."""
    if isinstance(micros, bool) or not isinstance(micros, int):
        raise Refuse("CAP", "outside day-one policy")
    if micros < 1 or micros > MAX_CAP_USD_MICROS:
        raise Refuse("CAP", "outside day-one policy")
    return micros


def repo_disposition(rel: str) -> str:
    """Classify one repo-relative path as SHIP, DEV, or DENY.

    SHIP may go into a peer installer. DEV may stay in the git checkout and
    must not go into the installer. DENY must not be committed or shipped:
    secrets, the live runtime, and build junk. Unknown paths are DEV so a
    new file is not shipped by accident.
    """
    if not isinstance(rel, str) or rel == "" or "\x00" in rel:
        return "DENY"
    if len(rel) >= 2 and rel[1] == ":":
        return "DENY"
    if rel.startswith("\\\\") or rel.startswith("//") or rel.startswith("/"):
        return "DENY"
    norm = rel.replace("\\", "/")
    if "://" in norm or norm.lower().startswith("file:"):
        return "DENY"
    parts = [part for part in norm.split("/") if part not in ("", ".")]
    if not parts or any(part == ".." for part in parts):
        return "DENY"
    name = parts[-1]
    lower = name.lower()
    if name in _DENY_NAMES or lower in _DENY_NAMES:
        return "DENY"
    if any(part in _DENY_SEGMENTS for part in parts):
        return "DENY"
    if "src-tauri" in parts and "target" in parts:
        return "DENY"
    if lower.endswith((
        ".pem", ".pyc", ".pyo", ".log", ".bak", ".apk",
        "_key.txt", "_token.txt",
    )):
        return "DENY"
    if "api_key" in lower or "apikey" in lower or lower.startswith("credentials"):
        return "DENY"
    if lower.endswith("_ledger.jsonl") or lower.endswith(".env"):
        return "DENY"
    joined = "/".join(parts)
    if joined in {"README.md", "Claude.md", ".gitignore", "serve.bat"}:
        return "SHIP"
    if parts[0] in {"cosmos", "docs", "kdash"}:
        return "SHIP"
    return "DEV"


__all__ = [
    "DEFAULT_CAP_USD_MICROS",
    "DEFAULT_HOST",
    "DEFAULT_PORT",
    "DOORS",
    "INSTALL_BUDGET_S",
    "KEY_PASTE_BUDGET_S",
    "MAX_CAP_USD_MICROS",
    "NONCE_TTL_S",
    "ROLES",
    "ROUTE_CHAT",
    "ROUTE_PAGE",
    "ROUTE_SETUP",
    "SCHEMA",
    "SOFTWARE_BUDGET_S",
    "check_cap",
    "check_door",
    "check_tree_id",
    "repo_disposition",
]
