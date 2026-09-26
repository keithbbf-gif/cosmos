# RESESSION SOP — CCr (Keith 2026-09-10, this close)

**This is the SOP.** Do not invent a second close ritual.

Measured this close: TidyUP + TU2 + **BUcr.toml** + pointer paste into **one new
interactive** Grok Build TUI + summary + END OF SESSION. The dying TUI then
stops.

**TWO STEPS. Do not forget. Carry this scar.**

- `grok -p` / `--prompt-file` **injects** the paste into a **new** `--session-id` and **exits**. That exit is correct for step 5a.
- Leaving it there is how successor `f5132f97` vanished (inject-only, no TUI).
- Positional prompt / `cmd /k` without `-r` was **NOPE** (Keith 2026-09-10, `4ecfbb83`).
- Step 5b **must** open the **same** id: `cmd /c start "COSMOS-CCr" /D <repo> grok.exe --cwd <repo> --fullscreen -r <uuid>`. First quoted token is the **window title**. Do **not** quote `grok.exe`.

## Watermark
- **65% persistent warn** — Grok window **200k**; warn at **130000** tokens. `RESESSION_WARN.flag` never self-clears. Does not pack or spawn.
- **~70%** — pack only. TU2 snapshot, `live/state/session_saves/<stamp>/`. Do **not** close. Do **not** spawn.
- **Keith says TidyUP / resession now / write BUcr** — full SOP below.

## Full close (order is the design)

1. **TidyUP** — `py -3.14 cosmos\cosmos.py session close --root V:\A\Ai\COSMOS\live --handoff Cm`  
   HMAC `live/state/SEED.json` + `SEED.decl.json`. Archive prior seed. Never unlink. Copy `CCR.lease` into the pack, then **release** the lease.
2. **TidyUP2 (adversarial)** — not "did the files exist." Re-run occupancy + live-emit. Ask what TidyUP claimed that the disk contradicts (stale SEED inherit is the usual). Write `session_saves/<stamp>/tu2_adversarial.json`. Mitigation = **BUcr `[next]`**, not a fake-green HMAC.
3. **Write BUcr** — `V:\A\Ai\COSMOS\BUcr.toml` (CCr pointer, git-ignored). `[read_order]`, `[next]`, successor UUID, pack path. Also refresh `BUCm.toml` `[tidyup]` + `[next]` so Cm BootUP still has a pointer. Trust BUcr / BUCm `[next]` over stale SEED prose.
4. **Paste file** — rewrite `live/state/BOOTUP_PASTE.md` as **pointers only** (BUcr, SUCCESSOR_ROADMAP, pack tu2, session start, first Gitur). Not a dump. Not the 407k patent pack.
5. **Spawn ONE NEW Grok Build TUI — two steps, same UUID. Script: `work_orders/ccr/_spawn_ccr_successor.ps1`.**  
   Mint a UUID. Put it in `BUcr.toml` `successor_id`. Not `-c` of the dying window.  
   **5a inject (exits):** `grok --cwd V:\A\Ai\COSMOS --session-id <uuid> --prompt-file live\state\BOOTUP_PASTE.md --always-approve`  
   **5b TUI (same id):** `cmd /c start "COSMOS-CCr" /D V:\A\Ai\COSMOS C:\Users\Papa\.grok\bin\grok.exe --cwd V:\A\Ai\COSMOS --fullscreen -r <uuid>`  
   Skip 5a → empty TUI. Skip 5b → session dies after inject. Both, every time.
6. **Print a summary** — SEED mac/len, pack path, BUcr path, paste path, successor UUID, grok pid if known.
7. **Print exactly** (last output; no more turns):

```
--------------------------------------------------------------------------------------------------------------------------
END OF SESSION
END OF SESSION
END OF SESSION
==========================================================================================================================
```

`SESSION CLOSED` ×3 + `TEXT SAVED TO <pack>` belongs on the TidyUP pack. **END OF SESSION** is the dying TUI after the successor exists.

## New session first acts
1. Read `BUcr.toml` then `ccr/sandbox_notes/SUCCESSOR_ROADMAP.md`.
2. `py -3.14 cosmos\cosmos.py session start Cm --root V:\A\Ai\COSMOS\live`
3. Acquire `CCR.lease`. Quote inherit. Resume-gate (Resume all · pick · hold). Default MOTION.
4. Continue the work BUcr `[next]` named.

## Improper close (no SOP run)
Pull Grok log if roomy (`-c` / `-r` **that** log only). Else typed `IMPROPER_CLOSE`. Never `-c` a full window. Never inject-only (`-p` without 5b `-r`). Never TUI-only (5b without 5a).

## Measured this close (2026-09-09/10 CCr)
- Pack: `live/state/session_saves/20260909T231930`
- TU2: `.../tu2_adversarial.json`
- BUcr: `V:\A\Ai\COSMOS\BUcr.toml`
- Paste: `live/state/BOOTUP_PASTE.md` (pointers)
- Successor retry: `a8f31c04-6e2b-4d91-9c7e-2b1e0d4a7c55` (5a `--prompt-file` + 5b `-r`; script `_spawn_ccr_successor.ps1`)
- HMAC SEED len=4763 mac `be659951…`
- Occupancy 154/154. Live-emit 6/6. Lease released. 10-min race clock OFF.
