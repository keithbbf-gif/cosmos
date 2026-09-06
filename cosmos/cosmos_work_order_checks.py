#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Work-order CHECKED rails — Gitur (GitHub + GitLab + Cursor), one each, on DONE.

Canon: docs/WORK_ORDER_SPEC.md step 4 CHECKED, docs/WORK_ORDER_SOP.md
"Checks (daemon, one each, before COW)". Same Work-Order Runner, on deposit
in assigned/ (the done folder), before COW accept. Not a second cron. Not
in the orch TUI. Cursor here is a CHECK, not the work-order Agent family.

Stamp shape (each rail): {status, url, detail, measured_at}.
status in {UNMEASURED, PASS, FAIL, PENDING, ERROR}. A missing rail is
UNMEASURED, never a fake green. Checks do not COMPLETE the order and do
not write kernel / ledger / sched / service.

    from cosmos_work_order_checks import (
        apply_done_checks, check_github, check_cursor, check_gitlab,
        cow_checks_view, rail_stamped, stamp_assigned_done,
    )
"""
from __future__ import annotations

import base64
import json
import os
import shutil
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

RAILS = ("github", "cursor", "gitlab")
UNMEASURED = "UNMEASURED"
PASS = "PASS"
FAIL = "FAIL"
PENDING = "PENDING"
ERROR = "ERROR"
GH_OWNER = "keithbbf-gif"
GH_REPO = "cosmos"
GH_API = "https://api.github.com"
GL_HOST = "https://gitlab.com"
GL_PROJECT = "keithbbf-gif/cosmos"
GL_PROJECT_ENC = "keithbbf-gif%2Fcosmos"
CURSOR_BASE = "https://api.cursor.com"
CURSOR_REPO = "https://github.com/keithbbf-gif/cosmos"
CURSOR_REF = "main"
CURSOR_KEY_NAME = "cursor_cosmos_key.txt"
HTTP_TIMEOUT_S = 20
CREATE_NO_WINDOW = 0x08000000 if os.name == "nt" else 0


def _iso_now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def stamp(*, status: str, url=None, detail: str = "", measured_at=None,
          extra: dict | None = None) -> dict:
    rec = {
        "status": str(status or UNMEASURED),
        "url": url,
        "detail": str(detail or "")[:800],
        "measured_at": measured_at or _iso_now(),
    }
    if extra:
        for k, v in extra.items():
            if k not in rec:
                rec[k] = v
    return rec


def unmeasured(detail: str, url=None) -> dict:
    return stamp(status=UNMEASURED, url=url, detail=detail)


def rail_stamped(rec: dict, rail: str) -> bool:
    checks = rec.get("checks") if isinstance(rec.get("checks"), dict) else {}
    item = checks.get(rail)
    return isinstance(item, dict) and "status" in item and "measured_at" in item


def proposal_branch(rec: dict) -> str:
    """Branch the GitHub/GitLab checks query. Cursor starts from main."""
    cursor = ((rec.get("checks") or {}) if isinstance(rec.get("checks"), dict)
              else {})
    cursor_st = cursor.get("cursor") if isinstance(cursor.get("cursor"), dict) else {}
    for cand in (
            rec.get("proposal_branch"),
            rec.get("branch"),
            (rec.get("git") or {}).get("branch") if isinstance(rec.get("git"), dict) else None,
            cursor_st.get("branch"),
            rec.get("order_id") and f"wo/{rec.get('order_id')}",
    ):
        s = str(cand or "").strip()
        if s:
            return s
    return "main"


def cow_checks_view(rec: dict) -> dict:
    """What COW reads at accept. Does not COMPLETE. Flags fake-green."""
    checks = rec.get("checks") if isinstance(rec.get("checks"), dict) else {}
    view = {}
    for rail in RAILS:
        item = checks.get(rail) if isinstance(checks.get(rail), dict) else {}
        view[rail] = {
            "status": item.get("status") or UNMEASURED,
            "url": item.get("url"),
            "detail": item.get("detail") or "",
            "measured_at": item.get("measured_at"),
        }
    view["any_unmeasured"] = any(view[r]["status"] == UNMEASURED for r in RAILS)
    view["any_fail"] = any(view[r]["status"] in (FAIL, ERROR) for r in RAILS)
    view["refuse_fake_green"] = any(
        view[r]["status"] == PASS and (
            not view[r]["measured_at"]
            or "absent" in view[r]["detail"].lower()
            or "no workflow" in view[r]["detail"].lower()
            or "unmeasured" in view[r]["detail"].lower()
        )
        for r in RAILS
    )
    return view


def _read_secret(paths, name: str) -> str | None:
    """One-line secret from the runtime config role. Never prints it."""
    try:
        p = paths.config(name)
    except Exception:  # noqa: BLE001
        return None
    if not Path(p).is_file():
        return None
    try:
        text = Path(p).read_text(encoding="utf-8").strip()
    except OSError:
        return None
    return text or None


def _urllib_json(url: str, method: str, body, headers: dict,
                 timeout_s: float = HTTP_TIMEOUT_S) -> tuple[int, object]:
    data = json.dumps(body).encode("utf-8") if body is not None else None
    hdrs = dict(headers)
    hdrs.setdefault("Accept", "application/json")
    if body is not None:
        hdrs.setdefault("Content-Type", "application/json")
    req = urllib.request.Request(url, method=method, data=data, headers=hdrs)
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as r:  # noqa: S310
            raw = r.read().decode("utf-8") or "null"
            try:
                return int(r.status), json.loads(raw)
            except ValueError:
                return int(r.status), {"raw": raw[:400]}
    except urllib.error.HTTPError as e:
        raw = (e.read() or b"").decode("utf-8", "replace")
        try:
            obj = json.loads(raw) if raw else {"error": str(e)}
        except ValueError:
            obj = {"error": raw[:400]}
        return int(e.code), obj
    except Exception as e:  # noqa: BLE001
        return -1, {"error": f"{type(e).__name__}: {e}"}


def _cli_json(binary: str, argv: list) -> tuple[int, object]:
    try:
        p = subprocess.run(
            [binary, *argv], capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=HTTP_TIMEOUT_S, shell=False,
            creationflags=CREATE_NO_WINDOW)
    except FileNotFoundError:
        return -1, {"error": f"{binary} not found"}
    except Exception as e:  # noqa: BLE001
        return -1, {"error": f"{type(e).__name__}: {e}"}
    raw = (p.stdout or "").strip() or (p.stderr or "").strip()
    try:
        return int(p.returncode), json.loads(raw) if raw else {}
    except ValueError:
        return int(p.returncode), {"raw": raw[:400], "rc": p.returncode}


def _github_http(paths):
    """urllib if config token exists; else `gh api`. None → UNMEASURED, no net."""
    token = _read_secret(paths, "github_token.txt") or _read_secret(
        paths, "gh_token.txt")
    if token:
        def _call(method, path, body=None):
            url = GH_API + path
            return _urllib_json(url, method, body, {
                "Authorization": "Bearer " + token,
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            })
        return _call
    gh = shutil.which("gh")
    if not gh:
        return None

    def _gh(method, path, body=None):
        api_path = path[1:] if path.startswith("/") else path
        argv = ["api", "-X", method, api_path]
        if body is not None:
            argv.extend(["-f", json.dumps(body)])
        rc, obj = _cli_json(gh, argv)
        if rc != 0:
            http = 404 if rc == 1 else -1
            return http, obj
        return 200, obj
    return _gh


def _gitlab_http(paths):
    token = _read_secret(paths, "gitlab_token.txt") or _read_secret(
        paths, "gl_token.txt")
    if token:
        def _call(method, path, body=None):
            url = GL_HOST + "/api/v4" + path
            return _urllib_json(url, method, body, {
                "PRIVATE-TOKEN": token,
            })
        return _call
    glab = shutil.which("glab")
    if not glab:
        return None

    def _gl(method, path, body=None):
        api_path = path[1:] if path.startswith("/") else path
        argv = ["api", "-X", method, api_path]
        rc, obj = _cli_json(glab, argv)
        if rc != 0:
            return (404 if rc == 1 else -1), obj
        return 200, obj
    return _gl


def _cursor_http(key: str):
    """Basic auth matching cosmos_dispatch_jobs._cursor_job (`-u KEY:`)."""
    auth = "Basic " + base64.b64encode((key + ":").encode("utf-8")).decode("ascii")

    def _call(method, path, body=None):
        return _urllib_json(CURSOR_BASE + path, method, body, {
            "Authorization": auth,
        })
    return _call


def check_github(paths, rec: dict, *, http=None) -> dict:
    """Status/checks on the proposal branch. No Actions → UNMEASURED, never PASS."""
    branch = proposal_branch(rec)
    url_actions = f"https://github.com/{GH_OWNER}/{GH_REPO}/actions"
    if http is None:
        http = _github_http(paths)
    if http is None:
        return unmeasured(
            "GitHub rail not wired (no config token, no gh) — UNMEASURED, never pass",
            url=url_actions)
    q = urllib.parse.urlencode({"branch": branch, "per_page": "5"})
    path = f"/repos/{GH_OWNER}/{GH_REPO}/actions/runs?{q}"
    try:
        status, body = http("GET", path)
    except Exception as e:  # noqa: BLE001
        return unmeasured(f"GitHub Actions GET raised {type(e).__name__}: {e}",
                          url=url_actions)
    if status in (-1, 401, 403, 404):
        return unmeasured(
            f"GitHub Actions HTTP {status} (Actions may be absent — "
            "UNMEASURED, never fake green)",
            url=url_actions)
    if not isinstance(body, dict):
        return unmeasured("GitHub Actions body is not an object", url=url_actions)
    msg = str(body.get("message") or "")
    if "workflow_runs" not in body:
        return unmeasured(
            msg or "GitHub Actions payload has no workflow_runs "
            "(Actions may be absent — UNMEASURED, never pass)",
            url=url_actions)
    runs = body.get("workflow_runs") or []
    if not runs:
        return unmeasured(
            "GitHub Actions has no workflow_runs on this branch "
            "(Actions may be absent — UNMEASURED, never pass)",
            url=url_actions)
    latest = runs[0] if isinstance(runs[0], dict) else {}
    html = latest.get("html_url") or url_actions
    run_status = str(latest.get("status") or "")
    conclusion = latest.get("conclusion")
    if run_status and run_status != "completed":
        return stamp(status=PENDING, url=html,
                     detail=f"Actions run {run_status} on {branch}")
    if conclusion == "success":
        return stamp(status=PASS, url=html,
                     detail=f"Actions conclusion=success on {branch}")
    return stamp(status=FAIL, url=html,
                 detail=f"Actions conclusion={conclusion!r} on {branch}")


def check_cursor(paths, rec: dict, *, http=None) -> dict:
    """Composer is Lane B at pickup. Live post-DONE must not POST /v1/agents.

    Tests inject http= and still exercise the old launch body. Live
    (http is None) never creates Cloud Agents — 2026-09-02 token burn.
    """
    if http is None:
        return unmeasured(
            "Cursor post-DONE POST disabled — Composer is Lane B at pickup, "
            "not a check (token burn 2026-09-02)")
    oid = rec.get("order_id") or ""
    outp = rec.get("_output_path") or ""
    body = {
        "prompt": {
            "text": (
                f"CHECK work-order {oid}. Review the proposal Output at {outp}. "
                "This is a CHECK rail, not the work-order Agent. "
                "Do not write the Windows live tree. Do not COMPLETE the order."
            ),
        },
        "repos": [{"url": CURSOR_REPO, "startingRef": CURSOR_REF}],
        "autoCreatePR": True,
    }
    try:
        status, created = http("POST", "/v1/agents", body)
    except Exception as e:  # noqa: BLE001
        return unmeasured(f"Cursor POST /v1/agents raised {type(e).__name__}: {e}")
    if status in (-1, 401, 403, 404):
        return unmeasured(f"Cursor POST /v1/agents HTTP {status}")
    if status not in (200, 201) or not isinstance(created, dict):
        err = ""
        if isinstance(created, dict):
            err = str(created.get("error") or created.get("message") or "")[:200]
        return stamp(status=ERROR, detail=f"Cursor POST HTTP {status} {err}".strip())
    agent = created.get("agent") if isinstance(created.get("agent"), dict) else {}
    run = created.get("run") if isinstance(created.get("run"), dict) else {}
    aid = agent.get("id") or created.get("id")
    rid = run.get("id") or created.get("latestRunId") or agent.get("latestRunId")
    git = run.get("git") if isinstance(run.get("git"), dict) else {}
    branches = git.get("branches") if isinstance(git.get("branches"), list) else []
    first = branches[0] if branches and isinstance(branches[0], dict) else {}
    pr_url = first.get("prUrl")
    branch = first.get("branch")
    extra = {}
    if aid:
        extra["agent_id"] = aid
    if rid:
        extra["run_id"] = rid
    if branch:
        extra["branch"] = branch
    if aid and rid:
        return stamp(
            status=PENDING, url=pr_url,
            detail=f"Cursor CHECK launched agent={aid} run={rid}",
            extra=extra)
    return stamp(status=PENDING, url=pr_url,
                 detail="Cursor POST /v1/agents accepted (no agent/run id)",
                 extra=extra)


def check_gitlab(paths, rec: dict, *, http=None) -> dict:
    """Existing .gitlab-ci.yml test stage on the proposal branch."""
    branch = proposal_branch(rec)
    url_ci = f"{GL_HOST}/{GL_PROJECT}/-/pipelines"
    if http is None:
        http = _gitlab_http(paths)
    if http is None:
        return unmeasured(
            "GitLab rail not wired (no config token, no glab)",
            url=url_ci)
    q = urllib.parse.urlencode({"ref": branch, "per_page": "5"})
    path = f"/projects/{GL_PROJECT_ENC}/pipelines?{q}"
    try:
        status, body = http("GET", path)
    except Exception as e:  # noqa: BLE001
        return unmeasured(f"GitLab pipelines GET raised {type(e).__name__}: {e}",
                          url=url_ci)
    if status in (-1, 401, 403, 404):
        return unmeasured(f"GitLab pipelines HTTP {status}", url=url_ci)
    pipelines = body if isinstance(body, list) else None
    if pipelines is None and isinstance(body, dict):
        pipelines = body.get("pipelines")
    if not pipelines:
        # Invoke the existing test-stage YAML on this branch (one POST).
        try:
            s2, created = http(
                "POST",
                f"/projects/{GL_PROJECT_ENC}/pipeline?ref="
                + urllib.parse.quote(branch, safe=""),
                {})
        except Exception as e:  # noqa: BLE001
            return unmeasured(
                f"GitLab no pipeline on {branch}; POST raised {type(e).__name__}: {e}",
                url=url_ci)
        if s2 in (200, 201) and isinstance(created, dict) and created.get("id"):
            return stamp(
                status=PENDING,
                url=created.get("web_url") or url_ci,
                detail=f"GitLab pipeline created on {branch} "
                       f"status={created.get('status')} (test stage)",
                extra={"pipeline_id": created.get("id")})
        return unmeasured(
            f"GitLab no pipeline on {branch} and POST HTTP {s2}",
            url=url_ci)
    latest = pipelines[0] if isinstance(pipelines[0], dict) else {}
    html = latest.get("web_url") or url_ci
    pid = latest.get("id")
    st = str(latest.get("status") or "")
    test_detail = ""
    if pid is not None:
        try:
            js, jobs = http(
                "GET", f"/projects/{GL_PROJECT_ENC}/pipelines/{pid}/jobs")
        except Exception:  # noqa: BLE001
            js, jobs = -1, None
        if js == 200 and isinstance(jobs, list):
            test_jobs = [j for j in jobs if isinstance(j, dict)
                         and (j.get("stage") == "test" or j.get("name") == "test")]
            if test_jobs:
                names = ", ".join(
                    f"{j.get('name')}={j.get('status')}" for j in test_jobs[:6])
                test_detail = f"; test stage: {names}"
                if st in ("success", "passed") and any(
                        j.get("status") in ("failed", "canceled") for j in test_jobs):
                    return stamp(status=FAIL, url=html,
                                 detail=f"GitLab pipeline {st} but test job failed{test_detail}")
    if st in ("success", "passed"):
        return stamp(status=PASS, url=html,
                     detail=f"GitLab pipeline {st} on {branch}{test_detail}")
    if st in ("failed", "canceled", "cancelled"):
        return stamp(status=FAIL, url=html,
                     detail=f"GitLab pipeline {st} on {branch}{test_detail}")
    if st:
        return stamp(status=PENDING, url=html,
                     detail=f"GitLab pipeline {st} on {branch}{test_detail}")
    return unmeasured(f"GitLab pipeline on {branch} has no status", url=html)


def _resolve_rails(rails):
    defaults = {
        "github": check_github,
        "cursor": check_cursor,
        "gitlab": check_gitlab,
    }
    if rails is None:
        return defaults
    if rails is False:
        return None
    if not isinstance(rails, dict):
        raise TypeError("check_rails must be dict | None | False")
    out = dict(defaults)
    out.update(rails)
    return out


def apply_done_checks(paths, rec: dict, *, rails=None, persist: bool = True) -> dict:
    """Stamp checks.* on a DONE record. Skip already-stamped rails. Never COMPLETE.

    FAILED / non-DONE records are returned unchanged (not checked).
    """
    rec = dict(rec)
    if rec.get("state") != "DONE":
        rec["checks_invoked"] = []
        return rec
    resolved = _resolve_rails(rails)
    if resolved is None:
        rec["checks_invoked"] = []
        return rec
    checks = dict(rec.get("checks") or {}) if isinstance(rec.get("checks"), dict) else {}
    rec["checks"] = checks
    invoked = []
    for rail in RAILS:
        if rail_stamped(rec, rail):
            continue
        fn = resolved.get(rail) or (lambda _p, _r, _rail=rail: unmeasured(
            f"{_rail} rail missing"))
        try:
            item = fn(paths, rec)
        except Exception as e:  # noqa: BLE001
            item = unmeasured(f"{rail} raised {type(e).__name__}: {e}")
        if not isinstance(item, dict) or "status" not in item:
            item = unmeasured(f"{rail} returned no stamp")
        item.setdefault("url", None)
        item.setdefault("detail", "")
        item.setdefault("measured_at", _iso_now())
        checks[rail] = item
        invoked.append(rail)
    rec["checks"] = checks
    rec["checked"] = all(rail_stamped(rec, r) for r in RAILS)
    rec["checks_invoked"] = invoked
    if rec["checked"]:
        rec["checked_at"] = rec.get("checked_at") or _iso_now()
    rec["cow_checks"] = cow_checks_view(rec)
    rec["state"] = "DONE"
    if persist and rec.get("order_id"):
        try:
            from cosmos_work_order import (  # local: avoid import cycle at load
                _atomic_json, order_file, work_order_dirs,
            )
            dest = order_file(work_order_dirs(paths)["assigned"], rec["order_id"])
            if dest.parent.is_dir():
                _atomic_json(dest, rec)
        except Exception:  # noqa: BLE001
            pass
    return rec


def stamp_assigned_done(paths, *, rails=None) -> list:
    """Crash-recovery: DONE in assigned/ missing a rail gets that rail once."""
    resolved = _resolve_rails(rails)
    if resolved is None:
        return []
    from cosmos_work_order import _read_json, work_order_dirs

    dirs = work_order_dirs(paths)
    assigned = dirs["assigned"]
    if not assigned.is_dir():
        return []
    out = []
    for p in sorted(assigned.glob("*.json")):
        if p.name.startswith("_") or p.name.endswith(".tmp"):
            continue
        try:
            rec = _read_json(p)
        except Exception:  # noqa: BLE001
            continue
        if rec.get("state") != "DONE":
            continue
        new = apply_done_checks(paths, rec, rails=resolved, persist=True)
        out.append({
            "order_id": new.get("order_id"),
            "invoked": new.get("checks_invoked") or [],
            "checked": new.get("checked"),
        })
    return out
