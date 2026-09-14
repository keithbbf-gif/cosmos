"""Runtime check for SLPWOW free-resources curriculum briefs."""

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
CHECK = ROOT / "content/slpwow-free-resources-curriculum/check_curriculum.py"
FOLDER = ROOT / "content/slpwow-free-resources-curriculum"


def test_check_curriculum_pass():
    proc = subprocess.run(
        [sys.executable, str(CHECK)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "PASS  slpwow-free-resources-curriculum" in proc.stdout


def test_pack_furniture_exists():
    for name in (
        "CLAIMS_GUARDRAILS.md",
        "INDEX.md",
        "README.md",
        "EDITOR_REPORT.md",
        "manifest.toml",
    ):
        assert (FOLDER / name).is_file(), name


def test_all_markdown_voice_check_edited():
    for path in FOLDER.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        assert text.startswith("---\n"), path.name
        assert "voice_check: edited" in text.split("---\n", 2)[1], path.name
