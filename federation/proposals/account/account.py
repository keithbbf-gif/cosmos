"""A day-one account is a person plus a door id, not a copy of Keith's keys.

The live tree keeps key bytes in config files the peer pastes on their own
machine. This object stores the credential id only, so a later seat can name
that key without holding it. Anthropic stays off the route.
"""

from __future__ import annotations

from dataclasses import dataclass

from cosmos_federation import Refuse, bound_int, bound_text, check_door, redact, secret_shape

SCHEMA = "cosmos-federation-account/1"

# A display name is a label. The same cap keeps a credential id a handle.
_NAME_LIMIT = 80
_ID_LIMIT = 80
# Caller epoch, not time.time. Negative is not a creation time.
_EPOCH_HI = 2**63 - 1


def _show(value: object) -> str:
    """One field for repr. Strings are redacted. Other types add no text."""
    if isinstance(value, str):
        return repr(redact(value))
    if isinstance(value, bool) or not isinstance(value, int):
        return "''"
    return repr(value)


def _fields(
    name: object,
    door: object,
    credential_id: object,
    now: object,
) -> tuple[str, str, str, int]:
    # A display name is not a place to park a pasted key. Shape before the
    # length cap, so a long key is SECRET and not BOUND.
    if isinstance(name, str) and secret_shape(name):
        raise Refuse("SECRET")
    checked_name = bound_text(name, limit=_NAME_LIMIT, name="name")
    if not isinstance(door, str):
        raise Refuse("DOOR", "unknown door")
    checked_door = check_door(door)
    # Shape before the length cap, so a long key is SECRET and not BOUND.
    if isinstance(credential_id, str) and secret_shape(credential_id):
        raise Refuse("SECRET")
    checked_id = bound_text(credential_id, limit=_ID_LIMIT, name="credential_id")
    created = bound_int(now, lo=0, hi=_EPOCH_HI, name="now")
    return checked_name, checked_door, checked_id, created


@dataclass(frozen=True, slots=True)
class Account:
    """Person, folded door, credential id, and the caller epoch. No key bytes."""

    name: str
    door: str
    credential_id: str
    created_epoch: int

    def __post_init__(self) -> None:
        name, door, credential_id, created = _fields(
            self.name,
            self.door,
            self.credential_id,
            self.created_epoch,
        )
        # check_door folds case. Store that id, not the caller's spelling.
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "door", door)
        object.__setattr__(self, "credential_id", credential_id)
        object.__setattr__(self, "created_epoch", created)

    def __repr__(self) -> str:
        # A slot poke after a valid open must not grow a secret into a log.
        return (
            "Account("
            f"name={_show(self.name)}, door={_show(self.door)}, "
            f"credential_id={_show(self.credential_id)}, "
            f"created_epoch={_show(self.created_epoch)})"
        )


def open_account(name: str, door: str, credential_id: str, now: int) -> Account:
    """Open one peer account. Key bytes never enter this object."""
    checked_name, checked_door, checked_id, created = _fields(
        name,
        door,
        credential_id,
        now,
    )
    return Account(checked_name, checked_door, checked_id, created)


__all__ = ["SCHEMA", "Account", "open_account"]
