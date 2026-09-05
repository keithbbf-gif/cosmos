# Unattended clock entry: detach any Task Scheduler console, then run the
# real script in-process. Must be the first thing pythonw executes.
from __future__ import annotations

import os
import runpy
import sys

if os.name == "nt":
    import ctypes
    ctypes.windll.kernel32.FreeConsole()

if len(sys.argv) < 2:
    sys.exit(2)
script = sys.argv[1]
sys.argv = [script, *sys.argv[2:]]
runpy.run_path(script, run_name="__main__")
