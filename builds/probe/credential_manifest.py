#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""credential_manifest.py -- a missing credential becomes a CLEAR ASK, not a silent stall.

WISHLIST "CREDENTIALING = open-window handoff": Keith owns money and credentials;
COSMOS opens the door. Today a missing key surfaces as a typed refusal buried in one
rail's probe output (`NO_KEY: [NO_KEY] OpenAI key missing at ...`), scattered across
agent returns -- so the ask never reaches him and the build quietly stalls. This tool
collects every credential COSMOS is waiting on into ONE machine-readable manifest and
renders ONE human list from it.

Four facts per credential, and only these four:
  WHAT it unblocks   -- named capabilities, each bound to a consumer at file:line
  WHERE it goes      -- a runtime-root role path (config/), never a drive literal
  HOW to verify it   -- the exact argv that proves it landed, and what to look for
  WHETHER it is here -- existence and non-emptiness, measured

SECRET DISCIPLINE (the reason this tool can be trusted with the subject):
  * it NEVER opens a credential file. `presence()` calls `stat()` and `is_file()` and
    nothing else -- no read_text, no read_bytes, no last-4, no length in the output.
  * every recorded path must resolve UNDER the runtime root's `config` role. A path
    outside it -- notably `D:\\R2Cloner`, which holds keys in plaintext -- raises
    FORBIDDEN_PATH. The manifest records WHICH key is missing, never a value.
  * the manifest is safe to commit, mail, or paste into a chat window. That is the
    whole point: an ask you cannot pass along is not an ask.

State per credential:
  BLOCKED    required, absent (or empty) -- something cannot run at all
  DEGRADED   the keyed path refuses, but a fallback still answers (say so, exactly)
  OPTIONAL   absent is legal; the key raises a limit or unlocks a gated feature
  PLANNED    researched, no consumer wired yet -- do NOT ask Keith for it today
  SATISFIED  measured present and non-empty
  UNMEASURED never green by default -- an interactive session this tool cannot probe

    py -3.14 builds\\probe\\credential_manifest.py --root V:\\A\\Ai\\COSMOS\\live
    py -3.14 builds\\probe\\credential_manifest.py --root ... --write-md
    py -3.14 builds\\probe\\credential_manifest.py --root ... --write-state

`--write-state` writes the manifest to the runtime root's `state` role -- the
Orchestrator's call, not an agent's (AGENT_BOUNDARIES: live/state is COW-only). By
default this tool writes only beside itself.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "cosmos"))

from cosmos_paths import CosmosPaths, CosmosPathError               # noqa: E402

SCHEMA = "cosmos-credentials-needed/1"
MANIFEST_NAME = "CREDENTIALS_NEEDED.json"
DOC_NAME = "CREDENTIALS_NEEDED.md"

# Key stores this tool must never read, list, or resolve into. Keith's plaintext R2
# store is the named one; the general rule (every path under the config role) already
# excludes it, and this list makes the refusal explicit instead of incidental.
FORBIDDEN_PREFIXES = ("d:\\r2cloner", "d:/r2cloner")

STATES = ("BLOCKED", "DEGRADED", "OPTIONAL", "PLANNED", "SATISFIED", "UNMEASURED")
ASK_STATES = ("BLOCKED", "DEGRADED")            # what Keith is actually asked for


class CredentialManifestError(RuntimeError):
    """Typed refusal. `kind` in {BAD_ROOT, FORBIDDEN_PATH, BAD_SPEC, UNWRITABLE,
    UNKNOWN_NEED, NO_WINDOW}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def check_need(n: Need) -> Need:
    """A Need is a declaration. A path in config_name, or a severity
    outside STATES, is a spec error — not a measured credential state."""
    if not n.id or not n.credential:
        raise CredentialManifestError(
            "BAD_SPEC", f"need missing id or credential: {n!r}")
    if n.severity not in STATES:
        raise CredentialManifestError(
            "BAD_SPEC",
            f"need {n.id} severity {n.severity!r} is not one of {STATES}")
    if n.config_name and ("/" in n.config_name or "\\" in n.config_name):
        raise CredentialManifestError(
            "BAD_SPEC",
            f"need {n.id} config_name is a path, not a name: {n.config_name!r}")
    return n


# --------------------------------------------------------------------------- needs
@dataclass(frozen=True)
class Need:
    """One credential COSMOS is waiting on. `config_name` is a NAME, never a path --
    the resolver turns it into one under the runtime root (canon: no hard-coded paths).
    `severity` is what this credential is worth when absent; `state` is measured."""

    id: str
    credential: str
    config_name: str | None            # None => not a file (an interactive session)
    severity: str                      # BLOCKED | DEGRADED | OPTIONAL | PLANNED
    shape: str                         # a SHAPE hint, never a value
    where_to_get: str
    unblocks: tuple[str, ...]
    consumers: tuple[str, ...]         # "path:line -- what refuses without it"
    verify_argv: tuple[str, ...]
    verify_expect: str
    verify_expect_not: str = ""
    fallback: str = ""                 # what still answers while this is absent
    wired: bool = True                 # False => the place_at name is PROPOSED
    evidence: dict = field(default_factory=dict)   # {kind, key} into the probe files
    note: str = ""


NEEDS: tuple[Need, ...] = (
    Need(
        id="openai-api-key",
        credential="OpenAI API key (Codex CLI)",
        config_name="openai_api_key.txt",
        severity="BLOCKED",
        shape="sk-... (one line; never printed, never committed)",
        where_to_get="https://platform.openai.com/api-keys",
        unblocks=(
            "the `codex-cli` node rail: probe, dispatch, and any coder/vetter job on it",
            "`cosmos_dispatch --kind codex` -- the whole Codex agent lane refuses NO_KEY "
            "before it writes a job",
            "Codex work orders through `cosmos_work_order_run`",
            "a future `codex-cli` row in `cosmos_rails_prober.WIRED_NODES` (the key is "
            "necessary, not sufficient -- see note)",
        ),
        consumers=(
            "cosmos/cosmos_codex_rail.py:79 -- KEY_NAME; read_key() raises NO_KEY",
            "cosmos/cosmos_dispatch.py:2003 -- DispatchError NO_KEY before job creation",
            "cosmos/cosmos_work_order_run.py:159 -- key_path_for(paths) on the codex path",
        ),
        verify_argv=("py", "-3.14", "cosmos/cosmos_codex_rail.py",
                     "--root", "<root>", "--probe"),
        verify_expect='"ok": true',
        verify_expect_not="NO_KEY",
        evidence={"kind": "mesh", "key": "codex-cli"},
        note="Placing the key clears the refusal but does NOT put codex-cli in the "
             "registry: it is also absent from cosmos_rails_prober.WIRED_NODES, so "
             "nothing asks it for a proof. Two independent blockers, one link_id.",
    ),
    Need(
        id="anthropic-api-key",
        credential="Anthropic API key (Claude Code CLI)",
        config_name="anthropic_api_key.txt",
        severity="DEGRADED",
        shape="sk-ant-... (one line; never printed, never committed)",
        where_to_get="https://console.anthropic.com/settings/keys",
        unblocks=(
            "`ClaudeRail.dispatch` -- the keyed Claude rail, which refuses NO_KEY today",
            "keyed (non-seat) Claude jobs, so seat exhaustion stops being a single point "
            "of failure for the whole core->code route",
        ),
        consumers=(
            "cosmos/cosmos_claude_rail.py:81 -- KEY_NAME; read_key() raises NO_KEY",
            "cosmos/cosmos_claude_rail.py:391 -- the child env's ANTHROPIC_API_KEY",
            "cosmos/cosmos_rails_prober.py:239 -- presence check on the keyed path",
        ),
        verify_argv=("py", "-3.14", "cosmos/cosmos_claude_rail.py",
                     "--root", "<root>", "--probe"),
        verify_expect='"ok": true',
        verify_expect_not="NO_KEY",
        fallback="the prepaid SEAT answers now: cosmos_rails_prober._claude_live_call "
                 "runs `claude -p` with ANTHROPIC_API_KEY UNSET (cosmos_rails_prober.py"
                 ":158-190), which is why claude-cli carries a registry proof while "
                 "ClaudeRail.probe() refuses NO_KEY. Not blocking; single-pathed.",
        evidence={"kind": "mesh", "key": "claude-cli"},
    ),
    Need(
        id="tailscale-login",
        credential="Tailscale login (an interactive session, NOT a file)",
        config_name=None,
        severity="DEGRADED",
        shape="n/a -- device auth in the Tailscale app; no key lands in the tree",
        where_to_get="https://login.tailscale.com/ (or the Tailscale tray app)",
        unblocks=(
            "`cosmos up` -- phone/remote reach over the tailnet",
            "`tailscale cert <fqdn>` -- the browser-trusted cert `cosmos serve --cert` "
            "wants, instead of a self-signed one",
        ),
        consumers=(
            "cosmos/cosmos_up.py:49 -- UpError kinds NO_TAILSCALE / NOT_LOGGED_IN",
            "cosmos/cosmos_up.py:106 -- detect_tailscale() locates the binary",
        ),
        verify_argv=("tailscale", "status"),
        verify_expect="(a tailnet name and this machine listed)",
        verify_expect_not="Logged out",
        fallback="LAN / localhost reach is unaffected; only off-LAN and the trusted "
                 "cert depend on it.",
        evidence={"kind": "none", "key": ""},
        note="No credential file is created for this one -- do not invent a path.",
    ),
    Need(
        id="firecrawl-api-key",
        credential="Firecrawl API key",
        config_name="firecrawl_api_key.txt",
        severity="OPTIONAL",
        shape="fc-...",
        where_to_get="https://www.firecrawl.dev/app/api-keys",
        unblocks=(
            "higher Firecrawl rate limits and the authenticated endpoints",
        ),
        consumers=(
            "cosmos/cosmos_firecrawl_rail.py:48 -- KEY_NAME; read_key() returns None "
            "when absent (keyless is a supported mode, not a refusal)",
        ),
        verify_argv=("py", "-3.14", "cosmos/cosmos_firecrawl_rail.py",
                     "--root", "<root>", "--probe"),
        verify_expect='"ok": true',
        fallback="the rail runs KEYLESS and answered on the last measured run "
                 "(http=200) with key_present=false.",
        evidence={"kind": "mesh", "key": "firecrawl-web"},
    ),
    Need(
        id="kill-token",
        credential="COSMOS kill-channel token",
        config_name="kill_token.txt",
        severity="OPTIONAL",
        shape="a secret Keith chooses (one line)",
        where_to_get="Keith invents it -- no vendor, no account",
        unblocks=(
            "gating the service off-switch: while this file is absent the kill/control "
            "channel is ungated behind the bearer token alone",
        ),
        consumers=(
            "cosmos/cosmos_service.py:474 -- kill_token.txt, when present, gates /kill",
        ),
        verify_argv=("py", "-3.14", "cosmos/cosmos.py", "status", "--root", "<root>"),
        verify_expect="(service starts; the kill endpoint then demands the token)",
        evidence={"kind": "none", "key": ""},
    ),
    Need(
        id="cursor-api-key",
        credential="Cursor COSMOS API key",
        config_name="cursor_cosmos_key.txt",
        severity="BLOCKED",
        shape="crsr_...",
        where_to_get="https://cursor.com/dashboard (Integrations -> API keys)",
        unblocks=(
            "`cosmos_dispatch --kind cursor` -- the Cursor agent lane",
            "the watchdog's Cursor overflow route when the Grok lanes are loaded",
        ),
        consumers=(
            "cosmos/cosmos_cursor_rail.py:48 -- KEY_NAME; read_key() raises NO_KEY",
            "cosmos/cosmos_dispatch.py:1996 -- DispatchError NO_KEY before job creation",
            "cosmos/cosmos_watchdog2.py:649 -- cursor_key_exists() gates the overflow lane",
        ),
        verify_argv=("py", "-3.14", "cosmos/cosmos_cursor_rail.py",
                     "--root", "<root>", "--probe"),
        verify_expect='"ok": true',
        verify_expect_not="NO_KEY",
        evidence={"kind": "mesh", "key": "cursor-api"},
    ),
    Need(
        id="core-api-token",
        credential="COSMOS Core bearer token",
        config_name="api_token.txt",
        severity="BLOCKED",
        shape="a high-entropy secret minted by `cosmos install`",
        where_to_get="minted by COSMOS itself -- `py -3.14 cosmos/cosmos.py install`",
        unblocks=(
            "every authenticated call to COSMOS Core: KDash, the mobile client, voice",
        ),
        consumers=(
            "cosmos/cosmos_service.py:410 -- refuses to serve rather than invent auth",
            "cosmos/cosmos_service.py:419 -- an EMPTY token file is an open door, also "
            "refused (this is why the manifest measures non-emptiness, not existence)",
        ),
        verify_argv=("py", "-3.14", "cosmos/cosmos.py", "status", "--root", "<root>"),
        verify_expect='"ok": true',
        evidence={"kind": "none", "key": ""},
    ),
    Need(
        id="install-key",
        credential="ledger HMAC install key",
        config_name="install_key.bin",
        severity="BLOCKED",
        shape="binary, minted by `cosmos install` -- never typed by a human",
        where_to_get="minted by COSMOS itself -- `py -3.14 cosmos/cosmos.py install`",
        unblocks=(
            "every ledger write, and therefore every spend-gated worker dispatch",
        ),
        consumers=(
            "cosmos/cosmos_node_worker.py:401 -- WorkerError NO_KEY",
            "cosmos/cosmos_bucket_daemon.py:486 -- WorkerError NO_KEY",
            "cosmos/cosmos_node_bucket_worker.py:466 -- WorkerError NO_KEY",
        ),
        verify_argv=("py", "-3.14", "cosmos/cosmos.py", "audit", "--root", "<root>"),
        verify_expect='"ok": true',
        evidence={"kind": "none", "key": ""},
    ),
    Need(
        id="groq-api-key",
        credential="Groq (GroqCloud) API key -- NOT xAI Grok",
        config_name="groq_api_key.txt",
        severity="PLANNED",
        shape="gsk_...",
        where_to_get="https://console.groq.com/keys",
        unblocks=(
            "a `groq-api` rail that does not exist yet (research only)",
        ),
        consumers=(),
        wired=False,
        verify_argv=("py", "-3.14", "-c", "(no consumer wired yet)"),
        verify_expect="(nothing to verify until a rail reads it)",
        evidence={"kind": "hands", "key": "Groq API"},
        note="Researched in docs/research/GROQ_HANDS.md; the maker-hands sweep measured "
             "an UNAUTHENTICATED 401 from api.groq.com, which is a probe of the public "
             "endpoint, not of a COSMOS key. Do not ask Keith for this until a rail "
             "reads the path -- an ask with no consumer is a chore.",
    ),
    Need(
        id="r2-credentials",
        credential="Cloudflare R2 credentials (backup target)",
        config_name="r2_credentials.json",
        severity="BLOCKED",
        shape="account id + access key id + secret (S3-compatible)",
        where_to_get="Keith already holds these; COSMOS has no copy and reads none",
        unblocks=(
            "the R2 offsite push (`builds/backup/cosmos_backup_r2.py`) and its "
            "scheduled clock (`cosmos_offsite_clock.py`)",
            "a copy whose failure is uncorrelated with this machine "
            "(WISHLIST: survives total tree DELETION)",
        ),
        consumers=(
            "builds/backup/cosmos_backup_r2.py:137 -- load_credentials raises NO_CREDENTIALS",
            "builds/backup/cosmos_offsite_clock.py:256 -- tick() heartbeats the same refusal",
        ),
        wired=True,
        verify_argv=("py", "-3.14", "builds/backup/cosmos_offsite_clock.py",
                     "--root", "<root>", "--preflight"),
        verify_expect='"status": "READY"',
        verify_expect_not="NO_CREDENTIALS",
        evidence={"kind": "none", "key": ""},
        note="The adapter landed 2026-08-31 (F-45, 29 tests) and the clock (F-47, 35/35) "
             "registers nothing. Keith places a copy at the config path; nothing "
             "automated goes near D:\\R2Cloner. The credential is the only remaining "
             "blocker for a real push.",
    ),
)


# ------------------------------------------------------------------- measurement
def guard(paths: CosmosPaths, p: Path) -> Path:
    """Fail-closed fence. Every recorded credential path lives under the runtime
    root's config role; anything else -- above all a plaintext key store on another
    volume -- is a typed refusal, not a warning."""
    s = str(p).replace("/", "\\").lower()
    for bad in FORBIDDEN_PREFIXES:
        if s.startswith(bad.replace("/", "\\")):
            raise CredentialManifestError(
                "FORBIDDEN_PATH",
                f"{p} is inside a plaintext key store this tool must never touch")
    try:
        p.resolve().relative_to(paths.config().resolve())
    except ValueError:
        raise CredentialManifestError(
            "FORBIDDEN_PATH",
            f"{p} is not under the config role {paths.config()} - REFUSING to record "
            f"a credential location outside the runtime root") from None
    return p


def presence(p: Path) -> dict:
    """Existence and non-emptiness ONLY. This function never opens the file: no
    read_text, no read_bytes, no digest, no length in the result. An EMPTY file is
    not satisfied -- cosmos_service.py:419 already learned that a blank secret is an
    open door, so 'it is there' is the wrong question."""
    try:
        st = p.stat()
    except OSError:
        return {"present": False, "nonempty": False}
    return {"present": p.is_file(), "nonempty": st.st_size > 0}


def load_probe_evidence(probe_dir: Path) -> dict:
    """Index the measured probe artifacts already in the tree, so every claim here is
    bound to something a machine emitted. Missing artifact => UNMEASURED, never green."""
    out: dict = {"mesh": {}, "hands": {}, "sources": {}}
    mesh = probe_dir / "MESH_STATUS.json"
    if mesh.is_file():
        try:
            d = json.loads(mesh.read_text(encoding="utf-8"))
            out["sources"]["mesh"] = {"path": _rel(mesh),
                                      "measured_at": d.get("measured_at")}
            for n in d.get("nodes", []):
                out["mesh"][n.get("link_id")] = n
        except (OSError, ValueError):
            pass
    for name in ("maker_hands_evidence.json", "maker_hands_evidence_extra.json"):
        f = probe_dir / name
        if not f.is_file():
            continue
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
            out["sources"].setdefault("hands", {"path": _rel(f), "measured_at": d.get("ts")})
            for r in d.get("rows", []):
                out["hands"].setdefault(r.get("candidate"), r)
        except (OSError, ValueError):
            pass
    return out


def _rel(p: Path) -> str:
    try:
        return str(p.resolve().relative_to(REPO)).replace("\\", "/")
    except ValueError:
        return str(p)


def evidence_for(need: Need, ev: dict) -> dict:
    """The verbatim line a machine emitted about this credential, or UNMEASURED."""
    kind, key = need.evidence.get("kind", "none"), need.evidence.get("key", "")
    if kind == "mesh" and key in ev["mesh"]:
        n = ev["mesh"][key]
        src = ev["sources"].get("mesh", {})
        return {"state": "MEASURED", "source": src.get("path"),
                "measured_at": src.get("measured_at"), "link_id": key,
                "quote": n.get("probe_detail") or n.get("blocker"),
                "key_present_at_measure": (n.get("evidence") or {}).get("key_present")}
    if kind == "hands" and key in ev["hands"]:
        r = ev["hands"][key]
        src = ev["sources"].get("hands", {})
        return {"state": "MEASURED", "source": src.get("path"),
                "measured_at": src.get("measured_at"), "candidate": key,
                "verdict": r.get("verdict"), "quote": str(r.get("evidence"))[:300]}
    if kind == "none":
        return {"state": "STATIC",
                "quote": "no probe artifact for this one; the consumers listed are the "
                         "binding (each raises a typed refusal without it)"}
    return {"state": "UNMEASURED",
            "quote": f"no measured artifact for {key!r} in {_rel(REPO / 'builds/probe')}"}


def resolve_need(paths: CosmosPaths, need: Need, ev: dict) -> dict:
    """One manifest row: where it goes, whether it is there, what it unblocks, how to
    prove it landed. `state` is measured; `severity` is what absence costs."""
    row: dict = {
        "id": need.id,
        "credential": need.credential,
        "shape": need.shape,
        "severity": need.severity,
        "owner": "Keith (credentials and money are his domain -- COSMOS opens the door)",
        "where_to_get": need.where_to_get,
        "unblocks": list(need.unblocks),
        "consumers": list(need.consumers),
        "wired": need.wired,
        "fallback": need.fallback or None,
        "note": need.note or None,
        "evidence": evidence_for(need, ev),
    }
    if need.config_name is None:
        row.update({"place_at_role": None, "place_at_name": None, "place_at": None,
                    "present": None, "nonempty": None, "state": "UNMEASURED"})
    else:
        p = guard(paths, paths.config(need.config_name))
        pres = presence(p)
        row.update({"place_at_role": "config", "place_at_name": need.config_name,
                    "place_at": str(p), **pres})
        if pres["present"] and pres["nonempty"]:
            row["state"] = "SATISFIED"
        elif pres["present"]:
            row["state"] = "BLOCKED"
            row["note"] = ((row["note"] + " ") if row["note"] else "") + \
                "The file EXISTS but is EMPTY -- treated as missing (a blank secret " \
                "is an open door, not a credential)."
        else:
            row["state"] = need.severity
    row["verify"] = {
        "argv": [str(paths.root) if a == "<root>" else a for a in need.verify_argv],
        "cwd": str(REPO),
        "expect": need.verify_expect,
        "expect_not": need.verify_expect_not or None,
    }
    return row


def build(root: str | Path, *, probe_dir: Path | None = None) -> dict:
    """The manifest. Deterministic apart from timestamps and measured presence."""
    try:
        paths = CosmosPaths(root)
    except CosmosPathError as e:
        raise CredentialManifestError("BAD_ROOT", str(e)) from e
    ev = load_probe_evidence(probe_dir or HERE)
    rows = [resolve_need(paths, check_need(n), ev) for n in NEEDS]
    tally: dict = {s: 0 for s in STATES}
    for r in rows:
        tally[r["state"]] = tally.get(r["state"], 0) + 1
    return {
        "ok": True,
        "schema": SCHEMA,
        "ts": _now(),
        "root": str(paths.root),
        "tree_id": paths.sentinel.tree_id,
        "generator": "builds/probe/credential_manifest.py",
        "policy": "Records WHICH credential is missing and what it unblocks. NEVER "
                  "reads, echoes, copies or digests key material; presence is stat() "
                  "only. Paths outside the runtime root's config role are refused "
                  "FORBIDDEN_PATH, including the plaintext store at D:\\R2Cloner.",
        "evidence_sources": ev["sources"],
        "ask_now": [r["id"] for r in rows if r["state"] in ASK_STATES],
        "tally": tally,
        "needs": rows,
    }


# ---------------------------------------------------------------------- rendering
_ORDER = {"BLOCKED": 0, "DEGRADED": 1, "OPTIONAL": 2, "UNMEASURED": 3,
          "PLANNED": 4, "SATISFIED": 5}


def _cmd(v: dict) -> str:
    return " ".join(f'"{a}"' if " " in a else a for a in v["argv"])


def render_md(m: dict) -> str:
    """The human list -- generated FROM the manifest, so the doc cannot drift from the
    machine. One list for Keith, in the order he would act on it."""
    rows = sorted(m["needs"], key=lambda r: (_ORDER.get(r["state"], 9), r["id"]))
    t = m["tally"]
    L: list[str] = []
    L.append("# CREDENTIALS NEEDED -- the open-window handoff, one list")
    L.append("")
    L.append(f"**Generated** by `{m['generator']}` (do not hand-edit; re-run it).")
    L.append(f"**Measured** {m['ts']}  ·  root `{m['root']}`  ·  tree `{m['tree_id']}`")
    L.append("")
    L.append("Keith owns money and credentials; COSMOS opens the door and never a bat. "
             "This file exists because a missing key used to surface as one rail's typed "
             "refusal buried in one agent's return -- an ask that never arrived, and a "
             "build that stalled silently. Every row below names WHAT it unblocks, WHERE "
             "the file goes, and HOW to prove it landed.")
    L.append("")
    L.append("**This file contains no key material and never will.** The generator "
             "measures presence with `stat()` and never opens a credential file; it "
             "refuses any path outside the runtime root's `config/` role, including the "
             "plaintext store at `D:\\R2Cloner`, which it does not read, list or touch.")
    L.append("")
    L.append(f"**Ask now: {t['BLOCKED'] + t['DEGRADED']}**  ·  "
             f"blocked {t['BLOCKED']} · degraded {t['DEGRADED']} · optional "
             f"{t['OPTIONAL']} · planned (do not ask yet) {t['PLANNED']} · satisfied "
             f"{t['SATISFIED']} · unmeasured {t['UNMEASURED']}")
    L.append("")
    L.append("| state | credential | put it here | it unblocks |")
    L.append("|---|---|---|---|")
    for r in rows:
        where = f"`{r['place_at_name']}`" if r["place_at_name"] else "*(no file -- login)*"
        if r["place_at_name"] and not r["wired"]:
            where += " *(proposed name; nothing reads it yet)*"
        first = r["unblocks"][0] if r["unblocks"] else "--"
        L.append(f"| **{r['state']}** | {r['credential']} | {where} | {first} |")
    L.append("")
    L.append(f"Every path below is `{m['root']}\\config\\<name>` -- resolved through the "
             "role, never typed by hand.")
    L.append("")

    for r in rows:
        L.append(f"## {r['credential']} -- {r['state']}")
        L.append("")
        if r["place_at"]:
            L.append(f"**Put it here:** `{r['place_at']}`"
                     + ("" if r["wired"] else "  *(PROPOSED name -- no code reads this "
                                              "path yet; see the note)*"))
        else:
            L.append("**No file.** This is an interactive login; nothing lands in the tree.")
        L.append("")
        L.append(f"**Shape:** {r['shape']}  ·  **Get it:** {r['where_to_get']}")
        L.append("")
        L.append("**Unblocks:**")
        L.append("")
        for u in r["unblocks"] or ["--"]:
            L.append(f"* {u}")
        L.append("")
        L.append("**Verify it landed:**")
        L.append("")
        L.append("```")
        L.append(_cmd(r["verify"]))
        L.append(f"expect:     {r['verify']['expect']}")
        if r["verify"]["expect_not"]:
            L.append(f"expect NOT: {r['verify']['expect_not']}")
        L.append("```")
        L.append("")
        if r["fallback"]:
            L.append(f"**What answers meanwhile:** {r['fallback']}")
            L.append("")
        if r["consumers"]:
            L.append("**What refuses without it** (each is a typed refusal in the tree):")
            L.append("")
            for c in r["consumers"]:
                L.append(f"* `{c}`")
            L.append("")
        e = r["evidence"]
        if e.get("quote"):
            L.append(f"**Evidence** ({e['state']}"
                     + (f", {e['source']}" if e.get("source") else "")
                     + (f", measured {e['measured_at']}" if e.get("measured_at") else "")
                     + "):")
            L.append("")
            L.append("```")
            L.append(str(e["quote"]).strip())
            L.append("```")
            L.append("")
        if r["note"]:
            L.append(f"> {r['note']}")
            L.append("")

    L.append("---")
    L.append("")
    L.append("Regenerate: `py -3.14 builds\\probe\\credential_manifest.py --root "
             "<runtime-root> --write-md`")
    L.append("")
    return "\n".join(L)


# ---------------------------------------------------------------- open-window (F-50)
def door_url(need: Need) -> str | None:
    """The signup/login URL, or None if this need is not a window (minted locally,
    or Keith already holds the value). Never a key."""
    w = (need.where_to_get or "").strip()
    if not w:
        return None
    token = w.split()[0].rstrip(").,;")
    if token.startswith("https://") or token.startswith("http://"):
        return token
    return None


def open_doors(ids: list[str], *, opener) -> dict:
    """Launch the Get-it URL for each id. Injected `opener` so a test cannot
    open a real browser. Unknown ids refuse; a need with no URL is skipped
    (NO_WINDOW), never invented. The returned payload names the public URL
    only — no credential value exists in this module to leak."""
    by_id = {n.id: n for n in NEEDS}
    opened, skipped = [], []
    unknown = [i for i in ids if i not in by_id]
    if unknown:
        raise CredentialManifestError("UNKNOWN_NEED", f"not a need id: {unknown}")
    for i in ids:
        n = by_id[i]
        url = door_url(n)
        if url is None:
            skipped.append({"id": i, "reason": "NO_WINDOW"})
            continue
        opener(url)
        opened.append({"id": i, "url": url})
    return {"ok": True, "opened": opened, "skipped": skipped}


def _default_opener(url: str) -> bool:
    import webbrowser
    return webbrowser.open(url, new=1, autoraise=True)


# ---------------------------------------------------------------------------- cli
def _write(p: Path, text: str) -> Path:
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    except OSError as e:
        raise CredentialManifestError("UNWRITABLE", f"{p}: {e}") from e
    return p


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", required=True, help="COSMOS runtime root")
    ap.add_argument("--json-out", default=None,
                    help=f"manifest path (default: beside this tool, {MANIFEST_NAME})")
    ap.add_argument("--write-md", action="store_true",
                    help=f"also render docs/{DOC_NAME} from the manifest")
    ap.add_argument("--write-state", action="store_true",
                    help="also write the manifest to the runtime root's state role "
                         "(Orchestrator-only: live/state is COW's, not an agent's)")
    ap.add_argument("--strict", action="store_true",
                    help="exit 3 when any credential is BLOCKED or DEGRADED")
    ap.add_argument("--open", action="append", metavar="NEED_ID", default=[],
                    help="open the Get-it URL for this need (repeatable); never a key")
    ap.add_argument("--open-asks", action="store_true",
                    help="open the Get-it URL for every BLOCKED/DEGRADED need that has one")
    a = ap.parse_args(argv)

    try:
        m = build(a.root)
        out = Path(a.json_out) if a.json_out else (HERE / MANIFEST_NAME)
        written = [_write(out, json.dumps(m, indent=1) + "\n")]
        if a.write_md:
            written.append(_write(REPO / "docs" / DOC_NAME, render_md(m)))
        if a.write_state:
            paths = CosmosPaths(a.root)
            written.append(_write(paths.state(MANIFEST_NAME),
                                  json.dumps(m, indent=1) + "\n"))
        opened = None
        ids = list(a.open)
        if a.open_asks:
            ids.extend(m["ask_now"])
        if ids:
            # Dedup preserving order. A flag is not an opener: tests inject
            # via open_doors(); production uses the stdlib browser.
            seen, uniq = set(), []
            for i in ids:
                if i not in seen:
                    seen.add(i)
                    uniq.append(i)
            opened = open_doors(uniq, opener=_default_opener)
    except CredentialManifestError as e:
        print(json.dumps({"ok": False, "kind": e.kind, "detail": str(e)}, indent=1))
        return 2

    report = {"ok": True, "schema": SCHEMA, "root": m["root"],
              "tally": m["tally"], "ask_now": m["ask_now"],
              "written": [_rel(p) for p in written]}
    if opened is not None:
        report["opened"] = opened
    print(json.dumps(report, indent=1))
    return 3 if (a.strict and m["ask_now"]) else 0


if __name__ == "__main__":
    raise SystemExit(main())
