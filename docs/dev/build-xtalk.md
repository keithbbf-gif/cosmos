# XTalk

XTalk is the agent stream Core already serves. The module is `cosmos/cosmos_xtalk.py`. The operator page is `builds/xtalk` (`index.html`, `xtalk.js`, `xtalk.css`). COSMOS is not finished. This page maps those two trees. It does not paste the module, and a selftest pass is not a finished console.

This is not a second ledger. Core's authority file stays `ledger/authority.jsonl`. XTalk is a separate JSONL stream with its own hash walk. It does not take `CCR.lease`. It does not inject into a harness. It does not iframe OpenWork or cDeck.

Two other surfaces call the same HTTP routes and are not a second writer: the cDeck tab (`builds/cdeck/ui/deck_xtalk.js`, panel `panel-xtalk`) and the host plugin `builds/xtalk-plugin` (tools `xtalk.get`, `xtalk.send`, `xtalk.roles`). The page does not require either one. The plugin does not store a bearer. The host supplies `COSMOS_CORE_URL` and the API token. This page does not print a token.

## Where the bytes are

`resolve_bind` picks a stream. It does not create a bind file.

| Bind | Stream | Writable from this module |
| --- | --- | --- |
| empty (local) | `<runtime root>/state/xtalk.jsonl`, roles beside it at `state/roles.json` | yes, unless config says otherwise |
| `live/config/xtalk.json` with a `stream` field | the path in that file; `roles` optional, else `state/roles.json` | only if `writable` is true (default false) |
| `openwork`, `ow`, or `workspace` | the OpenWork research file named in the module (`V:\OpenWork\XTalk\live\state\xtalk.jsonl`) | no |

The OpenWork pointer `V:\Streams\XTalk\BUxt.toml` is not this writer. GET of that bind is read-only. If that file is missing, the fold kind is `UNMEASURED`. POST never writes it.

Any non-empty `bind` on POST is `BIND_READONLY` before a line is considered. POST writes the Core-local stream only. The page's bind control is a GET query. Send does not post `bind`.

A missing local `xtalk.jsonl` is `UNMEASURED`, `n` 0, no lines. GET does not create the file and does not advance a cursor. Inbox is a peek: the same role asked twice still sees the same rows. Snapshot never mkdir for the stream. Append mkdir's the stream parent only inside `send`, and only after the fence has already chosen Transport B.

## The line

Fold schema is `cosmos-xtalk/1`. Each message object uses `cosmos-msg/1`. The on-disk line is canonical JSON: sorted keys, separators comma and colon, UTF-8, one trailing newline. `prev` is `sha256:` plus the SHA-256 of the previous record's canonical bytes. The first record's `prev` is the string `genesis`.

A record carries `seq`, `prev`, `ts` (epoch milliseconds), `transport` `B`, `reply` (null on append), and `msg`. `msg` holds schema, from, to, body (cut at 8000 characters), nonce, turn, phase, and reply_to. The roles fold returns harness, owner, alive, transport, and reason. It does not echo session ids.

`_read_records` walks every line. A blank line is skipped. A JSON `null` line is not blank. `null` parses, and it is not an object, so the reader **keeps** it. The row stays in the chain walk as `kind` `BROKE`, with a short `raw` snippet. The same keep applies to any other non-object JSON value and to a line that is not JSON. The file is not rewritten. The walker does not drop the line to make the chain look clean.

`verify_chain` is a forward walk. A `BROKE` row appends `unreadable line after seq N` and does not advance `seq` or `prev`. The result list is not "chain clean". A clean file is one line: `chain clean: <count> records, head=<sha256:...>`. A seq that is not the next integer, or a `prev` that is not the prior head, is reported on that same list. Verify does not repair the tail.

GET with `verify=1` (the page always sends it) returns that list on the snapshot. A dirty walk is still HTTP 200. The page prints the verify lines. It styles them as clean only when the first line starts with `chain clean`.

When the last row is `BROKE`, or its `seq` is not an int, snapshot `head` is `UNMEASURED`. It does not invent a `sha256:` for a tail it cannot hash. `n` still counts the broken row. The null line is in the fold.

## A broken tail refuses with CHAIN

`send` locks, re-reads, then links. The next seq and prev come from the last row. If that row is `BROKE`, or `seq` is not an int (a boolean does not count), `send` raises `XTalkError` kind **`CHAIN`**, detail `stream tail is unreadable; refusing to append`. If the last object cannot be canonicalized, the kind is also `CHAIN` (`stream tail is not canonical`). No new line is written.

The HTTP face maps that error to **400** with `{error, detail}`. It does not return 200 and it does not skip the bad tail to append after `genesis`. The null line stays. The chain stays refused until something else replaces the file. This module does not do that replacement.

Other refusals from the same function:

| Kind | When | HTTP |
| --- | --- | --- |
| `BAD_REQUEST` | Body is not a JSON object. | 400 |
| `BIND_READONLY` | POST carries `bind`, or the resolved stream is not writable. | 400 |
| `BAD_MSG` | `from`, `to`, or `body` missing after trim. | 400 |
| `BAD_ROLE` | `to` is absent, or the role row is not a non-empty object (a list or a string is not a role). Not a fake inject. | 400 |
| `NOT_COMPOSED` | Transport A and the body asks to inject (`1`, `true`, `yes`). | **501** |
| `BAD_TAIL` | GET `tail` is not an integer in `1..200`. Default is 40. The page asks for 80. | 400 |
| `BAD_BIND` | `xtalk.json` exists and is not readable JSON. | 400 |
| `LOCK` | `state/locks/stream.lock` is still held after 5 seconds. A lock older than 10 seconds is treated as stale and removed. | 400 |
| `NO_PATHS` | Local bind with no paths object. | 400 |

`NOT_COMPOSED` means inject stays in the OpenWork `cosmos_msg.py` CLI. Core does not fake it.

## DRY_RUN is a notice

The fence matches the message module's rule. Unknown is not Transport A.

| Role row | Transport |
| --- | --- |
| Missing, empty, or not an object | `unknown` → `BAD_ROLE` |
| `owner` is `server` or `none`, or `alive` is false | **A** |
| Any other live owner | **B** (detail names the live-owner fence) |

Transport B appends one line under the lock, `fsync`s, and returns `kind` `ACCEPTED`, `transport` `B`, `duplicate` false. A nonce that already appears in the last 100 lines returns `ACCEPTED` with `duplicate` true and does not append. A missing nonce is a new UUID hex. The note on a real append: the stream is the inbox; there is no harness inject.

Transport A **without** inject does not append and does not raise. `send` returns HTTP **200**, `kind` **`DRY_RUN`**, `transport` `A`, `inject` false, plus harness, owner, alive, and `to`. The note says Core would not inject and did not append. The CLI treats `DRY_RUN` as success, same bucket as `ACCEPTED`, `MEASURED`, and `UNMEASURED`. Anything else from the CLI printer exits 1.

The page treats that 200 as a **notice**, not as a failed GET. `xtalk.js` clears the error, sets the notice text `DRY_RUN A · <harness> · no inject · no append`, and polls again. The honesty label stays the GET fold (`MEASURED` or `UNMEASURED`). It does not flip the page to a transport failure because the crew role is server-owned. `inject: true` is the 501 hole above, and that one is an error on the page.

## How to run it

Core serves the page and the API on the same origin. With no `--remote`, that bind is loopback. The port on the usual serve line is 8770.

| Route | What |
| --- | --- |
| `GET /xtalk/` | `builds/xtalk/index.html` (also `/xtalk` redirects here) |
| `GET /xtalk/xtalk.js`, `GET /xtalk/xtalk.css` | The page. Allowlisted names only. |
| `GET /api/v1/xtalk` | Snapshot. Query: `role`, `tail`, `bind`, `verify`. |
| `POST /api/v1/xtalk` | `{from, to, body}` and optional `nonce`. |

The page polls every 4 seconds. Empty or unreachable reads as `UNMEASURED`. It does not iframe. If the page is not on port 8770 and the path is not under `/xtalk` or `/cdeck`, the script falls back to `http://127.0.0.1:8770`. That fallback is a loopback guess, not a second server.

The module does not boot a kernel:

```text
py -3.14 cosmos\cosmos_xtalk.py --selftest
py -3.14 cosmos\cosmos.py xtalk --selftest
py -3.14 cosmos\cosmos_xtalk.py --root <runtime root> get
py -3.14 cosmos\cosmos_xtalk.py --root <runtime root> --bind openwork verify
py -3.14 cosmos\cosmos_xtalk.py --root <runtime root> send --to <role> --from captain --body <text>
```

`--root` may also come from `XTALK_BASE` or `COSMOS_ROOT`. `send` with `--bind` still posts that bind and is `BIND_READONLY`. `inbox` peeks. `roles` is the fence projection. `verify` is the hash walk. `get` is the full fold as JSON.

`tests/test_xtalk.py` calls the module selftest and, in the HTTP test, checks `UNMEASURED` before any file exists, Transport B accept, nonce duplicate, inbox peek, `DRY_RUN` as HTTP 200, inject as HTTP 501, and `GET /xtalk/` serving the standalone page. This page does not report a pass count. Run it when you need a measurement. Do not treat a prior grade note as this run.

XTalk does not finish COSMOS. The stream can be clean and the rest of the house can still be open: spend gate, dispatch, seats, voice, and the phone client among them.
