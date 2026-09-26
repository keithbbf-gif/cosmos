# Gitur BUILD — P10 resolver identity bite if missing (PLAN.md D2)

**Repo (PRIVATE):** `keithbbf-gif/cosmos`
**Branch:** `ccr/p10-resolver-bite` from GitHub `main`.
**Not:** cDeck mix, drive-literal fallbacks, parent-walking, leftover PRs.

## Job
Empty directory without sentinel content is `IDENTITY_MISMATCH`. Existence is not identity.
Reuse `cosmos/cosmos_paths.py`. Add bite if missing; do not invent a second resolver.

## Bite
- Dir exists, no `.cosmos-root.json` → IDENTITY_MISMATCH.
- Sentinel content mismatch → IDENTITY_MISMATCH.
- `_bite_p10_identity.py` all_bite:true.
