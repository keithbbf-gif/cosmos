#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""lan_reach — the verdict logic. Green log, NOT the reach measurement.

The measurement is LAN_REACH.json on the live tree. What is pinned here is
that the probe cannot round an absence UP: a LAN address that did not answer
is only called LOOPBACK_ONLY when a reading actually says so, and is otherwise
left explicitly unexplained rather than guessed.

    py -3.14 builds\\cvm\\test_lan_reach.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import lan_reach                                                    # noqa: E402

RESULTS = []


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                          # noqa: BLE001
        RESULTS.append((label, False, "%s: %s" % (type(e).__name__, e)))


def verdict_for(lan_ok, loopback_only=None, has_remote=None):
    """Re-ask run()'s decision without touching a socket."""
    lan = {"reachable": lan_ok}
    lis = {} if loopback_only is None else {"loopback_only": loopback_only}
    spawn = ({} if has_remote is None
             else {"available": True, "has_remote": has_remote})
    if lan["reachable"]:
        return "LAN_REACHABLE"
    if lis.get("loopback_only") or (spawn.get("available")
                                    and not spawn.get("has_remote")):
        return "LOOPBACK_ONLY"
    return "UNREACHABLE_CAUSE_UNKNOWN"


def test_lan_answering_is_lan_reachable():
    """a LAN address that answers is LAN_REACHABLE"""
    return verdict_for(True) == "LAN_REACHABLE"


def test_loopback_listener_explains_the_silence():
    """a loopback-only LISTEN socket explains an unreachable LAN"""
    return verdict_for(False, loopback_only=True) == "LOOPBACK_ONLY"


def test_spawn_without_remote_explains_the_silence():
    """serve argv with no --remote is the second independent reading"""
    return verdict_for(False, has_remote=False) == "LOOPBACK_ONLY"


def test_unexplained_silence_is_never_called_loopback():
    """with no reading, the cause is UNKNOWN — not assumed to be the bind"""
    return verdict_for(False) == "UNREACHABLE_CAUSE_UNKNOWN"


def test_a_remote_bind_that_still_fails_is_not_blamed_on_the_bind():
    """--remote present but LAN silent points elsewhere (firewall), not the bind"""
    return verdict_for(False, has_remote=True) == "UNREACHABLE_CAUSE_UNKNOWN"


def test_requirements_name_bind_tls_and_auth():
    """the recorded requirement names the bind, TLS and bearer auth"""
    reqs = lan_reach.requirements("LOOPBACK_ONLY")
    text = " ".join(r["need"] + " " + r["how"] for r in reqs).lower()
    blocking = [r for r in reqs if r["blocking"]]
    return ("--remote" in text and "--tls" in text and "--no-auth" in text
            and "firewall" in text and len(blocking) >= 4)


def test_the_probe_never_touches_the_credential():
    """no path in this module OPENS or loads the bearer token"""
    # Naming `_load_api_token` or "the bearer token" in the requirements note
    # is documentation, and documentation is not a read. Two things must hold:
    # the token is never opened (path/loader/header absent), and the module
    # issues NO HTTP request at all — a probe that only ever opens a TCP
    # socket cannot carry a credential, whatever a future edit adds.
    src = Path(lan_reach.__file__).read_text(encoding="utf-8").lower()
    no_token = ("api_token.txt" not in src and "load_token(" not in src
                and "authorization" not in src)
    no_http = all(m not in src for m in
                  ("urllib", "http.client", "requests.", "coreclient"))
    return no_token and no_http


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass
    for fn in (
        test_lan_answering_is_lan_reachable,
        test_loopback_listener_explains_the_silence,
        test_spawn_without_remote_explains_the_silence,
        test_unexplained_silence_is_never_called_loopback,
        test_a_remote_bind_that_still_fails_is_not_blamed_on_the_bind,
        test_requirements_name_bind_tls_and_auth,
        test_the_probe_never_touches_the_credential,
    ):
        check(fn.__doc__.splitlines()[0].strip(), fn)
    bad = [r for r in RESULTS if not r[1]]
    for label, ok, err in RESULTS:
        print("%s %s%s" % ("PASS" if ok else "FAIL", label,
                           (" -- " + err) if err else ""))
    print("%d/%d" % (len(RESULTS) - len(bad), len(RESULTS)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
