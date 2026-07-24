"""EXP-20 -- split the budget across different ORDERINGS, not different relabels.

EXP-17 asked whether a fixed budget is better spent on one deep search or several shallow ones
from the eight signed-permutation relabels. The answer was a clean no: the alternates almost never
fired, and splitting only shortened the search that was going to work.

But that experiment held the *ordering* fixed and varied the starting string, which is the axis
with no reason to help. The axis with a reason is the other one. Two facts from this program point
straight at it:

- The best single ordering solves **19 of the 24** decidable rows, while the **union over all
  orderings tried anywhere in this program solves 23** -- only one row (``ms596``) has resisted
  every configuration, over 607 recorded attempts. Different orderings genuinely solve different
  presentations.
- That is not an accident of tuning. The knot ordering cracks a 26,838-node row in 108 nodes and
  misses rows the baseline solves in 16k: it *reorders* difficulty rather than uniformly improving
  it. Orderings that reorder difficulty differently are complementary by construction.

So: at a fixed total budget, is it better to spend it all on the best single ordering, or to split
it across two or three complementary ones? Every pair and triple below spends the same total nodes
as the single-ordering control, and stops at the first solve.

One caution the report carries rather than hides: with 6 pairs and 4 triples scored on 24 rows,
picking the best afterwards is a best-of-N choice and carries its own optimism. The honest question
is not "does the best combination beat the best single" -- it usually will by luck -- but "do
combinations beat singles *as a class*".

    python3 -m experiments.heuristic_search.exp20_config_portfolio
"""
import itertools
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from experiments.heuristic_search.hlab import LOGS, bench66        # noqa: E402
from experiments.heuristic_search.hfast import search_fast         # noqa: E402
from experiments.heuristic_search.perbin import bin_of             # noqa: E402

TOTAL = 1_000
MRL = 48
OUT = os.path.join(LOGS, "EXP20_cportfolio.jsonl")

ORDERINGS = {
    "richer": {"segments": [
        {"upto": None, "w": {"L": 1.0, "K": 2.53, "MK": 6.418, "S": 8.458, "xyimb": 3.292}}]},
    "blocks": {"segments": [{"upto": None, "w": {"L": 1.0, "Bmax": -2.185, "S": 5.668}}]},
    "K+xyimb": {"segments": [{"upto": 16, "w": {"L": 1.0}},
                             {"upto": None, "w": {"L": 1.0, "K": 8.936, "xyimb": -5.978}}]},
    "K8": {"segments": [{"upto": 16, "w": {"L": 1.0}},
                        {"upto": None, "w": {"L": 1.0, "K": 8.0}}]},
}


def run_team(r1, r2, names, total=TOTAL, mrl=MRL):
    """Give each ordering ``total // len(names)`` nodes, in order, stopping at the first solve."""
    each = total // len(names)
    spent = 0
    for nm in names:
        res = search_fast(r1, r2, each, ORDERINGS[nm], mrl)
        spent += res["nodes"]
        if res["solved"]:
            return {"solved": True, "nodes": spent, "path_length": res["path_length"],
                    "by": nm, "tried": names.index(nm) + 1}
    return {"solved": False, "nodes": spent, "path_length": None, "by": None,
            "tried": len(names)}


def teams():
    """Singles, then every pair and triple. Order within a team is alphabetical and fixed."""
    out = [(nm,) for nm in ORDERINGS]
    out += list(itertools.combinations(sorted(ORDERINGS), 2))
    out += list(itertools.combinations(sorted(ORDERINGS), 3))
    return out


def main():
    rows = [r for r in bench66() if r["source"] == "ladder" and bin_of(r["name"]) in (4, 5, 6, 7)]
    done = set()
    if os.path.exists(OUT):
        for line in open(OUT):
            try:
                r = json.loads(line)
            except ValueError:
                continue
            done.add((r["team"], r["name"]))

    all_teams = teams()
    print(f"  {len(all_teams)} teams x {len(rows)} rows, {TOTAL} total nodes each", flush=True)
    with open(OUT, "a") as f:
        for team in all_teams:
            tag = "+".join(team)
            for row in rows:
                if (tag, row["name"]) in done:
                    continue
                res = run_team(row["r1"], row["r2"], list(team))
                f.write(json.dumps({
                    "team": tag, "k": len(team), "each": TOTAL // len(team),
                    "name": row["name"], "bin": bin_of(row["name"]),
                    "total_budget": TOTAL, "mrl": MRL, **res}) + "\n")
                f.flush()
                os.fsync(f.fileno())

    data = [json.loads(l) for l in open(OUT)]
    n = len(rows)
    by_team = {}
    for r in data:
        by_team.setdefault(r["team"], {})[r["name"]] = r
    scored = {t: sum(1 for v in d.values() if v["solved"]) for t, d in by_team.items()}

    singles = {t: s for t, s in scored.items() if "+" not in t}
    pairs = {t: s for t, s in scored.items() if t.count("+") == 1}
    triples = {t: s for t, s in scored.items() if t.count("+") == 2}
    best_single = max(singles.values()) if singles else 0

    def blk(title, d, each):
        out = [f"### {title} ({each} nodes each)", "", "| team | solved |", "|---|---|"]
        for t, s in sorted(d.items(), key=lambda kv: -kv[1]):
            mark = " **←**" if s > best_single else ""
            out.append(f"| `{t}` | {s}/{n}{mark} |")
        return out + [""]

    lines = ["# EXP-20 — split the budget across ORDERINGS instead of relabels", "",
             f"Fixed total budget **{TOTAL} nodes** per row on the decidable band (bins 4–7, {n} "
             "rows). A team of `k` orderings gives each one `1000/k` nodes and stops at the first "
             "solve. Singles are the controls.", "",
             "The motivation is measured, not assumed: the best single ordering solves 19 of these "
             "rows while the union over every ordering tried in this program solves 23, and the "
             "knot ordering is known to *reorder* difficulty rather than uniformly improve it "
             "(it cracks a 26,838-node row in 108 nodes and misses rows the baseline solves in "
             "16k). Orderings that find different things hard are complementary by construction.",
             ""]
    lines += blk("Singles — the control", singles, TOTAL)
    lines += blk("Pairs", pairs, TOTAL // 2)
    lines += blk("Triples", triples, TOTAL // 3)

    def mean(d):
        return sum(d.values()) / len(d) if d else 0.0

    lines += ["## Do combinations beat singles as a class?", "",
              "The honest comparison. Picking the single best team out of "
              f"{len(pairs) + len(triples)} combinations is a best-of-N choice and would flatter "
              "them; comparing the *distributions* does not.", "",
              "| group | n | mean solved | best | worst |", "|---|---|---|---|---|"]
    for name, d in (("singles", singles), ("pairs", pairs), ("triples", triples)):
        if d:
            lines.append(f"| {name} | {len(d)} | {mean(d):.1f}/{n} | {max(d.values())}/{n} | "
                         f"{min(d.values())}/{n} |")

    beats = [t for t, s in {**pairs, **triples}.items() if s > best_single]
    lines += ["", "## Verdict", ""]
    if mean(pairs) > mean(singles):
        lines += [f"Pairs average **{mean(pairs):.1f}** against singles' **{mean(singles):.1f}** — "
                  "splitting across orderings is better *on average*, not just in its best case. "
                  "That is the result that survives the best-of-N objection.", ""]
    else:
        lines += [f"Pairs average **{mean(pairs):.1f}** against singles' **{mean(singles):.1f}**, "
                  "so combining does **not** help as a class. Halving the budget costs more than "
                  "the complementarity buys — the same lesson EXP-17 found for relabels, arriving "
                  "now on the axis that had a mechanism behind it.", ""]
    if beats:
        lines += [f"Individual teams beating the best single ({best_single}/{n}): "
                  + ", ".join(f"`{t}`" for t in beats)
                  + ". Treat as candidates, not conclusions — this is the best of "
                  f"{len(pairs) + len(triples)}.", ""]
    else:
        lines += [f"**No combination beats the best single ordering** ({best_single}/{n}). The "
                  "complementarity is real but only pays when each ordering gets a full budget — "
                  "which is a statement about running them in sequence with more compute, not "
                  "about dividing a fixed budget.", ""]

    # Which ordering actually produced the solves inside the winning teams?
    lines += ["## Inside the teams: which member actually solves?", "",
              "| team | solved | first member | later member |", "|---|---|---|---|"]
    for t in sorted({**pairs, **triples}, key=lambda x: -scored[x])[:8]:
        d = [v for v in by_team[t].values() if v["solved"]]
        first = sum(1 for v in d if v["tried"] == 1)
        later = len(d) - first
        lines.append(f"| `{t}` | {len(d)}/{n} | {first} | {later} |")

    with open(os.path.join(LOGS, "EXP20_cportfolio.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
