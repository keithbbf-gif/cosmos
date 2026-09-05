#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""maker_hands_probe - measure which AI-maker surfaces are REAL HANDS on THIS machine.

An API that exists is not a hand. A hand is a named verb that runs here and returns a
value only that surface can emit. This probe runs the verb and records what came back.

    py -3.14 builds/probe/maker_hands_probe.py --root V:/A/Ai/COSMOS/live

No hard-coded paths: --root is required and verified by sentinel CONTENT (not existence).
Fail-closed: a probe that cannot run is UNMEASURED or ABSENT, never a fabricated pass.
Secrets are never printed - credential probes report presence and the refusal code only.

Verdicts (typed, no fourth state invented at runtime):
    HAND          a verb ran and emitted a value only that surface can produce
    CRED_BLOCKED  surface answered, and refused for want of a credential (Keith's domain)
    ABSENT        binary/endpoint is not on this machine
    UNMEASURED    not probed this pass; `why` says what would close it
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

HAND, CRED, ABSENT, UNMEASURED = "HAND", "CRED_BLOCKED", "ABSENT", "UNMEASURED"

# Substrings that mean "the surface answered, but wants a credential from Keith".
_CRED_MARKS = ("invalid_api_key", "not logged in", "no api key", "unauthorized",
               "authentication", "requires authentication", "401", "403",
               "no_key", "key missing", "missing api key")


class ProbeRefusal(RuntimeError):
    """kind in {NO_SENTINEL, BAD_SENTINEL}. Message stays `KIND: detail` so
    older string prefixes still match; a caller can now branch on `kind`."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        self.detail = detail
        super().__init__(f"{kind}: {detail}")


def _verify_root(root: str) -> dict:
    """Sentinel CONTENT is identity. Existence is not identity."""
    sentinel = Path(root) / ".cosmos-root.json"
    if not sentinel.is_file():
        raise ProbeRefusal("NO_SENTINEL", str(sentinel))
    try:
        doc = json.loads(sentinel.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeDecodeError) as e:
        raise ProbeRefusal("BAD_SENTINEL", f"unreadable: {type(e).__name__}") from e
    if (not isinstance(doc, dict)
            or doc.get("system") != "COSMOS" or not doc.get("tree_id")):
        raise ProbeRefusal("BAD_SENTINEL", repr(doc))
    return doc


def _run(cmd: list[str] | str, timeout: int = 45, shell: bool = False) -> dict:
    """Run a verb. Never raises - a failure is evidence too."""
    t0 = time.time()
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                           shell=shell, cwd=str(REPO), errors="replace")
        return {"rc": p.returncode,
                "out": (p.stdout or "").strip()[:1400],
                "err": (p.stderr or "").strip()[:700],
                "ms": int((time.time() - t0) * 1000)}
    except subprocess.TimeoutExpired:
        return {"rc": None, "out": "", "err": f"TIMEOUT after {timeout}s",
                "ms": int((time.time() - t0) * 1000)}
    except (OSError, ValueError) as e:
        return {"rc": None, "out": "", "err": f"{type(e).__name__}: {e}",
                "ms": int((time.time() - t0) * 1000)}


def _http(url: str, timeout: int = 12, method: str = "GET") -> dict:
    """One unauthenticated request. 401/403 is a measurement, not a failure."""
    t0 = time.time()
    req = urllib.request.Request(url, method=method,
                                 headers={"User-Agent": "cosmos-maker-hands-probe/1"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return {"http": r.status, "body": r.read(600).decode("utf-8", "replace"),
                    "ms": int((time.time() - t0) * 1000)}
    except urllib.error.HTTPError as e:
        return {"http": e.code, "body": e.read(400).decode("utf-8", "replace"),
                "ms": int((time.time() - t0) * 1000)}
    except (urllib.error.URLError, OSError, ValueError) as e:
        return {"http": None, "body": f"{type(e).__name__}: {e}",
                "ms": int((time.time() - t0) * 1000)}


def _mcp(url: str, timeout: int = 25) -> dict:
    """One JSON-RPC `initialize` against a hosted MCP endpoint. A GET proves nothing
    about MCP; the handshake is the named verb. Accepts JSON or SSE framing."""
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                       "params": {"protocolVersion": "2025-06-18", "capabilities": {},
                                  "clientInfo": {"name": "cosmos-probe", "version": "1"}}})
    req = urllib.request.Request(
        url, data=body.encode("utf-8"), method="POST",
        headers={"Content-Type": "application/json",
                 "Accept": "application/json, text/event-stream",
                 "User-Agent": "cosmos-maker-hands-probe/1"})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read(4000).decode("utf-8", "replace")
            code = r.status
    except urllib.error.HTTPError as e:
        raw, code = e.read(1200).decode("utf-8", "replace"), e.code
    except (urllib.error.URLError, OSError, ValueError) as e:
        return {"http": None, "raw": f"{type(e).__name__}: {e}",
                "ms": int((time.time() - t0) * 1000)}
    out = {"http": code, "raw": raw[:900], "ms": int((time.time() - t0) * 1000)}
    for line in raw.splitlines():           # SSE frames carry the payload after "data: "
        payload = line[6:] if line.startswith("data: ") else line
        try:
            doc = json.loads(payload)
        except (json.JSONDecodeError, ValueError):
            continue
        info = (doc.get("result") or {}).get("serverInfo")
        if info:
            out["serverInfo"] = info
            break
    return out


def probe_mcp(name: str, url: str) -> dict:
    res = _mcp(url)
    row = {"candidate": name, "kind": "hosted MCP", "verb": f"POST {url} initialize",
           "need": "serverInfo", "http": res["http"], "ms": res["ms"],
           "evidence": res["raw"][:700]}
    if res.get("serverInfo"):
        row.update(verdict=HAND, serverInfo=res["serverInfo"])
    elif res["http"] is None:
        row["verdict"] = ABSENT
    else:
        row["verdict"] = _classify({"body": res["raw"]}, None)
    return row


def _which(binary: str) -> str | None:
    return shutil.which(binary)


def _classify(res: dict, need: str | None) -> str:
    """HAND only if the emitted text carries the value we demanded."""
    blob = f"{res.get('out', '')}\n{res.get('err', '')}\n{res.get('body', '')}".lower()
    if need and need.lower() in blob:
        return HAND
    if any(m in blob for m in _CRED_MARKS):
        return CRED
    return UNMEASURED


def probe_cli(name: str, binary: str, verb: list[str], need: str,
              timeout: int = 45) -> dict:
    """Binary on PATH + a named verb that emits `need`."""
    path = _which(binary)
    row = {"candidate": name, "kind": "CLI", "binary": binary, "resolved": path}
    if not path:
        row.update(verdict=ABSENT, verb=" ".join(verb),
                   evidence=f"{binary}: NOT_ON_PATH", need=need)
        return row
    res = _run([path] + verb[1:] if verb[0] == binary else verb, timeout=timeout)
    verdict = _classify(res, need)
    # A non-zero exit can never be a HAND, however inviting its output looks. Python
    # tracebacks echo the failing SOURCE LINE, so a `need` token quoted in the command
    # comes back verbatim from a crash - a substring match alone scores that as a pass.
    if verdict == HAND and res["rc"] != 0:
        verdict = CRED if _classify(res, None) == CRED else UNMEASURED
    row.update(verdict=verdict, verb=" ".join(verb), need=need,
               rc=res["rc"], ms=res["ms"],
               evidence=(res["out"] or res["err"])[:900])
    return row


def probe_http(name: str, url: str, need: str, timeout: int = 12) -> dict:
    res = _http(url, timeout=timeout)
    row = {"candidate": name, "kind": "HTTP", "verb": f"GET {url}", "need": need,
           "http": res["http"], "ms": res["ms"], "evidence": res["body"][:600]}
    if res["http"] is None:
        row["verdict"] = ABSENT
    else:
        row["verdict"] = _classify(res, need)
    return row


def probe_rail(name: str, module: str, root: str, timeout: int = 180) -> dict:
    """A COSMOS satellite rail's own --probe. This is the only in-mesh evidence class."""
    script = REPO / "cosmos" / f"{module}.py"
    row = {"candidate": name, "kind": "COSMOS rail", "module": module,
           "verb": f"py -3.14 cosmos/{module}.py --root <root> --probe"}
    if not script.is_file():
        row.update(verdict=ABSENT, evidence=f"{script.name}: NOT_IN_TREE")
        return row
    res = _run([sys.executable, str(script), "--root", root, "--probe"], timeout=timeout)
    body = res["out"] or res["err"]
    row.update(rc=res["rc"], ms=res["ms"], evidence=body[:900])
    try:
        doc = json.loads(body)
    except (json.JSONDecodeError, TypeError):
        row["verdict"] = CRED if any(m in body.lower() for m in _CRED_MARKS) else UNMEASURED
        return row
    row["parsed"] = {k: doc.get(k) for k in
                     ("ok", "link_id", "tool_count", "primaryId", "http", "gate")
                     if doc.get(k) is not None}
    row["verdict"] = HAND if doc.get("ok") else (
        CRED if any(m in body.lower() for m in _CRED_MARKS) else UNMEASURED)
    return row


def probe_kernel_compose(root: str) -> dict:
    """Does the running Kernel actually attach rails on a writing boot? Read-only dry-run."""
    script = REPO / "builds" / "probe" / "core8770_dryrun.py"
    row = {"candidate": "Kernel rail composition", "kind": "live tree",
           "verb": "py -3.14 builds/probe/core8770_dryrun.py --root <root>"}
    if not script.is_file():
        row.update(verdict=UNMEASURED, evidence="core8770_dryrun.py absent")
        return row
    res = _run([sys.executable, str(script), "--root", root], timeout=240)
    row.update(rc=res["rc"], ms=res["ms"], evidence=(res["out"] or res["err"])[:1400])
    row["verdict"] = HAND if res["rc"] == 0 else UNMEASURED
    return row


def config_names(root: str) -> list[str]:
    """File NAMES only. Never values - credentials are Keith's domain."""
    d = Path(root) / "config"
    return sorted(p.name for p in d.iterdir()) if d.is_dir() else []


def main() -> int:
    ap = argparse.ArgumentParser(prog="maker_hands_probe")
    ap.add_argument("--root", required=True)
    ap.add_argument("--out", default=None, help="JSON evidence file (default builds/probe/)")
    ap.add_argument("--skip-rails", action="store_true",
                    help="skip the slow COSMOS rail --probe pass")
    a = ap.parse_args()

    try:
        sentinel = _verify_root(a.root)
    except ProbeRefusal as e:
        print(json.dumps({"ok": False, "refusal": str(e)}, indent=1))
        return 2

    rows: list[dict] = []

    # --- forges: CLI hands whose auth is the whole question -------------------
    rows.append(probe_cli("GitHub gh", "gh", ["gh", "auth", "status"], "logged in to"))
    rows.append(probe_cli("GitHub gh (repo verb)", "gh",
                          ["gh", "repo", "view", "--json", "isPrivate,visibility"],
                          "isprivate"))
    rows.append(probe_cli("GitLab glab", "glab", ["glab", "auth", "status"],
                          "logged in to gitlab.com"))
    rows.append(probe_cli("GitLab glab (ci verb)", "glab", ["glab", "ci", "status"], "pipeline"))

    # --- coding-agent CLIs: presence is cheap, WALLET is the question ---------
    rows.append(probe_cli("Codex CLI", "codex", ["codex", "login", "status"], "logged in"))
    rows.append(probe_cli("Gemini CLI", "gemini", ["gemini", "--version"], "."))
    rows.append(probe_cli("Claude Code CLI", "claude", ["claude", "--version"], "claude code"))
    rows.append(probe_cli("Grok CLI", "grok", ["grok", "--version"], "."))
    rows.append(probe_cli("Aider", "aider", ["aider", "--version"], "aider"))

    # --- forge REST verbs: a quota value only the forge can emit --------------
    rows.append(probe_cli("GitHub REST quota", "gh",
                          ["gh", "api", "rate_limit", "--jq", ".resources.core"], "limit"))
    rows.append(probe_cli("GitLab REST verb", "glab", ["glab", "api", "user"], "username"))

    # --- MCP spawn substrate --------------------------------------------------
    rows.append(probe_cli("Node (MCP stdio host)", "node", ["node", "--version"], "v"))
    rows.append(probe_cli("uvx (MCP Fetch spawn path)", "uvx", ["uvx", "--version"], "uv"))
    # `need` must be a token only SUCCESS can print - a traceback quoting the import
    # line would otherwise score as a pass. That is the fabricated-pass class.
    rows.append(probe_cli("MCP python SDK (Fetch alt path)", "py",
                          ["py", "-3.14", "-c",
                           "import mcp;print('MCP_SDK_PRESENT', mcp.__file__)"],
                          "MCP_SDK_PRESENT"))

    # --- keyless hosted MCP: docs hands that need no credential ---------------
    rows.append(probe_mcp("xAI Docs MCP", "https://docs.x.ai/api/mcp"))
    rows.append(probe_mcp("OpenAI Docs MCP", "https://developers.openai.com/mcp"))

    # --- what the agent hosts already have mounted ----------------------------
    rows.append(probe_cli("Grok MCP host config", "grok", ["grok", "mcp", "list"], "."))
    rows.append(probe_cli("Codex MCP host config", "codex", ["codex", "mcp", "list"], "."))

    # --- local + metered HTTP surfaces ---------------------------------------
    rows.append(probe_http("Ollama local", "http://127.0.0.1:11434/api/version", "version"))
    rows.append(probe_http("Groq API", "https://api.groq.com/openai/v1/models", "\"data\""))
    rows.append(probe_http("COSMOS Core :8770", "http://127.0.0.1:8770/api/v1/health", "ok"))

    # --- already-wired COSMOS rails: the only in-mesh evidence ----------------
    if not a.skip_rails:
        for nm, mod in (("Playwright MCP rail", "cosmos_playwright_rail"),
                        ("Firecrawl rail", "cosmos_firecrawl_rail"),
                        ("Cursor rail", "cosmos_cursor_rail"),
                        ("Codex rail", "cosmos_codex_rail"),
                        ("Claude rail", "cosmos_claude_rail")):
            rows.append(probe_rail(nm, mod, a.root))
        rows.append(probe_kernel_compose(a.root))

    tally: dict[str, int] = {}
    for r in rows:
        tally[r["verdict"]] = tally.get(r["verdict"], 0) + 1

    doc = {"ok": True, "schema": "cosmos-maker-hands-probe/1",
           "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "tree_id": sentinel["tree_id"], "root": a.root,
           "host": platform.node(), "python": sys.version.split()[0],
           "config_names": config_names(a.root),
           "tally": tally, "rows": rows}

    out = Path(a.out) if a.out else REPO / "builds" / "probe" / "maker_hands_evidence.json"
    out.write_text(json.dumps(doc, indent=1), encoding="utf-8")
    print(json.dumps({k: doc[k] for k in
                      ("ok", "ts", "tree_id", "host", "tally", "config_names")}, indent=1))
    print(f"evidence -> {out}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ProbeRefusal as e:
        print(json.dumps({"ok": False, "refusal": str(e)}))
        raise SystemExit(2)
