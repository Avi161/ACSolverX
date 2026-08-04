"""Score an external length-reduction table against our 36-of-124 mu descents.

An external table gives `(start_r1, start_r2) -> (finish_r1, finish_r2)` with a
raw total-length improvement.  Raw length is the wrong ruler: a shorter spelling
of the SAME Aut(F2)-orbit is not a reduction at all, and only the orbit floor
`mu = aut_canon(...)[0]` is comparable across methods.  So this script reduces
BOTH endpoints of every external row to Aut-canonical form and asks three
questions:

  1. Which of the 124 AC classes does the row belong to?  Matched on the MS
     **label** (`21_2`) against `aca_124.csv`'s `members`, never on any row
     index -- an external index column need not agree with ours.  The match is
     then re-verified against `ms_reps_unsolved.csv`: the external start pair
     must be that label's presentation exactly.
  2. Did the external finish actually LOWER the orbit floor (`d_mu > 0`), or is
     it the same orbit spelled shorter (`d_mu == 0`)?
  3. Head-to-head on rows whose class we also reduced: whose floor is lower, and
     when the floors tie, is it literally the same orbit (same canonical rep)?

Usage:
    .venv/bin/python3 -m experiments.stable_ac.cov.ladder.compare_external_reductions \
        --ext <external.csv> [--out results/stable_ac/mu_scan/external_compare.csv]

The external csv needs the columns `label,start_r1,start_r2,finish_r1,finish_r2`.
"""

import argparse
import csv
import os

from experiments.equivalence_classes.lib.autcanon import aut_canon
from experiments.stable_ac.cov.ladder.mu_descent_scan import find_repo_root

HERE = os.path.dirname(os.path.abspath(__file__))

FIELDS = ["label", "class", "in_our_36", "ext_start_mu", "ext_finish_mu",
          "ext_d_mu", "ext_finish_r1", "ext_finish_r2", "our_mu_in",
          "our_mu_out", "our_new_r1", "our_new_r2", "verdict", "same_orbit",
          "label_pair_verified"]


def main():
    ap = argparse.ArgumentParser(description="Score an external reduction table.")
    ap.add_argument("--ext", required=True, help="external csv")
    ap.add_argument("--ours", default="data/ms_unsolved_reps/aca_124_reduced.csv")
    ap.add_argument("--ms", default="data/ms_unsolved_reps/ms_reps_unsolved.csv")
    ap.add_argument("--out", default="results/stable_ac/mu_scan/external_compare.csv")
    args = ap.parse_args()
    root = find_repo_root(HERE)

    ours = list(csv.DictReader(open(os.path.join(root, args.ours))))
    lab2cls = {m: r for r in ours for m in r["members"].split()}
    ms = {r["name"]: (r["r1"], r["r2"])
          for r in csv.DictReader(open(os.path.join(root, args.ms)))}

    rows = []
    for e in csv.DictReader(open(args.ext)):
        lab = e["label"]
        cls = lab2cls.get(lab)
        if cls is None:
            raise SystemExit(f"label {lab} is in none of the 124 classes")
        s_mu, s_rep, _ = aut_canon((e["start_r1"], e["start_r2"]))
        f_mu, f_rep, _ = aut_canon((e["finish_r1"], e["finish_r2"]))
        reduced = cls["reduced"] == "yes"
        our_out = int(cls["mu_out"]) if reduced else None
        if not reduced:
            verdict = "class not in our 36"
        elif our_out < f_mu:
            verdict = f"ours lower by {f_mu - our_out}"
        elif our_out == f_mu:
            verdict = "tie"
        else:
            verdict = f"theirs lower by {our_out - f_mu}"
        rows.append({
            "label": lab, "class": cls["name"],
            "in_our_36": "yes" if reduced else "no",
            "ext_start_mu": s_mu, "ext_finish_mu": f_mu, "ext_d_mu": s_mu - f_mu,
            "ext_finish_r1": f_rep[0], "ext_finish_r2": f_rep[1],
            "our_mu_in": cls["mu_in"], "our_mu_out": cls["mu_out"],
            "our_new_r1": cls["new_r1"], "our_new_r2": cls["new_r2"],
            "verdict": verdict,
            "same_orbit": ("yes" if list(f_rep) == [cls["new_r1"], cls["new_r2"]]
                           else "no") if reduced else "none",
            # the label must name exactly this start pair in the MS source
            "label_pair_verified": "yes" if ms.get(lab) == (
                e["start_r1"], e["start_r2"]) else "NO",
        })

    out = os.path.join(root, args.out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)

    n = len(rows)
    inset = [r for r in rows if r["in_our_36"] == "yes"]
    print(f"{n} external rows, {len({r['class'] for r in rows})} distinct classes "
          f"-> {out}")
    print(f"  label->pair verified against ms_reps_unsolved: "
          f"{sum(r['label_pair_verified'] == 'yes' for r in rows)}/{n}")
    print(f"  in our 36 reduced: {len(inset)}   not: {n - len(inset)}")
    print(f"  external finish actually lowers its own orbit floor: "
          f"{sum(r['ext_d_mu'] > 0 for r in rows)}/{n} "
          f"({sum(r['ext_d_mu'] == 0 for r in rows)} are the same orbit, shorter spelling)")
    print(f"  head-to-head on the {len(inset)} shared: "
          f"ours lower {sum(r['verdict'].startswith('ours') for r in inset)}, "
          f"tie {sum(r['verdict'] == 'tie' for r in inset)}, "
          f"theirs lower {sum(r['verdict'].startswith('theirs') for r in inset)}")


if __name__ == "__main__":
    main()
