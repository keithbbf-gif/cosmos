# subscription_proxy

Hermes exposes a local subscription proxy so an OpenAI-compatible app can call a managed model without holding the provider key. Shipped adapters are `nous` and `xai`. The proxy ignores one client `Authorization` bearer and a later host would attach the subscription credential. A second `Authorization` header is refused. Only `/v1/chat/completions`, `/v1/completions`, `/v1/embeddings`, and `/v1/models` are forwarded. The body is passed through and is not logged. The stored log line replaces that client authorization with `[redacted-bearer]` and then runs `redact` once. A colon form `Authorization: Bearer <token>` is not used, because `redact` keeps the token after that colon. The plan names loopback `127.0.0.1` only.

## Seam

No live COSMOS module binds a subscription proxy. `cosmos_cred_kit.py` already holds credential ids. This proposal is a new seam. The known gap is a forward plan only. `forward` returns a `ForwardPlan`. `listen` and `connect` refuse. Nothing in this module binds or connects a socket.

## Operations

`forward(upstream, headers, body, allow, cap=None, host="127.0.0.1")` admits `upstream` only when it is in `allow` and the allowlist names shipped providers. An empty allowlist refuses `UNKNOWN_UPSTREAM`. An allow entry outside `nous` and `xai` refuses `BAD_ALLOW`. More than one `Authorization` header refuses `DOUBLE_AUTH`. The path header must be one of the four paths. `x-credential-id` is required and is an id, not a bearer. The body cap is 65536. A higher `cap` is ignored, `clamped` is true, and `ForwardPlan.cap` stays 65536. `host` must be `127.0.0.1`. Any other host refuses `PUBLIC_HOST`. `adapters` returns `nous` and `xai`. `snapshot` emits the plan fields. `rebuild` from that record returns the same plan. `listen` and `connect` refuse `NO_SOCKET`.

## Authority

The human supplies the allowlist and the credential id. The plan stores that id, the loopback host, and the redacted log line. It does not store the client bearer. A later host would resolve the id, send `body` to `path` on `upstream`, and keep `log_line` on the attempt. This module does not spend, does not write a ledger, does not refresh a bearer, and does not bind.

## Refusal codes

`UNKNOWN_UPSTREAM` when `upstream` is not in `allow`, including an empty allowlist. `DOUBLE_AUTH` when the `Authorization` count is greater than one. `MISSING_CRED` when `x-credential-id` is absent or empty. `BAD_CRED` when that id is not an id. `BAD_PATH` when `path` is missing, repeated, or not one of the four paths. `SECRET` when an input is secret-shaped, when a non-auth header or the body carries a secret, when client-bearer material would remain on the plan, or when a stored field embeds `api_key=`. `PUBLIC_HOST` when `host` is not `127.0.0.1`. `BAD_UPSTREAM`, `BAD_ALLOW`, `BAD_HEADER`, `BAD_HEADERS`, `DUPLICATE`, `BAD_LIMIT`, and `BAD_PLAN` for malformed records. `NO_SOCKET` from `listen` and `connect`. Kernel codes `NOT_TEXT`, `NULL_BYTE`, `OVERSIZE`, `NOT_BYTES`, and `NOT_INT` come from the bounds.

## Landing

CCr would call `forward` from a loopback host that already decided to proxy. The host resolves `credential_id` through the credential kit, sends `body` unchanged, and stores `log_line` on the attempt. The host owns the connection. This module stays a pure descriptor. An empty allowlist still refuses. A second `Authorization` header still never leaves `forward`. A cap above 65536 is still stored as 65536.

## Ship

- operations: `ALLOW_CAP`, `BODY_CAP`, `HEADER_CAP`, `LOOPBACK`, `PATHS`, `PROVIDERS`, `SCHEMA`, `VALUE_CAP`, `ForwardPlan`, `adapters`, `connect`, `forward`, `listen`, `rebuild`, `snapshot`
- refusal codes: `UNKNOWN_UPSTREAM`, `DOUBLE_AUTH`, `MISSING_CRED`, `BAD_CRED`, `BAD_PATH`, `SECRET`, `PUBLIC_HOST`, `BAD_UPSTREAM`, `BAD_ALLOW`, `BAD_HEADER`, `BAD_HEADERS`, `DUPLICATE`, `BAD_LIMIT`, `BAD_PLAN`, `NO_SOCKET`, `NOT_TEXT`, `NULL_BYTE`, `OVERSIZE`, `NOT_BYTES`, `NOT_INT`
- what this module still refuses to execute: a bind, a connect, a credential refresh, a second authorization, a non-loopback host, a body or header that embeds key material, and any cap above 65536. It does not log the body and it does not spend the subscription.
- hot-path shape: one pass over the allowlist into a set, one pass over headers, one `redact` of the marker log, one sha256 of the body. A body past the recorded cap refuses. Later headers are not dropped to make an oversized body fit.
