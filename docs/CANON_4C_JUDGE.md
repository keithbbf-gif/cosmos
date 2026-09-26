# CANON: 4Cs + Judge formatting (all seats read this)

**Authority:** `cosmos/cosmos_crew_pipe.py` (`local_code_checks`), `cosmos/cosmos_code_checks.py`
(`cosmos-code-checks/1`), `cosmos/cosmos_route_variant.py` (`cosmos-or-routing/1`),
`work_orders/ccr/hero_luna/skills/judge-keep-drop/SKILL.md`.
**Purpose:** one formatting contract so WOMBAT-authored prompts, CCrew replies, Judge
verdicts, Final Auditor packs, and Scribe commits all parse first time.

---

## 1. Coder reply first line (machine-read)

`local_code_checks` classifies by first non-blank bytes. Emit exactly one form:

| First line | Meaning | Example |
|---|---|---|
| `NONE` | propose nothing; already on main | `NONE` |
| `diff --git` | unified diff proposal | `diff --git a/cosmos/cosmos_x.py b/cosmos/cosmos_x.py` |
| `{` | strict JSON (must parse) | `{"ok": true, "rail": "vertex"}` |
| `def `/`class `/`import `/`from ` (+ `.py` filename) | python file body | `def paint():` |

Anything else = `form: PASS (prose)` — ungradeable by 4Cs. Prose never reaches Judge.

## 2. The 4Cs (py_compile, ruff, mypy, pytest)

Runner: `run_code_checks(paths, rec, text)` where
`rec = {"order_id": "<oid>", "_output_path": "<name>.py"}`.
One DB row per tool into `state/code_checks.db`, table `code_checks`:

```json
{"schema": "cosmos-code-checks/1", "at": "2026-09-23T06:40:00-05:00",
 "order_id": "wo-20260902T114500", "tool": "py_compile", "status": "PASS",
 "returncode": 0, "target": "reply.py",
 "source_sha": "sha256-of-exact-checked-text",
 "stdout": "", "stderr": ""}
```

Status values: `PASS` (rc 0) · `FAIL` · `MISSING` (tool absent — never a silent
skip) · `NO_CODE` (reply was NONE) · `NO_TESTS` (pytest rc 5 only).
`fails_of(rows)` blocks Judge on `FAIL`/`MISSING` only.
Read-back: `rows_for(paths, order_id)` — tool, status, returncode, stdout, stderr.

## 3. Diffs must be split into FILE blocks first (no exceptions)

`run_code_checks` materializes reply text as ONE file. A whole unified diff
checked as `reply.py` fails `py_compile` spuriously. Contract for the extractor:

- Input: reply starting `diff --git a/<p> b/<p>`.
- Split on `^diff --git ` headers; per file take `+++ b/<path>` as name and
  `+`-lines (minus the `+`) as body; skip `/dev/null` deletions.
- Check EACH file body separately with its real filename (so ruff/mypy resolve).
- Receipt `source_sha` = sha256 of the exact checked body; `target` = real name.

Example:

```
in:  diff --git a/cosmos/cosmos_health.py b/cosmos/cosmos_health.py
     new file mode 100644
     +++ b/cosmos/cosmos_health.py
     +"""Health board snapshot."""
     +def snapshot(): ...
out: [{target: "cosmos_health.py", sha: "<sha256-of-body>",
       rows: [py_compile PASS, ruff …, mypy …, pytest …]}, …]
```

Whole-diff-as-one-file receipts are INVALID and must be re-run. Same rule for
Judge input: Judge reads extracted FILE blocks, never wrapper first-lines
(blind-leak guard — wrapper fingerprints unblind same-model A/B).

## 4. Judge call + verdict

Model string via `request_model(model, paths=…)`; saved priority wins, default
is `:floor` (flex endpoints). Example: base `openai/gpt-5.6-luna` → request sends
`openai/gpt-5.6-luna:floor`. Catalog ids stay bare (`catalog_id` drops routing
suffixes). Verify the id exists in `live/state/model_rater/catalog.json` before
paid calls — never invent ids. Key: `live/config/openrouter_api_key.txt`
(also `OPENROUTER_API_KEY` env). NEVER print, echo, or paste the key.

Verdict first line is exactly one of (per `judge-keep-drop` SKILL):

```
KEEP | DROP | NONE | HOLD | UNMEASURED
```

Then findings-first lines `severity file:line message`, then one sentence.
Example:

```
KEEP
minor cosmos/cosmos_health.py:12 docstring line too long
G46 health-board snapshot is style-clean and read-only as specified.
```

Rules: read Mission files only; no merge/push/apply_patch; no `CCR.lease`;
PREFIX carries no dates/PR ids/hashes; report Flex-vs-base honestly.

## 5. Score tracking keys (every judged row)

```json
{"ab_pair_id": "ab-<baseline-oid>", "arm": "hero|base",
 "baseline_oid": "<oid>", "baseline_write_path": "<abs path>",
 "judge_score_hero": null, "judge_score_base": null, "judge_winner": "PENDING"}
```

`judge_winner` flips to `hero|base|tie` only on a recorded verdict. PENDING
everywhere else. Final Auditor bin trips at 30 keeps (`FINAL_FLOOR` parity
with `JUDGE_FLOOR = 30`).
