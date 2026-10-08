# web_search

Hermes web search returns ranked hits for one query string. Hermes web extract reads page text for URLs the caller already has. Backend choice, including the keyless provider ring, stays outside this module. A query is text. A hit is an http or https URL, a title, and a snippet. Repeat calls with the same credential id, rail, and applied limit share a cache key. Case and extra whitespace do not change that key. This module does not serve a cache and does not fetch.

The live seam is `cosmos/cosmos_dom.py`. That module owns the DOM worker: one attempt, a ledger row, and typed failures, with no silent fallback to an API. `cosmos/cosmos_firecrawl_rail.py` remains an overflow papers satellite. This proposal does not call it.

`query(text, cred_id)` bounds the text at 400 characters, requires a credential id, and returns a frozen `QueryPlan`. The default rail is `dom`. `firecrawl` is the other allowed rail. The plan holds normalized text, at most 16 terms, a hash chain (`bind`, then `search`), the policy result limit of 8, and a digest. A caller who passes a limit above 8 is ignored. The stored limit is 8 and `clamped` is true. An empty query is `EMPTY_QUERY`. A missing credential id is `NO_CRED`. `confirm_retry` adds one `retry` step only for `RATE_LIMIT`. A second retry is `RETRY_CAP`. `accept` returns the plan only when the fence matches. `emit` writes the plan as records. `rebuild` from those records reproduces the plan. A broken link is `CHAIN`. A bad digest is `BAD_DIGEST`.

`ingest(rows)` checks every supplied row and keeps at most eight `SearchHit` values inside a snippet budget of 2000 characters. A valid hit that does not fit the remaining budget is skipped and counted in `dropped`. Later hits that fit are kept. A malformed row refuses, including a row past the count cap. Titles cap at 200 characters. Snippets cap at 500. URLs cap at 2000 characters and use the http or https scheme. Loopback, link-local, private, multicast, reserved, single-label, and `.local` hosts refuse `PRIVATE_URL`.

Authority for a real navigation sits on the DOM worker ledger. `ingest` is a projection of rows the caller already holds. This module writes no file and opens no socket. A human or the harness decides whether a plan becomes a DOM attempt.

## Ship

- operations: `CRED_CAP`, `PAYLOAD_CAP`, `QUERY_CAP`, `RAIL`, `RAILS`, `RESULT_CAP`, `RETRY_CLASS`, `ROW_CAP`, `SCHEMA`, `SNIPPET_CAP`, `TERM_CAP`, `TERM_LEN`, `TITLE_CAP`, `URL_CAP`, `IngestResult`, `PlanStep`, `QueryPlan`, `SearchHit`, `Term`, `accept`, `confirm_retry`, `emit`, `ingest`, `query`, `rebuild`
- refusal codes: `BAD_BUDGET`, `BAD_COUNT`, `BAD_CRED`, `BAD_DIGEST`, `BAD_FENCE`, `BAD_LIMIT`, `BAD_PLAN`, `BAD_RAIL`, `BAD_RECORD`, `BAD_ROW`, `BAD_ROWS`, `BAD_SCHEMA`, `BAD_TERM`, `BAD_URL`, `CHAIN`, `DUPLICATE`, `EMPTY_QUERY`, `NO_CRED`, `NO_RETRY`, `NOT_BOOL`, `NOT_INT`, `NOT_TEXT`, `NULL_BYTE`, `OUT_OF_RANGE`, `OVERSIZE`, `PRIVATE_URL`, `RETRY_CAP`, `SECRET`, `STALE`, `TOO_MANY`
- what this module still refuses to execute: HTTP and DNS, the keyless provider ring, page extract and truncation to disk, cache reads and writes, any rail other than `dom` or `firecrawl`, a second retry, and a plan whose fence does not match
- hot-path shape: one pass over the rows; skip a valid hit that does not fit the remaining snippet budget; keep later hits that fit; malformed rows refuse; plan identity is one hash chain of two steps, or three after the single retry

CCr lands this by binding the harness web search tool to `query`. The tool returns the frozen plan. A later approved step passes that plan to `DomWorker.run_attempt` on `cosmos_dom`, or to the Firecrawl rail when the plan says `firecrawl`. Rows from that attempt pass through `ingest` before they enter the loop. The landing adds no HTTP client and no API key field.
