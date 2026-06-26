#!/usr/bin/env python3
"""Compare harvested beam paths against the greedy baseline (pre-training analysis).

Reads the beam-harvest JSONL (one record per presentation, last-wins on idx) and
reports, per initial presentation joined by `idx`:
  - solve outcomes (beam vs greedy: both / new-solve / beam-failed / neither),
  - how often the beam path is shorter / equal / longer than greedy,
  - the d-o-t improvement distribution (greedy_path_length - beam_path_length),
  - path-length summary stats, histograms, top improvements, timing, integrity.

Stdlib only (json/csv/argparse/statistics) so it runs anywhere -- in Colab against
the Drive JSONL, or locally against a downloaded copy. No JAX/numpy/numba needed.

The comparison is per initial presentation (idx). Canonical-class min-aggregation
of d-o-t labels (canonical_pair_nj) is the *next* step (PLAN.md step 3), not here:
here we are answering "for each starting presentation, did beam beat greedy?".

Functions are importable (load_results / load_index / compare / format_report) so a
notebook can reuse them for plots.

Run (Colab):
    python scripts/compare_beam_greedy.py \
        --jsonl /content/drive/MyDrive/beam_harvest_greedy_solved/pilot_results.jsonl \
        --index data/greedy_all_index.csv
"""

import argparse
import csv
import json
import os
import statistics
from collections import Counter

DEFAULT_JSONL = "/content/drive/MyDrive/beam_harvest_greedy_solved/pilot_results.jsonl"
DEFAULT_INDEX = "data/greedy_all_index.csv"


# ---------------------------------------------------------------- loaders ----
def load_results(jsonl_path):
    """Read the harvest JSONL; last record wins per idx (matches resume dedup).

    Returns (by_idx, n_lines, n_bad). A truncated/garbled final line is tolerated
    (counted in n_bad) so a mid-write crash never breaks the analysis.
    """
    by_idx, n_lines, n_bad = {}, 0, 0
    with open(jsonl_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            n_lines += 1
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                n_bad += 1
                continue
            by_idx[rec["idx"]] = rec
    return by_idx, n_lines, n_bad


def load_index(index_csv):
    """data/<stem>_index.csv -> {idx: {r1,r2,greedy_solved,greedy_path_length}}."""
    out = {}
    with open(index_csv, newline="") as f:
        for row in csv.DictReader(f):
            i = int(row["line_idx"])
            out[i] = {
                "r1": row["r1"],
                "r2": row["r2"],
                "greedy_solved": row["greedy_solved"].strip().lower() in ("true", "1"),
                "greedy_path_length": int(row["greedy_path_length"]),
            }
    return out


# ------------------------------------------------------------- comparison ----
def compare(by_idx, index=None):
    """Join beam records to greedy labels and bucket the outcomes.

    If `index` is given it is the authoritative source of greedy labels (the JSONL
    copies them at harvest time; this cross-checks). Otherwise the JSONL's own
    greedy_solved / greedy_path_length fields are used.
    """
    buckets = {"both": [], "new_solve": [], "beam_failed": [], "neither": []}
    shorter, equal, longer = [], [], []   # shorter/longer hold (idx, gpl, bpl)
    improvements = []                      # greedy - beam over the `both` set
    g_len_both, b_len_both = [], []
    g_len_all, b_len_all = [], []
    horizon = Counter()
    label_mismatch = []                    # JSONL greedy label != index greedy label
    integrity = []                         # len(packed_path) != beam_path_length
    wall_values, winning_seeds = [], Counter()

    for idx, rec in by_idx.items():
        gs = bool(rec.get("greedy_solved"))
        gpl = rec.get("greedy_path_length")
        if index is not None and idx in index:
            if gs != index[idx]["greedy_solved"] or gpl != index[idx]["greedy_path_length"]:
                label_mismatch.append(idx)
            gs = index[idx]["greedy_solved"]
            gpl = index[idx]["greedy_path_length"]

        bs = bool(rec.get("beam_solved"))
        bpl = rec.get("beam_path_length")
        wt = rec.get("wall_time")
        if wt:
            wall_values.append(wt)

        if gs and isinstance(gpl, int) and gpl >= 0:
            g_len_all.append(gpl)
        if bs:
            horizon[rec.get("horizon")] += 1
            winning_seeds[rec.get("winning_seed")] += 1
            if isinstance(bpl, int):
                b_len_all.append(bpl)
                pp = rec.get("packed_path") or []
                if len(pp) != bpl:
                    integrity.append((idx, len(pp), bpl))

        if gs and bs:
            buckets["both"].append(idx)
            g_len_both.append(gpl)
            b_len_both.append(bpl)
            improvements.append(gpl - bpl)
            if bpl < gpl:
                shorter.append((idx, gpl, bpl))
            elif bpl == gpl:
                equal.append(idx)
            else:
                longer.append((idx, gpl, bpl))
        elif (not gs) and bs:
            buckets["new_solve"].append(idx)
        elif gs and not bs:
            buckets["beam_failed"].append(idx)
        else:
            buckets["neither"].append(idx)

    return {
        "n_presentations": len(by_idx),
        "greedy_solved": sum(1 for r in by_idx.values() if r.get("greedy_solved")),
        "beam_solved": sum(1 for r in by_idx.values() if r.get("beam_solved")),
        "buckets": {k: len(v) for k, v in buckets.items()},
        "bucket_idx": buckets,
        "shorter": shorter, "equal_n": len(equal), "longer": longer,
        "improvements": improvements,
        "g_len_both": g_len_both, "b_len_both": b_len_both,
        "g_len_all": g_len_all, "b_len_all": b_len_all,
        "horizon": dict(horizon), "winning_seeds": dict(winning_seeds),
        "wall_median": statistics.median(wall_values) if wall_values else 0.0,
        "label_mismatch": label_mismatch, "integrity": integrity,
    }


# ----------------------------------------------------------------- report ----
def _pct(n, d):
    return f"{100.0 * n / d:5.1f}%" if d else "  n/a"


def _summ(xs):
    if not xs:
        return "  (empty)"
    return (f"n={len(xs):<6d} min={min(xs):>4d} mean={statistics.mean(xs):6.2f} "
            f"median={statistics.median(xs):6.1f} max={max(xs):>4d}")


def _rows(pairs, width=40):
    if not pairs:
        return "    (none)"
    mx = max(c for _, c in pairs) or 1
    out = []
    for label, c in pairs:
        bar = "#" * max(1, round(width * c / mx))
        out.append(f"    {label:>5} | {bar} {c}")
    return "\n".join(out)


def _diff_hist(diffs, lo=-5, hi=20):
    mid = Counter(d for d in diffs if lo <= d <= hi)
    rows = []
    under = sum(1 for d in diffs if d < lo)
    over = sum(1 for d in diffs if d > hi)
    if under:
        rows.append((f"<{lo}", under))
    rows += [(f"{v:+d}", mid[v]) for v in range(lo, hi + 1) if mid.get(v)]
    if over:
        rows.append((f">{hi}", over))
    return rows


def _len_hist(lengths, hi=30):
    c = Counter(x for x in lengths if x <= hi)
    rows = [(str(v), c[v]) for v in range(0, hi + 1) if c.get(v)]
    over = sum(1 for x in lengths if x > hi)
    if over:
        rows.append((f">{hi}", over))
    return rows


def format_report(s, source=""):
    L = []
    P = L.append
    N = s["n_presentations"]
    both = s["buckets"]["both"]
    shorter, equal, longer = len(s["shorter"]), s["equal_n"], len(s["longer"])
    imp = s["improvements"]

    P("=" * 66)
    P("Beam-vs-Greedy harvest comparison")
    if source:
        P(f"source: {source}")
    P("=" * 66)

    P(f"\nPresentations (unique idx) : {N}")
    P(f"  greedy solved            : {s['greedy_solved']}")
    P(f"  beam solved              : {s['beam_solved']}  ({_pct(s['beam_solved'], N)})")
    P("\nSolve outcomes (joined by idx):")
    P(f"  both solved              : {s['buckets']['both']}")
    P(f"  new solves (beam only)   : {s['buckets']['new_solve']}   <- greedy failed, beam solved")
    P(f"  beam FAILED (greedy ok)  : {s['buckets']['beam_failed']}   <- keep greedy label")
    P(f"  neither solved           : {s['buckets']['neither']}")

    P(f"\nComparable set (both solved) = {both}:")
    P(f"  beam SHORTER than greedy : {shorter:6d}  ({_pct(shorter, both)})")
    P(f"  beam EQUAL  to greedy    : {equal:6d}  ({_pct(equal, both)})")
    P(f"  beam LONGER than greedy  : {longer:6d}  ({_pct(longer, both)})")

    if imp:
        net = sum(imp)
        saved = sum(d for d in imp if d > 0)
        cost = -sum(d for d in imp if d < 0)
        P("\nd-o-t improvement (greedy_len - beam_len), comparable set:")
        P(f"  net moves saved (sum)    : {net}")
        P(f"  saved where beam shorter : {saved}")
        P(f"  extra where beam longer  : {cost}")
        P(f"  mean / median improvement: {statistics.mean(imp):.2f} / {statistics.median(imp):.1f}")
        P(f"  best single improvement  : {max(imp)}")

    P("\nPath-length summary (comparable set):")
    P(f"  greedy : {_summ(s['g_len_both'])}")
    P(f"  beam   : {_summ(s['b_len_both'])}")
    P("\nBeam d-o-t over ALL beam-solved:")
    P(f"  beam   : {_summ(s['b_len_all'])}")

    P("\nImprovement histogram (greedy_len - beam_len):")
    P(_rows(_diff_hist(imp)))
    P("\nBeam path-length (d-o-t) histogram:")
    P(_rows(_len_hist(s["b_len_all"])))

    top = sorted(s["shorter"], key=lambda t: t[1] - t[2], reverse=True)[:10]
    if top:
        P("\nTop 10 improvements (idx: greedy -> beam, delta):")
        for idx, g, b in top:
            P(f"    idx {idx:<6d}: {g:>3d} -> {b:<3d}  (-{g - b})")
    worst = sorted(s["longer"], key=lambda t: t[2] - t[1], reverse=True)[:5]
    if worst:
        P("\nWorst regressions (beam longer than greedy):")
        for idx, g, b in worst:
            P(f"    idx {idx:<6d}: {g:>3d} -> {b:<3d}  (+{b - g})")

    P("\nTiming (wall_time is attributed per batched wave, NOT additive across "
      "the wave's elements — do not sum it):")
    if s["wall_median"]:
        P(f"  per-record median wave time: {s['wall_median']:.2f}s")
    if s["horizon"]:
        P(f"  solved by horizon (T_CAP fast pass vs full-T retry): {s['horizon']}")
    if s["winning_seeds"]:
        P(f"  winning seed counts: {s['winning_seeds']}")

    P("\nIntegrity:")
    if s["integrity"]:
        P(f"  !! {len(s['integrity'])} records where len(packed_path) != beam_path_length: "
          f"{s['integrity'][:5]}")
    else:
        P("  OK: every beam_solved record has len(packed_path) == beam_path_length")
    if s["label_mismatch"]:
        P(f"  !! {len(s['label_mismatch'])} idx where JSONL greedy label != index CSV: "
          f"{s['label_mismatch'][:5]}")
    elif "label_mismatch" in s:
        P("  OK: JSONL greedy labels agree with the index CSV")
    P("=" * 66)
    return "\n".join(L)


# ------------------------------------------------------------------- main ----
def parse_args():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--jsonl", default=DEFAULT_JSONL, help="beam-harvest JSONL")
    p.add_argument("--index", default=DEFAULT_INDEX,
                   help="greedy index CSV for cross-checking labels ('' to skip)")
    p.add_argument("--save_json", default="", help="optional path to dump the stats dict")
    return p.parse_args()


def main():
    args = parse_args()
    if not os.path.exists(args.jsonl):
        raise SystemExit(
            f"JSONL not found: {args.jsonl}\n"
            "  pass --jsonl <path to pilot_results.jsonl> "
            "(on Colab it's under your beam_harvest_greedy_solved Drive folder).")
    by_idx, n_lines, n_bad = load_results(args.jsonl)
    print(f"read {n_lines} lines -> {len(by_idx)} unique idx"
          + (f"  ({n_bad} unparseable lines skipped)" if n_bad else ""))

    index = None
    if args.index and os.path.exists(args.index):
        index = load_index(args.index)
    elif args.index:
        print(f"note: index CSV not found ({args.index}); using JSONL greedy labels only")

    stats = compare(by_idx, index)
    print(format_report(stats, source=args.jsonl))

    if args.save_json:
        with open(args.save_json, "w") as f:
            json.dump({k: v for k, v in stats.items()
                       if k not in ("shorter", "longer")}, f, indent=2)
        print(f"\nwrote stats dict -> {args.save_json}")


if __name__ == "__main__":
    main()
