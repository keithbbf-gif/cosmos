"""SPIKE cosmos_sched — concurrency, priority, interrupts.

Import has no filesystem side effect. Instantiate Scheduler explicitly.
"""

from cosmos.spikes.cosmos_sched.absence import Absence, TypedResult
from cosmos.spikes.cosmos_sched.stamp import ArtifactStamp, WorkerIdentity, now_stamp

__all__ = [
    "Absence",
    "ArtifactStamp",
    "TypedResult",
    "WorkerIdentity",
    "now_stamp",
]
