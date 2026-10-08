"""Speech rails.

``xai`` is the Grok-phone quality path: one bidirectional WebSocket,
server VAD, no Send button. ``cascade`` is STT then a text reply then TTS,
still with an open mic and barge-in. ``local`` keeps the loop alive when
the key or the credit is gone. It does not pretend to be neural speech.
"""

from cosmos_voice_duplex.rails.base import RailEvent
from cosmos_voice_duplex.rails.cascade import CascadeRail
from cosmos_voice_duplex.rails.local_mouth import LocalRail
from cosmos_voice_duplex.rails.xai_realtime import XaiRealtimeRail

__all__ = ["CascadeRail", "LocalRail", "RailEvent", "XaiRealtimeRail"]
