#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AST fence between Core SpendGate and Token Center pay.

Parses source. Does not import cosmos_pay or cosmos_spend.
A comment or a docstring mention is not an import.
"""
from __future__ import annotations

import ast
import os
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
COSMOS_ROOT = REPO / "cosmos"
TOKENCTR_ROOT = REPO / "tokenctr"


def _py_files(root: Path):
    """Every .py under root, skipping underscore directories and __pycache__."""
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [
            name
            for name in dirnames
            if name != "__pycache__" and not name.startswith("_")
        ]
        for name in filenames:
            if name.endswith(".py"):
                yield Path(dirpath) / name


def _bans_pay(module: str) -> bool:
    """cosmos_pay, cosmos_pay_*, and dotted children of those modules."""
    head = module.split(".", 1)[0]
    return head == "cosmos_pay" or head.startswith("cosmos_pay_")


def _bans_spend(module: str) -> bool:
    """cosmos_spend, cosmos.cosmos_spend, or a name starting with cosmos_spend."""
    if module == "cosmos.cosmos_spend" or module.startswith("cosmos.cosmos_spend."):
        return True
    return module.startswith("cosmos_spend")


def _imported_modules(node: ast.AST) -> list[str]:
    if isinstance(node, ast.Import):
        return [alias.name for alias in node.names]
    if not isinstance(node, ast.ImportFrom):
        return []
    modules: list[str] = []
    if node.module:
        modules.append(node.module)
    if node.module == "cosmos":
        # `from cosmos import cosmos_spend` is module cosmos.cosmos_spend.
        modules.extend(f"cosmos.{alias.name}" for alias in node.names)
    elif node.level and not node.module:
        # `from . import cosmos_pay` — relative, alias is the module.
        modules.extend(alias.name for alias in node.names)
    return modules


def _scan(root: Path, bans) -> list[str]:
    if not root.is_dir():
        return [f"{root}: missing"]
    hits: list[str] = []
    for path in _py_files(root):
        try:
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(path))
        except (OSError, SyntaxError, UnicodeError) as exc:
            hits.append(f"{path}: {exc.__class__.__name__}: {exc}")
            continue
        for node in ast.walk(tree):
            for module in _imported_modules(node):
                if bans(module):
                    hits.append(f"{path}:{getattr(node, 'lineno', 0)}: {module}")
    return hits


def test_cosmos_does_not_import_pay() -> None:
    hits = _scan(COSMOS_ROOT, _bans_pay)
    assert hits == [], "\n".join(hits)


def test_tokenctr_does_not_import_spend() -> None:
    hits = _scan(TOKENCTR_ROOT, _bans_spend)
    assert hits == [], "\n".join(hits)
