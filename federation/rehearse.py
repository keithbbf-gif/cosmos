# ruff: noqa: E402, I001
"""Run the day-one story on an empty directory. No network and no live tree.

The clock in ``package.steps`` is the allowance. This function is the
order those steps have to happen in, using the proposal modules. It
stops before any model call: ``fake_reply`` stands in for the body
``request_body`` would POST. A real reply is CCr landing
``POST /api/v1/dayone/chat`` on Core.
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
_PROPOSALS = _ROOT / "proposals"
if _PROPOSALS.is_dir():
    for _child in sorted(_PROPOSALS.iterdir()):
        if _child.is_dir() and str(_child) not in sys.path:
            sys.path.insert(0, str(_child))

from account import open_account
from bindpol import decide
from chatwindow import issue_nonce, page, redeem
from coldroot import apply
from cosmos_federation import DEFAULT_CAP_USD_MICROS, PathJail, repo_disposition
from domdefer import choose
from identity import peer_card
from ledgerboot import apply as apply_ledger
from package import members, total_seconds
from seat import bind, fake_reply, request_body, suggested_pin, user_turn
from secrets import acknowledge, mint, write_files  # type: ignore[attr-defined]
from spendcap import open_book, reserve, settle
from wizard import accept_key, begin, ready, submit

SCHEMA = "cosmos-federation-rehearse/1"

# Fixed bytes so a test can replay the story. Not key material by themselves;
# mint encodes them and then the report keeps only ids.
_DRAW_SEED = bytes(range(64))


def _draw(n: int) -> bytes:
    if n < 1 or n > len(_DRAW_SEED):
        raise RuntimeError("draw length")
    return _DRAW_SEED[:n]


def rehearse(root: Path, now: int = 1_700_000_000) -> dict[str, object]:
    """Install a peer in ``root`` and return a report that contains no secrets.

    ``root`` must be an empty directory the caller created. The pasted key
    exists only as the argument to ``accept_key`` and is not stored.
    """
    if not isinstance(root, Path) or not root.is_dir():
        raise RuntimeError("root")
    # Identity is a new tree id. The public repo's id is taken.
    tree_id = "Peer-1"
    wizard = begin(now)
    wizard = submit(wizard, "root", "peer-root", now)
    wizard = submit(wizard, "tree_id", tree_id, now)
    wizard = submit(wizard, "name", "Peer", now)
    wizard = submit(wizard, "door", "openrouter", now)
    # The shape is what the wizard demands. The value is not retained.
    wizard = accept_key(wizard, "sk-" + ("a" * 16), "peer-openrouter", now)
    wizard = submit(wizard, "cap", str(DEFAULT_CAP_USD_MICROS), now)
    wizard = submit(wizard, "bind", "loopback", now)
    if not ready(wizard):
        raise RuntimeError("wizard")
    if wizard.tree_id is None or wizard.name is None or wizard.door is None:
        raise RuntimeError("wizard")
    if wizard.credential_id is None or wizard.cap_usd_micros is None:
        raise RuntimeError("wizard")

    jail = PathJail(root)
    # Sentinel and role directories. The key file is the next step, not this one.
    apply(jail, wizard.tree_id, now)
    minted = mint(_draw, now)
    if minted.show_token is None or minted.install_key is None:
        raise RuntimeError("mint")
    write_files(jail, minted.show_token, minted.install_key)
    # After this, the report can be logged. The bearer is no longer on the object.
    minted = acknowledge(minted)
    card = peer_card(wizard.tree_id, wizard.name)
    account = open_account(wizard.name, wizard.door, wizard.credential_id, now)
    # A key id selects the API. A browser profile does not skip the paste.
    door_choice = choose(has_key_id=True, has_browser_profile=False, ask_scrape=False)
    pin = suggested_pin(account.door)
    seat = bind(account.door, account.credential_id, pin, wizard.cap_usd_micros)
    turn = user_turn(seat, "hello")
    body = request_body(turn)
    book = open_book(seat.cap_usd_micros)
    book = reserve(book, 1_000, now, "turn-1")
    reply = fake_reply(turn, "ready", 1_000)
    book = settle(book, "turn-1", reply.usd_micros, now)
    ledger_path = apply_ledger(jail, wizard.tree_id, now)
    binding = decide("127.0.0.1", 8770, False, False, False)
    nonce = issue_nonce(_draw, now)
    cookie = redeem(nonce, nonce.code, now, False)
    document = page()
    # Members are the payload. A DENY path must not be in that list.
    payload = tuple(item.rel for item in members())
    for rel in payload:
        if repo_disposition(rel) == "DENY":
            raise RuntimeError("deny member")
    report: dict[str, object] = {
        "schema": SCHEMA,
        "ready": True,
        "tree_id": card.tree_id,
        "host": card.host,
        "mesh_id": card.mesh_id,
        "product": card.product,
        "door": account.door,
        "via": door_choice.via,
        "phase": door_choice.phase,
        "pin": seat.pin,
        "model": body.get("model"),
        "cap_usd_micros": seat.cap_usd_micros,
        "settled_events": len(book.events),
        "reply": reply.text,
        "bind_host": binding.host,
        "bind_port": binding.port,
        "scheme": binding.scheme,
        "auth": binding.auth,
        "token_id": minted.token_id,
        "key_id": minted.key_id,
        "show_token": minted.show_token,
        "cookie_host": cookie.host,
        "cookie_http_only": cookie.http_only,
        "ledger": str(ledger_path.relative_to(root)),
        "page_has_route": "/api/v1/dayone/chat" in document,
        "seconds": total_seconds(),
        "members": len(payload),
    }
    blob = repr(report)
    if "sk-" in blob or minted.show_token is not None:
        raise RuntimeError("secret in report")
    return report


__all__ = ["SCHEMA", "rehearse"]
