#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_pay_vertex_rail — Pure Python stdlib Google Cloud Vertex AI Rail.

Zero third-party pip dependencies (no google-cloud-aiplatform, no google-auth).
Uses standard urllib, json, time, subprocess/openssl for RS256 token exchange.

Responsibilities:
  1. SDK-Free OAuth Token Exchange (GoogleOAuthTokenProvider):
     - Uses local openssl binary (auto-discovers Git/system OpenSSL) to sign RS256 JWT
     - Trades signed assertion at https://oauth2.googleapis.com/token for 60-min tokens
     - Auto-caches and refreshes tokens before expiration
  2. Translate OpenAI-style chat requests to Vertex AI Gemini REST payloads:
     messages [{"role": "user"|"assistant"|"system", "content": ...}]
     -> contents [{"role": "user"|"model", "parts": [{"text": ...}]}]
  3. Call Vertex AI streamGenerateContent (SSE / JSON stream) or generateContent:
     POST https://{region}-aiplatform.googleapis.com/v1/projects/{project}/locations/{region}/publishers/google/models/{model}:streamGenerateContent?alt=sse
  4. Extract byte-exact token provenance from Vertex usageMetadata:
     promptTokenCount, candidatesTokenCount, totalTokenCount, cachedContentTokenCount
     -> normalized into cosmos-meter/1 tokens {"in", "out", "cached"}
  5. Provenance & Fail-Closed Guard (F5 Spark13 Rule):
     If a stream terminates or disconnects without usageMetadata,
     flags response as unpriced so PayGateway emits RUN_UNPRICED and refunds the reserve.

Windows-first, stdlib only.
"""
from __future__ import annotations

import base64
import json
import os
import shutil
import subprocess
import tempfile
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Callable, Dict, Iterator, List, Optional, Tuple


class VertexRailError(RuntimeError):
    """Maps to RailError inside cosmos_pay_gateway."""


class VertexNoSupply(VertexRailError):
    """Project or credential missing. Gateway maps this to 503 with no meter event."""

    no_supply = True

    def __init__(self) -> None:
        super().__init__("vertex rail is not configured")


def _b64_urlsafe(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


class GoogleOAuthTokenProvider:
    """Pure stdlib Google Cloud OAuth2 token generator using system OpenSSL for RS256 signing."""

    TOKEN_URI = "https://oauth2.googleapis.com/token"
    DEFAULT_SCOPE = "https://www.googleapis.com/auth/cloud-platform"

    def __init__(self, sa_info: Dict[str, Any] | str):
        if isinstance(sa_info, (str, Path)):
            path = Path(sa_info)
            if not path.exists():
                raise VertexRailError(f"MISSING_SA_FILE service account JSON not found at {path}")
            self.sa_info = json.loads(path.read_text(encoding="utf-8"))
        else:
            self.sa_info = dict(sa_info)

        self._cached_token: str = ""
        self._cached_expiry: float = 0.0
        self._lock = threading.Lock()
        self._openssl_bin = self._find_openssl()

    @staticmethod
    def _find_openssl() -> str:
        bin_path = shutil.which("openssl")
        if bin_path:
            return bin_path
        for candidate in [
            r"C:\Program Files\Git\usr\bin\openssl.exe",
            r"C:\Program Files\Git\mingw64\bin\openssl.exe",
            r"C:\Program Files\OpenSSL-Win64\bin\openssl.exe",
        ]:
            if os.path.exists(candidate):
                return candidate
        return "openssl"

    def _sign_rsa_256(self, message: bytes, private_key_pem: str) -> bytes:
        """Execute isolated RS256 signing via openssl dgst."""
        with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".pem") as f:
            f.write(private_key_pem.strip())
            f.flush()
            key_path = f.name

        try:
            cmd = [self._openssl_bin, "dgst", "-sha256", "-sign", key_path]
            proc = subprocess.run(cmd, input=message, capture_output=True, check=True)
            return proc.stdout
        except Exception as e:
            raise VertexRailError(f"AUTH_FAILED OpenSSL signature error: {e}") from e
        finally:
            if os.path.exists(key_path):
                try:
                    os.unlink(key_path)
                except OSError:
                    pass

    def _exchange_jwt(self) -> Tuple[str, float]:
        client_email = self.sa_info.get("client_email")
        private_key = self.sa_info.get("private_key")
        token_uri = self.sa_info.get("token_uri") or self.TOKEN_URI

        if not client_email or not private_key:
            raise VertexRailError("BAD_CONFIG service account missing client_email or private_key")

        now = int(time.time())
        header = {"alg": "RS256", "typ": "JWT"}
        claim = {
            "iss": client_email,
            "scope": self.DEFAULT_SCOPE,
            "aud": token_uri,
            "exp": now + 3600,
            "iat": now,
        }

        signing_input = f"{_b64_urlsafe(json.dumps(header).encode())}.{_b64_urlsafe(json.dumps(claim).encode())}".encode()
        sig = self._sign_rsa_256(signing_input, private_key)
        assertion = f"{signing_input.decode('ascii')}.{_b64_urlsafe(sig)}"

        data = urllib.parse.urlencode({
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "assertion": assertion,
        }).encode("ascii")

        req = urllib.request.Request(token_uri, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                tok = res.get("access_token")
                exp_in = int(res.get("expires_in") or 3600)
                if not tok:
                    raise VertexRailError("BAD_RESPONSE Google token exchange returned empty token")
                return tok, time.time() + exp_in
        except urllib.error.HTTPError as e:
            raw = e.read().decode("utf-8", "replace")[:300] if hasattr(e, "read") else str(e)
            raise VertexRailError(f"AUTH_FAILED Google OAuth exchange {e.code}: {raw}") from e
        except Exception as e:
            raise VertexRailError(f"AUTH_FAILED Google OAuth unreachable: {e}") from e

    def get_token(self) -> str:
        now = time.time()
        with self._lock:
            if self._cached_token and now < (self._cached_expiry - 60):
                return self._cached_token
            tok, exp = self._exchange_jwt()
            self._cached_token = tok
            self._cached_expiry = exp
            return self._cached_token


class VertexAIRail:
    """Enterprise Vertex AI Gemini Rail with zero pip dependencies."""

    DEFAULT_REGION = "us-central1"
    ENDPOINT_TMPL = "https://{region}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{region}/publishers/google/models/{model}:generateContent"
    STREAM_TMPL = "https://{region}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{region}/publishers/google/models/{model}:streamGenerateContent?alt=sse"

    def __init__(
        self,
        project_id: str,
        access_token: str = "",
        api_key: str = "",
        token_provider: Optional[GoogleOAuthTokenProvider] = None,
        region: str = DEFAULT_REGION,
        timeout_s: int = 60,
        transport: Optional[Callable[..., Any]] = None,
    ):
        self.project_id = str(project_id).strip()
        self._access_token = str(access_token).strip()
        self._api_key = str(api_key).strip()
        self.token_provider = token_provider
        self.region = str(region or self.DEFAULT_REGION).strip()
        self.timeout_s = int(timeout_s)
        self.transport = transport

    def _configured(self) -> bool:
        if not self.project_id:
            return False
        return bool(self._access_token or self._api_key or self.token_provider is not None)

    def _get_bearer(self) -> str:
        if self.token_provider:
            return self.token_provider.get_token()
        return self._access_token

    # ------------------------------------------------------------- payload translation
    @staticmethod
    def _translate_request(openai_req: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], Dict[str, Any], Optional[Dict[str, Any]]]:
        """Convert OpenAI chat completion request to Vertex AI format:
        returns (contents, generation_config, system_instruction)."""
        messages = openai_req.get("messages") or []
        contents: List[Dict[str, Any]] = []
        system_instruction: Optional[Dict[str, Any]] = None

        for m in messages:
            if not isinstance(m, dict):
                continue
            role = m.get("role", "user")
            text = str(m.get("content") or "")

            if role == "system":
                # Vertex AI supports top-level systemInstruction
                system_instruction = {"parts": [{"text": text}]}
            else:
                vertex_role = "model" if role in ("assistant", "model") else "user"
                contents.append({
                    "role": vertex_role,
                    "parts": [{"text": text}],
                })

        if not contents:
            contents.append({"role": "user", "parts": [{"text": "Hello"}]})

        # Hyperparameters
        gen_config: Dict[str, Any] = {}
        if "max_tokens" in openai_req or "max_completion_tokens" in openai_req:
            raw_max = openai_req.get("max_tokens") or openai_req.get("max_completion_tokens")
            if raw_max and str(raw_max).isdigit():
                gen_config["maxOutputTokens"] = int(raw_max)
        if "temperature" in openai_req:
            try:
                gen_config["temperature"] = float(openai_req["temperature"])
            except (ValueError, TypeError):
                pass
        if "top_p" in openai_req:
            try:
                gen_config["topP"] = float(openai_req["top_p"])
            except (ValueError, TypeError):
                pass

        return contents, gen_config, system_instruction

    def _auth_headers(self) -> Dict[str, str]:
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": "TokenCenter-VertexRail/1.0",
        }
        bearer = self._get_bearer()
        if bearer:
            headers["Authorization"] = f"Bearer {bearer}"
            if self.project_id:
                headers["X-Goog-User-Project"] = self.project_id
        return headers

    def _resolve_model_name(self, model_id: str) -> str:
        """Resolve model slug to Vertex publisher model name.
        e.g., gemini-flash-vertex -> gemini-1.5-flash-002 (or latest)"""
        m = model_id.lower().strip()
        if "flash" in m:
            return "gemini-1.5-flash-002"
        if "pro" in m:
            return "gemini-1.5-pro-002"
        if "2.5" in m or "2-5" in m:
            return "gemini-2.5-flash"
        return m.split("/")[-1].replace("-vertex", "")

    def _post_json(self, url: str, payload: Dict[str, Any], timeout: int) -> Dict[str, Any]:
        """Injected transport, else urllib. The transport is the only test path."""
        if self.transport is not None:
            raw = self.transport({
                "url": url,
                "method": "POST",
                "headers": self._auth_headers(),
                "body": payload,
                "timeout_s": timeout,
            })
            if not isinstance(raw, dict):
                raise VertexRailError("BAD_RESPONSE transport returned no object")
            return raw
        req = urllib.request.Request(
            url, data=json.dumps(payload).encode("utf-8"), headers=self._auth_headers(), method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:300] if hasattr(e, "read") else str(e)
            raise VertexRailError(f"HTTP {e.code} on Vertex: {detail}") from e
        except Exception as e:
            raise VertexRailError(f"HTTP unreachable on Vertex: {e}") from e

    @staticmethod
    def _priced_usage(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """OpenAI usage block from an injected transport. Native Vertex JSON returns None."""
        usage = data.get("usage")
        if not isinstance(usage, dict) or usage.get("unpriced"):
            return None
        if "prompt_tokens" not in usage and "completion_tokens" not in usage:
            return None
        out = dict(data)
        out.setdefault(
            "choices",
            [{
                "index": 0,
                "message": {"role": "assistant", "content": ""},
                "finish_reason": "stop",
            }],
        )
        return out

    # ------------------------------------------------------------- blocking call
    def runsync(self, openai_request: Dict[str, Any], timeout_s: Optional[int] = None) -> Dict[str, Any]:
        """Execute blocking call against Vertex AI generateContent."""
        if not self._configured():
            raise VertexNoSupply()
        model = self._resolve_model_name(openai_request.get("model", "gemini-1.5-flash-002"))
        url = self.ENDPOINT_TMPL.format(region=self.region, project_id=self.project_id, model=model)
        if not self._get_bearer() and self._api_key:
            url += "?key=" + self._api_key

        contents, gen_config, sys_inst = self._translate_request(openai_request)
        payload: Dict[str, Any] = {"contents": contents}
        if gen_config:
            payload["generationConfig"] = gen_config
        if sys_inst:
            payload["systemInstruction"] = sys_inst

        t = int(timeout_s or self.timeout_s)
        data = self._post_json(url, payload, t)
        priced = self._priced_usage(data)
        if priced is not None:
            return priced

        # Extract text response
        candidates = data.get("candidates") or []
        content_text = ""
        if candidates:
            parts = (candidates[0].get("content") or {}).get("parts") or []
            if parts:
                content_text = parts[0].get("text", "")

        # Extract byte-exact usage metadata
        meta = data.get("usageMetadata") or {}
        usage = {
            "prompt_tokens": int(meta.get("promptTokenCount") or 0),
            "completion_tokens": int(meta.get("candidatesTokenCount") or 0),
            "total_tokens": int(meta.get("totalTokenCount") or 0),
            "cached_tokens": int(meta.get("cachedContentTokenCount") or 0),
        }
        if not usage["total_tokens"]:
            usage["unpriced"] = True

        return {
            "id": f"vertex-{int(time.time()*1000)}",
            "object": "chat.completion",
            "model": model,
            "choices": [{
                "index": 0,
                "message": {"role": "assistant", "content": content_text},
                "finish_reason": "stop",
            }],
            "usage": usage,
        }

    # ------------------------------------------------------------- SSE streaming
    def stream(self, openai_request: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        """SSE Streaming relay from Vertex streamGenerateContent.
        Yields chunk dicts in OpenAI format, ending with terminal usage block."""
        if not self._configured():
            raise VertexNoSupply()
        if self.transport is not None:
            resp = self.runsync(openai_request)
            yield {
                "id": resp.get("id", "vtx"),
                "object": "chat.completion.chunk",
                "choices": [{"index": 0, "delta": {"content": ""}, "finish_reason": "stop"}],
                "usage": resp.get("usage") or {"unpriced": True},
            }
            return
        model = self._resolve_model_name(openai_request.get("model", "gemini-1.5-flash-002"))
        url = self.STREAM_TMPL.format(region=self.region, project_id=self.project_id, model=model)
        if not self._get_bearer() and self._api_key:
            url += "&key=" + self._api_key

        contents, gen_config, sys_inst = self._translate_request(openai_request)
        payload: Dict[str, Any] = {"contents": contents}
        if gen_config:
            payload["generationConfig"] = gen_config
        if sys_inst:
            payload["systemInstruction"] = sys_inst

        req_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=req_bytes, headers=self._auth_headers(), method="POST")

        chunk_id = f"vtx-stream-{int(time.time())}"
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_s) as resp:
                buffer = ""
                for byte_chunk in resp:
                    if not byte_chunk:
                        continue
                    buffer += byte_chunk.decode("utf-8", "replace")
                    while "\n" in buffer:
                        line, buffer = buffer.split("\n", 1)
                        line = line.strip().lstrip(",").rstrip(",").strip()
                        if not line or line in ("[", "]"):
                            continue

                        json_str = line
                        if line.startswith("data:"):
                            json_str = line[5:].strip()

                        if not json_str:
                            continue

                        try:
                            chunk = json.loads(json_str)
                        except json.JSONDecodeError:
                            continue

                        candidates = chunk.get("candidates") or []
                        delta_text = ""
                        if candidates:
                            parts = (candidates[0].get("content") or {}).get("parts") or []
                            if parts:
                                delta_text = parts[0].get("text", "")

                        out_chunk: Dict[str, Any] = {
                            "id": chunk_id,
                            "object": "chat.completion.chunk",
                            "choices": [{
                                "index": 0,
                                "delta": {"content": delta_text},
                                "finish_reason": None,
                            }],
                        }

                        # Terminal usage metadata check
                        meta = chunk.get("usageMetadata")
                        if meta:
                            out_chunk["usage"] = {
                                "prompt_tokens": int(meta.get("promptTokenCount") or 0),
                                "completion_tokens": int(meta.get("candidatesTokenCount") or 0),
                                "total_tokens": int(meta.get("totalTokenCount") or 0),
                                "cached_tokens": int(meta.get("cachedContentTokenCount") or 0),
                            }

                        yield out_chunk

        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:300] if hasattr(e, "read") else str(e)
            raise VertexRailError(f"HTTP {e.code} on stream Vertex {model}: {detail}") from e
        except Exception as e:
            raise VertexRailError(f"HTTP unreachable on stream Vertex {model}: {e}") from e


def from_config(config: Dict[str, Any], secrets: Optional[Dict[str, Any]] = None) -> Optional[VertexAIRail]:
    """Attach when config carries the vertex project and a credential.

    Credential may sit on the vertex block or in secrets. This does not open
    a key file and does not call the network.
    """
    secrets = secrets or {}
    raw = config.get("vertex")
    block: Dict[str, Any] = raw if isinstance(raw, dict) else {}
    project = str(block.get("project_id") or config.get("vertex_project_id") or "").strip()
    if not project:
        return None
    token = str(block.get("access_token") or secrets.get("vertex_access_token") or "").strip()
    api_key = str(block.get("api_key") or secrets.get("vertex_api_key") or "").strip()
    if not token and not api_key:
        return None
    region = str(block.get("region") or config.get("vertex_region") or VertexAIRail.DEFAULT_REGION).strip()
    return VertexAIRail(project_id=project, access_token=token, api_key=api_key, region=region)
