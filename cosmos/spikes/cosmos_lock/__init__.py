"""cosmos_lock spike: arbiter leases, fencing tokens, fenced commit.

Import has no filesystem side effect. Compose an Arbiter with
``Arbiter.instantiate`` against an explicit root.
"""

from cosmos.spikes.cosmos_lock.absence import AbsenceKind, Outcome, RefusalCode
from cosmos.spikes.cosmos_lock.arbiter import Arbiter, LeaseCapability
from cosmos.spikes.cosmos_lock.clock import ArbiterClock, FrozenClock
from cosmos.spikes.cosmos_lock.identity import Stamp, WorkerIdentity
from cosmos.spikes.cosmos_lock.platform import PlatformAdapter

__all__ = [
    "AbsenceKind",
    "Arbiter",
    "ArbiterClock",
    "FrozenClock",
    "LeaseCapability",
    "Outcome",
    "PlatformAdapter",
    "RefusalCode",
    "Stamp",
    "WorkerIdentity",
]
