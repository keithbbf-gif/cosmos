"""Hooks as law — PreToolUse deny/rewrite before exec.

Mandatory matchers: shell delete/format/force-push; any delete tool
rewritten to archive (stage_to_delme). Advice lives in COSMOS.md; law here.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Callable, Optional


@dataclass
class HookDecision:
    deny: bool = False
    reason: str = ""
    rewrite_tool: Optional[str] = None
    rewrite_args: dict[str, Any] = field(default_factory=dict)


PreHook = Callable[[str, dict[str, Any]], Optional[HookDecision]]


class HookBus:
    def __init__(self) -> None:
        self._pre: list[PreHook] = []

    def add_pre(self, hook: PreHook) -> None:
        self._pre.append(hook)

    def pre(self, tool: str, args: dict[str, Any]) -> HookDecision:
        for hook in self._pre:
            d = hook(tool, args)
            if d is not None and (d.deny or d.rewrite_tool):
                return d
        return HookDecision()


_RM_RE = re.compile(
    r"\b(rm|unlink|del|erase|Remove-Item|rd|rmdir)\b",
    re.IGNORECASE,
)
_FORMAT_RE = re.compile(r"\bformat\b", re.IGNORECASE)
_FORCE_PUSH_RE = re.compile(r"git\s+push\b.*(--force|-f)\b", re.IGNORECASE)
_OS_UNLINK_RE = re.compile(r"os\.unlink|pathlib\.Path\(.*\)\.unlink|shutil\.rmtree", re.IGNORECASE)


def _extract_rm_target(command: str) -> Optional[str]:
    # naive: last non-flag token
    parts = command.split()
    flags = {"-r", "-rf", "-fr", "-f", "-R", "/s", "/q", "/f", "-Recurse", "-Force"}
    targets = [p for p in parts[1:] if p not in flags and not p.startswith("-")]
    return targets[-1] if targets else None


def pre_shell_delete_rewrite(tool: str, args: dict[str, Any]) -> Optional[HookDecision]:
    if tool not in ("shell", "bash", "Bash", "Shell"):
        return None
    cmd = str(args.get("command") or args.get("cmd") or "")
    if _FORMAT_RE.search(cmd):
        return HookDecision(deny=True, reason="format_forbidden")
    if _FORCE_PUSH_RE.search(cmd):
        return HookDecision(deny=True, reason="force_push_forbidden")
    if _RM_RE.search(cmd) or _OS_UNLINK_RE.search(cmd):
        target = _extract_rm_target(cmd) or args.get("path")
        return HookDecision(
            deny=True,
            reason="delete_rewritten_to_archive",
            rewrite_tool="stage_to_delme",
            rewrite_args={"path": target, "command": cmd},
        )
    return None


def pre_delete_tool_rewrite(tool: str, args: dict[str, Any]) -> Optional[HookDecision]:
    delete_tools = {
        "delete",
        "Delete",
        "delete_file",
        "DeleteFile",
        "remove",
        "Remove",
        "edit_delete",
        "EditDelete",
    }
    if tool not in delete_tools:
        # also catch apply_patch delete intent via args
        if tool in ("edit", "apply_patch", "Edit") and args.get("delete"):
            pass
        else:
            return None
    path = args.get("path") or args.get("file_path") or args.get("file")
    return HookDecision(
        deny=True,
        reason="delete_tool_rewritten_to_archive",
        rewrite_tool="stage_to_delme",
        rewrite_args={"path": path},
    )


def install_defaults(bus: Optional[HookBus] = None) -> HookBus:
    bus = bus or HookBus()
    bus.add_pre(pre_shell_delete_rewrite)
    bus.add_pre(pre_delete_tool_rewrite)
    return bus
