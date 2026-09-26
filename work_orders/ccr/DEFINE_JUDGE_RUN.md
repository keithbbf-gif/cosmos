# DEFINE — one Judge per run; idle until the board has work

Keith: silent fail is also the **partner** WO. Autopsy pairs. One Judge for a **run**. Do not spawn a new Judge (new fat cache) because the last one expired while WOMB was empty. If the board is empty long enough that the Judge cache dies, **leave the chair empty** until there are **20–40** work orders. Token economy.

## Measured (this occupancy)

| Fact | n |
|---|---|
| Failed WOs | 157 |
| Failed **with no same-minute partner** | **118** |
| Failed **with a partner that succeeded** (14 mixed minute-batches) | **24** |
| Fail-only batches (all died together) | 15 rows / 2 batches |
| Records that even **mention** judge / who_erred | **3 / 217** |

Judge was not in the runner. Partners were not scored. FAIL was terminal. Opposite of token economy.

## Functions (to code)

1. `wo_partner(order) -> {partner_id, partner_state} | UNMEASURED`  
   Same WO family: shared stamp-minute **or** same Task prefix **or** explicit `pair_id` on the six-field. Silent fail of A **always** autopsies B.

2. `judge_run` — one Judge model + **one** fat prefix for the whole run. `attempt` N regrade uses **that** cache. Do not mint Judge #2 because TTL expired on an empty board.

3. `judge_idle_gate(n_board, cache_alive) -> sit | leave`  
   If `n_board` (bucket+picked only) < **20** and cache expired: **leave**. Sit when n in **20–40** (or cache still alive and there is ≥1 pair).

4. `fail_xfer(order)` — FAIL → JSONL attempt + partner autopsy + GAC re-seat or `superseded`. Never a corpse on WOMB surface.

5. Board projection: **bucket + picked**. Failed is `_delme` autopsy archive after JSONL.
