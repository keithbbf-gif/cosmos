#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_copilot_rail - satellite `github-copilot` (Copilot cloud agent).

GitHub Copilot cloud SWE agent. Credit-metered. Surfaces:
  GET  https://api.github.com/agents/tasks          (cheap identity; never spends)
  POST https://api.github.com/agents/repos/{o}/{r}/tasks  (create; spends credits)
  CLI  `gh agent-task list|create` (preview wrapper; create is the same spend)

User-to-server token only (PAT / OAuth / App user token). Installation
tokens (`ghs_`) are REFUSED. Probe is GET /agents/tasks — never POST,
never `gh agent-task create`. A billed launch is opt-in dispatch() only.

Vendor-emitted prove: HTTP 200 + JSON `tasks` array + header
`x-ratelimit-resource=mission_control` (Agent Tasks / Mission Control).
The responder name `copilot-swe-agent` is emitted ONLY on that live
triple — a spec file cannot produce the header. USD rate is UNMEASURED
(GitHub AI credits, not a COSMOS rate card); do not read 0 as free.

Coding rail: src/dst=core->code. Never forge (github-forge keeps gh
issues/PRs). attach_to_kernel refuses authority LINK_REGISTERED unless
boot_compose=True. Compose row only — boot does not invoke.

    py -3.14 cosmos\\cosmos_copilot_rail.py --selftest
    py -3.14 cosmos\\cosmos_copilot_rail.py --root V:\\A\\Ai\\COSMOS\\live --probe
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cosmos_rail_base import (  # noqa: E402
    RailError as RailSeamError,
    _ledger_is_authority,
    _real_run,
    _real_which,
    write_probe_record,
)

SCHEMA = "cosmos-copilot-rail/1"
WORKER = "cosmos-copilot-rail"
LINK_ID = "github-copilot"
BASE = "https://api.github.com"
TASKS_PATH = "/agents/tasks"
CREATE_PATH = "/agents/repos/{owner}/{repo}/tasks"
KEY_NAME = "github_agent_token.txt"
SPEC_NAME = "copilot_rail.json"
PROBE_NAME = "copilot_rail_probe.json"
SRC = "core"
DST = "code"
REPO_OWNER = "keithbbf-gif"
REPO_NAME = "cosmos"
RESPONDER = "copilot-swe-agent"
VENDOR_RESOURCE = "mission_control"
API_VERSION = "2022-11-28"
ACCEPT = "application/vnd.github+json"
UA = "COSMOS-copilot-rail/1 (github-copilot; keithbbf-gif/cosmos)"
VENDOR_DOCS = (
    "https://docs.github.com/en/copilot/how-tos/use-copilot-agents/"
    "cloud-agent/use-cloud-agent-via-the-api"
)
VENDOR_REST = (
    "https://docs.github.com/en/rest/agent-tasks/agent-tasks"
    "?apiVersion=2026-03-10"
)
BINARY = "gh"


class CopilotRailError(RailSeamError):
    """kind in {NO_KEY, BAD_SPEC, BAD_ROOT, UNREACHABLE, AUTH_REQUIRED, BROKE, REFUSED}."""


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
        "credit_metered": True,
        "base": BASE,
        "key_name": KEY_NAME,
        "owner": REPO_OWNER,
        "repo": REPO_NAME,
        "timeout_s": 45,
        "vendor_docs": VENDOR_DOCS,
        "vendor_rest": VENDOR_REST,
        "note": (
            "Copilot cloud agent. Credit-metered (GitHub AI credits) — USD "
            "rate UNMEASURED, not $0. Probe is GET /agents/tasks only; "
            "POST /agents/repos/{o}/{r}/tasks and `gh agent-task create` "
            "are opt-in dispatch, never boot. User-to-server token only; "
            "ghs_ installation tokens REFUSED. dst=code, never forge."
        ),
    }


def _pin_origin(spec: dict) -> dict:
    base = str(spec.get("base") or BASE).rstrip("/")
    if base != BASE:
        raise CopilotRailError(
            "BAD_SPEC", f"base {base!r} != {BASE!r} (vendor origin only)")
    spec["base"] = BASE
    kn = str(spec.get("key_name") or KEY_NAME)
    if kn != KEY_NAME:
        raise CopilotRailError(
            "BAD_SPEC", f"key_name {kn!r} != {KEY_NAME!r}")
    spec["key_name"] = KEY_NAME
    src = str(spec.get("src") or SRC) or SRC
    dst = str(spec.get("dst") or DST) or DST
    if dst == "models" or dst == "forge":
        spec["route_note"] = (
            f"coerced {src}->{dst} to {SRC}->{DST} "
            "(coding rail; github-forge keeps forge)")
        src, dst = SRC, DST
    spec["src"] = src or SRC
    spec["dst"] = dst or DST
    if spec["src"] == "core" and spec["dst"] in ("models", "forge"):
        raise CopilotRailError(
            "BAD_SPEC",
            "github-copilot is a coding rail (core->code); "
            "refusing core->models and core->forge")
    spec["rail_type"] = "API"
    spec["link_id"] = str(spec.get("link_id") or LINK_ID) or LINK_ID
    spec["metered_usd"] = float(spec.get("metered_usd") or 0.0)
    spec["budget_usd"] = float(spec.get("budget_usd") or 0.0)
    spec["credit_metered"] = True
    spec["policy_rank"] = int(spec.get("policy_rank") or 0)
    spec["timeout_s"] = int(spec.get("timeout_s") or 45)
    spec["owner"] = str(spec.get("owner") or REPO_OWNER) or REPO_OWNER
    spec["repo"] = str(spec.get("repo") or REPO_NAME) or REPO_NAME
    spec["schema"] = SCHEMA
    spec["vendor_docs"] = VENDOR_DOCS
    spec["vendor_rest"] = VENDOR_REST
    return spec


def merge_spec(overlay) -> dict:
    spec = default_spec()
    if overlay is None:
        return _pin_origin(spec)
    if not isinstance(overlay, dict):
        raise CopilotRailError(
            "BAD_SPEC", f"spec overlay is {type(overlay).__name__}")
    for k, v in overlay.items():
        spec[k] = v
    if spec.get("schema") != SCHEMA:
        raise CopilotRailError(
            "BAD_SPEC", f"spec schema {spec.get('schema')!r} != {SCHEMA}")
    if spec.get("rail_type") not in (None, "API"):
        raise CopilotRailError(
            "BAD_SPEC",
            f"copilot rail_type must be API, got {spec.get('rail_type')!r}")
    return _pin_origin(spec)


def load_spec(path: Path | None) -> dict:
    if path is None or not Path(path).exists():
        return default_spec()
    try:
        raw = Path(path).read_text(encoding="utf-8")
    except OSError as e:
        raise CopilotRailError("BAD_SPEC", f"unreadable spec {path}: {e}") from e
    try:
        overlay = json.loads(raw)
    except ValueError as e:
        raise CopilotRailError("BAD_SPEC", f"unparseable spec {path}: {e}") from e
    return merge_spec(overlay)


def write_spec(path: Path, spec: dict | None = None) -> dict:
    body = merge_spec(spec)
    for k in ("api_key", "key", "token", "github_agent_token",
              "GITHUB_TOKEN", "GH_TOKEN", "COPILOT_GITHUB_TOKEN"):
        body.pop(k, None)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(body, indent=2, sort_keys=True,
                               ensure_ascii=False) + "\n",
                    encoding="utf-8")
    return body


def spec_path_for(paths) -> Path:
    return paths.config(SPEC_NAME)


def key_path_for(paths, spec: dict | None = None) -> Path:
    _ = spec
    return paths.config(KEY_NAME)


def probe_path_for(paths) -> Path:
    return paths.config(PROBE_NAME)


def _is_installation_token(key: str) -> bool:
    return (key or "").strip().startswith("ghs_")


def read_key(key_path: Path | None) -> str | None:
    """Optional COSMOS overlay. Existence read only when the file is present.

    Never prints the value. Installation tokens are REFUSED (vendor rejects
    them on the agent-tasks API; we refuse first so we do not spend a call).
    """
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
    if _is_installation_token(text):
        raise CopilotRailError(
            "REFUSED",
            "installation token (ghs_) rejected — agent-tasks is "
            "user-to-server only")
    return text


def _env_token() -> str | None:
    for name in ("GH_TOKEN", "GITHUB_TOKEN", "COPILOT_GITHUB_TOKEN"):
        val = (os.environ.get(name) or "").strip()
        if val:
            if _is_installation_token(val):
                raise CopilotRailError(
                    "REFUSED",
                    "installation token (ghs_) rejected — agent-tasks is "
                    "user-to-server only")
            return val
    return None


def _http_kind(status: int) -> str:
    if status in (401, 403):
        return "AUTH_REQUIRED"
    if status in (-1, 0):
        return "UNREACHABLE"
    return "BROKE"


def _real_http(method: str, url: str, body, headers: dict, timeout_s: float):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, method=method, data=data, headers=headers)
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


def _parse_gh_api_i(text: str) -> tuple[int, dict, object]:
    """Parse `gh api -i` (headers + body). Color is not expected; still strip none."""
    raw = text or ""
    split = raw.find("\r\n\r\n")
    sep_len = 4
    if split < 0:
        split = raw.find("\n\n")
        sep_len = 2
    if split < 0:
        try:
            return 200, {}, json.loads(raw)
        except ValueError:
            return -1, {}, {"error": "unparseable gh api reply"}
    head, body = raw[:split], raw[split + sep_len:]
    status = -1
    hdrs: dict[str, str] = {}
    for i, line in enumerate(head.splitlines()):
        line = line.strip()
        if i == 0 and line.upper().startswith("HTTP/"):
            parts = line.split()
            if len(parts) >= 2 and parts[1].isdigit():
                status = int(parts[1])
            continue
        if ":" in line:
            k, v = line.split(":", 1)
            hdrs[k.strip().lower()] = v.strip()
    try:
        obj = json.loads(body) if body.strip() else {}
    except ValueError:
        obj = {"raw": body[:400]}
    if status < 0:
        status = 200 if isinstance(obj, (dict, list)) else -1
    return status, hdrs, obj


def _tasks_list(obj) -> list:
    if isinstance(obj, list):
        return obj
    if isinstance(obj, dict) and isinstance(obj.get("tasks"), list):
        return obj["tasks"]
    return []


class CopilotRail:
    """Dispatcher adapter. kind=API. probe=GET /agents/tasks. create=opt-in POST."""

    kind = "API"

    def __init__(self, key_path: Path | str | None, spec: dict | None = None,
                 http=None, run=None, which=None):
        self.spec = merge_spec(spec)
        self.key_path = Path(key_path) if key_path is not None else None
        self.metered_usd = float(self.spec.get("metered_usd") or 0.0)
        self._http = http
        self._run = run or _real_run
        self._which = which or _real_which
        self.link_id = self.spec["link_id"]
        self._last = None

    def last_identity(self) -> dict | None:
        return self._last

    def _headers(self, key: str) -> dict:
        return {
            "Authorization": "Bearer " + key,
            "Accept": ACCEPT,
            "X-GitHub-Api-Version": API_VERSION,
            "User-Agent": UA,
        }

    def _call(self, method: str, path: str, body=None):
        if self._http is not None:
            return self._http(method, path, body)
        key = None
        try:
            key = read_key(self.key_path) or _env_token()
        except CopilotRailError:
            raise
        if key:
            url = self.spec["base"] + path
            hdrs = self._headers(key)
            if body is not None:
                hdrs["Content-Type"] = "application/json"
            return _real_http(method, url, body, hdrs,
                              float(self.spec["timeout_s"]))
        found = self._which(BINARY)
        if not found:
            return -1, {}, {"error": "NO_KEY: no user token and gh ABSENT"}
        argv = [found, "api", "-i",
                "-H", f"Accept: {ACCEPT}",
                "-H", f"X-GitHub-Api-Version: {API_VERSION}",
                "-X", method, path]
        if body is not None:
            argv.extend(["--input", "-"])
            run = self._run(argv, timeout_s=float(self.spec["timeout_s"]),
                            stdin=json.dumps(body))
        else:
            run = self._run(argv, timeout_s=float(self.spec["timeout_s"]))
        if run.get("timed_out"):
            return -1, {}, {"error": "TIMEOUT"}
        status, hdrs, obj = _parse_gh_api_i(run.get("out") or "")
        if status < 0 and run.get("rc") not in (0, None):
            err = (run.get("err") or "")[:200]
            return -1, {}, {"error": err or "gh api failed"}
        return status, hdrs, obj

    def probe(self):
        """Cheap identity. GET /agents/tasks. Never POST. Never create."""
        try:
            status, hdrs, obj = self._call("GET", TASKS_PATH)
        except CopilotRailError as e:
            rec = {"ok": False, "http": 0, "kind": e.kind,
                   "detail": f"{e.kind}: {e}", "bound": "",
                   "n_tasks": 0, "resource": "", "date": ""}
            self._last = rec
            return False, rec["detail"]
        tasks = _tasks_list(obj)
        resource = str((hdrs or {}).get("x-ratelimit-resource") or "")
        date = str((hdrs or {}).get("date") or "")
        rid = str((hdrs or {}).get("x-github-request-id") or "")
        has_tasks_key = (isinstance(obj, dict) and "tasks" in obj) or isinstance(obj, list)
        live = bool(status == 200 and has_tasks_key
                    and resource == VENDOR_RESOURCE and date)
        kind = None if live else _http_kind(status if status != 200 else 0)
        if status == 200 and not live:
            kind = "BROKE"
        rec = {
            "ok": live,
            "http": status,
            "n_tasks": len(tasks),
            "resource": resource,
            "date": date,
            "request_id": rid,
            "bound": RESPONDER if live else "",
            "kind": kind,
            "detail": (
                f"http={status} n={len(tasks)} resource={resource or '—'} "
                f"date={date or '—'}"
            ),
        }
        self._last = rec
        return live, rec["detail"]

    def dispatch(self, payload: dict) -> dict:
        """Identity GET by default. POST create only when payload.create is true.

        A billed cloud-agent launch is opt-in. Probe/boot must never reach POST.
        """
        payload = payload if isinstance(payload, dict) else {}
        if payload.get("create") or payload.get("launch"):
            return self._create(payload)
        argv = payload.get("argv")
        if isinstance(argv, (list, tuple)) and argv:
            joined = " ".join(str(x) for x in argv).lower()
            if "agent-task create" in joined or joined.startswith("create"):
                return {"ok": False, "kind": "REFUSED",
                        "detail": "gh agent-task create is opt-in via "
                                  "payload.create=true, never implicit argv",
                        "link_id": self.link_id}
        ok, detail = self.probe()
        ident = self.last_identity() or {}
        live = bool(ok and ident.get("bound"))
        body = (f"{self.link_id} GET {TASKS_PATH} {detail}"
                if live else "")
        return {
            "ok": live, "rc": 0 if live else 2, "body": body, "text": body,
            "model": ident.get("bound") or "",
            "kind": "API" if live else (ident.get("kind") or "UNREACHABLE"),
            "link_id": self.link_id, "detail": detail,
            "http": ident.get("http"),
        }

    def _create(self, payload: dict) -> dict:
        prompt = str(payload.get("prompt") or payload.get("text") or "").strip()
        if not prompt:
            return {"ok": False, "kind": "REFUSED",
                    "detail": "create requires prompt (credit-metered)",
                    "link_id": self.link_id}
        owner = str(payload.get("owner") or self.spec["owner"])
        repo = str(payload.get("repo") or self.spec["repo"])
        path = CREATE_PATH.format(owner=owner, repo=repo)
        body = {
            "prompt": prompt,
            "base_ref": str(payload.get("base_ref") or payload.get("base")
                            or "main"),
            "create_pull_request": bool(payload.get("create_pull_request", True)),
        }
        if payload.get("model"):
            body["model"] = str(payload["model"])
        status, hdrs, obj = self._call("POST", path, body)
        task_id = ""
        if isinstance(obj, dict):
            task_id = str(obj.get("id") or obj.get("task_id") or "")
        ok = status in (200, 201) and bool(task_id)
        return {
            "ok": ok, "http": status,
            "kind": None if ok else _http_kind(status),
            "model": str((obj or {}).get("model") or "") if isinstance(obj, dict) else "",
            "task_id": task_id,
            "link_id": self.link_id,
            "credit_metered": True,
            "detail": f"POST {path} http={status} task_id={task_id or '—'}",
        }


def register_copilot_rail(registry, adapters: dict, spend_gate=None,
                          src: str | None = None, dst: str | None = None, *,
                          paths=None, spec=None, key_path=None,
                          http=None, run=None, which=None) -> dict:
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
    rail = CopilotRail(key_path, spec, http=http, run=run, which=which)
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
        "credit_metered": True,
    }


def attach_to_kernel(kernel, adapters: dict | None = None, http=None,
                     run=None, which=None, *, boot_compose: bool = False) -> dict:
    if _ledger_is_authority(kernel) and not boot_compose:
        raise CopilotRailError(
            "REFUSED",
            "attach_to_kernel refuses authority LINK_REGISTERED until Kernel "
            "boot reattaches probes every boot. Isolated --gate ledger only. "
            "Pass boot_compose=True only from Kernel.__init__.")
    if adapters is None:
        adapters = getattr(kernel, "adapters", None)
        if adapters is None:
            adapters = {}
            kernel.adapters = adapters
    return register_copilot_rail(
        kernel.registry, adapters, spend_gate=getattr(kernel, "spend", None),
        paths=kernel.paths, http=http, run=run, which=which)


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
    except CopilotRailError as e:
        rec["refused"] = e.kind == "REFUSED"
        rec["kind"] = e.kind
        rec["detail"] = str(e)
    return rec


def _iso_now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _selftest() -> int:
    import tempfile
    from cosmos_kernel import Kernel, install
    from cosmos_ledger import Ledger
    from cosmos_registry import Registry, proof_ok
    from cosmos_rails import Dispatcher

    results = []

    def check(label, fn):
        try:
            results.append((label, bool(fn()), ""))
        except Exception as e:  # noqa: BLE001
            results.append((label, False, f"{type(e).__name__}: {e}"))

    spec = merge_spec(None)
    check("default dst is code, never forge",
          lambda: spec["dst"] == DST and spec["src"] == SRC
          and spec["credit_metered"] is True)
    coerced = merge_spec({"dst": "forge"})
    check("overlay dst=forge is coerced to code",
          lambda: coerced["dst"] == DST and "route_note" in coerced)
    check("unknown schema is BAD_SPEC",
          lambda: _expect_kind(lambda: merge_spec({"schema": "nope"}), "BAD_SPEC"))

    hdrs = {
        "date": "Mon, 14 Sep 2026 20:01:43 GMT",
        "x-ratelimit-resource": VENDOR_RESOURCE,
        "x-github-request-id": "2E0E:234735:probe",
    }

    def http_ok(method, path, body=None):
        if method == "GET" and path == TASKS_PATH:
            return 200, hdrs, {"tasks": []}
        if method == "POST" and path.startswith("/agents/repos/"):
            return 201, hdrs, {"id": "task-1", "model": "gpt-5"}
        return 404, {}, {"error": path}

    rail = CopilotRail(None, spec, http=http_ok)
    ok, detail = rail.probe()
    check("GET /agents/tasks 200 + mission_control binds copilot-swe-agent",
          lambda: ok and rail.last_identity().get("bound") == RESPONDER
          and VENDOR_RESOURCE in detail)
    check("empty tasks[] is still a live vendor answer (n=0 is measured)",
          lambda: rail.last_identity().get("n_tasks") == 0
          and rail.last_identity().get("http") == 200)

    ident = rail.dispatch({})
    check("default dispatch is identity GET, never POST",
          lambda: ident["ok"] is True and RESPONDER in ident["model"]
          and ident["kind"] == "API" and "GET" in ident["body"])

    created = rail.dispatch({"create": True, "prompt": "ping"})
    check("explicit create POSTs and binds task id",
          lambda: created["ok"] is True and created.get("task_id") == "task-1")
    no_prompt = rail.dispatch({"create": True})
    check("create without prompt is REFUSED (no spend)",
          lambda: no_prompt["kind"] == "REFUSED")
    argv_block = rail.dispatch({"argv": ["agent-task", "create", "x"]})
    check("implicit gh agent-task create argv is REFUSED",
          lambda: argv_block["kind"] == "REFUSED")

    def http_no_resource(method, path, body=None):
        return 200, {"date": "d"}, {"tasks": []}

    dead = CopilotRail(None, spec, http=http_no_resource)
    dok, _ = dead.probe()
    check("http=200 without mission_control is NOT a proof",
          lambda: dok is False and not dead.last_identity().get("bound"))

    def http_401(method, path, body=None):
        return 401, {}, {"message": "Bad credentials"}

    r401 = CopilotRail(None, spec, http=http_401)
    eok, edetail = r401.probe()
    check("401 is AUTH_REQUIRED, never ok",
          lambda: eok is False and r401.last_identity().get("kind") == "AUTH_REQUIRED"
          and "401" in edetail)

    td = Path(tempfile.mkdtemp(prefix="cosmos_copilot_rail_"))
    ghs = td / "ghs.txt"
    ghs.write_text("ghs_" + "x" * 20, encoding="utf-8")
    check("ghs_ installation token is REFUSED before the call",
          lambda: _expect_kind(lambda: read_key(ghs), "REFUSED"))

    led = Ledger(td / "n.jsonl", b"k", "core")
    reg = Registry(led)
    adapters = {}
    rec = register_copilot_rail(reg, adapters, spec=spec, http=http_ok)
    check("register claims github-copilot core->code",
          lambda: rec["link_id"] == LINK_ID and rec["dst"] == DST)
    check("registration is not capability (verified is None)",
          lambda: reg.state()[LINK_ID]["claim"]["dst"] == DST)
    reg.probe_all()
    disp = Dispatcher(reg, adapters, led)
    routed = disp.dispatch(SRC, DST, {})
    check("isolated Dispatcher identity-GET binds copilot-swe-agent",
          lambda: routed.get("ok") is True and routed.get("model") == RESPONDER)
    forge_miss = False
    try:
        disp.dispatch(SRC, "forge", {})
    except Exception as e:  # noqa: BLE001
        forge_miss = getattr(e, "kind", None) == "NO_LIVE_LINK"
    check("core->forge does not capture github-copilot", lambda: forge_miss is True)

    proof = {
        "ok": True, "rc": 0,
        "body": f"{LINK_ID} GET {TASKS_PATH} http=200 n=0 resource={VENDOR_RESOURCE}",
        "model": RESPONDER,
    }
    check("prove-shaped record clears proof_ok", lambda: proof_ok(proof))

    root = install(td / "live", tree_id="spike-copilot-rail")
    k = Kernel(root, worker="copilot-rail-selftest")
    _before = set(k.registry.state())
    refused = False
    try:
        attach_to_kernel(k, {})
    except CopilotRailError as e:
        refused = e.kind == "REFUSED"
    check("attach_to_kernel refuses writing Kernel without boot_compose",
          lambda: refused and set(k.registry.state()) == _before)
    composed = list((k.rails_compose or {}).get("composed") or [])
    check("writing Kernel compose includes github-copilot",
          lambda: "github-copilot" in composed)
    check("writing Kernel adapter is dst=code",
          lambda: LINK_ID in k.adapters
          and getattr(k.adapters[LINK_ID], "spec", {}).get("dst") == DST)

    write_spec(td / SPEC_NAME)
    on_disk = (td / SPEC_NAME).read_text(encoding="utf-8")
    check("write_spec never stores a token field",
          lambda: "ghs_" not in on_disk and "token" not in json.loads(on_disk))

    bad = [(l, e) for l, ok, e in results if not ok]
    for label, ok, err in results:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("live_value: " + json.dumps({
        "checks": len(results),
        "dst": DST,
        "link_id": LINK_ID,
        "bound": rail.last_identity().get("bound"),
        "credit_metered": True,
        "composed": "github-copilot" in composed,
    }, sort_keys=True))
    print("SELFTEST %s - %d checks (github-copilot GET /agents/tasks; "
          "mission_control bind; POST create opt-in; attach refused; "
          "Kernel compose)"
          % ("PASS" if not bad else "FAIL", len(results)))
    return 0 if not bad else 1


def _expect_kind(fn, kind: str) -> bool:
    try:
        fn()
    except CopilotRailError as e:
        return e.kind == kind
    return False


def main() -> int:
    ap = argparse.ArgumentParser(prog="cosmos_copilot_rail")
    ap.add_argument("--root", default=None)
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--write-probe", action="store_true")
    ap.add_argument("--write-spec", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if a.probe or a.write_spec or a.write_probe:
        if not a.root:
            print(json.dumps({
                "ok": False, "kind": "BAD_ROOT",
                "error": "--root is required (resolver does not guess)",
            }, indent=1))
            return 2
        from cosmos_paths import CosmosPaths
        paths = CosmosPaths(a.root)
        if a.write_spec:
            write_spec(spec_path_for(paths))
        spec = load_spec(spec_path_for(paths))
        rail = CopilotRail(key_path_for(paths, spec), spec)
        ok, detail = rail.probe()
        ident = rail.last_identity() or {}
        rec = {
            "schema": SCHEMA,
            "ok": ok,
            "detail": detail,
            "http": ident.get("http"),
            "n_tasks": ident.get("n_tasks"),
            "resource": ident.get("resource"),
            "bound": ident.get("bound"),
            "date": ident.get("date"),
            "credit_metered": True,
            "usd_rate": "UNMEASURED",
            "tree_id": paths.sentinel.tree_id,
            "measured_at": _iso_now(),
        }
        if a.write_probe:
            write_probe_record(probe_path_for(paths), rec)
        print(json.dumps(rec, indent=1, default=str))
        return 0 if ok else 1
    print(json.dumps({"ok": False, "kind": "BAD_ARGS",
                      "error": "pass --selftest or --root … --probe"}, indent=1))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
