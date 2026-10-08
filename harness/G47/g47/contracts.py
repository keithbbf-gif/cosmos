"""Frozen call contracts. The grader and the argv builder share these types."""

from __future__ import annotations

from dataclasses import dataclass

FIRST_LINE = {
    "CODER": ("NONE", "diff --git"),
    "WOMBAT": ("ITEM", "NONE"),
    "JUDGE": ("KEEP", "DROP", "NONE", "HOLD", "UNMEASURED"),
}

KIND = {
    "ORC": "orch",
    "WOMBAT": "board",
    "JUDGE": "review",
    "CODER": "coding",
    "CCR": "dispose",
    "DAEMON": "daemon",
}

CODING_DOORS = frozenset({
    "cosmos-code", "pi", "opencode", "dsh", "codex", "copilot", "claude",
    "antigravity",
})


@dataclass(frozen=True)
class OutputContract:
    """What a legal reply looks like. Ping is a shape, not a vibe."""

    role: str
    what: str  # text | python | no_prose
    ping: bool = False

    def __post_init__(self) -> None:
        if self.what not in ("text", "python", "no_prose"):
            raise ValueError(self.what)
        if self.role not in KIND:
            raise ValueError(self.role)


@dataclass(frozen=True)
class Legend:
    """Seven layers plus the mission tail. Context is a list of paths, never a joined string."""

    role: str
    model: str
    what: str = "text"
    ping: bool = False
    wrap: str = ""
    style: str = ""
    task: str = ""
    context: tuple[str, ...] = ()
    where: str = ""
    optimum: str | int = "float"
    window: int | None = None
    cached_tokens: int = 0
    skills: tuple[str, ...] = ()
    # OpenRouter class-6 only. Prefill forces a NONE prefix and drops wrapper credit.
    prefill_none: bool = False

    def kind(self) -> str:
        if self.role not in KIND:
            raise ValueError(self.role)
        return KIND[self.role]
