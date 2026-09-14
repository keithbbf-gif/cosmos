# PR triage — Website Builder content & staging packs

**Inventory as of:** 2026-09-14 ~19:40 UTC, refreshed via GitHub REST API against `keithbbf-gif/cosmos` (and `keithbbf-gif/cdm` where visible).

**Prior baseline:** [PR #261](https://github.com/keithbbf-gif/cosmos/pull/261) (first `_ops` triage) → [PR #296](https://github.com/keithbbf-gif/cosmos/pull/296) (refresh #262–#292). **This revision** adds the **supplements integration stack** (`cursor/supplements-rd-integration-85a9`, **#295**), **WXR** follow-up **#293**, and **SEO** cross-link layer **#294**.

**Scope:** Open pull requests for `content/*` editorial packs (writer → graphics → editor craft lanes), `content/_ops` / `_seo` tooling, and `sites/*` staging / marketing packages. Portfolio Studio (**PS-01…PS-06**), Sessions/cDeck B26 trains, and tensor/health jukebox fixes are **out of scope** unless they touch `content/` or `sites/`.

**Policy:** Triage only — **do not auto-merge** anything from this inventory.

---

## Method

```bash
export GH_TOKEN=…   # token with repo read (Cloud Agent git remote token works when `gh` GraphQL fails)
gh pr list --repo keithbbf-gif/cosmos --state open --limit 200 \
  --json number,title,headRefName,isDraft,mergeStateStatus,url,baseRefName,updatedAt
gh pr view <N> --repo keithbbf-gif/cosmos --json baseRefName,mergeStateStatus,files
```

`gh` logged in as the inactive `cursor` host sometimes returns *Could not resolve repository*; setting `GH_TOKEN` from the clone remote was used for this run.

### `keithbbf-gif/cdm`

| Check | Result |
|--------|--------|
| `gh pr list --repo keithbbf-gif/cdm` | **Repository not found** (404) |
| `gh api repos/keithbbf-gif/cdm` | **404 Not Found** |

No open pack PRs could be listed for **cdm** with the credentials available in this environment. Re-run the same `gh` commands with a token that has that repo scope and append a **cdm** section (preferred path on cdm: `web/staging/PR_TRIAGE.md`).

---

## Since PR #296 (delta summary)

| Change | Detail |
|--------|--------|
| **Supplements craft stack** | Integration branch **`cursor/supplements-rd-integration-85a9`** (writer **#230** lineage + **#240** SVG embeds, no open PR). Remediation editor **#295** stacks on integration — **close #245 without merge** (dirty / figure-stripping risk). |
| **WXR lane** | **#293** stacks on **#280** — real pack paths + sample WXR smoke exports (`content/_ops/`). |
| **SEO lane** | **#294** stacks on **#283** — cross-link menus from publish queues (`content/_seo/` + pack `INDEX.md`). |
| **Unchanged blockers** | **#245** (supplements, **DIRTY**); **#290** (ancient furniture, **DIRTY** duplicate of **#282**). |
| **Ready (non-draft) open PRs** | Unchanged set on `main`: #224, #227, #230, #236, #243, #249, #250, #252, #254, #257, #260, #268, #274 — merge review can proceed without draft promotion. |

---

## Craft lanes (dependency)

| Lane | Typical PR signals | Must land before |
|------|-------------------|------------------|
| **Writer** | “blog pack”, “staged drafts”, `content/<pack>/drafts/` | Graphics & editor for same pack |
| **Graphics** | “graphics pipeline”, SVG embeds, `figures/` | Editor pass (unless editor is docs-only HOLD) |
| **Editor** | “editor pass”, voice/stub de-clone, `EDITOR_REPORT.md` | Publish / WP deploy (out of scope here) |
| **Unify / craft** | “unify”, “merge prose with SVG”, stacked on merge branches | Single merge to `main` per pack |
| **WXR** | `wxr`, `WXR`, `draft-import`, `content/_ops/*wxr*` | After pack trees + SEO INDEX wiring are stable |
| **SEO** | `pillar`, `publish queue`, `cross-link`, `content/_seo/` | Before WXR export if menus/INDEX must appear in exports |
| **Site pack** | `sites/<name>/`, Eleventy / static / WP staging bundles | Independent per site tree (watch cross-site copy only) |

**Stacked PRs** (base branch ≠ `main`) must merge **in stack order** (bottom → top), then the stack tip to `main`.

**Merge state** (GitHub): `CLEAN` | `UNSTABLE` (behind base) | `DIRTY` (conflicts). **Draft** vs **ready** is separate from mergeability.

---

## Cross-pack infrastructure (open)

| PR | Lane | Title | Base | State | Notes |
|----|------|-------|------|-------|-------|
| [#275](https://github.com/keithbbf-gif/cosmos/pull/275) | rights | Rights hunt: PD/CC portraits for four staged history packs | `main` | Draft, CLEAN | Source overlay for **#281** |
| [#281](https://github.com/keithbbf-gif/cosmos/pull/281) | rights | Cherry-pick rights overlay from PR #275 into history packs | `main` | Draft, UNSTABLE | **Merge after** pack prose+graphics stable; large footprint (~436 files) |
| [#266](https://github.com/keithbbf-gif/cosmos/pull/266) | SEO | Staged SEO pillar maps for Keith brand lanes | `main` | Draft, CLEAN | `content/_seo/` |
| [#283](https://github.com/keithbbf-gif/cosmos/pull/283) | SEO | Wire SEO publish queues into pack INDEX files | `cursor/seo-brand-pillar-maps-6cc5` | Draft, UNSTABLE | Stacks on **#266** |
| [#294](https://github.com/keithbbf-gif/cosmos/pull/294) | SEO | Staged cross-link menus from SEO publish queues | `cursor/seo-wire-publish-queue-65eb` | Draft, UNSTABLE | Stacks on **#283**; touches many pack `INDEX.md` |
| [#280](https://github.com/keithbbf-gif/cosmos/pull/280) | WXR | WXR draft-import generators for COSMOS content packs | `main` | Draft, UNSTABLE | `content/_ops/` generators |
| [#293](https://github.com/keithbbf-gif/cosmos/pull/293) | WXR | Real content pack paths and sample WXR smoke exports | `cursor/wxr-draft-import-ad28` | Draft, UNSTABLE | Stacks on **#280** |
| [#286](https://github.com/keithbbf-gif/cosmos/pull/286) | research | Website Builder competitor UX teardown pack | `main` | Draft, UNSTABLE | `content/_research/` — no merge dependency on packs |

**Suggested order:** per-pack merges → **#281** (rights) → **#266** → **#283** → **#294** (SEO) → **#280** → **#293** (WXR). **#286** anytime.

**Conflict risk (infra):** **#283** / **#294** fan out across pack `INDEX.md` files — high chance of textual conflicts with in-flight editor PRs; land or rebase pack craft PRs first. **#281** is a wide cherry-pick (~436 files) — expect conflicts if merged before pack unification.

---

## Content packs — open PRs (`keithbbf-gif/cosmos`)

### `content/ai-industry-blog`

| PR | Title | Status | Lane | Base | Merge state |
|----|-------|--------|------|------|-------------|
| [#227](https://github.com/keithbbf-gif/cosmos/pull/227) | AI industry blog pack: 42 public-record drafts (2020–2026) | **Ready**, OPEN | writer | `main` | UNSTABLE |
| [#234](https://github.com/keithbbf-gif/cosmos/pull/234) | feat(content): AI industry blog graphics library | Draft, OPEN | graphics | `main` | UNSTABLE |
| [#244](https://github.com/keithbbf-gif/cosmos/pull/244) | AI industry blog graphics wave 2 + draft embeds | Draft, OPEN | graphics | `cursor/ai-industry-blog-graphics-e22a` | CLEAN |
| [#259](https://github.com/keithbbf-gif/cosmos/pull/259) | docs(ai-industry-blog): editor pass on pack 42 (stacked) | Draft, OPEN | editor | `cursor/ai-industry-blog-pack-019f` | UNSTABLE |

**Suggested merge order:** `#227` → `#234` → `#244` → `#259`.

**Conflict risk:** High — stacked graphics + editor on writer branch; refresh UNSTABLE branches before review.

---

### `content/supplements-rd-blog`

| PR / branch | Title | Status | Lane | Base | Merge state |
|-------------|-------|--------|------|------|-------------|
| [#230](https://github.com/keithbbf-gif/cosmos/pull/230) | Supplements R&D blog: editor pass (40 drafts, voice_check edited) | **Ready**, OPEN | writer/editor prose | `main` | CLEAN |
| [#240](https://github.com/keithbbf-gif/cosmos/pull/240) | feat(content): supplements R&D blog editorial SVG graphics pack | Draft, OPEN | graphics | `main` | UNSTABLE |
| *(branch)* | **`cursor/supplements-rd-integration-85a9`** — writer + **#240** embeds (`embed_graphics.py`) | **No open PR** | **craft / integration** | *(ahead of `main`)* | — |
| [#295](https://github.com/keithbbf-gif/cosmos/pull/295) | Clean editor pass — supplements R&D blog (figures preserved) | Draft, OPEN | editor (remediation) | `cursor/supplements-rd-integration-85a9` | UNSTABLE |
| [#245](https://github.com/keithbbf-gif/cosmos/pull/245) | Editor pass: supplements R&D blog (40 drafts) | Draft, OPEN | editor (**stale**) | `cursor/supplements-rd-blog-ee57` | **DIRTY** |

**Suggested merge order:**

1. **`#230` → `#240`** to `main`, **or** one merge PR from **`cursor/supplements-rd-integration-85a9` → `main`** (preferred craft artifact — already contains embedded figures).
2. **`#295` → `main`** after integration is on `main` (or squash-merge integration + **#295** as a single stack).
3. **Close `#245` without merge** — superseded by **#295**; see `content/_ops/REMEDIATION_REPORT.md` / `DIRTY_PR_NOTES.md` on the **#295** branch.

**Conflict risk:** **High** — three editor-shaped PRs (**#230**, **#245**, **#295**) plus parallel graphics **#240**. **#245** is **DIRTY** and must not merge. Rebasing **#295** without landing integration first will duplicate figure embed work.

---

### `content/furniture-craft-blog`

| PR | Title | Status | Lane | Base | Merge state |
|----|-------|--------|------|------|-------------|
| [#251](https://github.com/keithbbf-gif/cosmos/pull/251) | Furniture craft magazine blog pack (44 staged drafts) | Draft, OPEN | writer | `main` | UNSTABLE |
| [#235](https://github.com/keithbbf-gif/cosmos/pull/235) | GRAPHICS: furniture-craft-blog SVG diagrams (45 drafts) | Draft, OPEN | graphics | `main` | UNSTABLE |
| [#263](https://github.com/keithbbf-gif/cosmos/pull/263) | Merge furniture-craft prose (#251) with graphics pack | Draft, OPEN | unify | `cursor/furniture-craft-blog-623a` | UNSTABLE |
| [#272](https://github.com/keithbbf-gif/cosmos/pull/272) | Editor pass: furniture craft blog prose (44 essays) | Draft, OPEN | editor | `cursor/furniture-craft-blog-623a` | CLEAN |
| [#241](https://github.com/keithbbf-gif/cosmos/pull/241) | Editor pass: furniture-craft-blog voice and stub de-clone (45 drafts) | Draft, OPEN | editor | `cursor/furniture-craft-graphics-99ed` | UNSTABLE |
| [#279](https://github.com/keithbbf-gif/cosmos/pull/279) | **Unify furniture-craft editor prose with SVG embeds (#263 + #272)** | Draft, OPEN | **craft** | `cursor/furniture-craft-merge-1ad4` | UNSTABLE |

**Suggested merge order:** `#251` + `#235` → `#263` → `#272` → **`#279`** (canonical craft merge). Treat **`#241`** as legacy unless explicitly revived.

**Conflict risk:** High — parallel graphics (#235) vs writer (#251); **#279** is the intended single merge artifact.

---

### `content/furniture-fashion-fads-blog` (FFFB)

| PR | Title | Status | Lane | Base | Merge state |
|----|-------|--------|------|------|-------------|
| [#252](https://github.com/keithbbf-gif/cosmos/pull/252) | Furniture fashion & fads — 44 figured articles filled + 42 long drafts | **Ready**, OPEN | writer | `main` | UNSTABLE |
| [#238](https://github.com/keithbbf-gif/cosmos/pull/238) | feat(content): furniture-fashion-fads editorial graphics pack | Draft, OPEN | graphics | `main` | UNSTABLE |
| [#262](https://github.com/keithbbf-gif/cosmos/pull/262) | Fill 44 furniture/fashion fad articles (keep #238 figures) | Draft, OPEN | writer (fill) | `main` | UNSTABLE |
| [#269](https://github.com/keithbbf-gif/cosmos/pull/269) | Fill 44 #238 stubs with magazine prose (unblocks #246 hold) | Draft, OPEN | writer (fill) | `main` | UNSTABLE |
| [#246](https://github.com/keithbbf-gif/cosmos/pull/246) | docs(content): FFFB editor hold — stub inventory (await WRITER prose) | Draft, OPEN | editor (HOLD) | `cursor/furniture-fashion-fads-graphics-46bc` | UNSTABLE |
| [#273](https://github.com/keithbbf-gif/cosmos/pull/273) | Editor pass: furniture-fashion-fads blog (voice, grammar, EDITOR_REPORT) | Draft, OPEN | editor | `cursor/furniture-fashion-fads-blog-a5c3` | UNSTABLE |

**Suggested merge order:** **`#252`** (canonical prose) → drop or close redundant **`#262` / `#269`** after diff review → `#238` → `#273` (revisit **`#246`** hold).

**Conflict risk:** **Three writer-shaped PRs** (#252, #262, #269) — pick one prose source before graphics finalization.

---

### `content/furniture-history-ancient-blog`

| PR | Title | Status | Lane | Base | Merge state |
|----|-------|--------|------|------|-------------|
| [#253](https://github.com/keithbbf-gif/cosmos/pull/253) | Draft: History of Furniture magazine series (43 essays) | Draft, OPEN | writer | `main` | CLEAN |
| [#236](https://github.com/keithbbf-gif/cosmos/pull/236) | feat(content): ancient furniture blog — graphics pack (44 essays, 176 SVGs) | **Ready**, OPEN | graphics | `main` | UNSTABLE |
| [#248](https://github.com/keithbbf-gif/cosmos/pull/248) | Citation pass: deepen evidence for seven ancient furniture essays | Draft, OPEN | editor/citation | `cursor/furniture-ancient-graphics-2a96` | UNSTABLE |
| [#282](https://github.com/keithbbf-gif/cosmos/pull/282) | **Unify ancient furniture history pack (prose + graphics + citations)** | Draft, OPEN | **craft (preferred)** | `cursor/furniture-history-ancient-blog-bbf1` | UNSTABLE |
| [#290](https://github.com/keithbbf-gif/cosmos/pull/290) | Stack furniture-history prose (#253) + graphics embeds (#236) | Draft, OPEN | craft (duplicate) | `cursor/furniture-history-ancient-blog-bbf1` | **DIRTY** |

**Suggested merge order:** **`#282` only** (includes prose #253, graphics #236, citation lane). **Prefer #282 over #290** for history — **close or abandon #290** (DIRTY duplicate stack).

**Conflict risk:** **#290 vs #282** — do not merge both; **#248** may fold into **#282** or follow as a thin citation PR.

---

### `content/furniture-woods-500y-blog` (woods series)

| PR | Title | Status | Lane | Base | Merge state |
|----|-------|--------|------|------|-------------|
| [#260](https://github.com/keithbbf-gif/cosmos/pull/260) | docs: 46 furniture-woods magazine drafts (aligned to graphics PR 249) | **Ready**, OPEN | writer | `main` | CLEAN |
| [#249](https://github.com/keithbbf-gif/cosmos/pull/249) | feat(content): publish-ready furniture-woods figures (5 SVG + embeds) | **Ready**, OPEN | graphics | `main` | UNSTABLE |
| [#278](https://github.com/keithbbf-gif/cosmos/pull/278) | Editor pass: furniture-woods 500y blog (46 drafts) | Draft, OPEN | editor | `cursor/furniture-woods-500y-blog-23c0` | UNSTABLE |

**Suggested merge order:** `#260` → `#249` → `#278`.

**Conflict risk:** Low across packs; watch slug overlap with other furniture lanes.

---

### `content/figroots-blog` (grower / magazine — **not** fig-history)

| PR | Title | Status | Lane | Base | Merge state |
|----|-------|--------|------|------|-------------|
| [#224](https://github.com/keithbbf-gif/cosmos/pull/224) | FigRoots magazine pack: 45 keepable evergreen drafts | **Ready**, OPEN | writer | `main` | CLEAN |
| [#237](https://github.com/keithbbf-gif/cosmos/pull/237) | feat(figroots): blog graphics pipeline and SVG embeds (12 drafts) | Draft, OPEN | graphics | `main` | UNSTABLE |
| [#258](https://github.com/keithbbf-gif/cosmos/pull/258) | figroots-blog: second-pass graphics quality | Draft, OPEN | graphics (pass 2) | `cursor/figroots-graphics-7107` | UNSTABLE |
| [#265](https://github.com/keithbbf-gif/cosmos/pull/265) | docs(figroots): editor pass on drafts 41–45 (45-pack) | Draft, OPEN | editor | `cursor/figroots-blog-5eba` | CLEAN |

**Suggested merge order:** `#224` → `#237` → `#258` → `#265`.

**Conflict risk:** Medium — graphics pass-2 stacked; do not confuse with **`content/fig-history-ancient-to-today`** below.

---

### `content/fig-history-ancient-to-today` (History of the Fig)

| PR | Title | Status | Lane | Base | Merge state |
|----|-------|--------|------|------|-------------|
| [#250](https://github.com/keithbbf-gif/cosmos/pull/250) | History of the Fig — graphics pack (ancient to today) | **Ready**, OPEN | graphics | `main` | CLEAN |
| [#271](https://github.com/keithbbf-gif/cosmos/pull/271) | History of the Fig: staged ancient-to-today magazine series | Draft, OPEN | writer | `main` | UNSTABLE |
| [#292](https://github.com/keithbbf-gif/cosmos/pull/292) | Editor pass: fig-history essays (voice_check edited) | Draft, OPEN | editor | `cursor/fig-history-graphics-762d` | UNSTABLE |

**Suggested merge order:** **`#250` + `#271`** (prose) → **`#292`** (editor on fig-history graphics branch). Pair **#250 + #292** for the fig-history lane.

**Conflict risk:** Medium — editor stacked on graphics; writer **#271** parallel on `main`.

---

### `content/herbal-medicine-history-blog`

| PR | Title | Status | Lane | Base | Merge state |
|----|-------|--------|------|------|-------------|
| [#274](https://github.com/keithbbf-gif/cosmos/pull/274) | feat: herbal-history prose pack on the graphics shells (40 essays) | **Ready**, OPEN | writer | `main` | CLEAN |
| [#242](https://github.com/keithbbf-gif/cosmos/pull/242) | feat: herbal medicine history blog — graphics pipeline and 80 SVG embeds | Draft, OPEN | graphics | `main` | UNSTABLE |
| [#255](https://github.com/keithbbf-gif/cosmos/pull/255) | Herbal medicine history magazine blog pack (45 drafts) | Draft, OPEN | writer (alt) | `main` | UNSTABLE |
| [#270](https://github.com/keithbbf-gif/cosmos/pull/270) | Editor pass: herbal medicine history blog (45 drafts) | Draft, OPEN | editor | `cursor/herbal-medicine-history-blog-231e` | UNSTABLE |
| [#276](https://github.com/keithbbf-gif/cosmos/pull/276) | Editor pass: herbal history prose on graphics shells (#242 / #274 stack) | Draft, OPEN | editor | `cursor/herbal-history-prose-on-graphics-231e` | UNSTABLE |

**Suggested merge order:** **`#274`** → `#242` → **`#276`** (prefer over **#270** if **#274** is canonical prose). Reconcile **#255** vs **#274** before merge.

**Conflict risk:** Two writer shapes (#255 vs #274) — same pattern as FFFB.

---

### `content/slpwow-speech-pathology-history`

| PR | Title | Status | Lane | Base | Merge state |
|----|-------|--------|------|------|-------------|
| [#254](https://github.com/keithbbf-gif/cosmos/pull/254) | SLPWOW speech-pathology history pack (staged, 40 articles + real portraits) | **Ready**, OPEN | writer | `main` | CLEAN |
| [#243](https://github.com/keithbbf-gif/cosmos/pull/243) | SLPWOW history graphics pipeline + cleared portraits | **Ready**, OPEN | graphics | `main` | CLEAN |
| [#267](https://github.com/keithbbf-gif/cosmos/pull/267) | docs(content): SLPWOW speech-pathology history — editor pass | Draft, OPEN | editor | `cursor/slpwow-speech-pathology-history-b9a7` | UNSTABLE |

**Suggested merge order:** `#254` → `#243` → `#267`.

**Conflict risk:** Low — both writer and graphics are **ready CLEAN**; editor is the remaining gate.

---

### `content/ai-history-retrospective`

| PR | Title | Status | Lane | Base | Merge state |
|----|-------|--------|------|------|-------------|
| [#256](https://github.com/keithbbf-gif/cosmos/pull/256) | History of AI retrospective (COPY) — aligned with graphics #247 | Draft, OPEN | writer | `main` | CLEAN |
| [#247](https://github.com/keithbbf-gif/cosmos/pull/247) | feat(content): AI history retrospective graphics pipeline (staged) | Draft, OPEN | graphics | `main` | CLEAN |
| [#264](https://github.com/keithbbf-gif/cosmos/pull/264) | docs(content): editor pass — AI history retrospective (stacked on #256) | Draft, OPEN | editor | `cursor/ai-history-retrospective-7b08` | UNSTABLE |

**Suggested merge order:** `#256` → `#247` → `#264`.

**Conflict risk:** Medium — writer COPY lane vs graphics; confirm figure overlap before merge.

---

### `content/wowtherapies-therapy-history`

| PR | Title | Status | Lane | Base | Merge state |
|----|-------|--------|------|------|-------------|
| [#268](https://github.com/keithbbf-gif/cosmos/pull/268) | WOWTherapies therapy-history pack (42 staged educational essays) | **Ready**, OPEN | writer | `main` | CLEAN |
| [#257](https://github.com/keithbbf-gif/cosmos/pull/257) | feat(content): Wow Therapies therapy-history staged SVG graphics | **Ready**, OPEN | graphics | `main` | CLEAN |
| [#277](https://github.com/keithbbf-gif/cosmos/pull/277) | Editor pass: WOW Therapies therapy history (42 essays) | Draft, OPEN | editor | `cursor/wowtherapies-therapy-history-b51d` | UNSTABLE |

**Suggested merge order:** `#268` → `#257` → `#277`. Coordinate with **`sites/wowtherapies`** (#218) and **`sites/staging-wp`** (#215).

**Conflict risk:** Thematic overlap with site packs, not necessarily git conflicts.

---

## Site & staging packs — open drafts (`sites/*`)

Independent trees; merge order mostly **per site**, except WOW / SLP WOW cross-links.

| PR | Pack / dependency | Title | Merge state |
|----|-------------------|-------|-------------|
| [#211](https://github.com/keithbbf-gif/cosmos/pull/211) | `sites/slpwow` (Eleventy) | feat(sites): SLP WOW community site package (slpwow.com) | CLEAN |
| [#215](https://github.com/keithbbf-gif/cosmos/pull/215) | `sites/staging-wp` (WP + GP) | feat(sites): staging WordPress + GeneratePress packages | CLEAN |
| [#218](https://github.com/keithbbf-gif/cosmos/pull/218) | `sites/wowtherapies` | feat: WOW Therapies marketing site | CLEAN |
| [#219](https://github.com/keithbbf-gif/cosmos/pull/219) | `sites/dailyscar`, `sites/lmnator` | feat(sites): DailyScar and LMNator premium static marketing packages | CLEAN |
| [#212](https://github.com/keithbbf-gif/cosmos/pull/212) | `sites/ai-cluster-hub` | feat(sites): private AI Cluster staging hub | CLEAN |
| [#214](https://github.com/keithbbf-gif/cosmos/pull/214) | `sites/modelraters` | feat(sites): ModelRater marketing shell | CLEAN |
| [#216](https://github.com/keithbbf-gif/cosmos/pull/216) | `sites/mdrater` (alias) | feat(sites): mdrater.com alias shell for ModelRater | CLEAN |
| [#213](https://github.com/keithbbf-gif/cosmos/pull/213) | `sites/brokentokn` | feat(sites): BrokenTokn marketing shell | CLEAN |

**Suggested merge order (sites):**

1. **ModelRater cluster:** `#214` → `#216`.
2. **Parallel (no shared paths):** `#212`, `#213`, `#219`.
3. **WOW / SLP cluster:** align **`#218`** / **`#215`** / **`#211`** with product intent; merge therapy **content** `#268` → `#257` → `#277` before treating WP staging as canonical copy.
4. **SLP content + site:** `#254` → `#243` → `#267` before or in parallel with **`#211`** (Eleventy).

**Conflict risk:** Thematic overlap — `#215` vs `#218` (WOW Therapies), `#211` vs `#215` (SLP WOW). `sites/shared` in **#219** may affect verify scripts used elsewhere.

---

## Out of scope (open on same repo)

| Train | Examples | Note |
|-------|----------|------|
| Portfolio Studio | **#220–#223**, **#225–#226**, **#228–#229**, **#231–#233**, **#239** | API / profiles / jukebox — not Website Builder packs |
| Sessions / cDeck B26 | **#284–#285**, **#288–#291**, **#287**, **#289** | Separate merge train from `content/*` |
| cDeck arch doc | **#217** | Useful reference, not a content pack |
| Prior triage PRs | **#261**, **#296** | Superseded by the branch that updates this file |

---

## Global merge-order summary

1. **Per pack:** writer (or prose-complete **ready** writer) → graphics → editor / unify craft PR.
2. **Explicit craft targets:** supplements **`cursor/supplements-rd-integration-85a9` + `#295`** (not **`#245`**); furniture-craft **`#279`**; ancient furniture **`#282`** (not **#290**); fig-history **`#250` → `#292`** with **`#271`**; rights **`#281`** after packs.
3. **Respect stacked bases:** ai-industry **#244** on **#234**; figroots **#258** on **#237**; SEO **#283** on **#266**, **#294** on **#283**; WXR **#293** on **#280**; supplements **#295** on integration branch (see per-pack tables).
4. **Rebase or merge `main` into UNSTABLE** branches before review — many drafts remain UNSTABLE even when **ready**.
5. **Do not merge DIRTY:** supplements **`#245`**; duplicate ancient stack **`#290`**.
6. **Site packs:** ModelRater pair first; defer dual WOW/SLP WOW merges until canonical staging path is chosen.
7. **Infra last:** SEO stack **#266 → #283 → #294**, then WXR **#280 → #293**, after pack craft merges to reduce `INDEX.md` churn conflicts.
8. **cdm:** unknown until repo is visible to `gh`.

---

## Parallel craft lane hazards (quick reference)

| Pack directory | Open lanes | Hazard |
|----------------|------------|--------|
| `content/ai-industry-blog` | writer **#227** + 2× graphics + editor | Stacked + parallel on `main` |
| `content/furniture-craft-blog` | writer + graphics + merge **#263** + **#279** | **#279** is craft target; **#241** legacy |
| `content/furniture-fashion-fads-blog` | **#252** + **#262** / **#269** + graphics + editors | Pick one writer source |
| `content/supplements-rd-blog` | **#230** + **#240** + integration branch + **#295** + **#245 DIRTY** | Land integration before **#295**; close **#245** |
| `content/_seo` + pack INDEX | **#266** → **#283** → **#294** | Cross-pack INDEX edits vs editor PRs |
| `content/_ops` WXR | **#280** → **#293** | After packs + SEO wiring |
| `content/furniture-history-ancient-blog` | **#282** vs **#290 DIRTY** | **Prefer #282** |
| `content/fig-history-ancient-to-today` | **#250** + **#271** + **#292** | Not `figroots-blog` |
| `content/herbal-medicine-history-blog` | **#274** vs **#255** | Two writer lanes |
| `content/slpwow-speech-pathology-history` | ready writer + ready graphics + editor | Low git risk |
| `sites/*` WOW + SLP | **#211**, **#215**, **#218**, content **#257** / **#268** | Product/staging overlap |

---

*Generated for CCr / Gitur handoff. Update this file after each merge or when new pack PRs open.*
