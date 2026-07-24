"""EXP-17 -- spend the budget on one start, or split it across the eight relabels?

Every experiment so far has treated the node budget as belonging to a single search from a single
starting string. But a presentation has eight signed-permutation relabels -- the same problem under
a rename of the generators -- and the greedy reads *strings*, so each one is a different search
with a different chance of finding the path. This repo already measured that relabels supplied 14
of 17 unsolved->solved flips in the one-hop sweep.

That makes the split itself a hyperparameter, and a free one: **at a fixed total node budget, is it
better to run one search of B nodes, or k searches of B/k nodes from k different relabels?** The
question has never been asked here, and it has a real trade-off on both sides. A wide portfolio
gets more independent chances at an early solve but truncates every one of them, so any
presentation whose solution lies deeper than B/k becomes unreachable. A single deep search keeps
the full depth but bets everything on one string.

The comparison is only meaningful at **equal total cost**, so every arm below spends the same
number of nodes; k = 1 is the incumbent, and the portfolio arms divide the same budget. Node counts
are summed across the whole portfolio (including the searches that failed) so nothing is hidden.

    python3 -m experiments.heuristic_search.exp17_portfolio
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from experiments.heuristic_search.hlab import LOGS, bench66        # noqa: E402
from experiments.heuristic_search.hfast import search_fast         # noqa: E402
from experiments.heuristic_search.perbin import bin_of             # noqa: E402
from experiments.equivalence_classes.lib import words              # noqa: E402

TOTAL = 1_000            # the fixed total budget every arm spends
MRL = 48
SPLITS = (1, 2, 4, 8)    # portfolio width; 1 is the incumbent single deep search
OUT = os.path.join(LOGS, "EXP17_portfolio.jsonl")

ORDERINGS = {
    "baseline (length)": {"segments": [{"upto": None, "w": {"L": 1.0}}]},
    "phased K8": {"segments": [{"upto": 16, "w": {"L": 1.0}},
                               {"upto": None, "w": {"L": 1.0, "K": 8.0}}]},
    "richer knot climb": {"segments": [
        {"upto": 16, "w": {"L": 1.0}},
        {"upto": None, "w": {"L": 1.0, "K": 2.53, "MK": 6.418, "S": 8.458, "xyimb": 3.292}}]},
}


def portfolio(r1, r2, cfg, k, total=TOTAL, mrl=MRL):
    """Run the first ``k`` relabels at ``total // k`` nodes each; stop at the first solve.

    Stopping early is not cheating: a caller looking for one certificate would stop too, and the
    nodes actually spent are what is reported. The relabels are taken in ``SIGNED_PERMS`` order,
    which starts with the identity, so k = 1 is exactly the incumbent single search.
    """
    each = total // k
    spent = 0
    for i in range(k):
        a, b = words.apply_pair((r1, r2), words.SIGNED_PERMS[i][1])
        res = search_fast(a, b, each, cfg, mrl)
        spent += res["nodes"]
        if res["solved"]:
            return {"solved": True, "nodes": spent, "path_length": res["path_length"],
                    "relabel": words.SIGNED_PERMS[i][0], "tried": i + 1}
    return {"solved": False, "nodes": spent, "path_length": None, "relabel": None, "tried": k}


def main():
    rows = [r for r in bench66() if r["source"] == "ladder" and bin_of(r["name"]) in (4, 5, 6, 7)]
    done = set()
    if os.path.exists(OUT):
        for line in open(OUT):
            try:
                r = json.loads(line)
            except ValueError:
                continue
            done.add((r["ordering"], r["name"], r["k"]))

    print(f"  {len(rows)} rows x {len(ORDERINGS)} orderings x {len(SPLITS)} splits, "
          f"total budget {TOTAL} each", flush=True)
    with open(OUT, "a") as f:
        for label, cfg in ORDERINGS.items():
            for k in SPLITS:
                for row in rows:
                    if (label, row["name"], k) in done:
                        continue
                    res = portfolio(row["r1"], row["r2"], cfg, k)
                    f.write(json.dumps({
                        "ordering": label, "name": row["name"], "bin": bin_of(row["name"]),
                        "k": k, "each": TOTAL // k, "total_budget": TOTAL, "mrl": MRL,
                        **res}) + "\n")
                    f.flush()
                    os.fsync(f.fileno())

    data = [json.loads(l) for l in open(OUT)]
    n = len(rows)
    lines = ["# EXP-17 — one deep search, or a portfolio over the relabels?", "",
             f"Fixed total budget **{TOTAL} nodes** for every arm on the decidable band "
             f"(bins 4–7, {n} rows). `k` searches of {TOTAL}/`k` nodes, one per signed-permutation "
             "relabel, stopping at the first solve. `k=1` is the incumbent single deep search. "
             "A relabel is the same presentation under a rename of the generators — the same "
             "problem, but a different string, and the greedy reads strings.", "",
             "| ordering | " + " | ".join(f"k={k} ({TOTAL // k} each)" for k in SPLITS) + " |",
             "|---" * (len(SPLITS) + 1) + "|"]

    best = {}
    for label in ORDERINGS:
        cells = []
        for k in SPLITS:
            d = [r for r in data if r["ordering"] == label and r["k"] == k]
            s = sum(r["solved"] for r in d)
            cells.append(s)
        best[label] = cells
        mark = [f"**{v}**" if v == max(cells) else str(v) for v in cells]
        lines.append(f"| {label} | " + " | ".join(f"{m}/{n}" for m in mark) + " |")

    lines += ["", "## Does splitting the budget help?", ""]
    verdicts = []
    for label, cells in best.items():
        single, wide = cells[0], max(cells[1:])
        kbest = SPLITS[1:][cells[1:].index(wide)]
        if wide > single:
            verdicts.append(f"- `{label}`: **yes** — k={kbest} solves {wide}/{n} against the single "
                            f"search's {single}/{n}.")
        elif wide == single:
            verdicts.append(f"- `{label}`: no difference — k={kbest} matches the single search "
                            f"({single}/{n}).")
        else:
            verdicts.append(f"- `{label}`: **no** — splitting costs solves ({wide}/{n} at k={kbest} "
                            f"against {single}/{n} for one deep search).")
    lines += verdicts + [""]

    helps = sum(1 for v in verdicts if "**yes**" in v)
    if helps == len(best):
        lines += ["Splitting the budget across relabels helps **every** ordering. Depth is not "
                  "what these searches are short of — chances are. A caller with a fixed budget "
                  "should spend it on several relabels rather than one deep search.", ""]
    elif helps:
        lines += [f"Splitting helps {helps} of {len(best)} orderings. Where it helps, the search "
                  "was short of independent chances rather than depth; where it does not, the "
                  "solution lies deeper than the divided budget reaches.", ""]
    else:
        lines += ["**Splitting the budget never helps.** Every solution these orderings can reach "
                  "lies deeper than a divided budget allows, so the extra starting strings buy "
                  "nothing at fixed cost. Relabels remain useful as *additional* budget (EXP-12 "
                  "ran all eight at full depth), but not as a way to divide a fixed one.", ""]

    # Cost: a portfolio that solves on the first relabel spends far less than its budget.
    lines += ["## What the winning arms actually spent", "",
              "| ordering | k | solved | mean nodes spent | mean relabels tried |",
              "|---|---|---|---|---|"]
    for label in ORDERINGS:
        for k in SPLITS:
            d = [r for r in data if r["ordering"] == label and r["k"] == k]
            sv = [r for r in d if r["solved"]]
            if not sv:
                continue
            lines.append(f"| {label} | {k} | {len(sv)}/{n} | "
                         f"{sum(r['nodes'] for r in sv) / len(sv):.0f} | "
                         f"{sum(r['tried'] for r in sv) / len(sv):.1f} |")

    with open(os.path.join(LOGS, "EXP17_portfolio.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
