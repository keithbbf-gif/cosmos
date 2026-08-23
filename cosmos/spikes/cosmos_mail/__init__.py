"""SPIKE 3 — cosmos_mail: IPC at N>2.

Import is inert. A mailbox is opened only by explicit instantiation against a
sentinel-verified exchange root. Missing, empty, unreadable, and stale are four
distinct typed states; they are never collapsed.
"""

from __future__ import annotations

from cosmos.spikes.cosmos_mail.clock import Clock, FrozenClock, SystemClock
from cosmos.spikes.cosmos_mail.mail import (
    SENTINEL_BODY,
    SENTINEL_NAME,
    SPIKE_WORKER_ID,
    MailExchange,
    StalenessPolicy,
    prepare_surface,
)
from cosmos.spikes.cosmos_mail.platform import (
    PlatformAdapter,
    PosixPlatformAdapter,
    WindowsPlatformAdapter,
    detect_platform_adapter,
)
from cosmos.spikes.cosmos_mail.types import (
    AbsenceKind,
    InboxEntry,
    Message,
    Outcome,
    ProbeReport,
    Receipt,
    ReceiptKind,
    ReceiveReport,
    exit_code_for,
)

__all__ = [
    "SENTINEL_BODY",
    "SENTINEL_NAME",
    "SPIKE_WORKER_ID",
    "AbsenceKind",
    "Clock",
    "FrozenClock",
    "InboxEntry",
    "MailExchange",
    "Message",
    "Outcome",
    "PlatformAdapter",
    "PosixPlatformAdapter",
    "ProbeReport",
    "Receipt",
    "ReceiptKind",
    "ReceiveReport",
    "StalenessPolicy",
    "SystemClock",
    "WindowsPlatformAdapter",
    "detect_platform_adapter",
    "exit_code_for",
    "prepare_surface",
]
