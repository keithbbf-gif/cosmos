#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_pay_bedrock_rail — fail-closed Bedrock adapter.

No key or no endpoint refuses before any call. There is no SigV4 signer and
no default network transport: a caller injects the transport. The wizard
format check stays format-only and does not come through here.
"""
from __future__ import annotations

from typing import Any, Callable, Dict, Iterator, Optional


class NoSupply(RuntimeError):
    """Missing key or endpoint, or no injected transport. Gateway maps this to 503."""

    no_supply = True

    def __init__(self) -> None:
        super().__init__("bedrock rail is not configured")


class RailError(RuntimeError):
    """Transport returned a body this rail will not bill."""


def _as_chat(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Pass a priced OpenAI usage block through. Anything else is unpriced."""
    out = dict(raw)
    out.setdefault(
        "choices",
        [{
            "index": 0,
            "message": {"role": "assistant", "content": ""},
            "finish_reason": "stop",
        }],
    )
    usage = raw.get("usage")
    if (
        isinstance(usage, dict)
        and not usage.get("unpriced")
        and ("prompt_tokens" in usage or "completion_tokens" in usage)
    ):
        return out
    out["usage"] = {"unpriced": True}
    return out


class BedrockRail:
    """Bedrock chat relay. Signing is not implemented; transport is required."""

    def __init__(
        self,
        api_key: str = "",
        secret_key: str = "",
        region: str = "",
        endpoint: str = "",
        transport: Optional[Callable[..., Any]] = None,
        timeout_s: int = 60,
    ):
        self.api_key = str(api_key or "").strip()
        self._secret_key = str(secret_key or "").strip()
        self.region = str(region or "").strip()
        self.endpoint = str(endpoint or "").strip()
        self.transport = transport
        self.timeout_s = int(timeout_s)

    def _require(self) -> None:
        # Secret is stored for a later signer. This pass does not sign or call AWS.
        if not self.api_key or not self.endpoint or self.transport is None:
            raise NoSupply()

    def runsync(self, openai_request: Dict[str, Any], timeout_s: Optional[int] = None) -> Dict[str, Any]:
        self._require()
        assert self.transport is not None
        spec = {
            "url": self.endpoint,
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "body": openai_request,
            "timeout_s": int(timeout_s or self.timeout_s),
            "region": self.region,
        }
        raw = self.transport(spec)
        if not isinstance(raw, dict):
            raise RailError("BAD_RESPONSE transport returned no object")
        return _as_chat(raw)

    def stream(self, openai_request: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        resp = self.runsync(openai_request)
        yield {
            "id": resp.get("id", "bedrock"),
            "object": "chat.completion.chunk",
            "choices": [{"index": 0, "delta": {"content": ""}, "finish_reason": "stop"}],
            "usage": resp.get("usage") or {"unpriced": True},
        }


def from_config(config: Dict[str, Any], secrets: Optional[Dict[str, Any]] = None) -> Optional[BedrockRail]:
    """Attach only when a key and an endpoint are both present. Never opens a key file."""
    secrets = secrets or {}
    raw = config.get("bedrock")
    block: Dict[str, Any] = raw if isinstance(raw, dict) else {}
    key = str(
        block.get("api_key")
        or block.get("access_key")
        or secrets.get("bedrock_api_key")
        or secrets.get("aws_access_key_id")
        or ""
    ).strip()
    endpoint = str(block.get("endpoint") or secrets.get("bedrock_endpoint") or "").strip()
    if not key or not endpoint:
        return None
    secret = str(block.get("secret_key") or secrets.get("aws_secret_key") or "").strip()
    region = str(block.get("region") or secrets.get("aws_region") or "").strip()
    return BedrockRail(api_key=key, secret_key=secret, region=region, endpoint=endpoint)
