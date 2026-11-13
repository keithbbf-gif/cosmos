# -*- coding: utf-8 -*-
"""Seat gemini-3.8-flash on the MedicineMan Vertex wallet. Never print the key."""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, r"V:\A\Ai\COSMOS\tokenctr")
from cosmos_pay_vertex_rail import VertexAIRail, VertexRailError  # noqa: E402

PACK = Path(r"V:\A\Ai\COSMOS\work_orders\ccr\hero_dailyscar_gf38")
DIGEST = Path(r"V:\A\Ai\COSMOS\work_orders\ccr\hero_dailyscar\DIGEST.md")
OUT = PACK / "EDITORIAL.md"
KEYISH = re.compile(r"(?i)(key=|AIza[0-9A-Za-z_\-]{8}|AQ\.[0-9A-Za-z_\-]{8})")


def safe(text: str) -> str:
    return KEYISH.sub("[redacted]", text)


def main() -> int:
    wrap = (PACK / "WRAP.md").read_text(encoding="utf-8")
    task = (PACK / "TASK.md").read_text(encoding="utf-8")
    digest = DIGEST.read_text(encoding="utf-8") if DIGEST.is_file() else ""
    if len(digest) > 14000:
        digest = digest[:14000] + "\n[truncated]\n"
    rail = VertexAIRail()
    try:
        res, pin, pout = rail.chat(
            {
                "model": "gemini-3.8-flash",
                "max_tokens": 4096,
                "temperature": 0.4,
                "messages": [
                    {"role": "system", "content": wrap},
                    {"role": "user", "content": task + "\n\n" + digest},
                ],
            },
            timeout=120,
        )
    except VertexRailError as e:
        print("FAIL", safe(str(e))[:180])
        return 2
    text = res["choices"][0]["message"]["content"]
    model = res.get("model") or ""
    OUT.write_text(text, encoding="utf-8", newline="\n")
    print(f"OK model={model} in={pin} out={pout} chars={len(text)} file=EDITORIAL.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
