---
name: womb-six-field
description: Use when WOMBAT on gemini-3.8-flash writing the WOMB. Trigger on ITEM, drop, six-field work order, FIFO, partner pick. First line ITEM or NONE.
---
# WOMBAT — six-field drop

1. First line ITEM or NONE. Empty Output is a WOMBAT miss, not as-is retry.
2. Write only work_orders/drop/wo-*.json. Fields: Agent, Context source (list of existing paths, no ` · ` concat), Task, Target & scope, Timestamp, Output.
3. FIFO oldest first. Do not retry corpses. DEFINE then pick_pair (high orth, low porosity on the axis).
4. Stamp CCrew partner, cache window/floor, porosity mag, ortho. Missing cell = UNMEASURED, not 0.
5. Skills are model/role specific — write SKILL.md, never "none".
6. thinking medium. PREFIX fat ≥ 4096. No grok.exe. No LiT. Seat after JUDGE + Coders 1–6.
