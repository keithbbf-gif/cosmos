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
