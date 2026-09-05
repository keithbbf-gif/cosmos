#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_codex_rail - COSMOS-native OpenAI Codex CLI coder+vetter rail.

Vendor-plural: an OpenAI-family coder/vetter that can DISAGREE with G46/Grok +
Cursor. Primary path from docs/research/GITHUB_CODEX_RAIL.md (lowest
dependency; needs only an OpenAI key at the runtime root).

NOT a BTS wrap. NOT oa-api (that's the metered Responses HTTP rail). This
module drives the Codex CLI headless:

  CODER:  codex exec --sandbox workspace-write --skip-git-repo-check
          --json --output-last-message <file> "<task>"
          in an attempt-private clone. COSMOS's fenced commit gateway
          opens the PR; this rail never git-push / gh-pr-create.
  VETTER: codex exec --sandbox read-only --output-schema <schema>
          --json --output-last-message <file>  (diff on stdin)
          -> machine-readable approve|request-changes + findings JSON
          for the critics/consensus stage.

Key path is the runtime-root role `config/openai_api_key.txt` (never the git
tree, never hard-coded, never printed in full; redact to sk-…last4).
OPENAI_API_KEY / CODEX_API_KEY are injected into the child env only.

Does NOT modify COSMOS core (kernel/ledger/sched/service). attach_to_kernel()
refuses to append LINK_REGISTERED to the authority ledger until Kernel boot
reattaches probes every boot (H4). The coding route is core->code, never a
model peer (H3). --gate PASS binds Codex --version + key-shape; --launch /
--vet are separate verbs (H2). Runtime-binding "done" is the
--output-last-message file PLUS the real model field from the JSONL stream;
an exit code is recorded, never the predicate.

    from cosmos_codex_rail import CodexRail, register_codex_rail
    register_codex_rail(registry, adapters, spend_gate, paths=kernel.paths)

    py -3.14 cosmos\\cosmos_codex_rail.py --root V:\\A\\Ai\\COSMOS\\live --gate
    py -3.14 cosmos\\cosmos_codex_rail.py --selftest

Recipe: docs/research/GITHUB_CODEX_RAIL.md + docs/research/OPENAI_HANDS.md.
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

# Phase 3.1 (2026-08-30/31). These five lived HERE and four other modules
# imported them from this vendor rail as if it were a library. They now live in
# cosmos_rail_base and are RE-EXPORTED from this module, so
# cosmos_claude_rail / cosmos_dispatch / cosmos_rails_prober /
# cosmos_work_order_run keep working with no edit. tests/test_rail_base.py
# pins that every rail resolves them to the SAME object -- a re-export that
# silently forks would put the duplication straight back.
from cosmos_rail_base import (  # noqa: E402,F401
    CREATE_NO_WINDOW,
    RailError as RailSeamError,
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

SCHEMA = "cosmos-codex-rail/1"
WORKER = "cosmos-codex-rail"
LINK_ID = "codex-cli"
BINARY = "codex"
KEY_NAME = "openai_api_key.txt"
SPEC_NAME = "codex_rail.json"
PROBE_NAME = "codex_rail_probe.json"
LAUNCH_NAME = "codex_rail_launch.json"
VET_NAME = "codex_rail_vet.json"
REPO = "https://github.com/keithbbf-gif/cosmos"
SRC = "core"
DST = "code"
CODER_SANDBOX = "workspace-write"
VETTER_SANDBOX = "read-only"
DEFAULT_TIMEOUT_S = 1800
PROBE_TIMEOUT_S = 20
KEY_MIN_LEN = 20
RESULT_CAP = 4000

# Critics/consensus schema: the disagreeing OpenAI voice. Pinned so a live
# overlay cannot retarget the vetter into free-form prose.
VETTER_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "COSMOS Codex vetter",
    "type": "object",
    "additionalProperties": False,
    "required": ["verdict", "findings"],
    "properties": {
        "verdict": {
            "type": "string",
            "enum": ["approve", "request-changes"],
        },
        "findings": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["severity", "path", "message"],
                "properties": {
                    "severity": {
                        "type": "string",
                        "enum": ["high", "med", "low", "info"],
                    },
                    "path": {"type": "string"},
                    "line": {"type": ["integer", "null"]},
                    "message": {"type": "string"},
                },
            },
        },
        "model": {"type": "string"},
        "summary": {"type": "string"},
    },
}

VETTER_PROMPT = (
    "You are a COSMOS critic (OpenAI-family). Your job is to DISAGREE when "
    "the diff is wrong, incomplete, or unsafe. Review the unified diff on "
    "stdin. Emit JSON matching the output schema: verdict is approve or "
    "request-changes; findings is a list of {severity, path, message, line?}. "
    "Do not modify files. Do not commit. Do not open a PR."
)


class CodexRailError(RailSeamError):
    """kind in {NO_KEY, BAD_SPEC, BAD_ROOT, UNREACHABLE, BROKE, REFUSED}.

    Subclasses the seam-wide `cosmos_rail_base.RailError` (same
    `(kind, detail)` constructor, same message shape), so every existing
    `except CodexRailError` catches exactly what it caught before while the
    shared helpers in the base can refuse without importing this rail.
    """


def default_spec() -> dict:
    """Instance-free defaults. Live overlay is live/config/codex_rail.json."""
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
        "coder_sandbox": CODER_SANDBOX,
        "vetter_sandbox": VETTER_SANDBOX,
        "timeout_s": DEFAULT_TIMEOUT_S,
        "probe_timeout_s": PROBE_TIMEOUT_S,
        "skip_git_repo_check": True,
        "note": (
            "Codex CLI coder+vetter. OPENAI_API_KEY from runtime-root "
            f"config/{KEY_NAME}; never hard-code, redact sk-…last4. "
            "metered_usd=0 so Dispatcher does not spend-gate (Platform "
            "billing is Keith's wallet; UNPRICED != spend). Coding rail: "
            "src/dst=core->code, never a model peer. Coder writes an "
            "attempt-private clone; the fenced commit gateway opens the PR. "
            "Vetter is read-only. --launch/--vet are opt-in, never probe/"
            "--gate. done = last_message file + real model field, never rc."
        ),
    }


def _pin_origin(spec: dict) -> dict:
    """Fail-closed on binary, key file, sandboxes (M5). Coerce core->models
    landmine to core->code (H3). Refuse danger-full-access."""
    kn = str(spec.get("key_name") or KEY_NAME)
    if kn != KEY_NAME:
        raise CodexRailError(
            "BAD_SPEC",
            f"key_name {kn!r} != {KEY_NAME!r} (COSMOS key file is pinned)")
    spec["key_name"] = KEY_NAME
    binary = str(spec.get("binary") or BINARY).strip() or BINARY
    if Path(binary).name.lower() not in ("codex", "codex.exe", "codex.cmd",
                                         "codex.bat"):
        raise CodexRailError(
            "BAD_SPEC",
            f"binary {binary!r} is not the Codex CLI (pinned {BINARY!r})")
    spec["binary"] = BINARY
    coder_sb = str(spec.get("coder_sandbox") or CODER_SANDBOX)
    if coder_sb != CODER_SANDBOX:
        raise CodexRailError(
            "BAD_SPEC",
            f"coder_sandbox {coder_sb!r} != {CODER_SANDBOX!r} "
            "(never danger-full-access; never the live tree)")
    spec["coder_sandbox"] = CODER_SANDBOX
    vet_sb = str(spec.get("vetter_sandbox") or VETTER_SANDBOX)
    if vet_sb != VETTER_SANDBOX:
        raise CodexRailError(
            "BAD_SPEC",
            f"vetter_sandbox {vet_sb!r} != {VETTER_SANDBOX!r} "
            "(vetter is read-only)")
    spec["vetter_sandbox"] = VETTER_SANDBOX
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
        raise CodexRailError(
            "BAD_SPEC",
            "codex-cli is a coding rail (core->code); refusing core->models")
    spec["skip_git_repo_check"] = True
    return spec


def merge_spec(overlay) -> dict:
    spec = default_spec()
    if overlay is None:
        return _pin_origin(spec)
    if not isinstance(overlay, dict):
        raise CodexRailError("BAD_SPEC", f"spec overlay is {type(overlay).__name__}")
    for k, v in overlay.items():
        spec[k] = v
    if spec.get("schema") != SCHEMA:
        raise CodexRailError(
            "BAD_SPEC",
            f"spec schema {spec.get('schema')!r} != {SCHEMA}")
    if spec.get("rail_type") != "CLI":
        raise CodexRailError(
            "BAD_SPEC",
            f"codex rail_type must be CLI, got {spec.get('rail_type')!r}")
    link = str(spec.get("link_id") or "").strip()
    if not link:
        raise CodexRailError("BAD_SPEC", "link_id is required")
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
        raise CodexRailError("BAD_SPEC", f"unreadable spec {path}: {e}") from e
    try:
        overlay = json.loads(raw)
    except ValueError as e:
        raise CodexRailError("BAD_SPEC", f"unparseable spec {path}: {e}") from e
    return merge_spec(overlay)


def write_spec(path: Path, spec: dict | None = None) -> dict:
    """Write the runtime spec. Never includes the secret."""
    body = merge_spec(spec)
    body.pop("api_key", None)
    body.pop("key", None)
    body.pop("openai_api_key", None)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(body, indent=2, sort_keys=True,
                               ensure_ascii=False) + "\n",
                    encoding="utf-8")
    return body


def redact_key(key: str) -> str:
    k = (key or "").strip()
    if len(k) >= 4:
        return f"sk-…{k[-4:]}"
    return "sk-…????"


def read_key(key_path: Path | None) -> str:
    if key_path is None:
        raise CodexRailError(
            "NO_KEY",
            f"OpenAI key path not supplied (want runtime-root "
            f"config/{KEY_NAME}; never hard-code)")
    p = Path(key_path)
    if not p.exists():
        raise CodexRailError(
            "NO_KEY",
            f"OpenAI key missing at {p} (never hard-code; "
            f"redact to sk-…last4)")
    try:
        text = p.read_text(encoding="utf-8").strip()
    except OSError as e:
        raise CodexRailError("NO_KEY", f"unreadable key {p}: {e}") from e
    if text.startswith("\ufeff"):
        text = text.lstrip("\ufeff").strip()
    first = text.splitlines()[0].strip() if text else ""
    if not first.startswith("sk-") or len(first) < KEY_MIN_LEN:
        raise CodexRailError(
            "NO_KEY",
            f"key at {p} does not look like an OpenAI key "
            f"(want sk-…, min_len={KEY_MIN_LEN}, got len={len(first)})")
    return first


def done_from_artifacts(last_message, model) -> tuple[bool, str]:
    """Runtime-binding predicate. rc is not an input and cannot PASS this."""
    msg = (last_message or "").strip()
    mdl = (model or "").strip() if isinstance(model, str) else ""
    if not msg and not mdl:
        return False, "missing last_message and model"
    if not msg:
        return False, "missing last_message (--output-last-message empty)"
    if not mdl:
        return False, "missing real model field"
    return True, "ok"


def _lift_jsonl(stdout: str) -> dict:
    """Pull thread_id / model / usage / last agent_message from JSONL."""
    thread_id = None
    model = None
    usage = None
    last_text = None
    for raw in (stdout or "").splitlines():
        line = raw.strip()
        if not line.startswith("{"):
            continue
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        if not isinstance(ev, dict):
            continue
        t = ev.get("type")
        if t == "thread.started":
            thread_id = ev.get("thread_id") or thread_id
        if isinstance(ev.get("model"), str) and ev.get("model").strip():
            model = ev["model"].strip()
        item = ev.get("item") if isinstance(ev.get("item"), dict) else {}
        if isinstance(item.get("model"), str) and item.get("model").strip():
            model = item["model"].strip()
        payload = ev.get("payload") if isinstance(ev.get("payload"), dict) else {}
        if isinstance(payload.get("model"), str) and payload.get("model").strip():
            model = payload["model"].strip()
        if t == "turn.completed":
            if isinstance(ev.get("usage"), dict):
                usage = ev["usage"]
        if t in ("item.completed", "AgentMessage"):
            text = item.get("text") or ev.get("content") or ev.get("text")
            if isinstance(text, str) and text.strip():
                last_text = text
    return {
        "thread_id": thread_id,
        "model": model,
        "usage": usage,
        "jsonl_last": last_text,
    }


def _model_from_last_message(text: str):
    """If last-message is schema JSON, lift a model field (vetter)."""
    s = (text or "").strip()
    if not s.startswith("{"):
        return None
    try:
        obj = json.loads(s)
    except ValueError:
        return None
    if isinstance(obj, dict) and isinstance(obj.get("model"), str):
        m = obj["model"].strip()
        return m or None
    return None


def _parse_vetter_body(text: str) -> dict:
    s = (text or "").strip()
    if not s:
        return {"verdict": None, "findings": [], "parse": "empty"}
    try:
        obj = json.loads(s)
    except ValueError:
        start = s.find("{")
        end = s.rfind("}")
        if start >= 0 and end > start:
            try:
                obj = json.loads(s[start:end + 1])
            except ValueError:
                return {"verdict": None, "findings": [], "parse": "unparseable",
                        "raw_head": s[:400]}
        else:
            return {"verdict": None, "findings": [], "parse": "unparseable",
                    "raw_head": s[:400]}
    if not isinstance(obj, dict):
        return {"verdict": None, "findings": [], "parse": "not_object"}
    verdict = obj.get("verdict")
    if verdict not in ("approve", "request-changes"):
        verdict = None
    findings = obj.get("findings")
    if not isinstance(findings, list):
        findings = []
    return {
        "verdict": verdict,
        "findings": findings,
        "summary": obj.get("summary"),
        "model": obj.get("model") if isinstance(obj.get("model"), str) else None,
        "parse": "ok" if verdict else "no_verdict",
    }


class CodexRail:
    """Dispatcher adapter. kind=CLI. probe() is `codex --version` (cheap).
    dispatch() is opt-in `codex exec` — never called by probe or --gate.
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

    def _env(self, key: str) -> dict:
        env = os.environ.copy()
        env["OPENAI_API_KEY"] = key
        env["CODEX_API_KEY"] = key
        env["PYTHONUTF8"] = "1"
        env["PYTHONIOENCODING"] = "utf-8"
        return env

    def key_last4(self) -> str:
        try:
            return redact_key(read_key(self.key_path))
        except CodexRailError:
            return "sk-…????"

    def last_probe(self):
        return self._last_probe

    def probe(self):
        """Cheapest liveness: key shape + `codex --version`. Never exec.
        Fail-closed unless the binary answers and the key looks like sk-…."""
        try:
            read_key(self.key_path)
        except CodexRailError as e:
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
            return False, "UNREACHABLE: codex --version TIMEOUT"
        if r.get("rc") != 0 or not version:
            err = (r.get("err") or r.get("out") or "")[:200]
            return False, (
                f"UNREACHABLE: codex --version rc={r.get('rc')} {err}".strip())
        return True, (
            f"codex-cli live binary={found} version={version[:80]} "
            f"key={self.key_last4()}")

    def _assert_not_live(self, workspace: Path) -> None:
        try:
            _ws_assert_not_live(workspace, live_root=self._live_root)
        except WorkspaceError as e:
            raise CodexRailError(e.kind, e.detail) from e

    def _prepare_workspace(self, payload: dict) -> tuple[Path, dict]:
        try:
            return _ws_prepare(
                payload, live_root=self._live_root, lane="codex",
                clone_fn=self._clone)
        except WorkspaceError as e:
            raise CodexRailError(e.kind, e.detail) from e

    def _argv(self, mode: str, prompt: str, last_path: Path,
              schema_path: Path | None, model: str | None) -> list:
        bin_ = self._binary()
        if mode == "vetter":
            if schema_path is None:
                raise CodexRailError("BROKE", "vetter requires --output-schema")
            argv = [
                bin_, "exec",
                "--sandbox", VETTER_SANDBOX,
                "--output-schema", str(schema_path),
                "--json",
                "--output-last-message", str(last_path),
                "--skip-git-repo-check",
                "--color", "never",
                "--ignore-user-config",
            ]
        else:
            argv = [
                bin_, "exec",
                "--sandbox", CODER_SANDBOX,
                "--skip-git-repo-check",
                "--json",
                "--output-last-message", str(last_path),
                "--color", "never",
                "--ignore-user-config",
            ]
        if model:
            argv.extend(["--model", str(model)])
        argv.append(str(prompt))
        return argv

    def _exec(self, argv, cwd, timeout_s, key, stdin=None) -> dict:
        self._calls.append({"argv": list(argv), "cwd": str(cwd) if cwd else None})
        env = self._env(key)
        return self._run(argv, cwd=cwd, timeout_s=timeout_s, env=env, stdin=stdin)

    def _read_last_message(self, path: Path) -> str:
        if not path.exists():
            return ""
        try:
            return path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return ""

    def _bind_result(self, rec: dict, last_path: Path, run: dict,
                     started_at: float | None = None) -> dict:
        last = self._read_last_message(last_path)
        if started_at is not None and last_path.exists():
            try:
                if last_path.stat().st_mtime + 0.05 < started_at:
                    last = ""
            except OSError:
                pass
        lifted = _lift_jsonl(run.get("out") or "")
        model = lifted.get("model")
        model_source = "jsonl" if model else None
        if not model:
            from_msg = _model_from_last_message(last)
            if from_msg:
                model = from_msg
                model_source = "last_message"
        if not last.strip() and lifted.get("jsonl_last"):
            last = lifted["jsonl_last"]
        rec["last_message"] = last[:RESULT_CAP]
        rec["last_message_truncated"] = len(last) > RESULT_CAP
        rec["last_message_path"] = str(last_path)
        rec["model"] = model
        rec["model_source"] = model_source
        rec["thread_id"] = lifted.get("thread_id")
        rec["usage"] = lifted.get("usage")
        rec["rc"] = run.get("rc")
        rec["timed_out"] = bool(run.get("timed_out"))
        rec["stderr_tail"] = (run.get("err") or "")[-1500:]
        rec["stdout_tail"] = (run.get("out") or "")[-4000:]
        rec["secs"] = run.get("elapsed_s")
        rec["usd"] = None
        rec["provenance"] = "UNPRICED"
        ok, why = done_from_artifacts(last, model)
        rec["ok"] = ok
        rec["done"] = ok
        rec["done_why"] = why
        rec["text"] = rec["last_message"]
        if rec.get("timed_out"):
            rec["ok"] = False
            rec["done"] = False
            rec["kind"] = "BROKE"
            rec["detail"] = "TIMEOUT"
            rec["done_why"] = "TIMEOUT (last_message/model not a substitute)"
        elif not ok:
            rec["kind"] = "BROKE"
            rec["detail"] = why
        return rec

    def coder(self, payload: dict) -> dict:
        payload = payload or {}
        text = payload.get("prompt") or payload.get("text") or payload.get("task") or ""
        if not str(text).strip():
            return {"ok": False, "kind": "BROKE", "done": False,
                    "detail": "dispatch payload.prompt is required",
                    "node": self.link_id}
        try:
            key = read_key(self.key_path)
        except CodexRailError as e:
            return {"ok": False, "kind": "UNREACHABLE", "done": False,
                    "detail": f"{e.kind}: {e}", "node": self.link_id}
        try:
            ws, clone_rec = self._prepare_workspace(payload)
        except CodexRailError as e:
            return {"ok": False, "kind": e.kind, "done": False,
                    "detail": str(e), "node": self.link_id}
        last_path = ws / "codex_last_message.txt"
        argv = self._argv(
            "coder", str(text), last_path, None,
            payload.get("model"))
        timeout_s = float(payload.get("timeout_s") or self.spec["timeout_s"])
        started_at = time.time()
        run = self._exec(argv, ws, timeout_s, key, stdin=None)
        rec = {
            "ok": False, "kind": "CLI", "node": self.link_id,
            "mode": "coder",
            "sandbox": CODER_SANDBOX,
            "workspace": str(ws),
            "clone": clone_rec,
            "argv_head": argv[:8],
            "pr_url": None,
            "pr_ready": False,
            "gateway": "fenced_commit",
            "branch": None,
            "repo_url": self.spec.get("repo_url"),
        }
        self._bind_result(rec, last_path, run, started_at=started_at)
        rec["pr_ready"] = bool(rec.get("done"))
        rec["note"] = (
            "COSMOS fenced commit gateway opens the PR; this rail does not "
            "git push or gh pr create")
        return rec

    def vet(self, payload: dict) -> dict:
        payload = payload or {}
        diff = payload.get("diff") or payload.get("stdin") or ""
        if payload.get("diff_path"):
            dp = Path(payload["diff_path"])
            try:
                diff = dp.read_text(encoding="utf-8", errors="replace")
            except OSError as e:
                return {"ok": False, "kind": "BROKE", "done": False,
                        "detail": f"unreadable diff_path: {e}",
                        "node": self.link_id}
        if not str(diff).strip():
            return {"ok": False, "kind": "BROKE", "done": False,
                    "detail": "vetter payload.diff is required (stdin)",
                    "node": self.link_id}
        try:
            key = read_key(self.key_path)
        except CodexRailError as e:
            return {"ok": False, "kind": "UNREACHABLE", "done": False,
                    "detail": f"{e.kind}: {e}", "node": self.link_id}
        work = payload.get("workspace")
        if work:
            ws = Path(work)
            ws.mkdir(parents=True, exist_ok=True)
        elif self._live_root is not None:
            attempt = str(payload.get("attempt_id") or f"vet-{int(time.time())}")
            ws = Path(self._live_root) / "work" / "codex" / attempt
            ws.mkdir(parents=True, exist_ok=True)
        else:
            ws = Path(payload.get("cwd") or os.getcwd())
        schema_path = Path(payload["schema_path"]) if payload.get("schema_path") else (
            ws / "codex_vetter_schema.json")
        if not payload.get("schema_path") or not schema_path.exists():
            schema_path.write_text(
                json.dumps(VETTER_SCHEMA, indent=2) + "\n", encoding="utf-8")
        last_path = ws / "codex_last_message.json"
        prompt = payload.get("prompt") or payload.get("text") or VETTER_PROMPT
        argv = self._argv(
            "vetter", str(prompt), last_path, schema_path,
            payload.get("model"))
        timeout_s = float(payload.get("timeout_s") or self.spec["timeout_s"])
        cwd = payload.get("cwd") or (str(ws) if ws.exists() else None)
        started_at = time.time()
        run = self._exec(argv, cwd, timeout_s, key, stdin=str(diff))
        rec = {
            "ok": False, "kind": "CLI", "node": self.link_id,
            "mode": "vetter",
            "sandbox": VETTER_SANDBOX,
            "workspace": str(ws),
            "schema_path": str(schema_path),
            "argv_head": argv[:10],
            "pr_url": None,
            "gateway": None,
        }
        self._bind_result(rec, last_path, run, started_at=started_at)
        parsed = _parse_vetter_body(self._read_last_message(last_path) or rec.get("last_message") or "")
        rec["verdict"] = parsed.get("verdict")
        rec["findings"] = parsed.get("findings") or []
        rec["summary"] = parsed.get("summary")
        rec["vetter_parse"] = parsed.get("parse")
        if rec.get("done") and parsed.get("verdict") is None:
            rec["ok"] = False
            rec["done"] = False
            rec["kind"] = "BROKE"
            rec["detail"] = "vetter last_message missing verdict"
            rec["done_why"] = rec["detail"]
        return rec

    def dispatch(self, payload: dict) -> dict:
        """Opt-in exec. probe() never calls this. mode=coder|vetter."""
        payload = payload or {}
        mode = str(payload.get("mode") or "coder").strip().lower()
        if mode in ("vet", "vetter", "review", "critic"):
            return self.vet(payload)
        if mode in ("coder", "code", "launch", ""):
            return self.coder(payload)
        return {"ok": False, "kind": "BROKE", "done": False,
                "detail": f"unknown mode {mode!r}; want coder|vetter",
                "node": self.link_id}


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


def vet_path_for(paths) -> Path:
    return paths.config(VET_NAME)


def _assert_coding_route(spec: dict, src, dst) -> None:
    use_src = src if src is not None else spec.get("src")
    use_dst = dst if dst is not None else spec.get("dst")
    if use_dst == "models" or (use_src == "core" and use_dst == "models"):
        raise CodexRailError(
            "BAD_SPEC",
            "codex-cli is a coding rail (core->code); refusing core->models (H3)")


def register_codex_rail(registry, adapters: dict, spend_gate=None,
                        src: str | None = None, dst: str | None = None, *,
                        paths=None, spec=None, key_path=None,
                        run=None, which=None, clone=None) -> dict:
    """Register codex-cli into a Registry + adapter map. Missing key ->
    still registered; probe records UNREACHABLE (registration is not capability).
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
    live_root = paths.root if paths is not None else None
    rail = CodexRail(key_path, spec, run=run, which=which, clone=clone,
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
            raise CodexRailError(
                "BROKE", f"set_budget failed for {lid}: {e}") from e
    key_ok = False
    last4 = "sk-…????"
    try:
        last4 = redact_key(read_key(Path(key_path) if key_path else None))
        key_ok = True
    except CodexRailError:
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
    """Additive compose onto an already-built Kernel. Does not edit kernel.py.

    H4: refuses to append LINK_REGISTERED to the authority ledger unless
    `boot_compose=True` (Kernel.__init__ reattaches probes every boot — BACKLOG).
    Isolated --gate ledgers are not authority and are the only legal compose
    until that hole is closed.
    """
    if _ledger_is_authority(kernel) and not boot_compose:
        raise CodexRailError(
            "REFUSED",
            "attach_to_kernel refuses authority LINK_REGISTERED until Kernel "
            "boot reattaches probes every boot (BACKLOG). Isolated --gate "
            "ledger only. Pass boot_compose=True only from Kernel.__init__.")
    if adapters is None:
        adapters = getattr(kernel, "adapters", None)
        if adapters is None:
            adapters = {}
            kernel.adapters = adapters
    return register_codex_rail(
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
    except CodexRailError as e:
        rec["refused"] = e.kind == "REFUSED"
        rec["kind"] = e.kind
        rec["detail"] = str(e)
    return rec


def inspect_live_kernel(root) -> dict:
    """Read-only Kernel: is codex-cli in the production registry?"""
    out = {"opened": False, "codex_in_registry": None, "error": None}
    try:
        from cosmos_kernel import Kernel
        k = Kernel(root, worker="codex-rail-gate", read_only=True)
        out["opened"] = True
        out["tree_id"] = k.paths.sentinel.tree_id
        out["codex_in_registry"] = "codex-cli" in k.registry.state()
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
    gate_dir = paths.role("state", "codex_rail")
    gate_dir.mkdir(parents=True, exist_ok=True)
    led = Ledger(gate_dir / "gate.jsonl", b"codex-rail-gate", WORKER)
    reg = Registry(led)
    spend = SpendGate(led)
    attached = register_codex_rail(
        reg, adapters, spend_gate=spend, spec=spec, key_path=keyp,
        paths=paths, run=run, which=which, clone=clone)
    disp = Dispatcher(reg, adapters, led, spend=spend)
    return attached, adapters, disp, led, gate_dir


def gate(root: str | os.PathLike, *, run=None, which=None, clone=None) -> dict:
    """Runtime-binding gate for the Codex rail.

    Composes Registry + Dispatcher on an ISOLATED ledger under
    state/codex_rail/ (never authority.jsonl). probe() hits `codex --version`
    unless `run`/`which` are injected. Does not `codex exec` (H2: launch/vet
    are separate verbs).

    PASS iff probe_ok (binary+version) AND key_ok AND route core->code AND
    the authority ledger was not written. rc=0 is not the proof;
    config/codex_rail_probe.json is.
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
        "vet": False,
        "live_value": None,
        "gate": "FAIL",
        "stage6": {
            "kind": "satellite",
            "kernel_attach": "BACKLOG",
            "predicate": (
                "codex --version AND key sk-… AND "
                f"route {SRC}->{DST} AND attach refused on authority; "
                "done for --launch is last_message+model, never rc"
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
    not_in_kernel = rec["live_kernel"].get("codex_in_registry") is not True
    version = (rec.get("live_value") or {}).get("version")
    if (rec["probe_ok"] and attached["key_ok"] and version
            and route_ok and attach_refused
            and not rec["authority_ledger_written"]
            and rec["kernel_attached"] is False
            and not_in_kernel):
        rec["gate"] = "PASS"
    rec["proof"] = (
        f"codex-cli probe_ok={rec['probe_ok']} "
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
    """OPT-IN coder exec. Not --gate (H2). Never writes gate=PASS.
    Isolated Dispatcher ledgers RAIL_DISPATCH / RAIL_RESULT on
    state/codex_rail/ (not authority). done binds last_message+model.
    """
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
    payload.setdefault("mode", "coder")
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
        "mode": launched.get("mode"),
        "model": launched.get("model"),
        "model_source": launched.get("model_source"),
        "last_message_head": (launched.get("last_message") or "")[:400],
        "last_message_path": launched.get("last_message_path"),
        "workspace": launched.get("workspace"),
        "pr_url": launched.get("pr_url"),
        "pr_ready": launched.get("pr_ready"),
        "gateway": launched.get("gateway"),
        "rc": launched.get("rc"),
        "detail": launched.get("detail"),
    }
    rec["model"] = launched.get("model")
    rec["last_message"] = launched.get("last_message")
    try:
        rec["isolated_ledger_events"] = [e.get("event") for e in led.verify()]
    except Exception as e:  # noqa: BLE001
        rec["ledger_error"] = f"{type(e).__name__}: {e}"
    rec["isolated_ledger"] = str(gate_dir / "gate.jsonl")
    written = write_probe_record(launch_path_for(paths), rec)
    written["launch_path"] = str(launch_path_for(paths))
    return written


def vet_run(root: str | os.PathLike, diff: str, *,
            run=None, which=None, clone=None,
            extra: dict | None = None) -> dict:
    """OPT-IN vetter exec. Not --gate (H2). Diff on stdin of codex exec."""
    from cosmos_paths import CosmosPaths
    from cosmos_rails import RailError

    if not str(diff or "").strip():
        return {
            "ok": False, "kind": "BROKE", "done": False,
            "vet_error": "vet requested without diff",
            "gate": None, "vet": False,
        }
    paths = CosmosPaths(root)
    spec = load_spec(spec_path_for(paths))
    keyp = key_path_for(paths, spec)
    attached, adapters, disp, led, gate_dir = _compose_isolated(
        paths, spec, keyp, run, which, clone)
    payload = dict(extra or {})
    payload["diff"] = diff
    payload["mode"] = "vetter"
    rec = {
        "schema": SCHEMA,
        "worker": WORKER,
        "vetted_at": _iso_now(),
        "root": str(paths.root),
        "tree_id": paths.sentinel.tree_id,
        "link_id": attached["link_id"],
        "key_last4": attached["key_last4"],
        "route": f"{attached['src']}->{attached['dst']}",
        "gate": None,
        "vet": True,
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
        "mode": launched.get("mode"),
        "model": launched.get("model"),
        "verdict": launched.get("verdict"),
        "findings": launched.get("findings"),
        "last_message_head": (launched.get("last_message") or "")[:400],
        "rc": launched.get("rc"),
        "detail": launched.get("detail"),
    }
    rec["model"] = launched.get("model")
    rec["verdict"] = launched.get("verdict")
    rec["findings"] = launched.get("findings")
    try:
        rec["isolated_ledger_events"] = [e.get("event") for e in led.verify()]
    except Exception as e:  # noqa: BLE001
        rec["ledger_error"] = f"{type(e).__name__}: {e}"
    rec["isolated_ledger"] = str(gate_dir / "gate.jsonl")
    written = write_probe_record(vet_path_for(paths), rec)
    written["vet_path"] = str(vet_path_for(paths))
    return written


def run_coding_dispatch(root, prompt: str, *, mode: str = "coder",
                        extra: dict | None = None,
                        run=None, which=None, clone=None) -> dict:
    """The one Codex launcher. cosmos_dispatch._codex_job imports and calls
    this. done = last_message + real model field, never rc.
    """
    payload = dict(extra or {})
    payload["prompt"] = prompt
    payload["mode"] = mode or "coder"
    from cosmos_paths import CosmosPaths
    paths = CosmosPaths(root)
    spec = load_spec(spec_path_for(paths))
    rail = CodexRail(
        key_path_for(paths, spec), spec, run=run, which=which, clone=clone,
        live_root=paths.root)
    return rail.dispatch(payload)


def run_vetter(root, diff: str, *, extra: dict | None = None,
               run=None, which=None, clone=None) -> dict:
    payload = dict(extra or {})
    payload["diff"] = diff
    payload["mode"] = "vetter"
    from cosmos_paths import CosmosPaths
    paths = CosmosPaths(root)
    spec = load_spec(spec_path_for(paths))
    rail = CodexRail(
        key_path_for(paths, spec), spec, run=run, which=which, clone=clone,
        live_root=paths.root)
    return rail.dispatch(payload)


def _selftest() -> int:
    """Isolated. Fake run/which/clone. No live key spend, no authority ledger."""
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

    td = Path(tempfile.mkdtemp(prefix="cosmos_codex_rail_"))
    root = install(td / "live", tree_id="spike-codex-rail")
    from cosmos_paths import CosmosPaths
    paths = CosmosPaths(root)
    keyp = paths.config(KEY_NAME)
    dummy = "sk-" + ("a" * 40) + "31ab"
    keyp.write_text(dummy, encoding="utf-8")
    spec = write_spec(paths.config(SPEC_NAME))
    ws = td / "attempt"
    ws.mkdir()
    calls = []

    def fake_which(name):
        if name == BINARY:
            return r"C:\npm\codex.CMD"
        return None

    def fake_clone(src, dest):
        Path(dest).mkdir(parents=True, exist_ok=True)
        return {"ok": True, "how": "fake", "src": str(src), "dest": str(dest)}

    def fake_run(argv, cwd=None, timeout_s=60, env=None, stdin=None):
        argv = list(argv)
        env_keys = sorted((env or {}).keys()) if env is not None else []
        calls.append({"argv": argv, "cwd": cwd, "stdin": stdin,
                      "has_openai": bool(env and env.get("OPENAI_API_KEY")),
                      "openai_last4": (env.get("OPENAI_API_KEY") or "")[-4:]
                      if env and env.get("OPENAI_API_KEY") else None,
                      "env_keys": env_keys})
        if "--version" in argv:
            return {"rc": 0, "out": "codex 0.50.0\n", "err": "",
                    "timed_out": False, "elapsed_s": 0.1}
        if "exec" in argv:
            last = None
            if "--output-last-message" in argv:
                i = argv.index("--output-last-message")
                last = Path(argv[i + 1])
            sandbox = None
            if "--sandbox" in argv:
                sandbox = argv[argv.index("--sandbox") + 1]
            if sandbox == VETTER_SANDBOX:
                body = {
                    "verdict": "request-changes",
                    "findings": [{
                        "severity": "med",
                        "path": "cosmos/x.py",
                        "line": 3,
                        "message": "disagree: missing fail-closed",
                    }],
                    "model": "gpt-5.3-codex",
                    "summary": "OpenAI-family critic disagrees",
                }
                if last:
                    last.parent.mkdir(parents=True, exist_ok=True)
                    last.write_text(json.dumps(body), encoding="utf-8")
                jsonl = (
                    json.dumps({"type": "thread.started",
                                "thread_id": "t-vet",
                                "model": "gpt-5.3-codex"})
                    + "\n"
                    + json.dumps({"type": "turn.completed",
                                  "model": "gpt-5.3-codex",
                                  "usage": {"input_tokens": 10,
                                            "output_tokens": 4}})
                    + "\n"
                )
                return {"rc": 3, "out": jsonl, "err": "",
                        "timed_out": False, "elapsed_s": 0.2}
            msg = "ALIVE via codex-cli"
            if last:
                last.parent.mkdir(parents=True, exist_ok=True)
                last.write_text(msg, encoding="utf-8")
            jsonl = (
                json.dumps({"type": "thread.started",
                            "thread_id": "t-code",
                            "model": "gpt-5.3-codex"})
                + "\n"
                + json.dumps({"type": "item.completed",
                              "item": {"type": "agent_message",
                                       "text": msg}})
                + "\n"
                + json.dumps({"type": "turn.completed",
                              "model": "gpt-5.3-codex",
                              "usage": {"input_tokens": 8,
                                        "output_tokens": 3}})
                + "\n"
            )
            # rc != 0 on purpose: done must still PASS (never bind rc).
            return {"rc": 1, "out": jsonl, "err": "warn",
                    "timed_out": False, "elapsed_s": 0.2}
        return {"rc": 404, "out": "", "err": "unexpected",
                "timed_out": False, "elapsed_s": 0.0}

    missing = CodexRail(td / "no-such-key.txt", spec, run=fake_run,
                        which=fake_which, clone=fake_clone)
    mok, mdetail = missing.probe()
    check("missing key probe is UNREACHABLE (registration is not capability)",
          lambda: (not mok) and "UNREACHABLE" in mdetail and "NO_KEY" in mdetail)
    check("missing key dispatch is typed UNREACHABLE",
          lambda: missing.dispatch({"prompt": "x", "workspace": str(ws),
                                    "skip_clone": True})["kind"] == "UNREACHABLE")

    rail = CodexRail(keyp, spec, run=fake_run, which=fake_which,
                     clone=fake_clone, live_root=paths.root)
    ok, detail = rail.probe()
    check("probe codex --version 0 is live",
          lambda: ok and "codex 0.50.0" in detail and "sk-…31ab" in detail)
    check("probe never calls exec",
          lambda: all("exec" not in (c["argv"] or []) for c in calls))
    check("key last4 redacts (no full secret)",
          lambda: rail.key_last4() == "sk-…31ab")

    def which_none(name):
        return None

    dead = CodexRail(keyp, spec, run=fake_run, which=which_none, clone=fake_clone)
    dok, ddet = dead.probe()
    check("ABSENT binary probe is UNREACHABLE, not a crash",
          lambda: (not dok) and "UNREACHABLE" in ddet and "ABSENT" in ddet)

    toy = td / "toy_key.txt"
    toy.write_text("sk-short", encoding="utf-8")
    check("short toy key is NO_KEY",
          lambda: _raises_kind(lambda: read_key(toy), "NO_KEY"))
    check("non-sk key is NO_KEY",
          lambda: _raises_kind(
              lambda: read_key(_write_key(td / "badk.txt", "crsr_notopenai")),
              "NO_KEY"))

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
    check("M5 danger-full-access is BAD_SPEC",
          lambda: _raises_kind(lambda: merge_spec({
              "schema": SCHEMA, "rail_type": "CLI", "link_id": LINK_ID,
              "coder_sandbox": "danger-full-access",
          }), "BAD_SPEC"))
    coerced = merge_spec({
        "schema": SCHEMA, "rail_type": "CLI", "link_id": LINK_ID,
        "src": "core", "dst": "models",
    })
    check("H3 overlay core->models is coerced to core->code",
          lambda: coerced["src"] == SRC and coerced["dst"] == DST)

    calls.clear()
    out = rail.dispatch({"prompt": "hello", "workspace": str(ws),
                         "skip_clone": True, "timeout_s": 5})
    exec_calls = [c for c in calls if "exec" in c["argv"]]
    check("dispatch calls codex exec",
          lambda: len(exec_calls) == 1)
    check("coder argv uses workspace-write",
          lambda: "--sandbox" in exec_calls[0]["argv"]
          and exec_calls[0]["argv"][exec_calls[0]["argv"].index("--sandbox") + 1]
          == CODER_SANDBOX)
    check("coder argv uses --skip-git-repo-check",
          lambda: "--skip-git-repo-check" in exec_calls[0]["argv"])
    check("coder argv uses --output-last-message",
          lambda: "--output-last-message" in exec_calls[0]["argv"])
    check("coder argv uses --json (model field lives in JSONL)",
          lambda: "--json" in exec_calls[0]["argv"])
    check("done PASSES on last_message+model even when rc=1",
          lambda: out["done"] is True and out["ok"] is True
          and out.get("rc") == 1
          and out.get("model") == "gpt-5.3-codex"
          and out.get("last_message") == "ALIVE via codex-cli")
    check("coder does not invent a PR url (gateway opens it)",
          lambda: out.get("pr_url") is None
          and out.get("gateway") == "fenced_commit"
          and out.get("pr_ready") is True)
    check("child env received OPENAI_API_KEY (not printed in rec)",
          lambda: exec_calls[0]["has_openai"] is True
          and exec_calls[0]["openai_last4"] == "31ab"
          and dummy not in json.dumps(out))
    check("empty prompt is BROKE, not a launch",
          lambda: rail.dispatch({"prompt": ""})["kind"] == "BROKE")

    def run_no_msg(argv, cwd=None, timeout_s=60, env=None, stdin=None):
        if "--version" in argv:
            return {"rc": 0, "out": "codex 0.50.0\n", "err": "",
                    "timed_out": False, "elapsed_s": 0.0}
        jsonl = json.dumps({"type": "turn.completed",
                            "model": "gpt-5.3-codex"}) + "\n"
        return {"rc": 0, "out": jsonl, "err": "",
                "timed_out": False, "elapsed_s": 0.0}

    ws_nomsg = td / "attempt_nomsg"
    ws_nomsg.mkdir()
    nomsg = CodexRail(keyp, spec, run=run_no_msg, which=fake_which,
                      clone=fake_clone, live_root=paths.root)
    nout = nomsg.dispatch({"prompt": "x", "workspace": str(ws_nomsg),
                           "skip_clone": True})
    check("rc=0 without last_message is NOT done",
          lambda: nout.get("done") is False and nout.get("ok") is False
          and nout.get("rc") == 0 and "last_message" in (nout.get("done_why") or ""))

    def run_no_model(argv, cwd=None, timeout_s=60, env=None, stdin=None):
        if "--version" in argv:
            return {"rc": 0, "out": "codex 0.50.0\n", "err": "",
                    "timed_out": False, "elapsed_s": 0.0}
        last = None
        if "--output-last-message" in argv:
            last = Path(argv[argv.index("--output-last-message") + 1])
            last.write_text("hello without model", encoding="utf-8")
        return {"rc": 0, "out": json.dumps({"type": "turn.completed"}) + "\n",
                "err": "", "timed_out": False, "elapsed_s": 0.0}

    ws_nomod = td / "attempt_nomod"
    ws_nomod.mkdir()
    nomod = CodexRail(keyp, spec, run=run_no_model, which=fake_which,
                      clone=fake_clone, live_root=paths.root)
    mout = nomod.dispatch({"prompt": "x", "workspace": str(ws_nomod),
                           "skip_clone": True})
    check("rc=0 without model field is NOT done",
          lambda: mout.get("done") is False and mout.get("ok") is False
          and mout.get("rc") == 0 and "model" in (mout.get("done_why") or ""))

    calls.clear()
    vout = rail.dispatch({
        "mode": "vetter",
        "diff": "diff --git a/x b/x\n+hello\n",
        "workspace": str(ws),
        "timeout_s": 5,
    })
    vcalls = [c for c in calls if "exec" in c["argv"]]
    check("vetter argv uses read-only sandbox",
          lambda: vcalls and "--sandbox" in vcalls[0]["argv"]
          and vcalls[0]["argv"][vcalls[0]["argv"].index("--sandbox") + 1]
          == VETTER_SANDBOX)
    check("vetter argv uses --output-schema",
          lambda: vcalls and "--output-schema" in vcalls[0]["argv"])
    check("vetter piped the diff on stdin",
          lambda: vcalls and "diff --git" in (vcalls[0].get("stdin") or ""))
    check("vetter returns request-changes + findings (disagreeing voice)",
          lambda: vout.get("done") is True
          and vout.get("verdict") == "request-changes"
          and vout.get("model") == "gpt-5.3-codex"
          and vout.get("findings")
          and vout.get("rc") == 3)
    check("empty diff is BROKE, not a vet",
          lambda: rail.vet({"diff": ""})["kind"] == "BROKE")

    check("coder refuses the live runtime root as workspace",
          lambda: rail.dispatch({
              "prompt": "x", "workspace": str(paths.root),
              "skip_clone": True,
          }).get("kind") == "REFUSED")

    led = Ledger(td / "n.jsonl", b"k", "core")
    reg = Registry(led)
    adapters = {}
    rec = register_codex_rail(
        reg, adapters, spend_gate=SpendGate(led), spec=spec,
        key_path=keyp, run=fake_run, which=fake_which, clone=fake_clone,
        paths=paths)
    check("register_codex_rail claims codex-cli",
          lambda: rec["link_id"] == "codex-cli" and "codex-cli" in reg.state())
    check("register route is core->code not core->models",
          lambda: rec["src"] == SRC and rec["dst"] == DST)
    check("H3 explicit core->models register is BAD_SPEC",
          lambda: _raises_kind(lambda: register_codex_rail(
              Registry(Ledger(td / "bad.jsonl", b"k", "core")),
              {}, spec=spec, key_path=keyp, run=fake_run, which=fake_which,
              src="core", dst="models"), "BAD_SPEC"))
    reg.probe_all()
    disp = Dispatcher(reg, adapters, led, spend=SpendGate(led))
    models_err = None
    try:
        disp.dispatch("core", "models",
                      {"prompt": "hi", "workspace": str(ws), "skip_clone": True})
        models_posted = False
    except RailError as e:
        models_err = e
        models_posted = False
    check("H3 Dispatcher core->models does not exec",
          lambda: models_err is not None and models_err.kind == "NO_LIVE_LINK"
          and models_posted is False)
    routed = disp.dispatch("core", "code",
                           {"prompt": "route me", "workspace": str(ws),
                            "skip_clone": True, "timeout_s": 5})
    check("dispatcher reaches codex-cli on core->code",
          lambda: routed["ok"] and routed["last_message"] == "ALIVE via codex-cli")
    check("RAIL_DISPATCH + RAIL_RESULT ledgered (even at $0 marginal)",
          lambda: {e["event"] for e in led.verify()} >= {
              "LINK_REGISTERED", "PROBE_RESULT", "RAIL_DISPATCH", "RAIL_RESULT"})

    spec_txt = paths.config(SPEC_NAME).read_text(encoding="utf-8")
    check("spec file has no sk- secret",
          lambda: dummy not in spec_txt and "sk-aaaa" not in spec_txt)
    g = gate(root, run=fake_run, which=fake_which, clone=fake_clone)
    check("gate PASS on injected --version + key shape",
          lambda: g["gate"] == "PASS"
          and "codex 0.50.0" in str((g.get("live_value") or {}).get("version")))
    check("gate writes probe file under config/",
          lambda: Path(g["probe_path"]).exists()
          and Path(g["probe_path"]).name == PROBE_NAME)
    probe_txt = Path(g["probe_path"]).read_text(encoding="utf-8")
    check("probe file redacts key and does not bake the secret",
          lambda: dummy not in probe_txt and "sk-…31ab" in probe_txt)
    check("gate does not write the authority ledger",
          lambda: g["authority_ledger_written"] is False)
    check("gate does not claim Kernel attach",
          lambda: g["kernel_attached"] is False)
    check("gate did not exec (H2)",
          lambda: g["launch"] is False and g.get("vet") is False)
    check("gate route is core->code",
          lambda: g.get("route") == f"{SRC}->{DST}")
    check("H4 attach_to_kernel refused live-shaped authority",
          lambda: g["attach_refusal"]["refused"] is True
          and g["attach_refusal"]["kind"] == "REFUSED")

    def run_exec_fail(argv, cwd=None, timeout_s=60, env=None, stdin=None):
        if "--version" in argv:
            return {"rc": 0, "out": "codex 0.50.0\n", "err": "",
                    "timed_out": False, "elapsed_s": 0.0}
        return {"rc": 2, "out": "", "err": "nope",
                "timed_out": False, "elapsed_s": 0.0}

    launched_fail = launch_run(
        root, "x", run=run_exec_fail, which=fake_which, clone=fake_clone,
        extra={"workspace": str(ws), "skip_clone": True})
    check("H2 --launch without last_message+model is not gate=PASS",
          lambda: launched_fail.get("gate") is None
          and launched_fail.get("ok") is False
          and launched_fail.get("launch") is True
          and launched_fail.get("done") is False)
    g_ok = gate(root, run=run_exec_fail, which=fake_which, clone=fake_clone)
    check("H2 --gate still PASSes version when launch is not requested",
          lambda: g_ok["gate"] == "PASS" and g_ok["launch"] is False)

    k = Kernel(root, worker="codex-rail-selftest")
    ad = {}
    refused = False
    try:
        attach_to_kernel(k, ad, run=fake_run, which=fake_which, clone=fake_clone)
    except CodexRailError as e:
        refused = e.kind == "REFUSED"
    check("H4 attach_to_kernel on writing Kernel refuses without boot_compose",
          lambda: refused and "codex-cli" not in k.registry.state())
    att = attach_to_kernel(k, ad, run=fake_run, which=fake_which,
                           clone=fake_clone, boot_compose=True)
    check("attach_to_kernel(boot_compose=True) still registers (BACKLOG hook)",
          lambda: att["link_id"] in k.registry.state() and att["link_id"] in ad)

    check("default metered_usd is 0 (UNPRICED != spend)",
          lambda: float(spec["metered_usd"]) == 0.0)
    check("default src/dst is core/code",
          lambda: spec["src"] == SRC and spec["dst"] == DST)
    check("done_from_artifacts ignores a would-be rc",
          lambda: done_from_artifacts("hi", "gpt-x") == (True, "ok"))

    _ = types

    bad = [(l, e) for l, ok, e in results if not ok]
    for label, ok, err in results:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (codex-cli is a COSMOS coding rail; "
          "probe=codex --version; dispatch=opt-in exec; "
          "done=last_message+model never rc; core->code; secret never baked)"
          % ("PASS" if not bad else "FAIL", len(results)))
    return 0 if not bad else 1


def _write_key(path: Path, text: str) -> Path:
    path.write_text(text, encoding="utf-8")
    return path


def _raises_kind(fn, kind: str) -> bool:
    try:
        fn()
    except CodexRailError as e:
        return e.kind == kind
    return False


def main() -> int:
    ap = argparse.ArgumentParser(
        prog="cosmos_codex_rail",
        description="COSMOS Codex CLI coder+vetter rail. probe is cheap; "
                    "dispatch launches. --gate is the runtime-binding proof. "
                    "--launch / --vet are separate verbs (quota).")
    ap.add_argument("--root", default=None,
                    help="COSMOS runtime root (resolver-verified). Required for --gate.")
    ap.add_argument("--gate", action="store_true",
                    help="compose isolated Registry+Dispatcher, live codex --version, "
                         "write config/codex_rail_probe.json. Does not exec.")
    ap.add_argument("--probe", action="store_true",
                    help="probe only (same live --version, no isolated ledger).")
    ap.add_argument("--selftest", action="store_true",
                    help="isolated fake-run checks; no live network / no spend.")
    ap.add_argument("--launch", default=None, metavar="PROMPT",
                    help="OPT-IN coder: codex exec --sandbox workspace-write. "
                         "Spends quota. Separate from --gate. Refuse to guess a prompt.")
    ap.add_argument("--vet", default=None, metavar="DIFF_PATH",
                    help="OPT-IN vetter: read-only exec, diff file on stdin, "
                         "--output-schema. Separate from --gate.")
    ap.add_argument("--repo", default=None,
                    help="clone source for --launch (default: runtime parent / repo tree).")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if a.gate or a.probe or a.launch is not None or a.vet is not None:
        if not a.root:
            print(json.dumps({
                "ok": False, "kind": "BAD_ROOT",
                "error": "--root is required (resolver does not guess)",
            }, indent=1))
            return 2
        if a.probe and not a.gate and a.launch is None and a.vet is None:
            from cosmos_paths import CosmosPaths
            paths = CosmosPaths(a.root)
            spec = load_spec(spec_path_for(paths))
            rail = CodexRail(key_path_for(paths, spec), spec,
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
        gate_rec = None
        launch_rec = None
        vet_rec = None
        if a.gate:
            gate_rec = gate(a.root)
            combined = dict(gate_rec)
        if a.launch is not None:
            extra = {}
            if a.repo:
                extra["repo"] = a.repo
            launch_rec = launch_run(a.root, a.launch, extra=extra)
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
                        "launch failed the last_message+model predicate; "
                        "probe identity recorded but exit is not PASS (H2)")
        if a.vet is not None:
            diff_path = Path(a.vet)
            try:
                diff = diff_path.read_text(encoding="utf-8", errors="replace")
            except OSError as e:
                print(json.dumps({
                    "ok": False, "kind": "BROKE",
                    "error": f"unreadable --vet path: {e}",
                }, indent=1))
                return 2
            vet_rec = vet_run(a.root, diff)
            if combined is None:
                combined = dict(vet_rec)
            else:
                combined["vet"] = True
                combined["vet_dispatch"] = vet_rec.get("dispatch")
                combined["vet_ok"] = vet_rec.get("ok")
                if not vet_rec.get("done"):
                    combined["gate"] = "FAIL"
        print(json.dumps(combined, indent=1, default=str, ensure_ascii=False))
        if a.launch is not None and a.gate:
            return 0 if (gate_rec or {}).get("gate") == "PASS" and launch_rec.get("done") else 2
        if a.vet is not None and a.gate:
            return 0 if (gate_rec or {}).get("gate") == "PASS" and vet_rec.get("done") else 2
        if a.launch is not None:
            return 0 if launch_rec.get("done") else 2
        if a.vet is not None:
            return 0 if vet_rec.get("done") else 2
        return 0 if (gate_rec or {}).get("gate") == "PASS" else 2
    ap.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
