# Identity

## What this slice read

This slice read `V:\streams\federation\CONTRACT.md` (slot `identity`), `V:\streams\federation\README.md`, `check_tree_id` in `V:\streams\federation\cosmos_federation\product.py`, `V:\A\Ai\COSMOS\docs\federation\GRAYSON.md`, and the peer table in `V:\A\Ai\COSMOS\cosmos\cosmos_identity.py`.

## What is already true

Keith's live install names its own mesh in `cosmos_identity.py`. Grant and Grayson stay unassigned there, because an identity two people could answer to resolves to the wrong node. `probe_lan_node` reports `NO_HOST` while `host` is unset. The live module names no address for that case.

`docs/federation/GRAYSON.md` is one named person. His product was Crucible. His host is still `NO_HOST`. His mesh id is `UNASSIGNED`. That document is his install card. `check_tree_id` already refuses `KMesh-COSMOS-live` and `GMesh`.

## What this proposal adds

`peer_card` returns a frozen slotted `Card` for the day-one chat install. The fields are `tree_id`, `display_name`, `host` (`None`), `mesh_id` (`UNASSIGNED`), and `product` (`dayone-chat`). The card is the general installer record. Grayson remains the separate Crucible person above. This card leaves his mesh unassigned. Keith assigns a mesh id later. The card stores no address.

## Refusal codes

- `TREE_ID` — `check_tree_id` rejected the tree id. `KMesh-COSMOS-live` and `GMesh` take this path.
- `SECRET` — the display name is secret-shaped. The card is not built.
- `BOUND` — `bound_text` rejected the display name (empty, null, non-text, or longer than 80).

## How CCr lands it later

CCr lands `peer_card` beside the peer sentinel as the day-one chat identity. The landed record keeps `host` unset and `mesh_id` at `UNASSIGNED` until Keith names them. CCr leaves `GRAYSON.md` as that one person's Crucible card. The day-one product string stays `dayone-chat`.
