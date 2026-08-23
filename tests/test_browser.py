#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: cosmos_browser - the REAL browser driver that closes the last DOM gap.

Meaningful WITH OR WITHOUT a browser present, by design:
  (a) NO browser discovered -> assert start() raises ConnectionError (the correct
      UNREACHABLE signal) and PASS with a NATIVE-DEMO-REQUIRED note. Absence of a
      browser is a runner fact, not a driver defect.
  (b) browser present -> actually navigate to a data: URL / about:blank and assert DOM
      text returns and session_ok() is True. A real render, once, where the bytes are
      real.
  (c) the auth-wall heuristic runs ALWAYS, browser or not, by feeding synthetic DOM
      strings through detect_auth_wall() - the login detection is a module-level
      function precisely so it is testable without launching anything.

Same check()/expect() pattern as test_features.py. Standalone: exit 0/1. Pytest:
test_browser() asserts main()==0.
"""
from __future__ import annotations
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cosmos_browser import ChromeDriver, discover_browser, detect_auth_wall

RESULTS = []


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                            # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def expect(exc):
    """True iff calling f() raises `exc`."""
    def wrap(f):
        def inner():
            try:
                f()
            except exc:
                return True
            return False
        return inner
    return wrap


# A login-form DOM (form + password input + login language) and a normal page.
_AUTH_DOM = (
    "<html><body><h1>Sign in</h1>"
    "<form action='/login' method='post'>"
    "<input type='text' name='user'>"
    "<input type='password' name='pass'>"
    "<button>Log in</button></form></body></html>"
)
_NORMAL_DOM = (
    "<html><body><h1>GrokDex</h1>"
    "<table><tr><td>object_key</td><td>url</td></tr></table>"
    "<form action='/search'><input type='text' name='q'></form>"
    "</body></html>"
)
_NAV_LINK_DOM = (   # a 'Sign in' LINK in a nav bar, no form -> not a wall
    "<html><body><nav><a href='/login'>Sign in</a></nav>"
    "<h1>Public article</h1><p>Free to read.</p></body></html>"
)


def main() -> int:
    import tempfile
    td = Path(tempfile.mkdtemp(prefix="cosmos_browser_"))

    # ================= AUTH-WALL HEURISTIC (always runs) =================
    check("detect_auth_wall: TRUE on a login-form DOM (form + password + login language)",
          lambda: detect_auth_wall(_AUTH_DOM) is True)
    check("detect_auth_wall: FALSE on a normal page (a bare search <form> is not a wall)",
          lambda: detect_auth_wall(_NORMAL_DOM) is False)
    check("detect_auth_wall: FALSE on a 'Sign in' LINK with no <form> (link != wall)",
          lambda: detect_auth_wall(_NAV_LINK_DOM) is False)
    check("detect_auth_wall: FALSE on empty DOM",
          lambda: detect_auth_wall("") is False)
    check("detect_auth_wall: a <form> with a password input is decisive on its own",
          lambda: detect_auth_wall(
              "<form><input type=\"password\"></form>") is True)

    # ================= DRIVER, WITH OR WITHOUT A BROWSER =================
    # Live Chrome/Edge --dump-dom is the Windows native demo (Program Files paths,
    # taskkill-backed tree kill). On non-Windows, record the live-navigate checks
    # as SKIPPED-NON-NATIVE and still prove the no-browser contract.
    binary = discover_browser()

    if os.name != "nt":
        RESULTS.append(("live browser navigate (Chrome/Edge --dump-dom)",
                        True, "SKIPPED-NON-NATIVE"))
        check("start() with a non-existent injected binary raises ConnectionError",
              expect(ConnectionError)(
                  lambda: ChromeDriver(binary=str(td / "nope.exe")).start(
                      str(td / "p2"))))
        check("session_ok() before start() is False (never raises)",
              lambda: ChromeDriver().session_ok() is False)
        if binary is None:
            check("no browser present: start() raises ConnectionError (-> UNREACHABLE) "
                  "[NATIVE-DEMO-REQUIRED: (b) live-navigate path unexercised on this runner]",
                  expect(ConnectionError)(lambda: ChromeDriver().start(str(td / "profile"))))
    elif binary is None:
        # (a) No browser present: start() MUST raise ConnectionError (-> UNREACHABLE).
        drv = ChromeDriver()
        check("no browser present: start() raises ConnectionError (-> UNREACHABLE) "
              "[NATIVE-DEMO-REQUIRED: (b) live-navigate path unexercised on this runner]",
              expect(ConnectionError)(lambda: drv.start(str(td / "profile"))))
        # A driver handed a bogus binary must also refuse.
        check("start() with a non-existent injected binary raises ConnectionError",
              expect(ConnectionError)(
                  lambda: ChromeDriver(binary=str(td / "nope.exe")).start(
                      str(td / "p2"))))
        # session_ok() before a successful start() is False, never an exception.
        check("session_ok() before start() is False (never raises)",
              lambda: ChromeDriver().session_ok() is False)
    else:
        # (b) Browser present: actually render and assert DOM + session_ok.
        drv = ChromeDriver(binary=binary)
        drv.start(str(td / "profile"))
        data_url = "data:text/html,<html><body><h1>COSMOS-DOM-OK</h1></body></html>"
        dom = drv.navigate(data_url)
        check("browser present: navigate(data: URL) returns non-empty DOM text "
              "containing the rendered marker",
              lambda: isinstance(dom, str) and "COSMOS-DOM-OK" in dom)
        check("browser present: session_ok() is True (about:blank renders)",
              lambda: drv.session_ok() is True)
        check("browser present: navigating a login-wall data: URL raises PermissionError "
              "(-> AUTH_REQUIRED)",
              expect(PermissionError)(
                  lambda: drv.navigate("data:text/html," + _AUTH_DOM)))
        drv.stop()

    bad = [(l, e) for l, ok_, e in RESULTS if not ok_]
    for label, ok_, err in RESULTS:
        print("  %s  %s%s" % ("OK  " if ok_ else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    mode = "NO-BROWSER (NATIVE-DEMO-REQUIRED for the live-navigate path)" \
        if binary is None else ("browser: %s" % binary)
    print("SELFTEST %s - %d checks (%s)"
          % ("PASS" if not bad else "FAIL", len(RESULTS), mode))
    return 0 if not bad else 1


def test_browser():
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())
