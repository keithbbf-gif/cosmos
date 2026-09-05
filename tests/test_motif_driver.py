#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: cosmos_motif_driver mechanical clock.

Isolated from the live BTS queue and live DHx. Does not register schtasks.
Proves: tracker parse; stage-6 skip; inflight dedupe; next-stage Grok job
drop via dispatch (proven grok flags); DHx auto-stamp; tracker update;
schtasks plan is COSMOS Motif Driver every 15 minutes.
"""
from __future__ import annotations

import json
import sys
import tempfile
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "cosmos"))

from cosmos_dispatch import DEFAULT_MODEL, GROK_MAX_TURNS
from cosmos_inflight import Inflight  # noqa: E402
from cosmos_motif_driver import (
    TASK_NAME, canonical_slug, compare_projection, critique_exists, drive_once,
    effective_stage, inflight_filenames, is_advancing, motif_token,
    parse_tracker, plan_task_argv, record_agreement, release_completed,
    write_tracker_json,
)

RESULTS = []
ONE_OK = json.dumps({"ok": True})

TRACKER = """# MOTIF TRACKER

| deliverable | current stage (HONEST) | artifact | next stage |
|---|---|---|---|
| **cDeck** | 4 code — UNVETTED | builds/cdeck | 5 critique: different-family review |
| **CVM** (cosmos-android) | 4 code — UNVETTED | Ai\\tmp\\cosmos-android | 5 critique + build |
| **collector** | 6 runtime-binding gate PASSED | cosmos/cosmos_collector.py | done |
| **Cursor lane** | key verified | live/config | 4 code: wire as a COSMOS rail |
| **runtime binding — ALL** | 0 | — | nothing has passed stage 6 |
"""


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:  # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def _write(p: Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def _setup():
    td = Path(tempfile.mkdtemp(prefix="cosmos_motif_"))
    repo = td / "repo"
    queue = td / "queue"
    live = td / "live"
    for lane in (queue, queue / "_lanes" / "lg", queue / "_lanes" / "pb"):
        lane.mkdir(parents=True, exist_ok=True)
        (lane / "running").mkdir(parents=True, exist_ok=True)
        (lane / "done").mkdir(parents=True, exist_ok=True)
    (live / "logs").mkdir(parents=True)
    # dispatch() refuses a root without the sentinel (mesh() scar: existence
    # is not identity). The fixture must mint one or every drop is [NO_ROOT].
    _write(live / ".cosmos-root.json", json.dumps(
        {"system": "COSMOS", "tree_id": "KMesh-COSMOS-test",
         "schema_version": 1}))
    (live / "state" / "collector").mkdir(parents=True)
    tracker = repo / "docs" / "MOTIF_TRACKER.md"
    _write(tracker, TRACKER)
    _write(repo / "docs" / "COLLECTOR.md",
           "# COSMOS Results Collector\n\n- **2026-08-25** `log` · **idle**\n")
    dhx = repo / "docs" / "AGENT_BRIEF.md"
    _write(dhx, (
        "# DHx\n\n"
        "## Assignment log — APPEND-ONLY markers\n"
        "- preexisting\n\n"
        "## Active assignments\n"
        "- live\n"
    ))
    (repo / "docs" / "critique").mkdir(parents=True)
    return td, repo, queue, live, tracker, dhx


def main() -> int:
    td, repo, queue, live, tracker, dhx = _setup()

    rows = parse_tracker(TRACKER)
    check("parse finds 5 data rows", lambda: len(rows) == 5)
    check("cDeck slug", lambda: rows[0]["slug"] == "cdeck")
    check("CVM slug", lambda: rows[1]["slug"] == "cvm")
    check("runtimeall meta slug",
          lambda: canonical_slug("runtime binding — ALL") == "runtimeall")

    cdeck = [r for r in rows if r["slug"] == "cdeck"][0]
    cur, nxt = effective_stage(cdeck, repo)
    check("cDeck current 4 next 5", lambda: cur == 4 and nxt == 5)

    _write(repo / "docs" / "critique" / "cDeck_CRITIQUE_oa-api.md", "# c\n")
    cur2, nxt2 = effective_stage(cdeck, repo)
    check("critique file cannot lift stage (tracker row stays 4/5)",
          lambda: cur2 == 4 and nxt2 == 5
          and critique_exists(repo, "cdeck", "cDeck") is True)

    names = {"cosmos_stage6_improve__t1800.py", "other.py"}
    check("bundle stage6 marks cdeck advancing for s6",
          lambda: is_advancing("cdeck", 6, names) is not None)
    check("bundle stage6 also blocks leftover s5",
          lambda: is_advancing("cdeck", 5, names) is not None)
    check("unrelated slug not blocked by stage6 bundle",
          lambda: is_advancing("cursor", 4, names) is None)
    check("motif token match",
          lambda: is_advancing("cursor", 4, {"motif_cursor_s4_abc__t1800.py"})
          is not None)

    argv = plan_task_argv()
    check("plan_task_argv: schtasks /create",
          lambda: argv[0] == "schtasks" and argv[1] == "/create")
    check("plan_task_argv: task name COSMOS Motif Driver",
          lambda: TASK_NAME in argv)
    check("plan_task_argv: minute / 15",
          lambda: "/sc" in argv and argv[argv.index("/sc") + 1] == "minute"
          and "/mo" in argv and argv[argv.index("/mo") + 1] == "15")
    check("plan_task_argv: --once on this module",
          lambda: "cosmos_motif_driver.py" in argv[argv.index("/tr") + 1]
          and "--once" in argv[argv.index("/tr") + 1])
    check("plan_task_argv: no /rl highest",
          lambda: "/rl" not in argv)

    # inflight: CVM is already moving via an OWNED lease (the primitive).
    _write(queue / "running" / "motif_cvm_s6_busy__t1800.py", "print(1)\n")
    (live / "state").mkdir(parents=True, exist_ok=True)
    _cvm_lease = Inflight(live / "state" / "inflight.jsonl")
    _cvm_lease.claim("motif_cvm_s6", slug="cvm", stage=6,
                     job_file="motif_cvm_s6_busy__t1800.py")
    check("inflight_filenames sees running cvm token",
          lambda: any("motif_cvm_s6" in n for n in inflight_filenames(queue)))

    # Scar 2026-08-30: a COMPLETED job receipt sat in the queue root and was
    # counted as inflight, so the slug blocked itself forever with its own
    # proof of completion. cdeck + gbridge were wedged on the live tree, and
    # every later success would have wedged its own slug the same way.
    _write(queue / "motif_cursor_s4_done__t1800_result.json", ONE_OK)
    check("receipt is not inflight",
          lambda: not any("motif_cursor_s4" in n
                          for n in inflight_filenames(queue)))
    check("receipt does not block its own slug",
          lambda: is_advancing("cursor", 4, inflight_filenames(queue)) is None)

    # Filename without a lease is advisory and cannot skip. Plant AFTER the
    # receipt pins so motif_cursor_s4 in a live job file is not confused with
    # the receipt-exclusion proof.
    _write(queue / "running" / "motif_cursor_s4_busy__t1800.py", "print(1)\n")
    check("inflight_filenames still sees a cursor filename (advisory scrape)",
          lambda: any("motif_cursor_s4_busy" in n for n in inflight_filenames(queue)))

    # A lease must close on COMPLETION, not merely age out. The receipt drops
    # the __t<timeout> suffix the job file carries, and lands under
    # returns/<lane>/ rather than beside the job -- matching on the raw job
    # filename silently never fires, so leases only ever expired and a job
    # still running at TTL got dispatched twice. (2026-08-30)
    _fl = Inflight(queue / 'inflight.jsonl')
    _fl.claim('motif_zzz_s6', slug='zzz', stage=6,
              job_file='g46_grok_motif_zzz_s6_abc123__t1800.py')
    check('lease is active before its result lands',
          lambda: 'motif_zzz_s6' in _fl.active())
    check('no result yet -> nothing released',
          lambda: release_completed(_fl, queue) == [])
    (queue / 'returns' / 'cm').mkdir(parents=True, exist_ok=True)
    _write(queue / 'returns' / 'cm'
           / 'g46_grok_motif_zzz_s6_abc123_result.json', ONE_OK)
    check('result under returns/<lane> releases the lease',
          lambda: release_completed(_fl, queue) == ['motif_zzz_s6'])
    check('released lease is no longer active',
          lambda: 'motif_zzz_s6' not in _fl.active())

    # Phase 2 step one: the tracker's machine state is published as JSON.
    # Stage must be the COMPUTED integer, never the markdown cell -- the cell
    # is prose, which is the whole reason stage state cannot live in a doc.
    _tj = write_tracker_json(
        live, [{'slug': 'cdeck', 'name': 'cDeck', 'artifact': 'builds/cdeck',
                'next': '5 critique: prose, not a number - DISPATCHED x'}],
        tracker, 'stamp-1', {'cdeck': (5, 6)})
    check('tracker json publishes an integer stage, not the prose cell',
          lambda: _tj['rows'][0]['current_stage'] == 5
          and _tj['rows'][0]['next_stage'] == 6)
    check('tracker json keeps the raw cell for provenance',
          lambda: 'prose, not a number' in (_tj['rows'][0]['raw_next_cell'] or ''))
    check('markdown is still declared authority (flip is Phase 2 step two)',
          lambda: _tj['authority'] == 'markdown')
    check('first write reports no drift',
          lambda: _tj['drift_since_last_tick'] == [])
    _tj2 = write_tracker_json(
        live, [{'slug': 'cdeck', 'name': 'cDeck', 'artifact': 'builds/cdeck'}],
        tracker, 'stamp-2', {'cdeck': (6, 6)})
    check('a stage change since last tick is reported as drift',
          lambda: _tj2['drift_since_last_tick']
          == [{'slug': 'cdeck', 'was': 5, 'now': 6}])

    t_before = datetime.now().astimezone()
    rec = drive_once(repo=repo, queue=queue, runtime_root=live,
                     tracker=tracker, collector_md=repo / "docs" / "COLLECTOR.md",
                     dhx=dhx, dry_run=False)
    t_after = datetime.now().astimezone()

    slugs_dropped = {d["slug"] for d in rec["dispatched"]}
    skip_reasons = {s["slug"]: s["reason"] for s in rec["skipped"]}
    check("drive_once ok", lambda: rec["ok"] is True)
    check("meta runtimeall skipped",
          lambda: skip_reasons.get("runtimeall") == "meta")
    check("collector at stage 6 skipped",
          lambda: skip_reasons.get("collector") == "stage6")
    check("cvm inflight skipped",
          lambda: skip_reasons.get("cvm") == "inflight")
    check("cdeck dropped at tracker next (critique file cannot lift to s6)",
          lambda: "cdeck" in slugs_dropped)
    check("cursor dropped (filename without a lease cannot skip)",
          lambda: "cursor" in slugs_dropped)
    check("at least one job file created",
          lambda: any(d.get("created") for d in rec["dispatched"]))

    cdeck_job = next(d for d in rec["dispatched"] if d["slug"] == "cdeck")
    job = Path(cdeck_job["job_path"])
    src = job.read_text(encoding="utf-8")
    check("dropped job is a grok --single job", lambda: '"--single"' in src)
    check("dropped job uses proven grok flags",
          lambda: '"--always-approve"' in src
          and f'"--max-turns", "{GROK_MAX_TURNS}"' in src
          and DEFAULT_MODEL in src)
    check("job token is motif_cdeck_s5 (tracker next, not critique-lifted s6)",
          lambda: motif_token("cdeck", 5) in (cdeck_job.get("token") or ""))
    check("DHx marker stamped",
          lambda: cdeck_job.get("marker")
          and cdeck_job["marker"] in dhx.read_text(encoding="utf-8"))
    check("DHx stamp is ISO with offset",
          lambda: "T" in (cdeck_job.get("stamp") or "")
          and cdeck_job["stamp"][-6] in "+-"
          and "~" not in cdeck_job["stamp"])
    check("stamp in call window",
          lambda: t_before <= datetime.fromisoformat(cdeck_job["stamp"]) <= t_after)

    tr_txt = tracker.read_text(encoding="utf-8")
    check("tracker records DISPATCHED for cdeck",
          lambda: "DISPATCHED motif_cdeck_s5" in tr_txt)
    check("tracker tick footer written",
          lambda: "<!-- motif-driver-tick -->" in tr_txt
          and "dispatched=" in tr_txt)
    hb = live / "logs" / "motif_driver_heartbeat.json"
    check("heartbeat written", lambda: hb.exists())
    hbj = json.loads(hb.read_text(encoding="utf-8"))
    check("heartbeat last_run_epoch is int",
          lambda: isinstance(hbj.get("last_run_epoch"), int))

    # PHASE 2 step two: PREPARE the authority flip -- measure it, never take it.
    # The point of these checks is that the comparison CAN FAIL. A checker that
    # only ever agrees is not evidence for flipping; it is the same claim-as-
    # evidence that cost three days on 2026-08-26. So each divergence class is
    # injected deliberately and the checker must NAME it.
    proj = live / "state" / "motif_tracker.json"
    good = proj.read_text(encoding="utf-8")

    check("projection carries the real row's markdown cell as provenance",
          lambda: any("critique" in (r.get("raw_next_cell") or "")
                      for r in json.loads(good)["rows"]))

    v_ok = compare_projection(live, tracker, repo)
    check("projection agrees with a fresh markdown parse",
          lambda: v_ok["agree"] is True and v_ok["kind"] == "agree"
          and v_ok["checked_rows"] == 5 and v_ok["divergences"] == [])

    _b = json.loads(good)
    for _r in _b["rows"]:
        if _r["slug"] == "cursor":
            _r["current_stage"] = 99
    proj.write_text(json.dumps(_b), encoding="utf-8")
    v_stage = compare_projection(live, tracker, repo)
    check("a stage the markdown does not agree with is DETECTED, with values",
          lambda: v_stage["agree"] is False
          and v_stage["kind"] == "stage_differs"
          and {"slug": "cursor", "field": "current_stage",
               "json": 99, "markdown": 0} in v_stage["divergences"])

    _b2 = json.loads(good)
    _b2["rows"] = [r for r in _b2["rows"] if r["slug"] != "cdeck"]
    proj.write_text(json.dumps(_b2), encoding="utf-8")
    v_row = compare_projection(live, tracker, repo)
    check("a row missing from the projection is DETECTED",
          lambda: v_row["kind"] == "row_set_differs"
          and any(d["slug"] == "cdeck" and d["json"] == "absent"
                  for d in v_row["divergences"]))

    proj.write_text("{ not json", encoding="utf-8")
    check("an unreadable projection refuses; it never silently agrees",
          lambda: compare_projection(live, tracker, repo)["kind"]
          == "projection_unreadable")

    proj.replace(proj.with_suffix(".stashed"))          # never delete: stage it
    check("a missing projection refuses with a typed kind",
          lambda: compare_projection(live, tracker, repo)["kind"]
          == "projection_missing")
    proj.with_suffix(".stashed").replace(proj)
    proj.write_text(good, encoding="utf-8")
    check("a missing markdown source refuses rather than agreeing by default",
          lambda: compare_projection(live, tracker / "nope.md",
                                     repo)["kind"] == "source_missing")

    # The streak is the evidence a flip would be argued from, so it must be
    # earnable only by agreeing ticks and resettable by one divergence.
    banked = json.loads((live / "state" / "motif_agreement.json")
                        .read_text(encoding="utf-8"))
    check("the driver banked an AGREEING verdict on its own tick",
          lambda: banked["agree"] is True
          and banked["consecutive_agreements"] >= 1)
    _t0 = banked["ticks_total"]
    a_bad = record_agreement(live, {"agree": False, "kind": "stage_differs",
                                    "checked_at": "t", "checked_rows": 5,
                                    "divergences": [{"slug": "cursor"}]})
    check("one divergence resets the streak to zero",
          lambda: a_bad["consecutive_agreements"] == 0
          and a_bad["last_divergence"]["kind"] == "stage_differs")
    check("history survives the reset (longest streak, tick totals)",
          lambda: a_bad["longest_streak"] >= banked["consecutive_agreements"]
          and a_bad["ticks_total"] == _t0 + 1)
    a_good = record_agreement(live, compare_projection(live, tracker, repo))
    check("the streak restarts from 1, never from where it left off",
          lambda: a_good["consecutive_agreements"] == 1)
    check("flip is NOT ready on a short streak",
          lambda: a_good["flip_ready"] is False
          and a_good["flip_streak_target"] >= 96)

    check("heartbeat publishes the agreement verdict",
          lambda: hbj.get("projection_agree") is True
          and hbj.get("projection_kind") == "agree"
          and isinstance(hbj.get("projection_streak"), int)
          and hbj.get("projection_flip_ready") is False)
    check("PHASE 2 step two does NOT take the flip: authority stays markdown",
          lambda: json.loads(proj.read_text(encoding="utf-8"))["authority"]
          == "markdown" and hbj.get("tracker_authority") == "markdown")

    # second tick is a no-op for the same next-stage (job now queued)
    rec2 = drive_once(repo=repo, queue=queue, runtime_root=live,
                      tracker=tracker, collector_md=repo / "docs" / "COLLECTOR.md",
                      dhx=dhx)
    skip2 = {s["slug"]: s["reason"] for s in rec2["skipped"]}
    check("second tick skips already-queued cdeck",
          lambda: skip2.get("cdeck") == "inflight")
    check("second tick does not re-drop cursor (queued)",
          lambda: "cursor" not in {d["slug"] for d in rec2["dispatched"]})

    dry = drive_once(repo=repo, queue=queue, runtime_root=live,
                     tracker=tracker, dhx=dhx, dry_run=True)
    check("dry_run does not crash", lambda: dry.get("dry_run") is True)

    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for l, ok, e in RESULTS:
        print(("  OK  " if ok else "  FAIL") + f" {l}" + (f"  {e}" if e else ""))
    print(f"{len(RESULTS) - len(bad)}/{len(RESULTS)} passed")
    return 1 if bad else 0


def test_motif_driver():
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
