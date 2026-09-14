#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_cred_kit — API keys / SDK / local agents fold.

GET never returns secret material. GET never mkdir. LIVE is a rails probe
already on file, never a fresh vendor poll of 20 hosts.

Keith pastes keys. This TUI does not open vendor billing pages.

    py -3.14 cosmos\\cosmos_cred_kit.py --selftest
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

SCHEMA = "cosmos-cred-kit/1"
CUSTOM_NAME = "cred_custom.json"
CURSOR_COOKBOOK = (
    "https://openrouter.ai/docs/cookbook/coding-agents/cursor-integration"
)
HERMES_COOKBOOK = (
    "https://openrouter.ai/docs/cookbook/coding-agents/hermes-integration"
)
USAGE_COOKBOOK = (
    "https://openrouter.ai/docs/cookbook/administration/usage-accounting"
)
MCP_COOKBOOK = (
    "https://openrouter.ai/docs/cookbook/coding-agents/mcp-servers"
)
CURSOR_OR_BASE = "https://openrouter.ai/api/v1/cursor"
MAX_SECRET = 8_000
MAX_CUSTOM = 40

# Top 20 named sources. File names match existing rails when they exist.
SOURCES = (
    {"id": "openrouter", "label": "OpenRouter", "kind": "API",
     "file": "openrouter_api_key.txt", "env": "OPENROUTER_API_KEY",
     "link_id": "openrouter-api",
     "docs": "https://openrouter.ai/keys",
     "cookbook": CURSOR_COOKBOOK},
    {"id": "openai", "label": "OpenAI", "kind": "API",
     "file": "openai_api_key.txt", "env": "OPENAI_API_KEY",
     "link_id": "oa-api", "docs": "https://platform.openai.com/api-keys"},
    {"id": "anthropic", "label": "Anthropic / Claude", "kind": "API",
     "file": "anthropic_api_key.txt", "env": "ANTHROPIC_API_KEY",
     "docs": "https://console.anthropic.com/settings/keys"},
    {"id": "xai", "label": "xAI / Grok", "kind": "API",
     "file": "xai_api_key.txt", "env": "XAI_API_KEY",
     "link_id": "sgh-api", "docs": "https://console.x.ai"},
    {"id": "google_ai", "label": "Google AI Studio", "kind": "API",
     "file": "google_api_key.txt", "env": "GOOGLE_API_KEY",
     "link_id": "gem-api", "docs": "https://aistudio.google.com/apikey"},
    {"id": "gcloud", "label": "Google Cloud ADC", "kind": "ADC",
     "link_id": "vertex-coding",
     "docs": "https://cloud.google.com/docs/authentication/application-default-credentials"},
    {"id": "groq", "label": "Groq", "kind": "API",
     "file": "groq_api_key.txt", "env": "GROQ_API_KEY",
     "link_id": "groq-api", "docs": "https://console.groq.com/keys"},
    {"id": "cursor", "label": "Cursor", "kind": "API",
     "file": "cursor_api_key.txt", "env": "CURSOR_API_KEY",
     "link_id": "cursor-api",
     "docs": "https://cursor.com/help/models-and-usage/api-keys",
     "cookbook": CURSOR_COOKBOOK},
    {"id": "github", "label": "GitHub", "kind": "CLI",
     "bin": "gh", "docs": "https://github.com/settings/tokens"},
    {"id": "gitlab", "label": "GitLab", "kind": "CLI",
     "bin": "glab", "file": "gitlab_token.txt", "env": "GITLAB_TOKEN",
     "docs": "https://gitlab.com/-/user_settings/personal_access_tokens"},
    {"id": "gitlab_trigger", "label": "GitLab CI trigger token", "kind": "API",
     "file": "gitlab_trigger_token.txt", "link_id": "gitlab-duo-com",
     "docs": "https://docs.gitlab.com/ci/triggers/"},
    {"id": "huggingface", "label": "Hugging Face", "kind": "API",
     "file": "hf_api_key.txt", "env": "HF_TOKEN",
     "docs": "https://huggingface.co/settings/tokens"},
    {"id": "mistral", "label": "Mistral", "kind": "API",
     "file": "mistral_api_key.txt", "env": "MISTRAL_API_KEY",
     "docs": "https://console.mistral.ai/api-keys"},
    {"id": "together", "label": "Together", "kind": "API",
     "file": "together_api_key.txt", "env": "TOGETHER_API_KEY",
     "docs": "https://api.together.ai"},
    {"id": "fireworks", "label": "Fireworks", "kind": "API",
     "file": "fireworks_api_key.txt", "env": "FIREWORKS_API_KEY",
     "docs": "https://fireworks.ai/api-keys"},
    {"id": "perplexity", "label": "Perplexity", "kind": "API",
     "file": "perplexity_api_key.txt", "env": "PERPLEXITY_API_KEY",
     "docs": "https://www.perplexity.ai/settings/api"},
    {"id": "deepseek", "label": "DeepSeek", "kind": "API",
     "file": "deepseek_api_key.txt", "env": "DEEPSEEK_API_KEY",
     "docs": "https://platform.deepseek.com/api_keys"},
    {"id": "cohere", "label": "Cohere", "kind": "API",
     "file": "cohere_api_key.txt", "env": "COHERE_API_KEY",
     "docs": "https://dashboard.cohere.com/api-keys"},
    {"id": "azure_openai", "label": "Azure OpenAI", "kind": "API",
     "file": "azure_openai_api_key.txt", "env": "AZURE_OPENAI_API_KEY",
     "docs": "https://learn.microsoft.com/azure/ai-foundry"},
    {"id": "aws_bedrock", "label": "AWS Bedrock", "kind": "CLI",
     "bin": "aws", "docs": "https://docs.aws.amazon.com/bedrock/"},
    {"id": "hermes", "label": "Hermes Agent", "kind": "CLI",
     "bin": "hermes", "env": "OPENROUTER_API_KEY",
     "grab": "hermes_env",
     "docs": HERMES_COOKBOOK, "cookbook": HERMES_COOKBOOK},
)

AGENTS = (
    {"id": "sdk_openai", "label": "OpenAI SDK", "kind": "SDK",
     "module": "openai"},
    {"id": "sdk_anthropic", "label": "Anthropic SDK", "kind": "SDK",
     "module": "anthropic"},
    {"id": "sdk_google", "label": "Google GenAI SDK", "kind": "SDK",
     "module": "google.genai"},
    {"id": "sdk_groq", "label": "Groq SDK", "kind": "SDK",
     "module": "groq"},
    {"id": "cli_grok", "label": "grok CLI", "kind": "CLI", "bin": "grok"},
    {"id": "cli_claude", "label": "claude CLI", "kind": "CLI", "bin": "claude"},
    {"id": "cli_gemini", "label": "gemini CLI", "kind": "CLI", "bin": "gemini"},
    {"id": "cli_codex", "label": "Codex CLI", "kind": "CLI", "bin": "codex"},
    {"id": "cli_hermes", "label": "Hermes Agent CLI", "kind": "CLI",
     "bin": "hermes", "cookbook": HERMES_COOKBOOK},
    {"id": "cli_cursor", "label": "Cursor CLI / Cloud Agents", "kind": "CLI",
     "bin": "cursor", "cookbook": CURSOR_COOKBOOK},
    {"id": "local_ollama", "label": "Ollama (localhost)", "kind": "LOCAL",
     "bin": "ollama", "host": "http://127.0.0.1:11434"},
    {"id": "local_lmstudio", "label": "LM Studio", "kind": "LOCAL",
     "bin": "lms", "host": "http://127.0.0.1:1234"},
    {"id": "local_vllm", "label": "vLLM", "kind": "LOCAL",
     "host": "http://127.0.0.1:8000"},
    {"id": "local_llamacpp", "label": "llama.cpp server", "kind": "LOCAL",
     "bin": "llama-server", "host": "http://127.0.0.1:8080"},
)

SOURCE_IDS = frozenset(s["id"] for s in SOURCES)


class CredError(RuntimeError):
    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def _gcloud_cmd() -> str:
    win = Path(r"C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd")
    if win.is_file():
        return str(win)
    return shutil.which("gcloud") or "gcloud"


def _which(name: str) -> str | None:
    return shutil.which(name) or shutil.which(name + ".exe")


def _file_present(paths, name: str | None) -> bool:
    if not name:
        return False
    try:
        return paths.config(name).is_file()
    except Exception:  # noqa: BLE001
        return False


def _led(*, present: bool, live) -> str:
    if live is True:
        return "LIVE"
    if present:
        return "PRESENT"
    return "NO_SOURCE"


_GCLOUD_CACHE = {"at": 0.0, "rec": None}


def gcloud_accounts() -> dict:
    now = time.time()
    if _GCLOUD_CACHE["rec"] is not None and (now - _GCLOUD_CACHE["at"]) < 60:
        return _GCLOUD_CACHE["rec"]
    cmd = _gcloud_cmd()
    if not shutil.which(cmd) and not Path(cmd).is_file():
        return {"kind": "NO_SOURCE", "accounts": [], "bin": None}
    try:
        p = subprocess.run(
            [cmd, "auth", "list", "--format=json"],
            capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=6,
        )
    except (OSError, subprocess.TimeoutExpired) as e:
        return {"kind": "BROKE", "accounts": [],
                "detail": f"{type(e).__name__}: {e}"[:160], "bin": cmd}
    if p.returncode != 0:
        return {"kind": "NO_SOURCE", "accounts": [], "bin": cmd,
                "detail": (p.stderr or p.stdout or "")[:160]}
    try:
        rows = json.loads(p.stdout or "[]")
    except json.JSONDecodeError:
        return {"kind": "BROKE", "accounts": [], "bin": cmd,
                "detail": "auth list was not JSON"}
    accts = []
    if isinstance(rows, list):
        for r in rows:
            if not isinstance(r, dict):
                continue
            accts.append({
                "account": r.get("account"),
                "status": r.get("status"),
                "active": str(r.get("status") or "").upper() == "ACTIVE",
            })
    rec = {"kind": "OK" if accts else "NO_SOURCE", "accounts": accts, "bin": cmd}
    _GCLOUD_CACHE["at"] = now
    _GCLOUD_CACHE["rec"] = rec
    return rec


def load_custom(paths) -> list[dict]:
    p = paths.config(CUSTOM_NAME)
    if not p.is_file():
        return []
    try:
        rec = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    rows = rec.get("sources") if isinstance(rec, dict) else None
    if not isinstance(rows, list):
        return []
    out = []
    for r in rows:
        if isinstance(r, dict) and str(r.get("id") or "").strip():
            out.append({
                "id": str(r["id"]).strip().lower()[:40],
                "label": str(r.get("label") or r["id"])[:80],
                "kind": str(r.get("kind") or "API")[:12],
                "file": str(r.get("file") or "")[:80] or None,
                "custom": True,
            })
    return out[:MAX_CUSTOM]


def save_custom(paths, rows: list[dict]) -> dict:
    p = paths.config(CUSTOM_NAME)
    p.parent.mkdir(parents=True, exist_ok=True)
    body = {"schema": SCHEMA, "sources": rows[:MAX_CUSTOM]}
    p.write_text(json.dumps(body, indent=2) + "\n", encoding="utf-8")
    return body


def _row_for(src: dict, paths, rails: dict) -> dict:
    fid = src.get("file")
    present = _file_present(paths, fid)
    if src.get("kind") == "CLI" and src.get("bin"):
        present = present or bool(_which(src["bin"]))
    if src.get("id") == "hermes":
        present = present or bool(_which("hermes")) or (
            Path.home() / ".hermes" / ".env").is_file()
    link = src.get("link_id")
    live = None
    if link and isinstance(rails.get(link), dict):
        live = rails[link].get("verified")
    rec = {
        "id": src["id"],
        "label": src["label"],
        "kind": src["kind"],
        "file": fid,
        "docs": src.get("docs"),
        "cookbook": src.get("cookbook"),
        "present": bool(present),
        "live": live,
        "led": _led(present=bool(present), live=live),
        "custom": bool(src.get("custom")),
    }
    if src.get("id") == "gcloud":
        g = gcloud_accounts()
        rec["gcloud"] = {"kind": g.get("kind"), "n": len(g.get("accounts") or []),
                         "accounts": g.get("accounts") or []}
        rec["present"] = g.get("kind") == "OK"
        rec["led"] = _led(present=rec["present"], live=live)
    return rec


def snapshot(paths, *, rails: dict | None = None) -> dict:
    rails = rails or {}
    custom = load_custom(paths)
    rows = [_row_for(s, paths, rails) for s in SOURCES]
    rows.extend(_row_for(s, paths, rails) for s in custom)
    return {
        "schema": SCHEMA,
        "ok": True,
        "n": len(rows),
        "sources": rows,
        "cursor_cookbook": {
            "url": CURSOR_COOKBOOK,
            "base_url": CURSOR_OR_BASE,
            "note": "Cursor Settings → Models → API Keys → OpenAI key = OpenRouter "
                    "sk-or-… · Override OpenAI Base URL = "
                    + CURSOR_OR_BASE,
        },
        "hermes_cookbook": {"url": HERMES_COOKBOOK},
        "usage_cookbook": {
            "url": USAGE_COOKBOOK,
            "note": "Usage is always in the chat response (native tokenizer, "
                    "cost, cache). Do not send usage.include — deprecated. "
                    "GET /generation?id= is the async audit. Not a billing page.",
        },
        "mcp_cookbook": {
            "url": MCP_COOKBOOK,
            "note": "MCP tools/list → OpenAI tools for OpenRouter chat. "
                    "Named pins (cosmos, playwright, mcp:openwork/github/bts). "
                    "Does not vendor @openrouter/mcp. Cookbook filesystem "
                    "write_file on /Applications is REFUSED.",
        },
        "plugin": {
            "targets": ["cdeck", "openwork"],
            "rpc": ["/api/v1/cred", "/api/v1/agents"],
            "note": "RPC-shaped fold. Not a published OpenWork pack.",
        },
        "does_not_echo_secret": True,
        "note": "LED LIVE is a rails probe already on file, not a 20-host poll. "
                "Keith pastes keys. GET never mkdir.",
    }


def agents_snapshot() -> dict:
    rows = []
    for a in AGENTS:
        present = False
        if a.get("bin"):
            present = bool(_which(a["bin"]))
        if a.get("module"):
            try:
                present = present or (__import__(a["module"].split(".", 1)[0]) is not None)
            except Exception:  # noqa: BLE001
                pass
        rows.append({
            "id": a["id"], "label": a["label"], "kind": a["kind"],
            "bin": a.get("bin"), "module": a.get("module"),
            "host": a.get("host"), "cookbook": a.get("cookbook"),
            "present": present,
            "led": "PRESENT" if present else "NO_SOURCE",
        })
    return {
        "schema": SCHEMA,
        "ok": True,
        "agents": rows,
        "n": len(rows),
        "note": "SDK / CLI / localhost agents. Presence is PATH or import, "
                "not a live session. Not a published plugin pack.",
        "plugin": {"targets": ["cdeck", "openwork"], "rpc": "/api/v1/agents"},
    }


def _secret_path(paths, src: dict) -> Path:
    name = src.get("file")
    if not name:
        raise CredError("REFUSED", f"{src['id']} has no key file (CLI/ADC)")
    return paths.config(name)


def set_secret(paths, source_id: str, secret: str) -> dict:
    sid = str(source_id or "").strip().lower()
    src = next((s for s in SOURCES if s["id"] == sid), None)
    if src is None:
        src = next((s for s in load_custom(paths) if s["id"] == sid), None)
    if src is None:
        raise CredError("BAD_INPUT", f"unknown source {sid!r}")
    val = str(secret or "").strip()
    if not val or len(val) > MAX_SECRET:
        raise CredError("BAD_INPUT", "empty or oversized secret")
    if "\x00" in val:
        raise CredError("BAD_INPUT", "NUL in secret")
    dest = _secret_path(paths, src)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(val + "\n", encoding="utf-8")
    return snapshot(paths)


def delete_secret(paths, source_id: str) -> dict:
    sid = str(source_id or "").strip().lower()
    src = next((s for s in list(SOURCES) + load_custom(paths) if s["id"] == sid), None)
    if src is None:
        raise CredError("BAD_INPUT", f"unknown source {sid!r}")
    dest = _secret_path(paths, src)
    if dest.is_file():
        trash = dest.parent / "_delme"
        trash.mkdir(parents=True, exist_ok=True)
        stamp = time.strftime("%Y%m%dT%H%M%S")
        dest.replace(trash / f"{dest.name}.{stamp}")
    return snapshot(paths)


def grab_secret(paths, source_id: str) -> dict:
    """Copy from env / well-known file into live/config. Does not echo."""
    sid = str(source_id or "").strip().lower()
    src = next((s for s in list(SOURCES) + load_custom(paths) if s["id"] == sid), None)
    if src is None:
        raise CredError("BAD_INPUT", f"unknown source {sid!r}")
    val = ""
    envn = src.get("env")
    if envn:
        val = str(os.environ.get(envn) or "").strip()
    if not val and src.get("grab") == "hermes_env":
        envp = Path.home() / ".hermes" / ".env"
        if envp.is_file():
            for line in envp.read_text(encoding="utf-8", errors="replace").splitlines():
                if line.startswith("OPENROUTER_API_KEY="):
                    val = line.split("=", 1)[1].strip().strip('"').strip("'")
                    break
    if not val:
        raise CredError("NO_SOURCE", f"no env/file to grab for {sid}")
    return set_secret(paths, sid, val)


def add_custom(paths, *, source_id: str, label: str, kind: str = "API") -> dict:
    sid = str(source_id or "").strip().lower()
    if not sid or sid in SOURCE_IDS:
        raise CredError("BAD_INPUT", "id empty or collides with a named source")
    rows = load_custom(paths)
    if any(r["id"] == sid for r in rows):
        raise CredError("BAD_INPUT", "custom id already exists")
    if len(rows) >= MAX_CUSTOM:
        raise CredError("REFUSED", "custom catalog full")
    rows.append({
        "id": sid, "label": str(label or sid)[:80],
        "kind": str(kind or "API")[:12],
        "file": f"{sid}_api_key.txt", "custom": True,
    })
    save_custom(paths, rows)
    return snapshot(paths)


def _selftest() -> int:
    import tempfile
    from cosmos_kernel import install
    from cosmos_paths import CosmosPaths

    results = []

    def check(label, fn):
        try:
            results.append((label, bool(fn()), ""))
        except Exception as e:  # noqa: BLE001
            results.append((label, False, f"{type(e).__name__}: {e}"))

    td = Path(tempfile.mkdtemp(prefix="cosmos_cred_"))
    root = install(td / "live", tree_id="spike-cred")
    paths = CosmosPaths(root)
    rec = snapshot(paths)
    check("GET names 20 sources and does not mkdir custom file",
          lambda: rec["n"] >= 20
          and rec["does_not_echo_secret"] is True
          and not paths.config(CUSTOM_NAME).exists())
    check("Cursor cookbook URL is the OpenRouter /cursor endpoint doc",
          lambda: rec["cursor_cookbook"]["url"] == CURSOR_COOKBOOK
          and rec["cursor_cookbook"]["base_url"].endswith("/cursor"))
    check("usage-accounting cookbook is named, not a credits/billing page",
          lambda: rec["usage_cookbook"]["url"] == USAGE_COOKBOOK
          and "credits" not in rec["usage_cookbook"]["url"])
    check("MCP servers cookbook is named; filesystem example is not a pin",
          lambda: rec["mcp_cookbook"]["url"] == MCP_COOKBOOK
          and "filesystem" in rec["mcp_cookbook"]["note"].lower())
    check("LED is NO_SOURCE when the file is absent",
          lambda: any(s["id"] == "openrouter" and s["led"] == "NO_SOURCE"
                      for s in rec["sources"]))
    saved = set_secret(paths, "openrouter", "sk-or-test-not-real")
    check("SET writes the file and GET still does not echo the secret",
          lambda: paths.config("openrouter_api_key.txt").is_file()
          and "sk-or-test-not-real" not in json.dumps(saved)
          and any(s["id"] == "openrouter" and s["led"] == "PRESENT"
                  for s in saved["sources"]))
    gone = delete_secret(paths, "openrouter")
    check("DELETE stages to _delme, does not echo",
          lambda: not paths.config("openrouter_api_key.txt").is_file()
          and any((paths.config("_delme")).glob("openrouter_api_key.txt.*"))
          and any(s["id"] == "openrouter" and s["led"] == "NO_SOURCE"
                  for s in gone["sources"]))
    os.environ["OPENROUTER_API_KEY"] = "sk-or-grabbed"
    grabbed = grab_secret(paths, "openrouter")
    check("GRAB copies env into the rail file without echoing",
          lambda: paths.config("openrouter_api_key.txt").read_text(encoding="utf-8").startswith("sk-or-grabbed")
          and "sk-or-grabbed" not in json.dumps({k: v for k, v in grabbed.items() if k != "x"}))
    # The file contains the secret; the JSON fold must not.
    check("snapshot JSON does not contain the grabbed secret",
          lambda: "sk-or-grabbed" not in json.dumps(snapshot(paths)))
    cust = add_custom(paths, source_id="acme", label="Acme LLM")
    check("custom source can be added and then keyed",
          lambda: any(s["id"] == "acme" and s.get("custom") for s in cust["sources"]))
    ag = agents_snapshot()
    check("agents fold names SDK CLI LOCAL without inventing a session",
          lambda: ag["n"] >= 8
          and {a["kind"] for a in ag["agents"]} >= {"SDK", "CLI", "LOCAL"}
          and all(a["led"] in ("PRESENT", "NO_SOURCE") for a in ag["agents"]))
    check("plugin block names cDeck and OpenWork RPC, not a published pack",
          lambda: "openwork" in rec["plugin"]["targets"]
          and "published" in rec["plugin"]["note"].lower())

    failed = [(l, e) for l, ok, e in results if not ok]
    for label, ok, err in results:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (cred kit; secrets never in GET)"
          % ("PASS" if not failed else "FAIL", len(results)))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(_selftest())
