#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_vertex_rail - THE GEM FAMILY RAIL (Keith 2026-09-04: the live Crucible
critic set). Vertex EXPRESS mode on the Joanna account's free credit, and nothing
else: no Activate, no Keith GCloud billing, no account collapse.

FOUR THINGS THIS MODULE EXISTS TO REFUSE (each one a ruling, not a preference):

  * ACTIVATE. The Activate button converts the Express trial and DESTROYS the
    remaining free credit. do_not_activate defaults True and constructing with
    False is a typed refusal - the rail has no code path that could activate, so
    the flag is a declaration the caller cannot walk back.
  * KEITH'S GCLOUD BILLING. Express mode authenticates with an express API key
    and bills the trial credit. Application Default Credentials, a billing
    project, or a quota-project header would put the call on keith.bbf's card -
    so ADC is never read and a billing_project argument is refused.
  * ACCOUNT COLLAPSE. `keith.bbf@gmail.com` is the paid GEM/Studio API + GDX;
    `Joanna.bbf@gmail.com` is Vertex read/use-only (ARCH_SPEC 2026-08-17: "Do not
    collapse accounts"). The key is read from VERTEX_EXPRESS_API_KEY ONLY -
    GOOGLE_API_KEY / GEMINI_API_KEY / GOOGLE_APPLICATION_CREDENTIALS are ignored
    on purpose and the probe says so out loud.
  * AN UNGATED MODEL BUMP. gemini-2.5-flash is PINNED. The pin lifts only when a
    LIVE gate - a callable that asks the vendor what it actually serves - returns
    a 3.8 id. A gate that returns anything else, raises, or does not exist leaves
    the pin in place and the reason is carried in model_provenance.

THE KEY IS NEVER PRINTED. Every detail string this module produces, including the
ones lifted out of a transport exception, goes through redact() first.

THE TRANSPORT IS INJECTED (url, body, headers) -> response text. The default is
the native https reader; the tests inject a fake, which is how the whole rail is
proven without spending a cent of the credit or holding a key.
"""
from __future__ import annotations

import json
import os
from typing import Callable

# ---- the account, the project, the credit (identity, not configuration) ----
VERTEX_ACCOUNT = "Joanna.bbf@gmail.com"
VERTEX_PROJECT = "project-5a33f910-1251-4d6a-bf9"
VERTEX_CREDIT_USD = 300.0
VERTEX_CREDIT_EXPIRES_ISO = "2026-10-13"          # docs/COSMOS_PIPELINE.md, measured

# ---- auth: one env var, and the ones deliberately NOT read ----
EXPRESS_KEY_ENV = "VERTEX_EXPRESS_API_KEY"
IGNORED_AUTH_ENV = (
    "GOOGLE_API_KEY",                  # keith.bbf paid Studio key - account collapse
    "GEMINI_API_KEY",                  # same
    "GOOGLE_APPLICATION_CREDENTIALS",  # ADC -> Keith GCloud billing
    "GOOGLE_CLOUD_QUOTA_PROJECT",      # quota project -> Keith GCloud billing
)

# ---- the model pin and the only thing that lifts it ----
MODEL_PIN = "gemini-2.5-flash"
UNPIN_PREFIX = "gemini-3.8"

EXPRESS_ENDPOINT = ("https://aiplatform.googleapis.com/v1/publishers/google/"
                    "models/{model}:generateContent")


class VertexRailError(RuntimeError):
    """kind in {ACTIVATE_REFUSED, BILLING_REFUSED, NO_EXPRESS_KEY, MODEL_NOT_GATED,
    IDENTITY_MISMATCH}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def resolve_model(model_gate: Callable[[], str] | None = None) -> tuple[str, str]:
    """The pin, and what it would take to lift it. Returns (model, provenance).

    A gate is a LIVE question to the vendor ("what do you serve?"). Only a 3.8
    answer unpins; a stale answer, a raise, or no gate at all keeps
    gemini-2.5-flash - because a model name in a config file is not a model that
    exists, and the July forge already paid for that difference once."""
    if model_gate is None:
        return MODEL_PIN, "PINNED (no live gate ran - a config string is not a model)"
    try:
        served = model_gate()
    except Exception as e:                                            # noqa: BLE001
        return MODEL_PIN, (f"PINNED (live gate raised {type(e).__name__} - a gate "
                           f"that fails is a finding, not a version bump)")
    if isinstance(served, str) and served.startswith(UNPIN_PREFIX):
        return served, f"UNPINNED by live gate: vendor serves {served}"
    return MODEL_PIN, (f"PINNED (live gate returned {served!r}, not "
                       f"{UNPIN_PREFIX}*)")


def _urllib_transport(url: str, body: bytes, headers: dict,
                      timeout_s: float) -> str:
    import urllib.request
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout_s) as r:        # noqa: S310
        return r.read().decode("utf-8", "replace")


class VertexExpressRail:
    """kind=API, the gem-api critic's engine. dispatch() never raises and never
    fabricates: a missing key, a dead endpoint, or an unparseable body all come
    back typed, with the key redacted out of the detail."""
    kind = "API"
    family = "gem-api"
    vendor = "google"

    def __init__(self, *, account: str = VERTEX_ACCOUNT,
                 project: str = VERTEX_PROJECT,
                 do_not_activate: bool = True,
                 model: str | None = None,
                 model_gate: Callable[[], str] | None = None,
                 transport: Callable[..., str] | None = None,
                 env: dict | None = None,
                 metered_usd: float = 0.03,
                 timeout_s: float = 180.0,
                 billing_project: str | None = None):
        if do_not_activate is not True:
            raise VertexRailError(
                "ACTIVATE_REFUSED",
                "do_not_activate=True is the ruling, not the default: Activate "
                "converts the Express trial and destroys the remaining free "
                f"credit (${VERTEX_CREDIT_USD:.0f}, expires "
                f"{VERTEX_CREDIT_EXPIRES_ISO}). This rail has no activate path")
        if billing_project:
            raise VertexRailError(
                "BILLING_REFUSED",
                f"billing_project={billing_project!r} would put this call on "
                f"Keith's GCloud billing - Express mode bills the trial credit "
                f"through the express key and nothing else")
        self.account = account
        self.project = project
        self.do_not_activate = True
        self.metered_usd = metered_usd
        self.timeout_s = timeout_s
        self.env = dict(os.environ if env is None else env)
        self._transport = transport or _urllib_transport
        if model is None:
            self.model, self.model_provenance = resolve_model(model_gate)
        elif model == MODEL_PIN:
            self.model, self.model_provenance = model, "PINNED (caller named the pin)"
        elif model.startswith(UNPIN_PREFIX):
            self.model, self.model_provenance = model, f"caller supplied {model} (3.8 family)"
        else:
            raise VertexRailError(
                "MODEL_NOT_GATED",
                f"{model!r} is neither the pin ({MODEL_PIN}) nor a "
                f"{UNPIN_PREFIX}* id - the pin lifts on a LIVE gate return, not "
                f"on an argument")

    # ---------------- secrets ----------------
    def _key(self) -> str:
        key = (self.env.get(EXPRESS_KEY_ENV) or "").strip()
        if not key:
            raise VertexRailError(
                "NO_EXPRESS_KEY",
                f"{EXPRESS_KEY_ENV} is unset or blank - refusing to fall back to "
                f"{', '.join(IGNORED_AUTH_ENV)} (that is keith.bbf's paid key or "
                f"ADC billing, and collapsing the accounts is the failure)")
        return key

    def redact(self, text: str) -> str:
        """Every outbound string passes through here. A vendor library that echoes
        the key into an exception message must not put it in a ledger or a
        RETURN_*.md file."""
        out = str(text)
        key = (self.env.get(EXPRESS_KEY_ENV) or "").strip()
        if key:
            out = out.replace(key, "[REDACTED]")
        return out

    # ---------------- probe ----------------
    def probe(self) -> tuple[bool, str]:
        try:
            self._key()
        except VertexRailError as e:
            return False, f"UNREACHABLE: {e.kind} ({EXPRESS_KEY_ENV} absent)"
        ignored = [v for v in IGNORED_AUTH_ENV if self.env.get(v)]
        note = (f"; IGNORED on purpose: {', '.join(ignored)}" if ignored else "")
        return True, (f"express key present for {self.account} on {self.project}, "
                      f"model {self.model} [{self.model_provenance}], "
                      f"do_not_activate=True (liveness is per-call){note}")

    # ---------------- dispatch ----------------
    def dispatch(self, payload: dict) -> dict:
        try:
            key = self._key()
        except VertexRailError as e:
            return {"ok": False, "kind": "UNREACHABLE", "detail": str(e),
                    "node": self.family}
        url = EXPRESS_ENDPOINT.format(model=self.model)
        body = json.dumps({
            "contents": [{"role": "user",
                          "parts": [{"text": payload["prompt"]}]}],
        }).encode("utf-8")
        # The key travels in a HEADER, never in the query string: a URL lands in
        # logs, proxies and crash reports, and a key in a log is a leaked key.
        headers = {"Content-Type": "application/json; charset=utf-8",
                   "x-goog-api-key": key}
        try:
            raw = self._transport(url, body, headers, self.timeout_s)
        except Exception as e:                                        # noqa: BLE001
            return {"ok": False, "kind": "BROKE", "node": self.family,
                    "detail": self.redact(f"{type(e).__name__}: {e}")[:600]}
        try:
            data = json.loads(raw)
        except ValueError as e:
            return {"ok": False, "kind": "UNPARSEABLE", "node": self.family,
                    "detail": self.redact(f"vertex body is not JSON: {e}")[:300]}
        if isinstance(data, dict) and data.get("error"):
            return {"ok": False, "kind": "BROKE", "node": self.family,
                    "detail": self.redact(json.dumps(data["error"]))[:600]}
        parts = []
        for cand in (data.get("candidates") or []):
            for part in ((cand.get("content") or {}).get("parts") or []):
                if isinstance(part.get("text"), str):
                    parts.append(part["text"])
        text = "".join(parts)
        if not text.strip():
            return {"ok": False, "kind": "EMPTY_RETURN", "node": self.family,
                    "detail": self.redact(
                        "vertex answered with no text - an empty return is a "
                        "finding, not a review")[:300]}
        usage = data.get("usageMetadata") or {}
        return {"ok": True, "kind": "API", "text": text, "node": self.family,
                "model": self.model, "model_provenance": self.model_provenance,
                "account": self.account, "project": self.project,
                # Express bills the trial credit, and the response carries no
                # price: UNPRICED is the honest value (cosmos_spend settles it
                # as UNPRICED rather than as zero).
                "usd": None,
                "tokens": usage.get("totalTokenCount")}
