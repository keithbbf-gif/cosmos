#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""F-28: file the 15 unmapped HANDS stems as unverified COMPETENCY nodes.

possessed=false rating=0. Does not invent ratings. Does not add the new
ids to router.nodes_order (the live six stay the routing set).

    py -3.14 builds/probe/_apply_f28_rows.py
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
TOML = REPO / "docs" / "COMPETENCY.toml"
STAGE = (REPO / "docs" / "_delme" /
         "predispose_competency_f28_20260831T145400Z")
sys.path.insert(0, str(HERE))
from cosmos_newai_scout import inventory_from_competency, inventory_from_hands, norm  # noqa: E402

TASK_TYPES = [
    "code-build",
    "code-review-critique",
    "web-research",
    "docs-authoring",
    "DOM-automation",
    "long-context-reasoning",
    "bulk-structured-extraction",
    "vendor-plural-critique",
]

# id matches HANDS stem via norm() (Aider <-> AIDER, BrowserUse <-> BROWSER USE).
# family is the vendor token from the HANDS file, never "dom" (would steal
# DOM-automation ties). already_live names the routing node that already
# covers the vendor when one exists — this row still maps the HANDS stem.
ROWS = (
    ("Aider", "aider", "Aider", "AIDER_HANDS.md", "CLI",
     "Apache-2.0 terminal pair-programmer (BYO key); candidate backlog"),
    ("Anthropic", "anthropic", "Anthropic Claude", "ANTHROPIC_HANDS.md", "CLI",
     "Claude platform hands; live routing node is not this row (CC/claude-cli)"),
    ("BrowserUse", "browser-use", "Browser-Use", "BROWSER_USE_HANDS.md", "DOM",
     "MIT Chromium agent; candidate backlog, not the live DOM rail"),
    ("Firecrawl", "firecrawl", "Firecrawl", "FIRECRAWL_HANDS.md", "API",
     "web-context scrape/crawl/map; live rail is firecrawl-web, not this row"),
    ("GCloud", "google-cloud", "gcloud CLI", "GCLOUD_HANDS.md", "CLI",
     "gcloud groups against the Vertex wallet; live routing node is GEM"),
    ("GitHub", "github", "GitHub", "GITHUB_HANDS.md", "CLI",
     "gh / REST / MCP forge; live rail is github-forge, not a routing node"),
    ("GitLab", "gitlab", "GitLab", "GITLAB_HANDS.md", "CLI",
     "glab / CI forge; live rail is gitlab-forge, not a routing node"),
    ("GoogleGemini", "google", "Google Gemini", "GOOGLE_GEMINI_HANDS.md", "API",
     "Gemini/Vertex hands file; live routing node is GEM"),
    ("Groq", "groq", "GroqCloud", "GROQ_HANDS.md", "API",
     "LPU inference (not xAI Grok); WAVE C operator install/key"),
    ("MCPReferenceServers", "mcp", "MCP reference servers",
     "MCP_REFERENCE_SERVERS_HANDS.md", "MCP",
     "educational reference implementations, not production-ready"),
    ("MicrosoftCopilot", "microsoft", "Microsoft Copilot",
     "MICROSOFT_COPILOT_HANDS.md", "API",
     "M365/Graph/Studio hands; no live Copilot rail"),
    ("Ollama", "ollama", "Ollama", "OLLAMA_HANDS.md", "CLI",
     "local open-model runtime; WAVE C operator install"),
    ("OpenAI", "openai", "OpenAI Platform", "OPENAI_HANDS.md", "API",
     "Platform + Codex hands file; live routing node is OA"),
    ("PlaywrightMCP", "playwright", "Playwright MCP",
     "PLAYWRIGHT_MCP_HANDS.md", "MCP",
     "Microsoft a11y-tree MCP; live routing node is DOM"),
    ("XaiGrok", "xai", "xAI Grok", "XAI_GROK_HANDS.md", "API",
     "xAI API + Grok Build + Grok Bot hands; live routing nodes are G46/SGH"),
)


def _census(toml_text: str, repo: Path) -> dict:
    nodes = sorted(inventory_from_competency(toml_text))
    hands = sorted(inventory_from_hands(repo))
    node_keys = {norm(n) for n in nodes}
    seen: set[str] = set()
    unmapped = []
    for h in hands:
        k = norm(h)
        if k in seen or k in node_keys:
            continue
        seen.add(k)
        unmapped.append(h)
    return {
        "schema": "cosmos-f28-census/1",
        "toml_bytes": len(toml_text.encode("utf-8")),
        "node_count": len(nodes),
        "nodes": nodes,
        "hands_stems": hands,
        "unmapped_hands": unmapped,
        "unmapped_count": len(unmapped),
        "pin": (
            "tests/test_competency.py live_six_nodes SUPERSET "
            "required_six <= live_nodes"
        ),
        "live_six_nodes_pin_would_break_if_we_add": False,
    }


def _block() -> str:
    lines = [
        "",
        "# --- F-28 unverified HANDS stems (filed 2026-08-31T1454Z) ---",
        "# possessed=false rating=0. Ratings are NOT invented. These rows",
        "# map docs/research/*_HANDS.md stems into [nodes.*] so the census",
        "# is not 15-unmapped. They are NOT live routing nodes (absent from",
        "# router.nodes_order; pick() skips possessed!=true and rating<=0).",
        "# A later SGH pass may rate them; this pass will not.",
    ]
    for nid, family, product, hands, reach, blurb in ROWS:
        src = (
            f"docs/research/{hands} — unverified (possessed=false rating=0); "
            f"not a live routing node. {blurb}"
        )
        lines += [
            "",
            f"[nodes.{nid}]",
            f'id = "{nid}"',
            f'family = "{family}"',
            f'product = "{product}"',
            'model = "unverified"',
            "context_tokens = 0",
            'cosmos_lane = "unverified — not a live routing node"',
            f'reach = "{reach}"',
            f'hands = "{src}"',
        ]
        for task in TASK_TYPES:
            lines += [
                "",
                f"[skills.{task}.{nid}]",
                "possessed = false",
                "rating = 0",
                f'source = "{src}"',
            ]
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    text = TOML.read_text(encoding="utf-8")
    STAGE.mkdir(parents=True, exist_ok=True)
    staged = STAGE / "COMPETENCY.toml"
    if not staged.is_file():
        shutil.copy2(TOML, staged)
    old = _census(staged.read_text(encoding="utf-8"), REPO)
    bite = HERE / "_bite_f28_unmapped.json"
    old["why_not_filed"] = (
        "STAGED INCUMBENT before F-28 filing. 15 HANDS stems unmapped. "
        "The exact-set pin was already a SUPERSET (2026-08-31T14:36Z); "
        "this fence can file possessed=false rating=0 rows."
    )
    bite.write_text(json.dumps(old, indent=1) + "\n", encoding="utf-8")

    if "[nodes.Aider]" in text:
        new_text = text
        rec = {"already_filed": True}
    else:
        new_text = text.rstrip() + "\n" + _block()
        TOML.write_text(new_text, encoding="utf-8")
        rec = {"already_filed": False}

    new = _census(new_text, REPO)
    new["filed_ids"] = [r[0] for r in ROWS]
    new["staged"] = str(staged)
    new["why_not_filed"] = (
        "filed 2026-08-31T1454Z possessed=false rating=0 HANDS-cited source; "
        "ratings not invented; router.nodes_order still the live six"
    )
    (HERE / "_f28_hands_vs_nodes.json").write_text(
        json.dumps(new, indent=1) + "\n", encoding="utf-8")
    rec.update({
        "ok": new["unmapped_count"] == 0 and old["unmapped_count"] == 15,
        "old_unmapped_count": old["unmapped_count"],
        "new_unmapped_count": new["unmapped_count"],
        "old_node_count": old["node_count"],
        "new_node_count": new["node_count"],
        "new_nodes": new["nodes"],
        "toml_bytes": new["toml_bytes"],
        "staged": str(staged),
    })
    print(json.dumps(rec, indent=2))
    return 0 if rec["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
