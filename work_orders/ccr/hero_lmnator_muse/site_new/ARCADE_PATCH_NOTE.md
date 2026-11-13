# Arcade patch note

`site/arcade.html` was not edited. `arcade_new.html` is a copy with the lobby added. Do not replace the live arcade page with this file.

## What the copy changes

- Stylesheet `lobby.css`.
- Scripts, in order: `lobby.js` (the current four-seat mount), `mock_queue.js`, `lobby-map-n.js`, `lobby_new.js` (replaces `LMN_MOUNT_LOBBY`), the `site/` packs, the `site_new` team and enhancement packs, `engines.js`, `APPLY_SETTINGS.js`, `engines-lobby-n.js`, `arcade.js`. The team packs are loaded, not edited.
- A desk, `#lobby-desk`, above the game list. The same mount is used inside a game.
- `engines-lobby-n.js` holds the original `LMN_PLAY` until a match exists, then calls it. `engines.js` is not modified. The 18 engine functions still do not read `LMN_MATCH`.
- A fetch wrapper, only while this page is under `site_new` or opened as a file, points `board.json` at `../site/board.json`. `queue.php` is left as a relative URL so a docroot copy would still post beside itself.

## Paths in this work-order tree

`arcade.html` asks for `pack-single-a.js`, `pack-single-b.js`, `pack-multi-a.js`, and `pack-multi-b.js` next to itself. In this tree those four files are `site/packs/single-a.js`, `single-b.js`, `multi-a.js`, and `multi-b.js`. The copy points at those paths. The other `pack-*.js` files are in `site/` and the copy points there.

Home, account, favicon, CSS, and the download link point at `../site/` so this folder can be opened without copying the live tree.

## What a player can do here

- Pick 2 to 8 seats, people only, AI only, or people then AI.
- Set easy, medium, or hard for the table or for one seat. On a four-seat two-team table the default is the current Librarian / Sprinter / Novelist mix.
- Join a queue, open a lobby code, or join a code.
- On the local mock, seat one extra practice human in this same page, or advance the fill clock. Those two buttons are hidden when the transport is not the mock.
- The game board on this copy stays hidden until that match comes back. The live arcade does not wait.
- `?demo=1` on a game hash joins an AI-only table in the local mock as soon as the lobby is ready. It is a local check, not a call to the live queue.

## What this page does not do

- It does not upload, publish, or change `queue.php`.
- It does not put two browsers in one match. That waits on the API in `LOBBY_API_DESIGN.md`.
- It does not make the 18 engines simulate the other seats. `higher`, `tiles`, and `derby` remain the pages that read seat roles, and they still only know `you`, `teammate`, `enemy`, and `enemy2`.
