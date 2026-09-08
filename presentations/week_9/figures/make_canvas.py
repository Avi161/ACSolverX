#!/usr/bin/env python3
"""Turn the rendered week-9 deck into Design Component artboards.

    PYTHONPATH=. python3 presentations/week_9/figures/make_canvas.py

WHY IT RENDERS RATHER THAN RE-TYPES
-----------------------------------
The slide copy already exists once, in content.js, interpolated from stats.js. A
second hand-written copy for the canvas would be a second source of truth, and the
two would drift on the first wording change -- which is the exact failure this
project keeps guarding against. So this opens the GENERATED standalone deck in a
headless browser, lets the real renderer build the slides, and lifts each finished
slide out as an artboard. The canvas is the deck, by construction.

It reads standalone.html rather than the multi-file deck because standalone already
has every figure inlined as <svg>; an artboard cannot fetch a sibling file.

Output: presentations/week_9/canvas/{*.dc.html, canvas.json}, ready to seed.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WEEK = os.path.dirname(HERE)
OUTDIR = os.path.join(WEEK, "canvas")
SRC = os.path.join(WEEK, "standalone.html")

# Artboard stems, in slide order. Slide 1 must be Main -- the editor treats it as
# the entry artboard. The rest are named for what they show, so the canvas is
# navigable by name rather than by number.
STEMS = [
    "Main", "Populations", "Cascade", "Pattern", "BinsAutMin", "BinsExtended",
    "BandTable", "Compare", "Arms", "ArmsOnBands", "Stages", "Starvation",
    "TenMillion", "AutMinHarder", "U124", "Appendix",
]

W, H = 1440, 820          # the deck's own slide box
COLS, GAP_X, GAP_Y = 4, 140, 200

EXTRACT = r"""
const {chromium} = require('/opt/node22/lib/node_modules/playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({viewport: {width: %d, height: %d}});
  await p.goto('file://%s');
  await p.waitForTimeout(1500);
  const out = await p.evaluate(() => ({
    css: document.querySelector('style').textContent,
    slides: Array.from(document.querySelectorAll('.slide')).map(s => s.outerHTML),
  }));
  process.stdout.write(JSON.stringify(out));
  await b.close();
})();
"""


def extract():
    js = EXTRACT % (W, H, SRC)
    env = dict(os.environ, NODE_PATH="/opt/node22/lib/node_modules")
    r = subprocess.run(["node", "-e", js], capture_output=True, text=True, env=env)
    if r.returncode != 0:
        sys.exit("render failed:\n" + r.stderr[-2000:])
    return json.loads(r.stdout)


def artboard(css, slide_html):
    """One .dc.html. Static -- no holes, so no <script data-dc-script> at all.

    The deck's own CSS rides in <helmet> unchanged, minus the rules that only make
    sense inside a scrolling deck (fixed chrome, 100vh scroll-snap): on an artboard
    the slide IS the frame, so it is laid out at a fixed size instead.
    """
    css = re.sub(r"#(deck|counter|dots|progress|lightbox|err)\b[^{]*\{[^}]*\}", "", css)
    css = css.replace("height:100vh;scroll-snap-align:start;",
                      f"height:{H}px;width:{W}px;")
    return (
        "<!doctype html>\n<html>\n<head>\n"
        '  <meta charset="utf-8">\n'
        '  <script src="./support.js"></script>\n'
        "</head>\n<body>\n<x-dc>\n<helmet>\n  <style>\n"
        "  body{margin:0;background:#ffffff;}\n"
        f"{css}\n  </style>\n</helmet>\n{slide_html}\n</x-dc>\n</body>\n</html>\n"
    )


def main():
    if not os.path.exists(SRC):
        sys.exit("standalone.html missing -- run make_figures.py first")
    os.makedirs(OUTDIR, exist_ok=True)
    data = extract()
    slides, css = data["slides"], data["css"]
    if len(slides) != len(STEMS):
        sys.exit(f"deck has {len(slides)} slides but {len(STEMS)} stems are named -- "
                 "add or remove a stem so the canvas keeps stable artboard names")

    boards = []
    for i, (stem, html) in enumerate(zip(STEMS, slides)):
        with open(os.path.join(OUTDIR, stem + ".dc.html"), "w") as fh:
            fh.write(artboard(css, html))
        boards.append({"file": stem + ".dc.html",
                       "x": (i % COLS) * (W + GAP_X),
                       "y": (i // COLS) * (H + GAP_Y),
                       "w": W, "h": H, "title": f"{i + 1:02d} · {stem}"})

    manifest = {
        "artboards": boards,
        "annotations": [{
            "id": "how-to-edit", "x": 0, "y": -190, "w": 900,
            "text": ("Week 9 · the AC19 cascade. Retype any wording in place and Save.\n"
                     "Numbers come from the campaign jsonl and are regenerated, so edit "
                     "words, not figures — tell me which number looks wrong and I will "
                     "check it against the archive."),
        }],
        "launch": {"view": "canvas"},
    }
    with open(os.path.join(OUTDIR, "canvas.json"), "w") as fh:
        json.dump(manifest, fh, indent=2)

    print(f"wrote {len(boards)} artboards + canvas.json to {os.path.relpath(OUTDIR)}")
    print("  " + ", ".join(b["file"] for b in boards))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
