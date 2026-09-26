#!/usr/bin/env py -3.14
"""Live mouths use fill_first. Sealed HTTP. No real key, no network."""
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
from cosmos_dispatch_jobs import _openrouter_job
from cosmos_forge_bg import worker_main
from cosmos_kernel import Kernel, install
from cosmos_model_rater import ModelRaterError, refresh
from cosmos_openrouter_rail import OpenRouterRail
from cosmos_paths import CosmosPaths
from cosmos_service import Service

GEMMA = "google/gemma-4-26b-a4b-it:free"
FILE_A = "openrouter_api_key.txt"
FILE_B = "openrouter_api_key_2.txt"


class _Seal:
    def __init__(self, fake):
        self.fake = fake
        self.old_http = None
        self.old_open = None

    def __enter__(self):
        self.old_http = railmod._real_http
        self.old_open = urllib.request.urlopen
        railmod._real_http = self.fake
        old = self.old_open

        def guarded(req, *a, **k):
            url = getattr(req, "full_url", None) or str(req)
            if url.startswith(("http://127.0.0.1:", "http://localhost:")):
                return old(req, *a, **k)
            raise AssertionError("live network")

        urllib.request.urlopen = guarded
        return self

    def __exit__(self, *_exc):
        railmod._real_http = self.old_http
        urllib.request.urlopen = self.old_open
        return False


def _live(tag: str):
    td = Path(tempfile.mkdtemp(prefix=tag))
    root = install(td / "live", tree_id=tag.strip("_"))
    paths = CosmosPaths(root)
    return td, paths


def _put(paths, name: str, text: str) -> None:
    paths.config(name).write_text(text + "\n", encoding="utf-8")


def _env(token: str):
    old = os.environ.get("OPENROUTER_API_KEY")
    os.environ["OPENROUTER_API_KEY"] = token
    return old


def _restore_env(old) -> None:
    if old is None:
        os.environ.pop("OPENROUTER_API_KEY", None)
    else:
        os.environ["OPENROUTER_API_KEY"] = old


def test_dispatch_job_template_passes_paths():
    text = _openrouter_job(
        "gemma", "ping", GEMMA,
        Path("result.json"), Path("returns.json"), 30,
        None, None, Path("live"), Path("cosmos"),
    )
    assert "OpenRouterRail(paths.config(KEY_NAME), spec, paths=paths)" in text
    assert "}, paths=paths)" in text
    assert 'out["fill_first"]' in text
    assert "sk-" not in text


def test_forge_worker_sticks_then_rotates():
    _td, paths = _live("or_forge_")
    secret_a = "forge-file-a"
    secret_b = "forge-file-b"
    env_token = "forge-env-not-used"
    _put(paths, FILE_A, secret_a)
    _put(paths, FILE_B, secret_b)
    prompt = _td_file(paths.root.parent, "prompt.txt", "ping\n")
    seen = []

    def fake(method, url, body, headers, timeout_s):
        assert str(url).startswith("https://openrouter.ai/")
        seen.append(headers.get("Authorization"))
        return 429, {}, {"error": {"message": "limit"}}

    old = _env(env_token)
    try:
        with _Seal(fake):
            codes = []
            for i in range(3):
                out = paths.root.parent / f"out{i}.json"
                rc = worker_main([
                    "--worker", "--root", str(paths.root),
                    "--stage", "research", "--model", GEMMA,
                    "--prompt", str(prompt), "--out", str(out),
                ])
                codes.append(rc)
                blob = out.read_text(encoding="utf-8")
                assert secret_a not in blob and secret_b not in blob
                assert env_token not in blob
        assert codes == [1, 1, 1]
        assert seen == [
            "Bearer " + secret_a,
            "Bearer " + secret_a,
            "Bearer " + secret_b,
        ]
    finally:
        _restore_env(old)


def _td_file(directory: Path, name: str, text: str) -> Path:
    p = directory / name
    p.write_text(text, encoding="utf-8")
    return p


def test_model_rater_refresh_uses_the_pool():
    _td, paths = _live("or_rater_")
    secret_a = "rater-file-a"
    secret_b = "rater-file-b"
    _put(paths, FILE_A, secret_a)
    _put(paths, FILE_B, secret_b)
    seen = []

    def fake(method, url, body, headers, timeout_s):
        assert str(url).startswith("https://openrouter.ai/")
        seen.append(headers.get("Authorization"))
        return 429, {}, {"error": {"message": "limit"}}

    with _Seal(fake):
        for _ in range(3):
            try:
                refresh(paths)
            except ModelRaterError as e:
                assert e.kind == "BROKE"
            else:
                raise AssertionError("429 must surface as BROKE")
    assert seen == [
        "Bearer " + secret_a,
        "Bearer " + secret_a,
        "Bearer " + secret_b,
    ]
    state = (paths.role("state") / "openrouter" / "fill_first.json").read_text(
        encoding="utf-8")
    assert secret_a not in state and secret_b not in state
    assert FILE_B in state


def test_session_id_follows_the_key_file():
    _td, paths = _live("or_sid_")
    secret_a = "sid-file-a"
    secret_b = "sid-file-b"
    _put(paths, FILE_A, secret_a)
    _put(paths, FILE_B, secret_b)
    rail = OpenRouterRail(paths.config(FILE_A), None, paths=paths)
    codes = [200, 200, 402, 200]
    bodies = []

    def fake(method, url, body, headers, timeout_s):
        assert str(url).startswith("https://openrouter.ai/")
        assert str(headers.get("Authorization") or "").startswith("Bearer ")
        bodies.append(body)
        code = codes[len(bodies) - 1]
        if code == 200:
            return 200, {}, {
                "model": body.get("model"),
                "choices": [{"message": {"role": "assistant", "content": "ok"}}],
            }
        return code, {}, {"error": {"message": "limit"}}

    with _Seal(fake):
        for code in codes:
            rec = rail.dispatch({"text": "ping"}, paths=paths)
            assert rec["http"] == code
    sids = [b.get("session_id") for b in bodies]
    assert sids[0] == FILE_A
    assert sids[1] == sids[0]
    assert sids[2] == FILE_A
    assert sids[3] == FILE_B
    blob = json.dumps(sids)
    assert secret_a not in blob and secret_b not in blob
    assert all(FILE_A == s or FILE_B == s for s in sids)


def test_usage_route_sends_the_picked_file():
    td, paths = _live("or_usage_")
    secret_a = "usage-file-a"
    env_token = "usage-env-not-used"
    _put(paths, FILE_A, secret_a)
    _put(paths, FILE_B, "usage-file-b")
    seen = []

    def fake(method, url, body, headers, timeout_s):
        assert str(url).startswith("https://openrouter.ai/api/v1/generation")
        seen.append(headers.get("Authorization"))
        return 200, {}, {"data": {"id": "gen-smoke", "model": GEMMA}}

    k = Kernel(paths.root, worker="or-fill-usage")
    svc = Service(k, host="127.0.0.1", port=0)
    svc.serve_background()
    old = _env(env_token)
    try:
        with _Seal(fake):
            req = urllib.request.Request(
                f"http://127.0.0.1:{svc.port}/api/v1/usage",
                data=json.dumps({"action": "generation", "id": "gen-smoke"}).encode("utf-8"),
                method="POST",
            )
            req.add_header("Authorization", "Bearer " + svc.token)
            req.add_header("Content-Type", "application/json")
            with urllib.request.urlopen(req, timeout=20) as resp:
                raw = resp.read().decode("utf-8")
                status = resp.status
        assert status == 200
        assert seen == ["Bearer " + secret_a]
        assert secret_a not in raw and env_token not in raw
        state = (paths.role("state") / "openrouter" / "fill_first.json").read_text(
            encoding="utf-8")
        assert secret_a not in state and env_token not in state
        assert FILE_A in state
    finally:
        _restore_env(old)
        svc.shutdown()
        _ = td
