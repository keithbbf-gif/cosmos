# curator

Hermes runs a background maintenance pass over agent-created skills. The deterministic half marks long-unused skills stale, then archived. Pinned skills and skills named by a cron job stay in place. An optional auxiliary-model pass can consolidate overlapping skills. That pass is off unless someone opts in. The curator never auto-deletes. Archive is recoverable. Hub-installed skills stay out of scope. This proposal does not fork a model, move skill directories, or start the inactivity timer.

The live seam is deterministic select. Rank is priority descending, then id ascending. Length is not a rank key. Secret-shaped text is dropped and is not returned. A note that does not fit the remaining byte budget is skipped. Later notes that fit are kept. Duplicate ids refuse. A zero budget returns an empty tuple when every note has non-zero size. That empty selection does not raise. No model is called.

Seam: a projection over memory entries. The ledger stays the authority.

`select` returns the chosen notes. `curate` returns those notes plus the policy cap, the applied budget, the drops, the bytes used, and a digest. Text is capped at 8000 characters. The budget counts utf-8 bytes. A caller who asks for a budget above 1000000 is ignored. The selection records cap 1000000 and uses that ceiling. A lower budget is recorded as asked. `records` copies that public snapshot. `rebuild` packs the chosen notes again and checks the digest. A broken digest, a repeated id inside the snapshot, or a chosen set that does not fit is `STALE`. A schema or cap that is not the policy is `MISMATCH`.

Authority for which notes exist sits with the ledger. This module only projects a budgeted subset. It does not append memory and it does not write skill files.

## Ship

- operations: SCHEMA, POLICY_BUDGET, ID_LIMIT, TEXT_LIMIT, PRIORITY_MIN, PRIORITY_MAX, Candidate, Drop, Selection, Records, select, curate, records, rebuild
- refusal codes: BAD_ID, BAD_ITEMS, BAD_RECORD, DUP_ID, EMPTY, INVISIBLE, MISMATCH, NOT_INT, NOT_TEXT, NULL_BYTE, OUT_OF_RANGE, OVERSIZE, SECRET, STALE. `OVERSIZE` on a `Drop` means the note did not fit the remaining budget and was skipped. `SECRET` on a `Drop` means the text was secret-shaped and was not returned. A raised `SECRET` means the id itself was secret-shaped.
- what this module still refuses to execute: auxiliary-model consolidation, skill archive and restore, pin and adopt mutations, backup archives, ledger appends, inactivity timers, cron threads, and any raise of the byte ceiling
- hot-path shape: one set for duplicate ids, one rank by priority then id, one pack pass that skips a secret or a note that does not fit. The digest hashes each kept text once, and only when `curate` or `rebuild` runs. `select` does not hash.

CCr would land this later as a pure projection in front of the memory ledger. The harness supplies the notes and the budget. A human still persists memory. The skill curator's model pass stays outside this module until a separate approval exists. The policy budget stays 1000000 until policy itself changes.
