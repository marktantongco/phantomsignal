#!/usr/bin/env python3
"""Build print-resolution masters from generated page renders.

Generators emit ~1024px squares, but an 8.5in page needs 2550px for 300 DPI.
Line art is the easy case to upscale because there is nothing to invent: we only
need the edges to stay crisp. LANCZOS + hard threshold does that, and the
threshold has a bonus - it collapses the anti-aliased gray edge pixels to pure
black or pure white, so the printed page carries zero gray ink.

    python3 print_master.py pages/page-01-the-round-door.png
    python3 print_master.py "pages/page-*.png" --all

Outputs <name>.print.png next to the source (or in place with --all).
"""

import argparse
import os
import sys

import numpy as np
from PIL import Image, ImageFilter

PLACE_WIDTH_PX = 2550          # 8.5 in * 300 DPI
MIN_STROKE_AT_300DPI = 10.0    # below this a line will look broken in print


def make_master(src, dst, thresh=160):
    im = Image.open(src).convert("L")
    w, h = im.size
    if w != h:
        print(f"  ! {os.path.basename(src)} is {w}x{h}, not square - placing at 8.5in "
              f"will letterbox it")
    size = (PLACE_WIDTH_PX, int(round(h * PLACE_WIDTH_PX / w)))
    big = im.resize(size, Image.LANCZOS)

    # A touch of unsharp before thresholding keeps the stroke edge from going
    # soft at 2.5x; then hard-threshold to pure black on pure white.
    big = big.filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=2))
    a = np.asarray(big)
    out = np.where(a < thresh, 0, 255).astype(np.uint8)
    Image.fromarray(out, "L").save(dst, "PNG", optimize=True)

    # verify the stroke survived the resize
    from qa import run_lengths
    ink = out < 128
    scale = PLACE_WIDTH_PX / size[0]
    rl = np.concatenate([run_lengths(ink), run_lengths(ink.T)]) * scale
    stroke = float(np.median(rl))
    hair = float((rl < MIN_STROKE_AT_300DPI).mean() * 100)
    print(f"  {os.path.basename(dst)}: {size[0]}px | stroke {stroke:.1f}px @300dpi "
          f"({stroke / 300 * 25.4:.2f}mm) | thin runs {hair:.1f}% | gray 0.00%")
    if stroke < MIN_STROKE_AT_300DPI:
        print(f"  ! WARNING: median stroke {stroke:.1f}px is under "
              f"{MIN_STROKE_AT_300DPI}px - it will look thin in print")
    return stroke, hair


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--all", action="store_true", help="overwrite the source files")
    a = ap.parse_args()
    for f in a.files:
        if not os.path.exists(f):
            print(f"  ! missing {f}")
            continue
        base, ext = os.path.splitext(f)
        dst = f if a.all else base + ".print.png"
        make_master(f, dst)
    return 0


if __name__ == "__main__":
    sys.exit(main())
