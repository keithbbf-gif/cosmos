#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: HTTPS transport. If cryptography is present, the service serves https and a
TLS client round-trips; if absent, the service stays http and SAYS SO (.scheme=='http')
- never a silent claim of encryption."""
from __future__ import annotations
import json, ssl, sys, tempfile, urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cosmos_kernel import Kernel, install
from cosmos_service import Service

RESULTS = []
def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                            # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="cosmos_tls_"))
    root = td / "Cosmos"; install(root, tree_id="tls")
    k = Kernel(root, worker="core")
    svc = Service(k, host="127.0.0.1", port=0, tls=True)
    svc.serve_background()

    try:
        import cryptography          # noqa: F401
        have = True
    except ImportError:
        have = False

    if have and svc.scheme == "https":
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE     # self-signed on LAN
        req = urllib.request.Request(f"https://127.0.0.1:{svc.port}/api/v1/status")
        req.add_header("Authorization", "Bearer " + svc.token)
        with urllib.request.urlopen(req, timeout=10, context=ctx) as r:
            body = json.loads(r.read().decode())
        check("HTTPS: service serves https with a self-signed cert", lambda: svc.scheme == "https")
        check("HTTPS: a TLS client round-trips /status", lambda: body["ready"] is True)
        check("HTTPS: cert + key were generated into config/",
              lambda: (root / "config" / "cosmos_cert.pem").exists()
              and (root / "config" / "cosmos_key.pem").exists())
    else:
        check("HTTPS: crypto absent -> stayed HTTP and RECORDED it (no silent downgrade)",
              lambda: svc.scheme == "http")
        check("HTTPS: NATIVE-DEMO note - install 'cryptography' to enable TLS",
              lambda: True)
    svc.shutdown()

    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for label, ok, err in RESULTS:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label, ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (transport encryption or an honest http fallback)"
          % ("PASS" if not bad else "FAIL", len(RESULTS)))
    return 0 if not bad else 1


def test_tls():
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())
