#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_bite_check_f24_f25 - does test_rails_wired.py FAIL against the PRE-CHANGE code?

A regression test nobody has watched fail is a test that might be asserting
nothing. This builds a throwaway tree holding the pre-change modules and runs
the suite against it, in a subprocess so the reconstruction can never leak into
the real interpreter's sys.modules.

  * `cosmos_registry.py`  <- the file staged under _delme before it was replaced.
  * `cosmos_rails_prober.py` <- reconstructed by REMOVING exactly what this slice
    added: the four rows, the satellite live_calls, and the hands predicate.
    The reconstruction ASSERTS every excision matched, so a silent no-op
    reconstruction cannot masquerade as a bite.

  py -3.14 cosmos\\_bite_check_f24_f25.py --staged _delme\\predispose_...\\cosmos_registry.py
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent / "cosmos"

OLD_WIRED = '''# Wired hands (not a static registry). Each row is probed live; fail-closed.
WIRED_NODES = (
    {"link_id": "sgh-api", "rail_type": "API", "src": "core", "dst": "models",
     "family": "g46-grok", "module": "bts_sgh"},
    {"link_id": "gem-api", "rail_type": "API", "src": "core", "dst": "models",
     "family": "gem-vertex", "module": "bts_gem"},
    {"link_id": "oa-api", "rail_type": "API", "src": "core", "dst": "models",
     "family": "oa-openai", "module": "bts_oa_api"},
    {"link_id": "claude-cli", "rail_type": "CLI", "src": "core", "dst": "code",
     "family": "anthropic", "module": None},
)'''

OLD_DEFAULT_CALL = '''def default_live_call(paths: CosmosPaths, spec: dict):
    def _call():
        if spec.get("module"):
            return _node_live_call(paths, spec["module"])
        return _claude_live_call(paths)
    return _call'''

OLD_DECIDE = '''def _should_live_probe(paths: CosmosPaths, registry, spec: dict, *,
                       live: bool, ttl_s: float) -> bool:
    if live:
        return True
    row = registry.live_nodes().get(spec["link_id"])
    if row:
        age = row.get("age_s")
        if age is not None and age < ttl_s:
            return False
    if spec.get("module"):
        from cosmos_node_rails import resolve_incumbent_root
        return bool(resolve_incumbent_root(paths))
    return _claude_configured(paths)


def map_wired_nodes(paths: CosmosPaths, registry, *, live: bool = False,
                    live_calls: dict | None = None,
                    ttl_s: float = NODE_PROOF_TTL_S) -> list[dict]:
    """Prove each wired rail. Unanswered nodes are not registered."""
    out = []
    for spec in WIRED_NODES:
        lid = spec["link_id"]
        if not _should_live_probe(paths, registry, spec, live=live, ttl_s=ttl_s):
            row = registry.live_nodes().get(lid)
            if row:
                out.append({**row, "skipped": "fresh"})
            else:
                out.append({"link_id": lid, "ok": False, "registered": False,
                            "skipped": "no-hands-configured"})
            continue
        call = None
        if live_calls is not None:
            call = live_calls.get(lid)
        if call is None:
            call = default_live_call(paths, spec)
        rec = registry.prove(
            lid, spec["rail_type"], spec["src"], spec["dst"], call)
        rec["family"] = spec["family"]
        out.append(rec)
    return out'''


def _cut(text: str, start: str, end: str, label: str) -> str:
    i = text.index(start)
    j = text.index(end, i)
    return text[:i] + text[j:]


def reconstruct_prober(src: str) -> str:
    """Undo exactly this slice's additions. Every step asserts it matched."""
    out = src

    i = out.index('FIRECRAWL_RESPONDER = ')
    j = out.index('\nCLI_RAILS = (')
    assert i < j, "WIRED_NODES block not found where expected"
    out = out[:i] + OLD_WIRED + out[j:]

    i = out.index('def _cursor_live_call(')
    j = out.index('def default_live_call(')
    out = out[:i] + out[j:]

    i = out.index('def default_live_call(')
    j = out.index('\n\ndef open_registry(')
    out = out[:i] + OLD_DEFAULT_CALL + out[j:]

    i = out.index('def _hands_configured(')
    j = out.index('\n\ndef poll_once(')
    out = out[:i] + OLD_DECIDE + out[j:]

    # Identifier tokens only: "cursor-api" legitimately survives in
    # _cursor_probe(), which predates this slice and is not part of the wiring.
    for gone in ("SATELLITE_CALLS", "_hands_configured", "_playwright_live_call",
                 "_firecrawl_live_call", "_cursor_live_call",
                 "FIRECRAWL_RESPONDER"):
        assert gone not in out, f"reconstruction left {gone!r} behind"
    body = out[out.index("WIRED_NODES = ("):out.index("\nCLI_RAILS = (")]
    assert body.count('"link_id"') == 4, (
        f"reconstructed WIRED_NODES has {body.count(chr(34) + 'link_id' + chr(34))} "
        f"rows, expected the original 4")
    for wired in ("gw-api", "cursor-api", "firecrawl-web", "playwright-dom"):
        assert wired not in body, f"reconstruction left {wired!r} wired"
    return out


def main() -> int:
    ap = argparse.ArgumentParser(prog="_bite_check_f24_f25")
    ap.add_argument("--staged", required=True,
                    help="the pre-change cosmos_registry.py staged under _delme")
    a = ap.parse_args()
    staged = Path(a.staged)
    if not staged.is_file():
        print(f"staged registry not found: {staged}")
        return 2

    td = Path(tempfile.mkdtemp(prefix="cosmos_bite_"))
    pkg = td / "cosmos"
    pkg.mkdir()
    for p in HERE.iterdir():
        if p.is_file() and p.suffix in (".py", ".toml"):
            shutil.copy2(p, pkg / p.name)

    shutil.copy2(staged, pkg / "cosmos_registry.py")
    prober = pkg / "cosmos_rails_prober.py"
    prober.write_text(
        reconstruct_prober(prober.read_text(encoding="utf-8")), encoding="utf-8")

    print(f"OLD TREE {pkg}")
    r = subprocess.run([sys.executable, str(pkg / "test_rails_wired.py")],
                       capture_output=True, text=True, timeout=900)
    tail = [ln for ln in (r.stdout or "").splitlines() if ln.strip()]
    failed = [ln for ln in tail if ln.strip().startswith("FAIL")]
    print("\n".join(failed))
    print(tail[-1] if tail else (r.stderr or "")[-600:])
    print(f"BITE rc={r.returncode} failed_checks={len(failed)}")
    # The suite MUST fail against the old code, or it is asserting nothing.
    return 0 if r.returncode != 0 and failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
