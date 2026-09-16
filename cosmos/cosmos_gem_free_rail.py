#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_gem_free_rail - satellite API rail `gem-free` (AI Studio Developer API).

Google AI Studio free tier via `generativelanguage.googleapis.com`.
NOT Vertex (`gem-api` / Joanna). NOT `gemini.cmd`. Key:
live/config/google_api_key.txt (never printed). Billing-linked projects
typically return 429 RESOURCE_EXHAUSTED — fail-closed, never fake GREEN.

    py -3.14 cosmos\\cosmos_gem_free_rail.py --selftest
    py -3.14 cosmos\\cosmos_gem_free_rail.py --root V:\\A\\Ai\\COSMOS\\live --gate
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

SCHEMA = "cosmos-gem-free-rail/1"
WORKER = "cosmos-gem-free-rail"
LINK_ID = "gem-free"
BASE = "https://generativelanguage.googleapis.com/v1beta"
KEY_NAME = "google_api_key.txt"
ALT_KEY_NAME = "gemini_api_key.txt"
SPEC_NAME = "gem_free_rail.json"
PROBE_NAME = "gem_free_rail_probe.json"
SRC = "core"
DST = "models"
DEFAULT_MODEL = "gemini-2.5-flash"
GATE_PROMPT = "Reply with exactly GEM_FREE_READY and nothing else."
GATE_MAX_OUTPUT = 64
UA = "COSMOS-gem-free-rail/1 (gem-free; keithbbf-gif/cosmos)"
VENDOR_DOCS = "https://ai.google.dev/gemini-api/docs"
VENDOR_KEYS = "https://aistudio.google.com/apikey"
VENDOR_LIMITS = "https://aistudio.google.com/rate-limit"
# Keith 2026-09-04: billing-linked Free projects 429; credits depleted same symptom.
BILLING_429_NOTE = (
    "AI Studio free tier DEAD (HTTP 429 / RESOURCE_EXHAUSTED) — typical when "
    "billing is linked or daily quota is exhausted; not GREEN."
)


class GemFreeRailError(RuntimeError):
    """kind in {NO_KEY, BAD_SPEC, BAD_ROOT, UNREACHABLE, AUTH_REQUIRED, QUOTA_DEAD, BROKE, REFUSED}."""

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
        "timeout_s": 45,
        "vendor_docs": VENDOR_DOCS,
        "vendor_keys": VENDOR_KEYS,
        "vendor_limits": VENDOR_LIMITS,
        "note": (
            "Gemini Developer API (AI Studio). Free Flash RPD. Distinct from "
            "Vertex gem-api. Fail-closed on 429 when billing-linked. Key never "
            "printed."
        ),
    }


def _pin_origin(spec: dict) -> dict:
    base = str(spec.get("base") or BASE).rstrip("/")
    if base != BASE:
        raise GemFreeRailError("BAD_SPEC", f"base {base!r} != {BASE!r}")
    spec["base"] = BASE
    kn = str(spec.get("key_name") or KEY_NAME)
    if kn not in (KEY_NAME, ALT_KEY_NAME):
        raise GemFreeRailError("BAD_SPEC", f"key_name {kn!r} not Studio key file")
    spec["key_name"] = kn
    spec["src"] = str(spec.get("src") or SRC) or SRC
    spec["dst"] = str(spec.get("dst") or DST) or DST
    spec["rail_type"] = "API"
    spec["link_id"] = LINK_ID
    spec["schema"] = SCHEMA
    spec["default_model"] = str(spec.get("default_model") or DEFAULT_MODEL).strip() or DEFAULT_MODEL
    spec["timeout_s"] = int(spec.get("timeout_s") or 45)
    return spec


def merge_spec(overlay) -> dict:
    spec = default_spec()
    if overlay is None:
        return _pin_origin(spec)
    if not isinstance(overlay, dict):
        raise GemFreeRailError("BAD_SPEC", f"spec overlay is {type(overlay).__name__}")
    for k, v in overlay.items():
        spec[k] = v
    if spec.get("schema") != SCHEMA:
        raise GemFreeRailError("BAD_SPEC", f"spec schema {spec.get('schema')!r} != {SCHEMA}")
    return _pin_origin(spec)


def load_spec(path: Path | None) -> dict:
    if path is None or not Path(path).exists():
        return default_spec()
    try:
        raw = Path(path).read_text(encoding="utf-8")
    except OSError as e:
        raise GemFreeRailError("BAD_SPEC", f"unreadable spec {path}: {e}") from e
    try:
        overlay = json.loads(raw)
    except ValueError as e:
        raise GemFreeRailError("BAD_SPEC", f"unparseable spec {path}: {e}") from e
    return merge_spec(overlay)


def write_spec(path: Path, spec: dict | None = None) -> dict:
    body = merge_spec(spec)
    for k in ("api_key", "key", "google_api_key", "gemini_api_key"):
        body.pop(k, None)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(body, indent=2, sort_keys=True,
                               ensure_ascii=False) + "\n",
                    encoding="utf-8")
    return body


def redact_key(key: str) -> str:
    k = (key or "").strip()
    if len(k) >= 4:
        return f"AIza…{k[-4:]}"
    return "AIza…????"


def read_key(key_path: Path | None, paths=None) -> str | None:
    candidates = []
    if key_path is not None:
        candidates.append(Path(key_path))
    if paths is not None:
        candidates.append(paths.config(KEY_NAME))
        candidates.append(paths.config(ALT_KEY_NAME))
    seen = set()
    for p in candidates:
        ps = str(p)
        if ps in seen:
            continue
        seen.add(ps)
        if not p.exists():
            continue
        try:
            text = p.read_text(encoding="utf-8").strip()
        except OSError:
            continue
        if text:
            return text
    return None


def _http_kind(status: int, body: dict | None) -> str:
    if status == 429:
        return "QUOTA_DEAD"
    if status in (401, 403):
        return "AUTH_REQUIRED"
    if status == -1:
        return "UNREACHABLE"
    return "BROKE"


def _error_detail(status: int, body: dict | None) -> str:
    if status == 429:
        return BILLING_429_NOTE
    err = (body or {}).get("error") if isinstance(body, dict) else None
    if isinstance(err, dict):
        msg = str(err.get("message") or err.get("status") or "")[:240]
        if msg:
            return msg
    return f"http={status}"


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


def _response_text(body: dict) -> str:
    cands = body.get("candidates") if isinstance(body, dict) else None
    if not isinstance(cands, list) or not cands:
        return ""
    parts = ((cands[0] or {}).get("content") or {}).get("parts")
    if not isinstance(parts, list):
        return ""
    for part in parts:
        if isinstance(part, dict):
            t = part.get("text")
            if isinstance(t, str) and t.strip():
                return t.strip()
    return ""


def _response_model(body: dict, requested: str) -> str:
    if not isinstance(body, dict):
        return ""
    mv = body.get("modelVersion")
    if isinstance(mv, str) and mv.strip():
        return mv.strip()
    # Vendor may echo model id on some responses; never invent.
    rm = body.get("model")
    if isinstance(rm, str) and rm.strip():
        return rm.strip()
    return requested if requested else ""


class GemFreeRail:
    """Dispatcher adapter. probe + dispatch via generateContent."""

    kind = "API"

    def __init__(self, key_path: Path | str | None, spec: dict | None = None,
                 http=None, paths=None):
        self.spec = merge_spec(spec)
        self.key_path = Path(key_path) if key_path is not None else None
        self.paths = paths
        self.metered_usd = float(self.spec.get("metered_usd") or 0.0)
        self._http = http
        self.link_id = self.spec["link_id"]
        self._last = None

    def last_identity(self) -> dict | None:
        return self._last

    def _headers(self, key: str) -> dict:
        return {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "x-goog-api-key": key,
            "User-Agent": UA,
        }

    def _generate_path(self, model: str) -> str:
        m = (model or DEFAULT_MODEL).strip()
        return f"/models/{m}:generateContent"

    def _call(self, model: str, text: str, *, max_output: int):
        key = read_key(self.key_path, self.paths)
        if not key:
            return 401, {}, {"error": {"message": "NO_KEY", "status": "UNAUTHENTICATED"}}
        if self._http is not None:
            return self._http(model, text, max_output)
        path = self._generate_path(model)
        url = self.spec["base"] + path
        body = {
            "contents": [{"role": "user", "parts": [{"text": text}]}],
            "generationConfig": {"maxOutputTokens": max_output},
        }
        return _real_http("POST", url, body, self._headers(key),
                          float(self.spec["timeout_s"]))

    def probe(self):
        status, hdrs, body = self._call(
            self.spec["default_model"],
            "Reply with the single token PONG and nothing else.",
            max_output=16,
        )
        text = _response_text(body)
        model = _response_model(body, self.spec["default_model"])
        ok = status == 200 and bool(text.strip()) and bool(model.strip())
        kind = None if ok else _http_kind(status, body)
        detail = _error_detail(status, body) if not ok else (
            f"http=200 model={model!r} body_bytes={len(text.encode('utf-8'))}"
        )
        rec = {
            "ok": ok,
            "http": status,
            "model": model if ok else "",
            "text": text[:400],
            "body_bytes": len(text.encode("utf-8")) if text else 0,
            "kind": kind,
            "detail": detail,
            "model_source": "modelVersion" if body.get("modelVersion") else "requested",
        }
        self._last = rec
        return ok, rec["detail"]

    def dispatch(self, payload: dict) -> dict:
        payload = payload if isinstance(payload, dict) else {}
        model = str(payload.get("model") or self.spec["default_model"]).strip()
        text = str(payload.get("text") or payload.get("prompt") or "").strip()
        if not text:
            return {"ok": False, "kind": "REFUSED", "detail": "text or prompt required",
                    "link_id": self.link_id}
        max_out = payload.get("max_output_tokens") or payload.get("max_tokens")
        try:
            max_out = int(max_out) if max_out is not None else GATE_MAX_OUTPUT
        except (TypeError, ValueError):
            max_out = GATE_MAX_OUTPUT
        status, hdrs, body = self._call(model, text, max_output=max_out)
        content = _response_text(body)
        response_model = _response_model(body, model)
        ok = status == 200 and bool(response_model) and bool(content.strip())
        kind = None if ok else _http_kind(status, body)
        rec = {
            "ok": ok,
            "http": status,
            "kind": kind,
            "model_requested": model,
            "model": response_model if ok else "",
            "text": content[:4000],
            "body": content[:4000],
            "body_bytes": len(content.encode("utf-8")) if content else 0,
            "rc": 0 if ok else 2,
            "link_id": self.link_id,
            "detail": _error_detail(status, body) if not ok else (
                f"http=200 response_model={response_model!r}"
            ),
            "model_source": "modelVersion" if isinstance(body, dict)
            and body.get("modelVersion") else "requested",
        }
        if not ok and rec["kind"] is None:
            rec["kind"] = "BROKE"
        self._last = rec
        return rec


def spec_path_for(paths) -> Path:
    return paths.config(SPEC_NAME)


def key_path_for(paths, spec: dict | None = None) -> Path:
    spec = merge_spec(spec) if spec else default_spec()
    return paths.config(spec.get("key_name") or KEY_NAME)


def probe_path_for(paths) -> Path:
    return paths.config(PROBE_NAME)


def register_gem_free_rail(registry, adapters: dict, spend_gate=None,
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
    rail = GemFreeRail(key_path, spec, http=http, paths=paths)
    lid = rail.link_id
    if lid not in registry.state():
        registry.register(lid, spec["rail_type"], spec["src"], spec["dst"],
                          policy_rank=int(spec.get("policy_rank") or 0))
    registry.attach_probe(lid, rail.probe)
    adapters[lid] = rail
    key = read_key(Path(key_path) if key_path else None, paths)
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
        raise GemFreeRailError(
            "REFUSED",
            "attach_to_kernel refuses authority LINK_REGISTERED until Kernel "
            "boot reattaches probes every boot. Pass boot_compose=True only "
            "from Kernel.__init__.")
    if adapters is None:
        adapters = getattr(kernel, "adapters", None)
        if adapters is None:
            adapters = {}
            kernel.adapters = adapters
    return register_gem_free_rail(
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
    except GemFreeRailError as e:
        rec["refused"] = e.kind == "REFUSED"
        rec["kind"] = e.kind
        rec["detail"] = str(e)
    return rec


def _iso_now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def gate(root: str | os.PathLike, *, http=None) -> dict:
    from cosmos_paths import CosmosPaths

    paths = CosmosPaths(root)
    spec = write_spec(spec_path_for(paths))
    keyp = key_path_for(paths, spec)
    rail = GemFreeRail(keyp, spec, http=http, paths=paths)
    ok, detail = rail.probe()
    ident = rail.last_identity() or {}
    chat = rail.dispatch({"text": GATE_PROMPT, "max_output_tokens": GATE_MAX_OUTPUT})
    rec = {
        "schema": SCHEMA,
        "worker": WORKER,
        "gated_at": _iso_now(),
        "root": str(paths.root),
        "tree_id": paths.sentinel.tree_id,
        "link_id": LINK_ID,
        "key_last4": redact_key(read_key(keyp, paths) or ""),
        "key_ok": bool(read_key(keyp, paths)),
        "probe_ok": bool(ok),
        "probe_detail": detail,
        "billing_429_note": BILLING_429_NOTE,
        "chat": {
            "ok": chat.get("ok"),
            "http": chat.get("http"),
            "model": chat.get("model"),
            "kind": chat.get("kind"),
            "detail": chat.get("detail"),
        },
        "gate": "FAIL",
    }
    chat_ok = chat.get("http") == 200 and bool(chat.get("model"))
    if ok and chat_ok and rec["key_ok"]:
        rec["gate"] = "PASS"
    write_probe_record(probe_path_for(paths), rec)
    return rec


def _selftest() -> int:
    import tempfile
    from cosmos_kernel import install

    results = []

    def check(label, fn):
        try:
            results.append((label, bool(fn()), ""))
        except Exception as e:  # noqa: BLE001
            results.append((label, False, f"{type(e).__name__}: {e}"))

    td = Path(tempfile.mkdtemp(prefix="cosmos_gem_free_rail_"))
    root = install(td / "live", tree_id="spike-gem-free-rail")
    from cosmos_paths import CosmosPaths
    paths = CosmosPaths(root)
    spec = write_spec(spec_path_for(paths))
    check("spec pins gem-free + Studio vendor pointers",
          lambda: spec["link_id"] == LINK_ID and spec["default_model"] == DEFAULT_MODEL
          and spec.get("vendor_keys") == VENDOR_KEYS)
    keyp = paths.config(KEY_NAME)
    keyp.write_text("AIza_selftest_not_real_key_xxxx\n", encoding="utf-8")

    def fake_http(model, text, max_output):
        if "PONG" in text:
            return 200, {}, {
                "modelVersion": DEFAULT_MODEL,
                "candidates": [{"content": {"parts": [{"text": "PONG"}]}}],
            }
        if "GEM_FREE_READY" in text:
            return 200, {}, {
                "modelVersion": DEFAULT_MODEL,
                "candidates": [{"content": {"parts": [{"text": "GEM_FREE_READY"}]}}],
            }
        return 404, {}, {"error": {"message": "unexpected"}}

    rail = GemFreeRail(keyp, spec, http=fake_http, paths=paths)
    ok, detail = rail.probe()
    check("probe binds vendor modelVersion + body",
          lambda: ok and DEFAULT_MODEL in detail)
    chat = rail.dispatch({"text": GATE_PROMPT})
    check("dispatch binds response model + text",
          lambda: chat["ok"] and chat["model"] == DEFAULT_MODEL
          and chat["text"] == "GEM_FREE_READY")

    def http_429(model, text, max_output):
        return 429, {}, {
            "error": {
                "code": 429,
                "message": "Quota exceeded for quota metric "
                           "'GenerateContentRequestsPerDayPerProjectPerModel-FreeTier'.",
                "status": "RESOURCE_EXHAUSTED",
            }
        }

    dead = GemFreeRail(keyp, spec, http=http_429, paths=paths)
    ok429, det429 = dead.probe()
    check("429 is QUOTA_DEAD with billing-linked note (not GREEN)",
          lambda: (not ok429) and dead.last_identity().get("kind") == "QUOTA_DEAD"
          and "429" in BILLING_429_NOTE and "billing" in BILLING_429_NOTE.lower())

    no_key = GemFreeRail(None, spec, http=None, paths=None)
    ok_nk, _ = no_key.probe()
    check("missing key fails closed",
          lambda: not ok_nk and no_key.last_identity().get("kind") == "AUTH_REQUIRED")

    bad = [(l, e) for l, ok, e in results if not ok]
    for label, ok, err in results:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (gem-free rail)"
          % ("PASS" if not bad else "FAIL", len(results)))
    return 0 if not bad else 1


def main() -> int:
    ap = argparse.ArgumentParser(prog="cosmos_gem_free_rail")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--root")
    ap.add_argument("--gate", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return _selftest()
    if args.gate and args.root:
        rec = gate(args.root)
        print(json.dumps(rec, indent=2))
        return 0 if rec.get("gate") == "PASS" else 1
    ap.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
