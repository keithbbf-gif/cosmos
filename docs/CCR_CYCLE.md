# CCr factory cycle (Keith 2026-09-10)

Not idle. 1-minute loop runs **one pass**. 10-minute is Keith's report only.

```
fetch jobs → prompt-engineer ITEM → assign 2-man crews
  → Luna review (frozen prefix, new diffs in TAIL)
  → CCr reads Luna
  → Gitur check (Cursor PR / gh)
  → CCr implement (merge or write tree)
  → sync GitHub
  → repeat
```

Pairs: **GLM+GF38** and **DS+G31**. Luna Flex cached reviewer. **Sol = together, queued.**
Propose only on crew. CCr is the writer. Iterative `seat-NNN.json`. Never clobber Luna frozen.

Driver: `py -3.14 work_orders/ccr/_ccr_cycle.py`
Queue: `work_orders/ccr/CREW/OUT/QUEUE.json`
