#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_up - ROAD reachability. One command that makes COSMOS reachable from
Keith's phone over the internet, not just a USB cable or the LAN.

The reach layer is Tailscale (WireGuard mesh VPN): this PC gets a stable tailnet
IPv4 (100.x) and a MagicDNS name reachable from the phone anywhere, and
`tailscale cert <fqdn>` issues a REAL, browser-trusted cert for that name - which
is what lets the phone's Web Speech voice-IN run over the air (voice-out works
even over a self-signed cert; the mic API needs a trusted origin).

PURE LOGIC, INJECTED EFFECTS. Every system touch goes through an injected
runner `run(argv) -> (rc, out)`; the default runner is a real subprocess, but
tests pass a fake and prove every state without touching the machine. Nothing
here fabricates success: NOT-installed, NOT-logged-in, NO-cert and BAD-state
are DISTINCT, TYPED outcomes (UpError.kind), each carrying the one step Keith
must actually take.

KNOWN GAP, measured 2026-08-24: cosmos.py serve / cosmos_service.Service have
NO way to point at an existing cert/key pair (Service mints its own self-signed
pair into config/cosmos_cert.pem, and its SAN check would REGENERATE over a
tailscale cert dropped at that path). So the tailscale cert is fetched to
config/cosmos.crt|cosmos.key (distinct names - nothing clobbers them) and the
serve plan uses --tls (self-signed) until a --cert/--key flag lands. That flag
is the follow-up; this module already passes cert/key through plan_serve_cmd's
signature so call sites do not change when it does.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

_TAILNET_V4 = re.compile(r"^100\.\d{1,3}\.\d{1,3}\.\d{1,3}$")


class UpError(RuntimeError):
    """kind in {NO_TAILSCALE, NOT_LOGGED_IN, NO_CERT, BAD_STATE}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def _real_runner(argv) -> tuple[int, str]:
    """Default runner: a real subprocess. Combined stdout+stderr, text."""
    p = subprocess.run(list(argv), capture_output=True, text=True, timeout=120)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def _real_lan_ip():
    """This machine's LAN IPv4, measured by routing (no packet is sent).
    None when unknown - never a fabricated address."""
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
        finally:
            s.close()
    except OSError:
        return None


def _real_clock() -> float:
    import time
    return time.time()


class RoadUp:
    """Detect the tailnet, fetch the real cert, plan the reachable serve
    command, and (optionally) register the persistence task. Everything is a
    plan or a measured state; the only system-changing calls (tailscale cert,
    schtasks) go through the injected runner."""

    TASK_NAME = "COSMOS Serve"

    def __init__(self, runner=None, tailscale_exe: str | None = None,
                 clock=None, lan_ip_fn=None, script: str | None = None):
        self._run = runner or _real_runner
        self._exe = tailscale_exe
        self._clock = clock or _real_clock
        self._lan_ip = lan_ip_fn or _real_lan_ip
        self._script = script or str(Path(__file__).resolve().parent / "cosmos.py")
        self._found_exe: str | None = None    # set by a successful detect

    # ------------------------------------------------------------------ detect
    def _candidates(self):
        if self._exe:
            return [self._exe]
        pf = os.environ.get("ProgramFiles", r"C:\Program Files")
        return ["tailscale", os.path.join(pf, "Tailscale", "tailscale.exe")]

    def detect_tailscale(self) -> dict:
        """Locate tailscale.exe (PATH, then %ProgramFiles%\\Tailscale) and
        measure THIS host's tailnet state via `tailscale status --json`.

        Returns {installed, logged_in[, exe, ip, fqdn, state, detail]} - every
        field MEASURED; ip/fqdn are absent (not empty, not guessed) when
        unknown. installed=False <=> NO_TAILSCALE; logged_in=False with no
        'state' key <=> NOT_LOGGED_IN; state='BAD_STATE' when the binary
        answers but the backend is neither Running nor NeedsLogin."""
        last_err = None
        for cand in self._candidates():
            try:
                rc, out = self._run([cand, "status", "--json"])
            except OSError as e:                     # FileNotFoundError included
                last_err = f"{cand}: {e}"
                continue
            low = (out or "").lower()
            if rc != 0 and ("not recognized" in low or "no such file" in low
                            or "cannot find the" in low):
                last_err = f"{cand}: {out.strip()[:200]}"
                continue
            self._found_exe = cand
            return self._parse_status(cand, rc, out)
        info = {"installed": False, "logged_in": False}
        if last_err:
            info["detail"] = last_err
        return info

    def _parse_status(self, exe: str, rc: int, out: str) -> dict:
        info = {"installed": True, "logged_in": False, "exe": exe}
        try:
            st = json.loads(out)
        except (ValueError, TypeError):
            st = None
        if st is None:
            low = (out or "").lower()
            if "logged out" in low or "not logged in" in low or "needslogin" in low:
                return info                                # NOT_LOGGED_IN, plainly
            info["state"] = "BAD_STATE"
            info["detail"] = (out or "").strip()[:400] or f"status rc={rc}, no output"
            return info
        backend = st.get("BackendState")
        if backend == "NeedsLogin":
            return info
        if backend != "Running":
            info["state"] = "BAD_STATE"
            info["detail"] = f"BackendState={backend!r}"
            return info
        info["logged_in"] = True
        self_node = st.get("Self") or {}
        ips = [i for i in (self_node.get("TailscaleIPs") or [])
               if isinstance(i, str) and _TAILNET_V4.match(i)]
        if ips:
            info["ip"] = ips[0]
        fqdn = (self_node.get("DNSName") or "").rstrip(".")
        if fqdn:
            info["fqdn"] = fqdn
        return info

    # -------------------------------------------------------------------- cert
    def ensure_cert(self, fqdn: str, out_dir) -> dict:
        """`tailscale cert` for this host's tailnet name -> a REAL trusted pair
        at <out_dir>/cosmos.crt|cosmos.key (distinct from the service's
        self-signed cosmos_cert.pem, so nothing regenerates over it).
        Raises UpError('NO_CERT', <tailscale stderr>) on failure - e.g. HTTPS
        certificates not enabled on the tailnet - and the caller falls back to
        self-signed (voice-out still works; voice-in may warn)."""
        exe = self._found_exe or self._exe or "tailscale"
        out_dir = str(out_dir)
        try:
            os.makedirs(out_dir, exist_ok=True)
        except OSError:
            pass                    # tailscale will say so, loudly, below
        cert = os.path.join(out_dir, "cosmos.crt")
        key = os.path.join(out_dir, "cosmos.key")
        try:
            rc, out = self._run([exe, "cert",
                                 "--cert-file", cert, "--key-file", key, fqdn])
        except OSError as e:
            raise UpError("NO_CERT", f"tailscale cert could not run: {e}")
        if rc != 0:
            raise UpError("NO_CERT",
                          (out or "").strip() or f"tailscale cert rc={rc}")
        return {"cert": cert, "key": key, "fqdn": fqdn}

    # -------------------------------------------------------------------- plan
    def plan_serve_cmd(self, root, port: int,
                       cert: str | None = None, key: str | None = None) -> list:
        """The exact argv that serves COSMOS reachably: `--remote` is
        cosmos.py's 0.0.0.0 bind (host = "0.0.0.0" if a.remote - LAN and
        tailnet both reach it) and `--tls` is mandatory because Service REFUSES
        a non-loopback bind over cleartext (REMOTE_CLEARTEXT).

        cert/key are ACCEPTED but NOT passed: cosmos.py serve has no
        --cert/--key flag today (measured 2026-08-24; see module docstring).
        When that flag lands, this is the one function that changes."""
        argv = ["py", "-3.14", self._script, "serve",
                "--root", str(root), "--port", str(port), "--remote", "--tls"]
        # cert/key intentionally unused until the service accepts them.
        return argv

    # ------------------------------------------------------------- persistence
    def install_persistent(self, root, port: int) -> dict:
        """Register the Windows scheduled task so COSMOS serves at every logon
        (survives reboot/logoff; schtasks restarts it at the next logon if it
        died). /rl highest needs ONE elevated shell from Keith to register;
        after that it is standing. A nonzero rc is reported, never swallowed."""
        serve = self.plan_serve_cmd(root, port)
        tr = subprocess.list2cmdline(serve)
        argv = ["schtasks", "/create", "/tn", self.TASK_NAME, "/tr", tr,
                "/sc", "onlogon", "/rl", "highest", "/f"]
        try:
            rc, out = self._run(argv)
        except OSError as e:
            return {"argv": argv, "rc": -1, "ok": False, "out": str(e),
                    "note": "schtasks could not run at all"}
        return {
            "argv": argv, "rc": rc, "ok": rc == 0, "out": (out or "").strip(),
            "note": ("registered: serves on every logon" if rc == 0 else
                     "FAILED - schtasks returned nonzero (run from an "
                     "elevated shell: /rl highest requires admin)"),
            "needs_elevation": "/rl highest needs one elevated (admin) "
                               "registration from Keith",
        }

    # ---------------------------------------------------------------------- up
    def up(self, root, port: int) -> dict:
        """Orchestrate the road bring-up. Never raises for a reach state -
        returns it, typed and actionable:
          {phone_url, reach: 'tailnet'|'lan-only', cert: 'tailscale'|'self-signed',
           state: 'ok'|<UpError kind>, next_step: str|None, serve_cmd, notes,
           detect, checked_at}
        phone_url is None rather than invented when no address was measured."""
        det = self.detect_tailscale()
        serve_cmd = self.plan_serve_cmd(root, port)
        notes = [
            "a remote bind REFUSES to mint config/api_token.txt - if it does "
            "not exist yet, run one loopback serve first "
            "(py -3.14 cosmos.py serve --root ...) to mint it",
        ]
        base = {"serve_cmd": serve_cmd, "detect": det,
                "checked_at": self._clock(), "notes": notes}

        def _lan_fallback(state: str, next_step: str) -> dict:
            lan = self._lan_ip()
            return {**base, "state": state, "reach": "lan-only",
                    "cert": "self-signed",
                    "phone_url": f"https://{lan}:{port}/" if lan else None,
                    "next_step": next_step}

        if not det["installed"]:
            return _lan_fallback(
                "NO_TAILSCALE",
                "Install Tailscale on this PC "
                "(https://tailscale.com/download/windows) and sign in once; "
                "install the Tailscale app on the phone with the same account. "
                "Then run `cosmos up` again. Until then the phone reaches "
                "COSMOS on the LAN only (same Wi-Fi).")
        if not det["logged_in"]:
            if det.get("state") == "BAD_STATE":
                return _lan_fallback(
                    "BAD_STATE",
                    "Tailscale is installed but not running normally "
                    f"({det.get('detail', 'unknown state')}). Run "
                    "`tailscale up` once, then run `cosmos up` again.")
            return _lan_fallback(
                "NOT_LOGGED_IN",
                "Run `tailscale login` on this PC (opens the browser; sign in "
                "once), then run `cosmos up` again.")

        host = det.get("fqdn") or det.get("ip")
        if not host:
            return _lan_fallback(
                "BAD_STATE",
                "Tailscale is running but reported neither a MagicDNS name "
                "nor a 100.x address - run `tailscale status` and check the "
                "tailnet; then run `cosmos up` again.")

        cert_kind, next_step = "self-signed", None
        if det.get("fqdn"):
            try:
                pair = self.ensure_cert(det["fqdn"],
                                        os.path.join(str(root), "config"))
                cert_kind = "tailscale"
                notes.append(
                    f"trusted cert at {pair['cert']} - UNUSED by serve until "
                    "cosmos_service grows a --cert/--key flag (known follow-up); "
                    "serving --tls self-signed meanwhile")
            except UpError as e:
                next_step = (
                    "Enable HTTPS certificates for the tailnet (Tailscale "
                    "admin console -> DNS -> HTTPS Certificates -> Enable) so "
                    "the phone gets a TRUSTED cert - voice-IN (Web Speech) "
                    "needs it. Voice-out already works over the self-signed "
                    f"cert. (tailscale said: {str(e)[:300]})")
        else:
            next_step = ("Enable MagicDNS on the tailnet so this PC gets a "
                         "name `tailscale cert` can certify; reaching it by "
                         "100.x IP works meanwhile (self-signed).")

        return {**base, "state": "ok", "reach": "tailnet", "cert": cert_kind,
                "phone_url": f"https://{host}:{port}/",
                "next_step": next_step}
