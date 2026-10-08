"""Full-duplex voice for COSMOS and a later COSMOS Code plugin.

The mic stays open for the whole session. Turns end when the listener decides
the user has finished, not when a Send control is pressed. Barge-in clears
local playback in the same audio quantum and tells the speech rail to cancel.

This package is staged at ``V:\\streams\\cosmos_code_voice``. It does not write
``V:\\A\\Ai\\COSMOS`` or ``V:\\streams\\cosmos_code``.
"""

from cosmos_voice_duplex.config import VoiceConfig
from cosmos_voice_duplex.session import DuplexSession

__all__ = ["DuplexSession", "VoiceConfig", "__version__"]
__version__ = "0.1.0"
