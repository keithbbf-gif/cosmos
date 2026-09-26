# CSnS — COSMOS Safety n Security

**For the next orch and CCr.** Keith 2026-09-18: mix and match; not install this FIFO. Desktop copy for Keith.

Even if the **fence is solid**, the **house must stay neat** or the whole thing burns. CSnS is the fence (hard-coded, non-AI). Neat house is P10, FIFO Gitur→LiT, occupancy, WRAP, no corpse WOs, one head. **Both.** Swiss cheese: human hole × AI hole aligned = Aug 24 05:45 and 37-vs-189. A third layer with **different porosity** (OS/IAM/VM) is the 10–100× — if it actually ships.

**AI protecting humans from humans is aspirational.** Executable = the write principal is not the daily user and not the model.

---

## Intent

The copy you cannot afford to lose is not writable by a hurried human or an agent. Git is a **spare of pushed commits**, not a fuse, not `live/`. Analog AI mouth never hits the vault without a **non-AI ADC**.

Default WRAP question (already in chairs): **What is the intent, and the best execution of this intent?**

---

## Idea 1 — EE devices (canon: `CANON_FUSES.md`)

| Device | COSMOS |
|---|---|
| Fuse | Spend/day cap. Human resets. |
| Breaker | `warn3` ×3 then refuse (grok.exe, concat CTX, two heads, Judge on empty WOMB). |
| Contactor | Spawn Role→Enviro applied or no call. Gitur merge energizes CAM. |
| Diode | One-way write: Gitur → CCr check → CAM → vault. |
| Bipolar | One-way write, two-way read. |
| ADC | Schema/form/occupancy/`mac_v`/JSONL score. Non-AI. |
| DAC | Ledger → cDeck/human prose. Never analog-to-disk. |

No AI in the fuse.

---

## Idea 2 — CAM (not an AI)

Windows **service** / clock. Holds the write key. **Does not lend** ACL to Grok, Cursor, or CCr-the-model. TTL, one fencing token (`highest_seen`). Stale → WARN ×3 → refuse.

Issuing a write key *to* an AI CCr fails the zombie-pen way (`716fbaea` after the pen passed). CAM **applies**; it does not rent `S:`.

cDeck can arm/disarm the daemon (human coil).

---

## Idea 3 — Two `S:` modes (installer picks one)

**A — Sandbox (lab on `S:`):** COSMOS + AIs inside `S:`. Writes **outside** `S:` only via CAM. Honest: contains **CAM-spawned children**, not Admin PowerShell / Cursor you launched. `rd /s S:` can still trash the lab; GitHub spare for commits.

**B — S:afe (golden on `S:`):** Agents **read** `S:`. Only CAM writes. `rd /s S:` Access Denied for you and Grok. Lab stays `V:\A`. Dist/run wants B.

**Best mix:** B for authority + A only for spawned kids. **Never agents and golden copy on the same writable volume.**

---

## Idea 4 — Two Windows accounts

- **Admin (human, once):** creates `S:`, installs CAM (LocalSystem / `cosmos-cam`). Password **not** in COSMOS env.
- **Daily COSMOS user (no admin):** cDeck, Grok, Cursor, python.

UAC on the **same** user is a speed bump (AI can open the prompt; you can click Yes). `runas` does not require logout. The fuse is **the Admin password isn’t in the agent process.**

---

## Idea 5 — Cloud / R2 diode

Elevated PowerShell is still you on NTFS. **R2 `PutObject` is not**, unless that session has CAM’s key. Golden replica: CAM-only IAM. Dev disk disposable. Uncommitted KEEP and `live/` never hit R2 unless CAM folded them. **This is the fuse that survives Admin-on-the-box.**

---

## Idea 6 — GitHub as second vault

Protect `main`: no agent PAT push; squash-only; linear history. `starting_ref: main`. LiT **is** `origin/main` (`origin/main..HEAD` = 0). CCr writes LiT **only** by merging Gitur + fast-forward pull. (`CANON_ONE_HEAD.md`)

Does **not** stop local `rd`.

---

## Idea 7 — Spawn fail-closed (`CANON_SPAWN.md`, #578)

Role → Model → Wrapper → Skills → Tools → Enviro **applied** or **no spawn**. `grok --single` → WARN ×3 → no process. CTX is a **list**. Empty Output = WOMBAT miss (state / choose / prompt / follow-up).

---

## Idea 8 — Job Object / Hyper-V kids

Job Object today: attempt cwd, pens refused (`V:\Ai`, etc.). Hyper-V VM with **no host mounts** later — closer to Qubes AppVM. Windows Sandbox = one-shot, not Core. **WSL2 + `/mnt/v` is not a sandbox.**

---

## Idea 9 — Qubes methods, not Qubes-as-host

Steal: agents never run in the vault; copy-out is narrow and non-AI; dirty work is disposable. Do **not** move Core to Qubes OS unless we abandon native Windows (schtasks, grok.exe, cDeck). A Windows HVM on Qubes still needs a vault *inside* that HVM.

---

## Idea 10 — Linux (or Hyper-V) sandbox *around* COSMOS

Outer OS enforces. Inner COSMOS can be messy. **No bind-mount of the vault.** Windows cDeck = **client** of `:8770`. Agents that need a shell live **in** the sandbox. `grok.exe` on unsafe Windows talks HTTP or doesn’t touch the vault. Split-ready monolith already allowed this split.

---

## Idea 11 — Neat house (or the fence doesn’t matter)

FIFO. One CCr. No 112× MOTIF grok clones. File corpses, don’t leave them on WOMB. Score every attempt (JSONL). Grade duplicate Gitur PRs, don’t squash-clobber. Occupancy. WRAP: intent / best execution. **Solid fence + filthy house still burns.**

---

## Idea 12 — Research (fencing)

Kleppmann: lease in the writer’s head is not enough; **storage** rejects `token < highest_seen`. GLM/Ling: branch protection, OS ACL, CI-only merge, spawn refuse without lease. COSMOS already had Arbiter tokens — they didn’t bind NTFS.

---

## Honest stacking (best mix, no pride)

| Layer | Stops |
|---|---|
| WRAP / “no pen” | Almost nothing on `rd /s` |
| `#578` warn3 + no grok spawn | Extra grok.exe workers |
| GitHub protect + one head | Second git history |
| Job Object | Spawned kids only |
| Mode B ACL | Casual `rd` on `S:` until take-ownership |
| Admin-once / daily user | Agent without Admin password |
| CAM-only R2 | Admin PowerShell on the box |
| Outer Linux/Hyper-V vault, no bind-mount | Inner wipe, including “root” in the sandbox |

**Ship order if un-tabled:** (1) one head + Gitur-only LiT (done path), (2) CAM-only cloud replica, (3) Mode B volume + two accounts, (4) sandbox kids / Hyper-V, (5) optional outer Linux vault.

---

## Pointers

`CANON_FUSES.md` `CANON_S_DRIVE.md` `CANON_WARN.md` `CANON_ONE_HEAD.md` `CANON_SPAWN.md`  
`DEFINE_CAM_SAFE.md` `SAFETY_SECURITY_PRODUCT.md` `CAM_S_DRIVE_TABLED.md` `SCARS_2026-09.md`  
`work_orders/ccr/artifacts/fuses.html`

**Tabled for install.** Next orch/CCr: this file is the menu. Mix; don’t boil the ocean in one PR.
