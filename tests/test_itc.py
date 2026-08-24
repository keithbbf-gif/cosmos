#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: cosmos_itc - the ITC resource broker.

Every network touch is a FAKE injected fetcher (no real fetch anywhere in this
suite); the ledger is the real cosmos_ledger, so provenance and chain integrity
are proven against the actual authority primitive, not a stub of it."""
from __future__ import annotations

import hashlib
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cosmos_ledger import Ledger                                     # noqa: E402
from cosmos_itc import ITC, ItcError, DEFAULT_INDEX_URL              # noqa: E402

RESULTS = []


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                            # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def expect(label, kind, fn):
    """fn must raise ItcError with .kind == kind - typed, never bare."""
    try:
        fn()
        RESULTS.append((label, False, f"no error raised (wanted {kind})"))
    except ItcError as e:
        RESULTS.append((label, e.kind == kind,
                        "" if e.kind == kind else f"kind {e.kind} != {kind}"))
    except Exception as e:                                            # noqa: BLE001
        RESULTS.append((label, False, f"untyped {type(e).__name__}: {e}"))


# The fake index: the real GrokDex.csv columns, 6 rows, plus an EXTRA column
# (tolerated by contract). Substring targets: 'spectra' in descriptors,
# distinct areas/types for the filters.
FAKE_CSV = (
    "object_key,url,area,type,size_bytes,descriptor,extra\n"
    "UPS_DATA_XY/scan_001.txt,https://ai.dchambers.com/UPS_DATA_XY/scan_001.txt,"
    "physics,txt,10240,UPS spectra raw scan 001,x1\n"
    "UPS_DATA_XY/scan_002.txt,https://ai.dchambers.com/UPS_DATA_XY/scan_002.txt,"
    "physics,txt,10480,UPS spectra raw scan 002,x2\n"
    "figures/fig_4_3.png,https://ai.dchambers.com/figures/fig_4_3.png,"
    "physics,png,204800,Chapter 4 calibration figure,x3\n"
    "OPJ_exports/proj_a.csv,https://ai.dchambers.com/OPJ_exports/proj_a.csv,"
    "physics,csv,51200,Origin export project A spectra,x4\n"
    "Legal/exhibit_09.pdf,https://ai.dchambers.com/Legal/exhibit_09.pdf,"
    "legal,pdf,88064,Exhibit nine UCC bundle,x5\n"
    "00_INDEX/MASTER_FILE_MANIFEST.csv,"
    "https://ai.dchambers.com/00_INDEX/MASTER_FILE_MANIFEST.csv,"
    "index,csv,1848000,master manifest of all objects,x6\n"
)
FAKE_HASH = hashlib.sha256(FAKE_CSV.encode("utf-8")).hexdigest()

BAD_CSV = (  # 'descriptor' column missing -> BAD_INDEX
    "object_key,url,area,type,size_bytes\n"
    "k1,https://x/k1,physics,txt,1\n"
)


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="cosmos_itc_"))
    KEY = b"k"
    clock_now = [1_000_000.0]

    def clock():
        return clock_now[0]

    fetched_urls = []

    def fake_fetch(url):
        fetched_urls.append(url)
        return FAKE_CSV

    # ===== STALE before any refresh: typed, never empty-silent =====
    led = Ledger(td / "itc.jsonl", KEY, "F5")
    itc = ITC(led, fetcher=fake_fetch, clock=clock)
    expect("search BEFORE any refresh -> STALE (typed, not silently empty)",
           "STALE", lambda: itc.search("spectra"))
    expect("get BEFORE any refresh -> STALE too (NOT_FOUND would claim we looked)",
           "STALE", lambda: itc.get("UPS_DATA_XY/scan_001.txt"))

    # ===== refresh via the FAKE fetcher: counts, hash, ledger event =====
    res = itc.refresh()
    check("refresh returns row_count=6 (header excluded, all keyed rows counted)",
          lambda: res["row_count"] == 6)
    check("refresh content_hash == sha256 of the raw CSV text (measured here too)",
          lambda: res["content_hash"] == FAKE_HASH)
    check("refresh fetch_epoch comes from the injected clock",
          lambda: res["fetch_epoch"] == 1_000_000.0)
    check("fetcher was called with the DEFAULT index url (injected, not hardcoded fetch)",
          lambda: fetched_urls == [DEFAULT_INDEX_URL])
    refr = [r for r in led.verify() if r["event"] == "ITC_REFRESHED"]
    check("ITC_REFRESHED is IN THE LEDGER with url+hash+row_count+epoch",
          lambda: len(refr) == 1
          and refr[0]["payload"]["url"] == DEFAULT_INDEX_URL
          and refr[0]["payload"]["content_hash"] == FAKE_HASH
          and refr[0]["payload"]["row_count"] == 6
          and refr[0]["payload"]["fetch_epoch"] == 1_000_000.0)

    # ===== search: substring on object_key AND descriptor, filters, provenance =====
    hits = itc.search("spectra")
    check("search('spectra') finds the 3 descriptor matches",
          lambda: {h["object_key"] for h in hits} == {
              "UPS_DATA_XY/scan_001.txt", "UPS_DATA_XY/scan_002.txt",
              "OPJ_exports/proj_a.csv"})
    check("search matches object_key too (query 'figures' hits the png row)",
          lambda: [h["object_key"] for h in itc.search("figures")]
          == ["figures/fig_4_3.png"])
    check("search is case-insensitive ('SPECTRA' == 'spectra')",
          lambda: len(itc.search("SPECTRA")) == 3)
    check("area filter is exact: spectra+area=physics -> 3, area=legal -> 0",
          lambda: len(itc.search("spectra", area="physics")) == 3
          and len(itc.search("spectra", area="legal")) == 0)
    check("type filter is exact: spectra+type=csv -> only the OPJ export",
          lambda: [h["object_key"] for h in itc.search("spectra", type="csv")]
          == ["OPJ_exports/proj_a.csv"])
    check("limit caps results ('' matches all 6; limit=2 -> 2)",
          lambda: len(itc.search("", limit=2)) == 2)
    check("EVERY hit carries index_hash == this refresh's content_hash (provenance)",
          lambda: all(h["index_hash"] == FAKE_HASH for h in itc.search("", limit=50)))
    check("EVERY itc hit is tagged source='itc'",
          lambda: all(h["source"] == "itc" for h in hits))

    # ===== get: resolve a hit to a fetchable url =====
    row = itc.get("Legal/exhibit_09.pdf")
    check("get(known key) returns the full row incl. url + provenance",
          lambda: row["url"] == "https://ai.dchambers.com/Legal/exhibit_09.pdf"
          and row["area"] == "legal" and row["size_bytes"] == "88064"
          and row["index_hash"] == FAKE_HASH and row["source"] == "itc")
    expect("get(unknown key) -> NOT_FOUND (typed)",
           "NOT_FOUND", lambda: itc.get("no/such/object.bin"))

    # ===== UNREACHABLE: raising fetcher, and NO fabricated ledger event =====
    led2 = Ledger(td / "itc2.jsonl", KEY, "F5")

    def dead_fetch(url):
        raise ConnectionError("simulated network down")

    itc2 = ITC(led2, fetcher=dead_fetch, clock=clock)
    expect("fetcher that raises -> refresh raises UNREACHABLE (never fabricated)",
           "UNREACHABLE", lambda: itc2.refresh())
    check("NO ITC_REFRESHED appended for the failed fetch (ledger stays empty)",
          lambda: sum(1 for _ in led2.verify()) == 0)
    expect("fetcher=None -> UNREACHABLE as well",
           "UNREACHABLE", lambda: ITC(led2, fetcher=None).refresh())
    expect("...and the index is still STALE after the failed refresh",
           "STALE", lambda: itc2.search("anything"))

    # ===== BAD_INDEX: missing required column refuses, and appends nothing =====
    itc3 = ITC(Ledger(td / "itc3.jsonl", KEY, "F5"),
               fetcher=lambda u: BAD_CSV, clock=clock)
    expect("CSV missing 'descriptor' column -> BAD_INDEX (typed)",
           "BAD_INDEX", lambda: itc3.refresh())
    check("BAD_INDEX also appends nothing (parse precedes the ledger append)",
          lambda: sum(1 for _ in itc3._ledger.verify()) == 0)

    # ===== max_age staleness (the optional recency check, as stated) =====
    clock_now[0] = 1_000_000.0 + 7200.0
    check("max_age=86400: a 2h-old index still answers",
          lambda: len(itc.search("spectra", max_age=86400)) == 3)
    expect("max_age=3600: a 2h-old index -> STALE (recency the caller demanded)",
           "STALE", lambda: itc.search("spectra", max_age=3600))

    # ===== local corpus: register, search, source tags distinct =====
    reg = itc.register_corpus([
        r"V:\Research4\Ai\PhD2_DATA_ARCHIVE\00_WORKING\CH4_CALIBRATION_v3.docx",
        "V:/Research4/UPS DATA XY/scan_101.txt",
        r"D:\Research3\Ai\figures\fig_4_3.png",
    ])
    check("register_corpus records 3 paths",
          lambda: reg == {"registered": 3, "corpus_size": 3})
    creg = [r for r in led.verify() if r["event"] == "CORPUS_REGISTERED"]
    check("CORPUS_REGISTERED is in the ledger with the 3 normalized paths",
          lambda: len(creg) == 1 and creg[0]["payload"]["count"] == 3
          and all("\\" not in p for p in creg[0]["payload"]["paths"]))
    chits = itc.search_corpus("scan_101")
    check("search_corpus finds by path substring (filename included)",
          lambda: len(chits) == 1 and chits[0]["name"] == "scan_101.txt")
    check("search_corpus is case-insensitive and matches mid-path ('research4')",
          lambda: len(itc.search_corpus("research4")) == 2)
    check("corpus hits tagged source='corpus'; itc hits 'itc' - always tellable apart",
          lambda: all(h["source"] == "corpus" for h in chits)
          and itc.search("figures")[0]["source"] == "itc"
          and itc.search_corpus("figures")[0]["source"] == "corpus")
    check("re-registering the same path never deletes and never duplicates",
          lambda: itc.register_corpus(
              ["V:/Research4/UPS DATA XY/scan_101.txt"])["corpus_size"] == 3)

    # ===== state()/report(): the projection is rebuilt FROM THE LEDGER =====
    clock_now[0] = 1_000_000.0 + 9000.0
    res2 = itc.refresh()                       # second refresh, same content
    st = itc.state()
    check("state() shows the LAST refresh (hash, rows, epoch) from ledger replay",
          lambda: st["last_refresh"]["content_hash"] == FAKE_HASH
          and st["last_refresh"]["row_count"] == 6
          and st["last_refresh"]["fetch_epoch"] == res2["fetch_epoch"]
          and st["refresh_count"] == 2 and st["corpus_size"] == 3)
    check("a FRESH ITC on the same ledger rebuilds the same state (projection, "
          "not memory)",
          lambda: ITC(led, fetcher=None).state() == st)
    check("report() names the hash prefix, row count and corpus size",
          lambda: FAKE_HASH[:12] in itc.report() and "6 rows" in itc.report()
          and "corpus=3" in itc.report())

    # ===== the chain itself =====
    check("ledger .verify() passes over the whole session's chain",
          lambda: [r["seq"] for r in led.verify()]
          == list(range(1, sum(1 for _ in led.verify()) + 1)))

    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for label, ok, err in RESULTS:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (itc broker: provenance measured, errors typed, "
          "fetcher injected)" % ("PASS" if not bad else "FAIL", len(RESULTS)))
    return 0 if not bad else 1


def test_itc():
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())
