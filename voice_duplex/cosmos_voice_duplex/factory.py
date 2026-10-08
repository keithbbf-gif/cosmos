"""Choose a rail. This module does not open a socket and does not print a key.

``auto`` stays on the local rail when the configured environment variable is
empty. An explicit ``xai`` or ``cascade`` rail is constructed without a
network transport; the caller attaches one.
"""

from __future__ import annotations

from cosmos_voice_duplex.config import VoiceConfig
from cosmos_voice_duplex.rails.base import Rail
from cosmos_voice_duplex.rails.cascade import CascadeRail
from cosmos_voice_duplex.rails.local_mouth import LocalRail
from cosmos_voice_duplex.rails.xai_realtime import XaiRealtimeRail, api_key_from_env


def select_rail(cfg: VoiceConfig) -> Rail:
    if cfg.rail == "local":
        return LocalRail()
    if cfg.rail == "cascade":
        return CascadeRail()
    if cfg.rail == "xai":
        return XaiRealtimeRail()
    if api_key_from_env(cfg):
        return XaiRealtimeRail()
    return LocalRail()
