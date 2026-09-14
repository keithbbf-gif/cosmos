#!/usr/bin/env python3
"""Pin: jukebox poll failures surface server detail and mark cached body stale."""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
APP = REPO / "builds" / "cdeck" / "ui" / "app.js"
HEADER = REPO / "builds" / "cdeck" / "ui" / "header.js"


def test_app_js_poll_errors_not_swallowed():
    text = APP.read_text(encoding="utf-8")
    assert "onJukeboxPollError" in text
    assert "_pollStale" in text
    assert "addConsole" in text
    assert not re.search(
        r"pollJukebox\(\)\.catch\(function\s*\(\)\s*\{\s*/\*",
        text,
    ), "pollJukebox still swallows errors in an empty catch"


def test_header_http_error_surfaces_detail():
    snippet = HEADER.read_text(encoding="utf-8")
    m = re.search(r"function httpError[\s\S]*?^  \}", snippet, re.MULTILINE)
    assert m, "httpError not found in header.js"
    script = m.group(0) + """
function check(status, json, expect) {
  var e = httpError(status, json);
  if (e.message !== expect) {
    throw new Error('status ' + status + ' got ' + JSON.stringify(e.message));
  }
}
check(401, {error:'x'}, 'UNAUTHORIZED');
check(503, {error:'CDECK_PANEL_NOT_COMPOSED'}, 'CDECK_PANEL_NOT_COMPOSED');
check(500, {error:'fail', detail:'db down'}, 'fail \\u2014 db down');
"""
    proc = subprocess.run(
        ["node", "-e", script],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout


if __name__ == "__main__":
    test_app_js_poll_errors_not_swallowed()
    test_header_http_error_surfaces_detail()
    print("ok")
