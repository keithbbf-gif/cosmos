# Dirty PR notes — content pipeline

Quality-over-speed rule: **writer → graphics → editor** on separate branches. A dirty editor PR stacks on the wrong base, drops figure embeds, or re-lands work already merged elsewhere.

## Supplements R&D blog (2026-09-14)

| PR | Branch | Role | Status |
| --- | --- | --- | --- |
| **#230** | `cursor/supplements-rd-blog-ee57` | Writer pack (≥1k words, `voice_check: human`) — **do not stack editor here after remediation** | Open → retarget to `cursor/supplements-rd-integration-85a9` |
| **#240** | `cursor/supplements-rd-blog-graphics-af19` | Editorial SVG assets + embed scripts | Open → superseded by writer deepen `015e149` + integration embed commit |
| **#245** | `cursor/supplements-rd-blog-editor-b6b8` | **Dirty editor** (based on pre-graphics-merge ee57 snapshot) | **Close** — see `REMEDIATION_REPORT.md` |

### Why #245 is dirty

1. **Base skew:** Opened against `cursor/supplements-rd-blog-ee57` while that branch already carried a full editor pass (`662bbc5`–`76c76ff`). #245 re-ran editor on stale prose without the graphics-pack embed state the writer branch had landed.
2. **Figure regression:** Commit `9c98817` sets `voice_check: edited` but **removes all `![` SVG embed blocks** from articles (e.g. piece 01 loses both timeline and ingredient-thread figures). `EDITOR_REPORT.md` on #245 falsely claims “Graphic embeds unchanged.”
3. **Bibliography damage:** Drops verified COSMOS-Web / COSMOS-Clinic rows and other wave-2 citations while article bodies still reference them.
4. **PMID churn:** “Fixes” in #245 reintroduce swapped VITAL / REDUCE-IT PMIDs in `BIBLIOGRAPHY.md` even where article YAML was corrected — inconsistent with PubMed ground truth (VITAL D **31173679**, VITAL omega-3 **30415628**, REDUCE-IT **30415637**).

### Remediation pattern (this pack)

1. **`cursor/supplements-rd-integration-85a9`** — `main` + writer commits (`367617d`…`35b8b1b`) + `embed_graphics.py` run (assets from writer deepen + PR #240 lineage).
2. **`cursor/supplements-rd-editor-clean-85a9`** — integration + clean editor pass (figures preserved, dedupe on 03/07/13, PMID fixes, `EDITOR_REPORT.md`).
3. Close **#245** without merge. Open **clean editor PR** from step 2 → step 1.

## Reuse checklist (other content packs)

Before opening an editor PR:

- [ ] Base branch includes **graphics embeds** (`<!-- graphics-pack:v1 -->` + `../assets/...`).
- [ ] `rg '!\[' content/<pack>/articles` count matches `GRAPHICS_INDEX.md` / embed plan.
- [ ] No duplicate editor pass on a branch that already has `voice_check: edited`.
- [ ] `EDITOR_REPORT.md` “Graphic embeds” row verified by command, not assertion.
