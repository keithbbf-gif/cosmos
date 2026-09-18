#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_learn_clock - native DEFINE_AGENT_LEARN xfer clock (CLOCKS id 28).

Farm xfer loops (prompt → mouth → judge → STYLE append) run on a native
Windows --once tick, not an LLM loop. Each tick reads cosmos-xfer-loop/2
JSONL under a declared paths role (default state/session-ideas/), proposes
one STYLE line per new FAIL/DROP/HTTP_429 row that lacks xfer_applied, and
inventories WRAP/STYLE/skills/package sets.

GET never mkdir. JSONL is authority (append-only; this clock does not
rewrite source rows). STYLE appends land in a propose dir — never live
PREFIX.md. No OpenRouter. No Graphiti/Letta. Not an in-process cron.

    py -3.14 cosmos\\cosmos_learn_clock.py --root V:\\A\\Ai\\COSMOS\\live --once
    py -3.14 cosmos\\cosmos_learn_clock.py --root ... --standup
    py -3.14 cosmos\\cosmos_learn_clock.py --root ... --plan-task
    py -3.14 cosmos\\cosmos_learn_clock.py --selftest

Does not modify kernel / ledger / sched / service.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cosmos_clock import (  # noqa: E402
    create_task, plan_create, query_task, tr_cmdline, write_heartbeat,
)
from cosmos_paths import (  # noqa: E402
    ROLES, CosmosPathError, CosmosPaths,
)

WORKER = "cosmos-learn-clock"
SCHEMA = "cosmos-learn-clock/1"
XFER_SCHEMA = "cosmos-xfer-loop/2"
CLOCK_ID = 28
TASK_NAME = "COSMOS Learn Style"
HEARTBEAT_NAME = "learn_clock_heartbeat.json"
DEFAULT_JSONL_PARTS = ("session-ideas", "xfer.jsonl")
PROPOSE_PARTS = ("propose", "learn-style")
STYLE_NAME = "STYLE.md"
APPLIED_NAME = "xfer_applied.jsonl"
PREFIX_NAMES = frozenset({"PREFIX.md", "prefix.md"})
ACTION_KINDS = frozenset({"FAIL", "DROP", "HTTP_429"})
REQUIRED_FIELDS = (
    "model",
    "chair",
    "pack",
    "cached_tokens",
    "http",
    "checker.score",
    "xfer.kind",
    "prompt_path",
)
REVIEW_SETS = ("WRAP", "STYLE", "skills", "package")
_MISSING = object()


class LearnRefusal(RuntimeError):
    """Typed refuse. kind in {NO_ROOT, NO_ONCE, PREFIX_REWRITE, ESCAPE,
    IDENTITY_MISMATCH}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__("[%s] %s" % (kind, detail))


def _assert_clock_id() -> str | None:
    from cosmos_own_clocks import CLOCKS
    hits = [c for c in CLOCKS if c.get("id") == CLOCK_ID]
    if len(hits) != 1:
        return "clock id %s hits=%d in CLOCKS (need 1)" % (CLOCK_ID, len(hits))
    if hits[0].get("script") != "cosmos_learn_clock.py":
        return "clock id %s script mismatch" % CLOCK_ID
    if hits[0].get("task") != TASK_NAME:
        return "clock id %s task is not %s" % (CLOCK_ID, TASK_NAME)
    return None


def _now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def session_ideas_dir(paths: CosmosPaths) -> Path:
    return paths.role("state", "session-ideas")


def default_jsonl_path(paths: CosmosPaths) -> Path:
    return paths.role("state", *DEFAULT_JSONL_PARTS)


def propose_dir(paths: CosmosPaths) -> Path:
    return paths.role("work", *PROPOSE_PARTS)


def style_propose_path(paths: CosmosPaths) -> Path:
    return propose_dir(paths) / STYLE_NAME


def applied_path(paths: CosmosPaths) -> Path:
    return propose_dir(paths) / APPLIED_NAME


def _dotted(rec: dict, key: str):
    cur = rec
    for part in key.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return _MISSING
        cur = cur[part]
    return cur


def field_gaps(rec: dict) -> list[str]:
    """Required cosmos-xfer-loop/2 fields that are absent. Presence only."""
    if not isinstance(rec, dict):
        return list(REQUIRED_FIELDS)
    gaps = []
    schema = rec.get("schema")
    if schema is not None and schema != XFER_SCHEMA:
        gaps.append("schema")
    if schema is None:
        gaps.append("schema")
    for key in REQUIRED_FIELDS:
        val = _dotted(rec, key)
        if val is _MISSING:
            gaps.append(key)
            continue
        if key in ("model", "chair", "pack", "prompt_path", "xfer.kind"):
            if not str(val).strip():
                gaps.append(key)
    return gaps


def row_action_kind(rec: dict) -> str | None:
    kind = _dotted(rec, "xfer.kind")
    if kind is _MISSING:
        return None
    text = str(kind).strip().upper()
    return text if text in ACTION_KINDS else None


def xfer_already_applied(rec: dict) -> bool:
    if rec.get("xfer_applied") in (True, "true", "1", 1):
        return True
    xfer = rec.get("xfer")
    if isinstance(xfer, dict) and xfer.get("applied") in (True, "true", "1", 1):
        return True
    return False


def row_fingerprint(rec: dict) -> str:
    payload = {
        "model": rec.get("model"),
        "chair": rec.get("chair"),
        "pack": rec.get("pack"),
        "cached_tokens": rec.get("cached_tokens"),
        "http": rec.get("http"),
        "checker.score": _dotted(rec, "checker.score"),
        "xfer.kind": _dotted(rec, "xfer.kind"),
        "prompt_path": rec.get("prompt_path"),
    }
    blob = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _role_dirs() -> frozenset[str]:
    return frozenset(v for v in ROLES.values() if v not in (".",))


def path_under_declared_role(paths: CosmosPaths, path: Path) -> bool:
    try:
        rel = path.resolve().relative_to(paths.root.resolve())
    except ValueError:
        return False
    parts = rel.parts
    if not parts:
        return False
    return parts[0] in _role_dirs()


def resolve_jsonl(paths: CosmosPaths, jsonl: str | None) -> Path:
    """Resolve a JSONL path under a declared role. Does not mkdir."""
    if not jsonl:
        return default_jsonl_path(paths)
    raw = Path(jsonl)
    if raw.is_absolute():
        cand = raw
    else:
        text = str(jsonl).replace("\\", "/").strip("/")
        bits = [b for b in text.split("/") if b and b != "."]
        if bits and bits[0] in _role_dirs():
            cand = paths.role(bits[0], *bits[1:])
        else:
            cand = paths.role("state", *bits) if bits else default_jsonl_path(paths)
    if not path_under_declared_role(paths, cand):
        raise LearnRefusal(
            "ESCAPE",
            "JSONL %s is not under a declared paths role" % cand)
    if cand.name in PREFIX_NAMES:
        raise LearnRefusal("PREFIX_REWRITE", "Never rewrite PREFIX.md")
    return cand


def _read_jsonl_rows(path: Path) -> list[tuple[int, dict | None, str]]:
    """[(lineno, rec_or_None, raw)]. Missing file → []. Never mkdir."""
    if not path.is_file():
        return []
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return []
    out = []
    for i, line in enumerate(text.splitlines(), start=1):
        raw = line.strip()
        if not raw:
            continue
        try:
            rec = json.loads(raw)
        except ValueError:
            out.append((i, None, raw))
            continue
        out.append((i, rec if isinstance(rec, dict) else None, raw))
    return out


def _load_applied(path: Path) -> set[str]:
    seen: set[str] = set()
    if not path.is_file():
        return seen
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return seen
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except ValueError:
            continue
        if isinstance(rec, dict) and rec.get("fingerprint"):
            seen.add(str(rec["fingerprint"]))
    return seen


def _refuse_prefix(path: Path) -> None:
    if path.name in PREFIX_NAMES:
        raise LearnRefusal("PREFIX_REWRITE", "Never rewrite PREFIX.md")


def _append_line(path: Path, line: str) -> None:
    _refuse_prefix(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(line)
        if not line.endswith("\n"):
            fh.write("\n")


def style_line(rec: dict, fingerprint: str) -> str:
    score = _dotted(rec, "checker.score")
    kind = _dotted(rec, "xfer.kind")
    return (
        "- [xfer] schema=%s kind=%s model=%s chair=%s pack=%s "
        "cached_tokens=%s http=%s checker.score=%s prompt_path=%s fp=%s"
        % (
            XFER_SCHEMA,
            kind,
            rec.get("model"),
            rec.get("chair"),
            rec.get("pack"),
            rec.get("cached_tokens"),
            rec.get("http"),
            score,
            rec.get("prompt_path"),
            fingerprint[:12],
        )
    )


def _name_matches_set(name: str, label: str) -> bool:
    stem = Path(name).stem
    low = stem.lower()
    return low == label.lower() or low.startswith(label.lower())


def review_sets(paths: CosmosPaths, extra_dirs: list[Path] | None = None) -> dict:
    """Native inventory of WRAP/STYLE/skills/package. Never mkdir."""
    dirs: list[Path] = []
    ideas = session_ideas_dir(paths)
    if ideas.is_dir():
        dirs.append(ideas)
    prop = propose_dir(paths)
    if prop.is_dir():
        dirs.append(prop)
    for extra in extra_dirs or ():
        if extra.is_dir():
            dirs.append(extra)
    found: dict[str, list[dict]] = {label: [] for label in REVIEW_SETS}
    seen: set[str] = set()
    for base in dirs:
        try:
            names = os.listdir(base)
        except OSError:
            continue
        for name in names:
            fp = base / name
            key = str(fp)
            if key in seen or not fp.is_file():
                continue
            for label in REVIEW_SETS:
                if not _name_matches_set(name, label):
                    continue
                seen.add(key)
                try:
                    st = fp.stat()
                    digest = hashlib.sha256(fp.read_bytes()).hexdigest()
                except OSError:
                    found[label].append({"path": key, "kind": "UNREADABLE"})
                    break
                found[label].append({
                    "path": key,
                    "bytes": st.st_size,
                    "mtime_epoch": int(st.st_mtime),
                    "sha256": digest,
                })
                break
    return {
        "kind": "MEASURED" if any(found.values()) else "UNMEASURED",
        "sets": found,
        "n_files": sum(len(v) for v in found.values()),
        "note": "Native inventory only. No LLM. GET never mkdir.",
    }


def snapshot(paths: CosmosPaths, jsonl: str | None = None) -> dict:
    """GET fold. Never mkdir. Never invents rows."""
    try:
        src = resolve_jsonl(paths, jsonl)
    except LearnRefusal as e:
        return {
            "schema": SCHEMA,
            "xfer_schema": XFER_SCHEMA,
            "kind": "UNMEASURED",
            "ok": False,
            "refuse": e.kind,
            "detail": str(e),
            "jsonl": None,
            "jsonl_exists": False,
            "n_rows": 0,
            "note": "GET never mkdir.",
        }
    exists = src.is_file()
    rows = _read_jsonl_rows(src) if exists else []
    return {
        "schema": SCHEMA,
        "xfer_schema": XFER_SCHEMA,
        "kind": "MEASURED" if exists else "UNMEASURED",
        "ok": True,
        "jsonl": str(src),
        "jsonl_exists": exists,
        "n_rows": len(rows),
        "session_ideas_exists": session_ideas_dir(paths).is_dir(),
        "propose_exists": propose_dir(paths).is_dir(),
        "note": "Projection read only. GET never mkdir.",
    }


def poll_once(root: str, *, jsonl: str | None = None,
              dry_run: bool = False) -> dict:
    t0 = time.time()
    clock_err = _assert_clock_id()
    if clock_err:
        return {"ok": False, "state": "REFUSED", "kind": "IDENTITY_MISMATCH",
                "detail": clock_err, "clock_id": CLOCK_ID}
    paths = CosmosPaths(root)
    src = resolve_jsonl(paths, jsonl)
    ideas_before = session_ideas_dir(paths).is_dir()
    style_dest = style_propose_path(paths)
    applied_dest = applied_path(paths)
    reviews = review_sets(paths)
    if not src.is_file():
        extra = {
            "ok": True,
            "state": "UNMEASURED",
            "kind": "UNMEASURED",
            "detail": "JSONL absent; GET never mkdir",
            "jsonl": str(src),
            "jsonl_exists": False,
            "session_ideas_exists": ideas_before,
            "proposed": 0,
            "skipped_unmeasured": 0,
            "skipped_applied": 0,
            "skipped_other": 0,
            "reviews": reviews,
            "clock_id": CLOCK_ID,
            "schema": SCHEMA,
            "xfer_schema": XFER_SCHEMA,
            "elapsed_s": round(time.time() - t0, 3),
        }
        if not dry_run:
            hb_path = paths.logs() / HEARTBEAT_NAME
            extra["heartbeat"] = write_heartbeat(hb_path, WORKER, extra=extra)
            extra["heartbeat_path"] = str(hb_path)
        extra["dry_run"] = dry_run
        return extra

    applied = _load_applied(applied_dest)
    proposed = 0
    skipped_unmeasured = 0
    skipped_applied = 0
    skipped_other = 0
    actions: list[dict] = []
    for lineno, rec, _raw in _read_jsonl_rows(src):
        if rec is None:
            skipped_unmeasured += 1
            actions.append({"line": lineno, "kind": "UNMEASURED",
                            "detail": "unparseable or non-object"})
            continue
        gaps = field_gaps(rec)
        if gaps:
            skipped_unmeasured += 1
            actions.append({"line": lineno, "kind": "UNMEASURED",
                            "detail": "missing %s" % ",".join(gaps)})
            continue
        fp = row_fingerprint(rec)
        if xfer_already_applied(rec) or fp in applied:
            skipped_applied += 1
            actions.append({"line": lineno, "kind": "APPLIED",
                            "fingerprint": fp[:12]})
            continue
        kind = row_action_kind(rec)
        if kind is None:
            skipped_other += 1
            actions.append({"line": lineno, "kind": "SKIP",
                            "xfer.kind": _dotted(rec, "xfer.kind")})
            continue
        line = style_line(rec, fp)
        if not dry_run:
            _append_line(style_dest, line)
            _append_line(applied_dest, json.dumps({
                "schema": SCHEMA,
                "fingerprint": fp,
                "xfer.kind": kind,
                "prompt_path": rec.get("prompt_path"),
                "line": lineno,
                "proposed_at": _now_iso(),
            }, default=str))
            applied.add(fp)
        proposed += 1
        actions.append({"line": lineno, "kind": kind, "fingerprint": fp[:12],
                        "style": line})

    if proposed:
        state, kind_out = "PROPOSED", "MEASURED"
    elif skipped_unmeasured and not (skipped_applied or skipped_other):
        state, kind_out = "UNMEASURED", "UNMEASURED"
    else:
        state, kind_out = "IDLE", "MEASURED"

    reviews = review_sets(paths)
    extra = {
        "ok": True,
        "state": state,
        "kind": kind_out,
        "jsonl": str(src),
        "jsonl_exists": True,
        "style": str(style_dest) if (proposed and not dry_run) else (
            str(style_dest) if style_dest.is_file() else None),
        "proposed": proposed,
        "skipped_unmeasured": skipped_unmeasured,
        "skipped_applied": skipped_applied,
        "skipped_other": skipped_other,
        "reviews": reviews,
        "actions": actions,
        "clock_id": CLOCK_ID,
        "schema": SCHEMA,
        "xfer_schema": XFER_SCHEMA,
        "dry_run": dry_run,
        "elapsed_s": round(time.time() - t0, 3),
        "prefix_rewritten": False,
    }
    if not dry_run:
        hb_path = paths.logs() / HEARTBEAT_NAME
        extra["heartbeat"] = write_heartbeat(hb_path, WORKER, extra={
            k: extra[k] for k in extra
            if k not in ("actions", "reviews")
        })
        extra["heartbeat_path"] = str(hb_path)
    return extra


def standup(root: str, *, query=None, create=None) -> dict:
    """Register the 15-minute --once task if missing. Idempotent."""
    query = query or query_task
    create = create or create_task
    clock_err = _assert_clock_id()
    existing = query(TASK_NAME)
    script = Path(__file__).resolve()
    tr = tr_cmdline(script, root, "--once")
    if existing.get("ok"):
        tick_rec = poll_once(root)
        return {
            "started": "already",
            "task": existing,
            "tick": tick_rec,
            "keith_cmd": None,
            "task_name": TASK_NAME,
            "clock_id": CLOCK_ID,
            "clock_id_error": clock_err,
        }
    task = create(TASK_NAME, tr, "minute", mo=15, run_now=False)
    tick_rec = poll_once(root)
    return {
        "started": "schtasks" if task.get("ok") else "planned",
        "task": task,
        "tick": tick_rec,
        "proof": {"ok": tick_rec.get("ok"), "heartbeat": tick_rec.get("heartbeat")},
        "keith_cmd": task.get("keith_cmd") if (
            task.get("needs_elevation") or not task.get("ok")) else None,
        "task_name": TASK_NAME,
        "clock_id": CLOCK_ID,
        "clock_id_error": clock_err,
    }


def plan_task_argv(root: Path) -> list[str]:
    tr = tr_cmdline(Path(__file__).resolve(), str(root), "--once")
    return plan_create(TASK_NAME, tr, "minute", mo=15)


def emit_plan(root: str) -> dict:
    argv = plan_task_argv(Path(root))
    tr = tr_cmdline(Path(__file__).resolve(), root, "--once")
    return {
        "schema": "cosmos-learn-clock-plan/1",
        "clock_id": CLOCK_ID,
        "task_name": TASK_NAME,
        "cadence": "schtasks /sc minute /mo 15 --once",
        "tr": tr,
        "argv": argv,
        "argv_cmdline": subprocess.list2cmdline(argv),
        "heartbeat": HEARTBEAT_NAME,
        "script": "cosmos/cosmos_learn_clock.py",
        "root": str(Path(root).resolve()),
        "once_flag": "--once",
        "note": "Native Windows clock only; not an in-process cron loop.",
    }


def _selftest() -> int:
    import tempfile
    from cosmos_kernel import install  # noqa: E402

    results = []

    def check(label, fn):
        try:
            results.append((label, bool(fn()), ""))
        except Exception as e:  # noqa: BLE001
            results.append((label, False, "%s: %s" % (type(e).__name__, e)))

    src = Path(__file__).read_text(encoding="utf-8")
    body = src.split("def _selftest")[0]
    check("does not vendor Graphiti/Letta",
          lambda: "graphiti" not in body.lower() and "letta" not in body.lower())
    check("does not import OpenRouter",
          lambda: "openrouter" not in body.lower())
    check("has no in-process cron loop",
          lambda: "def loop(" not in body
          and "while True" not in body
          and "--loop" not in body
          and "time.sleep(" not in body)
    check("clock id is 28", lambda: CLOCK_ID == 28)
    check("clock id registered", lambda: _assert_clock_id() is None)

    td = Path(tempfile.mkdtemp(prefix="cosmos_learn_"))
    root = install(td / "live", tree_id="learn-selftest")
    paths = CosmosPaths(str(root), expected_tree_id="learn-selftest")
    ideas = session_ideas_dir(paths)
    prefix = paths.role("state", "PREFIX.md")
    prefix.write_text("CACHE PREFIX live — do not rewrite\n", encoding="utf-8")
    prefix_bytes = prefix.read_bytes()

    snap0 = snapshot(paths)
    check("GET never mkdir session-ideas when absent",
          lambda: snap0["kind"] == "UNMEASURED"
          and snap0["jsonl_exists"] is False
          and not ideas.exists())
    check("GET never mkdir propose dir",
          lambda: not propose_dir(paths).exists())

    rec0 = poll_once(str(root))
    check("absent JSONL is UNMEASURED skip, no mkdir ideas",
          lambda: rec0.get("kind") == "UNMEASURED"
          and rec0.get("proposed") == 0
          and not ideas.exists())
    check("PREFIX.md untouched on absent JSONL",
          lambda: prefix.read_bytes() == prefix_bytes)

    ideas.mkdir(parents=True, exist_ok=True)
    jsonl = default_jsonl_path(paths)
    (ideas / "WRAP.md").write_text("# WRAP pack\n", encoding="utf-8")
    (ideas / "skills.md").write_text("# skills\n", encoding="utf-8")
    (ideas / "package.json").write_text("{\"name\":\"farm\"}\n", encoding="utf-8")

    good = {
        "schema": XFER_SCHEMA,
        "model": "grok-4.6",
        "chair": "CCr",
        "pack": "farm",
        "cached_tokens": 2048,
        "http": 429,
        "checker": {"score": 0.21},
        "xfer": {"kind": "HTTP_429"},
        "prompt_path": "state/session-ideas/WRAP.md",
    }
    drop = dict(good)
    drop["xfer"] = {"kind": "DROP"}
    drop["http"] = 200
    drop["prompt_path"] = "state/session-ideas/skills.md"
    fail = dict(good)
    fail["xfer"] = {"kind": "FAIL"}
    fail["http"] = 500
    fail["prompt_path"] = "state/session-ideas/package.json"
    already = dict(good)
    already["xfer"] = {"kind": "FAIL", "applied": True}
    already["xfer_applied"] = True
    already["prompt_path"] = "already.md"
    incomplete = {"schema": XFER_SCHEMA, "model": "grok-4.6", "http": 429}
    other = dict(good)
    other["xfer"] = {"kind": "PASS"}
    other["http"] = 200
    other["prompt_path"] = "pass.md"

    jsonl.write_text("\n".join(json.dumps(r) for r in (
        good, drop, fail, already, incomplete, other,
    )) + "\n", encoding="utf-8")
    jsonl_bytes = jsonl.read_bytes()

    rec1 = poll_once(str(root))
    style = style_propose_path(paths)
    check("first tick proposes FAIL/DROP/HTTP_429 only",
          lambda: rec1.get("ok") is True
          and rec1.get("proposed") == 3
          and rec1.get("skipped_applied") == 1
          and rec1.get("skipped_unmeasured") == 1
          and rec1.get("skipped_other") == 1)
    check("STYLE lands in propose dir, not PREFIX",
          lambda: style.is_file()
          and style.parent == propose_dir(paths)
          and style.name == STYLE_NAME)
    text1 = style.read_text(encoding="utf-8")
    check("STYLE has one line per new actionable row",
          lambda: text1.count("- [xfer]") == 3)
    check("PREFIX.md never rewritten",
          lambda: prefix.read_bytes() == prefix_bytes
          and "PREFIX.md" not in text1)
    check("source JSONL not rewritten (authority stays append-only)",
          lambda: jsonl.read_bytes() == jsonl_bytes)
    check("reviews WRAP/skills/package natively",
          lambda: rec1["reviews"]["n_files"] >= 3
          and rec1["reviews"]["sets"]["WRAP"]
          and rec1["reviews"]["sets"]["skills"]
          and rec1["reviews"]["sets"]["package"])
    check("heartbeat written",
          lambda: (paths.logs() / HEARTBEAT_NAME).is_file())

    rec2 = poll_once(str(root))
    check("second tick is idempotent (no new STYLE lines)",
          lambda: rec2.get("proposed") == 0
          and rec2.get("skipped_applied") >= 3
          and style.read_text(encoding="utf-8") == text1)

    rec_dry = poll_once(str(root), dry_run=True)
    check("dry-run does not append STYLE",
          lambda: rec_dry.get("dry_run") is True
          and style.read_text(encoding="utf-8") == text1)

    already_rec = standup(
        str(root),
        query=lambda _n: {"ok": True, "name": TASK_NAME},
        create=lambda *a, **k: {"ok": False, "out": "not called"},
    )
    check("standup is idempotent started: already",
          lambda: already_rec.get("started") == "already")

    plan = emit_plan(str(root))
    check("plan is 15-minute --once schtask",
          lambda: plan["clock_id"] == CLOCK_ID
          and "--once" in plan["tr"]
          and "15" in plan["cadence"]
          and "minute" in plan["cadence"])

    rc_missing = main(["--root", str(root)])
    check("CLI missing --once → rc=2", lambda: rc_missing == 2)

    rc_once = main(["--root", str(root), "--once"])
    check("CLI --once returns 0", lambda: rc_once == 0)

    check("PREFIX.md still identical after CLI",
          lambda: prefix.read_bytes() == prefix_bytes)
    check("selftest stayed inside tmp root",
          lambda: style.resolve().is_relative_to(root.resolve()))

    bad = [(l, e) for l, ok, e in results if not ok]
    for l, ok, e in results:
        print(("  OK  " if ok else "  FAIL") + " %s" % l + (
            ("  " + e) if e else ""))
    print("%d/%d passed" % (len(results) - len(bad), len(results)))
    return 1 if bad else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="cosmos_learn_clock")
    ap.add_argument("--root", help="runtime root (live/)")
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--standup", action="store_true")
    ap.add_argument("--plan-task", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--jsonl", default=None,
                    help="JSONL under a declared role (default "
                         "state/session-ideas/xfer.jsonl)")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    if a.plan_task:
        if not a.root:
            print(json.dumps({"ok": False, "kind": "NO_ROOT",
                              "detail": "--root is required"}), file=sys.stderr)
            return 2
        print(json.dumps(emit_plan(a.root), indent=1))
        return 0
    if a.standup:
        if not a.root:
            print(json.dumps({"ok": False, "kind": "NO_ROOT",
                              "detail": "--root is required"}), file=sys.stderr)
            return 2
        rec = standup(a.root)
        print(json.dumps(rec, indent=1, default=str))
        return 0 if rec.get("started") in ("already", "schtasks") else 2
    if not a.root:
        print(json.dumps({"ok": False, "kind": "NO_ROOT",
                          "detail": "--root is required"}), file=sys.stderr)
        return 2
    if not a.once:
        print(json.dumps({
            "ok": False,
            "kind": "NO_ONCE",
            "detail": "--once is required (native schtask tick; not an LLM loop)",
        }), file=sys.stderr)
        return 2
    rec = poll_once(a.root, jsonl=a.jsonl, dry_run=bool(a.dry_run))
    print(json.dumps(rec, indent=1, default=str))
    return 0 if rec.get("ok") else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except LearnRefusal as e:
        print(json.dumps({"ok": False, "state": "REFUSED", "kind": e.kind,
                          "detail": str(e)}), file=sys.stderr)
        raise SystemExit(2)
    except CosmosPathError as e:
        print(json.dumps({"ok": False, "state": "REFUSED", "kind": "NO_ROOT",
                          "detail": str(e)}), file=sys.stderr)
        raise SystemExit(2)
