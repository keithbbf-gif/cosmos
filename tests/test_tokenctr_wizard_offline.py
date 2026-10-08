#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Offline format check for Token Center Bedrock BYOK.

Import of cosmos_pay_wizard only binds paths in cosmos_pay_config.
test_bedrock does not call the network. OpenRouter and Google tests are not called.
"""
from __future__ import annotations

import socket
import sys
from pathlib import Path

_TOKENCTR = Path(__file__).resolve().parents[1] / "tokenctr"
sys.path.insert(0, str(_TOKENCTR))

# Alias: pytest collects a bare test_bedrock name in this module.
from cosmos_pay_wizard import test_bedrock as bedrock_format  # noqa: E402

_KEY = "AKIATESTKEY00000000"
_REGION = "us-east-1"


def _block_network(monkeypatch) -> None:
    def _blocked(*_args, **_kwargs):
        raise AssertionError("network attempted")

    monkeypatch.setattr(socket, "socket", _blocked)
    monkeypatch.setattr(socket, "create_connection", _blocked)


def test_bedrock_accepts_akia_long_secret_and_region(monkeypatch) -> None:
    _block_network(monkeypatch)
    assert bedrock_format(_KEY, "x" * 30, _REGION) is True


def test_bedrock_rejects_short_secret(monkeypatch) -> None:
    _block_network(monkeypatch)
    assert bedrock_format(_KEY, "short", _REGION) is False
