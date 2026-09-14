---
pack: slpwow-free-resources-curriculum
doc: EDITOR_REPORT
status: curriculum-briefs-wave-1
voice: human
voice_check: edited
lint: check-curriculum
---

# Editor report — `slpwow-free-resources-curriculum`

**Pull request:** [#418](https://github.com/keithbbf-gif/cosmos/pull/418)  
**Editor pass:** 2026-09-14 (UTC)  
**Scope:** Fourteen curriculum markdown files, `check_curriculum.py`, `manifest.toml`, pack README  
**Outcome:** `voice_check: edited` on every markdown file; one brief wording fix; structural checker extended. **Draft PR only — not merged.**

## Mandate

Quality over speed. Claims law in `CLAIMS_GUARDRAILS.md` is stricter than polite marketplace copy: no diagnosis, no screen, no outcome guarantee, original compilation only.

## Method

1. Read `CLAIMS_GUARDRAILS.md`, `INDEX.md`, and all format/domain briefs.
2. Grep sweeps for brochure voice and diagnosis/screener product headings.
3. Add YAML frontmatter with `voice_check: edited` on every pack markdown file.
4. Extend `check_curriculum.py` to require frontmatter and refuse brochure terms in bodies.
5. `python3 content/slpwow-free-resources-curriculum/check_curriculum.py`
6. `python3 -m pytest tests/test_slpwow_free_resources_curriculum.py -q`

## Narrative edits

| File | Change | Rationale |
| --- | --- | --- |
| `briefs/printouts.md` | “If you added a 20-box grid…” → “If a brief adds a 20-box grid…” | Keeps writer-facing brief from sounding like a clinician instruction on the same page as caregiver copy rules. |

No SKU, footer, or refuse-list changes. Social scenario seeds (`You need a pencil…`) stay as **student-facing examples**, not clinician verdicts.

## Furniture / tooling

- **`voice_check: edited`** on all fourteen `.md` files (canon, index, briefs, domains).
- **`README.md`** — documents frontmatter and check commands.
- **`CLAIMS_GUARDRAILS.md`** — states the `voice_check` contract.
- **`check_curriculum.py`** — parses frontmatter; checks `voice_check`; scans bodies for brochure terms.
- **`manifest.toml`** — lists `README.md` and `EDITOR_REPORT.md` as required files.

## Verification

```
PASS  slpwow-free-resources-curriculum  files=…  skus=24
pytest: passed
```

## Sign-off

| Field | Value |
| --- | --- |
| `voice_check` | `edited` (all pack markdown) |
| `check_curriculum` | pass |
| `pytest` | pass |
| Merge | **no** — draft PR #418 only |
