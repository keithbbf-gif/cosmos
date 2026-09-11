#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_cursor_rail - COSMOS-native Cursor Cloud Agents rail.

Cursor is named in cosmos_node_rails' docstring and ported ADAPTED
(bts_cursor -> cosmos_rails) but was never in `specs`. This module is the
missing link driver: a Dispatcher-shaped API rail that talks to
https://api.cursor.com with COSMOS's own key.

NOT a BTS wrap. Keith 2026-08-25: COSMOS uses its own clocks/keys; it does not
wrap the legacy Cursor module. Key path is the runtime-root role
`config/cursor_cosmos_key.txt` (never the git tree, never hard-coded, never printed in full).

Does NOT modify COSMOS core (kernel/ledger/sched/service). Kernel.__init__
still does not call register_node_rails (BACKLOG). attach_to_kernel() refuses
to append LINK_REGISTERED to the authority ledger until Kernel boot reattaches
probes every boot (H4). The coding route is core->code, never a model peer
(H3). --gate PASS binds apiKeyName=="Cursor COSMOS 2" (H1). --launch is a
separate verb from --gate (H2).

    from cosmos_cursor_rail import CursorRail, register_cursor_rail
    register_cursor_rail(registry, adapters, spend_gate, paths=kernel.paths)

    py -3.14 cosmos\\cosmos_cursor_rail.py --root V:\\A\\Ai\\COSMOS\\live --gate
    py -3.14 cosmos\\cosmos_cursor_rail.py --selftest

Recipe: docs/research/CURSOR_CLOUD_AGENTS_API_v1.md + docs/CURSOR_LANE.md.
Stage-5: docs/critique/cursor_CRITIQUE_g46.md (HIGH/MED applied this slice).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

SCHEMA = "cosmos-cursor-rail/1"
WORKER = "cosmos-cursor-rail"
LINK_ID = "cursor-api"
BASE = "https://api.cursor.com"
KEY_NAME = "cursor_cosmos_key.txt"
KEY_LEN = 69
SPEC_NAME = "cursor_rail.json"
PROBE_NAME = "cursor_rail_probe.json"
LAUNCH_NAME = "cursor_rail_launch.json"
REPO = "https://github.com/keithbbf-gif/cosmos"
REF = "main"
SRC = "core"
DST = "code"
EXPECTED_KEY_NAME = "Cursor COSMOS 2"
DEFAULT_POLL_S = 15
DEFAULT_TIMEOUT_S = 900
TERMINAL = ("FINISHED", "ERROR", "CANCELLED", "EXPIRED")
RESULT_CAP = 4000
# Cursor Models pool (dashboard: Cursor Grok + Composer). Other Models
# (Opus/Sonnet/GPT/Gemini via Cursor) are a separate Ultra quota.
# Shot 2026-09-09: Cursor Models 7% used; Other Models 73% used; Grok Bot
# weekly 3% (NOT SuperGrok Heavy); on-demand Disabled; Ultra reset Sep 14.
CURSOR_GROK = "grok-4.6"
CURSOR_COMPOSER = "composer-2.5"
CURSOR_MODEL = CURSOR_GROK
CURSOR_SONNET = "claude-sonnet-5"
_CURSOR_GROK_IDS = frozenset({
    "grok-4.6", "grok-4.5",
    "cursor-grok-4.6", "cursor-grok-4.6-high-fast",
})


def pin_cursor_model(raw, *, review: bool = False) -> str:
    """Pin Cloud Agent to the Cursor Models pool.

    Default coding: grok-4.6. Composer 2.5 stays Composer.
    Gitur review=True: Other Models selectable — Sonnet 5 default,
    Opus 5 / Fable 5.1 select. Coding launches still coerce Sonnet→Grok.
    """
    low = str(raw or "").strip().lower()
    if "composer" in low:
        return CURSOR_COMPOSER
    if review:
        if "fable" in low:
            return "claude-fable-5.1"
        if "opus" in low:
            return "claude-opus-5"
        if "sonnet" in low or low.startswith("claude"):
            return CURSOR_SONNET
        return CURSOR_SONNET
    return CURSOR_GROK


class CursorRailError(RuntimeError):
    """kind in {NO_KEY, BAD_SPEC, BAD_ROOT, UNREACHABLE, BROKE, REFUSED}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def default_spec() -> dict:
    """Instance-free defaults. Live overlay is live/config/cursor_rail.json."""
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
        "expected_api_key_name": EXPECTED_KEY_NAME,
        "repo_url": REPO,
        "starting_ref": REF,
        "auto_create_pr": True,
        "work_on_current_branch": False,
        "model": CURSOR_MODEL,
        "poll_s": DEFAULT_POLL_S,
        "timeout_s": DEFAULT_TIMEOUT_S,
        "note": (
            "Cursor Ultra included with SuperGrok Heavy = $0 marginal. "
            "metered_usd=0 so Dispatcher does not spend-gate; RAIL_DISPATCH/"
            "RAIL_RESULT still ledger. Coding rail: src/dst=core->code, never a "
            "model peer. A billed Cloud Agent launch is opt-in dispatch()/"
            "--launch, never probe()/--gate."
        ),
    }


def _pin_origin(spec: dict) -> dict:
    """Fail-closed on vendor origin and COSMOS key file (M5). Coerce the
    core->models landmine to core->code (H3)."""
    base = str(spec.get("base") or BASE).rstrip("/")
    if base != BASE:
        raise CursorRailError(
            "BAD_SPEC",
            f"base {base!r} != {BASE!r} (vendor origin only; pin is documented)")
    spec["base"] = BASE
    kn = str(spec.get("key_name") or KEY_NAME)
    if kn != KEY_NAME:
        raise CursorRailError(
            "BAD_SPEC",
            f"key_name {kn!r} != {KEY_NAME!r} (COSMOS key file is pinned)")
    spec["key_name"] = KEY_NAME
    spec["expected_api_key_name"] = EXPECTED_KEY_NAME
    src = str(spec.get("src") or SRC)
    dst = str(spec.get("dst") or DST)
    if dst == "models":
        spec["route_note"] = (
            f"coerced {src}->{dst} to {SRC}->{DST} (H3: coding rail, not a "
            "model peer)")
        src, dst = SRC, DST
    spec["src"] = src or SRC
    spec["dst"] = dst or DST
    if spec["src"] == "core" and spec["dst"] == "models":
        raise CursorRailError(
            "BAD_SPEC",
            "cursor-api is a coding rail (core->code); refusing core->models")
    return spec


def merge_spec(overlay) -> dict:
    spec = default_spec()
    if overlay is None:
        return _pin_origin(spec)
    if not isinstance(overlay, dict):
        raise CursorRailError("BAD_SPEC", f"spec overlay is {type(overlay).__name__}")
    for k, v in overlay.items():
        spec[k] = v
    if spec.get("schema") != SCHEMA:
        raise CursorRailError(
            "BAD_SPEC",
            f"spec schema {spec.get('schema')!r} != {SCHEMA}")
    if spec.get("rail_type") != "API":
        raise CursorRailError(
            "BAD_SPEC",
            f"cursor rail_type must be API, got {spec.get('rail_type')!r}")
    link = str(spec.get("link_id") or "").strip()
    if not link:
        raise CursorRailError("BAD_SPEC", "link_id is required")
    spec["link_id"] = link
    spec["metered_usd"] = float(spec.get("metered_usd") or 0.0)
    spec["budget_usd"] = float(spec.get("budget_usd") or 0.0)
    spec["policy_rank"] = int(spec.get("policy_rank") or 0)
    spec["poll_s"] = int(spec.get("poll_s") or DEFAULT_POLL_S)
    spec["timeout_s"] = int(spec.get("timeout_s") or DEFAULT_TIMEOUT_S)
    spec["auto_create_pr"] = bool(spec.get("auto_create_pr", True))
    spec["work_on_current_branch"] = bool(spec.get("work_on_current_branch", False))
    return _pin_origin(spec)


def load_spec(path: Path | None) -> dict:
    if path is None or not Path(path).exists():
        return default_spec()
    try:
        raw = Path(path).read_text(encoding="utf-8")
    except OSError as e:
        raise CursorRailError("BAD_SPEC", f"unreadable spec {path}: {e}") from e
    try:
        overlay = json.loads(raw)
    except ValueError as e:
        raise CursorRailError("BAD_SPEC", f"unparseable spec {path}: {e}") from e
    return merge_spec(overlay)


def write_spec(path: Path, spec: dict | None = None) -> dict:
    """Write the runtime spec. Never includes the secret."""
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
        return f"crsr_…{k[-4:]}"
    return "crsr_…????"


def read_key(key_path: Path | None) -> str:
    if key_path is None:
        raise CursorRailError(
            "NO_KEY",
            f"Cursor COSMOS key path not supplied (want runtime-root "
            f"config/{KEY_NAME}; never hard-code)")
    p = Path(key_path)
    if not p.exists():
        raise CursorRailError(
            "NO_KEY",
            f"Cursor COSMOS key missing at {p} (never hard-code; "
            f"redact to crsr_…last4)")
    try:
        text = p.read_text(encoding="utf-8").strip()
    except OSError as e:
        raise CursorRailError("NO_KEY", f"unreadable key {p}: {e}") from e
    if not text.startswith("crsr_") or len(text) != KEY_LEN:
        raise CursorRailError(
            "NO_KEY",
            f"key at {p} does not look like a Cursor key "
            f"(want crsr_ + 64, len={KEY_LEN}, got len={len(text)})")
    return text


def identity_matches(name, http) -> tuple[bool, str]:
    """PASS predicate for the decided identity (H1)."""
    if http != 200:
        return False, f"http={http}"
    if not name:
        return False, "missing apiKeyName"
    if "BTS" in str(name):
        return False, f"BTS identity {name!r} (never Cursor BTS / Cursor BTS 2)"
    if name != EXPECTED_KEY_NAME:
        return False, f"mismatch apiKeyName={name!r} != {EXPECTED_KEY_NAME!r}"
    return True, "ok"


def _real_http(base: str, key: str, method: str, path: str, body, timeout_s: float):
    """The one HTTP helper. Bearer. Callers do not grow a second urllib stack."""
    url = base + path
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(
        url, method=method, data=data,
        headers={
            "Authorization": "Bearer " + key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as r:  # noqa: S310
            raw = r.read().decode("utf-8") or "{}"
            headers = {k.lower(): v for k, v in r.headers.items()}
            try:
                obj = json.loads(raw)
            except ValueError:
                obj = {"raw": raw[:400]}
            return int(r.status), headers, obj
    except urllib.error.HTTPError as e:
        raw = (e.read() or b"").decode("utf-8", "replace")
        try:
            obj = json.loads(raw) if raw else {"error": str(e)}
        except ValueError:
            obj = {"error": raw[:400]}
        headers = {k.lower(): v for k, v in (e.headers or {}).items()}
        return int(e.code), headers, obj
    except Exception as e:  # noqa: BLE001
        return -1, {}, {"error": f"{type(e).__name__}: {e}"}


def _lift_git(run_obj: dict) -> dict:
    """Promote DHx recipe fields out of git.branches[0] (M4)."""
    git = (run_obj or {}).get("git") or {}
    branches = git.get("branches") if isinstance(git, dict) else None
    first = branches[0] if isinstance(branches, list) and branches else {}
    if not isinstance(first, dict):
        first = {}
    return {
        "pr_url": first.get("prUrl"),
        "branch": first.get("branch"),
        "repo_url": first.get("repoUrl"),
    }


class CursorRail:
    """Dispatcher adapter. kind=API. probe() is GET /v1/me (cheap, proven).
    dispatch() is POST /v1/agents + optional poll — a billed/quota run; never
    called by probe or --gate. Registered core->code, not core->models."""
    kind = "API"

    def __init__(self, key_path: Path | str | None, spec: dict | None = None,
                 http=None):
        self.spec = merge_spec(spec)
        self.key_path = Path(key_path) if key_path is not None else None
        self.metered_usd = float(self.spec.get("metered_usd") or 0.0)
        self._http = http
        self.link_id = self.spec["link_id"]
        self._last_me = None

    def _call(self, method: str, path: str, body=None):
        key = read_key(self.key_path)
        if self._http is not None:
            return self._http(method, path, body)
        timeout = min(60, int(self.spec.get("timeout_s") or 60))
        return _real_http(self.spec["base"], key, method, path, body, timeout)

    def key_last4(self) -> str:
        try:
            return redact_key(read_key(self.key_path))
        except CursorRailError:
            return "crsr_…????"

    def last_identity(self):
        return self._last_me

    def probe(self):
        """Cheapest liveness: GET /v1/me. Never launches an agent.
        Fail-closed unless apiKeyName is exactly 'Cursor COSMOS 2' (H1)."""
        try:
            read_key(self.key_path)
        except CursorRailError as e:
            return False, f"UNREACHABLE: {e.kind}: {e}"
        try:
            status, headers, body = self._call("GET", "/v1/me")
        except Exception as e:  # noqa: BLE001
            return False, f"UNREACHABLE: probe raised {type(e).__name__}: {e}"
        self._last_me = {"http": status, "headers": headers or {}, "body": body}
        name = None
        if isinstance(body, dict):
            name = body.get("apiKeyName")
        date = (headers or {}).get("date", "")
        ok, why = identity_matches(name, status)
        if ok:
            return True, (
                f"cursor-api live apiKeyName={name} http=200 "
                f"date={date} key={self.key_last4()}")
        err = ""
        if isinstance(body, dict):
            err = str(body.get("error") or body.get("message") or "")[:200]
        return False, (
            f"UNREACHABLE: GET /v1/me identity {why}"
            + (f" {err}" if err else ""))

    def _create_body(self, payload: dict) -> dict:
        text = payload.get("prompt") or payload.get("text") or ""
        if not str(text).strip():
            raise CursorRailError("BROKE", "dispatch payload.prompt is required")
        body = {
            "prompt": {"text": str(text)},
            "repos": [{
                "url": payload.get("repo_url") or self.spec["repo_url"],
                "startingRef": payload.get("starting_ref")
                or self.spec["starting_ref"],
            }],
            "autoCreatePR": bool(payload.get(
                "auto_create_pr", self.spec["auto_create_pr"])),
            "workOnCurrentBranch": bool(payload.get(
                "work_on_current_branch",
                self.spec["work_on_current_branch"])),
        }
        name = payload.get("name")
        if name:
            body["name"] = str(name)[:100]
        model = payload.get("model") or self.spec.get("model") or CURSOR_MODEL
        if isinstance(model, str):
            model = pin_cursor_model(
                model, review=bool(payload.get("review")))
        body["model"] = {"id": model} if isinstance(model, str) else model
        mode = payload.get("mode")
        if mode:
            body["mode"] = mode
        return body

    def dispatch(self, payload: dict) -> dict:
        """Launch a Cloud Agent run. Opt-in. probe() never calls this."""
        payload = payload or {}
        try:
            read_key(self.key_path)
        except CursorRailError as e:
            return {"ok": False, "kind": "UNREACHABLE",
                    "detail": f"{e.kind}: {e}", "node": self.link_id}
        try:
            body = self._create_body(payload)
        except CursorRailError as e:
            return {"ok": False, "kind": "BROKE",
                    "detail": str(e), "node": self.link_id}
        try:
            status, _headers, created = self._call("POST", "/v1/agents", body)
        except Exception as e:  # noqa: BLE001
            return {"ok": False, "kind": "UNREACHABLE",
                    "detail": f"POST /v1/agents raised {type(e).__name__}: {e}",
                    "node": self.link_id}
        if not isinstance(created, dict):
            created = {"error": str(created)[:200]}
        agent = created.get("agent") or {}
        run = created.get("run") or {}
        aid = agent.get("id") or created.get("id")
        rid = run.get("id") or created.get("latestRunId") or agent.get("latestRunId")
        if status not in (200, 201) or not aid:
            kind = "UNREACHABLE" if status in (-1, 401, 403, 404) else "BROKE"
            return {"ok": False, "kind": kind,
                    "detail": f"POST /v1/agents HTTP {status} {created.get('error', '')}"[:300],
                    "http": status, "node": self.link_id}
        if not rid:
            return {"ok": False, "kind": "BROKE",
                    "detail": "POST /v1/agents returned no run.id (unpollable create)",
                    "http": status, "agent_id": aid, "node": self.link_id}
        rec = {
            "ok": True, "kind": "API", "node": self.link_id,
            "http": status, "agent_id": aid, "run_id": rid,
            "text": "", "usd": None, "provenance": "UNPRICED",
            "pr_url": None, "branch": None, "repo_url": None,
            "result_truncated": False,
        }
        do_poll = bool(payload.get("poll", True))
        if not do_poll:
            rec["text"] = f"launched {aid} run={rid} status={run.get('status')}"
            rec["run"] = {"id": rid, "status": run.get("status")}
            rec.update(_lift_git(run if isinstance(run, dict) else {}))
            return rec
        t0 = time.time()
        timeout_s = float(payload.get("timeout_s") or self.spec["timeout_s"])
        poll_s = float(payload.get("poll_s") or self.spec["poll_s"])
        deadline = t0 + max(1.0, timeout_s - 5.0)
        last = run
        while time.time() < deadline:
            s3, _h, last = self._call("GET", f"/v1/agents/{aid}/runs/{rid}")
            if not isinstance(last, dict):
                last = {"status": None, "error": str(last)[:200]}
            last["http"] = s3
            st = last.get("status")
            if st in TERMINAL:
                rec["run"] = {
                    "http": s3, "status": st,
                    "durationMs": last.get("durationMs"),
                    "git": last.get("git"),
                }
                raw = str(last.get("result") or "")
                rec["text"] = raw[:RESULT_CAP]
                rec["result_truncated"] = len(raw) > RESULT_CAP
                rec.update(_lift_git(last))
                rec["ok"] = st == "FINISHED"
                if st != "FINISHED":
                    rec["kind"] = "BROKE"
                    rec["detail"] = f"run {st}"
                rec["secs"] = round(time.time() - t0, 1)
                return rec
            time.sleep(max(0.2, poll_s))
        rec["ok"] = False
        rec["kind"] = "BROKE"
        rec["detail"] = "TIMEOUT_POLLING"
        rec["run"] = {"status": "TIMEOUT_POLLING", "last": last}
        rec["secs"] = round(time.time() - t0, 1)
        return rec


def spec_path_for(paths) -> Path:
    return paths.config(SPEC_NAME)


def key_path_for(paths, spec: dict | None = None) -> Path:
    # M5: key file name is pinned; overlay cannot retarget it.
    _ = spec
    return paths.config(KEY_NAME)


def probe_path_for(paths) -> Path:
    return paths.config(PROBE_NAME)


def launch_path_for(paths) -> Path:
    return paths.config(LAUNCH_NAME)


def _assert_coding_route(spec: dict, src, dst) -> None:
    use_src = src if src is not None else spec.get("src")
    use_dst = dst if dst is not None else spec.get("dst")
    if use_dst == "models" or (use_src == "core" and use_dst == "models"):
        raise CursorRailError(
            "BAD_SPEC",
            "cursor-api is a coding rail (core->code); refusing core->models (H3)")


def register_cursor_rail(registry, adapters: dict, spend_gate=None,
                         src: str | None = None, dst: str | None = None, *,
                         paths=None, spec=None, key_path=None,
                         http=None) -> dict:
    """Register cursor-api into a Registry + adapter map. Missing key ->
    still registered; probe records UNREACHABLE (registration is not capability).
    Does not write the authority ledger unless `registry` is the live one.
    Route is core->code. Explicit core->models is refused (H3).
    """
    if spec is None and paths is not None:
        spec = load_spec(spec_path_for(paths))
    else:
        spec = merge_spec(spec)
    _assert_coding_route(spec, src, dst)
    spec = dict(spec)
    if src:
        spec["src"] = src
    if dst:
        spec["dst"] = dst
    spec = _pin_origin(spec)
    if key_path is None and paths is not None:
        key_path = key_path_for(paths, spec)
    rail = CursorRail(key_path, spec, http=http)
    lid = rail.link_id
    if lid not in registry.state():
        registry.register(lid, spec["rail_type"], spec["src"], spec["dst"],
                          policy_rank=int(spec["policy_rank"]))
    registry.attach_probe(lid, rail.probe)
    adapters[lid] = rail
    metered = float(spec["metered_usd"]) > 0 or float(spec["budget_usd"]) > 0
    if spend_gate is not None and metered:
        try:
            spend_gate.set_budget(
                lid, float(spec["budget_usd"] or spec["metered_usd"]))
        except Exception as e:  # noqa: BLE001
            raise CursorRailError(
                "BROKE", f"set_budget failed for {lid}: {e}") from e
    key_ok = False
    last4 = "crsr_…????"
    try:
        last4 = redact_key(read_key(Path(key_path) if key_path else None))
        key_ok = True
    except CursorRailError:
        key_ok = False
    return {
        "link_id": lid,
        "rail": rail,
        "spec": spec,
        "key_ok": key_ok,
        "key_last4": last4,
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
    """Additive compose onto an already-built Kernel. Does not edit kernel.py.

    H4: refuses to append LINK_REGISTERED to the authority ledger unless
    `boot_compose=True` (Kernel.__init__ reattaches probes every boot — BACKLOG).
    Isolated --gate ledgers are not authority and are the only legal compose
    until that hole is closed.
    """
    if _ledger_is_authority(kernel) and not boot_compose:
        raise CursorRailError(
            "REFUSED",
            "attach_to_kernel refuses authority LINK_REGISTERED until Kernel "
            "boot reattaches probes every boot (BACKLOG). Isolated --gate "
            "ledger only. Pass boot_compose=True only from Kernel.__init__.")
    if adapters is None:
        adapters = getattr(kernel, "adapters", None)
        if adapters is None:
            adapters = {}
            kernel.adapters = adapters
    return register_cursor_rail(
        kernel.registry, adapters, spend_gate=getattr(kernel, "spend", None),
        paths=kernel.paths, http=http)


def refuse_live_authority_attach(paths) -> dict:
    """Prove H4 against THIS tree's authority path without writing it.

    Builds a duck with the resolver-verified authority.jsonl path. The
    refusal + tree_id + ledger path are a live-tree value. Does not open a
    writing Kernel and does not append.
    """
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
    except CursorRailError as e:
        rec["refused"] = e.kind == "REFUSED"
        rec["kind"] = e.kind
        rec["detail"] = str(e)
    return rec


def inspect_live_kernel(root) -> dict:
    """Read-only Kernel: is cursor-api in the production registry? Optional
    extra proof. A lock/refusal here must not invent a PASS."""
    out = {"opened": False, "cursor_in_registry": None, "error": None}
    try:
        from cosmos_kernel import Kernel
        k = Kernel(root, worker="cursor-rail-gate", read_only=True)
        out["opened"] = True
        out["tree_id"] = k.paths.sentinel.tree_id
        out["cursor_in_registry"] = "cursor-api" in k.registry.state()
        out["read_only"] = True
    except Exception as e:  # noqa: BLE001
        out["error"] = f"{type(e).__name__}: {e}"
    return out


def _iso_now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _compose_isolated(paths, spec, keyp, http):
    from cosmos_ledger import Ledger
    from cosmos_registry import Registry
    from cosmos_rails import Dispatcher
    from cosmos_spend import SpendGate

    adapters = {}
    gate_dir = paths.role("state", "cursor_rail")
    gate_dir.mkdir(parents=True, exist_ok=True)
    led = Ledger(gate_dir / "gate.jsonl", b"cursor-rail-gate", WORKER)
    reg = Registry(led)
    spend = SpendGate(led)
    attached = register_cursor_rail(
        reg, adapters, spend_gate=spend, spec=spec, key_path=keyp, http=http)
    disp = Dispatcher(reg, adapters, led, spend=spend)
    return attached, adapters, disp, led, gate_dir


def gate(root: str | os.PathLike, *, http=None) -> dict:
    """Runtime-binding gate for the Cursor rail.

    Composes Registry + Dispatcher on an ISOLATED ledger under
    state/cursor_rail/ (never authority.jsonl). probe() hits live GET /v1/me
    unless `http` is injected. Does not POST /v1/agents (H2: launch is a
    separate verb).

    PASS iff live_value.apiKeyName == 'Cursor COSMOS 2' and http == 200
    and the authority ledger was not written. Constructor flags and isolated
    event-*name* existence are not the predicate (M2, L5). rc=0 is not the
    proof; config/cursor_rail_probe.json is.
    """
    from cosmos_paths import CosmosPaths

    paths = CosmosPaths(root)
    spec = load_spec(spec_path_for(paths))
    write_spec(spec_path_for(paths), spec)
    keyp = key_path_for(paths, spec)
    attached, adapters, disp, led, gate_dir = _compose_isolated(
        paths, spec, keyp, http)
    # One GET /v1/me: Registry.probe calls rail.probe(); identity is cached
    # on the rail (L1). Do not GET again for the proof file.
    try:
        measured_rec = disp.registry.probe(attached["link_id"])
    except Exception as e:  # noqa: BLE001
        measured_rec = {"ok": False, "detail": f"{type(e).__name__}: {e}"}
    rail = adapters[attached["link_id"]]
    ident = rail.last_identity()
    if ident is None and attached["key_ok"]:
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
        "authority_ledger_written": False,
        "kernel_attached": False,
        "launch": False,
        "live_value": None,
        "gate": "FAIL",
        "stage6": {
            "kind": "satellite",
            "kernel_attach": "BACKLOG",
            "predicate": (
                f"apiKeyName=={EXPECTED_KEY_NAME!r} AND http==200 AND "
                f"route {SRC}->{DST} AND attach refused on authority"
            ),
        },
    }
    me_http = None
    me_body = None
    me_date = None
    if ident:
        me_http = ident.get("http")
        me_body = ident.get("body")
        me_date = (ident.get("headers") or {}).get("date")
    if isinstance(me_body, dict):
        rec["me"] = {
            "http": me_http,
            "date": me_date,
            "apiKeyName": me_body.get("apiKeyName"),
            "userId": me_body.get("userId"),
            "createdAt": me_body.get("createdAt"),
        }
        rec["live_value"] = {
            "apiKeyName": me_body.get("apiKeyName"),
            "http": me_http,
            "date": me_date,
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
    live_name = (rec.get("live_value") or {}).get("apiKeyName")
    live_http = (rec.get("live_value") or {}).get("http")
    id_ok, id_why = identity_matches(live_name, live_http)
    rec["identity_ok"] = id_ok
    rec["identity_why"] = id_why
    route_ok = rec["route"] == f"{SRC}->{DST}"
    attach_refused = bool(rec["attach_refusal"].get("refused"))
    not_in_kernel = rec["live_kernel"].get("cursor_in_registry") is not True
    if (rec["probe_ok"] and id_ok and route_ok and attach_refused
            and not rec["authority_ledger_written"]
            and rec["kernel_attached"] is False
            and not_in_kernel):
        rec["gate"] = "PASS"
    rec["proof"] = (
        f"cursor-api probe_ok={rec['probe_ok']} "
        f"apiKeyName={live_name!r} http={live_http} "
        f"date={(rec.get('live_value') or {}).get('date')!r} "
        f"key={rec['key_last4']} tree_id={rec['tree_id']} "
        f"route={rec['route']} attach_refused={attach_refused} "
        f"kernel_attached={rec['kernel_attached']}"
    )
    rec["dispatcher_class"] = type(disp).__name__
    probe_path = probe_path_for(paths)
    written = write_probe_record(probe_path, rec)
    written["probe_path"] = str(probe_path)
    gate_json = gate_dir / "gate.json"
    write_probe_record(gate_json, written)
    written["gate_json"] = str(gate_json)
    return written


def launch_run(root: str | os.PathLike, prompt: str, *, http=None,
               poll: bool = True) -> dict:
    """OPT-IN Cloud Agent launch. Not --gate (H2). rc follows dispatch['ok'].
    Never writes gate=PASS. Isolated Dispatcher ledgers RAIL_DISPATCH /
    RAIL_RESULT on state/cursor_rail/ (not authority). cosmos_dispatch kind
    cursor should call run_coding_dispatch (M1; this slice cannot edit
    cosmos_dispatch.py).
    """
    from cosmos_paths import CosmosPaths
    from cosmos_rails import RailError

    if not str(prompt or "").strip():
        rec = {
            "ok": False, "kind": "BROKE",
            "launch_error": "launch requested without prompt",
            "gate": None, "launch": False,
        }
        return rec
    paths = CosmosPaths(root)
    spec = load_spec(spec_path_for(paths))
    keyp = key_path_for(paths, spec)
    attached, adapters, disp, led, gate_dir = _compose_isolated(
        paths, spec, keyp, http)
    # Registration is not capability. Isolated compose has no LIVE row until
    # probe. Skipping this was NO_LIVE_LINK on every --launch, so Cursor
    # Cloud Agents never started and Gitur credits did not move.
    try:
        disp.registry.probe(attached["link_id"])
    except Exception as e:  # noqa: BLE001
        rec_fail = {
            "ok": False, "kind": "UNREACHABLE",
            "launch_error": f"probe-before-launch: {type(e).__name__}: {e}"[:200],
            "gate": None, "launch": True,
        }
        return rec_fail
    payload = {"prompt": prompt, "poll": poll}
    rec = {
        "schema": SCHEMA,
        "worker": WORKER,
        "launched_at": _iso_now(),
        "root": str(paths.root),
        "tree_id": paths.sentinel.tree_id,
        "link_id": attached["link_id"],
        "key_last4": attached["key_last4"],
        "route": f"{attached['src']}->{attached['dst']}",
        "gate": None,
        "launch": True,
        "ok": False,
        "authority_ledger_written": False,
        "kernel_attached": False,
    }
    try:
        launched = disp.dispatch(SRC, DST, payload)
    except RailError as e:
        launched = {"ok": False, "kind": e.kind, "detail": str(e)}
    rec["ok"] = bool(launched.get("ok"))
    rec["dispatch"] = {
        "ok": launched.get("ok"),
        "kind": launched.get("kind"),
        "agent_id": launched.get("agent_id"),
        "run_id": launched.get("run_id"),
        "detail": launched.get("detail"),
        "pr_url": launched.get("pr_url"),
        "branch": launched.get("branch"),
        "repo_url": launched.get("repo_url"),
        "run_status": (launched.get("run") or {}).get("status"),
        "text_head": (launched.get("text") or "")[:400],
    }
    try:
        rec["isolated_ledger_events"] = [e.get("event") for e in led.verify()]
    except Exception as e:  # noqa: BLE001
        rec["ledger_error"] = f"{type(e).__name__}: {e}"
    rec["isolated_ledger"] = str(gate_dir / "gate.jsonl")
    written = write_probe_record(launch_path_for(paths), rec)
    written["launch_path"] = str(launch_path_for(paths))
    return written


def run_coding_dispatch(root, prompt: str, *, poll: bool = True,
                        http=None, extra: dict | None = None) -> dict:
    """The one Cloud Agent launcher. cosmos_dispatch._cursor_job should import
    and call this instead of its embedded urllib/poll loop (M1). This slice
    cannot edit cosmos_dispatch.py; the helper is the collapse point.
    """
    payload = dict(extra or {})
    payload["prompt"] = prompt
    payload.setdefault("poll", poll)
    from cosmos_paths import CosmosPaths
    paths = CosmosPaths(root)
    spec = load_spec(spec_path_for(paths))
    rail = CursorRail(key_path_for(paths, spec), spec, http=http)
    return rail.dispatch(payload)


def _selftest() -> int:
    """Isolated. Fake HTTP. No live key, no live POST, no authority ledger."""
    import tempfile
    import types

    from cosmos_kernel import install, Kernel
    from cosmos_ledger import Ledger
    from cosmos_registry import Registry
    from cosmos_rails import Dispatcher, RailError
    from cosmos_spend import SpendGate

    results = []

    def check(label, fn):
        try:
            results.append((label, bool(fn()), ""))
        except Exception as e:  # noqa: BLE001
            results.append((label, False, f"{type(e).__name__}: {e}"))

    check("Cursor Models pin is native Grok 4.6; Composer stays if named",
          lambda: pin_cursor_model("claude-opus-5") == CURSOR_GROK
          and pin_cursor_model("auto") == CURSOR_GROK
          and pin_cursor_model("composer-2.5") == CURSOR_COMPOSER
          and pin_cursor_model("grok-4.6") == CURSOR_GROK)
    check("Gitur review=True unlocks Cursor Other Models Sonnet/Opus/Fable",
          lambda: pin_cursor_model("claude-sonnet-5", review=True) == CURSOR_SONNET
          and pin_cursor_model("claude-opus-5", review=True) == "claude-opus-5"
          and pin_cursor_model("claude-fable-5.1", review=True) == "claude-fable-5.1")

    td = Path(tempfile.mkdtemp(prefix="cosmos_cursor_rail_"))
    root = install(td / "live", tree_id="spike-cursor-rail")
    from cosmos_paths import CosmosPaths
    paths = CosmosPaths(root)
    keyp = paths.config(KEY_NAME)
    dummy = "crsr_" + ("a" * 60) + "31ab"
    assert len(dummy) == KEY_LEN
    keyp.write_text(dummy, encoding="utf-8")
    spec = write_spec(paths.config(SPEC_NAME))

    me_body = {
        "apiKeyName": EXPECTED_KEY_NAME,
        "userId": 405041965,
        "userEmail": "keith.bbf@gmail.com",
    }
    created = {
        "agent": {"id": "bc-test", "status": "ACTIVE", "latestRunId": "run-test"},
        "run": {"id": "run-test", "agentId": "bc-test", "status": "CREATING"},
    }
    finished = {
        "id": "run-test", "agentId": "bc-test", "status": "FINISHED",
        "result": "ALIVE via cursor-api", "durationMs": 12,
        "git": {"branches": [{"repoUrl": "github.com/keithbbf-gif/cosmos",
                              "branch": "cursor/test",
                              "prUrl": "https://github.com/keithbbf-gif/cosmos/pull/1"}]},
    }
    calls = []

    def fake_http(method, path, body=None):
        calls.append((method, path, body))
        headers = {"date": "Wed, 26 Aug 2026 03:00:00 GMT"}
        if method == "GET" and path == "/v1/me":
            return 200, headers, me_body
        if method == "POST" and path == "/v1/agents":
            return 201, headers, created
        if method == "GET" and "/runs/" in path:
            return 200, headers, finished
        return 404, headers, {"error": path}

    missing = CursorRail(td / "no-such-key.txt", spec, http=fake_http)
    mok, mdetail = missing.probe()
    check("missing key probe is UNREACHABLE (registration is not capability)",
          lambda: (not mok) and "UNREACHABLE" in mdetail and "NO_KEY" in mdetail)
    check("missing key dispatch is typed UNREACHABLE",
          lambda: missing.dispatch({"prompt": "x"})["kind"] == "UNREACHABLE")

    rail = CursorRail(keyp, spec, http=fake_http)
    ok, detail = rail.probe()
    check("probe GET /v1/me 200 with apiKeyName is live",
          lambda: ok and EXPECTED_KEY_NAME in detail and "http=200" in detail)
    check("probe never POSTs /v1/agents",
          lambda: all(c[0] != "POST" for c in calls))
    check("never GET /v1/repositories",
          lambda: all("/v1/repositories" not in (c[1] or "") for c in calls))
    check("key last4 redacts (no full secret)",
          lambda: rail.key_last4() == "crsr_…31ab")

    def http_401(method, path, body=None):
        return 401, {}, {"error": "unauthorized"}
    dead = CursorRail(keyp, spec, http=http_401)
    dok, ddet = dead.probe()
    check("HTTP 401 probe is UNREACHABLE, not a crash",
          lambda: (not dok) and "UNREACHABLE" in ddet and "401" in ddet)

    def http_bts(method, path, body=None):
        headers = {"date": "Wed, 26 Aug 2026 03:00:00 GMT"}
        if method == "GET" and path == "/v1/me":
            return 200, headers, {**me_body, "apiKeyName": "Cursor BTS 2"}
        return 404, headers, {"error": path}
    bts_ok, bts_det = CursorRail(keyp, spec, http=http_bts).probe()
    check("H1 probe rejects Cursor BTS 2",
          lambda: (not bts_ok) and "BTS" in bts_det)
    g_bts = gate(root, http=http_bts)
    check("H1 gate FAIL on Cursor BTS 2",
          lambda: g_bts["gate"] == "FAIL" and g_bts.get("identity_ok") is False)

    toy = td / "toy_key.txt"
    toy.write_text("crsr_short12", encoding="utf-8")
    check("H1/L2 12-char toy is NO_KEY",
          lambda: _raises_kind(lambda: read_key(toy), "NO_KEY"))

    check("M5 base example.invalid is BAD_SPEC",
          lambda: _raises_kind(lambda: merge_spec({
              "schema": SCHEMA, "rail_type": "API", "link_id": LINK_ID,
              "base": "https://example.invalid",
          }), "BAD_SPEC"))
    check("M5 key_name retarget is BAD_SPEC",
          lambda: _raises_kind(lambda: merge_spec({
              "schema": SCHEMA, "rail_type": "API", "link_id": LINK_ID,
              "key_name": "bts_cursor_key.txt",
          }), "BAD_SPEC"))
    coerced = merge_spec({
        "schema": SCHEMA, "rail_type": "API", "link_id": LINK_ID,
        "src": "core", "dst": "models",
    })
    check("H3 overlay core->models is coerced to core->code",
          lambda: coerced["src"] == SRC and coerced["dst"] == DST)

    calls.clear()
    out = rail.dispatch({"prompt": "hello", "poll": True, "poll_s": 0.2,
                         "timeout_s": 5})
    check("dispatch POSTs /v1/agents",
          lambda: any(c[0] == "POST" and c[1] == "/v1/agents" for c in calls))
    check("dispatch poll returns FINISHED text",
          lambda: out["ok"] and out["text"] == "ALIVE via cursor-api"
          and out["agent_id"] == "bc-test")
    check("M4 dispatch lifts pr_url / branch",
          lambda: out.get("pr_url") == "https://github.com/keithbbf-gif/cosmos/pull/1"
          and out.get("branch") == "cursor/test")
    check("create body uses COSMOS repo + autoCreatePR",
          lambda: any(
              c[0] == "POST" and c[2] and c[2]["repos"][0]["url"] == REPO
              and c[2]["autoCreatePR"] is True for c in calls))
    check("empty prompt is BROKE, not a launch",
          lambda: rail.dispatch({"prompt": ""})["kind"] == "BROKE")

    def http_norid(method, path, body=None):
        headers = {"date": "Wed, 26 Aug 2026 03:00:00 GMT"}
        if method == "GET" and path == "/v1/me":
            return 200, headers, me_body
        if method == "POST" and path == "/v1/agents":
            return 201, headers, {"agent": {"id": "bc-test"}, "run": {}}
        return 404, headers, {"error": path}
    norid = CursorRail(keyp, spec, http=http_norid).dispatch(
        {"prompt": "x", "poll": True})
    check("M3 create without run.id is BROKE",
          lambda: (not norid["ok"]) and norid["kind"] == "BROKE"
          and "run.id" in (norid.get("detail") or ""))

    led = Ledger(td / "n.jsonl", b"k", "core")
    reg = Registry(led)
    adapters = {}
    rec = register_cursor_rail(
        reg, adapters, spend_gate=SpendGate(led), spec=spec,
        key_path=keyp, http=fake_http)
    check("register_cursor_rail claims cursor-api",
          lambda: rec["link_id"] == "cursor-api" and "cursor-api" in reg.state())
    check("register route is core->code not core->models",
          lambda: rec["src"] == SRC and rec["dst"] == DST)
    check("H3 explicit core->models register is BAD_SPEC",
          lambda: _raises_kind(lambda: register_cursor_rail(
              Registry(Ledger(td / "bad.jsonl", b"k", "core")),
              {}, spec=spec, key_path=keyp, http=fake_http,
              src="core", dst="models"), "BAD_SPEC"))
    reg.probe_all()
    disp = Dispatcher(reg, adapters, led, spend=SpendGate(led))
    calls.clear()
    models_err = None
    try:
        disp.dispatch("core", "models",
                      {"prompt": "hi", "poll": True, "poll_s": 0.2, "timeout_s": 5})
        models_posted = any(c[0] == "POST" for c in calls)
    except RailError as e:
        models_err = e
        models_posted = any(c[0] == "POST" for c in calls)
    check("H3 Dispatcher core->models does not POST /v1/agents",
          lambda: models_err is not None and models_err.kind == "NO_LIVE_LINK"
          and models_posted is False)
    routed = disp.dispatch("core", "code",
                           {"prompt": "route me", "poll": True, "poll_s": 0.2,
                            "timeout_s": 5})
    check("dispatcher reaches cursor-api on core->code",
          lambda: routed["ok"] and routed["text"] == "ALIVE via cursor-api")
    check("RAIL_DISPATCH + RAIL_RESULT ledgered (even at $0 marginal)",
          lambda: {e["event"] for e in led.verify()} >= {
              "LINK_REGISTERED", "PROBE_RESULT", "RAIL_DISPATCH", "RAIL_RESULT"})

    spec_txt = paths.config(SPEC_NAME).read_text(encoding="utf-8")
    check("spec file has no crsr_ secret",
          lambda: dummy not in spec_txt and "crsr_" not in spec_txt)
    g = gate(root, http=fake_http)
    check("gate PASS on injected live /v1/me with bound identity",
          lambda: g["gate"] == "PASS"
          and g["live_value"]["apiKeyName"] == EXPECTED_KEY_NAME)
    check("gate writes probe file under config/",
          lambda: Path(g["probe_path"]).exists() and Path(g["probe_path"]).name == PROBE_NAME)
    probe_txt = Path(g["probe_path"]).read_text(encoding="utf-8")
    check("probe file redacts key and does not bake the secret",
          lambda: dummy not in probe_txt and "crsr_…31ab" in probe_txt)
    check("L4 probe file has no userEmail",
          lambda: "userEmail" not in probe_txt and "keith.bbf@" not in probe_txt)
    check("gate does not write the authority ledger",
          lambda: g["authority_ledger_written"] is False)
    check("gate does not claim Kernel attach",
          lambda: g["kernel_attached"] is False)
    check("gate did not launch a Cloud Agent",
          lambda: g["launch"] is False)
    check("gate route is core->code",
          lambda: g.get("route") == f"{SRC}->{DST}")
    check("H4 attach_to_kernel refused live-shaped authority",
          lambda: g["attach_refusal"]["refused"] is True
          and g["attach_refusal"]["kind"] == "REFUSED")
    check("M2 PASS does not use dispatcher_composed",
          lambda: "dispatcher_composed" not in g
          and g.get("dispatcher_constructed") is True)

    def http_post_500(method, path, body=None):
        headers = {"date": "Wed, 26 Aug 2026 03:00:00 GMT"}
        if method == "GET" and path == "/v1/me":
            return 200, headers, me_body
        if method == "POST" and path == "/v1/agents":
            return 500, headers, {"error": "nope"}
        return 404, headers, {"error": path}
    launched_fail = launch_run(root, "x", http=http_post_500, poll=True)
    check("H2 --launch POST 500 is not gate=PASS",
          lambda: launched_fail.get("gate") is None
          and launched_fail.get("ok") is False
          and launched_fail.get("launch") is True)
    g_ok = gate(root, http=http_post_500)
    check("H2 --gate still PASSes identity when launch is not requested",
          lambda: g_ok["gate"] == "PASS" and g_ok["launch"] is False)

    k = Kernel(root, worker="cursor-rail-selftest")
    ad = {}
    # Boot legitimately composes this rail (Kernel.rails_compose passes
    # boot_compose=True), so "the link is absent" stopped being true and this
    # check went red without the guard ever weakening. The property that matters
    # is that the REFUSED attach registered nothing NEW -- compare the registry
    # across the refusal instead of assuming it starts empty. (2026-08-30)
    _before = set(k.registry.state())
    refused = False
    try:
        attach_to_kernel(k, ad, http=fake_http)
    except CursorRailError as e:
        refused = e.kind == "REFUSED"
    check("H4 attach_to_kernel on writing Kernel refuses without boot_compose",
          lambda: refused and set(k.registry.state()) == _before)
    att = attach_to_kernel(k, ad, http=fake_http, boot_compose=True)
    check("attach_to_kernel(boot_compose=True) still registers (BACKLOG hook)",
          lambda: att["link_id"] in k.registry.state() and att["link_id"] in ad)

    check("default metered_usd is 0 (included lane, unpriced != spend)",
          lambda: float(spec["metered_usd"]) == 0.0)
    check("default src/dst is core/code",
          lambda: spec["src"] == SRC and spec["dst"] == DST)

    _ = types

    bad = [(l, e) for l, ok, e in results if not ok]
    for label, ok, err in results:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (cursor-api is a COSMOS coding rail; "
          "probe=/v1/me identity-bound; dispatch=opt-in POST /v1/agents; "
          "core->code; secret never baked)"
          % ("PASS" if not bad else "FAIL", len(results)))
    return 0 if not bad else 1


def _raises_kind(fn, kind: str) -> bool:
    try:
        fn()
    except CursorRailError as e:
        return e.kind == kind
    return False


def main() -> int:
    ap = argparse.ArgumentParser(
        prog="cosmos_cursor_rail",
        description="COSMOS Cursor Cloud Agents rail. probe is cheap; "
                    "dispatch launches. --gate is the runtime-binding proof. "
                    "--launch is a separate verb (quota).")
    ap.add_argument("--root", default=None,
                    help="COSMOS runtime root (resolver-verified). Required for --gate.")
    ap.add_argument("--gate", action="store_true",
                    help="compose isolated Registry+Dispatcher, live GET /v1/me, "
                         "write config/cursor_rail_probe.json. Does not launch.")
    ap.add_argument("--probe", action="store_true",
                    help="probe only (same live GET /v1/me, no isolated ledger).")
    ap.add_argument("--selftest", action="store_true",
                    help="isolated fake-HTTP checks; no live network.")
    ap.add_argument("--launch", default=None, metavar="PROMPT",
                    help="OPT-IN Cloud Agent POST /v1/agents. Spends quota. "
                         "Separate from --gate. Refuse to guess a prompt.")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if a.gate or a.probe or a.launch is not None:
        if not a.root:
            print(json.dumps({
                "ok": False, "kind": "BAD_ROOT",
                "error": "--root is required (resolver does not guess)",
            }, indent=1))
            return 2
        if a.probe and not a.gate and a.launch is None:
            from cosmos_paths import CosmosPaths
            paths = CosmosPaths(a.root)
            spec = load_spec(spec_path_for(paths))
            rail = CursorRail(key_path_for(paths, spec), spec)
            ok, detail = rail.probe()
            rec = {"ok": ok, "detail": detail, "link_id": rail.link_id,
                   "key_last4": rail.key_last4()}
            ident = rail.last_identity() or {}
            body = ident.get("body") if isinstance(ident.get("body"), dict) else {}
            rec["apiKeyName"] = body.get("apiKeyName")
            rec["http"] = ident.get("http")
            print(json.dumps(rec, indent=1))
            return 0 if ok else 2
        combined = None
        gate_rec = None
        launch_rec = None
        if a.gate:
            gate_rec = gate(a.root)
            combined = dict(gate_rec)
        if a.launch is not None:
            launch_rec = launch_run(a.root, a.launch)
            if combined is None:
                combined = dict(launch_rec)
            else:
                combined["launch"] = True
                combined["dispatch"] = launch_rec.get("dispatch")
                combined["launch_ok"] = launch_rec.get("ok")
                combined["launch_path"] = launch_rec.get("launch_path")
                if not launch_rec.get("ok"):
                    # H2: process must not claim PASS when launch failed.
                    combined["gate"] = "FAIL"
                    combined["gate_note"] = (
                        "launch failed; probe identity recorded but exit is "
                        "not PASS (H2)")
        print(json.dumps(combined, indent=1, default=str, ensure_ascii=False))
        if a.launch is not None and a.gate:
            return 0 if (gate_rec or {}).get("gate") == "PASS" and launch_rec.get("ok") else 2
        if a.launch is not None:
            return 0 if launch_rec.get("ok") else 2
        return 0 if (gate_rec or {}).get("gate") == "PASS" else 2
    ap.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
