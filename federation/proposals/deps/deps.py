"""Measured import census for the day-one peer installer.

The live kernel has no requirements file. This module records the import
lines in ``cosmos/*.py`` and turns that measurement into installer
metadata. The day-one installer must not grow a hidden pip install:
a dependency is an import root the census classified THIRD, never a
package added because a stack "usually" needs it, and never a stdlib
name that happens to fail to import on Windows.
"""

from __future__ import annotations

import ast
import json
import sys
from dataclasses import dataclass
from pathlib import Path

from cosmos_federation import Refuse, bound_text

SCHEMA = "cosmos-federation-deps/1"

STDLIB = "STDLIB"
THIRD = "THIRD"
LOCAL = "LOCAL"

_NAME_LIMIT = 200

# Name list, not import success. ``fcntl`` is stdlib and is not a wheel
# this Windows peer should be told to pip-install.
_STDLIB: frozenset[str] = frozenset(sys.stdlib_module_names) | frozenset(sys.builtin_module_names)

# Behavior source for ``dayone_pyproject``. Missing means refuse, not a
# second root and not an empty dependency list that hides the miss.
_MEASURED_ROOT = Path(r"V:\A\Ai\COSMOS")


def classify_module(name: str) -> str:
    """Return STDLIB, THIRD, or LOCAL.

    LOCAL is a ``cosmos_*`` module or a relative import. Everything that
    is not that and not on the 3.14 standard-library name list is THIRD.
    """
    text = bound_text(name, limit=_NAME_LIMIT, name="module")
    if text.startswith("."):
        return LOCAL
    head = text.split(".", 1)[0]
    if head.startswith("cosmos_"):
        return LOCAL
    if head in _STDLIB:
        return STDLIB
    return THIRD


@dataclass(frozen=True, slots=True)
class ImportRow:
    """One imported module and the ``cosmos/*.py`` filenames that import it."""

    module: str
    kind: str
    used_by: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.kind != classify_module(self.module):
            raise Refuse("CENSUS", "kind")
        if not isinstance(self.used_by, tuple) or len(self.used_by) < 1:
            raise Refuse("CENSUS", "used_by")
        seen: set[str] = set()
        for name in self.used_by:
            filename = bound_text(name, limit=_NAME_LIMIT, name="used_by")
            if "/" in filename or "\\" in filename or filename in {".", ".."}:
                raise Refuse("CENSUS", "used_by")
            if filename in seen:
                raise Refuse("CENSUS", "used_by")
            seen.add(filename)


def _package_dir(root: Path) -> Path:
    if not isinstance(root, Path):
        raise Refuse("CENSUS", "root must be a Path")
    base = root.resolve()
    if not base.is_dir():
        raise Refuse("CENSUS", "root is not a directory")
    package = (base / "cosmos").resolve()
    try:
        package.relative_to(base)
    except ValueError:
        raise Refuse("CENSUS", "cosmos escaped root") from None
    if not package.is_dir():
        raise Refuse("CENSUS", "cosmos package missing")
    return package


def _modules_in(source: str) -> tuple[str, ...]:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        raise Refuse("CENSUS", "unparsed") from None
    found: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "":
                    raise Refuse("CENSUS", "empty import")
                found.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = "." * node.level + (node.module or "")
            if module == "":
                raise Refuse("CENSUS", "empty import")
            found.append(module)
    return tuple(found)


def census(root: Path) -> tuple[ImportRow, ...]:
    """Parse import and from lines in ``root/cosmos/*.py`` only.

    ``builds/`` is outside that glob. A file that resolves outside the
    package refuses. The row key is the imported module, not the bound
    name (``from pathlib import Path`` is ``pathlib``).
    """
    package = _package_dir(root)
    used: dict[str, set[str]] = {}
    for path in sorted(package.glob("*.py"), key=lambda item: item.name):
        if not path.is_file():
            continue
        resolved = path.resolve()
        if resolved.parent != package:
            raise Refuse("CENSUS", "file escaped package")
        try:
            source = resolved.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            raise Refuse("CENSUS", "unreadable") from None
        for module in _modules_in(source):
            used.setdefault(module, set()).add(resolved.name)
    rows: list[ImportRow] = []
    for module in sorted(used):
        rows.append(
            ImportRow(
                module=module,
                kind=classify_module(module),
                used_by=tuple(sorted(used[module])),
            )
        )
    return tuple(rows)


def _third_roots(rows: tuple[ImportRow, ...]) -> tuple[str, ...]:
    """Import roots only.

    A requirement on ``cryptography.hazmat.primitives`` is a different
    project name after PEP 503 normalization. That would be an invented
    package and a hidden pip install. The root ``cryptography`` is the
    module the census found.
    """
    roots: set[str] = set()
    for row in rows:
        if row.kind != THIRD:
            continue
        roots.add(row.module.split(".", 1)[0])
    return tuple(sorted(roots))


def _render_pyproject(roots: tuple[str, ...]) -> str:
    lines = [
        "# Day-one installer metadata.",
        "# Dependencies are THIRD import roots measured in cosmos/*.py.",
        "# The day-one installer must not grow a hidden pip install:",
        "# no extra project, no build backend, and no submodule renamed",
        "# into its own distribution. `tools` is the in-repo package",
        "# tools/surface.py, recorded here so a landing step does not",
        "# replace it with a PyPI fetch.",
        "[project]",
        'name = "cosmos-dayone"',
        'version = "0.1.0"',
        'description = "Day-one COSMOS peer. Requires Python 3.14 and the measured third-party import roots only."',
        'requires-python = ">=3.14"',
    ]
    if not roots:
        lines.append("dependencies = []")
    else:
        lines.append("dependencies = [")
        for name in roots:
            lines.append(f"    {json.dumps(name)},")
        lines.append("]")
    return "\n".join(lines) + "\n"


def dayone_pyproject() -> str:
    """Pyproject text for the measured live tree.

    Requires Python ``>=3.14``. The dependency list is the THIRD import
    roots ``census`` found under ``V:\\A\\Ai\\COSMOS`` and nothing else.
    An empty list is what this returns when that census finds no THIRD
    root. Callers write this same text; they do not extend it.
    """
    return _render_pyproject(_third_roots(census(_MEASURED_ROOT)))


__all__ = [
    "LOCAL",
    "SCHEMA",
    "STDLIB",
    "THIRD",
    "ImportRow",
    "census",
    "classify_module",
    "dayone_pyproject",
]
