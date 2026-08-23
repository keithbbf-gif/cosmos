#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: cosmos_segments - SEGMENTS + CAS over the existing Ledger (finding M9).
Same check()/expect() shape as test_core.py. Forces 3+ rotations; proves global seqs are
continuous across segment boundaries while local seqs reset; proves the anchor chain;
plants a corrupt MIDDLE segment and a corrupt anchor and shows verify_all REFUSES naming
the culprit and RECORDS a LEDGER_INCIDENT; round-trips CAS, proves idempotence, catches a
tampered blob as HASH_MISMATCH, and runs CAS past MAX_PATH via extended()."""
from __future__ import annotations
import hashlib, json, os, shutil, sys, tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cosmos_ledger import Ledger, LedgerError
from cosmos_paths import extended
from cosmos_segments import SegmentedLedger, CAS

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

def refusal(f):
    """Run f(); return the LedgerError it raised (or None). Lets a check inspect BOTH the
    kind AND the message (verify_all must NAME the culprit segment/anchor)."""
    try:
        f()
    except LedgerError as e:
        return e
    return None

def _anchors_chain(ldir: Path) -> bool:
    prev = ""
    for n in sorted(int(p.stem.split("-")[1]) for p in ldir.glob("seg-*.jsonl")):
        ap = ldir / ("seg-%05d.anchor.json" % n)
        if not ap.exists():
            continue                       # the live (unsealed) head has no anchor
        raw = ap.read_bytes()
        if json.loads(raw.decode("utf-8"))["prev_anchor_sha256"] != prev:
            return False
        prev = hashlib.sha256(raw).hexdigest()
    return True

def _each_segment_self_contained(ldir: Path, key: bytes) -> bool:
    """Every segment file passes the ORDINARY Ledger.verify() on its own, with a local
    seq counting from 1 - the proof this is a LAYER, not a rewrite."""
    for p in sorted(ldir.glob("seg-*.jsonl")):
        recs = list(Ledger(p, key, "F5").verify())
        if recs and recs[0]["seq"] != 1:
            return False
    return True


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="cosmos_seg_"))
    KEY = b"spike-install-key"

    # ================= SEGMENTS: build + rotate =================
    ldir = td / "ledger"
    sl = SegmentedLedger(ldir, KEY, "F5", max_records=5)
    N = 17                                  # 5+5+5 sealed, 2 live -> 3 rotations
    appended = [sl.append("PING", {"n": i}) for i in range(N)]

    check("3+ rotations produced 4 segments on disk", lambda: sl.segments() == [1, 2, 3, 4])
    check("3 segments sealed with an anchor (the live head has none)",
          lambda: sum(1 for n in sl.segments()
                      if (ldir / ("seg-%05d.anchor.json" % n)).exists()) == 3)
    check("append returned continuous global_seq 1..N as it wrote",
          lambda: [r["global_seq"] for r in appended] == list(range(1, N + 1)))

    check("verify_all passes over the whole multi-segment history",
          lambda: len(list(sl.verify_all())) == N)
    check("global seqs are continuous 1..N ACROSS segment boundaries",
          lambda: [r["global_seq"] for r in sl.verify_all()] == list(range(1, N + 1)))
    check("local seq RESETS per segment while global does not (layer, not rewrite)",
          lambda: _each_segment_self_contained(ldir, KEY))
    check("anchors form their own hash chain (prev_anchor_sha256 links each)",
          lambda: _anchors_chain(ldir))
    check("anchor seq accounting matches the records (first/last/count)",
          lambda: json.loads((ldir / "seg-00002.anchor.json").read_text())["first_seq"] == 6
                  and json.loads((ldir / "seg-00002.anchor.json").read_text())["last_seq"] == 10
                  and json.loads((ldir / "seg-00002.anchor.json").read_text())["record_count"] == 5)

    # ================= corrupt a MIDDLE segment's BYTES =================
    d2 = td / "corrupt_seg"; shutil.copytree(ldir, d2)
    seg2 = d2 / "seg-00002.jsonl"
    lines = seg2.read_text(encoding="utf-8").splitlines()
    tam = json.loads(lines[1]); tam["payload"]["n"] = 999      # bytes/hash now disagree
    lines[1] = json.dumps(tam, sort_keys=True, separators=(",", ":"))
    seg2.write_text("\n".join(lines) + "\n", encoding="utf-8")
    sl2 = SegmentedLedger(d2, KEY, "F5", max_records=5)
    e_seg = refusal(lambda: list(sl2.verify_all()))
    check("corrupt MIDDLE segment -> verify_all REFUSES (BROKEN_CHAIN) naming seg-00002",
          lambda: e_seg is not None and e_seg.kind == "BROKEN_CHAIN" and "seg-00002" in str(e_seg))
    check("the corrupt segment recorded a LEDGER_INCIDENT",
          lambda: any(r["event"] == "LEDGER_INCIDENT" and r["payload"]["segment"] == 2
                      for r in sl2.incidents()))

    # ================= corrupt an ANCHOR =================
    d3 = td / "corrupt_anchor"; shutil.copytree(ldir, d3)
    a2 = d3 / "seg-00002.anchor.json"
    anc = json.loads(a2.read_text(encoding="utf-8"))
    anc["segment_sha256"] = "0" * 64                            # lie about the sealed bytes
    a2.write_text(json.dumps(anc, sort_keys=True, separators=(",", ":")), encoding="utf-8")
    sl3 = SegmentedLedger(d3, KEY, "F5", max_records=5)
    e_anc = refusal(lambda: list(sl3.verify_all()))
    check("corrupt ANCHOR -> verify_all REFUSES (BROKEN_CHAIN) naming seg-00002.anchor",
          lambda: e_anc is not None and e_anc.kind == "BROKEN_CHAIN"
                  and "seg-00002.anchor" in str(e_anc))
    check("the corrupt anchor recorded a LEDGER_INCIDENT",
          lambda: any(r["event"] == "LEDGER_INCIDENT" and r["payload"]["segment"] == 2
                      for r in sl3.incidents()))

    # ================= CAS =================
    cas = CAS(td / "cas")
    blob = b"a large artifact that belongs in the CAS, not inline in the ledger " * 500
    sha = cas.put(blob)
    check("CAS.put returns the sha256 of the content",
          lambda: sha == hashlib.sha256(blob).hexdigest())
    check("CAS.get round-trips the exact bytes", lambda: cas.get(sha) == blob)
    sha_again = cas.put(blob)
    check("CAS is idempotent: identical content -> identical sha", lambda: sha_again == sha)
    check("CAS idempotent: identical content is ONE blob file on disk",
          lambda: sum(1 for p in (td / "cas").iterdir() if p.suffix == ".blob") == 1)

    ptr = sl.append("ARTIFACT", {"cas": sha, "bytes": len(blob)})
    check("a large artifact goes in CAS; the LEDGER holds only the sha pointer",
          lambda: ptr["payload"] == {"cas": sha, "bytes": len(blob)}
                  and cas.get(ptr["payload"]["cas"]) == blob)

    bp = td / "cas" / (sha + ".blob")
    raw = bp.read_bytes(); bp.write_bytes(raw[:-1] + bytes([raw[-1] ^ 0xFF]))   # flip a bit
    check("a tampered CAS blob -> HASH_MISMATCH on read (never handed back)",
          expect(LedgerError, "HASH_MISMATCH")(lambda: cas.get(sha)))
    check("an ABSENT CAS blob -> NOT_FOUND, not UNREADABLE (four-state rule)",
          expect(LedgerError, "NOT_FOUND")(lambda: cas.get("f" * 64)))

    # ================= CAS past MAX_PATH =================
    deep = td
    for _ in range(8):
        deep = deep / ("d" * 40)
    os.makedirs(extended(deep), exist_ok=True)
    check("the deep CAS root exceeds MAX_PATH (>260 chars)",
          lambda: len(str(deep / "cas")) > 260)
    cas_deep = CAS(deep / "cas")
    dsha = cas_deep.put(b"deep blob beyond 260 chars")
    check("CAS put/get works past MAX_PATH via extended()",
          lambda: cas_deep.get(dsha) == b"deep blob beyond 260 chars")

    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for label, ok, err in RESULTS:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label, ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (3+ rotations, anchor chain, 2 planted corruptions BY "
          "KIND naming the culprit + incidents, CAS round-trip/idempotence/HASH_MISMATCH, "
          "MAX_PATH)" % ("PASS" if not bad else "FAIL", len(RESULTS)))
    return 0 if not bad else 1


def test_segments():
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())
