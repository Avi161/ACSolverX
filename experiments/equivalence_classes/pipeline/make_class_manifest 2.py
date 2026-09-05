"""The 126 ACA classes: one Aut-minimal presentation per class, as a runnable dataset.

The 1M-node sweep ran the *261 roots*, and 135 of those runs were answering a question
another run had already answered (results/equivalence_classes/EQUIVALENCE_FINDING.md).
This emits the 126 distinct problems so the next sweep does not repeat them.

Two files, because they are for two different readers:

  data/ms_unsolved_reps/ms_reps_126.txt   -- what run_baseline.py actually EATS.
      Flat ints, one line per presentation, `ast.literal_eval`-able, exactly the format
      of ms_reps_unsolved.txt (which is what the 261 sweep ran off). Point CONFIG's
      DATASET at this and the sweep runs the 126. The manifest jsonl is NOT loadable by
      run_baseline -- load_dataset() parses flat ints, never json -- so a jsonl alone
      would have been a description of the work, not a way to do it.

  results/equivalence_classes/sweep/classes_126_...jsonl  -- the human/analysis record.
      Same field set as the 261 sweep's jsonl, plus class provenance (which of the 261
      each row stands for). Every search-produced field is null: these 126 presentations
      have never been searched.

The presentation emitted per class is the class's **Aut-minimal** form, not one of the
member roots. That is deliberate: greedy is length-guided, so the shortest presentation of
a problem is the best-conditioned search for it, and for 6 of the 126 the Aut-minimal form
is strictly shorter than every member root.

So "which of the members IS this presentation?" usually has no answer, and the row says so
rather than leaving the reader to guess:

  rep_from            which member(s) the rep is the Aut-minimal FORM of. Not all of them:
                      an ACA class is several Aut-classes joined by AC moves, and the rep
                      canonicalises only the one it came from. Class 0 lists 8 members but
                      rep_from is ["18_6"] alone -- the other 7 are in different Aut-classes
                      and reach the rep only via AC moves.
  rep_phi             the change of variables with canon(phi(root of rep_from[0])) == (r1, r2).
  rep_is_member_root  whether the rep literally equals some member's canonical root. True in
                      only 52 of the 126; in the other 74 it is a form no member equals.

The jsonl is deliberately NOT written to results/greedy_baseline/. That directory is a
resume contract: run_baseline.py globs it by run-prefix to find a run to continue, and
difficulty_bins.py does a non-recursive listdir keyed on `greedy_{budget}_640_` and
hard-fails unless it matches exactly one file. A hand-built file with a run-shaped name in
there is a live hazard, not just data.
"""
import csv
import json
import os

from experiments.equivalence_classes.lib.autcanon import aut_canon, is_automorphism
from experiments.equivalence_classes.lib.words import abelian_det, apply_pair, canon_pair
from experiments.run_baseline import load_dataset

REPO = os.path.abspath(__file__)
while not (os.path.isdir(os.path.join(REPO, "experiments"))
           and os.path.isdir(os.path.join(REPO, "data"))):
    REPO = os.path.dirname(REPO)

CLASSES = os.path.join(REPO, "results", "equivalence_classes", "sweep",
                       "classes_sweep_seam_28_250.csv")
REPS = os.path.join(REPO, "data", "ms_unsolved_reps", "ms_reps_unsolved.csv")
OUT = os.path.join(REPO, "results", "equivalence_classes", "sweep",
                   "classes_126_from_greedy_1000000_261_mrl48.jsonl")
OUT_TXT = os.path.join(REPO, "data", "ms_unsolved_reps", "ms_reps_126.txt")

# The zero-padding width of the DATA FILE -- not the search's MAX_RELATOR_LENGTH cap.
# int_line_to_relators() strips the zeros, so this only has to be >= the longest single
# relator (17 here); the search cap is a separate CONFIG knob. ms_reps_unsolved.txt uses
# 24, so the 126 use 24, and the two files stay drop-in interchangeable.
PAD = 24
CHAR_TO_INT = {"x": 1, "X": -1, "y": 2, "Y": -2}


def _int_line(r1, r2):
    """(r1, r2) -> the flat int line, matching data/ms640_solved.txt's encoding."""
    out = []
    for rel in (r1, r2):
        assert len(rel) <= PAD, (rel, len(rel))
        out += [CHAR_TO_INT[c] for c in rel] + [0] * (PAD - len(rel))
    return out

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

        # Which members is the rep the Aut-minimal form OF? Not all of them: an ACA class
        # is several Aut-classes joined by AC moves, and the rep canonicalises only the
        # one it came from. In class 0 that is 18_6 alone -- the other 7 sit in different
        # Aut-classes and reach the rep only via AC moves. Recording this is the whole
        # point: without it the row names 8 members and silently declines to say which one
        # the presentation on the line actually is. (It is a member ROOT in only 52 of the
        # 126; in the other 74, like class 0, the rep is a canonical form no member equals.)
        phis = {m: aut_canon(roots[m]) for m in members}
        rep_from = sorted(m for m in members if tuple(phis[m][1]) == (r1, r2))

        # This doubles as the integrity check: re-derived from the raw CSV roots, so a
        # corrupted class table cannot slip in a presentation unrelated to the class.
        assert rep_from, c["class_id"]

        # |det| of the exponent-sum matrix is invariant under both AC moves and change of
        # variables, so it must agree across the rep and every member root. The *sign* is
        # not invariant -- inverting a relator flips it -- so compare absolute values.
        dets = {abs(abelian_det(r1, r2))} | {abs(abelian_det(*roots[m])) for m in members}
        assert dets == {int(c["abs_det"])} == {1}, (c["class_id"], dets)

        assert len(r1) + len(r2) == int(c["rep_len"]), c["class_id"]
        assert seen_members.isdisjoint(members), c["class_id"]
        seen_members.update(members)

        # phi carries rep_from[0]'s root TO the presentation on this line. Check that by
        # actually SUBSTITUTING phi and canonicalising -- not by re-reading aut_canon's own
        # answer, which would just be asking the same oracle twice.
        phi = phis[rep_from[0]][2]
        assert apply_pair(roots[rep_from[0]], phi) == (r1, r2), c["class_id"]
        assert is_automorphism(phi), (c["class_id"], phi)

        row = {"pres_id": len(rows), "r1": r1, "r2": r2,
               "class_id": int(c["class_id"]),
               "rep_from": rep_from, "rep_phi": phi,
               "rep_is_member_root": any(roots[m] == (r1, r2) for m in members),
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

    with open(OUT_TXT, "w") as f:
        for row in rows:
            f.write(json.dumps(_int_line(row["r1"], row["r2"])) + "\n")

    # The dataset is only useful if the thing that will run it can read it. Round-trip
    # through run_baseline's OWN loader -- not a reimplementation of it -- and require
    # that what comes back is exactly what went in, in order.
    loaded = list(load_dataset(OUT_TXT))
    assert loaded == [(r["pres_id"], r["r1"], r["r2"]) for r in rows], "round-trip failed"

    total = sum(r["rep_len"] for r in rows)
    orig = sum(len(a) + len(b) for a, b in roots.values())
    print(f"{OUT_TXT}")
    print(f"  run_baseline.load_dataset round-trip : {len(loaded)}/126 exact")
    print(f"{OUT}")
    print(f"  classes            : {len(rows)}")
    print(f"  member roots       : {len(seen_members)} (== the 261, exactly)")
    print(f"  rep IS a member root           : "
          f"{sum(1 for r in rows if r['rep_is_member_root'])}"
          f"  (in the other {sum(1 for r in rows if not r['rep_is_member_root'])} "
          f"it equals no member)")
    print(f"  shorter than every member root : "
          f"{sum(1 for r in rows if r['saved'] > 0)}")
    print(f"  total relator length : {total}  (vs {orig} to run all 261)")


if __name__ == "__main__":
    main()
