# Remediation report — supplements R&D blog editor PR #245

**Date:** 2026-09-14  
**Agent:** Cloud remediation pass (quality over speed)  
**Recommendation:** **Close PR #245 without merge.**

## Summary

PR **#245** (`cursor/supplements-rd-blog-editor-b6b8` → `cursor/supplements-rd-blog-ee57`) is a duplicate, figure-stripping editor pass. Clean replacement work lives on:

| Branch | Purpose | Next action |
| --- | --- | --- |
| `cursor/supplements-rd-integration-85a9` | Writer **#230** + figure embeds (**#240** asset lineage) | Retarget or supersede open writer PR; merge to `main` when ready |
| `cursor/supplements-rd-editor-clean-85a9` | **Clean editor** (voice, grammar, PMID fixes, deduped figures) | Open draft PR → integration branch |

## Evidence against merging #245

| Check | #245 (`9c98817`) | Clean editor branch |
| --- | --- | --- |
| Markdown `![` embeds in `articles/` | **0** on piece 01; figures stripped pack-wide | **53** embeds across 40 files; all slugs retain planned figures |
| `EDITOR_REPORT` figure claim | “unchanged (no `![` blocks)” | Dedupe on 03/07/13; embed QA table |
| VITAL D PMID in article 04 + biblio | Inconsistent (biblio reverts to wrong IDs) | **31173679 / 30415628 / 30415637** aligned in YAML, body, `BIBLIOGRAPHY.md` |
| Duplicate editor on ee57 | Yes — stacks on branch that already had `662bbc5`–`76c76ff` | Single editor commit series on integration base only |

Useful **prose** edits from #245 (e.g. COVID A to Z open-label wording in piece 03) were **cherry-picked** into the clean branch. No other #245 hunks were taken that remove figures or bibliography rows.

## QA reproduced on clean editor branch

```bash
cd content/supplements-rd-blog/articles
wc -w *.md | sort -n | head    # min 1001 words (piece 31)
grep -r 'voice_check: edited' . | wc -l   # 40
rg -c '!\[' *.md | awk -F: '{s+=$2} END{print s}'   # 53 embeds
python3 ../scripts/embed_graphics.py   # idempotent; 40 articles in plan
```

Style-guide hard bans: **0** hits in article bodies (ISAPP “utilize” paraphrased in piece 29).

## PR actions (human / Gitur)

1. **Close #245** — superseded by clean editor PR; cite this report.
2. **#230** — narrow scope to writer + integration branch (remove editor commits from `cursor/supplements-rd-blog-ee57` or point review at `cursor/supplements-rd-integration-85a9`).
3. **#240** — may close as merged-via-integration if assets + embeds already on integration branch; else merge graphics branch into integration before editor PR.
4. **Open clean editor PR** — head `cursor/supplements-rd-editor-clean-85a9`, base `cursor/supplements-rd-integration-85a9`, draft until writer + graphics land.

## Sign-off

Remediation **complete** in repo: ops notes (`DIRTY_PR_NOTES.md`), integration branch, clean editor branch, and this report. **Do not merge #245.**
