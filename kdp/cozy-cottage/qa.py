#!/usr/bin/env python3
"""Automated QA gate for bold & easy coloring pages.

Implements the six-point gate from the Phase 3 deck as measurements, so a page
is judged by numbers instead of vibes. Run it on every generated page BEFORE it
goes into the interior PDF.

    python3 qa.py pages/*.png
    python3 qa.py pages/*.png --json     # machine-readable
    python3 qa.py pages/page-01*.png --ref   # save as the style reference baseline

Checks
  1. GRAYSCALE    pure black ink on pure white paper - no color cast
  2. NO SHADING   almost no mid-gray pixels (the #1 bold & easy killer)
  3. LINE WEIGHT  stroke width normalized to 300 DPI at 8.5 in wide
  4. DENSITY      ink coverage - too empty reads as lazy, too dense reads as intricate
  5. SHAPES       connected-component count - the proxy for "is this fiddly"
  6. SAFE AREA    nothing important inside the outer 5% (trim/bind margin)

Requires: pillow, numpy, scipy  (pip install --break-system-packages pillow numpy scipy)
"""

import argparse
import glob
import json
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

# ---- targets ---------------------------------------------------------------
# Normalized line weight: measured px scaled to an 8.5 in page at 300 DPI (2550 px).
PLACE_WIDTH_PX = 2550          # 8.5 in * 300 DPI
MIN_SOURCE_PX = 2550           # below this the file cannot hold 300 DPI

T = {
    "gray_max": 8.0,           # % mid-tone pixels
    "gray_ideal": 3.0,
    "cast_max": 6.0,           # mean channel spread
    "stroke_min": 8.0,         # px at 300 DPI  (~0.7 mm printed)
    "stroke_ideal_min": 12.0,  # (~1.0 mm)
    "stroke_ideal_max": 28.0,  # (~2.4 mm)
    "stroke_max": 40.0,
    "fiddle_max": 45.0,        # ink runs per inked row; hero scenes sit ~26, vignettes ~12
    "fiddle_ideal": 30.0,
    "pocket_min": 0.25,        # median colorable pocket as % of page
    "ink_min": 4.0,            # % of page covered in ink
    "ink_ideal_min": 7.0,
    "ink_ideal_max": 20.0,
    "ink_max": 28.0,
    "shapes_min": 3,
    "shapes_ideal_min": 5,
    "shapes_ideal_max": 22,
    "shapes_max": 45,
    "edge_max": 6.0,           # % of ink sitting in the outer 5% frame
    "edge_ideal": 1.5,
}


def run_lengths(mask):
    """Every horizontal run of True in `mask`, as lengths in px."""
    idx = np.flatnonzero(np.diff(np.concatenate(
        ([0], mask.astype(np.int8).ravel(), [0]))).astype(np.int64))
    return idx[1::2] - idx[0::2]


def analyse(path):
    im = Image.open(path).convert("RGB")
    w, h = im.size
    a = np.asarray(im).astype(np.int16)

    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    lum = (0.299 * r + 0.587 * g + 0.114 * b)
    cast = float(max(np.abs(r - g).mean(), np.abs(g - b).mean(), np.abs(r - b).mean()))

    # 1/2 shading: mid-tones that are neither paper nor ink
    gray = ((lum > 35) & (lum < 225)).mean() * 100.0

    ink = lum < 128
    ink_pct = ink.mean() * 100.0

    # 3 line weight. Distance-transform means overestimate because ink pixels
    # cluster at stroke centres; run lengths measure the stroke directly.
    # (A run through a diagonal stroke overestimates slightly, so this is a
    # conservative upper bound - it errs toward flagging thin lines.)
    scale = PLACE_WIDTH_PX / float(w) if w else 1.0
    hr = run_lengths(ink)
    vr = run_lengths(ink.T)
    stroke = float(np.median(np.concatenate([hr, vr])) * scale)
    # hairlines: runs that are genuinely thin once scaled to 300 DPI
    # (4 source px on a 1024px render is NOT thin - that is the normal stroke)
    hairlines = float((np.concatenate([hr, vr]) * scale < 10.0).mean() * 100.0)
    stroke_dt = 0.0
    if ink.any():
        d = ndimage.distance_transform_edt(ink)[ink]
        stroke_dt = float(d.mean() * 4.0 * scale)

    # 5a fiddliness: how many separate ink runs the busiest rows contain.
    # Low = big calm shapes (bold & easy). High = intricate detail.
    per_row = np.array([(np.abs(np.diff(row.view(np.int8))).sum() // 2) for row in ink],
                       dtype=np.float64)
    fiddle = float(np.percentile(per_row, 95))

    # 5b shape count: connected components, ignoring specks
    lbl, n = ndimage.label(ink)
    if n:
        sizes = ndimage.sum(ink, lbl, range(1, n + 1))
        min_area = max(30, 0.0002 * w * h)
        shapes = int((sizes >= min_area).sum())
    else:
        shapes = 0

    # colorable pockets: enclosed white regions big enough to actually color
    white = ~ink
    wlbl, wn = ndimage.label(white)
    wsizes = np.sort(ndimage.sum(white, wlbl, range(1, wn + 1)))[::-1]
    colorable = wsizes[wsizes > 0.002 * white.size]
    pocket = float(np.median(colorable) / white.size * 100.0) if len(colorable) else 0.0
    pockets = int(len(colorable))

    # 6 safe area: share of ink in the outer 5% frame
    m = int(min(w, h) * 0.05)
    frame = np.ones_like(ink)
    frame[m:-m, m:-m] = False
    edge = (ink & frame).sum() / max(ink.sum(), 1) * 100.0

    checks = [
        ("grayscale", cast, T["cast_max"], cast <= T["cast_max"], "mean channel spread"),
        ("no shading", gray, T["gray_max"], gray <= T["gray_ideal"],
         gray <= T["gray_max"], "% mid-tone pixels"),
        ("line weight", stroke, (T["stroke_min"], T["stroke_max"]),
         T["stroke_ideal_min"] <= stroke <= T["stroke_ideal_max"],
         T["stroke_min"] <= stroke <= T["stroke_max"], "px @300dpi"),
        ("hairlines", hairlines, 10.0, hairlines <= 2.0, hairlines <= 10.0, "% runs < 4px"),
        ("fiddliness", fiddle, T["fiddle_max"], fiddle <= T["fiddle_ideal"],
         fiddle <= T["fiddle_max"], "runs/row (p95)"),
        ("pockets", pocket, T["pocket_min"], pocket >= 0.30, pocket >= T["pocket_min"],
         "% median colorable area"),
        ("density", ink_pct, (T["ink_min"], T["ink_max"]),
         T["ink_ideal_min"] <= ink_pct <= T["ink_ideal_max"],
         T["ink_min"] <= ink_pct <= T["ink_max"], "% ink"),
        ("shapes", shapes, (T["shapes_min"], T["shapes_max"]),
         T["shapes_ideal_min"] <= shapes <= T["shapes_ideal_max"],
         T["shapes_min"] <= shapes <= T["shapes_max"], "components"),
        ("safe area", edge, T["edge_max"], edge <= T["edge_ideal"],
         edge <= T["edge_max"], "% ink in outer 5%"),
    ]

    results = []
    for c in checks:
        name, val, limit = c[0], c[1], c[2]
        if len(c) == 6:
            ok, tol, unit = c[3], c[4], c[5]
        else:
            ok, tol, unit = c[3], c[3], c[4]
        results.append(dict(check=name, value=round(float(val), 2), unit=unit,
                            status="PASS" if ok else ("WARN" if tol else "FAIL")))

    res = dict(
        file=os.path.basename(path), width=w, height=h,
        square=abs(w - h) <= 2,
        dpi_at_8p5in=round(w / 8.5, 1),
        resolution_ok=w >= MIN_SOURCE_PX,
        grayscale_cast=round(cast, 2),
        gray_pct=round(gray, 2),
        stroke_px_300dpi=round(stroke, 1),
        stroke_dt_px_300dpi=round(stroke_dt, 1),
        hairline_pct=round(hairlines, 2),
        stroke_mm=round(stroke / 300.0 * 25.4, 2),
        fiddliness=round(fiddle, 1),
        pocket_pct=round(pocket, 3),
        pockets=pockets,
        ink_pct=round(ink_pct, 2),
        shapes=shapes,
        edge_ink_pct=round(edge, 2),
        checks=results,
    )
    res["verdict"] = ("FAIL" if any(c["status"] == "FAIL" for c in results)
                      else "WARN" if any(c["status"] == "WARN" for c in results)
                      else "PASS")
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--ref", action="store_true",
                    help="write this page's measurements to baseline.json as the style reference")
    a = ap.parse_args()

    files = []
    for pat in a.files:
        files.extend(sorted(glob.glob(pat)) or [pat])

    rows = [analyse(f) for f in files]

    if a.json:
        print(json.dumps(rows, indent=2))
    else:
        pad = max(len(r["file"]) for r in rows)
        for r in rows:
            print(f"\n{'=' * 78}\n{r['file']:<{pad}}  {r['verdict']}   "
                  f"[{r['width']}x{r['height']}, {r['dpi_at_8p5in']} DPI at 8.5in]")
            print("-" * 78)
            print(f"  {'CHECK':<14}{'VALUE':>10}  {'UNIT':<20}STATUS")
            for c in r["checks"]:
                print(f"  {c['check']:<14}{c['value']:>10}  {c['unit']:<20}{c['status']}")
            print(f"\n  stroke {r['stroke_px_300dpi']}px @300dpi = {r['stroke_mm']}mm printed "
                  f"(DT est {r['stroke_dt_px_300dpi']}px) | hairlines {r['hairline_pct']}% | "
                  f"fiddliness {r['fiddliness']}")
            print(f"  ink {r['ink_pct']}% | shapes {r['shapes']} | colorable pockets "
                  f"{r['pockets']} (median {r['pocket_pct']}%) | cast {r['grayscale_cast']}")
            if not r["square"]:
                print("  ! not square - the deck is 1:1")
            if not r["resolution_ok"]:
                print(f"  ! only {r['width']}px - upscale to >=2550px before placing at 8.5in/300DPI")
        print()

    if a.ref and rows:
        base = dict(
            file=rows[0]["file"],
            note="Style reference. Every later page must stay within these tolerances.",
            stroke_px_300dpi=rows[0]["stroke_px_300dpi"],
            stroke_mm=rows[0]["stroke_mm"],
            ink_pct=rows[0]["ink_pct"],
            gray_pct=rows[0]["gray_pct"],
            fiddliness=rows[0]["fiddliness"],
            shapes=rows[0]["shapes"],
            pockets=rows[0]["pockets"],
            pocket_pct=rows[0]["pocket_pct"],
            edge_ink_pct=rows[0]["edge_ink_pct"],
            tolerances=dict(
                stroke_pct=0.35, ink_pct=0.35, gray_pct=0.5,
                fiddliness_pct=0.45, shapes_pct=0.40, edge_ratio=3.0,
            ),
        )
        p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "baseline.json")
        with open(p, "w") as f:
            json.dump(base, f, indent=2)
            f.write("\n")
        print(f"style reference baseline saved from {rows[0]['file']} -> {p}")

    sys.exit(1 if any(r["verdict"] == "FAIL" for r in rows) else 0)


if __name__ == "__main__":
    main()
