#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_refusals.py -- the refusal taxonomy, DERIVED from the code.

PHASE 5, docs/CORE_RESTRUCTURE.md: "collect every `*Error(kind, detail)` into a
single documented set so a caller can branch on `kind` without knowing which
module raised."

The obvious way to do that is a hand-written table in docs/. This codebase has
already paid for that (pattern 3, "prose used as specification" -- a docstring
contradicted two tests and cost an audit a regression). A hand-written refusal
table would be stale the first time somebody adds a kind, and nothing would say
so. So the taxonomy is not written; it is READ OUT OF THE AST and rendered. The
markdown is a projection, the code is the source -- the same move Phase 2 made
for the tracker.

What it answers, mechanically:

  * WHICH classes carry the `(kind, detail)` refusal shape (including the ones
    that inherit it, e.g. CodexRailError <- cosmos_rail_base.RailError).
  * WHICH kinds each actually raises -- the raise sites, not the docstring.
  * COLLISIONS: one kind string raised by more than one class. Some are healthy
    (BAD_SPEC means the same thing in all five rails); some are the thing a
    caller branching on `kind` alone would get wrong. The tool reports the set;
    only a human decides which is which, so the verdict is recorded here in
    KNOWN_COLLISIONS rather than guessed at each run.
  * GAPS: kinds a class documents (`kind in {A, B}`) but never raises, and kinds
    it raises but never documents. This is the drift check, and it is the reason
    the module can claim to be a gate rather than a pretty-printer: run it and
    it names real disagreements in the live tree.

READ-ONLY. This module imports nothing from COSMOS and writes nothing outside a
path you hand it. It parses source text; it never imports the modules it
surveys, so surveying a rail cannot start a rail.
"""
from __future__ import annotations

import argparse
import ast
import builtins
import json
import re
import sys
from pathlib import Path

# A refusal class is one whose __init__ takes `kind` as its first real
# parameter. Not "the name ends in Error" -- CosmosPathError and LedgerError end
# in Error and carry a plain message, and lumping them in would make the
# taxonomy a lie about what a caller can branch on.
KIND_PARAM = "kind"

# How a class docstring declares its kinds. TWO conventions are in the tree --
# `kind in {A, B}` (the rails) and "`kind` is one of A, B" (cosmos_paths) -- and
# a reader of only the first would have concluded CosmosPathError declared
# nothing. Both are matched; neither is blessed.
_DOC_KINDS = (
    re.compile(r"kind`?\s+in\s*\{([^}]*)\}"),
    re.compile(r"kind`?\s+is\s+one\s+of\s+([^.]*)"),
)
_KIND_TOKEN = re.compile(r"[A-Z][A-Z0-9_]{2,}")

# The human verdicts on shared kind strings, from reading every raise site
# (2026-08-31). A collision is only a DEFECT when the same string means
# different things to a caller; when six rails all mean "the spec is malformed"
# it is the taxonomy WORKING -- that is precisely the branch-on-kind-without-
# knowing-the-module property Phase 5 is after. Recorded here so the judgement
# is reviewable, and so a NEW collision shows up as UNREVIEWED instead of
# blending into the benign ones.
KNOWN_COLLISIONS = {
    # kind: (verdict, note)
    "BAD_ENTRY": ("BENIGN", "one meaning: a record in a declarative list is malformed"),
    "BAD_INPUT": ("BENIGN", "one meaning: a caller-supplied argument is invalid"),
    "BAD_NODE": ("BENIGN", "one meaning: the node spec is malformed"),
    "BAD_OUT": ("BENIGN", "one meaning: the output target is unusable"),
    "BAD_SPEC": ("BENIGN", "one meaning: the rail spec is malformed"),
    "BAD_TASK": ("BENIGN", "one meaning: the task record is malformed"),
    "BROKE": ("BENIGN", "one meaning: a programmer error on this seam"),
    "DENIED": ("SYNONYM", "policy declined -- see the policy_declined cluster"),
    "DUPLICATE": ("BENIGN", "one meaning: an id appears twice in a registry"),
    "HASH_MISMATCH": ("BENIGN", "one meaning: content did not hash to what was declared"),
    "IDENTITY_MISMATCH": ("BENIGN", "one meaning: what was found is not what was declared"),
    "NOT_FOUND": ("BENIGN", "one meaning: the named thing is absent; the referent is in detail"),
    "NO_DEST": ("BENIGN", "one meaning: no destination was resolvable"),
    "NO_KEY": ("BENIGN", "one meaning: a required credential is absent"),
    "NO_RAIL": ("BENIGN", "one meaning: the named rail is absent or unknown"),
    "NO_ROOT": ("BENIGN", "one meaning: the COSMOS root did not verify"),
    "NO_SESSION": ("BENIGN", "one meaning: the named session does not exist"),
    "REFUSED": ("SYNONYM", "policy declined -- see the policy_declined cluster"),
    "REPLAY": ("BENIGN", "one meaning: the fence for this work is already held"),
    "UNKNOWN_KIND": ("BENIGN", "one meaning: a kind string outside the known set"),
    "UNPARSEABLE": ("BENIGN", "one meaning: bytes were read but did not parse"),
    "UNREACHABLE": ("BENIGN", "one meaning: the far endpoint did not answer"),
    "UNREADABLE": ("BENIGN", "one meaning: the bytes could not be read at all"),
}

# The REAL taxonomy defect, and the inverse of a collision: one concept wearing
# three kind strings, so a caller asking "was I blocked by policy?" must know
# all three or silently mishandle one. Each cluster carries the evidence that
# made it a finding rather than an opinion -- sites where the SAME event is
# relabelled as it crosses a seam.
SYNONYM_CLUSTERS = {
    "policy_declined": {
        "kinds": ("DENIED", "NOT_PERMITTED", "REFUSED"),
        "evidence": (
            "cosmos_rails.Dispatcher.dispatch catches SpendError('DENIED') and "
            "re-raises RailError('NOT_PERMITTED'); cosmos_node_worker, "
            "cosmos_bucket_daemon and cosmos_node_bucket_worker each catch the "
            "same SpendError('DENIED') and emit a result dict with "
            "kind='NOT_PERMITTED'. One spend refusal, two names, and a third "
            "('REFUSED') used for the same concept across the rails, "
            "cosmos_command and cosmos_workspace."
        ),
    },
}


def _dotted(node) -> str:
    """Best-effort dotted name for a Name/Attribute node. '' when neither."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        head = _dotted(node.value)
        return f"{head}.{node.attr}" if head else node.attr
    return ""


def _doc_kinds(doc: str | None) -> list[str]:
    if not doc:
        return []
    found: set[str] = set()
    for rx in _DOC_KINDS:
        for m in rx.finditer(doc):
            found |= set(_KIND_TOKEN.findall(m.group(1)))
    return sorted(found)


class _ModuleScan:
    """One parsed module: the classes it defines, and every raise/except in it."""

    def __init__(self, path: Path, tree: ast.Module):
        self.path = path
        self.module = path.stem
        self.classes: dict[str, dict] = {}
        # local name -> (source module, ORIGINAL name). The original name is not
        # decoration: cosmos_codex_rail does `RailError as RailSeamError`, and
        # resolving the local name against the source module would look for a
        # `cosmos_rail_base.RailSeamError` that does not exist -- which is
        # exactly how CodexRailError lost its inherited (kind, detail) shape the
        # first time this ran.
        self.imports: dict[str, tuple[str, str]] = {}
        self.raises: list[tuple[str, str, int]] = []   # (cls_name, kind, line)
        self.excepts: list[tuple[str, int]] = []       # (cls_name, line)

        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                for a in node.names:
                    self.imports[a.asname or a.name] = (node.module, a.name)
            elif isinstance(node, ast.ClassDef):
                self._class(node)
            elif isinstance(node, ast.Raise):
                self._raise(node)
            elif isinstance(node, ast.ExceptHandler):
                self._except(node)

    @staticmethod
    def _is_error(node: ast.ClassDef) -> bool:
        """An error class: named like one, or derived from one. Anything else is
        a Rail/Kernel/Ledger and none of this module's business."""
        names = [node.name] + [_dotted(b).split(".")[-1] for b in node.bases]
        return any(n.endswith(("Error", "Refusal", "Exception")) for n in names)

    def _class(self, node: ast.ClassDef) -> None:
        if not self._is_error(node):
            return
        own_kind_shape = None
        for sub in node.body:
            if isinstance(sub, ast.FunctionDef) and sub.name == "__init__":
                args = [a.arg for a in sub.args.args]
                own_kind_shape = len(args) > 1 and args[1] == KIND_PARAM
                break
        self.classes[node.name] = {
            "module": self.module,
            "name": node.name,
            "line": node.lineno,
            "bases": [_dotted(b) for b in node.bases],
            "own_shape": own_kind_shape,          # None = defines no __init__
            "doc_kinds": _doc_kinds(ast.get_docstring(node)),
        }

    def _raise(self, node: ast.Raise) -> None:
        exc = node.exc
        if not isinstance(exc, ast.Call):
            return
        name = _dotted(exc.func).split(".")[-1]
        if not name.endswith(("Error", "Refusal")):
            return
        kind = "<dynamic>"
        if exc.args and isinstance(exc.args[0], ast.Constant) \
                and isinstance(exc.args[0].value, str):
            kind = exc.args[0].value
        self.raises.append((name, kind, node.lineno))

    def _except(self, node: ast.ExceptHandler) -> None:
        t = node.type
        if t is None:
            return
        parts = t.elts if isinstance(t, ast.Tuple) else [t]
        for p in parts:
            name = _dotted(p).split(".")[-1]
            if name.endswith(("Error", "Refusal", "Exception")):
                self.excepts.append((name, node.lineno))


def survey(code_dir: Path) -> dict:
    """Parse every .py under `code_dir` and derive the taxonomy.

    Attribution rule for a raise/except naming class X in module M: X defined in
    M wins; else X imported into M from a surveyed module wins; else, if exactly
    one surveyed module defines X, that one; else AMBIGUOUS and it is reported,
    never guessed. `WorkerError` is defined three times and `RailError` twice, so
    this is not hypothetical.
    """
    code_dir = Path(code_dir)
    scans: list[_ModuleScan] = []
    unparsed: list[dict] = []
    for p in sorted(code_dir.glob("*.py")):
        try:
            scans.append(_ModuleScan(p, ast.parse(p.read_text(encoding="utf-8"))))
        except (SyntaxError, UnicodeDecodeError, OSError) as e:
            unparsed.append({"file": p.name, "error": f"{type(e).__name__}: {e}"})

    # name -> [qualified ids]
    by_name: dict[str, list[str]] = {}
    classes: dict[str, dict] = {}
    for s in scans:
        for name, rec in s.classes.items():
            qid = f"{s.module}.{name}"
            classes[qid] = dict(rec, qid=qid, raises={}, dynamic=0, catches=0)
            by_name.setdefault(name, []).append(qid)

    def resolve(name: str, scan: _ModuleScan) -> str | None:
        local = f"{scan.module}.{name}"
        if local in classes:
            return local
        imp = scan.imports.get(name)
        if imp and f"{imp[0]}.{imp[1]}" in classes:
            return f"{imp[0]}.{imp[1]}"
        cands = by_name.get(name, [])
        return cands[0] if len(cands) == 1 else None

    ambiguous: list[dict] = []
    # Builtins raised directly. Not a resolution failure -- a REAL gap: a caller
    # cannot branch on `kind` for these, because they have none.
    builtin: list[dict] = []

    # Inherited shape + inherited doc_kinds, transitively within the survey set.
    def shape_of(qid: str, seen: frozenset = frozenset()) -> bool:
        rec = classes[qid]
        if rec["own_shape"] is not None:
            return rec["own_shape"]
        if qid in seen:
            return False
        scan = next(s for s in scans if s.module == rec["module"])
        for b in rec["bases"]:
            bq = resolve(b.split(".")[-1], scan)
            if bq and shape_of(bq, seen | {qid}):
                return True
        return False

    for qid in classes:
        classes[qid]["shape"] = shape_of(qid)
        classes[qid].pop("own_shape")

    for s in scans:
        for name, kind, line in s.raises:
            qid = resolve(name, s)
            if qid is None:
                where = {"module": s.module, "class": name, "line": line}
                (builtin if hasattr(builtins, name) else ambiguous).append(where)
                continue
            if kind == "<dynamic>":
                classes[qid]["dynamic"] += 1
            else:
                classes[qid]["raises"].setdefault(kind, []).append(
                    f"{s.module}:{line}")
        for name, line in s.excepts:
            qid = resolve(name, s)
            if qid is not None:
                classes[qid]["catches"] += 1

    typed = {q: r for q, r in classes.items() if r["shape"]}

    # Collisions: one kind, more than one typed class.
    kind_owners: dict[str, list[str]] = {}
    for qid, rec in typed.items():
        for kind in rec["raises"]:
            kind_owners.setdefault(kind, []).append(qid)
    collisions = {
        k: {"owners": sorted(v),
            "verdict": KNOWN_COLLISIONS.get(k, ("UNREVIEWED", ""))[0],
            "note": KNOWN_COLLISIONS.get(k, ("", ""))[1]}
        for k, v in sorted(kind_owners.items()) if len(v) > 1
    }

    # Gaps: docstring says a kind the code never raises, or the reverse.
    #
    # Compared across the HIERARCHY, not per class, or the answer is wrong in
    # both directions: a base that declares the seam vocabulary would look like
    # it documents five kinds it never raises (its subclasses raise them), and a
    # subclass inheriting that docstring would look like it raises kinds nobody
    # documented. cosmos_rail_base.RailError / CodexRailError are exactly that
    # pair, so this is not a hypothetical refinement.
    parents = {q: [b for b in (resolve(bn.split(".")[-1],
                                       next(s for s in scans
                                            if s.module == classes[q]["module"]))
                               for bn in classes[q]["bases"]) if b]
               for q in classes}

    def _closure(qid, edges, seen=None):
        seen = seen if seen is not None else set()
        for nxt in edges.get(qid, ()):
            if nxt not in seen:
                seen.add(nxt)
                _closure(nxt, edges, seen)
        return seen

    children: dict[str, list[str]] = {}
    for q, ps in parents.items():
        for p in ps:
            children.setdefault(p, []).append(q)

    gaps = []
    for qid, rec in sorted(typed.items()):
        doc = set(rec["doc_kinds"])
        # everything this class or anything below it actually raises
        raised = set(rec["raises"])
        for d in _closure(qid, children):
            raised |= set(classes[d]["raises"])
        # everything this class or anything above it declares
        declared = set(doc)
        for a in _closure(qid, parents):
            declared |= set(classes[a]["doc_kinds"])
        if not declared and not rec["raises"]:
            continue
        undocumented = sorted(set(rec["raises"]) - declared) if declared else []
        unraised = sorted(doc - raised)
        if undocumented or unraised:
            gaps.append({"class": qid, "documented_never_raised": unraised,
                         "raised_never_documented": undocumented,
                         "has_doc_declaration": bool(doc)})
    undeclared = sorted(q for q, r in typed.items() if not r["doc_kinds"])

    # Synonym clusters, reported only for the kinds actually present.
    live_kinds = set(kind_owners)
    synonyms = {
        name: dict(c, present=sorted(k for k in c["kinds"] if k in live_kinds))
        for name, c in SYNONYM_CLUSTERS.items()
        if len(live_kinds & set(c["kinds"])) > 1
    }

    return {
        "code_dir": str(code_dir),
        "modules_parsed": len(scans),
        "unparsed": unparsed,
        "error_classes": len(classes),
        "typed_refusal_classes": len(typed),
        "kinds": sorted(kind_owners),
        "classes": {q: classes[q] for q in sorted(classes)},
        "typed": sorted(typed),
        "collisions": collisions,
        "synonym_clusters": synonyms,
        "gaps": gaps,
        "undeclared_doc_kinds": undeclared,
        "untyped_builtin_raises": sorted(
            builtin, key=lambda b: (b["module"], b["line"])),
        "ambiguous_sites": ambiguous,
    }


def render_table(sv: dict) -> str:
    """Markdown projection of the survey. Regenerate; never hand-edit."""
    L = [
        "# REFUSAL TAXONOMY — every `*Error(kind, detail)` in `cosmos/`",
        "",
        "**GENERATED — do not hand-edit.** Source is the code; this file is a",
        "projection. Regenerate:",
        "",
        "```",
        "py -3.14 cosmos\\cosmos_refusals.py --render > docs\\REFUSAL_TAXONOMY.md",
        "```",
        "",
        f"Modules parsed: **{sv['modules_parsed']}** · error classes: "
        f"**{sv['error_classes']}** · carrying the `(kind, detail)` shape: "
        f"**{sv['typed_refusal_classes']}** · distinct kinds: "
        f"**{len(sv['kinds'])}**",
        "",
        "## Typed refusals — branch on `kind`",
        "",
        "| Class | Module | Kinds raised (sites) | Declared in docstring | `except` sites |",
        "|---|---|---|---|---|",
    ]
    for qid in sv["typed"]:
        r = sv["classes"][qid]
        raised = ", ".join(f"`{k}`×{len(v)}" for k, v in sorted(r["raises"].items()))
        dyn = f" +{r['dynamic']} dynamic" if r["dynamic"] else ""
        doc = ", ".join(f"`{k}`" for k in r["doc_kinds"]) or "—"
        L.append(f"| `{r['name']}` | `{r['module']}` | {raised or '—'}{dyn} | "
                 f"{doc} | {r['catches']} |")

    L += ["", "## Untyped error classes — a message, not a kind", "",
          "Listed so the boundary is explicit: a caller CANNOT branch on `kind` "
          "for these.", ""]
    untyped = [r for r in sv["classes"].values() if not r["shape"]]
    if untyped:
        L += ["| Class | Module | `except` sites |", "|---|---|---|"]
        L += [f"| `{r['name']}` | `{r['module']}` | {r['catches']} |"
              for r in untyped]
    else:
        L.append("**None.** Every error class in `cosmos/` already carries the "
                 "`(kind, detail)` shape — the taxonomy is uniform at the class "
                 "level, and what remains to unify is the VOCABULARY below.")

    L += ["", "## Collisions — one kind string, more than one class", ""]
    if sv["collisions"]:
        L += ["| Kind | Classes | Verdict | Note |", "|---|---|---|---|"]
        for k, c in sv["collisions"].items():
            owners = ", ".join(f"`{o}`" for o in c["owners"])
            L.append(f"| `{k}` | {owners} | **{c['verdict']}** | {c['note'] or '—'} |")
    else:
        L.append("None.")

    L += ["", "## Synonym clusters — one concept, several kind strings", "",
          "The inverse of a collision, and the harder defect: a caller asking "
          "one question must know every spelling of the answer.", ""]
    if sv["synonym_clusters"]:
        for name, c in sv["synonym_clusters"].items():
            L += [f"**`{name}`** — {', '.join('`%s`' % k for k in c['present'])}",
                  "", f"> {c['evidence']}", ""]
    else:
        L.append("None.")

    L += ["", "## Gaps — docstring vs raise sites", "",
          "The drift check. `documented_never_raised` is a kind a caller may "
          "branch on that can never arrive; `raised_never_documented` is a kind "
          "that arrives with nothing telling the caller it exists.", ""]
    if sv["gaps"]:
        L += ["| Class | Documented, never raised | Raised, never documented |",
              "|---|---|---|"]
        for g in sv["gaps"]:
            L.append(f"| `{g['class']}` | "
                     f"{', '.join('`%s`' % k for k in g['documented_never_raised']) or '—'} | "
                     f"{', '.join('`%s`' % k for k in g['raised_never_documented']) or '—'} |")
    else:
        L.append("None.")

    if sv["undeclared_doc_kinds"]:
        L += ["", "## Typed classes declaring no kinds at all", "",
              "These carry `(kind, detail)` but no `kind in {…}` docstring line, "
              "so the declared set is unknown to a reader and to this tool.", ""]
        L += [f"- `{q}`" for q in sv["undeclared_doc_kinds"]]

    if sv["untyped_builtin_raises"]:
        by_mod: dict[str, int] = {}
        for b in sv["untyped_builtin_raises"]:
            by_mod[b["module"]] = by_mod.get(b["module"], 0) + 1
        L += ["", "## Outside the taxonomy — bare builtin raises", "",
              "A caller cannot branch on `kind` here, because there is none. "
              "Listed by module so the seams that still refuse untyped are "
              "visible.", "", "| Module | Bare raises | Classes |",
              "|---|---|---|"]
        for mod, n in sorted(by_mod.items(), key=lambda kv: (-kv[1], kv[0])):
            cls = sorted({b["class"] for b in sv["untyped_builtin_raises"]
                          if b["module"] == mod})
            L.append(f"| `{mod}` | {n} | {', '.join('`%s`' % c for c in cls)} |")

    if sv["ambiguous_sites"]:
        L += ["", "## Unattributed sites", "",
              "A raise naming a class this tool could not attribute to one "
              "definition (a duplicated class name). Reported, never guessed.", ""]
        L += [f"- `{a['module']}:{a['line']}` → `{a['class']}`"
              for a in sv["ambiguous_sites"]]
    if sv["unparsed"]:
        L += ["", "## Unparsed", ""]
        L += [f"- `{u['file']}` — {u['error']}" for u in sv["unparsed"]]
    return "\n".join(L) + "\n"


def _code_dir() -> Path:
    return Path(__file__).resolve().parent


def selftest() -> int:
    """Bind the claim to an emitted value.

    Two things must be true, and they are different: the surveyor must be
    RIGHT about this tree (facts a hand-check confirms), and it must be able to
    DETECT drift rather than always passing -- proven against a synthetic module
    whose answer is known, the same shape as the Phase 1 contract gate.
    """
    import tempfile

    results = []

    def check(label, fn):
        try:
            results.append((label, bool(fn()), ""))
        except Exception as e:                                        # noqa: BLE001
            results.append((label, False, f"{type(e).__name__}: {e}"))

    sv = survey(_code_dir())

    check("the live cosmos/ tree parses with no syntax failures",
          lambda: not sv["unparsed"] and sv["modules_parsed"] > 50)
    check("it finds the two RailErrors as SEPARATE classes",
          lambda: "cosmos_rails.RailError" in sv["classes"]
          and "cosmos_rail_base.RailError" in sv["classes"])
    check("both RailErrors carry the (kind, detail) shape",
          lambda: sv["classes"]["cosmos_rails.RailError"]["shape"]
          and sv["classes"]["cosmos_rail_base.RailError"]["shape"])
    check("CodexRailError INHERITS the shape (it defines no __init__)",
          lambda: sv["classes"]["cosmos_codex_rail.CodexRailError"]["shape"])
    check("the Dispatcher's kinds are read from its raise sites",
          lambda: set(sv["classes"]["cosmos_rails.RailError"]["raises"])
          == {"NO_LIVE_LINK", "RAIL_FAILED", "NOT_PERMITTED",
              "UNPRICED_METERED", "UNGATED_METERED"})
    check("CosmosPathError's OTHER docstring convention is read too",
          lambda: "IDENTITY_MISMATCH"
          in sv["classes"]["cosmos_paths.CosmosPathError"]["doc_kinds"])
    check("every collision carries a reviewed verdict (a new one shows up)",
          lambda: sv["collisions"] and all(
              c["verdict"] != "UNREVIEWED" for c in sv["collisions"].values()))
    check("the policy_declined synonym cluster is present in this tree",
          lambda: sorted(sv["synonym_clusters"]["policy_declined"]["present"])
          == ["DENIED", "NOT_PERMITTED", "REFUSED"])
    check("bare builtin raises are separated from unresolved names",
          lambda: sv["untyped_builtin_raises"] and not sv["ambiguous_sites"])
    check("the renderer emits a table naming a real class",
          lambda: "REFUSAL TAXONOMY" in render_table(sv)
          and "CodexRailError" in render_table(sv))

    # THE PHASE 5 MERGE QUESTION, as a measured fact rather than an opinion.
    # The two RailErrors were left separate (see the verdict in
    # tests/test_rail_base.py). The reason is this: their kind sets are
    # DISJOINT, so a caller can already branch on `kind` across both without
    # knowing which module raised -- which is the whole of what Phase 5 asked
    # for. Merging the classes would buy nothing and would change what
    # `except RailError` catches at cosmos_codex_rail.py:1063. If a future
    # edit makes the sets overlap, that argument dies and this goes red.
    disp = set(sv["classes"]["cosmos_rails.RailError"]["raises"])
    seam = set(sv["classes"]["cosmos_rail_base.RailError"]["doc_kinds"])
    check("the two RailError kind sets are DISJOINT (the no-merge argument)",
          lambda: bool(disp) and bool(seam) and not (disp & seam))

    # Drift detection, against a module whose answer is known by construction.
    td = Path(tempfile.mkdtemp(prefix="refusals_"))
    (td / "fixture_mod.py").write_text(
        'class FixError(RuntimeError):\n'
        '    """kind in {ALPHA, GHOST}."""\n'
        '    def __init__(self, kind, detail):\n'
        '        self.kind = kind\n'
        '        self.detail = detail\n'
        '        super().__init__(f"[{kind}] {detail}")\n'
        '\n\n'
        'def go(n):\n'
        '    if n:\n'
        '        raise FixError("ALPHA", "declared and raised")\n'
        '    raise FixError("UNDECLARED", "raised, never documented")\n',
        encoding="utf-8")
    fx = survey(td)
    fg = next((g for g in fx["gaps"]
               if g["class"] == "fixture_mod.FixError"), None)
    check("a synthetic documented-but-never-raised kind is DETECTED",
          lambda: fg is not None and fg["documented_never_raised"] == ["GHOST"])
    check("a synthetic raised-but-never-documented kind is DETECTED",
          lambda: fg is not None and fg["raised_never_documented"] == ["UNDECLARED"])
    check("a clean fixture produces NO gap (it does not always fail)",
          lambda: _clean_has_no_gap(td))

    for label, ok, err in results:
        print(f"  {'OK  ' if ok else 'FAIL'}  {label}{('  ' + err) if err else ''}")
    bad = [r for r in results if not r[1]]
    print("live_value: " + json.dumps(
        {"modules_parsed": sv["modules_parsed"],
         "error_classes": sv["error_classes"],
         "typed_refusal_classes": sv["typed_refusal_classes"],
         "kinds": len(sv["kinds"]),
         "collisions": sorted(sv["collisions"]),
         "gap_classes": [g["class"] for g in sv["gaps"]],
         "fixture_gap": fg},
        sort_keys=True))
    print(f"result: {'ok' if not bad else 'FAIL'}  "
          f"{len(results) - len(bad)}/{len(results)} on the refusal taxonomy")
    return 1 if bad else 0


def _clean_has_no_gap(td: Path) -> bool:
    """A fixture whose docstring and raise sites agree must produce no gap."""
    d = td / "clean"
    d.mkdir(exist_ok=True)
    (d / "clean_mod.py").write_text(
        'class CleanError(RuntimeError):\n'
        '    """kind in {ONLY}."""\n'
        '    def __init__(self, kind, detail):\n'
        '        self.kind = kind\n'
        '        self.detail = detail\n'
        '\n\n'
        'def go():\n'
        '    raise CleanError("ONLY", "agrees")\n',
        encoding="utf-8")
    return not survey(d)["gaps"]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="COSMOS refusal taxonomy (read-only)")
    ap.add_argument("--dir", default=None,
                    help="code directory to survey (default: this module's own)")
    ap.add_argument("--render", action="store_true",
                    help="emit the markdown table (default)")
    ap.add_argument("--json", action="store_true", help="emit the raw survey")
    ap.add_argument("--out", default=None,
                    help="write to PATH in UTF-8 instead of stdout")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    sv = survey(Path(a.dir) if a.dir else _code_dir())
    text = (json.dumps(sv, indent=2, sort_keys=True) + "\n") if a.json \
        else render_table(sv)
    if a.out:
        # `> file` on Windows encodes stdout with the console codepage, which
        # turns every em-dash in the table into a replacement char. Writing the
        # file here, explicitly UTF-8, is the difference between a projection
        # and a mangled one.
        Path(a.out).write_text(text, encoding="utf-8")
        print(f"wrote {a.out} ({len(text)} chars, utf-8)")
    else:
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):                          # noqa: BLE001
            pass
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
