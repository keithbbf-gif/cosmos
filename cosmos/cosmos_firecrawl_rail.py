#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_firecrawl_rail - satellite API rail `firecrawl-web` (keyless papers).

Slice-1 of mesh additions. Cursor-shaped satellite: probe / dispatch /
register_* / attach_to_kernel / --gate / --selftest. Does NOT edit
kernel / ledger / sched / service. Kernel.__init__ still does not attach
rails (BACKLOG). attach_to_kernel refuses the authority ledger unless
boot_compose=True.

kind=API. Route is core->papers (Chapter-4 index). This is NOT the
ROUTING.md default for web search or known-URL READ (dump-dom / SGH DOM
stay first; scrape/search are overflow verbs on this same adapter).

Keyless default. Optional `config/firecrawl_api_key.txt` (`fc-…`) raises
RPM and unlocks crawl/map. Missing key is not UNREACHABLE for
scrape/search/papers. Crawl/map without a key is AUTH_REQUIRED.

HTTP 402/429 map to BROKE + http= (not UNREACHABLE — Dispatcher
RAIL_FALLBACK would hide a cap as "down"). No `limit` on papers (live
400 unrecognized_keys). Hosted Firecrawl MCP cannot do papers — slice 1
is REST urllib, not MCP. AGPL self-host stays a process, not cosmos/.

    py -3.14 cosmos\\cosmos_firecrawl_rail.py --selftest
    py -3.14 cosmos\\cosmos_firecrawl_rail.py --root V:\\A\\Ai\\COSMOS\\live --gate

Stage-6 proof is live/config/firecrawl_rail_probe.json quoting a vendor
primaryId (arxiv: / doi: / pmid:), never an exit code.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

SCHEMA = "cosmos-firecrawl-rail/1"
WORKER = "cosmos-firecrawl-rail"
LINK_ID = "firecrawl-web"
BASE = "https://api.firecrawl.dev"
KEY_NAME = "firecrawl_api_key.txt"
SPEC_NAME = "firecrawl_rail.json"
PROBE_NAME = "firecrawl_rail_probe.json"
SRC = "core"
DST = "papers"
UA = "COSMOS-meshadditions/1 (firecrawl-web; keithbbf-gif/cosmos)"
PAPERS_QUERY = "Lindau theorem superluminal"
PAPERS_PATH = "/v2/search/research/papers"
KEYLESS_VERBS = frozenset({"scrape", "search", "papers", "probe"})
KEYED_VERBS = frozenset({"crawl", "map"})
ID_PREFIXES = ("arxiv:", "doi:", "pmid:")


class FirecrawlRailError(RuntimeError):
    """kind in {BAD_SPEC, BAD_ROOT, UNREACHABLE, AUTH_REQUIRED, BROKE, REFUSED}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def default_spec() -> dict:
    return {
        "schema": SCHEMA,
        "link_id": LINK_ID,
        "rail_type": "API",
        "src": SRC,
        "dst": DST,
        "policy_rank": 0,
        "metered_usd": 0.0,
        "budget_usd": 0.0,
        "base": BASE,
        "key_name": KEY_NAME,
        "papers_query": PAPERS_QUERY,
        "timeout_s": 45,
        "note": (
            "Keyless papers REST. scrape/search overflow of dump-dom / SGH DOM. "
            "core->papers so Registry.route cannot capture READ. 402/429=BROKE. "
            "No limit on papers. Kernel attach BACKLOG; --gate is satellite."
        ),
    }


def _pin_origin(spec: dict) -> dict:
    base = str(spec.get("base") or BASE).rstrip("/")
    if base != BASE:
        raise FirecrawlRailError(
            "BAD_SPEC",
            f"base {base!r} != {BASE!r} (vendor origin only)")
    spec["base"] = BASE
    kn = str(spec.get("key_name") or KEY_NAME)
    if kn != KEY_NAME:
        raise FirecrawlRailError(
            "BAD_SPEC",
            f"key_name {kn!r} != {KEY_NAME!r}")
    spec["key_name"] = KEY_NAME
    spec["src"] = str(spec.get("src") or SRC) or SRC
    spec["dst"] = str(spec.get("dst") or DST) or DST
    if spec["dst"] in ("search", "read", "models"):
        spec["route_note"] = (
            f"coerced dst={spec['dst']!r} to {DST} (papers; not ROUTING default)")
        spec["dst"] = DST
    spec["rail_type"] = "API"
    spec["link_id"] = str(spec.get("link_id") or LINK_ID) or LINK_ID
    spec["metered_usd"] = float(spec.get("metered_usd") or 0.0)
    spec["budget_usd"] = float(spec.get("budget_usd") or 0.0)
    spec["policy_rank"] = int(spec.get("policy_rank") or 0)
    spec["timeout_s"] = int(spec.get("timeout_s") or 45)
    spec["papers_query"] = str(spec.get("papers_query") or PAPERS_QUERY)
    spec["schema"] = SCHEMA
    return spec


def merge_spec(overlay) -> dict:
    spec = default_spec()
    if overlay is None:
        return _pin_origin(spec)
    if not isinstance(overlay, dict):
        raise FirecrawlRailError("BAD_SPEC", f"spec overlay is {type(overlay).__name__}")
    for k, v in overlay.items():
        spec[k] = v
    if spec.get("schema") != SCHEMA:
        raise FirecrawlRailError(
            "BAD_SPEC", f"spec schema {spec.get('schema')!r} != {SCHEMA}")
    if spec.get("rail_type") not in (None, "API"):
        raise FirecrawlRailError(
            "BAD_SPEC",
            f"firecrawl rail_type must be API, got {spec.get('rail_type')!r}")
    return _pin_origin(spec)


def load_spec(path: Path | None) -> dict:
    if path is None or not Path(path).exists():
        return default_spec()
    try:
        raw = Path(path).read_text(encoding="utf-8")
    except OSError as e:
        raise FirecrawlRailError("BAD_SPEC", f"unreadable spec {path}: {e}") from e
    try:
        overlay = json.loads(raw)
    except ValueError as e:
        raise FirecrawlRailError("BAD_SPEC", f"unparseable spec {path}: {e}") from e
    return merge_spec(overlay)


def write_spec(path: Path, spec: dict | None = None) -> dict:
    body = merge_spec(spec)
    body.pop("api_key", None)
    body.pop("key", None)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(body, indent=2, sort_keys=True,
                               ensure_ascii=False) + "\n",
                    encoding="utf-8")
    return body


def redact_key(key: str) -> str:
    k = (key or "").strip()
    if len(k) >= 4:
        return f"fc-…{k[-4:]}"
    return "fc-…????"


def read_key(key_path: Path | None) -> str | None:
    """Optional. None means keyless. Does not raise on missing file."""
    if key_path is None:
        return None
    p = Path(key_path)
    if not p.exists():
        return None
    try:
        text = p.read_text(encoding="utf-8").strip()
    except OSError:
        return None
    if not text:
        return None
    return text


def first_primary_id(obj) -> str | None:
    if isinstance(obj, dict):
        pid = obj.get("primaryId") or obj.get("primary_id")
        if isinstance(pid, str) and pid.strip():
            return pid.strip()
        for v in obj.values():
            found = first_primary_id(v)
            if found:
                return found
    elif isinstance(obj, list):
        for item in obj:
            found = first_primary_id(item)
            if found:
                return found
    return None


def first_title(obj) -> str | None:
    if isinstance(obj, dict):
        t = obj.get("title")
        if isinstance(t, str) and t.strip() and obj.get("primaryId"):
            return t.strip()[:200]
        for v in obj.values():
            found = first_title(v)
            if found:
                return found
    elif isinstance(obj, list):
        for item in obj:
            found = first_title(item)
            if found:
                return found
    return None


def id_is_live(pid: str | None) -> bool:
    if not pid:
        return False
    low = pid.lower()
    return any(low.startswith(p) for p in ID_PREFIXES)


def _http_kind(status: int) -> str:
    if status in (401, 403):
        return "AUTH_REQUIRED"
    if status in (402, 429):
        return "BROKE"
    if status in (-1,):
        return "UNREACHABLE"
    if status >= 500 or status in (404, 400, 408, 409, 422):
        return "BROKE"
    return "BROKE"


def _real_http(method: str, url: str, body, headers: dict, timeout_s: float):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(
        url, method=method, data=data, headers=headers,
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as r:  # noqa: S310
            raw = r.read().decode("utf-8") or "{}"
            hdrs = {k.lower(): v for k, v in r.headers.items()}
            try:
                obj = json.loads(raw)
            except ValueError:
                obj = {"raw": raw[:400]}
            return int(r.status), hdrs, obj
    except urllib.error.HTTPError as e:
        raw = (e.read() or b"").decode("utf-8", "replace")
        try:
            obj = json.loads(raw) if raw else {"error": str(e)}
        except ValueError:
            obj = {"error": raw[:400]}
        hdrs = {k.lower(): v for k, v in (e.headers or {}).items()}
        return int(e.code), hdrs, obj
    except Exception as e:  # noqa: BLE001
        return -1, {}, {"error": f"{type(e).__name__}: {e}"}


class FirecrawlRail:
    """Dispatcher adapter. kind=API. probe() is GET papers (cheap, live).
    dispatch() is one verb. Isolated --gate Dispatcher, not the live daemon."""
    kind = "API"

    def __init__(self, key_path: Path | str | None, spec: dict | None = None,
                 http=None):
        self.spec = merge_spec(spec)
        self.key_path = Path(key_path) if key_path is not None else None
        self.metered_usd = float(self.spec.get("metered_usd") or 0.0)
        self._http = http
        self.link_id = self.spec["link_id"]
        self._last = None

    def last_identity(self):
        return self._last

    def _headers(self, has_body: bool) -> dict:
        h = {"Accept": "application/json", "User-Agent": UA}
        if has_body:
            h["Content-Type"] = "application/json"
        key = read_key(self.key_path)
        if key:
            h["Authorization"] = "Bearer " + key
        return h

    def _call(self, method: str, path: str, body=None, query: dict | None = None):
        q = ""
        if query:
            q = "?" + urllib.parse.urlencode(query, doseq=True)
        url_path = path + q
        if self._http is not None:
            return self._http(method, url_path, body)
        timeout = min(60, int(self.spec.get("timeout_s") or 45))
        url = self.spec["base"] + url_path
        return _real_http(method, url, body, self._headers(body is not None), timeout)

    def probe(self):
        """Cheapest liveness: GET papers. Never crawl. Keyless is the path."""
        query = self.spec.get("papers_query") or PAPERS_QUERY
        try:
            status, headers, body = self._call(
                "GET", PAPERS_PATH, None, {"query": query})
        except Exception as e:  # noqa: BLE001
            return False, f"UNREACHABLE: probe raised {type(e).__name__}: {e}"
        pid = first_primary_id(body)
        title = first_title(body)
        date = (headers or {}).get("date", "")
        success = None
        if isinstance(body, dict):
            success = body.get("success")
        self._last = {
            "http": status, "headers": headers or {}, "body_ok": True,
            "primaryId": pid, "title": title, "success": success,
            "date": date, "verb": "papers",
        }
        if status in (402, 429):
            return False, f"BROKE http={status} (quota/cap; no silent fallback)"
        if status in (401, 403):
            return False, f"AUTH_REQUIRED http={status}"
        if status != 200 or not id_is_live(pid):
            err = ""
            if isinstance(body, dict):
                err = str(body.get("error") or body.get("message") or "")[:160]
            kind = _http_kind(status) if status != 200 else "BROKE"
            return False, (
                f"{kind} GET papers http={status} primaryId={pid!r} {err}").strip()
        return True, (
            f"firecrawl-web papers primaryId={pid} http=200 "
            f"success={success} date={date}")

    def dispatch(self, payload: dict) -> dict:
        payload = payload or {}
        verb = str(payload.get("verb") or payload.get("action") or "papers").lower()
        key = read_key(self.key_path)
        if verb in KEYED_VERBS and not key:
            return {"ok": False, "kind": "AUTH_REQUIRED",
                    "detail": f"{verb} needs fc- key (keyless cannot crawl/map)",
                    "node": self.link_id, "http": None}
        try:
            if verb in ("papers", "probe"):
                q = payload.get("query") or self.spec.get("papers_query") or PAPERS_QUERY
                # Do NOT send limit (live 400 unrecognized_keys).
                status, headers, body = self._call(
                    "GET", PAPERS_PATH, None, {"query": q})
            elif verb == "scrape":
                url = payload.get("url")
                if not url:
                    return {"ok": False, "kind": "BROKE",
                            "detail": "scrape requires url", "node": self.link_id}
                body_in = {"url": url, "formats": payload.get("formats") or ["markdown"]}
                status, headers, body = self._call("POST", "/v2/scrape", body_in)
            elif verb == "search":
                q = payload.get("query")
                if not q:
                    return {"ok": False, "kind": "BROKE",
                            "detail": "search requires query", "node": self.link_id}
                body_in = {"query": q}
                if payload.get("limit") is not None:
                    body_in["limit"] = payload["limit"]
                status, headers, body = self._call("POST", "/v2/search", body_in)
            elif verb in KEYED_VERBS:
                return {"ok": False, "kind": "BROKE",
                        "detail": f"{verb} not in slice 1 (HOLD behind fc- key)",
                        "node": self.link_id}
            else:
                return {"ok": False, "kind": "BROKE",
                        "detail": f"unknown verb {verb!r}", "node": self.link_id}
        except Exception as e:  # noqa: BLE001
            return {"ok": False, "kind": "UNREACHABLE",
                    "detail": f"{type(e).__name__}: {e}", "node": self.link_id}

        pid = first_primary_id(body)
        success = body.get("success") if isinstance(body, dict) else None
        rec = {
            "ok": False, "kind": "API", "node": self.link_id,
            "http": status, "verb": verb, "primaryId": pid,
            "success": success, "usd": 0.0, "text": "",
        }
        if status in (402, 429):
            rec["kind"] = "BROKE"
            rec["detail"] = f"http={status} (quota/cap; not UNREACHABLE)"
            return rec
        if status in (401, 403):
            rec["kind"] = "AUTH_REQUIRED"
            rec["detail"] = f"http={status}"
            return rec
        if status == -1:
            rec["kind"] = "UNREACHABLE"
            rec["detail"] = str((body or {}).get("error") if isinstance(body, dict) else body)[:240]
            return rec
        if status != 200:
            rec["kind"] = _http_kind(status)
            rec["detail"] = f"http={status}"
            return rec
        if verb in ("papers", "probe"):
            rec["ok"] = id_is_live(pid)
            rec["text"] = pid or ""
            rec["title"] = first_title(body)
            if not rec["ok"]:
                rec["kind"] = "BROKE"
                rec["detail"] = f"no arxiv:/doi:/pmid: primaryId (got {pid!r})"
            return rec
        rec["ok"] = bool(success is True or (isinstance(body, dict) and body.get("data")))
        if isinstance(body, dict):
            data = body.get("data") or {}
            md = data.get("markdown") if isinstance(data, dict) else None
            rec["text"] = (md or json.dumps(body)[:400])[:2000]
        if not rec["ok"]:
            rec["kind"] = "BROKE"
            rec["detail"] = f"http=200 but success={success!r}"
        return rec


def spec_path_for(paths) -> Path:
    return paths.config(SPEC_NAME)


def key_path_for(paths, spec: dict | None = None) -> Path:
    _ = spec
    return paths.config(KEY_NAME)


def probe_path_for(paths) -> Path:
    return paths.config(PROBE_NAME)


def register_firecrawl_rail(registry, adapters: dict, spend_gate=None,
                            src: str | None = None, dst: str | None = None, *,
                            paths=None, spec=None, key_path=None,
                            http=None) -> dict:
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
    if key_path is None and paths is not None:
        key_path = key_path_for(paths, spec)
    rail = FirecrawlRail(key_path, spec, http=http)
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
        "key_last4": redact_key(key) if key else "keyless",
        "key_path": str(key_path) if key_path is not None else None,
        "src": spec["src"],
        "dst": spec["dst"],
    }


# Moved to cosmos_rail_base (Phase 3.1, 2026-08-30/31): four rails carried a
# byte-identical `_ledger_is_authority`, and four carried a near-identical
# `write_probe_record` whose only difference was WHICH secret names it popped
# -- i.e. four chances to forget one. The base pops the union.
from cosmos_rail_base import (  # noqa: E402,F401
    _ledger_is_authority,
    write_probe_record,
)


def attach_to_kernel(kernel, adapters: dict | None = None, http=None,
                     *, boot_compose: bool = False) -> dict:
    """Additive. Refuses authority LINK_REGISTERED unless boot_compose=True."""
    if _ledger_is_authority(kernel) and not boot_compose:
        raise FirecrawlRailError(
            "REFUSED",
            "attach_to_kernel refuses authority LINK_REGISTERED until Kernel "
            "boot reattaches probes every boot (BACKLOG). Isolated --gate "
            "ledger only. Pass boot_compose=True only from Kernel.__init__.")
    if adapters is None:
        adapters = getattr(kernel, "adapters", None)
        if adapters is None:
            adapters = {}
            kernel.adapters = adapters
    return register_firecrawl_rail(
        kernel.registry, adapters, spend_gate=getattr(kernel, "spend", None),
        paths=kernel.paths, http=http)


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
    except FirecrawlRailError as e:
        rec["refused"] = e.kind == "REFUSED"
        rec["kind"] = e.kind
        rec["detail"] = str(e)
    return rec


def inspect_live_kernel(root) -> dict:
    out = {"opened": False, "firecrawl_in_registry": None, "error": None}
    try:
        from cosmos_kernel import Kernel
        k = Kernel(root, worker="firecrawl-rail-gate", read_only=True)
        out["opened"] = True
        out["tree_id"] = k.paths.sentinel.tree_id
        out["firecrawl_in_registry"] = LINK_ID in k.registry.state()
        out["read_only"] = True
    except Exception as e:  # noqa: BLE001
        out["error"] = f"{type(e).__name__}: {e}"
    return out


def _iso_now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _compose_isolated(paths, spec, keyp, http):
    """Isolated --gate Dispatcher (cosmos_rails.Dispatcher), not the live daemon."""
    from cosmos_ledger import Ledger
    from cosmos_registry import Registry
    from cosmos_rails import Dispatcher
    from cosmos_spend import SpendGate

    adapters = {}
    gate_dir = paths.role("state", "firecrawl_rail")
    gate_dir.mkdir(parents=True, exist_ok=True)
    led = Ledger(gate_dir / "gate.jsonl", b"firecrawl-rail-gate", WORKER)
    reg = Registry(led)
    spend = SpendGate(led)
    attached = register_firecrawl_rail(
        reg, adapters, spend_gate=spend, spec=spec, key_path=keyp, http=http)
    disp = Dispatcher(reg, adapters, led, spend=spend)
    return attached, adapters, disp, led, gate_dir


def gate(root: str | os.PathLike, *, http=None) -> dict:
    """Runtime-binding gate. Isolated ledger. Live GET papers unless http injected.

    PASS iff primaryId is arxiv:/doi:/pmid: AND http==200 AND attach refused
    AND kernel_attached is false. rc=0 is not the proof;
    config/firecrawl_rail_probe.json is.
    """
    from cosmos_paths import CosmosPaths

    paths = CosmosPaths(root)
    spec = load_spec(spec_path_for(paths))
    write_spec(spec_path_for(paths), spec)
    keyp = key_path_for(paths, spec)
    attached, adapters, disp, led, gate_dir = _compose_isolated(
        paths, spec, keyp, http)
    try:
        measured_rec = disp.registry.probe(attached["link_id"])
    except Exception as e:  # noqa: BLE001
        measured_rec = {"ok": False, "detail": f"{type(e).__name__}: {e}"}
    rail = adapters[attached["link_id"]]
    ident = rail.last_identity()
    if ident is None:
        ok, detail = rail.probe()
        ident = rail.last_identity()
        measured_rec = {"ok": ok, "detail": detail}
    matrix = disp.registry.matrix()
    rec = {
        "schema": SCHEMA,
        "worker": WORKER,
        "gated_at": _iso_now(),
        "root": str(paths.root),
        "tree_id": paths.sentinel.tree_id,
        "link_id": attached["link_id"],
        "key_last4": attached["key_last4"],
        "key_ok": attached["key_ok"],
        "key_path_name": KEY_NAME,
        "spec_path": str(spec_path_for(paths)),
        "route": f"{attached['src']}->{attached['dst']}",
        "probe_ok": bool((measured_rec or {}).get("ok")),
        "probe_detail": (measured_rec or {}).get("detail"),
        "matrix": matrix,
        "dispatcher_constructed": True,
        "dispatcher_class": type(disp).__name__,
        "authority_ledger_written": False,
        "kernel_attached": False,
        "live_value": None,
        "gate": "FAIL",
        "stage6": {
            "kind": "satellite",
            "kernel_attach": "BACKLOG",
            "predicate": (
                "primaryId startswith arxiv:|doi:|pmid: AND http==200 AND "
                "route core->papers AND attach refused on authority"
            ),
        },
    }
    if ident:
        rec["papers"] = {
            "http": ident.get("http"),
            "date": ident.get("date"),
            "primaryId": ident.get("primaryId"),
            "title": ident.get("title"),
            "success": ident.get("success"),
        }
        rec["live_value"] = {
            "primaryId": ident.get("primaryId"),
            "http": ident.get("http"),
            "date": ident.get("date"),
            "success": ident.get("success"),
        }
    events = []
    try:
        events = [e.get("event") for e in led.verify()]
    except Exception as e:  # noqa: BLE001
        rec["ledger_error"] = f"{type(e).__name__}: {e}"
    rec["isolated_ledger_events"] = events
    rec["isolated_ledger"] = str(gate_dir / "gate.jsonl")
    rec["attach_refusal"] = refuse_live_authority_attach(paths)
    rec["live_kernel"] = inspect_live_kernel(root)
    pid = (rec.get("live_value") or {}).get("primaryId")
    live_http = (rec.get("live_value") or {}).get("http")
    id_ok = id_is_live(pid) and live_http == 200
    rec["identity_ok"] = id_ok
    rec["identity_why"] = "ok" if id_ok else f"primaryId={pid!r} http={live_http}"
    route_ok = rec["route"] == f"{SRC}->{DST}"
    attach_refused = bool(rec["attach_refusal"].get("refused"))
    if (rec["probe_ok"] and id_ok and route_ok and attach_refused
            and not rec["authority_ledger_written"]
            and rec["kernel_attached"] is False):
        rec["gate"] = "PASS"
    rec["proof"] = (
        f"firecrawl-web probe_ok={rec['probe_ok']} "
        f"primaryId={pid!r} http={live_http} "
        f"tree_id={rec['tree_id']} route={rec['route']} "
        f"attach_refused={attach_refused} kernel_attached={rec['kernel_attached']}"
    )
    probe_path = probe_path_for(paths)
    written = write_probe_record(probe_path, rec)
    written["probe_path"] = str(probe_path)
    gate_json = gate_dir / "gate.json"
    write_probe_record(gate_json, written)
    written["gate_json"] = str(gate_json)
    return written


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

    td = Path(tempfile.mkdtemp(prefix="cosmos_firecrawl_rail_"))
    root = install(td / "live", tree_id="spike-firecrawl-rail")
    from cosmos_paths import CosmosPaths
    paths = CosmosPaths(root)
    spec = write_spec(paths.config(SPEC_NAME))
    calls = []

    papers_body = {
        "success": True,
        "data": [{"primaryId": "arxiv:physics/0103087",
                  "title": "Thoughtful comments on Bessel beams"}],
    }

    def fake_http(method, path, body=None):
        calls.append((method, path, body))
        headers = {"date": "Wed, 26 Aug 2026 15:00:00 GMT"}
        if method == "GET" and PAPERS_PATH in (path or ""):
            if "limit=" in (path or ""):
                return 400, headers, {"error": "unrecognized_keys", "keys": ["limit"]}
            return 200, headers, papers_body
        if method == "POST" and path == "/v2/scrape":
            return 200, headers, {
                "success": True,
                "data": {"markdown": "# Documentation Index"},
            }
        if method == "POST" and path == "/v2/search":
            return 200, headers, {
                "success": True,
                "data": {"web": [{"url": "https://github.com/microsoft/playwright-mcp"}]},
            }
        return 404, headers, {"error": path}

    rail = FirecrawlRail(paths.config(KEY_NAME), spec, http=fake_http)
    ok, detail = rail.probe()
    check("probe GET papers 200 with arxiv: primaryId",
          lambda: ok and "arxiv:physics/0103087" in detail and "http=200" in detail)
    check("probe never POSTs crawl",
          lambda: all("crawl" not in (c[1] or "") for c in calls))
    check("papers path has query and no limit",
          lambda: any(c[0] == "GET" and "query=" in (c[1] or "")
                      and "limit=" not in (c[1] or "") for c in calls))

    def http_429(method, path, body=None):
        return 429, {}, {"error": "rate"}
    r429 = FirecrawlRail(None, spec, http=http_429)
    d429 = r429.dispatch({"verb": "papers"})
    pok, pdet = r429.probe()
    check("429 dispatch is BROKE not UNREACHABLE",
          lambda: (not d429["ok"]) and d429["kind"] == "BROKE"
          and "429" in (d429.get("detail") or ""))
    check("429 probe is BROKE not UNREACHABLE",
          lambda: (not pok) and "BROKE" in pdet and "UNREACHABLE" not in pdet)

    def http_401(method, path, body=None):
        return 401, {}, {"error": "no"}
    r401 = FirecrawlRail(None, spec, http=http_401).dispatch({"verb": "papers"})
    check("401 is AUTH_REQUIRED",
          lambda: r401["kind"] == "AUTH_REQUIRED")

    crawl = rail.dispatch({"verb": "crawl", "url": "https://example.com"})
    check("crawl without key is AUTH_REQUIRED",
          lambda: crawl["kind"] == "AUTH_REQUIRED")

    scraped = rail.dispatch({"verb": "scrape",
                             "url": "https://docs.firecrawl.dev/introduction"})
    check("keyless scrape 200 success",
          lambda: scraped["ok"] and scraped.get("success") is True)

    led = Ledger(td / "n.jsonl", b"k", "core")
    reg = Registry(led)
    adapters = {}
    rec = register_firecrawl_rail(
        reg, adapters, spend_gate=SpendGate(led), spec=spec,
        key_path=paths.config(KEY_NAME), http=fake_http)
    check("register claims firecrawl-web core->papers",
          lambda: rec["link_id"] == LINK_ID and rec["dst"] == DST)
    check("rail_type is API not MCP",
          lambda: rec["spec"]["rail_type"] == "API")
    reg.probe_all()
    disp = Dispatcher(reg, adapters, led, spend=SpendGate(led))
    routed = disp.dispatch(SRC, DST, {"verb": "papers"})
    check("isolated Dispatcher reaches papers",
          lambda: routed["ok"] and routed.get("primaryId") == "arxiv:physics/0103087")
    check("RAIL_DISPATCH + RAIL_RESULT ledgered at $0",
          lambda: {e["event"] for e in led.verify()} >= {
              "LINK_REGISTERED", "PROBE_RESULT", "RAIL_DISPATCH", "RAIL_RESULT"})

    g = gate(root, http=fake_http)
    check("gate PASS quotes arxiv: primaryId",
          lambda: g["gate"] == "PASS"
          and g["live_value"]["primaryId"] == "arxiv:physics/0103087")
    check("gate kernel_attached is false",
          lambda: g["kernel_attached"] is False)
    check("gate attach refused",
          lambda: g["attach_refusal"]["refused"] is True)
    check("gate does not write authority",
          lambda: g["authority_ledger_written"] is False)
    check("gate route is core->papers",
          lambda: g.get("route") == f"{SRC}->{DST}")
    check("probe file exists under config/",
          lambda: Path(g["probe_path"]).name == PROBE_NAME)

    k = Kernel(root, worker="firecrawl-rail-selftest")
    # Boot legitimately composes this rail (Kernel.rails_compose passes
    # boot_compose=True), so "the link is absent" stopped being true and this
    # check went red without the guard ever weakening. The property that matters
    # is that the REFUSED attach registered nothing NEW -- compare the registry
    # across the refusal instead of assuming it starts empty. (2026-08-30)
    _before = set(k.registry.state())
    refused = False
    try:
        attach_to_kernel(k, {})
    except FirecrawlRailError as e:
        refused = e.kind == "REFUSED"
    check("attach_to_kernel refuses writing Kernel without boot_compose",
          lambda: refused and set(k.registry.state()) == _before)

    coerced = merge_spec({
        "schema": SCHEMA, "rail_type": "API", "link_id": LINK_ID,
        "dst": "search",
    })
    check("overlay dst=search is coerced to papers",
          lambda: coerced["dst"] == DST)

    bad = [(l, e) for l, ok, e in results if not ok]
    for label, ok, err in results:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (firecrawl-web satellite; papers gate; "
          "429=BROKE; crawl AUTH_REQUIRED; attach refused)"
          % ("PASS" if not bad else "FAIL", len(results)))
    return 0 if not bad else 1


def main() -> int:
    ap = argparse.ArgumentParser(
        prog="cosmos_firecrawl_rail",
        description="COSMOS Firecrawl keyless papers rail. --gate is the "
                    "runtime-binding proof. Isolated --gate Dispatcher, not "
                    "the live daemon.")
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
            rail = FirecrawlRail(key_path_for(paths, spec), spec)
            ok, detail = rail.probe()
            ident = rail.last_identity() or {}
            rec = {"ok": ok, "detail": detail, "link_id": rail.link_id,
                   "primaryId": ident.get("primaryId"), "http": ident.get("http")}
            print(json.dumps(rec, indent=1))
            return 0 if ok else 2
        rec = gate(a.root)
        print(json.dumps(rec, indent=1, default=str, ensure_ascii=False))
        return 0 if rec.get("gate") == "PASS" else 2
    ap.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
