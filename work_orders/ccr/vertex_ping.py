#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""vertex_ping.py — single-token round trip per Vertex account.

Sends a minimal generateContent (maxOutputTokens=1) to each account's key and
reports OK/FAIL. Keys are read from the secrets vault, never printed.

Accounts with a known project use the Vertex AI endpoint. Accounts without a
project id try the generativelanguage endpoint (no project needed); if that
fails with auth, they report UNMEASURED (project id required).
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from pathlib import Path

SECRETS = Path(r"V:\Research4\.secrets")
MODEL = "gemini-2.5-flash"
BODY = json.dumps({
    "contents": [{"role": "user", "parts": [{"text": "ping"}]}],
    "generationConfig": {"maxOutputTokens": 1},
}).encode()

ACCOUNTS = [
    ("joanna.bbf@gmail.com", "vertex_key.txt", "project-5a33f910-1251-4d6a-bf9"),
    ("orders.ggn@gmail.com", "vertex_coding_key.txt", "project-10b3a132-ec5b-41e9-a2c"),
    ("medicineman.mme@gmail.com", "vertex_medicineman_key.txt", "project-cc5302c9-190c-4cdf-87d"),
    ("patriotfuelstop.com@gmail.com", "vertex_patriotfuelstop_key.txt", "project-3cce004b-198c-45f3-81a"),
    ("fruitaholics.com@gmail.com", "vertex_fruitaholics_key.txt", "project-cbef203a-6f27-43be-811"),
]


def ping_vertex(key: str, project: str | None) -> tuple[bool, str]:
    if project:
        url = (f"https://aiplatform.googleapis.com/v1beta1/projects/{project}"
               f"/locations/global/publishers/google/models/{MODEL}:generateContent")
        req = urllib.request.Request(url, data=BODY, method="POST",
                                     headers={"Content-Type": "application/json",
                                              "x-goog-api-key": key})
    else:
        url = (f"https://generativelanguage.googleapis.com/v1beta/models/"
               f"{MODEL}:generateContent")
        req = urllib.request.Request(url, data=BODY, method="POST",
                                     headers={"Content-Type": "application/json",
                                              "x-goog-api-key": key})
    try:
        resp = json.loads(urllib.request.urlopen(req, timeout=30).read())
        text = resp.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        return True, f"OK text={text!r}"
    except urllib.error.HTTPError as e:
        return False, f"HTTP {e.code}: {e.reason}"
    except Exception as e:  # noqa: BLE001
        return False, f"{type(e).__name__}: {e}"


def main() -> None:
    print(f"{'account':<32} {'project':<38} result")
    print("-" * 100)
    for account, key_file, project in ACCOUNTS:
        kf = SECRETS / key_file
        if not kf.exists():
            print(f"{account:<32} {'-':<38} NO KEY FILE")
            continue
        key = kf.read_text(encoding="utf-8").strip()
        ok, msg = ping_vertex(key, project)
        proj = project or "UNMEASURED"
        print(f"{account:<32} {proj:<38} {'GREEN' if ok else 'RED'} | {msg}")


if __name__ == "__main__":
    main()