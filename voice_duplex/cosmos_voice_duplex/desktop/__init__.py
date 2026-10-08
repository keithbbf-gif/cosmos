"""Desktop duplex loop. The sound-card callback only moves bytes."""

from cosmos_voice_duplex.desktop.loop import SoundDeviceLoop, mix_callback
from cosmos_voice_duplex.desktop.runner import ScriptedDevice, build_session, run_frames

__all__ = [
    "ScriptedDevice",
    "SoundDeviceLoop",
    "build_session",
    "mix_callback",
    "run_frames",
]
