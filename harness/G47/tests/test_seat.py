"""Native seat and COSMOS CODE seat. No process is started."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from g47.refuse import Refuse
from g47.roster import AGENTS
from g47.seat import seat, seat_agent
from g47.superior import CLAUDE_LAW, ahead_of, law

TASK = "Write decode_rle. Empty in, empty out. Count then one character. A bad tail raises ValueError."


def test_every_agent_seats_native_and_on_cosmos_code(tmp_path: Path):
    for agent_id in AGENTS:
        native = seat(agent_id, via="native", task=TASK, where=str(tmp_path / agent_id / "native"))
        own = seat(agent_id, via="cosmos-code", task=TASK, where=str(tmp_path / agent_id / "own"))
        assert native.pack_applied and own.pack_applied
        assert len(native.layers) == 8 and len(own.layers) == 8
        assert own.door == "cosmos-code"
        assert native.door == AGENTS[agent_id].native_door
        assert "codex" not in own.plan.argv
        assert "--fallback-model" not in native.plan.argv
        assert ahead_of(own, CLAUDE_LAW)
        assert sum(law(own).values()) > sum(law(native).values())


def test_sol_native_is_codex_and_cosmos_code_is_not(tmp_path: Path):
    native = seat("sol", via="native", task=TASK, where=str(tmp_path / "n"))
    own = seat("sol", via="cosmos-code", task=TASK, where=str(tmp_path / "c"))
    assert native.plan.argv[:2] == ["codex", "exec"]
    assert "--approve-for-me" in native.plan.argv
    assert "--ignore-user-config" not in native.plan.argv
    assert own.executable is False
    assert "LOOP.md" in own.plan.files and "TOOLS.md" in own.plan.files
    assert "shell\n" not in own.plan.files["TOOLS.md"]
    assert "shell is not a tool" in own.plan.files["TOOLS.md"]
    assert own.plan.files["PIN.md"] == "model=gpt-5.4\n"
    assert "gpt-5.4" not in " ".join(own.plan.argv)


def test_luna_native_is_read_only_codex(tmp_path: Path):
    native = seat("luna", via="native", task=TASK, where=str(tmp_path / "l"))
    assert "--approve-for-me" not in native.plan.argv
    assert "--sandbox" in native.plan.argv
    assert native.model == "openai/gpt-5.6-luna:floor"
    joined = " ".join(native.plan.argv)
    assert 'wire_api="responses"' in joined
    assert "wire_api=chat" not in joined
    assert "service_tier" not in joined


def test_grok_native_does_not_become_a_worker(tmp_path: Path):
    native = seat("grok", via="native", task=TASK, where=str(tmp_path / "g"))
    assert native.executable is False
    assert native.plan.argv == ["grok.exe"]


def test_seat_agent_closes_only_on_the_served_id(tmp_path: Path):
    """An injected call seats only when the served id matches the roster pin."""

    def foreign(_attempt):
        return {"seated": True, "served": "other", "http": 200, "mouth": "HOLD"}

    missed = seat_agent("luna", TASK, tmp_path / "foreign", foreign)
    assert missed["seated"] is False
    assert missed["scar"] == "MOUTH_FOREIGN"
    row = json.loads((tmp_path / "foreign" / "seat.jsonl").read_text(encoding="utf-8").splitlines()[0])
    assert row["seated"] is False
    assert row["sop"] == "foreign_mouth"
    assert row["pin"] == "openai/gpt-5.6-luna:floor"

    def matched(attempt):
        assert attempt.pin == "openai/gpt-5.6-luna:floor"
        assert attempt.door == "codex"
        return {"seated": True, "served": "openai/gpt-5.6-luna", "http": 200, "mouth": "HOLD"}

    held = seat_agent("luna", TASK, tmp_path / "match", matched)
    assert held["seated"] is True
    assert held["served"] == "openai/gpt-5.6-luna"
    stamped = json.loads((tmp_path / "match" / "seat.jsonl").read_text(encoding="utf-8").splitlines()[0])
    assert stamped["seated"] is False

    def boom(_attempt):
        raise AssertionError("grok must not be called")

    with pytest.raises(Refuse) as exc:
        seat_agent("grok", TASK, tmp_path / "no-grok", boom)
    assert exc.value.reason == "GROK_NOT_A_WORKER"
    with pytest.raises(Refuse) as exc:
        seat_agent("luna", TASK, tmp_path / "live", matched)
    assert exc.value.reason == "LIVE_TREE"


def test_half_a_pack_is_refused(tmp_path: Path):
    with pytest.raises(Refuse) as exc:
        seat("sol", via="cosmos-code", task="  ", where=str(tmp_path))
    assert exc.value.reason == "PACK_INCOMPLETE"
    with pytest.raises(Refuse) as exc:
        seat("sol", via="native", task=TASK, where=str(tmp_path / "live"))
    assert exc.value.reason == "LIVE_TREE"


def test_style_stays_off_the_system_turn(tmp_path: Path):
    own = seat("gf38", via="native", task=TASK, where=str(tmp_path / "v"), style="be terse")
    assert "be terse" in own.plan.user
    assert "be terse" not in own.plan.system
