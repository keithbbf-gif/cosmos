"""Phone gateway. The handset is a thin client. The PC holds the key."""

from cosmos_voice_duplex.phone.protocol import MESSAGE_TYPES, SERVER_TYPES
from cosmos_voice_duplex.phone.server import PhoneGateway
from cosmos_voice_duplex.phone.token_broker import EphemeralToken, parse_client_secret

__all__ = [
    "MESSAGE_TYPES",
    "SERVER_TYPES",
    "EphemeralToken",
    "PhoneGateway",
    "parse_client_secret",
]
