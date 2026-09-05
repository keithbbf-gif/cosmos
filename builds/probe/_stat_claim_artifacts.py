#!/usr/bin/env python3
"""One-shot: print bytes + mtime of claim-backing sources and artifacts."""
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
FILES = [
    "builds/backup/cosmos_backup.py",
    "builds/backup/cosmos_backup_r2.py",
    "builds/backup/cosmos_backup_mounts.py",
    "builds/backup/cosmos_state_offsite.py",
    "builds/backup/cosmos_offsite_clock.py",
    "builds/backup/cosmos_mount_clock.py",
    "builds/probe/tools/mcp_docs.py",
    "builds/probe/tools/surface.py",
    "builds/probe/mesh_blockers.py",
    "builds/probe/longpath_census.py",
    "builds/probe/credential_manifest.py",
    "builds/probe/tool_disposition.py",
    "cosmos/cosmos_backup.py",
    "cosmos/cosmos_backup_clock.py",
    "cosmos/cosmos_refusals.py",
    "docs/REFUSAL_TAXONOMY.md",
    "docs/CREDENTIALS_NEEDED.md",
    "docs/MESH_STATUS.md",
    "builds/probe/MESH_STATUS.json",
    "builds/probe/MESH_STATUS.md",
    "builds/probe/_longpath_behaviour_20260831T0700Z.json",
    "builds/probe/_longpath_behaviour.json",
    "builds/probe/_tools_surface_live.json",
    "builds/probe/_blockers_freshness.json",
    "builds/probe/_f41_live_apply_refused.json",
    "builds/backup/_f43_mutate_retire_live.json",
    "builds/backup/_f47_live_adapter.json",
    "builds/backup/_f54_live_preflight.json",
    "builds/backup/_hmac_copyhash_live.json",
    "builds/backup/_stage_restore_live.json",
    "live/ledger/authority.jsonl",
    "live/state/SEED.json",
    "live/state/inflight.jsonl",
    "live/state/motif_tracker.json",
]
print(f"{'rel':<62} {'bytes':>10} mtime_utc")
for rel in FILES:
    p = REPO / rel
    if not p.exists():
        print(f"{rel:<62} MISSING")
        continue
    st = p.stat()
    mt = datetime.fromtimestamp(st.st_mtime, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"{rel:<62} {st.st_size:10d} {mt}")
