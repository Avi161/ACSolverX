"""EXP-12 -- the actual target: all 124 unsolved AC-classes, under the best orderings.

Every experiment so far scored on the 66-row benchmark, whose "hard" tier is six open rows. The
brief's real target is larger and harder: the **124 unsolved Miller-Schupp classes** -- the ones
that survive after quotienting the 1190 by AC-moves and change of variables. None of them is
expected to solve at 1,000 nodes (the user said as much, and EXP-08 found nothing on the six).
Running them anyway is still worth doing, for two reasons that do not depend on a solve:

1. It converts "probably nothing solves" into a measured statement over the whole target set,
   which is what makes the recommendation's scope honest rather than assumed.
2. **Each class is tried from eight starts, not one.** A class is one problem, but the greedy
   reads *strings*: a signed-permutation relabel (renaming the generators) leaves the AC-class and
   its difficulty untouched while giving the search an entirely different string to walk. This
   repo has already measured how much that matters -- relabels supplied 14 of 17 unsolved->solved
   flips in the one-hop sweep -- so every class enters as its eight images, and any one of them
   solving settles the class.

Solves only. EXP-07 established that knot- and length-progress at a checkpoint do not predict a
solve, so there is nothing here to rank orderings by; ``min_total``/``min_K`` are recorded for a
human to look at and are explicitly not scored.

    python3 -m experiments.heuristic_search.exp12_unsolved124
"""
import csv
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from experiments.heuristic_search.hlab import LOGS, ROOT, cfg_name  # noqa: E402
from experiments.heuristic_search.hfast import search_fast          # noqa: E402

BUDGET = 1_000
MRL = 64                 # generous: these starts are long, and the climb wants room
OUT = os.path.join(LOGS, "EXP12_unsolved124.jsonl")
SRC = os.path.join(ROOT, "results", "equivalence_classes", "ms1190_tables",
                   "unsolved_124_aca_classes.csv")

ORDERINGS = {
    "baseline (length)": {"segments": [{"upto": None, "w": {"L": 1.0}}]},
    "phased K+xyimb (win500)": {"segments": [
        {"upto": 16, "w": {"L": 1.0}},
        {"upto": None, "w": {"L": 1.0, "K": 8.936, "xyimb": -5.978}}]},
    "phased knot climb (win1000)": {"segments": [
        {"upto": 16, "w": {"L": 1.0}},
        {"upto": None, "w": {"L": 1.0, "K": 2.53, "MK": 6.418, "S": 8.458, "xyimb": 3.292}}]},
    "phased blocks": {"segments": [
        {"upto": 16, "w": {"L": 1.0}},
        {"upto": None, "w": {"L": 1.0, "Bmax": -2.185, "S": 5.668}}]},
}


def starts():
    """(class_id, label, r1, r2) for every distinct start: each class x its 8 signed relabels.

    The table's ``rep_r1/rep_r2`` turn out to equal ``r1/r2`` on every row, so the class supplies
    exactly one pair. The eight **signed-permutation relabels** are what actually multiply the
    attempts, and they are not a trick: a relabel is the same presentation under a rename of the
    generators -- same AC-class, same difficulty in any orbit sense -- but the greedy reads
    *strings*, so each image is a genuinely different search. This repo already measured that:
    relabels supplied 14 of 17 unsolved->solved flips in the one-hop sweep. Reusing
    ``equivalence_classes.lib.words`` rather than re-deriving the eight, so there is one definition
    of what a relabel is.
    """
    from experiments.equivalence_classes.lib import words
    out = []
    with open(SRC) as f:
        for row in csv.DictReader(f):
            seen = set()
            for name, img in words.SIGNED_PERMS:
                a, b = words.apply_pair((row["r1"], row["r2"]), img)
                if (a, b) in seen:
                    continue          # a symmetric pair can be fixed by some permutation
                seen.add((a, b))
                out.append((row["aca_id"], name, a, b))
    return out


def main():
    todo = starts()
    done = set()
    if os.path.exists(OUT):
        for line in open(OUT):
            try:
                r = json.loads(line)
            except ValueError:
                continue
            done.add((r["ordering"], r["aca_id"], r["rep"]))

    n_cls = len({c for c, _, _, _ in todo})
    print(f"  {len(todo)} starts over {n_cls} classes x {len(ORDERINGS)} orderings, "
          f"budget {BUDGET}, cap {MRL}", flush=True)

    with open(OUT, "a") as f:
        for label, cfg in ORDERINGS.items():
            for aca, tag, r1, r2 in todo:
                if (label, aca, tag) in done:
                    continue
                res = search_fast(r1, r2, BUDGET, cfg, MRL)
                f.write(json.dumps({
                    "ordering": label, "config_id": cfg_name(cfg), "aca_id": aca, "rep": tag,
                    "budget": BUDGET, "mrl": MRL, "start_len": len(r1) + len(r2),
                    "solved": res["solved"], "nodes": res["nodes"],
                    "path_length": res["path_length"], "min_total": res["min_total"],
                    "start_K": res["start_K"], "min_K": res["min_K"]}) + "\n")
                f.flush()
                os.fsync(f.fileno())

    data = [json.loads(l) for l in open(OUT)]
    solved = [r for r in data if r["solved"]]

    lines = ["# EXP-12 — the 124 unsolved AC-classes, under the best orderings", "",
             f"Every class from `unsolved_124_aca_classes.csv`, started from each of its **8 "
             f"signed-permutation relabels** ({len(todo)} starts over {n_cls} classes), at "
             f"budget {BUDGET} with cap {MRL}. A relabel is the same presentation under a rename of "
             "the generators, so it is the same problem — but the greedy reads strings, so each "
             "image is a different search and any one solving settles the class.", "",
             "Scored on solves alone — EXP-07 showed no checkpoint proxy predicts a solve, so "
             "`min_total`/`min_K` below are for reading, not ranking.", ""]

    if solved:
        lines += ["## A class solved", ""]
        for r in solved:
            lines.append(f"- **{r['aca_id']}** (relabel `{r['rep']}`) by `{r['ordering']}` in "
                         f"{r['nodes']} nodes, path {r['path_length']}")
        lines.append("")
    else:
        lines += [f"**No class solved, under any ordering, from any of its 8 relabels.** That is "
                  f"the expected result and it is now measured over the whole target set rather "
                  f"than assumed from a six-row sample: these classes survived a 10^6-node search, "
                  f"and {BUDGET} nodes is three orders of magnitude short. The heuristic's "
                  "demonstrated value is on the decidable tier; carrying it to these classes means "
                  "running it at a Colab-scale budget, which this program cannot do locally.", ""]

    lines += ["## What each ordering reached (descriptive — not a ranking)", "",
              "| ordering | solved | mean shortest total reached | classes reaching fewer knots |",
              "|---|---|---|---|"]
    for label in ORDERINGS:
        d = [r for r in data if r["ordering"] == label]
        if not d:
            continue
        mt = sum(r["min_total"] for r in d) / len(d)
        kr = len({r["aca_id"] for r in d if r["min_K"] < r["start_K"]})
        lines.append(f"| {label} | {sum(r['solved'] for r in d)}/{len(d)} | {mt:.1f} | {kr}/{n_cls} |")
    lines.append("")

    with open(os.path.join(LOGS, "EXP12_unsolved124.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
