#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_gdx_drive_rail - satellite API rail `gdx-drive` (PyDrive2 / Drive).

GDX Drive com rail. Vendor: Google Drive via PyDrive2 (Drive API v2 about.get).
OAuth refresh tokens minted under a Google Cloud **Testing** consent screen
expire every 7 days; `invalid_grant` after that lapse is AUTH_REQUIRED, never
GREEN. Keith remints; this rail does not invent a token.

kind=API. Route is core->drive so Registry.route cannot capture models/code/
search/papers. Prove-shaped identity is the vendor-emitted
`about.user.emailAddress`. A missing field yields an empty model and the
proof fails, fail-closed.

Does NOT edit kernel/ledger/sched/service. attach_to_kernel refuses the
authority ledger unless boot_compose=True. Compose attaches the adapter;
boot does not invoke Drive.

MAP (cDeck / farm):
  * KDash `#panel-rails` / cDeck System rails pane paints GET `/api/v1/rails`
    (esc() on link_id / rail_type / route). After prove, `gdx-drive` is a
    matrix row. Unproven = absent (claim != capability).
  * Surfaces extra-pane paints the GDX *storage surface* via GET `/surfaces`
    (canon name), not this link_id.
  * Model Rater has no farm seat with via=gdx-drive (not a model rail).
  * Farm consumers: SGH Voice loop Drive/CCr return path; bucket `--out GDX`.

    py -3.14 cosmos\\cosmos_gdx_drive_rail.py --selftest
    py -3.14 cosmos\\cosmos_gdx_drive_rail.py --root V:\\A\\Ai\\COSMOS\\live --probe
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

SCHEMA = "cosmos-gdx-drive-rail/1"
WORKER = "cosmos-gdx-drive-rail"
LINK_ID = "gdx-drive"
SRC = "core"
DST = "drive"
SPEC_NAME = "gdx_drive_rail.json"
CREDENTIALS_NAME = "gdx_drive_credentials.json"
CLIENT_SECRETS_NAME = "gdx_drive_client_secrets.json"
PROBE_NAME = "gdx_drive_rail_probe.json"
KEY_NAME = CREDENTIALS_NAME  # hands fact: token file exists (never a read)
CONSENT_MODE = "Testing"
REFRESH_TTL_S = 7 * 24 * 3600
VENDOR = "Google Drive"
VENDOR_LIB = "PyDrive2"
ABOUT_FIELDS = "user,quotaBytesTotal,quotaBytesUsed"
MODEL_SOURCE = "Drive about.user.emailAddress"
UA = "COSMOS-gdx-drive-rail/1 (gdx-drive; keithbbf-gif/cosmos)"
VENDOR_DOCS = "https://developers.google.com/drive/api/v2/reference/about/get"
VENDOR_OAUTH = (
    "https://developers.google.com/identity/protocols/oauth2"
    "#expiration"
)
# Testing consent: refresh tokens expire 7 days. Production consent is Keith.
CONSENT_NOTE = (
    "Google Cloud OAuth Testing consent: refresh tokens expire every 7 days. "
    "invalid_grant after lapse is AUTH_REQUIRED, never GREEN."
)


class GdxDriveRailError(RuntimeError):
    """kind in {NO_KEY, BAD_SPEC, BAD_ROOT, UNREACHABLE, AUTH_REQUIRED, BROKE, REFUSED}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


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
        "credentials_name": CREDENTIALS_NAME,
        "client_secrets_name": CLIENT_SECRETS_NAME,
        "consent_mode": CONSENT_MODE,
        "refresh_ttl_s": REFRESH_TTL_S,
        "timeout_s": 45,
        "vendor": VENDOR,
        "vendor_lib": VENDOR_LIB,
        "vendor_docs": VENDOR_DOCS,
        "vendor_oauth": VENDOR_OAUTH,
        "note": (
            "PyDrive2 Drive about.get. core->drive so Registry.route cannot "
            "capture models/code. Bind about.user.emailAddress. " + CONSENT_NOTE
        ),
    }


def _pin_origin(spec: dict) -> dict:
    kn = str(spec.get("credentials_name") or CREDENTIALS_NAME)
    if kn != CREDENTIALS_NAME:
        raise GdxDriveRailError(
            "BAD_SPEC", f"credentials_name {kn!r} != {CREDENTIALS_NAME!r}")
    spec["credentials_name"] = CREDENTIALS_NAME
    cs = str(spec.get("client_secrets_name") or CLIENT_SECRETS_NAME)
    if cs != CLIENT_SECRETS_NAME:
        raise GdxDriveRailError(
            "BAD_SPEC",
            f"client_secrets_name {cs!r} != {CLIENT_SECRETS_NAME!r}")
    spec["client_secrets_name"] = CLIENT_SECRETS_NAME
    spec["src"] = str(spec.get("src") or SRC) or SRC
    spec["dst"] = str(spec.get("dst") or DST) or DST
    if spec["dst"] in ("models", "code", "search", "papers", "read"):
        spec["route_note"] = (
            f"coerced dst={spec['dst']!r} to {DST} (drive; not a model rail)")
        spec["dst"] = DST
    spec["rail_type"] = "API"
    spec["link_id"] = str(spec.get("link_id") or LINK_ID) or LINK_ID
    spec["metered_usd"] = float(spec.get("metered_usd") or 0.0)
    spec["budget_usd"] = float(spec.get("budget_usd") or 0.0)
    spec["policy_rank"] = int(spec.get("policy_rank") or 0)
    spec["timeout_s"] = int(spec.get("timeout_s") or 45)
    spec["consent_mode"] = CONSENT_MODE
    spec["refresh_ttl_s"] = REFRESH_TTL_S
    spec["vendor"] = VENDOR
    spec["vendor_lib"] = VENDOR_LIB
    spec["vendor_docs"] = VENDOR_DOCS
    spec["vendor_oauth"] = VENDOR_OAUTH
    spec["schema"] = SCHEMA
    return spec


def merge_spec(overlay) -> dict:
    spec = default_spec()
    if overlay is None:
        return _pin_origin(spec)
    if not isinstance(overlay, dict):
        raise GdxDriveRailError(
            "BAD_SPEC", f"spec overlay is {type(overlay).__name__}")
    for k, v in overlay.items():
        spec[k] = v
    if spec.get("schema") != SCHEMA:
        raise GdxDriveRailError(
            "BAD_SPEC", f"spec schema {spec.get('schema')!r} != {SCHEMA}")
    if spec.get("rail_type") not in (None, "API"):
        raise GdxDriveRailError(
            "BAD_SPEC",
            f"gdx-drive rail_type must be API, got {spec.get('rail_type')!r}")
    return _pin_origin(spec)


def load_spec(path: Path | None) -> dict:
    if path is None or not Path(path).exists():
        return default_spec()
    try:
        raw = Path(path).read_text(encoding="utf-8")
    except OSError as e:
        raise GdxDriveRailError("BAD_SPEC", f"unreadable spec {path}: {e}") from e
    try:
        overlay = json.loads(raw)
    except ValueError as e:
        raise GdxDriveRailError(
            "BAD_SPEC", f"unparseable spec {path}: {e}") from e
    return merge_spec(overlay)


def write_spec(path: Path, spec: dict | None = None) -> dict:
    body = merge_spec(spec)
    for secret in ("refresh_token", "access_token", "client_secret",
                   "client_id", "token", "credentials"):
        body.pop(secret, None)
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
    return paths.config(CREDENTIALS_NAME)


def client_secrets_path_for(paths) -> Path:
    return paths.config(CLIENT_SECRETS_NAME)


def probe_path_for(paths) -> Path:
    return paths.config(PROBE_NAME)


def _email_of(about) -> str:
    if not isinstance(about, dict):
        return ""
    user = about.get("user")
    if isinstance(user, dict):
        return str(user.get("emailAddress") or "").strip()
    return str(about.get("emailAddress") or "").strip()


def _display_of(about) -> str:
    if not isinstance(about, dict):
        return ""
    user = about.get("user")
    if isinstance(user, dict):
        return str(user.get("displayName") or "").strip()
    return ""


def _permission_of(about) -> str:
    if not isinstance(about, dict):
        return ""
    user = about.get("user")
    if isinstance(user, dict):
        return str(user.get("permissionId") or "").strip()
    return ""


def _kind_of_oauth(err: str) -> str:
    up = (err or "").upper()
    if "INVALID_GRANT" in up or "TOKEN" in up and "REVOKED" in up:
        return "AUTH_REQUIRED"
    if "NO_KEY" in up or "CREDENTIAL" in up and "ABSENT" in up:
        return "NO_KEY"
    if "IMPORT" in up or "PYDRIVE" in up and "ABSENT" in up:
        return "UNREACHABLE"
    if "401" in up or "403" in up or "AUTH" in up:
        return "AUTH_REQUIRED"
    return "BROKE"


class GdxDriveRail:
    """Dispatcher adapter. kind=API. probe=Drive about.get. Never at boot."""

    kind = "API"

    def __init__(self, credentials_path: Path | str | None, spec: dict | None = None,
                 about_fn=None, client_secrets_path: Path | str | None = None):
        self.spec = merge_spec(spec)
        self.credentials_path = (
            Path(credentials_path) if credentials_path is not None else None)
        self.client_secrets_path = (
            Path(client_secrets_path) if client_secrets_path is not None else None)
        self.metered_usd = float(self.spec.get("metered_usd") or 0.0)
        self._about_fn = about_fn
        self.link_id = self.spec["link_id"]
        self._last = None

    def last_identity(self) -> dict | None:
        return self._last

    def _live_about(self) -> dict:
        cred = self.credentials_path
        if cred is None or not Path(cred).exists():
            raise GdxDriveRailError(
                "NO_KEY",
                f"GDX Drive OAuth token missing at {cred} "
                f"(never hard-code; Testing consent refresh every 7 days)")
        secrets = self.client_secrets_path
        if secrets is None or not Path(secrets).exists():
            raise GdxDriveRailError(
                "NO_KEY",
                f"GDX Drive OAuth client secrets missing at {secrets} "
                f"(PyDrive2 cannot refresh without the client)")
        try:
            from pydrive2.auth import GoogleAuth  # type: ignore
            from pydrive2.drive import GoogleDrive  # type: ignore
        except ImportError as e:
            raise GdxDriveRailError(
                "UNREACHABLE", f"PyDrive2 ABSENT: {e}") from e
        try:
            settings = {
                "client_config_file": str(secrets),
                "save_credentials": True,
                "save_credentials_backend": "file",
                "save_credentials_file": str(cred),
                "get_refresh_token": True,
                "oauth_scope": ["https://www.googleapis.com/auth/drive.readonly"],
            }
            gauth = GoogleAuth(settings=settings)
            gauth.LoadCredentialsFile(str(cred))
            if getattr(gauth, "access_token_expired", False):
                gauth.Refresh()
            if not getattr(gauth, "credentials", None):
                raise GdxDriveRailError(
                    "AUTH_REQUIRED",
                    "PyDrive2 loaded no credentials (Testing consent lapse?)")
            gauth.Authorize()
            drive = GoogleDrive(gauth)
            about = drive.GetAbout()
        except GdxDriveRailError:
            raise
        except Exception as e:  # noqa: BLE001
            kind = _kind_of_oauth(f"{type(e).__name__}: {e}")
            extra = (" " + CONSENT_NOTE) if kind == "AUTH_REQUIRED" else ""
            raise GdxDriveRailError(
                kind, f"{type(e).__name__}: {e}{extra}") from e
        if not isinstance(about, dict):
            raise GdxDriveRailError(
                "BROKE", f"GetAbout returned {type(about).__name__}, not a dict")
        return about

    def _about(self) -> dict:
        if self._about_fn is not None:
            about = self._about_fn()
            if isinstance(about, GdxDriveRailError):
                raise about
            if not isinstance(about, dict):
                raise GdxDriveRailError(
                    "BROKE", f"about_fn returned {type(about).__name__}")
            return about
        return self._live_about()

    def probe(self):
        try:
            about = self._about()
        except GdxDriveRailError as e:
            rec = {
                "ok": False, "kind": e.kind, "detail": str(e),
                "email": "", "model": "", "http": None,
            }
            self._last = rec
            return False, rec["detail"]
        email = _email_of(about)
        ok = bool(email)
        rec = {
            "ok": ok,
            "kind": None if ok else "BROKE",
            "email": email,
            "displayName": _display_of(about),
            "permissionId": _permission_of(about),
            "quotaBytesTotal": about.get("quotaBytesTotal"),
            "quotaBytesUsed": about.get("quotaBytesUsed"),
            "model": email,
            "model_source": MODEL_SOURCE,
            "consent_mode": CONSENT_MODE,
            "refresh_ttl_s": REFRESH_TTL_S,
            "http": 200 if ok else None,
            "detail": (
                f"gdx-drive about.get email={email} "
                f"permissionId={_permission_of(about)}"
                if ok else
                f"BROKE: Drive about.get named no emailAddress "
                f"(got user={about.get('user')!r})"
            ),
        }
        self._last = rec
        return ok, rec["detail"]

    def dispatch(self, payload: dict) -> dict:
        """Identity only. Prove path is about.get; boot never calls this."""
        _ = payload
        ok, detail = self.probe()
        ident = self._last or {}
        email = str(ident.get("email") or "")
        body = (
            f"gdx-drive about.get email={email} "
            f"permissionId={ident.get('permissionId') or ''}"
            if ok else ""
        )
        return {
            "ok": ok,
            "rc": 0 if ok else 2,
            "body": body,
            "body_bytes": len(body.encode("utf-8")),
            "model": email if ok else "",
            "model_source": MODEL_SOURCE if ok else "",
            "kind": ident.get("kind"),
            "detail": detail,
            "link_id": self.link_id,
            "text": body,
        }


def register_gdx_drive_rail(registry, adapters: dict, spend_gate=None,
                            src: str | None = None, dst: str | None = None, *,
                            paths=None, spec=None, key_path=None,
                            client_secrets_path=None, about_fn=None) -> dict:
    _ = spend_gate
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
    if client_secrets_path is None and paths is not None:
        client_secrets_path = client_secrets_path_for(paths)
    rail = GdxDriveRail(key_path, spec, about_fn=about_fn,
                        client_secrets_path=client_secrets_path)
    lid = rail.link_id
    if lid not in registry.state():
        registry.register(lid, spec["rail_type"], spec["src"], spec["dst"],
                          policy_rank=int(spec["policy_rank"]))
    registry.attach_probe(lid, rail.probe)
    adapters[lid] = rail
    cred_ok = bool(key_path) and Path(key_path).exists()
    return {
        "link_id": lid,
        "rail": rail,
        "spec": spec,
        "key_ok": cred_ok,
        "key_last4": "present" if cred_ok else "NO_KEY",
        "key_path": str(key_path) if key_path is not None else None,
        "src": spec["src"],
        "dst": spec["dst"],
    }


from cosmos_rail_base import (  # noqa: E402,F401
    _ledger_is_authority,
    write_probe_record,
)


def attach_to_kernel(kernel, adapters: dict | None = None, about_fn=None,
                     *, boot_compose: bool = False) -> dict:
    if _ledger_is_authority(kernel) and not boot_compose:
        raise GdxDriveRailError(
            "REFUSED",
            "attach_to_kernel refuses authority LINK_REGISTERED until Kernel "
            "boot reattaches probes every boot (BACKLOG). Isolated --gate "
            "ledger only. Pass boot_compose=True only from Kernel.__init__.")
    if adapters is None:
        adapters = getattr(kernel, "adapters", None)
        if adapters is None:
            adapters = {}
            kernel.adapters = adapters
    return register_gdx_drive_rail(
        kernel.registry, adapters, spend_gate=getattr(kernel, "spend", None),
        paths=kernel.paths, about_fn=about_fn)


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
    except GdxDriveRailError as e:
        rec["refused"] = e.kind == "REFUSED"
        rec["kind"] = e.kind
        rec["detail"] = str(e)
    return rec


def inspect_live_kernel(root) -> dict:
    out = {"opened": False, "gdx_drive_in_registry": None, "error": None}
    try:
        from cosmos_kernel import Kernel
        k = Kernel(root, worker="gdx-drive-rail-gate", read_only=True)
        out["opened"] = True
        out["tree_id"] = k.paths.sentinel.tree_id
        out["gdx_drive_in_registry"] = LINK_ID in k.registry.state()
        out["read_only"] = True
    except Exception as e:  # noqa: BLE001
        out["error"] = f"{type(e).__name__}: {e}"
    return out


def _iso_now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _compose_isolated(paths, spec, keyp, about_fn):
    from cosmos_ledger import Ledger
    from cosmos_registry import Registry
    from cosmos_rails import Dispatcher
    from cosmos_spend import SpendGate

    adapters = {}
    gate_dir = paths.role("state", "gdx_drive_rail")
    gate_dir.mkdir(parents=True, exist_ok=True)
    led = Ledger(gate_dir / "gate.jsonl", b"gdx-drive-rail-gate", WORKER)
    reg = Registry(led)
    spend = SpendGate(led)
    attached = register_gdx_drive_rail(
        reg, adapters, spend_gate=spend, spec=spec, key_path=keyp,
        client_secrets_path=client_secrets_path_for(paths),
        about_fn=about_fn)
    disp = Dispatcher(reg, adapters, led, spend=spend)
    return attached, adapters, disp, led, gate_dir


def gate(root: str | os.PathLike, *, about_fn=None) -> dict:
    """Runtime-binding gate. Isolated ledger. Live about.get unless injected.

    PASS iff about.user.emailAddress is non-empty AND attach refused AND
    kernel_attached is false. rc=0 is not the proof;
    config/gdx_drive_rail_probe.json is. Missing credential is NO_KEY /
    UNMEASURED, never GREEN.
    """
    from cosmos_paths import CosmosPaths

    paths = CosmosPaths(root)
    spec = load_spec(spec_path_for(paths))
    write_spec(spec_path_for(paths), spec)
    keyp = key_path_for(paths, spec)
    attached, adapters, disp, led, gate_dir = _compose_isolated(
        paths, spec, keyp, about_fn)
    try:
        measured_rec = disp.registry.probe(attached["link_id"])
    except Exception as e:  # noqa: BLE001
        measured_rec = {"ok": False, "detail": f"{type(e).__name__}: {e}"}
    rail = adapters[attached["link_id"]]
    ident = rail.last_identity()
    if ident is None:
        ok, detail = rail.probe()
        ident = rail.last_identity()
        measured_rec = {"ok": ok, "detail": detail}
    matrix = disp.registry.matrix()
    email = (ident or {}).get("email") or ""
    rec = {
        "schema": SCHEMA,
        "worker": WORKER,
        "gated_at": _iso_now(),
        "root": str(paths.root),
        "tree_id": paths.sentinel.tree_id,
        "link_id": attached["link_id"],
        "key_ok": attached["key_ok"],
        "key_path_name": CREDENTIALS_NAME,
        "key_value_emitted": False,
        "consent_mode": CONSENT_MODE,
        "refresh_ttl_s": REFRESH_TTL_S,
        "spec_path": str(spec_path_for(paths)),
        "route": f"{attached['src']}->{attached['dst']}",
        "vendor_docs": VENDOR_DOCS,
        "probe_ok": bool((measured_rec or {}).get("ok")),
        "probe_detail": (measured_rec or {}).get("detail"),
        "matrix": matrix,
        "dispatcher_constructed": True,
        "dispatcher_class": type(disp).__name__,
        "authority_ledger_written": False,
        "kernel_attached": False,
        "live_value": None,
        "gate": "FAIL",
        "stage6": {
            "kind": "satellite",
            "kernel_attach": "BACKLOG",
            "predicate": (
                "Drive about.user.emailAddress non-empty AND route "
                "core->drive AND attach refused on authority"
            ),
        },
    }
    rec["about"] = {
        "email_present": bool(email),
        "permissionId": (ident or {}).get("permissionId"),
        "http": (ident or {}).get("http"),
        "kind": (ident or {}).get("kind"),
    }
    rec["live_value"] = {
        "emailAddress": email or None,
        "permissionId": (ident or {}).get("permissionId"),
        "http": (ident or {}).get("http"),
        "consent_mode": CONSENT_MODE,
    }
    if not attached["key_ok"] and about_fn is None:
        rec["measured"] = "UNMEASURED"
        rec["identity_why"] = "NO_KEY: gdx_drive_credentials.json absent"
    events = []
    try:
        events = [e.get("event") for e in led.verify()]
    except Exception as e:  # noqa: BLE001
        rec["ledger_error"] = f"{type(e).__name__}: {e}"
    rec["isolated_ledger_events"] = events
    rec["isolated_ledger"] = str(gate_dir / "gate.jsonl")
    rec["attach_refusal"] = refuse_live_authority_attach(paths)
    rec["live_kernel"] = inspect_live_kernel(root)
    id_ok = bool(email)
    rec["identity_ok"] = id_ok
    rec["identity_why"] = rec.get("identity_why") or (
        "ok" if id_ok else f"emailAddress={email!r} kind={(ident or {}).get('kind')}")
    route_ok = rec["route"] == f"{SRC}->{DST}"
    attach_refused = bool(rec["attach_refusal"].get("refused"))
    if (rec["probe_ok"] and rec["identity_ok"] and route_ok and attach_refused
            and not rec["authority_ledger_written"]
            and rec["kernel_attached"] is False
            and (attached["key_ok"] or about_fn is not None)):
        rec["gate"] = "PASS"
    rec["proof"] = (
        f"gdx-drive probe_ok={rec['probe_ok']} "
        f"email_present={bool(email)} "
        f"tree_id={rec['tree_id']} route={rec['route']} "
        f"attach_refused={attach_refused} kernel_attached={rec['kernel_attached']} "
        f"measured={rec.get('measured') or ('BOUND' if rec['gate'] == 'PASS' else 'FAIL')}"
    )
    probe_path = probe_path_for(paths)
    written = write_probe_record(probe_path, rec)
    written["probe_path"] = str(probe_path)
    gate_json = gate_dir / "gate.json"
    write_probe_record(gate_json, written)
    written["gate_json"] = str(gate_json)
    return written


def _selftest() -> int:
    import tempfile
    from cosmos_kernel import install, Kernel
    from cosmos_ledger import Ledger
    from cosmos_registry import Registry
    from cosmos_rails import Dispatcher
    from cosmos_spend import SpendGate

    results = []

    def check(label, fn):
        try:
            results.append((label, bool(fn()), ""))
        except Exception as e:  # noqa: BLE001
            results.append((label, False, f"{type(e).__name__}: {e}"))

    td = Path(tempfile.mkdtemp(prefix="cosmos_gdx_drive_rail_"))
    root = install(td / "live", tree_id="spike-gdx-drive-rail")
    from cosmos_paths import CosmosPaths
    paths = CosmosPaths(root)
    spec = write_spec(paths.config(SPEC_NAME))
    check("spec pins Testing consent + 7-day refresh TTL",
          lambda: spec.get("consent_mode") == CONSENT_MODE
          and spec.get("refresh_ttl_s") == REFRESH_TTL_S
          and spec.get("vendor_lib") == VENDOR_LIB)
    hijack = merge_spec({
        "schema": SCHEMA,
        "dst": "models",
        "consent_mode": "Production",
        "vendor_docs": "https://example.invalid/fork",
    })
    check("merge_spec coerces dst=models to drive and pins origin",
          lambda: hijack.get("dst") == DST
          and hijack.get("consent_mode") == CONSENT_MODE
          and hijack.get("vendor_docs") == VENDOR_DOCS)

    about = {
        "user": {
            "displayName": "Keith",
            "emailAddress": "keith.bbf@gmail.com",
            "permissionId": "106848635693308452650",
            "isAuthenticatedUser": True,
        },
        "quotaBytesTotal": "16106127360",
        "quotaBytesUsed": "1234",
    }

    def fake_about():
        return dict(about)

    cred = paths.config(CREDENTIALS_NAME)
    cred.write_text("{\"refresh_token\":\"PLACEHOLDER-NOT-A-TOKEN\"}\n",
                    encoding="utf-8")
    secrets = paths.config(CLIENT_SECRETS_NAME)
    secrets.write_text("{\"installed\":{\"client_id\":\"x\"}}\n",
                       encoding="utf-8")

    rail = GdxDriveRail(cred, spec, about_fn=fake_about,
                        client_secrets_path=secrets)
    ok, detail = rail.probe()
    check("probe about.get binds vendor emailAddress",
          lambda: ok and "keith.bbf@gmail.com" in detail
          and rail.last_identity()["email"] == "keith.bbf@gmail.com")
    dispatched = rail.dispatch({"prompt": "ignored"})
    check("dispatch is prove-shaped: rc=0 body model=emailAddress",
          lambda: dispatched["ok"] and dispatched["rc"] == 0
          and dispatched["model"] == "keith.bbf@gmail.com"
          and "permissionId=106848635693308452650" in dispatched["body"])

    def blank_about():
        return {"user": {"displayName": "x"}}

    dead = GdxDriveRail(cred, spec, about_fn=blank_about)
    d_ok, _ = dead.probe()
    d_rec = dead.dispatch({})
    check("about without emailAddress is NOT a proof",
          lambda: d_ok is False and d_rec["model"] == ""
          and not d_rec["ok"])

    def raise_grant():
        raise GdxDriveRailError(
            "AUTH_REQUIRED",
            "invalid_grant: Token has been expired or revoked. " + CONSENT_NOTE)

    grant = GdxDriveRail(cred, spec, about_fn=raise_grant)
    g_ok, g_det = grant.probe()
    check("invalid_grant is AUTH_REQUIRED, never GREEN",
          lambda: g_ok is False and "AUTH_REQUIRED" in g_det
          and "7 days" in g_det)

    missing = GdxDriveRail(paths.config("no_such_token.json"), spec)
    m_ok, m_det = missing.probe()
    check("absent credential is NO_KEY, never GREEN",
          lambda: m_ok is False and "NO_KEY" in m_det)

    led = Ledger(td / "n.jsonl", b"k", "core")
    reg = Registry(led)
    adapters = {}
    rec = register_gdx_drive_rail(
        reg, adapters, spend_gate=SpendGate(led), spec=spec,
        key_path=cred, client_secrets_path=secrets, about_fn=fake_about)
    check("register claims gdx-drive core->drive",
          lambda: rec["link_id"] == LINK_ID and rec["dst"] == DST)
    reg.probe_all()
    disp = Dispatcher(reg, adapters, led, spend=SpendGate(led))
    routed = disp.dispatch(SRC, DST, {})
    check("isolated Dispatcher about.get binds emailAddress",
          lambda: routed["ok"] and routed.get("model") == "keith.bbf@gmail.com")
    check("RAIL_DISPATCH + RAIL_RESULT ledgered (hash-chained isolated)",
          lambda: {e["event"] for e in led.verify()} >= {
              "LINK_REGISTERED", "PROBE_RESULT", "RAIL_DISPATCH", "RAIL_RESULT"})

    g = gate(root, about_fn=fake_about)
    check("gate PASS quotes vendor emailAddress",
          lambda: g["gate"] == "PASS"
          and g["live_value"]["emailAddress"] == "keith.bbf@gmail.com")
    check("gate kernel_attached is false",
          lambda: g["kernel_attached"] is False)
    check("gate attach refused",
          lambda: g["attach_refusal"]["refused"] is True)
    check("gate does not write authority",
          lambda: g["authority_ledger_written"] is False)
    check("gate never emits the refresh token",
          lambda: g.get("key_value_emitted") is False
          and "PLACEHOLDER-NOT-A-TOKEN" not in json.dumps(g))
    check("gate route is core->drive",
          lambda: g.get("route") == f"{SRC}->{DST}")

    bare = install(td / "bare", tree_id="spike-gdx-drive-bare")
    g_bare = gate(bare)
    check("bare root gate is FAIL/UNMEASURED, never GREEN",
          lambda: g_bare.get("gate") != "PASS"
          and g_bare.get("measured") == "UNMEASURED")

    k = Kernel(root, worker="gdx-drive-rail-selftest")
    _before = set(k.registry.state())
    refused = False
    try:
        attach_to_kernel(k, {})
    except GdxDriveRailError as e:
        refused = e.kind == "REFUSED"
    check("attach_to_kernel refuses writing Kernel without boot_compose",
          lambda: refused and set(k.registry.state()) == _before)
    check("writing boot composed gdx-drive adapter (no invoke)",
          lambda: "gdx-drive" in (k.rails_compose or {}).get("composed", [])
          and LINK_ID in k.adapters)

    bad = [(l, e) for l, ok, e in results if not ok]
    for label, ok, err in results:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (gdx-drive PyDrive2 about.get; "
          "emailAddress bind; Testing 7d; invalid_grant AUTH_REQUIRED; "
          "UNMEASURED never GREEN; attach refused)"
          % ("PASS" if not bad else "FAIL", len(results)))
    return 0 if not bad else 1


def main() -> int:
    ap = argparse.ArgumentParser(
        prog="cosmos_gdx_drive_rail",
        description="COSMOS GDX Drive PyDrive2 rail. about.get identity. "
                    "Testing consent refresh every 7 days.")
    ap.add_argument("--root", default=None)
    ap.add_argument("--gate", action="store_true")
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if a.gate or a.probe:
        if not a.root:
            print(json.dumps({
                "ok": False, "kind": "BAD_ROOT",
                "error": "--root is required (resolver does not guess)",
            }, indent=1))
            return 2
        if a.probe and not a.gate:
            from cosmos_paths import CosmosPaths
            paths = CosmosPaths(a.root)
            spec = load_spec(spec_path_for(paths))
            rail = GdxDriveRail(
                key_path_for(paths, spec), spec,
                client_secrets_path=client_secrets_path_for(paths))
            ok, detail = rail.probe()
            ident = rail.last_identity() or {}
            rec = {
                "ok": ok, "detail": detail, "link_id": rail.link_id,
                "email_present": bool(ident.get("email")),
                "permissionId": ident.get("permissionId"),
                "kind": ident.get("kind"),
                "consent_mode": CONSENT_MODE,
                "measured": "BOUND" if ok else (
                    "UNMEASURED" if (ident.get("kind") == "NO_KEY") else "FAIL"),
            }
            print(json.dumps(rec, indent=1))
            return 0 if ok else 1
        rec = gate(a.root)
        print(json.dumps({
            "gate": rec.get("gate"),
            "proof": rec.get("proof"),
            "live_value": rec.get("live_value"),
            "measured": rec.get("measured"),
            "probe_path": rec.get("probe_path"),
            "tree_id": rec.get("tree_id"),
        }, indent=1, default=str))
        return 0 if rec.get("gate") == "PASS" else 1
    print(json.dumps({"ok": False, "kind": "BAD_ARGS",
                      "error": "pass --selftest or --root … --gate|--probe"},
                     indent=1))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
