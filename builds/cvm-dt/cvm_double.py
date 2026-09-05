#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cvm_double — a loopback Core DOUBLE. Real route code, throwaway root, NOT Core.

WHY THIS EXISTS. Stage 6 for cvm-dt is two claims wearing one name:

  A. "this client speaks the CVM wire correctly on this box"   — needs nothing
     but this machine;
  B. "the resident authority on :8770 answers it"              — needs Core.

Prior runs returned `partial` because A was chained to B: Core was down, so
nothing got measured, including everything that never needed Core. This module
is the fixture that unchains A. It stands up `cosmos_service.Service` — the
REAL handlers, `_cvm_pull_response` / `cvm_post_dispatch`, not a hand-written
canned reply — on a **fresh installed root in a temp directory**, bound to
127.0.0.1:0. The client then drives a true POST /cvm/push → GET /cvm/pull
round trip and the numbers are measured, not estimated.

WHAT IT IS NOT — and this is the whole discipline:

  * It is NOT Core, and it is NOT a substitute for Core. It carries
    `kind=LOOPBACK_DOUBLE`, every record that quotes it says `is_core: false`,
    and `cvm_gate core` has no import path to it. A double answering "yes"
    proves the double is up. That is not the claim half B makes.
  * It NEVER touches the live tree. Its root is `tempfile.mkdtemp`; the
    pull-clock stamps ITS state/cvm/pull.json, never the live one.
  * It is not the `:8791` trial kernel by another name. That was an attempt to
    pass half B with a stand-in; this is an admission that half B cannot be
    passed yet, plus a way to stop half A waiting on it.

    from cvm_double import CoreDouble, dead_loopback_base
    with CoreDouble() as dbl:
        ...                       # dbl.base, dbl.token, dbl.paths
"""
from __future__ import annotations

import socket
import sys
import tempfile
import time
from pathlib import Path
from typing import Optional

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
_COSMOS_LIB = Path(__file__).resolve().parents[2] / "cosmos"
if _COSMOS_LIB.is_dir() and str(_COSMOS_LIB) not in sys.path:
    sys.path.insert(0, str(_COSMOS_LIB))

from cosmos_kernel import Kernel, install                        # noqa: E402
from cosmos_service import Service                               # noqa: E402

DOUBLE_KIND = "LOOPBACK_DOUBLE"
DEFAULT_TREE_ID = "KMesh-COSMOS-live"


def scratch_root(token: str = "cvm-double-token",
                 tree_id: str = DEFAULT_TREE_ID,
                 worker: str = "cvm-dt-double") -> Kernel:
    """An installed COSMOS root in a temp dir. No listener, no live tree.

    The client half of stage 6 needs somewhere to WRITE — a voice heartbeat,
    a pull stamp — and the live runtime root is not it: the gate is a reader
    there. This is that somewhere.
    """
    root = Path(tempfile.mkdtemp(prefix="cvm-double-"))
    install(root, tree_id=tree_id)
    k = Kernel(root, worker=worker)
    k.paths.config("api_token.txt").write_text(token + "\n", encoding="utf-8")
    return k


class CoreDouble:
    """Real Core route code on a throwaway root. Typed as a double, always."""

    def __init__(self, tree_id: str = DEFAULT_TREE_ID,
                 token: str = "cvm-double-token",
                 worker: str = "cvm-dt-double"):
        self.tree_id = tree_id
        self.token = token
        self.worker = worker
        self.root: Optional[Path] = None
        self.kernel: Optional[Kernel] = None
        self.service: Optional[Service] = None
        self.boot_ms: float = 0.0

    # ---- lifecycle ----
    def start(self) -> "CoreDouble":
        t0 = time.perf_counter()
        self.kernel = scratch_root(self.token, self.tree_id, self.worker)
        self.root = self.kernel.paths.root
        self.service = Service(self.kernel, host="127.0.0.1", port=0)
        self.service.serve_background()
        self.boot_ms = round((time.perf_counter() - t0) * 1000.0, 3)
        return self

    def stop(self) -> None:
        """Shut the listener. The temp root is LEFT ON DISK — never delete."""
        if self.service is not None:
            self.service.shutdown()
            self.service = None

    def __enter__(self) -> "CoreDouble":
        return self.start()

    def __exit__(self, *exc) -> bool:
        self.stop()
        return False

    # ---- accessors ----
    @property
    def base(self) -> str:
        if self.service is None:
            raise RuntimeError("CoreDouble is not started")
        return "http://127.0.0.1:%d" % self.service.port

    @property
    def paths(self):
        if self.kernel is None:
            raise RuntimeError("CoreDouble is not started")
        return self.kernel.paths

    def describe(self) -> dict:
        """The provenance stanza every record quoting this double must carry."""
        return {
            "kind": DOUBLE_KIND,
            "is_core": False,
            "base": self.base,
            "root": str(self.root),
            "tree_id": self.tree_id,
            "handlers": ("cosmos_service._cvm_pull_response + "
                         "cosmos_cvm_push.cvm_post_dispatch (real route code)"),
            "boot_ms": self.boot_ms,
            "note": ("A double answering proves the double is up. It is not "
                     "evidence about the resident Core on :8770."),
        }


def dead_loopback_base() -> str:
    """A loopback URL with nothing listening — for proving the refusal path.

    Bind :0, read the port the OS handed out, close it. The next connect is a
    refused connect, which is exactly the UNREACHABLE branch we want measured
    rather than assumed.
    """
    s = socket.socket()
    try:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    finally:
        s.close()
    return "http://127.0.0.1:%d" % port
