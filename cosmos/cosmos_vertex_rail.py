#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_vertex_rail - COSMOS-native Vertex / Agent Platform Express rail.

Two wallets. Express generateContent. NOT AI Studio. NOT gemini.cmd.

Joanna (`gem-api`): `joanna.bbf@gmail.com` — OpenWork GEM. Key via
VERTEX_API_KEY / vertex_key.txt / vertex.json key_file.

Coding (`vertex-coding`): `orders.ggn@gmail.com` (console display Kelly
Gregory) — COSMOS / Crucible $300. API key (AQ.) via VERTEX_CODING_API_KEY /
vertex_coding_key.txt / vertex_coding.json key_file. ADC is the fallback,
not the daemon path. Never print the token.

Does not modify kernel/ledger/sched/service. No bts_* import.

    py -3.14 cosmos\\cosmos_vertex_rail.py --selftest
    py -3.14 cosmos\\cosmos_vertex_rail.py --root <live> --gate
    py -3.14 cosmos\\cosmos_vertex_rail.py --root <live> --gate-coding
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

SCHEMA = "cosmos-vertex-rail/1"
WORKER = "cosmos-vertex-rail"
LINK_ID = "gem-api"
ENDPOINT = (
    "https://aiplatform.googleapis.com/v1/publishers/google/models/"
    "{m}:generateContent"
)
SPEC_NAME = "vertex.json"
KEY_NAME = "vertex_key.txt"
CODING_SPEC_NAME = "vertex_coding.json"
CODING_KEY_NAME = "vertex_coding_key.txt"
CODING_LINK_ID = "vertex-coding"
CODING_ENV = "VERTEX_CODING_API_KEY"
DEFAULT_MODEL = "gemini-2.5-flash"
# Kelly / orders.ggn coding seat — Keith 2026-09-08 named 3.8 Flash.
CODING_DEFAULT_MODEL = "gemini-3.8-flash"
THINK_BUDGET = {
    "gemini-2.5-pro": 512,
    "gemini-2.5-flash": 1024,
    "gemini-flash-latest": 1024,
}
# Conservative USD / 1M tokens so the spend breaker can fire (UNPRICED = cap never fires).
USD_PER_M_IN = 0.30
USD_PER_M_OUT = 2.50


def price_usd(tokens: dict | None, prompt_chars: int = 0) -> float:
    """Never None. Missing usage → char estimate. Floor so a free 0.0 cannot skip the cap."""
    t = tokens if isinstance(tokens, dict) else {}
    tin = int(t.get("in") or 0)
    tout = int(t.get("out") or 0) + int(t.get("thinking") or 0)
    if tin <= 0:
        tin = max(1, int(prompt_chars) // 3)
    if tout <= 0:
        tout = 1
    usd = (tin / 1_000_000.0) * USD_PER_M_IN + (tout / 1_000_000.0) * USD_PER_M_OUT
    return round(max(usd, 0.0001), 6)


class VertexRailError(RuntimeError):
    """kind in {NO_KEY, BAD_SPEC, BAD_ROOT, UNREACHABLE, BROKE}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def default_spec() -> dict:
    return {
        "schema": SCHEMA,
        "link_id": LINK_ID,
        "rail_type": "API",
        "src": "core",
        "dst": "models",
        "endpoint": ENDPOINT,
        "default_model": DEFAULT_MODEL,
        "key_name": KEY_NAME,
        "account": "joanna.bbf@gmail.com",
        "project": "project-5a33f910-1251-4d6a-bf9",
        "location": "global",
        "do_not_activate": True,
        "timeout_s": 120,
        "note": (
            "Vertex Express. Existing Agent-Platform key. Do not Activate "
            "the Joanna billing account."
        ),
    }


def load_spec(paths) -> dict:
    spec = default_spec()
    cfg = paths.config(SPEC_NAME)
    if cfg.is_file():
        try:
            raw = json.loads(cfg.read_text(encoding="utf-8"))
        except (OSError, ValueError, UnicodeDecodeError) as e:
            raise VertexRailError("BAD_SPEC", f"{cfg} unreadable: {e}") from e
        if not isinstance(raw, dict):
            raise VertexRailError("BAD_SPEC", f"{cfg} is not an object")
        spec.update({k: v for k, v in raw.items() if v is not None})
    spec["schema"] = SCHEMA
    spec["link_id"] = LINK_ID
    spec["endpoint"] = ENDPOINT
    spec["key_name"] = KEY_NAME
    spec["timeout_s"] = int(spec.get("timeout_s") or 120)
    spec["default_model"] = str(
        spec.get("default_model") or DEFAULT_MODEL).strip() or DEFAULT_MODEL
    return spec


def key_path_for(paths, spec: dict | None = None) -> Path:
    spec = spec or load_spec(paths)
    local = paths.config(KEY_NAME)
    if local.is_file():
        return local
    kf = str(spec.get("key_file") or "").strip()
    if kf:
        p = Path(kf)
        if p.is_file():
            return p
    raise VertexRailError(
        "NO_KEY",
        f"no {KEY_NAME} under config/ and vertex.json key_file missing")


def load_coding_spec(paths) -> dict:
    """orders.ggn $300 coding/reasoning rail when `vertex_coding.json` exists.

    Absent file → Joanna fallback (current gem-api). Does not invent a
    project id. Does not steal Joanna's key.
    """
    cfg = paths.config(CODING_SPEC_NAME)
    if not cfg.is_file():
        spec = load_spec(paths)
        spec["role"] = "joanna-fallback"
        return spec
    try:
        raw = json.loads(cfg.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeDecodeError) as e:
        raise VertexRailError("BAD_SPEC", f"{cfg} unreadable: {e}") from e
    if not isinstance(raw, dict):
        raise VertexRailError("BAD_SPEC", f"{cfg} is not an object")
    spec = default_spec()
    spec.update({k: v for k, v in raw.items() if v is not None})
    spec["schema"] = SCHEMA
    spec["link_id"] = CODING_LINK_ID
    spec["endpoint"] = ENDPOINT
    spec["key_name"] = CODING_KEY_NAME
    spec["role"] = "coding"
    spec["do_not_activate"] = True
    if not str(spec.get("auth") or "").strip():
        spec["auth"] = "adc"
    spec["timeout_s"] = int(spec.get("timeout_s") or 120)
    spec["default_model"] = str(
        spec.get("default_model") or CODING_DEFAULT_MODEL).strip() or CODING_DEFAULT_MODEL
    if not str(spec.get("project") or "").strip():
        raise VertexRailError(
            "BAD_SPEC", f"{cfg} has no project — will not invent one")
    return spec


def _gcloud_cmd() -> str:
    win = Path(r"C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd")
    if win.is_file():
        return str(win)
    return "gcloud"


def _adc_bearer(*, env: dict | None = None) -> str:
    """OAuth access token. Never log the return value."""
    env = os.environ if env is None else env
    t = str(env.get("VERTEX_CODING_ADC_TOKEN") or "").strip().strip('"')
    if t:
        return t
    r = subprocess.run(
        [_gcloud_cmd(), "auth", "application-default", "print-access-token",
         "--quiet"],
        capture_output=True, text=True, timeout=45, errors="replace",
    )
    tok = (r.stdout or "").strip().split()[0] if r.returncode == 0 else ""
    if not tok:
        raise VertexRailError(
            "NO_KEY",
            "ADC missing — gcloud auth application-default login as "
            "orders.ggn@gmail.com (not joanna.bbf). Daemons use the API key.",
        )
    return tok


def _adc_url(spec: dict, model: str) -> str:
    proj = str(spec.get("project") or "").strip()
    loc = str(spec.get("location") or "global").strip() or "global"
    if not proj:
        raise VertexRailError("BAD_SPEC", "ADC Vertex URL needs project")
    return (
        "https://aiplatform.googleapis.com/v1/projects/%s/locations/%s/"
        "publishers/google/models/%s:generateContent" % (proj, loc, model)
    )


def key_path_for_coding(paths, spec: dict | None = None) -> Path:
    spec = spec or load_coding_spec(paths)
    if spec.get("role") != "coding":
        return key_path_for(paths, spec)
    if str(spec.get("auth") or "").strip().lower() == "adc":
        raise VertexRailError("NO_KEY", "coding rail is ADC — no API key file")
    local = paths.config(CODING_KEY_NAME)
    if local.is_file():
        return local
    kf = str(spec.get("key_file") or "").strip()
    if kf:
        p = Path(kf)
        if p.is_file():
            return p
    raise VertexRailError(
        "NO_KEY",
        f"no {CODING_KEY_NAME} under config/ and vertex_coding.json key_file missing")


def _read_key(key_path: Path | None, *, env: dict | None = None,
              coding: bool = False) -> str:
    env = os.environ if env is None else env
    names = (CODING_ENV,) if coding else ("VERTEX_API_KEY",)
    for n in names:
        k = str(env.get(n) or "").strip().strip('"')
        if k:
            return k
    if key_path is not None and Path(key_path).is_file():
        k = Path(key_path).read_text(encoding="utf-8").strip().strip('"')
        if k:
            return k
    raise VertexRailError(
        "NO_KEY",
        ("%s unset and key file empty" % (CODING_ENV if coding else "VERTEX_API_KEY")))


class VertexRail:
    """Express generateContent. http= is the test seam (no live vendor)."""

    def __init__(self, key_path, spec: dict, *, http=None, env=None):
        self.key_path = Path(key_path) if key_path else None
        self.spec = spec
        self.http = http
        self.env = env

    def ask(self, prompt: str, *, model: str | None = None) -> dict:
        model = str(model or self.spec.get("default_model") or DEFAULT_MODEL).strip()
        if not model:
            model = DEFAULT_MODEL
        body = {
            "contents": [{"role": "user", "parts": [{"text": str(prompt)}]}],
        }
        tb = THINK_BUDGET.get(model)
        if tb is not None:
            body["generationConfig"] = {
                "thinkingConfig": {"thinkingBudget": tb},
            }
        payload = json.dumps(body).encode("utf-8")
        if str(self.spec.get("auth") or "").strip().lower() == "adc":
            token = _adc_bearer(env=self.env)
            url = _adc_url(self.spec, model)
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + token,
            }
        else:
            key = _read_key(
                self.key_path, env=self.env,
                coding=self.spec.get("role") == "coding")
            url = ENDPOINT.format(m=model)
            headers = {
                "Content-Type": "application/json",
                "x-goog-api-key": key,
            }
        try:
            if self.http is not None:
                status, parsed = self.http("POST", url, body)
            else:
                req = urllib.request.Request(url, data=payload, headers=headers)
                timeout = int(self.spec.get("timeout_s") or 120)
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    status = getattr(resp, "status", 200) or 200
                    parsed = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            msg = e.read().decode("utf-8", errors="replace")[:200]
            return {
                "ok": False, "reason": f"HTTP_{e.code}", "text": "",
                "model": model, "via": "vertex", "detail": msg, "rc": 2,
            }
        except Exception as e:  # noqa: BLE001
            return {
                "ok": False, "reason": "UNREACHABLE", "text": "",
                "model": model, "via": "vertex",
                "detail": f"{type(e).__name__}: {e}"[:160], "rc": 2,
            }
        if status not in (200, 201) or not isinstance(parsed, dict):
            return {
                "ok": False, "reason": f"HTTP_{status}", "text": "",
                "model": model, "via": "vertex",
                "detail": "Vertex POST did not return a candidate object",
                "rc": 2,
            }
        cands = parsed.get("candidates") or []
        first = cands[0] if cands and isinstance(cands[0], dict) else {}
        content = first.get("content") if isinstance(first.get("content"), dict) else {}
        parts = content.get("parts") if isinstance(content.get("parts"), list) else []
        text = "".join(
            str(p.get("text") or "") for p in parts if isinstance(p, dict)
        ).strip()
        um = parsed.get("usageMetadata") if isinstance(
            parsed.get("usageMetadata"), dict) else {}
        tokens = {
            "in": um.get("promptTokenCount") or 0,
            "out": um.get("candidatesTokenCount") or 0,
            "thinking": um.get("thoughtsTokenCount") or 0,
        }
        if not text:
            return {
                "ok": False, "reason": "EMPTY", "text": "",
                "model": model, "via": "vertex",
                "detail": "Vertex returned no text",
                "tokens": tokens,
                "cost_usd": None,
                "rc": 2,
            }
        return {
            "ok": True, "reason": "OK", "text": text,
            "model": model, "via": "vertex",
            "tokens": tokens,
            "cost_usd": price_usd(tokens, len(prompt)),
            "rc": 0,
        }

    def dispatch(self, payload: dict) -> dict:
        prompt = (payload or {}).get("prompt") or ""
        kwargs = (payload or {}).get("kwargs") if isinstance(
            (payload or {}).get("kwargs"), dict) else {}
        model = (payload or {}).get("model") or kwargs.get("model")
        r = self.ask(prompt, model=model)
        usd = r.get("cost_usd")
        if r.get("ok") and usd is None:
            usd = price_usd(r.get("tokens"), len(str(prompt)))
        return {
            "ok": bool(r.get("ok")),
            "kind": "API" if r.get("ok") else (r.get("reason") or "BROKE"),
            "text": r.get("text") or "",
            "model": r.get("model"),
            "via": "vertex",
            "usd": usd,
            "detail": r.get("detail") or r.get("reason"),
            "reason": r.get("reason"),
            "rc": r.get("rc"),
            "node": "vertex",
            "tokens": r.get("tokens"),
        }


def rail_for(paths, *, http=None, env=None) -> VertexRail:
    spec = load_spec(paths)
    try:
        kp = key_path_for(paths, spec)
    except VertexRailError:
        kp = None
    return VertexRail(kp, spec, http=http, env=env)


def rail_for_coding(paths, *, http=None, env=None) -> VertexRail:
    """Coding/reasoning Vertex (`orders.ggn`). Joanna until vertex_coding.json is present."""
    spec = load_coding_spec(paths)
    if str(spec.get("auth") or "").strip().lower() == "adc":
        return VertexRail(None, spec, http=http, env=env)
    try:
        kp = key_path_for_coding(paths, spec)
    except VertexRailError:
        kp = None
    return VertexRail(kp, spec, http=http, env=env)


def attach_to_kernel(kernel, adapters: dict | None = None, http=None,
                     env=None, *, boot_compose: bool = False) -> dict:
    """Bind the native Express adapter. Does not LINK_REGISTER (gem-api may
    already be claimed by node_rails / bts_gem). Does not generateContent.

    Joanna stays `gem-api`. Optional `vertex-coding` binds only when
    live/config/vertex_coding.json exists — does not steal Joanna.
    """
    from cosmos_rail_base import _ledger_is_authority
    if _ledger_is_authority(kernel) and not boot_compose:
        raise VertexRailError(
            "BROKE",
            "attach_to_kernel refuses authority until Kernel boot_compose=True")
    if adapters is None:
        adapters = getattr(kernel, "adapters", None)
        if adapters is None:
            adapters = {}
            kernel.adapters = adapters
    rail = rail_for(kernel.paths, http=http, env=env)
    adapters[LINK_ID] = rail
    kernel.gem_rail = rail
    coding = rail_for_coding(kernel.paths, http=http, env=env)
    kernel.vertex_coding_rail = coding
    if coding.spec.get("role") == "coding":
        adapters[CODING_LINK_ID] = coding
    return {
        "link_id": LINK_ID,
        "adapter": True,
        "model": rail.spec.get("default_model"),
        "do_not_activate": bool(rail.spec.get("do_not_activate")),
        "registered": LINK_ID in getattr(kernel.registry, "state", lambda: {})(),
        "coding_role": coding.spec.get("role"),
        "coding_project": coding.spec.get("project"),
    }


def write_output(path: Path, rec: dict) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    text = rec.get("text") or ""
    if rec.get("ok") and text:
        path.write_text(text, encoding="utf-8")
        return
    body = {
        "ok": False,
        "kind": rec.get("reason") or "UNREACHABLE",
        "via": "vertex",
        "model": rec.get("model"),
        "detail": rec.get("detail") or "",
    }
    path.write_text(json.dumps(body, indent=1) + "\n", encoding="utf-8")


def _selftest() -> int:
    import tempfile

    from cosmos_kernel import install
    from cosmos_paths import CosmosPaths

    results = []

    def check(label, fn):
        try:
            results.append((label, bool(fn()), ""))
        except Exception as e:  # noqa: BLE001
            results.append((label, False, f"{type(e).__name__}: {e}"))

    td = Path(tempfile.mkdtemp(prefix="cosmos_vertex_rail_"))
    root = install(td / "live", tree_id="spike-vertex-rail")
    paths = CosmosPaths(root)
    keyp = paths.config(KEY_NAME)
    keyp.write_text("vertex-test-key-not-real\n", encoding="utf-8")
    cfg = paths.config(SPEC_NAME)
    cfg.write_text(json.dumps({
        "account": "joanna.bbf@gmail.com",
        "project": "project-5a33f910-1251-4d6a-bf9",
        "location": "global",
        "default_model": "gemini-2.5-flash",
        "do_not_activate": True,
    }), encoding="utf-8")

    spec = load_spec(paths)
    check("load_spec pins gem-api + Joanna project",
          lambda: spec["link_id"] == LINK_ID
          and spec["account"] == "joanna.bbf@gmail.com"
          and spec["project"] == "project-5a33f910-1251-4d6a-bf9"
          and spec["default_model"] == "gemini-2.5-flash")
    check("key_path is runtime config vertex_key.txt",
          lambda: key_path_for(paths, spec) == keyp)
    from cosmos_kernel import Kernel
    k = Kernel(root, worker="vertex-attach")
    att = attach_to_kernel(k, boot_compose=True)
    check("boot_compose binds gem-api adapter without generateContent",
          lambda: att.get("link_id") == LINK_ID
          and att.get("adapter") is True
          and getattr(k, "gem_rail", None) is not None)
    check("no coding spec: vertex_coding_rail falls back to Joanna",
          lambda: att.get("coding_role") == "joanna-fallback"
          and getattr(k, "vertex_coding_rail", None) is not None
          and k.vertex_coding_rail.spec.get("project")
          == "project-5a33f910-1251-4d6a-bf9"
          and CODING_LINK_ID not in k.adapters)
    ccfg = paths.config(CODING_SPEC_NAME)
    ccfg.write_text(json.dumps({
        "account": "company-coding@example.invalid",
        "project": "company-coding-project",
        "location": "global",
        "default_model": "gemini-2.5-flash",
        "do_not_activate": True,
        "auth": "apikey",
    }), encoding="utf-8")
    ckey = paths.config(CODING_KEY_NAME)
    ckey.write_text("vertex-coding-test-key-not-real\n", encoding="utf-8")
    k2 = Kernel(root, worker="vertex-coding")
    att2 = attach_to_kernel(k2, boot_compose=True)
    check("coding spec binds vertex-coding without stealing gem-api",
          lambda: att2.get("coding_role") == "coding"
          and k2.adapters[LINK_ID].spec.get("project")
          == "project-5a33f910-1251-4d6a-bf9"
          and k2.adapters[CODING_LINK_ID].spec.get("project")
          == "company-coding-project"
          and k2.vertex_coding_rail.spec.get("role") == "coding")
    check("coding key is not Joanna's vertex_key.txt",
          lambda: key_path_for_coding(paths).name == CODING_KEY_NAME)

    calls = []

    def fake_http(method, url, body):
        calls.append((method, url, body))
        return 200, {
            "candidates": [{
                "content": {"parts": [{"text": "PONG-VERTEX"}]},
            }],
            "usageMetadata": {
                "promptTokenCount": 3,
                "candidatesTokenCount": 2,
                "thoughtsTokenCount": 0,
            },
        }

    rail = VertexRail(keyp, spec, http=fake_http)
    rec = rail.ask("Reply PONG-VERTEX and nothing else.", model="gemini-2.5-flash")
    check("fake HTTP ask ok via=vertex",
          lambda: rec.get("ok") is True and rec.get("via") == "vertex"
          and rec.get("text") == "PONG-VERTEX"
          and rec.get("model") == "gemini-2.5-flash")
    check("ok Vertex call is priced (cap can fire)",
          lambda: rec.get("cost_usd") is not None and rec.get("cost_usd") >= 0.0001)
    check("price_usd never None without tokens",
          lambda: price_usd(None, 99) >= 0.0001)
    check("POST hits Express generateContent",
          lambda: calls and calls[0][0] == "POST"
          and "aiplatform.googleapis.com" in calls[0][1]
          and "gemini-2.5-flash" in calls[0][1]
          and "generateContent" in calls[0][1])
    check("thinkingBudget set for flash",
          lambda: (calls[0][2].get("generationConfig") or {})
          .get("thinkingConfig", {}).get("thinkingBudget") == 1024)
    adc_calls = []

    def fake_adc(method, url, body):
        adc_calls.append((method, url, body))
        return 200, {
            "candidates": [{
                "content": {"parts": [{"text": "PONG-ADC"}]},
            }],
            "usageMetadata": {
                "promptTokenCount": 1,
                "candidatesTokenCount": 1,
                "thoughtsTokenCount": 0,
            },
        }

    adc_rail = VertexRail(None, {
        "role": "coding", "auth": "adc",
        "project": "company-coding-project",
        "location": "global",
        "default_model": "gemini-2.5-flash",
    }, http=fake_adc, env={"VERTEX_CODING_ADC_TOKEN": "test-adc-token-not-real"})
    adc_rec = adc_rail.ask("hi")
    check("ADC coding rail uses project-scoped generateContent",
          lambda: adc_rec.get("ok") is True
          and adc_calls
          and "/projects/company-coding-project/locations/global/" in adc_calls[0][1]
          and "generateContent" in adc_calls[0][1])

    outp = Path(td) / "out" / "result.json"
    write_output(outp, rec)
    check("write_output lands Vertex text",
          lambda: outp.read_text(encoding="utf-8") == "PONG-VERTEX")

    fail = VertexRail(keyp, spec, http=lambda *_a, **_k: (403, {"error": "blocked"}))
    bad = fail.ask("x")
    check("HTTP 403 is not ok", lambda: bad.get("ok") is False)
    failp = Path(td) / "out" / "fail.json"
    write_output(failp, bad)
    fail_obj = json.loads(failp.read_text(encoding="utf-8"))
    check("typed failure still writes Output JSON",
          lambda: fail_obj.get("ok") is False and fail_obj.get("via") == "vertex")

    env_rail = VertexRail(None, spec, http=fake_http,
                          env={"VERTEX_API_KEY": "from-env"})
    check("VERTEX_API_KEY env is enough without a file",
          lambda: env_rail.ask("hi").get("ok") is True)

    dispatched = rail.dispatch({"prompt": "PONG", "model": "gemini-2.5-flash"})
    check("dispatch shape matches NodeRail",
          lambda: dispatched.get("via") == "vertex"
          and dispatched.get("ok") is True
          and dispatched.get("kind") == "API")

    import re as _re
    src = Path(__file__).read_text(encoding="utf-8")
    check("no bts_ import",
          lambda: _re.search(r"^\s*(?:from|import)\s+bts_", src, _re.M) is None)

    bad_n = [(l, e) for l, ok, e in results if not ok]
    for l, ok, e in results:
        print(("  OK  " if ok else "  FAIL") + f" {l}" + (f"  {e}" if e else ""))
    print(f"{len(results) - len(bad_n)}/{len(results)} passed")
    return 1 if bad_n else 0


def _gate(root: str, *, coding: bool = False) -> int:
    from cosmos_paths import CosmosPaths
    paths = CosmosPaths(root)
    if coding:
        spec = load_coding_spec(paths)
        if spec.get("role") != "coding":
            print(json.dumps({
                "ok": False, "reason": "NO_CODING_SPEC",
                "detail": "vertex_coding.json missing — refusing to spend Joanna",
            }))
            return 2
        rail = rail_for_coding(paths)
        probe_name = "vertex_coding_rail_probe.json"
        key_name = CODING_KEY_NAME
    else:
        spec = load_spec(paths)
        rail = rail_for(paths)
        probe_name = "vertex_rail_probe.json"
        key_name = KEY_NAME
    nonce = datetime.now().astimezone().strftime("%Y%m%dT%H%M%S")
    rec = rail.ask(
        f"Reply with the single token VERTEX_OK_{nonce} and nothing else.",
        model=spec.get("default_model"),
    )
    rec["tree_id"] = paths.sentinel.tree_id
    rec["nonce"] = nonce
    rec["key_path_name"] = key_name
    rec["account"] = spec.get("account")
    rec["project"] = spec.get("project")
    out = paths.config(probe_name)
    body = {
        "ok": bool(rec.get("ok")),
        "via": rec.get("via"),
        "model": rec.get("model"),
        "reason": rec.get("reason"),
        "tree_id": rec.get("tree_id"),
        "nonce": nonce,
        "text_head": (rec.get("text") or "")[:80],
        "account": spec.get("account"),
        "project": spec.get("project"),
        "role": spec.get("role"),
        "detail": rec.get("detail") or "",
    }
    out.write_text(json.dumps(body, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({
        "ok": rec.get("ok"), "via": rec.get("via"),
        "model": rec.get("model"), "reason": rec.get("reason"),
        "tree_id": rec.get("tree_id"), "probe": str(out),
        "project": spec.get("project"), "account": spec.get("account"),
        "text_head": (rec.get("text") or "")[:80],
    }))
    return 0 if rec.get("ok") else 2


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="cosmos_vertex_rail")
    p.add_argument("--root", default="")
    p.add_argument("--selftest", action="store_true")
    p.add_argument("--gate", action="store_true")
    p.add_argument("--gate-coding", action="store_true")
    ns = p.parse_args(argv)
    if ns.selftest:
        return _selftest()
    if ns.gate or ns.gate_coding:
        if not ns.root:
            print("need --root", file=sys.stderr)
            return 2
        return _gate(ns.root, coding=bool(ns.gate_coding))
    p.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
