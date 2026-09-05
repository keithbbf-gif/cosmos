#!/usr/bin/env python3
"""Retired one-shot. Logic lives in cosmos_master_desc.extract_text.

Staged, not deleted: this file is now a pointer so a later grep does not
treat the helper as live. Prefer cosmos.cosmos_master_desc.extract_text.
"""
from cosmos_master_desc import extract_text, main as _unused  # noqa: F401

if __name__ == "__main__":
    raise SystemExit("use cosmos/cosmos_master_desc.py")
