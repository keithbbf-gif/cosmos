"""Meter readings store the operator's text and do not reduce spend.

An empty usage view is not unlimited. Logged-out is not stopped.
Zen with auto-reload off is a hard stop. These tests use Store only.
They do not write a spend row or a quota row.
"""

from __future__ import annotations

import pytest

from clusters.meter import meter_gate, set_meter
from clusters.refuse import Refuse
from clusters.store import Store


def test_empty_with_source_and_observed_is_not_unlimited(tmp_path):
    # Evidence rule: source and observed can verify the claim, but an empty
    # reading is still not unlimited and the gate pauses.
    store = Store(tmp_path / "meter")
    opened = set_meter(
        store,
        provider="Muse",
        reading="empty",
        pool="window",
        source="usage view",
        observed="empty",
    )
    assert opened["provider"] == "Muse"
    assert opened["reading"] == "empty"
    assert opened["pool"] == "window"
    assert opened["verdict"] == "VERIFIED"
    assert opened["counted"] is False
    assert opened["unlimited"] is False
    assert opened["stopped"] is False
    assert opened["hard_stop"] is False
    row = store.fold("meter")[-1]
    assert row["claim"] == "meter"
    assert row["verdict"] == "VERIFIED"
    assert row["body"]["id"] == "meter-muse-window"
    assert row["body"]["unlimited"] is False
    assert row["body"]["stopped"] is False
    assert row["evidence"]["source"] == "usage view"
    assert row["evidence"]["observed"] == "empty"
    gate = meter_gate(store, provider="muse", pool="window")
    assert gate == {"decision": "pause", "code": "UNMEASURED"}
    assert store.fold("spend") == []
    assert store.fold("quota") == []


def test_logged_out_is_not_stopped(tmp_path):
    store = Store(tmp_path / "meter")
    opened = set_meter(
        store,
        provider="antigravity",
        reading="logged-out",
        pool="membership",
        source="local server",
        observed="logged-out",
    )
    assert opened["stopped"] is False
    assert opened["unlimited"] is False
    assert opened["counted"] is False
    assert opened["hard_stop"] is False
    row = store.fold("meter")[-1]
    assert row["claim"] == "meter"
    assert row["body"]["id"] == "meter-antigravity-membership"
    assert row["body"]["reading"] == "logged-out"
    assert row["body"]["stopped"] is False
    assert row["body"]["unlimited"] is False
    gate = meter_gate(store, provider="antigravity", pool="membership")
    assert gate == {"decision": "pause", "code": "UNMEASURED"}
    assert store.fold("spend") == []
    assert store.fold("quota") == []


def test_zen_without_auto_reload_is_hard_stop(tmp_path):
    store = Store(tmp_path / "meter")
    opened = set_meter(
        store,
        provider="OpenCode",
        reading="credits",
        pool="zen",
        auto_reload=False,
        source="zen balance",
        observed="12",
    )
    assert opened == {
        "provider": "OpenCode",
        "reading": "credits",
        "pool": "zen",
        "verdict": "VERIFIED",
        "counted": True,
        "unlimited": False,
        "stopped": False,
        "hard_stop": True,
    }
    row = store.fold("meter")[-1]
    assert row["claim"] == "meter"
    assert row["verdict"] == "VERIFIED"
    assert row["body"]["id"] == "meter-opencode-zen"
    assert row["body"]["auto_reload"] is False
    assert row["body"]["hard_stop"] is True
    assert row["body"]["stopped"] is False
    assert row["body"]["unlimited"] is False
    gate = meter_gate(store, provider="opencode", pool="zen")
    assert gate == {"decision": "pause", "code": "HARD_STOP"}
    assert store.fold("spend") == []
    assert store.fold("quota") == []


def test_bad_reading_refuses(tmp_path):
    store = Store(tmp_path / "meter")
    with pytest.raises(Refuse) as refused:
        set_meter(
            store,
            provider="cursor",
            reading="unlimited",
            pool="cursor-models",
            source="sidebar",
            observed="full",
        )
    assert refused.value.code == "READING"
    assert store.fold("meter") == []
    assert store.fold("spend") == []
    assert store.fold("quota") == []
