"""The 126 ACA classes as a run manifest: one Aut-minimal presentation per class.

This is an INPUT list for the next sweep, not a results file. Every search-produced
field is null, because these 126 have never been searched -- the 1M-node sweep ran the
*261 roots*, and 135 of those runs were answering a question another run had already
answered (results/equivalence_classes/EQUIVALENCE_FINDING.md).

The presentation emitted per class is the class's **Aut-minimal** form, not one of the
member roots. That is deliberate: greedy is length-guided, so the shortest presentation of
a problem is the best-conditioned search for it, and for 6 of the 126 the Aut-minimal form
is strictly shorter than every member root.

Deliberately NOT written to results/greedy_baseline/. That directory is a resume contract:
run_baseline.py globs it by run-prefix to find a run to continue, and difficulty_bins.py
does a non-recursive listdir keyed on `greedy_{budget}_640_`. A hand-built file with a
run-shaped name in there is a live hazard, not just data.
"""
import csv
import json
import os

from experiments.equivalence_classes.lib.autcanon import aut_canon
from experiments.equivalence_classes.lib.words import abelian_det, canon_pair

REPO = os.path.abspath(__file__)
while not (os.path.isdir(os.path.join(REPO, "experiments"))
           and os.path.isdir(os.path.join(REPO, "data"))):
    REPO = os.path.dirname(REPO)

CLASSES = os.path.join(REPO, "results", "equivalence_classes",
                       "classes_sweep_seam_28_250.csv")
REPS = os.path.join(REPO, "data", "ms_unsolved_reps", "ms_reps_unsolved.csv")
OUT = os.path.join(REPO, "results", "equivalence_classes",
                   "classes_126_from_greedy_1000000_261_mrl48.jsonl")

# Every field the 261 sweep's jsonl carries. The ones a search *produces* are null here;
# the run knobs are null too, because the run they describe has not been chosen yet.
SEARCH_FIELDS = (
    "solved", "nodes_explored", "path_length", "time_seconds",
    "min_relator", "min_relator_length",
    "max_relator", "max_relator_length",
    "max_relator_expanded", "max_relator_length_expanded",
    "node_budget", "max_relator_length_cap",
)


def main():
    roots = {r["name"]: canon_pair(r["r1"], r["r2"])
             for r in csv.DictReader(open(REPS))}
    assert len(roots) == 261, len(roots)

    classes = list(csv.DictReader(open(CLASSES)))
    assert len(classes) == 126, len(classes)

    seen_members, rows = set(), []
    for c in classes:
        members = c["members"].split()
        r1, r2 = c["representative"].split(",")

        # The rep must be a canonical pair already -- otherwise the file it seeds would
        # canonicalise to something other than what is written here.
        assert (r1, r2) == canon_pair(r1, r2), (c["class_id"], r1, r2)

        # And it must genuinely be the Aut-minimal form of one of its own members. This
        # re-derives the link from the raw CSV roots, so a corrupted class table cannot
        # slip a presentation in here that has nothing to do with the class.
        assert (r1, r2) in {tuple(aut_canon(roots[m])[1]) for m in members}, c["class_id"]

        # |det| of the exponent-sum matrix is invariant under both AC moves and change of
        # variables, so it must agree across the rep and every member root. The *sign* is
        # not invariant -- inverting a relator flips it -- so compare absolute values.
        dets = {abs(abelian_det(r1, r2))} | {abs(abelian_det(*roots[m])) for m in members}
        assert dets == {int(c["abs_det"])} == {1}, (c["class_id"], dets)

        assert len(r1) + len(r2) == int(c["rep_len"]), c["class_id"]
        assert seen_members.isdisjoint(members), c["class_id"]
        seen_members.update(members)

        row = {"pres_id": len(rows), "r1": r1, "r2": r2,
               "class_id": int(c["class_id"]),
               "n_members": len(members), "members": members,
               "rep_len": int(c["rep_len"]), "orig_len": int(c["orig_len"]),
               "saved": int(c["saved"]), "abs_det": int(c["abs_det"]),
               "cyclic_reduce": True}
        row.update({k: None for k in SEARCH_FIELDS})
        rows.append(row)

    assert seen_members == set(roots), len(seen_members ^ set(roots))

    with open(OUT, "w") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")

    total = sum(r["rep_len"] for r in rows)
    orig = sum(len(a) + len(b) for a, b in roots.values())
    print(f"{OUT}")
    print(f"  classes           : {len(rows)}")
    print(f"  member roots       : {len(seen_members)} (== the 261, exactly)")
    print(f"  shorter than every member root : "
          f"{sum(1 for r in rows if r['saved'] > 0)}")
    print(f"  total relator length : {total}  (vs {orig} to run all 261)")


if __name__ == "__main__":
    main()
