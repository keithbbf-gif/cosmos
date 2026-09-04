#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_critics - THE LIVE CRUCIBLE CRITIC SET (Keith 2026-09-04). Three families,
three vendors, composed from what is MEASURED present and refused otherwise.

cosmos_crucible has always taken injected dispatchers (name -> packet_text -> return
text) because a critic pool wired inside the crucible cannot be tested without
spending money. This module is the composition root for the real pool:

  grok-sgh  xai     grok CLI in headless mode (--single), with XAI_API_KEY WITHHELD
                    from the child environment. The CLI falls back to its cached
                    browser/device login, which is the SuperGrok Heavy weekly pool -
                    the subscription, not the prepaid API credit. Leaving the key set
                    would silently bill console.x.ai per token.
  gem-api   google  cosmos_vertex_rail: Vertex EXPRESS on Joanna.bbf@gmail.com,
                    project-5a33f910-1251-4d6a-bf9, do_not_activate=True, model
                    PINNED to gemini-2.5-flash until a live gate returns 3.8. Never
                    Keith GCloud billing, never Activate.
  oa-api    openai  the incumbent bts_oa_api at tier terra (gpt-5.6-terra). The API,
                    not Codex and not a ChatGPT plan.

FOUR RULES THIS MODULE ENFORCES STRUCTURALLY, NOT BY DISCIPLINE:

  1. VENDOR-PLURAL. One family per vendor. grok-sgh and sgh-api are BOTH xAI, so
     sgh-api exists only as the fallback for when the grok CLI is absent - never
     beside it. Two members of one vendor are one family wearing two badges, and
     their agreement proves nothing (README: "the value is that the members
     disagree").
  2. ANTHROPIC IS OFF THE ROUTE. ANTHROPIC_OFF stays on COSMOS dispatch: no
     claude-cli critic, no Claude-on-Bedrock, no Cowork lift. Asking for one is a
     typed OFF_ROUTE refusal, and compose() cannot yield one.
  3. LLAMA IS NOT A FOURTH FAMILY. Keith adds llama later, or taps it on Bedrock.
     The Bedrock account is opening and UNBOUND - no region, no keys - so there is
     nothing to bind and no Meta API is minted here. It is DEFERRED, which is a
     state, not an absence.
  4. A METERED RAIL WITHOUT A BREAKER IS NOT COMPOSED. OpenAI auto-reload does not
     self-limit: it tops the balance up and keeps going, so the ceiling has to be
     ours. gem-api additionally carries the credit's real EXPIRY, because an
     expired credit is not money (cosmos_spend's B7 finding).

ATTACHMENT HAPPENS IN EXACTLY ONE PLACE: cosmos.py serve(), after Kernel(). A bare
Kernel() + Service() composes NO critics, so POST /api/v1/crucible still answers
501 CRUCIBLE_NOT_RUNNABLE (tests/test_rest_surface.py) - a served endpoint is not a
running crucible, and the honest 501 is the whole point.
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import shutil
from typing import Callable

from cosmos_vertex_rail import (VERTEX_ACCOUNT, VERTEX_CREDIT_EXPIRES_ISO,
                                VERTEX_CREDIT_USD, VERTEX_PROJECT, VertexExpressRail,
                                VertexRailError)

# ---------------- the families ----------------
FAMILY_VENDOR = {
    "grok-sgh": "xai",       # preferred xAI member: the CLI on the weekly pool
    "sgh-api": "xai",        # fallback ONLY when the grok CLI is absent
    "gem-api": "google",
    "oa-api": "openai",
}

# ---------------- xai: the grok CLI on the SuperGrok Heavy weekly pool ----------------
SGH_BINARY = "grok"
# Withheld from the child environment. With XAI_API_KEY set, the CLI authenticates
# as an API client and bills console.x.ai prepaid credit; unset, it uses the cached
# subscription login - the weekly pool that is already paid for.
SGH_ENV_WITHHELD = ("XAI_API_KEY",)
# Headless flags: -p/--single takes the prompt. json output so the return is parsed
# rather than scraped; --no-auto-update because a scripted run must not mutate its
# own binary; deny Bash/Edit/Write because a CRITIC READS AND JUDGES - it does not
# get to touch the tree it is reviewing (P10); --max-turns as a runaway guard that
# still leaves room to answer after a denied tool call.
SGH_HEADLESS_FLAGS = ("--output-format", "json", "--no-auto-update",
                      "--max-turns", "4",
                      "--deny", "Bash", "--deny", "Edit", "--deny", "Write")
SGH_TIMEOUT_S = 900.0

# ---------------- xai fallback + openai: incumbent node clients ----------------
SGH_INCUMBENT = "bts_sgh"
SGH_API_EST_USD = 0.02
SGH_API_BUDGET_USD = 10.0

OA_INCUMBENT = "bts_oa_api"
OA_TIER = "terra"
OA_MODEL = "gpt-5.6-terra"
OA_EST_USD = 0.05
OA_BUDGET_USD = 5.0

GEM_EST_USD = 0.03

# ---------------- what may never be composed here ----------------
OFF_ROUTE = {
    "claude-cli": "anthropic - ANTHROPIC_OFF stays on COSMOS dispatch; this build "
                  "is not a lift of claude -p, Claude-on-Bedrock, or Cowork",
    "claude-api": "anthropic - same ruling; no Anthropic rail is composed by COSMOS",
    "claude-bedrock": "anthropic on Bedrock - the account is unbound AND Anthropic "
                      "is off the route; two independent reasons, either sufficient",
}
DEFERRED = {
    "llama": "NOT a fourth family this PR. Keith adds llama later, or taps it on "
             "Bedrock. The Bedrock account is opening and unbound - no region, no "
             "keys - so there is nothing to bind, and no Meta API is minted to fake "
             "one. DEFERRED is a state, not an absence",
    "bedrock": "the Bedrock account is opening/unbound: no region, no keys. A rail "
               "with no endpoint is not a rail",
}


class CriticError(RuntimeError):
    """kind in {OFF_ROUTE, DEFERRED_FAMILY, UNKNOWN_FAMILY, VENDOR_DOUBLE_COUNT,
    ENV_WITHHOLD_FAILED, CRITIC_FAILED, EMPTY_RETURN}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


CRITIC_BRIEF = """# CRUCIBLE CRITIC BRIEF
You are ONE independent critic ({family}, vendor {vendor}) in a vendor-plural
crucible. Other families are reviewing this same packet and you cannot see them.
Do not try to agree with anyone.

Return, in this order:

1. A fenced ```json array of findings. Each object:
   {{"id": "{family}-1", "topic": "<short-stable-slug>",
     "severity": "critical|major|minor",
     "why": "<what breaks, and how you know>",
     "fix": "<the smallest change that closes it>"}}
   The topic slug is how the merge groups your finding against the other families'
   findings - so name THE DEFECT, not your paragraph.

2. Prose after the block: what you could not assess from this packet, and what
   evidence would settle it.

Rules: judge only what the packet contains; a gap in the packet is a finding about
the packet. Do not edit files, run commands, or fetch anything. A stated absence is
worth more than a confident guess.

===== PACKET FOLLOWS =====
"""


def assert_routable(family: str) -> None:
    """The gate every candidate passes before it can join the pool. Off-route and
    deferred names are refused BY KIND here, so no code path anywhere can quietly
    compose one."""
    if family in OFF_ROUTE:
        raise CriticError("OFF_ROUTE", f"{family}: {OFF_ROUTE[family]}")
    if family in DEFERRED:
        raise CriticError("DEFERRED_FAMILY", f"{family}: {DEFERRED[family]}")
    if family not in FAMILY_VENDOR:
        raise CriticError("UNKNOWN_FAMILY",
                          f"{family!r} is not a declared critic family - critics are "
                          f"composed from measured rails, never invented")


def _credit_expiry_epoch(iso_day: str = VERTEX_CREDIT_EXPIRES_ISO) -> float:
    return _dt.datetime.fromisoformat(iso_day + "T00:00:00+00:00").timestamp()


# ---------------- critics ----------------
class Critic:
    """A critic is callable(packet_text) -> return_text, which is exactly what
    cosmos_crucible.run_round dispatches. Failure RAISES: the crucible records a
    dead critic as a FINDING (RETURN_<family>.FAILED.txt), and that is the July
    forge's lesson kept - never a silent absence, never an invented review."""
    family = "?"
    vendor = "?"
    metered_usd = 0.0

    def __init__(self, *, spend=None):
        self._spend = spend

    def describe(self) -> str:
        return f"{self.family} · {self.vendor}"

    def call(self, prompt: str) -> dict:                              # pragma: no cover
        raise NotImplementedError

    def _header(self, result: dict) -> str:
        usd = result.get("usd")
        return ("<!-- COSMOS CRUCIBLE RETURN · family=%s · vendor=%s · model=%s · "
                "spend=%s -->\n" % (self.family, self.vendor,
                                    result.get("model", "?"),
                                    "UNPRICED" if usd is None else f"${usd:.4f}"))

    def __call__(self, packet_text: str) -> str:
        prompt = CRITIC_BRIEF.format(family=self.family,
                                     vendor=self.vendor) + packet_text
        if self.metered_usd and self._spend is not None:
            # RESERVE -> DENY-or-CALL -> SETTLE. A denial raises SpendError out of
            # here, and the crucible records the denied critic as a finding.
            result = self._spend.guarded_call(self.family, self.metered_usd,
                                              lambda: self.call(prompt))
        else:
            result = self.call(prompt)
        if not result.get("ok"):
            raise CriticError(result.get("kind") or "CRITIC_FAILED",
                              f"{self.family}: {result.get('detail', 'no detail')}")
        text = result.get("text") or ""
        if not text.strip():
            raise CriticError("EMPTY_RETURN",
                              f"{self.family} returned no text - an empty review is "
                              f"a finding, not a review")
        return self._header(result) + text


class GrokSghCritic(Critic):
    """xAI on the SuperGrok Heavy weekly pool. The one thing this class must get
    right is the ENVIRONMENT: XAI_API_KEY withheld, verified by read-back before
    the process starts."""
    family = "grok-sgh"
    vendor = "xai"
    metered_usd = 0.0          # the weekly pool is already paid; no per-call money

    def __init__(self, *, binary: str = SGH_BINARY, env: dict | None = None,
                 runner: Callable[..., dict] | None = None,
                 flags: tuple = SGH_HEADLESS_FLAGS,
                 timeout_s: float = SGH_TIMEOUT_S, spend=None):
        super().__init__(spend=spend)
        self.binary = binary
        self.flags = tuple(flags)
        self.timeout_s = timeout_s
        self._base_env = dict(os.environ if env is None else env)
        if runner is None:
            # An agentic CLI can spawn descendants, so a timeout must kill the
            # TREE and say whether the kill finished (OA port hazard 7).
            from cosmos_platform import run_tree_killed
            runner = run_tree_killed
        self._runner = runner

    def describe(self) -> str:
        return (f"{self.family} · {self.vendor} · {self.binary} --single "
                f"(XAI_API_KEY withheld → SuperGrok Heavy weekly pool)")

    def _strip(self, base: dict) -> dict:
        return {k: v for k, v in base.items() if k not in SGH_ENV_WITHHELD}

    def child_env(self) -> dict:
        """The environment the CLI actually gets. Built by exclusion and then READ
        BACK - the scar is trusting a write you never re-read. (_strip is a seam so
        the read-back guard itself is provable: a test overrides it to leak.)"""
        env = self._strip(dict(self._base_env))
        still_there = [k for k in SGH_ENV_WITHHELD if k in env]
        if still_there:
            raise CriticError(
                "ENV_WITHHOLD_FAILED",
                f"{', '.join(still_there)} survived the strip - refusing to start "
                f"the CLI, because a leaked key here silently bills prepaid API "
                f"credit instead of the weekly pool")
        return env

    def argv(self, prompt: str) -> list[str]:
        return [self.binary, "--single", prompt, *self.flags]

    def call(self, prompt: str) -> dict:
        env = self.child_env()
        r = self._runner(self.argv(prompt), timeout_s=self.timeout_s, env=env)
        if r.get("timed_out"):
            return {"ok": False, "kind": "TIMEOUT", "model": self.binary,
                    "detail": f"{self.binary} --single exceeded "
                              f"{self.timeout_s:.0f}s; kill: {r.get('kill_result')}"}
        if r.get("rc") != 0:
            # exit 1 from the CLI is auth/network/runtime - all three are findings
            tail = (r.get("err") or r.get("out") or "").strip()[-600:]
            return {"ok": False, "kind": "CLI_FAILED", "model": self.binary,
                    "detail": f"rc={r.get('rc')}: {tail}"}
        out = (r.get("out") or "").strip()
        model = self.binary
        try:
            data = json.loads(out)
            text = data.get("text") or ""
            model = (data.get("modelUsage") and next(iter(data["modelUsage"]))) or model
            usd = data.get("total_cost_usd")
            parse = "json envelope"
        except ValueError:
            # A plain-text answer is still a review; discarding it would be the
            # louder failure. The parse state travels with the return.
            text, usd, parse = out, None, "RAW_STDOUT (json envelope absent)"
        return {"ok": bool(text.strip()), "kind": "CLI", "text": text,
                "model": model, "usd": usd, "parse": parse,
                "pool": "SuperGrok Heavy weekly (XAI_API_KEY withheld)",
                "detail": "" if text.strip() else
                          f"{self.binary} exited 0 with no text ({parse})"}


class RailCritic(Critic):
    """Any probe/dispatch rail as a critic: the incumbent node clients through
    cosmos_node_rails.NodeRail, and cosmos_vertex_rail for gem-api. THE RAIL IS
    INJECTABLE, which is how gem-api and oa-api are proven with no live vendor."""

    def __init__(self, family: str, vendor: str, rail, *, metered_usd: float,
                 kwargs: dict | None = None, spend=None, note: str = ""):
        super().__init__(spend=spend)
        self.family = family
        self.vendor = vendor
        self.rail = rail
        self.metered_usd = metered_usd
        self.kwargs = dict(kwargs or {})
        self.note = note

    def describe(self) -> str:
        base = f"{self.family} · {self.vendor} · {type(self.rail).__name__}"
        model = self.kwargs.get("model") or getattr(self.rail, "model", None)
        if model:
            base += f" · {model}"
        return base + (f" · {self.note}" if self.note else "")

    def call(self, prompt: str) -> dict:
        payload = {"prompt": prompt}
        if self.kwargs:
            payload["kwargs"] = dict(self.kwargs)
        r = self.rail.dispatch(payload)
        out = dict(r)
        out.setdefault("model", self.kwargs.get("model")
                       or getattr(self.rail, "model", self.family))
        return out


# ---------------- composition ----------------
def _metered(family: str, vendor: str, rail, est: float, budget: float,
             spend, absent: dict, *, kwargs: dict | None = None,
             note: str = "", expires_epoch: float | None = None):
    """A metered rail joins the pool only with a live probe AND a breaker. No
    breaker is a REFUSAL, not a warning: an unbudgeted metered rail has no ceiling
    at all, and OpenAI's auto-reload proves the vendor will not supply one."""
    assert_routable(family)
    if spend is None:
        absent[family] = ("no SpendGate composed - a metered rail without a breaker "
                          "has no ceiling (auto-reload tops the balance up and keeps "
                          "going), so it is refused rather than run")
        return None
    try:
        ok, detail = rail.probe()
    except Exception as e:                                            # noqa: BLE001
        ok, detail = False, f"probe raised {type(e).__name__}: {e}"
    if not ok:
        absent[family] = f"probe says not live: {detail}"
        return None
    spend.set_budget(family, budget, expires_epoch=expires_epoch)
    return RailCritic(family, vendor, rail, metered_usd=est, kwargs=kwargs,
                      spend=spend, note=note)


def compose_critics(*, env: dict | None = None,
                    which: Callable[[str], str | None] | None = None,
                    spend=None,
                    grok_runner: Callable[..., dict] | None = None,
                    sgh_rail=None, vertex_rail=None,
                    vertex_gate: Callable[[], str] | None = None,
                    vertex_transport: Callable[..., str] | None = None,
                    oa_rail=None) -> tuple[dict, dict]:
    """Build the pool from what is MEASURED present. Returns (critics, absent):
    critics is family -> callable(packet_text) -> return_text; absent is
    family -> the measured reason it is not there. An empty pool is a legitimate
    answer - the caller must then leave the crucible un-runnable (501) rather than
    invent a critic."""
    which = which or shutil.which
    critics: dict = {}
    absent: dict = {}

    # ---- xai: the CLI first; the API only in its absence (same vendor) ----
    grok_path = which(SGH_BINARY)
    if grok_path:
        assert_routable("grok-sgh")
        critics["grok-sgh"] = GrokSghCritic(binary=grok_path, env=env,
                                            runner=grok_runner)
        absent["sgh-api"] = (f"not composed BY RULE: the grok CLI is present "
                             f"({grok_path}) and sgh-api is the SAME VENDOR (xAI) - "
                             f"one family per vendor, and sgh-api would also spend "
                             f"prepaid credit the weekly pool already covers")
    else:
        absent["grok-sgh"] = (f"{SGH_BINARY} is not on PATH - falling back to the "
                              f"xAI API rail, which is what sgh-api is for")
        rail = sgh_rail if sgh_rail is not None else _node_rail(SGH_INCUMBENT,
                                                                SGH_API_EST_USD)
        c = _metered("sgh-api", "xai", rail, SGH_API_EST_USD, SGH_API_BUDGET_USD,
                     spend, absent,
                     note="fallback: grok CLI absent (prepaid API credit)")
        if c is not None:
            critics["sgh-api"] = c

    # ---- google: Vertex Express on the Joanna credit ----
    rail = vertex_rail
    if rail is None:
        try:
            rail = VertexExpressRail(env=env, model_gate=vertex_gate,
                                     transport=vertex_transport,
                                     metered_usd=GEM_EST_USD)
        except VertexRailError as e:
            absent["gem-api"] = str(e)
            rail = None
    if rail is not None:
        c = _metered("gem-api", "google", rail, GEM_EST_USD, VERTEX_CREDIT_USD,
                     spend, absent,
                     expires_epoch=_credit_expiry_epoch(),
                     note=(f"Vertex Express · {VERTEX_ACCOUNT} · {VERTEX_PROJECT} · "
                           f"do_not_activate=True · credit expires "
                           f"{VERTEX_CREDIT_EXPIRES_ISO}"))
        if c is not None:
            critics["gem-api"] = c

    # ---- openai: the incumbent API at tier terra ----
    rail = oa_rail if oa_rail is not None else _node_rail(OA_INCUMBENT, OA_EST_USD)
    c = _metered("oa-api", "openai", rail, OA_EST_USD, OA_BUDGET_USD, spend, absent,
                 kwargs={"model": OA_MODEL},
                 note=(f"tier {OA_TIER} ({OA_MODEL}) - the API, not Codex and not a "
                       f"ChatGPT plan; auto-reload does not self-limit, so this cap "
                       f"is the only ceiling"))
    if c is not None:
        critics["oa-api"] = c

    # ---- vendor-plural, checked structurally ----
    seen: dict = {}
    for family in critics:
        vendor = FAMILY_VENDOR[family]
        if vendor in seen:
            raise CriticError(
                "VENDOR_DOUBLE_COUNT",
                f"{family} and {seen[vendor]} are both {vendor} - two members of "
                f"one vendor are one family wearing two badges, and their agreement "
                f"proves nothing")
        seen[vendor] = family
    return critics, absent


def _node_rail(module_name: str, est: float):
    """Imported lazily: cosmos_node_rails puts the live BTS tree on sys.path at
    construction, and this module must stay importable on a machine that has no
    such tree (the tests, and this PR's CI)."""
    from cosmos_node_rails import NodeRail
    return NodeRail(module_name, metered_usd=est)


def attach_critics(kernel, **kw) -> dict:
    """THE ONE ATTACH POINT (called from cosmos.py serve(), after Kernel()).

    Sets kernel.crucible_critics ONLY when at least one family is live. An empty
    pool leaves the attribute untouched, so POST /api/v1/crucible keeps answering
    501 CRUCIBLE_NOT_RUNNABLE - the refusal a bare Kernel()+Service() already
    gives. Either way the outcome is ledgered with each family's measured reason,
    and NO KEY MATERIAL is in the payload."""
    kw.setdefault("spend", getattr(kernel, "spend", None))
    critics, absent = compose_critics(**kw)
    report = {
        "attached": {f: c.describe() for f, c in critics.items()},
        "vendors": sorted({FAMILY_VENDOR[f] for f in critics}),
        "absent": absent,
        "off_route": sorted(OFF_ROUTE),
        "deferred": sorted(DEFERRED),
    }
    ledger = getattr(kernel, "ledger", None)
    if critics:
        kernel.crucible_critics = critics
        if ledger is not None:
            ledger.append("CRUCIBLE_CRITICS_ATTACHED",
                          {"families": sorted(critics),
                           "vendors": report["vendors"],
                           "describe": report["attached"],
                           "absent": absent,
                           "single_family_warning": (
                               "a single-family round proves nothing"
                               if len(report["vendors"]) < 2 else None)})
    elif ledger is not None:
        ledger.append("CRUCIBLE_CRITICS_ABSENT",
                      {"absent": absent,
                       "effect": "POST /api/v1/crucible stays 501 "
                                 "CRUCIBLE_NOT_RUNNABLE - no critic is invented"})
    return report


def pool_summary(report: dict) -> str:
    """One line for the serve banner: what is live, and why anything missing is."""
    if report["attached"]:
        live = ", ".join(sorted(report["attached"]))
        vendors = "/".join(report["vendors"])
        note = ("" if len(report["vendors"]) > 1
                else " [SINGLE FAMILY - agreement proves nothing]")
        return f"crucible critics: {live} ({vendors}){note}"
    return ("crucible critics: NONE composed - /api/v1/crucible answers 501 "
            "CRUCIBLE_NOT_RUNNABLE (" +
            "; ".join(f"{k}: {v}" for k, v in sorted(report["absent"].items())) + ")")
