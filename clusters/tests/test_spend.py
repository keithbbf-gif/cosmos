"""Spend counts only when source and observed are both present."""

from __future__ import annotations

import pytest

from clusters.refuse import Refuse
from clusters.spend import bump_today, check, observe, report, set_budget
from clusters.store import Store


def test_unmeasured_spend_is_logged_and_pauses(tmp_path):
    store = Store(tmp_path / "spend")
    set_budget(
        store,
        provider="openai",
        daily_cap_usd=10,
        mode="smart_pace",
        on_limit="stop",
        window_days=2,
        day_index=0,
    )
    bare = observe(store, provider="openai", usd=6)
    half = observe(store, provider="openai", usd=1, source="invoice", observed="")
    assert bare == {"verdict": "UNMEASURED", "counted": False}
    assert half["counted"] is False
    assert len(store.fold("spend")) == 2
    gate = check(store, provider="openai", usd=4)
    assert gate["decision"] == "pause"
    assert gate["code"] == "UNMEASURED"
    assert gate["spent_usd"] == 0
    assert gate["allowance_usd"] == 5
    assert "on_limit" not in gate
    counted = observe(store, provider="openai", usd=2, source="invoice", observed="2")
    assert counted["counted"] is True
    still = check(store, provider="openai", usd=0)
    assert still["decision"] == "pause"
    assert still["code"] == "UNMEASURED"
    assert still["spent_usd"] == 2
    assert still["allowance_usd"] == 4


def test_measured_spend_counts(tmp_path):
    store = Store(tmp_path / "spend")
    set_budget(store, provider="openai", daily_cap_usd=10)
    seen = observe(
        store,
        provider="openai",
        usd=0.25,
        tokens=4,
        source="invoice",
        observed="0.25",
    )
    assert seen == {"verdict": "VERIFIED", "counted": True}
    gate = check(store, provider="openai")
    assert gate["spent_usd"] == 0.25
    assert gate["decision"] == "allow"
    assert gate["code"] == "OK"
    assert gate["on_limit"] == "pause"


def test_cap_pauses_when_the_request_exceeds(tmp_path):
    store = Store(tmp_path / "spend")
    set_budget(store, provider="openai", daily_cap_usd=1.00, on_limit="pause")
    seen = observe(store, provider="openai", usd=0.90, source="invoice", observed="0.90")
    observe(store, provider="other", usd=50, source="invoice", observed="50")
    assert seen["counted"] is True
    result = check(store, provider="openai", usd=0.20)
    assert result["decision"] == "pause"
    assert result["code"] == "LIMIT"
    assert result["on_limit"] == "pause"
    assert result["spent_usd"] == pytest.approx(0.90)
    assert result["allowance_usd"] == pytest.approx(1.00)


def test_second_bump_refuses(tmp_path):
    store = Store(tmp_path / "spend")
    set_budget(store, provider="OpenAI", daily_cap_usd=1)
    assert store.view("budget")["budget-openai"]["provider"] == "OpenAI"
    assert bump_today(store, provider="OpenAI") == {"bumped": True, "fraction": 0.05}
    assert store.fold("bump")[-1]["body"]["id"] == "bump-OpenAI-0"
    gate = check(store, provider="openai", usd=0)
    assert gate["allowance_usd"] == pytest.approx(1.05)
    with pytest.raises(Refuse) as refused:
        bump_today(store, provider="openai")
    assert refused.value.code == "ALREADY_BUMPED"


def test_smart_pace_splits_the_first_day(tmp_path):
    store = Store(tmp_path / "spend")
    opened = set_budget(
        store,
        provider="openai",
        daily_cap_usd=10,
        mode="smart_pace",
        on_limit="stop",
        window_days=2,
        day_index=0,
    )
    assert opened["allowance_usd"] == 5
    assert opened["spent_usd"] == 0
    assert opened["unmeasured"] is False
    assert report(store) == [opened]
    blocked = check(store, provider="openai", usd=6)
    assert blocked["decision"] == "stop"
    assert blocked["code"] == "LIMIT"
    assert blocked["allowance_usd"] == 5
    assert blocked["on_limit"] == "stop"
    allowed = check(store, provider="openai", usd=4)
    assert allowed["decision"] == "allow"
    assert allowed["code"] == "OK"
    assert check(store, provider="openai", usd=5)["decision"] == "allow"


def test_token_limit_is_independent_of_dollars(tmp_path):
    store = Store(tmp_path / "spend")
    set_budget(
        store,
        provider="openai",
        daily_cap_usd=10,
        daily_cap_tokens=100,
        on_limit="notify",
    )
    observe(store, provider="openai", usd=0.1, tokens=80, source="usage", observed="80")
    over = check(store, provider="openai", usd=0.1, tokens=30)
    assert over["decision"] == "notify"
    assert over["code"] == "LIMIT"
    assert check(store, provider="openai", usd=0.1, tokens=20)["decision"] == "allow"


def test_zero_token_cap_ignores_tokens(tmp_path):
    store = Store(tmp_path / "spend")
    set_budget(store, provider="openai", daily_cap_usd=10, daily_cap_tokens=0)
    observe(store, provider="openai", usd=1, tokens=5000, source="usage", observed="5000")
    assert check(store, provider="openai", tokens=5000)["decision"] == "allow"


def test_budget_inputs_fail_closed(tmp_path):
    store = Store(tmp_path / "spend")
    cases = (
        ({"provider": "", "daily_cap_usd": 1}, "PROVIDER"),
        ({"provider": "openai", "daily_cap_usd": 1, "mode": "loose"}, "MODE"),
        ({"provider": "openai", "daily_cap_usd": 1, "on_limit": "kill"}, "LIMIT"),
        ({"provider": "openai", "daily_cap_usd": 1, "window_days": 0}, "WINDOW"),
        ({"provider": "openai", "daily_cap_usd": 1, "window_days": 2, "day_index": 2}, "WINDOW"),
        ({"provider": "openai", "daily_cap_usd": 1, "day_index": -1}, "WINDOW"),
        ({"provider": "openai", "daily_cap_usd": -0.01}, "CAP"),
        ({"provider": "openai", "daily_cap_usd": 1, "daily_cap_tokens": -1}, "CAP"),
    )
    for kwargs, code in cases:
        with pytest.raises(Refuse) as refused:
            set_budget(store, **kwargs)
        assert refused.value.code == code
    with pytest.raises(Refuse) as refused:
        check(store, provider="openai")
    assert refused.value.code == "PROVIDER"
    with pytest.raises(Refuse) as refused:
        bump_today(store, provider="openai")
    assert refused.value.code == "PROVIDER"
    assert store.fold("budget") == []
