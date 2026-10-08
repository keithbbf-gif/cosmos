"""Clock and payload pins for the day-one installer."""

from __future__ import annotations

from cosmos_federation import (
    INSTALL_BUDGET_S,
    KEY_PASTE_BUDGET_S,
    SOFTWARE_BUDGET_S,
    Refuse,
    repo_disposition,
    secret_shape,
)
from package import SCHEMA, consider, members, missing_for_serve, steps, total_seconds

_ORDER = (
    "unpack_runtime",
    "apply_cold_root",
    "key_paste",
    "mint_secrets",
    "write_account",
    "bind_loopback",
    "open_chat_page",
)

_BLOCKED = ("npm", "npx", "cargo", "git clone", "rustc", "compiler")


def test_schema_and_clock() -> None:
    assert SCHEMA == "cosmos-federation-package/1"
    table = steps()
    assert tuple(step.name for step in table) == _ORDER
    assert all(isinstance(step.seconds, int) and not isinstance(step.seconds, bool) for step in table)
    paste = next(step for step in table if step.name == "key_paste")
    assert paste.seconds == KEY_PASTE_BUDGET_S
    software = sum(step.seconds for step in table if step.name != "key_paste")
    assert software <= SOFTWARE_BUDGET_S
    assert software == 90
    assert total_seconds() == sum(step.seconds for step in table)
    assert total_seconds() <= INSTALL_BUDGET_S
    assert total_seconds() == 120
    blob = "\n".join(f"{step.name}\n{step.detail}" for step in table).lower()
    for token in _BLOCKED:
        assert token not in blob
    assert "already" in next(step.detail for step in table if step.name == "unpack_runtime")
    for step in table:
        assert not secret_shape(repr(step))


def test_members_are_legal() -> None:
    found = members()
    rels = tuple(item.rel for item in found)
    assert "app/dayone.html" in rels
    assert "wizard/wizard.html" in rels
    assert "cosmos/cosmos.py" in rels
    assert "runtime/python-3.14.8-embed-amd64.zip" in rels
    assert "cosmos" not in rels
    assert "cosmos/" not in rels
    blob = "\n".join(rels).lower()
    for token in _BLOCKED:
        assert token not in blob
    for banned in (
        "api_token.txt",
        "install_key.bin",
        "live/",
        "BUCm.toml",
        "src-tauri",
        "cdeck",
        "serve.bat",
    ):
        assert banned not in blob
    for item in found:
        assert repo_disposition(item.rel) != "DENY"
        consider(item.rel)
        assert not secret_shape(repr(item))


# Module-level import closure of cosmos.py serve through cosmos_service.py
# and cosmos_kernel.py. Function-body imports are not in this tuple.
_SERVE_IMPORTS = (
    "cosmos_service.py",
    "cosmos_kernel.py",
    "cosmos_paths.py",
    "cosmos_ledger.py",
    "cosmos_lock.py",
    "cosmos_mail.py",
    "cosmos_sched.py",
    "cosmos_validate.py",
    "cosmos_cvm_projection.py",
    "cosmos_voice_hardening.py",
)


def test_missing_for_serve_names_the_load_gap() -> None:
    gap = missing_for_serve(_SERVE_IMPORTS)
    assert gap == ("cosmos_cvm_projection.py", "cosmos_voice_hardening.py")
    named = {_parts_name(item.rel) for item in members()}
    assert set(gap).isdisjoint(named)
    assert missing_for_serve(("cosmos/cosmos_kernel.py", "cosmos_spend.py")) == ()
    assert missing_for_serve((
        "cosmos/cosmos_cvm_projection.py",
        "cosmos_cvm_projection.py",
        "cosmos\\cosmos_voice_hardening.py",
    )) == ("cosmos_cvm_projection.py", "cosmos_voice_hardening.py")


def _parts_name(rel: str) -> str:
    return rel.replace("\\", "/").rsplit("/", 1)[-1]


def test_consider_refuses_deny_names() -> None:
    denied = (
        "live/config/api_token.txt",
        r"live\config\api_token.txt",
        "install_key.bin",
        "config/install_key.bin",
        "BUCm.toml",
        "BUcr.toml",
        "wizard/api_token.txt",
        "app/install_key.bin",
        "kdash/cosmos-voice.apk",
        r"builds\cdeck\src-tauri\target\release\cdeck.exe",
        "node_modules/leftpad/index.js",
    )
    for rel in denied:
        try:
            consider(rel)
        except Refuse as exc:
            assert exc.code == "DENY_MEMBER"
        else:
            raise AssertionError(rel)


def test_consider_refuses_dev_and_bare_trees() -> None:
    refused = (
        "cosmos",
        "cosmos/",
        "kdash",
        "builds/cdeck/ui/index.html",
        "tests/test_product.py",
    )
    for rel in refused:
        try:
            consider(rel)
        except Refuse as exc:
            assert exc.code == "NOT_SHIP"
        else:
            raise AssertionError(rel)
    consider("cosmos/cosmos.py")
    consider("kdash/index.html")
    consider("wizard/wizard.html")
    assert repo_disposition("cosmos/cosmos.py") == "SHIP"
