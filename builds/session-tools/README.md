# session-tools

Product on COSMOS. Not CORE. Open Sessions stays the list/open surface.

```
py -3.14 builds/session-tools/session_tools.py scan --family cowork --store <catalog-dir>
py -3.14 builds/session-tools/session_tools.py load --id cow-<sid> --store <catalog-dir>
py -3.14 builds/session-tools/session_tools.py migrate --id grok-<sid> --store <dir> --workspace-id <ws> --directory <ow-dir> [--dry-run]
```

Canonical: `{id}.ctr.jsonl` + `{id}.ctr.decl.json` (sha-only). Legal load refuses. 666 not re-ingested.

Tests: `tests/test_session_tools_scan_load.py` · `tests/test_session_tools_route.py`
