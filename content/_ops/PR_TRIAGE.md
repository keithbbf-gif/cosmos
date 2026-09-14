# PR triage — Website Builder content & staging packs

**Inventory as of:** 2026-09-14 (UTC), via `gh` against `keithbbf-gif/cosmos` and `keithbbf-gif/cdm`.

**Scope:** Open **draft** pull requests for `content/*` editorial packs (writer → graphics → editor craft lanes) and `sites/*` staging / marketing packages. Related **non-draft** open PRs that sit in the same merge chains are listed in a separate table (still not merged by this doc).

**Policy:** Triage only — **do not auto-merge** anything from this inventory.

---

## Method

```bash
export GH_TOKEN=…   # token with repo read (Cloud Agent git remote token works when `gh` GraphQL fails)
gh pr list --repo keithbbf-gif/cosmos --state open --draft --limit 200 \
  --json number,title,headRefName,isDraft,mergeStateStatus,url,baseRefName
gh pr view <N> --repo keithbbf-gif/cosmos --json baseRefName,mergeStateStatus,files
```

`gh` logged in as the inactive `cursor` host sometimes returns *Could not resolve repository*; setting `GH_TOKEN` from the clone remote was used for this run.

### `keithbbf-gif/cdm`

| Check | Result |
|--------|--------|
| `gh pr list --repo keithbbf-gif/cdm` | **Repository not found** (404) |
| `gh api repos/keithbbf-gif/cdm` | **404 Not Found** |
| `gh search repos cdm user:keithbbf-gif` | **0 results** |

No open draft PRs could be listed for **cdm** with the credentials available in this environment. If Website Builder packs live in a private `cdm` repo or under `web/staging/`, re-run the same `gh` commands with a token that has that repo scope and append a **cdm** section here (preferred path on cdm: `web/staging/PR_TRIAGE.md`).

---

## Craft lanes (dependency)

| Lane | Typical PR signals | Must land before |
|------|-------------------|------------------|
| **Writer** | “blog pack”, “staged drafts”, `content/<pack>/drafts/` | Graphics & editor for same pack |
| **Graphics** | “graphics pipeline”, SVG embeds, `figures/` | Editor pass (unless editor is docs-only hold) |
| **Editor** | “editor pass”, voice/stub de-clone, `EDITOR_REPORT.md` | Publish / WP deploy (out of scope here) |
| **Site pack** | `sites/<name>/`, Eleventy / static / WP staging bundles | Independent per site tree (watch cross-site copy only) |

**Stacked PRs** (base branch ≠ `main`) must merge **in stack order** (bottom → top), then the stack tip to `main`.

---

## Content packs — open drafts (`keithbbf-gif/cosmos`)

Merge state from GitHub: `CLEAN` | `UNSTABLE` (behind/out of date with base) | `DIRTY` (conflicts).

### `content/ai-industry-blog`

| PR | Title | Branch | Status | Lane | Base | Merge state |
|----|-------|--------|--------|------|------|-------------|
| [#234](https://github.com/keithbbf-gif/cosmos/pull/234) | feat(content): AI industry blog graphics library (timelines, architecture, eval, regulation) | `cursor/ai-industry-blog-graphics-e22a` | Draft, OPEN | graphics | `main` | UNSTABLE |
| [#244](https://github.com/keithbbf-gif/cosmos/pull/244) | feat(content): AI industry blog graphics wave 2 + draft embeds | `cursor/ai-industry-blog-graphics-wave2-1f4e` | Draft, OPEN | graphics | `cursor/ai-industry-blog-graphics-e22a` | CLEAN |
| [#259](https://github.com/keithbbf-gif/cosmos/pull/259) | docs(ai-industry-blog): editor pass on pack 42 (stacked) | `cursor/ai-industry-blog-editor-f4fe` | Draft, OPEN | editor | `cursor/ai-industry-blog-pack-019f` | UNSTABLE |

**Related non-draft:** [#227](https://github.com/keithbbf-gif/cosmos/pull/227) — writer, 42 drafts (`cursor/ai-industry-blog-pack-019f`), UNSTABLE. **#259 stacks on #227’s branch**, not on #244.

**Suggested merge order:** `#227` → `#234` → `#244` → `#259` (or squash stack into one merge after review).

**Conflict risk:** High — four PRs, two graphics layers + editor on writer branch; all touch `content/ai-industry-blog/`. Parallel edits to `INDEX.md` / `MANIFEST.md` likely.

---

### `content/supplements-rd-blog`

| PR | Title | Branch | Status | Lane | Base | Merge state |
|----|-------|--------|--------|------|------|-------------|
| [#240](https://github.com/keithbbf-gif/cosmos/pull/240) | feat(content): supplements R&D blog editorial SVG graphics pack | `cursor/supplements-rd-blog-graphics-af19` | Draft, OPEN | graphics | `main` | UNSTABLE |
| [#245](https://github.com/keithbbf-gif/cosmos/pull/245) | Editor pass: supplements R&D blog (40 drafts) | `cursor/supplements-rd-blog-editor-b6b8` | Draft, OPEN | editor | `cursor/supplements-rd-blog-ee57` | **DIRTY** |

**Related non-draft:** [#230](https://github.com/keithbbf-gif/cosmos/pull/230) — writer (`cursor/supplements-rd-blog-ee57`), UNSTABLE.

**Suggested merge order:** `#230` → `#240` → `#245` (resolve **DIRTY** on #245 before editor merge).

**Conflict risk:** High — editor PR already conflicts with base; graphics + writer both target same pack tree.

---

### `content/furniture-craft-blog`

| PR | Title | Branch | Status | Lane | Base | Merge state |
|----|-------|--------|--------|------|------|-------------|
| [#251](https://github.com/keithbbf-gif/cosmos/pull/251) | Furniture craft magazine blog pack (44 staged drafts) | `cursor/furniture-craft-blog-623a` | Draft, OPEN | writer | `main` | UNSTABLE |
| [#235](https://github.com/keithbbf-gif/cosmos/pull/235) | GRAPHICS: furniture-craft-blog SVG diagrams (45 drafts) | `cursor/furniture-craft-graphics-99ed` | Draft, OPEN | graphics | `main` | UNSTABLE |
| [#241](https://github.com/keithbbf-gif/cosmos/pull/241) | Editor pass: furniture-craft-blog voice and stub de-clone (45 drafts) | `cursor/furniture-craft-editor-6155` | Draft, OPEN | editor | `cursor/furniture-craft-graphics-99ed` | UNSTABLE |

**Suggested merge order:** `#251` → `#235` → `#241`.

**Conflict risk:** High — parallel **writer** (#251) and **graphics** (#235) both on `main`; editor stacked on graphics only.

---

### `content/furniture-fashion-fads-blog` (FFFB)

| PR | Title | Branch | Status | Lane | Base | Merge state |
|----|-------|--------|--------|------|------|-------------|
| [#252](https://github.com/keithbbf-gif/cosmos/pull/252) | Draft: furniture fashion & fads magazine blog pack (42 essays) | `cursor/furniture-fashion-fads-blog-a5c3` | Draft, OPEN | writer | `main` | UNSTABLE |
| [#238](https://github.com/keithbbf-gif/cosmos/pull/238) | feat(content): furniture-fashion-fads editorial graphics pack | `cursor/furniture-fashion-fads-graphics-46bc` | Draft, OPEN | graphics | `main` | UNSTABLE |
| [#246](https://github.com/keithbbf-gif/cosmos/pull/246) | docs(content): FFFB editor hold — stub inventory (await WRITER prose) | `cursor/fffb-editor-report-4278` | Draft, OPEN | editor (HOLD) | `cursor/furniture-fashion-fads-graphics-46bc` | UNSTABLE |

**Suggested merge order:** `#252` (prose) before treating graphics as final; today graphics (#238) can merge ahead only if stubs are intentional → `#238` → `#246` documents **HOLD** until writer fills articles.

**Conflict risk:** **Parallel craft lanes** — writer #252 vs graphics #238 on same pack; editor explicitly blocked on stub-only articles.

---

### `content/furniture-history-ancient-blog`

| PR | Title | Branch | Status | Lane | Base | Merge state |
|----|-------|--------|--------|------|------|-------------|
| [#253](https://github.com/keithbbf-gif/cosmos/pull/253) | Draft: History of Furniture magazine series (43 essays) | `cursor/furniture-history-ancient-blog-bbf1` | Draft, OPEN | writer | `main` | UNSTABLE |
| [#248](https://github.com/keithbbf-gif/cosmos/pull/248) | Citation pass: deepen evidence for seven ancient furniture essays | `cursor/citation-deepen-ancient-furniture-8a9f` | Draft, OPEN | editor | `cursor/furniture-ancient-graphics-2a96` | UNSTABLE |

**Related non-draft:** [#236](https://github.com/keithbbf-gif/cosmos/pull/236) — graphics (44 essays, 176 SVGs), UNSTABLE.

**Suggested merge order:** `#253` → `#236` → `#248`.

**Conflict risk:** Medium–high — citation/editor branch tracks **graphics** branch, not writer; merge writer before rebasing graphics stack.

---

### `content/furniture-woods-500y-blog` (woods series)

| PR | Title | Branch | Status | Lane | Base | Merge state |
|----|-------|--------|--------|------|------|-------------|
| [#260](https://github.com/keithbbf-gif/cosmos/pull/260) | Draft: furniture woods, 1500–present (45 articles) | `cursor/furniture-woods-500y-blog-23c0` | Draft, OPEN | writer | `main` | UNSTABLE |

**Related non-draft:** [#249](https://github.com/keithbbf-gif/cosmos/pull/249) — partial graphics (5 SVG + embeds), UNSTABLE.

**Suggested merge order:** `#260` → `#249` (expand graphics PR or follow-up wave).

**Conflict risk:** Low across packs; **name collision** with other furniture content lanes (human review for slug/topic overlap only).

---

### `content/figroots-blog`

| PR | Title | Branch | Status | Lane | Base | Merge state |
|----|-------|--------|--------|------|------|-------------|
| [#224](https://github.com/keithbbf-gif/cosmos/pull/224) | FigRoots evergreen blog drafts (grower voice) | `cursor/figroots-blog-5eba` | Draft, OPEN | writer | `main` | CLEAN |
| [#237](https://github.com/keithbbf-gif/cosmos/pull/237) | feat(figroots): blog graphics pipeline and SVG embeds (12 drafts) | `cursor/figroots-graphics-7107` | Draft, OPEN | graphics | `main` | UNSTABLE |
| [#258](https://github.com/keithbbf-gif/cosmos/pull/258) | figroots-blog: second-pass graphics quality (SVG upgrades + 3 earned figures) | `cursor/figroots-graphics-pass2-0843` | Draft, OPEN | graphics (pass 2) | `cursor/figroots-graphics-7107` | UNSTABLE |

**Suggested merge order:** `#224` → `#237` → `#258`.

**Conflict risk:** Medium — two graphics PRs; pass-2 stacked on pass-1. Writer still CLEAN vs UNSTABLE graphics.

---

### `content/herbal-medicine-history-blog`

| PR | Title | Branch | Status | Lane | Base | Merge state |
|----|-------|--------|--------|------|------|-------------|
| [#255](https://github.com/keithbbf-gif/cosmos/pull/255) | Herbal medicine history magazine blog pack (45 drafts) | `cursor/herbal-medicine-history-blog-231e` | Draft, OPEN | writer | `main` | UNSTABLE |
| [#242](https://github.com/keithbbf-gif/cosmos/pull/242) | feat: herbal medicine history blog — graphics pipeline and 80 SVG embeds | `cursor/herbal-medicine-history-graphics-594f` | Draft, OPEN | graphics | `main` | UNSTABLE |

**Suggested merge order:** `#255` → `#242` (no editor draft yet).

**Conflict risk:** Parallel writer/graphics on `main` — same pattern as furniture-craft.

---

### `content/slpwow-speech-pathology-history`

| PR | Title | Branch | Status | Lane | Base | Merge state |
|----|-------|--------|--------|------|------|-------------|
| [#254](https://github.com/keithbbf-gif/cosmos/pull/254) | Staged SLPWOW speech-pathology history series (40 articles) | `cursor/slpwow-speech-pathology-history-b9a7` | Draft, OPEN | writer | `main` | UNSTABLE |
| [#243](https://github.com/keithbbf-gif/cosmos/pull/243) | Staged SLPWOW history series: graphics pipeline + 40 articles | `cursor/slpwow-graphics-pipeline-b8b9` | Draft, OPEN | graphics | `main` | UNSTABLE |

**Suggested merge order:** `#254` → `#243` (confirm whether #243 duplicates writer work or only embeds).

**Conflict risk:** Medium — both mention “40 articles”; possible **duplicate writer/graphics** overlap in `content/slpwow-speech-pathology-history/`.

---

### `content/ai-history-retrospective`

| PR | Title | Branch | Status | Lane | Base | Merge state |
|----|-------|--------|--------|------|------|-------------|
| [#256](https://github.com/keithbbf-gif/cosmos/pull/256) | Draft: History of AI — Retrospective series (essays, figures, portraits) | `cursor/ai-history-retrospective-7b08` | Draft, OPEN | writer (+ figures in tree) | `main` | UNSTABLE |
| [#247](https://github.com/keithbbf-gif/cosmos/pull/247) | feat(content): AI history retrospective graphics pipeline (staged) | `cursor/ai-history-graphics-aae1` | Draft, OPEN | graphics | `main` | CLEAN |

**Suggested merge order:** `#256` → `#247` (writer includes figure/portrait work — avoid double SVG churn).

**Conflict risk:** Medium — writer PR description includes figures; graphics PR may overlap same paths.

---

### Other content-related open draft

| PR | Title | Branch | Status | Lane | Base | Merge state |
|----|-------|--------|--------|------|------|-------------|
| [#257](https://github.com/keithbbf-gif/cosmos/pull/257) | feat(content): Wow Therapies therapy-history staged SVG graphics | `cursor/wowtherapies-therapy-history-graphics-9a7f` | **Open, not draft** | graphics | `main` | CLEAN |

Listed because it pairs with WOW Therapies **site** packs below (`sites/wowtherapies`, `sites/staging-wp`).

**Related non-draft:** [#250](https://github.com/keithbbf-gif/cosmos/pull/250) — `fig-history` graphics pack (separate pack name; do not confuse with `figroots-blog`).

---

## Site & staging packs — open drafts (`sites/*`)

Independent trees; merge order mostly **per site**, except WOW / SLP WOW cross-links.

| PR | Pack / dependency | Title | Branch | Merge state |
|----|-------------------|-------|--------|-------------|
| [#211](https://github.com/keithbbf-gif/cosmos/pull/211) | `sites/slpwow` (Eleventy community site) | feat(sites): SLP WOW community site package (slpwow.com) | `cursor/slpwow-site-e459` | CLEAN |
| [#215](https://github.com/keithbbf-gif/cosmos/pull/215) | `sites/staging-wp` (WP + GP: WOW Therapies + SLP WOW) | feat(sites): staging WordPress + GeneratePress packages | `cursor/staging-wp-sites-e817` | CLEAN |
| [#218](https://github.com/keithbbf-gif/cosmos/pull/218) | `sites/wowtherapies` (marketing) | feat: WOW Therapies marketing site | `cursor/wowtherapies-site-244f` | CLEAN |
| [#219](https://github.com/keithbbf-gif/cosmos/pull/219) | `sites/dailyscar`, `sites/lmnator` | feat(sites): DailyScar and LMNator premium static marketing packages | `cursor/static-sites-dailyscar-lmnator-8dee` | CLEAN |
| [#212](https://github.com/keithbbf-gif/cosmos/pull/212) | `sites/ai-cluster-hub` | feat(sites): private AI Cluster staging hub | `cursor/ai-cluster-hub-643a` | CLEAN |
| [#214](https://github.com/keithbbf-gif/cosmos/pull/214) | `sites/modelraters` | feat(sites): ModelRater marketing shell | `cursor/modelraters-site-2393` | CLEAN |
| [#216](https://github.com/keithbbf-gif/cosmos/pull/216) | `sites/mdrater` (alias) | feat(sites): mdrater.com alias shell for ModelRater | `cursor/mdrater-site-5a5c` | CLEAN |
| [#213](https://github.com/keithbbf-gif/cosmos/pull/213) | `sites/brokentokn` | feat(sites): BrokenTokn marketing shell | `cursor/brokentokn-site-0db5` | CLEAN |

**Suggested merge order (sites):**

1. **ModelRater cluster:** `#214` → `#216` (alias depends on canonical shell).
2. **Parallel (no shared paths):** `#212`, `#213`, `#219`.
3. **WOW / SLP cluster (coordinate):** `#218` and/or `#215` before treating WP staging as canonical; `#211` (SLP WOW Eleventy) overlaps **SLP WOW** positioning with `#215` — pick product intent before merging both.
4. **Content graphics:** [#257](https://github.com/keithbbf-gif/cosmos/pull/257) after WOW site copy paths are stable.

**Conflict risk:** **Thematic overlap**, not necessarily git conflicts — `#215` vs `#218` (WOW Therapies), `#211` vs `#215` (SLP WOW). `sites/shared` in #219 may affect verify scripts used elsewhere.

---

## Out of scope (open drafts on same repo)

Portfolio Studio API work orders (**PS-01 … PS-06**, branches `cursor/b20-ps*`) are open drafts on `keithbbf-gif/cosmos` but are **not** Website Builder content/staging packs. Keep them on a separate merge train from `content/*` and `sites/*`.

---

## Global merge-order summary

1. **Per pack:** writer (or prose-complete writer) → graphics → editor (when not HOLD).
2. **Respect stacked bases:** e.g. ai-industry #244 on #234; figroots #258 on #237; editor #259 on writer #227; editor #241 on #235; editor #245 on #230; editor #246 on #238; citation #248 on #236.
3. **Rebase or merge `main` into UNSTABLE** branches before review — most content drafts are UNSTABLE.
4. **Resolve DIRTY #245** before any supplements editor merge.
5. **Site packs:** merge ModelRater pair first; defer dual WOW/SLP WOW merges until product owner picks Eleventy vs WP staging canonical paths.
6. **cdm:** unknown until repo is visible to `gh`.

---

## Parallel craft lane hazards (quick reference)

| Pack directory | Open lanes | Hazard |
|----------------|------------|--------|
| `content/ai-industry-blog` | writer #227 + 2× graphics + editor | Same tree; stacked and parallel PRs |
| `content/furniture-craft-blog` | writer #251 + graphics #235 + editor #241 | Graphics/editor not on writer branch |
| `content/furniture-fashion-fads-blog` | writer #252 + graphics #238 + editor HOLD #246 | Stub-only articles |
| `content/supplements-rd-blog` | writer #230 + graphics #240 + editor #245 | Editor **DIRTY** |
| `content/slpwow-speech-pathology-history` | writer #254 + graphics #243 | Possible duplicate article work |
| `sites/*` WOW + SLP | #211, #215, #218, #257 | Product/staging overlap |

---

*Generated for CCr / Gitur handoff. Update this file after each merge or when new pack PRs open.*
