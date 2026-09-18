# WRAP — smarter daemon (native, not an LLM)

Not a model chair. Windows clock + `cosmos_work_order_run` / a `--once` schtask. Token economy.

**Sit Judge only when:**
- `n_board` = count(bucket)+count(picked) is **20–40**, or cache still alive and ≥1 pair is waiting
- One Judge slug for the **run**; one fat prefix; measure `cached_tokens`
- If cache expired **and** n_board < 20: **leave**. Do not mint a new 80% write to watch an empty WOMB

**On FAIL:**
- `fail_xfer`: JSONL attempt, `wo_partner` autopsy, GAC re-seat or `superseded`
- Never spawn `grok.exe`. Never leave corpses on the WOMB surface (failed/ is archive after JSONL)

**FIFO:** oldest drop / oldest Gitur PR first. Chat silos join by Timestamp.

**Not:** in-process cron, LLM loop, second Core, SOL/non-flex Luna, extra grok.exe.
