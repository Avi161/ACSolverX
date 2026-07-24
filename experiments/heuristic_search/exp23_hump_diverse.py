"""EXP-23 -- point the *diverse* orderings at the second hump, which has only ever seen one family.

Everything aimed at the hard tier so far came from one family. EXP-08 ran the eight best orderings
on bins 8-9 and the reach rows; EXP-12 ran four on all 124 unsolved AC-classes. All of them were
knot climbs or their close relatives, and all of them found nothing -- which is the expected
result, and was reported as such.

But EXP-21 and EXP-22 changed what "the best orderings" means. The finalists turn out to be
*redundant with each other*: at budget 1,000 the union of all five equals the best single, because
they find the same presentations easy and the same ones hard. The rows that get unlocked come from
leaving the family -- a knot-free ordering added four rows the climbs could not reach, and
cross-validation put the honest marginal gain at about one row with a 4x edge over picking the
strongest second arm.

So the hard tier has never actually been attacked from a second direction. That is worth one run.
It is still very unlikely to solve anything -- these presentations survived 10^6 nodes and the
local ceiling is 1,000, three orders of magnitude short, and no reordering closes that by itself.
The point is that "nothing solves the second hump" would now be a claim about *one family* of
orderings unless the other family is tried too.

Solves only, as always for this tier: EXP-07 established that no checkpoint proxy predicts a
solve, so there is nothing here to rank on.

    python3 -m experiments.heuristic_search.exp23_hump_diverse
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from experiments.heuristic_search.hlab import LOGS, bench66        # noqa: E402
from experiments.heuristic_search.hfast import search_fast         # noqa: E402
from experiments.heuristic_search.perbin import bin_of             # noqa: E402

BUDGET = 1_000
MRL = 64
OUT = os.path.join(LOGS, "EXP23_hump_diverse.jsonl")

# Deliberately NOT knot climbs. These are the families that complemented the recommended ordering
# in EXP-21/22 -- the ones that reach different presentations.
DIVERSE = {
    "complement: Bspread+Lmin+imbal (CV winner)": {"segments": [
        {"upto": 20, "w": {"L": 1.0}},
        {"upto": None, "w": {"L": 1.0, "Bspread": 1.506, "Lmin": 0.413, "imbal": 9.99}}]},
    "complement: S+imbal, no knots": {"segments": [
        {"upto": 16, "w": {"L": 1.0}},
        {"upto": None, "w": {"L": 1.0, "S": 7.547, "imbal": 1.164}}]},
    "complement: Bmax+Lmax": {"segments": [
        {"upto": 14, "w": {"L": 1.0}},
        {"upto": None, "w": {"L": 1.0, "Bmax": -3.272, "Lmax": 5.679}}]},
    "complement: Bmin+Lmax+S+xyimb": {"segments": [
        {"upto": 12, "w": {"L": 1.0}},
        {"upto": None, "w": {"L": 1.0, "Bmin": -0.186, "Lmax": 5.519, "S": 5.369,
                             "xyimb": 2.3}}]},
    "ratio-led (never tried on this tier)": {"segments": [
        {"upto": None, "w": {"L": 1.0, "ratio": -8.0, "S": 4.0}}]},
    "density-led (never tried on this tier)": {"segments": [
        {"upto": None, "w": {"L": 1.0, "density": 12.0, "Lmax": 2.0}}]},
}


def main():
    rows = [r for r in bench66()
            if r["source"] == "reach" or (r["source"] == "ladder" and bin_of(r["name"]) in (8, 9))]
    done = set()
    if os.path.exists(OUT):
        for line in open(OUT):
            try:
                r = json.loads(line)
            except ValueError:
                continue
            done.add((r["ordering"], r["name"]))

    print(f"  {len(rows)} hard rows x {len(DIVERSE)} diverse orderings, budget {BUDGET}, cap {MRL}",
          flush=True)
    with open(OUT, "a") as f:
        for label, cfg in DIVERSE.items():
            for row in rows:
                if (label, row["name"]) in done:
                    continue
                res = search_fast(row["r1"], row["r2"], BUDGET, cfg, MRL)
                f.write(json.dumps({
                    "ordering": label, "name": row["name"],
                    "bin": bin_of(row["name"]), "source": row["source"],
                    "budget": BUDGET, "mrl": MRL, "solved": res["solved"],
                    "nodes": res["nodes"], "path_length": res["path_length"],
                    "min_total": res["min_total"], "start_K": res["start_K"],
                    "min_K": res["min_K"]}) + "\n")
                f.flush()
                os.fsync(f.fileno())

    data = [json.loads(l) for l in open(OUT)]
    solved = [r for r in data if r["solved"]]
    n = len(rows)

    lines = ["# EXP-23 — the second hump, attacked from the other family", "",
             f"Bins 8–9 plus the six reach rows ({n} presentations), budget {BUDGET}, cap {MRL}. "
             "The orderings here are deliberately **not** knot climbs: they are the families that "
             "complemented the recommended ordering on the decidable band, plus two led by "
             "second-family features that have never been pointed at this tier.", "",
             "Every previous attempt on this tier (EXP-08, EXP-12) used one family. Since the "
             "finalists turn out to be redundant with each other — at budget 1,000 the union of "
             "all five equals the best single — 'nothing solves the second hump' would have been "
             "a claim about that family alone.", ""]

    if solved:
        lines += ["## Something solved", ""]
        for r in solved:
            lines.append(f"- **{r['name']}** ({r['source']}, bin {r['bin']}) by "
                         f"`{r['ordering']}` in {r['nodes']} nodes, path {r['path_length']}")
        lines.append("")
    else:
        lines += [f"**Nothing solved — now across both families.** The expected result: these "
                  f"presentations survived a 10^6-node search and {BUDGET} nodes is three orders "
                  "of magnitude short, which no reordering closes on its own. What this adds to "
                  "EXP-08 and EXP-12 is that the negative is no longer specific to knot climbs.",
                  ""]

    lines += ["## Shortest total reached (descriptive — EXP-07 forbids ranking on this)", "",
              "| ordering | solved | mean shortest total | rows reaching fewer knots |",
              "|---|---|---|---|"]
    for label in DIVERSE:
        d = [r for r in data if r["ordering"] == label]
        if not d:
            continue
        mt = sum(r["min_total"] for r in d) / len(d)
        kr = sum(1 for r in d if r["min_K"] < r["start_K"])
        lines.append(f"| {label} | {sum(r['solved'] for r in d)}/{len(d)} | {mt:.1f} | {kr}/{len(d)} |")

    with open(os.path.join(LOGS, "EXP23_hump_diverse.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
