"""COSMOS Code plugin record for the voice client.

The four tools call the injected Core client. They do not read the environment
and they do not write the live tree. Anthropic stays off.
"""

from __future__ import annotations

from typing import Protocol, cast

from cosmos_voice.doors import CoreMouth
from cosmos_voice.session import VoiceSession
from cosmos_voice.transport import CoreClient


class _Pending(Protocol):
    """A road queue that can list rows it has not sent."""

    def list_pending(self) -> object:
        """Return the pending rows."""


def manifest() -> dict[str, object]:
    """Return the plugin record. ``writes_live_tree`` is false."""

    layers: dict[str, object] = {
        "l1_role": "file",
        "l2_model": "none",
        "l3_harness": "native",
        "l4_wrapper": "file",
        "l5_skills": "none",
        "l6_tools": "native",
        "l7_enviro": "file",
        "l8_mission": "file",
    }
    tools: list[object] = ["voice.say", "voice.status", "voice.kill", "voice.queue"]
    record: dict[str, object] = {
        "id": "cosmos-voice",
        "plugin_of": "cosmos-code",
        "writes_live_tree": False,
        "authority": "core-http-client",
        "anthropic": "off",
        "layers": layers,
        "tools": tools,
    }
    return record


def register(
    table: dict[str, object],
    *,
    client: CoreClient,
    session: VoiceSession,
    queue: object | None = None,
) -> dict[str, object]:
    """Add the four voice tools to ``table`` and return that same table."""

    mouth = CoreMouth(client)

    def voice_say(transcript: str) -> dict[str, object]:
        """Send one transcript through Core."""

        return mouth.speak_turn(transcript, session)

    def voice_status() -> dict[str, object]:
        """Return Core status."""

        return client.get_status()

    def voice_kill(client_id: str) -> dict[str, object]:
        """Ask Core to turn the mic off for this client."""

        return client.post_kill(client_id)

    def voice_queue() -> dict[str, object]:
        """List pending drops. No queue means nothing is waiting."""

        if queue is None:
            pending: object = []
        else:
            pending = cast(_Pending, queue).list_pending()
        body: dict[str, object] = {"pending": pending}
        return body

    table["voice.say"] = voice_say
    table["voice.status"] = voice_status
    table["voice.kill"] = voice_kill
    table["voice.queue"] = voice_queue
    return table
