"""Red before an edit. Green after it.

The oracle is an argument vector run with ``shell=False`` and a scrubbed
environment. The pre-edit run must exit non-zero. The post-edit run of the
same vector must exit zero. A green log from the model is not this result.

The working directory is the jail root. Timeout defaults to 15 seconds,
matching the constants host used while seating.
"""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass

from cosmos_harness.jail import Jail
from cosmos_harness.job import run_child
from cosmos_harness.layers import scrub_env
from cosmos_harness.refuse import Refuse


@dataclass(frozen=True)
class OracleResult:
    """One run. ``ok`` is exit code 0. ``log_hash`` covers stdout and stderr."""

    exit_code: int
    stdout: str
    stderr: str
    log_hash: str

    @property
    def ok(self) -> bool:
        return self.exit_code == 0


class Oracle:
    """The host runs this. The model may call the ``oracle`` hand to read it."""

    def __init__(self, jail: Jail, argv: tuple[str, ...], timeout: float = 15.0) -> None:
        if not argv:
            raise Refuse("PACK_INCOMPLETE", "oracle")
        self.jail = jail
        self.argv = argv
        self.timeout = timeout
        self.pre: OracleResult | None = None
        self.post: OracleResult | None = None

    def run(self) -> OracleResult:
        """Run the vector once. Timeout and a missing executable are failures."""
        env = scrub_env(dict(os.environ))
        # A pyc from the red run must not hide the edit the green run is judging.
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        try:
            # UNENCLOSED_CHILD propagates. A timeout is exit 124, which is
            # still an oracle result. An enclosure failure is not a red test.
            code, out, err = run_child(
                list(self.argv),
                cwd=self.jail.root,
                env=env,
                timeout=self.timeout,
            )
        except Refuse:
            raise
        except OSError as exc:
            out, err, code = "", str(exc), 127
        digest = hashlib.sha256(f"{code}\n{out}\n{err}".encode("utf-8")).hexdigest()
        return OracleResult(code, out[-4000:], err[-4000:], digest)

    def prove_red(self) -> OracleResult:
        """The bug is present. A zero exit refuses the attempt before any edit."""
        result = self.run()
        self.pre = result
        if result.ok:
            raise Refuse("ORACLE_ALREADY_GREEN", result.log_hash)
        return result

    def prove_green(self) -> OracleResult:
        """The same oracle after the edit. Non-zero refuses done."""
        if self.pre is None or self.pre.ok:
            raise Refuse("ORACLE_PRE_MISSING", "red was not recorded")
        result = self.run()
        self.post = result
        if not result.ok:
            raise Refuse("ORACLE_STILL_RED", result.log_hash)
        return result
