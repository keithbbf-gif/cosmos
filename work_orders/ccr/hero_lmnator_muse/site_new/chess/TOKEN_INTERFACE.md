# Token interface

Chess bets are play-money on this browser. They do not touch a real balance, a card, or a live endpoint.

## What buy.js does, and what chess does not

`site/buy.js` (read, not used here) sets `API` to `https://api.tokenctr.com`. It posts to `/v1/account/anonymous` and `/v1/credits/purchase`. When a key is already in the browser it sends `Authorization: Bearer`. The game-token purse key in that file is `lmnator-game-tokens`.

Chess does not read `lmnator-tc-key` or `lmnator-game-tokens`. It does not call `api.tokenctr.com`. Mock purses for You, Ada, and Bo live in `localStorage` under `lmn-chess-mock-balances-v1`.

## House cut

The only default is `houseCutRate: 0.05` in `config.js`. `bets.js` reads `book.houseCutRate`. It does not contain `0.05`.

`house = Math.round(stakes * houseCutRate)`, then `pool = stakes - house`. A test with rate `0.1` is in `test_bets.js`.

## Lifecycle

1. Open. `placeBet` and `cancelBet` work. Cancelling returns that stake to the mock purse.
2. Lock when the agent match starts. Further bets throw `window-closed`.
3. Settle on a result.
   - `white` or `black`: winners split the pool in stake order. The last winner gets the remainder so the shares add up to the pool. Losers get 0.
   - If nobody bet the winner: full stake refund, house 0 (`noWinnerPolicy: "full-stake"`).
   - `draw`: full stake refund, house 0 (`refundOnDraw: "full-stake"`).
   - `abort`, including abort from the open window: full stake refund, house 0 (`refundOnAbort: "full-stake"`).

Only `full-stake` is implemented. Another policy string throws.

The house figure is shown on the page and is not credited to any purse.

## Unwired calls

A later adapter could look like this. This build does not define these against a network:

- `hold({ name, amount, matchId })` while the window is open
- `release(holdId)` on cancel, draw, abort, or no winning bets
- `payout(holdId, amount)` on a decisive settle
- `houseCutRate()` returns the config number

Connecting any of that to `api.tokenctr.com`, to checkout, or to cash-out is out of scope. Betting real tokens on a winner may be regulated as gambling depending on how tokens are bought or cashed out. It needs Keith's OK and a legal check before it goes live.
