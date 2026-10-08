#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_pay_azure_rail — fail-closed Azure OpenAI chat adapter.

No key or no endpoint refuses before any call. Tests inject the transport.
The default transport is urllib and is not used when a transport is injected.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any, Callable, Dict, Iterator, Optional


class NoSupply(RuntimeError):
    """Missing key or endpoint. Gateway maps this to 503 with no meter event."""

    no_supply = True

    def __init__(self) -> None:
        super().__init__("azure rail is not configured")


class RailError(RuntimeError):
    """Vendor call failed or the body was not a usage block we can bill."""


def _as_chat(raw: Dict[str, Any]) -> Dict[str, Any]:
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


def _urllib_post(spec: Dict[str, Any]) -> Dict[str, Any]:
    req = urllib.request.Request(
        spec["url"],
        data=json.dumps(spec["body"]).encode("utf-8"),
        headers=spec["headers"],
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=int(spec.get("timeout_s") or 60)) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise RailError(f"HTTP {e.code}") from e
    except Exception as e:
        raise RailError("HTTP unreachable") from e


class AzureRail:
    def __init__(
        self,
        api_key: str = "",
        endpoint: str = "",
        transport: Optional[Callable[..., Any]] = None,
        timeout_s: int = 60,
    ):
        self.api_key = str(api_key or "").strip()
        self.endpoint = str(endpoint or "").strip()
        self.transport = transport
        self.timeout_s = int(timeout_s)

    def _require(self) -> None:
        if not self.api_key or not self.endpoint:
            raise NoSupply()

    def _call(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        raw = self.transport(spec) if self.transport is not None else _urllib_post(spec)
        if not isinstance(raw, dict):
            raise RailError("BAD_RESPONSE transport returned no object")
        return raw

    def runsync(self, openai_request: Dict[str, Any], timeout_s: Optional[int] = None) -> Dict[str, Any]:
        self._require()
        spec = {
            "url": self.endpoint,
            "method": "POST",
            "headers": {
                "Content-Type": "application/json",
                "api-key": self.api_key,
            },
            "body": openai_request,
            "timeout_s": int(timeout_s or self.timeout_s),
        }
        return _as_chat(self._call(spec))

    def stream(self, openai_request: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        resp = self.runsync(openai_request)
        yield {
            "id": resp.get("id", "azure"),
            "object": "chat.completion.chunk",
            "choices": [{"index": 0, "delta": {"content": ""}, "finish_reason": "stop"}],
            "usage": resp.get("usage") or {"unpriced": True},
        }


def from_config(config: Dict[str, Any], secrets: Optional[Dict[str, Any]] = None) -> Optional[AzureRail]:
    """Attach only when a key and an endpoint are both present. Never opens a key file."""
    secrets = secrets or {}
    raw = config.get("azure")
    block: Dict[str, Any] = raw if isinstance(raw, dict) else {}
    key = str(block.get("api_key") or secrets.get("azure_api_key") or "").strip()
    endpoint = str(block.get("endpoint") or secrets.get("azure_endpoint") or "").strip()
    if not key or not endpoint:
        return None
    return AzureRail(api_key=key, endpoint=endpoint)
