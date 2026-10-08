"""SOL on COSMOS CODE is not a Codex process."""

from __future__ import annotations

from pathlib import Path

from cosmos_code.own import seat_here


def test_sol_pack_lands_on_the_rail(tmp_path: Path):
    root = tmp_path / "attempt"
    built = seat_here("sol", root, "Write decode_rle from the stated rules.")
    assert built.door == "cosmos-code"
    assert built.pack_applied
    assert (root / "LOOP.md").is_file()
    assert (root / "TOOLS.md").read_text(encoding="utf-8").count("delete is not a tool") == 1
    assert (root / "PIN.md").read_text(encoding="utf-8") == "model=gpt-5.4\n"
    assert "codex" not in (root / "g47-plan.json").read_text(encoding="utf-8")
