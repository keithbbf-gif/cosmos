"""Pins for the stranger credential catalog."""

from __future__ import annotations

from cosmos_federation import Refuse, secret_shape
from credcat import SCHEMA, Cred, catalog


def _by_name(name: str) -> Cred:
    matches = [row for row in catalog() if row.name == name]
    assert len(matches) == 1
    return matches[0]


def _by_filename(filename: str) -> Cred:
    matches = [row for row in catalog() if row.filename == filename]
    assert len(matches) == 1
    return matches[0]


def test_api_token_is_day_one_anthropic_refused_r2_later() -> None:
    assert SCHEMA == "cosmos-federation-credcat/1"
    assert _by_filename("api_token.txt").phase == "DAY_ONE"
    assert _by_name("anthropic").phase == "REFUSED"
    assert _by_filename("anthropic_api_key.txt").phase == "REFUSED"
    assert _by_name("r2").phase == "LATER"
    assert _by_filename("r2_credentials.json").phase == "LATER"
    for row in catalog():
        assert "sk-" not in row.why
        assert row.filename is None or "sk-" not in row.filename
        assert not secret_shape(row.why)
        assert row.filename is None or not secret_shape(row.filename)
        assert "sk-" not in repr(row)


def test_day_one_files_are_minted_or_one_of_two_doors() -> None:
    rows = catalog()
    assert isinstance(rows, tuple)
    day_one = {row.filename for row in rows if row.phase == "DAY_ONE"}
    assert day_one == {
        "api_token.txt",
        "install_key.bin",
        "openrouter_api_key.txt",
        "xai_api_key.txt",
    }
    assert _by_filename("install_key.bin").phase == "DAY_ONE"
    assert _by_filename("openrouter_api_key.txt").name == "openrouter"
    assert _by_filename("xai_api_key.txt").phase == "DAY_ONE"


def test_later_and_refused_match_the_stranger_clock() -> None:
    later = {row.name: row.filename for row in catalog() if row.phase == "LATER"}
    assert later == {
        "r2": "r2_credentials.json",
        "tailscale": None,
        "cursor": "cursor_cosmos_key.txt",
        "codex": "openai_api_key.txt",
        "firecrawl": "firecrawl_api_key.txt",
        "kill_token": "kill_token.txt",
    }
    assert _by_name("tailscale").filename is None
    refused = _by_name("r2cloner")
    assert refused.phase == "REFUSED"
    assert refused.filename is None
    filenames = {row.filename for row in catalog()}
    assert "groq_api_key.txt" not in filenames
    assert catalog() == catalog()


def test_rows_are_one_sentence_and_frozen() -> None:
    for row in catalog():
        assert isinstance(row, Cred)
        assert row.phase in {"DAY_ONE", "LATER", "REFUSED"}
        assert row.why.endswith(".")
        assert row.why.count(".") == 1
        assert row.filename is None or ("/" not in row.filename and "\\" not in row.filename)
    cred = _by_name("bearer")
    try:
        setattr(cred, "why", "Changed.")
    except AttributeError:
        return
    raise AssertionError("frozen")


def test_refuses_bad_phase_secret_path_and_extra_sentence() -> None:
    try:
        Cred(name="nope", phase="NOW", filename=None, why="Not a peer phase.")
    except Refuse as exc:
        assert exc.code == "PHASE"
    else:
        raise AssertionError("phase")
    leaked = "sk-" + "a" * 12
    try:
        Cred(name="leak", phase="LATER", filename=None, why=f"Holds {leaked} which is not stored.")
    except Refuse as exc:
        assert exc.code == "SECRET"
    else:
        raise AssertionError("secret")
    try:
        Cred(
            name="clone",
            phase="REFUSED",
            filename="D:/R2Cloner/store",
            why="A path is not a config basename.",
        )
    except Refuse as exc:
        assert exc.code == "PATH"
    else:
        raise AssertionError("path")
    try:
        Cred(name="bare", phase="DAY_ONE", filename=None, why="Day one needs a file.")
    except Refuse as exc:
        assert exc.code == "FILE"
    else:
        raise AssertionError("file")
    try:
        Cred(name="long", phase="LATER", filename=None, why="First thought. Second thought.")
    except Refuse as exc:
        assert exc.code == "WHY"
    else:
        raise AssertionError("why")
