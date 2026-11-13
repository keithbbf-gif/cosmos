# Lobby hook

Human vs human on one device is Hotseat in `index.html`. That path does not use the queue.

## If Team E has published the lobby

From `chess/index.html` the page inserts `../lobby_new.js` (that is `site_new/lobby_new.js`).

On load, if `window.LMN_MOUNT_LOBBY` is a function, the page calls it with the element `#lobby`. That element has `data-game="t904"`.

`site/lobby.js` posts to a relative `queue.php` and expects `op` of `join`, `poll`, `move`, or `leave`. A chess page living in `site_new/chess/` would resolve `queue.php` to `site_new/chess/queue.php`, which is not the live script. Team E's mount has the same relative URL. A real lobby page has to be served next to `queue.php`, or the lobby script has to take a base URL. This page does not add that base.

## What the live queue accepts

`site/queue.php` allows `higher`, `tiles`, `derby`, and a game id matching `^[sm][0-9]{2}$`. `t904` does not match. A join for Lobby Chess is rejected with `{"error":"mode"}` until that allow-list changes. This folder does not edit `queue.php`.

## Contract for a later lobby script

- Set `window.LMN_MOUNT_LOBBY` to `function (root) { ... }`.
- Read `root.getAttribute("data-game")`. For this page that is `t904`.
- Do not replace `window.LMN_PACK`.
- `app.js` sets `window.LMN_CHESS_LOBBY_START`. Calling it with `{ white: "human", black: "human" }` starts hotseat on this page and returns true. Any other spec returns false. It does not seat a remote human. Remote seating still needs the queue.

Headless Chrome on 2026-10-28 loaded `http://127.0.0.1:8891/chess/index.html` with `site_new` as the server root. `../lobby_new.js` loaded. The DOM said `LMN_MOUNT_LOBBY` was called on `#lobby`, and `#lobby` contained Team E's lobby markup for `t904`. Hotseat is still the path that plays chess on this page. The mounted lobby does not, by itself, start a chess game or pass `t904` through the live `queue.php` allow-list.
