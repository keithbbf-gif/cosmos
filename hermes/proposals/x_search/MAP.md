# x_search

Hermes `x_search` is a read-only lookup of public X posts, profiles, and threads. It stays disabled until an xAI credential id is present. The live tool asks xAI to search on the server and returns a synthesized answer plus citations. It does not post, reply, like, or send a direct message. This proposal does not call xAI.

The credential seam is `cosmos/cosmos_cred_kit.py`. That module already names the `xai` source and keeps secret bytes out of GET. No COSMOS module owns an X search rail. The plan is a new seam. A later metered call stays on `cosmos/cosmos_spend.py`.

`enable(cred_id)` returns a frozen `Enabled` token whose `cap` is the text policy cap of 400. `query(text, cred_id)` with no credential id is `DISABLED` and does not read the text, the limit, or the kind. The same call with credential id `cred-x` and text `cone 6` returns a frozen `SearchPlan`. An `Enabled` token is accepted in place of the id. Empty ids are `NO_CRED`. Secret-shaped ids and a raw `Bearer` token are `SECRET`. The ids `off` and `yolo` are `BAD_CRED`. There is no `off` and no `yolo`.

The plan bounds the query at 400 characters after one whitespace collapse. The result `cap` is 10. A caller who asks for a higher result limit is ignored. The plan stores `limit` at the policy cap and `clamped` true. A lower limit is kept and `clamped` stays false. The text cap does not shrink when the result limit does. `kind` is `posts`, `profiles`, or `threads`. The default is `posts`. The plan is a hash chain of `arm` then `ask`. `confirm_retry` adds one `again` step only for `UPSTREAM`. A second retry is `RETRY_CAP`. `accept` returns the plan only when the fence matches. `emit` writes the plan as records. `rebuild` from those records reproduces the plan. A broken link is `CHAIN`. A bad digest is `BAD_DIGEST`. A duplicate step ordinal is `DUPLICATE`.

`ingest(rows)` checks every caller-supplied hit and keeps at most 10, inside a text budget of 4000 characters. A valid hit that does not fit the remaining budget or the count is skipped. Later hits that fit are kept. Rows past the count are still checked. More than 32 rows is `TOO_MANY`. A hit is an https URL on `x.com` or `twitter.com`, a handle of at most 15 characters, and text. A single leading `@` is stripped. Post identity ignores scheme case, host case, query, and fragment. A repeated post id is `DUPLICATE`. A requested limit or budget above policy is ignored, and the result records the policy cap.

The human chooses the credential id. `cosmos_cred_kit` is the later authority that resolves it. This module never sees key material. The plan is not evidence that a search ran. Ingest does not approve a search.

## Ship

- operations: `BUDGET_CAP`, `CRED_CAP`, `HANDLE_CAP`, `INGEST_CAP`, `KIND`, `KINDS`, `QUERY_CAP`, `RETRY_CLASS`, `ROW_CAP`, `SCHEMA`, `TEXT_CAP`, `URL_CAP`, `Enabled`, `Hit`, `IngestResult`, `PlanStep`, `SearchPlan`, `accept`, `confirm_retry`, `emit`, `enable`, `ingest`, `query`, `rebuild`
- refusal codes: `BAD_BUDGET`, `BAD_CAP`, `BAD_COUNT`, `BAD_CRED`, `BAD_DIGEST`, `BAD_FENCE`, `BAD_HANDLE`, `BAD_KIND`, `BAD_LIMIT`, `BAD_PLAN`, `BAD_RECORD`, `BAD_ROW`, `BAD_ROWS`, `BAD_SCHEMA`, `BAD_URL`, `CHAIN`, `DISABLED`, `DUPLICATE`, `EMPTY_QUERY`, `NO_CRED`, `NO_RETRY`, `NOT_BOOL`, `NOT_INT`, `NOT_TEXT`, `NULL_BYTE`, `OUT_OF_RANGE`, `OVERSIZE`, `RETRY_CAP`, `SECRET`, `STALE`, `TOO_MANY`
- what this module still refuses to execute: HTTP and DNS, posting, replying, liking, and direct messages, reading the query when no credential id is present, any host that is not X or Twitter, raw bearer tokens and other secret shapes, `off` and `yolo`, a second retry, any failure class other than `UPSTREAM`, and a plan whose fence does not match
- hot-path shape: one pass over the rows; a set of post-id keys; skip a valid hit that does not fit the remaining text budget or the count; keep later hits that fit; malformed rows and duplicate post ids refuse; the plan is one hash chain and the query string is hashed once

CCr would register the harness tool only after `query` accepts an id that `cosmos_cred_kit` can resolve. The tool returns the frozen plan. A later rail performs the single read and passes those rows through `ingest` before they enter the loop. The landing adds no HTTP client and no API key field. One confirming retry, for the named `UPSTREAM` failure, stays a descriptor on this plan.
