"""Paired synthesis over the three fftvar scout slices — the entry point for this scout.

Counts at n=20 per slice swing enormously (the shipped `lag345` scores 1, 4 and 10 out of 20 on
three disjoint slices of the same split), so *unpaired* slice totals cannot rank two arms here.
Pairing can: both arms run the same presentation, so a presentation neither solves carries no
information and drops out, and what is left is the discordant count. That is the exact McNemar /
sign test, and it is well defined at this n where a difference of totals is not.

    PYTHONPATH=. .venv/bin/python3 -m experiments.heuristic_search.runners.scout_fftvar_summary
"""
from __future__ import annotations

import collections
import json
import math
import os
import sys
from datetime import datetime, timezone

_d = os.path.dirname(os.path.abspath(__file__))
while _d != os.path.dirname(_d) and not all(
        os.path.isdir(os.path.join(_d, _s)) for _s in ("experiments", "data")):
    _d = os.path.dirname(_d)
sys.path.insert(0, _d)

OUT_DIR = os.path.join(_d, "results", "heuristic_search", "fftvar_scout")
RESULTS = os.path.join(OUT_DIR, "SUMMARY.md")
SOURCES = ("runs.jsonl", "confirm.jsonl", "slice_c.jsonl")

#: name in the report -> arm keys it appears under across the three jsonls
ALIAS = {
    "length": ("length", "length_w0"),
    "lag345 @ wF=4": ("F4_lag345", "lag345_w4"),
    "cplxlo @ wF=4": ("F4_cplxlo", "cplxlo_w4"),
    "cplxlo @ wF=8": ("cplxlo_w8",),
    "dftlo @ wF=4": ("F4_dftlo", "dftlo_w4"),
}
# runs.jsonl has no "slice" field; it is slice A by construction
DEFAULT_SLICE = "A"


def _load():
    """(slice, idx) -> {report name: solved}. Later files win on a repeat, but the arms are
    deterministic so a repeat is the same value."""
    d = collections.defaultdict(dict)
    inv = {k: name for name, keys in ALIAS.items() for k in keys}
    for fn in SOURCES:
        p = os.path.join(OUT_DIR, fn)
        if not os.path.exists(p):
            continue
        for line in open(p):
            r = json.loads(line)
            name = inv.get(r["arm"])
            if name is None:
                continue
            d[(r.get("slice", DEFAULT_SLICE), r["idx"])][name] = bool(r["solved"])
    return d


def _binom_two_sided(k, n):
    """Exact two-sided sign test on ``k`` of ``n`` discordant pairs, p = 1/2."""
    if n == 0:
        return 1.0
    k = min(k, n - k)
    tail = sum(math.comb(n, i) for i in range(0, k + 1)) / (2 ** n)
    return min(1.0, 2 * tail)


def paired(d, a, b, slice_filter=None):
    both = only_a = only_b = neither = 0
    for (sl, _), v in d.items():
        if slice_filter is not None and sl != slice_filter:
            continue
        if a in v and b in v:
            if v[a] and v[b]:
                both += 1
            elif v[a]:
                only_a += 1
            elif v[b]:
                only_b += 1
            else:
                neither += 1
    n_disc = only_a + only_b
    return {"n": both + only_a + only_b + neither, "both": both,
            "only_a": only_a, "only_b": only_b, "neither": neither,
            "p": _binom_two_sided(only_b, n_disc)}


def per_slice(d, name):
    out = {}
    for (sl, _), v in d.items():
        if name in v:
            s, n = out.get(sl, (0, 0))
            out[sl] = (s + int(v[name]), n + 1)
    return out


def main():
    d = _load()
    comparisons = [
        ("lag345 @ wF=4", "cplxlo @ wF=4"),
        ("lag345 @ wF=4", "cplxlo @ wF=8"),
        ("lag345 @ wF=4", "dftlo @ wF=4"),
        ("length", "lag345 @ wF=4"),
        ("length", "cplxlo @ wF=4"),
    ]

    L = []
    L.append("# fftvar scout — paired synthesis")
    L.append("")
    L.append(f"Updated `{datetime.now(timezone.utc).isoformat()}`")
    L.append("")
    L.append("Entry point for [`RESULTS.md`](RESULTS.md) (13 transforms, slice A), "
             "[`CONFIRM.md`](CONFIRM.md) (weight sweep + slice B) and "
             "[`SLICE_C.md`](SLICE_C.md) (pre-registered slice C).")
    L.append("")
    L.append("## Why paired, not totals")
    L.append("")
    L.append("| arm | slice A | slice B | slice C |")
    L.append("|---|---:|---:|---:|")
    for name in ALIAS:
        ps = per_slice(d, name)
        cells = []
        for sl in ("A", "B", "C"):
            cells.append(f"{ps[sl][0]}/{ps[sl][1]}" if sl in ps else "—")
        L.append(f"| `{name}` | " + " | ".join(cells) + " |")
    L.append("")
    L.append("The shipped `lag345` scores **1, 4 and 10 out of 20** on three disjoint slices of "
             "the same split at the same weight. Slice-to-slice variance swamps every "
             "between-arm gap, so a difference of totals at n=20 carries almost no information "
             "— which is exactly why slice A's 13-arm ranking put `dftlo` first and slice B "
             "then knocked it from 7/20 to 2/20. Pairing removes that variance: both arms see "
             "the same presentation, presentations neither solves drop out, and only the "
             "discordant pairs count.")
    L.append("")
    L.append("## Paired comparisons (all three slices pooled)")
    L.append("")
    L.append("| A vs B | n | both | only A | only B | exact p |")
    L.append("|---|---:|---:|---:|---:|---:|")
    for a, b in comparisons:
        r = paired(d, a, b)
        if r["n"] == 0:
            continue
        L.append(f"| `{a}` vs `{b}` | {r['n']} | {r['both']} | **{r['only_a']}** | "
                 f"**{r['only_b']}** | {r['p']:.4f} |")
    L.append("")
    L.append("`only A` / `only B` are the discordant pairs; `p` is the exact two-sided sign "
             "test on them. A zero in `only A` means B solved a **strict superset**.")
    L.append("")
    L.append("### The headline comparison, split by slice")
    L.append("")
    L.append("Pooling the selection slice into the significance test flatters it, so the same "
             "paired comparison is broken out. **Slice A selected `cplxlo`; slice B did not.**")
    L.append("")
    L.append("| slice | role | n | both | only `lag345` | only `cplxlo` | exact p |")
    L.append("|---|---|---:|---:|---:|---:|---:|")
    for sl, role in (("A", "selection"), ("B", "confirmation")):
        r = paired(d, "lag345 @ wF=4", "cplxlo @ wF=4", slice_filter=sl)
        if r["n"] == 0:
            continue
        L.append(f"| {sl} | {role} | {r['n']} | {r['both']} | **{r['only_a']}** | "
                 f"**{r['only_b']}** | {r['p']:.4f} |")
    rp = paired(d, "lag345 @ wF=4", "cplxlo @ wF=4")
    L.append(f"| A+B | pooled | {rp['n']} | {rp['both']} | **{rp['only_a']}** | "
             f"**{rp['only_b']}** | {rp['p']:.4f} |")
    L.append("")
    L.append("## Read")
    L.append("")
    rb = paired(d, "lag345 @ wF=4", "cplxlo @ wF=4", slice_filter="B")
    r44 = rp
    L.append(f"- **Direction is consistent, magnitude is not established.** Across "
             f"{r44['n']} paired presentations `cplxlo` solves {r44['only_b']} that `lag345` "
             f"misses and **{r44['only_a']}** the other way — it never loses a discordant pair "
             f"on either slice. But the pooled p = {r44['p']:.4f} leans on slice A, which is "
             f"the slice `cplxlo` was *selected* on; the clean confirmation slice B is only "
             f"{rb['only_b']}-vs-{rb['only_a']} (p = {rb['p']:.2f}) and cannot carry the claim "
             f"alone. Treat this as a promising direction with a clean sign, not a result.")
    L.append("- Matched weight is the control that matters, because the two features have "
             "similar spread on start states (std 0.32 for `cplxlo`, 0.36 for `lag345`), so "
             "`cplxlo` wins with slightly *less* effective push, not more. The win is the "
             "transform, not the scale.")
    L.append("- `cplxlo` is also one of the four variants **invariant under the x<->X relabel** "
             "— the documented wart of the shipped `lag345`, which scores two AC-identical "
             "states differently. It is the only *spectral* variant with that property.")
    L.append("- Raising the weight to 8 buys more solves in total but stops being a superset "
             "(4 presentations regress), so `wF` is a real knob and 4 is not obviously its "
             "best value.")
    L.append("- The `length` control is **0/60** across all three slices. Every spectral term "
             "beats it; that floor is the only thing here that n=20 measures reliably.")
    L.append("")
    L.append("## What this does not show")
    L.append("")
    L.append("- All of it is on `L + wF*F` — the *pure* spectral arm. It says nothing about "
             "whether `cplxlo` adds anything **on top of `S20_MK2`**, which is where the "
             "shipped heuristic lives and where the original Fourier term failed. The pure-F "
             "comparison is a transform ranking, not a promotion case.")
    L.append("- Budget 1,000, 60 train presentations, no holdout read. The decision run is the "
             "full train 120 and then both holdouts, on Colab.")
    L.append("- Both holdouts remain unspent by this work.")
    L.append("")
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(RESULTS, "w") as f:
        f.write("\n".join(L))
    print("\n".join(L))
    print(f"\nwrote {RESULTS}")


if __name__ == "__main__":
    main()
