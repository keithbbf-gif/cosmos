"""The HTTP routes call the real console, not a fake."""

from __future__ import annotations

import json
import threading
from urllib.request import Request, urlopen


def _post(base: str, path: str, body: dict) -> dict:
    raw = json.dumps(body).encode("utf-8")
    request = Request(base + path, data=raw, headers={"Content-Type": "application/json"})
    with urlopen(request) as response:
        return json.loads(response.read().decode("utf-8"))


def _get(base: str, path: str) -> dict:
    with urlopen(base + path) as response:
        return json.loads(response.read().decode("utf-8"))


def test_real_console_over_http(tmp_path):
    from clusters.api import serve
    from clusters.console import Console

    server = serve(Console(str(tmp_path / "projection")), port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_address[1]}"
    try:
        health = _get(base, "/v1/health")
        assert health["ok"] is True
        features = _get(base, "/v1/features")
        assert "harness-plan" in features["features"]
        project = _post(base, "/v1/projects", {"name": "web", "root": str(tmp_path / "web")})
        session = _post(
            base,
            "/v1/sessions",
            {"project_id": project["id"], "door": "cosmos-code", "hero": "sol", "task": "add a function"},
        )
        assert session["door_executable"] is False
        refused = _post(base, "/v1/policy/check", {"command": "grok.exe", "turbo": True})
        assert refused["decision"] == "refuse"
        plan = _post(
            base,
            "/v1/harness/plan",
            {
                "hero": "sol",
                "task": "Add one function that returns 1.",
                "where": str(tmp_path / "web"),
                "execute": False,
            },
        )
        assert plan["seated"] is False
        assert plan["started"] is False
        _post(base, "/v1/spend/budget", {"provider": "openai", "daily_cap_usd": 1})
        _post(base, "/v1/spend/observe", {"provider": "openai", "usd": 0.4})
        paused = _post(base, "/v1/spend/check", {"provider": "openai", "usd": 0.1})
        assert paused["decision"] == "pause"
        assert paused["code"] == "UNMEASURED"
        doors = _get(base, "/v1/doors")
        grok = next(row for row in doors["items"] if row["id"] == "grok")
        assert grok["executable"] is False
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()
