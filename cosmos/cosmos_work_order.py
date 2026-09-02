#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_work_order - typed work-order drop + Google-family rail routing.

MEASURED FAIL (wo-20260901T205646-a7b9c233): Agent `Google | Flash | gemini-2.5-flash`
ran `gemini.cmd` without COSMOS keys and died rc=41 Vertex env missing. No Output file.
FAILED-with-missing-file is indistinguishable from a job that never started.

THE FIX (stated so nobody relaxes it):
  * Family=Google search/prove NEVER invoke gemini.cmd / the Gemini CLI. That binary
    does not load the COSMOS Vertex key; bts_gem.ask does.
  * Web SEARCH prefers DOM (playwright-dom guest: gemini.google.com + Google/Bing).
    API is not a silent substitute for a search.
  * Typed PING / PROVE uses gem-api / bts_gem.ask (the rail that already loads the
    Vertex key). API is the fallback for a typed ping, not the default for search.
  * The runner ALWAYS writes Output JSON, including on rail failure (typed kind).
    A missing Output file is itself a defect.

tree_id of the live install is KMesh-COSMOS-live. This module QUOTES that identity;
it never restamps a sentinel (cosmos_kernel.install refuses a restamp).
Anthropic is off: no Claude family routes are invented here.
"""
from __future__ import annotations

import json
import time
import uuid
from pathlib import Path

from cosmos_identity import LIVE_TREE_ID
from cosmos_platform import makedirs


class WorkOrderError(RuntimeError):
    """kind in {BAD_FAMILY, BAD_TASK, BAD_AGENT, BAD_ORDER, REFUSED, NO_RAIL}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


FAMILIES = {"Google"}
TASKS = {"search", "prove", "ping"}
# ping is a typed prove; both ride gem-api.
API_TASKS = {"prove", "ping"}
SEARCH_TASKS = {"search"}

GOOGLE_AGENTS = {
    "Flash": "gemini-2.5-flash",
    "flash": "gemini-2.5-flash",
    "gemini-2.5-flash": "gemini-2.5-flash",
    "Google | Flash | gemini-2.5-flash": "gemini-2.5-flash",
}

# The scar: these names are how the measured fail launched Vertex-less.
FORBIDDEN_CLI = {"gemini.cmd", "gemini.exe", "gemini"}

INVOKED_API = "gem-api/bts_gem.ask"
INVOKED_DOM = "dom/playwright-dom"
INVOKED_REFUSED_CLI = "REFUSED/gemini.cmd"

# Preferred DOM guest surfaces for a Google-family web search. Guest chat first
# (reasoning is free over the DOM); public search engines next.
DOM_SEARCH_URLS = (
    "https://gemini.google.com",
    "https://www.google.com/search",
    "https://www.bing.com/search",
)

OUTPUT_NAME = "Output.json"
ORDER_NAME = "order.json"


def _wo_id(clock=time.time) -> str:
    ts = time.strftime("%Y%m%dT%H%M%S", time.gmtime(clock()))
    return "wo-%s-%s" % (ts, uuid.uuid4().hex[:8])


def resolve_google_model(agent: str) -> str:
    """Map a Google-family agent label to a model id. Unknown is BAD_AGENT."""
    if agent in GOOGLE_AGENTS:
        return GOOGLE_AGENTS[agent]
    raise WorkOrderError(
        "BAD_AGENT",
        f"{agent!r} is not a known Google-family agent - known: "
        f"{sorted(set(GOOGLE_AGENTS.values()))}. Refusing to guess "
        f"(a guess is how gemini.cmd got selected).")


def route_google(task: str) -> dict:
    """Decide the rail for a Google-family work-order. Never returns a CLI argv.

    search -> DOM preferred (playwright-dom guest). prove/ping -> gem-api.
    gemini.cmd is not a candidate on any path.
    """
    if task not in TASKS:
        raise WorkOrderError(
            "BAD_TASK",
            f"{task!r} is not a work-order task - known: {sorted(TASKS)}")
    if task in SEARCH_TASKS:
        return {
            "preferred": "DOM",
            "fallback": "API",
            "invoked_how": INVOKED_DOM,
            "fallback_how": INVOKED_API,
            "link_id": "gem-dom",
            "fallback_link_id": "gem-api",
            "module": "bts_gem",
            "urls": list(DOM_SEARCH_URLS),
            "cli": None,
        }
    return {
        "preferred": "API",
        "fallback": None,
        "invoked_how": INVOKED_API,
        "fallback_how": None,
        "link_id": "gem-api",
        "fallback_link_id": None,
        "module": "bts_gem",
        "urls": [],
        "cli": None,
    }


def _argv_is_forbidden(argv) -> bool:
    if not argv:
        return False
    names = []
    for tok in argv:
        names.append(Path(str(tok)).name.lower())
    return any(n in FORBIDDEN_CLI for n in names)


class WorkOrderDesk:
    """Drop + run work-orders under work/orders/<wo_id>/. Output.json is written
    on every terminal path, including typed rail failure. A missing Output is
    the measured scar and is not a legal outcome of run()."""

    def __init__(self, paths, ledger, gem_rail=None, dom_worker=None,
                 clock=time.time):
        self.paths = paths
        self.ledger = ledger
        self.gem_rail = gem_rail
        self.dom_worker = dom_worker
        self._clock = clock

    def inbox(self) -> Path:
        p = self.paths.role("work", "orders")
        makedirs(p)
        return p

    def wo_dir(self, wo_id: str) -> Path:
        # confine: wo_id is a single path part, never a traversal
        if not wo_id or "/" in wo_id or "\\" in wo_id or ".." in wo_id:
            raise WorkOrderError("BAD_ORDER", f"illegal wo_id {wo_id!r}")
        p = self.inbox() / wo_id
        makedirs(p)
        return p

    # ---------------- drop ----------------
    def drop(self, family: str, agent: str, task: str, prompt: str,
             model: str | None = None, nonce: str | None = None,
             wo_id: str | None = None) -> dict:
        """Write an immutable order.json. Returns the order dict (with wo_id)."""
        if family not in FAMILIES:
            raise WorkOrderError(
                "BAD_FAMILY",
                f"{family!r} is not a routed work-order family - known: "
                f"{sorted(FAMILIES)}. Anthropic is off; no invented routes.")
        if task not in TASKS:
            raise WorkOrderError(
                "BAD_TASK",
                f"{task!r} is not a work-order task - known: {sorted(TASKS)}")
        if family == "Google":
            resolved = resolve_google_model(agent)
        else:
            resolved = model or agent
        if model and model != resolved:
            raise WorkOrderError(
                "BAD_AGENT",
                f"model {model!r} does not match agent {agent!r} -> {resolved!r}")
        route = route_google(task) if family == "Google" else None
        order = {
            "wo_id": wo_id or _wo_id(self._clock),
            "family": family,
            "agent": agent,
            "model": resolved,
            "task": task,
            "prompt": prompt,
            "nonce": nonce or uuid.uuid4().hex,
            "tree_id": LIVE_TREE_ID,
            "install_tree_id": self.paths.sentinel.tree_id,
            "route": {k: route[k] for k in
                      ("preferred", "fallback", "invoked_how", "link_id",
                       "module") } if route else None,
            "dropped_at": self._clock(),
        }
        d = self.wo_dir(order["wo_id"])
        op = d / ORDER_NAME
        if op.exists():
            raise WorkOrderError("BAD_ORDER",
                                 f"{order['wo_id']} already dropped - orders are "
                                 f"immutable")
        op.write_text(json.dumps(order, indent=1), encoding="utf-8")
        self.ledger.append("WO_DROPPED",
                           {"wo_id": order["wo_id"], "family": family,
                            "task": task, "model": resolved,
                            "nonce": order["nonce"]})
        return order

    def load(self, wo_id: str) -> dict:
        p = self.wo_dir(wo_id) / ORDER_NAME
        if not p.exists():
            raise WorkOrderError("BAD_ORDER", f"no order.json for {wo_id}")
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except (ValueError, UnicodeDecodeError) as e:
            raise WorkOrderError("BAD_ORDER", f"torn order.json for {wo_id}: {e}") from e
        if not isinstance(d, dict) or d.get("wo_id") != wo_id:
            raise WorkOrderError("BAD_ORDER",
                                 f"order.json identity mismatch for {wo_id}")
        return d

    def pending(self) -> list[str]:
        out = []
        inbox = self.inbox()
        if not inbox.is_dir():
            return out
        for child in sorted(inbox.iterdir()):
            if (child / ORDER_NAME).is_file() and not (child / OUTPUT_NAME).is_file():
                out.append(child.name)
        return out

    # ---------------- run ----------------
    def run(self, wo_id: str) -> dict:
        """Execute one work-order. Output.json is written on EVERY path, including
        rail failure. The return value is the Output dict."""
        order = self.load(wo_id)
        out_path = self.wo_dir(wo_id) / OUTPUT_NAME
        if out_path.exists():
            # already terminal - do not re-run (report-never-retry)
            try:
                return json.loads(out_path.read_text(encoding="utf-8"))
            except (ValueError, UnicodeDecodeError):
                pass
        result = None
        try:
            result = self._execute(order)
        except WorkOrderError as e:
            result = self._fail(order, e.kind, str(e),
                                invoked_how=INVOKED_REFUSED_CLI if e.kind == "REFUSED"
                                else "REFUSED")
        except Exception as e:                                        # noqa: BLE001
            result = self._fail(order, "BROKE",
                                f"{type(e).__name__}: {e}",
                                invoked_how=order.get("route", {}).get(
                                    "invoked_how") or "BROKE")
        finally:
            # THE SCAR FIX: Output lands even if _execute raised, even if the
            # rail returned ok=false. A missing file is not a legal outcome.
            if result is None:
                result = self._fail(order, "BROKE",
                                    "runner produced no result record",
                                    invoked_how="BROKE")
            self._write_output(wo_id, result)
        return result

    def drain(self, max_orders: int = 20) -> list[dict]:
        out = []
        for wo_id in self.pending()[:max_orders]:
            out.append(self.run(wo_id))
        return out

    # ---------------- internals ----------------
    def _fail(self, order: dict, kind: str, detail: str,
              invoked_how: str) -> dict:
        return {
            "ok": False,
            "kind": kind,
            "detail": detail[:400],
            "nonce": order.get("nonce"),
            "invoked_how": invoked_how,
            "wo_id": order.get("wo_id"),
            "family": order.get("family"),
            "model": order.get("model"),
            "task": order.get("task"),
            "tree_id": LIVE_TREE_ID,
            "install_tree_id": self.paths.sentinel.tree_id,
            "text": "",
        }

    def _ok(self, order: dict, invoked_how: str, text: str,
            kind: str = "API", extra: dict | None = None) -> dict:
        out = {
            "ok": True,
            "kind": kind,
            "detail": "",
            "nonce": order["nonce"],
            "invoked_how": invoked_how,
            "wo_id": order["wo_id"],
            "family": order["family"],
            "model": order["model"],
            "task": order["task"],
            "tree_id": LIVE_TREE_ID,
            "install_tree_id": self.paths.sentinel.tree_id,
            "text": text,
        }
        if extra:
            out.update(extra)
        return out

    def _write_output(self, wo_id: str, result: dict) -> Path:
        p = self.wo_dir(wo_id) / OUTPUT_NAME
        p.write_text(json.dumps(result, indent=1), encoding="utf-8")
        self.ledger.append("WO_OUTPUT",
                           {"wo_id": wo_id, "ok": result.get("ok"),
                            "kind": result.get("kind"),
                            "invoked_how": result.get("invoked_how"),
                            "nonce": result.get("nonce")})
        return p

    def _execute(self, order: dict) -> dict:
        family, task = order["family"], order["task"]
        if family != "Google":
            raise WorkOrderError("BAD_FAMILY",
                                 f"{family!r} has no work-order route")
        route = route_google(task)
        # belt: never construct a forbidden CLI even if a caller stuffed argv
        if route.get("cli") or _argv_is_forbidden(route.get("argv")):
            raise WorkOrderError(
                "REFUSED",
                "gemini.cmd / Gemini CLI is not a COSMOS Google-family rail - "
                "the measured fail (rc=41 Vertex env missing, no Output) is "
                "why this path is closed. Use gem-api / bts_gem.ask.")
        if task in SEARCH_TASKS:
            return self._run_search(order, route)
        return self._run_api(order, route)

    def _run_search(self, order: dict, route: dict) -> dict:
        """DOM first. UNREACHABLE/SESSION_EXPIRED/AUTH_REQUIRED may fall through
        to gem-api as an EXPLICIT audited fallback - never silent, never CLI."""
        if self.dom_worker is not None:
            url = route["urls"][0]
            # guest gemini.google.com; query surfaces get the prompt as q=
            if "search" in url:
                url = url + "?q=" + order["prompt"][:200]
            r = self.dom_worker.run_attempt(order["wo_id"], url,
                                            require_session=False)
            if r.get("ok"):
                return self._ok(order, INVOKED_DOM, r.get("text") or "",
                                kind="DOM")
            if r.get("kind") in ("UNREACHABLE", "SESSION_EXPIRED", "AUTH_REQUIRED"):
                self.ledger.append("WO_RAIL_FALLBACK",
                                   {"wo_id": order["wo_id"],
                                    "from": INVOKED_DOM, "to": INVOKED_API,
                                    "reason": r.get("kind"),
                                    "detail": "explicit audited fallback to "
                                              "gem-api for a typed ping-shaped "
                                              "retry, not a silent downgrade"})
                return self._run_api(order, route_google("prove"))
            return self._fail(order, r.get("kind") or "BROKE",
                              r.get("detail") or "DOM rail failed",
                              invoked_how=INVOKED_DOM)
        # no DOM worker composed: typed, then explicit API fallback
        self.ledger.append("WO_RAIL_FALLBACK",
                           {"wo_id": order["wo_id"],
                            "from": INVOKED_DOM, "to": INVOKED_API,
                            "reason": "UNREACHABLE",
                            "detail": "no DOM worker composed - explicit "
                                      "audited fallback to gem-api"})
        return self._run_api(order, route_google("prove"))

    def _run_api(self, order: dict, route: dict) -> dict:
        rail = self.gem_rail
        if rail is None:
            from cosmos_node_rails import NodeRail
            rail = NodeRail(route["module"], metered_usd=0.03)
        payload = {
            "prompt": order["prompt"],
            "kwargs": {"model": order["model"],
                       "nonce": order["nonce"]},
        }
        r = rail.dispatch(payload)
        how = INVOKED_API
        if not r.get("ok"):
            return self._fail(order, r.get("kind") or "BROKE",
                              r.get("detail") or "gem-api rail failed",
                              invoked_how=how)
        text = r.get("text") or r.get("full_text") or ""
        return self._ok(order, how, text, kind=r.get("kind") or "API",
                        extra={"node": r.get("node"), "usd": r.get("usd")})


def register_google_family_rails(registry, adapters, gem_rail=None,
                                 dom_rail=None, spend_gate=None) -> dict:
    """Register the Google-family links: gem-dom (preferred for search) and
    gem-api (typed ping / prove). Probes are honest; registration is not
    capability. gemini.cmd is not registered."""
    from cosmos_node_rails import NodeRail
    if gem_rail is None:
        gem_rail = NodeRail("bts_gem", metered_usd=0.03)
    registry.register("gem-api", "API", "core", "google-prove", policy_rank=0)
    registry.register("gem-api-search", "API", "core", "google-search",
                      policy_rank=0)
    registry.attach_probe("gem-api", gem_rail.probe)
    registry.attach_probe("gem-api-search", gem_rail.probe)
    adapters["gem-api"] = gem_rail
    adapters["gem-api-search"] = gem_rail
    if spend_gate is not None:
        try:
            spend_gate.set_budget("gem-api", 300.0)
            spend_gate.set_budget("gem-api-search", 300.0)
        except Exception:                                            # noqa: BLE001
            pass
    if dom_rail is not None:
        registry.register("gem-dom", "DOM", "core", "google-search",
                          policy_rank=10)
        registry.attach_probe("gem-dom", dom_rail.probe)
        adapters["gem-dom"] = dom_rail
    return adapters
