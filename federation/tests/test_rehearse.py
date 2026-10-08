"""The day-one story writes a root and a report with ids only."""

from __future__ import annotations

from pathlib import Path

from rehearse import rehearse

from cosmos_federation import secret_shape


def test_rehearse_installs_a_peer_without_a_secret_in_the_report(scratch: Path) -> None:
    report = rehearse(scratch)
    assert report["ready"] is True
    assert report["tree_id"] == "Peer-1"
    assert report["host"] is None
    assert report["via"] == "api"
    assert report["phase"] == "DAY_ONE"
    assert report["bind_host"] == "127.0.0.1"
    assert report["bind_port"] == 8770
    assert report["scheme"] == "http"
    assert report["auth"] == "bearer"
    assert report["show_token"] is None
    assert report["cookie_http_only"] is True
    assert report["seconds"] == 120
    assert report["reply"] == "ready"
    assert report["page_has_route"] is True
    assert secret_shape(repr(report)) is False
    assert "sk-" not in repr(report)
    sentinel = (scratch / ".cosmos-root.json").read_text(encoding="utf-8")
    assert "Peer-1" in sentinel
    assert "KMesh-COSMOS-live" not in sentinel
    token = (scratch / "config" / "api_token.txt").read_bytes()
    key = (scratch / "config" / "install_key.bin").read_bytes()
    assert token.strip() != b""
    assert len(key) == 32
    assert token.decode("utf-8") not in repr(report)
    lines = (scratch / "ledger" / "genesis.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    assert "INSTALL" in lines[0]
    assert "CAP_SET" in lines[1]
