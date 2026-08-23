"""Measured demo of cosmos_lock. Prints MEASURED lines; refuses unknown flags."""

from __future__ import annotations

import argparse
import sys
import tempfile
import time
from pathlib import Path

from cosmos.spikes.cosmos_lock.absence import RefusalCode
from cosmos.spikes.cosmos_lock.arbiter import Arbiter
from cosmos.spikes.cosmos_lock.clock import FrozenClock
from cosmos.spikes.cosmos_lock.identity import Stamp, WorkerIdentity
from cosmos.spikes.cosmos_lock.ingress import IngressEnvelope, write_envelope
from cosmos.spikes.cosmos_lock.platform import PlatformAdapter, extended_win_path


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cosmos_lock")
    parser.add_argument("--root", default="", help="explicit arbiter root; empty uses a temp dir")
    parser.add_argument("--ttl", type=float, default=30.0, help="lease TTL in arbiter seconds")
    return parser


def run_measured(root: Path, ttl: float) -> list[str]:
    lines: list[str] = []
    clock = FrozenClock()
    adapter = PlatformAdapter()
    service_key = b"cosmos-lock-spike-demo-key"
    native = WorkerIdentity.mint("native-demo", lane="native")
    sandbox = WorkerIdentity.mint("sandbox-claimant", lane="sandbox")
    t0 = time.perf_counter()
    built = Arbiter.instantiate(
        root=root,
        clock=clock,
        service_key=service_key,
        installation_id="spike-cosmos-lock-demo",
        adapter=adapter,
        ttl_seconds=ttl,
    )
    if not built.ok:
        raise RuntimeError(f"instantiate failed: {built.kind} {built.reason}")
    arbiter = built.unwrap()
    arbiter.register_worker(native)
    arbiter.register_worker(sandbox)

    g0 = time.perf_counter()
    granted = arbiter.grant(native, "tree-write", purpose="demo")
    grant_ms = (time.perf_counter() - g0) * 1000.0
    cap = granted.unwrap()
    lines.append(f"MEASURED grant_latency_ms={grant_ms:.3f}")
    lines.append(f"MEASURED fencing_token={cap.fencing_token}")
    lines.append(f"MEASURED lease_id={cap.lease_id}")

    c0 = time.perf_counter()
    committed = arbiter.commit(
        worker=native,
        resource_id="tree-write",
        fencing_token=cap.fencing_token,
        artifact_bytes=b"native-protected-bytes",
        expected_inputs={},
    )
    commit_ms = (time.perf_counter() - c0) * 1000.0
    lines.append(f"MEASURED commit_latency_ms={commit_ms:.3f}")
    lines.append(f"MEASURED commit_ok={committed.ok}")

    fake_lock = root / "sandbox_universe" / r"V:\Ai\_queue\tree_lock.json"
    fake_lock.parent.mkdir(parents=True, exist_ok=True)
    fake_lock.write_text('{"holder":"sandbox-claimant","token":999}\n', encoding="utf-8")
    shape = adapter.native_authoritative_path(r"V:\Ai\_queue\tree_lock.json")
    env = IngressEnvelope.build(
        sandbox,
        Stamp.from_clock(sandbox, clock, time_source=clock.source_name),
        {"try": "claim", "resource_id": "tree-write", "token": 999},
    )
    env_path = write_envelope(arbiter.ingress_dir, env)
    ingested = arbiter.ingest_ingress(env_path)
    sandbox_commit = arbiter.commit_from_ingress(
        env,
        resource_id="tree-write",
        fencing_token=999,
        artifact_bytes=b"sandbox-should-not-publish",
    )
    holder = arbiter.current_holder("tree-write").unwrap()
    holders = 1 if holder is not None and holder.holder.worker_id == "native-demo" else 0
    lines.append(f"MEASURED two_universes_holders={holders}")
    lines.append(f"MEASURED windows_path_on_posix={shape.kind.value}:{shape.code}")
    lines.append(f"MEASURED ingress_accepted={ingested.ok}")
    lines.append(f"MEASURED sandbox_commit={sandbox_commit.code}")

    clock.advance(ttl + 1)
    expired_pub = arbiter.commit(
        worker=native,
        resource_id="tree-write",
        fencing_token=cap.fencing_token,
        artifact_bytes=b"expired-should-fail",
    )
    lines.append(f"MEASURED expired_holder_publish={expired_pub.code}")

    takeover = arbiter.grant(sandbox, "tree-write", purpose="takeover-after-death")
    cap2 = takeover.unwrap()
    chain = arbiter.takeover_chain("tree-write")
    lines.append(f"MEASURED takeover_chain={','.join(chain)}")
    lines.append(f"MEASURED dying_holder_cleanup_calls={arbiter.release_calls}")
    lines.append(f"MEASURED new_fencing_token={cap2.fencing_token}")

    stale = arbiter.commit(
        worker=native,
        resource_id="tree-write",
        fencing_token=cap.fencing_token,
        artifact_bytes=b"stale-should-fail",
    )
    lines.append(f"MEASURED stale_token_refusal={stale.code}")
    refused_events = [e for e in arbiter.ledger.of_type("COMMIT_REFUSED")]
    lines.append(f"MEASURED commit_refused_ledgered={len(refused_events)}")

    torn_path = arbiter.mirror_dir / "planted-torn.lease.json"
    torn_path.write_bytes(b"{this is not json")
    torn = arbiter.read_lease_mirror(torn_path)
    lines.append(f"MEASURED torn_state={torn.kind.value}:{torn.code}")

    job = adapter.create_job_object("cosmos-lock-demo")
    rdcw = adapter.watch_directory_rdcw(root)
    msvcrt = adapter.msvcrt_try_lock(root / "advisory.lock")
    volume = adapter.windows_volume_name(root)
    lines.append(f"MEASURED job_objects={job.kind.value}")
    lines.append(f"MEASURED readdirectorychangesw={rdcw.kind.value}")
    lines.append(f"MEASURED msvcrt={msvcrt.kind.value}")
    lines.append(f"MEASURED win_volume={volume.kind.value}")
    lines.append(f"MEASURED extended_win_path={extended_win_path(r'V:\Ai\COSMOS')}")

    posix_lock = adapter.try_exclusive_lock(root / "advisory.lock")
    posix_lock2 = adapter.try_exclusive_lock(root / "advisory.lock")
    lines.append(f"MEASURED posix_advisory_lock={posix_lock.ok}")
    lines.append(f"MEASURED posix_second_lock={posix_lock2.code}")
    if posix_lock.ok:
        posix_lock.unwrap().release()

    missing = arbiter.inspect_lease("never-granted")
    skew = arbiter.probe_client_clock(clock.epoch() + 10_000)
    lines.append(f"MEASURED not_in_record={missing.kind.value}")
    lines.append(f"MEASURED out_of_clock={skew.kind.value}")

    stamp = arbiter.stamp(native)
    lines.append(
        f"MEASURED stamp worker={stamp.worker.worker_id} offset={stamp.tz_offset} "
        f"epoch={stamp.epoch_seconds:.3f} iso={stamp.aware_iso}"
    )
    lines.append(f"MEASURED demo_wall_ms={(time.perf_counter() - t0) * 1000.0:.3f}")
    lines.append(f"MEASURED refusal_stale={RefusalCode.STALE_TOKEN.value}")
    return lines


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    try:
        args = parser.parse_args(argv if argv is not None else sys.argv[1:])
    except SystemExit as exc:
        code = exc.code
        return 2 if code not in (0, None) else 0
    if args.root:
        root = Path(args.root)
    else:
        root = Path(tempfile.mkdtemp(prefix="cosmos_lock_demo_"))
    for line in run_measured(root, ttl=args.ttl):
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
