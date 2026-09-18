#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_skills - agent skills that COSMOS can learn WITHOUT a second writer (COSMOS_next).

Borrowed from Hermes Agent's skills system (procedural memory an agent creates after a
hard task, SKILL.md files in the agentskills.io shape, progressive disclosure: list the
descriptions, load the body on demand) and re-shaped for P10 - agents propose, CCr
disposes:

  * An agent PROPOSES a SKILL.md. It is validated (frontmatter `name` / `description`,
    size limits) and every command-looking line is run through cosmos_approval's
    classifier: a skill that teaches a HARDLINE action is REFUSED at proposal.
  * The proposal is content-addressed (state/skills/proposed/<sha>/SKILL.md) and
    ledgered (SKILL_PROPOSED). Nothing is active yet.
  * ONLY THE CCr ACTIVATES. accept() requires cosmos_ccr.assert_pen(sid) and installs the
    body through the Arbiter's fenced commit on `skill:<name>` (staged, token CAS, atomic
    replace) - the same gateway as any protected write. SKILL_ACCEPTED records the sha
    and version.
  * load() re-hashes the active file against the accepted sha: an edit outside the fence
    is TAMPERED, never silently served to a seat.
  * Reads never mkdir.

Frontmatter is parsed without a YAML dependency: `key: value` lines between `---` fences.

    see tests/test_hermes_features.py
"""
from __future__ import annotations

import hashlib
import re
import time
from pathlib import Path
from typing import Optional

from cosmos_ccr import CcrError, held, read_lease

SCHEMA = "cosmos-skills/1"
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
MAX_NAME, MAX_DESC, MAX_BODY = 64, 1024, 64 * 1024
FOLD = "cosmos_skills.v1"


class SkillError(RuntimeError):
    """kind in {BAD_SKILL, HARDLINE, NO_PROPOSAL, TAMPERED, NOT_FOUND, NO_PEN,
    ALREADY_DECIDED}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def parse_skill(text: str) -> dict:
    if not isinstance(text, str) or len(text.encode("utf-8")) > MAX_BODY:
        raise SkillError("BAD_SKILL", f"SKILL.md must be text of at most {MAX_BODY} bytes")
    m = re.match(r"^---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(\r?\n|$)", text, re.S)
    if not m:
        raise SkillError("BAD_SKILL", "missing --- frontmatter ---")
    meta = {}
    for line in m.group(1).splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        k, sep, v = line.partition(":")
        if not sep:
            raise SkillError("BAD_SKILL", f"frontmatter line is not key: value: {line!r}")
        meta[k.strip()] = v.strip().strip('"').strip("'")
    name, desc = meta.get("name", ""), meta.get("description", "")
    if not NAME_RE.match(name) or len(name) > MAX_NAME:
        raise SkillError("BAD_SKILL", f"name {name!r}: lowercase words joined by hyphens, "
                                      f"at most {MAX_NAME} chars")
    if not desc or len(desc) > MAX_DESC:
        raise SkillError("BAD_SKILL", f"description is required, at most {MAX_DESC} chars")
    return {"name": name, "description": desc, "meta": meta,
            "body": text[m.end():]}


def _command_lines(body: str) -> list[str]:
    """Lines a reader would run: fenced code blocks and `$ `/`> ` prompts."""
    out, fence = [], False
    for line in body.splitlines():
        s = line.strip()
        if s.startswith("```"):
            fence = not fence
            continue
        if fence or s.startswith(("$ ", "> ", "PS> ")):
            out.append(s.lstrip("$> ").removeprefix("PS> ").strip())
    return [c for c in out if c]


def assert_pen(paths, *, sid: str) -> None:
    rec = read_lease(paths)
    if rec is None or not held(paths):
        raise CcrError("CCR_NO_LEASE", "no live CCR.lease")
    if str(rec.get("sid")) != str(sid):
        raise CcrError("CCR_SID_MISMATCH",
                       f"held sid={rec.get('sid')!r} pen sid={sid!r}")


class SkillRegistry:
    def __init__(self, paths, ledger, arbiter, approval=None, clock=time.time):
        self.paths = paths
        self.ledger = ledger
        self.arbiter = arbiter
        self.approval = approval
        self.clock = clock

    def _dir(self, *parts) -> Path:
        return self.paths.role("state", "skills", *parts)

    @staticmethod
    def _fold(s: dict, rec: dict) -> dict:
        ev, p = rec.get("event"), rec.get("payload") or {}
        if ev == "SKILL_PROPOSED":
            s["proposed"][p["sha"]] = {"name": p["name"], "description": p["description"],
                                       "principal": p["principal"], "state": "PROPOSED"}
        elif ev in ("SKILL_ACCEPTED", "SKILL_REJECTED") and p.get("sha") in s["proposed"]:
            s["proposed"][p["sha"]]["state"] = ev.split("_")[1]
            if ev == "SKILL_ACCEPTED":
                prior = s["active"].get(p["name"], {}).get("version", 0)
                s["active"][p["name"]] = {"sha": p["sha"], "version": prior + 1,
                                          "description": p["description"]}
        return s

    def _state(self) -> dict:
        return self.ledger.fold_cached(FOLD, self._fold,
                                       lambda: {"proposed": {}, "active": {}})

    def propose(self, principal: str, text: str, rationale: str = "") -> dict:
        sk = parse_skill(text)
        if self.approval is not None:
            for cmd in _command_lines(sk["body"]):
                c = self.approval.classify({"kind": "shell", "command": cmd})
                if c["class"] == "HARDLINE":
                    self.ledger.append("SKILL_REFUSED", {
                        "schema": SCHEMA, "name": sk["name"], "principal": principal,
                        "rules": c["rules"], "at": self.clock()})
                    raise SkillError("HARDLINE", f"skill teaches a HARDLINE action "
                                                 f"({', '.join(c['rules'])}): {cmd[:80]!r}")
        sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
        target = self._dir("proposed", sha, "SKILL.md")
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            tmp = target.with_name("SKILL.md.part")
            tmp.write_text(text, encoding="utf-8", newline="")
            tmp.replace(target)
        self.ledger.append("SKILL_PROPOSED", {
            "schema": SCHEMA, "sha": sha, "name": sk["name"],
            "description": sk["description"], "principal": principal,
            "rationale": str(rationale)[:500], "bytes": len(text.encode("utf-8")),
            "at": self.clock()})
        return {"sha": sha, "name": sk["name"], "state": "PROPOSED"}

    def _proposal(self, sha: str) -> dict:
        p = self._state()["proposed"].get(sha)
        if p is None:
            raise SkillError("NO_PROPOSAL", f"no proposal {sha[:12]}")
        if p["state"] != "PROPOSED":
            raise SkillError("ALREADY_DECIDED", f"{sha[:12]} is {p['state']}")
        return p

    def accept(self, sha: str, *, ccr_sid: str) -> dict:
        from cosmos_lock import StagedArtifact
        p = self._proposal(sha)
        try:
            assert_pen(self.paths, sid=ccr_sid)
        except CcrError as e:
            raise SkillError("NO_PEN", str(e)) from e
        src = self._dir("proposed", sha, "SKILL.md")
        text = src.read_bytes().decode("utf-8")
        if hashlib.sha256(text.encode("utf-8")).hexdigest() != sha:
            raise SkillError("TAMPERED", f"proposal file no longer hashes to {sha[:12]}")
        dst = self._dir("active", p["name"], "SKILL.md")
        dst.parent.mkdir(parents=True, exist_ok=True)
        lease = self.arbiter.acquire("skill:%s" % p["name"], "ccr:%s" % ccr_sid, ttl=60)
        try:
            def stage(token):
                tmp = dst.with_name("SKILL.md.part%d" % token)
                tmp.write_text(text, encoding="utf-8", newline="")
                return StagedArtifact(src=tmp, dst=dst)
            self.arbiter.fenced_commit(lease, stage)
        finally:
            self.arbiter.release(lease)
        self.ledger.append("SKILL_ACCEPTED", {
            "schema": SCHEMA, "sha": sha, "name": p["name"],
            "description": p["description"], "ccr_sid": ccr_sid, "at": self.clock()})
        try:
            from cosmos_action_chain import append_action
            append_action(
                self.ledger,
                creator="agent:propose",
                reviewer="gitur:check",
                approver="ccr:%s" % ccr_sid,
                kind="file_write",
                detail="skill:%s" % p["name"],
            )
        except Exception:  # noqa: BLE001
            pass
        return {"name": p["name"], "sha": sha,
                "version": self._state()["active"][p["name"]]["version"]}

    def reject(self, sha: str, *, ccr_sid: str, reason: str = "") -> None:
        self._proposal(sha)
        try:
            assert_pen(self.paths, sid=ccr_sid)
        except CcrError as e:
            raise SkillError("NO_PEN", str(e)) from e
        self.ledger.append("SKILL_REJECTED", {"schema": SCHEMA, "sha": sha,
                                              "ccr_sid": ccr_sid,
                                              "reason": str(reason)[:500],
                                              "at": self.clock()})

    def list(self) -> list[dict]:
        """Progressive disclosure: names and descriptions only."""
        return [{"name": n, "description": a["description"], "version": a["version"]}
                for n, a in sorted(self._state()["active"].items())]

    def load(self, name: str) -> str:
        a = self._state()["active"].get(name)
        if a is None:
            raise SkillError("NOT_FOUND", f"no active skill {name!r}")
        path = self._dir("active", name, "SKILL.md")
        if not path.exists():
            raise SkillError("TAMPERED", f"active skill {name!r} file is missing")
        text = path.read_bytes().decode("utf-8")
        if hashlib.sha256(text.encode("utf-8")).hexdigest() != a["sha"]:
            raise SkillError("TAMPERED", f"{name!r} changed outside the fenced gateway")
        return text


def open_registry(root: str | Path) -> SkillRegistry:
    """Compose SkillRegistry on an existing install. Does not boot Kernel
    (no BOOT_VERIFIED). list() still never mkdir."""
    from cosmos_approval import ApprovalGate
    from cosmos_ledger import Ledger
    from cosmos_lock import Arbiter
    from cosmos_paths import CosmosPaths
    paths = CosmosPaths(root)
    key = paths.config("install_key.bin").read_bytes()
    led = Ledger(paths.ledger("authority.jsonl"), key, "ccr", head_anchor=True)
    arb = Arbiter(paths.ledger("leases.jsonl"), key=key)
    return SkillRegistry(paths, led, arb, approval=ApprovalGate(led))


def main(argv: Optional[list[str]] = None) -> int:
    """CCr propose/accept without a REPL.

        py -3.14 cosmos\\cosmos_skills.py propose --root LIVE --file SKILL.md
        py -3.14 cosmos\\cosmos_skills.py accept  --root LIVE --sha HEX --sid CCR_SID
        py -3.14 cosmos\\cosmos_skills.py list    --root LIVE
    """
    import argparse
    import json
    import sys
    ap = argparse.ArgumentParser(prog="cosmos_skills")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("propose", help="content-address a SKILL.md; not active")
    p.add_argument("--root", required=True)
    p.add_argument("--file", required=True)
    p.add_argument("--principal", default="ccr")
    p.add_argument("--rationale", default="")
    p = sub.add_parser("accept", help="CCr pen + fenced_commit on skill:<name>")
    p.add_argument("--root", required=True)
    p.add_argument("--sha", required=True)
    p.add_argument("--sid", required=True)
    p = sub.add_parser("list", help="active names only; never mkdir")
    p.add_argument("--root", required=True)
    a = ap.parse_args(argv)
    try:
        reg = open_registry(a.root)
        if a.cmd == "propose":
            text = Path(a.file).read_bytes().decode("utf-8")
            out = reg.propose(a.principal, text, rationale=a.rationale)
        elif a.cmd == "accept":
            out = reg.accept(a.sha, ccr_sid=a.sid)
        else:
            names = reg.list()
            out = {"schema": SCHEMA, "skills": names,
                   "kind": "MEASURED" if names else "UNMEASURED"}
        print(json.dumps(out, indent=1))
        return 0
    except SkillError as e:
        print(json.dumps({"error": e.kind, "detail": str(e)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
