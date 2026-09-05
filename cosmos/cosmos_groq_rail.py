#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_groq_rail - satellite API rail `groq-api` (cheap reasoning).

GroqCloud LPU inference. NOT xAI Grok. Vendor contract:
https://console.groq.com/docs/api-reference#chat-create
Catalog: https://console.groq.com/docs/models
Cookbook (research pointer, not a rewrite):
https://github.com/groq/groq-api-cookbook
Rate limits (org-wide; headers are ground truth, not the docs table):
https://console.groq.com/docs/rate-limits
POST https://api.groq.com/openai/v1/chat/completions
GET  https://api.groq.com/openai/v1/models

Default model `openai/gpt-oss-20b` (Keith 2026-09-04 cheap reasoning).
Runtime binding = the `model` string in the RESPONSE, not the request.
Persist `usage` + `x-ratelimit-*` + `retry-after`. Budget $0 Free. Batch/Flex stay dark
(do not send service_tier=flex). Do not dispatch Mixtral or Llama 3.x
Free/Dev IDs. Cookbook tutorials that use Batch, Flex, Llama-3, or
LangChain/CrewAI/LiteLLM are vendor recipes — COSMOS does not import them.
Firecrawl MCP in the cookbook is a recipe; COSMOS already has firecrawl-web.
Key: live/config/groq_api_key.txt (never printed).

Does NOT edit kernel/ledger/sched/service. Kernel attach BACKLOG.
attach_to_kernel refuses the authority ledger unless boot_compose=True.

    py -3.14 cosmos\\cosmos_groq_rail.py --selftest
    py -3.14 cosmos\\cosmos_groq_rail.py --root V:\\A\\Ai\\COSMOS\\live --gate
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

SCHEMA = "cosmos-groq-rail/1"
WORKER = "cosmos-groq-rail"
LINK_ID = "groq-api"
BASE = "https://api.groq.com/openai/v1"
KEY_NAME = "groq_api_key.txt"
SPEC_NAME = "groq_rail.json"
PROBE_NAME = "groq_rail_probe.json"
SRC = "core"
DST = "models"
DEFAULT_MODEL = "openai/gpt-oss-20b"
CHAT_PATH = "/chat/completions"
MODELS_PATH = "/models"
# Vendor docs: gpt-oss supports low|medium|high; medium is their default.
# Cheap reasoning uses low.
DEFAULT_REASONING = "low"
DEFAULT_MAX_COMPLETION = 1024
GATE_MAX_COMPLETION = 256
UA = "COSMOS-groq-rail/1 (groq-api; keithbbf-gif/cosmos)"
VENDOR_DOCS = "https://console.groq.com/docs/api-reference#chat-create"
VENDOR_MODELS = "https://console.groq.com/docs/models"
# Guides + tutorials 01–10. Pointer, not a COSMOS rewrite (Keith 2026-09-04).
VENDOR_COOKBOOK = "https://github.com/groq/groq-api-cookbook"
# Org-wide RPM/RPD/TPM/TPD (+ ITPM/OTPM if the Console hover shows a split).
# Docs table is a high-level summary; live cap is settings/limits + headers.
VENDOR_LIMITS = "https://console.groq.com/docs/rate-limits"
VENDOR_LIMITS_LIVE = "https://console.groq.com/settings/limits"
# Vendor 2026-09-04: *-requests is RPD, *-tokens is TPM. retry-after only on 429.
RATE_HEADER_UNIT = {
    "x-ratelimit-limit-requests": "RPD",
    "x-ratelimit-remaining-requests": "RPD",
    "x-ratelimit-reset-requests": "RPD",
    "x-ratelimit-limit-tokens": "TPM",
    "x-ratelimit-remaining-tokens": "TPM",
    "x-ratelimit-reset-tokens": "TPM",
    "retry-after": "s",
}
# Catalog 2026-09-04 (console.groq.com/docs/models). Production vs Preview
# is the vendor split; Preview may be discontinued at short notice.
PRODUCTION_CHAT = frozenset({
    "openai/gpt-oss-20b",    # ~1000 t/s  $0.075 / $0.30  cheap default
    "openai/gpt-oss-120b",   # ~500 t/s   $0.15 / $0.60
})
PREVIEW_CHAT = frozenset({
    "openai/gpt-oss-safeguard-20b",
    "qwen/qwen3.6-27b",
    "qwen/qwen3.8-27b",
})
CHEAP_MODELS = PRODUCTION_CHAT | PREVIEW_CHAT
# Featured systems (tool-using). Not the cheap-reasoning default. Not Flex.
COMPOUND_SYSTEMS = frozenset({"groq/compound", "groq/compound-mini"})
# ARCH §4.3 E: Mixtral dead. Llama 3.1 8B / 3.3 70B are Production but
# Enterprise ContactSales — not the $0 Free cheap-reasoning pin.
_DEAD_EXACT = frozenset({
    "mixtral-8x7b-32768",
    "mixtral-8x7b",
})


class GroqRailError(RuntimeError):
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
        "reasoning_effort": DEFAULT_REASONING,
        "timeout_s": 45,
        "vendor_docs": VENDOR_DOCS,
        "vendor_models": VENDOR_MODELS,
        "vendor_cookbook": VENDOR_COOKBOOK,
        "vendor_limits": VENDOR_LIMITS,
        "vendor_limits_live": VENDOR_LIMITS_LIVE,
        "note": (
            "GroqCloud chat-create. Cheap reasoning. Not Grok. Not Flex. "
            "Production default openai/gpt-oss-20b. Catalog "
            "console.groq.com/docs/models. Cookbook github.com/groq/"
            "groq-api-cookbook is a research pointer, not a rewrite. "
            "Rate limits org-wide; bind x-ratelimit-* (requests=RPD, "
            "tokens=TPM) not the docs table. Bind response.model. "
            "Key never printed."
        ),
    }


def model_refused(model: str) -> str | None:
    """Typed refusal for dead / wrong-endpoint ids. None = allowed."""
    m = (model or "").strip()
    if not m:
        return "empty model"
    ml = m.lower()
    if m in _DEAD_EXACT or "mixtral" in ml:
        return f"dead Mixtral id {m!r}"
    if ml.startswith("llama-3.") or ml.startswith("llama3-") or ml.startswith("llama3."):
        return f"Llama 3.x Enterprise/ContactSales — not Free cheap-reasoning {m!r}"
    if ml.startswith("whisper-"):
        return f"Whisper is STT not chat-create {m!r}"
    return None


def _pin_origin(spec: dict) -> dict:
    base = str(spec.get("base") or BASE).rstrip("/")
    if base != BASE:
        raise GroqRailError("BAD_SPEC", f"base {base!r} != {BASE!r} (vendor origin only)")
    spec["base"] = BASE
    kn = str(spec.get("key_name") or KEY_NAME)
    if kn != KEY_NAME:
        raise GroqRailError("BAD_SPEC", f"key_name {kn!r} != {KEY_NAME!r}")
    spec["key_name"] = KEY_NAME
    spec["src"] = str(spec.get("src") or SRC) or SRC
    spec["dst"] = str(spec.get("dst") or DST) or DST
    spec["rail_type"] = "API"
    spec["link_id"] = str(spec.get("link_id") or LINK_ID) or LINK_ID
    spec["metered_usd"] = float(spec.get("metered_usd") or 0.0)
    spec["budget_usd"] = float(spec.get("budget_usd") or 0.0)
    spec["policy_rank"] = int(spec.get("policy_rank") or 0)
    spec["timeout_s"] = int(spec.get("timeout_s") or 45)
    dm = str(spec.get("default_model") or DEFAULT_MODEL).strip() or DEFAULT_MODEL
    why = model_refused(dm)
    if why:
        raise GroqRailError("BAD_SPEC", why)
    spec["default_model"] = dm
    reff = str(spec.get("reasoning_effort") or DEFAULT_REASONING).strip() or DEFAULT_REASONING
    spec["reasoning_effort"] = reff
    spec["schema"] = SCHEMA
    spec["vendor_docs"] = VENDOR_DOCS
    spec["vendor_models"] = VENDOR_MODELS
    spec["vendor_cookbook"] = VENDOR_COOKBOOK
    spec["vendor_limits"] = VENDOR_LIMITS
    spec["vendor_limits_live"] = VENDOR_LIMITS_LIVE
    return spec


def merge_spec(overlay) -> dict:
    spec = default_spec()
    if overlay is None:
        return _pin_origin(spec)
    if not isinstance(overlay, dict):
        raise GroqRailError("BAD_SPEC", f"spec overlay is {type(overlay).__name__}")
    for k, v in overlay.items():
        spec[k] = v
    if spec.get("schema") != SCHEMA:
        raise GroqRailError("BAD_SPEC", f"spec schema {spec.get('schema')!r} != {SCHEMA}")
    if spec.get("rail_type") not in (None, "API"):
        raise GroqRailError(
            "BAD_SPEC", f"groq rail_type must be API, got {spec.get('rail_type')!r}")
    return _pin_origin(spec)


def load_spec(path: Path | None) -> dict:
    if path is None or not Path(path).exists():
        return default_spec()
    try:
        raw = Path(path).read_text(encoding="utf-8")
    except OSError as e:
        raise GroqRailError("BAD_SPEC", f"unreadable spec {path}: {e}") from e
    try:
        overlay = json.loads(raw)
    except ValueError as e:
        raise GroqRailError("BAD_SPEC", f"unparseable spec {path}: {e}") from e
    return merge_spec(overlay)


def write_spec(path: Path, spec: dict | None = None) -> dict:
    body = merge_spec(spec)
    body.pop("api_key", None)
    body.pop("key", None)
    body.pop("groq_api_key", None)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(body, indent=2, sort_keys=True,
                               ensure_ascii=False) + "\n",
                    encoding="utf-8")
    return body


def redact_key(key: str) -> str:
    k = (key or "").strip()
    if len(k) >= 4:
        return f"gsk_…{k[-4:]}"
    return "gsk_…????"


def read_key(key_path: Path | None) -> str | None:
    if key_path is None:
        return None
    p = Path(key_path)
    if not p.exists():
        return None
    try:
        text = p.read_text(encoding="utf-8").strip()
    except OSError:
        return None
    return text or None


def _http_kind(status: int) -> str:
    if status in (401, 403):
        return "AUTH_REQUIRED"
    if status in (-1,):
        return "UNREACHABLE"
    return "BROKE"


def _ratelimits(hdrs: dict) -> dict:
    """Persist vendor headers. *-requests = RPD, *-tokens = TPM, retry-after = s."""
    out = {}
    for k, v in (hdrs or {}).items():
        lk = str(k).lower()
        if lk.startswith("x-ratelimit-") or lk == "retry-after":
            out[lk] = v
            unit = RATE_HEADER_UNIT.get(lk)
            if unit:
                out[lk + "_unit"] = unit
    return out


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
    reasoning = msg.get("reasoning")
    if isinstance(reasoning, str) and reasoning.strip():
        return reasoning.strip()
    return ""


class GroqRail:
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
        ok = status == 200 and has
        kind = None if ok else _http_kind(status if status != 200 else 0)
        if status == 200 and not has:
            kind = "BROKE"
        rec = {
            "ok": ok,
            "http": status,
            "n_models": len(ids),
            "has_gpt_oss_20b": has,
            "model_ids": ids,
            "ratelimit": _ratelimits(hdrs),
            "kind": kind,
            "detail": (
                f"http={status} n={len(ids)} has {DEFAULT_MODEL}={has}"
            ),
        }
        self._last = rec
        return ok, rec["detail"]

    def dispatch(self, payload: dict) -> dict:
        payload = payload if isinstance(payload, dict) else {}
        model = str(payload.get("model") or self.spec["default_model"]).strip()
        why = model_refused(model)
        if why:
            return {"ok": False, "kind": "REFUSED", "detail": why,
                    "model_requested": model, "link_id": self.link_id}
        tier = payload.get("service_tier")
        if tier in ("flex", "performance"):
            return {"ok": False, "kind": "REFUSED",
                    "detail": f"service_tier={tier!r} is dark (Batch/Flex)",
                    "link_id": self.link_id}
        text = str(payload.get("text") or payload.get("prompt") or "").strip()
        messages = payload.get("messages")
        if not isinstance(messages, list) or not messages:
            if not text:
                return {"ok": False, "kind": "REFUSED",
                        "detail": "messages or text required",
                        "link_id": self.link_id}
            messages = [{"role": "user", "content": text}]
        max_c = payload.get("max_completion_tokens")
        if max_c is None:
            max_c = payload.get("max_tokens")  # accept alias; send the live name
        try:
            max_c = int(max_c) if max_c is not None else DEFAULT_MAX_COMPLETION
        except (TypeError, ValueError):
            max_c = DEFAULT_MAX_COMPLETION
        body = {
            "model": model,
            "messages": messages,
            "max_completion_tokens": max_c,
            "stream": False,
            "n": 1,
        }
        reff = payload.get("reasoning_effort", self.spec.get("reasoning_effort"))
        if reff and model.startswith("openai/gpt-oss"):
            body["reasoning_effort"] = str(reff)
        elif reff and model.startswith("qwen/"):
            body["reasoning_effort"] = str(reff)
        status, hdrs, obj = self._call("POST", CHAT_PATH, body)
        usage = obj.get("usage") if isinstance(obj, dict) else None
        response_model = obj.get("model") if isinstance(obj, dict) else None
        content = _message_text(obj if isinstance(obj, dict) else {})
        ok = status == 200 and bool(response_model)
        rec = {
            "ok": ok,
            "http": status,
            "kind": None if ok else _http_kind(status),
            "model_requested": model,
            "model": response_model,  # bind THIS
            "text": content[:4000],
            "usage": usage if isinstance(usage, dict) else {},
            "ratelimit": _ratelimits(hdrs),
            "id": obj.get("id") if isinstance(obj, dict) else None,
            "object": obj.get("object") if isinstance(obj, dict) else None,
            "link_id": self.link_id,
            "detail": (
                f"http={status} response_model={response_model!r}"
            ),
        }
        if not ok and rec["kind"] is None:
            rec["kind"] = "BROKE"
        self._last = rec
        return rec


def spec_path_for(paths) -> Path:
    return paths.config(SPEC_NAME)


def key_path_for(paths, spec: dict | None = None) -> Path:
    _ = spec
    return paths.config(KEY_NAME)


def probe_path_for(paths) -> Path:
    return paths.config(PROBE_NAME)


def register_groq_rail(registry, adapters: dict, spend_gate=None,
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
    rail = GroqRail(key_path, spec, http=http)
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
        raise GroqRailError(
            "REFUSED",
            "attach_to_kernel refuses authority LINK_REGISTERED until Kernel "
            "boot reattaches probes every boot (BACKLOG). Isolated --gate "
            "ledger only. Pass boot_compose=True only from Kernel.__init__.")
    if adapters is None:
        adapters = getattr(kernel, "adapters", None)
        if adapters is None:
            adapters = {}
            kernel.adapters = adapters
    return register_groq_rail(
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
        "kernel_attach": "BACKLOG",
    }
    try:
        attach_to_kernel(duck, {})
        rec["detail"] = "attach_to_kernel DID NOT refuse the authority ledger"
    except GroqRailError as e:
        rec["refused"] = e.kind == "REFUSED"
        rec["kind"] = e.kind
        rec["detail"] = str(e)
    return rec


def inspect_live_kernel(root) -> dict:
    out = {"opened": False, "groq_in_registry": None, "error": None}
    try:
        from cosmos_kernel import Kernel
        k = Kernel(root, worker="groq-rail-gate", read_only=True)
        out["opened"] = True
        out["tree_id"] = k.paths.sentinel.tree_id
        out["groq_in_registry"] = LINK_ID in k.registry.state()
        out["read_only"] = True
    except Exception as e:  # noqa: BLE001
        out["error"] = f"{type(e).__name__}: {e}"
    return out


def _iso_now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _compose_isolated(paths, spec, keyp, http):
    from cosmos_ledger import Ledger
    from cosmos_registry import Registry
    from cosmos_rails import Dispatcher
    from cosmos_spend import SpendGate

    adapters = {}
    gate_dir = paths.role("state", "groq_rail")
    gate_dir.mkdir(parents=True, exist_ok=True)
    led = Ledger(gate_dir / "gate.jsonl", b"groq-rail-gate", WORKER)
    reg = Registry(led)
    spend = SpendGate(led)
    attached = register_groq_rail(
        reg, adapters, spend_gate=spend, spec=spec, key_path=keyp, http=http)
    disp = Dispatcher(reg, adapters, led, spend=spend)
    return attached, adapters, disp, led, gate_dir


def gate(root: str | os.PathLike, *, http=None) -> dict:
    """Runtime-binding gate. Isolated ledger. Live GET /models + one chat-create.

    PASS iff GET /models http=200 AND openai/gpt-oss-20b in the list AND
    chat-create response.model == openai/gpt-oss-20b AND attach refused
    AND kernel_attached is false. rc=0 is not the proof;
    config/groq_rail_probe.json is.
    """
    from cosmos_paths import CosmosPaths

    paths = CosmosPaths(root)
    spec = load_spec(spec_path_for(paths))
    write_spec(spec_path_for(paths), spec)
    keyp = key_path_for(paths, spec)
    attached, adapters, disp, led, gate_dir = _compose_isolated(
        paths, spec, keyp, http)
    try:
        measured_rec = disp.registry.probe(attached["link_id"])
    except Exception as e:  # noqa: BLE001
        measured_rec = {"ok": False, "detail": f"{type(e).__name__}: {e}"}
    rail = adapters[attached["link_id"]]
    ident = rail.last_identity()
    if ident is None:
        ok, detail = rail.probe()
        ident = rail.last_identity()
        measured_rec = {"ok": ok, "detail": detail}
    chat = rail.dispatch({
        "text": "Reply with exactly GROQ_READY and nothing else.",
        "max_completion_tokens": GATE_MAX_COMPLETION,
        "reasoning_effort": "low",
    })
    matrix = disp.registry.matrix()
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
        "expires_at": "2027-09-01",
        "spec_path": str(spec_path_for(paths)),
        "route": f"{attached['src']}->{attached['dst']}",
        "vendor_docs": VENDOR_DOCS,
        "vendor_models": VENDOR_MODELS,
        "vendor_cookbook": VENDOR_COOKBOOK,
        "vendor_limits": VENDOR_LIMITS,
        "vendor_limits_live": VENDOR_LIMITS_LIVE,
        "probe_ok": bool((measured_rec or {}).get("ok")),
        "probe_detail": (measured_rec or {}).get("detail"),
        "matrix": matrix,
        "dispatcher_constructed": True,
        "dispatcher_class": type(disp).__name__,
        "authority_ledger_written": False,
        "kernel_attached": False,
        "live_value": None,
        "gate": "FAIL",
        "stage6": {
            "kind": "satellite",
            "kernel_attach": "BACKLOG",
            "predicate": (
                "GET /models http=200 AND openai/gpt-oss-20b in list AND "
                "chat-create response.model==openai/gpt-oss-20b AND "
                "attach refused on authority"
            ),
        },
    }
    if ident:
        rec["models"] = {
            "http": ident.get("http"),
            "n_models": ident.get("n_models"),
            "has_gpt_oss_20b": ident.get("has_gpt_oss_20b"),
        }
    rec["chat"] = {
        "http": chat.get("http"),
        "model": chat.get("model"),
        "model_requested": chat.get("model_requested"),
        "ok": chat.get("ok"),
        "usage": chat.get("usage") or {},
        "ratelimit": chat.get("ratelimit") or {},
        "text_len": len(chat.get("text") or ""),
    }
    rec["live_value"] = {
        "response_model": chat.get("model"),
        "models_http": (ident or {}).get("http"),
        "has_gpt_oss_20b": (ident or {}).get("has_gpt_oss_20b"),
        "chat_http": chat.get("http"),
    }
    events = []
    try:
        events = [e.get("event") for e in led.verify()]
    except Exception as e:  # noqa: BLE001
        rec["ledger_error"] = f"{type(e).__name__}: {e}"
    rec["isolated_ledger_events"] = events
    rec["isolated_ledger"] = str(gate_dir / "gate.jsonl")
    rec["attach_refusal"] = refuse_live_authority_attach(paths)
    rec["live_kernel"] = inspect_live_kernel(root)
    models_ok = bool((ident or {}).get("has_gpt_oss_20b")) and (ident or {}).get("http") == 200
    chat_ok = chat.get("http") == 200 and chat.get("model") == DEFAULT_MODEL
    rec["identity_ok"] = models_ok and chat_ok
    rec["identity_why"] = (
        "ok" if rec["identity_ok"]
        else f"models={ident} chat_model={chat.get('model')!r} http={chat.get('http')}"
    )
    route_ok = rec["route"] == f"{SRC}->{DST}"
    attach_refused = bool(rec["attach_refusal"].get("refused"))
    if (rec["probe_ok"] and rec["identity_ok"] and route_ok and attach_refused
            and not rec["authority_ledger_written"]
            and rec["kernel_attached"] is False
            and attached["key_ok"]):
        rec["gate"] = "PASS"
    rec["proof"] = (
        f"groq-api probe_ok={rec['probe_ok']} "
        f"response_model={chat.get('model')!r} chat_http={chat.get('http')} "
        f"tree_id={rec['tree_id']} route={rec['route']} "
        f"attach_refused={attach_refused} kernel_attached={rec['kernel_attached']}"
    )
    probe_path = probe_path_for(paths)
    written = write_probe_record(probe_path, rec)
    written["probe_path"] = str(probe_path)
    gate_json = gate_dir / "gate.json"
    write_probe_record(gate_json, written)
    written["gate_json"] = str(gate_json)
    return written


def _selftest() -> int:
    import tempfile
    from cosmos_kernel import install, Kernel
    from cosmos_ledger import Ledger
    from cosmos_registry import Registry
    from cosmos_rails import Dispatcher
    from cosmos_spend import SpendGate

    results = []

    def check(label, fn):
        try:
            results.append((label, bool(fn()), ""))
        except Exception as e:  # noqa: BLE001
            results.append((label, False, f"{type(e).__name__}: {e}"))

    td = Path(tempfile.mkdtemp(prefix="cosmos_groq_rail_"))
    root = install(td / "live", tree_id="spike-groq-rail")
    from cosmos_paths import CosmosPaths
    paths = CosmosPaths(root)
    spec = write_spec(paths.config(SPEC_NAME))
    check("spec pins vendor docs/models/cookbook/limits (pointers not rewrite)",
          lambda: spec.get("vendor_docs") == VENDOR_DOCS
          and spec.get("vendor_models") == VENDOR_MODELS
          and spec.get("vendor_cookbook") == VENDOR_COOKBOOK
          and spec.get("vendor_limits") == VENDOR_LIMITS
          and spec.get("vendor_limits_live") == VENDOR_LIMITS_LIVE)
    hijack = merge_spec({
        "schema": SCHEMA,
        "vendor_cookbook": "https://example.invalid/fork",
        "vendor_limits": "https://example.invalid/limits",
    })
    check("merge_spec refuses cookbook/limits fork overlay (pin origin)",
          lambda: hijack.get("vendor_cookbook") == VENDOR_COOKBOOK
          and hijack.get("vendor_limits") == VENDOR_LIMITS
          and hijack.get("vendor_limits_live") == VENDOR_LIMITS_LIVE)
    check("x-ratelimit-limit-requests unit is RPD not RPM (vendor 2026-09-04)",
          lambda: RATE_HEADER_UNIT["x-ratelimit-limit-requests"] == "RPD"
          and RATE_HEADER_UNIT["x-ratelimit-limit-tokens"] == "TPM")
    keyp = paths.config(KEY_NAME)
    keyp.write_text("gsk_selftest_not_a_real_key_xxxx\n", encoding="utf-8")
    calls = []

    def fake_http(method, path, body=None):
        calls.append((method, path, body))
        headers = {
            "x-ratelimit-limit-requests": "30",
            "x-ratelimit-remaining-requests": "29",
        }
        if method == "GET" and path == MODELS_PATH:
            return 200, headers, {
                "object": "list",
                "data": [
                    {"id": "openai/gpt-oss-20b", "object": "model"},
                    {"id": "qwen/qwen3.8-27b", "object": "model"},
                ],
            }
        if method == "POST" and path == CHAT_PATH:
            assert body.get("stream") is False
            assert body.get("n") == 1
            assert "max_completion_tokens" in body
            assert "max_tokens" not in body
            assert body.get("service_tier") not in ("flex", "performance")
            return 200, headers, {
                "id": "chatcmpl-test",
                "object": "chat.completion",
                "model": body.get("model"),
                "choices": [{
                    "index": 0,
                    "message": {"role": "assistant", "content": "GROQ_READY"},
                    "finish_reason": "stop",
                }],
                "usage": {
                    "prompt_tokens": 8,
                    "completion_tokens": 2,
                    "total_tokens": 10,
                },
            }
        return 404, headers, {"error": path}

    rail = GroqRail(keyp, spec, http=fake_http)
    ok, detail = rail.probe()
    check("probe GET /models 200 has openai/gpt-oss-20b",
          lambda: ok and "openai/gpt-oss-20b" in detail and "http=200" in detail)
    chat = rail.dispatch({"text": "ping"})
    check("chat-create binds response.model not the prompt",
          lambda: chat["ok"] and chat["model"] == DEFAULT_MODEL
          and chat["text"] == "GROQ_READY"
          and chat["http"] == 200)
    check("chat-create uses max_completion_tokens not deprecated max_tokens",
          lambda: any(c[0] == "POST" and (c[2] or {}).get("max_completion_tokens")
                      for c in calls))
    check("x-ratelimit-* persisted with RPD unit",
          lambda: (chat.get("ratelimit") or {}).get("x-ratelimit-limit-requests") == "30"
          and (chat.get("ratelimit") or {}).get(
              "x-ratelimit-limit-requests_unit") == "RPD")

    dead = rail.dispatch({"model": "mixtral-8x7b-32768", "text": "x"})
    check("Mixtral is REFUSED",
          lambda: (not dead["ok"]) and dead["kind"] == "REFUSED")
    llama = rail.dispatch({"model": "llama-3.3-70b-versatile", "text": "x"})
    check("Llama 3.x is REFUSED",
          lambda: (not llama["ok"]) and llama["kind"] == "REFUSED")
    flex = rail.dispatch({"text": "x", "service_tier": "flex"})
    check("service_tier=flex is REFUSED (Batch/Flex dark)",
          lambda: (not flex["ok"]) and flex["kind"] == "REFUSED")
    whisper = rail.dispatch({"model": "whisper-large-v3", "text": "x"})
    check("Whisper on chat-create is REFUSED",
          lambda: (not whisper["ok"]) and whisper["kind"] == "REFUSED")

    def http_401(method, path, body=None):
        return 401, {}, {"error": {"message": "Invalid API Key",
                                   "code": "invalid_api_key"}}
    r401 = GroqRail(keyp, spec, http=http_401).dispatch({"text": "x"})
    check("401 is AUTH_REQUIRED",
          lambda: r401["kind"] == "AUTH_REQUIRED")

    def http_429(method, path, body=None):
        return 429, {
            "retry-after": "2",
            "x-ratelimit-remaining-requests": "0",
        }, {"error": "rate"}
    r429 = GroqRail(keyp, spec, http=http_429).dispatch({"text": "x"})
    check("429 is BROKE not UNREACHABLE",
          lambda: (not r429["ok"]) and r429["kind"] == "BROKE")
    check("429 persists retry-after (seconds; vendor only on 429)",
          lambda: (r429.get("ratelimit") or {}).get("retry-after") == "2"
          and (r429.get("ratelimit") or {}).get("retry-after_unit") == "s")

    led = Ledger(td / "n.jsonl", b"k", "core")
    reg = Registry(led)
    adapters = {}
    rec = register_groq_rail(
        reg, adapters, spend_gate=SpendGate(led), spec=spec,
        key_path=keyp, http=fake_http)
    check("register claims groq-api core->models",
          lambda: rec["link_id"] == LINK_ID and rec["dst"] == DST)
    reg.probe_all()
    disp = Dispatcher(reg, adapters, led, spend=SpendGate(led))
    routed = disp.dispatch(SRC, DST, {"text": "ping"})
    check("isolated Dispatcher chat-create binds response.model",
          lambda: routed["ok"] and routed.get("model") == DEFAULT_MODEL)

    g = gate(root, http=fake_http)
    check("gate PASS quotes response_model openai/gpt-oss-20b",
          lambda: g["gate"] == "PASS"
          and g["live_value"]["response_model"] == DEFAULT_MODEL)
    check("gate kernel_attached is false",
          lambda: g["kernel_attached"] is False)
    check("gate attach refused",
          lambda: g["attach_refusal"]["refused"] is True)
    check("gate does not write authority",
          lambda: g["authority_ledger_written"] is False)
    check("gate never emits the key value",
          lambda: g.get("key_value_emitted") is False
          and "gsk_selftest" not in json.dumps(g))

    k = Kernel(root, worker="groq-rail-selftest")
    _before = set(k.registry.state())
    refused = False
    try:
        attach_to_kernel(k, {})
    except GroqRailError as e:
        refused = e.kind == "REFUSED"
    check("attach_to_kernel refuses writing Kernel without boot_compose",
          lambda: refused and set(k.registry.state()) == _before)

    bad = [(l, e) for l, ok, e in results if not ok]
    for label, ok, err in results:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (groq-api chat-create; response.model bind; "
          "cookbook+limits pointers pinned; Mixtral/Llama3/flex REFUSED; "
          "429 retry-after; attach refused)"
          % ("PASS" if not bad else "FAIL", len(results)))
    return 0 if not bad else 1


def main() -> int:
    ap = argparse.ArgumentParser(
        prog="cosmos_groq_rail",
        description="COSMOS GroqCloud cheap-reasoning rail. chat-create "
                    "https://console.groq.com/docs/api-reference#chat-create "
                    "catalog https://console.groq.com/docs/models "
                    "cookbook https://github.com/groq/groq-api-cookbook "
                    "limits https://console.groq.com/docs/rate-limits")
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
            rail = GroqRail(key_path_for(paths, spec), spec)
            ok, detail = rail.probe()
            ident = rail.last_identity() or {}
            print(json.dumps({
                "ok": ok, "detail": detail,
                "http": ident.get("http"),
                "n_models": ident.get("n_models"),
                "has_gpt_oss_20b": ident.get("has_gpt_oss_20b"),
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
