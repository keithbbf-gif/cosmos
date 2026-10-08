"""Voice doors. Core is the authority. Vendor doors stay uncomposed without a transport.

No door in this module opens a socket. Claude stores nothing and is off the route.
A vendor key is sent only as an Authorization header, never in an error detail.
"""

from __future__ import annotations

import json
import urllib.parse
from typing import cast

from cosmos_voice.errors import VoiceError
from cosmos_voice.session import VoiceSession
from cosmos_voice.transport import CoreClient, Transport
from cosmos_voice.types import FAST_TIMEOUT_S, HttpResponse

# Documented sockets (research 2026-10-01). This package does not open them.
# grok-voice-latest is the moving alias; the pin is the dated model.
_GROK_BASE = "wss://api.x.ai/v1/realtime?model=grok-voice-think-fast-2.0"
_GROK_MODEL = "grok-voice-think-fast-2.0"
_OPENAI_BASE = "wss://api.openai.com/v1/realtime?model=gpt-realtime-2.1"
_OPENAI_MODEL = "gpt-realtime-2.1"


def _kw_str(kwargs: dict[str, object], key: str, default: str) -> str:
    """Read one string option. A non-string is BAD_MODE and is not echoed."""

    if key not in kwargs:
        return default
    value = kwargs[key]
    if isinstance(value, str):
        return value
    raise VoiceError("BAD_MODE", "bad field")


def _kw_transport(kwargs: dict[str, object]) -> Transport | None:
    """Read an injected transport. Absent means the vendor door is uncomposed."""

    if "transport" not in kwargs or kwargs["transport"] is None:
        return None
    return cast(Transport, kwargs["transport"])


def _clean_base(base: str, default: str) -> str:
    """Drop surrounding space and a trailing slash. Blank falls back to ``default``."""

    chosen = base.strip().rstrip("/")
    return chosen if chosen else default


def _object_body(response: object) -> dict[str, object]:
    """Accept an ``HttpResponse`` or a JSON object. The detail never carries a key."""

    raw: object
    if isinstance(response, HttpResponse):
        raw = response.body
    elif isinstance(response, dict):
        raw = response
    else:
        raise VoiceError("BAD_CORE", "vendor body")
    if not isinstance(raw, dict):
        raise VoiceError("BAD_CORE", "vendor body")
    body: dict[str, object] = {}
    for key, value in raw.items():
        body[str(key)] = cast(object, value)
    return body


def _mapped(body: dict[str, object], brain: str) -> dict[str, object]:
    """Take a string ``output`` or ``spoken`` field. Confirm stays with Core."""

    text = body.get("output")
    if not isinstance(text, str):
        text = body.get("spoken")
    if not isinstance(text, str):
        text = ""
    mapped: dict[str, object] = {
        "spoken": text,
        "needs_confirm": False,
        "brain": brain,
    }
    return mapped


def _secret_url(base: str) -> None:
    """A vendor key is not sent on cleartext or on a URL with no scheme."""
    scheme = urllib.parse.urlsplit(base).scheme.lower()
    if scheme not in {"https", "wss"}:
        raise VoiceError("BEARER_OVER_HTTP", "refused on cleartext http")


def _vendor_turn(
    *,
    api_key: str,
    transport: Transport | None,
    base: str,
    model: str,
    brain: str,
    transcript: str,
) -> dict[str, object]:
    """Exercise an injected transport. An empty key is NO_KEY.

    No transport is NOT_COMPOSED: the live WebSocket is not opened here.
    The JSON body is the test double (model pin plus transcript), not a
    vendor ``session.update``. The key travels only in the header.
    """

    if not api_key.strip():
        raise VoiceError("NO_KEY")
    _secret_url(base)
    if transport is None:
        raise VoiceError("NOT_COMPOSED")
    headers = {
        "Authorization": "Bearer " + api_key,
        "Content-Type": "application/json",
    }
    payload: dict[str, object] = {"model": model, "input": transcript}
    encoded = json.dumps(payload).encode("utf-8")
    response = transport.request("POST", base, headers, encoded, FAST_TIMEOUT_S)
    return _mapped(_object_body(response), brain)


class CoreMouth:
    """Posts one spoken turn to Core over ``/api/v1/voice``."""

    def __init__(self, client: CoreClient) -> None:
        """Remember the Core client. The client owns the bearer."""

        self._client = client

    def speak_turn(
        self,
        transcript: str,
        session: VoiceSession,
        *,
        confirm_id: str = "",
        mode: str = "ptt",
    ) -> dict[str, object]:
        """Post ``voice_body`` and return Core's reply unchanged."""

        body = session.voice_body(transcript, mode=mode, confirm_id=confirm_id)
        return self._client.post_voice(body)


class GrokVoiceDoor:
    """xAI voice door. It stays uncomposed until a transport is injected."""

    def __init__(
        self,
        api_key: str = "",
        *,
        transport: Transport | None = None,
        base: str = _GROK_BASE,
    ) -> None:
        """Hold a key and an optional transport. This does not open a connection."""

        self._api_key = api_key
        self._transport = transport
        self._base = _clean_base(base, _GROK_BASE)

    def speak_turn(
        self,
        transcript: str,
        session: VoiceSession,
        *,
        confirm_id: str = "",
        mode: str = "ptt",
    ) -> dict[str, object]:
        """Speak through xAI, or refuse when the key or the transport is missing."""

        del session, confirm_id, mode
        return _vendor_turn(
            api_key=self._api_key,
            transport=self._transport,
            base=self._base,
            model=_GROK_MODEL,
            brain="grok",
            transcript=transcript,
        )


class OpenAIRealtimeDoor:
    """OpenAI realtime door. It does not open a socket itself."""

    def __init__(
        self,
        api_key: str = "",
        *,
        transport: Transport | None = None,
        base: str = _OPENAI_BASE,
    ) -> None:
        """Hold a key and an optional transport. This does not open a connection."""

        self._api_key = api_key
        self._transport = transport
        self._base = _clean_base(base, _OPENAI_BASE)

    def speak_turn(
        self,
        transcript: str,
        session: VoiceSession,
        *,
        confirm_id: str = "",
        mode: str = "ptt",
    ) -> dict[str, object]:
        """Speak through OpenAI, or refuse when the key or the transport is missing."""

        del session, confirm_id, mode
        return _vendor_turn(
            api_key=self._api_key,
            transport=self._transport,
            base=self._base,
            model=_OPENAI_MODEL,
            brain="openai",
            transcript=transcript,
        )


class ClaudeDoor:
    """Anthropic is off this route. The door stores nothing and builds no client."""

    def __init__(self) -> None:
        """Accept no key and store nothing."""

    def speak_turn(
        self,
        transcript: str,
        session: VoiceSession,
        *,
        confirm_id: str = "",
        mode: str = "ptt",
    ) -> dict[str, object]:
        """Refuse. Claude is not called."""

        del transcript, session, confirm_id, mode
        raise VoiceError("ANTHROPIC_OFF")


Door = CoreMouth | GrokVoiceDoor | OpenAIRealtimeDoor | ClaudeDoor


def open_door(name: str, **kwargs: object) -> Door:
    """Return the named door. Unknown names raise BAD_MODE. Core requires ``client``."""

    if name == "core":
        found = kwargs.get("client")
        if not isinstance(found, CoreClient):
            raise VoiceError("BAD_MODE", "client required")
        return CoreMouth(found)
    if name == "grok":
        return GrokVoiceDoor(
            _kw_str(kwargs, "api_key", ""),
            transport=_kw_transport(kwargs),
            base=_kw_str(kwargs, "base", _GROK_BASE),
        )
    if name == "openai":
        return OpenAIRealtimeDoor(
            _kw_str(kwargs, "api_key", ""),
            transport=_kw_transport(kwargs),
            base=_kw_str(kwargs, "base", _OPENAI_BASE),
        )
    if name == "claude":
        return ClaudeDoor()
    raise VoiceError("BAD_MODE", "unknown door")
