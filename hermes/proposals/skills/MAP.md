# Skills

Hermes skills are agentskills.io `SKILL.md` files. The agent lists names and descriptions, then loads a body only when a task needs it. A learning loop may draft a skill after a hard task. Hermes can write that draft into the profile. This module does not.

The live seam is `cosmos/cosmos_skills.py`. It content-addresses a proposal, ledgers `SKILL_PROPOSED`, and lets only a CCr pen activate through the arbiter fence. `load` re-hashes the active file and refuses tamper. This proposal does not replace that module.

This review copy is an in-memory inbox. `propose` and `propose_from_task` store text under its sha256 and leave it `PROPOSED`. Skill text cannot activate itself. No method on this module mints a human activate flag. `activate` installs one proposal only when three outside facts already hold: the principal starts with `ccr:`, the presented flag matches the flag the human passed at construction, and the skill name sits in a non-empty allowlist. A missing or empty allow enables nothing. `list_skills` returns active name and description only. `load` returns active text only when those bytes still hash to the accepted sha. `ledger` plus `rebuild` replay the same public state.

A body, name, or description that matches `secret_shape`, or that contains a hardline mark, is `HARDLINE` and is not stored. The names `godmode` and `drug-discovery`, including a slug that carries either name, are `HARDLINE`. Nested YAML is refused. The inbox accepts no paths, opens no sockets, and writes no files.

Authority stays with the human CCr. The inbox is not a second ledger and not an attempt workspace. The human flag is compared and never issued here.

Caps are name 64, description 1024, body 65536, allow 32, list budget 4096, and 32 proposals. A higher requested cap is ignored. The policy cap and the requested number are both recorded.

## Ship

- operations: `SCHEMA`, `NAME_CAP`, `DESCRIPTION_CAP`, `BODY_CAP`, `ALLOW_CAP`, `LIST_BUDGET`, `PROPOSAL_CAP`, `GENESIS_FENCE`, `HARDLINE_MARKS`, `HARDLINE_NAMES`, `POLICY`, `Caps`, `SkillText`, `Proposal`, `ActiveSkill`, `SkillCard`, `Row`, `parse_skill`, `policy_caps`, `SkillInbox`, `rebuild`. Public methods on `SkillInbox` are `propose`, `activate`, `list_skills`, `load`, `propose_from_task`, `ledger`, `proposals`, and `actives`.
- refusal codes: `BAD_SKILL`, `BAD_LIMIT`, `BAD_SHA`, `BAD_FLAG`, `BAD_RECORD`, `OVERSIZE`, `NOT_TEXT`, `NOT_LIST`, `NOT_INT`, `NULL_BYTE`, `OUT_OF_RANGE`, `HARDLINE`, `NOT_CCR`, `NO_FLAG`, `FLAG_MISMATCH`, `EMPTY_ALLOW`, `NOT_ALLOWED`, `NO_PROPOSAL`, `ALREADY_DECIDED`, `NOT_FOUND`, `TAMPER`, `DUPLICATE`, `STALE_FENCE`, `BROKEN_CHAIN`, `CLOCK`, `FULL`
- what this module still refuses to execute: it does not write a skill file, does not seed a catalog, does not open a hub or a socket, does not self-activate, does not mint the human flag, and does not run a skill body
- hot-path shape: one pass over active cards in name order; a card that does not fit the remaining list budget is skipped; later cards that fit are kept; allow membership is a set; the hardline scan is one compiled expression

CCr would land this later by calling the live `SkillRegistry`. `propose` and `propose_from_task` append `SKILL_PROPOSED` only. `activate` maps to `accept` under `assert_pen` and the fenced commit on `skill:<name>`, and only when the human flag and the allow entry already exist outside this module. `load` keeps the live hash check. There is no second writer and no self-activation.
