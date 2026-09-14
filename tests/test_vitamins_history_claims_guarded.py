"""Runtime check for staged vitamin-history drafts."""

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
LINT = ROOT / "content/vitamins-history-claims-guarded/tools/claims_lint.py"
FOLDER = ROOT / "content/vitamins-history-claims-guarded"


def test_claims_lint_pass():
    proc = subprocess.run(
        [sys.executable, str(LINT)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "CLAIMS_LINT PASS" in proc.stdout


def test_folder_furniture_exists():
    for name in (
        "CLAIMS_GUARDRAILS.md",
        "README.md",
        "STAGING.md",
        "SOURCES.md",
    ):
        assert (FOLDER / name).is_file(), name


def test_draft_count_at_least_forty():
    drafts = list(FOLDER.glob("VH-*.md"))
    assert len(drafts) >= 40, len(drafts)
