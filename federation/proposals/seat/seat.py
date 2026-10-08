"""Day-one chat seat. A door, a named pin, and the JSON a later sender would POST.

Does not call a model and does not read a key. The POST object matches
OpenRouterRail._dispatch_body in cosmos/cosmos_openrouter_rail.py. That
function puts the bearer in OpenRouterRail._headers, not in the JSON.
"""

from __future__ import annotations

from dataclasses import dataclass

from cosmos_federation import Refuse, bound_text, check_cap, check_door, secret_shape

SCHEMA = "cosmos-federation-seat/1"

# Single default in cosmos_openrouter_rail.py (DEFAULT_MODEL). The module
# prices this pin at $0, so it is also the cheapest documented chat model.
_OPENROUTER_PIN = "google/gemma-4-26b-a4b-it:free"
# No cosmos_*xai*rail.py. cosmos_cursor_rail.py CURSOR_GROK / CURSOR_MODEL
# is the single Grok default (pin_cursor_model). GroqCloud is a different door.
_XAI_PIN = "grok-4.6"
_TEXT_LIMIT = 4000
_PIN_LIMIT = 160
_CREDENTIAL_LIMIT = 128
# cosmos_openrouter_rail.DEFAULT_MAX_TOKENS. Not a larger budget.
_MAX_TOKENS = 1024


def _pin(pin: object) -> str:
    """A named model id. Claude pins are off even when the door is allowed."""
    if not isinstance(pin, str):
        raise Refuse("BOUND", "pin")
    named = bound_text(pin.strip(), limit=_PIN_LIMIT, name="pin")
    low = named.lower()
    if "anthropic/" in low or "claude" in low:
        raise Refuse("ANTHROPIC_OFF", "anthropic is off the route")
    if secret_shape(named):
        raise Refuse("SECRET", "pin")
    return named


def _credential(credential_id: object) -> str:
    """An id only. Raw key text would land in Seat's repr."""
    if not isinstance(credential_id, str):
        raise Refuse("BOUND", "credential_id")
    cred = bound_text(credential_id.strip(), limit=_CREDENTIAL_LIMIT, name="credential_id")
    if secret_shape(cred):
        raise Refuse("SECRET", "credential id")
    return cred


def _user_text(text: object) -> str:
    if not isinstance(text, str):
        raise Refuse("BOUND", "text")
    cleaned = bound_text(text, limit=_TEXT_LIMIT, name="text")
    if secret_shape(cleaned):
        raise Refuse("SECRET", "user text")
    return cleaned


def _reply_text(reply_text: object) -> str:
    # The live rail keeps dispatch text at 4000. Longer input is refused, not sliced.
    if not isinstance(reply_text, str):
        raise Refuse("BOUND", "reply")
    cleaned = bound_text(reply_text, limit=_TEXT_LIMIT, name="reply")
    if secret_shape(cleaned):
        raise Refuse("SECRET", "reply text")
    return cleaned


def _usd(usd_micros: object) -> int:
    """A measured reply may be $0. The policy floor applies to the seat cap, not here."""
    if isinstance(usd_micros, bool) or not isinstance(usd_micros, int) or usd_micros < 0:
        raise Refuse("BOUND", "usd_micros")
    return usd_micros


def _canonical_door(door: str) -> None:
    folded = check_door(door)
    if door != folded:
        raise Refuse("DOOR", "unknown door")


@dataclass(frozen=True, slots=True)
class Seat:
    """One bound day-one door. Holds a credential id, never key bytes."""

    door: str
    credential_id: str
    pin: str
    cap_usd_micros: int

    def __post_init__(self) -> None:
        _canonical_door(self.door)
        _credential(self.credential_id)
        _pin(self.pin)
        check_cap(self.cap_usd_micros)


@dataclass(frozen=True, slots=True)
class Turn:
    """One user message plus the cap the reply has to stay under."""

    door: str
    pin: str
    text: str
    cap_usd_micros: int

    def __post_init__(self) -> None:
        _canonical_door(self.door)
        _pin(self.pin)
        _user_text(self.text)
        check_cap(self.cap_usd_micros)


@dataclass(frozen=True, slots=True)
class Reply:
    """Test double of a model reply. Cost was already checked against the seat."""

    pin: str
    text: str
    usd_micros: int

    def __post_init__(self) -> None:
        _pin(self.pin)
        _reply_text(self.text)
        _usd(self.usd_micros)


def suggested_pin(door: str) -> str:
    """The concrete default pin from the live rail for this door."""
    folded = check_door(door)
    if folded == "openrouter":
        return _OPENROUTER_PIN
    return _XAI_PIN


def bind(door: str, credential_id: str, pin: str, cap_usd_micros: int) -> Seat:
    """Bind a door. Empty pin, an Anthropic pin, a key-shaped id, and a bad cap refuse."""
    folded = check_door(door)
    cred = _credential(credential_id)
    named = _pin(pin)
    cap = check_cap(cap_usd_micros)
    return Seat(door=folded, credential_id=cred, pin=named, cap_usd_micros=cap)


def user_turn(seat: Seat, text: str) -> Turn:
    """Copy the seat's pin and cap. Text longer than 4000 characters refuses."""
    if not isinstance(seat, Seat):
        raise Refuse("SEAT", "not a seat")
    cleaned = _user_text(text)
    return Turn(door=seat.door, pin=seat.pin, text=cleaned, cap_usd_micros=seat.cap_usd_micros)


def request_body(turn: Turn) -> dict[str, object]:
    """JSON a later sender would POST. Pin and user text only; no header and no key.

    Field names match cosmos/cosmos_openrouter_rail.py OpenRouterRail._dispatch_body.
    That function always sends model, messages, max_tokens, stream, and
    provider.allow_fallbacks. allow_fallbacks stays false so the named pin
    cannot be swapped. tag_preload does not rewrite a user-only message, so
    the user turn stays role plus content. The bearer stays in _headers.
    """
    if not isinstance(turn, Turn):
        raise Refuse("TURN", "not a turn")
    messages: list[dict[str, str]] = [{"role": "user", "content": turn.text}]
    body: dict[str, object] = {
        "model": turn.pin,
        "messages": messages,
        "max_tokens": _MAX_TOKENS,
        "stream": False,
        "provider": {"allow_fallbacks": False},
    }
    return body


def fake_reply(turn: Turn, reply_text: str, usd_micros: int) -> Reply:
    """Accept a priced reply at or under the seat cap. Above the cap is OVER_CAP."""
    if not isinstance(turn, Turn):
        raise Refuse("TURN", "not a turn")
    cleaned = _reply_text(reply_text)
    cost = _usd(usd_micros)
    if cost > turn.cap_usd_micros:
        raise Refuse("OVER_CAP", "above seat cap")
    return Reply(pin=turn.pin, text=cleaned, usd_micros=cost)


__all__ = [
    "SCHEMA",
    "Reply",
    "Seat",
    "Turn",
    "bind",
    "fake_reply",
    "request_body",
    "suggested_pin",
    "user_turn",
]
