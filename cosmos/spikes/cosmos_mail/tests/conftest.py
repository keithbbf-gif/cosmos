"""Selftest fixtures. Import of cosmos_mail must remain inert."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cosmos.spikes.cosmos_mail.clock import SystemClock
from cosmos.spikes.cosmos_mail.mail import (
    MailExchange,
    StalenessPolicy,
    prepare_surface,
)
from cosmos.spikes.cosmos_mail.platform import PosixPlatformAdapter


@pytest.fixture
def clock() -> SystemClock:
    return SystemClock()


@pytest.fixture
def adapter(clock: SystemClock) -> PosixPlatformAdapter:
    return PosixPlatformAdapter(clock=clock)


@pytest.fixture
def exchange(
    tmp_path: Path, adapter: PosixPlatformAdapter, clock: SystemClock
) -> MailExchange:
    prepared = prepare_surface(tmp_path, adapter=adapter, clock=clock)
    assert prepared.kind.value == "FOUND"
    return MailExchange(
        tmp_path,
        adapter=adapter,
        clock=clock,
        policy=StalenessPolicy(
            heartbeat_stale_after_s=86400.0, clock_skew_future_s=5.0
        ),
    )
