"""Bind policy for the day-one peer installer.

Live ``cosmos.py serve`` selects ``127.0.0.1`` unless ``--remote``, which
selects ``0.0.0.0``. ``Service`` refuses open access on a non-loopback bind
(``REMOTE_OPEN_ACCESS``) and refuses a non-loopback bind that is not actually
HTTPS (``REMOTE_CLEARTEXT``), with one trial opt-out (``--insecure-http``).
Loopback open access still starts on the operator checkout. A peer installer
does not ship that trial.
"""

from __future__ import annotations

from dataclasses import dataclass

from cosmos_federation import DEFAULT_HOST, Refuse, bound_text

SCHEMA = "cosmos-federation-bindpol/1"

# The address ``cosmos.py`` uses when ``--remote`` is set. It is every
# interface, not a loopback alias.
_WILDCARD = "0.0.0.0"
_PORT_LO = 1
_PORT_HI = 65535
# Neither live bind address is longer than this. ``bound_text`` requires a cap.
_HOST_LIMIT = 15


def _flag(value: object, name: str) -> bool:
    # A bare int must not count as True. ``no_auth=1`` would otherwise open
    # the console the bool check exists to keep shut.
    if not isinstance(value, bool):
        raise Refuse("BOUND", name)
    return value


def _port(value: object) -> int:
    # Port 0 asks the kernel for an ephemeral port. The day-one window cannot
    # find that port. ``bound_int`` would report BOUND; the supervisor log
    # needs the PORT tag for this door.
    if isinstance(value, bool) or not isinstance(value, int):
        raise Refuse("PORT", "port must be 1..65535")
    if value < _PORT_LO or value > _PORT_HI:
        raise Refuse("PORT", "port must be 1..65535")
    return value


def _host(value: object) -> str:
    text = bound_text(value, limit=_HOST_LIMIT, name="host")
    # Live serve binds only these two addresses. A third string would be a
    # bind mode the installer does not ship, including ``localhost`` and ``::1``.
    if text != DEFAULT_HOST and text != _WILDCARD:
        raise Refuse("HOST", "host must be loopback or the remote wildcard")
    return text


@dataclass(frozen=True, slots=True)
class Bind:
    """A bind the installer is allowed to serve. Auth is bearer, never open."""

    host: str
    port: int
    scheme: str
    auth: str

    def __post_init__(self) -> None:
        # The record is the decision. Building one by hand must not smuggle
        # an open console or a cleartext listen on every interface.
        if self.auth != "bearer":
            raise Refuse("OPEN_AUTH", "day-one auth is bearer")
        if self.scheme not in {"http", "https"}:
            raise Refuse("SCHEME", "scheme is http or https")
        _port(self.port)
        host = _host(self.host)
        if host == _WILDCARD and self.scheme != "https":
            raise Refuse("REMOTE_PLAIN", "wildcard bind requires tls")


def decide(host: str, port: int, remote: bool, tls: bool, no_auth: bool) -> Bind:
    """Return the bind a day-one peer may serve.

    An unauthenticated Core on a LAN interface is a full operator console
    (ledger, jobs, and spend). That is why OPEN_AUTH exists. Live serve
    already refuses ``--no-auth`` with ``--remote``. This also refuses
    ``--no-auth`` on loopback so a stranger cannot ship an open console.
    """
    if _flag(no_auth, "no_auth"):
        raise Refuse("OPEN_AUTH", "unauthenticated console is refused on every interface")
    checked_remote = _flag(remote, "remote")
    checked_tls = _flag(tls, "tls")
    checked_port = _port(port)
    checked_host = _host(host)
    # Live names the cleartext remote door REMOTE_CLEARTEXT and still allows
    # ``--insecure-http``. Day-one has no such opt-out: a bearer on a LAN
    # interface is captured and replayed.
    if checked_remote and not checked_tls:
        raise Refuse("REMOTE_PLAIN", "remote bind requires tls")
    if checked_host == _WILDCARD and not checked_remote:
        raise Refuse("HOST", "wildcard bind requires remote")
    # ``--remote`` in cosmos.py is the wildcard, not a second name for loopback.
    # The flag and the address have to agree or the operator is looking at
    # a different interface than the one that was requested.
    if checked_remote and checked_host != _WILDCARD:
        raise Refuse("HOST", "remote binds the wildcard")
    scheme = "https" if checked_tls else "http"
    return Bind(host=checked_host, port=checked_port, scheme=scheme, auth="bearer")


__all__ = ["SCHEMA", "Bind", "decide"]
