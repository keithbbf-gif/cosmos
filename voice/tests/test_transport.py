"""CoreClient against a scripted transport. These tests open no socket."""

from __future__ import annotations

import inspect
import io
import json
import urllib.error
import urllib.request
from collections.abc import Callable
from email.message import Message
from typing import cast

from cosmos_voice.errors import VoiceError
from cosmos_voice.transport import (
    CoreClient,
    MemoryTransport,
    UrllibTransport,
    _NoRedirect,
    _opener,
)


def _raised(action: Callable[[], object]) -> VoiceError | None:
    try:
        action()
    except VoiceError as exc:
        return exc
    return None


def test_bearer_over_http_is_refused() -> None:
    secret = "xai-livekeyvalue"
    transport = MemoryTransport([("GET", "/api/v1/status", 200, {"ok": True})])
    client = CoreClient("http://core.example", secret, transport=transport)
    caught = _raised(client.get_status)
    refused = caught is not None and caught.kind == "BEARER_OVER_HTTP"
    leaked = caught is not None and secret in str(caught)
    assert refused is True
    assert leaked is False
    assert transport.calls == []


def test_blank_bearer_is_allowed_on_http() -> None:
    transport = MemoryTransport([("GET", "/api/v1/status", 200, {"ok": True})])
    client = CoreClient("http://core.example", "", transport=transport)
    assert client.get_status() == {"ok": True}
    headers = transport.calls[0][2]
    assert ("Authorization" in headers) is False


def test_https_bearer_is_sent_without_printing_it() -> None:
    secret = "xai-livekeyvalue"
    transport = MemoryTransport([("GET", "/api/v1/status", 200, {"ok": True})])
    client = CoreClient("https://core.example", secret, transport=transport)
    assert client.get_status() == {"ok": True}
    _method, url, headers, _body, _timeout = transport.calls[0]
    saw = headers.get("Authorization") == f"Bearer {secret}"
    leaked = secret in url
    assert saw is True
    assert leaked is False


def test_allow_bearer_over_http() -> None:
    secret = "xai-livekeyvalue"
    transport = MemoryTransport([("GET", "/api/v1/status", 200, {"ok": True})])
    client = CoreClient(
        "http://core.example",
        secret,
        allow_bearer_over_http=True,
        transport=transport,
    )
    assert client.get_status() == {"ok": True}
    saw = transport.calls[0][2].get("Authorization") == f"Bearer {secret}"
    assert saw is True


def test_unauthorized() -> None:
    transport = MemoryTransport(
        [("GET", "/api/v1/status", 401, {"error": "NOPE", "detail": "no"})]
    )
    client = CoreClient("https://core.example", transport=transport)
    caught = _raised(client.get_status)
    assert caught is not None
    assert caught.kind == "UNAUTHORIZED"
    assert caught.detail == "no"


def test_error_string_or_bad_request() -> None:
    transport = MemoryTransport(
        [
            ("POST", "/api/v1/kill", 400, {"error": "BAD_TOKEN", "detail": "no"}),
            ("POST", "/api/v1/kill", 500, {}),
        ]
    )
    client = CoreClient("https://core.example", transport=transport)
    named = _raised(lambda: client.post_kill("handset", token="kill-token"))
    plain = _raised(lambda: client.post_kill("handset"))
    assert named is not None and named.kind == "BAD_TOKEN"
    assert plain is not None and plain.kind == "BAD_REQUEST"


def test_voice_timeout_is_70_and_other_calls_use_8() -> None:
    transport = MemoryTransport(
        [
            ("POST", "/api/v1/voice", 200, {"spoken": "ok"}),
            ("GET", "/api/v1/status", 200, {"ok": True}),
        ]
    )
    client = CoreClient("https://core.example", transport=transport)
    assert client.post_voice({"transcript": "hello"}) == {"spoken": "ok"}
    assert client.get_status() == {"ok": True}
    voice_timeout = transport.calls[0][4]
    fast_timeout = transport.calls[1][4]
    voice_body = transport.calls[0][3]
    assert voice_timeout == 70.0
    assert fast_timeout == 8.0
    assert voice_body is not None
    assert json.loads(voice_body) == {"transcript": "hello"}


def test_pull_and_control_put_client_id_in_the_query() -> None:
    transport = MemoryTransport(
        [
            ("GET", "/api/v1/cvm/pull", 200, {"pull": True}),
            ("GET", "/api/v1/control", 200, {"effective": {}}),
        ]
    )
    client = CoreClient("https://core.example", transport=transport)
    assert client.get_pull("phone-1") == {"pull": True}
    assert client.get_control("phone-1") == {"effective": {}}
    pull_url = transport.calls[0][1]
    control_url = transport.calls[1][1]
    assert pull_url.endswith("/api/v1/cvm/pull?client_id=phone-1")
    assert control_url.endswith("/api/v1/control?client_id=phone-1")


def test_error_detail_does_not_contain_the_bearer() -> None:
    secret = "plain-bearer-value"
    transport = MemoryTransport(
        [("GET", "/api/v1/status", 500, {"detail": f"echo {secret}"})]
    )
    client = CoreClient("https://core.example", secret, transport=transport)
    caught = _raised(client.get_status)
    leaked = caught is None or secret in str(caught)
    kind = caught.kind if caught is not None else ""
    assert kind == "BAD_REQUEST"
    assert leaked is False
    assert caught is not None
    assert "[REDACTED]" in caught.detail


def test_script_pops_the_first_match_only() -> None:
    transport = MemoryTransport(
        [
            ("GET", "/api/v1/missing", 500, {"error": "NO"}),
            ("GET", "/api/v1/status", 200, {"ok": True}),
        ]
    )
    client = CoreClient("https://core.example", transport=transport)
    assert client.get_status() == {"ok": True}
    missed = _raised(client.get_status)
    assert missed is not None
    assert missed.kind == "NOT_COMPOSED"
    assert len(transport.script) == 1


def test_redirect_keeps_the_original_https_url() -> None:
    """A 3xx is the response. The Location is not a second request."""
    handler = _NoRedirect()
    original = "https://core.example/api/v1/status"
    req = urllib.request.Request(original, headers={"Authorization": "Bearer not-a-live-key"})
    headers = Message()
    headers["Location"] = "http://other.example/taken"
    caught: urllib.error.HTTPError | None = None
    try:
        handler.redirect_request(
            req,
            io.BytesIO(b""),
            302,
            "Found",
            headers,
            "http://other.example/taken",
        )
    except urllib.error.HTTPError as exc:
        caught = exc
    assert caught is not None
    assert caught.url == req.full_url
    assert caught.url == original
    assert caught.code == 302
    assert caught.url.startswith("https://")
    moved = "http://other.example/taken" in caught.url
    assert moved is False


def test_urllib_transport_does_not_follow_with_urlopen() -> None:
    """The live transport uses the opener that refuses a redirect."""
    source = inspect.getsource(UrllibTransport.request)
    assert "urlopen" not in source
    assert "_opener()" in source
    installed = cast(list[object], getattr(_opener(), "handlers"))
    found = [item for item in installed if isinstance(item, _NoRedirect)]
    plain = [item for item in installed if type(item) is urllib.request.HTTPRedirectHandler]
    assert len(found) == 1
    assert plain == []


def test_construct_does_not_call_the_transport() -> None:
    transport = MemoryTransport([("GET", "/api/v1/status", 200, {"ok": True})])
    CoreClient("https://core.example", "xai-livekeyvalue", transport=transport)
    assert transport.calls == []
