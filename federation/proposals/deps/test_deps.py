"""Census pins for the day-one dependency list."""

from __future__ import annotations

import tomllib
from pathlib import Path

from cosmos_federation import PathJail, Refuse, secret_shape
from deps import SCHEMA, ImportRow, census, classify_module, dayone_pyproject

_LIVE = Path(r"V:\A\Ai\COSMOS")
_THIRD_MODULES = (
    "cryptography",
    "cryptography.hazmat.primitives",
    "cryptography.hazmat.primitives.asymmetric",
    "cryptography.x509.oid",
    "tools.surface",
    "vosk",
    "watchdog.events",
    "watchdog.observers",
)
_THIRD_ROOTS = ("cryptography", "tools", "vosk", "watchdog")


def _write(jail: PathJail, rel: str, text: str) -> None:
    dest = jail.contain(rel)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(text, encoding="utf-8")


def test_schema() -> None:
    assert SCHEMA == "cosmos-federation-deps/1"


def test_classify_json_is_stdlib_and_made_up_is_third() -> None:
    assert classify_module("json") == "STDLIB"
    assert classify_module("made-up") == "THIRD"
    assert classify_module("os.path") == "STDLIB"
    # Present on the 3.14 name list. A failed Windows import is not a wheel.
    assert classify_module("fcntl") == "STDLIB"
    assert classify_module("cosmos_paths") == "LOCAL"
    assert classify_module(".sibling") == "LOCAL"
    assert classify_module("cryptography.hazmat.primitives") == "THIRD"


def test_blank_module_refuses() -> None:
    try:
        classify_module("")
    except Refuse as exc:
        assert exc.code == "BOUND"
    else:
        raise AssertionError("blank")


def test_row_is_frozen() -> None:
    row = ImportRow("json", "STDLIB", ("alpha.py",))
    try:
        setattr(row, "module", "os")
    except AttributeError:
        return
    raise AssertionError("frozen")


def test_row_refuses_a_kind_that_disagrees() -> None:
    try:
        ImportRow("json", "THIRD", ("alpha.py",))
    except Refuse as exc:
        assert exc.code == "CENSUS"
    else:
        raise AssertionError("kind")


def test_census_reads_cosmos_py_only(scratch: Path) -> None:
    jail = PathJail(scratch)
    _write(
        jail,
        "cosmos/alpha.py",
        "\n".join((
            "from __future__ import annotations",
            "import json",
            "import os.path",
            "from cosmos_paths import CosmosPaths",
            "from .sibling import name",
            "import madeup_widget",
            "from madeup_widget.sub import piece",
            "note = 'api_key=not-an-import'",
            "",
        )),
    )
    _write(
        jail,
        "cosmos/beta.py",
        "import json\nfrom cosmos_paths import extended\nimport fcntl\n",
    )
    _write(jail, "cosmos/nested/skip.py", "import nested_only_pkg\n")
    _write(jail, "builds/cdeck/nope.py", "import invented_build_dep\n")
    rows = census(scratch)
    by = {row.module: row for row in rows}
    assert by["json"].kind == "STDLIB"
    assert by["json"].used_by == ("alpha.py", "beta.py")
    assert by["os.path"].kind == "STDLIB"
    assert by["os.path"].used_by == ("alpha.py",)
    assert by["fcntl"].kind == "STDLIB"
    assert by["cosmos_paths"].kind == "LOCAL"
    assert by["cosmos_paths"].used_by == ("alpha.py", "beta.py")
    assert by[".sibling"].kind == "LOCAL"
    assert by["madeup_widget"].kind == "THIRD"
    assert by["madeup_widget.sub"].kind == "THIRD"
    assert by["__future__"].kind == "STDLIB"
    assert "nested_only_pkg" not in by
    assert "invented_build_dep" not in by
    blob = repr(rows)
    assert "api_key=" not in blob
    assert not secret_shape(blob)


def test_census_refuses_closed(scratch: Path) -> None:
    try:
        census(scratch)
    except Refuse as exc:
        assert exc.code == "CENSUS"
    else:
        raise AssertionError("missing package")
    jail = PathJail(scratch)
    target = jail.contain("not-a-root")
    target.write_text("x", encoding="utf-8")
    try:
        census(target)
    except Refuse as exc:
        assert exc.code == "CENSUS"
    else:
        raise AssertionError("file root")
    _write(jail, "cosmos/bad.py", "import (\n")
    try:
        census(scratch)
    except Refuse as exc:
        assert exc.code == "CENSUS"
    else:
        raise AssertionError("unparsed")


def test_census_refuses_unreadable(scratch: Path) -> None:
    jail = PathJail(scratch)
    dest = jail.contain("cosmos/badenc.py")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(b"\xff\xfe import json\n")
    try:
        census(scratch)
    except Refuse as exc:
        assert exc.code == "CENSUS"
    else:
        raise AssertionError("unreadable")


def test_live_third_modules_match_the_measurement() -> None:
    rows = census(_LIVE)
    got = tuple(row.module for row in rows if row.kind == "THIRD")
    assert got == _THIRD_MODULES
    by = {row.module: row for row in rows}
    assert by["cryptography"].used_by == ("cosmos_service.py",)
    assert by["cryptography.hazmat.primitives"].used_by == ("cosmos_service.py",)
    assert by["tools.surface"].used_by == ("_f29_composed_live.py",)
    assert by["vosk"].used_by == ("cosmos_stt.py",)
    assert by["watchdog.events"].used_by == ("cosmos_sched.py",)
    assert by["watchdog.observers"].used_by == ("cosmos_sched.py",)
    assert by["json"].kind == "STDLIB"
    assert by["cosmos_paths"].kind == "LOCAL"
    for absent in ("requests", "openai", "anthropic", "playwright", "numpy", "setuptools"):
        assert absent not in by
    for row in rows:
        assert not secret_shape(repr(row))


def test_dayone_pyproject_is_the_file_and_the_census() -> None:
    text = dayone_pyproject()
    written = Path(__file__).resolve().parent / "pyproject.proposed.toml"
    assert written.read_text(encoding="utf-8") == text
    parsed = tomllib.loads(text)
    project = parsed["project"]
    assert project["requires-python"] == ">=3.14"
    assert tuple(project["dependencies"]) == _THIRD_ROOTS
    assert "[build-system]" not in text
    assert "setuptools" not in text
    assert "cryptography.hazmat" not in text
    assert "watchdog.observers" not in text
    roots: set[str] = set()
    for row in census(_LIVE):
        if row.kind == "THIRD":
            roots.add(row.module.split(".", 1)[0])
    assert tuple(sorted(roots)) == tuple(project["dependencies"])
