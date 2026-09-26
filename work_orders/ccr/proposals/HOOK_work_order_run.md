# Hook (CCr LiT) — fail-closed spawn

In `cosmos_work_order_run.py` `process_one`, **before** `build_argv` / `spawn_detached`:

```python
from cosmos_spawn import apply, refuse_grok_argv, refuse_concat_ctx, SpawnError
refuse_concat_ctx(rec.get("Context source"))
spec = apply(role, model)  # from Agent field
refuse_grok_argv(argv)
```

On `SpawnError`: `fail_xfer` JSONL, **do not spawn**. Empty Output from grok.exe must become impossible.

Copy `proposals/cosmos_spawn.py` → `cosmos/cosmos_spawn.py`. Pen `f47bad79`. Gitur `GITUR_CANON_SPAWN.md` / agent `bc-4e6617bd`.
