"""Local pilot: reverse MITM — search from each catalog leaf toward {AK3, P25}x8.

Streams one JSONL record per leaf to results/stable_ac/ak3_stable_proof/runs/
reverse_pilot.jsonl (resumable by leaf key).
"""
import argparse
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
    ap = argparse.ArgumentParser()
    ap.add_argument("--max_nodes", type=int, default=100_000)
    ap.add_argument("--max_len", type=int, default=24)
    ap.add_argument("--limit", type=int, default=5)
    ap.add_argument("--min_len", type=int, default=10, help="skip trivial-class tiny leaves")
    ap.add_argument("--out", default=os.path.join(RUNS, "reverse_pilot.jsonl"))
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

    recs = [json.loads(l) for l in open(LEAVES)]
    recs = [r for r in recs
            if r["total_len"] >= args.min_len and all(len(x) < args.max_len
                                                      for x in r["relators"])]
    recs.sort(key=lambda r: r["total_len"])
    n_run = 0
    with open(args.out, "a") as f:
        for rec in recs:
            if rec["key"] in done or n_run >= args.limit:
                continue
            res = run_search(rec["relators"], targets, max_nodes=args.max_nodes,
                             max_len=args.max_len, tag=f"leaf:{rec['key'][:16]}")
            row = {"leaf_key": rec["key"], "leaf_total_len": rec["total_len"],
                   "budget": args.max_nodes, **{k: res[k] for k in
                                                ("nodes", "wall_s", "min_total_len")},
                   "hit": None if res["hit"] is None else res["hit"]["meta"]}
            if res["hit"]:
                hit_path = os.path.join(RUNS, f"hit_{rec['key'][:16]}.json")
                with open(hit_path, "w") as g:
                    json.dump(res, g)
                row["hit_path_file"] = hit_path
                print(f"*** HIT *** leaf {rec['key'][:16]} -> {res['hit']['meta']}")
            f.write(json.dumps(row) + "\n")
            f.flush()
            os.fsync(f.fileno())
            n_run += 1
            print(f"leaf {rec['key'][:16]} len={rec['total_len']}: nodes={res['nodes']} "
                  f"min_tl={res['min_total_len']} hit={row['hit']}")


if __name__ == "__main__":
    main()
