"""Turn a verified sweep into the deliverable class table.

Usage: make_class_table.py <sweep.json>
Writes: results/equivalence_classes/classes_<stem>.csv

One row per distinct problem. Columns:
  class_id      running index
  n_members     how many of the 261 reps collapse into it
  members       their names
  representative the Aut-minimal presentation to actually run (shortest in the class)
  rep_len       its total length
  orig_len      the total length of the lowest-named member as it appears in the CSV
  saved         orig_len - rep_len (greedy is length-guided, so this is a real head start)
  abs_det       the abelianisation invariant; must be constant within the class

RUN THE VERIFIER FIRST. This script does not re-check anything -- it formats results that
``verify_certificates.py`` has already accepted.
"""
import csv
import json
import os
import sys

# The repo root, found by walking up rather than by counting directory levels. A
# dirname chain encodes this file's depth, so it silently repoints at the wrong
# directory the moment the file moves -- and every path below is then wrong.
def _repo_root():
    d = os.path.dirname(os.path.abspath(__file__))
    while d != os.path.dirname(d):
        if (os.path.isdir(os.path.join(d, "experiments"))
                and os.path.isdir(os.path.join(d, "data"))):
            return d
        d = os.path.dirname(d)
    raise RuntimeError("repo root (holding experiments/ and data/) not found")


ROOT = _repo_root()
sys.path.insert(0, ROOT)

from experiments.equivalence_classes.lib.acmoves import canon  # noqa: E402
from experiments.equivalence_classes.lib.autcanon import aut_canon  # noqa: E402
from experiments.equivalence_classes.lib.words import abelian_det  # noqa: E402

OUT = os.path.join(ROOT, "results", "equivalence_classes")


def main():
    path = sys.argv[1]
    data = json.load(open(path))
    reps = {r["name"]: (r["r1"], r["r2"]) for r in csv.DictReader(
        open(os.path.join(ROOT, "data", "ms_unsolved_reps", "ms_reps_unsolved.csv")))}

    # older sweeps stored only `classes` (which include TRIVIAL / MS / J scaffolding sources)
    rep_classes = data.get("rep_classes")
    if rep_classes is None:
        rep_classes = [sorted(n for n in c if n in reps) for c in data["classes"]]
        rep_classes = [c for c in rep_classes if c]

    rows = []
    for cls in sorted(rep_classes, key=lambda c: (-len(c), c[0])):
        best = None
        for n in cls:
            t, rep, _ = aut_canon(canon(*reps[n]))
            if best is None or t < best[0]:
                best = (t, rep, n)
        t, rep, _ = best
        first = cls[0]
        orig = sum(map(len, reps[first]))
        dets = {abs(abelian_det(*reps[n])) for n in cls}
        assert len(dets) == 1, f"class {cls}: |det| not constant ({dets})"
        rows.append({
            "n_members": len(cls),
            "members": " ".join(cls),
            "representative": f"{rep[0]},{rep[1]}",
            "rep_len": t,
            "orig_len": orig,
            "saved": orig - t,
            "abs_det": dets.pop(),
        })

    stem = os.path.splitext(os.path.basename(path))[0]
    out = os.path.join(OUT, f"classes_{stem}.csv")
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, ["class_id", "n_members", "members", "representative",
                               "rep_len", "orig_len", "saved", "abs_det"])
        w.writeheader()
        for i, r in enumerate(rows):
            w.writerow({"class_id": i, **r})

    n = len(rows)
    multi = [r for r in rows if r["n_members"] > 1]
    shorter = [r for r in rows if r["saved"] > 0]
    print(f"{n} distinct problems from 261 presentations "
          f"({100*(1-n/261):.0f}% of the sweep was duplicated compute)")
    print(f"  multi-member classes : {len(multi)}   singletons: {n - len(multi)}")
    print(f"  largest              : {max(r['n_members'] for r in rows)}")
    print(f"  classes whose Aut-minimal representative is strictly shorter than the "
          f"member as shipped: {len(shorter)}")
    print(f"  total relator length to run: {sum(r['rep_len'] for r in rows)} "
          f"(vs {sum(sum(map(len, reps[n])) for n in reps)} for all 261)")
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
