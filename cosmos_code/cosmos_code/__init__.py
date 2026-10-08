"""COSMOS CODE — propose-only coding worker rail under Core.

Default: WOMBAT (mode=propose, sandbox=workspace-write, approval=on-request,
delete_policy=archive_only). CCr alone publishes live. Never write live/.
The harness call is G47. This package verifies the proposal.
"""

from __future__ import annotations

import sys
from pathlib import Path

__version__ = "1.0.0"

_G47 = Path(__file__).resolve().parents[2] / "harness" / "G47"
if _G47.is_dir() and str(_G47) not in sys.path:
    sys.path.insert(0, str(_G47))

from cosmos_code.pack.context_pack import ContextPack, ContextPackError, map_hash
from cosmos_code.safety.archive import ArchiveStore, CrashClass
from cosmos_code.safety.enclosure import (
    EnclosureStatus,
    detect_enclosure,
    refuse_unsandboxed_retry,
)
from cosmos_code.safety.hooks import HookBus, HookDecision, install_defaults
from cosmos_code.safety.pathjail import PathJail, PathJailError
from cosmos_code.verify.oracle import OracleGate, OracleGateError, OracleSpec
from cosmos_code.verify.stop_gate import DoneBundle, StopGate, StopGateError

__all__ = [
    "__version__",
    "PathJail",
    "PathJailError",
    "ArchiveStore",
    "CrashClass",
    "HookBus",
    "HookDecision",
    "install_defaults",
    "EnclosureStatus",
    "detect_enclosure",
    "refuse_unsandboxed_retry",
    "OracleSpec",
    "OracleGate",
    "OracleGateError",
    "DoneBundle",
    "StopGate",
    "StopGateError",
    "ContextPack",
    "ContextPackError",
    "map_hash",
]
