# chatwindow

The day-one window is a static loopback page plus a one-time nonce. The long-term bearer stays in `config/api_token.txt` and never enters the document.

## What I read

- `CONTRACT.md` slot `chatwindow` and the shared laws.
- `README.md` day-one steps: loopback Core, `/dayone`, one-time nonce, httpOnly cookie, bearer shown once and then kept as an id.
- `cosmos_federation/product.py`: `ROUTE_PAGE` is `/dayone`, `ROUTE_CHAT` is `/api/v1/dayone/chat`, `NONCE_TTL_S` is 60, `DEFAULT_HOST` is `127.0.0.1`, `DEFAULT_PORT` is 8770.
- `cosmos_federation/redact.py` `const_eq`, `cosmos_federation/errors.py` `Refuse`, `cosmos_federation/bounds.py` `bound_int`.
- Live `cosmos/cosmos.py` serve path: loopback `127.0.0.1` unless `--remote`, banner names `config/api_token.txt` and `kdash/index.html`.
- Live `cosmos/cosmos_service.py`: `_load_api_token` mints `token_urlsafe(24)` only when the file is missing on loopback, refuses `TOKEN_MISSING` on a remote bind, and refuses `BLANK_TOKEN` when the file is empty. `_bearer_matches` compares an Authorization header. `_request_authed` has no cookie. The route table serves kdash, `/cdeck`, and `/api/v1/agents`. It does not serve `/dayone` and it does not set a cookie.
- Live `kdash/index.html`: a password field labeled bearer. The page script sends that value on the Authorization header from an in-memory variable.

## What is already true

Core binds loopback on port 8770 unless the operator asks for a remote bind. The page a person is told to open is kdash, which is telemetry, and that page expects the bearer to be typed in. Authentication is the bearer file, not an httpOnly session cookie. Install does not open a chat window. There is no day-one transcript route on Core today. `ROUTE_PAGE` and `ROUTE_CHAT` are proposal constants, not live routes.

## What this proposal adds

- `dayone.html` is one document. CSS and script are inlined. `page()` returns those same bytes.
- The transcript markup starts empty. The empty copy is "No messages yet." It is not an assistant sentence.
- Submit posts JSON to `ROUTE_CHAT` with `credentials: "same-origin"`. A reply object with `role`, `text`, and `usd_micros` appends one line. A body that is not that object does not invent a line.
- The script comment records the installer URL `http://127.0.0.1:8770/dayone` and that redeem sets the loopback cookie. The document does not contain a nonce, a bearer, or `sk-`.
- `issue_nonce(draw, now)` builds a frozen `Nonce` from caller bytes. `redeem` returns a frozen `Cookie` with `name`, `value_id` (sha256 prefix, not the raw nonce), `http_only=True`, and `host="127.0.0.1"`.
- `SCHEMA` is `cosmos-federation-chatwindow/1`.

`dayone.html` is the extra file beside the module and the tests.

## Refusal codes

- `REMOTE` — `remote` is not exactly false. Checked before the compare.
- `NONCE` — the presented string fails `const_eq`, the draw is not 16 bytes, or the value is not a `Nonce`.
- `NONCE_USED` — a second redeem of a nonce that already succeeded.
- `NONCE_EXPIRED` — age is below zero or greater than `NONCE_TTL_S`. Age equal to 60 still redeems.
- `BOUND` — `now` or `issued_epoch` is outside `0 .. 4102444800`, from `bound_int`.
- `COOKIE` — a cookie whose name, `http_only`, host, or id is not the loopback shape.
- `PAGE` — `dayone.html` lost the installer URL or `ROUTE_CHAT`, or picked up a secret shape, a nonce, a bearer, or `sk-`.

A failed redeem does not spend the nonce. Only a success does. Equality of `Nonce` does not read the raw code. The compare on redeem is `const_eq`.

## How CCr lands it

CCr serves this document on GET `/dayone` from loopback Core and leaves kdash as the telemetry page. The installer calls `issue_nonce` and posts the presented code to `/api/v1/dayone/setup`. CCr sets the cookie from `redeem` as HttpOnly on host `127.0.0.1`. CCr does not write `config/api_token.txt` into the HTML. POST `/api/v1/dayone/chat` accepts that cookie on loopback, runs the day-one turn, and returns one JSON object with `role`, `text`, and `usd_micros`. A remote bind still refuses this redeem. If the cookie and the bearer file disagree, the bearer file and Core's existing auth stay the authority. This cookie is only the loopback grant for the page that just opened.
