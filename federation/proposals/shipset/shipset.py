"""Day-one ship set. Kind comes from the shared classifier; this module adds why.

A peer installer may carry SHIP. DEV may stay in git and must stay out of the
installer. DENY must not be committed or shipped. The shared function is the
decision. The sentences here tell a reviewer which of its rules fired, and
`measured_gaps` names the gitignore rules it still does not implement.
"""

from __future__ import annotations

import fnmatch
from dataclasses import dataclass

from cosmos_federation import redact, repo_disposition

SCHEMA = "cosmos-federation-shipset/1"

SHIP = "SHIP"
DEV = "DEV"
DENY = "DENY"

# Same names and segments repo_disposition denies. Duplicated so a why line
# can name the rule. This module does not change the shared decision.
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
_SHIP_FILES = frozenset({"README.md", "Claude.md", ".gitignore", "serve.bat"})
_SHIP_ROOTS = frozenset({"cosmos", "docs", "kdash"})
_STATE_JSON = frozenset({
    "mesh_state.json",
    "dash.json",
    "bench.json",
    "chan.json",
    "drive_health.json",
    "budget_knobs.json",
})
_KINDS = frozenset({SHIP, DEV, DENY})

# Snapshot from the live checkout .gitignore and public main on 2026-10-01.
# live/ is already DENY, so a public live tree is a repo leak, not a missing
# rule. MAP.md records that leak. Strings stay free of key material.
_GAPS: tuple[str, ...] = (
    "*_env.json, including gemini_cli_env.json, is DEV at the root and SHIP under cosmos/, docs/, or kdash/ (witnesses gemini_cli_env.json and docs/gemini_cli_env.json). It is not on public main.",
    "Live-state JSON names (*_heartbeat*.json, *_state.json, mesh_state.json, dash.json, bench.json, chan.json, drive_health.json, spend*.json, *_spend*.json, budget_knobs.json) are DEV at the root and SHIP under a ship root (witnesses dash.json and kdash/dash.json). Those basenames are not on public main.",
    "*_state/ directories are DEV (witness mesh_state/a.json).",
    "_queue/ and _lanes/ are DEV, and the same segments under a ship root are SHIP (witnesses _queue/a and cosmos/_queue/a).",
    "logs/ and out/ are DEV for names that do not already end in .log, and a non-log file under a ship root is SHIP (witnesses logs/a.txt and cosmos/logs/a.txt).",
    "docs/COLLECTOR.md is SHIP because docs/ is a ship root. The file is absent on public main.",
    ".venv/, venv/, and *.egg-info/ are DEV, and those segments under a ship root are SHIP (witnesses .venv/pyvenv.cfg and kdash/.venv/pyvenv.cfg).",
    "*.bak-*, delme__*, and *.PRE_* are DEV, and the same names under a ship root are SHIP (witnesses a.bak-1 and kdash/foo.bak-1). A final .bak suffix is already DENY.",
    "/trylive/ is DEV, and trylive under a ship root is SHIP (witnesses trylive/a and docs/trylive/a). Only the live segment is DENY.",
    "work_orders/ccr/*_last.txt is DEV. 116 such blobs are on public main (witness work_orders/ccr/CAT_BONSAI_last.txt).",
    "work_orders/ccr/hero_pings/*_last.txt is DEV. 18 such blobs are on public main. The gitignore star does not cross a slash, so the published rule misses them (witness work_orders/ccr/hero_pings/07_hy3preview_last.txt).",
    "work_orders/ccr/hero_coders/*/grade.json, wire.json, and harness_log.jsonl, plus work_orders/ccr/BAKEOFF70.jsonl, are DEV (witness work_orders/ccr/BAKEOFF70.jsonl). Those paths are absent on public main.",
    "work_orders/ccr/CREW/IN/CODER_PRELOAD_PATENT_IDEAS_CACHE.md and work_orders/ccr/CREW/OUT/ELEGANT/ are DEV (witness work_orders/ccr/CREW/OUT/ELEGANT/note.md). Those paths are absent on public main.",
    "BU seat files are DENY only as BUCm.toml, BUcr.toml, BUhar.toml, and BUorc.toml. bucm.toml is DEV and docs/bucm.toml is SHIP (witnesses bucm.toml and docs/bucm.toml).",
    "A basename that starts with credentials is DENY, so public docs/CREDENTIALS_NEEDED.md is DENY. Gitignore only excludes credentials*.json, and docs/ is otherwise a ship root.",
    "Editor and OS names (.vscode/, .idea/, Thumbs.db, desktop.ini, ~$*) are DEV at the root and SHIP under a ship root (witnesses desktop.ini and cosmos/desktop.ini).",
)


@dataclass(frozen=True, slots=True)
class Classified:
    """One repo-relative path after the shared classifier.

    `kind` is SHIP, DEV, or DENY. `why` is for a reviewer. `rel` is the
    caller path with secret-shaped spans removed so repr stays clean.
    """

    rel: str
    kind: str
    why: str


def classify(rel: str) -> Classified:
    """Classify `rel` with repo_disposition and attach the matching why.

    Empty input is DENY, not a raised refusal, so every caller gets a kind.
    An unknown kind from the shared function becomes DENY. A path that
    itself looks like key material is stored redacted.
    """
    kind = repo_disposition(rel)
    if kind not in _KINDS:
        # An unrecognized label must not pass as something an installer can carry.
        kind = DENY
        why = "denied because the shared classifier returned an unknown kind"
    elif kind == DENY:
        why = _deny_why(rel)
    elif kind == SHIP:
        why = _ship_why(rel)
    else:
        why = _dev_why(rel)
    stored = redact(rel) if isinstance(rel, str) else ""
    return Classified(stored, kind, redact(why))


def measured_gaps() -> tuple[str, ...]:
    """Return the missing shared-classifier rules measured for this snapshot.

    The value is fixed. Calling it does not read GitHub or the checkout.
    """
    return _GAPS


def _parse(rel: object) -> tuple[tuple[str, ...], str, str] | None:
    """Return parts, lower basename, and joined path, or None if it cannot ship."""
    if not isinstance(rel, str) or rel == "" or "\x00" in rel:
        return None
    if len(rel) >= 2 and rel[1] == ":":
        return None
    if rel.startswith("\\\\") or rel.startswith("//") or rel.startswith("/"):
        return None
    norm = rel.replace("\\", "/")
    if "://" in norm or norm.lower().startswith("file:"):
        return None
    parts_list = [part for part in norm.split("/") if part not in ("", ".")]
    if not parts_list or any(part == ".." for part in parts_list):
        return None
    parts = tuple(parts_list)
    return parts, parts[-1].lower(), "/".join(parts)


def _deny_why(rel: object) -> str:
    """Name the first shared deny rule that matches. Order follows that function."""
    if not isinstance(rel, str) or rel == "" or "\x00" in rel:
        return "denied because an empty path or a NUL cannot name an installer member"
    if len(rel) >= 2 and rel[1] == ":":
        # A drive letter would bake one machine into a peer package.
        return "denied because a drive letter is a machine path, not a repo-relative name"
    if rel.startswith("\\\\") or rel.startswith("//") or rel.startswith("/"):
        return "denied because a UNC or absolute path sits outside the repo"
    norm = rel.replace("\\", "/")
    if "://" in norm or norm.lower().startswith("file:"):
        return "denied because a URL is not a repo path"
    parts_list = [part for part in norm.split("/") if part not in ("", ".")]
    if not parts_list or any(part == ".." for part in parts_list):
        return "denied because the path is empty or walks to a parent directory"
    name = parts_list[-1]
    lower = name.lower()
    if name in _DENY_NAMES or lower in _DENY_NAMES:
        # Tokens, install keys, env files, and BU seat files belong to one running tree.
        return f"denied because {name} is a key, token, secret, or BU seat name and must not ship"
    for part in parts_list:
        if part in _DENY_SEGMENTS:
            # live/ carries somebody else's runtime. The other segments are junk or VCS.
            return f"denied because the {part} segment is live state, VCS metadata, or build junk"
    if "src-tauri" in parts_list and "target" in parts_list:
        # Day one does not compile Rust, so a Tauri target directory stays behind.
        return "denied because src-tauri target output is a compiled Rust build, and day one does not ship that"
    if lower.endswith(".pem"):
        return "denied because a pem file is key material"
    if lower.endswith((".pyc", ".pyo")):
        return "denied because bytecode is rebuildable junk"
    if lower.endswith(".log"):
        return "denied because a log is runtime output"
    if lower.endswith(".bak"):
        return "denied because a .bak file is a backup, not source"
    if lower.endswith(".apk"):
        # The gitignore calls the apk a local draft that also blows the GitHub size cap.
        return "denied because an apk is a local mobile draft, not day-one source"
    if lower.endswith("_key.txt"):
        return "denied because a name ending in _key.txt is key material"
    if lower.endswith("_token.txt"):
        return "denied because a name ending in _token.txt is token material"
    if "api_key" in lower or "apikey" in lower:
        return "denied because the name contains api_key or apikey"
    if lower.startswith("credentials"):
        # The shared prefix is wider than gitignore's credentials*.json.
        if lower.endswith(".json"):
            return "denied because a credentials json file is secret material"
        return (
            "denied because the basename starts with credentials; "
            "gitignore only excludes credentials*.json, so a governance doc such as "
            "docs/CREDENTIALS_NEEDED.md is caught too"
        )
    if lower.endswith("_ledger.jsonl"):
        return "denied because a ledger chain stays with the running install, not the installer"
    if lower.endswith(".env"):
        return "denied because an env file is a secret channel"
    return "denied because the shared classifier rejected the path"


def _ship_why(rel: object) -> str:
    parsed = _parse(rel)
    if parsed is None:
        return "ships because the shared classifier accepted the path"
    parts, lower, joined = parsed
    if joined in _SHIP_FILES:
        return "ships because this root file is part of the day-one source set"
    if parts[0] in _SHIP_ROOTS:
        note = _gap_clause(parts, lower, joined)
        base = f"ships because {parts[0]} is a day-one source root"
        # A ship root wins over gitignore exceptions the shared function never encoded.
        if note == "":
            return base
        return base + "; " + note
    return "ships because the shared classifier accepted the path"


def _dev_why(rel: object) -> str:
    parsed = _parse(rel)
    base = "dev because the path is not a ship root and no deny rule matches, so it stays out of the installer"
    if parsed is None:
        return base
    note = _gap_clause(parsed[0], parsed[1], parsed[2])
    if note == "":
        return base
    return base + "; " + note


def _state_json(lower: str) -> bool:
    if lower in _STATE_JSON:
        return True
    if fnmatch.fnmatchcase(lower, "*_heartbeat*.json"):
        return True
    if fnmatch.fnmatchcase(lower, "*_state.json"):
        return True
    if fnmatch.fnmatchcase(lower, "spend*.json"):
        return True
    return fnmatch.fnmatchcase(lower, "*_spend*.json")


def _editor_name(parts: tuple[str, ...], lower: str) -> bool:
    if any(part in {".vscode", ".idea"} for part in parts):
        return True
    if lower in {"thumbs.db", "desktop.ini"}:
        return True
    return fnmatch.fnmatchcase(parts[-1], "~$*")


def _gap_clause(parts: tuple[str, ...], lower: str, joined: str) -> str:
    """A gitignore exclusion the shared classifier did not turn into DENY."""
    if fnmatch.fnmatchcase(lower, "*_env.json"):
        return "gitignore excludes *_env.json, including gemini_cli_env.json, and that name is not a deny rule"
    if _state_json(lower):
        return "gitignore treats this basename as live state, and that name is not a deny rule"
    if any(fnmatch.fnmatchcase(part, "*_state") for part in parts):
        return "gitignore excludes *_state directories, and that segment is not a deny rule"
    if any(part in {"_queue", "_lanes", "logs", "out"} for part in parts):
        return "gitignore excludes _queue, _lanes, logs, and out, and those segments are not deny rules"
    if joined == "docs/COLLECTOR.md":
        return "gitignore excludes docs/COLLECTOR.md as a rebuilt projection, and the docs ship root wins"
    if any(part in {".venv", "venv"} or part.endswith(".egg-info") for part in parts):
        return "gitignore excludes .venv, venv, and egg-info, and those names are not deny segments"
    if (
        fnmatch.fnmatchcase(lower, "*.bak-*")
        or fnmatch.fnmatchcase(lower, "delme__*")
        or fnmatch.fnmatchcase(lower, "*.PRE_*")
    ):
        return "gitignore excludes *.bak-*, delme__*, and *.PRE_*, and only a final .bak suffix is denied"
    if "trylive" in parts:
        return "gitignore excludes /trylive/, and only the live segment is a deny rule"
    if joined.startswith("work_orders/ccr/") and lower.endswith("_last.txt"):
        # `*` in the gitignore line does not cross a slash, so hero_pings stays publishable.
        if joined.count("/") == 2:
            return "gitignore excludes work_orders/ccr/*_last.txt bakeoff artifacts, and the shared classifier leaves them DEV"
        return "a nested *_last.txt under work_orders/ccr is a bakeoff artifact the one-star gitignore rule misses, and the shared classifier leaves it DEV"
    if "hero_coders" in parts and lower in {"grade.json", "wire.json", "harness_log.jsonl"}:
        return "gitignore excludes hero_coders grade, wire, and harness logs, and the shared classifier leaves them DEV"
    if joined == "work_orders/ccr/BAKEOFF70.jsonl":
        return "gitignore excludes work_orders/ccr/BAKEOFF70.jsonl, and the shared classifier leaves it DEV"
    if joined == "work_orders/ccr/CREW/IN/CODER_PRELOAD_PATENT_IDEAS_CACHE.md":
        return "gitignore marks the CREW patent preload local-only, and the shared classifier leaves it DEV"
    if "ELEGANT" in parts and "OUT" in parts and "CREW" in parts:
        return "gitignore marks CREW/OUT/ELEGANT local-only, and the shared classifier leaves it DEV"
    if lower in {"bucm.toml", "bucr.toml", "buhar.toml", "buorc.toml"}:
        # The shared name set matches the seat files in one case only.
        return "BU seat files are denied only in their documented case, so this spelling is not DENY"
    if _editor_name(parts, lower):
        return "gitignore excludes editor and OS junk, and those names are not deny rules"
    return ""


__all__ = [
    "DENY",
    "DEV",
    "SCHEMA",
    "SHIP",
    "Classified",
    "classify",
    "measured_gaps",
]
