#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_claude_rail - COSMOS-native Anthropic Claude Code CLI rail.

RANK 1 of docs/research/NEW_AI_DISCOVERY.md: the 7-node mesh has no
Anthropic rail (largest vendor hole). This is the CLI HAND
(`claude -p`), not a BTS wrap and not the metered Messages overflow
(`anthropic-api` / MESH #17).

Primary invocation (print / headless). Prompt on STDIN — a trailing
`--add-dir` swallows a positional prompt (proven 2026-08-25):

  claude -p --model <model> --permission-mode dontAsk --add-dir <workspace>
          --output-format json

DOM-first fallback (documented, not driven here): Claude in Chrome
(GA on direct Anthropic plans). Canon is DOM-first / API-second when
the CLI seat is AUTH_REQUIRED or the weekly window is dry; Playwright
/ cosmos_browser already own Chrome. This module does not launch it.

Key path is the runtime-root role `config/anthropic_api_key.txt`
(never the git tree, never hard-coded, never printed in full; redact
to sk-ant-…last4). Child env UNSETS ANTHROPIC_API_KEY by default so
the prepaid Claude Code seat is used (H5 / ANTHROPIC_HANDS). wallet=api
injects the key (metered overflow, opt-in).

Does NOT modify COSMOS core (kernel/ledger/sched/service).
attach_to_kernel() refuses authority LINK_REGISTERED unless
boot_compose=True (H4). Coding route is core->code (H3). --gate PASS
binds `claude --version` + key-shape; --launch is a separate verb (H2).
done = JSON `result` + `session_id` + not is_error; never process rc.

Identical process/ledger helpers are imported from cosmos_codex_rail
(improvement-not-bloat). Agent Family|Clade|Version parsing is
cosmos_work_order.parse_agent (2-part specs refused there, once).

    from cosmos_claude_rail import ClaudeRail, register_claude_rail
    register_claude_rail(registry, adapters, spend_gate, paths=kernel.paths)

    py -3.14 cosmos\\cosmos_claude_rail.py --root V:\\A\\Ai\\COSMOS\\live --gate
    py -3.14 cosmos\\cosmos_claude_rail.py --selftest

Recipe: docs/research/NEW_AI_DISCOVERY.md (Rank 1) +
docs/research/ANTHROPIC_HANDS.md.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cosmos_rail_base import (  # noqa: E402
    CREATE_NO_WINDOW,
    _ledger_is_authority,
    _real_run,
    _real_which,
    write_probe_record,
)
from cosmos_workspace import (  # noqa: E402
    WorkspaceError,
    assert_not_live as _ws_assert_not_live,
    clone_tree as _real_clone,
    prepare_workspace as _ws_prepare,
)
from cosmos_work_order import (  # noqa: E402
    OrderError,
    claude_model,
    parse_agent,
)

SCHEMA = "cosmos-claude-rail/1"
WORKER = "cosmos-claude-rail"
LINK_ID = "claude-cli"
BINARY = "claude"
KEY_NAME = "anthropic_api_key.txt"
SPEC_NAME = "claude_rail.json"
PROBE_NAME = "claude_rail_probe.json"
LAUNCH_NAME = "claude_rail_launch.json"
REPO = "https://github.com/keithbbf-gif/cosmos"
SRC = "core"
DST = "code"
PERMISSION_MODE = "dontAsk"
DEFAULT_MODEL = "claude-opus-5"
DEFAULT_TIMEOUT_S = 1800
PROBE_TIMEOUT_S = 20
KEY_MIN_LEN = 20
RESULT_CAP = 4000
ANTHROPIC_FAMILIES = frozenset({"anthropic", "claude"})


class ClaudeRailError(RuntimeError):
    """kind in {NO_KEY, BAD_SPEC, BAD_ROOT, UNREACHABLE, BROKE, REFUSED, BAD_INPUT}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def default_spec() -> dict:
    """Instance-free defaults. Live overlay is live/config/claude_rail.json."""
    return {
        "schema": SCHEMA,
        "link_id": LINK_ID,
        "rail_type": "CLI",
        "src": SRC,
        "dst": DST,
        "policy_rank": 0,
        "metered_usd": 0.0,
        "budget_usd": 0.0,
        "binary": BINARY,
        "key_name": KEY_NAME,
        "repo_url": REPO,
        "permission_mode": PERMISSION_MODE,
        "model": DEFAULT_MODEL,
        "wallet": "seat",
        "timeout_s": DEFAULT_TIMEOUT_S,
        "probe_timeout_s": PROBE_TIMEOUT_S,
        "dom_fallback": (
            "Claude in Chrome (GA on direct Anthropic plans). Canon "
            "DOM-first/API-second: when this CLI seat is AUTH_REQUIRED or "
            "the weekly window is dry, Playwright/cosmos_browser on "
            "claude.ai is the documented fallback. This module does not "
            "drive Chrome."
        ),
        "note": (
            "Claude Code CLI (Anthropic node). ANTHROPIC_API_KEY from "
            f"runtime-root config/{KEY_NAME} is READ at runtime, never "
            "hard-coded, redact sk-ant-…last4. Default child env UNSETS "
            "that key so the prepaid seat is used (H5). wallet=api injects "
            "it (metered overflow). metered_usd=0: seat is UNPRICED; "
            "Dispatcher does not spend-gate. Coding rail: src/dst="
            "core->code. Prompt on stdin. --permission-mode dontAsk is "
            "pinned (never yolo). done = JSON result+session_id, never rc."
        ),
    }


def _pin_origin(spec: dict) -> dict:
    """Fail-closed on binary, key file, permission-mode. Coerce core->models
    to core->code (H3). Refuse yolo / dangerously-skip-permissions."""
    kn = str(spec.get("key_name") or KEY_NAME)
    if kn != KEY_NAME:
        raise ClaudeRailError(
            "BAD_SPEC",
            f"key_name {kn!r} != {KEY_NAME!r} (COSMOS key file is pinned)")
    spec["key_name"] = KEY_NAME
    binary = str(spec.get("binary") or BINARY).strip() or BINARY
    if Path(binary).name.lower() not in ("claude", "claude.exe", "claude.cmd",
                                         "claude.bat"):
        raise ClaudeRailError(
            "BAD_SPEC",
            f"binary {binary!r} is not the Claude Code CLI (pinned {BINARY!r})")
    spec["binary"] = BINARY
    mode = str(spec.get("permission_mode") or PERMISSION_MODE).strip()
    if mode != PERMISSION_MODE:
        raise ClaudeRailError(
            "BAD_SPEC",
            f"permission_mode {mode!r} != {PERMISSION_MODE!r} "
            "(never yolo / dangerously-skip-permissions)")
    spec["permission_mode"] = PERMISSION_MODE
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
        raise ClaudeRailError(
            "BAD_SPEC",
            "claude-cli is a coding rail (core->code); refusing core->models")
    wallet = str(spec.get("wallet") or "seat").strip().lower()
    if wallet not in ("seat", "api"):
        raise ClaudeRailError(
            "BAD_SPEC", f"wallet {wallet!r} not in {{seat, api}}")
    spec["wallet"] = wallet
    spec["model"] = str(spec.get("model") or DEFAULT_MODEL).strip() or DEFAULT_MODEL
    return spec


def merge_spec(overlay) -> dict:
    spec = default_spec()
    if overlay is None:
        return _pin_origin(spec)
    if not isinstance(overlay, dict):
        raise ClaudeRailError(
            "BAD_SPEC", f"spec overlay is {type(overlay).__name__}")
    for k, v in overlay.items():
        spec[k] = v
    if spec.get("schema") != SCHEMA:
        raise ClaudeRailError(
            "BAD_SPEC",
            f"spec schema {spec.get('schema')!r} != {SCHEMA}")
    if spec.get("rail_type") != "CLI":
        raise ClaudeRailError(
            "BAD_SPEC",
            f"claude rail_type must be CLI, got {spec.get('rail_type')!r}")
    link = str(spec.get("link_id") or "").strip()
    if not link:
        raise ClaudeRailError("BAD_SPEC", "link_id is required")
    spec["link_id"] = link
    spec["metered_usd"] = float(spec.get("metered_usd") or 0.0)
    spec["budget_usd"] = float(spec.get("budget_usd") or 0.0)
    spec["policy_rank"] = int(spec.get("policy_rank") or 0)
    spec["timeout_s"] = int(spec.get("timeout_s") or DEFAULT_TIMEOUT_S)
    spec["probe_timeout_s"] = int(
        spec.get("probe_timeout_s") or PROBE_TIMEOUT_S)
    return _pin_origin(spec)


def load_spec(path: Path | None) -> dict:
    if path is None or not Path(path).exists():
        return default_spec()
    try:
        raw = Path(path).read_text(encoding="utf-8")
    except OSError as e:
        raise ClaudeRailError("BAD_SPEC", f"unreadable spec {path}: {e}") from e
    try:
        overlay = json.loads(raw)
    except ValueError as e:
        raise ClaudeRailError("BAD_SPEC", f"unparseable spec {path}: {e}") from e
    return merge_spec(overlay)


def write_spec(path: Path, spec: dict | None = None) -> dict:
    """Write the runtime spec. Never includes the secret."""
    body = merge_spec(spec)
    for k in ("api_key", "key", "anthropic_api_key", "ANTHROPIC_API_KEY"):
        body.pop(k, None)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(body, indent=2, sort_keys=True,
                               ensure_ascii=False) + "\n",
                    encoding="utf-8")
    return body


def redact_key(key: str) -> str:
    k = (key or "").strip()
    if len(k) >= 4:
        return f"sk-ant-…{k[-4:]}"
    return "sk-ant-…????"


def read_key(key_path: Path | None) -> str:
    if key_path is None:
        raise ClaudeRailError(
            "NO_KEY",
            f"Anthropic key path not supplied (want runtime-root "
            f"config/{KEY_NAME}; never hard-code)")
    p = Path(key_path)
    if not p.exists():
        raise ClaudeRailError(
            "NO_KEY",
            f"Anthropic key missing at {p} (never hard-code; "
            f"redact to sk-ant-…last4)")
    try:
        text = p.read_text(encoding="utf-8").strip()
    except OSError as e:
        raise ClaudeRailError("NO_KEY", f"unreadable key {p}: {e}") from e
    if text.startswith("\ufeff"):
        text = text.lstrip("\ufeff").strip()
    first = text.splitlines()[0].strip() if text else ""
    if not first.startswith("sk-ant") or len(first) < KEY_MIN_LEN:
        raise ClaudeRailError(
            "NO_KEY",
            f"key at {p} does not look like an Anthropic key "
            f"(want sk-ant…, min_len={KEY_MIN_LEN}, got len={len(first)})")
    return first


def done_from_artifacts(result, session_id, is_error) -> tuple[bool, str]:
    """Runtime-binding predicate. rc is not an input and cannot PASS this."""
    if is_error:
        return False, "is_error"
    msg = (result or "").strip() if isinstance(result, str) else ""
    sid = (session_id or "").strip() if isinstance(session_id, str) else ""
    if not msg and not sid:
        return False, "missing result and session_id"
    if not msg:
        return False, "missing result"
    if not sid:
        return False, "missing session_id"
    return True, "ok"


def parse_agent_spec(value) -> dict:
    """Family | Clade | Version. Reuses work-order parser (2-part = BAD_INPUT).
    This rail only accepts Anthropic/Claude families."""
    try:
        parsed = parse_agent(value)
    except OrderError as e:
        raise ClaudeRailError(e.kind, e.detail) from e
    if parsed["family_fold"] not in ANTHROPIC_FAMILIES:
        raise ClaudeRailError(
            "BAD_INPUT",
            f"claude-cli refuses Agent family {parsed['family']!r} "
            "(want Anthropic|Claude)")
    parsed["model"] = claude_model(parsed.get("version") or "",
                                   parsed.get("clade") or "")
    return parsed


def _parse_claude_json(stdout: str) -> dict:
    """Lift result / session_id / is_error / model from --output-format json."""
    s = (stdout or "").strip()
    obj = None
    if s.startswith("{"):
        try:
            obj = json.loads(s)
        except ValueError:
            obj = None
    if obj is None:
        start = s.rfind("{")
        end = s.rfind("}")
        if start >= 0 and end > start:
            try:
                obj = json.loads(s[start:end + 1])
            except ValueError:
                obj = None
    if not isinstance(obj, dict):
        return {"result": s if s else None, "session_id": None,
                "is_error": None, "model": None, "parse": "not_json",
                "raw_head": s[:400]}
    result = obj.get("result")
    if not isinstance(result, str):
        result = obj.get("text") if isinstance(obj.get("text"), str) else None
    sid = obj.get("session_id")
    if not isinstance(sid, str):
        sid = None
    model = obj.get("model")
    if not isinstance(model, str) or not model.strip():
        usage = obj.get("usage") if isinstance(obj.get("usage"), dict) else {}
        model = usage.get("model") if isinstance(usage.get("model"), str) else None
    is_error = obj.get("is_error")
    if is_error is None:
        is_error = bool(obj.get("is_api_error"))
        if obj.get("subtype") == "error" or obj.get("type") == "error":
            is_error = True
    return {
        "result": result,
        "session_id": sid.strip() if sid else None,
        "is_error": bool(is_error),
        "model": (model.strip() if isinstance(model, str) and model.strip()
                  else None),
        "parse": "ok",
        "total_cost_usd": obj.get("total_cost_usd"),
        "usage": obj.get("usage") if isinstance(obj.get("usage"), dict) else None,
    }


class ClaudeRail:
    """Dispatcher adapter. kind=CLI. probe() is `claude --version` (cheap).
    dispatch() is opt-in `claude -p` — never called by probe or --gate.
    Registered core->code, not core->models."""
    kind = "CLI"

    def __init__(self, key_path: Path | str | None, spec: dict | None = None,
                 run=None, which=None, clone=None, *, live_root=None):
        self.spec = merge_spec(spec)
        self.key_path = Path(key_path) if key_path is not None else None
        self.metered_usd = float(self.spec.get("metered_usd") or 0.0)
        self._run = run if run is not None else _real_run
        self._which = which if which is not None else _real_which
        self._clone = clone if clone is not None else _real_clone
        self.link_id = self.spec["link_id"]
        self._last_probe = None
        self._live_root = Path(live_root) if live_root is not None else None
        self._calls: list = []

    def _binary(self) -> str:
        found = self._which(BINARY)
        return found or BINARY

    def _env(self, key: str, *, wallet: str | None = None) -> dict:
        env = os.environ.copy()
        env.pop("ANTHROPIC_API_KEY", None)
        env.pop("ANTHROPIC_AUTH_TOKEN", None)
        env["PYTHONUTF8"] = "1"
        env["PYTHONIOENCODING"] = "utf-8"
        use = (wallet or self.spec.get("wallet") or "seat").strip().lower()
        if use == "api":
            env["ANTHROPIC_API_KEY"] = key
        return env

    def key_last4(self) -> str:
        try:
            return redact_key(read_key(self.key_path))
        except ClaudeRailError:
            return "sk-ant-…????"

    def last_probe(self):
        return self._last_probe

    def probe(self):
        """Cheapest liveness: key shape + `claude --version`. Never -p.
        Fail-closed unless the binary answers and the key looks like sk-ant…."""
        try:
            read_key(self.key_path)
        except ClaudeRailError as e:
            return False, f"UNREACHABLE: {e.kind}: {e}"
        found = self._which(BINARY)
        if not found:
            rec = {"binary": None, "version": None, "rc": None}
            self._last_probe = rec
            return False, f"UNREACHABLE: {BINARY} ABSENT on PATH"
        timeout = min(PROBE_TIMEOUT_S, int(self.spec.get("probe_timeout_s") or 20))
        try:
            r = self._run([found, "--version"], timeout_s=timeout)
        except Exception as e:  # noqa: BLE001
            return False, f"UNREACHABLE: probe raised {type(e).__name__}: {e}"
        ver = ((r.get("out") or "") + (r.get("err") or "")).strip().splitlines()
        version = ver[0].strip() if ver else ""
        rec = {
            "binary": found,
            "version": version[:200],
            "rc": r.get("rc"),
            "timed_out": bool(r.get("timed_out")),
        }
        self._last_probe = rec
        if r.get("timed_out"):
            return False, "UNREACHABLE: claude --version TIMEOUT"
        if r.get("rc") != 0 or not version:
            err = (r.get("err") or r.get("out") or "")[:200]
            return False, (
                f"UNREACHABLE: claude --version rc={r.get('rc')} {err}".strip())
        return True, (
            f"claude-cli live binary={found} version={version[:80]} "
            f"key={self.key_last4()}")

    def _assert_not_live(self, workspace: Path) -> None:
        try:
            _ws_assert_not_live(workspace, live_root=self._live_root)
        except WorkspaceError as e:
            raise ClaudeRailError(e.kind, e.detail) from e

    def _prepare_workspace(self, payload: dict) -> tuple[Path, dict]:
        try:
            return _ws_prepare(
                payload, live_root=self._live_root, lane="claude",
                clone_fn=self._clone)
        except WorkspaceError as e:
            raise ClaudeRailError(e.kind, e.detail) from e

    def _resolve_model(self, payload: dict) -> str:
        agent = payload.get("Agent") or payload.get("agent")
        if agent:
            parsed = parse_agent_spec(agent)
            return parsed["model"]
        model = payload.get("model")
        if model:
            return str(model).strip()
        return str(self.spec.get("model") or DEFAULT_MODEL)

    def _argv(self, workspace: Path, model: str) -> list:
        bin_ = self._binary()
        return [
            bin_, "-p",
            "--model", str(model),
            "--permission-mode", PERMISSION_MODE,
            "--add-dir", str(workspace),
            "--output-format", "json",
        ]

    def _exec(self, argv, cwd, timeout_s, key, stdin=None, *,
              wallet: str | None = None) -> dict:
        self._calls.append({"argv": list(argv), "cwd": str(cwd) if cwd else None,
                            "stdin": stdin})
        env = self._env(key, wallet=wallet)
        return self._run(argv, cwd=cwd, timeout_s=timeout_s, env=env, stdin=stdin)

    def dispatch(self, payload: dict) -> dict:
        """Opt-in `claude -p`. probe() never calls this."""
        payload = payload or {}
        text = payload.get("prompt") or payload.get("text") or payload.get("task") or ""
        if not str(text).strip():
            return {"ok": False, "kind": "BROKE", "done": False,
                    "detail": "dispatch payload.prompt is required",
                    "node": self.link_id}
        try:
            model = self._resolve_model(payload)
        except ClaudeRailError as e:
            return {"ok": False, "kind": e.kind, "done": False,
                    "detail": str(e), "node": self.link_id}
        try:
            key = read_key(self.key_path)
        except ClaudeRailError as e:
            return {"ok": False, "kind": "UNREACHABLE", "done": False,
                    "detail": f"{e.kind}: {e}", "node": self.link_id}
        try:
            ws, clone_rec = self._prepare_workspace(payload)
        except ClaudeRailError as e:
            return {"ok": False, "kind": e.kind, "done": False,
                    "detail": str(e), "node": self.link_id}
        argv = self._argv(ws, model)
        timeout_s = float(payload.get("timeout_s") or self.spec["timeout_s"])
        wallet = payload.get("wallet")
        run = self._exec(argv, ws, timeout_s, key, stdin=str(text),
                         wallet=wallet)
        parsed = _parse_claude_json(run.get("out") or "")
        result = parsed.get("result") or ""
        rec = {
            "ok": False, "kind": "CLI", "node": self.link_id,
            "mode": "coder",
            "permission_mode": PERMISSION_MODE,
            "workspace": str(ws),
            "clone": clone_rec,
            "argv": argv,
            "argv_head": argv[:8],
            "pr_url": None,
            "pr_ready": False,
            "gateway": "fenced_commit",
            "dom_fallback": self.spec.get("dom_fallback"),
            "requested_model": model,
            "rc": run.get("rc"),
            "timed_out": bool(run.get("timed_out")),
            "stderr_tail": (run.get("err") or "")[-1500:],
            "stdout_tail": (run.get("out") or "")[-4000:],
            "secs": run.get("elapsed_s"),
            "usd": parsed.get("total_cost_usd"),
            "provenance": "UNPRICED" if (wallet or self.spec.get("wallet")) != "api"
            else "METERED",
            "session_id": parsed.get("session_id"),
            "is_error": parsed.get("is_error"),
            "parse": parsed.get("parse"),
            "usage": parsed.get("usage"),
        }
        model_live = parsed.get("model") or model
        rec["model"] = model_live
        rec["model_source"] = "json" if parsed.get("model") else "requested"
        rec["result"] = (result or "")[:RESULT_CAP]
        rec["result_truncated"] = len(result or "") > RESULT_CAP
        rec["text"] = rec["result"]
        rec["last_message"] = rec["result"]
        if rec.get("timed_out"):
            rec["ok"] = False
            rec["done"] = False
            rec["kind"] = "BROKE"
            rec["detail"] = "TIMEOUT"
            rec["done_why"] = "TIMEOUT (result/session_id not a substitute)"
            return rec
        ok, why = done_from_artifacts(
            result, parsed.get("session_id"), parsed.get("is_error"))
        rec["ok"] = ok
        rec["done"] = ok
        rec["done_why"] = why
        rec["pr_ready"] = bool(ok)
        if not ok:
            rec["kind"] = "BROKE"
            rec["detail"] = why
        rec["note"] = (
            "COSMOS fenced commit gateway opens the PR; this rail does not "
            "git push or gh pr create. DOM fallback is Claude in Chrome.")
        return rec


def spec_path_for(paths) -> Path:
    return paths.config(SPEC_NAME)


def key_path_for(paths, spec: dict | None = None) -> Path:
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
        raise ClaudeRailError(
            "BAD_SPEC",
            "claude-cli is a coding rail (core->code); refusing core->models (H3)")


def register_claude_rail(registry, adapters: dict, spend_gate=None,
                         src: str | None = None, dst: str | None = None, *,
                         paths=None, spec=None, key_path=None,
                         run=None, which=None, clone=None) -> dict:
    """Register claude-cli. Missing key -> still registered; probe records
    UNREACHABLE (registration is not capability). Route is core->code.
    Explicit core->models is refused (H3).
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
    live_root = paths.root if paths is not None else None
    rail = ClaudeRail(key_path, spec, run=run, which=which, clone=clone,
                      live_root=live_root)
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
            raise ClaudeRailError(
                "BROKE", f"set_budget failed for {lid}: {e}") from e
    key_ok = False
    last4 = "sk-ant-…????"
    try:
        last4 = redact_key(read_key(Path(key_path) if key_path else None))
        key_ok = True
    except ClaudeRailError:
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


def attach_to_kernel(kernel, adapters: dict | None = None, run=None,
                     which=None, clone=None, *,
                     boot_compose: bool = False) -> dict:
    """Additive compose onto an already-built Kernel.

    H4: refuses to append LINK_REGISTERED to the authority ledger unless
    `boot_compose=True` (Kernel.__init__ compose_rails fail-open). Isolated
    --gate ledgers are not authority.
    """
    if _ledger_is_authority(kernel) and not boot_compose:
        raise ClaudeRailError(
            "REFUSED",
            "attach_to_kernel refuses authority LINK_REGISTERED until Kernel "
            "boot reattaches probes every boot (BACKLOG). Isolated --gate "
            "ledger only. Pass boot_compose=True only from Kernel.__init__.")
    if adapters is None:
        adapters = getattr(kernel, "adapters", None)
        if adapters is None:
            adapters = {}
            kernel.adapters = adapters
    return register_claude_rail(
        kernel.registry, adapters, spend_gate=getattr(kernel, "spend", None),
        paths=kernel.paths, run=run, which=which, clone=clone)


def refuse_live_authority_attach(paths) -> dict:
    """Prove H4 against THIS tree's authority path without writing it."""
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
    except ClaudeRailError as e:
        rec["refused"] = e.kind == "REFUSED"
        rec["kind"] = e.kind
        rec["detail"] = str(e)
    return rec


def inspect_live_kernel(root) -> dict:
    """Read-only Kernel: is claude-cli in the production registry?"""
    out = {"opened": False, "claude_in_registry": None, "error": None}
    try:
        from cosmos_kernel import Kernel
        k = Kernel(root, worker="claude-rail-gate", read_only=True)
        out["opened"] = True
        out["tree_id"] = k.paths.sentinel.tree_id
        out["claude_in_registry"] = LINK_ID in k.registry.state()
        out["read_only"] = True
    except Exception as e:  # noqa: BLE001
        out["error"] = f"{type(e).__name__}: {e}"
    return out


def _iso_now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _compose_isolated(paths, spec, keyp, run, which, clone):
    from cosmos_ledger import Ledger
    from cosmos_registry import Registry
    from cosmos_rails import Dispatcher
    from cosmos_spend import SpendGate

    adapters = {}
    gate_dir = paths.role("state", "claude_rail")
    gate_dir.mkdir(parents=True, exist_ok=True)
    led = Ledger(gate_dir / "gate.jsonl", b"claude-rail-gate", WORKER)
    reg = Registry(led)
    spend = SpendGate(led)
    attached = register_claude_rail(
        reg, adapters, spend_gate=spend, spec=spec, key_path=keyp,
        paths=paths, run=run, which=which, clone=clone)
    disp = Dispatcher(reg, adapters, led, spend=spend)
    return attached, adapters, disp, led, gate_dir


def gate(root: str | os.PathLike, *, run=None, which=None, clone=None) -> dict:
    """Runtime-binding gate for the Claude rail.

    Isolated ledger under state/claude_rail/ (never authority.jsonl).
    probe() hits `claude --version`. Does not `claude -p` (H2).
    PASS iff probe_ok AND key_ok AND route core->code AND the authority
    ledger was not written. rc=0 is not the proof;
    config/claude_rail_probe.json is.
    """
    from cosmos_paths import CosmosPaths

    paths = CosmosPaths(root)
    spec = load_spec(spec_path_for(paths))
    write_spec(spec_path_for(paths), spec)
    keyp = key_path_for(paths, spec)
    attached, adapters, disp, led, gate_dir = _compose_isolated(
        paths, spec, keyp, run, which, clone)
    try:
        measured_rec = disp.registry.probe(attached["link_id"])
    except Exception as e:  # noqa: BLE001
        measured_rec = {"ok": False, "detail": f"{type(e).__name__}: {e}"}
    rail = adapters[attached["link_id"]]
    ident = rail.last_probe()
    if ident is None and attached["key_ok"]:
        ok, detail = rail.probe()
        ident = rail.last_probe()
        measured_rec = {"ok": ok, "detail": detail}
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
        "matrix": disp.registry.matrix(),
        "dispatcher_constructed": True,
        "authority_ledger_written": False,
        "kernel_attached": False,
        "launch": False,
        "live_value": None,
        "gate": "FAIL",
        "stage6": {
            "kind": "satellite",
            "kernel_attach": "compose_rails fail-open",
            "predicate": (
                "claude --version AND key sk-ant-… AND "
                f"route {SRC}->{DST} AND attach refused on authority; "
                "done for --launch is result+session_id, never rc"
            ),
        },
    }
    if ident:
        rec["me"] = {
            "binary": ident.get("binary"),
            "version": ident.get("version"),
            "rc": ident.get("rc"),
        }
        rec["live_value"] = {
            "binary": ident.get("binary"),
            "version": ident.get("version"),
            "key_last4": attached["key_last4"],
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
    route_ok = rec["route"] == f"{SRC}->{DST}"
    attach_refused = bool(rec["attach_refusal"].get("refused"))
    version = (rec.get("live_value") or {}).get("version")
    if (rec["probe_ok"] and attached["key_ok"] and version
            and route_ok and attach_refused
            and not rec["authority_ledger_written"]
            and rec["kernel_attached"] is False):
        rec["gate"] = "PASS"
    rec["proof"] = (
        f"claude-cli probe_ok={rec['probe_ok']} "
        f"version={(rec.get('live_value') or {}).get('version')!r} "
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


def launch_run(root: str | os.PathLike, prompt: str, *,
               run=None, which=None, clone=None,
               extra: dict | None = None) -> dict:
    """OPT-IN claude -p. Not --gate (H2). Never writes gate=PASS."""
    from cosmos_paths import CosmosPaths
    from cosmos_rails import RailError

    if not str(prompt or "").strip():
        return {
            "ok": False, "kind": "BROKE", "done": False,
            "launch_error": "launch requested without prompt",
            "gate": None, "launch": False,
        }
    paths = CosmosPaths(root)
    spec = load_spec(spec_path_for(paths))
    keyp = key_path_for(paths, spec)
    attached, adapters, disp, led, gate_dir = _compose_isolated(
        paths, spec, keyp, run, which, clone)
    payload = dict(extra or {})
    payload["prompt"] = prompt
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
        "done": False,
        "authority_ledger_written": False,
        "kernel_attached": False,
    }
    try:
        launched = disp.dispatch(SRC, DST, payload)
    except RailError as e:
        launched = {"ok": False, "kind": e.kind, "detail": str(e), "done": False}
    rec["ok"] = bool(launched.get("done") or launched.get("ok"))
    rec["done"] = bool(launched.get("done"))
    rec["dispatch"] = {
        "ok": launched.get("ok"),
        "done": launched.get("done"),
        "done_why": launched.get("done_why"),
        "kind": launched.get("kind"),
        "model": launched.get("model"),
        "session_id": launched.get("session_id"),
        "result_head": (launched.get("result") or "")[:400],
        "workspace": launched.get("workspace"),
        "argv": launched.get("argv"),
        "rc": launched.get("rc"),
        "detail": launched.get("detail"),
    }
    rec["model"] = launched.get("model")
    rec["result"] = launched.get("result")
    try:
        rec["isolated_ledger_events"] = [e.get("event") for e in led.verify()]
    except Exception as e:  # noqa: BLE001
        rec["ledger_error"] = f"{type(e).__name__}: {e}"
    rec["isolated_ledger"] = str(gate_dir / "gate.jsonl")
    written = write_probe_record(launch_path_for(paths), rec)
    written["launch_path"] = str(launch_path_for(paths))
    return written


def _selftest() -> int:
    """Isolated. Fake run/which/clone. No live key spend, no authority ledger."""
    import ast
    import tempfile

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

    td = Path(tempfile.mkdtemp(prefix="cosmos_claude_rail_"))
    root = install(td / "live", tree_id="spike-claude-rail")
    from cosmos_paths import CosmosPaths
    paths = CosmosPaths(root)
    keyp = paths.config(KEY_NAME)
    dummy = "sk-ant-api03-" + ("a" * 32) + "31ab"
    keyp.write_text(dummy, encoding="utf-8")
    spec = write_spec(paths.config(SPEC_NAME))
    ws = td / "attempt"
    ws.mkdir()
    calls = []

    def fake_which(name):
        if name == BINARY:
            return r"C:\npm\claude.CMD"
        return None

    def fake_clone(src, dest):
        Path(dest).mkdir(parents=True, exist_ok=True)
        return {"ok": True, "how": "fake", "src": str(src), "dest": str(dest)}

    def fake_run(argv, cwd=None, timeout_s=60, env=None, stdin=None):
        argv = list(argv)
        env = env or {}
        calls.append({
            "argv": argv, "cwd": cwd, "stdin": stdin,
            "has_anthropic": bool(env.get("ANTHROPIC_API_KEY")),
            "env_popped": "ANTHROPIC_API_KEY" not in env,
        })
        if "--version" in argv:
            return {"rc": 0, "out": "2.1.220 (Claude Code)\n", "err": "",
                    "timed_out": False, "elapsed_s": 0.1}
        if "-p" in argv:
            body = {
                "type": "result",
                "subtype": "success",
                "is_error": False,
                "result": "ALIVE via claude-cli",
                "session_id": "sess-test-1",
                "model": "claude-opus-5",
                "total_cost_usd": 0.0,
            }
            return {"rc": 1, "out": json.dumps(body) + "\n", "err": "warn",
                    "timed_out": False, "elapsed_s": 0.2}
        return {"rc": 404, "out": "", "err": "unexpected",
                "timed_out": False, "elapsed_s": 0.0}

    src_text = Path(__file__).read_text(encoding="utf-8")
    tree = ast.parse(src_text)

    def _imports_bts(mod_ast) -> bool:
        for node in ast.walk(mod_ast):
            if isinstance(node, ast.Import):
                for a in node.names:
                    if a.name == "bts_" or a.name.startswith("bts_"):
                        return True
            if isinstance(node, ast.ImportFrom):
                mod = node.module or ""
                if mod == "bts_" or mod.startswith("bts_"):
                    return True
        return False

    check("no bts_ import", lambda: not _imports_bts(tree))

    missing = ClaudeRail(td / "no-such-key.txt", spec, run=fake_run,
                         which=fake_which, clone=fake_clone)
    mok, mdetail = missing.probe()
    check("missing key probe is UNREACHABLE (registration is not capability)",
          lambda: (not mok) and "UNREACHABLE" in mdetail and "NO_KEY" in mdetail)

    rail = ClaudeRail(keyp, spec, run=fake_run, which=fake_which,
                      clone=fake_clone, live_root=paths.root)
    ok, detail = rail.probe()
    check("probe claude --version is live",
          lambda: ok and "2.1.220" in detail and "sk-ant-…31ab" in detail)
    check("probe never calls -p",
          lambda: all("-p" not in (c["argv"] or []) for c in calls))

    def which_none(name):
        return None

    dead = ClaudeRail(keyp, spec, run=fake_run, which=which_none, clone=fake_clone)
    dok, ddet = dead.probe()
    check("ABSENT binary probe is UNREACHABLE, not a crash",
          lambda: (not dok) and "UNREACHABLE" in ddet and "ABSENT" in ddet)

    check("M5 binary retarget is BAD_SPEC",
          lambda: _raises_kind(lambda: merge_spec({
              "schema": SCHEMA, "rail_type": "CLI", "link_id": LINK_ID,
              "binary": "curl",
          }), "BAD_SPEC"))
    check("M5 key_name retarget is BAD_SPEC",
          lambda: _raises_kind(lambda: merge_spec({
              "schema": SCHEMA, "rail_type": "CLI", "link_id": LINK_ID,
              "key_name": "bts_oa_key.txt",
          }), "BAD_SPEC"))
    check("M5 yolo permission-mode is BAD_SPEC",
          lambda: _raises_kind(lambda: merge_spec({
              "schema": SCHEMA, "rail_type": "CLI", "link_id": LINK_ID,
              "permission_mode": "bypassPermissions",
          }), "BAD_SPEC"))
    coerced = merge_spec({
        "schema": SCHEMA, "rail_type": "CLI", "link_id": LINK_ID,
        "src": "core", "dst": "models",
    })
    check("H3 overlay core->models is coerced to core->code",
          lambda: coerced["src"] == SRC and coerced["dst"] == DST)

    calls.clear()
    out = rail.dispatch({"prompt": "hello", "workspace": str(ws),
                         "skip_clone": True, "timeout_s": 5,
                         "model": DEFAULT_MODEL})
    pcalls = [c for c in calls if "-p" in c["argv"]]
    argv = pcalls[0]["argv"] if pcalls else []

    def _flag(av, name):
        if name in av:
            return av[av.index(name) + 1]
        prefix = name + "="
        for a in av:
            if a.startswith(prefix):
                return a[len(prefix):]
        return None

    check("dispatch calls claude -p", lambda: len(pcalls) == 1)
    check("argv carries --model",
          lambda: _flag(argv, "--model") == DEFAULT_MODEL)
    check("argv carries --permission-mode dontAsk",
          lambda: _flag(argv, "--permission-mode") == "dontAsk")
    check("argv --add-dir is the workspace",
          lambda: _flag(argv, "--add-dir") == str(ws))
    check("prompt went on stdin (not after --add-dir)",
          lambda: pcalls and pcalls[0].get("stdin") == "hello"
          and "hello" not in argv)
    check("done PASSES on result+session_id even when rc=1",
          lambda: out["done"] is True and out["ok"] is True
          and out.get("rc") == 1
          and out.get("session_id") == "sess-test-1"
          and out.get("result") == "ALIVE via claude-cli")
    check("seat wallet does not inject ANTHROPIC_API_KEY (H5)",
          lambda: pcalls and pcalls[0]["has_anthropic"] is False
          and dummy not in json.dumps(out))
    check("empty prompt is BROKE, not a launch",
          lambda: rail.dispatch({"prompt": ""})["kind"] == "BROKE")

    check("2-part Agent spec is refused",
          lambda: _raises_kind(
              lambda: parse_agent_spec("Anthropic | Opus"), "BAD_INPUT"))
    check("2-part Agent on dispatch is refused",
          lambda: rail.dispatch({
              "prompt": "x", "workspace": str(ws), "skip_clone": True,
              "Agent": "Anthropic | Sonnet",
          }).get("kind") == "BAD_INPUT")
    three = parse_agent_spec("Anthropic | Opus | claude-opus-5")
    check("3-part Anthropic Agent is accepted",
          lambda: three["family_fold"] == "anthropic"
          and three["model"] == "claude-opus-5")

    check("coder refuses the live runtime root as workspace",
          lambda: rail.dispatch({
              "prompt": "x", "workspace": str(paths.root),
              "skip_clone": True,
          }).get("kind") == "REFUSED")

    led = Ledger(td / "n.jsonl", b"k", "core")
    reg = Registry(led)
    adapters = {}
    rec = register_claude_rail(
        reg, adapters, spend_gate=SpendGate(led), spec=spec,
        key_path=keyp, run=fake_run, which=fake_which, clone=fake_clone,
        paths=paths)
    check("register_claude_rail claims claude-cli",
          lambda: rec["link_id"] == "claude-cli" and "claude-cli" in reg.state())
    check("register route is core->code not core->models",
          lambda: rec["src"] == SRC and rec["dst"] == DST)
    check("H3 explicit core->models register is BAD_SPEC",
          lambda: _raises_kind(lambda: register_claude_rail(
              Registry(Ledger(td / "bad.jsonl", b"k", "core")),
              {}, spec=spec, key_path=keyp, run=fake_run, which=fake_which,
              src="core", dst="models"), "BAD_SPEC"))
    reg.probe_all()
    disp = Dispatcher(reg, adapters, led, spend=SpendGate(led))
    models_err = None
    try:
        disp.dispatch("core", "models",
                      {"prompt": "hi", "workspace": str(ws), "skip_clone": True})
    except RailError as e:
        models_err = e
    check("H3 Dispatcher core->models does not exec",
          lambda: models_err is not None and models_err.kind == "NO_LIVE_LINK")
    routed = disp.dispatch("core", "code",
                           {"prompt": "route me", "workspace": str(ws),
                            "skip_clone": True, "timeout_s": 5})
    check("dispatcher reaches claude-cli on core->code",
          lambda: routed["ok"] and routed["result"] == "ALIVE via claude-cli")
    check("RAIL_DISPATCH + RAIL_RESULT ledgered (even at $0 marginal)",
          lambda: {e["event"] for e in led.verify()} >= {
              "LINK_REGISTERED", "PROBE_RESULT", "RAIL_DISPATCH", "RAIL_RESULT"})

    spec_txt = paths.config(SPEC_NAME).read_text(encoding="utf-8")
    check("spec file has no sk-ant secret",
          lambda: dummy not in spec_txt)
    g = gate(root, run=fake_run, which=fake_which, clone=fake_clone)
    check("gate PASS on injected --version + key shape",
          lambda: g["gate"] == "PASS"
          and "2.1.220" in str((g.get("live_value") or {}).get("version")))
    check("gate does not write the authority ledger",
          lambda: g["authority_ledger_written"] is False)
    check("gate does not claim Kernel attach",
          lambda: g["kernel_attached"] is False)
    check("gate did not -p (H2)",
          lambda: g["launch"] is False)
    check("H4 attach_to_kernel refused live-shaped authority",
          lambda: g["attach_refusal"]["refused"] is True
          and g["attach_refusal"]["kind"] == "REFUSED")

    k = Kernel(root, worker="claude-rail-selftest")
    ad = {}
    refused = False
    try:
        attach_to_kernel(k, ad, run=fake_run, which=fake_which, clone=fake_clone)
    except ClaudeRailError as e:
        refused = e.kind == "REFUSED"
    check("H4 attach_to_kernel on writing Kernel refuses without boot_compose",
          lambda: refused)
    att = attach_to_kernel(k, ad, run=fake_run, which=fake_which,
                           clone=fake_clone, boot_compose=True)
    check("attach_to_kernel(boot_compose=True) registers claude-cli",
          lambda: att["link_id"] in k.registry.state() and att["link_id"] in ad
          and att["link_id"] == "claude-cli")
    check("spec documents Claude in Chrome DOM fallback",
          lambda: "Claude in Chrome" in (spec.get("dom_fallback") or ""))
    check("CREATE_NO_WINDOW reused from codex rail (imported)",
          lambda: CREATE_NO_WINDOW == (0x08000000 if os.name == "nt" else 0))

    bad = [(l, e) for l, ok, e in results if not ok]
    for label, ok, err in results:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (claude-cli is the Anthropic coding rail; "
          "probe=claude --version; dispatch=opt-in -p; "
          "argv=--model + --permission-mode dontAsk + --add-dir; "
          "done=result+session_id never rc; core->code; no bts_ import)"
          % ("PASS" if not bad else "FAIL", len(results)))
    return 0 if not bad else 1


def _raises_kind(fn, kind: str) -> bool:
    try:
        fn()
    except ClaudeRailError as e:
        return e.kind == kind
    return False


def main() -> int:
    ap = argparse.ArgumentParser(
        prog="cosmos_claude_rail",
        description="COSMOS Claude Code CLI rail. probe is cheap; "
                    "dispatch launches. --gate is the runtime-binding proof. "
                    "--launch is a separate verb (quota).")
    ap.add_argument("--root", default=None,
                    help="COSMOS runtime root (resolver-verified). Required for --gate.")
    ap.add_argument("--gate", action="store_true",
                    help="compose isolated Registry+Dispatcher, live claude --version, "
                         "write config/claude_rail_probe.json. Does not -p.")
    ap.add_argument("--probe", action="store_true",
                    help="probe only (same live --version, no isolated ledger).")
    ap.add_argument("--selftest", action="store_true",
                    help="isolated fake-run checks; no live network / no spend.")
    ap.add_argument("--launch", default=None, metavar="PROMPT",
                    help="OPT-IN coder: claude -p --permission-mode dontAsk. "
                         "Spends seat/quota. Separate from --gate.")
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
            rail = ClaudeRail(key_path_for(paths, spec), spec,
                              live_root=paths.root)
            ok, detail = rail.probe()
            rec = {"ok": ok, "detail": detail, "link_id": rail.link_id,
                   "key_last4": rail.key_last4()}
            ident = rail.last_probe() or {}
            rec["version"] = ident.get("version")
            rec["binary"] = ident.get("binary")
            print(json.dumps(rec, indent=1))
            return 0 if ok else 2
        combined = None
        if a.gate:
            combined = dict(gate(a.root))
        if a.launch is not None:
            launch_rec = launch_run(a.root, a.launch)
            if combined is None:
                combined = dict(launch_rec)
            else:
                combined["launch"] = True
                combined["dispatch"] = launch_rec.get("dispatch")
                combined["launch_ok"] = launch_rec.get("ok")
                combined["launch_path"] = launch_rec.get("launch_path")
                if not launch_rec.get("done"):
                    combined["gate"] = "FAIL"
                    combined["gate_note"] = (
                        "launch failed the result+session_id predicate; "
                        "probe identity recorded but exit is not PASS (H2)")
        print(json.dumps(combined, indent=1, default=str))
        if combined and combined.get("gate") == "PASS" and not combined.get("launch"):
            return 0
        if combined and combined.get("launch") and combined.get("done"):
            return 0
        return 2
    ap.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
