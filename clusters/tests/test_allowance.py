"""Spend and quota both have to allow. This test does not append a third ledger."""

from __future__ import annotations

import pytest

from clusters.allowance import admit
from clusters.quota import set_window
from clusters.refuse import Refuse
from clusters.spend import observe, set_budget
from clusters.store import Store


def _budget(store: Store) -> None:
    set_budget(store, provider="openai", daily_cap_usd=10, day_index=0)


def test_missing_budget_refuses(tmp_path):
    store = Store(tmp_path / "s")
    with pytest.raises(Refuse) as refused:
        admit(store, provider="openai", now=1)
    assert refused.value.code == "PROVIDER"


def test_no_quota_window_follows_the_cap(tmp_path):
    store = Store(tmp_path / "s")
    _budget(store)
    row = admit(store, provider="openai", usd=1, now=1)
    assert row["decision"] == "allow"
    assert row["code"] == "OK"
    assert row["quota"] == "NO_WINDOW"
    assert row["gate"] == ""
    assert store.fold("spend") == []
    assert store.fold("quota") == []


def test_unmeasured_quota_pauses_even_when_the_cap_allows(tmp_path):
    store = Store(tmp_path / "s")
    _budget(store)
    set_window(
        store,
        provider="openai",
        limit_usd=100,
        period_seconds=100,
        resets_at=100,
        source="sidebar",
        observed="",
    )
    row = admit(store, provider="openai", usd=1, now=50)
    assert row["decision"] == "pause"
    assert row["code"] == "UNMEASURED"
    assert row["gate"] == "quota"


def test_unmeasured_spend_pauses_before_the_window(tmp_path):
    store = Store(tmp_path / "s")
    _budget(store)
    observe(store, provider="openai", usd=1, day_index=0)
    set_window(
        store,
        provider="openai",
        limit_usd=100,
        period_seconds=100,
        resets_at=100,
        source="sidebar",
        observed="100",
    )
    row = admit(store, provider="openai", now=50)
    assert row["decision"] == "pause"
    assert row["gate"] == "spend"
    assert row["code"] == "UNMEASURED"
