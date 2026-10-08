"""Read-only seam check against the live Core and COSMOS Code trees.

Files are read as text. This module does not import ``cosmos`` or
``cosmos_code`` and does not write either tree.
"""

from __future__ import annotations

from pathlib import Path


def probe(cosmos_root: Path, code_root: Path) -> dict[str, object]:
    """Score the voice seam and the code package.

    Each row is ``name``, ``status`` (``PASS`` or ``MISSING``), and a short
    ``detail``. A missing file or a missing literal is ``MISSING``.
    """
    service = cosmos_root / "cosmos" / "cosmos_service.py"
    rows = [
        _score("voice_route", service, ("/api/v1/voice",)),
        _score(
            "cvm_routes",
            service,
            ("/api/v1/cvm/pull", "/api/v1/cvm/snapshot", "/api/v1/cvm/push"),
        ),
        _score(
            "max_transcript",
            cosmos_root / "cosmos" / "cosmos_voice.py",
            ("MAX_TRANSCRIPT = 4000",),
        ),
        _score(
            "known_kinds",
            cosmos_root / "cosmos" / "cosmos_cvm_projection.py",
            ("voice_session", '"pcm"'),
        ),
        _score(
            "code_package",
            code_root / "product" / "pyproject.toml",
            ('name = "cosmos-code"',),
        ),
        _score(
            "code_layers",
            code_root / "product" / "cosmos_code" / "doorspec.py",
            ("l1_role", "l8_mission"),
        ),
    ]
    return {"rows": rows}


def _score(name: str, path: Path, needles: tuple[str, ...]) -> dict[str, str]:
    text = _read(path)
    if text is None:
        return {"name": name, "status": "MISSING", "detail": "file missing"}
    absent = [needle for needle in needles if needle not in text]
    if absent:
        return {"name": name, "status": "MISSING", "detail": "missing " + ", ".join(absent)}
    return {"name": name, "status": "PASS", "detail": "present"}


def _read(path: Path) -> str | None:
    if not path.is_file():
        return None
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return None
