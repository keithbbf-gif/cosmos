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
    segments = [part for part in folded.split("/") if part not in ("", ".")]
    if folded.endswith(":live") or any(
        part == "live" or part.endswith(":live") for part in segments
    ):
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


def _push_args(tokens: list[str]) -> list[str] | None:
    """Arguments of a git push subcommand, or None when this is not one."""
    if "git" not in tokens:
        return None
    index = tokens.index("git") + 1
    while index < len(tokens):
        token = tokens[index]
        if token == "push":
            return tokens[index + 1 :]
        if token in {"-c", "-C"} and index + 1 < len(tokens):
            index += 2
            continue
        if token.startswith("-"):
            index += 1
            continue
        return None
    return None


def is_protected_push(command: str, branch: str = "") -> bool:
    text = " ".join(command.lower().split())
    named = branch.strip().lower()
    tokens = text.split()
    if named in PROTECTED_BRANCHES and "push" in tokens:
        return True
    args = _push_args(tokens)
    if args is None:
        return False
    for token in args:
        if token.startswith("-"):
            continue
        dest = token.rsplit(":", 1)[-1].removeprefix("+")
        if dest in PROTECTED_BRANCHES:
            return True
        bare = dest.rsplit("/", 1)[-1]
        if bare in {"main", "master"} and (dest == bare or "/heads/" in dest):
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
