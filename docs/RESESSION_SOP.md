# RESESSION SOP — Keith 2026-09-01 (measured this close)

**This is the SOP.** Do not invent a second close ritual. First live run: TidyUP + TU2 + BU + paste into a new Grok Code TUI + summary + END OF SESSION banner.

**Next resession (this SOP, not a redesign):** the successor COW must run **this file** at 70% (pack) and at 90% / "resession now" (full close). Do not skip TU2, do not skip writing `[next]` on BUCm, do not spawn an empty Grok then a second one, do not keep talking after the END OF SESSION block.

## Watermark
- **~70%** — pack only. TU2 snapshot, `running_session_file.toml`, `live/state/session_saves/<stamp>/`. Do **not** close. Do **not** spawn.
- **90% or Keith says "resession now"** — full SOP below.

## Full close (order is the design)

1. **TidyUP** — `py -3.14 cosmos\cosmos.py session close --root V:\A\Ai\COSMOS\live --handoff Cm`  
   HMAC `live/state/SEED.json` + `SEED.decl.json`. Archive prior seed. Never unlink.
2. **TidyUP2 (adversarial)** — not "did the files exist." Ask what TidyUP claimed that the disk contradicts. First run finding: SEED inherit can be **stale** (`this_close` / `next_stream` / `pause_next`). Record findings. Mitigation = next BU, not a fake-green.
3. **Write the next BU** — `BUCm.toml` `[tidyup]` + `[next]`. Next work is whatever Keith just named (this run: **COSMOS development**). Read-order still BUCm first. Trust `[next]` over stale SEED prose.
4. **Paste file** — rewrite `live/state/BOOTUP_PASTE.md` for **this** close (next work, pens, diet, SOP pointer, files). Paste is **read-these-files**, not "run session start in headless `-p`."
5. **Spawn ONE NEW Grok Code session** — not `-c` of the dying window, not a second empty TUI.  
   Inject paste: `grok --cwd V:\A\Ai\COSMOS --session-id <new-uuid> -p <BOOTUP_PASTE.md>`  
   Then open **that same id** via **WMI `Win32_Process.Create` of
   `cmd /c start "COSMOS-Cm" /D <repo> grok --cwd <repo> -r <uuid>`**
   so the process is not a child of this TUI's Job Object (Popen/breakaway
   was killed; first-run inject TUI vanished on later `-p`).
   Do **not** `-p` into that id while the TUI is up.
   H7: dying COW is already closed. Interactive TUI runs BootUP so the resume-gate is on screen.
6. **Print a summary** of the session: timestamps and file paths (SEED, BUCm, running toml, session_saves, new session id).
7. **Print exactly:**

```
--------------------------------------------------------------------------------------------------------------------------
END OF SESSION
END OF SESSION
END OF SESSION
==========================================================================================================================
```

`SESSION CLOSED` ×3 + `TEXT SAVED TO <pack>` still belongs on the save pack / TidyUP. The **END OF SESSION** block is the human-visible end of the dying TUI after the successor exists. **It is the last output.** No more turns after it.

Owed on the next close (do not skip): pack `running_session` + BU `[next]` into HMAC SEED facts so TU2 does not find stale inherit again. Stamp `COW_HEARTBEAT.json` on BootUP (pid, session id, context_pct).

## New session first acts
`py -3.14 cosmos\cosmos.py session start Cm --root V:\A\Ai\COSMOS\live`  
Quote inherit. Resume-gate (Resume all · pick · hold). Default MOTION. Orch diet: drop discrete jobs; do not mine.

## Improper close (no SOP run)
Pull Grok log if roomy (`-c` / `-r` **that** log only). Else promote `running_session_file.toml`, typed `IMPROPER_CLOSE`. Never `-c` a full window.

## First measured paths (2026-09-01)
- 70% pack: `live/state/session_saves/20260901T192954`
- Close pack: `live/state/session_saves/20260901T193230`
- TU2 adversarial: `.../20260901T193230/tu2_adversarial.json`
- Paste: `live/state/BOOTUP_PASTE.md`
- Successor (paste injected): `28db1228-d4ca-4364-95e9-37a3be8878a1`

## First-run calibration (Keith 2026-09-01, this dying TUI)
Pack declared **~70%**. SOP finished with this window at **a little over 75% (~377k)**. Headroom for TidyUP + TU2 + BU + paste + spawn was **~5%**. 70% pack is enough if the SOP stays a script, not more orch coding. New session looked good.
