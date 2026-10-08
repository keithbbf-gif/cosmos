"""Quota shapes pause until source and observed are both present.

The stored label is the operator's text. These tests use Store only.
They do not write a quota row and they do not reduce spend.
"""

from __future__ import annotations

import pytest

from clusters.qshape import set_shape, shape_gate
from clusters.refuse import Refuse
from clusters.store import Store


def test_empty_observed_pauses(tmp_path):
    # Evidence rule: empty observed is not a measurement, so the gate pauses.
    store = Store(tmp_path / "qshape")
    opened = set_shape(
        store,
        provider="anthropic",
        shape="weekly",
        limit_label="weekly cap",
        source="guide",
        observed="",
    )
    assert opened["provider"] == "anthropic"
    assert opened["shape"] == "weekly"
    assert opened["verdict"] == "UNMEASURED"
    assert opened["counted"] is False
    row = store.fold("quota_shape")[-1]
    assert row["claim"] == "quota-shape"
    assert row["verdict"] == "UNMEASURED"
    assert row["body"]["id"] == "qshape-anthropic-weekly"
    assert row["body"]["limit_label"] == "weekly cap"
    assert row["evidence"] == {}
    gate = shape_gate(store, provider="anthropic", shape="weekly")
    assert gate == {"decision": "pause", "code": "UNMEASURED"}
    assert store.fold("quota") == []
    assert store.fold("spend") == []


def test_source_and_observed_allows(tmp_path):
    store = Store(tmp_path / "qshape")
    opened = set_shape(
        store,
        provider="Anthropic",
        shape="five-hour",
        limit_label="5-hour window",
        source="sidebar",
        observed="80 percent",
    )
    assert opened == {
        "provider": "Anthropic",
        "shape": "five-hour",
        "verdict": "VERIFIED",
        "counted": True,
    }
    row = store.fold("quota_shape")[-1]
    assert row["claim"] == "quota-shape"
    assert row["verdict"] == "VERIFIED"
    assert row["body"]["id"] == "qshape-anthropic-five-hour"
    assert row["evidence"]["source"] == "sidebar"
    assert row["evidence"]["observed"] == "80 percent"
    gate = shape_gate(store, provider="anthropic", shape="five-hour")
    assert gate == {"decision": "allow", "code": "OK"}
    assert store.fold("quota") == []
    assert store.fold("spend") == []


def test_bad_shape_refuses(tmp_path):
    store = Store(tmp_path / "qshape")
    with pytest.raises(Refuse) as refused:
        set_shape(
            store,
            provider="anthropic",
            shape="daily",
            limit_label="nope",
            source="guide",
            observed="1",
        )
    assert refused.value.code == "SHAPE"
    assert store.fold("quota_shape") == []
