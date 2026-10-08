"""HTTP seam between the voice client and Core.

``CoreClient`` is the only caller of a transport. Construction does not open
a socket. A bearer is attached only on a call, and never on cleartext HTTP
unless the caller opts in.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Mapping
from email.message import Message
from typing import IO, NoReturn, Protocol

from cosmos_voice.errors import VoiceError
from cosmos_voice.redact import redact, secret_shape
from cosmos_voice.types import FAST_TIMEOUT_S, VOICE_READ_TIMEOUT_S, HttpResponse

_STATUS = "/api/v1/status"
_CONTROL = "/api/v1/control"
_VOICE = "/api/v1/voice"
_PULL = "/api/v1/cvm/pull"
_SNAPSHOT = "/api/v1/cvm/snapshot"
_PUSH = "/api/v1/cvm/push"
_KILL = "/api/v1/kill"
_RESUME = "/api/v1/control/resume"
_LOOP = "/api/v1/voice_loop"


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """A Location is not a second hop for the bearer.

    The stdlib redirect handler copies Authorization and allows http.
    A Core call is one URL. A 3xx is the response, not a new request.
    """

    def redirect_request(
        self,
        req: urllib.request.Request,
        fp: IO[bytes],
        code: int,
        msg: str,
        headers: Message,
        newurl: str,
    ) -> NoReturn:
        raise urllib.error.HTTPError(req.full_url, code, msg, headers, fp)


def _opener() -> urllib.request.OpenerDirector:
    """Opener whose redirect handler is ``_NoRedirect``."""
    return urllib.request.build_opener(_NoRedirect)


class Transport(Protocol):
    """One HTTP exchange. A script or urllib may sit behind this."""

    def request(
        self,
        method: str,
        url: str,
        headers: Mapping[str, str],
        body: bytes | None,
        timeout: float,
    ) -> HttpResponse:
        """Perform one request and return the status plus a JSON object."""


def _json_object(raw: bytes) -> dict[str, object]:
    if not raw.strip():
        return {}
    try:
        parsed: object = json.loads(raw)
    except ValueError:
        return {}
    if not isinstance(parsed, dict):
        return {}
    found: dict[str, object] = {}
    for key, value in parsed.items():
        if isinstance(key, str):
            found[key] = value
    return found


class UrllibTransport:
    """HTTP via ``urllib.request``. Network failures are UNREACHABLE.

    The bearer is a request header only. It is not written into the refusal.
    """

    def request(
        self,
        method: str,
        url: str,
        headers: Mapping[str, str],
        body: bytes | None,
        timeout: float,
    ) -> HttpResponse:
        """Send one request. ``URLError`` and timeouts become UNREACHABLE."""
        req = urllib.request.Request(url, data=body, headers=dict(headers), method=method)
        try:
            with _opener().open(req, timeout=timeout) as response:
                status = int(response.status)
                raw = response.read()
        except urllib.error.HTTPError as exc:
            # HTTPError is a URLError. It must be read as a response, not a dead peer.
            status = int(exc.code)
            try:
                raw = exc.read()
            except OSError:
                raw = b""
            finally:
                exc.close()
        except (urllib.error.URLError, TimeoutError, OSError):
            raise VoiceError("UNREACHABLE", redact("request failed")) from None
        return HttpResponse(status=status, body=_json_object(raw))


class MemoryTransport:
    """Replay a script. No socket.

    Each row is ``(method, path_suffix, status, body)``. A call pops the first
    row whose method matches and whose path suffix is contained in the URL.
    ``calls`` records ``(method, url, headers, body, timeout)`` in order.
    """

    def __init__(
        self,
        script: list[tuple[str, str, int, dict[str, object]]],
    ) -> None:
        """Copy ``script``. Later calls pop rows from this copy."""
        self.script = list(script)
        self.calls: list[tuple[str, str, dict[str, str], bytes | None, float]] = []

    def request(
        self,
        method: str,
        url: str,
        headers: Mapping[str, str],
        body: bytes | None,
        timeout: float,
    ) -> HttpResponse:
        """Pop the first matching script row, or raise NOT_COMPOSED."""
        self.calls.append((method, url, dict(headers), body, timeout))
        wanted = method.upper()
        for index, (row_method, suffix, status, payload) in enumerate(self.script):
            if row_method.upper() == wanted and suffix in url:
                self.script.pop(index)
                return HttpResponse(status=status, body=dict(payload))
        raise VoiceError("NOT_COMPOSED", redact("no scripted response"))


class CoreClient:
    """Client of the live Core voice seam.

    A blank bearer is allowed on http and https. A non-blank bearer on http
    raises BEARER_OVER_HTTP unless ``allow_bearer_over_http`` is set.
    ``post_voice`` waits ``voice_timeout`` seconds. Every other verb uses
    ``timeout``. The default transport is built on the first call, not here.
    """

    def __init__(
        self,
        base: str,
        bearer: str = "",
        *,
        allow_bearer_over_http: bool = False,
        transport: Transport | None = None,
        timeout: float = FAST_TIMEOUT_S,
        voice_timeout: float = VOICE_READ_TIMEOUT_S,
    ) -> None:
        """Store the base URL and bearer. This does not open a socket."""
        self._base = base
        self._bearer = bearer.strip()
        self._allow_bearer_over_http = allow_bearer_over_http
        self._transport = transport
        self._timeout = timeout
        self._voice_timeout = voice_timeout

    def request(
        self,
        method: str,
        path: str,
        body: Mapping[str, object] | None = None,
        *,
        timeout: float | None = None,
        query: Mapping[str, str] | None = None,
    ) -> dict[str, object]:
        """Perform one Core call and return the JSON object.

        401 raises UNAUTHORIZED. Any other non-2xx uses ``body["error"]`` when
        that value is a safe string, otherwise BAD_REQUEST. The refusal detail
        is redacted and does not contain the bearer.
        """
        url = self._url(path, query)
        self._guard(url)
        payload = _encode(body)
        headers: dict[str, str] = {"Accept": "application/json"}
        if payload is not None:
            headers["Content-Type"] = "application/json"
        if self._bearer:
            headers["Authorization"] = f"Bearer {self._bearer}"
        waited = self._timeout if timeout is None else timeout
        response = self._live().request(method.upper(), url, headers, payload, waited)
        if 200 <= response.status <= 299:
            return response.body
        raise self._http_error(response.status, response.body)

    def get_status(self) -> dict[str, object]:
        """GET /api/v1/status."""
        return self.request("GET", _STATUS)

    def get_control(self, client_id: str) -> dict[str, object]:
        """GET /api/v1/control for one handset."""
        return self.request("GET", _CONTROL, query={"client_id": client_id})

    def post_voice(self, body: Mapping[str, object]) -> dict[str, object]:
        """POST /api/v1/voice using the voice read timeout."""
        return self.request("POST", _VOICE, body, timeout=self._voice_timeout)

    def get_pull(self, client_id: str) -> dict[str, object]:
        """GET /api/v1/cvm/pull for one handset."""
        return self.request("GET", _PULL, query={"client_id": client_id})

    def post_snapshot(self, body: Mapping[str, object]) -> dict[str, object]:
        """POST /api/v1/cvm/snapshot."""
        return self.request("POST", _SNAPSHOT, body)

    def post_push(self, body: Mapping[str, object]) -> dict[str, object]:
        """POST /api/v1/cvm/push."""
        return self.request("POST", _PUSH, body)

    def post_kill(self, client_id: str, token: str = "") -> dict[str, object]:
        """POST /api/v1/kill. ``token`` is the kill token, not the bearer."""
        payload: dict[str, object] = {"client_id": client_id, "token": token}
        return self.request("POST", _KILL, payload)

    def post_resume(self, client_id: str) -> dict[str, object]:
        """POST /api/v1/control/resume for one handset."""
        payload: dict[str, object] = {"client_id": client_id}
        return self.request("POST", _RESUME, payload)

    def post_voice_loop(self, body: Mapping[str, object]) -> dict[str, object]:
        """POST /api/v1/voice_loop. This files a drop and does not run an agent."""
        return self.request("POST", _LOOP, body)

    def _url(self, path: str, query: Mapping[str, str] | None) -> str:
        suffix = path if path.startswith("/") else f"/{path}"
        url = f"{self._base.rstrip('/')}{suffix}"
        if not query:
            return url
        return f"{url}?{urllib.parse.urlencode(query)}"

    def _guard(self, url: str) -> None:
        if not self._bearer:
            return
        scheme = urllib.parse.urlsplit(url).scheme.lower()
        if scheme == "http" and not self._allow_bearer_over_http:
            raise VoiceError("BEARER_OVER_HTTP", redact("refused on cleartext http"))

    def _live(self) -> Transport:
        if self._transport is None:
            self._transport = UrllibTransport()
        return self._transport

    def _safe(self, detail: str) -> str:
        cleaned = detail
        if self._bearer:
            cleaned = cleaned.replace(self._bearer, "[REDACTED]")
        return redact(cleaned)

    def _http_error(self, status: int, body: Mapping[str, object]) -> VoiceError:
        if status == 401:
            kind = "UNAUTHORIZED"
        else:
            raw = body.get("error")
            kind = "BAD_REQUEST"
            if isinstance(raw, str) and raw != "" and not self._unsafe_kind(raw):
                kind = raw
        raw_detail = body.get("detail")
        if isinstance(raw_detail, str) and raw_detail != "":
            detail = raw_detail
        else:
            detail = f"http {status}"
        return VoiceError(kind, self._safe(detail))

    def _unsafe_kind(self, kind: str) -> bool:
        if self._bearer and self._bearer in kind:
            return True
        return secret_shape(kind)


def _encode(body: Mapping[str, object] | None) -> bytes | None:
    if body is None:
        return None
    try:
        return json.dumps(body).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise VoiceError("BAD_REQUEST", redact(type(exc).__name__)) from None
