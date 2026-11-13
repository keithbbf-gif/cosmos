"""LMNator static site builder - ticket bout card room."""
from pathlib import Path
import re

SITE_NAME = "LMNator"
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
IPV4_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")

NAV_LINKS = [
    {"href": "index.html", "label": "Bout"},
    {"href": "line.html", "label": "The line"},
    {"href": "derby.html", "label": "Derby"},
    {"href": "higher.html", "label": "Higher"},
    {"href": "tiles.html", "label": "Tiles"},
    {"href": "play.html", "label": "Pit"},
    {"href": "shop.html", "label": "Shop"},
    {"href": "account.html", "label": "Account"},
    {"href": "card.html", "label": "Card"},
    {"href": "roster.html", "label": "Roster"},
    {"href": "exhibition.html", "label": "Exhibition"},
    {"href": "keep.html", "label": "Keep"},
    {"href": "about.html", "label": "About"},
]

PAGES = [
    {"file": "index.html", "title": "Bout Night", "desc": "LMNator is a public bout card: same ask, three runs, keep or cut."},
    {"file": "card.html", "title": "The Card", "desc": "How to read an LMNator bout: four cuts and how to reuse them."},
    {"file": "roster.html", "title": "Roster", "desc": "Eight seats in the LMNator room. Types, not products. No ladder."},
    {"file": "exhibition.html", "title": "Exhibition", "desc": "A teaching slip: the Librarian and the Novelist on one ask."},
    {"file": "keep.html", "title": "Keep", "desc": "When a model stays in the ring at LMNator."},
    {"file": "about.html", "title": "About", "desc": "What the LMNator room is, what it refuses to be, and family links."},
]

BEATS_INDEX = [
    {"n": "01", "name": "The claim", "text": "What the poster, the demo, or the model said it could do. Write it down before the bell."},
    {"n": "02", "name": "The ask", "text": "One prompt a reader could reuse. Same ask, three runs, unless the card says otherwise."},
    {"n": "03", "name": "The cut", "text": "Where it missed: a wrong step, a fake citation, a refusal that did not fit, a tool it said it called."},
    {"n": "04", "name": "Still standing, or out", "text": "A keep is allowed. Newest is not fittest. The work decides."},
]

SAMPLE_SLIPS = [
    {"seat": "CLAIM", "kind": "claim", "title": "Poster says it cites clean", "text": "The demo flashes sources and smooth prose. The card asks for the same ask, three times, with links that resolve."},
    {"seat": "CUT", "kind": "cut", "title": "Air where the citation should be", "text": "A real-looking link that does not resolve is a fall. Smooth prose does not save the round."},
    {"seat": "KEEP", "kind": "keep", "title": "Stops when the source is not in hand", "text": "It names what it knows and drops what it cannot show. That stop is a keep, not a miss."},
]

CUTS_CARD = [
    {"seat": "CUT 1", "kind": "cut", "title": "Accuracy", "text": "The answer matches a known-correct reference on a factual or procedural ask. An invented citation or a quietly wrong step fails the item."},
    {"seat": "CUT 2", "kind": "cut", "title": "Consistency", "text": "Same prompt, three runs. Large swings with no temperature excuse count against the model. A stable wrong answer still fails. It is only stably wrong."},
    {"seat": "CUT 3", "kind": "cut", "title": "Refusal edges", "text": "Does it refuse what it should, and allow what it should? Over-refusal and under-refusal both go on the card with the exact prompt. Refusal is a temperament. The cut is whether the refusal matches the ask."},
    {"seat": "CUT 4", "kind": "cut", "title": "Invent", "text": "Where it fabricates a tool, an API, a paper, or a person. Saying a tool was called is not a tool call. Smooth prose does not save the round."},
]

ROSTER_SEATS = [
    {"seat": "SEAT A", "kind": "claim", "title": "The Sprinter", "text": "First token is fast and the second hop is thin. Speed is not the bout."},
    {"seat": "SEAT B", "kind": "keep", "title": "The Librarian", "text": "Would rather abstain than invent. A clean stop beats a full paragraph of air."},
    {"seat": "SEAT C", "kind": "cut", "title": "The Novelist", "text": "Fluent, and the citations are air. Agreement with the prompt mistake is not accuracy."},
    {"seat": "SEAT D", "kind": "cut", "title": "The Bouncer", "text": "Refuses ordinary work, then lectures. The cut is whether the refusal matches the ask."},
    {"seat": "SEAT E", "kind": "claim", "title": "The Clerk", "text": "Good with tools when somebody checks the tool result. A claimed call is not a call."},
    {"seat": "SEAT F", "kind": "claim", "title": "The House Model", "text": "The one already on the bill. Familiar is not a score. Same ask decides."},
    {"seat": "SEAT G", "kind": "keep", "title": "The Old Hand", "text": "Previous generation, still correct on the narrow job. An old model that still does the job is a keep."},
    {"seat": "SEAT H", "kind": "keep", "title": "The Understudy", "text": "Weights you can inspect. Inspection is not the same as a win. Almost has to be shown, not announced."},
]

RIVALRY_NOTES = [
    {"seat": "NOTE", "kind": "claim", "title": "Which job, whose tools", "text": "Which model is best usually means best at which job, on whose dollar, with whose tools."},
    {"seat": "NOTE", "kind": "cut", "title": "Weight classes", "text": "A fast cheap model and a slow expensive one are not the same weight class. One ladder is how a poster lies."},
    {"seat": "NOTE", "kind": "cut", "title": "Middle forget", "text": "A long window that forgets the middle is not memory. Agreement with the prompt mistake is not accuracy."},
    {"seat": "NOTE", "kind": "keep", "title": "Cheap seat", "text": "Almost as good, at a much lower cost, can take the cheap seat. Almost has to be shown, not announced."},
    {"seat": "NOTE", "kind": "claim", "title": "Open weigh-in", "text": "You can read one family's weights and not another's. A closed card is not an open weigh-in."},
]

KEEP_STAYS = [
    {"seat": "KEEP", "kind": "keep", "title": "Clean abstain", "text": "Abstaining when the source is not in hand."},
    {"seat": "KEEP", "kind": "keep", "title": "Right three times", "text": "The same answer three times when that answer is actually right."},
    {"seat": "KEEP", "kind": "keep", "title": "Fit refusal", "text": "A refusal that matches the ask, with the prompt still on the card."},
    {"seat": "KEEP", "kind": "keep", "title": "Old hand", "text": "An older model that still does the narrow job."},
    {"seat": "KEEP", "kind": "keep", "title": "Shown cheap", "text": "A cheaper seat that matches the reference you brought, shown, not announced."},
]

CSS_TEXT = """:root{
--canvas:#070B14;
--card:#121B2E;
--text:#F6F2EA;
--secondary:#C8CFDB;
--muted:#9BA6B8;
--link:#A5BB00;
--stop2:#FFB52E;
--keep:#4ADE80;
--cut:#FF7A7A;
--claim:#FFB52E;
--accent:#A5BB00;
--on-accent:#070B14;
--font:"Inter",ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
--mono:"JetBrains Mono",ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--canvas);color:var(--text);font-family:var(--font);font-size:18px;line-height:30px}
a{color:var(--link);text-underline-offset:3px}
a:hover{color:var(--stop2)}
:focus-visible{outline:3px solid var(--link);outline-offset:3px;border-radius:4px}
.skip{position:absolute;left:-999px;top:0;background:var(--text);color:#030712;padding:.6rem 1rem;z-index:99;font-weight:700}
.skip:focus{left:.5rem;top:.5rem}
.nav{position:sticky;top:0;z-index:50;background:rgba(3,7,18,.78);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);border-bottom:1px solid #1e293b}
.nav-inner{max-width:62rem;margin:0 auto;padding:.7rem 1rem;display:flex;align-items:center;gap:1rem;flex-wrap:wrap}
.brand{display:flex;align-items:center;gap:.6rem;text-decoration:none;color:var(--text)}
.brand-mark{font-family:var(--mono);font-weight:800;background:linear-gradient(135deg,var(--link),var(--stop2));padding:.2rem .55rem;border-radius:.45rem;color:#fff}
.brand-name{font-weight:800;letter-spacing:.02em}
.kicker{font-family:var(--mono);font-size:.72rem;letter-spacing:.22em;color:var(--secondary)}
.nav-links{margin-left:auto;display:flex;gap:.4rem;flex-wrap:wrap;list-style:none;padding:0;margin-top:0;margin-bottom:0}
.nav-links a{display:inline-block;padding:.35rem .65rem;border-radius:.5rem;text-decoration:none;color:var(--secondary)}
.nav-links a[aria-current="page"]{color:#fff;background:#1e293b}
.wrap{max-width:62rem;margin:0 auto;padding:1.2rem 1rem 3rem}
.ticket{background:linear-gradient(180deg,#111a2e,#0b0f19);border:1px solid #1e293b;border-radius:1rem;overflow:hidden;display:grid;grid-template-columns:11rem 1fr;margin:1.5rem 0 2rem}
.ticket-stub{padding:1.2rem 1rem;border-right:2px dashed #334155;display:flex;flex-direction:column;gap:.5rem;justify-content:center;position:relative;background:#0b0f19}
.ticket-stub::after{content:"";position:absolute;top:0;right:-9px;bottom:0;width:18px;background-image:radial-gradient(circle at 50% 25%,var(--canvas) 6px,transparent 7px);background-size:18px 28px;background-repeat:repeat-y;pointer-events:none}
.seat-mono{font-family:var(--mono);font-size:.8rem;color:var(--secondary);letter-spacing:.08em}
.ticket-no{font-family:var(--mono);color:#fff;border:1px solid #334155;border-radius:.4rem;padding:.25rem .5rem;display:inline-block}
.ticket-main{padding:1.6rem 1.4rem}
.ticket-kicker{font-family:var(--mono);letter-spacing:.24em;font-size:.75rem;color:var(--claim)}
.ticket h1{margin:.4rem 0 .5rem;font-size:2.2rem;line-height:1.1}
.dek{color:var(--secondary);font-size:1.08rem;max-width:38rem}
.btn{display:inline-flex;align-items:center;min-height:48px;margin-top:1rem;background:var(--accent);color:var(--on-accent);text-decoration:none;font-weight:700;padding:0 22px;border-radius:12px}
.card{background:var(--card);border:1px solid #1e293b;border-radius:.9rem;padding:1.2rem 1.2rem;margin:1rem 0}
.card h2{margin-top:0}
.muted{color:var(--muted)}
.secondary{color:var(--secondary)}
.slip{display:flex;gap:0;background:var(--card);border:1px solid #1e293b;border-radius:.8rem;overflow:hidden;margin:.9rem 0;border-left-width:8px;border-left-style:solid}
.slip.claim{border-left-color:var(--claim)}
.slip.cut{border-left-color:var(--cut)}
.slip.keep{border-left-color:var(--keep)}
.slip-stub{flex:0 0 9rem;background:#070b14;padding:1rem;border-right:1px solid #1e293b;font-family:var(--mono);font-size:.78rem;color:var(--secondary);display:flex;align-items:center;justify-content:center;text-align:center;letter-spacing:.06em}
.slip-body{padding:1rem 1.1rem}
.slip-body h3{margin:.1rem 0 .4rem;font-size:1.05rem}
.slip-body p{margin:.3rem 0;color:var(--secondary)}
.beats{list-style:none;padding:0;margin:0;display:grid;gap:.8rem}
.beats li{background:var(--card);border:1px solid #1e293b;border-radius:.7rem;padding:.9rem 1rem}
.beats strong{color:#fff}
.grid-two{display:grid;grid-template-columns:1fr 1fr;gap:1rem}
footer{border-top:1px solid #1e293b;max-width:62rem;margin:2.5rem auto 0;padding:1.2rem 1rem 2.5rem;color:var(--muted);font-size:.92rem}
footer a{color:var(--secondary)}
.stamp{display:inline-block;font-family:var(--mono);font-size:.72rem;letter-spacing:.14em;padding:.15rem .5rem;border-radius:.4rem;border:1px solid #334155;color:var(--secondary)}
.stamp.keep{color:var(--keep);border-color:var(--keep)}
.stamp.cut{color:var(--cut);border-color:var(--cut)}
.stamp.claim{color:var(--claim);border-color:var(--claim)}
@media (max-width:720px){
.ticket{grid-template-columns:1fr}
.ticket-stub{border-right:0;border-bottom:2px dashed #334155}
.ticket-stub::after{display:none}
.slip{flex-direction:column}
.slip-stub{flex:auto;border-right:0;border-bottom:1px solid #1e293b}
.grid-two{grid-template-columns:1fr}
.ticket h1{font-size:1.7rem}
}
.hero-sun{width:148px;height:148px;display:block;margin:0 auto 8px;filter:drop-shadow(0 0 28px rgba(255,122,26,.45))}
.stage{display:grid;grid-template-columns:180px 1fr;gap:18px;align-items:center;margin-top:18px}
.line-meta{color:var(--secondary);font-size:16px}
.ring{margin:28px 0}
.ring h2{margin-bottom:8px}
.model-slip .slip-body p{margin:0}
.score{font-family:var(--mono);color:var(--text);font-size:22px}
.price{font-family:var(--mono);font-size:14px;color:var(--muted)}
@media (max-width:899px){
.stage{grid-template-columns:1fr}
.hero-sun{width:112px;height:112px}
}
@media (prefers-reduced-motion:reduce){
html{scroll-behavior:auto}
*{transition:none;animation:none}
}
"""

FAVICON_TEXT = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect x="6" y="14" width="52" height="36" rx="7" fill="#0b0f19" stroke="#3b82f6" stroke-width="3"/><circle cx="6" cy="26" r="4" fill="#030712"/><circle cx="6" cy="38" r="4" fill="#030712"/><circle cx="58" cy="26" r="4" fill="#030712"/><circle cx="58" cy="38" r="4" fill="#030712"/><text x="32" y="39" font-family="monospace" font-size="16" font-weight="bold" text-anchor="middle" fill="#ffffff">LMN</text></svg>
"""

ROBOTS_TEXT = "User-agent: *\nAllow: /\n"


def check_clean(text):
    if EMAIL_RE.search(text):
        raise ValueError("refused: email-like string in page")
    if IPV4_RE.search(text):
        raise ValueError("refused: IPv4-like string in page")


def _ref(name):
    return (Path(__file__).resolve().parent / "ref" / name).read_text(encoding="utf-8")


def render_head(title, desc):
    return '<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n<meta name="theme-color" content="#070B14">\n<title>LMNator \u2014 ' + title + '</title>\n<meta name="description" content="' + desc + '">\n<link rel="icon" href="favicon.svg" type="image/svg+xml">\n<link rel="stylesheet" href="site.css">\n<link rel="stylesheet" href="family.css">\n'


def _nav_anchors(active, klass):
    items = []
    for link in NAV_LINKS:
        cur = ' aria-current="page"' if link["href"] == active else ""
        items.append('<a class="' + klass + '" href="' + link["href"] + '"' + cur + '>' + link["label"] + '</a>')
    return "".join(items)


def render_header(active):
    mark = _ref("brand-mark.html")
    desk = _nav_anchors(active, "nav-link")
    pocket = _nav_anchors(active, "nav-m")
    return '<a class="skip" href="#main">Skip to content</a>\n<header class="nav-header"><div class="nav-inner"><a class="brand-wrapper" href="index.html" aria-label="LMNator home">' + mark + '<span class="brand-title">LMN<span>ator</span></span></a><nav class="nav-menu" aria-label="Primary">' + desk + '</nav><details class="nav-mobile"><summary>Menu</summary><nav aria-label="Primary mobile">' + pocket + '</nav></details></div></header>\n'


def render_footer():
    return _ref("eco-footer.html") + "\n"


def render_slip(slip):
    seat = slip.get("seat", "SLIP")
    kind = slip.get("kind", "claim")
    title = slip.get("title", "")
    text = slip.get("text", "")
    if kind not in ("claim", "cut", "keep"):
        kind = "claim"
    return '<article class="slip ' + kind + '"><div class="slip-stub">' + seat + '</div><div class="slip-body"><span class="stamp ' + kind + '">' + kind.upper() + '</span><h3>' + title + '</h3><p>' + text + '</p></div></article>\n'


def render_slips(slips):
    return "".join(render_slip(s) for s in slips)


def page_shell(active, title, desc, main_html):
    head = render_head(title, desc)
    header = render_header(active)
    footer = render_footer()
    html = '<!doctype html>\n<html lang="en" data-product="lmnator">\n<head>\n' + head + '</head>\n<body>\n' + header + '<main id="main"><div class="wrap">\n' + main_html + '\n</div></main>\n' + footer + '</body>\n</html>\n'
    check_clean(html)
    return html


def build_index():
    beats_items = "".join('<li><strong>' + b["n"] + ' \u2014 ' + b["name"] + '.</strong> ' + b["text"] + '</li>' for b in BEATS_INDEX)
    main = '<div class="stage"><img class="hero-sun" src="favicon.svg" alt=""><section class="ticket" aria-label="Ticket hero"><div class="ticket-stub"><span class="seat-mono">ADMIT ONE</span><span class="ticket-no">LMN-001</span><span class="seat-mono">SAME ASK \u00d7 3</span></div><div class="ticket-main"><div class="ticket-kicker">ELIMINATOR \u00b7 SOLAROLABS ROOM</div><h1>LMNator</h1><p class="dek">Two models walk in on the same ask, and only the work decides who stays.</p><a class="btn" href="derby.html">Watch a derby</a> <a class="btn" href="line.html" style="background:transparent;color:#F6F2EA;border:1px solid rgba(246,242,234,.28)">Open the line</a></div></section></div>\n'
    main += '<p class="secondary"><a href="arcade.html">Arcade, 100 games</a> \u00b7 <a href="higher.html">Higher</a> \u00b7 <a href="tiles.html">Tiles</a> \u00b7 <a href="derby.html">Derby</a></p>\n'
    main += '<section class="card" aria-label="Four beats"><h2>Four beats of a bout</h2><ol class="beats">' + beats_items + '</ol></section>\n'
    main += '<section aria-label="Sample slips"><h2>Sample slips</h2><p class="secondary">How a slip looks before anyone claims a win. The full rules live on the card.</p>\n' + render_slips(SAMPLE_SLIPS) + '<p><a href="card.html">How to read a bout \u2192</a></p></section>\n'
    return page_shell("index.html", "Bout Night", PAGES[0]["desc"], main)


def build_card():
    main = '<p class="ticket-kicker">ELIMINATOR \u00b7 THE CARD</p><h1>How to read a bout</h1><p class="secondary">One ask, three runs, four cuts. Bring your own reference and keep the prompt on the card.</p>\n'
    main += render_slips(CUTS_CARD)
    main += '<section class="card" aria-label="Reuse"><h2>Reuse the card</h2><p class="secondary">A reader can reuse the four cuts on any model they already have. Publish the ask and the outcome. Vibes are not a bout. A new model that only wins the demo is a cut.</p><p><a href="exhibition.html">See a teaching slip \u2192</a></p></section>\n'
    main += '<section aria-label="Notes"><h2>Rivalry notes</h2>\n' + render_slips(RIVALRY_NOTES) + '</section>\n'
    return page_shell("card.html", "The Card", PAGES[1]["desc"], main)


def build_roster():
    main = '<p class="ticket-kicker">ELIMINATOR \u00b7 ROSTER</p><h1>Eight seats</h1><p class="secondary">Types, not products. No ladder, no ranks, no scores. Familiar is not a score.</p>\n'
    main += render_slips(ROSTER_SEATS)
    return page_shell("roster.html", "Roster", PAGES[2]["desc"], main)


def build_exhibition():
    main = '<p class="ticket-kicker">ILLUSTRATION \u00b7 TEACHING SLIP</p><h1>The Librarian and the Novelist</h1><p class="secondary">This card is a teaching slip. It is not a measured bout and it has no score.</p>\n'
    main += '<section class="card" aria-label="Ask"><h2>The ask</h2><p>Who wrote a named public-domain book, and on which page a given sentence appears. Try it with Frankenstein and Mary Shelley: name the writer, then place the sentence.</p></section>\n'
    ex_slips = [
        {"seat": "NOVELIST", "kind": "cut", "title": "Beautiful paragraph, invented page", "text": "The Novelist answered in a beautiful paragraph and invented the page. A page that cannot be shown fails Invent."},
        {"seat": "LIBRARIAN", "kind": "keep", "title": "Named the writer, stopped at the page", "text": "The Librarian named Mary Shelley, said it did not have the page, and stopped. \u201cI do not have the page\u201d is a keep, not a refusal failure."},
    ]
    main += render_slips(ex_slips)
    main += '<section class="card" aria-label="Reading"><h2>Reading</h2><p class="secondary">The Novelist is cut on Invent. The Librarian is a keep on Accuracy. Stopping when the source is not in hand beats fluent air.</p></section>\n'
    return page_shell("exhibition.html", "Exhibition", PAGES[3]["desc"], main)


def build_keep():
    main = '<p class="ticket-kicker">ELIMINATOR \u00b7 KEEP</p><h1>When a model stays in the ring</h1><p class="secondary">A keep is allowed. Newest is not fittest. These stays count.</p>\n'
    main += render_slips(KEEP_STAYS)
    main += '<section class="card" aria-label="Note"><h2>Note</h2><p class="secondary">Publish the ask and the outcome so you or the shop can rerun it. A cheaper seat must match the reference you brought, shown, not announced.</p></section>\n'
    return page_shell("keep.html", "Keep", PAGES[4]["desc"], main)


def build_about():
    main = '<p class="ticket-kicker">ELIMINATOR \u00b7 ABOUT</p><h1>What this room is</h1><section class="card" aria-label="Is"><h2>The room</h2><p class="secondary">LMNator publishes the ask and the outcome. Vibes are not a bout. A reader can reuse the four cuts on any model they already have.</p></section>\n'
    main += '<section class="card" aria-label="Refuses"><h2>What it refuses to be</h2><p class="secondary">It is not a second leaderboard and not a shop-floor scar log. The line shows numbers that already live in the ModelRaters catalog. LMNator does not invent a score, a price, or a winner.</p></section>\n'
    main += '<section class="card" aria-label="Family"><h2>Family</h2><p class="secondary">Part of the Solarolabs family. Visit <a href="https://solarolabs.com">solarolabs.com</a> and <a href="https://ai.solarolabs.com">ai.solarolabs.com</a>. A call, when you want one, goes through <a href="account.html">a TokenCenter account</a>. Questions come from you and the shop. No personal names on the card.</p></section>\n'
    return page_shell("about.html", "About", PAGES[5]["desc"], main)


FAMILY_EXTRA = """
.nav-header{position:sticky;top:0;z-index:1000;background:rgba(7,11,20,.88);backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);border-bottom:1px solid rgba(255,255,255,.09)}
.nav-inner{display:flex;align-items:center;gap:12px;min-height:64px;height:auto;flex-wrap:wrap;max-width:1100px;margin:0 auto;padding:8px 16px;padding-left:max(16px,env(safe-area-inset-left));padding-right:max(16px,env(safe-area-inset-right))}
.brand-wrapper{display:flex;align-items:center;gap:10px;text-decoration:none;color:#F6F2EA;min-height:44px}
.brand-title{font-size:20px;font-weight:700;letter-spacing:-.01em;color:#F6F2EA}
.brand-title span{color:#A5BB00;font-weight:500}
.nav-menu{display:flex;align-items:center;gap:4px;margin-left:12px;flex-wrap:wrap}
.nav-link{color:#C8CFDB;font-size:16px;font-weight:500;text-decoration:none;padding:8px 10px;min-height:44px;display:inline-flex;align-items:center}
.nav-link:hover,.nav-link[aria-current="page"]{color:#F6F2EA}
.nav-link[aria-current="page"]{box-shadow:inset 0 -2px 0 #A5BB00}
.nav-right{margin-left:auto}
.nav-right .btn{margin-top:0}
.nav-mobile{display:none;position:relative}
.nav-mobile summary{list-style:none;display:inline-flex;align-items:center;min-height:44px;min-width:44px;padding:0 16px;border:1px solid rgba(246,242,234,.28);border-radius:10px;font-size:18px;font-weight:600;cursor:pointer;color:#F6F2EA}
.nav-mobile summary::-webkit-details-marker{display:none}
.nav-mobile nav{display:flex;flex-direction:column;position:absolute;right:0;top:52px;min-width:220px;padding:8px;background:#0B1220;border:1px solid rgba(255,255,255,.12);border-radius:12px;z-index:1200}
.nav-m{display:flex;align-items:center;min-height:44px;padding:0 14px;font-size:16px;color:#C8CFDB;text-decoration:none;border-radius:10px}
.nav-m[aria-current="page"]{color:#F6F2EA;background:rgba(165,187,0,.12)}
@media (max-width:899px){.nav-menu,.nav-right{display:none!important}.nav-mobile{display:block;margin-left:auto}.nav-inner{flex-wrap:nowrap;height:64px}}
.wrap{padding-bottom:calc(72px + env(safe-area-inset-bottom))}
.reels{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin:12px 0}
.reel{background:#0B1220;border:1px solid rgba(255,255,255,.12);border-radius:12px;min-height:88px;display:flex;align-items:center;justify-content:center;text-align:center;padding:10px;font-family:var(--mono);font-size:14px;line-height:1.3}
.reel.spinning{color:#A5BB00}
.pit-bar{display:flex;gap:8px;flex-wrap:wrap;align-items:center}
.pit-bar .btn{margin-top:0;min-height:52px}
.chip-count{font-family:var(--mono);font-size:16px}
.vote-row{display:grid;grid-template-columns:1fr 1fr;gap:8px}
.vote-row .btn{width:100%;justify-content:center;margin-top:0}
.seat-blind{background:#121B2E;border:1px solid rgba(255,255,255,.12);border-radius:12px;padding:14px;min-height:120px}
.seat-blind h3{margin:0 0 6px}
@media (max-width:520px){.reels{grid-template-columns:1fr}.vote-row{grid-template-columns:1fr}}
.thumb{min-height:64px;font-size:20px;width:100%;justify-content:center;margin-top:0}
.shop-grid{display:grid;grid-template-columns:1fr;gap:12px}
@media (min-width:720px){.shop-grid{grid-template-columns:1fr 1fr}}
.shop-card{background:#121B2E;border:1px solid rgba(255,255,255,.12);border-radius:16px;padding:16px}
.shop-card h3{margin:0 0 6px}
.shop-price{font-family:var(--mono);color:#A5BB00;font-size:22px;margin:0 0 8px}
.hand{display:flex;gap:8px;overflow-x:auto;scroll-snap-type:x mandatory;padding-bottom:8px;-webkit-overflow-scrolling:touch}
.pick{min-width:82%;scroll-snap-align:start;text-align:left;background:#121B2E;border:1px solid rgba(255,255,255,.14);border-radius:16px;padding:14px;color:#F6F2EA;min-height:128px}
.pick.on{border-color:#A5BB00;box-shadow:0 0 0 1px #A5BB00}
.bout-lane{display:grid;grid-template-columns:1fr 64px 1fr;gap:8px;align-items:stretch;margin:10px 0}
.fighter{border-radius:12px;padding:10px;background:#0B1220;min-height:84px}
.fighter.win{box-shadow:inset 0 0 0 2px #4ADE80}
.fighter.lose{opacity:.4}
.lane-mid{display:flex;align-items:center;justify-content:center;font-family:var(--mono);color:#A5BB00;font-size:12px;text-align:center}
@media (min-width:720px){.pick{min-width:31%}}
.hl-card{min-height:38vh;display:flex;flex-direction:column;justify-content:center;background:#121B2E;border-radius:20px;padding:18px;margin:12px 0}
.hl-score{font-family:var(--mono);font-size:64px;line-height:.95;color:#A5BB00;margin:8px 0}
.tile-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:8px}
.tile{min-height:26vh;border:0;border-radius:18px;background:#0B1220;color:#F6F2EA;font-size:18px;font-weight:700;padding:12px}
.tile:active{background:#A5BB00;color:#070B14}
.field{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin:10px 0}
.seat-row{background:#0B1220;border-radius:12px;padding:8px 10px;min-height:64px}
.seat-row.you{box-shadow:inset 0 0 0 1px #A5BB00}
.seat-row.out{opacity:.4}
.seat-row strong{display:block}
"""


def build_play():
    main = '<p class="ticket-kicker">ELIMINATOR \u00b7 THE PIT</p><h1>Three phone games</h1>'
    main += '<p class="secondary">A blind bout, a one-thumb slip game, and a house slot. Names stay hidden until you move. House chips are not for sale. Call credit is a different token, bought on <a href="shop.html">the shop</a> through TokenCenter.</p>'
    main += '<section class="card" aria-label="Blind bout"><h2>Who gets the call?</h2>'
    main += '<p class="secondary">Same ask for both seats: name the writer of Frankenstein, and stop if you do not have the page. Pick before the names show.</p>'
    main += '<div class="vote-row"><article class="seat-blind" id="seat-a"><h3>Left</h3><p class="secondary">Drawing a seat\u2026</p></article>'
    main += '<article class="seat-blind" id="seat-b"><h3>Right</h3><p class="secondary">Drawing a seat\u2026</p></article></div>'
    main += '<div class="vote-row" style="margin-top:8px"><button type="button" class="btn" id="vote-a">Left</button><button type="button" class="btn" id="vote-b">Right</button></div>'
    main += '<div class="vote-row" style="margin-top:8px"><button type="button" class="btn" id="vote-tie" style="background:transparent;color:#F6F2EA;border:1px solid rgba(246,242,234,.28)">Either</button>'
    main += '<button type="button" class="btn" id="vote-none" style="background:transparent;color:#F6F2EA;border:1px solid rgba(246,242,234,.28)">Neither</button></div>'
    main += '<div id="bout-reveal"></div><p style="margin-top:12px"><button type="button" class="btn" id="bout-next">Next pair</button></p></section>'
    main += '<section class="card" aria-label="House slot"><h2>House slot</h2>'
    main += '<p class="secondary">Three catalog names. One house chip a spin. House chips live in this browser. They are not TokenCenter credit, and they are not for sale.</p>'
    main += '<p class="chip-count" id="chip-count">House chips: \u2014</p>'
    main += '<div class="reels" aria-live="polite"><div class="reel" id="reel-0">\u2014</div><div class="reel" id="reel-1">\u2014</div><div class="reel" id="reel-2">\u2014</div></div>'
    main += '<div class="pit-bar"><button type="button" class="btn" id="spin">Spin</button><button type="button" class="btn" id="refill" style="background:transparent;color:#F6F2EA;border:1px solid rgba(246,242,234,.28)">Refill house chips</button></div>'
    main += '<div id="landed"></div></section>'
    main += '<section class="card" aria-label="Slip game"><h2>Slip</h2>'
    main += '<p class="secondary">One seat. You see the weight class and the price band. Cut if you think the catalog score is under 50. Keep if you think it is 50 or more. Then the name shows.</p>'
    main += '<p class="chip-count" id="slip-score">Streak: 0</p>'
    main += '<article class="seat-blind" id="slip-card"><h3>Seat</h3><p class="secondary">Drawing\u2026</p></article>'
    main += '<div class="vote-row" style="margin-top:8px"><button type="button" class="btn thumb" id="slip-cut" style="background:#FF7A7A;color:#070B14">Cut</button>'
    main += '<button type="button" class="btn thumb" id="slip-keep" style="background:#4ADE80;color:#070B14">Keep</button></div>'
    main += '<div id="slip-reveal"></div></section>'
    main += '<p class="secondary">The derby stakes game tokens. Buy those on the <a href="account.html">account page</a> or inside the derby. TokenCenter charges the card. This site is the shelf.</p>'
    main += '<script src="save.js?v=runs"></script>\n<script src="pit.js?v=runs"></script>\n<script src="slip.js?v=field"></script>\n'
    return page_shell("play.html", "The pit", "A blind seat bout and a house-chip slot. Names stay hidden until you vote. Chips are not credit.", main)


def token_shelf():
    main = '<p class="chip-count game-purse">Game tokens: \u2014</p>'
    main += '<p id="buy-msg" class="secondary" role="status"></p>'
    main += '<h2>Game tokens</h2><p class="secondary">For the derby. Stake them on your squad. They stay on this LMNator account. TokenCenter charges the card and does not list these packs.</p>'
    main += '<div class="shop-grid">'
    main += '<article class="shop-card"><h3>Bench</h3><p class="shop-price">40 \u00b7 $3</p><p class="secondary">Enough for four derbies.</p><p><button type="button" class="btn thumb" data-lmn-buy="game" data-amount="3" data-grant="40">Buy bench</button></p></article>'
    main += '<article class="shop-card"><h3>Squad</h3><p class="shop-price">120 \u00b7 $8</p><p class="secondary">A night of rematches.</p><p><button type="button" class="btn thumb" data-lmn-buy="game" data-amount="8" data-grant="120">Buy squad</button></p></article>'
    main += '<article class="shop-card"><h3>Season</h3><p class="shop-price">300 \u00b7 $18</p><p class="secondary">The long card.</p><p><button type="button" class="btn thumb" data-lmn-buy="game" data-amount="18" data-grant="300">Buy season</button></p></article>'
    main += '</div>'
    main += '<h2>AI tokens</h2><p class="secondary">Call credit on the TokenCenter key created at checkout. Same card desk. Different token. The balance is not the derby purse.</p>'
    main += '<div class="shop-grid">'
    main += '<article class="shop-card"><h3>Try</h3><p class="shop-price">$5</p><p class="secondary">A few real asks at provider price.</p><p><button type="button" class="btn thumb" data-lmn-buy="ai" data-amount="5" data-pack="mini">Buy AI tokens</button></p></article>'
    main += '<article class="shop-card"><h3>Work</h3><p class="shop-price">$19</p><p class="secondary">The same credit, fewer trips.</p><p><button type="button" class="btn thumb" data-lmn-buy="ai" data-amount="19" data-pack="maker">Buy AI tokens</button></p></article>'
    main += '<article class="shop-card"><h3>Night</h3><p class="shop-price">$59</p><p class="secondary">A long run of the same ask, three times.</p><p><button type="button" class="btn thumb" data-lmn-buy="ai" data-amount="59" data-pack="studio">Buy AI tokens</button></p></article>'
    main += '</div>'
    main += '<p class="secondary">TokenCenter processes the payment. LMNator never sees the card. If this phone has no key yet, checkout shows a new one once so the AI tokens have somewhere to land. Game tokens land here when TokenCenter sends you back.</p>'
    return main


def build_account():
    main = '<p class="ticket-kicker">ELIMINATOR \u00b7 ACCOUNT</p><h1>Game tokens and AI tokens</h1>'
    main += '<p class="secondary">This is the shelf. It is not on the TokenCenter site. Buy here, or buy the same packs inside the derby.</p>'
    main += token_shelf()
    main += '<script src="buy.js"></script>\n'
    return page_shell("account.html", "Account", "Buy game tokens for the derby, or AI tokens for real calls. Checkout is TokenCenter. The shelf is only here.", main)


def build_shop():
    main = '<p class="ticket-kicker">ELIMINATOR \u00b7 SHOP</p><h1>The same shelf as the account</h1>'
    main += token_shelf()
    main += '<p><a href="derby.html">Take them to the derby</a></p>'
    main += '<script src="buy.js"></script>\n'
    return page_shell("shop.html", "Shop", "Game tokens and AI tokens. The shelf lives on LMNator. TokenCenter charges the card.", main)


def build_derby():
    main = '<p class="ticket-kicker">ELIMINATOR \u00b7 DERBY</p><h1>Draft a squad. Watch it fight.</h1>'
    main += '<p class="secondary">You draft three. Sprinter, the Librarian, and the Novelist draft against you from the same catalog. Score, Price, and Reach each pay points. Highest points take the table. Stake is 10 game tokens. No cash-out.</p>'
    main += '<div id="lobby" data-game="derby"></div>'
    main += '<div id="match-board" hidden>'
    main += '<p class="chip-count game-purse">Game tokens: \u2014</p>'
    main += '<div class="hand" id="hand" aria-label="Draft hand"></div>'
    main += '<div class="pit-bar"><button type="button" class="btn thumb" id="fight" disabled>Watch the bout</button><button type="button" class="btn thumb" id="redeal" style="background:transparent;color:#F6F2EA;border:1px solid rgba(246,242,234,.28)">New hand</button></div>'
    main += '<div id="arena" aria-live="polite"></div>'
    main += '<section class="card" id="in-game-shop" aria-label="Buy tokens"><h2>Buy in the pit</h2>'
    main += token_shelf()
    main += '</section>'
    main += '</div>'
    main += '<script src="save.js?v=runs"></script>\n<script src="buy.js?v=queue"></script>\n<script src="lobby.js?v=queue"></script>\n<script src="derby.js?v=queue"></script>\n'
    return page_shell("derby.html", "Derby", "Draft three real models, stake game tokens, and watch Score, Price, and Reach decide the bout.", main)


def build_higher():
    main = '<p class="ticket-kicker">ELIMINATOR \u00b7 HIGHER</p><h1>Higher or lower</h1>'
    main += '<p class="secondary">Same hidden score for the whole table. Sprinter, the Librarian, and the Novelist call it with you. Two lives each. First to 5, or last one standing.</p>'
    main += '<div id="lobby" data-game="higher"></div>'
    main += '<div id="match-board" hidden>'
    main += '<div class="field" id="field" aria-label="The table"></div>'
    main += '<article class="hl-card" id="higher-now"><h2>Drawing</h2></article>'
    main += '<article class="seat-blind" id="higher-next"><h3>Next</h3><p>Price and maker land here. The score stays hidden.</p></article>'
    main += '<div class="vote-row"><button type="button" class="btn thumb" id="higher-up">Higher</button><button type="button" class="btn thumb" id="higher-down">Lower</button></div>'
    main += '<div id="higher-end"></div>'
    main += '</div>'
    main += '<script src="save.js?v=runs"></script>\n<script src="buy.js?v=queue"></script>\n<script src="lobby.js?v=queue"></script>\n<script src="higher.js?v=queue"></script>\n'
    return page_shell("higher.html", "Higher", "Higher or lower on real catalog scores. Price and maker show first. The score does not.", main)


def build_tiles():
    main = '<p class="ticket-kicker">ELIMINATOR \u00b7 TILES</p><h1>Tap the one that fits</h1>'
    main += '<p class="secondary">Same four tiles for the whole table. Sprinter is fast and sloppy. The Librarian is slow and sharp. The Novelist is sure and often wrong. First to 6 hits takes the match.</p>'
    main += '<div id="lobby" data-game="tiles"></div>'
    main += '<div id="match-board" hidden>'
    main += '<div class="field" id="field" aria-label="The table"></div>'
    main += '<p class="secondary" id="tile-ask">Get ready</p>'
    main += '<div class="tile-grid" id="tile-grid"></div>'
    main += '<div id="tile-end"></div>'
    main += '</div>'
    main += '<script src="save.js?v=runs"></script>\n<script src="buy.js?v=queue"></script>\n<script src="lobby.js?v=queue"></script>\n<script src="tiles.js?v=queue"></script>\n'
    return page_shell("tiles.html", "Tiles", "A one-thumb tile run. Tap the catalog model that matches the ask before the bar runs out.", main)


def build_line():
    main = '<p class="ticket-kicker">ELIMINATOR \u00b7 THE LINE</p><h1>The catalog, not a poster</h1><p class="secondary">Four rings cut from the ModelRaters catalog at mdata.modelraters.com. The number on a card is theirs. LMNator does not award it. Game bouts are saved for this catalog at runs.php.</p>\n'
    main += '<p class="line-meta" id="line-meta">Loading the catalog\u2026</p><div id="line-root"></div>\n<script src="app.js"></script>\n'
    return page_shell("line.html", "The line", "Live rings from the ModelRaters catalog: still standing, cheap seats, open weigh-in, and headroom.", main)


def build_site():
    base = Path(__file__).resolve().parent / "site"
    css_dir = base / "css"
    css_dir.mkdir(parents=True, exist_ok=True)
    (base / "js").mkdir(parents=True, exist_ok=True)
    pages = [
        {"file": "index.html", "html": build_index()},
        {"file": "line.html", "html": build_line()},
        {"file": "derby.html", "html": build_derby()},
        {"file": "higher.html", "html": build_higher()},
        {"file": "tiles.html", "html": build_tiles()},
        {"file": "play.html", "html": build_play()},
        {"file": "shop.html", "html": build_shop()},
        {"file": "account.html", "html": build_account()},
        {"file": "card.html", "html": build_card()},
        {"file": "roster.html", "html": build_roster()},
        {"file": "exhibition.html", "html": build_exhibition()},
        {"file": "keep.html", "html": build_keep()},
        {"file": "about.html", "html": build_about()},
    ]
    for p in pages:
        check_clean(p["html"])
        (base / p["file"]).write_text(p["html"], encoding="utf-8")
    check_clean(CSS_TEXT)
    (base / "site.css").write_text(CSS_TEXT, encoding="utf-8")
    family = _ref("ahs-header.css") + "\n" + _ref("eco-footer.css") + "\n" + FAMILY_EXTRA
    (base / "family.css").write_text(family, encoding="utf-8")
    fav = _ref("favicon.svg")
    check_clean(fav)
    (base / "favicon.svg").write_text(fav, encoding="utf-8")
    check_clean(ROBOTS_TEXT)
    (base / "robots.txt").write_text(ROBOTS_TEXT, encoding="utf-8")
    print("SITE_OK")


if __name__ == "__main__":
    build_site()