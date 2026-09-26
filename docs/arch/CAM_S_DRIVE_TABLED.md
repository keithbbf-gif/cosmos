# TABLED — CAM / S: / two Windows accounts (2026-09-18)

Keith: write it up, **table it**. Not install now. Not Gitur FIFO. Future DEV.

Swiss cheese: human mistakes × AI mistakes align. Hard-coded layer (not a prompt) is orthogonal — ~10–100× on that axis. **AI protecting humans from humans is aspirational.** Executable = the write principal isn’t the human’s daily token or the model.

## Intent

The copy you cannot afford to lose is **not writable** by a hurried human or an agent. Aug 24 05:45 `rd`-class wipe. Git is recovery for **committed** clones if `.git` or `origin` survives — not a fuse, not `live/`.

## Two installer modes (pick one)

| | **A — S: Sandbox (default if we ever ship this)** | **B — S:afe** |
|---|---|---|
| What `S:` is | Lab: COSMOS + AIs **inside** | Safe LiT: canon + ledger |
| Agents | Write on `S:` | **Read** `S:` only |
| Off-`S:` / to `S:` | Writes **outside** `S:` only via CAM | **Only CAM** writes `S:` |
| Typo `rd /s V:\` from agent | Access Denied (if Job Object actually contains that process) | N/A (agents aren’t on S:) |
| Typo `rd /s S:` | Can trash the **lab**; GitHub spare for commits | **Access Denied** (you and Grok) |
| Honest limit | Does **not** contain elevated PowerShell / Cursor you launched as Admin | Admin take-ownership can still beat NTFS; R2 IAM does not |

**Best execution if built:** **B for authority + A only for CAM-spawned sandbox kids.** Don’t advertise A as “the PC is safe.” Don’t put agents and the golden copy on the same writable volume.

## CAM (not an AI)

Hard-coded Windows **service** (clock + hooks). Holds the write key; **does not lend** `S:` R/W to Grok/Cursor/CCr-the-model. Gitur merge → you check → CAM apply. TTL, one fencing token (`highest_seen`). WARN ×3 then refuse stale token.

**Don’t** issue a write key to an AI CCr (zombie pen = `716fbaea` after pass).

## Two Windows accounts (extra layer)

- **Admin (human, once):** creates `S:`, installs CAM as LocalSystem / `cosmos-cam`. Password **not** in COSMOS env.
- **Daily COSMOS user (no admin):** cDeck, Grok, Cursor, python. Cannot take ownership / install services.
- UAC on the **same** user is a speed bump (AI can open the prompt; you can click Yes).
- `runas` does **not** require logout; the fuse is **the Admin password isn’t in the agent process**.

## Cloud / R2

Elevated PowerShell is still you on NTFS. **R2 PutObject** is not, unless that session has CAM’s key. Golden copy: CAM-only IAM. Dev disk disposable. Uncommitted KEEP and `live/` never hit R2 unless CAM folded them.

## EE (canon elsewhere, tabled here)

Fuse / breaker / contactor / diode (one-way write) / bipolar (one-way write, two-way read). Analog AI mouth → **non-AI ADC** before disk; DAC back to human. `docs/CANON_FUSES.md`.

## What already exists (not this tabled pack)

`CCR.lease` + Arbiter tokens — **did not** stop a second TUI writing files. GitHub protection — **does not** stop local `rd`. `warn3` (#578) — runner grok refuse, not `rd /s`. Job-Object pens — only **spawned** children.

## Pointers

- `docs/CANON_S_DRIVE.md` `docs/CANON_FUSES.md` `DEFINE_CAM_SAFE.md` `docs/SCARS_2026-09.md`
- Interactive: `work_orders/ccr/artifacts/fuses.html`
- Wishlist: CAM / S: two modes — **leave checked off / tabled**
- WRAP default question: “What is the intent, and the best execution of this intent?”

**Menu for next orch/CCr (all ideas, mix):** `docs/arch/CSnS.md`  
Desktop copy: `C:\Users\Papa\OneDrive\Desktop\CSnS.md`

**Not now:** VHD, `install` wizard, cDeck daemon switch, Gitur for this. FIFO Gitur pile stays Gitur. This folder is the parking bay.
