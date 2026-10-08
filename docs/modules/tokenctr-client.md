# Token Center client

A CLI wizard exists. cDeck is not a Token Center client. The edge worker forwards requests. It does not sell credits.

## CLI wizard

`tokenctr\cosmos_pay_wizard.py` is CLI v1. The module docstring says cDeck panels are GUI v1.1. Those panels are not in `builds\cdeck` (see below).

Providers (`--provider` and `GUIDES`): `openrouter`, `google`, `bedrock`.

- `test_openrouter` is a real HTTP GET to `https://openrouter.ai/api/v1/models` with `Authorization: Bearer`. Status 200 is verified. Any exception is not. Not executed for this note.
- `test_google` is a real HTTP POST to Generative Language `gemini-2.5-flash:generateContent`, key on the query string, small JSON body. Status 200 is verified. Not executed.
- `test_bedrock` is format-only. No SigV4 and no AWS call. It returns true only when the key starts with `AKIA`, the secret length is at least 30, and `region` is non-empty.

`run_wizard` writes the key into `secrets.json` under `COSMOS_PAY_ROOT` (default `~/.cosmos_pay`) even when the check fails, and stores that boolean as `verified` on a `{provider}-byok` row in `models.json`. The module docstring says Bedrock is saved unverified because the SigV4 call comes later. The code still sets `verified` from the format check.

Importing the wizard only loads `cosmos_pay_config` (path constants). It does not open a socket or a secret file. `load_secrets` runs inside `run_wizard`, not at import.

Interactive mode can `webbrowser.open` the provider console unless `--no-open` or the operator declines. Flags: `--provider`, `--key`, `--secret`, `--region` (default `us-east-1`).

## Edge worker

`tokenctr\cloudflare_worker_tokenctr.js` `fetch` (the file is under 200 lines). Not forwarded:

- `OPTIONS` returns 204 with CORS.
- More than 120 requests in a minute from one `CF-Connecting-IP` returns 429. The window is in memory on that colo.
- Path `/` or `/index.html` returns static HTML. The page links to `/founding`. That link is not a checkout.
- `GET /v1/models` on a cache hit returns the cached body (TTL 60s after an origin 200).

Every other path is proxied. Method, pathname, and query are copied onto `env.ORIGIN_URL`, or `http://127.0.0.1:8787` if that env var is unset. The body is forwarded except for `GET` and `HEAD`. That includes `/v1/credits/purchase`, `/v1/founding/purchase`, `/founding`, and `/v1/chat/completions`. An origin failure is 502 `bad_gateway`.

The worker does not sell credits and does not call Stripe or PayPal. `X-Cosmos-Credit-Balance` is only a CORS header name. The file header says Turnstile is enforced on sensitive routes. `fetch` never reads `CF-Turnstile-Token`. It allows that name through CORS and forwards the incoming headers.

## Cloudflare helper

`cosmos_pay_cloudflare.py` is an operator client, not a storefront. These are real HTTP when called (not called here): `verify_token` (`GET user/tokens/verify`), `get_zone_info`, DNS list/create/update/delete/upsert, and `setup_tokenctr_dns` (apex, `www`, `api`, SPF, DMARC). `verify_turnstile` POSTs to the Turnstile siteverify URL only when a secret is configured. A missing secret returns true (pass-through, not a verification). An empty token returns false. `install_secrets_to_root` writes empty placeholder strings for RunPod, Stripe, PayPal, and the Turnstile secret. `extract_client_ip` and `validate_edge_headers` only read headers.

## cDeck

Absent as a Token Center client.

Search of `builds\cdeck` for `cosmos_pay`, `tokenctr`, `BYOK`, `byok`, `credits purchase`, and `credit purchase` in `*.js`, `*.html`, `*.css`, `*.py`, `*.md`, `*.rs`, `*.toml`, `*.json`: no matches. Search of `builds\cdeck\ui\*.js` for `byok`, `BYOK`, `tokenctr`, `cosmos_pay`, and `8787`: no matches. Search of `builds\cdeck\ui\*.html` for `tokenctr`, `cosmos_pay`, `byok`, and `founding`: no matches.

`ui\header.js` `renderTokStrip` (from `renderMeters`) reads `spend.rails` already in memory. Settled dollars are the sum of numeric `settled_usd`. Token in and out stay `--`. Day and week stay `UNMEASURED`. `ui\index.html` titles that strip as token and dollar meters. The spend object is Core `GET /api/v1/spend` (`ui\app.js`), not Token Center and not port 8787.

The nearest Credits control is `ui\deck_more.html` `#panel-accounts` (`data-acc="plan"`). Its note says the page does not complete a charge. The links are `https://openrouter.ai/settings/credits`, `/activity`, and `/keys`. That is OpenRouter's site, not a BYOK panel and not Token Center.

## What a buyer can do today without a GUI

- Run `cosmos_pay_wizard.py` and paste their own OpenRouter, Google AI Studio, or Bedrock key. That is BYOK, not a credit purchase. OpenRouter and Google checks are live HTTP. Bedrock is the format check above. The wizard writes `secrets.json` and a BYOK row in `models.json`. It was not run for this note.
- `install.ps1` (not run) looks for `py` or `python`, creates `%USERPROFILE%\.cosmos_pay`, copies the listed pay modules from `-Source` or the script directory, and writes `config.json` plus a secrets template only when those files are absent. Template values are empty. The printed next steps are fill secrets, start `cosmos_pay_gateway.py`, run `cosmos_pay_smoke.py --live`, then "the app (cDeck) walks the rest." cDeck does not implement that walk.
- With the gateway process up, a credit sale is an origin HTTP route (`POST /v1/credits/purchase`, `POST /v1/founding/purchase` in `cosmos_pay_gateway.py`), not a page in this tree. Credits purchase returns a processor checkout object only when a Stripe or PayPal secret is set; otherwise it sends 503 `no_processor`. The founding handler says the webhook grants the tier, not the click. The worker will forward those paths. It will not charge a card.

No buyer GUI ships in this tree.
