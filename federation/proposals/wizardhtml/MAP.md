# wizardhtml

## Read

- `CONTRACT.md` slot `wizardhtml` and the shared laws.
- `README.md` two-minute install: one door, one pasted key, cap at or under one dollar, chat in the same window.
- `cosmos_federation/product.py`: `ROUTE_PAGE` is `/dayone`, `ROUTE_SETUP` is `/api/v1/dayone/setup`, `ROUTE_CHAT` is `/api/v1/dayone/chat`. `DOORS` is `openrouter` and `xai`. `DEFAULT_CAP_USD_MICROS` is 250000. `MAX_CAP_USD_MICROS` is 1000000.
- Live `cosmos/cosmos.py` serve banner points at `kdash/index.html`.
- A search of live `cosmos/*.py` found no `dayone` route and no `wizard.html`.
- Live `cosmos/cosmos_service.py` `do_GET` already serves `/cdeck` and `/api/v1/agents`. It does not serve the day-one paths.
- Live `cosmos/cosmos_cred_kit.py` documents OpenRouter keys at `https://openrouter.ai/keys` and the xAI console at `https://console.x.ai`.

## Already true

- Core binds `127.0.0.1:8770` unless `--remote`. The banner opens `kdash/index.html`. That page is telemetry, not a first-run wizard.
- `GET /dayone`, `POST /api/v1/dayone/setup`, and `POST /api/v1/dayone/chat` are proposed routes. They are not in the live service module.
- Day-one doors are OpenRouter and xAI. The other vendor route stays off.
- A remote bind does not mint a token, and a remote bind without TLS is refused.
- The policy cap is one dollar. The default shown to a person is 0.25 dollars.
- Identity is a tree id the person chooses, not a drive letter and not a path.

## This proposal adds

- `wizard.html`, `wizard.css`, and `wizard.js`, served as static files. No framework and no build.
- `page_text()` returns the HTML file beside the module.
- The form collects, in order, a root label, a tree id, a display name, a door, a key, a spend cap in US dollars, and loopback or remote.
- Door values are `openrouter` and `xai` only. Help links are `https://openrouter.ai/keys` and `https://console.x.ai` only.
- Choosing remote reveals a TLS confirmation (`tls=yes`). Loopback is the default and does not ask for TLS.
- The form's action is same-origin `POST /api/v1/dayone/setup`. The script posts that same path and does not rewrite the address.
- After a successful setup response, the same document hides the wizard and shows an empty chat. The empty state has no model sentence. Sending posts JSON `{"text": ...}` to `/api/v1/dayone/chat`. A reply `{role, text, usd_micros}` appends one line.
- The key control is cleared in the submit turn, after the body is copied and before the request returns. A refused response does not echo the key.
- The script does not write `localStorage` or `sessionStorage`, does not put the key on the query string, and does not read a password manager or a browser profile.

## Refusal codes

`page_text()` raises when the HTML itself is wrong:

- `ANTHROPIC_OFF` — the document names the vendor that is off the route.
- `DOOR` — either day-one door value is missing.
- `SECRET` — the document matches a secret shape.
- `PAGE` — the setup route is missing.

The page does not replace Core. Landing still refuses:

- `DOOR` and `ANTHROPIC_OFF` for any door other than the two values on the form.
- `CAP` when the dollar amount is outside one micro-dollar through one dollar after conversion to micros.
- `REMOTE_PLAIN` when bind is `remote` and `tls` is not `yes`.
- `SCRAPE` if a later change tries to read a password manager or drive a vendor login. This page does not do that.

## How CCr lands it

Serve these three files for `GET /dayone`. Map `wizard.css` and `wizard.js` as sibling names of that document so the relative links resolve. Do not inline a model key or a bearer. `POST /api/v1/dayone/setup` reads form fields `root`, `tree_id`, `name`, `door`, `key`, `cap`, `bind`, and `tls` when the bind is remote. The script sends those fields as `application/x-www-form-urlencoded`. A no-script submit uses the form's native POST to the same action. Convert `cap` from US dollars to micros, then `check_cap`. Keep the key only long enough to store a credential id. The response sets the httpOnly loopback cookie and does not repeat the key. The chat pane then posts to `ROUTE_CHAT` with the user text only. The vendor request shape stays with the seat proposal. `kdash/index.html` stays the telemetry page.

## Files

- `MAP.md`
- `wizardhtml.py`
- `test_wizardhtml.py`
- `wizard.html`
- `wizard.css`
- `wizard.js`
