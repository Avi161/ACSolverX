"""EXP-09 -- the finalists on the whole 66-row benchmark, for the headline solve count.

The split experiments answer "does this generalise" (train/test) and "leak-free" (aut-disjoint).
This answers the plainer question the user asked -- how many of the 66 does each finalist actually
solve -- by running them on every row at once. It is a *descriptive* total, not a selection: the
finalists were already chosen upstream, so scoring them on the full set adds no optimism, it just
reports the number without a denominator that hides the easy rows.

Per bin, both budgets, so the headline separates the saturated easy rows (every ordering gets
them) from the hard-decidable rows (where the orderings differ) from the second hump (nobody
solves). The six reach rows are included and expected to stay at zero.

    python3 -m experiments.heuristic_search.exp09_fullbench
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from experiments.heuristic_search.hlab import (                    # noqa: E402
    BASELINE_CONFIG, LOGS, bench66, cfg_name,
)
from experiments.heuristic_search.hfast import search_fast         # noqa: E402
from experiments.heuristic_search.perbin import bin_of             # noqa: E402

MRL = 48
OUT = os.path.join(LOGS, "EXP09_fullbench.jsonl")

FINALISTS = {
    "baseline (length)": BASELINE_CONFIG,
    "500-winner: phased K+xyimb": {"segments": [
        {"upto": 16, "w": {"L": 1.0}},
        {"upto": None, "w": {"L": 1.0, "K": 8.936, "xyimb": -5.978}}]},
    "1000-winner: phased blocks": {"segments": [
        {"upto": 16, "w": {"L": 1.0}},
        {"upto": None, "w": {"L": 1.0, "Bmax": -2.185, "S": 5.668}}]},
    "richer knot climb (EXP-06)": {"segments": [
        {"upto": 16, "w": {"L": 1.0}},
        {"upto": None, "w": {"L": 1.0, "K": 2.53, "MK": 6.418, "S": 8.458, "xyimb": 3.292}}]},
    "simple phased K8": {"segments": [
        {"upto": 16, "w": {"L": 1.0}},
        {"upto": None, "w": {"L": 1.0, "K": 8.0}}]},
}


def main():
    rows = bench66()
    done = set()
    if os.path.exists(OUT):
        for line in open(OUT):
            try:
                r = json.loads(line)
            except ValueError:
                continue
            done.add((r["label"], r["name"], r["budget"]))

    with open(OUT, "a") as f:
        for label, cfg in FINALISTS.items():
            for budget in (500, 1000):
                for row in rows:
                    if (label, row["name"], budget) in done:
                        continue
                    res = search_fast(row["r1"], row["r2"], budget, cfg, MRL)
                    f.write(json.dumps({
                        "label": label, "config_id": cfg_name(cfg), "name": row["name"],
                        "budget": budget, "mrl": MRL, "bin": bin_of(row["name"]),
                        "solved": res["solved"], "nodes": res["nodes"],
                        "path_length": res["path_length"], "source": row["source"]}) + "\n")
                    f.flush()
                    os.fsync(f.fileno())

    data = [json.loads(l) for l in open(OUT)]
    lines = ["# EXP-09 — the finalists on the full 66-row benchmark", "",
             "Descriptive total solve counts (not a selection). 60 ladder rows in difficulty bins "
             "0–9 plus 6 open reach rows. Cap 48.", ""]
    for budget in (500, 1000):
        lines += [f"## Budget {budget}", "",
                  "| ordering | total | bins 0–3 | bin 4 | bin 5 | bin 6 | bin 7 | bins 8–9 | reach |",
                  "|---|---|---|---|---|---|---|---|---|"]
        for label in FINALISTS:
            d = [r for r in data if r["label"] == label and r["budget"] == budget]
            def band(pred):
                sub = [r for r in d if pred(r)]
                return f"{sum(r['solved'] for r in sub)}/{len(sub)}"
            tot = sum(r["solved"] for r in d)
            lines.append(
                f"| {label} | **{tot}/{len(d)}** | "
                f"{band(lambda r: r['bin'] in (0,1,2,3))} | {band(lambda r: r['bin']==4)} | "
                f"{band(lambda r: r['bin']==5)} | {band(lambda r: r['bin']==6)} | "
                f"{band(lambda r: r['bin']==7)} | {band(lambda r: r['bin'] in (8,9))} | "
                f"{band(lambda r: r['source']=='reach')} |")
        lines.append("")

    with open(os.path.join(LOGS, "EXP09_fullbench.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
