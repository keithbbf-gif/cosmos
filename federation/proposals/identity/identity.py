"""Day-one peer card for a chat install.

Grayson is one named person whose product was Crucible and whose host is
still NO_HOST. This card is the day-one chat install. It does not assign
him GMesh. Keith assigns a mesh id. Until then the id stays UNASSIGNED.
Host stays None: an address is a later name, not a field on this card.
"""

from __future__ import annotations

from dataclasses import dataclass

from cosmos_federation import Refuse, bound_text, check_tree_id, secret_shape

SCHEMA = "cosmos-federation-identity/1"


@dataclass(frozen=True, slots=True)
class Card:
    """General day-one chat card. Not Grayson's Crucible card.

    host is None on purpose. The card has no address field. mesh_id stays
    UNASSIGNED so this module does not invent GMesh or any other mesh id.
    """

    tree_id: str
    display_name: str
    host: None = None
    mesh_id: str = "UNASSIGNED"
    product: str = "dayone-chat"


def peer_card(tree_id: str, display_name: str) -> Card:
    """Return one day-one chat card, or refuse.

    A taken or malformed tree id refuses as TREE_ID via check_tree_id.
    A secret-shaped display name refuses as SECRET before a Card exists,
    so key material never lands in repr. An empty name refuses as BOUND.
    """
    checked = check_tree_id(tree_id)
    if secret_shape(display_name):
        raise Refuse("SECRET", "display name")
    # bound_text refuses empty, null, non-text, and anything past 80.
    name = bound_text(display_name, limit=80, name="display_name")
    return Card(tree_id=checked, display_name=name)


__all__ = ["SCHEMA", "Card", "peer_card"]
