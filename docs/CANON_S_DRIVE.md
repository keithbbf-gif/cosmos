# CANON — S: two modes (installer option)

Keith 2026-09-18: Human mistakes × AI mistakes = Swiss cheese aligned = wipe. Hard-coded CAM/daemon is a **third layer with different porosity** (high orth to both human and model). Risk drop ~10–100× on that axis. **Default flipped:** COSMOS+AIs live on `S:`; writes **elsewhere** only through the write daemon. That may be hard on Windows — installer offers **two modes**.

CAM is **not an AI**. cDeck can arm/disarm the daemon (human coil). WARN ×3 then refuse.

## Mode A — `S: = Sandbox` (default)

COSMOS, agents, Cursor cwd, Job-Object kids **inside `S:`**.

- Process token for agents: write **on `S:`** (the lab).
- Write **off `S:`** (`V:\`, `C:\`, other volumes, remote) = **Access Denied** unless the **write daemon** (CAM) performs it.
- Daemon: Gitur→CCr check→CAM apply. cDeck switch.
- Typo `rd /s V:\A` from an agent on `S:` **fails**. Typo `rd /s S:\` still hurts the **lab** — GitHub/`main` is the spare for committed source. `live/` on `S:` still needs backup/VSS unless ledger is on Mode B volume.

Harder to execute: Job Object + NTFS + maybe AppContainer so the python/grok process cannot open `V:\` for write.

## Mode B — `S: = S:afe`

`S:` is the **safe** live tree (canon `cosmos/`, ledger, install). Agents **do not** live there.

- Agent/TUI identity: **Read** `S:`, **no Delete**.
- **Only CAM** writes `S:`.
- Lab stays on `V:\A\…` (unsafe). Pen discipline on the lab. `rd /s S:` from you or Grok = **Access Denied**.
- Dist/run: this is the diode. DEV can still wreck `V:\A`; LiT on `S:` survives.

## Installer

`cosmos.py install` asks **one** of:

1. Sandbox (A) — default  
2. S:afe (B)

Creates VHD, mount `S:`, ACL, CAM schtask. Cold peer, no bats. Cloud/remote: same two modes (bucket policy = ACL).

## Swiss cheese

Human hole (typo, `--hard`, `cd /d`) + AI hole (grok `--single`, zombie pen) **line up**. CAM/ACL hole is **orthogonal** (not a prompt, not a tired user). Holes don’t coincide → order of magnitude (Keith: ~2).

Does not replace P10 on the unsafe side. Analog mouth still needs ADC before CAM writes.

Canon: `CANON_FUSES.md` `DEFINE_CAM_SAFE.md` `CANON_WARN.md`. Interactive: `work_orders/ccr/artifacts/fuses.html`.
