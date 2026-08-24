#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: kdash_mobile.html — the PHONE-FIRST client of the COSMOS v1 API.
The page is inspected as HTML on disk (same style as test_kdash_create.py):
POSITIVE controls on the contract (viewport meta, the three endpoints, a
feature-detected SpeechRecognition mic, Bearer auth, visible command results)
and NEGATIVE controls on the same axes (a planted CDN script is caught, a
planted localStorage-token write is caught, no destructive verbs, no remote
src/href). The page is a pure CONSUMER of cosmos_service.py — this test never
touches the service or kdash_index.html."""
from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
def _find_mobile():
    # portable across layouts: SPIKE flat (beside test), repo (tests/ -> ../kdash/mobile.html)
    for c in (HERE / "kdash_mobile.html",
              HERE.parent / "kdash" / "mobile.html",
              HERE / "kdash" / "mobile.html",
              HERE.parent / "kdash_mobile.html"):
        if c.is_file():
            return c
    return HERE / "kdash_mobile.html"   # last resort -> reports missing clearly
MOBILE = _find_mobile()


def _find_shell(name: str):
    """Same layout resolution for the PWA shell files (manifest, SW):
    kdash/<name> in the repo layout, kdash_<name> flat in the SPIKE."""
    for c in (HERE / "kdash" / name,
              HERE.parent / "kdash" / name,
              HERE / ("kdash_" + name)):
        if c.is_file():
            return c
    return HERE / ("kdash_" + name)     # last resort -> reports missing clearly
MANIFEST = _find_shell("manifest.webmanifest")
SW = _find_shell("sw.js")

RESULTS = []


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                            # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


class MobileError(RuntimeError):
    """kind in {BAD_PAGE, CDN_FORBIDDEN, TOKEN_PERSISTED, DESTRUCTIVE_VERB}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


# Any src/href/url(...) pointing at a remote host is an external dependency —
# the page must survive CSP and an offline phone. (The API base the USER types
# into an input at runtime is not a page dependency.)
_REMOTE_REF = re.compile(
    r"""(?:src|href)\s*=\s*["']\s*(?:https?:)?//|url\(\s*["']?https?://""",
    re.IGNORECASE)


def inspect_mobile(html: str) -> dict:
    """The page contract, enforced. Raises MobileError; returns measured facts."""
    if not html or "<html" not in html.lower():
        raise MobileError("BAD_PAGE", "not an HTML document")
    if _REMOTE_REF.search(html) or "cdn." in html.lower() or "@import" in html:
        raise MobileError("CDN_FORBIDDEN",
                          "remote script/style/font reference — the page must be "
                          "self-contained (CSP + offline phone)")
    # the token must never touch persistent browser storage. Match USAGE
    # (localStorage.setItem / localStorage["x"]) — the page's own comment is
    # allowed to NAME the API while documenting why it is not used.
    for pat, name in ((r"\blocalStorage\s*[.\[]", "localStorage"),
                      (r"\bsessionStorage\s*[.\[]", "sessionStorage"),
                      (r"\bdocument\.cookie\b", "document.cookie")):
        if re.search(pat, html):
            raise MobileError("TOKEN_PERSISTED",
                              f"{name} usage present — the bearer token (or "
                              f"anything else) must not persist on the handset")
    # a phone dashboard has no business carrying destructive verbs
    for verb in ('"DELETE"', "'DELETE'", '"PUT"', "'PUT'"):
        if re.search(r"method\s*:\s*" + re.escape(verb), html):
            raise MobileError("DESTRUCTIVE_VERB",
                              f"HTTP method {verb} found — v1 mobile is "
                              f"GET + POST /command only")
    return {
        "viewport": bool(re.search(
            r'<meta\s+name=["\']viewport["\']\s+content=["\'][^"\']*'
            r'width=device-width', html)),
        "endpoints": {p: (p in html) for p in
                      ("/api/v1/status", "/api/v1/jobs", "/api/v1/health",
                       "/api/v1/spend", "/api/v1/events?since_seq=",
                       "/api/v1/voice")},
        "bearer": '"Authorization":"Bearer "+cfg.token' in html,
        "sr_detect": ("window.SpeechRecognition || window.webkitSpeechRecognition"
                      in html),
        "sr_graceful": "voice unavailable" in html,
        "shows_result": ("REFUSED" in html and '"OK"' in html
                         and "addConsole" in html),
        "shows_transcript": ("heard" in html and "tap SEND to run" in html),
    }


class SWError(RuntimeError):
    """kind in {API_CACHEABLE, EXTERNAL_URL, BAD_SW}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


# a LITERAL remote URL in the SW or manifest is an external dependency; the
# xmlns inside a fully percent-encoded data: SVG (http%3A%2F%2F...) is not a
# fetchable reference and must NOT trip this.
_LITERAL_URL = re.compile(r"https?://", re.IGNORECASE)


def inspect_sw(js: str) -> dict:
    """The service-worker contract, enforced. The one non-negotiable: /api/ is
    NEVER cached (the frozen-dashboard scar - stale data shown as live)."""
    if not js or "addEventListener" not in js:
        raise SWError("BAD_SW", "not a service worker script")
    if _LITERAL_URL.search(js) or "importScripts" in js:
        raise SWError("EXTERNAL_URL",
                      "remote URL or importScripts in the service worker - the "
                      "shell must be self-contained (CSP + offline phone)")
    # the fetch handler must bail out on /api/ BEFORE any cache logic, and no
    # /api path may appear in the precache allowlist
    if ('indexOf("/api/")' not in js) or ('"/api' in js.replace('("/api/")', "")):
        raise SWError("API_CACHEABLE",
                      "no /api/ exclusion guard (or an /api path in the shell "
                      "list) - a cached /api/v1/* response is frozen data")
    return {
        "shell_only": ('var SHELL = ["/m", "/kdash_manifest.webmanifest", '
                       '"/kdash_sw.js"];' in js),
        "api_guard": 'url.pathname.indexOf("/api/") === 0' in js,
        "non_get_untouched": 'e.request.method !== "GET"' in js,
    }


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
    # ================= POSITIVE: the live page on disk =================
    check("kdash_mobile.html exists in SPIKE_F5_core", lambda: MOBILE.is_file())
    html = MOBILE.read_text(encoding="utf-8")
    info = inspect_mobile(html)

    check("phone viewport meta (width=device-width) present",
          lambda: info["viewport"])
    check("consumes GET /api/v1/status", lambda: info["endpoints"]["/api/v1/status"])
    check("consumes GET /api/v1/jobs", lambda: info["endpoints"]["/api/v1/jobs"])
    check("consumes GET /api/v1/health", lambda: info["endpoints"]["/api/v1/health"])
    check("consumes GET /api/v1/spend", lambda: info["endpoints"]["/api/v1/spend"])
    check("polls GET /api/v1/events?since_seq= (append-only cursor)",
          lambda: info["endpoints"]["/api/v1/events?since_seq="])
    check("POSTs to /api/v1/voice (the session-continuous voice seam)",
          lambda: info["endpoints"]["/api/v1/voice"]
          and 'apiPost("/api/v1/voice", body)' in html)
    check("every request carries Authorization: Bearer <token>",
          lambda: info["bearer"])
    check("mic is feature-detected (SpeechRecognition || webkitSpeechRecognition)",
          lambda: info["sr_detect"])
    check("no-SR browsers get a graceful 'voice unavailable', not an error",
          lambda: info["sr_graceful"])
    check("command results are SHOWN (OK / REFUSED via addConsole) — no silent action",
          lambda: info["shows_result"])
    check("voice transcript is echoed and staged, never auto-executed",
          lambda: info["shows_transcript"]
          and "rec.onresult" in html
          and "runCommand" not in html.split("rec.onresult")[1].split("};")[0])
    check("token is an in-memory JS variable, documented as such",
          lambda: "cfg = { base:\"\", token:\"\" }" in html
          and "NEVER written to localStorage" in html)
    check("same dark theme family as kdash_index (--bg token, mono stack)",
          lambda: "--bg:#0b0e12" in html and "--mono" in html)
    check("one-column phone layout (max-width capped, no fixed wide widths)",
          lambda: "max-width:560px" in html and "overflow-x:hidden" in html)
    check("touch targets are >= 48px (inputs and buttons)",
          lambda: "min-height:48px" in html and "min-width:48px" in html)
    check("big mic button is the primary input (>=96px circle)",
          lambda: re.search(r"#btnMic\{width:1\d\dpx;height:1\d\dpx", html))

    # ================= NEGATIVE CONTROLS =================
    check("page as-shipped passes inspect (no CDN, no persisted token, no DELETE)",
          lambda: inspect_mobile(html) is not None)
    check("NO external script/link/src to a remote host anywhere",
          lambda: not _REMOTE_REF.search(html) and "<script src=" not in html
          and "cdn." not in html.lower())
    check("NO localStorage / sessionStorage / cookie token storage",
          lambda: not re.search(r"\blocalStorage\s*[.\[]", html)
          and not re.search(r"\bsessionStorage\s*[.\[]", html)
          and "document.cookie" not in html)
    check("NO destructive endpoint call (no DELETE/PUT; only POST is /voice)",
          lambda: not re.search(r"method\s*:\s*['\"](DELETE|PUT)['\"]", html)
          and re.findall(r'apiPost\("(/api/v1/[^"]*)"', html)
          == ["/api/v1/voice"])

    # planted page defects (the real file is never rewritten)
    planted_cdn = html.replace(
        "</head>", '<script src="https://cdn.jsdelivr.net/npm/x"></script></head>')
    check("planted CDN script -> CDN_FORBIDDEN",
          expect(MobileError, "CDN_FORBIDDEN")(lambda: inspect_mobile(planted_cdn)))
    planted_store = html.replace(
        "</script>", 'localStorage.setItem("token", cfg.token);</script>')
    check("planted localStorage token write -> TOKEN_PERSISTED",
          expect(MobileError, "TOKEN_PERSISTED")(
              lambda: inspect_mobile(planted_store)))
    planted_delete = html.replace(
        'method:(opts && opts.method)||"GET"', 'method:"DELETE"')
    check("planted DELETE verb -> DESTRUCTIVE_VERB",
          expect(MobileError, "DESTRUCTIVE_VERB")(
              lambda: inspect_mobile(planted_delete)))
    check("empty string -> BAD_PAGE",
          expect(MobileError, "BAD_PAGE")(lambda: inspect_mobile("")))

    # ================= PWA: MANIFEST + SERVICE WORKER LINKAGE =================
    check("page links the manifest (/kdash_manifest.webmanifest)",
          lambda: '<link rel="manifest" href="/kdash_manifest.webmanifest">'
          in html)
    check("page carries theme-color meta matching the dark theme (#0b0e12)",
          lambda: '<meta name="theme-color" content="#0b0e12">' in html)
    check("page registers /kdash_sw.js, feature-detected, never page-breaking",
          lambda: '"serviceWorker" in navigator' in html
          and 'navigator.serviceWorker.register("/kdash_sw.js")' in html
          and ".catch(function(){" in html.split("serviceWorker.register")[1])

    import json as _json
    check("kdash_manifest.webmanifest exists beside the page",
          lambda: MANIFEST.is_file())
    man_text = MANIFEST.read_text(encoding="utf-8")
    man = _json.loads(man_text)
    check("manifest: name/short_name COSMOS, start_url /m, display standalone",
          lambda: man["name"] == "COSMOS" and man["short_name"] == "COSMOS"
          and man["start_url"] == "/m" and man["display"] == "standalone")
    check("manifest: theme/background colors are the dark theme (#0b0e12)",
          lambda: man["theme_color"] == "#0b0e12"
          and man["background_color"] == "#0b0e12")
    check("manifest: 192 + 512 icons, every src an inline data: URI",
          lambda: {"192x192", "512x512"} <= {i["sizes"] for i in man["icons"]}
          and all(i["src"].startswith("data:image/") for i in man["icons"]))
    check("manifest: NO literal external URL anywhere (data: URIs only)",
          lambda: not _LITERAL_URL.search(man_text))

    check("kdash_sw.js exists beside the page", lambda: SW.is_file())
    sw_js = SW.read_text(encoding="utf-8")
    sw = inspect_sw(sw_js)
    check("SW: fetch handler bails on /api/ BEFORE any cache logic "
          "(data is never cached - the frozen-dashboard scar)",
          lambda: sw["api_guard"]
          and sw_js.index('indexOf("/api/")') < sw_js.index("caches.match"))
    check("SW: precache list is the shell ONLY (page, manifest, worker - no /api)",
          lambda: sw["shell_only"])
    check("SW: non-GET requests (POST /command) are never intercepted",
          lambda: sw["non_get_untouched"])
    check("SW: NO external URL, NO importScripts (self-contained)",
          lambda: not _LITERAL_URL.search(sw_js) and "importScripts" not in sw_js)

    # planted SW defects (the real file is never rewritten)
    no_guard = sw_js.replace('if (url.pathname.indexOf("/api/") === 0) {', "if (false) {")
    check("planted removal of the /api/ guard -> API_CACHEABLE",
          expect(SWError, "API_CACHEABLE")(lambda: inspect_sw(no_guard)))
    api_in_shell = sw_js.replace('"/kdash_sw.js"]', '"/kdash_sw.js", "/api/v1/status"]')
    check("planted /api path in the precache shell list -> API_CACHEABLE",
          expect(SWError, "API_CACHEABLE")(lambda: inspect_sw(api_in_shell)))
    ext_sw = sw_js.replace('"use strict";',
                           '"use strict";\nimportScripts("https://cdn.evil/x.js");')
    check("planted importScripts/CDN in the SW -> EXTERNAL_URL",
          expect(SWError, "EXTERNAL_URL")(lambda: inspect_sw(ext_sw)))
    check("empty SW -> BAD_SW",
          expect(SWError, "BAD_SW")(lambda: inspect_sw("")))

    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for label, ok, err in RESULTS:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (kdash_mobile: phone-first voice client of "
          "/api/v1; Bearer in memory only; no CDNs; results always shown; "
          "installable PWA shell, SW never caches /api)"
          % ("PASS" if not bad else "FAIL", len(RESULTS)))
    return 0 if not bad else 1


def test_kdash_mobile():
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())
