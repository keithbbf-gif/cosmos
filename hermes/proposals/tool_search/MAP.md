# tool_search

Hermes Tool Search is progressive disclosure for a large deferred catalog. MCP tools, non-core plugin tools, and any built-in named in `defer` leave the eager tool list. The model then sees three bridge tools: search, describe, and call. Hermes ranks that catalog with BM25, English stemming, and a rarest-token rule, and it may ask a connector gateway. Core tools stay loaded. Listing size picks a disclosure tier. A requested search limit is clamped by configuration.

This proposal does not stem, score BM25, describe a schema, dispatch a call, or touch the network. It ranks a caller-supplied in-memory catalog of name plus description. Exact name wins, then a name that starts with the query, then a description that contains the normalized query. Equal bands sort by name. The result holds at most 8 hits. A requested limit above 8 and at most 10000 is ignored, and the result records the policy cap. A requested limit above 10000 refuses. Each query in a batch is ranked on its own. `lookup` refuses a name that is not in the catalog.

The live seam is `cosmos/cosmos_tools.py` (`ToolContracts`). That module is the tool-contract registry: declarations, dispositions, and check results are ledger events, and current state is a projection. It does not search. This proposal is a new read beside that registry, not a second registry and not a change to `cosmos_tools`.

Operations this proposal adds:

- `ToolRecord` stores one bounded name and one bounded description.
- `freeze` validates a catalog and returns those records in input order.
- `lookup` returns the one granted record for a name, or refuses `UNKNOWN_TOOL`.
- `search` ranks one query.
- `search_many` ranks each query independently. The limit applies per query.
- `SearchResult` returns the hits, how many rows matched, the policy cap (8), the requested limit, and the applied limit.

Authority stays on the ledger. The caller builds the catalog from tools the session was already granted. Search does not declare a tool, write a ledger row, or invoke anything. A human still approves a real action through the existing contract and approval path.

Query text is bounded at 512 characters. Names are bounded at 128, descriptions at 4000, and the catalog at 4096 records. A batch holds at most 16 queries. Match text is the query with whitespace collapsed. Matching is case-sensitive. Names are ASCII identifiers. Empty and secret-shaped inputs refuse. There is no `off` switch.

Refusal codes: `BAD_BAND`, `BAD_CAP`, `BAD_CATALOG`, `BAD_HIT`, `BAD_NAME`, `BAD_ORDER`, `BAD_QUERIES`, `CATALOG_CAP`, `DUPLICATE_NAME`, `EMPTY_QUERY`, `NOT_INT`, `NOT_TEXT`, `NULL_BYTE`, `OUT_OF_RANGE`, `OVERSIZE`, `QUERY_CAP`, `SECRET_SHAPE`, `UNKNOWN_TOOL`.

CCr would land this later as a pure function the harness calls when it assembles a deferred list. The function would read granted names from the `ToolContracts` projection, rank those rows, and return hit names. Describe and call would stay on the existing tool path and the approval gate. No gateway client would be added. `lookup` is the fail-closed check before that path accepts a name.

## Ship

- Operations: `SCHEMA`, `POLICY_CAP`, `QUERY_LIMIT`, `MAX_NAME`, `MAX_DESCRIPTION`, `MAX_CATALOG`, `REQUEST_LIMIT`, `QUERY_BATCH_CAP`, `ToolRecord`, `ToolHit`, `SearchResult`, `freeze`, `lookup`, `search`, `search_many`.
- Refusal codes: `BAD_BAND`, `BAD_CAP`, `BAD_CATALOG`, `BAD_HIT`, `BAD_NAME`, `BAD_ORDER`, `BAD_QUERIES`, `CATALOG_CAP`, `DUPLICATE_NAME`, `EMPTY_QUERY`, `NOT_INT`, `NOT_TEXT`, `NULL_BYTE`, `OUT_OF_RANGE`, `OVERSIZE`, `QUERY_CAP`, `SECRET_SHAPE`, `UNKNOWN_TOOL`.
- This module still refuses to dispatch a tool, load a JSON schema, stem a word, score BM25, or call a connector gateway. It does not open a socket, write a file, spawn a thread, or read a clock. An unknown tool name refuses. An empty query refuses. A requested hit limit above 8 is ignored, and the recorded cap stays 8. A requested limit above 10000 refuses.
- Hot-path shape: one pass builds a dict keyed by tool name. Membership tests use that dict. Descriptions are whitespace-normalized once per call. A second pass scores every row (exact, then prefix, then description). The full match list is sorted by band, then name. The applied limit keeps that prefix. A non-matching row is skipped. A later exact match is not dropped because an earlier description already filled a slot.
