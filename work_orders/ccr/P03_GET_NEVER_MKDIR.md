# Gitur BUILD — P03 GET never mkdir (PLAN.md C1)

**Repo (PRIVATE):** `keithbbf-gif/cosmos`
**Branch:** `ccr/p03-get-never-mkdir` from GitHub `main`. Not unique HEAD.
**Not:** cDeck mix, ballot, invented obs rows, P03_PUBLIC_TENSOR, GET /forge, USPTO.

## Job
GET `/api/v1/porosity` must rebuild from JSONL and must **not mkdir** when the store is absent. `n_obs=0` stays `kind=UNMEASURED`. Do not invent a pair.

Reuse: `cosmos/cosmos_porosity.py` `empty_snapshot`. Live GET already UNMEASURED.

## Bite
1. Delete SQLite projection only → GET still 200 from `obs.jsonl`.
2. Absent store → GET does not create directories; body `kind=UNMEASURED` `n_obs=0`.
3. `_bite_p03_get_never_mkdir.py` `all_bite:true`.

P06 COMPARE only after real rows is a **later** PR. No ballot writer.
