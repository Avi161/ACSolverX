#!/usr/bin/env python3
"""Re-seed the published design-canvas payload from the regenerated artboards.

    PYTHONPATH=. python3 presentations/week_9/figures/reseed_canvas.py

WHY THIS EXISTS
---------------
`make_canvas.py` writes `canvas/*.dc.html` + `canvas.json`. The thing that
actually gets PUBLISHED is a single 2.9 MB page that carries the canvas editor
AND the artboards together: the artboards live inside it as JSON, in the
`<script id="appifact-doc">` block. Re-running make_canvas.py therefore updates
the sources and leaves the published payload stale -- which is exactly what
happened after the 10,000-node rung landed and every figure changed.

This rewrites `content.files` in that block from the current canvas directory
and leaves everything else in the page alone. In particular it PRESERVES
`comments`: those are reader feedback left on the published artifact, and
regenerating a figure is not a reason to throw them away.

An artboard that was renamed disappears by construction, since the new file set
replaces the old one wholesale rather than merging into it.
"""
from __future__ import annotations

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WEEK = os.path.dirname(HERE)
CANVAS = os.path.join(WEEK, "canvas")
PAYLOAD = os.path.join(WEEK, "ac19-cascade-week-9.html")
TAG = re.compile(r'<script[^>]*id="appifact-doc"[^>]*>')


def read_canvas():
    """`{filename: text}` for every artboard plus canvas.json, in canvas order."""
    manifest_path = os.path.join(CANVAS, "canvas.json")
    if not os.path.exists(manifest_path):
        sys.exit("canvas/canvas.json missing -- run make_canvas.py first")
    manifest = json.load(open(manifest_path))
    files = {}
    for board in manifest["artboards"]:
        path = os.path.join(CANVAS, board["file"])
        if not os.path.exists(path):
            sys.exit(f"{board['file']} named in canvas.json but not on disk")
        files[board["file"]] = open(path, encoding="utf-8").read()
    files["canvas.json"] = open(manifest_path, encoding="utf-8").read()
    return files


def main():
    if not os.path.exists(PAYLOAD):
        sys.exit(f"{PAYLOAD} missing -- it is the published page, seeded once by "
                 "the design helper; this script only refreshes its contents")
    page = open(PAYLOAD, encoding="utf-8").read()
    m = TAG.search(page)
    if not m:
        sys.exit("no <script id=\"appifact-doc\"> block in the payload")
    # raw_decode, not index("</script>"): the JSON is one object, so the decoder
    # itself finds its end. Searching for the closing tag instead breaks the
    # moment an artboard's own "</script>" appears INSIDE the JSON -- which is
    # exactly what a previous version of this script caused, by writing the
    # payload back with literal "<".
    doc, end = json.JSONDecoder().raw_decode(page, m.end())

    old = set(doc["content"]["files"])
    files = read_canvas()
    doc["content"]["files"] = files
    new = set(files)

    # `comments` rides through untouched -- see the module docstring.
    #
    # "<" MUST be escaped. This JSON lives inside a <script> element, so the
    # first literal "</script>" in an artboard's own markup would terminate the
    # block early and truncate the document -- the artboards each carry a
    # <script src="./support.js"></script>, so that is every one of them. The
    # original payload escapes "<" as \u003c for this reason; matching it is
    # not cosmetic. "<" never occurs in JSON outside a string, so the blanket
    # replace is safe.
    body = json.dumps(doc, ensure_ascii=False).replace("<", "\\u003c")
    open(PAYLOAD, "w", encoding="utf-8").write(page[:m.end()] + body + page[end:])

    print(f"reseeded {len(files)} files into {os.path.relpath(PAYLOAD)} "
          f"({len(body) / 2**20:.1f} MB of JSON, "
          f"{len(doc.get('comments', []))} comment(s) preserved)")
    for label, s in (("added", new - old), ("removed", old - new)):
        if s:
            print(f"  {label}: {', '.join(sorted(s))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
