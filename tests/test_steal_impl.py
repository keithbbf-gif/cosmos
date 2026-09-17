#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SGH steal-map item 9: _fail_/_bite_ waist lives in tools/; cosmos/ is shim.

Bodies were git-mv'd into tools/ (same basenames). cosmos/_fail_*.py and
cosmos/_bite_*.py re-export / runpy the tools/ file — not a copy of the body.
tools/__init__.py still exports ToolSurface / MCP_DOCS (F-29 surface).
JSON OUT paths stay under cosmos/. No second plugin loader.
"""
from __future__ import annotations

import py_compile
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
COSMOS = REPO / "cosmos"
TOOLS = REPO / "tools"


def _waist_names() -> list[str]:
    names = sorted(
        {p.name for p in TOOLS.glob("_fail_*.py")}
        | {p.name for p in TOOLS.glob("_bite_*.py")}
    )
    return names


def test_tools_surface_exports_untouched():
    sys.path.insert(0, str(REPO))
    import tools as tools_pkg  # noqa: WPS433

    assert hasattr(tools_pkg, "ToolSurface")
    assert hasattr(tools_pkg, "MCP_DOCS")
    init = (TOOLS / "__init__.py").read_text(encoding="utf-8")
    assert "from .surface import" in init and "ToolSurface" in init
    assert "from .mcp_docs import" in init and "MCP_DOCS" in init
    # Waist scripts are not a second plugin loader and are not re-exported.
    assert "_fail_" not in init and "_bite_" not in init


def test_waist_bodies_in_tools_shims_in_cosmos():
    names = _waist_names()
    assert len(names) >= 48
    for name in names:
        body = TOOLS / name
        shim = COSMOS / name
        assert body.is_file(), name
        assert shim.is_file(), name
        body_txt = body.read_text(encoding="utf-8")
        shim_txt = shim.read_text(encoding="utf-8")
        assert "runpy.run_path" in shim_txt, name
        assert "tools/" in shim_txt, name
        assert "not a copy" in shim_txt, name
        assert "runpy.run_path" not in body_txt, name
        # Shim is not a copy of the body.
        assert "all_new_pins_failed" not in shim_txt
        assert "def reconstruct_prober" not in shim_txt


def test_shims_and_bodies_compile():
    for name in _waist_names():
        py_compile.compile(str(TOOLS / name), doraise=True)
        py_compile.compile(str(COSMOS / name), doraise=True)


def test_in_tree_import_shim_reexports_bite_check():
    sys.path.insert(0, str(REPO))
    import cosmos._bite_check_f24_f25 as bite  # noqa: WPS433

    assert callable(getattr(bite, "reconstruct_prober", None))
    assert callable(getattr(bite, "main", None))


def test_exec_old_path_via_shim():
    """`py cosmos/_fail_p13_voice_drop_against_old.py` still runs (cheap pin)."""
    script = COSMOS / "_fail_p13_voice_drop_against_old.py"
    proc = subprocess.run(
        [sys.executable, str(script)],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "pin_passes" in (proc.stdout or "")


def test_json_out_stays_in_cosmos():
    """Moved HERE-based bodies still point OUT at cosmos/, not tools/."""
    src = (TOOLS / "_bite_p13_voice_drop.py").read_text(encoding="utf-8")
    assert 'HERE = Path(__file__).resolve().parent.parent / "cosmos"' in src
    assert 'OUT = HERE / "_bite_p13_voice_drop.json"' in src
    repo_src = (TOOLS / "_fail_f30_against_old.py").read_text(encoding="utf-8")
    assert 'OUT = REPO / "cosmos" / "_fail_f30_against_old.json"' in repo_src


def main() -> int:
    test_tools_surface_exports_untouched()
    test_waist_bodies_in_tools_shims_in_cosmos()
    test_shims_and_bodies_compile()
    test_in_tree_import_shim_reexports_bite_check()
    test_exec_old_path_via_shim()
    test_json_out_stays_in_cosmos()
    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
