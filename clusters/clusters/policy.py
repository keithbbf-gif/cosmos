"""Turbo allowlist and hard refusals.

FLAG, DESTRUCTIVE, PROTECTED, LIVE_TREE, DENY, and LIMIT always refuse.
An empty claim is RECORDED and is not evidence a command ran.
"""

from __future__ import annotations

from clusters.models import ROUTINE
from clusters.refuse import Refuse, forbidden_flag, is_destructive, is_protected_push
from clusters.store import Store


def check_command(
    store: Store,
    *,
    command: str,
    turbo: bool = False,
    branch: str = "",
) -> dict[str, str]:
    """Turbo allowlist and hard refusals: returns FLAG, DESTRUCTIVE, PROTECTED, LIVE_TREE, DENY, APPROVAL, or OK; records no claim."""
    text = " ".join(command.split())
    flag = forbidden_flag(text)
    if flag:
        return _decision("refuse", "FLAG", flag)
    if is_destructive(text):
        return _decision("refuse", "DESTRUCTIVE", "destructive")
    if is_protected_push(text, branch):
        return _decision("refuse", "PROTECTED", "protected branch")
    live = _live_hit(text)
    if live:
        return _decision("refuse", "LIVE_TREE", live)
    extra_allow, extra_deny = _limits(store)
    denied = _denied(text, extra_deny)
    if denied:
        return _decision("refuse", "DENY", denied)
    if _listed(text, [*ROUTINE, *extra_allow]):
        return _decision("allow", "OK", "")
    # Turbo allowlist and hard refusals: turbo does not widen this; code is APPROVAL. Records no claim.
    del turbo
    return _decision("needs_approval", "APPROVAL", "not on the routine allowlist")


def set_limits(
    store: Store,
    *,
    allow: list[str] | None = None,
    deny: list[str] | None = None,
) -> dict[str, list[str]]:
    """Turbo allowlist and hard refusals: raises LIMIT; empty claim is RECORDED, not evidence."""
    clean_allow = _phrases(allow)
    clean_deny = _phrases(deny)
    store.append(
        "policy",
        {"id": "policy", "op": "set", "allow": clean_allow, "deny": clean_deny},
    )
    return {"allow": list(clean_allow), "deny": list(clean_deny)}


# Turbo allowlist and hard refusals: returns the given code. Records no claim.
def _decision(decision: str, code: str, detail: str) -> dict[str, str]:
    return {"decision": decision, "code": code, "detail": detail}


# Turbo allowlist and hard refusals: raises LIMIT. Records no claim.
def _phrases(values: list[str] | None) -> list[str]:
    if values is None:
        return []
    if not isinstance(values, list):
        raise Refuse("LIMIT", "list of strings")
    cleaned: list[str] = []
    for item in values:
        if not isinstance(item, str) or "\n" in item or "\r" in item:
            raise Refuse("LIMIT", "single-line string")
        cleaned.append(item)
    return cleaned


def _limits(store: Store) -> tuple[list[str], list[str]]:
    row = store.latest_kind("policy")
    if not row:
        return [], []
    body = row.get("body")
    if not isinstance(body, dict):
        return [], []
    return _kept(body.get("allow")), _kept(body.get("deny"))


def _kept(values: object) -> list[str]:
    if not isinstance(values, list):
        return []
    return [item for item in values if isinstance(item, str)]


# Turbo allowlist and hard refusals: a hit is the detail for DENY. Records no claim.
def _denied(command: str, phrases: list[str]) -> str:
    lowered = command.lower()
    for phrase in phrases:
        needle = " ".join(phrase.split()).lower()
        if needle and needle in lowered:
            return phrase
    return ""


# Turbo allowlist and hard refusals: a hit is allow (OK); a miss is not a refusal. Records no claim.
def _listed(command: str, phrases: list[str]) -> bool:
    for phrase in phrases:
        text = " ".join(phrase.split())
        if text and (command == text or command.startswith(text + " ")):
            return True
    return False


# Turbo allowlist and hard refusals: a hit is the detail for LIVE_TREE. Records no claim.
def _live_hit(command: str) -> str:
    lowered = command.lower()
    if "cosmos/live" in lowered:
        return "cosmos/live"
    if "cosmos\\live" in lowered:
        return "cosmos\\live"
    for token in command.split():
        if "/" not in token and "\\" not in token:
            continue
        folded = token.replace("\\", "/").rstrip("/")
        if folded.lower().endswith("/live"):
            return token
    return ""
