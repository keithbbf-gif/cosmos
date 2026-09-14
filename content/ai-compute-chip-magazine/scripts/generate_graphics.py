#!/usr/bin/env python3
"""Original SVG timelines and architecture diagrams for ai-compute-chip-magazine."""

from __future__ import annotations

import html
from pathlib import Path

from pack_data import ARTICLES, PACK

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"

PAPER = "#f4f1ea"
INK = "#1c2430"
MUTED = "#5a6470"
RULE = "#c5c9cf"
ACCENT = "#1a5f7a"
ACCENT2 = "#8b4518"
PANEL = "#e8e4dc"
CHIP = "#2d6a4f"


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def header(title: str, sub: str, w: int = 760, h: int = 460) -> list[str]:
    return [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc">',
        f'  <title id="title">{esc(title)}</title>',
        f'  <desc id="desc">{esc(sub)}</desc>',
        f'  <rect width="100%" height="100%" fill="{PAPER}"/>',
        f'  <text x="24" y="36" font-family="Source Serif 4, Georgia, serif" font-size="20" font-weight="600" fill="{INK}">{esc(title[:72])}</text>',
        f'  <text x="24" y="58" font-family="IBM Plex Sans, system-ui, sans-serif" font-size="12" fill="{MUTED}">{esc(sub)}</text>',
    ]


def footer(h: int = 460) -> str:
    return (
        f'  <text x="24" y="{h - 14}" font-family="IBM Plex Sans, system-ui, sans-serif" '
        f'font-size="11" fill="{MUTED}">Original magazine illustration — public facts only. {PACK}, staged.</text>\n</svg>\n'
    )


def timeline_svg(art: dict) -> str:
    title = f"{art['title']} — timeline"
    sub = "Dated anchors from the public record. Verify years in the essay Sources."
    lines = header(title, sub)
    y0 = 80
    for i, (when, what) in enumerate(art["anchors"]):
        y = y0 + i * 78
        if i:
            lines.append(f'  <line x1="118" y1="{y - 50}" x2="118" y2="{y + 8}" stroke="{RULE}" stroke-width="2"/>')
        fill = ACCENT if i % 2 == 0 else PANEL
        fg = PAPER if i % 2 == 0 else INK
        lines.append(f'  <rect x="24" y="{y}" width="96" height="28" rx="4" fill="{fill}" stroke="{RULE}"/>')
        lines.append(
            f'  <text x="72" y="{y + 19}" text-anchor="middle" font-family="IBM Plex Sans, system-ui, sans-serif" '
            f'font-size="11" font-weight="600" fill="{fg}">{esc(when)}</text>'
        )
        lines.append(
            f'  <text x="136" y="{y + 14}" font-family="IBM Plex Sans, system-ui, sans-serif" font-size="14" '
            f'font-weight="600" fill="{INK}">{esc(what[:70])}</text>'
        )
        lines.append(
            f'  <text x="136" y="{y + 32}" font-family="IBM Plex Sans, system-ui, sans-serif" font-size="12" fill="{MUTED}">'
            f"Not a live benchmark — calendar spine only.</text>"
        )
    lines.append(footer())
    return "\n".join(lines)


def panel(x: float, y: float, w: float, h: float, label: str, fill: str = PANEL) -> list[str]:
    return [
        f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{fill}" stroke="{RULE}"/>',
        f'  <text x="{x + w/2}" y="{y + h/2 + 5}" text-anchor="middle" font-family="IBM Plex Sans, system-ui, sans-serif" '
        f'font-size="12" fill="{INK}">{esc(label)}</text>',
    ]


def arrow(x1: float, y1: float, x2: float, y2: float) -> str:
    return (
        f'  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{ACCENT}" stroke-width="2" '
        f'marker-end="url(#ah)"/>'
    )


def diagram_svg(art: dict) -> str:
    kind = art["chart"]
    title = f"{art['title']} — diagram"
    sub = "Illustrative architecture shape for this article. Not a vendor block diagram."
    lines = header(title, sub)
    lines.append(
        '  <defs><marker id="ah" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">'
        f'<path d="M0,0 L6,3 L0,6 Z" fill="{ACCENT}"/></marker></defs>'
    )
    lines.append(f'  <rect x="24" y="72" width="712" height="360" fill="{PANEL}" stroke="{RULE}" rx="4"/>')

    if kind == "graphics_pipeline":
        stages = ["vertices", "raster", "shaders", "framebuffer"]
        for i, s in enumerate(stages):
            lines.extend(panel(48 + i * 168, 140, 140, 56, s, PAPER if i % 2 else PANEL))
            if i < len(stages) - 1:
                lines.append(arrow(188 + i * 168, 168, 216 + i * 168, 168))
        lines.append(
            f'  <text x="36" y="400" font-family="IBM Plex Sans, system-ui, sans-serif" font-size="12" fill="{MUTED}">'
            f"3D pipeline era — compute arrives later in the same silicon.</text>"
        )
    elif kind == "shader_stages":
        for i, s in enumerate(["VS", "GS", "PS", "CS slot"]):
            lines.extend(panel(60 + i * 155, 130, 130, 80, s, ACCENT if i == 3 else PANEL))
        lines.append(
            f'  <text x="36" y="400" font-family="IBM Plex Sans, system-ui, sans-serif" font-size="12" fill="{MUTED}">'
            f"Programmable stages — algebra moves into the pixel pipe.</text>"
        )
    elif kind == "software_stack":
        stack = ["C / Python", "CUDA / runtime", "driver", "GPU"]
        for i, s in enumerate(stack):
            lines.extend(panel(200, 100 + i * 62, 360, 48, s, PAPER if i % 2 else PANEL))
        if len(stack) > 1:
            lines.append(arrow(380, 148, 380, 162))
            lines.append(arrow(380, 210, 380, 224))
            lines.append(arrow(380, 272, 380, 286))
    elif kind == "unified_shader":
        lines.extend(panel(80, 130, 520, 100, "unified shader cores (pixels or compute)", CHIP))
        lines.extend(panel(80, 260, 240, 56, "command queue", PAPER))
        lines.extend(panel(360, 260, 240, 56, "same ISA", ACCENT))
    elif kind == "compute_sku":
        lines.extend(panel(60, 130, 280, 120, "no display outputs", PANEL))
        lines.extend(panel(400, 130, 280, 120, "ECC / datacenter SKU", PAPER))
    elif kind == "cache_hierarchy":
        for i, s in enumerate(["L1 / shared", "L2", "device DRAM", "host RAM"]):
            lines.extend(panel(120, 95 + i * 58, 480, 44, s, PAPER if i % 2 else PANEL))
    elif kind == "cluster_scale":
        for i in range(8):
            col, row = i % 4, i // 4
            lines.extend(panel(48 + col * 168, 110 + row * 72, 140, 48, f"GPU {i+1}", ACCENT if i == 0 else PANEL))
        lines.extend(panel(260, 300, 240, 48, "chassis / pod", PAPER))
    elif kind == "dual_gpu":
        lines.extend(panel(80, 140, 260, 100, "GPU 0 — model shard", ACCENT))
        lines.extend(panel(420, 140, 260, 100, "GPU 1 — model shard", ACCENT))
        lines.append(arrow(340, 190, 420, 190))
        lines.extend(panel(200, 280, 360, 48, "PCIe / NVLink era dependent", PANEL))
    elif kind == "memory_interconnect":
        lines.extend(panel(48, 120, 200, 80, "HBM stack", CHIP))
        lines.extend(panel(300, 120, 200, 80, "GPU die", PANEL))
        lines.extend(panel(552, 120, 160, 80, "NVLink / PCIe", PAPER))
        lines.append(arrow(248, 160, 300, 160))
        lines.append(arrow(500, 160, 552, 160))
    elif kind == "tensor_unit":
        lines.extend(panel(48, 120, 280, 72, "FP32 CUDA cores", PANEL))
        lines.extend(panel(360, 120, 340, 72, "matrix multiply unit", ACCENT))
        lines.extend(panel(48, 230, 652, 56, "tensor op fuses dot products", PAPER))
    elif kind == "partition_sku":
        lines.extend(panel(48, 120, 640, 56, "physical GPU", PANEL))
        for i in range(3):
            lines.extend(panel(48 + i * 210, 200, 190, 48, f"MIG slice {i+1}", PAPER if i else ACCENT))
    elif kind == "rack_scale":
        lines.extend(panel(48, 100, 200, 280, "rack U", PANEL))
        for i in range(4):
            lines.extend(panel(280, 110 + i * 62, 400, 48, f"tray / module {i+1}", PAPER if i % 2 else PANEL))
    elif kind in ("cuda_hierarchy",):
        lines.extend(panel(200, 100, 360, 44, "grid", PANEL))
        lines.extend(panel(120, 170, 520, 44, "block", PAPER))
        lines.extend(panel(80, 240, 600, 44, "thread (×N)", ACCENT))
    elif kind == "memory_hierarchy":
        lines.extend(panel(48, 110, 300, 56, "registers / shared", PANEL))
        lines.extend(panel(400, 110, 300, 56, "L2", PANEL))
        lines.extend(panel(48, 200, 652, 56, "global DRAM — bandwidth bound", PAPER))
    elif kind == "launch_overhead":
        lines.extend(panel(48, 120, 200, 56, "host setup", PANEL))
        lines.append(arrow(248, 148, 300, 148))
        lines.extend(panel(300, 120, 200, 56, "kernel launch", ACCENT2))
        lines.extend(panel(520, 120, 180, 56, "graph replay", ACCENT))
    elif kind == "precision_ladder":
        for i, p in enumerate(["FP64", "FP32", "FP16", "INT8"]):
            lines.extend(panel(48 + i * 168, 150, 140, 56, p, ACCENT if p == "FP16" else PANEL))
    elif kind == "collective_ring":
        pts = [(120, 200), (320, 120), (520, 200), (320, 280)]
        for i, (x, y) in enumerate(pts):
            lines.extend(panel(x - 50, y - 24, 100, 48, f"rank {i}", PANEL))
        for i in range(4):
            x1, y1 = pts[i]
            x2, y2 = pts[(i + 1) % 4]
            lines.append(arrow(x1 + 40, y1, x2 - 40, y2))
        lines.extend(panel(260, 300, 240, 40, "all-reduce", PAPER))
    elif kind == "ecosystem_moat":
        for i, s in enumerate(["CUDA", "cuBLAS", "cuDNN", "NCCL", "apps"]):
            lines.extend(panel(48, 100 + i * 52, 620, 40, s, ACCENT if i == 0 else PANEL))
    elif kind == "vendor_chair":
        for i, s in enumerate(["NVIDIA", "AMD", "Intel", "Google TPU"]):
            lines.extend(panel(48 + i * 168, 160, 140, 80, s, PANEL if i else ACCENT))
    elif kind == "systolic_board":
        for row in range(4):
            for col in range(8):
                lines.append(
                    f'  <rect x="{48+col*78}" y="{110+row*48}" width="70" height="40" rx="3" fill="{CHIP if (row+col)%3==0 else PANEL}" stroke="{RULE}"/>'
                )
        lines.extend(panel(48, 320, 620, 40, "systolic mesh — data flows through MAC grid", PAPER))
    elif kind == "compiler_stack":
        for i, s in enumerate(["Python / JAX", "XLA HLO", "fusion", "TPU / GPU backend"]):
            lines.extend(panel(160, 100 + i * 58, 440, 44, s, PAPER if i % 2 else PANEL))
    elif kind == "datacenter_limit":
        lines.extend(panel(48, 120, 280, 72, "chip TDP", PANEL))
        lines.extend(panel(400, 120, 280, 72, "rack kW", PAPER))
        lines.extend(panel(200, 240, 360, 56, "facility water / power", ACCENT2))
    elif kind == "train_infer_split":
        lines.extend(panel(48, 130, 300, 100, "training — wide, noisy", ACCENT))
        lines.extend(panel(412, 130, 300, 100, "inference — narrow, SLA", PANEL))
    elif kind == "sku_ladder":
        labels = ["GeForce", "Quadro", "Tesla / DC", "cloud SKU"]
        for i, s in enumerate(labels):
            lines.extend(panel(48, 110 + i * 58, 620, 44, s, ACCENT if i == 3 else PANEL))
    elif kind == "market_demand":
        lines.extend(panel(48, 130, 260, 80, "gamers", PANEL))
        lines.extend(panel(400, 130, 260, 80, "coin miners", ACCENT2))
        lines.extend(panel(200, 260, 360, 48, "same silicon, different queue", PAPER))
    elif kind == "flop_meter":
        lines.extend(panel(48, 140, 200, 56, "peak FLOPs", PANEL))
        lines.append(arrow(248, 168, 320, 168))
        lines.extend(panel(320, 140, 200, 56, "useful work?", ACCENT))
        lines.extend(panel(540, 140, 160, 56, "memory", PAPER))
    else:
        lines.extend(panel(200, 180, 360, 80, kind, PANEL))

    lines.append(footer())
    return "\n".join(lines)


def main() -> None:
    for art in ARTICLES:
        slug_dir = ASSETS / art["slug"]
        slug_dir.mkdir(parents=True, exist_ok=True)
        (slug_dir / "historical-timeline.svg").write_text(timeline_svg(art), encoding="utf-8")
        (slug_dir / "architecture-diagram.svg").write_text(diagram_svg(art), encoding="utf-8")
    print(f"generated SVGs for {len(ARTICLES)} articles under {ASSETS}")


if __name__ == "__main__":
    main()
