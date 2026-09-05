#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gate for `cvm_runtimes.py` — the inventory must be able to say NO.

An inventory that only ever reports presence is a press release. Every check
here is paired: the wheel matcher must REJECT a Linux wheel and a freethreaded
ABI as firmly as it accepts this interpreter's own; the isolated probe must NOT
see the vendored VOSK that the vendor-path probe DOES see, in the same run, on
the same interpreter — that difference is the whole basis for reporting
`installed` and `vendored_only` as separate facts.

The network half is driven by a FAKE fetcher with a recorded PyPI shape, so the
closure logic is tested without asking whether pypi.org is up, and one live
check confirms the real fetcher still parses what pypi.org actually returns.

    py -3.14 builds\\cvm-dt\\test_cvm_runtimes.py
    py -3.14 builds\\cvm-dt\\test_cvm_runtimes.py --no-net
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
import time
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

import cvm_runtimes as R  # noqa: E402

RESULTS: list[tuple[str, bool, str]] = []
LIVE: dict = {}


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                        # noqa: BLE001
        RESULTS.append((label, False, "%s: %s" % (type(e).__name__, e)))


# --------------------------------------------------------------------------
# a recorded PyPI shape — enough structure to exercise the closure, no network
# --------------------------------------------------------------------------

def _rel(fn, size, when="2026-01-01T00:00:00.000000Z", kind="bdist_wheel"):
    return {"filename": fn, "size": size, "packagetype": kind,
            "upload_time_iso_8601": when}


FAKE = {
    "alpha": {
        "info": {"version": "2.0",
                 "requires_dist": ["beta>=1", "gamma; extra == 'dev'",
                                   "delta; sys_platform == 'linux'",
                                   "epsilon; python_version >= '3.9'"]},
        "releases": {
            "2.0": [_rel("alpha-2.0-cp314-cp314-win_amd64.whl", 1000)],
            "1.0": [_rel("alpha-1.0-cp310-cp310-win_amd64.whl", 900,
                         "2025-01-01T00:00:00.000000Z")],
        },
    },
    "beta": {  # newest release has no usable wheel; an older one does
        "info": {"version": "9.9", "requires_dist": []},
        "releases": {
            "9.9": [_rel("beta-9.9-cp310-cp310-manylinux_2_28_x86_64.whl", 50)],
            "9.0": [_rel("beta-9.0-py3-none-any.whl", 500,
                         "2025-06-01T00:00:00.000000Z")],
        },
    },
    "epsilon": {
        "info": {"version": "1.0", "requires_dist": None},
        "releases": {"1.0": [_rel("epsilon-1.0-py3-none-any.whl", 7)]},
    },
    "sdistonly": {
        "info": {"version": "3.0", "requires_dist": []},
        "releases": {"3.0": [_rel("sdistonly-3.0.tar.gz", 20, kind="sdist")]},
    },
    "loop_a": {"info": {"version": "1.0", "requires_dist": ["loop_b"]},
               "releases": {"1.0": [_rel("loop_a-1.0-py3-none-any.whl", 1)]}},
    "loop_b": {"info": {"version": "1.0", "requires_dist": ["loop_a"]},
               "releases": {"1.0": [_rel("loop_b-1.0-py3-none-any.whl", 1)]}},
}


def fake_fetch(url: str) -> dict:
    name = url.rstrip("/").split("/")[-2]
    key = name.lower().replace("-", "_")
    if key not in FAKE:
        raise LookupError("no such package in the recorded shape: %s" % name)
    return FAKE[key]


TAGS = R.interpreter_tags(major=3, minor=14, platform="win_amd64", gil=True)
FREE = R.interpreter_tags(major=3, minor=14, platform="win_amd64", gil=False)


# --------------------------------------------------------------------------

def _isolated_vs_vendored() -> bool:
    """The two probes must DISAGREE about vosk, or neither means anything."""
    clean = R.probe_interpreter(sys.executable, ["vosk"])
    vend = R.probe_interpreter(sys.executable, ["vosk"],
                               extra_path=[str(R.VENDOR_SITE)])
    LIVE["isolated_vs_vendored"] = {
        "clean_ok": clean.get("ok"), "clean_vosk": clean.get("found"),
        "vendor_ok": vend.get("ok"), "vendor_vosk": vend.get("found"),
        "vendor_site": str(R.VENDOR_SITE),
        "vendor_site_exists": R.VENDOR_SITE.exists(),
    }
    if not (clean.get("ok") and vend.get("ok")):
        return False
    if not R.VENDOR_SITE.exists():
        # Nothing vendored: then BOTH must say absent. A probe that reports a
        # runtime from a directory that does not exist is the failure mode.
        return (clean["found"]["vosk"] is False
                and vend["found"]["vosk"] is False)
    return clean["found"]["vosk"] is False and vend["found"]["vosk"] is True


def _live_pypi_parses() -> bool:
    r = R.package_reach("vosk", TAGS, R._fetch_json)
    LIVE["live_pypi_vosk"] = {"ok": r.get("ok"), "latest": r.get("latest"),
                              "wheel": r.get("wheel")}
    return bool(r.get("ok")) and "win_amd64" in (r["wheel"]["filename"])


def _gpu_named_or_refused() -> bool:
    g = R.gpu()
    LIVE["gpu"] = g
    if g.get("ok"):
        return bool((g["devices"][0].get("name") or "").strip())
    return g.get("kind") in ("NO_NVIDIA_SMI", "SMI_FAILED", "SMI_RC",
                             "SMI_EMPTY")


def _offline_refuses() -> bool:
    rec = R.run(net=False, stacks={"x": {"roots": ("alpha",), "why": "t"}})
    LIVE["offline_verdict"] = rec["reachability"]["x"]["verdict"]
    return (rec["reachability"]["x"]["verdict"] == "NOT_MEASURED_OFFLINE"
            and "total_mb" not in rec["reachability"]["x"])


def _closure_walks_and_skips() -> bool:
    s = R.stack_reach(("alpha",), TAGS, fake_fetch)
    names = sorted(p["name"] for p in s["packages"])
    LIVE["fake_closure"] = {"names": names, "bytes": s["total_bytes"],
                            "verdict": s["verdict"],
                            "cuda_in_closure": s["cuda_in_closure"]}
    # gamma is an extra -> excluded. delta is linux-only -> excluded.
    # epsilon has a python_version marker -> included conservatively.
    return (names == ["alpha", "beta", "epsilon"]
            and s["total_bytes"] == 1000 + 500 + 7
            and s["verdict"] == "REACHABLE"
            and s["cuda_in_closure"] == [])


def _cap_is_reported() -> bool:
    s = R.stack_reach(("loop_a",), TAGS, fake_fetch, max_packages=1)
    return s["truncated"] is True and s["verdict"] == "TRUNCATED"


def _sdist_only_blocks() -> bool:
    s = R.stack_reach(("sdistonly",), TAGS, fake_fetch)
    return (s["verdict"] == "BLOCKED" and s["blocked"] == ["sdistonly"]
            and s["packages"][0]["kind"] == "SDIST_ONLY")


def _unknown_package_is_a_refusal() -> bool:
    r = R.package_reach("no_such_pkg_zzz", TAGS, fake_fetch)
    return r["ok"] is False and r["kind"] == "PYPI_UNREACHABLE"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-net", action="store_true")
    a = ap.parse_args(argv)

    # ---- the matcher accepts ------------------------------------------
    check("matcher_accepts_this_interpreters_own_cp_tag",
          lambda: R.wheel_matches("ctranslate2-4.8.1-cp314-cp314-win_amd64.whl",
                                  TAGS))
    check("matcher_accepts_py3_none_any",
          lambda: R.wheel_matches("faster_whisper-1.2.1-py3-none-any.whl", TAGS))
    check("matcher_accepts_abi3_from_an_older_minor",
          lambda: R.wheel_matches("piper_tts-1.7.0-cp39-abi3-win_amd64.whl",
                                  TAGS))
    check("matcher_accepts_a_dot_expanded_compound_tag",
          lambda: R.wheel_matches("x-1-py2.py3-none-any.whl", TAGS))

    # ---- and the matcher REJECTS --------------------------------------
    check("matcher_REJECTS_a_linux_only_wheel",
          lambda: not R.wheel_matches(
              "torch-2.13.0-cp314-cp314-manylinux_2_28_x86_64.whl", TAGS))
    check("matcher_REJECTS_a_newer_minor_than_this_one",
          lambda: not R.wheel_matches("x-1-cp315-cp315-win_amd64.whl", TAGS))
    check("matcher_REJECTS_an_abi3_from_a_NEWER_minor",
          lambda: not R.wheel_matches("x-1-cp315-abi3-win_amd64.whl", TAGS))
    check("matcher_REJECTS_freethreaded_abi_on_a_gil_build",
          lambda: not R.wheel_matches("x-1-cp314-cp314t-win_amd64.whl", TAGS))
    check("a_freethreaded_build_WOULD_accept_that_same_wheel",
          lambda: R.wheel_matches("x-1-cp314-cp314t-win_amd64.whl", FREE))
    check("matcher_REJECTS_a_non_wheel",
          lambda: not R.wheel_matches("x-1.tar.gz", TAGS))

    # ---- markers -------------------------------------------------------
    check("marker_with_extra_is_excluded",
          lambda: R.marker_admits(" extra == 'dev'")["include"] is False)
    check("linux_only_marker_is_excluded",
          lambda: R.marker_admits(" sys_platform == 'linux'")["include"]
          is False)
    check("win32_marker_is_included",
          lambda: R.marker_admits(" sys_platform == 'win32'")["include"]
          is True)
    check("a_not_windows_marker_is_excluded",
          lambda: R.marker_admits(" platform_system != 'Windows'")["include"]
          is False)
    check("unreadable_marker_is_included_and_FLAGGED",
          lambda: (R.marker_admits(" implementation_name == 'pypy'")["include"]
                   and R.marker_admits(
                       " implementation_name == 'pypy'").get("flagged")))

    # ---- the closure ---------------------------------------------------
    check("closure_walks_deps_skips_extras_and_linux_only",
          _closure_walks_and_skips)
    check("closure_falls_back_to_an_older_release_with_a_usable_wheel",
          lambda: R.package_reach("beta", TAGS, fake_fetch)["wheel"]["version"]
          == "9.0")
    check("closure_cap_is_REPORTED_not_silent", _cap_is_reported)
    check("an_sdist_only_package_BLOCKS_the_stack", _sdist_only_blocks)
    check("an_unfetchable_package_is_a_named_refusal",
          _unknown_package_is_a_refusal)

    # ---- the local probes ----------------------------------------------
    check("isolated_probe_and_vendor_probe_DISAGREE_about_vosk",
          _isolated_vs_vendored)
    check("the_isolated_probe_really_ran_isolated",
          lambda: R.probe_interpreter(sys.executable, ["json"])["isolated"]
          is True)
    check("a_module_that_cannot_exist_is_reported_absent",
          lambda: R.probe_interpreter(
              sys.executable, ["definitely_not_a_module_zzz"]
          )["found"]["definitely_not_a_module_zzz"] is False)
    check("the_probe_reports_the_probed_interpreters_own_version",
          lambda: R.probe_interpreter(sys.executable, [])["ver"]
          == sys.version.split()[0])
    check("interpreters_include_the_running_one",
          lambda: any(Path(i["path"]).resolve() == Path(sys.executable).resolve()
                      for i in R.interpreters()["found"]))
    check("gpu_is_named_by_nvidia_smi_or_refused_by_kind",
          _gpu_named_or_refused)
    check("cuda_TOOLKIT_is_reported_separately_from_the_driver",
          lambda: "toolkit_present" in R.accelerator_libs())

    # ---- offline honesty + artifact ------------------------------------
    check("offline_records_NOT_MEASURED_rather_than_guessing", _offline_refuses)

    def _artifact():
        rec = R.run(net=False, stacks={"x": {"roots": ("alpha",), "why": "t"}})
        with tempfile.TemporaryDirectory() as td:
            p = R.write_artifact(rec, Path(td))
            back = json.loads(p.read_text(encoding="utf-8"))
        LIVE["artifact_emitted"] = back.get("emitted")
        return (back["wire"] == R.WIRE and back["emitted"]
                and "installed=" in back["emitted"])
    check("artifact_round_trips_with_an_emitted_line", _artifact)

    if not a.no_net:
        check("the_REAL_fetcher_still_parses_what_pypi_returns",
              _live_pypi_parses)

    passed = sum(1 for _, ok, _ in RESULTS if ok)
    for label, ok, err in RESULTS:
        print("%s %s%s" % ("PASS" if ok else "FAIL", label,
                           (" - " + err) if err else ""))
    ok_all = passed == len(RESULTS)
    rec = {
        "ok": ok_all, "wire": "cvm-dt-runtimes-gate/1",
        "suite": "test_cvm_runtimes.py",
        "passed": passed, "total": len(RESULTS),
        "gated_at_epoch": time.time(), "python": sys.version.split()[0],
        "live_value": LIVE,
        "emitted": "runtimes-gate:%d/%d:%s" % (
            passed, len(RESULTS),
            (LIVE.get("live_pypi_vosk") or {}).get("wheel", {}).get("filename")
            or "no-net"),
        "results": [{"name": n, "verdict": "PASS" if ok else "FAIL",
                     "detail": e} for n, ok, e in RESULTS],
    }
    (_HERE / "RUNTIMES_TEST.json").write_text(
        json.dumps(rec, indent=1), encoding="utf-8")
    print("%d/%d" % (passed, len(RESULTS)))
    print(rec["emitted"])
    return 0 if ok_all else 1


if __name__ == "__main__":
    raise SystemExit(main())
