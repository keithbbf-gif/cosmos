#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Typed refusals for sessions-app. A kind is the product, not a traceback."""


class SessionsAppRefusal(RuntimeError):
    def __init__(self, kind: str, detail: str, **fields):
        self.kind = kind
        # Structured extras (size, cap, …) travel with the refusal so a surface
        # can pin them on the wire without parsing the detail string.
        self.fields = fields
        super().__init__(f"[{kind}] {detail}")
