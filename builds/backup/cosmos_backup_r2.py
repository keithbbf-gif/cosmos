#!/usr/bin/env python3
"""cosmos_backup_r2.py — the R2 (Cloudflare) offsite leg for cosmos_backup.

WHY THIS EXISTS: `builds/backup/cosmos_backup.py` proves a backup restores, but
its destination is a directory on the SAME VOLUME as the source. A drive failure
takes both. R2 is the first destination that is not this machine.

WHAT IS IMPLEMENTED HERE, WITHOUT ANY CREDENTIAL:
  * SigV4 request signing (stdlib hmac/hashlib) — R2 speaks the S3 API, so the
    signer is the whole protocol. Pure function, no I/O, no network.
  * `R2Target`, a real `cosmos_backup.BackupTarget` over an INJECTED transport
    (the ITC idiom): production passes `UrllibTransport`, tests and `selfcheck`
    pass `MemoryTransport`. No code path a test exercises can silently reach the
    network, and the whole push→verify pipeline is provable offline.
  * `push()` — manifest → store → RETRIEVE EVERY OBJECT BACK and re-hash. An
    upload that is not read back is not a backup; the proof is the round trip.
  * A secret scan that REFUSES to push a scope containing key material, and a
    credential fence that REFUSES the plaintext key store outright.

WHAT IS NOT AND CANNOT BE HERE: the credential. Keith owns money and keys.
This module never reads, lists, resolves into, or names the contents of the
plaintext store — `FORBIDDEN_PREFIXES` refuses it as a typed error, the same
fence `builds/probe/credential_manifest.py` carries. Secrets are redacted to a
last-4 fingerprint in every repr, log line and artifact this file can emit.

No path is hard-coded: every root, credential path and prefix is a parameter.
Stdlib only (matches its sibling); target runtime `py -3.14` on Windows.

  py -3.14 builds/backup/cosmos_backup_r2.py preflight --source <tree>
  py -3.14 builds/backup/cosmos_backup_r2.py selfcheck --source <tree>
  py -3.14 builds/backup/cosmos_backup_r2.py push --source <tree> \
        --credentials <runtime-root>/config/r2_credentials.json
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import shutil
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import cosmos_backup as cb
from cosmos_backup import BackupRefusal

SERVICE = "s3"
REGION = "auto"                      # R2 has one region and it is spelled "auto"
ALGORITHM = "AWS4-HMAC-SHA256"
EMPTY_SHA256 = hashlib.sha256(b"").hexdigest()
RECEIPT_NAME = "REMOTE_PUSH.json"

# The plaintext key store named in docs/WISHLIST.md. This module must never
# read, list or resolve into it — the same fence credential_manifest.py carries.
FORBIDDEN_PREFIXES = ("d:\\r2cloner", "d:/r2cloner")

REQUIRED_CREDENTIAL_FIELDS = ("account_id", "access_key_id", "secret_access_key", "bucket")

# Paths whose CONTENT is key material. Credential shapes are matched on the
# manifest key only — those files are never opened. PEM-like suffixes are NOT
# in this list: a vendored CA bundle (`cacert.pem`) is public certificates,
# while `*.pem`/`*.key` can also hold a private-key envelope. Classification
# of those suffixes is by BEGIN label (see cosmos_backup.pem_label_kind);
# unknown/unreadable/empty is fail-closed (treated as a hit).
# `.pfx` / `.p12` stay path-hits: PKCS#12 is typically a private-key store
# and is ambiguous without parsing the binary.
SECRET_SUFFIXES = ("_key.txt", "_key.bin", "_credentials.json", "_token.txt",
                   ".pfx", ".p12")
SECRET_NAMES = ("api_token.txt", "install_key.bin", "id_rsa", ".env", ".npmrc")
SECRET_PATH_FRAGMENTS = (".git/config",)
PEM_CLASSIFY_SUFFIXES = cb.PEM_CLASSIFY_SUFFIXES


# ------------------------------------------------------------------ credentials

class R2Credentials:
    """Credential holder that cannot leak. `repr`/`str`/`asdict` carry a last-4
    FINGERPRINT of the access key id and nothing else — the secret has no
    accessor that renders it, only `.sign()` consumes it."""

    __slots__ = ("account_id", "access_key_id", "_secret", "bucket", "endpoint",
                 "region", "service")

    def __init__(self, account_id: str, access_key_id: str, secret_access_key: str,
                 bucket: str, endpoint: str | None = None,
                 region: str = REGION, service: str = SERVICE):
        for name, val in (("account_id", account_id), ("access_key_id", access_key_id),
                          ("secret_access_key", secret_access_key), ("bucket", bucket)):
            if not isinstance(val, str) or not val.strip():
                raise BackupRefusal("BAD_CREDENTIALS", f"field {name!r} is empty or not a string")
        self.account_id = account_id.strip()
        self.access_key_id = access_key_id.strip()
        self._secret = secret_access_key.strip()
        self.bucket = bucket.strip()
        self.endpoint = (endpoint or f"https://{self.account_id}.r2.cloudflarestorage.com").rstrip("/")
        # Carried on the credential, not baked into the signer, so the pure signer
        # can be run against AWS's published SigV4 vectors (region/service differ there).
        self.region, self.service = region, service

    @property
    def fingerprint(self) -> str:
        """Last 4 of the ACCESS KEY ID (public half). Never the secret."""
        return "…" + self.access_key_id[-4:]

    def asdict(self) -> dict:
        return {"account_id_fingerprint": "…" + self.account_id[-4:],
                "access_key_id_fingerprint": self.fingerprint,
                "bucket": self.bucket, "endpoint": self.endpoint,
                "secret_access_key": "<redacted — never emitted>"}

    def __repr__(self) -> str:
        return (f"R2Credentials(bucket={self.bucket!r}, access_key_id={self.fingerprint!r}, "
                "secret=<redacted>)")

    __str__ = __repr__

    def sign(self, string_to_sign: str, datestamp: str) -> str:
        k = ("AWS4" + self._secret).encode("utf-8")
        for part in (datestamp, self.region, self.service, "aws4_request"):
            k = hmac.new(k, part.encode("utf-8"), hashlib.sha256).digest()
        return hmac.new(k, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()


def guard_credential_path(path: Path) -> Path:
    """Fail-closed fence: the plaintext key store is never a legal source."""
    s = str(Path(path)).replace("/", "\\").lower()
    for bad in FORBIDDEN_PREFIXES:
        if s.startswith(bad.replace("/", "\\")):
            raise BackupRefusal("FORBIDDEN_CREDENTIAL_PATH",
                                f"{path} is inside a plaintext key store this tool never touches")
    return Path(path)


def load_credentials(path: Path) -> R2Credentials:
    """Read a credential JSON. Every failure message names the FIELD, never a value."""
    p = guard_credential_path(path)
    if not p.is_file():
        raise BackupRefusal("NO_CREDENTIALS", f"no credential file at {p} "
                                              "(Keith places it; COSMOS opens the door)")
    try:
        obj = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise BackupRefusal("BAD_CREDENTIALS", f"{p} is not readable JSON: {type(e).__name__}") from e
    if not isinstance(obj, dict):
        raise BackupRefusal("BAD_CREDENTIALS", f"{p} is not a JSON object")
    missing = [f for f in REQUIRED_CREDENTIAL_FIELDS if f not in obj]
    if missing:
        raise BackupRefusal("BAD_CREDENTIALS", f"{p} is missing field(s): {', '.join(missing)}")
    return R2Credentials(obj["account_id"], obj["access_key_id"], obj["secret_access_key"],
                         obj["bucket"], obj.get("endpoint"))


# ------------------------------------------------------------------ SigV4

def _canonical_uri(key: str) -> str:
    # Path-style: /<bucket>/<key>. Each segment percent-encoded, "/" preserved.
    return "/" + "/".join(urllib.parse.quote(seg, safe="") for seg in key.split("/") if seg != "")


def canonical_request(method: str, canonical_uri: str, headers: dict,
                      payload_sha256: str) -> tuple[str, str]:
    """(canonical request, signed-header list). Pure. Split out from `sigv4_headers`
    so the AWS published SigV4 vectors — which sign a DIFFERENT header set than an
    R2 object PUT — can be driven through the same code the wire uses."""
    if not isinstance(headers, dict):
        raise BackupRefusal(
            "BAD_HEADERS",
            f"headers is {type(headers).__name__}, not an object")
    low = {k.lower(): str(v).strip() for k, v in headers.items()}
    signed = ";".join(sorted(low))
    canonical_headers = "".join(f"{k}:{low[k]}\n" for k in sorted(low))
    return ("\n".join([method, canonical_uri, "", canonical_headers, signed, payload_sha256]),
            signed)


def sign_request(creds: R2Credentials, canonical: str, amzdate: str) -> tuple[str, str]:
    """(signature, credential scope) for an already-canonicalised request. Pure."""
    datestamp = amzdate[:8]
    scope = f"{datestamp}/{creds.region}/{creds.service}/aws4_request"
    string_to_sign = "\n".join([ALGORITHM, amzdate, scope,
                                hashlib.sha256(canonical.encode("utf-8")).hexdigest()])
    return creds.sign(string_to_sign, datestamp), scope


def sigv4_headers(method: str, host: str, canonical_uri: str, payload_sha256: str,
                  creds: R2Credentials, now: datetime,
                  extra_headers: dict | None = None) -> dict:
    """Return the signed headers for one request. Pure: no I/O, no clock, no network.

    `now` is injected rather than read so a test can pin the timestamp — a signer
    that reads its own clock is untestable.
    """
    amzdate = now.strftime("%Y%m%dT%H%M%SZ")
    headers = {"host": host, "x-amz-content-sha256": payload_sha256, "x-amz-date": amzdate}
    headers.update({k.lower(): v for k, v in (extra_headers or {}).items()})
    canonical, signed = canonical_request(method, canonical_uri, headers, payload_sha256)
    signature, scope = sign_request(creds, canonical, amzdate)
    out = {k: v for k, v in headers.items() if k != "host"}
    out["Authorization"] = (f"{ALGORITHM} Credential={creds.access_key_id}/{scope}, "
                            f"SignedHeaders={signed}, Signature={signature}")
    return out


# ------------------------------------------------------------------ transports

class Transport:
    """Injected byte mover. `request` returns (status, headers, body)."""

    def request(self, method: str, url: str, headers: dict, body: bytes | None = None):
        raise NotImplementedError


class UrllibTransport(Transport):
    """The only code path in this file that can reach the network."""

    def __init__(self, timeout: int = 120):
        self.timeout = timeout

    def request(self, method, url, headers, body=None):
        req = urllib.request.Request(url, data=body, method=method, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                return r.status, dict(r.headers), r.read()
        except urllib.error.HTTPError as e:
            return e.code, dict(e.headers or {}), e.read()
        except OSError as e:
            raise BackupRefusal("R2_UNREACHABLE", f"{method} failed: {type(e).__name__}: {e}") from e


class MemoryTransport(Transport):
    """An in-memory bucket. Lets the FULL push→retrieve→re-hash pipeline run with
    zero credentials and zero network, so everything except the wire is proven."""

    def __init__(self):
        self.objects: dict[str, bytes] = {}
        self.calls: list[tuple[str, str]] = []

    def request(self, method, url, headers, body=None):
        key = url.split("://", 1)[-1].split("/", 1)[-1]
        self.calls.append((method, key))
        if method == "PUT":
            self.objects[key] = body or b""
            return 200, {}, b""
        if method == "GET":
            if key not in self.objects:
                return 404, {}, b"<Error><Code>NoSuchKey</Code></Error>"
            return 200, {}, self.objects[key]
        return 405, {}, b""


# ------------------------------------------------------------------ target

def safe_rel(rel: str) -> str:
    """Validate a manifest key for use as an object key. Same rule and same typed
    refusal as `cosmos_backup._child`; a test asserts the two agree, because two
    containment checks that drift are worse than one."""
    r = str(rel).replace("\\", "/")
    parts = tuple(p for p in r.split("/") if p)
    if not parts or r.startswith("/") or ".." in parts or (len(r) > 1 and r[1] == ":"):
        raise BackupRefusal("UNSAFE_MANIFEST_KEY",
                            f"manifest key {rel!r} is empty, absolute or traverses")
    return "/".join(parts)


class R2Target(cb.BackupTarget):
    """`cosmos_backup.BackupTarget` over the S3 API. Verification stays in the daemon."""

    def __init__(self, creds: R2Credentials, prefix: str, transport: Transport | None = None):
        if transport is None:
            raise BackupRefusal("NO_TRANSPORT", "R2Target requires an injected transport "
                                                "(UrllibTransport for the wire, MemoryTransport offline)")
        self.creds = creds
        self.prefix = safe_rel(prefix)
        self.transport = transport
        self.host = creds.endpoint.split("://", 1)[-1]

    def key_for(self, rel: str) -> str:
        return f"{self.prefix}/{safe_rel(rel)}"

    def _call(self, method: str, rel_key: str, body: bytes | None, payload_sha: str) -> bytes:
        key = f"{self.creds.bucket}/{rel_key}"
        uri = _canonical_uri(key)
        headers = sigv4_headers(method, self.host, uri, payload_sha, self.creds,
                                datetime.now(timezone.utc))
        status, _hdrs, resp = self.transport.request(method, self.creds.endpoint + uri, headers, body)
        if status == 404:
            raise BackupRefusal("R2_OBJECT_MISSING", f"{method} {rel_key}: 404")
        if not 200 <= status < 300:
            # The body can echo the request; never let it carry a credential out.
            raise BackupRefusal("R2_HTTP_ERROR", f"{method} {rel_key}: HTTP {status}")
        return resp

    # MAX_PATH, on BOTH sides of the wire (measured 2026-08-31, docs/LONGPATH_FINDING.md).
    # `cosmos_backup` walks and hashes through the `\\?\` prefix, so build_manifest
    # happily lists a 300-char file that a plain open() cannot touch. These two methods
    # are where the manifest turns back into filesystem calls, and both were plain:
    #   store()     re-READS the source by name  -> FileNotFoundError winerror=3
    #   retrieve()  WRITES the read-back copy    -> the destination side, which needs the
    #               prefix independently: a SHORT scratch root plus a 240-char manifest
    #               key is a long path even when the source root was short.
    # Untyped crashes from a module whose contract is typed refusals, and they would have
    # fired on the first push of V:\Ai (2,125 long paths). Pinned by test_longpath_r2.py.
    def store(self, rel: str, src: Path) -> None:
        with open(cb._x(src), "rb") as fh:
            data = fh.read()
        self._call("PUT", self.key_for(rel), data, hashlib.sha256(data).hexdigest())

    def retrieve(self, rel: str, dst: Path) -> None:
        data = self._call("GET", self.key_for(rel), None, EMPTY_SHA256)
        os.makedirs(cb._x(Path(dst).parent), exist_ok=True)
        with open(cb._x(dst), "wb") as fh:
            fh.write(data)

    def put_artifact(self, name: str, obj: dict) -> None:
        data = json.dumps(obj, indent=2, sort_keys=True).encode("utf-8")
        self._call("PUT", f"{self.prefix}/{safe_rel(name)}", data,
                   hashlib.sha256(data).hexdigest())

    def get_artifact(self, name: str) -> dict:
        raw = self._call("GET", f"{self.prefix}/{safe_rel(name)}",
                         None, EMPTY_SHA256)
        try:
            obj = json.loads(raw.decode("utf-8"))
        except (ValueError, UnicodeDecodeError) as e:
            raise BackupRefusal("NOT_A_BACKUP_SET",
                                f"{name} is not readable JSON: {type(e).__name__}") from e
        if not isinstance(obj, dict):
            raise BackupRefusal("NOT_A_BACKUP_SET",
                                f"{name} is not a JSON object")
        return obj


# ------------------------------------------------------------------ secret scan

def scan_secrets(manifest: dict) -> list[str]:
    """Manifest keys whose CONTENT is key material. Prints no value.

    Credential path-shapes refuse by name and are never opened. PEM-like
    suffixes are classified by BEGIN label against source_root: public-only
    certificates are not hits; private-key envelopes are; missing source_root,
    missing file, empty file, or unknown label is a hit (fail-closed).

    manifest.files must be an object of rel-path keys. A JSON array, a
    string (iterates characters and returns [] — the green-log), None,
    or a missing files field is NOT_A_BACKUP_SET, never KeyError /
    TypeError / a silent empty hit-list. Bite `_bite_unpinned_round6.json`.
    """
    if not isinstance(manifest, dict):
        raise BackupRefusal("NOT_A_BACKUP_SET", "manifest is not a JSON object")
    files = manifest.get("files")
    if not isinstance(files, dict):
        raise BackupRefusal(
            "NOT_A_BACKUP_SET",
            f"manifest.files is {type(files).__name__}, not an object")
    root = None
    raw_root = manifest.get("source_root")
    if isinstance(raw_root, str) and raw_root.strip():
        root = Path(raw_root)
    hits = []
    for rel in files:
        if not isinstance(rel, str):
            raise BackupRefusal(
                "NOT_A_BACKUP_SET",
                f"manifest.files key is {type(rel).__name__}, not a path")
        low = rel.replace("\\", "/").lower()
        name = low.rsplit("/", 1)[-1]
        if (name in SECRET_NAMES or low.endswith(SECRET_SUFFIXES)
                or any(f in low for f in SECRET_PATH_FRAGMENTS)):
            hits.append(rel)
            continue
        if not low.endswith(PEM_CLASSIFY_SUFFIXES):
            continue
        # Fail-closed: a PEM-like name we cannot classify is a hit.
        if root is None:
            hits.append(rel)
            continue
        try:
            p = cb._child(root, rel)
        except BackupRefusal:
            hits.append(rel)
            continue
        if cb.classify_pem_file(p) != "public":
            hits.append(rel)
    return sorted(hits)


# ------------------------------------------------------------------ push

def push(source_root: Path, target: R2Target, excludes=cb.DEFAULT_EXCLUDES,
         key: bytes | None = None, scratch: Path | None = None) -> dict:
    """manifest → store → RETRIEVE EVERY OBJECT BACK → re-hash → sealed receipt.

    The read-back is the point. An upload nobody reads is a claim; a re-hashed
    round trip is the artifact. Refuses before the first byte if the scope holds
    key material, because off-machine storage inherits every exposure in it.
    """
    source_root = Path(source_root).resolve()
    manifest = cb.build_manifest(source_root, excludes)
    offenders = scan_secrets(manifest)
    if offenders:
        raise BackupRefusal(
            "SECRETS_IN_SCOPE",
            f"{len(offenders)} file(s) in scope hold key material and this target is "
            f"UNENCRYPTED: {', '.join(offenders[:5])}"
            f"{' …' if len(offenders) > 5 else ''} — exclude them or encrypt first")
    if scratch is None:
        raise BackupRefusal("NO_SCRATCH", "push needs an explicit read-back scratch dir "
                                          "(no path is invented for you)")
    # Store, then prove by reading back into scratch and re-hashing — not by trusting the PUT.
    for rel in manifest["files"]:
        target.store(rel, cb._child(source_root, rel))
    scratch = Path(scratch)
    # Prefixed, like do_rehearse's guard: a scratch holding only long-path leftovers
    # would look EMPTY to a plain listdir, and the guard would wave through a dir the
    # read-back is about to write into. A guard that cannot see is not a guard.
    if cb._xisdir(scratch) and os.listdir(cb._x(scratch)):
        raise BackupRefusal("SCRATCH_NOT_EMPTY", f"read-back scratch not empty: {scratch}")
    cb._xmkdirs(scratch)
    bad = cb._check(manifest, lambda rel: cb._child(scratch, rel),
                    produce=lambda rel, p: target.retrieve(rel, p))
    if bad:
        raise BackupRefusal("R2_HASH_MISMATCH",
                            f"{len(bad)} object(s) read back from R2 fail re-hash")
    sealed = cb.seal(manifest, key)
    target.put_artifact(cb.MANIFEST_NAME, sealed)
    receipt = cb.seal({"format": cb.FORMAT, "kind": "R2_PUSH_OK",
                       "at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                       "source_root": str(source_root), "prefix": target.prefix,
                       "target": target.creds.asdict(),
                       "files_pushed": len(manifest["files"]),
                       "bytes_pushed": manifest["total_bytes"],
                       "readback_verified": len(manifest["files"]),
                       "manifest_seal_sha256": sealed["seal"]["sha256"]}, key)
    target.put_artifact(RECEIPT_NAME, receipt)
    return receipt


# ------------------------------------------------------------------ preflight

def preflight(source: Path | None, credentials: Path | None) -> dict:
    """What is configured vs missing, measured. No network, no credential read
    beyond shape, no value ever rendered."""
    import importlib.util
    blockers, notes = [], []
    cred_state, cred_detail = "ABSENT", None
    if credentials is not None:
        try:
            creds = load_credentials(Path(credentials))
            cred_state, cred_detail = "PRESENT", creds.asdict()
        except BackupRefusal as e:
            cred_state, cred_detail = e.kind, e.detail
    if cred_state != "PRESENT":
        blockers.append("R2 credential absent or unusable — Keith places "
                        "r2_credentials.json {account_id, access_key_id, secret_access_key, bucket} "
                        "under the runtime root's config role")
    scope = None
    if source is not None:
        try:
            m = cb.build_manifest(Path(source))
            offenders = scan_secrets(m)
            scope = {"files": m["file_count"], "bytes": m["total_bytes"],
                     "secrets_in_scope": offenders}
            if offenders:
                blockers.append(f"{len(offenders)} file(s) in scope hold key material; "
                                "exclude them (this target is unencrypted)")
        except BackupRefusal as e:
            scope = {"refused": e.kind, "detail": e.detail}
            blockers.append(f"scope unreadable: {e.kind}")
    for mod in ("boto3", "botocore"):
        if importlib.util.find_spec(mod) is None:
            notes.append(f"{mod} NOT installed — not needed: signing is stdlib here")
    for exe in ("rclone", "aws"):
        if shutil.which(exe) is None:
            notes.append(f"{exe} NOT on PATH — not needed: no external tool is invoked")
    return {"format": cb.FORMAT, "kind": "R2_PREFLIGHT",
            "at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "adapter_implemented": True, "signing": "SigV4 (stdlib hmac/hashlib)",
            "region": REGION, "credential": {"state": cred_state, "detail": cred_detail},
            "scope": scope, "notes": notes, "blockers": blockers,
            "status": "READY" if not blockers else "BLOCKED"}


SELFCHECK_ID = "SELFCHECK-NOT-A-CREDENTIAL"


def selfcheck(source: Path, scratch: Path, key: bytes | None = None) -> dict:
    """Run the ENTIRE R2 code path — sign, PUT, GET, re-hash, seal — against an
    in-memory bucket with an obviously-fake credential. Proves everything except
    the wire, with nothing to leak."""
    creds = R2Credentials("selfcheckaccount", SELFCHECK_ID, SELFCHECK_ID, "selfcheck-bucket")
    tp = MemoryTransport()
    receipt = push(Path(source), R2Target(creds, "selfcheck", tp), key=key, scratch=Path(scratch))
    return {**receipt, "transport": "MemoryTransport", "objects": len(tp.objects),
            "requests": len(tp.calls)}


# ------------------------------------------------------------------ CLI

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--key-file", help="optional HMAC key file for sealing artifacts")
    sub = ap.add_subparsers(dest="cmd", required=True)

    pf = sub.add_parser("preflight", help="what is configured vs missing (no network)")
    pf.add_argument("--source")
    pf.add_argument("--credentials")

    sc = sub.add_parser("selfcheck", help="prove the R2 path offline against a memory bucket")
    sc.add_argument("--source", required=True)
    sc.add_argument("--scratch", required=True)

    ps = sub.add_parser("push", help="push a tree to R2 and read every object back")
    ps.add_argument("--source", required=True)
    ps.add_argument("--credentials", required=True)
    ps.add_argument("--prefix", required=True)
    ps.add_argument("--scratch", required=True)
    ps.add_argument("--exclude", action="append", default=list(cb.DEFAULT_EXCLUDES))

    args = ap.parse_args(argv)
    key = Path(args.key_file).read_bytes().strip() if args.key_file else None
    try:
        if args.cmd == "preflight":
            out = preflight(Path(args.source) if args.source else None,
                            Path(args.credentials) if args.credentials else None)
        elif args.cmd == "selfcheck":
            out = selfcheck(Path(args.source), Path(args.scratch), key)
        else:
            creds = load_credentials(Path(args.credentials))
            out = push(Path(args.source), R2Target(creds, args.prefix, UrllibTransport()),
                       tuple(args.exclude), key, Path(args.scratch))
    except BackupRefusal as e:
        print(json.dumps({"refused": True, "kind": e.kind, "detail": e.detail}), file=sys.stderr)
        return 2
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
