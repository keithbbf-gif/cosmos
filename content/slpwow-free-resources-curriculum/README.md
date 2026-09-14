---
pack: slpwow-free-resources-curriculum
doc: README
status: curriculum-briefs-wave-1
voice: human
voice_check: edited
lint: check-curriculum
---

# SLPWOW free-resources curriculum

Wave-1 **briefs** for clinician-facing free PDFs. Not designed pages. Not Core.

Read `CLAIMS_GUARDRAILS.md` before editing a sentence. Read `PREPUBLISH.md` before imagining a ship date.

## Frontmatter (every `.md` file)

| key | required value / shape |
| --- | --- |
| `pack` | `slpwow-free-resources-curriculum` |
| `doc` | stable slug for this file |
| `status` | `curriculum-briefs-wave-1` |
| `voice` | `human` |
| `voice_check` | `edited` after editor pass; `pending` before |
| `lint` | `check-curriculum` |

## Check

```bash
python3 content/slpwow-free-resources-curriculum/check_curriculum.py
python3 -m pytest tests/test_slpwow_free_resources_curriculum.py -q
```
