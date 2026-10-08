"""Run each direct-run pay suite in a subprocess. Do not import those modules."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMP = Path(r"C:\Users\Papa\AppData\Local\Temp\c4-tokenctr")


def _run(script: str) -> None:
    TEMP.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["TEMP"] = str(TEMP)
    env["TMP"] = str(TEMP)
    proc = subprocess.run(
        [sys.executable, str(Path(__file__).resolve().parent / script)],
        cwd=str(ROOT),
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=180,
    )
    if proc.returncode != 0:
        tail = "\n".join((proc.stdout or "").splitlines()[-40:])
        raise AssertionError(f"{script} exited {proc.returncode}\n{tail}")


def test_pay_bulletproof() -> None:
    _run("test_pay_bulletproof.py")


def test_pay_cloudflare() -> None:
    _run("test_pay_cloudflare.py")


def test_pay_entitlement() -> None:
    _run("test_pay_entitlement.py")


def test_pay_founding() -> None:
    _run("test_pay_founding.py")


def test_pay_gateway_integration() -> None:
    _run("test_pay_gateway_integration.py")


def test_pay_meter() -> None:
    _run("test_pay_meter.py")


def test_pay_money_safety() -> None:
    _run("test_pay_money_safety.py")


def test_pay_pricing() -> None:
    _run("test_pay_pricing.py")


def test_pay_privacy() -> None:
    _run("test_pay_privacy.py")


def test_pay_toll() -> None:
    _run("test_pay_toll.py")


def test_pay_vertex_rail() -> None:
    _run("test_pay_vertex_rail.py")


def test_pay_webhooks() -> None:
    _run("test_pay_webhooks.py")
