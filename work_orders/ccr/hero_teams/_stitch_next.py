import re
from pathlib import Path

site = Path(r"V:\A\Ai\COSMOS\work_orders\ccr\hero_lmnator_muse\site")
teams = Path(r"V:\A\Ai\COSMOS\work_orders\ccr\hero_teams")

raw = (teams / "argon" / "NEXT.js").read_text(encoding="utf-8")
blocks = re.findall(r"window\.LMN_PACK\['c\d+'\] = (\{.*?\n\});", raw, re.S)
out = "window.LMN_PACK = window.LMN_PACK || [];\nwindow.LMN_PACK.push(\n" + ",\n".join(blocks) + "\n);\n"
(site / "pack-next-argon.js").write_text(out, encoding="utf-8")
(site / "pack-next-grok.js").write_text((teams / "grok47" / "NEXT.js").read_text(encoding="utf-8"), encoding="utf-8")

luna = (teams / "luna6" / "NEXT.txt").read_text(encoding="utf-8")
seps = list(re.finditer(r"\n  \},\n", luna))
if seps:
    luna = luna[: seps[-1].end() - 1]
    if "push(" in luna and not luna.rstrip().endswith(");"):
        luna = luna.rstrip().rstrip(",") + "\n);\n"
luna = luna.replace("inspired_by", "inspired").replace("nearMiss", "better").replace("near_miss", "better")
(site / "pack-next-luna.js").write_text(luna, encoding="utf-8")

mx = (teams / "luna6max" / "NEXT.txt").read_text(encoding="utf-8")
mx = mx.replace("inspired_by", "inspired").replace("nearMiss", "better").replace("near_miss", "better")
(site / "pack-next-lunamax.js").write_text(mx, encoding="utf-8")

for name in ("pack-next-argon.js", "pack-next-grok.js", "pack-next-luna.js", "pack-next-lunamax.js"):
    text = (site / name).read_text(encoding="utf-8")
    ids = re.findall(r'id:\s*["\'](c\d+)["\']', text)
    print(name, len(ids), ids[:1], ids[-1:])
