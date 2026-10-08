#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Session procedures: resession close, ask ladder, autosave, learned skills.

Resession order is TidyUP, then TidyUP2, then one BU file for the stream or
the special session type. Auto-resession asks at 75, 80, and 85 percent of
the context window. A decline waits for the next rung. A live Grok session
closes at 190000 input tokens, not at 92 percent. Compaction asks. It does
not close. Autosave writes the session to documents, the existing state/cas
store, and a ROLD update. A demonstrated skill is proposed through
cosmos_skills (agentskills.io frontmatter). CCr accept stays on the pen.

The clock does not engage the close unless the caller passes engage=True
(--engage). Saving the kit does not fire any of this.

    py -3.14 cosmos\\cosmos_session_procedures.py --selftest
"""
from __future__ import annotations

import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path

from cosmos_resession import (
    close_banner, cosmos_tu2, render_running_session, unique_stamp,
    write_session_save)
from cosmos_rold_index import index_credential, index_seat, index_skill, lookup
from cosmos_session_kit import load_kit

ASK_NAME = "RESESSION_ASK.flag"
ASK_SCHEMA = "cosmos-resession-ask/1"
DEFAULT_ASK = (0.75, 0.80, 0.85)
DEFAULT_FORCE = 0.92
DEFAULT_CLOSE_TOKENS = 190_000
BU_FILES = {
    "Cm": "BUCm.toml",
    "CCr": "BUcr.toml",
    "ORC": "BUorc.toml",
    "harness": "BUhar.toml",
    "websites": "BUcr.toml",
    "XTalk": "BUxt.toml",
}
_SECRET = re.compile(
    r"(sk-[A-Za-z0-9][A-Za-z0-9_-]*|sk-ant-\S+|sk-or-\S+|"
    r"Bearer\s+\S+|-----BEGIN [A-Z ]+-----|"
    r"api[_-]?key\s*[:=]\s*\S+)",
    re.I,
)


class SessionProcedureError(RuntimeError):
    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def _now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def _stamp(parent: Path | None = None, suffix: str = "",
           now: datetime | None = None) -> str:
    return unique_stamp(parent, suffix, now)


def canon_pct(value) -> str:
    return "%.4f" % float(value)


def redact(text: str) -> str:
    return _SECRET.sub("[redacted]", text)


def ladder(kit: dict) -> tuple[tuple[float, ...], float]:
    rs = kit.get("resession") if isinstance(kit.get("resession"), dict) else {}
    raw = rs.get("ask_pct") or DEFAULT_ASK
    ask = tuple(float(x) for x in raw)
    force = float(rs.get("force_pct") if rs.get("force_pct") is not None else DEFAULT_FORCE)
    if (not ask or list(ask) != sorted(ask) or len(set(canon_pct(x) for x in ask)) != len(ask)
            or any(not (0.0 < x < 1.0) for x in ask)
            or not (0.0 < force < 1.0) or ask[-1] >= force):
        raise SessionProcedureError(
            "BAD_LADDER", "ask rungs must climb and stop before force")
    return ask, force


def pct_from_heartbeat(hb: dict | None, window: int) -> float | None:
    if not isinstance(hb, dict):
        return None
    tokens = hb.get("tokens_in")
    if tokens not in (None, "") and window:
        try:
            return float(tokens) / float(window)
        except (TypeError, ValueError, ZeroDivisionError):
            return None
    raw = hb.get("context_pct")
    if raw in (None, ""):
        return None
    try:
        got = float(raw)
    except (TypeError, ValueError):
        return None
    if got > 1.0:
        got = got / 100.0
    return got


def decide_rung(pct: float, ask: tuple[float, ...], force: float,
                declined: set[str]) -> dict:
    """idle, ask at the first rung not yet declined, or force at the last line."""
    if pct >= force:
        return {"act": "force", "pct": force, "why": "context %.0f%%" % (pct * 100)}
    for rung in ask:
        if pct >= rung and canon_pct(rung) not in declined:
            return {"act": "ask", "pct": rung,
                    "why": "ask at %.0f%%" % (rung * 100)}
    return {"act": "idle", "pct": pct, "why": "below the next rung"}


def _token_count(tokens_in, heartbeat: dict | None) -> int | None:
    raw = None
    if isinstance(heartbeat, dict) and heartbeat.get("tokens_in") not in (None, ""):
        raw = heartbeat.get("tokens_in")
    elif tokens_in not in (None, ""):
        raw = tokens_in
    if raw is None:
        return None
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None


def _close_tokens(rs: dict) -> int:
    raw = rs.get("close_tokens")
    if raw in (None, ""):
        return DEFAULT_CLOSE_TOKENS
    try:
        return int(raw)
    except (TypeError, ValueError):
        return DEFAULT_CLOSE_TOKENS


def next_action(kit: dict, tokens_in, *, declined: set[str],
                compaction: bool = False, heartbeat: dict | None = None) -> dict:
    ask, _force = ladder(kit)
    rs = kit.get("resession") or {}
    if compaction and rs.get("on_compaction", True):
        if canon_pct(ask[0]) not in declined:
            return {"act": "ask", "pct": ask[0], "why": "compaction"}
    if not rs.get("on_token_count", True):
        return {"act": "idle", "pct": 0.0, "why": "token count off"}
    window = int(rs.get("window_tokens") or 0)
    if heartbeat is not None:
        pct = pct_from_heartbeat(heartbeat, window)
    else:
        try:
            pct = float(tokens_in) / float(window) if window else None
        except (TypeError, ValueError):
            pct = None
    tokens = _token_count(tokens_in, heartbeat)
    close_at = _close_tokens(rs)
    if tokens is not None and tokens >= close_at:
        return {"act": "force", "pct": (close_at / window) if window else 0.0,
                "why": "close at %d tokens" % close_at}
    if (tokens is None and pct is not None and window
            and pct >= (close_at / float(window))):
        return {"act": "force", "pct": close_at / float(window),
                "why": "close at %d tokens" % close_at}
    if pct is None:
        return {"act": "idle", "pct": 0.0, "why": "no tokens"}
    for rung in ask:
        if pct >= rung and canon_pct(rung) not in declined:
            return {"act": "ask", "pct": rung,
                    "why": "ask at %.0f%%" % (rung * 100)}
    return {"act": "idle", "pct": pct, "why": "below the next rung"}


def ask_path(paths) -> Path:
    return paths.role("state", "control", ASK_NAME)


def read_ask(paths) -> dict | None:
    p = ask_path(paths)
    if not p.is_file():
        return None
    try:
        rec = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeDecodeError):
        return None
    return rec if isinstance(rec, dict) else None


def declined_set(flag: dict | None) -> set[str]:
    if not isinstance(flag, dict):
        return set()
    out = set()
    for item in flag.get("declined") or []:
        try:
            out.add(canon_pct(item))
        except (TypeError, ValueError):
            continue
    return out


def write_ask(paths, *, rung: float, declined: set[str], why: str) -> dict:
    rec = {
        "schema": ASK_SCHEMA,
        "act": "ask",
        "rung": float(rung),
        "declined": sorted(declined),
        "why": why,
        "asked_at": _now(),
        "question": "Resession now?",
    }
    dest = ask_path(paths)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    return rec


def decline_rung(paths, rung: float) -> dict:
    cur = read_ask(paths) or {}
    declined = declined_set(cur)
    declined.add(canon_pct(rung))
    rec = {
        "schema": ASK_SCHEMA,
        "act": "declined",
        "rung": float(rung),
        "declined": sorted(declined),
        "why": "declined %.0f%%" % (float(rung) * 100),
        "asked_at": cur.get("asked_at") or _now(),
    }
    dest = ask_path(paths)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    return rec


def session_identity(heartbeat: dict | None) -> tuple[str, str]:
    """Stream from the session, then an explicit session type.

    The chair role on a heartbeat is not a session type. A role of CCr must
    not select the websites pointer while the session is Cm.
    """
    rec = heartbeat or {}
    stream = str(rec.get("stream") or rec.get("cosmos_sid") or "Cm").strip()
    session_type = str(rec.get("session_type") or "").strip()
    return stream or "Cm", session_type


def bu_name(stream: str, session_type: str = "") -> str:
    """A known session type wins. Anything else uses the stream."""
    for key in ((session_type or "").strip(), (stream or "").strip()):
        if key in BU_FILES:
            return BU_FILES[key]
    raise SessionProcedureError(
        "BAD_STREAM", f"no BU file for {session_type!r} / {stream!r}")


def render_bu(*, stream: str, session_type: str, pack: Path,
              tu2_ok, reason: str, work: str) -> str:
    lines = [
        "# BU pointer. HMAC SEED is the carry-over authority.",
        'schema = "bu/1"',
        "stream = %s" % json.dumps(stream),
        "session_type = %s" % json.dumps(session_type or stream),
        "written_at = %s" % json.dumps(_now()),
        "",
        "[read_order]",
        "r1 = %s" % json.dumps(bu_name(stream, session_type)),
        "r2 = %s" % json.dumps(str(Path(pack) / "TIDYUP.md")),
        "r3 = %s" % json.dumps(str(Path(pack) / "tu2_adversarial.json")),
        "",
        "[next]",
        "work = %s" % json.dumps(work or ""),
        "pack = %s" % json.dumps(str(pack)),
        "",
        "[tidyup]",
        "reason = %s" % json.dumps(reason or ""),
        "tu2_ok = %s" % ("true" if tu2_ok else "false"),
        "",
    ]
    return "\n".join(lines)


def _paste(bu: Path, pack: Path, stream: str) -> str:
    return (
        "# BootUP paste — pointers only\n"
        "# Written %s\n\n"
        "Read in this order:\n"
        "1. `%s`\n"
        "2. `%s`\n"
        "3. `%s`\n\n"
        "Then `py -3.14 cosmos\\cosmos.py session start %s`\n"
    ) % (_now(), bu, pack / "TIDYUP.md", pack / "tu2_adversarial.json", stream)


def tidyup_close(kernel, handoff: str, force: bool = True):
    """Kernel TidyUP. force=True records unresolved watchers in the seed."""
    return kernel.sessions.close_session(handoff_to=handoff, force=force)


def close_resession(paths, repo, *, stream: str, session_type: str = "",
                    kit: dict, reason: str, work: str = "",
                    closer=None, bu_dir: Path | None = None) -> dict:
    """TidyUP, then TidyUP2, then one BU file. Panes that are off are skipped."""
    cos = kit.get("cos") if isinstance(kit.get("cos"), dict) else {}
    saves = paths.state("session_saves")
    pack = saves / _stamp(saves)
    out = {"pack": str(pack), "steps": []}
    files: dict[str, str] = {}
    tu2_ok = None
    if cos.get("tidyup", True):
        if closer is None:
            raise SessionProcedureError("NO_CLOSER", "TidyUP needs a closer")
        seed_path = Path(closer())
        files["TIDYUP.md"] = (
            "# TidyUP\n\nClosed: %s\n\nSeed: `%s`\n\nReason: %s\n" % (
                _now(), seed_path, reason or ""))
        out["steps"].append("tidyup")
        out["seed"] = str(seed_path)
    if cos.get("tu2", True):
        tu2 = cosmos_tu2(repo=Path(repo), root=Path(paths.root))
        files["tu2_adversarial.json"] = json.dumps(tu2, indent=1)
        tu2_ok = bool(tu2.get("ok"))
        out["tu2_ok"] = tu2_ok
        out["tu2_findings"] = list(tu2.get("findings") or [])
        out["steps"].append("tu2")
    if files:
        banner = close_banner(str(pack)) if "tidyup" in out["steps"] else (
            "SNAPSHOT\nTEXT SAVED TO %s\n" % pack)
        write_session_save(pack, banner=banner, files=files)
    if cos.get("bu", True):
        name = bu_name(stream, session_type)
        dest_dir = Path(bu_dir) if bu_dir else Path(repo)
        dest = dest_dir / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        pack.mkdir(parents=True, exist_ok=True)
        dest.write_text(render_bu(
            stream=stream, session_type=session_type or stream, pack=pack,
            tu2_ok=bool(tu2_ok), reason=reason, work=work,
        ), encoding="utf-8")
        paste = paths.state("BOOTUP_PASTE.md")
        paste.write_text(_paste(dest, pack, stream), encoding="utf-8")
        out["bu"] = str(dest)
        out["paste"] = str(paste)
        out["steps"].append("bu")
    return out


def _artifact(paths, name: str, raw: bytes) -> dict:
    """Store bytes in the existing state/cas. No second artifact tree."""
    from cosmos_packet import cas_dir, packetize
    pkt = packetize(raw.decode("utf-8"), dest_dir=cas_dir(paths))
    return {
        "name": name,
        "sha256": pkt.get("sha256"),
        "len": len(raw),
        "kind": pkt.get("kind"),
        "path": pkt.get("path") or "",
    }


def autosave_tick(paths, session: dict, kit: dict | None = None,
                  rold: Path | None = None) -> dict:
    """Write documents, artifacts, and a ROLD update. Does not close or spawn."""
    kit = kit if kit is not None else load_kit(paths)
    sid = str(session.get("sid") or "session")
    safe_sid = re.sub(r"[^A-Za-z0-9._-]", "_", sid)[:80] or "session"
    parent = paths.state("session_saves", safe_sid, "autosave")
    dest = parent / _stamp(parent)
    dest.mkdir(parents=True, exist_ok=True)
    markdown = redact(str(session.get("markdown") or ""))
    record = session.get("record") if isinstance(session.get("record"), dict) else {}
    record_text = redact(json.dumps(record, indent=1, default=str))
    fields = session.get("fields") if isinstance(session.get("fields"), dict) else {}
    docs = {
        "SESSION.md": markdown,
        "session.json": record_text,
        "running.toml": render_running_session(fields),
    }
    blobs = [_artifact(paths, name, raw.encode("utf-8"))
             for name, raw in docs.items()]
    note = _rold_update(session, blobs)
    inbox_dir = paths.state("rold", "inbox")
    inbox = inbox_dir / (_stamp(inbox_dir, suffix=".md") + ".md")
    inbox.parent.mkdir(parents=True, exist_ok=True)
    inbox.write_text(note, encoding="utf-8")
    indexed = _index_session_events(rold, session)
    auto = {
        "schema": "cosmos-autosave/1",
        "artifacts": blobs,
        "rold_inbox": str(inbox),
        "indexed": indexed,
    }
    docs["ROLD_UPDATE.md"] = note
    docs["AUTOSAVE.json"] = json.dumps(auto, indent=1)
    write_session_save(
        dest, banner="AUTOSAVE\nTEXT SAVED TO %s\n" % dest, files=docs)
    return {"pack": str(dest), "n": len(blobs), "inbox": str(inbox),
            "indexed": indexed}


BEAT_NAME = "COW_HEARTBEAT.json"
BEAT_SCHEMA = "cosmos-cow-heartbeat/1"
AUTOSAVE_MARK = "AUTOSAVE_MARK.json"
_DROP_KEYS = frozenset({
    "value", "secret", "token", "key", "password", "bearer",
    "seed_hmac", "hmac", "api_token", "authorization",
})


def record_session_beat(paths, beat: dict, *, now: float | None = None,
                        acted: bool = True) -> dict:
    """Merge one sitting-session beat onto COW_HEARTBEAT.json.

    The ladder reads tokens_in, context_pct, and last_act_epoch from that file.
    Secret-shaped keys are dropped. Secret-shaped strings are redacted. The
    credential file is not opened. last_act_epoch moves only when acted is true.
    """
    if not isinstance(beat, dict):
        raise SessionProcedureError("BAD_BEAT", "beat is not an object")
    now_s = time.time() if now is None else float(now)
    path = paths.role("state", "control", BEAT_NAME)
    prev: dict = {}
    if path.is_file():
        try:
            got = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError, UnicodeDecodeError):
            got = None
        if isinstance(got, dict):
            prev = got
    merged: dict = {}
    for src in (prev, beat):
        for key, value in src.items():
            if str(key).lower() in _DROP_KEYS:
                continue
            if isinstance(value, str) and _SECRET.search(value):
                value = redact(value)
            merged[key] = value
    merged["schema"] = BEAT_SCHEMA
    if acted:
        merged["last_act_epoch"] = now_s
        merged.setdefault("spawned_at_epoch", now_s)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(merged, indent=1, default=str), encoding="utf-8")
    return merged


def maybe_autosave(paths, heartbeat: dict | None, *, now: float,
                   pid_alive: bool | None, stale_s: float) -> dict | None:
    """Save when the sitting session marked itself dirty and is still fresh.

    A dead pid, a stale last_act, or an empty note writes nothing. A quiet
    session does not get a pack. The interval is the kit's autosave_min.
    """
    if pid_alive is False or not isinstance(heartbeat, dict):
        return None
    if not heartbeat.get("dirty"):
        return None
    try:
        last = float(heartbeat.get("last_act_epoch") or 0)
    except (TypeError, ValueError):
        return None
    if not last or (float(now) - last) >= float(stale_s):
        return None
    kit = load_kit(paths)
    try:
        mins = int(kit.get("autosave_min") or 0)
    except (TypeError, ValueError):
        return None
    if mins not in (5, 10, 20, 30):
        return None
    mark_path = paths.role("state", "control", AUTOSAVE_MARK)
    last_save = 0.0
    if mark_path.is_file():
        try:
            rec = json.loads(mark_path.read_text(encoding="utf-8"))
            last_save = float(rec.get("epoch") or 0) if isinstance(rec, dict) else 0.0
        except (OSError, ValueError, UnicodeDecodeError, TypeError):
            last_save = 0.0
    if last_save and (float(now) - last_save) < mins * 60:
        return None
    note = str(heartbeat.get("note") or "")
    seats = heartbeat.get("seats") if isinstance(heartbeat.get("seats"), list) else []
    creds = heartbeat.get("credentials") if isinstance(heartbeat.get("credentials"), list) else []
    skills = heartbeat.get("skills") if isinstance(heartbeat.get("skills"), list) else []
    if not (note.strip() or seats or creds or skills):
        record_session_beat(paths, {"dirty": False}, now=now, acted=False)
        return None
    session = {
        "sid": str(heartbeat.get("cosmos_sid") or heartbeat.get("stream") or "session"),
        "markdown": note,
        "record": {
            "stream": heartbeat.get("stream"),
            "turn_n": heartbeat.get("turn_n"),
            "context_pct": heartbeat.get("context_pct"),
            "tokens_in": heartbeat.get("tokens_in"),
        },
        "fields": {
            "pid": heartbeat.get("pid") or "",
            "state": "OPEN",
            "rail": heartbeat.get("rail") or "",
            "vendor_session_id": heartbeat.get("vendor_session_id") or "",
            "turn_n": heartbeat.get("turn_n") or 0,
        },
        "seats": seats,
        "credentials": creds,
        "skills": skills,
    }
    saved = autosave_tick(paths, session, kit=kit, rold=None)
    mark_path.parent.mkdir(parents=True, exist_ok=True)
    mark_path.write_text(json.dumps({
        "schema": "cosmos-autosave-mark/1",
        "epoch": float(now),
        "pack": saved.get("pack"),
    }, indent=1), encoding="utf-8")
    record_session_beat(paths, {"dirty": False}, now=now, acted=False)
    saved["due"] = True
    return saved


def _rold_update(session: dict, blobs: list[dict]) -> str:
    lines = ["# ROLD update", "", "Saved %s" % _now(), ""]
    for blob in blobs:
        lines.append("- %s → artifact `%s`" % (blob["name"], blob["sha256"]))
    for seat in session.get("seats") or []:
        if isinstance(seat, dict):
            lines.append("- seat %s → `%s`" % (seat.get("id"), seat.get("path")))
    for cred in session.get("credentials") or []:
        if isinstance(cred, dict):
            lines.append("- credential %s → `%s`" % (cred.get("rail"), cred.get("path")))
    for skill in session.get("skills") or []:
        if isinstance(skill, dict):
            lines.append("- skill %s → `%s`" % (skill.get("slug"), skill.get("path")))
    lines.append("")
    return redact("\n".join(lines))


def _index_session_events(rold: Path | None, session: dict) -> list[dict]:
    if rold is None:
        return []
    out = []
    for seat in session.get("seats") or []:
        if not isinstance(seat, dict):
            continue
        out.append(index_seat(
            rold, model_id=str(seat.get("id") or ""),
            harness=str(seat.get("harness") or ""),
            path=str(seat.get("path") or ""),
            seated_at=str(seat.get("seated_at") or "")))
    for cred in session.get("credentials") or []:
        if not isinstance(cred, dict):
            continue
        out.append(index_credential(
            rold, rail=str(cred.get("rail") or ""),
            kind=str(cred.get("kind") or "file"),
            path=str(cred.get("path") or ""),
            acquired_at=str(cred.get("acquired_at") or "")))
    for skill in session.get("skills") or []:
        if not isinstance(skill, dict):
            continue
        out.append(index_skill(
            rold, slug=str(skill.get("slug") or ""),
            description=str(skill.get("description") or ""),
            path=str(skill.get("path") or ""),
            demonstrated_at=str(skill.get("demonstrated_at") or ""),
            routine=str(skill.get("routine") or "")))
    return out


def render_skill(slug: str, description: str, steps: list[str],
                 when: str = "", title: str = "") -> str:
    """agentskills.io frontmatter. `name` is the slug the registry accepts."""
    desc = " ".join(description.split())
    lines = ["---", "name: %s" % slug, "description: %s" % desc]
    if when.strip():
        lines.append("when: %s" % " ".join(when.split()))
    lines += ["---", "", "# %s" % (title.strip() or slug), ""]
    for i, step in enumerate(steps, 1):
        lines.append("%d. %s" % (i, " ".join(step.split())))
    lines.append("")
    return "\n".join(lines)


def parse_skill_md(text: str) -> dict:
    rows = text.splitlines()
    name = rows[0][2:].strip() if rows and rows[0].startswith("# ") else ""
    desc, steps, when = [], [], []
    mode = "desc"
    for line in rows[1:]:
        if line.startswith("## Steps"):
            mode = "steps"
            continue
        if line.startswith("## When"):
            mode = "when"
            continue
        if line.startswith("## "):
            mode = "other"
            continue
        if mode == "desc":
            desc.append(line)
        elif mode == "when":
            when.append(line)
        elif mode == "steps":
            matched = re.match(r"\d+\.\s+(.*)", line.strip())
            if matched and matched.group(1).strip():
                steps.append(matched.group(1).strip())
    description = " ".join(part.strip() for part in desc if part.strip())
    return {
        "name": name,
        "description": description,
        "steps": steps,
        "when": " ".join(part.strip() for part in when if part.strip()),
    }


def _registry(paths):
    from cosmos_skills import open_registry
    return open_registry(paths.root)


def _propose_body(paths, body: str, *, rold: Path | None = None,
                  registry=None, principal: str = "seat:autosave") -> dict:
    """Propose one SKILL.md. The file lands at state/skills/proposed/<sha>."""
    from cosmos_skills import SkillError, parse_skill
    try:
        parsed = parse_skill(body)
    except SkillError as e:
        raise SessionProcedureError(e.kind, str(e)) from e
    reg = registry if registry is not None else _registry(paths)
    try:
        proposed = reg.propose(principal, body, rationale="demonstrated during session")
    except SkillError as e:
        raise SessionProcedureError(e.kind, str(e)) from e
    dest = paths.state("skills", "proposed", proposed["sha"], "SKILL.md")
    indexed = None
    if rold is not None:
        indexed = index_skill(
            rold, slug=parsed["name"], description=parsed["description"],
            path=str(dest))
    return {
        "slug": parsed["name"],
        "sha": proposed["sha"],
        "path": str(dest),
        "state": proposed["state"],
        "routine": str((parsed.get("meta") or {}).get("when") or ""),
        "indexed": indexed,
    }


def save_skill(paths, slug: str, *, name: str, description: str,
               steps: list[str], when: str = "", rold: Path | None = None,
               registry=None) -> dict:
    """Propose a skill. A second body keeps its own sha. Activation is CCr accept."""
    from cosmos_skills import NAME_RE
    if not NAME_RE.match(slug):
        raise SessionProcedureError("BAD_SLUG", slug)
    if not description.strip() or not steps:
        raise SessionProcedureError(
            "THIN_SKILL", "description and steps are required")
    body = render_skill(slug, description, steps, when, title=name)
    return _propose_body(paths, body, rold=rold, registry=registry)


def promote_inbox(paths, rold: Path | None = None, registry=None) -> dict:
    """Propose inbox skills. A thin note stays in state/skill_inbox."""
    from cosmos_skills import NAME_RE, SkillError, parse_skill
    inbox = paths.state("skill_inbox")
    promoted, skipped = [], []
    if not inbox.is_dir():
        return {"promoted": promoted, "skipped": skipped}
    reg = registry if registry is not None else _registry(paths)
    for child in sorted(p for p in inbox.iterdir() if p.is_dir()):
        if not NAME_RE.match(child.name):
            continue
        src = child / "SKILL.md"
        if not src.is_file():
            skipped.append({"slug": child.name, "why": "no SKILL.md"})
            continue
        text = src.read_text(encoding="utf-8")
        if text.lstrip().startswith("---"):
            try:
                sk = parse_skill(text)
            except SkillError as e:
                skipped.append({"slug": child.name, "why": e.kind})
                continue
            if sk["name"] != child.name:
                skipped.append({"slug": child.name, "why": "name"})
                continue
            promoted.append(_propose_body(
                paths, text, rold=rold, registry=reg))
            continue
        parsed = parse_skill_md(text)
        if not parsed["description"] or not parsed["steps"]:
            skipped.append({"slug": child.name, "why": "thin"})
            continue
        promoted.append(save_skill(
            paths, child.name, name=parsed["name"] or child.name,
            description=parsed["description"], steps=parsed["steps"],
            when=parsed["when"], rold=rold, registry=reg))
    return {"promoted": promoted, "skipped": skipped}


def preview_rung(paths, *, heartbeat: dict | None = None, pause: dict | None = None,
                tokens_in=None, compaction: bool = False) -> dict:
    """Decide the rung. Writes nothing."""
    kit = load_kit(paths)
    if isinstance(pause, dict) and str(pause.get("mode") or "").lower() == "hold":
        return {"act": "hold", "why": "operator hold", "engaged": False}
    action = next_action(
        kit, tokens_in, declined=declined_set(read_ask(paths)),
        compaction=compaction, heartbeat=heartbeat)
    action["engaged"] = False
    return action


def apply_rung(paths, repo, *, kit: dict, stream: str, session_type: str = "",
               reason: str, work: str = "", heartbeat: dict | None = None,
               tokens_in=None, compaction: bool = False, engage: bool = False,
               closer=None, bu_dir: Path | None = None, pause: dict | None = None,
               rold: Path | None = None) -> dict:
    """Ask, record a decline, or engage the close. HOLD does none of those."""
    if isinstance(pause, dict) and str(pause.get("mode") or "").lower() == "hold":
        return {"act": "hold", "why": "operator hold", "engaged": False}
    declined = declined_set(read_ask(paths))
    action = next_action(
        kit, tokens_in, declined=declined, compaction=compaction, heartbeat=heartbeat)
    action["engaged"] = False
    if action["act"] == "ask":
        action["flag"] = write_ask(
            paths, rung=float(action["pct"]), declined=declined, why=action["why"])
        return action
    if action["act"] == "force" and engage:
        def _closer():
            if closer is not None:
                return closer()
            from cosmos_kernel import Kernel
            return tidyup_close(Kernel(paths.root), stream, force=True)
        closed = close_resession(
            paths, repo, stream=stream, session_type=session_type, kit=kit,
            reason=reason or action["why"], work=work, closer=_closer, bu_dir=bu_dir)
        flag = ask_path(paths)
        if flag.is_file():
            flag.unlink()
        action["engaged"] = True
        action["close"] = closed
        if rold is not None:
            action["rold"] = str(rold)
    return action


def _selftest() -> int:
    import tempfile

    from cosmos_kernel import install
    from cosmos_paths import CosmosPaths

    results = []

    def check(label, fn):
        try:
            results.append((label, bool(fn()), ""))
        except Exception as e:  # noqa: BLE001
            results.append((label, False, f"{type(e).__name__}: {e}"))

    kit = {
        "cos": {"rold": True, "tidyup": True, "tu2": True, "bu": True},
        "resession": {
            "ask_pct": [0.75, 0.80, 0.85],
            "force_pct": 0.92,
            "close_tokens": 190000,
            "window_tokens": 200000,
            "on_compaction": True,
            "on_token_count": True,
        },
    }
    ask, force = ladder(kit)
    check("default ladder is 75 80 85 then 92",
          lambda: ask == (0.75, 0.80, 0.85) and force == 0.92)
    check("74 percent is idle",
          lambda: next_action(kit, 148000, declined=set())["act"] == "idle")
    check("75 percent asks",
          lambda: next_action(kit, 150000, declined=set())["act"] == "ask"
          and next_action(kit, 150000, declined=set())["pct"] == 0.75)
    check("a decline at 75 waits until 80",
          lambda: next_action(kit, 155000, declined={canon_pct(0.75)})["act"] == "idle"
          and next_action(kit, 160000, declined={canon_pct(0.75)})["pct"] == 0.80)
    declined_all = {canon_pct(x) for x in (0.75, 0.80, 0.85)}
    check("184000 does not close",
          lambda: next_action(kit, 184000, declined=declined_all)["act"] == "idle")
    check("190000 tokens closes",
          lambda: next_action(kit, 190000, declined=declined_all)["act"] == "force")
    check("compaction asks at the first rung",
          lambda: next_action(kit, 10, declined=set(), compaction=True)["why"] == "compaction")
    check("a secret in the session text is redacted",
          lambda: "sk-live" not in redact("token sk-live-secret-value"))

    td = Path(tempfile.mkdtemp(prefix="cosmos_proc_"))
    root = install(td / "live", tree_id="spike-proc")
    paths = CosmosPaths(root)
    repo = td / "repo"
    (repo / "docs").mkdir(parents=True)
    for name in ("WISHLIST.md", "BACKLOG.md", "MOTIF_TRACKER.md"):
        (repo / "docs" / name).write_text("- [x] done\n", encoding="utf-8")
    calls = []

    def closer():
        calls.append("tidyup")
        seed = paths.state("SEED.json")
        seed.parent.mkdir(parents=True, exist_ok=True)
        seed.write_text("{}\n", encoding="utf-8")
        paths.state("SEED.decl.json").write_text("{}\n", encoding="utf-8")
        return seed

    held = apply_rung(
        paths, repo, kit=kit, stream="Cm", reason="hold", pause={"mode": "hold"},
        tokens_in=190000, engage=True, closer=closer)
    check("operator hold does not close",
          lambda: held["act"] == "hold" and calls == [])
    asked = apply_rung(
        paths, repo, kit=kit, stream="Cm", reason="ask", tokens_in=150000,
        engage=True, closer=closer)
    check("75 percent writes the ask and does not close",
          lambda: asked["act"] == "ask" and calls == []
          and ask_path(paths).is_file())
    decline_rung(paths, 0.75)
    decline_rung(paths, 0.80)
    decline_rung(paths, 0.85)
    forced = apply_rung(
        paths, repo, kit=kit, stream="Cm", reason="full", work="continue the route",
        tokens_in=190000, engage=True, closer=closer, bu_dir=td / "bu")
    check("190000 tokens runs TidyUP then TU2 then BU",
          lambda: forced["engaged"] is True
          and forced["close"]["steps"] == ["tidyup", "tu2", "bu"]
          and calls == ["tidyup"])
    bu = Path(forced["close"]["bu"])
    check("the BU file is the Cm pointer",
          lambda: bu.name == "BUCm.toml" and "continue the route" in bu.read_text(encoding="utf-8"))
    check("the ask flag is cleared after the close",
          lambda: not ask_path(paths).is_file())
    closed_pack = Path(forced["close"]["pack"])
    check("the close pack is a session save",
          lambda: json.loads((closed_pack / "MANIFEST.json").read_text(
              encoding="utf-8"))["schema"] == "cosmos-session-save/1"
          and (closed_pack / "BANNER.txt").is_file()
          and (closed_pack / "TIDYUP.md").is_file()
          and (closed_pack / "tu2_adversarial.json").is_file())
    xt = close_resession(
        paths, repo, stream="XTalk", session_type="XTalk", kit=kit,
        reason="xt", closer=closer, bu_dir=td / "xt")
    check("XTalk writes BUxt.toml in the seat directory",
          lambda: Path(xt["bu"]).name == "BUxt.toml")
    bad_stream = False
    try:
        bu_name("nope")
    except SessionProcedureError as e:
        bad_stream = e.kind == "BAD_STREAM"
    check("an unknown stream has no BU file", lambda: bad_stream)
    check("a chair role is not a session type",
          lambda: session_identity({"role": "CCr", "cosmos_sid": "Cm"}) == ("Cm", "")
          and bu_name("Cm", "") == "BUCm.toml"
          and bu_name("Cm", "ccr-Cm-g46-tui") == "BUCm.toml")
    check("an explicit session type picks its BU file",
          lambda: bu_name(*session_identity(
              {"stream": "Cm", "session_type": "XTalk"})) == "BUxt.toml")

    rold = td / "ROLD"
    rold.mkdir()
    (rold / "00_INDEX.md").write_text("# ROLD — 00_INDEX\n", encoding="utf-8")
    seat_file = td / "seat.json"
    seat_file.write_text('{"seated": true}\n', encoding="utf-8")
    cred = td / "rail.txt"
    cred.write_text("sk-live-secret-value\n", encoding="utf-8")
    skill_body = save_skill(
        paths, "resession-ask", name="Resession ask",
        description="Ask at three rungs, then close.",
        steps=["Read the ask flag.", "Decline or close."],
        when="context percent crosses a rung", rold=rold)
    again = save_skill(
        paths, "resession-ask", name="Resession ask",
        description="Ask at three rungs, then close.",
        steps=["Read the ask flag.", "Close at 92."],
        when="context percent crosses a rung", rold=rold)
    first_body = Path(skill_body["path"]).read_text(encoding="utf-8")
    second_body = Path(again["path"]).read_text(encoding="utf-8")
    check("a second skill save keeps the previous body",
          lambda: skill_body["state"] == "PROPOSED"
          and again["state"] == "PROPOSED"
          and skill_body["sha"] != again["sha"]
          and "Decline or close." in first_body
          and "Close at 92." in second_body
          and not paths.state("skills", "active").exists())
    inbox = paths.state("skill_inbox", "pack-pointer")
    inbox.mkdir(parents=True)
    (inbox / "SKILL.md").write_text(
        "# Pack pointer\n\nPoint at the pack.\n\n## Steps\n\n1. Read TIDYUP.md\n",
        encoding="utf-8")
    thin = paths.state("skill_inbox", "thin-skill")
    thin.mkdir(parents=True)
    (thin / "SKILL.md").write_text("# Thin\n\nNo steps yet.\n", encoding="utf-8")
    promoted = promote_inbox(paths, rold=rold)
    check("inbox promotion keeps a thin skill and saves a complete one",
          lambda: [row["slug"] for row in promoted["promoted"]] == ["pack-pointer"]
          and promoted["promoted"][0]["state"] == "PROPOSED"
          and promoted["skipped"][0]["slug"] == "thin-skill"
          and not paths.state("skills", "active").exists())
    saved = autosave_tick(paths, {
        "sid": "Cm",
        "markdown": "aim sk-live-secret-value",
        "record": {"aim": "continue"},
        "fields": {"state": "OPEN", "stream": "Cm"},
        "seats": [{"id": "openai/gpt-5.6-luna", "harness": "codex",
                   "path": str(seat_file)}],
        "credentials": [{"rail": "openrouter", "kind": "api_key_file",
                         "path": str(cred)}],
    }, kit=kit, rold=rold)
    pack = Path(saved["pack"])
    from cosmos_packet import cas_dir
    session_md = (pack / "SESSION.md").read_text(encoding="utf-8")
    cred_index = (rold / "credentials.toml").read_text(encoding="utf-8")
    auto = json.loads((pack / "AUTOSAVE.json").read_text(encoding="utf-8"))
    manifest = json.loads((pack / "MANIFEST.json").read_text(encoding="utf-8"))
    sha = auto["artifacts"][0]["sha256"]
    check("autosave redacts, stores an artifact, and indexes the seat",
          lambda: "sk-live" not in session_md
          and "[redacted]" in session_md
          and manifest["schema"] == "cosmos-session-save/1"
          and (cas_dir(paths) / sha).is_file()
          and not paths.state("artifacts").exists()
          and "openai/gpt-5.6-luna" in (rold / "seats.toml").read_text(encoding="utf-8")
          and "sk-live-secret-value" not in cred_index
          and lookup(rold, "credential", str(cred))["path"] == str(cred))

    stamp_dir = td / "stamps"
    stamp_dir.mkdir()
    moment = datetime(2026, 10, 1, 12, 0, 0)
    first_name = _stamp(stamp_dir, now=moment)
    (stamp_dir / first_name).mkdir()
    second_name = _stamp(stamp_dir, now=moment)
    check("two saves in one second get two names",
          lambda: first_name != second_name and second_name.endswith("_01"))
    beat = record_session_beat(paths, {
        "stream": "Cm", "cosmos_sid": "Cm", "role": "CCr",
        "pid": 1, "rail": "grok", "turn_n": 2,
        "tokens_in": 150000, "context_pct": 0.75,
        "note": "aim sk-live-secret-value",
        "seed_hmac": "should-drop", "dirty": True,
    }, now=5000.0, acted=True)
    beat_text = paths.role("state", "control", BEAT_NAME).read_text(encoding="utf-8")
    check("a session beat stores the window and drops the secret",
          lambda: beat["tokens_in"] == 150000 and beat["context_pct"] == 0.75
          and beat["last_act_epoch"] == 5000.0 and beat["stream"] == "Cm"
          and "sk-live" not in beat_text and "should-drop" not in beat_text
          and "[redacted]" in beat_text)
    saved_auto = maybe_autosave(
        paths, beat, now=5000.0, pid_alive=True, stale_s=180.0)
    auto_md = (Path(saved_auto["pack"]) / "SESSION.md").read_text(encoding="utf-8") if saved_auto else ""
    again = maybe_autosave(
        paths, {**beat, "dirty": True, "last_act_epoch": 5000.0},
        now=5060.0, pid_alive=True, stale_s=180.0)
    dead_save = maybe_autosave(
        paths, {**beat, "dirty": True, "last_act_epoch": 5000.0},
        now=5000.0, pid_alive=False, stale_s=180.0)
    check("a fresh dirty beat autosaves once",
          lambda: saved_auto is not None and again is None and dead_save is None
          and "sk-live" not in auto_md and "[redacted]" in auto_md)

    failed = [label for label, ok, _err in results if not ok]
    for label, ok, err in results:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (session procedures)"
          % ("PASS" if not failed else "FAIL", len(results)))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(_selftest())
