#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_service - THE API SURFACE, first cut (F5 builder). One versioned HTTP API that
KDash, the alternate frontend, voice, and mobile all consume - stdlib only, no deps.

ENDPOINTS (v1) - COMPLETE when read with the CVM, CONTROL and STATIC blocks below;
nothing reaches a handler that is not named across those four lists (a route table
that omits what it serves is an undocumented surface, not a short one):
    GET /api/v1/status   - kernel READY + root identity + ledger head
    GET /api/v1/audit    - the audit projection (every number carries measured_at)
    GET /api/v1/health   - HealthBoard run, 10s cache. GET never mkdir and
                           never appends HEALTH_BOARD. Command `health` ledgers.
    GET /api/v1/spend    - the spend gate's audit
    GET /api/v1/tools    - the tool-contract report
    GET /api/v1/tools_kit - COSMOS components + local callables + other tools.
                           GET never mutates. UPS-JUDGE is NAMED.
    GET /api/v1/voice_loop - SGH → GitHub → daemon → GDX → SGH status.
                           GET never mutates. Does not POST /voice.
    GET /api/v1/events   - ?since_seq= oldest <=100 records past the cursor
                           (a non-integer or out-of-range seq is 400 BAD_SINCE_SEQ);
                           optional ?tail=N (1..100) returns the NEWEST N past
                           the cursor instead - the dashboard primitive. One
                           verify() walk; head_seq is taken from that walk.
    GET /api/v1/jobs     - job states from the scheduler projection
    GET /api/v1/rails    - the rails matrix with verification AGE per link
                           (/api/v1/nodes is the SAME route under its older name)
    GET /api/v1/makers   - the maker map (where agents/tools/connectors/skills are made)
    GET /api/v1/surfaces - storage surfaces (measured reachability + free_gb + age)
    GET /api/v1/surfaces_kit - storage + addable types + channels + tools.
                           GET never mutates, never mkdir, never disk_usage.
                           UPS-JUDGE is NAMED, not invented.
    GET /api/v1/fleet    - cDeck FLEET + host-volume projection (disk binders)
    GET /api/v1/nodemap  - cDeck NODE MAP projection (registry + heartbeats)
    GET /api/v1/jukebox  - rich job/queue fold (command, priority, stale flag)
    GET /api/v1/model_rater - OpenRouter catalog + seat assignments (local cache)
                           ?type=docs = text out, text/file/image in (cards cut).
    GET /api/v1/model_rater/roles - named COSMOS roles (ORC, CCr, MOTIF, Crucible)
    GET /api/v1/porosity - pairwise orthogonal porosity tensor T plus complement
                           tensor C (rescue / co-failure / XOR-error). Directed
                           grid tensors[agent][vs][axis] (agent_tensor). GET never
                           mkdir. UNMEASURED until a pair is observed. Does not invent.
    GET /api/v1/usage    - OpenRouter usage accounting fold (tokens/cost/cache).
                           GET never mkdir. UNMEASURED until a dispatch is recorded.
    GET /api/v1/gitur      - GitHub + GitLab + Cursor projection (rails + probe, no vendor poll)
    GET /api/v1/cred       - API/CLI/ADC key LEDs. Never echoes the secret. GET never mkdir.
    GET /api/v1/agents     - SDK / CLI / localhost agent presence (PATH/import).
    GET /api/v1/mcp        - named MCP servers + OpenAI tool conversion.
                           GET never mkdir, never spawns. Filesystem MCP REFUSED.
    GET /api/v1/work_orders - timestamped work-order list (agents, product, checks).
                           Folders are the live list; ?id= returns output_head.
                           GET never mutates and never mkdir.
    GET /api/v1/studio     - MOTIF DEFINE text + RESEARCH models/targets (pack).
                           GET never mutates. Does not start MOTIF.
    GET /api/v1/profiles   - occupancy skins + per-profile MOTIF engine.
                           ?profile=website. GET never mutates. Does not start MOTIF.
    GET /api/v1/backup     - backup clock fold (heartbeat + verified names).
                           GET never runs a backup and never mkdir.
    POST /api/v1/backup    - suite verbs: surface_test (measure_all), search
                           (dest candidates), restore/generate refuse without
                           bak/dest. Never a silent full-tree backup.
    GET /api/v1/session_kit - COS panes + autosave + auto-resession config.
                           GET never mutates. Does not fire a resession.
    GET /api/v1/session_tools - Open Sessions + suite verbs (scan/load/convert/
                           diff/check/anonymize/crash-recover). GET never mutates.
    GET /api/v1/research_call - MOTIF RESEARCH envelope for a chat research
                           function (Perplexity search_web/fetch_url). GET never
                           fetches. Core does not call Perplexity API.
    GET /api/v1/orc        - ORC BootUP inspect (SEED vs running pointer).
                           GET never mkdir. Does not spawn OpenWork.
    GET /api/v1/runs_ops   - Runs ops fold: watchdog, clocks, work orders,
                           streams, gitur, spend. GET never mutates.
    GET /api/v1/review     - HITL: spend approvals, blockers, required logins,
                           work-product catalog (day/week/month/90). GET never mutates.
    POST /api/v1/model_rater/refresh - pull models/rates from OpenRouter (TTL 24h)
    POST /api/v1/model_rater/seat    - assign DEFAULT + fallbacks, via, effort, budget to a role
    POST /api/v1/model_rater/policy  - favored / banned models and families
                                       action=add|remove for N parallel adversarial coders
    POST /api/v1/model_rater/cap     - per-model spend limit on the rater (0 = off).
                                       Not the Core spend gate.
    POST /api/v1/model_rater/porosity - record errors/100LOC × severity 1-10.
                                       Forwards Irbe stamps (agent_id, action,
                                       authority source:class). Federation
                                       aggregates; does not invent.
    POST /api/v1/porosity - pair observation, action=trial hook, or
                           action=recommend. Vector, not scalar. Mag =
                           disagreement_freq × error_magnitude. C from who_erred.
                           Forwards Irbe stamps (authority, audit_action).
    POST /api/v1/usage   - action=generation {id} fetches GET /generation audit.
                           Not a billing page. Does not send usage.include.
    POST /api/v1/model_rater/estimate - token * rate-card USD for a prestaged job
    POST /api/v1/model_rater/job_estimate - CCr token estimate + override; costs follow seats
    POST /api/v1/cred      - set/grab/delete/custom a named key. Never echoes.
                           Keith pastes. Does not open vendor billing.
    POST /api/v1/spend   - SET/ADJUST a rail cap or the breaker thresholds
                           (F-03). Bearer-gated, every field validated, and
                           NEVER a silent widen: any change giving more room
                           to spend is 409 WIDEN_REQUIRES_CONFIRM without a
                           literal "allow_widen": true. The change and its
                           provenance (actor / prev / direction / reason) land
                           in ONE signed BUDGET_SET; refusals leave a
                           SPEND_CAP_REFUSED trace. See cosmos_spend_admin.
    POST /api/v1/jobs    - submit {command, priority} -> job_id
    POST /api/v1/work_orders/picked - runner notify after pickup_order;
                           Core ledgers WORK_ORDER_PICKED (idempotent on
                           order_id). Daemon never opens live/ledger/.
    POST /api/v1/studio    - save DEFINE and/or RESEARCH config. Does not
                           start MOTIF. Keys stay on the named via.
    POST /api/v1/profiles  - save a profile MOTIF skin (problem + dest + stage notes).
    POST /api/v1/profiles/bg - Forge RESEARCH→CONSENSUS background free CLI. Not IMPLEMENT.
                           Does not start MOTIF. Does not publish.
    POST /api/v1/session_kit - save COS/autosave/resession config. Does not
                           fire TidyUP or a resession.
    POST /api/v1/session_tools - Sessions verbs (scan/load/convert/diff/check/
                           anonymize/crash-recover/strip/doi). Legal OMITTED.
                           GET never mutates. Original stays.
    POST /api/v1/voice_loop - action=new_sop. Files a Voice DROP SOP name.
                           GET never mutates.
    POST /api/v1/research_call - action=call files the envelope; action=ingest
                           accepts the research-function JSON. Does not fetch.
    POST /api/v1/surfaces  - add/remove operator catalog rows (R2, Drive,
                           local, NAS, GitHub). Keith pastes paths. GET
                           never mkdir. Does not invent reachability.
    POST /api/v1/backup    - surface_test / search / restore / generate.
                           restore and generate refuse without bak/dest.
                           GET never runs a backup.
    POST /api/v1/orc       - {stream} TidyUP/TU2 recovery if partial, then
                           session start. Temp/Recovery closes. Does not spawn OpenWork.exe.
    POST /api/v1/makers  - add a maker entry (unknown kind REFUSES)
    POST /api/v1/command - the voice/frontend seam: text in, kernel action out
    POST /api/v1/voice   - the spoken turn (hardened + spend-gated; see below)
    POST /api/v1/crucible - a critic round run as a job; 501 CRUCIBLE_NOT_RUNNABLE
                           when no critic dispatchers are composed
CVM (P3 additive, projection only - never the ledger):
    GET  /api/v1/cvm/pull?client_id=  - publish state/cvm/pull.json + status prewarm
    POST /api/v1/cvm/snapshot         - land the Android mule as state/cvm/phone.json
    POST /api/v1/cvm/push             - phone turn; same §8.3 envelope as snapshot;
                                        stamps pull.json audio_owner=desktop (never
                                        a phone claim). Composes snapshot+pull.
CONTROL CHANNEL + SPEND BREAKER (2026-08-25, cosmos_control/cosmos_spendguard):
    GET  /api/v1/control?client_id=X  - the pause/mic_off/clear_queue state the
                                        app polls (bearer-authed; NEVER gated
                                        by the spend breaker)
    POST /api/v1/kill , GET /kill     - the HUMAN OFF-SWITCH: mic_off +
                                        clear_queue, global or ?client_id=.
                                        Served WITHOUT the bearer (it can only
                                        reduce capability); an optional
                                        config/kill_token.txt gates it when
                                        present (?token= / {"token"}).
    POST /api/v1/control/resume       - clears the flags AND resets the local
                                        spend counters (bearer-authed: OFF is
                                        cheap by design, ON is deliberate)
    /api/v1/voice is HARDENED: control flags refuse fast (zero spend); an
    identical (client_id, utterance) inside ~15s is dropped as a duplicate
    (zero spend); the SpendGuard breaker (session/day USD caps + rate limit)
    refuses with a canned local reply BEFORE any model call; {stream, build,
    client_id, idempotency_key} are accepted and ledgered as telemetry; the
    minted session carries stream:<name> scope and the orchestrator's file
    roots are scoped to the stream; {"action": "bootup", "stream": s} answers
    a READ-ONLY spoken summary of the stream's handoff (V:\\Ai\\BU.MD).
    THE BRAIN IS HYBRID (2026-08-25, cosmos_brain): command/lookup shapes stay
    on the fast local path; free-form turns go to OPUS via the local claude
    CLI (claude -p, session mapped 1:1 from the COSMOS sid so it is resumable
    on the desktop via /resume), bounded by control state + rate limit + a
    per-session TURN CAP (opus_turns_per_session in spendguard_config.json),
    with fallback to the spend-gated Grok ask on any timeout/failure/over-cap.
    Every reply carries "brain": opus|grok|local (or the ask verb's model
    name) and chat/ask turns ledger a VOICE_BRAIN event.
STATIC APP SHELL (PWA, no bearer - see _STATIC_ROUTES):
    GET / , /m , /mobile - the phone-first page (mobile is the road default)
    GET /dash            - the desktop KDash page
    GET /kdash_manifest.webmanifest , /kdash_sw.js - installability shell
CDECK SHELL (F-11, no bearer - see _CDECK_ROUTES):
    GET /cdeck           - 302 to /cdeck/ (so relative app.css/app.js resolve)
    GET /cdeck/          - builds/cdeck/ui/index.html
    GET /cdeck/index.html, /cdeck/app.js, /cdeck/app.css,
        /cdeck/cdeck.webmanifest, /cdeck/sw.js, plus exact pane/shell
        names in _CDECK_UI_NAMES (header.js, deck_more.html, planets/*.mp3, …)
    Exact-match allowlist of fixed files, same rule as KDash: NO data, NO
    token. Same-origin with /api/v1/* is the browser path; a header that
    would let any other origin read Core is not added (PARITY_AUDIT K-2).
The shell is an exact-match allowlist of fixed files carrying NO data and NO
token (the bearer is pasted into the page at runtime, memory only); every
/api/v1/* route keeps requiring the bearer exactly as before.
Every response carries served_at + measured_at - a panel that cannot show its age is
the frozen-dashboard scar. Auth is a bearer token from the install config - remote
access control exists from day one, invisible in use (zero-friction canon). A blank
or whitespace token is REFUSED (an open door). A missing token file is minted only
on a loopback bind; a remote bind REFUSES rather than inventing silently.
"""
from __future__ import annotations

import hmac
import json
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from cosmos_kernel import Kernel

# Loopback binds may mint a token (zero-friction local use). A remote bind must
# never invent one - a silently minted secret on 0.0.0.0 is an open door.
_LOOPBACK_HOSTS = frozenset({"127.0.0.1", "localhost", "::1"})

# Per-request body cap for every POST endpoint. All v1 POST bodies are small
# JSON control messages; 1 MiB is generous. An uncapped Content-Length is an
# invitation to allocate arbitrary memory on an authenticated-or-not socket.
_MAX_BODY_BYTES = 1 << 20

# POST /api/v1/spend carries a handful of numbers and a short reason. It gets a
# far tighter cap than the general one: the money route has no reason to accept
# a megabyte, and the smallest cap that fits the contract is the right one.
_MAX_SPEND_BODY_BYTES = 16 << 10

# GET /api/v1/events page cap. The deck's TAIL_WINDOW follows this number.
EVENTS_PAGE = 100


WORK_ORDER_PICKED = "WORK_ORDER_PICKED"


def record_work_order_picked(kernel, body) -> tuple[int, dict]:
    """Idempotent WORK_ORDER_PICKED. Core is the ledger writer.

    First POST for an order_id appends and returns 201. A second POST with
    the same order_id returns 200 already=true and the original seq/hmac.
    Missing order_id is 400. decide() runs inside append_guarded.
    """
    if not isinstance(body, dict):
        return 400, {"error": "BAD_REQUEST", "detail": "body must be an object"}
    oid = str(body.get("order_id") or "").strip()
    if not oid:
        return 400, {"error": "BAD_REQUEST", "detail": "order_id is required"}
    payload = {
        "order_id": oid,
        "agent": body.get("agent") or body.get("Agent"),
        "output_path": body.get("output_path") or body.get("_output_path"),
        "picked_at": body.get("picked_at"),
        "tree_id": kernel.paths.sentinel.tree_id,
    }
    found: dict = {}

    def decide(recs):
        for r in recs:
            if r.get("event") != WORK_ORDER_PICKED:
                continue
            p = r.get("payload") if isinstance(r.get("payload"), dict) else {}
            if str(p.get("order_id") or "") == oid:
                found["rec"] = r
                return None
        return (WORK_ORDER_PICKED, payload)

    rec = kernel.ledger.append_guarded(decide)
    if rec is None:
        prev = found.get("rec") or {}
        return 200, {
            "ok": True, "already": True, "order_id": oid,
            "seq": prev.get("seq"), "hmac": prev.get("hmac"),
            "prev_sha": prev.get("prev_sha"), "event": WORK_ORDER_PICKED,
        }
    return 201, {
        "ok": True, "already": False, "order_id": oid,
        "seq": rec.get("seq"), "hmac": rec.get("hmac"),
        "prev_sha": rec.get("prev_sha"), "event": WORK_ORDER_PICKED,
    }


def page_events(ledger, since: int, tail=None, page: int = EVENTS_PAGE):
    """One verify() walk. Default: the OLDEST `page` records with seq > since
    (the existing cursor contract). `tail=N`: the NEWEST N with seq > since —
    the dashboard primitive the deck otherwise fakes with a second request.

    head_seq is the last seq observed on THIS walk, so the caller never calls
    ledger.head_seq() (a second full verify of the same chain). Empty ledger
    returns head_seq 0. The chain is still hash-verified end-to-end: a
    hash-chained ledger cannot skip earlier records.
    """
    from collections import deque
    if tail is not None:
        buf = deque(maxlen=int(tail))
    else:
        buf = []
        cap = int(page)
    head = 0
    for r in ledger.verify():
        head = r["seq"]
        if r["seq"] <= since:
            continue
        row = {"seq": r["seq"], "event": r["event"], "t": r["t"],
               "writer": r["writer"], "payload": r["payload"]}
        if tail is not None:
            buf.append(row)
        elif len(buf) < cap:
            buf.append(row)
    return head, list(buf)

# ---------------- CVM projection (P3 additive; not the ledger) ----------------
# PHASE 4 seam: helpers live in cosmos_cvm_projection and are re-exported
# here -- same objects, not copies -- so cosmos_cvm_push.py and
# tests/test_cvm_push.py (`CvmError`, `_cvm_pull_response`,
# `_cvm_store_snapshot`) keep working unchanged. Handlers below only call
# these helpers. Additive.
from cosmos_cvm_projection import (  # noqa: E402
    CvmError, _CVM_KNOWN_KINDS, _CVM_PCM_INLINE,
    _cvm_blob_ptrs, _cvm_filter_kinds, _cvm_pull_response,
    _cvm_read_json, _cvm_stat, _cvm_status_prewarm, _cvm_store_snapshot,
)


def _frontend_file(name: str):
    """Resolve one shell file: kdash/<name> beside (or above) this module in the
    repo layout, or flat kdash_<name> in a spike checkout - the same resolution
    order as cosmos_kdash._find_kdash_index. None if absent (an honest 404)."""
    from pathlib import Path as _P
    here = _P(__file__).resolve().parent
    for cand in (here / "kdash" / name,
                 here.parent / "kdash" / name,
                 here / ("kdash_" + name)):
        if cand.is_file():
            return cand
    return None


# THE STATIC APP SHELL (PWA). Served WITHOUT the bearer, deliberately: these are
# fixed, allowlisted files containing no data and no secret - the token is pasted
# by the user into the page at runtime and lives in page memory only. Serving the
# shell openly is what makes the client installable/reachable from a phone; the
# data behind it still requires the bearer on every /api/v1/* request. The dict
# is an EXACT-MATCH allowlist: no request text ever becomes a filesystem path,
# so there is no traversal surface. Mobile is the default at / (the road case).
_CT_HTML = "text/html; charset=utf-8"
_STATIC_ROUTES = {
    "/": ("mobile.html", _CT_HTML),
    "/m": ("mobile.html", _CT_HTML),
    "/mobile": ("mobile.html", _CT_HTML),
    "/dash": ("index.html", _CT_HTML),
    "/kdash_manifest.webmanifest": ("manifest.webmanifest",
                                    "application/manifest+json"),
    # served at the ROOT path so its default scope ("/") can control /m
    "/kdash_sw.js": ("sw.js", "text/javascript; charset=utf-8"),
    # the native Android app installer (download-and-sideload), served on the
    # known-good port so no new firewall rule is needed. No data, no token.
    "/cosmos-voice.apk": ("cosmos-voice.apk",
                          "application/vnd.android.package-archive"),
}

# F-11: cDeck's ui/ on Core's own origin. Exact-match allowlist — the request
# path is a dict key, never concatenated onto a filesystem path, so there is
# no traversal surface. Relative hrefs in index.html (app.css, app.js, the
# manifest) only resolve when the document URL is under /cdeck/, so /cdeck
# (no slash) 302s there. Finder is _cdeck_file, not _frontend_file.
_CT_JS = "text/javascript; charset=utf-8"
_CT_CSS = "text/css; charset=utf-8"
_CT_SVG = "image/svg+xml"
_CT_MP3 = "audio/mpeg"
_CT_JPEG = "image/jpeg"
# Exact names on disk under builds/cdeck/ui/. No wildcard. Nested planets/
# only because those files exist (Holst). Do not invent icons/favicon.
_CDECK_UI_FILES = (
    ("index.html", _CT_HTML),
    ("app.js", _CT_JS),
    ("app.css", _CT_CSS),
    ("cdeck.webmanifest", "application/manifest+json"),
    ("sw.js", _CT_JS),
    ("header.js", _CT_JS),
    ("header.css", _CT_CSS),
    ("kdash_native.js", _CT_JS),
    ("deck_more.html", _CT_HTML),
    ("deck_more.css", _CT_CSS),
    ("deck_tabs.js", _CT_JS),
    ("model_rater.js", _CT_JS),
    ("deck_profiles.js", _CT_JS),
    ("deck_settings.js", _CT_JS),
    ("deck_studio.js", _CT_JS),
    ("deck_forge.js", _CT_JS),
    ("deck_gitur.js", _CT_JS),
    ("deck_backup.js", _CT_JS),
    ("deck_session_kit.js", _CT_JS),
    ("deck_orders.js", _CT_JS),
    ("deck_sfx.js", _CT_JS),
    ("openwork.svg", _CT_SVG),
    ("skins/forge-engineroom.jpg", _CT_JPEG),
    ("skins/crucible-chamber.jpg", _CT_JPEG),
    ("skins/diligence-dealroom.jpg", _CT_JPEG),
    ("skins/docket-archive.jpg", _CT_JPEG),
    ("skins/ups-lab.jpg", _CT_JPEG),
    ("skins/differentiator-clinic.jpg", _CT_JPEG),
    ("skins/website-studio.jpg", _CT_JPEG),
    ("planets/jupiter.mp3", _CT_MP3),
    ("planets/mars.mp3", _CT_MP3),
    ("planets/venus.mp3", _CT_MP3),
    ("planets/mercury.mp3", _CT_MP3),
    ("planets/saturn.mp3", _CT_MP3),
    ("planets/uranus.mp3", _CT_MP3),
    ("planets/neptune.mp3", _CT_MP3),
)
_CDECK_UI_NAMES = frozenset(n for n, _ct in _CDECK_UI_FILES)
_CDECK_ROUTES = {"/cdeck/": ("index.html", _CT_HTML)}
for _n, _ct in _CDECK_UI_FILES:
    _CDECK_ROUTES["/cdeck/" + _n] = (_n, _ct)


_CDECK_PANEL_MOD = {
    "/api/v1/fleet": "cosmos_fleet_panel",
    "/api/v1/nodemap": "cosmos_nodemap_panel",
    "/api/v1/jukebox": "cosmos_jukebox_panel",
    "/api/v1/recents": "cosmos_recents_panel",
}


def _cdeck_panel_get(mod: str):
    """Lazy-import a builds/cdeck handle_get. Prefer the binder in
    builds/cdeck when present; fall back to cosmos/ so an uninitialized
    gitlink does not 503 a live Core. No new measurement."""
    import importlib
    import sys
    from pathlib import Path as _P
    d = str((_P(__file__).resolve().parent.parent / "builds" / "cdeck").resolve())
    if d not in sys.path:
        sys.path.insert(0, d)
    try:
        return getattr(importlib.import_module(mod), "handle_get")
    except ImportError:
        if d in sys.path:
            sys.path.remove(d)
        return getattr(importlib.import_module(mod), "handle_get")


def _cdeck_panel_invoke(hg, root, *, expected_tree_id, query=None):
    """Call a binder with only the kwargs its handle_get accepts.

    Recents takes query= (open= / id=). Fleet / nodemap / jukebox do not —
    passing query= is TypeError, swallowed as 503 CDECK_PANEL_NOT_COMPOSED.
    """
    import inspect
    params = inspect.signature(hg).parameters
    kw = {}
    if "expected_tree_id" in params:
        kw["expected_tree_id"] = expected_tree_id
    if "query" in params:
        kw["query"] = query
    return hg(root, **kw)


def _annotate_nodemap_row(row: dict) -> dict:
    """Attach GBW/SGH identity from the prober table. Never invents a model."""
    if not isinstance(row, dict):
        return row
    out = dict(row)
    lid = out.get("link_id") or out.get("id")
    try:
        from cosmos_rails_prober import identity_for
        ident = identity_for(str(lid or ""))
    except Exception:  # noqa: BLE001
        ident = {}
    for key, val in ident.items():
        if out.get(key) in (None, "", []):
            out[key] = val
    return out


def _nodemap_overlay_kernel(kernel, body: dict) -> dict:
    """Disk rails.json is proven-live only (often count 0). GET /nodemap is
    served while Kernel is up, so overlay registry.matrix() — the same rows
    GET /rails already returns — when the disk projection has no rows.
    Always annotate identity + stale list so System/Forge can paint RED
    and the SGH+GBW independence note. Does not rewrite the file."""
    if not isinstance(body, dict) or body.get("ok") is False:
        return body
    reg = body.get("registry") if isinstance(body.get("registry"), dict) else {}
    disk_mx = reg.get("matrix") if isinstance(reg.get("matrix"), list) else []
    kr = getattr(kernel, "registry", None)
    source = reg.get("source") or "disk"
    mx = list(disk_mx)
    stale = list(reg.get("stale") or [])
    if not mx and kr is not None:
        try:
            mx = list(kr.matrix() or [])
            source = "kernel.matrix"
        except Exception:  # noqa: BLE001
            mx = []
        if kr is not None:
            try:
                stale = list((kr.stale_nodes() or {}).values())
            except Exception:  # noqa: BLE001
                stale = stale
    if not mx and not stale:
        return body
    mx = [_annotate_nodemap_row(r) for r in mx]
    stale = [_annotate_nodemap_row(r) for r in stale]
    meta = dict(reg)
    meta["available"] = True
    meta["source"] = source
    meta["schema"] = meta.get("schema") or "cosmos-registry/1"
    meta["matrix"] = mx
    meta["stale"] = stale
    meta["composed"] = len(mx)
    meta["count"] = sum(1 for r in mx if r.get("verified") is True)
    meta["stale_count"] = len(stale)
    out = dict(body)
    out["registry"] = meta
    topo = out.get("topology") if isinstance(out.get("topology"), dict) else {}
    nodes = list(topo.get("nodes") or [])
    have = {n.get("id") for n in nodes if isinstance(n, dict)}
    for r in mx + stale:
        lid = r.get("link_id") or r.get("id")
        if not lid or lid in have:
            continue
        nodes.append({
            "id": lid,
            "label": r.get("node") or lid,
            "type": "rail",
            "proof_state": r.get("proof_state"),
            "model": r.get("model"),
            "independence_note": r.get("independence_note"),
        })
        have.add(lid)
    out["topology"] = {**topo, "nodes": nodes, "edges": topo.get("edges") or []}
    return out


def _cdeck_file(name: str):
    """Resolve one allowlisted file under builds/cdeck/ui/. `name` is a
    dict value from _CDECK_ROUTES, never a slice of the request path."""
    if name not in _CDECK_UI_NAMES:
        return None
    from pathlib import Path as _P
    here = _P(__file__).resolve().parent
    ui = (here.parent / "builds" / "cdeck" / "ui").resolve()
    cand = (ui / name).resolve()
    try:
        cand.relative_to(ui)
    except ValueError:
        return None
    return cand if cand.is_file() else None


# ---------------- voice hardening constants (2026-08-25) ----------------
# PHASE 4 seam: helpers live in cosmos_voice_hardening and are re-exported
# here -- same objects, not copies -- so make_handler's POST /api/v1/voice
# path (DEDUPE_WINDOW_S, STREAM_ROOTS, _bootup_summary) keeps working
# unchanged. Handlers below only call these helpers. Additive.
from cosmos_voice_hardening import (  # noqa: E402
    BU_MD_PATH, DEDUPE_WINDOW_S, STREAM_ROOTS,
    _BOOTUP_REPLY_CAP, _SPOKEN_CAP,
    _bootup_summary, _flat_trim, _stream_section,
)


class ServiceError(RuntimeError):
    """kind in {BLANK_TOKEN, TOKEN_MISSING, REMOTE_CLEARTEXT, REMOTE_OPEN_ACCESS,
    CERT_NOT_FOUND}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def _is_remote_bind(host: str) -> bool:
    return (host or "").strip().lower() not in _LOOPBACK_HOSTS


def _is_loopback_peer(addr: str) -> bool:
    """True iff the TCP peer is this machine (DT cDeck / local browser).

    Keith 2026-09-04: loopback auto-connects without a bearer; Tailscale/LAN
    still need the token. Mapped IPv4-in-IPv6 (::ffff:127.0.0.1) counts.
    """
    a = (addr or "").strip().lower()
    if a in _LOOPBACK_HOSTS:
        return True
    if a.startswith("::ffff:"):
        return a.rsplit(":", 1)[-1] == "127.0.0.1"
    return False


def _request_authed(peer: str, authorization: str, token: str,
                    open_access: bool = False) -> bool:
    """Bearer gate. Loopback DT auto-connects; Tailscale/phone/LAN still need it.

    open_access is loopback-bind only (Service refuses REMOTE_OPEN_ACCESS).
    Wrong bearer on loopback still passes — the peer is this machine.
    """
    if open_access:
        return True
    if _is_loopback_peer(peer):
        return True
    got = authorization or ""
    return hmac.compare_digest(
        got.encode("utf-8"), ("Bearer " + token).encode("utf-8"))


def _write_private(path, data: bytes) -> None:
    """Create/overwrite a secret-bearing file with owner-only perms (0o600) from
    the first byte - never default perms then a chmod race. On Windows the mode
    is advisory; NTFS ACLs inherit, and 0o600 is still the correct intent."""
    fd = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "wb") as fh:
        fh.write(data)


def _load_api_token(tok_file, remote: bool) -> str:
    """Bearer material is install config, not something the service invents on a
    remote bind. Empty/whitespace is always an open door and is REFUSED."""
    from pathlib import Path as _P
    tok_file = _P(tok_file)
    if not tok_file.exists():
        if remote:
            raise ServiceError(
                "TOKEN_MISSING",
                "api_token.txt is missing - refusing to invent authentication "
                "material in a remote context (a silently minted token is an "
                "open door on the LAN)")
        import secrets as _s
        _write_private(tok_file, _s.token_urlsafe(24).encode("utf-8"))
    token = tok_file.read_text(encoding="utf-8").strip()
    if not token:
        raise ServiceError(
            "BLANK_TOKEN",
            "api_token.txt is empty or whitespace - a blank token is an open door")
    return token


def _crucible_dispatchers(kernel, names) -> dict | None:
    """Critics are injected callables on the kernel (name -> packet_text -> return
    text). A requested critic that is not composed is not invented; None means
    the round cannot actually run."""
    pool = getattr(kernel, "crucible_critics", None)
    if not isinstance(pool, dict) or not pool:
        return None
    if not names:
        return dict(pool)
    out = {}
    for n in names:
        fn = pool.get(n)
        if not callable(fn):
            return None
        out[n] = fn
    return out or None


def make_handler(kernel: Kernel, token: str, open_access: bool = False):
    # ---- the safety seams, ONE instance each per handler class (2026-08-25).
    # State lives in config/ JSON files, so a restarted service keeps a kill
    # that was set and a day's spend that was counted.
    from cosmos_control import ControlChannel, ControlError
    from cosmos_spendguard import SpendGuard, PAUSED_REPLY, CALL_EST_USD
    _ctrl = ControlChannel(kernel.paths.config("control_state.json"),
                           clock=kernel._clock)
    _guard = SpendGuard(kernel.paths.config("spendguard_state.json"),
                        config_file=kernel.paths.config("spendguard_config.json"),
                        ledger=kernel.ledger, clock=kernel._clock)
    # The OPUS TURN CAP (cosmos_brain, 2026-08-25): Opus is not dollar-priced
    # like the API rails, so the USD breaker cannot bound it - a per-session
    # turn count can. Cap is tunable live via "opus_turns_per_session" in
    # spendguard_config.json (one tuning surface). Absent module -> None, and
    # the voice brain falls back to Grok (which the USD breaker does bound).
    try:
        from cosmos_brain import TurnGuard as _TurnGuard
        _turns = _TurnGuard(
            kernel.paths.config("opus_turns.json"),
            config_file=kernel.paths.config("spendguard_config.json"),
            clock=kernel._clock)
    except Exception:                                             # noqa: BLE001
        _turns = None
    # The turn cap's compiled-in default, so POST /api/v1/spend can state the
    # BEFORE value of opus_turns_per_session when the config file does not set
    # it. An absent brain module means the knob has no current value to widen
    # from - 0 makes any write to it a widen, which fails toward confirmation.
    try:
        from cosmos_brain import OPUS_TURNS_PER_SESSION as _OPUS_TURNS_DEFAULT
    except Exception:                                             # noqa: BLE001
        _OPUS_TURNS_DEFAULT = 0
    _dedupe: dict = {}                 # sha256 key -> epoch of first sight
    _dedupe_lock = threading.Lock()

    def _kill_token() -> str:
        """Optional gate on the off-switch: config/kill_token.txt, when it
        exists and is non-blank. Absent = ungated (the switch only reduces
        capability). Unreadable = fail CLOSED (require a token nobody can
        give, rather than an open mutation on an error)."""
        try:
            p = kernel.paths.config("kill_token.txt")
            if not p.exists():
                return ""
            return p.read_text(encoding="utf-8").strip() or "\x00UNREADABLE"
        except Exception:                                         # noqa: BLE001
            return "\x00UNREADABLE"

    class Handler(BaseHTTPRequestHandler):
        server_version = "COSMOS/1.0"

        # ------------ voice-refusal shape (mirrors VoiceMode's result) ------
        @staticmethod
        def _voice_refused(sid, kind, error, reply, spoken):
            return {"ok": False, "session_id": sid, "kind": kind,
                    "reply": reply, "spoken": spoken, "needs_confirm": False,
                    "confirm_id": None, "action": None, "sources": [],
                    "refused": True, "error": error}

        def _do_kill(self, client_id, token_given):
            kt = _kill_token()
            if kt and not hmac.compare_digest(
                    str(token_given or "").encode("utf-8"),
                    kt.encode("utf-8")):
                return self._send(403, {"error": "BAD_KILL_TOKEN",
                                        "detail": "kill_token.txt is set and "
                                                  "the given token does not "
                                                  "match"})
            st = _ctrl.kill(client_id or None)
            return self._send(200, {"killed": True,
                                    "client_id": client_id or None,
                                    "control": st})

        def _send(self, code: int, obj: dict):
            body = json.dumps({"served_at": time.time(), **obj}, indent=1).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _authed(self) -> bool:
            # Keith 2026-09-04: DT cDeck auto-connects. Peer on 127.0.0.1/::1
            # skips the bearer; Tailscale/phone/LAN still need it.
            peer = ""
            try:
                peer = self.client_address[0]
            except Exception:  # noqa: BLE001
                peer = ""
            return _request_authed(
                peer, self.headers.get("Authorization", "") or "",
                token, open_access)

        def _drain_body(self, cap: int = _MAX_BODY_BYTES) -> None:
            """Discard a pending request body before an early refusal.

            Replying and closing while the client is still sending makes Windows
            RST the connection, so the caller sees ConnectionResetError instead of
            the status we sent. An auth failure must reach the client as 401, not
            as a transport error. Best effort: a body we cannot drain is not worth
            failing the refusal over. (Scar 2026-08-30: test_makers flaked ~25% of
            runs on exactly this, and a phone with a stale token would have seen a
            network error rather than "unauthorized".)
            """
            try:
                n = int(self.headers.get("Content-Length") or 0)
            except (TypeError, ValueError):
                return
            if n <= 0:
                return
            remaining = min(n, cap)
            try:
                while remaining > 0:
                    chunk = self.rfile.read(min(65536, remaining))
                    if not chunk:
                        break
                    remaining -= len(chunk)
            except OSError:
                pass

        def _read_body(self, cap: int = _MAX_BODY_BYTES):
            """Read the POST body under a hard cap, or send a controlled refusal
            and return None. A missing/negative/non-int/oversized Content-Length
            is rejected BEFORE any read - rfile.read(N) on an unbounded N is a
            memory DoS, and read(-1) blocks on the open socket."""
            raw = self.headers.get("Content-Length")
            if raw is None:
                self._send(400, {"error": "LENGTH_REQUIRED",
                                 "detail": "Content-Length header is required"})
                return None
            try:
                n = int(raw)
            except ValueError:
                self._send(400, {"error": "BAD_LENGTH",
                                 "detail": f"Content-Length is not an integer: "
                                           f"{raw[:64]!r}"})
                return None
            if n < 0:
                self._send(400, {"error": "BAD_LENGTH",
                                 "detail": "Content-Length must be non-negative"})
                return None
            if n > cap:
                self._send(413, {"error": "BODY_TOO_LARGE",
                                 "detail": f"body of {n} bytes exceeds the "
                                           f"{cap}-byte cap for this endpoint"})
                return None
            return self.rfile.read(n)

        def _send_static(self, name: str, ctype: str, finder=_frontend_file):
            """Serve one allowlisted shell file as bytes. A missing file is an
            honest 404 (SHELL_FILE_MISSING), never a silent empty page."""
            path = finder(name)
            if path is None:
                return self._send(404, {"error": "SHELL_FILE_MISSING",
                                        "file": name})
            body = path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("X-Content-Type-Options", "nosniff")
            # the service worker does shell caching; the server stays honest
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(body)

        def _redirect(self, loc: str):
            self.send_response(302)
            self.send_header("Location", loc)
            self.send_header("Content-Length", "0")
            self.end_headers()

        def do_GET(self):                                             # noqa: N802
            # Static app shell FIRST, without the bearer (see _STATIC_ROUTES
            # and _CDECK_ROUTES: fixed files, no data, no token). Everything
            # below this line keeps requiring the bearer exactly as before.
            from urllib.parse import parse_qs as _parse_qs
            from urllib.parse import urlparse as _urlparse
            parsed = _urlparse(self.path)
            if parsed.path == "/cdeck":
                # trailing slash so relative href="app.css" stays under /cdeck/
                return self._redirect("/cdeck/")
            route = _STATIC_ROUTES.get(parsed.path)
            if route is not None:
                return self._send_static(*route)
            route = _CDECK_ROUTES.get(parsed.path)
            if route is not None:
                return self._send_static(*route, finder=_cdeck_file)
            if parsed.path == "/kill":
                # the browser-convenience OFF-SWITCH: no bearer (it can only
                # reduce capability); the optional kill token still gates it.
                q = _parse_qs(parsed.query)
                return self._do_kill(q.get("client_id", [""])[0],
                                     q.get("token", [""])[0])
            if not self._authed():
                self._drain_body()
                return self._send(401, {"error": "UNAUTHORIZED"})
            if parsed.path == "/api/v1/control":
                # what the app POLLS. Bearer-authed like every /api/v1 read;
                # NEVER touched by the spend breaker - a spend-blocked phone
                # must still see (and clear) its own state.
                cid = _parse_qs(parsed.query).get("client_id", [""])[0]
                try:
                    return self._send(200, _ctrl.get(cid or None))
                except ControlError as e:
                    return self._send(500, {"error": e.kind,
                                            "detail": str(e)[:300]})
            if self.path == "/api/v1/status":
                last = kernel.ledger.last()
                return self._send(200, {"ready": kernel.ready,
                                        "root": str(kernel.paths.root),
                                        "tree_id": kernel.paths.sentinel.tree_id,
                                        "ledger_head": {"seq": last["seq"],
                                                        "event": last["event"]}})
            if self.path == "/api/v1/audit":
                return self._send(200, kernel.audit())
            if self.path == "/api/v1/jobs":
                st = kernel.sched._state()
                return self._send(200, {"measured_at": time.time(),
                                        "jobs": {j: v["st"] for j, v in st.items()}})
            if self.path == "/api/v1/health":
                from cosmos_health import snapshot as health_snapshot
                return self._send(200, health_snapshot(kernel))
            if self.path == "/api/v1/spend":
                return self._send(200, kernel.spend.audit())
            if self.path == "/api/v1/tools":
                from cosmos_tools import ToolContracts
                # F-29 composed the tools/ surface onto kernel.tools
                # (inventory/invoke). GET /tools is the ToolContracts
                # registry report (disposition + verified + age). Do not
                # call .report() on a surface that is not the registry —
                # a promotion that keeps boot green can still 500 this
                # route (wave3 AttributeError / RemoteDisconnected scar).
                bound = getattr(kernel, "tools", None)
                tc = (bound if isinstance(bound, ToolContracts)
                      else ToolContracts(kernel.ledger))
                return self._send(200, {"measured_at": time.time(),
                                        "report": tc.report()})
            if parsed.path == "/api/v1/tools_kit":
                from cosmos_tools_kit import snapshot as tools_kit_snapshot
                rec = tools_kit_snapshot(kernel)
                rec["tree_id"] = kernel.paths.sentinel.tree_id
                return self._send(200, rec)
            if parsed.path == "/api/v1/voice_loop":
                from cosmos_voice_loop import snapshot as voice_loop_snapshot
                rec = voice_loop_snapshot(kernel)
                rec["tree_id"] = kernel.paths.sentinel.tree_id
                return self._send(200, rec)
            if self.path.startswith("/api/v1/events"):
                # THE LIVE-BACKEND PRIMITIVE: ledger tail since a sequence - the
                # interactive frontend polls this append-only; old events never refetch.
                # Default window = oldest EVENTS_PAGE past since_seq (cursor
                # contract, unchanged). ?tail=N = newest N past since_seq, so
                # a cold dashboard is one request, not two. One verify() walk
                # (head_seq comes off that walk — never a second full verify).
                from urllib.parse import parse_qs, urlparse
                q = parse_qs(urlparse(self.path).query)
                raw_since = q.get("since_seq", ["0"])[0]
                try:
                    since = int(raw_since)
                except ValueError:
                    return self._send(400, {"error": "BAD_SINCE_SEQ",
                                            "detail": f"since_seq must be an "
                                                      f"integer: {raw_since[:64]!r}"})
                if since < 0 or since > (1 << 62):
                    return self._send(400, {"error": "BAD_SINCE_SEQ",
                                            "detail": "since_seq must be a "
                                                      "non-negative bounded integer"})
                raw_tail = q.get("tail", [None])[0]
                tail = None
                if raw_tail is not None:
                    try:
                        tail = int(raw_tail)
                    except ValueError:
                        return self._send(400, {"error": "BAD_TAIL",
                                                "detail": f"tail must be an "
                                                          f"integer: {raw_tail[:64]!r}"})
                    if tail < 1 or tail > EVENTS_PAGE:
                        return self._send(400, {"error": "BAD_TAIL",
                                                "detail": f"tail must be 1.."
                                                          f"{EVENTS_PAGE}"})
                head, evs = page_events(kernel.ledger, since, tail=tail)
                return self._send(200, {"head_seq": head, "events": evs})
            if self.path in ("/api/v1/rails", "/api/v1/nodes"):
                reg = getattr(kernel, "registry", None)
                if reg is None:
                    # CRITIC M3 FIX: an uncomposed registry was a silent 200+empty -
                    # "no links" and "not composed" read identically. 503 is the truth.
                    return self._send(503, {"error": "REGISTRY_NOT_COMPOSED",
                                            "detail": "kernel has no registry - this is "
                                                      "a composition fault, not an empty "
                                                      "rails matrix"})
                return self._send(200, {"measured_at": time.time(),
                                        "matrix": reg.matrix()})
            if parsed.path == "/api/v1/surfaces":
                sf = getattr(kernel, "surfaces", None)
                if sf is None:
                    return self._send(503, {"error": "SURFACES_NOT_COMPOSED",
                                            "detail": "kernel has no surfaces map - this is "
                                                      "a composition fault, not an empty "
                                                      "catalog"})
                return self._send(200, {"measured_at": time.time(),
                                        "surfaces": sf.report()})
            if parsed.path == "/api/v1/surfaces_kit":
                from cosmos_surfaces_kit import snapshot as surfaces_kit_snapshot
                rec = surfaces_kit_snapshot(kernel)
                rec["tree_id"] = kernel.paths.sentinel.tree_id
                return self._send(200, rec)
            if parsed.path in _CDECK_PANEL_MOD:
                try:
                    hg = _cdeck_panel_get(_CDECK_PANEL_MOD[parsed.path])
                    tid = kernel.paths.sentinel.tree_id
                    q = None
                    if parsed.path == "/api/v1/recents":
                        from urllib.parse import parse_qs
                        q = parse_qs(parsed.query)
                    code, body = _cdeck_panel_invoke(
                        hg, kernel.paths.root,
                        expected_tree_id=tid, query=q)
                except Exception as e:  # noqa: BLE001
                    return self._send(503, {
                        "error": "CDECK_PANEL_NOT_COMPOSED",
                        "detail": "%s: %s" % (type(e).__name__, e),
                    })
                if parsed.path == "/api/v1/nodemap" and code == 200:
                    body = _nodemap_overlay_kernel(kernel, body)
                return self._send(code, body)
            if self.path.startswith("/api/v1/makers"):
                from urllib.parse import parse_qs, urlparse
                from cosmos_makers import MakerError
                parsed = urlparse(self.path)
                if parsed.path != "/api/v1/makers":
                    return self._send(404, {"error": "NOT_FOUND", "path": self.path})
                mm = getattr(kernel, "makers", None)
                if mm is None:
                    # M3: "not composed" is not "empty". GET must not seed (B1).
                    return self._send(503, {"error": "MAKERS_NOT_COMPOSED",
                                            "detail": "kernel has no maker map - this is "
                                                      "a composition fault, not an empty "
                                                      "catalog"})
                q = parse_qs(parsed.query)
                kind = q.get("kind", [None])[0]
                tag = q.get("tag", [None])[0]
                text = q.get("text", [None])[0]
                try:
                    rows = mm.find(tag=tag, kind=kind, text=text)
                except MakerError as e:
                    return self._send(400, {"error": e.kind, "detail": str(e)[:300]})
                return self._send(200, {"measured_at": time.time(),
                                        "makers": rows})
            if parsed.path == "/api/v1/gitur":
                from cosmos_gitur import GiturError, snapshot as gitur_snapshot
                try:
                    return self._send(200, gitur_snapshot(kernel))
                except GiturError as e:
                    return self._send(400, {"error": e.kind, "detail": str(e)[:300]})
            if parsed.path == "/api/v1/crew":
                from cosmos_crew_roster import snapshot as crew_snapshot
                rec = crew_snapshot(kernel.paths)
                rec["tree_id"] = kernel.paths.sentinel.tree_id
                return self._send(200, rec)
            if parsed.path == "/api/v1/cred":
                from cosmos_cred_kit import snapshot as cred_snapshot
                rails = {}
                try:
                    reg = getattr(kernel, "registry", None)
                    if reg is not None:
                        for r in (reg.matrix() or []):
                            if isinstance(r, dict) and r.get("link_id"):
                                rails[r["link_id"]] = r
                except Exception:  # noqa: BLE001
                    rails = {}
                rec = cred_snapshot(kernel.paths, rails=rails)
                rec["tree_id"] = kernel.paths.sentinel.tree_id
                return self._send(200, rec)
            if parsed.path == "/api/v1/agents":
                from cosmos_cred_kit import agents_snapshot
                rec = agents_snapshot()
                rec["tree_id"] = kernel.paths.sentinel.tree_id
                return self._send(200, rec)
            if parsed.path == "/api/v1/mcp":
                from cosmos_mcp_client import named_servers
                rec = named_servers()
                rec["measured_at"] = time.time()
                rec["tree_id"] = kernel.paths.sentinel.tree_id
                return self._send(200, rec)
            if parsed.path == "/api/v1/research_call":
                from cosmos_research_call import snapshot as research_call_snapshot
                rec = research_call_snapshot(kernel.paths)
                rec["tree_id"] = kernel.paths.sentinel.tree_id
                return self._send(200, rec)
            if parsed.path == "/api/v1/studio":
                from cosmos_studio import snapshot as studio_snapshot
                rec = studio_snapshot(kernel.paths)
                rec["tree_id"] = kernel.paths.sentinel.tree_id
                return self._send(200, rec)
            if parsed.path == "/api/v1/profiles":
                from urllib.parse import parse_qs as _pf_qs
                from cosmos_profiles import ProfileError, snapshot as profiles_snapshot
                q = _pf_qs(parsed.query)
                try:
                    rec = profiles_snapshot(
                        kernel.paths,
                        profile=(q.get("profile") or [""])[0],
                    )
                except ProfileError as e:
                    return self._send(400, {"error": e.kind, "detail": str(e)[:300]})
                rec["measured_at"] = time.time()
                rec["tree_id"] = kernel.paths.sentinel.tree_id
                return self._send(200, rec)
            if parsed.path == "/api/v1/backup":
                from cosmos_backup_fold import snapshot as backup_snapshot
                rec = backup_snapshot(kernel.paths)
                rec["tree_id"] = kernel.paths.sentinel.tree_id
                return self._send(200, rec)
            if parsed.path == "/api/v1/session_kit":
                from cosmos_session_kit import snapshot as session_kit_snapshot
                rec = session_kit_snapshot(kernel.paths)
                rec["tree_id"] = kernel.paths.sentinel.tree_id
                return self._send(200, rec)
            if parsed.path == "/api/v1/session_tools":
                from cosmos_session_tools_kit import snapshot as session_tools_snapshot
                rec = session_tools_snapshot(kernel.paths)
                rec["tree_id"] = kernel.paths.sentinel.tree_id
                return self._send(200, rec)
            if parsed.path == "/api/v1/orc":
                from cosmos_orc_boot import inspect_boot as orc_inspect
                rec = orc_inspect(kernel.paths)
                rec["measured_at"] = time.time()
                rec["tree_id"] = kernel.paths.sentinel.tree_id
                return self._send(200, rec)
            if parsed.path == "/api/v1/runs_ops":
                from cosmos_runs_ops import snapshot as runs_ops_snapshot
                rec = runs_ops_snapshot(kernel)
                rec["tree_id"] = kernel.paths.sentinel.tree_id
                return self._send(200, rec)
            if parsed.path == "/api/v1/review":
                from urllib.parse import parse_qs as _rv_qs
                from cosmos_review import snapshot as review_snapshot
                q = _rv_qs(parsed.query)
                rec = review_snapshot(kernel, window=(q.get("window") or ["week"])[0])
                rec["tree_id"] = kernel.paths.sentinel.tree_id
                return self._send(200, rec)
            if parsed.path == "/api/v1/work_orders":
                from urllib.parse import parse_qs as _wo_list_qs
                from cosmos_work_order import OrderError, fold_work_orders
                q = _wo_list_qs(parsed.query)
                try:
                    rec = fold_work_orders(
                        kernel.paths,
                        order_id=(q.get("id") or [""])[0],
                        state=(q.get("state") or [""])[0],
                        limit=(q.get("limit") or ["200"])[0],
                    )
                except OrderError as e:
                    return self._send(400, {"error": e.kind, "detail": str(e)[:300]})
                rec["measured_at"] = time.time()
                rec["tree_id"] = kernel.paths.sentinel.tree_id
                return self._send(200, rec)
            if parsed.path == "/api/v1/model_rater/roles":
                from urllib.parse import parse_qs as _mr_roles_qs
                from cosmos_model_rater import scan_roles
                q = _mr_roles_qs(parsed.query)
                rec = scan_roles(kernel.paths, q=(q.get("q") or [""])[0])
                rec["measured_at"] = time.time()
                rec["tree_id"] = kernel.paths.sentinel.tree_id
                return self._send(200, rec)
            if parsed.path == "/api/v1/model_rater":
                from urllib.parse import parse_qs as _mr_qs
                from cosmos_model_rater import ModelRaterError, snapshot
                q = _mr_qs(parsed.query)
                try:
                    rec = snapshot(
                        kernel.paths,
                        sort=(q.get("sort") or ["price"])[0],
                        desc=(q.get("desc") or ["0"])[0] in ("1", "true", "yes"),
                        type_name=(q.get("type") or [""])[0],
                        q=(q.get("q") or [""])[0],
                        limit=(q.get("limit") or [400])[0],
                        show_banned=(q.get("show_banned") or ["0"])[0]
                        in ("1", "true", "yes"),
                        role_q=(q.get("role_q") or [""])[0],
                        input_modalities=(q.get("input_modalities") or [""])[0],
                        output_modalities=(q.get("output_modalities") or [""])[0],
                        category=(q.get("category") or [""])[0],
                    )
                except ModelRaterError as e:
                    return self._send(400, {"error": e.kind, "detail": str(e)[:300]})
                rec["measured_at"] = time.time()
                return self._send(200, rec)
            if parsed.path == "/api/v1/porosity":
                from urllib.parse import parse_qs as _poro_qs
                from cosmos_porosity import snapshot as porosity_snapshot
                q = _poro_qs(parsed.query)
                agents_raw = (q.get("agents") or [""])[0]
                agents = [a.strip() for a in str(agents_raw).split(",")
                          if a.strip()]
                rec = porosity_snapshot(
                    kernel.paths,
                    profile=(q.get("profile") or [""])[0],
                    agents=agents or None,
                )
                rec["measured_at"] = time.time()
                rec["tree_id"] = kernel.paths.sentinel.tree_id
                return self._send(200, rec)
            if parsed.path == "/api/v1/usage":
                from cosmos_openrouter_rail import snapshot_usage
                rec = snapshot_usage(kernel.paths)
                rec["measured_at"] = time.time()
                rec["tree_id"] = kernel.paths.sentinel.tree_id
                return self._send(200, rec)
            if parsed.path == "/api/v1/cvm/pull":
                # CVM P3 additive. Bearer already checked. Projection is the
                # source of truth; this branch does not rewrite pull.json and
                # does not append the ledger.
                cid = (_parse_qs(parsed.query).get("client_id", [""])[0]
                       or "").strip()
                if not cid:
                    return self._send(400, {"error": "CLIENT_ID_REQUIRED",
                                            "detail": "client_id query is required"})
                try:
                    return self._send(200, _cvm_pull_response(kernel, cid))
                except CvmError as e:
                    code = 400 if e.kind in (
                        "IDENTITY_MISMATCH", "CLIENT_ID_REQUIRED",
                        "BAD_SNAPSHOT") else 500
                    return self._send(code, {"error": e.kind,
                                            "detail": str(e)[:300]})
            return self._send(404, {"error": "NOT_FOUND", "path": self.path})

        def do_POST(self):                                            # noqa: N802
            if self.path == "/api/v1/kill":
                # the HUMAN OFF-SWITCH: served without the bearer, because it
                # can only reduce capability (mic_off + clear_queue) and must
                # work from anything that can reach the port. Optional token
                # gate via config/kill_token.txt. Body is optional JSON.
                d = {}
                if self.headers.get("Content-Length"):
                    body = self._read_body()
                    if body is None:
                        return
                    if body.strip():
                        try:
                            d = json.loads(body.decode("utf-8"))
                        except Exception:                         # noqa: BLE001
                            d = {}
                if not isinstance(d, dict):
                    d = {}
                return self._do_kill(str(d.get("client_id") or ""),
                                     str(d.get("token") or ""))
            if not self._authed():
                self._drain_body()
                return self._send(401, {"error": "UNAUTHORIZED"})
            if self.path == "/api/v1/control/resume":
                # the explicit road back: clears the control flags AND resets
                # the local spend counters ("say 'resume' or clear it on the
                # desktop"). Bearer-authed: OFF is cheap by design, ON is a
                # deliberate act.
                body = self._read_body()
                if body is None:
                    return
                try:
                    d = json.loads(body.decode("utf-8")) if body.strip() else {}
                except Exception as e:                            # noqa: BLE001
                    return self._send(400, {"error": "BAD_REQUEST",
                                            "detail": str(e)[:200]})
                cid = str(d.get("client_id") or "") or None
                st = _ctrl.resume(cid)
                cleared = _guard.clear(cid)
                return self._send(200, {"resumed": True, "client_id": cid,
                                        "spend_counters_cleared": cleared,
                                        "control": st})
            if self.path == "/api/v1/spend":
                # F-03: the WRITE side of the money surface. GET /spend showed
                # every cap and could change none of them; this sets a rail cap
                # or the breaker thresholds. Body is bounded BEFORE the read
                # (service.every_body_is_bounded_before_it_is_read) and small -
                # a cap change is a handful of numbers.
                import hashlib as _hashlib
                from cosmos_spend_admin import handle_post as _spend_post
                body = self._read_body(_MAX_SPEND_BODY_BYTES)
                if body is None:
                    return
                try:
                    payload = json.loads(body.decode("utf-8")) if body.strip() else {}
                except Exception as e:                            # noqa: BLE001
                    return self._send(400, {"error": "BAD_REQUEST",
                                            "kind": "BAD_REQUEST",
                                            "detail": str(e)[:200]})
                # WHO. Derived from the bearer this request just proved it holds
                # - a sha256 PREFIX, never the token itself. Under --no-auth
                # there is no proven bearer, so the record says so rather than
                # claiming an identity nobody presented.
                actor = ("bearer:" + _hashlib.sha256(
                    token.encode("utf-8")).hexdigest()[:16]) if not open_access \
                    else "open-access:no-bearer-presented"
                code, out = _spend_post(
                    kernel, _guard,
                    kernel.paths.config("spendguard_config.json"),
                    payload, actor,
                    turn_default=_OPUS_TURNS_DEFAULT,
                    remote=str(self.client_address[0]
                               if self.client_address else ""))
                return self._send(code, out)
            if self.path == "/api/v1/voice":
                # VOICE MODE: session-continuous voice seam. Body:
                #   {transcript, session_id?, mode?, confirm_id?}
                # No session_id -> a session is minted and returned; the client
                # carries the sid (the sid, not the handset, holds the
                # conversation). Consequential transcripts come back
                # needs_confirm+confirm_id - NEVER executed silently.
                import hashlib as _hashlib
                from cosmos_command import Commander
                from cosmos_convo import ConvoStore, ConvoError
                from cosmos_voice import VoiceMode, VoiceError, MAX_TRANSCRIPT
                body = self._read_body()
                if body is None:
                    return
                try:
                    d = json.loads(body.decode("utf-8"))
                    # Input caps BEFORE anything touches the chain: an
                    # oversized transcript/title is a 400, not a ledger write.
                    transcript = str(d.get("transcript") or "")
                    if len(transcript) > MAX_TRANSCRIPT:
                        return self._send(400, {
                            "error": "TRANSCRIPT_TOO_LONG",
                            "detail": f"transcript of {len(transcript)} chars "
                                      f"exceeds the {MAX_TRANSCRIPT}-char cap"})
                    title = str(d.get("title") or "voice session")
                    if len(title) > 200:
                        return self._send(400, {
                            "error": "TITLE_TOO_LONG",
                            "detail": f"title of {len(title)} chars exceeds "
                                      f"the 200-char cap"})
                    # ---- HARDENING (2026-08-25): telemetry fields in, then
                    # control -> dedupe -> spend breaker, ALL before anything
                    # touches a model, the orchestrator, or the convo chain.
                    client_id = str(d.get("client_id") or "")[:120]
                    build = str(d.get("build") or "")[:120]
                    stream = str(d.get("stream") or d.get("project")
                                 or "").strip().lower()[:40]
                    idem = str(d.get("idempotency_key") or "")[:120]
                    sid_in = str(d.get("session_id") or "") or None
                    guard_key = sid_in or client_id or "anon"
                    # 1. CONTROL: pause/mic_off refuses FAST, zero spend, zero
                    # ledger writes. blocked() fails closed by construction.
                    is_blocked, why = _ctrl.blocked(client_id or None)
                    if is_blocked:
                        return self._send(200, self._voice_refused(
                            sid_in, "refused", "CONTROL_BLOCKED",
                            f"[CONTROL_BLOCKED] voice is {why} - nothing was "
                            f"recorded, nothing was spent; resume from the "
                            f"desktop or POST /api/v1/control/resume",
                            "Voice is paused."))
                    # 2. DEDUPE: an identical (client_id, utterance [+ confirm
                    # nonce]) inside the window is the SAME utterance heard
                    # twice - dropped, zero spend. The confirm_id is part of
                    # the key so a confirm re-call is never eaten as a dupe.
                    if transcript.strip():
                        dk = idem or _hashlib.sha256(
                            (client_id + "|"
                             + " ".join(transcript.split()).lower() + "|"
                             + str(d.get("confirm_id") or "")
                             ).encode("utf-8")).hexdigest()
                        now_d = time.time()
                        with _dedupe_lock:
                            for k in [k for k, t0 in _dedupe.items()
                                      if now_d - t0 > DEDUPE_WINDOW_S]:
                                del _dedupe[k]
                            dup = dk in _dedupe
                            if not dup:
                                _dedupe[dk] = now_d
                        if dup:
                            return self._send(200, self._voice_refused(
                                sid_in, "duplicate", "DUPLICATE",
                                f"[DUPLICATE] identical utterance from this "
                                f"client within {DEDUPE_WINDOW_S:.0f}s - "
                                f"dropped, nothing was recorded, nothing "
                                f"was spent", ""))
                    # 3. SPEND BREAKER: session/day USD caps + rate limit,
                    # BEFORE any model/orchestrator call. Fails CLOSED; a
                    # refusal is a canned LOCAL reply costing zero.
                    allowed, reason = _guard.check(guard_key)
                    if not allowed:
                        return self._send(200, self._voice_refused(
                            sid_in, "refused", "SPEND_BLOCKED",
                            f"[SPEND_BLOCKED] {reason} - {PAUSED_REPLY}",
                            PAUSED_REPLY))
                    # 4. TELEMETRY: the build/stream/client provenance goes on
                    # the chain (only when a client actually sent any - a bare
                    # caller adds no ledger noise). Best-effort by design.
                    if client_id or build or stream or idem:
                        try:
                            kernel.ledger.append("VOICE_TELEMETRY", {
                                "client_id": client_id, "build": build,
                                "stream": stream, "session_id": sid_in,
                                "idempotency_key": idem})
                        except Exception:                         # noqa: BLE001
                            pass
                    # 5. BOOTUP (read-only): a payload asking for bootup gets
                    # the stream's handoff summary - no model, no writes.
                    if str(d.get("action") or "").strip().lower() == "bootup":
                        return self._send(200, _bootup_summary(
                            stream, session_id=sid_in))
                    # The authenticated principal: derived from the bearer the
                    # request just proved it holds. One principal today;
                    # device-scoped tokens will each derive their own, and the
                    # ownership seam is already closed.
                    principal = ("bearer:" + _hashlib.sha256(
                        token.encode("utf-8")).hexdigest()[:16])
                    convo = ConvoStore(kernel.ledger, clock=kernel._clock)
                    # ASK: compose the asker OVER the spend gate. VoiceMode never
                    # spends - the money decision lives HERE (guarded_call: reserve
                    # -> deny-or-call -> settle). Incumbents/gate absent -> asker
                    # stays None and 'ask' refuses in-band (ASK_UNAVAILABLE).
                    asker = None
                    _spend = getattr(kernel, "spend", None)
                    if _spend is not None:
                        try:
                            from cosmos_node_rails import NodeRail
                            _ASK_RAILS = {
                                "grok":   ("sgh-api", "bts_sgh", 0.02, 10.0),
                                "gemini": ("gem-api", "bts_gem", 0.03, 300.0),
                                "openai": ("oa-api", "bts_oa_api", 0.05, 5.0),
                            }

                            def asker(question, model=None):
                                link, mod, est, budget = _ASK_RAILS.get(
                                    model or "grok", _ASK_RAILS["grok"])
                                if link not in _spend.audit()["rails"]:
                                    _spend.set_budget(link, budget)
                                # paths= so NodeRail reads live/config/node_rails.json
                                # bts_root. Without it, __import__('bts_sgh') is
                                # UNREACHABLE (Talk MODEL_FAILED 2026-09-01).
                                rail = NodeRail(mod, metered_usd=est,
                                                paths=kernel.paths)
                                r = _spend.guarded_call(
                                    link, est,
                                    lambda: rail.dispatch({"prompt": question}))
                                if not r.get("ok"):
                                    return {"ok": False, "error": r.get("kind"),
                                            "detail": r.get("detail")}
                                return {"text": r.get("text", ""),
                                        "model": r.get("node", mod),
                                        "usd": r.get("usd"),
                                        "link_id": link,
                                        "rail": r.get("rail") or link,
                                        "node": r.get("node") or mod,
                                        "rid": r.get("rid")}
                        except Exception:                             # noqa: BLE001
                            asker = None
                    # HANDED ORCHESTRATOR: free speech gets TOOLS and a BRAIN.
                    # HYBRID ROUTING (2026-08-25): obvious file/data lookups
                    # stay on the FAST LOCAL path - rule-routed to search_files
                    # (x.ai's Responses API doesn't do chat-completions function
                    # calling), the spend-gated Grok ask phrases the found
                    # paths; these must stay instant, NO Opus call. Everything
                    # else - the free-form conversational turn - goes to the
                    # OPUS brain via the local claude CLI (cosmos_brain), with
                    # native read access to the stream's roots (--add-dir) and
                    # a claude session derived DETERMINISTICALLY from the
                    # COSMOS sid, so the road conversation is resumable in the
                    # desktop app via /resume. Opus is BOUNDED: control state
                    # and the rate limit are re-checked before EVERY Opus call
                    # (an orchestrator run can call more than once), plus the
                    # per-session TURN CAP; a timeout/failure/over-cap FALLS
                    # BACK to Grok so voice never hangs on a dead brain. Which
                    # brain answered lands on the reply and the ledger. Tools
                    # are READ-ONLY over registered roots + the real ITC.
                    # Absent gate -> orchestrator None and VoiceMode falls
                    # back to the bare asker.
                    orchestrator = None
                    _brain_used = {"brain": "local", "why": ""}
                    _sid_box = {"sid": sid_in}
                    if _spend is not None:
                        try:
                            import re as _re, sys as _sys  # noqa: F401
                            _sgh = None       # no-BTS (P4): the SGH brain import is
                            # retired; cosmos_brain (below) is the only brain path.
                            try:
                                import cosmos_brain as _cbrain
                            except Exception:                     # noqa: BLE001
                                _cbrain = None    # Grok-only host: no brain
                            from cosmos_orchestrator import (Orchestrator,
                                                             build_tools)
                            # Legal + COSMOS FIRST (small, high-signal) so a hit
                            # lands before V:\Ai's huge tmp/ exhausts the walk cap.
                            _ROOTS = [r"V:\Ai\Legal", r"V:\A\Ai\COSMOS",
                                      r"V:\Ai\ROLD", r"V:\Ai\BTS_MESH", r"V:\Ai"]
                            # STREAM SCOPING (2026-08-25): a declared stream
                            # puts its roots FIRST, so the walk cap spends
                            # itself where the session actually lives.
                            if stream in STREAM_ROOTS:
                                _sr = STREAM_ROOTS[stream]
                                _ROOTS = _sr + [r for r in _ROOTS
                                                if r not in _sr]
                            if _sgh is not None \
                                    and "sgh-api" not in _spend.audit()["rails"]:
                                _spend.set_budget("sgh-api", 10.0)
                            _PRE = ("You are COSMOS, the user's self-hosted voice "
                                    "assistant with access to his files. Answer "
                                    "concisely for text-to-speech - a few plain "
                                    "sentences, no markdown. When search results "
                                    "are provided, answer from them and name the "
                                    "file(s) found.")

                            def _grok_call(ctx):
                                """The spend-gated Grok ask (the old synthesis
                                path, and the Opus fallback). VOICE PATH ONLY:
                                wall-clock cap = cosmos_brain.GROK_FALLBACK_S
                                (never the rail default 60s) so Opus 45 +
                                Grok fallback stays inside the 70s client."""
                                grok_s = (
                                    float(_cbrain.GROK_FALLBACK_S)
                                    if _cbrain is not None else 20.0)
                                box = {"r": None, "e": None}

                                def _invoke():
                                    try:
                                        if _sgh is not None:
                                            r = _spend.guarded_call(
                                                "sgh-api", 0.02,
                                                lambda: _sgh.ask(ctx))
                                        elif asker is not None:
                                            # P4 retired the direct bts_sgh
                                            # import; reuse the already-
                                            # composed voice asker (NodeRail).
                                            out = asker(ctx, "grok")
                                            if out.get("ok") is False:
                                                raise RuntimeError(
                                                    f"[{out.get('error')}] "
                                                    f"{out.get('detail')}")
                                            r = {"ok": True,
                                                 "text": out.get("text") or ""}
                                        else:
                                            raise RuntimeError(
                                                "[NO_RAIL] no Grok rail "
                                                "composed and the Opus "
                                                "brain did not answer")
                                        box["r"] = r
                                    except Exception as e:        # noqa: BLE001
                                        box["e"] = e

                                th = threading.Thread(
                                    target=_invoke, daemon=True)
                                th.start()
                                th.join(grok_s)
                                if th.is_alive():
                                    raise RuntimeError(
                                        f"[TIMEOUT] grok fallback exceeded "
                                        f"{grok_s:.0f}s")
                                if box["e"] is not None:
                                    raise box["e"]
                                r = box["r"] or {}
                                if not r.get("ok"):
                                    raise RuntimeError(
                                        f"[{r.get('kind')}] {r.get('detail')}")
                                return {"ok": True,
                                        "content": r.get("text")
                                        or r.get("content") or ""}

                            def _model_call(messages, tools_schema):
                                user = next((m["content"] for m in messages
                                             if m.get("role") == "user"), "")
                                ran = [m for m in messages
                                       if m.get("role") == "tool"]
                                if not ran:
                                    low = user.lower()
                                    # COMMAND/LOOKUP SHAPE -> the fast local
                                    # path, exactly as before. NO Opus call.
                                    if any(k in low for k in (
                                            "find", "search", "where", "look for",
                                            "locate", "show me", "list")):
                                        stop = {"find", "search", "where", "is",
                                                "are", "the", "a", "an", "my",
                                                "for", "look", "locate", "show",
                                                "me", "in", "on", "under", "of",
                                                "stream", "file", "files", "about",
                                                "to", "and", "list", "please"}
                                        ws = _re.findall(r"[a-z0-9_.\-]+", low)
                                        terms = [w for w in ws
                                                 if w not in stop and len(w) > 2]
                                        q = " ".join(terms[:4]) if terms else user
                                        return {"ok": True, "tool_calls": [
                                            {"id": "1", "name": "search_files",
                                             "arguments": {"query": q}}]}
                                    # FREE-FORM -> the OPUS brain, BOUNDED.
                                    if _cbrain is not None and _turns is not None:
                                        blkd, bwhy = _ctrl.blocked(
                                            client_id or None)
                                        if blkd:
                                            raise RuntimeError(
                                                f"[CONTROL_BLOCKED] voice is "
                                                f"{bwhy} - refused mid-turn")
                                        ok_g, why_g = _guard.check(guard_key)
                                        if not ok_g:
                                            raise RuntimeError(
                                                f"[SPEND_BLOCKED] {why_g}")
                                        cos_sid = (_sid_box.get("sid")
                                                   or guard_key)
                                        t_ok, t_why = _turns.check(cos_sid)
                                        if t_ok:
                                            rb = _cbrain.opus_ask(
                                                user, session_id=cos_sid,
                                                stream=stream or None,
                                                timeout=_cbrain.OPUS_TIMEOUT_S,
                                                add_dirs=(
                                                    STREAM_ROOTS.get(stream)
                                                    or _ROOTS[:2]))
                                            if rb.get("ok") and str(
                                                    rb.get("text")
                                                    or "").strip():
                                                _turns.record(cos_sid)
                                                _brain_used.update(
                                                    brain="opus", why="")
                                                return {"ok": True,
                                                        "content": str(
                                                            rb["text"]).strip()}
                                            _brain_used.update(
                                                brain="grok",
                                                why=str(rb.get("error")
                                                        or "OPUS_EMPTY"))
                                        else:
                                            _brain_used.update(
                                                brain="grok", why=t_why)
                                    else:
                                        _brain_used.update(
                                            brain="grok",
                                            why="BRAIN_NOT_COMPOSED")
                                    # FALLBACK: the spend-gated Grok ask -
                                    # voice never hangs on a dead brain.
                                    return _grok_call(
                                        _PRE + "\n\nUser asked: " + user)
                                # tool results ran: the fast LOCAL lookup lane
                                # finishes as before - Grok phrases the found
                                # paths. No Opus call on this lane either.
                                ctx = _PRE + "\n\nUser asked: " + user
                                for tr in ran:
                                    ctx += ("\n\nSearch results:\n"
                                            + str(tr.get("content"))[:2500])
                                return _grok_call(ctx)
                            orchestrator = Orchestrator(
                                _model_call,
                                build_tools(_ROOTS, getattr(kernel, "itc", None)),
                                clock=kernel._clock)
                        except Exception:                             # noqa: BLE001
                            orchestrator = None
                    vm = VoiceMode(convo, Commander(kernel),
                                   getattr(kernel, "itc", None),
                                   asker=asker, orchestrator=orchestrator,
                                   clock=kernel._clock)
                    sid = sid_in
                    if not sid:
                        # the minted session CARRIES ITS STREAM as scope, so
                        # a reconnect knows what the conversation was about.
                        sid = convo.create_session(
                            title,
                            scope=([f"stream:{stream}"] if stream else None),
                            owner=principal)
                    else:
                        # NO_SESSION on a sid this principal does not own -
                        # existence is never leaked across principals.
                        convo.assert_owner(sid, principal)
                    # the brain needs the REAL sid (minted or given) so the
                    # claude session maps to the COSMOS session, not the
                    # guard key. The closure reads this box at call time.
                    _sid_box["sid"] = sid
                    out = vm.handle(
                        sid, transcript,
                        mode=str(d.get("mode") or "voice"),
                        confirm_id=d.get("confirm_id"))
                    # ---- WHICH BRAIN answered (opus|grok|local, or the ask
                    # verb's model name): on the reply for the client, and on
                    # the ledger for the audit. Best-effort by design.
                    brain = _brain_used["brain"]
                    if brain == "local":
                        for s_ in out.get("sources") or []:
                            if isinstance(s_, str) and s_.startswith("model:"):
                                brain = s_[6:] or "grok"
                                break
                    out["brain"] = brain
                    if _brain_used["why"]:
                        out["brain_note"] = _brain_used["why"]
                    if out.get("kind") in ("chat", "ask"):
                        try:
                            kernel.ledger.append("VOICE_BRAIN", {
                                "brain": brain,
                                "why": _brain_used["why"],
                                "session_id": out.get("session_id") or sid,
                                "kind": out.get("kind")})
                        except Exception:                     # noqa: BLE001
                            pass
                    # ---- SPEND ACCOUNTING for the breaker: usd:<x> sources
                    # are the measured spend; an unpriced or unlabeled model
                    # answer records the worst-case estimate (never free).
                    try:
                        usd = 0.0
                        for s_ in out.get("sources") or []:
                            if isinstance(s_, str) and s_.startswith("usd:"):
                                v = s_[4:]
                                usd += (CALL_EST_USD if v == "unpriced"
                                        else float(v))
                        # an OPUS answer rides the subscription, not the USD
                        # rails - its bound is the TURN CAP, so it is not
                        # charged the per-call estimate (charging it would
                        # conflate two budgets and starve the Grok fallback).
                        if usd <= 0.0 and out.get("ok") \
                                and out.get("kind") in ("chat", "ask") \
                                and _brain_used["brain"] != "opus":
                            usd = CALL_EST_USD
                        if usd > 0.0:
                            _guard.record(out.get("session_id") or sid, usd)
                    except Exception:                             # noqa: BLE001
                        pass
                    return self._send(200, out)
                except (VoiceError, ConvoError) as e:
                    return self._send(400, {"error": e.kind,
                                            "detail": str(e)[:300]})
                except Exception as e:                                # noqa: BLE001
                    return self._send(400, {"error": "BAD_REQUEST",
                                            "detail": str(e)[:200]})
            if self.path == "/api/v1/command":
                # the voice/frontend seam, served: text in, kernel action out
                from cosmos_command import Commander, CommandError
                body = self._read_body()
                if body is None:
                    return
                try:
                    d = json.loads(body.decode("utf-8"))
                    return self._send(200, Commander(kernel).handle(str(d["text"])))
                except CommandError as e:
                    return self._send(400, {"error": e.kind, "detail": str(e)[:300]})
                except Exception as e:                                # noqa: BLE001
                    return self._send(400, {"error": "BAD_REQUEST",
                                            "detail": str(e)[:200]})
            if self.path == "/api/v1/crucible":
                # Submit-only. Pool is the sole claim_next (pool-only claimant).
                # HTTP must not run_round: kernel.crucible_critics is process-local
                # and a detached worker cannot use it. A print stub is not a round;
                # if no critic dispatchers are composed, 501 is the honest answer.
                body = self._read_body()
                if body is None:
                    return
                try:
                    d = json.loads(body.decode("utf-8"))
                except Exception as e:                                # noqa: BLE001
                    return self._send(400, {"error": "BAD_REQUEST",
                                            "detail": str(e)[:200]})
                names = list(d.get("critics") or [])
                dispatchers = _crucible_dispatchers(kernel, names)
                if dispatchers is None:
                    kernel.ledger.append("CRUCIBLE_REFUSED",
                                         {"kind": "CRUCIBLE_NOT_RUNNABLE",
                                          "sources": d.get("sources", []),
                                          "critics": names})
                    return self._send(501, {
                        "error": "CRUCIBLE_NOT_RUNNABLE",
                        "detail": "no composed critic dispatchers for this round - "
                                  "refusing to queue a print stub (a queued print "
                                  "is not a crucible)"})
                from cosmos_paths import CosmosPathError
                try:
                    srcs = [kernel.paths.role("docs", s) for s in d["sources"]]
                except CosmosPathError as e:
                    kernel.ledger.append("CRUCIBLE_REFUSED",
                                         {"kind": e.kind, "sources": d.get("sources")})
                    return self._send(400, {"error": e.kind, "detail": str(e)[:300]})
                except Exception as e:                                # noqa: BLE001
                    return self._send(400, {"error": "BAD_REQUEST",
                                            "detail": str(e)[:200]})
                from pathlib import Path as _CruP
                if not srcs or any(
                        (not _CruP(s).is_file()) or _CruP(s).stat().st_size == 0
                        for s in srcs):
                    kernel.ledger.append("CRUCIBLE_REFUSED",
                                         {"kind": "EMPTY_SOURCE",
                                          "sources": d.get("sources")})
                    return self._send(400, {
                        "error": "EMPTY_SOURCE",
                        "detail": "a crucible with no sources judges air",
                    })
                cmd = "crucible:round " + json.dumps(
                    {"sources": list(d["sources"]),
                     "critics": sorted(dispatchers)}, sort_keys=True)
                try:
                    jid = kernel.sched.submit(cmd, d.get("priority", "high"),
                                              lane="crucible")
                except Exception as e:                                # noqa: BLE001
                    return self._send(400, {"error": "BAD_REQUEST",
                                            "detail": str(e)[:200]})
                kernel.ledger.append("CRUCIBLE_REQUESTED",
                                     {"job_id": jid, "sources": d["sources"],
                                      "critics": list(dispatchers)})
                return self._send(201, {
                    "job_id": jid,
                    "sources": [str(s) for s in srcs],
                    "outcome": "QUEUED",
                })
            from urllib.parse import urlparse as _wo_urlparse
            if _wo_urlparse(self.path).path == "/api/v1/research_call":
                from cosmos_research_call import (
                    ResearchCallError, run as research_call_run,
                )
                body = self._read_body()
                if body is None:
                    return
                try:
                    d = json.loads(body.decode("utf-8")) if body.strip() else {}
                except Exception as e:  # noqa: BLE001
                    return self._send(400, {"error": "BAD_REQUEST",
                                            "detail": str(e)[:200]})
                try:
                    rec = research_call_run(kernel.paths, d)
                except ResearchCallError as e:
                    return self._send(400, {"error": e.kind, "detail": str(e)[:300]})
                rec["tree_id"] = kernel.paths.sentinel.tree_id
                rec["measured_at"] = time.time()
                return self._send(200, rec)
            if _wo_urlparse(self.path).path == "/api/v1/studio":
                from cosmos_studio import StudioError, save_pack as studio_save
                body = self._read_body()
                if body is None:
                    return
                try:
                    d = json.loads(body.decode("utf-8")) if body.strip() else {}
                except Exception as e:                            # noqa: BLE001
                    return self._send(400, {"error": "BAD_REQUEST",
                                            "detail": str(e)[:200]})
                try:
                    rec = studio_save(kernel.paths, d)
                except StudioError as e:
                    return self._send(400, {"error": e.kind, "detail": str(e)[:300]})
                rec["tree_id"] = kernel.paths.sentinel.tree_id
                return self._send(200, rec)
            if _wo_urlparse(self.path).path == "/api/v1/usage":
                from cosmos_openrouter_rail import (
                    KEY_NAME, OpenRouterRail, OpenRouterRailError,
                    record_usage,
                )
                body = self._read_body()
                if body is None:
                    return
                try:
                    d = json.loads(body.decode("utf-8")) if body.strip() else {}
                except Exception as e:  # noqa: BLE001
                    return self._send(400, {"error": "BAD_REQUEST",
                                            "detail": str(e)[:200]})
                if not isinstance(d, dict):
                    return self._send(400, {"error": "BAD_REQUEST",
                                            "detail": "body must be a JSON object"})
                act = str(d.get("action") or "generation").strip().lower()
                if act != "generation":
                    return self._send(400, {"error": "BAD_INPUT",
                                            "detail": "action=generation {id}"})
                try:
                    rail = OpenRouterRail(kernel.paths.config(KEY_NAME))
                    rec = rail.fetch_generation(d.get("id") or d.get("generation_id") or "")
                    if rec.get("ok") and rec.get("usage_fold"):
                        record_usage(
                            kernel.paths, rec["usage_fold"],
                            model=str((rec["usage_fold"] or {}).get("model") or ""),
                            stage="audit", profile="openrouter",
                        )
                    rec["tree_id"] = kernel.paths.sentinel.tree_id
                    return self._send(200 if rec.get("ok") else 400, rec)
                except OpenRouterRailError as e:
                    return self._send(400, {"error": e.kind, "detail": str(e)[:300]})
            if _wo_urlparse(self.path).path == "/api/v1/porosity":
                from cosmos_porosity import (
                    PorosityError, coverage, hook_trial, record_pair, recommend,
                )
                body = self._read_body()
                if body is None:
                    return
                try:
                    d = json.loads(body.decode("utf-8")) if body.strip() else {}
                except Exception as e:  # noqa: BLE001
                    return self._send(400, {"error": "BAD_REQUEST",
                                            "detail": str(e)[:200]})
                if not isinstance(d, dict):
                    return self._send(400, {"error": "BAD_REQUEST",
                                            "detail": "body must be a JSON object"})
                try:
                    act = str(d.get("action") or "pair").strip().lower()
                    if act == "trial":
                        rec = hook_trial(
                            kernel.paths, d.get("runs") or [],
                            profile=d.get("profile") or "forge",
                            stage=d.get("stage") or "",
                            axis=d.get("axis") or "",
                            trial_id=d.get("trial_id") or "",
                            error_mag=d.get("error_mag"),
                            source=d.get("source") or "local",
                            authority=d.get("authority") or "",
                            action=d.get("audit_action") or "trial",
                        )
                    elif act == "recommend":
                        rec = {
                            "ok": True,
                            "ranked": recommend(
                                kernel.paths,
                                d.get("seated") or [],
                                d.get("candidates") or [],
                                axes=d.get("axes"),
                                costs=d.get("costs"),
                                profile=d.get("profile") or "forge",
                                mode=d.get("mode") or "complement",
                            ),
                        }
                    elif act == "coverage":
                        rec = coverage(
                            kernel.paths,
                            d.get("agents") or d.get("candidates") or [],
                            profile=d.get("profile") or "forge",
                            costs=d.get("costs"),
                            incumbent=d.get("incumbent") or "",
                        )
                    else:
                        rec = record_pair(
                            kernel.paths,
                            d.get("model_a") or "",
                            d.get("model_b") or "",
                            axis=d.get("axis") or "",
                            disagree=d.get("disagree", True),
                            error_mag=d.get("error_mag"),
                            profile=d.get("profile") or "forge",
                            stage=d.get("stage") or "",
                            trial_id=d.get("trial_id") or "",
                            tokens_a=d.get("tokens_a"),
                            tokens_b=d.get("tokens_b"),
                            who_erred=d.get("who_erred") or "",
                            source=d.get("source") or "local",
                            authority=d.get("authority") or "",
                            action=d.get("audit_action") or "ballot",
                            note=d.get("note") or "",
                        )
                    rec["tree_id"] = kernel.paths.sentinel.tree_id
                    return self._send(200, rec)
                except PorosityError as e:
                    return self._send(400, {"error": e.kind, "detail": str(e)[:300]})
            if _wo_urlparse(self.path).path == "/api/v1/profiles/bg":
                from cosmos_forge_bg import ForgeBgError, facilitate, start as forge_bg_start
                from cosmos_profiles import load_engine
                body = self._read_body()
                if body is None:
                    return
                try:
                    d = json.loads(body.decode("utf-8")) if body.strip() else {}
                except Exception as e:  # noqa: BLE001
                    return self._send(400, {"error": "BAD_REQUEST",
                                            "detail": str(e)[:200]})
                try:
                    stage = str(d.get("stage") or "")
                    if d.get("action") == "facilitate":
                        rec = facilitate(kernel.paths, stage,
                                         load_engine(kernel.paths, "forge"))
                    else:
                        rec = forge_bg_start(kernel.paths, stage, n=d.get("n"))
                    rec["tree_id"] = kernel.paths.sentinel.tree_id
                    return self._send(200, rec)
                except ForgeBgError as e:
                    return self._send(400, {"error": e.kind, "detail": str(e)[:300]})
            if _wo_urlparse(self.path).path == "/api/v1/profiles":
                from cosmos_profiles import ProfileError, save_engine as profiles_save
                body = self._read_body()
                if body is None:
                    return
                try:
                    d = json.loads(body.decode("utf-8")) if body.strip() else {}
                except Exception as e:                            # noqa: BLE001
                    return self._send(400, {"error": "BAD_REQUEST",
                                            "detail": str(e)[:200]})
                try:
                    rec = profiles_save(kernel.paths, d)
                except ProfileError as e:
                    return self._send(400, {"error": e.kind, "detail": str(e)[:300]})
                rec["tree_id"] = kernel.paths.sentinel.tree_id
                return self._send(200, rec)
            if _wo_urlparse(self.path).path == "/api/v1/orc":
                from cosmos_orc_boot import OrcBootError, boot as orc_boot
                body = self._read_body()
                if body is None:
                    return
                try:
                    d = json.loads(body.decode("utf-8")) if body.strip() else {}
                except Exception as e:  # noqa: BLE001
                    return self._send(400, {"error": "BAD_REQUEST",
                                            "detail": str(e)[:200]})
                if not isinstance(d, dict):
                    return self._send(400, {"error": "BAD_REQUEST",
                                            "detail": "body must be a JSON object"})
                try:
                    rec = orc_boot(kernel, d.get("stream") or "Cm")
                except OrcBootError as e:
                    return self._send(400, {"error": e.kind, "detail": str(e)[:300]})
                rec["tree_id"] = kernel.paths.sentinel.tree_id
                return self._send(200, rec)
            if _wo_urlparse(self.path).path == "/api/v1/surfaces":
                from cosmos_surfaces_kit import SurfacesKitError, save_surface
                body = self._read_body()
                if body is None:
                    return
                try:
                    d = json.loads(body.decode("utf-8")) if body.strip() else {}
                except Exception as e:  # noqa: BLE001
                    return self._send(400, {"error": "BAD_REQUEST",
                                            "detail": str(e)[:200]})
                try:
                    rec = save_surface(kernel.paths, d, kernel=kernel)
                except SurfacesKitError as e:
                    return self._send(400, {"error": e.kind, "detail": str(e)[:300]})
                rec["tree_id"] = kernel.paths.sentinel.tree_id
                rec["measured_at"] = time.time()
                return self._send(200, rec)
            if _wo_urlparse(self.path).path == "/api/v1/backup":
                from cosmos_backup_fold import BackupFoldError, run_action as backup_run
                body = self._read_body()
                if body is None:
                    return
                try:
                    d = json.loads(body.decode("utf-8")) if body.strip() else {}
                except Exception as e:  # noqa: BLE001
                    return self._send(400, {"error": "BAD_REQUEST",
                                            "detail": str(e)[:200]})
                if not isinstance(d, dict):
                    return self._send(400, {"error": "BAD_REQUEST",
                                            "detail": "body must be a JSON object"})
                try:
                    rec = backup_run(kernel.paths, d, kernel=kernel)
                except BackupFoldError as e:
                    return self._send(400, {"error": e.kind, "detail": str(e)[:300]})
                rec["tree_id"] = kernel.paths.sentinel.tree_id
                rec["measured_at"] = time.time()
                return self._send(200, rec)
            if _wo_urlparse(self.path).path == "/api/v1/session_tools":
                from cosmos_session_tools_kit import (
                    SessionToolsKitError, run as session_tools_run,
                )
                body = self._read_body()
                if body is None:
                    return
                try:
                    d = json.loads(body.decode("utf-8")) if body.strip() else {}
                except Exception as e:  # noqa: BLE001
                    return self._send(400, {"error": "BAD_REQUEST",
                                            "detail": str(e)[:200]})
                try:
                    rec = session_tools_run(d, paths=kernel.paths)
                except SessionToolsKitError as e:
                    return self._send(400, {"error": e.kind, "detail": str(e)[:300]})
                rec["tree_id"] = kernel.paths.sentinel.tree_id
                rec["measured_at"] = time.time()
                return self._send(200, rec)
            if _wo_urlparse(self.path).path == "/api/v1/voice_loop":
                from cosmos_voice_loop import VoiceLoopError, save_sop as voice_sop_save
                body = self._read_body()
                if body is None:
                    return
                try:
                    d = json.loads(body.decode("utf-8")) if body.strip() else {}
                except Exception as e:  # noqa: BLE001
                    return self._send(400, {"error": "BAD_REQUEST",
                                            "detail": str(e)[:200]})
                try:
                    rec = voice_sop_save(kernel.paths, d)
                except VoiceLoopError as e:
                    return self._send(400, {"error": e.kind, "detail": str(e)[:300]})
                rec["tree_id"] = kernel.paths.sentinel.tree_id
                rec["measured_at"] = time.time()
                return self._send(200, rec)
            if _wo_urlparse(self.path).path == "/api/v1/session_kit":
                from cosmos_session_kit import SessionKitError, save_kit as session_kit_save
                body = self._read_body()
                if body is None:
                    return
                try:
                    d = json.loads(body.decode("utf-8")) if body.strip() else {}
                except Exception as e:                            # noqa: BLE001
                    return self._send(400, {"error": "BAD_REQUEST",
                                            "detail": str(e)[:200]})
                try:
                    rec = session_kit_save(kernel.paths, d)
                except SessionKitError as e:
                    return self._send(400, {"error": e.kind, "detail": str(e)[:300]})
                rec["tree_id"] = kernel.paths.sentinel.tree_id
                return self._send(200, rec)
            if _wo_urlparse(self.path).path == "/api/v1/work_orders/picked":
                body = self._read_body()
                if body is None:
                    return
                try:
                    d = json.loads(body.decode("utf-8")) if body.strip() else {}
                except Exception as e:                            # noqa: BLE001
                    return self._send(400, {"error": "BAD_REQUEST",
                                            "detail": str(e)[:200]})
                code, rec = record_work_order_picked(kernel, d)
                return self._send(code, rec)
            if self.path == "/api/v1/jobs":
                body = self._read_body()
                if body is None:
                    return
                try:
                    d = json.loads(body.decode("utf-8"))
                    jid = kernel.sched.submit(d["command"], d.get("priority", "normal"))
                except Exception as e:                                # noqa: BLE001
                    return self._send(400, {"error": "BAD_REQUEST", "detail": str(e)[:200]})
                return self._send(201, {"job_id": jid})
            if self.path == "/api/v1/makers":
                from cosmos_makers import MakerError
                body = self._read_body()
                if body is None:
                    return
                try:
                    d = json.loads(body.decode("utf-8"))
                    mm = getattr(kernel, "makers", None)
                    if mm is None:
                        return self._send(503, {"error": "MAKERS_NOT_COMPOSED",
                                                "detail": "kernel has no maker map - this "
                                                          "is a composition fault"})
                    rec = mm.add(d)
                    return self._send(201, {"maker": rec})
                except MakerError as e:
                    return self._send(400, {"error": e.kind, "detail": str(e)[:300]})
                except Exception as e:                                # noqa: BLE001
                    return self._send(400, {"error": "BAD_REQUEST",
                                            "detail": str(e)[:200]})
            from urllib.parse import urlparse as _cvm_urlparse
            _cvm_post = _cvm_urlparse(self.path).path
            if _cvm_post in ("/api/v1/cvm/snapshot", "/api/v1/cvm/push"):
                # CVM additive. Snapshot lands phone.json. Push composes that
                # helper then stamps pull.json audio_owner=desktop. Bearer
                # already checked. Never ledger. One parse, one error map.
                body = self._read_body()
                if body is None:
                    return
                try:
                    d = json.loads(body.decode("utf-8")) if body.strip() else {}
                except Exception as e:                            # noqa: BLE001
                    return self._send(400, {"error": "BAD_REQUEST",
                                            "detail": str(e)[:200]})
                if not isinstance(d, dict):
                    return self._send(400, {"error": "BAD_SNAPSHOT",
                                            "detail": "body must be a JSON object"})
                try:
                    if _cvm_post == "/api/v1/cvm/push":
                        from cosmos_cvm_push import cvm_store_push
                        return self._send(200, cvm_store_push(kernel, d))
                    return self._send(200, _cvm_store_snapshot(kernel, d))
                except CvmError as e:
                    code = 500 if e.kind in ("UNPARSEABLE", "UNREADABLE") else 400
                    return self._send(code, {"error": e.kind,
                                            "detail": str(e)[:300]})
                except Exception as e:                            # noqa: BLE001
                    return self._send(400, {"error": "BAD_REQUEST",
                                            "detail": str(e)[:200]})
            _mr = _cvm_urlparse(self.path).path
            if _mr in ("/api/v1/model_rater/refresh",
                       "/api/v1/model_rater/seat",
                       "/api/v1/model_rater/cap",
                       "/api/v1/model_rater/porosity",
                       "/api/v1/model_rater/policy",
                       "/api/v1/model_rater/estimate",
                       "/api/v1/model_rater/job_estimate"):
                from cosmos_model_rater import (
                    ModelRaterError, add_adversary, assign_seat, estimate,
                    load_catalog, load_job_estimate, record_porosity,
                    remove_adversary, reset_job_estimate, save_job_estimate,
                    set_model_cap, set_policy, snapshot, refresh as mr_refresh,
                )
                body = self._read_body()
                if body is None:
                    return
                try:
                    d = json.loads(body.decode("utf-8")) if body.strip() else {}
                except Exception as e:  # noqa: BLE001
                    return self._send(400, {"error": "BAD_REQUEST",
                                            "detail": str(e)[:200]})
                if not isinstance(d, dict):
                    return self._send(400, {"error": "BAD_REQUEST",
                                            "detail": "body must be a JSON object"})
                try:
                    if _mr.endswith("/refresh"):
                        rec = mr_refresh(kernel.paths)
                        return self._send(200, {
                            "ok": True, "n": rec.get("n"),
                            "fetched_at": rec.get("fetched_at"),
                            "http": rec.get("http"),
                        })
                    if _mr.endswith("/seat"):
                        act = str(d.get("action") or "assign").strip().lower()
                        if act == "add":
                            rec = add_adversary(kernel.paths,
                                                d.get("model") or "",
                                                d.get("label") or "",
                                                d.get("via") or "")
                            return self._send(200, rec)
                        if act == "remove":
                            rec = remove_adversary(kernel.paths,
                                                   d.get("seat") or "")
                            return self._send(200, rec)
                        rec = assign_seat(kernel.paths, d.get("profile"),
                                          d.get("seat"),
                                          model=d["model"] if "model" in d else None,
                                          via=d.get("via") or "",
                                          cap_usd=d.get("cap_usd"),
                                          model_2=d.get("model_2"),
                                          model_3=d.get("model_3"),
                                          via_2=d.get("via_2"),
                                          via_3=d.get("via_3"),
                                          effort=d.get("effort"))
                        return self._send(200, rec)
                    if _mr.endswith("/policy"):
                        rec = set_policy(
                            kernel.paths,
                            favored_models=d.get("favored_models"),
                            favored_families=d.get("favored_families"),
                            banned_models=d.get("banned_models"),
                            banned_families=d.get("banned_families"),
                        )
                        return self._send(200, rec)
                    if _mr.endswith("/cap"):
                        rec = set_model_cap(kernel.paths, d.get("model") or "",
                                            d.get("cap_usd"))
                        return self._send(200, rec)
                    if _mr.endswith("/porosity"):
                        rec = record_porosity(
                            kernel.paths,
                            d.get("model") or "",
                            d.get("loc_per_100"),
                            d.get("severity"),
                            source=d.get("source") or "local",
                            loc_n=d.get("loc_n"),
                            note=d.get("note") or "",
                            agent_id=d.get("agent_id") or "",
                            action=d.get("action") or "",
                            authority=d.get("authority") or "",
                        )
                        return self._send(200, rec)
                    if _mr.endswith("/job_estimate"):
                        if d.get("reset"):
                            rec = reset_job_estimate(kernel.paths)
                        else:
                            rec = save_job_estimate(
                                kernel.paths,
                                d.get("tokens_in"), d.get("tokens_out"),
                                override=d.get("override", True))
                        snap = snapshot(kernel.paths, limit=1)
                        rec["job_costs"] = snap.get("job_costs")
                        rec["seats"] = snap.get("seats")
                        return self._send(200, rec)
                    cat = load_catalog(kernel.paths)
                    rec = estimate(cat, d.get("model"),
                                   d.get("tokens_in") or 0,
                                   d.get("tokens_out") or 0)
                    return self._send(200, rec)
                except ModelRaterError as e:
                    code = 401 if e.kind in ("NO_KEY", "AUTH_REQUIRED") else 400
                    if e.kind == "UNREACHABLE":
                        code = 503
                    return self._send(code, {"error": e.kind,
                                            "detail": str(e)[:300]})
            if _cvm_urlparse(self.path).path == "/api/v1/cred":
                from cosmos_cred_kit import (
                    CredError, add_custom, delete_secret, grab_secret,
                    set_secret, snapshot as cred_snapshot,
                )
                body = self._read_body()
                if body is None:
                    return
                try:
                    d = json.loads(body.decode("utf-8")) if body.strip() else {}
                except Exception as e:  # noqa: BLE001
                    return self._send(400, {"error": "BAD_REQUEST",
                                            "detail": str(e)[:200]})
                if not isinstance(d, dict):
                    return self._send(400, {"error": "BAD_REQUEST",
                                            "detail": "body must be a JSON object"})
                try:
                    act = str(d.get("action") or "").strip().lower()
                    sid = d.get("id") or ""
                    if act == "set":
                        rec = set_secret(kernel.paths, sid, d.get("secret") or "")
                    elif act == "delete":
                        rec = delete_secret(kernel.paths, sid)
                    elif act == "grab":
                        rec = grab_secret(kernel.paths, sid)
                    elif act == "custom":
                        rec = add_custom(kernel.paths, source_id=sid,
                                         label=d.get("label") or sid,
                                         kind=d.get("kind") or "API")
                    else:
                        rec = cred_snapshot(kernel.paths)
                    rec["ok"] = True
                    rec["action"] = act or "fold"
                    return self._send(200, rec)
                except CredError as e:
                    return self._send(400, {"error": e.kind,
                                            "detail": str(e)[:300]})
            return self._send(404, {"error": "NOT_FOUND", "path": self.path})

        def log_message(self, *a):                                    # quiet server
            pass

    return Handler


def _san_entries(host: str) -> tuple[list[str], list]:
    """(dns_names, ip_addresses) the cert must cover so a LAN client can VERIFY,
    not just encrypt. Always: cosmos.local, localhost, this machine's hostname,
    127.0.0.1, ::1. Plus the actual bind host (as IP or DNS), and on a wildcard
    bind (0.0.0.0 / ::) the machine's resolvable local IPs - a cert whose SAN
    names none of the addresses it is served on cannot be verified by anyone."""
    import ipaddress
    import socket
    dns = {"cosmos.local", "localhost"}
    ips = {ipaddress.ip_address("127.0.0.1"), ipaddress.ip_address("::1")}
    try:
        hn = socket.gethostname()
        if hn:
            dns.add(hn)
    except OSError:
        hn = ""
    h = (host or "").strip()
    wildcard = h in ("", "0.0.0.0", "::")
    if h and not wildcard:
        try:
            ips.add(ipaddress.ip_address(h))
        except ValueError:
            dns.add(h)
    if wildcard and hn:
        try:
            for info in socket.getaddrinfo(hn, None):
                try:
                    ips.add(ipaddress.ip_address(info[4][0]))
                except ValueError:
                    pass
        except OSError:
            pass
    return sorted(dns), sorted(ips, key=str)


def _ensure_cert(kernel, host: str = "127.0.0.1") -> tuple[str, str] | None:
    """Self-signed cert for HTTPS, generated into config/. Returns (cert, key)
    paths, or None if the crypto lib is unavailable (then the caller stays HTTP and
    SAYS SO - never a silent downgrade). The SAN covers the ACTUAL bind host/IP
    (plus the documented names) - a cert naming only cosmos.local/localhost cannot
    be verified by a LAN client dialing an IP, which reduces 'HTTPS' to unverified
    encryption. An existing cert that already covers the needed names is reused;
    one that does not is regenerated in place. A self-signed cert on a LAN is real
    transport encryption; a public CA cert is a later cutover step."""
    cfg = kernel.paths.config
    cert, key = str(cfg("cosmos_cert.pem")), str(cfg("cosmos_key.pem"))
    from pathlib import Path as _P
    try:
        import datetime as _dt
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import rsa
    except Exception:                                                # noqa: BLE001
        # No crypto lib: a pre-provisioned pair still serves; nothing can be minted.
        if _P(cert).exists() and _P(key).exists():
            return cert, key
        return None
    dns_names, ip_addrs = _san_entries(host)
    if _P(cert).exists() and _P(key).exists():
        try:
            existing = x509.load_pem_x509_certificate(_P(cert).read_bytes())
            san = existing.extensions.get_extension_for_class(
                x509.SubjectAlternativeName).value
            have_dns = set(san.get_values_for_type(x509.DNSName))
            have_ip = {str(i) for i in san.get_values_for_type(x509.IPAddress)}
            if (set(dns_names) <= have_dns
                    and {str(i) for i in ip_addrs} <= have_ip):
                return cert, key
            # else: falls through and regenerates with the full SAN set
        except Exception:                                            # noqa: BLE001
            pass                     # unreadable or SAN-less cert: regenerate
    try:
        k = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "cosmos.local")])
        sans = ([x509.DNSName(d) for d in dns_names]
                + [x509.IPAddress(i) for i in ip_addrs])
        cert_obj = (x509.CertificateBuilder()
                    .subject_name(name).issuer_name(name).public_key(k.public_key())
                    .serial_number(x509.random_serial_number())
                    .not_valid_before(_dt.datetime.utcnow())
                    .not_valid_after(_dt.datetime.utcnow() + _dt.timedelta(days=825))
                    .add_extension(x509.SubjectAlternativeName(sans), critical=False)
                    .sign(k, hashes.SHA256()))
        _write_private(key, k.private_bytes(
            serialization.Encoding.PEM, serialization.PrivateFormat.TraditionalOpenSSL,
            serialization.NoEncryption()))
        _P(cert).write_bytes(cert_obj.public_bytes(serialization.Encoding.PEM))
        return cert, key
    except Exception:                                                # noqa: BLE001
        return None


class Service:
    """Serve a kernel. serve_background() for tests; serve_forever() for the real thing.

    REMOTE ACCESS + HTTPS (Keith, 2026-08-23): host="0.0.0.0" binds the LAN; the bearer
    token is access control. tls=True wraps the socket with a self-signed cert generated
    into config/ (real transport encryption on the LAN; SAN covers the bind host/IP so
    clients can verify).

    TWO refusals guard a non-loopback bind, and they are NOT the same guard:

    1. REMOTE_OPEN_ACCESS - a remote bind REFUSES open_access/--no-auth. There is no
       flag past this one. It is checked FIRST, before the socket is bound and before
       any token is touched. `remote + open_access` does not mean "no bearer left to
       capture", it means EVERY host that can route to the port is an authenticated
       operator of Core: it can drain the whole ledger (GET /api/v1/events pages the
       chain with `since_seq` - conversation transcripts included), submit jobs, add
       makers, drive the voice/command rails that SPEND MONEY, and flip the control
       channel. "The tailnet/LAN is the access control" is only true of a tailnet;
       0.0.0.0 is every interface, including the house wifi and any VM host-only net.
       Loopback + open_access is untouched - that is the local trial and it is fine.
       MEASURED 2026-08-31: the trial Core on :8791 served all 2,349 ledger records and
       accepted a state-mutating POST from a LAN address with no credentials.
       See docs/CORE_SERVE_SUPERVISOR.md.
    2. REMOTE_CLEARTEXT - a remote bind refuses to start unless TLS is actually up; a
       bearer token over LAN HTTP is captured and replayed by any observer.
       THE ONE OPT-OUT: insecure_http=True (CLI --insecure-http), Keith's explicit
       reversible trial flag. NOTE its original rationale ("paired with --no-auth so
       there is no bearer to capture") is dead - guard 1 refuses that pairing on a
       remote bind, so --insecure-http remotely now means a REAL bearer crossing the
       LAN in the clear. It is a knowing trade of confidentiality-in-transit, never
       of authentication.

    The guards read `if remote and open_access` and
    `if remote and self.scheme != "https" and not insecure_http`; these sentences
    exist so the prose can never again promise an absolute the code does not enforce.

    On loopback, if the crypto lib is absent the service stays HTTP and
    RECORDS the downgrade in .scheme - never a silent claim of encryption. A public-CA
    cert for internet exposure is a later cutover step."""

    def __init__(self, kernel: Kernel, host: str = "127.0.0.1", port: int = 0,
                 tls: bool = False, cert_file: str | None = None,
                 key_file: str | None = None, open_access: bool = False,
                 insecure_http: bool = False):
        remote = _is_remote_bind(host)
        if remote and open_access:
            # FAIL CLOSED, FIRST: before the socket binds and before any token is
            # read. No flag opens this door - not --insecure-http, not --tls. An
            # unauthenticated Core on a non-loopback interface is not a "trial",
            # it is an open operator console for the whole subnet.
            raise ServiceError(
                "REMOTE_OPEN_ACCESS",
                f"refusing to serve a non-loopback bind ({host!r}) with bearer auth "
                f"disabled - every host that can reach this port would be a full "
                f"operator of Core (drain the ledger, submit jobs, spend money, flip "
                f"the control channel); bind loopback for the no-auth trial, or drop "
                f"open_access/--no-auth and serve the bearer over TLS")
        self.open_access = open_access
        if open_access:
            # bearer auth disabled (trial). No token minted/loaded. Reachable only
            # from this machine - the remote+open_access refusal above already ran.
            self.token = ""
        else:
            tok_file = kernel.paths.config("api_token.txt")
            self.token = _load_api_token(tok_file, remote=remote)
        self.httpd = ThreadingHTTPServer((host, port),
                                         make_handler(kernel, self.token, open_access))
        self.scheme = "http"
        self.cert_source = None
        if cert_file or key_file:
            # A provided pair IS the TLS instruction: use it, do not self-sign.
            from pathlib import Path as _P
            problems = []
            if not (cert_file and key_file):
                problems.append("cert_file and key_file must BOTH be given - half a "
                                "pair cannot serve TLS")
            else:
                for label, pth in (("cert_file", cert_file), ("key_file", key_file)):
                    if not _P(pth).is_file():
                        problems.append(f"{label} does not exist: {pth}")
            if problems:
                self.httpd.server_close()
                raise ServiceError("CERT_NOT_FOUND", "; ".join(problems))
            import ssl
            ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            try:
                ctx.load_cert_chain(certfile=cert_file, keyfile=key_file)
            except Exception:
                self.httpd.server_close()
                raise
            self.httpd.socket = ctx.wrap_socket(self.httpd.socket, server_side=True)
            self.scheme = "https"
            self.cert_source = "provided"
        elif tls:
            pair = _ensure_cert(kernel, host)
            if pair:
                import ssl
                ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                ctx.load_cert_chain(certfile=pair[0], keyfile=pair[1])
                self.httpd.socket = ctx.wrap_socket(self.httpd.socket, server_side=True)
                self.scheme = "https"
                self.cert_source = "self-signed"
            # else: stayed http; self.scheme records the honest truth
        if remote and self.scheme != "https" and not insecure_http:
            # A non-loopback bind over cleartext HTTP serves the bearer token to
            # any LAN observer on every request - capture and replay. The honest
            # HTTP fallback is for LOOPBACK only; remotely it is an open door,
            # so the service refuses to start rather than start downgraded.
            # insecure_http (TRIAL, reversible): Keith's explicit opt-in to serve
            # plain HTTP on a private LAN, with a Chrome insecure-origin flag, to
            # test the mic without a cert. It can no longer be paired with --no-auth
            # on a remote bind (REMOTE_OPEN_ACCESS above), so a REAL bearer now
            # crosses the LAN in the clear: it trades confidentiality, not auth.
            self.httpd.server_close()
            raise ServiceError(
                "REMOTE_CLEARTEXT",
                f"refusing to serve a non-loopback bind ({host!r}) without TLS - "
                f"the bearer token would cross the network in the clear; pass "
                f"tls=True (and have the 'cryptography' lib installed), or bind "
                f"loopback")
        self.port = self.httpd.server_address[1]

    def serve_background(self) -> threading.Thread:
        t = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        t.start()
        return t

    def shutdown(self):
        self.httpd.shutdown()