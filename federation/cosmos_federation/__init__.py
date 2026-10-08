"""Shared law for the federation day-one installer proposals.

Proposal modules import this package and the standard library only.
They do not import the live COSMOS tree and they do not import each other.
"""

from __future__ import annotations

from cosmos_federation.bounds import bound_int, bound_text
from cosmos_federation.errors import Refuse
from cosmos_federation.jail import PathJail
from cosmos_federation.product import (
    DEFAULT_CAP_USD_MICROS,
    DEFAULT_HOST,
    DEFAULT_PORT,
    INSTALL_BUDGET_S,
    KEY_PASTE_BUDGET_S,
    MAX_CAP_USD_MICROS,
    NONCE_TTL_S,
    ROLES,
    ROUTE_CHAT,
    ROUTE_PAGE,
    ROUTE_SETUP,
    SCHEMA,
    SOFTWARE_BUDGET_S,
    check_cap,
    check_door,
    check_tree_id,
    repo_disposition,
)
from cosmos_federation.redact import const_eq, redact, secret_shape

__all__ = [
    "DEFAULT_CAP_USD_MICROS",
    "DEFAULT_HOST",
    "DEFAULT_PORT",
    "INSTALL_BUDGET_S",
    "KEY_PASTE_BUDGET_S",
    "MAX_CAP_USD_MICROS",
    "NONCE_TTL_S",
    "ROLES",
    "ROUTE_CHAT",
    "ROUTE_PAGE",
    "ROUTE_SETUP",
    "SCHEMA",
    "SOFTWARE_BUDGET_S",
    "PathJail",
    "Refuse",
    "bound_int",
    "bound_text",
    "check_cap",
    "check_door",
    "check_tree_id",
    "const_eq",
    "redact",
    "repo_disposition",
    "secret_shape",
]
