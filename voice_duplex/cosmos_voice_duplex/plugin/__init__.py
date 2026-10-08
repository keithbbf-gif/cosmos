"""COSMOS Code voice plugin. It does not import the product package."""

from cosmos_voice_duplex.plugin.host import CodeHost
from cosmos_voice_duplex.plugin.voice_plugin import VoicePlugin

__all__ = ["CodeHost", "VoicePlugin"]
