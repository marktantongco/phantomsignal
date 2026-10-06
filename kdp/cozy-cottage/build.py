#!/usr/bin/env python3
"""Build script for the Phase 3 interior prompt deck (Cozy Cottage, Bold & Easy).

Source of truth for the 40 interior prompts lives in PAGES below.
Running this file regenerates:

    prompts.json                 machine-readable deck (batch/API runs)
    prompts.csv                  spreadsheet run sheet
    phase3-interior-prompts.md   copy-paste markdown deck
    phase3-interior-prompts.html self-contained HTML artifact

Usage:  python3 build.py
"""

import csv
import html
import json
import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

TRIM = '8.5 x 8.5 in'
PRICE = '$9.99'

# ---------------------------------------------------------------------------
# THE LOCKS
# Every prompt you ship = STYLE_LOCK + subject + NEGATIVE_LOCK.
# The locks are what keep 40 AI-generated pages looking like ONE book.
# ---------------------------------------------------------------------------

STYLE_LOCK = (
    "Bold and easy coloring book page for adults, cozy cottagecore theme, "
    "ONE single centered subject, very thick uniform black outlines, simple flat chunky shapes, "
    "large open coloring areas, minimal detail, clean white background, no shading, no gray tones, "
    "no fill, no texture, high-contrast pure black and white line art, cute whimsical storybook style, "
    "square 1:1 composition, generous 0.5 inch margins, subject centered with breathing room on all sides. "
)

NEGATIVE_LOCK = (
    "NO text, no words, no letters, no numbers, no labels, no watermark, no signature, "
    "no frame, no border, no panel layout, no multiple scenes, no shading, no gradient, "
    "no hatching, no crosshatching, no stippling, no color, no gray fill, no background scenery, "
    "no tiny fiddly details, no photorealism, no 3D render, no blurry or broken lines."
)

# ---------------------------------------------------------------------------
# THE 40 PAGES
# type: "Hero scene" (full little world, 9-13 shapes) or "Object vignette" (one
# cluster of objects, 5-8 shapes). Sequence alternates hero / vignette so the
# book never feels like 40 identical object drawings.
# ---------------------------------------------------------------------------

PAGES = [
    # --- GROUP 1: OUTSIDE THE COTTAGE (1-8) -------------------------------
    dict(page=1, group="Outside the Cottage", title="The Round Door",
         type="Hero scene", shapes="9-11",
         subject="A small cozy stone cottage front with a round wooden door, two round windows with flower boxes overflowing with tulips, a curved stone step, a lantern hanging beside the door, and three flat stepping stones leading up to it.",
         notes="Your cover promise page. Keep the door and windows BIG - this is the page reviewers photograph."),
    dict(page=2, group="Outside the Cottage", title="Chimney Smoke",
         type="Object vignette", shapes="6-8",
         subject="A cottage rooftop corner with a stone chimney and three big curling puffs of smoke rising from it, three simple swallows in flight, and a weather vane on the ridge.",
         notes="Smoke puffs must be solid closed shapes, not wispy lines - wispy = fiddly."),
    dict(page=3, group="Outside the Cottage", title="The Garden Path",
         type="Hero scene", shapes="9-11",
         subject="A winding stone path through grass with a tall lantern on a post beside it, three toadstool mushrooms, a small watering can set down on the path, and two butterflies.",
         notes="CUT LIST candidate if you must ship a 36-design book."),
    dict(page=4, group="Outside the Cottage", title="Cottage at Dusk",
         type="Hero scene", shapes="10-12",
         subject="A cozy cottage at night with four warm glowing square windows, a lantern lit beside the door, five fireflies drawn as simple dots with tiny wings, and a crescent moon with four stars.",
         notes="TRAP: 'glowing' must render as WHITE with a thick outline, never gray fill. If it comes back gray, add 'white windows, unfilled windows'."),
    dict(page=5, group="Outside the Cottage", title="The Vegetable Patch",
         type="Object vignette", shapes="7-8",
         subject="A raised garden bed with three carrots with leafy tops, two cabbages, a trowel stuck in the soil, and a watering can resting on the edge of the bed."),
    dict(page=6, group="Outside the Cottage", title="The Wishing Well",
         type="Hero scene", shapes="9-11",
         subject="An old stone well with a shingled roof, a bucket hanging from a rope over a pulley, ivy climbing one side, and five simple flowers growing at its base."),
    dict(page=7, group="Outside the Cottage", title="The Firewood Stack",
         type="Object vignette", shapes="7-8",
         subject="A neat stack of split logs against a cottage wall, a round chopping stump with an axe stuck into it, and a curious squirrel holding an acorn on top of the stump."),
    dict(page=8, group="Outside the Cottage", title="The Front Gate",
         type="Hero scene", shapes="9-11",
         subject="A white picket garden gate left slightly open with a mailbox on a post beside it, two parcels tied with string resting on the ground, and a small garden gnome with a pointed hat.",
         notes="Parcels and envelopes must be BLANK - no stamps, no writing, no address lines."),

    # --- GROUP 2: KITCHEN & HEARTH (9-16) ---------------------------------
    dict(page=9, group="Kitchen & Hearth", title="The Wood Stove",
         type="Hero scene", shapes="9-11",
         subject="A cast-iron wood-burning kitchen stove with a round kettle on top, a pot on a second burner, an oven mitt hanging from a hook, and a small pile of firewood stacked beside it."),
    dict(page=10, group="Kitchen & Hearth", title="The Pantry Shelf",
         type="Object vignette", shapes="7-8",
         subject="A wooden pantry shelf holding five unlabeled jars of preserves, two tall bottles, a tin can, and a bundle of wheat stalks leaning at one end.",
         notes="TRAP: jars must be BLANK. AI loves to invent labels. Say 'unlabeled, no writing' twice if needed."),
    dict(page=11, group="Kitchen & Hearth", title="Baking Day",
         type="Hero scene", shapes="9-11",
         subject="A kitchen table with a round loaf of bread, a rolling pin, a sack of flour, a mixing bowl, and three eggs resting in a small basket."),
    dict(page=12, group="Kitchen & Hearth", title="Pie on the Sill",
         type="Object vignette", shapes="6-8",
         subject="A fruit pie cooling on an open windowsill with three curls of steam rising from it, a checked cloth beneath it, and a spoon resting on a small plate."),
    dict(page=13, group="Kitchen & Hearth", title="Teatime",
         type="Object vignette", shapes="7-8",
         subject="A teapot with a matching teacup and saucer, a sugar bowl with two sugar cubes, a teaspoon, and a round biscuit with three dots on a small plate.",
         notes="The single most 'cozy' object cluster in the book. Also your best A+ Content / ad image."),
    dict(page=14, group="Kitchen & Hearth", title="Mixing Bowl",
         type="Object vignette", shapes="6-8",
         subject="A large mixing bowl with a whisk standing in it, a wooden spoon leaning against the rim, a measuring cup, a cracked eggshell, and a small pile of flour.",
         notes="CUT LIST candidate - overlaps page 11 (Baking Day)."),
    dict(page=15, group="Kitchen & Hearth", title="The Hearth",
         type="Hero scene", shapes="10-12",
         subject="A stone fireplace with a crackling log fire, a kettle hanging from a crane hook over the flames, a fire poker leaning at the side, and a cat curled asleep on the hearth rug."),
    dict(page=16, group="Kitchen & Hearth", title="Hanging Herbs",
         type="Object vignette", shapes="7-8",
         subject="A wooden beam above a kitchen counter with three bundles of dried herbs hanging upside down, a braid of garlic, and two pans hanging from hooks."),

    # --- GROUP 3: COZY CORNERS (17-24) ------------------------------------
    dict(page=17, group="Cozy Corners", title="The Reading Chair",
         type="Hero scene", shapes="9-11",
         subject="A big soft armchair with a chunky knit blanket draped over one arm, an open book resting on the seat, a pair of slippers on the floor, and a small round side table with a mug on it.",
         notes="Blanket folds = 3-4 thick lines max. This is the page that gets over-detailed most often."),
    dict(page=18, group="Cozy Corners", title="The Window Seat",
         type="Hero scene", shapes="9-11",
         subject="A cushioned window seat with three pillows, a cat sitting upright watching a bird outside the window, and a gathered curtain tied back to one side."),
    dict(page=19, group="Cozy Corners", title="The Bookshelf",
         type="Object vignette", shapes="7-8",
         subject="A wooden bookshelf with two rows of books, a trailing plant in a pot on the top shelf, a lit candle in a holder, and a small round clock.",
         notes="TRAP: book spines must be BLANK rectangles - no titles, no author names."),
    dict(page=20, group="Cozy Corners", title="The Knitting Basket",
         type="Object vignette", shapes="7-8",
         subject="A rocking chair with a woven basket beside it holding three balls of yarn, two knitting needles crossed, and a half-knitted scarf spilling over the rim."),
    dict(page=21, group="Cozy Corners", title="The Mantelpiece",
         type="Hero scene", shapes="9-11",
         subject="A fireplace mantel with a round wall clock, two candlesticks, a garland of leaves draped along the front edge, and one small framed picture with a blank oval mat inside.",
         notes="Frame must be EMPTY. Second most common AI failure in this deck."),
    dict(page=22, group="Cozy Corners", title="Hot Cocoa",
         type="Object vignette", shapes="6-8",
         subject="A mug of hot cocoa with three marshmallows floating on top and steam curling up, a plate with two cookies, and a small jug beside them on a round table."),
    dict(page=23, group="Cozy Corners", title="The Braided Rug",
         type="Object vignette", shapes="7-8",
         subject="An oval braided rug on a wooden floor with a basket of logs beside it, a pair of boots, and a sleeping dog curled up in the center of the rug."),
    dict(page=24, group="Cozy Corners", title="The Sewing Table",
         type="Object vignette", shapes="7-8",
         subject="A small sewing table with three spools of thread, open scissors, a pincushion with two pins, a folded square of fabric, and a thimble.",
         notes="CUT LIST candidate - pins and scissors are the fiddliest shapes in the deck."),

    # --- GROUP 4: GARDEN & GREENHOUSE (25-32) -----------------------------
    dict(page=25, group="Garden & Greenhouse", title="The Pumpkin Cart",
         type="Hero scene", shapes="9-11",
         subject="A wooden wheelbarrow filled with three plump pumpkins and two gourds, one pumpkin sitting on the ground beside it, and a few fallen leaves scattered around."),
    dict(page=26, group="Garden & Greenhouse", title="Sunflowers & Can",
         type="Object vignette", shapes="7-8",
         subject="A tall galvanized watering can beside two big sunflowers with broad leaves, and three terracotta pots stacked at the base."),
    dict(page=27, group="Garden & Greenhouse", title="The Potting Bench",
         type="Hero scene", shapes="9-11",
         subject="A garden potting bench with four seedling pots in a tray, a hand trowel, a ball of twine, and two blank seed packets propped against the bench leg.",
         notes="TRAP: seed packets must be BLANK. Same failure mode as pantry jars."),
    dict(page=28, group="Garden & Greenhouse", title="The Beehive",
         type="Object vignette", shapes="7-8",
         subject="A beehive made of stacked wooden boxes on a stand with three bees buzzing around it, a patch of clover, and two tall flowers at the sides.",
         notes="CUT LIST candidate if you need a fourth cut."),
    dict(page=29, group="Garden & Greenhouse", title="The Birdhouse",
         type="Hero scene", shapes="9-11",
         subject="A birdhouse on a tall post with a small round entrance hole, two perched birds, a leafy branch arching over the top, and three berries on the branch."),
    dict(page=30, group="Garden & Greenhouse", title="Washing Day",
         type="Hero scene", shapes="10-12",
         subject="A clothesline strung between two posts with three hanging sheets and two towels, a peg bag dangling from the line, a woven laundry basket of folded cloth below, and a gentle breeze shown as two curved lines."),
    dict(page=31, group="Garden & Greenhouse", title="The Mushroom Patch",
         type="Object vignette", shapes="7-8",
         subject="A cluster of five toadstool mushrooms with spotted caps, two curling ferns, a snail with a spiral shell, and three smooth stones in the grass.",
         notes="Spots must be BIG - small dots are the #1 'not bold and easy' complaint."),
    dict(page=32, group="Garden & Greenhouse", title="Apple Ladder",
         type="Hero scene", shapes="9-11",
         subject="A wooden ladder leaning into an apple tree with a basket of apples on the ground below, four apples still hanging in the branches, and a few leaves."),

    # --- GROUP 5: BED, BATH & SEASONS (33-40) -----------------------------
    dict(page=33, group="Bed, Bath & Seasons", title="The Quilted Bed",
         type="Hero scene", shapes="9-11",
         subject="A made bed with a patchwork quilt folded back, two plump pillows, a sleeping cat curled at the foot, and a small folded blanket on a bench beside the bed.",
         notes="Quilt patches should be 6-8 large squares, not a grid of 30. Grid = intricate, not easy."),
    dict(page=34, group="Bed, Bath & Seasons", title="The Nightstand",
         type="Object vignette", shapes="7-8",
         subject="A small nightstand with a table lamp, a closed book with a bookmark ribbon, a pair of round glasses, a water carafe with a glass, and a tiny alarm clock."),
    dict(page=35, group="Bed, Bath & Seasons", title="The Clawfoot Tub",
         type="Hero scene", shapes="9-11",
         subject="A clawfoot bathtub with three big bubbles floating above the rim, a lit candle on a stool beside it, a folded towel, and a rubber duck floating at the far end."),
    dict(page=36, group="Bed, Bath & Seasons", title="The Washstand",
         type="Object vignette", shapes="7-8",
         subject="A washstand with a pitcher and basin, a towel hanging from a rail, a round mirror above it, a bar of soap on a dish, and a small sprig of lavender.",
         notes="CUT LIST candidate - lowest emotional pull of the group."),
    dict(page=37, group="Bed, Bath & Seasons", title="The Attic Trunk",
         type="Hero scene", shapes="10-12",
         subject="An open attic trunk with folded quilts spilling out of it, three stacked books, an old lantern, a garland of dried flowers, and a little mouse peeking over the rim."),
    dict(page=38, group="Bed, Bath & Seasons", title="Snowy Cottage Night",
         type="Hero scene", shapes="10-12",
         subject="The cottage in deep snow with warm glowing windows, a snowman with a scarf and twig arms, three pine trees, and a full moon with five stars.",
         notes="Second cover-candidate page. Also your winter/seasonal hook for gift listings."),
    dict(page=39, group="Bed, Bath & Seasons", title="Harvest Porch",
         type="Hero scene", shapes="10-12",
         subject="A cottage porch dressed for harvest with four pumpkins on the steps, a hay bale, two pots of chrysanthemums, a round wreath on the door, and a jug of cider."),
    dict(page=40, group="Bed, Bath & Seasons", title="Rainy Doorstep",
         type="Hero scene", shapes="9-11",
         subject="The cottage doorstep on a spring day with a pair of rain boots, a closed umbrella leaning against the wall, a puddle reflecting a heart shape, three tulips in a pot, and rain falling as straight dashed lines.",
         notes="Closing page. Rain as straight dashed lines keeps it bold and easy - never stippled dots."),
]

CUT_LIST = [14, 24, 36, 28]

GROUPS = [
    ("Outside the Cottage", 1, 8),
    ("Kitchen & Hearth", 9, 16),
    ("Cozy Corners", 17, 24),
    ("Garden & Greenhouse", 25, 32),
    ("Bed, Bath & Seasons", 33, 40),
]

for p in PAGES:
    p["prompt"] = STYLE_LOCK + p["subject"] + " " + NEGATIVE_LOCK

e = html.escape


def write_json():
    payload = {
        "deck": "Phase 3 - Cozy Cottage interior prompts",
        "spec": {"trim": TRIM, "price": PRICE, "page_count": 40,
                 "style": "bold and easy", "audience": "adults"},
        "style_lock": STYLE_LOCK.strip(),
        "negative_lock": NEGATIVE_LOCK.strip(),
        "pages": [{k: p.get(k, "") for k in
                   ("page", "group", "title", "type", "shapes", "subject", "prompt", "notes")}
                  for p in PAGES],
    }
    with open(os.path.join(OUT_DIR, "prompts.json"), "w") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
        f.write("\n")


def write_csv():
    with open(os.path.join(OUT_DIR, "prompts.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["page", "group", "title", "type", "shapes", "prompt", "notes"])
        for p in PAGES:
            w.writerow([p["page"], p["group"], p["title"], p["type"], p["shapes"],
                        p["prompt"], p.get("notes", "")])


def write_md():
    L = []
    A = L.append
    A("# Phase 3 - Interior Prompt Deck: Cozy Cottage (Bold & Easy)")
    A("")
    A(f"**Spec lock:** {TRIM} trim | 40 interior pages | bold & easy | adult coloring | list price {PRICE}")
    A("")
    A("Every prompt below is `STYLE LOCK + subject + NEGATIVE LOCK`, pre-assembled so you can "
      "copy one line into any image model and get a page that matches the other 39.")
    A("")
    A("---")
    A("")
    A("## 1. The two locks (copy these once, understand them forever)")
    A("")
    A("### STYLE LOCK (prefix - goes before every subject)")
    A("")
    A("```")
    A(STYLE_LOCK.strip())
    A("```")
    A("")
    A("### NEGATIVE LOCK (suffix - goes after every subject)")
    A("")
    A("```")
    A(NEGATIVE_LOCK.strip())
    A("```")
    A("")
    A("The locks are the entire game. 40 pages generated with 40 different phrasings look like "
      "a clip-art bundle. 40 pages generated through one locked prefix look like one artist's book.")
    A("")
    A("---")
    A("")
    A("## 2. The 40 pages")
    A("")
    for name, start, end in GROUPS:
        A(f"### {name} - pages {start:02d}-{end:02d}")
        A("")
        for p in PAGES:
            if not (start <= p["page"] <= end):
                continue
            A(f"**{p['page']:02d}. {p['title']}** - {p['type']} - {p['shapes']} shapes")
            A("")
            A("```")
            A(p["prompt"])
            A("```")
            A("")
            if p.get("notes"):
                A(f"> {p['notes']}")
                A("")
    A("---")
    A("")
    A("## 3. Machine-readable files")
    A("")
    A("- `prompts.json` - full deck with group, type, shape budget and per-page notes")
    A("- `prompts.csv` - run sheet: one row per page, paste into a sheet and track status")
    A("")
    A("Files are generated by `build.py`; edit the source there and re-run to regenerate all four.")
    A("")
    with open(os.path.join(OUT_DIR, "phase3-interior-prompts.md"), "w") as f:
        f.write("\n".join(L))


def write_html():
    cards = []
    for name, start, end in GROUPS:
        cards.append(f'<h2 class="group" id="g{start}">{e(name)} <span>pages {start:02d}-{end:02d}</span></h2>')
        cards.append('<div class="grid">')
        for p in PAGES:
            if not (start <= p["page"] <= end):
                continue
            notes = (f'<p class="note">{e(p["notes"])}</p>' if p.get("notes") else "")
            cards.append(f'''<article class="card" data-prompt="{e(p["prompt"])}">
  <header>
    <span class="num">{p["page"]:02d}</span>
    <h3>{e(p["title"])}</h3>
  </header>
  <div class="meta"><span class="chip t">{e(p["type"])}</span><span class="chip s">{e(p["shapes"])} shapes</span></div>
  <pre>{e(p["prompt"])}</pre>
  {notes}
  <div class="row"><button class="copy">Copy prompt</button><span class="ok">Copied</span></div>
</article>''')
        cards.append('</div>')

    cut_rows = "".join(
        f"<li><b>{p['page']:02d}. {e(p['title'])}</b> - {e(p.get('notes','').split('.')[0])}</li>"
        for p in PAGES if p["page"] in sorted(CUT_LIST))

    doc = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Phase 3 - Cozy Cottage Interior Prompt Deck</title>
<style>
  :root {{
    --paper:#fbf6ec; --ink:#2f2a25; --muted:#7d7267; --line:#e6dccb;
    --terra:#c2703f; --sage:#7c8b6a; --gold:#d9a441;
  }}
  * {{ box-sizing:border-box; }}
  body {{
    margin:0; background:var(--paper); color:var(--ink);
    font:16px/1.6 ui-sans-serif,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  }}
  .wrap {{ max-width:1120px; margin:0 auto; padding:48px 24px 96px; }}
  header.top {{ border-bottom:3px double var(--line); padding-bottom:28px; margin-bottom:36px; }}
  .kicker {{ letter-spacing:.18em; text-transform:uppercase; font-size:12px; color:var(--terra); font-weight:700; }}
  h1 {{ font-size:34px; line-height:1.15; margin:10px 0 12px; }}
  .sub {{ color:var(--muted); max-width:70ch; }}
  .specs {{ display:flex; flex-wrap:wrap; gap:10px; margin-top:20px; }}
  .spec {{ background:#fff; border:1px solid var(--line); border-radius:999px; padding:6px 14px; font-size:13px; }}
  .lock {{ background:#fff; border:1px solid var(--line); border-left:4px solid var(--terra);
           border-radius:10px; padding:18px 20px; margin:18px 0; }}
  .lock h2 {{ margin:0 0 8px; font-size:15px; letter-spacing:.04em; text-transform:uppercase; }}
  .lock p {{ margin:0 0 12px; font-size:13px; color:var(--muted); }}
  .lock pre {{ margin:0; white-space:pre-wrap; font:13px/1.55 ui-monospace,SFMono-Regular,Menlo,monospace; }}
  .bar {{ display:flex; gap:10px; flex-wrap:wrap; margin:26px 0 8px; }}
  button {{
    font:inherit; font-size:14px; cursor:pointer; border-radius:8px; padding:9px 16px;
    border:1px solid var(--ink); background:var(--ink); color:var(--paper);
  }}
  button.ghost {{ background:transparent; color:var(--ink); border-color:var(--line); }}
  button.ghost:hover {{ border-color:var(--ink); }}
  h2.group {{
    font-size:20px; margin:52px 0 18px; padding-bottom:8px; border-bottom:1px solid var(--line);
    scroll-margin-top:20px;
  }}
  h2.group span {{ float:right; font-size:13px; color:var(--muted); font-weight:400; }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(330px,1fr)); gap:18px; }}
  .card {{ background:#fff; border:1px solid var(--line); border-radius:14px; padding:18px 18px 14px; }}
  .card header {{ display:flex; align-items:baseline; gap:10px; }}
  .num {{ font:700 13px/1 ui-monospace,monospace; color:#fff; background:var(--terra);
          border-radius:6px; padding:6px 8px; }}
  .card h3 {{ margin:0; font-size:17px; }}
  .meta {{ display:flex; gap:8px; margin:12px 0 10px; }}
  .chip {{ font-size:11px; text-transform:uppercase; letter-spacing:.06em; border-radius:999px;
           padding:4px 10px; border:1px solid var(--line); color:var(--muted); }}
  .chip.t {{ background:#f2f5ee; border-color:#dbe3d2; color:var(--sage); }}
  .card pre {{
    margin:0; max-height:190px; overflow:auto; background:#fdfaf4; border:1px solid var(--line);
    border-radius:8px; padding:12px; font:12px/1.55 ui-monospace,SFMono-Regular,Menlo,monospace;
    white-space:pre-wrap; word-break:break-word;
  }}
  .note {{ font-size:12.5px; color:var(--muted); margin:10px 0 0; border-left:3px solid var(--gold);
           padding-left:10px; }}
  .row {{ display:flex; align-items:center; gap:10px; margin-top:12px; }}
  .row button {{ padding:6px 12px; font-size:13px; }}
  .ok {{ font-size:12px; color:var(--sage); opacity:0; transition:opacity .2s; }}
  .ok.on {{ opacity:1; }}
  section.notes {{ margin-top:64px; background:#fff; border:1px solid var(--line);
                   border-radius:14px; padding:26px 28px; }}
  section.notes h2 {{ margin-top:0; font-size:20px; }}
  section.notes h3 {{ font-size:15px; margin:26px 0 8px; text-transform:uppercase; letter-spacing:.05em; }}
  section.notes ul {{ margin:0; padding-left:20px; }}
  section.notes li {{ margin:6px 0; }}
  table {{ border-collapse:collapse; width:100%; margin-top:10px; font-size:14px; }}
  th,td {{ border-bottom:1px solid var(--line); text-align:left; padding:8px 10px; }}
  th {{ font-size:12px; text-transform:uppercase; letter-spacing:.05em; color:var(--muted); }}
  code {{ background:#f2ece0; padding:1px 5px; border-radius:4px; font-size:13px; }}
  footer {{ margin-top:44px; color:var(--muted); font-size:13px; }}
</style>
</head>
<body>
<div class="wrap">

<header class="top">
  <div class="kicker">Phase 3 &middot; Interior build</div>
  <h1>Cozy Cottage &mdash; 40 Bold &amp; Easy Interior Prompts</h1>
  <p class="sub">Every prompt below is pre-assembled as <b>STYLE&nbsp;LOCK + subject + NEGATIVE&nbsp;LOCK</b>.
  Copy one line into any image model and it will match the other 39. The locks are the whole game &mdash;
  40 pages with 40 different phrasings look like a clip-art bundle; 40 pages through one locked
  prefix look like one artist's book.</p>
  <div class="specs">
    <span class="spec">8.5 &times; 8.5 in trim</span>
    <span class="spec">40 interior pages</span>
    <span class="spec">Bold &amp; easy</span>
    <span class="spec">Adult coloring</span>
    <span class="spec">List price {PRICE}</span>
    <span class="spec">1:1 square, 300+ DPI</span>
  </div>
</header>

<div class="lock">
  <h2>Style lock &mdash; prefix every prompt</h2>
  <p>Do not vary the wording between pages. Vary only the subject.</p>
  <pre id="styleLock">{e(STYLE_LOCK.strip())}</pre>
  <div class="bar"><button class="ghost" data-copy="#styleLock">Copy style lock</button></div>
</div>

<div class="lock">
  <h2>Negative lock &mdash; suffix every prompt</h2>
  <p>This is what stops the three things that kill bold &amp; easy pages: gray shading, micro-detail, and garbled AI text.</p>
  <pre id="negLock">{e(NEGATIVE_LOCK.strip())}</pre>
  <div class="bar"><button class="ghost" data-copy="#negLock">Copy negative lock</button></div>
</div>

<div class="bar">
  <button id="copyAll">Copy all 40 prompts</button>
  <button class="ghost" id="copySubjects">Copy subjects only (for re-locking later)</button>
  <span class="ok" id="allOk">Copied</span>
</div>

{chr(10).join(cards)}

<section class="notes">
  <h2>Production notes</h2>

  <h3>Page math &mdash; the free 64 pages</h3>
  <p>KDP's US black-ink paperback schedule is <code>$1.00 fixed + $0.012/page</code> with a
  <b>$2.30 minimum</b> that covers everything from 24 up to 108 pages. That means a 44-page book
  and a 108-page book cost the same to print. Single-sided printing &mdash; the standard for bold
  &amp; easy because markers bleed &mdash; is therefore <b>free</b> for this book:</p>
  <table>
    <tr><th>Interior</th><th>Pages</th><th>Print cost</th><th>Royalty @ {PRICE} (60%)</th></tr>
    <tr><td>4 front matter + 40 designs, back-to-back</td><td>44</td><td>$2.30</td><td>$3.69</td></tr>
    <tr><td>4 front matter + 40 single-sided designs</td><td>84</td><td>$2.30 (still under the floor)</td><td>$3.69</td></tr>
    <tr><td>6 front/back matter + 40 single-sided + 6 bonus</td><td>98</td><td>$2.30</td><td>$3.69</td></tr>
    <tr><td>&hellip;but crossing 108 pages</td><td>110</td><td>$2.32 and climbing</td><td>drops</td></tr>
  </table>
  <p><b>Recommendation:</b> ship 4 front matter pages + 40 single-sided designs + blank versos +
  2 back matter pages = <b>86 pages</b>. Under the floor, so it costs the same as the 44-page
  version, and you get the marker-friendly single-sided interior that the bold &amp; easy buyer
  expects. Verify against KDP's printing-cost page before you set the price &mdash; the schedule
  changes.</p>

  <h3>Cut list &mdash; if the listing must be a true 40-page book</h3>
  <p>If your listing promises "40 pages" rather than "40 designs", drop these four and ship
  4 front matter + 36 single-sided designs = 76 pages. Every group stays represented.</p>
  <ul>{cut_rows}</ul>

  <h3>Front matter (4 pages, no prompts needed)</h3>
  <ul>
    <li><b>p1</b> Half title / title page &mdash; reuse the page 1 cottage as a small centered vignette, 40% size</li>
    <li><b>p2</b> "This book belongs to" &mdash; two ruled lines, one small tulip</li>
    <li><b>p3</b> How to use &mdash; 3 short lines: single-sided, thick lines, any medium</li>
    <li><b>p4</b> Color test page &mdash; six empty swatch circles</li>
  </ul>

  <h3>Generation workflow</h3>
  <ul>
    <li><b>1.</b> Generate page 1 first. Iterate until it is exactly right. That image becomes your style reference.</li>
    <li><b>2.</b> Feed page 1 back as an image reference / style reference for pages 2&ndash;40. This is the single biggest consistency lever you have.</li>
    <li><b>3.</b> Batch by group, 8 at a time, so drift is easy to spot.</li>
    <li><b>4.</b> Upscale to 3000 &times; 3000 px minimum (8.5 in at 300 DPI = 2550 px; 3000 gives you bleed headroom).</li>
    <li><b>5.</b> Cleanup: convert to grayscale, levels/threshold to crush gray to pure white, then check that no line is thinner than ~12 px at 300 DPI (about 1 mm printed).</li>
    <li><b>6.</b> Assemble at 8.75 &times; 8.75 in with 0.125 in bleed; keep all art inside a 0.5 in safe margin.</li>
  </ul>

  <h3>Per-model parameters</h3>
  <ul>
    <li><b>Midjourney:</b> append <code>--ar 1:1 --style raw</code>; use <code>--sref</code> pointing at page 1 and <code>--cref</code> if you want a recurring cat. <code>--style raw</code> matters &mdash; the default MJ look adds shading you do not want.</li>
    <li><b>Ideogram:</b> strongest at clean line art and best at obeying "no text"; use its Magic Prompt off and paste the full locked prompt verbatim.</li>
    <li><b>Flux / SDXL:</b> paste the negative lock into the negative field instead of the prompt tail, and drop guidance to ~3.5 so it stops adding texture.</li>
  </ul>

  <h3>The five AI traps in this deck</h3>
  <ul>
    <li><b>Invented text</b> &mdash; pages 8, 10, 19, 21, 27. Jars, books, parcels, seed packets and picture frames all come back with gibberish writing. Regenerate; do not Photoshop it out.</li>
    <li><b>Gray "glow"</b> &mdash; pages 4 and 38. Ask for "unfilled white windows with thick outlines".</li>
    <li><b>Wispy smoke and steam</b> &mdash; pages 2, 12, 22. Must be thick closed outlines.</li>
    <li><b>Micro-spots</b> &mdash; page 31 mushroom caps. Small dots are the #1 "this isn't bold and easy" review complaint.</li>
    <li><b>Quilt grids</b> &mdash; page 33. Ask for "6 large patchwork squares", not a patchwork quilt.</li>
  </ul>

  <h3>QA gate &mdash; every page must pass all six</h3>
  <ul>
    <li>One subject, centered, breathing room on all four sides</li>
    <li>Line weight visibly identical to page 1</li>
    <li>Pure black lines on pure white &mdash; zero gray pixels</li>
    <li>No text, no numbers, no watermark</li>
    <li>Nothing important within 0.5 in of any trim edge</li>
    <li>Colorable in under 5 minutes with a chisel marker</li>
  </ul>
</section>

<footer>
  Generated by <code>build.py</code> in this folder. Edit the <code>PAGES</code> list there and
  re-run <code>python3 build.py</code> to regenerate prompts.json, prompts.csv,
  phase3-interior-prompts.md and this file.
</footer>

</div>
<script>
const toast = el => {{ el.classList.add('on'); setTimeout(() => el.classList.remove('on'), 1400); }};
async function copy(text, okEl) {{
  try {{ await navigator.clipboard.writeText(text); if (okEl) toast(okEl); }}
  catch (e) {{
    const t = document.createElement('textarea'); t.value = text; document.body.appendChild(t);
    t.select(); document.execCommand('copy'); t.remove(); if (okEl) toast(okEl);
  }}
}}
document.querySelectorAll('[data-copy]').forEach(b =>
  b.onclick = () => copy(document.querySelector(b.dataset.copy).innerText, b.nextElementSibling));
document.querySelectorAll('.card').forEach(c => {{
  const btn = c.querySelector('.copy'), ok = c.querySelector('.ok');
  btn.onclick = () => copy(c.dataset.prompt, ok);
}});
document.getElementById('copyAll').onclick = () => copy(
  PROMPTS.join('\\n\\n'), document.getElementById('allOk'));
document.getElementById('copySubjects').onclick = () => copy(
  SUBJECTS.map((s,i) => String(i+1).padStart(2,'0') + '. ' + s).join('\\n'),
  document.getElementById('allOk'));
</script>
<script>
const PROMPTS = {json.dumps([p["prompt"] for p in PAGES])};
const SUBJECTS = {json.dumps([p["subject"] for p in PAGES])};
</script>
</body>
</html>
'''
    with open(os.path.join(OUT_DIR, "phase3-interior-prompts.html"), "w") as f:
        f.write(doc)


if __name__ == "__main__":
    write_json()
    write_csv()
    write_md()
    write_html()
    print(f"wrote 4 files for {len(PAGES)} pages -> {OUT_DIR}")
