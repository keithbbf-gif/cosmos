#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Crucible critic composition — wallets, ANTHROPIC_OFF, 501 stays the default."""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "cosmos"))

from cosmos_crucible_critics import (  # noqa: E402
    GROK_SGH, GROK_CONSOLE, GEM, OA, ARGV_PROMPT_MAX, OA_TERRA_ID, VERTEX_SPEND,
    compose_crucible_critics, grok_sgh_env, grok_sgh_argv, attach_crucible_critics,
    make_grok_sgh_critic, make_oa_critic, CriticError,
)


class _Probe:
    kind = "API"
    metered_usd = 0.02

    def __init__(self, ok=True):
        self._ok = ok
        self.dispatched = []

    def probe(self):
        return self._ok, "ok" if self._ok else "UNREACHABLE"

    def dispatch(self, payload):
        self.dispatched.append(payload)
        return {"ok": True, "kind": "API", "text": "```json\n[]\n```"}


def test_grok_sgh_env_unsets_console_key():
    env = grok_sgh_env({"XAI_API_KEY": "xai-secret", "PATH": "/bin", "OTHER": "1"})
    assert "XAI_API_KEY" not in env
    assert env["OTHER"] == "1"
    argv = grok_sgh_argv("critique", r"C:\ws")
    assert argv[0] == "grok" and "--single" in argv
    assert argv[argv.index("-m") + 1] == "grok-4.6"
    assert argv[argv.index("--max-turns") + 1] == "3"
    assert "--cwd" in argv


def test_prefer_grok_sgh_over_console_same_family():
    k = SimpleNamespace(adapters={
        GROK_CONSOLE: _Probe(True),
        GEM: _Probe(True),
        OA: _Probe(True),
        "claude-cli": _Probe(True),
        "gw-api": _Probe(True),
    }, spend=None, paths=None, ledger=None)
    out = compose_crucible_critics(k, which=lambda n: r"C:\grok.exe" if n == "grok" else None)
    assert GROK_SGH in out
    assert GROK_CONSOLE not in out
    assert "gw-api" not in out
    assert "claude-cli" not in out
    # adapters["gem-api"] is bts_gem / Keith Studio — Crucible must not tap it.
    assert GEM not in out
    assert OA in out


def test_console_only_when_grok_cli_absent():
    k = SimpleNamespace(adapters={GROK_CONSOLE: _Probe(True), GEM: _Probe(False)},
                        spend=None, paths=None, ledger=None)
    out = compose_crucible_critics(k, which=lambda n: None)
    assert GROK_CONSOLE in out
    assert GROK_SGH not in out
    assert GEM not in out


def test_empty_compose_is_honest_501_pool():
    k = SimpleNamespace(adapters={}, spend=None, paths=None, ledger=None)
    out = compose_crucible_critics(k, which=lambda n: None)
    assert out == {}


def test_vertex_rail_injects_joanna_gem_family():
    class Fake:
        def dispatch(self, payload):
            assert "PACKET" in (payload or {}).get("prompt", "")
            return {"ok": True, "kind": "API", "usd": 0.0002,
                    "text": '```json\n[{"id":"gem-api-1","topic":"t","finding":"x","severity":"LOW"}]\n```'}

    k = SimpleNamespace(adapters={GROK_CONSOLE: _Probe(True)},
                        spend=None, paths=None, ledger=None)
    out = compose_crucible_critics(
        k, which=lambda n: None, vertex_rail=Fake())
    assert GEM in out and GROK_CONSOLE in out
    assert "gem-api-1" in out[GEM]("hello packet")


def test_oa_rail_injects_platform_api_family():
    class Fake:
        def dispatch(self, payload):
            assert (payload or {}).get("kwargs", {}).get("tier") == "terra"
            return {"ok": True, "kind": "API", "model": "gpt-5.6-terra",
                    "text": '```json\n[{"id":"oa-api-1","topic":"t","finding":"x","severity":"LOW"}]\n```'}

    k = SimpleNamespace(adapters={}, spend=None, paths=None, ledger=None)
    out = compose_crucible_critics(
        k, which=lambda n: None, oa_rail=Fake())
    assert OA in out
    assert "oa-api-1" in out[OA]("hello packet")


def test_grok_argv_does_not_carry_packet():
    seen = []

    class R:
        returncode = 0
        stdout = '```json\n[{"id":"grok-sgh-1","topic":"t"}]\n```'
        stderr = ""

    def fake_run(**kw):
        seen.append(kw["args"])
        return R()

    fn = make_grok_sgh_critic(
        work_dir=Path(tempfile.mkdtemp(prefix="cru_argv_")),
        run=fake_run, which=lambda n: r"C:\grok.exe")
    packet = "P" * 50_000
    text = fn(packet)
    assert "grok-sgh-1" in text
    argv = seen[0]
    prompt = argv[argv.index("--single") + 1]
    assert packet not in prompt
    assert len(prompt) <= ARGV_PROMPT_MAX
    assert "PACKET.md" in prompt


def test_oa_refuses_missing_model_provenance():
    class Fake:
        def dispatch(self, payload):
            return {"ok": True, "kind": "API", "model": "gpt-5.3-codex",
                    "text": '```json\n[{"id":"oa-api-1","topic":"t"}]\n```'}

    fn = make_oa_critic(rail=Fake())
    try:
        fn("packet")
    except CriticError as e:
        assert e.kind == "NO_RAIL"
        assert OA_TERRA_ID in str(e)
        assert "Codex" in str(e) or "provenance" in str(e)
    else:
        raise AssertionError("Codex model must not stamp terra")


def test_bts_gem_adapter_is_not_a_crucible_family():
    k = SimpleNamespace(adapters={GEM: _Probe(True)}, spend=None, paths=None, ledger=None)
    out = compose_crucible_critics(k, which=lambda n: None)
    assert GEM not in out
    assert VERTEX_SPEND != GEM
    assert VERTEX_SPEND == "vertex-coding"


def test_attach_sets_kernel_and_skips_when_empty():
    k = SimpleNamespace(adapters={}, spend=None, paths=None, ledger=None)
    rec = attach_crucible_critics(k, which=lambda n: None)
    assert rec["critics"] == []
    assert rec["anthropic"] == "OFF"
    assert not hasattr(k, "crucible_critics") or not getattr(k, "crucible_critics", None)

    class FakeGem:
        def dispatch(self, payload):
            return {"ok": True, "kind": "API", "usd": 0.0001,
                    "text": '```json\n[{"id":"gem-api-1","topic":"t"}]\n```'}

    k2 = SimpleNamespace(adapters={GEM: _Probe(True)}, spend=None, paths=None, ledger=None)
    rec2 = attach_crucible_critics(k2, which=lambda n: None, vertex_rail=FakeGem())
    assert GEM in rec2["critics"]
    assert GEM not in rec2["wallets"] or "vertex_coding" in rec2["wallets"]
    assert callable(k2.crucible_critics[GEM])


if __name__ == "__main__":
    test_grok_sgh_env_unsets_console_key()
    test_prefer_grok_sgh_over_console_same_family()
    test_console_only_when_grok_cli_absent()
    test_empty_compose_is_honest_501_pool()
    test_attach_sets_kernel_and_skips_when_empty()
    test_vertex_rail_injects_joanna_gem_family()
    test_oa_rail_injects_platform_api_family()
    test_grok_argv_does_not_carry_packet()
    test_oa_refuses_missing_model_provenance()
    test_bts_gem_adapter_is_not_a_crucible_family()
    print("ok")
