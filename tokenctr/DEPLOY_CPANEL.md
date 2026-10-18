# TokenCenter gateway on cPanel / CloudLinux "Setup Python App" (sandbox)

Deployed 2026-10-16 (America/Chicago) on MochaHost, user `papafigc`.

| Item | Value |
|---|---|
| URL | `https://api.tokenctr.com` (Cloudflare proxied A -> 65.181.111.252, SSL full) |
| cPanel subdomain | `api.tokenctr.com`, docroot `/home/papafigc/api.tokenctr.com` (Passenger block in its `.htaccess`) |
| Python app | CloudLinux selector, Python 3.11, app root `~/tokenctr_gw`, startup `passenger_wsgi.py`, entry `application` |
| Data root | `COSMOS_PAY_ROOT=/home/papafigc/.cosmos_pay` (0700; `secrets.json`/`config.json` 0600) |
| Restart | `touch ~/tokenctr_gw/tmp/restart.txt` |
| Stripe | sandbox webhook -> `https://api.tokenctr.com/v1/webhooks/stripe` (`checkout.session.completed`, `charge.refunded`) |

## passenger_wsgi.py
The gateway is a stdlib `BaseHTTPRequestHandler`. `passenger_wsgi.py` rebuilds the raw
HTTP request from the WSGI environ and feeds it to the same handler through in-memory
streams, so every route, CORS header and the raw-bytes Stripe signature check behave the
same as under `py -3 cosmos_pay_gateway.py`. Responses are buffered (SSE arrives in one
piece) and requests are serialised per process; run ONE process.

## config.json used for sandbox
```json
{"gateway": {"host": "127.0.0.1", "port": 8787},
 "free_tier": {"daily_face_usd": 0.0, "reset_tz": "UTC"},
 "anonymous": {"enabled": true, "per_ip_daily": 3, "global_daily": 300}}
```
`free_tier.daily_face_usd` is 0 on purpose: anonymous keys cannot spend the operator's
supply until they buy credits. Raise it only with an explicit decision.

## Tests
`python3 tests/test_pay_*.py` (each file direct-run). `test_pay_cloudflare.py` needs a
Cloudflare token in the environment and fails closed without one.

## Refreshing the paid catalog (models.json)

The gateway sells exactly what is in `~/.cosmos_pay/models.json`. Each OpenRouter entry
carries split prices (`prompt_per_m_usd`, `completion_per_m_usd`, USD per 1M tokens, zero
markup); legacy entries with a single `price_per_m_usd` still work (both sides).
Billing = prompt_tokens x prompt price + completion_tokens x completion price; if OpenRouter
reports a higher actual `usage.cost` (images, web search, audio, cache writes, a price change
since the last refresh) the gateway bills that vendor cost instead, so the operator never
undercollects. The reserve uses the same split (padded input + max_tokens x completion price).

Canon: TokenCenter keeps a local copy of model data (site `data/lanes.json` + `data/models.json`)
refreshed from the hub at **mdata.mdrater.com**. Refresh flow:

1. Refresh the site's `data/` copy from the hub (as today; the hub does not yet serve
   `/data/*.json` at a stable URL - once it does, point `--base` at it directly).
2. Regenerate the registry on the server (atomic write, 0600; gateway hot-reloads on mtime):

       cp ~/.cosmos_pay/models.json ~/.cosmos_pay/models.json.$(date +%Y%m%d-%H%M%S).bak
       ~/virtualenv/tokenctr_gw/3.11/bin/python ~/tokenctr_gw/build_models_from_catalog.py \
           --base https://tokenctr.com/data --public-out ~/tokenctr.com/data/prices.json
           # or the hub URL; --dry-run to preview. --public-out refreshes the site estimator's price list.

   It takes the paid lane, joins catalog pricing, verifies every id against OpenRouter's public
   `GET https://openrouter.ai/api/v1/models` (no key), skips missing/negative/variable (-1 router)
   prices and ids not on OpenRouter, uses the live OpenRouter price where the catalog is stale
   (reported), and keeps non-OpenRouter entries already in the file.
3. Could run from cron daily; not scheduled yet.
