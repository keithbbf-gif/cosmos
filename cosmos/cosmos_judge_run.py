#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""One Judge per run, partner autopsy, attempt JSONL.

DEFINE: work_orders/ccr/DEFINE_JUDGE_RUN.md. Not a second scheduler.
GET never mkdir. A silent miss is UNMEASURED, never a guessed id.

    py -3.14 cosmos\\cosmos_judge_run.py --selftest
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

SCHEMA = "cosmos-judge-run/1"
ATTEMPT_SCHEMA = "cosmos-score-attempt/1"
IDLE_LO = 20
IDLE_HI = 40
TASK_PREFIX = 80


def _warn(kind: str, detail: str) -> None:
    try:
        from cosmos_warn import warn3
        warn3(kind, detail)
    except Exception:  # noqa: BLE001
        pass


def stamp_minute(value) -> str | None:
    """YYYY-MM-DDTHH:MM from an ISO timestamp. Unparseable is None."""
    s = str(value or "").strip()
    if len(s) < 16 or s[4] != "-" or s[7] != "-" or s[10] != "T":
        return None
    hhmm = s[11:16]
    if len(hhmm) != 5 or hhmm[2] != ":":
        return None
    return s[:16]


def task_prefix(value, n: int = TASK_PREFIX) -> str:
    return " ".join(str(value or "").split())[:n]


def _pair_of(row: dict):
    if not isinstance(row, dict):
        return None
    return row.get("pair_id") or row.get("ab_pair_id") or None


def wo_partner(order, siblings=None) -> dict:
    """{partner_id, partner_state} or UNMEASURED.

    Same family: explicit pair_id / ab_pair_id, else the same stamp-minute,
    else the same Task prefix. A lookup that finds nothing is UNMEASURED.
    """
    empty = {
        "partner_id": None,
        "partner_state": "UNMEASURED",
        "kind": "UNMEASURED",
    }
    if not isinstance(order, dict):
        return dict(empty)
    oid = str(order.get("order_id") or "").strip()
    pair = _pair_of(order)
    minute = stamp_minute(order.get("Timestamp") or order.get("timestamp"))
    prefix = task_prefix(order.get("Task") or "")
    hits = []
    for row in list(siblings or []):
        if not isinstance(row, dict):
            continue
        rid = str(row.get("order_id") or "").strip()
        if not rid or rid == oid:
            continue
        same_pair = bool(pair) and _pair_of(row) == pair
        same_min = bool(minute) and stamp_minute(
            row.get("Timestamp") or row.get("timestamp")) == minute
        other = task_prefix(row.get("Task") or "")
        same_task = bool(prefix) and other == prefix
        if same_pair or same_min or same_task:
            hits.append((0 if same_pair else 1, rid, row))
    if not hits:
        return dict(empty)
    hits.sort(key=lambda item: (item[0], item[1]))
    hit = hits[0][2]
    state = hit.get("state") or hit.get("partner_state")
    if not state:
        return {
            "partner_id": str(hit.get("order_id")),
            "partner_state": "UNMEASURED",
            "kind": "UNMEASURED",
        }
    return {
        "partner_id": str(hit.get("order_id")),
        "partner_state": str(state),
        "kind": "MEASURED",
    }


def judge_idle_gate(n_board, cache_alive, *, n_pairs=0) -> str:
    """sit or leave. Empty board + dead cache leaves the chair.

    Sit when n_board is in 20–40, when the board is already past 40,
    or when the cache is still alive and at least one pair is waiting.
    Below 20 with a dead cache: WARN ×3, then leave. Do not mint a Judge.
    """
    try:
        n = int(n_board)
    except (TypeError, ValueError):
        _warn("JUDGE_IDLE", "n_board unmeasured — leave the chair")
        return "leave"
    if n < 0:
        _warn("JUDGE_IDLE", "n_board negative — leave the chair")
        return "leave"
    try:
        pairs = int(n_pairs or 0)
    except (TypeError, ValueError):
        pairs = 0
    if bool(cache_alive) and pairs >= 1:
        return "sit"
    if n >= IDLE_LO:
        return "sit"
    _warn(
        "JUDGE_IDLE",
        "n_board=%s cache dead — leave until %s-%s" % (n, IDLE_LO, IDLE_HI),
    )
    return "leave"


def _prefix_id(prefix: str) -> str:
    return hashlib.sha256(prefix.encode("utf-8")).hexdigest()[:16]


def judge_run_path(paths) -> Path:
    return paths.state("attempts") / "judge_run.json"


def load_judge_run(paths) -> dict | None:
    """Read the saved run. Missing file is None. Never mkdir."""
    if paths is None:
        return None
    path = judge_run_path(paths)
    if not path.is_file():
        return None
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeDecodeError):
        return None
    return obj if isinstance(obj, dict) else None


def judge_run(paths=None, *, model=None, prefix=None, attempt=1,
              prior=None) -> dict:
    """One Judge model and one fat prefix for the whole run.

    attempt > 1 reuses prior (or the saved run). It does not mint Judge #2
    because a caller passed a different model. No prior on a regrade is
    UNMEASURED.
    """
    try:
        n = int(attempt)
    except (TypeError, ValueError):
        n = 1
    saved = prior if isinstance(prior, dict) else load_judge_run(paths)
    if n > 1:
        if isinstance(saved, dict) and saved.get("model") and saved.get("prefix"):
            return {
                "schema": SCHEMA,
                "model": saved["model"],
                "prefix": saved["prefix"],
                "prefix_id": saved.get("prefix_id") or _prefix_id(str(saved["prefix"])),
                "attempt": n,
                "reused": True,
                "minted": False,
                "kind": "MEASURED",
            }
        return {
            "schema": SCHEMA,
            "model": None,
            "prefix": None,
            "prefix_id": None,
            "attempt": n,
            "reused": False,
            "minted": False,
            "kind": "UNMEASURED",
        }
    model_s = str(model or "").strip()
    prefix_s = str(prefix or "")
    if not model_s or not prefix_s.strip():
        return {
            "schema": SCHEMA,
            "model": None,
            "prefix": None,
            "prefix_id": None,
            "attempt": n,
            "reused": False,
            "minted": False,
            "kind": "UNMEASURED",
        }
    rec = {
        "schema": SCHEMA,
        "model": model_s,
        "prefix": prefix_s,
        "prefix_id": _prefix_id(prefix_s),
        "attempt": n,
        "reused": False,
        "minted": True,
        "kind": "MEASURED",
    }
    if paths is not None:
        path = judge_run_path(paths)
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_name(path.name + ".tmp")
        tmp.write_text(json.dumps(rec, indent=1), encoding="utf-8")
        tmp.replace(path)
    return rec


def attempts_path(paths) -> Path:
    return paths.state("attempts") / "attempts.jsonl"


def read_attempts(paths) -> dict:
    """GET. Missing file is UNMEASURED, n=0. Never mkdir."""
    path = attempts_path(paths)
    if not path.is_file():
        return {"kind": "UNMEASURED", "n": 0, "rows": [], "schema": ATTEMPT_SCHEMA}
    rows = []
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return {"kind": "UNMEASURED", "n": 0, "rows": [], "schema": ATTEMPT_SCHEMA}
    for line in text.splitlines():
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except ValueError:
            continue
        if isinstance(obj, dict):
            rows.append(obj)
    return {"kind": "MEASURED", "n": len(rows), "rows": rows, "schema": ATTEMPT_SCHEMA}


def _next_attempt(paths, order_id: str) -> int:
    seen = read_attempts(paths)
    n = 0
    for row in seen["rows"]:
        if str(row.get("order_id") or "") == order_id:
            try:
                n = max(n, int(row.get("attempt") or 0))
            except (TypeError, ValueError):
                continue
    return n + 1


def append_attempt(paths, row: dict) -> dict:
    """Append one cosmos-score-attempt/1 line. Write path; may mkdir."""
    path = attempts_path(paths)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, default=str) + "\n")
    return {"ok": True, "path": str(path), "attempt": row.get("attempt")}


def list_sibling_orders(paths) -> list[dict]:
    """Read existing fold files. Missing fold is empty. Never mkdir."""
    from cosmos_work_order import work_order_dirs_ro

    dirs = work_order_dirs_ro(paths)
    rows = []
    for name, folder in dirs.items():
        if not Path(folder).is_dir():
            continue
        for path in sorted(Path(folder).glob("*.json")):
            if path.name.startswith("_"):
                continue
            try:
                obj = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, ValueError, UnicodeDecodeError):
                continue
            if not isinstance(obj, dict):
                continue
            obj["_fold"] = name
            if not obj.get("state"):
                obj["state"] = {
                    "bucket": "DROPPED",
                    "picked": "PICKED_UP",
                    "assigned": "DONE",
                    "failed": "FAILED",
                    "completed": "COMPLETED",
                }.get(name)
            rows.append(obj)
    return rows


def xfer_for(partner: dict) -> str:
    """GAC re-seat when the partner is measured and not itself FAILED.

    Otherwise superseded. This records the disposition. It does not spawn.
    """
    if not isinstance(partner, dict) or partner.get("kind") != "MEASURED":
        return "superseded"
    if str(partner.get("partner_state") or "").upper() == "FAILED":
        return "superseded"
    return "GAC_RESEAT"


def autopsy_fail(paths, rec: dict, kind: str, detail: str,
                 siblings=None) -> dict:
    """Partner autopsy + one JSONL attempt. Not a scheduler."""
    oid = str((rec or {}).get("order_id") or "order")
    try:
        rows = list(siblings) if siblings is not None else list_sibling_orders(paths)
    except Exception:  # noqa: BLE001
        rows = None
    if rows is None:
        partner = {
            "partner_id": None,
            "partner_state": "UNMEASURED",
            "kind": "UNMEASURED",
        }
    else:
        partner = wo_partner(rec, rows)
    xfer = xfer_for(partner)
    follow = reseat_follow_up(paths, rec, xfer)
    try:
        attempt = _next_attempt(paths, oid)
        row = {
            "schema": ATTEMPT_SCHEMA,
            "order_id": oid,
            "attempt": attempt,
            "parent_attempt": None if attempt == 1 else attempt - 1,
            "chair": "WOMBAT",
            "verdict": "FAIL",
            "fail_kind": str(kind or "")[:80],
            "fail_detail": str(detail or "")[:240],
            "partner_id": partner.get("partner_id"),
            "partner_state": partner.get("partner_state"),
            "xfer": xfer,
            "follow_up_oid": follow.get("follow_up_oid"),
        }
        append_attempt(paths, row)
        attempt_kind = "MEASURED"
    except Exception as e:  # noqa: BLE001
        attempt = None
        attempt_kind = "UNMEASURED"
        row = {"error": "%s: %s" % (type(e).__name__, e)}
    return {
        "wo_partner": partner,
        "partner_id": partner.get("partner_id"),
        "partner_state": partner.get("partner_state"),
        "xfer": xfer,
        "follow_up_oid": follow.get("follow_up_oid"),
        "reseat": follow,
        "attempt": attempt,
        "attempt_schema": ATTEMPT_SCHEMA,
        "attempt_kind": attempt_kind,
        "attempt_row": row,
    }


CACHE_TTL_S = 30 * 60


def board_counts(paths) -> dict:
    """bucket + picked only. GET never mkdir. Absent fold is UNMEASURED, not 0."""
    from cosmos_work_order import work_order_dirs_ro

    dirs = work_order_dirs_ro(paths)
    present = False
    counts = {"bucket": 0, "picked": 0}
    rows = []
    for name in ("bucket", "picked"):
        folder = Path(dirs[name])
        if not folder.is_dir():
            continue
        present = True
        for path in folder.glob("*.json"):
            if not path.is_file() or path.name.startswith("_") or path.name.endswith(".tmp"):
                continue
            counts[name] += 1
            try:
                obj = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, ValueError, UnicodeDecodeError):
                continue
            if isinstance(obj, dict):
                rows.append(obj)
    pairs = {}
    for row in rows:
        pair = _pair_of(row)
        if pair:
            pairs[pair] = pairs.get(pair, 0) + 1
    n_pairs = sum(1 for n in pairs.values() if n >= 2)
    if not present:
        return {
            "kind": "UNMEASURED", "n_board": None, "n_pairs": 0,
            "counts": counts, "surface": "bucket+picked",
        }
    return {
        "kind": "MEASURED",
        "n_board": counts["bucket"] + counts["picked"],
        "n_pairs": n_pairs,
        "counts": counts,
        "surface": "bucket+picked",
    }


def cache_alive(paths, *, now=None, ttl_s: float = CACHE_TTL_S) -> bool:
    """Saved judge_run.json younger than the TTL. Missing file is dead. Never mkdir."""
    path = judge_run_path(paths)
    if not path.is_file():
        return False
    try:
        mtime = path.stat().st_mtime
    except OSError:
        return False
    if now is None:
        import time
        now = time.time()
    return (float(now) - mtime) <= float(ttl_s)


def poll_once(paths, *, model=None, prefix=None, now=None) -> dict:
    """One chair tick. Does not spawn a model and does not drop a work order.

    Leave when the board is unmeasured, or below 20 with a dead cache.
    Sit reuses the saved run. A new mint needs an explicit model and prefix.
    """
    board = board_counts(paths)
    alive = cache_alive(paths, now=now)
    n = board["n_board"] if board["kind"] == "MEASURED" else None
    chair = judge_idle_gate(n, alive, n_pairs=board.get("n_pairs") or 0)
    saved = load_judge_run(paths)
    out = {
        "schema": SCHEMA,
        "chair": chair,
        "board": board,
        "cache_alive": alive,
        "minted": False,
        "judge": None,
    }
    if chair != "sit":
        return out
    if isinstance(saved, dict) and saved.get("model") and saved.get("prefix"):
        reused = dict(saved)
        reused["reused"] = True
        reused["minted"] = False
        out["judge"] = reused
        return out
    if str(model or "").strip() and str(prefix or "").strip():
        out["judge"] = judge_run(paths, model=model, prefix=prefix, attempt=1)
        out["minted"] = True
        return out
    out["judge"] = {
        "schema": SCHEMA, "kind": "UNMEASURED", "model": None,
        "prefix": None, "minted": False,
        "note": "chair is sit; no saved run and no model/prefix to mint",
    }
    return out


def reseat_follow_up(paths, rec: dict, xfer: str) -> dict:
    """One bucket drop for a measured partner that lived. Not a scheduler.

    A corpse that is itself a reseat does not drop another. A second call
    sees the filed id and does not drop again.
    """
    none = {"dropped": False, "follow_up_oid": None, "why": xfer or "not reseat"}
    if xfer != "GAC_RESEAT":
        return none
    if not isinstance(rec, dict) or rec.get("reseated_from"):
        return {"dropped": False, "follow_up_oid": None, "why": "already a reseat"}
    oid = str(rec.get("order_id") or "").strip()
    if not oid:
        return {"dropped": False, "follow_up_oid": None, "why": "no order_id"}
    needed = ("Agent", "Context source", "Task", "Target & scope", "Timestamp", "Output")
    if any(not rec.get(k) for k in needed):
        return {"dropped": False, "follow_up_oid": None, "why": "missing six-field"}
    follow = oid + "-reseat"
    from cosmos_work_order import drop_order, order_file, work_order_dirs_ro

    dirs = work_order_dirs_ro(paths)
    for folder in dirs.values():
        if order_file(folder, follow).is_file():
            return {"dropped": False, "follow_up_oid": follow, "why": "already filed"}
    raw = {
        "Agent": rec.get("Agent"),
        "Context source": rec.get("Context source"),
        "Task": rec.get("Task"),
        "Target & scope": rec.get("Target & scope"),
        "Timestamp": rec.get("Timestamp"),
        "Output": rec.get("Output"),
        "order_id": follow,
        "reseated_from": oid,
        "pair_id": rec.get("pair_id") or rec.get("ab_pair_id"),
    }
    try:
        path = drop_order(paths, raw, order_id=follow)
    except Exception as e:  # noqa: BLE001
        return {
            "dropped": False, "follow_up_oid": None,
            "why": "%s: %s" % (type(e).__name__, e)[:200],
        }
    return {"dropped": True, "follow_up_oid": follow, "path": str(path), "why": "GAC_RESEAT"}


def archive_corpse(paths, rec: dict) -> dict:
    """Copy the corpse under state/attempts/archive. Does not delete the fold."""
    oid = str((rec or {}).get("order_id") or "").strip()
    if not oid:
        return {"ok": False, "kind": "BAD_INPUT"}
    dest = paths.state("attempts") / "archive" / (oid + ".json")
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_name(dest.name + ".tmp")
    tmp.write_text(json.dumps(rec, indent=1, default=str), encoding="utf-8")
    tmp.replace(dest)
    return {"ok": True, "path": str(dest), "deleted": False}


def backfill_failed(paths) -> dict:
    """Append attempt rows for failed orders that have none. Idempotent.

    Does not reseat and does not delete. Absent failed/ is UNMEASURED.
    """
    from cosmos_work_order import work_order_dirs_ro

    folder = Path(work_order_dirs_ro(paths)["failed"])
    if not folder.is_dir():
        return {"kind": "UNMEASURED", "appended": 0, "skipped": 0, "n": 0}
    seen = {str(row.get("order_id") or "") for row in read_attempts(paths)["rows"]}
    appended = 0
    skipped = 0
    n = 0
    for path in sorted(folder.glob("*.json")):
        if path.name.startswith("_") or path.name.endswith(".tmp"):
            continue
        n += 1
        try:
            rec = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError, UnicodeDecodeError):
            continue
        if not isinstance(rec, dict):
            continue
        oid = str(rec.get("order_id") or path.stem)
        if oid in seen:
            skipped += 1
            continue
        append_attempt(paths, {
            "schema": ATTEMPT_SCHEMA,
            "order_id": oid,
            "attempt": _next_attempt(paths, oid),
            "chair": "WOMBAT",
            "verdict": "FAIL",
            "fail_kind": str(rec.get("fail_kind") or "FAILED")[:80],
            "fail_detail": str(rec.get("fail_detail") or "")[:240],
            "partner_id": rec.get("partner_id"),
            "partner_state": rec.get("partner_state") or "UNMEASURED",
            "xfer": rec.get("xfer") or "superseded",
            "follow_up_oid": rec.get("follow_up_oid"),
            "backfill": True,
        })
        seen.add(oid)
        appended += 1
    return {"kind": "MEASURED", "appended": appended, "skipped": skipped, "n": n}


def _selftest() -> int:
    import tempfile

    from cosmos_paths import CosmosPaths, write_sentinel

    results = []

    def check(label, fn):
        try:
            results.append((label, bool(fn()), ""))
        except Exception as e:  # noqa: BLE001
            results.append((label, False, "%s: %s" % (type(e).__name__, e)))

    a = {
        "order_id": "wo-a",
        "Timestamp": "2026-09-24T16:40:00-05:00",
        "Task": "ONE bite: wo_partner returns partner",
        "state": "FAILED",
    }
    b = {
        "order_id": "wo-b",
        "Timestamp": "2026-09-24T16:40:12-05:00",
        "Task": "different task same minute",
        "state": "DONE",
    }
    hit = wo_partner(a, [a, b])
    check("same stamp-minute is the partner",
          lambda: hit["partner_id"] == "wo-b" and hit["partner_state"] == "DONE"
          and hit["kind"] == "MEASURED")
    lone = wo_partner(a, [a])
    check("no sibling is UNMEASURED",
          lambda: lone["partner_state"] == "UNMEASURED" and lone["partner_id"] is None)
    paired = wo_partner(
        {"order_id": "x", "pair_id": "ab-1", "Task": "a", "state": "FAILED"},
        [{"order_id": "y", "pair_id": "ab-1", "Task": "other", "state": "PICKED_UP",
          "Timestamp": "2026-01-01T00:00:00-05:00"}],
    )
    check("explicit pair_id wins over a different minute",
          lambda: paired["partner_id"] == "y" and paired["kind"] == "MEASURED")

    check("dead cache and n=3 leaves",
          lambda: judge_idle_gate(3, False) == "leave")
    check("n=25 sits", lambda: judge_idle_gate(25, False) == "sit")
    check("alive cache plus one pair sits under 20",
          lambda: judge_idle_gate(1, True, n_pairs=1) == "sit")
    check("unmeasured board leaves",
          lambda: judge_idle_gate(None, True, n_pairs=1) == "leave")

    minted = judge_run(model="luna", prefix="FAT-PREFIX-ONE", attempt=1)
    again = judge_run(model="other-judge", prefix="OTHER", attempt=2, prior=minted)
    check("regrade reuses the first Judge and prefix",
          lambda: again["reused"] is True and again["minted"] is False
          and again["model"] == "luna" and again["prefix"] == "FAT-PREFIX-ONE")
    missing = judge_run(model="luna", prefix="x", attempt=3)
    check("regrade with no prior is UNMEASURED",
          lambda: missing["kind"] == "UNMEASURED" and missing["minted"] is False)

    td = Path(tempfile.mkdtemp(prefix="cosmos_judge_"))
    live = td / "live"
    write_sentinel(live, tree_id="judge-selftest")
    paths = CosmosPaths(live)
    before = read_attempts(paths)
    check("GET attempts never mkdir",
          lambda: before["kind"] == "UNMEASURED" and before["n"] == 0
          and not attempts_path(paths).exists())
    extra = autopsy_fail(paths, a, "REFUSED", "grok.exe", siblings=[a, b])
    after = read_attempts(paths)
    check("fail autopsy writes one attempt and names the partner",
          lambda: extra["partner_id"] == "wo-b"
          and extra["xfer"] == "GAC_RESEAT"
          and extra["attempt"] == 1
          and after["n"] == 1
          and after["rows"][0]["schema"] == ATTEMPT_SCHEMA
          and after["rows"][0]["follow_up_oid"] is None)
    dead = autopsy_fail(
        paths, {"order_id": "wo-c", "Timestamp": "2026-09-24T16:40:00-05:00",
                "Task": "c", "state": "FAILED"},
        "FAILED", "both died",
        siblings=[{"order_id": "wo-d", "Timestamp": "2026-09-24T16:40:01-05:00",
                   "Task": "d", "state": "FAILED"}],
    )
    check("failed partner is superseded, not a new scheduler",
          lambda: dead["xfer"] == "superseded" and dead["follow_up_oid"] is None)

    idle = poll_once(paths)
    check("empty board leaves and does not mint a Judge",
          lambda: idle["chair"] == "leave" and idle["minted"] is False
          and not judge_run_path(paths).exists())
    bucket = paths.state("work_orders") / "bucket"
    bucket.mkdir(parents=True, exist_ok=True)
    for i in range(20):
        (bucket / ("n%d.json" % i)).write_text(
            json.dumps({"order_id": "n%d" % i, "state": "DROPPED"}),
            encoding="utf-8")
    sat = poll_once(paths, model="luna", prefix="FAT-PREFIX-ONE")
    check("20 on the board sits and mints one Judge",
          lambda: sat["chair"] == "sit" and sat["minted"] is True
          and sat["judge"]["model"] == "luna")
    again_tick = poll_once(paths, model="other", prefix="OTHER")
    check("second tick reuses the Judge and does not mint",
          lambda: again_tick["chair"] == "sit" and again_tick["minted"] is False
          and again_tick["judge"]["model"] == "luna")

    seat_order = {
        "order_id": "wo-seat",
        "Agent": "xAI | Grok | grok-4.6",
        "Context source": ["docs/AGENT_BRIEF.md"],
        "Task": "reseat me",
        "Target & scope": "proposals under Output only",
        "Timestamp": "2026-09-24T18:00:00-05:00",
        "Output": "proposals | reseat.md",
        "state": "FAILED",
    }
    seated = autopsy_fail(
        paths, seat_order, "FAILED", "empty output",
        siblings=[{
            "order_id": "wo-live",
            "Timestamp": "2026-09-24T18:00:10-05:00",
            "Task": "other",
            "state": "DONE",
        }],
    )
    follow_path = paths.state("work_orders") / "bucket" / "wo-seat-reseat.json"
    check("GAC re-seat drops one follow-up and does not spawn",
          lambda: seated["follow_up_oid"] == "wo-seat-reseat"
          and seated["reseat"]["dropped"] is True
          and follow_path.is_file()
          and "grok.exe" not in follow_path.read_text(encoding="utf-8"))
    seated_again = reseat_follow_up(paths, seat_order, "GAC_RESEAT")
    check("a second re-seat does not drop another order",
          lambda: seated_again["dropped"] is False
          and seated_again["why"] == "already filed")

    (paths.state("work_orders") / "failed").mkdir(parents=True, exist_ok=True)
    (paths.state("work_orders") / "failed" / "wo-old.json").write_text(
        json.dumps({"order_id": "wo-old", "state": "FAILED", "fail_kind": "FAILED"}),
        encoding="utf-8")
    filled = backfill_failed(paths)
    filled2 = backfill_failed(paths)
    check("backfill appends once and does not delete the corpse",
          lambda: filled["appended"] >= 1 and filled2["appended"] == 0
          and (paths.state("work_orders") / "failed" / "wo-old.json").is_file())

    bad = [(label, err) for label, ok, err in results if not ok]
    for label, ok, err in results:
        print(("  OK  " if ok else "  FAIL") + " " + label + (("  " + err) if err else ""))
    print("%d/%d passed" % (len(results) - len(bad), len(results)))
    return 1 if bad else 0


def main() -> int:
    import argparse
    import sys

    from cosmos_paths import CosmosPaths

    ap = argparse.ArgumentParser(prog="cosmos_judge_run")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--backfill", action="store_true")
    ap.add_argument("--root", default=None)
    ap.add_argument("--model", default=None)
    ap.add_argument("--prefix", default=None)
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.root:
        print("usage: py -3.14 cosmos\\cosmos_judge_run.py --selftest | --once --root LIVE",
              file=sys.stderr)
        return 2
    paths = CosmosPaths(a.root)
    if a.backfill:
        print(json.dumps(backfill_failed(paths), indent=1, default=str))
        return 0
    print(json.dumps(poll_once(paths, model=a.model, prefix=a.prefix), indent=1, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
