"""Export the mu-descended CoV starts as a searchable dataset.

Reads a ``mu_descent_scan`` jsonl, re-derives each descending chain's CONCRETE
output pair (the scan records ``z_path`` + target orbit, not the pair), verifies
the re-derivation lands in an orbit with the recorded mu, and writes a CSV in
the aca_124 format (``name,r1,r2`` + provenance columns) for the portfolio /
greedy runners. A solve from any exported start certifies STABLE AC-triviality
of its source class: the start is reached from the class rep by 1-2 CoV hops
(stable supermoves), so the certificate is [CoV chain] + [greedy path] — the
same segmented accounting as the restart tree.

Usage:
    .venv/bin/python3 -m experiments.stable_ac.cov.export_mu_descents \
        [--scan results/stable_ac/mu_scan/mu_scan_aca124_d2_k10_mrl24.jsonl] \
        [--out data/ms_unsolved_reps/mu_descents_d2.csv]
"""

import argparse
import csv
import json
import os

from experiments.equivalence_classes.lib.autcanon import aut_canon
from experiments.greedy_tests.spec.words import str_to_word, word_to_str
from experiments.stable_ac.cov import cov
from experiments.stable_ac.cov.mu_descent_scan import find_repo_root

HERE = os.path.dirname(os.path.abspath(__file__))


def _branches(r1s, r2s, z, cap):
    """All CoV branch outputs of (r1s, r2s) for subword z, as string pairs."""
    out = []
    for iso_gen in ("x", "y"):
        for res in cov.cov_branches(str_to_word(r1s), str_to_word(r2s),
                                    str_to_word(z), default_cap=cap,
                                    cap_headroom=cov.CAP_HEADROOM,
                                    reject_len=cov.REJECT_LEN,
                                    iso_gen=iso_gen):
            out.append((word_to_str(res.r1), word_to_str(res.r2)))
    return out


def derive_chain(r1s, r2s, z_path, target_mu, cap):
    """Follow z_path from (r1s, r2s); return the first concrete pair whose
    orbit has the recorded target mu (BFS over branch choices per hop)."""
    frontier = [(r1s, r2s)]
    for z in z_path:
        nxt = []
        for a, b in frontier:
            nxt.extend(_branches(a, b, z, cap))
        frontier = list(dict.fromkeys(nxt))
        if not frontier:
            return None
    for a, b in frontier:
        t, _, _ = aut_canon((a, b))
        if t == target_mu:
            return (a, b)
    return None


def main():
    ap = argparse.ArgumentParser(description="Export mu-descended starts.")
    ap.add_argument("--scan", default="results/stable_ac/mu_scan/"
                                      "mu_scan_aca124_d2_k10_mrl24.jsonl")
    ap.add_argument("--out", default="data/ms_unsolved_reps/mu_descents_d2.csv")
    ap.add_argument("--cap", type=int, default=24)
    args = ap.parse_args()
    root = find_repo_root(HERE)
    scan = os.path.join(root, args.scan)
    out = os.path.join(root, args.out)
    rows_out, failed = [], []
    for ln in open(scan):
        r = json.loads(ln)
        base = {row["name"]: row for row in csv.DictReader(
            open(os.path.join(root, "data/ms_unsolved_reps/aca_124.csv")))}
        if r["pres_id"] not in base:
            continue
        src = base[r["pres_id"]]
        for i, d in enumerate(dd for dd in r["descents"]
                              if dd["mu"] < r["mu_in"]):
            pair = derive_chain(src["r1"], src["r2"], d["z_path"], d["mu"],
                                args.cap)
            if pair is None:
                failed.append((r["pres_id"], d))
                continue
            rows_out.append({
                "name": f"{r['pres_id']}_d{d['hops']}_{i}",
                "r1": pair[0], "r2": pair[1],
                "source_class": r["pres_id"], "mu_source": r["mu_in"],
                "mu": d["mu"], "hops": d["hops"],
                "z_path": "+".join(d["z_path"]),
            })
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows_out[0].keys()))
        w.writeheader()
        w.writerows(rows_out)
    print(f"exported {len(rows_out)} descended starts from "
          f"{len({r['source_class'] for r in rows_out})} classes -> {out}")
    if failed:
        print(f"FAILED to re-derive {len(failed)}: "
              f"{[(p, d['z_path']) for p, d in failed]}")


if __name__ == "__main__":
    main()
