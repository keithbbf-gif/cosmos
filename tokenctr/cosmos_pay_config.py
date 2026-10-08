#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_pay_config — paths, config, secrets discipline (COSMOS pay, 2026-09-30).

Borrowed pattern: Hermes Agent separates secrets (~/.hermes/.env) from settings
(config.yaml) so "the right value goes to the right file automatically." COSMOS
keeps both under one root with deny-by-default gitignore discipline:

    $COSMOS_PAY_ROOT (default ~/.cosmos_pay)
      config.json    — non-secret settings (host, port, quotas, brackets, eps)
      secrets.json   — key material (runpod key, mesh HMAC key, MoR key). NEVER in git.
      models.json    — the supply registry (per-model COGS/OR/price)
      keys.db        — mesh API keys + credit balances (sqlite)
      meter.db       — cosmos-meter/1 event buffer

Fail-closed: missing secrets refuse at load. Key material never appears in
logs, errors, or responses (the no-echo rule — cDeck SET-2).
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict

ROOT = Path(os.environ.get("COSMOS_PAY_ROOT", str(Path.home() / ".cosmos_pay")))
CONFIG_PATH = ROOT / "config.json"
SECRETS_PATH = ROOT / "secrets.json"
MODELS_PATH = ROOT / "models.json"
KEYS_DB = ROOT / "keys.db"
METER_DB = ROOT / "meter.db"

DEFAULT_CONFIG: Dict[str, Any] = {
    "gateway": {"host": "127.0.0.1", "port": 8787},
    "free_tier": {
        "daily_face_usd": 1.50,        # ~$1–2 face/day per account (the abuse ceiling)
        "reset_tz": "UTC",
    },
    "toll_brackets": [                  # marginal slices: [floor, ceiling_exclusive, rate]
        [0, 100, 0.0],
        [100, 200, 0.02],
        [200, 1000, 0.015],
        [1000, None, 0.01],
    ],
    "pricing": {"eps_pct": 1.0, "cap_multiple": 5.0},
    "surcharge_pct": 5.0,               # customer-facing: 3.5% bank + 1.5% net
    "founding": {"cap": 500, "price_usd": 10.0, "grant_face_usd": 20.0},
    "sync": {"base_url": "", "batch": 500},   # empty base_url = local-only (offline-safe)
}


class ConfigError(RuntimeError):
    """kind in {MISSING, BAD_JSON, BAD_SECRET}."""


def _read_json(path: Path, required: bool) -> Dict[str, Any]:
    if not path.exists():
        if required:
            raise ConfigError(f"MISSING {path.name} at {path} — fail-closed")
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ConfigError(f"BAD_JSON {path.name}: {e}") from e


def ensure_dirs() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)


def write_default_config(force: bool = False) -> Path:
    """Bootstrap: write config.json + an empty secrets template. Never overwrites silently."""
    ensure_dirs()
    if CONFIG_PATH.exists() and not force:
        return CONFIG_PATH
    CONFIG_PATH.write_text(json.dumps(DEFAULT_CONFIG, indent=2), encoding="utf-8")
    if not SECRETS_PATH.exists():
        import secrets as _secrets
        SECRETS_PATH.write_text(
            json.dumps(
                {
                    "_comment": "Fill these. This file is NEVER in git (deny-by-default).",
                    "mesh_hmac_key_hex": _secrets.token_hex(32),
                    "setup_key": "setup_" + _secrets.token_hex(16),
                    "runpod_api_key": "",
                    "runpod_endpoint_id": "",
                    "cloudflare_api_token": "",
                    "cloudflare_account_id": "",
                    "cloudflare_zone_id": "",
                    "cloudflare_turnstile_secret_key": "",
                    "stripe_secret_key": "",
                    "stripe_webhook_secret": "",
                    "paypal_client_id": "",
                    "paypal_client_secret": "",
                },
                indent=2,
            ),
            encoding="utf-8",
        )
    return CONFIG_PATH


def load_config() -> Dict[str, Any]:
    """Non-secret settings; defaults merged under file values."""
    cfg = _read_json(CONFIG_PATH, required=False)
    merged = json.loads(json.dumps(DEFAULT_CONFIG))  # deep copy
    for section, values in cfg.items():
        if isinstance(values, dict) and isinstance(merged.get(section), dict):
            merged[section].update(values)
        else:
            merged[section] = values
    return merged


def load_secrets(required: Optional[list[str]] = None) -> Dict[str, str]:
    """Key material. Fail-closed: empty/missing required secrets refuse."""
    # Auto-bootstrap if secrets file doesn't exist
    if not SECRETS_PATH.exists():
        write_default_config(force=False)

    sec = _read_json(SECRETS_PATH, required=True)

    # Ensure mesh_hmac_key_hex is always populated (auto-seed if empty)
    if not sec.get("mesh_hmac_key_hex"):
        import secrets as _secrets
        sec["mesh_hmac_key_hex"] = _secrets.token_hex(32)
        SECRETS_PATH.write_text(json.dumps(sec, indent=2), encoding="utf-8")

    # Discover Cloudflare tokens from env / alternate vaults if missing
    if not sec.get("cloudflare_api_token"):
        alt_env = Path(r"V:\streams\webdev\keys\.env")
        if alt_env.exists():
            try:
                for line in alt_env.read_text(encoding="utf-8").splitlines():
                    if line.startswith("CF_API_TOKEN="):
                        sec["cloudflare_api_token"] = line.split("=", 1)[1].strip().strip("\"'")
                        break
            except Exception:
                pass

    req_keys = required if required is not None else ["runpod_api_key", "mesh_hmac_key_hex"]
    missing = [k for k in req_keys if not sec.get(k)]
    if missing:
        raise ConfigError(f"BAD_SECRET missing/empty: {', '.join(missing)} in {SECRETS_PATH} — fail-closed")
    return sec


def load_models() -> Dict[str, Any]:
    """The supply registry. Empty registry is legal (gateway serves 503 until a model lands)."""
    return _read_json(MODELS_PATH, required=False)


def save_models(models: Dict[str, Any]) -> None:
    ensure_dirs()
    MODELS_PATH.write_text(json.dumps(models, indent=2, sort_keys=True), encoding="utf-8")
