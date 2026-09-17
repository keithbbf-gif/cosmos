#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prove F-21 / F-68 pins FAIL against the staged predecessor.

F-21: staged cosmos_cvm_push.probe_stt (env-gated, no vendor site) does
not bind vosk when COSMOS_VOSK_MODEL is unset.

F-68: repo-root COSMOS_MASTER_DESCRIPTION.docx (2026-08-25) lacks the
ITERATE 1→8 pin and the competency table.

all_new_pins_failed is the bite. Does not import the live new modules
for the F-21 probe (loads the staged file by path).
"""
from __future__ import annotations

import importlib.util
import json
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OLD_PUSH = (REPO / "_delme" / "predispose_cosmos_cvm_push_f21_20260831T145131Z"
            / "cosmos_cvm_push.py")
OUT = REPO / "cosmos" / "_fail_f21_f68_against_old.json"
INCUMBENT = REPO / "COSMOS_MASTER_DESCRIPTION.docx"


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    # staged file imports cosmos_* from the same package dir — put cosmos/ on path
    sys.path.insert(0, str(REPO / "cosmos"))
    spec.loader.exec_module(mod)
    return mod


def extract_text(path: Path) -> str:
    import re
    import zipfile
    with zipfile.ZipFile(path) as z:
        xml = z.read("word/document.xml")
    text = re.sub(rb"</w:p>", b"\n", xml)
    text = re.sub(rb"<[^>]+>", b"", text)
    return text.decode("utf-8", "replace")


def main() -> int:
    old_env = os.environ.pop("COSMOS_VOSK_MODEL", None)
    try:
        push = load("cvm_push_old", OLD_PUSH)
        probed = push.probe_stt()
    finally:
        if old_env is not None:
            os.environ["COSMOS_VOSK_MODEL"] = old_env

    old_text = extract_text(INCUMBENT) if INCUMBENT.is_file() else ""
    pins = {
        "old_probe_stt_ok": bool(probed.get("ok")),
        "old_probe_kind_ok": probed.get("kind") == "ok",
        "old_docx_has_iterate_1_to_8_pin": (
            "ITERATE returns to stage 1 RESEARCH" in old_text
            or "not 5→8" in old_text
            or "not 5->8" in old_text
        ),
        "old_docx_has_competency_toml": "COMPETENCY.toml" in old_text,
        "old_docx_has_code_build": "code-build" in old_text,
    }
    rec = {
        "schema": "cosmos-f21-f68-fail-old/1",
        "old_push": str(OLD_PUSH),
        "old_probe": {
            "ok": probed.get("ok"),
            "kind": probed.get("kind"),
            "detail": probed.get("detail"),
        },
        "incumbent_chars": len(old_text),
        "pins": pins,
        "all_new_pins_failed": all(v is False for v in pins.values()),
    }
    OUT.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(rec, indent=1))
    return 0 if rec["all_new_pins_failed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
