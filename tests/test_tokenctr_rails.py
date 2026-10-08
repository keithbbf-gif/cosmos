#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PayGateway resale dispatch. Fakes only. No vendor network.

vertex, bedrock, openrouter, and azure do not fall through to RunPod.
A missing key or endpoint is 503 and writes no meter event.
A priced usage block settles face credits the same way RunPod does.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import urllib.request
from pathlib import Path

_TOKENCTR = Path(__file__).resolve().parents[1] / "tokenctr"
_GATEWAY_PY = _TOKENCTR / "cosmos_pay_gateway.py"
_WIZARD_PY = _TOKENCTR / "cosmos_pay_wizard.py"

# Isolate before import so this file does not open a live secrets.json.
os.environ["COSMOS_PAY_ROOT"] = tempfile.mkdtemp(prefix="c4-token-rails-")
sys.path.insert(0, str(_TOKENCTR))

import cosmos_pay_azure_rail as azure_rail  # noqa: E402
import cosmos_pay_bedrock_rail as bedrock_rail  # noqa: E402
import cosmos_pay_meter as meter_mod  # noqa: E402
import cosmos_pay_openrouter_rail as openrouter_rail  # noqa: E402
import cosmos_pay_vertex_rail as vtx  # noqa: E402

_IMPORT_FAIL_CLOSED = False
_IMPORT_ERROR = ""
try:
    import cosmos_pay_gateway as pay_gateway
except Exception as exc:
    pay_gateway = None  # type: ignore[assignment]
    _IMPORT_ERROR = f"{type(exc).__name__}: {exc}"
    lowered = _IMPORT_ERROR.lower()
    if "secret" in lowered or "fail-closed" in lowered:
        _IMPORT_FAIL_CLOSED = True
    else:
        raise


_PRICE = 0.297
_USAGE = {"prompt_tokens": 100, "completion_tokens": 20, "cached_tokens": 0}
_SEQ = 0


class _RunPod:
    def __init__(self) -> None:
        self.calls = 0

    def runsync(self, body: dict, timeout_s: int | None = None) -> dict:
        self.calls += 1
        return {
            "choices": [{"message": {"role": "assistant", "content": "pod"}}],
            "usage": dict(_USAGE),
        }

    def stream(self, body: dict):
        self.calls += 1
        yield {"usage": dict(_USAGE)}


def _block_network(monkeypatch) -> None:
    def _blocked(*_args, **_kwargs):
        raise AssertionError("network attempted")

    monkeypatch.setattr(urllib.request, "urlopen", _blocked)


def _books():
    global _SEQ
    _SEQ += 1
    root = Path(os.environ["COSMOS_PAY_ROOT"]) / f"case-{_SEQ}"
    root.mkdir(parents=True, exist_ok=True)
    assert pay_gateway is not None
    store = pay_gateway.Store(str(root / "keys.db"))
    meter = meter_mod.Meter(str(root / "meter.db"))
    return store, meter


def _paid(store):
    account, key = store.create_account(plan="free")
    store.grant(account, 5.0)
    return account, key


def _registry(rail: str) -> dict:
    return {"m": {"rail": rail, "endpoint": "registry-ep", "price_per_m_usd": _PRICE}}


def _config() -> dict:
    return {"free_tier": {"daily_face_usd": 1.5}}


def _priced_body(_spec: dict) -> dict:
    return {
        "choices": [{"message": {"role": "assistant", "content": "ok"}}],
        "usage": dict(_USAGE),
    }


def _chat(gw, key: str, model: str = "m"):
    return gw.chat(key, {"model": model, "messages": [{"role": "user", "content": "x"}]})


def _settled(meter) -> list:
    return [event for event in meter.tail(20) if event.get("event") == "RUN_SETTLED"]


def test_resolve_source_names_each_rail() -> None:
    text = _GATEWAY_PY.read_text(encoding="utf-8")
    start = text.index("    def _resolve_rail")
    end = text.index("    def maybe_reload_models")
    branch = text[start:end]
    assert 'if rail_type == "vertex"' in branch
    assert "return self.vertex_rail" in branch
    assert 'if rail_type == "bedrock"' in branch
    assert "return self.bedrock_rail" in branch
    assert 'if rail_type == "openrouter"' in branch
    assert "return self.openrouter_rail" in branch
    assert 'if rail_type == "azure"' in branch
    assert "return self.azure_rail" in branch
    assert 'if rail_type == "runpod"' in branch
    assert "return self.rail" in branch
    assert "return None" in branch
    main_body = text[text.index("def main"):]
    assert "attach_rails(config, secrets)" in main_body
    wizard = _WIZARD_PY.read_text(encoding="utf-8")
    assert "lands with the rail" not in wizard
    assert "no SigV4 call" in wizard
    assert "Does not call the bedrock rail or SigV4." in wizard


def test_resolve_rail_does_not_fall_through() -> None:
    if pay_gateway is None:
        assert _IMPORT_FAIL_CLOSED, _IMPORT_ERROR
        return
    default = _RunPod()
    vertex = _RunPod()
    bedrock = _RunPod()
    router = _RunPod()
    azure = _RunPod()
    wired = pay_gateway.PayGateway(
        None, None, default, {}, {},
        vertex_rail=vertex, bedrock_rail=bedrock, openrouter_rail=router, azure_rail=azure,
    )
    assert wired._resolve_rail({"rail": "vertex"}) is vertex
    assert wired._resolve_rail({"rail": "bedrock"}) is bedrock
    assert wired._resolve_rail({"rail": "openrouter"}) is router
    assert wired._resolve_rail({"rail": "azure"}) is azure
    assert wired._resolve_rail({"rail": "runpod"}) is default
    assert wired._resolve_rail({}) is default

    stock = pay_gateway.PayGateway(None, None, default, {}, {})
    assert stock.vertex_rail is None
    assert stock.bedrock_rail is None
    assert stock.openrouter_rail is None
    assert stock.azure_rail is None
    assert stock._resolve_rail({"rail": "vertex"}) is None
    assert stock._resolve_rail({"rail": "bedrock"}) is None
    assert stock._resolve_rail({"rail": "openrouter"}) is None
    assert stock._resolve_rail({"rail": "azure"}) is None
    assert stock._resolve_rail({"rail": "runpod"}) is default
    assert stock._resolve_rail({}) is default
    assert default.calls == 0


def test_attach_rails_requires_config_fields() -> None:
    if pay_gateway is None:
        assert _IMPORT_FAIL_CLOSED, _IMPORT_ERROR
        return
    empty = pay_gateway.attach_rails({}, {})
    assert empty == {
        "vertex_rail": None,
        "bedrock_rail": None,
        "openrouter_rail": None,
        "azure_rail": None,
    }
    assert pay_gateway.attach_rails({"vertex": {"project_id": "p"}}, {})["vertex_rail"] is None
    wired = pay_gateway.attach_rails(
        {"vertex": {"project_id": "p", "region": "us-central1", "access_token": "tok-test"}},
        {},
    )
    assert isinstance(wired["vertex_rail"], vtx.VertexAIRail)
    from_secret = pay_gateway.attach_rails(
        {"vertex": {"project_id": "p"}},
        {"vertex_access_token": "tok-test"},
    )
    assert isinstance(from_secret["vertex_rail"], vtx.VertexAIRail)
    assert pay_gateway.attach_rails({}, {"bedrock_api_key": "AKIATEST"})["bedrock_rail"] is None
    assert openrouter_rail.from_config({"openrouter": {"api_key": "sk-test"}}) is None
    assert azure_rail.from_config({"azure": {"endpoint": "https://azure.invalid/chat"}}) is None
    got = pay_gateway.attach_rails(
        {
            "bedrock": {"api_key": "AKIATEST", "endpoint": "https://bedrock.invalid/invoke"},
            "openrouter": {"api_key": "sk-test", "endpoint": "https://openrouter.invalid/v1"},
            "azure": {"api_key": "az-test", "endpoint": "https://azure.invalid/chat"},
        },
        {},
    )
    assert isinstance(got["bedrock_rail"], bedrock_rail.BedrockRail)
    assert isinstance(got["openrouter_rail"], openrouter_rail.OpenRouterRail)
    assert isinstance(got["azure_rail"], azure_rail.AzureRail)


def test_seed_rows_without_endpoint_do_not_call_runpod(monkeypatch) -> None:
    if pay_gateway is None:
        assert _IMPORT_FAIL_CLOSED, _IMPORT_ERROR
        return
    _block_network(monkeypatch)
    seed = json.loads((_TOKENCTR / "models.seed.json").read_text(encoding="utf-8"))
    store, meter = _books()
    runpod = _RunPod()
    gw = pay_gateway.PayGateway(store, meter, runpod, seed, _config())
    _account, key = _paid(store)
    for model in ("gemini-flash-vertex", "claude-sonnet-bedrock"):
        code, body, _headers = _chat(gw, key, model)
        assert code == 503
        assert body["error"]["code"] == "no_supply"
    assert runpod.calls == 0
    assert _settled(meter) == []
    assert meter.tail(20) == []


def test_unconfigured_vertex_does_not_call_runpod(monkeypatch) -> None:
    if pay_gateway is None:
        assert _IMPORT_FAIL_CLOSED, _IMPORT_ERROR
        return
    _block_network(monkeypatch)
    store, meter = _books()
    runpod = _RunPod()
    hits: list = []

    def transport(spec: dict) -> dict:
        hits.append(spec)
        return _priced_body(spec)

    bare = vtx.VertexAIRail(project_id="", access_token="tok-test", transport=transport)
    gw = pay_gateway.PayGateway(
        store, meter, runpod, _registry("vertex"), _config(), vertex_rail=bare,
    )
    account, key = _paid(store)
    code, body, _headers = _chat(gw, key)
    assert code == 503
    assert body["error"]["code"] == "no_supply"
    assert runpod.calls == 0
    assert hits == []
    assert meter.tail(20) == []
    assert abs(store.credits(account) - 5.0) < 1e-8

    store2, meter2 = _books()
    runpod2 = _RunPod()
    missing = pay_gateway.PayGateway(store2, meter2, runpod2, _registry("vertex"), _config())
    account2, key2 = _paid(store2)
    code2, body2, _headers2 = _chat(missing, key2)
    assert code2 == 503 and body2["error"]["code"] == "no_supply"
    assert runpod2.calls == 0
    assert meter2.tail(20) == []
    assert store2.credits(account2) == 5.0


def test_google_is_not_a_named_rail(monkeypatch) -> None:
    if pay_gateway is None:
        assert _IMPORT_FAIL_CLOSED, _IMPORT_ERROR
        return
    _block_network(monkeypatch)
    store, meter = _books()
    runpod = _RunPod()
    gw = pay_gateway.PayGateway(store, meter, runpod, _registry("google"), _config())
    assert gw._resolve_rail({"rail": "google"}) is None
    account, key = _paid(store)
    code, body, _headers = _chat(gw, key)
    assert code == 503
    assert body["error"]["code"] == "no_supply"
    assert runpod.calls == 0
    assert meter.tail(20) == []
    assert abs(store.credits(account) - 5.0) < 1e-8


def test_unset_bedrock_openrouter_azure_do_not_call_runpod(monkeypatch) -> None:
    if pay_gateway is None:
        assert _IMPORT_FAIL_CLOSED, _IMPORT_ERROR
        return
    _block_network(monkeypatch)
    store, meter = _books()
    runpod = _RunPod()
    names = ("bedrock", "openrouter", "azure")
    models = {
        name: {"rail": name, "endpoint": "registry-ep", "price_per_m_usd": _PRICE}
        for name in names
    }
    gw = pay_gateway.PayGateway(store, meter, runpod, models, _config())
    assert gw.bedrock_rail is None
    assert gw.openrouter_rail is None
    assert gw.azure_rail is None
    account, key = _paid(store)
    for name in names:
        assert gw._resolve_rail({"rail": name}) is None
        code, body, _headers = _chat(gw, key, name)
        assert code == 503, name
        assert body["error"]["code"] == "no_supply", name
    assert runpod.calls == 0
    assert meter.tail(20) == []
    assert abs(store.credits(account) - 5.0) < 1e-8


def test_runpod_rail_still_settles(monkeypatch) -> None:
    if pay_gateway is None:
        assert _IMPORT_FAIL_CLOSED, _IMPORT_ERROR
        return
    _block_network(monkeypatch)
    store, meter = _books()
    runpod = _RunPod()
    gw = pay_gateway.PayGateway(store, meter, runpod, _registry("runpod"), _config())
    account, key = _paid(store)
    code, body, _headers = _chat(gw, key)
    assert code == 200
    assert body["choices"][0]["message"]["content"] == "pod"
    assert runpod.calls == 1
    settled = _settled(meter)
    assert len(settled) == 1
    assert settled[0]["cost"]["provenance"] == "measured"
    assert settled[0]["tokens"] == {"in": 100, "out": 20, "cached": 0}
    assert store.credits(account) < 5.0


def _refuse(monkeypatch, rail_name: str, rail) -> None:
    assert pay_gateway is not None
    _block_network(monkeypatch)
    store, meter = _books()
    runpod = _RunPod()
    gw = pay_gateway.PayGateway(
        store, meter, runpod, _registry(rail_name), _config(), **{f"{rail_name}_rail": rail},
    )
    account, key = _paid(store)
    code, body, _headers = _chat(gw, key)
    assert code == 503
    assert body["error"]["code"] == "no_supply"
    assert runpod.calls == 0
    assert meter.tail(20) == []
    assert abs(store.credits(account) - 5.0) < 1e-8


def test_bedrock_openrouter_azure_refuse_without_key_or_endpoint(monkeypatch) -> None:
    if pay_gateway is None:
        assert _IMPORT_FAIL_CLOSED, _IMPORT_ERROR
        return
    hits: list = []

    def transport(spec: dict) -> dict:
        hits.append(spec)
        return _priced_body(spec)

    cases = [
        ("bedrock", bedrock_rail.BedrockRail(api_key="", endpoint="https://bedrock.invalid/invoke", transport=transport)),
        ("bedrock", bedrock_rail.BedrockRail(api_key="AKIATEST", endpoint="", transport=transport)),
        ("bedrock", bedrock_rail.BedrockRail(api_key="AKIATEST", endpoint="https://bedrock.invalid/invoke")),
        ("openrouter", openrouter_rail.OpenRouterRail(api_key="", endpoint="https://openrouter.invalid/v1", transport=transport)),
        ("openrouter", openrouter_rail.OpenRouterRail(api_key="sk-test", endpoint="", transport=transport)),
        ("azure", azure_rail.AzureRail(api_key="", endpoint="https://azure.invalid/chat", transport=transport)),
        ("azure", azure_rail.AzureRail(api_key="az-test", endpoint="", transport=transport)),
    ]
    for rail_name, rail in cases:
        hits.clear()
        _refuse(monkeypatch, rail_name, rail)
        assert hits == []


def test_priced_transport_settles_like_runpod_and_skips_it(monkeypatch) -> None:
    if pay_gateway is None:
        assert _IMPORT_FAIL_CLOSED, _IMPORT_ERROR
        return
    _block_network(monkeypatch)
    store, meter = _books()
    runpod = _RunPod()
    base = pay_gateway.PayGateway(store, meter, runpod, _registry("runpod"), _config())
    base_account, base_key = _paid(store)
    assert _chat(base, base_key)[0] == 200
    assert runpod.calls == 1
    base_left = store.credits(base_account)
    base_cost = _settled(meter)[0]["cost"]["measured_usd"]

    makers = {
        "vertex": lambda transport: vtx.VertexAIRail(
            project_id="p", access_token="tok-test", transport=transport,
        ),
        "bedrock": lambda transport: bedrock_rail.BedrockRail(
            api_key="AKIATEST", endpoint="https://bedrock.invalid/invoke", transport=transport,
        ),
        "openrouter": lambda transport: openrouter_rail.OpenRouterRail(
            api_key="sk-test", endpoint="https://openrouter.invalid/v1", transport=transport,
        ),
        "azure": lambda transport: azure_rail.AzureRail(
            api_key="az-test", endpoint="https://azure.invalid/chat", transport=transport,
        ),
    }
    for rail_name, make in makers.items():
        hits: list = []

        def transport(spec: dict, _hits: list = hits) -> dict:
            _hits.append(spec["url"])
            return _priced_body(spec)

        store_i, meter_i = _books()
        spy = _RunPod()
        gw = pay_gateway.PayGateway(
            store_i, meter_i, spy, _registry(rail_name), _config(),
            **{f"{rail_name}_rail": make(transport)},
        )
        account, key = _paid(store_i)
        code, body, _headers = _chat(gw, key)
        assert code == 200, rail_name
        assert body["usage"]["prompt_tokens"] == 100
        assert spy.calls == 0, rail_name
        assert len(hits) == 1, rail_name
        assert "runpod" not in hits[0]
        settled = _settled(meter_i)
        assert len(settled) == 1
        assert settled[0]["cost"]["provenance"] == "measured"
        assert settled[0]["cost"]["measured_usd"] == base_cost
        assert settled[0]["tokens"] == {"in": 100, "out": 20, "cached": 0}
        assert store_i.credits(account) == base_left
        assert not any(event.get("event") == "RUN_FAILED" for event in meter_i.tail(20))
