"""Day-one answers for one peer. No disk, no clock, no network.

Order is root, tree_id, name, door, accept_key, cap, bind.
Loopback bind enters confirm. Remote bind stops on tls until the
caller records yes, because a cleartext remote bind would carry
the bearer off the machine. The raw vendor key is an argument to
accept_key and is not a field: Wizard is repr'd, and a key in that
repr would leave the process.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from cosmos_federation import (
    DEFAULT_CAP_USD_MICROS,
    Refuse,
    bound_int,
    bound_text,
    check_cap,
    check_door,
    check_tree_id,
    const_eq,
    redact,
    secret_shape,
)

SCHEMA = "cosmos-federation-wizard/1"

# The UI shows this. begin does not copy it onto the wizard; the caller
# still submits the digit string, and check_cap still applies.
RECOMMENDED_CAP_USD_MICROS: int = DEFAULT_CAP_USD_MICROS

_EPOCH_HI = 9_999_999_999
_ROOT_LIMIT = 64
_NAME_LIMIT = 80
_ID_LIMIT = 80
_KEY_LIMIT = 512


@dataclass(frozen=True, slots=True)
class Wizard:
    """Collected answers. `step` is the next legal field, or confirm.

    `credential_id` names a key the peer already pasted. It is not the key.
    `tls` stays unset on loopback. Remote confirm requires tls yes.
    """

    step: str
    root: str | None
    tree_id: str | None
    name: str | None
    door: str | None
    credential_id: str | None
    cap_usd_micros: int | None
    bind: str | None
    tls: str | None
    started_epoch: int
    updated_epoch: int

    def __repr__(self) -> str:
        # Backstop for a public object. The key is not interpolated here.
        shown = (
            "Wizard("
            f"step={self.step!r}, root={self.root!r}, tree_id={self.tree_id!r}, "
            f"name={self.name!r}, door={self.door!r}, credential_id={self.credential_id!r}, "
            f"cap_usd_micros={self.cap_usd_micros!r}, bind={self.bind!r}, tls={self.tls!r}, "
            f"started_epoch={self.started_epoch!r}, updated_epoch={self.updated_epoch!r})"
        )
        return redact(shown)


def begin(now: int) -> Wizard:
    """Start at root. `now` is the caller epoch, stored and not read from a clock."""
    stamped = _epoch(now)
    return Wizard(
        step="root",
        root=None,
        tree_id=None,
        name=None,
        door=None,
        credential_id=None,
        cap_usd_micros=None,
        bind=None,
        tls=None,
        started_epoch=stamped,
        updated_epoch=stamped,
    )


def submit(wizard: Wizard, field: str, value: object, now: int) -> Wizard:
    """Record one field. A field that is not the current step raises STEP.

    `tls` is legal only after bind remote. The key step is not a submit;
    that call is accept_key, so a key never arrives as `value`.
    """
    stamped = _epoch(now)
    _need_wizard(wizard)
    if not isinstance(field, str) or field == "":
        raise Refuse("STEP", "field")
    _demand(wizard, field)
    if field == "root":
        return replace(wizard, updated_epoch=stamped, step="tree_id", root=_root_label(value))
    if field == "tree_id":
        return replace(wizard, updated_epoch=stamped, step="name", tree_id=_tree(value))
    if field == "name":
        return replace(wizard, updated_epoch=stamped, step="door", name=_person(value))
    if field == "door":
        return replace(wizard, updated_epoch=stamped, step="key", door=_door(value))
    if field == "cap":
        return replace(wizard, updated_epoch=stamped, step="bind", cap_usd_micros=_cap(value))
    if field == "bind":
        choice = _bind_choice(value)
        if choice == "loopback":
            # Loopback has no tls question. Confirm means ready.
            return replace(wizard, updated_epoch=stamped, step="confirm", bind="loopback")
        # Remote is recorded and is not ready. The next legal field is tls.
        return replace(wizard, updated_epoch=stamped, step="tls", bind="remote")
    if field == "tls":
        # Reaching this step means bind was remote. Anything but yes is cleartext.
        if wizard.bind != "remote":
            raise Refuse("STEP", "tls follows remote")
        if value != "yes":
            raise Refuse("REMOTE_PLAIN", "remote requires tls yes")
        return replace(wizard, updated_epoch=stamped, step="confirm", tls="yes")
    raise Refuse("STEP", "out of order")


def _refuse_anthropic_text(text: str) -> None:
    """`sk-ant-` is an Anthropic paste even when it is not the first bytes.

    A prefix test misses a leading space, a tab, or a Bearer wrapper. Those
    still match `secret_shape`, so the paste would be accepted as a normal key.
    """
    if "sk-ant-" in text.lower():
        check_door("anthropic")


def accept_key(wizard: Wizard, raw: str, credential_id: str, now: int) -> Wizard:
    """Check the pasted key and keep `credential_id` only.

    Called after door and before cap. The door is checked again so Anthropic
    still refuses here. `raw` must look like key material; an id that is itself
    key material is refused, because the id is what repr prints. `raw` is not
    written onto the returned wizard.
    """
    stamped = _epoch(now)
    _need_wizard(wizard)
    if wizard.step != "key":
        raise Refuse("STEP", "accept_key")
    if not isinstance(wizard.door, str):
        raise Refuse("STEP", "door")
    check_door(wizard.door)
    if not isinstance(raw, str) or raw == "":
        raise Refuse("KEY", "not secret shaped")
    # Before the length cap, so a long sk-ant- paste is ANTHROPIC_OFF, not KEY.
    _refuse_anthropic_text(raw)
    if len(raw) > _KEY_LIMIT or not secret_shape(raw):
        raise Refuse("KEY", "not secret shaped")
    if not isinstance(credential_id, str):
        raise Refuse("BOUND", "credential_id")
    # Before bound_text, so a long or short marker is not stored and then repr'd.
    _refuse_anthropic_text(credential_id)
    cid = bound_text(credential_id, limit=_ID_LIMIT, name="credential_id")
    if cid != cid.strip():
        raise Refuse("BOUND", "credential_id")
    if secret_shape(cid) or const_eq(cid, raw):
        raise Refuse("KEY", "credential id is not key material")
    return replace(wizard, updated_epoch=stamped, step="cap", credential_id=cid)


def ready(wizard: Wizard) -> bool:
    """True only on confirm, with every answer this bind requires.

    Loopback does not require tls. Remote requires the recorded word yes.
    """
    if not isinstance(wizard, Wizard) or wizard.step != "confirm":
        return False
    if wizard.root is None or wizard.tree_id is None or wizard.name is None:
        return False
    if wizard.door is None or wizard.credential_id is None or wizard.cap_usd_micros is None:
        return False
    if wizard.bind == "loopback":
        return True
    return wizard.bind == "remote" and wizard.tls == "yes"


def _epoch(now: int) -> int:
    return bound_int(now, lo=0, hi=_EPOCH_HI, name="now")


def _need_wizard(wizard: Wizard) -> None:
    if not isinstance(wizard, Wizard):
        raise Refuse("STEP", "wizard")


def _demand(wizard: Wizard, field: str) -> None:
    if wizard.step == "confirm":
        raise Refuse("STEP", "confirmed")
    if wizard.step == "key":
        raise Refuse("STEP", "accept_key")
    if field != wizard.step:
        raise Refuse("STEP", "out of order")


def _root_label(value: object) -> str:
    """A short label. Slashes and drive colons are paths, and this slot does not read a disk."""
    text = bound_text(value, limit=_ROOT_LIMIT, name="root")
    if text != text.strip():
        raise Refuse("BOUND", "root")
    if secret_shape(text):
        raise Refuse("SECRET", "root")
    if text in {".", ".."} or text.startswith(".") or any(mark in text for mark in ("/", "\\", ":")):
        raise Refuse("ROOT", "label is not a path")
    return text


def _tree(value: object) -> str:
    if not isinstance(value, str):
        raise Refuse("TREE_ID", "rejected")
    return check_tree_id(value)


def _person(value: object) -> str:
    text = bound_text(value, limit=_NAME_LIMIT, name="name")
    if text != text.strip():
        raise Refuse("BOUND", "name")
    if secret_shape(text):
        raise Refuse("SECRET", "name")
    return text


def _door(value: object) -> str:
    if not isinstance(value, str):
        raise Refuse("DOOR", "unknown door")
    return check_door(value)


def _cap(value: object) -> int:
    if (
        not isinstance(value, str)
        or value == ""
        or len(value) > 12
        or not value.isascii()
        or not value.isdigit()
    ):
        raise Refuse("CAP", "integer string")
    return check_cap(int(value))


def _bind_choice(value: object) -> str:
    if not isinstance(value, str) or value not in {"loopback", "remote"}:
        raise Refuse("BIND", "loopback or remote")
    return value


__all__ = [
    "RECOMMENDED_CAP_USD_MICROS",
    "SCHEMA",
    "Wizard",
    "accept_key",
    "begin",
    "ready",
    "submit",
]
