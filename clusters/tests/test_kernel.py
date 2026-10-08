"""Store, path guard, verify, and the harness port."""

from __future__ import annotations

import json

import pytest

from clusters.harness import plan_seat
from clusters.models import DOORS
from clusters.refuse import Refuse, guard_path, scrub
from clusters.store import Store
from clusters.verify import judge


def test_verify_claim_needs_both_stamps():
    assert judge("", None)["verdict"] == "RECORDED"
    assert judge("done", {"source": "diff"})["verdict"] == "UNMEASURED"
    assert judge("done", {"source": "diff", "observed": "sha256:abc"})["verdict"] == "VERIFIED"


def test_live_path_and_secrets_refuse():
    with pytest.raises(Refuse) as live:
        guard_path(r"V:\A\Ai\COSMOS\live")
    assert live.value.code == "LIVE_TREE"
    with pytest.raises(Refuse):
        guard_path(r"V:\work\..\live")
    with pytest.raises(Refuse) as secret:
        scrub({"profile_dir": r"V:\profiles\a", "api_key": "sk-real"})
    assert secret.value.code == "SECRET"


def test_store_folds_and_fsyncs(tmp_path):
    store = Store(tmp_path / "proj")
    store.append("note", {"id": "n1", "text": "one"})
    store.append("note", {"id": "n1", "text": "two"}, {"source": "tester", "observed": "two"}, "edited")
    view = store.view("note")
    assert view["n1"]["text"] == "two"
    assert view["n1"]["_verdict"] == "VERIFIED"
    lines = (tmp_path / "proj" / "events.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    assert json.loads(lines[0])["seq"] == 1


def test_store_refuses_live_root():
    with pytest.raises(Refuse):
        Store(r"V:\A\Ai\COSMOS\live\clusters")


def test_plan_seat_does_not_start_and_refuses_native_grok(tmp_path):
    missing = plan_seat("nope", "task", str(tmp_path), harness_root=tmp_path / "missing")
    assert missing["seated"] is False
    assert missing["why"] == "UNKNOWN_HERO"
    with pytest.raises(Refuse) as refused:
        plan_seat("grok", "write a function", str(tmp_path), via="native")
    assert refused.value.code == "GROK_EXE"


def test_plan_seat_against_the_stream_harness_stays_unseated(tmp_path):
    result = plan_seat("sol", "Add one function that returns 1.", str(tmp_path), via="cosmos-code")
    assert result["seated"] is False
    assert result["started"] is False
    assert result.get("agent") == "sol"
    assert result["verdict"] == "RECORDED"


def test_plain_shell_is_named_and_does_not_execute():
    door = DOORS["shell"]
    assert door["executable"] is False
    assert door["seated"] is False
    assert door["resume"] is False
