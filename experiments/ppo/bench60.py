"""Scoring the benchmark-60 evaluation, at row level AND at orbit level.

Evaluation happens on `benchmark/subsets/benchmark_subset_60.csv` by standing rule. Two
properties of that file decide how its numbers have to be written down.

**60 rows are only 45 Aut orbits.** `aut_class` 106 appears eight times; 93 and 97 three
times each; 87, 99, 108 and 110 twice each. A method that happens to suit orbit 106 collects
eight rows for one idea, so a bare `n/60` overstates it. Every headline here is reported both
ways, and the orbit count credits an orbit only when at least one of its rows solved -- the
same correction the 66-row benchmark needed.

**Bins 0-6 saturate.** A 1024x150 beam solves the easy head with no policy worth the name: on
the 331 rows one smoke covered, a *two-update* model scored 318/331 against the fully trained
model's 331/331. So an arm difference can only appear in bins 7-9, which is 18 rows and 11
orbits. That is a thin denominator and it is printed next to the headline rather than left for
someone to work out later.

The evaluation itself is an ordinary `beam_eval` over a 60-row dataset (`heldout.BENCH_STEM`),
not a bespoke stage: that way it resumes, verifies every solved certificate and reports through
exactly the same code as the 1190-row run. This module only joins its jsonl back to the CSV --
row `i` of the beam is row `i` of the CSV, which is why `build_benchmark_dataset` preserves
CSV order.
"""

import glob
import json
import os

from experiments.ppo import heldout

DISCRIMINATING_BINS = {"7", "8", "9"}


def _rows(path):
    out = []
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    out.append(json.loads(line))
                except ValueError:      # a torn trailing line from a killed VM
                    pass
    return out


def score(beam_jsonl, bench=None):
    """`{rows, solved, orbits_*, by_bin, discriminating, path_*}` for one beam run."""
    bench = bench or heldout.benchmark_rows()
    rows = _rows(beam_jsonl)
    solved_idx = {r["presentation_idx"] for r in rows if r.get("solved")}
    seen_idx = {r["presentation_idx"] for r in rows}

    orbits, orbits_solved = set(), set()
    by_bin = {}
    disc_total = disc_solved = 0
    for i, b in enumerate(bench):
        if i not in seen_idx:
            continue
        orbits.add(b["aut_class"])
        hit = i in solved_idx
        if hit:
            orbits_solved.add(b["aut_class"])
        got, tot = by_bin.get(b["bin"], (0, 0))
        by_bin[b["bin"]] = (got + int(hit), tot + 1)
        if b["bin"] in DISCRIMINATING_BINS:
            disc_total += 1
            disc_solved += int(hit)

    paths = sorted(r["path_length"] for r in rows if r.get("solved"))
    return {
        "file": os.path.basename(beam_jsonl),
        "rows": len(rows), "solved": len(solved_idx),
        "orbits": len(orbits), "orbits_solved": len(orbits_solved),
        # Bins 0-6 saturate for any competent model, so this is the number an arm
        # comparison actually turns on. Reported next to the headline, never instead.
        "discriminating_solved": disc_solved, "discriminating_rows": disc_total,
        "by_bin": {k: f"{v[0]}/{v[1]}" for k, v in sorted(by_bin.items())},
        "path_median": paths[len(paths) // 2] if paths else None,
        "path_max": paths[-1] if paths else None,
    }


def summarise(out_dir):
    """Score every benchmark-60 beam jsonl in `out_dir`. Empty list if there are none."""
    pattern = os.path.join(out_dir, f"beam-*-{heldout.BENCH_STEM}-*.jsonl")
    bench = heldout.benchmark_rows()
    return [score(p, bench) for p in sorted(glob.glob(pattern))]


def format_table(scores):
    """One line per arm, for a notebook cell. Row level and orbit level, always both."""
    if not scores:
        return "no benchmark-60 evaluation on disk yet"
    out = [f"{'arm':<52} {'rows':>7} {'orbits':>7} {'bins7-9':>8}  path med/max"]
    for s in scores:
        arm = s["file"].replace("beam-", "").replace(f"-{heldout.BENCH_STEM}", "")
        arm = arm.split("-w1024")[0]
        out.append(f"{arm[:52]:<52} {s['solved']:>3}/{s['rows']:<3} "
                   f"{s['orbits_solved']:>3}/{s['orbits']:<3} "
                   f"{s['discriminating_solved']:>3}/{s['discriminating_rows']:<4} "
                   f"  {s['path_median']}/{s['path_max']}")
    return "\n".join(out)
