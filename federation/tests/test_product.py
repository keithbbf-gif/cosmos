"""Pins for the shared day-one law."""

from __future__ import annotations

from pathlib import Path

from cosmos_federation import (
    DEFAULT_PORT,
    INSTALL_BUDGET_S,
    PathJail,
    Refuse,
    check_cap,
    check_door,
    check_tree_id,
    const_eq,
    redact,
    repo_disposition,
    secret_shape,
)


def test_tree_id_accepts_a_new_peer_and_refuses_taken_names() -> None:
    assert check_tree_id("Peer-1") == "Peer-1"
    for taken in ("GMesh", "KMesh-COSMOS-live", "live", "", "C:\\root", "sk-abcdefghij"):
        try:
            check_tree_id(taken)
        except Refuse as exc:
            assert exc.code == "TREE_ID"
        else:
            raise AssertionError(taken)


def test_anthropic_is_off_and_the_two_doors_stay() -> None:
    assert check_door("OpenRouter") == "openrouter"
    assert check_door("xai") == "xai"
    try:
        check_door("anthropic")
    except Refuse as exc:
        assert exc.code == "ANTHROPIC_OFF"
    else:
        raise AssertionError("anthropic")
    try:
        check_door("other")
    except Refuse as exc:
        assert exc.code == "DOOR"
    else:
        raise AssertionError("other")


def test_cap_policy_is_one_dollar() -> None:
    assert check_cap(1) == 1
    assert check_cap(1_000_000) == 1_000_000
    for bad in (0, -1, 1_000_001, True):
        try:
            check_cap(bad)
        except Refuse as exc:
            assert exc.code == "CAP"
        else:
            raise AssertionError(bad)


def test_repo_disposition_ships_code_and_denies_live_secrets() -> None:
    assert repo_disposition("cosmos/cosmos.py") == "SHIP"
    assert repo_disposition("kdash/index.html") == "SHIP"
    assert repo_disposition("README.md") == "SHIP"
    assert repo_disposition("tests/test_product.py") == "DEV"
    assert repo_disposition("builds/cdeck/ui/index.html") == "DEV"
    assert repo_disposition("live/config/api_token.txt") == "DENY"
    assert repo_disposition("BUCm.toml") == "DENY"
    assert repo_disposition("config/openai_api_key.txt") == "DENY"
    assert repo_disposition("node_modules/leftpad/index.js") == "DENY"
    assert repo_disposition(r"src-tauri\target\release\cdeck.exe") == "DENY"
    assert repo_disposition(r"V:\A\Ai\COSMOS\cosmos\cosmos.py") == "DENY"
    assert repo_disposition("../secrets.txt") == "DENY"


def test_secret_shape_redacts_and_compare_is_exact() -> None:
    raw = "sk-" + "a" * 12
    assert secret_shape(raw)
    assert "sk-" not in redact("prefix " + raw + " suffix")
    assert const_eq("same", "same")
    assert not const_eq("same", "same!")
    assert INSTALL_BUDGET_S == 120
    assert DEFAULT_PORT == 8770


def test_jail_contains_relative_writes(scratch: Path) -> None:
    jail = PathJail(scratch)
    target = jail.contain("config/api_token.txt")
    assert scratch.resolve() in target.parents
    for bad in ("../outside.txt", "C:/Windows/notepad.exe", "//server/share", "file:///etc/passwd", ""):
        try:
            jail.contain(bad)
        except Refuse as exc:
            assert exc.code == "PATH"
        else:
            raise AssertionError(bad)


def test_jail_refuses_device_names_and_streams(scratch: Path) -> None:
    jail = PathJail(scratch)
    blocked = (
        "NUL",
        "con",
        "PRN.txt",
        "aux",
        "COM1",
        "lpt9.dat",
        "config/NUL",
        "config/api_token.txt:stream",
        "notes/file.txt:Zone.Identifier",
    )
    for rel in blocked:
        try:
            jail.contain(rel)
        except Refuse as exc:
            assert exc.code == "PATH"
            assert exc.detail == "device or stream"
        else:
            raise AssertionError(rel)
    plain = jail.contain("null.txt")
    assert plain.name == "null.txt"
    assert scratch.resolve() in plain.parents
