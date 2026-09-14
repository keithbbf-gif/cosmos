#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cDeck feature pins for the normalized jukebox fold (PS-03).

    py -3.14 test_deck_features.py
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "cosmos"))
sys.path.insert(0, str(HERE))

from cosmos_jukebox_panel import IN_FLIGHT, LEGAL_STATES, handle_get  # noqa: E402
from cosmos_kernel import Kernel, install  # noqa: E402
from cosmos_service import Service  # noqa: E402

RESULTS: list[tuple[str, bool, str]] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    RESULTS.append((label, bool(ok), str(detail)[:400]))


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="cdeck_jukebox_feat_"))
    root = install(td / "live", tree_id="cdeck-jukebox-feat")
    k = Kernel(root, worker="core")
    qid = k.sched.submit("gitur forge implement — do not classify", "low")
    rid = k.sched.submit("py:run.py", "normal")
    fid = k.sched.submit("py:find.py", "high")
    k.sched.claim_next()
    k.sched.done(fid, "FINDINGS")
    k.sched.claim_next()
    k.sched.report_stale(older_than_s=-1)

    code, body = handle_get(str(root), expected_tree_id="cdeck-jukebox-feat",
                            kernel=k)
    check("fold is 200", code == 200 and body.get("ok") is True, str(code))
    by = {r["job_id"]: r for r in body["jobs"]}
    check("QUEUED/RUNNING/FINDINGS from scheduler, not command text",
          by[qid]["st"] == "QUEUED" and by[rid]["st"] == "RUNNING"
          and by[fid]["st"] == "FINDINGS"
          and by[qid]["stage"] == "UNMEASURED"
          and by[qid]["product"] == "UNATTRIBUTED",
          by[qid]["st"])
    check("stale is a flag on RUNNING",
          by[rid]["stale_flag"] is True and by[rid]["st"] == "RUNNING")
    check("FINDINGS is not done_n; BROKE is not in-flight",
          body["done_n"] == 0 and body["findings_n"] == 1
          and body["in_flight_n"] == 3
          and set(IN_FLIGHT) == {"QUEUED", "RUNNING", "FINDINGS"})
    check("compatibility aliases present",
          body["queue"]["jobs"] == body["jobs"]
          and body["jobs_n"] == 3
          and body["stale_flagged"] == 1)
    check("no invented cancel/retry verbs in the fold",
          "actions" not in body and "cancel" not in body
          and "retry" not in body)

    svc = Service(k, host="127.0.0.1", port=0)
    svc.serve_background()
    try:
        import urllib.request
        req = urllib.request.Request(
            "http://127.0.0.1:%s/api/v1/jobs" % svc.port)
        with urllib.request.urlopen(req, timeout=10) as resp:
            jobs = json.loads(resp.read().decode("utf-8"))
        check("existing /jobs stays {measured_at, jobs: {id: st}}",
              isinstance(jobs.get("jobs"), dict)
              and jobs["jobs"][qid] == "QUEUED"
              and "counts" not in jobs)
        import cosmos_service as svcmod
        orig = svcmod._cdeck_panel_get
        svcmod._cdeck_panel_get = lambda mod: (_ for _ in ()).throw(
            ImportError("uncomposed"))
        try:
            req = urllib.request.Request(
                "http://127.0.0.1:%s/api/v1/jukebox" % svc.port)
            try:
                urllib.request.urlopen(req, timeout=10)
                code503 = 200
                err = None
            except Exception as e:  # noqa: BLE001
                import urllib.error
                if isinstance(e, urllib.error.HTTPError):
                    code503 = e.code
                    err = json.loads(e.read().decode("utf-8")).get("error")
                else:
                    code503 = 0
                    err = str(e)
        finally:
            svcmod._cdeck_panel_get = orig
        check("uncomposed binder stays 503 CDECK_PANEL_NOT_COMPOSED",
              code503 == 503 and err == "CDECK_PANEL_NOT_COMPOSED",
              "%s %s" % (code503, err))
    finally:
        svc.shutdown()

    failed = [r for r in RESULTS if not r[1]]
    for label, ok, detail in RESULTS:
        mark = "OK  " if ok else "FAIL"
        extra = ("  [" + detail + "]") if detail and not ok else ""
        print("  %s  %s%s" % (mark, label, extra))
    print("%d/%d passed" % (len(RESULTS) - len(failed), len(RESULTS)))
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
