#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_verdict - voice-facing Verdict stamp + GitHub write-back + notify.

Contract: docs/VERDICT_SPEC.md. Writer is the Work-Order Runner, not the
agent. Agents stay WRITE-PRIVATE. This module does not touch kernel /
ledger / sched / service and does not add a Core route.

    stamp_verdict(rec)           mutate live rec with one Verdict object
    emit_verdict(rec, paths=…)   GitHub PUT + jsonl + optional HTTPS POST
    objection_is_concrete(s)     fail-closed validator
    format_objection(...)        self-contained rejected text

GitHub transport is injectable. Default live transport is `gh api`.
Temp installs (tree_id wo-selftest) never hit the network.
"""
from __future__ import annotations

import base64
import json
import os
import re
import subprocess
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

SCHEMA = "cosmos-wo-verdict/1"
EVENT_SCHEMA = "cosmos-wo-verdict-event/1"
STATUSES = ("applied", "rejected", "pending")
REASON_CAP = 240
NOTIFY_FILE = "ara_notify_url.txt"
JSONL_NAME = "verdict_events.jsonl"
GITHUB_PREFIX = "github:"
DEFAULT_BRANCH = "main"
DEFAULT_REPO = "keithbbf-gif/cosmos"
CLAIM_REASON = "Claimed by COSMOS Work-Order Runner; executing write-private."
DONE_REASON = "Proposal filed; awaiting COW accept."
APPLIED_REASON = "COW accepted the proposal."
VAGUE = frozenset({
    "doesn't work", "doesnt work", "failed", "error", "no", "broken",
    "wrong", "see desktop",
})
_LOC_RE = re.compile(
    r"([A-Za-z]:)?[^\s'\"]+\.(json|py|md|txt|html|css|js)\b"
    r"|\"[^\"]+\""
    r"|`[^`]+`"
)


class VerdictError(RuntimeError):
    def __init__(self, kind: str, detail: str):
        self.kind = kind
        self.detail = detail
        super().__init__(f"[{kind}] {detail}")


def _iso_now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _one_line(s: str, cap: int = REASON_CAP) -> str:
    t = " ".join(str(s or "").replace("\r", " ").split())
    return t[:cap].rstrip()


def objection_is_concrete(text: str) -> bool:
    s = str(text or "").strip()
    if len(s) < 20:
        return False
    if s.lower() in VAGUE:
        return False
    if "fix:" not in s.lower():
        return False
    return _LOC_RE.search(s) is not None


def format_objection(*, kind: str, file: str, what: str, fix: str,
                     line=None, symbol: str | None = None) -> str:
    loc = str(file or "(unknown)").strip()
    if line is not None and str(line).strip():
        loc = f"{loc}:{line}"
    sym = f" {symbol}" if symbol else ""
    body = (
        f"{kind}: {loc}{sym} — {_one_line(what, 180)}. "
        f"Fix: {_one_line(fix, 180)}."
    )
    if not objection_is_concrete(body):
        body = (
            f"{kind}: {loc} — {_one_line(what, 180) or 'order refused'}. "
            f"Fix: {_one_line(fix, 180) or 'correct the named field and re-drop'}."
        )
    return body


def make_verdict(status: str, *, reason: str, objection: str = "",
                 timestamp: str | None = None, order_id: str | None = None,
                 proposal: str | None = None) -> dict:
    st = str(status or "").strip().lower()
    if st not in STATUSES:
        raise VerdictError("BAD_INPUT", f"Verdict.status must be one of {STATUSES}")
    reason = _one_line(reason)
    if not reason:
        raise VerdictError("BAD_INPUT", "Verdict.reason is required")
    obj: dict = {
        "status": st,
        "reason": reason,
        "timestamp": timestamp or _iso_now(),
    }
    if st == "rejected":
        ob = str(objection or "").strip()
        if not objection_is_concrete(ob):
            raise VerdictError(
                "BAD_INPUT",
                "rejected Verdict.objection must name a file/field and a Fix:")
        obj["objection"] = ob
    elif objection:
        obj["objection"] = ""
    if order_id:
        obj["order_id"] = order_id
    if proposal:
        obj["proposal"] = proposal
    obj["writer"] = "cosmos-work-order"
    return obj


def parse_github_source(source: str | None) -> dict | None:
    s = str(source or "").strip()
    if not s.startswith(GITHUB_PREFIX):
        return None
    rest = s[len(GITHUB_PREFIX):].lstrip("/")
    parts = rest.split("/", 2)
    if len(parts) < 3 or not parts[0] or not parts[1] or not parts[2]:
        return None
    owner, repo, path = parts[0], parts[1], parts[2]
    if not path.startswith("work_orders/drop/") or not path.endswith(".json"):
        return None
    if path.rstrip("/").endswith("README.json") or path.endswith("/README.md"):
        return None
    return {"owner": owner, "repo": repo, "path": path,
            "repo_slug": f"{owner}/{repo}"}


def spoken_line(verdict: dict, *, order_id: str | None = None) -> str:
    st = (verdict or {}).get("status")
    oid = order_id or (verdict or {}).get("order_id") or "work order"
    if st == "pending":
        return f"Work order {oid} is in progress. {(verdict or {}).get('reason') or ''}".strip()
    if st == "applied":
        return (
            f"Work order {oid} applied. {(verdict or {}).get('reason')}. "
            f"{(verdict or {}).get('timestamp')}"
        ).strip()
    if st == "rejected":
        return f"Work order {oid} rejected. {(verdict or {}).get('objection')}".strip()
    return f"Work order {oid} has no verdict yet."


def proposal_of(rec: dict) -> str | None:
    out = rec.get("_output") or {}
    folder = out.get("folder")
    filename = out.get("filename")
    if filename and folder:
        return f"{folder}/{filename}"
    return filename or None


def verdict_for(rec: dict) -> dict | None:
    """Map live lifecycle onto the three voice statuses. DROPPED → None."""
    state = str(rec.get("state") or "").upper()
    oid = rec.get("order_id")
    prop = proposal_of(rec)
    if rec.get("rejected") or state == "FAILED":
        kind = rec.get("fail_kind") or "FAILED"
        what = rec.get("fail_detail") or rec.get("reject_note") or "order failed"
        err = ""
        run = rec.get("run") if isinstance(rec.get("run"), dict) else {}
        if run.get("err"):
            err = _one_line(run.get("err"), 120)
        loc = rec.get("source") or rec.get("_output_path") or oid or "work order"
        if str(loc).startswith(GITHUB_PREFIX):
            parsed = parse_github_source(str(loc))
            loc = parsed["path"] if parsed else loc
        fix = rec.get("reject_note") or (
            "correct the named field and re-drop the JSON on work_orders/drop/"
        )
        if kind == "FAILED" and rec.get("output_exists") is False:
            fix = (
                "re-drop with a reachable Agent rail (xAI | Grok | grok-4.6); "
                "do not retry a rail that emitted no Output file"
            )
        ob = format_objection(
            kind=str(kind), file=str(loc), what=f"{what} {err}".strip(),
            fix=str(fix), symbol=str(kind))
        reason = _one_line(rec.get("reject_note") or what) or "rejected"
        return make_verdict(
            "rejected", reason=reason, objection=ob, order_id=oid, proposal=prop)
    if state == "COMPLETED":
        reason = rec.get("accept_note") or APPLIED_REASON
        return make_verdict(
            "applied", reason=reason, objection="", order_id=oid, proposal=prop)
    if state == "DONE":
        return make_verdict(
            "pending", reason=DONE_REASON, objection="",
            order_id=oid, proposal=prop)
    if state == "PICKED_UP":
        return make_verdict(
            "pending", reason=CLAIM_REASON, objection="",
            order_id=oid, proposal=prop)
    return None


def stamp_verdict(rec: dict) -> dict | None:
    """Overwrite rec['Verdict']. Returns the object or None (DROPPED)."""
    v = verdict_for(rec)
    if v is None:
        rec.pop("Verdict", None)
        return None
    rec["Verdict"] = v
    return v


def voice_drop_payload(raw: dict, verdict: dict) -> dict:
    """Six SOP fields + Verdict. Strip live-private underscore keys."""
    keep = ("Agent", "Context source", "Task", "Target & scope",
            "Timestamp", "Output")
    out = {k: raw[k] for k in keep if k in raw}
    for k, val in raw.items():
        if k in keep or k == "Verdict" or str(k).startswith("_"):
            continue
        if k in ("state", "order_id", "run", "picked_at", "filed_at",
                 "dropped_at", "completed_at", "accepted_by", "rejected",
                 "rejected_at", "rejected_by", "reject_note", "accept_note",
                 "fail_kind", "fail_detail", "output_exists", "observed_rc",
                 "filed_by", "source", "output_head", "output_bytes",
                 "already_completed"):
            continue
        out[k] = val
    out["Verdict"] = {
        "status": verdict["status"],
        "reason": verdict["reason"],
        "timestamp": verdict["timestamp"],
    }
    if verdict["status"] == "rejected":
        out["Verdict"]["objection"] = verdict.get("objection") or ""
    return out


def _selftest_tree(paths) -> bool:
    try:
        return str(getattr(getattr(paths, "sentinel", None), "tree_id", "")) == "wo-selftest"
    except Exception:
        return False


def gh_get_file(owner: str, repo: str, path: str) -> dict:
    proc = subprocess.run(
        ["gh", "api", f"repos/{owner}/{repo}/contents/{path}"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=30)
    if proc.returncode != 0:
        raise VerdictError("GITHUB_GET", (proc.stderr or proc.stdout or "gh get failed")[:400])
    obj = json.loads(proc.stdout)
    content = base64.b64decode("".join(str(obj.get("content") or "").split()))
    return {"sha": obj.get("sha"), "json": json.loads(content.decode("utf-8")),
            "raw": obj}


def gh_put_file(owner: str, repo: str, path: str, *, message: str,
                payload: dict, sha: str, branch: str = DEFAULT_BRANCH) -> dict:
    body = {
        "message": message[:72],
        "content": base64.b64encode(
            json.dumps(payload, indent=2).encode("utf-8")).decode("ascii"),
        "sha": sha,
        "branch": branch,
    }
    proc = subprocess.run(
        ["gh", "api", "--method", "PUT",
         f"repos/{owner}/{repo}/contents/{path}",
         "--input", "-"],
        input=json.dumps(body), capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=30)
    if proc.returncode != 0:
        raise VerdictError("GITHUB_PUT", (proc.stderr or proc.stdout or "gh put failed")[:400])
    return json.loads(proc.stdout or "{}")


def load_notify_url(paths) -> tuple[str | None, str]:
    p = paths.config(NOTIFY_FILE)
    if not p.is_file():
        return None, "MISSING"
    try:
        url = p.read_text(encoding="utf-8").strip().splitlines()[0].strip()
    except OSError:
        return None, "UNREADABLE"
    if not url:
        return None, "EMPTY"
    if not url.lower().startswith("https://"):
        return None, "REFUSED_NOT_HTTPS"
    return url, "OK"


def default_http_post(url: str, body: bytes, timeout_s: float = 8.0) -> dict:
    req = urllib.request.Request(
        url, data=body, method="POST",
        headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            return {"ok": 200 <= getattr(resp, "status", 200) < 300,
                    "status": getattr(resp, "status", 200)}
    except urllib.error.HTTPError as e:
        return {"ok": False, "status": e.code, "detail": str(e)[:200]}
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        return {"ok": False, "status": None, "detail": str(e)[:200]}


def _append_jsonl(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(obj, default=str) + "\n")


def emit_verdict(rec: dict, *, paths, github: bool = True, notify: bool = True,
                 dry_run: bool = False, getter=None, putter=None,
                 poster=None) -> dict:
    """Write-back + jsonl + optional POST. Stamp first if missing."""
    prev = (rec.get("Verdict") or {}).get("status") if isinstance(
        rec.get("Verdict"), dict) else None
    verdict = stamp_verdict(rec)
    out = {
        "ok": True,
        "dry_run": bool(dry_run),
        "order_id": rec.get("order_id"),
        "status": None if verdict is None else verdict.get("status"),
        "prev_status": prev,
        "github": {"skipped": True, "kind": "NO_VERDICT" if verdict is None else "pending"},
        "notify": {"skipped": True, "kind": "NO_VERDICT" if verdict is None else "pending"},
        "jsonl": None,
    }
    if verdict is None:
        return out
    new_status = verdict["status"]
    landed = prev is None
    changed = (prev is not None and prev != new_status)
    event_name = "verdict_landed" if landed else (
        "verdict_changed" if changed else "verdict_refresh")
    src = parse_github_source(rec.get("source"))
    voice = None
    if src is not None:
        try:
            current = (getter or gh_get_file)(src["owner"], src["repo"], src["path"])
            raw = current.get("json") if isinstance(current.get("json"), dict) else {}
            voice = voice_drop_payload(raw, verdict)
            msg = f"Verdict {new_status} on {rec.get('order_id') or src['path']}"
            if dry_run or _selftest_tree(paths) or not github:
                out["github"] = {"skipped": True, "kind": "DRY" if dry_run or not github else "SELFTEST",
                                 "path": src["path"], "payload": voice, "sha": current.get("sha")}
            else:
                put = (putter or gh_put_file)(
                    src["owner"], src["repo"], src["path"],
                    message=msg, payload=voice, sha=str(current.get("sha") or ""))
                out["github"] = {"skipped": False, "kind": "PUT", "path": src["path"],
                                 "sha": (put or {}).get("content", {}).get("sha") or put.get("sha")}
        except VerdictError as e:
            out["github"] = {"skipped": True, "kind": e.kind, "detail": e.detail}
            out["ok"] = False
        except Exception as e:  # noqa: BLE001
            out["github"] = {"skipped": True, "kind": type(e).__name__, "detail": str(e)[:300]}
            out["ok"] = False
    else:
        out["github"] = {"skipped": True, "kind": "NO_GITHUB_SOURCE"}

    ev = {
        "schema": EVENT_SCHEMA,
        "order_id": rec.get("order_id"),
        "github_path": None if src is None else src["path"],
        "Verdict": {k: verdict[k] for k in ("status", "reason", "timestamp") if k in verdict},
        "prev_status": prev,
        "event": event_name,
        "spoken": spoken_line(verdict, order_id=rec.get("order_id")),
        "timestamp": verdict["timestamp"],
    }
    if verdict.get("objection"):
        ev["Verdict"]["objection"] = verdict["objection"]
    jsonl_path = paths.state("work_orders") / JSONL_NAME
    if dry_run:
        out["jsonl"] = {"skipped": True, "kind": "DRY", "path": str(jsonl_path), "event": ev}
    else:
        _append_jsonl(jsonl_path, ev)
        out["jsonl"] = {"skipped": False, "path": str(jsonl_path)}

    should_post = notify and event_name in ("verdict_landed", "verdict_changed")
    if not should_post:
        out["notify"] = {"skipped": True, "kind": "NO_STATUS_CHANGE" if notify else "OFF"}
        out["event"] = ev
        return out
    url, url_kind = load_notify_url(paths)
    if url_kind != "OK":
        out["notify"] = {"skipped": True, "kind": url_kind}
        out["event"] = ev
        return out
    body = json.dumps(ev, default=str).encode("utf-8")
    if dry_run:
        out["notify"] = {"skipped": True, "kind": "DRY", "url_host": url.split("/", 3)[2], "event": ev}
    else:
        posted = (poster or default_http_post)(url, body)
        out["notify"] = {"skipped": False, "kind": "POST", **posted}
        if not posted.get("ok"):
            out["ok"] = False
    out["event"] = ev
    return out
