# COSMOS as a Safety & Security product — review (2026-09-18)

Keith: deeper dive; this takes COSMOS to another level. Tabled for *install*; this is the product review. Installer still not this FIFO.

## What “lead” would actually mean

Most AI coding stacks sell **permission theater**: the model asks, the human clicks Allow, the process is still **the same Windows user**. Cursor, Copilot, Claude Code, many “agent sandboxes” are analog WRAP around a fully armed principal. OpenHands-class Docker “cannot see the host” is real — for **children the harness spawned**, not for the TUI you opened.

COSMOS already ratified (2026-08-23) **leases + fencing tokens + fenced commit gateway** on the **ledger**. The Aug 24 05:45 scar and the 37-vs-189 two-head scar were **not ledger**. They were **NTFS + git working tree + same user + a second TUI**. The product gap is: **make the resource refuse the write** when the agent (or the tired human) is analog.

If that ships — **CAM (not an AI) holds the write principal; `S:` / R2 IAM reject everyone else; spawn Role→Enviro fail-closed; WARN ×3; Gitur→CCr→CAM diode** — then yes, that is **ahead of the agent-IDE pack** on Windows, because almost nobody sells a **non-AI breaker in the write path** as the product. Qubes/Whonix are stronger isolation and **not** an AI-mesh OS. Don’t claim Qubes. Claim: **agent runtime whose golden copy is not writable by the model or by a normal shell.**

**Lead is conditional on shipping B + CAM-only replica + Admin-once vs daily user.** WRAP PDFs and `fuses.html` are not the product.

## Threats (assume mistakes)

| Threat | Analog (fails) | Digital breaker (holds if built) |
|---|---|---|
| Agent `search_replace` on LiT after pen passed | “You don’t have the pen” | ACL: process cannot write `S:` |
| `rd /s` / `Remove-Item -Recurse` | WRAP, lease file, GitHub | Mode B Access Denied; R2 PutObject without CAM key |
| Elevated PowerShell (same user) | UAC click | **Does not hold** on NTFS if Admin. **Holds on R2** if key isn’t in that session |
| `git reset --hard` | Human will run it | Recovery if `origin` has the commits; not a fuse |
| Two git heads | Social FIFO | `origin/main..HEAD` = 0 gate + GitHub protect `main` + `starting_ref: main` |
| Zombie TUI (lease expired, still writing) | Lease in the agent’s head | Fence on **CAM / GitHub / S:** `token < highest_seen` → refuse |
| 112× `grok --single` | Prompt | Runner `warn3` ×3 then no spawn (#578) |
| Sandbox typo against `V:\` | Hope Job Object | Only if **that process** was spawned into the Job with pens. Cursor you launched by hand is not |

## Modes (installer, one of two)

**A Sandbox:** COSMOS+AIs on `S:`; off-`S:` only via daemon. Honest: contains **CAM-spawned kids**, not Admin you.  
**B S:afe:** `S:` = golden LiT; agents Read; only CAM writes. **This is the Safety product.** Dist/run wants B.

**Best execution:** B for authority + A for sandbox children. Never same writable volume for agents and the copy you cannot lose. Cloud: CAM-only R2 either way.

**Accounts:** Admin-once installs CAM. Daily COSMOS user is not Admin. Password not in `live/config/`. UAC-on-same-user is a bump; two accounts is a fuse.

## What is already COSMOS (don’t rebuild)

Fenced commit, Arbiter tokens, Job-Object sandbox, spend fuse, `warn3`, spawn spec (propose), one-head canon, Gitur FIFO. **Productize the missing OS diode** so those kernel ideas actually bind NTFS and object storage.

## What not to claim

- “AI will stop you” — aspirational.  
- “Git protects the tree” — spare of **pushed** commits.  
- “We’re Qubes.”  
- USPTO from this TUI.

## Qubes — steal methods, don’t pretend we’re Xen

Qubes is **compartments + a trusted dom0 that agents never run in**, copy-out through a narrow qrexec, disposable VMs for dirty work. That *is* the best isolation design in the field. It is **not** a Windows feature.

| Approach | Stops agent `rd` on golden copy? | Fits COSMOS-as-ratified (Windows service, grok.exe, Cursor, schtasks)? |
|---|---|---|
| **Qubes OS as the host** | Yes for *other* VMs and dom0. **No** for files *inside* a Windows HVM — Aug 24 can still happen on `V:` in that VM. | Poor. Windows is a second-class HVM (GPU, USB, licenses). Porting Core off Windows is a new product. |
| **Qubes methods on Windows** | **Yes, if we split vault vs lab.** Vault = no agent principal. Lab = disposable (Job Object today, **Hyper-V VM** if we want Qubes-closer). Copy-out = CAM (qrexec analog). | **This is the fit.** Don’t name it Qubes. Name it compartments. |
| **NTFS `S:afe` only** | Yes until Admin take-ownership. | Executable now. Weaker than a VM. |
| **Hyper-V agent VM, no host mounts** | Stronger than Job Object; closer to AppVM. Needs Pro, VT-x, and CAM copy-out only. | Best *Windows* execution of Qubes intent if Keith will turn Hyper-V on. |
| **Windows Sandbox** | Ephemeral; good for one-shot, not Core. | Side tool, not LiT. |

**Best solution, no pride:**

1. **Vault ≠ lab.** Golden copy (ledger, install, `S:afe` or R2) has **zero** agent write principal. That is Qubes dom0/vault. CAM is qrexec.  
2. **Agents never run in the vault.** Job Object now; Hyper-V later if we want a real VM boundary. That is AppVM/dispVM.  
3. **GitHub `main` protected** — second vault off-box.  
4. **Do not move COSMOS to Qubes OS** unless we explicitly abandon native Windows Core. A Windows HVM on Qubes still needs (1)+(2) *inside* the HVM.

Qubes as daily host = lead in *isolation*, lose the Windows-native mesh (schtasks, grok.exe, cDeck). Qubes **methods** on Windows = lead in *agent-safety product* without changing OS. Ship **vault (B + R2 + CAM)** first; **Hyper-V kids** if Job Object isn’t enough. That’s the honest stack.

### Linux sandbox *around* COSMOS (outer breaker)

Keith: COSMOS lives in a Linux sandbox; the **OS** enforces the rules. That’s a **digital breaker around** the analog AI/COSMOS OS — not WRAP inside it.

If the inner system is compromised, buggy, or you type `rd` *inside* the sandbox, the **host** golden copy still isn’t writable. Same Swiss-cheese idea: inner holes don’t reach outer vault.

| Outer (enforcer) | Inner (COSMOS + agents) | Honest limit |
|---|---|---|
| Linux VM / systemd-nspawn / Docker / Qubes AppVM, **no host bind-mount** | Full COSMOS, messy, even “root” inside | Inner wipe is cheap. Outer vault + R2 only via CAM/qrexec/API. |
| Windows host + **Linux VM** (Hyper-V) holding Core | cDeck on Windows is a **client** of `:8770` | Matches ratified “UI is not authority.” grok.exe/Cursor on Windows must **not** have the vault mounted. |
| WSL2 | Tempting, weak | `/mnt/v` **is** the host. Don’t call it a sandbox if the tree is bind-mounted. |

**Best execution of this intent:** Core (ledger, CAM apply target) in a **Linux (or Hyper-V) vault with no agent write mount**. Windows keeps cDeck + human tools as **clients**. Agents that need a shell run **inside** the sandbox. Copy-out = CAM / API INGRESS only (already in FINAL_ARCHITECTURE).

**Cost:** schtasks → systemd (or Core still Windows *inside* the VM). `grok.exe` is a Windows binary — it stays on the unsafe Windows side talking HTTP, or we don’t run it in the vault. Split-ready monolith already said modules can be processes; **this is that split, with an OS boundary.**

Not install this FIFO. Stronger than NTFS-on-the-same-box if we actually omit the bind-mount. A Linux box with `V:\` mounted in is **not** this idea.

## Verdict

**Yes, it can put COSMOS in the lead in agent-safety on a Windows workstation — if CAM/`S:`/R2 are real.** The idea is orthogonal to every WRAP on the market. Until install exists, it is **architecture**, not a product. Table: `docs/arch/CAM_S_DRIVE_TABLED.md`. This review: ship B first when un-tabled.
