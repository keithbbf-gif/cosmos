#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_pay_gateway_fixes - 2026-10-18 docs-audit fixes. Direct-run, house style.

1 stream:true -> upstream non-streaming, OpenAI-compatible SSE back
2 $0 balance -> 402 insufficient_credits (never the free-capacity 429)
3 /v1/account promises + /v1/statement toll language gone
4 /v1/models lists only configured supply; unknown model -> 404 model_not_found
5 /v1/cloudflare/status needs the setup key
6 missing max_tokens -> min(4096, model max), clamped to balance, sent upstream
7 /v1/keys/rotate|revoke|cap reject empty/short/unknown key_hash (no lockout)
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import threading
import urllib.request
import urllib.error

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cosmos_pay_config as cfg
import cosmos_pay_gateway as gw
import cosmos_pay_meter as meter_mod

PASS = 0
FAIL = 0


def check(name: str, cond: bool) -> None:
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  PASS {name}")
    else:
        FAIL += 1
        print(f"  FAIL {name}")


class ORRail:
    """Stands in for OpenRouter (non-streaming only; stream() must not be used)."""
    def __init__(self):
        self.last = None

    def runsync(self, req):
        self.last = dict(req)
        return {"id": "gen-1", "created": 1760000000, "model": req.get("model"),
                "choices": [{"index": 0, "finish_reason": "stop",
                             "message": {"role": "assistant", "content": "hello world"}}],
                "usage": {"prompt_tokens": 10, "completion_tokens": 2, "total_tokens": 12}}

    def stream(self, req):
        raise AssertionError("upstream stream must not be called")


class Unconfigured:
    configured = False

    def runsync(self, req):
        raise gw.RailError("BAD_CONFIG")


if __name__ == "__main__":
    tmp = tempfile.mkdtemp()
    store = gw.Store(os.path.join(tmp, "keys.db"))
    meter = meter_mod.Meter(os.path.join(tmp, "meter.db"))
    rail = ORRail()
    models = {
        "or/cheap": {"endpoint": "or/cheap", "rail": "openrouter",
                     "prompt_per_m_usd": 1.0, "completion_per_m_usd": 10.0, "context_length": 128000},
        "or/small-ctx": {"endpoint": "or/small-ctx", "rail": "openrouter",
                         "prompt_per_m_usd": 1.0, "completion_per_m_usd": 10.0, "context_length": 1000},
        "qwen3-coder-30b-fp8": {"endpoint": "RUNPOD_ENDPOINT_ID_PLACEHOLDER", "rail": "runpod",
                                "price_per_m_usd": 0.297},
        "gemini-flash-vertex": {"rail": "vertex", "price_per_m_usd": 0.3},
        "claude-sonnet-bedrock": {"rail": "bedrock", "price_per_m_usd": 3.0},
    }
    config = json.loads(json.dumps(cfg.DEFAULT_CONFIG))
    config["free_tier"]["daily_face_usd"] = 0
    g = gw.PayGateway(store, meter, Unconfigured(), models, config, openrouter_rail=rail)
    api = {"founding": None, "webhooks": None, "stripe": None, "setup_key": "setup-xyz", "config": config}
    httpd = gw.ThreadingHTTPServer(("127.0.0.1", 0), gw.make_handler(g, api))
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    BASE = f"http://127.0.0.1:{httpd.server_address[1]}"

    def call(method, path, body=None, key=None, headers=None):
        h = {"Content-Type": "application/json"}
        if key:
            h["Authorization"] = f"Bearer {key}"
        h.update(headers or {})
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(BASE + path, data=data, headers=h, method=method)
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                return r.status, r.read().decode(), dict(r.headers)
        except urllib.error.HTTPError as e:
            return e.code, e.read().decode(), dict(e.headers)

    ah, key = store.create_account(plan="free")
    store.grant(ah, 1.0)
    zero_ah, zero_key = store.create_account(plan="free")
    paid0_ah, paid0_key = store.create_account(plan="verified_free")

    # ---- 1. streaming ----
    before = store.credits(ah)
    code, text, hdr = call("POST", "/v1/chat/completions",
                           {"model": "or/cheap", "stream": True, "stream_options": {"include_usage": True},
                            "max_tokens": 20, "messages": [{"role": "user", "content": "hi"}]}, key=key)
    check("stream 200", code == 200)
    check("stream content-type event-stream", "text/event-stream" in hdr.get("Content-Type", ""))
    check("upstream called without stream flag", rail.last is not None and "stream" not in rail.last
          and "stream_options" not in rail.last)
    lines = [ln[6:] for ln in text.split("\n") if ln.startswith("data: ")]
    check("ends with [DONE]", lines and lines[-1] == "[DONE]")
    chunks = [json.loads(x) for x in lines[:-1]]
    check("all chunks are chat.completion.chunk", chunks and all(c["object"] == "chat.completion.chunk" for c in chunks))
    check("first chunk carries role", chunks[0]["choices"][0]["delta"].get("role") == "assistant")
    text_out = "".join(c["choices"][0]["delta"].get("content") or "" for c in chunks if c["choices"])
    check("content reassembles to full text", text_out == "hello world")
    check("finish chunk has finish_reason + usage",
          chunks[-1]["choices"][0]["finish_reason"] == "stop" and chunks[-1]["usage"]["completion_tokens"] == 2)
    want = (10 * 1.0 + 2 * 10.0) / 1e6
    check("stream billed like non-stream", abs((before - store.credits(ah)) - want) < 1e-12)
    check("stream response has balance header", "x-cosmos-credit-balance" in {k.lower() for k in hdr})

    # stream errors keep real HTTP status
    code, text, _ = call("POST", "/v1/chat/completions",
                         {"model": "or/cheap", "stream": True, "messages": []}, key=zero_key)
    check("stream with $0 -> 402 JSON", code == 402 and json.loads(text)["error"]["code"] == "insufficient_credits")

    # ---- 2. out of credit ----
    for label, k in (("anonymous free $0", zero_key), ("verified_free $0", paid0_key)):
        code, text, _ = call("POST", "/v1/chat/completions",
                             {"model": "or/cheap", "messages": [{"role": "user", "content": "x"}]}, key=k)
        err = json.loads(text).get("error", {})
        check(f"{label} -> 402 insufficient_credits", code == 402 and err.get("code") == "insufficient_credits")
        check(f"{label} message points to pricing", "https://tokenctr.com/pricing.html" in err.get("message", ""))
        check(f"{label} no free-capacity/$10 copy", "free capacity" not in text and "$10" not in text)

    # ---- 3. promises / statement ----
    code, text, _ = call("GET", "/v1/account", key=key)
    check("account 200", code == 200)
    check("no 'free forever'/'toll-free' promises", "free forever" not in text and "toll" not in text.lower())
    code, text, _ = call("GET", "/v1/statement", key=key)
    st = json.loads(text)
    check("statement 200 without toll", code == 200 and "toll" not in st and "credit_events" in st)
    check("statement usage counts the run", st["usage"]["runs"] >= 1 and st["usage"]["spent_usd"] > 0)

    # ---- 4. models ----
    code, text, _ = call("GET", "/v1/models", key=key)
    ids = {m["id"] for m in json.loads(text)["data"]}
    check("models lists configured supply", ids == {"or/cheap", "or/small-ctx"})
    code, _, _ = call("GET", "/v1/models/claude-sonnet-bedrock", key=key)
    check("unsupplied model detail -> 404", code == 404)
    for mid in ("nope/nothing", "qwen3-coder-30b-fp8", "gemini-flash-vertex"):
        code, text, _ = call("POST", "/v1/chat/completions", {"model": mid, "messages": []}, key=key)
        check(f"{mid} -> 404 model_not_found", code == 404 and json.loads(text)["error"]["code"] == "model_not_found")

    # ---- 5. cloudflare status ----
    code, _, _ = call("GET", "/v1/cloudflare/status")
    check("cloudflare status anonymous -> 404", code == 404)
    code, _, _ = call("GET", "/v1/cloudflare/status", headers={"X-Setup-Key": "wrong"})
    check("cloudflare status wrong setup key -> 404", code == 404)
    code, _, _ = call("GET", "/v1/cloudflare/status", headers={"X-Setup-Key": "setup-xyz"})
    check("cloudflare status with setup key -> 200", code == 200)

    # ---- 6. missing max_tokens ----
    rich_ah, rich_key = store.create_account(plan="free")
    store.grant(rich_ah, 5.0)
    g.chat(rich_key, {"model": "or/cheap", "messages": [{"role": "user", "content": "hi"}]})
    check("default max_tokens 4096 sent upstream", rail.last.get("max_tokens") == 4096)
    g.chat(rich_key, {"model": "or/small-ctx", "messages": [{"role": "user", "content": "hi"}]})
    check("capped at model max", rail.last.get("max_tokens") == 1000)
    g.chat(rich_key, {"model": "or/cheap", "max_tokens": 7, "messages": [{"role": "user", "content": "hi"}]})
    check("explicit max_tokens untouched", rail.last.get("max_tokens") == 7)
    poor_ah, poor_key = store.create_account(plan="free")
    store.grant(poor_ah, 0.001)  # 4096 out tokens at $10/M = $0.04 > balance
    code, out, _ = g.chat(poor_key, {"model": "or/cheap", "messages": [{"role": "user", "content": "hi"}]})
    mt = rail.last.get("max_tokens")
    check("small balance -> 200 with clamped max_tokens", code == 200 and isinstance(mt, int) and 16 <= mt < 4096)
    check("clamped reserve fits balance", store.credits(poor_ah) >= 0)
    dust_ah, dust_key = store.create_account(plan="free")
    store.grant(dust_ah, 0.00001)
    code, out, _ = g.chat(dust_key, {"model": "or/cheap", "messages": [{"role": "user", "content": "hi"}]})
    check("dust balance -> 402", code == 402 and out["error"]["code"] == "insufficient_credits")
    code, out, _ = g.chat(poor_key, {"model": "or/cheap", "max_tokens": 100000,
                                     "messages": [{"role": "user", "content": "hi"}]})
    check("explicit max_tokens over balance -> 402", code == 402)

    # ---- 7. key rotate/revoke safety ----
    k_ah, k1 = store.create_account(plan="free")
    k2 = store.issue_key(k_ah, "second")
    for path in ("/v1/keys/rotate", "/v1/keys/revoke", "/v1/keys/cap"):
        for bad in ("", "...", "abc", "zzzzzzzzzzzz", "0000000000000000"):
            code, _, _ = call("POST", path, {"key_hash": bad, "daily_cap_usd": 1}, key=k1)
            if code != 400:
                break
        check(f"{path} rejects empty/short/unknown key_hash with 400", code == 400)
        code, _, _ = call("POST", path, {}, key=k1)
        check(f"{path} rejects missing key_hash with 400", code == 400)
    check("both keys still live", store.account_for_key(k1) and store.account_for_key(k2))
    shown = [k["key_hash"] for k in store.keys_for(k_ah)]
    k1_hash = store.hash_key(k1)
    code, text, _ = call("POST", "/v1/keys/rotate", {"key_hash": k1_hash[:12] + "..."}, key=k1)
    new = json.loads(text).get("key", "")
    check("rotate by displayed prefix -> 200", code == 200 and new.startswith("ck_"))
    check("rotated key revoked", not store.account_for_key(k1))
    check("new key works (no lockout)", bool(store.account_for_key(new)))
    check("other key untouched", bool(store.account_for_key(k2)))
    code, text, _ = call("POST", "/v1/keys/revoke", {"key_hash": k2}, key=new)
    check("revoke by raw key -> revoked", code == 200 and json.loads(text)["revoked"] is True)
    check("revoke left caller key alive", bool(store.account_for_key(new)))

    # ---- SSE helper unit ----
    sse = gw.completion_to_sse({"choices": [{"message": {"content": "x" * 1200}}], "usage": {"prompt_tokens": 1}}, "m")
    check("long text split into chunks", sum(1 for s in sse if '"content": "x' in s) == 3)
    check("tool_calls get an index", '"index": 0' in "".join(gw.completion_to_sse(
        {"choices": [{"message": {"tool_calls": [{"id": "t", "type": "function",
                                                  "function": {"name": "f", "arguments": "{}"}}]},
                      "finish_reason": "tool_calls"}]}, "m")))

    httpd.shutdown()
    print(f"\n{PASS} pass, {FAIL} fail")
    sys.exit(1 if FAIL else 0)
