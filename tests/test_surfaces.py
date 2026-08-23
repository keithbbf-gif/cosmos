#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: cosmos_surfaces (storage surfaces as first-class MEASURED resources). Refusals
BY KIND; the three qualification questions each proven to fail on their own axis; a stale
measurement disqualified by advancing an injected clock past the window; "publishing is not
backup" and "off-machine or it does not count" made structural rather than remembered."""
from __future__ import annotations
import sys, tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cosmos_ledger import Ledger
from cosmos_surfaces import Surfaces, SurfaceError

RESULTS = []

def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                            # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))

def expect(exc, kind):
    def wrap(f):
        def inner():
            try:
                f()
            except exc as e:
                return e.kind == kind
            return False
        return inner
    return wrap


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="cosmos_surf_"))
    KEY = b"k"

    # ================= SURFACES =================
    fake = [1000.0]
    led = Ledger(td / "surfaces.jsonl", KEY, "F5", clock=lambda: fake[0])
    sf = Surfaces(led, clock=lambda: fake[0])

    # ---- positive: register a LOCAL and a CLOUD surface, plus a never-measured mirror ----
    sf.register("local-v", "LOCAL", "V:\\A\\Ai", "SCRATCH")
    sf.register("odx", "CLOUD", "onedrive://papa@figroots.com", "BACKUP")
    sf.register("itc", "PUBLISH", "https://ai.dchambers.com", "PUBLISH")
    check("register three surfaces -> all in state",
          lambda: set(sf.state()) == {"local-v", "odx", "itc"})

    # attach probes (code, not prose) and measure
    sf.attach_probe("local-v", lambda: (True, 226_000_000_000, "NVMe ADATA SX8200NP"))
    sf.attach_probe("odx", lambda: (True, 900_000_000_000, "OneDrive 1TB, ~10% used"))
    m = sf.measure("local-v")
    check("measure runs the probe and returns reachable + free_bytes",
          lambda: m["reachable"] is True and m["free_bytes"] == 226_000_000_000)
    sf.measure("odx")

    # report shows AGE (advance clock 5s since the measurements)
    fake[0] += 5
    rep = {r["id"]: r for r in sf.report()}
    check("report shows a measured surface with age_s and free_gb",
          lambda: rep["local-v"]["age_s"] == 5 and rep["local-v"]["free_gb"] == 226.0
          and rep["local-v"]["reachable"] is True)
    check("a never-measured surface shows reachable=None (UNKNOWN, never True)",
          lambda: rep["itc"]["reachable"] is None and rep["itc"]["age_s"] is None
          and rep["itc"]["free_gb"] is None)

    # ---- negatives BY KIND ----
    check("duplicate id -> DUPLICATE", expect(SurfaceError, "DUPLICATE")(
        lambda: sf.register("local-v", "LOCAL", "V:\\A", "SCRATCH")))
    check("bad kind -> UNQUALIFIED", expect(SurfaceError, "UNQUALIFIED")(
        lambda: sf.register("bad", "USB", "D:\\", "ARCHIVE")))
    check("bad role -> UNQUALIFIED", expect(SurfaceError, "UNQUALIFIED")(
        lambda: sf.register("bad", "LOCAL", "D:\\", "MIRROR")))
    check("measure unknown surface -> UNKNOWN_SURFACE", expect(SurfaceError, "UNKNOWN_SURFACE")(
        lambda: sf.measure("nope")))
    check("measure with no probe attached -> UNQUALIFIED", expect(SurfaceError, "UNQUALIFIED")(
        lambda: sf.measure("itc")))
    # the no-probe measure must NOT have recorded anything - itc stays never-measured
    check("...and the refused measure recorded nothing (itc still UNKNOWN)",
          lambda: {r["id"]: r for r in sf.report()}["itc"]["reachable"] is None)

    # ---- qualify: THE THREE QUESTIONS, each failing on its own axis ----
    # a reachable but tiny CLOUD surface, for the capacity axis
    sf.register("gdx", "CLOUD", "gdrive://BTS_SGH_Handoff", "BACKUP")
    sf.attach_probe("gdx", lambda: (True, 1_000_000, "Drive nearly full"))
    sf.measure("gdx")

    # (3) mesh-addressability: a LOCAL surface with plenty of space still FAILS off-machine
    q_local = sf.qualify_backup_target("local-v", min_free_bytes=1_000_000_000)
    check("LOCAL surface FAILS mesh-addressability (off-machine or it does not count)",
          lambda: q_local["qualified"] is False
          and any("mesh-addressability" in r for r in q_local["reasons"]))

    # (2) capacity: a reachable CLOUD surface that is too small FAILS capacity
    q_gdx = sf.qualify_backup_target("gdx", min_free_bytes=50_000_000_000)
    check("small-capacity CLOUD surface FAILS capacity",
          lambda: q_gdx["qualified"] is False
          and any("capacity" in r for r in q_gdx["reasons"]))

    # (1) reachability: a never-measured surface FAILS reachability
    q_itc = sf.qualify_backup_target("itc", min_free_bytes=1)
    check("never-measured surface FAILS reachability",
          lambda: q_itc["qualified"] is False
          and any("reachability" in r for r in q_itc["reasons"]))

    # positive: a reachable, large-enough, off-machine CLOUD surface QUALIFIES
    q_odx = sf.qualify_backup_target("odx", min_free_bytes=50_000_000_000)
    check("reachable large-enough CLOUD surface QUALIFIES (no reasons)",
          lambda: q_odx["qualified"] is True and q_odx["reasons"] == [])

    # stale: advance the injected clock past the window; the same surface now FAILS reachability
    fake[0] += 90_000
    q_stale = sf.qualify_backup_target("odx", min_free_bytes=50_000_000_000)
    check("stale measurement FAILS reachability (age advanced past the window)",
          lambda: q_stale["qualified"] is False
          and any("reachability" in r for r in q_stale["reasons"]))

    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for label, ok, err in RESULTS:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label, ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (surfaces measured not assumed; three questions each fail "
          "on their own axis; off-machine is structural)" % ("PASS" if not bad else "FAIL", len(RESULTS)))
    return 0 if not bad else 1


def test_surfaces():
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())