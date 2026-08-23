#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_browser - A REAL browser driver for the DOM rail (F5 builder, 6b work).

Closes the last DOM gap: cosmos_dom owns the PROTOCOL and the typed-failure mapping,
FakeDriver proves every failure path, and until now the only thing missing was a driver
that talks to an actual browser. This is it.

  🔴 HONEST SCOPE - THIS IS A BEST-EFFORT DOM-READ DRIVER, NOT FULL CDP AUTOMATION.
  It drives headless Chrome/Edge with `--headless=new --dump-dom <url>`, which asks the
  browser to render the page and print the resulting DOM to stdout, then hands that text
  back. That is a READ. It cannot fill a form, click a button, solve MFA, or complete an
  OAuth consent - and it is not meant to. Interactive automation is a later CDP upgrade
  (a real DevTools websocket client). When that lands it plugs in behind the SAME
  Driver protocol, so DomRail / DomWorker do not change - the upgrade is drop-in.

WHY dump-dom and not a websocket CDP client here: the house rule is stdlib-only, and a
full CDP client is a heavy dependency (websocket framing, target discovery, an event
loop). `--dump-dom` gets rendered DOM text through the ONE process door (cosmos_platform
.run / .run_tree_killed - argv list, no shell, UTF-8 both ends, whole-tree kill on
timeout) with nothing but the standard library. It buys the READ that the rail needs now
and defers the INTERACT that it does not yet need.

Failure mapping (so DomWorker types it correctly):
  * binary not found / process failed / empty DOM after a real attempt -> ConnectionError
    -> DomWorker maps to UNREACHABLE.
  * rendered DOM looks like a login wall (detect_auth_wall) -> PermissionError
    -> DomWorker maps to AUTH_REQUIRED. AUTH is Keith's click, never automated.
"""
from __future__ import annotations

import os
import re
import shutil
from pathlib import Path

from cosmos_platform import run, run_tree_killed


# ---------------------------------------------------------------------------
# Binary discovery
# ---------------------------------------------------------------------------
# Common Windows install locations for Chrome and Edge, plus PATH names. Order is a
# preference: Chrome first (the DOM rail's primary target), Edge as the always-present
# Windows fallback. PATH is checked for both under every plausible executable name.
_WIN_CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]
# PATH executable names (Windows and POSIX), Chrome-family before Edge.
_PATH_NAMES = [
    "chrome", "chrome.exe",
    "google-chrome", "google-chrome-stable", "chromium", "chromium-browser",
    "msedge", "msedge.exe", "microsoft-edge",
]


def discover_browser() -> str | None:
    """Return the path to a Chromium-family browser binary, or None if none is found.
    Checks common Windows install paths first, then PATH. Pure lookup - launches
    nothing."""
    for cand in _WIN_CANDIDATES:
        try:
            if cand and Path(cand).is_file():
                return cand
        except OSError:
            continue
    for name in _PATH_NAMES:
        found = shutil.which(name)
        if found:
            return found
    return None


# ---------------------------------------------------------------------------
# Auth-wall heuristic (factored out so it is testable WITHOUT a browser)
# ---------------------------------------------------------------------------
_AUTH_PHRASES = ("sign in", "log in", "login", "password", "sign-in", "log-in")


def detect_auth_wall(dom_text: str) -> bool:
    """Best-effort login-wall heuristic on rendered DOM text.

    TRUE when the DOM both (a) contains a <form> element AND (b) mentions a sign-in /
    log-in / password phrase. Requiring BOTH is deliberate: a page that merely links to
    a login page (a 'Sign in' link in a nav bar) is not itself an auth wall, and a bare
    <form> (a search box) is not either. The pair - a form plus login language - is the
    cheap, high-precision signal that navigation landed on a credential prompt, which is
    Keith's click and never Cowork's. It is a heuristic, not a proof; the honest name for
    what it does is 'looks like a login wall.'"""
    if not dom_text:
        return False
    low = dom_text.lower()
    has_form = "<form" in low
    if not has_form:
        return False
    # A password input is by itself decisive; otherwise require a login phrase.
    if re.search(r'<input[^>]*type\s*=\s*["\']?password', low):
        return True
    return any(p in low for p in _AUTH_PHRASES)


# ---------------------------------------------------------------------------
# The driver
# ---------------------------------------------------------------------------
class ChromeDriver:
    """A REAL Driver implementation (start/navigate/session_ok/stop) backed by headless
    Chrome/Edge --dump-dom. Best-effort DOM READ only - see the module docstring.

    The profile dir is ephemeral and attempt-private: DomWorker creates a fresh one per
    attempt and passes it to start(); this driver records it and hands it to the browser
    as --user-data-dir. stop() NEVER deletes it - staging the profile is the worker's
    job (report-never-retry: a profile may hold evidence of what happened)."""

    def __init__(self, binary: str | None = None, timeout_s: float = 60):
        # Discovery is deferred to start() unless a binary is injected, so constructing a
        # driver never touches the filesystem and tests can build one freely.
        self._binary = binary
        self._timeout_s = timeout_s
        self._profile_dir: str | None = None

    # -- protocol ----------------------------------------------------------
    def start(self, profile_dir: str) -> None:
        """Record the ephemeral profile dir and verify a browser binary exists.
        Raises ConnectionError (-> UNREACHABLE) if no browser can be found or the
        recorded binary is missing - there is nothing to drive."""
        self._profile_dir = profile_dir
        if self._binary is None:
            self._binary = discover_browser()
        if not self._binary or not Path(self._binary).is_file():
            raise ConnectionError(
                "no Chrome/Edge binary found (checked Program Files, LOCALAPPDATA and "
                "PATH) - nothing to drive")

    def navigate(self, url: str) -> str:
        """Fetch rendered DOM for `url` via headless --dump-dom. Returns the DOM text.

        Raises:
          ConnectionError (-> UNREACHABLE) - browser not started, process failed
            (nonzero rc / timeout), or empty DOM after a real attempt.
          PermissionError (-> AUTH_REQUIRED) - the DOM looks like a login wall.
        """
        if not self._binary or self._profile_dir is None:
            raise ConnectionError("navigate() before a successful start()")
        argv = [
            self._binary,
            "--headless=new",
            "--disable-gpu",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-extensions",
            f"--user-data-dir={self._profile_dir}",
            "--dump-dom",
            url,
        ]
        res = run_tree_killed(argv, timeout_s=self._timeout_s)
        if res["timed_out"]:
            raise ConnectionError(
                f"browser timed out after {self._timeout_s}s on {url} "
                f"({res.get('kill_result')})")
        if res["rc"] not in (0, None):
            err = (res["err"] or res["out"] or "").strip()[:200]
            raise ConnectionError(
                f"browser exited rc={res['rc']} on {url}: {err}")
        dom = res["out"] or ""
        if not dom.strip():
            # A real attempt that returns nothing is UNREACHABLE, not OK-with-empty.
            raise ConnectionError(f"empty DOM returned for {url} (rc={res['rc']})")
        if detect_auth_wall(dom):
            raise PermissionError(
                f"navigation landed on a login wall for {url} - AUTH is Keith's click, "
                f"never automated")
        return dom

    def session_ok(self) -> bool:
        """Cheap preflight: can the browser render a trivial page. Navigates to
        about:blank and treats a non-empty (or cleanly-returned) render as OK. Any
        failure -> False, which DomWorker turns into SESSION_EXPIRED at the preflight
        gate. This checks that the DRIVER is live, not that a remote login is valid -
        real session validation is a CDP-era upgrade."""
        if not self._binary or self._profile_dir is None:
            return False
        argv = [
            self._binary,
            "--headless=new",
            "--disable-gpu",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-extensions",
            f"--user-data-dir={self._profile_dir}",
            "--dump-dom",
            "about:blank",
        ]
        try:
            res = run(argv, timeout_s=min(self._timeout_s, 30))
        except Exception:                                             # noqa: BLE001
            return False
        return (not res["timed_out"]) and res["rc"] in (0, None)

    def stop(self) -> None:
        """Best-effort teardown. The ephemeral profile is LEFT ON DISK for the worker to
        stage - never deleted here (report-never-retry; the profile may be evidence).
        --dump-dom exits on its own, so there is no long-lived process to reap; this is
        a no-op today and the hook for a future CDP session close."""
        return None