# Chess model proxy

This page does not call this API. Nothing in `site_new/chess` stores or sends a key. A future server would own the keys and the browser would only send a position.

## Request

`POST /v1/chess/move`

JSON body:

- `model_id` string. Must be a key in `tokenctr/mdata/src/seats.json`. Labels with no seats.json id have no route. `gf38` / Gemini 3.8 Flash is rejected until Keith re-enables it, and then only through the Joanna Vertex account.
- `fen` string.
- `pgn` string. May be empty.
- `legal_moves` array of UCI strings produced by the client rules engine.

## Response

- `uci` string. The server must reject a value that is not in `legal_moves`.
- `legal` true when `uci` is in that list.

The server may ask the model again once after an illegal reply. It records `illegal_attempts`. It does not store the prompt body or the model reply body. Benchmark rows keep counts only: legal-move rate, illegal attempts, result, latency, token counts.

## What runs instead

`mock_opponent.js` `choose(model, chess)` picks one move from `legalMoves()` with a local material heuristic plus a tie-break from the label. `illegal_attempts` is 0 because the chooser never leaves that list. `tokens_in` and `tokens_out` stay null. The row is labelled `mock`.
