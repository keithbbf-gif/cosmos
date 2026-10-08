# credential_pools

Hermes keeps several credential ids for one provider and rotates among the healthy ones. Selection strategies are `fill_first` (the default), `round_robin`, `least_used`, and `random`. A transient HTTP 429 confirms once on that same credential; the next 429 benches it. HTTP 402 benches immediately. HTTP 401 tries one OAuth refresh, then benches the id. Hermes benches rate-limit and billing failures for an hour and auth failures for five minutes, unless the provider supplies `reset_at`. When every id is cooling, Hermes may call `fallback_model` on a different provider. A pool rotation is not a provider change. Fallback is a separate feature. Hermes keeps pool metadata in `auth.json` and may borrow an env secret without writing the secret back. A rotated key has no prompt-cache prefix of its own.

The live seam is `cosmos/cosmos_cred_kit.py`. The kit names sources and keeps secret bytes out of GET. This proposal does not import the kit and does not read those files.

`CredentialPool` is an in-memory ledger for one provider. `add` stores a credential id. `next_id(now)` returns the next id that is not cooling and counts that selection. `report(id, code, now)` sets cooldown until `now + 60` for `HTTP_429` and `HTTP_401`. Any other accepted code leaves the current id in place and does not switch provider. `report(..., confirm=True)` on the first consecutive `HTTP_429` is the one confirming retry and does not bench; the next `HTTP_429` benches even when `confirm` is true. `reveal` refuses. `change_provider` refuses, including when every id is cooling. A requested cap above 8 is stored and not applied. `random` is refused because a selection must be repeatable. The module performs no IO and reads no clock.

Each committed add, selection, and report appends a `PoolRecord`. `rebuild` replays that chain into the same public status. A broken link is `CHAIN`. A malformed record is `BAD_RECORD`. A `now` earlier than the last committed `next_id` or `report` is `STALE` and does not change the pool. `status` stays a peek and does not move that fence.

The human names credential ids. The caller passes `now`. Authority for this ledger is the pool itself. Secret bytes stay in the kit. The pool is not a secret projection and not an attempt workspace.

Refusal codes are `SECRET`, `PLAINTEXT`, `PROVIDER_FIXED`, `POOL_EXHAUSTED`, `EMPTY`, `CAP`, `DUPLICATE`, `UNKNOWN_ID`, `UNCLASSIFIED`, `UNKNOWN_STRATEGY`, `NONDETERMINISTIC`, `MISSING_ID`, `MISSING_PROVIDER`, `BAD_ID`, `BAD_PROVIDER`, `NOT_TEXT`, `NULL_BYTE`, `OVERSIZE`, `NOT_INT`, `OUT_OF_RANGE`, `STALE`, `CHAIN`, and `BAD_RECORD`.

CCr would call `next_id` from the provider rail and let `cosmos_cred_kit` resolve that id on the existing path that never echoes a secret. `POOL_EXHAUSTED` ends the attempt. CCr would not add a second provider here and would not implement `reveal`.

## Ship

Operations: `SCHEMA`, `POLICY_CAP`, `COOLDOWN_S`, `MAX_CONFIRMING_RETRIES`, `RETRY_CLASS`, `Action`, `Strategy`, `Cred`, `PoolRecord`, `PoolStatus`, `Report`, `CredentialPool`, `rebuild`, `reveal`. `CredentialPool` methods are `add`, `next_id`, `report`, `status`, `change_provider`, `reveal`, and `records`.

Refusal codes: `SECRET`, `PLAINTEXT`, `PROVIDER_FIXED`, `POOL_EXHAUSTED`, `EMPTY`, `CAP`, `DUPLICATE`, `UNKNOWN_ID`, `UNCLASSIFIED`, `UNKNOWN_STRATEGY`, `NONDETERMINISTIC`, `MISSING_ID`, `MISSING_PROVIDER`, `BAD_ID`, `BAD_PROVIDER`, `NOT_TEXT`, `NULL_BYTE`, `OVERSIZE`, `NOT_INT`, `OUT_OF_RANGE`, `STALE`, `CHAIN`, `BAD_RECORD`.

This module still refuses to execute secret reveal, a provider change, `random` selection, OAuth refresh, network, file writes, and fallback onto another provider. It does not bench `HTTP_402` or a generic `HTTP_400`. It does not read a clock. A second confirming retry is not attempted.

Hot path: one pass over at most the policy cap. Cooling ids are skipped and later healthy ids are kept. `fill_first` takes the earliest healthy id. `round_robin` resumes after the cursor and skips cooling ids with a set membership test. `least_used` keeps the lowest count and breaks ties toward the earlier index. Status codes use a set. One sha256 links each committed selection or report.
