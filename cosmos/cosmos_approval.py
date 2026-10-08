#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_approval - the ACTION approval gate (COSMOS_next, 2026-09-17).

Borrowed from Hermes Agent's tools/approval.py (dangerous-pattern detection + content
scan + approve/deny through a gateway + session/permanent allowlists) and re-shaped for
COSMOS canon:

  * FAIL-CLOSED. There is no `off` and no `yolo` mode. An unclassified action is CONFIRM.
  * HARDLINE never moves. No principal, no allowlist, no Captain grant runs a HARDLINE
    action (delete outside _delme, force push, pipe-to-shell from the network, writes to
    the ledger or key material, disabling defences...). The canon's "never delete" and
    "keys are Keith's" become refusals, not reminders.
  * THE LEDGER IS THE AUTHORITY. Every classification that matters is an event:
    APPROVAL_REQUESTED / GRANTED / DENIED / CONSUMED / REFUSED / ALLOWLISTED. State is a
    projection (Ledger.fold_cached).
  * SINGLE-USE, ACTION-BOUND NONCES. A grant issues a nonce whose sha256 (never the
    nonce) is ledgered, bound to the sha256 of the exact action requested. A replay, an
    edited command, or an expired grant refuses.
  * NO SELF-APPROVAL. Only a `captain:*` principal approves, and never its own request.
  * SILENCE IS NOT CONSENT. A request that is not granted within its TTL is expired.

An action is a small dict: {"kind": shell|git|file_write|file_delete|http|publish|spend|
install|other, "command"?: str, "path"?: str, "url"?: str, "detail"?: str}.

    py -3.14 cosmos\\cosmos_approval.py --selftest   (see tests/test_hermes_features.py)
"""
from __future__ import annotations

import hashlib
import json
import re
import secrets
import time
import unicodedata
from pathlib import Path
from typing import Callable, Optional

SCHEMA = "cosmos-approval/1"
HARDLINE, CONFIRM, ALLOW = "HARDLINE", "CONFIRM", "ALLOW"
_RANK = {ALLOW: 0, CONFIRM: 1, HARDLINE: 2}
KINDS = ("shell", "git", "file_write", "file_delete", "http", "publish", "spend",
         "install", "other")
REQUEST_TTL_S = 900.0
FOLD = "cosmos_approval.v1"

_I = re.IGNORECASE

# (rule id, action kinds or None for any, regex over the searchable text, why)
HARDLINE_RULES = (
    ("delete-outside-delme", ("file_delete",), None,
     "COSMOS never deletes: stage to _delme\\ (AGENT_BOUNDARIES item 4)"),
    ("shell-recursive-delete", ("shell",),
     re.compile(r"\brm\s+-[a-z]*r[a-z]*f|\brm\s+-[a-z]*f[a-z]*r"
                r"|\brm\b[^\n]*?(?:--recursive\b|-[a-z]*r\b)[^\n]*?(?:--force\b|-[a-z]*f\b)"
                r"|\brm\b[^\n]*?(?:--force\b|-[a-z]*f\b)[^\n]*?(?:--recursive\b|-[a-z]*r\b)"
                r"|\brmdir\s+/s\b|\bdel\s+/[sq]"
                r"|remove-item\b[^\n]*-recurse|\bshred\b|\bsdelete\b", _I),
     "recursive delete from a shell - never delete, stage to _delme\\"),
    ("disk-destroy", ("shell",),
     re.compile(r"\bformat\s+[a-z]:|\bdiskpart\b|\bmkfs\b|\bdd\s+if=|clear-disk\b"
                r"|initialize-disk\b", _I),
     "disk-level destruction"),
    ("force-push", ("git", "shell"),
     re.compile(r"\bgit\b[^\n]*\bpush\b[^\n]*(--force\b|--force-with-lease\b|\s-f+\b)"
                r"|\bgit\b[^\n]*\bpush\b[^\n]*\s\+\S+", _I),
     "force push rewrites shared history (CCR.md: do not force-push)"),
    ("pipe-to-interpreter", ("shell",),
     re.compile(r"(curl|wget|iwr|irm|invoke-webrequest|invoke-restmethod)\b[^\n|;]*\|\s*"
                r"(?:sudo\s+)?(?:sh|bash|zsh|python\d*|py|node|iex|invoke-expression|pwsh|powershell)\b"
                r"|\b(?:iex|invoke-expression)\s*\(\s*(?:irm|iwr|invoke-restmethod|invoke-webrequest)\b",
                _I),
     "executes code fetched from the network"),
    ("encoded-command", ("shell",),
     re.compile(r"\b(powershell|pwsh)(\.exe)?\b[^\n]*\s-e(nc(odedcommand)?)?\s+[A-Za-z0-9+/=]{16,}"
                r"|base64\s+(-d|--decode)\b[^\n]*\|\s*(sh|bash)", _I),
     "encoded / decoded-and-executed command hides what runs"),
    ("ledger-or-key-write", ("file_write", "file_delete", "shell"),
     re.compile(r"(^|[\\/])live[\\/]ledger[\\/]|install_key\.bin|api_token\.txt"
                r"|kill_token\.txt|[\\/]\.secrets[\\/]|_key\.txt\b|\.pem\b|id_rsa|id_ed25519",
                _I),
     "authority ledger and key material are Core's / Keith's alone"),
    ("secret-exfil", ("shell", "http"),
     re.compile(r"(install_key|api_token|_key\.txt|\.pem|id_rsa|\.secrets)[^\n]*"
                r"(curl|wget|invoke-webrequest|invoke-restmethod|iwr|irm|scp|ftp)\b"
                r"|(curl|wget|invoke-webrequest|invoke-restmethod|iwr|irm|scp)\b[^\n]*"
                r"(install_key|api_token|_key\.txt|\.pem|id_rsa|\.secrets)", _I),
     "key material leaving the machine"),
    ("defence-off", ("shell",),
     re.compile(r"set-mppreference\b[^\n]*-disable|\bbcdedit\b|\bvssadmin\s+delete\b"
                r"|\bwevtutil\s+cl\b|netsh\s+advfirewall\s+set\b[^\n]*\boff\b", _I),
     "disables defences, recovery or logs"),
    ("registry-machine-delete", ("shell",),
     re.compile(r"\breg\s+delete\s+hklm|remove-item(property)?\b[^\n]*hklm:", _I),
     "machine registry deletion"),
)

CONFIRM_RULES = (
    ("git-push", ("git", "shell"), re.compile(r"\bgit\b[^\n]*\bpush\b", _I), "publishes commits"),
    ("pr-merge", ("git", "shell"),
     re.compile(r"\b(gh|glab)\s+(pr|mr)\s+merge\b", _I), "merges a PR / MR"),
    ("package-install", ("install", "shell"),
     re.compile(r"\b(pip|pip3|npm|pnpm|yarn|winget|choco|scoop|cargo)\s+(install|add|i)\b"
                r"|\bnpx\s+", _I), "installs third-party code"),
    ("package-publish", ("publish", "shell"),
     re.compile(r"\b(npm|pnpm|twine|cargo)\s+publish\b", _I), "publishes a package"),
    ("scheduled-task", ("shell",),
     re.compile(r"\bschtasks\s+/(create|change|delete)\b|register-scheduledtask\b", _I),
     "changes a native clock"),
    ("live-prove", ("shell", "other"), re.compile(r"--live\b", _I), "paid live prove"),
    ("git-history", ("git", "shell"),
     re.compile(r"\bgit\s+(reset\s+--hard|clean\s+-[a-z]*f|rebase\b|branch\s+-D)", _I),
     "discards or rewrites local work"),
)

ALWAYS_CONFIRM_KINDS = ("publish", "spend", "http", "install")


class ApprovalError(RuntimeError):
    """kind in {HARDLINE, NEEDS_APPROVAL, BAD_ACTION, NO_REQUEST, NOT_APPROVER,
    SELF_APPROVAL, EXPIRED, BAD_NONCE, ACTION_MISMATCH, DENIED, ALREADY_DECIDED}."""

    def __init__(self, kind: str, detail: str, **extra):
        self.kind = kind
        self.extra = extra
        super().__init__(f"[{kind}] {detail}")


def _sha(obj) -> str:
    if not isinstance(obj, (bytes, str)):
        obj = json.dumps(obj, sort_keys=True, separators=(",", ":"))
    if isinstance(obj, str):
        obj = obj.encode("utf-8")
    return hashlib.sha256(obj).hexdigest()


def normalize_action(action) -> dict:
    if not isinstance(action, dict):
        raise ApprovalError("BAD_ACTION", "action must be an object")
    kind = str(action.get("kind") or "").strip().lower()
    if kind not in KINDS:
        raise ApprovalError("BAD_ACTION", f"kind {kind!r} not in {KINDS}")
    out = {"kind": kind}
    for k in ("command", "path", "url", "detail"):
        v = action.get(k)
        if v is not None:
            if not isinstance(v, str):
                raise ApprovalError("BAD_ACTION", f"{k} must be a string")
            out[k] = v
    return out


def _text(a: dict) -> str:
    return "\n".join(a.get(k, "") for k in ("command", "path", "url", "detail"))


def content_scan(a: dict) -> list[str]:
    """Findings that can only RAISE a class (Hermes' Tirith role)."""
    t = _text(a)
    found = []
    if any(ch in t for ch in ("\u200B", "\u200C", "\u200D", "\u2060", "\uFEFF")):
        found.append("zero-width characters hide text")
    if any(unicodedata.bidirectional(ch) in ("RLO", "LRO", "RLE", "LRE", "RLI", "LRI", "FSI")
           for ch in t):
        found.append("bidirectional override reorders what is displayed")
    for host in re.findall(r"[a-z][a-z0-9+.-]*://([^/\s:?#]+)", t, _I):
        if any(ord(ch) > 127 for ch in host):
            found.append(f"non-ASCII hostname {host!r} (homoglyph risk)")
    if re.search(r"[A-Za-z0-9+/]{200,}={0,2}", t):
        found.append("long base64 blob")
    return found


def _for_rules(text: str) -> str:
    """Text the rule regexes see. NFKC folds fullwidth lookalikes; format
    characters (zero-width, bidi) are removed so they cannot hide a match.
    content_scan still reads the raw action and can only raise the class."""
    folded = unicodedata.normalize("NFKC", text)
    return "".join(ch for ch in folded if unicodedata.category(ch) != "Cf")


def _canon_principal(name: object) -> str:
    text = unicodedata.normalize("NFKC", "" if name is None else str(name))
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Cf")
    return text.strip()


def _is_captain(name: object) -> bool:
    return str("" if name is None else name).startswith("captain:")


def _same_principal(a: object, b: object) -> bool:
    left, right = _canon_principal(a), _canon_principal(b)
    return bool(left) and left == right


def _is_anchor(part: str) -> bool:
    if part in ("/", "\\") or part.endswith(("/", "\\")):
        return True
    return len(part) == 2 and part[1] == ":" and part[0].isalpha()


def _lexical_parts(path: str) -> list[str]:
    raw = path
    if raw.startswith("\\\\?\\UNC\\") or raw.startswith("//?/UNC/"):
        raw = "\\\\" + raw[8:]
    elif raw.startswith("\\\\?\\") or raw.startswith("//?/"):
        raw = raw[4:]
    out: list[str] = []
    for part in Path(raw).parts:
        if part == ".":
            continue
        if part == "..":
            if out and not _is_anchor(out[-1]) and out[-1] != "..":
                out.pop()
            else:
                out.append("..")
            continue
        out.append(part)
    return out


def _is_under_delme(path: str) -> bool:
    """True only when a lexical component is exactly the staging directory.

    Path.resolve() is the wrong test: it uses the process cwd and follows
    links, so one action dict changes class, and a path that does not name
    the staging directory can look staged."""
    if not path or "\x00" in path:
        return False
    try:
        parts = _lexical_parts(path)
    except (OSError, ValueError):
        return False
    if any(part == ".." for part in parts):
        return False
    return any(part.lower() == "_delme" for part in parts)


class ApprovalGate:
    def __init__(self, ledger, clock: Callable[[], float] = time.time,
                 request_ttl_s: float = REQUEST_TTL_S):
        self.ledger = ledger
        self.clock = clock
        self.ttl = float(request_ttl_s)

    # ---------------- projection ----------------
    @staticmethod
    def _fold(s: dict, rec: dict) -> dict:
        ev, p = rec.get("event"), rec.get("payload") or {}
        if not str(ev).startswith("APPROVAL_"):
            return s
        rid = p.get("request_id")
        if ev == "APPROVAL_REQUESTED":
            # First id wins. A replay must not reopen a consumed or denied request.
            if rid not in s["requests"]:
                s["requests"][rid] = {"principal": p["principal"], "action_sha": p["action_sha"],
                                      "action": p["action"], "expires": p["expires"],
                                      "state": "PENDING", "nonce_sha": None,
                                      "class": p["class"]}
        elif ev == "APPROVAL_GRANTED" and rid in s["requests"]:
            row = s["requests"][rid]
            if row["state"] == "PENDING":
                row.update(state="GRANTED", nonce_sha=p["nonce_sha"],
                           approver=p["approver"], grant_expires=p["expires"])
        elif ev == "APPROVAL_DENIED" and rid in s["requests"]:
            row = s["requests"][rid]
            if row["state"] == "PENDING":
                row.update(state="DENIED", approver=p["approver"])
        elif ev == "APPROVAL_CONSUMED" and rid in s["requests"]:
            row = s["requests"][rid]
            if row["state"] == "GRANTED":
                row["state"] = "CONSUMED"
        elif ev == "APPROVAL_ALLOWLISTED":
            s["allow"].append({"principal": p["principal"], "kind": p["kind"],
                               "pattern": p["pattern"], "expires": p.get("expires"),
                               "approver": p["approver"]})
        return s

    def _state(self) -> dict:
        return self.ledger.fold_cached(FOLD, self._fold,
                                       lambda: {"requests": {}, "allow": []})

    # ---------------- classification ----------------
    def classify(self, action, principal: Optional[str] = None) -> dict:
        a = normalize_action(action)
        t = _for_rules(_text(a))
        hits, why = [], []
        for rid, kinds, rx, reason in HARDLINE_RULES:
            if kinds is not None and a["kind"] not in kinds:
                continue
            if rid == "delete-outside-delme":
                if a["kind"] == "file_delete" and not _is_under_delme(a.get("path", "")):
                    hits.append(rid)
                    why.append(reason)
                continue
            if rx is not None and rx.search(t):
                hits.append(rid)
                why.append(reason)
        if hits:
            return {"class": HARDLINE, "rules": hits, "why": why, "scan": content_scan(a),
                    "action_sha": _sha(a)}
        confirm_hits = [(rid, reason) for rid, kinds, rx, reason in CONFIRM_RULES
                        if a["kind"] in kinds and rx.search(t)]
        scan = content_scan(a)
        needs_confirm = (bool(confirm_hits) or bool(scan)
                         or a["kind"] in ALWAYS_CONFIRM_KINDS)
        allowed = (principal is not None and not needs_confirm
                   and self._allowlisted(principal, a))
        cls = ALLOW if allowed else CONFIRM
        return {"class": cls, "rules": [r for r, _ in confirm_hits],
                "why": [w for _, w in confirm_hits] + scan, "scan": scan,
                "action_sha": _sha(a),
                "allowlisted": allowed}

    def _allowlisted(self, principal: str, a: dict) -> bool:
        now = self.clock()
        t = _text(a)
        for row in self._state()["allow"]:
            if row["principal"] != principal or row["kind"] != a["kind"]:
                continue
            if row.get("expires") is not None and now >= row["expires"]:
                continue
            try:
                if re.fullmatch(row["pattern"], t.strip()):
                    return True
            except re.error:
                continue
        return False

    # ---------------- the gate ----------------
    def request(self, principal: str, action) -> dict:
        a = normalize_action(action)
        c = self.classify(a, principal)
        if c["class"] == HARDLINE:
            self._record_refusal(principal, a, c)
            raise ApprovalError("HARDLINE", "; ".join(c["why"]), rules=c["rules"])
        if c["class"] == ALLOW:
            return {"class": ALLOW, "request_id": None, "action_sha": c["action_sha"]}
        rid = "ap-" + secrets.token_hex(8)
        self.ledger.append("APPROVAL_REQUESTED", {
            "schema": SCHEMA, "request_id": rid, "principal": principal,
            "action": a, "action_sha": c["action_sha"], "class": CONFIRM,
            "why": c["why"], "expires": self.clock() + self.ttl, "at": self.clock()})
        return {"class": CONFIRM, "request_id": rid, "action_sha": c["action_sha"],
                "why": c["why"]}

    def pending(self) -> list[dict]:
        now = self.clock()
        return [{"request_id": k, **{kk: v[kk] for kk in ("principal", "action", "expires")}}
                for k, v in self._state()["requests"].items()
                if v["state"] == "PENDING" and now < v["expires"]]

    def _decidable(self, request_id: str, approver: str) -> dict:
        r = self._state()["requests"].get(request_id)
        if r is None:
            raise ApprovalError("NO_REQUEST", f"unknown request {request_id}")
        if not _is_captain(approver):
            raise ApprovalError("NOT_APPROVER", f"{approver} cannot approve - captain only")
        if _same_principal(approver, r["principal"]):
            raise ApprovalError("SELF_APPROVAL", "a principal never approves its own request")
        if r["state"] != "PENDING":
            raise ApprovalError("ALREADY_DECIDED", f"{request_id} is {r['state']}")
        if self.clock() >= r["expires"]:
            raise ApprovalError("EXPIRED", "silence is not consent - the request expired")
        return r

    def grant(self, request_id: str, approver: str, grant_ttl_s: float = 120.0) -> str:
        nonce = secrets.token_urlsafe(18)
        nonce_sha = _sha(nonce)
        ttl = float(grant_ttl_s)

        def decide(_recs):
            self._decidable(request_id, approver)
            now = self.clock()
            return ("APPROVAL_GRANTED", {
                "schema": SCHEMA, "request_id": request_id, "approver": approver,
                "nonce_sha": nonce_sha, "expires": now + ttl, "at": now})

        self.ledger.append_guarded(decide)  # check and append share the lock
        return nonce

    def deny(self, request_id: str, approver: str, reason: str = "") -> None:
        def decide(_recs):
            self._decidable(request_id, approver)
            return ("APPROVAL_DENIED", {
                "schema": SCHEMA, "request_id": request_id, "approver": approver,
                "reason": str(reason)[:300], "at": self.clock()})

        self.ledger.append_guarded(decide)

    def consume(self, request_id: str, nonce: str, principal: str, action) -> None:
        a = normalize_action(action)
        failure: dict = {}

        def decide(_recs):
            c = self.classify(a)
            if c["class"] == HARDLINE:
                failure["e"] = ("HARDLINE", "; ".join(c["why"]))
                failure["extra"] = {"rules": c["rules"]}
                return ("APPROVAL_REFUSED", {
                    "schema": SCHEMA, "principal": principal, "action_sha": c["action_sha"],
                    "kind": a["kind"], "rules": c["rules"], "request_id": request_id,
                    "at": self.clock()})
            r = self._state()["requests"].get(request_id)
            if r is None:
                failure["e"] = ("NO_REQUEST", f"unknown request {request_id}")
            elif r["state"] == "DENIED":
                failure["e"] = ("DENIED", "the Captain denied this action")
            elif r["state"] != "GRANTED":
                failure["e"] = ("BAD_NONCE", f"{request_id} is {r['state']}, not GRANTED")
            elif r["principal"] != principal:
                failure["e"] = ("BAD_NONCE", "grant belongs to another principal")
            elif self.clock() >= r.get("grant_expires", 0):
                failure["e"] = ("EXPIRED", "the grant expired unused")
            elif r["action_sha"] != _sha(a):
                failure["e"] = ("ACTION_MISMATCH", "the action differs from what was approved")
            elif _sha(str(nonce or "")) != r["nonce_sha"]:
                failure["e"] = ("BAD_NONCE", "nonce does not match the grant")
            if failure:
                return None
            return ("APPROVAL_CONSUMED", {"schema": SCHEMA, "request_id": request_id,
                                          "principal": principal, "at": self.clock()})
        self.ledger.append_guarded(decide)       # single use: decided under the lock
        if failure:
            extra = failure.get("extra") or {}
            raise ApprovalError(*failure["e"], **extra)

    def guard(self, principal: str, action, run: Callable[[], object], *,
              request_id: Optional[str] = None, nonce: Optional[str] = None):
        """Classify, then run only if ALLOW or a matching grant is consumed."""
        a = normalize_action(action)
        if request_id is None:
            r = self.request(principal, a)
            if r["class"] == ALLOW:
                return run()
            raise ApprovalError("NEEDS_APPROVAL", "Captain approval required: "
                                + "; ".join(r.get("why") or ["unclassified action"]),
                                request_id=r["request_id"])
        c = self.classify(a, principal)
        if c["class"] == HARDLINE:          # a grant can never unlock HARDLINE
            self._record_refusal(principal, a, c)
            raise ApprovalError("HARDLINE", "; ".join(c["why"]), rules=c["rules"])
        self.consume(request_id, nonce or "", principal, a)
        return run()

    def _record_refusal(self, principal: str, action: dict, classified: dict) -> None:
        self.ledger.append("APPROVAL_REFUSED", {
            "schema": SCHEMA, "principal": principal, "action_sha": classified["action_sha"],
            "kind": action["kind"], "rules": classified["rules"], "at": self.clock()})

    def allowlist(self, principal: str, kind: str, pattern: str, approver: str, *,
                  ttl_s: Optional[float] = None) -> None:
        """A standing ALLOW for a principal (session: ttl_s; permanent: None). Never
        covers HARDLINE or any CONFIRM rule - those are checked first."""
        if not _is_captain(approver) or _same_principal(approver, principal):
            raise ApprovalError("NOT_APPROVER", "only another captain principal allowlists")
        if kind not in KINDS:
            raise ApprovalError("BAD_ACTION", f"kind {kind!r}")
        re.compile(pattern)
        self.ledger.append("APPROVAL_ALLOWLISTED", {
            "schema": SCHEMA, "principal": principal, "kind": kind, "pattern": pattern,
            "approver": approver, "at": self.clock(),
            "expires": (self.clock() + ttl_s) if ttl_s else None})
