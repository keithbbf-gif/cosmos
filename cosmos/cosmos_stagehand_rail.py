#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_stagehand_rail - preferred-rail DOM adapter UNDER playwright-dom.

SGH steal: Stagehand (Browserbase) act / extract / observe, schema-validated
page projections, action caching, DOM-is-untrusted. Playwright MCP stays the
GATE PASS interact satellite (`playwright-dom`). This module does NOT replace
it, does NOT become a scheduler, does NOT attach at Kernel boot (no second
Core), and does NOT spawn grok.exe.

Cursor-rail shape. kind=DOM. attach_to_kernel refuses authority unless
boot_compose=True. browser_run_code_unsafe stays client-denied (same pin as
playwright-dom / cosmos_mcp_client.DEFAULT_DENY). GET folds never mkdir.
Locator-shaped act (click/goto/type/fill/press) dispatches through the
composed playwright-dom adapter; uncomposed stays fail-open
("locator deferred to playwright-dom"). eval/javascript/document.cookie
refused. Page text is UNTRUSTED.

    py -3.14 cosmos\\cosmos_stagehand_rail.py --selftest
    py -3.14 cosmos\\cosmos_stagehand_rail.py --root V:\\A\\Ai\\COSMOS\\live --gate
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cosmos_mcp_client import (  # noqa: E402
    DEFAULT_DENY, FakeTransport, McpClient, McpClientError,
)
from cosmos_rail_base import (  # noqa: E402,F401
    RailError,
    _ledger_is_authority,
    write_probe_record,
)

SCHEMA = "cosmos-stagehand-rail/1"
WORKER = "cosmos-stagehand-rail"
LINK_ID = "stagehand-dom"
UNDERLAY = "playwright-dom"
PINNED = "4.0.2"
SPEC_NAME = "stagehand_rail.json"
PROBE_NAME = "stagehand_rail_probe.json"
CACHE_NAME = "actions.jsonl"
SRC = "core"
DST = "interact"
PROBE_TOOLS = ("act", "extract", "observe")
UNSAFE_TOOL = "browser_run_code_unsafe"
LOCATOR_OPS = frozenset({"click", "goto", "type", "fill", "press"})
DEFERRED_NOTE = "locator deferred to playwright-dom"
DEFAULT_ALLOW = frozenset({
    "act", "extract", "observe",
    "browser_navigate", "browser_snapshot",
    "browser_click", "browser_type",
})
# DEFAULT_DENY already contains browser_run_code_unsafe. Pin it here so a
# future mcp_client drift cannot silently re-enable RCE on this adapter.
DENY = frozenset(DEFAULT_DENY | {UNSAFE_TOOL})
PROBE_TIMEOUT_S = 45
DISPATCH_TIMEOUT_S = 180
SCHEDULER_DSTS = frozenset({
    "sched", "schedule", "scheduler", "queue", "claim",
})


class StagehandRailError(RailError):
    """kind in {BAD_SPEC, BAD_ROOT, UNREACHABLE, BROKE, DENIED, REFUSED}."""


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
        "package": f"stagehand=={PINNED}",
        "timeout_s": DISPATCH_TIMEOUT_S,
        "probe_timeout_s": PROBE_TIMEOUT_S,
        "kernel_attached": False,
        "replaces_playwright": False,
        "is_scheduler": False,
        "dom_is_untrusted": True,
        "preferred_under": UNDERLAY,
        "unsafe_denied": True,
        "note": (
            "Stagehand preferred-rail adapter UNDER playwright-dom. "
            "act/extract/observe + schema-validated projections + action cache. "
            "DOM is untrusted. Playwright stays. No second Core. GET never mkdir."
        ),
    }


def _pin_origin(spec: dict) -> dict:
    spec["schema"] = SCHEMA
    lid = str(spec.get("link_id") or LINK_ID) or LINK_ID
    if lid == UNDERLAY:
        raise StagehandRailError(
            "BAD_SPEC",
            f"link_id {lid!r} would replace {UNDERLAY}; Stagehand stays under it")
    spec["link_id"] = LINK_ID
    spec["rail_type"] = "DOM"
    spec["src"] = str(spec.get("src") or SRC) or SRC
    dst = str(spec.get("dst") or DST) or DST
    if dst in SCHEDULER_DSTS:
        raise StagehandRailError(
            "BAD_SPEC",
            f"dst={dst!r} refused: Stagehand is not a scheduler")
    if dst in ("read", "models", "search", "code", "papers"):
        spec["route_note"] = (
            f"coerced dst={dst!r} to {DST} (UNDER {UNDERLAY}; dump-dom stays READ)")
        dst = DST
    spec["dst"] = dst
    spec["package"] = f"stagehand=={PINNED}"
    spec["metered_usd"] = float(spec.get("metered_usd") or 0.0)
    spec["budget_usd"] = float(spec.get("budget_usd") or 0.0)
    spec["policy_rank"] = int(spec.get("policy_rank") or 0)
    spec["timeout_s"] = int(spec.get("timeout_s") or DISPATCH_TIMEOUT_S)
    spec["probe_timeout_s"] = int(spec.get("probe_timeout_s") or PROBE_TIMEOUT_S)
    # Overlay cannot claim Kernel attach, a playwright replacement, or a scheduler.
    spec["kernel_attached"] = False
    spec["replaces_playwright"] = False
    spec["is_scheduler"] = False
    spec["dom_is_untrusted"] = True
    spec["preferred_under"] = UNDERLAY
    spec["unsafe_denied"] = True
    return spec


def merge_spec(overlay) -> dict:
    spec = default_spec()
    if overlay is None:
        return _pin_origin(spec)
    if not isinstance(overlay, dict):
        raise StagehandRailError(
            "BAD_SPEC", f"spec overlay is {type(overlay).__name__}")
    for k, v in overlay.items():
        spec[k] = v
    if spec.get("schema") != SCHEMA:
        raise StagehandRailError(
            "BAD_SPEC", f"spec schema {spec.get('schema')!r} != {SCHEMA}")
    if spec.get("rail_type") not in (None, "DOM"):
        raise StagehandRailError(
            "BAD_SPEC",
            f"stagehand rail_type must be DOM, got {spec.get('rail_type')!r}")
    return _pin_origin(spec)


def load_spec(path: Path | None) -> dict:
    if path is None or not Path(path).exists():
        return default_spec()
    try:
        raw = Path(path).read_text(encoding="utf-8")
    except OSError as e:
        raise StagehandRailError("BAD_SPEC", f"unreadable spec {path}: {e}") from e
    try:
        overlay = json.loads(raw)
    except ValueError as e:
        raise StagehandRailError("BAD_SPEC", f"unparseable spec {path}: {e}") from e
    return merge_spec(overlay)


def write_spec(path: Path, spec: dict | None = None) -> dict:
    body = merge_spec(spec)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(body, indent=2, sort_keys=True,
                               ensure_ascii=False) + "\n",
                    encoding="utf-8")
    return body


def spec_path_for(paths) -> Path:
    return paths.config(SPEC_NAME)


def probe_path_for(paths) -> Path:
    return paths.config(PROBE_NAME)


def cache_dir(paths) -> Path:
    return paths.role("state", "stagehand_rail")


def cache_path(paths) -> Path:
    return cache_dir(paths) / CACHE_NAME


def _iso_now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _cache_key(instruction: str) -> str:
    return hashlib.sha256(str(instruction or "").encode("utf-8")).hexdigest()


def validate_projection(data, schema) -> dict:
    """DOM is untrusted. Schema is the authority for an extract projection.

    JSON-Schema-lite: type=object, required[], properties{name: {type}}.
    Raw HTML / a bare string is REFUSED, not accepted as a page fact.
    """
    if not isinstance(schema, dict) or not schema:
        raise StagehandRailError(
            "BROKE", "extract requires a schema (DOM is untrusted)")
    if isinstance(data, str):
        raise StagehandRailError(
            "BROKE", "raw DOM/string rejected (DOM is untrusted; want object)")
    if not isinstance(data, dict):
        raise StagehandRailError(
            "BROKE", f"projection is {type(data).__name__}, want object")
    if schema.get("type") not in (None, "object"):
        raise StagehandRailError(
            "BROKE", f"schema.type {schema.get('type')!r} unsupported")
    required = schema.get("required") or []
    if not isinstance(required, list):
        raise StagehandRailError("BAD_SPEC", "schema.required must be a list")
    missing = [k for k in required if k not in data]
    if missing:
        raise StagehandRailError(
            "BROKE", f"projection missing required {missing} (DOM is untrusted)")
    props = schema.get("properties") if isinstance(schema.get("properties"), dict) else {}
    for name, rule in props.items():
        if name not in data:
            continue
        want = (rule or {}).get("type") if isinstance(rule, dict) else None
        val = data[name]
        if want == "string" and not isinstance(val, str):
            raise StagehandRailError(
                "BROKE", f"projection.{name} want string got {type(val).__name__}")
        if want == "number" and (
                isinstance(val, bool) or not isinstance(val, (int, float))):
            raise StagehandRailError(
                "BROKE", f"projection.{name} want number got {type(val).__name__}")
        if want == "boolean" and not isinstance(val, bool):
            raise StagehandRailError(
                "BROKE", f"projection.{name} want boolean got {type(val).__name__}")
        if want == "object" and not isinstance(val, dict):
            raise StagehandRailError(
                "BROKE", f"projection.{name} want object got {type(val).__name__}")
        if want == "array" and not isinstance(val, list):
            raise StagehandRailError(
                "BROKE", f"projection.{name} want array got {type(val).__name__}")
        if isinstance(val, str) and "<" in val and ">" in val:
            raise StagehandRailError(
                "BROKE", f"projection.{name} looks like raw HTML (DOM is untrusted)")
    return dict(data)


def snapshot_cache(paths) -> dict:
    """GET fold. Never mkdir. Never invents. DOM is untrusted.

    Absent store = UNMEASURED. A read must not create state/stagehand_rail/.
    """
    rec = {
        "schema": SCHEMA,
        "ok": True,
        "kind": "UNMEASURED",
        "n_obs": 0,
        "kernel_attached": False,
        "dom_is_untrusted": True,
        "playwright_stays": True,
        "underlay": UNDERLAY,
        "link_id": LINK_ID,
        "is_scheduler": False,
        "note": (
            "GET never mkdir. Action cache is POST-path only. "
            "kernel_attached is false unless Kernel boot_compose attached."
        ),
    }
    p = cache_path(paths)
    if not p.is_file():
        return rec
    try:
        text = p.read_text(encoding="utf-8")
    except OSError:
        rec["kind"] = "BROKE"
        return rec
    n = 0
    last = None
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except ValueError:
            continue
        if not isinstance(row, dict):
            continue
        n += 1
        last = row
    rec["n_obs"] = n
    rec["last"] = last
    rec["kind"] = "MEASURED" if n else "UNMEASURED"
    return rec


def record_action(paths, instruction: str, action: dict) -> dict:
    """POST-path only. May mkdir the cache role. GET must not call this."""
    row = {
        "schema": SCHEMA,
        "at": _iso_now(),
        "key": _cache_key(instruction),
        "instruction": str(instruction or "")[:400],
        "action": action if isinstance(action, dict) else {"text": str(action)[:400]},
    }
    d = cache_dir(paths)
    d.mkdir(parents=True, exist_ok=True)
    with cache_path(paths).open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    return snapshot_cache(paths)


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
        data = result.get("data")
        if isinstance(data, (dict, list)):
            parts.append(json.dumps(data)[:4000])
        elif result.get("text"):
            parts.append(str(result.get("text")))
        else:
            parts.append(json.dumps(result)[:4000])
    return "\n".join(parts)


def _json_of(result: dict):
    if not isinstance(result, dict):
        return None
    if isinstance(result.get("data"), (dict, list)):
        return result["data"]
    text = _text_of(result)
    try:
        obj = json.loads(text)
    except ValueError:
        return None
    return obj if isinstance(obj, (dict, list)) else None


class ActionCache:
    """In-process Stagehand action cache. Disk persist is POST-only."""

    def __init__(self):
        self._mem: dict[str, dict] = {}

    def get(self, instruction: str):
        return self._mem.get(_cache_key(instruction))

    def put(self, instruction: str, action: dict) -> dict:
        rec = dict(action) if isinstance(action, dict) else {"text": str(action)}
        rec["cached"] = True
        rec["key"] = _cache_key(instruction)
        self._mem[rec["key"]] = rec
        return rec


def refused_act(text, payload=None) -> bool:
    """act() refuses eval / javascript / document.cookie (fail-closed)."""
    payload = payload if isinstance(payload, dict) else {}
    blob = " ".join([
        str(text or ""),
        str(payload.get("instruction") or ""),
        str(payload.get("prompt") or ""),
        str(payload.get("url") or ""),
        str(payload.get("op") or ""),
        str(payload.get("action") or ""),
        str(payload.get("code") or ""),
        str(payload.get("selector") or ""),
    ]).lower()
    if "document.cookie" in blob:
        return True
    if "javascript:" in blob:
        return True
    if re.search(r"(?<![\w])javascript(?![\w])", blob):
        return True
    if "eval(" in blob or re.search(r"(?<![\w])eval(?![\w])", blob):
        return True
    return False


def parse_locator_intent(instruction, payload=None):
    """Locator-shaped intent: click / goto / type / fill / press.

    Structured payload.op wins. Else the first word of the instruction.
    Returns None when the instruction is NL Stagehand act (not a locator).
    """
    payload = payload if isinstance(payload, dict) else {}
    op = str(payload.get("op") or payload.get("action")
             or payload.get("locator_op") or "").strip().lower()
    if op == "navigate":
        op = "goto"
    text = str(instruction or payload.get("instruction")
               or payload.get("prompt") or "").strip()
    if op in LOCATOR_OPS:
        return _intent_from_payload(op, payload, text)
    if not text:
        return None
    m = re.match(r"^(click|goto|navigate|type|fill|press)\b(.*)$", text, re.I)
    if not m:
        return None
    raw_op = m.group(1).lower()
    if raw_op == "navigate":
        raw_op = "goto"
    return _intent_from_text(raw_op, (m.group(2) or "").strip(), payload)


def _intent_from_payload(op: str, payload: dict, instruction: str) -> dict:
    rec = {"op": op}
    if payload.get("selector"):
        rec["selector"] = str(payload["selector"])
    if payload.get("url"):
        rec["url"] = str(payload["url"])
    elif op == "goto" and instruction and not instruction.lower().startswith("goto"):
        rec["url"] = instruction
    if payload.get("element"):
        rec["element"] = str(payload["element"])
    if payload.get("ref"):
        rec["ref"] = str(payload["ref"])
    if op in ("type", "fill"):
        if payload.get("text") is not None:
            rec["text"] = str(payload["text"])
        elif payload.get("value") is not None:
            rec["text"] = str(payload["value"])
    if op == "press" and payload.get("key"):
        rec["key"] = str(payload["key"])
    if op == "goto" and "url" not in rec:
        rec["url"] = str(payload.get("url") or instruction or "")
    return rec


def _intent_from_text(op: str, rest: str, payload: dict) -> dict:
    rec = {"op": op}
    if op == "goto":
        rec["url"] = rest or str(payload.get("url") or "")
        return rec
    if op == "press":
        rec["key"] = rest.split()[0] if rest else str(payload.get("key") or "")
        return rec
    if op == "click":
        rec["selector"] = rest or str(payload.get("selector") or "")
        rec["element"] = rec["selector"]
        return rec
    if op == "type":
        m = re.match(r"^(.*?)(?:\s+into\s+(.+))$", rest, re.I)
        if m:
            rec["text"] = m.group(1).strip().strip("'\"")
            rec["selector"] = m.group(2).strip()
        else:
            rec["text"] = rest.strip().strip("'\"")
            if payload.get("selector"):
                rec["selector"] = str(payload["selector"])
        return rec
    if op == "fill":
        m = re.match(r"^(\S+)(?:\s+with\s+(.+))?$", rest, re.I)
        if m:
            rec["selector"] = m.group(1)
            if m.group(2):
                rec["text"] = m.group(2).strip().strip("'\"")
        elif rest:
            rec["selector"] = rest
        if payload.get("text") is not None and "text" not in rec:
            rec["text"] = str(payload["text"])
        return rec
    return rec


def locator_tool_args(intent: dict) -> dict:
    """Map a locator intent onto Playwright MCP tool arguments."""
    op = intent.get("op")
    selector = str(intent.get("selector") or intent.get("element") or "")
    ref = str(intent.get("ref") or selector)
    if op == "goto":
        return {"url": str(intent.get("url") or "")}
    if op == "click":
        return {"element": selector or ref, "ref": ref or selector}
    if op == "type":
        return {"element": selector or ref, "ref": ref or selector,
                "text": str(intent.get("text") or "")}
    if op == "fill":
        value = str(intent.get("text") or intent.get("value") or "")
        return {"fields": [{
            "name": selector or "field",
            "type": "textbox",
            "ref": ref or selector,
            "value": value,
        }]}
    if op == "press":
        return {"key": str(intent.get("key") or "")}
    return {k: v for k, v in intent.items() if k != "op"}


class StagehandRail:
    """Dispatcher adapter. kind=DOM. Preferred for act/extract/observe.

    Playwright-dom stays the GATE PASS interact rail. This adapter sits UNDER
    it: same MCP client deny pin, navigate/snapshot underlay tools optional,
    Stagehand verbs preferred. Isolated --gate Dispatcher, not the live daemon.
    """
    kind = "DOM"

    def __init__(self, spec: dict | None = None, *, output_dir: Path | None = None,
                 client_factory=None, timeout_s: float | None = None,
                 underlay=None):
        self.spec = merge_spec(spec)
        self.metered_usd = float(self.spec.get("metered_usd") or 0.0)
        self.link_id = self.spec["link_id"]
        self.output_dir = Path(output_dir) if output_dir is not None else Path(".")
        self._client_factory = client_factory
        self._timeout = float(timeout_s or self.spec.get("timeout_s") or DISPATCH_TIMEOUT_S)
        self._last = None
        self._client = None
        self._underlay = underlay
        self.cache = ActionCache()

    def compose_underlay(self, adapter):
        """Bind the existing playwright-dom adapter. Does not spawn a second stack."""
        self._underlay = adapter
        return adapter

    def underlay_composed(self) -> bool:
        return self._underlay is not None

    def last_identity(self):
        return self._last

    def _make_client(self, timeout_s: float) -> McpClient:
        if self._client_factory is not None:
            return self._client_factory()
        raise StagehandRailError(
            "UNREACHABLE",
            "no Stagehand transport (inject client_factory for --selftest / "
            "--gate; live SDK is optional and must not invent PASS)")

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
        """Cheapest liveness: tools/list contains act AND extract AND observe."""
        tmo = float(self.spec.get("probe_timeout_s") or PROBE_TIMEOUT_S)
        try:
            client = self._ensure(tmo)
            client.timeout_s = tmo
            names = client.tool_names()
            info = client.server_info or {}
        except StagehandRailError as e:
            self._last = {"ok": False, "kind": e.kind, "detail": str(e)}
            return False, f"{e.kind}: {e}"
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
            "unsafe_listed": UNSAFE_TOOL in names,
            "unsafe_denied": UNSAFE_TOOL in getattr(client, "denylist", DENY),
            "underlay": UNDERLAY,
            "kernel_attached": False,
        }
        if missing:
            return False, (
                f"BROKE tools/list missing {missing} "
                f"(have {len(names)}: {','.join(names[:8])})")
        return True, (
            f"stagehand-dom tools/list n={len(names)} "
            f"act+extract+observe present under={UNDERLAY} "
            f"server={info.get('name')} version={info.get('version')}")

    def _call(self, client: McpClient, tool: str, args: dict) -> dict:
        if tool == UNSAFE_TOOL or tool in DENY:
            raise StagehandRailError(
                "DENIED",
                f"tool {tool!r} is client-denied (browser_run_code_unsafe stays denied)")
        try:
            return client.tools_call(tool, args)
        except McpClientError as e:
            raise StagehandRailError(e.kind, str(e)) from e

    def dispatch(self, payload: dict) -> dict:
        payload = payload or {}
        verb = str(payload.get("verb") or payload.get("tool") or "").strip().lower()
        if verb == UNSAFE_TOOL or verb in DENY:
            return {"ok": False, "kind": "DENIED",
                    "detail": f"{UNSAFE_TOOL} stays denied",
                    "node": self.link_id}
        tmo = float(payload.get("timeout_s") or self._timeout)
        try:
            client = self._ensure(tmo)
            client.timeout_s = tmo
            if verb in PROBE_TOOLS:
                return self._dispatch_stagehand(client, verb, payload)
            url = payload.get("url")
            if url:
                return self._dispatch_underlay(client, payload, url)
            return {"ok": False, "kind": "BROKE",
                    "detail": "dispatch wants verb=act|extract|observe or payload.url",
                    "node": self.link_id}
        except StagehandRailError as e:
            return {"ok": False, "kind": e.kind, "detail": str(e),
                    "node": self.link_id}
        except McpClientError as e:
            return {"ok": False, "kind": e.kind, "detail": str(e),
                    "node": self.link_id}
        except Exception as e:  # noqa: BLE001
            return {"ok": False, "kind": "UNREACHABLE",
                    "detail": f"{type(e).__name__}: {e}", "node": self.link_id}

    def act(self, instruction: str = "", payload: dict | None = None, **extra) -> dict:
        """Preferred act. Locator-shaped intents go through playwright-dom.

        Uncomposed underlay stays fail-open: ok + note
        'locator deferred to playwright-dom'. Does not invent a second DOM
        stack. eval / javascript / document.cookie are DENIED. Page text
        is UNTRUSTED.
        """
        payload = dict(payload or {})
        payload.update(extra)
        text = str(instruction or payload.get("instruction")
                   or payload.get("prompt") or payload.get("text") or "")
        payload.setdefault("instruction", text)
        if refused_act(text, payload):
            return {
                "ok": False, "kind": "DENIED",
                "detail": "act refuses eval/javascript/document.cookie",
                "node": self.link_id, "verb": "act",
                "dom_is_untrusted": True, "text_trust": "UNTRUSTED",
                "kernel_attached": False, "underlay": UNDERLAY,
                "locator_dispatched": False,
            }
        intent = parse_locator_intent(text, payload)
        if intent is not None:
            return self._act_locator(intent, text)
        rec = {
            "ok": True, "kind": "DOM", "node": self.link_id,
            "verb": "act", "underlay": UNDERLAY, "usd": 0.0,
            "dom_is_untrusted": True, "kernel_attached": False,
            "text_trust": "UNTRUSTED", "cached": False,
            "locator_dispatched": False,
            "underlay_composed": self.underlay_composed(),
        }
        hit = self.cache.get(text)
        if hit is not None:
            rec["cached"] = True
            rec["text"] = str(hit.get("text") or hit.get("action") or "cached-act")[:4000]
            rec["action"] = hit
            return rec
        tmo = float(payload.get("timeout_s") or self._timeout)
        client = self._ensure(tmo)
        client.timeout_s = tmo
        out = self._call(client, "act", {"instruction": str(text)})
        stored = self.cache.put(text, {"text": _text_of(out), "action": "act"})
        rec["text"] = _text_of(out)[:8000]
        rec["action"] = stored
        rec["cached"] = False
        return rec

    def _act_locator(self, intent: dict, instruction: str) -> dict:
        rec = {
            "ok": True, "kind": "DOM", "node": self.link_id,
            "verb": "act", "op": intent.get("op"),
            "underlay": UNDERLAY, "usd": 0.0,
            "dom_is_untrusted": True, "kernel_attached": False,
            "text_trust": "UNTRUSTED",
            "locator_shaped": True,
            "locator_dispatched": False,
            "underlay_composed": self.underlay_composed(),
            "instruction": str(instruction)[:400],
        }
        underlay = self._underlay
        if underlay is None:
            rec["note"] = DEFERRED_NOTE
            rec["action"] = {"op": intent.get("op"), "deferred": True}
            return rec
        runner = getattr(underlay, "run_locator", None)
        if callable(runner):
            try:
                out = runner(intent.get("op"), locator_tool_args(intent))
            except Exception as e:  # noqa: BLE001
                rec["ok"] = False
                rec["kind"] = "BROKE"
                rec["detail"] = f"{type(e).__name__}: {e}"
                rec["note"] = DEFERRED_NOTE
                return rec
            if not isinstance(out, dict):
                out = {"ok": True, "text": str(out)[:8000]}
            rec["locator_dispatched"] = True
            rec["underlay_node"] = out.get("node") or UNDERLAY
            rec["tool"] = out.get("tool")
            rec["text"] = str(out.get("text") or "")[:8000]
            rec["text_trust"] = "UNTRUSTED"
            rec["dom_is_untrusted"] = True
            rec["ok"] = bool(out.get("ok", True))
            rec["kind"] = out.get("kind") or "DOM"
            if out.get("detail"):
                rec["detail"] = out["detail"]
            rec["action"] = {"op": intent.get("op"), "tool": out.get("tool"),
                             "via": UNDERLAY}
            return rec
        if (intent.get("op") == "goto" and hasattr(underlay, "dispatch")
                and intent.get("url")):
            out = underlay.dispatch({"url": intent["url"]}) or {}
            rec["locator_dispatched"] = True
            rec["underlay_node"] = out.get("node") or UNDERLAY
            rec["text"] = str(out.get("text") or "")[:8000]
            rec["text_trust"] = "UNTRUSTED"
            rec["ok"] = bool(out.get("ok"))
            rec["kind"] = out.get("kind") or "DOM"
            rec["action"] = {"op": "goto", "via": UNDERLAY}
            if out.get("detail"):
                rec["detail"] = out["detail"]
            return rec
        rec["note"] = DEFERRED_NOTE
        rec["action"] = {
            "op": intent.get("op"), "deferred": True,
            "reason": "underlay has no run_locator",
        }
        return rec

    def extract(self, instruction: str = "", schema=None,
                payload: dict | None = None, **extra) -> dict:
        """Schema-validated projection. GET/extract never mkdir. DOM untrusted."""
        payload = dict(payload or {})
        payload.update(extra)
        payload["verb"] = "extract"
        payload["instruction"] = (
            instruction or payload.get("instruction") or payload.get("prompt") or "")
        if schema is not None:
            payload["schema"] = schema
        return self.dispatch(payload)

    def observe(self, instruction: str = "", payload: dict | None = None,
                **extra) -> dict:
        """Candidates only. GET/observe never mkdir. DOM untrusted."""
        payload = dict(payload or {})
        payload.update(extra)
        payload["verb"] = "observe"
        payload["instruction"] = (
            instruction or payload.get("instruction") or payload.get("prompt") or "")
        return self.dispatch(payload)

    def _dispatch_stagehand(self, client: McpClient, verb: str, payload: dict) -> dict:
        instruction = payload.get("instruction") or payload.get("prompt") or payload.get("text") or ""
        rec = {
            "ok": True, "kind": "DOM", "node": self.link_id,
            "verb": verb, "underlay": UNDERLAY, "usd": 0.0,
            "dom_is_untrusted": True, "kernel_attached": False,
            "cached": False, "text_trust": "UNTRUSTED",
        }
        if verb == "act":
            return self.act(instruction, payload=payload)
        if verb == "observe":
            out = self._call(client, "observe", {"instruction": str(instruction)})
            rec["text"] = _text_of(out)[:8000]
            rec["candidates"] = _json_of(out) if isinstance(_json_of(out), list) else []
            rec["raw_dom_authority"] = False
            return rec
        # extract — schema is mandatory (DOM is untrusted)
        schema = payload.get("schema")
        out = self._call(client, "extract", {
            "instruction": str(instruction),
            "schema": schema or {},
        })
        data = _json_of(out)
        if data is None:
            raise StagehandRailError(
                "BROKE", "extract returned no JSON object (DOM is untrusted)")
        rec["data"] = validate_projection(data, schema)
        rec["text"] = json.dumps(rec["data"])[:8000]
        expect = payload.get("expect")
        if expect and expect not in rec["text"] and expect not in rec["data"].values():
            rec["ok"] = False
            rec["kind"] = "BROKE"
            rec["detail"] = f"projection missing expect={expect!r}"
        return rec

    def _dispatch_underlay(self, client: McpClient, payload: dict, url) -> dict:
        if str(url).lower().startswith("file:"):
            return {"ok": False, "kind": "BROKE",
                    "detail": "file:// refused (gate is loopback HTTP; DOM is untrusted)",
                    "node": self.link_id}
        nav = self._call(client, "browser_navigate", {"url": str(url)})
        snap = self._call(client, "browser_snapshot", {})
        text = _text_of(snap)
        rec = {
            "ok": True, "kind": "DOM", "node": self.link_id,
            "verb": "underlay", "url": url, "text": text[:8000],
            "navigate_head": _text_of(nav)[:400],
            "underlay": UNDERLAY, "usd": 0.0, "kernel_attached": False,
            "dom_is_untrusted": True,
        }
        expect = payload.get("expect")
        if expect and expect not in text:
            rec["ok"] = False
            rec["kind"] = "BROKE"
            rec["detail"] = f"underlay snapshot missing expect={expect!r}"
        return rec


def register_stagehand_rail(registry, adapters: dict, spend_gate=None,
                            src: str | None = None, dst: str | None = None, *,
                            paths=None, spec=None, output_dir=None,
                            client_factory=None) -> dict:
    """Register stagehand-dom. Does not unregister playwright-dom."""
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
        output_dir = paths.role("work", "stagehand_rail")
    underlay = adapters.get(UNDERLAY) if adapters else None
    rail = StagehandRail(spec, output_dir=output_dir,
                         client_factory=client_factory, underlay=underlay)
    lid = rail.link_id
    if lid == UNDERLAY:
        raise StagehandRailError("BAD_SPEC", "refusing to occupy playwright-dom")
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
        "underlay": UNDERLAY,
        "kernel_attached": False,
        "output_dir": str(output_dir) if output_dir is not None else None,
        "underlay_composed": rail.underlay_composed(),
    }


# Public face named in the KEEP_STAGEHAND work order. Same rail.
StagehandAdapter = StagehandRail


def attach_to_kernel(kernel, adapters: dict | None = None,
                     client_factory=None, *, boot_compose: bool = False) -> dict:
    """Additive. Refuses authority LINK_REGISTERED unless boot_compose=True.

    Kernel.__init__ compose_rails does NOT call this (no second Core). Pass
    boot_compose=True only from a deliberate Kernel compose if CCr later
    wires it. Isolated --gate ledgers are not authority.
    """
    if _ledger_is_authority(kernel) and not boot_compose:
        raise StagehandRailError(
            "REFUSED",
            "attach_to_kernel refuses authority LINK_REGISTERED until Kernel "
            "boot_compose=True. Isolated --gate ledger only. Stagehand is an "
            "adapter UNDER playwright-dom, not a second Core.")
    if adapters is None:
        adapters = getattr(kernel, "adapters", None)
        if adapters is None:
            adapters = {}
            kernel.adapters = adapters
    out_dir = None
    paths = getattr(kernel, "paths", None)
    if paths is not None:
        out_dir = paths.role("work", "stagehand_rail")
    return register_stagehand_rail(
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
        "kernel_attached": False,
    }
    try:
        attach_to_kernel(duck, {})
        rec["detail"] = "attach_to_kernel DID NOT refuse the authority ledger"
    except StagehandRailError as e:
        rec["refused"] = e.kind == "REFUSED"
        rec["kind"] = e.kind
        rec["detail"] = str(e)
    return rec


def inspect_live_kernel(root) -> dict:
    out = {
        "opened": False,
        "stagehand_in_registry": None,
        "playwright_in_registry": None,
        "error": None,
        "kernel_attached": False,
    }
    try:
        from cosmos_kernel import Kernel
        k = Kernel(root, worker="stagehand-rail-gate", read_only=True)
        out["opened"] = True
        out["tree_id"] = k.paths.sentinel.tree_id
        state = k.registry.state()
        out["stagehand_in_registry"] = LINK_ID in state
        out["playwright_in_registry"] = UNDERLAY in state
        out["read_only"] = True
    except Exception as e:  # noqa: BLE001
        out["error"] = f"{type(e).__name__}: {e}"
    return out


def _compose_isolated(paths, spec, client_factory):
    """Isolated --gate Dispatcher, not the live daemon. Not a scheduler."""
    from cosmos_ledger import Ledger
    from cosmos_registry import Registry
    from cosmos_rails import Dispatcher
    from cosmos_spend import SpendGate

    adapters = {}
    gate_dir = paths.role("state", "stagehand_rail_gate")
    gate_dir.mkdir(parents=True, exist_ok=True)
    out_dir = paths.role("work", "stagehand_rail")
    out_dir.mkdir(parents=True, exist_ok=True)
    led = Ledger(gate_dir / "gate.jsonl", b"stagehand-rail-gate", WORKER)
    reg = Registry(led)
    spend = SpendGate(led)
    attached = register_stagehand_rail(
        reg, adapters, spend_gate=spend, spec=spec,
        output_dir=out_dir, client_factory=client_factory)
    disp = Dispatcher(reg, adapters, led, spend=spend)
    return attached, adapters, disp, led, gate_dir


def gate(root: str | os.PathLike, *, client_factory=None) -> dict:
    """Optional runtime-binding gate. Isolated ledger. Fake transport in tests.

    PASS iff act+extract+observe present AND extract projection contains
    tree_id AND attach refused AND kernel_attached is false AND playwright-dom
    was not replaced. GET cache fold must not mkdir. rc=0 is not the proof.
    """
    from cosmos_paths import CosmosPaths

    paths = CosmosPaths(root)
    spec = load_spec(spec_path_for(paths))
    write_spec(spec_path_for(paths), spec)
    get_before = snapshot_cache(paths)
    cache_existed = cache_dir(paths).exists()
    attached = adapters = disp = led = gate_dir = None
    rec = {
        "schema": SCHEMA,
        "worker": WORKER,
        "gated_at": _iso_now(),
        "root": str(paths.root),
        "tree_id": paths.sentinel.tree_id,
        "link_id": LINK_ID,
        "underlay": UNDERLAY,
        "replaces_playwright": False,
        "is_scheduler": False,
        "spec_path": str(spec_path_for(paths)),
        "dispatcher_constructed": False,
        "authority_ledger_written": False,
        "kernel_attached": False,
        "dom_is_untrusted": True,
        "live_value": None,
        "gate": "FAIL",
        "get_mkdir": False,
        "stage6": {
            "kind": "satellite",
            "kernel_attach": "BACKLOG",
            "preferred_under": UNDERLAY,
            "predicate": (
                "tools/list has act AND extract AND observe AND extract "
                "schema-validates tree_id AND attach refused on authority AND "
                "kernel_attached is false AND playwright-dom stays"
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
        rec["unsafe_denied"] = ident.get("unsafe_denied")
        marker = f"tree_id={paths.sentinel.tree_id}"
        schema = {
            "type": "object",
            "required": ["tree_id"],
            "properties": {"tree_id": {"type": "string"}, "title": {"type": "string"}},
        }
        dispatched = None
        if rec["probe_ok"]:
            dispatched = rail.dispatch({
                "verb": "extract",
                "instruction": "extract the gate marker",
                "schema": schema,
                "expect": paths.sentinel.tree_id,
                "timeout_s": spec.get("timeout_s") or DISPATCH_TIMEOUT_S,
            })
        rec["dispatch_ok"] = bool((dispatched or {}).get("ok"))
        rec["dispatch_detail"] = (dispatched or {}).get("detail")
        rec["dispatch_kind"] = (dispatched or {}).get("kind")
        data = (dispatched or {}).get("data") or {}
        rec["projection"] = data
        rec["projection_has_tree_id"] = (
            isinstance(data, dict) and data.get("tree_id") == paths.sentinel.tree_id
        )
        rec["live_value"] = {
            "tool_names": ident.get("tool_names"),
            "tool_count": ident.get("tool_count"),
            "server": (ident.get("serverInfo") or {}).get("name"),
            "server_version": (ident.get("serverInfo") or {}).get("version"),
            "tree_id": paths.sentinel.tree_id,
            "projection_has_tree_id": rec["projection_has_tree_id"],
            "underlay": UNDERLAY,
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
    get_after = snapshot_cache(paths)
    rec["get_fold"] = get_after
    rec["get_mkdir"] = (not cache_existed) and cache_dir(paths).exists()
    rec["get_kind"] = get_after.get("kind")
    rec["get_before_kind"] = get_before.get("kind")
    names = rec.get("tool_names") or []
    tools_ok = all(n in names for n in PROBE_TOOLS)
    proj_ok = bool(rec.get("projection_has_tree_id"))
    route_ok = rec.get("route") == f"{SRC}->{DST}"
    attach_refused = bool(rec["attach_refusal"].get("refused"))
    rec["identity_ok"] = tools_ok and proj_ok
    rec["identity_why"] = (
        "ok" if rec["identity_ok"]
        else f"tools_ok={tools_ok} projection_has_tree_id={proj_ok}"
    )
    if (rec.get("probe_ok") and rec.get("dispatch_ok") and tools_ok and proj_ok
            and route_ok and attach_refused
            and not rec["authority_ledger_written"]
            and rec["kernel_attached"] is False
            and rec["replaces_playwright"] is False
            and rec["is_scheduler"] is False
            and rec["get_mkdir"] is False):
        rec["gate"] = "PASS"
    rec["proof"] = (
        f"stagehand-dom probe_ok={rec.get('probe_ok')} "
        f"tools={rec.get('tool_count')} "
        f"projection_has_tree_id={rec.get('projection_has_tree_id')} "
        f"tree_id={rec['tree_id']} underlay={UNDERLAY} "
        f"route={rec.get('route')} attach_refused={attach_refused} "
        f"kernel_attached={rec['kernel_attached']} get_mkdir={rec['get_mkdir']}"
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
        {"name": "act"},
        {"name": "extract"},
        {"name": "observe"},
        {"name": "browser_navigate"},
        {"name": "browser_snapshot"},
    ]
    if with_unsafe:
        tools.append({"name": UNSAFE_TOOL})
    marker = {"tree_id": tree_id, "title": "COSMOS stagehand gate"}
    state = {"url": None, "acts": 0}

    def handler(msg):
        method = msg.get("method")
        rid = msg.get("id")
        if method == "initialize":
            return {"jsonrpc": "2.0", "id": rid, "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "Stagehand", "version": PINNED},
            }}
        if method == "notifications/initialized":
            return None
        if method == "tools/list":
            return {"jsonrpc": "2.0", "id": rid, "result": {"tools": tools}}
        if method == "tools/call":
            name = (msg.get("params") or {}).get("name")
            args = (msg.get("params") or {}).get("arguments") or {}
            if name == "act":
                state["acts"] += 1
                return {"jsonrpc": "2.0", "id": rid, "result": {
                    "content": [{"type": "text",
                                 "text": f"acted:{args.get('instruction')} n={state['acts']}"}],
                }}
            if name == "extract":
                return {"jsonrpc": "2.0", "id": rid, "result": {
                    "content": [{"type": "text", "text": json.dumps(marker)}],
                    "data": marker,
                }}
            if name == "observe":
                return {"jsonrpc": "2.0", "id": rid, "result": {
                    "content": [{"type": "text", "text": json.dumps([
                        {"selector": "#tree", "available": True},
                    ])}],
                    "data": [{"selector": "#tree", "available": True}],
                }}
            if name == "browser_navigate":
                state["url"] = args.get("url")
                return {"jsonrpc": "2.0", "id": rid, "result": {
                    "content": [{"type": "text", "text": f"navigated {state['url']}"}],
                }}
            if name == "browser_snapshot":
                return {"jsonrpc": "2.0", "id": rid, "result": {
                    "content": [{"type": "text", "text": (
                        f"- heading: COSMOS stagehand gate\n"
                        f"- paragraph: tree_id={tree_id}\n"
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
            denylist=DENY,
        )
    return factory


def _selftest() -> int:
    """Isolated. Fake transport. No live Stagehand SDK, no authority ledger."""
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

    td = Path(tempfile.mkdtemp(prefix="cosmos_stagehand_rail_"))
    root = install(td / "live", tree_id="spike-stagehand-rail")
    from cosmos_paths import CosmosPaths
    paths = CosmosPaths(root)
    spec = write_spec(paths.config(SPEC_NAME))
    factory = _fake_factory(paths.sentinel.tree_id)

    check("kind=DOM", lambda: StagehandRail.kind == "DOM")
    check("default kernel_attached is false",
          lambda: spec["kernel_attached"] is False
          and default_spec()["kernel_attached"] is False)
    check("overlay cannot claim kernel_attached=true",
          lambda: merge_spec({
              "schema": SCHEMA, "rail_type": "DOM", "kernel_attached": True,
          })["kernel_attached"] is False)
    check("does not replace playwright-dom",
          lambda: spec["link_id"] == LINK_ID
          and spec["replaces_playwright"] is False
          and spec["preferred_under"] == UNDERLAY)
    check("link_id=playwright-dom overlay is BAD_SPEC",
          lambda: _raises_kind(lambda: merge_spec({
              "schema": SCHEMA, "rail_type": "DOM", "link_id": UNDERLAY,
          }), "BAD_SPEC"))
    check("scheduler dst is REFUSED",
          lambda: _raises_kind(lambda: merge_spec({
              "schema": SCHEMA, "rail_type": "DOM", "dst": "sched",
          }), "BAD_SPEC"))
    check("unsafe deny pin includes browser_run_code_unsafe",
          lambda: UNSAFE_TOOL in DENY and UNSAFE_TOOL in DEFAULT_DENY
          and spec["unsafe_denied"] is True)

    empty = snapshot_cache(paths)
    check("GET cache is UNMEASURED and does not mkdir",
          lambda: empty["kind"] == "UNMEASURED" and empty["n_obs"] == 0
          and empty["kernel_attached"] is False
          and not cache_dir(paths).exists())

    rail = StagehandRail(spec, output_dir=td / "sh", client_factory=factory)
    ok, detail = rail.probe()
    check("probe tools/list has act+extract+observe",
          lambda: ok and "act+extract+observe present" in detail)
    ident = rail.last_identity() or {}
    check("unsafe is listed by server (client still denies call)",
          lambda: ident.get("unsafe_listed") is True)
    check("probe identity kernel_attached is false",
          lambda: ident.get("kernel_attached") is False)
    denied = False
    try:
        rail._ensure().tools_call(UNSAFE_TOOL, {"code": "1"})
    except McpClientError as e:
        denied = e.kind == "DENIED"
    check("dispatch path DENIED unsafe", lambda: denied)
    unsafe_d = rail.dispatch({"verb": UNSAFE_TOOL, "instruction": "rce"})
    check("verb=browser_run_code_unsafe is DENIED",
          lambda: (not unsafe_d["ok"]) and unsafe_d["kind"] == "DENIED")

    schema = {
        "type": "object",
        "required": ["tree_id"],
        "properties": {"tree_id": {"type": "string"}},
    }
    ext = rail.dispatch({
        "verb": "extract",
        "instruction": "extract gate marker",
        "schema": schema,
        "expect": paths.sentinel.tree_id,
    })
    check("extract schema-validates tree_id (DOM is untrusted)",
          lambda: ext["ok"] and ext["data"]["tree_id"] == paths.sentinel.tree_id)
    raw = False
    try:
        validate_projection("<html>nope</html>", schema)
    except StagehandRailError as e:
        raw = e.kind == "BROKE"
    check("raw HTML projection is BROKE", lambda: raw)
    noschema = False
    try:
        validate_projection({"tree_id": "x"}, {})
    except StagehandRailError as e:
        noschema = e.kind == "BROKE"
    check("extract without schema is BROKE", lambda: noschema)

    act1 = rail.dispatch({"verb": "act", "instruction": "dismiss the modal"})
    act2 = rail.dispatch({"verb": "act", "instruction": "dismiss the modal"})
    check("act caches the second identical instruction",
          lambda: act1["ok"] and act2["ok"] and act2.get("cached") is True
          and act1.get("cached") is False)
    obs = rail.dispatch({"verb": "observe", "instruction": "find the marker"})
    check("observe returns candidates, not raw-DOM authority",
          lambda: obs["ok"] and obs.get("raw_dom_authority") is False
          and obs.get("text_trust") == "UNTRUSTED")
    check("extract page text stays UNTRUSTED",
          lambda: ext.get("text_trust") == "UNTRUSTED"
          and ext.get("dom_is_untrusted") is True)

    uncomp = rail.act("click #tree")
    check("uncomposed locator act is fail-open deferred (no second DOM stack)",
          lambda: uncomp["ok"] is True
          and uncomp.get("note") == DEFERRED_NOTE
          and uncomp.get("locator_dispatched") is False
          and uncomp.get("underlay_composed") is False
          and uncomp.get("text_trust") == "UNTRUSTED"
          and uncomp.get("dom_is_untrusted") is True
          and rail._underlay is None)
    typed_u = rail.act("type hello into #q")
    filled_u = rail.act("fill #email with a@b.c")
    pressed_u = rail.act("press Enter")
    gone_u = rail.act("goto http://127.0.0.1:9/")
    check("uncomposed type/fill/press/goto stay deferred",
          lambda: all(r.get("note") == DEFERRED_NOTE and r["ok"]
                      and r.get("locator_dispatched") is False
                      for r in (typed_u, filled_u, pressed_u, gone_u)))

    from cosmos_playwright_rail import (
        PlaywrightRail, default_spec as _pw_default_spec,
        _fake_factory as _pw_fake_factory,
    )
    pw = PlaywrightRail(
        _pw_default_spec(), output_dir=td / "pw-under",
        client_factory=_pw_fake_factory(paths.sentinel.tree_id))
    composed = StagehandAdapter(
        spec, output_dir=td / "shc", client_factory=factory, underlay=pw)
    clicked = composed.act("click #tree")
    check("composed locator act dispatches through playwright-dom",
          lambda: clicked["ok"] and clicked.get("locator_dispatched") is True
          and clicked.get("underlay_composed") is True
          and clicked.get("underlay_node") == "playwright-dom"
          and clicked.get("tool") == "browser_click"
          and clicked.get("text_trust") == "UNTRUSTED"
          and clicked.get("dom_is_untrusted") is True)
    gone = composed.act("goto http://127.0.0.1:9/")
    typed = composed.act("type hello into #q")
    filled = composed.act("fill #email with a@b.c")
    pressed = composed.act("press Enter")
    check("composed goto/type/fill/press map to playwright tools",
          lambda: gone.get("tool") == "browser_navigate"
          and typed.get("tool") == "browser_type"
          and filled.get("tool") == "browser_fill_form"
          and pressed.get("tool") == "browser_press_key"
          and all(r.get("locator_dispatched") is True
                  for r in (gone, typed, filled, pressed)))
    for label, instr in (
        ("eval", "eval(document.body)"),
        ("javascript", "javascript:alert(1)"),
        ("document.cookie", "document.cookie"),
    ):
        denied_act = rail.act(instr)
        check("act refuses %s" % label,
              lambda d=denied_act: (not d["ok"]) and d["kind"] == "DENIED")
    check("StagehandAdapter is the rail face (act/extract/observe)",
          lambda: StagehandAdapter is StagehandRail
          and callable(StagehandAdapter.act)
          and callable(StagehandAdapter.extract)
          and callable(StagehandAdapter.observe))
    via_obs = rail.observe("find the marker")
    via_ext = rail.extract("extract gate marker", schema=schema)
    check("observe/extract methods keep text UNTRUSTED and do not mkdir",
          lambda: via_obs["ok"] and via_ext["ok"]
          and via_obs.get("text_trust") == "UNTRUSTED"
          and via_ext.get("text_trust") == "UNTRUSTED"
          and via_ext["data"]["tree_id"] == paths.sentinel.tree_id
          and not cache_dir(paths).exists())
    composed.close()
    pw.close()

    file_d = rail.dispatch({"url": "file:///C:/nope.html"})
    check("file:// underlay is BROKE",
          lambda: (not file_d["ok"]) and file_d["kind"] == "BROKE")
    nav = rail.dispatch({
        "url": "http://127.0.0.1:9/",
        "expect": f"tree_id={paths.sentinel.tree_id}",
    })
    check("underlay snapshot contains tree_id (playwright stays)",
          lambda: nav["ok"] and f"tree_id={paths.sentinel.tree_id}" in nav["text"]
          and nav.get("underlay") == UNDERLAY)
    rail.close()

    still_empty = snapshot_cache(paths)
    check("GET after fake dispatch still does not mkdir cache role",
          lambda: still_empty["kind"] == "UNMEASURED"
          and not cache_dir(paths).exists())

    recorded = record_action(paths, "click the marker", {"text": "acted"})
    check("POST record_action may mkdir; GET then MEASURED",
          lambda: recorded["kind"] == "MEASURED" and recorded["n_obs"] == 1
          and cache_dir(paths).exists())
    get2 = snapshot_cache(paths)
    check("GET after POST does not invent extra rows",
          lambda: get2["n_obs"] == 1 and get2["kernel_attached"] is False)

    led = Ledger(td / "n.jsonl", b"k", "core")
    reg = Registry(led)
    adapters = {}
    rec = register_stagehand_rail(
        reg, adapters, spend_gate=SpendGate(led), spec=spec,
        output_dir=td / "sh2", client_factory=factory)
    check("register kind=DOM core->interact under playwright-dom",
          lambda: rec["spec"]["rail_type"] == "DOM" and rec["dst"] == DST
          and rec["underlay"] == UNDERLAY and rec["kernel_attached"] is False)
    check("register does not occupy playwright-dom",
          lambda: rec["link_id"] == LINK_ID and UNDERLAY not in adapters
          and rec.get("underlay_composed") is False)
    bound = {
        UNDERLAY: PlaywrightRail(
            _pw_default_spec(), output_dir=td / "pw-reg",
            client_factory=_pw_fake_factory(paths.sentinel.tree_id)),
    }
    rec_composed = register_stagehand_rail(
        Registry(Ledger(td / "n2.jsonl", b"k2", "core")),
        bound, spend_gate=SpendGate(led), spec=spec,
        output_dir=td / "sh3", client_factory=factory)
    check("register binds composed playwright-dom underlay when present",
          lambda: rec_composed["rail"].underlay_composed() is True
          and rec_composed.get("underlay_composed") is True
          and rec_composed["link_id"] == LINK_ID
          and UNDERLAY in bound and LINK_ID in bound)
    rec_composed["rail"].close()
    bound[UNDERLAY].close()
    reg.probe_all()
    disp = Dispatcher(reg, adapters, led, spend=SpendGate(led))
    routed = disp.dispatch(SRC, DST, {
        "verb": "extract",
        "instruction": "extract",
        "schema": schema,
        "expect": paths.sentinel.tree_id,
    })
    check("isolated Dispatcher reaches stagehand-dom",
          lambda: routed["ok"] and routed["kind"] == "DOM")
    for ad in adapters.values():
        ad.close()

    g = gate(root, client_factory=_fake_factory(paths.sentinel.tree_id))
    check("gate PASS on fake Stagehand transport",
          lambda: g["gate"] == "PASS" and g["projection_has_tree_id"] is True)
    check("gate kernel_attached is false",
          lambda: g["kernel_attached"] is False)
    check("gate attach refused",
          lambda: g["attach_refusal"]["refused"] is True)
    check("gate does not write authority",
          lambda: g["authority_ledger_written"] is False)
    check("gate GET did not mkdir the action-cache role as a side effect of GET",
          lambda: g.get("get_mkdir") is False)
    check("gate does not claim to replace playwright",
          lambda: g.get("replaces_playwright") is False
          and g.get("underlay") == UNDERLAY)
    check("gate is not a scheduler",
          lambda: g.get("is_scheduler") is False)

    k = Kernel(root, worker="stagehand-rail-selftest")
    _before = set(k.registry.state())
    refused = False
    try:
        attach_to_kernel(k, {})
    except StagehandRailError as e:
        refused = e.kind == "REFUSED"
    check("attach_to_kernel refuses writing Kernel without boot_compose",
          lambda: refused and set(k.registry.state()) == _before)
    att = attach_to_kernel(k, {}, client_factory=factory, boot_compose=True)
    check("attach_to_kernel(boot_compose=True) still registers (BACKLOG hook)",
          lambda: att["link_id"] in k.registry.state()
          and att["link_id"] == LINK_ID)

    from cosmos_playwright_rail import LINK_ID as PW_LINK
    check("playwright-dom link_id unchanged (Playwright stays)",
          lambda: PW_LINK == "playwright-dom" and PW_LINK != LINK_ID)
    kernel_src = (Path(__file__).resolve().parent / "cosmos_kernel.py").read_text(
        encoding="utf-8")
    check("kernel compose_rails does not attach stagehand (no second Core)",
          lambda: "cosmos_stagehand_rail" not in kernel_src
          and "stagehand-dom" not in kernel_src)
    here = Path(__file__).read_text(encoding="utf-8")
    check("this module does not import the job scheduler",
          lambda: "import cosmos_sch" + "ed" not in here
          and "from cosmos_sch" + "ed" not in here)

    bad = [(l, e) for l, ok, e in results if not ok]
    for label, ok, err in results:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (stagehand-dom UNDER playwright-dom; "
          "act/extract/observe; DOM untrusted; unsafe denied; GET never mkdir; "
          "kernel_attached false; attach refused; no second Core)"
          % ("PASS" if not bad else "FAIL", len(results)))
    return 0 if not bad else 1


def _raises_kind(fn, kind: str) -> bool:
    try:
        fn()
    except StagehandRailError as e:
        return e.kind == kind
    return False


def main() -> int:
    ap = argparse.ArgumentParser(
        prog="cosmos_stagehand_rail",
        description="COSMOS Stagehand DOM adapter UNDER playwright-dom. "
                    "--selftest is fake transport. --gate is optional and "
                    "does not invent PASS without a transport. Not a scheduler.")
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
            out = paths.role("work", "stagehand_rail")
            rail = StagehandRail(spec, output_dir=out)
            try:
                ok, detail = rail.probe()
                ident = rail.last_identity() or {}
                rec = {"ok": ok, "detail": detail, "link_id": rail.link_id,
                       "kernel_attached": False,
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
