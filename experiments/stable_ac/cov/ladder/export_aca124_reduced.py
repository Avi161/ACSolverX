"""Annotate the 124 class reps with their mu-ladder descent (the "reduced" ones).

Reads the big-ladder summary (`mu_ladder_big_aca124_r256_b64_mrl24.jsonl`, 256
rungs / beam 64, the closed census) and writes `aca_124.csv` back out with four
extra columns: whether the class's Aut-minimal total length was strictly
reduced, and the Aut-minimal representative pair of the descended orbit.

`mu` = the Aut(F2)-minimal total length of a class's orbit (`aut_canon`), so
`new_r1`/`new_r2` is the shortest pair in the orbit the CoV ladder reached, and
`mu_out = |new_r1| + |new_r2|`.  A class is **reduced** iff `mu_out < mu_in`;
the 88 that never descended carry the literal string `none` in every new column.

Every reduced row is re-verified here against the pure-Python `aut_canon` spec:
the recorded pair must be its own Aut-canonical representative and its total
must equal the recorded `mu_out`.  (The ladder itself keyed on the numba twin
`autcanon_fast`, so this is also a fast-vs-slow cross-check on all 36 rows.)

A greedy solve from a `new_r1`/`new_r2` start certifies STABLE AC-triviality of
the source class only -- the certificate is [CoV chain] + [greedy path], never a
plain AC path.  The chains themselves stay in the jsonl (`best_chain`).

Usage:
    .venv/bin/python3 -m experiments.stable_ac.cov.ladder.export_aca124_reduced \
        [--ladder results/stable_ac/mu_scan/mu_ladder_big_aca124_r256_b64_mrl24.jsonl] \
        [--base data/ms_unsolved_reps/aca_124.csv] \
        [--out data/ms_unsolved_reps/aca_124_reduced.csv]
"""

import argparse
import csv
import json
import os

from experiments.equivalence_classes.lib.autcanon import aut_canon
from experiments.stable_ac.cov.ladder.mu_descent_scan import find_repo_root

HERE = os.path.dirname(os.path.abspath(__file__))

NONE = "none"
NEW_FIELDS = ["reduced", "mu_in", "mu_out", "new_r1", "new_r2", "n_hops"]


def verify(pair, mu_out):
    """The recorded pair must BE the Aut-canonical rep, at the recorded total."""
    total, rep, _ = aut_canon(tuple(pair))
    return total == mu_out and list(rep) == list(pair)


def main():
    ap = argparse.ArgumentParser(description="Annotate aca_124 with mu descents.")
    ap.add_argument("--ladder", default="results/stable_ac/mu_scan/"
                    "mu_ladder_big_aca124_r256_b64_mrl24.jsonl")
    ap.add_argument("--base", default="data/ms_unsolved_reps/aca_124.csv")
    ap.add_argument("--out", default="data/ms_unsolved_reps/aca_124_reduced.csv")
    ap.add_argument("--no-verify", action="store_true",
                    help="skip the aut_canon re-verification of reduced rows")
    args = ap.parse_args()
    root = find_repo_root(HERE)

    ladder = {}
    for ln in open(os.path.join(root, args.ladder)):
        r = json.loads(ln)
        ladder[r["pres_id"]] = r

    with open(os.path.join(root, args.base)) as f:
        base = list(csv.DictReader(f))
        base_fields = list(base[0].keys())

    rows, n_reduced, bad = [], 0, []
    for src in base:
        row = dict(src)
        lad = ladder.get(src["name"])
        if lad is None:
            raise SystemExit(f"{src['name']} missing from the ladder summary")
        if (lad["r1_orig"], lad["r2_orig"]) != (src["r1"], src["r2"]):
            raise SystemExit(f"{src['name']}: ladder pair != base csv pair")
        if lad["best_mu"] < lad["mu_in"]:
            n_reduced += 1
            new_r1, new_r2 = lad["best_rep"]
            if not args.no_verify and not verify((new_r1, new_r2), lad["best_mu"]):
                bad.append(src["name"])
            row.update(reduced="yes", mu_in=lad["mu_in"], mu_out=lad["best_mu"],
                       new_r1=new_r1, new_r2=new_r2,
                       n_hops=len(lad["best_chain"]))
        else:
            row.update(reduced="no", mu_in=lad["mu_in"], mu_out=NONE,
                       new_r1=NONE, new_r2=NONE, n_hops=NONE)
        rows.append(row)

    if bad:
        raise SystemExit(f"aut_canon verification FAILED on {len(bad)}: {bad}")

    out = os.path.join(root, args.out)
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=base_fields + NEW_FIELDS)
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} classes -> {out}  "
          f"({n_reduced} reduced, {len(rows) - n_reduced} not)"
          f"{'' if args.no_verify else '; all reduced rows aut_canon-verified'}")


if __name__ == "__main__":
    main()
