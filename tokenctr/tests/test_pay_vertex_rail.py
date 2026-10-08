#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_pay_vertex_rail — tests for the stdlib Vertex AI rail translation and usage extraction."""
from __future__ import annotations

import sys
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CODE_DIR))

import cosmos_pay_vertex_rail as vtx

PASS = 0
FAIL = 0


def check(name: str, cond: bool) -> None:
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  PASS {name}")
    else:
        FAIL += 1
        print(f"  FAIL {name}")


print("-- test_pay_vertex_rail --")

rail = vtx.VertexAIRail(project_id="test-proj", access_token="test-token")

# 1. Translation: system + user + assistant messages
req = {
    "model": "gemini-flash-vertex",
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"},
        {"role": "assistant", "content": "Hi there!"},
        {"role": "user", "content": "Can you code?"},
    ],
    "max_tokens": 1024,
    "temperature": 0.7,
}

contents, gen_config, sys_inst = rail._translate_request(req)
check("contents has 3 dialog turns", len(contents) == 3)
check("turn 1 is user", contents[0]["role"] == "user")
check("turn 2 is model", contents[1]["role"] == "model")
check("system instruction extracted", sys_inst is not None and "helpful assistant" in sys_inst["parts"][0]["text"])
check("maxOutputTokens mapped", gen_config.get("maxOutputTokens") == 1024)
check("temperature mapped", gen_config.get("temperature") == 0.7)

# 2. Model slug resolution
check("gemini-flash-vertex resolves to flash", rail._resolve_model_name("gemini-flash-vertex") == "gemini-1.5-flash-002")
check("gemini-pro resolves to pro", rail._resolve_model_name("gemini-pro-vertex") == "gemini-1.5-pro-002")

# 3. Auth headers
headers = rail._auth_headers()
check("bearer token header present", "Bearer test-token" in headers.get("Authorization", ""))
check("X-Goog-User-Project present", headers.get("X-Goog-User-Project") == "test-proj")

print(f"\n{PASS} pass, {FAIL} fail")
sys.exit(1 if FAIL else 0)
