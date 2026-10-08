"""Read-only probe of the live Core tree and the COSMOS Code tree."""

from __future__ import annotations

from pathlib import Path

from cosmos_voice.compat import probe

_ROWS = (
    "voice_route",
    "cvm_routes",
    "max_transcript",
    "known_kinds",
    "code_package",
    "code_layers",
)


def test_probe_live_trees_pass() -> None:
    """Every seam row is PASS. A MISSING row fails with that row name."""
    found = probe(Path(r"V:\A\Ai\COSMOS"), Path(r"V:\streams\cosmos_code"))
    raw = found["rows"]
    assert isinstance(raw, list)
    names: list[str] = []
    for item in raw:
        assert isinstance(item, dict)
        name = item.get("name")
        assert item.get("status") == "PASS", name
        names.append(str(name))
    assert names == list(_ROWS)
