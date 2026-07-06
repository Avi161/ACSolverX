"""Classify every catalog leaf: does plain greedy trivialize it (=> AC-trivial,
a confirming instance of the paper's Conjecture 18, useless as an AK3 bridge), or does
it get STUCK (=> candidate stably-trivial-but-not-AC-trivial presentation — exactly
the kind that could share AK(3)'s AC-class)? Streams to runs/leaf_class.jsonl.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)

from hmoves import AK3, P25  # noqa: E402
from mitm import load_targets, run_search  # noqa: E402

RUNS = os.path.join(ROOT, "results", "stable_ac", "ak3_stable_proof", "runs")
LEAVES = os.path.join(ROOT, "results", "stable_ac", "ak3_stable_proof", "catalog",
                      "catalog_leaves.jsonl")


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--max_nodes", type=int, default=50_000)
    ap.add_argument("--max_len", type=int, default=24)
    ap.add_argument("--out", default=os.path.join(RUNS, "leaf_class.jsonl"))
    args = ap.parse_args()
    os.makedirs(RUNS, exist_ok=True)

    targets, _ = load_targets(None, include={"AK3": AK3, "P25": P25})
    done = set()
    if os.path.exists(args.out):
        for line in open(args.out):
            try:
                done.add(json.loads(line)["leaf_key"])
            except Exception:
                pass
    recs = {r["key"]: r for line in open(LEAVES)
            for r in [json.loads(line)]}
    recs = [r for r in recs.values() if all(len(x) < args.max_len for x in r["relators"])]
    recs.sort(key=lambda r: r["total_len"])
    print(f"{len(recs)} leaves fit max_len={args.max_len}; {len(done)} already classified")
    n_triv = n_stuck = n_hit = 0
    with open(args.out, "a") as f:
        for rec in recs:
            if rec["key"] in done:
                continue
            res = run_search(rec["relators"], targets, max_nodes=args.max_nodes,
                             max_len=args.max_len, tag=f"leaf:{rec['key'][:16]}")
            trivialized = res["min_total_len"] == 2
            cls = "hit" if res["hit"] else ("ac_trivial" if trivialized else "stuck")
            if cls == "hit":
                n_hit += 1
                hit_path = os.path.join(RUNS, f"hit_{rec['key'][:16]}.json")
                with open(hit_path, "w") as g:
                    json.dump(res, g)
                print(f"*** HIT *** leaf {rec['key'][:16]} -> {res['hit']['meta']}")
            elif trivialized:
                n_triv += 1
            else:
                n_stuck += 1
                print(f"STUCK leaf {rec['key'][:16]} len={rec['total_len']} "
                      f"min_tl={res['min_total_len']}")
            f.write(json.dumps({"leaf_key": rec["key"],
                                "leaf_total_len": rec["total_len"],
                                "budget": args.max_nodes, "class": cls,
                                "min_total_len": res["min_total_len"],
                                "nodes": res["nodes"]}) + "\n")
            f.flush()
    print(f"classified: ac_trivial={n_triv} stuck={n_stuck} hit={n_hit}")


if __name__ == "__main__":
    main()
