"""Measured container demo for cosmos_paths.

Prints MEASURED lines. Windows-only APIs print NATIVE-DEMO-REQUIRED and do
not pretend they ran. Invoke: python -m cosmos.spikes.cosmos_paths.demo
"""

from __future__ import annotations

import tempfile
import time
from pathlib import Path

from .absence import Absent, Found
from .platform import LONG_PATH_DEMO_CHARS, DriveSemantics, PlatformAdapter
from .plant import plant_installation
from .resolver import RootResolver
from .stamp import now_stamp, worker_identity


def run_demo(scratch: Path | None = None) -> dict[str, object]:
    stamp = now_stamp(worker_identity("demo"))
    adapter = PlatformAdapter()
    cleanup = False
    if scratch is None:
        scratch = Path(tempfile.mkdtemp(prefix="cosmos_paths_demo_"))
        cleanup = False  # leave it; .gitignore covers tmp-like trees if under tmp/

    a_root = scratch / "install_a" / "root"
    b_root = scratch / "install_b" / "root"
    a_rec = scratch / "install_a" / "installation-record.json"
    b_rec = scratch / "install_b" / "installation-record.json"

    t0 = time.perf_counter()
    plant_a = plant_installation(a_root, a_rec)
    plant_b = plant_installation(b_root, b_rec)
    resolver_a = RootResolver.instantiate(a_rec, adapter=adapter)
    resolver_b = RootResolver.instantiate(b_rec, adapter=adapter)
    instantiate_ms = (time.perf_counter() - t0) * 1000.0

    target = adapter.long_path_demo_target(resolver_a.work())
    t1 = time.perf_counter()
    written = adapter.write_bytes(target, b"cosmos-long-path\n")
    walked = adapter.walk(resolver_a.work())
    walk_ms = (time.perf_counter() - t1) * 1000.0
    walk_ok = isinstance(written, Found) and isinstance(walked, Found)
    found_payload = False
    if isinstance(walked, Found):
        found_payload = any("payload.txt" in hit.filenames for hit in walked.value)

    job = adapter.create_job_object("cosmos_paths_demo")
    watch = adapter.read_directory_changes(resolver_a.queue())
    msvcrt = adapter.msvcrt_locking(resolver_a.work() / "msvcrt.lock")
    volume = adapter.windows_volume_info(r"V:\A\Ai\COSMOS")
    winerr = adapter.max_path_winerror3_without_prefix(target)

    measured: dict[str, object] = {
        "instantiate_two_roots_ms": round(instantiate_ms, 3),
        "long_path_chars": len(str(target)),
        "long_path_threshold": LONG_PATH_DEMO_CHARS,
        "long_path_walk_ms": round(walk_ms, 3),
        "long_path_walk_ok": walk_ok and found_payload,
        "roles_resolved": len(resolver_a.report()["roles"]),  # type: ignore[arg-type]
        "second_install_distinct": resolver_a.installation_id != resolver_b.installation_id,
        "second_install_roots": [str(resolver_a.root()), str(resolver_b.root())],
        "drive_letters_distinct": DriveSemantics.roots_are_distinct(r"V:\A\Ai\COSMOS", r"D:\Ai\COSMOS"),
        "secrets_sibling_of_publish": resolver_a.secrets_is_sibling_of_publish(),
        "job_object": job.kind.value if isinstance(job, Absent) else "FOUND",
        "read_directory_changes": watch.kind.value if isinstance(watch, Absent) else "FOUND",
        "msvcrt_locking": msvcrt.kind.value if isinstance(msvcrt, Absent) else "FOUND",
        "volume_info": volume.kind.value if isinstance(volume, Absent) else "FOUND",
        "max_path_winerror3": winerr.kind.value if isinstance(winerr, Absent) else "FOUND",
        **stamp.as_dict(),
    }
    for key, value in measured.items():
        print(f"MEASURED {key}={value}")
    print("NATIVE-DEMO-REQUIRED items:")
    for row in adapter.native_demo_checklist():
        print(f"  {row['item']}: {row['status']} ({row['api']})")
    _ = cleanup
    return measured


def main() -> int:
    run_demo()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
