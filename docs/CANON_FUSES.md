# CANON — hard-coded fuses, breakers, contactors (future DEV)

Keith 2026-09-18: controlling AI is **not** another prompt. It is **hardware-shaped, non-AI** protection. EE analogies are the vocabulary. Future DEV implements these as code + OS, not as WRAP prose.

AI output is **analog** (continuous, plausible, variable). COSMOS **digitizes** it through a **non-AI transformer** (ADC) before it may write. Need **DACs** the other way (safe state → analog mouth for the human).

## Devices

| Device | EE | COSMOS |
|---|---|---|
| **Fuse** | Opens on overcurrent; must be replaced | Spend cap, day lane, token budget. Blows; human resets. Not an LLM. |
| **Breaker** | Opens on fault; can be reset | `warn3` ×3 then refuse (grok.exe, concat CTX, two heads, Judge on empty WOMB). CAM clock. |
| **Contactor** | Coil must be energized to close the power path | Spawn layers Role→Enviro **applied** or **no spawn**. CCR.lease token. Gitur merge is the coil. |
| **Diode** | One-way | Gitur → CAM → `S:afe` **write**. Agents **read** LiT; they do not write it. |
| **Bipolar** | One-way write, two-way read | Agents **read** `S:` and GitHub; **write** only the unsafe lab. CAM **writes** LiT one way. Human **reads** both. |
| **ADC** | Analog → digital | Non-AI xform: schema check, expected-form checker, occupancy grep, `mac_v`, JSONL score. Mouth does not land until ADC says 1. |
| **DAC** | Digital → analog | Safe ledger/state → human prose, cDeck paint, WOMBAT ITEM. Never the reverse without ADC. |

## Rules (smallest)

1. **No AI in the fuse.** CAM, `warn3`, NTFS ACL, GitHub ruleset, spend gate — hard-coded.
2. **The resource rejects the write.** Lease in the agent’s head is not enough (zombie pen). `S:afe` / GitHub `main` / CAS check `token >= highest_seen`.
3. **Diode on LiT write.** Only CAM (or CCr merge → CAM) writes `S:`. Agents never hold that ACL.
4. **Unsafe side still has pen discipline.** Fuses don’t replace P10.
5. **WARN ×3 then trip** (`docs/CANON_WARN.md`). Humans are distracted.
6. **One head** (`docs/CANON_ONE_HEAD.md`). Gitur → LiT only.
7. **Spawn layers** (`docs/CANON_SPAWN.md`). Role→Enviro applied or no call.
8. Analog mouth → ADC → digital artifact → (optional) DAC to the human. Never analog-to-disk.

Install (`cosmos.py install`) is where S:afe / CAM / ACL are created — cold machine, no bats.

Related: `DEFINE_CAM_SAFE.md`, `CANON_SPAWN.md`, `CANON_WARN.md`, `CANON_ONE_HEAD.md`.
