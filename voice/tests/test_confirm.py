"""Tests for the single-use confirm gate."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest
from cosmos_voice.confirm import ConfirmGate


def test_pending_starts_empty() -> None:
    """Nothing is pending until a confirm reply is observed."""
    assert ConfirmGate().pending() is None


def test_observe_stores_and_returns_id() -> None:
    """A real confirm reply stores the id and a later one replaces it."""
    gate = ConfirmGate()
    body: dict[str, object] = {"needs_confirm": True, "confirm_id": "n1"}
    assert gate.observe(body) == "n1"
    assert gate.pending() == "n1"
    assert gate.observe({"needs_confirm": True, "confirm_id": "n2"}) == "n2"
    assert gate.pending() == "n2"


@pytest.mark.parametrize(
    "body",
    [
        {},
        {"needs_confirm": False, "confirm_id": "x"},
        {"needs_confirm": True, "confirm_id": ""},
        {"needs_confirm": True},
        {"needs_confirm": True, "confirm_id": 12},
        {"needs_confirm": "true", "confirm_id": "x"},
        {"needs_confirm": 1, "confirm_id": "x"},
        {"confirm_id": "x"},
    ],
)
def test_observe_ignores_non_confirm(body: dict[str, object]) -> None:
    """A reply that is not a confirm ask does not clear the stored id."""
    gate = ConfirmGate()
    gate.observe({"needs_confirm": True, "confirm_id": "keep"})
    assert gate.observe(body) == ""
    assert gate.pending() == "keep"


def test_accept_yes_and_confirm_is_single_use() -> None:
    """The first yes or confirm returns the id; the next one does not."""
    gate = ConfirmGate()
    gate.observe({"needs_confirm": True, "confirm_id": "n1"})
    assert gate.accept_phrase("Yes!") == "n1"
    assert gate.pending() is None
    assert gate.accept_phrase("yes") is None
    assert gate.accept_phrase("confirm") is None
    gate.observe({"needs_confirm": True, "confirm_id": "n2"})
    assert gate.accept_phrase("  Confirm, do it ") == "n2"
    assert gate.pending() is None


def test_accept_first_word_only() -> None:
    """Only the first word counts, after punctuation is stripped."""
    gate = ConfirmGate()
    gate.observe({"needs_confirm": True, "confirm_id": "cid"})
    assert gate.accept_phrase("(yes) please") == "cid"
    gate.observe({"needs_confirm": True, "confirm_id": "cid"})
    assert gate.accept_phrase("confirm the shutdown") == "cid"


def test_other_words_do_not_accept_or_clear() -> None:
    """A near miss is not yes, and it leaves the nonce pending."""
    gate = ConfirmGate()
    gate.observe({"needs_confirm": True, "confirm_id": "n1"})
    assert gate.accept_phrase("please yes") is None
    assert gate.accept_phrase("yesterday") is None
    assert gate.accept_phrase("confirmation") is None
    assert gate.accept_phrase("ok") is None
    assert gate.accept_phrase("yeah") is None
    assert gate.pending() == "n1"


def test_silence_is_not_yes() -> None:
    """Silence and whitespace neither accept nor clear."""
    gate = ConfirmGate()
    gate.observe({"needs_confirm": True, "confirm_id": "n1"})
    assert gate.accept_phrase("") is None
    assert gate.accept_phrase("   ") is None
    assert gate.accept_phrase("...") is None
    assert gate.reject_phrase("") is False
    assert gate.reject_phrase("   ") is False
    assert gate.pending() == "n1"


def test_yes_with_nothing_pending_returns_none() -> None:
    """An accept word does not invent an id."""
    gate = ConfirmGate()
    assert gate.accept_phrase("yes") is None
    assert gate.pending() is None


def test_reject_no_and_cancel_clears() -> None:
    """``no`` and ``cancel`` drop the nonce so a later yes cannot fire it."""
    gate = ConfirmGate()
    gate.observe({"needs_confirm": True, "confirm_id": "n1"})
    assert gate.reject_phrase("No, thanks") is True
    assert gate.pending() is None
    assert gate.accept_phrase("yes") is None
    gate.observe({"needs_confirm": True, "confirm_id": "n2"})
    assert gate.reject_phrase("CANCEL!") is True
    assert gate.pending() is None


def test_reject_first_word_only_and_does_not_clear_on_miss() -> None:
    """``nope`` and a trailing no are not rejections."""
    gate = ConfirmGate()
    gate.observe({"needs_confirm": True, "confirm_id": "n1"})
    assert gate.reject_phrase("nope") is False
    assert gate.reject_phrase("not now") is False
    assert gate.reject_phrase("please no") is False
    assert gate.pending() == "n1"
    assert gate.reject_phrase("cancel that") is True
    assert gate.pending() is None


def test_reject_without_pending_is_still_true() -> None:
    """The phrase match does not depend on an id already being stored."""
    gate = ConfirmGate()
    assert gate.reject_phrase("no") is True
    assert gate.pending() is None


def test_accept_does_not_treat_no_as_yes() -> None:
    """A rejection word is not an acceptance, and it stays pending here."""
    gate = ConfirmGate()
    gate.observe({"needs_confirm": True, "confirm_id": "n1"})
    assert gate.accept_phrase("no") is None
    assert gate.accept_phrase("cancel") is None
    assert gate.pending() == "n1"


def test_confirm_module_does_not_import_a_client() -> None:
    """The gate source does not import a network stack."""
    path = Path(__file__).resolve().parents[1] / "cosmos_voice" / "confirm.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.add(alias.name.split(".", maxsplit=1)[0])
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            modules.add(node.module.split(".", maxsplit=1)[0])
    assert "string" in modules
    assert modules.isdisjoint({"socket", "urllib", "http", "requests", "httpx"})
