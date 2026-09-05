"""Depth-2 mu-descent scan over the 124 unsolved classes.

Background (STABLE_AC_NEW.tex, orbit-floor section): the Aut-minimal total
length mu is NOT invariant under subword-CoV — an ``n_subs >= 2`` hop can land
in a strictly lower-mu orbit (AK(2) 11 -> 10; one ms640 row 6 -> 2, the
standard orbit). On the aca124 sweep data exactly 4 classes have a hop-1
descent. This tool maps hop-2: from each class rep, enumerate the gated
subword-CoV family (hop 1), keep the ``K`` lowest-mu orbit-moving outputs, and
enumerate each of those (hop 2), recording the minimum mu reachable and every
descending path found. Descents can pass through uphill intermediates, so
hop-2 is enumerated from ALL kept hop-1 outputs, not only descending ones.

Pure enumeration + Whitehead canonicalisation — ZERO search nodes, so it runs
locally. Cost ~ 124 x (family + K x family) transforms x ~5 ms aut_canon.

Usage:
    .venv/bin/python3 -m experiments.stable_ac.cov.mu_descent_scan \
        [--cap 24] [--keep 10] [--names aca_0 ...] [--out results/...]

Output: one jsonl row per class: {pres_id, cap, mu_in, best_mu1, best_mu2,
n_orbits1, n_orbits2, descents: [{hops, mu, z_path, via}]} sorted by gain.
"""

import argparse
import json
import os

from experiments.equivalence_classes.lib.autcanon import aut_canon
from experiments.greedy_tests.spec.words import str_to_word, word_to_str
from experiments.stable_ac.cov import cov

HERE = os.path.dirname(os.path.abspath(__file__))


def find_repo_root(start):
    d = os.path.abspath(start)
    while True:
        if (os.path.isdir(os.path.join(d, "experiments"))
                and os.path.isdir(os.path.join(d, "data"))):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            raise RuntimeError(f"no repo root above {start}")
        d = parent


def orbit(pair_strs):
    t, rep, _ = aut_canon(pair_strs)
    return t, rep


def hop_outputs(r1s, r2s, cap):
    """Deduped orbit-moving CoV outputs of one pair: {orbit_rep: (mu, out_pair, z)}."""
    res = cov.enumerate_cov(str_to_word(r1s), str_to_word(r2s),
                            default_cap=cap, cap_headroom=cov.CAP_HEADROOM,
                            reject_len=cov.REJECT_LEN)
    _, rep_in = orbit((r1s, r2s))
    out = {}
    for c in res:
        o1, o2 = word_to_str(c.r1), word_to_str(c.r2)
        mu, rep = orbit((o1, o2))
        if rep == rep_in or rep in out:
            continue
        out[rep] = (mu, (o1, o2), word_to_str(c.z_word))
    return out


def scan_one(pres_id, r1s, r2s, cap, keep):
    mu_in, rep_in = orbit((r1s, r2s))
    h1 = hop_outputs(r1s, r2s, cap)
    best1 = min((m for m, _, _ in h1.values()), default=mu_in)
    descents = [{"hops": 1, "mu": m, "z_path": [z], "via": rep}
                for rep, (m, _, z) in h1.items() if m < mu_in]
    kept = sorted(h1.items(), key=lambda kv: kv[1][0])[:keep]
    seen2, best2 = set(h1), best1
    for rep1, (m1, pair1, z1) in kept:
        for rep2, (m2, pair2, z2) in hop_outputs(*pair1, cap).items():
            if rep2 == rep_in or rep2 in seen2:
                continue
            seen2.add(rep2)
            best2 = min(best2, m2)
            if m2 < mu_in:
                descents.append({"hops": 2, "mu": m2, "z_path": [z1, z2],
                                 "via": rep1})
    descents.sort(key=lambda d: d["mu"])
    return {"pres_id": pres_id, "cap": cap, "mu_in": mu_in,
            "best_mu1": best1, "best_mu2": best2,
            "n_orbits1": len(h1), "n_orbits2": len(seen2),
            "descents": descents[:20]}


def main():
    ap = argparse.ArgumentParser(description="Depth-2 mu-descent scan.")
    ap.add_argument("--cap", type=int, default=24)
    ap.add_argument("--keep", type=int, default=10,
                    help="hop-1 orbits (lowest mu first) to expand at hop 2")
    ap.add_argument("--names", nargs="*", default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--data", default="data/ms_unsolved_reps/aca_124.csv",
                    help="name,r1,r2 CSV of presentations to scan")
    args = ap.parse_args()
    root = find_repo_root(HERE)
    tag = os.path.splitext(os.path.basename(args.data))[0]
    tag = "aca124" if tag == "aca_124" else tag    # keep the shipped file identity
    out = args.out or os.path.join(
        root, f"results/stable_ac/mu_scan/mu_scan_{tag}_d2_k{args.keep}"
              f"_mrl{args.cap}.jsonl")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    done = set()
    if os.path.exists(out):
        for ln in open(out):
            try:
                done.add(json.loads(ln)["pres_id"])
            except (ValueError, KeyError):
                continue
    import csv
    rows = list(csv.DictReader(open(os.path.join(root, args.data))))
    if args.names:
        keep_names = set(args.names)
        rows = [r for r in rows if r["name"] in keep_names]
    todo = [r for r in rows if r["name"] not in done]
    print(f"{len(todo)} classes to scan (cap {args.cap}, keep {args.keep}) "
          f"-> {os.path.basename(out)}", flush=True)
    with open(out, "a") as f:
        for i, r in enumerate(todo):
            row = scan_one(r["name"], r["r1"], r["r2"], args.cap, args.keep)
            f.write(json.dumps(row) + "\n")
            f.flush()
            tag = (f" DESC mu {row['mu_in']}->{row['best_mu2']}"
                   if row["best_mu2"] < row["mu_in"] else "")
            print(f"  [{i+1}/{len(todo)}] {r['name']} orbits "
                  f"{row['n_orbits1']}/{row['n_orbits2']}{tag}", flush=True)
    print(f"written: {out}", flush=True)


if __name__ == "__main__":
    main()
