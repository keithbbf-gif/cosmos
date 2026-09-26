# Student record — same ethic as the tensor, not the same file

Keith 2026-09-18: preload, prompts, outputs, grades, who graded, every test the student takes — must be saved. *Same dbase as the tensor?* Then: *Don't you think it should be in a dbase, or TOML, or what?* **Finish that. Make it so.** WOs written, **not fired**.

## Decision

Same **pattern** as porosity. **Two directories.** Do not merge into `porosity.sqlite`. Do not put this in TOML.

| What | Authority | Projection | Schema |
|---|---|---|---|
| Tensor | `live/state/porosity/obs.jsonl` | `live/state/porosity/porosity.sqlite` | `cosmos-porosity-tensor/5` |
| Student | `live/state/attempts/attempts.jsonl` | `live/state/attempts/attempts.sqlite` | `cosmos-score-attempt/1` |

TOML stays the **legend** defaults (Role×Model×Harness…), not the transcript.

Core ledger stays the OS chain. Student blobs do not bloat it. A bad grade must not refuse the kernel.

## Row (attempt N; regrade = N+1, never UPDATE)

`job`, chair (`WOMBAT`\|`CODER`\|`JUDGE`\|`ORC`\|`CCR`), model, legend hash (the seven layers as applied), preload/prefix hash, prompt path+hash, output path+hash, grader (model + chair), verdict/score, xfer, `attempt`, `parent_attempt`, `rejected`, stamps.

Fat prefix/output live as path+hash (CAS or `live/state/attempts/blobs/<hash>`), not a 2MB JSONL line.

SOL Codex vet of Gitur PRs writes a row here or it did not happen.

## API (later, Gitur — do not fire now)

GET `/api/v1/attempts` — never mkdir, never invents. Empty → `kind=UNMEASURED`, `n=0`. Rebuild sqlite from JSONL on boot/read.

## Not

One mutable SQL gradebook. TOML attempt files. Mixing tensor folds into attempt rows. USPTO. Occupancy pin drop.
