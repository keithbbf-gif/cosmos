#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: ROAD bring-up (cosmos_up.RoadUp) with a FAKE runner - every
tailscale/schtasks interaction is canned, nothing touches the real system.
Proves: tailnet+cert happy path, NOT_LOGGED_IN, NO_TAILSCALE (lan-only
fallback), NO_CERT -> self-signed fallback, the schtasks persistence argv, and
that the serve plan carries --tls and the 0.0.0.0 bind (--remote). Every state
typed, nothing fabricated."""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cosmos_up import RoadUp, UpError

RESULTS = []


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                            # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def expect(label, kind, fn):
    """fn must raise UpError with .kind == kind - typed errors ONLY."""
    def _run():
        try:
            fn()
        except UpError as e:
            return e.kind == kind
        except Exception:                                             # noqa: BLE001
            return False   # a bare exception escaping the API is a FAIL
        return False       # not raising at all is a FAIL
    check(label, _run)


FQDN_DOTTED = "keiths-pc.tail1234.ts.net."
FQDN = "keiths-pc.tail1234.ts.net"
TS_IP = "100.101.102.103"
RUNNING = json.dumps({
    "BackendState": "Running",
    "Self": {"DNSName": FQDN_DOTTED,
             "TailscaleIPs": [TS_IP, "fd7a:115c:a1e0:ab12::1"]},
    "MagicDNSSuffix": "tail1234.ts.net"})
NEEDS_LOGIN = json.dumps({"BackendState": "NeedsLogin"})
STOPPED = json.dumps({"BackendState": "Stopped"})


def make_runner(status_out=RUNNING, status_rc=0, cert_rc=0, cert_out="",
                no_exe=False, schtasks_rc=0, schtasks_out="SUCCESS: task created.",
                calls=None):
    """Canned tailscale/schtasks. calls (if given) records every argv."""
    def run(argv):
        if calls is not None:
            calls.append(list(argv))
        if argv[0] == "schtasks":
            return (schtasks_rc, schtasks_out)
        if no_exe:
            raise FileNotFoundError(argv[0])       # not on PATH, not installed
        if "status" in argv:
            return (status_rc, status_out)
        if "cert" in argv:
            return (cert_rc, cert_out)
        return (1, f"unexpected argv: {argv}")
    return run


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="cosmos_up_"))
    root = td / "Cosmos"
    LAN = lambda: "192.168.1.50"                                      # noqa: E731
    CLOCK = lambda: 1234.5                                            # noqa: E731

    # ===== happy path: tailscale installed + logged in ==========================
    calls = []
    ru = RoadUp(runner=make_runner(calls=calls), clock=CLOCK, lan_ip_fn=LAN)
    det = ru.detect_tailscale()
    check("detect: installed AND logged_in, both measured",
          lambda: det["installed"] is True and det["logged_in"] is True)
    check("detect: tailnet IPv4 is the 100.x address (v6 filtered out)",
          lambda: det["ip"] == TS_IP)
    check("detect: fqdn is the MagicDNS name with the trailing dot STRIPPED",
          lambda: det["fqdn"] == FQDN)

    r = ru.up(root, 8770)
    check("up: state ok / reach tailnet / cert tailscale",
          lambda: (r["state"], r["reach"], r["cert"]) ==
          ("ok", "tailnet", "tailscale"))
    check("up: phone_url is https on the tailnet FQDN with the port",
          lambda: r["phone_url"] == f"https://{FQDN}:8770/")
    check("up: no next_step on the happy path (nothing owed from Keith)",
          lambda: r["next_step"] is None)
    check("up: injected clock stamped the check",
          lambda: r["checked_at"] == 1234.5)
    cert_calls = [c for c in calls if "cert" in c]
    check("up: tailscale cert argv carries --cert-file/--key-file cosmos.crt|key + fqdn",
          lambda: cert_calls and cert_calls[0][1] == "cert"
          and cert_calls[0][2] == "--cert-file"
          and cert_calls[0][3].endswith("cosmos.crt")
          and cert_calls[0][4] == "--key-file"
          and cert_calls[0][5].endswith("cosmos.key")
          and cert_calls[0][6] == FQDN)
    check("up: notes admit the cert is UNUSED by serve (no --cert flag yet)",
          lambda: any("--cert/--key" in n for n in r["notes"]))
    check("up: notes carry the token rule (remote bind never mints api_token)",
          lambda: any("api_token" in n for n in r["notes"]))

    # ===== the serve plan =======================================================
    cmd = ru.plan_serve_cmd(root, 8770)
    check("plan_serve_cmd: py -3.14 cosmos.py serve --root --port",
          lambda: cmd[0] == "py" and cmd[1] == "-3.14"
          and cmd[2].endswith("cosmos.py") and cmd[3] == "serve"
          and "--root" in cmd and "--port" in cmd and "8770" in cmd)
    check("plan_serve_cmd: --remote present (cosmos.py's 0.0.0.0 bind)",
          lambda: "--remote" in cmd)
    check("plan_serve_cmd: --tls present (remote cleartext is REFUSED by Service)",
          lambda: "--tls" in cmd)

    # ===== NOT_LOGGED_IN ========================================================
    ru2 = RoadUp(runner=make_runner(status_out=NEEDS_LOGIN), lan_ip_fn=LAN)
    det2 = ru2.detect_tailscale()
    check("detect: NeedsLogin -> installed True, logged_in False",
          lambda: det2["installed"] is True and det2["logged_in"] is False)
    check("detect: no ip/fqdn FABRICATED when not logged in (fields absent)",
          lambda: "ip" not in det2 and "fqdn" not in det2)
    r2 = ru2.up(root, 8770)
    check("up: NOT_LOGGED_IN is the typed state, reach lan-only",
          lambda: r2["state"] == "NOT_LOGGED_IN" and r2["reach"] == "lan-only")
    check("up: NOT_LOGGED_IN next_step names the ONE step (tailscale login)",
          lambda: "tailscale login" in r2["next_step"])
    check("up: NOT_LOGGED_IN still hands a LAN fallback phone_url",
          lambda: r2["phone_url"] == "https://192.168.1.50:8770/")

    # plain-text logged-out (older CLI, non-JSON, rc!=0) is STILL not BAD_STATE
    ru2b = RoadUp(runner=make_runner(status_out="Logged out.", status_rc=1),
                  lan_ip_fn=LAN)
    det2b = ru2b.detect_tailscale()
    check("detect: plain 'Logged out.' rc=1 -> logged_in False, NOT BAD_STATE",
          lambda: det2b["installed"] and not det2b["logged_in"]
          and det2b.get("state") != "BAD_STATE")

    # ===== NO_TAILSCALE =========================================================
    ru3 = RoadUp(runner=make_runner(no_exe=True), lan_ip_fn=LAN)
    det3 = ru3.detect_tailscale()
    check("detect: exe absent on BOTH candidates -> installed False, nothing invented",
          lambda: det3["installed"] is False and det3["logged_in"] is False
          and "ip" not in det3 and "fqdn" not in det3)
    r3 = ru3.up(root, 8770)
    check("up: NO_TAILSCALE typed state + lan-only + self-signed",
          lambda: (r3["state"], r3["reach"], r3["cert"]) ==
          ("NO_TAILSCALE", "lan-only", "self-signed"))
    check("up: NO_TAILSCALE next_step says install Tailscale (PC and phone)",
          lambda: "Install Tailscale" in r3["next_step"]
          and "phone" in r3["next_step"])
    check("up: NO_TAILSCALE lan fallback url still offered",
          lambda: r3["phone_url"] == "https://192.168.1.50:8770/")
    check("up: serve_cmd still composed even when unreachable from the road",
          lambda: "--tls" in r3["serve_cmd"] and "--remote" in r3["serve_cmd"])

    # honest when even the LAN ip is unknown: None, never a made-up address
    ru3b = RoadUp(runner=make_runner(no_exe=True), lan_ip_fn=lambda: None)
    check("up: unknown LAN ip -> phone_url is None, not fabricated",
          lambda: ru3b.up(root, 8770)["phone_url"] is None)

    # ===== NO_CERT -> self-signed fallback ======================================
    ERR = "error: Tailscale HTTPS cert support is not enabled on this tailnet"
    ru4 = RoadUp(runner=make_runner(cert_rc=1, cert_out=ERR), lan_ip_fn=LAN)
    ru4.detect_tailscale()
    expect("ensure_cert: failure raises TYPED UpError NO_CERT", "NO_CERT",
           lambda: ru4.ensure_cert(FQDN, td / "cfg"))
    def _stderr_carried():
        try:
            ru4.ensure_cert(FQDN, td / "cfg")
        except UpError as e:
            return ERR in str(e)
        return False
    check("ensure_cert: the tailscale stderr rides in the error", _stderr_carried)
    r4 = ru4.up(root, 8770)
    check("up: cert failure -> reach STILL tailnet, cert self-signed (fallback)",
          lambda: (r4["state"], r4["reach"], r4["cert"]) ==
          ("ok", "tailnet", "self-signed"))
    check("up: cert-failure next_step says enable HTTPS certs; voice-out still offered",
          lambda: "HTTPS" in r4["next_step"] and "Voice-out" in r4["next_step"])
    check("up: cert-failure phone_url still the tailnet fqdn",
          lambda: r4["phone_url"] == f"https://{FQDN}:8770/")

    # ===== BAD_STATE ============================================================
    ru5 = RoadUp(runner=make_runner(status_out=STOPPED), lan_ip_fn=LAN)
    det5 = ru5.detect_tailscale()
    check("detect: BackendState Stopped -> BAD_STATE, never a fabricated success",
          lambda: det5.get("state") == "BAD_STATE" and not det5["logged_in"])
    r5 = ru5.up(root, 8770)
    check("up: BAD_STATE typed through, lan-only, actionable next_step",
          lambda: r5["state"] == "BAD_STATE" and r5["reach"] == "lan-only"
          and "tailscale up" in r5["next_step"])

    # ===== persistence: the schtasks plan =======================================
    calls6 = []
    ru6 = RoadUp(runner=make_runner(calls=calls6), lan_ip_fn=LAN)
    p = ru6.install_persistent(root, 8770)
    check("install_persistent: rc 0 -> ok True and argv returned",
          lambda: p["ok"] is True and p["rc"] == 0 and p["argv"] == calls6[0])
    a = p["argv"]
    def _flag(name):
        return a[a.index(name) + 1]
    check("install_persistent: schtasks /create /tn 'COSMOS Serve' /sc onlogon",
          lambda: a[0] == "schtasks" and a[1] == "/create"
          and _flag("/tn") == "COSMOS Serve" and _flag("/sc") == "onlogon")
    check("install_persistent: /rl highest and /f present",
          lambda: _flag("/rl") == "highest" and "/f" in a)
    check("install_persistent: /tr carries the FULL reachable serve cmd",
          lambda: "serve" in _flag("/tr") and "--remote" in _flag("/tr")
          and "--tls" in _flag("/tr") and "-3.14" in _flag("/tr"))
    check("install_persistent: elevation need is STATED in the return",
          lambda: "elevat" in p["needs_elevation"])

    ru6b = RoadUp(runner=make_runner(schtasks_rc=1,
                                     schtasks_out="ERROR: Access is denied."),
                  lan_ip_fn=LAN)
    pb = ru6b.install_persistent(root, 8770)
    check("install_persistent: nonzero rc REPORTED, never swallowed",
          lambda: pb["ok"] is False and pb["rc"] == 1
          and "Access is denied" in pb["out"] and "elevated" in pb["note"])

    # ===== injected exe path is honored =========================================
    calls7 = []
    ru7 = RoadUp(runner=make_runner(calls=calls7),
                 tailscale_exe=r"C:\Program Files\Tailscale\tailscale.exe",
                 lan_ip_fn=LAN)
    ru7.detect_tailscale()
    check("detect: injected tailscale_exe is the argv[0] actually run",
          lambda: calls7[0][0] == r"C:\Program Files\Tailscale\tailscale.exe")

    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for label, ok, err in RESULTS:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (road bring-up: every reach/cert state "
          "typed and measured, nothing fabricated)"
          % ("PASS" if not bad else "FAIL", len(RESULTS)))
    return 0 if not bad else 1


def test_up():
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())
