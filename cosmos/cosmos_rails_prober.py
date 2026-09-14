#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_rails_prober - 1-minute rail freshness satellite + runtime node map.

Satellite: Cursor Cloud Agents GET /v1/me (cheap, never launches an agent),
CLI binaries on PATH, local HTTP (Core :8770, Ollama :11434) ->
live/state/rails/probe.json + heartbeat.

Runtime map (wishlist #64): `--live` probes the wired rails that actually
have hands and registers ONLY nodes that answer (rc=0 + non-empty body +
the responder that answered) through the ledger/registry authority.
`--once` (the 1-minute clock) is identity only: PATH + local HTTP. It
does not dispatch ANY rail. Keith 2026-09-01: rail proves are request +
permission. Projection: live/registry/{nodes,rails}.json. A node that
does not answer is NOT registered (fail-closed). Existence of
live/registry/ is not identity.

F-24 FIX (MEASURED, 2026-08-31): four rails answered their own probes and
were never asked for a PROOF, because WIRED_NODES held only four rows and
nothing else had a prove() call path. That is why the registry was small --
not refusal, not credentials, nobody asked. gw-api, cursor-api,
firecrawl-web and playwright-dom are now wired, each with a live_call that
returns the rail's OWN emitted response.

`model` for a rail that is not a model rail: proof_ok's fourth gate means
"name what answered", so each satellite carries the responder identity its
VENDOR emitted, and `model_source` says which field that was. Nothing is
synthesized -- if the emitted field is absent the model is empty and the
proof fails, fail-closed:

    gw-api          grok-build-0.1             bts_gw.ask() response model
    cursor-api      Cursor COSMOS 2            apiKeyName, GET /v1/me
    firecrawl-web   firecrawl/v2-research-papers   endpoint, emitted ONLY on a
                                               live arxiv:/doi:/pmid: primaryId
    playwright-dom  Playwright/<version>       MCP serverInfo from initialize

    py -3.14 cosmos\\cosmos_rails_prober.py --root V:\\A\\Ai\\COSMOS\\live --once
    py -3.14 cosmos\\cosmos_rails_prober.py --root ... --once --live
    py -3.14 cosmos\\cosmos_rails_prober.py --root ... --standup

Task: COSMOS Rails Prober. schtasks every 1 minute. No bts_* import.
Does not modify kernel/sched/service. Registry writes go through the
ledger/registry authority (projection only). Does not honor PAUSE.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import socket
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cosmos_clock import (  # noqa: E402
    create_task, heartbeat_age_s, query_task, read_heartbeat, tr_cmdline,
    write_heartbeat, atomic_json,
)
from cosmos_paths import CosmosPaths, CosmosPathError  # noqa: E402

WORKER = "cosmos-rails-prober"
TASK_NAME = "COSMOS Rails Prober"
HEARTBEAT_NAME = "rails_prober_heartbeat.json"
SCHEMA = "cosmos-rails-prober/1"
FRESH_S = 180.0
NODE_PROOF_TTL_S = 3600.0
LIVE_PROMPT = "Reply with the single token PONG and nothing else."
LIVE_TIMEOUT_S = 45.0
# Keith 2026-09-01: ALL rails — not just OpenAI. Unattended ticks never
# dispatch. PATH + local HTTP are identity. Any rail prove is --live
# (request + permission). Codex PONG loop billed ~$90 in 26h with no spend_ok.
SKIP_REQUIRES_LIVE = "requires-live"

FIRECRAWL_RESPONDER = "firecrawl/v2-research-papers"

# Wired hands (not a static registry). Each row is probed live; fail-closed.
# `module` -> an incumbent node client wrapped by NodeRail.
# `satellite` -> a COSMOS-native rail module with its own probe().
# neither    -> the Anthropic seat path.
WIRED_NODES = (
    {"link_id": "sgh-api", "rail_type": "API", "src": "core", "dst": "models",
     "family": "g46-grok", "module": "bts_sgh"},
    {"link_id": "gem-api", "rail_type": "API", "src": "core", "dst": "models",
     "family": "gem-vertex", "module": "bts_gem"},
    {"link_id": "gw-api", "rail_type": "API", "src": "core", "dst": "models",
     "family": "gw-grok-build", "module": "bts_gw"},
    {"link_id": "oa-api", "rail_type": "API", "src": "core", "dst": "models",
     "family": "oa-openai", "module": "bts_oa_api"},
    {"link_id": "claude-cli", "rail_type": "CLI", "src": "core", "dst": "code",
     "family": "anthropic", "module": None},
    # Same rail_type/src/dst/module shape as claude-cli (the other CLI coding
    # rail). satellite=codex so probe_module_for / default_live_call cannot
    # fall through to the Anthropic rail — that was the F-24 wiring's second
    # escape, and it is why a WIRED_NODES row with module=None is not enough.
    {"link_id": "codex-cli", "rail_type": "CLI", "src": "core", "dst": "code",
     "family": "openai-codex", "module": None, "satellite": "codex"},
    {"link_id": "cursor-api", "rail_type": "API", "src": "core", "dst": "code",
     "family": "cursor-cloud-agents", "module": None, "satellite": "cursor"},
    {"link_id": "firecrawl-web", "rail_type": "API", "src": "core",
     "dst": "papers", "family": "firecrawl", "module": None,
     "satellite": "firecrawl"},
    {"link_id": "groq-api", "rail_type": "API", "src": "core",
     "dst": "models", "family": "groqcloud", "module": None,
     "satellite": "groq"},
    {"link_id": "playwright-dom", "rail_type": "DOM", "src": "core",
     "dst": "interact", "family": "playwright-mcp", "module": None,
     "satellite": "playwright"},
    {"link_id": "github-forge", "rail_type": "CLI", "src": "core",
     "dst": "forge", "family": "github-cli", "module": None,
     "satellite": "github-forge"},
    {"link_id": "gitlab-forge", "rail_type": "CLI", "src": "core",
     "dst": "forge", "family": "gitlab-cli", "module": None,
     "satellite": "gitlab-forge"},
    # Copilot cloud agent. Credit-metered. Prove is GET /agents/tasks
    # (never POST / `gh agent-task create`). dst=code, never forge.
    {"link_id": "github-copilot", "rail_type": "API", "src": "core",
     "dst": "code", "family": "github-copilot-cloud", "module": None,
     "satellite": "github-copilot"},
)

CLI_RAILS = (
    "py", "grok", "claude", "cursor", "gh", "glab", "ollama",
    "npx", "node", "tailscale", "git",
)
HTTP_PROBES = (
    ("core-8770", "127.0.0.1", 8770),
    ("ollama-11434", "127.0.0.1", 11434),
)


def _tcp(host: str, port: int, timeout_s: float = 0.6) -> dict:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout_s)
    t0 = time.time()
    try:
        s.connect((host, port))
        ok, err = True, None
    except OSError as e:
        ok, err = False, f"{type(e).__name__}: {e}"
    finally:
        try:
            s.close()
        except OSError:
            pass
    return {"ok": ok, "error": err, "rtt_s": round(time.time() - t0, 4),
            "host": host, "port": port}


def _http_head(url: str, timeout_s: float = 1.5) -> dict:
    t0 = time.time()
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout_s) as r:  # noqa: S310
            return {"ok": 200 <= int(r.status) < 500,
                    "http": int(r.status),
                    "rtt_s": round(time.time() - t0, 4)}
    except urllib.error.HTTPError as e:
        return {"ok": True, "http": int(e.code),
                "rtt_s": round(time.time() - t0, 4),
                "note": "HTTPError still proves a listener"}
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": f"{type(e).__name__}: {e}",
                "rtt_s": round(time.time() - t0, 4)}


def _cursor_probe(paths: CosmosPaths) -> dict:
    try:
        from cosmos_cursor_rail import CursorRail, load_spec, KEY_NAME
        spec_path = paths.config("cursor_rail.json")
        spec = load_spec(spec_path if spec_path.exists() else None)
        key_path = paths.config(KEY_NAME)
        rail = CursorRail(key_path, spec)
        t0 = time.time()
        ok, detail = rail.probe()
        return {"ok": bool(ok), "detail": str(detail)[:300],
                "rtt_s": round(time.time() - t0, 4),
                "link_id": "cursor-api", "key_last4": rail.key_last4()}
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "detail": f"{type(e).__name__}: {e}",
                "link_id": "cursor-api"}


def _norm_proof(r: dict) -> dict:
    """Shape a rail result into the prove() contract. Never invents a model."""
    body = str(r.get("body") or r.get("text") or r.get("result") or "")
    rc = r.get("rc")
    if rc is None and r.get("ok") and body.strip():
        rc = 0
    model = str(r.get("model") or "")
    return {
        "ok": bool(r.get("ok")),
        "rc": rc,
        "body": body,
        "body_bytes": int(r.get("body_bytes") or len(body.encode("utf-8"))),
        "model": model,
        "detail": str(r.get("detail") or r.get("kind") or "")[:300],
        "via": r.get("via"),
        "kind": r.get("kind"),
    }


def _node_live_call(paths: CosmosPaths, module: str) -> dict:
    """Real NodeRail.dispatch — import-liveness is not a proof."""
    from cosmos_node_rails import NodeRail
    rail = NodeRail(module, paths=paths)
    return _norm_proof(rail.dispatch({"prompt": LIVE_PROMPT}))


def _claude_live_call(paths: CosmosPaths) -> dict:
    """Real Anthropic rail call. Seat-path if the COSMOS key file is absent.

    ClaudeRail.dispatch requires config/anthropic_api_key.txt; the prepaid
    seat still answers via `claude -p` with ANTHROPIC_API_KEY unset (H5).
    Same binary + permission-mode the wired rail uses. Not a second client.
    """
    from cosmos_claude_rail import (
        BINARY, PERMISSION_MODE, ClaudeRail, ClaudeRailError,
        _parse_claude_json, key_path_for, load_spec, spec_path_for,
    )
    from cosmos_rail_base import _real_run, _real_which

    spec = load_spec(spec_path_for(paths))
    keyp = key_path_for(paths, spec)
    ws = Path(tempfile.mkdtemp(prefix="claude_probe_"))
    if keyp.exists():
        try:
            rail = ClaudeRail(keyp, spec, live_root=paths.root)
            rec = rail.dispatch({
                "prompt": LIVE_PROMPT,
                "workspace": str(ws),
                "timeout_s": LIVE_TIMEOUT_S,
                "model": "haiku",
            })
            return _norm_proof(rec)
        except ClaudeRailError as e:
            if e.kind not in ("NO_KEY", "UNREACHABLE"):
                return {"ok": False, "rc": 2, "body": "", "body_bytes": 0,
                        "model": "", "detail": f"{e.kind}: {e}"}
    found = _real_which(BINARY)
    if not found:
        return {"ok": False, "rc": 2, "body": "", "body_bytes": 0, "model": "",
                "detail": f"UNREACHABLE: {BINARY} ABSENT on PATH"}
    env = os.environ.copy()
    env.pop("ANTHROPIC_API_KEY", None)
    env.pop("ANTHROPIC_AUTH_TOKEN", None)
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    argv = [found, "-p", "--model", "haiku",
            "--permission-mode", PERMISSION_MODE,
            "--add-dir", str(ws), "--output-format", "json"]
    run = _real_run(argv, cwd=ws, timeout_s=LIVE_TIMEOUT_S, env=env,
                    stdin=LIVE_PROMPT)
    parsed = _parse_claude_json(run.get("out") or "")
    body = str(parsed.get("result") or "")
    # Same as ClaudeRail.dispatch: JSON model, else the model we asked.
    requested = "haiku"
    model = str(parsed.get("model") or requested)
    rc = 2 if run.get("timed_out") else run.get("rc")
    ok = (rc == 0 and bool(body.strip()) and bool(model.strip())
          and not parsed.get("is_error"))
    err = (run.get("err") or "")[:200]
    return {
        "ok": bool(ok), "rc": rc, "body": body,
        "body_bytes": len(body.encode("utf-8")), "model": model,
        "detail": ("seat-path claude -p" if ok
                   else f"UNREACHABLE: rc={rc} {err}".strip()),
        "model_source": "json" if parsed.get("model") else "requested",
    }


def _codex_live_call(paths: CosmosPaths) -> dict:
    """Real Codex CLI exec. The rail reads config/openai_api_key.txt itself.

    Never prints or copies key material. A missing/invalid key is the rail's
    typed NO_KEY — not a seat fallback (there is no prepaid-seat path here)
    and not a workaround. dispatch() is the prove path: `codex --version` is
    not a proof (no body, no model that answered).
    """
    from cosmos_codex_rail import (
        CodexRail, CodexRailError, key_path_for, load_spec, spec_path_for,
    )
    spec = load_spec(spec_path_for(paths))
    keyp = key_path_for(paths, spec)
    ws = Path(tempfile.mkdtemp(prefix="codex_probe_"))
    try:
        rail = CodexRail(keyp, spec, live_root=paths.root)
        rec = rail.dispatch({
            "prompt": LIVE_PROMPT,
            "workspace": str(ws),
            "timeout_s": LIVE_TIMEOUT_S,
        })
        out = _norm_proof(rec)
        out["model_source"] = rec.get("model_source") or ""
        detail = rec.get("detail") or rec.get("done_why") or out.get("detail")
        kind = rec.get("kind") or ""
        if kind in ("NO_KEY", "UNREACHABLE", "BROKE", "REFUSED", "BAD_SPEC"):
            out["detail"] = f"{kind}: {detail}".strip(": ")
            out["kind"] = kind
        else:
            out["detail"] = str(detail or "")[:300]
        return out
    except CodexRailError as e:
        return {"ok": False, "rc": 2, "body": "", "body_bytes": 0,
                "model": "", "detail": f"{e.kind}: {e}", "kind": e.kind}


def _cursor_live_call(paths: CosmosPaths) -> dict:
    """Real GET /v1/me. The vendor NAMES what answered (apiKeyName) and the
    rail already binds that name to 'Cursor COSMOS 2', so the identity is the
    proof's model. The body is built here from the emitted fields only -- the
    rail's own detail string carries a redacted key fragment, and nothing
    key-shaped belongs in the authority ledger.
    """
    from cosmos_cursor_rail import CursorRail, KEY_NAME, load_spec, spec_path_for
    sp = spec_path_for(paths)
    rail = CursorRail(paths.config(KEY_NAME),
                      load_spec(sp if sp.exists() else None))
    ok, detail = rail.probe()
    ident = rail.last_identity() or {}
    body_obj = ident.get("body") if isinstance(ident.get("body"), dict) else {}
    name = str(body_obj.get("apiKeyName") or "")
    http = ident.get("http")
    date = (ident.get("headers") or {}).get("date", "")
    live = bool(ok and name)
    body = (f"cursor-api /v1/me http={http} apiKeyName={name} date={date}"
            if live else "")
    return {"ok": live, "rc": 0 if live else 2, "body": body,
            "body_bytes": len(body.encode("utf-8")),
            "model": name, "model_source": "apiKeyName (GET /v1/me)",
            "detail": (f"cursor-api identity-bound live probe http={http}"
                       if live else str(detail)[:300])}


def _firecrawl_live_call(paths: CosmosPaths) -> dict:
    """Real keyless GET /v2/search/research/papers.

    Firecrawl emits no product name in body or headers (measured: the response
    carries only date/etag/x-request-id/x-response-time), so the responder is
    named by its ENDPOINT -- and that name is emitted ONLY when the response
    carried a live arxiv:/doi:/pmid: primaryId. A config read or a cached file
    cannot produce one, so the constant can never stand in for a dead rail.
    """
    from cosmos_firecrawl_rail import (
        FirecrawlRail, id_is_live, key_path_for, load_spec, spec_path_for,
    )
    sp = spec_path_for(paths)
    spec = load_spec(sp if sp.exists() else None)
    rail = FirecrawlRail(key_path_for(paths, spec), spec)
    ok, detail = rail.probe()
    ident = rail.last_identity() or {}
    pid, http = ident.get("primaryId"), ident.get("http")
    live = bool(ok and http == 200 and id_is_live(pid))
    body = (f"firecrawl-web papers primaryId={pid} "
            f"title={str(ident.get('title') or '')[:120]} "
            f"http={http} success={ident.get('success')}") if live else ""
    return {"ok": live, "rc": 0 if live else 2, "body": body,
            "body_bytes": len(body.encode("utf-8")),
            "model": FIRECRAWL_RESPONDER if live else "",
            "model_source": "endpoint, emitted only on a live vendor primaryId",
            "detail": str(detail)[:300]}


def _playwright_live_call(paths: CosmosPaths) -> dict:
    """Real MCP initialize + tools/list against the pinned @playwright/mcp.

    The server NAMES and VERSIONS itself in serverInfo, which a spec file
    cannot forge, so that is the responder. The client is closed on EVERY
    path: this prober runs on a 1-minute clock, and a leaked node process per
    tick is a slow way to take the machine down.
    """
    from cosmos_playwright_rail import PlaywrightRail, load_spec, spec_path_for
    sp = spec_path_for(paths)
    spec = load_spec(sp if sp.exists() else None)
    rail = PlaywrightRail(spec, output_dir=paths.state("playwright_rail"))
    try:
        ok, detail = rail.probe()
        ident = rail.last_identity() or {}
    finally:
        rail.close()
    info = ident.get("serverInfo") or {}
    name, ver = str(info.get("name") or ""), str(info.get("version") or "")
    n = int(ident.get("tool_count") or 0)
    live = bool(ok and name and ver and n)
    body = (f"playwright-dom tools/list n={n} navigate+snapshot present "
            f"protocol={ident.get('protocolVersion')}") if live else ""
    return {"ok": live, "rc": 0 if live else 2, "body": body,
            "body_bytes": len(body.encode("utf-8")),
            "model": f"{name}/{ver}" if live else "",
            "model_source": "MCP serverInfo (initialize)",
            "detail": str(detail)[:300]}


def _forge_live_call(paths: CosmosPaths, link_id: str) -> dict:
    """Real authenticated REST identity (gh rate_limit / glab api user).

    The bound value is a forge-only field (rate_limit.limit / user.id). rc==0
    is required but is never itself the pass. No COSMOS secret is read.
    """
    from cosmos_forge_rail import ForgeRail, load_spec, spec_path_for
    sp = spec_path_for(paths)
    spec = load_spec(sp if sp.exists() else None)
    rail = ForgeRail(link_id, spec)
    ok, detail = rail.probe()
    bound = str((rail.last_identity() or {}).get("bound") or "")
    live = bool(ok and bound)
    body = f"{link_id} {bound}" if live else ""
    return {"ok": live, "rc": 0 if live else 2, "body": body,
            "body_bytes": len(body.encode("utf-8")),
            "model": bound if live else "",
            "model_source": "authenticated REST identity (limit / user.id)",
            "detail": str(detail)[:300]}


def _groq_live_call(paths: CosmosPaths) -> dict:
    """GET /models; bind openai/gpt-oss-20b in the vendor id list."""
    from cosmos_groq_rail import (
        DEFAULT_MODEL, GroqRail, key_path_for, load_spec, spec_path_for,
    )
    sp = spec_path_for(paths)
    spec = load_spec(sp if sp.exists() else None)
    rail = GroqRail(key_path_for(paths, spec), spec)
    ok, detail = rail.probe()
    ident = rail.last_identity() or {}
    has = bool(ident.get("has_gpt_oss_20b"))
    live = bool(ok and has)
    n = int(ident.get("n_models") or 0)
    body = (f"groq-api GET /models n={n} has {DEFAULT_MODEL}") if live else ""
    return {"ok": live, "rc": 0 if live else 2, "body": body,
            "body_bytes": len(body.encode("utf-8")),
            "model": DEFAULT_MODEL if live else "",
            "model_source": "GET /models id list",
            "detail": str(detail)[:300]}


def _github_forge_live_call(paths: CosmosPaths) -> dict:
    return _forge_live_call(paths, "github-forge")


def _gitlab_forge_live_call(paths: CosmosPaths) -> dict:
    return _forge_live_call(paths, "gitlab-forge")


def _copilot_live_call(paths: CosmosPaths) -> dict:
    """Real GET /agents/tasks. Never POST. Never `gh agent-task create`.

    The vendor names the rate-limit resource `mission_control` and the
    documented actor is `copilot-swe-agent`. The constant is emitted ONLY
    when the live header is present — a spec file cannot forge it.
    """
    from cosmos_copilot_rail import CopilotRail, key_path_for, load_spec, spec_path_for
    sp = spec_path_for(paths)
    spec = load_spec(sp if sp.exists() else None)
    rail = CopilotRail(key_path_for(paths, spec), spec)
    ok, detail = rail.probe()
    ident = rail.last_identity() or {}
    bound = str(ident.get("bound") or "")
    live = bool(ok and bound)
    body = (f"github-copilot GET /agents/tasks http={ident.get('http')} "
            f"n={ident.get('n_tasks')} resource={ident.get('resource')} "
            f"date={ident.get('date')}") if live else ""
    return {"ok": live, "rc": 0 if live else 2, "body": body,
            "body_bytes": len(body.encode("utf-8")),
            "model": bound if live else "",
            "model_source": "GET /agents/tasks x-ratelimit-resource=mission_control",
            "detail": str(detail)[:300]}


# satellite name -> (the rail module that speaks for it, its prove-shaped call).
# ONE table: "which module IS this rail?" and "what do I call to prove it?" are
# read off the same row, so the two answers cannot drift apart.
SATELLITES = {
    "cursor": ("cosmos_cursor_rail", _cursor_live_call),
    "firecrawl": ("cosmos_firecrawl_rail", _firecrawl_live_call),
    "groq": ("cosmos_groq_rail", _groq_live_call),
    "playwright": ("cosmos_playwright_rail", _playwright_live_call),
    "github-forge": ("cosmos_forge_rail", _github_forge_live_call),
    "gitlab-forge": ("cosmos_forge_rail", _gitlab_forge_live_call),
    "github-copilot": ("cosmos_copilot_rail", _copilot_live_call),
    "codex": ("cosmos_codex_rail", _codex_live_call),
}


def probe_module_for(spec: dict) -> str:
    """The rail module that speaks for a wired row -- its OWN, never a default.

    MEASURED 2026-08-31, the F-24 wiring's second escape: a consumer that wants
    "which module do I probe this rail with" derived it as
    `spec.get("module") or "cosmos_claude_rail"`. That reads correctly for the
    incumbent rows (module="bts_*") and for claude-cli, and WRONGLY for every
    satellite -- those rows carry module=None and name their rail in
    `satellite`, so cursor-api, firecrawl-web and playwright-dom each fell
    through to the ANTHROPIC rail. builds/probe/MESH_STATUS.md consequently
    reported all three refusing "NO_KEY: Anthropic key missing at
    live/config/anthropic_api_key.txt" -- a credential none of the three uses,
    for a rail that was proving live at that moment.

    Same lesson as the double-count that shipped beside it: the four rails moved
    from `mesh_blockers.UNWIRED_ROWS` (where each named its own probe module) to
    `WIRED_NODES` (where none did), and what they carried was left behind. The
    table's owner names the module; a consumer that guesses gets it wrong.
    """
    sat = spec.get("satellite")
    return (spec.get("module")
            or (SATELLITES[sat][0] if sat else "cosmos_claude_rail"))


def default_live_call(paths: CosmosPaths, spec: dict):
    def _call():
        if spec.get("module"):
            return _node_live_call(paths, spec["module"])
        sat = spec.get("satellite")
        if sat:
            return SATELLITES[sat][1](paths)
        return _claude_live_call(paths)
    return _call


def open_registry(paths: CosmosPaths):
    """Authority ledger + Registry. No key → None (fail-closed, no invented key)."""
    keyfile = paths.config("install_key.bin")
    if not keyfile.exists():
        return None
    from cosmos_ledger import Ledger
    from cosmos_registry import Registry
    led_dir = paths.ledger()
    led_dir.mkdir(parents=True, exist_ok=True)
    led = Ledger(led_dir / "authority.jsonl", keyfile.read_bytes(), WORKER)
    return Registry(led)


def _claude_configured(paths: CosmosPaths) -> bool:
    return (paths.config("anthropic_api_key.txt").exists()
            or paths.config("claude_rail.json").exists())


def _hands_configured(paths: CosmosPaths, spec: dict) -> bool:
    """Does THIS runtime root have something to ask this rail with?

    Existence only -- never a read. Key material is Keith's; the prober needs
    to know a credential is present, never what it says.
    """
    if spec.get("module"):
        from cosmos_node_rails import resolve_incumbent_root
        return bool(resolve_incumbent_root(paths))
    sat = spec.get("satellite")
    if sat == "cursor":
        from cosmos_cursor_rail import KEY_NAME, SPEC_NAME
        return (paths.config(SPEC_NAME).exists()
                and paths.config(KEY_NAME).exists())
    if sat == "firecrawl":
        # Keyless by design, so the spec file its own --gate writes IS the
        # configuration fact. A bare install has none and stays offline.
        from cosmos_firecrawl_rail import SPEC_NAME
        return paths.config(SPEC_NAME).exists()
    if sat == "groq":
        from cosmos_groq_rail import KEY_NAME
        return paths.config(KEY_NAME).exists()
    if sat == "playwright":
        from cosmos_playwright_rail import SPEC_NAME, find_pinned_cli
        return (paths.config(SPEC_NAME).exists()
                and (find_pinned_cli() is not None
                     or bool(shutil.which("npx"))))
    if sat in ("github-forge", "gitlab-forge"):
        # Keyless: gh/glab tokens live in the OS keyring. The spec file this
        # rail's --write-spec produces IS the configuration fact, matching
        # firecrawl. A bare install has none and stays offline -- PATH
        # presence of gh is NOT enough, because that would spend a live
        # REST call from poll_once(live=False) on every machine that has
        # the CLI.
        from cosmos_forge_rail import SPEC_NAME
        return paths.config(SPEC_NAME).exists()
    if sat == "github-copilot":
        # Spec file is the configuration fact (same as forge/firecrawl).
        # PATH of gh / GH_TOKEN in the environment is NOT enough — that
        # would spend GET /agents/tasks from poll_once(live=False).
        from cosmos_copilot_rail import SPEC_NAME
        return paths.config(SPEC_NAME).exists()
    if sat == "codex":
        # Existence only -- never a read. The rail itself reads the key at
        # dispatch time. A spec overlay is optional (load_spec handles None);
        # the key file is the configuration fact.
        from cosmos_codex_rail import KEY_NAME
        return paths.config(KEY_NAME).exists()
    return _claude_configured(paths)


def _should_live_probe(paths: CosmosPaths, registry, spec: dict, *,
                       live: bool, ttl_s: float, injected: bool = False) -> bool:
    """Ask this rail now?

    A satellite is asked ONLY where this root configures it, and `live` does
    not override that: forcing a satellite this root has never configured
    cannot produce a proof, and for playwright-dom it would spawn a browser
    server in order to fail. `injected` lifts that one guard and nothing else,
    because a caller-supplied live_call IS the configuration -- a test double
    needs no key on disk.

    Everything after this is unchanged, deliberately. The model/CLI hands keep
    the old `live` semantics exactly (claude-cli's prepaid SEAT answers with no
    key file present, so gating IT on hands would break the path that works),
    and `live=False` still refuses to spend even on an injected call - that is
    the "poll_once without hands configured does not spend" invariant.

    ALL rails: the 1-minute clock never dispatches. A failed Codex prove
    (`BROKE: missing real model field`) never entered live_nodes, so TTL
    could not save us — that billed gpt-5.6-sol every minute. Rail prove
    is `--live` only (Keith request + permission). PATH/HTTP are identity.
    """
    if not live and not injected:
        return False
    if spec.get("satellite") and not injected and not _hands_configured(paths, spec):
        return False
    if live:
        return True
    row = registry.live_nodes().get(spec["link_id"])
    if row:
        age = row.get("age_s")
        if age is not None and age < ttl_s:
            return False
    return _hands_configured(paths, spec)


def map_wired_nodes(paths: CosmosPaths, registry, *, live: bool = False,
                    live_calls: dict | None = None,
                    ttl_s: float = NODE_PROOF_TTL_S) -> list[dict]:
    """Prove each wired rail. Unanswered nodes are not registered."""
    out = []
    for spec in WIRED_NODES:
        lid = spec["link_id"]
        call = (live_calls or {}).get(lid)
        if not _should_live_probe(paths, registry, spec, live=live,
                                  ttl_s=ttl_s, injected=call is not None):
            row = registry.live_nodes().get(lid)
            if not live and call is None:
                skip = SKIP_REQUIRES_LIVE
            elif row:
                skip = "fresh"
            else:
                skip = "no-hands-configured"
            out.append({**row, "skipped": skip} if row else
                       {"link_id": lid, "ok": False, "registered": False,
                        "skipped": skip})
            continue
        rec = registry.prove(
            lid, spec["rail_type"], spec["src"], spec["dst"],
            call or default_live_call(paths, spec))
        rec["family"] = spec["family"]
        out.append(rec)
    return out


def poll_once(root: str, *, live: bool = False, live_calls: dict | None = None,
              ttl_s: float = NODE_PROOF_TTL_S) -> dict:
    paths = CosmosPaths(root)
    logs = paths.logs()
    logs.mkdir(parents=True, exist_ok=True)
    dest_dir = paths.state("rails")
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / "probe.json"
    t0 = time.time()

    rails = []
    if live:
        cur = _cursor_probe(paths)
        rails.append({"id": "cursor-api", "kind": "API", **cur})
    else:
        rails.append({
            "id": "cursor-api", "kind": "API", "ok": None,
            "detail": SKIP_REQUIRES_LIVE, "skipped": SKIP_REQUIRES_LIVE,
        })

    for name in CLI_RAILS:
        found = shutil.which(name)
        rails.append({
            "id": name, "kind": "CLI", "ok": bool(found),
            "detail": found or "ABSENT",
        })

    for rid, host, port in HTTP_PROBES:
        tcp = _tcp(host, port)
        rec = {"id": rid, "kind": "HTTP", "ok": tcp["ok"],
               "detail": "listening" if tcp["ok"] else tcp.get("error"),
               "rtt_s": tcp["rtt_s"]}
        if rid == "ollama-11434" and tcp["ok"]:
            rec["http"] = _http_head("http://127.0.0.1:11434/api/version")
        rails.append(rec)

    cli_live = [r for r in rails if r.get("ok")]
    node_proofs = []
    runtime = None
    reg = open_registry(paths)
    if reg is not None:
        node_proofs = map_wired_nodes(
            paths, reg, live=live, live_calls=live_calls, ttl_s=ttl_s)
        runtime = reg.file_runtime(paths.role("registry"))
    registered = list((runtime or {}).get("nodes") or [])
    projection = {
        "schema": SCHEMA,
        "measured_at": None,
        "worker": WORKER,
        "live_count": len(cli_live),
        "probed_count": len(rails),
        "rails": rails,
        "nodes": [
            {"link_id": p.get("link_id"), "ok": p.get("ok"),
             "registered": p.get("registered"), "model": p.get("model"),
             "model_source": p.get("model_source"),
             "rc": p.get("rc"), "body_bytes": p.get("body_bytes"),
             "skipped": p.get("skipped"), "detail": p.get("detail")}
            for p in node_proofs
        ],
        "registered": registered,
        "registry": str(paths.role("registry")) if runtime else None,
        "elapsed_s": round(time.time() - t0, 3),
    }
    hb = write_heartbeat(logs / HEARTBEAT_NAME, WORKER, extra={
        "schema": SCHEMA,
        "tick": "once",
        "live_count": len(cli_live),
        "probed_count": len(rails),
        "projection": str(dest),
        "elapsed_s": projection["elapsed_s"],
        "live": [r["id"] for r in cli_live],
        "registered": registered,
        "registered_count": len(registered),
    })
    projection["measured_at"] = hb["last_run"]
    projection["measured_epoch"] = hb["last_run_epoch"]
    atomic_json(dest, projection)
    return {"ok": True, "heartbeat": hb, "projection": str(dest),
            "live_count": len(cli_live), "probed_count": len(rails),
            "registered": registered,
            "registered_count": len(registered),
            "nodes": projection["nodes"],
            "registry": projection["registry"]}


def standup(root: str) -> dict:
    existing = query_task(TASK_NAME)
    script = Path(__file__).resolve()
    tr = tr_cmdline(script, root, "--once")
    if existing.get("ok"):
        tick = poll_once(root, live=False)
        return {"started": "already", "task": existing, "tick": tick,
                "keith_cmd": None, "task_name": TASK_NAME}
    task = create_task(TASK_NAME, tr, "minute", mo=1, run_now=True)
    tick = poll_once(root, live=False)
    return {
        "started": "schtasks" if task.get("ok") else "in-process-tick",
        "task": task,
        "tick": {"live_count": tick.get("live_count"),
                 "probed_count": tick.get("probed_count"),
                 "registered": tick.get("registered"),
                 "registered_count": tick.get("registered_count")},
        "proof": {"ok": True, "heartbeat": tick.get("heartbeat")},
        "keith_cmd": task.get("keith_cmd") if (
            task.get("needs_elevation") or not task.get("ok")) else None,
        "task_name": TASK_NAME,
        "heartbeat_path": str(CosmosPaths(root).logs(HEARTBEAT_NAME)),
    }


def main() -> int:
    ap = argparse.ArgumentParser(prog="cosmos_rails_prober")
    ap.add_argument("--root", required=True)
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--live", action="store_true",
                    help="permissioned rail prove (spend). Default --once is "
                         "identity only: PATH + local HTTP. No rail dispatch.")
    ap.add_argument("--standup", action="store_true")
    ap.add_argument("--status", action="store_true")
    a = ap.parse_args()
    if a.status:
        paths = CosmosPaths(a.root)
        rec = read_heartbeat(paths.logs(HEARTBEAT_NAME))
        age = heartbeat_age_s(rec)
        print(json.dumps({"path": str(paths.logs(HEARTBEAT_NAME)),
                          "age_s": age, "heartbeat": rec}, indent=1,
                         default=str))
        return 0 if age is not None and age < FRESH_S else 2
    if a.standup:
        r = standup(a.root)
        print(json.dumps(r, indent=1, default=str))
        return 0 if r.get("started") in ("already", "schtasks",
                                         "in-process-tick") else 2
    r = poll_once(a.root, live=a.live)
    print(json.dumps({"ok": True, "live_count": r["live_count"],
                      "probed_count": r["probed_count"],
                      "registered": r.get("registered"),
                      "registered_count": r.get("registered_count"),
                      "nodes": r.get("nodes"),
                      "registry": r.get("registry"),
                      "projection": r["projection"],
                      "heartbeat": str(CosmosPaths(a.root).logs(HEARTBEAT_NAME))},
                     indent=1, default=str))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CosmosPathError as e:
        print(e, file=sys.stderr)
        raise SystemExit(2)
