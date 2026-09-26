# Factory TICK — P10 propose (2026-09-24)

**KEEP propose. Do not start a second clock.**

## Measured
- `_ccr_loop.py` already exists: 60s cycle, TICK every 5 min, roster every 30 min, OpenWork post via `_ow_post.py`.
- `_crew_spend.py`, `_crew_report_sink.py`, `_crew_chart.py` are on disk (older roster log that said spend missing is stale).
- No new `schtasks` / pythonw / second factory.

## Leftover (operator, not a WO to spawn)
- Whether `pythonw work_orders\ccr\_ccr_loop.py` is **running** is UNMEASURED this sit.
- `_ow_post.py` no-ops on PAUSE / missing `OW_SIT.sid`.
- Do **not** install a second TICK. If the loop is dead, restart **this** script, don’t mint another.

## Not
OpenWork post as a second Core. Grok.exe. A 60s clock beside CLOCKS collapse.
