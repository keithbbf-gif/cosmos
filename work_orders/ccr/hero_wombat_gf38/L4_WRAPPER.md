# Layer 4 — Wrapper

**Hole:** no `cosmos/WRAP/WOMBAT` on LiT (only CODER, CCR). Fill until Gitur:

```
role = WOMBAT
pen = none
first_line = ITEM | NONE
wrap = What is the intent, and the best execution of this intent?
board = write work_orders/drop/ wo-*.json only
empty_output = error (not as-is retry)
style = STYLES/_TEMPLATE
```

ITEM body: Agent, Context source **list**, Task, Target & scope, Timestamp, Output. No ` · ` concat in Context source.
