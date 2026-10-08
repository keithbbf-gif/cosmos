"""Shared types for Hermes-shaped COSMOS proposals.

Feature packages import this package and nothing else from the proposal tree.
"""

from __future__ import annotations

from cosmos_hermes.bounds import bound_bytes, bound_int, bound_text
from cosmos_hermes.errors import Refuse
from cosmos_hermes.jail import PathJail
from cosmos_hermes.redact import const_eq, redact, secret_shape

__all__ = [
    "PathJail",
    "Refuse",
    "bound_bytes",
    "bound_int",
    "bound_text",
    "const_eq",
    "redact",
    "secret_shape",
]
