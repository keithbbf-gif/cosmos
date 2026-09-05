# Post-ban COSMOS rebuild — tonight (2026-09-04)

**Goal tonight is the map + the first binds.** Not Grayson live, not T7, not
OpenWork iframe, not Core taken down.

## Bound this turn

| Fact | Value |
|---|---|
| OpenWork desktop | **Installed.** `C:\Users\Papa\AppData\Local\Programs\@openworkdesktop\OpenWork.exe` |
| Version | **0.18.42** (`app-update.yml` currentVersion, written 2026-09-03) |
| GitHub | **Public:** https://github.com/different-ai/openwork (`dev` branch, MIT outside `ee/`) |
| Workspace grant | `C:\Users\Papa\OpenWork Chat` — **not** `V:\A\Ai\COSMOS` (Cowork grant trick already true) |
| Local server | `openwork-server-state.json` workspace port **57383** |
| Pane path | OpenWork **headless web / local server** into cDeck webview — not embedding Electron |
| CCr lease | `cosmos/cosmos_ccr.py` + `tests/test_ccr.py` — flag `live/state/control/CCR.lease`. **Not** taken on live tonight. **Not** wired into WD2 |

## Tonight — done vs not

**Done (this packet):** occupancy map locked; OpenWork bound; CCr lease code; product→profile→skin; Grayson=Crucible on his PC; hub=T7 or SRV1; cDeck frame (leftmost system rail / OpenWork / variable right).

**Not tonight:** cDeck webview of OpenWork; Grayson install; T7/SRV1 host; anonymizer; model picker UI; GDX SOP ingest; lifting `ANTHROPIC_OFF`; clearing HOLD (WD2 still paused until you say RESUME).

## Do not

- Clone `different-ai/openwork` into this tree.
- Grant OpenWork the COSMOS root.
- Silent-overwrite a peer from the hub.
- Invent GMesh or a Grayson/T7 address.
