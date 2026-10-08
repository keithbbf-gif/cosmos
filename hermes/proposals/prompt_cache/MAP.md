# prompt_cache

Hermes keeps a cached system prompt separate from ephemeral text added at call time. The cached prompt is ordered stable, then context, then volatile, so a provider can reuse one byte-identical prefix. Anthropic-style caching places cache-control markers on that prefix and on a short rolling window of recent messages. A long-lived layout holds the stable system prefix and the tool list on a longer TTL so a later session can read the same prefix. A hit requires the prefix to still match. Hermes selects a TTL tier. It does not invent a cached-token count.

The live seam is `cosmos/cosmos_openrouter_rail.py`. That module tags the first system or developer block and folds `cached_tokens` from vendor usage. Missing usage stays unmeasured. `docs/PROMPT_CACHE.md` is the P11 rule for the same seam: static prefix, volatile tail, exact bytes, no dates or request UUIDs in the prefix. This proposal is that prefix check. It does not open a socket and it does not replace the rail.

## Operations

`freeze(prefix)` stores the prefix bytes and sets `cache_id` to the sha256 hex digest of those bytes. The tail starts empty. `cached_tokens` is `None`. A requested cap above 262144 is ignored and 262144 is recorded. A lower positive cap is recorded as asked. The prefix is decoded as latin-1. An ISO date `YYYY-MM-DD` or a UUID (`8-4-4-4-12` hex) raises `VOLATILE_PREFIX`.

`append(cache, tail)` and `cache.append(tail)` concatenate tail bytes. The cache id stays the digest of the prefix. A one-byte change to the prefix is a new `freeze` and a new id. Dates and UUIDs are allowed in the tail. The tail cap is 65536 bytes and cannot be raised. Append scans the merged tail and does not hash the prefix again.

`record_hit(cache, measured)` and `cache.record_hit(measured)` store the caller-supplied cached token count. Zero is a measured miss. The count replaces any previous count. The id does not change.

`measured(cache)` and `cache.measured()` return that stored count. `None` raises `ASSUMED_HIT` and does not become zero.

`assume_hit()` and `cache.assume_hit()` always raise `ASSUMED_HIT`. A stored measurement does not make an assumption legal.

`plan(pieces, requested_cap)` freezes one cache from ordered `Piece` blocks. `kind` is `prefix` or `tail`. Prefix blocks are static-first. A prefix block after a tail block raises `BAD_ORDER`. A date, UUID, or secret in a prefix block raises even when that block would not fit. A block that is clean and does not fit the remaining prefix budget, or the remaining tail budget, is skipped. Later blocks that fit are kept. The piece-count cap is 64. A longer list raises `OVERSIZE` and is not truncated. Duplicate names raise `DUPLICATE`. The cache id is the sha256 of the kept prefix bytes only.

`rebuild(cache)` re-validates the public record and returns an equal cache. It does not invent a token count.

## Authority

The ledger is the authority for usage. This record stores a cached-token count only when the caller passes a measured integer. The module does not read a clock, price a call, or decide spend. Prefix identity is a pure function of the prefix bytes. The tail is not part of that identity.

## Refusal codes

`VOLATILE_PREFIX`, `ASSUMED_HIT`, `SECRET`, `EMPTY`, `BAD_CACHE`, `BAD_ID`, `BAD_PLAN`, `BAD_KIND`, `BAD_ORDER`, `DUPLICATE`, `NOT_BYTES`, `NOT_INT`, `BAD_LIMIT`, `OVERSIZE`, `OUT_OF_RANGE`, `NULL_BYTE`.

Secret-shaped prefix or tail text is `SECRET`, so `repr` stays free of key material. An empty prefix or an empty append is `EMPTY`. A cache id that is not the sha256 of the prefix is `BAD_ID`. A measured count below 0 or above 2000000 is `OUT_OF_RANGE` and is not clamped.

## Landing

CCr would call `freeze` or `plan` on the preload bytes before `tag_preload` marks them, and would refuse a volatile prefix instead of sending it. The routing key may still be a short affinity string, but the cache id this module records is the full sha256 of the prefix. After the rail folds usage, only that folded `cached_tokens` integer is passed to `record_hit`, and `measured` is the only read of that count. `assume_hit` stays a refusal so a seat cannot report a hit the usage fold did not measure. No second HTTP client.

## Ship

- Operations: `SCHEMA`, `PREFIX_CAP`, `TAIL_CAP`, `TOKEN_CAP`, `PIECE_CAP`, `PrefixCache`, `Piece`, `CachePlan`, `freeze`, `append`, `record_hit`, `measured`, `assume_hit`, `plan`, `rebuild`. Methods: `PrefixCache.append`, `PrefixCache.record_hit`, `PrefixCache.measured`, `PrefixCache.assume_hit`.
- Refusal codes: `VOLATILE_PREFIX`, `ASSUMED_HIT`, `SECRET`, `EMPTY`, `BAD_CACHE`, `BAD_ID`, `BAD_PLAN`, `BAD_KIND`, `BAD_ORDER`, `DUPLICATE`, `NOT_BYTES`, `NOT_INT`, `BAD_LIMIT`, `OVERSIZE`, `OUT_OF_RANGE`, `NULL_BYTE`.
- This module still refuses to execute a prompt, open a socket, tag a live vendor payload, or mint `cache_control`. It does not invent `cached_tokens`, does not treat a routing key as a hit, and does not raise the prefix cap, the tail cap, the token cap, or the piece cap. `assume_hit` returns nothing. A block past the piece cap is `OVERSIZE`, not a silent drop.
- Hot path: one pass over the blocks. A clean block that does not fit the remaining budget is skipped. Later blocks that fit are kept. A date or UUID in a prefix block refuses before that skip. The joined prefix is hashed once. Append does not hash the prefix again.
