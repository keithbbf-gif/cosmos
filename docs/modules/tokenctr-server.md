# Token Center server

Direct-run report, 2026-10-08. Working directory `V:\A\Ai\COSMOS\tokenctr`. Interpreter `py -3.14`. `TEMP` and `TMP` were `C:\Users\Papa\AppData\Local\Temp\c4-token-server`. Each file was one process, not pytest. No file under `tokenctr` was edited. No commit. No `secrets.json`, `keys.db`, or key file was opened by this note. No payment or model API was called.

## Routes `make_handler` registers

`cosmos_pay_gateway.make_handler` builds one `BaseHTTPRequestHandler`. `do_GET`, `do_POST`, and `do_OPTIONS` are the only methods. Paths below are after stripping a trailing slash. Routes marked `api` exist only when `main` mounts the UI dict (`Founding`, `WebhookRouter`, optional adapters). `main` still serves chat if that mount raises.

| Asked | Method and path | Handler |
|---|---|---|
| Health | `GET /healthz` | `do_GET` returns `ok` |
| Models | `GET /v1/models`, `GET /v1/models/{id}` | bearer via `Store.account_for_key` |
| Chat | `POST /v1/chat/completions` | `PayGateway.chat`, or `PayGateway.chat_stream` when `stream` is true |
| Usage | `GET /v1/usage/today` | bearer; `Store.credits` plus `Meter.rollup_day` |
| Account | `GET /v1/account` (`api`); `POST /v1/account/create` (`api`, setup key) | `Store.create_account` on create |
| Keys | `POST /v1/keys/issue`, `/revoke`, `/rotate`, `/cap` (`api`, bearer) | `Store.issue_key`, `revoke_key`, `set_key_cap` |
| Statement | `GET /v1/statement`, `GET /v1/statement/export` (`api`, bearer) | `cosmos_pay_toll.statement_line` |
| Founding | `GET /v1/founding/status` (`api`, no bearer); `POST /v1/founding/purchase` (`api`, bearer) | `Founding.status`; checkout via `StripeAdapter.create_checkout_session` |
| Credits purchase | `POST /v1/credits/purchase` (`api`, bearer) | see below |
| Webhooks | `POST /v1/webhooks/{processor}` (`api`, raw body, no bearer) | `WebhookRouter.receive` |

Also registered, not in that list: `GET /v1/logs` and `GET /v1/logs/{event_id}`, `GET /v1/settings`, `POST /v1/settings/{key}`, `GET /v1/export`, `GET /v1/export/full`, `POST /v1/meter/ingest`, `GET /v1/cloudflare/status`, and `OPTIONS` (204, CORS). Anything else is 404 from `do_GET` or `do_POST`.

Dispatch, read after the rails pass: `main` still builds `RunPodRail` or `_UnconfiguredRail`, then calls `PayGateway(..., **attach_rails(config, secrets))`. `attach_rails` returns `vertex_rail`, `bedrock_rail`, `openrouter_rail`, and `azure_rail` from each module's `from_config`. A missing project, credential, key, or endpoint leaves that object `None`. `chat` then returns 503 `no_supply` and writes no meter event. The receipt `C:\Users\Papa\AppData\Local\Temp\c4-rails2-result.md` records dispatch pytest 8 passed. Those eight tests are not part of the 12 script wrappers below. The gateway does not import `cosmos_spend`.

## Credits purchase without a Stripe or PayPal secret

No. `POST /v1/credits/purchase` does not call `Store.grant`. `main` builds `StripeAdapter` only when `stripe_secret_key` is non-empty, and `PayPalAdapter` only when `paypal_client_id` is non-empty. `StripeAdapter.__init__` raises `ProcessorError` (`BAD_CONFIG`) on an empty secret. `PayPalAdapter.__init__` raises the same if `client_id` or `client_secret` is empty. With neither adapter, the handler sends 503 `no_processor`. PayPal is tried only when `processor` is `paypal` and `api["paypal"]` is set; otherwise it falls through to Stripe, then 503.

The grant is a later webhook. `StripeAdapter.create_checkout_session` posts to Stripe and returns `{id, url}`. `WebhookRouter.receive` refuses a missing adapter (`UNKNOWN_PROCESSOR`). `WebhookRouter._route_stripe` and `_route_paypal` call `Store.grant` only after `verify_webhook`. Stripe verify requires `webhook_secret`. That path was not called against a live processor.

## Meter and `credits_face_usd`

They do not share one transaction. `cosmos_pay_config.KEYS_DB` is `keys.db`. `METER_DB` is `meter.db`. `Store.reserve`, `Store.settle_refund_unused`, and `Store.grant` each `commit` on the store connection. `Meter.emit` `commit`s on the meter connection. `PayGateway.chat` settles, then calls `PayGateway._emit`, which swallows `MeterError`. `WebhookRouter._route_stripe` grants, then emits `CREDIT_PURCHASED`. `Founding.grant` commits the plan and face balance, then calls `Meter.emit` after releasing that work. Idempotency is a third file, `webhooks.db`, with its own commits in `WebhookRouter._claim`. No `BEGIN` spans the two balances. A meter failure does not roll the face balance back.

## Core SpendGate

Not bound. The earlier search of `V:\A\Ai\COSMOS\cosmos\*.py` found no `import cosmos_pay` and no `from cosmos_pay`. That same read of `cosmos_pay_gateway.py` showed imports of `cosmos_pay_config`, `cosmos_pay_founding`, `cosmos_pay_meter`, `cosmos_pay_processors`, `cosmos_pay_webhooks`, and `RunPodRail`, and no import of `cosmos_spend`. `Store.reserve` only says it mirrors `SpendGate`. Core `SpendGate` stays in `cosmos.cosmos_spend` and is wired from Core (`cosmos_kernel`, rails, `cosmos_spend_meter`). Those imports point at `cosmos_spend`, not this package.

The same gateway file imports `cosmos_pay_vertex_rail`, `cosmos_pay_bedrock_rail`, `cosmos_pay_openrouter_rail`, and `cosmos_pay_azure_rail`. It does not import `cosmos_spend`. The 8 dispatch tests are a rail map inside this package. They are not a SpendGate bind.

The jury record is `docs/modules/JURY_SPENDGATE.md`. Tally: BIND_NOW 1, BIND_READ_ONLY 1, DO_NOT_BIND 3. Chair: DO_NOT_BIND. That verdict still stands. Do not merge `credits_face_usd` with `meter.db`.

## HANDOFF section 3 (definition of done)

Quoted from `tokenctr/HANDOFF.md`. Every box is still empty in that file:

- [ ] All 7 test suites exit 0
- [ ] Gateway serves /healthz, /v1/models, /v1/chat/completions
- [ ] One measured `RUN_SETTLED` from the manufactured rail
- [ ] Free-tier 429 carries the Founding offer (machine-readable)
- [ ] Webhook signature verify passes on raw bytes through the real HTTP layer
- [ ] Founding cap enforced (sold-out refuses)
- [ ] Nightly job recomputes prices; the dashboard shows the new price

`README.md` says the package is complete at 190/190 checks, and that `tests/` holds 12 suites, all green. This run supports that count. It does not close section 3. The first box says 7 suites. The `RUN_SETTLED` box wants the manufactured rail. The last box wants the nightly job on a dashboard. This run measured neither.

On this later read of `tokenctr/HANDOFF.md`, those seven boxes were still empty. Section 3 stays open. The checker grade below does not check them.

## What this run supports

`tests\test_pay_runpod.py` is not in the tree, so it was not run. The other twelve scripts exited 0. Last summary line of each:

| Script | Exit | Last summary line |
|---|---|---|
| `test_pay_toll.py` | 0 | 20 pass, 0 fail |
| `test_pay_pricing.py` | 0 | 16 pass, 0 fail |
| `test_pay_meter.py` | 0 | 12 pass, 0 fail |
| `test_pay_entitlement.py` | 0 | 11 pass, 0 fail |
| `test_pay_vertex_rail.py` | 0 | 10 pass, 0 fail |
| `test_pay_founding.py` | 0 | 12 pass, 0 fail |
| `test_pay_webhooks.py` | 0 | 11 pass, 0 fail |
| `test_pay_gateway_integration.py` | 0 | 22 pass, 0 fail |
| `test_pay_cloudflare.py` | 0 | 16 pass, 0 fail |
| `test_pay_bulletproof.py` | 0 | 36 pass, 0 fail |
| `test_pay_money_safety.py` | 0 | 14 pass, 0 fail |
| `test_pay_privacy.py` | 0 | 10 pass, 0 fail |

20+16+12+11+10+12+11+22+16+36+14+10 = 190 pass, 0 fail. That is the README figure. Local checks inside those suites do cover a fake-rail `RUN_SETTLED` (`test_pay_gateway_integration.py`), a 429 `founding_offer`, an HTTP webhook verify, and `Founding.grant` refusing `SOLD_OUT`. `test_pay_pricing.py` recomputes a price in memory. None of that is a live manufactured rail or a nightly dashboard.

`test_pay_cloudflare.py` discovered a credential and called the live Cloudflare token and zone endpoints. Those checks passed on this single run. It was not a payment or model API, and it was not repeated. No key material is recorded here.

`test_pay_vertex_rail.py` only called `VertexAIRail._translate_request`, `_resolve_model_name`, and `_auth_headers` with a fixture token. It did not call Vertex.

## Checker grade (later package run)

A later package run from `tokenctr`, recorded in `C:\Users\Papa\AppData\Local\Temp\c4-rails2-result.md`, reported `ruff` 0, `mypy` 0, `pytest` 12 passed, and `compileall` 0. The 12 are the subprocess wrappers in `tests/test_suites_pytest.py`: the twelve scripts in the table above. `tests\test_pay_runpod.py` is still not in that list. None of the twelve is the dispatch file. `tests\test_tokenctr_rails.py` is the dispatch file, and that same receipt records 8 passed.

That grade is not a finished resale desk. Named rails no longer fall through to RunPod. Bedrock does not sign. A purchase with no processor is still 503 `no_processor` and does not grant credits. SpendGate is not bound (`docs/modules/JURY_SPENDGATE.md`, chair DO_NOT_BIND). `HANDOFF.md` section 3 stays open while its boxes are unchecked.
