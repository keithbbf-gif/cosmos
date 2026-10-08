"""CLI doctor and say. The say tests inject a memory client so no socket opens."""

from __future__ import annotations

import io
import json
from contextlib import redirect_stderr, redirect_stdout

from cosmos_voice.cli import main
from cosmos_voice.transport import CoreClient, MemoryTransport

_SPOKEN = "scripted hello"


def _client(spoken: str) -> CoreClient:
    body: dict[str, object] = {"spoken": spoken}
    script: list[tuple[str, str, int, dict[str, object]]] = [
        ("POST", "/api/v1/voice", 200, body),
    ]
    return CoreClient("http://127.0.0.1:9", transport=MemoryTransport(script))


def test_doctor_prints_manifest() -> None:
    """doctor exits 0 and the manifest JSON names cosmos-voice."""
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        code = main(["doctor"])
    assert code == 0
    text = buffer.getvalue()
    parsed = json.loads(text)
    assert isinstance(parsed, dict)
    assert "cosmos-voice" in text


def test_say_injected_without_base() -> None:
    """An injected client does not need --base."""
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        code = main(["say", "--transcript", "hi"], client=_client(_SPOKEN))
    assert code == 0
    assert _SPOKEN in buffer.getvalue()


def test_bearer_over_http_prints_kind_only() -> None:
    """A cleartext bearer is refused with the kind and not the secret."""
    secret = "secret-token"
    out = io.StringIO()
    err = io.StringIO()
    argv = [
        "say",
        "--base",
        "http://127.0.0.1:9",
        "--transcript",
        "hi",
        "--bearer",
        secret,
    ]
    with redirect_stdout(out), redirect_stderr(err):
        code = main(argv)
    assert code == 2
    assert out.getvalue().strip() == "BEARER_OVER_HTTP"
    assert secret not in out.getvalue()
    assert secret not in err.getvalue()


def test_say_injected_accepts_closed_base() -> None:
    """The parser accepts --base to a closed port and the scripted mouth answers."""
    buffer = io.StringIO()
    argv = ["say", "--base", "http://127.0.0.1:9", "--transcript", "hi"]
    with redirect_stdout(buffer):
        code = main(argv, client=_client(_SPOKEN))
    assert code == 0
    assert _SPOKEN in buffer.getvalue()
