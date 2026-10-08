"""Named refusals. A bad path or a forbidden command is a reason, never a success."""

from __future__ import annotations

from pathlib import Path

PROTECTED_BRANCHES = ("main", "master", "origin/main", "origin/master")

SECRET_KEYS = {
    "token",
    "secret",
    "password",
    "api_key",
    "authorization",
    "credential",
    "access_token",
    "refresh_token",
}

HARD_FLAGS = (
    "--dangerously-skip-permissions",
    "--danger-full-access",
    "--full-auto",
    "--ignore-user-config",
)


class Refuse(Exception):
    def __init__(self, code: str, detail: str = "") -> None:
        self.code = code
        self.detail = detail
        super().__init__(code if not detail else f"{code}: {detail}")

    def to_public(self) -> dict[str, str]:
        return {"error": self.code, "detail": self.detail}


def guard_path(text: str) -> str:
    """Reject a path that leaves the caller's tree or names the live root."""
    if not isinstance(text, str) or not text.strip():
        raise Refuse("PATH", "empty")
    if "\x00" in text or text.startswith("\\\\") or text.lower().startswith("file:"):
        raise Refuse("PATH", "rejected")
    parts = Path(text).parts
    if ".." in parts:
        raise Refuse("PATH", "rejected")
    folded = text.replace("\\", "/").rstrip("/").lower()
    if folded.endswith(("/live", ":live")) or "/cosmos/live" in folded:
        raise Refuse("LIVE_TREE", text)
    return text


def scrub(body: dict) -> dict:
    """Refuse secret bytes. A profile path is allowed. A token value is not."""
    for key, value in body.items():
        if str(key).lower() in SECRET_KEYS and value not in ("", None, False):
            raise Refuse("SECRET", str(key))
        if isinstance(value, dict):
            scrub(value)
    return body


def is_destructive(command: str) -> bool:
    text = " ".join(command.lower().split())
    needles = (
        "rm -rf",
        "rm -fr",
        "remove-item -recurse",
        "remove-item -force -recurse",
        "git clean",
        "git reset --hard",
        "drop database",
        "drop table",
        "format c:",
        "format d:",
        "del /s",
        "rmdir /s",
    )
    return any(item in text for item in needles)


def is_protected_push(command: str, branch: str = "") -> bool:
    text = " ".join(command.lower().split())
    named = branch.strip().lower()
    if named in PROTECTED_BRANCHES and "push" in text:
        return True
    if "git push" not in text and not text.startswith("git push"):
        return False
    for item in PROTECTED_BRANCHES:
        if item in text.split():
            return True
    return False


def forbidden_flag(command: str) -> str:
    text = command.lower()
    for flag in HARD_FLAGS:
        if flag in text:
            return flag
    if "grok.exe" in text:
        return "grok.exe"
    return ""
