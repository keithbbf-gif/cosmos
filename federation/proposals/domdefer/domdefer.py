"""Day-one door versus a later DOM session.

DOM is the preferred path once a person already has a vendor session.
A clean install has no such session. Capturing one would be collecting
a credential the installer does not own, so the two-minute chooser
never returns DOM and never opens a browser, a profile, or a login.
"""

from __future__ import annotations

from dataclasses import dataclass

from cosmos_federation import Refuse

SCHEMA = "cosmos-federation-domdefer/1"

__all__ = ["SCHEMA", "Choice", "choose", "later"]


@dataclass(frozen=True, slots=True)
class Choice:
    """How a later installer step may reach a model, and when."""

    via: str
    phase: str


def choose(has_key_id: bool, has_browser_profile: bool, ask_scrape: bool) -> Choice:
    """Pick the two-minute door. This function never returns ``via="dom"``.

    Scrape is refused first. A key id does not excuse it: capturing a
    vendor session would collect a credential the installer does not own.
    The profile flag cannot select DOM either. A clean install has no
    vendor session, and a profile that happens to exist is still not
    one this installer may read. Day one is an api key id, or a stop
    that says a key is still required. ``later`` is the only DOM door.
    """
    if ask_scrape:
        raise Refuse("SCRAPE", "installer does not collect a vendor session")
    if has_key_id:
        return Choice(via="api", phase="DAY_ONE")
    # Read and discard the profile flag. Presence does not change day one.
    if has_browser_profile:
        return Choice(via="none", phase="NEED_KEY")
    return Choice(via="none", phase="NEED_KEY")


def later(has_browser_profile: bool) -> Choice:
    """Name DOM only after day one, and only when a profile is asserted.

    The flag is the caller's claim. This function does not launch a
    browser, read a profile, or automate a login. No asserted profile
    means there is no session to defer to.
    """
    if not has_browser_profile:
        raise Refuse("NO_PROFILE", "no vendor session to defer to")
    return Choice(via="dom", phase="LATER")
