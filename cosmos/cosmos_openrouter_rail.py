#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_openrouter_rail - satellite API rail `openrouter-api`.

Named-model pin (Keith 2026-09-07). MESH_ADDITIONS row 16 REJECTED the
rotating `openrouter/free` router (silent model swap / H3 H4). Named pin
only because Keith asked.

  google/gemma-4-26b-a4b-it:free   (default, $0)
  google/gemma-4-31b-it:free
  z-ai/glm-5.3-flash              (value coder 2026-09-07: high skill, low cost)

POST https://openrouter.ai/api/v1/chat/completions
GET  https://openrouter.ai/api/v1/models
Key: live/config/openrouter_api_key.txt (never printed). OPENROUTER_API_KEY
env is a fallback, not a second store.

Runtime binding = response.model, not the request. allow_fallbacks=false.
Do not send openrouter/free or openrouter/auto.

    py -3.14 cosmos\\cosmos_openrouter_rail.py --selftest
    py -3.14 cosmos\\cosmos_openrouter_rail.py --root V:\\A\\Ai\\COSMOS\\live --gate
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

SCHEMA = "cosmos-openrouter-rail/1"
WORKER = "cosmos-openrouter-rail"
LINK_ID = "openrouter-api"
BASE = "https://openrouter.ai/api/v1"
KEY_NAME = "openrouter_api_key.txt"
SPEC_NAME = "openrouter_rail.json"
PROBE_NAME = "openrouter_rail_probe.json"
SRC = "core"
DST = "models"
DEFAULT_MODEL = "google/gemma-4-26b-a4b-it:free"
GEMMA_31B = "google/gemma-4-31b-it:free"
PINNED_FREE = frozenset({DEFAULT_MODEL, GEMMA_31B})
# Live GET /api/v1/model_rater 2026-09-07: coding 71.5, $0.075 / $0.250 per 1M.
# Different family from Grok / Gemini / Claude. Not the rotator.
VALUE_CODER = "z-ai/glm-5.3-flash"
PINNED_VALUE = frozenset({VALUE_CODER})
PINNED = PINNED_FREE | PINNED_VALUE
CHAT_PATH = "/chat/completions"
MODELS_PATH = "/models"
GENERATION_PATH = "/generation"
USAGE_COOKBOOK = (
    "https://openrouter.ai/docs/cookbook/administration/usage-accounting"
)
USAGE_OBS = "usage.jsonl"
# Artificial Analysis indices (intelligence / coding / agentic) live here,
# not on every GET /models row. Citation: openrouter.ai/docs … /benchmarks.
BENCHMARKS_PATH = "/benchmarks?source=artificial-analysis&max_results=500"
DEFAULT_MAX_TOKENS = 1024
GATE_MAX_TOKENS = 256
UA = "COSMOS-openrouter-rail/1 (openrouter-api; keithbbf-gif/cosmos)"
VENDOR_DOCS = "https://openrouter.ai/docs"
VENDOR_MODELS = "https://openrouter.ai/models"
HTTP_REFERER = "https://github.com/keithbbf-gif/cosmos"
X_TITLE = "COSMOS"
_ROTATING = frozenset({"openrouter/free", "openrouter/auto", "openrouter/free:free"})


class OpenRouterRailError(RuntimeError):
    """kind in {NO_KEY, BAD_SPEC, BAD_ROOT, UNREACHABLE, AUTH_REQUIRED, BROKE, REFUSED}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def default_spec() -> dict:
    return {
        "schema": SCHEMA,
        "link_id": LINK_ID,
        "rail_type": "API",
        "src": SRC,
        "dst": DST,
        "policy_rank": 0,
        "metered_usd": 0.0,
        "budget_usd": 0.0,
        "base": BASE,
        "key_name": KEY_NAME,
        "default_model": DEFAULT_MODEL,
        "pinned_free": sorted(PINNED_FREE),
        "timeout_s": 60,
        "vendor_docs": VENDOR_DOCS,
        "vendor_models": VENDOR_MODELS,
        "usage_cookbook": USAGE_COOKBOOK,
        "note": (
            "OpenRouter named Gemma 4 :free pins. Not openrouter/free rotator. "
            "Keith 2026-09-07. Bind response.model. Key never printed. "
            "Usage is always in the chat response (cookbook usage-accounting). "
            "Do not send usage.include — deprecated, no effect."
        ),
    }


def model_refused(model: str) -> str | None:
    m = (model or "").strip()
    if not m:
        return "empty model"
    ml = m.lower()
    if ml in _ROTATING or (ml.endswith("/free") and "gemma-4" not in ml):
        return f"rotating/unpinned OpenRouter id {m!r} (H3 silent swap — named pin only)"
    if m not in PINNED:
        return f"not a pinned OpenRouter id {m!r}; want {sorted(PINNED)}"
    return None


def _pin_origin(spec: dict) -> dict:
    base = str(spec.get("base") or BASE).rstrip("/")
    if base != BASE:
        raise OpenRouterRailError("BAD_SPEC", f"base {base!r} != {BASE!r}")
    spec["base"] = BASE
    kn = str(spec.get("key_name") or KEY_NAME)
    if kn != KEY_NAME:
        raise OpenRouterRailError("BAD_SPEC", f"key_name {kn!r} != {KEY_NAME!r}")
    spec["key_name"] = KEY_NAME
    spec["src"] = str(spec.get("src") or SRC) or SRC
    spec["dst"] = str(spec.get("dst") or DST) or DST
    spec["rail_type"] = "API"
    spec["link_id"] = str(spec.get("link_id") or LINK_ID) or LINK_ID
    spec["metered_usd"] = float(spec.get("metered_usd") or 0.0)
    spec["budget_usd"] = float(spec.get("budget_usd") or 0.0)
    spec["policy_rank"] = int(spec.get("policy_rank") or 0)
    spec["timeout_s"] = int(spec.get("timeout_s") or 60)
    dm = str(spec.get("default_model") or DEFAULT_MODEL).strip() or DEFAULT_MODEL
    why = model_refused(dm)
    if why:
        raise OpenRouterRailError("BAD_SPEC", why)
    spec["default_model"] = dm
    spec["pinned_free"] = sorted(PINNED_FREE)
    spec["pinned_value"] = sorted(PINNED_VALUE)
    spec["pinned"] = sorted(PINNED)
    spec["schema"] = SCHEMA
    spec["vendor_docs"] = VENDOR_DOCS
    spec["vendor_models"] = VENDOR_MODELS
    spec["usage_cookbook"] = USAGE_COOKBOOK
    return spec


def merge_spec(overlay) -> dict:
    spec = default_spec()
    if overlay is None:
        return _pin_origin(spec)
    if not isinstance(overlay, dict):
        raise OpenRouterRailError("BAD_SPEC", f"spec overlay is {type(overlay).__name__}")
    for k, v in overlay.items():
        spec[k] = v
    if spec.get("schema") != SCHEMA:
        raise OpenRouterRailError("BAD_SPEC", f"spec schema {spec.get('schema')!r} != {SCHEMA}")
    if spec.get("rail_type") not in (None, "API"):
        raise OpenRouterRailError(
            "BAD_SPEC", f"openrouter rail_type must be API, got {spec.get('rail_type')!r}")
    return _pin_origin(spec)


def load_spec(path: Path | None) -> dict:
    if path is None or not Path(path).exists():
        return default_spec()
    try:
        raw = Path(path).read_text(encoding="utf-8")
    except OSError as e:
        raise OpenRouterRailError("BAD_SPEC", f"unreadable spec {path}: {e}") from e
    try:
        overlay = json.loads(raw)
    except ValueError as e:
        raise OpenRouterRailError("BAD_SPEC", f"unparseable spec {path}: {e}") from e
    return merge_spec(overlay)


def write_spec(path: Path, spec: dict | None = None) -> dict:
    body = merge_spec(spec)
    body.pop("api_key", None)
    body.pop("key", None)
    body.pop("openrouter_api_key", None)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(body, indent=2, sort_keys=True,
                               ensure_ascii=False) + "\n",
                    encoding="utf-8")
    return body


def redact_key(key: str) -> str:
    k = (key or "").strip()
    if len(k) >= 4:
        return f"sk-or-…{k[-4:]}"
    return "sk-or-…????"


def read_key(key_path: Path | None) -> str | None:
    if key_path is not None:
        p = Path(key_path)
        if p.exists():
            try:
                text = p.read_text(encoding="utf-8").strip()
            except OSError:
                text = ""
            if text:
                return text
    env = (os.environ.get("OPENROUTER_API_KEY") or "").strip()
    return env or None


def _http_kind(status: int) -> str:
    if status in (401, 403):
        return "AUTH_REQUIRED"
    if status in (-1,):
        return "UNREACHABLE"
    return "BROKE"


def _real_http(method: str, url: str, body, headers: dict, timeout_s: float):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, method=method, data=data, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as r:  # noqa: S310
            raw = r.read().decode("utf-8") or "{}"
            hdrs = {k.lower(): v for k, v in r.headers.items()}
            try:
                obj = json.loads(raw)
            except ValueError:
                obj = {"raw": raw[:400]}
            return int(r.status), hdrs, obj
    except urllib.error.HTTPError as e:
        raw = (e.read() or b"").decode("utf-8", "replace")
        try:
            obj = json.loads(raw) if raw else {"error": str(e)}
        except ValueError:
            obj = {"error": raw[:400]}
        hdrs = {k.lower(): v for k, v in (e.headers or {}).items()}
        return int(e.code), hdrs, obj
    except Exception as e:  # noqa: BLE001
        return -1, {}, {"error": f"{type(e).__name__}: {e}"}


def _as_int(v):
    if v is None or v == "":
        return None
    try:
        return int(v)
    except (TypeError, ValueError):
        try:
            return int(float(v))
        except (TypeError, ValueError):
            return None


def _as_float(v):
    if v is None or v == "":
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def fold_usage(obj) -> dict:
    """Vendor usage as returned. Missing fields stay None — never invented.

    Cookbook: usage is always in the chat response. usage.include is
    deprecated and must not be sent. GET /generation?id= is the async audit.
    """
    rec = {
        "kind": "UNMEASURED",
        "generation_id": None,
        "prompt_tokens": None,
        "completion_tokens": None,
        "total_tokens": None,
        "reasoning_tokens": None,
        "cached_tokens": None,
        "cache_write_tokens": None,
        "audio_tokens": None,
        "cost": None,
        "upstream_inference_cost": None,
        "cookbook": USAGE_COOKBOOK,
        "note": (
            "Usage is always included in the chat response. "
            "usage.include / stream_options.include_usage are deprecated "
            "and are not sent. Does not invent."
        ),
    }
    if not isinstance(obj, dict):
        return rec
    gid = obj.get("id")
    if gid:
        rec["generation_id"] = str(gid)
    u = obj.get("usage") if isinstance(obj.get("usage"), dict) else {}
    details_c = (u.get("completion_tokens_details")
                 if isinstance(u.get("completion_tokens_details"), dict) else {})
    details_p = (u.get("prompt_tokens_details")
                 if isinstance(u.get("prompt_tokens_details"), dict) else {})
    cost_d = (u.get("cost_details")
              if isinstance(u.get("cost_details"), dict) else {})
    rec["prompt_tokens"] = _as_int(u.get("prompt_tokens"))
    rec["completion_tokens"] = _as_int(u.get("completion_tokens"))
    rec["total_tokens"] = _as_int(u.get("total_tokens"))
    rec["reasoning_tokens"] = _as_int(details_c.get("reasoning_tokens"))
    rec["cached_tokens"] = _as_int(details_p.get("cached_tokens"))
    rec["cache_write_tokens"] = _as_int(details_p.get("cache_write_tokens"))
    rec["audio_tokens"] = _as_int(details_p.get("audio_tokens"))
    rec["cost"] = _as_float(u.get("cost"))
    rec["upstream_inference_cost"] = _as_float(
        cost_d.get("upstream_inference_cost"))
    measured = any(
        rec[k] is not None
        for k in ("prompt_tokens", "completion_tokens", "total_tokens",
                  "cost", "cached_tokens", "reasoning_tokens")
    )
    rec["kind"] = "MEASURED" if measured else "UNMEASURED"
    return rec


def usage_dir(paths) -> Path:
    return paths.role("state", "openrouter")


def usage_path(paths) -> Path:
    return usage_dir(paths) / USAGE_OBS


def record_usage(paths, fold: dict, *, model="", stage="", profile="") -> dict:
    """Append one observed usage row. Does not invent. POST-path only."""
    row = dict(fold) if isinstance(fold, dict) else fold_usage({})
    row["schema"] = SCHEMA
    row["at"] = datetime.now().astimezone().isoformat(timespec="seconds")
    row["model"] = str(model or "")[:160]
    row["stage"] = str(stage or "")[:40]
    row["profile"] = str(profile or "")[:40]
    d = usage_dir(paths)
    d.mkdir(parents=True, exist_ok=True)
    with usage_path(paths).open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    snap = snapshot_usage(paths)
    snap["last"] = row
    return snap


def snapshot_usage(paths) -> dict:
    """GET fold. Never mkdir. Never invents."""
    p = usage_path(paths)
    rec = {
        "schema": SCHEMA,
        "ok": True,
        "kind": "UNMEASURED",
        "n_obs": 0,
        "prompt_tokens": None,
        "completion_tokens": None,
        "total_tokens": None,
        "cost": None,
        "cookbook": USAGE_COOKBOOK,
        "does_not_send_include": True,
        "note": (
            "OpenRouter usage accounting: tokens/cost/cache from the chat "
            "response. GET /generation?id= is audit, not a billing page. "
            "UNMEASURED until a dispatch is recorded."
        ),
    }
    if not p.is_file():
        return rec
    try:
        text = p.read_text(encoding="utf-8")
    except OSError:
        rec["kind"] = "BROKE"
        return rec
    n = 0
    ptok = ctok = ttok = 0
    cost = 0.0
    saw_p = saw_c = saw_t = saw_cost = False
    last = None
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except ValueError:
            continue
        if not isinstance(row, dict):
            continue
        n += 1
        last = row
        v = _as_int(row.get("prompt_tokens"))
        if v is not None:
            ptok += v
            saw_p = True
        v = _as_int(row.get("completion_tokens"))
        if v is not None:
            ctok += v
            saw_c = True
        v = _as_int(row.get("total_tokens"))
        if v is not None:
            ttok += v
            saw_t = True
        f = _as_float(row.get("cost"))
        if f is not None:
            cost += f
            saw_cost = True
    rec["n_obs"] = n
    rec["prompt_tokens"] = ptok if saw_p else None
    rec["completion_tokens"] = ctok if saw_c else None
    rec["total_tokens"] = ttok if saw_t else None
    rec["cost"] = round(cost, 8) if saw_cost else None
    rec["kind"] = "MEASURED" if n else "UNMEASURED"
    rec["last"] = last
    return rec


def _message_text(body: dict) -> str:
    choices = body.get("choices") if isinstance(body, dict) else None
    if not isinstance(choices, list) or not choices:
        return ""
    msg = (choices[0] or {}).get("message") if isinstance(choices[0], dict) else {}
    if not isinstance(msg, dict):
        return ""
    content = msg.get("content")
    if isinstance(content, str) and content.strip():
        return content.strip()
    return ""


class OpenRouterRail:
    """Dispatcher adapter. kind=API. probe=GET /models. dispatch=chat-create."""

    kind = "API"

    def __init__(self, key_path: Path | str | None, spec: dict | None = None,
                 http=None):
        self.spec = merge_spec(spec)
        self.key_path = Path(key_path) if key_path is not None else None
        self.metered_usd = float(self.spec.get("metered_usd") or 0.0)
        self._http = http
        self.link_id = self.spec["link_id"]
        self._last = None

    def last_identity(self) -> dict | None:
        return self._last

    def _headers(self, key: str) -> dict:
        return {
            "Authorization": "Bearer " + key,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "HTTP-Referer": HTTP_REFERER,
            "X-OpenRouter-Title": X_TITLE,
            "User-Agent": UA,
        }

    def _call(self, method: str, path: str, body=None):
        if self._http is not None:
            return self._http(method, path, body)
        key = read_key(self.key_path)
        if not key:
            return 401, {}, {"error": {"message": "NO_KEY", "code": "invalid_api_key"}}
        url = self.spec["base"] + path
        return _real_http(method, url, body, self._headers(key),
                          float(self.spec["timeout_s"]))

    def probe(self):
        status, hdrs, body = self._call("GET", MODELS_PATH)
        ids = []
        if isinstance(body, dict):
            for row in body.get("data") or []:
                if isinstance(row, dict) and row.get("id"):
                    ids.append(str(row["id"]))
        has = DEFAULT_MODEL in ids
        has_31 = GEMMA_31B in ids
        ok = status == 200 and has
        kind = None if ok else _http_kind(status if status != 200 else 0)
        if status == 200 and not has:
            kind = "BROKE"
        rec = {
            "ok": ok,
            "http": status,
            "n_models": len(ids),
            "has_gemma4_26b": has,
            "has_gemma4_31b": has_31,
            "model_ids": [i for i in ids if i in PINNED_FREE],
            "kind": kind,
            "detail": (
                f"http={status} n={len(ids)} has {DEFAULT_MODEL}={has}"
            ),
        }
        self._last = rec
        return ok, rec["detail"]

    def dispatch(self, payload: dict, *, paths=None) -> dict:
        payload = payload if isinstance(payload, dict) else {}
        model = str(payload.get("model") or self.spec["default_model"]).strip()
        why = model_refused(model)
        if why:
            return {"ok": False, "kind": "REFUSED", "detail": why,
                    "model_requested": model, "link_id": self.link_id}
        if payload.get("allow_fallbacks") is True:
            return {"ok": False, "kind": "REFUSED",
                    "detail": "allow_fallbacks=true is H3 silent swap",
                    "link_id": self.link_id}
        text = str(payload.get("text") or payload.get("prompt") or "").strip()
        messages = payload.get("messages")
        if not isinstance(messages, list) or not messages:
            if not text:
                return {"ok": False, "kind": "REFUSED",
                        "detail": "messages or text required",
                        "link_id": self.link_id}
            messages = [{"role": "user", "content": text}]
        max_c = payload.get("max_tokens")
        if max_c is None:
            max_c = payload.get("max_completion_tokens")
        try:
            max_c = int(max_c) if max_c is not None else DEFAULT_MAX_TOKENS
        except (TypeError, ValueError):
            max_c = DEFAULT_MAX_TOKENS
        body = {
            "model": model,
            "messages": messages,
            "max_tokens": max_c,
            "stream": False,
            "provider": {"allow_fallbacks": False},
        }
        # Cookbook: usage is always in the response. Do not send the
        # deprecated usage.include / stream_options.include_usage flags.
        status, hdrs, obj = self._call("POST", CHAT_PATH, body)
        usage = obj.get("usage") if isinstance(obj, dict) else None
        response_model = obj.get("model") if isinstance(obj, dict) else None
        content = _message_text(obj if isinstance(obj, dict) else {})
        bound_ok = bool(response_model) and (
            str(response_model) == model or str(response_model).startswith(model.split(":")[0])
        )
        ok = status == 200 and bound_ok
        usage_fold = fold_usage(obj if isinstance(obj, dict) else {})
        rec = {
            "ok": ok,
            "http": status,
            "kind": None if ok else _http_kind(status),
            "model_requested": model,
            "model": response_model,
            "text": content[:4000],
            "usage": usage if isinstance(usage, dict) else {},
            "usage_fold": usage_fold,
            "id": obj.get("id") if isinstance(obj, dict) else None,
            "link_id": self.link_id,
            "detail": f"http={status} response_model={response_model!r}",
        }
        if not ok and rec["kind"] is None:
            rec["kind"] = "BROKE"
        if ok and paths is not None:
            try:
                record_usage(paths, usage_fold, model=str(response_model or model),
                             stage=str(payload.get("stage") or ""),
                             profile=str(payload.get("profile") or ""))
            except Exception:  # noqa: BLE001
                rec["usage_record"] = "BROKE"
        self._last = rec
        return rec

    def fetch_generation(self, generation_id: str) -> dict:
        """GET /generation?id= — async usage audit. Not a billing page."""
        gid = str(generation_id or "").strip()
        if not gid:
            return {"ok": False, "kind": "BAD_INPUT",
                    "detail": "generation id required",
                    "cookbook": USAGE_COOKBOOK}
        q = GENERATION_PATH + "?id=" + urllib.parse.quote(gid, safe="")
        status, hdrs, obj = self._call("GET", q)
        data = obj.get("data") if isinstance(obj, dict) else None
        if not isinstance(data, dict):
            data = obj if isinstance(obj, dict) else {}
        fold = {
            "kind": "UNMEASURED",
            "generation_id": data.get("id") or gid,
            "prompt_tokens": _as_int(data.get("native_tokens_prompt")
                                     or data.get("tokens_prompt")),
            "completion_tokens": _as_int(data.get("native_tokens_completion")
                                         or data.get("tokens_completion")),
            "total_tokens": None,
            "reasoning_tokens": _as_int(data.get("native_tokens_reasoning")),
            "cached_tokens": _as_int(data.get("native_tokens_cached")),
            "cost": _as_float(data.get("total_cost")
                              if data.get("total_cost") is not None
                              else data.get("usage")),
            "upstream_inference_cost": _as_float(
                data.get("upstream_inference_cost")),
            "model": data.get("model"),
            "is_byok": data.get("is_byok"),
            "cookbook": USAGE_COOKBOOK,
            "source": "GET /generation",
        }
        if fold["prompt_tokens"] is not None and fold["completion_tokens"] is not None:
            fold["total_tokens"] = fold["prompt_tokens"] + fold["completion_tokens"]
        fold["kind"] = (
            "MEASURED" if any(fold[k] is not None for k in (
                "prompt_tokens", "completion_tokens", "cost"))
            else "UNMEASURED"
        )
        # Cookbook: upstream_inference_cost is only for BYOK; else 0/null.
        return {
            "ok": status == 200,
            "http": status,
            "kind": None if status == 200 else _http_kind(status),
            "usage_fold": fold,
            "cookbook": USAGE_COOKBOOK,
            "link_id": self.link_id,
        }


def spec_path_for(paths) -> Path:
    return paths.config(SPEC_NAME)


def key_path_for(paths, spec: dict | None = None) -> Path:
    _ = spec
    return paths.config(KEY_NAME)


def probe_path_for(paths) -> Path:
    return paths.config(PROBE_NAME)


def register_openrouter_rail(registry, adapters: dict, spend_gate=None,
                             src: str | None = None, dst: str | None = None, *,
                             paths=None, spec=None, key_path=None,
                             http=None) -> dict:
    _ = spend_gate
    if spec is None and paths is not None:
        spec = load_spec(spec_path_for(paths))
    else:
        spec = merge_spec(spec)
    spec = dict(spec)
    if src:
        spec["src"] = src
    if dst:
        spec["dst"] = dst
    spec = _pin_origin(spec)
    if key_path is None and paths is not None:
        key_path = key_path_for(paths, spec)
    rail = OpenRouterRail(key_path, spec, http=http)
    lid = rail.link_id
    if lid not in registry.state():
        registry.register(lid, spec["rail_type"], spec["src"], spec["dst"],
                          policy_rank=int(spec["policy_rank"]))
    registry.attach_probe(lid, rail.probe)
    adapters[lid] = rail
    key = read_key(Path(key_path) if key_path else None)
    return {
        "link_id": lid,
        "rail": rail,
        "spec": spec,
        "key_ok": bool(key),
        "key_last4": redact_key(key) if key else "NO_KEY",
        "key_path": str(key_path) if key_path is not None else None,
        "src": spec["src"],
        "dst": spec["dst"],
    }


from cosmos_rail_base import (  # noqa: E402,F401
    _ledger_is_authority,
    write_probe_record,
)


def attach_to_kernel(kernel, adapters: dict | None = None, http=None,
                     *, boot_compose: bool = False) -> dict:
    if _ledger_is_authority(kernel) and not boot_compose:
        raise OpenRouterRailError(
            "REFUSED",
            "attach_to_kernel refuses authority LINK_REGISTERED until Kernel "
            "boot reattaches probes every boot. Pass boot_compose=True only "
            "from Kernel.__init__.")
    if adapters is None:
        adapters = getattr(kernel, "adapters", None)
        if adapters is None:
            adapters = {}
            kernel.adapters = adapters
    return register_openrouter_rail(
        kernel.registry, adapters, spend_gate=getattr(kernel, "spend", None),
        paths=kernel.paths, http=http)


def refuse_live_authority_attach(paths) -> dict:
    auth = paths.ledger("authority.jsonl")
    duck = type("KernelView", (), {})()
    duck.paths = paths
    duck.ledger = type("Led", (), {"_path": auth})()
    duck.registry = None
    duck.spend = None
    rec = {
        "authority_ledger": str(auth),
        "authority_exists": Path(auth).exists(),
        "tree_id": paths.sentinel.tree_id,
        "refused": False,
        "kind": None,
        "detail": None,
        "boot_compose_required": True,
    }
    try:
        attach_to_kernel(duck, {})
        rec["detail"] = "attach_to_kernel DID NOT refuse the authority ledger"
    except OpenRouterRailError as e:
        rec["refused"] = e.kind == "REFUSED"
        rec["kind"] = e.kind
        rec["detail"] = str(e)
    return rec


def _iso_now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def gate(root: str | os.PathLike, *, http=None) -> dict:
    from cosmos_paths import CosmosPaths
    from cosmos_ledger import Ledger
    from cosmos_registry import Registry
    from cosmos_spend import SpendGate

    paths = CosmosPaths(root)
    spec = load_spec(spec_path_for(paths))
    write_spec(spec_path_for(paths), spec)
    keyp = key_path_for(paths, spec)
    adapters = {}
    gate_dir = paths.role("state", "openrouter_rail")
    gate_dir.mkdir(parents=True, exist_ok=True)
    led = Ledger(gate_dir / "gate.jsonl", b"openrouter-rail-gate", WORKER)
    reg = Registry(led)
    spend = SpendGate(led)
    attached = register_openrouter_rail(
        reg, adapters, spend_gate=spend, spec=spec, key_path=keyp, http=http)
    rail = adapters[attached["link_id"]]
    ok, detail = rail.probe()
    ident = rail.last_identity() or {}
    chat = rail.dispatch({
        "text": "Reply with exactly GEMMA4_READY and nothing else.",
        "max_tokens": GATE_MAX_TOKENS,
    })
    rec = {
        "schema": SCHEMA,
        "worker": WORKER,
        "gated_at": _iso_now(),
        "root": str(paths.root),
        "tree_id": paths.sentinel.tree_id,
        "link_id": attached["link_id"],
        "key_last4": attached["key_last4"],
        "key_ok": attached["key_ok"],
        "key_path_name": KEY_NAME,
        "key_value_emitted": False,
        "probe_ok": ok,
        "probe_detail": detail,
        "authority_ledger_written": False,
        "kernel_attached": False,
        "gate": "FAIL",
        "live_value": {
            "response_model": chat.get("model"),
            "models_http": ident.get("http"),
            "has_gemma4_26b": ident.get("has_gemma4_26b"),
            "chat_http": chat.get("http"),
        },
        "attach_refusal": refuse_live_authority_attach(paths),
    }
    models_ok = bool(ident.get("has_gemma4_26b")) and ident.get("http") == 200
    chat_ok = chat.get("http") == 200 and bool(chat.get("model"))
    attach_refused = bool(rec["attach_refusal"].get("refused"))
    if (ok and models_ok and chat_ok and attach_refused
            and not rec["authority_ledger_written"]
            and rec["kernel_attached"] is False
            and attached["key_ok"]):
        rec["gate"] = "PASS"
    rec["proof"] = (
        f"openrouter-api probe_ok={ok} "
        f"response_model={chat.get('model')!r} chat_http={chat.get('http')} "
        f"tree_id={rec['tree_id']} attach_refused={attach_refused}"
    )
    written = write_probe_record(probe_path_for(paths), rec)
    written["probe_path"] = str(probe_path_for(paths))
    return written


def _selftest() -> int:
    import tempfile
    from cosmos_kernel import install, Kernel
    from cosmos_ledger import Ledger
    from cosmos_registry import Registry
    from cosmos_spend import SpendGate

    results = []

    def check(label, fn):
        try:
            results.append((label, bool(fn()), ""))
        except Exception as e:  # noqa: BLE001
            results.append((label, False, f"{type(e).__name__}: {e}"))

    td = Path(tempfile.mkdtemp(prefix="cosmos_openrouter_rail_"))
    root = install(td / "live", tree_id="spike-openrouter-rail")
    from cosmos_paths import CosmosPaths
    paths = CosmosPaths(root)
    spec = write_spec(paths.config(SPEC_NAME))
    check("spec pins named Gemma 4, not the rotator",
          lambda: spec["default_model"] == DEFAULT_MODEL
          and DEFAULT_MODEL in spec["pinned_free"]
          and GEMMA_31B in spec["pinned_free"])
    keyp = paths.config(KEY_NAME)
    keyp.write_text("sk-or-selftest_xxxx\n", encoding="utf-8")

    def fake_http(method, path, body=None):
        if method == "GET" and path == MODELS_PATH:
            return 200, {}, {
                "data": [
                    {"id": DEFAULT_MODEL},
                    {"id": GEMMA_31B},
                    {"id": "openrouter/free"},
                ],
            }
        if method == "POST" and path == CHAT_PATH:
            assert body.get("provider", {}).get("allow_fallbacks") is False
            assert "usage" not in body
            assert "stream_options" not in body
            return 200, {}, {
                "id": "gen-test",
                "model": body.get("model"),
                "choices": [{"message": {"role": "assistant",
                                         "content": "GEMMA4_READY"}}],
                "usage": {
                    "prompt_tokens": 4,
                    "completion_tokens": 2,
                    "total_tokens": 6,
                    "cost": 0.0,
                    "cost_details": {"upstream_inference_cost": 0},
                    "completion_tokens_details": {"reasoning_tokens": 0},
                    "prompt_tokens_details": {
                        "cached_tokens": 1,
                        "cache_write_tokens": 0,
                        "audio_tokens": 0,
                    },
                },
            }
        if method == "GET" and path.startswith(GENERATION_PATH):
            return 200, {}, {"data": {
                "id": "gen-test",
                "model": DEFAULT_MODEL,
                "tokens_prompt": 4,
                "tokens_completion": 2,
                "native_tokens_prompt": 4,
                "native_tokens_completion": 2,
                "native_tokens_cached": 1,
                "native_tokens_reasoning": 0,
                "total_cost": 0.0,
                "upstream_inference_cost": 0,
                "usage": 0.0,
                "is_byok": False,
            }}
        return 404, {}, {"error": path}

    rail = OpenRouterRail(keyp, spec, http=fake_http)
    ok, detail = rail.probe()
    check("probe has gemma-4-26b-a4b-it:free",
          lambda: ok and DEFAULT_MODEL in detail)
    empty_u = snapshot_usage(paths)
    check("usage GET is UNMEASURED and does not mkdir",
          lambda: empty_u["kind"] == "UNMEASURED" and empty_u["n_obs"] == 0
          and not usage_dir(paths).exists())
    chat = rail.dispatch({"text": "ping"}, paths=paths)
    check("chat-create binds response.model",
          lambda: chat["ok"] and chat["model"] == DEFAULT_MODEL
          and chat["text"] == "GEMMA4_READY")
    check("usage fold is vendor-native; cost 0 is measured not invented",
          lambda: chat["usage_fold"]["kind"] == "MEASURED"
          and chat["usage_fold"]["prompt_tokens"] == 4
          and chat["usage_fold"]["cached_tokens"] == 1
          and chat["usage_fold"]["cost"] == 0.0
          and chat["usage_fold"]["cookbook"] == USAGE_COOKBOOK)
    snap_u = snapshot_usage(paths)
    check("recorded usage is on disk after dispatch, not before GET",
          lambda: snap_u["n_obs"] == 1 and snap_u["kind"] == "MEASURED"
          and snap_u["prompt_tokens"] == 4)
    gen = rail.fetch_generation("gen-test")
    check("GET /generation audit copies native tokens, not a billing page",
          lambda: gen["ok"] and gen["usage_fold"]["prompt_tokens"] == 4
          and gen["cookbook"] == USAGE_COOKBOOK)
    rot = rail.dispatch({"model": "openrouter/free", "text": "x"})
    check("openrouter/free rotator is REFUSED",
          lambda: (not rot["ok"]) and rot["kind"] == "REFUSED")
    other = rail.dispatch({"model": "meta-llama/llama-4-scout:free", "text": "x"})
    check("unpinned :free id is REFUSED",
          lambda: (not other["ok"]) and other["kind"] == "REFUSED")
    fb = rail.dispatch({"text": "x", "allow_fallbacks": True})
    check("allow_fallbacks=true is REFUSED",
          lambda: (not fb["ok"]) and fb["kind"] == "REFUSED")
    g31 = rail.dispatch({"model": GEMMA_31B, "text": "x"})
    check("pinned 31b :free is allowed",
          lambda: g31["ok"] and g31["model"] == GEMMA_31B)
    val = rail.dispatch({"model": VALUE_CODER, "text": "x"})
    check("pinned value coder glm-5.3-flash is allowed",
          lambda: val["ok"] and val["model"] == VALUE_CODER)

    led = Ledger(td / "n.jsonl", b"k", "core")
    reg = Registry(led)
    rec = register_openrouter_rail(
        reg, {}, spend_gate=SpendGate(led), spec=spec,
        key_path=keyp, http=fake_http)
    check("register claims openrouter-api core->models",
          lambda: rec["link_id"] == LINK_ID and rec["dst"] == DST)

    g = gate(root, http=fake_http)
    check("gate PASS quotes Gemma 4 response.model",
          lambda: g["gate"] == "PASS"
          and g["live_value"]["response_model"] == DEFAULT_MODEL)
    check("gate never emits the key value",
          lambda: g.get("key_value_emitted") is False
          and "sk-or-selftest" not in json.dumps(g))

    k = Kernel(root, worker="openrouter-rail-selftest")
    _before = set(k.registry.state())
    refused = False
    try:
        attach_to_kernel(k, {})
    except OpenRouterRailError as e:
        refused = e.kind == "REFUSED"
    check("attach_to_kernel refuses writing Kernel without boot_compose",
          lambda: refused and set(k.registry.state()) == _before)

    bad = [(l, e) for l, ok, e in results if not ok]
    for label, ok, err in results:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (openrouter named Gemma 4; rotator REFUSED)"
          % ("PASS" if not bad else "FAIL", len(results)))
    return 0 if not bad else 1


def main() -> int:
    ap = argparse.ArgumentParser(prog="cosmos_openrouter_rail")
    ap.add_argument("--root", default=None)
    ap.add_argument("--gate", action="store_true")
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if a.gate or a.probe:
        if not a.root:
            print(json.dumps({
                "ok": False, "kind": "BAD_ROOT",
                "error": "--root is required (resolver does not guess)",
            }, indent=1))
            return 2
        if a.probe and not a.gate:
            from cosmos_paths import CosmosPaths
            paths = CosmosPaths(a.root)
            spec = load_spec(spec_path_for(paths))
            rail = OpenRouterRail(key_path_for(paths, spec), spec)
            ok, detail = rail.probe()
            ident = rail.last_identity() or {}
            print(json.dumps({
                "ok": ok, "detail": detail,
                "http": ident.get("http"),
                "n_models": ident.get("n_models"),
                "has_gemma4_26b": ident.get("has_gemma4_26b"),
                "has_gemma4_31b": ident.get("has_gemma4_31b"),
                "key_last4": redact_key(read_key(key_path_for(paths, spec)) or ""),
            }, indent=1))
            return 0 if ok else 1
        rec = gate(a.root)
        print(json.dumps({
            "gate": rec.get("gate"),
            "proof": rec.get("proof"),
            "live_value": rec.get("live_value"),
            "key_last4": rec.get("key_last4"),
            "probe_path": rec.get("probe_path"),
            "tree_id": rec.get("tree_id"),
        }, indent=1, default=str))
        return 0 if rec.get("gate") == "PASS" else 1
    print(json.dumps({"ok": False, "kind": "BAD_ARGS",
                      "error": "pass --selftest or --root … --gate"}, indent=1))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
