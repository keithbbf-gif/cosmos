#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gitur projection — GitHub + GitLab + Cursor as one BUILD triad.

GET /api/v1/gitur folds rails matrix + Cursor probe/launch files + jukebox
rows that already name the triad, PLUS a live CLI fold: `gh` (PRs + Actions
runs) and `glab` (identity). Cursor live is GET /v1/me only — never
/v1/repositories (1/min). Does not invent PR lists: CLI fail → UNMEASURED.
"""
from __future__ import annotations

import concurrent.futures
import json
import re
import subprocess
import threading
import time
from pathlib import Path

from cosmos_ccr import read_lease
from cosmos_cursor_rail import LAUNCH_NAME, PROBE_NAME

SCHEMA = "cosmos-gitur/1"
LEGS = (
    ("cursor-api", "Cursor",
     "Lane B BUILD grok-4.6 native pool. Probe is GET /v1/me."),
    ("github-forge", "GitHub",
     "origin, PRs, Sonnet Gitur review (Anthropic-off exception). Not the live-tree writer."),
    ("gitlab-forge", "GitLab",
     "CI is the execute-the-gate. Sonnet Gitur review. Duo still proposes."),
)
# Keith 2026-09-11: Gitur default reviewer = Sonnet. Exception to
# ANTHROPIC_OFF — Gitur vendor/OR named pin only. Not COSMOS ``claude -p``.
# Not api.anthropic.com key file. Cursor Cloud Agents stay Grok 4.6.
# CCr still reviews all code before dispose.
DEFAULT_REVIEWER = "sonnet"
DEFAULT_REVIEW_VIA = "openrouter"
DEFAULT_REVIEW_MODEL = "anthropic/claude-sonnet-5"
DEFAULT_REVIEW_TRIGGER = "gitur-sonnet-exception"
JOB_NEEDLES = ("gitur", "github", "gitlab", "cursor", "glab", "copilot")
FORGE_NEEDLES = ("forge", "motif", "adversar", "cheap_coder")
IMPLEMENT_NEEDLES = ("implement", "accept_order", "--accept", "dispose", "ccr write")
SGH_NEEDLES = ("sgh", "voice", "drop_ingest", "work_orders/drop")
GITHUB_NEEDLES = ("github", "copilot", "keithbbf-gif")
GITLAB_NEEDLES = ("gitlab", "glab", "duo")
CURSOR_NEEDLES = ("cursor",)
_SNAP_CACHE = {"key": None, "at": 0.0, "payload": None, "busy": False}
_SNAP_CACHE_S = 10.0
_SNAP_LOCK = threading.Lock()
_ANSI = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")
CLI_TIMEOUT_S = 4.0
GH_REPOS = ("keithbbf-gif/cdeck", "keithbbf-gif/cosmos")
# Parked Cursor leftovers — shown, never auto-merged from this fold.
CDECK_PARKED = frozenset({6, 16, 17, 68})
COSMOS_PARKED = frozenset({30, 32, 36, 37, 38, 40})
GLAB_PROJECT = "keithbbf-gif/cosmos"


class GiturError(RuntimeError):
    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def _strip_ansi(text: str) -> str:
    return _ANSI.sub("", text or "")


def _json_from_cli(text: str):
    """gh/glab may prefix a version banner. First { or [ is the payload."""
    raw = _strip_ansi(text or "")
    for i, ch in enumerate(raw):
        if ch in "{[":
            try:
                return json.loads(raw[i:])
            except ValueError:
                return None
    return None


def _cli(argv, *, timeout=CLI_TIMEOUT_S, run=None) -> tuple[int, str, str]:
    """Injected `run(argv) -> (rc, out[, err])` for tests. Never a shell string."""
    if run is not None:
        rec = run(list(argv))
        if isinstance(rec, tuple) and len(rec) == 2:
            return int(rec[0]), rec[1] or "", ""
        if isinstance(rec, tuple) and len(rec) >= 3:
            return int(rec[0]), rec[1] or "", rec[2] or ""
        return 1, "", "BAD_RUNNER"
    try:
        p = subprocess.run(
            list(argv), capture_output=True, text=True, timeout=timeout,
        )
    except FileNotFoundError:
        return 127, "", "NO_CLI"
    except subprocess.TimeoutExpired:
        return 124, "", "TIMEOUT"
    return int(p.returncode), p.stdout or "", p.stderr or ""


def request_default_review(repo: str, number, *, run=None, kind: str = "pr",
                           launch=None, root=None) -> dict:
    """Gitur default: Sonnet reviews the PR/MR (Keith 2026-09-11 exception).

    ANTHROPIC_OFF still holds for COSMOS dispatch / ``claude -p`` /
    ``api.anthropic.com``. This path is Gitur-only, OpenRouter named pin.
    Does not spend Cursor Other Models. Does not merge. ``launch`` injects tests.
    """
    repo = str(repo or "").strip()
    try:
        n = int(number)
    except (TypeError, ValueError):
        return {"ok": False, "kind": "REFUSED", "detail": "bad number",
                "reviewer": DEFAULT_REVIEWER}
    if not repo:
        return {"ok": False, "kind": "REFUSED", "detail": "empty repo",
                "reviewer": DEFAULT_REVIEWER}
    if kind == "mr":
        url = f"https://gitlab.com/{repo}/-/merge_requests/{n}"
        gh_url = f"https://github.com/{repo}"
    else:
        url = f"https://github.com/{repo}/pull/{n}"
        gh_url = f"https://github.com/{repo}"
    prompt = (
        "REVIEW ONLY. You are the Gitur default reviewer: Sonnet "
        f"({DEFAULT_REVIEW_MODEL}). Exception to ANTHROPIC_OFF for Gitur only. "
        "Different family from CCr Grok 4.6. Do not merge. Do not write V:\\A. "
        "Not Fable. Not Opus. Not COSMOS claude -p. Not Cursor Other Models. "
        f"Target: {url}. Post findings with file and line. "
        "No invented scores. Empty review if the diff is sound."
    )
    extra = {
        "model": DEFAULT_REVIEW_MODEL,
        "review": True,
        "auto_create_pr": False,
        "repo_url": gh_url,
        "poll": False,
        "name": f"gitur-sonnet-{kind}-{n}"[:100],
    }
    if launch is not None:
        rec = launch(prompt, extra)
    else:
        from cosmos_openrouter_rail import (
            OpenRouterRail, key_path_for, load_spec, spec_path_for,
        )
        from cosmos_paths import CosmosPaths
        live = root or Path(r"V:\A\Ai\COSMOS\live")
        paths = CosmosPaths(str(live))
        spec = load_spec(spec_path_for(paths))
        rail = OpenRouterRail(key_path_for(paths, spec), spec)
        rec = rail.dispatch({
            "model": DEFAULT_REVIEW_MODEL,
            "messages": [
                {"role": "system", "content": "Gitur reviewer. Findings only."},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": 2048,
        })
    rec = rec if isinstance(rec, dict) else {"ok": False, "detail": str(rec)[:200]}
    ok = bool(rec.get("ok"))
    return {
        "ok": ok,
        "kind": rec.get("kind") or ("OK" if ok else "UNREACHABLE"),
        "reviewer": DEFAULT_REVIEWER,
        "model": DEFAULT_REVIEW_MODEL,
        "trigger": DEFAULT_REVIEW_TRIGGER,
        "repo": repo,
        "number": n,
        "via": DEFAULT_REVIEW_VIA,
        "url": url,
        "agent_id": rec.get("agent_id") or (rec.get("dispatch") or {}).get("agent_id"),
        "detail": (rec.get("detail") or rec.get("launch_error") or "")[:200],
    }


def _parked(repo: str, number) -> bool:
    try:
        n = int(number)
    except (TypeError, ValueError):
        return False
    if repo.endswith("/cdeck"):
        return n in CDECK_PARKED
    if repo.endswith("/cosmos"):
        return n in COSMOS_PARKED
    return False


def _github_prs(repo: str, *, run=None) -> list:
    prc, pout, _perr = _cli(
        ["gh", "pr", "list", "--repo", repo, "--state", "open",
         "--json", "number,title,isDraft,url,headRefName,updatedAt",
         "--limit", "12"],
        timeout=CLI_TIMEOUT_S, run=run)
    body = _json_from_cli(pout) if prc == 0 else None
    prs = []
    if isinstance(body, list):
        for row in body:
            if not isinstance(row, dict):
                continue
            num = row.get("number")
            prs.append({
                "repo": repo,
                "number": num,
                "title": row.get("title"),
                "draft": bool(row.get("isDraft")),
                "url": row.get("url"),
                "branch": row.get("headRefName"),
                "updated_at": row.get("updatedAt"),
                "parked": _parked(repo, num),
                "leg": "github",
                "st": "DRAFT" if row.get("isDraft") else "OPEN",
            })
    return prs


def _github_runs(repo: str, *, run=None) -> list:
    rrc, rout, _rerr = _cli(
        ["gh", "run", "list", "--repo", repo, "--limit", "6",
         "--json", "databaseId,name,status,conclusion,headBranch,updatedAt,url,event"],
        timeout=CLI_TIMEOUT_S, run=run)
    rbody = _json_from_cli(rout) if rrc == 0 else None
    runs = []
    if isinstance(rbody, list):
        for row in rbody:
            if not isinstance(row, dict):
                continue
            st = str(row.get("status") or "").lower()
            conc = str(row.get("conclusion") or "").lower()
            word = "RUNNING" if st in ("in_progress", "queued") else (
                "CLEAN" if conc == "success" else (
                    "BROKE" if conc in ("failure", "cancelled", "timed_out")
                    else (conc or st or "UNMEASURED").upper()))
            runs.append({
                "repo": repo,
                "id": row.get("databaseId"),
                "name": row.get("name"),
                "st": word,
                "status": row.get("status"),
                "conclusion": row.get("conclusion") or "",
                "branch": row.get("headBranch"),
                "event": row.get("event"),
                "url": row.get("url"),
                "updated_at": row.get("updatedAt"),
                "leg": "github",
                "kind": "actions",
            })
    return runs


def github_live(*, run=None) -> dict:
    """Measured `gh` CLI. Identity is rate_limit.limit. PRs/runs are lists
    gh actually returned — empty list is measured zero, not invented.
    Identity first, then per-repo PR + Actions walks overlap."""
    t0 = time.time()
    rc, out, err = _cli(["gh", "api", "rate_limit"], timeout=CLI_TIMEOUT_S, run=run)
    doc = _json_from_cli(out) if rc == 0 else None
    core = (doc or {}).get("resources", {}).get("core") if isinstance(doc, dict) else None
    if not isinstance(core, dict) or core.get("limit") is None:
        return {
            "kind": "UNMEASURED" if rc == 127 else "UNREACHABLE",
            "ok": False,
            "detail": (err or out or "gh api rate_limit failed")[:200],
            "prs": [], "runs": [], "age_s": round(time.time() - t0, 3),
        }
    got = {repo: {"pr": [], "run": []} for repo in GH_REPOS}
    with concurrent.futures.ThreadPoolExecutor(
            max_workers=max(1, len(GH_REPOS) * 2)) as pool:
        futs = {}
        for repo in GH_REPOS:
            futs[pool.submit(_github_prs, repo, run=run)] = ("pr", repo)
            futs[pool.submit(_github_runs, repo, run=run)] = ("run", repo)
        for fut in concurrent.futures.as_completed(futs):
            kind, repo = futs[fut]
            try:
                rows = fut.result()
            except Exception:  # noqa: BLE001
                rows = []
            got[repo][kind] = rows if isinstance(rows, list) else []
    prs, runs = [], []
    for repo in GH_REPOS:
        prs.extend(got[repo]["pr"])
        runs.extend(got[repo]["run"])
    return {
        "kind": "OK",
        "ok": True,
        "bound": f"rest_limit={core.get('limit')} remaining={core.get('remaining')}",
        "limit": core.get("limit"),
        "remaining": core.get("remaining"),
        "prs": prs,
        "runs": runs,
        "age_s": round(time.time() - t0, 3),
        "via": "gh",
    }


def _live_or_broke(fut) -> dict:
    try:
        rec = fut.result()
    except Exception as e:  # noqa: BLE001
        return {
            "kind": "BROKE", "ok": False,
            "detail": f"{type(e).__name__}: {e}"[:200],
        }
    return rec if isinstance(rec, dict) else {
        "kind": "BROKE", "ok": False, "detail": "BAD_LIVE",
    }


def vendor_lives(paths, *, run=None, http=None) -> tuple[dict, dict, dict]:
    """GitHub / GitLab / Cursor folds are independent. Sequential first-fill
    measured 6.6s and sat under the extra-pane 8s FAST GET; overlap them."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        f_gh = pool.submit(github_live, run=run)
        f_gl = pool.submit(gitlab_live, run=run)
        f_cur = pool.submit(cursor_live, paths, http=http)
        return (
            _live_or_broke(f_gh),
            _live_or_broke(f_gl),
            _live_or_broke(f_cur),
        )


def gitlab_live(*, run=None) -> dict:
    """Measured `glab api user`. Does not start a pipeline."""
    t0 = time.time()
    rc, out, err = _cli(["glab", "api", "user"], timeout=CLI_TIMEOUT_S, run=run)
    doc = _json_from_cli(out) if rc == 0 else None
    if not isinstance(doc, dict) or not doc.get("id") or not doc.get("username"):
        return {
            "kind": "UNMEASURED" if rc == 127 else "UNREACHABLE",
            "ok": False,
            "detail": (err or out or "glab api user failed")[:200],
            "age_s": round(time.time() - t0, 3),
        }
    mrs = []
    mrc, mout, _ = _cli(
        ["glab", "mr", "list", "--repo", GLAB_PROJECT, "-P", "12", "-F", "json"],
        timeout=CLI_TIMEOUT_S, run=run)
    body = _json_from_cli(mout) if mrc == 0 else None
    if isinstance(body, list):
        for row in body:
            if not isinstance(row, dict):
                continue
            mrs.append({
                "repo": GLAB_PROJECT,
                "number": row.get("iid") or row.get("id"),
                "title": row.get("title"),
                "url": row.get("web_url"),
                "st": str(row.get("state") or "OPEN").upper(),
                "leg": "gitlab",
            })
    return {
        "kind": "OK",
        "ok": True,
        "bound": f"user_id={doc.get('id')} username={doc.get('username')}",
        "user_id": doc.get("id"),
        "username": doc.get("username"),
        "mrs": mrs,
        "project": GLAB_PROJECT,
        "age_s": round(time.time() - t0, 3),
        "via": "glab",
    }


def cursor_live(paths, *, http=None) -> dict:
    """Live GET /v1/me. Does not write probe json. Does not POST /v1/agents.
    Does not GET /v1/repositories."""
    t0 = time.time()
    note = ("attach_refused on isolated --gate is designed, not a dead "
            "rail. Live identity is this GET /v1/me.")
    try:
        if http is not None:
            status, headers, body = http("GET", "/v1/me", None)
            name = body.get("apiKeyName") if isinstance(body, dict) else None
            ok = status == 200 and name == "Cursor COSMOS 2"
            return {
                "kind": "OK" if ok else "UNREACHABLE",
                "ok": bool(ok),
                "http": status,
                "apiKeyName": name,
                "via": "GET /v1/me",
                "age_s": round(time.time() - t0, 3),
                "note": note,
            }
        from cosmos_cursor_rail import (
            CursorRail, key_path_for, load_spec, spec_path_for,
        )
        spec = load_spec(spec_path_for(paths))
        rail = CursorRail(key_path_for(paths, spec), spec)
        ok, detail = rail.probe()
        ident = rail.last_identity() or {}
        body = ident.get("body") if isinstance(ident.get("body"), dict) else {}
        return {
            "kind": "OK" if ok else "UNREACHABLE",
            "ok": bool(ok),
            "detail": detail,
            "http": ident.get("http"),
            "apiKeyName": body.get("apiKeyName"),
            "via": "GET /v1/me",
            "age_s": round(time.time() - t0, 3),
            "note": note,
        }
    except Exception as e:  # noqa: BLE001
        return {
            "kind": "BROKE",
            "ok": False,
            "detail": f"{type(e).__name__}: {e}"[:200],
            "age_s": round(time.time() - t0, 3),
        }


def _read_json(p: Path) -> dict | None:
    if not p.is_file():
        return None
    try:
        rec = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"kind": "BROKE"}
    return rec if isinstance(rec, dict) else {"kind": "BROKE"}


def _public_probe(rec: dict | None) -> dict | None:
    if not rec:
        return None
    if rec.get("kind") == "BROKE":
        return rec
    live = rec.get("live_value") if isinstance(rec.get("live_value"), dict) else {}
    return {
        "gate": rec.get("gate"),
        "gated_at": rec.get("gated_at"),
        "identity_ok": rec.get("identity_ok"),
        "kernel_attached": rec.get("kernel_attached"),
        "key_ok": rec.get("key_ok"),
        "key_last4": rec.get("key_last4"),
        "link_id": rec.get("link_id"),
        "http": live.get("http") or rec.get("http"),
        "apiKeyName": live.get("apiKeyName"),
        "attach_refused": bool((rec.get("attach_refusal") or {}).get("refused")),
    }


def _public_launch(rec: dict | None) -> dict | None:
    if not rec:
        return None
    if rec.get("kind") == "BROKE":
        return rec
    keep = {}
    for k in ("ok", "kind", "agent_id", "run_id", "pr_url", "branch",
              "http", "detail", "node", "status"):
        if rec.get(k) is not None:
            keep[k] = rec.get(k)
    return keep or None


def _blob(row: dict) -> str:
    return " ".join(str(row.get(k) or "") for k in
                    ("command", "job_id", "lane", "node", "detail",
                     "task", "agent", "source_url", "github_path")).lower()


def _gitur_job(row: dict) -> bool:
    blob = _blob(row)
    return any(n in blob for n in JOB_NEEDLES)


def _has(blob: str, needles: tuple[str, ...]) -> bool:
    return any(n in blob for n in needles)


def _leg_of(row: dict) -> str | None:
    blob = _blob(row)
    if _has(blob, GITLAB_NEEDLES):
        return "gitlab"
    if _has(blob, CURSOR_NEEDLES):
        return "cursor"
    if _has(blob, GITHUB_NEEDLES) or _has(blob, JOB_NEEDLES):
        return "github"
    return None


def _stage_of(row: dict) -> str | None:
    blob = _blob(row)
    if _has(blob, SGH_NEEDLES):
        return "sgh"
    if _has(blob, IMPLEMENT_NEEDLES):
        return "implement"
    if _has(blob, FORGE_NEEDLES):
        return "forge"
    if _gitur_job(row):
        return "gitur"
    return None


def _job_pub(row: dict, *, stage: str | None = None,
             leg: str | None = None, source: str = "jukebox") -> dict:
    oid = row.get("job_id") or row.get("order_id")
    st = row.get("st") or row.get("state")
    return {
        "job_id": oid,
        "st": st,
        "command": row.get("command") or row.get("task"),
        "priority": row.get("priority"),
        "age_s": row.get("age_s"),
        "lane": row.get("lane") or row.get("folder"),
        "stale_flag": row.get("stale_flag"),
        "submitted": row.get("submitted") or row.get("dropped_at")
        or row.get("timestamp"),
        "submitted_iso": row.get("submitted_iso") or row.get("timestamp")
        or row.get("dropped_at"),
        "finished": row.get("finished") or row.get("accepted_at")
        or row.get("filed_at"),
        "stage": stage or _stage_of(row),
        "leg": leg or _leg_of(row),
        "source": source,
        "terminal": bool(row.get("terminal")) or str(st or "").upper() in
        {"CLEAN", "FINDINGS", "BROKE", "COMPLETED", "FAILED", "DONE"},
    }


def _forge_bg_rows(paths) -> list[dict]:
    rows = []
    now = time.time()
    for stage in ("research", "arch", "consensus1", "consensus2"):
        d = paths.state("profiles", "forge", "bg", stage)
        if not d.is_dir():
            continue
        try:
            names = list(d.glob("*.json"))
        except OSError:
            continue
        for p in names:
            try:
                st = p.stat()
            except OSError:
                continue
            rows.append({
                "job_id": p.stem,
                "st": stage,
                "command": "forge bg " + stage,
                "age_s": round(max(0.0, now - st.st_mtime), 1),
                "submitted_iso": None,
                "finished": None,
                "stage": "forge",
                "leg": None,
                "source": "forge_bg",
                "terminal": False,
            })
    return rows


def _sgh_fold(paths) -> dict:
    from cosmos_clock import heartbeat_age_s, read_heartbeat
    from cosmos_sgh_drop_ingest import (
        GH_BRANCH, GH_DROP_PATH, GH_REPO, HEARTBEAT_NAME, SEEN_NAME,
    )
    p = paths.logs(HEARTBEAT_NAME)
    rec = read_heartbeat(p) if p.is_file() else None
    age = heartbeat_age_s(rec)
    seen_n = None
    seen_p = paths.state("work_orders", SEEN_NAME)
    seen_kind = "NO_SOURCE"
    if seen_p.is_file():
        try:
            body = json.loads(seen_p.read_text(encoding="utf-8"))
            if isinstance(body, dict):
                shas = body.get("seen") or body.get("shas") or body
                seen_n = len(shas) if isinstance(shas, (dict, list)) else None
                seen_kind = "OK"
        except (OSError, ValueError):
            seen_kind = "BROKE"
    return {
        "kind": "NO_SOURCE" if rec is None and seen_kind == "NO_SOURCE" else "OK",
        "repo": GH_REPO,
        "path": GH_DROP_PATH,
        "branch": GH_BRANCH,
        "heartbeat": HEARTBEAT_NAME,
        "age_s": None if age is None else round(age, 1),
        "last_run": None if not rec else rec.get("last_run"),
        "filed_this_tick": None if not rec else rec.get("filed_this_tick"),
        "github_via": None if not rec else rec.get("github_via"),
        "seen_kind": seen_kind,
        "seen_n": seen_n,
        "note": ("SGH Voice writes JSON to GitHub work_orders/drop. "
                 "Ingest daemon files the bucket. Does not delete GitHub. "
                 "Does not poll grok.com."),
    }


def _crew_fold(paths) -> dict:
    """10-min CCr roster + spend belong on the Gitur tab. GET never mkdir."""
    try:
        from cosmos_crew_roster import snapshot as crew_snapshot
        return crew_snapshot(paths)
    except Exception as e:  # noqa: BLE001
        return {"schema": "cosmos-crew-roster/1", "kind": "BROKE",
                "detail": f"{type(e).__name__}: {e}"[:200]}


def snapshot(kernel) -> dict:
    """Projection. kernel.registry / paths / jukebox only — no vendor poll.

    Lock is only for the 10s cache slot. Jukebox + work-order + cred folds
    run outside it — holding the lock queued extra-pane GETs behind one
    walk and the deck read 8s timeout then connection refused.
    """
    paths = kernel.paths
    key = str(getattr(paths, "root", ""))
    wall = time.time()
    with _SNAP_LOCK:
        hit = _SNAP_CACHE
        if hit["key"] == key and hit["payload"] and (wall - hit["at"]) < _SNAP_CACHE_S:
            return hit["payload"]
        if hit["busy"]:
            if hit["payload"]:
                return hit["payload"]
            return {
                "schema": SCHEMA,
                "kind": "BUSY",
                "note": "gitur fold in flight. Not an empty triad.",
            }
        _SNAP_CACHE["busy"] = True
    try:
        out = _snapshot_uncached(kernel)
    except Exception as e:  # noqa: BLE001
        with _SNAP_LOCK:
            _SNAP_CACHE["busy"] = False
        return {
            "schema": SCHEMA,
            "kind": "BROKE",
            "detail": f"{type(e).__name__}: {e}"[:200],
            "note": "GET fold refused rather than hang.",
        }
    with _SNAP_LOCK:
        _SNAP_CACHE["key"] = key
        _SNAP_CACHE["at"] = time.time()
        _SNAP_CACHE["payload"] = out
        _SNAP_CACHE["busy"] = False
    return out


def _snapshot_uncached(kernel) -> dict:
    paths = kernel.paths
    matrix = []
    rails_err = None
    try:
        reg = getattr(kernel, "registry", None)
        if reg is None:
            rails_err = "REGISTRY_NOT_COMPOSED"
        else:
            matrix = list(reg.matrix() or [])
    except Exception as e:  # noqa: BLE001
        rails_err = f"{type(e).__name__}: {e}"[:200]
        matrix = []
    by_id = {r.get("link_id"): r for r in matrix if isinstance(r, dict)}
    legs = []
    for lid, name, role in LEGS:
        row = by_id.get(lid)
        legs.append({
            "id": lid,
            "name": name,
            "role": role,
            "present": row is not None,
            "verified": None if row is None else row.get("verified"),
            "age_s": None if row is None else row.get("age_s"),
            "route": None if row is None else row.get("route"),
            "rail_type": None if row is None else row.get("rail_type"),
        })
    lease = None
    try:
        lease = read_lease(paths)
    except Exception as e:  # noqa: BLE001
        lease = {"kind": "BROKE", "detail": f"{type(e).__name__}: {e}"[:200]}
    ccr = {"held": False}
    if isinstance(lease, dict) and lease.get("schema"):
        ccr = {
            "held": True,
            "sid": lease.get("sid"),
            "stream": lease.get("stream"),
            "tree_id": lease.get("tree_id"),
            "taken_at": lease.get("taken_at"),
        }
    elif isinstance(lease, dict) and lease.get("kind"):
        ccr = {"held": False, "kind": lease.get("kind"),
               "detail": lease.get("detail")}

    jobs = []
    log = []
    jobs_kind = "UNMEASURED"
    try:
        import sys
        from pathlib import Path as _P
        _cdeck = str((_P(__file__).resolve().parent.parent / "builds" / "cdeck").resolve())
        if _cdeck not in sys.path:
            sys.path.insert(0, _cdeck)
        from cosmos_jukebox_panel import handle_get
        code, body = handle_get(str(paths.root),
                                expected_tree_id=paths.sentinel.tree_id)
        if code != 200:
            jobs_kind = (body or {}).get("error") or f"HTTP_{code}"
        else:
            q = (body or {}).get("queue") or {}
            raw = q.get("jobs") if isinstance(q, dict) else None
            if not q.get("available"):
                jobs_kind = (q.get("kind") if isinstance(q, dict) else None) or "QUEUE_UNAVAILABLE"
            else:
                jobs_kind = "jukebox"
                for row in (raw or []):
                    if not isinstance(row, dict):
                        continue
                    stage = _stage_of(row)
                    if _gitur_job(row):
                        pub = _job_pub(row, stage=stage or "gitur",
                                       source="jukebox")
                        jobs.append(pub)
                        log.append(pub)
                    elif stage in ("forge", "implement", "sgh"):
                        log.append(_job_pub(row, stage=stage, source="jukebox"))
    except Exception as e:  # noqa: BLE001
        jobs_kind = f"{type(e).__name__}: {e}"[:200]

    try:
        from cosmos_work_order import fold_work_orders
        wo = fold_work_orders(paths, limit=80)
        for row in (wo.get("rows") or []):
            if not isinstance(row, dict):
                continue
            stage = _stage_of(row) or (
                "sgh" if row.get("github_path") or row.get("source_url") else None)
            if not stage:
                continue
            log.append(_job_pub(row, stage=stage, source="work_order"))
    except Exception:  # noqa: BLE001
        pass

    for row in _forge_bg_rows(paths):
        log.append(row)

    creds = None
    try:
        from cosmos_cred_kit import snapshot as cred_snapshot
        creds = cred_snapshot(paths, rails=by_id)
    except Exception as e:  # noqa: BLE001
        creds = {"kind": "BROKE", "detail": f"{type(e).__name__}: {e}"[:200]}

    cursor = _public_probe(_read_json(paths.config(PROBE_NAME)))
    launch = _public_launch(_read_json(paths.config(LAUNCH_NAME)))
    sgh = _sgh_fold(paths)
    run = getattr(kernel, "gitur_run", None)
    gh_live, gl_live, cur_live = vendor_lives(
        paths, run=run, http=getattr(kernel, "gitur_http", None))
    by_leg = {L["id"]: L for L in legs}
    if gh_live.get("ok") and "github-forge" in by_leg:
        by_leg["github-forge"]["verified"] = True
        by_leg["github-forge"]["age_s"] = gh_live.get("age_s")
        by_leg["github-forge"]["bound"] = gh_live.get("bound")
    if gl_live.get("ok") and "gitlab-forge" in by_leg:
        by_leg["gitlab-forge"]["verified"] = True
        by_leg["gitlab-forge"]["age_s"] = gl_live.get("age_s")
        by_leg["gitlab-forge"]["bound"] = gl_live.get("bound")
    if cur_live.get("ok") and "cursor-api" in by_leg:
        by_leg["cursor-api"]["verified"] = True
        by_leg["cursor-api"]["age_s"] = cur_live.get("age_s")
        by_leg["cursor-api"]["bound"] = cur_live.get("apiKeyName")

    def _pane_jobs(leg_id: str) -> list[dict]:
        return [j for j in jobs if j.get("leg") == leg_id][:24]

    panes = {
        "github": {
            "id": "github-forge", "name": "GitHub",
            "role": "origin, PRs, GLM other-family review, SGH drop path. Not the live-tree writer.",
            "leg": next((L for L in legs if L["id"] == "github-forge"), {}),
            "jobs": _pane_jobs("github"),
            "n": sum(1 for j in jobs if j.get("leg") == "github"),
            "live": gh_live,
            "prs": gh_live.get("prs") or [],
            "runs": gh_live.get("runs") or [],
        },
        "gitlab": {
            "id": "gitlab-forge", "name": "GitLab",
            "role": "CI is the execute-the-gate. GLM review. Duo still proposes.",
            "leg": next((L for L in legs if L["id"] == "gitlab-forge"), {}),
            "jobs": _pane_jobs("gitlab"),
            "n": sum(1 for j in jobs if j.get("leg") == "gitlab"),
            "live": gl_live,
            "mrs": gl_live.get("mrs") or [],
        },
        "cursor": {
            "id": "cursor-api", "name": "Cursor",
            "role": "Lane B BUILD. Cloud Agents. Probe is GET /v1/me.",
            "leg": next((L for L in legs if L["id"] == "cursor-api"), {}),
            "probe": cursor,
            "live": cur_live,
            "launch": launch,
            "jobs": _pane_jobs("cursor"),
            "n": sum(1 for j in jobs if j.get("leg") == "cursor"),
        },
    }

    def _stage_jobs(stage: str) -> list[dict]:
        return [j for j in log if j.get("stage") == stage][:16]

    flow = [
        {
            "id": "forge",
            "label": "Forge",
            "role": "MOTIF BUILD / adversarial coders. Does not write the live tree.",
            "n": sum(1 for j in log if j.get("stage") == "forge"),
            "jobs": _stage_jobs("forge"),
        },
        {
            "id": "gitur",
            "label": "Gitur",
            "role": "GitHub + GitLab + Cursor BUILD. Proposes. Not a fourth writer.",
            "n": len(jobs),
            "jobs": jobs[:16],
        },
        {
            "id": "implement",
            "label": "Implement",
            "role": "CCr reviews all code then writes the live tree. One lease.",
            "n": sum(1 for j in log if j.get("stage") == "implement"),
            "jobs": _stage_jobs("implement"),
            "ccr": ccr,
        },
    ]

    def _log_key(j: dict):
        return str(j.get("submitted_iso") or j.get("submitted")
                   or j.get("finished") or "")

    log_sorted = sorted(log, key=_log_key, reverse=True)[:80]
    submitted_n = sum(1 for j in log if not j.get("terminal"))
    completed_n = sum(1 for j in log if j.get("terminal"))

    return {
        "schema": SCHEMA,
        "measured_at": time.time(),
        "gitur": "GitHub + GitLab + Cursor",
        "note": ("Live CLI fold: gh PRs+Actions, glab user/MRs, Cursor GET "
                 "/v1/me. Plus rails + probe file + jukebox + work-order + "
                 "Forge bg. Does not poll Cursor /v1/repositories. Does not "
                 "invent PR lists (UNMEASURED if CLI fails). Parked leftover "
                 "PRs are named, not merged."),
        "rails_err": rails_err,
        "ccr": ccr,
        "review": {
            "default": DEFAULT_REVIEWER,
            "model": DEFAULT_REVIEW_MODEL,
            "via": DEFAULT_REVIEW_VIA,
            "trigger": DEFAULT_REVIEW_TRIGGER,
            "ccr": "Grok 4.6 this TUI reviews all code before dispose",
            "note": ("GLM other-family reviews Gitur. Claude optional, not "
                     "required. Cursor stays Grok 4.6 native pool. CCr is Grok."),
        },
        "legs": legs,
        "panes": panes,
        "flow": flow,
        "sgh": sgh,
        "log": log_sorted,
        "log_n": len(log_sorted),
        "submitted_n": submitted_n,
        "completed_n": completed_n,
        "creds": creds,
        "cursor": cursor,
        "launch": launch,
        "jobs": jobs[:80],
        "jobs_n": len(jobs),
        "jobs_kind": jobs_kind,
        "crew": _crew_fold(paths),
    }
