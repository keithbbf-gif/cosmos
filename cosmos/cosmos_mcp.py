#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_mcp - COSMOS SPOKEN AS MCP (F5 builder). A stdio JSON-RPC 2.0 MCP server that
exposes the kernel's verbs as MCP tools, so any MCP client (Claude, Cursor, Copilot,
Grok) drives COSMOS through one protocol - the incumbent's bts_fs_mcp lesson: one
protocol adapter, many clients, every op delegating to the real thing (here, the kernel).

TOOLS EXPOSED: cosmos_status · cosmos_submit · cosmos_jobs · cosmos_audit ·
cosmos_health · cosmos_command · cosmos_events. Every tool call delegates to the kernel
and is ledgered - an MCP client cannot reach around the authority.

Transport is stdio JSON-RPC (one JSON object per line): initialize · tools/list ·
tools/call. No external deps. The handler is pure (str->str) so it is tested without a
pipe, then wired to stdin/stdout for the real server.
"""
from __future__ import annotations

import json
import sys
from typing import Callable

PROTOCOL = "2024-11-05"

TOOLS = [
    {"name": "cosmos_status", "description": "kernel readiness + root identity + ledger head",
     "inputSchema": {"type": "object", "properties": {}}},
    {"name": "cosmos_submit", "description": "submit a job",
     "inputSchema": {"type": "object",
                     "properties": {"command": {"type": "string"},
                                    "priority": {"type": "string"}},
                     "required": ["command"]}},
    {"name": "cosmos_jobs", "description": "job states",
     "inputSchema": {"type": "object", "properties": {}}},
    {"name": "cosmos_audit", "description": "the audit projection",
     "inputSchema": {"type": "object", "properties": {}}},
    {"name": "cosmos_health", "description": "the health board",
     "inputSchema": {"type": "object", "properties": {}}},
    {"name": "cosmos_command", "description": "the voice/frontend command seam",
     "inputSchema": {"type": "object", "properties": {"text": {"type": "string"}},
                     "required": ["text"]}},
    {"name": "cosmos_events", "description": "ledger tail since a sequence",
     "inputSchema": {"type": "object",
                     "properties": {"since_seq": {"type": "integer"}}}},
]


class MCPServer:
    def __init__(self, kernel):
        self.k = kernel

    def _call_tool(self, name: str, args: dict) -> dict:
        k = self.k
        if name == "cosmos_status":
            last = k.ledger.last()
            return {"ready": k.ready, "root": str(k.paths.root),
                    "tree_id": k.paths.sentinel.tree_id,
                    "ledger_head": {"seq": last["seq"], "event": last["event"]}}
        if name == "cosmos_submit":
            return {"job_id": k.sched.submit(args["command"], args.get("priority", "normal"))}
        if name == "cosmos_jobs":
            return {j: v["st"] for j, v in k.sched._state().items()}
        if name == "cosmos_audit":
            return k.audit()
        if name == "cosmos_health":
            from cosmos_health import HealthBoard
            return HealthBoard(k).run()
        if name == "cosmos_command":
            from cosmos_command import Commander
            return Commander(k).handle(args["text"])
        if name == "cosmos_events":
            since = int(args.get("since_seq", 0))
            evs = [{"seq": r["seq"], "event": r["event"], "writer": r["writer"]}
                   for r in k.ledger.verify() if r["seq"] > since][:100]
            return {"events": evs}
        raise KeyError(name)

    def handle(self, line: str) -> str | None:
        """One JSON-RPC request line -> one response line (or None for notifications)."""
        try:
            req = json.loads(line)
        except ValueError:
            return json.dumps({"jsonrpc": "2.0", "id": None,
                               "error": {"code": -32700, "message": "parse error"}})
        rid = req.get("id")
        method = req.get("method")
        try:
            if method == "initialize":
                result = {"protocolVersion": PROTOCOL,
                          "capabilities": {"tools": {}},
                          "serverInfo": {"name": "cosmos", "version": "1.0-f5"}}
            elif method == "tools/list":
                result = {"tools": TOOLS}
            elif method == "tools/call":
                p = req.get("params", {})
                out = self._call_tool(p["name"], p.get("arguments", {}))
                # MCP content contract: text content blocks
                result = {"content": [{"type": "text",
                                       "text": json.dumps(out, indent=1)}]}
            elif method in ("notifications/initialized", "initialized"):
                return None                # notification, no response
            else:
                return json.dumps({"jsonrpc": "2.0", "id": rid,
                                   "error": {"code": -32601,
                                             "message": f"method not found: {method}"}})
        except KeyError as e:
            return json.dumps({"jsonrpc": "2.0", "id": rid,
                               "error": {"code": -32602,
                                         "message": f"unknown tool/arg: {e}"}})
        except Exception as e:                                        # noqa: BLE001
            return json.dumps({"jsonrpc": "2.0", "id": rid,
                               "error": {"code": -32603,
                                         "message": f"{type(e).__name__}: {e}"}})
        return json.dumps({"jsonrpc": "2.0", "id": rid, "result": result})

    def serve_stdio(self) -> None:                       # pragma: no cover (real pipe)
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            resp = self.handle(line)
            if resp is not None:
                sys.stdout.write(resp + "\n")
                sys.stdout.flush()
