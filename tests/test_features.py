#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: cosmos_platform + cosmos_validate + cosmos_dom + cosmos_identity.
Platform owns encoding/quoting/paths (scar R9); validate is the declared-vs-consumed
gate wired into acceptance (R1/R4, S-55); DOM failures are TYPED and every one is
ledgered (never a silent fallback); identity is asked FROM THE FUNCTION, never quoted
from prose (the four-blockers-for-eleven-days scar)."""
from __future__ import annotations
import sys, tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cosmos_paths import extended
from cosmos_platform import (PlatformError, run, run_tree_killed, write_text_lf,
                             write_text_crlf, makedirs)
from cosmos_validate import (ValidateError, read_verified, write_declared,
                             ReturnValidator)
from cosmos_dom import DomWorker
from cosmos_identity import MESH_ID, PEERS, federation_ready, federation_blockers
from cosmos_ledger import Ledger

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


class FakeDriver:
    """Implements the Driver protocol; configurable to fail on demand - which no real
    browser can be asked to do. mode in {ok, no_start, auth, broke}; session_valid
    drives the preflight."""

    def __init__(self):
        self.mode = "ok"
        self.session_valid = True
        self.profiles = []                 # every profile dir start() was handed

    def start(self, profile_dir: str) -> None:
        self.profiles.append(profile_dir)  # recorded BEFORE any refusal
        if self.mode == "no_start":
            raise ConnectionError("chrome/transport did not launch")

    def navigate(self, url: str) -> str:
        if self.mode == "auth":
            raise PermissionError("login wall - auth is Keith's click")
        if self.mode == "broke":
            raise RuntimeError("mid-action explosion")
        return "PAGE TEXT for " + url

    def session_ok(self) -> bool:
        return self.session_valid

    def stop(self) -> None:
        pass


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="cosmos_ft_"))
    KEY = b"k"
    E_ACUTE = "é"
    CHECKMARK = "✓"

    # ================= PLATFORM =================
    r = run(["py", "-3.14", "-c", "print('unicode: \\u00e9\\u2713')"])
    check("subprocess UTF-8 on BOTH ends: e-acute and checkmark survive capture",
          lambda: r["rc"] == 0 and E_ACUTE in r["out"] and CHECKMARK in r["out"])

    check("run() with a STRING command -> SHELL_REFUSED (argv lists only)",
          expect(PlatformError, "SHELL_REFUSED")(lambda: run("echo hazard % ! ^")))

    rk = run_tree_killed(["py", "-3.14", "-c", "import time; time.sleep(30)"],
                         timeout_s=2)
    check("run_tree_killed on timeout: timed_out True AND kill outcome REPORTED",
          lambda: rk["timed_out"] is True and rk["kill_result"] is not None)

    lf = td / "endings_lf.txt"
    write_text_lf(lf, "line1\nline2\n")
    lf_bytes = lf.read_bytes()
    check("write_text_lf: bytes carry \\n and NO \\r\\n (S-59: caller says the endings)",
          lambda: b"\n" in lf_bytes and b"\r\n" not in lf_bytes)

    crlf = td / "endings_crlf.txt"
    write_text_crlf(crlf, "line1\nline2\n")
    check("write_text_crlf: bytes carry \\r\\n",
          lambda: b"\r\n" in crlf.read_bytes())

    deep = td / ("a" * 80) / ("b" * 80) / ("c" * 80) / ("d" * 80)
    makedirs(deep)
    check("makedirs on a >300-char path succeeds (MAX_PATH bites at CREATION)",
          lambda: len(str(deep)) > 300 and Path(extended(deep)).is_dir())

    # ================= VALIDATE =================
    content = b"declared bytes, consumed bytes, and they must AGREE\n"
    decl = write_declared(td / "declared.bin", content)
    check("write_declared -> read_verified round-trips against its declaration",
          lambda: read_verified(td / "declared.bin", expect_len=decl["len"],
                                expect_sha=decl["sha"]) == content)

    check("wrong declared length -> SHORT_READ (the mount's signature)",
          expect(ValidateError, "SHORT_READ")(
              lambda: read_verified(td / "declared.bin",
                                    expect_len=decl["len"] + 1)))

    check("wrong declared sha -> HASH_MISMATCH",
          expect(ValidateError, "HASH_MISMATCH")(
              lambda: read_verified(td / "declared.bin", expect_sha="0" * 64)))

    vled = Ledger(td / "validate.jsonl", KEY, "F5")
    rv = ReturnValidator(vled)
    real_file = td / "really_here.txt"
    real_file.write_text("present on disk", encoding="utf-8")
    check("path_exists PASSES for a file that is on disk",
          lambda: rv.accept("r-ok",
                            [{"validator": "path_exists",
                              "path": str(real_file)}])["checks"][0]["ok"])

    check("path_exists on a missing file REFUSES the whole return",
          expect(ValidateError, "FAILED_VALIDATION")(
              lambda: rv.accept("r-missing",
                                [{"validator": "path_exists",
                                  "path": str(td / "never_written.txt")}])))

    check("...and the refusal is LEDGERED (RETURN_REFUSED event present)",
          lambda: any(rec["event"] == "RETURN_REFUSED"
                      and rec["payload"].get("rid") == "r-missing"
                      for rec in vled.verify()))

    doi_ok = rv.accept("r-doi", [{"validator": "doi_shape",
                                  "doi": "10.1103/PhysRevB.13.492"}])
    check("doi_shape passes a real-shaped DOI, detail says UNPROVEN (shape is not "
          "existence - Crossref is the authority)",
          lambda: doi_ok["checks"][0]["ok"]
          and "UNPROVEN" in doi_ok["checks"][0]["detail"])

    check("doi_shape FAILS 'not-a-doi' (shape failure is a certain fabrication signal)",
          expect(ValidateError, "FAILED_VALIDATION")(
              lambda: rv.accept("r-doi-bad", [{"validator": "doi_shape",
                                              "doi": "not-a-doi"}])))

    source = td / "source.txt"
    source.write_text("The measured edge width is 424 meV, not 96 meV.\n",
                      encoding="utf-8")
    check("quote_in_source: an exact quotation is found verbatim",
          lambda: rv.accept("r-quote",
                            [{"validator": "quote_in_source",
                              "source_path": str(source),
                              "quote": "The measured edge width is 424 meV"}])
          ["checks"][0]["ok"])

    check("quote_in_source: a FABRICATED quotation is refused (S-55 control)",
          expect(ValidateError, "FAILED_VALIDATION")(
              lambda: rv.accept("r-fab",
                                [{"validator": "quote_in_source",
                                  "source_path": str(source),
                                  "quote": "The edge width is exactly 96 meV as "
                                           "predicted"}])))

    check("unknown validator name -> NO_VALIDATOR (never silently skipped)",
          expect(ValidateError, "NO_VALIDATOR")(
              lambda: rv.accept("r-novalid", [{"validator": "vibes_check"}])))

    # ================= DOM =================
    dled = Ledger(td / "dom.jsonl", KEY, "F5")
    drv = FakeDriver()
    worker = DomWorker(dled, td / "dom_work", "W1", drv)

    def dom_failed_ledgered(kind):
        return any(rec["event"] == "DOM_ATTEMPT_FAILED"
                   and rec["payload"].get("kind") == kind
                   for rec in dled.verify())

    ok = worker.run_attempt("job-ok", "https://ai.dchambers.com/GrokDex.csv")
    check("OK path: evidence file written and holds the page text",
          lambda: ok["ok"] and ok["kind"] == "OK"
          and Path(ok["evidence"]).read_text(encoding="utf-8") == ok["text"])
    check("OK path ledgers DOM_ATTEMPT_OK",
          lambda: any(rec["event"] == "DOM_ATTEMPT_OK"
                      and rec["payload"].get("job_id") == "job-ok"
                      for rec in dled.verify()))

    drv.mode = "no_start"
    r_un = worker.run_attempt("job-un", "https://example.com")
    check("driver raising on start -> UNREACHABLE, and it is ledgered",
          lambda: r_un["kind"] == "UNREACHABLE"
          and dom_failed_ledgered("UNREACHABLE"))

    drv.mode = "ok"
    drv.session_valid = False
    r_se = worker.run_attempt("job-se", "https://example.com", require_session=True)
    check("stale session with require_session -> SESSION_EXPIRED, ledgered",
          lambda: r_se["kind"] == "SESSION_EXPIRED"
          and dom_failed_ledgered("SESSION_EXPIRED"))

    drv.session_valid = True
    drv.mode = "auth"
    r_au = worker.run_attempt("job-au", "https://example.com")
    check("navigate raising PermissionError -> AUTH_REQUIRED, ledgered",
          lambda: r_au["kind"] == "AUTH_REQUIRED"
          and dom_failed_ledgered("AUTH_REQUIRED"))

    drv.mode = "broke"
    r_br = worker.run_attempt("job-br", "https://example.com")
    check("navigate raising mid-action -> BROKE (report-never-retry), ledgered",
          lambda: r_br["kind"] == "BROKE" and dom_failed_ledgered("BROKE"))

    check("every attempt used a DIFFERENT profile dir (ephemeral per attempt)",
          lambda: len(drv.profiles) == 5
          and len(set(drv.profiles)) == len(drv.profiles))

    # ================= IDENTITY =================
    check("federation_ready() is False - never reported working while blockers stand",
          lambda: federation_ready() is False)
    check("federation blockers == 5, counted FROM THE FUNCTION, not from prose",
          lambda: len(federation_blockers()) == 5)
    check("MESH_ID is KMesh", lambda: MESH_ID == "KMesh")
    check("no peer ID starts with G (GMesh UNASSIGNED - Keith assigns, nobody guesses)",
          lambda: not any(k.startswith("G") for k in PEERS))

    bad = [(l, e) for l, ok_, e in RESULTS if not ok_]
    for label, ok_, err in RESULTS:
        print("  %s  %s%s" % ("OK  " if ok_ else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (platform owns the shell; validation is a gate; "
          "DOM failures are typed and ledgered; identity is asked, not quoted)"
          % ("PASS" if not bad else "FAIL", len(RESULTS)))
    return 0 if not bad else 1


def test_features():
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())
