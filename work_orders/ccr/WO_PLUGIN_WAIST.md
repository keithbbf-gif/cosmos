# Gitur BUILD — Plugin-ize lanes / subtract cosmos/_fail_* _bite_* scratch

**Repo (PRIVATE):** `keithbbf-gif/cosmos`
**Branch:** `ccr/plugin-waist` from GitHub `main`. Not unique HEAD `8b5ad84`.
**Lane B:** Cursor Cloud Agent, Opus 5 / Sonnet class. Composer 2.5 / Auto refused. Do not change Opus T.
**P10:** PROPOSE only. Never unlink. Stage leftovers to `_delme\` after CCr accepts.
**Do not:** spawn grok.exe, pull 8b5ad84, merge leftover PRs, USPTO, delete, rewrite kernel/ledger/sched/service, a second plugin OS.

FIRST read `docs/AGENT_BRIEF.md` and `docs/AGENT_BOUNDARIES.md`. Then `docs/STEAL_MAP.md` order item 9: *Plugin-ize lanes (DeepSeek Harness waist). Subtract `_fail_*` / `_bite_*` scratch.* Improvement is not bloat.

## Already on this tree

- `tools/` is the F-29 surface (`tools.mcp_docs.attach_to_kernel`, Kernel compose `tools-surface`, fail-open). Keep that waist.
- `cosmos/_bite_*.py` and `cosmos/_fail_*.py` (plus sibling `.json` artifacts) are CRUCIBLE predecessor-fail pins. They pollute the hot package. Invocation today: `py -3.14 cosmos/_bite_bootup.py` etc.
- DeepSeek Harness idea: **thin core, lanes as plugins**. COSMOS analog is this waist — not a new product named Harness.

## Job

1. **Subtract scratch from `cosmos/`:** move `_fail_*` and `_bite_*` modules (and their json sidecars) to `tools/` (e.g. `tools/bite/`, `tools/fail/`).
2. **Shims stay:** `cosmos/_bite_foo.py` becomes a short re-export so existing `py -3.14 cosmos/_bite_foo.py` still runs. Do not break all_bite pins.
3. **Plugin-ize lanes:** document + (if a real seam exists) extract lane adapters behind the tools waist rather than growing `cosmos_kernel.compose_rails` with more one-off names. Do **not** invent a plugin marketplace. One waist, existing attach pattern.
4. **Never delete.** After CCr accepts, originals stage to `_delme\plugin-waist-<stamp>\`. Agents do not unlink.
5. Net complexity **down**: fewer files on the Core import path, same bite proofs, no new daemon.

Do not move production modules (`cosmos_sandbox.py`, clocks, ledger). Only `_fail_*` / `_bite_*` scratch + a waist note.

## Bite

- `py -3.14 cosmos/_bite_bootup.py` still exits with the same all_bite contract (shim).
- `import cosmos` / Kernel compose does not import bite/fail scratch.
- Occupancy / steal-impl tests that grepped `cosmos/_bite_` still find the shim or are updated in the same PR.
- No new GET. No new clock.

## Output

Unified diffs + file map (from → to → shim) under `proposals | PLUGIN_WAIST.json`. PR `WO: plugin waist subtract bite/fail`. Gitur BUILD. autoCreatePR.
