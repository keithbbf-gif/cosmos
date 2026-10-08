#!/usr/bin/env python3
"""Typed refusals for session-tools. A kind is the product, not a traceback."""


class SessionToolsRefusal(RuntimeError):
    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")
