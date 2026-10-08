# tool_gateway

Hermes routes four managed tools through one Nous subscription: web search and extract, image generation, text-to-speech, and cloud browser (`browser_navigate`, `browser_click`, `browser_type`, `browser_vision`). Enablement is per tool. A tool the caller never enables stays off, including when some other credential id exists. An empty allow enables nothing. The gateway does not fetch, speak, draw, launch a browser, or start a shell. This module records the route and returns a call descriptor. It does not open a socket.

The live seam is new. `cosmos/cosmos_tools.py` (`ToolContracts`) records declarations and dispositions. It does not bind a subscription credential to web, image, tts, or browser. `cosmos/cosmos_spend.py` prices a call after a route exists. This proposal does not import either module.

`vision` is not a fifth subscription. It is the browser vision call, and enabling `vision` fills the browser credential slot. `terminal` and `modal` are outside this bundle. A missing id on either name is `NO_CRED`. An id that is present is `NOT_GATEWAY`.

The stored selection is the route. `nous` is the gateway. A direct provider (`firecrawl`, `fal`, `openai`, and the other catalog names) stays direct and does not fall back to nous when the id is missing. A tool pinned to another backend is not overwritten by `admit`. A decline sticks until `clear_decline` or a later `select`. Env-only configuration is offered unchecked and does not enable the tool. Legacy `use_gateway: true` reads as `nous`. `false` is `LEGACY` and does not turn a tool off.

The image model is pinned once. A per-call model raises `OVERRIDE`. The free pool cannot fund a Krea id. A call with no entitlement is `NO_ENTITLE`.

## Operations

`TOOLS` is exactly `web`, `image`, `tts`, `browser`. `enable(name, cred_id)` turns that one name on and returns a `Route`. `admit(allow, creds)` turns on every name in the allow list. Each name needs its own credential-id entry. The same id string may be repeated. A missing entry raises `NO_CRED` and enables nothing. An empty allow raises `EMPTY_ALLOW` and does not clear tools that were already on. `plan` returns only nous-enabled names, in catalog order.

`call` and `dispatch` return descriptors. They do not execute. `dispatch` is one pass: an argument that does not fit the remaining budget is skipped, and a later argument that fits is kept. `retry` confirms one `RATE_LIMIT` failure and then stops. `snapshot` and `rebuild` reproduce the same public state. `load` returns a gateway with that snapshot.

`CRED_CAP` is 64. A constructor `cred_cap` above 64 is ignored. `cap_note` records the policy cap and `clamped=True`. A lower positive cap is kept. The stored id is never longer than the applied cap. `BATCH_BUDGET` is 1024 and is clamped the same way. `CALL_CAP` is 8.

An unknown name raises `BAD_TOOL`. An empty `cred_id`, including whitespace and `None`, raises `NO_CRED`. On `enable`, that one tool is left off. `secret_shape` raises `SECRET` and does not change the plan. `repr` of `Route`, `Snapshot`, and `ToolGateway` omits credential ids.

## Authority

The human enablement call is the authority. A credential id is a handle, not a key, and this module does not check it against a portal. The plan and the call chain are descriptors. Spend, ledger rows, and tool execution stay outside this package. A checklist row is not an enablement. Nobody answering an entitlement prompt is a deny.

## Refusal codes

`BAD_ARG`, `BAD_CALL`, `BAD_CAP`, `BAD_CRED`, `BAD_FAILURE`, `BAD_KIND`, `BAD_LIMIT`, `BAD_MODEL`, `BAD_OP`, `BAD_PROVIDER`, `BAD_SNAPSHOT`, `BAD_STATE`, `BAD_TOOL`, `BAD_URL`, `BROKEN_CHAIN`, `CALL_CAP`, `DECLINED`, `DIRECT`, `DUPLICATE`, `EMPTY`, `EMPTY_ALLOW`, `LEGACY`, `NO_CRED`, `NO_ENTITLE`, `NO_RETRY`, `NOT_BOOL`, `NOT_GATEWAY`, `NOT_INT`, `NOT_LIST`, `NOT_MAP`, `NOT_TEXT`, `NULL_BYTE`, `OFF`, `OUT_OF_RANGE`, `OVERSIZE`, `OVERRIDE`, `PINNED`, `POOL`, `RETRY_CAP`, `SECRET`, `STALE`.

`NOT_TEXT`, `NULL_BYTE`, and the absolute text ceiling come from `bound_text`. `NOT_INT` and `OUT_OF_RANGE` on a timestamp come from `bound_int`. A credential id longer than the applied cap is `OVERSIZE`.

## Landing

CCr would call `plan` before a turn offers web, image, tts, or browser through the managed gateway, and would pass only those names plus the matching `call` descriptors forward. `ToolContracts` stays the declaration registry. `SpendGate` stays the spender. An empty credential stays `NO_CRED` and that name stays out of the plan. The landing adds no HTTP client, no shell, and no raw key field.

## Ship

- operations: `ARG_CAP`, `BATCH_BUDGET`, `CALL_CAP`, `CRED_CAP`, `DEFAULT_MODEL`, `GENESIS`, `IMAGE_MODELS`, `LIST_CAP`, `MODEL_CAP`, `NAME_CAP`, `OPS`, `PROVIDERS`, `RETRY_CLASS`, `SCHEMA`, `TOOLS`, `Batch`, `Call`, `CapNote`, `Offer`, `Route`, `Snapshot`, `ToolGateway`, `rebuild`. Methods: `entitle`, `enable`, `admit`, `decline`, `clear_decline`, `select`, `legacy`, `note_env`, `pin_model`, `plan`, `offers`, `call`, `dispatch`, `retry`, `snapshot`, `load`, `cap_note`.
- refusal codes: `BAD_ARG`, `BAD_CALL`, `BAD_CAP`, `BAD_CRED`, `BAD_FAILURE`, `BAD_KIND`, `BAD_LIMIT`, `BAD_MODEL`, `BAD_OP`, `BAD_PROVIDER`, `BAD_SNAPSHOT`, `BAD_STATE`, `BAD_TOOL`, `BAD_URL`, `BROKEN_CHAIN`, `CALL_CAP`, `DECLINED`, `DIRECT`, `DUPLICATE`, `EMPTY`, `EMPTY_ALLOW`, `LEGACY`, `NO_CRED`, `NO_ENTITLE`, `NO_RETRY`, `NOT_BOOL`, `NOT_GATEWAY`, `NOT_INT`, `NOT_LIST`, `NOT_MAP`, `NOT_TEXT`, `NULL_BYTE`, `OFF`, `OUT_OF_RANGE`, `OVERSIZE`, `OVERRIDE`, `PINNED`, `POOL`, `RETRY_CAP`, `SECRET`, `STALE`.
- what this module still refuses to execute: network fetches, image bytes, audio, a browser launch, a shell, terminal and modal sessions, a per-call model override, a silent fallback from a direct provider onto nous, a second retry, and any tool whose credential id is missing.
- hot-path shape: one pass over the allow list with set lookups; `plan` and `offers` are one pass over the four-name catalog; `dispatch` is one pass that skips an argument which does not fit the remaining budget and still takes a later argument that fits. Each call hashes once onto the previous digest.
