"""Resolve optional doors and print the install state. Does not download them."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "harness" / "G47"))

from g47.locate import probe, write_local  # noqa: E402
from g47.refuse import Refuse  # noqa: E402


def main() -> int:
    try:
        dest = write_local()
    except Refuse as exc:
        print(f"{exc.reason}: {exc.detail}", file=sys.stderr)
        return 2
    print(dest)
    missing = 0
    for row in probe():
        place = row["local"] or row["binary_found"] or "-"
        print(f"{row['id']}\t{row['state']}\t{place}")
        if row["state"] != "found":
            missing += 1
            print(f"  obtain: {row['obtain']}")
    print("pip: py -3.14 -m pip install -e harness/G47 -e cosmos_harness -e cosmos_code")
    print(f"missing={missing}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
