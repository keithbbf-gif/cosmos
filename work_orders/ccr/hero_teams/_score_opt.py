import re
from pathlib import Path

files = {
    "ds": Path(r"V:\A\Ai\COSMOS\work_orders\ccr\hero_teams\ds41\OPT.txt"),
    "spark": Path(r"V:\A\Ai\COSMOS\work_orders\ccr\hero_teams\spark13\OPT.txt"),
    "glm": Path(r"V:\A\Ai\COSMOS\work_orders\ccr\hero_teams\glm53\OPT.txt"),
    "luna": Path(r"V:\A\Ai\COSMOS\work_orders\ccr\hero_teams\luna6\OPT.txt"),
    "max": Path(r"V:\A\Ai\COSMOS\work_orders\ccr\hero_teams\luna6max\OPT.txt"),
    "argon": Path(r"V:\A\Ai\COSMOS\work_orders\ccr\hero_teams\argon\OPT.js"),
    "grok": Path(r"V:\A\Ai\COSMOS\work_orders\ccr\hero_teams\grok47\OPT.js"),
}
for name, path in files.items():
    text = path.read_text(encoding="utf-8", errors="replace")
    start = text.lstrip()[:24].replace("\n", " ")
    ids = re.findall(r"id:\s*[\"'](c\d+)[\"']", text)
    bad = any(s in text for s in ("inspired_by", "near_miss", "nearMiss", "LMN_PACK = {}", "LMN_PACK={}"))
    print(name, len(text), start, ids, "bad", bad)
