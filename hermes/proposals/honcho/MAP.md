# Honcho

Hermes Honcho keeps a separate peer for each person and accumulates observations about preferences, style, and goals. Conflicting claims stay in the evidence together. The hosted product also refreshes a base context layer and a dialectic layer on a cadence and searches conclusions over the network.

The live seam is a projection, not a SEED. `cosmos/cosmos_recall.py` remains the session-search projection and does not own a per-principal dialectic log. This module does not write the authority ledger.

`Honcho` starts disabled. `enable` arms it. There is no off switch. `observe(principal, text, now)` appends one claim. `contradict(principal, claim_a, claim_b, now)` appends both claims under one pair. `profile(principal)` returns that peer's claims newest first (`now`, then sequence), at most 32. A higher cap is ignored, and the policy cap 32 stays on `recorded_cap`. An unknown peer refuses. Each peer stores at most 256 claims. `dialectic(principal)` projects notes from those claims: one pass, newest first, skipping any claim whose text does not fit the remaining character budget of 600. A higher budget or a depth above 3 is ignored, and the policy caps stay on the result. Depth does not invent sentences and does not call a model. `export_projection` returns frozen rows whose `authority` is `projection` and whose schema is `cosmos-hermes-honcho/1`. `rebuild` replays those rows into the same claims and the same notes. `now` is an int the caller supplies. The module does not read a clock.

Authority lives in the projection. The log is evidence, not a SEED and not a handoff. A row whose authority is `seed` refuses. A row whose authority is `handoff` refuses. Notes are derived from claims. Feeding notes back into `rebuild` refuses. Text that matches `secret_shape` raises `SECRET` and is not stored. Duplicate sequence numbers, a stale chain fence, and a broken hash refuse.

Refusal codes: `DISABLED`, `EMPTY`, `SECRET`, `NOT_TEXT`, `NULL_BYTE`, `OVERSIZE`, `NOT_INT`, `OUT_OF_RANGE`, `FULL`, `UNKNOWN_PEER`, `NOT_SEED`, `NOT_HANDOFF`, `BAD_SCHEMA`, `BAD_KIND`, `BAD_PAIR`, `BAD_NOTE`, `BAD_RECORD`, `BAD_HASH`, `CHAIN`, `STALE`, `DUP_ID`, `BAD_SEQ`, `CAP`.

CCr would land this later as a rebuildable read model beside recall. Ledger turns would feed `observe` and `contradict`. Dropping the projection and replaying the exported rows reproduces the claims and the dialectic notes. The landing stays off the network and never promotes a note to a SEED or to a second handoff.

## Ship

- operations: `DEPTH_CAP`, `GENESIS`, `NOTE_BUDGET`, `POLICY_CAP`, `PRINCIPAL_CAP`, `SCHEMA`, `STORE_CAP`, `TEXT_CAP`, `Claim`, `DataRecord`, `Dialectic`, `Honcho`, `Note`, `evidence_sha`, `rebuild`, `Honcho.enable`, `Honcho.observe`, `Honcho.contradict`, `Honcho.profile`, `Honcho.dialectic`, `Honcho.export_projection`, `Honcho.recorded_cap`, `Honcho.recorded_budget`, `Honcho.recorded_depth`
- refusal codes: `DISABLED`, `EMPTY`, `SECRET`, `NOT_TEXT`, `NULL_BYTE`, `OVERSIZE`, `NOT_INT`, `OUT_OF_RANGE`, `FULL`, `UNKNOWN_PEER`, `NOT_SEED`, `NOT_HANDOFF`, `BAD_SCHEMA`, `BAD_KIND`, `BAD_PAIR`, `BAD_NOTE`, `BAD_RECORD`, `BAD_HASH`, `CHAIN`, `STALE`, `DUP_ID`, `BAD_SEQ`, `CAP`
- what this module still refuses to execute: a Honcho network call, `peer.chat` synthesis, semantic search, session prewarm, raw API keys, disabling the gate, raising the profile cap, the note budget, or the depth cap, and any use of a note or a handoff as authority
- hot-path shape: one dict of claims per peer; profile sorts that peer and stops at the count cap; dialectic walks that order once and skips claims that do not fit the remaining character budget
