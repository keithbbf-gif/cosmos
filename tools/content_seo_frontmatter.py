#!/usr/bin/env python3
"""Add description / image / image_alt YAML to staged content drafts (idempotent)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ERA_IMAGE = {
    "asilomar": (
        "assets/svg/dual-asilomar-1975-2017.svg",
        "Comparison of the 1975 DNA Asilomar conference and the 2017 Beneficial AI principles meeting.",
    ),
    "fhi": (
        "assets/svg/four-spine-overview.svg",
        "Four-spine overview of public AI safety discourse drafts (Asilomar, FHI, charter era, EU Act).",
    ),
    "openai-charter": (
        "assets/svg/four-spine-overview.svg",
        "Four-spine overview of public AI safety discourse drafts (Asilomar, FHI, charter era, EU Act).",
    ),
    "eu-ai-act": (
        "assets/svg/eu-legislative-rail-2019-2024.svg",
        "EU AI Act legislative rail from HLEG (2019) through formal adoption and EIF dates.",
    ),
    "neighboring": (
        "assets/svg/spine-asilomar-to-eu-ai-act.svg",
        "Timeline schematic of public AI safety milestones from 1975 Asilomar through the EU AI Act.",
    ),
    "method": (
        "assets/svg/four-spine-overview.svg",
        "Four-spine reading map for the public AI safety discourse draft set.",
    ),
}

COMPUTE_DEFAULT = (
    "assets/svg/spine-gpu-public-history.svg",
    "Timeline schematic of selected public GPU, CUDA, and TPU milestones from 1999 through 2024.",
)

COMPUTE_SPECIAL_IMAGE = {
    "01-when-nvidia-named-the-gpu.md": (
        "assets/svg/geforce256-gpu-naming-1999.svg",
        "1999 GeForce 256 launch when NVIDIA coined the term graphics processing unit.",
    ),
    "07-november-8-2006-cuda-gets-a-name.md": (
        "assets/svg/cuda-g80-2006-hinge.svg",
        "November 8, 2006 CUDA and GeForce 8800 G80 launch on the same calendar day.",
    ),
    "12-two-gtx-580s-alexnet.md": (
        "assets/svg/alexnet-two-gtx580.svg",
        "Public lore diagram of AlexNet running on two GTX 580 GPUs in 2012.",
    ),
    "15-volta-tensor-core.md": (
        "assets/svg/volta-tensor-core-2017.svg",
        "Volta-generation tensor cores for mixed-precision matrix multiply.",
    ),
    "18-hopper-transformer-factory.md": (
        "assets/svg/hopper-transformer-engine-2022.svg",
        "Hopper generation Transformer Engine and datacenter messaging.",
    ),
    "34-tpu-v1-board-in-a-datacenter.md": (
        "assets/svg/tpu-v1-datacenter-2016.svg",
        "Google TPU v1 inference accelerator in the datacenter (2016 public story).",
    ),
}

SPECIAL_IMAGE = {
    "34-risk-pyramid-public.md": (
        "assets/svg/eu-risk-pyramid-public.svg",
        "Four-tier EU AI Act risk pyramid: unacceptable, high, limited, and minimal risk (public explainer).",
    ),
    "37-oj-july-eif-august-2024.md": (
        "assets/svg/eu-legislative-rail-2019-2024.svg",
        "EU AI Act legislative rail with OJ publication and entry-into-force dates.",
    ),
}


def split_frontmatter(text: str) -> tuple[str | None, str]:
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return None, text
    return text[4:end], text[end + 5 :]


def first_description_paragraph(body: str) -> str:
    for line in body.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("<"):
            continue
        if line.startswith("**") and line.endswith("**") and len(line) < 80:
            continue
        plain = re.sub(r"\*+", "", line)
        plain = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", plain)
        plain = re.sub(r"`([^`]+)`", r"\1", plain)
        if len(plain) < 40:
            continue
        if len(plain) <= 158:
            return plain
        cut = plain[:158].rsplit(" ", 1)[0]
        return cut + "…"
    title = ""
    for line in body.splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
            break
    return f"Staged educational draft on public AI safety discourse: {title}."[:158]


def yaml_get(fm: str, key: str) -> str | None:
    m = re.search(rf"^{key}:\s*(.+)$", fm, re.MULTILINE)
    if not m:
        return None
    val = m.group(1).strip()
    if val.startswith('"') and val.endswith('"'):
        return val[1:-1]
    return val


def yaml_has(fm: str, key: str) -> bool:
    return re.search(rf"^{key}:", fm, re.MULTILINE) is not None


def inject_fields(fm: str, fields: dict[str, str]) -> str:
    lines = fm.splitlines()
    insert_at = len(lines)
    for i, line in enumerate(lines):
        if line.startswith("sources:"):
            insert_at = i
            break
    new_lines = []
    for key, val in fields.items():
        if yaml_has(fm, key):
            continue
        escaped = val.replace('"', '\\"')
        new_lines.append(f'{key}: "{escaped}"')
    if not new_lines:
        return fm
    return "\n".join(lines[:insert_at] + new_lines + lines[insert_at:])


def process_file(path: Path, series: str) -> bool:
    text = path.read_text(encoding="utf-8")
    fm, body = split_frontmatter(text)
    if fm is None:
        return False
    if yaml_has(fm, "description") and yaml_has(fm, "image"):
        return False
    slug_file = path.name
    if series == "ai-compute-chip-magazine":
        if slug_file in COMPUTE_SPECIAL_IMAGE:
            image, image_alt = COMPUTE_SPECIAL_IMAGE[slug_file]
        else:
            image, image_alt = COMPUTE_DEFAULT
        title = yaml_get(fm, "title") or path.stem
        desc = yaml_get(fm, "dek") or first_description_paragraph(body)
        if not desc:
            desc = f"Public GPU/CUDA/TPU history: {title}."
    else:
        era = yaml_get(fm, "era") or "method"
        if slug_file in SPECIAL_IMAGE:
            image, image_alt = SPECIAL_IMAGE[slug_file]
        else:
            image, image_alt = ERA_IMAGE.get(era, ERA_IMAGE["method"])
        title = yaml_get(fm, "title") or path.stem
        desc = first_description_paragraph(body)
        if not desc:
            desc = f"Public-record recap: {title}."
    fields = {
        "description": desc,
        "image": image,
        "image_alt": image_alt if image_alt else title,
    }
    new_fm = inject_fields(fm, fields)
    if new_fm == fm:
        return False
    path.write_text(f"---\n{new_fm}\n---\n{body}", encoding="utf-8")
    return True


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else "content/ai-safety-public-discourse")
    series = root.name
    changed = 0
    skip = {"README.md", "RIGHTS.md", "MANIFEST.md", "SOURCES.md", "INDEX.md", "EDITOR_REPORT.md"}
    for path in sorted(root.glob("*.md")):
        if path.name in skip:
            continue
        if process_file(path, series):
            changed += 1
    print(f"updated {changed} files under {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
