#!/usr/bin/env python3
"""Emit pack_data.py from staged markdown front matter + editorial anchors."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent / "pack_data.py"

FM = re.compile(r"^---\n(.*?)\n---\n", re.S)
YEAR = re.compile(r"\b(19|20)\d{2}\b")

PACK = "ai-compute-chip-magazine"
GRAPHICS_AGENT = "v1"

# architecture-diagram.svg template key per slug
CHART: dict[str, str] = {
    "01-when-nvidia-named-the-gpu": "graphics_pipeline",
    "02-voodoo-and-the-card-that-vanished": "graphics_pipeline",
    "03-ati-radeon-the-other-house": "graphics_pipeline",
    "04-shader-algebra-in-a-pixel-pipe": "shader_stages",
    "05-brook-for-gpus": "software_stack",
    "06-ian-buck-walks-into-santa-clara": "software_stack",
    "07-november-8-2006-cuda-gets-a-name": "software_stack",
    "08-g80-the-unified-shader": "unified_shader",
    "09-tesla-compute-without-a-monitor": "compute_sku",
    "10-fermi-caches-and-ecc": "cache_hierarchy",
    "11-supercomputers-notice-the-gpu": "cluster_scale",
    "12-two-gtx-580s-alexnet": "dual_gpu",
    "13-cudnn-the-library-that-hid-the-hardware": "software_stack",
    "14-pascal-p100-hbm2-nvlink": "memory_interconnect",
    "15-volta-tensor-core": "tensor_unit",
    "16-turing-rays-and-consumer-tensors": "tensor_unit",
    "17-ampere-a100-mig": "partition_sku",
    "18-hopper-transformer-factory": "tensor_unit",
    "19-blackwell-the-rack-is-the-chip": "rack_scale",
    "20-grids-blocks-threads": "cuda_hierarchy",
    "21-the-warp-thirty-two-threads": "cuda_hierarchy",
    "22-occupancy-is-not-performance": "cuda_hierarchy",
    "23-shared-memory-scratchpad": "memory_hierarchy",
    "24-unified-memory-hid-the-copies": "memory_hierarchy",
    "25-cuda-graphs-launch-tax": "launch_overhead",
    "26-mixed-precision-bargain": "precision_ladder",
    "27-nccl-all-reduce": "collective_ring",
    "28-nvlink-nvswitch-midplane": "memory_interconnect",
    "29-dgx-1-eight-gpus": "cluster_scale",
    "30-the-cuda-moat": "ecosystem_moat",
    "31-opencl-the-standard-that-lost": "software_stack",
    "32-amd-firestream-rocm-hip": "software_stack",
    "33-intel-third-chair": "vendor_chair",
    "34-tpu-v1-board-in-a-datacenter": "systolic_board",
    "35-systolic-arrays-kung-to-jouppi": "systolic_board",
    "36-tpu-pods-the-network-is-the-machine": "cluster_scale",
    "37-xla-jax-compiling-for-a-chip": "compiler_stack",
    "38-why-tpus-and-gpus-coexist": "vendor_chair",
    "39-memory-bandwidth-ate-the-decade": "memory_hierarchy",
    "40-hbm-stacking-dram": "memory_interconnect",
    "41-power-water-building-as-limit": "datacenter_limit",
    "42-training-vs-inference-silicon": "train_infer_split",
    "43-the-sku-wall": "sku_ladder",
    "44-bitcoin-gamers-commodity": "market_demand",
    "45-what-a-flop-stopped-meaning": "flop_meter",
}

ANCHORS: dict[str, list[tuple[str, str]]] = {
    "01-when-nvidia-named-the-gpu": [
        ("Aug 1999", "GeForce 256 launch; GPU coined"),
        ("Oct 1999", "SDR cards ship to retail"),
        ("2006", "CUDA names a C-on-GPU platform"),
        ("now", "GPU is a class, not a monitor"),
    ],
    "07-november-8-2006-cuda-gets-a-name": [
        ("Nov 2006", "CUDA + GeForce 8800 announced"),
        ("2007", "Public CUDA SDK and docs trail"),
        ("2012", "Consumer cards in ImageNet training"),
        ("now", "Platform habit outlives any one chip"),
    ],
    "12-two-gtx-580s-alexnet": [
        ("2012", "AlexNet paper: two GTX 580s, ~6 days"),
        ("2012", "ILSVRC top-5 error step change"),
        ("2014", "cuDNN hides conv details"),
        ("now", "Bedroom scale vs datacenter scale"),
    ],
    "34-tpu-v1-board-in-a-datacenter": [
        ("2016", "TPU v1 paper at ISCA"),
        ("2017", "Pods and cloud inference story"),
        ("2018", "TPU v3 public discourse"),
        ("now", "ASIC line beside general GPUs"),
    ],
    "29-dgx-1-eight-gpus": [
        ("Apr 2016", "DGX-1 announced with P100"),
        ("2017", "Eight-GPU box as category"),
        ("2020", "A100 generation refresh"),
        ("now", "Appliance SKU, not a hobby rack"),
    ],
    "45-what-a-flop-stopped-meaning": [
        ("1999", "Graphics peak FLOPs as marketing"),
        ("2012", "Convnets care about memory too"),
        ("2020", "Sparse / tensor FLOPs multiply"),
        ("now", "Read the benchmark contract"),
    ],
}

# slug -> optional Wikimedia product photo (see fetch_photos.py)
PHOTO: dict[str, str] = {
    "01-when-nvidia-named-the-gpu": "geforce-256.jpg",
    "02-voodoo-and-the-card-that-vanished": "3dfx-voodoo2.jpg",
    "03-ati-radeon-the-other-house": "ati-radeon-9700-pro.png",
    "07-november-8-2006-cuda-gets-a-name": "geforce-8800-gtx-board.jpg",
    "08-g80-the-unified-shader": "geforce-8800-gtx-board.jpg",
    "09-tesla-compute-without-a-monitor": "tesla-gpu-cluster.jpg",
    "12-two-gtx-580s-alexnet": "gtx-580-die.jpg",
    "29-dgx-1-eight-gpus": "nvidia-dgx-front.jpg",
    "34-tpu-v1-board-in-a-datacenter": "tpu-v4.png",
}


def parse_fm(text: str) -> dict[str, str]:
    m = FM.match(text)
    if not m:
        return {}
    out: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip().strip('"')
    return out


def fallback_anchors(slug: str, title: str, body: str) -> list[tuple[str, str]]:
    if slug in ANCHORS:
        return ANCHORS[slug]
    years = sorted(set(YEAR.findall(body)))
    # YEAR.findall returns prefix groups; fix by re-searching
    ys = sorted(set(m.group(0) for m in YEAR.finditer(body)))[:3]
    anchors: list[tuple[str, str]] = []
    if ys:
        anchors.append((ys[0], f"{title[:52]} enters public record"))
    if len(ys) > 1:
        anchors.append((ys[1], "Architecture or software sequel in trade press"))
    if len(ys) > 2:
        anchors.append((ys[2], "Datacenter or consumer SKU crossover"))
    anchors.append(("now", "Cross-check dates in essay Sources"))
    while len(anchors) < 3:
        anchors.insert(1, ("era", "Verify milestone years in prose"))
    return anchors[:4]


def chart_for(slug: str) -> str:
    return CHART.get(slug, "graphics_pipeline")


def main() -> None:
    articles: list[dict] = []
    for path in sorted(ROOT.glob("[0-9][0-9]-*.md")):
        text = path.read_text(encoding="utf-8")
        fm = parse_fm(text)
        slug = fm.get("slug") or path.stem
        title = fm.get("title") or path.stem
        body = text.split("---", 2)[-1] if text.startswith("---") else text
        art = {
            "slug": slug,
            "file": path.name,
            "title": title,
            "chart": chart_for(slug),
            "anchors": fallback_anchors(slug, title, body),
        }
        if slug in PHOTO:
            art["photo"] = PHOTO[slug]
        articles.append(art)

    lines = [
        '"""Pack metadata for ai-compute-chip-magazine graphics. Auto-built; re-run build_pack_data.py."""',
        "",
        "from __future__ import annotations",
        "",
        f'PACK = "{PACK}"',
        f'GRAPHICS_AGENT = "{GRAPHICS_AGENT}"',
        "",
        "ARTICLES: list[dict] = [",
    ]
    for a in articles:
        lines.append("    {")
        for key in ("slug", "file", "title", "chart"):
            lines.append(f'        "{key}": {a[key]!r},')
        lines.append(f'        "anchors": {a["anchors"]!r},')
        if "photo" in a:
            lines.append(f'        "photo": {a["photo"]!r},')
        lines.append("    },")
    lines.append("]")
    lines.append("")
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT} ({len(articles)} articles)")


if __name__ == "__main__":
    main()
