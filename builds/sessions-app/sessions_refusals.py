#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Typed refusals for sessions-app. A kind is the product, not a traceback."""


class SessionsAppRefusal(RuntimeError):
    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")
