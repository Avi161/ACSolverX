"""Iterated mu-descent beam ladder over CoV hops.

The depth-2/4 scans showed the Aut-orbit floor of most of the 124 classes is
not a wall: 19 classes descend within 2 hops, 7 of their outputs descend
further by hop 4, with no bottom in sight. This driver iterates properly: per
class, keep a beam of the K lowest-mu CONCRETE reachable pairs, expand each by
one gated subword-CoV hop per rung, dedupe orbits per class, track the best
floor and its full z-chain.

WHY THE FINISH LINE MATTERS (the jackpot criterion): every balanced
2-generator presentation of the trivial group with total length <= 12 is
AC-trivial (Miasnikov GA 1999 + MM03 exhaustion — AK(3) at length 13 is the
minimal open case), and by Havas-Ramsay a length-13 one is AC-equivalent to
standard or to AK(3). A CoV chain is a sequence of STABLE moves, so reaching
an orbit with mu <= 12 certifies the source class STABLY AC-TRIVIAL, and
reaching mu = 13 makes it stably equivalent to standard-or-AK(3) — decidable
by one aut_canon comparison against AK(3)'s orbit. Any hit is reported loudly
as a LEAD; the claim requires ac-advisor review of the criterion citations
plus independent chain re-derivation before being believed.

Pure enumeration + Whitehead canonicalisation — zero search nodes.

CLI:
    .venv/bin/python3 -m experiments.stable_ac.cov.mu_ladder \
        [--rungs 6] [--beam 10] [--jobs 8] [--stop-mu 13] [--names ...]
"""

import argparse
import json
import os
from concurrent.futures import ProcessPoolExecutor, as_completed

from experiments.equivalence_classes.lib.autcanon import aut_canon
from experiments.stable_ac.cov.mu_descent_scan import (
    find_repo_root,
    hop_outputs,
)

HERE = os.path.dirname(os.path.abspath(__file__))

AK3 = ("xxxYYYY", "xyxYXY")


def climb_one(args):
    """Ladder for one class. Returns the summary row (pure function, pickled
    to a worker). Beam entries are (mu, pair, chain) with chain = [z, z, ...];
    orbits are deduped per class across all rungs."""
    pres_id, r1, r2, rungs, beam_k, cap, stop_mu = args
    mu_in, rep_in, _ = aut_canon((r1, r2))
    seen = {rep_in}
    beam = [(mu_in, (r1, r2), [])]
    best_mu, best_chain, best_rep = mu_in, [], rep_in
    rung_log = []
    for rung in range(1, rungs + 1):
        cand = []
        for mu_b, pair, chain in beam:
            for rep, (mu, out_pair, z) in hop_outputs(*pair, cap).items():
                if rep in seen:
                    continue
                seen.add(rep)
                cand.append((mu, out_pair, chain + [z], rep))
        if not cand:
            rung_log.append({"rung": rung, "new_orbits": 0, "best": best_mu})
            break
        cand.sort(key=lambda t: (t[0], t[1]))
        for mu, out_pair, chain, rep in cand:
            if mu < best_mu:
                best_mu, best_chain, best_rep = mu, chain, rep
        beam = [(mu, p, c) for mu, p, c, _ in cand[:beam_k]]
        rung_log.append({"rung": rung, "new_orbits": len(cand),
                         "best": best_mu})
        if best_mu <= stop_mu:
            break
    _, ak3_rep, _ = aut_canon(AK3)
    return {"pres_id": pres_id, "mu_in": mu_in, "best_mu": best_mu,
            "best_chain": best_chain, "best_rep": best_rep,
            "hits_stop": best_mu <= stop_mu,
            "is_ak3_orbit": best_rep == ak3_rep,
            "n_orbits_seen": len(seen), "rungs": rung_log}


def main():
    ap = argparse.ArgumentParser(description="Iterated mu-descent beam ladder.")
    ap.add_argument("--data", default="data/ms_unsolved_reps/aca_124.csv")
    ap.add_argument("--rungs", type=int, default=6)
    ap.add_argument("--beam", type=int, default=10)
    ap.add_argument("--cap", type=int, default=24)
    ap.add_argument("--jobs", type=int, default=None)
    ap.add_argument("--stop-mu", type=int, default=13)
    ap.add_argument("--names", nargs="*", default=None)
    args = ap.parse_args()
    root = find_repo_root(HERE)
    import csv
    rows = list(csv.DictReader(open(os.path.join(root, args.data))))
    if args.names:
        keep = set(args.names)
        rows = [r for r in rows if r["name"] in keep]
    tag = os.path.splitext(os.path.basename(args.data))[0]
    tag = "aca124" if tag == "aca_124" else tag
    out = os.path.join(root, f"results/stable_ac/mu_scan/mu_ladder_{tag}"
                             f"_r{args.rungs}_b{args.beam}_mrl{args.cap}.jsonl")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    done = set()
    if os.path.exists(out):
        for ln in open(out):
            try:
                done.add(json.loads(ln)["pres_id"])
            except (ValueError, KeyError):
                pass
    todo = [(r["name"], r["r1"], r["r2"], args.rungs, args.beam, args.cap,
             args.stop_mu) for r in rows if r["name"] not in done]
    jobs = args.jobs or max(1, (os.cpu_count() or 4) - 2)
    print(f"{len(todo)} classes, rungs {args.rungs}, beam {args.beam}, "
          f"{jobs} workers -> {os.path.basename(out)}", flush=True)
    n = 0
    with open(out, "a") as f, ProcessPoolExecutor(max_workers=jobs) as ex:
        futs = {ex.submit(climb_one, t): t[0] for t in todo}
        for fut in as_completed(futs):
            row = fut.result()
            f.write(json.dumps(row) + "\n")
            f.flush()
            n += 1
            tag2 = ""
            if row["hits_stop"]:
                tag2 = (" *** JACKPOT-LEAD: mu<=stop — AK3-orbit"
                        if row["is_ak3_orbit"] else
                        " *** JACKPOT-LEAD: mu<=stop — NOT AK3 orbit")
            elif row["best_mu"] < row["mu_in"]:
                tag2 = f" DESC {row['mu_in']}->{row['best_mu']}"
            print(f"  [{n}/{len(todo)}] {row['pres_id']} best "
                  f"{row['best_mu']} (in {row['mu_in']}, "
                  f"{row['n_orbits_seen']} orbits){tag2}", flush=True)
    print(f"written: {out}", flush=True)


if __name__ == "__main__":
    main()
