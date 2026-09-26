# Gitur BUILD — fenced-activate Superpowers skill verification-before-completion

**Repo (PRIVATE):** `keithbbf-gif/cosmos`
**Branch:** `ccr/skill-activate` from GitHub `main`. Not unique HEAD `8b5ad84`.
**Lane B:** Cursor Cloud Agent, Opus 5 / Sonnet class. Composer 2.5 / Auto refused. Do not change Opus T.
**P10:** PROPOSE only. `SkillRegistry.accept` requires CCr pen (`cosmos_ccr.assert_pen`). This run does **not** hold the pen; it proposes the path CCr will execute.
**Do not:** spawn grok.exe, pull 8b5ad84, merge leftover PRs, USPTO, self-activate skills, activate all six skills this pass, mkdir on GET /skills.

FIRST read `docs/AGENT_BRIEF.md` and `docs/AGENT_BOUNDARIES.md`. Then `docs/STEAL_MAP.md` order item 6 and `cosmos/cosmos_skills.py`.

## Already on this tree (do not re-build)

- Hermes four: `cosmos_approval.py` `cosmos_delegate.py` `cosmos_recall.py` `cosmos_skills.py`. Tests 46/46.
- Superpowers pack: six `SKILL.md` under `work_orders/ccr/skills/` — **propose-only**, not fenced-activated.
  - `verification-before-completion` (this pass)
  - `brainstorm-before-code` `plan-for-junior` `quality-reviewer` `spec-reviewer` `tdd-subagent` (later)
- `GET /api/v1/skills` **200** (UNMEASURED until an active skill exists). GET never mkdir.
- `SkillRegistry.propose` → content-addressed `state/skills/proposed/<sha>/SKILL.md` + `SKILL_PROPOSED`.
- `SkillRegistry.accept(sha, ccr_sid=…)` → `assert_pen` + arbiter `fenced_commit` on `skill:<name>` + `SKILL_ACCEPTED`.
- `load()` re-hashes; outside-fence edit is `TAMPERED`.

## Job

Fenced-activate **one** skill: **verification-before-completion**.

Body already on disk:

```
work_orders/ccr/skills/verification-before-completion/SKILL.md
```

Frontmatter `name: verification-before-completion`. Portable SCAR_PLACATION: a claim is not evidence; runtime-binding only.

Path (do not invent another):

1. `SkillRegistry.propose(principal, text)` from that SKILL.md (HARDLINE classifier already on command-looking lines).
2. CCr (after this PR is reviewed) calls `SkillRegistry.accept(sha, ccr_sid=<lease sid>)` with the live pen. Agents never call `accept` without the pen (`NO_PEN`).
3. Runtime bind: `GET /api/v1/skills` lists `verification-before-completion` as active; ledger `SKILL_ACCEPTED` with the sha; `load()` matches sha.

This pass proposes: (a) any missing CLI/verb so CCr can `--accept` without a REPL, (b) a bite that `accept` without pen raises `NO_PEN`, (c) a bite that GET still never mkdir when no skills are active. Do **not** write `live/state/skills/active/` from Cursor.

Do not activate the other five. Format is agentskills.io — do not invent another skill product.

## Bite

- Missing pen → `SkillError.kind == NO_PEN`; no `SKILL_ACCEPTED`.
- Tampered proposed file → `TAMPERED`; accept refuses.
- GET /skills with empty active set → 200 `kind=UNMEASURED`, no mkdir.
- HARDLINE command in a skill body → `SKILL_REFUSED` at propose (already tested; do not regress).

## Output

Unified diffs + a CCr runbook (exact `propose` then `accept` calls, sha of the on-disk SKILL.md) under `proposals | SKILL_ACTIVATE.json`. PR `WO: fenced-activate verification-before-completion`. Gitur BUILD. autoCreatePR.
