"""Pins for the day-one chat identity card."""

from __future__ import annotations

from cosmos_federation import Refuse
from identity import SCHEMA, Card, peer_card


def test_legal_card() -> None:
    card = peer_card("Peer-1", "Ada")
    assert card == Card("Peer-1", "Ada")
    assert card.tree_id == "Peer-1"
    assert card.display_name == "Ada"
    assert card.host is None
    assert card.mesh_id == "UNASSIGNED"
    assert card.product == "dayone-chat"
    assert SCHEMA == "cosmos-federation-identity/1"
    assert set(Card.__slots__) == {
        "tree_id",
        "display_name",
        "host",
        "mesh_id",
        "product",
    }


def test_kmesh_cosmos_live_is_refused() -> None:
    try:
        peer_card("KMesh-COSMOS-live", "Ada")
    except Refuse as exc:
        assert exc.code == "TREE_ID"
    else:
        raise AssertionError("KMesh-COSMOS-live")


def test_secret_shaped_display_name_is_refused() -> None:
    secret = "sk-" + ("a" * 12)
    try:
        peer_card("Peer-1", secret)
    except Refuse as exc:
        assert exc.code == "SECRET"
        assert secret not in str(exc)
    else:
        raise AssertionError("secret")
