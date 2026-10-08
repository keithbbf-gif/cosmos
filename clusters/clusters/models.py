"""Shared constants. Door rows mirror the harness catalog read for this build.

A door their site names and the harness does not seat stays listed with
seated false. The GUI may show it. plan_seat will not pretend it ran.
"""

from __future__ import annotations

SESSION_CAP = 50
SHORTCUT_CAP = 6

COLUMNS = ("pending", "auto", "in_progress", "in_testing", "completed")
STATUSES = ("idle", "working", "needs_input", "finished", "failed", "expired", "paused")
BUSY = ("working", "needs_input")
ROLES = ("worker", "coordinator", "global_coordinator")
VIEWS = ("grid", "tabs", "list")
MESSAGE_KINDS = (
    "user",
    "agent",
    "assignment",
    "followup",
    "correction",
    "request",
    "system",
)
ON_LIMIT = ("notify", "pause", "stop")
BUDGET_MODES = ("cap", "smart_pace")
PACK_SCOPES = ("agent", "cluster", "both")
MEMBER_KINDS = ("agent", "cluster")

HEROES = ("luna", "sol", "mini", "glm", "gf38", "deepseek", "ling", "grok")

DOOR_CATALOG: tuple[dict, ...] = (
    {
        "id": "claude",
        "binary": "claude",
        "harness_door": "claude",
        "seated": False,
        "executable": False,
        "managed_accounts": True,
        "resume": False,
        "modes": ["default"],
        "note": "Harness door exists and is unseated. dangerously-skip-permissions is refused.",
    },
    {
        "id": "codex",
        "binary": "codex",
        "harness_door": "codex",
        "seated": True,
        "executable": True,
        "managed_accounts": True,
        "resume": True,
        "modes": ["default"],
        "note": "Native Codex door. --full-auto and --danger-full-access are refused.",
    },
    {
        "id": "agy",
        "binary": "agy",
        "harness_door": "antigravity",
        "seated": False,
        "executable": False,
        "managed_accounts": False,
        "resume": False,
        "modes": [],
        "note": "Antigravity CLI. Unseated in the harness.",
    },
    {
        "id": "opencode",
        "binary": "opencode",
        "harness_door": "opencode",
        "seated": True,
        "executable": True,
        "managed_accounts": False,
        "resume": True,
        "modes": [],
        "note": "OpenCode door.",
    },
    {
        "id": "kimi",
        "binary": "kimi",
        "harness_door": "",
        "seated": False,
        "executable": False,
        "managed_accounts": False,
        "resume": False,
        "modes": [],
        "note": "Named on their site. No harness door in this build.",
    },
    {
        "id": "grok",
        "binary": "grok",
        "harness_door": "grok",
        "seated": True,
        "executable": False,
        "managed_accounts": False,
        "resume": False,
        "modes": [],
        "note": "Do not start grok.exe. The coding seat is cosmos-code.",
    },
    {
        "id": "cursor-agent",
        "binary": "cursor-agent",
        "harness_door": "",
        "seated": False,
        "executable": False,
        "managed_accounts": False,
        "resume": False,
        "modes": ["agent", "plan", "ask"],
        "note": "ACP catalog. resume stays false until a probe reports loadSession. This build does not probe.",
    },
    {
        "id": "muse",
        "binary": "muse",
        "harness_door": "",
        "seated": False,
        "executable": False,
        "managed_accounts": False,
        "resume": False,
        "modes": [],
        "note": "Named on their site in 2.4.0. No harness door in this build.",
    },
    {
        "id": "pi",
        "binary": "pi",
        "harness_door": "pi",
        "seated": True,
        "executable": True,
        "managed_accounts": False,
        "resume": False,
        "modes": ["chat", "cli"],
        "note": "pi door.",
    },
    {
        "id": "devin",
        "binary": "devin",
        "harness_door": "",
        "seated": False,
        "executable": False,
        "managed_accounts": False,
        "resume": False,
        "modes": [],
        "note": "Named on their site in 2.4.0. No harness door in this build.",
    },
    {
        "id": "cosmos-code",
        "binary": "python -m cosmos_code",
        "harness_door": "cosmos-code",
        "seated": True,
        "executable": False,
        "managed_accounts": False,
        "resume": False,
        "modes": [],
        "note": "Harness rail. Planning a seat does not start the loop.",
    },
    {
        "id": "shell",
        "binary": "bash",
        "harness_door": "",
        "seated": False,
        "executable": False,
        "managed_accounts": False,
        "resume": False,
        "modes": [],
        "note": "Plain terminal named beside the agents. This build does not start a shell.",
    },
)

DOORS = {row["id"]: row for row in DOOR_CATALOG}

MCP_CATALOG: tuple[dict, ...] = (
    {"id": "notion", "group": "team", "note": "Docs. Enable records intent. Tokens are not stored."},
    {"id": "supabase", "group": "database", "note": "Database. Enable records intent."},
    {"id": "github", "group": "team", "note": "Pull requests and issues. Enable records intent."},
    {"id": "slack", "group": "team", "note": "Team chat. Enable records intent."},
    {"id": "atlassian", "group": "team", "note": "Jira and Confluence. Enable records intent."},
    {"id": "playwright", "group": "browser", "note": "Browser automation. Enable records intent."},
    {"id": "puppeteer", "group": "browser", "note": "Browser automation. Enable records intent."},
    {"id": "gdrive", "group": "database", "note": "Google Drive. Enable records intent."},
    {"id": "postgres", "group": "database", "note": "Postgres. Enable records intent."},
    {"id": "brave", "group": "browser", "note": "Search. Enable records intent."},
)

MCP = {row["id"]: row for row in MCP_CATALOG}

ROUTINE = (
    "git status",
    "git diff",
    "git log",
    "git rev-parse",
    "pytest",
    "py -3.14 -m pytest",
    "python -m pytest",
    "ruff",
    "py_compile",
    "python -m py_compile",
    "npm test",
    "dir",
    "ls",
)


FEATURES = (
    "parallel-sessions",
    "session-cap-50",
    "grid-tabs-list",
    "project-shortcuts-6",
    "agent-shortcuts",
    "keyboard-map",
    "project-coordinator",
    "global-coordinator",
    "session-comms",
    "kanban",
    "auto-lane",
    "history-search",
    "resume-pointer",
    "live-diffs",
    "worktree-plan",
    "commit-proposal",
    "protected-branch",
    "notifications",
    "turbo-allowlist",
    "daily-budget",
    "smart-pace",
    "spend-bump-5",
    "managed-accounts",
    "mcp-catalog",
    "mobile-pair",
    "hero-packs",
    "clusters",
    "harness-plan",
    "permission-matrix",
    "git-guards",
    "review-bundle",
    "skill-paths",
    "quota-window",
    "door-mode",
    "cancel-intent",
    "follow-up",
    "title-history",
    "subtasks",
    "bookmarks",
    "spend-quota",
    "git-confirm",
    "isolation-intent",
    "seat-binding",
    "attention",
    "thread-state",
    "shortcut-preset",
    "work-style",
    "review-seen",
    "instruction-paths",
    "door-id",
    "cred-route",
    "quota-shape",
    "door-caps",
    "host-note",
    "conflict-record",
    "tool-perm",
    "headless-intent",
    "plain-shell",
    "seat-flags",
    "usage-meter",
)


def door(name: str) -> dict | None:
    return DOORS.get(name)


def public_doors() -> list[dict]:
    return [dict(row) for row in DOOR_CATALOG]


def public_mcp() -> list[dict]:
    return [dict(row) for row in MCP_CATALOG]
