"""Annotate the 124 class reps with their mu-ladder descent (the "reduced" ones).

Reads the big-ladder summary (`mu_ladder_big_aca124_r256_b64_mrl24.jsonl`, 256
rungs / beam 64, the closed census) and writes `aca_124.csv` back out with four
extra columns: whether the class's Aut-minimal total length was strictly
reduced, and the Aut-minimal representative pair of the descended orbit.

`mu` = the Aut(F2)-minimal total length of a class's orbit (`aut_canon`), so
`new_r1`/`new_r2` is the shortest pair in the orbit the CoV ladder reached, and
`mu_out = |new_r1| + |new_r2|`.  All 124 class reps are themselves Aut-canonical
at `mu_in`, so `mu_in` is equally the rep's raw total length -- the two rulers
agree at the start and can only diverge at the finish.

**`reduce_kind` is the column that matters, not `reduced`.**  Two different
claims live in this file and merging them would be a category error:

  - `mu_floor` (36 classes) -- the CoV ladder moved the class to a **strictly
    lower Aut-orbit floor**, `mu_out < mu_in`.  A genuinely new orbit.
  - `length_only` (3 classes, via `--ext`) -- an external table shortened one
    *member*'s raw spelling, but `aut_canon` puts the finish at `mu_out ==
    mu_in`: the same orbit written shorter, or a member walked up to the class
    rep we already start from.  Zero orbit distance.  These rows exist so the
    external result is recorded, NOT because the class descended.

Every `mu_floor` row is re-verified against the pure-Python `aut_canon` spec:
the recorded pair must be its own Aut-canonical representative and its total
must equal the recorded `mu_out`.  (The ladder itself keyed on the numba twin
`autcanon_fast`, so this is also a fast-vs-slow cross-check on all 36 rows.)

A greedy solve from a `mu_floor` start certifies STABLE AC-triviality of the
source class only -- the certificate is [CoV chain] + [greedy path], never a
plain AC path.  The chains themselves stay in the jsonl (`best_chain`).  A
`length_only` start certifies nothing new: it is in the class rep's own orbit.

Usage:
    .venv/bin/python3 -m experiments.stable_ac.cov.ladder.export_aca124_reduced \
        [--ladder results/stable_ac/mu_scan/mu_ladder_big_aca124_r256_b64_mrl24.jsonl] \
        [--base data/ms_unsolved_reps/aca_124.csv] \
        [--ext <external length-reduction csv>] \
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
NEW_FIELDS = ["reduced", "reduce_kind", "mu_in", "mu_out", "new_r1", "new_r2",
              "n_hops", "source", "ext_label"]


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
    ap.add_argument("--best-out", default="data/ms_unsolved_reps/aca_124_best.csv",
                    help="drop-in replacement for aca_124.csv: SAME 5 columns, "
                         "r1/r2 swapped to the reduced pair on reduced classes, "
                         "byte-identical rows on the rest")
    ap.add_argument("--ext", action="append", default=[],
                    help="external length-reduction csv (label,finish_r1,finish_r2); "
                         "folded in as reduce_kind=length_only for classes the "
                         "ladder did NOT descend. Repeatable.")
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

    # label -> best external finish, keyed by the class the label belongs to.
    # Keep the LOWEST-mu finish per class; ties broken by shortest raw spelling.
    ext_by_class = {}
    lab2cls = {m: r["name"] for r in base for m in r["members"].split()}
    for path in args.ext:
        for e in csv.DictReader(open(path)):
            cls = lab2cls.get(e["label"])
            if cls is None:
                raise SystemExit(f"external label {e['label']} is in none of the 124")
            pair = (e["finish_r1"], e["finish_r2"])
            mu = aut_canon(pair)[0]
            key = (mu, len(pair[0]) + len(pair[1]))
            if cls not in ext_by_class or key < ext_by_class[cls][0]:
                ext_by_class[cls] = (key, e["label"], pair, mu)

    rows, n_mu, n_len, bad = [], 0, 0, []
    for src in base:
        row = dict(src)
        lad = ladder.get(src["name"])
        if lad is None:
            raise SystemExit(f"{src['name']} missing from the ladder summary")
        if (lad["r1_orig"], lad["r2_orig"]) != (src["r1"], src["r2"]):
            raise SystemExit(f"{src['name']}: ladder pair != base csv pair")
        ext = ext_by_class.get(src["name"])
        if lad["best_mu"] < lad["mu_in"]:
            n_mu += 1
            new_r1, new_r2 = lad["best_rep"]
            if not args.no_verify and not verify((new_r1, new_r2), lad["best_mu"]):
                bad.append(src["name"])
            row.update(reduced="yes", reduce_kind="mu_floor", mu_in=lad["mu_in"],
                       mu_out=lad["best_mu"], new_r1=new_r1, new_r2=new_r2,
                       n_hops=len(lad["best_chain"]),
                       source="mu_ladder_r256_b64", ext_label=NONE)
        elif ext is not None:
            # The ladder found no descent; an external table shortened one
            # member's spelling. mu_out == mu_in here BY CONSTRUCTION of this
            # branch -- if it were lower the ladder branch above would have
            # taken it -- so guard that the external claim is not a real
            # descent we are about to mislabel.
            _, lab, pair, mu = ext
            if mu < lad["mu_in"]:
                raise SystemExit(
                    f"{src['name']}: external {lab} reaches mu {mu} < mu_in "
                    f"{lad['mu_in']} -- a REAL orbit descent the ladder missed. "
                    f"Do not file it as length_only; rerun the ladder.")
            n_len += 1
            row.update(reduced="yes", reduce_kind="length_only",
                       mu_in=lad["mu_in"], mu_out=mu,
                       new_r1=pair[0], new_r2=pair[1], n_hops=NONE,
                       source="external_len_table", ext_label=lab)
        else:
            row.update(reduced="no", reduce_kind=NONE, mu_in=lad["mu_in"],
                       mu_out=NONE, new_r1=NONE, new_r2=NONE, n_hops=NONE,
                       source=NONE, ext_label=NONE)
        rows.append(row)

    if bad:
        raise SystemExit(f"aut_canon verification FAILED on {len(bad)}: {bad}")
    n_reduced = n_mu + n_len

    out = os.path.join(root, args.out)
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=base_fields + NEW_FIELDS)
        w.writeheader()
        w.writerows(rows)

    # The drop-in twin: aca_124.csv's exact schema, best-known pair per class.
    # Anything that loads aca_124.csv loads this unchanged, which is the point --
    # so it must carry NO extra column and no reduction bookkeeping.
    best_path = os.path.join(root, args.best_out)
    n_swapped = 0
    with open(best_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=base_fields)
        w.writeheader()
        for r in rows:
            b = {k: r[k] for k in base_fields}
            if r["reduced"] == "yes":
                b["r1"], b["r2"] = r["new_r1"], r["new_r2"]
                n_swapped += 1
            w.writerow(b)
    print(f"{len(rows)} classes -> {out}")
    print(f"  reduced: {n_reduced}   not reduced: {len(rows) - n_reduced}")
    print(f"    reduce_kind=mu_floor    {n_mu:>3}  (strictly lower Aut-orbit floor)"
          f"{'' if args.no_verify else ' -- all aut_canon-verified'}")
    print(f"    reduce_kind=length_only {n_len:>3}  (shorter spelling, mu_out == mu_in"
          f" -- NOT an orbit descent)")
    print(f"{len(rows)} classes -> {best_path}")
    print(f"  drop-in for aca_124.csv ({','.join(base_fields)}); "
          f"{n_swapped} rows swapped to the reduced pair, "
          f"{len(rows) - n_swapped} byte-identical")


if __name__ == "__main__":
    main()
