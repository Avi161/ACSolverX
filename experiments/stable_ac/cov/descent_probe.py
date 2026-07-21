"""Descent-probe ranking (IMPLEMENTATION_IDEAS.md idea 2 — track T3).

Replaces the abel/mu proxies with a MEASUREMENT: for each of a presentation's
top CoV candidates, run a bounded probe (default 500 nodes — a ranking pass,
never a solve attempt) and score by realized descent rate

    (start_total_len - min_total_len_reached) / nodes_to_reach_it

using the shipped solver's stats. Probes are the sanctioned local use of
search here (IDEAS.md idea 2: "affordable locally as a ranking pass"); the
output is a per-presentation candidate ORDER for the production portfolio.
All-zero descent rates on a presentation are honest signal ("no better basin
among its candidates"), not failure.

CLI:
    .venv/bin/python3 -m experiments.stable_ac.cov.descent_probe \
        --bench mu_floors_r8 [--top 8] [--probe-budget 500] [--cap 24]
"""

import argparse
import json
import os

from experiments import run_baseline
from experiments.equivalence_classes.lib.autcanon import aut_min_len
from experiments.greedy_tests.spec.words import str_to_word, word_to_str
from experiments.stable_ac.cov import cov
from experiments.stable_ac.cov.restart_planner import abel_magnitude

HERE = os.path.dirname(os.path.abspath(__file__))


def top_candidates(r1, r2, cap, top):
    """The `top` mu-then-abel-ranked CoV candidates of (r1, r2)."""
    res = cov.enumerate_cov(str_to_word(r1), str_to_word(r2),
                            default_cap=cap, cap_headroom=cov.CAP_HEADROOM,
                            reject_len=cov.REJECT_LEN)
    seen, out = set(), []
    for c in res:
        o = (word_to_str(c.r1), word_to_str(c.r2))
        if o in seen:
            continue
        seen.add(o)
        out.append((aut_min_len(o), abel_magnitude(c.r1, c.r2), o,
                    max(cap, c.cap), word_to_str(c.z_word)))
    out.sort(key=lambda t: (t[0], t[1], t[2]))
    return out[:top]


def probe(r1, r2, budget, cap):
    st = run_baseline.greedy_search(r1, r2, budget,
                                    max_relator_length=cap,
                                    cyclic_reduce=True)
    start_total = len(r1) + len(r2)
    reached = st["min_relator_length"]      # min TOTAL reached during search
    drop = max(0, start_total - reached)
    return {"solved": st["solved"], "nodes": st["nodes_explored"],
            "min_total": reached,
            "rate": drop / max(st["nodes_explored"], 1)}


def main():
    from experiments.stable_ac.idea_bench import harness

    ap = argparse.ArgumentParser(description="Descent-probe candidate ranking.")
    ap.add_argument("--bench", default="mu_floors_r8")
    ap.add_argument("--top", type=int, default=8)
    ap.add_argument("--probe-budget", type=int, default=500)
    ap.add_argument("--cap", type=int, default=24)
    ap.add_argument("--row-limit", type=int, default=None)
    args = ap.parse_args()
    assert args.probe_budget <= 1000, "probes are a ranking pass: <= 1000"
    root = harness.find_repo_root(HERE)
    out = os.path.join(root, "results/stable_ac/mu_scan",
                       f"descent_probe_{args.bench}_t{args.top}"
                       f"_p{args.probe_budget}_mrl{args.cap}.jsonl")
    done = set()
    if os.path.exists(out):
        for ln in open(out):
            try:
                done.add(json.loads(ln)["pres_id"])
            except (ValueError, KeyError):
                pass
    rows = harness.load_bench(args.bench)
    if args.row_limit:
        rows = rows[:args.row_limit]
    with open(out, "a") as f:
        for p in rows:
            if p["pres_id"] in done:
                continue
            cands = top_candidates(p["r1"], p["r2"], args.cap, args.top)
            probed = []
            for mu, abel, (o1, o2), ccap, z in cands:
                pr = probe(o1, o2, args.probe_budget, ccap)
                probed.append({"z_word": z, "mu": mu, "abel": abel,
                               "r1": o1, "r2": o2, "cap": ccap, **pr})
            probed.sort(key=lambda d: (-d["rate"], d["mu"]))
            rec = {"pres_id": p["pres_id"], "probe_budget": args.probe_budget,
                   "cap": args.cap, "n_cands": len(probed),
                   "best_rate": probed[0]["rate"] if probed else 0.0,
                   "any_solved": any(d["solved"] for d in probed),
                   "candidates": probed}
            f.write(json.dumps(rec) + "\n")
            f.flush()
            print(f"  {p['pres_id']}: {len(probed)} cands, best rate "
                  f"{rec['best_rate']:.4f}, solved={rec['any_solved']}",
                  flush=True)
    print(f"written: {out}", flush=True)


if __name__ == "__main__":
    main()
