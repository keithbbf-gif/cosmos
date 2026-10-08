"""Phone pull plan and snapshot mule.

The mule builds a snapshot body. It does not open a socket and it does
not touch audio hardware.
"""

from __future__ import annotations

import uuid

from cosmos_voice.errors import VoiceError
from cosmos_voice.types import KNOWN_KINDS, PCM_INLINE, PullPlan


def _text(value: object, default: str) -> str:
    """Return ``value`` when it is a string, otherwise ``default``."""
    if isinstance(value, str) and value:
        return value
    return default


def kind_status(
    name: str,
    *,
    granted: bool,
    collected: dict[str, object] | None,
) -> dict[str, object]:
    """Status object for one asked kind.

    ``name`` is the kind the ticket asked for. A missing grant is
    ``PERM_DENIED``. A grant with no collector is ``NO_COLLECTOR``.
    Neither refusal is an empty object. A collected object is copied,
    and ``status`` defaults to ``ok`` when the collector left it out.
    """
    if not granted:
        return {"status": "PERM_DENIED"}
    if collected is None:
        return {"status": "NO_COLLECTOR"}
    blob = dict(collected)
    blob.setdefault("status", "ok")
    return blob


def plan_pull(ticket: dict[str, object]) -> PullPlan:
    """Turn one pull ticket into what this handset may do.

    ``pull`` false, or ``core_kind`` ``UNREACHABLE``, means no capture and
    no TTS. Desktop ownership silences phone TTS. ``none`` or a missing
    owner is idle. ``fight_bluetooth`` is always false: the phone uses its
    own mic and does not force SCO, so a caller cannot win the headset by
    accident.
    """
    pull_on = ticket.get("pull") is True
    core_kind = _text(ticket.get("core_kind"), "")
    audio_owner = _text(ticket.get("audio_owner"), "none")
    play_tts = False
    capture = False
    if pull_on and core_kind != "UNREACHABLE":
        if audio_owner == "desktop":
            capture = True
        elif audio_owner == "phone":
            play_tts = True
            capture = True
    return PullPlan(
        play_tts=play_tts,
        capture=capture,
        fight_bluetooth=False,
        core_kind=core_kind,
        audio_owner=audio_owner,
    )


def _require_pcm_pointer(blob: dict[str, object]) -> None:
    """Refuse inline audio. ``pcm`` may name a sha256 and nothing inline."""
    if any(key in blob for key in PCM_INLINE):
        raise VoiceError("BAD_SNAPSHOT", "pcm must be a sha256 pointer, not inline bytes")
    digest = blob.get("sha256")
    if not isinstance(digest, str) or digest.strip() == "":
        raise VoiceError("BAD_SNAPSHOT", "pcm must include sha256")


class PhoneMule:
    """Builds ``POST /api/v1/cvm/snapshot`` bodies. It does not bind a port."""

    def __init__(self, client_id: str, tree_id: str) -> None:
        """Remember the handset id and the tree id Core expects."""
        self.client_id = client_id
        self.tree_id = tree_id

    def snapshot(self, kinds: dict[str, dict[str, object]]) -> dict[str, object]:
        """Copy known kinds into a snapshot body.

        Unknown kind names are dropped. That drop is not an error. A known
        kind must be a non-empty object. ``pcm`` must be a sha256 pointer:
        ``bytes``, ``pcm``, ``data``, and ``b64`` are refused.
        """
        kept: dict[str, dict[str, object]] = {}
        for name, blob in kinds.items():
            if name not in KNOWN_KINDS:
                continue
            if not isinstance(blob, dict) or len(blob) == 0:
                raise VoiceError("BAD_SNAPSHOT", f"{name} is empty")
            if name == "pcm":
                _require_pcm_pointer(blob)
            kept[name] = dict(blob)
        return {
            "client_id": self.client_id,
            "tree_id": self.tree_id,
            "request_id": uuid.uuid4().hex,
            "kinds": kept,
        }
