#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_pay_wizard — the BYOK wizard (CLI v1; cDeck panels are the GUI v1.1).

The rule: we never create subaccounts FOR users — the wizard guides them to
create their own key, test-calls it, saves it. Borrowed: Hermes `hermes model`
(the interactive provider picker), Gemini CLI's auth-type selection.

    py -3 cosmos_pay_wizard.py                # interactive
    py -3 cosmos_pay_wizard.py --provider openrouter --key sk-or-…
    py -3 cosmos_pay_wizard.py --provider google --key AIza…
    py -3 cosmos_pay_wizard.py --provider bedrock --key AKIA… --secret … --region us-east-1

Providers (v1):
    openrouter  — paste key (or the referral link to get one free) → test via /models
    google      — AI Studio auth key (guide opens aistudio.google.com/apikey) → test generateContent
    bedrock     — AWS keys + region → saved unverified (SigV4 test lands with the rail)
Each: test call → save to live/config + models.json BYOK entry → rail appears in the picker.
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.request
import webbrowser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import cosmos_pay_config as cfg

PASS = 0
FAIL = 0


def ok(name: str, cond: bool) -> None:
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  PASS {name}")
    else:
        FAIL += 1
        print(f"  FAIL {name}")


# ----------------------------------------------------------------- test calls
def test_openrouter(key: str) -> bool:
    req = urllib.request.Request("https://openrouter.ai/api/v1/models",
                                 headers={"Authorization": f"Bearer {key}"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status == 200
    except Exception:
        return False


def test_google(key: str) -> bool:
    body = json.dumps({"contents": [{"parts": [{"text": "PONG"}]}]}).encode("utf-8")
    req = urllib.request.Request(
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
        "?key=" + key, data=body, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status == 200
    except Exception:
        return False


def test_bedrock(key: str, secret: str, region: str) -> bool:
    """v1: format validation only — the SigV4 test call lands with the bedrock rail."""
    return bool(key.startswith("AKIA") and len(secret) >= 30 and region)


# ----------------------------------------------------------------- guides
GUIDES = {
    "openrouter": [
        "1. We'll open openrouter.ai/keys — sign in (Google/GitHub), create a key.",
        "   (Signing up through this link supports COSMOS — same price for you.)",
        "2. Copy the key (starts sk-or-).",
    ],
    "google": [
        "1. We'll open aistudio.google.com/apikey — sign in with your Google account.",
        "2. Create an API key (the new 'auth key' kind). Free tier: ~250 requests/day on Flash.",
        "3. Copy the key (starts AIza).",
    ],
    "bedrock": [
        "1. AWS Console → IAM → create a user with the Bedrock policy (the wizard prints the JSON).",
        "2. Create an access key pair (AKIA… / secret).",
        "3. Enable model access: Bedrock → Model access → request the models you want.",
    ],
}

URLS = {
    "openrouter": "https://openrouter.ai/keys",
    "google": "https://aistudio.google.com/apikey",
    "bedrock": "https://console.aws.amazon.com/iam/",
}

BEDROCK_POLICY = {
    "Version": "2012-10-17",
    "Statement": [{"Effect": "Allow", "Action": ["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream"],
                   "Resource": "*"}],
}


def run_wizard(provider: str, key: str = "", secret: str = "", region: str = "us-east-1",
               auto_open: bool = True) -> bool:
    print(f"-- {provider} wizard --")
    for line in GUIDES[provider]:
        print(f"  {line}")
    if provider == "bedrock":
        print("  IAM policy JSON (paste into the console):")
        print("  " + json.dumps(BEDROCK_POLICY))
    if not key:
        if auto_open and input(f"  Open {URLS[provider]} in your browser? [Y/n] ").strip().lower() != "n":
            webbrowser.open(URLS[provider])
        key = input("  Paste the key: ").strip()
        if provider == "bedrock":
            secret = input("  Paste the secret key: ").strip()

    print(f"  testing {provider}...")
    if provider == "openrouter":
        verified = test_openrouter(key)
    elif provider == "google":
        verified = test_google(key)
    else:
        verified = test_bedrock(key, secret, region)
    ok(f"{provider} key verified" if verified else f"{provider} key NOT verified (saved anyway -- rail marks it)",
       verified)

    # save: secrets file + models.json BYOK entry
    secrets = cfg.load_secrets(required=[]) if cfg.SECRETS_PATH.exists() else {}
    secrets[f"{provider}_api_key"] = key
    if provider == "bedrock":
        secrets["aws_secret_key"] = secret
        secrets["aws_region"] = region
    cfg.ensure_dirs()
    cfg.SECRETS_PATH.write_text(json.dumps(secrets, indent=2), encoding="utf-8")

    models = cfg.load_models()
    byok_id = f"{provider}-byok"
    models[byok_id] = {
        "rail": provider, "byok": True, "verified": verified,
        "price_rule": "passthrough+surcharge", "surcharge_pct": 5.0,
        "note": "user's own key -- Lane B toll applies to coordinated use; solo local is free",
    }
    cfg.save_models(models)
    print(f"  saved: {byok_id} -> models.json + secrets (never in git)")
    return verified


def main() -> None:
    ap = argparse.ArgumentParser(description="TokenCenter BYOK wizard")
    ap.add_argument("--provider", choices=["openrouter", "google", "bedrock"])
    ap.add_argument("--key", default="")
    ap.add_argument("--secret", default="")
    ap.add_argument("--region", default="us-east-1")
    ap.add_argument("--no-open", action="store_true")
    args = ap.parse_args()
    if args.provider:
        run_wizard(args.provider, args.key, args.secret, args.region, auto_open=not args.no_open)
    else:
        print("TokenCenter BYOK wizard — pick a provider:")
        for i, p in enumerate(["openrouter", "google", "bedrock"], 1):
            print(f"  {i}. {p}")
        choice = input("number: ").strip()
        providers = ["openrouter", "google", "bedrock"]
        if choice.isdigit() and 1 <= int(choice) <= len(providers):
            run_wizard(providers[int(choice) - 1])
        else:
            print("bye.")
    print(f"\n{PASS} pass, {FAIL} fail (test results only)")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
