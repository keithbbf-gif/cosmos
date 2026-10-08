"""Mint helper for an ephemeral xAI client secret.

The long-lived key stays on the PC. ``mint_request`` only builds the
``POST /v1/realtime/client_secrets`` call. It does not perform it. The
parsed token's ``repr`` hides the value so a log of the object is safe.
The phone receives the value over the PC gateway, never ``XAI_API_KEY``.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from urllib.request import Request

from cosmos_voice_duplex.config import VoiceConfig
from cosmos_voice_duplex.rails.xai_realtime import client_secret_request


@dataclass(frozen=True)
class EphemeralToken:
    value: str
    expires_at: int | None = None

    def __repr__(self) -> str:
        return f"EphemeralToken(value='***', expires_at={self.expires_at!r})"


def parse_client_secret(body: bytes) -> EphemeralToken:
    data = json.loads(body.decode("utf-8"))
    if not isinstance(data, dict):
        raise ValueError("client secret response")
    value = data.get("value")
    if not isinstance(value, str) or value == "":
        raise ValueError("client secret response has no value")
    expires = data.get("expires_at")
    expires_at = expires if isinstance(expires, int) else None
    return EphemeralToken(value, expires_at)


def mint_request(cfg: VoiceConfig, api_key: str, seconds: int = 300) -> Request:
    """Build the mint call. Seconds are capped at the published 3600 maximum."""

    if seconds < 1 or seconds > 3600:
        raise ValueError("seconds must be 1..3600")
    return client_secret_request(cfg, api_key, seconds)


def subprotocol(token: EphemeralToken) -> str:
    """Browser and phone WebSocket subprotocol. The value is not a log line."""

    return "xai-client-secret." + token.value
