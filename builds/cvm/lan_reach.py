#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""lan_reach — is Core reachable from the LAN, and if not, what is missing?

Written because the CVM phone half cannot be measured from this host and the
temptation is to assume the phone "will probably work once someone opens the
port". It will not: `:8770` is bound to loopback, so there is nothing on the
LAN to open. This probe RECORDS that instead of working around it.

It answers three separate questions that are easy to conflate:

    1. does loopback answer?              connect_ex 127.0.0.1:<port>
    2. does the LAN address answer?       connect_ex <lan-ip>:<port>
    3. WHY not — bind or firewall?        the LISTEN socket's own address,
                                          plus the argv Core was spawned with

(2) alone cannot tell bind from firewall: a dropped SYN and a closed port look
similar from one host. (3) settles it with two independent readings — the
kernel's socket table and the spawn record — which is why both are quoted.

NOTHING here reads, prints or copies the bearer token. Reach is a transport
question; the credential is Keith's.

    py -3.14 builds\\cvm\\lan_reach.py --root V:\\A\\Ai\\COSMOS\\live --port 8770
"""
from __future__ import annotations

import argparse
import json
import socket
import sys
import time
from pathlib import Path

WIRE = "cvm-lan-reach/1"
ARTIFACT = "LAN_REACH.json"
CONNECT_TIMEOUT_S = 1.0


def lan_ip() -> str:
    """This box's LAN address, as the routing table resolves it (no send)."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))          # UDP connect: no packet leaves
        return s.getsockname()[0]
    finally:
        s.close()


def probe(host: str, port: int) -> dict:
    s = socket.socket()
    s.settimeout(CONNECT_TIMEOUT_S)
    t0 = time.perf_counter()
    err = s.connect_ex((host, port))
    ms = round((time.perf_counter() - t0) * 1000.0, 3)
    s.close()
    return {"host": host, "port": int(port), "connect_ex": int(err),
            "reachable": err == 0, "ms": ms,
            "errno_name": {0: "OK", 10035: "WSAEWOULDBLOCK (timed out)",
                           10061: "WSAECONNREFUSED",
                           10060: "WSAETIMEDOUT"}.get(err, "errno %d" % err)}


def listeners(port: int) -> dict:
    """The LISTEN socket's OWN local address — the kernel's answer, not ours."""
    try:
        import psutil
    except ImportError:
        return {"available": False,
                "why": "psutil absent — bind address unread, not assumed"}
    rows = []
    for c in psutil.net_connections(kind="tcp"):
        if c.laddr and int(c.laddr.port) == int(port) and c.status == "LISTEN":
            rows.append({"laddr": c.laddr.ip, "port": int(c.laddr.port),
                         "pid": c.pid})
    return {"available": True, "listen": rows,
            "loopback_only": bool(rows) and all(
                r["laddr"] in ("127.0.0.1", "::1") for r in rows)}


def spawn_argv(root: Path) -> dict:
    """The argv Core was actually started with. `--remote` is the bind switch."""
    p = Path(root) / "logs" / "core_serve.json"
    if not p.is_file():
        return {"available": False, "path": str(p)}
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except ValueError as e:
        return {"available": False, "path": str(p), "why": str(e)[:120]}
    argv = [str(x) for x in (d.get("argv") or [])]
    return {"available": True, "path": str(p), "pid": d.get("pid"),
            "argv": argv,
            "has_remote": "--remote" in argv,
            "has_tls": "--tls" in argv,
            "has_cert": "--cert" in argv,
            "has_no_auth": "--no-auth" in argv,
            "has_insecure_http": "--insecure-http" in argv}


def requirements(verdict: str) -> list[dict]:
    """What LAN reach actually needs — each step with the code that enforces it.

    Recorded, not performed: the bind is the resident authority's, restarting
    it is the operator's call, and the firewall rule needs elevation. This is
    the work order, not a workaround.
    """
    return [
        {"step": 1, "need": "bind the LAN, not loopback",
         "how": "cosmos.py serve --remote  (cosmos.py:112 -> host='0.0.0.0')",
         "enforced_by": "cosmos_service.Service.__init__ (_is_remote_bind)",
         "blocking": True},
        {"step": 2, "need": "TLS, because a remote bind refuses cleartext",
         "how": "--tls (self-signed into config/, SAN covers the bind IP) or "
                "--cert/--key for a trusted pair",
         "enforced_by": "cosmos_service.py:1503 raises REMOTE_CLEARTEXT — a "
                        "non-loopback bind will not start over HTTP",
         "note": "the 'cryptography' lib must be importable or --tls silently "
                 "stays HTTP and then trips the same refusal",
         "blocking": True},
        {"step": 3, "need": "keep bearer auth ON across the LAN",
         "how": "do NOT pass --no-auth; the token stays the access control and "
                "TLS stops it being captured in flight",
         "enforced_by": "_load_api_token(remote=True) refuses an empty token",
         "blocking": True},
        {"step": 4, "need": "a Windows Firewall inbound rule for the port",
         "how": "operator action, needs elevation — a LAN bind with no rule is "
                "still a dropped SYN",
         "enforced_by": "nothing in COSMOS; the OS",
         "blocking": True},
        {"step": 5, "need": "the phone must trust the cert",
         "how": "self-signed means installing the CA on the phone, or use "
                "`cosmos up` (Tailscale) and reach it over the tailnet instead",
         "enforced_by": "the phone's TLS stack",
         "blocking": False},
    ]


def run(root: str, port: int, artifact: str | None = None) -> dict:
    ip = lan_ip()
    loop = probe("127.0.0.1", port)
    lan = probe(ip, port)
    lis = listeners(port)
    spawn = spawn_argv(Path(root))
    if lan["reachable"]:
        verdict = "LAN_REACHABLE"
        why = "the LAN address answered — a phone on this network can reach Core"
    elif lis.get("loopback_only") or (spawn.get("available")
                                      and not spawn.get("has_remote")):
        verdict = "LOOPBACK_ONLY"
        why = ("Core is bound to loopback, so there is no LAN socket to open. "
               "A firewall rule alone would change nothing.")
    else:
        verdict = "UNREACHABLE_CAUSE_UNKNOWN"
        why = ("the LAN address did not answer and neither the socket table "
               "nor the spawn record settled why — not guessed at")
    rec = {
        "wire": WIRE,
        "measured_at_epoch": time.time(),
        "iso": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "live_root": str(Path(root).resolve()),
        "port": int(port),
        "lan_ip": ip,
        "probes": {"loopback": loop, "lan": lan},
        "listeners": lis,
        "spawn": spawn,
        "verdict": verdict,
        "why": why,
        "two_independent_readings": bool(
            lis.get("available") and spawn.get("available")),
        "requirements_for_lan_reach": requirements(verdict),
        "phone_measurable_now": False if verdict != "LAN_REACHABLE" else True,
        "note": ("A measurement taken from THIS host says nothing about the "
                 "phone half of CVM. While the verdict is LOOPBACK_ONLY the "
                 "phone-side latency is UNMEASURED — recorded as absent with a "
                 "reason, never estimated from the desktop numbers."),
        "no_credential_read": True,
    }
    dest = Path(artifact) if artifact else (Path(__file__).resolve().parent
                                            / ARTIFACT)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(rec, indent=1), encoding="utf-8")
    rec["artifact_path"] = str(dest)
    return rec


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="lan-reach")
    ap.add_argument("--root", required=True)
    ap.add_argument("--port", type=int, default=8770)
    ap.add_argument("--artifact", default="")
    ns = ap.parse_args(list(sys.argv[1:] if argv is None else argv))
    rec = run(ns.root, ns.port, ns.artifact or None)
    print(json.dumps(rec, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
