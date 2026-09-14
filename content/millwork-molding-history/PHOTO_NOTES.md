# Photo / plate notes

No generated photographs. No fake temples, no fake shops.

Each article has two SVGs:

1. `historical-timeline.svg` — four dated anchors from `scripts/pack_data.py`.
2. `shop-plate.svg` — line sections on shop paper (ink `#2c2416`, ochre `#8b5a2b`). Dashed line is wall or fence.

Period plates: six slugs now include `historical-plate.jpg` (PD / CC0) with JSON metadata and
`<figure>` captions — see `RIGHTS.md` and `scripts/download_historical.py`. Do not drop a stock
photo of “luxury crown moulding” into this pack.

All articles use HTML `<figure>` with `alt` and `<figcaption>` for the two SVGs (and the
historical scan where present). Regenerate with `scripts/inject_figures.py`.
