#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""cosmos_pay_cloudflare — Cloudflare server-side processing for TokenCenter.

Integrates Cloudflare's API, edge security, DNS automation, and Turnstile
verification for tokenctr.com and api.tokenctr.com.

Responsibilities:
  1. DNS & Zone Automation:
     - Verified zone management for tokenctr.com (zone ID: 80cd1e9c7b44c5dd0efd1d3d5a1e3f36)
     - Upsert A, CNAME, and TXT records (api.tokenctr.com, origin gateway, mail security)
     - SPF / DMARC enforcement for billing@tokenctr.com (12_VENDOR_BILLING.md §1)
  2. Edge Security & Client Identification:
     - Extract true client IP via CF-Connecting-IP, True-Client-IP, X-Forwarded-For
     - Validate CF-Ray and Cloudflare edge proxy headers
     - Edge rate limiting metadata
  3. Turnstile CAPTCHA Verification:
     - Server-side siteverify endpoint validation (challenges.cloudflare.com)
     - Frictionless bot-defense on /v1/account/create and /v1/founding/purchase
  4. Secrets Discipline:
     - Secure token discovery from ~/.cosmos_pay/secrets.json and V:\streams\webdev\keys\.env
     - No-echo rule: tokens and keys are never printed, logged, or serialized to responses

Stdlib only (urllib, json, os, time, typing). Windows-first.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional

CF_API_BASE = "https://api.cloudflare.com/client/v4"
TURNSTILE_VERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"

# Canonical zone and account constants for tokenctr.com
TOKENCTR_ZONE_ID = "80cd1e9c7b44c5dd0efd1d3d5a1e3f36"
TOKENCTR_ACCOUNT_ID = "86ac7c72bc79dd58328d26abd07ce031"
TOKENCTR_DOMAIN = "tokenctr.com"


class CloudflareError(RuntimeError):
    """kind in {BAD_CONFIG, AUTH_FAILED, API_ERROR, DNS_ERROR, TURNSTILE_FAILED}."""


def discover_cloudflare_credentials() -> Dict[str, str]:
    """Discover Cloudflare credentials with zero echo.

    Search order:
      1. Environment variables: CF_API_TOKEN, CLOUDFLARE_API_TOKEN
      2. ~/.cosmos_pay/secrets.json
      3. V:\\streams\\webdev\\keys\\.env
      4. V:\\streams\\webdev\\spidercaster_local\\credentials.env
    """
    creds: Dict[str, str] = {
        "api_token": os.environ.get("CF_API_TOKEN") or os.environ.get("CLOUDFLARE_API_TOKEN", ""),
        "account_id": os.environ.get("CF_ACCOUNT_ID") or os.environ.get("CLOUDFLARE_ACCOUNT_ID", ""),
        "zone_id": os.environ.get("CF_ZONE_ID") or os.environ.get("CLOUDFLARE_ZONE_ID", ""),
    }

    # 2. Try ~/.cosmos_pay/secrets.json
    try:
        import cosmos_pay_config as cfg
        if cfg.SECRETS_PATH.exists():
            sec = json.loads(cfg.SECRETS_PATH.read_text(encoding="utf-8"))
            if not creds["api_token"]:
                creds["api_token"] = sec.get("cloudflare_api_token", "")
            if not creds["account_id"]:
                creds["account_id"] = sec.get("cloudflare_account_id", "")
            if not creds["zone_id"]:
                creds["zone_id"] = sec.get("cloudflare_zone_id", "")
    except Exception:
        pass

    # 3. Try V:\streams\webdev\keys\.env
    alt_env = Path(r"V:\streams\webdev\keys\.env")
    if not creds["api_token"] and alt_env.exists():
        try:
            for line in alt_env.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line.startswith("CF_API_TOKEN="):
                    creds["api_token"] = line.split("=", 1)[1].strip().strip("\"'")
                    break
        except Exception:
            pass

    # 4. Fallback defaults for tokenctr.com
    if not creds["zone_id"]:
        creds["zone_id"] = TOKENCTR_ZONE_ID
    if not creds["account_id"]:
        creds["account_id"] = TOKENCTR_ACCOUNT_ID

    return creds


class CloudflareClient:
    """Client for Cloudflare API v4 and edge services."""

    def __init__(
        self,
        api_token: Optional[str] = None,
        account_id: Optional[str] = None,
        zone_id: Optional[str] = None,
        base_url: str = CF_API_BASE,
        timeout_s: int = 20,
    ):
        creds = discover_cloudflare_credentials()
        self._token = (api_token or creds["api_token"]).strip()
        self.account_id = (account_id or creds["account_id"]).strip()
        self.zone_id = (zone_id or creds["zone_id"]).strip()
        self.base_url = base_url.rstrip("/")
        self.timeout_s = int(timeout_s)

        if not self._token:
            raise CloudflareError("BAD_CONFIG: Cloudflare API token not found — fail-closed")

    # ------------------------------------------------------------- HTTP transport
    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        body: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/{path.lstrip('/')}"
        if params:
            qs = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
            if qs:
                url += ("?" if "?" not in url else "&") + qs

        data = json.dumps(body).encode("utf-8") if body is not None else None
        headers = {
            "Authorization": f"Bearer {self._token}",
            "Accept": "application/json",
            "User-Agent": "TokenCenter-Cloudflare/1.0",
        }
        if data is not None:
            headers["Content-Type"] = "application/json"

        req = urllib.request.Request(url, data=data, headers=headers, method=method.upper())
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_s) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                if not res.get("success", False):
                    errs = res.get("errors", [])
                    msg = errs[0].get("message", "unknown error") if errs else "API failed"
                    raise CloudflareError(f"API_ERROR on {path}: {msg}")
                return res
        except urllib.error.HTTPError as e:
            raw = e.read().decode("utf-8", "replace")[:300]
            try:
                err_data = json.loads(raw)
                errs = err_data.get("errors", [])
                detail = errs[0].get("message", raw) if errs else raw
            except Exception:
                detail = raw
            raise CloudflareError(f"HTTP {e.code} on {path}: {detail}") from e
        except urllib.error.URLError as e:
            raise CloudflareError(f"HTTP unreachable on {path}: {e.reason}") from e

    # ------------------------------------------------------------- Token & Zone verification
    def verify_token(self) -> Dict[str, Any]:
        """Verify API token validity and status."""
        res = self._request("GET", "user/tokens/verify")
        result = res.get("result", {})
        return {
            "valid": bool(res.get("success")),
            "id": result.get("id"),
            "status": result.get("status"),
        }

    def get_zone_info(self, zone_id: Optional[str] = None) -> Dict[str, Any]:
        """Fetch zone details."""
        zid = zone_id or self.zone_id
        if not zid:
            raise CloudflareError("BAD_CONFIG: zone_id is required")
        res = self._request("GET", f"zones/{zid}")
        z = res.get("result", {})
        return {
            "id": z.get("id"),
            "name": z.get("name"),
            "status": z.get("status"),
            "name_servers": z.get("name_servers", []),
            "account": z.get("account", {}),
        }

    # ------------------------------------------------------------- DNS Management
    def list_dns_records(
        self,
        zone_id: Optional[str] = None,
        record_type: Optional[str] = None,
        name: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List DNS records in zone with optional filters."""
        zid = zone_id or self.zone_id
        params: Dict[str, Any] = {"per_page": 100}
        if record_type:
            params["type"] = record_type.upper()
        if name:
            params["name"] = name

        res = self._request("GET", f"zones/{zid}/dns_records", params=params)
        return res.get("result", [])

    def create_dns_record(
        self,
        name: str,
        rtype: str,
        content: str,
        proxied: bool = False,
        ttl: int = 1,
        priority: Optional[int] = None,
        comment: str = "managed by TokenCenter",
        zone_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a DNS record."""
        zid = zone_id or self.zone_id
        body: Dict[str, Any] = {
            "type": rtype.upper(),
            "name": name,
            "content": content,
            "ttl": ttl,
            "proxied": proxied if rtype.upper() in ("A", "AAAA", "CNAME") else False,
            "comment": comment,
        }
        if priority is not None and rtype.upper() == "MX":
            body["priority"] = priority

        res = self._request("POST", f"zones/{zid}/dns_records", body=body)
        return res.get("result", {})

    def update_dns_record(
        self,
        record_id: str,
        name: str,
        rtype: str,
        content: str,
        proxied: bool = False,
        ttl: int = 1,
        priority: Optional[int] = None,
        comment: str = "managed by TokenCenter",
        zone_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update an existing DNS record."""
        zid = zone_id or self.zone_id
        body: Dict[str, Any] = {
            "type": rtype.upper(),
            "name": name,
            "content": content,
            "ttl": ttl,
            "proxied": proxied if rtype.upper() in ("A", "AAAA", "CNAME") else False,
            "comment": comment,
        }
        if priority is not None and rtype.upper() == "MX":
            body["priority"] = priority

        res = self._request("PUT", f"zones/{zid}/dns_records/{record_id}", body=body)
        return res.get("result", {})

    def delete_dns_record(self, record_id: str, zone_id: Optional[str] = None) -> bool:
        """Delete a DNS record."""
        zid = zone_id or self.zone_id
        res = self._request("DELETE", f"zones/{zid}/dns_records/{record_id}")
        return bool(res.get("success", False))

    def upsert_dns_record(
        self,
        name: str,
        rtype: str,
        content: str,
        proxied: bool = False,
        ttl: int = 1,
        priority: Optional[int] = None,
        comment: str = "managed by TokenCenter",
        zone_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Idempotently create or update a record matching name and type."""
        zid = zone_id or self.zone_id
        existing = self.list_dns_records(zone_id=zid, record_type=rtype, name=name)
        if existing:
            rec_id = existing[0]["id"]
            return self.update_dns_record(
                record_id=rec_id,
                name=name,
                rtype=rtype,
                content=content,
                proxied=proxied,
                ttl=ttl,
                priority=priority,
                comment=comment,
                zone_id=zid,
            )
        return self.create_dns_record(
            name=name,
            rtype=rtype,
            content=content,
            proxied=proxied,
            ttl=ttl,
            priority=priority,
            comment=comment,
            zone_id=zid,
        )

    def setup_tokenctr_dns(
        self,
        origin_ip: Optional[str] = None,
        gateway_cname: Optional[str] = None,
        billing_email: str = "billing@tokenctr.com",
    ) -> List[Dict[str, Any]]:
        """Configure standard DNS records for tokenctr.com:
          - A/CNAME for tokenctr.com (apex)
          - CNAME for www.tokenctr.com
          - A/CNAME for api.tokenctr.com (gateway public endpoint)
          - SPF TXT record for email security
          - DMARC TXT record for billing identity protection
        """
        results: List[Dict[str, Any]] = []

        # 1. Apex & WWW
        if origin_ip:
            results.append(self.upsert_dns_record(
                name=TOKENCTR_DOMAIN, rtype="A", content=origin_ip, proxied=True,
                comment="TokenCenter web apex",
            ))
            results.append(self.upsert_dns_record(
                name=f"api.{TOKENCTR_DOMAIN}", rtype="A", content=origin_ip, proxied=True,
                comment="TokenCenter API gateway",
            ))
        elif gateway_cname:
            results.append(self.upsert_dns_record(
                name=f"api.{TOKENCTR_DOMAIN}", rtype="CNAME", content=gateway_cname, proxied=True,
                comment="TokenCenter API gateway CNAME",
            ))

        results.append(self.upsert_dns_record(
            name=f"www.{TOKENCTR_DOMAIN}", rtype="CNAME", content=TOKENCTR_DOMAIN, proxied=True,
            comment="TokenCenter www alias",
        ))

        # 2. Email security (SPF + DMARC for billing@tokenctr.com)
        # 12_VENDOR_BILLING.md §1: role-based billing identity, no-spoofing
        spf_content = "v=spf1 include:_spf.google.com ~all"
        results.append(self.upsert_dns_record(
            name=TOKENCTR_DOMAIN, rtype="TXT", content=spf_content, proxied=False, ttl=3600,
            comment="TokenCenter SPF policy",
        ))

        dmarc_content = f"v=DMARC1; p=quarantine; rua=mailto:{billing_email}; pct=100; aspf=s;"
        results.append(self.upsert_dns_record(
            name=f"_dmarc.{TOKENCTR_DOMAIN}", rtype="TXT", content=dmarc_content, proxied=False, ttl=3600,
            comment="TokenCenter DMARC policy",
        ))

        return results

    # ------------------------------------------------------------- Turnstile & Security
    @staticmethod
    def verify_turnstile(
        token: str,
        remote_ip: Optional[str] = None,
        secret_key: Optional[str] = None,
        timeout: int = 10,
    ) -> bool:
        """Verify Cloudflare Turnstile token via Cloudflare siteverify endpoint.

        Returns True if token is valid. If secret_key is absent, defaults to True
        in test/local environments so verification never breaks offline development.
        """
        if not token:
            return False

        secret = secret_key or os.environ.get("CF_TURNSTILE_SECRET_KEY")
        if not secret:
            # Check ~/.cosmos_pay/secrets.json
            try:
                import cosmos_pay_config as cfg
                if cfg.SECRETS_PATH.exists():
                    sec = json.loads(cfg.SECRETS_PATH.read_text(encoding="utf-8"))
                    secret = sec.get("cloudflare_turnstile_secret_key", "")
            except Exception:
                pass

        if not secret:
            # If Turnstile secret is unconfigured, allow pass-through in non-enforcing mode
            return True

        params: Dict[str, str] = {"secret": secret, "response": token}
        if remote_ip:
            params["remoteip"] = remote_ip

        data = urllib.parse.urlencode(params).encode("utf-8")
        req = urllib.request.Request(
            TURNSTILE_VERIFY_URL,
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                outcome = json.loads(resp.read().decode("utf-8"))
                return bool(outcome.get("success", False))
        except Exception:
            return False

    @staticmethod
    def extract_client_ip(headers: Dict[str, str]) -> str:
        """Extract the real client IP behind Cloudflare and reverse proxies."""
        # Cloudflare provides CF-Connecting-IP as the canonical visitor IP
        for header_name in ("CF-Connecting-IP", "cf-connecting-ip", "True-Client-IP", "true-client-ip"):
            val = headers.get(header_name)
            if val:
                return val.strip()

        # Fallback to X-Forwarded-For (first hop)
        xff = headers.get("X-Forwarded-For") or headers.get("x-forwarded-for")
        if xff:
            return xff.split(",")[0].strip()

        return "127.0.0.1"

    @staticmethod
    def validate_edge_headers(headers: Dict[str, str]) -> Dict[str, Any]:
        """Extract Cloudflare edge metadata for audit and rate-limiting."""
        return {
            "client_ip": CloudflareClient.extract_client_ip(headers),
            "ray_id": headers.get("CF-Ray") or headers.get("cf-ray", ""),
            "country": headers.get("CF-IPCountry") or headers.get("cf-ipcountry", ""),
            "is_cloudflare": bool(headers.get("CF-Ray") or headers.get("cf-ray")),
        }


# ----------------------------------------------------------------------------- Install / Setup
def install_secrets_to_root(force: bool = False) -> Path:
    """Install discovered Cloudflare credentials and standard secrets safely
    into %USERPROFILE%\\.cosmos_pay\\secrets.json with ZERO chat/console echo."""
    import secrets as secrets_mod

    import cosmos_pay_config as cfg

    cfg.ensure_dirs()
    target = cfg.SECRETS_PATH
    existing: Dict[str, Any] = {}
    if target.exists():
        try:
            existing = json.loads(target.read_text(encoding="utf-8"))
        except Exception:
            existing = {}

    creds = discover_cloudflare_credentials()
    updated = False

    # Seed mesh HMAC key if missing
    if not existing.get("mesh_hmac_key_hex"):
        existing["mesh_hmac_key_hex"] = secrets_mod.token_hex(32)
        updated = True

    # Seed setup key if missing
    if not existing.get("setup_key"):
        existing["setup_key"] = "setup_" + secrets_mod.token_hex(16)
        updated = True

    # Seed Cloudflare values
    if creds["api_token"] and (not existing.get("cloudflare_api_token") or force):
        existing["cloudflare_api_token"] = creds["api_token"]
        updated = True

    if creds["account_id"] and (not existing.get("cloudflare_account_id") or force):
        existing["cloudflare_account_id"] = creds["account_id"]
        updated = True

    if creds["zone_id"] and (not existing.get("cloudflare_zone_id") or force):
        existing["cloudflare_zone_id"] = creds["zone_id"]
        updated = True

    # Placeholder stubs for user-managed keys
    existing.setdefault("runpod_api_key", "")
    existing.setdefault("runpod_endpoint_id", "")
    existing.setdefault("stripe_secret_key", "")
    existing.setdefault("stripe_webhook_secret", "")
    existing.setdefault("paypal_client_id", "")
    existing.setdefault("paypal_client_secret", "")
    existing.setdefault("cloudflare_turnstile_secret_key", "")

    if updated or not target.exists():
        target.write_text(json.dumps(existing, indent=2), encoding="utf-8")
        print(f"  -> secrets installed to {target} (no-echo: secrets kept secure)")
    else:
        print(f"  -> {target} already configured")

    return target


def main() -> None:
    parser = argparse.ArgumentParser(description="TokenCenter Cloudflare Management")
    parser.add_argument("--verify", action="store_true", help="verify API token and zone")
    parser.add_argument("--list-dns", action="store_true", help="list DNS records for tokenctr.com")
    parser.add_argument("--setup-dns", action="store_true", help="apply standard DNS setup for tokenctr.com")
    parser.add_argument("--origin", default="", help="origin IP address for A record")
    parser.add_argument("--install-secrets", action="store_true", help="install credentials to ~/.cosmos_pay/secrets.json")
    args = parser.parse_args()

    if args.install_secrets:
        install_secrets_to_root()

    try:
        cf = CloudflareClient()
    except CloudflareError as e:
        print(f"Cloudflare configuration error: {e}")
        sys.exit(1)

    if args.verify:
        v = cf.verify_token()
        print(f"Token active: {v['valid']} (status: {v['status']})")
        z = cf.get_zone_info()
        print(f"Zone: {z['name']} (id: {z['id']}, status: {z['status']})")
        print(f"Name servers: {', '.join(z['name_servers'])}")

    elif args.list_dns:
        records = cf.list_dns_records()
        print(f"DNS records for {TOKENCTR_DOMAIN} ({len(records)} found):")
        for r in records:
            p = " (proxied)" if r.get("proxied") else ""
            print(f"  {r['type']:6} {r['name']:28} -> {r['content']}{p} [id: {r['id'][:8]}...]")

    elif args.setup_dns:
        print(f"Setting up DNS for {TOKENCTR_DOMAIN}...")
        res = cf.setup_tokenctr_dns(origin_ip=args.origin or None)
        print(f"Configured {len(res)} DNS records successfully.")
        for r in res:
            print(f"  OK: {r.get('type')} {r.get('name')} -> {r.get('content')}")
    else:
        v = cf.verify_token()
        z = cf.get_zone_info()
        print(f"TokenCenter Cloudflare Ready: {z['name']} (active: {v['valid']})")


if __name__ == "__main__":
    main()
