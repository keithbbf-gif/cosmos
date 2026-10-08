#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_pay_cloudflare — tests for Cloudflare server-side processing."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import cosmos_pay_cloudflare as cf_mod

PASS = 0
FAIL = 0


def check(name: str, cond: bool) -> None:
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  PASS {name}")
    else:
        FAIL += 1
        print(f"  FAIL {name}")


if __name__ == "__main__":
    print("— test_pay_cloudflare —")

    # 1. Credentials discovery
    creds = cf_mod.discover_cloudflare_credentials()
    check("credentials discovery finds token", bool(creds.get("api_token")))
    check("credentials discovery has tokenctr zone_id", creds.get("zone_id") == cf_mod.TOKENCTR_ZONE_ID)
    check("credentials discovery has tokenctr account_id", creds.get("account_id") == cf_mod.TOKENCTR_ACCOUNT_ID)

    # 2. Client IP extraction
    headers_cf = {"CF-Connecting-IP": "198.51.100.42", "X-Forwarded-For": "10.0.0.1"}
    check("extract CF-Connecting-IP first", cf_mod.CloudflareClient.extract_client_ip(headers_cf) == "198.51.100.42")

    headers_true = {"True-Client-IP": "203.0.113.19"}
    check("extract True-Client-IP fallback", cf_mod.CloudflareClient.extract_client_ip(headers_true) == "203.0.113.19")

    headers_xff = {"X-Forwarded-For": "192.0.2.1, 10.0.0.2"}
    check("extract X-Forwarded-For first hop", cf_mod.CloudflareClient.extract_client_ip(headers_xff) == "192.0.2.1")

    headers_empty = {}
    check("extract default 127.0.0.1 on empty", cf_mod.CloudflareClient.extract_client_ip(headers_empty) == "127.0.0.1")

    # 3. Edge headers validation
    edge_meta = cf_mod.CloudflareClient.validate_edge_headers({
        "CF-Connecting-IP": "198.51.100.42",
        "CF-Ray": "8c1234567890abcd-DFW",
        "CF-IPCountry": "US",
    })
    check("edge headers detects cloudflare", edge_meta["is_cloudflare"] is True)
    check("edge headers extracts country", edge_meta["country"] == "US")
    check("edge headers extracts ray_id", edge_meta["ray_id"] == "8c1234567890abcd-DFW")

    # 4. Turnstile verification helper
    check("empty turnstile token returns False", cf_mod.CloudflareClient.verify_turnstile("") is False)
    check("unconfigured secret passes through safely in dev", cf_mod.CloudflareClient.verify_turnstile("dummy_token", secret_key="") is True)

    # 5. Live Cloudflare API verification (real token verification against Cloudflare API)
    client = cf_mod.CloudflareClient()
    token_status = client.verify_token()
    check("live API token verification succeeds", token_status.get("valid") is True)
    check("live API token status is active", token_status.get("status") == "active")

    zone_info = client.get_zone_info()
    check("live zone info name matches tokenctr.com", zone_info.get("name") == cf_mod.TOKENCTR_DOMAIN)
    check("live zone status is active", zone_info.get("status") == "active")

    print(f"\n{PASS} pass, {FAIL} fail")
    sys.exit(1 if FAIL else 0)
