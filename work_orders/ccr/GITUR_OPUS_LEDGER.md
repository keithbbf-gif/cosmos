# Gitur BUILD — Opus AM pack #5+#6 first (CHANGES.md §4 order)

Repo keithbbf-gif/cosmos. Branch `ccr/ledger-head-cache-mac2` from **origin/main**. P10. CCr `f47bad79` disposes LiT. Do not pull unique HEAD `8b5ad84`.

Pack: Desktop `Claude Review of COSMOS 9-17/COSMOS_next/CHANGES.md` rows **#5** and **#6**. REVIEW_NOTES.md findings 5–6. Not gospel vs live — unique HEAD already has `mac_v: 2`; this PR ports that **behavior** onto GitHub main.

**Do (simple):**
1. `cosmos_ledger.py`: verified-head cache — append verifies only bytes since last verified offset (O(Δ)). Records written now include `mac_v: 2` HMAC over the **whole** canonical record minus `hmac`. Legacy records without `mac_v` still verify old way. File shorter than verified offset → `TRUNCATED`. Optional signed `<ledger>.head.json` seq match.
2. `cosmos_kernel.py`: turn on head anchor for the authority ledger.
3. `fold_cached()` if missing — incremental projection helper used by spend/sched (minimal; don't rewrite spend in this PR).
4. `--selftest` or tests: mac_v 2 roundtrip; legacy line still loads; truncating the file is TRUNCATED.

**Expected:** unified diff first. Runtime-binding on LiT (already): BOOT_VERIFIED `mac_v: 2` + `authority.jsonl.head.json` seq match. This PR is for **main**.

**Must not:** copy COSMOS_next wholesale (gitur/crew/porosity/copilot bloat). Do not change Opus T. Do not USPTO. No extra grok.exe.

Title: `WO: Opus #5+#6 ledger head-cache + mac_v:2`
