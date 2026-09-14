#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_cop_rail - satellite CHAT rail `cop-chat` (CoP — M365 Copilot).

Office/docs, read-only, chat-attach only. Not GitHub Copilot. Not Cowork.
Not Graph CRUD / mail / file create. Write verbs are REFUSED.

Runtime binding = the vendor-emitted `model` on a real live attach.
A spec file cannot forge it. Missing model = proof fails, fail-closed.

Documented Microsoft Chat API (not a COSMOS route):
  POST https://graph.microsoft.com/beta/copilot/conversations
  POST https://graph.microsoft.com/beta/copilot/conversations/{id}/chat

Token: live/config/cop_token.txt (never printed). Spec overlay optional.
Does NOT edit ledger/sched/service. attach_to_kernel refuses the authority
ledger unless boot_compose=True.

    py -3.14 cosmos\\cosmos_cop_rail.py --selftest
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

SCHEMA = "cosmos-cop-rail/1"
WORKER = "cosmos-cop-rail"
LINK_ID = "cop-chat"
BASE = "https://graph.microsoft.com/beta/copilot"
KEY_NAME = "cop_token.txt"
SPEC_NAME = "cop_rail.json"
SRC = "core"
DST = "docs"
RAIL_TYPE = "CHAT"
UA = "COSMOS-cop-rail/1 (cop-chat; keithbbf-gif/cosmos)"
VENDOR_CHAT = "https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/api/ai-services/chat/overview"
WRITE_VERBS = frozenset({
    "write", "send", "create", "edit", "delete", "mail", "update", "patch",
})
INDEPENDENCE_NOTE = (
    "SGH+GBW are not independent checks of each other"
)

from cosmos_rail_base import (  # noqa: E402
    RailError, _ledger_is_authority,
)


class CopRailError(RailError):
    """kind in {NO_KEY, BAD_SPEC, BAD_ROOT, UNREACHABLE, AUTH_REQUIRED, BROKE, REFUSED}."""


def default_spec() -> dict:
    return {
        "schema": SCHEMA,
        "link_id": LINK_ID,
        "rail_type": RAIL_TYPE,
        "src": SRC,
        "dst": DST,
        "policy_rank": 0,
        "metered_usd": 0.0,
        "budget_usd": 0.0,
        "base": BASE,
        "key_name": KEY_NAME,
        "timeout_s": 45,
        "read_only": True,
        "chat_attach_only": True,
        "vendor_docs": VENDOR_CHAT,
        "independence_note": INDEPENDENCE_NOTE,
        "note": (
            "CoP M365 Copilot. Office/docs read-only chat-attach. "
            "Bind vendor-emitted model on a live call only. "
            "Not GitHub Copilot. Not Cowork. Writes REFUSED. "
            + INDEPENDENCE_NOTE + "."
        ),
    }


def _pin_origin(spec: dict) -> dict:
    base = str(spec.get("base") or BASE).rstrip("/")
    if base != BASE:
        raise CopRailError("BAD_SPEC", f"base {base!r} != {BASE!r}")
    spec["base"] = BASE
    kn = str(spec.get("key_name") or KEY_NAME)
    if kn != KEY_NAME:
        raise CopRailError("BAD_SPEC", f"key_name {kn!r} != {KEY_NAME!r}")
    spec["key_name"] = KEY_NAME
    spec["src"] = str(spec.get("src") or SRC) or SRC
    spec["dst"] = DST
    spec["rail_type"] = RAIL_TYPE
    spec["link_id"] = LINK_ID
    spec["read_only"] = True
    spec["chat_attach_only"] = True
    spec["metered_usd"] = float(spec.get("metered_usd") or 0.0)
    spec["budget_usd"] = float(spec.get("budget_usd") or 0.0)
    spec["policy_rank"] = int(spec.get("policy_rank") or 0)
    spec["timeout_s"] = int(spec.get("timeout_s") or 45)
    spec["schema"] = SCHEMA
    spec["vendor_docs"] = VENDOR_CHAT
    spec["independence_note"] = INDEPENDENCE_NOTE
    return spec


def merge_spec(overlay) -> dict:
    spec = default_spec()
    if overlay is None:
        return _pin_origin(spec)
    if not isinstance(overlay, dict):
        raise CopRailError("BAD_SPEC", f"spec overlay is {type(overlay).__name__}")
    for k, v in overlay.items():
        spec[k] = v
    if spec.get("schema") != SCHEMA:
        raise CopRailError("BAD_SPEC", f"spec schema {spec.get('schema')!r} != {SCHEMA}")
    if spec.get("rail_type") not in (None, RAIL_TYPE, "CHAT"):
        raise CopRailError(
            "BAD_SPEC", f"cop rail_type must be CHAT, got {spec.get('rail_type')!r}")
    return _pin_origin(spec)


def load_spec(path: Path | None) -> dict:
    if path is None or not Path(path).exists():
        return default_spec()
    try:
        overlay = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise CopRailError("BAD_SPEC", f"unreadable spec {path}: {e}") from e
    return merge_spec(overlay)


def write_spec(path: Path, spec: dict | None = None) -> dict:
    body = merge_spec(spec)
    body.pop("api_key", None)
    body.pop("key", None)
    body.pop("token", None)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(body, indent=2, sort_keys=True,
                               ensure_ascii=False) + "\n",
                    encoding="utf-8")
    return body


def redact_key(key: str) -> str:
    k = (key or "").strip()
    if len(k) >= 4:
        return f"…{k[-4:]}"
    return "…????"


def read_key(key_path: Path | None) -> str | None:
    if key_path is None:
        return None
    p = Path(key_path)
    if not p.exists():
        return None
    try:
        text = p.read_text(encoding="utf-8").strip()
    except OSError:
        return None
    return text or None


def _http_kind(status: int) -> str:
    if status in (401, 403):
        return "AUTH_REQUIRED"
    if status in (-1,):
        return "UNREACHABLE"
    return "BROKE"


def _real_http(method: str, url: str, body, headers: dict, timeout_s: float):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, method=method, data=data, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as r:  # noqa: S310
            raw = r.read().decode("utf-8") or "{}"
            try:
                obj = json.loads(raw)
            except ValueError:
                obj = {"raw": raw[:400]}
            return int(r.status), obj
    except urllib.error.HTTPError as e:
        raw = (e.read() or b"").decode("utf-8", "replace")
        try:
            obj = json.loads(raw) if raw else {"error": str(e)}
        except ValueError:
            obj = {"error": raw[:400]}
        return int(e.code), obj
    except Exception as e:  # noqa: BLE001
        return -1, {"error": f"{type(e).__name__}: {e}"}


def _vendor_model(obj) -> str:
    """Name the responder ONLY from a vendor-emitted field. Never invent."""
    if not isinstance(obj, dict):
        return ""
    for key in ("model", "modelId", "model_id"):
        val = obj.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    msg = obj.get("message") if isinstance(obj.get("message"), dict) else {}
    for key in ("model", "modelId"):
        val = msg.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return ""


def _message_text(obj) -> str:
    if not isinstance(obj, dict):
        return ""
    msg = obj.get("message") if isinstance(obj.get("message"), dict) else {}
    for key in ("text", "content"):
        val = msg.get(key) or obj.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return ""


class CopRail:
    """Dispatcher adapter. kind=CHAT. probe + dispatch = chat-attach only."""

    kind = "CHAT"

    def __init__(self, key_path: Path | str | None, spec: dict | None = None,
                 http=None):
        self.spec = merge_spec(spec)
        self.key_path = Path(key_path) if key_path is not None else None
        self.metered_usd = float(self.spec.get("metered_usd") or 0.0)
        self._http = http
        self.link_id = LINK_ID
        self._last = None

    def last_identity(self) -> dict | None:
        return self._last

    def _headers(self, key: str) -> dict:
        return {
            "Authorization": "Bearer " + key,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": UA,
        }

    def _call(self, method: str, path: str, body=None):
        if self._http is not None:
            return self._http(method, path, body)
        key = read_key(self.key_path)
        if not key:
            return 401, {"error": {"message": "NO_KEY", "code": "invalid_token"}}
        url = self.spec["base"] + path
        status, obj = _real_http(method, url, body, self._headers(key),
                                 float(self.spec["timeout_s"]))
        return status, obj

    def probe(self):
        rec = self._attach_ask("Reply with the single token PONG and nothing else.")
        self._last = rec
        ok = bool(rec.get("ok") and rec.get("model"))
        return ok, str(rec.get("detail") or "")[:300]

    def dispatch(self, payload: dict) -> dict:
        payload = payload if isinstance(payload, dict) else {}
        verb = str(payload.get("verb") or "attach").strip().lower()
        if verb in WRITE_VERBS or payload.get("write"):
            rec = {
                "ok": False, "kind": "REFUSED", "rc": 2, "body": "",
                "model": "", "link_id": self.link_id,
                "detail": "CoP is read-only chat-attach; write/send/create REFUSED",
            }
            self._last = rec
            return rec
        text = str(payload.get("text") or payload.get("prompt") or "").strip()
        if not text:
            rec = {
                "ok": False, "kind": "REFUSED", "rc": 2, "body": "",
                "model": "", "link_id": self.link_id,
                "detail": "attach/ask requires text or prompt",
            }
            self._last = rec
            return rec
        rec = self._attach_ask(text, attachments=payload.get("attachments"))
        self._last = rec
        return rec

    def _attach_ask(self, text: str, attachments=None) -> dict:
        """Live chat-attach. Model is vendor-emitted or empty (proof fails)."""
        status, created = self._call("POST", "/conversations", {})
        if status in (401, 403):
            return {
                "ok": False, "kind": "AUTH_REQUIRED", "rc": 2, "body": "",
                "model": "", "http": status, "link_id": self.link_id,
                "detail": f"AUTH_REQUIRED http={status}",
            }
        if status != 200 and status != 201:
            kind = _http_kind(status)
            return {
                "ok": False, "kind": kind, "rc": 2, "body": "",
                "model": "", "http": status, "link_id": self.link_id,
                "detail": f"{kind} http={status}",
            }
        cid = ""
        if isinstance(created, dict):
            cid = str(created.get("id") or created.get("conversationId") or "")
        if not cid:
            return {
                "ok": False, "kind": "BROKE", "rc": 2, "body": "",
                "model": "", "http": status, "link_id": self.link_id,
                "detail": "BROKE: conversation id absent (not a live attach)",
            }
        body = {
            "message": {"text": text},
            "locationHint": {"timeZone": "America/Chicago"},
        }
        if isinstance(attachments, list) and attachments:
            # Names/ids only — read-only attach. Never write the doc.
            body["attachments"] = attachments
        status2, obj = self._call("POST", f"/conversations/{cid}/chat", body)
        model = _vendor_model(obj)
        text_out = _message_text(obj)
        live = status2 == 200 and bool(model) and bool(text_out)
        kind = None if live else (
            _http_kind(status2) if status2 != 200 else "BROKE")
        return {
            "ok": live,
            "kind": kind,
            "rc": 0 if live else 2,
            "http": status2,
            "body": text_out if live else "",
            "text": text_out if live else "",
            "model": model if live else "",
            "model_source": "vendor chat response.model" if live else "",
            "link_id": self.link_id,
            "conversation_id": cid,
            "detail": (
                f"cop-chat attach http={status2} model={model!r}"
                if live else
                f"{kind or 'BROKE'} http={status2} model={model!r}"
            ),
        }


def spec_path_for(paths) -> Path:
    return paths.config(SPEC_NAME)


def key_path_for(paths, spec: dict | None = None) -> Path:
    _ = spec
    return paths.config(KEY_NAME)


def register_cop_rail(registry, adapters: dict, spend_gate=None,
                      src: str | None = None, dst: str | None = None, *,
                      paths=None, spec=None, key_path=None,
                      http=None) -> dict:
    _ = spend_gate
    if spec is None and paths is not None:
        spec = load_spec(spec_path_for(paths) if spec_path_for(paths).exists()
                         else None)
    else:
        spec = merge_spec(spec)
    spec = dict(spec)
    if src:
        spec["src"] = src
    spec = _pin_origin(spec)
    if key_path is None and paths is not None:
        key_path = key_path_for(paths, spec)
    rail = CopRail(key_path, spec, http=http)
    lid = rail.link_id
    if lid not in registry.state():
        registry.register(lid, spec["rail_type"], spec["src"], spec["dst"],
                          policy_rank=int(spec["policy_rank"]))
    registry.attach_probe(lid, rail.probe)
    adapters[lid] = rail
    key = read_key(Path(key_path) if key_path else None)
    return {
        "link_id": lid,
        "rail": rail,
        "spec": spec,
        "key_ok": bool(key),
        "key_last4": redact_key(key) if key else "NO_KEY",
        "key_path": str(key_path) if key_path is not None else None,
        "src": spec["src"],
        "dst": spec["dst"],
    }


def attach_to_kernel(kernel, adapters: dict | None = None, http=None,
                     *, boot_compose: bool = False) -> dict:
    if _ledger_is_authority(kernel) and not boot_compose:
        raise CopRailError(
            "REFUSED",
            "attach_to_kernel refuses authority LINK_REGISTERED until Kernel "
            "boot reattaches probes every boot. Pass boot_compose=True only "
            "from Kernel.__init__.")
    if adapters is None:
        adapters = getattr(kernel, "adapters", None)
        if adapters is None:
            adapters = {}
            kernel.adapters = adapters
    return register_cop_rail(
        kernel.registry, adapters, spend_gate=getattr(kernel, "spend", None),
        paths=kernel.paths, http=http)


def _selftest() -> int:
    import tempfile
    from cosmos_kernel import install, Kernel
    from cosmos_ledger import Ledger
    from cosmos_registry import Registry

    results = []

    def check(label, fn):
        try:
            results.append((label, bool(fn()), ""))
        except Exception as e:  # noqa: BLE001
            results.append((label, False, f"{type(e).__name__}: {e}"))

    td = Path(tempfile.mkdtemp(prefix="cosmos_cop_rail_"))
    root = install(td / "live", tree_id="spike-cop-rail")
    from cosmos_paths import CosmosPaths
    paths = CosmosPaths(root)
    spec = write_spec(paths.config(SPEC_NAME))
    check("spec is CHAT core->docs chat-attach read-only",
          lambda: spec["rail_type"] == "CHAT" and spec["dst"] == DST
          and spec["read_only"] is True and spec["chat_attach_only"] is True)
    check("independence note is kept on the spec",
          lambda: spec["independence_note"] == INDEPENDENCE_NOTE)
    keyp = paths.config(KEY_NAME)
    keyp.write_text("not-a-real-token-xxxx\n", encoding="utf-8")
    calls = []

    def fake_http(method, path, body=None):
        calls.append((method, path, body))
        if method == "POST" and path == "/conversations":
            return 201, {"id": "conv-1"}
        if method == "POST" and path == "/conversations/conv-1/chat":
            return 200, {"model": "gpt-5.6", "message": {"text": "PONG"}}
        return 404, {"error": path}

    rail = CopRail(keyp, spec, http=fake_http)
    ok, detail = rail.probe()
    check("probe binds vendor-emitted model gpt-5.6",
          lambda: ok and rail.last_identity()["model"] == "gpt-5.6"
          and "PONG" in (rail.last_identity().get("body") or ""))
    wrote = rail.dispatch({"verb": "write", "prompt": "draft this doc"})
    check("write verb is REFUSED (read-only)",
          lambda: (not wrote["ok"]) and wrote["kind"] == "REFUSED"
          and wrote["model"] == "")
    check("write does not call Graph",
          lambda: not any("/chat" in str(c[1]) and (c[2] or {}).get("message", {}).get("text") == "draft this doc"
                          for c in calls))
    ask = rail.dispatch({"prompt": "summarise the attached doc",
                         "attachments": [{"name": "notes.docx"}]})
    check("attach/ask binds vendor model and keeps the attachment read-only",
          lambda: ask["ok"] and ask["model"] == "gpt-5.6"
          and any(isinstance(c[2], dict) and c[2].get("attachments")
                  for c in calls))

    def http_401(method, path, body=None):
        return 401, {"error": "nope"}

    r401 = CopRail(keyp, spec, http=http_401).dispatch({"prompt": "x"})
    check("401 is AUTH_REQUIRED with empty model",
          lambda: r401["kind"] == "AUTH_REQUIRED" and r401["model"] == "")

    def http_nomodel(method, path, body=None):
        if path == "/conversations":
            return 201, {"id": "conv-1"}
        return 200, {"message": {"text": "PONG"}}

    bare = CopRail(keyp, spec, http=http_nomodel).dispatch({"prompt": "x"})
    check("live body without vendor model is not a proof",
          lambda: (not bare["ok"]) and bare["model"] == "")

    led = Ledger(td / "n.jsonl", b"k", "core")
    reg = Registry(led)
    rec = register_cop_rail(reg, {}, spec=spec, key_path=keyp, http=fake_http)
    check("register claims cop-chat core->docs",
          lambda: rec["link_id"] == LINK_ID and rec["dst"] == DST)

    k = Kernel(root, worker="cop-rail-selftest")
    before = set(k.registry.state())
    refused = False
    try:
        attach_to_kernel(k, {})
    except CopRailError as e:
        refused = e.kind == "REFUSED"
    check("attach_to_kernel refuses writing Kernel without boot_compose",
          lambda: refused and set(k.registry.state()) == before)

    bad = [(l, e) for l, ok, e in results if not ok]
    for label, ok, err in results:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (cop-chat chat-attach; vendor model bind; "
          "writes REFUSED; independence note kept)"
          % ("PASS" if not bad else "FAIL", len(results)))
    return 0 if not bad else 1


def main() -> int:
    ap = argparse.ArgumentParser(prog="cosmos_cop_rail")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    print(json.dumps({"ok": False, "kind": "BAD_ARGS",
                      "error": "pass --selftest"}, indent=1))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
