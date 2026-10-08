#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_pay_runpod_rail — RunPod serverless adapter for the vLLM worker.

Borrowed pattern: cosmos_forge_rail (table-driven, dst= discipline, fail-closed,
never log the key). This rail is Layer 3a — the manufactured-supply lane.

RunPod serverless API (all under https://api.runpod.ai/v2/{endpoint_id}):
    POST /runsync        — wait up to ~90s, return result (v1 default)
    POST /run            — async, returns {id}
    GET  /stream/{id}    — SSE partial outputs (streaming relay)
    GET  /health         — workers loaded/running

Job input follows the runpod-workers/vllm contract:
    {"input": {"openai_route": "/v1/chat/completions", "openai_input": {…}}}

Provenance: cost is `measured` from the usage block the worker returns; the
gateway never bills an estimate. The key is never logged, never echoed
(the no-echo rule — cDeck SET-2).
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any, Dict, Iterator, Optional

BASE = "https://api.runpod.ai/v2"


class RailError(RuntimeError):
    """kind in {BAD_CONFIG, HTTP, TIMEOUT, BAD_RESPONSE, STREAM_ABORT}."""


class RunPodRail:
    def __init__(self, endpoint_id: str, api_key: str, base: str = BASE, timeout_s: int = 90):
        if not endpoint_id or not api_key:
            raise RailError("BAD_CONFIG endpoint_id and api_key are required — fail-closed")
        self.endpoint_id = endpoint_id
        self._key = api_key
        self.base = base.rstrip("/")
        self.timeout_s = int(timeout_s)

    # ---------------- internals ----------------
    def _url(self, path: str) -> str:
        return f"{self.base}/{self.endpoint_id}/{path.lstrip('/')}"

    def _post(self, path: str, body: Dict[str, Any], timeout: int) -> Dict[str, Any]:
        req = urllib.request.Request(
            self._url(path),
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self._key}"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read().decode("utf-8")
                try:
                    return json.loads(raw)
                except json.JSONDecodeError as e:
                    raise RailError(f"BAD_RESPONSE invalid json on {path}: {e}") from e
        except urllib.error.HTTPError as e:
            try:
                detail = e.read().decode("utf-8", "replace")[:300]
            except Exception:
                detail = str(e)
            raise RailError(f"HTTP {e.code} on {path}: {detail}") from e
        except urllib.error.URLError as e:
            raise RailError(f"HTTP unreachable on {path}: {getattr(e, 'reason', e)}") from e
        except (TimeoutError, OSError) as e:
            raise RailError(f"TIMEOUT on {path}: {e}") from e

    @staticmethod
    def _job(openai_request: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "input": {
                "openai_route": "/v1/chat/completions",
                "openai_input": openai_request,
            }
        }

    @staticmethod
    def _extract(result: Dict[str, Any]) -> Dict[str, Any]:
        """Unwrap the worker envelope → the OpenAI-shaped response + usage."""
        if result.get("status") not in ("COMPLETED", None):
            raise RailError(f"BAD_RESPONSE status={result.get('status')!r}")
        out = result.get("output") or {}
        # runpod-workers/vllm returns {"output": <openai response>} or the
        # response directly depending on worker version — accept both.
        resp = out.get("output", out) if isinstance(out, dict) else out
        if not isinstance(resp, dict) or "choices" not in resp:
            raise RailError("BAD_RESPONSE no choices in worker output")
        return resp

    # ---------------- public ----------------
    def runsync(self, openai_request: Dict[str, Any], timeout_s: Optional[int] = None) -> Dict[str, Any]:
        """Blocking relay (v1 default). Returns the OpenAI-shaped response.
        Usage block (tokens) is REQUIRED for measured provenance upstream."""
        t = int(timeout_s or self.timeout_s)
        raw = self._post("runsync", self._job(openai_request), timeout=t + 10)
        resp = self._extract(raw)
        if not isinstance(resp.get("usage"), dict):
            # UNPRICED is never zero: no usage block = the upstream must hold worst case.
            resp.setdefault("usage", {"unpriced": True})
        return resp

    def stream(self, openai_request: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        """SSE relay: POST /run → GET /stream/{id}. Yields chunk dicts; final
        chunk carries the usage block when the worker sends it."""
        job = self._post("run", self._job(openai_request), timeout=30)
        job_id = job.get("id")
        if not job_id:
            raise RailError("BAD_RESPONSE /run returned no job id")
        req = urllib.request.Request(
            self._url(f"stream/{job_id}"),
            headers={"Authorization": f"Bearer {self._key}", "Accept": "text/event-stream"},
            method="GET",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_s) as resp:
                for raw in resp:
                    line = raw.decode("utf-8", "replace").strip()
                    if not line.startswith("data:"):
                        continue
                    data = line[5:].strip()
                    if data == "[DONE]":
                        break
                    try:
                        yield json.loads(data)
                    except json.JSONDecodeError:
                        continue
        except urllib.error.URLError as e:
            raise RailError(f"STREAM_ABORT {e.reason}") from e

    def health(self) -> Dict[str, Any]:
        req = urllib.request.Request(
            self._url("health"), headers={"Authorization": f"Bearer {self._key}"}, method="GET"
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            raise RailError(f"HTTP {e.code} on health") from e
        except urllib.error.URLError as e:
            raise RailError(f"HTTP unreachable on health: {e.reason}") from e
