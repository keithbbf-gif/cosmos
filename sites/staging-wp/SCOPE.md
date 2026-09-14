# Scope — `sites/staging-wp/`

## In scope

- Staging-ready **WordPress + GeneratePress** packages for two public-facing properties:
  - **WOW Therapies** (`wowtherapies/`) — private practice marketing site (patients and families).
  - **SLP WOW** (`slpwow/`) — professional community site (speech-language pathologists).
- Child themes, page/post Markdown drafts, deployment notes for **MochaHost** hosting with **GeneratePress Premium**, and packaging scripts under this tree only.

## Out of scope (explicit non-goals)

- **COSMOS core** — no changes to `cosmos/`, live runtime, queues, ledgers, KDash, or orchestration code.
- **AI runtime / agent mesh** — no model routing, worker configs, or session handoff artifacts.
- **Patents and proprietary R&D** — no patent text, claim language, internal architecture canon, or unreleased product design from the COSMOS repository.
- **Production credentials** — no API keys, hosting passwords, or live-database dumps in git.

## Disclosure boundary

Content here is **public marketing and professional education** suitable for staging import. It does not describe COSMOS internals, BTS mesh, or patent-pending systems. If material from other repo areas is needed for a site, it must be rewritten for a public audience and reviewed before publish.

## Maintainer note

Pull requests touching this folder should remain limited to `sites/staging-wp/**` unless Keith explicitly expands scope.
