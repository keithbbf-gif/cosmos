#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_mcp_client - COSMOS as an MCP *client* (stdio JSON-RPC 2.0).

`cosmos_mcp.py` is the inbound server (KDash/Claude talk TO Core). This module
speaks OUT to a child MCP server. Two faces, one protocol. Does not edit the
server.

Owns a long-lived stdin Popen + tree-kill. `cosmos_platform.run` /
`run_tree_killed` cannot keep a pipe (no stdin=PIPE). Kill is `taskkill /T`
on the child pid (grandchildren). There is no Job-Object in cosmos_platform.

Windows: if the command is `npx`, argv is `[cmd.exe, /c, npx, …]` — not
`shell=True`, never a .bat. Prefer `node.exe` + a resolved `cli.js` when the
caller already has that path (cmd's parser is a quoting surface). Prompts and
tool arguments travel on JSON-RPC stdin, never interpolated into the cmd line.

Transport is newline-delimited JSON-RPC (MCP SDK stdio: stringify + newline).
"""
from __future__ import annotations

import json
import os
import queue
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

PROTOCOL = "2024-11-05"
CLIENT_NAME = "cosmos-mcp-client"
CLIENT_VERSION = "1"
SCHEMA = "cosmos-mcp-client/1"
MCP_COOKBOOK = (
    "https://openrouter.ai/docs/cookbook/coding-agents/mcp-servers"
)

# Default-deny RCE-equivalent. Playwright lists this in the core 24; the
# client must refuse tools/call even though the server will list it.
DEFAULT_DENY = frozenset({"browser_run_code_unsafe"})
# Cookbook example: @modelcontextprotocol/server-filesystem on /Applications
# with write_file. Not a COSMOS named pin. Do not spawn it.
FILESYSTEM_MCP = "@modelcontextprotocol/server-filesystem"

NAMED_SERVERS = (
    {"id": "cosmos", "label": "COSMOS spoken as MCP", "kind": "server",
     "module": "cosmos_mcp",
     "note": "Inbound: KDash/Cursor talk TO Core. tools/list is in-process."},
    {"id": "playwright", "label": "Playwright DOM", "kind": "client",
     "module": "cosmos_playwright_rail",
     "note": "Existing DOM rail. MCP is transport, not a second Core."},
    {"id": "openwork", "label": "OpenWork", "kind": "via",
     "via": "mcp:openwork", "note": "Named via. NO_HOST until a session exists."},
    {"id": "github", "label": "GitHub", "kind": "via",
     "via": "mcp:github", "note": "Named via. NO_HOST until a session exists."},
    {"id": "bts", "label": "BTS", "kind": "via",
     "via": "mcp:bts", "note": "Named via. NO_HOST until a session exists."},
)


class McpClientError(RuntimeError):
    """kind in {UNREACHABLE, BROKE, DENIED, TIMEOUT, BAD_SPEC}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def convert_tool_format(tool) -> dict:
    """MCP tools/list item → OpenAI-compatible function tool.

    OpenRouter cookbook mcp-servers: spread these into chat.completions
    `tools`. Does not spawn a server. Does not call the tool.
    """
    if not isinstance(tool, dict):
        raise McpClientError("BAD_SPEC", "tool must be a dict (MCP JSON-RPC, not SDK object)")
    name = str(tool.get("name") or "").strip()
    if not name:
        raise McpClientError("BAD_SPEC", "tool.name is required")
    schema = tool.get("inputSchema")
    if schema is None:
        schema = tool.get("input_schema")
    if not isinstance(schema, dict):
        schema = {}
    props = schema.get("properties") if isinstance(schema.get("properties"), dict) else {}
    req = schema.get("required") if isinstance(schema.get("required"), list) else []
    req = [str(x) for x in req if x]
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": str(tool.get("description") or ""),
            "parameters": {
                "type": "object",
                "properties": props,
                "required": req,
            },
        },
    }


def openai_tools_from_mcp(tools) -> list[dict]:
    out = []
    for t in tools or []:
        if not isinstance(t, dict):
            continue
        if not t.get("name"):
            continue
        out.append(convert_tool_format(t))
    return out


def named_servers() -> dict:
    """GET fold. Never mkdir. Never spawn npx / filesystem MCP."""
    here = Path(__file__).resolve().parent
    rows = []
    for s in NAMED_SERVERS:
        rec = dict(s)
        mod = s.get("module")
        present = False
        if mod:
            present = (here / f"{mod}.py").is_file()
        rec["present"] = present
        rec["led"] = "PRESENT" if present else "NO_HOST"
        rec.pop("module", None)
        rows.append(rec)
    cosmos_tools = []
    try:
        from cosmos_mcp import TOOLS as CORE_TOOLS
        cosmos_tools = openai_tools_from_mcp(CORE_TOOLS)
    except Exception:  # noqa: BLE001
        cosmos_tools = []
    return {
        "schema": SCHEMA,
        "ok": True,
        "cookbook": MCP_COOKBOOK,
        "n": len(rows),
        "servers": rows,
        "cosmos_openai_tools": cosmos_tools,
        "n_cosmos_tools": len(cosmos_tools),
        "does_not_vendor_openrouter_mcp": True,
        "does_not_spawn_filesystem": True,
        "filesystem_mcp_refused": FILESYSTEM_MCP,
        "note": (
            "MCP tool defs convert to OpenAI tools for OpenRouter chat. "
            "Named pins only. Cookbook filesystem /Applications write_file "
            "is REFUSED. GET never spawns. tools/call still hits the deny list."
        ),
    }


def npx_argv(npx_args: list[str]) -> list[str]:
    """Windows-safe npx spawn. Argv list, cmd.exe as argv[0], never shell=True."""
    if not isinstance(npx_args, list) or any(not isinstance(a, str) for a in npx_args):
        raise McpClientError("BAD_SPEC", "npx_args must be a list of str")
    if any(FILESYSTEM_MCP in a for a in npx_args):
        raise McpClientError(
            "REFUSED",
            f"{FILESYSTEM_MCP} is the cookbook filesystem example — not a COSMOS pin",
        )
    cmd = shutil.which("cmd") or shutil.which("cmd.exe")
    if not cmd:
        raise McpClientError("UNREACHABLE", "cmd.exe not on PATH (Windows spawn)")
    return [cmd, "/c", "npx", *npx_args]


def tree_kill(pid: int | None) -> str:
    """Kill the process tree. Reports the outcome; does not claim Job-Object."""
    if pid is None:
        return "no-pid"
    if os.name == "nt":
        from cosmos_platform import CREATE_NO_WINDOW
        k = subprocess.run(
            ["taskkill", "/PID", str(pid), "/T", "/F"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            creationflags=CREATE_NO_WINDOW,
        )
        return f"taskkill /T rc={k.returncode}: {(k.stdout or k.stderr or '').strip()[:150]}"
    try:
        os.kill(pid, 9)
        return "SIGKILL"
    except OSError as e:
        return f"kill-failed: {e}"


class StdioTransport:
    """Newline JSON-RPC over a child stdin/stdout. Inject a FakeTransport in tests."""

    def __init__(self, argv: list[str], *, env: dict | None = None,
                 cwd: str | Path | None = None, timeout_s: float = 30):
        if isinstance(argv, str):
            raise McpClientError("BAD_SPEC", "argv list only — a string implies a shell")
        self.argv = list(argv)
        self.env = env
        self.cwd = str(cwd) if cwd is not None else None
        self.timeout_s = float(timeout_s)
        self.proc = None
        self._q: queue.Queue = queue.Queue()
        self._stderr: list[str] = []
        self._alive = False
        self.kill_result = None

    @property
    def pid(self) -> int | None:
        return None if self.proc is None else self.proc.pid

    def start(self) -> None:
        from cosmos_platform import CREATE_NO_WINDOW
        env = dict(os.environ)
        env["PYTHONUTF8"] = "1"
        env["PYTHONIOENCODING"] = "utf-8"
        if self.env:
            env.update(self.env)
        flags = CREATE_NO_WINDOW if os.name == "nt" else 0
        try:
            self.proc = subprocess.Popen(
                self.argv,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.cwd,
                env=env,
                shell=False,
                bufsize=0,
                creationflags=flags,
            )
        except OSError as e:
            raise McpClientError("UNREACHABLE", f"spawn failed: {e}") from e
        self._alive = True
        threading.Thread(target=self._read_stdout, daemon=True).start()
        threading.Thread(target=self._read_stderr, daemon=True).start()

    def _read_stdout(self) -> None:
        proc = self.proc
        if proc is None or proc.stdout is None:
            return
        try:
            for raw in iter(proc.stdout.readline, b""):
                line = raw.decode("utf-8", "replace").strip()
                if not line:
                    continue
                try:
                    self._q.put(json.loads(line))
                except ValueError:
                    # sidecar log on stdout — not a protocol frame
                    self._stderr.append(line[:300])
        except (OSError, ValueError):
            pass

    def _read_stderr(self) -> None:
        proc = self.proc
        if proc is None or proc.stderr is None:
            return
        try:
            for raw in iter(proc.stderr.readline, b""):
                line = raw.decode("utf-8", "replace").strip()
                if line:
                    self._stderr.append(line[:300])
                    if len(self._stderr) > 80:
                        self._stderr = self._stderr[-40:]
        except (OSError, ValueError):
            pass

    def send(self, msg: dict) -> None:
        if self.proc is None or self.proc.stdin is None:
            raise McpClientError("UNREACHABLE", "Not connected")
        if self.proc.poll() is not None:
            raise McpClientError(
                "UNREACHABLE",
                f"child exited rc={self.proc.returncode} err={self.stderr_tail()}")
        data = (json.dumps(msg, ensure_ascii=False) + "\n").encode("utf-8")
        try:
            self.proc.stdin.write(data)
            self.proc.stdin.flush()
        except OSError as e:
            raise McpClientError("UNREACHABLE", f"stdin write failed: {e}") from e

    def recv(self, timeout_s: float | None = None) -> dict:
        wait = self.timeout_s if timeout_s is None else float(timeout_s)
        try:
            msg = self._q.get(timeout=wait)
        except queue.Empty:
            if self.proc is not None and self.proc.poll() is not None:
                raise McpClientError(
                    "UNREACHABLE",
                    f"TIMEOUT then child exited rc={self.proc.returncode} "
                    f"err={self.stderr_tail()}")
            raise McpClientError(
                "UNREACHABLE",
                f"TIMEOUT waiting {wait}s for JSON-RPC err={self.stderr_tail()}")
        if not isinstance(msg, dict):
            raise McpClientError("BROKE", f"non-object frame: {type(msg).__name__}")
        return msg

    def stderr_tail(self) -> str:
        return " | ".join(self._stderr[-4:])[:400]

    def close(self) -> None:
        if not self._alive and self.proc is None:
            return
        self._alive = False
        proc = self.proc
        if proc is None:
            return
        try:
            if proc.stdin:
                proc.stdin.close()
        except OSError:
            pass
        if proc.poll() is None:
            self.kill_result = tree_kill(proc.pid)
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.kill_result = (self.kill_result or "") + " | KILL_INCOMPLETE"
        try:
            if proc.stdout:
                proc.stdout.close()
            if proc.stderr:
                proc.stderr.close()
        except OSError:
            pass


class FakeTransport:
    """In-process JSON-RPC. Tests only. handler(msg) -> response or None."""

    def __init__(self, handler):
        self.handler = handler
        self._q: queue.Queue = queue.Queue()
        self.pid = None
        self.kill_result = None
        self.argv = ["fake"]
        self._closed = False

    def start(self) -> None:
        pass

    def send(self, msg: dict) -> None:
        if self._closed:
            raise McpClientError("UNREACHABLE", "fake transport closed")
        resp = self.handler(msg)
        if resp is not None:
            self._q.put(resp)

    def recv(self, timeout_s: float | None = None) -> dict:
        wait = 1.0 if timeout_s is None else float(timeout_s)
        try:
            return self._q.get(timeout=wait)
        except queue.Empty:
            raise McpClientError("UNREACHABLE", "TIMEOUT fake transport")

    def stderr_tail(self) -> str:
        return ""

    def close(self) -> None:
        self._closed = True


class McpClient:
    """initialize → notifications/initialized → tools/list | tools/call."""

    def __init__(self, argv: list[str] | None = None, *,
                 transport=None, timeout_s: float = 30,
                 allowlist: frozenset | set | None = None,
                 denylist: frozenset | set | None = None,
                 env: dict | None = None, cwd: str | Path | None = None,
                 client_name: str = CLIENT_NAME):
        if transport is None and not argv:
            raise McpClientError("BAD_SPEC", "argv or transport required")
        self.argv = list(argv) if argv else []
        self.timeout_s = float(timeout_s)
        self.allowlist = None if allowlist is None else frozenset(allowlist)
        self.denylist = frozenset(denylist) if denylist is not None else DEFAULT_DENY
        self.env = env
        self.cwd = cwd
        self.client_name = client_name
        self._transport = transport
        self._id = 0
        self._lock = threading.Lock()
        self.server_info: dict | None = None
        self.protocol_version: str | None = None
        self._started = False

    def _next_id(self) -> int:
        with self._lock:
            self._id += 1
            return self._id

    def _t(self):
        if self._transport is None:
            self._transport = StdioTransport(
                self.argv, env=self.env, cwd=self.cwd, timeout_s=self.timeout_s)
        return self._transport

    def start(self) -> dict:
        """Spawn (if needed) and initialize. Idempotent."""
        if self._started and self.server_info is not None:
            return self.server_info
        t = self._t()
        t.start()
        rid = self._next_id()
        t.send({
            "jsonrpc": "2.0",
            "id": rid,
            "method": "initialize",
            "params": {
                "protocolVersion": PROTOCOL,
                "capabilities": {},
                "clientInfo": {"name": self.client_name, "version": CLIENT_VERSION},
            },
        })
        msg = self._recv_id(rid)
        result = msg.get("result") if isinstance(msg.get("result"), dict) else {}
        self.server_info = result.get("serverInfo") or {}
        self.protocol_version = result.get("protocolVersion")
        t.send({
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {},
        })
        self._started = True
        return self.server_info

    def _recv_id(self, rid: int) -> dict:
        t = self._t()
        deadline = time.time() + self.timeout_s
        while True:
            remain = max(0.05, deadline - time.time())
            if remain <= 0.05 and time.time() >= deadline:
                raise McpClientError("UNREACHABLE", f"TIMEOUT waiting id={rid}")
            msg = t.recv(timeout_s=remain)
            if msg.get("id") == rid:
                if "error" in msg and msg["error"]:
                    err = msg["error"]
                    raise McpClientError(
                        "BROKE",
                        f"jsonrpc error id={rid}: {err}")
                return msg
            # skip notifications / unmatched (progress, logging)

    def tools_list(self) -> list[dict]:
        self.start()
        rid = self._next_id()
        self._t().send({
            "jsonrpc": "2.0", "id": rid, "method": "tools/list", "params": {},
        })
        msg = self._recv_id(rid)
        result = msg.get("result") if isinstance(msg.get("result"), dict) else {}
        tools = result.get("tools") or []
        if not isinstance(tools, list):
            raise McpClientError("BROKE", "tools/list did not return tools[]")
        return tools

    def tool_names(self) -> list[str]:
        names = []
        for t in self.tools_list():
            if isinstance(t, dict) and t.get("name"):
                names.append(str(t["name"]))
        return names

    def _assert_allowed(self, name: str) -> None:
        if name in self.denylist:
            raise McpClientError(
                "DENIED",
                f"tool {name!r} is client-denied (opt-in required; RCE-equivalent)")
        if self.allowlist is not None and name not in self.allowlist:
            raise McpClientError(
                "DENIED", f"tool {name!r} is not on this job's allowlist")

    def tools_call(self, name: str, arguments: dict | None = None) -> dict:
        self.start()
        self._assert_allowed(name)
        rid = self._next_id()
        self._t().send({
            "jsonrpc": "2.0",
            "id": rid,
            "method": "tools/call",
            "params": {"name": name, "arguments": arguments or {}},
        })
        msg = self._recv_id(rid)
        result = msg.get("result") if isinstance(msg.get("result"), dict) else {}
        return result

    def close(self) -> None:
        t = self._transport
        if t is not None:
            t.close()
        self._started = False

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *exc):
        self.close()
        return False


def _selftest() -> int:
    """Fake transport only. No child process, no network."""
    results = []

    def check(label, fn):
        try:
            results.append((label, bool(fn()), ""))
        except Exception as e:  # noqa: BLE001
            results.append((label, False, f"{type(e).__name__}: {e}"))

    tools = [
        {"name": "browser_navigate", "description": "nav"},
        {"name": "browser_snapshot", "description": "snap"},
        {"name": "browser_run_code_unsafe", "description": "rce"},
    ]

    def handler(msg):
        method = msg.get("method")
        rid = msg.get("id")
        if method == "initialize":
            return {"jsonrpc": "2.0", "id": rid, "result": {
                "protocolVersion": PROTOCOL,
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "Playwright", "version": "0.0.79"},
            }}
        if method == "notifications/initialized":
            return None
        if method == "tools/list":
            return {"jsonrpc": "2.0", "id": rid, "result": {"tools": tools}}
        if method == "tools/call":
            name = (msg.get("params") or {}).get("name")
            return {"jsonrpc": "2.0", "id": rid, "result": {
                "content": [{"type": "text", "text": f"called:{name}"}],
            }}
        return {"jsonrpc": "2.0", "id": rid, "error": {"code": -32601, "message": method}}

    c = McpClient(transport=FakeTransport(handler), timeout_s=2)
    info = c.start()
    check("initialize binds serverInfo.name",
          lambda: info.get("name") == "Playwright")
    names = c.tool_names()
    check("tools/list includes navigate and snapshot",
          lambda: "browser_navigate" in names and "browser_snapshot" in names)
    check("tools/list includes default-deny unsafe (server lists it)",
          lambda: "browser_run_code_unsafe" in names)
    called = c.tools_call("browser_navigate", {"url": "http://127.0.0.1/"})
    check("tools/call navigate is allowed",
          lambda: "called:browser_navigate" in str(called))
    denied = False
    kind = None
    try:
        c.tools_call("browser_run_code_unsafe", {"code": "1"})
    except McpClientError as e:
        denied = True
        kind = e.kind
    check("browser_run_code_unsafe is DENIED by client",
          lambda: denied and kind == "DENIED")
    c.close()

    allow = McpClient(
        transport=FakeTransport(handler), timeout_s=2,
        allowlist={"browser_snapshot"},
    )
    allow.start()
    off = False
    try:
        allow.tools_call("browser_navigate", {})
    except McpClientError as e:
        off = e.kind == "DENIED"
    check("allowlist refuses unlisted tools", lambda: off)
    allow.close()

    conv = convert_tool_format({
        "name": "read_file",
        "description": "read",
        "inputSchema": {
            "type": "object",
            "properties": {"path": {"type": "string"}},
            "required": ["path"],
        },
    })
    check("MCP tool converts to OpenAI function for OpenRouter",
          lambda: conv["type"] == "function"
          and conv["function"]["name"] == "read_file"
          and conv["function"]["parameters"]["required"] == ["path"])
    snap = named_servers()
    check("named MCP servers GET does not spawn; filesystem example refused",
          lambda: snap["does_not_spawn_filesystem"] is True
          and snap["cookbook"] == MCP_COOKBOOK
          and snap["n_cosmos_tools"] >= 1
          and any(t["function"]["name"] == "cosmos_status"
                  for t in snap["cosmos_openai_tools"])
          and any(s["id"] == "cosmos" and s["present"] for s in snap["servers"]))
    fs_refused = False
    try:
        npx_argv(["-y", FILESYSTEM_MCP, "/Applications"])
    except McpClientError as e:
        fs_refused = e.kind == "REFUSED"
    check("npx filesystem MCP is REFUSED (write_file on a grant is a hole)",
          lambda: fs_refused)

    argv = npx_argv(["-y", "@playwright/mcp@0.0.79", "--help"])
    check("npx argv is cmd.exe /c npx, not a string and not shell",
          lambda: (len(argv) >= 4
                   and argv[0].lower().endswith("cmd.exe")
                   and argv[1] == "/c"
                   and argv[2] == "npx"
                   and argv[3] == "-y"))
    check("npx argv refuses a string command",
          lambda: _raises_kind(lambda: npx_argv("npx --help"), "BAD_SPEC"))  # type: ignore[arg-type]

    bad = [(l, e) for l, ok, e in results if not ok]
    for label, ok, err in results:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (stdio MCP client; unsafe denied; npx argv)"
          % ("PASS" if not bad else "FAIL", len(results)))
    return 0 if not bad else 1


def _raises_kind(fn, kind: str) -> bool:
    try:
        fn()
    except McpClientError as e:
        return e.kind == kind
    return False


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(prog="cosmos_mcp_client")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    ap.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
