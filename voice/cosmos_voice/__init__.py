"""COSMOS voice module.

A client of Core and a COSMOS Code plugin. See ``docs/ARCHITECTURE.md``.
Importing this package does not open a socket and does not touch the live tree.
"""

from __future__ import annotations

from cosmos_voice.compat import probe
from cosmos_voice.confirm import ConfirmGate
from cosmos_voice.control import ControlView
from cosmos_voice.desktop import DesktopLoop, NullEngine, ScriptEngine
from cosmos_voice.doors import (
    ClaudeDoor,
    CoreMouth,
    GrokVoiceDoor,
    OpenAIRealtimeDoor,
    open_door,
)
from cosmos_voice.errors import VoiceError
from cosmos_voice.modes import ModeMachine
from cosmos_voice.owner import AudioOwner
from cosmos_voice.phone import PhoneMule, kind_status, plan_pull
from cosmos_voice.plugin import manifest, register
from cosmos_voice.road import RoadQueue
from cosmos_voice.session import VoiceSession, new_idempotency_key
from cosmos_voice.transport import CoreClient, MemoryTransport, UrllibTransport

__all__ = [
    "AudioOwner",
    "ClaudeDoor",
    "ConfirmGate",
    "ControlView",
    "CoreClient",
    "CoreMouth",
    "DesktopLoop",
    "GrokVoiceDoor",
    "MemoryTransport",
    "ModeMachine",
    "NullEngine",
    "OpenAIRealtimeDoor",
    "PhoneMule",
    "RoadQueue",
    "ScriptEngine",
    "UrllibTransport",
    "VoiceError",
    "VoiceSession",
    "kind_status",
    "manifest",
    "new_idempotency_key",
    "open_door",
    "plan_pull",
    "probe",
    "register",
]
