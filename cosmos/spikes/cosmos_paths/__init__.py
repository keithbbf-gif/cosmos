"""cosmos_paths spike.

Importing this package must not resolve a root, must not read a sentinel,
and must not create files. Call RootResolver.instantiate(record_path).
"""

from .absence import AbsenceKind, Absent, Found, TypedRefusal
from .platform import DriveSemantics, PlatformAdapter
from .plant import plant_installation
from .resolver import RootResolver
from .stamp import ArtifactStamp, now_stamp, worker_identity

__all__ = [
    "AbsenceKind",
    "Absent",
    "ArtifactStamp",
    "DriveSemantics",
    "Found",
    "PlatformAdapter",
    "RootResolver",
    "TypedRefusal",
    "now_stamp",
    "plant_installation",
    "worker_identity",
]
