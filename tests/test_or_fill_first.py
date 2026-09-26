#!/usr/bin/env py -3.14
"""OpenRouter fill_first: stick on key A, 402 rotates, second 429 rotates."""
from __future__ import annotations

import json
import os
import sys
import tempfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cosmos"))

import cosmos_openrouter_rail as railmod
from cosmos_openrouter_rail import OpenRouterRail
from cosmos_or_fill_first import (
    FillFirstError,
    _selftest,
    note_status,
    pick,
)


class Paths:
    def __init__(self, root: Path):
        self.root = root
        (root / "config").mkdir(exist_ok=True)
        (root / "state").mkdir(exist_ok=True)

    def role(self, name: str, *parts: str) -> Path:
        return self.root.joinpath(name, *parts)

    def config(self, name: str) -> Path:
        return self.root / "config" / name


def test_fill_first_selftest():
    assert _selftest() == 0


def test_rail_source_picks_fill_first():
    src = (ROOT / "cosmos" / "cosmos_openrouter_rail.py").read_text(encoding="utf-8")
    assert "from cosmos_or_fill_first import pick, view" in src
    assert "note_status(" in src
    assert "rail.paths = paths" in src
    assert src.count("def _fill_key") == 1
    assert src.count("chosen = pick(self.paths)") == 1


def test_pick_unmeasured_and_rotate_without_echo():
    p = Paths(Path(tempfile.mkdtemp(prefix="or_fill_")))
    rec = pick(p)
    assert rec["kind"] == "UNMEASURED"
    state = p.role("state") / "openrouter" / "fill_first.json"
    assert not state.exists()
    secret_a = "kA-pytest"
    secret_b = "kB-pytest"
    p.config("openrouter_api_key.txt").write_text(secret_a + "\n", encoding="utf-8")
    p.config("openrouter_api_key_2.txt").write_text(secret_b + "\n", encoding="utf-8")
    assert pick(p)["key_name"] == "openrouter_api_key.txt"
    note_status(p, 429, retry=True)
    assert pick(p)["key_name"] == "openrouter_api_key.txt"
    rotated = note_status(p, 429, retry=True)
    assert rotated["rotated"] is True
    assert rotated["key_name"] == "openrouter_api_key_2.txt"
    blob = json.dumps(rotated) + state.read_text(encoding="utf-8")
    assert secret_a not in blob and secret_b not in blob
    try:
        note_status(Paths(Path(tempfile.mkdtemp(prefix="or_fill_nokey_"))), 402)
    except FillFirstError as e:
        assert e.kind == "NO_KEYS"
    else:
        raise AssertionError("NO_KEYS")


def test_rail_fill_key_sticks_then_rotates():
    p = Paths(Path(tempfile.mkdtemp(prefix="or_fill_rail_")))
    secret_a = "kA-rail"
    secret_b = "kB-rail"
    path_a = p.config("openrouter_api_key.txt")
    path_b = p.config("openrouter_api_key_2.txt")
    path_a.write_text(secret_a + "\n", encoding="utf-8")
    path_b.write_text(secret_b + "\n", encoding="utf-8")
    rail = OpenRouterRail(path_a, None)
    rail.paths = p
    assert rail._fill_key() == secret_a
    rail._fill_note(429)
    assert rail._fill["rotated"] is False
    assert rail._fill_key() == secret_a
    rail._fill_note(429)
    assert rail._fill["rotated"] is True
    assert rail._fill["key_name"] == "openrouter_api_key_2.txt"
    assert rail._fill_key() == secret_b
    state = (p.role("state") / "openrouter" / "fill_first.json").read_text(encoding="utf-8")
    assert secret_a not in state and secret_b not in state
    shown = json.dumps(rail._fill)
    assert secret_a not in shown and secret_b not in shown


def _paths(tag: str) -> Paths:
    return Paths(Path(tempfile.mkdtemp(prefix=tag)))


def _put(paths: Paths, name: str, text: str) -> None:
    paths.config(name).write_text(text + "\n", encoding="utf-8")


def test_smoke_bearer_sequence_never_calls_network():
    """Live _call path: bearer follows fill_first. urllib is sealed."""
    secret_a = "smoke-file-a"
    secret_b = "smoke-file-b"
    secret_c = "smoke-file-c"
    env_token = "smoke-env-not-used"
    p = _paths("or_fill_smoke_")
    _put(p, "openrouter_api_key.txt", secret_a)
    _put(p, "openrouter_api_key_2.txt", secret_b)
    _put(p, "openrouter_api_key_3.txt", secret_c)
    rail = OpenRouterRail(p.config("openrouter_api_key.txt"), None)
    rail.paths = p
    codes = [429, 429, 200, 402, 200]
    seen = []

    def fake(method, url, body, headers, timeout_s):
        assert str(url).startswith("https://openrouter.ai/")
        seen.append(headers.get("Authorization"))
        code = codes[len(seen) - 1]
        if code == 200:
            return code, {}, {"ok": True}
        return code, {}, {"error": {"message": "limit"}}

    def sealed(*_a, **_k):
        raise AssertionError("live network")

    old_http = railmod._real_http
    old_open = urllib.request.urlopen
    old_env = os.environ.get("OPENROUTER_API_KEY")
    os.environ["OPENROUTER_API_KEY"] = env_token
    railmod._real_http = fake
    urllib.request.urlopen = sealed
    try:
        for code in codes:
            status, _hdrs, _obj = rail._call("POST", "/chat/completions", {"model": "x"})
            assert status == code
        assert seen == [
            "Bearer " + secret_a,
            "Bearer " + secret_a,
            "Bearer " + secret_b,
            "Bearer " + secret_b,
            "Bearer " + secret_c,
        ]
        state = (p.role("state") / "openrouter" / "fill_first.json").read_text(encoding="utf-8")
        blob = state + json.dumps(rail._fill)
        assert secret_a not in blob and secret_b not in blob and secret_c not in blob
        assert env_token not in blob
        assert rail._fill["key_name"] == "openrouter_api_key_3.txt"
        # Chosen file wins over the env token.
        solo = _paths("or_fill_env_")
        _put(solo, "openrouter_api_key.txt", secret_a)
        one = OpenRouterRail(solo.config("openrouter_api_key.txt"), None)
        one.paths = solo
        seen.clear()
        status, _hdrs, _obj = one._call("POST", "/chat/completions", {})
        assert status == 429
        assert seen == ["Bearer " + secret_a]
        # No files: env is the fallback, and pick still does not mkdir.
        bare = _paths("or_fill_envonly_")
        bare_rail = OpenRouterRail(bare.config("openrouter_api_key.txt"), None)
        bare_rail.paths = bare
        assert pick(bare)["kind"] == "UNMEASURED"
        assert not (bare.role("state") / "openrouter").exists()
        seen.clear()
        status, _hdrs, _obj = bare_rail._call("GET", "/models")
        assert status == 429
        assert seen == ["Bearer " + env_token]
    finally:
        railmod._real_http = old_http
        urllib.request.urlopen = old_open
        if old_env is None:
            os.environ.pop("OPENROUTER_API_KEY", None)
        else:
            os.environ["OPENROUTER_API_KEY"] = old_env


def test_smoke_dispatch_records_retry_then_rotate():
    secret_a = "smoke-disp-a"
    secret_b = "smoke-disp-b"
    p = _paths("or_fill_disp_")
    _put(p, "openrouter_api_key.txt", secret_a)
    _put(p, "openrouter_api_key_2.txt", secret_b)
    rail = OpenRouterRail(p.config("openrouter_api_key.txt"), None)
    rail.paths = p
    # The 429 that rotates is still sent with the old key. The next call moves.
    expect = [secret_a, secret_a, secret_b]
    n = {"i": 0}

    def fake(method, url, body, headers, timeout_s):
        i = n["i"]
        n["i"] += 1
        assert headers.get("Authorization") == "Bearer " + expect[i]
        return 429, {}, {"error": {"message": "limit"}}

    old_http = railmod._real_http
    old_open = urllib.request.urlopen
    railmod._real_http = fake
    urllib.request.urlopen = lambda *_a, **_k: (_ for _ in ()).throw(
        AssertionError("live network"))
    try:
        first = rail.dispatch({"text": "ping"}, paths=p)
        assert first["http"] == 429
        assert first["fill_first"]["rotated"] is False
        assert first["fill_first"]["retries"] == 1
        assert first["fill_first"]["key_name"] == "openrouter_api_key.txt"
        second = rail.dispatch({"text": "ping"}, paths=p)
        assert second["http"] == 429
        assert second["fill_first"]["rotated"] is True
        assert second["fill_first"]["key_name"] == "openrouter_api_key_2.txt"
        status, _hdrs, _obj = rail._call("POST", "/chat/completions", {})
        assert status == 429
        assert n["i"] == 3
        blob = json.dumps(first) + json.dumps(second) + json.dumps(rail._fill)
        assert secret_a not in blob and secret_b not in blob
    finally:
        railmod._real_http = old_http
        urllib.request.urlopen = old_open
