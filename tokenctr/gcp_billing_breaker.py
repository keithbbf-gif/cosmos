#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gcp_billing_breaker — Cloud-side Spend Breaker for Google Cloud Vertex AI.

This module is the GCP cloud companion to COSMOS's local SpendGate (cosmos_spend.py).
It executes inside a serverless Google Cloud Function triggered by Cloud Billing
budget alerts over Google Cloud Pub/Sub.

Architecture:
    Google Cloud Billing Budget ($500 / monthly threshold)
        │
        │ Publishes Pub/Sub alert on 50%, 80%, 100% of budget
        ▼
    Pub/Sub Topic: projects/{project_id}/topics/cosmos-billing-breaker
        │
        ▼
    Cloud Function: halt_vertex_rail(event, context)
        │
        │ If costAmount >= budgetAmount:
        ▼
    CRM API / IAM: Revokes 'roles/aiplatform.user' from 'cosmos-vertex-rail'
        │
        ▼
    Vertex AI API calls immediately fail with 403 Forbidden.
    TokenCenter gateway catches 403 -> refunds reserves -> halts queues.
    Result: Programmatic hard cost ceiling enforced BEFORE overdraft occurs.

Stdlib only (base64, json, os, urllib.request).
"""
from __future__ import annotations

import base64
import json
import os
import urllib.error
import urllib.request
from typing import Any, Dict


def parse_pubsub_payload(event: Dict[str, Any]) -> Dict[str, Any]:
    """Extract and decode JSON payload from Cloud Billing Pub/Sub event."""
    data_b64 = event.get("data", "")
    if not data_b64:
        return {}
    decoded = base64.b64decode(data_b64).decode("utf-8")
    return json.loads(decoded)


def get_metadata_access_token() -> str:
    """Fetch ephemeral access token from Google Cloud Compute/Cloud Run metadata server."""
    url = "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token"
    req = urllib.request.Request(url, headers={"Metadata-Flavor": "Google"})
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("access_token", "")
    except Exception:
        return ""


def revoke_iam_role(project_id: str, sa_email: str, target_role: str = "roles/aiplatform.user") -> bool:
    """Revoke specific IAM role from the service account via Google Cloud Resource Manager API."""
    token = get_metadata_access_token()
    if not token:
        print("[ERROR] Could not fetch Google metadata access token")
        return False

    url = f"https://cloudresourcemanager.googleapis.com/v1/projects/{project_id}:getIamPolicy"
    req = urllib.request.Request(url, data=b"{}", headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            policy = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"[ERROR] Failed to get IAM policy: {e}")
        return False

    # Modify bindings
    target_member = f"serviceAccount:{sa_email}"
    modified = False
    new_bindings = []
    for binding in policy.get("bindings", []):
        if binding.get("role") == target_role:
            members = [m for m in binding.get("members", []) if m != target_member]
            if members != binding.get("members", []):
                modified = True
            if members:
                binding["members"] = members
                new_bindings.append(binding)
        else:
            new_bindings.append(binding)

    if not modified:
        print(f"[INFO] Member {target_member} not found under role {target_role}; no change needed.")
        return True

    policy["bindings"] = new_bindings

    # Set updated IAM policy
    set_url = f"https://cloudresourcemanager.googleapis.com/v1/projects/{project_id}:setIamPolicy"
    set_req = urllib.request.Request(set_url, data=json.dumps({"policy": policy}).encode("utf-8"), headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }, method="POST")

    try:
        with urllib.request.urlopen(set_req, timeout=10) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"[ERROR] Failed to set IAM policy: {e}")
        return False


def halt_vertex_rail(event: Dict[str, Any], context: Any = None) -> Dict[str, Any]:
    """Cloud Function entry point for Cloud Billing Pub/Sub topic."""
    billing_data = parse_pubsub_payload(event)
    cost = float(billing_data.get("costAmount") or 0.0)
    budget = float(billing_data.get("budgetAmount") or 0.0)
    project_id = os.environ.get("GCP_PROJECT_ID") or billing_data.get("budgetDisplayName", "")
    sa_email = os.environ.get("RESELLER_SA_EMAIL") or f"cosmos-vertex-rail@{project_id}.iam.gserviceaccount.com"

    print(f"[SPEND_BREAKER] Check: Spend=${cost:.2f} / Budget=${budget:.2f} (Project: {project_id})")

    if budget > 0 and cost >= budget:
        print(f"[SPEND_BREAKER] BUDGET BREACHED! Spend ${cost:.2f} >= Budget ${budget:.2f}. Executing IAM halt on {sa_email}...")
        ok = revoke_iam_role(project_id, sa_email, "roles/aiplatform.user")
        return {
            "status": "HALTED" if ok else "FAILED",
            "cost": cost,
            "budget": budget,
            "target": sa_email,
        }

    return {"status": "OK", "cost": cost, "budget": budget}
