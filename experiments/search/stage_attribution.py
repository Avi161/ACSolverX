"""Attribute every AC19 orbit to the cascade stage that returned its certificate.

`cascade_heuristics.search()` records the deciding stage per row in `winner`,
so the whole screen can be broken down without re-running anything. Rows are
taken at the highest ladder rung they reached.

    PYTHONPATH=. python experiments/search/stage_attribution.py
"""
from __future__ import annotations

import collections
import json
import statistics
import sys

RESULTS = "results/heuristic_search"
LADDER = (
    f"{RESULTS}/ac19_cascade_screen/ac19_cascade_screen_cascade501_b501_mrl255.jsonl",
    f"{RESULTS}/ac19_residue_unstarved/ac19_cascade_screen_cascade501_b1000_mrl255_sb1000.jsonl",
    f"{RESULTS}/ac19_residue_unstarved/ac19_cascade_screen_cascade501_b100000_mrl255_sb10000.jsonl",
)
ORDER = ("descent alone", "rewrite (BS collapse)", "s40_gen", "s20_mk2",
         "terminal", "unsolved")


def load(path):
    with open(path) as handle:
        return [json.loads(line) for line in handle if line.strip()]


def stage(record):
    """The pipeline stage that returned this row's certificate."""
    if not (record["solved"] or record["aut_assisted"]):
        return "unsolved"
    if record["winner"] != "rewrite":
        return record["winner"]
    # A descent that landed on (x,y) reaches bs_collapse and returns
    # reason='terminal'; an actual Baumslag-Solitar collapse returns 'collapsed'.
    attempts = {a["component"]: a for a in record["attempts"]}
    if attempts.get("rewrite", {}).get("reason") == "terminal":
        return "descent alone"
    return "rewrite (BS collapse)"


def final_rows(ladder=LADDER):
    """Each orbit at the highest rung it reached."""
    rows = {}
    for path in ladder:
        for record in load(path):
            rows[record["name"]] = record
    return rows


def attribute(rows):
    counts = collections.Counter(stage(r) for r in rows.values())
    split = collections.defaultdict(lambda: [0, 0])
    for record in rows.values():
        name = stage(record)
        if name == "unsolved":
            continue
        split[name][0 if record["solved"] else 1] += 1
    return counts, split


def starter_starvation(path=LADDER[0], budget=501, starter_budget=500):
    """Nodes spent before s20_mk2 at the shipped default, and its allowance."""
    before, reached = collections.Counter(), 0
    for record in load(path):
        attempts = {a["component"]: a for a in record["attempts"]}
        if "s20_mk2" in attempts:
            reached += 1
        if "s40_gen" not in attempts:
            continue
        before[attempts.get("normalization", {}).get("nodes", 0)
               + attempts.get("rewrite", {}).get("nodes", 0)] += 1
    spent = max(before, key=before.get) + starter_budget
    return before, reached, spent, min(budget, budget - spent)


def main():
    rows = final_rows()
    counts, split = attribute(rows)
    total = sum(counts.values())
    print(f"=== stage attribution, {total:,} orbits ===")
    print(f"  {'stage':<24} {'rows':>7} {'share':>8} {'AC-cert':>9} {'aut_asst':>9}")
    for name in ORDER:
        n = counts.get(name, 0)
        ac, aut = split.get(name, [0, 0])
        print(f"  {name:<24} {n:>7} {100 * n / total:>7.3f}% "
              f"{ac if name != 'unsolved' else '-':>9} "
              f"{aut if name != 'unsolved' else '-':>9}")
    ac = sum(1 for r in rows.values() if r["solved"])
    aut = sum(1 for r in rows.values() if r["aut_assisted"] and not r["solved"])
    print(f"\n  settled {ac + aut:,} of {total:,}  "
          f"({ac:,} AC-certified, {aut:,} aut_assisted), {counts['unsolved']} open")
    print("  open:", ", ".join(sorted(n for n, r in rows.items()
                                      if not (r["solved"] or r["aut_assisted"]))))

    before, reached, spent, allowance = starter_starvation()
    print(f"\n=== s20_mk2 at the shipped default (budget 501, starter 500) ===")
    print(f"  normalization+rewrite nodes before s40_gen: {dict(before)}")
    print(f"  spent before s20_mk2 = {spent}; allowance = "
          f"min(501, 501 - {spent}) = {allowance}")
    print(f"  rows carrying an s20_mk2 attempt at this rung: {reached}")
    if allowance > 0 or reached:
        print("  UNEXPECTED: the stage is reachable at this rung", file=sys.stderr)
        return 1

    bs = [r for r in rows.values() if stage(r) == "rewrite (BS collapse)"]
    moves = sorted(r["certificate_moves"] for r in bs)
    print(f"\n=== BS collapse: {len(bs):,} rows ===")
    print(f"  certificate moves min={moves[0]} median={int(statistics.median(moves))} "
          f"p99={moves[int(len(moves) * 0.99)]} max={moves[-1]}")
    print(f"  rows whose shorter relator has length exactly 5: "
          f"{sum(1 for r in bs if 5 in (len(r['r1']), len(r['r2'])))} of {len(bs)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
