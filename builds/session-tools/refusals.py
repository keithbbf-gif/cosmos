#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Typed refusals for session-tools. Fail-closed; never a silent empty."""
from __future__ import annotations

RESULT_SCHEMA = "cosmos-session-tools-result/1"

# Slice-1 kinds (ARCH §4.10 + load/scan). Later slices add more.
GUESSED_ROOT = "GUESSED_ROOT"
LEGAL_OMITTED = "LEGAL_OMITTED"
NO_STORE = "NO_STORE"
NOT_FOUND = "NOT_FOUND"
UNMEASURED = "UNMEASURED"
UNKNOWN = "UNKNOWN"
UNPARSEABLE = "UNPARSEABLE"
TRUNCATED = "TRUNCATED"
WRONG_SCHEMA = "WRONG_SCHEMA"
SCHEMA_UNKNOWN = "SCHEMA_UNKNOWN"
NOT_A_KERNEL = "NOT_A_KERNEL"

OK = "OK"


class Refusal(Exception):
    """kind is the JSON result kind. extra is merged into the result body."""

    def __init__(self, kind: str, detail: str = "", **extra):
        self.kind = kind
        self.detail = detail
        self.extra = extra
        super().__init__(f"[{kind}] {detail}")


def result(verb: str, kind: str, gate: dict | None = None,
           legal_omitted=False, **extra) -> dict:
    rec = {
        "schema": RESULT_SCHEMA,
        "verb": verb,
        "kind": kind,
        "gate": gate if gate is not None else {},
        "legal_omitted": legal_omitted,
    }
    rec.update(extra)
    return rec


def ok(verb: str, gate: dict, legal_omitted=False, **extra) -> dict:
    return result(verb, OK, gate=gate, legal_omitted=legal_omitted, **extra)


def refuse(verb: str, kind: str, detail: str = "", legal_omitted=False,
           gate: dict | None = None, **extra) -> dict:
    rec = result(verb, kind, gate=gate, legal_omitted=legal_omitted,
                 detail=detail, **extra)
    return rec
