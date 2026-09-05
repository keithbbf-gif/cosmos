#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tools.surface — the invoke layer for the F-29 tools/ surface.

A tool is a named verb that returns a value only that surface can emit.
`inventory()` is a declaration. `invoke()` is the measurement. A non-zero
rc is never a hand — the maker-hands scar (a CLI that printed the sought
token while failing would otherwise score green). An empty bind value is
never a hand either: a reply is not an *authenticated* reply.

Typed refusals, fail-closed. No hard-coded runtime paths; no key material
is read, printed, or logged. Default tests inject a transport so the gate
never reaches the network.
"""
from __future__ import annotations

import json
from dataclasses import dataclass

SCHEMA = "cosmos-tools-surface/1"


class ToolError(RuntimeError):
    """kind in {UNKNOWN_TOOL, BAD_VERB, NONZERO_RC, NO_VALUE, UNREACHABLE, BAD_TRANSPORT}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


@dataclass(frozen=True)
class ToolSpec:
    """The CONTRACT: what the tool promises, not how it is implemented.

    No credential field. A tool that needs a COSMOS-held secret is a rail,
    not an entry on this surface (the first two tools are keyless MCP).
    """
    name: str
    verbs: tuple[str, ...]
    behavior: str
    bind: str
    url: str


class ToolSurface:
    def __init__(self, specs: dict[str, ToolSpec], transport=None,
                 parser=None):
        if not specs:
            raise ToolError("BAD_TRANSPORT", "empty tool table")
        self.specs = dict(specs)
        self.transport = transport
        self.parser = parser

    def inventory(self) -> list[dict]:
        """Declared tools. Registration is not capability; nothing is invoked."""
        return [{"name": s.name, "verbs": list(s.verbs),
                 "behavior": s.behavior, "bind": s.bind, "url": s.url}
                for s in (self.specs[k] for k in sorted(self.specs))]

    def report(self) -> list[dict]:
        """Contracts-shaped projection of the declared inventory. Does not invoke.

        GET /api/v1/tools historically called kernel.tools.report(). F-29
        rebound that slot to this surface; a missing .report 500s the
        route (wave3 AttributeError scar). Registration is not capability:
        verified is None until invoke() measures.
        """
        return [{"name": s.name,
                 "disposition": None,
                 "verified": None,
                 "age_s": None}
                for s in (self.specs[k] for k in sorted(self.specs))]

    def invoke(self, name: str, verb: str = "probe") -> dict:
        """Run the verb NOW. NONZERO_RC is never ok. Empty bind is never ok."""
        spec = self.specs.get(name)
        if spec is None:
            raise ToolError("UNKNOWN_TOOL", name)
        if verb not in spec.verbs:
            raise ToolError("BAD_VERB",
                            f"{name} verbs={list(spec.verbs)} not {verb!r}")
        if self.transport is None:
            raise ToolError("BAD_TRANSPORT",
                            "no transport injected and no default bound")
        if self.parser is None:
            raise ToolError("BAD_TRANSPORT", "no parser bound")
        result = self.transport(spec.url, _INIT_BODY, _HEADERS)
        rc = result.get("rc")
        http = result.get("http")
        raw = result.get("body") or ""
        if rc is None and http is None:
            raise ToolError("UNREACHABLE", raw[:200] or "no http and no rc")
        if rc is None:
            rc = 0 if http == 200 else 1
        info = self.parser(raw)
        if rc != 0:
            raise ToolError(
                "NONZERO_RC",
                f"rc={rc} http={http}; a non-zero exit is never a hand "
                f"(maker-hands scar). body_has_bind={bool(info)}")
        if not info or not info.get("name"):
            raise ToolError("NO_VALUE",
                            f"{name}: initialize reply has no {spec.bind}")
        return {
            "ok": True,
            "schema": SCHEMA,
            "tool": name,
            "verb": verb,
            "value": info["name"],
            "bind": spec.bind,
            "http": http,
            "serverInfo": info,
        }


_INIT_BODY = json.dumps({
    "jsonrpc": "2.0", "id": 1, "method": "initialize",
    "params": {"protocolVersion": "2025-06-18", "capabilities": {},
               "clientInfo": {"name": "cosmos-tools-surface", "version": "1"}},
})
_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream",
    "User-Agent": "cosmos-tools-surface/1",
}


def parse_server_info(raw: str) -> dict | None:
    """Lift result.serverInfo from a JSON body or an SSE `data:` frame.

    A GET proves nothing about MCP; the handshake is the named verb. xAI
    replies plain JSON; OpenAI replies SSE (`event: message` / `data: {…}`).
    Substring-matching the token is not proof — we json.loads a frame.
    """
    for line in str(raw or "").splitlines():
        payload = line[6:] if line.startswith("data: ") else line
        payload = payload.strip()
        if not payload or payload[0] not in "{[":
            continue
        try:
            doc = json.loads(payload)
        except (json.JSONDecodeError, ValueError):
            continue
        info = (doc.get("result") or {}).get("serverInfo")
        if isinstance(info, dict) and info.get("name"):
            return info
    return None
