"""Quota counts only when source and observed are both present."""

from __future__ import annotations

import pytest

from clusters.quota import mark_used, prorata, set_window
from clusters.store import Store


def test_window_without_observed_is_not_counted(tmp_path):
    store = Store(tmp_path / "quota")
    opened = set_window(
        store,
        provider="openai",
        limit_usd=100,
        period_seconds=100,
        resets_at=100,
        source="sidebar",
        observed="",
    )
    assert opened["provider"] == "openai"
    assert opened["verdict"] == "UNMEASURED"
    assert opened["counted"] is False
    stored = store.fold("quota")
    assert len(stored) == 1
    assert stored[0]["claim"] == "quota"
    assert stored[0]["body"]["id"] == "quota-openai"
    assert stored[0]["body"]["op"] == "set"
    gate = prorata(store, provider="openai", now=50)
    assert gate == {"decision": "pause", "code": "UNMEASURED", "ahead": None}


def test_even_pace_allows(tmp_path):
    store = Store(tmp_path / "quota")
    opened = set_window(
        store,
        provider="openai",
        limit_usd=100,
        period_seconds=100,
        resets_at=100,
        source="sidebar",
        observed="100",
    )
    assert opened["counted"] is True
    seen = mark_used(
        store,
        provider="openai",
        used_usd=50,
        source="sidebar",
        observed="50",
    )
    assert seen == {"verdict": "VERIFIED", "counted": True}
    used = store.fold("quota_used")[-1]
    assert used["claim"] == "quota-used"
    assert str(used["body"]["id"]).startswith("qus-")
    gate = prorata(store, provider="openai", now=50)
    assert gate["decision"] == "allow"
    assert gate["code"] == "OK"
    assert gate["time_fraction"] == pytest.approx(0.5)
    assert gate["used_fraction"] == pytest.approx(0.5)
    assert gate["ahead"] == pytest.approx(0)
    assert gate["resets_at"] == pytest.approx(100)


def test_ahead_of_the_clock_allows_under_the_cap(tmp_path):
    store = Store(tmp_path / "quota")
    set_window(
        store,
        provider="openai",
        limit_usd=100,
        period_seconds=100,
        resets_at=100,
        source="sidebar",
        observed="100",
    )
    mark_used(store, provider="openai", used_usd=80, source="sidebar", observed="80")
    gate = prorata(store, provider="openai", now=50)
    assert gate["time_fraction"] == pytest.approx(0.5)
    assert gate["used_fraction"] == pytest.approx(0.8)
    assert gate["ahead"] == pytest.approx(0.3)
    assert gate["decision"] == "allow"
    assert gate["code"] == "OK"


def test_used_at_the_cap_pauses(tmp_path):
    store = Store(tmp_path / "quota")
    set_window(
        store,
        provider="openai",
        limit_usd=100,
        period_seconds=100,
        resets_at=100,
        source="sidebar",
        observed="100",
    )
    mark_used(store, provider="openai", used_usd=100, source="sidebar", observed="100")
    gate = prorata(store, provider="openai", now=50)
    assert gate["decision"] == "pause"
    assert gate["code"] == "LIMIT"
    assert gate["used_fraction"] == pytest.approx(1)
    assert gate["time_fraction"] == pytest.approx(0.5)
    assert gate["ahead"] == pytest.approx(0.5)
