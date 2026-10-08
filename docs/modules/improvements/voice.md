# Voice improvements

Base: `V:\A\Ai\COSMOS` main `501fdee2`. Package `voice\` already passes 4C.
These are reviewable diffs. They are not applied. Voice refine stays TABLED.
No new door, no socket in tests, no key printed.

`plan_pull`, `ConfirmGate`, and `ControlView` match the contract. Left alone.

## 1. `voice/cosmos_voice/transport.py` — a redirect resends the bearer

`CoreClient._guard` refuses a bearer on the URL it is about to call when
that URL is `http`. `UrllibTransport` then calls `urllib.request.urlopen`.
On this machine's CPython 3.14, `HTTPRedirectHandler.redirect_request`
copies every header except `content-length` and `content-type`, and
`http_error_302` allows an `http`, `https`, or `ftp` target. A 302 from
the https Core host therefore sends `Authorization` to the next host,
including a cleartext one. MemoryTransport tests never open that path.

Refuse the redirect. The 3xx comes back through the existing `HTTPError`
arm and is not followed. No new dependency.

```diff
--- a/voice/cosmos_voice/transport.py
+++ b/voice/cosmos_voice/transport.py
@@ -11,6 +11,7 @@ from __future__ import annotations
 import json
 import urllib.error
 import urllib.parse
 import urllib.request
+from email.message import Message
 from collections.abc import Mapping
+from typing import IO, NoReturn, Protocol
-from typing import Protocol
```

Place the new handler after the path constants and before `class Transport`.
Strict mypy is on, and `warn_unused_ignores` is on, so the override is
typed and there is no type-ignore comment.

```diff
--- a/voice/cosmos_voice/transport.py
+++ b/voice/cosmos_voice/transport.py
@@ -28,6 +29,28 @@ _RESUME = "/api/v1/control/resume"
 _LOOP = "/api/v1/voice_loop"
 
 
+class _NoRedirect(urllib.request.HTTPRedirectHandler):
+    """A Location is not a second hop for the bearer.
+
+    The stdlib redirect handler copies Authorization and allows http.
+    A Core call is one URL. A 3xx is the response, not a new request.
+    """
+
+    def redirect_request(
+        self,
+        req: urllib.request.Request,
+        fp: IO[bytes],
+        code: int,
+        msg: str,
+        headers: Message,
+        newurl: str,
+    ) -> NoReturn:
+        raise urllib.error.HTTPError(req.full_url, code, msg, headers, fp)
+
+
+def _opener() -> urllib.request.OpenerDirector:
+    """Opener whose redirect handler is ``_NoRedirect``."""
+    return urllib.request.build_opener(_NoRedirect)
+
+
 class Transport(Protocol):
@@ -76,7 +99,7 @@ class UrllibTransport:
         """Send one request. ``URLError`` and timeouts become UNREACHABLE."""
         req = urllib.request.Request(url, data=body, headers=dict(headers), method=method)
         try:
-            with urllib.request.urlopen(req, timeout=timeout) as response:
+            with _opener().open(req, timeout=timeout) as response:
                 status = int(response.status)
                 raw = response.read()
```

`build_opener` drops the default redirect handler when a subclass is
passed. Ruff isort keeps straight imports (`json`, `urllib`) above
`from` imports, and sorts those as `collections.abc`, `email.message`,
`typing`. Add a test that calls
`_NoRedirect.redirect_request` with a `https` request and an `http`
Location and expects `HTTPError` whose URL is the original one. That
test does not bind a port.

## 2. `voice/cosmos_voice/doors.py` — vendor key rides on any base

`_vendor_turn` puts the key in `Authorization` and posts to `base`.
The default base is `wss://`. A caller can pass `http://` or a
scheme-less string. `CoreClient` would refuse that for its own bearer.
The vendor doors do not. Tests use the default `wss` base, so they keep
posting through `MemoryTransport`.

```diff
--- a/voice/cosmos_voice/doors.py
+++ b/voice/cosmos_voice/doors.py
@@ -6,6 +6,7 @@ A vendor key is sent only as an Authorization header, never in an error detail.
 
 from __future__ import annotations
 
 import json
+import urllib.parse
 from typing import cast
@@ -82,6 +83,14 @@ def _mapped(body: dict[str, object], brain: str) -> dict[str, object]:
     return mapped
 
 
+def _secret_url(base: str) -> None:
+    """A vendor key is not sent on cleartext or on a URL with no scheme."""
+    scheme = urllib.parse.urlsplit(base).scheme.lower()
+    if scheme not in {"https", "wss"}:
+        raise VoiceError("BEARER_OVER_HTTP", "refused on cleartext http")
+
+
 def _vendor_turn(
@@ -99,6 +108,7 @@ def _vendor_turn(
     """
     if not api_key.strip():
         raise VoiceError("NO_KEY")
+    _secret_url(base)
     if transport is None:
         raise VoiceError("NOT_COMPOSED")
```

`test_doors.py` forbids `urlopen` and `import socket` in this module.
`urllib.parse` is neither. Empty key still raises `NO_KEY` before the
scheme check.

## 3. `voice/cosmos_voice/desktop.py` — confirm sees the wake word, not the phrase

`once` decides the mode, then runs `reject_phrase` / `accept_phrase` on
the raw line, then posts `decision.transcript`. In wake mode that
transcript has `hey cosmos` removed. `hey cosmos yes` therefore does not
match `yes`, the stored confirm id is not attached, and the mouth still
receives `yes`. `hey cosmos no` does not clear the pending id. The
contract order is mode decision, then the confirm phrase. The fakes in
`test_desktop.py` ignore the words, so those tests stay green.

```diff
--- a/voice/cosmos_voice/desktop.py
+++ b/voice/cosmos_voice/desktop.py
@@ -143,10 +143,13 @@ class DesktopLoop:
         decision = self._modes.accept(heard, held=held, tapped=tapped, mode=mode, now=now)
         if not decision.accepted:
             return self._stop(decision.kind)
-        if self._confirm.reject_phrase(heard):
+        phrase = decision.transcript
+        if self._confirm.reject_phrase(phrase):
             return self._stop("cancelled", ok=True, spoken="Cancelled.")
-        confirm_id = self._confirm.accept_phrase(heard) or ""
-        body = self._mouth.speak_turn(decision.transcript, self._session, confirm_id=confirm_id)
+        confirm_id = self._confirm.accept_phrase(phrase) or ""
+        body = self._mouth.speak_turn(phrase, self._session, confirm_id=confirm_id)
         self._session.note_reply(body)
         self._confirm.observe(body)
```
