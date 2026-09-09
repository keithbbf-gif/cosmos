#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Compose live Crucible critics. POST /api/v1/crucible is 501 until these
are attached (tests inject fakes; production attach is serve() only).

GROK WALLETS (docs/research/XAI_GROK_HANDS.md) — do not mix:
  grok-sgh   grok CLI, XAI_API_KEY unset → SuperGrok Heavy weekly pool
  sgh-api    bts_sgh / Console key         → metered api.x.ai credits

GOOGLE WALLETS — do not collapse:
  vertex-coding  orders.ggn@gmail.com (Kelly Gregory display) COSMOS $300
  gem-api        Joanna.bbf — OpenWork, not this critic once coding spec exists
  $580 was Joanna+Ranny combined, not a keith.bbf overflow.

Crucible needs disagreeing *families*. grok-sgh and sgh-api are one
family; attach at most one Grok critic (prefer grok-sgh so SGH is spent).
Never attach claude-cli while ANTHROPIC_OFF. gw-api is the same Grok
family as sgh-api. Never Activate the Joanna billing account.

    attach_crucible_critics(kernel)   # serve() only — not Kernel.__init__
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cosmos_rail_base import CREATE_NO_WINDOW  # noqa: E402

GROK_SGH = "grok-sgh"
GROK_CONSOLE = "sgh-api"
GEM = "gem-api"
OA = "oa-api"
GROK_MODEL = "grok-4.6"
MAX_PACKET_CHARS = 120_000
GROK_TIMEOUT_S = 180
GROK_MAX_TURNS = "3"
# Distinct from kernel adapters["gem-api"] / bts_gem (Studio mix).
# COSMOS Vertex spend is orders.ggn (`vertex-coding`), not Joanna.
VERTEX_SPEND = "vertex-coding"
VERTEX_CAP_USD = 300.0
OA_TERRA_ID = "gpt-5.6-terra"
ARGV_PROMPT_MAX = 1800

# Same-vendor as grok-sgh / sgh-api — never a second family.
GROK_FAMILY_LINKS = frozenset({GROK_CONSOLE, "gw-api", "grok", "g46-grok"})
ANTHROPIC_OFF_LINKS = frozenset({"claude-cli", "anthropic-api", "claude"})

CRITIC_PROMPT = (
    "You are a Crucible critic. Do not explore the repo. Do not list files. "
    "The packet is in this message (and PACKET.md). Reply with ONLY a markdown "
    "json fence, nothing else:\n"
    "```json\n"
    '[{"id":"FAM-1","topic":"short-topic","finding":"...","severity":"HIGH|MED|LOW"}]\n'
    "```\n"
    "Replace FAM with your critic name. Name real problems. "
    "Do not write the COSMOS live tree. Do not git push."
)


class CriticError(RuntimeError):
    """kind in {NO_RAIL, EMPTY_OUTPUT, ANTHROPIC_OFF}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def grok_sgh_env(base: dict | None = None) -> dict:
    """SuperGrok wallet: leftover XAI_API_KEY would steal the weekly pool onto Console."""
    env = dict(os.environ if base is None else base)
    env.pop("XAI_API_KEY", None)
    return env


def grok_sgh_argv(prompt: str, cwd: str, model: str = GROK_MODEL) -> list[str]:
    return [
        "grok", "--single", prompt, "-m", model,
        "--output-format", "plain", "--always-approve",
        "--max-turns", GROK_MAX_TURNS, "--cwd", cwd,
    ]


def _run_grok(argv: list[str], *, cwd: str, env: dict, run=subprocess.run):
    kw = dict(args=argv, cwd=cwd, env=env, capture_output=True, text=True,
              timeout=GROK_TIMEOUT_S, encoding="utf-8", errors="replace")
    if CREATE_NO_WINDOW:
        kw["creationflags"] = CREATE_NO_WINDOW
    return run(**kw)


def make_grok_sgh_critic(*, work_dir: Path, run=subprocess.run,
                         which=shutil.which):
    """Callable(packet_text) -> return_text. Spends SuperGrok Heavy, not Console."""

    def _fn(packet_text: str) -> str:
        if not which("grok"):
            raise CriticError("NO_RAIL", "grok not on PATH")
        ws = Path(work_dir) / f"grok-sgh-{uuid.uuid4().hex[:12]}"
        ws.mkdir(parents=True, exist_ok=True)
        body = packet_text if len(packet_text) <= MAX_PACKET_CHARS else (
            packet_text[:MAX_PACKET_CHARS] + "\n\n[PACKET TRUNCATED]\n")
        (ws / "PACKET.md").write_text(body, encoding="utf-8")
        # Packet lives in PACKET.md only. Putting it on argv hits Windows E2BIG.
        prompt = (
            CRITIC_PROMPT.replace("FAM", GROK_SGH)
            + "\nRead PACKET.md in this cwd. Write RETURN.md. Do not put the packet on the command line."
        )
        if len(prompt) > ARGV_PROMPT_MAX:
            prompt = prompt[:ARGV_PROMPT_MAX]
        r = _run_grok(grok_sgh_argv(prompt, str(ws)), cwd=str(ws),
                      env=grok_sgh_env(), run=run)
        ret = ws / "RETURN.md"
        chunks = []
        if ret.is_file() and ret.stat().st_size:
            chunks.append(ret.read_text(encoding="utf-8"))
        out = (r.stdout or "").strip()
        if out:
            chunks.append(out)
        text = "\n".join(chunks).strip()
        if "```json" not in text and '"topic"' not in text:
            err = (r.stderr or "")[:300]
            raise CriticError(
                "EMPTY_OUTPUT",
                f"grok critic produced no findings rc={r.returncode} {err}".strip())
        return text

    return _fn


JOANNA_ACCOUNT = "joanna.bbf@gmail.com"
JOANNA_PROJECT = "project-5a33f910-1251-4d6a-bf9"
CODING_ACCOUNT = "orders.ggn@gmail.com"
CODING_PROJECT = "project-10b3a132-ec5b-41e9-a2c"


def make_vertex_critic(paths=None, *, rail=None, spend=None):
    """COSMOS Vertex Express on the named $300 coding rail (orders.ggn).
    Joanna only if vertex_coding.json is absent. Not Activate.
    Spends on VERTEX_SPEND, never kernel gem-api / bts_gem (Studio mix)."""
    if rail is None:
        from cosmos_vertex_rail import (
            load_coding_spec, load_spec, rail_for, rail_for_coding,
        )
        coding = load_coding_spec(paths)
        if coding.get("role") == "coding":
            acct = str(coding.get("account") or coding.get("email") or "").strip().lower()
            proj = str(coding.get("project") or "").strip()
            if proj != CODING_PROJECT:
                raise CriticError(
                    "NO_RAIL",
                    f"vertex-coding project {proj!r} is not orders.ggn "
                    f"{CODING_PROJECT} — do not collapse Google wallets")
            if acct not in {CODING_ACCOUNT, "kelly gregory"}:
                raise CriticError(
                    "NO_RAIL",
                    f"vertex-coding account {acct!r} is not {CODING_ACCOUNT}")
            if coding.get("do_not_activate") is False:
                raise CriticError(
                    "NO_RAIL",
                    "orders.ggn do_not_activate is off — refusing rather than Upgrade")
            rail = rail_for_coding(paths)
        else:
            spec = load_spec(paths)
            acct = str(spec.get("account") or "").strip().lower()
            if acct != JOANNA_ACCOUNT:
                raise CriticError(
                    "NO_RAIL",
                    f"gem-api account {acct!r} is not Joanna Vertex — "
                    "do not collapse onto another Google billing account")
            if spec.get("do_not_activate") is False:
                raise CriticError(
                    "NO_RAIL",
                    "Joanna Vertex do_not_activate is off — refusing rather than Activate")
            rail = rail_for(paths)

    def _fn(packet_text: str) -> str:
        from cosmos_vertex_rail import price_usd
        body = packet_text if len(packet_text) <= MAX_PACKET_CHARS else (
            packet_text[:MAX_PACKET_CHARS] + "\n\n[PACKET TRUNCATED]\n")
        payload = {
            "prompt": CRITIC_PROMPT.replace("FAM", GEM) + "\n\nPACKET:\n" + body,
        }
        est = price_usd(None, len(payload["prompt"]))

        def _call():
            rec = rail.dispatch(payload)
            if isinstance(rec, dict) and rec.get("ok") and rec.get("usd") is None:
                raise CriticError(
                    "UNPRICED",
                    "gem-api returned no usd — the $300 cap cannot fire")
            return rec

        if spend is not None:
            r = spend.guarded_call(VERTEX_SPEND, est, _call)
        else:
            r = _call()
        if not isinstance(r, dict) or not r.get("ok"):
            detail = ""
            if isinstance(r, dict):
                detail = str(r.get("detail") or r.get("kind") or "")
            raise CriticError("NO_RAIL", f"gem-api {detail}".strip())
        text = str(r.get("text") or "").strip()
        if "```json" not in text and '"topic"' not in text:
            raise CriticError("EMPTY_OUTPUT", "gem-api produced no findings")
        return text

    return _fn


def make_oa_critic(paths=None, *, rail=None):
    """OpenAI Platform API (`bts_oa_api` / terra). Not Codex ChatGPT-plan."""
    if rail is None:
        from cosmos_node_rails import NodeRail
        rail = NodeRail("bts_oa_api", metered_usd=0.05, paths=paths)
        ok, detail = rail.probe()
        if not ok:
            raise CriticError("NO_RAIL", f"oa-api {detail}")

    def _fn(packet_text: str) -> str:
        body = packet_text if len(packet_text) <= MAX_PACKET_CHARS else (
            packet_text[:MAX_PACKET_CHARS] + "\n\n[PACKET TRUNCATED]\n")
        r = rail.dispatch({
            "prompt": CRITIC_PROMPT.replace("FAM", OA) + "\n\nPACKET:\n" + body,
            "kwargs": {
                "tier": "terra",
                "max_output_tokens": 4000,
                "store": False,
            },
        })
        if not isinstance(r, dict) or not r.get("ok"):
            detail = ""
            if isinstance(r, dict):
                detail = str(r.get("detail") or r.get("kind") or r.get("reason") or "")
            raise CriticError("NO_RAIL", f"oa-api {detail}".strip())
        model = str(r.get("model") or "").strip()
        if model != OA_TERRA_ID:
            raise CriticError(
                "NO_RAIL",
                f"oa-api provenance: wanted {OA_TERRA_ID}, rail reported {model or 'missing'!r} "
                "(do not stamp terra on a Codex/other answer)")
        text = str(r.get("text") or r.get("full_text") or "").strip()
        if "```json" not in text and '"topic"' not in text:
            raise CriticError("EMPTY_OUTPUT", "oa-api produced no findings")
        return text

    return _fn


def make_rail_critic(kernel, link_id: str):
    """Spend-gated adapter.dispatch. Specific link — not Dispatcher.route."""

    def _fn(packet_text: str) -> str:
        adapters = getattr(kernel, "adapters", None) or {}
        adapter = adapters.get(link_id)
        if adapter is None or not hasattr(adapter, "dispatch"):
            raise CriticError("NO_RAIL", f"{link_id} has no adapter")
        body = packet_text if len(packet_text) <= MAX_PACKET_CHARS else (
            packet_text[:MAX_PACKET_CHARS] + "\n\n[PACKET TRUNCATED]\n")
        payload = {"prompt": CRITIC_PROMPT.replace("FAM", link_id) + "\n\n" + body}
        spend = getattr(kernel, "spend", None)
        usd = float(getattr(adapter, "metered_usd", 0) or 0)
        if spend is not None and usd:
            result = spend.guarded_call(
                link_id, usd, lambda: adapter.dispatch(payload))
        else:
            result = adapter.dispatch(payload)
        if not isinstance(result, dict) or not result.get("ok"):
            detail = ""
            if isinstance(result, dict):
                detail = str(result.get("detail") or result.get("kind") or "")
            raise CriticError("NO_RAIL", f"{link_id} {detail}".strip())
        text = str(result.get("text") or "").strip()
        if not text:
            raise CriticError("EMPTY_OUTPUT", f"{link_id} empty text")
        return text

    return _fn


def _probe_ok(adapter) -> bool:
    probe = getattr(adapter, "probe", None)
    if not callable(probe):
        return True
    try:
        ok, _detail = probe()
        return bool(ok)
    except Exception:  # noqa: BLE001
        return False


def compose_crucible_critics(kernel, *, which=shutil.which, run=subprocess.run,
                             work_dir: Path | None = None, paths=None,
                             vertex_rail=None, oa_rail=None) -> dict:
    """Build name -> callable. Empty dict means 501 stays honest."""
    out: dict = {}
    adapters = getattr(kernel, "adapters", None) or {}
    if work_dir is None:
        try:
            work_dir = Path(kernel.paths.role("work", "crucible", "attempts"))
        except Exception:  # noqa: BLE001
            work_dir = Path(os.environ.get("TEMP") or "/tmp") / "cosmos-crucible"

    grok_cli = bool(which("grok"))
    if grok_cli:
        out[GROK_SGH] = make_grok_sgh_critic(
            work_dir=work_dir, run=run, which=which)
    elif GROK_CONSOLE in adapters and _probe_ok(adapters[GROK_CONSOLE]):
        out[GROK_CONSOLE] = make_rail_critic(kernel, GROK_CONSOLE)

    gem_paths = paths if paths is not None else getattr(kernel, "paths", None)
    spend = getattr(kernel, "spend", None)
    # Never kernel.adapters["gem-api"] / bts_gem — Studio mix. COSMOS spends vertex-coding.
    if vertex_rail is not None:
        out[GEM] = make_vertex_critic(rail=vertex_rail, spend=spend)
    elif gem_paths is not None:
        try:
            out[GEM] = make_vertex_critic(gem_paths, spend=spend)
        except Exception:  # noqa: BLE001
            pass

    oa_paths = paths if paths is not None else getattr(kernel, "paths", None)
    if oa_rail is not None:
        out[OA] = make_oa_critic(rail=oa_rail)
    elif oa_paths is not None:
        try:
            out[OA] = make_oa_critic(oa_paths)
        except Exception:  # noqa: BLE001
            if OA in adapters and _probe_ok(adapters[OA]):
                out[OA] = make_rail_critic(kernel, OA)
    elif OA in adapters and _probe_ok(adapters[OA]):
        out[OA] = make_rail_critic(kernel, OA)
    return out


def attach_crucible_critics(kernel, *, which=shutil.which, run=subprocess.run,
                            work_dir: Path | None = None, paths=None,
                            vertex_rail=None, oa_rail=None) -> dict:
    """Serve-time only. Does not change Kernel() so tests keep 501."""
    critics = compose_crucible_critics(
        kernel, which=which, run=run, work_dir=work_dir,
        paths=paths, vertex_rail=vertex_rail, oa_rail=oa_rail)
    if critics:
        kernel.crucible_critics = critics
    spend = getattr(kernel, "spend", None)
    if spend is not None and GEM in critics:
        try:
            spend.set_budget(VERTEX_SPEND, VERTEX_CAP_USD)
        except Exception:  # noqa: BLE001
            pass
    names = sorted(critics)
    wallets = []
    if GROK_SGH in critics:
        wallets.append("super_grok_heavy")
    if GROK_CONSOLE in critics:
        wallets.append("xai_console")
    if GEM in critics:
        wallets.append("vertex_coding")
    if OA in critics:
        wallets.append("openai_api")
    rec = {"critics": names, "wallets": wallets,
           "anthropic": "OFF", "attached_at": time.time()}
    ledger = getattr(kernel, "ledger", None)
    if ledger is not None and names:
        try:
            ledger.append("CRUCIBLE_CRITICS_ATTACHED", rec)
        except Exception:  # noqa: BLE001
            pass
    return rec


def spend_round(sources: list[Path], out_dir: Path, *,
                which=shutil.which, run=subprocess.run, root: str | None = None,
                vertex_rail=None, oa_rail=None) -> dict:
    """Run critics without booting a writing Kernel (no second ledger writer).
    Lands PACKET + RETURN_* under out_dir. Not a substitute for POST /crucible."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    parts = ["# CRUCIBLE SPEND ROUND\n",
             "wallets: SuperGrok Heavy (grok CLI, XAI_API_KEY unset); "
             "Joanna Vertex Express (do_not_activate). Not a fused GCloud pool.\n"]
    names = []
    for s in sources:
        p = Path(s)
        body = p.read_text(encoding="utf-8")
        names.append(p.name)
        parts.append(
            f"===== BEGIN {p.name} ({len(body)} chars) =====\n{body}\n"
            f"===== END {p.name} =====\n")
    packet = "\n".join(parts)
    (out_dir / "_PACKET.md").write_text(packet, encoding="utf-8")
    paths = None
    if root:
        from cosmos_paths import CosmosPaths
        paths = CosmosPaths(root)
    kernel = type("K", (), {"adapters": {}, "spend": None, "paths": paths,
                            "ledger": None})()
    critics = compose_crucible_critics(
        kernel, which=which, run=run, work_dir=out_dir, paths=paths,
        vertex_rail=vertex_rail, oa_rail=oa_rail)
    returned, failed = {}, {}
    for name, fn in critics.items():
        try:
            text = fn(packet)
            rp = out_dir / f"RETURN_{name}.md"
            rp.write_text(text, encoding="utf-8")
            returned[name] = str(rp)
        except Exception as e:  # noqa: BLE001
            fp = out_dir / f"RETURN_{name}.FAILED.txt"
            fp.write_text(f"CRITIC FAILED MID-RUN: {type(e).__name__}: {e}\n",
                          encoding="utf-8")
            failed[name] = str(fp)
    families = sorted(returned)
    warn = ("single-family — agreement proves nothing"
            if len(returned) < 2 else f"families={families}")
    note = (
        f"returned={families} failed={sorted(failed)} "
        f"sources={names}\n"
        f"{warn}\n"
        "Joanna Vertex only until a company $300 rail is named. "
        "do_not_activate.\n"
        "This round is not the authority ledger. POST /api/v1/crucible "
        "stays 501 until `cosmos.py serve` attaches critics.\n"
    )
    (out_dir / "_ROUND.txt").write_text(note, encoding="utf-8")
    rec = {"returned": returned, "failed": failed, "out_dir": str(out_dir),
           "sources": names, "families": families}
    if paths is not None and returned:
        try:
            from cosmos_porosity import hook_returns
            rec["porosity"] = hook_returns(
                paths, returned, profile="crucible", axis="law",
                authority="crew:crucible", action="round",
            )
        except Exception as e:  # noqa: BLE001
            rec["porosity"] = {
                "kind": "BROKE",
                "detail": f"{type(e).__name__}: {e}"[:200],
            }
    return rec


if __name__ == "__main__":
    import argparse
    from datetime import datetime

    ap = argparse.ArgumentParser()
    ap.add_argument("--round", action="store_true")
    ap.add_argument("--out", default="")
    ap.add_argument("--root", default="")
    ap.add_argument("sources", nargs="*")
    a = ap.parse_args()
    if not a.round:
        print("ok compose-only; pass --round --root <live> and source files",
              file=sys.stderr)
        sys.exit(0)
    if not a.sources:
        print("NO_SOURCE: name the files to judge", file=sys.stderr)
        sys.exit(2)
    stamp = datetime.now().strftime("%Y%m%dT%H%M%S")
    out = Path(a.out) if a.out else (
        Path(__file__).resolve().parent.parent / "live" / "work" / "crucible"
        / f"sgh-spend-{stamp}")
    rec = spend_round([Path(s) for s in a.sources], out,
                      root=(a.root or None))
    print(rec)

