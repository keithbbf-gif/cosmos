# api_server

Hermes exposes an OpenAI-compatible HTTP surface on the gateway. Chat completions send `model` and `messages`. The gateway listens on `127.0.0.1` port 8642 unless an operator deliberately publishes another IPv4 host. `API_SERVER_KEY` is required, including on loopback. A request that starts an agent run counts against `max_concurrent_runs` (default 10). A higher number is ignored. Zero disables the limit in Hermes. This proposal refuses zero. It does not listen.

The live seam is the loopback handler. The assignment names no existing COSMOS module. This proposal is that seam. `describe_loopback` returns the route table a later listener would mount. `GET /health` and `POST /session` are descriptors. `resolve` names the matching descriptor. Nothing is accepted from the network.

## Operations

`parse_chat(body)` requires a string `model` and a list of messages. A blank model, an empty message list, a message that is not a dict with string `role` and string `content`, a role outside `system`, `user`, `assistant`, and `tool`, and a non-bool `stream` are `BAD_BODY`. Missing `stream` means not streaming. One walk reads every string key and string value. Each string is bounded at 256000 characters and checked for a secret shape once. The sum of those lengths is capped at 256000. Nesting deeper than 32 is `BAD_BODY`. `requested_cap` above 10 is ignored and 10 is recorded. A lower positive cap is recorded as asked.

`check_bind(host, public_grant)` allows the exact host `127.0.0.1`. Any other host raises `PUBLIC_BIND` unless `public_grant` is `True` and the host is a dotted IPv4 address. A blank host stays `PUBLIC_BIND` even with a grant. `localhost`, `::1`, and any other non-IPv4 text raise `BAD_HOST` when a grant is present. The return value is a descriptor. The function does not listen.

`check_bearer(presented, expected)` compares the two strings with `const_eq`. An empty or whitespace-only `expected` raises `NO_BEARER`. A mismatch raises `BAD_BEARER`. The matched id is not stored.

`describe_loopback(host, bearer_id)` refuses any host other than `127.0.0.1` with `NOT_LOOPBACK`, including when `public_grant` is `True`. A missing bearer id raises `NO_BEARER`. The grant flag does not publish the table: `public_grant` is recorded false. `listens` is false. Every route `kind` is `descriptor` and `executes` is false. The default port is 8642. The default fence is 0. `resolve` must repeat that fence. A different fence is `STALE`. A missing fence is `STALE`. Routes come from a fixed catalog. A caller cannot add a route. Duplicate ids are `DUPLICATE`. An empty selection is `EMPTY_ROUTES`. `text_budget` above the policy sum is ignored and the policy sum is recorded. The selection walk skips a route whose cost does not fit in the remaining budget and keeps a later route that does. If none fit, the call raises `EMPTY_ROUTES`.

`resolve(table, target, presented, fence=...)` splits one request line on a single space. A different shape is `BAD_TARGET`. `GET /health` needs no presented id. `POST /session` and every other bearer route refuse a missing id with `NO_BEARER`. A mismatch is `BAD_BEARER`. The result is a descriptor. It does not start a run.

`rebuild(table)` builds the table again from the host, bearer id, port, caps, fence, and route records. The same public state comes back, including the chain. A chain that does not match those records is `BROKEN_CHAIN`.

## Authority

A human holds the public-bind grant and the bearer credential id. This module does not decide to publish, does not append a ledger, and does not store a presented token. The route table records the bearer id so a later service can resolve it. The chat descriptor and the route resolution are what that service would run. They are not turn results.

## Refusal codes

`BAD_BODY`, `BAD_METHOD`, `BAD_PATH`, `BAD_TARGET`, `BAD_AUTH`, `BAD_HOST`, `BAD_GRANT`, `BAD_BEARER`, `BAD_TABLE`, `BAD_LIMIT`, `OVERSIZE`, `EMPTY_ROUTES`, `UNKNOWN_ROUTE`, `DUPLICATE`, `NOT_LOOPBACK`, `PUBLIC_BIND`, `NO_BEARER`, `NOT_TEXT`, `NOT_INT`, `NOT_BOOL`, `NULL_BYTE`, `OUT_OF_RANGE`, `SECRET`, `STALE`, `BROKEN_CHAIN`.

Secret-shaped text raises `SECRET` and is not kept on a record. `repr` of a successful result does not contain `sk-`, `Bearer `, or `api_key=`. There is no off switch and no retry.

## Landing

CCr can place this table in front of the gateway listener. The service resolves the bearer id, calls these functions, and only then may listen on `127.0.0.1`. A public IPv4 host remains a `check_bind` descriptor until a human passes `public_grant`. The loopback route table never takes that grant. Concurrent runs stay at the recorded cap. This module never listens and never starts a run.

## Ship

- operations: `SCHEMA`, `BODY_TEXT_CAP`, `POLICY_RUN_CAP`, `POLICY_TEXT_BUDGET`, `LOOPBACK_HOST`, `DEFAULT_PORT`, `FENCE_CAP`, `BearerCheck`, `BindCheck`, `ChatMessage`, `ChatRequest`, `Resolution`, `Route`, `RouteTable`, `parse_chat`, `check_bind`, `check_bearer`, `describe_loopback`, `resolve`, `rebuild`
- refusal codes: `BAD_BODY`, `BAD_METHOD`, `BAD_PATH`, `BAD_TARGET`, `BAD_AUTH`, `BAD_HOST`, `BAD_GRANT`, `BAD_BEARER`, `BAD_TABLE`, `BAD_LIMIT`, `OVERSIZE`, `EMPTY_ROUTES`, `UNKNOWN_ROUTE`, `DUPLICATE`, `NOT_LOOPBACK`, `PUBLIC_BIND`, `NO_BEARER`, `NOT_TEXT`, `NOT_INT`, `NOT_BOOL`, `NULL_BYTE`, `OUT_OF_RANGE`, `SECRET`, `STALE`, `BROKEN_CHAIN`
- what this module still refuses to execute: listening, binding an address, accepting a non-loopback route table, starting a chat or session run, streaming SSE, storing responses, scheduling jobs, fetching images or files, emitting CORS, and writing a ledger or a file. `GET /health` and `POST /session` stay descriptors with `executes` false and `listens` false.
- hot-path shape: one body walk that bounds and secret-checks each string once; one pass over the selected routes that skips a route whose cost does not fit and keeps a later route that does; route membership is a `frozenset` built when the table is sealed. Regexes and the catalog index are module-level.
