#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_dispatch_critique - stage-5 critic visibility (inline disposed bodies).

Split out of `cosmos_dispatch.py` (PHASE 4, `docs/CORE_RESTRUCTURE.md`) along a
seam that already existed:

    # ---------------------------------------------------------------------------
    # stage-5 critic visibility: inline disposed bodies, not paths the rail
    # cannot open (measured 2026-08-27T15:10: OA gpt-5.6-terra refused honestly
    # when the prompt named builds/cvm-dt/*.py and carried no file text).
    # ---------------------------------------------------------------------------

This is the dispatch harness's *pure* critic-inline layer. Assignment +
tree / `_propose` in, a prompt that carries CODE (not paths) out -- no
runtime root identity, no DHx stamp, no collector index, no queue drop.
`cosmos_dispatch` re-exports every name below, so every existing importer
of these names off cosmos_dispatch keeps working unchanged.

What lives here, and why it is one piece:
  * `_is_critique_task` -- stage-5 / critique / vendor-plural hint
  * `_path_tokens` / `_locate_artifact` / `_inline_file` / `_format_inlined`
    -- find the disposed bytes and embed them with a full-file sha256
  * `compose_critique_prompt` -- the public builder callers already used

What deliberately did NOT move: `dispatch()` / `job_status` / `run_gate`.
Those own the queue drop, the collector index, and the stage-6 live-tree
gate. `write_inbox_sidecar` stays with DHx/stamps (the next named helper
banner), not this seam.

`CRITIQUE_INLINE_CAP` is duplicated here with the same value dispatch
already published. Dispatch re-exports the FUNCTIONS as the same objects
(not copies). Importing the constant the other way would cycle (dispatch
imports this module).

Does not modify kernel / ledger / sched / service. No hard-coded drive
literals. Truncation is marked; sha256 is of the FULL file on disk.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

# Value MUST match cosmos_dispatch.py. Dispatch re-exports the FUNCTIONS
# (same objects). This name is the inliner's closed-over vocabulary, not
# a second identity table.
CRITIQUE_INLINE_CAP = 120_000


# ---------------------------------------------------------------------------
# stage-5 critic visibility: inline disposed bodies, not paths the rail
# cannot open (measured 2026-08-27T15:10: OA gpt-5.6-terra refused honestly
# when the prompt named builds/cvm-dt/*.py and carried no file text).
# ---------------------------------------------------------------------------

_CRITIQUE_HINT_RE = re.compile(
    r"\b(stage[\s-]*5|critique|different-family|vendor-plural)\b", re.I)
_SRC_TOKEN_RE = re.compile(r"[A-Za-z0-9_./\\:-]+\.[A-Za-z0-9]+")
_SRC_SUFFIX = (".py", ".md", ".toml", ".json", ".js", ".ts", ".tsx", ".kt")
_BEGIN_FILE_MARK = "===== BEGIN FILE "
_INLINE_HEADER = (
    "## INLINED ARTIFACTS (disposed bytes; sha256 of the full file on disk)\n"
    "You have the CODE. A path you cannot open is not evidence.\n"
)


def _load_json(path: Path) -> dict | None:
    if path is None or not path.exists():
        return None
    try:
        d = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except (OSError, ValueError):
        return None
    return d if isinstance(d, dict) else None


def _is_critique_task(task: str) -> bool:
    return bool(_CRITIQUE_HINT_RE.search(str(task or "")))


def _posix_rel(path: str) -> str:
    return str(path or "").replace("\\", "/").lstrip("./")


def _under_root(root, rel) -> Path | None:
    if root in (None, ""):
        return None
    try:
        base = Path(root).resolve()
        raw = Path(str(rel).replace("\\", "/"))
        p = raw.resolve() if raw.is_absolute() else (base / raw).resolve()
        p.relative_to(base)
        return p
    except (OSError, ValueError):
        return None


def _path_tokens(text: str) -> list[str]:
    out: list[str] = []
    for raw in _SRC_TOKEN_RE.findall(str(text or "")):
        if "://" in raw:
            continue
        s = raw.replace("\\", "/").strip(".,;:()[]{}<>\"'")
        if s.lower().endswith(_SRC_SUFFIX) and s not in out:
            out.append(s)
    return out


def _seen_path(seen: set[str], rel: str) -> bool:
    if rel in seen:
        return True
    return any(s.endswith("/" + rel) for s in seen)


def _file_row(item) -> tuple[str, str | None] | None:
    if isinstance(item, str):
        rel, sha = item, None
    elif isinstance(item, dict):
        rel = item.get("target_path") or item.get("path") or item.get("file")
        sha = item.get("sha256")
    else:
        return None
    rel = _posix_rel(rel or "")
    return (rel, sha) if rel else None


def _locate_artifact(rel: str, *, tree, propose_dir, parents: list[str]) -> Path | None:
    rel_n = _posix_rel(rel)
    name = Path(rel_n).name
    rels = [rel_n] + ([name] if name != rel_n else [])
    rels.extend(f"{parent}/{name}" for parent in parents)
    for root in (propose_dir, tree):
        for r in rels:
            p = _under_root(root, r)
            if p is not None and p.is_file():
                return p
    return None


def _inline_file(path: Path, rel: str, bind_sha=None) -> dict:
    rec = {
        "path": _posix_rel(rel), "abs": str(path), "missing": False,
        "truncated": False, "sha256": None, "bytes": 0,
        "bind_sha256": bind_sha, "text": "",
    }
    try:
        raw = path.read_bytes()
    except OSError as e:
        rec.update(missing=True, error=f"{type(e).__name__}: {e}",
                   text=f"(unreadable: {type(e).__name__}: {e})\n")
        return rec
    rec["bytes"] = len(raw)
    rec["sha256"] = hashlib.sha256(raw).hexdigest()
    rec["sha256_match_bind"] = (
        None if not bind_sha else rec["sha256"] == str(bind_sha).lower())
    rec["truncated"] = len(raw) > CRITIQUE_INLINE_CAP
    chunk = raw[:CRITIQUE_INLINE_CAP] if rec["truncated"] else raw
    rec["text"] = chunk.decode("utf-8", errors="replace")
    if rec["truncated"]:
        rec["text"] += (
            f"\n...[TRUNCATED: inlined first {CRITIQUE_INLINE_CAP} of "
            f"{rec['bytes']} bytes; sha256 is of the FULL file on disk]...\n")
    return rec


def _format_inlined(rec: dict) -> str:
    rel = rec["path"]
    body = rec.get("text") or ""
    if rec.get("missing"):
        head = f"{_BEGIN_FILE_MARK}path={rel} missing=true ====="
    else:
        head = (
            f"{_BEGIN_FILE_MARK}path={rel} sha256={rec['sha256']} "
            f"bytes={rec['bytes']} truncated={str(rec['truncated']).lower()} =====")
    if not body.endswith("\n"):
        body += "\n"
    return f"{head}\n{body}===== END FILE path={rel} ====="


def compose_critique_prompt(assignment: str, *, bind=None, files=None,
                            tree=None, propose_dir=None) -> dict:
    """Build a critic prompt that carries CODE, not paths.

    Reads each file named in `_propose/BIND.json` (schema cosmos-p10-bind/1)
    or in `files` / disposed target paths extracted from the assignment.
    Embeds the on-disk body with a per-file sha256 of the FULL bytes so a
    non-local rail (OA/GEM) can quote the same bytes that were disposed.
    """
    assignment_s = str(assignment or "")
    if _BEGIN_FILE_MARK in assignment_s and "sha256=" in assignment_s:
        return {"prompt": assignment_s, "inlined": True, "already": True,
                "files": []}

    bind_obj = bind if isinstance(bind, dict) else None
    if bind_obj is None:
        cands = []
        if bind not in (None, ""):
            cands.append(Path(bind))
        if propose_dir not in (None, ""):
            cands.append(Path(propose_dir) / "BIND.json")
        if tree not in (None, ""):
            cands += [Path(tree) / "_propose" / "BIND.json",
                      Path(tree) / "BIND.json"]
        for p in cands:
            loaded = _load_json(p)
            if loaded:
                bind_obj = loaded
                bind_obj["_bind_path"] = str(p)
                break

    rows: list[dict] = []
    seen: set[str] = set()
    items = list((bind_obj or {}).get("files") or []) if isinstance(
        (bind_obj or {}).get("files"), list) else []
    items.extend(files or [])
    items.extend(_path_tokens(assignment_s))
    for item in items:
        parsed = _file_row(item)
        if parsed is None or _seen_path(seen, parsed[0]):
            continue
        seen.add(parsed[0])
        rows.append({"target_path": parsed[0], "bind_sha256": parsed[1]})

    parents = []
    for r in rows:
        parent = str(Path(r["target_path"]).parent).replace("\\", "/")
        if parent not in (".", "") and parent not in parents:
            parents.append(parent)

    artifacts: list[dict] = []
    for r in rows:
        loc = _locate_artifact(r["target_path"], tree=tree,
                               propose_dir=propose_dir, parents=parents)
        if loc is None:
            artifacts.append({
                "path": r["target_path"], "abs": None, "missing": True,
                "truncated": False, "sha256": None, "bytes": 0,
                "bind_sha256": r.get("bind_sha256"),
                "text": "(file not found; cannot inline)\n",
            })
        else:
            artifacts.append(_inline_file(loc, r["target_path"],
                                          r.get("bind_sha256")))

    present = [a for a in artifacts if a.get("sha256")]
    bind_path = (bind_obj or {}).get("_bind_path")
    if not present:
        return {"prompt": assignment_s, "inlined": False, "already": False,
                "files": artifacts, "bind": bind_path}
    prompt = (assignment_s.rstrip() + "\n\n" + _INLINE_HEADER
              + "\n".join(_format_inlined(a) for a in artifacts) + "\n")
    keys = ("path", "abs", "sha256", "bytes", "truncated", "missing",
            "bind_sha256", "sha256_match_bind")
    return {"prompt": prompt, "inlined": True, "already": False,
            "files": [{k: a.get(k) for k in keys} for a in artifacts],
            "bind": bind_path}
