#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""regen_refusal_taxonomy.py -- keep docs/REFUSAL_TAXONOMY.md a live projection.

The taxonomy is READ OUT OF THE AST (`cosmos/cosmos_refusals.py`). The markdown
is a projection. Agents add a kind; the projection goes stale; the only repair
was a hand regen. That step has drifted THREE times today (CHANGELOG: 11:20,
12:03, 13:43) after this module already existed with --diff/--write. A
recurring manual step is the thing that silently rots -- the same defect
class builds/cdeck/remeasure_probes.py closed for probe artifacts.

THIS FILE is the remesure-shaped loop:

    py -3.14 builds/probe/regen_refusal_taxonomy.py            # heal only stale
    py -3.14 builds/probe/regen_refusal_taxonomy.py --check    # rc=1 if stale; no write
    py -3.14 builds/probe/regen_refusal_taxonomy.py --diff     # rc=2 on drift; no write
    py -3.14 builds/probe/regen_refusal_taxonomy.py --write    # heal, rc=2 this tick

Default (no flags) is refresh_if_stale -- the hand ``--out`` paste is no
longer the heal path. ``--check`` makes drift impossible to ship without
anyone remembering to regen. test_refusal_taxonomy.py calls
refresh_if_stale before the live MATCH gate, the same way
test_artifact_freshness.py calls remeasure_claims.refresh_stale.

``tests/test_refusals.py`` is NOT weakened: it still fails the same tick
if it runs first. This writer heals so the *next* consumer is green.

Why ``--out`` and never ``>``: ``cosmos_refusals.main`` documents the scar.
A Windows console codepage (cp437) turns every em-dash in the table into a
replacement char. ``--out`` writes UTF-8. A regen that used ``>`` would
itself be drift.

COSMOS_SKIP_TAXONOMY_REMEASURE=1 is the bite hatch that must observe stale.

READ-ONLY unless default / ``--write`` / refresh_if_stale. Imports
cosmos_refusals (AST surveyor); never imports a rail, never opens a
credential.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
COSMOS = REPO / "cosmos"
DOC_REL = Path("docs") / "REFUSAL_TAXONOMY.md"
ARTIFACT = "docs/REFUSAL_TAXONOMY.md"
SCHEMA = "cosmos-refusal-taxonomy-regen/1"
SKIP_ENV = "COSMOS_SKIP_TAXONOMY_REMEASURE"
RECEIPT = HERE / "REMEASURE_TAXONOMY.json"

# The command that actually works. Printed verbatim on drift so an agent
# that cannot find the writer still has one pasteable line.
REGEN_COMMAND = r"py -3.14 cosmos\cosmos_refusals.py --out docs\REFUSAL_TAXONOMY.md"
# The command the GENERATED doc still prints (cosmos_refusals.render_table).
# Named so a reader can see why we refuse to run it.
WRONG_REDIRECT = r"py -3.14 cosmos\cosmos_refusals.py --render > docs\REFUSAL_TAXONOMY.md"


class TaxonomyRegenError(RuntimeError):
    """Typed refusal. kind in {NO_GENERATOR, DOC_ABSENT, DRIFT, UNWRITABLE, BAD_ARGS}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        self.detail = detail
        super().__init__(f"[{kind}] {detail}")


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def load_generator():
    gen = COSMOS / "cosmos_refusals.py"
    if not gen.is_file():
        raise TaxonomyRegenError("NO_GENERATOR", f"missing {gen}")
    sys.path.insert(0, str(COSMOS))
    import cosmos_refusals as refusals  # noqa: WPS433
    return refusals


def fresh_render(refusals=None, *, code_dir: Path | None = None) -> tuple[str, dict]:
    """UTF-8 markdown + the survey facts a heartbeat can name.

    ``code_dir`` is the tree to survey. Default is the generator's own
    parent (live ``cosmos/``). A scratch copy with an extra kind is how
    the remesure loop is proven, and must not survey the live tree.
    """
    refusals = refusals or load_generator()
    survey_dir = Path(code_dir) if code_dir is not None else Path(
        refusals.__file__).resolve().parent
    sv = refusals.survey(survey_dir)
    return refusals.render_table(sv), sv


def first_diff_line(a: str, b: str) -> int | None:
    la, lb = a.splitlines(), b.splitlines()
    n = max(len(la), len(lb))
    for i in range(n):
        left = la[i] if i < len(la) else ""
        right = lb[i] if i < len(lb) else ""
        if left != right:
            return i + 1
    if a != b:
        return 1
    return None


def compare(on_disk: str | None, fresh: str) -> dict:
    """Match is byte-identity of the unicode strings after UTF-8 decode.

    An absent filed projection is DRIFT, never a skip. Skipping an absent
    projection is how a missing taxonomy stays missing.
    """
    if on_disk is None:
        return {
            "match": False,
            "kind": "DOC_ABSENT",
            "on_disk_chars": None,
            "fresh_chars": len(fresh),
            "first_diff_line": None,
        }
    if on_disk == fresh:
        return {
            "match": True,
            "kind": "MATCH",
            "on_disk_chars": len(on_disk),
            "fresh_chars": len(fresh),
            "first_diff_line": None,
        }
    return {
        "match": False,
        "kind": "DRIFT",
        "on_disk_chars": len(on_disk),
        "fresh_chars": len(fresh),
        "first_diff_line": first_diff_line(on_disk, fresh),
    }


def read_doc(path: Path) -> str | None:
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8")


def stage_incumbent(doc: Path, repo: Path) -> Path | None:
    """Never-delete: copy the filed doc aside before overwrite."""
    if not doc.is_file():
        return None
    dest = repo / "_delme" / f"predispose_refusal_taxonomy_{_now()}"
    dest.mkdir(parents=True, exist_ok=True)
    staged = dest / "REFUSAL_TAXONOMY.md"
    shutil.copy2(doc, staged)
    return staged


def write_utf8(path: Path, text: str) -> None:
    """Write LF UTF-8. Never a console redirect."""
    tmp = path.with_name(path.name + ".tmp")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp.write_text(text, encoding="utf-8", newline="\n")
        tmp.replace(path)
    except OSError as e:
        raise TaxonomyRegenError("UNWRITABLE", f"{path}: {e}") from e
    finally:
        if tmp.exists():
            try:
                tmp.unlink()
            except OSError:
                pass


def cp437_mangle(text: str) -> str:
    """What ``> docs\\REFUSAL_TAXONOMY.md`` does on a US OEM console."""
    return text.encode("cp437", errors="replace").decode("cp437")


def tick(*, repo: Path | None = None, write: bool = False,
         code_dir: Path | None = None) -> dict:
    """One compare, optional heal. ``ok`` is match-before-heal, never after.

    Healing this tick does not flip ``ok``: the red is how the drift is
    noticed. The next clock tick sees MATCH. ``refresh_if_stale`` is the
    remesure entry that heals first so a later MATCH gate can be green.
    """
    repo = Path(repo) if repo is not None else REPO
    doc = repo / DOC_REL
    refusals = load_generator()
    fresh, sv = fresh_render(refusals, code_dir=code_dir)
    on_disk = read_doc(doc)
    cmp = compare(on_disk, fresh)
    healed = False
    staged = None
    if write and not cmp["match"]:
        staged_path = stage_incumbent(doc, repo)
        staged = str(staged_path) if staged_path else None
        write_utf8(doc, fresh)
        healed = True
        after = read_doc(doc)
        if after != fresh:
            raise TaxonomyRegenError(
                "UNWRITABLE",
                f"wrote {doc} but read-back does not match the render",
            )
    payload = {
        "schema": SCHEMA,
        "ok": bool(cmp["match"]),
        "match": bool(cmp["match"]),
        "kind": cmp["kind"],
        "healed": healed,
        "command": REGEN_COMMAND,
        "wrong_command": WRONG_REDIRECT,
        "why_not_redirect": (
            "Windows console codepage (cp437) mangles em-dashes; "
            "--out writes UTF-8. Never regenerate with '>'."
        ),
        "doc": str(doc),
        "render_chars": cmp["fresh_chars"],
        "on_disk_chars": cmp["on_disk_chars"],
        "typed_refusal_classes": sv["typed_refusal_classes"],
        "distinct_kinds": len(sv["kinds"]),
        "modules_parsed": sv["modules_parsed"],
        "first_diff_line": cmp["first_diff_line"],
        "staged": staged,
        "cp437_would_drift": cp437_mangle(fresh) != fresh,
    }
    return payload


def _skip() -> bool:
    return os.environ.get(SKIP_ENV) == "1"


def stale_in(repo: Path | None = None,
             names: list[str] | None = None,
             *,
             code_dir: Path | None = None) -> list[str]:
    """Artifact names whose filed projection does not MATCH a fresh render.

    Same shape as remeasure_probes.stale_in / remeasure_claims.stale_in.
    An absent doc is stale (DOC_ABSENT), never a skip.
    """
    repo = Path(repo) if repo is not None else REPO
    want = names or [ARTIFACT]
    out: list[str] = []
    for name in want:
        norm = str(name).replace("\\", "/")
        if norm != ARTIFACT:
            continue
        payload = tick(repo=repo, write=False, code_dir=code_dir)
        if not payload["match"]:
            out.append(ARTIFACT)
    return out


def refresh_if_stale(names: list[str] | None = None, *,
                     force: bool = False,
                     label: str | None = None,
                     repo: Path | None = None,
                     code_dir: Path | None = None) -> dict:
    """Heal every named (or catalogued) taxonomy artifact that is not MATCH.

    No-op when COSMOS_SKIP_TAXONOMY_REMEASURE=1 (the bite path that must
    observe stale). Returns a receipt dict. ``ok`` of the inner tick stays
    match-before-heal; the receipt's stale_after is the post-heal state.
    """
    if _skip():
        return {"skipped": True, "reason": SKIP_ENV, "kind": "REMEASURE_TAXONOMY"}
    repo = Path(repo) if repo is not None else REPO
    label = label or ("AFTER-REMEASURE-" + time.strftime("%Y-%m-%dT%H%M"))
    selected = list(names) if names else [ARTIFACT]
    unknown = [n for n in selected if str(n).replace("\\", "/") != ARTIFACT]
    if unknown:
        raise TaxonomyRegenError("BAD_ARGS", f"unknown taxonomy artifact(s): {unknown}")
    ran: list[str] = []
    skipped_fresh: list[str] = []
    stale_before = stale_in(repo, selected, code_dir=code_dir)
    for name in selected:
        if not force and ARTIFACT not in stale_before:
            skipped_fresh.append(ARTIFACT)
            continue
        tick(repo=repo, write=True, code_dir=code_dir)
        ran.append(ARTIFACT)
    stale_after = stale_in(repo, selected, code_dir=code_dir)
    receipt = {
        "kind": "REMEASURE_TAXONOMY",
        "label": label,
        "probed_at_epoch": time.time(),
        "ran": ran,
        "skipped_fresh": skipped_fresh,
        "stale_before": stale_before,
        "stale_after": stale_after,
        "artifact": ARTIFACT,
        "skip_env": SKIP_ENV,
        "repo": str(repo),
        "code_dir": str(code_dir) if code_dir is not None else None,
    }
    if repo.resolve() == REPO.resolve() and (ran or stale_before):
        RECEIPT.write_text(json.dumps(receipt, indent=1, default=str) + "\n",
                           encoding="utf-8", newline="\n")
    return receipt


def refresh_stale(*, reason: str = "refresh_stale",
                  repo: Path | None = None,
                  code_dir: Path | None = None) -> dict:
    """test_refusal_taxonomy entry: heal whatever is currently not MATCH."""
    names = stale_in(repo, code_dir=code_dir)
    if not names:
        return {"ran": [], "skipped_fresh": [ARTIFACT], "reason": reason,
                "kind": "REMEASURE_TAXONOMY"}
    print(f"[remeasure] {reason}: stale {names}")
    return refresh_if_stale(
        names, label="AFTER-REMEASURE-" + time.strftime("%Y-%m-%dT%H%M"),
        repo=repo, code_dir=code_dir)


def _print_drift(payload: dict) -> None:
    print("FAIL  docs/REFUSAL_TAXONOMY.md has drifted from cosmos/*.py")
    print(f"  kind:            {payload['kind']}")
    print(f"  first_diff_line: {payload['first_diff_line']}")
    print(f"  on_disk_chars:   {payload['on_disk_chars']}")
    print(f"  fresh_chars:     {payload['render_chars']}")
    print(f"  typed_classes:   {payload['typed_refusal_classes']}")
    print(f"  distinct_kinds:  {payload['distinct_kinds']}")
    print("  regenerate with EXACTLY this command (UTF-8 --out, not '>' ):")
    print(f"    {payload['command']}")
    print(f"  or: py -3.14 builds\\probe\\regen_refusal_taxonomy.py --write")
    print(f"  do NOT run: {payload['wrong_command']}")
    print(f"  ({payload['why_not_redirect']})")
    if payload["healed"]:
        print("  healed this tick; the next selftest-clock tick will MATCH.")
        if payload["staged"]:
            print(f"  incumbent staged at {payload['staged']}")


def _print_tick(payload: dict) -> None:
    print("live_value: " + json.dumps(
        {k: payload[k] for k in (
            "ok", "match", "kind", "healed", "render_chars",
            "on_disk_chars", "typed_refusal_classes", "distinct_kinds",
            "first_diff_line", "command", "cp437_would_drift")},
        sort_keys=True))
    if payload["match"]:
        print("OK    docs/REFUSAL_TAXONOMY.md matches a fresh UTF-8 render")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="diff / heal docs/REFUSAL_TAXONOMY.md against cosmos/")
    ap.add_argument("--diff", action="store_true",
                    help="compare only; exit 2 on drift/absent")
    ap.add_argument("--write", action="store_true",
                    help="heal on drift (stage incumbent, UTF-8 --out)")
    ap.add_argument("--check", action="store_true",
                    help="report stale artifacts and exit 1 if any; do not re-run")
    ap.add_argument("--force", action="store_true",
                    help="heal even if currently matching (rewrite the projection)")
    ap.add_argument("--repo", default=None,
                    help="repo root (default: two parents above this file)")
    ap.add_argument("--code-dir", default=None,
                    help="directory of .py files to survey (default: live cosmos/)")
    ap.add_argument("--json-out", default=None,
                    help="write the tick/receipt payload as UTF-8 JSON")
    a = ap.parse_args(argv)
    if a.diff and a.write:
        raise TaxonomyRegenError(
            "BAD_ARGS", "use --diff OR --write, not both")
    if a.check and a.write:
        raise TaxonomyRegenError(
            "BAD_ARGS", "use --check OR --write, not both")
    if a.check and a.diff:
        raise TaxonomyRegenError(
            "BAD_ARGS", "use --check OR --diff, not both")
    repo = Path(a.repo) if a.repo else REPO
    code_dir = Path(a.code_dir) if a.code_dir else None

    if a.check:
        stale = stale_in(repo, code_dir=code_dir)
        payload = tick(repo=repo, write=False, code_dir=code_dir)
        report = {
            "kind": "REMEASURE_CHECK",
            "artifacts_dir": str(repo),
            "code_dir": str(code_dir) if code_dir is not None else str(COSMOS),
            "stale": stale,
            "match": payload["match"],
            "tick_kind": payload["kind"],
            "typed_refusal_classes": payload["typed_refusal_classes"],
            "distinct_kinds": payload["distinct_kinds"],
            "first_diff_line": payload["first_diff_line"],
            "command": payload["command"],
        }
        if a.json_out:
            Path(a.json_out).write_text(
                json.dumps(report, indent=2, sort_keys=True) + "\n",
                encoding="utf-8", newline="\n")
        print(json.dumps(report, indent=1))
        return 1 if stale else 0

    if a.diff or a.write:
        payload = tick(repo=repo, write=bool(a.write), code_dir=code_dir)
        if a.json_out:
            Path(a.json_out).write_text(
                json.dumps(payload, indent=2, sort_keys=True) + "\n",
                encoding="utf-8", newline="\n")
        _print_tick(payload)
        if payload["match"]:
            return 0
        _print_drift(payload)
        return 2

    # Default: remesure_probes shape -- heal only stale, rc=1 if still stale.
    receipt = refresh_if_stale(
        force=a.force, repo=repo, code_dir=code_dir)
    if a.json_out:
        Path(a.json_out).write_text(
            json.dumps(receipt, indent=2, sort_keys=True, default=str) + "\n",
            encoding="utf-8", newline="\n")
    print(json.dumps({
        "kind": receipt.get("kind"),
        "ran": receipt.get("ran"),
        "skipped_fresh": receipt.get("skipped_fresh"),
        "stale_before": receipt.get("stale_before"),
        "stale_after": receipt.get("stale_after"),
        "skipped": receipt.get("skipped"),
        "artifact": receipt.get("artifact"),
    }, indent=1))
    if receipt.get("skipped"):
        return 0
    if receipt.get("stale_after"):
        return 1
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except TaxonomyRegenError as e:
        print(f"FAIL  [{e.kind}] {e.detail}")
        raise SystemExit(2)
