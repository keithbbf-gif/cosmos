#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_playwright_rail - satellite DOM rail `playwright-dom`.

Slice-1 of mesh additions. Cursor-shaped satellite. Does NOT edit
kernel / ledger / sched / service. attach_to_kernel refuses the authority
ledger unless boot_compose=True (BACKLOG).

kind=DOM. Route is core->interact (distinct dst from dump-dom READ).
policy_rank is 0 — do not outrank dump-dom on a shared route. dump-dom
stays the cheap READ; this rail is INTERACT (navigate / snapshot / optional
steps). Pin `@playwright/mcp@0.0.79`. `--browser chrome` (help values; not
chromium). `--headless --isolated`. No `--caps` on the default worker.
`browser_run_code_unsafe` is client-denied. No `--extension`. No Keith
daily profile. Gate URL is loopback HTTP, never file://.
Headed Chrome must not get `--no-sandbox` (infobar is Keith's click).
Spawn passes MCP `--sandbox` (that is the flag that drops it). Config-only
`chromiumSandbox` is overwritten by the CLI default.

Spawn prefers `node.exe` + pinned cli.js (no cmd parser). Fallback is
`cmd.exe /c npx -y @playwright/mcp@0.0.79 …` (measured necessary when
npm.ps1 is execution-policy blocked). Kill is taskkill /T, not Job-Object.

    py -3.14 cosmos\\cosmos_playwright_rail.py --selftest
    py -3.14 cosmos\\cosmos_playwright_rail.py --root V:\\A\\Ai\\COSMOS\\live --gate

Stage-6 proof is live/config/playwright_rail_probe.json quoting
tools/list names AND a snapshot containing this install's tree_id.
`--help` is not the gate.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import threading
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cosmos_mcp_client import (  # noqa: E402
    DEFAULT_DENY, FakeTransport, McpClient, McpClientError, npx_argv,
)

SCHEMA = "cosmos-playwright-rail/1"
WORKER = "cosmos-playwright-rail"
LINK_ID = "playwright-dom"
PINNED = "0.0.79"
NPM_SPEC = f"@playwright/mcp@{PINNED}"
SPEC_NAME = "playwright_rail.json"
PROBE_NAME = "playwright_rail_probe.json"
SRC = "core"
DST = "interact"
PROBE_TOOLS = ("browser_navigate", "browser_snapshot")
DEFAULT_ALLOW = frozenset({
    "browser_navigate", "browser_snapshot", "browser_navigate_back",
    "browser_click", "browser_type", "browser_fill_form", "browser_press_key",
    "browser_hover", "browser_select_option", "browser_wait_for",
    "browser_tabs", "browser_close", "browser_take_screenshot",
    "browser_resize", "browser_console_messages", "browser_handle_dialog",
    "browser_file_upload", "browser_drop", "browser_find",
    "browser_network_requests", "browser_network_request",
})
PROBE_TIMEOUT_S = 45
DISPATCH_TIMEOUT_S = 180


class PlaywrightRailError(RuntimeError):
    """kind in {BAD_SPEC, BAD_ROOT, UNREACHABLE, BROKE, DENIED, REFUSED}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def default_spec() -> dict:
    return {
        "schema": SCHEMA,
        "link_id": LINK_ID,
        "rail_type": "DOM",
        "src": SRC,
        "dst": DST,
        "policy_rank": 0,
        "metered_usd": 0.0,
        "budget_usd": 0.0,
        "package": NPM_SPEC,
        "browser": "chrome",
        "headless": True,
        "isolated": True,
        "chromium_sandbox": True,
        "timeout_s": DISPATCH_TIMEOUT_S,
        "probe_timeout_s": PROBE_TIMEOUT_S,
        "note": (
            "Playwright MCP 0.0.79 satellite. core->interact, not dump-dom READ. "
            "--browser chrome. No --caps. unsafe client-denied. Gate is loopback "
            "HTTP containing tree_id. Kernel attach BACKLOG."
        ),
    }


def _pin_origin(spec: dict) -> dict:
    spec["schema"] = SCHEMA
    spec["link_id"] = str(spec.get("link_id") or LINK_ID) or LINK_ID
    spec["rail_type"] = "DOM"
    spec["src"] = str(spec.get("src") or SRC) or SRC
    spec["dst"] = str(spec.get("dst") or DST) or DST
    if spec["dst"] in ("read", "models", "search"):
        spec["route_note"] = (
            f"coerced dst={spec['dst']!r} to {DST} (INTERACT; dump-dom stays READ)")
        spec["dst"] = DST
    pkg = str(spec.get("package") or NPM_SPEC)
    if pkg != NPM_SPEC:
        raise PlaywrightRailError(
            "BAD_SPEC", f"package {pkg!r} != pinned {NPM_SPEC!r}")
    spec["package"] = NPM_SPEC
    browser = str(spec.get("browser") or "chrome").lower()
    if browser == "chromium":
        browser = "chrome"
        spec["browser_note"] = "coerced chromium -> chrome (CLI help values)"
    if browser not in ("chrome", "firefox", "webkit", "msedge"):
        raise PlaywrightRailError(
            "BAD_SPEC",
            f"browser {browser!r} not in chrome|firefox|webkit|msedge")
    spec["browser"] = browser
    spec["metered_usd"] = float(spec.get("metered_usd") or 0.0)
    spec["budget_usd"] = float(spec.get("budget_usd") or 0.0)
    spec["policy_rank"] = int(spec.get("policy_rank") or 0)
    spec["timeout_s"] = int(spec.get("timeout_s") or DISPATCH_TIMEOUT_S)
    spec["probe_timeout_s"] = int(spec.get("probe_timeout_s") or PROBE_TIMEOUT_S)
    spec["headless"] = bool(spec.get("headless", True))
    spec["isolated"] = bool(spec.get("isolated", True))
    spec["chromium_sandbox"] = bool(spec.get("chromium_sandbox", True))
    return spec


def merge_spec(overlay) -> dict:
    spec = default_spec()
    if overlay is None:
        return _pin_origin(spec)
    if not isinstance(overlay, dict):
        raise PlaywrightRailError("BAD_SPEC", f"spec overlay is {type(overlay).__name__}")
    for k, v in overlay.items():
        spec[k] = v
    if spec.get("schema") != SCHEMA:
        raise PlaywrightRailError(
            "BAD_SPEC", f"spec schema {spec.get('schema')!r} != {SCHEMA}")
    if spec.get("rail_type") not in (None, "DOM"):
        raise PlaywrightRailError(
            "BAD_SPEC",
            f"playwright rail_type must be DOM (MCP is transport), got "
            f"{spec.get('rail_type')!r}")
    return _pin_origin(spec)


def load_spec(path: Path | None) -> dict:
    if path is None or not Path(path).exists():
        return default_spec()
    try:
        raw = Path(path).read_text(encoding="utf-8")
    except OSError as e:
        raise PlaywrightRailError("BAD_SPEC", f"unreadable spec {path}: {e}") from e
    try:
        overlay = json.loads(raw)
    except ValueError as e:
        raise PlaywrightRailError("BAD_SPEC", f"unparseable spec {path}: {e}") from e
    return merge_spec(overlay)


def write_spec(path: Path, spec: dict | None = None) -> dict:
    body = merge_spec(spec)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(body, indent=2, sort_keys=True,
                               ensure_ascii=False) + "\n",
                    encoding="utf-8")
    return body


def find_pinned_cli() -> Path | None:
    """Resolve @playwright/mcp@0.0.79 cli.js from the npx cache. No drive literal."""
    local = os.environ.get("LOCALAPPDATA")
    if not local:
        return None
    root = Path(local) / "npm-cache" / "_npx"
    if not root.is_dir():
        return None
    try:
        children = list(root.iterdir())
    except OSError:
        return None
    for child in children:
        pkg = child / "node_modules" / "@playwright" / "mcp" / "package.json"
        cli = pkg.with_name("cli.js")
        if not pkg.is_file() or not cli.is_file():
            continue
        try:
            data = json.loads(pkg.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if str(data.get("version")) == PINNED:
            return cli
    return None


def write_mcp_config(output_dir: Path, spec: dict) -> Path:
    """Playwright MCP `--sandbox` CLI is a no-op (true becomes undefined).
    Config launchOptions.chromiumSandbox is the flag that actually stops
    Chrome's `--no-sandbox` infobar on a headed COSMOS window."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "playwright_mcp.launch.json"
    body = {
        "browser": {
            "launchOptions": {
                "chromiumSandbox": bool(spec.get("chromium_sandbox", True)),
            }
        }
    }
    # GEM DOM everyday search: COSMOS Chrome profile (not Keith daily, not
    # --isolated blank). Playwright MCP hands: userDataDir. DHx SEARCH=GEM DOM.
    udd = spec.get("user_data_dir") or spec.get("userDataDir")
    if udd:
        body["browser"]["userDataDir"] = str(udd)
    path.write_text(json.dumps(body, indent=2) + "\n", encoding="utf-8")
    return path


def spawn_argv(spec: dict, output_dir: Path) -> list[str]:
    """Pin 0.0.79. Prefer node.exe+cli.js; else cmd.exe /c npx (no shell=True)."""
    flags = []
    if spec.get("headless", True):
        flags.append("--headless")
    if spec.get("isolated", True):
        flags.append("--isolated")
    udd = spec.get("user_data_dir") or spec.get("userDataDir")
    if udd:
        flags.extend(["--user-data-dir", str(udd)])
    cfg = write_mcp_config(output_dir, spec)
    # MCP `--sandbox` is required. Config chromiumSandbox is overwritten by
    # Commander's default sandbox=false unless this flag is present. Without
    # it, headed Chrome gets `--no-sandbox` and Keith has to click the infobar.
    if spec.get("chromium_sandbox", True):
        flags.append("--sandbox")
    else:
        flags.append("--no-sandbox")
    flags.extend([
        "--browser", str(spec.get("browser") or "chrome"),
        "--output-dir", str(output_dir),
        "--image-responses", "omit",
        "--console-level", "error",
        "--config", str(cfg),
    ])
    node = shutil.which("node")
    cli = find_pinned_cli()
    if node and cli is not None:
        exe = None
        try:
            from cosmos_browser import discover_browser
            exe = discover_browser()
        except Exception:  # noqa: BLE001
            exe = None
        extra = []
        if exe:
            extra.extend(["--executable-path", exe])
        return [node, str(cli), *flags, *extra]
    return npx_argv(["-y", NPM_SPEC, *flags])


def _text_of(result: dict) -> str:
    parts = []
    content = result.get("content") if isinstance(result, dict) else None
    if isinstance(content, list):
        for block in content:
            if isinstance(block, dict):
                t = block.get("text")
                if t:
                    parts.append(str(t))
    if not parts and isinstance(result, dict):
        parts.append(json.dumps(result)[:4000])
    return "\n".join(parts)


class PlaywrightRail:
    """Dispatcher adapter. kind=DOM. probe() is tools/list (no navigate).
    dispatch() is navigate then snapshot; steps optional. Isolated --gate
    Dispatcher, not the live daemon.
    """
    kind = "DOM"

    def __init__(self, spec: dict | None = None, *, output_dir: Path | None = None,
                 client_factory=None, timeout_s: float | None = None):
        self.spec = merge_spec(spec)
        self.metered_usd = float(self.spec.get("metered_usd") or 0.0)
        self.link_id = self.spec["link_id"]
        self.output_dir = Path(output_dir) if output_dir is not None else Path(".")
        self._client_factory = client_factory
        self._timeout = float(timeout_s or self.spec.get("timeout_s") or DISPATCH_TIMEOUT_S)
        self._last = None
        self._client = None

    def last_identity(self):
        return self._last

    def _make_client(self, timeout_s: float) -> McpClient:
        if self._client_factory is not None:
            return self._client_factory()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        argv = spawn_argv(self.spec, self.output_dir)
        return McpClient(
            argv,
            timeout_s=timeout_s,
            allowlist=DEFAULT_ALLOW,
            denylist=DEFAULT_DENY,
            cwd=str(self.output_dir),
            client_name=WORKER,
        )

    def _ensure(self, timeout_s: float | None = None) -> McpClient:
        if self._client is not None:
            return self._client
        self._client = self._make_client(timeout_s or self._timeout)
        return self._client

    def close(self) -> None:
        c = self._client
        self._client = None
        if c is not None:
            try:
                c.close()
            except Exception:  # noqa: BLE001
                pass

    def probe(self):
        """Cheapest liveness: tools/list contains navigate AND snapshot.
        Does not browser_navigate (first navigate may download a browser).
        """
        tmo = float(self.spec.get("probe_timeout_s") or PROBE_TIMEOUT_S)
        try:
            client = self._ensure(tmo)
            client.timeout_s = tmo
            names = client.tool_names()
            info = client.server_info or {}
        except McpClientError as e:
            self._last = {"ok": False, "kind": e.kind, "detail": str(e)}
            return False, f"{e.kind}: {e}"
        except Exception as e:  # noqa: BLE001
            self._last = {"ok": False, "kind": "UNREACHABLE",
                          "detail": f"{type(e).__name__}: {e}"}
            return False, f"UNREACHABLE: probe raised {type(e).__name__}: {e}"
        missing = [n for n in PROBE_TOOLS if n not in names]
        self._last = {
            "ok": not missing,
            "tool_names": names,
            "tool_count": len(names),
            "serverInfo": info,
            "protocolVersion": getattr(client, "protocol_version", None),
            "unsafe_listed": "browser_run_code_unsafe" in names,
            "spawn": getattr(getattr(client, "_transport", None), "argv", None),
        }
        if missing:
            return False, (
                f"BROKE tools/list missing {missing} "
                f"(have {len(names)}: {','.join(names[:8])})")
        return True, (
            f"playwright-dom tools/list n={len(names)} "
            f"navigate+snapshot present server={info.get('name')} "
            f"version={info.get('version')}")

    def dispatch(self, payload: dict) -> dict:
        payload = payload or {}
        url = payload.get("url")
        if not url:
            return {"ok": False, "kind": "BROKE",
                    "detail": "dispatch payload.url is required", "node": self.link_id}
        if str(url).lower().startswith("file:"):
            return {"ok": False, "kind": "BROKE",
                    "detail": "file:// refused (server blocks it; gate is loopback HTTP)",
                    "node": self.link_id}
        tmo = float(payload.get("timeout_s") or self._timeout)
        try:
            client = self._ensure(tmo)
            client.timeout_s = tmo
            nav = client.tools_call("browser_navigate", {"url": str(url)})
            steps = payload.get("steps") or []
            step_out = []
            if isinstance(steps, list):
                for step in steps:
                    if not isinstance(step, dict):
                        continue
                    tool = step.get("tool") or step.get("name")
                    args = step.get("arguments") or step.get("args") or {}
                    if not tool:
                        continue
                    if str(tool) in DEFAULT_DENY:
                        raise McpClientError(
                            "DENIED",
                            f"tool {tool!r} is client-denied "
                            "(opt-in required; RCE-equivalent)")
                    step_out.append({
                        "tool": tool,
                        "result_head": _text_of(client.tools_call(str(tool), args))[:400],
                    })
            snap = client.tools_call("browser_snapshot", {})
            text = _text_of(snap)
        except McpClientError as e:
            return {"ok": False, "kind": e.kind, "detail": str(e),
                    "node": self.link_id}
        except Exception as e:  # noqa: BLE001
            return {"ok": False, "kind": "UNREACHABLE",
                    "detail": f"{type(e).__name__}: {e}", "node": self.link_id}
        rec = {
            "ok": True, "kind": "DOM", "node": self.link_id,
            "url": url, "text": text[:8000],
            "navigate_head": _text_of(nav)[:400],
            "steps": step_out, "usd": 0.0,
        }
        expect = payload.get("expect")
        if expect and expect not in text:
            rec["ok"] = False
            rec["kind"] = "BROKE"
            rec["detail"] = f"snapshot missing expect={expect!r}"
        return rec

    def run_locator(self, op: str, args: dict | None = None) -> dict:
        """One locator-shaped step on THIS composed client. No second DOM.

        Stagehand act() calls this when playwright-dom is already composed.
        Does not mkdir. Page text is UNTRUSTED.
        """
        args = dict(args or {})
        name = str(op or "").strip().lower()
        tool = {
            "click": "browser_click",
            "goto": "browser_navigate",
            "navigate": "browser_navigate",
            "type": "browser_type",
            "fill": "browser_fill_form",
            "press": "browser_press_key",
        }.get(name)
        if tool is None and str(name).startswith("browser_"):
            tool = name
        if not tool:
            return {"ok": False, "kind": "BROKE",
                    "detail": f"unknown locator op {op!r}",
                    "node": self.link_id, "text_trust": "UNTRUSTED",
                    "dom_is_untrusted": True}
        if tool == "browser_run_code_unsafe" or tool in DEFAULT_DENY:
            return {"ok": False, "kind": "DENIED",
                    "detail": "unsafe tool denied",
                    "node": self.link_id, "tool": tool,
                    "text_trust": "UNTRUSTED", "dom_is_untrusted": True}
        url = str(args.get("url") or "")
        if tool == "browser_navigate":
            low = url.lower()
            if low.startswith("file:"):
                return {"ok": False, "kind": "BROKE",
                        "detail": "file:// refused (gate is loopback HTTP)",
                        "node": self.link_id, "tool": tool,
                        "text_trust": "UNTRUSTED", "dom_is_untrusted": True}
            if low.startswith("javascript:"):
                return {"ok": False, "kind": "DENIED",
                        "detail": "javascript: refused",
                        "node": self.link_id, "tool": tool,
                        "text_trust": "UNTRUSTED", "dom_is_untrusted": True}
        try:
            client = self._ensure(self._timeout)
            out = client.tools_call(tool, args)
            text = _text_of(out)
        except McpClientError as e:
            return {"ok": False, "kind": e.kind, "detail": str(e),
                    "node": self.link_id, "tool": tool,
                    "text_trust": "UNTRUSTED", "dom_is_untrusted": True}
        except Exception as e:  # noqa: BLE001
            return {"ok": False, "kind": "UNREACHABLE",
                    "detail": f"{type(e).__name__}: {e}",
                    "node": self.link_id, "tool": tool,
                    "text_trust": "UNTRUSTED", "dom_is_untrusted": True}
        return {
            "ok": True, "kind": "DOM", "node": self.link_id,
            "op": name, "tool": tool,
            "text": text[:8000],
            "text_trust": "UNTRUSTED",
            "dom_is_untrusted": True,
            "usd": 0.0,
        }


def spec_path_for(paths) -> Path:
    return paths.config(SPEC_NAME)


def probe_path_for(paths) -> Path:
    return paths.config(PROBE_NAME)


def register_playwright_rail(registry, adapters: dict, spend_gate=None,
                             src: str | None = None, dst: str | None = None, *,
                             paths=None, spec=None, output_dir=None,
                             client_factory=None) -> dict:
    if spec is None and paths is not None:
        spec = load_spec(spec_path_for(paths))
    else:
        spec = merge_spec(spec)
    spec = dict(spec)
    if src:
        spec["src"] = src
    if dst:
        spec["dst"] = dst
    spec = _pin_origin(spec)
    if output_dir is None and paths is not None:
        output_dir = paths.role("work", "playwright_rail")
    rail = PlaywrightRail(spec, output_dir=output_dir,
                          client_factory=client_factory)
    lid = rail.link_id
    if lid not in registry.state():
        registry.register(lid, spec["rail_type"], spec["src"], spec["dst"],
                          policy_rank=int(spec["policy_rank"]))
    registry.attach_probe(lid, rail.probe)
    adapters[lid] = rail
    return {
        "link_id": lid,
        "rail": rail,
        "spec": spec,
        "src": spec["src"],
        "dst": spec["dst"],
        "output_dir": str(output_dir) if output_dir is not None else None,
    }


# Moved to cosmos_rail_base (Phase 3.1, 2026-08-30/31): four rails carried a
# byte-identical `_ledger_is_authority`, and four carried a near-identical
# `write_probe_record`. This rail's copy redacted NOTHING -- it is a DOM rail
# with no key, so nothing leaked, but the divergence is exactly the drift the
# seam exists to stop. The base pops the union of every rail's secret names.
from cosmos_rail_base import (  # noqa: E402,F401
    _ledger_is_authority,
    write_probe_record,
)


def attach_to_kernel(kernel, adapters: dict | None = None,
                     client_factory=None, *, boot_compose: bool = False) -> dict:
    if _ledger_is_authority(kernel) and not boot_compose:
        raise PlaywrightRailError(
            "REFUSED",
            "attach_to_kernel refuses authority LINK_REGISTERED until Kernel "
            "boot reattaches probes every boot (BACKLOG). Isolated --gate "
            "ledger only. Pass boot_compose=True only from Kernel.__init__.")
    if adapters is None:
        adapters = getattr(kernel, "adapters", None)
        if adapters is None:
            adapters = {}
            kernel.adapters = adapters
    out_dir = None
    paths = getattr(kernel, "paths", None)
    if paths is not None:
        out_dir = paths.role("work", "playwright_rail")
    return register_playwright_rail(
        kernel.registry, adapters, spend_gate=getattr(kernel, "spend", None),
        paths=paths, output_dir=out_dir, client_factory=client_factory)


def refuse_live_authority_attach(paths) -> dict:
    auth = paths.ledger("authority.jsonl")
    duck = type("KernelView", (), {})()
    duck.paths = paths
    duck.ledger = type("Led", (), {"_path": auth})()
    duck.registry = None
    duck.spend = None
    rec = {
        "authority_ledger": str(auth),
        "authority_exists": Path(auth).exists(),
        "tree_id": paths.sentinel.tree_id,
        "refused": False,
        "kind": None,
        "detail": None,
        "boot_compose_required": True,
        "kernel_attach": "BACKLOG",
    }
    try:
        attach_to_kernel(duck, {})
        rec["detail"] = "attach_to_kernel DID NOT refuse the authority ledger"
    except PlaywrightRailError as e:
        rec["refused"] = e.kind == "REFUSED"
        rec["kind"] = e.kind
        rec["detail"] = str(e)
    return rec


def inspect_live_kernel(root) -> dict:
    out = {"opened": False, "playwright_in_registry": None, "error": None}
    try:
        from cosmos_kernel import Kernel
        k = Kernel(root, worker="playwright-rail-gate", read_only=True)
        out["opened"] = True
        out["tree_id"] = k.paths.sentinel.tree_id
        out["playwright_in_registry"] = LINK_ID in k.registry.state()
        out["read_only"] = True
    except Exception as e:  # noqa: BLE001
        out["error"] = f"{type(e).__name__}: {e}"
    return out


def _iso_now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


class _GateHTTP:
    """Loopback page that bakes the live sentinel tree_id. Never file://."""

    def __init__(self, tree_id: str):
        self.tree_id = tree_id
        marker = f"tree_id={tree_id}"
        self.html = (
            "<!doctype html><html><head><meta charset='utf-8'>"
            "<title>COSMOS meshadditions gate</title></head><body>"
            "<h1>COSMOS mesh additions stage-6 gate</h1>"
            f"<p id='tree'>{marker}</p>"
            "<p>satellite playwright-dom snapshot target</p>"
            "</body></html>"
        )
        self.httpd = None
        self.thread = None
        self.url = None

    def start(self) -> str:
        html = self.html

        class H(BaseHTTPRequestHandler):
            def do_GET(self):  # noqa: N802
                body = html.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, fmt, *args):
                return

        httpd = ThreadingHTTPServer(("127.0.0.1", 0), H)
        self.httpd = httpd
        self.thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        self.thread.start()
        host, port = httpd.server_address[:2]
        self.url = f"http://{host}:{port}/"
        return self.url

    def stop(self) -> None:
        if self.httpd is not None:
            try:
                self.httpd.shutdown()
            except Exception:  # noqa: BLE001
                pass
            try:
                self.httpd.server_close()
            except Exception:  # noqa: BLE001
                pass


def _compose_isolated(paths, spec, client_factory):
    """Isolated --gate Dispatcher (cosmos_rails.Dispatcher), not the live daemon."""
    from cosmos_ledger import Ledger
    from cosmos_registry import Registry
    from cosmos_rails import Dispatcher
    from cosmos_spend import SpendGate

    adapters = {}
    gate_dir = paths.role("state", "playwright_rail")
    gate_dir.mkdir(parents=True, exist_ok=True)
    out_dir = paths.role("work", "playwright_rail")
    out_dir.mkdir(parents=True, exist_ok=True)
    led = Ledger(gate_dir / "gate.jsonl", b"playwright-rail-gate", WORKER)
    reg = Registry(led)
    spend = SpendGate(led)
    attached = register_playwright_rail(
        reg, adapters, spend_gate=spend, spec=spec,
        output_dir=out_dir, client_factory=client_factory)
    disp = Dispatcher(reg, adapters, led, spend=spend)
    return attached, adapters, disp, led, gate_dir


def gate(root: str | os.PathLike, *, client_factory=None) -> dict:
    """Runtime-binding gate. Isolated ledger. Live Playwright MCP unless injected.

    PASS iff tools/list has navigate+snapshot AND snapshot contains
    tree_id=<sentinel> AND attach refused AND kernel_attached is false.
    """
    from cosmos_paths import CosmosPaths

    paths = CosmosPaths(root)
    spec = load_spec(spec_path_for(paths))
    write_spec(spec_path_for(paths), spec)
    page = _GateHTTP(paths.sentinel.tree_id)
    url = page.start()
    attached = adapters = disp = led = gate_dir = None
    rec = {
        "schema": SCHEMA,
        "worker": WORKER,
        "gated_at": _iso_now(),
        "root": str(paths.root),
        "tree_id": paths.sentinel.tree_id,
        "link_id": LINK_ID,
        "spec_path": str(spec_path_for(paths)),
        "gate_url": url,
        "file_url": False,
        "dispatcher_constructed": False,
        "authority_ledger_written": False,
        "kernel_attached": False,
        "live_value": None,
        "gate": "FAIL",
        "stage6": {
            "kind": "satellite",
            "kernel_attach": "BACKLOG",
            "predicate": (
                "tools/list has browser_navigate AND browser_snapshot AND "
                "snapshot contains tree_id=<sentinel> via http://127.0.0.1 "
                "AND attach refused on authority"
            ),
        },
    }
    try:
        attached, adapters, disp, led, gate_dir = _compose_isolated(
            paths, spec, client_factory)
        rec["route"] = f"{attached['src']}->{attached['dst']}"
        rec["dispatcher_constructed"] = True
        rec["dispatcher_class"] = type(disp).__name__
        rail = adapters[attached["link_id"]]
        try:
            measured = disp.registry.probe(attached["link_id"])
        except Exception as e:  # noqa: BLE001
            measured = {"ok": False, "detail": f"{type(e).__name__}: {e}"}
        ident = rail.last_identity() or {}
        rec["probe_ok"] = bool((measured or {}).get("ok"))
        rec["probe_detail"] = (measured or {}).get("detail")
        rec["tool_names"] = ident.get("tool_names")
        rec["tool_count"] = ident.get("tool_count")
        rec["serverInfo"] = ident.get("serverInfo")
        rec["unsafe_listed"] = ident.get("unsafe_listed")
        marker = f"tree_id={paths.sentinel.tree_id}"
        dispatched = None
        if rec["probe_ok"]:
            dispatched = rail.dispatch({
                "url": url, "expect": marker,
                "timeout_s": spec.get("timeout_s") or DISPATCH_TIMEOUT_S,
            })
        rec["dispatch_ok"] = bool((dispatched or {}).get("ok"))
        rec["dispatch_detail"] = (dispatched or {}).get("detail")
        rec["dispatch_kind"] = (dispatched or {}).get("kind")
        snap = (dispatched or {}).get("text") or ""
        rec["snapshot_head"] = snap[:1200]
        rec["snapshot_has_tree_id"] = marker in snap
        rec["live_value"] = {
            "tool_names": ident.get("tool_names"),
            "tool_count": ident.get("tool_count"),
            "server": (ident.get("serverInfo") or {}).get("name"),
            "server_version": (ident.get("serverInfo") or {}).get("version"),
            "gate_url": url,
            "tree_id": paths.sentinel.tree_id,
            "snapshot_has_tree_id": rec["snapshot_has_tree_id"],
        }
        events = []
        try:
            events = [e.get("event") for e in led.verify()]
        except Exception as e:  # noqa: BLE001
            rec["ledger_error"] = f"{type(e).__name__}: {e}"
        rec["isolated_ledger_events"] = events
        rec["isolated_ledger"] = str(gate_dir / "gate.jsonl")
        rec["matrix"] = disp.registry.matrix()
        rail.close()
    except Exception as e:  # noqa: BLE001
        rec["probe_ok"] = False
        rec["probe_detail"] = f"{type(e).__name__}: {e}"
    finally:
        page.stop()
        if adapters:
            for ad in adapters.values():
                close = getattr(ad, "close", None)
                if close:
                    try:
                        close()
                    except Exception:  # noqa: BLE001
                        pass

    rec["attach_refusal"] = refuse_live_authority_attach(paths)
    rec["live_kernel"] = inspect_live_kernel(root)
    names = rec.get("tool_names") or []
    tools_ok = all(n in names for n in PROBE_TOOLS)
    snap_ok = bool(rec.get("snapshot_has_tree_id"))
    route_ok = rec.get("route") == f"{SRC}->{DST}"
    attach_refused = bool(rec["attach_refusal"].get("refused"))
    rec["identity_ok"] = tools_ok and snap_ok
    rec["identity_why"] = (
        "ok" if rec["identity_ok"]
        else f"tools_ok={tools_ok} snapshot_has_tree_id={snap_ok}"
    )
    if (rec.get("probe_ok") and rec.get("dispatch_ok") and tools_ok and snap_ok
            and route_ok and attach_refused
            and not rec["authority_ledger_written"]
            and rec["kernel_attached"] is False):
        rec["gate"] = "PASS"
    rec["proof"] = (
        f"playwright-dom probe_ok={rec.get('probe_ok')} "
        f"tools={rec.get('tool_count')} "
        f"snapshot_has_tree_id={rec.get('snapshot_has_tree_id')} "
        f"tree_id={rec['tree_id']} url={rec.get('gate_url')} "
        f"route={rec.get('route')} attach_refused={attach_refused} "
        f"kernel_attached={rec['kernel_attached']}"
    )
    probe_path = probe_path_for(paths)
    written = write_probe_record(probe_path, rec)
    written["probe_path"] = str(probe_path)
    if gate_dir is not None:
        gate_json = gate_dir / "gate.json"
        write_probe_record(gate_json, written)
        written["gate_json"] = str(gate_json)
    return written


def _fake_factory(tree_id: str, *, with_unsafe: bool = True):
    tools = [
        {"name": "browser_navigate"},
        {"name": "browser_snapshot"},
        {"name": "browser_click"},
    ]
    if with_unsafe:
        tools.append({"name": "browser_run_code_unsafe"})
    marker = f"tree_id={tree_id}"
    state = {"url": None}

    def handler(msg):
        method = msg.get("method")
        rid = msg.get("id")
        if method == "initialize":
            return {"jsonrpc": "2.0", "id": rid, "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "Playwright", "version": "0.0.79"},
            }}
        if method == "notifications/initialized":
            return None
        if method == "tools/list":
            return {"jsonrpc": "2.0", "id": rid, "result": {"tools": tools}}
        if method == "tools/call":
            name = (msg.get("params") or {}).get("name")
            args = (msg.get("params") or {}).get("arguments") or {}
            if name == "browser_navigate":
                state["url"] = args.get("url")
                return {"jsonrpc": "2.0", "id": rid, "result": {
                    "content": [{"type": "text", "text": f"navigated {state['url']}"}],
                }}
            if name == "browser_snapshot":
                return {"jsonrpc": "2.0", "id": rid, "result": {
                    "content": [{"type": "text", "text": (
                        f"- heading: COSMOS mesh additions stage-6 gate\n"
                        f"- paragraph: {marker}\n"
                    )}],
                }}
            return {"jsonrpc": "2.0", "id": rid, "result": {
                "content": [{"type": "text", "text": f"called:{name}"}],
            }}
        return {"jsonrpc": "2.0", "id": rid, "error": {"code": -32601}}

    def factory():
        return McpClient(
            transport=FakeTransport(handler),
            timeout_s=2,
            allowlist=DEFAULT_ALLOW,
            denylist=DEFAULT_DENY,
        )
    return factory


def _selftest() -> int:
    import tempfile
    from cosmos_kernel import install, Kernel
    from cosmos_ledger import Ledger
    from cosmos_registry import Registry
    from cosmos_rails import Dispatcher
    from cosmos_spend import SpendGate

    results = []

    def check(label, fn):
        try:
            results.append((label, bool(fn()), ""))
        except Exception as e:  # noqa: BLE001
            results.append((label, False, f"{type(e).__name__}: {e}"))

    td = Path(tempfile.mkdtemp(prefix="cosmos_playwright_rail_"))
    root = install(td / "live", tree_id="spike-playwright-rail")
    from cosmos_paths import CosmosPaths
    paths = CosmosPaths(root)
    spec = write_spec(paths.config(SPEC_NAME))
    factory = _fake_factory(paths.sentinel.tree_id)
    rail = PlaywrightRail(spec, output_dir=td / "pw", client_factory=factory)
    ok, detail = rail.probe()
    check("probe tools/list has navigate+snapshot",
          lambda: ok and "navigate+snapshot present" in detail)
    ident = rail.last_identity() or {}
    check("unsafe is listed by server (client still denies call)",
          lambda: ident.get("unsafe_listed") is True)
    denied = False
    try:
        rail._ensure().tools_call("browser_run_code_unsafe", {"code": "1"})
    except McpClientError as e:
        denied = e.kind == "DENIED"
    check("dispatch path DENIED unsafe", lambda: denied)
    unsafe_step = rail.dispatch({
        "url": "http://127.0.0.1:9/",
        "steps": [{"tool": "browser_run_code_unsafe", "args": {"code": "1"}}],
    })
    check("dispatch DENIED unsafe step (does not skip)",
          lambda: (not unsafe_step["ok"]) and unsafe_step["kind"] == "DENIED")

    file_d = rail.dispatch({"url": "file:///C:/nope.html"})
    check("file:// dispatch is BROKE",
          lambda: (not file_d["ok"]) and file_d["kind"] == "BROKE")

    nav = rail.dispatch({
        "url": "http://127.0.0.1:9/",
        "expect": f"tree_id={paths.sentinel.tree_id}",
    })
    check("fake snapshot contains tree_id",
          lambda: nav["ok"] and f"tree_id={paths.sentinel.tree_id}" in nav["text"])
    rail.close()

    argv = spawn_argv(spec, td / "pw")
    check("spawn argv is a list, never a string",
          lambda: isinstance(argv, list) and all(isinstance(a, str) for a in argv))
    check("spawn pins 0.0.79 or resolved cli.js",
          lambda: any(PINNED in a or a.endswith("cli.js") for a in argv))
    check("spawn uses chrome not chromium",
          lambda: "chrome" in argv and "chromium" not in argv)
    check("no --caps on default worker",
          lambda: "--caps" not in argv)
    check("spawn writes --config chromiumSandbox (not --sandbox CLI no-op)",
          lambda: ("--config" in argv
                   and json.loads(Path(argv[argv.index("--config")+1]).read_text(
                       encoding="utf-8"))
                   ["browser"]["launchOptions"]["chromiumSandbox"] is True))
    check("spawn passes --sandbox so headed Chrome has no --no-sandbox infobar",
          lambda: "--sandbox" in argv and "--no-sandbox" not in argv)

    coerced = merge_spec({
        "schema": SCHEMA, "rail_type": "DOM", "link_id": LINK_ID,
        "browser": "chromium", "dst": "read",
    })
    check("chromium coerced to chrome; dst=read coerced to interact",
          lambda: coerced["browser"] == "chrome" and coerced["dst"] == DST)

    led = Ledger(td / "n.jsonl", b"k", "core")
    reg = Registry(led)
    adapters = {}
    rec = register_playwright_rail(
        reg, adapters, spend_gate=SpendGate(led), spec=spec,
        output_dir=td / "pw2", client_factory=factory)
    check("register kind=DOM core->interact",
          lambda: rec["spec"]["rail_type"] == "DOM" and rec["dst"] == DST)
    reg.probe_all()
    disp = Dispatcher(reg, adapters, led, spend=SpendGate(led))
    routed = disp.dispatch(SRC, DST, {
        "url": "http://127.0.0.1:9/",
        "expect": f"tree_id={paths.sentinel.tree_id}",
    })
    check("isolated Dispatcher reaches playwright-dom",
          lambda: routed["ok"] and routed["kind"] == "DOM")
    for ad in adapters.values():
        ad.close()

    g = gate(root, client_factory=_fake_factory(paths.sentinel.tree_id))
    check("gate PASS on fake MCP + loopback page",
          lambda: g["gate"] == "PASS" and g["snapshot_has_tree_id"] is True)
    check("gate URL is http://127.0.0.1 not file://",
          lambda: str(g.get("gate_url") or "").startswith("http://127.0.0.1")
          and g.get("file_url") is False)
    check("gate kernel_attached is false",
          lambda: g["kernel_attached"] is False)
    check("gate attach refused",
          lambda: g["attach_refusal"]["refused"] is True)
    check("gate does not write authority",
          lambda: g["authority_ledger_written"] is False)

    k = Kernel(root, worker="playwright-rail-selftest")
    # Boot legitimately composes this rail (Kernel.rails_compose passes
    # boot_compose=True), so "the link is absent" stopped being true and this
    # check went red without the guard ever weakening. The property that matters
    # is that the REFUSED attach registered nothing NEW -- compare the registry
    # across the refusal instead of assuming it starts empty. (2026-08-30)
    _before = set(k.registry.state())
    refused = False
    try:
        attach_to_kernel(k, {})
    except PlaywrightRailError as e:
        refused = e.kind == "REFUSED"
    check("attach_to_kernel refuses writing Kernel without boot_compose",
          lambda: refused and set(k.registry.state()) == _before)

    bad = [(l, e) for l, ok, e in results if not ok]
    for label, ok, err in results:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (playwright-dom satellite; tools/list probe; "
          "unsafe denied; file:// refused; attach refused)"
          % ("PASS" if not bad else "FAIL", len(results)))
    return 0 if not bad else 1


def main() -> int:
    ap = argparse.ArgumentParser(
        prog="cosmos_playwright_rail",
        description="COSMOS Playwright MCP DOM rail. --gate is the "
                    "runtime-binding proof. Isolated --gate Dispatcher, not "
                    "the live daemon. --help of the npm package is not the gate.")
    ap.add_argument("--root", default=None)
    ap.add_argument("--gate", action="store_true")
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if a.gate or a.probe:
        if not a.root:
            print(json.dumps({
                "ok": False, "kind": "BAD_ROOT",
                "error": "--root is required (resolver does not guess)",
            }, indent=1))
            return 2
        if a.probe and not a.gate:
            from cosmos_paths import CosmosPaths
            paths = CosmosPaths(a.root)
            spec = load_spec(spec_path_for(paths))
            out = paths.role("work", "playwright_rail")
            rail = PlaywrightRail(spec, output_dir=out)
            try:
                ok, detail = rail.probe()
                ident = rail.last_identity() or {}
                rec = {"ok": ok, "detail": detail, "link_id": rail.link_id,
                       "tool_names": ident.get("tool_names"),
                       "tool_count": ident.get("tool_count"),
                       "serverInfo": ident.get("serverInfo")}
                print(json.dumps(rec, indent=1, default=str))
                return 0 if ok else 2
            finally:
                rail.close()
        rec = gate(a.root)
        print(json.dumps(rec, indent=1, default=str, ensure_ascii=False))
        return 0 if rec.get("gate") == "PASS" else 2
    ap.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
