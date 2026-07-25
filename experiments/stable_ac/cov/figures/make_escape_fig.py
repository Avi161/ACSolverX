"""The corrected picture for the eight: what each route to them actually costs.

Emits SVG, written by hand — the repo's other figures were made ad hoc on Colab
with matplotlib, which is not installed locally, and re-rendering a three-panel
chart whose producer is gone would silently change every arm on it. This draws
only the rows the escalation changed.

Reads `escape_b{budget}_summary.csv` (written by `allcov_escape_report.py`), so
every number on the figure is the one in the table.

    .venv/bin/python3 -m experiments.stable_ac.cov.figures.make_escape_fig --budget 20000
"""

import argparse
import csv
import math
import os

OUT_DIR = "results/stable_ac/cov/allcov_escape"

W, H = 980, 470
L, R, T = 96, 34, 96
ROW_H, ROW_GAP = 30, 6
X0, X1 = 8_000, 340_000          # log domain, covers 10k budget .. greedy worst

SERIES = [
    ("best_nodes", "best CoV — oracle, cheapest of ~170", "#3a5c88", "circle"),
    ("blind_restart_expected_nodes", "blind CoV restart — E[nodes], runnable", "#ab5433", "diamond"),
    ("heur_b100k_nodes", "tuned heap ordering — one search", "#0d6b5f", "square"),
    ("greedy_b1M_nodes", "plain greedy on the untransformed pair", "#8c9998", "triangle"),
]


def _repo_root():
    d = os.path.abspath(os.path.dirname(__file__))
    while d != "/":
        if os.path.isdir(os.path.join(d, "experiments")) and os.path.isdir(os.path.join(d, "data")):
            return d
        d = os.path.dirname(d)
    raise RuntimeError("repo root not found")


ROOT = _repo_root()


def x_of(v):
    lo, hi = math.log10(X0), math.log10(X1)
    return L + (math.log10(v) - lo) / (hi - lo) * (W - L - R)


def marker(kind, cx, cy, fill, r=5.0):
    if kind == "circle":
        return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{fill}"/>'
    if kind == "square":
        return (f'<rect x="{cx - r:.1f}" y="{cy - r:.1f}" width="{2 * r}" '
                f'height="{2 * r}" fill="{fill}"/>')
    if kind == "diamond":
        return (f'<polygon points="{cx:.1f},{cy - r - 1:.1f} {cx + r + 1:.1f},{cy:.1f} '
                f'{cx:.1f},{cy + r + 1:.1f} {cx - r - 1:.1f},{cy:.1f}" fill="{fill}"/>')
    return (f'<polygon points="{cx:.1f},{cy - r - 1:.1f} {cx + r + 1:.1f},{cy + r:.1f} '
            f'{cx - r - 1:.1f},{cy + r:.1f}" fill="{fill}"/>')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget", type=int, default=20000)
    args = ap.parse_args()

    src = os.path.join(ROOT, OUT_DIR, f"escape_b{args.budget}_summary.csv")
    rows = [r for r in csv.DictReader(open(src)) if r["escaped"] == "True"]
    rows.sort(key=lambda r: int(r["pres_id"]))

    s = []
    s.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
             f'width="{W}" height="{H}" font-family="ui-sans-serif,-apple-system,Helvetica,Arial,sans-serif">')
    s.append('<style>'
             '.ttl{font-size:16px;font-weight:600;fill:#16201f}'
             '.dek{font-size:11.5px;fill:#5d6b6a}'
             '.ax{font-size:10px;fill:#8c9998}'
             '.lab{font-size:11.5px;fill:#16201f;font-family:ui-monospace,Menlo,monospace}'
             '.bin{font-size:9.5px;fill:#8c9998}'
             '.leg{font-size:11px;fill:#5d6b6a}'
             '.cut{font-size:10px;fill:#ab5433}'
             '@media (prefers-color-scheme:dark){'
             '.ttl{fill:#e3eae8}.dek{fill:#93a3a1}.lab{fill:#e3eae8}.leg{fill:#93a3a1}'
             '.ax,.bin{fill:#6f807e}.cut{fill:#dd8560}}'
             '</style>')
    s.append(f'<rect width="{W}" height="{H}" fill="none"/>')
    s.append('<text x="24" y="30" class="ttl">The eight that no change of variables solved at 10,000 nodes</text>')
    s.append(f'<text x="24" y="50" class="dek">Every one escapes at {args.budget:,}. '
             f'What each route to them costs — nodes explored, log scale.</text>')
    s.append('<text x="24" y="67" class="dek">The oracle column is not a procedure: finding it cost '
             '~2.2M nodes per presentation. Read it against the two that are.</text>')

    # x grid
    body_h = len(rows) * (ROW_H + ROW_GAP)
    for p in range(4, 6):
        for m in (1, 2, 5):
            v = m * 10 ** p
            if not X0 <= v <= X1:
                continue
            x = x_of(v)
            s.append(f'<line x1="{x:.1f}" y1="{T - 12}" x2="{x:.1f}" y2="{T + body_h}" '
                     f'stroke="#dce3e1" stroke-width="1" stroke-opacity="0.5"/>')
            lab = f"{v // 1000:,}k" if v >= 1000 else str(v)
            s.append(f'<text x="{x:.1f}" y="{T - 18}" class="ax" text-anchor="middle">{lab}</text>')

    # the 10,000-node budget that produced the old verdict
    xb = x_of(10_000)
    s.append(f'<line x1="{xb:.1f}" y1="{T - 12}" x2="{xb:.1f}" y2="{T + body_h}" '
             f'stroke="#ab5433" stroke-width="1.5" stroke-dasharray="4 3"/>')
    s.append(f'<text x="{xb + 5:.1f}" y="{T - 18}" class="cut">10,000 — the old budget</text>')

    for i, r in enumerate(rows):
        y = T + i * (ROW_H + ROW_GAP) + ROW_H / 2
        if i % 2 == 0:
            s.append(f'<rect x="{L}" y="{y - ROW_H / 2:.1f}" width="{W - L - R}" '
                     f'height="{ROW_H}" fill="#16201f" fill-opacity="0.028"/>')
        pid = int(r["pres_id"])
        s.append(f'<text x="{L - 40}" y="{y + 4:.1f}" class="lab" text-anchor="end">ms{pid}</text>')
        s.append(f'<text x="{L - 8}" y="{y + 4:.1f}" class="bin" text-anchor="end">bin '
                 f'{8 if pid < 630 else 9}</text>')
        vals = [(k, float(r[k])) for k, _l, _c, _m in SERIES if r.get(k)]
        if len(vals) > 1:
            xs = [x_of(v) for _k, v in vals]
            s.append(f'<line x1="{min(xs):.1f}" y1="{y:.1f}" x2="{max(xs):.1f}" y2="{y:.1f}" '
                     f'stroke="#8c9998" stroke-width="1" stroke-opacity="0.45"/>')
        for key, _lab, colour, kind in SERIES:
            if not r.get(key):
                continue
            s.append(marker(kind, x_of(float(r[key])), y, colour))

    # legend
    ly = T + body_h + 30
    s.append(f'<line x1="24" y1="{ly - 16}" x2="{W - 24}" y2="{ly - 16}" stroke="#dce3e1"/>')
    lx = 24
    for _key, lab, colour, kind in SERIES:
        s.append(marker(kind, lx + 5, ly + 2, colour, 4.5))
        s.append(f'<text x="{lx + 16}" y="{ly + 6}" class="leg">{lab}</text>')
        lx += 22 + int(len(lab) * 5.9)
        if lx > W - 260:
            lx, ly = 24, ly + 19
    s.append(f'<text x="24" y="{ly + 26}" class="dek">'
             'Ordering and greedy figures are prior measurements at their own budgets '
             '(100,000 / 1,000,000) — they are what the escape has to be priced against, not new runs.</text>')
    s.append('</svg>')

    dest = os.path.join(ROOT, OUT_DIR, f"escape_b{args.budget}_cost.svg")
    with open(dest, "w") as fh:
        fh.write("\n".join(s) + "\n")
    print(f"[fig] wrote {dest} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
