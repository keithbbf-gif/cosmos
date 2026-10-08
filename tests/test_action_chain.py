#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Public tests for cosmos_action_chain. Scratch ledger only."""
from __future__ import annotations

import hashlib
import json
import sys
import uuid
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cosmos"))

from cosmos_action_chain import (  # noqa: E402
    SCHEMA,
    ActionError,
    append_action,
    last_action_sha,
    snapshot,
    verify_actions,
)
from cosmos_ledger import Ledger  # noqa: E402

SCRATCH = Path(r"C:\Users\Papa\AppData\Local\Temp\c4-pkt")
KEY = b"c4-action-chain-test-key"


def _scratch(label: str) -> Path:
    path = SCRATCH / "action" / label / uuid.uuid4().hex
    path.mkdir(parents=True, exist_ok=True)
    resolved = path.resolve()
    assert resolved.is_relative_to(SCRATCH.resolve())
    live = (ROOT / "live").resolve()
    assert not resolved.is_relative_to(live)
    return path


def _open(root: Path) -> tuple[Ledger, Path]:
    path = root / "actions.jsonl"
    return Ledger(path, KEY, "core"), path


def _canon_sha(obj: dict) -> str:
    # Canonical body the chain hashes, excluding action_sha.
    body = json.dumps(obj, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def test_empty_chain_is_unmeasured_and_does_not_invent():
    led, path = _open(_scratch("empty"))
    checked = verify_actions(led)
    assert checked == {"ok": True, "n": 0, "head": ""}
    assert last_action_sha(led) == ""
    snap = snapshot(led)
    assert snap["schema"] == SCHEMA == "cosmos-action-chain/1"
    assert snap["kind"] == "UNMEASURED"
    assert snap["ok"] is True
    assert snap["n"] == 0
    assert snap["head"] == ""
    assert "mkdir" in snap["note"]
    assert not path.exists()
    lock = path.with_name(path.name + ".lock")
    assert not lock.exists()


def test_sod_refuses_blank_and_shared_roles():
    led, path = _open(_scratch("sod"))
    with pytest.raises(ActionError) as blank:
        append_action(
            led, creator="", reviewer="rev", approver="app",
            kind="git", detail="x",
        )
    assert blank.value.kind == "SOD"
    with pytest.raises(ActionError) as shared:
        append_action(
            led, creator="same", reviewer="rev", approver="same",
            kind="git", detail="x",
        )
    assert shared.value.kind == "SOD"
    assert not path.exists()


def test_chain_measures_two_distinct_roles():
    led, _path = _open(_scratch("chain"))
    led.append("NOTE", {"n": 1})
    first = append_action(
        led, creator="worker:w1", reviewer="gitur:one",
        approver="captain:keith", kind="k" * 80, detail="d" * 600,
        token=3,
    )
    led.append("NOTE", {"n": 2})
    second = append_action(
        led, creator="worker:w2", reviewer="gitur:two",
        approver="ccr:716fbaea", kind="file_write", detail="work",
        token=7,
    )
    assert first["ok"] is True
    assert first["prev_action_sha"] == ""
    assert second["prev_action_sha"] == first["action_sha"]
    assert first["seq"] == 2
    assert second["seq"] == 4
    checked = verify_actions(led)
    assert checked["ok"] is True
    assert checked["n"] == 2
    assert checked["head"] == second["action_sha"]
    assert last_action_sha(led) == second["action_sha"]
    snap = snapshot(led)
    assert snap["kind"] == "MEASURED"
    assert snap["n"] == 2
    assert snap["ok"] is True
    actions = [r for r in led.verify() if r.get("event") == "ACTION"]
    assert len(actions[0]["payload"]["kind"]) == 40
    assert len(actions[0]["payload"]["detail"]) == 500
    assert actions[0]["payload"]["token"] == 3
    assert actions[1]["payload"]["token"] == 7
    assert actions[1]["payload"]["schema"] == SCHEMA


def test_missing_action_hash_is_forged():
    led, _path = _open(_scratch("hash"))
    led.append("ACTION", {
        "schema": SCHEMA,
        "kind": "git",
        "detail": "x",
        "creator": "c",
        "reviewer": "r",
        "approver": "a",
        "prev_action_sha": "",
        "token": None,
        "at": 1.0,
    })
    with pytest.raises(ActionError) as forged:
        verify_actions(led)
    assert forged.value.kind == "FORGED"
    snap = snapshot(led)
    assert snap["ok"] is False
    assert snap["kind"] == "FORGED"
    assert snap["error"] == "FORGED"
    assert snap["schema"] == SCHEMA


def test_broken_prev_is_broken_chain():
    led, _path = _open(_scratch("link"))
    first = append_action(
        led, creator="c1", reviewer="r1", approver="a1",
        kind="git", detail="one",
    )
    payload = {
        "schema": SCHEMA,
        "kind": "file",
        "detail": "two",
        "creator": "c2",
        "reviewer": "r2",
        "approver": "a2",
        "prev_action_sha": "f" * 64,
        "token": None,
        "at": 2.0,
    }
    payload["action_sha"] = _canon_sha(payload)
    assert payload["prev_action_sha"] != first["action_sha"]
    led.append("ACTION", payload)
    with pytest.raises(ActionError) as broken:
        verify_actions(led)
    assert broken.value.kind == "BROKEN_CHAIN"
    snap = snapshot(led)
    assert snap["ok"] is False
    assert snap["kind"] == "BROKEN_CHAIN"
    assert snap["error"] == "BROKEN_CHAIN"
