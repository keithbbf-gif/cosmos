# Gitur BUILD — attempts JSONL + sqlite projection

**HOLD. Do not fire.** Keith 2026-09-18: write the WO, don't fire. After **#580–#586** have a real Judge (SOL/Codex named) and CCr merge or DROP.

**Repo:** `keithbbf-gif/cosmos`  
**Branch:** `ccr/attempts-store` from `origin/main`.  
**P10:** PROPOSE. CCr `f47bad79` disposes.

FIRST read `docs/AGENT_BRIEF.md`, `docs/AGENT_BOUNDARIES.md`, `docs/arch/STUDENT_RECORD.md`, `docs/arch/POROSITY_MATH.md` (clone the Database table, do not join the files), `work_orders/ccr/DEFINE_AGENT_LEARN.md`.

## Job (one PR, later)

1. Authority `live/state/attempts/attempts.jsonl` schema `cosmos-score-attempt/1`. Append only. Regrade = new line `attempt+1`.
2. Projection `live/state/attempts/attempts.sqlite` rebuildable. GET never mkdir.
3. GET `/api/v1/attempts` empty → `kind=UNMEASURED`, `n=0`. Never invent.
4. Blobs by hash (preload, prompt, output). JSONL holds hashes + grader + verdict.
5. `record_attempt(...)` hook from WOMB / Codex vet / Luna judge. A SOL Codex review without a row is a leak.
6. `--selftest`: write two attempts (parent + regrade), rebuild sqlite, GET does not mkdir, porosity store untouched.
7. Do not write Core ledger events for blob bytes. Do not TOML.

Title: `WO: student record JSONL + sqlite projection (not porosity.sqlite)`

**Must not:** fire while 580–586 open; restore unique-head; USPTO; extra grok.exe; merge cDeck #320.
