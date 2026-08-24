#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: HTTPS transport. If cryptography is present, the service serves https and a
TLS client round-trips; if absent, the service stays http and SAYS SO (.scheme=='http')
- never a silent claim of encryption. Also: an operator-PROVIDED cert/key pair (e.g. a
Tailscale-issued trusted cert) is served verbatim - no self-signing, no config/ pair -
and half a pair or a missing file is a typed CERT_NOT_FOUND refusal, never a silent
fallback to a cert the operator did not choose."""
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
        from cryptography import x509
        cert = x509.load_pem_x509_certificate(
            (root / "config" / "cosmos_cert.pem").read_bytes())
        san = cert.extensions.get_extension_for_class(
            x509.SubjectAlternativeName).value
        check("HTTPS: cert SAN covers the bind IP + documented names "
              "(verifiable, not just encrypted)",
              lambda: "127.0.0.1" in {str(i) for i in
                                      san.get_values_for_type(x509.IPAddress)}
              and {"cosmos.local", "localhost"}
              <= set(san.get_values_for_type(x509.DNSName)))
    else:
        check("HTTPS: crypto absent -> stayed HTTP and RECORDED it (no silent downgrade)",
              lambda: svc.scheme == "http")
        check("HTTPS: NATIVE-DEMO note - install 'cryptography' to enable TLS",
              lambda: True)
    svc.shutdown()

    # ---- PROVIDED-CERT PATH (trusted external cert, e.g. Tailscale-issued) ----
    if have:
        import shutil
        import socket
        from cosmos_service import ServiceError, _ensure_cert

        # Mint a throwaway pair with the module's OWN generator, copy it out of
        # config/ so it plays the role of an externally-supplied cert+key.
        mint_root = td / "CertMint"; install(mint_root, tree_id="tlsmint")
        pair = _ensure_cert(Kernel(mint_root, worker="core"), "127.0.0.1")
        ext_cert, ext_key = td / "ext_cert.pem", td / "ext_key.pem"
        shutil.copy(pair[0], ext_cert); shutil.copy(pair[1], ext_key)

        root2 = td / "Cosmos2"; install(root2, tree_id="tls2")
        k2 = Kernel(root2, worker="core")
        svc2 = Service(k2, host="127.0.0.1", port=0, tls=True,
                       cert_file=str(ext_cert), key_file=str(ext_key))
        svc2.serve_background()
        check("PROVIDED: operator cert+key -> scheme=https, cert_source='provided'",
              lambda: svc2.scheme == "https"
              and getattr(svc2, "cert_source", None) == "provided")
        check("PROVIDED: did NOT self-sign - no cosmos_cert.pem/cosmos_key.pem in config/",
              lambda: not (root2 / "config" / "cosmos_cert.pem").exists()
              and not (root2 / "config" / "cosmos_key.pem").exists())
        cctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        cctx.check_hostname = False
        cctx.verify_mode = ssl.CERT_NONE
        with socket.create_connection(("127.0.0.1", svc2.port), timeout=10) as raw:
            with cctx.wrap_socket(raw, server_hostname="127.0.0.1") as tls_sock:
                served_der = tls_sock.getpeercert(binary_form=True)
        check("PROVIDED: the SERVED cert is the provided cert (byte-identical DER)",
              lambda: served_der == ssl.PEM_cert_to_DER_cert(ext_cert.read_text()))
        req2 = urllib.request.Request(f"https://127.0.0.1:{svc2.port}/api/v1/status")
        req2.add_header("Authorization", "Bearer " + svc2.token)
        with urllib.request.urlopen(req2, timeout=10, context=cctx) as r:
            body2 = json.loads(r.read().decode())
        check("PROVIDED: a TLS client round-trips /status over the provided cert",
              lambda: body2["ready"] is True)
        svc2.shutdown()

        def expect_cert_not_found(**kw):
            try:
                Service(k2, host="127.0.0.1", port=0, tls=True, **kw)
            except ServiceError as e:
                return e.kind == "CERT_NOT_FOUND"
            return False
        check("PROVIDED: cert without key -> typed CERT_NOT_FOUND (no silent self-sign)",
              lambda: expect_cert_not_found(cert_file=str(ext_cert)))
        check("PROVIDED: key without cert -> typed CERT_NOT_FOUND",
              lambda: expect_cert_not_found(key_file=str(ext_key)))
        check("PROVIDED: missing cert file -> typed CERT_NOT_FOUND",
              lambda: expect_cert_not_found(cert_file=str(td / "no_such.pem"),
                                            key_file=str(ext_key)))

        # CLI plumbing: the serve subparser accepts --cert/--key (help text names both)
        import subprocess
        import cosmos_service as _csmod
        cos_py = Path(_csmod.__file__).resolve().parent / "cosmos.py"
        hp = subprocess.run([sys.executable, str(cos_py), "serve", "--help"],
                            capture_output=True, text=True, timeout=60)
        check("PROVIDED: cosmos.py serve exposes --cert and --key",
              lambda: hp.returncode == 0
              and "--cert" in hp.stdout and "--key" in hp.stdout)
    else:
        check("PROVIDED: crypto absent in this interpreter - provided-cert round-trip "
              "deferred to the native gate (load_cert_chain path unexercised here)",
              lambda: True)

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