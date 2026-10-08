# session_search

Hermes `session_search` reads past conversations from a SQLite FTS5 index over real messages. Keyword queries are an implicit AND. The tool returns stored messages, not a model summary. Hermes also accepts FTS operators such as quoted phrases and a trailing `*`. This proposal does not interpret those operators.

The live seam is `cosmos/cosmos_recall.py`. That module already projects ledger turns into an owner-scoped recall index. A missing index is `UNMEASURED`. A principal whose id starts with `captain:` may see every owner. This proposal keeps that seam and does not open SQLite.

## Operations

`rebuild(turns)` replaces the projection from caller-supplied turns. Each turn has an owner, a session name, a seq, and text. Text is stored only after `redact`. Word tokens and their counts are computed once at rebuild. A failed rebuild leaves the previous projection in place. Rebuilding from `records()` reproduces the same digest and the same search result.

`search(principal, query)` splits the query into words. A turn is kept only when every word is present, compared by casefold. Weight is the sum of stored counts for those words. Higher weight ranks first, then fewer tokens, then the earlier rebuild ordinal. Hits follow that total order, not insertion order. A foreign owner is omitted. A principal that starts with `captain:` sees every owner. The result limit defaults to 10. A requested limit above 50 is ignored. The result records the policy cap of 50 and the page token budget of 8192. A row that does not fit the remaining token budget is skipped. Later rows that fit are still taken.

`clear()` drops the projection. The next search is `UNMEASURED` again. An empty rebuild is measured and may return no hits.

`stat_index(root, name)` checks one jailed path. A missing file is `UNMEASURED`. An existing file is `FOREIGN_INDEX`. The call does not create a database, a WAL file, a SHM file, or a directory.

## Authority

The ledger remains the authority for transcripts. This module is a memory projection only. It does not write a database, a session file, or the ledger. It does not authenticate the caller. Passing a `captain:` principal is a decision made before the call.

## Refusal codes

`UNMEASURED`, `BAD_QUERY`, `BAD_TURN`, `BAD_PRINCIPAL`, `SECRET`, `NOT_TEXT`, `NULL_BYTE`, `OVERSIZE`, `NOT_INT`, `OUT_OF_RANGE`, `DUPLICATE`, `SESSION_OWNER`, `OVER_COUNT`, `BAD_PATH`, `NO_GRANT`, `RELATIVE_GRANT`, `DRIVE_ROOT`, `DRIVE_RELATIVE`, `UNC`, `FILE_URL`, `ENCODED_DOTDOT`, `DOTDOT`, `ALT_STREAM`, `TRAILING_DOT`, `FOREIGN_INDEX`.

A query that contains `*`, a quote, no words, or more than 16 words is `BAD_QUERY`. Secret-shaped owner, session, principal, query, or path text is `SECRET`. Secret-shaped message text is not refused. It is stored only in redacted form. The same session and seq twice is `DUPLICATE`. The same session name under two owners is `SESSION_OWNER`. More than 4096 turns is `OVER_COUNT`.

## Landing

CCr can keep `cosmos_recall.py` as the owner of recall and feed this projection from the same caller-supplied turn records the ledger already holds. The pure-Python index stays disposable: delete it, call `rebuild`, and search matches the turns again. SQLite FTS may remain an optional acceleration later. It must not become a second authority, and a missing index must stay `UNMEASURED` rather than an empty success. A read must not create the index file.

## Ship

- operations: `SCHEMA`, `POLICY_CAP`, `DEFAULT_LIMIT`, `INDEX_CAP`, `PAGE_TOKENS`, `MAX_TERMS`, `Turn`, `Hit`, `IndexState`, `SearchResult`, `SessionSearch`, `rebuild`, `search`, `clear`, `records`, `stat_index`. `SessionSearch` exposes `rebuild`, `search`, `clear`, and `records`.
- refusal codes: `UNMEASURED`, `BAD_QUERY`, `BAD_TURN`, `BAD_PRINCIPAL`, `SECRET`, `NOT_TEXT`, `NULL_BYTE`, `OVERSIZE`, `NOT_INT`, `OUT_OF_RANGE`, `DUPLICATE`, `SESSION_OWNER`, `OVER_COUNT`, `BAD_PATH`, `NO_GRANT`, `RELATIVE_GRANT`, `DRIVE_ROOT`, `DRIVE_RELATIVE`, `UNC`, `FILE_URL`, `ENCODED_DOTDOT`, `DOTDOT`, `ALT_STREAM`, `TRAILING_DOT`, `FOREIGN_INDEX`
- what this module still refuses to execute: it does not open SQLite, create a database, WAL, or SHM file, mkdir on read, interpret FTS operators, stem words, authenticate a `captain:` principal, write the ledger, fetch sessions from disk or the network, or summarize with a model. There is no retry loop.
- hot-path shape: one pass over stored token counts with dict membership per query word, a total order by weight then fewer tokens then earlier ordinal, then a page fill that skips a row too large for the remaining token budget and still takes later rows that fit.
