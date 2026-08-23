#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_makers - the CREATE catalog (F5 builder).

A maker is a dated catalog card that tells an operator HOW to create one kind of
thing: Agent, Tool, Connector, or Skill. KDash is a pure client of this catalog
via GET /api/v1/makers?kind=...; the dashboard does not invent makers.

Same authority pattern as the registry: register() records a CLAIM on the ledger;
list() and get() are projections. Built-in makers live in this module so a
read-only kernel (status/audit) can still answer without writing. There is no
delete - never delete.

Scar this closes: a CREATE panel that hard-codes cards is a second universe the
moment the catalog moves. The panel reads the API; the API is the catalog.
"""
from __future__ import annotations

import time
from typing import Optional

from cosmos_ledger import Ledger

MAKER_KINDS = ("agent", "tool", "connector", "skill")


class MakerError(RuntimeError):
    """kind in {BAD_KIND, MISSING_KIND, UNKNOWN_MAKER, DUPLICATE, UNQUALIFIED}.

    BAD_KIND      - kind is present but not one of the four CREATE kinds.
    MISSING_KIND  - list() was asked with no kind; empty is not "all".
    UNKNOWN_MAKER - asked about a maker_id that is not in the catalog.
    DUPLICATE     - re-registering a maker_id that already exists.
    UNQUALIFIED   - a card is missing a required field (location / function /
                    access / invoke). A maker nobody can open is a claim.
    """

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def normalize_kind(kind: Optional[str]) -> str:
    """Lower-case the kind and REFUSE if it is missing or not one of the four."""
    if kind is None or str(kind).strip() == "":
        raise MakerError(
            "MISSING_KIND",
            "kind is required - Agent, Tool, Connector, or Skill; "
            "omitting it is not 'all makers'")
    k = str(kind).strip().lower()
    if k not in MAKER_KINDS:
        raise MakerError(
            "BAD_KIND",
            f"{kind!r} is not a CREATE kind; expected one of {list(MAKER_KINDS)}")
    return k


def _card(row: dict) -> dict:
    """Public card shape: location, function, access, tags, plus invoke."""
    return {
        "maker_id": row["maker_id"],
        "kind": row["kind"],
        "name": row.get("name") or row["maker_id"],
        "location": row["location"],
        "function": row["function"],
        "access": row["access"],
        "tags": list(row.get("tags") or []),
        "invoke": row["invoke"],
    }


# Built-in catalog. These are the COSMOS surfaces an operator can create from
# today. location is a repo path (not a guessed absolute). access is how the
# maker is reached. invoke is the instruction the CREATE panel reveals.
BUILTINS: tuple[dict, ...] = (
    # ---- agents ----
    {
        "maker_id": "dom-agent",
        "kind": "agent",
        "name": "DOM agent",
        "location": "cosmos/cosmos_dom.py",
        "function": "Browser-DOM agent worker - the preferred path, and the path used when no other rail works",
        "access": "local",
        "tags": ["dom", "preferred", "browser"],
        "invoke": (
            "Preferred path. This maker starts a browser-DOM agent worker.\n"
            "1. Confirm access is local on this workstation.\n"
            "2. POST /api/v1/jobs\n"
            "   {\"command\": \"maker:dom-agent\", \"priority\": \"normal\"}\n"
            "3. The scheduler claims the job. Typed failures: UNREACHABLE, "
            "SESSION_EXPIRED, AUTH_REQUIRED, BROKE.\n"
            "4. DOM is the default rail; API is the fallback, never a silent swap."
        ),
    },
    {
        "maker_id": "kernel-worker",
        "kind": "agent",
        "name": "Kernel worker",
        "location": "cosmos/cosmos_kernel.py",
        "function": "Core worker identity on the composed kernel - fenced writes, mail, scheduler",
        "access": "local",
        "tags": ["core", "worker"],
        "invoke": (
            "Create a kernel worker identity.\n"
            "1. Boot a writing Kernel(root, worker=<name>).\n"
            "2. Protected writes go through Kernel.protected_write (lease + fenced commit).\n"
            "3. Status and audit use a read-only kernel - a reader is not a writer."
        ),
    },
    {
        "maker_id": "mcp-agent",
        "kind": "agent",
        "name": "MCP agent",
        "location": "cosmos/cosmos_mcp.py",
        "function": "Drive COSMOS through the stdio JSON-RPC MCP adapter (one protocol, many clients)",
        "access": "stdio",
        "tags": ["mcp", "protocol"],
        "invoke": (
            "Open the MCP adapter as an agent rail.\n"
            "1. Access is stdio JSON-RPC (one JSON object per line).\n"
            "2. Handshake: initialize, then tools/list, then tools/call.\n"
            "3. Every tool call delegates to the kernel and is ledgered - "
            "the client cannot reach around authority."
        ),
    },
    # ---- tools ----
    {
        "maker_id": "tool-contracts",
        "kind": "tool",
        "name": "Tool contracts",
        "location": "cosmos/cosmos_tools.py",
        "function": "Declare a tool contract (verbs + behavior); disposition is a dated decision, never drift",
        "access": "local",
        "tags": ["contracts", "ledger"],
        "invoke": (
            "Declare a tool, then attach a check.\n"
            "1. ToolContracts(ledger).declare(name, verbs, behavior)\n"
            "2. attach_check(name, fn) where fn is () -> (ok, detail)\n"
            "3. verify(name) REFUSES CONTRACT_FAIL when no check is attached - "
            "registration is not capability.\n"
            "4. GET /api/v1/tools returns the report with measurement age."
        ),
    },
    {
        "maker_id": "commander",
        "kind": "tool",
        "name": "Command seam",
        "location": "cosmos/cosmos_command.py",
        "function": "Voice and frontend command seam: text in, kernel action out, refusals typed",
        "access": "bearer",
        "tags": ["command", "voice"],
        "invoke": (
            "Speak a command through the HTTP seam.\n"
            "1. POST /api/v1/command  {\"text\": \"status\"}  (Bearer token)\n"
            "2. First word is the verb; help teaches the submit grammar.\n"
            "3. Refusals arrive as {error: <kind>} - BAD_ARGS, FORBIDDEN, and kin."
        ),
    },
    {
        "maker_id": "health-board",
        "kind": "tool",
        "name": "Health board",
        "location": "cosmos/cosmos_health.py",
        "function": "Kernel selftests with positive AND negative controls - a row that cannot go red is not a check",
        "access": "bearer",
        "tags": ["health", "selftest"],
        "invoke": (
            "Run the health board now.\n"
            "1. GET /api/v1/health  (Bearer token)\n"
            "2. Every row is a measurement. negative_control_red must be able to go red.\n"
            "3. Do not treat a missing probe as a pass."
        ),
    },
    {
        "maker_id": "spend-gate",
        "kind": "tool",
        "name": "Spend gate",
        "location": "cosmos/cosmos_spend.py",
        "function": "Deny before spend rather than report after - the breaker is a gate, not a log",
        "access": "local",
        "tags": ["spend", "breaker"],
        "invoke": (
            "Ask the spend gate before a metered call.\n"
            "1. GET /api/v1/spend  (Bearer token) for the audit projection.\n"
            "2. A rail that cannot answer is denied, not guessed.\n"
            "3. Totals without a measured_at are not totals."
        ),
    },
    # ---- connectors ----
    {
        "maker_id": "http-api",
        "kind": "connector",
        "name": "HTTP API",
        "location": "cosmos/cosmos_service.py",
        "function": "Versioned HTTP API - the one surface KDash, voice, and mobile all consume",
        "access": "bearer",
        "tags": ["http", "api", "v1"],
        "invoke": (
            "Connect a client to the API.\n"
            "1. cosmos serve --root <root> --port 8770\n"
            "2. Bearer token lives in config/api_token.txt (created on first serve).\n"
            "3. Every JSON response carries served_at. A panel that cannot show its age "
            "is the frozen-dashboard scar.\n"
            "4. Open kdash/index.html, enter the API base and token, CONNECT."
        ),
    },
    {
        "maker_id": "rails-registry",
        "kind": "connector",
        "name": "Rails registry",
        "location": "cosmos/cosmos_registry.py",
        "function": "Node and rail links as first-class entities with dated probes; DOM-first is policy data",
        "access": "bearer",
        "tags": ["rails", "registry"],
        "invoke": (
            "Register a rail, then probe it.\n"
            "1. Registry.register(link_id, rail_type, src, dst)\n"
            "2. attach_probe(link_id, fn) where fn is () -> (ok, detail)\n"
            "3. GET /api/v1/rails returns the matrix with verification age per link.\n"
            "4. A link with no probe is UNPROBEABLE, never silently verified."
        ),
    },
    {
        "maker_id": "mcp-server",
        "kind": "connector",
        "name": "MCP server",
        "location": "cosmos/cosmos_mcp.py",
        "function": "stdio JSON-RPC MCP server exposing kernel verbs to Claude, Cursor, Copilot, Grok",
        "access": "stdio",
        "tags": ["mcp", "json-rpc"],
        "invoke": (
            "Wire an MCP client to COSMOS.\n"
            "1. Access is stdio, protocol 2024-11-05.\n"
            "2. tools/list exposes cosmos_status, cosmos_submit, cosmos_jobs, "
            "cosmos_audit, cosmos_health, cosmos_command, cosmos_events.\n"
            "3. tools/call delegates to the live kernel."
        ),
    },
    {
        "maker_id": "mail-ipc",
        "kind": "connector",
        "name": "Mail IPC",
        "location": "cosmos/cosmos_mail.py",
        "function": "N>2 mailbox IPC - missing, empty, unreadable, and stale are four distinct states",
        "access": "local",
        "tags": ["mail", "ipc"],
        "invoke": (
            "Open a worker mailbox.\n"
            "1. Mailbox(state/mail, worker).register()\n"
            "2. send(recipient, subject, body) writes an immutable message file.\n"
            "3. probe() reports LIVE / EMPTY / MISSING / STALE - missing is not 'no news'.\n"
            "4. A half-written message is TORN_MESSAGE by hash."
        ),
    },
    # ---- skills ----
    {
        "maker_id": "backup-rehearse",
        "kind": "skill",
        "name": "Backup and rehearse",
        "location": "cosmos/cosmos_backup.py",
        "function": "Hash-verified backup plus a rehearsed restore - a backup that was never restored is a claim",
        "access": "local",
        "tags": ["backup", "rehearse"],
        "invoke": (
            "Run backup, then rehearse the restore.\n"
            "1. cosmos backup --root <root> --target <off-machine>\n"
            "2. cosmos rehearse --root <root> --backup <dest> --scratch <dir>\n"
            "3. Tampered bytes raise REHEARSAL_FAILED. Empty scope raises EMPTY_SCOPE.\n"
            "4. Off-machine or it does not count."
        ),
    },
    {
        "maker_id": "crucible",
        "kind": "skill",
        "name": "Crucible round",
        "location": "cosmos/cosmos_crucible.py",
        "function": "Submit a crucible critique round as a scheduled job - remote is not unaudited",
        "access": "bearer",
        "tags": ["crucible", "critique"],
        "invoke": (
            "Queue a crucible round.\n"
            "1. POST /api/v1/crucible\n"
            "   {\"sources\": [\"FINAL_ARCHITECTURE.md\"], \"critics\": [], "
            "\"priority\": \"high\"}\n"
            "2. Sources are role-relative docs paths; the run goes through the scheduler.\n"
            "3. Returns land in the run's out_dir; the request is ledgered."
        ),
    },
    {
        "maker_id": "fenced-commit",
        "kind": "skill",
        "name": "Fenced commit",
        "location": "cosmos/cosmos_lock.py",
        "function": "Lease plus monotonic fencing token plus fenced commit - stale tokens are refused and ledgered",
        "access": "local",
        "tags": ["lock", "fence"],
        "invoke": (
            "Take a lease, then commit under it.\n"
            "1. Kernel.protected_write(resource, relpath, content)\n"
            "2. A stale token is STALE_TOKEN - refused and ledgered, never a silent overwrite.\n"
            "3. Dying-holder recovery is expiry on the arbiter clock, not cleanup discipline."
        ),
    },
    {
        "maker_id": "context-manifest",
        "kind": "skill",
        "name": "Context manifest",
        "location": "cosmos/cosmos_context.py",
        "function": "Session context at close - inherited facts, live leases, open watchers, handoff recipient",
        "access": "local",
        "tags": ["context", "carry-over"],
        "invoke": (
            "Open a session, then close it with a valid manifest.\n"
            "1. session = Kernel.open_session(session_id, stream)\n"
            "2. Closure without a valid manifest is an OPEN_CONTEXT incident.\n"
            "3. Carry-over is structural: the next session reads the manifest, not memory."
        ),
    },
)


class Makers:
    """Built-in catalog plus ledger-registered extras. list(kind) is the CREATE
    panel's only read. There is no delete."""

    def __init__(self, ledger: Ledger, clock=time.time):
        self.ledger = ledger
        self._clock = clock

    # ---------------- claims ----------------
    def register(self, maker_id: str, kind: str, location: str, function: str,
                 access: str, tags: Optional[list] = None, invoke: str = "",
                 name: str = "") -> dict:
        """Record a new maker. Required: maker_id, kind, location, function,
        access, invoke. A second registration of the same id is DUPLICATE."""
        kind = normalize_kind(kind)
        mid = str(maker_id or "").strip()
        if not mid:
            raise MakerError("UNQUALIFIED", "maker_id is required")
        if mid in self.catalog():
            raise MakerError(
                "DUPLICATE",
                f"{mid!r} already exists - a second registration is a drift, "
                f"not an update; never delete, never silently replace")
        loc = str(location or "").strip()
        fn = str(function or "").strip()
        acc = str(access or "").strip()
        inv = str(invoke or "").strip()
        if not loc or not fn or not acc:
            raise MakerError(
                "UNQUALIFIED",
                "location, function, and access are required - a card without "
                "them cannot be rendered")
        if not inv:
            raise MakerError(
                "UNQUALIFIED",
                "invoke instructions are required - a maker nobody can open is a claim")
        if tags is None:
            tags = []
        if not isinstance(tags, list) or any(not isinstance(t, str) for t in tags):
            raise MakerError("UNQUALIFIED", "tags must be a list of strings")
        payload = {
            "maker_id": mid,
            "kind": kind,
            "name": str(name or mid),
            "location": loc,
            "function": fn,
            "access": acc,
            "tags": list(tags),
            "invoke": inv,
        }
        self.ledger.append("MAKER_REGISTERED", payload)
        return _card(payload)

    # ---------------- projection ----------------
    def state(self) -> dict:
        """Ledger-registered makers only (not builtins)."""
        def fold(s, rec):
            if rec["event"] == "MAKER_REGISTERED":
                p = rec["payload"]
                s[p["maker_id"]] = dict(p)
            return s
        return self.ledger.project(fold, {})

    def catalog(self) -> dict:
        """Builtins plus ledger overlays. Ledger wins on the same maker_id
        only after a successful register, which refuses duplicates, so the
        overlay is extras rather than replacements."""
        out = {m["maker_id"]: dict(m) for m in BUILTINS}
        out.update(self.state())
        return out

    def list(self, kind: Optional[str]) -> list[dict]:
        """Matching cards for one kind. Empty list is not an error."""
        k = normalize_kind(kind)
        rows = [_card(m) for m in self.catalog().values() if m["kind"] == k]
        rows.sort(key=lambda r: r["maker_id"])
        return rows

    def get(self, maker_id: str) -> dict:
        """One card, including invoke instructions. UNKNOWN_MAKER if absent."""
        mid = str(maker_id or "").strip()
        cat = self.catalog()
        if mid not in cat:
            raise MakerError("UNKNOWN_MAKER", mid or "(empty id)")
        return _card(cat[mid])

    def report(self, kind: Optional[str]) -> dict:
        """API body: kind + makers + measured_at. served_at is added by the service."""
        k = normalize_kind(kind)
        return {
            "measured_at": self._clock(),
            "kind": k,
            "makers": self.list(k),
        }
