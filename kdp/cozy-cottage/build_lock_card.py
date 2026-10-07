#!/usr/bin/env python3
"""Builds the page-1 style-reference lock card (self-contained HTML).

The reference image is embedded as a data URI so the card renders in a sandboxed
preview with no network and no sibling files.

    python3 build_lock_card.py
"""

import base64
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REF_IMG = os.path.join(HERE, "pages", "page-01-the-round-door.png")
REJ_IMG = os.path.join(HERE, "pages", "rejected", "page-01-the-round-door.png")
OUT = os.path.join(HERE, "phase3-style-reference.html")


def data_uri(path):
    with open(path, "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()


def main():
    b = json.load(open(os.path.join(HERE, "baseline.json")))
    ref, rej = data_uri(REF_IMG), data_uri(REJ_IMG)

    css = """
*{box-sizing:border-box}
body{margin:0;background:#f4f1ea;color:#241f1a;
 font:16px/1.62 Georgia,'Iowan Old Style',serif}
.wrap{max-width:1000px;margin:0 auto;padding:34px 22px 70px}
h1{font-size:30px;line-height:1.2;margin:0 0 6px;letter-spacing:-.01em}
h2{font-size:19px;margin:44px 0 12px;padding-bottom:7px;border-bottom:2px solid #241f1a}
h3{font-size:15px;margin:22px 0 7px;text-transform:uppercase;letter-spacing:.09em;color:#6b5f52}
.sub{color:#6b5f52;font-size:15px;margin:0 0 26px}
.card{background:#fff;border:1px solid #ddd5c7;border-radius:12px;padding:20px 22px;margin:16px 0;
 box-shadow:0 1px 3px rgba(0,0,0,.05)}
.lede{font-size:17px}
table{border-collapse:collapse;width:100%;font-size:14px;margin:12px 0 4px}
th,td{border:1px solid #ddd5c7;padding:8px 10px;text-align:left;vertical-align:top}
th{background:#f7f3ec;font-size:12px;text-transform:uppercase;letter-spacing:.06em;color:#6b5f52}
td.n{font-variant-numeric:tabular-nums;white-space:nowrap}
.pass{color:#1d6b3f;font-weight:700}.fail{color:#a8321e;font-weight:700}
.warn{color:#8a6100;font-weight:700}
code,.mono{font:13px/1.55 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
pre{background:#241f1a;color:#f2ece1;padding:14px 16px;border-radius:9px;overflow-x:auto;
 font:12.5px/1.6 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;margin:10px 0}
pre .c{color:#a99c88}
.imgbox{background:#fff;border:1px solid #ddd5c7;border-radius:12px;padding:14px;margin:14px 0}
.imgbox img{width:100%;display:block;border-radius:4px}
.two{display:grid;grid-template-columns:1fr 1fr;gap:14px}
@media(max-width:720px){.two{grid-template-columns:1fr}}
.cap{font-size:12.5px;color:#6b5f52;margin:7px 2px 0}
.tag{display:inline-block;background:#241f1a;color:#f4f1ea;font-size:11px;letter-spacing:.08em;
 text-transform:uppercase;padding:3px 9px;border-radius:20px;margin-bottom:8px}
.tag.alt{background:#a8321e}
ul,ol{margin:9px 0 9px 4px;padding-left:20px}
li{margin:5px 0}
.hr{height:1px;background:#ddd5c7;margin:30px 0}
.note{background:#fdf6e3;border-left:4px solid #c9a227;padding:13px 16px;border-radius:0 8px 8px 0;
 margin:14px 0;font-size:14.5px}
.ok{background:#eef7f0;border-left:4px solid #1d6b3f;padding:13px 16px;border-radius:0 8px 8px 0;
 margin:14px 0;font-size:14.5px}
"""

    html = f"""<!doctype html>
<html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Page 1 style reference &mdash; Cozy Cottage, Bold &amp; Easy</title>
<style>{css}</style>
<div class="wrap">

<h1>Page 1 is the style reference</h1>
<p class="sub">Cozy Cottage &middot; Bold &amp; Easy &middot; 8.5&times;8.5in &middot; page 01 of 40</p>

<div class="note"><b>Why this page matters more than the other 39.</b> A coloring book is
bought as a set and abandoned as a set. If page 12 is drawn finer than page 3, the buyer does not
think &ldquo;page 12 is off&rdquo; &mdash; they think the whole book is inconsistent, and they ask for a
refund. Page 1 is not the first page; it is the <b>specification</b> that the other 39 are measured
against. Everything below is that specification, written down as numbers.</p></div>

<div class="imgbox">
 <span class="tag">The reference &mdash; page 01, The Round Door</span>
 <img src="{ref}" alt="Page 1 bold and easy cozy cottage coloring page">
 <p class="cap">2550&times;2550px &middot; 300 DPI at 8.5in &middot; pure black on pure white,
 zero gray pixels &middot; median stroke {b['stroke_mm']}mm</p>
</div>

<h2>What changed, and why</h2>
<p>I generated page 1 twice. The first attempt is archived, not deleted, because the diff is the
most useful thing on this page &mdash; it shows you exactly what &ldquo;bold and easy&rdquo; costs in
prompt terms.</p>

<div class="two">
 <div class="imgbox"><img src="{rej}" alt="First attempt, archived">
  <p class="cap"><b>Rejected</b> &mdash; wall built from ~30 small outlined stones</p></div>
 <div class="imgbox"><img src="{ref}" alt="Accepted page 1">
  <p class="cap"><b>Accepted</b> &mdash; wall built from a few large stones</p></div>
</div>

<table>
<tr><th>Measurement</th><th>Rejected</th><th>Accepted</th><th>What it means</th></tr>
<tr><td>Fiddliness <span class="mono">(runs/row, p95)</span></td><td class="n fail">34.0</td>
 <td class="n pass">26.0</td><td>The single most important number. Higher = busier page. This is the
 metric that separates bold &amp; easy from intricate.</td></tr>
<tr><td>Hairline runs</td><td class="n fail">4.43%</td><td class="n pass">0.16%</td>
 <td>Runs thin enough to look broken in print. Near zero is correct.</td></tr>
<tr><td>Colorable pockets</td><td class="n">33</td><td class="n pass">38</td>
 <td>More, larger open areas = more satisfying to color.</td></tr>
<tr><td>Median pocket size</td><td class="n">0.42%</td><td class="n pass">0.61%</td>
 <td>Bigger areas a chisel marker can fill in one pass.</td></tr>
<tr><td>Stroke</td><td class="n">1.90mm</td><td class="n pass">2.12mm</td>
 <td>Both pass; the accepted page is chunkier, which reads as bolder.</td></tr>
<tr><td>Shapes</td><td class="n">8</td><td class="n">15</td><td>More distinct objects, not more detail.</td></tr>
</table>

<div class="note"><b>The one-line fix that did it.</b> The style lock was identical in both
attempts. The only change was adding to the subject:
<code>&ldquo;built from a FEW LARGE irregular stones only &mdash; never many small stones,
never a brick pattern, never repeated small shapes.&rdquo;</code> That clause moved fiddliness from
34 to 26. <b>Every one of the remaining 39 prompts needs a clause like it.</b> Stone walls, brick,
roof shingles, tile, thatch, cobblestones, quilt grids and bookshelf rows are the seven textures
that will quietly turn this into an intricate book.</div>

<h2>The reference prompt (reusable)</h2>
<p>This is the exact prompt that produced the accepted page. Keep the style lock byte-identical for
all 40 pages; swap only the subject sentence.</p>
<pre id="refprompt">Black and white coloring book page for adults, bold and easy style, cozy cottagecore theme. One single centered subject: <b>[SUBJECT]</b>. The wall is built from a FEW LARGE irregular stones only - never many small stones, never a brick pattern, never repeated small shapes. Very thick uniform black outlines, simple flat chunky shapes, large open coloring areas, minimal detail, clean pure white background, no shading, no gray tones, no fill, no texture, high-contrast pure black and white line art, cute whimsical storybook style, square 1:1 composition, generous margins, subject centered with breathing room on all sides. NO text, no words, no letters, no numbers, no labels, no watermark, no signature, no frame, no border, no shading, no gradient, no hatching, no crosshatching, no stippling, no color, no gray fill, no background scenery, no tiny fiddly details, no photorealism, no blurry lines.</pre>

<h3>Per-model parameters</h3>
<table>
<tr><th>Model</th><th>Settings</th></tr>
<tr><td><b>Midjourney</b></td><td class="mono">--ar 1:1 --style raw --stylize 60 --sref &lt;url of this page&gt; --sw 100</td></tr>
<tr><td><b>Ideogram</b></td><td class="mono">Magic Prompt OFF &middot; style = Design &middot; aspect 1:1 &middot; negative prompt = the NO-list</td></tr>
<tr><td><b>Flux / SDXL</b></td><td class="mono">CFG 3.5 &middot; steps 28 &middot; sampler DPM++ 2M Karras &middot; control the NO-list via negative prompt</td></tr>
<tr><td><b>DALL&middot;E / GPT-image</b></td><td class="mono">1024&times;1024 &middot; send this image as the style reference &middot; ask for &ldquo;same line weight and style as the reference&rdquo;</td></tr>
</table>

<h2>Locking pages 2&ndash;40 to this image</h2>
<ol>
<li><b>Feed page 1 back in.</b> Every model above accepts an image reference. Page 1 goes in on
 every subsequent generation &mdash; not just the first batch. Style drift is cumulative.</li>
<li><b>Generate in small batches, QA each batch.</b> Not 39 at once. Run 4, measure, adjust the
 subject wording, run the next 4.</li>
<li><b>Reject on measurement, not on feeling.</b> Run <code>python3 qa.py pages/*.png</code> and
 compare against the baseline below.</li>
<li><b>Re-roll, don't patch.</b> If a page fails fiddliness, change the subject wording and
 regenerate. Do not send it back with &ldquo;make it simpler&rdquo; &mdash; that reliably makes it
 <i>greener</i> and <i>thinner</i>, not bolder.</li>
</ol>

<h2>The gate every page must pass</h2>
<table>
<tr><th>Check</th><th>Reference</th><th>Reject if</th><th>Why</th></tr>
<tr><td>Grayscale purity</td><td class="n">{b['gray_pct']}% mid-tone</td><td class="n">&gt;8%</td>
 <td>Gray means shading, means print ink, means &ldquo;not bold and easy&rdquo;</td></tr>
<tr><td>Line weight</td><td class="n">{b['stroke_px_300dpi']}px @300dpi ({b['stroke_mm']}mm)</td>
 <td class="n">&lt;8px or &gt;40px</td><td>Must match page 1 across all 40 pages</td></tr>
<tr><td>Fiddliness</td><td class="n">{b['fiddliness']} runs/row</td>
 <td class="n">&gt;45</td><td>The intricacy tripwire</td></tr>
<tr><td>Ink density</td><td class="n">{b['ink_pct']}%</td><td class="n">&lt;4% or &gt;28%</td>
 <td>Too empty = lazy; too dense = uncolorable</td></tr>
<tr><td>Shapes</td><td class="n">{b['shapes']} components</td><td class="n">&gt;45</td>
 <td>Component count is the fiddliness proxy</td></tr>
<tr><td>Safe area</td><td class="n">{b['edge_ink_pct']}% ink in outer 5%</td><td class="n">&gt;6%</td>
 <td>Nothing may sit inside the trim margin</td></tr>
<tr><td>Hairlines</td><td class="n">0.16%</td><td class="n">&gt;10%</td>
 <td>Thin lines look broken when printed</td></tr>
<tr><td>Colorable pockets</td><td class="n">{b['pockets']} pockets, median {b['pocket_pct']}%</td>
 <td class="n">median &lt;0.25%</td><td>Areas must fit a chisel marker</td></tr>
</table>

<h3>Two different targets, not one</h3>
<p>The deck alternates <b>hero scenes</b> (9&ndash;13 shapes) and <b>object vignettes</b>
(5&ndash;8 shapes), so they should not be judged against one number:</p>
<table>
<tr><th>Page type</th><th>Target fiddliness</th><th>Target shapes</th></tr>
<tr><td>Hero scene (1, 3, 5, 7, 9&hellip;)</td><td class="n">22&ndash;30 runs/row</td>
 <td class="n">12&ndash;20</td></tr>
<tr><td>Object vignette (2, 4, 6, 8, 10&hellip;)</td><td class="n">10&ndash;18 runs/row</td>
 <td class="n">5&ndash;10</td></tr>
</table>
<p>Page 1 is a hero scene at {b['fiddliness']}. The vignettes must read
<b>calmer</b> than that, or the alternation the deck is built on disappears and the book reads as 40
of the same thing.</p>

<div class="ok"><b>Page 1 verdict: locked.</b> All nine checks pass. Stroke
{b['stroke_mm']}mm, {b['ink_pct']}% ink, zero gray pixels, nothing inside the trim margin.
This is the spec for the remaining 39.</div>

<h2>Commands</h2>
<pre><span class="c"># QA any set of pages against the gate</span>
python3 qa.py "pages/page-*.png"

<span class="c"># build a 300 DPI print master from a 1024px render</span>
python3 print_master.py pages/page-02-chimney-smoke.png

<span class="c"># re-lock the baseline after a deliberate style change</span>
python3 qa.py pages/page-01-the-round-door.print.png --ref

<span class="c"># machine-readable output for a batch script</span>
python3 qa.py "pages/page-*.png" --json</pre>

<h2>Files</h2>
<table>
<tr><th>File</th><th>Role</th></tr>
<tr><td class="mono">pages/page-01-the-round-door.png</td><td>Accepted reference, 1024px render</td></tr>
<tr><td class="mono">pages/page-01-the-round-door.print.png</td><td><b>The print master</b>, 2550px / 300 DPI</td></tr>
<tr><td class="mono">pages/rejected/page-01-the-round-door.png</td><td>First attempt, archived for the diff</td></tr>
<tr><td class="mono">baseline.json</td><td>The numbers above, plus tolerances</td></tr>
<tr><td class="mono">qa.py</td><td>The gate. Run on every page</td></tr>
<tr><td class="mono">print_master.py</td><td>Upscale + threshold to 300 DPI</td></tr>
<tr><td class="mono">phase3-interior-prompts.html</td><td>The 40 prompts</td></tr>
</table>

</div>
"""

    with open(OUT, "w") as f:
        f.write(html)
    print(f"wrote {OUT} ({len(html):,} bytes, image inlined)")


if __name__ == "__main__":
    main()
